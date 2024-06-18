#! /usr/bin/env python3
# -*- coding: UTF-8 -*-

"""
rutils.py - DataServers's utilities

include in programs with:
    from rutils include *
"""

#####################################################################################################
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
#####################################################################################################


# NOTE: Using a Headless Raspi (no monitor, no keyboard, no mouse)
# Recommended: use 'no-vnc' connection to Raspi
# see: https://forums.raspberrypi.com/viewtopic.php?t=333132
# see post on dumping mutter: https://forums.raspberrypi.com/viewtopic.php?t=333132#p2040420
# Remote call Raspi from browser: http://raspberrypi.local/
# don't forget to configure Port under: Extended -> WebSocket to 5900 (is 80 by default)

# NOTE: sound output from Raspi:
# http://cool-web.de/raspberry/raspberry-pi-lautsprecher-sirene.htm

# NOTE: PWM on Raspi
# https://www.raspberry-pi-geek.de/ausgaben/rpg/2020/04/grundlagen-der-pulsweitenmodulation/

# NOTE: Using Raspi's 'i2cdetect' in terminal:
# scan I2c: i2cdetect -y 1
# list I2c: i2cdetect -l

# NOTE: it looks like the GDK101 does need a 5V supply! At 3.3V it appears to
# be working, but count rate comes out as way too high!


import sys, os, io, time                        # basic modules
import datetime    as dt                        # datetime
import traceback                                # more details on crashes
import platform                                 # finding OS
import socket                                   # finding IP Adress
import http.server                              # web server
import urllib.parse                             # parsing queries
import threading                                # higher-level threading interfaces
import random                                   # fudging some numbers
import math                                     # calculating SQRT (for normal distribution)
import numpy    as np

if not 'win32' in sys.platform:                 # Py3:'linux', Py2:'linux2'
    import curses                               # not available on Windows

from collections import deque                   # deque is used as fixed-size buffer

import rglobs as g                              # get the global variables
from rconfig import *                           # get the configuration script

# colors for terminal
# TDEFAULT                    = '\033[0m'       # default, i.e greyish
TDEFAULT                    = '\033[;1m'        # default, i.e greyish BOLD
TGREEN                      = '\033[92m'        # green
TYELLOW                     = '\033[93m'        # yellow

BOLDRED                     = '\033[91;1m'      # bold red
BOLDGREEN                   = '\033[92;1m'      # bold green
BOLDCYAN                    = '\033[96;1m'      # bold cyan
# if "WINDOWS" in platform.platform().upper():    # Windows does not support terminal colors
#     TDEFAULT                = ""
#     TGREEN                  = ""
#     TYELLOW                 = ""
#     BOLDRED                 = ""
#     BOLDGREEN               = ""
#     BOLDCYAN                = ""


# Activate all deque queus
# GMC
g.GMCstoreCounts            = deque([],  1)     # queue for max of  1 values of CPM from GMC Geiger counter

# I2C
g.I2CstoreLM75B             = deque([], 60)     # queue for max of 60 values of Temperature
g.I2CstoreBME280            = deque([], 60)     # queue for max of 60 values of Temp, Press, Humid
g.I2CstoreBH1750            = deque([], 60)     # queue for max of 60 values of Light
g.I2CstoreVEML6075          = deque([], 60)     # queue for max of 60 values of [UV-A, UV-B, other]
g.I2CstoreLTR390            = deque([], 60)     # queue for max of 60 values of [visible, UV]
g.I2CstoreGDK101            = deque([],  1)     # queue for max of  1 values of CPM from Solid State Geiger counter
g.I2CstoreSCD30             = deque([],  1)     # queue for max of  1 values of CO2 from NDIR
g.I2CstoreSCD41             = deque([],  1)     # queue for max of  1 values of CO2 from NDIR

# Pulse
g.PulseStore                = deque([], 60)     # empty queue for max of 60 values for last 60 sec of CPS


# set cycletime in sec
cycletime           = ccycletime if ccycletime > 1 else 1


## Display name for this setup
g.DisplayName       = cDisplayName              # default: "Raspi-Data Server"


# Log files
g.DataLogFile       = cDataLogFile              # default: "DataServer.datalog"
g.ProgLogFile       = cProgLogFile              # default: "DataServer.proglog"


## needed if cTransferType is "MQTT" or "BOTH":
if cTransferType.upper() in ("WIFI", "MQTT", "BOTH"):
    g.TransferType = cTransferType.upper()
else:
    emsg  = "You have configured a TransferType of '{}', which does not exist.\n".format(cTransferType)
    emsg += "Please, review your configuration. Cannot continue - will exit."
    print(emsg)
    sys.exit()

## needed if cTransferType is "WiFi" or "BOTH":
if (1024 <= cWiFiServerPort <= 65535):          # check proper WiFi Server Port
    g.WiFiServerPort = int(cWiFiServerPort)
else:
    emsg  = "You have configured a WiFiServerPort of '{}', which is not allowed.\n".format(int(cWiFiServerPort))
    emsg += "Please, review your configuration. Cannot continue - will exit."
    print(emsg)
    sys.exit()

## needed if cTransferType is "MQTT" or "BOTH":
g.IoTBrokerIP       = cIoTBrokerIP              # default: "test.mosquitto.org"
g.IoTBrokerPort     = cIoTBrokerPort            # default: 1883
g.IoTBrokerFolder   = cIoTBrokerFolder          # default: "/"
g.IoTTimeout        = cIoTTimeout               # default: 5

# ## GMC counter specific settings
g.GMCusage          = cGMCusage                 # use the GMC counter (True) or not (False)
g.GMCport           = cGMCport                  # "auto"
g.GMCbaudrate       = cGMCbaudrate              # "auto"
g.GMCvariables      = cGMCvariables             # "auto"

## I2C Sensor specific settings
g.I2Cusage          = cI2Cusage                 # to use or not use I2C

# use from one to all I2C sensors; use it (True) or not (False)
g.I2Cusage_LM75B    = cI2Cusage_LM75B           # T
g.I2Cusage_BME280   = cI2Cusage_BME280          # T, P, H
g.I2Cusage_BH1750   = cI2Cusage_BH1750          # Vis
g.I2Cusage_VEML6075 = cI2Cusage_VEML6075        # UV-A and UV-B, and helper data
g.I2Cusage_LTR390   = cI2Cusage_LTR390          # Vis and UV
g.I2Cusage_GDK101   = cI2Cusage_GDK101          # "Geiger" counts
g.I2Cusage_SCD30    = cI2Cusage_SCD30           # CO2
g.I2Cusage_SCD41    = cI2Cusage_SCD41           # CO2

# define the I2C address your sensor is set to
g.I2Caddr_LM75B     = cI2Caddr_LM75B            # 0x48; options: 0x48 | 0x49 | 0x4A | 0x4B | 0x4C | 0x4D | 0x4E | 0x4F
g.I2Caddr_BME280    = cI2Caddr_BME280           # 0x77; options: 0x76 | 0x77 NOTE: Bluedot breakout board has only 0x77; 0x76 is NOT available!
g.I2Caddr_BH1750    = cI2Caddr_BH1750           # 0x23; options: 0x23 | 0x5C
g.I2Caddr_VEML6075  = cI2Caddr_VEML6075         # 0x10; options: 0x10 | (no other option)
g.I2Caddr_LTR390    = cI2Caddr_LTR390           # 0x53; options: 0x53 | (no other option)
g.I2Caddr_GDK101    = cI2Caddr_GDK101           # 0x18; options: 0x18 | 0x19 | 0x1A | 0x1B
g.I2Caddr_SCD30     = cI2Caddr_SCD30            # 0x61; options: 0x61 | (no other option)
g.I2Caddr_SCD41     = cI2Caddr_SCD41            # 0x62; options: 0x62 | (no other option)


g.I2Cvars_LM75B     = cI2Cvars_LM75B            # {"CPS1st":10}
g.I2Cvars_BME280    = cI2Cvars_BME280           # {"Temp":3, "Press":3, "Humid":3}
g.I2Cvars_BH1750    = cI2Cvars_BH1750           # {"Xtra":1}
g.I2Cvars_VEML6075  = cI2Cvars_VEML6075         # {"CPM2nd":1, "CPS2nd":1, "CPM3rd":1, "CPS3rd":1}
g.I2Cvars_LTR390    = cI2Cvars_LTR390           # {"CPM":1, "CPS":60 }       # even at cps:10 big fluctuations due to single-digit values
g.I2Cvars_GDK101    = cI2Cvars_GDK101           # {"CPS1st":1}
g.I2Cvars_SCD30     = cI2Cvars_SCD30            # {"CPM":1}
g.I2Cvars_SCD41     = cI2Cvars_SCD41            # {"Xtra":1}

## Pulse specific settings
g.Pulseusage        = cPulseUsage               # use the Pulse device (True) or not (False)
g.PulseVariables    = cPulseVariables           # "auto"; defaults to "CPM, CPS"
if 5 <= int(cPulseCountPin) <=26:
    g.PulseCountPin = int(cPulseCountPin)       # default: 17; the GPIO pin in BCM mode to be used for pulse counting
else:
    emsg  = "You have configured a PulseCountPin of '{}', which is not allowed.\n".format(int(cPulseCountPin))
    emsg += "Allowed is 5 ... 26. But verify no other comflicting uses of the chosen pin!\n"
    emsg += "Please, review your configuration. Cannot continue - will exit."
    print(emsg)
    sys.exit()



# randomness
random.seed(66666)                              # seed with a develish sequence


def getProgName():
    """Return program_base, i.e. 'DataServer' even if named 'DataServer.py' """

    progname          = os.path.basename(sys.argv[0])
    progname_base     = os.path.splitext(progname)[0]

    return progname_base


def getPathToProgDir():
    """Return full path of the program directory"""

    dp = os.path.dirname(os.path.realpath(__file__))
    return dp


def getLogPath():
    """Return full path of the log directory"""

    dp = os.path.join(getPathToProgDir(), "log")
    return dp



def stime():
    """Return current time as YYYY-MM-DD HH:MM:SS"""

    return longstime()[:-4]


def longstime():
    """Return current time as YYYY-MM-DD HH:MM:SS.mmm, (mmm = millisec)"""

    return dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3] # ms resolution


def setIndent(arg):
    """increases or decreased the indent of prints"""

    if arg > 0:  g.PrintIndent += "   "
    else:        g.PrintIndent  = g.PrintIndent[:-3]


def commonPrint(ptype, *args, save=True):
    """Printing and saving
    ptype : DEBUG, VERBOSE, ERROR, ALERT
    args  : anything; will be printed and saved to file
    return: nothing
    """

    tag = ""
    for arg in args: tag += str(arg)

    if tag > "":
        g.PrintCounter += 1
        tag = "{:23s} {:7s}: {:.>6d} ".format(longstime(), ptype, g.PrintCounter) + g.PrintIndent + tag
        if   ptype == "ERROR":    print(TYELLOW   + tag + TDEFAULT)
        elif ptype == "ALERT":    print(BOLDRED   + tag + TDEFAULT)
        elif ptype == "OK":       print(BOLDGREEN + tag + TDEFAULT)
        elif ptype == "TECH":     print(BOLDCYAN  + tag + TDEFAULT)
        else:                     print(tag)
    else:
        print("")

    writeToProgLogFile(tag)


def dprint(*args):
    """Print args as single line"""

    if g.debug:   commonPrint("DEBUG", *args)


def vprint(*args):
    """Print args as single line"""

    if g.verbose: commonPrint("VERBOSE", *args)


def edprint(*args):
    """Print args as single line in yellow"""

    if g.debug:   commonPrint("ERROR", *args)


def rdprint(*args):
    """Print args as single line in red"""

    if g.debug:   commonPrint("ALERT", *args)


def gdprint(*args):
    """Print args as single line in green"""

    if g.debug:   commonPrint("OK", *args)


def cdprint(*args):
    """Print args as single line in cyan"""

    if g.debug:   commonPrint("TECH", *args)


def exceptPrint(e, srcinfo):
    """Print exception details (errmessage, file, line no)"""

    exc_type, exc_obj, exc_tb = sys.exc_info()
    fname                     = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]    # which file?

    # don't use dprint et al - they include saving, which might be at fault!
    print(" " * 39 + g.PrintIndent, TYELLOW + "EXCEPTION: {} ({}) in file: {} in line: {}".format(srcinfo, e, fname, exc_tb.tb_lineno), TDEFAULT)
    if g.tracebackFlag: print(TYELLOW, traceback.format_exc(), TDEFAULT)


def clamp(value, smallest, largest):
    """return value between smallest, largest, both inclusive;
    round to interger value, return as float"""

    return round(max(smallest, min(value, largest)), 0)


def getMyIP():
    """get the IP of the computer currently running this program"""
    # fails on IP6

    defname = "getMyIP: "
    try:
        st = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        st.connect(('8.8.8.8', 80))
        IP = st.getsockname()[0]
    except Exception as e:
        IP = '127.0.0.1'
        srcinfo = "Bad socket connect, IP set to:" + IP
        exceptPrint(defname + str(e), srcinfo)
    finally:
        st.close()

    return IP


def CheckIfRaspberryPi():
    """check if it is a Raspberry Pi computer"""
    # my Raspi: Raspberry Pi 4 Model B Rev 1.1
    # CAREFUL:  'model' holds a 'C'-string - ends with 0x00 !!!

    defname = "CheckIfRaspberryPi: "

    try:
        with io.open('/sys/firmware/devicetree/base/model', 'r') as m:
            compmodel = m.read().replace("\x00", "")
    except Exception as e:
        # exceptPrint(e, defname)
        compmodel = ""

    if 'raspberry pi' in compmodel.lower():
        g.isRaspberryPi = True
        g.computer      = compmodel
    else:
        g.isRaspberryPi = False
        g.computer      = "Unknown (Not a Raspi Computer)"


def createProgLogFile(msg):
    """Make new file, or empty old one, then write msg to file"""

    if g.ProgLogFile == "":
        # no writing if filename is empty
        g.ProgLogFileWOK = False
        dprint("{:33s} : {}".format("Init ProgLogFile", "ProgLogFile will NOT be written"))
        return

    try:
        with open(g.ProgLogPath, "wt") as log:
            log.write(msg + "\n")
            g.ProgLogFilePos = int(log.tell())

        dprint("{:33s} : {}".format("Init ProgLogFile", "Ok"))
    except Exception as e:
        msg = "{:33s} : {}".format("Init ProgLogFile", "FAILURE: ProgLogFile '{}' Could NOT be written!".format(g.ProgLogFile))
        exceptPrint(e, msg)


def writeToProgLogFile(msg):
    """initially append msg to the end of file,
    later overwrite file beginning after startphase"""

    defname = "writeToProgLogFile: "

    if g.ProgLogFileWOK == False: return                # no writing

    msg += "\n"
    try:
        with open(g.ProgLogPath, 'rb+') as log:         # write binary
            log.seek(int(g.ProgLogFilePos))
            log.write(msg.encode('utf-8'))
            g.ProgLogFilePos = log.tell()
            log.write(b"\n")

            if  g.ProgLogFilePhase == 1:                # startup done; set pos min
                g.ProgLogFilePhase  = 2                 # set phase 2; append data
                g.ProgLogFilePosMin = g.ProgLogFilePos  # pos min

            elif g.ProgLogFilePhase == 2:
                g.ProgLogFilePos = log.tell() - 1
                log.write(b"#" * 150 + b"\n")
                newpos = log.tell()
                cleaner = b""                           # find the remnants in the line up to '\n'
                while True:
                    c = log.read(1)
                    if c == b"" or c == b"\n":  break
                    else:                       cleaner += b" "
                log.seek(int(newpos))
                log.write(cleaner)

            if g.ProgLogFilePos > g.ProgLogFilePosMax:  # overflow; set pos to pos min
                log.truncate(g.ProgLogFilePos)
                g.ProgLogFilePos      = g.ProgLogFilePosMin

    except Exception as e:
        exceptPrint(e, defname)
        createProgLogFile("File had been deleted")
        g.ProgLogFilePos    = 22
        g.ProgLogFilePosMin = 22



def createDataLogFile(msg):
    """Make new file, or empty old one, then write msg to file"""

    if g.DataLogFile == "":
        # no writing if filename is empty
        g.DataLogFileWriteOK = False
        dprint("{:33s} : {}".format("Init DataLogFile", "DataLogFile will NOT be written"))
        return

    try:
        with open(g.DataLogPath, "wt") as log:       # append - file won't be deleted
            log.write(msg + "\n")
        dprint("{:33s} : {}".format("Init DataLogFile", "Ok"))
    except Exception as e:
        msg = "{:33s} : {}".format("Init DataLogFile", "FAILURE: DataLogFile '{}' Could NOT be written!".format(g.DataLogFile))
        exceptPrint(e, msg)
        try:
            with open(g.DataLogFile, "wt") as log:
                log.write(msg + "\n")
        except Exception as e:
            msg = "{:33s} : {}".format("Init DataLogFile", "FAILURE: DataLogFile '{}' 2nd Attempt: Could NOT be written!".format(g.DataLogFile))
            exceptPrint(e, msg)


def writeToDataLogFile(msg):
    """append msg to the end of file"""

    if g.DataLogFileWriteOK == False: return        # no writing

    try:
        with open(g.DataLogPath, 'a') as log:       # append text
            if log.tell() < g.DataLogFileMax:
                log.write(msg + "\n")               # write unless there is no space left
            else:
                log.write(g.DataLogFileMaxMsg)      # write last message and ...
                g.DataLogFileWriteOK = False        # ... block further writing
    except Exception as e:
        exceptPrint(e, "writeToDataLogFile")


def resetDevices(device = "All"):
    """resets devices; device = 'All' | 'GMC' | 'Pulse' | 'I2C' """

    g.ResetOngoing = True              # block data collection while this def runs
    while g.CycleOngoing:
        time.sleep(0.001)

    defname     = "resetDevices: "
    # rdprint(defname)
    setIndent(1)

    DEVICE      = device.upper()
    resetresp   = ""

    # GMC
    if DEVICE == "ALL" or DEVICE == "GMC" :
        from rdev_gmc import resetGMC
        if g.GMCusage:           resetresp += "GMC {}, "     .format(resetGMC())                   # reboot; will reset CPM to zero
                                                                                                   # -> takes 1 min to get correct CPM!

    # I2C
    if DEVICE == "ALL" or DEVICE == "I2C" :
        if g.I2Cusage:
            if g.I2Cusage_LM75B:     resetresp += "LM75B {}, "   .format(g.lm75b     .resetLM75B())    # fake reset, but clears deque
            if g.I2Cusage_BME280:    resetresp += "BME280 {}, "  .format(g.bme280    .resetBME280())   # reset, and clears deque
            if g.I2Cusage_BH1750:    resetresp += "BH1750 {}, "  .format(g.bh1750    .resetBH1750())   # true reset, and clears deque
            if g.I2Cusage_VEML6075:  resetresp += "VEML6075 {}, ".format(g.veml6075  .resetVEML6075()) # fake reset, but clears deque
            if g.I2Cusage_LTR390:    resetresp += "LTR390 {}, "  .format(g.ltr390    .resetLTR390())   # fake reset, but clears deque
            if g.I2Cusage_GDK101:    resetresp += "GDK101 {}, "  .format(g.gdk101    .resetGDK101())   # will reset counter, -> takes 1 min to get new read >0!

    # Pulse
    if DEVICE == "ALL" or DEVICE == "PULSE" :
        from rdev_pulse import resetPulse

        if g.Pulseusage:         resetresp  += "Pulse {}, "  .format(resetPulse())

    resetresp = resetresp[:-2]   # remove last ", "

    rdprint("{} Result: {}".format(defname, resetresp))

    setIndent(0)
    g.ResetOngoing = False       # re-allow data collection

    return resetresp


def KeyChecker():
    """gets last keypresses and acts on them"""

    ## local def ##################################################################
    def checkForKeys():
        """checking for a key press; uses curses, not available on windows"""

        return curses.wrapper(kchecker) # does all the inits for curses


    def kchecker(stdscr):
        """checking for keypress; uses curses, not available on windows"""

        stdscr.nodelay(True)            # do not wait for input when calling getch

        rv = ""
        while True:                     # collect all last keypresses
            c = stdscr.getch()
            if   c == -1:               break
            elif c >= 32 and c <= 128:  rv += chr(c)
        return rv

    ## end local def ##############################################################

    defname   = "KeyChecker: "

    ret       = checkForKeys()
    keyIgnore = False

    try:
        for c in ret:
            if keyIgnore:
                keyIgnore = False
                continue

            if c == "d":
                cdprint("KeyPress 'd' : negate debug")
                g.debug = not g.debug
                print("KeyPress 'd' : debug =>", g.debug)

            elif c == "v":
                cdprint("KeyPress 'v' : negate verbose")
                g.verbose = not g.verbose
                print("KeyPress 'v' : verbose =>", g.verbose)

            elif c == "s":
                cdprint("KeyPress 's' : I2C Scan")
                from rdev_i2c import scanI2C
                scanI2C()

            elif c == "C":
                cdprint("KeyPress 'C' : print g.GMCstoreCounts")
                cdprint(g.GMCstoreCounts)

            elif c == "T":
                cdprint("KeyPress 'T' : print g.I2CstoreLM75B")
                cdprint(g.I2CstoreLM75B)

            elif c == "L":
                cdprint("KeyPress 'L' : print g.I2CstoreBH1750")
                cdprint(g.I2CstoreBH1750)

            elif c == "P":
                cdprint("KeyPress 'P' : print g.PulseStore")
                cdprint(g.PulseStore)

            elif c == "V":
                cdprint("KeyPress 'V' : Versions: ")
                cdprint("Script:    ",   g.ProgName, ": ", g.__version__)
                cdprint("SMBus:     ",   g.versions["smbus"])
                cdprint("RPi.GPIO:  ",   g.versions["GPIO"])
                cdprint("paho-mqtt: ",   g.versions["paho-mqtt"])

            elif c == "[":
                # cdprint("KeyPress '[' : ESCAPE")
                keyIgnore = True        # to ignore 2nd key following the Escape char

            else:
                cdprint("KeyPress '{}' : Press one or more keys out of these:".format(c))
                cdprint("- h:    Help")
                cdprint("- d:    negate debug")
                cdprint("- v:    negate verbose")
                cdprint("- s:    I2C scan")
                cdprint("- C:    print g.GMCstoreCounts")
                cdprint("- T:    print g.I2CstoreLM75B")
                cdprint("- L:    print g.I2CstoreBH1750")
                cdprint("- P:    print g.PulseStore")
                cdprint("- V:    Versions")
    except Exception as e:
        exceptPrint(e, defname)


# Data collection; used by WiFi and MQTT
def collectData(avg=None):
    """
    get the data as byte sequence in the form needed by GeigerLog
    parameter:  avg: get the data as average over the last avg seconds; avg > 0
    return:     data as a CSV list (as bytes): M, S, M1, S1, M2, S2, M3, S3, T, P, H, X (must have 11 commas)
      like:                                  b'1733.0,36.0,1884.7,30.2,34.0,34.2,34.0,0.0,34.0,32.3,32.0,2.0'
    """
    # NOTE: parameter avg is not used

    if g.ResetOngoing:     return b"," * 11   # send 11 commas on ongoing reset

    start    = time.time()
    defname  = "collectData: "

    dprint(defname)
    setIndent(1)

    from rdev_gmc   import getDataGMC
    from rdev_i2c   import getDataI2C
    from rdev_pulse import getDataPulse

    # Merging the Dicts:
    # -  In Python 3.9.0 or greater: z = x | y
    # -  In Python 3.5 or greater:   z = {**x, **y}
    setIndent(1)
    rawDict = {}
    if g.GMCinit:   rawDict = {**rawDict, **getDataGMC()}
    if g.I2Cinit:   rawDict = {**rawDict, **getDataI2C()}
    if g.PulseInit: rawDict = {**rawDict, **getDataPulse()}
    setIndent(0)

    # sort into native GL variable order
    DataDict = {}
    for vname in g.GLVarNames:
        if vname in rawDict:  DataDict.update({vname : rawDict[vname]})

    # create the CSV string in GL var order to send to data-file
    CSVstring = ""
    for vname in g.GLVarNames:
        if vname in DataDict:  CSVstring += "{:8.7g},".format(DataDict[vname])
        else:                  CSVstring += "{:8s},"  .format(" ")
    CSVstring = CSVstring[:-1]                  # remove "," at end

    dur = 1000 * (time.time() - start) # ms

    # save to file
    g.WiFiIndex += 1
    writeToDataLogFile("{:7d}, {:23s}, {}, {:8.3f}".format(g.WiFiIndex, longstime(), CSVstring, dur))

    # prints like: 'collectData:   Temp:20.9  Xtra:471  CPM:618.0  CPS:12   dur: 0.136 ms'
    strdict = str(DataDict).replace(": ", ":").replace(",", "").replace("'", "").replace("{", "").replace("}", "")
    # dprint("{:14s}{}  dur:{:0.2f} ms".format(defname, strdict, dur))
    dprint(defname, "{:10s}{}  dur:{:0.2f} ms".format("combined:", strdict, dur))

    CSV4Web = CSVstring.replace(" ", "")      # remove blanks for transmission

    setIndent(0)
    return bytes(CSV4Web, "UTF-8")


def getCRC8(data):
    """
    calculates 8-Bit checksum as defined by Sensirion
    data:   tuple of 2 bytes
    return: CRC8 of data
    """

    # Adapted from Sensirion code - must clip crc to 8 bit (uint8)
    # in depth: https://barrgroup.com/embedded-systems/how-to/crc-calculation-c-code
    # // Original Sensirion C code:
    # // Example:       CRC(0xBEEF) = 0x92  (dec:146)
    # // my examples:   CRC(0x0000) = 0x81  (dec:129)
    # //
    # #define CRC8_POLYNOMIAL 0x31
    # #define CRC8_INIT 0xFF

    # uint8_t sensirion_common_generate_crc(const uint8_t* data, uint16_t count) {
    #     uint16_t    current_byte;
    #     uint8_t     crc = CRC8_INIT;
    #     uint8_t     crc_bit;
    #     /* calculates 8-Bit checksum with given polynomial */
    #     for (current_byte = 0; current_byte < count; ++current_byte) {
    #         crc ^= (data[current_byte]);
    #         for (crc_bit = 8; crc_bit > 0; --crc_bit) {
    #             if (crc & 0x80)
    #                 crc = (crc << 1) ^ CRC8_POLYNOMIAL;
    #             else
    #                 crc = (crc << 1);
    #         }
    #     }
    #     return crc;
    # }

    CRC8_POLYNOMIAL = 0x31
    CRC8_INIT       = 0xFF

    count           = len(data)
    crc             = CRC8_INIT
    for dbyte in data:
        # print("dbyte: ", dbyte)
        crc = (crc ^ dbyte) & 0xFF                                  # limit to uint8
        for i in range(0, 8):
            if crc & 0x80:  crc = (crc << 1) ^ CRC8_POLYNOMIAL
            else:           crc = crc << 1
            crc = crc & 0xFF                                        # limit to uint8
            # print("i: ", i, ", crc: ", crc)

    return crc


def getPoissonValue(mean):
    """get  a single value from a Poisson distribution with mean 'mean'"""

    start = time.time()
    defname = "getPoissonValue: "

    x       = np.random.poisson(mean)

    dur = 1000 * (time.time() - start)
    rdprint(defname, "Value Poisson({}): {}  (dur: {:0.3f} ms)".format(mean, x, dur))

    return x

