# -*- coding: utf-8 -*-
"""
TI CC2650 SensorTag
-------------------

Adapted by Ashwin from the following sources:
 - https://github.com/IanHarvey/bluepy/blob/a7f5db1a31dba50f77454e036b5ee05c3b7e2d6e/bluepy/sensortag.py
 - https://github.com/hbldh/bleak/blob/develop/examples/sensortag.py

"""
import asyncio
import datetime
import platform
import struct
import os
import sys

from bleak import BleakClient

# 0: Idle, 1: Nod, 2: Shake, 3: Look up, 4: Tilt
LABEL = '0'
DATA_POINTS = 2000
LABELTOACTION = {
    '0': 'Idle',
    '1': 'Nod',
    '2': 'Shake',
    '3': 'Lookup',
    '4': 'Tilt',
}

# LABELTOACTION = {
#     '0': 'Idle',
#     '1': 'Raise',
#     '2': 'Wave',
#     '3': 'Clap',
#     '4': 'Tilt',
# }

# Coordination global variable
READY = -1
# remove number of data to ensure parallel
START_THRESHOLD = 5
# Datatype: test or train
DATATYPE = "train"

# Number of timesteps for lstm
TIMESTEPS = 5
val_count = 0
useful_data = 0
write_count = 0


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
        # self.period_uuid = None
        # self.freq_bits = bytearray([0x64]) # 1hz
        self.freq_bits = bytearray([0x0A])  # 10hz


class Sensor(Service):

    def callback(self, sender: int, data: bytearray):
        raise NotImplementedError()

    async def enable(self, client, *args):
        # start the sensor on the device
        write_value = bytearray([0x01])
        await client.write_gatt_char(self.ctrl_uuid, write_value)
        await client.write_gatt_char(self.freq_uuid, self.freq_bits)
        # write_value = bytearray([0x0A])
        # await client.write_gatt_char(self.period_uuid, write_value)

        return self

    async def read(self, client):
        val = await client.read_gatt_char(self.data_uuid)
        return self.callback(1, val)


class BarometerSensor(Sensor):
    def __init__(self):
        super().__init__()
        self.data_uuid = "f000aa41-0451-4000-b000-000000000000"
        self.ctrl_uuid = "f000aa42-0451-4000-b000-000000000000"
        self.freq_uuid = "f000aa44-0451-4000-b000-000000000000"

    def callback(self, sender: int, data: bytearray):
        (tL, tM, tH, pL, pM, pH) = struct.unpack('<BBBBBB', data)
        # temp = (tH*65536 + tM*256 + tL) / 100.0
        press = (pH*65536 + pM*256 + pL) / 100.0
        return press


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
    ACCEL_RANGE_2G = 0 << 8
    ACCEL_RANGE_4G = 1 << 8
    ACCEL_RANGE_8G = 2 << 8
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

    async def enable(self, client, *args):
        # start the sensor on the device
        # write_value = bytearray([0x01])
        await client.write_gatt_char(self.freq_uuid, self.freq_bits)
        await client.write_gatt_char(self.ctrl_uuid, struct.pack("<H", self.ctrlBits))
        return self

    async def read(self, client):
        val = await client.read_gatt_char(self.data_uuid)
        return self.callback(1, val)

    def callback(self, sender: int, data: bytearray):
        unpacked_data = struct.unpack("<hhhhhhhhh", data)
        # return unpacked_data
        # for cb in self.sub_callbacks:
        #     cb(unpacked_data)
        accel_vals = self.sub_callbacks[0](unpacked_data)
        gryo_vals = self.sub_callbacks[1](unpacked_data)
        mag_vals = self.sub_callbacks[2](unpacked_data)
        return gryo_vals + accel_vals + mag_vals


class AccelerometerSensorMovementSensorMPU9250(MovementSensorMPU9250SubService):
    def __init__(self):
        super().__init__()
        self.bits = MovementSensorMPU9250.ACCEL_XYZ | MovementSensorMPU9250.ACCEL_RANGE_4G
        self.scale = 8.0/32768.0  # TODO: why not 4.0, as documented? @Ashwin Need to verify

    def cb_sensor(self, data):
        '''Returns (x_accel, y_accel, z_accel) in units of g'''
        rawVals = data[3:6]
        return [(x*self.scale) for x in rawVals]
        # return rawVals


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
        # return rawVals


class GyroscopeSensorMovementSensorMPU9250(MovementSensorMPU9250SubService):
    def __init__(self):
        super().__init__()
        self.bits = MovementSensorMPU9250.GYRO_XYZ
        self.scale = 500.0/65536.0

    def cb_sensor(self, data):
        '''Returns (x_gyro, y_gyro, z_gyro) in units of degrees/sec'''
        rawVals = data[0:3]
        return [(x*self.scale) for x in rawVals]
        # return rawVals


async def run(address):
    async with BleakClient(address) as client:
        x = await client.is_connected()
        print("Connected: {0}".format(x))

        barometer_sensor = await BarometerSensor().enable(client)
        acc_sensor = AccelerometerSensorMovementSensorMPU9250()
        gyro_sensor = GyroscopeSensorMovementSensorMPU9250()
        magneto_sensor = MagnetometerSensorMovementSensorMPU9250()
        movement_sensor = MovementSensorMPU9250()
        movement_sensor.register(acc_sensor)
        movement_sensor.register(gyro_sensor)
        movement_sensor.register(magneto_sensor)
        m_sensor = await movement_sensor.enable(client)
        global val_count, useful_data, write_count

        while (write_count < DATA_POINTS):
            # await asyncio.sleep(0.08)
            data1 = await barometer_sensor.read(client)
            data2 = await m_sensor.read(client)
            # data = await asyncio.gather(light_sensor.read(client), humidity_sensor.read(client))

            # print(data1, data2)
            if useful_data < START_THRESHOLD:
                print(f"countdown: {START_THRESHOLD - useful_data}")
                useful_data += 1
                continue
            elif useful_data == START_THRESHOLD:
                print("You may begin!")
                useful_data += 1
                await asyncio.sleep(1)

            with open('./ProjectData/{0}/IndividualSignals/acc_x_{0}.csv'.format(DATATYPE), 'a') as acc_x_file, \
                    open('./ProjectData/{0}/IndividualSignals/acc_y_{0}.csv'.format(DATATYPE), 'a') as acc_y_file, \
                    open('./ProjectData/{0}/IndividualSignals/acc_z_{0}.csv'.format(DATATYPE), 'a') as acc_z_file, \
                    open('./ProjectData/{0}/IndividualSignals/baro_{0}.csv'.format(DATATYPE), 'a') as baro_file, \
                    open('./ProjectData/{0}/IndividualSignals/gyro_x_{0}.csv'.format(DATATYPE), 'a') as gyro_x_file, \
                    open('./ProjectData/{0}/IndividualSignals/gyro_y_{0}.csv'.format(DATATYPE), 'a') as gyro_y_file, \
                    open('./ProjectData/{0}/IndividualSignals/gyro_z_{0}.csv'.format(DATATYPE), 'a') as gyro_z_file, \
                    open('./ProjectData/{0}/IndividualSignals/mag_x_{0}.csv'.format(DATATYPE), 'a') as mag_x_file, \
                    open('./ProjectData/{0}/IndividualSignals/mag_y_{0}.csv'.format(DATATYPE), 'a') as mag_y_file, \
                    open('./ProjectData/{0}/IndividualSignals/mag_z_{0}.csv'.format(DATATYPE), 'a') as mag_z_file, \
                    open('./ProjectData/{0}/y_{0}.csv'.format(DATATYPE), 'a') as result_file:

                if val_count == TIMESTEPS - 1:
                    gyro_x_file.write("{}\n".format(data2[0]))
                    gyro_y_file.write("{}\n".format(data2[1]))
                    gyro_z_file.write("{}\n".format(data2[2]))
                    acc_x_file.write("{}\n".format(data2[3]))
                    acc_y_file.write("{}\n".format(data2[4]))
                    acc_z_file.write("{}\n".format(data2[5]))
                    mag_x_file.write("{}\n".format(data2[6]))
                    mag_y_file.write("{}\n".format(data2[7]))
                    mag_z_file.write("{}\n".format(data2[8]))
                    baro_file.write("{}\n".format(data1))
                    result_file.write("{}\n".format(LABEL))
                    val_count = 0
                    write_count += 1
                    print(f"writecount: {write_count / TIMESTEPS}")
                else:
                    gyro_x_file.write("{},".format(data2[0]))
                    gyro_y_file.write("{},".format(data2[1]))
                    gyro_z_file.write("{},".format(data2[2]))
                    acc_x_file.write("{},".format(data2[3]))
                    acc_y_file.write("{},".format(data2[4]))
                    acc_z_file.write("{},".format(data2[5]))
                    mag_x_file.write("{},".format(data2[6]))
                    mag_y_file.write("{},".format(data2[7]))
                    mag_z_file.write("{},".format(data2[8]))
                    baro_file.write("{},".format(data1))
                    val_count += 1
                    write_count += 1

        print("Finished training...")


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

        print("Generating data for {}, get ready to {}".format(
            LABEL, LABELTOACTION[LABEL]))

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

        # finally:
        #     loop.stop()
        #     loop.close()
        #     print("close")
    except FileNotFoundError:
        print("no file named sensortag_addr.txt, create file and input sensortag MAC addr")
