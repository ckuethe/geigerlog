#! /usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Sensirion software
"""
# start X11vnc on raspi:  sudo x11vnc -httpport 80 -httpdir /usr/share/novnc/ -no6 -xkb -repeat -auth guess -display WAIT:0 -forever -shared

import time

try:
    from sensirion_i2c_driver import LinuxI2cTransceiver
except Exception as e:
    print("mein print: ", e)
try:
    from sensirion_i2c_driver import I2cConnection
except Exception as e:
    print(e)

print("all imports done")


with LinuxI2cTransceiver('/dev/i2c-1') as i2c_transceiver:
    i2c_connection = I2cConnection(i2c_transceiver)
    print("i2c_connection: ", i2c_connection)

    scd41 = Scd4xI2cDevice(i2c_connection)

    # start periodic measurement in high power mode
    scd41.start_periodic_measurement()

    # Measure every 5 seconds
    while True:
        time.sleep(5)
        co2, temperature, humidity = scd41.read_measurement()
        # use default formatting for printing output:
        print("{}, {}, {}".format(co2, temperature, humidity))
        # custom printing of attributes:
        print("{:d} ppm CO2, {:0.2f} °C ({} ticks), {:0.1f} %RH ({} ticks)".format(
            co2.co2,
            temperature.degrees_celsius, temperature.ticks,
            humidity.percent_rh, humidity.ticks))
    scd41.stop_periodic_measurement()

