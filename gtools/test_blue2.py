#! /usr/bin/env python3
# -*- coding: UTF-8 -*-

"""
test_blue2
"""
# sudo ./owon_multi_cli -a A6:C0:80:94:54:D9 -t cm2100b     # orig
# sudo ./owon_multi_cli -a A6:C0:80:E3:85:9D -t cm2100b     # mod

# AdvertisementData(local_name='BDM',
# service_uuids=['00001800-0000-1000-8000-00805f9b34fb',
#                '00001801-0000-1000-8000-00805f9b34fb',
#                '0000180a-0000-1000-8000-00805f9b34fb',
#                '0000fff0-0000-1000-8000-00805f9b34fb',
#                '00010203-0405-0607-0809-0a0b0c0d1911'
# ]


import sys
import asyncio
import platform
import logging
import keyboard
import csv

from multimeter import *
import matplotlib.pyplot as plt
from bleak import BleakClient

# ADDRESS = (
#     "FC:58:FA:3C:94:16"
# )

ADDRESS = "A6:C0:80:E3:85:9D"

CHARACTERISTIC_UUID = "0000fff4-0000-1000-8000-00805f9b34fb"        # Output: 23 f0 04 00 5b 0f
# CHARACTERISTIC_UUID = "00001801-0000-1000-8000-00805f9b34fb"
# CHARACTERISTIC_UUID = '00001800-0000-1000-8000-00805f9b34fb'
# CHARACTERISTIC_UUID = '0000180a-0000-1000-8000-00805f9b34fb'
# CHARACTERISTIC_UUID = '0000fff0-0000-1000-8000-00805f9b34fb'
# CHARACTERISTIC_UUID = '00010203-0405-0607-0809-0a0b0c0d1911'

dataGraph = []
multimeter = AN9002()
lastDisplayedUnit = ""

def notification_handler(sender, data):
    global dataGraph
    global multimeter
    global lastDisplayedUnit
    """Simple notification handler which prints the data received."""
    print("Data multimeter: {0}".format(data.hex(' ') ))
    data.append(10)
    data.append(13)
    print("Data multimeter: {0}".format(data.hex(' ') ))

    multimeter.SetMeasuredValue(data)
    displayedData = multimeter.GetDisplayedValue()
    if multimeter.overloadFlag:
        displayedData = 99999
        print("Overload")

    unit = multimeter.GetDisplayedUnit()
    if lastDisplayedUnit == "":
        lastDisplayedUnit = unit

    if unit != lastDisplayedUnit:
        lastDisplayedUnit = unit
        dataGraph.clear()
        plt.clf()

    dataGraph.append(displayedData)
    plt.ylabel(unit)
    print(str(displayedData) + " " + unit)


async def run(address):
    client = BleakClient(address)

    try:
        await client.connect()
        await client.start_notify(CHARACTERISTIC_UUID, notification_handler)

        while(1):
            if keyboard.is_pressed("q"):
                print("Shutting down!");
                break;
            else:
                plt.plot(dataGraph, color='b')
                plt.draw()
                plt.pause(0.1)
                await asyncio.sleep(0.5)

    except Exception as e:
        print(e)
    finally:
        await client.stop_notify(CHARACTERISTIC_UUID)
        await client.disconnect()


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.set_debug(False)
    loop.run_until_complete(run(ADDRESS))

    with open('plot.csv', 'w') as f:
        wr = csv.writer(f)
        wr.writerow(dataGraph)
