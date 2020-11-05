# -*- coding: utf-8 -*-
"""
TI CC2650 SensorTag
-------------------

Adapted by Ashwin from the following sources:
 - https://github.com/IanHarvey/bluepy/blob/a7f5db1a31dba50f77454e036b5ee05c3b7e2d6e/bluepy/sensortag.py
 - https://github.com/hbldh/bleak/blob/develop/examples/sensortag.py

"""
import sys
import os
import asyncio
import platform
import struct
import csv

from time import time
from bleak import BleakClient

# 1: Nod, 2: Shake, 3: Look up, 4: Tilt
LABEL = '4'
LABELTOACTION = {
    '1': 'Nod',
    '2': 'Shake',
    '3': 'Look up',
    '4': 'Tilt',
}
# Coordination global variable
READY = -1
# remove number of data to ensure parallel
START_THRESHOLD = 50
# Datatype: test or train
DATATYPE = "train"

# Number of timesteps for lstm
TIMESTEPS = 10
accel_count = 0
gryo_count = 0
mag_count = 0
baro_count = 0
useful_data = 0

class Service:
    """
    Here is a good documentation about the concepts in ble;
    https://learn.adafruit.com/introduction-to-bluetooth-low-energy/gatt

    In TI SensorTag there is a control characteristic and a data characteristic which define a service or sensor
    like the Light Sensor, Humidity Sensor etc

    Please take a look at the official TI user guide as well at
    https://processors.wiki.ti.com/index.php/CC2650_SensorTag_User's_Guide
    """

    def __init__(self):
        self.data_uuid = None
        self.ctrl_uuid = None
        self.freq_uuid = None
        self.ctrl_bits = bytearray([0x01])
        # self.freq_bits = bytearray([0x64]) # 1hz
        self.freq_bits = bytearray([0x0A]) # 10hz

class Sensor(Service):

    def callback(self, sender: int, data: bytearray):
        raise NotImplementedError()

    async def start_listener(self, client, *args):
        await client.write_gatt_char(self.freq_uuid, self.freq_bits)
        # start the sensor on the device
        await client.write_gatt_char(self.ctrl_uuid, self.ctrl_bits)

        # listen using the handler
        await client.start_notify(self.data_uuid, self.callback)


class MovementSensorMPU9250SubService:

    def __init__(self):
        self.ctrl_bits = 0

    def enable_bits(self):
        return self.ctrl_bits

    def cb_sensor(self, data):
        raise NotImplementedError


class MovementSensorMPU9250(Sensor):
    GYRO_XYZ = 7
    ACCEL_XYZ = 7 << 3
    MAG_XYZ = 1 << 6
    ACCEL_RANGE_2G = 0 << 8
    ACCEL_RANGE_4G = 2 << 8
    ACCEL_RANGE_8G = 1 << 8
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

    async def start_listener(self, client, *args):
        await client.write_gatt_char(self.freq_uuid, self.freq_bits)
        # start the sensor on the device
        await client.write_gatt_char(self.ctrl_uuid, struct.pack("<H", self.ctrlBits))

        # listen using the handler
        await client.start_notify(self.data_uuid, self.callback)

    def callback(self, sender: int, data: bytearray):
        unpacked_data = struct.unpack("<hhhhhhhhh", data)
        for cb in self.sub_callbacks:
            cb(unpacked_data)


class AccelerometerSensorMovementSensorMPU9250(MovementSensorMPU9250SubService):
    def __init__(self):
        super().__init__()
        self.ctrl_bits = MovementSensorMPU9250.ACCEL_XYZ | MovementSensorMPU9250.ACCEL_RANGE_8G
        self.scale = 8.0/32768.0  # convert raw data to gravity ## sensortag user guide
        self.start_time = 0.0
        self.received = 0
        self.scaledVals = []

    def cb_sensor(self, data):
        '''Returns (x_accel, y_accel, z_accel) in units of g'''
        global READY, useful_data
        READY += 1
        if READY == 0:
            print("Setup not ready, please wait...")
        elif READY == 1:
            print("Setup ready, please do your action...")
        elif READY >= 2:
            READY = 2
            if useful_data < START_THRESHOLD:
                return
            rawVals = data[3:6]
            self.scaledVals = [(x*self.scale) for x in rawVals]
            self.save_values()
            # print("[MovementSensor] Accelerometer:", tuple([v*self.scale for v in rawVals]))
            # print(f"acc_x: {rawVals[0]}, acc_y: {rawVals[1]}, acc_z: {rawVals[2]}")
            self.received += 1
            if time() - self.start_time > 1:
                print(f"accel count: {self.received}")
                self.start_time = time()

    def save_values(self):
        global accel_count
        with open('./ProjectData/{0}/IndividualSignals/acc_x_{0}.csv'.format(DATATYPE), 'a') as a, \
                    open('./ProjectData/{0}/IndividualSignals/acc_y_{0}.csv'.format(DATATYPE), 'a') as b, \
                    open('./ProjectData/{0}/IndividualSignals/acc_z_{0}.csv'.format(DATATYPE), 'a') as c:
            if accel_count == TIMESTEPS - 1:
                a.write("{}\n".format(self.scaledVals[0]))
                b.write("{}\n".format(self.scaledVals[1]))
                c.write("{}\n".format(self.scaledVals[2]))
                accel_count = 0
            else:
                a.write("{},".format(self.scaledVals[0]))
                b.write("{},".format(self.scaledVals[1]))
                c.write("{},".format(self.scaledVals[2]))
                accel_count += 1


class MagnetometerSensorMovementSensorMPU9250(MovementSensorMPU9250SubService):
    def __init__(self):
        super().__init__()
        self.ctrl_bits = MovementSensorMPU9250.MAG_XYZ
        self.scale = 4912.0 / 32760 # dont need to scale for magnetometer?
        # Reference: MPU-9250 register map v1.4
        self.start_time = 0.0
        self.received = 0
        self.scaledVals = []

    def cb_sensor(self, data):
        '''Returns (x_mag, y_mag, z_mag) in units of uT, +- 4900'''
        global READY, useful_data

        if READY >= 2:
            if useful_data < START_THRESHOLD:
                return
            rawVals = data[6:9]
            self.scaledVals = [(x*self.scale) for x in rawVals]
            self.save_values()
            # print("[MovementSensor] Magnetometer:", tuple([v*self.scale for v in rawVals]))
            self.received += 1
            if time() - self.start_time > 1:
                print(f"magneto count: {self.received}")
                self.start_time = time()

    def save_values(self):
        global mag_count
        with open('./ProjectData/{0}/IndividualSignals/mag_x_{0}.csv'.format(DATATYPE), 'a') as a, \
                    open('./ProjectData/{0}/IndividualSignals/mag_y_{0}.csv'.format(DATATYPE), 'a') as b, \
                    open('./ProjectData/{0}/IndividualSignals/mag_z_{0}.csv'.format(DATATYPE), 'a') as c:
            if mag_count == TIMESTEPS - 1:
                a.write("{}\n".format(self.scaledVals[0]))
                b.write("{}\n".format(self.scaledVals[1]))
                c.write("{}\n".format(self.scaledVals[2]))
                mag_count = 0
            else:
                a.write("{},".format(self.scaledVals[0]))
                b.write("{},".format(self.scaledVals[1]))
                c.write("{},".format(self.scaledVals[2]))
                mag_count += 1


class GyroscopeSensorMovementSensorMPU9250(MovementSensorMPU9250SubService):
    def __init__(self):
        super().__init__()
        self.ctrl_bits = MovementSensorMPU9250.GYRO_XYZ
        self.scale = 500.0/65536.0 # convert to degrees/second ## sensortag user guide
        self.start_time = 0.0
        self.received = 0
        self.scaledVals = []

    def cb_sensor(self, data):
        '''Returns (x_gyro, y_gyro, z_gyro) in units of degrees/sec'''
        global READY, useful_data

        if READY >= 2:
            if useful_data < START_THRESHOLD:
                return
            rawVals = data[0:3]
            self.scaledVals = [(x*self.scale) for x in rawVals]
            self.save_values()
            # print("[MovementSensor] Gyroscope:", tuple([v*self.scale for v in rawVals]))
            self.received += 1
            if time() - self.start_time > 1:
                print(f"gyro count: {self.received}")
                self.start_time = time()

    def save_values(self):
        global gryo_count
        with open('./ProjectData/{0}/IndividualSignals/gyro_x_{0}.csv'.format(DATATYPE), 'a') as a, \
                    open('./ProjectData/{0}/IndividualSignals/gyro_y_{0}.csv'.format(DATATYPE), 'a') as b, \
                    open('./ProjectData/{0}/IndividualSignals/gyro_z_{0}.csv'.format(DATATYPE), 'a') as c:
            if gryo_count == TIMESTEPS - 1:
                a.write("{}\n".format(self.scaledVals[0]))
                b.write("{}\n".format(self.scaledVals[1]))
                c.write("{}\n".format(self.scaledVals[2]))
                gryo_count = 0
            else:
                a.write("{},".format(self.scaledVals[0]))
                b.write("{},".format(self.scaledVals[1]))
                c.write("{},".format(self.scaledVals[2]))
                gryo_count += 1


class BarometerSensor(Sensor):
    def __init__(self):
        super().__init__()
        self.data_uuid = "f000aa41-0451-4000-b000-000000000000"
        self.ctrl_uuid = "f000aa42-0451-4000-b000-000000000000"
        self.freq_uuid = "f000aa44-0451-4000-b000-000000000000"
        self.start_time = 0.0
        self.press = 0.0
        self.received = 0

    def callback(self, sender: int, data: bytearray):

        global READY, useful_data

        if READY >= 1:
            useful_data += 1
            if useful_data < START_THRESHOLD:
                print(f"countdown to start: {START_THRESHOLD - useful_data}")
                return
            (_, _, _, pL, pM, pH) = struct.unpack('<BBBBBB', data)
            # temp = (tH*65536 + tM*256 + tL) / 100.0
            self.press = (pH*65536 + pM*256 + pL) / 100.0
            self.save_values()
            # print(f"[BarometerSensor] Ambient temp: {temp}; Pressure Millibars: {press}")
            self.received += 1
            if time() - self.start_time > 1:
                print(f"baro count: {self.received}")
                self.start_time = time()

    def save_values(self):
        global baro_count
        with open('./ProjectData/{0}/IndividualSignals/baro_{0}.csv'.format(DATATYPE), 'a') as barofile,\
                    open('./ProjectData/{0}/y_{0}.csv'.format(DATATYPE), 'a') as yfile:
            if baro_count == TIMESTEPS - 1:
                barofile.write(str(self.press))
                barofile.write('\n')
                yfile.write(LABEL)
                yfile.write('\n')
                baro_count = 0
            else:
                barofile.write(str(self.press))
                barofile.write(',')
                baro_count += 1
            


class LEDAndBuzzer(Service):
    """
        Adapted from various sources. Src: https://evothings.com/forum/viewtopic.php?t=1514 and the original TI spec
        from https://processors.wiki.ti.com/index.php/CC2650_SensorTag_User's_Guide#Activating_IO

        Codes:
            1 = red
            2 = green
            3 = red + green
            4 = buzzer
            5 = red + buzzer
            6 = green + buzzer
            7 = all
    """

    def __init__(self):
        super().__init__()
        self.data_uuid = "f000aa65-0451-4000-b000-000000000000"
        self.ctrl_uuid = "f000aa66-0451-4000-b000-000000000000"

    async def notify(self, client, code):
        # enable the config
        write_value = bytearray([0x01])
        await client.write_gatt_char(self.ctrl_uuid, write_value)

        # turn on the red led as stated from the list above using 0x01
        write_value = bytearray([code])
        await client.write_gatt_char(self.data_uuid, write_value)


async def run(address):
    async with BleakClient(address) as client:
        x = await client.is_connected()
        print("Connected: {0}".format(x))

        led_and_buzzer = LEDAndBuzzer()

        barometer_sensor = BarometerSensor()
        await barometer_sensor.start_listener(client)

        acc_sensor = AccelerometerSensorMovementSensorMPU9250()
        gyro_sensor = GyroscopeSensorMovementSensorMPU9250()
        magneto_sensor = MagnetometerSensorMovementSensorMPU9250()

        movement_sensor = MovementSensorMPU9250()
        movement_sensor.register(acc_sensor)
        movement_sensor.register(gyro_sensor)
        movement_sensor.register(magneto_sensor)
        await movement_sensor.start_listener(client)

        cntr = 0

        while True:
            # we don't want to exit the "with" block initiating the client object
            # as the connection is disconnected unless the object is stored
            await asyncio.sleep(1.0)

            if cntr == 0:
                # shine the red light
                await led_and_buzzer.notify(client, 0x01)

            if cntr == 5:
                # shine the green light
                await led_and_buzzer.notify(client, 0x02)

            cntr += 1

            if cntr == 10:
                cntr = 0


if __name__ == "__main__":
    """
    To find the address, once your sensor tag is blinking the green led after pressing the button, run the discover.py
    file which was provided as an example from bleak to identify the sensor tag device
    """

    os.environ["PYTHONASYNCIODEBUG"] = str(1)
    try:
        with open(f"{sys.path[0]}/sensortag_addr.txt") as f:
            address = (
                f.read() 
                if platform.system() != "Darwin"
                else "6FFBA6AE-0802-4D92-B1CD-041BE4B4FEB9"
            )

        print("Generating data for {}, get ready to {}".format(LABEL, LABELTOACTION[LABEL]))

        loop = asyncio.get_event_loop()

        try:
            loop.run_until_complete(run(address))
            loop.run_forever()
        except KeyboardInterrupt:
            loop.stop()
            loop.close()
            print("Received exit, exiting...")
        except Exception as e:
            print(f"exception: {e}")
            
        # finally:
        #     loop.stop()
        #     loop.close()
        #     print("close")
    except FileNotFoundError:
        print("no file named sensortag_addr.txt, create file and input sensortag MAC addr")
    