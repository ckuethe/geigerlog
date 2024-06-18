#! /usr/bin/env python3
# -*- coding: utf-8 -*-

"""
rdev_gmc.py - DataServer's GMC device handler

include in programs with:
    import rdev_gmc
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

from   rutils   import *


def initGMC():
    """Initialize GMC"""

    # needed for GMC: module pyserial
    try:
        import serial                      # (part of pyserial) communication with serial port
        import serial.tools.list_ports     # (part of pyserial) allows listing of serial ports
    except ImportError as ie:
        msg  = "The module 'pyserial' was not found, but is required for using a GMC counter."
        exceptPrint(ie, msg)
        msg += "\nInstall with 'python -m pip install -U pyserial'."
        return msg
    except Exception as e:
        msg = "Unexpected Failure importing 'serial'. Cannot use GMC counter. Exiting."
        exceptPrint(e, msg)
        return msg + str(e)

    defname = "initGMC: "
    dprint(defname)
    setIndent(1)

    if g.GMCport         == "auto" : g.GMCport      = "auto"
    else:                            g.GMCport      = g.GMCport

    if g.GMCbaudrate     == "auto" : g.GMCbaudrate  = "auto"
    else:                            g.GMCbaudrate  = g.GMCbaudrate

    if g.GMCtimeout      == "auto":  g.GMCtimeout   = 1

    if g.GMCvariables    == "auto" : pv = "CPM1st, CPS1st, CPM2nd, CPS2nd"#.split(",")
    else:                            pv = g.GMCvariables

    # check if customized cGMCvariables are ok
    g.GMCvariables = []
    for vname in pv.split(","):
    # for vname in pv:
        pvar = vname.strip()
        if pvar in g.GMCvarsAll:
            g.GMCvariables.append(pvar)
        else:
            edprint("ERROR: '{}' is not a possible variable for GMC.".format(pvar))
            edprint("Allowed is: {}".format(g.GMCvarsAll))
            setIndent(0)
            return "ERROR"


    # finding USB-to-Serial port for GMC
    if g.GMCport != "auto":
        # GMCport was set manually; do not change
        pass
    else:
        # GMCport is "auto". Search for ports on this system
        dprint("Searching for USB-to-Serial Ports - found these:")
        GMCports = serial.tools.list_ports.comports()
        if len(GMCports) == 0:
            dprint("No USB-to-Serial Ports found on this system - Cannot run without one. Exiting.")
            setIndent(0)
            return "Failure - No USB-to-Serial Ports found on this system"

        # check for a port with chip CH340
        foundport = False
        setIndent(1)
        for port in GMCports :
            dprint (str(port))
            if  port.vid == 0x1a86 and port.pid == 0x7523:
                foundport = True
                g.GMCport = port.device
                break
        setIndent(0)
        if not foundport:
            dprint("No USB-to-Serial Ports for GMC counters found on this system - Cannot run without one. Exiting.")
            setIndent(0)
            return "Failure - No USB-to-Serial Ports for GMC counters found on this system"
    # dprint("   Selected Port: " + g.GMCport)

    # getting baudrate
    if g.GMCbaudrate != "auto":
        # g.GMCbaudrate was set manually; do not change
        pass
    else:
        # GMCbaudrate is "auto". Find the baudrate; begin at higest
        testbr = (115200, 57600)
        for tbr in testbr:
            try:
                testser = serial.Serial(g.GMCport, tbr, timeout=g.GMCtimeout)
                # print("testser: ", testser)
                bwrt = testser.write(b'<GETVER>>')
                trec = testser.read(14) # may leave bytes in the pipeline, if GETVER has
                                        # more than 14 bytes as may happen in newer counters
                while True:
                    cnt = testser.in_waiting
                    if cnt == 0: break
                    trec += testser.read(cnt)
                    time.sleep(0.1)

                testser.close()

                if trec.startswith(b"GMC"):
                    g.GMCbaudrate = tbr
                    # dprint("Baudrate: Success with {}".format(g.GMCbaudrate))
                    g.GMCcounterversion = trec.decode("UTF-8")
                    break

            except Exception as e:
                exceptPrint(e, defname + "ERROR: Serial communication error on finding baudrate")
                baudrate = None
                break

    # dprint("   Selected Baudrate: {}".format(g.GMCbaudrate))
    if g.GMCbaudrate == "auto":
        dprint("Could not establish communication with a counter. Is it connected? Will exit.")
        setIndent(0)
        return "Failure"

    # open the serial port with selected settings
    try:
        g.GMCser  = serial.Serial(g.GMCport, g.GMCbaudrate, timeout=g.GMCtimeout)
    except Exception as e:
        exceptPrint(e, defname + "FAILURE connecting to GMC counter. Cannot continue.")
        return "Failure"

    g.GMCinit = True

    # set GMCbytes
    if   "GMC-3"         in g.GMCcounterversion:   g.GMCbytes  = 2    # all 3XX
    elif "GMC-500Re 1."  in g.GMCcounterversion:   g.GMCbytes  = 2    # perhaps Mike is only user
    elif "GMC-5"         in g.GMCcounterversion:   g.GMCbytes  = 4    # all 500+ and 510
    elif "GMC-6"         in g.GMCcounterversion:   g.GMCbytes  = 4    # all 600
    else:                                          g.GMCbytes  = 4    # everything else

    # print settings
    dprint("GMC Settings:")
    dprint("   {:24s} : {}".format("GMC Counter Version"      , g.GMCcounterversion))
    dprint("   {:24s} : {}".format("GMC Serial Port"          , g.GMCport))
    dprint("   {:24s} : {}".format("GMC Serial Baudrate"      , g.GMCbaudrate))
    dprint("   {:24s} : {}".format("GMC Serial Timeout (sec)" , g.GMCtimeout))
    dprint("   {:24s} : {}".format("GMC Counter Byte-Counts"  , g.GMCbytes))
    dprint("   {:24s} : {}".format("GMC Variables"            , g.GMCvariables))

    g.GMCstoreCounts.append(getValGMC())

    setIndent(0)
    return "Ok"


def terminateGMC():
    """shuts down the counter"""

    defname = "terminateGMC: "

    if g.GMCser is not None:
        try:
            g.GMCser.close()
        except Exception as e:
            msg = "Unexpected Failure closing GMC Serial connection"
            exceptPrint(e, msg)
    g.GMCser = None

    return "Terminate GMC: Done"


def resetGMC():
    """do a Reboot of the counter"""
    # NOTE: this will reset CPM to zero

    defname = "resetGMC: "
    dprint(defname)
    setIndent(1)

    wcommand = b'<REBOOT>>'
    rlength  = 0
    try:
        bwrt = g.GMCser.write(wcommand)                           # bytes-written (type int)
        brec = g.GMCser.read(rlength)                             # rec received  (type bytes)
        # dprint(defname + "bwrt: ", bwrt, "  brec: ", brec)
        dprint("- done rebooting")
    except Exception as e:
        exceptPrint(e, defname)
        msg = "# EXCEPTION: {} '{}'\n".format(defname, str(e))
        edprint(msg)

    time.sleep(0.6)

    getValGMC()

    setIndent(0)
    return "Ok"


def getDataGMC():
    """get the data from GMC Geiger counter deque-store into dict for the web"""

    start   = time.time()
    defname = "getDataGMC: "

    # GMCstoreCounts is fixed at len=1, but may have multiple var values as list!
    GMCdict = {}
    for i, vname in enumerate(g.GMCvariables):  GMCdict.update({vname: g.GMCstoreCounts[0][i]})

    dur     = 1000 * (time.time() - start)
    dprint(defname + "  {}  dur: {:0.3f} ms".format(GMCdict, dur))

    return GMCdict


def getValGMC():
    """get the var values from a GMC Geiger counter and put into list"""

    start   = time.time()
    defname = "getValGMC: "
    # rdprint(defname, g.GMCvariables)

    GMCvals = []
    for vname in g.GMCvariables:
        GMCvals.append(getRawGMC(vname))

    dur     = 1000 * (time.time() - start)
    vprint("- {:17s}{}:{}  dur: {:0.3f} ms".format(defname, g.GMCvariables, GMCvals, dur))

    return GMCvals


def getRawGMC(vname):
    """
    input:  vname - varname to get value for (only for CPM, CPS, CPM1st, CPS1st, CPM2nd, CPS2nd - all others return NAN)
    return: value - as float
    """

    start   = time.time()
    defname = "getRawGMC: "
    error   = False

    if   vname == "CPM"   : wcommand = b'<GETCPM>>'
    elif vname == "CPS"   : wcommand = b'<GETCPS>>'
    elif vname == "CPM1st": wcommand = b'<GETCPML>>'
    elif vname == "CPS1st": wcommand = b'<GETCPSL>>'
    elif vname == "CPM2nd": wcommand = b'<GETCPMH>>'
    elif vname == "CPS2nd": wcommand = b'<GETCPSH>>'
    else:                   return g.NAN

    for trial in range(5):  # try up to 5 times
        brec = b""
        if time.time() - start > 0.5:
            msg = "# {} 'takes too long; giving up in trial #{}".format(defname, trial)
            edprint(msg)
            writeToDataLogFile(msg)
            error = True
            break

        try:
            bwrt = g.GMCser.write(wcommand)                           # bytes-written (type int)
            brec = g.GMCser.read(g.GMCbytes)                          # rec received  (type bytes)
            break                                                     # break (successful)
        except Exception as e:
            exceptPrint(e, defname)
            msg = "# EXCEPTION: {} '{}' trial #{}".format(defname, str(e), trial)
            edprint(msg)
            writeToDataLogFile(msg)
            error = True

        time.sleep(0.05)        # does it help?


    if len(brec) == g.GMCbytes:
        # ok, got expected number of bytes
        # "mask out high bits" applies only to CPS* calls on 300 series counters
        # 4 bytes: value = ((brec[0] << 8 | brec[1]) << 8 | brec[2]) << 8 | brec[3]
        # 2 btyes: value =  (brec[0] << 8 | brec[1])
        value = brec[0] << 8 | brec[1]
        if   g.GMCbytes == 4:                     value = (value << 8 | brec[2]) << 8 | brec[3]
        elif g.GMCbytes == 2 and "CPS" in vname : value = value & 0x3fff     # mask out high bits

    else:
        # Fail, bytes missing or too many
        error = True
        msg = "# ERROR in byte count, got {} bytes, expected {}!".format(len(brec), g.GMCbytes)
        dprint(msg)
        writeToDataLogFile(msg)
        value = g.NAN

    dur     = 1000 * (time.time() - start)
    g.GMCcallduration = dur
    loooong = "" if dur < 30 else "***Looooooong***"

    msg     = "- {:17s}{:7s}{:7s}:{:9.3f}   brec:{:20s} trial:{} dur:{:0.2f} ms  {}".\
              format(defname, vname, str(wcommand), value, str(brec), trial + 1, dur, loooong)
    if error or dur > 10:   rdprint(msg)
    else:                   vprint (msg)

    return value

