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
__copyright__       = "Copyright 2016, 2017, 2018, 2019, 2020"
__credits__         = ["Phil Gillaspy", "GQ"]
__license__         = "GPL3"

# credits:
# device command coding taken from:
# Phil Gillaspy, https://sourceforge.net/projects/gqgmc/
# and GQ document 'GQ-RFC1201.txt'
# (GQ-RFC1201,GQ Geiger Counter Communication Protocol, Ver 1.40 Jan-2015)
# and GQ's disclosure at:
# http://www.gqelectronicsllc.com/forum/topic.asp?TOPIC_ID=4948

from   gutils           import *

#
# Commands and functions implemented in device
#

def getVER():
    # Get hardware model and version
    # send <GETVER>> and read 14 bytes
    # returns total of 14 bytes ASCII chars from GQ GMC unit.
    # includes 7 bytes hardware model and 7 bytes firmware version.
    # e.g.: 'GMC-300Re 4.20'
    # ATTENTION: new counters may deliver 15 bytes. e.g. "GMC-500+Re 1.18",
    # the 500 version with firmware 1.18

    dprint("getVER:")
    setDebugIndent(1)
    recd    = None

    rec, error, errmessage = serialCOMM(b'<GETVER>>', 14, orig(__file__))
    #for i in range(0,14):
    #    print("i={:2d}  rec={:08b}  rec={:02X}".format(i, rec[i], rec[i]))

    if error >= 0:
        try:
            recd = rec.decode('UTF-8')    # convert from bytes to str
        except Exception as e:
            error      = -1
            errmessage = "ERROR getting Version - Bytes are not ASCII: " + str(rec)
            exceptPrint(e, sys.exc_info(), errmessage)
            recd       = str(rec)

    # FOR TESTING ONLY - start GL with command: 'testing'
    if gglobs.testing:
        pass
        #recd = "GMC-300Re 3.20"
        #recd = "GMC-300Re 4.20"
        #recd = "GMC-300Re 4.22"
        recd = "GMC-320Re 3.22"     # device used by user katze
        #recd = "GMC-320Re 4.19"
        #recd = "GMC-320Re 5.xx"
        #recd = "GMC-500Re 1.00"
        #recd = "GMC-500Re 1.08"
        #recd = "GMC-500+Re 1.0x"
        #recd = "GMC-500+Re 1.18"
        #recd = "GMC-600Re 1.xx"
        #recd = "GMC-600+Re 2.xx"    # fictitious device; not (yet) existing
                                     # simulates the bug in the 'GMC-500+Re 1.18'
        #recd = ""

    try:
        lenrec = len(rec)
    except:
        lenrec = None

    dprint("getVER: len:{}, rec:\"{}\", recd='{}', err={}, errmessage='{}'".format(lenrec, rec, recd, error, errmessage))

    setDebugIndent(0)

    return (recd, error, errmessage)


def getValuefromRec(rec, maskHighBit=False):
    """calclate the CPM, CPS value from a record"""

    if gglobs.nbytes == 2 and maskHighBit==True:
        value = (rec[0] & 0x3f) << 8 | rec[1]

    elif gglobs.nbytes == 2 and maskHighBit==False:
        value = rec[0]<< 8 | rec[1]

    elif gglobs.nbytes == 4 :
        value = ((rec[0]<< 8 | rec[1]) << 8 | rec[2]) << 8 | rec[3]

    return value


def getGMCValues(varlist):
    """return all values in the varlist
    NOTE: the getC* functions all return (value, error, errmessage)
          now only value will be forwarded
    """

    alldata = {}

    if not gglobs.GMCConnection: # GMCcounter  is NOT connected!
        dprint("getGMCValues: GMC Counter is not connected")
        return alldata

    if varlist == None:
        return alldata

    for vname in varlist:
        if   vname == "CPM":     alldata[vname] = getCPM() [0]  # counts per MINUTE
        elif vname == "CPS":     alldata[vname] = getCPS() [0]  # counts per SECOND
        elif vname == "CPM1st":  alldata[vname] = getCPML()[0]  # CPM from 1st tube, normal tube
        elif vname == "CPS1st":  alldata[vname] = getCPSL()[0]  # CPS from 1st tube, normal tube
        elif vname == "CPM2nd":  alldata[vname] = getCPMH()[0]  # CPM from 2nd tube, extra tube
        elif vname == "CPS2nd":  alldata[vname] = getCPSH()[0]  # CPS from 2nd tube, extra tube
        elif vname == "X":       alldata[vname] = getDateTimeAsNum() # time as read from device

    vprint("{:20s}:  Variables:{}  Data:{}".format("getGMCValues", varlist, alldata))

    return alldata


def getCPM():
    # Get current CPM value
    # send <GETCPM>> and read 2 bytes
    # In total 2 bytes data are returned from GQ GMC unit
    # as a 16 bit unsigned integer.
    # The first byte is MSB byte data and second byte is LSB byte data.
    # e.g.: 00 1C  -> the returned CPM is 28
    # e.g.: 0B EA  -> the returned CPM is 3050
    #
    # return CPM, error, errmessage

    wprint("getCPM: standard command")
    setDebugIndent(1)

    value = gglobs.NAN
    rec, error, errmessage = serialCOMM(b'<GETCPM>>', gglobs.nbytes, orig(__file__))
    if error >= 0:
        value = getValuefromRec(rec, maskHighBit=False)
        value = scaleVarValues("CPM", value, gglobs.ValueScale["CPM"])

    wprint("getCPM: rec= {}, value= {}, err= {}, errmsg= {}".format(rec, value, error, errmessage ))

    setDebugIndent(0)
    return (value, error, errmessage)


def getCPS():
    # Get current CPS value
    # send <GETCPS>> and read 2 bytes
    # In total 2 bytes data are returned from GQ GMC unit
    #
    # Comment from Phil Gallespy:
    # 1st byte is MSB, but note that upper two bits are reserved bits.
    # cps_int |= ((uint16_t(cps_char[0]) << 8) & 0x3f00);
    # cps_int |=  (uint16_t(cps_char[1]) & 0x00ff);
    # my observation: highest bit in MSB is always set!
    # e.g.: 80 1C  -> the returned CPS is 28
    # e.g.: FF FF  -> = 3F FF -> the returned maximum CPS is 16383
    #                 or 16383 * 60 = 982980 CPM
    #
    # return CPS, error, errmessage

    wprint("getCPS: standard command")
    setDebugIndent(1)

    value = gglobs.NAN
    rec, error, errmessage = serialCOMM(b'<GETCPS>>', gglobs.nbytes, orig(__file__))
    if error >= 0:
        value = getValuefromRec(rec, maskHighBit=True)
        value = scaleVarValues("CPS", value, gglobs.ValueScale["CPS"])

    wprint("getCPS: rec=", rec, ", value=", value)

    setDebugIndent(0)
    return (value, error, errmessage)


def getCPML():
    """get CPM from High Sensitivity tube that should be the 'normal' tube"""

    wprint("getCPML: 1st tube, HIGH sensitivity")
    setDebugIndent(1)

    value = gglobs.NAN
    rec, error, errmessage = serialCOMM(b'<GETCPML>>', gglobs.nbytes, orig(__file__))
    if error >= 0:
        value = getValuefromRec(rec, maskHighBit=False)
        value = scaleVarValues("CPM1st", value, gglobs.ValueScale["CPM1st"])

    wprint("getCPML: rec=", rec, ", value=", value)

    setDebugIndent(0)
    return (value, error, errmessage)


def getCPMH():
    """get CPM from Low Sensitivity tube that should be the 2nd tube in the 500+"""

    wprint("getCPMH: 2nd tube, LOW sensitivity")
    setDebugIndent(1)

    value = gglobs.NAN
    rec, error, errmessage = serialCOMM(b'<GETCPMH>>', gglobs.nbytes, orig(__file__))
    if error >= 0:
        value = getValuefromRec(rec, maskHighBit=False)
        value = scaleVarValues("CPM2nd", value, gglobs.ValueScale["CPM2nd"])

    wprint("getCPMH: rec=", rec, ", value=", value)

    setDebugIndent(0)
    return (value, error, errmessage)



def getCPSL():
    """get CPS from High Sensitivity tube that should be the 'normal' tube"""

    wprint("getCPSL: 1st tube, HIGH sensitivity")
    setDebugIndent(1)

    value = gglobs.NAN
    rec, error, errmessage = serialCOMM(b'<GETCPSL>>', gglobs.nbytes, orig(__file__))
    if error >= 0:
        value = getValuefromRec(rec, maskHighBit=True)
        value = scaleVarValues("CPS1st", value, gglobs.ValueScale["CPS1st"])

    wprint("getCPSL: rec=", rec, ", value=", value)

    setDebugIndent(0)
    return (value, error, errmessage)


def getCPSH():
    """get CPS from Low Sensitivity tube that should be the 2nd tube in the 500+"""

    wprint("getCPSH: 2nd tube, LOW sensitivity")
    setDebugIndent(1)

    value = gglobs.NAN
    rec, error, errmessage = serialCOMM(b'<GETCPSH>>', gglobs.nbytes, orig(__file__))
    if error >= 0:
        value = getValuefromRec(rec, maskHighBit=True)
        value = scaleVarValues("CPS2nd", value, gglobs.ValueScale["CPS2nd"])

    wprint("getCPSH: rec=", rec, ", value=", value)

    setDebugIndent(0)
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

    dprint("turnHeartbeatOn:")
    setDebugIndent(1)

    if gglobs.GMCser == None:
        rec         = ""
        error       = 1
        errmessage  = "No serial connection"
    else:
        rec, error, errmessage = serialCOMM(b'<HEARTBEAT1>>', 0, orig(__file__))

    dprint("turnHeartbeatOn: rec='{}', err={}, errmessage='{}'".format(rec, error, errmessage))

    setDebugIndent(0)

    return (rec, error, errmessage)


def turnHeartbeatOFF():
    # 4. Turn off the GQ GMC heartbeat
    # Command:  <HEARTBEAT0>>
    # Return:   None
    # Firmware supported:  Re.2.10 or later

    dprint("turnHeartbeatOFF:")
    setDebugIndent(1)

    if gglobs.GMCser == None:
        rec         = ""
        error       = 1
        errmessage  = "No serial connection"

    else:
        rec, error, errmessage = serialCOMM(b'<HEARTBEAT0>>', 0, orig(__file__))

    dprint("turnHeartbeatOFF: rec='{}', err={}, errmessage='{}'".format(rec, error, errmessage))

    setDebugIndent(0)

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

    dprint("getVOLT:")
    setDebugIndent(1)

    if gglobs.GMCser == None:
        rec         = ""
        error       = 1
        errmessage  = "No serial connection"

    else:
        rec, error, errmessage = serialCOMM(b'<GETVOLT>>', gglobs.voltagebytes, orig(__file__))
        dprint("getVOLT: VOLT: raw:", rec)

        ######## TESTING (uncomment all 4) #############
        #rec         = b'3.76v'              # 3.76 Volt
        #error       = 1
        #errmessage  = "testing"
        #dprint("getVOLT: TESTING with rec=", rec, debug=True)
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

    dprint("getVOLT: Using config setting voltagebytes={}:  Voltage='{}', err={}, errmessage='{}'".format(gglobs.voltagebytes, rec, error, errmessage))
    setDebugIndent(0)

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

    dprint("getSPIR: SPIR requested: address: {:5d}, datalength:{:5d}   (hex: address: {:02x} {:02x} {:02x}, datalength: {:02x} {:02x})".format(address, datalength, ad[0], ad[1], ad[2], dl[0], dl[1]))
    setDebugIndent(1)

    rec, error, errmessage = serialCOMM(b'<SPIR' + ad + dl + b'>>', datalength, orig(__file__)) # returns bytes

    if rec != None :
        msg = "datalength={:4d}".format(len(rec))
    else:
        msg = "ERROR: No data received!"

    dprint("getSPIR: received: {}, err={}, errmessage='{}'".format(msg, error, errmessage))
    setDebugIndent(0)

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
        rec = gglobs.GMCser.read(2)
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
        bytesWaiting = gglobs.GMCser.in_waiting
    except:
        #print("---------------------getExtraByte: failed try")
        bytesWaiting = 0

    #bytesWaiting += 5   # TESTING ONLY
    if bytesWaiting == 0:
        wprint("getExtraByte: No extra bytes waiting for reading")
    else:
        vprint("getExtraByte: Bytes waiting: {}".format(bytesWaiting), verbose=True)
        while True:                # read single byte until nothing is returned
            try:
                x = gglobs.GMCser.read(1)
            except Exception as e:
                edprint("getExtraByte: Exception: {}".format(e))
                exceptPrint(e, sys.exc_info(), "getCFG: Exception: ")
                x = 0

            if len(x) == 0: break
            xrec += x

        vprint("getExtraByte: Got {} extra bytes from reading-pipeline:".format(len(xrec)), list(xrec), verbose=True)
        vprint("getExtraByte: Extra bytes as ASCII: '{}'".format(BytesAsASCII(xrec)), verbose=True)

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

    # http://www.gqelectronicsllc.com/forum/topic.asp?TOPIC_ID=5278, Reply #47
    # bBatteryType: 1 is non rechargeable. 0 is chargeable.
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

    dprint("getCFG:")
    setDebugIndent(1)

    getExtraByte()  # cleaning buffer before getting cfg (some problem in the 500)

    cfg         = b""
    error       = 0
    errmessage  = ""

    cfg, error, errmessage = serialCOMM(b'<GETCFG>>', gglobs.configsize, orig(__file__))
    #print("getCFG: cfg:", cfg, type(cfg))

    ####### BEGIN TESTDATA ####################################################
    # replaces rec with data from other runs
    # requires that a testdevice was activated in getVER; the only relevant
    # prperty is the length of config
    if gglobs.testing: # only do this when command line command testing was used
        if gglobs.configsize == 512:
            # using a 512 bytes sequence; data from a GMC-500(non-plus) readout
            #
            # power is OFF:
            cfg500 = "01 00 00 02 1F 00 00 64 00 3C 3E C7 AE 14 27 10 42 82 00 00 00 19 41 1C 00 00 00 3F 00 00 00 00 02 02 00 00 00 00 FF FF FF FF FF FF 00 01 00 78 0A FF FF 3C 00 05 FF 01 00 00 0A 00 01 0A 00 64 00 3F 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 77 77 77 2E 67 6D 63 6D 61 70 2E 63 6F 6D 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 6C 6F 67 32 2E 61 73 70 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 02 00 02 11 05 1E 10 34 05 FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF".split(' ')
            # power is ON:
            cfg500 = ["0"] + cfg500[1:]
            #print("cfg500:\n", len(cfg500), cfg500)

            cfg = b''
            for a in cfg500:       cfg += bytes([int(a, 16)])

        elif "GMC-320Re 5." in gglobs.GMCdeviceDetected :  # 320v5 device (with WiFi)
            cfg = (cfg[:69] + b'abcdefghijklmnopqrstuvwxyz0123456789' * 10)[:256] # to simulate WiFi settings

        elif gglobs.configsize == 256: # 320v4 device
            # next line from 320+ taken on: 2017-05-26 15:29:38
            # power is off:
            cfg320plus = [255, 0, 0, 2, 31, 0, 0, 100, 0, 60, 20, 174, 199, 62, 0, 240, 20, 174, 199, 63, 3, 232, 0, 0, 208, 64, 0, 0, 0, 0, 63, 0, 2, 2, 0, 0, 0, 0, 255, 255, 255, 255, 255, 255, 0, 1, 0, 120, 25, 255, 255, 60, 1, 8, 255, 1, 0, 254, 10, 0, 1, 10, 0, 100, 0, 0, 0, 0, 63, 17, 5, 23, 16, 46, 58, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255]
            # power is on:
            cfg320plus = [  0] + cfg320plus[1:]

            cfg = b''
            for a in cfg320plus:       cfg += bytes([a])

        else:
            #cfg = rec
            pass

        print("TESTDATA: cfg:", len(cfg), type(cfg), "\n", BytesAsHex(cfg))

        #rec         = cfg # simulates a return from GETCFG
        error       = 1
        errmessage  = "SIMULATION"
    ####### END TESTDATA ######################################################

    if cfg != None:
        dprint("getCFG: Got {} bytes as {}"  .format(len(cfg), type(cfg)))
        dprint("getCFG: CFG as HEX  : {}"    .format(BytesAsHex(cfg)))
        dprint("getCFG: CFG as DEC  : {}"    .format(BytesAsDec(cfg)))
        dprint("getCFG: CFG as ASCII: {}"    .format(BytesAsASCII(cfg)))

        if gglobs.endianness == 'big':
            #print "using 500er, 600er:  use big-endian"
            fString = ">f"
        else:
            #print "using other than 500er and 600er: use little-endian"
            fString = "<f"

        try:
            for key in gglobs.cfgLowKeys:
                gglobs.cfgLow[key] = cfg[gglobs.cfgLowndx[key][0] :  gglobs.cfgLowndx[key][1]]
        except Exception as e:
            edprint("getCFG: Exception: cfgLow[key]: {}".format(e))
            exceptPrint(e, sys.exc_info(), "getCFG: Exception: ")
            return cfg, -1, "getCFG: Exception: {}".format(e)


        #print("cfgLow: len: ", len(gglobs.cfgLow))
        #for key in gglobs.cfgLowKeys:            print("{:15s} {}".format(key, gglobs.cfgLow[key]))
        #print("cfgLow['Speaker']: len: ", len(gglobs.cfgLow["Speaker"]), gglobs.cfgLow["Speaker"])
        #print("gglobs.cfgLow['Speaker'][0]", gglobs.cfgLow["Speaker"][0])

        try:
            #  ("Power", "Alarm", "Speaker", "CalibCPM_0", "CalibuSv_0", "CalibCPM_1", "CalibuSv_0", "CalibCPM_2", "CalibuSv_0", "SaveDataType", "MaxCPM", "Baudrate", "Battery")
            gglobs.cfgLow["Power"]          = gglobs.cfgLow["Power"]        [0]
            gglobs.cfgLow["Alarm"]          = gglobs.cfgLow["Alarm"]        [0]
            gglobs.cfgLow["Speaker"]        = gglobs.cfgLow["Speaker"]      [0]
            gglobs.cfgLow["SaveDataType"]   = gglobs.cfgLow["SaveDataType"] [0]
            gglobs.cfgLow["Baudrate"]       = gglobs.cfgLow["Baudrate"]     [0]
            gglobs.cfgLow["Battery"]        = gglobs.cfgLow["Battery"]      [0]

            gglobs.cfgLow["CalibCPM_0"]     = struct.unpack(">H",    gglobs.cfgLow["CalibCPM_0"] )[0]
            gglobs.cfgLow["CalibCPM_1"]     = struct.unpack(">H",    gglobs.cfgLow["CalibCPM_1"] )[0]
            gglobs.cfgLow["CalibCPM_2"]     = struct.unpack(">H",    gglobs.cfgLow["CalibCPM_2"] )[0]

            gglobs.cfgLow["CalibuSv_0"]     = struct.unpack(fString, gglobs.cfgLow["CalibuSv_0"] )[0]
            gglobs.cfgLow["CalibuSv_1"]     = struct.unpack(fString, gglobs.cfgLow["CalibuSv_1"] )[0]
            gglobs.cfgLow["CalibuSv_2"]     = struct.unpack(fString, gglobs.cfgLow["CalibuSv_2"] )[0]

            gglobs.cfgLow["MaxCPM"]         = struct.unpack(">H",    gglobs.cfgLow["MaxCPM"] )[0]

            gglobs.cfgLow["ThresholdMode"]  = gglobs.cfgLow["ThresholdMode"]      [0]
            gglobs.cfgLow["ThresholdCPM"]   = struct.unpack(">H",    gglobs.cfgLow["ThresholdCPM"] )[0]
            gglobs.cfgLow["ThresholduSv"]   = struct.unpack(fString, gglobs.cfgLow["ThresholduSv"] )[0]
        except Exception as e:
            edprint("getCFG: Exception: set cfgLow[key]: {}".format(e))
            exceptPrint(e, sys.exc_info(), "getCFG: Exception: ")
            return cfg, -1, "getCFG: Exception: set cfgLow[key]: {}".format(e)


        #print("cfgLow:")
        #for key in gglobs.cfgLowKeys:            print("{:15s} {}".format(key, gglobs.cfgLow[key]))
        #for i in range(0, 3): print("Calib#{:1d}  {}".format(i, gglobs.cfgLow["CalibuSv_{}".format(i)] / gglobs.cfgLow["CalibCPM_{}".format(i)]))

        # now get the WiFi part of the config
        #wifinames = ("SSID", "Password", "Website", "URL", "UserID", "CounterID", "Period")
        if gglobs.configsize == 512:
            for key in gglobs.cfgMapKeys:
                #print("key: ", key)
                try:
                    gglobs.cfgMap[key] = cfg[gglobs.cfg512ndx[key][0] :  gglobs.cfg512ndx[key][1]]      .decode("UTF-8").replace("\x00", "")
                    #gglobs.GMCmap[key] = gglobs.cfgMap[key]
                except Exception as e:
                    dprint("Failure getting gglobs.cfgMap[key] with key==", key, debug=True)
                    gglobs.cfgMap[key] = "ERROR INVALID"
                    #gglobs.GMCmap[key] = gglobs.cfgMap[key]
            #print("gglobs.cfgMap:", gglobs.cfgMap)


        elif "GMC-320Re 5." in gglobs.GMCdeviceDetected:  # 320v5 device
            for key in gglobs.cfgMapKeys:
                try:
                    gglobs.cfgMap[key] = cfg[gglobs.cfg256ndx[key][0] :  gglobs.cfg256ndx[key][1]]  .decode("UTF-8").replace("\x00", "")
                    #gglobs.GMCmap[key] = gglobs.cfgMap[key]
                except:
                    gglobs.cfgMap[key] = "ERROR INVALID"
                    #gglobs.GMCmap[key] = gglobs.cfgMap[key]

        else: # all other non-Wifi counters
            for key in gglobs.cfgMapKeys:
                gglobs.cfgMap[key] = "None"
                #gglobs.GMCmap[key] = gglobs.cfgMap[key]

    else:
        dprint("getCFG: ERROR: Failed to get any configuration data", debug=True)

    gglobs.cfg = cfg        # set the global value with whatever you got !!!

    setDebugIndent(0)

    return cfg, error, errmessage


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

    dprint("writeConfigData: cfgaddress: {}, value: {}".format(cfgaddress, value))
    setDebugIndent(1)

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
        msg  = "Number of configuration data inconsistent with detected device.<br>Updating config will NOT be done, as Device might be damaged by it!"
        fprint(msg, error=True)
        dprint("writeConfigData: " + msg.replace('<br>', ' '), debug=True)

        setDebugIndent(0)
        return


    # remove right side FFs; will be default after erasing
    cfgstrip = cfg.rstrip(b'\xFF')
    dprint("writeConfigData: Config right-stripped from FF: len:{}: ".format(len(cfgstrip)), BytesAsHex(cfgstrip))

    # modify config at cfgaddress
    cfgmod   = cfgstrip[:cfgaddress] + bytes([value]) + cfgstrip[cfgaddress + 1:]
    dprint("writeConfigData: Config mod @address: {};   new len:{}: ".format(cfgaddress, len(cfgmod)), BytesAsHex(cfgmod))

    # erase config
    dprint("WriteConfig: Erase Config")
    setDebugIndent(1)
    rec = serialCOMM(b'<ECFG>>', 1, orig(__file__))
    setDebugIndent(0)

    dprint("WriteConfig: Write new Config Data for Config Size:{}".format(doUpdate))
    if doUpdate == 256:
        pfs = "i=A0={:>3d}(0x{:02X}), cfgval=D0={:>3d}(0x{:02X})" # formatted print string
        # write config of up to 256 bytes
        for i, c in enumerate(cfgmod):

            A0 = bytes([i])
            D0 = bytes([c])
            vprint("WriteConfig: " + pfs.format(i, int.from_bytes(A0, byteorder='big'), c, int.from_bytes(D0, byteorder='big')))
            setDebugIndent(1)
            rec = serialCOMM(b'<WCFG' + A0 + D0 + b'>>', 1, orig(__file__))
            setDebugIndent(0)

    else: # doUpdate == 512
        pfs = "i==A0={:>3d}(0x{:03X}), cfgval==D0={:>3d}(0x{:02X})" # formatted print string
        # write config of up to 512 bytes
        for i, c in enumerate(cfgmod):
            A0 = struct.pack(">H", i)   # pack address into 2 bytes, big endian
            D0 = bytes([c])
            vprint("WriteConfig: " + pfs.format(i, int.from_bytes(A0, byteorder='big'), c, int.from_bytes(D0, byteorder='big')))
            setDebugIndent(1)
            rec = serialCOMM(b'<WCFG' + A0 + D0 + b'>>', 1, orig(__file__))
            setDebugIndent(0)

            # GMC-500 always times out at byte #11.
            # solved: it is a bug in the firmware; data resulted in ">>>"

    # update config
    dprint("WriteConfig: Update Config")
    setDebugIndent(1)
    rec = updateConfig()
    setDebugIndent(0)

    setDebugIndent(0)


def updateConfig():
    # 13. Reload/Update/Refresh Configuration
    # Command: <CFGUPDATE>>
    # Return: 0xAA
    # Firmware supported: GMC-280, GMC-300 Re.2.20 or later
    # in GMC-500Re 1.08 this command returns:  b'0071\r\n\xaa'
    # see http://www.gqelectronicsllc.com/forum/topic.asp?TOPIC_ID=4948 #40

    dprint("updateConfig:")
    setDebugIndent(1)

    rec, error, errmessage = serialCOMM(b'<CFGUPDATE>>', 1, orig(__file__))
    dprint("updateConfig: rec: ", rec)

    setDebugIndent(0)

    return rec, error, errmessage


def getSERIAL():
    # Get serial number
    # send <GETSERIAL>> and read 7 bytes
    # returns the serial number in 7 bytes
    # each nibble of 4 bit is a single hex digit of a 14 character serial number
    # e.g.: F488007E051234
    #
    # This routine returns the serial number as a 14 character ASCII string

    dprint("getSERIAL:")
    setDebugIndent(1)

    rec, error, errmessage  = serialCOMM(b'<GETSERIAL>>', 7, orig(__file__))
    dprint("getSERIAL: raw: rec: ", rec)

    if error == 0 or error == 1:  # Ok or Warning
        hexlookup = "0123456789ABCDEF"
        sn =""
        for i in range(0,7):
            n1   = ((rec[i] & 0xF0) >>4)
            n2   = ((rec[i] & 0x0F))
            sn  += hexlookup[n1] + hexlookup[n2]
        rec = sn
    dprint("getSERIAL: decoded:  ", rec)

    setDebugIndent(0)

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

    dprint("setDATETIME:")
    setDebugIndent(1)

    tl      = list(time.localtime())  # tl: [2018, 4, 19, 13, 2, 50, 3, 109, 1]
                                      # for: 2018-04-19 13:02:50
    tl0     = tl.copy()

    tl[0]  -= 2000
    tlstr   = b''
    for i in range(0,6):  tlstr += bytes([tl[i]])
    dprint("setDATETIME: now:", tl0[:6], ", coded:", tlstr)

    rec, error, errmessage = serialCOMM(b'<SETDATETIME'+ tlstr + b'>>', 1, orig(__file__))

    setDebugIndent(0)

    return (rec, error, errmessage)


def getDATETIME():
    # Get year date and time
    # send <GETDATETIME>> and read 7 bytes
    # returns 7 bytes data: YY MM DD HH MM SS 0xAA
    #
    # This routine returns date and time in the format:
    #       YYYY-MM-DD HH:MM:SS
    # e.g.: 2017-12-31 14:03:19

    dprint("getDATETIME:")
    setDebugIndent(1)

    # yields: rec: b'\x12\x04\x13\x0c9;\xaa' , len:7
    # for:           2018-04-19 12:57:59
    rec, error, errmessage = serialCOMM(b'<GETDATETIME>>', 7, orig(__file__))

    if rec == None:
        dprint("ERROR getting DATETIME from counter - nothing received - ", errmessage)
    else:
        dprint("getDATETIME: raw:", rec, ", len: "+str(len(rec)))

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
            dprint("ERROR getting DATETIME from counter: ", errmessage, debug=True)

        dprint("getDATETIME: ", rec)

    setDebugIndent(0)

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

    dprint("getTEMP:")
    setDebugIndent(1)

    rec, error, errmessage  = serialCOMM(b'<GETTEMP>>', 4, orig(__file__))

    # TESTING example for '-28.8 °C'
    #rec = b'\x1c\x08\x01\xaa'

    srec = ""
    for i in range(4): srec += "{}, ".format(rec[i])

    dprint("getTEMP: Temp raw: rec= {} (=dec: {}), err={}, errmessage='{}'".format(rec, srec[:-2], error, errmessage))

    if error == 0 or error == 1:  # Ok or Warning
        if "GMC-3" in gglobs.GMCdeviceDetected :   # all 300 series
            temp = rec[0] + rec[1]/10.0     # unclear: is  decimal part rec[1] single digit or a 2 digit?
                                            # 3 digit not possible as byte value is from 0 ... 255
                                            # expecting rec[1] always from 0 ... 9
            if rec[2] != 0 : temp *= -1
            if rec[1]  > 9 : temp  = "ERROR: Temp={} - illegal value found for decimal part of temperature={}".format(temp, rec[1])
            rec = temp

        elif   "GMC-5" in gglobs.GMCdeviceDetected \
            or "GMC-6" in gglobs.GMCdeviceDetected:  # GMC-500/600
            temp = rec[0] + rec[1]/10.0     # unclear: is  decimal part rec[1] single digit or a 2 digit?
                                            # 3 digit not possible as byte value is from 0 ... 255
                                            # expecting rec[1] always from 0 ... 9
            #if rec[2] <= 0 : temp *= -1     # guessing: value=1 looks like positive Temperature. Negative is??? Maybe not right at all
            if rec[2] != 0 : temp *= -1     # using the old definition again
            if rec[1]  > 9 : temp  = "ERROR: Temp={} - illegal value found for decimal part of temperature={}".format(temp, rec[1])
            rec = temp

        else: # perhaps even 200 series?
            rec = "UNDEFINED"

    dprint("getTEMP: Temp      rec= {}, err={}, errmessage='{}'".format(rec, error, errmessage))

    setDebugIndent(0)

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

    dprint("getGYRO:")
    setDebugIndent(1)

    rec, error, errmessage  = serialCOMM(b'<GETGYRO>>', 7, orig(__file__))
    dprint("getGYRO: raw: rec={}, err={}, errmessage='{}'".format(rec, error, errmessage))

    if error == 0 or error == 1:  # Ok or Warning
        x = rec[0] * 256 + rec[1]
        y = rec[2] * 256 + rec[3]
        z = rec[4] * 256 + rec[5]
        rec = "X=0x{:04x}, Y=0x{:04x}, Z=0x{:04x}   ({},{},{})".format(x,y,z,x,y,z)

    dprint("getGYRO: rec='{}', err={}, errmessage='{}'".format(rec, error, errmessage))

    setDebugIndent(0)

    return rec, error, errmessage


def setPOWEROFF():
    # 12. Power OFF
    # Command: <POWEROFF>>
    # Return: none
    # Firmware supported: GMC-280, GMC-300 Re.2.11 or later

    setDebugIndent(1)
    rec  = serialCOMM(b'<POWEROFF>>', 0, orig(__file__))
    dprint("setPOWEROFF:", rec)
    setDebugIndent(0)

    return rec


def setPOWERON():
    # 26. Power ON
    # Command: <POWERON>>
    # Return: none
    # Firmware supported: GMC-280, GMC-300, GMC-320 Re.3.10 or later

    setDebugIndent(1)
    rec  = serialCOMM(b'<POWERON>>', 0, orig(__file__))
    dprint("setPOWERON:", rec)
    setDebugIndent(0)

    return rec


def setREBOOT():
    # 21. Reboot unit
    # command: <REBOOT>>
    # Return: None
    # Firmware supported: GMC-280, GMC-300 Re.3.00 or later

    setDebugIndent(1)
    rec  = serialCOMM(b'<REBOOT>>', 0, orig(__file__))
    dprint("setREBOOT:", rec)
    setDebugIndent(0)

    return rec


def setFACTORYRESET():
    # 20. Reset unit to factory default
    # command: <FACTORYRESET>>
    # Return: 0xAA
    # Firmware supported: GMC-280, GMC-300 Re.3.00 or later

    setDebugIndent(1)
    rec  = serialCOMM(b'<FACTORYRESET>>', 1, orig(__file__))
    dprint("setFACTORYRESET:", rec)
    setDebugIndent(0)

    return rec


#
# Derived commands and functions
#

def getDateTimeAsNum():
    """reads the DateTime from the device, converts into a number, and returns
    the delta time in sec with 1 sec precision"""

    rec, error, errmessage = getDATETIME()
    if error < 0:
        #fprint("getDateTimeAsNum: Device Date & Time:", errmessage, error=True, debug=True)
        return gglobs.NAN
    else:
        delta = (mpld.datestr2num(str(rec)) - mpld.datestr2num(stime())) * 86400
        wprint("getDateTimeAsNum: str(rec):", str(rec), ", Delta:", delta)
        return round(delta, 0) # 1 sec precision


def isPowerOn():
    """Checks Power status in the configuration"""

    #PowerOnOff byte:
    #at config offset  : 0
    #300 series        : 0 for ON and 255 for OFF
    #http://www.gqelectronicsllc.com/forum/topic.asp?TOPIC_ID=4948  Reply #14
    #confirmed in Reply #17
    #500/600 series    : PowerOnOff byte: 0 for ON, and 1 for OFF

    c = gglobs.cfgLow["Power"]

    #print("gglobs.GMCdeviceDetected:", gglobs.GMCdeviceDetected)
    try:
        if "GMC-3" in gglobs.GMCdeviceDetected: # all 300series
            #print("GMC-3 in gglobs.GMCdeviceDetected")
            if   c == 0:            p = "ON"
            elif c == 255:          p = "OFF"
            else:                   p = c
        elif "GMC-5" in gglobs.GMCdeviceDetected or \
             "GMC-6" in gglobs.GMCdeviceDetected :  # 500, 500+, 600, 600+
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

    c = gglobs.cfgLow["Alarm"]

    if   c == 0:            p = "OFF"
    elif c == 1:            p = "ON"
    else:                   p = c

    return p


def isSpeakerOn():
    """Checks Speaker On status in the configuration
    Speaker at offset:2"""

    c = gglobs.cfgLow["Speaker"]

    if   c == 0:            p = "OFF"
    elif c == 1:            p = "ON"
    else:                   p = c

    return p


def getBatteryType():
    """Checks Battery Type in the configuration"""

    # cfg Offset Battery = 56
    # Battery Type: 1 is non rechargeable. 0 is chargeable.
    c = gglobs.cfgLow["Battery"]

    if   c == 0:            p = "ReChargeable"
    elif c == 1:            p = "Non-ReChargeable"
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

    try:
        sdt = gglobs.cfgLow["SaveDataType"]
    except:
        sdt = 9999

    #print "sdt:", sdt
    try:
        if sdt <= len(sdttxt):
            txt                 = sdttxt[sdt]
            gglobs.savedatatype = txt
            gglobs.savedataindex= sdt
        else:
            txt = "UNKNOWN"
    except:
        txt= "Error in getSaveDataType, undefined type: {}".format(sdt)

    return sdt, txt  # <number>, <text>


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

    dprint("getBAUDRATE:")
    setDebugIndent(1)

    if  "GMC-3" in gglobs.GMCdeviceDetected: # all 300series
        brdict  = {64:1200, 160:2400, 208:4800, 232:9600, 240:14400, 244:19200, 248:28800, 250:38400, 252:57600, 254:115200}

    elif "GMC-5" in gglobs.GMCdeviceDetected or \
         "GMC-6" in gglobs.GMCdeviceDetected :  # 500, 500+, 600, 600+
        brdict  = {0:115200, 1:1200, 2:2400, 3:4800, 4:9600, 5:14400, 6:19200, 7:28800, 8:38400, 9:57600}
    else:
        brdict  = {}

    #print("getBAUDRATE: cfg Baudrate:")
    #for key, value in sorted(brdict.items()):
    #    print ("      {:08b} {:3d} {:6d}".format(key, key, value))

    try:
        key = gglobs.cfgLow["Baudrate"]
        rec = brdict[key]
    except:
        key = -999
        rec = "ERROR: Baudrate cannot be determined"

    dprint("getBAUDRATE: " + str(rec) + " with gglobs.cfgLow[\"Baudrate\"]={}".format(key))

    setDebugIndent(0)

    return rec


def GMCquickPortTest(usbport):
    """Tests GMC usbport with the 2 baudrates 57600 and 115200 using the GMC
    command <GETVER>>.
    Returns:    -1 on comm error,
                 0 (zero) if no test is successful
                 first successful baudrate otherwise
    """

    dprint("GMCquickPortTest: testing 57600 and 115200 baudrate on port: '{}'".format(usbport))
    setDebugIndent(1)

    baudrate_found = 0
    if os.access(usbport, os.F_OK):  # test if file with name like '/dev/geiger' exists
        for baudrate in (115200, 57600):
            dprint("GMCquickPortTest: Trying baudrate:", baudrate, debug=True)
            try:
                QPTser = serial.Serial(usbport, baudrate, timeout=0.5, write_timeout=0.5)
                QPTser.write(b'<GETVER>>')
                rec = QPTser.read(14)   # may leave bytes in the pipeline, if GETVER has
                                        # more than 14 bytes as may happen in newer GMC counters
                while QPTser.in_waiting:
                    QPTser.read(1)
                    time.sleep(0.1)
                QPTser.close()
                if rec.startswith(b"GMC"):
                    dprint("GMCquickPortTest: Success with baudrate {} on port {}".format(baudrate, usbport), debug=True)
                    baudrate_found = baudrate
                    break

            except Exception as e:
                errmessage1 = "GMCquickPortTest: ERROR: Serial communication error on testing baudrate {} on port {}".format(baudrate, usbport)
                exceptPrint(e, sys.exc_info(), errmessage1)
                baudrate_found = -1
                break

    else:
        errmessage1 = "GMCquickPortTest: ERROR: Serial Port '{}' does not exist".format(usbport)
        edprint(errmessage1)
        baudrate_found = -1

    setDebugIndent(0)

    return baudrate_found


def GMCautoBAUDRATE(usbport):
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

    dprint("GMCautoBAUDRATE: Autodiscovery of baudrate on port: '{}'".format(usbport))
    setDebugIndent(1)

    baudrates = gglobs.GMCbaudrates
    baudrates.sort(reverse=True) # to start with highest baudrate
    for baudrate in baudrates:
        dprint("GMCautoBAUDRATE: Trying baudrate:", baudrate, debug=True)
        try:
            ABRser = serial.Serial(usbport, baudrate, timeout=0.5, write_timeout=0.5)
            ABRser.write(b'<GETVER>>')
            rec = ABRser.read(14) # may leave bytes in the pipeline, if GETVER has
                                  # more than 14 bytes as may happen in newer counters
            while ABRser.in_waiting:
                ABRser.read(1)
                time.sleep(0.1)
            ABRser.close()
            if rec.startswith(b"GMC"):
                dprint("GMCautoBAUDRATE: Success with {}".format(baudrate), debug=True)
                break

        except Exception as e:
            errmessage1 = "GMCautoBAUDRATE: ERROR: GMCautoBAUDRATE: Serial communication error on finding baudrate"
            exceptPrint(e, sys.exc_info(), errmessage1)
            baudrate = None
            break

        baudrate = 0

    dprint("GMCautoBAUDRATE: Found baudrate: {}".format(baudrate))
    setDebugIndent(0)

    return baudrate


#
# Communication with serial port OPEN, CLOSE, COMM
#
def initGMC():
    """
    Tries to open the serial port, and to verify communication
    Return: on success: ""
            on failure: errmessage
    """

    gglobs.GMCDeviceName = "GMC Device"

    msg         = "port='{}' baudrate={} timeoutR={} timeoutW={}".format(gglobs.GMCusbport, gglobs.GMCbaudrate, gglobs.GMCtimeout, gglobs.GMCtimeout_write)
    gglobs.GMCser  = None
    error       = 0
    errmessage  = ""
    errmessage1 = ""

    dprint("initGMC: Settings: " + msg)
    setDebugIndent(1)

    if os.access(gglobs.GMCusbport, os.F_OK):  # test if file with name like '/dev/geiger' exists
        while True:
            # Make the serial connection
            errmessage1 = "Connection failed using " + msg
            try:
                # gglobs.GMCser is like:
                # Serial<id=0x7f2014d371d0, open=True>(port='/dev/ttyUSB0',
                # baudrate=115200, bytesize=8, parity='N', stopbits=1, timeout=20,
                # xonxoff=False, rtscts=False, dsrdtr=False)
                gglobs.GMCser = serial.Serial(gglobs.GMCusbport, gglobs.GMCbaudrate, timeout=gglobs.GMCtimeout, write_timeout=gglobs.GMCtimeout_write)

            except serial.SerialException as e:
                exceptPrint(e, sys.exc_info(), "initGMC: SerialException: " + errmessage1)
                terminateGMC()
                break

            except Exception as e:
                exceptPrint(e, sys.exc_info(), "initGMC: Exception: " + errmessage1)
                terminateGMC()
                break

            # Connection is made. Now test for successful communication with a
            # GMC Geiger counter, because the device port can be opened without
            # error even when no communication can be done, e.g. due to wrong
            # baudrate or wrong device
            dprint("initGMC: Port opened ok, now testing communication")

            # any bytes in pipeline? clear them
            getExtraByte()

            try:
                ver, error, errmessage = getVER()
            except Exception as e:
                errmessage1  = "ERROR: Port opened ok, but Communication failed. Is baudrate correct?"
                exceptPrint(e, sys.exc_info(), "initGMC: " + errmessage1)
                terminateGMC()
                break

            if error < 0:
                errmessage1  = "ERROR: Communication problem: " + errmessage
                dprint("initGMC: " + errmessage1, debug=True)
                terminateGMC()
                break
            else:
                # Got something back for ver like: 'GMC-300Re 4.22'
                if ver.startswith("GMC"):
                    gglobs.GMCdeviceDetected = ver

                else:
                    err  = "<br>INFO: No GMC device detected. While a connected device was found, it <br>"
                    err += "identified itself with this unknown signature: '{}'.".format(ver)
                    errmessage1 += err
                    dprint("initGMC: " + err, debug=True)
                    terminateGMC()

            break

        if gglobs.GMCser == None:
            rmsg = "{}".format(errmessage1.replace('[Errno 2]', '<br>'))
            gglobs.GMCConnection = False
        else:
            dprint("initGMC: " + "Communication ok with device: '{}'".format(ver))
            rmsg = ""
            gglobs.GMCConnection = True

    else:
        rmsg = "initGMC: Initialization failed, Serial Port '{}' does not exist".format(gglobs.GMCusbport)
        edprint(rmsg)


    Qt_update()
    setDebugIndent(0)

    return rmsg



def terminateGMC():
    """what is needed here???"""

    if gglobs.GMCser != None:
        try:
            gglobs.GMCser.close()
        except:
            dprint("terminateGMC: Failed trying to close serial port", debug=True)
        gglobs.GMCser  = None

    gglobs.GMCConnection = False


def serialCOMM(sendtxt, returnlength, caller = ("", "", -1)):
    # write to and read from serial port, exit on serial port error
    # when not enough bytes returned, try send+read again up to 3 times.
    # exit if it still fails

    wprint("serialCOMM: sendtxt: '{}', returnlength: {}, caller: '{}'".format(sendtxt, returnlength, caller))
    setDebugIndent(1)
    #print("serialCOMM: gglobs.GMCser: ", gglobs.GMCser)

    rec         = None
    error       = 0
    errmessage  = ""

    while True:

    # is GMC device still connected?
        if not os.access(gglobs.GMCusbport , os.R_OK):
            # /dev/ttyUSB* can NOT be read
            #serialCLOSE()
            terminateGMC()
            rec         = None
            error       = -1
            errmessage  = "ERROR: Is GMC device connected? USB Port '{}' not found".format(gglobs.GMCusbport)
            dprint("serialCOMM: " + errmessage, debug=True)
            fprint(errmessage, error=True)
            break
        else:
            # /dev/ttyUSB* can be read
            if gglobs.GMCser == None:
                # serial connection does NOT exist
                try:
                    #serialOPEN()    # try to reconnect
                    initGMC()        # try to reconnect
                except:
                    rec         = None
                    error       = -1
                    errmessage  = "No connection (Serial Port is closed)"
                    break
            else:
                # serial connection exists
                pass

    #write to USB port
        try:
            #raise Exception
            #raise serial.SerialException
            #raise serial.SerialTimeoutException  # write-timeout exception
            wtime = time.time()
            rec = gglobs.GMCser.write(sendtxt)  # rec = no of bytes written
            wtime = (time.time() - wtime) * 1000 # wtime in ms

        except serial.SerialException as e:
            srcinfo = "serialCOMM: ERROR: WRITE failed with SerialException when writing: '{}'".format(sendtxt)
            exceptPrint(e, sys.exc_info(), srcinfo)
            wtime = -99

        except serial.SerialTimeoutException as e:
            srcinfo = "serialCOMM: ERROR: WRITE failed with SerialTimeoutException when writing: '{}'".format(sendtxt)
            exceptPrint(e, sys.exc_info(), srcinfo)
            wtime = -99

        except Exception as e:
            srcinfo = "serialCOMM: ERROR: WRITE failed with Exception when writing: '{}'".format(sendtxt)
            exceptPrint(e, sys.exc_info(), srcinfo)
            wtime = -99

        if wtime == -99:
            #print("serialCOMM: wtime:", wtime)
            #serialCLOSE()
            terminateGMC()
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
            rec    = gglobs.GMCser.read(returnlength)
            rtime  = (time.time() - rtime) * 1000
            wprint("serialCOMM: got {} bytes, first (up to 15) bytes: {}".format(len(rec), rec[:15]))
            if len(rec) < returnlength:
                for i in range(len(rec[:15])):
                    try:
                        #wprint("serialCOMM: got bytes decoded: {}".format(rec[:15].decode("UTF-8")))
                        wprint("byte: ", rec[i])
                    except Exception as e:
                        print("e: ", e)

            extra  = getExtraByte()
            rec   += extra
            rtimex = (time.time() - rtimex) * 1000 - rtime

        except serial.SerialException as e:
            srcinfo = "serialCOMM: ERROR: READ failed with serial exception"
            exceptPrint(e, sys.exc_info(), srcinfo)
            dprint("serialCOMM: ERROR: caller is: {} in line no: {}".format(caller[0], caller[1]), debug=True)
            breakRead = True

        except Exception as e:
            srcinfo = "serialCOMM: ERROR: READ failed with exception"
            exceptPrint(e, sys.exc_info(), srcinfo)
            dprint("serialCOMM: ERROR: caller is: {} in line no:{}".format(caller[0], caller[1]), debug=True)
            breakRead = True

        if breakRead:
            terminateGMC()
            rec         = None
            error       = -1
            errmessage  = "serialCOMM: ERROR: READ failed. See log for details"
            break

        # avoid divide by zero
        if returnlength > 0:    rbyte = "{:6.1f}".format(rtime/returnlength)
        else:                   rbyte = "N/A"

        if rtime > (gglobs.GMCtimeout * 1000):
            marker      = "Timeout--" * 7     # mark Timeout lines
            localdebug  = True                # and force these to debug print

        elif rtime > 400:
            marker      = ">" * 50            # mark long reading times
            localdebug  = True                # and force these to debug print

        else:
            marker      = ""
            localdebug  = gglobs.werbose
        wprint("serialCOMM: Timing (ms): write:{:6.2f}, read:{:6.1f}, read per byte:{}, extraread:{:6.1f}  ".format(wtime, rtime, rbyte, rtimex), marker, werbose=localdebug)

    # Retry loop
        if len(rec) < returnlength:
            if rtime > (gglobs.GMCtimeout * 1000):
                msg  = "{} TIMEOUT ERROR Serial Port; command {} exceeded {:3.1f}s".format(stime(), sendtxt, gglobs.GMCtimeout)
                fprint(html_escape(msg), error=True) # escaping needed as GMC commands like b'<GETCPS>>' have <> brackets
                dprint("serialCOMM: " + msg, "- rtime:{:5.1f}ms".format(rtime), debug=True)

            fprint("Got {} data bytes, expected {}. Retrying.".format(len(rec), returnlength))
            dprint("serialCOMM: ERROR: Received length: {} is less than requested: {}".format(len(rec), returnlength), debug=True)
            dprint("serialCOMM: rec: (len={}): {}".format(len(rec), BytesAsHex(rec)))

            error       = 1
            errmessage  = "serialCOMM: ERROR: Command:{} - Record too short: Received bytes:{} < requested:{}".format(sendtxt, len(rec), returnlength)

            # RETRYING
            count    = 0
            countmax = 3
            while True:
                count += 1
                errmsg = "serialCOMM: RETRY: to get full return record, trial #{}".format(count)
                dprint(errmsg, debug=True)

                time.sleep(0.5) # extra sleep after not reading enough data

                extra = getExtraByte()   # just to make sure the pipeline is clean

                gglobs.GMCser.write(sendtxt)
                time.sleep(0.3) # after sending

                rtime  = time.time()
                rec = gglobs.GMCser.read(returnlength)
                rtime = (time.time() - rtime) * 1000
                dprint("Timing (ms): Retry read:{:6.1f}".format(rtime))

                if len(rec) == returnlength:
                    dprint("serialCOMM: RETRY: returnlength is {} bytes. OK now. Continuing normal cycle".format(len(rec)), ", rec:", rec, debug=True)
                    errmessage += "; ok after {} retry".format(count)
                    extra = getExtraByte()   # just to make sure the pipeline is clean
                    fprint("Retry successful.")
                    gglobs.exgg.addError(errmessage)
                    break
                else:
                    #dprint(u"RETRY: serialCOMM: returnlength is {} bytes. Still NOT ok; trying again".format(len(rec)), debug=True)
                    pass

                if count >= countmax:
                    dprint("serialCOMM: RETRY: Retried {} times, always failure, giving up. Serial communication error.".format(count), debug=True)
                    error       = -1
                    errmessage  = "ERROR communicating via serial port. Giving up."
                    fprint(errmessage)
                    gglobs.exgg.addError(errmessage)
                    break

                fprint("ERROR communicating via serial port. Retrying again.")

        break

    setDebugIndent(0)

    return (rec, error, errmessage)


def fprintDeviceInfo(extended = False):
    """Print device info via fprint"""

    if not gglobs.GMCConnection:
        fprint("No connected device")
        return

    dprint("fprintDeviceInfo:")
    setDebugIndent(1)

    fprintShortGMCInfo()

    if extended == True:
        # baudrate as read from device
        fprint("Baudrate read from device:", getBAUDRATE(), debug=True)

        # No of bytes in CP* records
        fprint("No. of bytes in CP* records:", gglobs.nbytes, debug=True)

        # voltage
        rec, error, errmessage = getVOLT()
        if error < 0:
            fprint("Device Battery Voltage:", "{}"      .format(errmessage), debug=True)
        else:
            fprint("Device Battery Voltage:", "{} Volt" .format(rec)       , debug=True)

        # Battery Type
        fprint("Device Battery Type Setting:", getBatteryType(), debug=True)

        # temperature taken out. Apparently not valid at all in 500 series
        # not working in the 300series
        # temperature
        #rec, error, errmessage = getTEMP()
        #if error < 0:
        #    fprint("Device Temperature:", "'{}'" .format(errmessage), debug=True)
        #else:
        #    fprint("Device Temperature:", "{} °C".format(rec)       , debug=True)
        #    fprint("", "(ONLY for GMC-320 ?)")

        # gyro
        rec, error, errmessage = getGYRO()
        if error < 0:
            fprint("Device Gyro Data:", "'{}'".format(errmessage))
        else:
            fprint("Device Gyro data:", rec)
            fprint("", "(only GMC-320 Re.3.01 and later)")

        # Alarm state
        fprint("Device Alarm State:", isAlarmOn(), debug=True)

        # Speaker state
        fprint("Device Speaker State:", isSpeakerOn(), debug=True)

        # MaxCPM
        value = gglobs.cfgLow["MaxCPM"]
        fprint("Max CPM (invalid if 65535!):", value, debug=True)

        # Calibration settings
        fprint(ftextCalibrationSettings(), debug=True)


        # Save Data Type
        sdt, sdttxt = getSaveDataType()
        fprint("Device History Saving Mode:", sdttxt, debug=True)

        # Device History Saving Mode - Threshold
        #print("gglobs.cfgLow['ThresholdMode']", gglobs.cfgLow["ThresholdMode"])
        if gglobs.cfgLow["ThresholdMode"] in (0,1,2):
            ThresholdMode = ("CPM", "µSv/h", "mR/h")
            fprint("Device History Threshold Mode:",   ThresholdMode[gglobs.cfgLow["ThresholdMode"]])
            fprint("Device History Threshold CPM:",    gglobs.cfgLow["ThresholdCPM"] )
            fprint("Device History Threshold µSv/h:",  "{:0.3f}".format(gglobs.cfgLow["ThresholduSv"]))
        else:
            fprint("Device History Threshold Mode:",   "Not available on this device")


        # Web related High bytes in Config
        ghc    = "Device WiFi Data Setup\n"
        fmt    = "{:30s}{}\n"
        for key in ("Website", "URL", "UserID", "CounterID", "SSID", "Password", "Period"):
            ghc += fmt.format("   " + key, gglobs.GMCmap[key])
        fprint(ghc[:-1], debug=True)

        # Firmware settings
        fprint("GeigerLog's Configuration for Device Firmware:", debug=True)
        fprint(ftextFirmwareSettings(), debug=True)

    setDebugIndent(0)


def fprintShortGMCInfo():
    """used for both info and extended info"""

    # device name
    fprint("Connected device:", "'{}'".format(gglobs.GMCdeviceDetected), debug=True)

    if not gglobs.GMCConnection:
        fprint("No connected device", error=True)
        return

    # GMCvariables
    fprint("Configured Variables:", gglobs.GMCvariables, debug=True)
    Qt_update()

    # calibration 1st tube
    fprint("Geiger tube calib. factor:", "{:0.1f} CPM/(µSv/h) (= {:0.4f} µSv/h/CPM)".format(gglobs.calibration1st, 1 / gglobs.calibration1st), debug=True)

    Qt_update()

    # calibration 2nd tube
    if "2nd" in gglobs.GMCvariables:
        fprint("Geiger tube#2 calib. factor:", "{:0.1f} CPM/(µSv/h) (= {:0.4f} µSv/h/CPM)".format(gglobs.calibration2nd, 1 / gglobs.calibration2nd), debug=True)

    Qt_update()

    # serial number
    sn,  error, errmessage = getSERIAL()

    cfg, error, errmessage = getCFG()
    if error < 0: fprint("ERROR trying to read Device Configuration", error=True, debug=True)
    Qt_update()

    # get date and time from device, compare with computer time
    rec, error, errmessage = getDATETIME()
    if error < 0:
        fprint("Device Date & Time:", errmessage, error=True, debug=True)
    else:
        devtime = str(rec)
        cmptime = stime()
        deltat  = round((mpld.datestr2num(cmptime) - mpld.datestr2num(devtime)) * 86400)
        if deltat == 0:
            dtxt = "Device time is same as computer time"
        elif deltat > 0:
            dtxt = "Device is slower than computer by {:0.0f} sec".format(deltat)
        else:
            dtxt = "Device is faster than computer by {:0.0f} sec".format(abs(deltat))

    #    fprint("Date & Time from device:",   devtime, debug=True)
    #    fprint("Date & Time from computer:", cmptime, debug=True)
        if abs(deltat) > 5:
            fprint("Device time:", dtxt, error=True, debug=True)
        else:
            fprint("Device time:", dtxt, debug=True)
    Qt_update()

    # power state
    fprint("Device Power State:", isPowerOn(), debug=True)


def ftextFirmwareSettings():
    """Return device firmware settings formatted as text"""

    si  = ""
    fmt = "{:30s}{}\n"
    if gglobs.GMCdeviceDetected != "auto":
        si += fmt.format("   Memory (bytes):",                "{:,}".format(gglobs.GMCmemory))
        si += fmt.format("   SPIRpage Size (bytes):",         "{:,}".format(gglobs.SPIRpage))
        si += fmt.format("   SPIRbugfix: (True | False)",     "{:}" .format(gglobs.SPIRbugfix))
        si += fmt.format("   Config Size (bytes):",           "{:}" .format(gglobs.configsize))
        si += fmt.format("   Calibration (µSv/h / CPM):",     "{:}" .format(gglobs.calibration1st))
        si += fmt.format("   Voltagebytes (1 | 5):",          "{:}" .format(gglobs.voltagebytes))
        si += fmt.format("   Endianness: (big | little)",     "{:}" .format(gglobs.endianness))

    return si[:-1]


def ftextCalibrationSettings():
    """Return formatted Calibration from device config"""

    ftext  = "Device Calibration Points:\n"
    ftext += "   Calibration Points:     CPM  =  µSv/h   CPM / (µSv/h)   µSv/h / CPM\n"
    for i in range(0,3):
        calcpm = gglobs.cfgLow["CalibCPM_{}".format(i)]
        calusv = gglobs.cfgLow["CalibuSv_{}".format(i)]
        try:
            #~ calfac = calusv / calcpm
            calfac = calcpm / calusv
        except:
            calfac = -999
        ftext += "   Calibration Point {:}: {:6d}  ={:7.2f}       {:5.1f}          {:0.4f} \n".format(i + 1, calcpm, calusv, calfac, 1 / calfac)
        #~ ftext += "   Calibration Point {:}: {:6d}  ={:7.2f}  ({:0.6f} \n".format(i + 1, calcpm, calusv, calfac)
        #~ ftext += "   Calibration Point {:}: {:6.2f} CPM ={:7.2f} µSv/h ({:0.6f} µSv/h / CPM)\n".format(i + 1, 1/calcpm, 1/calusv, 1/calfac)

    return ftext[:-1] # remove last newline char


def ftextCFG():
    """Return device configuration formatted as text"""

    cfg, error, errmessage = getCFG()
    #print("RawCfg: \n", BytesAsHex(cfg))
    fText                  = ""

    if cfg == None:
        fText += errmessage

    elif error < 0 and len(cfg) not in (256, 512):
        fText += errmessage

    else: # if len(cfg) == 256 or len(cfg) == 512 even if error
        lencfg  = len(cfg)
        fText  += "The configuration is:  (Format: dec byte_number: hex value=dec value=ASCII char|)\n"

        cfg     = cfg.rstrip(b'\xFF')       # remove the right side FF values
        #print("RawCfg: after FF strip\n", BytesAsHex(cfg))
        if len(cfg) == 0:
            return "ERROR: Configuration is empty. Try a factory reset!"

        lencfg_strp = len(cfg)
        for i in range(0, lencfg_strp, 6):
            pcfg = ""
            for j in range(0, 6):
                k = i+j
                if k < lencfg_strp:
                    pcfg += "%3d:%02x=%3d" % (k, cfg[k], cfg[k])
                    #print("cfg[k]:", cfg[k], type(cfg[k]))
                    pcfg += "={:1s}| ".format(IntToChar(cfg[k]))
            #fText += pcfg[:-2] + "\n"
            fText += pcfg[:-1] + "\n"

        if lencfg_strp < lencfg:
            fText += "Remaining {} values up to address {} are all 'ff=255'\n".format(lencfg -lencfg_strp, lencfg - 1)

        fText += "The configuration as ASCII is (non-ASCII characters as '.'):\n" + BytesAsASCII(cfg)

    return fText


def getDeviceProperties():
    """define a device and its parameters"""

    # GETVER            Model               Firmware  nominal (observed)
    # GMC-300Re 3.xx,   GMC-300             Firmware: 3.xx    (3.20)
    #                   GMC-300E            existing?
    # GMC-300Re 4.xx,   GMC-300E+           Firmware: 4.xx    (4.20, 4.22)
    #                   GMC-320             existing?
    # GMC-320Re 4.xx,   GMC-320+            Firmware: 4.xx    (4.19)
    # GMC-320Re 5.xx,   GMC-320+V5 (WiFi)   Firmware: 5.xx
    # GMC-500Re 1.xx,   GMC-500 and 500+    Firmware: 1.xx    (1.00, 1.08)
    # GMC-500+Re 1.xx,  GMC-500+            Firmware: 1.??    (1.18(bug), 1.21)
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

    dprint("getDeviceProperties: of connected device: '{}'".format(gglobs.GMCdeviceDetected))
    setDebugIndent(1)

    calibration2nd = gglobs.DefaultCalibration2nd

    if "GMC-300Re 3." in gglobs.GMCdeviceDetected :
        #######################################################################
        # the "GMC-300" delivers the requested page after ANDing with 0fff
        # hence when you request 4k (=1000hex) you get zero
        # therefore use pagesize 2k only
        #######################################################################
        memory               = 2**16
        SPIRpage             = 2048
        SPIRbugfix           = False
        configsize           = 256
        calibration          = 154  # CPM/ (µSv/h), the inverse of 0.0065 µSv/h/CPM
        voltagebytes         = 1
        endianness           = 'little'
        GMCvariables         = "CPM, CPS"
        nbytes               = 2

    elif "GMC-300Re 4." in gglobs.GMCdeviceDetected:
        #######################################################################
        # when using a page of 4k, you need the datalength workaround in
        # gcommand, i.e. asking for 1 byte less
        #######################################################################
        memory               = 2**16
        SPIRpage             = 4096
        SPIRbugfix           = True
        configsize           = 256
        calibration          = 154  # CPM/ (µSv/h), the inverse of 0.0065 µSv/h/CPM
        voltagebytes         = 1
        endianness           = 'little'
        GMCvariables         = "CPM, CPS"
        nbytes               = 2

    elif "GMC-320Re 3." in gglobs.GMCdeviceDetected:
        #######################################################################
        #
        #######################################################################
        memory               = 2**20
        SPIRpage             = 4096
        SPIRbugfix           = False
        configsize           = 256
        calibration          = 154  # CPM/ (µSv/h), the inverse of 0.0065 µSv/h/CPM
        voltagebytes         = 1
        endianness           = 'little'
        GMCvariables         = "CPM, CPS"
        nbytes               = 2

    elif "GMC-320Re 4." in gglobs.GMCdeviceDetected:
        #######################################################################
        #
        #######################################################################
        memory               = 2**20
        SPIRpage             = 4096
        SPIRbugfix           = True
        configsize           = 256
        calibration          = 154  # CPM/ (µSv/h), the inverse of 0.0065 µSv/h/CPM
        voltagebytes         = 1
        endianness           = 'little'
        GMCvariables         = "CPM, CPS"
        nbytes               = 2

    elif "GMC-320Re 5." in gglobs.GMCdeviceDetected:
        #######################################################################
        #
        #######################################################################
        memory               = 2**20
        SPIRpage             = 4096
        SPIRbugfix           = True
        configsize           = 256
        calibration          = 154  # CPM/ (µSv/h), the inverse of 0.0065 µSv/h/CPM
        voltagebytes         = 1
        endianness           = 'little'
        GMCvariables         = "CPM, CPS"
        nbytes               = 2

    elif "GMC-500Re 1." in gglobs.GMCdeviceDetected:
        #######################################################################
        #
        #######################################################################
        memory               = 2**20
        #SPIRpage            = 4096  # ist bug jetzt behoben oder auf altem Stand???
        SPIRpage             = 2048   # Workaround erstmal auf 2048 bytes
        SPIRbugfix           = False
        configsize           = 512
        calibration          = 154  # CPM/ (µSv/h), the inverse of 0.0065 µSv/h/CPM
        voltagebytes         = 5
        endianness           = 'big'
        GMCvariables         = "CPM, CPS"
        nbytes               = 2

    elif "GMC-500+Re 1.18" in gglobs.GMCdeviceDetected:
        #######################################################################
        # Yields 4 bytes on all CPx calls!
        # Has a firmware bug: on first call to GETVER gets nothing returned.
        # WORK AROUND: must cycle connection ON->OFF->ON. then ok
        #######################################################################
        memory               = 2**20
        #SPIRpage            = 4096  # ist bug jetzt behoben oder auf altem Stand???
        SPIRpage             = 2048   # Workaround erstmal auf 2048 bytes
        SPIRbugfix           = False
        configsize           = 512
        # calib based on: http://www.gqelectronicsllc.com/forum/topic.asp?TOPIC_ID=5120 Reply #3
        # calib 2nd tube: 0.194, see Reply #21 in:
        # http://www.gqelectronicsllc.com/forum/topic.asp?TOPIC_ID=5148
        # "The GMC-500+ low sensitivity tube conversion rate is 0.194 uSv/h per
        # CPM. It is about 30 times less than M4011."
        calibration          = 154   # CPM/ (µSv/h), the inverse of 0.0065 µSv/h/CPM
        #~calibration2nd       = 5.15     # CPM/ (µSv/h), the inverse of 0.194  µSv/h/CPM
        calibration2nd       = 2.08     # CPM/ (µSv/h), the inverse of 0.48  µSv/h/CPM
        voltagebytes         = 5
        endianness           = 'big'
        GMCvariables         = "CPM, CPS, CPM1st, CPM2nd, CPS1st, CPS2nd"
        nbytes               = 4

    elif "GMC-500+Re 1.21" in gglobs.GMCdeviceDetected:
        #######################################################################
        # Yields 4 bytes on all CPx calls!
        # Firmware bug from 'GMC-500+Re 1.18' is corrected
        #######################################################################
        memory               = 2**20
        SPIRpage            = 4096  # ist bug jetzt behoben oder auf altem Stand???
        # appears to be working with 4096 and no SPIRbugfix
    #    SPIRpage             = 2048   # Workaround erstmal auf 2048 bytes
        SPIRbugfix           = False
        configsize           = 512
        # calib based on: http://www.gqelectronicsllc.com/forum/topic.asp?TOPIC_ID=5120 Reply #3
        # calib 2nd tube: 0.194, see Reply #21 in:
        # http://www.gqelectronicsllc.com/forum/topic.asp?TOPIC_ID=5148
        # "The GMC-500+ low sensitivity tube conversion rate is 0.194 uSv/h per
        # CPM. It is about 30 times less than M4011."
        calibration          = 154  # CPM/ (µSv/h), the inverse of 0.0065 µSv/h/CPM
        #~calibration2nd       = 5.15     # CPM/ (µSv/h), the inverse of 0.194  µSv/h/CPM
        calibration2nd       = 2.08     # CPM/ (µSv/h), the inverse of 0.48  µSv/h/CPM
        voltagebytes         = 5
        endianness           = 'big'
        GMCvariables         = "CPM, CPS, CPM1st, CPM2nd, CPS1st, CPS2nd"
        nbytes               = 4


    elif "GMC-500+Re 1.2" in gglobs.GMCdeviceDetected: # to cover 1.22ff
        #######################################################################
        # Yields 4 bytes on all CPx calls!
        # Firmware bug from 'GMC-500+Re 1.18' is corrected
        #######################################################################
        memory               = 2**20
        SPIRpage            = 4096  # ist bug jetzt behoben oder auf altem Stand???
        # appears to be working with 4096 and no SPIRbugfix
    #    SPIRpage             = 2048   # Workaround erstmal auf 2048 bytes
        SPIRbugfix           = False
        configsize           = 512
        # calib based on: http://www.gqelectronicsllc.com/forum/topic.asp?TOPIC_ID=5120 Reply #3
        # calib 2nd tube: 0.194, see Reply #21 in:
        # http://www.gqelectronicsllc.com/forum/topic.asp?TOPIC_ID=5148
        # "The GMC-500+ low sensitivity tube conversion rate is 0.194 uSv/h per
        # CPM. It is about 30 times less than M4011."
        calibration          = 154  # CPM/ (µSv/h), the inverse of 0.0065 µSv/h/CPM
        #~calibration2nd       = 5.15     # CPM/ (µSv/h), the inverse of 0.194  µSv/h/CPM
        calibration2nd       = 2.08     # CPM/ (µSv/h), the inverse of 0.48  µSv/h/CPM
        voltagebytes         = 5
        endianness           = 'big'
        GMCvariables         = "CPM, CPS, CPM1st, CPM2nd, CPS1st, CPS2nd"
        nbytes               = 4


    elif "GMC-500+Re 1." in gglobs.GMCdeviceDetected: # if not caught in 1.18, 1.21, 1.22
        #######################################################################
        #
        #######################################################################
        memory               = 2**20
        #SPIRpage            = 4096  # ist bug jetzt behoben oder auf altem Stand???
        SPIRpage             = 2048   # Workaround erstmal auf 2048 bytes
        SPIRbugfix           = False
        configsize           = 512
        # calib based on: http://www.gqelectronicsllc.com/forum/topic.asp?TOPIC_ID=5120 Reply #3
        # calib 2nd tube: 0.194, see Reply #21 in:
        # http://www.gqelectronicsllc.com/forum/topic.asp?TOPIC_ID=5148
        # "The GMC-500+ low sensitivity tube conversion rate is 0.194 uSv/h per
        # CPM. It is about 30 times less than M4011."
        calibration          = 154  # CPM/ (µSv/h), the inverse of 0.0065 µSv/h/CPM
        #~calibration2nd       = 5.15     # CPM/ (µSv/h), the inverse of 0.194  µSv/h/CPM
        calibration2nd       = 2.08     # CPM/ (µSv/h), the inverse of 0.48  µSv/h/CPM
        voltagebytes         = 5
        endianness           = 'big'
        GMCvariables         = "CPM, CPS, CPM1st, CPM2nd"
        nbytes               = 2


    elif "GMC-500+Re 2." in gglobs.GMCdeviceDetected: # to cover 2.00ff
        #######################################################################
        # same as: GMC-500+Re 1.2
        #######################################################################
        memory               = 2**20
        SPIRpage            = 4096  # ist bug jetzt behoben oder auf altem Stand???
        # appears to be working with 4096 and no SPIRbugfix
    #    SPIRpage             = 2048   # Workaround erstmal auf 2048 bytes
        SPIRbugfix           = False
        configsize           = 512
        # calib based on: http://www.gqelectronicsllc.com/forum/topic.asp?TOPIC_ID=5120 Reply #3
        # calib 2nd tube: 0.194, see Reply #21 in:
        # http://www.gqelectronicsllc.com/forum/topic.asp?TOPIC_ID=5148
        # "The GMC-500+ low sensitivity tube conversion rate is 0.194 uSv/h per
        # CPM. It is about 30 times less than M4011."
        calibration          = 154  # CPM/ (µSv/h), the inverse of 0.0065 µSv/h/CPM
        #~calibration2nd       = 5.15     # CPM/ (µSv/h), the inverse of 0.194  µSv/h/CPM
        calibration2nd       = 2.08     # CPM/ (µSv/h), the inverse of 0.48  µSv/h/CPM
        voltagebytes         = 5
        endianness           = 'big'
        GMCvariables         = "CPM, CPS, CPM1st, CPM2nd, CPS1st, CPS2nd"
        nbytes               = 4


    elif "GMC-510+Re 1." in gglobs.GMCdeviceDetected:
        #######################################################################
        # reported by dishemesdr: https://sourceforge.net/p/geigerlog/discussion/general/thread/48ffc25514/
        # Connected device: GMC-510Re 1.04
        #######################################################################
        memory               = 2**20
        #SPIRpage            = 4096  # ist bug jetzt behoben oder auf altem Stand???
        SPIRpage             = 2048   # Workaround erstmal auf 2048 bytes
        SPIRbugfix           = False
        configsize           = 512
        # calib based on: http://www.gqelectronicsllc.com/forum/topic.asp?TOPIC_ID=5120 Reply #3
        # calib 2nd tube: 0.194, see Reply #21 in:
        # http://www.gqelectronicsllc.com/forum/topic.asp?TOPIC_ID=5148
        # "The GMC-500+ low sensitivity tube conversion rate is 0.194 uSv/h per
        # CPM. It is about 30 times less than M4011."
        calibration          = 154  # CPM/ (µSv/h), the inverse of 0.0065 µSv/h/CPM
        #calibration2nd       = 5.15     # CPM/ (µSv/h), the inverse of 0.194  µSv/h/CPM
        calibration2nd       = 2.08      # CPM/ (µSv/h), the inverse of 0.48  µSv/h/CPM
        #~voltagebytes         = 5
        #   2020-09-19 12:57:43 TIMEOUT ERROR Serial Port; command b'<getvolt>>' exceeded 1.0s
        #   Got 1 data bytes, expected 5. Retrying.
        voltagebytes         = 1
        endianness           = 'big'
        GMCvariables         = "CPM, CPS, CPM1st, CPM2nd, CPS1st, CPS2nd"
        nbytes               = 4


    elif "GMC-600Re 1." in gglobs.GMCdeviceDetected:
        #######################################################################
        #
        #######################################################################
        memory               = 2**20
        #SPIRpage            = 4096  # ist bug jetzt behoben oder auf altem Stand???
        SPIRpage             = 2048   # Workaround erstmal auf 2048 bytes
        SPIRbugfix           = False
        configsize           = 512
        calibration          = 154  # CPM/ (µSv/h), the inverse of 0.0065 µSv/h/CPM
        voltagebytes         = 5
        endianness           = 'big'
        GMCvariables         = "CPM, CPS"
        nbytes               = 2


    elif "GMC-600+Re 1." in gglobs.GMCdeviceDetected:
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
        calibration          = 379     # CPM/ (µSv/h), the inverse of 0.002637  µSv/h/CPM
        voltagebytes         = 5
        endianness           = 'big'
        GMCvariables         = "CPM, CPS"
        nbytes               = 2


    else: # If none of the above match, then this will be reached
        #######################################################################
        # to integrate as of now unknown new (or old) devices
        #######################################################################
        dprint("getDeviceProperties: New, unknown device has been connected:", gglobs.GMCdeviceDetected, debug=True)
        playWav("error")
        memory               = 2**20
        SPIRpage             = 2048
        SPIRbugfix           = False
        configsize           = 512
        calibration          = 154  # CPM/ (µSv/h), the inverse of 0.0065 µSv/h/CPM
        voltagebytes         = 5
        endianness           = 'big'
        GMCvariables         = "CPM, CPS"
        nbytes               = 2

    # overwrite preset values if defined in the GeigerLog config file
    if gglobs.GMCmemory      == 'auto':     gglobs.GMCmemory        = memory
    if gglobs.SPIRpage       == 'auto':     gglobs.SPIRpage         = SPIRpage
    if gglobs.SPIRbugfix     == 'auto':     gglobs.SPIRbugfix       = SPIRbugfix
    if gglobs.configsize     == 'auto':     gglobs.configsize       = configsize
    if gglobs.calibration1st == 'auto':     gglobs.calibration1st   = calibration
    if gglobs.calibration2nd == 'auto':     gglobs.calibration2nd   = calibration2nd
    if gglobs.voltagebytes   == 'auto':     gglobs.voltagebytes     = voltagebytes
    if gglobs.endianness     == 'auto':     gglobs.endianness       = endianness
    if gglobs.GMCvariables   == 'auto':     gglobs.GMCvariables     = GMCvariables
    if gglobs.nbytes         == 'auto':     gglobs.nbytes           = nbytes

    #print("deviceDetected: configsize:", gglobs.GMCdeviceDetected, gglobs.configsize)

    DevVars = gglobs.GMCvariables.split(",")
    for i in range(0, len(DevVars)):  DevVars[i] = DevVars[i].strip()
    gglobs.DevicesVars["GMC"] = DevVars
    #print("DevicesVars:", gglobs.DevicesVars)

    setDebugIndent(0)

