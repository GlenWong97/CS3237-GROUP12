import os
import csv
import sys
import json
import numpy
import struct
import asyncio
import platform
import paho.mqtt.client as mqtt

from time import time
from bleak import BleakClient

from numpy import mean, std, dstack
from keras.models import Sequential, load_model

ACC_X_BUFFER = []
ACC_Y_BUFFER = []
ACC_Z_BUFFER = []
GYRO_X_BUFFER = []
GYRO_Y_BUFFER = []
GYRO_Z_BUFFER = []
MAG_X_BUFFER = []
MAG_Y_BUFFER = []
MAG_Z_BUFFER = []
BARO_BUFFER = []

READY = False
BATTERYLIFE = 0

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

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected")
        # Please uncomment accordingly
        # client.subscribe("Group_12/LSTM/predict/Glen")
        # client.subscribe("Group_12/LSTM/predict/Sean")
        client.subscribe("Group_12/LSTM/predict/Nicholas")
    else:
        print("Failed to connect. Error code: %d." % rc)


def on_message(client, userdata, msg):
    # print("Received message from server.")
    resp_dict = json.loads(msg.payload)
    print("Prediction: %s" % (resp_dict["Prediction"]))
    global READY
    READY = True


def sending_data(mqtt_client):
    
    global BATTERYLIFE
    # load all data
    loaded = list()
    loaded.append(ACC_X_BUFFER)
    loaded.append(ACC_Y_BUFFER)
    loaded.append(ACC_Z_BUFFER)
    loaded.append(GYRO_X_BUFFER)
    loaded.append(GYRO_Y_BUFFER)
    loaded.append(GYRO_Z_BUFFER)
    loaded.append(MAG_X_BUFFER)
    loaded.append(MAG_X_BUFFER)
    loaded.append(MAG_X_BUFFER)
    loaded.append(BARO_BUFFER)
    
    # stack group so that features are the 3rd dimension
    data = dstack(loaded)
    data = data.tolist()
    send_dict = {"data": data, "batterylife": BATTERYLIFE}
    mqtt_client.publish("Group_12/LSTM/classify/Nicholas", json.dumps(send_dict))

    # Clearing buffers after making prediction
    BARO_BUFFER.clear()
    GYRO_X_BUFFER.clear()
    GYRO_Y_BUFFER.clear()
    GYRO_Z_BUFFER.clear()
    ACC_X_BUFFER.clear()
    ACC_Y_BUFFER.clear()
    ACC_Z_BUFFER.clear()
    MAG_X_BUFFER.clear()
    MAG_Y_BUFFER.clear()
    MAG_Z_BUFFER.clear()


def setup(hostname):
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(hostname)
    client.loop_start()
    return client

async def run(address):
    async with BleakClient(address) as client:
        global READY
        global BATTERYLIFE
        READY = False
        x = await client.is_connected()
        print("Connected: {0}".format(x))

        # Setting MQTT Client
        mqtt_client = setup("test.mosquitto.org")
    
        # Enabling sensors
        barometer_sensor = await BarometerSensor().enable(client)
        acc_sensor = AccelerometerSensorMovementSensorMPU9250()
        gyro_sensor = GyroscopeSensorMovementSensorMPU9250()
        magneto_sensor = MagnetometerSensorMovementSensorMPU9250()
        movement_sensor = MovementSensorMPU9250()
        movement_sensor.register(acc_sensor)
        movement_sensor.register(gyro_sensor)
        movement_sensor.register(magneto_sensor)
        m_sensor = await movement_sensor.enable(client)

        # Enabling battery status
        battery = BatteryService()
        prev_battery_reading_time = time()
        BATTERYLIFE = await battery.read(client)
        # print("Battery Reading: {}\n".format(BATTERYLIFE))
            
        while (True):

            # Iterations of data collection
            timesteps = 5        
            # print("Please perform action for 3 seconds.")

            for i in range(0, timesteps):
                baro_reading = await barometer_sensor.read(client)
                motion_reading = await m_sensor.read(client)
                BARO_BUFFER.append(baro_reading)
                GYRO_X_BUFFER.append(motion_reading[0])
                GYRO_Y_BUFFER.append(motion_reading[1])
                GYRO_Z_BUFFER.append(motion_reading[2])
                ACC_X_BUFFER.append(motion_reading[3])
                ACC_Y_BUFFER.append(motion_reading[4])
                ACC_Z_BUFFER.append(motion_reading[5])
                MAG_X_BUFFER.append(motion_reading[6])
                MAG_Y_BUFFER.append(motion_reading[7])
                MAG_Z_BUFFER.append(motion_reading[8])
            
            sending_data(mqtt_client)

            while not READY:
                # Updates battery status after 15s
                if time() - prev_battery_reading_time > 15:
                    BATTERYLIFE = await battery.read(client)
                    # print("Battery Reading: {}\n".format(BATTERYLIFE))
                    prev_battery_reading_time = time()

if __name__ == '__main__':

    os.environ["PYTHONASYNCIODEBUG"] = str(1)
    try:
        with open(f"{sys.path[0]}/sensortag_addr.txt") as f:
            address = (
                f.read() 
                if platform.system() != "Darwin"
                else "6FFBA6AE-0802-4D92-B1CD-041BE4B4FEB9"
            )

        loop = asyncio.get_event_loop()

        try:
            loop.run_until_complete(run(address))
            # loop.run_forever()
        except KeyboardInterrupt:
            loop.stop()
            loop.close()
            print("Received exit, exiting...")
        except Exception as e:
            print(f"exception: {e}")

    except FileNotFoundError:
        print("no file named sensortag_addr.txt, create file and input sensortag MAC addr")      