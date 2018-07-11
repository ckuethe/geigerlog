#!/usr/bin/python
# -*- coding: UTF-8 -*-

"""
gcommands.py - the commands specific to the Geiger counter

using serial communication

device command coding taken from:
Phil Gillaspy, https://sourceforge.net/projects/gqgmc/
and document GQ-RFC1201.txt (GQ-RFC1201, GQ Geiger Counter Communication
Protocol, Ver 1.40    Jan-2015)
"""


import sys                      # system functions
import serial
import serial.tools.list_ports  # allows listing of serial ports
import time
import datetime                 # date and time conversions
import struct                   # packing numbers into chars
import traceback                # for traceback on error

from gutils import *

__author__      = "ullix"
__copyright__   = "Copyright 2016"
__credits__     = ["Phil Gillaspy"]
__license__     = "GPL"


#
# Commands and functions implemented in device
#

def getVER(ser):
    # Get hardware model and version
    # send <GETVER>> and read 14 bytes
    # returns total of 14 bytes ASCII chars from GQ GMC unit.
    # includes 7 bytes hardware model and 7 bytes firmware version.
    # e.g.: 'GMC-300Re 4.20'
    # use byteformat=False to NOT convert into int but return ASCII string

    dprint(gglobs.debug, u"getVER: Begin.")
    debugIndent(1)

    rec, error, errmessage = serialCOMM(ser, b'<GETVER>>', 14, orig(__file__), False)
    extra = getExtraByte(ser)

    rec   = convertBytesToAscii(rec)   # problem observed only in defect system

    debugIndent(0)
    dprint(gglobs.debug, u"getVER: Done. rec='{}', error='{}', errmessage='{}'".format(rec, error, errmessage))

    return (rec, error, errmessage)


def getCPMS(ser, CPMflag = True):
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

    if CPMflag:  # measure as CPM
        rec, error, errmessage = serialCOMM(ser, b'<GETCPM>>', 2, orig(__file__))
        vprint(gglobs.verbose, "getCPMS: CPMflag=True, rec=", rec)

        if error == 0 or error == 1: rec = rec[0]<< 8 | rec[1]

    else:       # measure as CPS
        rec, error, errmessage = serialCOMM(ser, b'<GETCPS>>', 2, orig(__file__))
        vprint(gglobs.verbose, "getCPMS: CPMflag=False, rec=", rec)

        if error == 0 or error == 1: rec = ((rec[0] & 0x3f) << 8 | rec[1]) * 60
        #print "Testing:    len={:}, MSB:{:x}={:d}, LSB:{:x}={:d}, value:{:d} ".format(len(rec), (rec[0]), (rec[0]), (rec[1]), (rec[1]), r)

    return (rec, error, errmessage)


def turnHeartbeatOn(ser):
    # 3. Turn on the GQ GMC heartbeat
    # Note:     This command enable the GQ GMC unit to send count per second data to host every second automatically.
    # Command:  <HEARTBEAT1>>
    # Return:   A 16 bit unsigned integer is returned every second automatically. Each data package consist of 2 bytes data from GQ GMC unit.
    #           The first byte is MSB byte data and second byte is LSB byte data.
    # e.g.:     10 1C     the returned 1 second count is 28.   Only lowest 14 bits are used for the valid data bit.
    #           The highest bit 15 and bit 14 are reserved data bits.
    # Firmware supported:  GMC-280, GMC-300  Re.2.10 or later

    dprint(gglobs.debug, u"turnHeartbeatOn: Begin.")
    debugIndent(1)

    if ser == None:
        rec         = ""
        error       = 1
        errmessage  = "No serial connection"
    else:
        rec, error, errmessage = serialCOMM(ser, b'<HEARTBEAT1>>', 0, orig(__file__))
        extra                  = getExtraByte(ser)

    debugIndent(0)
    dprint(gglobs.debug, u"turnHeartbeatOn: Done. rec='{}', error='{}', errmessage='{}'".format(rec, error, errmessage))

    return (rec, error, errmessage)


def turnHeartbeatOFF(ser):
    # 4. Turn off the GQ GMC heartbeat
    # Command:  <HEARTBEAT0>>
    # Return:   None
    # Firmware supported:  Re.2.10 or later

    dprint(gglobs.debug, u"turnHeartbeatOFF: Begin.")
    debugIndent(1)

    if ser == None:
        rec         = ""
        error       = 1
        errmessage  = "No serial connection"
    else:
        rec, error, errmessage = serialCOMM(ser, b'<HEARTBEAT0>>', 0, orig(__file__))
        extra                  = getExtraByte(ser)

    debugIndent(0)
    dprint(gglobs.debug, u"turnHeartbeatOFF: Done. rec='{}', error='{}', errmessage='{}'".format(rec, error, errmessage))

    return (rec, error, errmessage)


def getVOLT(ser):
    # Get battery voltage status
    # send <GETVOLT>> and read 1 byte
    # returns one byte voltage value of battery (X 10V)
    # e.g.: return 62(hex) is 9.8V
    # Example: Geiger counter GMC-300E+
    # with Li-Battery 3.7V, 800mAh (2.96Wh)
    # -> getVOLT reading is: 4.2V
    # -> Digital Volt Meter reading is: 4.18V
    #
    # GMC 500 scheint anders zu sein! Scheint 5 bytes zu liefern, die als
    # ASCII interpretiert werden müssen
    # z.B.[52, 46, 49, 49, 118] = "4.11v"

    dprint(gglobs.debug, u"getVOLT: Begin. Using device: '{}'".format(gglobs.devices[gglobs.devicesIndex]))
    debugIndent(1)

    if ser == None:
        rec         = ""
        error       = 1
        errmessage  = "No serial connection"

    elif gglobs.device in ["GMC-300", "GMC-320", "GMC-320+", "GMC-300E+"]:
        rec, error, errmessage = serialCOMM(ser, b'<GETVOLT>>', 1, orig(__file__))
        dprint(gglobs.debug, "VOLT: raw:", rec)
        extra = getExtraByte(gglobs.ser)

        if error == 0 or error == 1:
            rec = rec[0]/10.0

    elif gglobs.device in ["GMC-500", "GMC-500+", "GMC-600", "GMC-600+"]:
        rec, error, errmessage = serialCOMM(ser, b'<GETVOLT>>', 5, orig(__file__))

        # TEST!!!!!!!!!!!
        #rec         = [52, 46, 49, 49, 118] # 4.11 V
        #error       = 1
        #errmessage  = "testing"
        ###############

        dprint(gglobs.debug, "VOLT: raw:", rec)
        extra = getExtraByte(gglobs.ser)

        arec = ""
        if error == 0 or error == 1:
            for i in range(4):
                arec += chr(rec[i])
            rec = arec
    else:
        rec         = ""
        error       = 1
        errmessage  = "Illegal Setting for Device; check configuration"

    debugIndent(0)
    dprint(gglobs.debug, u"getVOLT: Done. Volt='{}', error='{}', errmessage='{}'".format(rec, error, errmessage))

    return (rec, error, errmessage)


def getSPIR(ser, address = 0, datalength = 4096):
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

    # This contains a WORKAROUND:
    # it asks for only (datalength - 1) bytes,
    # but as it then reads one more byte, the original datalength is obtained

    dprint(gglobs.debug, u"getSPIR: Begin.")
    debugIndent(1)

    # pack address into 4 bytes, big endian; then clip 1st byte = high byte!
    ad = struct.pack(">I", address)[1:]

    ###########################################################################
    # pack datalength into 2 bytes, big endian; use all bytes
    #
    # BUG ALERT - WORKAROUND
    # GMC-300E+ : use workaround 'datalength - 1'
    # GMC-320   : same as GMC-300E+
    # GMC-320+  : same as GMC-300E+
    # GMC-300   : the '- 1' must be dropped and only 2k bytes read
    # GMC-500   : bei Lesen von 4095 bytes werden nur 4095 und KEINE 4096 zurückgegeben
    # ist der Bug behoben oder nur auf altem Stand von GMC-300 zurück?
    # workaround dafür ist nur 2048 anzufordern und zu lesen
    # GMC-500+  : treated as a GM-500
    # GMC-600   : treated as a GM-500
    # GMC-600+  : treated as a GM-500

    if   gglobs.device == "GMC-300":
        dl = struct.pack(">H", datalength)

    elif gglobs.device == "GMC-300E+":
        dl = struct.pack(">H", datalength - 1)

    elif gglobs.device == "GMC-320":
        dl = struct.pack(">H", datalength - 1)

    elif gglobs.device == "GMC-320+":
        dl = struct.pack(">H", datalength - 1)

    elif gglobs.device == "GMC-500":
        dl = struct.pack(">H", datalength)

    elif gglobs.device == "GMC-500+":
        dl = struct.pack(">H", datalength)      # same as GMC-500

    elif gglobs.device == "GMC-600":
        dl = struct.pack(">H", datalength)      # same as GMC-500

    elif gglobs.device == "GMC-600+":
        dl = struct.pack(">H", datalength)      # same as GMC-500

    else:
        dprint(True, "Illegal setting for device; check configuration file")
        sys.exit()

    ###########################################################################

    dprint(gglobs.debug, "SPIR requested: address: {:5d}, datalength:{:5d}   (hex: address: {:02x} {:02x} {:02x}, datalength: {:02x} {:02x})".format(address, datalength, ord(ad[0]), ord(ad[1]), ord(ad[2]), ord(dl[0]), ord(dl[1])))
    rec, error, errmessage = serialCOMM(ser, b'<SPIR'+ad+dl+'>>', datalength, orig(__file__), False) # returns ASCII string

    if rec != None :
        msg = "SPIR received: datalength:{:5d}".format(len(rec))
    else:
        msg = "SPIR received: ERROR: No data received!"

    debugIndent(0)
    dprint(gglobs.debug, u"getSPIR: Done. msg='{}', error='{}', errmessage='{}'".format(msg, error, errmessage))

    return (rec, error, errmessage)


def getHeartbeatCPS(ser):
    """read bytes until no further bytes coming"""

    if not gglobs.debug: return  # execute only in debug mode

    eb= 0
    while True:                  # read more until nothing is returned
                                 # (actually, never more than 1 more is returned)
        eb += 1
        rec = ""
        rec = ser.read(2)
        rec = map (ord, rec)
        cps =  ((rec[0] & 0x3f) << 8 | rec[1])
        #print "eb=", eb

        #print "cps:", cps
        """
        if len(x) > 0:
            #dprint(gglobs.debug, "got more bytes: x=", x, ", type:", type(x), ", len(x)=", len(x), ", dec value:", ord(x))
            print "got more bytes: x=", x, ", type:", type(x), ", len(x)=", len(x), ", dec value:"#, ord(x)
            rec += x
        else:
            dprint(gglobs.debug, "no more bytes : x=", x, ", type:", type(x), ", len(x)=", len(x))
            break
        """
        break

    return cps


def getExtraByte(ser):
    """read single bytes until no further bytes coming"""

    dprint(gglobs.debug, u"getExtraByte: Begin.")
    debugIndent(1)

    rec          = b""
    try: # failed when called from 2nd instance of GeigerLog; just to avoid error
        bytesWaiting = gglobs.ser.in_waiting
    except:
        bytesWaiting = 0

    #bytesWaiting += 5   # TESTING ONLY
    if bytesWaiting == 0:
        msg = u"No extra bytes waiting for reading"
    else:
        msg = ""
        dprint(True, u"Bytes waiting: {}".format(bytesWaiting))
        while True:                # read single byte until nothing is returned
            x = ser.read(1)
            if len(x) == 0: break
            rec += x

        dprint(True, "Got {} extra bytes from reading-pipeline:".format(len(rec)), map(ord, rec))
        dprint(True, "Extra bytes as ASCII: '{}'".format(convertBytesToAscii(rec)))

    #rec = ["A", "B", "C", "D"]  # testing

    debugIndent(0)
    dprint(gglobs.debug, u"getExtraByte: Done. " + msg)

    return rec


def getCFG(ser):
    # Get configuration data
    # send <GETCFG>> and read 256 bytes
    # returns the configuration data as a Python list of 256 int

    # NOTE: 300series uses 256 bytes; 500series 512 bytes; 600 series 512(?)
    # Reading 256 bytes first, and if more available then until all done

    """
    The meaning is: (from: http://www.gqelectronicsllc.com/forum/topic.asp?TOPIC_ID=4447)

    CFG data Offset table. Start from 0
    ==========================================
    PowerOnOff, //to check if the power is turned on/off intended
    AlarmOnOff, //1
    SpeakerOnOff,
    GraphicModeOnOff,
    BackLightTimeoutSeconds,
    IdleTitleDisplayMode,
    AlarmCPMValueHiByte, //6
    AlarmCPMValueLoByte,
    CalibrationCPMHiByte_0,
    CalibrationCPMLoByte_0,
    CalibrationuSvUcByte3_0,
    CalibrationuSvUcByte2_0, //11
    CalibrationuSvUcByte1_0,
    CalibrationuSvUcByte0_0,
    CalibrationCPMHiByte_1,
    CalibrationCPMLoByte_1, //15
    CalibrationuSvUcByte3_1,
    CalibrationuSvUcByte2_1,
    CalibrationuSvUcByte1_1,
    CalibrationuSvUcByte0_1,
    CalibrationCPMHiByte_2, //20
    CalibrationCPMLoByte_2,
    CalibrationuSvUcByte3_2,
    CalibrationuSvUcByte2_2,
    CalibrationuSvUcByte1_2,
    CalibrationuSvUcByte0_2, //25
    IdleDisplayMode,
    AlarmValueuSvByte3,
    AlarmValueuSvByte2,
    AlarmValueuSvByte1,
    AlarmValueuSvByte0, //30
    AlarmType,
    SaveDataType,
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
    PowerSavingMode,
    Reserved, //45
    Reserved,
    Reserved,
    DisplayContrast,
    MAX_CPM_HIBYTE,
    MAX_CPM_LOBYTE, //50
    Reserved,
    LargeFontMode,
    LCDBackLightLevel,
    ReverseDisplayMode,
    MotionDetect, //55
    bBatteryType,
    BaudRate,
    Reserved,
    GraphicDrawingMode,
    LEDOnOff,
    Reserved,
    SaveThresholdValueuSv_m_nCPM_HIBYTE,
    SaveThresholdValueuSv_m_nCPM_LOBYTE,
    SaveThresholdMode,
    SaveThresholdValue3,
    SaveThresholdValue2,
    SaveThresholdValue1,
    SaveThresholdValue0,
    Save_DateTimeStamp, //this one uses 6 byte space
    """

    dprint(gglobs.debug, u"getCFG: Begin.")
    debugIndent(1)

    rec, error, errmessage = serialCOMM(ser, b'<GETCFG>>', 256, orig(__file__))

    while True:
        if rec == None:
            dprint(True, "ERROR: Failed to get configuration data")
            break

        dprint(gglobs.debug, u"Got {} bytes".format(len(rec)))
        time.sleep(1)       # zu schnell um frische bytes in die pipeline zu kriegen?
        if ser.in_waiting > 0:
            dprint(gglobs.debug, "found {} bytes waiting".format(ser.in_waiting))
            extra = getExtraByte(ser)
            rec   = rec + map(ord, extra)
        else:
            dprint(gglobs.debug, "found no bytes waiting")

        asc    = convertBytesToAscii("".join(map(chr,rec)))

        dprint(gglobs.debug, "CFG bytes as list of length {}:\n".format(len(rec)), rec)
        dprint(gglobs.debug, "CFG bytes as ASCII: '{}'".format(asc))
        break

    debugIndent(0)
    dprint(gglobs.debug, u"getCFG: Done.")

    return rec, error, errmessage


def writeConfigData(ser, cfg, cfgaddress, value):
    # 9. Write configuration data
    # Command:  <WCFG[A0][D0]>>
    # A0 is the address and the D0 is the data byte(hex).
    # A0 is offset of byte in configuration data.
    # D0 is the assigned value of the byte.
    # Return: 0xAA
    # Firmware supported: GMC-280, GMC-300 Re.2.10 or later

    # erase config
    rec  = serialCOMM(ser, b'<ECFG>>', 1, orig(__file__))

    cfg[cfgaddress] = value
    cfg             = remove_trailing(cfg, remove_value=255)

    for i, c in enumerate(cfg):
        #print i, c, "\t"
        A0 = chr(i)
        D0 = chr(c)
        rec  = serialCOMM(ser, b'<WCFG{}{}>>'.format(A0, D0), 1, orig(__file__))

    rec  = updateConfig(gglobs.ser)
    dprint(gglobs.debug, "writeConfigData:", rec)

    return rec


def updateConfig(ser):
    # 13. Reload/Update/Refresh Configuration
    # Command: <CFGUPDATE>>
    # Return: 0xAA
    # Firmware supported: GMC-280, GMC-300 Re.2.20 or later

    rec  = serialCOMM(ser, b'<CFGUPDATE>>', 1, orig(__file__))
    dprint(gglobs.debug, "updateConfig:", rec)
    return rec


def getSERIAL(ser):
    # Get serial number
    # send <GETSERIAL>> and read 7 bytes
    # returns the serial number in 7 bytes
    # each nibble of 4 bit is a single hex digit of a 14 character serial number
    # e.g.: F488007E051234
    #
    # This routine returns the serial number as a 14 character ASCII string

    dprint(gglobs.debug, u"getSERIAL: Begin.")
    debugIndent(1)

    rec, error, errmessage  = serialCOMM(ser, b'<GETSERIAL>>', 7, orig(__file__))
    dprint(gglobs.debug, "getSERIAL: raw:", rec)

    extra = getExtraByte(ser)

    if error == 0 or error == 1:  # Ok or Warning
        hexlookup = "0123456789ABCDEF"
        sn =""
        for i in range(0,7):
            n1   = ((rec[i] & 0xF0) >>4)
            n2   = ((rec[i] & 0x0F))
            sn  += hexlookup[n1] + hexlookup[n2]
        rec = sn

    debugIndent(0)
    dprint(gglobs.debug, u"getSERIAL: Done. rec={}, error={}, errmessage='{}'".format(rec, error, errmessage))

    return (rec, error, errmessage)


def setDATETIME(ser):
    # from GQ-RFC1201.txt:
    # NOT CORRECT !!!!
    # 22. Set year date and time
    # command: <SETDATETIME[YYMMDDHHMMSS]>>
    # Return: 0xAA
    # Firmware supported: GMC-280, GMC-300 Re.3.00 or later

    # from: GQ-GMC-ICD.odt
    # CORRECT! 6 bytes, no square brackets
    # <SETDATETIME[YY][MM][DD][hh][mm][ss]>>

    dprint(gglobs.debug, u"setDATETIME: Begin.")
    debugIndent(1)

    tl      = list(time.localtime())
    #print "tl:", tl
    tl[0]  -= 2000
    tlstr   = b''
    for i in range(0,6):  tlstr += chr(tl[i])
    #print "tlstr:", tlstr
    #for a in tlstr: print ord(a),
    #print
    rec, error, errmessage = serialCOMM(ser, b'<SETDATETIME'+ tlstr +'>>', 1, orig(__file__))

    extra = getExtraByte(ser)

    debugIndent(0)
    dprint(gglobs.debug, u"setDATETIME: Done. rec={}, error={}, errmessage='{}'".format(rec, error, errmessage))

    return (rec, error, errmessage)


def getDATETIME(ser):
    # Get year date and time
    # send <GETDATETIME>> and read 7 bytes
    # returns 7 bytes data: YY MM DD HH MM SS 0xAA
    #
    # This routine returns date and time in the format:
    #       YYYY-MM-DD HH:MM:SS
    # e.g.: 2017-12-31 14:03:19

    dprint(gglobs.debug, u"getDATETIME: Begin.")
    debugIndent(1)

    rec, error, errmessage = serialCOMM(ser, b'<GETDATETIME>>', 7, orig(__file__))
    extra                  = getExtraByte(ser)

    if rec != None:
        dprint(gglobs.debug, "raw:", rec, ", len(rec):"+str(len(rec)))
    else:
        dprint(gglobs.debug, "raw", rec)

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

    debugIndent(0)
    dprint(gglobs.debug, u"getDATETIME: Done. rec={}, error={}, errmessage='{}'".format(rec, error, errmessage))

    return (rec, error, errmessage)


def getTEMP(ser):
    # Get temperature
    # Firmware supported: GMC-320 Re.3.01 or later (NOTE: Not for GMC-300!)
    # send <GETTEMP>> and read 4 bytes
    # Return: Four bytes celsius degree data in hexdecimal: BYTE1,BYTE2,BYTE3,BYTE4
    # Here: BYTE1 is the integer part of the temperature.
    #       BYTE2 is the decimal part of the temperature.
    #       BYTE3 is the negative signe if it is not 0.  If this byte is 0,
    #       then current temperture is greater than 0, otherwise the temperature is below 0.
    #       BYTE4 always 0xAA (=170dec)

    dprint(gglobs.debug, u"getTEMP: Begin.")
    debugIndent(1)

    rec, error, errmessage  = serialCOMM(ser, b'<GETTEMP>>', 4, orig(__file__))
    #rec = [28, 8, 1, 170 ]  # TESTING example
    extra                   = getExtraByte(ser)
    dprint(gglobs.debug, "Temp raw: rec={}, error={}, errmessage='{}'".format(rec, error, errmessage))

    if error == 0 or error == 1:  # Ok or Warning
        if gglobs.device in ["GMC-300", "GMC-300E+", "GMC-320", "GMC-320+"]:
            temp = rec[0] + rec[1]/10.0     # unclear: is  decimal part rec[1] single digit or a 2 digit?
                                            # 3 digit not possible as byte value is from 0 ... 255
                                            # expecting rec[1] always from 0 ... 9
            if rec[2] <> 0 : temp *= -1
            if rec[1]  > 9 : temp  = str(temp) + " ERROR: illegal value found for decimal part of temperature ={}".format(rec[1])
            rec = temp

        elif gglobs.device in ["GMC-500", "GMC-500+", "GMC-600", "GMC-600+"]:
            temp = rec[0] + rec[1]/10.0     # unclear: is  decimal part rec[1] single digit or a 2 digit?
                                            # 3 digit not possible as byte value is from 0 ... 255
                                            # expecting rec[1] always from 0 ... 9
            if rec[2] <= 0 : temp *= -1     # guessing: value=1 looks like positive Temperature. Negative is???
            if rec[1]  > 9 : temp  = str(temp) + " ERROR: illegal value found for decimal part of temperature ={}".format(rec[1])
            rec = temp

    debugIndent(0)
    dprint(gglobs.debug, u"getTEMP: Done. rec={}, error={}, errmessage='{}'".format(rec, error, errmessage))

    return (rec, error, errmessage)


def getGYRO(ser):
    # Get gyroscope data
    # Firmware supported: GMC-320 Re.3.01 or later (NOTE: Not for GMC-300!)
    # Send <GETGYRO>> and read 7 bytes
    # Return: Seven bytes gyroscope data in hexdecimal: BYTE1,BYTE2,BYTE3,BYTE4,BYTE5,BYTE6,BYTE7
    # Here: BYTE1,BYTE2 are the X position data in 16 bits value. The first byte is MSB byte data and second byte is LSB byte data.
    #       BYTE3,BYTE4 are the Y position data in 16 bits value. The first byte is MSB byte data and second byte is LSB byte data.
    #       BYTE5,BYTE6 are the Z position data in 16 bits value. The first byte is MSB byte data and second byte is LSB byte data.
    #       BYTE7 always 0xAA

    dprint(gglobs.debug, u"getGYRO: Begin.")
    debugIndent(1)

    rec, error, errmessage  = serialCOMM(ser, b'<GETGYRO>>', 7, orig(__file__))
    extra                   = getExtraByte(ser)
    dprint(gglobs.debug, "GYRO: raw: rec={}, error={}, errmessage='{}'".format(rec, error, errmessage))

    if error == 0 or error == 1:  # Ok or Warning
        x = rec[0] * 256 + rec[1]
        y = rec[2] * 256 + rec[3]
        z = rec[4] * 256 + rec[5]
        rec = "X=0x{:04x}, Y=0x{:04x}, Z=0x{:04x}   ({},{},{})".format(x,y,z,x,y,z)

    debugIndent(0)
    dprint(gglobs.debug, u"getGYRO: Done. rec={}, error={}, errmessage='{}'".format(rec, error, errmessage))

    return rec, error, errmessage


def setPOWEROFF(ser):
    # 12. Power OFF
    # Command: <POWEROFF>>
    # Return: none
    # Firmware supported: GMC-280, GMC-300 Re.2.11 or later

    rec  = serialCOMM(ser, b'<POWEROFF>>', 0, orig(__file__))
    dprint(gglobs.debug, "setPOWEROFF:", rec)

    return rec


def setPOWERON(ser):
    # 26. Power ON
    # Command: <POWERON>>
    # Return: none
    # Firmware supported: GMC-280, GMC-300, GMC-320 Re.3.10 or later

    rec  = serialCOMM(ser, b'<POWERON>>', 0, orig(__file__))
    dprint(gglobs.debug, "setPOWERON:", rec)

    return rec


def setREBOOT(ser):
    # 21. Reboot unit
    # command: <REBOOT>>
    # Return: None
    # Firmware supported: GMC-280, GMC-300 Re.3.00 or later

    rec  = serialCOMM(ser, b'<REBOOT>>', 0, orig(__file__))
    dprint(gglobs.debug, "setREBOOT:", rec)

    return rec


def setFACTORYRESET(ser):
    # 20. Reset unit to factory default
    # command: <FACTORYRESET>>
    # Return: 0xAA
    # Firmware supported: GMC-280, GMC-300 Re.3.00 or later

    rec  = serialCOMM(ser, b'<FACTORYRESET>>', 1, orig(__file__))
    dprint(gglobs.debug, "setFACTORYRESET:", rec)

    return rec


#
# Derived commands and functions
#

def isPowerOn():
    """Checks Power status in the configuration
    Power at offset:0"""

    cfg    = gglobs.cfg

    try:
        if gglobs.device in ["GMC-300", "GMC-300E+", "GMC-320", "GMC-320+"]: # all 300series
            c = cfg[gglobs.cfgOffsetPower]
        else:                                # 500, 500+, 600, 600+
            c = "Unknown due to unddisclosed firmware changes"
    except:
        c = "Unknown"

    if   c == 0:            p = "ON"
    elif c == 255:          p = "OFF"
    else:                   p = c

    return p


def isAlarmOn():
    """Checks Alarm On status in the configuration
    Alarm at offset:1"""

    cfg    = gglobs.cfg

    try:
        if gglobs.device in ["GMC-300", "GMC-300E+", "GMC-320", "GMC-320+"]: # all 300series
            c = cfg[gglobs.cfgOffsetAlarm]
        else:                                # 500, 500+, 600, 600+
            c = "Unknown due to unddisclosed firmware changes"
    except:
        c = "Unknown"

    if   c == 0:            p = "OFF"
    elif c == 1:            p = "ON"
    else:                   p = c

    return p


def isSpeakerOn():
    """Checks Speaker On status in the configuration
    Speaker at offset:2"""

    cfg    = gglobs.cfg

    try:
        if gglobs.device in ["GMC-300", "GMC-300E+", "GMC-320", "GMC-320+"]: # all 300series
            c = cfg[gglobs.cfgOffsetSpeaker]
        else:                                # 500, 500+, 600, 600+
            c = "Unknown due to unddisclosed firmware changes"
    except:
        c = "Unknown"

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
        if gglobs.device in ["GMC-300", "GMC-300E+", "GMC-320", "GMC-320+"]: # all 300series
            sdt    = cfg[gglobs.cfgOffsetSDT]
        else:                                # 500, 500+, 600, 600+
            sdt = 999
    except:
        sdt = 888

    #print "sdt:", sdt
    try:
        if sdt <= len(sdttxt):  txt = sdttxt[sdt]
        elif sdt == 999:        txt = "Unknown due to unddisclosed firmware changes"
        else:                   txt = "Unknown"
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
    """

    brdict  = {64:1200, 160:2400, 208:4800, 232:9600, 240:14400, 244:19200, 248:28800, 250:38400, 252:57600, 254:115200}
    key     = 99999
    cfg     = gglobs.cfg
    #print "cfg      cfg Baudrate"
    #for key, value in sorted(brdict.iteritems()):
    #    print "{:08b} {:3d} {:6d}".format(key, key, value)

    try:
        if gglobs.device in ["GMC-300", "GMC-300E+", "GMC-320", "GMC-320+"]: # all 300series
            key = cfg[57]
            rec = brdict[key]
        else:                                # 500, 500+, 600, 600+
            rec = "Unknown due to unddisclosed firmware changes"
            dprint(True, rec + "; cfg[57]={}".format(key))
    except:
        rec = "ERROR: Baudrate unknown; cfg[57]={}".format(key)
        dprint(True, rec)

    return rec


def autoBAUDRATE(usbport):
    """Tries to find a proper baudrate by testing for successful serial
    communication at up to all possible baudrates, beginning with the
    highest
    NOTE: the device port can be opened without error at any baudrate,
    even when no communication can be done, e.g. due to wrong baudrate.
    Therfore we test for successful communication by checking for correct
    number of bytes returned and the return string begins with 'GMC'.
    ON success, this baudrate will be returned.
    A baudrate=0 will be returned when all communication fails.
    On a serial error, a hard exit will occur.
    """

    dprint(True, "autoBAUDRATE: Begin. Autodiscovery of baudrate on port: '{}'".format(usbport))
    debugIndent(1)

    baudrates = gglobs.baudrates
    baudrates.sort(reverse=True) # to start with highest baudrate
    for baudrate in baudrates:
        dprint(True, "Trying baudrate:", baudrate)
        try:
            ser = serial.Serial(usbport, baudrate, timeout= 0.5)
            ser.write(b'<GETVER>>')
            rec = ser.read(14)
            ser.close()
            #print "autoBAUDRATE: usbport: '{}', rec: '{}'".format(usbport, rec)

            if len(rec) == 14 and rec.startswith("GMC"):
                dprint(True, "Success with {}".format(baudrate))
                break
        except ( serial.SerialException,  ValueError) as err:
            dprint(True, "ERROR: autoBAUDRATE: Serial communication error on finding baudrate:", unicode(err))
            baudrate = None
            break

        baudrate = 0

    debugIndent(0)
    dprint(True, "autoBAUDRATE: Done. Found baudrate: {}".format(baudrate))

    return baudrate


def autoPORT():
    """Tries to find a working port and baudrate by testing all serial
    ports for successful communication by auto discovery of baudrate.
    All available ports will be listed with the highest baudrate found.
    Ports are found as:
    /dev/ttyS0 - ttyS0              # a regular serial port
    /dev/ttyUSB0 - USB2.0-Serial    # a USB-to-Serial port
    """

    dprint(True, "autoPORT: Begin. Autodiscovery of Serial Ports")
    debugIndent(1)

    time.sleep(0.5) # a freshly plugged in device, not fully recognized
                    # by system, sometimes produces errors

    ports =[]
    # Pyserial: include_links (bool) – include symlinks under /dev when they point to a serial port
    #lp = serial.tools.list_ports.comports(include_links=True) # also shows e.g. /dev/geiger
    lp = serial.tools.list_ports.comports(include_links=False) # default; no symlinks shown
    #lp.append("/dev/ttyS0 - ttyS0") # for TESTING only

    if len(lp) == 0:
        errmessage = "ERROR: autoPORT: No available serial ports found"
        dprint(True, errmessage)
        return None, errmessage
    else:
        dprint(True, "Found these ports:")
        for p in lp :
            dprint(True, "   ", p)
            ports.append(str(p).split(" ",1)[0])

    ports.sort()
    ports_found = []

    dprint(True, "Testing all ports for communication:")
    for port in ports:
        #dprint(True, "Port:", port)

        if "/dev/ttyS" in port:
            if gglobs.ttyS == 'include':
                dprint(True, "Include Flag is set for port: '{}'".format(port))
            else:
                dprint(True, "Ignore Flag is set for port: '{}'".format(port))
                continue

        abr = autoBAUDRATE(port)
        if abr > 0:
            ports_found.append((port, abr))
        elif abr == 0:
            dprint(True, "Failure - no communication at any baudrate on port: '{}'".format(port))
        else: # abr = None
            dprint(True, "ERROR: autoPORT: Failure during Serial Communication on port: '{}'".format(port))

    if len(ports_found) == 0:
        errmessage = "ERROR: No communication at any serial port and baudrate"
        ports_found = None
    else:
        errmessage = ""

    debugIndent(0)
    dprint(True, "autoPORT: Done. " + errmessage)
    return ports_found, errmessage


#
# Communication with serial port with exception handling
#
def serialCOMM(ser, sendtxt, returnlength, caller = ("", "", -1), byteformat = True):
    # write to and read from serial port, exit on serial port error
    # when not enough bytes returned, try send+read again up to 3 times.
    # exit if it still fails
    # if byteformat is True, then convert string to list of int
    # before returning the record

    vprint(gglobs.verbose, "serialCOMM: Begin. sendtxt: '{}', caller: '{}'".format(getUnicodeString(sendtxt), caller))
    debugIndent(1)

    rec         = None
    error       = 0
    errmessage  = ""

    while True:
        if ser == None:
            error       = -1
            errmessage  = u"Serial Port is closed"
            break

        time.sleep(0.03)  # occasional failures, when it goes too fast

        try:
            rec = ser.write(sendtxt)  # rec = no of bytes written
        except:
            dprint(True, u"ERROR: serialCOMM: WRITE failed in function serialCOMM")
            dprint(True, u"ERROR: serialCOMM: sys.exc_info(): ", sys.exc_info())
            dprint(True, u"ERROR: serialCOMM: caller is: {} in line no:{}".format(caller[0], caller[1]))
            #dprint(True, traceback.format_exc()) # more extensive info
            try:
                ser.close()
            except:
                pass

            rec         = None
            error       = -1
            errmessage  = u"ERROR: serialCOMM: WRITE failed in function serialCOMM. See log for details"
            break

        time.sleep(0.03)

        #print "\nserialCOMM: after ser.write({}): serial.in_waiting:{}".format(sendtxt, gglobs.ser.in_waiting)
        #print "serialCOMM: after ser.write: serial.out_waiting:", gglobs.ser.out_waiting

        try:
            rec = ser.read(returnlength)
        except:
            dprint(True, u"ERROR: serialCOMM: READ failed in function serialCOMM")
            dprint(True, u"ERROR: serialCOMM: sys.exc_info(): ", sys.exc_info())
            dprint(True, u"ERROR: serialCOMM: caller is: {} in line no:{}".format(caller[0], caller[1]))
            dprint(True, traceback.format_exc()) # more extensive info
            try:
                ser.close()
            except:
                pass

            rec         = None
            error       = -1
            errmessage  = u"ERROR: serialCOMM: READ failed in function serialCOMM. See log for details"
            break

        #print "serialCOMM: after ser.read: serial.in_waiting:", gglobs.ser.in_waiting
        #print "serialCOMM: after ser.read: serial.out_waiting:", gglobs.ser.out_waiting

        if len(rec) < returnlength:
            fprint("Found a device but got communication error. Retrying.")

            dprint(True, "ERROR: serialCOMM: Received length: {} is less than requested: {}".format(len(rec), returnlength))

            dprint(gglobs.debug, "rec (raw):", rec)
            strrec = ""
            for a in rec:
                strrec += str(ord(a)) + ", "
            dprint(gglobs.debug, "rec (val):", strrec[:-2])

            error       = 1
            errmessage  = "ERROR: serialCOMM: Record too short: Received bytes: {} < requested: {}".format(len(rec), returnlength)

            # RETRYING
            count    = 0
            countmax = 3
            while True:
                count += 1
                #beep()
                dprint(True, "RETRY: serialCOMM: to get full return record, trial #", count)


                time.sleep(1)
                ser.write(sendtxt)

                time.sleep(0.3)
                rec = ser.read(returnlength)

                if len(rec) == returnlength:
                    dprint(True,  u"RETRY: serialCOMM: returnlength is {} bytes. OK now. Continuing normal cycle".format(len(rec)))
                    errmessage += u"; ok after {} retry".format(count)
                    break
                else:
                    #dprint(True,  u"RETRY: serialCOMM: returnlength is {} bytes. Still NOT ok; trying again".format(len(rec)))
                    pass

                if count >= countmax:
                    dprint(True, u"RETRY: serialCOMM: Retried {} times, always failure, giving up".format(count))
                    dprint(True, u"ERROR: serialCOMM: Serial communication error. Is the baudrate set correctly?")
                    rec         = None
                    error       = -1
                    errmessage  = u"ERROR communicating via serial port. Giving up."
                    break

                fprint("ERROR communicating via serial port. Retrying again.")

        if byteformat and rec != None:
            #dprint(gglobs.debug, "rec=", rec)
            rec = map(ord,rec) # convert string to list of int
        break

    debugIndent(0)
    vprint(gglobs.verbose, "serialCOMM: Done. ")

    return (rec, error, errmessage)


def serialOPEN(usbport, baudrate, timeout):
    """Tries to open the serial port
    Return: on success: ser, ""
            on failure: None, errmessage
    """

    msg         = u"port='{}', baudrate={}, timeout={}".format(usbport, baudrate, timeout)
    gglobs.ser  = None
    error       = 0
    errmessage  = ""
    errmessage1 = ""

    dprint(gglobs.debug, "serialOPEN: Begin. Settings: " + msg)
    debugIndent(1)

    while True:
        try:
            gglobs.ser = serial.Serial(usbport, baudrate, timeout=timeout)
            # ser is like: Serial<id=0x7f2014d371d0, open=True>(port='/dev/gqgmc', baudrate=115200, bytesize=8, parity='N', stopbits=1, timeout=20, xonxoff=False, rtscts=False, dsrdtr=False)
        except serial.SerialException as e:
            errmessage1 = u"ERROR: Connection problem with device @ " + msg + ( str(e) if str(e) != None else str(sys.exc_info()))
            gglobs.ser  = None
            dprint(True, errmessage1 )
            break

        # NOTE: the device port can be opened without error even when no
        # communication can be done, e.g. due to wrong baudrate
        # This tests for successful communication
        dprint(gglobs.debug, u"Port opened ok, now testing communication")
        try:
            ver, error, errmessage = getVER(gglobs.ser)
        except Exception as e:
            errmessage1  = u"ERROR: Port opened ok, but Communication failed. Is baudrate correct?"
            exceptPrint(e, sys.exc_info(), errmessage1)
            gglobs.ser  = None
            break

        if error < 0:
            errmessage1  = u"ERROR: Communication problem: " + errmessage
            dprint(True, errmessage1 )
            gglobs.ser  = None
            break

        if ver.startswith("GMC"):
            gglobs.deviceDetected = ver
        else:
            gglobs.deviceDetected = u"ERROR: No device detected"
            dprint(True, u"ERROR: No device detected")
            gglobs.ser  = None

        break

    if gglobs.ser == None:
        rmsg = u"{}".format(errmessage1.replace('[Errno 2]', '<br>'))
    else:
        dprint(gglobs.debug, "Communication ok")
        rmsg = ""

    debugIndent(0)
    dprint(gglobs.debug, "serialOPEN: Done.")

    return gglobs.ser, rmsg


def getDeviceConfig():
    """ Get the device configuration"""

    dprint(gglobs.debug, "getDeviceConfig: Begin.")
    debugIndent(1)

    try:
        cfg, error, errmessage = getCFG(gglobs.ser)
    except:
        cfg = None
        dprint(gglobs.debug, "ERROR: not getting config, sys.exc_info:'{}'".format(sys.exc_info()))

    gglobs.cfg = cfg

    debugIndent(0)
    dprint(gglobs.debug, "getDeviceConfig: Done.")


def fprintDeviceInfo():
    """Print device info via fprint"""

    dprint(gglobs.debug, "fprintDeviceInfo: Begin.")
    debugIndent(1)

    forcedebug = "debug"
    while True:
        fprint(header(u"Device Info"), forcedebug)

        cfg, error, errmessage     = getCFG(gglobs.ser)
        gglobs.cfg = cfg
        if error < 0:
            fprint(u"ERROR trying to read Device Configuration: '{}'".format(errmessage), forcedebug)
            #cfg = [255] * 512    # dummy list to satisfy functions

        # device name
        fprint(u"Selected device (Model Name):", gglobs.device, forcedebug)

        # device name and firmware version reading from device
        ver, error, errmessage = getVER(gglobs.ser)
        if error < 0:
            fprint(u"ERROR detecting device & firmware: '{}'".format(errmessage), forcedebug)
        else:
            try:
                fprint(u"Detected device & firmware:",  ver, forcedebug)
                gglobs.deviceDetected = ver
            except:
                # ver is not in ASCII format
                errmessage  = "ERROR detecting device & firmware; not ASCII - got:" + str( map(ord,ver))
                fprint(errmessage, forcedebug)

        # serial number
        sn, error, errmessage = getSERIAL(gglobs.ser)
        if error < 0:
            fprint(u"ERROR getting Device Serial Number: '{}'".format(errmessage), forcedebug)
        else:
            dprint(gglobs.debug, "Serial Number is:", sn)

        # connected port
        fprint(u"Device connected with port:", u"{} (Timeout:{} sec)".format(gglobs.usbport, gglobs.timeout), forcedebug)

        # baudrate as read from device
        fprint(u"Baudrate read from device:", getBAUDRATE(), forcedebug)

        # baudrate as set in program
        fprint(u"Baudrate set by program:",  gglobs.baudrate, forcedebug)

        # get date and time from device, compare with computer time
        rec, error, errmessage = getDATETIME(gglobs.ser)

        if error < 0:
            fprint(u"Device Date and Time:", errmessage, forcedebug)
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

            fprint("Date and Time from device:", devtime, forcedebug)
            fprint("Date and Time from computer:", cmptime, forcedebug)
            fprint("", dtxt, forcedebug)

        # voltage
        rec, error, errmessage = getVOLT(gglobs.ser)
        if error < 0:
            fprint(u"Device Battery Voltage:", "{}".format(errmessage), forcedebug)
        else:
            fprint(u"Device Battery Voltage:", "{} V".format(rec), forcedebug)

        # temperature
        rec, error, errmessage = getTEMP(gglobs.ser)
        if error < 0:
            fprint(u"ERROR getting Device Temperature: '{}'".format(errmessage), forcedebug)
        else:
            fprint(u"Device Temperature:", u"{} °C ".format(rec ), forcedebug)
            fprint(u"", "(only GMC-320 Re.3.01 and later)")

        # gyro
        rec, error, errmessage = getGYRO(gglobs.ser)
        if error < 0:
            fprint(u"ERROR getting Device Gyro Data: '{}'".format(errmessage), forcedebug)
        else:
            fprint(u"Device Gyro data:", rec, forcedebug)
            fprint(u"", "(only GMC-320 Re.3.01 and later)")

        # power state
        fprint(u"Device Power State:", isPowerOn(), forcedebug)

        # Alarm state
        fprint(u"Device Alarm State:", isAlarmOn(), forcedebug)

        # Speaker state
        fprint(u"Device Speaker State:", isSpeakerOn(), forcedebug)

        # Save Data Type
        sdt, sdttxt = getSaveDataType()
        fprint(u"Device Save Mode:", sdttxt, forcedebug)

        # MaxCPM
        try:
            if gglobs.device in ["GMC-300", "GMC-300E+", "GMC-320", "GMC-320+"]: # all 300series
                value = cfg[gglobs.cfgOffsetMaxCPM] * 256 + cfg[gglobs.cfgOffsetMaxCPM +1]
            else:
                value = "Unknown due to unddisclosed firmware changes"
        except:
            value = "Unknown"
        fprint(u"Max CPM (invalid if 65535!):", value, forcedebug)

        # Calibration
        fprint(ftextCalibration(), forcedebug)

        break

    debugIndent(0)
    dprint(gglobs.debug, "fprintDeviceInfo: Done.")


def ftextCFG():
    """Return device configuration as formatted text"""

    fText = u""

    cfg, error, errmessage = getCFG(gglobs.ser)
    gglobs.cfg  = cfg
    if error < 0:
        fText += errmessage
    else:
        lencfg      = len(cfg)
        fText += u"The configuration is:  (Format: dec byte_number: hex value=dec value)\n"

        while cfg[-1] == 255:  cfg.pop()  # remove trailing FF

        lencfg_pop = len(cfg)
        for i in range(0, lencfg_pop, 6):
            pcfg = ""
            for j in range(0, 6):
                k = i+j
                if k < lencfg_pop: pcfg += u"%3d:%02x=%3d |" % (k, cfg[k], cfg[k])
            fText += pcfg[:-2] + "\n"

        if lencfg_pop < lencfg:
            fText += u"Remaining {} values up to address {} are all 'ff=255'\n".format(lencfg -lencfg_pop, lencfg - 1)

        asc = convertBytesToAscii(map(chr, cfg))
        fText += u"The configuration as ASCII is (non-ASCII characters as '.'):\n" + asc

    dprint(gglobs.debug, "ftextCFG: " + fText)

    return unicode(fText)


def ftextCalibration():
    """extract Calibration from device"""

    cfg = gglobs.cfg

    try:
        cal_CPM = []
        cal_CPM.append(struct.unpack(">H", chr(cfg[8] ) + chr(cfg[9] ) )[0])
        cal_CPM.append(struct.unpack(">H", chr(cfg[14]) + chr(cfg[15]) )[0])
        cal_CPM.append(struct.unpack(">H", chr(cfg[20]) + chr(cfg[21]) )[0])

        if gglobs.device in ["GMC-500", "GMC-500+", "GMC-600", "GMC-600+"]:
            #print "using 500er, 600er:  use big-endian"
            fString = ">f"
        else:
            #print "using other than 500er and 600er: use little-endian"
            fString = "<f"

        cal_uSv = []
        cal_uSv.append(struct.unpack(fString,  chr(cfg[10] ) + chr(cfg[11]) + chr(cfg[12]) + chr(cfg[13]) )[0])
        cal_uSv.append(struct.unpack(fString,  chr(cfg[16] ) + chr(cfg[17]) + chr(cfg[18]) + chr(cfg[19]) )[0])
        cal_uSv.append(struct.unpack(fString,  chr(cfg[22] ) + chr(cfg[23]) + chr(cfg[24]) + chr(cfg[25]) )[0])

        #print cal_CPM
        #print cal_uSv

        ftext = u"Device Calibration:\n"
        for i in range(0,3):
            if gglobs.device in ["GMC-300", "GMC-300E+", "GMC-320", "GMC-320+"]: # all 300series
                ftext += u"   Calibration Point {:}:  {:6d} CPM ={:7.2f} µSv/h   ({:0.5f} µSv/h / CPM)\n".format(i + 1, cal_CPM[i], cal_uSv[i], cal_uSv[i] / cal_CPM[i])
            else:
                ftext += u"   Calibration Point {:}:  Unknown due to unddisclosed firmware changes\n".format(i + 1)

    except:
        #print sys.exc_info()
        ftext = u"{:35s}{:s}\n".format(u"Device Calibration:", u"Unknown")

    return ftext[:-1] # remove last newline char



