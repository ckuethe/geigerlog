#! /usr/bin/env python
# -*- coding: UTF-8 -*-

import smbus as smbus
# import smbus2 as smbus

I2Chandle = smbus.SMBus(1)
rtest = I2Chandle.read_byte(0x62)     # SCD41:  FAILS with ERRNO 121

