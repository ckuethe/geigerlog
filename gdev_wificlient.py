#! /usr/bin/env python3
# -*- coding: UTF-8 -*-

"""
WiFiClient Devices - External devices which call GeigerLog's built-in web server

NOTE: the external device acts as a http-client: it contacts a http-server inside GeigerLog
      Example: GMC counter with WiFi
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

# Port Scanning Example:
# ~$ nmap  10.0.0.20 -p1-65535
#     Starting Nmap 7.80 ( https://nmap.org ) at 2023-04-14 11:23 CEST
#     Nmap scan report ...
#     Host is up (0.000053s latency).
#     Not shown: 65527 closed ports
#     PORT      STATE SERVICE
#     22/tcp    open  ssh
#     80/tcp    open  http                  # Apache or GLrelay.py
#     111/tcp   open  rpcbind
#     1716/tcp  open  xmsg
#     4000/tcp  open  http-alt              # GeigerLog WiFiClient
#     8080/tcp  open  http-proxy            # GeigerLog Monitor Server
#     46099/tcp open  unknown               # GMC counter (may change)
#     48863/tcp open  unknown               # GMC counter (may change)
#
#     Nmap done: 1 IP address (1 host up) scanned in 0.80 seconds


__author__          = "ullix"
__copyright__       = "Copyright 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024"
__credits__         = [""]
__license__         = "GPL3"


from gsup_utils   import *


def initWiFiClient():
    """Initialize WiFiClient"""

    defname            = "initWiFiClient: "
    g.WiFiClientValues = {}
    msg                = ""

    dprint(defname)
    setIndent(1)

    if g.WiFiClientPort == "auto":                  g.WiFiClientPort = 4000      # port 1024 and up

    # set the variables
    # g.WiFiClientType can be only GMC or GENERIC, enforced in gsup_config. GMC is default
    # for GMC
    if g.WiFiClientType == "GMC":
        # rdprint(defname, "g.WiFiClientVariables: ", g.WiFiClientVariables)
        # rdprint(defname, "g.WiFiClientMapping: ",   g.WiFiClientMapping)

        if g.WiFiClientMapping == "auto":           g.WiFiClientMapping = "CPM:CPM"

        try:
            for a in g.WiFiClientMapping.split(","):
                asp = a.replace(" ", "").split(":")
                g.WiFiClientVariablesMap.update({asp[0] : asp[1]})
        except Exception as e:
            exceptPrint(e, defname + "set Type 'GMC' variables")
            g.WiFiClientMapping      = "CPM:CPM"
            g.WiFiClientVariablesMap = {"CPM":"CPM"}

        g.WiFiClientVariables = ", ".join(g.WiFiClientVariablesMap) # join the keys only

    # for GENERIC
    else:
        if g.WiFiClientVariables == "auto":     g.WiFiClientVariables = "CPM, CPS, Temp, Press, Humid"
        g.WiFiClientMapping = "GeigerLog Default"

    g.WiFiClientVariables = setLoggableVariables("WiFiClient", g.WiFiClientVariables)


    # housekeeping
    g.Devices["WiFiClient"][g.DNAME] = "WiFiClient " + g.WiFiClientType
    g.Devices["WiFiClient"][g.CONN]  = True
    dprint(defname + "connected to: IP:Port '{}:{}', detected device: '{}'".format(
                                                g.GeigerLogIP,
                                                g.WiFiClientPort,
                                                g.Devices["WiFiClient"][g.DNAME]))

    # create the web server
    try:
        g.WiFiClientServer = http.server.ThreadingHTTPServer    ((g.GeigerLogIP, g.WiFiClientPort), WiFiClientServer)
        g.WiFiClientServer.timeout = 3
        dprint(defname + "WiFiClient HTTPServer listening at: http://%s:%s" % (g.GeigerLogIP, g.WiFiClientPort))

    except OSError as e:
        exceptPrint(e, "")
        msg0 = "WiFiClientServer could not be started, because "
        if e.errno == 98:   msg = (False, msg0 + "Port number {} is already in use".format(g.WiFiClientPort))
        else:               msg = (False, msg0 + "of OS.Error: {}".format(e.errno))

    except Exception as e:
        msg = "Unexpected Failure - WiFiClientServer could not be started"
        exceptPrint(e, msg)
        efprint(e)
        qefprint(msg)

    else:
        g.WiFiClientThread = threading.Thread(target=WiFiClientThreadTarget)
        g.WiFiClientThread.daemon = True        # daemons will be stopped on exit!
        g.WiFiClientThread.start()

    setIndent(0)
    return msg


def WiFiClientThreadTarget():
    """Thread that constantly triggers readings from the HTTP Server"""

    defname = "WiFiClientThreadTarget: "

    try:
        g.WiFiClientServer.serve_forever()
    except Exception as e:
        exceptPrint(e, defname + "serve_forever")


def terminateWiFiClient():
    """terminate all WiFiClient function"""

    defname = "terminateWiFiClient: "

    dprint(defname)
    setIndent(1)

    if g.WiFiClientServer is not None:
        g.WiFiClientServer.server_close()

    g.Devices["WiFiClient"][g.CONN] = False

    dprint(defname + "Terminated")
    setIndent(0)


def getInfoWiFiClient(extended=False):
    """Info on the WiFiClient Device"""

    WiFiInfo  = ""
    WiFiInfo += "Configured Connection:        Server IP:Port: '{}:{}'\n"      .format(g.GeigerLogIP, g.WiFiClientPort)

    if not g.Devices["WiFiClient"][g.CONN]: return WiFiInfo + "<red>Device is not connected</red>"

    WiFiInfo += "Connected Device:             {}\n"         .format(g.Devices["WiFiClient"][g.DNAME])
    WiFiInfo += "Configured Device Type:       {}\n"         .format(g.WiFiClientType)
    WiFiInfo += "Configured Variables:         {}\n"         .format(g.WiFiClientVariables)
    WiFiInfo += "Configured Mapping:           {}\n"         .format(g.WiFiClientMapping)
    WiFiInfo += getTubeSensitivities(g.WiFiClientVariables)

    if extended == True:
        WiFiInfo += ""

    return WiFiInfo


def getValuesWiFiClient(varlist):
    """Read and return all WiFiClient data"""

    #############################################################################
    # inner function
    def getValueWiFiClient(valname):
        """check for missing value in WiFiClient data and return floats; missing data as NAN"""

        val    = g.NAN
        try:
            rawval = g.WiFiClientValues[valname]
        except Exception as e:
            # exceptPrint(e, defname)
            return val

        if  rawval > "":                                    # not a missing value
            try:                    val = float(rawval)
            except Exception as e:  exceptPrint(e, "valname: {}".format(valname))

        val = applyValueFormula(vname, val, g.ValueScale[vname])

        return val
    # end inner function
    #############################################################################


    start   = time.time()
    defname = "getValuesWiFiClient: "
    alldata = {}                        # data to be returned

    # GMC
    if g.WiFiClientType == "GMC":
        for vname in varlist:
            # print("vname: ", vname, "  varlist: ", varlist)
            if vname in g.WiFiClientVariablesMap:
                key = g.WiFiClientVariablesMap[vname]
                alldata.update({vname: getValueWiFiClient(key)})

    # GENERIC
    else:
        for vname in varlist:
            # print("vname: ", vname, "  varlist: ", varlist)
            if   vname in g.WiFiClientValues:
                alldata.update({vname:  getValueWiFiClient(vname)})

    g.WiFiClientValues = {}  # reset

    vprintLoggedValues(defname, varlist, alldata, (time.time() - start) * 1000)

    return alldata


class WiFiClientHandler(http.server.BaseHTTPRequestHandler):

    def log_message(self, format, *args):
        """replacing the log_message function"""
        # not used

        # strarg: like:  GET /GMC?AID=01234&GID=12345678901&CPM=44&ACPM=46&uSV=0.30 HTTP/1.1, 200, -
        # strarg = ", ".join(args)    # count(args) = 3 (except on errors)
        # rdprint(strarg)
        pass


class WiFiClientServer(WiFiClientHandler):

    def do_GET(self):
        """'do_GET' overwrites class function"""

        ######## this is the only place with these details #################################################################
        # when calling with: http://10.0.0.20:4000/log2.asp?CPM=44&AID=karl&GID=12345&ACPM=46&uSV=0.30
        #
        # vprint("self.path: ",               self.path)              # /log2.asp?CPM=44&AID=karl&GID=12345&ACPM=46&uSV=0.30
        # vprint("self.command: ",            self.command)           # GET
        # vprint("self.client_address: ",     self.client_address)    # ('10.0.0.20', 60856)
        # vprint("self.server: ",             self.server)            # <http.server.ThreadingHTTPServer object at 0x7f0fbd160a00>
        # vprint("self.close_connection: ",   self.close_connection)  # True
        # vprint("self.requestline: ",        self.requestline)       # GET /log2.asp?CPM=44&AID=karl&GID=12345&ACPM=46&uSV=0.30 HTTP/1.1
        # vprint("self.responses: ",          self.responses)         # {<HTTPStatus.CONTINUE: 100>: ('Continue', 'Request received, please continue'), <and much more>
        # vprint("self.handle(): ",           self.handle())          # None
        # vprint("self.version_string(): ",   self.version_string())  # BaseHTTP/0.6 Python/3.9.4
        # vprint("self.headers: ",            self.headers)           # Host: 10.0.0.20:4000
        #                                                             # Connection: keep-alive
        #                                                             # Cache-Control: max-age=0
        #                                                             # DNT: 1
        #                                                             # Upgrade-Insecure-Requests: 1
        #                                                             # User-Agent: Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.72 Safari/537.36
        #                                                             # Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9
        #                                                             # Accept-Encoding: gzip, deflate
        #                                                             # Accept-Language: en-US,en;q=0.9,de;q=0.8
        ###################################################################################################################


        defname = "WiFiClientServer GET call: "

        if not g.logging: return

        # mdprint("")
        mdprint(defname + "path:   " + self.path)

        # send favicon.ico
        if self.path == '/favicon.ico':
            myheader    = 'Content-Type', 'image/png'
            mybytes     = g.iconGeigerLogWeb
            myresponse  = 200


        # send Root page
        elif self.path == "/":
            answer  = """
            <!DOCTYPE html>
            <html lang='en'>
            <meta name='viewport' content='width=device-width, initial-scale=1.0, user-scalable=yes'>
            <meta charset='utf-8' />\n
            <style>html  {font-family:Helvetica; display:inline-block; margin:0px auto; text-align:center; font-size:20px;}</style>\n
            <img style='width:100px; height:100px;' src='favicon.ico'>
            <h3>I am<br>GeigerLog's Web Server,<br>waiting for <h2>WiFiClient Devices</h2> to call me at:</h3>\n
            <p>%s</p>
            <p>GeigerLog Version: %s
            """ % (self.headers.get("Host"), g.__version__)

            myheader    = 'Content-Type', "text/html"
            mybytes     = bytes(answer.strip().replace("  ", ""), "UTF-8")
            myresponse  = 200


        # either GENERIC or GMC, nothing else possible as WiFiClientType is limited to those
        elif self.path.startswith("/" + g.WiFiClientType):  # thus the not-configured Type will be irgnored!
            query_components = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query, max_num_fields=20)
            # like: for GMC:  query_components: {'AID': ['01234'], 'GID': ['12345678901'], 'CPM': ['44'], 'ACPM': ['46'], 'uSV': ['0.30']}

            if self.path.startswith("/GENERIC"):
                # Generic Device was configured
                # url : http://10.0.0.20:4000/GENERIC?M=10&S=11&M1=12&S1=13&M2=14&S2=15&M3=16&S3=17&T=18&P=19&H=20&X=21

                for vname in g.VarsCopy:
                    vsvname = g.VarsCopy[vname][1]
                    if vsvname in query_components: g.WiFiClientValues[vname] = query_components[vsvname][0]

                answer = "OK from GeigerLog to WiFiClient Generic"

            elif self.path.startswith("/GMC"):
                # GMC device was configured
                # url : http://10.0.0.20:4000/GMC?AID=01234&GID=12345678901&CPM=44&ACPM=46&uSV=0.30
                #
                # gmcmap info:      http://www.gmcmap.com/AutomaticallySubmitData.asp
                # URL format:       http://www.GMCmap.com/log2.asp?AID=UserAccountID&GID=GeigerCounterID&CPM=CPM&ACPM=ACPM&uSV=uSV
                # like:             http://www.GMCmap.com/log2.asp?AID=123&GID=456&CPM=15&ACPM=19.7&uSV=0.12
                #                   - uSV is calculated from CPM, NOT from ACPM!
                #                   - there are only 2 decimals for ACPM and uSV; all decimals are kept in GeigerLog
                # test user:        GMC map Account ID: 04365, GMC map Geiger Counter ID: 18368167648
                # gmcmap response when ok:   b'\r\n<!--               sendmail.asp-->\r\n\r\nOK.ERR0'
                #                 when Err:  b"User is not found.ERR1."
                #                 when Err:  b"Counter is not found.ERR2."
                #
                # the counter receives an 'OK 200' via the header. But this is not enough; the counter
                # also wants an 'Err0' within the answer or it will say "Link Server failed"
                #       answer = 'OK'           : Counter: Link Server Failed
                #       answer = 'ERR0'         : Counter: Successful!
                #       answer = 'blahERR0blah' : Counter: Successful!

                # AID and GID are ignored
                if 'CPM'  in query_components: g.WiFiClientValues["CPM"]  = query_components["CPM"] [0]
                if 'ACPM' in query_components: g.WiFiClientValues["ACPM"] = query_components["ACPM"][0]
                if 'uSV'  in query_components: g.WiFiClientValues["uSV"]  = query_components["uSV"] [0]

                answer = 'OK from GeigerLog to WiFiClient GMC'

            myheader    = 'Content-Type', "text/plain"
            mybytes     = bytes(answer, "UTF-8")
            myresponse  = 200

        # page not found 404 error
        else:
            # "headers['User-Agent']: self.headers["User-Agent"]
            #       from Python:      BaseHTTP/0.6 Python/3.9.4
            #       from GMC counter: None
            #       from Firefox:     Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:88.0) Gecko/20100101 Firefox/88.0
            #       from Chromium:    Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36
            if self.headers["User-Agent"] is None or "Python" in self.headers["User-Agent"]:
                answer   = "404 Page not found"
                myheader = 'Content-Type', "text/plain"
            else:
                answer   = "<!DOCTYPE html><style>html{text-align:center;</style><h1>404 Page not found</h1>"
                myheader = 'Content-Type', "text/html"

            rdprint(defname, answer)

            mybytes    = bytes(answer, "UTF-8")
            myresponse = 404

        try:
            self.send_response(myresponse)
            self.send_header(*myheader)
            self.end_headers()
            self.wfile.write(mybytes)
        except Exception as e:
            exceptPrint(e, defname + "send & write 200")

        # mdprint(defname + "values: " + str(g.WiFiClientValues).replace(" ", "").replace("'", "").replace(",", "  "))

