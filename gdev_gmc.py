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
__copyright__       = "Copyright 2016, 2017, 2018, 2019, 2020, 2021"
__credits__         = ["Phil Gillaspy", "GQ"]
__license__         = "GPL3"

# credits:
# device command coding taken from:
# Phil Gillaspy, https://sourceforge.net/projects/gqgmc/
# and GQ document 'GQ-RFC1201.txt'
# (GQ-RFC1201,GQ Geiger Counter Communication Protocol, Ver 1.40 Jan-2015)
# and GQ's disclosure at:
# http://www.gqelectronicsllc.com/forum/topic.asp?TOPIC_ID=4948

from   gsup_utils           import *


# "Power", "Alarm", "Speaker", "SaveDataType"
# common to all GMCs
cfgKeyLow =  \
{
#                                      Index
#    key                Value,    from       to
    "Power"                   : [ None,     (0,        0 + 1) ],
    "Alarm"                   : [ None,     (1,        1 + 1) ],
    "Speaker"                 : [ None,     (2,        2 + 1) ],
    "BackLightTimeoutSeconds" : [ None,     (4,        4 + 1) ],
    "CalibCPM_0"              : [ None,     (8,        8 + 2) ],     # calibration_0 CPM Hi+Lo Byte
    "CalibuSv_0"              : [ None,     (10,      10 + 4) ],     # calibration_0 uSv 4 Byte
    "CalibCPM_1"              : [ None,     (14,      14 + 2) ],     # calibration_1 CPM Hi+Lo Byte
    "CalibuSv_1"              : [ None,     (16,      16 + 4) ],     # calibration_1 uSv 4 Byte
    "CalibCPM_2"              : [ None,     (20,      20 + 2) ],     # calibration_2 CPM Hi+Lo Byte
    "CalibuSv_2"              : [ None,     (22,      22 + 4) ],     # calibration_2 uSv 4 Byte
    "SaveDataType"            : [ None,     (32,      32 + 1) ],     # History Save Data Type
    "MaxCPM"                  : [ None,     (49,      49 + 2) ],     # MaxCPM Hi + Lo Byte
    "nLCDBackLightLevel"      : [ None,     (53,      53 + 1) ],     # Backlightlevel; seems to go from 0 ... 20
    "Battery"                 : [ None,     (56,      56 + 1) ],     # Battery Type: 1 is non rechargeable. 0 is chargeable.
    "Baudrate"                : [ None,     (57,      57 + 1) ],     # Baudrate, coded differently for 300 and 500/600 series
    "ThresholdCPM"            : [ None,     (62,      62 + 2) ],     # yes, at 62! Threshold in CPM (2 bytes)
    "ThresholdMode"           : [ None,     (64,      64 + 1) ],     # yes, at 64! Mode: 0:CPM, 1:µSv/h, 2:mR/h
    "ThresholduSv"            : [ None,     (65,      65 + 4) ],     # yes, at 65! Threshold in usv (4 bytes)
}


# "SSID", "Password", "Website", "URL", "UserID", "CounterID", "Period", "WiFi"
# only WiFi enabled counter
cfgKeyHigh =  \
{
#                     0         1           2                    3                      4
#                     GMCmap    cfgMap      cfg256ndx            cfg512ndx
#                     from GL   from GMC
#                     config    device    # only GMC-320+V5     # GMC-500/600          # GMC500+2.24
    "SSID"        : [ None,     None,     (69,     69 + 16),    (69,     69 + 32) ,    (69,     69 + 64) ],
    "Password"    : [ None,     None,     (85,     85 + 16),    (101,   101 + 32) ,    (133,   133 + 64) ],
    "Website"     : [ None,     None,     (101,   101 + 25),    (133,   133 + 32) ,    (197,   197 + 32) ],
    "URL"         : [ None,     None,     (126,   126 + 12),    (165,   165 + 32) ,    (229,   229 + 32) ],
    "UserID"      : [ None,     None,     (138,   138 + 12),    (197,   197 + 32) ,    (261,   261 + 32) ],
    "CounterID"   : [ None,     None,     (150,   150 + 12),    (229,   229 + 32) ,    (293,   293 + 32) ],
    "Period"      : [ None,     None,     (112,   112 +  1),    (261,   261 +  1) ,    (325,   325 +  1) ], # 0 ... 255
    "WiFi"        : [ None,     None,     (113,   113 +  1),    (262,   262 +  1) ,    (326,   326 +  1) ], # WiFi On=1 Off=0
    "FastEstTime" : [ None,     None,     (255,   255 +  1),    (262,   262 +  1) ,    (328,   328 +  1) ], # Fast Estimate Time:
                                                                                                            # on 500+: 5, 10, 15, 20, 30, 60=sec, 3=dynamic
                                                                                                            # not on 300 series
}


# the History mode of saving
savedatatypes = (
                    "OFF (no history saving)",
                    "CPS, save every second",
                    "CPM, save every minute",
                    "CPM, save hourly average",
                    "CPS, save every second if exceeding threshold",
                    "CPM, save every minute if exceeding threshold",
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

#
# Commands and functions implemented in GMC device
#

def getGMC_VER():
    # Get hardware model and version
    # send <GETVER>> and read 14 bytes
    # returns total of 14 bytes ASCII chars from GQ GMC unit.
    # includes 7 bytes hardware model and 7 bytes firmware version.
    # e.g.: 'GMC-300Re 4.20'
    # ATTENTION: new counters may deliver 15 bytes. e.g. "GMC-500+Re 1.18",
    # the 500 version with firmware 1.18
    # These versions are called by requesting14 bytes and then checking for Extrabytes

    # see: http://www.gqelectronicsllc.com/forum/topic.asp?TOPIC_ID=4948 Reply #30
    # Quote EmfDev:
    # "On the 500 and 600 series, the GETVER return can be any length.
    # So far its only 14 bytes or 15 bytes. But it should return any given
    # model name completely so the length is variable.
    # And the '+' sign is included in the model name. e.g. GMC500+Re 1.10
    # But I don't think the 300 or 320 has been updated so maybe you can ask
    # support for the fix."


    fncname = "getGMC_VER:"

    dprint(fncname)
    setDebugIndent(1)
    recd    = None

    rec, error, errmessage = serialGMC_COMM(b'<GETVER>>', 14, orig(__file__))
    #for i in range(0, 14): print("i={:2d}  rec={:08b}  rec={:02X}".format(i, rec[i], rec[i]))

    if error >= 0:
        try:
            recd = rec.decode('UTF-8')    # convert from bytes to str
        except Exception as e:
            error      = -1
            errmessage = "ERROR getting Version - Bytes are not ASCII: " + str(rec)
            exceptPrint(e, sys.exc_info(), errmessage)
            recd       = str(rec)

###############################################################################
# FOR TESTING ONLY - start GL with command: 'testing' #########################
# use in combination with testing setting in getGMC_cfg
    if gglobs.testing:
        pass
        #recd = "GMC-300Re 3.20"
        #recd = "GMC-300Re 4.20"
        #recd = "GMC-300Re 4.22"
        #recd = "GMC-320Re 3.22"    # device used by user katze
        #recd = "GMC-320Re 4.19"
        recd = "GMC-320Re 5.xx"     # with WiFi
        #recd = "GMC-500Re 1.00"
        #recd = "GMC-500Re 1.08"
        #recd = "GMC-500+Re 1.0x"
        #recd = "GMC-500+Re 1.18"
        #recd = "GMC-600Re 1.xx"
        #recd = "GMC-600+Re 2.xx"   # fictitious device; not (yet) existing
                                    # simulates the bug in the 'GMC-500+Re 1.18'
        #recd = ""
# TESTING END #################################################################
###############################################################################


    try:    lenrec = len(rec)
    except: lenrec = None

    dprint(fncname + "len:{}, rec:\"{}\", recd='{}', err={}, errmessage='{}'".format(lenrec, rec, recd, error, errmessage))

    setDebugIndent(0)

    return (recd, error, errmessage)


def getGMC_ValuefromRec(rec, maskHighBit=False):
    """calclate the CPM, CPS value from a 2 or 4 byte record"""

    if      gglobs.GMCnbytes == 2 and maskHighBit==True:   value = (rec[0] & 0x3f) << 8 | rec[1]
    elif    gglobs.GMCnbytes == 2 and maskHighBit==False:  value = rec[0]          << 8 | rec[1]
    elif    gglobs.GMCnbytes == 4 :                        value = ((rec[0]        << 8 | rec[1]) << 8 | rec[2]) << 8 | rec[3]

    return value


def getGMC_Values(varlist):
    """return all values in the varlist
    NOTE: the getGMC_CPM/S[L | H] functions all return (value, error, errmessage)
          here only value will be forwarded
    """

    fncname = "getGMC_Values: "

    alldata = {}

    for vname in varlist:
        if   vname == "CPM":    alldata[vname] = getGMC_CPM ()[0]    # CPM counts per MINUTE
        elif vname == "CPS":    alldata[vname] = getGMC_CPS ()[0]    # CPS counts per SECOND
        elif vname == "CPM1st": alldata[vname] = getGMC_CPML()[0]    # CPM from 1st tube, normal tube
        elif vname == "CPS1st": alldata[vname] = getGMC_CPSL()[0]    # CPS from 1st tube, normal tube
        elif vname == "CPM2nd": alldata[vname] = getGMC_CPMH()[0]    # CPM from 2nd tube, extra tube
        elif vname == "CPS2nd": alldata[vname] = getGMC_CPSH()[0]    # CPS from 2nd tube, extra tube
        elif vname == "CPM3rd":
            # try, in case CPS1st had not been defined
            try:    alldata[vname] = getGMC_CPMfromCPS(alldata["CPS1st"]) # calculate CPM from CPS* reading
            except: alldata[vname] = gglobs.NAN

        elif vname == "CPS3rd":
            alldata[vname] = getGMC_CPM_FET(alldata["CPS1st"])       # counts per MINUTE with simulated Fast Estimate Time

        elif vname == "X":      alldata[vname] = getGMC_DeltaTime()  # Delta Time "computer minus device" (negative if device is faster than computer)

    printLoggedValues(fncname, varlist, alldata)

    return alldata


def getGMC_CPM_FET(lastcps):
    """calculate CPM from the last N values of CPS;
    N is used as in Fast Estimate Time, i.e. N = FET = 3, 5, 10, 15, 20, 30, 60
    used in getGMC_Values:  cps data from CPS1st, CPM mapped to CPM"""

    """
    from: http://www.gqelectronicsllc.com/forum/topic.asp?TOPIC_ID=9506
    reply#29, EmfDev:

        The calculation for fast Estimate is:
        Let x = duration in seconds
        Estimated CPM = SUM(Last X seconds CPS reading) * (60/X)
        e.g. for 5 sec fast estimate. (e.g. [1, 0, 1, 0, 2] ==> sum = 4)
        Estimated CPM = 4 * 60/5 = 4*12 = 48.

        for Dynamic Fast Estimate:
        x varies depending on how stable the data is from 3 seconds to 60 seconds.
        If the latest few CPS is significantly higher than the average CPS then the
        x goes to 3 for 3 seconds and then starts going to 60 as long as the CPS is
        stable or around certain range from the average CPS. If dynamic estimate
        reaches 60 seconds reading then it becomes the same as 60 second reading,
        then when there is sudden change in CPS again it will trigger to change
        back to estimate faster.

        These numbers are called "estimate" for a reason and so the accuracy is not
        that great. Some users who survey the unknown do not want to put the unit
        there for too long and just wants to get an estimate or check if there is
        radiation.
    """

    # keep np array at 60 values and use last 60 only
    gglobs.GMCEstFET = np.append(gglobs.GMCEstFET, lastcps)[1:]

    # estimate 60 sec based on last FET counts
    try:    FET = gglobs.GMC_FastEstTime
    except: FET = 60

    return int(np.nansum(gglobs.GMCEstFET[-FET:]) * 60 / FET) # without int a blob is saved to DB!



def getGMC_CPMfromCPS(lastcps):
    """calculate CPM from the last 60 values of CPS;
    used in getGMC_Values:  cps data from CPS1st, CPM mapped to CPM3rd"""

    # keep np array at 60 values and use last 60 only
    gglobs.GMCLast60CPS = np.append(gglobs.GMCLast60CPS, lastcps)[1:]

    return int(np.nansum(gglobs.GMCLast60CPS)) # without int a blob is saved to DB!



def getGMC_CPM():
    # Get current CPM value
    # send <GETCPM>> and read 2 bytes
    # In total 2 bytes data are returned from GQ GMC unit
    # as a 16 bit unsigned integer.
    # The first byte is MSB byte data and second byte is LSB byte data.
    # e.g.: 00 1C  -> the returned CPM is 28
    # e.g.: 00 1C  -> the returned CPM is 28
    # e.g.: 0B EA  -> the returned CPM is 3050
    #
    # return CPM, error, errmessage

    wprint("getGMC_CPM: standard command")
    setDebugIndent(1)

    value = gglobs.NAN
    rec, error, errmessage = serialGMC_COMM(b'<GETCPM>>', gglobs.GMCnbytes, orig(__file__))
    if error >= 0:
        value = getGMC_ValuefromRec(rec, maskHighBit=False)
        value = scaleVarValues("CPM", value, gglobs.ValueScale["CPM"])

    wprint("getGMC_CPM: rec= {}, value= {}, err= {}, errmsg= {}".format(rec, value, error, errmessage ))

    setDebugIndent(0)
    return (value, error, errmessage)


def getGMC_CPS():
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

    wprint("getGMC_CPS: standard command")
    setDebugIndent(1)

    value = gglobs.NAN
    rec, error, errmessage = serialGMC_COMM(b'<GETCPS>>', gglobs.GMCnbytes, orig(__file__))
    if error >= 0:
        value = getGMC_ValuefromRec(rec, maskHighBit=True)
        value = scaleVarValues("CPS", value, gglobs.ValueScale["CPS"])

    wprint("getGMC_CPS: rec=", rec, ", value=", value)

    setDebugIndent(0)
    return (value, error, errmessage)


def getGMC_CPML():
    """get CPM from High Sensitivity tube that should be the 'normal' tube"""

    wprint("getGMC_CPML: 1st tube, HIGH sensitivity")
    setDebugIndent(1)

    value = gglobs.NAN
    rec, error, errmessage = serialGMC_COMM(b'<GETCPML>>', gglobs.GMCnbytes, orig(__file__))
    if error >= 0:
        value = getGMC_ValuefromRec(rec, maskHighBit=False)
        value = scaleVarValues("CPM1st", value, gglobs.ValueScale["CPM1st"])

    wprint("getGMC_CPML: rec=", rec, ", value=", value)

    setDebugIndent(0)
    return (value, error, errmessage)


def getGMC_CPMH():
    """get CPM from Low Sensitivity tube that should be the 2nd tube in the 500+"""

    wprint("getGMC_CPMH: 2nd tube, LOW sensitivity")
    setDebugIndent(1)

    value = gglobs.NAN
    rec, error, errmessage = serialGMC_COMM(b'<GETCPMH>>', gglobs.GMCnbytes, orig(__file__))
    if error >= 0:
        value = getGMC_ValuefromRec(rec, maskHighBit=False)
        value = scaleVarValues("CPM2nd", value, gglobs.ValueScale["CPM2nd"])

    wprint("getGMC_CPMH: rec=", rec, ", value=", value)

    setDebugIndent(0)
    return (value, error, errmessage)



def getGMC_CPSL():
    """get CPS from High Sensitivity tube that should be the 'normal' tube"""

    wprint("getGMC_CPSL: 1st tube, HIGH sensitivity")
    setDebugIndent(1)

    value = gglobs.NAN
    rec, error, errmessage = serialGMC_COMM(b'<GETCPSL>>', gglobs.GMCnbytes, orig(__file__))
    if error >= 0:
        value = getGMC_ValuefromRec(rec, maskHighBit=True)
        value = scaleVarValues("CPS1st", value, gglobs.ValueScale["CPS1st"])

    wprint("getGMC_CPSL: rec=", rec, ", value=", value)

    setDebugIndent(0)
    return (value, error, errmessage)


def getGMC_CPSH():
    """get CPS from Low Sensitivity tube that should be the 2nd tube in the 500+"""

    wprint("getGMC_CPSH: 2nd tube, LOW sensitivity")
    setDebugIndent(1)

    value = gglobs.NAN
    rec, error, errmessage = serialGMC_COMM(b'<GETCPSH>>', gglobs.GMCnbytes, orig(__file__))
    if error >= 0:
        value = getGMC_ValuefromRec(rec, maskHighBit=True)
        value = scaleVarValues("CPS2nd", value, gglobs.ValueScale["CPS2nd"])

    wprint("getGMC_CPSH: rec=", rec, ", value=", value)

    setDebugIndent(0)
    return (value, error, errmessage)


def turnGMC_HeartbeatOn():
    # 3. Turn on the GQ GMC heartbeat
    # Note:     This command enable the GQ GMC unit to send count per second data to host every second automatically.
    # Command:  <HEARTBEAT1>>
    # Return:   A 16 bit unsigned integer is returned every second automatically. Each data package consist of 2 bytes data from GQ GMC unit.
    #           The first byte is MSB byte data and second byte is LSB byte data.
    # e.g.:     10 1C     the returned 1 second count is 28.   Only lowest 14 bits are used for the valid data bit.
    #           The highest bit 15 and bit 14 are reserved data bits.
    # Firmware supported:  GMC-280, GMC-300  Re.2.10 or later

    dprint("turnGMC_HeartbeatOn:")
    setDebugIndent(1)

    if gglobs.GMCser == None:
        rec         = ""
        error       = 1
        errmessage  = "No serial connection"
    else:
        rec, error, errmessage = serialGMC_COMM(b'<HEARTBEAT1>>', 0, orig(__file__))

    dprint("turnGMC_HeartbeatOn: rec='{}', err={}, errmessage='{}'".format(rec, error, errmessage))

    setDebugIndent(0)

    return (rec, error, errmessage)


def turnGMC_HeartbeatOFF():
    # 4. Turn off the GQ GMC heartbeat
    # Command:  <HEARTBEAT0>>
    # Return:   None
    # Firmware supported:  Re.2.10 or later

    dprint("turnGMC_HeartbeatOFF:")
    setDebugIndent(1)

    if gglobs.GMCser == None:
        rec         = ""
        error       = 1
        errmessage  = "No serial connection"

    else:
        rec, error, errmessage = serialGMC_COMM(b'<HEARTBEAT0>>', 0, orig(__file__))

    dprint("turnGMC_HeartbeatOFF: rec='{}', err={}, errmessage='{}'".format(rec, error, errmessage))

    setDebugIndent(0)

    return (rec, error, errmessage)


def getGMC_VOLT():
    # Get battery voltage status
    # send <GETVOLT>> and read 1 byte
    # returns one byte voltage value of battery (X 10V)
    # e.g.: return 62(hex) is 9.8V
    # Example: Geiger counter GMC-300E+
    # with Li-Battery 3.7V, 800mAh (2.96Wh)
    # -> getGMC_VOLT reading is: 4.2V
    # -> Digital Volt Meter reading is: 4.18V
    #
    # GMC 500/600 is different. Delivers 5 ASCII bytes
    # z.B.[52, 46, 49, 49, 118] = "4.11v"

    dprint("getGMC_VOLT:")
    setDebugIndent(1)

    if gglobs.GMCser == None:
        rec         = ""
        error       = 1
        errmessage  = "No serial connection"

    else:
        rec, error, errmessage = serialGMC_COMM(b'<GETVOLT>>', gglobs.GMCvoltagebytes, orig(__file__))
        dprint("getGMC_VOLT: VOLT: raw:", rec)

        ######## TESTING (uncomment all 4) #############
        #rec         = b'3.76v'              # 3.76 Volt
        #error       = 1
        #errmessage  = "testing"
        #dprint("getGMC_VOLT: TESTING with rec=", rec, debug=True)
        ################################################

        if error == 0 or error == 1:
            if gglobs.GMCvoltagebytes == 1:
                rec = str(rec[0]/10.0)

            elif gglobs.GMCvoltagebytes == 5:
                rec = rec.decode('UTF-8')

            else:
                rec = str(rec) + " @config: GMCvoltagebytes={}".format(gglobs.GMCvoltagebytes)

        else:
            rec         = "ERROR"
            error       = 1
            errmessage  = "getGMC_VOLT: ERROR getting voltage"

    dprint("getGMC_VOLT: Using config setting GMCvoltagebytes={}:  Voltage='{}', err={}, errmessage='{}'".format(gglobs.GMCvoltagebytes, rec, error, errmessage))
    setDebugIndent(0)

    return (rec, error, errmessage)


def getGMC_SPIR(address = 0, datalength = 4096):
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

    # BUG ALERT - WORKAROUND ##################################################
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
    # End BUG ALERT - WORKAROUND ##############################################


    # address: pack into 4 bytes, big endian; then clip 1st byte = high byte!
    ad = struct.pack(">I", address)[1:]

    # datalength: pack into 2 bytes, big endian; use all bytes
    # but adjust datalength to fix bug!
    if gglobs.GMC_SPIRbugfix:   dl = struct.pack(">H", datalength - 1)
    else:                       dl = struct.pack(">H", datalength    )

    dprint("getGMC_SPIR: SPIR requested: address: {:5d}, datalength:{:5d}   (hex: address: {:02x} {:02x} {:02x}, datalength: {:02x} {:02x})".\
            format(address, datalength, ad[0], ad[1], ad[2], dl[0], dl[1]))
    setDebugIndent(1)

    rec, error, errmessage = serialGMC_COMM(b'<SPIR' + ad + dl + b'>>', datalength, orig(__file__)) # returns bytes

    if rec != None :    msg = "datalength={:4d}".format(len(rec))
    else:               msg = "ERROR: No data received!"

    dprint("getGMC_SPIR: received: {}, err={}, errmessage='{}'".format(msg, error, errmessage))
    setDebugIndent(0)

    return (rec, error, errmessage)


def getGMC_HeartbeatCPS():
    """read bytes until no further bytes coming"""
    # Caution: untested under Py3; might not be working

    if not gglobs.debug: return  # execute only in debug mode

    eb= 0
    while True:                  # read more until nothing is returned
                                 # (actually, never more than 1 more is returned)
        eb += 1
        rec = ""
        rec = gglobs.GMCser.read(2)
        cps =  ((rec[0] & 0x3f) << 8 | rec[1])
        #print( "eb=", eb, "cps:", cps)
        break

    return cps


def getGMC_ExtraByte():
    """read single bytes until no further bytes coming"""

    fncname = "getGMC_ExtraByte: "

    # failed when called from 2nd instance of GeigerLog; just to avoid error
    try:    bytesWaiting = gglobs.GMCser.in_waiting
    except: bytesWaiting = 0

    xrec = b""
    if bytesWaiting == 0:
        wprint(fncname + "No extra bytes waiting for reading")
    else:
        # read single byte until nothing is in_waiting
        vprint(fncname + "Bytes waiting: {}".format(bytesWaiting), verbose=True)
        while gglobs.GMCser.in_waiting:
            try:
                x = gglobs.GMCser.read(1)
                time.sleep(0.001) # it may be running too fast and missing waiting bytes. Happened with 500+
            except Exception as e:
                edprint(fncname + "Exception: {}".format(e))
                exceptPrint(e, sys.exc_info(), fncname + "Exception: ")
                x = b""

            if len(x) == 0: break
            xrec += x

        vprint(fncname + "Got {} extra bytes from reading-pipeline: ".format(len(xrec)), list(xrec), verbose=True)
        vprint(fncname + "Extra bytes as ASCII: (0xFF --> F) {}".format(BytesAsASCIIFF(xrec)), verbose=True)

    return xrec


def getGMC_CFG():
    # Get configuration data
    # send <GETCFG>> and read 256 bytes
    # returns
    # - the cfg as a Python bytes string, should be 256 or 512 bytes long
    # - the error value (0, -1, +1)
    # - the error message as string
    # has set gglobs.GMCcfg with read cfg

    # NOTE: 300series uses 256 bytes; 500 and 600 series 512 bytes
    # config size is determined by deviceproperties

    dprint("getGMC_CFG:")
    setDebugIndent(1)

    getGMC_ExtraByte()  # cleaning buffer before getting cfg (some problem in the 500)

    cfg         = b""
    error       = 0
    errmessage  = ""

    cfg, error, errmessage = serialGMC_COMM(b'<GETCFG>>', gglobs.GMCconfigsize, orig(__file__))
    #print("getGMC_CFG: cfg:", type(cfg), cfg)
    #~print("getGMC_CFG: gglobs.GMCconfigsize: ", gglobs.GMCconfigsize)
    #~print("getGMC_CFG: type gglobs.GMCconfigsize: ", type(gglobs.GMCconfigsize))

###############################################################################
####### BEGIN TESTDATA ########################################################
# replaces current cfg with cfg from other runs
# requires that a testdevice was activated in getGMC_VER
# only do this when command 'testing' was given on command line !

    if gglobs.testing:
        if gglobs.GMCconfigsize == 512:
            # using a 512 bytes sequence; data from a GMC-500(non-plus) readout
            #
            # power is OFF:
            cfg500str = "01 00 00 02 1F 00 00 64 00 3C 3E C7 AE 14 27 10 42 82 00 00 00 19 41 1C 00 00 00 3F 00 00 00 00 02 02 00 00 00 00 FF FF FF FF FF FF 00 01 00 78 0A FF FF 3C 00 05 FF 01 00 00 0A 00 01 0A 00 64 00 3F 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 77 77 77 2E 67 6D 63 6D 61 70 2E 63 6F 6D 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 6C 6F 67 32 2E 61 73 70 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 02 00 02 11 05 1E 10 34 05 FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF"
            cfg500    = cfg500str.split(' ')
            # power is ON:
            cfg500    = ["0"] + cfg500[1:]
            #print("cfg500:\n", len(cfg500), cfg500)

            cfg = b''
            for a in cfg500: cfg += bytes([int(a, 16)]) # using hex data

        elif "GMC-320Re 5." in gglobs.GMCDeviceDetected :  # 320v5 device (with WiFi)
            cfg = (cfg[:69] + b'abcdefghijklmnopqrstuvwxyz0123456789' * 10)[:256] # to simulate WiFi settings just fill up config

        elif gglobs.GMCconfigsize == 256: # 320v4 device
            # next line from 320+ taken on: 2017-05-26 15:29:38
            # power is off:
            cfg320plus = [255, 0, 0, 2, 31, 0, 0, 100, 0, 60, 20, 174, 199, 62, 0, 240, 20, 174, 199, 63, 3, 232, 0, 0, 208, 64, 0, 0, 0, 0, 63, 0, 2, 2, 0, 0, 0, 0, 255, 255, 255, 255, 255, 255, 0, 1, 0, 120, 25, 255, 255, 60, 1, 8, 255, 1, 0, 254, 10, 0, 1, 10, 0, 100, 0, 0, 0, 0, 63, 17, 5, 23, 16, 46, 58, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255]
            # power is on:
            cfg320plus = [  0] + cfg320plus[1:]

            cfg = b''
            for a in cfg320plus: cfg += bytes([a]) # using dec data

        else:
            pass

        error       = 1
        errmessage  = "SIMULATION"

        print("TESTDATA: cfg:", len(cfg), type(cfg))
        print(BytesAsHex(cfg))
        print(BytesAsASCIIFF(cfg))
        print("TESTDATA:  END ------------")

####### END TESTDATA ##########################################################
###############################################################################

    gglobs.GMCcfg = cfg  # set the global value with whatever you got, real or fake data

    if cfg == None:
        dprint("getGMC_CFG: ERROR: Failed to get any configuration data", debug=True)

    else: # cfg != None
        dprint("getGMC_CFG: Got {} bytes as {} (set werbose for printout)"  .format(len(cfg), type(cfg)))
        wprint("getGMC_CFG: CFG as HEX  : \n{}"    .format(BytesAsHex(cfg)))
        wprint("getGMC_CFG: CFG as DEC  : \n{}"    .format(BytesAsDec(cfg)))
        wprint("getGMC_CFG: CFG as ASCII: \n{}"    .format(BytesAsASCIIFF(cfg)))

        if gglobs.GMCendianness == 'big':  fString = ">f"  # use big-endian ---   500er, 600er:
        else:                              fString = "<f"  # use little-endian -- other than 500er and 600er:

        try:
            for key in cfgKeyLow:
                cfgKeyLow[key][0] = cfg[cfgKeyLow[key][1][0] : cfgKeyLow[key][1][1]]
        except Exception as e:
            edprint("getGMC_CFG: Exception: cfgKeyLow[{}]: {}".format(key, e))
            exceptPrint(e, sys.exc_info(), "getGMC_CFG: Exception: cfgKeyLow[{}]".format(key))
            return cfg, -1, "getGMC_CFG: Exception: {}".format(e)

        try:
            #  ("Power", "Alarm", "Speaker", "CalibCPM_0", "CalibuSv_0", "CalibCPM_1", "CalibuSv_0", "CalibCPM_2", "CalibuSv_0", "SaveDataType", "MaxCPM", "Baudrate", "Battery")
            #~cfgKeyLow["Power"][0]          = cfgKeyLow["Power"][0]        #[0]
            #~cfgKeyLow["Alarm"][0]          = cfgKeyLow["Alarm"][0]        #[0]
            #~cfgKeyLow["Speaker"][0]        = cfgKeyLow["Speaker"][0]      #[0]
            #~cfgKeyLow["SaveDataType"][0]   = cfgKeyLow["SaveDataType"][0] #[0]
            #~cfgKeyLow["Baudrate"][0]       = cfgKeyLow["Baudrate"][0]     #[0]
            #~cfgKeyLow["Battery"][0]        = cfgKeyLow["Battery"][0]      #[0]
            #cfgKeyLow["ThresholdMode"][0]  = cfgKeyLow["ThresholdMode"][0] #[0]

            cfgKeyLow["CalibCPM_0"]  [0]     = struct.unpack(">H",    cfgKeyLow["CalibCPM_0"]  [0] )[0]
            cfgKeyLow["CalibCPM_1"]  [0]     = struct.unpack(">H",    cfgKeyLow["CalibCPM_1"]  [0] )[0]
            cfgKeyLow["CalibCPM_2"]  [0]     = struct.unpack(">H",    cfgKeyLow["CalibCPM_2"]  [0] )[0]

            cfgKeyLow["CalibuSv_0"]  [0]     = struct.unpack(fString, cfgKeyLow["CalibuSv_0"]  [0] )[0]
            cfgKeyLow["CalibuSv_1"]  [0]     = struct.unpack(fString, cfgKeyLow["CalibuSv_1"]  [0] )[0]
            cfgKeyLow["CalibuSv_2"]  [0]     = struct.unpack(fString, cfgKeyLow["CalibuSv_2"]  [0] )[0]

            cfgKeyLow["MaxCPM"    ]  [0]     = struct.unpack(">H",    cfgKeyLow["MaxCPM"]      [0] )[0]

            cfgKeyLow["ThresholdCPM"][0]     = struct.unpack(">H",    cfgKeyLow["ThresholdCPM"][0] )[0]
            cfgKeyLow["ThresholduSv"][0]     = struct.unpack(fString, cfgKeyLow["ThresholduSv"][0] )[0]

        except Exception as e:
            edprint("getGMC_CFG: Exception: set cfgKeyLow[{}]: {}".format("?", e))
            exceptPrint(e, sys.exc_info(), "getGMC_CFG: set cfgKeyLow[{}]".format("?"))
            return cfg, -1, "getGMC_CFG: Exception: set cfgKeyLow[?]: {}".format(e)


        # now get the WiFi part of the config
        ndx = gglobs.GMCcfgWifiCol
        if ndx >= 0:
            #print("ndx = ", ndx)
            for key in cfgKeyHigh:
                #~print("key: ", key)
                if key == "Period":
                    # Period is one byte, value = 0...255 (minutes)
                    cfgKeyHigh[key][1] = str(ord((cfg[cfgKeyHigh[key][ndx][0] : cfgKeyHigh[key][ndx][1]])))

                elif key == "FastEstTime":
                    if cfgKeyHigh[key][ndx][0] != None:
                        # FastEstTime is one byte, value = 3(dynamic), 5,10,15,20,30,60 seconds
                        cfgKeyHigh[key][1] = str(ord((cfg[cfgKeyHigh[key][ndx][0] : cfgKeyHigh[key][ndx][1]])))
                    else:
                        cfgKeyHigh[key][1] = None

                else:
                    try:
                        temp               = cfg[cfgKeyHigh[key][ndx][0] : cfgKeyHigh[key][ndx][1]]
                        cfgKeyHigh[key][1] = temp.replace(b"\x00", b"").replace(b"\xff", b"").decode("UTF-8")
                    except Exception as e:
                        cfgKeyHigh[key][1] = "Failure getting Config: {}".format(e)
                #print("key: {:13s} cfgKeyHigh[][1]: {}".format(key, cfgKeyHigh[key][1]))

        else:
            # no WiFi
            for key in cfgKeyHigh:
                #~cfgKeyHigh[key][1] = "None"
                cfgKeyHigh[key][1] = ""

    setDebugIndent(0)

    return cfg, error, errmessage


def writeGMC_ConfigSingle(cfgaddress, value):
    """prepare cfg by modifying single byte for writing full cfg to the config memory"""

    dprint("writeGMC_ConfigSingle: cfgaddress: {}, value: {}".format(cfgaddress, value))
    setDebugIndent(1)

    # get a fresh config and make a copy
    getGMC_CFG()
    cfgcopy = copy.copy(gglobs.GMCcfg)

    # modify cfgcopy at cfgaddress with value
    cfgcopy = cfgcopy[:cfgaddress] + bytes([value]) + cfgcopy[cfgaddress + 1:]
    wprint("writeGMC_ConfigSingle: new cfg\n", BytesAsHex(cfgcopy))

    writeGMC_Config(cfgcopy)

    setDebugIndent(0)


def writeGMC_Config(config):
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

    def printstr(size, i, c, A0, D0):
        index = 5
        if size == 256: pfs = "i==A0={:>3d}(0x{:02X}), cfgval==D0={:>3d}(0x{:02X})" # formatted print string for single byte address
        else:           pfs = "i==A0={:>3d}(0x{:03X}), cfgval==D0={:>3d}(0x{:02X})" # formatted print string for double byte address
        if i < index or i > (len(cfgstrip) - (index +1)):
            vprint(pfs.format(i, int.from_bytes(A0, byteorder='big'), c, int.from_bytes(D0, byteorder='big')))
        if i == index: vprint("...")


    fncname = "writeGMC_Config: "

    dprint(fncname)
    setDebugIndent(1)

    cfgcopy = copy.copy(config)
    #dprint(fncname + "Config copy: len: {}:\n".format(len(cfgcopy)), BytesAsASCIIFF(cfgcopy))

    if   len(cfgcopy) <= 256 and gglobs.GMCconfigsize == 256:  doUpdate = 256
    elif len(cfgcopy) <= 512 and gglobs.GMCconfigsize == 512:  doUpdate = 512
    else: # ERROR:
        msg  = "Number of configuration data inconsistent with detected device.<br>Updating config will NOT be done, as Device might be damaged by it!"
        efprint(msg)
        dprint(fncname + msg.replace('<br>', ' '), debug=True)
        setDebugIndent(0)
        return

    # remove right side FFs; after erasing th config memory this will be the default anyway
    cfgstrip = cfgcopy.rstrip(b'\xFF')
    #~dprint(fncname + "Config right-stripped from FF: len:{}:\n".format(len(cfgstrip)), BytesAsASCIIFF(cfgstrip))

    # erase config on device
    dprint(fncname + "Erase Config")
    rec = serialGMC_COMM(b'<ECFG>>', 1, orig(__file__))

    dprint(fncname + "Write new Config Data for Config Size: >>>>>>>>>>>>>>>>{}<<<<<<<<<<<<".format(doUpdate))
    setDebugIndent(1)
    if doUpdate == 256:
        # SINGLE byte address writing config of up to 256 bytes
        for i, c in enumerate(cfgstrip):
            A0 = bytes([i])             # single byte address
            D0 = bytes([c])
            printstr(256, i, c, A0, D0)
            setDebugIndent(1)
            rec = serialGMC_COMM(b'<WCFG' + A0 + D0 + b'>>', 1, orig(__file__))
            setDebugIndent(0)

    else: # doUpdate == 512
        # DOUBLE byte address writing config of up to 512 bytes
        for i, c in enumerate(cfgstrip):
            A0 = struct.pack(">H", i)   # pack address into 2 bytes, big endian
            D0 = bytes([c])
            printstr(512, i, c, A0, D0)
            setDebugIndent(1)
            rec = serialGMC_COMM(b'<WCFG' + A0 + D0 + b'>>', 1, orig(__file__))
            setDebugIndent(0)

            # GMC-500 always times out at byte #11.
            # solved: it is a bug in the firmware; data resulted in ">>>"

    setDebugIndent(0)

    # activate new config on device
    updateGMC_Config()

    # read the config
    getGMC_CFG()
    wprint(fncname + "Config copy strip: len: {}:\n".format(len(cfgstrip)),      BytesAsASCIIFF(cfgstrip))
    wprint(fncname + "Config read back:  len: {}:\n".format(len(gglobs.GMCcfg)), BytesAsASCIIFF(gglobs.GMCcfg))

    setDebugIndent(0)


def updateGMC_Config():
    # 13. Reload/Update/Refresh Configuration
    # must come after writing config to enable new config
    # Command: <CFGUPDATE>>
    # Return: 0xAA
    # Firmware supported: GMC-280, GMC-300 Re.2.20 or later
    # in GMC-500Re 1.08 this command returns:  b'0071\r\n\xaa'
    # see http://www.gqelectronicsllc.com/forum/topic.asp?TOPIC_ID=4948 #40

    fncname = "updateGMC_Config: "
    dprint(fncname)
    setDebugIndent(1)

    time.sleep(1)
    rec = serialGMC_COMM(b'<CFGUPDATE>>', 1, orig(__file__))
    time.sleep(1)

    dprint(fncname + "rec: ", rec)


    setDebugIndent(0)


def saveGMC_ConfigToFile():
    """save the GMC device config to a file - use for testing"""

    fncname = "saveGMC_ConfigToFile: "
    cfg, error, errmessage = getGMC_CFG()
    path = gglobs.dataPath + "/config" + stime() + ".bin"
    writeBinaryFile(path, cfg)


def setGMC_ConfigSettings():
    """puts the config settings into cfg and writes it to the config memory"""

    setBusyCursor()
    fncname = "setGMC_ConfigSettings: "
    dprint(fncname)
    setDebugIndent(1)

    while True: # to allow jumping to exit

        gcfg = bytearray(gglobs.GMCcfg)
        wprint(fncname + "gcfg:\n" + BytesAsASCIIFF(gcfg))

    # low index - single byte values
        lowkeys = "Power", "Alarm", "Speaker", "SaveDataType"
        for key in lowkeys:
            # all keys are only 1 byte long
            cfgrec      = cfgKeyLow[key]
            ndxfrom     = cfgrec[1][0]
            try: keyval = int(cfgrec[0])
            except Exception as e:
                edprint(fncname + "low index - single byte values: Exception: ", e)
                keyval = 0
            writeBytesToCFG(gcfg, ndxfrom, [keyval])

            wprint(fncname + "#1 cfgKeyLow: {:15s}, val: {:1d}, ndx: {}".format(key, keyval, cfgrec[1]))

    # low index - multi byte values (GMCendianness)
        if gglobs.GMCendianness == 'big':  fString = ">f"  # use big-endian ---   500er, 600er:
        else:                              fString = "<f"  # use little-endian -- other than 500er and 600er:
        lowkeys = "CalibCPM_0", "CalibuSv_0", "CalibCPM_1", "CalibuSv_1", "CalibCPM_2", "CalibuSv_2"
        for key in lowkeys:
            # keys are either 2 bytes or 4 bytes width
            cfgrec      = cfgKeyLow[key]
            ndxfrom     = cfgrec[1][0]
            ndxto       = cfgrec[1][1]
            width       = ndxto - ndxfrom
            if width == 2:
                try:
                    keyval = struct.pack(">H",    int(cfgrec[0])) #int(cfgKeyLow[key][0])
                except Exception as e:
                    edprint(fncname + "low index - multi byte values: Exception: ", e)
                    keyval = [0, 0]
                writeBytesToCFG(gcfg, ndxfrom, keyval)

            elif width == 4:
                try:
                    keyval = struct.pack(fString,    float(cfgrec[0])) #int(cfgKeyLow[key][0])
                except Exception as e:
                    edprint(fncname + "low index - multi byte values: Exception: ", e)
                    keyval = [0, 0, 0, 0]
                writeBytesToCFG(gcfg, ndxfrom, keyval)

            wprint("#2 cfgKeyLow: {:15s}, val: {}, width: {:2d}, ndx: {}".format(key, keyval, width, cfgKeyLow[key][1]))


        if gglobs.GMCWifiEnabled:
            wprint("now writing highkey stuff" * 5)
        # high index
            #print("gglobs.GMCcfgWifiCol: ", gglobs.GMCcfgWifiCol)
            padding = b"\x00" * 64
            colndx  = gglobs.GMCcfgWifiCol
            for key in cfgKeyHigh:
                cfgrec      = cfgKeyHigh[key]
                ndxfrom     = cfgrec[colndx][0]
                ndxto       = cfgrec[colndx][1]
                width       = ndxto - ndxfrom           # bytes reserved for this var

                if key == "Period":
                    try:    keyval = int(cfgrec[1])
                    except Exception as e:
                        edprint(fncname + "high index - Period: Exception: ", e)
                        keyval = 3
                    writeBytesToCFG(gcfg, ndxfrom, [keyval])

                elif key == "WiFi":
                    try:    keyval = int(cfgrec[1])
                    except Exception as e:
                        edprint(fncname + "high index - WiFi: Exception: ", e)
                        keyval = 1
                    writeBytesToCFG(gcfg, ndxfrom, [keyval])

                elif key == "FastEstTime":
                    try:    keyval = int(cfgrec[1])
                    except Exception as e:
                        edprint(fncname + "high index - FastEstTime: Exception: ", e)
                        keyval = 1
                    if not keyval in (3,5,10,15,20,30,60): keyval = 60
                    writeBytesToCFG(gcfg, ndxfrom, [keyval])

                else:
                    try:
                        keyval      = bytearray(cfgrec[1], "utf-8")
                        keyval      = (keyval + padding)[0:width]
                    except Exception as e:
                        edprint(fncname + "high index - multi bytes: Exception: ", e)
                        keyval = ("ERROR" + padding)[0:width]
                    writeBytesToCFG(gcfg, ndxfrom, keyval)

                wprint(fncname + "cfgKeyHigh: {:15s}, width: {:2d}".format(key, width), cfgrec[1], keyval)

            wprint(fncname + "gcfg:\n" + BytesAsASCIIFF(gcfg))
            gglobs.GMC_FastEstTime = cfgKeyHigh["FastEstTime"][1]


        fprint("Config is set, writing to device")
    # write the new config data
        writeGMC_Config(bytes(gcfg))

        fprint("Reading back from device")
    # read the config
        getGMC_CFG()
        break

    getGMC_HistSaveMode()
    gglobs.exgg.setGMCPowerIcon()
    printGMC_DevInfo(extended = False)

    setDebugIndent(0)
    setNormalCursor()


def writeBytesToCFG(cfg, address, bytesrec):
    """write the bytes in byterec to the Python var cfg beginning at address"""

    for i in range(0, len(bytesrec)):
        cfg[address + i] = bytesrec[i]


def editGMC_Configuration():
    """Edit the configuration from the GMC config memory"""

    """ checking radiobuttons
    radio1 = QRadioButton("button 1")
    radio2 = QRadioButton("button 2")
    radio3 = QRadioButton("button 3")

    for i in range(1,4):
        buttonname = "radio" + str(i)           # das geht???????
        if buttonname.isChecked():
            print buttonname + "is Checked"
    """

    rmself = gglobs.exgg    # access to ggeiger "remote self"

    if not gglobs.GMCConnection:
        showStatusMessage("No GMC Device Connected")
        return

# get gglobs.config
    cfg, error, errmessage = getGMC_CFG()
    #~print("error, errmessage: ", error, errmessage, ", cfg:\n", cfg)
    if error < 0:
        efprint("Error:" + errmessage)
        return

    fncname = "editGMC_Configuration: "

    #~dprint("*"*100)
    #~dprint("*"*100)
    #~dprint("*"*100)
    dprint(fncname)

    setDebugIndent(1)

    # https://www.tutorialspoint.com/pyqt/pyqt_qlineedit_widget.htm
    # https://snorfalorpagus.net/blog/2014/08/09/validating-user-input-in-pyqt4-using-qvalidator/

    setDefault = False  # i.e. False: show what is read from device

    while True:
        fbox=QFormLayout()
        fbox.setFieldGrowthPolicy (QFormLayout.AllNonFixedFieldsGrow)

        fbox.addRow(QLabel("<span style='font-weight:900;'>All GMC Counter</span>"))

    # Power
        r01=QRadioButton("On")
        r02=QRadioButton("Off")
        r01.setChecked(False)
        r02.setChecked(False)
        powergroup = QButtonGroup()
        powergroup.addButton(r01)
        powergroup.addButton(r02)
        hbox0=QHBoxLayout()
        hbox0.addWidget(r01)
        hbox0.addWidget(r02)
        hbox0.addStretch()
        fbox.addRow(QLabel("Power"), hbox0)
        if isGMC_PowerOn() == 'ON': r01.setChecked(True)
        else:                       r02.setChecked(True)

    # Alarm
        r11=QRadioButton("On")
        r12=QRadioButton("Off")
        r11.setChecked(False)
        r12.setChecked(False)
        alarmgroup = QButtonGroup()
        alarmgroup.addButton(r11)
        alarmgroup.addButton(r12)
        hbox1=QHBoxLayout()
        hbox1.addWidget(r11)
        hbox1.addWidget(r12)
        hbox1.addStretch()
        fbox.addRow(QLabel("Alarm"), hbox1)
        if isGMC_AlarmOn() == 'ON': r11.setChecked(True)
        else:                       r12.setChecked(True)

    # Speaker
        r21=QRadioButton("On")
        r22=QRadioButton("Off")
        r21.setChecked(False)
        r22.setChecked(False)
        speakergroup = QButtonGroup()
        speakergroup.addButton(r21)
        speakergroup.addButton(r22)
        hbox2=QHBoxLayout()
        hbox2.addWidget(r21)
        hbox2.addWidget(r22)
        hbox2.addStretch()
        fbox.addRow(QLabel("Speaker"), hbox2)
        if isGMC_SpeakerOn() == 'ON':   r21.setChecked(True)
        else:                           r22.setChecked(True)

    # history Savedatatype
        hbox3=QHBoxLayout()
        cb1=QComboBox()
        cb1.addItems(savedatatypes)
        cb1.setCurrentIndex(gglobs.GMCsavedataindex)
        hbox3.addWidget(cb1)
        fbox.addRow(QLabel("History Saving Mode"), hbox3)

    # calibration
        cpmtip   = "Enter an integer number 1 ... 1 Mio"
        usvtip   = "Enter a number 0.00001 ... 100 000"
        cpmlimit = (1, 1000000)
        usvlimit = (0.00001, 100000, 5 )

      # calibration 0
        rmself.cal1_cpm = QLineEdit()
        rmself.cal1_cpm.setFont(gglobs.fontstd)
        rmself.cal1_cpm.setValidator (QIntValidator(*cpmlimit))
        rmself.cal1_cpm.setToolTip(cpmtip)

        rmself.cal1_usv = QLineEdit()
        rmself.cal1_usv.setFont(gglobs.fontstd)
        rmself.cal1_usv.setValidator(QDoubleValidator(*usvlimit))
        rmself.cal1_usv.setToolTip(usvtip)

        rmself.cal1_fac = QLabel("")                      # CPM / (µSv/h)
        rmself.cal1_fac.setAlignment(Qt.AlignCenter)

        rmself.cal1_rfac = QLabel("")                     # reverse: µSv/h/CPM
        rmself.cal1_rfac.setAlignment(Qt.AlignCenter)

      # calibration 1
        rmself.cal2_cpm = QLineEdit()
        rmself.cal2_cpm.setValidator (QIntValidator(*cpmlimit))
        rmself.cal2_cpm.setFont(gglobs.fontstd)
        rmself.cal2_cpm.setToolTip(cpmtip)

        rmself.cal2_usv = QLineEdit()
        rmself.cal2_usv.setValidator(QDoubleValidator(*usvlimit))
        rmself.cal2_usv.setFont(gglobs.fontstd)
        rmself.cal2_usv.setToolTip(usvtip)

        rmself.cal2_fac = QLabel()
        rmself.cal2_fac.setAlignment(Qt.AlignCenter)

        rmself.cal2_rfac = QLabel()
        rmself.cal2_rfac.setAlignment(Qt.AlignCenter)

      # calibration 2
        rmself.cal3_cpm = QLineEdit()
        rmself.cal3_cpm.setValidator (QIntValidator(*cpmlimit))
        rmself.cal3_cpm.setFont(gglobs.fontstd)
        rmself.cal3_cpm.setToolTip(cpmtip)

        rmself.cal3_usv = QLineEdit()
        rmself.cal3_usv.setValidator(QDoubleValidator(*usvlimit))
        rmself.cal3_usv.setFont(gglobs.fontstd)
        rmself.cal3_usv.setToolTip(usvtip)

        rmself.cal3_fac = QLabel()
        rmself.cal3_fac.setAlignment(Qt.AlignCenter)

        rmself.cal3_rfac = QLabel()
        rmself.cal3_rfac.setAlignment(Qt.AlignCenter)

      # Grid
        calOptions=QGridLayout()
        calOptions.setContentsMargins(0,0,0,0)

        row = 0
        calOptions.addWidget(QLabel("Point"),          row, 0)
        calOptions.addWidget(QLabel("CPM"),            row, 1)
        calOptions.addWidget(QLabel("µSv/h"),          row, 2)
        calOptions.addWidget(QLabel("CPM/(µSv/h)"),    row, 3)
        calOptions.addWidget(QLabel("µSv/h/CPM"),      row, 4)

        row = 1
        calOptions.addWidget(QLabel("#1"),             row, 0)
        calOptions.addWidget(rmself.cal1_cpm,          row, 1)
        calOptions.addWidget(rmself.cal1_usv,          row, 2)
        calOptions.addWidget(rmself.cal1_fac,          row, 3)
        calOptions.addWidget(rmself.cal1_rfac,         row, 4)

        row = 2
        calOptions.addWidget(QLabel("#2"),             row, 0)
        calOptions.addWidget(rmself.cal2_cpm,          row, 1)
        calOptions.addWidget(rmself.cal2_usv,          row, 2)
        calOptions.addWidget(rmself.cal2_fac,          row, 3)
        calOptions.addWidget(rmself.cal2_rfac,         row, 4)

        row = 3
        calOptions.addWidget(QLabel("#3"),             row, 0)
        calOptions.addWidget(rmself.cal3_cpm,          row, 1)
        calOptions.addWidget(rmself.cal3_usv,          row, 2)
        calOptions.addWidget(rmself.cal3_fac,          row, 3)
        calOptions.addWidget(rmself.cal3_rfac,         row, 4)

        for i in range(0, 3):
            calcpm = cfgKeyLow["CalibCPM_{}".format(i)][0]
            calusv = cfgKeyLow["CalibuSv_{}".format(i)][0]
            calfac = calcpm / calusv
            rcalfac = 1 / calfac

            if   i == 0:
                rmself.cal1_cpm. setText("{:1.0f}".format(calcpm))
                rmself.cal1_usv. setText("{:1.3f}".format(calusv))
                rmself.cal1_fac. setText("{:9.3f}".format(calfac))
                rmself.cal1_rfac.setText("{:9.5f}".format(rcalfac))
            elif i == 1:
                rmself.cal2_cpm. setText("{:1.0f}".format(calcpm))
                rmself.cal2_usv. setText("{:1.3f}".format(calusv))
                rmself.cal2_fac. setText("{:9.3f}".format(calfac))
                rmself.cal2_rfac.setText("{:9.5f}".format(rcalfac))
            elif i == 2:
                rmself.cal3_cpm. setText("{:1.0f}".format(calcpm))
                rmself.cal3_usv. setText("{:1.3f}".format(calusv))
                rmself.cal3_fac. setText("{:9.3f}".format(calfac))
                rmself.cal3_rfac.setText("{:9.5f}".format(rcalfac))

        fbox.addRow("\n\nCalibration Points", calOptions)

        rmself.cal1_cpm.textChanged.connect(lambda: checkCalibValidity("cal0cpm", rmself.cal1_cpm, rmself.cal1_usv, rmself.cal1_fac, rmself.cal1_rfac ))
        rmself.cal1_usv.textChanged.connect(lambda: checkCalibValidity("cal0usv", rmself.cal1_cpm, rmself.cal1_usv, rmself.cal1_fac, rmself.cal1_rfac ))
        rmself.cal2_cpm.textChanged.connect(lambda: checkCalibValidity("cal1cpm", rmself.cal2_cpm, rmself.cal2_usv, rmself.cal2_fac, rmself.cal2_rfac ))
        rmself.cal2_usv.textChanged.connect(lambda: checkCalibValidity("cal1usv", rmself.cal2_cpm, rmself.cal2_usv, rmself.cal2_fac, rmself.cal2_rfac ))
        rmself.cal3_cpm.textChanged.connect(lambda: checkCalibValidity("cal2cpm", rmself.cal3_cpm, rmself.cal3_usv, rmself.cal3_fac, rmself.cal3_rfac ))
        rmself.cal3_usv.textChanged.connect(lambda: checkCalibValidity("cal2usv", rmself.cal3_cpm, rmself.cal3_usv, rmself.cal3_fac, rmself.cal3_rfac ))

###############################################################################
    # WiFi settings

        if not gglobs.GMCWifiEnabled:
            wifimsg = QLabel("<span style='font-weight:400;'>This counter is not WiFi enabled</span>")
            wififlag = False
        else:
            wifimsg = QLabel("")
            wififlag = True

        dashline = QLabel("<span style='font-weight:500;'>{}</span>".format("-" * 70))
        dashline.setAlignment(Qt.AlignCenter)
        fbox.addRow(dashline)
        fbox.addRow(QLabel("<span style='font-weight:900;'>WiFi Enabled GMC Counter</span>"), wifimsg)

    # WiFi On Off settings
        r31=QRadioButton("On")
        r32=QRadioButton("Off")
        r31.setChecked(False)
        r32.setChecked(False)
        r31.setEnabled(wififlag)
        r32.setEnabled(wififlag)
        wifigroup = QButtonGroup()
        wifigroup.addButton(r31)
        wifigroup.addButton(r32)
        hbox3=QHBoxLayout()
        hbox3.addWidget(r31)
        hbox3.addWidget(r32)
        hbox3.addStretch()
        fbox.addRow(QLabel("WiFi"), hbox3)
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

        fbox.addRow("WiFi SSID",            l1e)
        fbox.addRow("WiFi Password",        l2e)
        fbox.addRow("Server Website",       l3e)
        fbox.addRow("Server URL",           l4e)
        fbox.addRow("Server CounterID",     l5e)
        fbox.addRow("Server UserID",        l6e)
        fbox.addRow("Server Period (min)",  l7e)

        # fill the text fields
        if setDefault : ndx = 0 # i.e. show what is defined in the GeigerLog config
        else:           ndx = 1 # otherwise from device
        l1e.setText(cfgKeyHigh["SSID"]      [ndx])
        l2e.setText(cfgKeyHigh["Password"]  [ndx])
        l3e.setText(cfgKeyHigh["Website"]   [ndx])
        l4e.setText(cfgKeyHigh["URL"]       [ndx])
        l5e.setText(cfgKeyHigh["CounterID"] [ndx])
        l6e.setText(cfgKeyHigh["UserID"]    [ndx])
        l7e.setText(cfgKeyHigh["Period"]    [ndx])

        l1e.setEnabled(wififlag)
        l2e.setEnabled(wififlag)
        l3e.setEnabled(wififlag)
        l4e.setEnabled(wififlag)
        l5e.setEnabled(wififlag)
        l6e.setEnabled(wififlag)
        l7e.setEnabled(wififlag)

    # Fast Estimate
        hbox4=QHBoxLayout()
        cb4=QComboBox()
        cb4.addItems(["60", "30", "20", "15", "10", "5", "3"])
        cb4.setCurrentIndex(0)
        cb4.setEnabled(wififlag)
        hbox4.addWidget(cb4)
        fbox.addRow(QLabel("Fast Estimate Time <span style='color:red;'>CAUTION: see GeigerLog manual</span>"), hbox4)

    # dialog
        dialog = QDialog()
        dialog.setWindowIcon(gglobs.iconGeigerLog)
        dialog.setFont(gglobs.fontstd)
        dialog.setWindowTitle("Set GMC Configuration")
        dialog.setWindowModality(Qt.WindowModal)

        # buttonbox: https://srinikom.github.io/pyside-docs/PySide/QtGui/QDialogButtonBox.html
        bbox = QDialogButtonBox()
        bbox.setStandardButtons(QDialogButtonBox.Ok|QDialogButtonBox.Cancel|QDialogButtonBox.Reset|QDialogButtonBox.Help)
        bbox.rejected.connect           (lambda: dialog.done(0))    # cancel, ESC key
        bbox.accepted.connect           (lambda: dialog.done(1))    # ok
        bbox.helpRequested.connect      (lambda: dialog.done(2))    # Help: Apply ...
        bbox.clicked .connect           (lambda: dialog.done(3))    # reset

        gglobs.bboxbtn = bbox.button(QDialogButtonBox.Ok)   # ok button
        gglobs.bboxbtn.setEnabled(True)

        bboxhbtn = bbox.button(QDialogButtonBox.Help)       # Help button
        bboxhbtn.setText("Apply GeigerLog Configuration")
        bboxhbtn.setEnabled(wififlag)

        layoutV   = QVBoxLayout(dialog)
        layoutV.addLayout(fbox)
        layoutV.addWidget(bbox)

        popupdlg = dialog.exec_()
        #~print("-------------Ex:", popupdlg)

        if   popupdlg == 0:     return              # reject
        elif popupdlg == 1:     break               # accept
        elif popupdlg == 2:     setDefault = True   # help, Apply ... i.e. show what is defined in the GeigerLog config
        elif popupdlg == 3:     setDefault = False  # reset           i.e. show what is read from device
        else:                   return              # should never be called


    wprint("Power:       r01 is Checked: ", r01.isChecked(), ", Power:       r02 is Checked: ", r02.isChecked())
    wprint("Alarm:       r11 is Checked: ", r11.isChecked(), ", Alarm:       r12 is Checked: ", r12.isChecked())
    wprint("Speaker:     r21 is Checked: ", r21.isChecked(), ", Speaker:     r22 is Checked: ", r22.isChecked())
    wprint("HistSavMode: cb1.currentIndex():", cb1.currentIndex())

    wprint("cal1_cpm: ", rmself.cal1_cpm.text ())
    wprint("cal1_usv: ", rmself.cal1_usv.text ())
    wprint("cal2_cpm: ", rmself.cal2_cpm.text ())
    wprint("cal2_usv: ", rmself.cal2_usv.text ())
    wprint("cal3_cpm: ", rmself.cal3_cpm.text ())
    wprint("cal3_usv: ", rmself.cal3_usv.text ())

    ndx = 0
    cfgKeyLow["Power"]          [ndx] = 0   if r01.isChecked() else 255
    cfgKeyLow["Alarm"]          [ndx] = 1   if r11.isChecked() else 0
    cfgKeyLow["Speaker"]        [ndx] = 1   if r21.isChecked() else 0
    cfgKeyLow["SaveDataType"]   [ndx] = cb1.currentIndex()

    cfgKeyLow["CalibCPM_0"]     [ndx] = rmself.cal1_cpm.text()
    cfgKeyLow["CalibuSv_0"]     [ndx] = rmself.cal1_usv.text()
    cfgKeyLow["CalibCPM_1"]     [ndx] = rmself.cal2_cpm.text()
    cfgKeyLow["CalibuSv_1"]     [ndx] = rmself.cal2_usv.text()
    cfgKeyLow["CalibCPM_2"]     [ndx] = rmself.cal3_cpm.text()
    cfgKeyLow["CalibuSv_2"]     [ndx] = rmself.cal3_usv.text()

    for key in cfgKeyLow:
        wprint("cfgKeyLow:  {:20s}".format(key), cfgKeyLow[key][ndx])
    wprint()


    if gglobs.GMCWifiEnabled:
        wprint("WiFi:        r31 is Checked: ", r31.isChecked(), ", WiFi:        r32 is Checked: ", r32.isChecked())
        wprint("Fast Est Time: cb4.currentIndex():", cb4.currentIndex())
        wprint("Fast Est Time: cb4.currentText():", cb4.currentText())

        ndx = 1
        cfgKeyHigh["SSID"]      [ndx] = l1e.text()
        cfgKeyHigh["Password"]  [ndx] = l2e.text()
        cfgKeyHigh["Website"]   [ndx] = l3e.text()
        cfgKeyHigh["URL"]       [ndx] = l4e.text()
        cfgKeyHigh["CounterID"] [ndx] = l5e.text()
        cfgKeyHigh["UserID"]    [ndx] = l6e.text()
        cfgKeyHigh["Period"]    [ndx] = l7e.text()
        cfgKeyHigh["WiFi"]      [ndx] = r31.isChecked()
        cfgKeyHigh["FastEstTime"][ndx] = int(cb4.currentText())

        for key in cfgKeyHigh:
            wprint("cfgKeyHigh: {:20s}".format(key), cfgKeyHigh[key][ndx])

    wprint()

    fprint(header("Set GMC Configuration"))
    setGMC_ConfigSettings()

    setDebugIndent(0)


def checkCalibValidity(field, var1, var2, var3, var4):
    """verify proper calibration data"""

    # GMC popup editing:
    # var1 = rmself.calN_cpm
    # var2 = rmself.calN_usv
    # var3 = rmself.calN_fac
    # var4 = rmself.calN_rfac

    #~QValidator.Invalid                    0   The string is clearly invalid.
    #~QValidator.Intermediate               1   The string is a plausible intermediate value.
    #~QValidator.Acceptable                 2   The string is acceptable as a final result; i.e. it is valid.
    #~QDoubleValidator.StandardNotation     0   The string is written as a standard number (i.e. 0.015).
    #~QDoubleValidator.ScientificNotation   1   The string is written in scientific form. It may have an exponent part(i.e. 1.5E-2).

    rmself = gglobs.exgg

    if "," in var1.text(): var1.setText(var1.text().replace(",", ""))   # no comma
    if "," in var2.text(): var2.setText(var2.text().replace(",", "."))  # replace comma with period

    fncname = "checkCalibValidity: "
    wprint("\n" + fncname + "--- field, var1, var2, var3, var4: ", field, var1.text(), var2.text(), var3.text(), var4.text())

    sender = rmself.sender()
    wprint("sender.text():",   sender.text())

    validator = sender.validator()

    state = validator.validate(sender.text(), 0)
    wprint("state:    ", state)
    wprint("state[0]: ", state[0])

    if state[0] == QValidator.Acceptable:
        bgcolor = 'white'
        validMatrix[field] = True

    elif state[0] == QValidator.Intermediate:
        bgcolor = '#fff79a' # yellow
        validMatrix[field] = False

    else:
        playWav("error")
        bgcolor = '#f6989d' # red
        validMatrix[field] = False
        playWav("err")

    sender.setStyleSheet('QLineEdit { background-color: %s }' % bgcolor)

    if False in validMatrix.values():   gglobs.bboxbtn.setEnabled(False)
    else:                               gglobs.bboxbtn.setEnabled(True)

    try:    ivar1 = int(abs(float(var1.text().replace(",", "."))))
    except: ivar1 = float('nan')

    try:    fvar2 = abs(float(var2.text().replace(",", ".")))
    except: fvar2 = float('nan')

    var3.setText("{:8.5g}".format(float('nan') if fvar2 == 0 else ivar1 / fvar2))   # calib fac  (New)
    var4.setText("{:8.5g}".format(float('nan') if ivar1 == 0 else fvar2 / ivar1))   # calib rfac (Old)



def getGMC_SERIAL():
    # Get serial number
    # send <GETSERIAL>> and read 7 bytes
    # each nibble of 4 bit is a single hex digit of a 14 character serial number
    # e.g.: F488007E051234
    #
    # return: the serial number as a 14 character ASCII string
    #         error code
    #         error message

    fncname = "getGMC_SERIAL: "
    dprint(fncname)
    setDebugIndent(1)

    rec, error, errmessage  = serialGMC_COMM(b'<GETSERIAL>>', 7, orig(__file__))
    dprint(fncname + "raw: rec: ", rec)

    if error == 0 or error == 1:  # Ok or Warning
        hexlookup = "0123456789ABCDEF"
        sn =""
        for i in range(0,7):
            n1   = ((rec[i] & 0xF0) >>4)
            n2   = ((rec[i] & 0x0F))
            sn  += hexlookup[n1] + hexlookup[n2]
        rec = sn
    dprint(fncname + "decoded:  ", rec)

    setDebugIndent(0)

    return (rec, error, errmessage)


def setGMC_DATETIME():
    # from GQ-RFC1201.txt:
    # NOT CORRECT !!!!
    # 22. Set year date and time
    # command: <SETDATETIME[YYMMDDHHMMSS]>>
    # Return: 0xAA
    # Firmware supported: GMC-280, GMC-300 Re.3.00 or later

    # from: GQ-GMC-ICD.odt
    # CORRECT! 6 bytes, no square brackets
    # <SETDATETIME[YY][MM][DD][hh][mm][ss]>>

    dprint("setGMC_DATETIME:")
    setDebugIndent(1)

    tl      = list(time.localtime())  # tl: [2018, 4, 19, 13, 2, 50, 3, 109, 1]
                                      # for: 2018-04-19 13:02:50
    tl0     = tl.copy()

    tl[0]  -= 2000
    tlstr   = b''
    for i in range(0,6):  tlstr += bytes([tl[i]])
    dprint("setGMC_DATETIME: now:", tl0[:6], ", coded:", tlstr)

    rec, error, errmessage = serialGMC_COMM(b'<SETDATETIME'+ tlstr + b'>>', 1, orig(__file__))

    setDebugIndent(0)

    return (rec, error, errmessage)


def getGMC_DATETIME():
    # Get date and time
    # send <GETDATETIME>> and read 7 bytes: YY MM DD HH MM SS 0xAA
    #
    # return: date and time in the format:
    #           YYYY-MM-DD HH:MM:SS
    # e.g.:     2017-12-31 14:03:19

    fncname = "getGMC_DATETIME: "
    wprint(fncname)
    setDebugIndent(1)

    extra = getGMC_ExtraByte()   # just to make sure the pipeline is clean

    # yields: rec: b'\x12\x04\x13\x0c9;\xaa' , len:7
    # for:           2018-04-19 12:57:59
    rec, error, errmessage = serialGMC_COMM(b'<GETDATETIME>>', 7, orig(__file__))

    if rec == None:
        dprint(fncname + "ERROR: no DateTime received - ", errmessage)
    else:
        wprint(fncname + "raw: len: " + str(len(rec)) + ", rec: ", rec )
        #fprint(fncname + "raw: len: " + str(len(rec)) + ", rec: ", rec )

        if error == 0 or error == 1:  # Ok or only Warning
            try:
                rec  = datetime.datetime(rec[0] + 2000, rec[1], rec[2], rec[3], rec[4], rec[5])
            except:
                if rec ==  [0, 1, 1, 0, 0, 80, 170]:    # the values found after first start!
                    rec         = "2000-01-01 00:00:01" # overwrite rec with fake date
                    error       = -1
                    errmessage  = "ERROR getting Date & Time - Set at device first!"
                else:
                    # conversion to date failed
                    rec         = "2099-09-09 09:09:09" # overwrite rec with fake date
                    error       = -1
                    errmessage  = "ERROR getting Date & Time"
        else:   # a real error
            dprint(fncname + "ERROR getting DATETIME: ", errmessage, debug=True)

        wprint(fncname, rec)

    setDebugIndent(0)

    return (rec, error, errmessage)


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

    fncname = "getGMC_TEMP: "
    dprint(fncname)
    setDebugIndent(1)

    rec, error, errmessage  = serialGMC_COMM(b'<GETTEMP>>', 4, orig(__file__))

    # TESTING example for '-28.8 °C'
    #rec = b'\x1c\x08\x01\xaa'

    srec = ""
    for i in range(4): srec += "{}, ".format(rec[i])

    dprint(fncname + "Temp raw: rec= {} (=dec: {}), err={}, errmessage='{}'".format(rec, srec[:-2], error, errmessage))

    if error == 0 or error == 1:  # Ok or Warning
        if "GMC-3" in gglobs.GMCDeviceDetected :   # all 300 series
            temp = rec[0] + rec[1]/10.0     # unclear: is  decimal part rec[1] single digit or a 2 digit?
                                            # 3 digit not possible as byte value is from 0 ... 255
                                            # expecting rec[1] always from 0 ... 9
            if rec[2] != 0 : temp *= -1
            if rec[1]  > 9 : temp  = "ERROR: Temp={} - illegal value found for decimal part of temperature={}".format(temp, rec[1])
            rec = temp

        elif   "GMC-5" in gglobs.GMCDeviceDetected \
            or "GMC-6" in gglobs.GMCDeviceDetected:  # GMC-500/600
            temp = rec[0] + rec[1]/10.0     # unclear: is  decimal part rec[1] single digit or a 2 digit?
                                            # 3 digit not possible as byte value is from 0 ... 255
                                            # expecting rec[1] always from 0 ... 9
            #if rec[2] <= 0 : temp *= -1     # guessing: value=1 looks like positive Temperature. Negative is??? Maybe not right at all
            if rec[2] != 0 : temp *= -1     # using the old definition again
            if rec[1]  > 9 : temp  = "ERROR: Temp={} - illegal value found for decimal part of temperature={}".format(temp, rec[1])
            rec = temp

        else: # perhaps even 200 series?
            rec = "UNDEFINED"

    dprint(fncname + "Temp      rec= {}, err={}, errmessage='{}'".format(rec, error, errmessage))

    setDebugIndent(0)

    return (rec, error, errmessage)


def getGMC_GYRO():
    # Get gyroscope data
    # Firmware supported: GMC-320 Re.3.01 or later (NOTE: Not for GMC-300!)
    # Send <GETGYRO>> and read 7 bytes
    # Return: Seven bytes gyroscope data in hexdecimal: BYTE1,BYTE2,BYTE3,BYTE4,BYTE5,BYTE6,BYTE7
    # Here: BYTE1,BYTE2 are the X position data in 16 bits value. The first byte is MSB byte data and second byte is LSB byte data.
    #       BYTE3,BYTE4 are the Y position data in 16 bits value. The first byte is MSB byte data and second byte is LSB byte data.
    #       BYTE5,BYTE6 are the Z position data in 16 bits value. The first byte is MSB byte data and second byte is LSB byte data.
    #       BYTE7 always 0xAA

    dprint("getGMC_GYRO:")
    setDebugIndent(1)

    rec, error, errmessage  = serialGMC_COMM(b'<GETGYRO>>', 7, orig(__file__))
    dprint("getGMC_GYRO: raw: rec={}, err={}, errmessage='{}'".format(rec, error, errmessage))

    if error == 0 or error == 1:  # Ok or Warning
        x = rec[0] * 256 + rec[1]
        y = rec[2] * 256 + rec[3]
        z = rec[4] * 256 + rec[5]
        rec = "X=0x{:04x}, Y=0x{:04x}, Z=0x{:04x}   ({},{},{})".format(x,y,z,x,y,z)

    dprint("getGMC_GYRO: rec='{}', err={}, errmessage='{}'".format(rec, error, errmessage))

    setDebugIndent(0)

    return rec, error, errmessage


def setGMC_POWEROFF():
    # 12. Power OFF
    # Command: <POWEROFF>>
    # Return: none
    # Firmware supported: GMC-280, GMC-300 Re.2.11 or later

    setDebugIndent(1)
    rec  = serialGMC_COMM(b'<POWEROFF>>', 0, orig(__file__))
    dprint("setGMC_POWEROFF:", rec)
    setDebugIndent(0)

    return rec


def setGMC_POWERON():
    # 26. Power ON
    # Command: <POWERON>>
    # Return: none
    # Firmware supported: GMC-280, GMC-300, GMC-320 Re.3.10 or later

    setDebugIndent(1)
    rec  = serialGMC_COMM(b'<POWERON>>', 0, orig(__file__))
    dprint("setGMC_POWERON:", rec)
    setDebugIndent(0)

    return rec


def setGMC_REBOOT():
    # 21. Reboot unit
    # command: <REBOOT>>
    # Return: None
    # Firmware supported: GMC-280, GMC-300 Re.3.00 or later

    setDebugIndent(1)
    rec  = serialGMC_COMM(b'<REBOOT>>', 0, orig(__file__))
    dprint("setGMC_REBOOT:", rec)
    setDebugIndent(0)

    return rec


def setGMC_FACTORYRESET():
    # 20. Reset unit to factory default
    # command: <FACTORYRESET>>
    # Return: 0xAA
    # Firmware supported: GMC-280, GMC-300 Re.3.00 or later

    setDebugIndent(1)
    rec  = serialGMC_COMM(b'<FACTORYRESET>>', 1, orig(__file__))
    dprint("setGMC_FACTORYRESET:", rec)
    setDebugIndent(0)

    return rec


#
# Derived commands and functions
#


def getGMC_DeltaTime():
    """reads the DateTime from the device, converts into a number, and returns
    the delta time in sec with 1 sec precision"""

    rec, error, errmessage = getGMC_DATETIME()

    if error < 0:
        #fprint("getGMC_DeltaTime: rec:{}, errmessage:'{}'".format( rec, errmessage))
        return gglobs.NAN
    else:
        time_computer = longstime()
        time_device   = str(rec)
        time_delta    = round((mpld.datestr2num(time_computer) - mpld.datestr2num(time_device)) * 86400, 3)
       #fprint("getGMC_DeltaTime: device:{}, computer:{}, Delta C./.D:{:0.3f}".format(time_device, time_computer, time_delta))
        return time_delta


def getGMC_TimeMessage(msg):
    """determines difference between times of computer and device and gives message"""

    deltatime = getGMC_DeltaTime() # is nan on error
    if   abs(deltatime) <= 1:    dtxt = "Device time is same as computer time within 1 sec"                     # uncertainty 1 sec
    elif np.isnan(deltatime):    dtxt = "Device time cannot be read"                                            # clock defect?
    elif deltatime >= +1:        dtxt = "Device is slower than computer by {:0.1f} sec".format(deltatime)       # delta positiv
    elif deltatime <= -1:        dtxt = "Device is faster than computer by {:0.1f} sec".format(abs(deltatime))  # delta negativ

    if abs(deltatime) > 5:
        efprint("Device time:",                 dtxt,                  debug=True)
        qefprint("Date & Time from device:",    getGMC_DATETIME()[0],  debug=True)
        qefprint("Date & Time from computer:",  longstime(),           debug=True)

    elif np.isnan(deltatime):
        efprint("Device time:", dtxt, debug=True)

    else:
        fprint("Device time:", dtxt, debug=True)


def isGMC_PowerOn():
    """Checks Power status in the configuration"""

    #PowerOnOff byte:
    #at config offset  : 0
    #300 series        : 0 for ON and 255 for OFF
    #http://www.gqelectronicsllc.com/forum/topic.asp?TOPIC_ID=4948  Reply #14
    #confirmed in Reply #17
    #500/600 series    : PowerOnOff byte: 0 for ON, and 1 for OFF

    try:        c = ord(cfgKeyLow["Power"][0])
    except:
        try:    c = cfgKeyLow["Power"][0]
        except Exception as e:
            dprint( "isGMC_PowerOn: Exception: {}".format(e))
            return "UNKNOWN"

    try:
        if "GMC-3" in gglobs.GMCDeviceDetected: # all 300series
            #print("GMC-3 in gglobs.GMCDeviceDetected")
            if   c == 0:            p = "ON"
            elif c == 255:          p = "OFF"
            else:                   p = c

        elif "GMC-5" in gglobs.GMCDeviceDetected or \
             "GMC-6" in gglobs.GMCDeviceDetected :  # 500, 500+, 600, 600+
            # as stated by EmfDev from GQ, but strange because different from
            # handling the Speaker and Alarm settings
            if   c == 0:            p = "ON"
            elif c  > 0:            p = "OFF"
            else:                   p = c

        else:
            p = "UNKNOWN"
    except:
        p = "UNKNOWN"

    return p


def isGMC_AlarmOn():
    """Checks Alarm On status in the configuration.
    Alarm is at offset:1"""

    try:    c = ord(cfgKeyLow["Alarm"][0])
    except: return "UNKNOWN"

    if   c == 0:            p = "OFF"
    elif c == 1:            p = "ON"
    else:                   p = c

    return p


def isGMC_SpeakerOn():
    """Checks Speaker On status in the configuration.
    Speaker is at offset:2"""

    try:    c = ord(cfgKeyLow["Speaker"][0])
    except: return "UNKNOWN"

    if   c == 0:            p = "OFF"
    elif c == 1:            p = "ON"
    else:                   p = c

    return p


def isGMC_WifiOn():
    """Checks WiFi status in the configuration"""

    #~if not gglobs.GMCWifiEnabled: return "OFF"
    if not gglobs.GMCWifiEnabled: return 255

    fncname = "isGMC_WifiOn: "

    try:   c = gglobs.GMCcfg[cfgKeyHigh["WiFi"][gglobs.GMCcfgWifiCol][0]]
    except Exception as e:
        dprint(fncname + "Exception: {}".format(e))
        return 255
    #~print(fncname + "c=", c)

    if   c == 0:            p = "OFF"
    elif c == 1:            p = "ON"
    else:                   p = c

    return p


def getFastEstTime():

    return gglobs.GMC_FastEstTime


def getGMC_BatteryType():
    """Checks Battery Type in the configuration"""

    # cfg Offset Battery = 56
    # Battery Type: 1 is non rechargeable. 0 is chargeable.

    try:    c = ord(cfgKeyLow["Battery"][0])
    except: return "UNKNOWN"

    if   c == 0:            p = "ReChargeable"
    elif c == 1:            p = "Non-ReChargeable"
    else:                   p = c

    return p


def getGMC_BAUDRATE():
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

    dprint("getGMC_BAUDRATE:")
    setDebugIndent(1)

    if  "GMC-3" in gglobs.GMCDeviceDetected: # all 300series
        brdict  = {64:1200, 160:2400, 208:4800, 232:9600, 240:14400, 244:19200, 248:28800, 250:38400, 252:57600, 254:115200}

    elif "GMC-5" in gglobs.GMCDeviceDetected or \
         "GMC-6" in gglobs.GMCDeviceDetected :  # 500, 500+, 600, 600+
        brdict  = {0:115200, 1:1200, 2:2400, 3:4800, 4:9600, 5:14400, 6:19200, 7:28800, 8:38400, 9:57600}

    else:
        brdict  = {}

    #print("getGMC_BAUDRATE: cfg Baudrate:")
    #for key, value in sorted(brdict.items()):
    #    print ("      {:08b} {:3d} {:6d}".format(key, key, value))

    try:
        key = ord(cfgKeyLow["Baudrate"][0])
        rec = brdict[key]
    except:
        key = -999
        rec = "ERROR: Baudrate cannot be determined"

    dprint("getGMC_BAUDRATE: " + str(rec) + " with cfgKeyLow[\"Baudrate\"][0]={}".format(key))

    setDebugIndent(0)

    return rec


def quickGMC_PortTest(usbport):
    """Tests GMC usbport with the 2 baudrates 57600 and 115200 using the GMC
    command <GETVER>>.
    Returns:    -1 on comm error,
                 0 (zero) if no test is successful
                 first successful baudrate otherwise
    """

    dprint("quickGMC_PortTest: testing 57600 and 115200 baudrate on port: '{}'".format(usbport))
    setDebugIndent(1)

    baudrate_found = 0
    if os.access(usbport, os.F_OK):  # test if file with name like '/dev/geiger' exists
        for baudrate in (115200, 57600):
            dprint("quickGMC_PortTest: Trying baudrate:", baudrate, debug=True)
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
                    dprint("quickGMC_PortTest: Success with baudrate {} on port {}".format(baudrate, usbport), debug=True)
                    baudrate_found = baudrate
                    break

            except Exception as e:
                errmessage1 = "quickGMC_PortTest: ERROR: Serial communication error on testing baudrate {} on port {}".format(baudrate, usbport)
                exceptPrint(e, sys.exc_info(), errmessage1)
                baudrate_found = -1
                break

    else:
        errmessage1 = "quickGMC_PortTest: ERROR: Serial Port '{}' does not exist".format(usbport)
        edprint(errmessage1)
        baudrate_found = -1

    setDebugIndent(0)

    return baudrate_found


def autoGMC_BAUDRATE(usbport):
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

    dprint("autoGMC_BAUDRATE: Autodiscovery of baudrate on port: '{}'".format(usbport))
    setDebugIndent(1)

    baudrates = gglobs.GMCbaudrates
    baudrates.sort(reverse=True) # to start with highest baudrate
    for baudrate in baudrates:
        dprint("autoGMC_BAUDRATE: Trying baudrate:", baudrate, debug=True)
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
                dprint("autoGMC_BAUDRATE: Success with {}".format(baudrate), debug=True)
                break

        except Exception as e:
            errmessage1 = "autoGMC_BAUDRATE: ERROR: autoGMC_BAUDRATE: Serial communication error on finding baudrate"
            exceptPrint(e, sys.exc_info(), errmessage1)
            baudrate = None
            break

        baudrate = 0

    dprint("autoGMC_BAUDRATE: Found baudrate: {}".format(baudrate))
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

    fncname = "initGMC: "
    gglobs.GMCDeviceName = "GMC Device"

    gglobs.GMCLast60CPS  = np.full(60, 0)   # storing last 60 sec of CPS values, filled with all 0
    gglobs.GMCEstFET     = np.full(60, 0)   # storing last 60 sec of CPS values, filled with all 0

    msg         = "port='{}' baudrate={} timeoutR={} timeoutW={}".format(gglobs.GMCusbport, gglobs.GMCbaudrate, gglobs.GMCtimeout, gglobs.GMCtimeout_write)
    gglobs.GMCser  = None
    error       = 0
    errmessage  = ""
    errmessage1 = ""

    dprint(fncname + "Settings: " + msg)
    setDebugIndent(1)

    if not os.access(gglobs.GMCusbport, os.F_OK):  # file with name like '/dev/geiger' does NOT exist
        rmsg = fncname + "Initialization failed, Serial Port '{}' does not exist".format(gglobs.GMCusbport)
        edprint(rmsg)

    else:                                       # file with name like '/dev/geiger' DOES exist
        while True:
            # Make the serial connection
            errmessage1 = "Connection failed using " + msg
            try:
                # gglobs.GMCser is like:
                # Serial<id=0x7f2014d371d0, open=True>(port='/dev/ttyUSB0',
                # baudrate=115200, bytesize=8, parity='N', stopbits=1,
                # timeout=20, xonxoff=False, rtscts=False, dsrdtr=False)
                gglobs.GMCser = serial.Serial(gglobs.GMCusbport, gglobs.GMCbaudrate, timeout=gglobs.GMCtimeout, write_timeout=gglobs.GMCtimeout_write)

            except serial.SerialException as e:
                exceptPrint(e, sys.exc_info(), fncname + "SerialException: " + errmessage1)
                terminateGMC()
                break

            except Exception as e:
                exceptPrint(e, sys.exc_info(), fncname + "Exception: " + errmessage1)
                terminateGMC()
                break

            # Connection is made. Now test for successful communication with a
            # GMC Geiger counter, because the device port can be opened without
            # error even when no communication can be done, e.g. due to wrong
            # baudrate or wrong device
            dprint(fncname + "Port opened ok, now testing communication")

            # any bytes in pipeline? clear them first
            getGMC_ExtraByte()

            try:
                ver, error, errmessage = getGMC_VER()
            except Exception as e:
                errmessage1  = "ERROR: Port opened ok, but Communication failed. Is baudrate correct?"
                exceptPrint(e, sys.exc_info(), fncname + errmessage1)
                terminateGMC()
                break

            if error < 0:
                errmessage1  = "ERROR: Communication problem: " + errmessage
                edprint(fncname + errmessage1, debug=True)
                terminateGMC()
                break

            else:
                # Got something back for ver like: 'GMC-300Re 4.22'
                if ver.startswith("GMC"):
                    gglobs.GMCDeviceDetected = ver
                    gglobs.Devices["GMC"][0] = gglobs.GMCDeviceDetected

                else:
                    err  = "<br>INFO: No GMC device detected. While a connected device was found, it <br>"
                    err += "identified itself with this unknown signature: '{}'.".format(ver)
                    errmessage1 += err
                    edprint(fncname + err, debug=True)
                    terminateGMC()

            break

        if gglobs.GMCser == None:
            rmsg = "{}".format(errmessage1.replace('[Errno 2]', '<br>'))
            gglobs.GMCConnection = False

        else:
            dprint(fncname + "Communication ok with device: '{}'".format(ver))
            rmsg = ""
            gglobs.GMCConnection = True

            # identify device
            getGMC_DeviceProperties()

            # get the cfg
            cfg, error, errmessage = getGMC_CFG() # goes to gglobs.GMCcfg within f'on
            if error < 0:
                rmsg = "ERROR trying to read GMC Device Configuration: " + errmessage
                gglobs.GMCConnection = False
            else:
                pass

    setDebugIndent(0)

    return rmsg


def terminateGMC():
    """what is needed here???"""

    if gglobs.GMCser != None:
        try:    gglobs.GMCser.close()
        except: dprint("terminateGMC: Failed trying to close serial port", debug=True)
        gglobs.GMCser  = None

    gglobs.GMCConnection = False


def serialGMC_COMM(sendtxt, returnlength, caller = ("", "", -1)):
    # write to and read from serial port, exit on serial port error
    # when not enough bytes returned, try send+read again up to 3 times.
    # exit if it still fails

    fncname = "serialGMC_COMM: "

    wprint(fncname + "sendtxt: '{}', returnlength: {}, caller: '{}'".format(sendtxt, returnlength, caller))
    setDebugIndent(1)
    #print(fncname + "gglobs.GMCser: ", gglobs.GMCser)

    rec         = None
    error       = 0
    errmessage  = ""

    while True:

    # is GMC device still connected?
        if not os.access(gglobs.GMCusbport , os.R_OK):
            # /dev/ttyUSB* can NOT be read
            terminateGMC()
            rec         = None
            error       = -1
            errmessage  = "ERROR: Is GMC device connected? USB Port '{}' not found".format(gglobs.GMCusbport)
            dprint(fncname + errmessage, debug=True)
            fprint(errmessage, error=True)
            break
        else:
            # /dev/ttyUSB* can be read
            if gglobs.GMCser == None:
                # serial connection does NOT exist
                try:
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
            srcinfo = fncname + "ERROR: WRITE failed with SerialException when writing: '{}'".format(sendtxt)
            exceptPrint(e, sys.exc_info(), srcinfo)
            wtime = -99

        except serial.SerialTimeoutException as e:
            srcinfo = fncname + "ERROR: WRITE failed with SerialTimeoutException when writing: '{}'".format(sendtxt)
            exceptPrint(e, sys.exc_info(), srcinfo)
            wtime = -99

        except Exception as e:
            srcinfo = fncname + "ERROR: WRITE failed with Exception when writing: '{}'".format(sendtxt)
            exceptPrint(e, sys.exc_info(), srcinfo)
            wtime = -99

        if wtime == -99:
            #print(fncname + "wtime:", wtime)
            terminateGMC()
            rec         = None
            error       = -1
            errmessage  = fncname + "ERROR: WRITE failed. See log for details"
            break


    # read from port
        breakRead = False
        rtime  = time.time()
        rtimex = rtime
        try:
            #raise Exception
            #raise serial.SerialException
            rec    = gglobs.GMCser.read(returnlength)
        except serial.SerialException as e:
            srcinfo = fncname + "ERROR: READ failed with serial exception"
            exceptPrint(e, sys.exc_info(), srcinfo)
            edprint(fncname + "ERROR: caller is: {} in line no: {}".format(caller[0], caller[1]), debug=True)
            breakRead = True

        except Exception as e:
            srcinfo = fncname + "ERROR: READ failed with exception"
            exceptPrint(e, sys.exc_info(), srcinfo)
            edprint(fncname + "ERROR: caller is: {} in line no: {}".format(caller[0], caller[1]), debug=True)
            breakRead = True

        if breakRead:
            terminateGMC()
            rec         = None
            error       = -1
            errmessage  = fncname + "ERROR: READ failed. See log for details"
            break

        rtime  = (time.time() - rtime) * 1000
        wprint(fncname + "got {} bytes, first (up to 15) bytes: {}".format(len(rec), rec[:15]))
        if len(rec) < returnlength:
            for i in range(len(rec[:15])):
                try:
                    wprint("byte: ", rec[i])
                except Exception as e:
                    dprint(fncname + "Exception: ", e)

        extra  = getGMC_ExtraByte()
        rec   += extra
        rtimex = (time.time() - rtimex) * 1000 - rtime

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
        wprint(fncname + "Timing (ms): write:{:6.2f}, read:{:6.1f}, read per byte:{}, extraread:{:6.1f}  ".format(wtime, rtime, rbyte, rtimex), marker, werbose=localdebug)

    # Retry loop
        if len(rec) < returnlength:
            if rtime > (gglobs.GMCtimeout * 1000):
                msg  = "{} TIMEOUT ERROR Serial Port; command {} exceeded {:3.1f}s".format(stime(), sendtxt, gglobs.GMCtimeout)
                efprint(html_escape(msg)) # escaping needed as GMC commands like b'<GETCPS>>' have <> brackets
                dprint(fncname + msg, "- rtime:{:5.1f}ms".format(rtime), debug=True)

            efprint("Got {} data bytes, expected {}. Retrying.".format(len(rec), returnlength))
            Qt_update()

            edprint(fncname + "ERROR: Received length: {} is less than requested: {}".format(len(rec), returnlength), debug=True)
            edprint(fncname + "rec: (len={}): {}".format(len(rec), BytesAsHex(rec)))

            error       = 1
            errmessage  = fncname + "ERROR: Command:{} - Record too short: Received bytes:{} < requested:{}".format(sendtxt, len(rec), returnlength)

            # RETRYING
            count    = 0
            countmax = 3
            while True:
                count += 1
                errmsg = fncname + "RETRY: to get full return record, trial #{}".format(count)
                dprint(errmsg, debug=True)

                time.sleep(0.5) # extra sleep after not reading enough data

                extra = getGMC_ExtraByte()   # just to make sure the pipeline is clean

                gglobs.GMCser.write(sendtxt)
                time.sleep(0.3) # after sending

                rtime  = time.time()
                rec = gglobs.GMCser.read(returnlength)
                rtime = (time.time() - rtime) * 1000
                dprint("Timing (ms): Retry read:{:6.1f}".format(rtime))

                if len(rec) == returnlength:
                    dprint(fncname + "RETRY: returnlength is {} bytes. OK now. Continuing normal cycle".format(len(rec)), ", rec:\n", BytesAsHex(rec), debug=True)
                    errmessage += "; ok after {} retry".format(count)
                    extra = getGMC_ExtraByte()   # just to make sure the pipeline is clean
                    fprint("Retry successful.")
                    gglobs.exgg.addError(errmessage)
                    break
                else:
                    #dprint(u"RETRY:" + fncname + "returnlength is {} bytes. Still NOT ok; trying again".format(len(rec)), debug=True)
                    pass

                if count >= countmax:
                    dprint(fncname + "RETRY: Retried {} times, always failure, giving up. Serial communication error.".format(count), debug=True)
                    error       = -1
                    errmessage  = "ERROR communicating via serial port. Giving up."
                    fprint(errmessage)
                    gglobs.exgg.addError(errmessage)
                    break

                fprint("ERROR communicating via serial port. Retrying again.")

        break

    setDebugIndent(0)

    return (rec, error, errmessage)


def setGMC_DateTime():
    """ set date and time on GMC device to computer date and time"""

    dprint("setGMC_DateTime:")
    setDebugIndent(1)

    fprint(header("Set Date&Time of GMC Device"))
    rec, error, errmessage = getGMC_DATETIME()

    if error < 0:
        efprint("Communication problem with device: ", errmessage)
        qefprint("Trying to force setting of Date&Time")

    else:
        getGMC_TimeMessage("setGMC_DateTime")
        fprint("Setting device time to computer time")

    setGMC_DATETIME()
    rec, error, errmessage = getGMC_DATETIME()
    fprint("New Date&Time from device:", str(rec))

    setDebugIndent(0)


def getGMC_HistSaveMode():
    """
    Bytenumber:32  Parameter: CFG_SaveDataType
    0 = OFF (no history saving)
    1 = CPS, save every second
    2 = CPM, save every minute
    3 = CPM, save hourly average
    4 = CPS, save every second if exceeding threshold
    5 = CPM, save every minute if exceeding threshold
    """

    fncname = "getGMC_HistSaveMode: "

    sdttxt = savedatatypes
    #print sdttxt, len(sdttxt)

    try:        sdt = ord(cfgKeyLow["SaveDataType"][0])
    except:
        try:    sdt = int(cfgKeyLow["SaveDataType"][0])
        except Exception as e:
            edprint(fncname + "Exception: ", e)
            sdt = 9999
    #print "sdt:", sdt

    try:
        if sdt <= len(sdttxt):  txt = sdttxt[sdt]
        else:                   txt = "UNKNOWN"
        gglobs.GMCsavedatatype  = txt
        gglobs.GMCsavedataindex = sdt
    except Exception as e:
        edprint(fncname + "Exception: ", e)
        txt= fncname + "Error: undefined type: {}".format(sdt)

    return sdt, txt  # <index>, <mode as text>


def setGMC_HistSaveMode():
    """sets the History Saving Mode"""

    dprint("setGMC_HistSaveMode:")
    setDebugIndent(1)

    while True:
        # get current config
        cfg, error, errmessage = getGMC_CFG()
        gglobs.GMCcfg = cfg
        if error < 0:
            fprint("Error:" + errmessage)
            break

        SDT, SDTtxt = getGMC_HistSaveMode()
        gglobs.GMCsavedatatype = SDTtxt

        # setup dialog and get new config setting
        selection   = savedatatypes
        text, ok    = QInputDialog().getItem(None, 'Set History Saving Mode', "Select new history saving mode and press ok:   ", selection, SDT, False )
        vprint("Set History Saving Mode:", "text=", text, ",  ok=", ok)
        if not ok: break      # user has selected Cancel

        fprint(header("Set History Saving Mode"))

        newSDT = selection.index(text)
        #print "newSDT:", newSDT

        # write the new config data
        setBusyCursor()
        writeGMC_ConfigSingle(cfgKeyLow["SaveDataType"][1][0], newSDT)
        setNormalCursor()

        fprint("Device History Saving Mode:", "{}".format(getGMC_HistSaveMode()[1]))

        break

    setDebugIndent(0)


def switchGMC_DeviceSpeaker(newstate = "ON"):
    """Switch Device Speaker to ON or OFF"""

    setBusyCursor()
    fprint(header("Switch Device Speaker {}".format(newstate)))

    if newstate == "ON": st = 1
    else:                st = 0

    # write the new config data (will get a fresh config)
    writeGMC_ConfigSingle(cfgKeyLow["Speaker"][1][0], st)

    if gglobs.GMCcfg[cfgKeyLow["Speaker"][1][0]] == 1: ipo = "ON"
    else:                                              ipo = "OFF"

    fprint("Device Speaker State is: ",  ipo)

    setNormalCursor()


def switchGMC_DeviceAlarm(newstate = "ON"):
    """Switch Device Alarm to ON or OFF"""

    setBusyCursor()
    fprint(header("Switch Device Alarm {}".format(newstate)))

    if newstate == "ON":    st = 1
    else:                   st = 0

    # write the new config data
    writeGMC_ConfigSingle(cfgKeyLow["Alarm"][1][0], st)
    time.sleep(1.0)

    fprint("Device Alarm State is: ",  isGMC_AlarmOn())

    setNormalCursor()


def printGMC_DevConfig():
    """prints the 256 or 512 bytes of device configuration memory"""

    setBusyCursor()

    fncname = "printGMC_DevConfig: "

    fprint(header("GMC Device Configuration"))

    cfg, error, errmessage = getGMC_CFG()
    lencfg = len(cfg)
    #~print("cfg: len: {}\n{}".format(lencfg, BytesAsHex(cfg)))
    #~print("cfg: len: {}\n{}".format(lencfg, BytesAsDec(cfg)))

    cfgcopy = copy.copy(cfg) # need copy, will remove right-side FF
    fText  = ""

    if cfg == None:
        fText += errmessage

    elif error < 0 and lencfg not in (256, 512):
        fText += errmessage

    else:
    # if len(cfg) == 256 or len(cfg) == 512 even with error
        fText     += "The configuration is:\nFormat: index(dec):index(hex)  | value(hex)=value(dec)=char(ASCII)|... \n"
        cfgstrp    = cfgcopy.rstrip(b'\xFF')       # remove the right side FF values
        lencfgstrp = len(cfgstrp)
        if lencfgstrp == 0:  return "ERROR: Configuration is empty. Try a factory reset!"

        for i in range(0, lencfgstrp, 8):
            pcfg = "{:3d}:{:03X}  | ".format(i, i)
            for j in range(0, 8):
                k = i+j
                if k < lencfgstrp:
                    pcfg += "{:02x}={:3d}={:1s}| ".format(cfgstrp[k], cfgstrp[k], IntToChar(cfgstrp[k]))
            fText += pcfg + "\n"

        if lencfgstrp < lencfg:
            fText += "Remaining {} values up to address {} are all 'ff=255'\n".format(lencfg - lencfgstrp, lencfg - 1)

        fText += "\nThe configuration as ASCII (0xFF as 'F', other non-ASCII characters as '.'):\n" + BytesAsASCIIFF(cfgcopy)

    fprint(fText)
    dprint(fncname + "\n" + fText)

    setNormalCursor()


def printGMC_DevInfo(extended = False):
    """prints basic or extended info on the GMC device"""
    # the config is read in initGMC

    txt = "GMC Device Info"
    if extended:  txt += " Extended"
    fprint(header(txt))

    if not gglobs.GMCConnection:
        efprint("No connected device")
        return

    setBusyCursor()

    fprint("Configured Connection:", "port:'{}' baud:{} timeoutR:{}s timeoutW:{}s".\
            format(gglobs.GMCusbport, gglobs.GMCbaudrate, gglobs.GMCtimeout, gglobs.GMCtimeout_write))

    fncname = "printGMC_DevInfo: "
    dprint(fncname)
    setDebugIndent(1)

    # device name
    fprint("Connected device:", "'{}'".format(gglobs.GMCDeviceDetected), debug=True)

    # GMCvariables
    fprint("Configured Variables:", gglobs.GMCvariables, debug=True)

    # calibration 1st tube
    no1 = "#1" if not gglobs.GMCSingleTubeDevice else ""
    fprint("Geiger tube{} calib. factor:".format(no1), "{:5.1f} CPM/(µSv/h) (= {:0.4f} µSv/h/CPM)".format(gglobs.calibration1st, 1 / gglobs.calibration1st), debug=True)

    # calibration 2nd tube
    if not gglobs.GMCSingleTubeDevice:
        fprint("Geiger tube#2 calib. factor:", "{:5.1f} CPM/(µSv/h) (= {:0.4f} µSv/h/CPM)".format(gglobs.calibration2nd, 1 / gglobs.calibration2nd), debug=True)

    # serial number
    sn,  error, errmessage = getGMC_SERIAL()
    # no printing of SN

    getGMC_TimeMessage("called from: " + fncname)

    # power state
    fprint("Device Power State:", isGMC_PowerOn(), debug=True)

    # WiFi enabled counter
    if gglobs.GMCWifiEnabled:
        fet = getFastEstTime()
        if fet == 60 or fet == "60":
            fprint("Fast Estimate Time:", fet, " sec. Okay")
        else:
            efprint("Fast Estimate Time:", fet, " seconds")
            qefprint("CAUTION: anything different from 60 results in false data!")
            qefprint("Correct in 'Set GMC Configuration'. See GeigerLog manual.")

    if extended == True:
        # baudrate as read from device
        fprint("Baudrate read from device:", getGMC_BAUDRATE(), debug=True)

        # No of bytes in CP* records
        fprint("No. of bytes in CP* records:", gglobs.GMCnbytes, debug=True)

        # voltage
        rec, error, errmessage = getGMC_VOLT()
        if error < 0:   fprint("Device Battery Voltage:", "{}"      .format(errmessage), debug=True)
        else:           fprint("Device Battery Voltage:", "{} Volt" .format(rec)       , debug=True)

        # Battery Type
        fprint("Device Battery Type Setting:", getGMC_BatteryType(), debug=True)

        # temperature taken out. Apparently not valid at all in 500 series
        # not working in the 300series
        # temperature
        #rec, error, errmessage = getGMC_TEMP()
        #if error < 0:
        #    fprint("Device Temperature:", "'{}'" .format(errmessage), debug=True)
        #else:
        #    fprint("Device Temperature:", "{} °C".format(rec)       , debug=True)
        #    fprint("", "(ONLY for GMC-320 ?)")

        # gyro
        rec, error, errmessage = getGMC_GYRO()
        if error < 0:
            fprint("Device Gyro Data:", "'{}'".format(errmessage))
        else:
            fprint("Device Gyro data:", rec)
            fprint("", "(only GMC-320 Re.3.01 and later)")

        # Alarm state
        fprint("Device Alarm State:", isGMC_AlarmOn(), debug=True)

        # Speaker state
        fprint("Device Speaker State:", isGMC_SpeakerOn(), debug=True)

        # MaxCPM
        value = cfgKeyLow["MaxCPM"][0]
        fprint("Max CPM (invalid if 65535!):", value, debug=True)

        # Calibration settings
        fprint("Device Calibration Points:", "       CPM  =   µSv/h   CPM / (µSv/h)      µSv/h/CPM", debug=True)
        for i in range(0, 3):
            calcpm = cfgKeyLow["CalibCPM_{}".format(i)][0]
            calusv = cfgKeyLow["CalibuSv_{}".format(i)][0]
            try:    calfac      = calcpm / calusv
            except: calfac      = gglobs.NAN
            try:    invcalfac   = calusv / calcpm
            except: invcalfac   = gglobs.NAN
            fprint("   Calibration Point", "#{:}: {:6d}  = {:7.3f}       {:6.2f}          {:0.5f}".format(i + 1, calcpm, calusv, calfac, invcalfac))

        # Save Data Type
        sdt, sdttxt = getGMC_HistSaveMode()
        fprint("Device Hist. Saving Mode:", sdttxt, debug=True)

        # Device History Saving Mode - Threshold
        ThM = ord(cfgKeyLow["ThresholdMode"][0])
        if  ThM in (0, 1, 2):
            ThresholdMode = ("CPM", "µSv/h", "mR/h")
            fprint("Device Hist. Threshold Mode:",   ThresholdMode[ThM])
            fprint("Device Hist. Threshold CPM:",    cfgKeyLow["ThresholdCPM"][0] )
            fprint("Device Hist. Threshold µSv/h:",  "{:0.3f}".format(cfgKeyLow["ThresholduSv"][0]))
        else:
            fprint("Device Hist. Threshold Mode:",   "Not available on this device")

        # WiFi enabled counter
        if gglobs.GMCWifiEnabled:
            sfmt   = "{:30s}{}\n"
            skeys  = ("SSID", "Password", "Website", "URL", "UserID", "CounterID", "Period")

            # Web related High bytes in Config - as read out from device
            ghc    = "Device WiFi Settings\n"
            for key in skeys: ghc += sfmt.format("   " + key, cfgKeyHigh[key][1])
            ghc += sfmt.format("   WiFi:",           isGMC_WifiOn())
            fprint(ghc[:-1], debug=True)

            # Web related High bytes in GL Config
            ghc    = "GeigerLog's WiFi Configuration:\n"
            for key in skeys: ghc += sfmt.format("   " + key, cfgKeyHigh[key][0])
            # no WiFi setting
            fprint(ghc[:-1], debug=True)

        # Firmware settings
        ghc = "GeigerLog's Firmware Configuration:\n"
        fmt = "   {:27s}{}\n"
        if gglobs.GMCDeviceDetected != "auto":
            ghc += fmt.format("Memory (bytes):",                "{:,}".format(gglobs.GMCmemory))
            ghc += fmt.format("SPIRpage Size (bytes):",         "{:,}".format(gglobs.GMC_SPIRpage))
            ghc += fmt.format("SPIRbugfix (True | False):",     "{:}" .format(gglobs.GMC_SPIRbugfix))
            ghc += fmt.format("Config Size (bytes):",           "{:}" .format(gglobs.GMCconfigsize))
            ghc += fmt.format("Calibr.1st (CPM/(µSv/h)):",      "{:}" .format(gglobs.calibration1st))
            if not gglobs.GMCSingleTubeDevice:
                ghc += fmt.format("Calibr.2nd (CPM/(µSv/h)):",  "{:}" .format(gglobs.calibration2nd))
            ghc += fmt.format("Voltagebytes (1 | 5):",          "{:}" .format(gglobs.GMCvoltagebytes))
            ghc += fmt.format("Endianness (big | little):",     "{:}" .format(gglobs.GMCendianness))
        fprint(ghc[:-1], debug=True)

    fprint("")
    setDebugIndent(0)
    setNormalCursor()


def pushGMC_ToWeb():
    """Send countrate info to website"""

    """
    Info on GMCmap:
    from: http://www.gmcmap.com/AutomaticallySubmitData.asp

    Auto submit data URL format:
    http://www.GMCmap.com/log2.asp?AID=UserAccountID&GID=GeigerCounterID &CPM=nCPM&ACPM=nACPM&uSV=nuSV
    At lease one reading data has to be submitted.
        UserAccountID:   user account ID. This ID is assigned once a user registration is completed.
        GeigerCounterID: a global unique ID for each registered Geiger Counter.
        nCPM:  Count Per Minute reading from this Geiger Counter.
        nACPM: Average Count Per Minute reading from this Geiger Counter(optional).
        nuSv:  uSv/h reading from this Geiger Counter(optional).

    Followings are valid data submission examples:
        http://www.GMCmap.com/log2.asp?AID=0230111&GID=0034021&CPM=15&ACPM=13.2&uSV=0.075
        http://www.GMCmap.com/log2.asp?AID=0230111&GID=0034021&CPM=15&ACPM=0&uSV=0
        http://www.GMCmap.com/log2.asp?AID=0230111&GID=0034021&CPM=15&ACPM=0&uSV=0
        http://www.GMCmap.com/log2.asp?AID=0230111&GID=0034021&CPM=15
        http://www.GMCmap.com/log2.asp?AID=0230111&GID=0034021&CPM=15&ACPM=13.2

    The submission result will be returned immediately. Followings are the returned result examples:
        OK.
        Error! User is not found.ERR1.
        Error! Geiger Counter is not found.ERR2.
        Warning! The Geiger Counter location changed, please confirm the location.
     """

    if gglobs.logging == False:
        fprint("Must be logging to update radiation maps", error=True, errsound=True)
        return

    # Dialog
    msgbox = QMessageBox()
    msgbox.setWindowIcon(gglobs.iconGeigerLog)
    msgbox.setIcon(QMessageBox.Warning)
    msgbox.setFont(gglobs.fontstd)
    msgbox.setWindowTitle("Updating Radiation World Maps")
    msgbox.setStandardButtons(QMessageBox.Ok)
    msgbox.setDefaultButton(QMessageBox.Ok)
    msgbox.setEscapeButton(QMessageBox.Ok)

    # Exit if no DataSource or His DataSource; need Log DataSource
    if gglobs.activeDataSource == None or gglobs.activeDataSource == "His":
        datatext = "Must show a Log Plot to update Radiation Maps"
        msgbox.setText(datatext)
        retval = msgbox.exec_()
        return

    cpmdata = gglobs.logSlice["CPM"]
    #print("cpmdata:", cpmdata)
    ymask   = np.isfinite(cpmdata)      # mask for nan values
    cpmdata = cpmdata[ymask]
    #print("cpmdata:", cpmdata)

    lendata = len(cpmdata)
    CPM     = np.mean(cpmdata)
    ACPM    = CPM

    # gglobs.calibration1st, 2nd, 3rd may be 'auto' if no device connected!
    if gglobs.calibration1st == "auto": uSV = 0
    else:                               uSV = CPM / gglobs.calibration1st
    #~print("gglobs.calibration1st:", gglobs.calibration1st, "CPM:", CPM, "ACPM:", ACPM, "uSV:", uSV)

    # Defintions valid for cfgKeyHigh[key][0] (0=zero)
    # holding the definitions of the geigerlog,cfg file!
    data         = {}
    data['AID']  = cfgKeyHigh["UserID"][0]
    data['GID']  = cfgKeyHigh["CounterID"][0]
    data['CPM']  = "{:3.1f}".format(CPM)
    data['ACPM'] = data['CPM']
    data['uSV']  = "{:3.2f}".format(uSV)
    gmcmapURL    = cfgKeyHigh["Website"][0] + "/" + cfgKeyHigh["URL"][0]  + '?' + urllib.parse.urlencode(data)

    strdata = ""
    mapform = "   {:11s}: {}\n"
    strdata += mapform.format("CPM",        data['CPM'])
    strdata += mapform.format("ACPM",       data['ACPM'])
    strdata += mapform.format("uSV",        data['uSV'])
    strdata += mapform.format("UserID",     data['AID'])
    strdata += mapform.format("CounterID",  data['GID'])
    strdata  = strdata[:-1] # remove last linefeed

    # Dialog Confirm Sending
    datatext  = "Calling server: " + cfgKeyHigh["Website"][0] + "/" + cfgKeyHigh["URL"][0]
    datatext += "\nwith these data based on {} datapoints:                                          \n\n".format(lendata)
    datatext += strdata + "\n\nPlease confirm with OK, or Cancel"
    msgbox.setText(datatext)
    msgbox.setStandardButtons(QMessageBox.Ok|QMessageBox.Cancel)
    msgbox.setDefaultButton(QMessageBox.Ok)
    msgbox.setEscapeButton(QMessageBox.Cancel)
    retval = msgbox.exec_()
    if retval != 1024:   return

    fprint(header("Updating Radiation World Maps"))

    dprint("Updating Radiation World Maps - " +  gmcmapURL)
    for a in ("AID", "GID", "CPM", "ACPM", "uSV"): # ordered print
        dprint("{:5s}: {}".format(a, data[a]))

    try:
        with urllib.request.urlopen(gmcmapURL) as response:
            answer = response.read()
        dprint("Server Response: ", answer)
    except Exception as e:
        answer  = b"Bad URL"
        srcinfo = "Bad URL: " + gmcmapURL
        exceptPrint(e, sys.exc_info(), srcinfo)

    # possible gmcmap server responses:
    # on proper credentials:                    b'\r\n<!--  sendmail.asp-->\r\n\r\nWarrning! Please update/confirm your location.<BR>OK.ERR0'
    # on wrong credentials:                     b'\r\n<!--  sendmail.asp-->\r\n\r\nError! User not found.ERR1.'
    # on proper userid but wrong counterid:     b'\r\n<!--  sendmail.asp-->\r\n\r\nError! Geiger Counter not found.ERR2.'
    # something wrong in the data part of URL:  b'\r\n<!--  sendmail.asp-->\r\n\r\nError! Data Error!(CPM)ERR4.'

    # ERR0 = 0k
    if   b"ERR0" in answer:
        fprint("Successfully updated Radiation World Maps with these data:")
        fprint(strdata)
        fprint("Website response:", answer.decode('UTF-8'))

    # ERR1 or ERR2 - wrong userid  or wrong counterid
    elif b"ERR1" in answer or b"ERR2" in answer :
        efprint("Failure updating Radiation World Maps.")
        qefprint("Website response: ", answer.decode('UTF-8'))

    # misformed URL - programming error?
    elif b"Bad URL" in answer:
        efprint("Failure updating Radiation World Maps.")
        qefprint(" ERROR: ", "Bad URL: " + gmcmapURL)

    # other errors
    else:
        efprint("Unexpected response updating Radiation World Maps.")
        qefprint("Website response: ", answer.decode('UTF-8'))


#device
def doREBOOT():
    """reboot the GMC device"""

    msg = QMessageBox()
    msg.setWindowIcon(gglobs.iconGeigerLog)
    msg.setIcon(QMessageBox.Warning)
    msg.setWindowTitle("Reboot GMC Device")
    msg.setText("Rebooting your GMC device.\nPlease confirm with OK, or Cancel")
    msg.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
    msg.setDefaultButton(QMessageBox.Cancel)
    msg.setEscapeButton(QMessageBox.Cancel)
    retval = msg.exec_()

    if retval != 1024:   return

    fprint(header("GMC Device Reboot"))
    rec, err, errmessage = setGMC_REBOOT()
    if err == 0 or err == 1:    fprint("REBOOT completed")
    else:                       fprint("ERROR in setGMC_REBOOT: " + errmessage)


def doFACTORYRESET(force):
    """Does a FACTORYRESET of the GMC device"""

    d = QInputDialog()
    d.setWindowIcon(gglobs.iconGeigerLog)
    warning ="""
CAUTION - You are about to reset the GMC device to factory condition!
All data and your changes of settings will be lost. \n
If you want to proceed, enter the word 'FACTORYRESET' (in all capital)
and press OK"""

    if force: text, ok = "FACTORYRESET", True
    else:     text, ok = d.getText(None, 'FACTORYRESET', warning)

    vprint("Factory Reset:", "text=", text, ",  ok=", ok)
    if ok:
        fprint(header("GMC Device FACTORYRESET"))
        if text == "FACTORYRESET":
            rec, err, errmessage = setGMC_FACTORYRESET()
            if err == 0 or err == 1: fprint("FACTORYRESET completed")
            else:                    fprint("ERROR in setGMC_FACTORYRESET: " + errmessage)
        else:
            fprint("Entry '{}' not matching 'FACTORYRESET' - Reset NOT done".format(text))



###############################################################################

def getGMC_DeviceProperties():
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


    dprint("getGMC_DeviceProperties: of connected device: '{}'".format(gglobs.GMCDeviceDetected))
    setDebugIndent(1)

    calibration2nd = gglobs.DefaultCalib2nd

    if "GMC-300Re 3." in gglobs.GMCDeviceDetected :
        #######################################################################
        # the "GMC-300" delivers the requested page after ANDing with 0fff
        # hence when you request 4k (=1000hex) you get zero
        # therefore use pagesize 2k only
        #######################################################################
        GMCmemory               = 2**16
        GMC_SPIRpage            = 2048
        GMC_SPIRbugfix          = False
        GMCconfigsize           = 256
        calibration             = 154  # CPM/(µSv/h)
        GMCvoltagebytes         = 1
        GMCendianness           = 'little'
        GMCvariables            = "CPM, CPS"
        GMCnbytes               = 2

    elif "GMC-300Re 4." in gglobs.GMCDeviceDetected:
        #######################################################################
        # when using a page of 4k, you need the datalength workaround in
        # gcommand, i.e. asking for 1 byte less
        # 'GMC-300Re 4.54' from AZ Jan 2021 has Serial No: F488C39506ABFA
        # when writing config data into the unused portion of the memory, the
        # counter seems to delete the changes after ~1 sec
        #######################################################################
        GMCmemory               = 2**16
        GMC_SPIRpage            = 4096
        GMC_SPIRbugfix          = True
        GMCconfigsize           = 256
        calibration             = 154  # CPM/(µSv/h)
        GMCvoltagebytes         = 1
        GMCendianness           = 'little'
        GMCvariables            = "CPM, CPS"
        GMCnbytes               = 2

    elif "GMC-320Re 3." in gglobs.GMCDeviceDetected:
        #######################################################################
        #
        #######################################################################
        GMCmemory               = 2**20
        GMC_SPIRpage            = 4096
        GMC_SPIRbugfix          = False
        GMCconfigsize           = 256
        calibration             = 154  # CPM/(µSv/h)
        GMCvoltagebytes         = 1
        GMCendianness           = 'little'
        GMCvariables            = "CPM, CPS"
        GMCnbytes               = 2

    elif "GMC-320Re 4." in gglobs.GMCDeviceDetected:
        #######################################################################
        # GMC-320Re 4.19 : kein Fast Estimate Time
        #######################################################################
        GMCmemory               = 2**20
        GMC_SPIRpage            = 4096
        GMC_SPIRbugfix          = True
        GMCconfigsize           = 256
        calibration             = 154  # CPM/(µSv/h)
        GMCvoltagebytes         = 1
        GMCendianness           = 'little'
        GMCvariables            = "CPM, CPS"
        GMCnbytes               = 2

    elif "GMC-320Re 5." in gglobs.GMCDeviceDetected:
        #######################################################################
        #
        #######################################################################
        GMCmemory               = 2**20
        GMC_SPIRpage            = 4096
        GMC_SPIRbugfix          = True
        GMCconfigsize           = 256
        calibration             = 154  # CPM/(µSv/h)
        GMCvoltagebytes         = 1
        GMCendianness           = 'little'
        GMCvariables            = "CPM, CPS"
        GMCnbytes               = 2

    elif "GMC-500Re 1." in gglobs.GMCDeviceDetected:
        #######################################################################
        # 500 - OHNE +
        # GMC-500Re 1.08 : kein Fast Estimate Time (von user the_mike
        #######################################################################
        GMCmemory               = 2**20
        #GMC_SPIRpage           = 4096  # ist bug jetzt behoben oder auf altem Stand???
        GMC_SPIRpage            = 2048   # Workaround erstmal auf 2048 bytes
        GMC_SPIRbugfix          = False
        GMCconfigsize           = 512
        calibration             = 154  # CPM/(µSv/h)
        GMCvoltagebytes         = 5
        GMCendianness           = 'big'
        GMCvariables            = "CPM, CPS"
        GMCnbytes               = 2

    elif "GMC-500+Re 1.18" in gglobs.GMCDeviceDetected:
        #######################################################################
        # Yields 4 bytes on all CPx calls!
        # Has a firmware bug: on first call to GETVER gets nothing returned.
        # WORK AROUND: must cycle connection ON->OFF->ON. then ok
        #######################################################################
        GMCmemory               = 2**20
        #GMC_SPIRpage           = 4096  # ist bug jetzt behoben oder auf altem Stand???
        GMC_SPIRpage            = 2048   # Workaround erstmal auf 2048 bytes
        GMC_SPIRbugfix          = False
        GMCconfigsize           = 512
        calibration             = 154   # CPM/(µSv/h)
        calibration2nd          = 2.08     # CPM/(µSv/h)
        GMCvoltagebytes         = 5
        GMCendianness           = 'big'
        GMCvariables            = "CPM1st, CPS1st, CPM2nd, CPS2nd"
        GMCnbytes               = 4

    elif "GMC-500+Re 1.21" in gglobs.GMCDeviceDetected:
        #######################################################################
        # Yields 4 bytes on all CPx calls!
        # Firmware bug from 'GMC-500+Re 1.18' is corrected
        #######################################################################
        GMCmemory               = 2**20
        GMC_SPIRpage            = 4096  # ist bug jetzt behoben oder auf altem Stand???
        # appears to be working with 4096 and no GMC_SPIRbugfix
    #    GMC_SPIRpage           = 2048   # Workaround erstmal auf 2048 bytes
        GMC_SPIRbugfix          = False
        GMCconfigsize           = 512
        calibration             = 154  # CPM/(µSv/h)
        calibration2nd          = 2.08     # CPM/(µSv/h)
        GMCvoltagebytes         = 5
        GMCendianness           = 'big'
        GMCvariables            = "CPM1st, CPS1st, CPM2nd, CPS2nd"
        GMCnbytes               = 4


    elif "GMC-500+Re 1.2" in gglobs.GMCDeviceDetected: # to cover 1.22ff
        #######################################################################
        # Yields 4 bytes on all CPx calls!
        # Firmware bug from 'GMC-500+Re 1.18' is corrected
        #######################################################################
        GMCmemory               = 2**20
        GMC_SPIRpage            = 4096  # ist bug jetzt behoben oder auf altem Stand???
        # appears to be working with 4096 and no GMC_SPIRbugfix
    #    GMC_SPIRpage           = 2048   # Workaround erstmal auf 2048 bytes
        GMC_SPIRbugfix          = False
        GMCconfigsize           = 512
        calibration             = 154  # CPM/(µSv/h)
        calibration2nd          = 2.08 # CPM/(µSv/h)
        GMCvoltagebytes         = 5
        GMCendianness           = 'big'
        GMCvariables            = "CPM1st, CPS1st, CPM2nd, CPS2nd"
        GMCnbytes               = 4


    elif "GMC-500+Re 1." in gglobs.GMCDeviceDetected: # if not caught in 1.18, 1.21, 1.22
        #######################################################################
        #
        #######################################################################
        GMCmemory               = 2**20
        #GMC_SPIRpage           = 4096  # ist bug jetzt behoben oder auf altem Stand???
        GMC_SPIRpage            = 2048   # Workaround erstmal auf 2048 bytes
        GMC_SPIRbugfix          = False
        GMCconfigsize           = 512
        calibration             = 154  # CPM/(µSv/h)
        calibration2nd          = 2.08 # CPM/(µSv/h)
        GMCvoltagebytes         = 5
        GMCendianness           = 'big'
        GMCvariables            = "CPM, CPS, CPM1st, CPM2nd"
        GMCnbytes               = 2


    elif "GMC-500+Re 2." in gglobs.GMCDeviceDetected: # to cover 2.00ff
        #######################################################################
        #
        #######################################################################
        # same as: GMC-500+Re 1.2.
        # Latest Firmware: 2.24
        # Calibration points read out from firmware:
        # Calibration Points:     CPM  =  µSv/h   CPM / (µSv/h)   µSv/h / CPM
        # Calibration Point 1:    100  =   0.65       153.8          0.0065
        # Calibration Point 2:  30000  = 195.00       153.8          0.0065
        # Calibration Point 3:     25  =   4.85         5.2          0.1940
        #######################################################################
        GMCmemory               = 2**20
        #~GMC_SPIRpage          = 4096     # appears to be working with 4k and no GMC_SPIRbugfix
        #~GMC_SPIRpage          = 4096 * 2 # appears to be working with 8k and no GMC_SPIRbugfix
        #~GMC_SPIRpage          = 4096 * 3 # appears to be working with 12k and no GMC_SPIRbugfix
        #~GMC_SPIRpage          = 4096 * 4 # appears to be working with 16k and no GMC_SPIRbugfix
        #~GMC_SPIRpage          = 4096 * 8 # timeout errors with 32k and no GMC_SPIRbugfix
        GMC_SPIRpage            = 4096     # chosen default for now
        GMC_SPIRbugfix          = False
        GMCconfigsize           = 512
        calibration             = 154  # CPM / (µSv/h)
        calibration2nd          = 2.08 # CPM / (µSv/h)
        GMCvoltagebytes         = 5
        GMCendianness           = 'big'
        GMCvariables            = "CPM1st, CPS1st, CPM2nd, CPS2nd"
        GMCnbytes               = 4


    elif "GMC-510+Re 1." in gglobs.GMCDeviceDetected:
        #######################################################################
        # reported by dishemesdr: https://sourceforge.net/p/geigerlog/discussion/general/thread/48ffc25514/
        # Connected device: GMC-510Re 1.04
        #######################################################################
        GMCmemory               = 2**20
        #~GMC_SPIRpage          = 4096   # ist bug jetzt behoben oder auf altem Stand???
        GMC_SPIRpage            = 2048   # Workaround erstmal auf 2048 bytes
        GMC_SPIRbugfix          = False
        GMCconfigsize           = 512
        calibration             = 154  # CPM / (µSv/h)
        calibration2nd          = 2.08 # CPM / (µSv/h)
        #~GMCvoltagebytes         = 5
        #   2020-09-19 12:57:43 TIMEOUT ERROR Serial Port; command b'<getvolt>>' exceeded 1.0s
        #   Got 1 data bytes, expected 5. Retrying.
        GMCvoltagebytes         = 1
        GMCendianness           = 'big'
        GMCvariables            = "CPM, CPS, CPM1st, CPS1st, CPM2nd, CPS2nd"
        GMCnbytes               = 4


    elif "GMC-600Re 1." in gglobs.GMCDeviceDetected:
        #######################################################################
        # calibration: using LND calib 348, not GQ setting 379; see note in ceigerlog.cfg
        #######################################################################
        GMCmemory               = 2**20
        #GMC_SPIRpage           = 4096  # ist bug jetzt behoben oder auf altem Stand???
        GMC_SPIRpage            = 2048   # Workaround erstmal auf 2048 bytes
        GMC_SPIRbugfix          = False
        GMCconfigsize           = 512
        calibration             = 348  # CPM/(µSv/h)
        GMCvoltagebytes         = 5
        GMCendianness           = 'big'
        GMCvariables            = "CPM, CPS"
        GMCnbytes               = 2


    elif "GMC-600+Re 1." in gglobs.GMCDeviceDetected:
        #######################################################################
        # calibration: using LND calib 348, not GQ setting 379; see note in ceigerlog.cfg
        #######################################################################
        GMCmemory               = 2**20
        #GMC_SPIRpage           = 4096  #  ist bug jetzt behoben oder auf altem Stand???
        GMC_SPIRpage            = 2048   # Workaround erstmal auf 2048 bytes
        GMC_SPIRbugfix          = False
        GMCconfigsize           = 512
        calibration             = 348     # CPM/(µSv/h)
        GMCvoltagebytes         = 5
        GMCendianness           = 'big'
        GMCvariables            = "CPM, CPS"
        GMCnbytes               = 2


    else: # If none of the above match, then this will be reached
        #######################################################################
        # to integrate as of now unknown new (or old) devices
        #######################################################################
        msg = "getGMC_DeviceProperties: New, unknown GMC device has been connected: {}".format(gglobs.GMCDeviceDetected)
        edprint(msg, debug=True)
        efprint(msg)
        qefprint("You may have to edit the configuration file geigerlog.cfg to adapt the settings to your counter")
        qefprint("Review the Extended Info for your GMC counter")
        GMCmemory               = 2**20
        GMC_SPIRpage            = 2048
        GMC_SPIRbugfix          = False
        GMCconfigsize           = 512
        calibration             = 154  # CPM/(µSv/h)
        GMCvoltagebytes         = 5
        GMCendianness           = 'big'
        GMCvariables            = "CPM, CPS"
        GMCnbytes               = 4

    # valid for all counter
    GMC_locationBug             = "GMC-500+Re 1.18, GMC-500+Re 1.21"
    GMC_FastEstTime             = 60
    gglobs.GMCSingleTubeDevice  = True

    # overwrite preset values if defined in the GeigerLog config file
    if gglobs.GMCmemory         == 'auto':         gglobs.GMCmemory        = GMCmemory
    if gglobs.GMC_SPIRpage      == 'auto':         gglobs.GMC_SPIRpage     = GMC_SPIRpage
    if gglobs.GMC_SPIRbugfix    == 'auto':         gglobs.GMC_SPIRbugfix   = GMC_SPIRbugfix
    if gglobs.GMCconfigsize     == 'auto':         gglobs.GMCconfigsize    = GMCconfigsize
    if gglobs.calibration1st    == 'auto':         gglobs.calibration1st   = calibration
    if gglobs.calibration2nd    == 'auto':         gglobs.calibration2nd   = calibration2nd
    if gglobs.GMCvoltagebytes   == 'auto':         gglobs.GMCvoltagebytes  = GMCvoltagebytes
    if gglobs.GMCendianness     == 'auto':         gglobs.GMCendianness    = GMCendianness
    if gglobs.GMCnbytes         == 'auto':         gglobs.GMCnbytes        = GMCnbytes
    if gglobs.GMCvariables      == 'auto':         gglobs.GMCvariables     = GMCvariables
    if gglobs.GMC_FastEstTime   == 'auto':         gglobs.GMC_FastEstTime  = GMC_FastEstTime
    if gglobs.GMClocationBug    == 'auto':         gglobs.GMClocationBug   = GMC_locationBug

    cfgKeyHigh["FastEstTime"][0] = str(gglobs.GMC_FastEstTime)

    if   "GMC-500+Re"      in gglobs.GMCDeviceDetected:     gglobs.GMCSingleTubeDevice = False  # 500+ with 2 tubes
    if   "GMC-500Re 1.08"  in gglobs.GMCDeviceDetected:     gglobs.GMCSingleTubeDevice = False  # 500 (without +) with 2 tubes owned by the_Mike

    # WiFi settings
    gglobs.GMCWifiEnabled = True
    if   "GMC-500+Re 2.24" in gglobs.GMCDeviceDetected:     gglobs.GMCcfgWifiCol = 4            # 500+ version 2.24
    elif "GMC-320Re 5."    in gglobs.GMCDeviceDetected:     gglobs.GMCcfgWifiCol = 2            # 320v5 device
    elif gglobs.GMCconfigsize == 512:                       gglobs.GMCcfgWifiCol = 3            # 500er, 600er
    else:
        gglobs.GMCcfgWifiCol  = -1        # WiFi is invalid
        gglobs.GMCWifiEnabled = False     # redundant?

    # verify locationBug
    try:    ts = gglobs.GMClocationBug.split(",") # to avoid crash due to wrong user entry
    except: ts = GMC_locationBug.split(",")
    for i in range(0, len(ts)): ts[i] = ts[i].strip()
    #print("ts:", ts)
    gglobs.GMClocationBug     = ts

    setLoggableVariables("GMC", gglobs.GMCvariables)

    setDebugIndent(0)

#### end getGMC_DeviceProperties ##############################################

