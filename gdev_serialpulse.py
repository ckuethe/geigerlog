#! /usr/bin/env python3
# -*- coding: utf-8 -*-

"""
gdev_serialpulse.py -   GeigerLog device to count "clicks" coming as single bytes
                        from a USB-To-Serial device after it receives pulses to its RX input.
                        Used e.g. for Audio-clicks as inputs (after pulse shaping?)
                        or from a device sending pulses 0...3.3V or 0...5V.
                        Preferrably as pulses normally HIGH, and LOW during a pulse.
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


def initSerialPulse():
    """Initializes the SerialPulse Device, opens the serial port, and starts the thread to
    monitor the serial input for clicks"""

    ### local def #############################################################################

    def makeSerialConnection(port, baud, toR, toW):
        """try to make a serial connaction and return handle (None on failure) and error message"""

        defname = "makeSerialConnection: "

        # rdprint(defname,  "(port, baud, toR, toW): ", (port, baud, toR, toW))
        serconn = None
        errmsg  = ""
        try:
            serconn = serial.Serial(port, baud, timeout=toR, write_timeout=toW)

        except OSError as oe:
            errmsg  = "OSError"
            exceptPrint(oe, defname + errmsg )

        except Exception as e:
            errmsg  = "Exception "
            if e.errno == 19: errmsg += "USB-To-Serial Port '{}' does not exist".format(g.SerialPulseUsbport)
            else:             errmsg += "Unexpected Error"
            exceptPrint(e, defname + errmsg)

        else:
            errmsg = ""

        return serconn, errmsg


    def findPort(baud, toR, toW):
        """
        find an USB-To-Serial Port not in use by GMC, GS, or I2C, and test it
        for returns of any bytes when reading from the port without having send
        any command to the port.
        If the port returns any bytes it is the right port!
        If no such port found, then return the last found unused port.
        If no unused port is found, return string "None found"
        """

        defname    = "findPort: "
        port       = None
        NWait      = 0
        foundPort  = False
        allserconn = []
        fprint("Searching for SerialPulse port ...")
        QtUpdate()

        try:
            lp = getPortList(symlinks=False)
            # rdprint(defname, (g.GMC_usbport, g.I2Cusbport, g.GSusbport))

            for p in lp:
                # p.device is like: /dev/ttyUSB0
                if p.device in (g.GMC_usbport, g.I2Cusbport, g.GSusbport): continue  # this port is in use
                allserconn.append({"port" : p.device, "errmsg" : None, "handle" : None })
            # rdprint(defname, "allserconn: ", allserconn)

            # open all ports
            for i, a in enumerate(allserconn):
                hh, ee = makeSerialConnection(allserconn[i]["port"], baud, toR, toW)
                if hh is not None:
                    allserconn[i]["handle"] = hh
                    allserconn[i]["errmsg"] = ee
                    cdprint(defname, "#{}  Found unused port '{} ...'".format(i, str(a)[0:148]))
                else:
                    rdprint(defname, "Cannot open port")


            # testing for bytes in pipeline for up to waitsec sec
            waitsec = 6
            cdprint(defname, "Testing all ports for having bytes in pipeline")
            start = time.time()
            while time.time() - start < waitsec:
                time.sleep(0.2)
                for i, a in enumerate(allserconn):
                    port = allserconn[i]["port"]
                    # rdprint(defname, "Testing port: {}".format(port))
                    if allserconn[i]["handle"] is not None:
                        NWait = allserconn[i]["handle"].in_waiting
                        if NWait > 0:
                            brec  = allserconn[i]["handle"].read(NWait)
                            cdprint(defname, "Port: {}  NWait: {}  brec[0:30]: {}".format(port, NWait, brec[0:30]))
                            foundPort = True
                            break       # break for-loop
                if foundPort: break # break while-loop

            # close all ports
            for i, a in enumerate(allserconn):
                if allserconn[i]["handle"] is not None:
                    allserconn[i]["handle"].close()
                    allserconn[i]["handle"] = None

            if foundPort:
                msg = "Found matching port: {}".format(port)
                gdprint(defname, msg)
                fprint("<green>" + msg)
            elif port is None:
                rdprint(defname, "No port found; returning 'None'")
            else:
                msg = "Failure finding port; using last-tested port:'{}'. Verify functionality!".format(port)
                rdprint(defname, msg)
                efprint(msg)

        except Exception as e:
            exceptPrint(e, defname)

        return port

    ### end local def ##########################################################################


    defname = "initSerialPulse: "
    dprint(defname)
    setIndent(1)

    g.Devices["SerialPulse"][g.DNAME] = "SerialPulse"

    timeoutR = 0.1          # sec Read
    timeoutW = 0.1          # sec Write

    # baud rate DOES matter!  make it the highest setting possible!
    # Observation: counts decrease from 5000 to 10 going from baud 921600 to 4800 !!!
    # baud 921600 is present in: CH340, FTDI232RL, CP2102, PL2303
    if g.SerialPulseBaudrate  == "auto": g.SerialPulseBaudrate  = 921600
    if g.SerialPulseUsbport   == "auto": g.SerialPulseUsbport   = findPort(g.SerialPulseBaudrate, timeoutR, timeoutW) # may fail

    if g.SerialPulseUsbport is None:            # findport did not result in finding a port
        return "No Serial Port available"

    # try connecting; but be cautious, the port might have been user defined and may be wrong!
    # rdprint(defname, "connecting to: Port: ", g.SerialPulseUsbport)
    g.SerialPulseSerialConn, errmsg = makeSerialConnection(g.SerialPulseUsbport, g.SerialPulseBaudrate, timeoutR, timeoutW)

    if g.SerialPulseSerialConn is None: return errmsg
    else:                               g.SerialPulseSerialConn.reset_input_buffer()   # clear the buffer

    gdprint(defname, "Successfully opened Serial Connection at Port: {}".format(g.SerialPulseUsbport))
    g.Devices["SerialPulse"][g.CONN] = True

    if g.SerialPulseVariables == "auto": g.SerialPulseVariables = "CPM3rd, CPS3rd" # to not conflict with the GMC-counter variables
    g.SerialPulseVariables     = setLoggableVariables("SerialPulse", g.SerialPulseVariables)

    g.SerialPulseThreadRun     = True
    g.SerialPulseThread        = threading.Thread(target=SerialPulseThreadTarget, args=(None,))
    g.SerialPulseThread.daemon = True   # must come before start: makes threads stop on exit!
    g.SerialPulseThread.start()

    if g.SerialPulseThread.is_alive():
        gdprint(defname, "Thread-status: is alive  - {} successfully initialized".format(g.Devices["SerialPulse"][g.DNAME]))
        errmsg = ""
    else:
        rdprint(defname, "Thread-status: NOT alive - {} FAILED to initialize"    .format(g.Devices["SerialPulse"][g.DNAME]))
        errmsg = "Failure to initialize!"

    setIndent(0)

    return errmsg


def terminateSerialPulse():
    """Stop the thread to monitor the sounddev pulses for clicks"""

    defname ="terminateSerialPulse: "

    dprint(defname)
    setIndent(1)

    dprint(defname + "stopping thread")
    g.SerialPulseThreadRun = False
    g.SerialPulseThread.join()  # "This blocks the calling thread until the thread
                                #  whose join() method is called is terminated."

    # verify that thread has ended, but wait not longer than 5 sec (takes 0.006...0.016 ms)
    start = time.time()
    while g.SerialPulseThread.is_alive() and (time.time() - start) < 5:
        pass

    alivestatus = "is alive" if g.SerialPulseThread.is_alive() else "NOT alive"

    dprint(defname + "thread-status: {} after:{:0.1f} ms".format(alivestatus, 1000 * (time.time() - start)))
    g.Devices["SerialPulse"][g.CONN] = False

    if g.SerialPulseSerialConn is not None:
        try:
            g.SerialPulseSerialConn.reset_input_buffer()
            g.SerialPulseSerialConn.close()
        except Exception as e:
            exceptPrint(e, defname + "reset & close")

        g.SerialPulseSerialConn = None

    g.SerialPulseUsbport = "auto"

    dprint(defname + "Terminated")
    setIndent(0)


def getSerialPulseCounts():
    """Call Serial for waiting bytes, and clear buffer by reading"""
    # dur avg:64µs at CPS=40

    defname = "getSerialPulseCounts: "

    # start = time.time()
    try:
        wcnt = g.SerialPulseSerialConn.in_waiting       # dur avg:44µs
        g.SerialPulseSerialConn.reset_input_buffer()    # dur avg:15µs --> 1 count loss at 67kHz - returns None
    except Exception as e:
        msg = defname + "Serial Connection Problem  "
        exceptPrint(e, msg)
        QueuePrint(msg + str(e))
        wcnt = g.NAN

    # stop = time.time()
    # rdprint(defname, "wcnt: ", wcnt, "  total dur: {:0.3f} ms".format(1000 * (stop - start)))

    return wcnt


def SerialPulseThreadTarget(Dummy):
    """The thread to read the serial input"""

    ################################################################################################

    # CAUTION: Serial buffer appears limited to <= 4095 Bytes !!!
    # #1  CH340C   max buffer is 4095!   Module "DSD TECH SH-U07B" (via Amazon)
    # #2  CH340C   max buffer is 4095!   USB TYP C zu TTL Serial Port (from Ali @USD 1.00)
    #              bad piece: requires almost always a double-start to get a connection !???
    # #3  PL2303TA max buffer is 4095!   (blue device with cable) https://www.amazon.de/dp/B07Z7PPT6Y
    # #4  CP2102   max buffer is 3971!   USB zu TTL Konverter HW-598 (from AZDelivery on Amazon)
    # #5  FT232RL  max buffer is 3969!   (Mini-USB port, AZDelivery, Amazon, https://www.amazon.de/gp/product/B01N9RZK6I/)

    ################################################################################################
    ### check for the max buffer size and duration
    ###     --> all chips show the same performance
    ###                 inwaiting      download 3k bytes
    ### #1  CH340C:     50 ... 70 µs   220 µs
    ### #2  CH340C:     50 ... 58 µs   165 µs   the bad module
    ### #3  PL2303TA:   50 ... 70 µs   210 µs
    ### #4  CP2102:     ~50+ µs        187 µs
    ### #5  FT232RL:    ~50+ µs        201 µs
    ###
    # start = time.time()
    # while True and (time.time() - start) < 1000:
    #     wstart = time.time()
    #     wcnt = g.SerialPulseSerialConn.in_waiting
    #     wstop = time.time()
    #     rdprint(defname, "wcnt: {}  dur: {:0.3f} ms".format(wcnt, 1000 * (wstop - wstart)))
    #     time.sleep(0.1)
    #     if wcnt >= 3000: break
    ###
    # dstart = time.time()
    # brec = g.SerialPulseSerialConn.read(wcnt)
    # dstop  = time.time()
    # mdprint(defname, "wcnt: {}  dur: {:0.3f} ms".format(wcnt, 1000 * (dstop - dstart)))
    ################################################################################################

    defname = "SerialPulseThreadTarget: "

    # clear the serial buffer by resetting
    try:
        g.SerialPulseSerialConn.reset_input_buffer()
    except Exception as e:
        exceptPrint(e, defname + "reset input/output buffer at logging start")

    g.SerialPulseLastCPS    = g.NAN                                             # the last cps value
    g.SerialPulseLast60CPS  = deque([], 60)
    cps_count               = 0
    cps_start               = time.time()

    while g.SerialPulseThreadRun:

        # sleep before calling for serial counts
        # NOTE: buffer is limited to 4095 bytes or less; make sure to read-out before buffer is full!
        #       at high CPS=6000:  in 0.5 sec you get ~3000 counts --> ok
        ts = (0.5 * (1 - (time.time() - cps_start)))
        # rdprint(defname, "sleeping: {:0.3f} ms".format(ts))
        time.sleep(max(0.000001, ts))

        new_counts  = getSerialPulseCounts()
        cps_restart = time.time()

        cps_count  += new_counts
        deltat      = cps_restart - cps_start
        # rdprint(defname, "deltat: ", deltat, "  cps_counts: ", cps_count)

        if deltat >= 1: # sec
            # Laufzeit: avg 41µs
            # Laufzeit: avg 18µs without deltacount

            # start = time.time()

            g.SerialPulseLastCPS = round(cps_count / deltat, 0) # correct for time period duration and round to zero decimals
            g.SerialPulseLast60CPS.append(g.SerialPulseLastCPS) # append to last 60 cps

            if 0: # not really needed?
                deltaCount = cps_count - g.SerialPulseLastCPS
                msg = "after {:0.6f} sec CPS: {:0.0f} corr: {:0.0f}  Delta: {:+0.0f}".format(deltat, cps_count, g.SerialPulseLastCPS, deltaCount)
                if deltaCount != 0: rdprint(defname, msg)

            # reset for next loop
            cps_count        = 0
            cps_start        = cps_restart

            # stop = time.time()
            # mdprint(defname, "g.SerialPulseLastCPS: ", g.SerialPulseLastCPS, "  dur@>1s: {:0.3f} ms".format(1000 * (stop - start)))


def getValuesSerialPulse(varlist):
    """return data for CPM and CPS for each variable CPM* and CPS*"""

    start = time.time()

    defname = "getValuesSerialPulse: "
    alldata = {}

    cps     = g.SerialPulseLastCPS
    if not np.isnan(cps): cpm = getCPMfromCPS(g.SerialPulseLast60CPS)   # code is in gsup_utils.py
    else:                 cpm = g.NAN

    for vname in varlist:
        if   vname in ("CPM", "CPM1st", "CPM2nd", "CPM3rd"):
            cpm = applyValueFormula(vname, cpm, g.ValueScale[vname])    # is vname dependent
            cpm = round(cpm, 0)                                         # round to zero decimals
            alldata.update({vname: cpm})

        elif vname in ("CPS", "CPS1st", "CPS2nd", "CPS3rd"):
            cps = applyValueFormula(vname, cps, g.ValueScale[vname] )   # is vname dependent
            cps = round(cps, 0)                                         # round to zero decimals
            alldata.update({vname: cps})

        else:
            alldata.update({vname: g.NAN})                              # any ambient var becomes NAN

    vprintLoggedValues(defname, varlist, alldata, (time.time() - start) * 1000)

    return alldata


def getInfoSerialPulse(extended = False):
    """Info on settings of the SerialPulse device"""

    defname = "getInfoSerialPulse: "

    SerialPulseInfo  = "Configured Connection:        Port:'{}' Baud:{} \n".format(
                                                                                    g.SerialPulseUsbport,
                                                                                    g.SerialPulseBaudrate
                                                                                  )

    if not g.Devices["SerialPulse"][g.CONN]:
        return SerialPulseInfo + "<red>Device is not connected</red>"

    SerialPulseInfo += "Connected Device:             {}\n".format(g.Devices["SerialPulse"][g.DNAME])
    SerialPulseInfo += "Configured Variables:         {}\n".format(g.SerialPulseVariables)
    SerialPulseInfo += getTubeSensitivities(g.SerialPulseVariables)
    SerialPulseInfo += "\n"

    if extended == True:
        SerialPulseInfo += "No extended info"

    return SerialPulseInfo


################################################################################################################################

    # Testing Performance Part 1
    # USB2Serial: CP2102 Modules USB TO TTL HW-598 (AZDelivery via Amazon)
    # Pulses from OWON DGE2070, NEGATIVE pulse                                                                            CPS
    # Freq             Duty[%]  Width[ms]     Rise[µs]   Fall[µs]    Volt[V]     CPS      %StdDev  CPM         %StdDev    Dev[%]
    #    10.000 00     97.84                  295.312    195.312     3.300       13.885   ±13.4%     831.909    ±2.8%      +39
    #    30.000 00     97.84                  295.312    195.312     3.300       48.561   ±7.3%     2911.755    ±1.1%      +62
    #   100.000 0      97.84    9.784 000     135.000    135.000     3.300       128.541  ±4.3%     7706.625    ±1.4%      +29
    #   300.000 0      97.95    3.265 333      21.666     21.666     3.300       296.063  ±2.4%    17760.348    ±1.0%      -1.3
    #  1000.000        97.95    0.979 500      12.812     12.812     3.300       991.223  ±1.4%    59517.335    ±0.5%      -0.88
    # software change, no printing in getSerialPulseCounts
    #  1000.000        97.95    0.979 500      12.812     12.812     3.300      1001.086  ±0.1%    60064.446    ±0.0%      +0.1
    #   300.000 0      98.98    3.299 376       6.510      6.510     3.300       299.773  ±0.4%    17987.109    ±0.1%      -0.08
    #    30.000 00     98.98   32.993 33       65.104     65.104     3.300        34.966  ±6.8%     2103.020    ±1.1%      +17
    # software change: no reset_input_buffer but read(wcnt) instead
    #    30.000 00     98.98   32.993 33       65.104     65.104     3.300        34.959  ±6.1%     2097.042    ±1.0%      +17
    # pulse change: POSITIVE pulse
    #    30.000 00      0.45   150.000 µs      65.104     65.104     3.300        35.229  ±7.7%     2114.684    ±1.2%      +17
    # pulse change now using rectangle
    #     3.000 000                                                  3.300         3.006  ±2.5%      180.341    ±0.3%      +0.2
    #    30.000 00                                                   3.300        30.016  ±0.6%     1801.145    ±0.1%      +0.05
    #   100.000 0                                                    3.300       100.006  ±0.1%     6000.335    ±0.0%      +0.06
    #   300.000 0                                                    3.300       300.046  ±0.9%    18002.617    ±0.0%      +0.02
    #  1000.000                                                      3.300      1000.043  ±0.8%    60003.396    ±0.0%      +0.004
    #  3000.000                                                      3.300      2999.908  ±0.5%   180011.749    ±0.0%      -0.003
    # 10000.00                                                       3.300      6613.381  ±0.1%   396780.049    ±0.0%      -34!
    # 30000.00                                                       3.300      9878.609  ±0.7%   593632.866    ±0.1%      -67!!
    #     1.000 000                                                  3.300         1.000  ±0.0%       60.000    ±0.0%      +0.00
    #     0.300 000                                                  3.300         0.288  ±157.2%     17.856    ±4.1%      -4


    # Testing Performance Part 2
    # USB2Serial: CP2102 Modules USB TO TTL HW-598 (AZDelivery via Amazon)
    # Pulses from Raspi 5, POSITIVE pulses, length 150 µs, 3.3V pulseamplitude
    # Freq[Hz]         Duty[%]  Width[ms]     Rise[µs]   Fall[µs]    Volt[V]     CPS      %StdDev  CPM         %StdDev    CPS-Dev[%]
    #      0.3         99.9955  3333.3333       ?          ?         3.3            0.301 ±152.3%        7.817 ±6.4%      +0.3
    #      1.0         99.9955  1000.0000       ?          ?         3.3            1.000 ±0.0%         60.000 ±0.0%       0.0
    #      3.0         99.955    333.3333       ?          ?         3.3            3.000 ±0.0%        180.000 ±0.0%       0.0
    #     10.0         99.850    100.0000       ?          ?         3.3           10.016 ±1.2%        601.823 ±0.2%      +0.2
    #     30.0         99.550     33.3333       ?          ?         3.3           30.025 ±0.5%       1800.103 ±0.0%      +0.08
    #    100.0         98.500     10.0000       ?          ?         3.3          100.029 ±0.5%       6001.333 ±0.0%      +0.03
    #    300.0         95.500      3.3333       ?          ?         3.3          300.045 ±0.1%      18002.562 ±0.0%      +0.02
    #   1000.0         85.500      1.0000       ?          ?         3.3         1000.068 ±0.0%      60003.885 ±0.0%      +0.007
    #   3000.0         55.500      0.3333       ?          ?         3.3         3003.167 ±0.3%     180190.244 ±0.0%      +0.1
    #   5000.0         25.000      0.2000       ?          ?         3.3         5000.264 ±0.9%     299993.824 ±0.0%      +0.005
    #   6000.0         10.000      0.1666       ?          ?         3.3         5810.578 ±0.0%     348646.386 ±0.0%      -3.2!


    # Testing Performance Part 3
    # USB2Serial: CH340C Modules "DSD TECH SH-U07B" (via Amazon)
    # Pulses from Raspi 5, NEGATIVE pulses, length 150 µs,  3.3V pulseamplitude
    # Freq[Hz]         Duty[%]  Width[ms]     Rise[µs]   Fall[µs]    Volt[V]     CPS      %StdDev  CPM         %StdDev CPS-Dev[%]
    #      0.3         99.996   3333.333        ?          ?         3.3            0.290 ±156.3%        7.541 ±7.1%      -3.3
    #      1.0         99.985   1000.000        ?          ?         3.3            1.011 ±10.5%        60.953 ±1.3%
    #      3.0         99.955    333.333        ?          ?         3.3            3.000 ±0.0%        180.000 ±0.0%       0.0
    #     10.0         99.850    100.000        ?          ?         3.3           10.030 ±1.7%        604.016 ±0.4%      +0.3
    #     30.0         99.550     33.333        ?          ?         3.3           30.062 ±1.4%       1804.145 ±0.1%      +0.2
    #    100.0         98.500     10.000        ?          ?         3.3          100.033 ±0.8%       6001.311 ±0.0%      +0.03
    #    300.0         95.500      3.333        ?          ?         3.3          300.077 ±0.7%      18003.447 ±0.0%      +0.03
    #   1000.0         85.000      1.000        ?          ?         3.3          998.478 ±1.3%      60033.221 ±0.1%      -0.2
    #   3000.0         55.000      0.333        ?          ?         3.3         3003.346 ±0.5%     180203.468 ±0.0%      +0.1
    #   5000.0         25.000      0.200        ?          ?         3.3         4999.024 ±0.3%     300028.341 ±0.0%      -0.02
    #   6000.0         10.000      0.167        ?          ?         3.3         5987.724 ±0.2%     359262.163 ±0.0%      -0.2


    # Testing Performance Part 4
    # USB2Serial: CH340C TYP C USB zu TTL Serial Port (from Ali @USD 1.00)
    # Pulses from Raspi 5, NEGATIVE pulses, length 150 µs,  3.3V pulseamplitude
    # Freq[Hz]         Duty[%]  Width[ms]     Rise[µs]   Fall[µs]    Volt[V]     CPS      %StdDev  CPM         %StdDev CPS-Dev[%]
    #      0.3         99.996   3333.333        ?          ?         3.3            0.300 ±152.8%       18.290 ±4.9%       0.0
    #      1.0         99.985   1000.000        ?          ?         3.3            1.000 ±0.0%         60.000 ±0.0%       0.0
    #      3.0         99.955    333.333        ?          ?         3.3            3.000 ±0.0%        180.000 ±0.0%       0.0
    #     10.0         99.850    100.000        ?          ?         3.3           10.000 ±0.0%        600.000 ±0.0%       0.0
    #     30.0         99.550     33.333        ?          ?         3.3           30.000 ±0.0%       1800.000 ±0.0%       0.0
    #    100.0         98.500     10.000        ?          ?         3.3          100.059 ±0.5%       6004.788 ±0.0%      +0.06
    #    300.0         95.500      3.333        ?          ?         3.3          300.048 ±0.7%      18002.057 ±0.0%      +0.02
    #   1000.0         85.000      1.000        ?          ?         3.3          999.988 ±0.1%      59995.280 ±0.0       -0.01
    #   3000.0         55.000      0.333        ?          ?         3.3         3003.102 ±0.0%     180186.360 ±0.0%      +0.1
    #   5000.0         25.000      0.200        ?          ?         3.3         4999.461 ±0.1%     299989.080 ±0.0%      -0.01
    #   6000.0         10.000      0.167        ?          ?         3.3         5987.966 ±0.0%     359270.365 ±0.0%      -0.2

