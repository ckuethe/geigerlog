#! /usr/bin/env python3
# -*- coding: UTF-8 -*-

"""
test Bluetooth @ OW18E
"""

import time
import asyncio
from bleak import BleakClient

ADDRESS             = "A6:C0:80:E3:85:9D"
CHARACTERISTIC_UUID = "0000fff4-0000-1000-8000-00805f9b34fb"        # Output like: 23 f0 04 00 5b 0f

def notification_handler(sender, data):

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
    if (reading[2] < 0x7fff): measurement = reading[2]
    else:                     measurement = -1 * (reading[2] & 0x7fff)
    print(f"measurement: {measurement / 10**decimal:0.3f}")


async def run(address):

    global lasttime

    client = BleakClient(address)
    async with BleakClient(address) as client:
        lasttime = time.time()
        await client.start_notify(CHARACTERISTIC_UUID, notification_handler)
        await asyncio.sleep(60.0)  #show data for a minute
        await client.stop_notify(CHARACTERISTIC_UUID)


if __name__ == "__main__":
    try:
        loop = asyncio.get_event_loop()
        loop.set_debug(False)
        loop.run_until_complete(run(ADDRESS))
    except KeyboardInterrupt:
        loop.stop()

