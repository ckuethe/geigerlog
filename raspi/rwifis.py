#! /usr/bin/env python3
# -*- coding: utf-8 -*-

"""
rwifis.py - DataServer's WiFiServer

include in programs with:
    import rwifis
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

from   rutils   import *


class MyHandler(http.server.BaseHTTPRequestHandler):

    def log_message(self, format, *args):
        """replacing the log_message function"""

        strarg = ", ".join(args)    # count(args) = 3 (except on errors)
        if g.WiFiError:  edprint("WiFiServer LogMsg: ", strarg, g.WiFigetmsg)


class MyServer(MyHandler):

    def do_GET(self):
        """'do_GET' overwrites class function"""

        defname  = "WiFiServer do_GET: "

        g.WiFigetmsg = ""
        g.WiFiError  = False

        dprint(defname, "path: '{}'".format(self.path))

        # if thread stopped this is the last dummy call to close the server
        if g.WiFiServerThreadStop:
            self.send_response(200)
            self.end_headers()
            dprint("WiFiServerThreadStop is True") # never reached?
            return


        # lastdata
        if   self.path.startswith("/lastdata"):
            # CSV values of all 12 vars; like:
            # 6.500, 994.786, 997.429, 907.214, 983.857, 892.071, 154,  154,  2.08,  154, 0.9, 6.0
            # bdata       = collectData(1)  # for 1 sec = 1 single record
            bdata       = g.CollectedData

            myheader    = "Content-type", "text/plain; charset=utf-8"
            mybytes     = bdata
            myresponse  = 200

            # gdprint(defname, "Sending: ", bdata)

        # lastavg
        elif self.path.startswith("/lastavg"):
            # like lastdata, except for DeltaT option
            DeltaT      = 1     # default
            query_components = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
            if "chunk" in query_components: DeltaT = int(query_components["chunk"] [0])
            DeltaTsec   = DeltaT * 60                        # DeltaT is in minutes; but need sec
            DeltaTsec   = DeltaTsec if DeltaTsec > 0 else 1  # at least == 1
            # print("DeltaT, DeltaTsec", DeltaT, DeltaTsec)
            # bdata       = collectData(DeltaTsec)      # DeltaTsec is not used
            bdata       = g.CollectedData

            myheader    = "Content-type", "text/plain; charset=utf-8"
            mybytes     = bdata
            myresponse  = 200

        # id
        elif self.path == "/id":
            answer      = "{} {}".format(g.DisplayName, g.__version__)
            bdata       = bytes(answer, "UTF-8")

            myheader    = "Content-type", "text/plain; charset=utf-8"
            mybytes     = bdata
            myresponse  = 200

        # reset Devices
        elif self.path == "/resetdevices":
            answer      = resetDevices("All")
            # rdprint(defname, "/reset - answer: ", answer)
            bdata       = bytes(answer, "UTF-8")

            myheader    = "Content-type", "text/plain; charset=utf-8"
            mybytes     = bdata
            myresponse  = 200

        # # reset WiFiServer
        # elif self.path == "/resetserver":
        #     answer      = resetWiFiServer()
        #     rdprint(defname, "/resetserver - answer: ", answer)
        #     bdata       = bytes(answer, "UTF-8")

        #     myheader    = "Content-type", "text/plain; charset=utf-8"
        #     mybytes     = bdata
        #     myresponse  = 200

        # favicon
        elif "favicon.ico" in self.path:
            bdata       = b""                           # empty; no icon

            myheader    = "Content-type", "image/png"   # png image
            mybytes     = bdata
            myresponse  = 200

        # root
        elif self.path == '/':
            answer      = "<!DOCTYPE html><style>html{text-align:center;</style><h1>Welcome to<br>WiFiServer</h1>"
            answer     += "<b>Supported Requests:</b><br>/id<br>/lastdata<br>/lastavg<br>/reset<br>"
            bdata       = bytes(answer, "UTF-8")

            myheader    = 'Content-Type', "text/html"  # HTML
            mybytes     = bdata
            myresponse  = 200

        # page not found (404 error)
        else:
            # get calling system from self.headers["User-Agent"]:
            #   self.headers["User-Agent"] from Python:      BaseHTTP/0.6 Python/3.9.4
            #   self.headers["User-Agent"] from GMC counter: None
            #   self.headers["User-Agent"] from Firefox:     Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:88.0) Gecko/20100101 Firefox/88.0
            #   self.headers["User-Agent"] from Chromium:    Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.72 Safari/537.36
            # dprint("self.headers['User-Agent']: ", self.headers["User-Agent"])

            g.WiFiError    = True
            if self.headers["User-Agent"] is None or "Python" in self.headers["User-Agent"]:
                answer   = "404 Page not found"
                myheader = 'Content-Type', "text/plain" # PLAIN

            else:
                answer   = "<!DOCTYPE html><style>html{text-align:center;}</style><h1>404 Page not found</h1>"
                myheader = 'Content-Type', "text/html"  # HTML

            # g.WiFigetmsg = "{} | {}{} {}".format(g.WiFiError, defname, answer, TDEFAULT)
            # g.WiFigetmsg = "{} | {}{} {}".format(g.WiFiError, defname, answer)
            g.WiFigetmsg = "{} | {}{}".format(g.WiFiError, defname, answer)

            mybytes    = bytes(answer, "UTF-8")
            myresponse = 404

        gdprint(defname, "Sending: ", bdata)

        self.send_response(myresponse)
        self.send_header(*myheader)
        self.end_headers()

        try:                    self.wfile.write(mybytes)
        except Exception as e:  exceptPrint(e, defname + "Writing bytes to net")


def initWiFiServer():
    """Initialize WiFiServer"""

    defname = "initWiFiServer: "

    tmsg = startWiFiServer()

    return tmsg


def WiFiServerThreadTarget():
    """Thread constantly triggers web readings"""

    defname = "WiFiServerThreadTarget: "

    while not g.WiFiServerThreadStop:
        g.WiFiServer.handle_request()
        time.sleep(0.05)


def resetWiFiServer():
    """reset the WiFiServer"""
    # does it help with the WiFi failures?

    defname = "resetWiFiServer: "

    dprint(defname)
    setIndent(1)

    # terminateWiFiServer()
    # time.sleep(3) # to allow socket release

    # startWiFiServer()

    # rdprint(defname, "Done")
    rdprint(defname, "NOT ACTIVE !!!!!!!!!!!!!!!!!")
    # time.sleep(0.5)

    setIndent(0)
    return "resetWiFiServer Done"


def startWiFiServer():
    """start Web server"""

    defname = "startWiFiServer: "

    # use IP as detected
    WiFiServerIP = getMyIP()

    # create the web server
    try:
        # # 'ThreadingHTTPServer': New in version Py 3.7. Not compatible with 3.6!
        # # non-threading may have been cause for crashing on double requests!
        # # g.WiFiServer = http.server.HTTPServer((WiFiServerIP, g.WiFiServerPort), MyServer)

        import socketserver
        # socketserver.ThreadingTCPServer.allow_reuse_address = True
        g.WiFiServer = socketserver.ThreadingTCPServer((WiFiServerIP, g.WiFiServerPort), MyServer, False) # Do not automatically bind)
        g.WiFiServer.allow_reuse_address = True # Prevent 'cannot bind to address' errors on restart
        g.WiFiServer.server_bind()     # Manually bind, to support allow_reuse_address
        g.WiFiServer.server_activate() # (see above comment)
        # httpd.serve_forever()

        # socketserver.TCPServer.allow_reuse_address = True
        # socketserver.ThreadingTCPServer.allow_reuse_address = True
        # http.server.ThreadingHTTPServer.allow_reuse_address = True
        # g.WiFiServer = http.server.ThreadingHTTPServer((WiFiServerIP, g.WiFiServerPort), MyServer)
        g.WiFiServer.timeout = 1
        tmsg = (True, "Ok, listening at: http://{}:{}".format(WiFiServerIP, g.WiFiServerPort))

    except OSError as e:
        exceptPrint(e, defname)
        msg = "WiFiServer could not be started, because "
        if e.errno == 98:   tmsg = (False, msg + "Port number {} is already in use".format(g.WiFiServerPort))
        else:               tmsg = (False, msg + "of OS.Error: {}".format(e.errno))

    except Exception as e:
        tmsg = (False, "Unexpected Failure - WiFiServer could not be started")
        exceptPrint(e, tmsg[1])

    # make thread only on successful creation of WiFiServer
    if tmsg[0]:
        g.WiFiServerThreadStop        = False
        g.WiFiServerThread            = threading.Thread(target = WiFiServerThreadTarget)
        g.WiFiServerThread.daemon     = True   # must come before start(): makes threads stop on exit!
        g.WiFiServerThread.start()

    return tmsg


def terminateWiFiServer():
    """stop and close Web server"""

    defname = "terminateWiFiServer: "

    g.WiFiServerThreadStop = True
    try:
        # g.WiFiServer.server_close()
        return "Terminate WiFiServer: Done"
    except Exception as e:
        exceptPrint(e, defname)
        return "Terminate WiFiServer: Failure"

