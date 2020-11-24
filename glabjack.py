#!/usr/bin/python3
# -*- coding: UTF-8 -*-

"""
glabjack.py - GeigerLog commands to handle the LabJack U3 with EI1050 probe

NOTE: verfied to work **ONLY** on Linux; it may work on Mac
      Windows needs a different installation of Exodriver
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
__credits__         = [""]
__license__         = "GPL3"

"""
For LabJack Python support see:
https://labjack.com/support/software/examples/ud/labjackpython

For threading example see:
https://github.com/labjack/LabJackPython/blob/master/Examples/EI1050/ei1050SampleApp.py

INSTALLATIONS:
To use this device you need the installation of:
- the so called Exodriver
- the LabJackPython library
- the u3 Python module
- the ei1050 Python module

The Exodriver is here: https://labjack.com/support/software/installers/exodriver
The latest version is 2.6.0, compatible with Linux kernels from 2.6.28 onwards.
Download, unzip and run: $ sudo ./install.sh

LabJackPython is needed in the version 2.0.0 (Jan 2019) or later in order for
compatibility with Python3! Available here:
https://labjack.com/support/software/examples/ud/labjackpython
Unzip and install with: $ sudo python3 setup.py install

Included in the LabJackPython download are the modules u3 and ei1050

NOTE:
For detection of a busy LabJack see my discussion "Detecting the presence of an
U3 even when in use elsewhere" at: https://labjack.com/comment/6040


LabJack Software Versions:
--- LabJackPython                : 2.0.0
--- U3                           : unknown
--- EI1050                       : unknown
Connected Probe (Status)         : EI1050 (0)
LabJack Config:
--- BootloaderVersion            : 0.11
--- CIODirection                 : 0
--- CIOState                     : 0
--- CompatibilityOptions         : 0
--- DAC0                         : 0
--- DAC1                         : 0
--- DAC1Enable                   : 0
--- DeviceName                   : U3B
--- EIOAnalog                    : 255
--- EIODirection                 : 0
--- EIOState                     : 0
--- FIOAnalog                    : 255
--- FIODirection                 : 0
--- FIOState                     : 0
--- FirmwareVersion              : 1.54
--- HardwareVersion              : 1.21
--- LocalID                      : 2
--- ProductID                    : 3
--- SerialNumber                 : 320015845
--- TimerClockConfig             : 0
--- TimerClockDivisor            : 256
--- TimerCounterMask             : 0
--- VersionInfo                  : 1
"""

from   gutils       import *

import LabJackPython                        # see installation instructions above
import u3                                   # dito
import ei1050                               # dito



def setLabJackSettings(a,b,c):
    """Set Settings ... at the LabJack Device"""

    global LJdevice, LJprobe, targetQueue, thread

    # There are no settings (at least not for the EI1050 probe)
    pass


def getLabJackValues(varlist):

    global LJdevice, LJprobe, targetQueue, thread

    alldata = {}

    if not gglobs.LJConnection:
        dprint("getLabJackValues: NO LabJack connection")
        return alldata

    if varlist == None:
        return alldata

    latestReading   = None
    while not targetQueue.empty():
        latestReading = targetQueue.get()

    if latestReading != None:
        for vname in varlist:
            if   vname == "T":  # from the probe EI1050
                Temp            = latestReading.getTemperature()
                Temp            = round(scaleVarValues(vname, Temp, gglobs.ValueScale[vname]), 2)
                alldata.update({vname: Temp})

            elif vname == "H":  # from the probe EI1050
                Hum             = latestReading.getHumidity()
                Hum             = round(scaleVarValues(vname, Hum, gglobs.ValueScale[vname]), 2)
                alldata.update({vname: Hum})

            elif vname == "X":  # from the U3 internal sensor
                u3t             = LJdevice.getTemperature() - 273.15
                u3t             = round(scaleVarValues(vname, u3t, gglobs.ValueScale[vname]), 2)
                alldata.update({vname: u3t})

    vprint("{:20s}:  Variables:{}  Data:{}".format("getLabJackValues", varlist, alldata))

    return alldata


def getLabJackInfo(extended = False):
    """Info on the LabJack Device"""

    global LJdevice, LJprobe, targetQueue, thread

    if gglobs.LJActivation == False:
        dprint("initLabJack: LabJack device not activated")
        return "LabJack device not activated"

    #print("--- getLabJackInfo LabJackPython.listAll(3):", LabJackPython.listAll(3))
    if gglobs.LJConnection  == True:
        LJInfo = """Connected Device:             '{}'
Connected Probe (Status):     {} ({})
Connection:                   USB
Configured Variables:         {}""".format(\
                                           gglobs.LJDeviceName, \
                                           "EI1050", \
                                           LJprobe.getStatus(), \
                                           gglobs.LJVariables)

        if extended == True:
            LJInfo += "\nLabJack Software Versions:\n"
            LJInfo += "--- {:28s} : {}\n".format("LabJackPython", gglobs.LJversionLJP)
            LJInfo += "--- {:28s} : {}\n".format("U3",            gglobs.LJversionU3)
            LJInfo += "--- {:28s} : {}\n".format("EI1050",        gglobs.LJversionEI1050)
            LJInfo += "LabJack Config:"
            for key, value in sorted(LJdevice.configU3().items()):
                LJInfo += "\n--- {:28s} : {}".format(key, value)
    else:
        LJInfo = """No connected device"""

    return LJInfo


def terminateLabJack():
    """opposit of init ;-)"""

    global LJdevice, LJprobe, targetQueue, thread

    if not gglobs.LJActivation: return

    try:
        thread.stop()
        thread.join()       # ???
    except Exception as e:
        print("terminateLabJack: Exception: ", e)

    dprint("terminateLabJack: Terminating LabJack")

    if gglobs.LJConnection:
        LJdevice.close()        # important to detach from USB  !!!
        gglobs.LJConnection  = False


def initLabJack():
    """Initialize LabJack U3 with probe EI1050"""

    global LJdevice, LJprobe, targetQueue, thread

    fncname = "initLabJack: "

    if not gglobs.LJActivation:
        dprint(fncname + "LabJack device not activated")
        return "LabJack device not activated"

    dprint(fncname + "Initialzing LabJack")
    setDebugIndent(1)
    #print("--- initLabJack LabJackPython.listAll(3):", LabJackPython.listAll(3))

    gglobs.LJDeviceName = "LabJack"

    # try to get the versions
    gglobs.LJversionLJP         = LabJackPython.__version__ # version of LabJackPython
    try:
        gglobs.LJversionU3      = u3.__version__            # version of U3
    except:
        gglobs.LJversionU3      = "unknown"

    try:
        gglobs.LJversionEI1050  = EI1050.__version__        # version of EI1050
    except:
        gglobs.LJversionEI1050  = "unknown"

    try:
        LJdevice.close()                                    # important to detach from USB!
    except:
        pass

    # open the device
    try:
        lju3 = u3.U3()
    except Exception as e:
        #print("e:", e, type(e), "str(e):", str(e))

        stre    = str(e)
        srcinfo = fncname + "ERROR: U3 exception"
        exceptPrint(e, sys.exc_info(), srcinfo)

        if   "Couldn't open device. Please check that the device you are trying to open is connected." in stre:
            errmsg = "No LabJack device found. Is it connected?"

        elif "Couldn't open device. Device access or claim error" in stre:
            errmsg = "A LabJack device was found, but it may already be in use by a different program"

        else:
            errmsg = "Connecting to LabJack device gave unexpected error: {}".format(stre)

        gglobs.LJConnection     = False

        return errmsg

    targetQueue = queue.Queue()
    thread = ei1050.EI1050Reader(lju3, targetQueue)
    thread.start()

    LJdevice                = lju3
    LJprobe                 = ei1050.EI1050(LJdevice)
    gglobs.LJConnection     = True

    if gglobs.LJVariables  == "auto":   gglobs.LJVariables = "T, H, X"

    DevVars = gglobs.LJVariables.split(",")
    for i in range(0, len(DevVars)):  DevVars[i] = DevVars[i].strip()
    gglobs.DevicesVars["LabJack"] = DevVars
    #print("DevicesVars:", gglobs.DevicesVars)

    setDebugIndent(0)

    return ""
