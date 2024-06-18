#! /usr/bin/env python3
# -*- coding: UTF-8 -*-

"""
gweb_monserv.py - GeigerLog supports being monitored by smartphones and other computers
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

# NOTE:     http.server.allow_reuse_address = True  # seems to have no effect no matter where I put it???
# config:   in geigerlog.cfg under: [MonServer]

__author__          = "ullix"
__copyright__       = "Copyright 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024"
__credits__         = [""]
__license__         = "GPL3"

from    gsup_utils   import *


def initMonServer(force=False):             # Force=True -> bypass dialogue
    """Init MonServer and set properties"""

    defname = "initMonServer: "

    dprint(defname, "by ", "Auto-Installation" if force else "Dialogue Installation")
    setIndent(1)

    DefaultPortRange = list(range(8080, 8090))                                            # [8080, 8081, ...]

    if g.MonServerThresholds   == "auto":  g.MonServerThresholds   = (0.9, 6.0)           # 2 thresholds: 0.9 µSv/h,  6.0 µSv/h
    if g.MonServerPlotConfig   == "auto":  g.MonServerPlotConfig   = (10, 2, 3)           # 10 min, CPM1st, CPS1st
    if g.MonServerDataConfig   == "auto":  g.MonServerDataConfig   = (1, 3, 10)           # avg period 1, 3, 10 min
    if g.MonServerPorts        == "auto":  g.MonServerPorts        = DefaultPortRange     # 8080 ... 8089

    g.MonServerPlotLength  = g.MonServerPlotConfig[0]
    g.MonServerPlotTop     = g.MonServerPlotConfig[1]
    g.MonServerPlotBottom  = g.MonServerPlotConfig[2]


    oldSettings = ( g.MonServerIsActive,
                    g.GeigerLogIP,
                    g.MonServerPorts,
                    g.MonServerPlotLength,
                    g.MonServerPlotTop,
                    g.MonServerPlotBottom,
                  )

    if force:
        # assume defaults, do NOT call dialogue to request properties
        retval = 99
        g.MonServerIsActive = True

    else:
        # call dialogue to request properties
        retval = setMonServerProperties()

        if g.MonServerPorts == "auto":  g.MonServerPorts = DefaultPortRange
        g.MonServerPlotConfig = ( g.MonServerPlotLength,
                                  g.MonServerPlotTop,
                                  g.MonServerPlotBottom,
                                )

    newSettings = ( g.MonServerIsActive,
                    g.GeigerLogIP,
                    g.MonServerPorts,
                    g.MonServerPlotLength,
                    g.MonServerPlotTop,
                    g.MonServerPlotBottom,
                  )

    msg = ""
    if retval == 0:
        msg += "Cancelled, properties unchanged"
        dprint(defname, msg)

    else:
        # rdprint(defname, "retval: ", retval)
        # rdprint("oldSettings: ", oldSettings)
        # rdprint("newSettings: ", newSettings)

        fprint(header("Monitor Server"))

        if oldSettings == newSettings:
            # no changes
            msg += "No Changes requested\n"

        else:
            # some changes, go activate

            # mdprint(defname, "new go activate: ", newSettings)

            try:
                if g.MonServer is not None:
                    # g.MonServer.shutdown()
                    g.MonServer.socket.close()
                    pass

            except Exception as e:
                exceptPrint(e, defname + "Cannot close MonServer because ...")

            # mdprint(defname, "new go activate: ", "DONE####################################")

            if g.MonServerIsActive:
                NoFreePort = True

                for monport in g.MonServerPorts:
                    # dprint(defname, "Port: ", monport)
                    try:
                        # this is the server for both NON-SSL and SSL
                        g.MonServer         = http.server.ThreadingHTTPServer((g.GeigerLogIP, monport), MyServer)
                        g.MonServer.timeout = 0.3

                        if g.MonServerSSL:
                            # This is the only code needed for SSL, but you MUST provide a PEM file!
                            # Python code for SSL server: https://gist.github.com/timopb/5376bdbd869d4e1e4ae69eacbc9ccbae
                            # make *.pem file: openssl req -x509 -newkey rsa:4096 -keyout geigerlog.pem -out geigerlog.pem -days 365 -nodes
                            context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
                            context.load_cert_chain('gweb/geigerlog.pem')
                            g.MonServer.socket = context.wrap_socket(g.MonServer.socket, server_side=True)

                        # Port is ok; use it
                        g.MonServerPort     = monport
                        g.MonServerIsActive = True
                        NoFreePort          = False
                        gdprint(defname, "Port {} initializes ok and will be used".format(g.MonServerPort))
                        break

                    except OSError as e:
                        g.MonServerIsActive = False
                        errmsg  = "OSError on initialization with Port:{}".format(monport)

                        if e.errno == 98:
                            errmsg += " - Port is already taken!"
                            mdprint(defname, errmsg)
                            if force == False:
                                QueuePrint(errmsg)
                                QueuePrint("Trying next port from list: " + str(g.MonServerPorts))
                        else:
                            exceptPrint(e, "OSError on Port: '{}'".format(monport))
                            QueuePrint(errmsg)
                            QueuePrint("Trying next port from list: " + str(g.MonServerPorts))

                        # g.MonServer.socket.close() # socket had not been opened!

                    except Exception as e:
                        g.MonServerIsActive = False
                        errmsg = "FAILURE, Monitor Server could not be started at port: {}\n".format(monport)
                        exceptPrint(e, defname + errmsg)
                        QueuePrint(errmsg + str(e))
                        # g.MonServer.socket.close() # socket had not been opened!

                if NoFreePort:
                    errmsg = "None of the ports in your list is available, could not start MonServer.<br>Try changing the port number to: auto"
                    QueuePrint(errmsg)
                    rdprint(errmsg)
                    terminateMonServer()
                else:
                    g.MonServerThreadStop    = False
                    g.MonServerThread        = threading.Thread(target = MonServerTarget)
                    g.MonServerThread.daemon = True                                          # daemons will be stopped on exit!
                    g.MonServerThread.start()

            else:
                terminateMonServer()

            if g.MonServerIsActive: icon = "icon_monserver.png"
            else:                   icon = "icon_monserver_inactive.png"
            g.exgg.MonServerAction.setIcon(QIcon(QPixmap(os.path.join(g.resDir, icon))))

        # keylist == ['CPM', 'CPS', 'CPM1st', 'CPS1st', 'CPM2nd', 'CPS2nd', 'CPM3rd', 'CPS3rd', 'Temp', 'Press', 'Humid', 'Xtra']
        keylist = list(g.VarsCopy.keys())
        frmt = "   {:25s}  {}\n"
        msg += "Current settings:\n"
        msg += frmt.format("Autostart:",         g.MonServerAutostart)
        msg += frmt.format("Active State:",      g.MonServerIsActive)
        msg += frmt.format("IP Adress:",         g.GeigerLogIP)
        msg += frmt.format("Port:",              g.MonServerPort)
        msg += frmt.format("RecLength [min]:",   "{:0.6g}".format(g.MonServerPlotLength))
        msg += frmt.format("Top Plot:",          keylist[g.MonServerPlotTop])
        msg += frmt.format("Bottom Plot:",       keylist[g.MonServerPlotBottom])

        # if g.MonServerIsActive:
        #     if force:
        #         QueuePrint("Autostarted Monitor Server at: {}  Port: {}".format(g.GeigerLogIP, g.MonServerPort), color="")
        #     else:
        #         QueuePrint(msg, color="")
        #         QueuePrint("Started Monitor Server at: {}  Port: {}".format(g.GeigerLogIP, g.MonServerPort), color="")
        # else:
        #         QueuePrint("FAILURE starting Monitor Server at: {}  Port: {}".format(g.GeigerLogIP, g.MonServerPort))

        # Do I need QueuePrint ????
        if g.MonServerIsActive:
            if force:
                fprint("Auto-Started Monitor Server at: {}  Port: {}".      format(g.GeigerLogIP, g.MonServerPort))
            else:
                fprint("Started Monitor Server at: {}  Port: {}".           format(g.GeigerLogIP, g.MonServerPort))
                fprint(msg)
        else:
                fprint("Monitor Server is inactive")


    setIndent(1)
    for m in msg.split("\n")[:-1]:
        dprint(defname, m)
    setIndent(0)

    setIndent(0)

    g.exgg.MonServerAction.setToolTip("Set Properties of Monitor Server\nCurrent IP:Port: {} : {}".format(g.GeigerLogIP, g.MonServerPort))


def MonServerTarget():
    """Thread that constantly triggers readings from the port"""

    defname = "MonServerTarget: "

    try:
        while not g.MonServerThreadStop:
            g.MonServer.handle_request()    # this has a timeout of 1 sec; no extra sleep needed
            # rdprint(defname, "in while loop")

    except Exception as e:
        exceptPrint(e, defname + "serve_forever")


def terminateMonServer():
    """terminate all MonServer function"""

    defname = "terminateMonServer: "

    dprint(defname)
    setIndent(1)

    # shut down thread
    dprint(defname, "stopping thread")

    start = time.time()
    g.MonServerThreadStop = True

    # crashes when no config file present
    try:
        g.MonServerThread.join()                 # "This blocks the calling thread until the thread
                                                 #  whose join() method is called is terminated."
    except Exception as e:
        exceptPrint(e, defname)

    else:
        # verify that thread has ended, but wait not longer than 5 sec. !!: up to 400ms seen!
        # start = time.time()
        while g.MonServerThread.is_alive() and (time.time() - start) < 5:
            pass

        msgalive = "is alive" if g.MonServerThread.is_alive() else "NOT alive"
        dprint(defname + "thread-status: {} after:{:0.1f} ms".format(msgalive, 1000 * (time.time() - start)))

        g.MonServer.server_close()

    g.MonServerIsActive = False

    dprint(defname + "Terminated")
    setIndent(0)


def setMonServerProperties():
    """Set all properties"""

    defname = "setMonServerProperties: "

    # set Activation
    lactivate = QLabel("Activate Monitor Server")
    lactivate.setAlignment(Qt.AlignLeft)
    lactivate.setMinimumWidth(200)

    rb01=QRadioButton("Yes")
    rb02=QRadioButton("No")
    rb01.setToolTip("Check 'Yes' to activate")
    rb02.setToolTip("Check 'No' to in-activate")
    rb01.setChecked(True)
    rb02.setChecked(False)

    hbox0=QHBoxLayout()
    hbox0.addWidget(rb01)
    hbox0.addWidget(rb02)
    hbox0.addStretch()

    # set IP
    lMSIP = QLabel("Detected IP Address")
    lMSIP.setAlignment(Qt.AlignLeft)
    MSIP  = QLabel(g.GeigerLogIP)
    MSIP.setToolTip("Auto-detected by GeigerLog")

    # set Port
    lMSPort = QLabel("Port\n(allowed: auto or a single \nvalue from 1024 ... 65535)")
    lMSPort.setAlignment(Qt.AlignLeft)
    MSPort  = QLineEdit()
    MSPort.setToolTip("Enter auto or any number from 1024 to 65535")
    if g.MonServerPort is None: g.MonServerPort = "auto"

    MSPort.setText("{}".format(g.MonServerPort))

    # set Record length in min
    lreclen = QLabel("Length of Record to show [min]\n(allowed: 0.1 to 1500)")
    lreclen.setAlignment(Qt.AlignLeft)
    reclen  = QLineEdit()
    reclen.setToolTip("Enter any number from 0.1 to 1500")
    reclen.setText("{:0.6g}".format(g.MonServerPlotLength))

    # set top graph
    ltopgraph = QLabel("Default Variable for Top Plot")
    ltopgraph.setAlignment(Qt.AlignLeft)
    TopSelect = QComboBox()
    TopSelect.setToolTip('Select the  default Variable for Top Plot')
    TopSelect.setMaxVisibleItems(12)
    for vname in g.VarsCopy:
        TopSelect.addItems([vname])
    TopSelect.setCurrentIndex(g.MonServerPlotTop)

    # set bottom graph
    lbottomgraph = QLabel("Default Variable for Bottom Plot")
    lbottomgraph.setAlignment(Qt.AlignLeft)
    BottomSelect = QComboBox()
    BottomSelect.setToolTip('Select the default Variable for Bottom Plot')
    BottomSelect.setMaxVisibleItems(12)
    for vname in g.VarsCopy:
        BottomSelect.addItems([vname])
    BottomSelect.setCurrentIndex(g.MonServerPlotBottom)

    graphOptions=QGridLayout()
    graphOptions.addWidget(lactivate,      0, 0)
    graphOptions.addLayout(hbox0,          0, 1)
    graphOptions.addWidget(lMSIP,          1, 0)
    graphOptions.addWidget(MSIP,           1, 1)
    graphOptions.addWidget(lMSPort,        2, 0)
    graphOptions.addWidget(MSPort,         2, 1)
    graphOptions.addWidget(lreclen,        3, 0)
    graphOptions.addWidget(reclen,         3, 1)
    graphOptions.addWidget(ltopgraph,      4, 0)
    graphOptions.addWidget(TopSelect,      4, 1)
    graphOptions.addWidget(lbottomgraph,   5, 0)
    graphOptions.addWidget(BottomSelect,   5, 1)

    graphOptions.addWidget(QLabel(""),     6, 0) # empty line

    d = QDialog() # set parent to None to popup in center of screen not in center of window
    d.setWindowIcon(g.iconGeigerLog)
    d.setFont(g.fontstd)
    d.setWindowTitle("Set up Monitor Server")
    d.setMinimumWidth(300)

    # Nanu?
    # d.setWindowModality(Qt.NonModal)          # default alles andere blockiert
    # d.setWindowModality(Qt.WindowModal)       #         alles andere blockiert
    # d.setWindowModality(Qt.ApplicationModal)  #         alles andere blockiert
    # nothing set                               # same:   alles andere blockiert
    # d.setModal(False)                         #         alles andere blockiert!
    # d.setModal(True)                          #         alles andere blockiert

    bbox = QDialogButtonBox()
    bbox.setStandardButtons(QDialogButtonBox.Cancel | QDialogButtonBox.Ok )
    bbox.accepted.connect(lambda: d.done(100))
    bbox.rejected.connect(lambda: d.done(0))

    layoutV = QVBoxLayout(d)
    layoutV.addLayout(graphOptions)
    layoutV.addWidget(bbox)

    retval = d.exec()
    # print(defname + "retval:", retval)

    if retval == 0: # cancel pressed, no changes
        pass

    else:           # ok pressed
        errmsg = ""
        # set MonServer active
        g.MonServerIsActive = True if rb01.isChecked() else False
        # cdprint("g.MonServerIsActive: ", g.MonServerIsActive)

        # set port number
        pn = MSPort.text().strip().lower().replace(",", ".")  #replace any comma with dot
        if pn.lower() == "auto":
            g.MonServerPorts = "auto"
        else:
            try:
                pnumber = int(float(pn))
                if pnumber in range(1024, 65536): g.MonServerPorts = [pnumber]
                else:
                    errmsg += "Illegal Port Number entered; resetting to default 'auto'\n"
                    g.MonServerPorts = "auto"
            except Exception as e:
                g.MonServerPorts = "auto"

        # set record length in min
        try:                    rlen = float(reclen.text().strip().lower().replace(",", "."))  #replace any comma with dot
        except Exception as e:  rlen = 10
        if 0.1 <= rlen <= 1500:
            g.MonServerPlotLength = rlen
        else:
            errmsg += "Illegal Record Length entered; resetting to default '10'\n"
            g.MonServerPlotLength = 10

        # set top var index
        g.MonServerPlotTop = TopSelect.currentIndex()

        # set bottom var index
        g.MonServerPlotBottom = BottomSelect.currentIndex()

        if errmsg > "":
            QueuePrint(header("ERROR Setting Monitor Server"))
            QueuePrint(errmsg)

    return retval


def getLastdataCSV():
    """
    The last collected data record as list
    like: b'2021-10-25 11:26:33,1733.0,36.0,1884.7,30.2,34.0,34.2,34.0,0.0,34.0,32.3,32.0,2.0
    """
#xyz
    defname = "getLastdataCSV: "
    # edprint(defname + "g.lastLogValues: ", g.lastLogValues)

    if g.logging:
        lastrec = "{},".format(stime())
        try:
            for vname in g.lastLogValues:      # ist schneller als join!
                lastrec += "{:0.6g},".format(g.lastLogValues[vname])
        except Exception as e:
            exceptPrint(e, defname + "Data list incomplete")
            lastrec = "Failure during logging," + "nan," * 12  # dummy for: DateTime + 12 nan variables
    else:
        lastrec = "Available when logging," + "nan," * 12      # dummy for: DateTime + 12 nan variables

    # edprint(defname + "return: ", lastrec)

    return bytes(lastrec, "UTF-8") # it does have comma at the end!


def getLastDataAvgCSV(DeltaT): # DeltaT in min
    """Return list with average of all variables for the last DeltaT min plus the added DeltaT as last value
    like: b'2021-10-25 11:39:23,1751.556,31.944,1864.722,30.806,29.667,29.400,29.222,0.444,27.778,27.794,27.611,0.167,3.1'
    """

    defname = "getLastDataAvgCSV: "

    varvalues       = {}
    strdata         = "{},".format(stime())
    DeltaT_found    = DeltaT
    DeltaT_returned = DeltaT
    strnan          = "nan,"

    try:
        for vname in g.VarsCopy:
            strvmean = strnan
            if g.varsSetForLog[vname]:
                # print("vname is in varsSetForLog", vname)

                timedata, vdata, DeltaT_found = getTimeCourseInLimits(vname, DeltaT)

                if not np.isnan(vdata).all():
                    strvmean = "{:0.3f},".format(np.nanmean(vdata)) # at least some data are not nan
                # print("vname: {:6s}  strvmean: {}".format(vname, strvmean))

                if   DeltaT == 1:
                    DeltaT_returned = DeltaT_found

                elif DeltaT == 3:
                    if DeltaT_found <= DeltaT and DeltaT_found > 1:
                        DeltaT_returned = DeltaT_found
                    else:
                        strvmean = strnan
                        DeltaT_returned = 3

                elif DeltaT == 10:
                    if DeltaT_found <= DeltaT and DeltaT_found > 3:
                        DeltaT_returned = DeltaT_found
                    else:
                        strvmean = strnan
                        DeltaT_returned = 10

                else:   # any DeltaT (should not happen!?)
                    DeltaT_returned = DeltaT_found

            strdata += strvmean

    except Exception as e:
        msg = "No proper data available for DeltaT={} min".format(DeltaT)
        exceptPrint(defname + str(e), msg)
        QueuePrint(msg)
        strdata += strnan * 12

    strdata += "{:0.1f}".format(DeltaT_returned)
    # rdprint(defname + "strdata: ", strdata)

    return bytes(strdata, "UTF-8")     # no last comma present


#xyz
def getLastRecords(VarIndex, DeltaT): # VarIndex: 0 ... 11
    """Return records for the last DeltaT min (@1sec cycle and DeltaT=10min -> 600 records)"""
    # like:
    #     DateTime,Value
    #     2022-05-12 09:28:09,15.0
    #     2022-05-12 09:28:10,14.0
    #     2022-05-12 09:28:11,17.0
    #     2022-05-12 09:28:12,13.0
    #     ...

    defname = "getLastRecords: "

    keys  = g.VarsCopy.keys()
    # edprint(defname, list(keys))
    vname = list(keys)[VarIndex]
    # edprint(defname + "VarIndex: ", VarIndex, ", vname: ", vname)

    try:
        tdata, vdata, delta_t = getTimeCourseInLimits(vname, DeltaT)
        tdata = tdata * 86400 - g.TimeZoneOffset
    except Exception as e:
        msg = "No proper data available for DeltaT={} min".format(DeltaT)
        exceptPrint(defname + str(e), msg)
        tdata, vdata = [], []
    # edprint(defname + "len(tdata): ", len(tdata))
    # edprint(defname + "len(vdata): ", len(vdata))
    # edprint("\n", vdata)
    # edprint("\n", tdata)

    if np.isnan(tdata).all() or np.isnan(vdata).all():
        return b""
    else:
        tvdata = "DateTime,Value\n"
        for i in range(len(tdata)):
            tvdata += "{},{}\n".format(num2datestr(tdata[i]), vdata[i])
        # rdprint("tvdata:\n", tvdata)

        return bytes(tvdata, "UTF-8")


def getListTubesSensitivities():
    """Sensitivities for all 4 tube definitions as list, like:  '154,154,2.04,154' """

    defname = "getListTubesSensitivities: "

    sensitlist = ",".join(str(x) for x in g.Sensitivity)
    # cdprint(defname + "return: ",sensitlist)

    return bytes(sensitlist, "UTF-8")


def getWebcodeLastRecord():
    """Prepare Last Rec as table"""

    defname = "getWebcodeLastRecord: "

    splbdata = getLastdataCSV().decode("UTF-8").split(",")
    nbdata   = "<div>Last Data Record:<br>"
    nbdata  += "{}\n".format(splbdata[0])
    if len(splbdata) > 1:
        nbdata  += "<pre style='margin-left:120px; text-align:left;'>\n"
        for i, vname in enumerate(g.VarsCopy):
            val     = splbdata[i + 1]
            sval    = "-" if val == "nan" else val
            nbdata += "{:7s}: {:<}\n".format(vname, sval)
        nbdata += "</pre>"

    bdata    = bytes(nbdata, "UTF-8")

    return bdata


def getWebcodeTubes():
    """The 4 tubes and their sensitivities as a Web page table"""

    defname = "getWebcodeTubes: "

    tubes  = "<div>Tube Sensitivity [CPM / (µSv / h)]:"
    tubes += "<pre style='margin-left:110px; text-align:left;'>\n"
    for i in range(0, 4):
        tubes += "Tube #{} : {}\n".format(i, g.Sensitivity[i])
    tubes += "</pre>"

    return bytes(tubes, "UTF-8")


def getWebcodeOther():
    """record count and cycle time as a Web page table"""

    defname = "getWebcodeOther: "
    sdeltat = "Unknown"

    if g.logTime is not None:
        countinfo = g.logTime.size
        try:
            deltaT = (g.logTime[-1] - g.logTime[0]) * 24 * 60 * 60 # sec
            if   deltaT < 120         : sdeltat = "{:0.0f} sec".format(deltaT)
            elif deltaT < 3600        : sdeltat = "{:0.1f} min".format(deltaT / 60)
            elif deltaT < 3600 * 24   : sdeltat = "{:0.1f} h".format(deltaT / 60 / 60)
            else                      : sdeltat = "{:0.1f} d".format(deltaT / 60 / 60 / 24)
        except Exception as e:
            exceptPrint(e, "no logtime")
    else:
        countinfo = "No active database"

    other  = "<div>Other"
    other += "<pre style='margin-left:60px; text-align:left;'>\n"
    other += "Record Count : {}\n".format(countinfo)
    other += "Log Duration : {}\n".format(sdeltat)
    other += "Cycle time   : {} sec\n".format(g.LogCycle)
    other += "</pre>"

    return bytes(other, "UTF-8")


def getWebcodeDeviceInfo():
    """The non-extended device info"""

    defname = "getWebcodeDeviceInfo: "

    DevInfo = ""
    for a in g.DevVarsAsText:
        if g.DevVarsAsText[a] is not None:
            devs     = g.DevVarsAsText[a].split(" ")
            DevInfo += "{:10s} : {}\n".format(a, devs[0])
            for i in range(1, len(devs)):
                DevInfo += "{:10s} : {}\n".format(" ", devs[i])
    # print(DevInfo)
    if len(DevInfo) == 0:   DevInfo = "    No Connections"

    DevCon  = "<div>Connections"
    DevCon += "<pre style='margin-left:80px; text-align:left;'>\n"
    DevCon += "<b>Devices    : Variables</b>\n"
    DevCon += DevInfo
    DevCon += "</pre>"

    return bytes(DevCon, "UTF-8")


def getWebPage(page):

    # <button class='submit' type='button' onclick='location.href="/graph2"'>
    #     G2
    # </button>
    # <button id='mplgraph'  type='button' onclick="location.href='/glpng'">
    #     GLG
    # </button>

    defname  = "getWebPage: "

    htmlmenu = b"""
<h2><a href='/' style='text-decoration: none; color:darkblue;'>
        <img alt="" style='width:30px; height:30px; vertical-align:top; margin-right:5px;' src='/favicon.ico'>
        GeigerLog Monitor&nbsp;Server
    </a>
</h2>

<h3>
    <button class='submit' type='button' onclick='location.href="/mon"'>
        Monitor
    </button>
    <button class='submit' type='button' onclick='location.href="/plot"'>Plot
    </button>
    <button class='submit' type='button' onclick='location.href="/data"'>
        Data
    </button>
    <button class='submit' type='button' onclick='location.href="/info"'>
        Info
    </button>
</h3>
"""

    htmlmenu += b"""
<p style='margin:5px 5px 10px 5px;'>
    <button id='btnquick' class='startstop' type='button' disabled onclick="fetchRecord('/quicklog')">
        Quick Log
    </button>
    <button id='btnstart' class='startstop' type='button' disabled onclick="fetchRecord('/startlog')">
        Start Log
    </button>
    <button id='btnstop'  class='startstop' type='button' disabled onclick="fetchRecord('/stoplog')">
        Stop Log
    </button>
"""

#xyz
    # get the webpage from file
    filepath = os.path.join(g.progDir, (g.webDir + "/" + page))
    try:
        with open(filepath, "rb") as f:
            fcontent = f.read()
            # print("type fcontent: ", type(fcontent), "\n", fcontent)
    except Exception as e:
        exceptPrint(e, defname + "Cannot read file")
        fcontent = b""

    # insert htmlmenu (header and menu buttons) into web page
    fcontent = fcontent.replace(b"INSERTHTMLMENU", htmlmenu)

    return fcontent


class MyHandler(http.server.BaseHTTPRequestHandler):
    """replacing the log_message function"""

    def log_message(self, format, *args):
        """g.MonServer log message: count(args) = 3"""

        # Example output: 14 13:07:01.248 DEVEL  : ...521 MonServer LogMsg: ('GET /lastdata HTTP/1.1', '200', '-') |
        # cdprint("MonServer LogMsg: {} | {}".format(args, g.MonServerMsg))
        pass


class MyServer(MyHandler):
    """Based on:  http.server.BaseHTTPRequestHandler  """

    def do_GET(self):
        """'do_GET' overwrites class function"""

        defname = "MonServer do_GET: "

        do_get_start        = time.time()

        myresponse          = 200       # ok is normal response
        myheader2           = None      # for 2nd header if needed
        VarName             = ""        # the longname for a variable
        VarIndex            = ""        # the Variable index used in some replacements
        g.MonServerMsg      = ""        # a message to be shown by log_message()


        # GeigerLog main graph as PNG
        if self.path.startswith('/glpng'):
            # time.sleep(120) # getestet bis 120 sec; keine Probleme, Main loop läuft korrekt weiter
            try:
                g.TelegramNeedsPic = True
                start = time.time()
                gotit = False
                while True:
                    time.sleep(0.02)
                    if g.TelegramPicIsReady:
                        gotit = True
                        break
                    if (time.time() - start) > 10:   # allow 10 sec
                        break
                    print(".", end="")

                if gotit: bdata = g.TelegramPicBytes.getvalue()
                else:     bdata = g.iconGeigerLogWeb                   # send GL icon if no real graph available

            except Exception as e:
                exceptPrint(e, defname + "make and get graph pic")

            myheader = "Content-type", "image/png"
            mybytes  = bdata


        # lastdata -  includes status; called by all pages
        elif self.path.startswith("/lastdata"):
            # single line of data,
            # 1 x DateTime, 12 x vars, 4 x sensitivity, 2 x threshold, 1 x LogStatus, 1 x Filestatus
            # like: 2021-10-08 10:01:41, 6.500, 994.786, 997.429, 907.214, 983.857, 892.071, 154,  154,  2.08,  154, 0.9, 6.0, 1, 1

            bdata  = getLastdataCSV()                                          # set DateTime, and add values of all 12 vars
            bdata += getListTubesSensitivities()                               # add the 4 tube sensitivities
            bdata += bytes(",{},{}".format(*g.MonServerThresholds), "UTF-8")   # add the lower, upper Mon limits
            bdata += b",1" if g.logging                   else b",0"           # add logging status
            bdata += b",1" if (g.logDBPath is not None)   else b",0"           # add status file-loaded
            GIndx  = ",{},{}".format(g.MonServerPlotTop, g.MonServerPlotBottom)
            bdata += bytes(GIndx, "utf-8")

            myheader = "Content-type", "text/plain; charset=utf-8"
            mybytes  = bdata

            g.MonServerMsg = str(bdata)


        # lastavgdata -  called by /data once per 10 second
        elif self.path.startswith("/lastavgdata"):
            # single line of data as averages over chunk minutes
            # js: let dataSource = "/lastavg?chunk=" + chunk;
            # return like: 2021-10-08 10:01:41, 6.500, 994.786, 997.429, 907.214, 983.857, 892.071,
            query_components = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)

            DeltaT = 1 # default
            try:
                if "chunk" in query_components: DeltaT = float(query_components["chunk"] [0])
            except: pass

            bdata  = getLastDataAvgCSV(DeltaT)
            bdata += b"," + getListTubesSensitivities()

            myheader = "Content-type", "text/plain; charset=utf-8"
            mybytes  = bdata

            g.MonServerMsg = str(bdata)


        # lastrecs - called by /widget_line; gets all recs in last DeltaT minutes for var VarIndex
        elif self.path.startswith("/lastrecs"):
            query_components = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)

            # set VarIndex ( 0 ... 11 )
            VarIndex = 0
            try:
                if "var" in query_components: VarIndex = int(query_components["var"] [0])
            except Exception as e:
                exceptPrint(e, "getting VarIndex")
            VarIndex = clamp(VarIndex, 0, 11)

            # set DeltaT
            DeltaT = 10                                 # default is 10 min
            try:
                if "dt" in query_components:  DeltaT = float(query_components["dt"] [0])
            except Exception as e:
                exceptPrint(e, "getting DeltaT")
            DeltaT = clamp(DeltaT, 0.1, 1500)           # at least 0.1 min, no more than ~1 day
            # edprint(defname + "path:", self.path, "  query:", query_components, "   VarIndex:", VarIndex, "   DeltaT:", DeltaT)

            bdata  = getLastRecords(VarIndex, DeltaT)

            myheader = "Content-type", "text/plain; charset=utf-8"
            mybytes  = bdata


        # ROOT
        elif self.path == "/":
            g.MonServerWebPage = self.path

            # List of active devices
            wpstr = "<h1 style='margin:20px auto 10px auto'>Devices</h1>"
            for devname in g.Devices:
                if g.Devices[devname][g.ACTIV]:  wpstr += "{}<br>".format(devname)

            # html
            wpbytes  = getWebPage("gwebh_root.html").replace(b"GEIGERLOGVERSION", bytes(g.__version__, "UTF-8"))
            wpbytes += bytes(wpstr, "UTF-8")

            # js
            wpbytes += b"\n<script>"
            wpbytes += getWebPage("gwebj_common.js")
            wpbytes += getWebPage("gwebj_root.js")
            wpbytes += b"</script>"

            myheader = "Content-type", "text/html; charset=utf-8"
            mybytes  = wpbytes


        # MON web page
        elif self.path == "/mon":
            g.MonServerWebPage = self.path

            # html
            wpbytes  = getWebPage("gwebh_mon.html")

            # js
            wpbytes += b"\n<script>"
            wpbytes += getWebPage("gwebj_common.js")
            wpbytes += getWebPage("gwebj_d3gauge.js")
            wpbytes += getWebPage("gwebj_mon.js")
            wpbytes += b"</script>"

            myheader = "Content-type", "text/html; charset=utf-8"
            mybytes  = wpbytes


        # PLOT web page IFRAMEs with widgets
        elif self.path == "/plot":
            g.MonServerWebPage = self.path

            # html
            wpbytes  = getWebPage("gwebh_plot.html");

            # js
            wpbytes += b"\n<script>"
            wpbytes += getWebPage("gwebj_common.js");
            wpbytes += getWebPage("gwebj_plot.js");
            wpbytes += b"</script>"

            myheader = "Content-type", "text/html; charset=utf-8"
            mybytes  = wpbytes


        # DATA web page
        elif self.path == "/data":
            g.MonServerWebPage = self.path

            # html
            wpbytes  = getWebPage("gwebh_data.html")

            # js
            wpbytes += b"\n<script>"
            wpbytes += getWebPage("gwebj_common.js")
            wpbytes += getWebPage("gwebj_data.js")
            wpbytes += b"</script>"

            # replace placeholder for MONSERVERDATACONFIG A, B, C
            wpbytes = wpbytes.replace(b"MONSERVERDATACONFIGA",  bytes(str(g.MonServerDataConfig[0]), "utf-8"))
            wpbytes = wpbytes.replace(b"MONSERVERDATACONFIGB",  bytes(str(g.MonServerDataConfig[1]), "utf-8"))
            wpbytes = wpbytes.replace(b"MONSERVERDATACONFIGC",  bytes(str(g.MonServerDataConfig[2]), "utf-8"))

            myheader = "Content-type", "text/html; charset=utf-8"
            mybytes  = wpbytes


        # INFO web page
        elif self.path == "/info":
            g.MonServerWebPage = self.path

            # html
            wpbytes  = getWebPage("gwebh_info.html")
            wpbytes += getWebcodeLastRecord()
            wpbytes += getWebcodeDeviceInfo()
            wpbytes += getWebcodeTubes()
            wpbytes += getWebcodeOther()

            # js
            wpbytes += b"\n<script>"
            wpbytes += getWebPage("gwebj_common.js")
            wpbytes += getWebPage("gwebj_info.js")
            wpbytes += b"</script>"

            myheader = "Content-type", "text/html; charset=utf-8"
            mybytes  = wpbytes


        # ID
        elif self.path == "/id":
            answer   = "GeigerLog {}".format(g.__version__)

            myheader = 'Content-Type', "text/plain"
            mybytes  = bytes(answer, "UTF-8")


        # WIDGET Demo web page
        elif self.path == "/widget_demo":
            g.MonServerWebPage = self.path

            # html
            wpbytes  = getWebPage("gwebh_w_demo.html")

            # js
            wpbytes += b"\n<script>"
            wpbytes += getWebPage("gwebj_common.js")
            wpbytes += getWebPage("gwebj_w_demo.js")
            wpbytes += b"</script>"

            myheader = "Content-type", "text/html; charset=utf-8"
            mybytes  = wpbytes

#xyz
        # WIDGET GAUGE -- Gauge web page
        elif self.path.startswith("/widget_gauge"):
            # send gauge widget and VarIndex, VarName
            query_components = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)

            # get VarIndex
            VarIndex = 0
            try:
                if "var" in query_components:  VarIndex = int(query_components["var"][0])
            except Exception as e:
                exceptPrint(e, "VarIndex")
            VarIndex = clamp(VarIndex, 0, 11)

            # get VarName
            vname   = list(g.VarsCopy.keys())[VarIndex]
            VarName = g.VarsCopy[vname][0]

            wpbytes  = b""
            if   VarIndex in [0, 2, 4, 6]:                          # CPM *
                wpbytes += getWebPage("gwebh_w_gauge_tube.html")
                js4bytes = getWebPage("gwebj_w_gauge_tube.js")
            elif VarIndex in [1, 3, 5, 7]:                          # CPS * (is handled same as CPM)
                wpbytes += getWebPage("gwebh_w_gauge_tube.html")
                js4bytes = getWebPage("gwebj_w_gauge_tube.js")
            elif VarIndex in [8, 9, 10, 11]:                        # Ambient
                wpbytes += getWebPage("gwebh_w_gauge_amb.html")
                js4bytes = getWebPage("gwebj_w_gauge_amb.js")

            if wpbytes > b"":
                wpbytes += b"\n<script>"
                wpbytes += getWebPage("gwebj_common.js")
                wpbytes += getWebPage("gwebj_d3gauge.js")
                wpbytes += js4bytes
                wpbytes += b"</script>"

                myheader = "Content-type", "text/html; charset=utf-8"
                mybytes  = wpbytes
            else:
                myresponse, myheader, mybytes = getNotFoundResponse()


        # WIDGET LINE -- Line web page
        elif self.path.startswith("/widget_line"):
            # send line widget and VarIndex, VarName
            query_components = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)

            # get VarIndex
            VarIndex = 0
            try:
                if "var" in query_components:  VarIndex = int(query_components["var"][0])
            except Exception as e:
                exceptPrint(e, "VarIndex")
            VarIndex = clamp(VarIndex, 0, 11)

            # get VarName
            vname    = list(g.VarsCopy.keys())[VarIndex]
            VarName  = g.VarsCopy[vname][0]

            # html
            wpbytes = getWebPage("gwebh_w_line_all.html")

            if wpbytes > b"":
                wpbytes += b"\n<script>"
                wpbytes += getWebPage("gwebj_common.js")
                wpbytes += getWebPage("gwebj_d3line.js")
                wpbytes += getWebPage("gwebj_w_line_all.js")
                wpbytes += b"</script>"

                myheader = "Content-type", "text/html; charset=utf-8"
                mybytes  = wpbytes
            else:
                myresponse, myheader, mybytes = getNotFoundResponse()


        # CSS
        elif self.path == "/css":
            # send the css file; allow caching
            myheader  = "Content-type", "text/css; charset=utf-8"
            myheader2 = "Cache-Control", "public, max-age=31536000"
            mybytes   = getWebPage("gwebc.css")


        # favicon
        elif self.path == '/favicon.ico':
            # send the GeigerLog icon; allow caching
            myheader  = "Content-type", "image/png"
            myheader2 = "Cache-Control", "public, max-age=31536000"
            mybytes   = g.iconGeigerLogWeb


        # quick log
        elif self.path == "/quicklog":
            # set flag and set switching to one the MonServer web pages mon, data, graph, info, or widget_demo after 600 ms
            g.quickflag     = True

            answer   = "ok"

            myheader = 'Content-Type', "text/plain"
            mybytes  = bytes(answer, "UTF-8")


        # start log
        elif self.path == "/startlog":
            # set flag and set switching to one the MonServer web pages mon, data, graph, info, or widget_demo after 600 ms
            g.startflag     = True

            answer   = "ok"

            myheader = 'Content-Type', "text/plain"
            mybytes  = bytes(answer, "UTF-8")


        # stop log
        elif self.path == "/stoplog":
            # set flag and set switching to one the MonServer web pages mon, data, graph, info, or widget_demo after 600 ms
            g.stopflag      = True

            answer   = "ok"

            myheader = 'Content-Type', "text/plain"
            mybytes  = bytes(answer, "UTF-8")


        # not found
        else:
            myresponse, myheader, mybytes = getNotFoundResponse()

        # replace placeholder
        mybytes = mybytes.replace(b"VARNAME",                   bytes(    VarName, "utf-8"))
        mybytes = mybytes.replace(b"VARINDEX",                  bytes(str(VarIndex), "utf-8"))
        mybytes = mybytes.replace(b"MONSERVER_REC_LENGTH",      bytes(str(g.MonServerPlotLength), "utf-8"))

        # supress console.log() output when NOT on devel
        if g.devel: suppressconsolelog = b""
        else:       suppressconsolelog = b"console.log = function(){/*suppr*/}"
        mybytes = mybytes.replace(b"SUPPRESSCONSOLELOG", suppressconsolelog)

        try:
            self.send_response(myresponse)
            self.send_header  (*myheader)
            if myheader2 is not None: self.send_header(*myheader2)
            self.end_headers()
            self.wfile.write(mybytes)
        except Exception as e:
            exceptPrint(e, defname + "send & write")

        # durations:
        #   lastData:                       <  2 ms
        #   lastrecs?var=9&dt=10            < 20 ms     # more on FireFox than on Chrome?
        #   lastavgdata?chunk=1 ... 10:     < 50 ms
        #   glpng:                           460 ms bei 67000 recs @ 12 vars, 160 ms bei <100 recs @12 vars
        #   mon:                            <  1 ms
        dur  = 1000 * (time.time() - do_get_start)
        dt   = 0
        myUserAgent = self.headers["User-Agent"]
        if dur > dt:
            browser = "Unknown"
            if "Firefox" in myUserAgent:   browser = "Firefox"
            if "Chrome"  in myUserAgent:   browser = "Chrome"

            mdprint(defname + "{:25s}  client:{}  browser:{:10s}  size:{:6.0f}  dur(>{}ms):{:5.1f} ms".format(
                self.path, self.client_address, browser, len(mybytes), dt, dur))


def getNotFoundResponse():

    wpbytes     = getWebPage("gwebh_root.html").replace(b"GEIGERLOGVERSION", bytes(g.__version__, "UTF-8"))
    wpbytes    += bytes("<h1 style='margin:20px auto 10px auto'>404 Page not found</h1>", "UTF-8")

    myresponse  = 404
    myheader    = "Content-type", "text/html; charset=utf-8"
    mybytes     = wpbytes

    return (myresponse, myheader, mybytes)

