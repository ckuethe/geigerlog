#!/usr/bin/python3
# -*- coding: UTF-8 -*-

"""
gcommands.py - GeigerLog commands to handle the Geiger counter

include in programs with:
    import gcommands
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
__copyright__       = "Copyright 2016, 2017, 2018"
__credits__         = ["Phil Gillaspy"]
__license__         = "GPL3"

# credits:
# device command coding taken from:
# Phil Gillaspy, https://sourceforge.net/projects/gqgmc/
# and document 'GQ-RFC1201.txt'
# (GQ-RFC1201,GQ Geiger Counter Communication Protocol, Ver 1.40 Jan-2015)
# and GQ's disclosure at:
# http://www.gqelectronicsllc.com/forum/topic.asp?TOPIC_ID=4948


import sys                      # system functions
import serial                   # using the serial port
import serial.tools.list_ports  # allows listing of serial ports
import time
import datetime                 # date and time conversions
import copy                     # make copies of bytes
import struct                   # packing numbers into chars
import traceback                # for traceback on error
#import html

from gutils import *

#
# Commands and functions implemented in device
#

def getVER():
    # Get hardware model and version
    # send <GETVER>> and read 14 bytes
    # returns total of 14 bytes ASCII chars from GQ GMC unit.
    # includes 7 bytes hardware model and 7 bytes firmware version.
    # e.g.: 'GMC-300Re 4.20'

    dprint(gglobs.debug, "getVER:")
    debugIndent(1)
    recd    = None

    rec, error, errmessage = serialCOMM(b'<GETVER>>', 14, orig(__file__))
    if error >= 0:
        try:
            recd = rec.decode('UTF-8')    # convert from bytes to str
        except Exception as e:
            error      = -1
            errmessage = "ERROR getting Version - Bytes are not ASCII: " + str(rec)
            exceptPrint(e, sys.exc_info(), errmessage)
            recd       = str(rec)

    # FOR TESTING ONLY
    if gglobs.testing:
        pass
        recd = "GMC-300Re 3.20"
        recd = "GMC-300Re 4.20"
        recd = "GMC-300Re 4.22"
        recd = "GMC-320Re 4.19"
        #recd = "GMC-320Re 5.xx"
        #recd = "GMC-500Re 1.00"
        #recd = "GMC-500Re 1.08"
        #recd = "GMC-600Re 1.xx"
        #recd = "GMC-600+Re 2.xx"    # fictitious device; not (yet) existing

    try:
        lenrec = len(rec)
    except:
        lenrec = None

    dprint(gglobs.debug, "getVER: len:{}, rec:\"{}\", recd='{}', error={}, errmessage='{}'".format(lenrec, rec, recd, error, errmessage))

    debugIndent(0)

    return (recd, error, errmessage)


def getCPMS(CPMflag = True):
    # Get current CPM or CPS value
    # if CPMflag=True get CPM, else get CPS
    # if CPM:     send <GETCPM>> and read 2 bytes
    # if CPS:     send <GETCPS>> and read 2 bytes
    # In total 2 bytes data are returned from GQ GMC unit
    # in CPM:
    # as a 16 bit unsigned integer.
    # The first byte is MSB byte data and second byte is LSB byte data.
    # e.g.: 00 1C  -> the returned CPM is 28
    # e.g.: 0B EA  -> the returned CPM is 3050
    #
    # in CPS:
    # Comment from Phil Gallespy:
    # 1st byte is MSB, but note that upper two bits are reserved bits.
    # cps_int |= ((uint16_t(cps_char[0]) << 8) & 0x3f00);
    # cps_int |=  (uint16_t(cps_char[1]) & 0x00ff);
    # my observation: highest bit in MSB is always set!
    # e.g.: 80 1C  -> the returned CPS is 28
    # e.g.: FF FF  -> = 3F FF -> the returned maximum CPS is 16383
    #                 or 16383 * 60 = 982980 CPM
    # return CPM even if CPS requested (then return is CPS*60 )

    vprint(gglobs.verbose, "getCPMS: CPMflag= ", CPMflag)
    debugIndent(1)

    value = -99
    if CPMflag:  # measure as CPM
        rec, error, errmessage = serialCOMM(b'<GETCPM>>', 2, orig(__file__))
        if error >= 0: value = rec[0]<< 8 | rec[1]

    else:       # measure as CPS
        rec, error, errmessage = serialCOMM(b'<GETCPS>>', 2, orig(__file__))
        if error >= 0: value = ((rec[0] & 0x3f) << 8 | rec[1]) * 60

    vprint(gglobs.verbose, "getCPMS: rec=", rec, ", value=", value)

    debugIndent(0)
    return (value, error, errmessage)


def turnHeartbeatOn():
    # 3. Turn on the GQ GMC heartbeat
    # Note:     This command enable the GQ GMC unit to send count per second data to host every second automatically.
    # Command:  <HEARTBEAT1>>
    # Return:   A 16 bit unsigned integer is returned every second automatically. Each data package consist of 2 bytes data from GQ GMC unit.
    #           The first byte is MSB byte data and second byte is LSB byte data.
    # e.g.:     10 1C     the returned 1 second count is 28.   Only lowest 14 bits are used for the valid data bit.
    #           The highest bit 15 and bit 14 are reserved data bits.
    # Firmware supported:  GMC-280, GMC-300  Re.2.10 or later

    dprint(gglobs.debug, "turnHeartbeatOn:")
    debugIndent(1)

    if gglobs.ser == None:
        rec         = ""
        error       = 1
        errmessage  = "No serial connection"
    else:
        rec, error, errmessage = serialCOMM(b'<HEARTBEAT1>>', 0, orig(__file__))

    dprint(gglobs.debug, "turnHeartbeatOn: rec='{}', error='{}', errmessage='{}'".format(rec, error, errmessage))

    debugIndent(0)

    return (rec, error, errmessage)


def turnHeartbeatOFF():
    # 4. Turn off the GQ GMC heartbeat
    # Command:  <HEARTBEAT0>>
    # Return:   None
    # Firmware supported:  Re.2.10 or later

    dprint(gglobs.debug, "turnHeartbeatOFF:")
    debugIndent(1)

    if gglobs.ser == None:
        rec         = ""
        error       = 1
        errmessage  = "No serial connection"

    else:
        rec, error, errmessage = serialCOMM(b'<HEARTBEAT0>>', 0, orig(__file__))

    dprint(gglobs.debug, "turnHeartbeatOFF: rec='{}', error='{}', errmessage='{}'".format(rec, error, errmessage))

    debugIndent(0)

    return (rec, error, errmessage)


def getVOLT():
    # Get battery voltage status
    # send <GETVOLT>> and read 1 byte
    # returns one byte voltage value of battery (X 10V)
    # e.g.: return 62(hex) is 9.8V
    # Example: Geiger counter GMC-300E+
    # with Li-Battery 3.7V, 800mAh (2.96Wh)
    # -> getVOLT reading is: 4.2V
    # -> Digital Volt Meter reading is: 4.18V
    #
    # GMC 500/600 is different. Delivers 5 ASCII bytes
    # z.B.[52, 46, 49, 49, 118] = "4.11v"

    dprint(gglobs.debug, "getVOLT:")
    debugIndent(1)

    if gglobs.ser == None:
        rec         = ""
        error       = 1
        errmessage  = "No serial connection"

    else:
        rec, error, errmessage = serialCOMM(b'<GETVOLT>>', gglobs.voltagebytes, orig(__file__))
        dprint(gglobs.debug, "getVOLT: VOLT: raw:", rec)

        ######## TESTING (uncomment all 4) #############
        #rec         = b'3.76v'              # 3.76 Volt
        #error       = 1
        #errmessage  = "testing"
        #dprint(True, "getVOLT: TESTING with rec=", rec)
        ################################################

        if error == 0 or error == 1:
            if gglobs.voltagebytes == 1:
                rec = str(rec[0]/10.0)

            elif gglobs.voltagebytes == 5:
                rec = rec.decode('UTF-8')

            else:
                rec = str(rec) + " @config: voltagebytes={}".format(gglobs.voltagebytes)

        else:
            rec         = "ERROR"
            error       = 1
            errmessage  = "getVOLT: ERROR getting voltage"

    dprint(gglobs.debug, "getVOLT: Using config setting voltagebytes={}:  Voltage='{}', error='{}', errmessage='{}'".format(gglobs.voltagebytes, rec, error, errmessage))
    debugIndent(0)

    return (rec, error, errmessage)


def getSPIR(address = 0, datalength = 4096):
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

    # This contains a WORKAROUND activated with  'SPIRbugfix=True':
    # it asks for only (datalength - 1) bytes,
    # but as it then reads one more byte, the original datalength is obtained

    # BUG ALERT - WORKAROUND ##################################################
    #
    # GMC-300   : no workaround, but use 2k SPIRpage only!
    # GMC-300E+ : use workaround 'datalength - 1' with 4k SPIRpage
    # GMC-320   : same as GMC-300E+
    # GMC-320+  : same as GMC-300E+
    # GMC-500   : ist der Bug behoben oder nur auf altem Stand von GMC-300 zurück?
    #             workaround ist nur 2k SPIRpage anzufordern
    # GMC-500+  : treated as a GM-500
    # GMC-600   : treated as a GM-500
    # GMC-600+  : treated as a GM-500
    # End BUG ALERT - WORKAROUND ##############################################


    # address: pack into 4 bytes, big endian; then clip 1st byte = high byte!
    ad = struct.pack(">I", address)[1:]

    # datalength: pack into 2 bytes, big endian; use all bytes
    # but adjust datalength to fix bug!
    if gglobs.SPIRbugfix:
        dl = struct.pack(">H", datalength - 1)
    else:
        dl = struct.pack(">H", datalength)

    dprint(gglobs.debug, "getSPIR: SPIR requested: address: {:5d}, datalength:{:5d}   (hex: address: {:02x} {:02x} {:02x}, datalength: {:02x} {:02x})".format(address, datalength, ad[0], ad[1], ad[2], dl[0], dl[1]))
    debugIndent(1)

    rec, error, errmessage = serialCOMM(b'<SPIR' + ad + dl + b'>>', datalength, orig(__file__)) # returns bytes

    if rec != None :
        msg = "received: datalength:{:5d}".format(len(rec))
    else:
        msg = "received: ERROR: No data received!"

    dprint(gglobs.debug, "getSPIR: '{}', error='{}', errmessage='{}'".format(msg, error, errmessage))
    debugIndent(0)

    return (rec, error, errmessage)


def getHeartbeatCPS():
    """read bytes until no further bytes coming"""
    # Caution: untested; might not be working

    if not gglobs.debug: return  # execute only in debug mode

    eb= 0
    while True:                  # read more until nothing is returned
                                 # (actually, never more than 1 more is returned)
        eb += 1
        rec = ""
        rec = gglobs.ser.read(2)
        #rec = list(map (ord, rec))      # fails with py3????????????????
        rec = rec      # not tested with Py3 !!!
        cps =  ((rec[0] & 0x3f) << 8 | rec[1])
        #print( "eb=", eb, "cps:", cps)
        break

    return cps


def getExtraByte():
    """read single bytes until no further bytes coming"""

    xrec = b""

    try: # failed when called from 2nd instance of GeigerLog; just to avoid error
        bytesWaiting = gglobs.ser.in_waiting
    except:
        bytesWaiting = 0

    #bytesWaiting += 5   # TESTING ONLY
    if bytesWaiting == 0:
        vprint(gglobs.verbose, "getExtraByte: No extra bytes waiting for reading")
    else:
        dprint(True, "getExtraByte: Bytes waiting: {}".format(bytesWaiting))
        while True:                # read single byte until nothing is returned
            x = gglobs.ser.read(1)
            if len(x) == 0: break
            xrec += x

        dprint(True, "getExtraByte: Got {} extra bytes from reading-pipeline:".format(len(xrec)), list(xrec))
        dprint(True, "getExtraByte: Extra bytes as ASCII: '{}'".format(BytesAsASCII(xrec)))

    return xrec


def getCFG():
    # Get configuration data
    # send <GETCFG>> and read 256 bytes
    # returns
    # - the cfg as a Python bytes string, should be 256 or 512 bytes long
    # - the error value (0, -1, +1)
    # - the error message as string
    # has set gglobs.cfg with read cfg

    # NOTE: 300series uses 256 bytes; 500 and 600 series 512 bytes
    # config size is determined by deviceproperties

    """
    The meaning is: (from: http://www.gqelectronicsllc.com/forum/topic.asp?TOPIC_ID=4447)

    CFG data Offset table. Start from 0
    '*' in left column = read and/or set by GeigerLog
    ==========================================
*   PowerOnOff, //to check if the power is turned on/off intended
*   AlarmOnOff, //1
*   SpeakerOnOff,
    GraphicModeOnOff,
    BackLightTimeoutSeconds,
    IdleTitleDisplayMode,
    AlarmCPMValueHiByte, //6
    AlarmCPMValueLoByte,
*   CalibrationCPMHiByte_0,
*   CalibrationCPMLoByte_0,
*   CalibrationuSvUcByte3_0,
*   CalibrationuSvUcByte2_0, //11
*   CalibrationuSvUcByte1_0,
*   CalibrationuSvUcByte0_0,
*   CalibrationCPMHiByte_1,
*   CalibrationCPMLoByte_1, //15
*   CalibrationuSvUcByte3_1,
*   CalibrationuSvUcByte2_1,
*   CalibrationuSvUcByte1_1,
*   CalibrationuSvUcByte0_1,
*   CalibrationCPMHiByte_2, //20
*   CalibrationCPMLoByte_2,
*   CalibrationuSvUcByte3_2,
*   CalibrationuSvUcByte2_2,
*   CalibrationuSvUcByte1_2,
*   CalibrationuSvUcByte0_2, //25
    IdleDisplayMode,
    AlarmValueuSvByte3,
    AlarmValueuSvByte2,
    AlarmValueuSvByte1,
    AlarmValueuSvByte0, //30
    AlarmType,
*   SaveDataType,
    SwivelDisplay,
    ZoomByte3,
    ZoomByte2, //35
    ZoomByte1,
    ZoomByte0,
    SPI_DataSaveAddress2,
    SPI_DataSaveAddress1,
    SPI_DataSaveAddress0, //40
    SPI_DataReadAddress2,
    SPI_DataReadAddress1,
    SPI_DataReadAddress0,
*   PowerSavingMode,
    Reserved, //45
    Reserved,
    Reserved,
    DisplayContrast,
*   MAX_CPM_HIBYTE,
*   MAX_CPM_LOBYTE, //50
    Reserved,
    LargeFontMode,
    LCDBackLightLevel,
    ReverseDisplayMode,
    MotionDetect, //55
    bBatteryType,
*   BaudRate,
    Reserved,
    GraphicDrawingMode,
    LEDOnOff,
    Reserved,
    SaveThresholdValueuSv_m_nCPM_HIBYTE,
    SaveThresholdValueuSv_m_nCPM_LOBYTE,
    SaveThresholdMode,
    SaveThresholdValue3,        # 65 by my count
    SaveThresholdValue2,
    SaveThresholdValue1,
    SaveThresholdValue0,
    Save_DateTimeStamp, //this one uses 6 byte space  # 69 by my count
    !!! but in the GMC-300E this is at #62 !!!

    # from: http://www.gqelectronicsllc.com/forum/topic.asp?TOPIC_ID=4948 Reply #17
    CFG_nSaveThresholdValue3, //65
    CFG_nSaveThresholdValue2,
    CFG_nSaveThresholdValue1,
    CFG_nSaveThresholdValue0,

    CFG_SSID_0, // 69
    //...
    CFG_SSID_31 = CFG_SSID_0 + 31, //69 + 31

    CFG_Password_0, //101
    //...
    CFG_Password_31 = CFG_Password_0 + 31, //101 + 31

    CFG_Website_0, //133
    //....
    CFG_Website_31 = CFG_Website_0 + 31, //133 + 31

    CFG_URL_0, //165
    //....
    CFG_URL_31 = CFG_URL_0 + 31, //165 + 31

    CFG_UserID_0, //197
    //...........
    CFG_UserID_31 = CFG_UserID_0 + 31, //197+31

    CFG_CounterID_0, //229
    //....
    CFG_CounterID_31 = CFG_CounterID_0 + 31, //229 + 31

    CFG_Period, //261
    CFG_WIFIONOFF, //262
    CFG_TEXT_STATUS_MODE,

    Meaning of the values:
        PowerOnOff byte:
        300 series        : 0 for ON and 255 for OFF
        500 and 600 series: 0 for ON and   1 for OFF # strange, but EmfDev in :
        http://www.gqelectronicsllc.com/forum/topic.asp?TOPIC_ID=4948  Reply #14

        CFG_TEXT_STATUS_MODE is for displaying the "normal/medium/high" text in the large font mode.
        0 - "Off" - not displayed
        1 - "On" - black text and white background
        2 - "Inverted" - White text and black background

        calibration data:
        300 series:     little-endian
        500/600 series: big-endian

    from: http://www.gmcmap.com/tutorial.asp
        *The Wifi feature is only available on models GMC 320+ V5, GMC 500, GMC 500+, GMC 600, GMC 600+ or later.
        **If you are using a GMC-600 or GMC-600+, after factory reset, please go to Wifi, Reset Wifi Module, press YES.
        -->??? is 320+ using a 256 or 512 bytes config???
    """

    dprint(gglobs.debug, "getCFG:")
    debugIndent(1)

    getExtraByte()  # cleaning buffer before getting cfg (some problem in the 500)

    rec         = b""
    error       = 0
    errmessage  = ""

    rec, error, errmessage = serialCOMM(b'<GETCFG>>', gglobs.configsize, orig(__file__))

    ####### BEGIN TESTDATA ####################################
    # replaces rec with data from other runs
    # requires that a testdevice was activated in getVER; the only relevant
    # prperty is the length of config
    if gglobs.testing: # only do this when command line command testing was used
        if gglobs.configsize == 512:
            # using a 512 bytes sequence; data from a GMC-500 readout
            #
            # this one with Power=OFF
            #cfg500d = "01 00 00 02 1F 00 00 64 00 3C 3E C7 AE 14 27 10 42 82 00 00 00 19 41 1C 00 00 00 3F 00 00 00 00 02 02 00 00 00 00 FF FF FF FF FF FF 00 01 00 78 0A FF FF 3C 00 05 FF 01 00 00 0A 00 01 0A 00 64 00 3F 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 77 77 77 2E 67 6D 63 6D 61 70 2E 63 6F 6D 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 6C 6F 67 32 2E 61 73 70 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 02 00 02 11 05 1E 10 34 05 FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF".split(' ')
            # this one with Power = ON
            cfg500d = "00 00 00 02 1F 00 00 64 00 3C 3E C7 AE 14 27 10 42 82 00 00 00 19 41 1C 00 00 00 3F 00 00 00 00 02 02 00 00 00 00 FF FF FF FF FF FF 00 01 00 78 0A FF FF 3C 00 05 FF 01 00 00 0A 00 01 0A 00 64 00 3F 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 77 77 77 2E 67 6D 63 6D 61 70 2E 63 6F 6D 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 6C 6F 67 32 2E 61 73 70 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 02 00 02 11 05 1E 10 34 05 FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF".split(' ')
            cfg500 = cfg500d
            #print("cfg500:\n", len(cfg500), cfg500)

            cfg = b''
            for a in cfg500:       cfg += bytes([int(a, 16)])
            print("TESTDATA: cfg:", len(cfg), type(cfg), "\n", cfg)

        elif "GMC-320Re 5." in gglobs.deviceDetected :  # 320v5 device
            cfg = rec

        elif gglobs.configsize == 256: # 320v4 device
            # next line from 320+ taken on: 2017-05-26 15:29:38

            # power is off
            #cfg320plus = [255, 0, 0, 2, 31, 0, 0, 100, 0, 60, 20, 174, 199, 62, 0, 240, 20, 174, 199, 63, 3, 232, 0, 0, 208, 64, 0, 0, 0, 0, 63, 0, 2, 2, 0, 0, 0, 0, 255, 255, 255, 255, 255, 255, 0, 1, 0, 120, 25, 255, 255, 60, 1, 8, 255, 1, 0, 254, 10, 0, 1, 10, 0, 100, 0, 0, 0, 0, 63, 17, 5, 23, 16, 46, 58, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255]

            # power is on
            cfg320plus = [  0, 0, 0, 2, 31, 0, 0, 100, 0, 60, 20, 174, 199, 62, 0, 240, 20, 174, 199, 63, 3, 232, 0, 0, 208, 64, 0, 0, 0, 0, 63, 0, 2, 2, 0, 0, 0, 0, 255, 255, 255, 255, 255, 255, 0, 1, 0, 120, 25, 255, 255, 60, 1, 8, 255, 1, 0, 254, 10, 0, 1, 10, 0, 100, 0, 0, 0, 0, 63, 17, 5, 23, 16, 46, 58, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255]
            cfg = b''
            for a in cfg320plus:       cfg += bytes([a])
            print("TESTDATA: cfg:", len(cfg), type(cfg), "\n", cfg)
        else:
            cfg = rec

        rec         = cfg # simulates a return from GETCFG
        error       = 1
        errmessage  = "SIMULATION"
    ####### END TESTDATA ####################################

    if rec != None:
        dprint(gglobs.debug, "getCFG: Got {} bytes as {}"  .format(len(rec), type(rec)))
        dprint(gglobs.debug, "getCFG: CFG as HEX  : {}"    .format(BytesAsHex(rec)))
        dprint(gglobs.debug, "getCFG: CFG as DEC  : {}"    .format(BytesAsDec(rec)))
        dprint(gglobs.debug, "getCFG: CFG as ASCII: {}"    .format(BytesAsASCII(rec)))
    else:
        dprint(True, "getCFG: ERROR: Failed to get any configuration data")

    gglobs.cfg = rec        # set the global value with whatever you got !!!

    debugIndent(0)

    return rec, error, errmessage


def writeConfigData(cfgaddress, value):
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
    I think you already know that you can't change a byte from 0x00 to 0x01 but you can change it from 0x01
    to 0x00

    So one way users can change config is to:
    1. <GETCFG>> copy each byte of the config
    2. <ECFG>> erase config from the device
    3. Edit the config you got from 1 like you can change speaker from 1 to 0 or 0 to 1
    4. <WCFG[0x00 - 0x01][0x00 - 0xFF][valid 8bits]>> starting from position 0 to the end of config
    5. <CFGUPDATE>>
    """

    dprint(gglobs.debug, "writeConfigData: cfgaddress: {}, value: {}".format(cfgaddress, value))
    debugIndent(1)

    # get config
    getCFG()        # get a fresh config to the global variable
                    # could there be a problem by using old config? time stamps?
    cfg      = copy.copy(gglobs.cfg)
    cfglen   = len(cfg)

    if cfglen <= 256 and gglobs.configsize == 256:
        doUpdate = 256

    elif cfglen <= 512 and gglobs.configsize == 512:
        doUpdate = 512

    else: # failure:
        bell()
        msg  = "Number of configuration data inconsistent with detected device.<br>Updating config will NOT be done, as Device might be damaged by it!"
        fprint("<span style='color:red;'>" + msg + "</span>")
        dprint(True, "writeConfigData: " + msg.replace('<br>', ' '))

        debugIndent(0)
        return


    # remove right side FFs; will be default after erasing
    cfgstrip = cfg.rstrip(b'\xFF')
    dprint(gglobs.debug, "writeConfigData: Config right-stripped from FF: len:{}: ".format(len(cfgstrip)), BytesAsHex(cfgstrip))

    # modify config at cfgaddress
    cfgmod   = cfgstrip[:cfgaddress] + bytes([value]) + cfgstrip[cfgaddress + 1:]
    dprint(gglobs.debug, "writeConfigData: Config mod @address: {};   new len:{}: ".format(cfgaddress, len(cfgmod)), BytesAsHex(cfgmod))

    # erase config
    dprint(gglobs.debug, "WriteConfig: Erase Config")
    debugIndent(1)
    rec = serialCOMM(b'<ECFG>>', 1, orig(__file__))
    debugIndent(0)

    getCFG()                # getting blank config?
    gglobs.cfg  = cfg       # replace with original cfg

    #pfs = "i={:>3d}  c={:>3d} A0={:<12s}  D0={:<12s}  A0:0x{:03X} D0=0x{:02X}" # formatted print string

    dprint(gglobs.debug, "WriteConfig: Write new Config Data for Config Size:{}".format(doUpdate))
    if doUpdate == 256:
        pfs = "i=A0={:>3d}(0x{:02X}), cfgval=D0={:>3d}(0x{:02X})" # formatted print string
        # write config of up to 256 bytes
        for i, c in enumerate(cfgmod):

            A0 = bytes([i])
            D0 = bytes([c])
            vprint(gglobs.verbose, "WriteConfig: " + pfs.format(i, int.from_bytes(A0, byteorder='big'), c, int.from_bytes(D0, byteorder='big')))
            debugIndent(1)
            rec = serialCOMM(b'<WCFG' + A0 + D0 + b'>>', 1, orig(__file__))
            debugIndent(0)
            #if gglobs.test2:
            #    sleeptime = 1
            #    if ((i + 1) % 10) == 0:     # sleep before the byte #11
            #        dprint(gglobs.debug, "\nSleeping after writing byte #{} for: {} sec\n".format(i, sleeptime))
            #        time.sleep(sleeptime)

    else: # doUpdate == 512
        pfs = "i==A0={:>3d}(0x{:03X}), cfgval==D0={:>3d}(0x{:02X})" # formatted print string
        # write config of up to 512 bytes
        for i, c in enumerate(cfgmod):
            A0 = struct.pack(">H", i)   # pack address into 2 bytes, big endian
            D0 = bytes([c])
            vprint(gglobs.verbose, "WriteConfig: " + pfs.format(i, int.from_bytes(A0, byteorder='big'), c, int.from_bytes(D0, byteorder='big')))
            debugIndent(1)
            rec = serialCOMM(b'<WCFG' + A0 + D0 + b'>>', 1, orig(__file__))
            debugIndent(0)
            #if gglobs.test2:
            #    if ((i + 1) % 10) == 0:     # sleep before the byte #11
            #        sleeptime = 1
            #        dprint(gglobs.debug, "\nSleeping after writing byte #{} for: {} sec\n".format(i, sleeptime))
            #        time.sleep(sleeptime)

    getCFG()                # still getting blank config?
    gglobs.cfg  = cfg       # replace with original cfg

    # update config
    dprint(gglobs.debug, "WriteConfig: Update Config")
    debugIndent(1)
    rec = updateConfig()
    debugIndent(0)

    debugIndent(0)


def updateConfig():
    # 13. Reload/Update/Refresh Configuration
    # Command: <CFGUPDATE>>
    # Return: 0xAA
    # Firmware supported: GMC-280, GMC-300 Re.2.20 or later
    # in GMC-500Re 1.08 this command returns:  b'0071\r\n\xaa'
    # see http://www.gqelectronicsllc.com/forum/topic.asp?TOPIC_ID=4948 #40

    dprint(gglobs.debug, "updateConfig:")
    debugIndent(1)

    rec, error, errmessage = serialCOMM(b'<CFGUPDATE>>', 1, orig(__file__))
    dprint(gglobs.debug, "updateConfig: rec: ", rec)

    debugIndent(0)

    return rec, error, errmessage


def getSERIAL():
    # Get serial number
    # send <GETSERIAL>> and read 7 bytes
    # returns the serial number in 7 bytes
    # each nibble of 4 bit is a single hex digit of a 14 character serial number
    # e.g.: F488007E051234
    #
    # This routine returns the serial number as a 14 character ASCII string

    dprint(gglobs.debug, "getSERIAL:")
    debugIndent(1)

    rec, error, errmessage  = serialCOMM(b'<GETSERIAL>>', 7, orig(__file__))
    dprint(gglobs.debug, "getSERIAL: raw: rec:", rec)

    if error == 0 or error == 1:  # Ok or Warning
        hexlookup = "0123456789ABCDEF"
        sn =""
        for i in range(0,7):
            n1   = ((rec[i] & 0xF0) >>4)
            n2   = ((rec[i] & 0x0F))
            sn  += hexlookup[n1] + hexlookup[n2]
        rec = sn
    dprint(gglobs.debug, "getSERIAL:", rec)

    debugIndent(0)

    return (rec, error, errmessage)


def setDATETIME():
    # from GQ-RFC1201.txt:
    # NOT CORRECT !!!!
    # 22. Set year date and time
    # command: <SETDATETIME[YYMMDDHHMMSS]>>
    # Return: 0xAA
    # Firmware supported: GMC-280, GMC-300 Re.3.00 or later

    # from: GQ-GMC-ICD.odt
    # CORRECT! 6 bytes, no square brackets
    # <SETDATETIME[YY][MM][DD][hh][mm][ss]>>

    dprint(gglobs.debug, "setDATETIME:")
    debugIndent(1)

    tl      = list(time.localtime())  # tl: [2018, 4, 19, 13, 2, 50, 3, 109, 1]
                                      # for: 2018-04-19 13:02:50
    tl0     = tl.copy()

    tl[0]  -= 2000
    tlstr   = b''
    for i in range(0,6):  tlstr += bytes([tl[i]])
    dprint(gglobs.debug, "setDATETIME: now:", tl0[:6], ", coded:", tlstr)

    rec, error, errmessage = serialCOMM(b'<SETDATETIME'+ tlstr + b'>>', 1, orig(__file__))

    debugIndent(0)

    return (rec, error, errmessage)


def getDATETIME():
    # Get year date and time
    # send <GETDATETIME>> and read 7 bytes
    # returns 7 bytes data: YY MM DD HH MM SS 0xAA
    #
    # This routine returns date and time in the format:
    #       YYYY-MM-DD HH:MM:SS
    # e.g.: 2017-12-31 14:03:19

    dprint(gglobs.debug, "getDATETIME:")
    debugIndent(1)

    # yields: rec: b'\x12\x04\x13\x0c9;\xaa' , len:7
    # for:           2018-04-19 12:57:59
    rec, error, errmessage = serialCOMM(b'<GETDATETIME>>', 7, orig(__file__))

    if rec == None:
        dprint(gglobs.debug, "ERROR getting DATETIME from counter - nothing received - ", errmessage)
    else:
        dprint(gglobs.debug, "getDATETIME: raw:", rec, ", len: "+str(len(rec)))

        if error == 0 or error == 1:  # Ok or only Warning
            try:
                rec  = datetime.datetime(rec[0] + 2000, rec[1], rec[2], rec[3], rec[4], rec[5])
            except:
                if rec ==  [0, 1, 1, 0, 0, 80, 170]:    # the values found after first start!
                    rec         = "2000-01-01 00:00:01" # overwrite rec with fake date
                    error       = -1
                    errmessage  = "ERROR getting Date & Time - Set at device first!"
                    localdebug  = True
                else:
                    # conversion to date failed
                    rec         = "2099-09-09 09:09:09" # overwrite rec with fake date
                    error       = -1
                    errmessage  = "ERROR getting Date & Time"
                    localdebug  = True
        else:   # a real error
            dprint(True, "ERROR getting DATETIME from counter: ", errmessage)

        dprint(gglobs.debug, "getDATETIME:", rec)

    debugIndent(0)

    return (rec, error, errmessage)


def getTEMP():
    # NOTE: Temperature may be completely in active in 500 and 600 versions
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

    dprint(gglobs.debug, "getTEMP:")
    debugIndent(1)

    rec, error, errmessage  = serialCOMM(b'<GETTEMP>>', 4, orig(__file__))

    # TESTING example for '-28.8 °C'
    #rec = [28, 8, 1, 170 ]

    dprint(gglobs.debug, "getTEMP: Temp raw: rec={}, error={}, errmessage='{}'".format(rec, error, errmessage))

    if error == 0 or error == 1:  # Ok or Warning
        if "GMC-3" in gglobs.deviceDetected :   # all 300 series
            temp = rec[0] + rec[1]/10.0     # unclear: is  decimal part rec[1] single digit or a 2 digit?
                                            # 3 digit not possible as byte value is from 0 ... 255
                                            # expecting rec[1] always from 0 ... 9
            if rec[2] != 0 : temp *= -1
            if rec[1]  > 9 : temp  = "getTEMP: ERROR: Temp={} - illegal value found for decimal part of temperature ={}".format(temp, rec[1])
            rec = temp

        elif   "GMC-5" in gglobs.deviceDetected \
            or "GMC-6" in gglobs.deviceDetected:  # GMC-500/600
            temp = rec[0] + rec[1]/10.0     # unclear: is  decimal part rec[1] single digit or a 2 digit?
                                            # 3 digit not possible as byte value is from 0 ... 255
                                            # expecting rec[1] always from 0 ... 9
            if rec[2] <= 0 : temp *= -1     # guessing: value=1 looks like positive Temperature. Negative is???
            if rec[1]  > 9 : temp  = "getTEMP: ERROR: Temp={} - illegal value found for decimal part of temperature ={}".format(temp, rec[1])
            rec = temp

        else: # perhaps even 200 series?
            rec = "UNDEFINED"

    dprint(gglobs.debug, "getTEMP: Temp rec={}, error={}, errmessage='{}'".format(rec, error, errmessage))

    debugIndent(0)

    return (rec, error, errmessage)


def getGYRO():
    # Get gyroscope data
    # Firmware supported: GMC-320 Re.3.01 or later (NOTE: Not for GMC-300!)
    # Send <GETGYRO>> and read 7 bytes
    # Return: Seven bytes gyroscope data in hexdecimal: BYTE1,BYTE2,BYTE3,BYTE4,BYTE5,BYTE6,BYTE7
    # Here: BYTE1,BYTE2 are the X position data in 16 bits value. The first byte is MSB byte data and second byte is LSB byte data.
    #       BYTE3,BYTE4 are the Y position data in 16 bits value. The first byte is MSB byte data and second byte is LSB byte data.
    #       BYTE5,BYTE6 are the Z position data in 16 bits value. The first byte is MSB byte data and second byte is LSB byte data.
    #       BYTE7 always 0xAA

    dprint(gglobs.debug, "getGYRO:")
    debugIndent(1)

    rec, error, errmessage  = serialCOMM(b'<GETGYRO>>', 7, orig(__file__))
    dprint(gglobs.debug, "getGYRO: raw: rec={}, error={}, errmessage='{}'".format(rec, error, errmessage))

    if error == 0 or error == 1:  # Ok or Warning
        x = rec[0] * 256 + rec[1]
        y = rec[2] * 256 + rec[3]
        z = rec[4] * 256 + rec[5]
        rec = "X=0x{:04x}, Y=0x{:04x}, Z=0x{:04x}   ({},{},{})".format(x,y,z,x,y,z)

    dprint(gglobs.debug, "getGYRO: rec='{}', error={}, errmessage='{}'".format(rec, error, errmessage))

    debugIndent(0)

    return rec, error, errmessage


def setPOWEROFF():
    # 12. Power OFF
    # Command: <POWEROFF>>
    # Return: none
    # Firmware supported: GMC-280, GMC-300 Re.2.11 or later

    debugIndent(1)
    rec  = serialCOMM(b'<POWEROFF>>', 0, orig(__file__))
    dprint(gglobs.debug, "setPOWEROFF:", rec)
    debugIndent(0)

    return rec


def setPOWERON():
    # 26. Power ON
    # Command: <POWERON>>
    # Return: none
    # Firmware supported: GMC-280, GMC-300, GMC-320 Re.3.10 or later

    debugIndent(1)
    rec  = serialCOMM(b'<POWERON>>', 0, orig(__file__))
    dprint(gglobs.debug, "setPOWERON:", rec)
    debugIndent(0)

    return rec


def setREBOOT():
    # 21. Reboot unit
    # command: <REBOOT>>
    # Return: None
    # Firmware supported: GMC-280, GMC-300 Re.3.00 or later

    debugIndent(1)
    rec  = serialCOMM(b'<REBOOT>>', 0, orig(__file__))
    dprint(gglobs.debug, "setREBOOT:", rec)
    debugIndent(0)

    return rec


def setFACTORYRESET():
    # 20. Reset unit to factory default
    # command: <FACTORYRESET>>
    # Return: 0xAA
    # Firmware supported: GMC-280, GMC-300 Re.3.00 or later

    debugIndent(1)
    rec  = serialCOMM(b'<FACTORYRESET>>', 1, orig(__file__))
    dprint(gglobs.debug, "setFACTORYRESET:", rec)
    debugIndent(0)

    return rec


#
# Derived commands and functions
#

def isPowerOn():
    """Checks Power status in the configuration"""

    #PowerOnOff byte:
    #at config offset  : 0
    #300 series        : 0 for ON and 255 for OFF
    #http://www.gqelectronicsllc.com/forum/topic.asp?TOPIC_ID=4948  Reply #14
    #confirmed in Reply #17
    #500/600 series    : PowerOnOff byte: 0 for ON, and 1 for OFF

    cfg    = gglobs.cfg
    c      = cfg[gglobs.cfgOffsetPower]
    #print("gglobs.deviceDetected:", gglobs.deviceDetected)
    try:
        if "GMC-3" in gglobs.deviceDetected: # all 300series
            #print("GMC-3 in gglobs.deviceDetected")
            if   c == 0:            p = "ON"
            elif c == 255:          p = "OFF"
            else:                   p = c
        elif "GMC-5" in gglobs.deviceDetected or \
             "GMC-6" in gglobs.deviceDetected :  # 500, 500+, 600, 600+
            # as stated by EmfDev from GQ, but strange because different from
            # handling the Speaker and Alarm settings
            if   c == 0:            p = "ON"
            elif c == 1:            p = "OFF"
            else:                   p = c
        else:
            p = "UNKNOWN"
    except:
        p = "UNKNOWN"

    return p


def isAlarmOn():
    """Checks Alarm On status in the configuration
    Alarm at offset:1"""

    cfg    = gglobs.cfg

    try:
        c = cfg[gglobs.cfgOffsetAlarm]
    except:
        c = "UNKNOWN"

    if   c == 0:            p = "OFF"
    elif c == 1:            p = "ON"
    else:                   p = c

    return p


def isSpeakerOn():
    """Checks Speaker On status in the configuration
    Speaker at offset:2"""

    cfg    = gglobs.cfg

    try:
        c = cfg[gglobs.cfgOffsetSpeaker]
    except:
        c = "UNKNOWN"

    if   c == 0:            p = "OFF"
    elif c == 1:            p = "ON"
    else:                   p = c

    return p


def getSaveDataType():
    """
    Bytenumber:32  Parameter: CFG_SaveDataType
    0 = off (history is off),
    1 = CPS every second,
    2 = CPM every minute,
    3 = CPM recorded once per hour.
    """

    sdttxt = gglobs.savedatatypes
    #print sdttxt, len(sdttxt)

    cfg    = gglobs.cfg

    try:
        sdt = cfg[gglobs.cfgOffsetSDT]
    except:
        sdt = 9999

    #print "sdt:", sdt
    try:
        if sdt <= len(sdttxt):
            txt                 = sdttxt[sdt]
            gglobs.savedatatype = txt
        else:
            txt = "UNKNOWN"
    except:
        txt= "Error in getSaveDataType, undefined type: {}".format(sdt)

    return sdt, txt


def getBAUDRATE():
    # reads the baudrate from the configuration data
    # cfg is counter configuration
    # Note: kind of pointless, because in order to read the config data
    # from the device you must already know the baudrate,
    # or the comm will fail :-/

    """
    discovered for the 300 series:
        baudrate = 1200         # config setting:  64
        baudrate = 2400         # config setting: 160
        baudrate = 4800         # config setting: 208
        baudrate = 9600         # config setting: 232
        baudrate = 14400        # config setting: 240
        baudrate = 19200        # config setting: 244
        baudrate = 28800        # config setting: 248
        baudrate = 38400        # config setting: 250
        baudrate = 57600        # config setting: 252
        baudrate = 115200       # config setting: 254
        #baudrate = 921600      # config setting: not available

    for the GMC-500 and 600 series
    by EmfDev from GQ from here:
    http://www.gqelectronicsllc.com/forum/topic.asp?TOPIC_ID=4948 Reply #14
    - The baudrate config is now
        baudrate = 115200       # config setting: 0
        baudrate = 1200         # config setting: 1
        baudrate = 2400         # config setting: 2
        baudrate = 4800         # config setting: 3
        baudrate = 9600         # config setting: 4
        baudrate = 14400        # config setting: 5
        baudrate = 19200        # config setting: 6
        baudrate = 28800        # config setting: 7
        baudrate = 38400        # config setting: 8
        baudrate = 57600        # config setting: 9
    """

    dprint(gglobs.debug, "getBAUDRATE:")
    debugIndent(1)

    if  "GMC-3" in gglobs.deviceDetected: # all 300series
        brdict  = {64:1200, 160:2400, 208:4800, 232:9600, 240:14400, 244:19200, 248:28800, 250:38400, 252:57600, 254:115200}

    elif "GMC-5" in gglobs.deviceDetected or \
         "GMC-6" in gglobs.deviceDetected :  # 500, 500+, 600, 600+
        brdict  = {0:115200, 1:1200, 2:2400, 3:4800, 4:9600, 5:14400, 6:19200, 7:28800, 8:38400, 9:57600}
    else:
        brdict  = {}

    key     = 99999
    cfg     = gglobs.cfg
    #print("getBAUDRATE: cfg Baudrate:")
    #for key, value in sorted(brdict.items()):
    #    print ("      {:08b} {:3d} {:6d}".format(key, key, value))

    try:
        key = cfg[57]
        rec = brdict[key]
    except:
        rec = "ERROR: Baudrate cannot be determined"

    dprint(gglobs.debug, "getBAUDRATE: " + str(rec) + " with config[57]={}".format(key))

    debugIndent(0)

    return rec


def autoBAUDRATE(usbport):
    """Tries to find a proper baudrate by testing for successful serial
    communication at up to all possible baudrates, beginning with the
    highest"""

    """
    NOTE: the device port can be opened without error at any baudrate,
    even when no communication can be done, e.g. due to wrong baudrate.
    Therfore we test for successful communication by checking for the return
    string beginning with 'GMC'. ON success, this baudrate will be returned.
    A baudrate=0 will be returned when all communication fails.
    On a serial error, baudrate=None will be returned.
    """

    dprint(gglobs.debug, "autoBAUDRATE: Autodiscovery of baudrate on port: '{}'".format(usbport))
    debugIndent(1)

    baudrates = gglobs.baudrates
    baudrates.sort(reverse=True) # to start with highest baudrate
    for baudrate in baudrates:
        dprint(True, "autoBAUDRATE: Trying baudrate:", baudrate)
        try:
            ser = serial.Serial(usbport, baudrate, timeout= 0.5)
            ser.write(b'<GETVER>>')
            rec = ser.read(14) # may leave bytes in the pipeline, if GETVER has
                               # more than 14 bytes as may happen in newer counters
            while ser.in_waiting:
                ser.read(1)
                time.sleep(0.1)
            ser.close()
            if rec.startswith(b"GMC"):
                dprint(True, "autoBAUDRATE: Success with {}".format(baudrate))
                break

        except Exception as e:
            errmessage1 = "autoBAUDRATE: ERROR: autoBAUDRATE: Serial communication error on finding baudrate"
            exceptPrint(e, sys.exc_info(), errmessage1)
            baudrate = None
            break

        baudrate = 0

    dprint(gglobs.debug, "autoBAUDRATE: Found baudrate: {}".format(baudrate))
    debugIndent(0)

    return baudrate


def autoPORT():
    """Tries to find a working port and baudrate by testing all serial
    ports for successful communication by auto discovery of baudrate.
    All available ports will be listed with the highest baudrate found.
    Ports are found as:
    /dev/ttyS0 - ttyS0              # a regular serial port
    /dev/ttyUSB0 - USB2.0-Serial    # a USB-to-Serial port
    """

    dprint(gglobs.debug, "autoPORT: Autodiscovery of Serial Ports")
    debugIndent(1)

    time.sleep(0.5) # a freshly plugged in device, not fully recognized
                    # by system, sometimes produces errors

    ports =[]
    # Pyserial:
    # 'include_links (bool)' – include symlinks under /dev when they point to a serial port
    #lp = serial.tools.list_ports.comports(include_links=True) # also shows e.g. /dev/geiger
    lp = serial.tools.list_ports.comports(include_links=False) # default; no symlinks shown

    # ####### TESTING only #########
    #lp.append("/dev/ttyS0 - ttyS0")

    if len(lp) == 0:
        errmessage = "autoPORT: ERROR: No available serial ports found"
        dprint(True, errmessage)
        return None, errmessage
    else:
        dprint(True, "autoPORT: Found these ports:")
        for p in lp :
            dprint(True, "   ", p)
            ports.append(str(p).split(" ",1)[0])

    ports.sort()
    ports_found = []

    dprint(True, "autoPORT: Testing all ports for communication:")
    for port in ports:
        #dprint(True, "Port:", port)
        if "/dev/ttyS" in port:
            if gglobs.ttyS == 'include':
                dprint(True, "autoPORT: Include Flag is set for port: '{}'".format(port))
            else:
                dprint(True, "autoPORT: Ignore Flag is set for port: '{}'".format(port))
                continue

        abr = autoBAUDRATE(port)
        if abr == None:
            dprint(True, "autoPORT: ERROR: Failure during Serial Communication on port: '{}'".format(port))
        elif abr > 0:
            ports_found.append((port, abr))
        elif abr == 0:
            dprint(True, "autoPORT: Failure - no communication at any baudrate on port: '{}'".format(port))

    if len(ports_found) == 0:
        errmessage = "autoPORT: ERROR: No communication at any serial port and baudrate"
        ports_found = None
    else:
        errmessage = ""

    dprint(gglobs.debug, "autoPORT: " + errmessage)
    debugIndent(0)

    return ports_found, errmessage


#
# Communication with serial port with exception handling
#
def serialCOMM(sendtxt, returnlength, caller = ("", "", -1)):
    # write to and read from serial port, exit on serial port error
    # when not enough bytes returned, try send+read again up to 3 times.
    # exit if it still fails

    vprint(gglobs.verbose, "serialCOMM: sendtxt: '{}', returnlength: {}, caller: '{}'".format(sendtxt, returnlength, caller))
    debugIndent(1)

    rec         = None
    error       = 0
    errmessage  = ""

    while True:
        if gglobs.ser == None:
            error       = -1
            errmessage  = "No connection (Serial Port is closed)"
            break

    #write to port
        breakWrite = False
        try:
            #raise Exception
            #raise serial.SerialException
            #raise serial.SerialTimeoutException  # write-timeout exception
            wtime = time.time()
            rec = gglobs.ser.write(sendtxt)  # rec = no of bytes written
            wtime = (time.time() - wtime) * 1000 # wtime in ms
        except serial.SerialException as e:
            srcinfo = "serialCOMM: ERROR: WRITE failed with serial exception"
            exceptPrint(e, sys.exc_info(), srcinfo)
            dprint(True, "serialCOMM: ERROR: caller is: {} in line no:{}".format(caller[0], caller[1]))
            dprint(True, traceback.format_exc()) # more extensive info
            breakWrite = True

        except serial.SerialTimeoutException as e:
            srcinfo = "serialCOMM: ERROR: WRITE failed with SerialTimeoutException"
            exceptPrint(e, sys.exc_info(), srcinfo)
            dprint(True, "serialCOMM: ERROR: caller is: {} in line no:{}".format(caller[0], caller[1]))
            dprint(True, traceback.format_exc()) # more extensive info
            breakWrite = True

        except Exception as e:
            srcinfo = "serialCOMM: ERROR: WRITE failed"
            exceptPrint(e, sys.exc_info(), srcinfo)
            dprint(True, "serialCOMM: ERROR: caller is: {} in line no:{}".format(caller[0], caller[1]))
            dprint(True, traceback.format_exc()) # more extensive info
            dprint(True, traceback.format_exc()) # more extensive info
            breakWrite = True

        if breakWrite:
            try:
                gglobs.ser.close()
            except:
                pass
            rec         = None
            error       = -1
            errmessage  = "serialCOMM: ERROR: WRITE failed. See log for details"
            break

    # read from port
        breakRead = False
        rtime  = time.time()
        rtimex = rtime
        try:
            #raise Exception
            #raise serial.SerialException
            rec    = gglobs.ser.read(returnlength)
            rtime  = (time.time() - rtime) * 1000
            vprint(gglobs.verbose, "serialCOMM: got {} bytes, first (up to ten) bytes: {}".format(len(rec), rec[:10]))
            extra  = getExtraByte()
            rec   += extra
            rtimex = (time.time() - rtimex) * 1000 - rtime

        except serial.SerialException as e:
            srcinfo = "serialCOMM: ERROR: READ failed with serial exception"
            exceptPrint(e, sys.exc_info(), srcinfo)
            dprint(True, "serialCOMM: ERROR: caller is: {} in line no:{}".format(caller[0], caller[1]))
            dprint(True, traceback.format_exc()) # more extensive info
            breakRead = True

        except Exception as e:
            srcinfo = "serialCOMM: ERROR: READ failed"
            exceptPrint(e, sys.exc_info(), srcinfo)
            dprint(True, "serialCOMM: ERROR: caller is: {} in line no:{}".format(caller[0], caller[1]))
            dprint(True, traceback.format_exc()) # more extensive info
            breakRead = True

        if breakRead:
            try:
                gglobs.ser.close()
            except:
                pass
            rec         = None
            error       = -1
            errmessage  = "serialCOMM: ERROR: READ failed. See log for details"
            break

        # avoid divide by zero
        if returnlength > 0:    rbyte = "{:6.1f}".format(rtime/returnlength)
        else:                   rbyte = "N/A"

        if rtime > (gglobs.timeout * 1000):
            marker      = "Timeout--" * 15    # mark Timeout lines
            localdebug  = True                # and force these to debug print
        elif rtime > 100:
            marker      = ">" * 80            # mark long reading times
            localdebug  = True                # and force these to debug print
        else:
            marker      = ""
            localdebug  = gglobs.verbose
        vprint(localdebug, "serialCOMM: Timing (ms): write:{:6.2f}, read:{:6.1f}, read per byte:{}, extraread:{:6.1f}  ".format(wtime, rtime, rbyte, rtimex), marker)

    # Retry loop
        if len(rec) < returnlength:
            if rtime > (gglobs.timeout * 1000):
                msg  = "TIMEOUT ERROR: Serial Port Timeout of {:3.1f}s exceeded.".format(gglobs.timeout)
                fprint(msg, error = True)
                dprint(True, "serialCOMM: " + msg, "- rtime:{:5.1f}ms".format(rtime))
                stxt =  "Failure with command " + html_escape(str(sendtxt))
                fprint(stxt)
                dprint(True, "serialCOMM: " + stxt)

            fprint("Got some data from device, but not enough. Retrying.")
            dprint(True, "serialCOMM: ERROR: Received length: {} is less than requested: {}".format(len(rec), returnlength))
            dprint(gglobs.debug, "serialCOMM: rec: (len={}): {}".format(len(rec), BytesAsHex(rec)))

            error       = 1
            errmessage  = "serialCOMM: ERROR: Record too short: Received bytes: {} < requested: {}".format(len(rec), returnlength)

            # RETRYING
            count    = 0
            countmax = 3
            while True:
                count += 1
                dprint(True, "serialCOMM: RETRY: to get full return record, trial #", count)

                time.sleep(0.5) # extra sleep after not reading enough data

                extra = getExtraByte()   # just to make sure the pipeline is clean

                gglobs.ser.write(sendtxt)
                time.sleep(0.3) # after sending

                rtime  = time.time()
                rec = gglobs.ser.read(returnlength)
                rtime = (time.time() - rtime) * 1000
                dprint(gglobs.debug, "Timing (ms): Retry read:{:6.1f}".format(rtime))

                if len(rec) == returnlength:
                    dprint(True,  "serialCOMM: RETRY: returnlength is {} bytes. OK now. Continuing normal cycle".format(len(rec)), ", rec:", rec)
                    errmessage += "; ok after {} retry".format(count)
                    extra = getExtraByte()   # just to make sure the pipeline is clean
                    fprint("Retry successful.")
                    break
                else:
                    #dprint(True,  u"RETRY: serialCOMM: returnlength is {} bytes. Still NOT ok; trying again".format(len(rec)))
                    pass

                if count >= countmax:
                    dprint(True, "serialCOMM: RETRY: Retried {} times, always failure, giving up. Serial communication error.".format(count))
                    error       = -1
                    errmessage  = "ERROR communicating via serial port. Giving up."
                    fprint(errmessage)
                    break

                fprint("ERROR communicating via serial port. Retrying again.")

        break

    debugIndent(0)

    return (rec, error, errmessage)


def serialOPEN(usbport, baudrate, timeout):
    """
    Tries to open the serial port
    Return: on success: ser, ""
            on failure: None, errmessage
    """

    msg         = "port='{}', baudrate={}, timeout={}".format(usbport, baudrate, timeout)
    gglobs.ser  = None
    error       = 0
    errmessage  = ""
    errmessage1 = ""

    dprint(gglobs.debug, "serialOPEN: Settings: " + msg)
    debugIndent(1)

    while True:
        # Make the serial connection
        try:
            gglobs.ser = serial.Serial(usbport, baudrate, timeout=timeout)
            # ser is like:
            # Serial<id=0x7f2014d371d0, open=True>(port='/dev/gqgmc',
            # baudrate=115200, bytesize=8, parity='N', stopbits=1, timeout=20,
            # xonxoff=False, rtscts=False, dsrdtr=False)
        except Exception as e:
            errmessage1 = "ERROR: Connection problem with device @ " + msg
            exceptPrint(e, sys.exc_info(), "serialOPEN: " + errmessage1)
            gglobs.ser  = None
            break

        # Test for successful communication with a GMC Geiger counter
        # The device port can be opened without error even when no
        # communication can be done, e.g. due to wrong baudrate or wrong device
        dprint(gglobs.debug, "serialOPEN: Port opened ok, now testing communication")
        try:
            ver, error, errmessage = getVER()
        except Exception as e:
            errmessage1  = "ERROR: Port opened ok, but Communication failed. Is baudrate correct?"
            exceptPrint(e, sys.exc_info(), "serialOPEN: " + errmessage1)
            gglobs.ser  = None
            break

        if error < 0:
            errmessage1  = "ERROR: Communication problem: " + errmessage
            dprint(True, "serialOPEN: " + errmessage1 )
            gglobs.ser  = None
            break
        else:
            # ver[0:12]: model name + major number of firmware version
            # like: 'GMC-300Re 4.'
            #print ("ver: {}, ver[0:12]: '{}'".format(ver, ver[0:12]))
            if ver.startswith("GMC"):
                gglobs.deviceDetected = ver

            #elif ver.startswith("xyz"):
            #    # code for other counters goes here
            else:
                err = "ERROR: No GMC device detected"
                errmessage1 += err
                dprint(True, "serialOPEN: " + err)
                gglobs.ser  = None

        break

    if gglobs.ser == None:
        rmsg = "{}".format(errmessage1.replace('[Errno 2]', '<br>'))
    else:
        dprint(gglobs.debug, "serialOPEN: " + "Communication ok with device:", ver)
        rmsg = ""

    debugIndent(0)

    return gglobs.ser, rmsg


def fprintDeviceInfo():
    """Print device info via fprint"""

    dprint(gglobs.debug, "fprintDeviceInfo:")
    debugIndent(1)

    forcedebug = "debug"
    while True:
        fprint(header("Device Info"))

        # device name
        fprint("Connected device:", gglobs.deviceDetected, forcedebug)

        # connected port
        fprint("Device connected with port:", "{} (Timeout:{} sec)".format(gglobs.usbport, gglobs.timeout), forcedebug)

        # serial number
        sn, error, errmessage = getSERIAL()

        # baudrate as set in program
        fprint("Baudrate set by program:",  gglobs.baudrate, forcedebug)

        cfg, error, errmessage     = getCFG()
        if error < 0:
            fprint("ERROR trying to read Device Configuration", error = True)

        # baudrate as read from device
        fprint("Baudrate read from device:", getBAUDRATE(), forcedebug)

        # get date and time from device, compare with computer time
        rec, error, errmessage = getDATETIME()
        if error < 0:
            fprint("Device Date and Time:", errmessage, forcedebug)
        else:
            devtime = str(rec)
            cmptime = stime()
            deltat  = datestr2num(cmptime) - datestr2num(devtime)
            if deltat == 0:
                dtxt = "Device time is same as computer time"
            elif deltat > 0:
                dtxt = "Device is slower than computer by {:0.0f} sec".format(deltat)
            else:
                dtxt = "Device is faster than computer by {:0.0f} sec".format(abs(deltat))

            fprint("Date and Time from device:",   devtime, forcedebug)
            fprint("Date and Time from computer:", cmptime, forcedebug)
            fprint("", dtxt, forcedebug)

        # voltage
        rec, error, errmessage = getVOLT()
        if error < 0:
            fprint("Device Battery Voltage:", "{}".format(errmessage))
        else:
            fprint("Device Battery Voltage:", "{} Volt".format(rec))

        # temperature
        rec, error, errmessage = getTEMP()
        if error < 0:
            fprint("Device Temperature:", "'{}'".format(errmessage))
        else:
            fprint("Device Temperature:", "{} °C".format(rec))
            fprint("", "(ONLY for GMC-320 ?)")

        # gyro
        rec, error, errmessage = getGYRO()
        if error < 0:
            fprint("Device Gyro Data:", "'{}'".format(errmessage))
        else:
            fprint("Device Gyro data:", rec)
            fprint("", "(only GMC-320 Re.3.01 and later)")

        # power state
        fprint("Device Power State:", isPowerOn(), forcedebug)

        # Alarm state
        fprint("Device Alarm State:", isAlarmOn(), forcedebug)

        # Speaker state
        fprint("Device Speaker State:", isSpeakerOn(), forcedebug)

        # Save Data Type
        sdt, sdttxt = getSaveDataType()
        fprint("Device Saving Mode:", sdttxt, forcedebug)

        # MaxCPM
        try:
            value = cfg[gglobs.cfgOffsetMaxCPM] * 256 + cfg[gglobs.cfgOffsetMaxCPM +1]
        except:
            value = "Unknown"
        fprint("Max CPM (invalid if 65535!):", value, forcedebug)

        # Calibration
        fprint(ftextCalibration(), forcedebug)

        # Web related High bytes in Config
        fprint(getHighConfig(), forcedebug )

        break

    debugIndent(0)


def getHighConfig():
    """get the Web and other data sitting in the config at 68 ... 268"""

    cfg    = gglobs.cfg
    ghc    = ""
    #print("getHighConfig: type(cfg), len(cfg):", type(cfg), len(cfg))
    #print("cfg:\n", cfg)

    ghc    += "Device WiFi Data Setup\n"

    if gglobs.configsize == 512:

        cfgbyte         = 0x45
        cfgstep         = 0x20

        # 0x45 = 69d
        try:
            CFG_SSID        = cfg[ cfgbyte + 0 * cfgstep : cfgbyte + 1 * cfgstep ].decode("UTF-8")
            ghc += "{:35s}{}\n". format("   SSID",      CFG_SSID.replace("\x00", ""))
        except:
            ghc += "{:35s}{}\n". format("   SSID",      "Unknown")

        # 0x45 + 0x20 = 0x65 = 101
        try:
            CFG_PASSWORD    = cfg[ cfgbyte + 1 * cfgstep : cfgbyte + 2 * cfgstep ].decode("UTF-8")
            ghc += "{:35s}{}\n". format("   Password",  CFG_PASSWORD.replace("\x00", ""))
        except:
            ghc += "{:35s}{}\n". format("   Password",  "Unknown")

        # 0x45 + 0x20*2 = 0x85 = 133
        try:
            CFG_WEBSITE     = cfg[ cfgbyte + 2 * cfgstep : cfgbyte + 3 * cfgstep ].decode("UTF-8")
            ghc += "{:35s}{}\n". format("   Website",   CFG_WEBSITE.replace("\x00", ""))
        except:
            ghc += "{:35s}{}\n". format("   Website",   "Unknown")

        # 0x45 + 0x20*3 = 0xA5 = 165
        try:
            CFG_URL         = cfg[ cfgbyte + 3 * cfgstep : cfgbyte + 4 * cfgstep ].decode("UTF-8")
            ghc += "{:35s}{}\n". format("   URL",       CFG_URL.replace("\x00", ""))
        except:
            ghc += "{:35s}{}\n". format("   URL",       "Unknown")

        # 0x45 + 0x20*4 = 0xC5 = 197
        try:
            CFG_UserID      = cfg[ cfgbyte + 4 * cfgstep : cfgbyte + 5 * cfgstep ].decode("UTF-8")
            ghc += "{:35s}{}\n". format("   UserID",    CFG_UserID.replace("\x00", ""))
        except:
            ghc += "{:35s}{}\n". format("   UserID",    "Unknown")

        # 0x45 + 0x20*5 = 0xE5 = 229
        try:
            CFG_CounterID   = cfg[ cfgbyte + 5 * cfgstep : cfgbyte + 6 * cfgstep ].decode("UTF-8")
            ghc += "{:35s}{}\n". format("   CounterID", CFG_CounterID.replace("\x00", ""))
        except:
            ghc += "{:35s}{}\n". format("   CounterID", "Unknown")

        # 0x45 + 0x20*6 = 0x105 = 261
        try:
            CFG_Period      = cfg[ 261]
            ghc += "{:35s}{}\n". format("   Period (min)", CFG_Period)
        except:
            ghc += "{:35s}{}\n". format("   Period (min)", "Unknown")

        # 0x106 = 262
        try:
            CFG_WIFIONOFF   = cfg[ 262]
            ghc += "{:35s}{}\n". format("   WiFiOnOff", CFG_WIFIONOFF)
        except:
            ghc += "{:35s}{}\n". format("   WiFiOnOff ", "Unknown")

        # 0x107 = 263
        # from http://www.gqelectronicsllc.com/forum/topic.asp?TOPIC_ID=4948 Reply #17
        # CFG_TEXT_STATUS_MODE is for displaying the "normal/medium/high" text in the large font mode.
        # 0 - "Off" - not displayed
        # 1 - "On" - black text and white background
        # 2 - "Inverted" - White text and black background
        try:
            CFG_TEXT_STATUS_MODE   = cfg[ 262]
            if   CFG_TEXT_STATUS_MODE == 0:   strMode = "Large Font Mode: OFF"
            elif CFG_TEXT_STATUS_MODE == 1:   strMode = "Large Font Mode: ON"
            elif CFG_TEXT_STATUS_MODE == 2:   strMode = "Large Font Mode: Inverted"
            else                          :   strMode = "Unknown"
            ghc += "{:35s}{}\n". format("TextStatusMode", strMode)
        except:
            ghc += "{:35s}{}\n". format("TextStatusMode", "Unknown")

        if gglobs.devel:    # show only in development mode
            # 0x108 = 264
            try:
                rec = cfg[ 0x108 : 0x108 + 6 ] # CFG_Save_DateTimeStamp
                dt  = datetime.datetime(rec[0] + 2000, rec[1], rec[2], rec[3], rec[4], rec[5])
                ghc += "{:35s}{}\n". format("Save_DateTimeStamp", dt)
            except:
                ghc += "{:35s}{}\n". format("Save_DateTimeStamp", "ERROR: incorrect DateTime stamp")
                dprint(gglobs.debug, "Save_DateTimeStamp", "ERROR: incorrect DateTime stamp at pos #d264")

    elif "GMC-320Re 5." in gglobs.deviceDetected:  # 320v5 device

        # 0x45 = 69d
        try:
            CFG_SSID        = cfg[ 69  : 69 + 16 ].decode("UTF-8")
            ghc += "{:35s}{}\n". format("   SSID",      CFG_SSID.replace("\x00", ""))
        except:
            ghc += "{:35s}{}\n". format("   SSID",      "Unknown")

        # 85
        try:
            CFG_PASSWORD    = cfg[ 85 : 85 + 16 ].decode("UTF-8")
            ghc += "{:35s}{}\n". format("   Password",  CFG_PASSWORD.replace("\x00", ""))
        except:
            ghc += "{:35s}{}\n". format("   Password",  "Unknown")

        # 101
        try:
            CFG_WEBSITE     = cfg[ 101 : 101 + 25 ].decode("UTF-8")
            ghc += "{:35s}{}\n". format("   Website",   CFG_WEBSITE.replace("\x00", ""))
        except:
            ghc += "{:35s}{}\n". format("   Website",   "Unknown")

        # 126
        try:
            CFG_URL         = cfg[ 126 : 126 + 12 ].decode("UTF-8")
            ghc += "{:35s}{}\n". format("   URL",       CFG_URL.replace("\x00", ""))
        except:
            ghc += "{:35s}{}\n". format("   URL",       "Unknown")

        # 138
        try:
            CFG_UserID      = cfg[ 138 : 138 + 12 ].decode("UTF-8")
            ghc += "{:35s}{}\n". format("   UserID",    CFG_UserID.replace("\x00", ""))
        except:
            ghc += "{:35s}{}\n". format("   UserID",    "Unknown")

        # 150
        try:
            CFG_CounterID   = cfg[ 150 : 150 + 12 ].decode("UTF-8")
            ghc += "{:35s}{}\n". format("   CounterID", CFG_CounterID.replace("\x00", ""))
        except:
            ghc += "{:35s}{}\n". format("   CounterID", "Unknown")

        # 112
        try:
            CFG_Period      = cfg[ 112]
            ghc += "{:35s}{}\n". format("   Period (min)", CFG_Period)
        except:
            ghc += "{:35s}{}\n". format("   Period (min)", "Unknown")

        # 113
        try:
            CFG_WIFIONOFF   = cfg[ 113]
            ghc += "{:35s}{}\n". format("   WiFiOnOff", CFG_WIFIONOFF)
        except:
            ghc += "{:35s}{}\n". format("   WiFiOnOff ", "Unknown")

        if gglobs.devel:    # show only in development mode
            # 114
            try:
                rec = cfg[ 114 : 114 + 6 ] # CFG_Save_DateTimeStamp
                dt  = datetime.datetime(rec[0] + 2000, rec[1], rec[2], rec[3], rec[4], rec[5])
                ghc += "{:35s}{}\n". format("Save_DateTimeStamp", dt)
            except:
                ghc += "{:35s}{}\n". format("Save_DateTimeStamp", "ERROR: incorrect DateTime stamp")
                dprint(gglobs.debug, "Save_DateTimeStamp", "ERROR: incorrect DateTime stamp at pos #d264")


    else: # 300 series, version 4
        ghc += "{:35s}{}\n". format("   None with the connected device", "")

        if gglobs.devel:    # show only in development mode
            # 0x45 = 69 ?
            # 0x3e = 62 ?
            try:
                # stated by ZLM to be at 0x45=69, but in my 300E is at 0x3E=62 !
                # rec = cfg[ 0x45 : 0x45 + 6 ] # CFG_Save_DateTimeStamp - WRONG for 300E+
                rec = cfg[ 0x3E : 0x3E + 6 ] # CFG_Save_DateTimeStamp for 300E+
                #print("rec[45:45+6]:", rec)
                dt  = datetime.datetime(rec[0] + 2000, rec[1], rec[2], rec[3], rec[4], rec[5])
                ghc += "{:35s}{}\n". format("Save_DateTimeStamp", dt)
            except:
                ghc += "{:35s}{}\n". format("Save_DateTimeStamp", "ERROR: incorrect DateTime stamp")
                dprint(gglobs.debug, "Save_DateTimeStamp", "ERROR: incorrect DateTime stamp at pos #d62: ", rec)

    return ghc[:-1]


def ftextCFG():
    """Return device configuration as formatted text"""

    cfg, error, errmessage = getCFG()
    #print("RawCfg: \n", BytesAsHex(cfg))
    fText                  = ""

    if cfg == None:
        fText += errmessage

    elif error < 0 and len(cfg) not in (256, 512):
        fText += errmessage

    else: # if len(cfg) == 256 or len(cfg) == 512 even if error
        lencfg  = len(cfg)
        fText  += "The configuration is:  (Format: dec byte_number: hex value=dec value)\n"

        cfg     = cfg.rstrip(b'\xFF')       # remove the right side FF values
        #print("RawCfg: after FF strip\n", BytesAsHex(cfg))
        if len(cfg) == 0:
            return "ERROR: Configuration is empty. Try a factory reset!"

        lencfg_strp = len(cfg)
        for i in range(0, lencfg_strp, 6):
            pcfg = ""
            for j in range(0, 6):
                k = i+j
                if k < lencfg_strp: pcfg += "%3d:%02x=%3d |" % (k, cfg[k], cfg[k])
            fText += pcfg[:-2] + "\n"

        if lencfg_strp < lencfg:
            fText += "Remaining {} values up to address {} are all 'ff=255'\n".format(lencfg -lencfg_strp, lencfg - 1)

        fText += "The configuration as ASCII is (non-ASCII characters as '.'):\n" + BytesAsASCII(cfg)

    return fText


def ftextSettings():
    """Return device settings as formatted text"""

    si  = ""
    fmt = "{:35s}{}\n"
    if gglobs.deviceDetected != "auto":
        si += fmt.format("   Memory (bytes):",                "{:,}"   .format(gglobs.memory))
        si += fmt.format("   SPIRpage Size (bytes):",         "{:,}"   .format(gglobs.SPIRpage))
        si += fmt.format("   SPIRbugfix: (True | False)",     "{:}"    .format(gglobs.SPIRbugfix))
        si += fmt.format("   Config Size (bytes):",           "{:}"    .format(gglobs.configsize))
        si += fmt.format("   Calibration (µSv/h / CPM):",      str(gglobs.calibration))
        si += fmt.format("   Voltagebytes (1 | 5):",          "{:}"    .format(gglobs.voltagebytes))
        si += fmt.format("   Endianness: (big | little)",     "{:}"    .format(gglobs.endianness))

    return si[:-1]


def ftextCalibration():
    """extract Calibration from device"""

    cfg = gglobs.cfg
    #print("RawCfg:", BytesAsHex(cfg))

    try:
        cal_CPM = []
        cal_CPM.append(struct.unpack(">H", cfg[ 8:10] )[0])
        cal_CPM.append(struct.unpack(">H", cfg[14:16] )[0])
        cal_CPM.append(struct.unpack(">H", cfg[20:22] )[0])

        if gglobs.endianness == 'big':
            #print "using 500er, 600er:  use big-endian"
            fString = ">f"
        else:
            #print "using other than 500er and 600er: use little-endian"
            fString = "<f"

        cal_uSv = []
        cal_uSv.append(struct.unpack(fString,  cfg[10:14] )[0])
        cal_uSv.append(struct.unpack(fString,  cfg[16:20] )[0])
        cal_uSv.append(struct.unpack(fString,  cfg[22:26] )[0])

        #print( cal_CPM)
        #print( cal_uSv)

        ftext  = "Device Calibration Points:\n"
        #ftext += "{:35s}{:0.6f} µSv/h / CPM\n".format("   GeigerLog setting:", gglobs.calibration)
        #ftext += "   Device setting:\n"

        for i in range(0,3):
            ftext += "   Calibration Point {:}: {:6d} CPM ={:7.2f} µSv/h ({:0.6f} µSv/h / CPM)\n".format(i + 1, cal_CPM[i], cal_uSv[i], cal_uSv[i] / cal_CPM[i])

    except Exception as e:
        srcinfo = "Device Calibration"
        exceptPrint(e, sys.exc_info(), srcinfo)
        ftext = "{:35s}{:s}\n".format("Device Calibration:", "Unknown")

    return ftext[:-1] # remove last newline char



def getDeviceProperties():
    """define a device and its parameters"""

    # GETVER            Model               Firmware  (observed)
    # GMC-300Re 3.xx,   GMC-300             Firmware: 3.xx  (3.20)
    #                   GMC-300E            existing?
    # GMC-300Re 4.xx,   GMC-300E+           Firmware: 4.xx  (4.20, 4.22)
    #                   GMC-320             existing?
    # GMC-320Re 4.xx,   GMC-320+            Firmware: 4.xx  (4.19)
    # GMC-320Re 5.xx,   GMC-320+V5 (WiFi)   Firmware: 5.xx
    # GMC-500Re 1.xx,   GMC-500 and 500+    Firmware: 1.xx  (1.00, 1.08)
    # GMC-600Re 1.xx,   GMC-600 and 600+    Firmware: 1.xx
    #
    # see: http://www.gqelectronicsllc.com/forum/topic.asp?TOPIC_ID=4948 Reply #30
    # Quote EmfDev:
    # "On the 500 and 600 series, the GETVER return can be any length.
    # So far its only 14 bytes or 15 bytes. But it should return any given
    # model name completely so the length is variable.
    # And the '+' sign is included in the model name. e.g. GMC500+Re 1.10
    # But I don't think the 300 or 320 has been updated so maybe you can ask
    # support for the fix."

    dprint(gglobs.debug, "getDeviceProperties: of connected device: '{}'".format(gglobs.deviceDetected))
    debugIndent(1)

    if "GMC-300Re 3." in gglobs.deviceDetected :
        #######################################################################
        # the "GMC-300" delivers the requested page after ANDing with 0fff
        # hence when you request 4k (=1000hex) you get zero
        # therefore use pagesize 2k only
        #######################################################################
        memory               = 2**16
        SPIRpage             = 2048
        SPIRbugfix           = False
        configsize           = 256
        calibration          = 0.0065
        voltagebytes         = 1
        endianness           = 'little'

    elif "GMC-300Re 4." in gglobs.deviceDetected:
        #######################################################################
        # when using a page of 4k, you need the datalength workaround in
        # gcommand, i.e. asking for 1 byte less
        #######################################################################
        memory               = 2**16
        SPIRpage             = 4096
        SPIRbugfix           = True
        configsize           = 256
        calibration          = 0.0065
        voltagebytes         = 1
        endianness           = 'little'

    elif "GMC-320Re 4." in gglobs.deviceDetected:
        #######################################################################
        #
        #######################################################################
        memory               = 2**20
        SPIRpage             = 4096
        SPIRbugfix           = True
        configsize           = 256
        calibration          = 0.0065
        voltagebytes         = 1
        endianness           = 'little'

    elif "GMC-320Re 5." in gglobs.deviceDetected:
        #######################################################################
        #
        #######################################################################
        memory               = 2**20
        SPIRpage             = 4096
        SPIRbugfix           = True
        configsize           = 256
        calibration          = 0.0065
        voltagebytes         = 1
        endianness           = 'little'

    elif "GMC-500Re 1." in gglobs.deviceDetected:
        #######################################################################
        #
        #######################################################################
        memory               = 2**20
        #SPIRpage            = 4096  # ist bug jetzt behoben oder auf altem Stand???
        SPIRpage             = 2048   # Workaround erstmal auf 2048 bytes
        SPIRbugfix           = False
        configsize           = 512
        calibration          = 0.0065
        voltagebytes         = 5
        endianness           = 'big'

    elif "GMC-500+Re 1." in gglobs.deviceDetected:
        #######################################################################
        #
        #######################################################################
        memory               = 2**20
        #SPIRpage            = 4096  # ist bug jetzt behoben oder auf altem Stand???
        SPIRpage             = 2048   # Workaround erstmal auf 2048 bytes
        SPIRbugfix           = False
        configsize           = 512
        calibration          = 0.0065
        voltagebytes         = 5
        endianness           = 'big'

    elif "GMC-600Re 1." in gglobs.deviceDetected:
        #######################################################################
        #
        #######################################################################
        memory               = 2**20
        #SPIRpage            = 4096  # ist bug jetzt behoben oder auf altem Stand???
        SPIRpage             = 2048   # Workaround erstmal auf 2048 bytes
        SPIRbugfix           = False
        configsize           = 512
        calibration          = 0.0065
        voltagebytes         = 5
        endianness           = 'big'

    elif "GMC-600+Re 1." in gglobs.deviceDetected:
        #######################################################################
        #
        # Amazon:   https://www.amazon.de/gmc-600-Plus-Geiger-Counter-Detektor-Dosimeter/dp/B077V7QSHP
        #           Hohe Empfindlichkeit Pancake Geiger Röhre LND 7317 installiert
        # LND 7317: https://shop.kithub.cc/products/pancake-geiger-mueller-tube-lnd-7317
        #           Gamma sensitivity Co60 (cps/mr/hr) 58
        # SBM20 :   http://www.gstube.com/data/2398/
        #           Gamma Sensitivity Ra226 (cps/mR/hr) : 29
        #           Gamma Sensitivity Co60 (cps/mR/hr) : 22
        #######################################################################
        memory               = 2**20
        #SPIRpage            = 4096  #  ist bug jetzt behoben oder auf altem Stand???
        SPIRpage             = 2048   # Workaround erstmal auf 2048 bytes
        # re calib: see user Kaban here: http://www.gqelectronicsllc.com/forum/topic.asp?TOPIC_ID=4948
        SPIRbugfix           = False
        configsize           = 512
        calibration          = 0.002637
        voltagebytes         = 5
        endianness           = 'big'

    else: # If none of the above match, then this will be reached
        #######################################################################
        # to integrate as of now unknown new (or old) devices
        #######################################################################
        dprint(True, "getDeviceProperties: New, unknown device has been connected:", gglobs.deviceDetected)
        bell()
        memory               = 2**20
        SPIRpage             = 2048
        SPIRbugfix           = False
        configsize           = 512
        calibration          = 0.0065
        voltagebytes         = 5
        endianness           = 'big'

    if gglobs.memory        == 'auto':     gglobs.memory        = memory
    if gglobs.SPIRpage      == 'auto':     gglobs.SPIRpage      = SPIRpage
    if gglobs.SPIRbugfix    == 'auto':     gglobs.SPIRbugfix    = SPIRbugfix
    if gglobs.configsize    == 'auto':     gglobs.configsize    = configsize
    if gglobs.calibration   == 'auto':     gglobs.calibration   = calibration
    if gglobs.voltagebytes  == 'auto':     gglobs.voltagebytes  = voltagebytes
    if gglobs.endianness    == 'auto':     gglobs.endianness    = endianness

    debugIndent(0)


def test1():
    """Test to comply with EmfDev request from Reply #36 in
    http://www.gqelectronicsllc.com/forum/topic.asp?TOPIC_ID=4948
    """

    """
    EmfDev:
    Can you please try to
    reboot(and
    reconnect) the unit, then try to
    restart
    your software and
    make sure the pipeline is clean maybe clear it before
    sending update.
    They try to send only the CFGUPDATE command after restart
    and nothing else to verify if the return is still 7 bytes.
    """

    dprint(gglobs.debug, "test1: Update Config")
    debugIndent(1)
    extra  = getExtraByte()
    dprint(gglobs.debug, "now updating")
    debugIndent(1)
    rec = updateConfig()
    debugIndent(0)
    debugIndent(0)
