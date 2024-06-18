#! /usr/bin/env python3
# -*- coding: UTF-8 -*-

"""
gdev_gmc.py - GeigerLog commands to handle the Geiger counter

include in programs with:
    import gdev_gmc
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
__credits__         = ["Phil Gillaspy", "GQ"]
__license__         = "GPL3"

# credits:
# device command coding taken from:
# - Phil Gillaspy, https://sourceforge.net/projects/gqgmc/
# - and GQ documents
#     'GQ-RFC1201 GMC Communication Protocol. Re. 1.30'
# -   'GQ-RFC1201,GQ Ver 1.40 Jan-2015' http://www.gqelectronicsllc.com/downloads/download.asp?DownloadID=62
# -   'GQ-RFC1801 GMC Communication Protocol' http://www.gqelectronicsllc.com/downloads/download.asp?DownloadID=91
# -   GQ's disclosure at: http://www.gqelectronicsllc.com/forum/topic.asp?TOPIC_ID=4948

# GMC memory configs:
# For listing of GMC memory configs see file: 'GMC_memory_config, 2018-2024-v4.ods'
# in folder: /home/ullix/geigerlog/evaluation/Geiger Counter - GMC-All Config memory

from gsup_utils   import *


# Data only in the 1st 256 byte config (all counters)
cfgKeyLoDefault = {
#
#    key                    Value,     Index width
    "Power"             : [ None,     [0,        1] ],     # Power state (read only, not settable!)
    "Alarm"             : [ None,     [1,        1] ],     # Alarm state
    "Speaker"           : [ None,     [2,        1] ],     # Speaker state
    "BackLightTOSec"    : [ None,     [4,        1] ],     # see Light States (OFF ... 30, 6 states)
    "AlarmCPMValue"     : [ None,     [6,        2] ],     # AlarmlevelCPM (Hi, Lo Byte)
    "CalibCPM_0"        : [ None,     [8,        2] ],     # calibration_0 CPM Hi+Lo Byte
    "CalibuSv_0"        : [ None,     [10,       4] ],     # calibration_0 uSv 4 Byte
    "CalibCPM_1"        : [ None,     [14,       2] ],     # calibration_1 CPM Hi+Lo Byte
    "CalibuSv_1"        : [ None,     [16,       4] ],     # calibration_1 uSv 4 Byte
    "CalibCPM_2"        : [ None,     [20,       2] ],     # calibration_2 CPM Hi+Lo Byte
    "CalibuSv_2"        : [ None,     [22,       4] ],     # calibration_2 uSv 4 Byte
    "AlarmValueuSv"     : [ None,     [27,       4] ],     # Alarm Value in units of uSv/h, 4 bytes
    "AlarmType"         : [ None,     [31,       1] ],     # Alarmtype: CPM (=0) or µSv/h (=1)
    "SaveDataType"      : [ None,     [32,       1] ],     # History Save Data Type, see savedatatypes
    "MaxCPM"            : [ None,     [49,       2] ],     # MaxCPM Hi + Lo Byte
    "LCDBackLightLevel" : [ None,     [53,       1] ],     # Backlightlevel; seems to go from 0 ... 20
    "Battery"           : [ None,     [56,       1] ],     # Battery Type: 1 is non rechargeable. 0 is chargeable.
    "Baudrate"          : [ None,     [57,       1] ],     # Baudrate, coded differently for 300 and 500/600 series
    "ThresholdCPM"      : [ None,     [62,       2] ],     # yes, at 62! Threshold in CPM               (2 bytes)
    "ThresholdMode"     : [ None,     [64,       1] ],     # yes, at 64! Mode: 0:CPM, 1:µSv/h, 2:mR/h   (1 byte)
    "ThresholduSv"      : [ None,     [65,       4] ],     # yes, at 65! Threshold in µSv               (4 bytes)
}
cfgKeyLo = cfgKeyLoDefault.copy()    # shallow copy


# Data all 512 bytes of config (even allowing counters having only 256 bytes)
# cfgKeyHiDefault = {
# # cfgHiIndex:               0       1        2           3           4           5           6           7
# #                           GLcfg   counter  GMC-300(E)  GMC-320+V5  GMC-500     GMC500+     GMC-300S    GMC-800
# #                                            only        only        GMC-600     2.24        no WiFi     no WiFi,
# #                                                                                            but FET     FET,Cal6
#     "SSID"              : [ None,   None,    (253,  0),  (69,  16),  (69,  32),  (69,  64),  (253,  0),  (508,  0) ],  # user specific value
#     "Password"          : [ None,   None,    (253,  0),  (85,  16),  (101, 32),  (133, 64),  (253,  0),  (508,  0) ],  # user specific value
#     "Website"           : [ None,   None,    (253,  0),  (101, 25),  (133, 32),  (197, 32),  (253,  0),  (508,  0) ],  # default: www.gmcmap.com
#     "URL"               : [ None,   None,    (253,  0),  (126, 12),  (165, 32),  (229, 32),  (253,  0),  (508,  0) ],  # default: log2.asp
#     "UserID"            : [ None,   None,    (253,  0),  (138, 12),  (197, 32),  (261, 32),  (253,  0),  (508,  0) ],  # user specific value
#     "CounterID"         : [ None,   None,    (253,  0),  (150, 12),  (229, 32),  (293, 32),  (253,  0),  (508,  0) ],  # user specific value
#     "Period"            : [ None,   1,       (253,  0),  (162,  1),  (261,  1),  (325,  1),  (251,  1),  (508,  0) ],  # value can be 1 ... 255
#     "WiFi"              : [ None,   False,   (253,  0),  (163,  1),  (262,  1),  (326,  1),  (253,  1),  (508,  0) ],  # WiFi On=1 Off=0

#     "FET"               : [ None,   60,      (253,  0),  (253,  0),  (508,  1),  (328,  1),  ( 69,  1),  ( 69,  1) ],  # FET
#     "RTC_OFFSET"        : [ None,   0,       (253,  0),  (253,  0),  (508,  1),  (328,  1),  (253,  0),  (508,  0) ],  # RTC_OFFSET -59 sec ... +59sec
#     "DEADTIME_ENABLE"   : [ None,   False,   (253,  0),  (253,  0),  (508,  1),  (335,  1),  (253,  1),  (508,  0) ],  # enable dead time setting (fw 2.41+)
#     "DEADTIME_TUBE1"    : [ None,   0,       (253,  0),  (253,  2),  (508,  2),  (336,  2),  (253,  2),  (508,  0) ],  # DEADTIME_TUBE1_HIBYTE, LOBYTE
#     "DEADTIME_TUBE2"    : [ None,   0,       (253,  0),  (253,  2),  (508,  2),  (338,  2),  (253,  2),  (508,  0) ],  # DEADTIME_TUBE2_HIBYTE, LOBYTE
#     "TARGET_HV"         : [ None,   None,    (253,  0),  (253,  2),  (508,  2),  (346,  2),  (253,  2),  (508,  0) ],  # Voltage read out
#     "HV_CALIB"          : [ None,   None,    (253,  0),  (253,  0),  (508,  1),  (348,  1),  (253,  1),  (508,  0) ],  # HV_CALIB (?)
#     "DATETIME"          : [ None,   None,    ( 62,  6),  (253,  0),  (379,  6),  (379,  6),  ( 70,  6),  (508,  0) ],  # DateTime (for what?) YY,MM,DD,hh,mm,ss

#     "Cal6CPM_0"         : [ None,   None,    (253,  0),  (253,  0),  (508,  0),  (508,  0),  (251,  4),  (73,   4) ],  # Calibration CPM for 6 point calib
#     "Cal6CPM_1"         : [ None,   None,    (253,  0),  (253,  0),  (508,  0),  (508,  0),  (251,  4),  (77,   4) ],  # Calibration CPM for 6 point calib
#     "Cal6CPM_2"         : [ None,   None,    (253,  0),  (253,  0),  (508,  0),  (508,  0),  (251,  4),  (81,   4) ],  # Calibration CPM for 6 point calib
#     "Cal6CPM_3"         : [ None,   None,    (253,  0),  (253,  0),  (508,  0),  (508,  0),  (251,  4),  (85,   4) ],  # Calibration CPM for 6 point calib
#     "Cal6CPM_4"         : [ None,   None,    (253,  0),  (253,  0),  (508,  0),  (508,  0),  (251,  4),  (89,   4) ],  # Calibration CPM for 6 point calib
#     "Cal6CPM_5"         : [ None,   None,    (253,  0),  (253,  0),  (508,  0),  (508,  0),  (251,  4),  (93,   4) ],  # Calibration CPM for 6 point calib
#     "Cal6uSv_0"         : [ None,   None,    (253,  0),  (253,  0),  (508,  0),  (508,  0),  (251,  4),  (97,   4) ],  # Calibration uSv for 6 point calib
#     "Cal6uSv_1"         : [ None,   None,    (253,  0),  (253,  0),  (508,  0),  (508,  0),  (251,  4),  (101,  4) ],  # Calibration uSv for 6 point calib
#     "Cal6uSv_2"         : [ None,   None,    (253,  0),  (253,  0),  (508,  0),  (508,  0),  (251,  4),  (105,  4) ],  # Calibration uSv for 6 point calib
#     "Cal6uSv_3"         : [ None,   None,    (253,  0),  (253,  0),  (508,  0),  (508,  0),  (251,  4),  (109,  4) ],  # Calibration uSv for 6 point calib
#     "Cal6uSv_4"         : [ None,   None,    (253,  0),  (253,  0),  (508,  0),  (508,  0),  (251,  4),  (113,  4) ],  # Calibration uSv for 6 point calib
#     "Cal6uSv_5"         : [ None,   None,    (253,  0),  (253,  0),  (508,  0),  (508,  0),  (251,  4),  (117,  4) ],  # Calibration uSv for 6 point calib
# }


cfgKeyHiDefault = {
# cfgHiIndex:               0       1        2           3           4           5           6           7          8
#                           GLcfg   counter  GMC-300(E)  GMC-320+V5  GMC-500     GMC500+     GMC-300S    GMC-800    GMC-500
#                                            only        only        GMC-600     2.24        no WiFi     no WiFi,   GMC-600,
#                                                                                            but FET     FET,Cal6
    "SSID"              : [ None,   None,    (253,  0),  (69,  16),  (69,  32),  (69,  64),  (253,  0),  (508,  0), (69,  64) ],  # user specific value
    "Password"          : [ None,   None,    (253,  0),  (85,  16),  (101, 32),  (133, 64),  (253,  0),  (508,  0), (133, 64) ],  # user specific value
    "Website"           : [ None,   None,    (253,  0),  (101, 25),  (133, 32),  (197, 32),  (253,  0),  (508,  0), (197, 32) ],  # default: www.gmcmap.com
    "URL"               : [ None,   None,    (253,  0),  (126, 12),  (165, 32),  (229, 32),  (253,  0),  (508,  0), (229, 32) ],  # default: log2.asp
    "UserID"            : [ None,   None,    (253,  0),  (138, 12),  (197, 32),  (261, 32),  (253,  0),  (508,  0), (261, 32) ],  # user specific value
    "CounterID"         : [ None,   None,    (253,  0),  (150, 12),  (229, 32),  (293, 32),  (253,  0),  (508,  0), (293, 32) ],  # user specific value
    "Period"            : [ None,   1,       (253,  0),  (162,  1),  (261,  1),  (325,  1),  (251,  1),  (508,  0), (325,  1) ],  # value can be 1 ... 255
    "WiFi"              : [ None,   False,   (253,  0),  (163,  1),  (262,  1),  (326,  1),  (253,  1),  (508,  0), (326,  1) ],  # WiFi On=1 Off=0

    "FET"               : [ None,   60,      (253,  0),  (253,  0),  (508,  1),  (328,  1),  ( 69,  1),  ( 69,  1), (328,  1) ],  # FET
    "RTC_OFFSET"        : [ None,   0,       (253,  0),  (253,  0),  (508,  1),  (328,  1),  (253,  0),  (508,  0), (508,  0) ],  # RTC_OFFSET -59 sec ... +59sec
    "DEADTIME_ENABLE"   : [ None,   False,   (253,  0),  (253,  0),  (508,  1),  (335,  1),  (253,  1),  (508,  0), (508,  0) ],  # enable dead time setting (fw 2.41+)
    "DEADTIME_TUBE1"    : [ None,   0,       (253,  0),  (253,  2),  (508,  2),  (336,  2),  (253,  2),  (508,  0), (508,  0) ],  # DEADTIME_TUBE1_HIBYTE, LOBYTE
    "DEADTIME_TUBE2"    : [ None,   0,       (253,  0),  (253,  2),  (508,  2),  (338,  2),  (253,  2),  (508,  0), (508,  0) ],  # DEADTIME_TUBE2_HIBYTE, LOBYTE
    "TARGET_HV"         : [ None,   None,    (253,  0),  (253,  2),  (508,  2),  (346,  2),  (253,  2),  (508,  0), (346,  2) ],  # Voltage read out
    "HV_CALIB"          : [ None,   None,    (253,  0),  (253,  0),  (508,  1),  (348,  1),  (253,  1),  (508,  0), (348,  1) ],  # HV_CALIB (?)
    "DATETIME"          : [ None,   None,    ( 62,  6),  (253,  0),  (379,  6),  (379,  6),  ( 70,  6),  (508,  0), (508,  0) ],  # DateTime (for what?) YY,MM,DD,hh,mm,ss

    "Cal6CPM_0"         : [ None,   None,    (253,  0),  (253,  0),  (508,  0),  (508,  0),  (251,  4),  (73,   4), (379,  4) ],  # Calibration CPM for 6 point calib
    "Cal6CPM_1"         : [ None,   None,    (253,  0),  (253,  0),  (508,  0),  (508,  0),  (251,  4),  (77,   4), (383,  4) ],  # Calibration CPM for 6 point calib
    "Cal6CPM_2"         : [ None,   None,    (253,  0),  (253,  0),  (508,  0),  (508,  0),  (251,  4),  (81,   4), (387,  4) ],  # Calibration CPM for 6 point calib
    "Cal6CPM_3"         : [ None,   None,    (253,  0),  (253,  0),  (508,  0),  (508,  0),  (251,  4),  (85,   4), (391,  4) ],  # Calibration CPM for 6 point calib
    "Cal6CPM_4"         : [ None,   None,    (253,  0),  (253,  0),  (508,  0),  (508,  0),  (251,  4),  (89,   4), (395,  4) ],  # Calibration CPM for 6 point calib
    "Cal6CPM_5"         : [ None,   None,    (253,  0),  (253,  0),  (508,  0),  (508,  0),  (251,  4),  (93,   4), (399,  4) ],  # Calibration CPM for 6 point calib
    "Cal6uSv_0"         : [ None,   None,    (253,  0),  (253,  0),  (508,  0),  (508,  0),  (251,  4),  (97,   4), (403,  4) ],  # Calibration uSv for 6 point calib
    "Cal6uSv_1"         : [ None,   None,    (253,  0),  (253,  0),  (508,  0),  (508,  0),  (251,  4),  (101,  4), (407,  4) ],  # Calibration uSv for 6 point calib
    "Cal6uSv_2"         : [ None,   None,    (253,  0),  (253,  0),  (508,  0),  (508,  0),  (251,  4),  (105,  4), (411,  4) ],  # Calibration uSv for 6 point calib
    "Cal6uSv_3"         : [ None,   None,    (253,  0),  (253,  0),  (508,  0),  (508,  0),  (251,  4),  (109,  4), (415,  4) ],  # Calibration uSv for 6 point calib
    "Cal6uSv_4"         : [ None,   None,    (253,  0),  (253,  0),  (508,  0),  (508,  0),  (251,  4),  (113,  4), (419,  4) ],  # Calibration uSv for 6 point calib
    "Cal6uSv_5"         : [ None,   None,    (253,  0),  (253,  0),  (508,  0),  (508,  0),  (251,  4),  (117,  4), (423,  4) ],  # Calibration uSv for 6 point calib
}
cfgKeyHi = cfgKeyHiDefault.copy()    # shallow copy


# the History mode of saving
savedatatypes = (
                    "OFF (no history saving)",
                    "CPS, save every second",
                    "CPM, save every minute",
                    "CPM, save hourly average",
                    "CPS, save every second if exceeding threshold",
                    "CPM, save every minute if exceeding threshold",
                )

# Light states
LightState    = (
                    "Light: OFF",
                    "Light: ON",
                    "Timeout: 1",
                    "Timeout: 3",
                    "Timeout: 10",
                    "Timeout: 30",
                )

# to keep track of illegal entries in cal* fields
validMatrix   = {
                    "cal0cpm" : True ,
                    "cal0usv" : True ,
                    "cal1cpm" : True ,
                    "cal1usv" : True ,
                    "cal2cpm" : True ,
                    "cal2usv" : True ,
                }


def initGMC():
    """
    Sets configuration, gets counter version, verifies communication
    Return: on success: ""
            on failure: <errmessage>
    """

    ## local ###################################################################################

    def getGMC_SerialPorts(device):
        """
        gets all USB-to-Serial port names which MATCH USB's vid + pid associated with device.
        """

        # output by: lsusb
        # NOTE: all have idVendor 0x1a86 and idProduct 0x7523 !
        # GMC-300E+:
        #   bcdUSB                 1.10
        #   idVendor             0x1a86 QinHeng Electronics
        #   idProduct            0x7523 HL-340 USB-Serial adapter
        #   iProduct                  2 USB Serial
        #
        # GMC-300S: (and also GMC-320S ?)
        #     bcdUSB               1.10
        #     idVendor           0x1a86 QinHeng Electronics
        #     idProduct          0x7523 CH340 serial converter
        #     iProduct                2 USB Serial
        #
        # GMC-500+:
        #   bcdUSB                 1.10
        #   idVendor             0x1a86 QinHeng Electronics
        #   idProduct            0x7523 HL-340 USB-Serial adapter
        #   iProduct                  2 USB2.0-Serial


        defname = "getGMC_SerialPorts: "

        dprint(defname, "for device: '{}'".format(device))
        setIndent(1)

        PortsFound  = []
        ports       = getPortList(symlinks=False)
        for port in ports:
            dprint(defname, "port: ", port)

            if g.GMC_simul:
                # simulation
                PortsFound.append(port.device)
            else:
                # use real data from USB port
                if port.vid == 0x1a86 and port.pid == 0x7523:
                    tmplt_match = "Found Chip ID match for device '{}' at: Port:'{}' - vid:0x{:04x}, pid:0x{:04x}"
                    gdprint(defname, tmplt_match.format(device, port, port.vid, port.pid))
                    PortsFound.append(port.device)
                else:
                    dprint(defname, "Chip ID does not match")

        setIndent(0)
        return PortsFound


    def getGMC_SerialBaudrate(usbport):
        """
        Uses the provided usbport and tries to find a proper baudrate by testing for successful
        serial communication at up to all possible baudrates, beginning with the highest.
        return: returnBR = None     :   serial error
                returnBR = 0        :   No device found
                returnBR = <number> :   highest baudrate which worked
        """

        # NOTE: the device port can be opened without error at any baudrate permitted by the Python code,
        # even when no communication can be done, e.g. due to wrong baudrate. Therefore we test for
        # successful communication by checking for the return string for getVersion beginning with 'GMC'.

        defname = "getGMC_SerialBaudrate: "

        dprint(defname, "Testing port: '{}'".format(usbport))
        setIndent(1)

        baudrates = g.GMCbaudrates[:]           # limited to [57600, 115200]
        baudrates.sort(reverse=True)            # to start with highest baudrate

        loop    = 1
        loopmax = 3
        foundit = False
        brec    = None
        while loop < loopmax:                   # try up to loopmax times to get a version from the device at this port
            # cdprint(defname, "testing - loop #{} on port: '{}".format(loop, usbport))
            for baudrate in baudrates:
                dprint(defname, "testing - loop #{} on port: '{}' with baudrate: {}".format(loop, usbport, baudrate))

                try:
                    with serial.Serial(usbport, baudrate=baudrate, timeout=0.3, write_timeout=0.5) as ABRser:
                        # calling getGMC_Version may fail after plugging in of device. Somehow, calling GETCPM first
                        # breaks up this failure. Strange.
                        bwrt = ABRser.write(b'<GETCPM>>')       # returns bwrt: Number of bytes written, type: <class 'int'>
                        while True:
                            time.sleep(0.01)
                            brec = ABRser.read(1)               # returns brec: data record of           type: <class 'bytes'>
                            # rdprint("brec: ", brec)
                            if ABRser.in_waiting == 0: break

                        srec  = getGMC_Version(ABRser)          # get the GMC device version as string. Can be real or simulated
                        # rdprint(defname, "srec:", srec)


                except OSError as e:
                    exceptPrint(e, "")
                    # edprint(defname + "OSError: ERRNO:{} ERRtext:'{}'".format(e.errno, e.strerror))
                    if e.errno == 13:
                        # no permission for port
                        msg  = "You have no permission to access Serial Port '{}'.".format(usbport)
                        msg += "<br>Please review Appendix C of the GeigerLog manual.<br>"
                    else:
                        # ???
                        msg = "Serial Port {} not available".format(usbport)
                    edprint(msg)
                    efprint(msg)

                    return None

                except Exception as e:
                    errmessage1 = defname + "FAILURE: Reading from device"
                    exceptPrint(e, "")

                    edprint(defname, errmessage1)
                    efprint(errmessage1)
                    setIndent(0)
                    return None     # Python's None signals communication error


                if srec.startswith("GMC"):
                    # it is a GMC device
                    foundit = True
                    loop = loopmax # got communication; no need for further calls in case model or serno don't match
                    dprint(defname + "Success - found GMC device '{}' using baudrate {}".format(g.GMC_DeviceDetected, baudrate))

                    # now check for a Model definition
                    # rdprint(defname, g.GMC_ID)

                    if g.GMC_ID[0] is None:
                        # a GMC device was found ok, and a specific Model was not requested. You're done
                        break   # the for loop

                    else:
                        if srec.startswith(g.GMC_ID[0]):
                            # we found the specified Model
                            foundit = True
                            dprint(defname + "Success - matches configured Model '{}' ".format(g.GMC_ID[0]))

                            # now check for a SerialNumber definition if requested
                            if g.GMC_ID[1] is None:
                                break                   # not requested
                            else:
                                serno = getGMC_SerialNumber(usbport, baudrate)
                                if serno.startswith(g.GMC_ID[1]):
                                    # it is the specified SerialNo
                                    foundit = True
                                    dprint(defname + "Success - matches SerialNumber '{}' ".format(g.GMC_ID[1]))
                                    break   # the for loop
                                else:
                                    # not the specified SerialNo
                                    foundit = False

                        else:
                            # not the specified Model
                            rdprint(defname + "FAILURE - does NOT match configured Model '{}' ".format(g.GMC_ID[0]))
                            foundit = False

                    break # the for loop

                else:
                    # not a GMC device found; try next baudrate
                    foundit = False

            # end for loop: for baudrate in baudrates:

            if foundit:
                returnBR = baudrate
                break # the while loop
            else:
                returnBR  = 0
                dprint(defname + "FAILURE No matching device detected at port: {}  baudrate: {}".format(usbport, baudrate))
                rdprint("fail in loop #{} - repeating".format(loop))
                loop     += 1
        # end while loop

        setIndent(0)
        return returnBR


    def getGMC_SerialSetting():
        """test all USB-To-Serial ports and return first found port and baudrate with device
        matching ID and/or Serial number if so requested"""

        defname = "getGMC_SerialSetting: "

        PortsFound = getGMC_SerialPorts("GMC")

        portfound   = None
        baudfound   = None

        for port in PortsFound:
            baudrate = getGMC_SerialBaudrate(port)     # like: port: '/dev/ttyUSB0'
            if baudrate is not None and baudrate > 0:
                portfound = port
                baudfound = baudrate
                break

        return (portfound, baudfound)

    ## end local defs ##################################################################################


    defname = "initGMC: "
    dprint(defname)
    setIndent(1)

    g.GMC_DeviceName = "GMC Device"        # full model name is held in later set g.GMC_DeviceDetected

    # this sets the values defined in the GeigerLog config file
    if g.GMC_usbport            == "auto":  g.GMC_usbport            = None
    if g.GMC_baudrate           == "auto":  g.GMC_baudrate           = None
    if g.GMC_timeoutR           == "auto":  g.GMC_timeoutR           = 3
    if g.GMC_timeoutR_getData   == "auto":  g.GMC_timeoutR_getData   = 0.5    # shorter Timeout-Read used for data collection
    if g.GMC_timeoutW           == "auto":  g.GMC_timeoutW           = 1

    if g.GMC_ID                 == "auto":  g.GMC_ID                 = (None, None)
    if g.GMC_WiFiPeriod         == "auto":  g.GMC_WiFiPeriod         = 1
    if g.GMC_WiFiSwitch         == "auto":  g.GMC_WiFiSwitch         = 1
    if g.GMC_FastEstTime        == "auto":  g.GMC_FastEstTime        = 60
    if g.GMC_RTC_Offset         == "auto":  g.GMC_RTC_Offset         = +1
    if g.GMC_GL_ClockCorrection == "auto":  g.GMC_GL_ClockCorrection = 30


    # this sets the values defined in GeigerLog's own config to cfgHi
    cfgKeyHi["SSID"]      [0] = g.WiFiSSID
    cfgKeyHi["Password"]  [0] = g.WiFiPassword

    cfgKeyHi["Website"]   [0] = g.gmcmapWebsite
    cfgKeyHi["URL"]       [0] = g.gmcmapURL
    cfgKeyHi["UserID"]    [0] = g.gmcmapUserID
    cfgKeyHi["CounterID"] [0] = g.gmcmapCounterID

    cfgKeyHi["Period"]    [0] = g.GMC_WiFiPeriod
    cfgKeyHi["WiFi"]      [0] = g.GMC_WiFiSwitch
    cfgKeyHi["FET"]       [0] = g.GMC_FastEstTime
    cfgKeyHi["RTC_OFFSET"][0] = g.GMC_RTC_Offset

    #
    # get the usbport and find the baudrate
    #
    if  g.GMC_usbport is None:
        # user has NOT defined a port; now auto-find it and its baudrate

        port, baud = getGMC_SerialSetting()

        # rdprint(defname + "port, baud: ", port, baud)
        if port is None or baud is None:
            setIndent(0)
            g.Devices["GMC"][g.CONN]  = False
            msg = "A {} was not detected.".format(g.GMC_DeviceName)
            return msg
        else:
            g.GMC_usbport          = port
            g.GMC_baudrate         = baud
            g.Devices["GMC"][0]    = g.GMC_DeviceDetected                        # detected at getGMC_Version()

            # Example fprint: 'GMC Device 'GMC-300Re 4.54' was detected at port: /dev/ttyUSB0 and baudrate: 57600'
            fprint("{} '{}' was detected at port: {} and baudrate: {}".format(
                                                                                g.GMC_DeviceName,
                                                                                g.GMC_DeviceDetected,
                                                                                g.GMC_usbport,
                                                                                g.GMC_baudrate),
                                                                             )

    else:
        # user has defined a port; use it if it exists, return error if not; don't try anything else

        if not os.path.exists(g.GMC_usbport):
            # edprint("den shit gibbes nich")
            return "The user defined port '{}' does not exist".format(g.GMC_usbport)
        else:
            # use the port configured by the user
            # Example fprint:   A GMC Device was user configured for port: '/dev/ttyUSB0'
            fprint("A device {} was <b>user configured</b> for port: '{}'".format(
                                                                                g.GMC_DeviceName,
                                                                                g.GMC_usbport,))
            baudrate = getGMC_SerialBaudrate(g.GMC_usbport)
            if baudrate is not None and baudrate > 0:
                g.GMC_baudrate = baudrate
                fprint("{} '{}' was detected at port: {} and baudrate: {}".format(
                                                                                g.GMC_DeviceName,
                                                                                g.GMC_DeviceDetected,
                                                                                g.GMC_usbport,
                                                                                g.GMC_baudrate))
            else:
                return "A {} was not detected at user defined port '{}'.".format(
                                                                                g.GMC_DeviceName,
                                                                                g.GMC_usbport)

    # if this point is reached, a serial connection does exist and the counter is connected and ID'd
    g.Devices["GMC"][g.DNAME] = g.GMC_DeviceDetected
    g.Devices["GMC"][g.CONN]  = True

    # PPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPP
    # PPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPP
    # get device details and GMC_variables
    dprint(defname, "Found proper device '{}', now getting Device Properties:".format(g.GMC_DeviceDetected))
    getGMC_DeviceProperties()
    # PPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPP
    # PPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPP


    g.GMC_Variables = setLoggableVariables("GMC", g.GMC_Variables)
    g.exgg.dbtnGMC.setToolTip("GMC Device<br><b>{}</b><br>Click Button for Device Info".format(g.GMC_DeviceDetected))

    # turn Heartbeat --> OFF  ---  just in case it had been turned on!
    turnGMC_HeartbeatOFF()

    # ### turn Heartbeat --> ON --- use only for TESTING heartbeat !
    # turnGMC_HeartbeatON()
    # ### end

    # set Threading
    devvars = g.Devices["GMC"][g.VNAMES]
    for vname in devvars:  g.GMC_Value[vname] = g.NAN   # define all vars

    g.GMC_ThreadRun     = True

    g.GMC_Thread        = threading.Thread(target=GMC_THREAD_Target, args=["Dummy"])     # auch tuple (args=("Dummy",)) möglich, aber NUR einzelnes Argument!
    g.GMC_Thread.daemon = True
    g.GMC_Thread.start()

    # do a clock correction, but only if so configured
    if g.GMC_GL_ClockCorrection > 0:
        GMC_WriteDateTime()
        g.GMC_NextCorrMin = (getMinute() + g.GMC_GL_ClockCorrection) % 60

    # get the config and set it up for GL
    rcfg, error, errmessage = getGMC_RawConfig()
    vprintGMC_Config(defname, rcfg)
    if error >= 0:
        if g.devel:
            # make list of cfg for copy/paste to simulator
            ac = "["
            for i, a in enumerate(rcfg):
                if i % 20 == 0 and i > 0: ac += "\n "
                ac += "{:3d}, ".format(a)
            ac = ac[:-2] + "]"
            cdprint(defname, " Python list for copy/paste of config for use in simulation\n", ac)

        setGMC_Config4GL(rcfg)  # no return val

    setIndent(0)

    return ""   # empty message signals "Ok"; only other useful msg is "SIM" (for simulated, like from Raspi devices)

#end initgmc

    # #
    # # using AT code for 8266 chip in WiFi enabled counters
    # #
    # getResponseAT(b'<AT>>')                 # b'AT\r\r\n\r\nOK\r\n\n'
    # getResponseAT(b'<AT+RST>>')             # b'AT+RST\r\r\n\r\nOK\r\nWIFI DISCONNECT\r\n\r\n ets Jan  8 2013,rst cause:2, boot mode:(3,6)\r\n\r\nload 0x40100000, len 1856, room 16 \r\ntail 0\r\nchksum 0x63\r\nload 0x3ffe8000, len 776, room 8 \r\ntail 0\r\nchksum 0x02\r\nload 0x3ffe8310, len 552, room 8 \r\ntail 0\r\nchksum 0x7'
    # # getResponseAT(b'<AT+GMR>>')           # b'AT+GMR\r\r\nAT version:1.2.0.0(Jul  1 2016 20:04:45)\r\nSDK version:1.5.4.1(39cb9a32)\r\nAi-Thinker Technology Co. Ltd.\r\nDec  2 2016 14:21:16\r\nOK\r\nWIFI DISCONNECT\r\nWIFI CONNECTED\r\nWIFI GOT IP\r\n\n'
    # # getResponseAT(b'<AT+CIFSR>>')         # b'AT+CIFSR\r\r\n+CIFSR:APIP,"192.168.4.1"\r\n+CIFSR:APMAC,"a2:20:a6:36:ac:ba"\r\n+CIFSR:STAIP,"10.0.0.42"\r\n+CIFSR:STAMAC,"a0:20:a6:36:ac:ba"\r\n\r\nOK\r\n\n'
    # #                                       # FritzBox: GMC-500+: A0:20:A6:36:AC:BA == STAMAC!
    # getResponseAT(b'<AT+CIPSTART="TCP","10.0.0.20",8000>>')
    # getResponseAT(b'<AT+CIFSR>>')

    # # getResponseAT(b'<AT+CIPMODE=0>>')
    # # getResponseAT(b'<AT+CIPMODE=1>>')     # 1 führt zur Blockade von CIPSTART

    # # getResponseAT(b'<AT+CWLIF>>')         # b'AT+CWLIF\r\r\n\r\nOK\r\n\n'
    # # getResponseAT(b'<AT+CWSAP?>>')        # b'AT+CWSAP?\r\r\n+CWSAP:"AI-THINKER_36ACBA","",1,0,4,0\r\n\r\nOK\r\nWIFI GOT IP\r\n\n'
    # # getResponseAT(b'<AT+CWMODE?>>')       # b'AT+CWMODE?\r\r\n+CWMODE:3\r\n\r\nOK\r\nWIFI DISCONNECT\r\nWIFI CONNECTED\r\nWIFI GOT IP\r\n\n'
    # # getResponseAT(b'<AT+CWMODE=?>>')      # b'AT+CWMODE=?\r\r\n+CWMODE:(1-3)\r\n\r\nOK\r\nWIFI GOT IP\r\n\n'

    # # getResponseAT(b'<AT+CWLIF="mac">>')   # --> error                         ??? not avialable?
    # # getResponseAT(b'<AT+CMD>>')           # b'AT+CMD?\r\r\n\r\nERROR\r\n\n'   ??? not avialable?
    # # getResponseAT(b'<AT+CMD?>>')          # b'AT+CMD?\r\r\n\r\nERROR\r\n\n'   ??? not avialable?

    # return ""   # empty message signals "Ok"


def terminateGMC():
    """close Serial connection if open, and reset some properties"""

    defname = "terminateGMC: "

    dprint(defname )
    setIndent(1)

    if g.GMCser is not None:
        try:        g.GMCser.close()
        except:     edprint(defname + "Failed trying to close Serial Connection; terminating anyway", debug=True)
        g.GMCser    = None

    # shut down thread
    dprint(defname, "stopping thread")
    g.GMC_ThreadRun = False
    g.GMC_Thread.join()                 # "This blocks the calling thread until the thread
                                        #  whose join() method is called is terminated."

    # verify that thread has ended, but wait not longer than 5 sec (takes 0.006...0.016 ms)
    start = time.time()
    while g.GMC_Thread.is_alive() and (time.time() - start) < 5:
        pass

    msgalive = "Yes" if g.GMC_Thread.is_alive() else "No"
    dprint(defname + "thread-status: alive: {}, waiting took:{:0.1f} ms".format(msgalive, 1000 * (time.time() - start)))

    # set the GMC power icon to inactive state
    g.exgg.dbtnGMCPower.setIcon(QIcon(QPixmap(os.path.join(g.resDir, 'icon_power-round_on.png'))))
    g.exgg.dbtnGMCPower.setEnabled(False)

    g.Devices["GMC"][g.CONN] = False

    dprint(defname + "Terminated")
    dprint(defname, "GMC_ThreadMessages: '{}'".format(g.GMC_ThreadMessages))

    setIndent(0)


def getValuesGMC(varlist):
    """Read data from the locally held vars; set them to NAN after readout"""

    ###
    ### on 'g.GMC_testing' count values are reset to -20 to allow showing of missed data calls
    ###

    start = time.time()

    defname = "getValuesGMC: "
    # mdprint(defname, "varlist: ", varlist)

    ambientvars = ("Temp", "Press", "Humid", "Xtra")
    alldata     = {}
    for vname in varlist:
        if vname in g.GMC_Value.keys():

            # g.GMC_Value has already the scaled data - do not scale again!!
            alldata[vname] = g.GMC_Value[vname]

            # reset g.GMC_Value
            if vname in ambientvars: g.GMC_Value[vname] = g.NAN    # do NOT set the ambient values to the -20 flag for missed calls
            else:                    g.GMC_Value[vname] = -20 if g.GMC_testing else g.NAN

    vprintLoggedValues(defname, varlist, alldata, (time.time() - start) * 1000)

    return alldata


def GMC_THREAD_Target(args):
    """The thread to read the variables from the device"""

    # funny args issue: threading.Thread(target=GMC_THREAD_Target, args=["Dummy"])
    #                   auch tuple (args=("Dummy",)) möglich, aber stets NUR einzelnes Argument!

    defname = "GMC_THREAD_Target: "
    # rdprint(defname, "args: ", args)

    oldnexttime = 0
    varlist     = g.Devices["GMC"][g.VNAMES]

    while g.GMC_ThreadRun:

        # go to sleep until (GMC_timeoutR_getData + 100 ms) before next cycle begins to be ready even when 1 timeout occurs
        # Note: when GMC_timeoutR_getData is >= cycletime then NO sleeping occurs!
        oldnexttime = g.nexttime
        sleeptime   = max(0, g.nexttime - time.time() - g.GMC_timeoutR_getData - 0.1)              # sec
        # rdprint(defname, "sleeptime: ", sleeptime)
        time.sleep(sleeptime)

        # actions when logging
        actionstart = time.time()

        if g.logging:
            # fetch the values
            g.GMC_Value = THREAD_GMC_fetchValues(varlist)           # gives error if doing when not logging

            # # alert on NAN
            # if "CPM1st" in g.GMC_Value.keys():
            #     if np.isnan(g.GMC_Value["CPM1st"]): QueueSoundDVL("burp")

            # clock correction
            if g.GMC_GL_ClockCorrection > 0 and (getMinute() == g.GMC_NextCorrMin):
                GMC_WriteDateTime()
                g.GMC_NextCorrMin = (g.GMC_NextCorrMin + g.GMC_GL_ClockCorrection) % 60
                # rdprint(defname, "g.GMC_NextCorrMin: ", g.GMC_NextCorrMin, "  CurrentMinute: ", getMinute(), "  GMC_GL_ClockCorrection: ", g.GMC_GL_ClockCorrection)

        actiondur   = time.time() - actionstart                     # sec

        # wait until the next cycle has started
        wstart = time.time()
        loops  = 0
        while oldnexttime == g.nexttime:                            # wait until g.nexttime changes
            if g.GMC_ThreadRun == False: break
            time.sleep(0.020)
            loops += 1
        wdur   = time.time() - wstart                               # sec

        # save fSV
        if g.GMC_testing and g.fSVStringSet:
            msg  = "TIMEOUT-FAIL: Device: '{}'  Total calls:{:<6.0f} (CPM:{:0.2%}  CPS:{:0.2%})  ".\
                    format(g.GMC_DeviceDetected, g.GMC_calls, g.GMC_callsTimeoutCPM / g.GMC_calls, g.GMC_callsTimeoutCPS / g.GMC_calls)
            msg += "Varlist: {}  Times[ms]: Sleeping:{:<6.0f} Action:{:<6.0f} Waiting:{:<6.0f} (loops: {})".\
                    format(varlist, sleeptime * 1000, actiondur * 1000, wdur * 1000, loops)
            # writeSpecialLog(msg)
            cdlogprint(msg)


def getClockDelta():
    """Delta of time_computer minus time_device - negative: device is faster"""

    cstart = time.time()

    defname = "getClockDelta: "
    # mdprint(defname)
    setIndent(1)

    clock_delta = g.NAN

    try:
        with serial.Serial(g.GMC_usbport, baudrate=g.GMC_baudrate, timeout=1, write_timeout=0.5) as ABRser:
            bwrt = ABRser.write(b'<GETDATETIME>>')
            brec = ABRser.read(7)
    except Exception as e:
        exceptPrint(e, defname)
    else:   # successful try
        # rdprint(defname, "brec: ", brec)
        # broken clock in GMC-500:  --> brec = b'\x00\x00\x00\x00\x00\x00\xaa'
        if brec == b'\x00\x00\x00\x00\x00\x00\xaa':
            rdprint(defname, "Broken clock - brec: {}".format(brec))
        else:
            if len(brec) >= 6:
                try:
                    datetime_device    = str(dt.datetime(brec[0] + 2000, brec[1], brec[2], brec[3], brec[4], brec[5]))
                    timestamp_device   = mpld.datestr2num(datetime_device)                      # days

                    datetime_computer  = longstime()
                    timestamp_computer = mpld.datestr2num(datetime_computer)                    # days
                    # rdprint(defname, "datetime_computer: ", datetime_computer, "  timestamp_computer: ", timestamp_computer)

                    timestamp_delta    = (timestamp_computer - timestamp_device) * 86400        # --> sec
                    # rdprint(defname, "datetime_device:   ", datetime_device,   "      timestamp_device:   ", timestamp_device, "   Delta: {:0.6f} sec".format(timestamp_delta))

                    rounding           = 3 # count of decimals
                    clock_delta        = round(timestamp_delta, rounding)  # delta time in sec
                except Exception as e:
                    exceptPrint(e, "converting to time, and calc clock delta")
            else:
                rdprint(defname, "brec is too short - brec: ", brec, "  len(brec): ", len(brec), "   ", " ".join(str(x) for x in brec))

    cdur = 1000 * (time.time() - cstart)
    mdprint(defname, "Clock Delta is: {} s   dur: {:0.1f} ms".format(clock_delta, cdur))

    setIndent(0)
    return (clock_delta, cdur)


def GMC_WriteDateTime():
    """Write DateTime to counter"""

    # from GQ-RFC1201.txt:
    # NOT CORRECT !!!!
    # 22. Set year date and time
    # command: <SETDATETIME[YYMMDDHHMMSS]>>
    # Return: 0xAA
    # Firmware supported: GMC-280, GMC-300 Re.3.00 or later

    # from: GQ-GMC-ICD.odt
    # CORRECT! 6 bytes, no square brackets
    # <SETDATETIME[YY][MM][DD][hh][mm][ss]>>

    defname = "GMC_WriteDateTime: "

    # convert Computer DateTime to byte sequence format needed by counter
    timelocal     = list(time.localtime())  # timelocal: 2018-04-19 13:02:50 --> [2018, 4, 19, 13, 2, 50, 3, 109, 1]
    timelocal[0] -= 2000
    btimelocal    = bytes(timelocal[:6])
    # rdprint(defname, "Setting DateTime:  now:", timelocal[:6], ", coded:", btimelocal)

    # write DATETIME Byte-sequence to the counter
    try:
        with serial.Serial(g.GMC_usbport, baudrate=g.GMC_baudrate, timeout=3, write_timeout=0.5) as ABRser:
            bwrt = ABRser.write(b'<SETDATETIME' + btimelocal + b'>>')    # returns bwrt: Number of bytes written, type: <class 'int'>
            brec = ABRser.read(1)                                        # returns brec: b'\xaa'                  type: <class 'bytes'>
            # rdprint(defname, "brec: ", brec)
    except Exception as e:
        msg = "DateTime could NOT be set!"
        exceptPrint(e, defname + msg)
        QueuePrint(msg)
        QueueSoundDVL("burp")
    else:
        gdprint(defname, "DateTime was set!")


def THREAD_GMC_fetchValues(varlist):
    """get all data for vars in varlist for LOCAL storage"""

    totalstart   = time.time()

    defname = "THREAD_GMC_fetchValues: "
    # mdprint(defname, varlist)
    # setIndent(1)
    g.GMC_ThreadMessages = longstime() + " " + defname + str(varlist) + "\n"

    durCPM          = 0
    durCPS          = 0
    THREAD_alldata  = {}
    g.fSVStringSet  = False

    # does the USB-Port exist?
    if not os.path.exists(g.GMC_usbport):
        # den shit gibbes nich  -   kann passieren, wenn nach Start der USB Stecker gezogen wird!
        emsg = "FAILURE: GMC Serial Port '{}' does not exist; cannot access GMC device.".format(g.GMC_usbport)
        QueuePrint(emsg)
        QueueSound("burp")
        mdprint(defname, emsg)

    else:
        # USB-Port does exist
        # try to make a serial connection and get values on success
        GMC_DataSerial = None
        try:
            GMC_DataSerial = serial.Serial(g.GMC_usbport, baudrate=g.GMC_baudrate, timeout=g.GMC_timeoutR_getData, write_timeout=g.GMC_timeoutW)
        except serial.SerialException as e:
            # no serial connection
            exceptPrint(e, "Device can not be found or can not be configured; Port may already be open.")
        except Exception as e:
            # no serial connection
            exceptPrint(e, "Unexpected Exception opening Serial Port")
        else:
            # serial connection had been made ok

            for vname in varlist:
                # THREAD_alldata[vname] = g.NAN
                if vname in ["CPM3rd", "CPS3rd", "Temp", "Press", "Humid", "Xtra"]:
                    # ignore calls for these variables (possibly modified later, see end of function)
                    # pass
                    THREAD_alldata[vname] = g.NAN

                else:
                    # vname in ["CPM", "CPS", CPM1st", "CPS1st", "CPM2nd", "CPS2nd"]
                    fSVstart    = time.time()
                    fSV         = fetchSingleValueGMC(GMC_DataSerial, vname)
                    fSVdur      = 1000 * (time.time() - fSVstart)
                    # rdprint(defname, "fSVdur: {0:0.1f}".format(fSVdur))
                    g.GMC_calls += 1

                    if   "CPM" in vname : durCPM += fSVdur
                    elif "CPS" in vname : durCPS += fSVdur

                    if type(fSV) is str:
                        # mdprint(defname, fSV, type(fSV), str(type(fSV)))
                        g.fSVStringSet = True

                        if   "R_TIMEOUT" in fSV:
                                if   "CPM" in vname:    g.GMC_callsTimeoutCPM += 1
                                elif "CPS" in vname:    g.GMC_callsTimeoutCPS += 1
                                emsg = "TIMEOUT-FAIL: {:6s} Dur:{:3.0f}ms  (Fails: CPM:{:0.3%} CPS:{:0.3%})".format(vname, fSVdur, g.GMC_callsTimeoutCPM / g.GMC_calls, g.GMC_callsTimeoutCPS / g.GMC_calls)

                                QueuePrint("{} {}".format(longstime(), emsg))
                                dprint(defname, emsg)
                                g.SoundMsgQueue.append("doublebip")
                                fSV = -1000 * g.GMC_timeoutR_getData if g.GMC_testing else g.NAN

                        elif "EXTRABYTES" in fSV:
                                # wurde unter Windows einmal beobachtet. Nach einem timeout
                                g.GMC_callsExtrabyte += 1

                                emsg = "EXTRABYTES-FAIL: {:6s}".format(vname)
                                QueuePrint(emsg)
                                cdlogprint(defname + emsg)
                                fSV =  -7000 if g.GMC_testing else g.NAN

                        elif "WRONG_BYTECOUNT" in fSV:
                                g.GMC_callsWrongbyteCount += 1

                                emsg = "BYTECOUNT-FAIL: {:6s} got {} bytes, expected {}!".format(vname, fSV.split(" ")[1], g.GMC_Bytes)
                                QueuePrint(emsg)
                                cdlogprint(defname + emsg)
                                fSV =  -9000 if g.GMC_testing else g.NAN

                        elif "USBPORT_MISSING" in fSV:
                                emsg = "USBPORT_MISSING-FAIL: Serial port '{}' does not exist. Cannot read variable: '{}'".format(g.GMC_usbport, vname)
                                QueuePrint(emsg)
                                cdlogprint(defname + emsg)
                                fSV = -10000 if g.GMC_testing else g.NAN

                        elif "WRONG_VARNAME" in fSV:
                                emsg = "WRONG_VARNAME-FAIL: '{}' cannot be used".format(vname)
                                QueuePrint(emsg)
                                cdlogprint(defname + emsg)
                                fSV = -11000 if g.GMC_testing else g.NAN

                        elif "EXCEPTION" in fSV:
                                emsg = "EXCEPTION: getting value for '{}' on port: {}".format(vname, g.GMC_usbport)
                                QueuePrint(emsg)
                                cdlogprint(defname + emsg)
                                fSV = -12000 if g.GMC_testing else g.NAN

                        else:
                                cdlogprint(defname, "UNCAUGHT fSV string: ", fSV)
                                fSV = -20000 if g.GMC_testing else g.NAN

                    # end if (str message)

                    # fSV can be the original value or the negative error-string-modified-to-value
                    # valuescaling should only be done on original values, i.e. on non-negative values!
                    # fetchSingleValueGMC already retuns the scaled data !!!
                    THREAD_alldata[vname] = fSV if fSV < 0 else applyValueFormula(vname, fSV, g.ValueScale[vname], info=defname)

                    # Info on the Call performance
                    msg  = "{:6s} Value: {:<5.0f}   Calls: Total: {:<5d}  Timeouts: CPM:{:<4d} ({:0.2%})  CPS:{:<4d} ({:0.2%})  Exceptions: {:<4d}  ExtraBytes: {:<4d}  WrongByteCount: {:<4d}"\
                        .format(vname, THREAD_alldata[vname], g.GMC_calls, g.GMC_callsTimeoutCPM, g.GMC_callsTimeoutCPM / g.GMC_calls, g.GMC_callsTimeoutCPS, g.GMC_callsTimeoutCPS / g.GMC_calls, g.GMC_callsException, g.GMC_callsExtrabyte, g.GMC_callsWrongbyteCount)
                    msg += "  Call dur: {:0.1f} ms"\
                        .format(fSVdur)
                    g.GMC_ThreadMessages += longstime() + " " + defname + msg + "\n"

                # end if-else: 'if vname in vars...'
            # end loop: 'for vname in varlist'

            GMC_DataSerial.close()

            if g.devel:
                pass
                if "Temp"  in varlist or "Press" in varlist:
                    T, P = getClockDelta()
                    if "Temp"  in varlist: THREAD_alldata["Temp"]  = T                # counter's clocktime minus real time in sec (negative: --> counter runs faster)
                    if "Press" in varlist: THREAD_alldata["Press"] = P                # duration of getting Clock Delta
                if     "Humid" in varlist: THREAD_alldata["Humid"] = round(durCPM, 3) # sum of durations of only all CPM calls
                if     "Xtra"  in varlist: THREAD_alldata["Xtra"]  = round(durCPS, 3) # sum of durations of only all CPS calls

                # ### testing for response to RadPro commands on the formula interpreter
                # if     "Humid" in varlist: applyValueFormula("Humid", g.NAN, g.ValueScale["Humid"], info=defname)
                # applyValueFormula("Humid", g.NAN, g.ValueScale["Humid"], info=defname)
                # ####


    totaldur = 1000 * (time.time() - totalstart)                              # sum of durations of all actions in this def
    msg      = "Total dur all calls: {:0.1f} ms".format(totaldur)
    g.GMC_ThreadMessages += longstime() + " " + defname + msg + "\n"

    vprintLoggedValues(defname, varlist, THREAD_alldata, totaldur)

    # get GMCinfo during logging if requested
    #    as info requires multiple calls to counter, it can only be done when not
    #    interfering with calls for data. This place here is the ONLY one to assure this!
    if   g.GMC_getInfoFlag == 1: g.GMC_DatetimeMsg = getInfoGMC(extended=False, force=True)
    elif g.GMC_getInfoFlag == 2: g.GMC_DatetimeMsg = getInfoGMC(extended=True,  force=True)
    g.GMC_getInfoFlag = 0

    # setIndent(0)

    return THREAD_alldata


def fetchSingleValueGMC(GMC_DataSerial, vname):
    """Get value for a single, specific var, and return single value after ValueFormula"""

    # NOTE: Do not call with vname in ["CPM3rd", "CPS3rd", "Temp", "Press", "Humid", "Xtra"]
    #       These will result in return of NAN
    # NOTE: Windows CANNOT open serial port when already opened elsewhere!

    # for the 300 series counter:
    # send <GETCPM>> and read 2 bytes
    # In total 2 bytes data are returned from GQ GMC unit as a 16 bit unsigned integer.
    # The first byte is MSB byte data and second byte is LSB byte data.
    #   e.g.: 00 1C  -> the returned CPM is 28
    #   e.g.: 0B EA  -> the returned CPM is 3050
    #
    # send <GETCPS>> and read 2 bytes
    # In total 2 bytes data are returned from GQ GMC unit
    # my observation: highest bit in MSB is always set -> mask out!
    # e.g.: 80 1C  -> the returned CPS is 28
    # e.g.: FF FF  -> the returned CPS is 3F FF -> thus maximum CPS is 16383
    #                                           -> thus maximum CPM is 16383 * 60 = 982980
    #
    # for the 500, 600 series counter:
    # send <GETCPM>> and read 4 bytes -- all GETCPM* commands return 4 bytes! note cmd extension with L or H!
    # send <GETCPS>> and read 4 bytes -- all GETCPS* commands return 4 bytes! note cmd extension with L or H!


    ### local function #######################################################
    def getCommandCode(vname):
        """return tuple: (<GET_CallCode>>, maskHighBit)"""

        CmdCode = (b'', False)  # default when illegal vname used

        # if   vname == "CPM":    CmdCode = (b'<GETCPMXYZabc>>' , False ) # this works also!!!
        # elif vname == "CPS":    CmdCode = (b'<GETCPSxyzabc>>' , True  ) # this works also!!!

        if   vname == "CPM":    CmdCode = (b'<GETCPM>>' , False ) # the normal CPM call; on GMC-500+ gets CPM as sum of both tubes
        elif vname == "CPS":    CmdCode = (b'<GETCPS>>' , True  ) # the normal CPS call; on GMC-500+ gets CPM as sum of both tubes
        elif vname == "CPM1st": CmdCode = (b'<GETCPML>>', False ) # get CPM from High Sensitivity tube; that should be the 'normal' tube
        elif vname == "CPS1st": CmdCode = (b'<GETCPSL>>', True  ) # get CPS from High Sensitivity tube; that should be the 'normal' tube
        elif vname == "CPM2nd": CmdCode = (b'<GETCPMH>>', False ) # get CPM from Low  Sensitivity tube; that should be the 2nd tube in the 500+
        elif vname == "CPS2nd": CmdCode = (b'<GETCPSH>>', True  ) # get CPS from Low  Sensitivity tube; that should be the 2nd tube in the 500+

        return CmdCode


    def cleanExtrabytes():
        """getting extrabytes -  faster routine"""

        brec = b""
        bsum = 0
        while True:
            bytesWaiting = GMC_DataSerial.in_waiting
            if bytesWaiting > 0:
                brec = GMC_DataSerial.read(bytesWaiting)
                for i in range(0, len(brec)):
                    # rdprint("i: ", i, "  brec[i]: ", brec[i])
                    bsum *= 256
                    bsum += brec[i]
                emsg  = "Got bytes waiting before writing for reading {} (={}) from GMC counter: {}".format(brec, bsum, vname)
                rdprint(defname, emsg)
                QueuePrintDVL(emsg)
            else:
                break

        return  (brec, bsum)

    ########################################################################

    defname = "fetchSingleValueGMC: "

    # get CmdCode for the variable 'vname'
    wcommand, maskHighBit = getCommandCode(vname)
    if wcommand == b"":                      return "WRONG_VARNAME"          # can happen only with programming errors

    # does the USB-Port exist?
    if not os.path.exists(g.GMC_usbport):    return "USBPORT_MISSING"        # can happen when plug is pulled aftr init

    # is the Serial Port open?
    if GMC_DataSerial is None: return "GMC Serial Port is not open"

    # get the value for variable vname
    try:
        # getting Extrabytes
        if GMC_DataSerial.in_waiting > 0:
            extra = cleanExtrabytes()
            return "EXTRABYTES " + str(extra)                                # can happen, but when ???

        # getting data bytes
        callstart = time.time()
        bwrt      = GMC_DataSerial.write(wcommand)                           # returns bwrt: Number of bytes written, type: <class 'int'>
        brec      = GMC_DataSerial.read(g.GMC_Bytes)                         # returns brec: data record of           type: <class 'bytes'>
        calldur   = time.time() - callstart                                  # get duration of call in sec
        # rdprint(defname, "{}  brec: {} calldur: {:0.1f} ms ".format(vname, brec, 1000 * calldur))

    except Exception as e:
        g.GMC_callsException += 1
        exceptPrint(e, defname + "getting data for {:6s} from port: {}".format(vname, g.GMC_usbport))
        return "EXCEPTION"                                                   # might happen, but I have not seen it yet

    # check for read timeout
    if calldur >= g.GMC_timeoutR_getData:       return "R_TIMEOUT"           # it is a timeout

    # check for correct number of bytes
    if len(brec) != g.GMC_Bytes:                return "WRONG_BYTECOUNT " + str(len(brec))

    # all ok, got correct no of bytes, either 2 or 4
    if    g.GMC_Bytes == 4:
            value = ((brec[0]<< 8 | brec[1]) << 8 | brec[2]) << 8 | brec[3]

    elif  g.GMC_Bytes == 2:
            value = brec[0] << 8 | brec[1]
            if maskHighBit: value = value & 0x3fff                          # mask out high bits; ONLY for CPS* calls on 300 series counters

    # rdprint(defname, "{}  brec: {} value: {}  calldur: {:0.1f} ms ".format(vname, brec, value, 1000 * calldur))

    # scale values before returning
    # value is single integer number, like 2345 (maybe float after scaling), it is NOT an array
    return applyValueFormula(vname, value, g.ValueScale[vname], info=defname)  # returns single number, int or float


def getGMC_Version(GMCserial):
    """Get GMC hardware model and firmware version"""

    # ATTENTION: new counters may deliver 15 bytes and more for version
    #            e.g. "GMC-500+Re 1.18"         --> 15 bytes
    #                 "GMC-320+V5\x00RRe 5.73"  --> 19 bytes    NOTE: the zero WITHIN the string!
    # see: http://www.gqelectronicsllc.com/forum/topic.asp?TOPIC_ID=4948 Reply #30
    # Quote EmfDev:
    #   "On the 500 and 600 series, the GETVER return can be any length.
    #   So far its only 14 bytes or 15 bytes. But it should return any given
    #   model name completely so the length is variable.
    #   And the '+' sign is included in the model name. e.g. GMC500+Re 1.10
    #   But I don't think the 300 or 320 has been updated so maybe you can ask
    #   support for the fix."
    #
    # Old version:
    #   send <GETVER>> and read 14 bytes
    #   returns string (!) with total of 14 bytes ASCII chars from GQ GMC unit, e.g.: 'GMC-300Re 4.20'
    #   includes 7 bytes hardware model (GMC-300) and 7 bytes firmware version (Re 4.20).
    #

    defname     = "getGMC_Version: "
    errmessage  = "None"

    setIndent(1)

    # write to serial
    try:
        GMCserial.write(b'<GETVER>>')
    except Exception as e:
        errmessage = defname + "FAILURE writing to GMCserial"
        exceptPrint(e, errmessage)
        setIndent(0)
        return errmessage

    # read from serial
    try:
        brec = GMCserial.read(14)   # may leave bytes in the pipeline
        while True:
            cnt = GMCserial.in_waiting
            if cnt == 0: break
            brec += GMCserial.read(cnt)
            time.sleep(0.05)
    except Exception as e:
        errmessage = defname + "FAILURE reading from GMCserial"
        exceptPrint(e, errmessage)
        setIndent(0)
        return errmessage

    ##### 'NULL' CHARACTER PROBLEM ###################################################
    # latest GMC-320+V5 has NULL char in name:
    # from Tom Johnson's new GMC-320:     b'GMC-320+V5\x00RRe 5.73'
    brec = brec.replace(b"\x00", b"?")
    ##### End 'NULL' CHARACTER PROBLEM ###############################################

    # convert to string
    try:
        GMCversion = brec.decode("UTF-8")
    except Exception as e:
        errmessage = defname  + "ERROR getting Version - Bytes are not ASCII: " + str(brec)
        exceptPrint(e, errmessage)
        setIndent(0)
        return errmessage + "brec: " + str(brec)

    # rdprint(defname, "brec: '{}'".format(brec))

    if len(brec) == 0: dprint(defname + "FAILURE: No data returned")
    else:              dprint(defname + "len: {} bytes, rec: {}, GMCversion: '{}', errmessage: '{}'".format(len(brec), brec, GMCversion, errmessage))

    setIndent(0)

    g.GMC_DeviceDetected = GMCversion

    return GMCversion


def cleanupGMC(ctype = "Dummy"):    # ctype should be "before" and "after" logging
    """clearing the pipeline"""

    defname = "cleanupGMC: "

    if g.Devices["GMC"][g.CONN] :
        dprint(defname, "'{}': Cleaning Pipeline '{}'".format(g.GMC_DeviceDetected, ctype))
        getGMC_ExtraByte()

        dprint(defname, "'{}': Cleaning Thread Values '{}'".format(g.GMC_DeviceDetected, ctype))
        for vname in g.VarsCopy:
            g.GMC_Value[vname] = g.NAN


def turnGMC_HeartbeatON():
    # 3. Turn on the GQ GMC heartbeat
    # Note:     This command enable the GQ GMC unit to send count per second data to host every second automatically.
    # Command:  <HEARTBEAT1>>
    # Return:   A 16 bit unsigned integer is returned every second automatically. Each data package consist of 2 bytes
    #           data from GQ GMC unit. The first byte is MSB byte data and second byte is LSB byte data.
    # e.g.:     10 1C     the returned 1 second count is 28.   Only lowest 14 bits are used for the valid data bit.
    #           The highest bit 15 and bit 14 are reserved data bits.
    # Firmware supported:  GMC-280, GMC-300  Re.2.10 or later

    # ???       What CPS do you get? That one for the first tube? How to get one for the second tube?

    defname = "turnGMC_HeartbeatON: "
    # dprint(defname)

    brec, error, errmessage = serialGMC_COMM(b'<HEARTBEAT1>>', 0, orig(__file__))
    if error == 0:  dprint (defname, "Success")
    else:           edprint(defname, "FAILURE: " + errmessage)

    return (brec, error, errmessage)


def turnGMC_HeartbeatOFF():
    # 4. Turn off the GQ GMC heartbeat
    # Command:  <HEARTBEAT0>>
    # Return:   None
    # Firmware supported:  Re.2.10 or later

    defname = "turnGMC_HeartbeatOFF: "
    # dprint(defname)

    brec, error, errmessage = serialGMC_COMM(b'<HEARTBEAT0>>', 0, orig(__file__))
    if error == 0:  dprint (defname, "Success")
    else:           edprint(defname, "FAILURE: " + errmessage)

    return (brec, error, errmessage)


def getGMC_VOLT():
    # Get battery voltage status
    #
    # 1 Byte returns; like: GMC-300E+
    # send <GETVOLT>> and read 1 byte
    # returns one byte voltage value of battery (X 10V)
    # e.g.: return 62(hex) is 9.8V
    # Example: Geiger counter GMC-300E+
    # with Li-Battery 3.7V, 800mAh (2.96Wh)
    # -> getGMC_VOLT reading is: 4.2V
    # -> Digital Volt Meter reading is: 4.18V
    #
    # 5 Byte returns; like: GMC 500/600
    # send <GETVOLT>> and read 5 bytes (as ASCII)
    # z.B.[52, 46, 49, 118, 0] = "4.1v\x00"

    defname = "getGMC_VOLT: "
    dprint(defname)
    setIndent(1)

    if g.GMC_voltagebytes is None:
        (rec, error, errmessage) = "Voltage not supported", -1, "Unsupported on this device"
        dprint(defname, "(rec, error, errmessage): ", (rec, error, errmessage))
        setIndent(0)
        return (rec, error, errmessage)

    rec, error, errmessage = serialGMC_COMM(b'<GETVOLT>>', g.GMC_voltagebytes, orig(__file__))
    try:
        dprint(defname, "VOLT: rec: {} (len:{})  as Dec:{}".format(rec, len(rec), BytesAsDec(rec)))
    except Exception as e:
        exceptPrint(e, "Voltage format is not matching expectations!")
        error = 99

    ### For TESTING uncomment all 4 #######################################
    # ATTENTION: Voltage in Firmware 2.42 does NOT have the Null character!
    #######################################################################
    #rec         = b'3.76v\x00'              # 3.76 Volt
    #error       = 1
    #errmessage  = "testing"
    #dprint(defname + "TESTING with rec=", rec, debug=True)
    ################################################

    if error == 0 or error == 1:
        if   g.GMC_voltagebytes == 1:
            rec = str(rec[0]/10.0)

        elif g.GMC_voltagebytes == 5:
            reccopy = rec[:]
            reccopy = reccopy.replace(b"\x00", b"").replace(b"v", b"")  # it ends with \x00:  b'4.6v\x00'
            rec     = reccopy.decode('UTF-8')

        else:
            rec = str(rec) + " Unexpected voltage format @config: GMC_voltagebytes={}".format(g.GMC_voltagebytes)

    else:
        rec         = "ERROR: Voltage has unexpected format!"
        error       = 1
        errmessage  = defname + "ERROR getting voltage"

    dprint(defname, "Using config setting GMC_voltagebytes={}:  Voltage='{}', err={}, errmessage='{}'".format(g.GMC_voltagebytes, rec, error, errmessage))
    setIndent(0)

    return (rec, error, errmessage)


def getGMC_SPIR(address = 0, datalength = 4096):
    """Reads datalength bytes from the internal flash memory at address to get history data"""

    # Request history data from internal flash memory
    # Command:  <SPIR[A2][A1][A0][L1][L0]>>
    # A2,A1,A0 are three bytes address data, from MSB to LSB.
    # The L1,L0 are the data length requested.
    # L1 is high byte of 16 bit integer and L0 is low byte.
    # The length normally not exceed 4096 bytes in each request.
    # Return: The history data in raw byte array.
    # Comment: The minimum address is 0, and maximum address value is
    # the size of the flash memory of the GQ GMC Geiger count. Check the
    # user manual for particular model flash size.

    # address must not exceed 2^(3*8) = 16 777 215 because high byte
    # is clipped off and only lower 3 bytes are used here
    # (but device address is limited to 2^20 - 1 = 1 048 575 = "1M"
    # anyway, or even only 2^16 - 1 = 65 535 = "64K" !)

    # datalength must not exceed 2^16 = 65536 or python conversion
    # fails with error; should be less than 4096 anyway

    # device delivers [(datalength modulo 4096) + 1] bytes,
    # e.g. with datalength = 4128 (= 4096 + 32 = 0x0fff + 0x0020)
    # it returns: (4128 modulo 4096) + 1 = 32 + 1 = 33 bytes

    # This contains a WORKAROUND activated with  'GMC_SPIRbugfix=True':
    # it asks for only (datalength - 1) bytes,
    # but as it then reads one more byte, the original datalength is obtained

    # BUG WARNING - WORKAROUND ##################################################
    #
    # GMC-300   : no workaround, but use 2k GMC_SPIRpage only!
    # GMC-300E+ : use workaround 'datalength - 1' with 4k GMC_SPIRpage
    # GMC-320   : same as GMC-300E+
    # GMC-320+  : same as GMC-300E+
    # GMC-500   : ist der Bug behoben oder nur auf altem Stand von GMC-300 zurück?
    #             workaround ist nur 2k GMC_SPIRpage anzufordern
    # GMC-500+  : treated as a GM-500
    # GMC-600   : treated as a GM-500
    # GMC-600+  : treated as a GM-500
    # End BUG WARNING - WORKAROUND ##############################################

    defname = "getGMC_SPIR: "
    # dprint(defname)

    # address: pack into 4 bytes, big endian; then clip 1st byte = high byte!
    ad = struct.pack(">I", address)[1:]

    # datalength: pack into 2 bytes, big endian; use all bytes but adjust datalength when fixing bug!
    if g.GMC_SPIRbugfix:   dl = struct.pack(">H", datalength - 1)
    else:                  dl = struct.pack(">H", datalength    )

    rec, error, errmessage = serialGMC_COMM(b'<SPIR' + ad + dl + b'>>', datalength, orig(__file__)) # returns bytes
    if rec is not None :    rmsg = "datalength:{:5d}".format(len(rec))
    else:                   rmsg = "ERROR: No data received!"

    msg  = "requested: datalength:{:5d} (0x{:02x}{:02x})  address: {:5d} (0x{:02x}{:02x}{:02x})   ".\
                format(datalength,          dl[0], dl[1], address,           ad[0], ad[1], ad[2])
    msg += "received: {}  err={}  errmessage='{}'".format(rmsg, error, errmessage)
    dprint(defname, msg)

    return (rec, error, errmessage)


# not in use! # not good! keep as reminder --- Use GMC_EraseMemBySPISE instead!
def GMC_EraseMemByFacRESET():
    """Erase the History Data saved to memory Factory Reset and re-updatin CFG"""

    # not good; see Reply #12 of: http://www.gqelectronicsllc.com/forum/topic.asp?TOPIC_ID=9812
    # quote:For now maybe you can try to get cfg, then factory reset, then write to cfg which will be faster.
    # @EmfDev, that sounded like a great idea, but at the end it was even a lot worse that the SPISE thing,
    # both in speed and reliability. Writing the config to the counter is a rather slow process, since -
    # according to your documents - it needs to be done byte-by-byte. Writing a single byte to the config
    # of a GMC500 takes 14 ms (21 ms for a GMC300). So, 512 bytes need 512 * 0.014 = 7.2 sec. Plus overhead
    # makes it ~9 sec, just as much as the SPISE process takes.
    # But on top of this the config-writing is notoriously unreliable, often requiring 1, 2, or even 3
    # re-writes, before a read-back confirms the correct configuration finally made it to the counter.
    # And more, on top of this the ECFG command also has a tendency to timeout. Again, most of the time
    # requiring multiple repeats.
    # Overall this Factory Reset based approach may easily result in 20 to 30 sec before it is finished!
    # The SPISE approach is anything but a speed champion, but at least is a lot more reliable to handle.
    # Hopefully the firmware can be improved on this.

    start = time.time()

    defname = "GMC_EraseMemByFacRESET: "
    dprint(defname)
    setIndent(1)

    # cleaning pipeline
    getGMC_ExtraByte()

    cfg, error, errmessage = getGMC_RawConfig()
    mdprint(defname + "getGMC_RawConfig: rcvd: cfg={}, err={}, errmessage='{}'".format(cfg[:25], error, errmessage))

    # msg = defname
    vprintGMC_Config("cfg BEFORE Factory Reset: ", cfg)

    # cleaning pipeline
    getGMC_ExtraByte()

    # execute the Factory Reset
    setGMC_FACTORYRESET()

    resetcfg, error, errmessage = getGMC_RawConfig()
    mdprint(defname + "getGMC_RawConfig: rcvd: cfg={}, err={}, errmessage='{}'".format(cfg[:25], error, errmessage))

    vprintGMC_Config("cfg AFTER Factory Reset: ", resetcfg)

    # write the new config data
    writeGMC_ConfigFull(cfg)

    # verification of written data
    # PROBLEM:  the counter may overwrite some data (like date/time, MaxCPM) with new values, before verification is done!
    # print message but don't stop the programm
    rawcfg, error, errmessage = getGMC_RawConfig()                      # read the raw config ...
    if verifyCFGwriting(cfg, resetcfg):  gdprint("compare is good")   # ... and compare with intended config
    else:                                rdprint("compare is bad")    # ... but ignore if comparison is bad

    # cleaning pipeline
    getGMC_ExtraByte()

    rec, error, errmessage = serialGMC_COMM(b'<GetSPISA>>', 4, orig(__file__))
    dprint(defname + "GetSPISA: rcvd: rec={}, err={}, errmessage='{}'".format(rec, error, errmessage))

    # cleaning pipeline
    getGMC_ExtraByte()

    setIndent(0)

    return (rec, error, errmessage)


def GMC_EraseMemBySPISE():
    """Erase the History Data saved to memory"""

    # from http://www.gqelectronicsllc.com/forum/topic.asp?TOPIC_ID=9812
    # 1. SPISE[0xAA][0xAA][0xAA] this is a sector erase. each sector is 4KB.
    # e.g. 53 50 49 53 45 00 00 00 -> erase first sector
    # then
    # 2. Need to set the SPI Save Address back to 0x000000. No need if device is off.
    # SetSPISA[0xAA][0xAA][0xAA] -> SPI save address.
    # If you want to erase the full storage must erase all the sectors.
    # Maybe it is better to do it when device is off so that timestamp will be saved during power on.
    # Go to Top of Page
    # 3C 53 65 74 53 50 49 53 41 00 00 00 3E 3E
    # <  S  e  t  S  P  I  S  A  (3x Null)>  >
    #
    # Conclusion:
    # the above comments by EmDev are partially wrong!
    # It only works on GMC-300E+ and GMC-500+ if you do:
    #   1) Power OFF
    #   2) Delete all content with SPISE command
    #   3) send SetSPISA
    #   4) Power ON

    start = time.time()
    defname = "GMC_EraseMemBySPISE: "
    dprint(defname)
    setIndent(1)

    # cleaning pipeline
    getGMC_ExtraByte()

    # delete all memory in chunks of 4096
    page = 4096
    for address in range(0, g.GMC_memory, page):

        # address: pack into 4 bytes, big endian;
        # then clip 1st byte = high byte, so only 3 LSB bytes are left!
        # result like: address: Dec: 49152 --> HEX: 00 c0 00
        ad = struct.pack(">I", address)[1:]

        # return bytes differ by counter:
        # GMC-500+:     read time: 33 ... 36 ms; some calls >100 ms (approx every 50th)
        #               returns:  b'\xaa'   (1 byte only)
        # GMC-300E+:    read time: 33 ... 40 ms; some calls 80 ms, 230 ms
        #               returns:   b'\x00\x80\x00' (3 bytes; is same as address given)
        rec, error, errmessage = serialGMC_COMM(b'<SPISE' + ad + b'>>', 1, orig(__file__))
        msg = defname + "SPISE: address: {:5d} (0x {:02x} {:02x} {:02x})  ".format(address, ad[0], ad[1], ad[2])
        cdprint(msg + "rcvd: rec={}, err={}, errmessage='{}'".format(rec, error, errmessage))

    rec, error, errmessage = serialGMC_COMM(b'<GetSPISA>>', 4, orig(__file__))

    msg = defname + "GetSPISA "
    cdprint(msg + "rcvd: rec={}, err={}, errmessage='{}'".format(rec, error, errmessage))

    # send SetSPISA[0xAA][0xAA][0xAA]
    SPISaveAddress = b'\x00\x00\x00'
    rec, error, errmessage = serialGMC_COMM(b'<SetSPISA' + SPISaveAddress + b'>>', 0, orig(__file__)) # returns bytes
    cdprint(defname + "SetSPISA\x00\x00\x00: rcvd: rec={}, err={}, errmessage='{}'".format(rec, error, errmessage))

    cdprint(defname + "Duration: {:0.1f} sec".format(time.time() - start))

    rec, error, errmessage = serialGMC_COMM(b'<GetSPISA>>', 4, orig(__file__))
    msg = defname + "GetSPISA "
    dprint(msg + "rcvd: rec={}, err={}, errmessage='{}'".format(rec, error, errmessage))

    setIndent(0)

    return (rec, error, errmessage)


def getGMC_ExtraByte(SerHandle = None):
    """Clearing the serial pipeline by reading all bytes from it"""

    defname = "getGMC_ExtraByte: "

    setIndent(1)

    if SerHandle is None:
        # no SerHandle given as parameter; make new one
        if os.path.exists(g.GMC_usbport):
            try:
                with serial.Serial( g.GMC_usbport,
                                    g.GMC_baudrate,
                                    timeout=g.GMC_timeoutR_getData,                     # 0.5 sec ( a shorter value than default)
                                    write_timeout=g.GMC_timeoutW)       as GMCserEB:
                    xrec = origgetGMC_ExtraByte(GMCserEB)

            except Exception as e:
                exceptPrint(e, defname + "Failure trying to establish serial connection")
                xrec = b""
        else:
            msg = "USBport '{}' does not exist".format(g.GMC_usbport)
            rdprint(defname, msg)
            xrec = b""

    else:
        # a SerHandle was given as parameter, use it
        xrec = origgetGMC_ExtraByte(SerHandle)

    setIndent(0)

    return xrec


def origgetGMC_ExtraByte(SerHandleEB):
    """read until no further bytes coming"""

    start   = time.time()
    defname = "origgetGMC_ExtraByte: "
    xrec    = b""

    time.sleep(0.005) # this code may be running too fast and missing waiting bytes. Happened with 500+

    if os.path.exists(g.GMC_usbport):
        try:
            # failed when called from 2nd instance of GeigerLog; just to avoid crash
            bytesWaiting = SerHandleEB.in_waiting
            # rdprint(defname, "bytes waiting; ", bytesWaiting)
        except Exception as e:
            exceptPrint(e, "Exception bytesWaiting")
            bytesWaiting = 0
    else:
        # edprint("den shit gibbes nich")
        bytesWaiting = 0

    if bytesWaiting > 0:
        # read until nothing is in_waiting
        # mdprint(defname + "Bytes waiting: {}".format(bytesWaiting))
        while True:
            try:
                x = SerHandleEB.read(bytesWaiting)
                # edprint("x: len:", len(x), " ", x)
                time.sleep(0.010)   # this loop may be running too fast and missing waiting bytes.
                                    # Happened with 500+
            except Exception as e:
                edprint(defname + "Exception: {}".format(e))
                exceptPrint(e, defname + "Exception: ")
                x = b""

            if len(x) == 0: break
            xrec += x

            try:
                bytesWaiting = SerHandleEB.in_waiting
            except Exception as e:
                exceptPrint(e, defname + "SerHandleEB.in_waiting Exception")
                bytesWaiting = 0

            if bytesWaiting == 0: break

        msg = BOLDRED + "Got {} extra bytes from reading-pipeline: {}".format(len(xrec), xrec[:70])

        duration = 1000 * (time.time() - start)
        cdprint(defname + msg + " - duration:{:0.1f} ms".format(duration))

    return xrec


def getGMC_RawConfig():
    """
    - get the config from the counter
    - return cfg, error, errmessage
    """

    # NOTE: 300 series uses 256 bytes; 500, 600, 800 series 512 bytes
    #       config size is registered in deviceproperties

    # call to get cfg:
    # send <GETCFG>> and read all bytes
    # returns
    # - the cfg as Python bytes, should be 256 or 512 bytes long
    # - the error value (0, -1, +1)
    # - the error message as string
    # - it does NOT set the global cfg g.GMC_cfg !!!

    defname = "getGMC_RawConfig: "
    dprint(defname)
    setIndent(1)

    # get the config from the counter
    try:
        startGETCFG = time.time()
        cfg, error, errmessage = serialGMC_COMM(b'<GETCFG>>', g.GMC_configsize, orig(__file__))
        durGETCFG   = 1000 * (time.time() - startGETCFG)
    except Exception as e:
        exceptPrint(e, defname)
        return (b"", -1, "EXCEPTION reading config from counter")

    if len(cfg) == g.GMC_configsize:
        # it has the right size
        dprint (defname + "Got config as {} bytes in {:5.1f} ms; first 20 B as hex: {}".format(len(cfg), durGETCFG, BytesAsHex(cfg[:20])))
    else:
        # the size is wrong - either empty or not expected config size
        edprint (defname + "FAILURE getting config - wrong byte count={} received in {:0.1f} ms".format(len(cfg), durGETCFG))
        QueuePrint("ERROR: Could not load proper configuration from GMC counter. Please, retry.")

    setIndent(0)

    return cfg, error, errmessage


def setGMC_Config4GL(cfg):
    """
    Take configuration data and parse into dict
    parameter: cfg:  config data as read from device (real or simulated)
    return:    None
    """

    # local defs ########################################
    def convBytesToVals(cbytes):
        cval = ""
        cval = " ".join("%02X" % e for e in cbytes)
        # tbytes      = "5 Bytes hex:" + " ".join("%02X" % e for e in hisbytes[index + 1: index + 6]) + " "
        return cval


    def getType(val):
        t = str(type(val))
        return t[8:-2]

    # end local defs ####################################


    start1 = time.time()

    defname = "setGMC_Config4GL: "
    dprint(defname)
    setIndent(1)

    cfgheader = "   {:20s} {:5s} : {:33s}{:8s} {}".format("key", "Index", "Value", "Type", "Bytes")

    # set low keys
    mdprint(defname, "cfgKeyLo")
    mdprint(cfgheader)

    # set endian
    if g.GMC_endianness == "big": fcode = ">f"         # use big-endian ---   500er, 600er, 800er:
    else:                         fcode = "<f"         # use little-endian -- 3XX and 3XXS series

    try:
        for key in cfgKeyLo:
            index        = cfgKeyLo[key][1][0]
            width        = cfgKeyLo[key][1][1]
            cfgkeyBinVal = cfg [index : index + width]        # cut bytes out from config

            if   key == "CalibCPM_0"   : cfgKeyLo[key][0] = struct.unpack(">H",    cfgkeyBinVal)[0]
            elif key == "CalibCPM_1"   : cfgKeyLo[key][0] = struct.unpack(">H",    cfgkeyBinVal)[0]
            elif key == "CalibCPM_2"   : cfgKeyLo[key][0] = struct.unpack(">H",    cfgkeyBinVal)[0]
            elif key == "CalibuSv_0"   : cfgKeyLo[key][0] = struct.unpack(fcode,   cfgkeyBinVal)[0]
            elif key == "CalibuSv_1"   : cfgKeyLo[key][0] = struct.unpack(fcode,   cfgkeyBinVal)[0]
            elif key == "CalibuSv_2"   : cfgKeyLo[key][0] = struct.unpack(fcode,   cfgkeyBinVal)[0]
            elif key == "AlarmCPMValue": cfgKeyLo[key][0] = struct.unpack(">H",    cfgkeyBinVal)[0]
            elif key == "AlarmValueuSv": cfgKeyLo[key][0] = struct.unpack(fcode,   cfgkeyBinVal)[0]
            elif key == "MaxCPM"       : cfgKeyLo[key][0] = struct.unpack(">H",    cfgkeyBinVal)[0]
            elif key == "ThresholdCPM" : cfgKeyLo[key][0] = struct.unpack(">H",    cfgkeyBinVal)[0]
            elif key == "ThresholduSv" : cfgKeyLo[key][0] = struct.unpack(fcode,   cfgkeyBinVal)[0]
            else:                        cfgKeyLo[key][0] = struct.unpack(">B",    cfgkeyBinVal)[0] # all other keys are single byte values

            mdprint("   {:20s} {:5d} : {:<33.10g}{:8s} {}".format(key, int(cfgKeyLo[key][1][0]), cfgKeyLo[key][0], getType(cfgKeyLo[key][0]), convBytesToVals(cfgkeyBinVal)))

    except Exception as e:
        exceptPrint(e, defname + "key: {}".format(key))

    # set High keys
    try:
        # set pointer cfgHiIndex
        cfgHiIndex = int(g.GMC_CfgHiIndex)

        # set endian
        if g.GMC_endianness == "big": fcode = ">f"       # use big-endian ---   500er, 600er:
        else:                         fcode = "<f"       # use little-endian -- other than 500er and 600er:

        mdprint(defname, "cfgKeyHi CfgHiIndex: {}  Endianness: {}".format(cfgHiIndex, g.GMC_endianness))
        mdprint(cfgheader)

        for key in cfgKeyHi:
            xfrom        = int(cfgKeyHi[key][cfgHiIndex][0])
            width        = int(cfgKeyHi[key][cfgHiIndex][1])
            cfgkeyBinVal = cfg[xfrom : xfrom + width]

            if width == 0:
                # print("width==0")
                pass

            # single byte
            elif key == "Period":           cfgKeyHi[key][1] = struct.unpack(">B", cfgkeyBinVal)[0] # Period is one byte, value = 0...255 (minutes)
            elif key == "WiFi":             cfgKeyHi[key][1] = struct.unpack(">B", cfgkeyBinVal)[0] # WiFi is one byte
            elif key == "FET":              cfgKeyHi[key][1] = struct.unpack(">B", cfgkeyBinVal)[0] # FastEstTime is one byte, value = 3(dynamic), 5,10,15,20,30,60 seconds
            elif key == "RTC_OFFSET":       cfgKeyHi[key][1] = struct.unpack(">B", cfgkeyBinVal)[0] # RTC_OFFSET is one byte, value = -59 ... + 59 (sec)
            elif key == "DEADTIME_ENABLE":  cfgKeyHi[key][1] = struct.unpack(">B", cfgkeyBinVal)[0] # DEADTIME_ENABLE is one byte, value = 1 (ON), or 0 (OFF)
            elif key == "HV_CALIB":         cfgKeyHi[key][1] = struct.unpack(">B", cfgkeyBinVal)[0] # HV_CALIB is one byte, value = 0 ... 255

            # double byte
            elif key == "TARGET_HV":        cfgKeyHi[key][1] = struct.unpack(">H", cfgkeyBinVal)[0] # double byte value; should be 300 ... 600 V
            elif key == "DEADTIME_TUBE1":   cfgKeyHi[key][1] = struct.unpack(">H", cfgkeyBinVal)[0] # double byte value; should be 0 ... ? µs
            elif key == "DEADTIME_TUBE2":   cfgKeyHi[key][1] = struct.unpack(">H", cfgkeyBinVal)[0] # double byte value; should be 0 ... ? µs

#eee
            # quad bytes
            elif key == "Cal6CPM_0":        cfgKeyHi[key][1] = struct.unpack(">I",  cfgkeyBinVal)[0]
            elif key == "Cal6CPM_1":        cfgKeyHi[key][1] = struct.unpack(">I",  cfgkeyBinVal)[0]
            elif key == "Cal6CPM_2":        cfgKeyHi[key][1] = struct.unpack(">I",  cfgkeyBinVal)[0]
            elif key == "Cal6CPM_3":        cfgKeyHi[key][1] = struct.unpack(">I",  cfgkeyBinVal)[0]
            elif key == "Cal6CPM_4":        cfgKeyHi[key][1] = struct.unpack(">I",  cfgkeyBinVal)[0]
            elif key == "Cal6CPM_5":        cfgKeyHi[key][1] = struct.unpack(">I",  cfgkeyBinVal)[0]
            elif key == "Cal6uSv_0":        cfgKeyHi[key][1] = struct.unpack(fcode, cfgkeyBinVal)[0]
            elif key == "Cal6uSv_1":        cfgKeyHi[key][1] = struct.unpack(fcode, cfgkeyBinVal)[0]
            elif key == "Cal6uSv_2":        cfgKeyHi[key][1] = struct.unpack(fcode, cfgkeyBinVal)[0]
            elif key == "Cal6uSv_3":        cfgKeyHi[key][1] = struct.unpack(fcode, cfgkeyBinVal)[0]
            elif key == "Cal6uSv_4":        cfgKeyHi[key][1] = struct.unpack(fcode, cfgkeyBinVal)[0]
            elif key == "Cal6uSv_5":        cfgKeyHi[key][1] = struct.unpack(fcode, cfgkeyBinVal)[0]

            # six bytes
            elif key == "DATETIME":         cfgKeyHi[key][1] = " ".join(str(a) for a in cfgkeyBinVal) # 6 bytes fore Datetime

            # other
            else:
                # multi-byte values
                # keys: 'SSID, Password, Website, URL, UserID, CounterID',  32 or 64 byte wide byte sequences
                keyval = cfgkeyBinVal.replace(b"\x00", b"").replace(b"\xFF", b"?").decode("ASCII")          # convert bytes to string
                cfgKeyHi[key][1] = keyval

            mdprint("   {:20s} {:5d} : {:33s}{:8s} {}".format(key, int(cfgKeyHi[key][cfgHiIndex][0]), str(cfgKeyHi[key][1]), getType(cfgKeyHi[key][1]), convBytesToVals(cfgkeyBinVal)))

    except Exception as e:
        exceptPrint(e, "key: '{}'  setting the High part of config".format(key))

    DurWith  = 1000 * (time.time() - start1)
    dprint(defname, "Duration: {:0.0f} ms".format(DurWith))

    setIndent(0)


def writeGMC_ConfigFull(config):
    """write a full config"""

    # 9. Write configuration data
    # Command:  <WCFG[A0][D0]>>
    # A0 is the address and the D0 is the data byte(hex).
    # A0 is offset of byte in configuration data.
    # D0 is the assigned value of the byte.
    # Return: 0xAA
    # Firmware supported: GMC-280, GMC-300 Re.2.10 or later

    """
    from: http://www.gqelectronicsllc.com/forum/topic.asp?TOPIC_ID=4948 Reply #20
    EmfDev:
    The <ECFG>> and <CFGUPDATE>> still work.

    But the <WCFG[A0][D0]>> is now <WCFG[Hi][Lo][Ch]>>
    So instead of 2, there are 3 params.
    Hi - High byte
    Lo - Low byte
    Ch - Byte to write

    3c 57 43 46 47 00 02 01 3e 3e example for writing 1 to the speaker.
    I think you already know that you can't change a byte from 0x00 to 0x01 but
    you can change it from 0x01 to 0x00

    So one way users can change config is to:
    1. <GETCFG>> copy each byte of the config
    2. <ECFG>> erase config from the device
    3. Edit the config you got from 1 like you can change speaker from 1 to 0 or 0 to 1
    4. <WCFG[0x00 - 0x01][0x00 - 0xFF][valid 8bits]>> starting from position 0 to the end of config
    5. <CFGUPDATE>>
    """

    start = time.time()

    defname = "writeGMC_ConfigFull: "

    dprint(defname)
    setIndent(1)

    cfgcopy = copy.copy(config)

    if   len(cfgcopy) <= 256 and g.GMC_configsize == 256:  doUpdate = 256
    elif len(cfgcopy) <= 512 and g.GMC_configsize == 512:  doUpdate = 512
    else: # ERROR:
        msg = "Number of configuration data inconsistent with detected device.\nUpdating config will NOT be done, as Device might be damaged by it!"
        efprint(msg)
        dprint(defname + msg.replace('\n', ' '), debug=True)
        setIndent(0)
        return

    # remove right side FFs; after erasing the config memory this will be the default anyway
    cfgstrip = cfgcopy.rstrip(b'\xFF')
    # dprint(defname + "Config right-stripped from FF: len:{}:\n".format(len(cfgstrip)), BytesAsHex(cfgstrip))

    # erase config on device
    # GMC-300E+: ECFG: Duration: 0.204 sec (??), 0.045 sec, 0.044 sec, 0.041 sec
    # GMC-500+:  ECFG: Duration: 0.155 sec    dprint(defname + "Erase Config with ECFG")
    startecfg = time.time()
    rec, error, errmessage = serialGMC_COMM(b'<ECFG>>', 1, orig(__file__))
    cdprint(defname + "rec: {}  ECFG: Duration: {:0.3f} ms".format(rec, 1000 * (time.time() - startecfg)))

    # write the (modified) config to device
    dprint(defname + "Write new Config Data for Config Size: >>>>>>>>>>>>>>>> {} <<<<<<<<<<<<".format(doUpdate))
    #### GMC Bug #######################################################
    # GMC-500 always times out at byte #11.
    # solved: it is a bug in the firmware; data resulted in ">>>"
    ####################################################################
    ##### Writing #####################################################################
    # GMC-500:  single byte write :    0.014 sec
    #           All 512 bytes :        up to addr: 0x10f (=271), Full Duration: 1.6 sec
    # GMC-300:  single byte write :    about 10 ms
    #           All 256 bytes :        up to addr: 0x043 (=67)   Full Duration: 1.0 sec
    ###################################################################################
    startAllups = time.time()
    pfs = "addr:{:>3d} (0x{:03X})   cfgval:{:>3d} (0x{:02X})"
    with serial.Serial(g.GMC_usbport, g.GMC_baudrate, timeout=0.3) as GMCserData:
        for i, cfgval in enumerate(cfgstrip):
            startsingle = time.time()

            if doUpdate == 256: A0 = bytes([i])           # SINGLE byte : address writing config of up to 256 bytes
            else:               A0 = struct.pack(">H", i) # DOUBLE bytes: pack address into 2 bytes, big endian, for address writing config of up to 512 bytes

            D0 = bytes([cfgval])
            if D0 == ">": edprint("D0 == > !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")

            bwrt = GMCserData.write(b'<WCFG' + A0 + D0 + b'>>')       # bwrt: Number of bytes written, type: <class 'int'>
            brec = GMCserData.read(1)                                 # brec: is always 0xaa; type: <class 'bytes'>

            duration   = 1000 * (time.time() - startsingle)
            extra      = "  Duration: {:0.1f} ms".format(duration)

            # ### skip some printing
            # min  = 7
            # max  = len(cfgstrip) - min
            # step = 1
            # if i == max: print()
            # else:
            #     if i > min and i < max:
            #         if i % step == 0: print(".", end="", flush=True)
            #         continue

            ix         = int.from_bytes(A0, byteorder="big")
            cx         = int.from_bytes(D0, byteorder="big")
            mdprint(defname + pfs.format(i, ix, cfgval, cx), extra)

    dprint(defname + "Duration All Bytes: {:0.1f} sec".format(time.time() - startAllups))

    # activate new config on device
    updateGMC_Config()

    # overall
    dprint(defname + "Duration Overall w. Update: {:0.1f} sec".format(time.time() - start))

    setIndent(0)


def updateGMC_Config():
    # 13. Reload/Update/Refresh Configuration
    # must come after writing config to enable new config
    # Command: <CFGUPDATE>>
    # Return: 0xAA
    # Firmware supported: GMC-280, GMC-300 Re.2.20 or later
    # in GMC-500Re 1.08 this command returns:  b'0071\r\n\xaa'
    # see http://www.gqelectronicsllc.com/forum/topic.asp?TOPIC_ID=4948 #40

    defname = "updateGMC_Config: "
    dprint(defname)
    setIndent(1)

    rec = serialGMC_COMM(b'<CFGUPDATE>>', 1, orig(__file__))

    dprint(defname + "rec: ", rec)

    setIndent(0)


#rep
def replaceGMC_ConfigValues():
    """puts the config settings into cfg and writes it to the config memory"""
    # remember to NOT call 'setGMC_Config4GL(cfg)' here: it resets all low and high keys !!!


    #### local defs #######################################################

    def replaceBytesInCFG(key, address, bytesrec):
        """write the bytes in byterec to the Python var cfg beginning at address"""

        defname = "replaceBytesInCFG: "

        # rdprint(defname, "key: {}  address:{} bytesrec: '{}'".format(key, address, bytesrec))

        for i in range(0, len(bytesrec)):
            gcfg[address + i] = bytesrec[i]

    #######################################################################

    defname = "replaceGMC_ConfigValues: "

    setBusyCursor()
    dprint(defname, "Modified key settings")
    setIndent(1)

    cdprint(defname, "          Width:Key      Index:Width Value")

    gcfg = bytearray(g.GMC_cfg)           # <class 'bytes'> --> CANNOT be modified, <class 'bytearray'> --> CAN be modified

    # set endian
    if g.GMC_endianness == "big": fcode = ">f"                                            # use big-endian ---   500er, 600er:
    else:                         fcode = "<f"                                            # use little-endian -- other than 500er and 600er:

    # low keys as set by configuration dialog
    # "Alarm", "Speaker", "SaveDataType", "BackLightTOSec",
    #                                        "CalibCPM_0", "CalibuSv_0", "CalibCPM_1", "CalibuSv_1", "CalibCPM_2", "CalibuSv_2"
    # cfgKeyLo:
    #    key                    Value,     Index, width
    #   "Power"             : [ None,     [0,         1] ],     # Power state (read only, not settable!)

    for key in cfgKeyLo:
        cfgrec      = cfgKeyLo[key]
        indxfrom    = cfgrec[1][0]
        width       = cfgrec[1][1]
        cfgkeyVal   = cfgrec[0]

        cdprint(defname, " Lo: {:20s} {:4d}:{:2d}    {}".format(key, indxfrom, width, cfgkeyVal))

        if   width == 1: replaceBytesInCFG(key, indxfrom, struct.pack(">B",   cfgkeyVal))
        elif width == 2: replaceBytesInCFG(key, indxfrom, struct.pack(">H",   cfgkeyVal))
        elif width == 4: replaceBytesInCFG(key, indxfrom, struct.pack(fcode,  cfgkeyVal))

    cdprint()

    # high keys                           WORKING
    # cfgKeyHiDefault = {                 COLUMNS
    # # cfgHiIndex:               0       1        2           3           4           5           6           7
    # #                           from    from     GMC-300(E)  GMC-320+V5  GMC-500     GMC500+     GMC-300S    GMC-800
    # #                           GLcfg   counter  only        only        GMC-600     2.24        no WiFi     no WiFi,
    # #                                                                                            but FET     FET,Cal6
    #     "SSID"              : [ None,   None,    (253,  0),  (69,  16),  (69,  32),  (69,  64),  (253,  0),  (508,  0) ],

    padding    = b"\x00" * 64
    cfgHiIndex = g.GMC_CfgHiIndex
    for key in cfgKeyHi:
        cfgrec      = cfgKeyHi[key]
        indxfrom    = cfgrec[cfgHiIndex][0]
        width       = cfgrec[cfgHiIndex][1]
        cfgkeyVal   = cfgrec[1]                   # the value as int, float, string from the 2nd column

        cdprint(defname, " Hi: {:20s} {:4d}:{:2d}    {}".format(key, indxfrom, width, cfgkeyVal))

        if   width == 0:
            # print(defname, "width==0  key: ", key)
            pass

        elif   width == 1:
            if key == "RTC_OFFSET":
                if g.GMC_HasRTC_Offset and (-59 <= cfgkeyVal <= 59):
                    replaceBytesInCFG(key, indxfrom, struct.pack(">b", cfgkeyVal))  # signed char; single byte values for RTC Offset= -59...+59
                else:
                    replaceBytesInCFG(key, indxfrom, struct.pack(">b", 0))          # Zero is same as switch-off
            else:
                replaceBytesInCFG(key, indxfrom, struct.pack(">B", cfgkeyVal))      # unsigned char single byte values

        elif width == 2:
            replaceBytesInCFG(key, indxfrom, struct.pack(">H", cfgkeyVal))          # double-byte values

        elif width == 4:
            rdprint(defname, "key: '{}'  width:{}  cfgkeyVal: '{}'".format(key, width, cfgkeyVal))
            if key.startswith("Cal6CPM"): replaceBytesInCFG(key, indxfrom, struct.pack(">I",  cfgkeyVal))  # quad-byte values
            if key.startswith("Cal6uSv"): replaceBytesInCFG(key, indxfrom, struct.pack(fcode, cfgkeyVal))  # float values
            # if key.startswith("Cal6CPM"): replaceBytesInCFG(key, indxfrom, struct.pack(">I",  cfgkeyVal))  # quad-byte values
            # if key.startswith("Cal6uSv"): replaceBytesInCFG(key, indxfrom, struct.pack(fcode, cfgkeyVal))  # float values

        else:
            # multi-byte values,
            if g.GMC_WiFiCapable:
                # all remaining keys: 'SSID, Password, Website, URL, UserID, CounterID',  32 or 64 byte wide byte sequences
                # print(defname, "key: ", key)
                keyval = bytes(cfgkeyVal, "utf-8")          # convert to string
                keyval = (keyval + padding)[0:width]        # pad with 0x00 and cut to width
                replaceBytesInCFG(key, indxfrom, keyval)

    vprintGMC_Config("Modified key settings: ", gcfg)

    fprint("Preparation completed, now writing to counter ...")
    QtUpdate()
    writeNewConfig(bytes(gcfg))

# # write the new config data
#     writeGMC_ConfigFull(bytes(gcfg))
#     fprint("Done. New configuration is activated.")  # no verifying anymore! (fprint("Writing is complete; now verifying ..."))
#     QtUpdate()

# # verification of written data
#     # PROBLEM:  the counter may overwrite some data (like date/time, MaxCPM) with new values, before verification is done!
#     # print message but don't stop the programm
#     rawcfg, _, _ = getGMC_RawConfig()                               # read the raw config
#     if verifyCFGwriting(gcfg, rawcfg):
#         gdprint("compare is good")  # ... and compare with intended config
#         fprint("The Configuration was verified ok")
#     else:
#         rdprint("compare is bad")   # ... but ignore if comparison is bad
#         qefprint("The Configuration did NOT verify ok!")
#         qefprint("However, this could also result from a counter's change after the configuration")
#         qefprint("had been written properly, like changing MaxCPM. Verify manually by reloading")
#         efprint ("the configuration.")


    # reread some settings
    g.GMC_FastEstTime = cfgKeyHi["FET"][1]
    getGMC_HistSaveMode()
    g.exgg.setGMCPowerIcon(getconfig=False)

    rdprint(defname, "g.GMC_FastEstTime: ", g.GMC_FastEstTime)

    setIndent(0)
    setNormalCursor()


def writeNewConfig(newcfg):
    """Writes the modified config to the counter"""

    # write the new config data
    writeGMC_ConfigFull(newcfg)
    fprint("Done. New configuration is activated.")  # no verifying anymore! (fprint("Writing is complete; now verifying ..."))
    QtUpdate()

    # verification of written data
    # PROBLEM:  the counter may overwrite some data (like date/time, MaxCPM) with new values, before verification is done!
    # print message but don't stop the programm
    rawcfg, _, _ = getGMC_RawConfig()                               # read the raw config
    if verifyCFGwriting(newcfg, rawcfg):
        gdprint("compare is good")  # ... and compare with intended config
        fprint("The Configuration was verified ok")
    else:
        rdprint("compare is bad")   # ... but ignore if comparison is bad
        qefprint("The Configuration did NOT verify ok!")
        qefprint("However, this could also result from a counter's change after the configuration")
        qefprint("had been written properly, like changing MaxCPM. Verify manually by reloading")
        efprint ("the configuration.")


def verifyCFGwriting(old, new):
    """Compare a newly read CFG to a previous CFG"""

    # PROBLEM: some values in the config may be changed by the counter between writing and
    # reading, resulting in non-identity. These are (at least):
    # bytes: 2 bytes   "MaxCPM"                  : [ None,     (49,      49 + 2) ],     # MaxCPM Hi + Lo Byte
    # bytes: 6 bytes   Last 6 bytes in written-to space takes Date and Time; different location between counters!
    # in GMC-600:      350:0x15E  28  12  15  49  14  22  28  12  15  49  18  22  27  12  23  32  13  22  28  12   2  25  36   1   8  82   0   0   0  22  12  30  15  43  29
    #                  last 6 bytes  at 379dec = 0x17B are:  22  12  30  15  43  29
    #                                                       2022 Dec 30  15h:43m:29s
    # in GMC-500:      FF data begin at 272 dec (no clock data seen in the last 6 positions)

    defname = "verifyCFGwriting: "

    if len(old) != len(new):
        errmsg  = "FAILURE trying to read from / write to the counter!\n"
        errmsg += "You can try to restart GeigerLog, but if the problem persists,\n"
        errmsg += "you may have to FACTORYRESET the counter!"
        edprint(errmsg)
        efprint(errmsg)

    verifyOK = True
    for i in range(0, len(old)):
        if i in (49, 50):                       continue     # ignore; MaxCPM is at same location for all counters
        # if i in (379, 380, 381, 382, 383, 384): continue     # ignore; DateTime; may be atdifferent place for each counter
        if old[i] != new[i]:
            rdprint(defname + "Wrong byte at: addr:{:#05x} ({:3d}) written:{:#04x} read:{:#04x}".format(i, i, old[i], new[i]))
            verifyOK = False

    return verifyOK


#edit
def editGMC_Configuration():
    """Edit the configuration from the GMC config memory"""

    if not g.Devices["GMC"][g.CONN] :
        showStatusMessage("No GMC Device Connected")
        return

    defname = "editGMC_Configuration: "

    ydprint(defname, "$" * 160)
    setIndent(1)

    # get a fresh config and show it
    cfg, error, errmessage = getGMC_RawConfig()
    vprintGMC_Config("Starting cfg", cfg)

    if error < 0 or cfg is None:
        efprint("Error:" + errmessage)
        setIndent(0)
        return

    # create GL dict
    setGMC_Config4GL(cfg)

    # https://www.tutorialspoint.com/pyqt/pyqt_qlineedit_widget.htm
    # https://snorfalorpagus.net/blog/2014/08/09/validating-user-input-in-pyqt4-using-qvalidator/

    setDefault = False  # i.e. False --> show what is read from device

    while True:
        fbox = QFormLayout()
        fbox.setFieldGrowthPolicy (QFormLayout.AllNonFixedFieldsGrow)
        fbox.addRow(QLabel("<span style='font-weight:900;'>All GMC Counter</span>"))

    # Power
        # changing the Power via the config is NOT possible!
        #
        # r01 = QRadioButton("On")
        # r02 = QRadioButton("Off")
        # r01.setChecked(False)
        # r02.setChecked(False)
        # if isGMC_PowerOn() == 'ON': r01.setChecked(True)
        # else:                       r02.setChecked(True)
        # r01.setEnabled(False)
        # r02.setEnabled(False)
        # powergroup = QButtonGroup()
        # powergroup.addButton(r01)
        # powergroup.addButton(r02)

        # hbox0 = QHBoxLayout()
        # hbox0.addWidget(r01)
        # hbox0.addWidget(r02)
        # hbox0.addStretch()

        pmsg = "On" if isGMC_PowerOn() == 'ON' else "Off"
        fbox.addRow(QLabel("Power State"), QLabel("<span style='font-weight:900;'>{}</span>".format(pmsg)))

    # Alarm
        r11 = QRadioButton("On")
        r12 = QRadioButton("Off")
        r11.setChecked(False)
        r12.setChecked(False)
        alarmgroup = QButtonGroup()
        alarmgroup.addButton(r11)
        alarmgroup.addButton(r12)
        hbox1 = QHBoxLayout()
        hbox1.addWidget(r11)
        hbox1.addWidget(r12)
        hbox1.addStretch()
        fbox.addRow(QLabel("Alarm State"), hbox1)
        if isGMC_AlarmOn() == 'ON': r11.setChecked(True)
        else:                       r12.setChecked(True)

    # Speaker
        r21 = QRadioButton("On")
        r22 = QRadioButton("Off")
        r21.setChecked(False)
        r22.setChecked(False)
        speakergroup = QButtonGroup()
        speakergroup.addButton(r21)
        speakergroup.addButton(r22)
        hbox2 = QHBoxLayout()
        hbox2.addWidget(r21)
        hbox2.addWidget(r22)
        hbox2.addStretch()
        fbox.addRow(QLabel("Speaker State"), hbox2)
        if isGMC_SpeakerOn() == 'ON':   r21.setChecked(True)
        else:                           r22.setChecked(True)

    # history Savedatatype
        # 0 "OFF (no history saving)",
        # 1 "CPS, save every second",
        # 2 "CPM, save every minute",
        # 3 "CPM, save hourly average",
        # 4 "CPS, save every second if exceeding threshold",
        # 5 "CPM, save every minute if exceeding threshold",
        index, text = getGMC_HistSaveMode()
        if index not in range(0, 6): index = 0
        cb1   = QComboBox()
        cb1.addItems(g.GMC_savedatatypes)
        cb1.setCurrentIndex(index)

        hbox3 = QHBoxLayout()
        hbox3.addWidget(cb1)
        fbox.addRow(QLabel("History Saving Mode"), hbox3)

    # Light states                       DropDn    reported by
        # LightState = ( "Light: OFF",     # 0     counter: 0
        #                "Light: ON",      # 1     counter: 1
        #                "Timeout: 1",     # 2     counter: 2
        #                "Timeout: 3",     # 3     counter: 4
        #                "Timeout: 10",    # 4     counter: 11
        #                "Timeout: 30",    # 5     counter: 31
        #                 )
        hbox4 = QHBoxLayout()
        cb2   = QComboBox()
        cb2.addItems(LightState)

        LightStatusValue = cfgKeyLo["BackLightTOSec"] [0]
        if   LightStatusValue == 0 : LightStatusIndex = 0
        elif LightStatusValue == 1 : LightStatusIndex = 1
        elif LightStatusValue == 2 : LightStatusIndex = 2
        elif LightStatusValue == 4 : LightStatusIndex = 3
        elif LightStatusValue == 11: LightStatusIndex = 4
        else                       : LightStatusIndex = 5

        cb2.setCurrentIndex(LightStatusIndex)
        hbox4.addWidget(cb2)
        fbox.addRow(QLabel("Light State"), hbox4)

    # Calibration points
        # QIntValidator   (bottom, top[, parent=None]
        # QDoubleValidator(bottom, top, decimals[, parent=None]
        cpmtip   = "Enter an integer number 1 ... 1 Mio"
        usvtip   = "Enter a number 0.00001 ... 100 000"
        cpmlimit = (1, 1000000)
        usvlimit = (0.00001, 100000, 5 )

      # Calibration point #1
        g.exgg.cal1_cpm = QLineEdit()
        g.exgg.cal1_cpm.setFont(g.fontstd)
        g.exgg.cal1_cpm.setValidator (QIntValidator(*cpmlimit))
        g.exgg.cal1_cpm.setToolTip(cpmtip)

        g.exgg.cal1_usv = QLineEdit()
        g.exgg.cal1_usv.setFont(g.fontstd)
        g.exgg.cal1_usv.setValidator(QDoubleValidator(*usvlimit))
        g.exgg.cal1_usv.setToolTip(usvtip)

        g.exgg.cal1_fac = QLabel("")                      # CPM / (µSv/h)
        g.exgg.cal1_fac.setAlignment(Qt.AlignCenter)

        g.exgg.cal1_rfac = QLabel("")                     # reverse: µSv/h/CPM
        g.exgg.cal1_rfac.setAlignment(Qt.AlignCenter)

      # Calibration point #2
        g.exgg.cal2_cpm = QLineEdit()
        g.exgg.cal2_cpm.setValidator (QIntValidator(*cpmlimit))
        g.exgg.cal2_cpm.setFont(g.fontstd)
        g.exgg.cal2_cpm.setToolTip(cpmtip)

        g.exgg.cal2_usv = QLineEdit()
        g.exgg.cal2_usv.setValidator(QDoubleValidator(*usvlimit))
        g.exgg.cal2_usv.setFont(g.fontstd)
        g.exgg.cal2_usv.setToolTip(usvtip)

        g.exgg.cal2_fac = QLabel()
        g.exgg.cal2_fac.setAlignment(Qt.AlignCenter)

        g.exgg.cal2_rfac = QLabel()
        g.exgg.cal2_rfac.setAlignment(Qt.AlignCenter)

      # Calibration point #3
        g.exgg.cal3_cpm = QLineEdit()
        g.exgg.cal3_cpm.setValidator (QIntValidator(*cpmlimit))
        g.exgg.cal3_cpm.setFont(g.fontstd)
        g.exgg.cal3_cpm.setToolTip(cpmtip)

        g.exgg.cal3_usv = QLineEdit()
        g.exgg.cal3_usv.setValidator(QDoubleValidator(*usvlimit))
        g.exgg.cal3_usv.setFont(g.fontstd)
        g.exgg.cal3_usv.setToolTip(usvtip)

        g.exgg.cal3_fac = QLabel()
        g.exgg.cal3_fac.setAlignment(Qt.AlignCenter)

        g.exgg.cal3_rfac = QLabel()
        g.exgg.cal3_rfac.setAlignment(Qt.AlignCenter)

      # Calibration point #4
        g.exgg.cal4_cpm = QLineEdit()
        g.exgg.cal4_cpm.setValidator (QIntValidator(*cpmlimit))
        g.exgg.cal4_cpm.setFont(g.fontstd)
        g.exgg.cal4_cpm.setToolTip(cpmtip)

        g.exgg.cal4_usv = QLineEdit()
        g.exgg.cal4_usv.setValidator(QDoubleValidator(*usvlimit))
        g.exgg.cal4_usv.setFont(g.fontstd)
        g.exgg.cal4_usv.setToolTip(usvtip)

        g.exgg.cal4_fac = QLabel()
        g.exgg.cal4_fac.setAlignment(Qt.AlignCenter)

        g.exgg.cal4_rfac = QLabel()
        g.exgg.cal4_rfac.setAlignment(Qt.AlignCenter)

      # Calibration point #5
        g.exgg.cal5_cpm = QLineEdit()
        g.exgg.cal5_cpm.setValidator (QIntValidator(*cpmlimit))
        g.exgg.cal5_cpm.setFont(g.fontstd)
        g.exgg.cal5_cpm.setToolTip(cpmtip)

        g.exgg.cal5_usv = QLineEdit()
        g.exgg.cal5_usv.setValidator(QDoubleValidator(*usvlimit))
        g.exgg.cal5_usv.setFont(g.fontstd)
        g.exgg.cal5_usv.setToolTip(usvtip)

        g.exgg.cal5_fac = QLabel()
        g.exgg.cal5_fac.setAlignment(Qt.AlignCenter)

        g.exgg.cal5_rfac = QLabel()
        g.exgg.cal5_rfac.setAlignment(Qt.AlignCenter)

      # Calibration point #6
        g.exgg.cal6_cpm = QLineEdit()
        g.exgg.cal6_cpm.setValidator (QIntValidator(*cpmlimit))
        g.exgg.cal6_cpm.setFont(g.fontstd)
        g.exgg.cal6_cpm.setToolTip(cpmtip)

        g.exgg.cal6_usv = QLineEdit()
        g.exgg.cal6_usv.setValidator(QDoubleValidator(*usvlimit))
        g.exgg.cal6_usv.setFont(g.fontstd)
        g.exgg.cal6_usv.setToolTip(usvtip)

        g.exgg.cal6_fac = QLabel()
        g.exgg.cal6_fac.setAlignment(Qt.AlignCenter)

        g.exgg.cal6_rfac = QLabel()
        g.exgg.cal6_rfac.setAlignment(Qt.AlignCenter)


      # Grid
        calOptions = QGridLayout()
        calOptions.setContentsMargins(0,0,0,0)

        row = 0
        calOptions.addWidget(QLabel("Point"),          row, 0)
        calOptions.addWidget(QLabel("CPM"),            row, 1)
        calOptions.addWidget(QLabel("µSv/h"),          row, 2)
        calOptions.addWidget(QLabel("CPM/(µSv/h)"),    row, 3)
        calOptions.addWidget(QLabel("µSv/h/CPM"),      row, 4)

        row = 1
        calOptions.addWidget(QLabel("#1"),             row, 0)
        calOptions.addWidget(g.exgg.cal1_cpm,          row, 1)
        calOptions.addWidget(g.exgg.cal1_usv,          row, 2)
        calOptions.addWidget(g.exgg.cal1_fac,          row, 3)
        calOptions.addWidget(g.exgg.cal1_rfac,         row, 4)

        row = 2
        calOptions.addWidget(QLabel("#2"),             row, 0)
        calOptions.addWidget(g.exgg.cal2_cpm,          row, 1)
        calOptions.addWidget(g.exgg.cal2_usv,          row, 2)
        calOptions.addWidget(g.exgg.cal2_fac,          row, 3)
        calOptions.addWidget(g.exgg.cal2_rfac,         row, 4)

        row = 3
        calOptions.addWidget(QLabel("#3"),             row, 0)
        calOptions.addWidget(g.exgg.cal3_cpm,          row, 1)
        calOptions.addWidget(g.exgg.cal3_usv,          row, 2)
        calOptions.addWidget(g.exgg.cal3_fac,          row, 3)
        calOptions.addWidget(g.exgg.cal3_rfac,         row, 4)

        row = 4
        calOptions.addWidget(QLabel("#4"),             row, 0)
        calOptions.addWidget(g.exgg.cal4_cpm,          row, 1)
        calOptions.addWidget(g.exgg.cal4_usv,          row, 2)
        calOptions.addWidget(g.exgg.cal4_fac,          row, 3)
        calOptions.addWidget(g.exgg.cal4_rfac,         row, 4)

        row = 5
        calOptions.addWidget(QLabel("#5"),             row, 0)
        calOptions.addWidget(g.exgg.cal5_cpm,          row, 1)
        calOptions.addWidget(g.exgg.cal5_usv,          row, 2)
        calOptions.addWidget(g.exgg.cal5_fac,          row, 3)
        calOptions.addWidget(g.exgg.cal5_rfac,         row, 4)

        row = 6
        calOptions.addWidget(QLabel("#6"),             row, 0)
        calOptions.addWidget(g.exgg.cal6_cpm,          row, 1)
        calOptions.addWidget(g.exgg.cal6_usv,          row, 2)
        calOptions.addWidget(g.exgg.cal6_fac,          row, 3)
        calOptions.addWidget(g.exgg.cal6_rfac,         row, 4)

#cal
        if g.GMC_CountCalibPoints == 3:
            # 3 calibration points
            for i in range(1, 4):
                calcpm = cfgKeyLo["CalibCPM_{}".format(i - 1)][0]
                calusv = cfgKeyLo["CalibuSv_{}".format(i - 1)][0]
                calfac = calcpm / calusv
                rcalfac = 1 / calfac

                if   i == 1:
                    g.exgg.cal1_cpm. setText("{:1.0f}".format(calcpm))
                    g.exgg.cal1_usv. setText("{:1.3f}".format(calusv))
                    g.exgg.cal1_fac. setText("{:9.3f}".format(calfac))
                    g.exgg.cal1_rfac.setText("{:9.5f}".format(rcalfac))

                elif i == 2:
                    g.exgg.cal2_cpm. setText("{:1.0f}".format(calcpm))
                    g.exgg.cal2_usv. setText("{:1.3f}".format(calusv))
                    g.exgg.cal2_fac. setText("{:9.3f}".format(calfac))
                    g.exgg.cal2_rfac.setText("{:9.5f}".format(rcalfac))

                elif i == 3:
                    g.exgg.cal3_cpm. setText("{:1.0f}".format(calcpm))
                    g.exgg.cal3_usv. setText("{:1.3f}".format(calusv))
                    g.exgg.cal3_fac. setText("{:9.3f}".format(calfac))
                    g.exgg.cal3_rfac.setText("{:9.5f}".format(rcalfac))

            for i in range(4, 7):
                if   i == 4:
                    g.exgg.cal4_cpm. setText("{:1.0f}".format(g.NAN))
                    g.exgg.cal4_cpm. setEnabled(False)

                    g.exgg.cal4_usv. setText("{:1.3f}".format(g.NAN))
                    g.exgg.cal4_usv. setEnabled(False)

                    g.exgg.cal4_fac. setText("{:9.3f}".format(g.NAN))
                    g.exgg.cal4_rfac.setText("{:9.5f}".format(g.NAN))

                elif i == 5:
                    g.exgg.cal5_cpm. setText("{:1.0f}".format(g.NAN))
                    g.exgg.cal5_cpm. setEnabled(False)

                    g.exgg.cal5_usv. setText("{:1.3f}".format(g.NAN))
                    g.exgg.cal5_usv. setEnabled(False)

                    g.exgg.cal5_fac. setText("{:9.3f}".format(g.NAN))
                    g.exgg.cal5_rfac.setText("{:9.5f}".format(g.NAN))

                elif i == 6:
                    g.exgg.cal6_cpm. setText("{:1.0f}".format(g.NAN))
                    g.exgg.cal6_cpm. setEnabled(False)
                    g.exgg.cal6_usv. setText("{:1.3f}".format(g.NAN))
                    g.exgg.cal6_usv. setEnabled(False)

                    g.exgg.cal6_fac. setText("{:9.3f}".format(g.NAN))
                    g.exgg.cal6_rfac.setText("{:9.5f}".format(g.NAN))
        else:
            # 6 calibration points
            for i in range(1, 7):
                calcpm = cfgKeyHi["Cal6CPM_{}".format(i - 1)][1]
                calusv = cfgKeyHi["Cal6uSv_{}".format(i - 1)][1]
                # rdprint(defname, "calcpm:{}  calusv:{}".format(calcpm, calusv))
                # if calcpm is not None and calusv is not None: calfac = calcpm / calusv
                # else:                                         calfac = g.NAN
                if calcpm is None: calcpm = g.NAN   # was None on GMC-600+ Re2.52 simulate
                if calusv is None: calusv = g.NAN
                if calusv == 0:    calusv = g.NAN
                calfac  = calcpm / calusv
                rcalfac = 1 / calfac

                if   i == 1:
                    g.exgg.cal1_cpm. setText("{:1.0f}".format(calcpm))
                    g.exgg.cal1_usv. setText("{:1.3f}".format(calusv))
                    g.exgg.cal1_fac. setText("{:9.3f}".format(calfac))
                    g.exgg.cal1_rfac.setText("{:9.5f}".format(rcalfac))

                elif i == 2:
                    g.exgg.cal2_cpm. setText("{:1.0f}".format(calcpm))
                    g.exgg.cal2_usv. setText("{:1.3f}".format(calusv))
                    g.exgg.cal2_fac. setText("{:9.3f}".format(calfac))
                    g.exgg.cal2_rfac.setText("{:9.5f}".format(rcalfac))

                elif i == 3:
                    g.exgg.cal3_cpm. setText("{:1.0f}".format(calcpm))
                    g.exgg.cal3_usv. setText("{:1.3f}".format(calusv))
                    g.exgg.cal3_fac. setText("{:9.3f}".format(calfac))
                    g.exgg.cal3_rfac.setText("{:9.5f}".format(rcalfac))

                elif   i == 4:
                    g.exgg.cal4_cpm. setText("{:1.0f}".format(calcpm))
                    g.exgg.cal4_usv. setText("{:1.3f}".format(calusv))
                    g.exgg.cal4_fac. setText("{:9.3f}".format(calfac))
                    g.exgg.cal4_rfac.setText("{:9.5f}".format(rcalfac))

                elif i == 5:
                    g.exgg.cal5_cpm. setText("{:1.0f}".format(calcpm))
                    g.exgg.cal5_usv. setText("{:1.3f}".format(calusv))
                    g.exgg.cal5_fac. setText("{:9.3f}".format(calfac))
                    g.exgg.cal5_rfac.setText("{:9.5f}".format(rcalfac))

                elif i == 6:
                    g.exgg.cal6_cpm. setText("{:1.0f}".format(calcpm))
                    g.exgg.cal6_usv. setText("{:1.3f}".format(calusv))
                    g.exgg.cal6_fac. setText("{:9.3f}".format(calfac))
                    g.exgg.cal6_rfac.setText("{:9.5f}".format(rcalfac))

        fbox.addRow("Calibration Points", calOptions)

        g.exgg.cal1_cpm.textChanged.connect(lambda: checkCalibValidity("cal0cpm", g.exgg.cal1_cpm, g.exgg.cal1_usv, g.exgg.cal1_fac, g.exgg.cal1_rfac ))
        g.exgg.cal1_usv.textChanged.connect(lambda: checkCalibValidity("cal0usv", g.exgg.cal1_cpm, g.exgg.cal1_usv, g.exgg.cal1_fac, g.exgg.cal1_rfac ))
        g.exgg.cal2_cpm.textChanged.connect(lambda: checkCalibValidity("cal1cpm", g.exgg.cal2_cpm, g.exgg.cal2_usv, g.exgg.cal2_fac, g.exgg.cal2_rfac ))
        g.exgg.cal2_usv.textChanged.connect(lambda: checkCalibValidity("cal1usv", g.exgg.cal2_cpm, g.exgg.cal2_usv, g.exgg.cal2_fac, g.exgg.cal2_rfac ))
        g.exgg.cal3_cpm.textChanged.connect(lambda: checkCalibValidity("cal2cpm", g.exgg.cal3_cpm, g.exgg.cal3_usv, g.exgg.cal3_fac, g.exgg.cal3_rfac ))
        g.exgg.cal3_usv.textChanged.connect(lambda: checkCalibValidity("cal2usv", g.exgg.cal3_cpm, g.exgg.cal3_usv, g.exgg.cal3_fac, g.exgg.cal3_rfac ))
        g.exgg.cal4_cpm.textChanged.connect(lambda: checkCalibValidity("cal3cpm", g.exgg.cal4_cpm, g.exgg.cal4_usv, g.exgg.cal4_fac, g.exgg.cal4_rfac ))
        g.exgg.cal4_usv.textChanged.connect(lambda: checkCalibValidity("cal3usv", g.exgg.cal4_cpm, g.exgg.cal4_usv, g.exgg.cal4_fac, g.exgg.cal4_rfac ))
        g.exgg.cal5_cpm.textChanged.connect(lambda: checkCalibValidity("cal4cpm", g.exgg.cal5_cpm, g.exgg.cal5_usv, g.exgg.cal5_fac, g.exgg.cal5_rfac ))
        g.exgg.cal5_usv.textChanged.connect(lambda: checkCalibValidity("cal4usv", g.exgg.cal5_cpm, g.exgg.cal5_usv, g.exgg.cal5_fac, g.exgg.cal5_rfac ))
        g.exgg.cal6_cpm.textChanged.connect(lambda: checkCalibValidity("cal5cpm", g.exgg.cal6_cpm, g.exgg.cal6_usv, g.exgg.cal6_fac, g.exgg.cal6_rfac ))
        g.exgg.cal6_usv.textChanged.connect(lambda: checkCalibValidity("cal5usv", g.exgg.cal6_cpm, g.exgg.cal6_usv, g.exgg.cal6_fac, g.exgg.cal6_rfac ))

 ###############################################################################
    # WiFi settings
        if g.GMC_WiFiCapable:
            # with WiFi
            wififlag = True
            if setDefault : wifimsg = QLabel("<span style='font-weight:900;'>Showing user's configuration read from 'geigerlog.cfg' file</span>")
            else:           wifimsg = QLabel("<span style='font-weight:900;'>Showing active configuration read from the Counter</span>")
        else:
            # no WiFi
            wififlag = False
            wifimsg  = QLabel("<span style='font-weight:400;'>This counter is not WiFi capable</span>")

        dashline = QLabel("<span style='font-weight:500;'>{}</span>".format("-" * 70))
        dashline.setAlignment(Qt.AlignCenter)
        fbox.addRow(dashline)
        fbox.addRow(QLabel("<span style='font-weight:900;'>WiFi Capable Counter</span>"), wifimsg)

    # WiFi On Off settings
        r31 = QRadioButton("On")
        r32 = QRadioButton("Off")
        r31.setChecked(False)
        r32.setChecked(False)
        r31.setEnabled(wififlag)
        r32.setEnabled(wififlag)
        wifigroup = QButtonGroup()
        wifigroup.addButton(r31)
        wifigroup.addButton(r32)
        hbox3 = QHBoxLayout()
        hbox3.addWidget(r31)
        hbox3.addWidget(r32)
        hbox3.addStretch()
        fbox.addRow(QLabel("WiFi State"), hbox3)
        if isGMC_WifiOn() == 'ON':   r31.setChecked(True)
        else:                        r32.setChecked(True)

    # WiFi text settings
        wwifi = 32
        l1e=QLineEdit()                     # SSID (< 32 char)
        l1e.setMaxLength (wwifi)
        l2e=QLineEdit()                     # pw (< 63 char)
        l2e.setMaxLength (wwifi * 2 - 1)
        l3e=QLineEdit()                     # website
        l3e.setMaxLength (wwifi)
        l4e=QLineEdit()                     # url
        l4e.setMaxLength (wwifi)
        l5e=QLineEdit()                     # counter id
        l5e.setMaxLength (wwifi)
        l6e=QLineEdit()                     # user id
        l6e.setMaxLength (wwifi)
        l7e=QLineEdit()                     # period (0 ... 255)
        l7e.setMaxLength (3)

        fbox.addRow("WiFi SSID",                        l1e)
        fbox.addRow("WiFi Password",                    l2e)
        fbox.addRow("Server Website",                   l3e)
        fbox.addRow("Server URL",                       l4e)
        fbox.addRow("Server CounterID",                 l5e)
        fbox.addRow("Server UserID",                    l6e)
        fbox.addRow("Server Period (1 ... 255 min)",    l7e)

        # fill the text fields
        if setDefault : ndx = 0 # i.e. show what is defined in the GeigerLog config
        else:           ndx = 1 # otherwise from device
        l1e.setText(cfgKeyHi["SSID"]      [ndx])    # String
        l2e.setText(cfgKeyHi["Password"]  [ndx])    # String
        l3e.setText(cfgKeyHi["Website"]   [ndx])    # String
        l4e.setText(cfgKeyHi["URL"]       [ndx])    # String
        l5e.setText(cfgKeyHi["CounterID"] [ndx])    # String
        l6e.setText(cfgKeyHi["UserID"]    [ndx])    # String

        l7e.setText(str(cfgKeyHi["Period"][ndx]))   # Int

        # rdprint(defname, "wififlag: ", wififlag)

        l1e.setEnabled(wififlag)
        l2e.setEnabled(wififlag)
        l3e.setEnabled(wififlag)
        l4e.setEnabled(wififlag)
        l5e.setEnabled(wififlag)
        l6e.setEnabled(wififlag)
        l7e.setEnabled(wififlag)

    # FET (Fast Estimate) Capable GMC counter
        # separate with dashline
        dashline3 = QLabel("<span style='font-weight:500;'>{}</span>".format("-" * 70))
        dashline3.setAlignment(Qt.AlignCenter)
        fbox.addRow(dashline3)

        # header
        if not g.GMC_FETenabled:
            FETmsg = QLabel("<span style='font-weight:400;'>This Counter has no FET setting</span>")
        else:
            FETmsg = QLabel("<span style='color:red;'>CAUTION: before chosing anything but 60 see GeigerLog manual</span>")
        fbox.addRow(QLabel("<span style='font-weight:900;'>FET Capable Counter</span>"), FETmsg)

        # selector
        lcb5 = QLabel("FET (Fast Estimate Time) ")
        lcb5.setEnabled(g.GMC_FETenabled)

        cb5 = QComboBox()
        cb5.addItems(["60", "30", "20", "15", "10", "5", "3"])
        cb5.setCurrentIndex(0)
        cb5.setEnabled(g.GMC_FETenabled)

        hbox5 = QHBoxLayout()
        hbox5.addWidget(cb5)
        fbox.addRow(lcb5, hbox5)

    # Deadtime Enable Capable GMC counter
        # separate with dashline
        dashline3 = QLabel("<span style='font-weight:500;'>{}</span>".format("-" * 70))
        dashline3.setAlignment(Qt.AlignCenter)
        fbox.addRow(dashline3)

        # header
        if not g.GMC_DeadTimeEnabled: FETmsg = QLabel("<span style='font-weight:400;'>This Counter has no Deadtime Enable setting</span>")
        else:                         FETmsg = QLabel("<span style='color:red;'>CAUTION: before activating Deadtime Enable see GeigerLog manual</span>")
        fbox.addRow(QLabel("<span style='font-weight:900;'>Deadtime Enable Capable Counter</span>"), FETmsg)

        # Deadtime Enable On Off settings
        r61 = QRadioButton("On")
        r62 = QRadioButton("Off")
        r61.setChecked(False)
        r62.setChecked(False)
        r61.setEnabled(g.GMC_DeadTimeEnabled)
        r62.setEnabled(g.GMC_DeadTimeEnabled)

        if cfgKeyHi["DEADTIME_ENABLE"][ndx] == 1:  r61.setChecked(True)
        else:                                      r62.setChecked(True)

        hbox6 = QHBoxLayout()
        hbox6.addWidget(r61)
        hbox6.addWidget(r62)
        hbox6.addStretch()
        fbox.addRow(QLabel("Deadtime Enabled State"), hbox6)

#rrr
    # RTC_OFFSET enabled
        # separate with dashline
        dashline3 = QLabel("<span style='font-weight:500;'>{}</span>".format("-" * 70))
        dashline3.setAlignment(Qt.AlignCenter)
        fbox.addRow(dashline3)

        # header
        if not g.GMC_HasRTC_Offset: FETmsg = QLabel("<span style='font-weight:400;'>This Counter has no RTC Offset</span>")
        else:                       FETmsg = QLabel("")
        fbox.addRow(QLabel("<span style='font-weight:900;'>RTC Offset Capable Counter</span>"), FETmsg)


        rtcoffset = QLineEdit()
        rtcoffset.setFont(g.fontstd)
        rtcoffset.setToolTip("Enter sec to correct from -59 ... +59 sec")
        rtcoffset.setText(str(cfgKeyHi["RTC_OFFSET"][1]))
        rtcoffset.setValidator (QIntValidator(-59, +59))        # needs more to make fails visible
        rtcoffset.setEnabled(g.GMC_HasRTC_Offset)

        fbox.addRow(QLabel("Enter RTC Offset in -59 ... +59 sec/hour"), rtcoffset)

    # final blank line
        fbox.addRow(QLabel(""))

    # create dialog
        dialog = QDialog()
        dialog.setWindowIcon(g.iconGeigerLog)
        dialog.setFont(g.fontstd)
        dialog.setWindowTitle("Set GMC Configuration of Counter: {} {}".format(g.GMC_Model, g.GMC_FWVersion))
        dialog.setWindowTitle("Set GMC Configuration of Counter: {}".format(g.GMC_DeviceDetected))
        dialog.setWindowModality(Qt.WindowModal)
        dialog.setMinimumWidth(800)

        # buttonbox: https://srinikom.github.io/pyside-docs/PySide/QtGui/QDialogButtonBox.html
        bbox = QDialogButtonBox()
        bbox.setStandardButtons(QDialogButtonBox.Ok|QDialogButtonBox.Cancel|QDialogButtonBox.Reset|QDialogButtonBox.Help)
        bbox.rejected.connect           (lambda: dialog.done(0))    # cancel, ESC key
        bbox.accepted.connect           (lambda: dialog.done(1))    # ok
        bbox.helpRequested.connect      (lambda: dialog.done(2))    # Help: Apply ...
        bbox.clicked .connect           (lambda: dialog.done(3))    # reset

        g.bboxbtn = bbox.button(QDialogButtonBox.Ok)                # ok button
        g.bboxbtn.setEnabled(True)

        bboxRbtn = bbox.button(QDialogButtonBox.Reset)              # Reset button
        bboxRbtn.setText("Show User Configuration")
        bboxRbtn.setEnabled(wififlag)

        bboxhbtn = bbox.button(QDialogButtonBox.Help)               # Help button
        bboxhbtn.setText("Show Counter's Active Configuration")
        bboxhbtn.setEnabled(wififlag)

        layoutV   = QVBoxLayout(dialog)
        layoutV.addLayout(fbox)
        layoutV.addWidget(bbox)

    # execute dialog ###########################################################################################################
        rdprint(defname, "Executing Dialog")
        popupdlg = dialog.exec()
        rdprint(defname, "Executing Dialog done: Response: '{}'   (0=Cancel, 1=ok , 2=readDevice, 3=readGLcfg) ".format(popupdlg))

        if   popupdlg == 0:
            setIndent(0)
            return                                  # reject (Cancel, ESC)
        elif popupdlg == 1:     break               # accept; end while
        elif popupdlg == 2:     setDefault = False  # help, Apply ... i.e. show what is read from device
        elif popupdlg == 3:     setDefault = True   # reset           i.e. show what is defined in the GeigerLog config

    # while loop ends here

    ndx = 0
    # cfgKeyLo["Power"]          [ndx] = 0 if r01.isChecked() else 1 #255  Power cannot be set by config
    cfgKeyLo["Alarm"]          [ndx] = 1 if r11.isChecked() else 0
    cfgKeyLo["Speaker"]        [ndx] = 1 if r21.isChecked() else 0
    cfgKeyLo["SaveDataType"]   [ndx] = cb1.currentIndex()

    cb2ci = cb2.currentIndex()
    if   cb2ci == 0 : LightStatusValue = 0          # "Light: OFF",     # 0     counter: 0
    elif cb2ci == 1 : LightStatusValue = 1          # "Light: ON",      # 1     counter: 1
    elif cb2ci == 2 : LightStatusValue = 2          # "Timeout: 1",     # 2     counter: 2
    elif cb2ci == 3 : LightStatusValue = 4          # "Timeout: 3",     # 3     counter: 4
    elif cb2ci == 4 : LightStatusValue = 11         # "Timeout: 10",    # 4     counter: 11
    else            : LightStatusValue = 31         # "Timeout: 30",    # 5     counter: 31
    cfgKeyLo["BackLightTOSec"] [ndx] = LightStatusValue

    ### begin local def ####################
    def getCalibValue(calibtext, type):
        """convert text to float or int"""

        defname = "getCalibValue: "

        # rdprint(defname, "calibtext: ", calibtext)
        if type == "float":
            try: val = float(calibtext)
            except Exception as e:
                exceptPrint(e, defname)
                val = g.NAN
        else:
            try:
                val = int(float(calibtext))
            except Exception as e:
                exceptPrint(e, defname)
                val = 0

        # rdprint(defname, "calibtext:{}, packstring:{}, val:{}".format(calibtext, type, val))
        return val

    ### end local def ####################

    if g.GMC_CountCalibPoints == 3:
        cfgKeyLo["CalibCPM_0"]    [ndx] = getCalibValue(g.exgg.cal1_cpm.text(), "int")
        cfgKeyLo["CalibuSv_0"]    [ndx] = getCalibValue(g.exgg.cal1_usv.text(), "float")
        cfgKeyLo["CalibCPM_1"]    [ndx] = getCalibValue(g.exgg.cal2_cpm.text(), "int")
        cfgKeyLo["CalibuSv_1"]    [ndx] = getCalibValue(g.exgg.cal2_usv.text(), "float")
        cfgKeyLo["CalibCPM_2"]    [ndx] = getCalibValue(g.exgg.cal3_cpm.text(), "int")
        cfgKeyLo["CalibuSv_2"]    [ndx] = getCalibValue(g.exgg.cal3_usv.text(), "float")
    else:
        # g.GMC_CountCalibPoints == 6
        ndx = 1   # Hi-cfg needs second col, index=1!
        cfgKeyHi["Cal6CPM_0"]     [ndx] = getCalibValue(g.exgg.cal1_cpm.text(), "int")
        cfgKeyHi["Cal6uSv_0"]     [ndx] = getCalibValue(g.exgg.cal1_usv.text(), "float")
        cfgKeyHi["Cal6CPM_1"]     [ndx] = getCalibValue(g.exgg.cal2_cpm.text(), "int")
        cfgKeyHi["Cal6uSv_1"]     [ndx] = getCalibValue(g.exgg.cal2_usv.text(), "float")
        cfgKeyHi["Cal6CPM_2"]     [ndx] = getCalibValue(g.exgg.cal3_cpm.text(), "int")
        cfgKeyHi["Cal6uSv_2"]     [ndx] = getCalibValue(g.exgg.cal3_usv.text(), "float")
        cfgKeyHi["Cal6CPM_3"]     [ndx] = getCalibValue(g.exgg.cal4_cpm.text(), "int")
        cfgKeyHi["Cal6uSv_3"]     [ndx] = getCalibValue(g.exgg.cal4_usv.text(), "float")
        cfgKeyHi["Cal6CPM_4"]     [ndx] = getCalibValue(g.exgg.cal5_cpm.text(), "int")
        cfgKeyHi["Cal6uSv_4"]     [ndx] = getCalibValue(g.exgg.cal5_usv.text(), "float")
        cfgKeyHi["Cal6CPM_5"]     [ndx] = getCalibValue(g.exgg.cal6_cpm.text(), "int")
        cfgKeyHi["Cal6uSv_5"]     [ndx] = getCalibValue(g.exgg.cal6_usv.text(), "float")

    # for key in cfgKeyLo:
    #     rdprint(defname, ">>> cfgKeyLo: {:25s}".format(key), cfgKeyLo[key][ndx])
    # rdprint()

    ndx = 1
    if g.GMC_WiFiCapable:
        try:
            PeriodValue = int(l7e.text())                  # Period setting
            if PeriodValue not in range(1, 256): PeriodValue = 2
        except:
            PeriodValue = 2

        # all get str!!!
        cfgKeyHi["SSID"]       [ndx] = l1e.text()
        cfgKeyHi["Password"]   [ndx] = l2e.text()
        cfgKeyHi["Website"]    [ndx] = l3e.text()
        cfgKeyHi["URL"]        [ndx] = l4e.text()
        cfgKeyHi["CounterID"]  [ndx] = l5e.text()
        cfgKeyHi["UserID"]     [ndx] = l6e.text()
        cfgKeyHi["Period"]     [ndx] = PeriodValue
        cfgKeyHi["WiFi"]       [ndx] = 1 if r31.isChecked() else 0

    if g.GMC_FETenabled:
        key = "FET"
        # rdprint(defname, "getfetval cb5.currentText(): ", cb5.currentText())
        fetval = getCalibValue(cb5.currentText(), "int")
        if not fetval in (3, 5, 10, 15, 20, 30, 60): fetval = 60
        cfgKeyHi[key][ndx] = fetval
        # rdprint("cfgKeyHi: {:25s}".format(key), cfgKeyHi[key][ndx])

    if g.GMC_DeadTimeEnabled:
        key = "DEADTIME_ENABLE"
        cfgKeyHi["DEADTIME_ENABLE"][ndx] = 1 if r61.isChecked() else 0
        rdprint("cfgKeyHi: {:25s}".format(key), cfgKeyHi[key][ndx])

    if g.GMC_HasRTC_Offset:
        key = "RTC_OFFSET"
        rdprint(defname, "RTC_OFFSET rtcoffset.text(): ", rtcoffset.text())
        try:
            val = clamp(int(rtcoffset.text()), -59, +59)
        except Exception as e:
            exceptPrint(e, "RTC_OFFSET illegal")
            val = 0

        cfgKeyHi[key][ndx] = val
        rdprint("cfgKeyHi: {:25s}".format(key), cfgKeyHi[key][ndx])

    fprint(header("Transferring new configuration to counter"))
    QtUpdate()
    replaceGMC_ConfigValues()

    setIndent(0)


def checkCalibValidity(field, var1, var2, var3, var4):
    """verify proper sensitivity data"""

    # GMC popup editing:
    # var1 = g.exgg.calN_cpm
    # var2 = g.exgg.calN_usv
    # var3 = g.exgg.calN_fac
    # var4 = g.exgg.calN_rfac

    # QValidator.Invalid                    0   The string is clearly invalid.
    # QValidator.Intermediate               1   The string is a plausible intermediate value.
    # QValidator.Acceptable                 2   The string is acceptable as a final result; i.e. it is valid.

    # QDoubleValidator.StandardNotation     0   The string is written as a standard number (i.e. 0.015).
    # QDoubleValidator.ScientificNotation   1   The string is written in scientific form. It may have an exponent part(i.e. 1.5E-2).

    if "," in var1.text(): var1.setText(var1.text().replace(",", ""))   # no comma
    if "," in var2.text(): var2.setText(var2.text().replace(",", "."))  # replace comma with period

    defname = "checkCalibValidity: "
    cdprint("\n" + defname + "--- field, var1, var2, var3, var4: ", field, var1.text(), var2.text(), var3.text(), var4.text())

    sender = g.exgg.sender()
    cdprint("sender.text():",   sender.text())

    validator = sender.validator()

    state = validator.validate(sender.text(), 0)
    cdprint("state:    ", state)
    cdprint("state[0]: ", state[0])

    if state[0] == QValidator.Acceptable:
        bgcolor = 'white'
        validMatrix[field] = True

    elif state[0] == QValidator.Intermediate:
        bgcolor = '#fff79a' # yellow
        validMatrix[field] = False

    else:
        burp()
        bgcolor = '#f6989d' # red
        validMatrix[field] = False

    sender.setStyleSheet('QLineEdit { background-color: %s }' % bgcolor)

    if False in validMatrix.values():   g.bboxbtn.setEnabled(False)
    else:                               g.bboxbtn.setEnabled(True)

    try:    ivar1 = int(abs(float(var1.text().replace(",", "."))))
    except: ivar1 = float('nan')

    try:    fvar2 = abs(float(var2.text().replace(",", ".")))
    except: fvar2 = float('nan')

    var3.setText("{:8.5g}".format(float('nan') if fvar2 == 0 else ivar1 / fvar2))   # calib fac  (New)
    var4.setText("{:8.5g}".format(float('nan') if ivar1 == 0 else fvar2 / ivar1))   # calib rfac (Old)


def getGMC_SerialNumber(usbport, baudrate):
    # Get serial number
    # send <GETSERIAL>> and read 7 bytes
    # each nibble of 4 bit is a single hex digit of a 14 character serial number
    # e.g.: F488007E051234
    #
    # return: the serial number as a 14 character ASCII string

    defname = "getGMC_SerialNumber: "
    dprint(defname)
    setIndent(1)

    # rdprint(defname,  "initial  ", getGMC_ExtraByte())

    try:
        with serial.Serial(usbport, baudrate=baudrate, timeout=g.GMC_timeoutR, write_timeout=g.GMC_timeoutW) as ABRser:
            bwrt = ABRser.write(b'<GETSERIAL>>')
            brec = ABRser.read(7)                       # get the GMC device serial number
    except Exception as e:
        errmessage1 = defname + "FAILURE: Reading Serial Number from device; returning None"
        exceptPrint(e, errmessage1)
        setIndent(0)
        return None

    if len(brec) == 7:
        hexlookup = "0123456789ABCDEF"
        srec      = ""
        for i in range(0, 7):
            n1    = ((brec[i] & 0xF0) >> 4)
            n2    = ((brec[i] & 0x0F))
            srec += hexlookup[n1] + hexlookup[n2]
        # dprint(defname + "decoded: '{}' ".format(srec), type(srec))
    else:
        srec = "undefined"

    dprint(defname + "raw: {}  decoded: '{}' ".format(brec, srec), type(srec))

    ###################################################################################
    # DSID - 2nd part of serial number sometimes needed when upgrading firmware
    # response scheint auf 8 char begrenzt zu sein?
    # rdprint(defname, "before DSID  ", getGMC_ExtraByte())
    try:
        with serial.Serial(usbport, baudrate=baudrate, timeout=g.GMC_timeoutR, write_timeout=g.GMC_timeoutW) as ABRser:
            bwrt = ABRser.write(b'<DSID>>')
            brec = ABRser.read(4)        # if DSID is not supported, then the response is \x00 (up to 8 char when so requested)
    except Exception as e:
        exceptPrint(e, defname + "FAILURE: Reading DSID Serial Number from device")

    brec += getGMC_ExtraByte()          # with 300S counter there is no extrabyte

    dprint(defname, "DSID raw: ", brec)

    # rdprint(defname,  "after DSID  ", getGMC_ExtraByte())
    ###################################################################################

    setIndent(0)

    return srec + " - " + str(brec)


def getGMC_Datetime(force=False):
    """Get DateTime from the GMC counter"""

    # Get date and time by sending <GETDATETIME>> and reading 7 bytes: YY MM DD HH MM SS 0xAA
    #
    # return: date and time in the format:
    #           YYYY-MM-DD HH:MM:SS
    # e.g.:     2017-12-31 14:03:19
    #
    # <GETDATETIME>> yields: rec: b'\x12\x04\x13\x0c9;\xaa' , len:7
    #                for:         2018-04-19 12:57:59
    #
    # duration: calling <GETDATETIME>> :  < 45    ms        on GMC-300S @ 57600 baud
    #           1 print cmd            :  <  0.4  ms
    #           Other                  :  <  0.02 ms


    defname = "getGMC_Datetime: "
    # cdprint(defname)
    setIndent(1)

    dtrec  = "2000-01-01 00:00:01" # default fake date to use on error

    if not force:
        if g.logging:
            emsg = "Cannot get GMC DateTime when logging. Stop logging first"
            return (dtrec, -1, emsg)

    # this call takes < 45 ms
    # dstart  = time.time()
    rec, error, errmessage = serialGMC_COMM(b'<GETDATETIME>>', 7, orig(__file__))
    # ddur1   = 1000 * (time.time() - dstart)

    if rec is None:
        dprint(defname + "ERROR: no DateTime received - ", errmessage)
    else:
        if error == 0 or error == 1:  # Ok or only-Warning
            try:
                dtrec = dt.datetime(rec[0] + 2000, rec[1], rec[2], rec[3], rec[4], rec[5])
            except Exception as e:
                # conversion of counter values to Python DateTime failed
                # dtrec       = "2099-09-09 09:09:09" # overwrite rec with fake date
                error       = -1
                errmessage  = "ERROR getting DateTime"
                if rec ==  [0, 1, 1, 0, 0, 80, 170]:    # the values found after first start! ??? sec is 80, das kann nicht sein???
                    errmessage  += " - Set at device first!"

        else:   # a real error
            dprint(defname, "ERROR getting DATETIME: ", errmessage, debug=True)

        # cdprint(defname + "raw: len: {} rec: {}   parsed: {}  errmsg: '{}'".format(len(rec), str(rec), dtrec, errmessage))

    # ddur2  = 1000 * (time.time() - dstart)
    # rdprint(defname, "dur <GETDATETIME>>:{:0.3f}ms  dur total: +{:0.3f}ms  GMC DateTime={} - {}=CompTime".format(ddur1, ddur2 - ddur1, dtrec, stime()[-5:]))

    setIndent(0)

    return (dtrec, error, errmessage)


def getGMC_TEMP():
    # NOTE: Temperature may be completely inactive in 500 and 600 versions
    # and or produce random results! see:
    # http://www.gqelectronicsllc.com/forum/topic.asp?TOPIC_ID=4948
    #
    # Get temperature
    # Firmware supported: GMC-320 Re.3.01 or later (NOTE: Not for GMC-300!)
    # send <GETTEMP>> and read 4 bytes
    # Return: Four bytes celsius degree data in hexdecimal: BYTE1,BYTE2,BYTE3,BYTE4
    # Here: BYTE1 is the integer part of the temperature.
    #       BYTE2 is the decimal part of the temperature.
    #       BYTE3 is the negative signe if it is not 0.  If this byte is 0,
    #       then current temperture is greater than 0, otherwise the temperature is below 0.
    #       BYTE4 always 0xAA (=170dec)

    defname = "getGMC_TEMP: "
    dprint(defname)
    setIndent(1)

    rec, error, errmessage = serialGMC_COMM(b'<GETTEMP>>', 4, orig(__file__))

    # # TESTING example for '-28.8 °C' ###
    # rec        = b'\x1c\x08\x01\xaa'
    # error      = 0
    # errmessage = "testing"
    # ####################################

    srec = ""
    for i in range(len(rec)): srec += "{}, ".format(rec[i])

    cdprint(defname + "Temp raw: rec= {} (=dec: {}), err={}, errmessage='{}'".format(rec, srec[:-2], error, errmessage))

    if error == 0 or error == 1:  # Ok or Warning
        if "GMC-3" in g.GMC_DeviceDetected :   # all 300 series
            temp = rec[0] + rec[1]/100.0     # unclear: is  decimal part rec[1] single digit or a 2 digit?
                                            # 3 digit not possible as byte value is from 0 ... 255
                                            # expecting rec[1] always from 0 ... 9
            if rec[2] != 0 : temp *= -1
            # if rec[1]  > 9 : temp  = "ERROR: Temp={} - illegal value found for decimal part of temperature={}".format(temp, rec[1])

            # edprint("temp: ", rec[0] + rec[1]/100.0, "  ", rec[0] + rec[1]/10.0)
            rec = temp

        elif   "GMC-5" in g.GMC_DeviceDetected \
            or "GMC-6" in g.GMC_DeviceDetected:  # GMC-500/600
            # rec[1] is always one of dec: 0, 8, 10, 12, 14 - nothong else???
            # temp = rec[0] + rec[1]/10.0    # unclear: is  decimal part rec[1] single digit or a 2 digit?
            temp = rec[0] + rec[1]/100.0     # unclear: is  decimal part rec[1] single digit or a 2 digit?
                                             # 3 digit not possible as byte value is from 0 ... 255
                                             # expecting rec[1] always from 0 ... 9
            #if rec[2] <= 0 : temp *= -1     # guessing: value=1 looks like positive Temperature. Negative is??? Maybe not right at all
            if rec[2] != 0 : temp *= -1      # using the old definition again
            # if rec[1]  > 9 : temp  = "ERROR: Temp={} - illegal value found for decimal part of temperature={}".format(temp, rec[1])

            # edprint("temp: ", rec[0] + rec[1]/100.0, "  ", rec[0] + rec[1]/10.0, "  ", rec[0] + (rec[1]<<4)/100.0)

            rec = temp

        else: # perhaps even 200 series?
            rec = "UNDEFINED"

    dprint(defname + "Temp      rec= {}, err={}, errmessage='{}'".format(rec, error, errmessage))

    setIndent(0)

    return (rec, error, errmessage)


def getGMC_GYRO():
    # Get gyroscope data
    # Firmware supported:
    #   GMC-320 Re 3.01 or later (NOTE: Not for GMC-300!)
    #   GMC-800Re1.08            : No support for gyro readout
    # Send <GETGYRO>> and read 7 bytes
    # Return: Seven bytes gyroscope data in hexdecimal: BYTE1,BYTE2,BYTE3,BYTE4,BYTE5,BYTE6,BYTE7
    # Here: BYTE1,BYTE2 are the X position data in 16 bits value. The first byte is MSB byte data and second byte is LSB byte data.
    #       BYTE3,BYTE4 are the Y position data in 16 bits value. The first byte is MSB byte data and second byte is LSB byte data.
    #       BYTE5,BYTE6 are the Z position data in 16 bits value. The first byte is MSB byte data and second byte is LSB byte data.
    #       BYTE7 always 0xAA

    defname = "getGMC_GYRO: "

    dprint(defname)
    setIndent(1)

    if not g.GMC_HasGyroCommand:
        (rec, error, errmessage) = "Gyro not supported", -1, "Unsupported on this device"
        dprint(defname, "(rec, error, errmessage): ", (rec, error, errmessage))
        setIndent(0)
        return (rec, error, errmessage)

    rec, error, errmessage = serialGMC_COMM(b'<GETGYRO>>', 7, orig(__file__))
    dprint(defname + "raw: rec={}, err={}, errmessage='{}'".format(rec, error, errmessage))

    if error in (0, 1):             # Ok or Warning
        x = rec[0] * 256 + rec[1]
        y = rec[2] * 256 + rec[3]
        z = rec[4] * 256 + rec[5]
        srec = "X=0x{:04x}, Y=0x{:04x}, Z=0x{:04x}   ({}, {}, {})".format(x, y, z, x, y, z)
    else:
        srec = "Failure getting Gyro data:  rec='{}' errmsg='{}".format(rec, errmessage)

    dprint(defname, "(srec, error, errmessage): ", (srec, error, errmessage))
    setIndent(0)

    return (srec, error, errmessage)


def setGMC_POWEROFF():
    # 12. Power OFF
    # Command: <POWEROFF>>
    # Return: none
    # Firmware supported: GMC-280, GMC-300 Re.2.11 or later

    # sleeping after Power OFF
    #   on a GMC-300E+ a minimum of 2 sec is needed
    #   on a GMC-500+  a minimum of 1 sec is needed
    #   using 3 sec to be safe

    rec  = serialGMC_COMM(b'<POWEROFF>>', 0, orig(__file__))
    dprint("setGMC_POWEROFF: ", rec)

    time.sleep(3)

    return rec


def setGMC_POWERON():
    # 26. Power ON
    # Command: <POWERON>>
    # Return: none
    # Firmware supported: GMC-280, GMC-300, GMC-320 Re.3.10 or later

    # sleeping after Power ON
    #   on a GMC-300E+ not tested
    #   on a GMC-500+  not tested
    #   using 3 sec to be safe, as for setGMC_POWEROFF

    rec  = serialGMC_COMM(b'<POWERON>>', 0, orig(__file__))
    dprint("setGMC_POWERON: ", rec)

    time.sleep(3)

    return rec


def setGMC_REBOOT():
    # 21. Reboot unit
    # command: <REBOOT>>
    # Return: None
    # Firmware supported: GMC-280, GMC-300 Re.3.00 or later
    # Duration: 20.2 ms
    # GMC 300 takes 580 ms before responding normally

    defname = "setGMC_REBOOT: "
    dprint(defname)
    setIndent(1)

    rec  = serialGMC_COMM(b'<REBOOT>>', 0, orig(__file__))
    dprint(defname, rec)

    time.sleep(0.6)

    setIndent(0)

    return rec


def setGMC_FACTORYRESET():
    # 20. Reset unit to factory default
    # command: <FACTORYRESET>>
    # Return: 0xAA
    # Firmware supported: GMC-280, GMC-300 Re.3.00 or later

    defname = "setGMC_FACTORYRESET: "
    dprint(defname)
    setIndent(1)

    rec  = serialGMC_COMM(b'<FACTORYRESET>>', 1, orig(__file__))
    dprint(defname, rec)
    time.sleep(0.1)
    dprint(defname + "Done")
    setIndent(0)

    return rec


#
# Derived commands and functions
#

def getGMC_DeltaTime(force=False):
    """reads the DateTime from both computer and device, converts into a number, and returns delta time in sec"""

    defname = "getGMC_DeltaTime: "
    cdprint(defname)
    setIndent(1)
    time_delta = g.NAN

    recDateTime, error, errmessage = getGMC_Datetime(force=force)       # recDateTime like: "2000-01-01 00:00:01"
    if error < 0:
        # error occurred
        edprint(defname + "recDateTime:{}, error:{}, errmessage:'{}'".format(recDateTime, error, errmessage))

    else:
        # ok or only Warning
        time_computer = longstime()
        time_device   = str(recDateTime)
        time_delta    = round((mpld.datestr2num(time_computer) - mpld.datestr2num(time_device)) * 86400, 3)
        if   time_delta > 0:  tmsg = "Device is slower"
        elif time_delta < 0:  tmsg = "Device is faster"
        else:                 tmsg = "same"
        cdprint(defname + "device:{}, computer:{}, Delta Comp ./. Dev: {:+0.1f} sec - {}".format(time_device, time_computer, time_delta, tmsg))

        setIndent(0)

    return (time_delta, recDateTime)


def isGMC_PowerOn(getconfig=False, force=False):
    """Checks Power status in the configuration
    returns: ON, OFF, or UNKNOWN as string"""

    # PowerOnOff byte:
    # 300 series
    #   at config offset  : 0       :    0 for ON and 255 for OFF
    #   http://www.gqelectronicsllc.com/forum/topic.asp?TOPIC_ID=4948  Reply #14
    #   confirmed in Reply #17
    #
    # 500/600 series
    #   at config offset  : 0       :    0 for ON, and 1 for OFF
    #
    # 800 series ???????????????????????

    defname = "isGMC_PowerOn: "
    dprint(defname)
    setIndent(1)

    if getconfig:
        # get new cfg
        # if g.logging and not force:
        #     emsg = "Cannot access Device's config when logging"
        #     rdprint(defname, emsg)
        #     setIndent(0)
        #     return emsg

        cfg, error, _ = getGMC_RawConfig()      # get the raw config, be it real or simulated
        if error == 0:
            g.GMC_cfg = cfg                     # set the cfg global value
            power     = g.GMC_cfg[0]
        else:
            msg = "Failure reading the counter's config - Is counter connected?"
            rdprint(defname, msg)
            QueuePrint(msg)
            power = -1                          # dummy value
    else:
        # use existing cfg
        power = g.GMC_cfg[0]

    if   power == 0:        p = "ON"            # all counter
    elif power == 255:      p = "OFF"           # 300, 800 series
    elif power == 1:        p = "OFF"           # 500, 600 series
    else:                   p = "Unknown"
    dprint(defname, p)

    if   p == "ON":   g.exgg.dbtnGMCPower.setIcon(QIcon(QPixmap(os.path.join(g.resDir, 'icon_power-round_on.png'))))
    elif p == "OFF":  g.exgg.dbtnGMCPower.setIcon(QIcon(QPixmap(os.path.join(g.resDir, 'icon_power-round_off.png'))))
    else:             g.exgg.dbtnGMCPower.setIcon(QIcon(QPixmap(os.path.join(g.resDir, 'icon_power-round_X.png'))))

    setIndent(0)
    return p


def isGMC_AlarmOn():
    """Checks Alarm On status in the configuration.
    Alarm is at offset:1"""

    try:    c = g.GMC_cfg[1]
    except: return "UNKNOWN"

    if   c == 0:            p = "OFF"
    elif c == 1:            p = "ON"
    elif c == 255:          p = "ON"    # stimmt das so?
    else:                   p = c

    return p


def isGMC_SpeakerOn():
    """Checks Speaker On status in the configuration.
    Speaker is at offset:2"""

    try:    c = g.GMC_cfg[2]
    except: return "UNKNOWN"

    if   c == 0:            p = "OFF"
    elif c == 1:            p = "ON"
    elif c == 255:          p = "ON"        # stimmt das so?
    else:                   p = c

    return p


def isGMC_WifiOn():
    """Checks WiFi status in the configuration"""

    # if not g.GMC_WifiEnabled: return "No WiFi"
    if g.GMC_CfgHiIndex in (0, 5): return "No WiFi"

    defname = "isGMC_WifiOn: "

    try:
        c = g.GMC_cfg[cfgKeyHi["WiFi"][g.GMC_CfgHiIndex][0]]
    except Exception as e:
        exceptPrint(e, defname)
        c = 255

    #~print(defname + "c=", c)

    if   c == 0:            return "OFF"
    elif c == 1:            return "ON"
    else:                   return "Unknown"


def getLightStatus():

    # try:    c = ord(cfgKeyLo["BackLightTOSec"][0])
    # except: return "UNKNOWN"

    c = cfgKeyLo["BackLightTOSec"][0]

    if   c == 0     : p = "Light: OFF"
    elif c == 1     : p = "Light: ON"
    elif c is None  : p = "Light: Unknown"
    else            : p = "Timeout: {} sec".format(c - 1)

    return p


def getGMC_BatteryType():
    """Checks Battery Type in the configuration"""

    # cfg Offset Battery = 56
    # Battery Type: 1       is non rechargeable.
    #               0       is chargeable.
    #               else    unsupported function

    c = cfgKeyLo["Battery"][0]

    if   c == 0:    p = "Rechargeable"
    elif c == 1:    p = "Non-Rechargeable"
    else:           p = "Unsupported on this device"

    return p


# is not in use; keep for config reference
def XXXgetGMC_BAUDRATE():
    """reads the baudrate from the counter's configuration data"""

    # NOTE: kind of pointless, because in order to read the config data
    # from the device you must already know the baudrate, or the comm
    # will fail :-/

    # discovered for the 300 series:
    #     baudrate = 1200         # config setting:  64
    #     baudrate = 2400         # config setting: 160
    #     baudrate = 4800         # config setting: 208
    #     baudrate = 9600         # config setting: 232
    #     baudrate = 14400        # config setting: 240
    #     baudrate = 19200        # config setting: 244
    #     baudrate = 28800        # config setting: 248
    #     baudrate = 38400        # config setting: 250
    #     baudrate = 57600        # config setting: 252
    #     baudrate = 115200       # config setting: 254
    #     #baudrate = 921600      # config setting: not available
    #
    # discovered for the GMC-500 and 600 series
    # by EmfDev from GQ from here:
    # http://www.gqelectronicsllc.com/forum/topic.asp?TOPIC_ID=4948 Reply #14
    # The baudrate config is now
    #     baudrate = 115200       # config setting: 0
    #     baudrate = 1200         # config setting: 1
    #     baudrate = 2400         # config setting: 2
    #     baudrate = 4800         # config setting: 3
    #     baudrate = 9600         # config setting: 4
    #     baudrate = 14400        # config setting: 5
    #     baudrate = 19200        # config setting: 6
    #     baudrate = 28800        # config setting: 7
    #     baudrate = 38400        # config setting: 8
    #     baudrate = 57600        # config setting: 9

    defname = "getGMC_BAUDRATE: "
    dprint(defname)
    setIndent(1)

    if  "GMC-3" in g.GMC_DeviceDetected:
        # all 300 series
        brdict  = {64:1200, 160:2400, 208:4800, 232:9600, 240:14400, 244:19200, 248:28800, 250:38400, 252:57600, 254:115200}

    elif "GMC-5" in g.GMC_DeviceDetected or "GMC-6" in g.GMC_DeviceDetected :
        # 500, 500+, 600, 600+
        brdict  = {0:115200, 1:1200, 2:2400, 3:4800, 4:9600, 5:14400, 6:19200, 7:28800, 8:38400, 9:57600}

    else:
        brdict  = {}

    # print(defname + "cfg Baudrate:")
    # for key, value in sorted(brdict.items()):
    #    print("      {:08b} {:3d} {:6d}".format(key, key, value))

    try:
        key = ord(cfgKeyLo["Baudrate"][0])
        cdprint("key: ", key)
        rec = brdict[key]
    except Exception as e:
        exceptPrint(e, "cfgKeyLo[Baudrate] ")
        key = -999
        rec = "ERROR: Baudrate cannot be determined"

    dprint(defname + str(rec) + " with cfgKeyLo[\"Baudrate\"][0]={}".format(key))

    setIndent(0)

    return rec


#xyz
def serialGMC_COMM(sendtxt, RequestLength, caller=("", "", -1)):
    """open the port to make the serial call
    return: (brec, error, errmessage)
    """
    # brec:       bytes as received
    # error==0:   OK
    # error==1:   Warning
    # error==-1:  ERROR
    # errmessage: <string>

    defname = "serialGMC_COMM: "
    # dprint(defname)
    setIndent(1)

    brec        = b""
    error       = -1
    errmessage  = "Error Message is Undefined"

    if g.GMC_usbport is not None and os.path.exists(g.GMC_usbport):
        # gdprint(defname, "USB port: '{}'  exists.".format(g.GMC_usbport))
        try:
            with  serial.Serial(g.GMC_usbport, g.GMC_baudrate, timeout=g.GMC_timeoutR, write_timeout=g.GMC_timeoutW) as g.GMCser:
                brec, error, errmessage = origserialGMC_COMM(sendtxt, RequestLength, caller=caller, serhandle=g.GMCser)

        except Exception as e:
            exceptPrint(e, defname + "'{}'".format(errmessage))
    else:
        # USB port is missing
        errmessage  = "USB port '{}' does not exist".format(g.GMC_usbport)
        rdprint(defname, errmessage)

    setIndent(0)
    return (brec, error, errmessage)


def origserialGMC_COMM(sendtxt, RequestLength, caller=("", "", -1), serhandle=None):
    """write to and read from serial port, exit on serial port error
    return: (brec, error, errmessage)
        brec:       bytes sequence as received
        error:      ==0:OK,  ==1:Warning,  ==-1:ERROR
        errmessage: string
    """

    defname = "origserialGMC_COMM: "
    # rdprint(defname + "sendtxt:{}  RequestLength:{}  caller:'{}', serhandle-Port:{}".format(sendtxt, RequestLength, caller, serhandle.port))
    setIndent(1)

    brec        = None
    error       = 0
    errmessage  = ""

    while True:

    #write sendtxt to serial port
        breakWrite = True
        srcinfo    = ""
        try:
            bwrt = serhandle.write(sendtxt)          # bwrt = no of bytes written
            breakWrite = False

        except serial.SerialTimeoutException as e:
            # Exception that is raised ONLY on WRITE timeouts.
            srcinfo = defname + "ERROR: WRITE failed with SerialTimeoutException when writing: '{}'".format(sendtxt)
            exceptPrint(e, srcinfo)

        except serial.SerialException as e:
            srcinfo = defname + "ERROR: WRITE failed with SerialException when writing: '{}'".format(sendtxt)
            exceptPrint(e, srcinfo)

        except Exception as e:
            srcinfo = defname + "ERROR: WRITE failed with Exception when writing: '{}'".format(sendtxt)
            exceptPrint(e, srcinfo)

        if breakWrite:
            terminateGMC()
            brec        = None
            error       = -1
            errmessage  = defname + "ERROR: WRITE failed. See log for details"
            break


    # read from serial port
        startrtime = time.time()

        breakRead = True
        srcinfo   = ""
        srce      = ""
        try:
            brec  = serhandle.read(RequestLength)
            brec += getGMC_ExtraByte(serhandle)
            # mdprint(defname, "brec: ", brec)
            breakRead  = False

        except serial.SerialException as e:
            srcinfo = defname + "EXCEPTION: READ failed with SerialException"
            exceptPrint(e, srcinfo)
            srce    = e

        except Exception as e:
            srcinfo = defname + "EXCEPTION: READ failed with Exception"
            exceptPrint(e, srcinfo)
            srce    = e

        # rdprint(defname, "srce: ", srce, "  srcinfo: ", srcinfo)

        try:
            if srcinfo > "":
                edprint(defname + "EXCEPTION: caller is: {} in line no: {}".format(caller[0], caller[2]), debug=True)
                exceptPrint(srce, srcinfo)
        except Exception as e:
            rdprint(defname, "srcinfo empty?  e: ", e)


        rdur  =  1000 * (time.time() - startrtime)
        # rdprint(defname + "caller is: {} in line no: {} duration: {:0.1f} ms".format(caller[0], caller[2], rdur))

        if breakRead:
            terminateGMC()
            brec        = None
            error       = -1
            errmessage  = defname + "ERROR: READ failed. See log for details"
            break

    # Retry loop - if len(brec) < RequestLength
        if len(brec) < RequestLength:
            efprint("{} Got {} data bytes, expected {} for call '{}'.".format(stime(), len(brec), RequestLength, cleanHTML(sendtxt)))

            # check for read timeout
            if rdur > (g.GMC_timeoutR * 1000):
                # yes, a read timeout
                msg  = "{} GMC TIMEOUT ERROR Serial Port; command {} exceeded {:3.1f}s".format(stime(), sendtxt, g.GMC_timeoutR)
                qefprint(cleanHTML(msg)) # escaping needed as GMC commands like b'<GETCPS>>' have <> brackets
                edprint(defname + msg, " - rdur:{:5.1f} ms".format(rdur), debug=True)

            efprint("{} Got {} data bytes, expected {} for call '{}'.".format(stime(), len(brec), RequestLength, cleanHTML(sendtxt)))
            qefprint("{} Retrying.".format(stime()))
            QtUpdate()

            edprint(defname + "ERROR: Received length: {} is less than requested: {}".format(len(brec), RequestLength), debug=True)
            # edprint(defname + "brec (len={}): {}".format(len(brec), BytesAsHex(brec)))

            # RETRYING
            count    = 0
            countmax = 3
            while True:
                count += 1
                errmsg = defname + "RETRY to get full return record, retrial #{}".format(count)
                dprint(errmsg, debug=True)

                time.sleep(0.5)                         # extra sleep after not reading enough data
                extra = getGMC_ExtraByte(serhandle)     # just to make sure the pipeline is clean

                serhandle.write(sendtxt)

                rtime = time.time()
                brec   = serhandle.read(RequestLength)
                dprint("Timing (ms): Retry read:{:6.3f}".format(1000 * (time.time() - rtime)))

                if len(brec) == RequestLength:
                    bah = BytesAsHex(brec)
                    if len(bah) > 50: sbah = ", brec (1st 20 Bytes): " + bah[:20]
                    else:             sbah = ", brec:" + bah
                    dprint(defname + "RETRY: OK now. Length is {} bytes as requested. Continuing normal cycle".format(len(brec)), sbah, debug=True)
                    errmessage += "; ok after {} retry".format(count)
                    extra = getGMC_ExtraByte(serhandle)   # just to make sure the pipeline is clean
                    fprint("<green>{} Retry successful.".format(stime()))
                    g.exgg.addGMC_Error(errmessage)
                    break
                else:
                    dprint(u"RETRY:" + defname + "RequestLength is {} bytes. Still NOT ok; trying again".format(len(brec)), debug=True)
                    pass

                if count >= countmax:
                    dprint(defname + "RETRY: Retried {} times, always failure, giving up. Serial communication error.".format(count), debug=True)
                    error       = -1
                    errmessage  = "ERROR communicating via serial port. Giving up."
                    efprint(errmessage)
                    g.exgg.addGMC_Error(errmessage)
                    break

                efprint("ERROR communicating via serial port. Retrying again.")

        break

    setIndent(0)

    # rdprint(defname, "(brec, error, errmessage): ", (brec, error, errmessage))
    return (brec, error, errmessage)


def GMC_setDateTime():
    """ set date and time on GMC device to computer date and time"""

    defname = "GMC_setDateTime: "
    dprint(defname)
    setIndent(1)

    fprint(header("Set DateTime of GMC Device"))
    fprint("Setting Device DateTime to GeigerLog DateTime")

    GMC_WriteDateTime()

    tmsg = getDeltaTimeMessage(*getGMC_DeltaTime())
    fprint(tmsg)

    dprint(defname, "GMC Datetime was set")
    setIndent(0)


def getGMC_HistSaveMode():
    """
    Bytenumber:32  Parameter: CFG_SaveDataType
    savedatatypes:
    0 = OFF (no history saving)
    1 = CPS, save every second
    2 = CPM, save every minute
    3 = CPM, save hourly average
    4 = CPS, save every second if exceeding threshold
    5 = CPM, save every minute if exceeding threshold
    """

    defname = "getGMC_HistSaveMode: "
    dprint(defname)
    setIndent(1)

    sdt = "UNKNOWN"
    txt = "UNKNOWN"

    try:
        sdt                 = cfgKeyLo["SaveDataType"][0]
        # rdprint(defname, "savedatatypes: ", savedatatypes, "  sdt: ", sdt)
        if sdt <= len(savedatatypes): txt = savedatatypes[sdt]
        else:                         txt = "UNKNOWN"
        g.GMC_savedataindex = sdt
        g.GMC_savedatatype  = txt
    except Exception as e:
        exceptPrint(e, defname + "Error: undefined type: {}".format(sdt))

    else:
        dprint(defname + "return: (index:{}, mode: '{}')".format(sdt, txt) )

    setIndent(0)
    return (sdt, txt)  # (<index>, <mode as text>)


def fprintGMC_ConfigMemory():
    """prints the 256 or 512 bytes of device configuration memory to the NotePad"""

    defname = "fprintGMC_ConfigMemory: "
    setBusyCursor()

    fprint(header("GMC Device Configuration"))
    dprint(defname)
    setIndent(1)

    cfg, error, errmessage = getGMC_RawConfig()

    fText = ""
    if   cfg is None:
        msg = "FAILURE getting config from device. See log for details."
        dprint(defname + msg + " errmessage: " + errmessage)
        fText += msg
    else:
        lencfg = len(cfg)
        if error < 0 and lencfg not in (256, 512):
            msg = "FAILURE getting config from device. See log for details."
            dprint(defname + msg + " errmessage: " + errmessage)
            fText += msg
        else:
            # len(cfg) == 256 or == 512, even with error
            fText     += "The size of the configuration memory is: {} bytes\n".format(lencfg)
            fText     += "|Index | |------------ HEX -------------|   |------------------ DEC ------------------|\n"
            cfgcopy    = copy.copy(cfg)                 # use copy of cfg
            cfgstrp    = cfgcopy.rstrip(b'\xFF')        # remove the right-side FF values

            lencfgstrp = len(cfgstrp)
            if lencfgstrp == 0:
                fText += "ERROR: GMC Configuration memory is empty. Try a factory reset!"
            else:
                rr = 10
                for i in range(0, lencfgstrp, rr):
                    pcfg = "{:3d}:{:03X}:  ".format(i, i)
                    for j in range(0, rr):
                        k = i + j
                        if j == 5: pcfg += " "
                        # if k < lencfgstrp:  pcfg += "{:02x} ".format(cfgstrp[k])
                        if k < lencfgstrp:  pcfg += "{:02X} ".format(cfgstrp[k])

                    pcfg += "    "
                    # print("k: ", k, "lencfgstrp % rr: ", lencfgstrp % rr)
                    if k >= lencfgstrp: pcfg += "   " * (rr - (lencfgstrp % rr))

                    for j in range(0, rr):
                        k = i + j
                        if j == 5: pcfg += "  "
                        if k < lencfgstrp:  pcfg += "{:3d} ".format(cfgstrp[k])

                    fText += pcfg + "\n"

                if lencfgstrp < lencfg:
                    # fText += "Remaining {} values up to address {} are all '0xff=255'\n".format(lencfg - lencfgstrp, lencfg - 1)
                    fText += "Remaining {} values up to address {} are all '0xFF=255'\n".format(lencfg - lencfgstrp, lencfg - 1)

                fText += "\nThe configuration as ASCII (byte 0xFF as 'F', other non-ASCII characters as '.'):\n"
                fText += cleanHTML(fBytesAsASCIIFF(cfgcopy))

    vprintGMC_Config(defname, cfg)
    fprint(fText)

    setIndent(0)
    setNormalCursor()

#iii
def getInfoGMC(extended=False, force=False):
    """builds string msg of basic or extended info on the GMC device"""

    defname  = "getInfoGMC: "
    dprint(defname)
    setIndent(1)

    tmp      = "{:30s}{}\n"
    gmcinfo  = ""
    gmcinfo += tmp.format("Configured Connection:", "Port:'{}' Baud:{} Timeouts[s]: R:{} W:{}".format(
        g.GMC_usbport,
        g.GMC_baudrate,
        g.GMC_timeoutR,
        g.GMC_timeoutW)
    )

    if not g.Devices["GMC"][g.CONN]:
        msg = "Device is not connected"
        dprint(msg)
        setIndent(0)
        return gmcinfo + "<red>" + msg + "</red>"

    # device name
    gmcinfo += tmp.format("Connected Device:", g.GMC_DeviceDetected)

    # GMC_Variables
    gmcinfo += tmp.format("Configured Variables:", g.GMC_Variables)

    # Tube sensitivities
    gmcinfo += getTubeSensitivities(g.GMC_Variables)


    # handle info request when logging
    if g.logging and g.GMC_getInfoFlag == 0:
        if extended : g.GMC_getInfoFlag = 2
        else:         g.GMC_getInfoFlag = 1

        while g.GMC_getInfoFlag > 0:
            time.sleep(0.01)

        setIndent(0)
        return g.GMC_DatetimeMsg

    else:
        # not logging or g.GMC_getInfoFlag >0
        # time check
        gmcinfo += getDeltaTimeMessage(*getGMC_DeltaTime(force=True))

        # read the cfg
        cfg, error, errmessage = getGMC_RawConfig()
        g.GMC_cfg = cfg
        vprintGMC_Config(defname, cfg)
        setGMC_Config4GL(cfg)

        # power state
        gmcinfo += tmp.format("Device Power State:", isGMC_PowerOn(getconfig=False, force=force))


    # critical settings
    if g.GMC_FETenabled:
        # FET enabled counter
        gmcinfo += "\n"
        gmcinfo += tmp.format("Critical Settings (see GeigerLog manual): ", "")

        gmcinfo += tmp.format("   FET (Fast Estimate Time):", "{} seconds".format(g.GMC_FastEstTime))
        if g.GMC_FastEstTime != 60:
            gmcinfo += tmp.format("   <red>CAUTION: anything different from 60 sec results in false data!","")
            gmcinfo += tmp.format("   <red>Correct in menu: Device -> GMC Series -> Set GMC Configuration.", "")

        if g.GMC_DeadTimeEnabled:
            # DeadTime enabled counter
            if cfgKeyHi["DEADTIME_ENABLE"][1] == 1:
                gmcinfo += tmp.format("   Dead Time Enabled State:", "On")
                gmcinfo += tmp.format("   <red>CAUTION: Dead Time Enablement may result in a distortion of data!","")
                gmcinfo += tmp.format("   <red>Correct in menu: Device -> GMC Series -> Set GMC Configuration.", "")
                gmcinfo += tmp.format("   <red>Switching to Off is recommended.","")
            else:
                gmcinfo += tmp.format("   Dead Time Enabled State:", "Off")

    dprint(defname, "GMC_ThreadMessages: '{}'".format(g.GMC_ThreadMessages))

    if extended:
        gmcinfo += "\n"
        gmcinfo += tmp.format("Extended Info:", "")

        # Speaker state
        gmcinfo += tmp.format("Device Speaker State:", isGMC_SpeakerOn())

        # Alarm state
        gmcinfo += tmp.format("Device Alarm State:", isGMC_AlarmOn())

        # Alarm level CPM
        if g.GMC_Model != "GMC-800":

            CPMAlarmType = "Unknown"
            try:
                AlarmCPM     = cfgKeyLo["AlarmCPMValue"][0]
                AlarmType    = cfgKeyLo["AlarmType"][0]
                CPMAlarmType = "Selected" if AlarmType == 0 else "NOT selected"
            except Exception as e:
                exceptPrint(e, "Alarm level CPM")
                AlarmCPM = g.NAN

            if AlarmCPM is not None:
                try:
                    gmcinfo += tmp.format("Device Alarm Level CPM:  ", "{:12s}: CPM:   {:<5.0f} (= µSv/h: {:5.3f})".format(CPMAlarmType, AlarmCPM, AlarmCPM / g.Sensitivity[0]))
                except Exception as e:
                    exceptPrint(e, defname + "Alarmlevel" )
                    rdprint(defname, "AlarmCPM: ", AlarmCPM)
                    rdprint(defname, "g.Sensitivity[0]: ", g.Sensitivity[0])
                    gmcinfo += tmp.format("Device Alarm Level CPM:  Undefined due to Exception")

            # Alarm level µSv/h
            uSvAlarmType = "Unknown"
            try:
                AlarmuSv     = cfgKeyLo["AlarmValueuSv"][0]
                ### ???
                AlarmuSv     = AlarmuSv if AlarmuSv is not None else g.NAN
                ###
                CPMAlarmType = "Selected" if AlarmType == 0 else "NOT selected"
                uSvAlarmType = "Selected" if AlarmType == 1 else "NOT selected"
            except Exception as e:
                exceptPrint(e, "Alarm level uSv")
                AlarmuSv = g.NAN
            gmcinfo += tmp.format("Device Alarm Level µSv/h:", "{:12s}: µSv/h: {:<5.3f} (= CPM:   {:<5.0f})".format(uSvAlarmType, AlarmuSv, AlarmuSv * g.Sensitivity[0]))

        else: # this is for GMC-800
            cfg, error, errmessage = getGMC_RawConfig()
            ndx = 121 + 4 # single byte options?
            alarmcpm = struct.unpack(">I",    cfg [ndx: ndx + 4])[0]
            gmcinfo += tmp.format("Device Alarm Level CPM:  ", alarmcpm)


        # Light state
        gmcinfo += tmp.format("Device Light State:", getLightStatus())


        # Save Data Type
        sdt, sdttxt = getGMC_HistSaveMode()
        gmcinfo += tmp.format("Device Hist. Saving Mode:", sdttxt)


        # get the current writing position in the History memory
        try:
            wpos = getGMC_HistWritePos()
        except Exception as e:
            exceptPrint(e, "Getting HistWritePosition")
        else:
            gmcinfo += tmp.format("Device Hist. Write position:", wpos)


        # MaxCPM
        value = cfgKeyLo["MaxCPM"][0]
        if value == 65535: value = 0
        # gmcinfo += tmp.format("Device Max CPM:", "{} (invalid if equal to 65535!)".format(value))
        gmcinfo += tmp.format("Device Max CPM:", "{}".format(value))


        # Battery Voltage
        rec, error, errmessage = getGMC_VOLT()
        if error < 0:   gmcinfo += tmp.format("Device Battery Voltage:", "{}"      .format(errmessage))
        else:           gmcinfo += tmp.format("Device Battery Voltage:", "{} Volt" .format(rec)       )


        # Battery Type
        gmcinfo += tmp.format("Device Battery Type Setting:", getGMC_BatteryType())


        # # temperature
        # # temperature is taken out of firmware.
        # # Apparently not valid at all in 500 series, not working in the 300 series
        # rec, error, errmessage = getGMC_TEMP()
        # if error < 0:
        #     gmcinfo += tmp.format("Device Temperature:", "'{}'" .format(errmessage))
        # else:
        #     edprint(defname + "rec: ", rec, type(rec))
        #     gmcinfo += tmp.format("Device Temperature:", "{} °C".format(rec))   # ONLY for GMC-320 ?


        # gyro
        rec, error, errmessage = getGMC_GYRO()
        if error < 0: gmcinfo += tmp.format("Device Gyro Data:", errmessage)
        else:         gmcinfo += tmp.format("Device Gyro Data:", rec)


        # Device History Saving Mode - Threshold
        try:
            ThM = cfgKeyLo["ThresholdMode"][0]
            if  ThM in (0, 1, 2):
                ThresholdMode = ("CPM", "µSv/h", "mR/h")
                gmcinfo += tmp.format("Device Hist. Threshold Mode:",   ThresholdMode[ThM])
                gmcinfo += tmp.format("Device Hist. Threshold CPM:",    cfgKeyLo["ThresholdCPM"][0] )
                gmcinfo += tmp.format("Device Hist. Threshold µSv/h:",  "{:0.3f}".format(cfgKeyLo["ThresholduSv"][0]))
            else:
                gmcinfo += tmp.format("Device Hist. Threshold Mode:",   "Unsupported on this device")
        except Exception as e:
            gmcinfo += tmp.format(str(e), "")


        # clock adjustment setting as done by counter itself
        msg = "Device Clock correction:"
        if    g.GMC_HasRTC_Offset: gmcinfo += "{:30s}{} sec\n".format(msg, str(cfgKeyHi["RTC_OFFSET"][1]))
        else:                      gmcinfo += "{:30s}{}\n"    .format(msg, "Unsupported on this device")


        # WiFi enabled counter
        if g.GMC_WiFiCapable:
            sfmt   = "{:30s}{}\n"
            skeys  = ("SSID", "Password", "Website", "URL", "UserID", "CounterID", "Period")

            # Web related High bytes in Config - as read out from device
            ghc    = "\nDevice Settings for GMCmap (currently active):\n"
            for key in skeys:
                keyval = cfgKeyHi[key][1]
                if key == "Password": keyval = "******"
                if keyval == "":      keyval = "<empty>"
                ghc += sfmt.format("   " + key, keyval)

            ghc += sfmt.format("   WiFi:",           isGMC_WifiOn())
            gmcinfo += tmp.format(ghc[:-1], "")

            # Web related High bytes in GL Config
            ghc    = "\nYour Configuration of GeigerLog for Counter's GMCmap Settings:\n"
            for key in skeys:
                keyval = cfgKeyHi[key][0]
                if key == "Password": keyval = "******"
                if keyval == "":      keyval = "<empty>"
                ghc += sfmt.format("   " + key, keyval)
            ghc += sfmt.format("   WiFi:", "ON" if cfgKeyHi[key][0] else "OFF")
            gmcinfo += tmp.format(ghc[:-1], "")
        else:
            gmcinfo += tmp.format("Device WiFi", "Unsupported on this device")


        # TARGET_HV enabled counter
        if g.GMC_TargetHVEnabled:
            try:    thv = str(cfgKeyHi["TARGET_HV"][1]) + " Volt"
            except: thv = g.NAN
            if g.GMC_Model == "GMC-800": thv = "Set to: " + str(cfg[72]) + " Units"
            gmcinfo += tmp.format("Device Anode Voltage:", "{}".format(thv))

            try:    thv = cfgKeyHi["HV_CALIB"][1]
            except: thv = g.NAN
            if g.GMC_Model == "GMC-800": gmcinfo += tmp.format("Device HV Calibration:", "Unsupported on this device")
            else:                        gmcinfo += tmp.format("Device HV Calibration:", "{}".format(thv))


        tmark = " #1" if g.GMC_DualTube else ""
        try:    thv = cfgKeyHi["DEADTIME_TUBE1"][1]
        except: thv = g.NAN
        if g.GMC_DeadTimeEnabled: gmcinfo += tmp.format("Device Deadtime Tube{}:".format(tmark), "{} µs".format(thv))
        else:                     gmcinfo += tmp.format("Device Deadtime Tube{}:".format(tmark), "Unsupported on this device")

        if g.GMC_DualTube:
            try:    thv = cfgKeyHi["DEADTIME_TUBE2"][1]
            except: thv = g.NAN
            gmcinfo += tmp.format("Device Deadtime Tube #2:", "{} µs".format(thv))


        # serial number of counter
        gmcinfo += "\n"
        gmcinfo += tmp.format("Device Serial Number:", "{}".format(getGMC_SerialNumber(g.GMC_usbport, g.GMC_baudrate)))


        # Calibration settings
        gmcinfo += tmp.format("\nDevice Calibration Points:", "        CPM  =    µSv/h   CPM / (µSv/h) µSv/h/CPM")
        try:
            if g.GMC_CountCalibPoints == 3:
                for i in range(0, 3):
                    calcpm = cfgKeyLo["CalibCPM_{}".format(i)][0]
                    calusv = cfgKeyLo["CalibuSv_{}".format(i)][0]
                    if calcpm is None: calcpm = g.NAN
                    if calusv is None: calusv = g.NAN
                    try:    calfac      = calcpm / calusv
                    except: calfac      = g.NAN
                    try:    invcalfac   = calusv / calcpm
                    except: invcalfac   = g.NAN
                    gmcinfo += tmp.format("   Calibration Point", "#{:}: {:6.0f}  = {:8.3f}       {:6.2f}     {:0.5f}".format(
                                                                    i + 1, calcpm, calusv, calfac, invcalfac))
            else:
                for i in range(0, 6):
                    calcpm = cfgKeyHi["Cal6CPM_{}".format(i)][1]
                    calusv = cfgKeyHi["Cal6uSv_{}".format(i)][1]
                    if calcpm is None: calcpm = g.NAN
                    if calusv is None: calusv = g.NAN
                    try:    calfac      = calcpm / calusv
                    except: calfac      = g.NAN
                    try:    invcalfac   = calusv / calcpm
                    except: invcalfac   = g.NAN
                    gmcinfo += tmp.format("   Calibration Point", "#{:}: {:6.0f}  = {:8.3f}       {:6.2f}     {:0.5f}".format(
                                                                    i + 1, calcpm, calusv, calfac, invcalfac))

        except Exception as e:
            exceptPrint(e, "Calibration Info")
            gmcinfo += "Failure getting Calibration Info from Counter!"


        # Firmware settings
        fmt = "   {:27s}{}\n"
        ghc = "\nYour Configuration of GeigerLog for Counter's Firmware:\n"
        ghc += fmt.format("Memory (bytes):",                "{:,}".format(g.GMC_memory))
        ghc += fmt.format("SPIRpage Size (bytes):",         "{:,}".format(g.GMC_SPIRpage))
        ghc += fmt.format("SPIRbugfix (True | False):",     "{:}" .format(g.GMC_SPIRbugfix))
        ghc += fmt.format("Config Size (bytes):",           "{:}" .format(g.GMC_configsize))
        ghc += fmt.format("Voltagebytes (1|5|None):",       "{:}" .format(g.GMC_voltagebytes))
        ghc += fmt.format("Endianness (big | little):",     "{:}" .format(g.GMC_endianness))
        ghc += fmt.format("Bytes in CP* records:",          "{:}" .format(g.GMC_Bytes))

        gmcinfo += ghc

    setIndent(0)
    return gmcinfo


#xyz
def doEraseSavedData():
    """Erase all data in History memory"""

    defname = "doEraseSavedData: "

    msg = QMessageBox()
    msg.setWindowIcon(g.iconGeigerLog)
    msg.setIcon(QMessageBox.Warning)
    msg.setWindowTitle("Erase Saved Data")
    msg.setText("All data saved into the counter's <b>History memory</b> will be erased. A recovery is not possible.<br><br>Please confirm with OK, or Cancel")
    msg.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
    msg.setDefaultButton(QMessageBox.Cancel)
    msg.setEscapeButton(QMessageBox.Cancel)
    retval = msg.exec()

    if retval == QMessageBox.Ok:    # QMessageBox.Ok == 1024
        # edprint("retval: ", retval)

        dprint(defname)
        setIndent(1)
        setBusyCursor()

        fprint(header("GMC Device Erase Saved History Data"))
        QtUpdate()

        setGMC_Config4GL(g.GMC_cfg)     #
        if isGMC_PowerOn() == "OFF":    # reads the config again
            power_was_on = False
        else:
            power_was_on = True
            fprint("Switching Power OFF")
            g.exgg.dbtnGMCPower.setIcon(QIcon(QPixmap(os.path.join(g.resDir, 'icon_power-round_off.png'))))
            QtUpdate()
            setGMC_POWEROFF()

        fprint("Begin Erasing")
        QtUpdate()

        rec, err, errmessage     = GMC_EraseMemBySPISE()        # ok to use
        # rec, err, errmessage     = GMC_EraseMemByFacRESET()   # not good! keep as reminder
        if err == 0 or err == 1:    fprint("Done Erasing")
        else:                       efprint("ERROR trying to Erase Saved Data: " + errmessage)
        QtUpdate()

        if power_was_on:
            fprint("Switching Power ON")
            g.exgg.dbtnGMCPower.setIcon(QIcon(QPixmap(os.path.join(g.resDir, 'icon_power-round_on.png'))))
            QtUpdate()
            setGMC_POWERON()

        setNormalCursor()
        setIndent(0)


def doREBOOT(force = False):
    """reboot the GMC device"""

    if force:
        retval = QMessageBox.Ok
    else:
        msg = QMessageBox()
        msg.setWindowIcon(g.iconGeigerLog)
        msg.setIcon(QMessageBox.Warning)
        msg.setWindowTitle("Reboot GMC Device")
        msg.setText("Rebooting your GMC device.\n\nPlease confirm with OK, or Cancel")
        msg.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
        msg.setDefaultButton(QMessageBox.Cancel)
        msg.setEscapeButton(QMessageBox.Cancel)
        retval = msg.exec()

    if retval == QMessageBox.Ok:
        fprint(header("GMC Device Reboot"))
        QtUpdate()
        rec, err, errmessage = setGMC_REBOOT()
        if err in (0, 1):    fprint("REBOOT completed")
        else:                fprint("ERROR in setGMC_REBOOT: " + errmessage)


def doFACTORYRESET(force = False):
    """Does a FACTORYRESET of the GMC device"""

    defname = "doFACTORYRESET: "

    d = QInputDialog()
    d.setWindowIcon(g.iconGeigerLog)
    warning ="""
<b>CAUTION</b> - You are about to reset the GMC device to factory<br>
condition! All data and your changes of settings will be lost.<br><br>
If you want to proceed, enter the word <b>RESET</b> (in all capital)<br>
and press OK"""

    if force: text, ok = ("RESET", True)
    else:     text, ok = d.getText(None, 'RESET', warning)

    vprint(defname, "Entered text: ", text, ",  ok: ", ok)
    if ok:
        fprint(header("GMC Device FACTORYRESET"))
        QtUpdate()

        if text == "RESET":
            setBusyCursor()
            rec, err, errmessage = setGMC_FACTORYRESET()
            if err in (0, 1): fprint("FACTORYRESET completed")
            else:             fprint("ERROR in setGMC_FACTORYRESET: " + errmessage)

            time.sleep(3.5)     # some is needed, but how long???

            cfg, _, _ = getGMC_RawConfig()
            setGMC_Config4GL(cfg)
            setNormalCursor()
        else:
            fprint("Entry '{}' not matching 'FACTORYRESET' - Reset NOT done".format(text))


def getResponseAT(command):
    """communication with the ESP8266 chip in the counter"""

    defname = "getResponseAT: "

    print()
    dprint(defname + "for command: {}".format(command))
    setIndent(1)

    rec = g.GMCser.write(command)  # rec = no of bytes written
    # print("bytes written: ", rec, "for command:", command)

    t0 = time.time()
    print("waiting for response ", end="", flush=True)
    while g.GMCser.in_waiting == 0:
        print(".", end="", flush=True)
        time.sleep(0.2)
    print(" received after {:0.1f} sec".format(time.time() - t0))    #  ca 5 sec

    rec = b''
    t0 = time.time()
    while g.GMCser.in_waiting > 0 or time.time() - t0 < 2:
        bw = g.GMCser.in_waiting
        if bw > 0:
            # print("reading {:3d} bytes".format(bw), end="  ")
            newrec = g.GMCser.read(bw)
            # print(newrec)
            rec += newrec
        else:
            print(".", end="", flush=True)
        time.sleep(0.2)
    print("\nfinal rec: ({} bytes) {}".format(len(rec), rec))

    setIndent(0)


def GMC_TESTING():
    """put here any testing code, which can be called from the Devel menu"""

    defname = "GMC_TESTING: "
    dprint(defname, "presently nothing is programmed in this function")


def vprintGMC_Config(msg, cfg):
    """prints the GMC memory config as Hex, Dec, ASCII to terminal"""

    defname = "vprintGMC_Config: "

    vprint(defname, " HEX    " + msg)
    for ncfg in BytesAsHex(cfg).split("\n"):       vprint(ncfg)

    vprint(defname, " DEC    " + msg)
    for ncfg in BytesAsDec(cfg).split("\n"):       vprint(ncfg)

    vprint(defname, " ASCII   " + msg)
    vprint(defname, " print 0xFF as F, other non-printable ASCII as Blank")
    for ncfg in BytesAsASCIIFF(cfg).split("\n"):   vprint(ncfg)

    # if g.devel:
    #     ac = "["
    #     for i, a in enumerate(cfg):
    #         if i % 20 == 0 and i > 0: ac += "\n "
    #         ac += "{:3d}, ".format(a)
    #     ac = ac[:-2] + "]"

    #     cdprint(defname, msg + " Python list for copy/paste of config\n", ac)

# ### not in use anywhere
# def cdprintGMC_Allcfg_keys():
#     """print Low und High keys with values"""

#     defname = "cdprintGMC_Allcfg_keys: "
#     cdprint(defname)

#     setIndent(1)
#     for key in cfgKeyLo:
#         cdprint("key: {:20s} : {}".format(key, cfgKeyLo[key][0]))

#     print()

#     for key in cfgKeyHi:
#         cdprint("key: {:20s} : {}".format(key, cfgKeyHi[key][1]))

#     setIndent(0)


def getGMC_HistWritePos():
    """Get the Write Position in the History memory"""

    defname = "getGMC_HistWritePos: "

    dprint(defname)
    setIndent(1)

    RequestLength = 4
    rec, error, errmessage = serialGMC_COMM(b'<GetSPISA>>', RequestLength, orig(__file__))
    writepos = (rec[0] << 16) | rec[1] << 8 | rec[2]        # rec[3] is always 0xaa, i.e. 3 valid bytes remain

    dprint(defname + "GetSPISA: ReqLen={}  rcvd: rec={}  err={}  errmessage='{}'" .format(RequestLength, rec, error, errmessage))
    dprint(defname + "GetSPISA: Write position: @Byte #{} (@{:0.3%} of memory)"   .format(writepos, writepos / g.GMC_memory))

    setIndent(0)

    return "Byte #{} ({:0.3%} of memory)".format(writepos, writepos / g.GMC_memory)


#PPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPP
#PPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPP
#PPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPP

def getGMC_DeviceProperties():
    """define a device and its parameters"""

    # NOTE: this def does NOT make any call to the device!

    # GETVER                    Model               nominal (observed)
    # GMC-300Re 2.39,           GMC-300             2.xx    (2.39)
    # GMC-300Re 3.xx,           GMC-300             3.xx    (3.20)
    # GMC-300Re 4.xx,           GMC-300E+           4.xx    (4.20, 4.22, 4.54)

    # GMC-320Re 4.xx,           GMC-320+            4.xx    (4.19)
    # GMC-320Re 5.xx,           GMC-320+V5 (WiFi)   5.xx
    # GMC-320+V5\x00RRe 5.73,   GMC-320+V5 (WiFi)   5.xx    (5.73)              from Tom Johnson's new GMC-320

    # GMC-500Re 1.xx,           GMC-500 and 500+    1.xx    (1.00, 1.08)

    # GMC-500+Re 1.xx,          GMC-500+            1.??    (1.18(bug), 1.21, 1.22)
    # GMC-500+Re 2.xx,          GMC-500+            2.??
    # GMC-500+Re 2.40,          GMC-500+            2.40    2.40                with new 2nd tube

    # GMC-600Re 1.xx,           GMC-600 and 600+    1.xx    2.26
    # GMC-600Re 2.4x,           GMC-600+            2.42    2.41, 2.42, 2.45, 2.46 (since July 23)

    # GMC-800Re1.08,            GMC-800             1.08    1.08

    # FET (FastEstTime): on 300S, 800, 500+ series: 5, 10, 15, 20, 30, 60=sec, 3=dynamic (firmware >= 2.28)
    #                  : on 300, 320 series not defined



    ## local ###################################################
    def showUnknownDeviceMsg(DeviceName, DModel, DFirmware):
        """call if any 'last resort' config had been reached"""

        defname = "showUnknownDeviceMsg: "

        msg = "<b>ATTENTION</b> A GMC device '{}' was detected, but of a so far unknown model / firmware! (Model: {} Firmware: {})".format(DeviceName, DModel, DFirmware)
        edprint(defname + msg, debug=True)
        efprint(msg)
        qefprint("Review the 'Extended Info' for this GMC device. You may have to edit the")
        qefprint("configuration file <b>geigerlog.cfg</b> to adapt the settings to this new device.")
    ## end local ###############################################

    defname = "getGMC_DeviceProperties: "
    dprint(defname)
    setIndent(1)


    #
    # default settings
    #
    GMC_locationBug             = "GMC-500+Re 1.18, GMC-500+Re 1.21"
    GMC_sensitivityDef          = 154                                   # CPM/(µSv/h) - all counters except GMC600, GMC-300S, GMC-320S
    GMC_sensitivity1st          = 154                                   # CPM/(µSv/h) - all counters except GMC600, GMC-300S, GMC-320S
    GMC_DualTube                = False                                 # all are single tube, except 1) 500+ and 2) 500(without +) owned by the_Mike
    GMC_FETenabled              = False                                 # 500 and 600 counter are enabled, and now also 300S counter
                                                                        # GMC-320Re 4.19 : kein Fast Estimate Time
    GMC_DeadTimeEnabled         = False                                 # from Firmware 2.41 onwards the DeadTime "Feature" is present
    GMC_CfgHiIndex              = 2                                     # column index; 2 for only-low-config
    GMC_WiFiCapable             = False                                 # does counter have WiFi
    GMC_TargetHVEnabled         = False                                 # ability to read and set HV
    GMC_Variables               = "CPM1st, CPS1st"                      # all counters except GMC-500 with 2 tubes
    GMC_HasGyroCommand          = False                                 # supports the command GETGYRO
    GMC_HasRTC_Offset           = False                                 # EmfDef: From 1.04 for the S versions and 4.71 for the regular versions.
    GMC_RTC_Offset              = +1                                    # correct 1 sec per hour as default; value is from -59 -> 59 seconds
    GMC_CountCalibPoints        = 3                                     # Number of Calibration Points; Default=3, GMC-800 => 6
    GMC_savedatatypes           = savedatatypes                         # saving every sec, min,h - thresholds eliminated in GMC3002, GMC-800

    GMC_DevDet                  = g.GMC_DeviceDetected.split("Re")       # g.GMC_DeviceDetected is set in function "getGMC_Version()"
    GMC_Model                   = GMC_DevDet[0].strip()
    try:    GMC_FWVersion       = float(GMC_DevDet[1].strip())
    except: GMC_FWVersion       = 0.0
    # rdprint(defname, "GMC_DeviceDetected: >{}<   GMC_Model: >{}<   GMC_FWVersion: >{}< (type: {})".format(g.GMC_DeviceDetected, GMC_Model, GMC_FWVersion, type(GMC_FWVersion)))


# 300
    if GMC_Model == "GMC-300":
        # My counter: "GMC-300Eplus", read-out: >GMC-300Re 4.54<
        # Measuring clock drift: "-19.9 sec/day" --> counter is faster than computer by 19.9 sec in 1 day
        # EmfDef: GMC_HasRTC_Offset = True:  From 1.04 for the S versions and 4.71 for the regular versions.
        GMC_memory               = 2**16
        GMC_SPIRpage             = 2048
        GMC_SPIRbugfix           = False
        GMC_configsize           = 256
        GMC_voltagebytes         = 1
        GMC_endianness           = "little"
        GMC_Bytes                = 2
        GMC_savedatatypes        = GMC_savedatatypes[0:4]

        if 1 <= GMC_FWVersion < 3:
            # "GMC-300Re 2.39" is used by user ori0n; ok with "GMC-300"
            # see:  http://www.gqelectronicsllc.com/forum/topic.asp?TOPIC_ID=9893
            #
            # various aspects not yet determined!!!
            # errors from:      <GETDATETIME>>
            #                   <GETGYRO>>
            # not working:      reboot              # confirmed in GQ-RFC1201 - Ver 1.40 Jan-2015
            #                   factoryreset        # confirmed in GQ-RFC1201 - Ver 1.40 Jan-2015
            # sensitivity:      200 CPM / (µSv/h) (setting: 0.005 µSv/h/CPM)
            # tube:             ?
            # Device Battery Voltage:       10.0 Volt   # had 9V rechargeable (Block Batterie Akku)
            # Device Battery Type Setting:  24          # why?
            pass

        elif 3 <= GMC_FWVersion < 4:
            # the "GMC-300" delivers the requested SPIR page after ANDing with 0x0fff,
            # hence when you request 4k (=1000hex) you get zero; therefore use pagesize 2k only
            pass

        elif 4 <= GMC_FWVersion < 4.71:                     # known versions: 4.54
            # When using a SPIR page of 4k, you need the datalength workaround in
            # gcommand, i.e. asking for 1 byte less.
            # When writing config data into the unused portion of the memory, the
            # counter seems to delete the changes after ~1 sec
            GMC_SPIRpage             = 4096
            GMC_SPIRbugfix           = True

        elif 4.71 <= GMC_FWVersion:
            # when using a page of 4k, you need the datalength workaround in
            # gcommand, i.e. asking for 1 byte less
            # when writing config data into the unused portion of the memory, the
            # counter seems to delete the changes after ~1 sec
            GMC_SPIRpage             = 4096
            GMC_SPIRbugfix           = True
            GMC_HasRTC_Offset        = True

        else:
            # last resort for "GMC-300" counters
            showUnknownDeviceMsg(g.GMC_DeviceDetected, GMC_Model, GMC_FWVersion)
            GMC_SPIRpage             = 4096
            GMC_SPIRbugfix           = True
            GMC_HasRTC_Offset        = True


# 300S "SSSSSSSSS !!!"
    elif GMC_Model == "GMC-300S":
        # My counter: >GMC-300SRe 1.03<
        # Measuring clock drift: "-20.6 sec/day" --> counter is faster than computer by 20.6 sec in 1 day
        # EmfDef: GMC_HasRTC_Offset = True:  From 1.04 for the S versions and 4.71 for the regular versions.
        GMC_memory               = 2**16
        GMC_SPIRpage             = 4096
        GMC_SPIRbugfix           = True
        GMC_configsize           = 256
        GMC_voltagebytes         = 1
        GMC_endianness           = "little"
        GMC_Bytes                = 2
        GMC_FETenabled           = True
        GMC_CfgHiIndex           = 6
        GMC_sensitivityDef       = 161.54
        GMC_sensitivity1st       = 161.54
        GMC_HasGyroCommand       = False                        # supports the command GETGYRO: it does
                                                                # but the command returns no meaningful data
        GMC_savedatatypes        = GMC_savedatatypes[0:4]

        if 1 <= GMC_FWVersion < 1.04:                           # known versions: 1.03
            # "GMC-300SRe 1.03" as of 2023-02-23
            GMC_HasRTC_Offset    = False

        elif 1.04 <= GMC_FWVersion:                             # or any higher version
            GMC_HasRTC_Offset    = True

        else: # so far no devices
            GMC_HasRTC_Offset    = True
            showUnknownDeviceMsg(g.GMC_DeviceDetected, GMC_Model, GMC_FWVersion)

# 320
    elif GMC_Model == "GMC-320":
        # EmfDef: GMC_HasRTC_Offset = True:  From 1.04 for the S versions and 4.71 for the regular versions.
        GMC_memory               = 2**20
        GMC_SPIRpage             = 4096
        GMC_SPIRbugfix           = False
        GMC_configsize           = 256
        GMC_voltagebytes         = 1
        GMC_endianness           = "little"
        GMC_Bytes                = 2
        GMC_HasGyroCommand       = True                         # supports the command GETGYRO

        if 3.0 <= GMC_FWVersion < 4:                            # known versions: 3.01
            pass

        elif 4 <= GMC_FWVersion < 4.71:                         # known versions: 4.19, 4.27 (latest as of 2024-03-04, see forum 10184, Reply#22)
            GMC_SPIRbugfix           = True

        elif 4.71 <= GMC_FWVersion:
            GMC_SPIRbugfix           = True
            GMC_HasRTC_Offset        = True

        else:
            # no devices known
            showUnknownDeviceMsg(g.GMC_DeviceDetected, GMC_Model, GMC_FWVersion)
            GMC_SPIRbugfix           = True
            GMC_HasRTC_Offset        = True

# 320V5
    elif GMC_Model == "GMC-320+V5":     # Model with WiFi
        # EmfDef: GMC_HasRTC_Offset = True:  From 1.04 for the S versions and 4.71 for the regular versions.
        GMC_memory               = 2**20
        GMC_SPIRpage             = 4096
        GMC_SPIRbugfix           = True
        GMC_configsize           = 256
        GMC_voltagebytes         = 1
        GMC_endianness           = "little"
        GMC_Bytes                = 2
        GMC_CfgHiIndex           = 3
        GMC_HasGyroCommand       = True                 # supports the command GETGYRO
        GMC_WiFiCapable          = True
        GMC_HasRTC_Offset        = True

        if 5.0 <= GMC_FWVersion:                        # known versions: 5.73
            # NOTE: the NULL within string !!!
            # "b'GMC-320+V5\x00RRe 5.73'"  # from Tom Johnson's new GMC-320
            # see: https://sourceforge.net/p/geigerlog/discussion/general/thread/d3c228ff79/
            pass

        else:
            # no devices known
            showUnknownDeviceMsg(g.GMC_DeviceDetected, GMC_Model, GMC_FWVersion)


# 320S "SSSSSSSSSS !!!!!!!!"
    elif GMC_Model == "GMC-320S":
        # EmfDef: GMC_HasRTC_Offset = True:  From 1.04 for the S versions and 4.71 for the regular versions.
        GMC_memory               = 2**16
        GMC_SPIRpage             = 4096
        GMC_SPIRbugfix           = True
        GMC_configsize           = 256
        GMC_voltagebytes         = 1
        GMC_endianness           = "little"
        GMC_Bytes                = 2
        GMC_FETenabled           = True
        GMC_CfgHiIndex           = 6
        GMC_sensitivityDef       = 161.54
        GMC_sensitivity1st       = 161.54
        GMC_HasGyroCommand       = True                     # supports the command GETGYRO
        GMC_savedatatypes        = GMC_savedatatypes[0:4]

        # rdprint(defname, "GMC_FWVersion: ", GMC_FWVersion)
        if 1.0 <= GMC_FWVersion < 1.04:                        # known versions:    1.03
            # "GMC-320SRe 1.03" as of 2023-02-23; verified by user Ted Sled
            pass

        elif 1.04 <= GMC_FWVersion:                            # or any higher version
            GMC_HasRTC_Offset = True

        else: # so far no devices
            showUnknownDeviceMsg(g.GMC_DeviceDetected, GMC_Model, GMC_FWVersion)
            GMC_HasRTC_Offset = True


# 500 OHNE "PLUS" !!!
    elif GMC_Model == "GMC-500":
        # EmfDef: GMC_HasRTC_Offset = True:  From 1.04 for the S versions and 4.71 for the regular versions.
        GMC_memory               = 2**20
        GMC_SPIRpage             = 2048   # ist bug jetzt behoben oder auf altem Stand? erstmal auf 2048 bytes
        GMC_SPIRbugfix           = False
        GMC_configsize           = 512
        GMC_voltagebytes         = 5
        GMC_endianness           = "big"
        GMC_Variables            = "CPM1st, CPS1st, CPM2nd, CPS2nd"
        GMC_Bytes                = 2
        GMC_DualTube             = True
        GMC_sensitivity2nd       = 2.08                         # only GMC 500 with 2 tubes
        GMC_CfgHiIndex           = 4                            # 500er, 600er
        GMC_HasGyroCommand       = True                         # supports the command GETGYRO
        GMC_WiFiCapable          = True

        if 1.0 <= GMC_FWVersion <= 1.08:                        # known versions: 1.08 (only existing version?)
            # GMC-500Re 1.08 : No '+' but 2 tubes, kein Fast Estimate Time (von user the_mike)
            pass

        elif 1.08 < GMC_FWVersion <= 1.40:                      # known versions: 1.40 at user Mike
            pass

        else: # so far no other devices
            showUnknownDeviceMsg(g.GMC_DeviceDetected, GMC_Model, GMC_FWVersion)


# 500 MIT "PLUS" !!!
    elif GMC_Model == "GMC-500+":
        # EmfDef: GMC_HasRTC_Offset = True:  From 1.04 for the S versions and 4.71 for the regular versions.
        # 2nd tube in new, undeclared version:
        # "EmfDev: The name of the tube is J707. It is similar to SI-3BG."
        # see: http://www.gqelectronicsllc.com/forum/topic.asp?TOPIC_ID=10358, Reply #2
        # see: https://www.alibaba.com/product-detail/J707-Geiger-tube-nuclear-radiation-detector_1600885257039.html
        #
        # SPIR download timing data:  see 'gsub_config'  @GMC_Device GMC_SPIRpage
        # from Firmware 2.41 onwards the DeadTime "Feature" is present
        GMC_memory               = 2**20
        GMC_SPIRpage             = 4096
        GMC_SPIRbugfix           = False
        GMC_configsize           = 512
        GMC_voltagebytes         = 5
        GMC_endianness           = "big"
        GMC_Variables            = "CPM1st, CPS1st, CPM2nd, CPS2nd"
        GMC_Bytes                = 4                                        # Yields 4 bytes on all CPx calls!
        GMC_DualTube             = True                                     # 500+ with 2 tubes
        GMC_sensitivity2nd       = 2.08                                     # only GMC 500 with 2 tubes
        GMC_CfgHiIndex           = 4                                        # 500er, 600er
        GMC_HasGyroCommand       = True                                     # supports the command GETGYRO
        GMC_WiFiCapable          = True

        if 1.0 <= GMC_FWVersion < 1.2:                        # known versions:    1.18 (only known one)
            # Has a firmware bug: on first call to GETVER gets nothing returned.
            # WORK AROUND: must cycle connection ON->OFF->ON. then ok
            GMC_SPIRpage             = 2048   # ist bug jetzt behoben oder auf altem Stand??? erstmal auf 2048 bytes

        elif 1.2 <= GMC_FWVersion < 2:                        # known versions: 1.21, 1.22
            # Firmware bug from 'GMC-500+Re 1.18' is corrected
            # original found in: GMC-500+Re 1.2.
            # Calibration points read out from firmware:
            # Calibration Points:     CPM  =  µSv/h   CPM / (µSv/h)   µSv/h / CPM
            # Calibration Point 1:    100  =   0.65       153.8          0.0065
            # Calibration Point 2:  30000  = 195.00       153.8          0.0065
            # Calibration Point 3:     25  =   4.85         5.2          0.1940
            pass

        elif 2 <= GMC_FWVersion < 2.4:                            # known versions: 2.24, 2.28, 2.29
            # GMC-500+Re 2.28   latest as of 2021-10-20
            # GMC-500+Re 2.29   latest as of 2022-06-22 http://www.gqelectronicsllc.com/forum/topic.asp?TOPIC_ID=9910
            GMC_CfgHiIndex            = 5

        elif 2.40 <= GMC_FWVersion < 2.41:                        # known versions: 2.40
            # GMC-500+Re 2.40 as of 2022-10-18 as reported by Quaxo76, see:
            # http://www.gqelectronicsllc.com/forum/topic.asp?TOPIC_ID=9910, Reply #5
            # Calibration points read out from firmware:
            # Device Calibration Points:        CPM  =   µSv/h   CPM / (µSv/h)      µSv/h/CPM
            # Calibration Point          #1:    100  =   0.650       153.85          0.00650
            # Calibration Point          #2:  30000  = 195.000       153.85          0.00650
            # Calibration Point          #3:   1000  =  46.800        21.37          0.04680
            GMC_sensitivity2nd       = 21.4     # unknown tube, wrapped completely in black plastic
            GMC_CfgHiIndex           = 5
            GMC_FETenabled           = True

        elif 2.41 <= GMC_FWVersion < 2.44:                        # known versions: 2.41
            # GMC-500+Re 2.41   see: http://www.gqelectronicsllc.com/forum/topic.asp?TOPIC_ID=10007
            GMC_sensitivity2nd       = 21.4   # unknown tube, wrapped completely in black plastic
            GMC_CfgHiIndex           = 5
            GMC_FETenabled           = True
            GMC_DeadTimeEnabled      = True   # at least in fw 2.41 and later, see forum topic 10080

        elif 2.44 <= GMC_FWVersion:                                # known versions: 2.52
            # see: http://www.gqelectronicsllc.com/forum/topic.asp?TOPIC_ID=10437
            # Reply #5: EmfDev: "6 point calibration is added with 2.44 rev."
            GMC_sensitivity2nd       = 21.4   # unknown tube, wrapped completely in black plastic
            GMC_CfgHiIndex           = 6
            GMC_FETenabled           = True
            GMC_DeadTimeEnabled      = True   # at least in fw 2.41 and later, see forum topic 10080

        else:
            # last resort for GMC-500plus anything
            showUnknownDeviceMsg(g.GMC_DeviceDetected, GMC_Model, GMC_FWVersion)
            GMC_sensitivity2nd       = 21.4   # unknown tube, wrapped completely in black plastic
            GMC_CfgHiIndex           = 5
            GMC_FETenabled           = True
            GMC_DeadTimeEnabled      = True   # at least in fw 2.41 and later, see forum topic 10080
            GMC_HasRTC_Offset        = True
            GMC_CountCalibPoints     = 6      # from fw 2.44 onwards


# 510
    elif GMC_Model == "GMC-510+":
        # EmfDef: GMC_HasRTC_Offset = True:  From 1.04 for the S versions and 4.71 for the regular versions.
        GMC_memory               = 2**20
        GMC_SPIRpage             = 2048   # ist bug jetzt behoben oder auf altem Stand?; erstmal auf 2048 bytes
        GMC_SPIRbugfix           = False
        GMC_configsize           = 512
        GMC_voltagebytes         = 1                                # strange but working
        GMC_endianness           = "big"
        GMC_Bytes                = 4
        GMC_CfgHiIndex           = 4                                # 500er, 600er
        GMC_HasGyroCommand       = True                             # supports the command GETGYRO
        GMC_WiFiCapable          = True

        if 1.0 <= GMC_FWVersion < 4.71:                             # known versions:    1.04
            # reported by dishemesdr: https://sourceforge.net/p/geigerlog/discussion/general/thread/48ffc25514/
            # Connected Device: GMC-510Re 1.04
            # tube: single tube M4011   https://www.gqelectronicsllc.com/support/GMC_Selection_Guide.htm
            pass
        else:
            # no other version known
            showUnknownDeviceMsg(g.GMC_DeviceDetected, GMC_Model, GMC_FWVersion)
            GMC_HasRTC_Offset        = True
            pass


# 600
    elif GMC_Model == "GMC-600+":
        # see: http://www.gqelectronicsllc.com/forum/topic.asp?TOPIC_ID=10437
        # Reply #3 by Ihab17:
        # GMC 600+ in version 2.52 has 6 calibration points (seen from the counter)
        # 003541 CPM, 10 uSv/h      --> 354.1   CPM / (µSv/h)
        # 031870 CPM, 100 uSv/h     --> 318.7
        # 112584 CPM, 500 uSv/h     --> 225.168
        # 183243 CPM, 1000 uSv/h    --> 183.243
        # 228730 CPM, 2000 uSv/h    --> 114.365
        # 282307 CPM, 5000 uSv/h    -->  56.461
        #
        # EmfDef: GMC_HasRTC_Offset = True:  From 1.04 for the S versions and 4.71 for the regular versions.
        # sensitivity: using LND's 348, not GQ's 379; see note in ceigerlog.cfg for tube LND-7317info
        # see: http://www.gqelectronicsllc.com/forum/topic.asp?TOPIC_ID=9961
        # see: http://www.gqelectronicsllc.com/forum/topic.asp?TOPIC_ID=10080
        # firmware version 2.41 may have been the first to have deadtime enabled, see forum topic 10080
        GMC_memory               = 2**20
        GMC_SPIRpage             = 4096
        GMC_SPIRbugfix           = False
        GMC_configsize           = 512
        GMC_sensitivityDef       = 348                      # CPM/(µSv/h)
        GMC_sensitivity1st       = 348                      # CPM/(µSv/h)
        GMC_voltagebytes         = 5
        GMC_endianness           = "big"
        GMC_Bytes                = 4
        GMC_CfgHiIndex           = 5                        # 500er, 600er
        GMC_FETenabled           = True
        GMC_HasGyroCommand       = True                     # supports the command GETGYRO
        GMC_WiFiCapable          = True

        if 1.0 <= GMC_FWVersion < 2.4:                      # known versions: 2.22, 2.26
            # 600+ version: 2.22 is version from Ihab's 1st counter
            # 600+ version: 2.26 from user "1967"
            GMC_SPIRpage             = 2048
            GMC_Bytes                = 2
            GMC_CfgHiIndex           = 4                    # first versions????

        elif 2.4 <= GMC_FWVersion < 2.44:                   # known versions: 2.41
            GMC_TargetHVEnabled      = True                 # allows to measure and set anode voltage (??? in v 2.40???)
            GMC_DeadTimeEnabled      = True                 # at least in fw 2.41 and later, see forum topic 10080

        elif 2.44 <= GMC_FWVersion:                         # known versions: 2.47, 2.52
            # Bobackman, 11.2.2024: forum-topic: 10184: latest firmware revision for the GMC 600+? Currently I am at 2.47.
            # Ihab17,    12.2.2024: forum-topic: 10184: I have just updated my device to the latest FW version 2.52 -->Reply#18
            # Ihab17,    23.4.2024: forum-topic: 10437: GMC 600+ Rev 2.52 has 6 calibration points (seen from the counter)
            # EmfDEv,    23.4.2024: forum-topic: 10437: For 500/600/+: 6 point calibration is added with 2.44 rev.
            GMC_TargetHVEnabled      = True                 # allows to measure and set anode voltage
            GMC_DeadTimeEnabled      = True                 # at least in fw 2.41 and later, see forum topic 10080
            GMC_CountCalibPoints     = 6                    # from 2.44 onwards
            GMC_CfgHiIndex           = 8                    # from 2.44 onwards

        else:
            # last resort for GMC-600 anything
            showUnknownDeviceMsg(g.GMC_DeviceDetected, GMC_Model, GMC_FWVersion)
            GMC_HasRTC_Offset        = False                # just guessing
            GMC_DeadTimeEnabled      = True                 # at least in fw 2.41 and later, see forum topic 10080
            GMC_TargetHVEnabled      = True                 # allows to measure and set anode voltage
            GMC_CountCalibPoints     = 6                    # from 2.44 onwards
            GMC_CfgHiIndex           = 8                    # from 2.44 onwards


# 800
    elif GMC_Model.startswith("GMC-800"):
        # EmfDef: GMC_HasRTC_Offset = True:  From 1.04 for the S versions and 4.71 for the regular versions.
        # NOTE: cfg data from user MaoBra suggest is does NOT have GMC_HasRTC_Offset = True ????
        # based on reports from MaoBra, see:
        # https://sourceforge.net/p/geigerlog/discussion/devel/thread/bb09f83308/?limit=25#3810
        # device has 6 calibration points, each one coding exact same Sensitivity= 153.8 CPM / (mſv/h)
        #                                       Sensitivity CPM / (µSv/h)
        # -1	CPM	1538	microSv/h	10	    153.8
        # -2	CPM	15380	microSv/h	100	    153.8
        # -3	CPM	30760	microSv/h	200	    153.8
        # -4	CPM	76900	microSv/h	500	    153.8
        # -5	CPM	153800	microSv/h	1000	153.8
        # -6	CPM	307600	microSv/h	2000	153.8

        GMC_memory               = 2**21                # 2 MB
        GMC_SPIRpage             = 4096
        GMC_SPIRbugfix           = False
        GMC_configsize           = 512
        GMC_sensitivityDef       = 154                  # CPM/(µSv/h)
        GMC_sensitivity1st       = 154                  # CPM/(µSv/h)
        GMC_voltagebytes         = None
        GMC_endianness           = "big"
        GMC_Bytes                = 4
        GMC_CfgHiIndex           = 7                    # no WiFi but FET, and new calibs
        GMC_FETenabled           = True
        GMC_HasGyroCommand       = False                # does NOT support the command GETGYRO
        GMC_CountCalibPoints     = 6
        GMC_savedatatypes        = GMC_savedatatypes[0:4]
        GMC_HasRTC_Offset        = False                # based on reports from MaoBra, see above
        GMC_DeadTimeEnabled      = False
        GMC_TargetHVEnabled      = True                 # allows to measure and set anode voltage

        if 1.0 <= GMC_FWVersion:                        # known versions:  1.08, 1.09 (forum 10370 #2,#3)
            pass
        else:
            # last resort for GMC-800 anything
            showUnknownDeviceMsg(g.GMC_DeviceDetected, GMC_Model, GMC_FWVersion)
            pass


# last resort
    else:
        # The very last resort:  If none of the above match, then this place will be reached.
        # Allows integrating unknown new (and also old) devices
        showUnknownDeviceMsg(g.GMC_DeviceDetected, GMC_Model, GMC_FWVersion)

        GMC_memory               = 2**20            # 1 MByte
        GMC_SPIRpage             = 2048             # should be safe
        GMC_SPIRbugfix           = False            # should be safe at 2048
        GMC_configsize           = 512              # like in 320, 500, 600 series
        GMC_voltagebytes         = 5                # like in 500 series
        GMC_endianness           = "big"            # like in 500 series
        GMC_Bytes                = 4                # like in 500 series
        GMC_CfgHiIndex           = 7                # like any newer series
        GMC_FETenabled           = False            # what to chose?
        GMC_DeadTimeEnabled      = False            # what to chose?
        GMC_TargetHVEnabled      = False            # what to chose?
        GMC_HasGyroCommand       = False            # what to chose? does NOT support the command GETGYRO
        GMC_WiFiCapable          = False            # ???
        GMC_HasRTC_Offset        = False            # ???



    # overwrite any "auto" values with defaults
    if g.GMC_memory             == "auto" : g.GMC_memory           = GMC_memory
    if g.GMC_SPIRpage           == "auto" : g.GMC_SPIRpage         = GMC_SPIRpage
    if g.GMC_SPIRbugfix         == "auto" : g.GMC_SPIRbugfix       = GMC_SPIRbugfix
    if g.GMC_configsize         == "auto" : g.GMC_configsize       = GMC_configsize
    if g.GMC_voltagebytes       == "auto" : g.GMC_voltagebytes     = GMC_voltagebytes
    if g.GMC_endianness         == "auto" : g.GMC_endianness       = GMC_endianness
    if g.GMC_Bytes              == "auto" : g.GMC_Bytes            = GMC_Bytes
    if g.GMC_locationBug        == "auto" : g.GMC_locationBug      = GMC_locationBug
    if g.GMC_WiFiCapable        == "auto" : g.GMC_WiFiCapable      = GMC_WiFiCapable
    if g.GMC_CfgHiIndex         == "auto" : g.GMC_CfgHiIndex       = GMC_CfgHiIndex
    if g.GMC_DualTube           == "auto" : g.GMC_DualTube         = GMC_DualTube
    if g.GMC_FETenabled         == "auto" : g.GMC_FETenabled       = GMC_FETenabled
    if g.GMC_DeadTimeEnabled    == "auto" : g.GMC_DeadTimeEnabled  = GMC_DeadTimeEnabled
    if g.GMC_TargetHVEnabled    == "auto" : g.GMC_TargetHVEnabled  = GMC_TargetHVEnabled
    if g.GMC_HasGyroCommand     == "auto" : g.GMC_HasGyroCommand   = GMC_HasGyroCommand
    if g.GMC_CountCalibPoints   == "auto" : g.GMC_CountCalibPoints = GMC_CountCalibPoints
    if g.GMC_savedatatypes      == "auto" : g.GMC_savedatatypes    = GMC_savedatatypes
    if g.GMC_HasRTC_Offset      == "auto" : g.GMC_HasRTC_Offset    = GMC_HasRTC_Offset
    if g.GMC_RTC_Offset         == "auto" : g.GMC_RTC_Offset       = GMC_RTC_Offset
    if g.GMC_Variables          == "auto" : g.GMC_Variables        = GMC_Variables

    # tube settings
    if g.Sensitivity[0]         == "auto":
        if g.TubeSensitivity[0] == "auto":  g.Sensitivity[0]       = GMC_sensitivityDef
        else:                               g.Sensitivity[0]       = g.TubeSensitivity[0]

    if g.Sensitivity[1]         == "auto":
        if g.TubeSensitivity[1] == "auto":  g.Sensitivity[1]       = GMC_sensitivity1st
        else:                               g.Sensitivity[1]       = g.TubeSensitivity[1]

    if GMC_DualTube:
        if g.Sensitivity[2]     == "auto":
            if g.TubeSensitivity[2] == "auto":  g.Sensitivity[2]   = GMC_sensitivity2nd
            else:                               g.Sensitivity[2]   = g.TubeSensitivity[2]


    # clean up locationBug to avoid crash due to any wrong user entry; on Exception resort to default setting
    try:    ts = g.GMC_locationBug.split(",")           # user entered
    except: ts =   GMC_locationBug.split(",")           # default
    for i in range(0, len(ts)): ts[i] = ts[i].strip()   # cleanup
    g.GMC_locationBug = ts                              # is list like: ['GMC-500+Re 1.18', 'GMC-500+Re 1.21']

    g.GMC_Model              = GMC_Model                # Model Name like 'GMC-500+'; extracted from g.GMC_DeviceDetected
    g.GMC_FWVersion          = GMC_FWVersion            # Firmware Version like '1.18'; extracted from g.GMC_DeviceDetected

    dpformat = defname + "  {:20s} : {}"
    dprint(dpformat.format("Detected device",       g.GMC_DeviceDetected))
    dprint(dpformat.format("--> Model",             g.GMC_Model))
    dprint(dpformat.format("--> Firmware Version",  g.GMC_FWVersion))
    dprint(dpformat.format("GMC_DualTube",          g.GMC_DualTube))
    dprint(dpformat.format("GMC_configsize",        g.GMC_configsize))
    dprint(dpformat.format("GMC_memory",            g.GMC_memory))
    dprint(dpformat.format("GMC_SPIRpage",          g.GMC_SPIRpage))
    dprint(dpformat.format("GMC_SPIRbugfix",        g.GMC_SPIRbugfix))
    dprint(dpformat.format("GMC_voltagebytes",      g.GMC_voltagebytes))
    dprint(dpformat.format("GMC_HasGyroCommand",    g.GMC_HasGyroCommand))
    dprint(dpformat.format("GMC_Bytes",             g.GMC_Bytes))
    dprint(dpformat.format("GMC_endianness",        g.GMC_endianness))
    dprint(dpformat.format("GMC_locationBug",       g.GMC_locationBug))
    dprint(dpformat.format("GMC_WiFiCapable",       g.GMC_WiFiCapable))
    dprint(dpformat.format("GMC_CfgHiIndex",        g.GMC_CfgHiIndex))
    dprint(dpformat.format("GMC_FETenabled",        g.GMC_FETenabled))
    dprint(dpformat.format("GMC_HasRTC_Offset",     g.GMC_HasRTC_Offset))
    dprint(dpformat.format("GMC_RTC_Offset",        g.GMC_RTC_Offset))
    dprint(dpformat.format("GMC_DeadTimeEnabled",   g.GMC_DeadTimeEnabled))
    dprint(dpformat.format("GMC_TargetHVEnabled",   g.GMC_TargetHVEnabled))
    dprint(dpformat.format("GMC_CountCalibPoints",  g.GMC_CountCalibPoints))
    dprint(dpformat.format("GMC_savedatatypes",     g.GMC_savedatatypes))
    dprint(dpformat.format("GMC_Variables",         g.GMC_Variables))

    dprint(dpformat.format("Tube 0 Sensitivity",    g.Sensitivity[0]))
    dprint(dpformat.format("Tube 1 Sensitivity",    g.Sensitivity[1]))
    dprint(dpformat.format("Tube 2 Sensitivity",    g.Sensitivity[2]))

    setIndent(0)

#### end getGMC_DeviceProperties PPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPP
#PPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPP
#PPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPP

