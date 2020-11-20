import os
import csv
import sys
import json
import numpy
import struct
import asyncio
import platform
import tensorflow as tf
import paho.mqtt.client as mqtt

from time import time
from bleak import BleakClient
from dotenv import load_dotenv
from argparse import ArgumentParser

from numpy import mean, std, dstack
from keras.models import Sequential, load_model
from tensorflow.python.keras.backend import set_session

SHOW_INTERVAL = 3
BATTERY_INTERVAL = 15

session = tf.compat.v1.Session(graph=tf.compat.v1.Graph())

# actions = {0: 'NOD', 1: 'SHAKE'}
PREVIOUS_SHOWN = ''

class Service:

    def __init__(self):
        self.data_uuid = None
        self.ctrl_uuid = None
        self.freq_uuid = None
        self.freq_bits = bytearray([0x0A])  # 10hz

class Sensor(Service):

    def callback(self, sender: int, data: bytearray):
        raise NotImplementedError()

    async def enable(self, client, *args):
        write_value = bytearray([0x01])
        await client.write_gatt_char(self.ctrl_uuid, write_value)
        await client.write_gatt_char(self.freq_uuid, self.freq_bits)
        return self

    async def read(self, client):
        val = await client.read_gatt_char(self.data_uuid)
        return self.callback(1, val)

class BatteryService(Service):
    def __init__(self):
        super().__init__()
        self.data_uuid = "00002a19-0000-1000-8000-00805f9b34fb"

    async def read(self, client):
        val = await client.read_gatt_char(self.data_uuid)
        return int(val[0])

class MovementSensorMPU9250SubService:

    def __init__(self):
        self.bits = 0

    def enable_bits(self):
        return self.bits

    def cb_sensor(self, data):
        raise NotImplementedError


class MovementSensorMPU9250(Sensor):
    GYRO_XYZ = 7
    ACCEL_XYZ = 7 << 3
    MAG_XYZ = 1 << 6
    ACCEL_RANGE_2G  = 0 << 8
    ACCEL_RANGE_4G  = 1 << 8
    ACCEL_RANGE_8G  = 2 << 8
    ACCEL_RANGE_16G = 3 << 8

    def __init__(self):
        super().__init__()
        self.data_uuid = "f000aa81-0451-4000-b000-000000000000"
        self.ctrl_uuid = "f000aa82-0451-4000-b000-000000000000"
        self.freq_uuid = "f000aa83-0451-4000-b000-000000000000"
        self.ctrlBits = 0
        self.sub_callbacks = []

    def register(self, cls_obj: MovementSensorMPU9250SubService):
        self.ctrlBits |= cls_obj.enable_bits()
        self.sub_callbacks.append(cls_obj.cb_sensor)

    def callback(self, sender: int, data: bytearray):
        unpacked_data = struct.unpack("<hhhhhhhhh", data)
        # return unpacked_data
        accel_vals = self.sub_callbacks[0](unpacked_data)
        gryo_vals = self.sub_callbacks[1](unpacked_data)
        mag_vals = self.sub_callbacks[2](unpacked_data)
        return gryo_vals + accel_vals + mag_vals

    async def enable(self, client, *args):
        await client.write_gatt_char(self.freq_uuid, self.freq_bits)
        await client.write_gatt_char(self.ctrl_uuid, struct.pack("<H", self.ctrlBits))
        return self

    async def read(self, client):
        val = await client.read_gatt_char(self.data_uuid)
        return self.callback(1, val)       

        
class GyroscopeSensorMovementSensorMPU9250(MovementSensorMPU9250SubService):
    def __init__(self):
        super().__init__()
        self.bits = MovementSensorMPU9250.GYRO_XYZ
        self.scale = 500.0/65536.0

    def cb_sensor(self, data):
        '''Returns (x_gyro, y_gyro, z_gyro) in units of degrees/sec'''
        rawVals = data[0:3]
        return [(x*self.scale) for x in rawVals]


class AccelerometerSensorMovementSensorMPU9250(MovementSensorMPU9250SubService):
    def __init__(self):
        super().__init__()
        self.bits = MovementSensorMPU9250.ACCEL_XYZ | MovementSensorMPU9250.ACCEL_RANGE_4G
        self.scale = 8.0/32768.0 

    def cb_sensor(self, data):
        '''Returns (x_accel, y_accel, z_accel) in units of g'''
        rawVals = data[3:6]
        return [(x*self.scale) for x in rawVals] 


class MagnetometerSensorMovementSensorMPU9250(MovementSensorMPU9250SubService):
    def __init__(self):
        super().__init__()
        self.bits = MovementSensorMPU9250.MAG_XYZ
        self.scale = 4912.0 / 32760
        # Reference: MPU-9250 register map v1.4

    def cb_sensor(self, data):
        '''Returns (x_mag, y_mag, z_mag) in units of uT'''
        rawVals = data[6:9]
        return [(x*self.scale) for x in rawVals]

class BarometerSensor(Sensor):
    def __init__(self):
        super().__init__()
        self.data_uuid = "f000aa41-0451-4000-b000-000000000000"
        self.ctrl_uuid = "f000aa42-0451-4000-b000-000000000000"
        self.freq_uuid = "f000aa44-0451-4000-b000-000000000000"

    def callback(self, sender: int, data: bytearray):
        (tL, tM, tH, pL, pM, pH) = struct.unpack('<BBBBBB', data)
        press = (pH*65536 + pM*256 + pL) / 100.0
        return press

class lstm_model():
    def __init__(self, model):
        self._temp_predict = ''
        self._predict_time = 0.0

        if model == "hand_model.hd5":
            self._confidence = 0.85
            self._actions = {0: 'HAND_IDLE', 1: 'RAISE', 2: 'WAVE', 3: 'CLAP'}
        else: # head model
            self._confidence = 0.88
            self._actions = {0: 'NOD', 1: 'SHAKE', 2: 'LOOKUP', 3: 'TILT'}

        self._loaded_model = load_model(model)
        print(f"{model} loaded, ready to predict")
        
        self.ACC_X_BUFFER  = []
        self.ACC_Y_BUFFER  = []
        self.ACC_Z_BUFFER  = []
        self.GYRO_X_BUFFER = []
        self.GYRO_Y_BUFFER = []
        self.GYRO_Z_BUFFER = []
        self.MAG_X_BUFFER  = []
        self.MAG_Y_BUFFER  = []
        self.MAG_Z_BUFFER  = []
        self.BARO_BUFFER   = []

    def append_buffer(self, baro, motion):
        self.BARO_BUFFER.append(baro)
        self.GYRO_X_BUFFER.append(motion[0])
        self.GYRO_Y_BUFFER.append(motion[1])
        self.GYRO_Z_BUFFER.append(motion[2])
        self.ACC_X_BUFFER.append(motion[3])
        self.ACC_Y_BUFFER.append(motion[4])
        self.ACC_Z_BUFFER.append(motion[5])
        self.MAG_X_BUFFER.append(motion[6])
        self.MAG_Y_BUFFER.append(motion[7])
        self.MAG_Z_BUFFER.append(motion[8])

    # load the dataset, returns train and test X and y elements
    def load_dataset(self):
        # load all data
        loaded = []
        loaded.append(self.ACC_X_BUFFER)
        loaded.append(self.ACC_Y_BUFFER)
        loaded.append(self.ACC_Z_BUFFER)
        loaded.append(self.GYRO_X_BUFFER)
        loaded.append(self.GYRO_Y_BUFFER)
        loaded.append(self.GYRO_Z_BUFFER)
        loaded.append(self.MAG_X_BUFFER)
        loaded.append(self.MAG_X_BUFFER)
        loaded.append(self.MAG_X_BUFFER)
        loaded.append(self.BARO_BUFFER)
        # stack group so that features are the 3rd dimension
        data = dstack(loaded)
        return data

    # Clearing buffers after making prediction
    def clear_buffer(self):
        self.BARO_BUFFER.clear()
        self.GYRO_X_BUFFER.clear()
        self.GYRO_Y_BUFFER.clear()
        self.GYRO_Z_BUFFER.clear()
        self.ACC_X_BUFFER.clear()
        self.ACC_Y_BUFFER.clear()
        self.ACC_Z_BUFFER.clear()
        self.MAG_X_BUFFER.clear()
        self.MAG_Y_BUFFER.clear()
        self.MAG_Z_BUFFER.clear()

    def predict(self):
        data = self.load_dataset()
        result = self._loaded_model.predict(data)
        self.clear_buffer()
        themax = numpy.argmax(result[0])

        if (result[0][themax] < self._confidence): # prediction = 'IDLE'            
            
            if self._temp_predict != 'IDLE':
                if time() - self._predict_time < SHOW_INTERVAL:
                    return self._temp_predict
                else:
                    self._temp_predict = 'IDLE'
                    return 'IDLE'
            else:
                return self._temp_predict
        else:
            self._temp_predict = self._actions[themax]
            self._predict_time = time()
            return self._temp_predict

class SensorTag:
    def __init__(self, address, name, model, mqtt_client):
        self._battery_life = None
        self._address = address
        self._mqtt_client = mqtt_client
        self._previous_shown = ''
        # Iterations of data collection
        self._timesteps = 5 

        self._topic = "Group_12/LSTM/predict/"
        print(f"name: {name}")
        if name == 'glen':
            self._topic += "Glen"
        elif name == 'nicholas':
            self._topic += "Nicholas"
        elif name == 'sean':
            self._topic += "Sean"
        else:
            self._topic += "Permas"

        # Enabling battery status
        self._battery = BatteryService()
        
        if model == 'hand':
            self._topic += "_hand"
            self._model = lstm_model(model= "hand_model.hd5")
        else:
            self._model = lstm_model(model= "lstm_model.hd5")

        print(f"topic: {self._topic}")

    def check_and_publish(self, prediction):
        result = {}
        if prediction != self._previous_shown:
            result["Shown"] = prediction
            result["batterylife"] = self._battery_life    
            self._mqtt_client.publish(self._topic, json.dumps(result))
        
        self._previous_shown = prediction

    async def run(self):
        async with BleakClient(self._address) as client:
            x = await client.is_connected()
            print("Connected: {0}".format(x))

            print("Enabling sensors")

            # Enabling sensors
            self._barometer_sensor = await BarometerSensor().enable(client)
            self._acc_sensor = AccelerometerSensorMovementSensorMPU9250()
            self._gyro_sensor = GyroscopeSensorMovementSensorMPU9250()
            self._magneto_sensor = MagnetometerSensorMovementSensorMPU9250()
            self._movement_sensor = MovementSensorMPU9250()
            self._movement_sensor.register(self._acc_sensor)
            self._movement_sensor.register(self._gyro_sensor)
            self._movement_sensor.register(self._magneto_sensor)
            self._m_sensor = await self._movement_sensor.enable(client)
            print("sensors enabled")

            self._battery_life = await self._battery.read(client) 
            prev_battery_reading_time = time() 
                
            while (True):
                for i in range(self._timesteps):
                    baro_reading = await self._barometer_sensor.read(client)
                    motion_reading = await self._m_sensor.read(client)
                    self._model.append_buffer(baro= baro_reading, motion= motion_reading)
                
                prediction = self._model.predict()

                print('predicted result: ', prediction)
                
                if time() - prev_battery_reading_time > BATTERY_INTERVAL:
                    self._battery_life = await self._battery.read(client)
                    print(self._battery_life)
                    prev_battery_reading_time = time()

                self.check_and_publish(prediction)

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected")
    else:
        print("Failed to connect. Error code: %d." % rc)
        
def setup(hostname):
    print("setting up client")
    USERID = os.getenv("REACT_APP_EC2_USER")
    PASSWORD = os.getenv("REACT_APP_EC2_PASSWORD")    

    client = mqtt.Client()
    client.username_pw_set(USERID, PASSWORD)
    client.on_connect = on_connect
    client.connect(hostname, port=1883)
    client.loop_start()
    return client
    
if __name__ == '__main__':

    os.environ["PYTHONASYNCIODEBUG"] = str(1)
    load_dotenv()
    p = ArgumentParser(description= "Script for sensortag")
    p.add_argument("-n", required= True, choices= ['glen', 'nicholas', 'sean', 'permas'], type= str, help= "your name in lower case")
    p.add_argument("-s1", action= "store_true", help= "sensortag 1")
    p.add_argument("-s2", action= "store_true", help = "sensortag 2")
    p.add_argument("-m", required= True, choices= ['head', 'hand'], type = str, help= "choose model to use")

    args = p.parse_args()
    if args.s1 and args.s2:
        p.error("choose only s1 or s2")
        exit(1)

    if not (args.s1 or args.s2):
        p.error("need to have at least -s1 or -s2")
        exit(1)
        
    try:
        with open(f"{sys.path[0]}/sensortag_addr.txt") as f:
            addrs = f.read().splitlines()

            if args.s1 and platform != "Darwin":
                addr = addrs[0]
            elif args.s2 and platform != "Darwin":
                addr = addrs[-1]
            else:
                addr = "6FFBA6AE-0802-4D92-B1CD-041BE4B4FEB9"

        # Setting MQTT Client
        mqtt_client = setup(os.getenv("REACT_APP_EC2_PUBLIC_IP"))

        sensortag = SensorTag(address= addr, name= args.n, model= args.m, mqtt_client= mqtt_client)

        loop = asyncio.get_event_loop()
        
        try:
            loop.run_until_complete(sensortag.run())
        except KeyboardInterrupt:
            loop.stop()
            loop.close()
            print("Received exit, exiting...")
        # except Exception as e:
        #     print(f"exception: {e}")

    except FileNotFoundError:
        print("no file named sensortag_addr.txt, create file and input sensortag MAC addr")      