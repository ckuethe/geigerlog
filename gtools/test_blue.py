#! /usr/bin/env python3
# -*- coding: UTF-8 -*-

"""
test Bluetooth on OW18E
"""

import time
import asyncio
from bleak import BleakClient

ADDRESS = "A6:C0:80:E3:85:9D"

CHARACTERISTIC_UUID = "0000fff4-0000-1000-8000-00805f9b34fb"        # Output: 23 f0 04 00 5b 0f
# CHARACTERISTIC_UUID = "00001801-0000-1000-8000-00805f9b34fb"      # Generic Attribute
# CHARACTERISTIC_UUID = '00001800-0000-1000-8000-00805f9b34fb'      # Generic Access
# CHARACTERISTIC_UUID = '0000180a-0000-1000-8000-00805f9b34fb'      # Device Information
# CHARACTERISTIC_UUID = '0000fff0-0000-1000-8000-00805f9b34fb'      # Unknown
# CHARACTERISTIC_UUID = '00010203-0405-0607-0809-0a0b0c0d1911'      # Proprietary

def notification_handler(sender, data):
    # Simple notification handler which prints the data received

    global lasttime

    nowtime = time.time()
    print(f"{nowtime - lasttime:0.3f} sec   Data OW18E: {data.hex(' ')}", end = "  ")
    print("value: ", data[5] <<8 |data[4], end="   ")
    lasttime = nowtime

    # Owon meter logic (from: https://github.com/sercona/Owon-Multimeters/blob/main/owon_multi_cli.c)
    reading =  [0, 0, 0]

    # convert bytes to 'reading' array
    reading[0] = data[1] << 8 | data[0]
    reading[1] = data[3] << 8 | data[2]
    reading[2] = data[5] << 8 | data[4]

    # Extract data items from first field
    function = (reading[0] >> 6) & 0x0f
    scale    = (reading[0] >> 3) & 0x07
    decimal  = reading[0] & 0x07

    # Extract and convert measurement value (sign)
    if (reading[2] < 0x7fff):     measurement = reading[2]
    else:                         measurement = -1 * (reading[2] & 0x7fff)

    print(f"measurement: {measurement / 10**decimal:0.3f}", end="  ")
    print(f"function: {function}  scale: {scale}  decimal: {decimal}")


async def run(address):
    global lasttime

    client = BleakClient(address)
    async with BleakClient(address) as client:
        lasttime = time.time()
        await client.start_notify(CHARACTERISTIC_UUID, notification_handler)
        N = 60
        await asyncio.sleep(N)  #show data for N sec
        await client.stop_notify(CHARACTERISTIC_UUID)



if __name__ == "__main__":
    try:
        loop = asyncio.get_event_loop()
        loop.set_debug(False)
        loop.run_until_complete(run(ADDRESS))
        # loop.create_future()
        # asyncio.run(ADDRESS)
        # loop.run_forever()
    except KeyboardInterrupt:
        loop.stop()




############################################################################################################



"""
test Bluetooth on OW18E with pygatt

"""
# import sys, time
import pygatt                           # https://pypi.org/project/pygatt/
                                        # pip install pygatt
                                        # pip install "pygatt[GATTTOOL]"
                                        # pip install git+https://github.com/peplin/pygatt
                                        # Can’t find BGAPI device in Windows --> see website
# import logging
# logging.basicConfig()
# logging.getLogger('pygatt').setLevel(logging.DEBUG)


lasttime = time.time()
# adapter = pygatt.GATTToolBackend()
# adapter = pygatt.BGAPIBackend()   # does not work

def GATThandle_data(handle, data):
    """
    handle -- integer, characteristic read handle the data was received on
    value  -- bytearray, the data returned in the notification
    """

    global lasttime

    defname = "handle_data: "
    print(defname, end= "  ")

    nowtime = time.time()
    dur     = 1000 * (nowtime - lasttime)
    g.Bluetoothdur = dur
    print(f"{nowtime - lasttime:0.3f} sec   Data OW18E: {data.hex(' ')}", end = "  ")
    print("value: ", data[5] <<8 |data[4], end="   ")
    lasttime = nowtime

    # Owon meter logic (from: https://github.com/sercona/Owon-Multimeters/blob/main/owon_multi_cli.c)
    reading =  [0, 0, 0]

    # convert bytes to 'reading' array
    reading[0] = data[1] << 8 | data[0]
    reading[1] = data[3] << 8 | data[2]
    reading[2] = data[5] << 8 | data[4]

    # Extract data items from first field
    function = (reading[0] >> 6) & 0x0f
    scale    = (reading[0] >> 3) & 0x07
    decimal  = reading[0]        & 0x07
    # print(f"function: {function}  scale: {scale}  decimal: {decimal}")

    # Extract and convert measurement value (sign)
    if (reading[2] < 0x7fff):     measurement = reading[2]
    else:                         measurement = -1 * (reading[2] & 0x7fff)

    result = measurement / 10**decimal
    print(f"measurement: {result:0.3f}")

    g.RadProGATT = result


# def GATTmain():
#     global lasttime, adapter

#     lasttime = time.time()
#     adapter = pygatt.GATTToolBackend()
#     adapter.start()
#     device = adapter.connect("A6:C0:80:E3:85:9D")
#     device.subscribe("0000fff4-0000-1000-8000-00805f9b34fb", callback=GATThandle_data)


# if __name__ == "__main__":
#     try:
#         main()
#         while True: time.sleep(1)
#     except KeyboardInterrupt:
#         adapter.stop()



def GATTThread_Target(args):
    """The thread to read the variables from the device via Bluetooth"""

    defname = "GATTThread_Target: "
    rdprint(defname, "args: ", args)

    global lasttime, adapter

    lasttime = time.time()
    adapter = pygatt.GATTToolBackend()
    adapter.start()
    device = adapter.connect("A6:C0:80:E3:85:9D")
    device.subscribe("0000fff4-0000-1000-8000-00805f9b34fb", callback=GATThandle_data)

    while g.GATTThreadRun:
        time.sleep(0.05)
        ydprint("GATT Runde")


