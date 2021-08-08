#! /usr/bin/env python3
# -*- coding: UTF-8 -*-

"""
AmbioMon++ - calling AmbioMon++ running on ESP32
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

from   gsup_utils           import *
import gsup_sql                             # database handling


###############################################################################
# used only internally within gdev_ambiomon.py

def _getAmbioUrl():
    # Port is always 80
    return "http://{}".format(gglobs.AmbioServerIP)


def _getAmbioDevice():
    # get the device like 'ESP32-WROOM-Dev' by calling page '/amID' yielding:
    #   2020-06-02 09:39:01, ESP32-WROOM-Dev, 10.0.0.85, ambiomon.local, 3

    try:
        url   = _getAmbioUrl() + "/amid"
        page  = urllib.request.urlopen(url, timeout=gglobs.AmbioTimeout)
        data  = page.read().decode("UTF-8").split(",")
    except Exception as e:
        edprint("Failed _getAmbioDevice at url:'{}' with Exception: ".format(url), e, debug=True)
        efprint ("{} Getting AmbioMon Device Identifier @ url:<br>'{}' failed with exception:<br>{}".format(stime(), url, cleanHTML(e)))
        return "NONE"

    return data[1].strip()


def _convertUnixtimeToDateTime(unixtime):
    """convert a Unix time in sec into datetime like: 2020-05-10 11:48:50"""

    return datetime.datetime.utcfromtimestamp(unixtime).strftime('%Y-%m-%d %H:%M:%S')


def _printException(e, rec):
    dprint  ("Exception _parseValueAdder: ", e)
    efprint ("AmbioMon History Download had error: ", cleanHTML(e))
    qefprint("Record is ignored, has Error: ", rec)
    dprint  ("Record is ignored, has Error: ", rec)


def _parseValueAdderCPS(i, rec):
    """Add the parse results to the *.his list"""

    # create the data for the database; datalist covers:
    # Index, DateTime, <modifier>,  CPM, CPS, CPM1st, CPS1st, CPM2nd, CPS2nd,  CPM3rd, CPS3rd, Temp, Press, Humid, X
    # 0      1         2            3    4    5       6       7        8       9       10      11    12     13     14

    #~ print("_parseValueAdder: i, rec:", i, rec)
    try:
        reclist      = rec.split(",", 5)        #
        datalist     = [None] * (gglobs.datacolsDefault + 2)   # (13 + 2)=15 x None
        datalist[0]  = i                        # byte index
        datalist[1]  = reclist[0]               # DateTime UTC
        datalist[2]  = "0 hours"                # the modifier for julianday; here: no modification
        datalist[4]  = reclist[1]               # cps

        datalist[9]  = reclist[2]               # selector
        datalist[10] = reclist[3]               # volt

        gglobs.HistoryDataList.append (datalist)

    except Exception as e:
        _printException(e, rec)


def _parseValueAdderCAM(i, rec):
    """Add the parse results to the *.his list"""

    # create the data for the database; datalist covers:
    # Index, DateTime, <modifier>,  CPM, CPS, CPM1st, CPS1st, CPM2nd, CPS2nd,  CPM3rd, CPS3rd, Temp, Press, Humid, X
    # 0      1         2            3    4    5       6       7        8       9       10      11    12     13     14

    #~ print("_parseValueAdder: i, rec:", i, rec)
    try:
        reclist      = rec.split(",", 9)    # results in datetime + 6 values + 1 extra for the rest
        datalist     = [None] * (gglobs.datacolsDefault + 2)   # (13 + 2)=15 x None
        datalist[0]  = i                    # byte index
        datalist[1]  = reclist[0]           # DateTime UTC
        datalist[2]  = "0 hours"            # the modifier for julianday; here: no modification
        datalist[3]  = reclist[1]           # cpm

        datalist[9]  = reclist[6]           # selector
        datalist[10] = reclist[7]           # volt

        datalist[11] = reclist[2]           # temp
        datalist[12] = reclist[3]           # pressure
        datalist[13] = reclist[4]           # humidity
        datalist[14] = reclist[5]           # air quality

        gglobs.HistoryDataList.append (datalist)

    except Exception as e:
        _printException(e, rec)


# gdev_ambiomon.py use only
###############################################################################


###############################################################################
# Public Functions


def makeAmbioHistory(source, device):  # source == "AMDeviceCAM" or "AMDeviceCPS"
    """read the history from an AmbioMon device"""

    fncname = "makeAmbioHistory: "

    if not gglobs.AmbioActivation:
        emsg = "AmbioMon device is not activated"
        dprint(fncname + emsg)
        return -1, emsg

    dprint(fncname + "from source: '{}' using device: '{}'".format(source, device))
    dprint(fncname + "gglobs.AMFilePath: {}".format(gglobs.AMFilePath))
    setDebugIndent(1)

    error           = 0         # default: no error
    message         = ""        # default: no message

    start = time.time()

    if   source == "AMDeviceCPS" or source == "AMDeviceCAM":
    # get data from AmbioMon device

        if not gglobs.AmbioConnection:
            emsg = "AmbioMon device is not connected"
            dprint(fncname + emsg)
            return -1, emsg

        if   source == "AMDeviceCPS": url = _getAmbioUrl() + "/log.cps"
        elif source == "AMDeviceCAM": url = _getAmbioUrl() + "/log.cam"
        fprint("Using URL: ", url)

        try:
            page        = urllib.request.urlopen(url, timeout=10)
            devicedata  = page.read()   # type(devicedata) = <class 'byte'>
        except Exception as e:
            dprint("Failed urlib: Exception: ", e, debug=True)
            playWav("error")
            efprint("{} Reading data from Web failed with exception:<br>{}".format(stime(), cleanHTML(e)))
            setDebugIndent(0)
            Qt_update()
            return -1, cleanHTML(e)

    elif source == "AMFileCPS" or source == "AMFileCAM":
    # get data from AmbioMon File
        try:
            devicedata = readBinaryFile(gglobs.AMFilePath)
        except Exception as e:
            playWav("error")
            efprint("{} Reading data from File failed with exception:<br>{}".format(stime(), cleanHTML(e)))
            setDebugIndent(0)
            Qt_update()
            return -1, cleanHTML(e)

    stop       = time.time()

    dtime      = (stop - start)
    lendevicedata = len(devicedata)
    msg        = "Downloaded {:0.1f} kB from {} in {:0.1f} milliseconds ({:0.1f} kB/s)".format(lendevicedata / 1000, source, dtime * 1000, lendevicedata/dtime/1000)
    vprint(msg)
    fprint(msg)
    fprint("Processing data ...")
    Qt_update()

    data_originDB   = (stime(), gglobs.AmbioDeviceDetected)
    dbheader        = "File created by reading log from device"
    dborigin        = "Download from device"
    dbdevice        = "{}".format(data_originDB[1])

    dumpdata = []
    if   source == "AMDeviceCPS" or source == "AMFileCPS":
        #~ upformat = "<HBBL" + "H" * 60
        #~upformat = "<BBBL" + "H" * 60
        upformat = "<BBHL" + "H" * 60
        wprint("Unpack Format: ", upformat)
        for i in range(0, len(devicedata), 128):
            dbuf = devicedata[i : i + 128]
            data = struct.unpack(upformat, dbuf)
            #~volt = data[2] + 350     # volt is given minus 350 to fit into 1 byte
            volt = data[2]            # volt is given as int
            dcfg = data[1] & 0x03    # selector is 1, or 2, or 3

            for j in range(0, 60):   # make 60 records
                dt = _convertUnixtimeToDateTime(data[3] - 60 + j)
                sdata = "{},{},{},{}".format(
                                    dt,
                                    data[4 + j],
                                    dcfg,
                                    volt,
                                    )
                dumpdata.append(sdata)
            #~ if i > 1000: break

    elif source == "AMDeviceCAM" or source == "AMFileCAM":
        upformat = "<BBHLLfffff"
        wprint("Unpack Format: ", upformat)
        for i in range(0, len(devicedata), 32):
            dbuf = devicedata[i : i + 32]
            data = struct.unpack(upformat, dbuf)
            #~volt = data[2] + 350     # volt is given minus 350 to fit into 1 byte
            volt = data[2]           # volt is now in 2 bytes, int 16
            dcfg = data[1] & 0x03    # selector is 1, or 2, or 3

            sdata = "{},{},{:0.2f},{:0.2f},{:0.2f},{:0.2f},{},{}".format( # make single record
                                _convertUnixtimeToDateTime(data[3]),
                                data[4],
                                data[5],
                                data[6],
                                data[7],
                                data[8],
                                dcfg,
                                volt,
                                )
            dumpdata.append(sdata)

    #~for a in dumpdata[:6]:  print("dumpdata:", a)
    #~print()
    #~for a in dumpdata[-6:]: print("dumpdata:", a)

    if len(dumpdata) == 0:
        error   = -1
        message = "No valid data found!"
        dprint(message)

    else:
    # parse HIST data
        gglobs.HistoryDataList      = []
        gglobs.HistoryParseList     = []
        gglobs.HistoryCommentList   = []

        #~ _getParsedHistoryCPS(dumpdata)
        if   source == "AMDeviceCPS" or source == "AMFileCPS":
            for i, rec in enumerate(dumpdata):
                _parseValueAdderCPS(i, rec)

        elif source == "AMDeviceCAM" or source == "AMFileCAM":
            for i, rec in enumerate(dumpdata):
                _parseValueAdderCAM(i, rec)

    # add headers
        dbhisClines    = [None] * 3
        #                  ctype    jday, jday modifier to use time unmodified
        dbhisClines[0] = ["HEADER", None, "0 hours", dbheader]
        dbhisClines[1] = ["ORIGIN", None, "0 hours", dborigin]
        dbhisClines[2] = ["DEVICE", None, "0 hours", dbdevice]

    # write to database
        gsup_sql.DB_insertDevice        (gglobs.hisConn, *data_originDB)
        gsup_sql.DB_insertComments      (gglobs.hisConn, dbhisClines)
        gsup_sql.DB_insertComments      (gglobs.hisConn, gglobs.HistoryCommentList)
        gsup_sql.DB_insertData          (gglobs.hisConn, gglobs.HistoryDataList)
        gsup_sql.DB_insertParse         (gglobs.hisConn, gglobs.HistoryParseList)

    # write device data to database
        saveToBin = True
        if saveToBin:   gsup_sql.DB_insertBin(gglobs.hisConn, devicedata)

        fprint("Database is created", debug=gglobs.debug)

    setDebugIndent(0)
    return error, message


def setAmbioServerIP():
    """Set settings for Ambiomon when in Station mode"""

    # setting a server address must be possible without a prior connection,
    # because Init fails if IP not accessible

    fncname = "setAmbioServerIP: "

    dprint(fncname)
    setDebugIndent(1)

    # AmbioServer IP
    lstaip = QLabel("Domain Name or IP Adress of AmbioMon")
    lstaip.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
    staip  = QLineEdit()
    staip.setToolTip("Enter the local Domain Name (if supported) or local IP where your AmbioMon device can be reached")
    staip.setText("{}".format(gglobs.AmbioServerIP))

    graphOptions=QGridLayout()
    graphOptions.setContentsMargins(10,10,10,10) # spacing around the graph options
    graphOptions.addWidget(lstaip, 0, 0)
    graphOptions.addWidget(staip,  0, 1)

    # Dialog box
    d = QDialog()
    d.setWindowIcon(gglobs.iconGeigerLog)
    d.setFont(gglobs.fontstd)
    d.setWindowTitle("Set AmbioMon Device IP")
    d.setWindowModality(Qt.ApplicationModal)
    #d.setWindowModality(Qt.NonModal)
    #d.setWindowModality(Qt.WindowModal)
    d.setMinimumWidth(400)

    # Buttons
    bbox = QDialogButtonBox()
    bbox.setStandardButtons(QDialogButtonBox.Cancel | QDialogButtonBox.Ok )
    bbox.accepted.connect(lambda: d.done(1))
    bbox.rejected.connect(lambda: d.done(-1))

    gglobs.btn = bbox.button(QDialogButtonBox.Ok)
    gglobs.btn.setEnabled(True)

    layoutV = QVBoxLayout(d)
    layoutV.addLayout(graphOptions)
    layoutV.addWidget(bbox)

    if gglobs.logging:         # no change of parameters when logging
        gglobs.btn  .setEnabled(False)
        staip       .setEnabled(False)

    retval = d.exec()
    #print("reval:", retval)

    if retval != 1:
        # ESCAPE pressed or Cancel Button
        dprint(fncname + "Canceling; settings unchanged")

    else:
        # OK pressed
        gglobs.AmbioServerIP = staip.text().strip()

        dprint(fncname + "new IP Address:    ", gglobs.AmbioServerIP)
        fprint(header("Configure AmbioMon WiFi Station Mode"))
        fprint("AmbioMon Station Mode IP:"     , "{}"    .format(gglobs.AmbioServerIP))

    setDebugIndent(0)


def setAmbioLogDatatype():
    """Set the datatype GeigerLog will request from Ambiomon (LAST or AVG)"""

    if not gglobs.AmbioConnection: return "No connected device"

    dprint("setAmbioLogDatatype:")
    setDebugIndent(1)

    lstaip = QLabel("Data as LAST value or last AVG value?\n(No change during logging)" + " "*15)
    lstaip.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)

    b0 = QRadioButton("LAST")             # this is default
    b1 = QRadioButton("AVG")
    b0.setToolTip("Select 'LAST' to get last value of data, or 'AVG' to get last 1 min average of values")
    b1.setToolTip("Select 'LAST' to get last value of data, or 'AVG' to get last 1 min average of values")

    if gglobs.AmbioDataType == "LAST" : b0.setChecked(True)
    else:                               b1.setChecked(True)

    layoutT = QHBoxLayout()
    layoutT.addWidget(b0)
    layoutT.addWidget(b1)

    graphOptions=QGridLayout()
    graphOptions.setContentsMargins(10,10,10,10) # spacing around the options
    graphOptions.addWidget(lstaip,          0, 0)
    graphOptions.addLayout(layoutT,         0, 1)

    # Dialog box
    d = QDialog()
    d.setWindowIcon(gglobs.iconGeigerLog)
    d.setFont(gglobs.fontstd)
    d.setWindowTitle("Select Data Type Mode")
    d.setWindowModality(Qt.ApplicationModal)
    #d.setWindowModality(Qt.NonModal)
    #d.setWindowModality(Qt.WindowModal)
    d.setMinimumWidth(400)

    # Buttons
    bbox = QDialogButtonBox()
    bbox.setStandardButtons(QDialogButtonBox.Cancel | QDialogButtonBox.Ok )
    bbox.accepted.connect(lambda: d.done(1))
    bbox.rejected.connect(lambda: d.done(-1))

    gglobs.btn = bbox.button(QDialogButtonBox.Ok)
    gglobs.btn.setEnabled(True)

    layoutV = QVBoxLayout(d)
    layoutV.addLayout(graphOptions)
    layoutV.addWidget(bbox)

    if gglobs.logging:         # no change of parameters when logging
        gglobs.btn  .setEnabled(False)

    retval = d.exec()
    #print("reval:", retval)

    if retval != 1:
        # ESCAPE pressed or Cancel Button clicked
        dprint("setAmbioLogDatatype: Settings unchanged")
    else:
        if b0.isChecked(): gglobs.AmbioDataType = "LAST"    # b0.isChecked()
        else:              gglobs.AmbioDataType = "AVG"     # b1.isChecked()

        fprint(header("Select Data Type Mode"))
        fprint("AmbioMon Data Type:", "{}"    .format(gglobs.AmbioDataType), debug=True)

    setDebugIndent(0)


def getAmbioValues(varlist):
    """Read all AmbioMon data"""

    fncname = "getAmbioValues: "

    alldata = {}

    start = time.time()
    attempts     = 0        # no of attempts to get a connection
    attempts_max = 5        # max no of attempts

    while attempts < attempts_max:
        try:
            if not gglobs.logging:  break
            attempts += 1

            if gglobs.AmbioDataType == "LAST":  url = _getAmbioUrl() + "/lastdata"
            else:                               url = _getAmbioUrl() + "/lastavg"

            page  = urllib.request.urlopen(url, timeout=gglobs.AmbioTimeout)        # 40...120 ms, rest < 0.05 ms
            data  = page.read().decode("UTF-8").split(",")
            #~print("page: geturl : ", page.geturl())
            #~print("page: getcode: ", page.getcode())
            #~for a, b in page.info().items(): print ("page.info:  {:20s}   {}".format(a, b))
            #~print(fncname + "page.read: ", data)

            #stop = time.time()
            #~start = time.time()

            for a in varlist:
                if   a == "CPM":
                                    cpm = float(data[1]) if (float(data[1]) != 4294967295) else gglobs.NAN
                                    alldata.update({"CPM":      cpm                 })   # CPM
                elif a == "CPS":    alldata.update({"CPS":      float(data[2])      })   # CPS
                elif a == "CPM1st": alldata.update({"CPM1st":   float(data[6])      })   # BME680 resistance kOhm
                elif a == "CPS1st": alldata.update({"CPS1st":   float(data[6])      })   # BME680 resistance kOhm
                elif a == "CPM2nd": alldata.update({"CPM2nd":   float(data[9])      })   # Chip Voltage
                elif a == "CPS2nd": alldata.update({"CPS2nd":   float(data[10])     })   # Supply Voltage
                elif a == "CPM3rd": alldata.update({"CPM3rd":   float(data[9])      })   # Chip Voltage
                elif a == "CPS3rd": alldata.update({"CPS3rd":   float(data[10])     })   # Supply Voltage
                elif a == "T":      alldata.update({"T":        float(data[3])      })   # T     from BMEX80
                elif a == "P":      alldata.update({"P":        float(data[4])      })   # P     from BMEX80
                elif a == "H":      alldata.update({"H":        float(data[5])      })   # H     from BMEX80
                elif a == "X":      alldata.update({"X":        float(data[6])      })   # Airq  BME680 resistance kOhm (plotted as (LOG10(1/VAL) + 3 )*50)

            break

        except Exception as e:
            msg = fncname + "#{}: {}: Reading '{}' failed <br>with exception:  '{}'".format(attempts, stime(), url, cleanHTML(e))
            exceptPrint(e, msg)
            if attempts == attempts_max:  playWav("error")
            qefprint(msg)
            qefprint(" Timeout setting: {} sec".format(gglobs.AmbioTimeout))
            Qt_update()
            time.sleep(2) # does a pause help? 0.5 not much; 1 not really

    stop = time.time()
    loadTime = round((stop - start) * 1000, 2)      # ms
    alldata.update({"CPM1st":   float(loadTime)})   # Overall duration of loading the data set

    printLoggedValues(fncname, varlist, alldata)

    return alldata


def initAmbioMon():
    """Initialize AmbioMon"""

    fncname = "initAmbioMon: "
    errmsg  = ""

    if not gglobs.AmbioActivation:
        errmsg = "Initialzing AmbioMon not possible as AmbioMon device is not activated in configuration"
        dprint(fncname + errmsg)
        return errmsg

    dprint(fncname + "Initialzing AmbioMon")
    setDebugIndent(1)

    # set configuration
    if gglobs.AmbioServerIP     == "auto":  gglobs.AmbioServerIP     = "192.168.4.1"
    if gglobs.AmbioTimeout      == "auto":  gglobs.AmbioTimeout      = 3    # 1 sec scheint zu kurz, 5 sec bringt nichts
    if gglobs.AmbioCalibration  == "auto":  gglobs.AmbioCalibration  = 154
    if gglobs.AmbioVariables    == "auto":  gglobs.AmbioVariables    = "CPM, CPS, CPM1st, CPS1st, CPM2nd, CPS2nd, CPM3rd, CPS3rd, T, P, H, X"
    if gglobs.AmbioDataType     == "auto":  gglobs.AmbioDataType     = "LAST"           # using 'lastdata' call, not avg for 'lastavg'

    setCalibrations(gglobs.AmbioVariables, gglobs.AmbioCalibration)

    gglobs.AmbioDeviceName        = "AmbioMon++"
    gglobs.AmbioDeviceDetected    = _getAmbioDevice()            # expect like 'ESP32-WROOM-Dev'
    gglobs.Devices["AmbioMon"][0] = gglobs.AmbioDeviceDetected

    if gglobs.AmbioDeviceDetected == "NONE":
        errmsg = "<br>No connection to: AmbioServerIP: '{}'".format(gglobs.AmbioServerIP)
        edprint(fncname + errmsg)
        return errmsg

    # connected
    gglobs.AmbioConnection = True
    dprint(fncname + "connected to: AmbioServerIP: '{}', detected device: '{}'".format(gglobs.AmbioServerIP, gglobs.AmbioDeviceDetected))

    setLoggableVariables("AmbioMon", gglobs.AmbioVariables)

    setDebugIndent(0)
    return errmsg


def terminateAmbioMon():
    """opposit of init ;-)"""

    if not gglobs.AmbioConnection: return

    fncname = "terminateAmbioMon: "

    dprint(fncname)
    gglobs.AmbioConnection = False


def printAmbioInfo(extended=False):
    """prints basic info on the AmbioMon device"""

    setBusyCursor()

    txt = "AmbioMon Device"
    if extended:  txt += " Extended"
    fprint(header(txt))
    fprint("Configured Connection:", "Server IP: '{}'".format(gglobs.AmbioServerIP))
    fprint(getAmbioInfo(extended=extended))

    setNormalCursor()


def getAmbioInfo(extended=False):
    """Info on the AmbioMon Device"""

    if not gglobs.AmbioConnection: return "No connected device"

    AmbioInfo = """Connected Device:             '{}'
Configured Variables:         {}
Geiger Tube Sensitivity:      {:0.1f} CPM/(µSv/h) ({:0.4f} µSv/h/CPM)
Data Handling [LAST, AVG]:    {}
TESTING USAGE:  CPM         = GMtube CPM
                CPS         = GMtube CPS

                CPM1st      = FreeHeap [B]
                CPS1st      = AllocHeap [B]

                CPM2nd      = Batt Voltage ADS1115
                CPS2nd      = Batt Voltage ESP32

                CPM3rd      = Selector position
                CPS3rd      = Anode Voltage

                T           = BME680 Temp
                P           = BME680 Press
                H           = BME680 Humid
                X           = BME680 (log10(1/R[kOhm]) + 3 )*50

""".format(\
                                gglobs.AmbioDeviceDetected, \
                                gglobs.AmbioVariables, \
                                gglobs.AmbioCalibration, 1 / gglobs.AmbioCalibration, \
                                gglobs.AmbioDataType \
                                )
    if extended == True:
        AmbioInfo += """
Geiger tube voltage:          {} Volt
Cycletime:                    {} sec
Frequency:                    {} Hz
PWM:                          {}
Saving:                       {}
""".format(\
                                gglobs.AmbioVoltage,
                                gglobs.AmbioCycletime,
                                gglobs.AmbioFrequency,
                                gglobs.AmbioPwm,
                                gglobs.AmbioSav,
                                )
    return AmbioInfo

