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
# NOTE:     PowerGauge: see: https://github.com/e-tinkers/d3-dashboard-gauge
# config:   in geigerlog.cfg under: [MonServer]

__author__          = "ullix"
__copyright__       = "Copyright 2016, 2017, 2018, 2019, 2020, 2021, 2022"
__credits__         = [""]
__license__         = "GPL3"

from    gsup_utils          import *

dogetmsg = "dummy"                       # dummy; just to have it defined


class MyHandler(http.server.BaseHTTPRequestHandler):
    """replacing the log_message function"""

    def log_message(self, format, *args):
        """gglobs.MonServer log message: count(args) = 3"""

        # for a in args:    print("a: len:{:3d}  '{}'".format(len(a), a))    # no CR or LF included

        # 10:51:29.785 WERBOSE: ...352 MonServer LogMsg: GET /lastdata HTTP/1.1 200 -  /lastdatab'2021-10-25 10:51:29,1733.0,36.0, ...
        wprint("MonServer LogMsg: {} {} {} | {}".format(*args, dogetmsg))


class MyServer(MyHandler):

    def do_GET(self):
        """'do_GET' overwrites class function"""

        global dogetmsg

        fncname = "MonServer do_GET: "

        dogetmsg      = ""
        bExtra = ""
        myheader2     = None

        # when gglobs.MonServer is stopped this is the
        # last dummy call to close it
        if gglobs.MWSThreadStop:
            myheader = "Content-type", "text/html; charset=utf-8"
            mybytes  = b""


        # GeigerLog main graph as PNG
        elif self.path == '/glpng':
            gglobs.flagGetGraph = True
            mybytes             = gglobs.iconGeigerLogWeb # GL icon as default
            if gglobs.picbytes is not None:
                try:
                    mybytes  = gglobs.picbytes.getvalue()
                except Exception as e:
                    exceptPrint(e, "at /glpng")

            myheader = "Content-type", "image/png"


        # lastdata -  called by /mon once per 1 second
        elif self.path.startswith("/lastdata"):
            # single line of data,
            # like: 2021-10-08 10:01:41, 6.500, 994.786, 997.429, 907.214, 983.857, 892.071, 154,  154,  2.08,  154, 0.9, 6.0

            bdata  = getLastdataCSV()                                             # set Datetime, and add values of all 12 vars
            bdata += getListTubesSensitivities()                                  # add the 4 tube sensitivities
            bdata += bytes(",{},{}".format(*gglobs.DoseRateThreshold), "UTF-8")   # add the lower, upper Mon limits
            # rdprint(fncname + str(bdata))

            bExtra = " " + str(bdata)

            myheader = "Content-type", "text/plain; charset=utf-8"
            mybytes  = bdata


        # lastavg -  called by /avg once per 10 second
        elif self.path.startswith("/lastavg"):
            # single line of data, averaged over chunk minutes
            # js: let dataSource = "/lastavg?chunk=" + chunk;
            # like: 2021-10-08 10:01:41, 6.500, 994.786, 997.429, 907.214, 983.857, 892.071,
            query_components = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)

            try:
                if "chunk" in query_components: DeltaT = int(query_components["chunk"] [0])
            except:
                DeltaT = 1 # default

            bdata  = getLastavgCSV(DeltaT)
            bdata += b"," + getListTubesSensitivities()
            bExtra = " " + str(bdata)

            myheader = "Content-type", "text/plain; charset=utf-8"
            mybytes  = bdata


        # root web page
        elif self.path == "/":
            gglobs.MonServerWebPage = self.path
            wpbytes  = getWebPage("gwebh_root.html")
            wpbytes += bytes("<h1 style='margin:60px auto 10px auto'>GeigerLog</h1><h3>Version: {}".format(gglobs.__version__), "UTF-8")

            DevInfo = "<h1>Devices</h1>"
            for devname in gglobs.Devices:
                if gglobs.Devices[devname][ACTIV]:
                    DevInfo += "{}<br>".format(devname)
            wpbytes += bytes(DevInfo, "UTF-8")
            wpbytes += getLoggingStatus()

            myheader = "Content-type", "text/html; charset=utf-8"
            mybytes  = wpbytes


        # Short ID
        elif self.path == "/id":
            answer   = "GeigerLog {}".format(gglobs.__version__)

            myheader = 'Content-Type', "text/plain"
            mybytes  = bytes(answer, "UTF-8")


        # MON web page
        elif self.path == "/mon":
            gglobs.MonServerWebPage = self.path
            wpbytes  = getWebPage("gwebh_mon.html")
            js2bytes = getWebPage("gwebj_common.js")
            js3bytes = getWebPage("gwebj_gauge2.js")
            js4bytes = getWebPage("gwebj_mon.js")
            js4bytes = js4bytes.replace(b"MONSERVERREFRESH", bytes(str((gglobs.MonServerRefresh[0] * 1000)), "utf-8"))
            wpbytes += b"<script>" + js2bytes + js3bytes + js4bytes + b"</script>"
            wpbytes += getLoggingStatus()

            myheader = "Content-type", "text/html; charset=utf-8"
            mybytes  = wpbytes


        # AVG web page
        elif self.path == "/avg":
            gglobs.MonServerWebPage = self.path
            wpbytes  = getWebPage("gwebh_avg.html")
            js1bytes = getWebPage("gwebj_avg.js")
            js1bytes = js1bytes.replace(b"MONSERVERREFRESH", bytes(str((gglobs.MonServerRefresh[1] * 1000)), "utf-8"))
            js2bytes = getWebPage("gwebj_common.js")
            wpbytes += b"<script>" + js1bytes + js2bytes + b"</script>"
            wpbytes += getLoggingStatus()

            myheader = "Content-type", "text/html; charset=utf-8"
            mybytes  = wpbytes


        # GRAPH web page
        elif self.path == "/graph":
            gglobs.MonServerWebPage = self.path
            wpbytes  = getWebPage("gwebh_graph.html")
            wpbytes  = wpbytes.replace(b"MONSERVERREFRESH", bytes(str((int(gglobs.MonServerRefresh[2]))), "utf-8"))
            wpbytes += getLoggingStatus()

            myheader = "Content-type", "text/html; charset=utf-8"
            mybytes  = wpbytes


        # info web page
        elif self.path == "/info":
            gglobs.MonServerWebPage = self.path
            wpbytes  = getWebPage("gwebh_info.html")
            bdata    = getWebcodeLastRecord()
            bdata   += getWebcodeDeviceInfo()
            bdata   += getWebcodeTubes()
            bdata   += getWebcodeOther()
            wpbytes += getLoggingStatus()

            myheader = "Content-type", "text/html; charset=utf-8"
            mybytes  = wpbytes + bdata


        # css
        elif self.path == "/css":
            myheader  = "Content-type", "text/css; charset=utf-8"
            myheader2 = "Cache-Control", "public, max-age=31536000"
            mybytes   = getWebPage("gwebc.css")


        # favicon, glicon
        elif self.path == '/favicon.ico' or self.path == '/glicon':
            myheader  = "Content-type", "image/png"
            myheader2 = "Cache-Control", "public, max-age=31536000"
            mybytes   = gglobs.iconGeigerLogWeb


        # start log
        elif self.path == "/startlog":
            gglobs.startflag = True
            msg      = "<script>setTimeout(function(){window.location.href='%s';}, 600);</script>" % gglobs.MonServerWebPage

            myheader = "Content-type", "text/html; charset=utf-8"
            mybytes  = bytes(msg, "UTF-8")


        # stop log
        elif self.path == "/stoplog":
            gglobs.stopflag = True
            msg      = "<script>setTimeout(function(){window.location.href='%s';}, 600);</script>" % gglobs.MonServerWebPage

            myheader = "Content-type", "text/html; charset=utf-8"
            mybytes  = bytes(msg, "UTF-8")


        # not found
        else:
            wpbytes  = getWebPage("gwebh_root.html")
            wpbytes += bytes("<h1 style='margin:60px auto 10px auto'>404 Page not found</h1>", "UTF-8")
            wpbytes += getLoggingStatus()

            myheader = "Content-type", "text/html; charset=utf-8"
            mybytes  = wpbytes

        dogetmsg = bExtra
        # gdprint(fncname + self.path + bExtra)
        # gdprint(fncname + dogetmsg + " " + str(mybytes))

        self.send_response(200)
        self.send_header(*myheader)
        if myheader2 is not None: self.send_header(*myheader2)
        self.end_headers()

        try:    self.wfile.write(mybytes)
        except: pass


def MWSThreadTarget():
    """Thread that constantly triggers readings from the port"""

    fncname = "gglobs.MWSThreadTarget: "

    # equiv to : gglobs.MonServer.serve_forever()
    # to end, a final call from a client is needed !!!
    while not gglobs.MWSThreadStop:
        if gglobs.MonServer is not None: gglobs.MonServer.handle_request()
        time.sleep(0.01)


def initMonServer(force=False):       # Force=True: bypass dialogue
    """Init MonServer and set properties"""

    fncname = "initMonServer: "
    dprint(fncname)
    setDebugIndent(1)

    gglobs.MonServerIP  = getGeigerLogIP()
    currentMSAddress    = (gglobs.MonServerIP, gglobs.MonServerPort)
    currentMSActiv      = gglobs.MonServerActive

    if force:
        # do NOT call dialogue
        retval = 99
        gglobs.MonServerActive = True

    else:
        # call dialogue to request properties
        retval = setMonServerProperties()

    newMSAddress       = (gglobs.MonServerIP, gglobs.MonServerPort)

    if retval == 0:
        msg = "Cancelled, all properties unchanged"

    else:
        fprint(header("Monitor Server Properties"))
        msg = "Setting up Monitor Server"

        if gglobs.MonServerRefresh == "auto":   gglobs.MonServerRefresh = [1, 10, 3]

        if currentMSAddress == newMSAddress and currentMSActiv == gglobs.MonServerActive:
            # no changes
            msg += " - No Changes requested"
            fprint(msg)
        else:
            # fprint("go and activate")
            msg += " - Activating"

            gglobs.MWSThreadStop    = False
            gglobs.MWSThread        = threading.Thread(target = MWSThreadTarget)
            gglobs.MWSThread.daemon = True                                          # daemons will be stopped on exit!

            if gglobs.MonServerActive:
                try:
                    gglobs.MonServer            = http.server.HTTPServer((gglobs.MonServerIP, gglobs.MonServerPort), MyServer)
                    gglobs.MonServer.timeout    = 2

                except OSError as e:
                    msg = fncname + "OSError: ERRNO:{} ERRtext:'{}'".format(e.errno, e.strerror)
                    exceptPrint(e, msg)
                    edprint(msg)
                    if e.errno == 98:
                        gglobs.MonServerActive = False
                        msg  = "Address IP:Port ({}:{}) is already in use.".format(gglobs.MonServerIP, gglobs.MonServerPort)
                        msg += "\nMonitor Server is in non-active state, please, activate manually."
                        efprint(msg)

                except Exception as e:
                    gglobs.MonServerActive = False
                    msg = "FAILURE, Monitor Server could not be started:\n"
                    exceptPrint(e, fncname + msg)
                    efprint(msg + str(e))

                else:
                    # gglobs.MWSThread.start()
                    pass

                # finally:
                #     print("mist")

                gglobs.MWSThread.start()

            else:
                terminateMonServer()

            if  gglobs.MonServerActive: icon = "icon_monserver.png"
            else:                       icon = "icon_monserver_inactive.png"
            gglobs.exgg.MonServerAction.setIcon(QIcon(QPixmap(os.path.join(gglobs.gresPath, icon))))

            if gglobs.MonServerActive:
                fprint("Active State:",       "ON")
                fprint("IP Adress:Port:",     "{}:{}".format(*newMSAddress))
            else:
                fprint("Active State:",       "OFF")

            msg = "ok, new settings: Active State:{}, Autostart:{}, IP Adress:Port:{}:{}".format(
                        gglobs.MonServerActive,
                        gglobs.MonServerAutostart,
                        gglobs.MonServerIP,
                        gglobs.MonServerPort,
                    )

            gglobs.MonServerIP, gglobs.MonServerPort = newMSAddress

    dprint(fncname + msg)

    setDebugIndent(0)


def setMonServerProperties():
    """Set ..."""

    fncname = "setMonServerProperties: "

    # set Activation
    lactivate = QLabel("Activate Monitor Server")
    lactivate.setAlignment(Qt.AlignLeft)
    lactivate.setMinimumWidth(200)

    rb01=QRadioButton("Yes")
    rb02=QRadioButton("No")
    rb01.setToolTip("Check 'Yes' to activate")
    rb02.setToolTip("Check 'No' to in-activate")
    # if gglobs.MonServerAutostart:
    #     rb01.setChecked(True)
    #     rb02.setChecked(False)
    # else:
    #     rb01.setChecked(False)
    #     rb02.setChecked(True)

    rb01.setChecked(True)
    rb02.setChecked(False)

    hbox0=QHBoxLayout()
    hbox0.addWidget(rb01)
    hbox0.addWidget(rb02)
    hbox0.addStretch()

    # set IP
    lMSIP = QLabel("Detected IP Address")
    lMSIP.setAlignment(Qt.AlignLeft)
    MSIP  = QLabel(gglobs.MonServerIP)
    MSIP.setToolTip("Auto-detected by GeigerLog")

    # set Port
    lMSPort = QLabel("Port\n(allowed: 1024 ... 65535)")
    lMSPort.setAlignment(Qt.AlignLeft)
    MSPort  = QLineEdit()
    MSPort.setToolTip("Any number from 1024 to 65535")
    MSPort.setText("{:d}".format(gglobs.MonServerPort))

    graphOptions=QGridLayout()
    graphOptions.addWidget(lactivate,      0, 0)
    graphOptions.addLayout(hbox0,          0, 1)
    graphOptions.addWidget(lMSIP,          1, 0)
    graphOptions.addWidget(MSIP,           1, 1)
    graphOptions.addWidget(lMSPort,        2, 0)
    graphOptions.addWidget(MSPort,         2, 1)
    graphOptions.addWidget(QLabel(""),     3, 0)

    d = QDialog() # set parent to None to popup in center of screen
    d.setWindowIcon(gglobs.iconGeigerLog)
    d.setFont(gglobs.fontstd)
    d.setWindowTitle("Set up Monitor Server")
    # d.setWindowModality(Qt.WindowModal)
    # d.setWindowModality(Qt.ApplicationModal)
    d.setWindowModality(Qt.NonModal)
    d.setMinimumWidth(300)

    bbox = QDialogButtonBox()
    bbox.setStandardButtons(QDialogButtonBox.Cancel | QDialogButtonBox.Ok )
    bbox.accepted.connect(lambda: d.done(100))
    bbox.rejected.connect(lambda: d.done(0))

    layoutV = QVBoxLayout(d)
    layoutV.addLayout(graphOptions)
    layoutV.addWidget(bbox)

    retval = d.exec()
    # print("retval:", retval)

    if retval == 0: # cancel pressed
        # no change
        pass

    else:   # ok pressed
        # changing
        # gglobs.MonServerAutostart = True if rb01.isChecked() else False
        gglobs.MonServerActive = True if rb01.isChecked() else False
        cdprint("gglobs.MonServerActive: ", gglobs.MonServerActive)

        # port number
        pn      = MSPort.text().replace(",", ".")  #replace any comma with dot
        errmsg  = "Illegal entry: '{}'. Port must be a number from 1024 ... 65535.".format(pn)
        errflag = True
        try:
            pnumber = abs(int(float(pn)))
            if pnumber in range(1024, 65536):
                gglobs.MonServerPort = pnumber
                errflag = False

        except Exception as e:
            pass

        if errflag:
            fprint(header("Set up Monitor Server"))
            efprint(errmsg)
            retval = 0

    return retval


def terminateMonServer():
    """opposit of init ;-)"""

    # NOTE: for thread stopping see:
    # https://www.geeksforgeeks.org/python-different-ways-to-kill-a-thread/
    # damons will be stopped on exit!
    # Using a hidden function _stop() : (note the underscore!)
    # function _stop not working in Py3.9.4:
    # WiFiClientThread._stop() --> results in: AssertionError

    # global gglobs.MWSThread, gglobs.MWSThreadStop

    fncname = "terminateMonServer: "

    dprint(fncname)
    setDebugIndent(1)

    gglobs.MWSThreadStop = True

    # dummy call to satisfy one last gglobs.MonServer.handle_request()
    # gglobs.WiFiClientPort = 8080
    # myurl = "http://{}:{}/?AID=HabeFertig".format(gglobs.WiFiClientIP, gglobs.WiFiClientPort)
    # try:
    #     with urllib.request.urlopen(myurl, timeout=10) as response:
    #         answer = response.read()
    #     filler = " ..." if len(answer) > 100 else ""
    #     dprint("Server Response: ", answer[:100], filler)
    # except Exception as e:
    #     srcinfo = "Bad URL: " + myurl
    #     exceptPrint(fncname + str(e), srcinfo)


    # "This blocks the calling thread until the thread
    #  whose join() method is called is terminated."
    if gglobs.MWSThread.is_alive():
        gglobs.MWSThread.join(3)

        # verify that thread has ended, but wait not longer than 5 sec (takes 0.006...0.016 ms)
        start = time.time()
        while gglobs.MWSThread.is_alive() and (time.time() - start) < 5:
            pass
        dprint(fncname + "thread-status: is_alive: {}, waiting took:{:0.1f}ms".format(gglobs.MWSThread.is_alive(), 1000 * (time.time() - start)))

    else:
        dprint(fncname + "thread is not alive")

    if gglobs.MonServer is not None:
        try:
            gglobs.MonServer
        except NameError:
            rdprint(fncname + "gglobs.MonServer WASN'T defined after all!")
        else:
            # print("gglobs.MonServer: sure, it was defined.")
            gglobs.MonServer.server_close()

    # gglobs.MonServerAutostart = False
    gglobs.MonServerActive = False

    dprint(fncname + "Terminated")
    setDebugIndent(0)


def getLastdataCSV():
    """
    The last collected data record only as list
    like: b'2021-10-25 11:26:33,1733.0,36.0,1884.7,30.2,34.0,34.2,34.0,0.0,34.0,32.3,32.0,2.0
    """

    fncname = "getLastdataCSV: "
    lastrec = "Available when logging," + "nan," * 12  # dummy for: DateTime + 12 variables

    if gglobs.logging:
        strrec = "{},".format(stime())
        try:
            strrec += ",".join(str(gglobs.lastLogValues[vname]) for vname in gglobs.lastLogValues)
            strrec += ","
            lastrec = strrec
        except Exception as e:
            msg = "Data list incomplete"
            exceptPrint(fncname + str(e), msg)
            sys.exit(1)

    # cdprint(fncname + "return: ", lastrec)

    return bytes(lastrec, "UTF-8") # no comma at the end!


def getLastavgCSV(DeltaT): # DeltaT in min
    """Return list with average of all variables for the last DeltaT min
    plus the added DeltaT as last value
    like: b'2021-10-25 11:39:23,1751.556,31.944,1864.722,30.806,29.667,29.400,29.222,0.444,27.778,27.794,27.611,0.167,3.1'
    """

    fncname = "getLastavgCSV: "

    varvalues       = {}
    strdata         = "{},".format(stime())
    DeltaT_found    = DeltaT
    DeltaT_returned = DeltaT
    strnan          = "nan,"

    try:
        for vname in gglobs.varsCopy:
            strvmean = strnan
            # raise Exception("Last Avg testing")

            if gglobs.varsSetForLog[vname]:
                # print("vname is in varsSetForLog", vname)

                vdata, DeltaT_found = getDataInLimits(vname, DeltaT)
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
        exceptPrint(fncname + str(e), msg)
        efprint(msg)
        strdata += strnan * 12

    strdata += "{:0.1f}".format(DeltaT_returned)

    # cdprint(fncname + "strdata: ", strdata)
    return bytes(strdata, "UTF-8")     # no last comma present


def getListTubesSensitivities():
    """Sensitivities for all 4 tube definitions as list, like:  '154,154,2.04,154' """

    fncname = "getListTubesSensitivities: "

    sensitlist = ",".join(str(x) for x in gglobs.Sensitivity)
    # cdprint(fncname + "return: ",sensitlist)

    return bytes(sensitlist, "UTF-8")


def getWebcodeLastRecord():
    """Prepate Last Rec as table"""

    fncname = "getWebcodeLastRecord: "

    splbdata = getLastdataCSV().decode("UTF-8").split(",")
    nbdata   = "<div>Last Data Record:<br>"
    nbdata  += "{}\n".format(splbdata[0])
    if len(splbdata) > 1:
        nbdata  += "<pre style='margin-left:120px; text-align:left;'>\n"
        for i, vname in enumerate(gglobs.varsCopy):
            val     = splbdata[i + 1]
            sval    = "-" if val == "nan" else val
            nbdata += "{:7s}: {:<}\n".format(vname, sval)
        nbdata += "</pre>"

    bdata    = bytes(nbdata, "UTF-8")

    return bdata


def getWebcodeTubes():
    """The 4 tubes and their sensitivities as a Web page table"""

    fncname = "getWebcodeTubes: "

    tubes  = "<div>Tube Sensitivity [CPM / (µSv / h)]:"
    tubes += "<pre style='margin-left:110px; text-align:left;'>\n"
    for i in range(0, 4):
        tubes += "Tube #{} : {}\n".format(i, gglobs.Sensitivity[i])
    tubes += "</pre>"

    return bytes(tubes, "UTF-8")


def getWebcodeOther():
    """record count and cycle time as a Web page table"""

    fncname = "getWebcodeOther: "
    sdeltat = "Unknown"

    if gglobs.logTime is not None:
        countinfo = gglobs.logTime.size
        try:
            deltaT = (gglobs.logTime[-1] - gglobs.logTime[0]) * 24 * 60 * 60 # sec
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
    other += "Cycle time   : {} sec\n".format(gglobs.logCycle)
    other += "</pre>"

    return bytes(other, "UTF-8")


def getWebcodeDeviceInfo():
    """The non-extended device info"""

    fncname = "getWebcodeDeviceInfo: "

    DevInfo = ""
    for a in gglobs.DevVarsAsText:
        if gglobs.DevVarsAsText[a] != None:
            devs     = gglobs.DevVarsAsText[a].split(" ")
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

    fncname  = "getWebPage: "

    htmlmenu1 = b"""
    <h2><a href='/' style='text-decoration: none; color:darkblue;'>
            <img alt="" style='width:30px; height:30px; vertical-align:top; margin-right:5px;' src='/glicon'>
            GeigerLog Monitor&nbsp;Server
        </a>
    </h2>

    <h3>
        <button class='submit' type='button' onclick='location.href="/mon"'>
            Monitor
        </button>
        <button class='submit' type='button' onclick='location.href="/avg"'>
            Data
        </button>
        <button class='submit' type='button' onclick='location.href="/graph"'>
            Graph
        </button>
        <button class='submit' type='button' onclick='location.href="/info"'>
            Info
        </button>
    </h3>

    <p style='margin:5px 5px 10px 5px;'>
        <button id='btnstart' class='startstop' type='button' title="golden on not-logging,\ngrey otherwise" DISABLE onclick="location.href='/startlog'">
            Start Log
        </button>
        <button id='btnstop' class='startstop' type='button' title="golden on logging,\ngrey otherwise" DISABLE onclick="location.href='/stoplog'">
            Stop Log
        </button>
        <!--<button id='loginfo' class='loginfo' type='button' title="green when logging\ngrey otherwise" style='background-color:grey'>
            Log
        </button>-->
    """


    filepath = os.path.join(gglobs.progPath, ("gweb/" + page))

    try:
        with open(filepath, "rb") as f:
            fcontent = f.read()
            # print("type fcontent: ", type(fcontent), "\n", fcontent)

    except Exception as e:
        msg = "Cannot read file"
        exceptPrint(fncname + str(e), msg)
        efprint(msg)
        fcontent = b""

    if gglobs.currentConn is None or gglobs.DevicesConnected == 0:  disable = b"disabled"
    else:                                                           disable = b""

    htmlmenu = htmlmenu1.replace(b"DISABLE", disable)
    fcontent = fcontent.replace(b"INSERTHTMLMENU", htmlmenu)

    return fcontent


def getLoggingStatus():
    stat = """
    <script>
        if (%i){
            document.getElementById("btnstart").disabled = true;
            document.getElementById("btnstop") .style.backgroundColor="#F4D345";
            document.getElementById("btnstop") .disabled = false;
        }
        else{
            document.getElementById("btnstart").style.backgroundColor="#F4D345";
            document.getElementById("btnstart").disabled = false;
            document.getElementById("btnstop") .disabled = true;
        }
    </script>
    """ % gglobs.logging

    return bytes(stat, "UTF-8")

