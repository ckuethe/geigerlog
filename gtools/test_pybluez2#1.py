#! /usr/bin/env python3
# -*- coding: UTF-8 -*-

"""
test Bluetooth on OW18E with pygatt

"""
import sys, time
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

def handle_data(handle, data):
    """
    handle -- integer, characteristic read handle the data was received on
    value  -- bytearray, the data returned in the notification
    """

    global lasttime

    defname = "handle_data: "
    print(defname, end= "  ")

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
    decimal  = reading[0]        & 0x07

    # Extract and convert measurement value (sign)
    if (reading[2] < 0x7fff):     measurement = reading[2]
    else:                         measurement = -1 * (reading[2] & 0x7fff)

    result = measurement / 10**decimal
    print(f"measurement: {result:0.3f}")


def main():
    global lasttime, adapter

    lasttime = time.time()
    adapter = pygatt.GATTToolBackend()
    adapter.start()
    device = adapter.connect("A6:C0:80:E3:85:9D")
    device.subscribe("0000fff4-0000-1000-8000-00805f9b34fb", callback=handle_data)


if __name__ == "__main__":
    try:
        main()
        while True: time.sleep(1)
    except KeyboardInterrupt:
        adapter.stop()
