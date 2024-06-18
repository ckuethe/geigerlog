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
__copyright__       = "Copyright 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024"
__credits__         = [""]
__license__         = "GPL3"

from gsup_utils   import *
import gsup_sql                         # database handling for history downloads


###  used only internally within gdev_ambiomon.py ##############################

def _getAmbioUrl():
    """get url like 'http://10.0.0.78/'; Port is always 80"""

    return "http://{}".format(g.AmbioServerIP)


def _getAmbioDevice():
    """get the device name by calling page '/devid' returning:
                      like:   'AmbioMon++, ESP32-WROOM-2, ambiomon04, 1, 456, 240'
                      giving: 'AmbioMon++ on ESP32-WROOM-2'
    """

    defname             = "_getAmbioDevice: "
    retvalue            = "NONE"                  # default for failure
    g.AmbioCPUFrequency = g.NAN                   # default for failure
    g.AmbioSelector     = g.NAN                   # default for failure
    g.AmbioVoltage      = g.NAN                   # default for failure

    loops = 1
    while loops <= 3:
        try:
            url   = _getAmbioUrl() + "/devid"
            page  = urllib.request.urlopen(url, timeout=g.AmbioTimeout)
            data  = page.read()
            data  = data.decode("UTF-8")
            g.AmbioDevIDPage = data
            data  = data.split(",")
            cdprint(defname, "devid data: ", data)

        except Exception as e:
            exceptPrint(e, defname + "Failed at url:'{}'".format(url))

        else:
            # like:   'AmbioMon++, ESP32-WROOM-2, ambiomon04, 1, 456, 240'

            retvalue = "{} on {}".format(data[0].strip(), data[1].strip())      # 0, 1

            # hostname = data[2]                                                # 2 --- not used

            try:    g.AmbioSelector     = float(data[3])                        # 3
            except: g.AmbioSelector     = g.NAN

            try:    g.AmbioVoltage      = float(data[4])                        # 4
            except: g.AmbioVoltage      = g.NAN

            try:    g.AmbioCPUFrequency = float(data[5])                        # 5
            except: g.AmbioCPUFrequency = g.NAN

            break

        loops += 1
        edprint(defname, "FAILURE: Retrying, attempt #{}".format(loops))

    cdprint(defname, "Device: '{}'  Frequency: {} MHz".format(retvalue, g.AmbioCPUFrequency))

    return retvalue


def _getAmbioDeviceCalib():
    """get the calibration like '123.0' by calling page '/calib' yielding:
                           like:    '2, ra226, Ra-226, 174.0'
                                    '3, custom, Custom, 123.0'
                                    '4, special, LND712, 108.0'
    """

    defname  = "_getAmbioDeviceCalib: "
    retvalue = g.NAN

    loops = 1
    while loops <= 3:
        try:
            url   = _getAmbioUrl() + "/calib"
            page  = urllib.request.urlopen(url, timeout=g.AmbioTimeout)
            data  = page.read()
            data  = data.decode("UTF-8")
            g.AmbioCalibPage = data
            data  = data.split(",")
            cdprint(defname, "Calib data: ", data)

        except Exception as e:
            exceptPrint(e, defname + "Failed at url:'{}'".format(url))

        else:
            try:    retvalue = float(data[3].strip())
            except: retvalue = g.NAN
            break

        loops += 1
        edprint(defname, "FAILURE: Retrying, attempt #{}".format(loops))

    cdprint(defname, "Calib Value: {}".format(retvalue))

    return retvalue


def _convertUnixtimeToDateTime(unixtime):
    """convert a Unix time in sec into datetime like: 2020-05-10 11:48:50"""

    return dt.datetime.utcfromtimestamp(unixtime).strftime('%Y-%m-%d %H:%M:%S')


def _printException(e, rec):
    dprint  ("Exception _parseValueAdder: ", e)
    efprint ("AmbioMon History Download had error: ", cleanHTML(e))
    qefprint("Record is ignored, has Error: ", rec)
    dprint  ("Record is ignored, has Error: ", rec)


def _parseValueAdderCPS(i, rec):
    """Add the parse results to the *.his list"""

    defname = "_parseValueAdderCPS: "

    # create the data for the database; datalist covers:
    #     Index, DateTime, CPM, CPS, CPM1st, CPS1st, CPM2nd, CPS2nd,  CPM3rd, CPS3rd, Temp, Press, Humid, X
    #     0      1         2    3    4       5       6       7        8       9       10    11     12     13

    # rdprint(defname, "i:{}, rec:{}".format(i, rec))
    try:
        reclist      = rec.split(",", 5)
        # rdprint(defname, "i:{}, rec:{}".format(i, reclist))

        datalist     = [None] * (g.datacolsDefault + 1)     # (13 + 1) = 14 x None
        datalist[0]                 = i                     # byte index
        datalist[1]                 = reclist[0]            # DateTime UTC
        datalist[g.AmbioCPSpointer] = reclist[1]            # cps
        datalist[8]                 = reclist[2]            # selector
        datalist[9]                 = reclist[3]            # volt

        g.HistoryDataList.append (datalist)

    except Exception as e:
        exceptPrint(e, rec)
        _printException(e, rec)


def _parseValueAdderCAM(i, rec):
    """Add the parse results to the *.his list"""

    defname = "_parseValueAdderCAM: "

    # create the data for the database; datalist covers:
    #     Index, DateTime, CPM, CPS, CPM1st, CPS1st, CPM2nd, CPS2nd,  CPM3rd, CPS3rd, Temp, Press, Humid, X
    #     0      1         2    3    4       5       6       7        8       9       10    11     12     13

    # rec:          DateTime           ,CPM,T     P      H     X    S,V
    # rec:          2023-08-06 13:31:40,198,25.31,998.80,50.86,0.00,1,456
    # reclist:      DateTime             ,  CPM,   T        P          H        X       S,   V
    # reclist:     ['2023-08-06 17:24:00', '182', '25.39', '1001.30', '50.37', '0.00', '1', '456']


    # rdprint(defname, "i:{}, rec:{}".format(i, rec))
    try:
        reclist      = rec.split(",", 9)                    # --> datetime + 6 values + 1 extra for the rest
        # rdprint(defname, "i:{}, rec:{}".format(i, reclist))

        datalist     = [None] * (g.datacolsDefault + 1)     # (13 + 1) = 14 x None

        datalist[0]                 = i                    # byte index
        datalist[1]                 = reclist[0]           # DateTime UTC
        datalist[g.AmbioCPMpointer] = reclist[1]           # cpm

        datalist[8]                 = reclist[6]           # selector (CPM3rd)
        datalist[9]                 = reclist[7]           # volt     (CPS3rd)

        datalist[10]                = reclist[2]           # temp
        datalist[11]                = reclist[3]           # pressure
        datalist[12]                = reclist[4]           # humidity
        datalist[13]                = reclist[5]           # Xtra (e.g. air quality)

        g.HistoryDataList.append (datalist)

    except Exception as e:
        exceptPrint(e, rec)
        _printException(e, rec)


# gdev_ambiomon.py use only
###############################################################################


###############################################################################
# Public Functions


def makeAmbioHistory(source, device):  # source == "AMDeviceCAM" or "AMDeviceCPS"
    """read the history from an AmbioMon device
       parameter: source == "AMDeviceCAM" or "AMDeviceCPS"
       return   : error, message
    """

    defname = "makeAmbioHistory: "

    if not g.Devices["AmbioMon"][g.ACTIV]:
        emsg = "AmbioMon device is not activated"
        dprint(defname, emsg)
        return -1, emsg

    dprint(defname, "from source: '{}' using device: '{}'".format(source, device))
    dprint(defname, "g.AMFilePath: {}".format(g.AMFilePath))
    setIndent(1)

    error           = 0         # default: no error
    message         = ""        # default: no message

    start = time.time()

# get device data for AmbioMon
    if   source == "AMDeviceCPS" or source == "AMDeviceCAM":

        if not g.Devices["AmbioMon"][g.CONN] :
            emsg = "AmbioMon device is not connected"
            dprint(defname + emsg)
            return -1, emsg

        if   source == "AMDeviceCPS": url = _getAmbioUrl() + "/cps.data"
        elif source == "AMDeviceCAM": url = _getAmbioUrl() + "/cam.data"
        fprint("Using URL: " + url)
        QtUpdate()

        try:
            page        = urllib.request.urlopen(url, timeout=10)
            devicedata  = page.read()   # type(devicedata) = <class 'byte'>
        except Exception as e:
            msg = "urllib.request.urlopen Failed"
            exceptPrint(e, msg)
            efprint("{} Reading data from AmbioMon++ failed with exception:\n{}".format(stime(), cleanHTML(e)))
            setIndent(0)
            # QtUpdate()
            return -1, cleanHTML(e)

# get file data for AmbioMon
    elif source == "AMFileCPS" or source == "AMFileCAM":
        try:
            devicedata = readBinaryFile(g.AMFilePath)
        except Exception as e:
            msg1 = "Reading AmbioMon++ data from File failed"
            msg2 = "{} ".format(stime()) + msg1 + "with exception:\n{}" + cleanHTML(e)
            exceptPrint(e, msg1)
            efprint(msg)
            setIndent(0)
            # QtUpdate()
            return -1, cleanHTML(e)

    stop       = time.time()

    dtime      = (stop - start)
    lendevicedata = len(devicedata)
    msg        = "Downloaded {:0.1f} kB from {} in {:0.1f} milliseconds ({:0.1f} kB/s)".format(lendevicedata / 1000, source, dtime * 1000, lendevicedata/dtime/1000)
    vprint(msg)
    fprint(msg)
    fprint("Processing data ...")
    QtUpdate()

    data_originDB   = (stime(), g.Devices["AmbioMon"][g.DNAME])
    dbheader        = "File created by reading log from device"
    dborigin        = "Download from device"
    dbdevice        = "{}".format(data_originDB[1])

    dumpdata = []
# CPS data
    if   source == "AMDeviceCPS" or source == "AMFileCPS":
        upformat = "<BBHL" + "H" * 60
        wprint("Unpack Format: ", upformat)
        try:
            for i in range(0, len(devicedata), 128):
                dbuf = devicedata[i : i + 128]
                data = struct.unpack(upformat, dbuf)
                volt = data[2]            # volt is given as int
                dcfg = data[1] & 0x03     # selector is 1, or 2, or 3

                for j in range(0, 60):   # make 60 records
                    cdt = _convertUnixtimeToDateTime(data[3] - 60 + j)
                    sdata = "{},{},{},{}".format(
                                        cdt,
                                        data[4 + j],
                                        dcfg,
                                        volt,
                                        )
                    dumpdata.append(sdata)
                    # rdprint(defname, sdata)
                #~ if i > 1000: break

        except Exception as e:
            msg = "unpacking CPS data"
            exceptPrint(e, msg)
            efprint(defname + msg)
            setIndent(0)
            return -1, cleanHTML(e)

# CAM data
    elif source == "AMDeviceCAM" or source == "AMFileCAM":
        upformat = "<BBHLLfffff"
        wprint("Unpack Format: ", upformat)
        try:
            for i in range(0, len(devicedata), 32):
                dbuf = devicedata[i : i + 32]
                data = struct.unpack(upformat, dbuf)
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
        except Exception as e:
            msg = "unpacking CAM data"
            exceptPrint(e, msg)
            efprint(defname + msg)
            setIndent(0)
            return -1, cleanHTML(e)


    #~for a in dumpdata[:6]:  print("dumpdata:", a)
    #~print()
    #~for a in dumpdata[-6:]: print("dumpdata:", a)

    if len(dumpdata) == 0:
        error   = -1
        message = "No valid data found!"
        dprint(message)

    else:
    # parse HIST data
        g.HistoryDataList      = []
        g.HistoryParseList     = []
        g.HistoryCommentList   = []

        #~ _getParsedHistoryCPS(dumpdata)
        if   source == "AMDeviceCPS" or source == "AMFileCPS":
            for i, rec in enumerate(dumpdata):
                _parseValueAdderCPS(i, rec)                         # adds values to g.HistoryDataList

        elif source == "AMDeviceCAM" or source == "AMFileCAM":
            for i, rec in enumerate(dumpdata):
                _parseValueAdderCAM(i, rec)                         # adds values to g.HistoryDataList

    # add headers
        dbhisClines    = [None] * 3
        jtime = getTimeJulian()
        #                  ctype    jday,  text
        dbhisClines[0] = ["HEADER", jtime, dbheader]
        dbhisClines[1] = ["ORIGIN", jtime, dborigin]
        dbhisClines[2] = ["DEVICE", jtime, dbdevice]

    # write to database
        gsup_sql.DB_insertDevice        (g.hisConn, *data_originDB)
        gsup_sql.DB_insertComments      (g.hisConn, dbhisClines)
        gsup_sql.DB_insertComments      (g.hisConn, g.HistoryCommentList)
        gsup_sql.DB_insertData          (g.hisConn, g.HistoryDataList)
        gsup_sql.DB_insertParse         (g.hisConn, g.HistoryParseList)         # remains empty!

    # write device data to database
        saveToBin = True
        if saveToBin:   gsup_sql.DB_insertBin(g.hisConn, devicedata)

        msg = "Database is created"
        fprint(msg)
        dprint(msg)

    setIndent(0)
    return error, message


def setAmbioServerIP():
    """Set settings for Ambiomon when in Station mode"""

    # setting a server address must be possible without a prior connection,
    # because Init fails if IP not accessible

    defname = "setAmbioServerIP: "

    dprint(defname)
    setIndent(1)

    # AmbioServer IP
    lstaip = QLabel("Domain Name or IP Adress of AmbioMon")
    lstaip.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
    staip  = QLineEdit()
    staip.setToolTip("Enter the local Domain Name (if supported) or local IP where your AmbioMon device can be reached")
    staip.setText("{}".format(g.AmbioServerIP))

    graphOptions=QGridLayout()
    graphOptions.setContentsMargins(10,10,10,10) # spacing around the graph options
    graphOptions.addWidget(lstaip, 0, 0)
    graphOptions.addWidget(staip,  0, 1)

    # Dialog box
    d = QDialog()
    d.setWindowIcon(g.iconGeigerLog)
    d.setFont(g.fontstd)
    d.setWindowTitle("Set AmbioMon Device IP")
    d.setWindowModality(Qt.WindowModal)
    d.setMinimumWidth(400)

    # Buttons
    bbox = QDialogButtonBox()
    bbox.setStandardButtons(QDialogButtonBox.Cancel | QDialogButtonBox.Ok )
    bbox.accepted.connect(lambda: d.done(1))
    bbox.rejected.connect(lambda: d.done(-1))

    g.btn = bbox.button(QDialogButtonBox.Ok)
    g.btn.setEnabled(True)

    layoutV = QVBoxLayout(d)
    layoutV.addLayout(graphOptions)
    layoutV.addWidget(bbox)

    if g.logging:         # no change of parameters when logging
        g.btn  .setEnabled(False)
        staip       .setEnabled(False)

    retval = d.exec()
    #print("reval:", retval)

    if retval != 1:
        # ESCAPE pressed or Cancel Button
        dprint(defname + "Canceling; settings unchanged")

    else:
        # OK pressed
        g.AmbioServerIP = staip.text().strip()

        dprint(defname + "new IP Address:    ", g.AmbioServerIP)
        fprint(header("Configure AmbioMon WiFi Station Mode"))
        fprint("AmbioMon Station Mode IP:"     , "{}"    .format(g.AmbioServerIP))

    setIndent(0)


def sendToSerial():
    """Sends text to the AmbioMon via Serial"""

    defname = "sendToSerial: "

    dprint(defname)
    setIndent(1)

    # Message
    lstaip = QLabel("Message for AmbioMon")
    lstaip.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
    staip  = QLineEdit()
    staip.setToolTip("Enter a message tp be send to AmbioMon via Serial")
    staip.setText("")

    graphOptions=QGridLayout()
    graphOptions.setContentsMargins(10,10,10,10) # spacing around the graph options
    graphOptions.addWidget(lstaip, 0, 0)
    graphOptions.addWidget(staip,  0, 1)

    # Dialog box
    d = QDialog()
    d.setWindowIcon(g.iconGeigerLog)
    d.setFont(g.fontstd)
    d.setWindowTitle("Send Message to AmbioMon")
    d.setWindowModality(Qt.WindowModal)
    d.setMinimumWidth(400)

    # Buttons
    bbox = QDialogButtonBox()
    bbox.setStandardButtons(QDialogButtonBox.Cancel | QDialogButtonBox.Ok )
    bbox.accepted.connect(lambda: d.done(1))
    bbox.rejected.connect(lambda: d.done(-1))

    g.btn = bbox.button(QDialogButtonBox.Ok)
    g.btn.setEnabled(True)

    layoutV = QVBoxLayout(d)
    layoutV.addLayout(graphOptions)
    layoutV.addWidget(bbox)

    retval = d.exec()
    #print("reval:", retval)

    if retval != 1:
        # ESCAPE pressed or Cancel Button
        dprint(defname + "Canceling; settings unchanged")

    else:
        # OK pressed
        msg = staip.text().strip()

        dprint(defname + "Message:    ", msg)
        fprint(header("Sending Message to AmbioMon"))
        fprint("AmbioMon Message:"     , "{}"    .format(msg))

        if g.ESP32Serial is None:
            openESP32Serial()

        g.ESP32Serial.write(bytes(msg + "\n", "UTF-8"))

    setIndent(0)


def setAmbioLogDatatype():
    """Set the datatype GeigerLog will request from Ambiomon (LAST or AVG)"""

    if not g.Devices["AmbioMon"][g.CONN] : return "No connected device"

    dprint("setAmbioLogDatatype:")
    setIndent(1)

    lstaip = QLabel("Data as LAST value or last AVG value?\n(No change during logging)" + " "*15)
    lstaip.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)

    b0 = QRadioButton("LAST")             # this is default
    b1 = QRadioButton("AVG")
    b0.setToolTip("Select 'LAST' to get last value of data, or 'AVG' to get last 1 min average of values")
    b1.setToolTip("Select 'LAST' to get last value of data, or 'AVG' to get last 1 min average of values")

    if g.AmbioDataType == "LAST" : b0.setChecked(True)
    else:                          b1.setChecked(True)

    layoutT = QHBoxLayout()
    layoutT.addWidget(b0)
    layoutT.addWidget(b1)

    graphOptions=QGridLayout()
    graphOptions.setContentsMargins(10,10,10,10) # spacing around the options
    graphOptions.addWidget(lstaip,          0, 0)
    graphOptions.addLayout(layoutT,         0, 1)

    # Dialog box
    d = QDialog()
    d.setWindowIcon(g.iconGeigerLog)
    d.setFont(g.fontstd)
    d.setWindowTitle("Select Data Type Mode")
    d.setWindowModality(Qt.WindowModal)
    d.setMinimumWidth(400)

    # Buttons
    bbox = QDialogButtonBox()
    bbox.setStandardButtons(QDialogButtonBox.Cancel | QDialogButtonBox.Ok )
    bbox.accepted.connect(lambda: d.done(1))
    bbox.rejected.connect(lambda: d.done(-1))

    g.btn = bbox.button(QDialogButtonBox.Ok)
    g.btn.setEnabled(True)

    layoutV = QVBoxLayout(d)
    layoutV.addLayout(graphOptions)
    layoutV.addWidget(bbox)

    if g.logging:         # no change of parameters when logging
        g.btn  .setEnabled(False)

    retval = d.exec()
    #print("reval:", retval)

    if retval != 1:
        # ESCAPE pressed or Cancel Button clicked
        dprint("setAmbioLogDatatype: Settings unchanged")
    else:
        # Ok clicked
        if b0.isChecked(): g.AmbioDataType = "LAST"    # b0.isChecked()
        else:              g.AmbioDataType = "AVG"     # b1.isChecked()

        fprint(header("Select Data Type Mode"))
        msg = "New AmbioMon Data Type:", "{}".format(g.AmbioDataType)
        fprint(msg)
        dprint(msg)

    setIndent(0)


def openESP32Serial():
    """Open the Serial connection to the ESP32"""

    defname = "openESP32Serial: "

    dv      = "/dev/ttyUSB0" # device
    br      = 115200         # baudrate
    to      = 3              # timeout
    wto     = 1              # write timeout

    # try to close it first
    closeESP32Serial()

    # now try to open it
    try:
        g.ESP32Serial = serial.Serial(dv, br, timeout=to, write_timeout=wto)
    except Exception as e:
        closeESP32Serial()
        msg = defname + "Open failed"
        exceptPrint(e, msg)
        qefprint(msg)
    else:
        fprint(defname + "connected")


def closeESP32Serial():
    """Try to close the Serial connection to the ESP32 and Null it"""

    try:    g.ESP32Serial.close()
    except: pass

    g.ESP32Serial = None


def writeESP32Serial(msg):
    """Try to close the Serial connection to the ESP32 and Null it"""

    try:
        g.ESP32Serial.write(msg)
        # without delay after writing, ESP isn't fast enough to provide answer
        #  1 ms: too short
        #  2 ms: works most but not always
        #  3 ms: works most but not always
        #  4 ms: works most but not always
        #  5 ms: works most but not always
        # 10 ms: works; occasionally a failure
        time.sleep(0.010)
    except Exception as e:
        msg = "Failure writing to the ESPSerial"
        exceptPrint(e, msg)
        qefprint(msg)


def readESP32Serial():
    """read the ESP32 terminal output"""
    # results in problems with other serial devices

    # using 2 terminals
    # https://unix.stackexchange.com/questions/261531/how-to-send-output-from-one-terminal-to-another-without-making-any-new-pipe-or-f

    defname = "readESP32Serial: "
    vprint(defname)

    logfile         = "esp32.termlog"
    bytesWaiting    = 0                             # to avoid reference error
    empty           = "nan, nan, nan, nan, nan, nan, nan, nan, nan"
    glval           = empty
    logfilepath     = os.path.join(g.dataDir, logfile) # save in data dir

    # if the serial port is not open then try to open it now,
    # and clear the logfile if sucessful
    if g.ESP32Serial is None:
        openESP32Serial()
        if g.ESP32Serial is None:  # tried to connect again, but failed
            edprint("g.ESP32Serial is None --- returning with nans")
            return glval
        try:
            with open(logfilepath, "wt", encoding="UTF-8", errors='replace', buffering = 1) as f:
                f.write("Starting at: {}\n".format(longstime()))
        except Exception as e:
            exceptPrint(e, "readESP32Serial")

    setIndent(1)

    writeESP32Serial(b"GeigerLog\n")

    while True:
        try:
            bytesWaiting = g.ESP32Serial.in_waiting
            #print("bytesWaiting: ", bytesWaiting)
        except Exception as e:
            msg = "Exception: fasilure in getting bytesWaiting"
            exceptPrint(e, defname + msg)
            closeESP32Serial()
            break

        if bytesWaiting == 0: break

        try:
            # readline(size): Read and return one line from the stream.
            # If size is specified, at most size bytes will be read.
            #print("bytes waiting before readline: ", g.ESP32Serial.in_waiting)
            rec = g.ESP32Serial.readline()
            #print("rec: ", rec)
        except Exception as e:
            msg = "Exception: failure in 'readline'"
            exceptPrint(e, defname + msg)
            closeESP32Serial()
            break

        try:
            rec = rec.decode('UTF-8')
            #print("rec.decode: ", rec)
        except Exception as e:
            msg = "Exception: failure in 'decode'"
            exceptPrint(e, defname + msg)
            closeESP32Serial()
            break

        if rec[-1] != "\n": rec += "\n"         # add a linefeed if none present
        if rec.startswith("ESP32: GeigerLog"):
            vprint(rec[:-1])                    # remove LF for print
            glval = rec[17:-1]                  # cut off 'GeigerLog:' and LF

        try:
            with open(logfilepath, "at", encoding="UTF-8", errors='replace', buffering = 1) as f:
                f.write(rec)                        # keep LF
        except Exception as e:
            exceptPrint(e, defname + "write to logfilepath")

    #print("glval: ", glval)
    if glval == empty: vprint("ESP32: GeigerLog - No Data!")

    setIndent(0)

    return glval


#iii
def initAmbioMon():
    """Initialize AmbioMon"""

    defname = "initAmbioMon: "

    dprint(defname, "Initializing AmbioMon Device")
    setIndent(1)

    # set configuration
    if g.AmbioServerIP    == "auto": g.AmbioServerIP    = getGeigerLogIP()    # GeigerLog's onw IP
    if g.AmbioServerPort  == "auto": g.AmbioServerPort  = 80                  # default port no
    if g.AmbioTimeout     == "auto": g.AmbioTimeout     = 3                   # 1 sec scheint zu kurz, 2 häufig zu kurz, 3 meist ok, 5 sec bringt nichts
    if g.AmbioDataType    == "auto": g.AmbioDataType    = "LAST"              # using 'lastdata' call, not avg for 'lastavg'
    if g.AmbioVariables   == "auto": g.AmbioVariables   = "CPM3rd, CPS3rd, Temp, Press, Humid, Xtra"

    g.AmbioVariables = setLoggableVariables("AmbioMon", g.AmbioVariables)

    for vname in g.AmbioVariables.split(","):
        vname = vname.strip()
        # rdprint(defname, "vname: ", vname)
        if   vname == "CPM":      g.AmbioCPMpointer = 2
        elif vname == "CPS":      g.AmbioCPSpointer = 3
        elif vname == "CPM1st":   g.AmbioCPMpointer = 4
        elif vname == "CPS1st":   g.AmbioCPSpointer = 5
        elif vname == "CPM2nd":   g.AmbioCPMpointer = 6
        elif vname == "CPM2nd":   g.AmbioCPSpointer = 7
        # elif vname == "CPM3rd":   g.AmbioCPMpointer = 8   # is used for selector
        # elif vname == "CPM3rd":   g.AmbioCPSpointer = 9   # is used for volt

    g.Devices["AmbioMon"][g.DNAME] = _getAmbioDevice() # expect like 'AmbioMon++ on ESP32-WROOM-Dev' on success, 'NONE' on failure

    if g.Devices["AmbioMon"][g.DNAME] == "NONE":
        # not connected
        g.Devices["AmbioMon"][g.CONN] = False
        msg = "No connection to: AmbioServerIP: '{}'".format(g.AmbioServerIP)
        edprint(defname + msg)
    else:
        # is connected
        g.Devices["AmbioMon"][g.CONN] = True
        msg  = ""
        dprint(defname, "connected to: AmbioServerIP: '{}', detected device: '{}'".format(g.AmbioServerIP, g.Devices["AmbioMon"][g.DNAME]))

        AmbioSense = _getAmbioDeviceCalib()
        for vname in g.AmbioVariables.split(","):
            vname = vname.strip()
            # rdprint(defname, "vname: ", vname)
            if   vname == "CPM":      g.Sensitivity[0] = AmbioSense
            elif vname == "CPS":      g.Sensitivity[0] = AmbioSense
            elif vname == "CPM1st":   g.Sensitivity[1] = AmbioSense
            elif vname == "CPS1st":   g.Sensitivity[1] = AmbioSense
            elif vname == "CPM2nd":   g.Sensitivity[2] = AmbioSense
            elif vname == "CPM2nd":   g.Sensitivity[2] = AmbioSense

    # set all active g.AmbioValues to nan (only the active ones!)
    # rdprint(defname, "g.Devices['AmbioMon'][g.VNAMES]: ", g.Devices["AmbioMon"][g.VNAMES])
    for vname in g.Devices["AmbioMon"][g.VNAMES]:
        g.AmbioValues[vname] = g.NAN

    g.AmbioThreadRun         = True
    g.AmbioMonThread            = threading.Thread(target = AmbioMonThreadTarget)
    g.AmbioMonThread.daemon     = True   # must come before daemon start: makes threads stop on exit!
    g.AmbioMonThread.start()

    setIndent(0)
    return msg


def terminateAmbioMon():
    """opposit of init ;-)"""

    defname = "terminateAmbioMon: "

    dprint(defname)
    setIndent(1)

    # shut down thread
    dprint(defname, "stopping thread")
    g.AmbioThreadRun        = False
    g.AmbioMonThread.join()                 # "This blocks the calling thread until the thread
                                            #  whose join() method is called is terminated."

    # verify that thread has ended, but wait not longer than 5 sec (takes 0.006...0.016 ms)
    start = time.time()
    while g.AmbioMonThread.is_alive() and (time.time() - start) < 5:
        pass

    msgalive = "Yes" if g.AmbioMonThread.is_alive() else "No"
    dprint(defname + "thread-status: alive: {}, waiting took:{:0.3f} ms".format(msgalive, 1000 * (time.time() - start)))

    g.Devices["AmbioMon"][g.CONN]  = False

    dprint(defname + "Terminated")
    setIndent(0)


def AmbioMonThreadTarget():
    """Thread triggers readings about every 1 sec"""

    defname = "AmbioMonThreadTarget: "

    while g.AmbioThreadRun:

        # go to sleep until 500ms before next cycle begins
        oldnexttime = g.nexttime
        # sleeptime   = max(0, g.nexttime - time.time() - 0.5)              # sec
        sleeptime   = max(0, g.nexttime - time.time() - 0.2)              # sec
        time.sleep(sleeptime)
        if g.logging: g.AmbioValues = THREAD_AMBIO_fetchVals(g.Devices["AmbioMon"][g.VNAMES])

        # wait until the next cycle has started
        # while oldnexttime == g.nexttime:                            # wait until g.nexttime changes
        #     if not g.AmbioThreadRun: break
        #     time.sleep(0.020)


        # wait until the next cycle has started, but no longer than 0.6 sec
        start = time.time()
        while time.time() - start < 0.6:                            # wait until g.nexttime changes
            if not g.AmbioThreadRun: break
            if g.nexttime > oldnexttime: break
            time.sleep(0.020)

        # # wait until the next cycle has started, but no longer than 0.5 sec
        # start = time.time()
        # while time.time() - start < 0.5:                            # wait until g.nexttime changes
        #     if not g.AmbioThreadRun: break
        #     if g.nexttime > oldnexttime: break
        #     time.sleep(0.020)


def getValuesAmbioMon(varlist):
    """Read all data; return empty dict when not available"""

    start = time.time()
    defname = "getValuesAmbioMon: " # + str(varlist)

    alldata = {}

    # rdprint(defname, "  g.AmbioValues: ", g.AmbioValues)
    if len(g.AmbioValues) > 0:
        for vname in varlist:
            # rdprint(defname, "  vname: ", vname)
            if vname in g.AmbioValues:
                value = g.AmbioValues[vname]
                value = applyValueFormula(vname, value, g.ValueScale[vname], info=defname)
                g.AmbioValues[vname] = g.NAN        # reset after use

                alldata.update({vname: value})

    duration = 1000 * (time.time() - start)
    vprintLoggedValues(defname, varlist, alldata, duration)

    return alldata


def THREAD_AMBIO_fetchVals(varlist):
    """Read all AmbioMon data"""

    ###############################################################
    def getValueAmbioMon(index):
        """check for missing value and return float value"""

        try:
            if data[index] == "":   # missing value
                val = g.NAN
            else:
                try:
                    val = float(data[index])
                except Exception as e:
                    msg = "index: {}".format(index)
                    exceptPrint(e, msg)
                    val = g.NAN
        except Exception as e:
            val = g.NAN

        return val
    ###############################################################

    fetchstart = time.time()

    defname = "THREAD_AMBIO_fetchVals: "

    if g.AmbioDataType == "LAST":  url = _getAmbioUrl() + "/lastdata"
    else:                          url = _getAmbioUrl() + "/lastavg"

    alldata      = {}       # data to be returned
    data         = []       # data read from url as list
    etext        = None     # error_text, used as flag
    ddur         = g.NAN    # default duration of the downloading only
    ddur2        = g.NAN    # default duration of the downloading plus processing
    pread        = b"empty" # page_read
    GLtime       = "empty"  # GeigerLog DateTime like: 2023-11-04 09:32:43

    try:
        mdprint("")
        dstart = time.time()
        # mdprint(defname, "start: '{}'".format(num2datestrMS(dstart)))
        mdprint(defname, "start")

        # rdprint(defname, "delta starts[ms]: ", 1000 * (dstart - fetchstart))
        page   = urllib.request.urlopen(url, timeout=g.AmbioTimeout)        # 40...150 ms, rest < 0.2 ms
        ddur   = 1000 * (time.time() - dstart)
        pread  = page.read()
        data   = pread.decode("UTF-8")
        g.AmbioDataPage = data                                              # used in: AmbioInfo
        data   = data.split(",")
        for i, d in enumerate(data): data[i] = d.strip()                    # clean each value
        GLtime = num2datestr(dstart)                                        # return like: '2023-11-04 10:36:24'
        ddur2  = 1000 * (time.time() - dstart)                              # is <1 ms more than ddur

    except urllib.error.URLError as e:
        exceptPrint(e, "URLError")
        etext = cleanHTML(e.reason)

    except Exception as e:
        exceptPrint(e, "General")
        etext = cleanHTML(e)

    else:
        if g.werbose:
            wprint(defname, "page: geturl : ", page.geturl())   # e.g.  http://10.0.0.85/lastdata
            wprint(defname, "page: getcode: ", page.getcode())  # 200 if ok
            for a, b in page.info().items(): wprint (defname, "page: info:    {:20s}: {}".format(a, b))              # page.info
            for i, a in enumerate(data):     wprint (defname, "data: {:4d}:    {:20s}"   .format(i, a.strip()))      # data
            wprint(defname, "download ambio data: {:0.3f} ms".format(ddur))
            wprint(defname, "total    ambio data: {:0.3f} ms".format(ddur2))

        mdprint(defname, "Dnld-cmpct: {}".format(pread.replace(b"  ", b"").replace(b", ", b",")))
        # mdprint(defname, "pread: len:{}  dnld: {:0.1f} ms  dnldplus: {:0.1f} ms".format(len(pread), ddur, ddur2))

        if not data[0].startswith("1970-01-01"):        # this old date indicates a failure
            #              ,     CPM,     CPS,    Temp,    Press,   Humid,     Airq, Sel, Volt, Save, FreeHp, HpAllc,   BattV,   ChipV,    ADSV,   Avg33, Frq,      Ws,   Hall,               Ambio,                RTC,                  NTP
            # lastdata:    ,     167,   4.000,  24.470,  984.908,  45.343,    0.000,   1,  456,    1, 151552,  86004,   4.988,   3.235,   0.000,   3.213, 240,   0.000,     29, 2023-10-19 10:50:03, 2023-10-19 10:50:02, 2023-10-19 10:50:03
            # lastavg:     ,     167,   2.783,  24.468,  984.930,  45.346,    0.000,   1,  456,    1, 153948,  86004,   4.988,   3.235,   0.000,   3.213, 240,   0.000,     41, 2023-10-19 10:50:03, 2023-10-19 10:50:02, 2023-10-19 10:50:03

            # Basic
                # DateTime                               // 0  DateTime from record (is ignored here)
                # CPM                                    // 1  CPM
                # CPS                                    // 2  CPS

                # Temp                                   // 3  Temp from BME Sensor
                # Press                                  // 4  Press from BME Sensor
                # Humid                                  // 5  Humid from BME Sensor
                # Airq                                   // 6  AirQuality from BME 680 Sensor

            # Extended
                # getAvgDcfg() & 0x03;                   // 7  abc-Selector setting
                # getAvgVolt();                          // 8  Anode Voltage
                # bSavingIsON,                           // 9  Saving status
                # ESP.getFreeHeap(),                     // 10 Free Heap
                # ESP.getMaxAllocHeap(),                 // 11 Max Heap Allocation
                # ESPBattVolt,                           // 12 Batt Voltage (~5V on USB, 3 ... 4.2V by Batt)
                # ESPChipVolt,                           // 13 Chip Voltage (~3.3V)
                # ADSBattVolt,                           // 14 Batt Volt measured by ADS
                # getAvgV33(),                           // 15 Average of ESPChipVolt
                # ESP.getCpuFreqMHz(),                   // 16 CPU Freq
                # ESPLastWs,                             // 17 Energy consumed by device (Ws)
                # hallRead()                             // 18 Hall sensor
                # Ambiotime                              // 19 Ambio DateTime
                # RTCtime                                // 20 RTC DateTime
                # NTPtime                                // 21 NTP DateTime

            # updated with every call for data
            g.AmbioCPUFrequency = getValueAmbioMon(16)
            g.AmbioSelector     = getValueAmbioMon(7)
            g.AmbioVoltage      = getValueAmbioMon(8)

            for vname in varlist:
                if   vname == "CPM":    value = getValueAmbioMon(1)                    # CPM
                elif vname == "CPS":    value = getValueAmbioMon(2)                    # CPS
                elif vname == "CPM1st": value = getValueAmbioMon(1)                    # CPM
                elif vname == "CPS1st": value = getValueAmbioMon(2)                    # CPS

                # elif vname == "CPM2nd": value = getValueAmbioMon(1)                  # CPM
                # elif vname == "CPS2nd": value = getValueAmbioMon(2)                  # CPS

                elif vname == "CPM2nd": value = getAmbioClockDelta(data[21], data[20], UTCcorr=False)   # NTP - RTC clock difference in sec
                elif vname == "CPS2nd": value = getAmbioClockDelta(data[21], GLtime,   UTCcorr=True)    # NTP   clock difference in sec

                elif vname == "CPM3rd": value = getAmbioClockDelta(data[19], GLtime,   UTCcorr=True)    # Ambio clock difference in sec
                elif vname == "CPS3rd": value = getAmbioClockDelta(data[20], GLtime,   UTCcorr=True)    # RTC   clock difference in sec

                elif vname == "Temp":   value = getValueAmbioMon(3)                    # T      from BME280 / BME680
                # elif vname == "Temp":   value = getNTPDateTime()[0] / 1000           # NTP Offset in sec  (offset is single digit ms)

                elif vname == "Press":  value = getValueAmbioMon(4)                    # P      from BME280 / BME680

                elif vname == "Humid":  value = getValueAmbioMon(5)                    # H      from BME280 / BME680
                # elif vname == "Humid":  value = getValueAmbioMon(13)                 # ESP Chip Volt

                # elif vname == "Xtra":   value = getValueAmbioMon(6)                  # X      Air Quality
                # elif vname == "Xtra":   value = getValueAmbioMon(12)                 # ESPBattVolt
                elif vname == "Xtra":   value = getValueAmbioMon(15)                   # ESPChipVolt Avg

                alldata.update({vname: value})

       # failure
    if etext is not None:
        msg  = defname + "'{}' @url:'{}' ".format(etext, url)
        msg += (" (Timeout setting: {} sec)".format(g.AmbioTimeout)) if "timed out" in etext else ""
        edprint(msg)
        QueuePrintDVL(msg)

    duration = 1000 * (time.time() - fetchstart)

    if duration > 1000:
        msg = defname + "Long Dwnld: data:{:0.0f} ms Total:{:0.0f} ms".format(ddur2, duration)
        rdprint(msg)
        QueuePrintDVL(msg)

    print(INVMAGENTA, end="")
    vprintLoggedValues(defname, varlist, alldata, duration)

    return alldata


def THREAD_AMBIO_fetchValsBySerial(varlist):
    """not tested!!!"""

    return

    # calling ESP32 via serial
    rsc = readESP32Serial()
    #print(rsc)
    listrsc = rsc.strip().split(",")
    #print("readESP32Serial: listrsc: ", listrsc)
    try:
        alldata.update({"Temp":       float(listrsc[4])     })   # T   Duration in µs of all shunt actions
        alldata.update({"Press":      float(listrsc[1])     })   # P   CurrentLastADC
        alldata.update({"Humid":      float(listrsc[2])     })   # H   CurrentLastVolt
        if g.FirstLogValuesCall:
            alldata.update({"Xtra":      g.NAN         })   # X   CurrentIntegral - 1st value is wrong
        else:
            alldata.update({"Xtra":      float(listrsc[3])  })   # X   CurrentIntegral
        #raise Exception("test readSerial")
    except Exception as e:
        exceptPrint(e, defname + "readESP32Serial: listrsc: {}".format(listrsc))


def getAmbioClockDelta(DateTimeA, DateTimeB, UTCcorr=False):
    """Delta of time_computer (DateTimeB) minus time_device (DateTimeA) - negative: device is faster"""
    # duration: 0.3 ... 1.1 ms

    from datetime import timezone

    cstart = time.time()

    defname = "getAmbioClockDelta: "
    # mdprint(defname)
    setIndent(1)
    # mdprint(defname, "DateTimeA: >{}<  DateTimeB: >{}<".format(DateTimeA, DateTimeB))

    clock_delta = g.NAN

    try:
        datetime_device    = DateTimeA
        timestamp_device   = mpld.datestr2num(datetime_device)                          # days

        datetime_computer  = DateTimeB
        timestamp_computer = mpld.datestr2num(datetime_computer)                        # days

        if UTCcorr: DefaultUTCcorr = - g.TimeZoneOffset
        else:       DefaultUTCcorr = 0
        # cdprint(defname, "New DefaultUTCcorr: ", DefaultUTCcorr)

        timestamp_delta    = (timestamp_computer - timestamp_device) * 86400 + DefaultUTCcorr # --> sec (plus time offset to UTC)
        # cdprint(defname, "datetime_device: ", datetime_device,   "  timestamp_device: ", timestamp_device, "   Delta: {:0.6f} sec".format(timestamp_delta))

        rounding           = 3                                  # count of decimals
        clock_delta        = round(timestamp_delta, rounding)   # delta time in sec
    except Exception as e:
        exceptPrint(e, defname)

    cdur = 1000 * (time.time() - cstart)
    # mdprint(defname, "Clock Delta is: {:6.3f} s   dur: {:0.1f} ms".format(clock_delta, cdur))

    if abs(clock_delta) > 60000: clock_delta = g.NAN            # when ESP is OFF results are > 1E9! and meaningless
                                                                # time zone delta range is -43200 ... 50400 sec

    setIndent(0)
    return clock_delta


def getInfoAmbioMon(extended=False):
    """Info on the AmbioMon Device"""

    AmbioInfo  = ""
    AmbioInfo += "Configured Connection:        Server IP:Port: '{}:{}'  Timeout: {} sec\n".format(
                                                                                                    g.AmbioServerIP,
                                                                                                    g.AmbioServerPort,
                                                                                                    g.AmbioTimeout
                                                                                                  )

    if not g.Devices["AmbioMon"][g.CONN]: return AmbioInfo + "<red>Device is not connected</red>"

    AmbioInfo       += "Connected Device:             {}\n"                                     .format(g.Devices["AmbioMon"][g.DNAME])
    AmbioInfo       += "CPU Frequency:                {:0.0f} MHz\n"                            .format(g.AmbioCPUFrequency)
    AmbioInfo       += "Geiger tube voltage:          {:0.0f} Volt\n"                           .format(g.AmbioVoltage)
    AmbioInfo       += "Radiation Selector:           {:0.0f}   (1:Alpha+B+G, 2:Beta+G, 3:Gamma)\n"   .format(g.AmbioSelector)
    AmbioInfo       += "Configured Variables:         {}\n"                                     .format(g.AmbioVariables)
    AmbioInfo       += getTubeSensitivities(g.AmbioVariables)

    AmbioInfo       += "Data Type Mode [LAST, AVG]:   {}\n"                                     .format(g.AmbioDataType)
    AmbioInfo       += "\n"
    AmbioInfo       += "AmbioMon++ Configuration:\n"
    AmbioInfo       += "   CPM:                       CPM\n"
    AmbioInfo       += "   CPS:                       CPS\n"
    AmbioInfo       += "   CPM1st:                    CPM\n"
    AmbioInfo       += "   CPS1st:                    CPS\n"
    AmbioInfo       += "   CPM2nd:                    Delta NTP - RTC calculated by GeigerLog\n"
    AmbioInfo       += "   CPS2nd:                    Delta NTP Time to GeigerLog Time [sec]\n"
    AmbioInfo       += "   CPM3rd:                    Delta Ambio Time to GeigerLog Time [sec]\n"
    AmbioInfo       += "   CPS3rd:                    Delta RTC Time to GeigerLog Time [sec]\n"
    AmbioInfo       += "   T:                         Temperature BME280\n"
    AmbioInfo       += "   P:                         Pressure BME280\n"
    AmbioInfo       += "   H:                         ESP Chip Volt\n"
    AmbioInfo       += "   X:                         ESPChipVolt Avg\n"                        # alt: ESP Batt Volt

    if extended == True:
        AmbioInfo   += "\n"
        AmbioInfo   += "Extended Info:\n"
        AmbioInfo   += "   Frequency:                 {} Hz\n"        .format(g.AmbioFrequency)
        AmbioInfo   += "   PWM:                       {}\n"           .format(g.AmbioPwm)
        AmbioInfo   += "   DevID Page:                {}\n"           .format(g.AmbioDevIDPage)
        AmbioInfo   += "   Calib Page:                {}\n"           .format(g.AmbioCalibPage)
        AmbioInfo   += "   Data Page:                 {}\n"           .format(g.AmbioDataPage.replace("  ", ""))

    return AmbioInfo


def pingAmbioServer():
    """
    Ping the AmbioMon Server.
    Remember that a host may not respond to a ping (ICMP) request even if the host name is valid!
    """

    # fprints like:
    #       ==== Pinging AmbioMon Server 10.0.0.56 ===============================================
    #       Ping Result:                  Success, time=191 ms

    setBusyCursor()

    fprint(header("Pinging AmbioMon Server " + g.AmbioServerIP))
    QtUpdate() # to make the header visible right away as ping may take time

    presult, ptime = ping(g.AmbioServerIP)

    pr = "Ping Result:"
    if presult:
        bip()
        fprint (pr, "Success, ", ptime)
    else:
        efprint(pr, "Failure")          # includes burp()

    setNormalCursor()

