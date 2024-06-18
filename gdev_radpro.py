#! /usr/bin/env python3
# -*- coding: utf-8 -*-

"""
gdev_radpro.py - GeigerLog module to handle devices with the RadPro firmware.
                 see: https://github.com/Gissio/radpro
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

from gsup_utils import *
import gsup_sql


__author__      = "Gissio"               # adapted to GeigerLog by ullix
__copyright__   = "Copyright 2024"
__credits__     = [""]
__license__     = "GPL3"


def initRadPro():
    """Find serial device by USB-manufactuerer and check it for being a RadPro device"""

    defname = "initRadPro: "
    dprint(defname)
    setIndent(1)

    g.RadProHardwareId = None

    if (g.RadProPort == "auto"):
        # check all USB ports and make list of all qualifying
        # Frustratingly, Windows overwrites both product and manufacturer :-(())
        newPortList  = []
        for port in getPortList(symlinks=False):
            rdprint(defname, f"Port Details:  Product: '{port.product}'   Manufacturer: '{port.manufacturer}'")
            if 'win32' in sys.platform:
                ### Windows
                if queryRadPro("GET deviceId", port=port.device) > "":  newPortList.append(port)
            else:
                ### Linux, Mac
                if port.product == "Rad Pro":                           newPortList.append(port)

        ports = [port.device for port in newPortList]
        dprint("List of port devices found: ", ports)

    else:
        ports = [g.RadProPort]
        msg = f"RadPro uses <b>user-configured</b> port: '{g.RadProPort}'"
        dprint(defname, msg)
        fprint(msg)

    # check ports for proper RadPro device response; (yielding HardwareID and other)
    # break on first qualifying port
    for g.RadProPort in ports:
        # rdprint(defname, "port: ", g.RadProPort)
        if checkIDs(): break

    if g.RadProHardwareId is None:
        # did NOT find a RadPro
        g.RadProPort = None
        return "A RadPro device was not detected"

    # found a RadPro device
    dprint(f"Found RadPro device with Hardware Id: '{g.RadProHardwareId}'")

    # mark device as connected and named 'RadPro'
    g.Devices["RadPro"][g.CONN]  = True
    g.Devices["RadPro"][g.DNAME] = "RadPro"

    # configure RadPro
    if g.RadProClockCorrection == "auto":     g.RadProClockCorrection   = 30
    if g.RadProVariables       == "auto":     g.RadProVariables         = "CPM3rd, CPS3rd"
    g.RadProVariables = setLoggableVariables("RadPro", g.RadProVariables)

    # do a clock correction by setting time of counter to that of computer,
    # but only if so configured
    if g.RadProClockCorrection > 0:
        setRadProDateTime(quiet=True)
        g.RadProNextCorrMin = (getMinute() + g.RadProClockCorrection) % 60


    # fill CPS-deque
    g.RadProLast60CPS       = deque([0], 60)                                   # default deque list with single CPS=0
    g.RadProLast60CPSclean  = deque([0], 60)                                   # default deque list with single CPS=0
    lastMin                 = 5                                                # to get last 5 min of rcords
    try:
        Hist, _, _ = getRadProHist(time.time() - (lastMin * 60))
        if len(Hist) <= 2:
            rdprint(defname, f"No Hist data in the last {lastMin} min")
        else:
            sumHistCPS = 0
            counter    = 0
            for i, rec in enumerate(Hist[-lastMin:]):
                # rdprint(defname, "rec: ", rec)
                if i == 0: continue
                hTime       = rec[0]
                hCPM        = rec[1]
                sumHistCPS += hCPM
                counter    += 1

            avgCPM = sumHistCPS / counter
            avgCPS = avgCPM / 60
            if not np.isnan(avgCPS):
                g.RadProLast60CPS      = deque([avgCPS] * 60, 60)    # deque list filled with lastCPS in all 60 places
                g.RadProLast60CPSclean = deque([avgCPS] * 60, 60)    # deque list filled with lastCPS in all 60 places
            dprint(f"Got History for last {lastMin} min with {len(Hist)} records; last one from '{num2datestr(hTime)}', averaging CPM={avgCPM:0.3f} --> CPS={avgCPS:0.3f}")

    except Exception as e:
        exceptPrint(e, defname + "Getting Hist Data for CPS deque")

    # init Threading
    devvars = g.Devices["RadPro"][g.VNAMES]
    for vname in devvars:
        g.RadProValues[vname] = g.NAN                                       # set all configured vars to NAN

    g.RadProThreadRun     = True
    g.RadProThread        = threading.Thread(target=RadProThread_Target, args=["Dummy"]) # auch tuple (args=("Dummy",)) möglich, aber NUR einzelnes Argument!
    g.RadProThread.daemon = True
    g.RadProThread.start()

    # record the clockdrift
    getClockDrift()
    dprint(defname, f"Clockdrift: {g.RadProClockDrift:+0.0f} sec, from: {g.RadProClockDriftFrom}  {g.RadProClockDriftMsg}")

    if g.RadProPWM: # cmd line code: radpropwm
        g.RadProDuties    = list(range(0, 100, 10))
        g.RadProDuties[0] = 1
        rdprint(defname, "Duties to test: ", list(g.RadProDuties))

    setIndent(0)
    return ""


def checkIDs():
    """Check if device responds to command 'GET deviceId' and collect Ids"""

    defname = "checkIDs: "

    qstr = queryRadPro("GET deviceId")
    if qstr > "":
        g.RadProHardwareId, g.RadProSoftwareId, g.RadProDeviceId = qstr.split(";")
        return True
    else:
        return False


def RadProThread_Target(args):
    """The thread to read the variables from the device"""

    defname = "RadProThread_Target: "
    # rdprint(defname, "args: ", args)

    varlist  = g.Devices["RadPro"][g.VNAMES]
    needtime = True
    while g.RadProThreadRun:
        if g.logging:
            if needtime:
                nexttime = time.time()
                needtime = False

            if time.time() >= nexttime:
                fetchValuesRadPro(varlist)      # fetch the values
                nexttime += 1                   # always use 1 sec cycle; everything else gives Nicht-Poisson CPS!

            # clock correction
            if g.RadProClockCorrection > 0 and (getMinute() == g.RadProNextCorrMin):
                setRadProDateTime(quiet=True)
                g.RadProNextCorrMin = (g.RadProNextCorrMin + g.RadProClockCorrection) % 60
                # rdprint(defname, f"CurrentMinute: {getMinute()}  RadProClockCorrection: {g.RadProClockCorrection}  RadProNextCorrMin: {g.RadProNextCorrMin}" )

        else:
            needtime = True

        time.sleep(0.005)


def fetchValuesRadPro(varlist):
    """get all data for vars in varlist for LOCAL storage"""

    ### CPM by RadPro:                  - is now done via formula RADPROCPM()
    ### clock drift                     - is now done via formula RADPROCLOCKDRIFT()
    ### get Hist to obtain its len      - is now done via formula RADPROHISTLEN()

    start   = time.time()
    defname = "fetchValuesRadPro: "


    ### CPS: get from (cumulative) tubePulseCount
    # 1) find the delta-counts
    command                     = "GET tubePulseCount"
    pulsestart                  = time.time()
    try:
        qstr                    = queryRadPro(command)
        if qstr > "": cpsPulseCount = float(qstr)
        else:         cpsPulseCount = g.NAN
    except Exception as e:
        exceptPrint(e, defname + f"Failure with query command: {command}")
        cpsPulseCount = g.NAN
    pulsedur                    = 1000 * (time.time() - pulsestart)
    cpsPulseCountDelta          = cpsPulseCount - g.RadProLastCPSPulseCount
    g.RadProLastCPSPulseCount   = cpsPulseCount

    # 2) find the delta-time
    CPSTime                     = time.time()
    CPSTimeDelta                = CPSTime - g.RadProLastCPSTime     # in sec; ideally should be exactly 1 sec, no decimals
    g.RadProLastCPSTime         = CPSTime

    # 3) finally:
    cpsPC                       = cpsPulseCountDelta / CPSTimeDelta

    ### If LogCycle != 1 a correction is needed because of the cumulative counts from the RadPro
    # cpsPC = cpsPC * g.LogCycle   # This makes 'CPS' to 'Counts-Per-LogCycle-seconds' and is Poissonian only in the latter representation

    ### As mostly CPSTimeDelta != 1 round cps to zero decimals. CAUTION: makes the value Non-Poissonian!
    cpsPC      = round(cpsPC, 0)
    cpsPCclean = cpsPC

    if cpsPC != cpsPulseCountDelta:
        cpsPCclean = g.NAN           # if pulse count needs correction then ignore this value!

    cpsPCclean = round(cpsPCclean, 0)

    # ### CPM:  get GeigerLog's CPM by summing last 60 cpsPC
    # if not np.isnan(cpsPC): g.RadProLast60CPS.append(cpsPC)
    # CPMbySum = sum(g.RadProLast60CPS)

    ### use only for Poissonian values
    if not np.isnan(cpsPCclean): g.RadProLast60CPSclean.append(cpsPCclean)
    CPMbySumclean = round(sum(g.RadProLast60CPSclean), 0)

    # fill RadProValues
    for vname in varlist:
        if   vname == "CPM":        val = CPMbySumclean
        elif vname == "CPS":        val = cpsPCclean
        elif vname == "CPM1st":     val = CPMbySumclean
        elif vname == "CPS1st":     val = cpsPCclean
        elif vname == "CPM2nd":     val = CPMbySumclean
        elif vname == "CPS2nd":     val = cpsPCclean
        elif vname == "CPM3rd":     val = CPMbySumclean
        elif vname == "CPS3rd":     val = cpsPCclean

        elif vname == "Temp":       val = g.NAN
        elif vname == "Press":      val = g.NAN
        elif vname == "Humid":      val = g.NAN
        elif vname == "Xtra":       val = g.NAN

        else:                       val = g.NAN

        g.RadProValues[vname] = val                                     # holds all data locally

### Experimental - for testing PWM setting on HV
    if g.RadProPWM:
        # set new Config for HV
        if g.LogReadings % 10 == 0:
            duty = round(g.RadProDuties[g.RadProDindex] / 100, 2)
            setRadProConfig(g.RadProFrequency, duty)
            g.RadProDindex += 1
            if g.RadProDindex >= 10: g.RadProDindex = 0

    vprintLoggedValues(defname, varlist, g.RadProValues, (time.time() - start) * 1000)


def terminateRadPro():
    """Close device"""

    defname = "terminateRadPro: "
    dprint(defname)
    setIndent(1)

    errmsg = ""
    g.Devices["RadPro"][g.CONN] = False

    dprint(defname, "Terminated")
    setIndent(0)

    return errmsg


def queryRadPro(request, port="default"):
    """Query the RadPro device with a command 'request'"""
    # return: str of scrubbed, downloaded byte-data; empty str on failure

    ### local defs
    def verifyData(DataStr):
        """Check the data for validity, and return:
        on ok:  cleaned data (without ok at Start and LF at end)
        else:   empty string ("")
        """

        if g.devel: printQueryDetails(DataStr)

        if DataStr     == "":           return ("",                  f"Bad data - Empty DataStr: '{DataStr}'")       # empty DataStr
        if DataStr[-1] != "\n":         return ("",                  f"Bad data - No LF ending:  '{DataStr[-50:]}'") # no LF ending
        if DataStr.startswith("OK"):    return (DataStr.strip()[3:], f"Good Data: '{DataStr}'")                      # skip the initial "OK "
        else:                           return ("",                  f"Bad data - No initial OK:  '{DataStr[:50]}'") # missing initial OK


    def printQueryDetails(DataStr):
        """print some query details on size, dur, speed"""

        lendata = len(DataStr)
        tdur    = 1000 * (time.time() - tstart)
        wspeed  = g.NAN if wdur == 0 else wcnt    / wdur
        rspeed  = g.NAN if rdur == 0 else lendata / rdur
        tspeed  = g.NAN if tdur == 0 else lendata / tdur
        plimit  = 45    # print-length limit
        breclim = brec[:plimit] + (b"..." if len(brec) > plimit else b"")
        msg     = f"cmd: {request:20s}  Byte:W:{wcnt} R:{lendata}  Dur[ms]:W:{wdur:0.2f} R:{rdur:0.1f} Ttl:{tdur:0.1f}  "
        msg    += f"Speed[kB/s]:W:{wspeed:5.1f} R:{rspeed:5.1f} Ttl:{tspeed:5.1f}  response:{breclim}"
        mdprint(defname, msg)
    ### end local defs


    tstart   = time.time()
    defname  = "queryRadPro: "
    # mdprint(defname, f"request: '{request}' ")

    response = ""   # default response on failure

    # to avoid exceptions from multiple serial accesses
    if g.RadProSerialBlocking: return response

    if port == "default":  port = g.RadProPort
    # rdprint(defname, "port: ", port, "   ", type(port))

    try:
        ### using serial port with context manager ######################################################################
        g.RadProSerialBlocking = True
        # with serial.Serial( port          = g.RadProPort,
        with serial.Serial( port          = port,
                            baudrate      = g.RadProBaud,
                            timeout       = g.RadProTimeoutRHist,
                            write_timeout = g.RadProTimeoutW,
                            ) as RPser:
        # write
            try:
                wstart   = time.time()
                wcnt     = g.NAN
                brequest = (request + "\n").encode("ascii", errors='replace')       # are there ever errors on encoding?
                wcnt     = RPser.write(brequest)                                    # wcnt= no of Bytes written
            except serial.SerialTimeoutException as e:                              # this exception ONLY on WRITE timeout !
                exceptPrint(e, defname + f"FAILURE Timeout on WRITING; request: '{request}'")
            except Exception as e:
                exceptPrint(e, defname + f"FAILURE writing to serial; request: '{request}'")
            wdur = 1000 * (time.time() - wstart)                                    # in ms


        # wait for data in the pipeline but wait no longer than 5 sec - takes 0 ... 3 ms
            beginwait = time.time()
            dtime = 0
            while RPser.in_waiting == 0:
                dtime = time.time() - beginwait
                if (dtime) > 5:
                    rdprint(defname, f"Waited: {dtime:0.3f} sec")
                    setIndent(0)
                    return response
            # rdprint(defname, f"Waited: {1000 * dtime:0.3f} ms")


        # read
            rstart = time.time()
            try:
                brec = RPser.readline()  # waits for LF; timeoutR when no LF received, but download Hist takes > 2 sec, yet works?
            except Exception as e:
                exceptPrint(e, defname + f"FAILURE reading serial request: '{request}'")
                brec     = b""
            rdur = 1000 * (time.time() - rstart)                                    # in ms
        ### serial port is now CLOSED again ####################################################################################

    except Exception as e:
        emsg = f"FAILURE writing/reading serial request: '{request}'"
        exceptPrint(e, defname + emsg)
        QueuePrint("RadPro Failure: " + str(e))

    else:
        # rdprint(defname, "brec: ", brec)
        if rdur >= g.RadProTimeoutRHist * 1000:                           # timeout R; brec kann trotzdem ok sein, siehe datalog!
            rdprint(defname, f"requ:'{request}' --- EXCEEDED READ-TIMEOUT --- dur: {rdur:0.3f} ms")

        response, _ = verifyData(brec.decode("ascii", errors='replace'))  # with errors='replace' no further exception possible(?)

    finally:
        g.RadProSerialBlocking = False

    # rdprint(defname, f"returning: '{response}'")

    return response     # response is type str


def getClockDrift():
    """check the Device Clock Drift"""

    if not g.logging:
        g.RadProClockDrift     = getRadProDeltaTime()
        g.RadProClockDriftFrom = num2datestr(time.time())

    if   np.isnan(g.RadProClockDrift):
                                       msg = f"<red>Device Clock cannot be read"
                                       QueueSoundDVL("burp")
    elif abs(g.RadProClockDrift) <= 1: msg = f"Device Clock is same as Computer's within 1 sec"
    elif     g.RadProClockDrift  >  1: msg = f"Device Clock is slower than Computer's by {abs(g.RadProClockDrift):0.0f} sec"
    else:                              msg = f"Device Clock is faster than Computer's by {abs(g.RadProClockDrift):0.0f} sec"

    g.RadProClockDriftMsg = msg


def getInfoRadPro(extended=False):
    """Return RadPro info"""

    ### Factory Default PWM setting
    # Tube HV PWM frequency:        9207.16 Hz
    # Tube HV PWM duty cycle:       75.0 %      --> 650V - bei Abdunkelung; starke Lichtempfindlichkeit

    # Tube HV PWM frequency:        1250 Hz
    # Tube HV PWM duty cycle:       11.0 %      --> 330V - keine Lichtempfindlichkeit beobachtet

    # Tube HV PWM frequency:        5000 Hz
    # Tube HV PWM duty cycle:       11.0 %      --> 235V - nicht getestet

    # Tube HV PWM frequency:        5000 Hz
    # Tube HV PWM duty cycle:       20.0 %      --> 347V - nicht getestet

    # Tube HV PWM frequency:        5000 Hz
    # Tube HV PWM duty cycle:       25.5 %      --> 405V - Lichtempfindlich

    # Tube HV PWM frequency:        5000 Hz
    # Tube HV PWM duty cycle:       23.0 %      --> 385V - bei Tageslicht nichts sichtbar, mit Laser 405nm starke Reaktion

    # Tube HV PWM frequency:        5000 Hz
    # Tube HV PWM duty cycle:       29.0 %      --> 450V - bei Tageslicht erhöhter Background 30+  statt 20-

    # Tube HV PWM frequency:        5000 Hz
    # Tube HV PWM duty cycle:       24.25 %     --> 395V - bei Tageslicht nichts sichtbar, mit Laser 405nm starke Reaktion



    defname = "getInfoRadPro: "

    info = ""
    if g.RadProHardwareId is not None:
        info += "Configured Connection:        Port:'{}' Baud:{} Timeouts[s]: R:{} W:{}\n".format(
                                                                                                    g.RadProPort,
                                                                                                    g.RadProBaud,
                                                                                                    g.RadProTimeoutR,
                                                                                                    g.RadProTimeoutW,
                                                                                                 )

    if not g.Devices["RadPro"][g.CONN]:
        info += "<red>Device not connected.</red>\n"
    else:
        getClockDrift()
        rdprint(defname, f"Clockdrift: {g.RadProClockDrift:+0.0f} sec, checked @ Comp.Time: {g.RadProClockDriftFrom}  {g.RadProClockDriftMsg}")

        info += "Device is connected\n"
        info += "Hardware ID:                  {}\n".format(g.RadProHardwareId)

        if extended: getClockDrift()
        info += "Device Clock Drift:           {:0.0f} sec  (checked @ Comp.Time: {})\n".format(g.RadProClockDrift, g.RadProClockDriftFrom)
        info += "                              {}\n".format(g.RadProClockDriftMsg)
        info += "\n"

        if extended:
            try:
                try:
                    dtimestmp = int(queryRadPro("GET deviceTime"))     # convert to int from str
                except Exception as e:
                    exceptPrint(e, "no dtimestmp")
                    dtimestmp = g.NAN

                info += f"Device Time:                  {num2datestr(dtimestmp)}  timestamp: {dtimestmp}\n"
                info += f"Software ID                   {g.RadProSoftwareId}\n"
                info += f"Device ID:                    {g.RadProDeviceId}\n"
                info += f"Device Battery Voltage:       {queryRadPro('GET deviceBatteryVoltage')} V\n"
                info += f"Tube life time:               {queryRadPro('GET tubeTime')}\n"
                info += f"Tube life pulse count:        {queryRadPro('GET tubePulseCount')}\n"
                info += f"Tube rate:                    {queryRadPro('GET tubeRate')} CPM\n"
                info += f"Tube conversion factor:       {queryRadPro('GET tubeConversionFactor')} CPM/(µSv/h)\n"
                info += f"Tube dead time:               {queryRadPro('GET tubeDeadTime')} s\n"
                info += f"Tube dead-time compensation:  {queryRadPro('GET tubeDeadTimeCompensation')} s\n"
                info += f"Tube background compensation: {queryRadPro('GET tubeBackgroundCompensation')} CPM\n"
                info += f"Tube HV PWM frequency:        {queryRadPro('GET tubeHVFrequency')} Hz\n"
                info += f"Tube HV PWM duty cycle:       {100 * float(queryRadPro('GET tubeHVDutyCycle'))} %\n"
            except Exception as e:
                msg   = "Failure getting Extended Info"
                info += msg
                exceptPrint(e, defname + msg)

    return info + "\n"


def getRadProCPM():
    """get CPM from RadPro's command 'GET tubeRate'"""

    defname = "getRadProCPM: "

    try:
        qstr = queryRadPro("GET tubeRate")
        if qstr > "":   cpmTR = float(qstr)                             # will except when qstr == ""
        else:           cpmTR = g.NAN
    except Exception as e:
        exceptPrint(e, defname)
        cpmTR = g.NAN

    # mdprint(defname, "CPM: ", cpmTR)

    return cpmTR


def getValuesRadPro(varlist):
    """Read data from the locally held vars; set them to NAN after readout"""

    start   = time.time()
    defname = "getValuesRadPro: "
    alldata = {}
    # rdprint(defname, "g.RadProValues: ", g.RadProValues)
    for vname in varlist:
        if vname in g.RadProValues.keys():
            alldata[vname]        = applyValueFormula(vname, g.RadProValues[vname], g.ValueScale[vname])
            g.RadProValues[vname] = g.NAN   # reset g.RadProValues to NAN after reading

    vprintLoggedValues(defname, varlist, alldata, (time.time() - start) * 1000)

    return alldata


def loadHistoryRadPro(sourceHist):
    """Load history from device"""

    start = time.time()

    defname = "loadHistoryRadPro: "

    fprint("Loading data from source {sourceHist} ...")
    QtUpdate()

    # get Hist as list
    Hist, bytecount, _ = getRadProHist(0)

    # save data to database
    historyDB = []
    for i, HisRecord in enumerate(Hist):
        # rdprint(defname, "HisRecord: ", HisRecord)    # loadHistoryRadPro: HisRecord: [1713345208, 1263.0, 60,         1263]
                                                        # loadHistoryRadPro: HisRecord: [1713345268, 1221.0, 60,         1221]
                                                        # loadHistoryRadPro: HisRecord: [1713345328, 1233.0, 60,         1233]
                                                        # HistData.append(             [record_time, cpm,    delta_time, delta_pulse_count])
                                                        #                                                    between     pulse delta betw.
                                                        #                                                    2 records   2 records
                                                        #                                                                same as CPM
                                                        #                                                                if dt==60

        historyDB.append(
            [i,
             num2datestr(HisRecord[0]), # DateTime str

             HisRecord[1],              # CPM:  counts per min
             None,
             None,
             None,

             None,
             None,
             None,
             None,

             HisRecord[2],              # Temp: delta_time to previous record in sec
             None,
             None,
             None,
            ]
        )

    # updating database - SQL Device
    gsup_sql.DB_insertDevice(g.hisConn, stime(), str(g.RadProHardwareId))

    # updating database -  SQL Comments
    gsup_sql.DB_insertComments(g.hisConn, [
                                            ["HEADER",  None, "File created by reading history from device"],
                                            ["ORIGIN",  None, "Download from device"],
                                            ["DEVICE",  None, str(g.RadProHardwareId)],
                                            ["COMMENT", None, "CPM: Counts per 1 min; Temp: Delta t[sec] to prev. record"],
                                          ])

    # updating database - SQL Data
    gsup_sql.DB_insertData(g.hisConn, historyDB)

    lenhist  = len(historyDB)                   # no of records
    duration = time.time() - start              # sec
    rec_rate = lenhist   / duration             # records / sec
    byterate = bytecount / duration / 1000      # kilobytes / sec
    msg      = "Done. Got {} records in {:0.1f} s;  {:0.0f} rec/s  ({:0.1f} kB/s)".format(lenhist, duration, rec_rate, byterate)
    dprint(defname, msg)
    fprint(msg)

    return (0, "")


def getRadProHist(startTime):
    """Download History from Counter"""
    # return: - List of Hist records
    #         - count of downloaded bytes
    #         - duration of full processing

    # - high count rates
    # - run: /RadPro-Hist-Len check_#2.logdb
    #    143, 2024-04-11 18:19:57,  2367.000
    #    144, 2024-04-11 18:20:00,  1861.000  delta = 506   /8 = 63.25
    #
    #      9, 2024-04-11 18:19:57,  2367.000
    #     10, 2024-04-11 18:20:00,  1861.000  delta = 506

    #     18, 2024-04-12 10:52:21,  2339.000  delta = 506
    #     19, 2024-04-12 10:52:24,  1833.000

    # - at Background count rates
    # - run: Using GMC-300E+ & FNIRSI GC-01 on Background get Hist-Len.logdb
    #      7, 2024-04-13 10:11:20,  2861.000  delta = 490 /8 = 61.25
    #      8, 2024-04-13 10:11:23,  2371.000

    #     11, 2024-04-13 17:38:39,  2696.000  delta = 502 /8 = 62.75
    #     12, 2024-04-13 17:38:42,  2194.000

    #     21, 2024-04-14 02:29:53,  2679.000  delta = 482
    #     22, 2024-04-14 02:29:56,  2197.000

    #     74, 2024-04-14 19:16:29,  2693.000  delta = 924 /8 = 115.5
    #     75, 2024-04-14 19:16:32,  1769.000

    #      4, 2024-04-15 09:52:50,  2627.000  delta = 457
    #      5, 2024-04-15 09:52:53,  2170.000

    #     63, 2024-04-15 19:04:39,  2675.000  delta = 325
    #     64, 2024-04-15 19:04:42,  2350.000

    #      2, 2024-04-18 16:21:01,  3320.000  delta = 859
    #      3, 2024-04-18 16:21:05,  2461.000

    #     33, 2024-04-19 08:50:18,  3444.000  delta = 504
    #     34, 2024-04-19 08:50:22,  2940.000

    #      2, 2024-04-20 13:22:34,  3295.000  delta = 725
    #      3, 2024-04-20 13:22:38,  2570.000

    #      2, 2024-04-20 22:12:23,  3044.000  delta = 899
    #      3, 2024-04-20 22:12:27,  2145.000

    #     13, 2024-04-21 06:35:23,  2647.000  delta = 984
    #     14, 2024-04-21 06:35:27,  1663.000

    #      9, 2024-04-22 12:21:20,  1866.000  delta = 506 (10 sec storage)
    #     10, 2024-04-22 12:21:24,  1360.000

    #      5, 2024-04-22 13:38:52,  1822.000  delta = 506 (10 sec storage)
    #      6, 2024-04-22 13:38:56,  1316.000

    # Quote: "Data logging can store up to 5060 data points. At normal radiation levels, this allows for
    #         3 days of data at 1-minute intervals, 8 days at 5-minute intervals, 17 days at 10-minute
    #         intervals, 52 days at 30-minute intervals, and 105 days at 60-minute intervals."

    ####
    def printRecordInfo():
        # print only first, last records, and those different from delta_time==60

        global sixty, sixtyplus, sixtyminus, sixtyall

        if    delta_time == 60:     sixty        += 1
        elif  np.isnan(delta_time): pass
        elif  delta_time >  60:     sixtyplus    += 1
        else:                       sixtyminus   += 1
        sixtyall = sixty + sixtyplus + sixtyminus
        sixtypct = sixtyplus / sixtyall if sixtyall > 0 else g.NAN

        ilimit      = 11
        conditionLo = index < ilimit                            # first and last ilimit records
        conditionHi = index > (len(records) - ilimit)           # first and last ilimit records
        conditionM  = False #delta_time != 60                          # records where deltaTime is not == 60
        if conditionLo or conditionHi or conditionM:
            msg  = f"index:{index:4d}  time:{record_time:10d} {num2datestr(record_time):19s}  pulse_count:{record_pulse_count:7d}  "
            msg += f"delta_time:{delta_time:4.0f}  delta_pulse_count:{delta_pulse_count:<4.0f}  "
            msg += f". sixty:{sixty:<5.0f}  >:{sixtyplus:<4.0f} {sixtypct:<4.0%}   <:{sixtyminus:<3.0f}  . CPM:{cpm}"
            if index == (len(records) - ilimit + 1): print()
            if conditionLo or conditionHi:  cdprint(defname, msg)
            else:                           mdprint(defname, msg)
    ####

    global sixty, sixtyplus, sixtyminus, sixtyall

    defname = "getRadProHist: "

    sixty               = 0
    sixtyplus           = 0
    sixtyminus          = 0
    sixtyall            = 0

    # get records since "startTime" - set startTime==0 to fetch all records
    Hstart  = time.time()
    qstr    = queryRadPro(f"GET datalog {int(startTime)}")          # must NOT have decimals in starttime!
    Hdur1   = 1000 * (time.time() - Hstart)                         # Got 3036 records in 3.1 s;  967 rec/s  (19.4 kB/s)

    records = qstr.split(";")                                       # recs like: '1713200682,12713637;' format: (timestamp, cum-count)
    cdprint(defname, f"Total no of records: {len(records) - 1} (+ 1 for header)", )


    # parse the records and create list of HistData records
    last_time           = g.NAN
    last_pulse_count    = g.NAN
    HistData            = []
    for index, record in enumerate(records):
        if index == 0:                                                  # skipping the header line: 'time,tubePulseCount;'
            cdprint(defname, f"index:{index:4d}  header: '{record}'")
            continue

        values = record.split(",")                                      # 'values' are strings!
        if len(values) != 2:
            rdprint(defname, f"Record '{record}' malformed (too many commas)")
            continue

        try:
            record_time         = int(values[0])                            # unix time stamp
            record_pulse_count  = int(values[1])                            # cumulative counts

            delta_time          = record_time        - last_time            # in sec
            delta_pulse_count   = record_pulse_count - last_pulse_count     # in counts

            last_time           = record_time
            last_pulse_count    = record_pulse_count

            cpm = round(delta_pulse_count / delta_time * 60, 0)             # to correct for delta_time != 60; kills Poissonian!
            if g.devel: printRecordInfo()

            # HistData.append([record_time, cpm])
            HistData.append([record_time, cpm, delta_time, delta_pulse_count])

        except Exception as e:
            exceptPrint(e, defname + "Error while parsing records")

    Hdur2 = 1000 * (time.time() - Hstart)                               # 20 ... 30 ms länger als Hdur1
    cdprint(defname, f"Hist: get Dur:{Hdur1:0.1f} ms  processing: plus:{Hdur2 - Hdur1:0.1f} ms")

    return (HistData, len(qstr), (Hdur1, Hdur2))


def getRadProDeltaTime():
    """
    reads the timestamp from device and computer
    return: on success: delta time 'Computer minus Device' in sec with 1 sec resolution
            on failure: NAN
    """

    defname = "getRadProDeltaTime: "

    dtimestamp = queryRadPro("GET deviceTime")
    # rdprint(defname, f"devtimestmp: '{dtimestamp}'")

    try:
        time_computer = int(time.time())
        if dtimestamp > "": time_device   = int(dtimestamp)
        else:               time_device   = g.NAN
    except Exception as e:
        exceptPrint(e, defname + f"FAILURE getting timestamps; computer: '{time_computer}'  RadPro: '{dtimestamp}'")
        time_device = g.NAN

    time_delta = time_computer - time_device
    # gdprint(defname, f"Clock: computer:{time_computer}, device:{time_device}, Delta CD:{time_delta:+0.3f}"

    return time_delta


def setRadProDateTime(quiet=False):

    defname = "setRadProDateTime: "

    msg = "Setting RadPro Datetime to Computer DateTime"
    dprint(defname, msg)
    if not quiet:
        fprint(header("Set RadPro DateTime"))
        fprint(msg)

    ctime = int(time.time())                                         # cut off the decimals from time.time() by int()
    queryRadPro(f"SET deviceTime {ctime}")


def getRadProDuty():
    """get the Duty Cycle in %"""

    defname = "getRadProDuty: "

    hvdc = queryRadPro('GET tubeHVDutyCycle')
    try:
        fhvdc = float(hvdc)
    except Exception as e:
        exceptPrint(e, defname)
        fhvdc = g.NAN

    return fhvdc


def getRadProFreq():
    """get the Freq in Hz"""

    defname = "getRadProFreq: "

    hvfreq = queryRadPro('GET tubeHVFrequency')
    try:
        fhvfreq = float(hvfreq)
    except Exception as e:
        exceptPrint(e, defname)
        fhvfreq = g.NAN

    return fhvfreq


def editRadProConfig():
    """Enter values for Freqency and Duty Cycle"""

    defname = "editRadProConfig: "

    dprint(defname)
    setIndent(1)

    fbox = QFormLayout()
    fbox.setFieldGrowthPolicy (QFormLayout.AllNonFixedFieldsGrow)
    fbox.addRow(QLabel("<span style='font-weight:900;'>PWM Settings:</span>"))


    # SET tubeHVFrequency [value]\r\n:
    #   Enables the custom HV profile and sets its PWM frequency, provided in decimal format.
    #   Valid values are 1250, 2500, 5000, 10000, 20000, 40000.
    Qfreq = QComboBox()
    Qfreq.addItems(["1250", "2500", "5000", "10000", "20000", "40000"])
    Qfreq.setToolTip("The PWM Frequency of the HV Generator")
    Qfreq.setCurrentText(str(g.RadProFrequency))
    fbox.addRow(QLabel("Frequency [Hz]"), Qfreq)

    # SET tubeHVDutyCycle [value]\r\n:
    #   Enables the custom HV profile and sets its PWM duty-cycle, provided in decimal format.
    #   Valid values are 0.0025 to 0.9, in 0.0025 steps.
    dutyitems = []
    for i in range(25, 9001, 25):                                     # 0.0025 to 0.9, in 0.0025 steps.
        dutyitems.append(f"{i / 100:0.2f}%")
    # print(dutyitems)

    Qduty = QComboBox()
    Qduty.addItems(dutyitems)
    Qduty.setToolTip("The PWM Duty Cycle of the HV Generator")
    ctext = f"{g.RadProDutyCycle:0.2f}%"
    # rdprint(defname, f"ctext: '{ctext}'")
    Qduty.setCurrentText(ctext)
    fbox.addRow(QLabel("Duty Cycle [%]"), Qduty)


    # Dialog box
    d = QDialog()
    d.setWindowIcon(g.iconGeigerLog)
    d.setFont(g.fontstd)
    d.setWindowTitle("Enter Configuration Values")
    d.setWindowModality(Qt.WindowModal)
    d.setMinimumWidth(250)

    # Buttons
    bbox = QDialogButtonBox()
    bbox.setStandardButtons(QDialogButtonBox.Cancel | QDialogButtonBox.Ok )
    bbox.accepted.connect(lambda: d.done(1))
    bbox.rejected.connect(lambda: d.done(-1))

    layoutV = QVBoxLayout(d)
    layoutV.addLayout(fbox)
    layoutV.addWidget(bbox)

    retval = d.exec()
    #print("reval:", retval)

    if retval != 1:
        # ESCAPE key or Cancel Button pressed
        dprint(defname + "Canceling; no changes made")

    else:
        # OK pressed
        fprint(header("RadPro Device PWM Configuration"))
        try:
            tQfreq = Qfreq.currentText()
            tQduty = Qduty.currentText()

            fval = int(tQfreq)
            dval = float(tQduty.replace("%", "")) / 100
        except Exception as e:
            msg = "Converting Text Entries to Numbers"
            exceptPrint(e, defname + msg)
            qefprint("FAILURE " + msg)
            efprint(f"You've entered:  Freq: {tQfreq}  Duty: {tQduty}")
            fval = g.NAN
            dval = g.NAN

        fprint(f"{'Frequency:':30s}{fval} Hz")
        fprint(f"{'Duty Cycle:':30s}{dval * 100:0.2f} %")

        dprint(defname, "PWM Frequency [Hz]: ", fval)
        dprint(defname, "PWM Duty Cycle[%]:  ", dval)

        setRadProConfig(fval, dval)

    setIndent(0)


def setRadProConfig(freq, duty):

    if g.RadProHardwareId is None: return g.NAN

    defname = "setRadProConfig: "
    rdprint(defname, f"Setting: freq: {freq:0.0f}  duty: {duty:0.2f}")
    QueuePrintDVL(f"Setting: freq: {freq:0.0f} Hz  duty: {duty * 100:5.2f}%")

    qstr = queryRadPro(f"{'SET tubeHVDutyCycle {duty}'}")       # qstr is always ""
    qstr = queryRadPro(f"{'SET tubeHVFrequency {freq}'}")

    # too fast ???
    # time.sleep(0.1) # not helping
    # time.sleep(0.2) # not helping

    rd = getRadProDuty()
    rf = getRadProFreq()
    rdprint(defname, f"Found:   freq: {rf:0.0f}  duty: {rd:0.2f}")

