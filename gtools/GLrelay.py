#! /usr/bin/env python3
# -*- coding: UTF-8 -*-

"""
GLrelay.py - http calls to port 80 are relayed to a GeigerLog via Port like 8000
    Program must be started with Admin priviledges!
    start:  Linux:    sudo gtools/GLrelay.py
            Windows:  python gtools/GLrelay.py --- starting from ADMIN CMD Window
    stop:   CTRL-C
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
#     8000/tcp  open  http-alt              # GeigerLog WiFiClient
#     8080/tcp  open  http-proxy            # GeigerLog Monitor Server
#     46099/tcp open  unknown               # GMC counter (may change)
#     48863/tcp open  unknown               # GMC counter (may change)
#
#     Nmap done: 1 IP address (1 host up) scanned in 0.80 seconds
#
#
# To see open TCP files, opened by GMC-500 counter:
#       sudo lsof -a -i  -u root -c python -r 10
#       response like:
#       COMMAND     PID USER   FD   TYPE   DEVICE SIZE/OFF NODE NAME
#       python3 3148390 root    3u  IPv4 47974849      0t0  TCP urkam.fritz.box:http (LISTEN)
#       python3 2910646 root    5u  IPv4 46954092      0t0  TCP urkam.fritz.box:http->GMC-500-old.fritz.box:18418 (ESTABLISHED)
# or use;
#       sudo netstat -antvwee4p  | grep "42:"
#       outputs like:
#       Active Internet connections (servers and established)
#       Proto Recv-Q Send-Q Local Address           Foreign Address         State       User       Inode      PID/Program name        #       tcp        0      0 10.0.0.20:80            10.0.0.42:7005          ESTABLISHED 0          57464899   1554160/python3
#       tcp        0      0 10.0.0.20:80            10.0.0.42:18703         TIME_WAIT   0          0          -
#       tcp        0      0 10.0.0.20:80            10.0.0.42:39532         ESTABLISHED 0          57461527   1554160/python3
#


__author__          = "ullix"
__copyright__       = "Copyright 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024"
__credits__         = [""]
__license__         = "GPL3"
__version__         = "1.0"
__version__         = "1.0.0pre08"

# non-pip imports
import sys, os, time                            # basic modules
import datetime         as dt                   # Datetime
import getopt                                   # parse command line for options and commands
import threading                                # higher-level threading interfaces
import http.server                              # web server to listen for counter
import socket                                   # for finding the IP address
import urllib.request                           # web client to call GeigerLog with GET
import ctypes                                   # for finding if admin on Windows
import ipaddress                                # for checking for valid IP address
import psutil                                   # needed to find if GeigerLog is running


# constants
NAN                     = float("NAN")          # Not A Number, here: Missing value

# colors
TDEFAULT                = '\033[0m'             # default, i.e greyish
TRED                    = '\033[91m'            # red
BRED                    = '\033[91;1m'          # bold red
TGREEN                  = '\033[92m'            # light green
BGREEN                  = '\033[92;1m'          # bold green
TYELLOW                 = '\033[93m'            # yellow

# globals
class GLRelayVars:
    """A class with the only task to make certain variables global"""

    RunningScripts      = {}
    RunningScripts["geigerlog"] = False
    RunningScripts["GLrelay"]   = False

    devel               = False

    datadir             = "data_relay"          # for GLrelay to store its log files
    logfile             = "GLrelay.log"         # regular log file for dprint commands
    handlelogfile       = "GLrelayHandler.log"  # handler log file for non-normal RelayHandler log-messages
    allLogPaths         = (None, None)          # all log paths as tupel: (all dprint messages, only HTTP Server Log Messages)

    logfilePath         = None                  # to hold the full relative path
    handlelogfilePath   = None                  # to hold the full relative path

    GLrelayIP           = "10.0.0.20"           # IP of the computer running this script GLrelay.py # known by the script itself
    GLRelayPort         = 80                    # receiving port is fixed to 80                     # known by the script itself

    GeigerLogIP         = "10.0.0.20"           # IP of the computer running GeigerLog              # can be configured
    GeigerLogPort       = 8000                  # HTTP Port where GeigerLog will be listening.      # can be configured

    GLRelayServer       = None                  # http-server handle; to be set in main
    GLRelayServerRun    = False                 # http-server run/stop flag

    CallCounter         = 1                     # the number of client calls to GeigerLog
    relayMsg            = None                  # this is not None once a GMC call had happened

    ClientIP            = "Undefined"           # e.g. 10.0.0.42 for GMC-500 counter,  detected by the script itself

    helpOptions  = """
        Usage:  GLrelay.py [Options]

        Start:  GLrelay.py      MUST start as ADMIN
        Stop:   CTRL-C

        Options:
            -h, --help          Show this help and exit
            -V, --Version       Show version status and exit
            -I, --GLIP          Set the IP of the computer running GeigerLog
            -P, --GLPort        Set the Port where GeigerLog will be listening

        Example: start GLrelay.py with options:
            GLrelay.py --GLIP=10.0.0.20 --GLPort=8000   # set (receiving) GeigerLog Address to '10.0.0.20:8000'
        or: GLrelay.py -I 10.0.0.20 -P 8000             # same

"""

g = GLRelayVars                             # instantiate all GLRelayVars


def stime():
    """Return current time as YYYY-MM-DD HH:MM:SS"""

    return dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]


def dprint(*args):
    """print timestamp followed by args"""

    defname = "dprint: "

    tag = ""
    for arg in args: tag += str(arg)
    if tag > "": tag = "{:20s} {}".format(stime(), tag)

    print(tag)
    writeTagToFile(tag, defname)


def exceptPrint(e, srcinfo):
    """Print exception details (errmessage, file, line no)"""

    defname = "exceptPrint: "

    exc_type, exc_obj, exc_tb = sys.exc_info()
    fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]    # which file?

    tag = TYELLOW + stime() + " EXCEPTION: '{}' in file: '{}' in line {}".format(e, fname, exc_tb.tb_lineno) + TDEFAULT

    if srcinfo > "": tag += "\n{} {}".format(stime(), srcinfo)

    print(tag)
    writeTagToFile(tag, defname)


def writeTagToFile(tag, origin):
    """write text 'tag' to log file; origin is defname of writer"""

    # remove any color code from the tag to be written to file
    # \x1B = ESC, followed by codes like:  '\x1B[0m', '\x1B[96m', ...
    if "\x1B" in tag:
        codes = ['[0m', '[96m', '[93m', '[92;1m', "[92;1m30", "[92m", "[91;1m41", "[91;1m30", "[91m", "[91;1m", ]
        for c in codes: tag = tag.replace("\x1B" + c, "")

    try:
        with open(g.logfilePath, "at") as f:
            f.write(tag + " \n")
        os.chmod(g.logfilePath, 0o666)
    except Exception as e:
        print("EXCEPTION: coming from {}".format(origin), e)


def writeHandlermsgToFile(msg, origin):
    """write text 'tag' to handler-log file; origin is defname of writer"""

    try:
        with open(g.handlelogfilePath, "at") as f:
            f.write(msg + "\n")
        os.chmod(g.handlelogfilePath, 0o666)
    except Exception as e:
        print("EXCEPTION: coming from {}".format(origin), e)


def clearTerminal():
    """clear the terminal"""

    # print("os.name: ", os.name) # os.name:  posix (on Linux), nt on Windows
    os.system('cls' if os.name == 'nt' else 'clear')


def getIP():
    """get the IP of the computer running GLrelay.py"""

    defname = "getGeigerLogIP: "

    try:
        st = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        st.connect(('8.8.8.8', 80))
        IP = st.getsockname()[0]
    except Exception as e:
        IP = '127.0.0.1'
        srcinfo = "Bad socket connect, IP set to:" + IP
        exceptPrint(e, defname + srcinfo)
    finally:
        st.close()

    return IP


def isAdmin():
    """Finds if user is Admin; valid for both Windows and Linux"""

    try:                   is_admin = (os.getuid() == 0)
    except AttributeError: is_admin = (ctypes.windll.shell32.IsUserAnAdmin() != 0)

    return is_admin


def isValidIP(ip):
    """determine validity of given IP address"""

    defname = "isValidIP: "

    try:
        ipaddress.ip_address(ip)
        return True
    except Exception as e:
        # exceptPrint(e, defname)
        return False


def WiFiRelayThreadTarget():
    """Thread that constantly triggers readings from the HTTP Server"""

    defname = "WiFiRelayThreadTarget: "

    while True:
        # dprint(defname, "in while loop: relayMsg: ", g.relayMsg)
        if g.relayMsg is not None: relayToGeigerLog()                  # takes a few ms on success
        else:                      time.sleep(0.05)                    # to lower CPU load


def startRelayServer():
    """Create a Web Server and start it"""

    defname = "startRelayServer: "

    try:
        # raise OSError("Hoppla")
        g.GLRelayServer = http.server.ThreadingHTTPServer((g.GLrelayIP, g.GLRelayPort), RelayServer)
        g.GLRelayServer.close_connection = True
        g.GLRelayServer.timeout = 3

        msg = "Listening at: http://%s:%s" % (g.GLrelayIP, g.GLRelayPort)
        dprint("{:44s} {}".format(defname, msg))

        # serve forever - method #1
        g.GLRelayServer.serve_forever() # this is blocking

        # # serve forever - method #2
        # # can never be reached when method #1 is active !!!
        # while True:
        #     # dprint(defname, "in while loop")
        #     try:
        #         g.GLRelayServer.handle_request()    # this has a timeout as configured (3s) --- return is always None
        #     except Exception as e:
        #         exceptPrint(e, defname + "handle_request")

    except KeyboardInterrupt:
        print()
        print("Exit by CTRL-C")
        print()
        os._exit(0)

    except OSError as e:
        if   e.errno == 98:          msg = "Port number {} is already in use. Is any other HTTP server active?" .format(g.GLRelayPort)
        elif e.errno in (99, 10049): msg = "Cannot assign requested address {}. Verify GeigerLog's IP address!" .format(g.GLrelayIP)
        elif e.errno == 13:          msg = "Permission denied.   DID YOU START AS ADMIN?"                       # cannot happen
        else:                        msg = "Unexpected OS.Error: {}"                                            .format(e)

    except Exception as e:
        msg = "Unexpected Exception: '{}'".format(e)

    msg0 = "FAILURE GLRelayServer could not be started: "
    dprint("{:44s} {}".format(msg0, msg))


class RelayHandler(http.server.BaseHTTPRequestHandler):
    """Extending the class BaseHTTPRequestHandler"""

    def log_message(self, format, *args):
        """replacing the log_message function"""

        # the default log message is like:
        #       10.0.0.20 - - [19/Apr/2023 10:27:40] "GET /GMC?CPM=30&ACPM=30.47&uSV=0.19 HTTP/1.1" 200 -
        # based on format: '"%s" %s %s' (default setting)
        # normal is 3 args; but only 2 args also happens; perhaps more on errors?
        # the format parameter takes seems to take care of the number of args

        # was ist das denn??
        #   2023-04-21 13:35:26.363 RelayHandler.log_message: code 400, message Bad request syntax ('AT+CIPCLOSE')
        #   2023-04-21 13:35:26.363 RelayHandler.log_message: "AT+CIPCLOSE" 400 -

        defname = "RelayHandler.log_message: "

        try:
            if   not args[0].startswith("GET /GMC") : normal = False
            elif not args[1] == "200"               : normal = False
            elif not args[2] == "-"                 : normal = False
            elif len(args) != 3                     : normal = False
            else:                                     normal = True
        except Exception as e:
            exceptPrint(e, "")
            normal = False

        sargs = format % args
        dprint("{:44s} {}".format(defname, sargs))

        if not normal:
            dprint("Log message is not normal, format parameter: '{}'".format(format))
            for i, a in enumerate(args):    dprint("i: {} a: {}".format(i, a))

            msg = stime() + "  " + sargs + " \n"
            writeHandlermsgToFile(msg, defname)


class RelayServer(RelayHandler):
    """Replacing the do_GET of the class  BaseHTTPRequestHandler"""

    def do_GET(self):
        """'do_GET' overwrites class function"""

        defname = "do_GET: "

        dprint("")
        dprint("{:44s} headers: {}".format("WiFiClient call from {}:".format(self.client_address), bytes(self.headers)))

        # send Ok-mypage
        if self.path.startswith("/GMC"):
            # valid only for GMC counters, e.g.:
            #     self.path:                    /GMC?AID=66&GID=6666&CPM=35&ACPM=21.97&uSV=0.23
            #     self.headers:                 Host: 10.0.0.20
            #                                   Connection: close
            #                                   Accept: */*
            #     self.headers["User-Agent"]:   None
            #
            # mypage      = b'\r\n<!--               sendmail.asp-->\r\n\r\nOK.ERR0' # full (len=47) response from gmcmap.com; header: 'Content-Type', "text/html"
            #                                                                        # auch dieser full response führt bei Raspi mit nur 100 ms delay
            #                                                                        # zu ESTABLISHED fds. Dito 150 ms, dito 200 ms.
            # mypage      = b'ERR0'                                                  # 'ERR0' is all what the counter needs!   header: 'Content-Type', "text/plain"

            mypage        = b'ERR0'
            myheaders     = [('Content-Type', "text/plain")]
            myresponse    = 200

            g.ClientIP = self.client_address[0]
            # dprint("g.ClientIP: ", g.ClientIP, type(g.ClientIP))

        # send favicon dummy
        elif self.path == '/favicon.ico':
            mypage      = b""
            myheaders   = [('Content-Type', 'image/png')]
            myresponse  = 200

        # send 404 page not found error
        else:
            dprint("{:44s} path   : {}   version: {}   command: {}".format("GET call from {}:".format(self.client_address), \
                           self.path, self.request_version, self.command))
            mypage      = b"GeigerLog Relay Server - 404 Page not found"
            myheaders   = [('Content-Type', "text/plain")]
            myresponse  = 404
            dprint(TYELLOW, "{:44s} {}".format("HTTP Error:", mypage), TDEFAULT)
            dprint(TYELLOW, "{:44s} {}".format("HTTP User-Agent:", self.headers["User-Agent"]), TDEFAULT)

        # send the response with headers back to caller (= GMC counter)
        myheaders += [("Connection",  "close")]
        myheaders += [("Content-Length",  len(mypage))]
        try:
            self.send_response(myresponse)
            for header in myheaders:  self.send_header(*header)
            self.end_headers()
            self.wfile.write(mypage) # must provide e.g. to answer FireFox
        except Exception as e:
            exceptPrint(e, defname + "send & write")

        msg = "{:44s} Response: {}  Webpage: {}  Headers: {}".format("Responded to WiFiClient with:", myresponse, mypage, myheaders)
        if b"404" in mypage:  dprint(TYELLOW, msg, TDEFAULT)
        else:                 dprint(TGREEN,  msg, TDEFAULT)

        #######################################################################
        # delay needed to allow the counter to close the TCP File Descriptor!
        # time.sleep(0)             #    0 ms on urkam never enough!
        # time.sleep(0.03)          #   30 ms on urkam never enough
        # time.sleep(0.05)          #   50 ms on urkam never enough
        # time.sleep(0.06)          #   60 ms on urkam never enough
        # time.sleep(0.07)          #   70 ms on urkam ALWAYS enough!
        # time.sleep(0.1)           #  100 ms on urkam ALWAYS enough!
        # time.sleep(0.1)           #  100 ms on Raspi every call results in ESTABLISHED
        # time.sleep(0.15)          #  150 ms on Raspi every 2nd call results in ESTABLISHED
        # time.sleep(0.2)           #  200 ms on Raspi gives 1 ESTABLISHED fd in about 25 calls
        # time.sleep(0.5)           #  500 ms on Raspi gives None ESTABLISHED fd in >800 calls
        # time.sleep(1)             # 1000 ms on Raspi gives None ESTABLISHED fd in >110 calls          # 1 second !!!!
        time.sleep(1)               # sleep kann NICHT auf relayToGeigerLog verschoben werden
        #######################################################################

        # set flag to allow sending data to GeigerLog
        if self.path.startswith("/GMC"): g.relayMsg = self.path                                     # relayMsg is None otherwise
        else:                            dprint("NOT relaying to GeigerLog: '{}".format(self.path))


def relayToGeigerLog():
    """send 'relayMsg' to GeigerLog as GET request"""
    # takes 2 ... 10 ms on Success; on Fail up to 3000 ms (on timeout))

    defname      = "relayToGeigerLog: "

    GeigerLogURL = "http://{}:{}{}".format(g.GeigerLogIP, g.GeigerLogPort, g.relayMsg)
    g.relayMsg   = None     # reset after using in URL

    dprint("{:44s} {}".format("GET request to GeigerLog with URL:", GeigerLogURL))

    rgstart   = time.time()
    try:
        with urllib.request.urlopen(GeigerLogURL) as response:
            GLcontent = response.read()
            GLstatus  = response.status
            # dprint(defname, "info:    ", response.info())   # info:    Server: BaseHTTP/0.6 Python/3.9.2, \n Date: Mon, 01 May 2023 12:29:09 GMT \n Content-Type: text/plain
            # dprint(defname, "geturl : ", response.geturl()) # http://10.0.0.20:8000/GMC?CPM=31&ACPM=30.95&uSV=0.2

    except OSError as e:
        errcode = "" if e.errno is None else "Error-Code: {}".format(e.errno)
        if g.devel: exceptPrint(e, errcode)
        # if e.errno is not None:
        #     Errmsg0 = defname + "Relaying to GeigerLog failed - "
        #     if   e.errno == 98:          emsg = "Port number {} is already in use. Is any other Web Server active?"    .format(g.GLRelayPort)
        #     elif e.errno in (99, 10049): emsg = "Cannot assign requested address '{}'. Verify GeigerLog's IP address!" .format(g.GLrelayIP)
        #     elif e.errno == 13:          emsg = "Permission denied.   DID YOU START AS ADMIN?"
        #     elif e.errno == 111:         emsg = "Connection refused. Verify IP address: '{}' and Port number: {}"      .format(g.GLRelayPort, g.GLrelayIP)
        #     else:                        emsg = "Unexpected OS.Error"
        #     dprint(Errmsg0 + emsg)
        # else:
        #     dprint("errno is None: ", e.errno)
        #     dprint("strerrno is None: ", e.strerror)
        #     dprint("e: ", e)

        if   "Connection refused" in str(e):                            emsg = "Make sure " + TRED + "that GeigerLog is RUNNING AND LOGGING !"
        elif "Remote end closed connection without response" in str(e): emsg = "Make sure " + TRED + "that GeigerLog is LOGGING !"
        else:                                                           emsg = TRED + "Error: " + str(e)
        if emsg > "": dprint("No connection to GeigerLog - ", emsg, TDEFAULT)

        time.sleep(1)         # sleep after a failed GET call

    except Exception as e:
        if g.devel: exceptPrint(e, "")
        Errmsg0 = defname + "Relaying to GeigerLog failed with Exception: '{}'".format(e)
        dprint(Errmsg0)

        time.sleep(1)         # sleep after failed GET call

    else:
        rgdur = 1000 *(time.time() - rgstart)
        msg   = "{:38s} {}   Webpage: '{}'  after {:0.1f} ms  CallCounter: {}".format("Response from GeigerLog:",  GLstatus, GLcontent, rgdur, g.CallCounter)
        if GLstatus == 200:   dprint(TGREEN, msg, TDEFAULT)
        else:                 dprint(BRED,   msg, TDEFAULT)

    finally:
        g.CallCounter += 1

    # showPSUTIL()
    # cleanupFileDescriptors()


# def showPSUTIL():
#     """Discovering net connections"""
#     # see: https://psutil.readthedocs.io/en/latest/index.html?highlight=connection#psutil.net_connections

#     ospid = os.getpid() # pid of this GLrelay.py process

#     dprint("")
#     # dprint("Total number of File Descriptors this process: ",  pp.num_fds())    # available ONLY on UNIX

#     g.FileDescriptors = []
#     pnc = psutil.net_connections(kind="inet4") # returns a Python list of named tuples for inet4 = TCP v4
#     for p in pnc:
#         if g.ClientIP in str(p.raddr) and p.fd != -1:
#             if ospid == p.pid:  ppid = "same "
#             else:               ppid = "other"
#             dprint("os.pid: ", os.getpid(), " pid: ", ppid, "  fd: ", p.fd, "  raddr: ", p.raddr)

#             g.FileDescriptors.append(p.fd)

#     g.FileDescriptors.sort()
#     dprint("Discovered TCP File Descriptors: ", g.FileDescriptors)


# def cleanupFileDescriptors():
#     """Deleting File Descriptors"""

#     # Info on File Descriptors:
#     # Linux:  https://www.baeldung.com/linux/limit-file-descriptors
#     # "The -n option shows the soft limit on the number of open file descriptors:""
#     #       ulimit -n   :   1024    (on urkam, DELL)
#     #
#     # Windows: https://learn.microsoft.com/en-us/cpp/c-runtime-library/reference/setmaxstdio?redirectedfrom=MSDN&view=msvc-170
#     # "By default, up to 512 files can be open simultaneously at the stream I/O level.
#     # This level includes files opened and accessed using the fopen, fgetc, and fputc
#     # family of functions. The limit of 512 open files at the stream I/O level can be
#     # increased to a maximum of 8,192 by use of the _setmaxstdio function."
#     #       Default     :   512

#     # delete files by Filedescriptor:
#     #       os.closerange(fd0, fdN)       # fd = Filedescriptor
#     # or by:
#     #       for fd in range(5, 7):
#     #          try:
#     #              os.close(fd)
#     #          except OSError as e:
#     #              print(e, fd, end="  ")
#     # may check first for existing fd with: (also needs try!)
#     #       os.fstat(fd)    # does fd exist?

#     # dprint("g.FileDescriptors: ", g.FileDescriptors)
#     if len(g.FileDescriptors) < 9: return

#     for fd in g.FileDescriptors:
#         if fd < 0: continue         # Filedescriptor may be "-1"

#         try:
#             # may check first for existing fd with: os.stat() (also needs try!)
#             os.close(fd)
#             print("closed FD: ", fd)
#         except OSError as e:
#             print(e, fd)

#     g.FileDescriptors = []


# def makeOpenFiles():
#     """open 'total' files and leave open"""

#     total   = 1000
#     counter = [None] * total
#     pathbase = "/home/ullix/temp/test"
#     print("Opening files:")
#     for i in range(total):
#         counter[i] = open(pathbase + str(i), "at")
#         counter[i].write("test\n")
#         print(i, end="  ")
#         time.sleep(0.000005)
#     print()



def getRunningScripts():

    print("Testing for running GeigerLog programs:")
    for proc in psutil.process_iter(['pid', 'name']):
        if "python"  in str(proc.info).lower():
            for a in proc.cmdline():
                if   "geigerlog" in a:
                    # print(proc.cmdline())
                    print("   GeigerLog is running")
                    g.RunningScripts["geigerlog"] = True

                elif "GLrelay" in a:
                    # print(proc.cmdline())
                    print("   GLrelay is running")
                    g.RunningScripts["GLrelay"] = True

                elif "Demo"  in a:
                    # print(proc.cmdline())
                    print("   Demo* is running")

    if not g.RunningScripts["geigerlog"] :
        print(TRED + "GeigerLog is not running and cannot listen to calls from this GLrelay!" + TDEFAULT)
        x = input("Press Enter to continue anyway")

    print()


def main():
    """Entry point"""

    defname = "main: "

    # clear screen
    clearTerminal()

    # header
    print(BGREEN + "*" * 150 + TDEFAULT)

    # checking if Admin
    if not isAdmin():
        print()
        print("This program must be run with administrative right, but you started as regular user")
        print("Please, restart as administrator")
        return 1

    # set devel flag
    if "devel" in sys.argv: g.devel = True

    # get and set the default IPs
    # by default GLrelay.py and GeigerLog are running on the same computer having the same IP; change with command line options
    g.GLrelayIP   = getIP()
    g.GeigerLogIP = g.GLrelayIP

    # parse command line options
    try:
        # sys.argv[0] is progname
        opts, args = getopt.getopt(sys.argv[1:], "hdVI:P:", ["help", "debug", "Version", "GLIP=", "GLPort="])
    except getopt.GetoptError as e :
        # print info like "option -x not recognized", then exit
        msg = "For Help use: './GLrelay.py -h'"
        exceptPrint(e, msg)
        return 1

    # process the options
    for opt, optval in opts:

        if   opt in ("-h", "--help"):                   # show the help info
            print(g.helpOptions)
            return 1

        elif opt in ("-V", "--Version"):                # show the GLrelay.py version
            print("GLrelay.py Version:", __version__)
            return 1

        elif opt in ("-I", "--GLIP"):                   # re-define the GeigerLog IP address
            if isValidIP(optval):
                g.GeigerLogIP = optval
            else:
                print("The configured IP address '{}' is not valid. See: https://en.wikipedia.org/wiki/IP_address".format(optval))
                print("As example, this computer has the IP address: '{}'".format(g.GLrelayIP))
                return 1

        elif opt in ("-P", "--GLPort"):                 # re-define the GeigerLog Port number
            try:    pnum = int(float(optval))
            except: pnum = -1

            if pnum >= 1024 and pnum <= 65535:
                g.GeigerLogPort = pnum                  # valid port
            else:
                print("The configured GeigerLog Port number '{}' is not valid".format(optval))
                print("Allowed range for Port numbers is 1024 ... 65535 (incl.)")
                return 1


    # process the commands
    deleteLog = True
    for arg in args:
        if "cont" in arg.lower(): deleteLog = False


    getRunningScripts()

    # make data dir and log file paths
    try:
        if not os.path.exists(g.datadir):
            os.mkdir(g.datadir, mode = 0o777)
        else:
            os.chmod(g.datadir, 0o777)
        g.logfilePath       = os.path.join(g.datadir, g.logfile)                  # the full relative path
        g.handlelogfilePath = os.path.join(g.datadir, g.handlelogfile)            # the full relative path
        g.allLogPaths       = (g.logfilePath, g.handlelogfilePath)                # tuple:
    except Exception as e:
        exceptPrint(e, "Cannot create log files. Please, verify. Cannot continue, will exit.".format(g.datadir))
        return 1

    # delete the log files unless 'cont' requested
    if deleteLog:
        for path in g.allLogPaths:
            try:    os.remove(path)
            except: pass

    # make new logfiles or continue old ones
    msg = "\n" + stime() + " GLrelay Version: {} {}\n".format(__version__, "*" * 100)
    writeTagToFile       (msg, defname)
    writeHandlermsgToFile(msg, defname)

    # print config
    dprint("{:44s} {}".format("GLrelay.py is configured for Listening at:", "{}:{}".format(g.GLrelayIP, g.GLRelayPort)))
    dprint("{:44s} {}".format("GLrelay.py is configured for Relaying to :", "{}:{}".format(g.GeigerLogIP, g.GeigerLogPort)))

    # start the thread for relaying to GeigerLog
    WiFiRelayThread = threading.Thread(target=WiFiRelayThreadTarget)
    WiFiRelayThread.daemon = True        # daemons will be auto-stopped on exit!
    WiFiRelayThread.start()

    ### testing
    # makeOpenFiles()
    # showPSUTIL()
    # dprint("")
    ###

    # start the http Server to listen for GMC calls
    # dprint("{:44s} {}".format("Starting the Relay-Server", ""))
    startRelayServer()



###################################################################################################
if __name__ == '__main__':
    main()

