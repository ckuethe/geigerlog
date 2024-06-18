#!/usr/bin/python3
# -*- coding: UTF-8 -*-

"""
I2C sensor module GDK101 - PIN Diode as Radiation sensor
"""

###############################################################################
#    This file is part of GeigerLog.
#
#    GeigerLog is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    GeigerLog is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with GeigerLog.  If not, see <http://www.gnu.org/licenses/>.
###############################################################################


__author__          = "ullix"
__copyright__       = "Copyright 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024"
__credits__         = [""]
__license__         = "GPL3"


from gsup_utils   import *

# Reference: http://allsmartlab.com/eng/294-2/
# I2C Maximum Speed is 100 kHz.
# Document: AN_GDK101_V1.1_I2C.pdf
#   Gamma sensor module GDK101, www.ftlab.co.kr
#   Revision:       1.1
#   Last-Updated:   22/3/2021
#   Author:         FTLAB
# Document: GDK101datasheet_v1.6.pdf
#   GDK101 ver1.6 Gamma Radiation Sensor Module
#   DS_GDK101_016, www.ftlab.co.kr, 0000564592100ETF8210, June 28, 2016

##
## CAUTION: the GDK101 does need a 5V supply! At 3.3V it appears to be working,
## but count rate comes out as way too high! The GDK101's SDA and SCL signals,
## however, do remain at 3.3V levels, and can be fed directly to a Raspi!
##

## Sensitivity:
## NOTE: the sensor returns count rates reported as µSv/h values!
##       These are converted here to CPM with Sensitivity value of 8.33 CPM/(µSv/h)
##       instead of official value of 12! see my report article
##
## LOW COUNTRATE:   On a Raspi5 with RaspiPulse, SerialPulse, and GDK101 the background was recorded
##                  on both the Ukrainian counter with SBM20, and the GDK101 overnight. All recordings
##                  show proper Poisson.
## RaspiPulse:      CPM=19.074
## SerialPulse:     CPM=19.053
## GDK101:          CPM=0.381   ==> 19.06 / 0.381 = 50.03 times less sensitive than a SBM20
##                                  if SBM20 has Sensitivity 154 CPM/(µSv/h) then GDK101 has 3.08
##                                  much less than what is used here as 8.33 CPM/(µSv/h), which
##                                  is already less than official 12!
##                                  But is it real? is there perhaps less electronic noise than in
##                                  a real Geiger counter???
##
## High COUNTRATE:  On a Raspi5 with RaspiPulse, SerialPulse, and GDK101 some Uranium beads were put on both
##                  the Ukrainian counter with SBM20, and the GDK101.
## RaspiPulse:      CPM=1458
## SerialPulse:     CPM=1455
## GDK101:          CPM=45   ==> 1456 / 45 = 33 times less sensitive than a SBM20 (no good comparison as
##                               same exposure cannot be assured, and GDK101 with metal enclosure might
##                               be less sensitive to beta)


class SensorGDK101:
    """Code for the SmartFTLab GDK101 sensor"""

    addr        = 0x18           # Default option for the GDK101; all options: 0x18, 0x19, 0x1A, 0x1B
    name        = "GDK101"
    firmware    = "not set"      # my device: "0.6" (??? sollte 1.6 sein???)
    handle      = g.I2CDongle    # default for use by 'I2C' device; RaspiI2C defines its own
    sensitivity = 8.33           # instead of occicial value of 12, see NOTE above!
    print2nd    = False          # Print secondary comments


    def __init__(self, addr, I2Chandle=None):
        """Init SensorGDK101 class"""

        self.addr       = addr
        if I2Chandle is not None: self.handle = I2Chandle


    def SensorInit(self):
        """Scan for presence, do, Reset, get Firmware"""

        defname = "SensorInit: " + self.name + ": "
        dmsg    = "Sensor {:8s} at address 0x{:02X}".format(self.name, self.addr)

        # dprint(defname)
        setIndent(1)

        # check for presence of an I2C device at I2C address
        # takes ~0.6 ms
        # start = time.time()
        presence = self.handle.DongleIsSensorPresent(self.addr)
        # dur = 1000 * (time.time() - start)
        # edprint(defname + "dur: ", dur)

        if not presence:
            # no device found
            setIndent(0)
            msg = "Did not find any I2C device at address 0x{:02X}".format(self.addr)
            edprint(defname + msg)
            return  False, msg
        else:
            # device found
            gdprint("Found an I2C device at address 0x{:02X}".format(self.addr))


        # soft reset
        # dprint(defname + "Sensor Reset")
        gdprint(self.SensorReset())

        ## get status
        # dprint(defname + "Get Status")
        gdprint(self.SensorgetStatus())

        ## get firmware version
        # dprint(defname + "Get Firmware")
        gdprint(self.SensorgetFirmwareVersion())

        setIndent(0)

        return (True,  "Initialized " + dmsg)


    def SensorgetStatus(self):
        """get Status Power and Vibration"""

        # Read the status of power and vibration
        # CMD   Description                 Read Data 1             Read Data 2
        # 0xB0  Read the status of          0 - Power On ~ 10sec    0 - Not detect vibrations
        #       measurement and vibration   1 - 10sec to 10min      1 - Detect vibrations
        #                                   2 - after 10 min

        # Duration:
        # ISS: SensorgetStatus: duration: 1.5 ms
        # ELV: SensorgetStatus: duration:

        start   = time.time()
        defname = "SensorgetStatus: " + self.name + ": "
        # dprint(defname)

        tmsg      = "Status"
        register  = 0xB0
        readbytes = 2
        data      = []
        wait      = 0   #0.01 # sec
        answ      = self.handle.DongleWriteRead (self.addr, register, readbytes, data, addrScheme=1, msg=tmsg, wait=wait)

        if len(answ) == readbytes:
            # ok
            status = "{} - {}".format(answ[0], answ[1])
        else:
            # FAILURE
            status = "FAILURE reading Status"
            edprint(defname + status + ", reponse: ", answ)

        duration = (time.time() - start) * 1000
        msg = defname + "got status: {}  in: {:0.1f} ms".format(status, duration)

        return msg


    def SensorgetFirmwareVersion(self):
        """get the Firmware Version as Major.Minor"""

        # Read firmware version
        # CMD   Description             Read Data 1         Read Data 2
        # 0xB4  Read Firmware Version   Main of version     Sub of version

        # Duration:
        # ISS: SensorgetFirmwareVersion: duration: 1.4 ms
        # ELV: SensorgetFirmwareVersion: duration:

        start     = time.time()
        defname   = "SensorgetFirmwareVersion: " + self.name + ": "
        # dprint(defname)

        tmsg      = "FirmWr"
        register  = 0xB4
        readbytes = 2
        data      = []
        wait      = 0   #0.01
        answ      = self.handle.DongleWriteRead (self.addr, register, readbytes, data, addrScheme=1, msg=tmsg, wait=wait)

        if len(answ) == readbytes:
            # ok
            self.firmware = "{}.{}".format(answ[0], answ[1])
        else:
            # FAILURE
            self.firmware = "Failure reading Firmware"
            edprint(defname + self.firmware + ", reponse: ", answ)

        duration = (time.time() - start) * 1000
        msg = defname + "got firmware: {}  in: {:0.1f} ms".format(self.firmware, duration)

        return msg


    def SensorgetMeasuringTime(self):
        """get the Measuring Time in minutes"""

        # Read Measuring Time
        # CMD   Description             Read Data 1         Read Data 2
        # 0xB1  Read Measuring Time     Minutes of time     Seconds of time
        # NOTE: time increases up to 10 (min) and then goes up to 11 (min) and resets to 10 (min), and so on.
        #       on return time is converted to seconds

        # Duration:
        # ISS:    duration: 1.8 ms
        # ELV:    duration:
        # Raspi5: duration: 0.8 ... 0.85 ms

        start     = time.time()
        defname   = "SensorgetMeasuringTime: " + self.name + ": "
        # dprint(defname)

        tmsg      = "mtime"
        register  = 0xB1        # Read measuring time
        readbytes = 2
        data      = []
        wait      = 0   #0.01
        answ      = self.handle.DongleWriteRead (self.addr, register, readbytes, data, addrScheme=1, msg=tmsg, wait=wait)

        if len(answ) == readbytes:
            value = (answ[0] * 60 + answ[1])                        # (minutes * 60 + seconds) ==> seconds
            msg   = defname + "answ: {}->{}:{:<3.0f} sec".format(answ, tmsg, value)
            bmsg  = True, msg
            value = (round(value, 5))
        else:
            msg   = defname + "Failure reading proper byte count"
            bmsg  = False, msg
            value = g.NAN

        duration  = (time.time() - start) * 1000
        pmsg      = msg + "  dur:{:0.2f} ms".format(duration)
        if bmsg[0] and self.print2nd:  gdprint(pmsg)
        # else:        edprint(pmsg)
        if not bmsg[0]:                edprint(pmsg)

        return value


    def SensorReset(self):
        """Soft Reset GDK101 sensor"""

        # Reset
        # CMD   Description             Read Data 1         Read Data 2
        # 0xA0  Reset                   0 - Fail            Not used
        #                               1 - Pass
        #
        # Duration:
        # ISS: SensorReset:    duration: 1003 ms
        # ELV: SensorReset:    duration:

        start   = time.time()
        defname = "SensorReset: " + self.name + ": "
        # dprint(defname)

        tmsg      = "Reset"
        register  = 0xA0
        readbytes = 2
        data      = []
        wrt       = self.handle.DongleWriteReg(self.addr, register, readbytes, data, addrScheme=1, msg=tmsg)
        # time.sleep(2)
        answ      = self.handle.DongleGetData(self.addr, register, readbytes, data, addrScheme=1, msg=tmsg)

        duration = 1000 * (time.time() - start)
        msg = defname + "answ: {}  took {:0.1f} ms".format(answ, duration)

        return msg


    def SensorgetValues(self):
        """Read the count rate values for 1 and 10 min"""

# 1min  # Read Measured Value 1 min
        # this is CPM over 1 min, which is updated every 1 min, and at this value constant for 1min
        # First value after 1 min (CPM from 0 ... <1 min is == 0)
        #
        # CMD   Description                 Read Data 1         Read Data 2
        # 0xB3  Read Measured Value         Integer of value    Decimal of value
        #       (1min avg. 1min update)
        #
        #
        # Duration:
        # ISS: SensorgetValues:  1 min    duration: 2.3 ms
        # ELV: SensorgetValues:  1 min    duration:
        #

# 10min # Read Measured Value 10 min
        # this is CPM averaged over 10 min, which is updated every 1 min, and at this value constant for 1min
        # First value after 1 min (this being the same as CPM 1 min value)
        #
        # CMD   Description                 Read Data 1         Read Data 2
        # 0xB2  Read Measured Value         Integer of value    Decimal of value
        #       (10min avg. 1min update)
        #
        # Duration:
        # ISS: SensorgetValues: 10 min    duration: 4.2 ms
        # ELV: SensorgetValues: 10 min    duration:
        #


        start   = time.time()
        defname = "SensorgetValues: " + self.name + ": "
        # cdprint(defname)
        setIndent(1)

        cpm     = g.NAN
        cpm10   = g.NAN
        mtime   = g.NAN

# 1 min CPM
        tmsg      = "get1min"
        register  = 0xB3
        readbytes = 2
        data      = []
        wait      = 0   #0.01
        answ      = self.handle.DongleWriteRead (self.addr, register, readbytes, data, addrScheme=1, msg=tmsg, wait=wait)
        # edprint(defname + "answ: ", answ)

        if len(answ) == readbytes:
            value = answ[0] + (answ[1] / 100)               # ist µSv value, not CPM
            cpm   = round(value * self.sensitivity, 0)      # convert to CPM

            msg   = defname + "answ:{}->{}:{:<6.2f}  CPM:{}".format(answ, tmsg, value, cpm)
            bmsg  = True, msg
        else:
            msg   = defname + "Failure reading proper byte count"
            bmsg  = False, msg

        duration = (time.time() - start) * 1000
        if bmsg[0] and self.print2nd:      gdprint(msg + "  dur:{:0.2f} ms".format(duration))


# 10 min CPM average
        tmsg      = "get10m "
        register  = 0xB2
        readbytes = 2
        data      = []
        wait      = 0   #0.01
        answ      = self.handle.DongleWriteRead (self.addr, register, readbytes, data, addrScheme=1, msg=tmsg, wait=wait)

        if len(answ) == readbytes:
            value = answ[0] + (answ[1] / 100)               # ist µSv value, not CPM
            cpm10 = round(value * self.sensitivity, 0)      # convert to CPM

            msg  = defname + "answ:{}->{}:{:<6.2f}  CPM:{}".format(answ, tmsg, value, cpm10)
            bmsg = True, msg
        else:
            msg  = defname + "Failure reading proper byte count"
            bmsg = False, msg

        duration = (time.time() - start) * 1000
        if bmsg[0] and self.print2nd:      gdprint(msg + "  dur:{:0.2f} ms".format(duration))

# Measuring time
        # other
        mtime    = self.SensorgetMeasuringTime()

        setIndent(0)
        return (cpm, cpm10, mtime)


    def SensorGetInfo(self):

        info  = "{}\n"                             .format("Count Rate")
        info += "- Address:         0x{:02X}\n"    .format(self.addr)
        info += "- Firmware:        {}\n"          .format(self.firmware)
        info += "- Variables:       {}\n"          .format(", ".join("{}".format(x) for x in g.Sensors["GDK101"][5]))

        return info.split("\n")

