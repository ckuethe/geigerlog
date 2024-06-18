#! /usr/bin/env python3
# -*- coding: UTF-8 -*-

"""
WiFiServer - calling WiFiServer Devices
NOTE: the external device acts as a http-server: you have to browse it for data
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


def initWiFiServer():
    """Initialize WiFiServer"""

    defname = "initWiFiServer: "

    dprint(defname)
    setIndent(1)

    # set configuration
    # g.WiFiServerTimeout   = 0.2 # gibt Warnngen like: DVL 2024-02-19 00:53:02.563 getValuesWiFiSrv #0: NO DATA after 1 trial(s) in 211 ms from http://10.0.0.60:4000/lastdata - Failed readings: 0.042%
                                  # ber eben nur 0.042%
    g.WiFiServerTimeout   = 0.5

    # get url, devicename, connection
    for i in range(len(g.WiFiServerList)):
        if "y" in  g.WiFiServerList[i][0].lower():  # is WiFiServer activated?
            # url on 5
            url = getWiFiServerUrl(g.WiFiServerList[i][1], g.WiFiServerList[i][2], g.WiFiServerList[i][3])
            g.WiFiServerList[i].append(url)

            # name on 6
            name = getDeviceNameWiFiServer(url)
            g.WiFiServerList[i].append(name)

            # connection on 7
            # on device name "NONE" (string) -> failed connection
            g.WiFiServerList[i].append(False if name == "NONE" else True)
        else:
            g.WiFiServerList[i].append("No URL")        # index 5
            g.WiFiServerList[i].append("No Name")       # index 6
            g.WiFiServerList[i].append(False)           # index 7 - (False ==> not connected)


    # get variables
    vprint(defname, "g.WiFiServerList:", g.WiFiServerList)
    VarsComboList = []
    newVarList    = []
    for a in g.WiFiServerList:
        if a[7]:    VarsComboList += a[4]   # select only the variables of connected WiFiServers
    vprint(defname, "VarsComboList:", VarsComboList)

    for vname in g.VarsCopy:
        if vname in VarsComboList: newVarList.append(vname) # sort Vars into GeigerLog order
    g.WiFiServerVariables = ", ".join(newVarList)           # make str from list

    # set device name
    g.Devices["WiFiServer"][g.DNAME] = "WiFiServer Portal"

    # count connected WiFiServers
    connected = 0
    for a in g.WiFiServerList:
        if a[7]:
            connected += 1
            dprint(defname, a)

    if connected > 0:   # at least 1 connected?
        # connected
        g.Devices["WiFiServer"][g.CONN] = True
        msg = ""
        dprint(defname + "{} WiFiServer connected".format(connected))
        g.WiFiServerVariables = setLoggableVariables("WiFiServer", g.WiFiServerVariables)
    else:
        # not connected
        g.Devices["WiFiServer"][g.CONN] = False
        msg = "No connection to any Device"
        rdprint(defname + msg)

    setIndent(0)

    return msg


def terminateWiFiServer():
    """terminating all connections"""
    # nothing has to be done; the httpserver is off by default

    defname = "terminateWiFiServer: "

    dprint(defname)
    setIndent(1)

    g.Devices["WiFiServer"][g.CONN] = False

    dprint(defname + "Terminated")
    setIndent(0)


def getInfoWiFiServer(extended=False):
    """Info on the WiFiServer Device"""

    WiFiInfo  = "Configured Connection:        GeigerLog PlugIn\n"

    if not g.Devices["WiFiServer"][g.CONN]:
        # not connected
        WiFiInfo      += "<red>Device is not connected</red>"
    else:
        # is connected
        wtmplt         = "#{} {:26s} {:9s} {:25s} {}\n"

        WiFiInfo      += "Connected Device:             {}\n".format(g.Devices["WiFiServer"][g.DNAME])
        WiFiInfo      += "\n"
        WiFiInfo      += wtmplt.format("#", "Activated WebServers (URL)", "Status", "Name", "Variables")

        for i, a in enumerate(g.WiFiServerList):
            url        = a[5]
            connect    = "Connected" if a[7] else "Failure"
            name       = a[6].strip()
            vars       = ", ".join(v for v in a[4])
            WiFiInfo  += wtmplt.format(i + 1, url, connect, name, vars)

        WiFiInfo      += "\n"
        WiFiInfo      += "Active Variables:             {}\n"        .format(g.WiFiServerVariables)
        WiFiInfo      += getTubeSensitivities(g.WiFiServerVariables)

    return WiFiInfo


def getWiFiServerUrl(IP, Port, Folder):
    """get url like 'http://10.0.0.78:4000' or 'http://10.0.0.78:4000/folder'"""

    defname = "getWiFiServerUrl: "

    # empty folder MUST NOT have leading "/" in Firefox, but OK in Chrome
    if Folder == "": WSFolder = ""
    else:            WSFolder = "/{}".format(Folder)
    url = "http://{}:{}{}".format(IP, Port, WSFolder)
    vprint(defname, url)

    return url


# calling url for response
def getUrlResponse(url, GET, trials=1):
    """get url antwort"""

    ################################################
    def lcl_exceptMsg(e, excmsg, trial):
        """print the local exception message"""

        exceptPrint(e, defname + excmsg + " url:{} trial: {} of {}".format(url, trial, trials))
        if g.devel:
            dur = 1000 * (time.time() - xstart)
            # QueuePrint("DVL {} {}{:9s}: trial#{} dur:{:0.0f} ms '{}' {}".format(longstime(), defname, excmsg, trial, dur, cleanHTML(e), url))
            # rdprint("DVL {} {}{:9s}: trial#{} dur:{:0.0f} ms '{}' {}".format(longstime(), defname, excmsg, trial, dur, cleanHTML(e), url))
            rdprint("{} {}{:9s}: trial#{} dur:{:0.0f} ms '{}' {}".format(longstime(), defname, excmsg, trial, dur, cleanHTML(e), url))
    ################################################

    gurStart    = time.time()

    defname     = "getUrlResponse: "
    FullURL     = url + GET
    response    = None

    mdprint(defname, FullURL)

    for trial in range(trials):
        xstart = time.time()
        try:
            # urllib.request.urlopen: das dauert 200 ms obwohl timeout mit 100 ms vorgegeben
            #                         das dauert 400 ms obwohl timeout mit 200 ms vorgegeben
            with urllib.request.urlopen(FullURL, timeout=g.WiFiServerTimeout) as page:
                response = page.read().strip().decode("UTF-8")

            # if g.timing:
            #     xdur = 1000 * (time.time() - xstart)
            #     g.ManuValue[2] = xdur
            #     rdprint(defname + "duration: {:5.1f} ms  GET:{} response: ".format(xdur, GET), response)

            if trial >= 1:
                # tmsg = "DVL {} {}{}".format(longstime(), defname, "Success on trial #{}".format(trial))
                tmsg = "{} {}{}".format(longstime(), defname, "Success on trial #{}".format(trial))
                rdprint(tmsg)
                QueuePrint(tmsg)

            break   # break the while loop on successful wifi call

        except TimeoutError as e:
            # NOTE: DEPRECATION:  "exception 'socket.timeout':  A deprecated alias of TimeoutError."
            lcl_exceptMsg(e, 'TimeOutError', trial)

        except urllib.error.HTTPError as e:
            lcl_exceptMsg(e, 'HTTPError', trial)

        except urllib.error.URLError as e:
            # <urlopen error [Errno -2] Name or service not known>
            # <urlopen error [Errno 111] Connection refused>
            # mdprint(defname, "urllib.error.URLError.reason: ", urllib.error.URLError.reason())
            # mdprint(defname, "urllib.error.URLError e: ", e)
            # mdprint(defname, "urllib.error.URLError e: ", e.errno)
            # mdprint(defname, "urllib.error.URLError e: ", e.reason)
            # mdprint(defname, "urllib.error.URLError e: ", e.strerror)
            # mdprint(defname, "urllib.error.URLError e: ", e.filename)
            # if e.errno == 111: time.sleep(0.05) # does it help on conn refused?
            lcl_exceptMsg(e, 'URLError', trial)

        except OSError as e:
            lcl_exceptMsg(e, "OSError", trial)

        except Exception as e:
            lcl_exceptMsg(e, 'Exception', trial)

        # break when cumulative duration reaches half of cycle time
        deltat = time.time() - gurStart
        if deltat > (g.LogCycle * 0.5) :
            edprint(defname, "time is up: {:0.1f} ms".format(1000 * deltat))
            break

        time.sleep(0.01)

    TotalDur = 1000 * (time.time() - gurStart)
    msg = "after {} trial(s) in {:0.0f} ms from {}".format(trial + 1, TotalDur, FullURL)

    return response, msg


# "/lastdata" from all WiFiServer devices
def getValuesWiFiSrvAll(varlist):
    """Read data from all connected WiFiServer devices"""
    # NOTE: varlist is ignored; individual vars for devices is used

    defname = "getValuesWiFiSrvAll: "

    alldata = {}

    for index in range(len(g.WiFiServerList)):
        dev = g.WiFiServerList[index]
        if dev[7]:  alldata = {**alldata, **getValuesWiFiSrv(index, url=dev[5], varlist=dev[4])}

    # get dict into GeigerLog sort order
    alldataOrdered = {}
    for vname in g.VarsCopy:
        if vname in alldata: alldataOrdered.update({vname : alldata[vname]})

    return alldataOrdered


# "/lastdata" for single WiFiServer device
def getValuesWiFiSrv(index, url, varlist):
    """Read all WiFiServer data from a single device"""

    # request : http://serverip:port/folder/lastdata
    # response: CPM, CPS, CPM1st, CPS1st, CPM2nd, CPS2nd,  CPM3rd, CPS3rd, Temp, Press, Humid, Xtra
    # example : 100.496, 1.159,,,,,,,25.000, 1018.000, 54.000, 97.000

    #### local functions ######################################################
    def getValueWiFiServer(index):
        """check for missing value and convert to floats"""

        idata = data[index]
        val   = g.NAN

        if idata > "":   # real value; not a missing value
            try:
                val = float(idata)
            except Exception as e:
                exceptPrint(e, "index: {}".format(index))

        return val
    #### end local functions ##################################################

    gVstart   = time.time()

    defname = "getValuesWiFiSrv #{}: ".format(index)
    alldata = {}                                                                    # dict for return data
    thisGET = "/lastdata"

    # get response on /lastdata
    response, msg = getUrlResponse(url, thisGET, trials=1)
    # rdprint(defname, "url: '{}'  response:'{}'  msg:'{}' ".format(url, response, msg))

    if response is None:
        # got no response
        g.LogReadingsFail += 1
        msg  = defname + "NO DATA " + msg
        msg += " - Failed readings: {:0.3%}".format(g.LogReadingsFail / g.LogReadings)
        # if g.devel: QueuePrint("DVL " + longstime() + " " + msg)
        if g.devel: QueuePrint(longstime() + " " + msg)
        edprint(defname + msg)

    else:
        # got a response
        data = response.split(",")

        if len(data) >= len(g.VarsCopy):
            # got complete set of data
            for i, vname in enumerate(g.VarsCopy):
                if vname in varlist:
                    value = getValueWiFiServer(i)
                    alldata.update({vname: value})
                    # gdprint(defname + "i={}, vname={}, value={}".format(i, vname, value))
        else:
            # got some data but not complete
            msg = defname + "WiFiServer sent incomplete Data: expecting {} values, got only {}".format(len(g.VarsCopy), len(data))
            edprint(msg)
            QueuePrint(msg)

    gVdur = 1000 * (time.time() - gVstart)

    # if g.timing:
    #     g.ManuValue[1] = gVdur

    vprintLoggedValues(defname, varlist, alldata, gVdur)

    return alldata


# id
def getDeviceNameWiFiServer(url):
    """return the name of the external device having URL url"""

    # request url:  http://serverip:port/folder/id
    # return: DeviceName  (example: 'GeigerLog WiFiServer', or: 'WiFiServer Simulator on Apache PHP')
    # dur: 11 ms (GeigerLog on urkam calling Raspi)

    start    = time.time()
    defname  = "getDeviceNameWiFiServer: "

    response, msg = getUrlResponse(url, "/id", trials=3)
    if response is None: devname = "NONE"
    else:                devname = cleanHTML(response)

    dur = 1000 *(time.time() - start)
    if devname == "None":   edprint(defname, "msg:{} dur:{:0.0f} ms".format(msg, dur))
    else:                   vprint (defname, "'{}' dur:{:0.0f} ms"  .format(devname, dur))

    return devname


# reset WiFiServer, but not its Devices
def resetWiFiServer():
    """Reset the WiFiServer, but not its Devices, and only when connected"""

    start = time.time()
    defname  = "resetWiFiServer: "
    setBusyCursor()

    fprint(header("Resetting WiFiServer"))
    QtUpdate()

    command = "/resetserver"

    for i in range(len(g.WiFiServerList)):
        url = g.WiFiServerList[i][5]

        if g.WiFiServerList[i][7]:
            # device reset may take longer than 1 sec!
            oldTimeout = g.WiFiServerTimeout
            g.WiFiServerTimeout = 3
            rdprint(defname, "url: ", url, "  command: ", command)
            response = getUrlResponse(url, command, trials=3)
            if response is None: efprint("{}".format(url), "Failed")
            else:                fprint ("{}".format(url), "Successful")
            g.WiFiServerTimeout = oldTimeout
            QtUpdate()
        else:
            rdprint(defname, "url: ", url, " not connected")

    setNormalCursor()

    dur = 1000 *(time.time() - start)
    vprint(defname, "dur:{:0.0f} ms".format(dur))


def resetWiFiServerDevices():
    """Reset WiFiServer Devices - but only when connected - and not the WiFiServer"""

    start = time.time()
    defname  = "resetWiFiServerDevices: "
    setBusyCursor()

    fprint(header("Resetting Connected WiFiServer Devices"))
    QtUpdate()
    command = "/resetdevices"

    # rdprint(defname, "g.WiFiServerList: ", g.WiFiServerList)
    for i in range(len(g.WiFiServerList)):
        url = g.WiFiServerList[i][5]
        if g.WiFiServerList[i][7]: # connected?
            # rdprint(defname, "url: ", url, "  command: ", command)
            # device reset may take longer than 1 sec!
            oldTO = g.WiFiServerTimeout
            # g.WiFiServerTimeout = 2
            g.WiFiServerTimeout = 5
            response = getUrlResponse(url, command, trials=3)
            if response is None: efprint("{}".format(url), "Failed")
            else:                fprint ("{}".format(url), "Successful")
            g.WiFiServerTimeout = oldTO
            QtUpdate()
        else:
            rdprint(defname, "url: ", url, " not connected")

    setNormalCursor()

    dur = 1000 *(time.time() - start)
    vprint(defname, "dur:{:0.3f} ms".format(dur))


# ping
def pingWiFiServer():
    """Ping the WiFiServer"""

    # NOTE: Remember that a host may not respond to a ping (ICMP) request
    #       even if the host name is valid and the host exists!

    setBusyCursor()

    fprint(header("Pinging WiFiServer"))
    QtUpdate()

    for i in range(len(g.WiFiServerList)):
        if g.WiFiServerList[i][7]:                                     # ping connected devices only
            pr = "Ping Result: IP:{}".format(g.WiFiServerList[i][1])

            presult, ptime = ping(g.WiFiServerList[i][1])
            if presult:
                fprint ("<green>" + pr, "Success in ", ptime)
                bip()
            else:
                efprint(pr, "Failure - ", ptime)

    setNormalCursor()


###############################################################################################################
###############################################################################################################

# A WiFiServer needs to respond to these calls:
# - id
# - lastdata
# - reset
#
# http://serverip:port/folder/id
#                      response:         DeviceName
#                      response example: AmbioMon
# http://serverip:port/folder/lastdata
#                      response:         CPM, CPS, CPM1st, CPS1st, CPM2nd, CPS2nd,  CPM3rd, CPS3rd, Temp, Press, Humid, Xtra
#                      response example: 100.496, 1.159,,,,,,,25.000, -18.000, 54.000, 97.000
# http://serverip:port/folder/reset
#                      response:         <anything>
#                      response example: Ok
#
# Demo code using PHP files on Apache server with Port=80:
#
# <?php
# // use for: id
# $ID      = "GeigerLog";
# $date    = date("Y-m-d H:i:s");
# $devname = "PHP Simulator on Apache";
# echo sprintf("%s, %s, %s", $ID, $date, $devname);
# ?>
#
# <?php
# // use for: /lastdata
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
#
# <?php
# // use for: reset
# echo "Ok";
# ?>
#
# Example code for a HTML-only Server
# Server-Root -> GL ->
#                   -> id
#                       - index.html # Content: 'MyWiFiServer'
#                   -> lastdata
#                       - index.html # Content: '1,2,3,4,5,6,7,8,9,10,11,12'
#                   -> reset
#                       - index.html # Content: 'Ok'
#