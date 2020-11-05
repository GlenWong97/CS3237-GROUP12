import asyncio
import platform
import struct
import os

from bleak import BleakClient

conn_params_uuid = "f000ccc1-0451-4000-b000-000000000000"

def callback(self, sender: int, data: bytearray):
        (conn_interval, slave_latency, supervision_timeout) = struct.unpack('<HHH', data)
        print(f"connection interval: {conn_interval}, slave latency: {slave_latency}, supervision timeout: {supervision_timeout}")

async def start_listener(client):
    try:
        data = await client.read_gatt_char(conn_params_uuid)
        (conn_interval, slave_latency, supervision_timeout) = struct.unpack('<HHH', data)
        print(f"connection interval: {conn_interval}, slave latency: {slave_latency}, supervision timeout: {supervision_timeout}")

    except KeyboardInterrupt:
        return
async def run(address):
    try:
        async with BleakClient(address) as client:
            x = await client.is_connected()
            print("Connected: {0}".format(x))

            await start_listener(client)

            await asyncio.sleep(1.0)
    except KeyboardInterrupt:
        return

if __name__ == "__main__":
    os.environ["PYTHONASYNCIODEBUG"] = str(1)
    address = (
        "B0:91:22:F7:01:06" # new
        if platform.system() != "Darwin"
        else "6FFBA6AE-0802-4D92-B1CD-041BE4B4FEB9"
    )

    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(run(address))
        loop.run_forever()
    except KeyboardInterrupt:
        loop.stop()
        loop.close()
        print("Received exit, exiting...")