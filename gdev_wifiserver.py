#! /usr/bin/env python3
# -*- coding: UTF-8 -*-

"""
WiFiServer - calling WiFiServer Devices
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

# http://serverip:port/folder/id         GLID, DeviceName
#                               example: GeigerLog, AmbioMon
# http://serverip:port/folder/lastdata   GLID, CPM, CPS, CPM1st, CPS1st, CPM2nd, CPS2nd,  CPM3rd, CPS3rd, Temp, Press, Humid, Xtra
#                               example: GeigerLog, 100.496, 1.159,,,,,,,25.000, -18.000, 54.000, 97.000
#
# use PHP files on Apache server with Port=80
#
# <?php
# // use for: devid
# $ID      = "GeigerLog";
# $date    = date("Y-m-d H:i:s");
# $devname = "PHP Simulator on Apache";
# echo sprintf("%s, %s, %s", $ID, $date, $devname);
# ?>
#
# <?php
# // use for: /lastdata, /lastavg
# /*
# * makes approx normal dist
# * Alternative of "stats_rand_gen_normal()".
# * "Box–Muller transform" based random deviate generator.
# * @ref https://en.wikipedia.org/wiki/Box%E2%80%93Muller_transform
# *
# * @param  float|int $av Average/Mean
# * @param  float|int $sd Standard deviation
# * @return float
# */
# function rand_pseudo_normal($av, $sd): float
# {
#     $x = mt_rand() / mt_getrandmax();
#     $y = mt_rand() / mt_getrandmax();
#
#     return sqrt(-2 * log($x)) * cos(2 * pi() * $y) * $sd + $av;
# }
#
# function rand_pseudo_poisson($av): float
# {
#     // use with $av >= 10
#     return abs(rand_pseudo_normal($av, sqrt($av)));
# }
#
# $ID     = "GeigerLog";
# $date   = date("Y-m-d H:i:s");
# $CPM    = rand_pseudo_poisson(100);
# $CPS    = rand_pseudo_poisson(1.67);
# $T      = rand( 20, 25);
# $P      = rand(-20, 20);
# $H      = rand( 40, 60);
# $X      = rand( 80, 100);
#
# // GL-cfg: WiFiServer: Option auto defaults to 'CPM, CPS, Temp, Press, Humid'
# echo sprintf("%s, %s, %0.3f, %0.3f,,,,,,,%0.3f, %0.3f, %0.3f, %0.3f", $ID, $date, $CPM, $CPS, $T, $P, $H, $X);
# ?>


__author__          = "ullix"
__copyright__       = "Copyright 2016, 2017, 2018, 2019, 2020, 2021, 2022"
__credits__         = [""]
__license__         = "GPL3"

from   gsup_utils           import *
import gsup_sql                                 # database handling


def initWiFiServer():
    """Initialize WiFiServer"""

    fncname = "initWiFiServer: "

    dprint(fncname + "Initializing WiFiServer")
    setDebugIndent(1)

    # set configuration
    if gglobs.WiFiServerIP          == "auto": gglobs.WiFiServerIP          = getGeigerLogIP()      # GL computer's own IP
    if gglobs.WiFiServerPort        == "auto": gglobs.WiFiServerPort        = 80                    # std Port (0...65535 ok)
    if gglobs.WiFiServerFolder      == "auto": gglobs.WiFiServerFolder      = "DemoWiFiServer"      # folder on WiFiServer device
    if gglobs.WiFiServerTimeout     == "auto": gglobs.WiFiServerTimeout     = 3                     # 1 sec zu kurz, 2 häufig zu kurz, 3 meist ok, 5 sec bringt nichts
    if gglobs.WiFiServerSensitivity == "auto": gglobs.WiFiServerSensitivity = 154                   # same as used for M4011
    if gglobs.WiFiServerDataType    == "auto": gglobs.WiFiServerDataType    = "LAST"                # using 'lastdata' call, not avg for 'lastavg'
    if gglobs.WiFiServerVariables   == "auto": gglobs.WiFiServerVariables   = "CPM, CPS, Temp, Press, Humid"   # simple default

    gglobs.Devices["WiFiServer"][DNAME] = getWiFiServerDeviceName()                                 # request from device

    url = getWiFiServerUrl()

    if gglobs.Devices["WiFiServer"][DNAME] == "NONE":
        # not connected
        gglobs.Devices["WiFiServer"][CONN] = False
        msg = "No connection to Device at URL: '{}'".format(url)
        edprint(fncname + msg)

    else:
        # connected
        gglobs.Devices["WiFiServer"][CONN] = True
        msg  = ""
        dprint(fncname + "connected to Device at URL: '{}', detected name: '{}'".format(url, gglobs.Devices["WiFiServer"][DNAME]))

        setLoggableVariables("WiFiServer", gglobs.WiFiServerVariables)
        setTubeSensitivities(gglobs.WiFiServerVariables, gglobs.WiFiServerSensitivity)

    setDebugIndent(0)

    return msg


def terminateWiFiServer():
    """opposit of init ;-)"""

    fncname = "terminateWiFiServer: "

    dprint(fncname)
    setDebugIndent(1)

    gglobs.Devices["WiFiServer"][CONN] = False

    dprint(fncname + "Terminated")
    setDebugIndent(0)


def getInfoWiFiServer(extended=False):
    """Info on the WiFiServer Device"""

    WiFiInfo  = ""
    WiFiInfo += "Configured Connection:        URL: '{}'   Timeout: {} sec\n".format(getWiFiServerUrl(), gglobs.WiFiServerTimeout)

    if not gglobs.Devices["WiFiServer"][CONN]: return WiFiInfo + "Device is not connected"

    WiFiInfo += "Connected Device:             '{}'\n"         .format(gglobs.Devices["WiFiServer"][DNAME])
    WiFiInfo += "Configured Variables:         {}\n"           .format(gglobs.WiFiServerVariables)
    WiFiInfo += "Configured Tube Sensitivity:  {:0.1f} CPM/(µSv/h) ({:0.4f} µSv/h/CPM)\n".format(gglobs.WiFiServerSensitivity, 1 / gglobs.WiFiServerSensitivity)
    WiFiInfo += "Data Type Mode [LAST, AVG]:   {}\n"           .format(gglobs.WiFiServerDataType)

    if extended == True:
        pass
        # no extended info so far

    return WiFiInfo


def getWiFiServerUrl():
    """get url like 'http://10.0.0.78:8080' """

    url = ("http://{}:{}/{}".format(gglobs.WiFiServerIP, gglobs.WiFiServerPort, gglobs.WiFiServerFolder)).strip()
    # gdprint(url)

    return url


def getWiFiServerDeviceName():
    """get the name of the external device"""

    # request:  http://serverip:port/folder/id
    # response: DeviceName
    #  example: WiFiServer Simulator on Apache PHP

    fncname  = "getWiFiServerDeviceName: "
    devname  = "NONE"
    pagedata = "Empty"
    url      = getWiFiServerUrl() + "/id"
    # gdprint("url: ", url)
    try:
        page     = urllib.request.urlopen(url, timeout=gglobs.WiFiServerTimeout)
        pagedata = page.read()
        # replace < and >; just in case
        devname  = pagedata.strip().decode("UTF-8").replace("<", "&lt;").replace(">", "&gt;")

    except Exception as e:
        msg = fncname + "url: {},  pagedata: {}".format(url, pagedata)
        exceptPrint(e, msg)

    # gdprint("devname: ", devname)

    return devname


def getValuesWiFiServer(varlist):
    """Read all WiFiServer data"""

    # request:  http://serverip:port/folder/lastdata
    # response: CPM, CPS, CPM1st, CPS1st, CPM2nd, CPS2nd,  CPM3rd, CPS3rd, Temp, Press, Humid, Xtra
    #  example: 100.496, 1.159,,,,,,,25.000, 1018.000, 54.000, 97.000

    # local getValue
    def getValue(index):
        """check for missing value and make floats"""

        if data[index] == "":   # missing value
            val = gglobs.NAN
        else:
            try:
                val = float(data[index])
            except Exception as e:
                msg = "index: {}".format(index)
                exceptPrint(e, msg)
                val = gglobs.NAN
        return val


    start = time.time()

    fncname = "getValuesWiFiServer: "

    if gglobs.WiFiServerDataType == "LAST":  url = getWiFiServerUrl() + "/lastdata"
    else:                                    url = getWiFiServerUrl() + "/lastavg"
    # gdprint(fncname + "url:", url)

    alldata      = {}       # data to be returned
    data         = []       # data read from url

    try:
        #raise Exception("test")
        #raise urllib.error.URLError("my dear test")
        try:
            dstart      = time.time()
            page        = urllib.request.urlopen(url, timeout=gglobs.WiFiServerTimeout)
            pagedata    = page.read()
            deltat      = time.time() - dstart

            strdata     = pagedata.strip().decode("UTF-8")
            data        = strdata.split(",")

            # gdprint(fncname + "url: {}  =>  {}".format(url, pagedata))
            # gdprint("data: ", data)

            # download times:
            # from  ???         : 40...120 ms
            # from php simulator: 1 ... 5 ms
            # gdprint(fncname + "download wifi data: {:0.1f} ms".format(deltat * 1000))

        except Exception as e:
            msg = "url: {} data: {}".format(url, data)
            exceptPrint(e, msg)

        if len(data) >= len(gglobs.varsCopy): # must be complete to process
            for i, vname in enumerate(gglobs.varsCopy):
                if vname in varlist:
                    # gdprint("i={}, vname={}, getValue={}".format(i, vname, getValue(i)))
                    alldata.update({vname: getValue(i)})
        else:
            msg = "WiFiServer sent incomplete Data: expecting {} values, got only {}".format(len(gglobs.varsCopy), len(data))
            edprint(msg)
            efprint(msg)

        # gdprint("alldata", alldata)

    except urllib.error.URLError as e:
        exceptPrint(e, fncname)

    except Exception as e:
        exceptPrint(e, fncname)

    printLoggedValues(fncname, varlist, alldata, (time.time() - start) * 1000)

    return alldata


def pingWiFiServer():
    """Ping the WiFiServer"""
    # Remember that a host may not respond to a ping (ICMP) request even
    # if the host name is valid and the host exists!

    setBusyCursor()

    fprint(header("Pinging WiFiServer IP: " + gglobs.WiFiServerIP))
    Qt_update() # to make the header visible right away

    presult, ptime = ping(gglobs.WiFiServerIP)

    pr = "Ping Result:"
    if presult:
        playWav("ok")
        fprint (pr, "Success, ", ptime)
    else:
        efprint(pr, "Failure")

    setNormalCursor()


def setWiFiServerProperties():
    """Set Properties: Data type to request: LAST or AVG"""

    fncname = "setWiFiServerProperties: "

    dprint(fncname)
    setDebugIndent(1)

    # Choose type of data
    lstaip2 = QLabel("Data as <b>LAST</b> value or last <b>AVG</b> value? &nbsp; &nbsp;")
    lstaip2.setAlignment(Qt.AlignLeft )
    b0      = QRadioButton("LAST")             # this is default
    b1      = QRadioButton("AVG")
    ttip    = "Select 'LAST' to get last value of data, or 'AVG' to get last 1 min average of values"
    b0.setToolTip(ttip)
    b1.setToolTip(ttip)
    if    gglobs.WiFiServerDataType == "LAST" : b0.setChecked(True)
    else:                                    b1.setChecked(True)

    # put radiobutton in H box
    layoutRB = QHBoxLayout()
    layoutRB.addWidget(b0)
    layoutRB.addWidget(b1)

    gridl=QGridLayout()
    gridl.setContentsMargins(10,10,10,10) # spacing around
    gridl.addWidget(lstaip2,     0, 0)
    gridl.addLayout(layoutRB,    0, 1)

    # Dialog box
    d = QDialog()
    d.setWindowIcon(gglobs.iconGeigerLog)
    d.setWindowTitle("Set WiFiServer Data Type")
    d.setWindowModality(Qt.WindowModal)
    d.setMinimumWidth(400)

    # Buttons
    bbox = QDialogButtonBox()
    bbox.setStandardButtons(QDialogButtonBox.Cancel | QDialogButtonBox.Ok )
    bbox.accepted.connect(lambda: d.done(1))
    bbox.rejected.connect(lambda: d.done(-1))

    okbtn = bbox.button(QDialogButtonBox.Ok)

    layoutV = QVBoxLayout(d)
    layoutV.addLayout(gridl)
    layoutV.addWidget(bbox)

    if gglobs.logging:         # no change of parameters when logging
        okbtn.setEnabled(False)

    retval = d.exec()
    #print("reval:", retval)

    if retval != 1:
        # ESCAPE pressed or Cancel Button clicked
        dprint(fncname + "Settings unchanged")

    else:
        fprint(header("WiFiServer Data Type"))

        # data type
        if b0.isChecked(): gglobs.WiFiServerDataType = "LAST"    # b0.isChecked()
        else:              gglobs.WiFiServerDataType = "AVG"     # b1.isChecked()
        fprint("WiFiServer Data Type:", "{}".format(gglobs.WiFiServerDataType), debug=True)

    setDebugIndent(0)

