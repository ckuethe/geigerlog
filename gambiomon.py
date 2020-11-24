#!/usr/bin/python3
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
__copyright__       = "Copyright 2016, 2017, 2018, 2019, 2020"
__credits__         = [""]
__license__         = "GPL3"

from   gutils           import *
import gsql                             # database handling

###############################################################################
# unusedtools

# not used. raw data are binary
def xxxAMshowDatData():
    """Show AmbioMon type Raw Data (=CSV, ASCII data) from the database table bin"""

    if gglobs.hisConn == None:
        gglobs.exgg.showStatusMessage("No data available")
        return

    fprint(header("Show History Raw Data"))
    hist    = gsql.DB_readBinblob(gglobs.hisConn)
    #print("createLstFromDB: hist:", hist)
    #print("type Hist data: ", type(hist))

    if hist == None:
        fprint("No Dat data found in this database", error=True)
        return

    if isinstance(hist, str):           # data are of type  <class 'str'>
        gglobs.exgg.setBusyCursor()
        fprint(hist)
        gglobs.exgg.setNormalCursor()

    elif isinstance(hist, bytes):       # data are of type <class byte>
        gglobs.exgg.setBusyCursor()

        histsplit = hist.split(b"\n")
        for a in histsplit:
            try:
                fprint(a.decode("UTF-8"))
            except Exception as e:
                fprint(a)
        gglobs.exgg.setNormalCursor()

    else:
        fprint("Cannot read the Dat data; possibly not of AmbioMon origin")


# not used. raw data are binary
def xxxAMsaveHistDatData():
    """get the AmbioMon data from the database and save to *.csv file"""
    # is that needed? can be save to csv anyway

    if gglobs.hisConn == None:
        gglobs.exgg.showStatusMessage("No data available")
        return

    fncname = "AMsaveHistDatData: "
    fprint(header("Save History Raw Data to File"))
    fprint("from: {}\n".format(gglobs.hisDBPath))

    hist    = gsql.DB_readBinblob(gglobs.hisConn)
    if hist == None:
        fprint("No data found in this database", error=True)
        return
    #vprint(fncname + "hist: type: ", type(hist))

    newpath = gglobs.hisDBPath + ".csv"
    if isinstance(hist, str):
        gglobs.exgg.setBusyCursor()
        #fprint(hist)
        writeBinaryFile(newpath, bytes(hist, 'utf-8'))
        gglobs.exgg.setNormalCursor()

    elif isinstance(hist, bytes):
        gglobs.exgg.setBusyCursor()
        #fprint(hist.decode("UTF-8"))
        writeBinaryFile(newpath, hist)
        gglobs.exgg.setNormalCursor()

    vprint(fncname + "saved as file: " + newpath)
    fprint("saved as file: " + newpath)


# not used
def xxxconfigureAmbioMon():
    """Set settings for Ambiomon"""

    if not gglobs.AmbioConnection: return "No connected device"

    dprint("configureAmbioMon:")
    setDebugIndent(1)

    # AM Voltage
    lavolt     = QLabel("Anode voltage [V]\n(0 ... 999 V)")
    lavolt.setAlignment(Qt.AlignLeft)
    avolt  = QLineEdit()
    validator = QDoubleValidator(0, 999, 1, avolt)
    avolt.setValidator(validator)
    avolt.setToolTip('The anode voltage in Volt')
    avolt.setText("{:0.6g}".format(gglobs.AmbioVoltage))

    # AM Cycle Time
    lctime     = QLabel("Cycle time [s]\n(at least 1 s)")
    lctime.setAlignment(Qt.AlignLeft)
    ctime  = QLineEdit()
    validator = QDoubleValidator(0, 999, 1, ctime)
    ctime.setValidator(validator)
    ctime.setToolTip('The cycle time of the AmbioMon device in seconds')
    ctime.setText("{:0.6g}".format(gglobs.AmbioCycletime))

    # AM Frequency
    lfreq     = QLabel("Frequency HV gen [Hz]\n(0 ... 99999 Hz)")
    lfreq.setAlignment(Qt.AlignLeft)
    freq  = QLineEdit()
    validator = QDoubleValidator(0, 99999, 1, freq)
    freq.setValidator(validator)
    freq.setToolTip('The frequency used in the anode voltage generator of the AmbioMon device in Hertz')
    freq.setText("{:0.6g}".format(gglobs.AmbioFrequency))

    # AM PWM
    lpwm     = QLabel("PWM fraction\n(0.000 ... 1.000)")
    lpwm.setAlignment(Qt.AlignLeft)
    pwm  = QLineEdit()
    validator = QDoubleValidator(0.00, 1.00, 1, pwm)
    pwm.setValidator(validator)
    pwm.setToolTip('The Pulse Width Modulation fraction of the AmbioMon device')
    pwm.setText("{:0.6g}".format(gglobs.AmbioPwm))


    # AM Saving
    lsav     = QLabel("Saving data to Flash:\n(Yes/No)")
    lsav.setAlignment(Qt.AlignLeft)
    sav  = QLineEdit()
    #validator = QDoubleValidator(0.00, 1.00, 1, sav)
    #sav.setValidator(validator)
    sav.setToolTip('To switch AmbioMon into saving data mode (Yes/No)')
    sav.setText("{:s}".format(gglobs.AmbioSav))

    graphOptions=QGridLayout()
    graphOptions.setContentsMargins(10,10,10,10) # spacing around the graph options
    graphOptions.addWidget(lavolt,          0, 0)
    graphOptions.addWidget(avolt,           0, 1)
    graphOptions.addWidget(lctime,          1, 0)
    graphOptions.addWidget(ctime,           1, 1)
    graphOptions.addWidget(lfreq,           2, 0)
    graphOptions.addWidget(freq,            2, 1)
    graphOptions.addWidget(lpwm,            3, 0)
    graphOptions.addWidget(pwm,             3, 1)
    graphOptions.addWidget(lsav,            4, 0)
    graphOptions.addWidget(sav,             4, 1)

    # Dialog box
    d = QDialog()       # set parent self to popup in center of geigerlog window
    d.setWindowIcon(gglobs.iconGeigerLog)
    d.setFont(gglobs.fontstd)
    d.setWindowTitle("Configure AmbioMon Device")
    d.setWindowModality(Qt.ApplicationModal)
    #d.setWindowModality(Qt.NonModal)
    #d.setWindowModality(Qt.WindowModal)

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

#### needs to change !!!!!
#        ctime.textChanged.connect(check_state) # last chance
#        ctime.textChanged.emit   (ctime.text())
#######

#TESTING

    #if gglobs.logging:         # no change of parameters when logging
    if 0 and gglobs.logging:    # allow changes even when logging
        setbgcolor = 'QLineEdit {background-color:%s;}' % ("#e0e0e0",)
        gglobs.btn  .setEnabled(False)
        ctime  .setEnabled(False)
        ctime  .setStyleSheet(setbgcolor)
        avolt  .setEnabled(False)
        avolt  .setStyleSheet(setbgcolor)
        freq   .setEnabled(False)
        freq   .setStyleSheet(setbgcolor)
        pwm    .setEnabled(False)
        pwm    .setStyleSheet(setbgcolor)

    retval = d.exec_()
    #print("reval:", retval)

    if retval != 1:
        # ESCAPE pressed or Cancel Button
        dprint("configureAmbioMon: Settings unchanged")

    else:
        # OK pressed

        # change the voltage setting
        oldvoltage = gglobs.AmbioVoltage
        voltage    = avolt.text().replace(",", ".")  #replace comma with dot
        try:
            lc  = round(float(voltage), 0)
            if lc > 999: lc = 999
            if lc < 0:   lc = 0
        except: lc  = oldvoltage
        gglobs.AmbioVoltage = lc

        # change the cycle time
        oldcycletime = gglobs.AmbioCycletime
        cycletime    = ctime.text().replace(",", ".")  #replace comma with dot
        try:
            lc  = round(float(cycletime), 2)
            if lc < 0: lc = 0
        except: lc  = oldcycletime
        gglobs.AmbioCycletime = lc

        # change the frequency
        oldfrequency = gglobs.AmbioFrequency
        frequency    = freq.text().replace(",", ".")  #replace comma with dot
        try:
            lc  = round(float(frequency), 0)
            if lc > 99999: lc = 99999
            if lc < 0:     lc = 0
        except: lc  = oldfrequency
        gglobs.AmbioFrequency = lc

        # change the pwm
        oldpwm = gglobs.AmbioPwm
        pwm    = pwm.text().replace(",", ".")  #replace comma with dot
        try:
            lc  = round(float(pwm), 3)
            if lc > 1: lc = 1
            if lc < 0: lc = 0
        except: lc  = oldpwm
        gglobs.AmbioPwm = lc

        # change the saving mode
        oldpwm = gglobs.AmbioSav
        sav    = sav.text().upper()
        try:
            if   sav == "YES":  lc = "Yes"
            else:               lc = "No"
        except: lc  = oldpwm
        gglobs.AmbioSav = lc

        # per Web http
        tranferSettingsToAMDevice(gglobs.AmbioVoltage, gglobs.AmbioCycletime, gglobs.AmbioFrequency, gglobs.AmbioPwm, gglobs.AmbioSav)

        dprint("configureAmbioMon: new voltage: "       , gglobs.AmbioVoltage)
        dprint("configureAmbioMon: new cycle time: "    , gglobs.AmbioCycletime)
        dprint("configureAmbioMon: new frequency: "     , gglobs.AmbioFrequency)
        dprint("configureAmbioMon: new PWM: "           , gglobs.AmbioPwm)
        dprint("configureAmbioMon: new Saving Mode: "   , gglobs.AmbioSav)

        fprint(header("Configure AmbioMon Device"))
        fprint("Anode voltage setting:" , "{} V"    .format(gglobs.AmbioVoltage))
        fprint("Cycle time setting:"    , "{} s"    .format(gglobs.AmbioCycletime))
        fprint("Frequency HV gen:"      , "{} Hz"   .format(gglobs.AmbioFrequency))
        fprint("PWM fraction:"          , "{}"      .format(gglobs.AmbioPwm))
        fprint("Saving mode:"           , "{}"      .format(gglobs.AmbioSav))

    setDebugIndent(0)


# not used
def xxxtranferSettingsToAMDevice(voltage, cycletime, frequency, pwm, sav):
    """HTTP:  Transfer all settings to the AmbioMon Device"""

    if not gglobs.AmbioConnection: return "No connected device"

    GETString  = ""
    GETString += "?Volt={}"         .format(voltage)
    GETString += "&Cycletime={}"    .format(cycletime)
    GETString += "&Frequency={}"    .format(frequency)
    GETString += "&PWM={}"          .format(pwm)
    GETString += "&saving={}"       .format(sav)

    print("gglobs.AmbioTimeout: ", type(gglobs.AmbioTimeout), gglobs.AmbioTimeout)
    url = _getAmbioUrl() + "/config" + GETString
    page = urllib.request.urlopen(url, timeout=gglobs.AmbioTimeout)
    data = page.read().decode("UTF-8")
    print("data web transfer: ", data)



# unusedtools
###############################################################################


###############################################################################
# gambiomon.py internal use only

def _getAmbioUrl():
    # Port is always 80
    return "http://{}".format(gglobs.AmbioServerIP)


def _getAmbioDevice():
# get the device like 'ESP32-WROOM-Dev' by calling page '/amID' yielding:
# 2020-06-02 09:39:01, ESP32-WROOM-Dev, 10.0.0.85, ambiomon.local, 3

    try:
        url   = _getAmbioUrl() + "/amid"
        page  = urllib.request.urlopen(url, timeout=gglobs.AmbioTimeout)
        data  = page.read().decode("UTF-8").split(",")
    except Exception as e:
        dprint("Failed _getAmbioDevice at url:'{}' with Exception: ".format(url), e, debug=True)
        efprint ("{} Getting AmbioMon Device Identifier @ url:<br>'{}' failed with exception:<br>{}".format(stime(), url, cleanHTML(e)))
        return "NONE"

    return data[1].strip()


def _convertUnixtimeToDateTime(unixtime):
# convert a Unix time in sec into datetime like: 2020-05-10 11:48:50
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


# gambiomon.py use only
###############################################################################

###############################################################################
# Public Functions

def AMmakeHistory(source, device):  # source == "AMDeviceCAM" or "AMDeviceCPS"
    """read the history from an AmbioMon device"""

    fncname = "AMmakeHistory: "

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
    nbytes     = len(devicedata)
    msg        = "Downloaded {:0.1f} kB from {} in {:0.1f} milliseconds ({:0.1f} kB/s)".format(nbytes / 1000, source, dtime * 1000, nbytes/dtime/1000)
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
        upformat = "<BBBL" + "H" * 60
        wprint("Unpack Format: ", upformat)
        for i in range(0, len(devicedata), 127):
            dbuf = devicedata[i : i + 127]
            data = struct.unpack(upformat, dbuf)
            volt = data[2] + 350     # volt is given minus 350 to fit into 1 byte
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
        #~ upformat = "<HBBLLffff"
        upformat = "<BBBLLffff"
        wprint("Unpack Format: ", upformat)
        for i in range(0, len(devicedata), 27):
            dbuf = devicedata[i : i + 27]
            data = struct.unpack(upformat, dbuf)
            volt = data[2] + 350     # volt is given minus 350 to fit into 1 byte
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
        gsql.DB_insertDevice        (gglobs.hisConn, *data_originDB)
        gsql.DB_insertComments      (gglobs.hisConn, dbhisClines)
        gsql.DB_insertComments      (gglobs.hisConn, gglobs.HistoryCommentList)
        gsql.DB_insertData          (gglobs.hisConn, gglobs.HistoryDataList)
        gsql.DB_insertParse         (gglobs.hisConn, gglobs.HistoryParseList)

    # write device data to database
        saveToBin = True
        if saveToBin:   gsql.DB_insertBin(gglobs.hisConn, devicedata)

        fprint("Database is created", debug=gglobs.debug)

    setDebugIndent(0)
    return error, message


def AMsetDeviceIP():
    """Set settings for Ambiomon when in Station mode"""

# setting a server address must be possible without a prior connection, because
# Init fails if IP not accessible

    dprint("AMsetDeviceIP:")
    setDebugIndent(1)

    # AmbioAP_IP
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
    d = QDialog()       # set parent self to pop up in center of geigerlog window
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
        dprint("AMsetDeviceIP: Settings unchanged")

    else:
        # OK pressed
        gglobs.AmbioServerIP = staip.text().strip()

        dprint("AMsetDeviceIP: new IP Address:    ", gglobs.AmbioServerIP)
        fprint(header("Configure AmbioMon WiFi Station Mode"))
        fprint("AmbioMon Station Mode IP:"     , "{}"    .format(gglobs.AmbioServerIP))

    setDebugIndent(0)


def AMsetLogDatatype():
    """Set the datatype GeigerLog will request from Ambiomon (LAST or AVG)"""

    if not gglobs.AmbioConnection: return "No connected device"

    dprint("AMsetLogDatatype:")
    setDebugIndent(1)

    lstaip = QLabel("Data as LAST point value or last AVG value?")
    lstaip.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)

    b0 = QRadioButton("LAST")             # this is default
    b1 = QRadioButton("AVG")

    if gglobs.AmbioDataType == "LAST" : b0.setChecked(True)
    else:                               b1.setChecked(True)

    layoutT = QHBoxLayout()
    layoutT.addWidget(b0)
    layoutT.addWidget(b1)

    b0.setToolTip("Select 'LAST' to get last point of data set, or 'AVG' to get last 1 min average")
    b1.setToolTip("Select 'LAST' to get last point of data set, or 'AVG' to get last 1 min average")

    graphOptions=QGridLayout()
    graphOptions.setContentsMargins(10,10,10,10) # spacing around the graph options
    graphOptions.addWidget(lstaip,          0, 0)
    graphOptions.addLayout(layoutT,         0, 1)

    # Dialog box
    d = QDialog()       # set parent self to popup in center of geigerlog window
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
        b0          .setEnabled(False)
        b1          .setEnabled(False)

    retval = d.exec()
    #print("reval:", retval)

    if retval != 1:
        # ESCAPE pressed or Cancel Button
        dprint("AMsetLogDatatype: Settings unchanged")
    else:
        gglobs.AmbioDataType = "LAST"                   # b0.isChecked()
        if b1.isChecked(): gglobs.AmbioDataType = "AVG" # b1.isChecked()
        dprint("AMsetLogDatatype: Data type: ", gglobs.AmbioDataType)

        fprint(header("Select Data Type Mode"))
        fprint("AmbioMon Data Type:", "{}"    .format(gglobs.AmbioDataType))

    setDebugIndent(0)


def getAmbioMonValues(varlist):
    """Read all AmbioMon data"""

    fncname = "getAmbioMonValues: "

    #~ print(fncname + "({})".format(varlist))

    alldata = {}

    if not gglobs.AmbioConnection: # AmbioMon is NOT connected!
        dprint(fncname + "NO AmbioMon connection")
        return alldata

    if varlist == None:     return alldata

    #setDebugIndent(1)

    #~ start = time.time()
    attempts = 0        # no of attempts to get a connection

    while attempts < 10:
        try:
            if not gglobs.logging:  break
            attempts += 1

            if gglobs.AmbioDataType == "LAST":  url   = _getAmbioUrl() + "/lastdata"
            else:                               url   = _getAmbioUrl() + "/lastavg"

            page  = urllib.request.urlopen(url, timeout=gglobs.AmbioTimeout)
            #print("page: geturl : ", page.geturl())
            #print("page: info   : ", page.info())
            #print("page: getcode: ", page.getcode())
            #~ pi = page.info()
            #~ for a,b in pi.items(): print ("a: ", a, "b: ", b, end="\n")
            #~ print()

            data  = page.read().decode("UTF-8").split(",")
            #~print(fncname, data)
            cpm = float(data[1]) if (float(data[1]) != 4294967295) else gglobs.NAN

            #~alldata.update({"CPM":      float(data[1])      })          # CPM
            alldata.update({"CPM":      cpm                 })          # CPM
            alldata.update({"CPS":      float(data[2])      })          # CPS
            alldata.update({"T":        float(data[3])      })          # T     from BMEX80
            alldata.update({"P":        float(data[4])      })          # P     from BMEX80
            alldata.update({"H":        float(data[5])      })          # H     from BMEX80
            alldata.update({"X":        float(data[6])      })          # Airq  BME680 resistance kOhm (plotted as (LOG10(1/VAL) + 3 )*50)

            #~alldata.update({"CPM1st":   float(data[6])      })          # BME680 resistance kOhm
            #~alldata.update({"CPS1st":   float(data[6])      })          # BME680 resistance kOhm
            alldata.update({"CPM1st":   float(data[11])     })          # FreeHeap
            alldata.update({"CPS1st":   float(data[12])     })          # AllocHeap

            alldata.update({"CPM2nd":   float(data[9])      })          # Chip Voltage
            alldata.update({"CPS2nd":   float(data[10])     })          # Supply Voltage

            alldata.update({"CPM3rd":   float(data[7])      })          # Selector position
            alldata.update({"CPS3rd":   float(data[8])      })          # Anode Voltage

            break

        except Exception as e:
            dprint(fncname + "Failed with Exception: ", e, debug=True)
            if attempts == 10:  playWav("error")
            qefprint("#{}: {}: Reading '{}' failed <br>with exception:  '{}'".format(attempts, stime(), url, cleanHTML(e)))
            qefprint(" Timeout setting: {} sec".format(gglobs.AmbioTimeout))
            Qt_update()
            time.sleep(2) # does a pause help? 0.5 not much; 1 not really

    #~ stop = time.time()
    #~ loadTime = round((stop - start) * 1000, 2)
    #~ alldata.update({"CPM1st":   float(loadTime)     })                  # Overall duration of loading the data set

    #~vprint("{:20s}:  Data:{} ".format(fncname, alldata))
    #setDebugIndent(0)

    return alldata


def getAmbioMonInfo(extended=False):
    """Info on the AmbioMon Device"""

    if not gglobs.AmbioConnection: return "No connected device"

    AmbioInfo = """Connected Device:             '{}'
Configured Variables:         {}
Geiger tube calib. factor:    {:0.1f} CPM/(µSv/h) ({:0.4f} µSv/h/CPM)
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


def terminateAmbioMon():
    """opposit of init ;-)"""

    if not gglobs.AmbioConnection: return

    dprint("terminateAmbioMon: Terminating AmbioMon")

    gglobs.AmbioConnection = False


def initAmbioMon():
    """Initialize """

    fncname = "initAmbioMon: "
    errmsg  = ""

    if not gglobs.AmbioActivation:
        errmsg = "Initialzing AmbioMon not possible as AmbioMon device is not activated in configuration"
        dprint(fncname + errmsg)
        return errmsg

    dprint(fncname + "Initialzing AmbioMon")
    setDebugIndent(1)

    # set configuration
    if gglobs.AmbioServerIP     == "auto":  gglobs.AmbioServerIP     = "ambiomon.local"
    if gglobs.AmbioAP_IP        == "auto":  gglobs.AmbioAP_IP        = "192.168.4.1"
    if gglobs.AmbioTimeout      == "auto":  gglobs.AmbioTimeout      = 2    # 1 sec scheint zu kurz, 5 sec bringt nichts
    if gglobs.AmbioCalibration  == "auto":  gglobs.AmbioCalibration  = 154
    if gglobs.AmbioVariables    == "auto":  gglobs.AmbioVariables    = "CPM, CPS, CPM1st, CPS1st, CPM2nd, CPS2nd, CPM3rd, CPS3rd, T, P, H, X"
    #~if gglobs.AmbioVariables    == "auto":  gglobs.AmbioVariables    = "CPM, CPS, CPM1st, CPS1st, T, P, H, X"
    if gglobs.AmbioDataType     == "auto":  gglobs.AmbioDataType     = "LAST"           # using lastdata call, not avg fpr lastavg
    #~ if gglobs.AmbioDataType     == "auto":  gglobs.AmbioDataType     = "AVG"           # using lastdata call, not avg fpr lastavg
    if gglobs.AmbioSSID         == "auto":  gglobs.AmbioSSID         = "yourSSID"       # SSID of user's WiFi network
    if gglobs.AmbioSSIDPW       == "auto":  gglobs.AmbioSSIDPW       = "yourPassword"   # Password of your SSID WiFi network

    # depending on where the Ambiomon is mapped to, the calibration of those
    # vars must also be set:
    if "1st" in gglobs.AmbioVariables:                      # CPM, CPS, CPM1st, CPS1st
        gglobs.calibration1st = gglobs.AmbioCalibration

    if "2nd" in gglobs.AmbioVariables:                      # CPM2nd, CPS2nd
        gglobs.calibration2nd = gglobs.AmbioCalibration

    if "3rd" in  gglobs.AmbioVariables:                     # CPM3rd, CPS3rd
        gglobs.calibration3rd = gglobs.AmbioCalibration



    gglobs.AmbioDeviceName      = "AmbioMon++"
    gglobs.AmbioDeviceDetected  = _getAmbioDevice()                                      # expect like 'ESP32-WROOM-Dev'

    if gglobs.AmbioDeviceDetected == "NONE":
        errmsg = "<br>No connection to: AmbioServerIP: '{}'".format(gglobs.AmbioServerIP)
        dprint(fncname + errmsg)
        return errmsg

    # connected
    gglobs.AmbioConnection = True
    dprint(fncname + "connected to: AmbioServerIP: '{}', detected device: '{}'".format(gglobs.AmbioServerIP, gglobs.AmbioDeviceDetected))

    # set the loggable variables
    DevVars = gglobs.AmbioVariables.split(",")
    for i in range(0, len(DevVars)):  DevVars[i] = DevVars[i].strip()
    gglobs.DevicesVars["AmbioMon"] = DevVars
    #print("DevicesVars:", gglobs.DevicesVars)

    setDebugIndent(0)
    return errmsg

