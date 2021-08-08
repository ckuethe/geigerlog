#! /usr/bin/env python3
# -*- coding: UTF-8 -*-

"""
gdev_labjack.py - GeigerLog commands to handle the LabJack U3 with EI1050 probe

NOTE: verfied to work on Linux; it may work on Mac
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
__copyright__       = "Copyright 2016, 2017, 2018, 2019, 2020, 2021"
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
- the Python module: LabJackPython.py
- the Python module: u3.py
- the Python module: ei1050.py

Exodriver -- Linux-only:
The Exodriver is here: https://labjack.com/support/software/installers/exodriver
The latest version is 2.6.0, compatible with Linux kernels from 2.6.28 onwards.
The exodriver is stored as: /usr/local/lib/liblabjackusb.so.

LabJackPython, u3:
LabJackPython is needed in the version 2.0.0 (Jan 2019) or later. Latest version
(Feb 2021) is 2.0.4 from September 9, 2020.
Location: https://labjack.com/support/software/examples/ud/labjackpython
But preferably the modules are installed via pip (includes u3):
    python3 -m pip install -U LabJackPython
On my Python Virtual instllations 'u3.py' is located at: ( X= 6,7,8,9,10)
/home/ullix/geigerlog/vgl3X/lib/python3.X/site-packages/u3.py

ei1050.py:
https://github.com/labjack/LabJackPython/tree/master/Examples/EI1050
example: https://forums.labjack.com/index.php?showtopic=5804


NOTE:
For detection of a busy LabJack see my discussion "Detecting the presence of an
U3 even when in use elsewhere" at: https://labjack.com/comment/6040


###############################################################################
New LabJackSoftware 2021-02-03:

==== Device Mappings =================================================================
The configuration is determined in the configuration file geigerlog.cfg

Device      :  CPM    CPS    CPM1st CPS1st CPM2nd CPS2nd CPM3rd CPS3rd   T   P   H   X
--------------------------------------------------------------------------------------
LabJack     :  -      -      -      -      -      -      -      -        X   -   X   X
Mapping is valid

==== LabJack Device Info Extended ====================================================
Configured Connection:        USB (auto-configuration)
Connected Device:             'LabJack'
Connected Probe (Status):     EI1050 (0)
Connection:                   USB
Configured Variables:         T, H, X
LabJack Software Versions:
--- LabJackPython                : 2.0.4
--- U3                           : unknown
--- EI1050                       : unknown
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
###############################################################################
"""

from   gsup_utils       import *

try:
    import LabJackPython                        # see installation instructions above
    import ei1050                               # dito
    import u3                                   # dito
    #raise Exception
except Exception as e:
    playWav("err")
    exceptPrint(e, "Exception importing LabJack modules")
    edprint("See installation instructions in file gdev_labjack.py")
    #~edprint("Halting GeigerLog") # not halting; no harm is done by running
    #~sys.exit()



def setLabJackSettings(a, b, c):
    """Set Settings ... at the LabJack Device"""

    global LJdevice, LJprobe, targetQueue, thread

    # There are no settings (at least not for the EI1050 probe)
    pass


def getLabJackValues(varlist):

    global LJdevice, LJprobe, targetQueue, thread

    fncname = "getLabJackValues: "

    alldata = {}

    latestReading   = None
    while not targetQueue.empty():
        try:
            latestReading = targetQueue.get()
        except Exception as e:
            exceptPrint(fncname + str(e), "targetQueue.get() failed")
            latestReading = gglobs.NAN

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
                try:
                    u3t         = LJdevice.getTemperature() - 273.15
                except Exception as e:
                    exceptPrint(fncname + str(e), "LJdevice.getTemperature() failed")
                    u3t = gglobs.NAN
                u3t             = round(scaleVarValues(vname, u3t, gglobs.ValueScale[vname]), 2)
                alldata.update({vname: u3t})

    printLoggedValues(fncname, varlist, alldata)

    return alldata


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

    gglobs.LJDeviceName          = "LabJack"
    gglobs.LJDeviceDetected      = gglobs.LJDeviceName
    gglobs.Devices["LabJack"][0] = gglobs.LJDeviceDetected

    # try to get the versions
    try:    gglobs.LJversionLJP     = LabJackPython.__version__ # version of LabJackPython
    except: gglobs.LJversionLJP     = "unknown"

    try:    gglobs.LJversionU3      = u3.__version__            # version of U3
    except: gglobs.LJversionU3      = "undefined"

    try:    gglobs.LJversionEI1050  = EI1050.__version__        # version of EI1050
    except: gglobs.LJversionEI1050  = "undefined"

    try:    LJdevice.close()                                    # important to detach from USB!
    except: pass

    # open the device
    try:
        lju3 = u3.U3()
    except Exception as e:
        stre    = str(e)

        if   "Couldn't open device. Please check that the device you are trying to open is connected." in stre:
            errmsg = "No LabJack device found. Is it connected?"

        elif "Couldn't open device. Device access or claim error" in stre:
            errmsg = "A LabJack device was found, but it may already be in use by a different program."

        elif "name 'u3' is not defined" in stre:
            errmsg = "Failure loading LabJack driver 'u3'. Please, check installation."

        else:
            errmsg = "Connecting to LabJack device gave unexpected error: {}".format(stre)

        srcinfo = fncname + "ERROR: U3 exception: " + errmsg
        exceptPrint(e, srcinfo)

        gglobs.LJConnection     = False

        return errmsg

    targetQueue = queue.Queue()
    thread = ei1050.EI1050Reader(lju3, targetQueue)
    thread.start()

    LJdevice                = lju3
    LJprobe                 = ei1050.EI1050(LJdevice)
    gglobs.LJConnection     = True

    if gglobs.LJVariables  == "auto":   gglobs.LJVariables = "T, H, X"

    setLoggableVariables("LabJack", gglobs.LJVariables)

    setDebugIndent(0)

    return ""


def terminateLabJack():
    """opposit of init ;-)"""

    global LJdevice, LJprobe, targetQueue, thread

    if not gglobs.LJActivation: return

    fncname = "terminateLabJack: "

    try:
        thread.stop()
        thread.join()       # ???
    except Exception as e:
        print(fncname + "Exception: ", e)

    dprint(fncname)

    if gglobs.LJConnection:
        LJdevice.close()        # important to detach from USB  !!!
        gglobs.LJConnection  = False


def printLJDevInfo(extended=False):
    """prints basic info on the LabJack device"""

    setBusyCursor()

    txt = "LabJack Device"
    if extended:  txt += " Extended"
    fprint(header(txt))
    fprint("Configured Connection:", "USB (auto-configuration)")
    fprint(getLabJackInfo(extended=extended))

    setNormalCursor()


def getLabJackInfo(extended = False):
    """Info on the LabJack Device"""

    global LJdevice, LJprobe, targetQueue, thread

    fncname = "getLabJackInfo: "

    if gglobs.LJActivation == False:
        msg = "LabJack device not activated"
        dprint(fncname + msg)
        return msg

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

