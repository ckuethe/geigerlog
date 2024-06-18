#!/usr/bin/python3
# -*- coding: UTF-8 -*-

"""
Simul_GMCcounter.py - GeigerLog's Simulator for a GMC counter

use with GeigerLog to simulate responses of a GMC Geiger counter. See more in
the header of file gdev_gmc.py located in the GeigerLog folder.

- MUST start as SUDO (!):
- pyserial must have been installed as root:   sudo python -m pip install -U pyserial
- socat must have been installed as root:      sudo apt install socat
- GeigerLog must have been started with command: 'simulgmc'

The communication between GeigerLog and the Pseudo device is logged into file
Simul_GMCcounter.log
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


# check ports with:  stty -F /dev/pts/5
#                    stty -F /dev/ttyS90
#
# cstopb=<bool>  Sets two stop bits, rather than one.    # How to use?
#
# socat -d -d -d -d tcp-listen:4141,reuseaddr,fork file:/dev/ttyUSB0,nonblock,cs8,b9600,cstopb=0,raw,echo=0
# socat -d -d  pty,b9600,cs8,raw,echo=0    # cs8 ok, cs7 geht nicht
#
# use sudo to make links
    # sudo socat -d -d  pty,b9600,raw,echo=0,link=/dev/ttyS90    pty,b9600,raw,echo=0,link=/dev/ttyS91
# but then it needs these commands:
#   sudo chmod 777 /dev/ttyS91
#   sudo chmod 777 /dev/ttyS90
# obgleich das schon erfüllt sein sollte:
#   lrwxrwxrwx 1 root root       10 Sep  7 11:56 /dev/ttyS90 -> /dev/pts/2
#   lrwxrwxrwx 1 root root       10 Sep  7 11:56 /dev/ttyS91 -> /dev/pts/4


__author__          = "ullix"
__copyright__       = "Copyright 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024"
__credits__         = [""]
__license__         = "GPL3"
__version__         = "1.2"

import sys, os, io, time
import datetime                  as dt
import subprocess
import serial                               # serial port
import serial.tools.list_ports              # allows listing of serial ports
import numpy                     as np      # for Poisson values
import struct
import threading
import getopt                               # parsing command line options
from collections import deque               # deque is used as fixed-size buffer


TDEFAULT            = '\033[0m'             # default, i.e greyish
TRED                = '\033[91m'            # red
TGREEN              = '\033[92m'            # light green
TYELLOW             = '\033[93m'            # yellow
TBLUE               = '\033[94m'            # blue (dark)
TMAGENTA            = '\033[95m'            # magenta
TCYAN               = '\033[96m'            # cyan
TWHITE              = '\033[97m'            # high intensity white

INVMAGENTA          = '\033[45m'            # invers magenta looks ok
INVBOLDMAGENTA      = '\033[45;1m'          # invers magenta with bold white

# BOLDxyz are brighter colors
BOLDRED             = '\033[91;1m'          # bold red
BOLDGREEN           = '\033[92;1m'          # bold green
BOLDYELLOW          = '\033[93;1m'          # bold yellow
BOLDBLUE            = '\033[94;1m'          # bold blue
BOLDMAGENTA         = '\033[95;1m'          # bold magenta
BOLDCYAN            = '\033[96;1m'          # bold cyan
BOLDWHITE           = '\033[97;1m'          # bold white


class globalvars():
    NAN                 = float("nan")
    # GMCVersion          = "GMC-300"
    GMCVersion          = "GMC-600_252"
    GMCcfg              = None
    GMCpowerIsON        = True

    SimulGMCThreadRun   = False
    SimulGMCThread      = None

    CPSmeanFirstTube    = 10
    CPSmeanSecondTube   = 0

    CPSqueueFirstTube   = deque([], 60)     # size limited to 60
    CPSqueueSecondTube  = deque([], 60)     # size limited to 60

    helpOptions         = """
            Usage:  Simul_GMCcounter.py [Options]

            Start:  Simul_GMCcounter.py
            Stop:   CTRL-C

            Options:
                -h, --help          Show this help and exit
                -V, --Version       Show version status and exit
                -C, --Counter       Set the counter name (GMC-300, GMC-500, GMC-600)                Default: GMC-500
                -F, --FirstTube     Set the CPS count rate for the first (high sensitivity) tube    Default: 10
                -S, --SecondTube    Set the CPS count rate for the second (low sensitivity) tube    Default: 1

            Example: starting Simul_WiFiClient.py with options:
                                 Simul_GMCcounter.py --Counter=GMC-500 --FirstTube=10 --SecondTube=1
            or with same result: Simul_GMCcounter.py -C GMC-500 -F 10 -S 1
    """

# instantiate class vars
g = globalvars

### function code ##############################################################################################################

def longstime():
    """Return current time as YYYY-MM-DD HH:MM:SS.mmm, (mmm = millisec)"""

    return dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3] # ms resolution


def exceptPrint(e, srcinfo):
    """Print exception details (errmessage, file, line no)"""

    exc_type, exc_obj, exc_tb = sys.exc_info()
    fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]    # which file?

    print(longstime(), "EXCEPTION: '{}' in file: '{}' in line {}".format(e, fname, exc_tb.tb_lineno))
    if srcinfo > "": print(longstime(), srcinfo)


def init():
    """Init the Simul_GMCcounter"""

    print("\n------------------------ Simul_GMCcounter.py -------------------------------")
    print("File:                 ", __file__)

    # parse command line options
    try:
        # sys.argv[0] is progname
        opts, args = getopt.getopt(sys.argv[1:], "hdVC:F:S:", ["help", "debug", "Version", "Counter=", "FirstTube=", "SecondTube="])
    except getopt.GetoptError as e :
        # print info like "option -x not recognized", then exit
        msg = "For Help use: './Simul_GMCcounter.py -h'"
        exceptPrint(e, msg)
        return 1

    # process the options
    for opt, optval in opts:

        if   opt in ("-h", "--help"):                       # show the help info
            print(g.helpOptions)
            return 1

        elif opt in ("-V", "--Version"):                    # show the Simul_WiFiClient.py version
            print("Simul_GMCcounter.py Version:", __version__)
            return 1

        elif opt in ("-C", "--Counter"):                    # set the counter name
            g.GMCVersion = optval.strip()

        elif opt in ("-F", "--FirstTube"):                  # The mean count rate for the  first tube
            try:
                g.CPSmeanFirstTube = float(optval)
            except Exception as e:
                exceptPrint(e, "CPSmeanFirstTube")
                g.CPSmeanFirstTube = 10

        elif opt in ("-S", "--SecondTube"):                 # The mean count rate for the  second tube
            try:
                g.CPSmeanSecondTube = float(optval)
            except Exception as e:
                exceptPrint(e, "CPSmeanSecondTube")
                g.CPSmeanSecondTube = 1

    # print("Config:")
    # print("   Counter:           ", g.GMCVersion)
    # print("   CPSmeanFirstTube:  ", g.CPSmeanFirstTube)
    # print("   CPSmeanSecondTube: ", g.CPSmeanSecondTube)
    # print()

    # g.GMCVersion    = getVersion()
    # g.GMCcfg        = getCFG()
    # print("Counter Version found:")
    # print("   Version:           ", g.GMCVersion)
    # print("   CFG: len:          ", len(g.GMCcfg))
    # print("   CFG:")
    # print(g.GMCcfg)
    # print()


    print("Executing subprocess.Popen with socat command: ")

    # mypopen = subprocess.Popen([
    #                             "socat",
    #                             '-d',
    #                             '-d',
    #                             'pty,b4000000,CSIZE=CS8,PARENB=0,PARODD=0,raw,echo=0,link=/dev/ttyS90',
    #                             'pty,b4000000,CSIZE=CS8,PARENB=0,PARODD=0,raw,echo=0,link=/dev/ttyS91'
    #                             ])

    mypopen = subprocess.Popen([
                                "socat",
                                'pty,link=/dev/ttyS90',
                                'pty,link=/dev/ttyS91'
                                ])

    print("   subprocess.Popen: mypopen:           ", mypopen)
    print("   subprocess.Popen: mypopen.args:      ", mypopen.args)
    print("   subprocess.Popen: mypopen.pid:       ", mypopen.pid)

    time.sleep(0.005) # socat needs ~0.001 sec to complete its action; but then keeps running

    print("\nFound permissions:")
    try:
        print("   /dev/ttyS90: ", oct(os.stat('/dev/ttyS90')[0]))
        print("   /dev/ttyS91: ", oct(os.stat('/dev/ttyS91')[0]))
    except Exception as e:
        print("Listing permissions failed with Exception: ", e)
        print()
        print("??????????   FAILURE - Forgot to start program with 'sudo'  ???????????\n\n")
        print()
        sys.exit()

    print("\nChanging permission with os.chmod on: ", '/dev/ttyS90', '/dev/ttyS91', 'to 0o777')
    start = time.time()
    while True:
        try:
            os.chmod('/dev/ttyS90', 0o777)
            os.chmod('/dev/ttyS91', 0o777)
            break
        except:
            pass
    print("   success after {:0.3f} ms".format((time.time() - start) * 1000))

    print("\nChanged permissions:")
    print("   /dev/ttyS90: ", oct(os.stat('/dev/ttyS90')[0]))
    print("   /dev/ttyS91: ", oct(os.stat('/dev/ttyS91')[0]))

    print("\nList of Ports found on system (including linked ports): ")
    lps = serial.tools.list_ports.comports(include_links=True)
    lps.sort()
    for lp in lps:  print(" ", lp)




    print("Config:")
    print("   Counter:           ", g.GMCVersion)
    print("   CPSmeanFirstTube:  ", g.CPSmeanFirstTube)
    print("   CPSmeanSecondTube: ", g.CPSmeanSecondTube)
    print()

    g.GMCVersion    = getVersion()
    g.GMCcfg        = getCFG()
    print("Counter Version found:")
    print("   Version:           ", g.GMCVersion)
    print("   CFG: len:          ", len(g.GMCcfg))
    print("   CFG:")
    print(g.GMCcfg)
    print()







    g.SimulGMCThreadRun         = True
    g.SimulGMCThread            = threading.Thread(target = SimulGMCThreadTarget)
    g.SimulGMCThread.daemon     = True   # must come before daemon start: makes threads stop on exit!
    g.SimulGMCThread.start()

    start           = time.time()
    counter         = -1
    portsim         = "/dev/ttyS91"

    # create serial connection
    # for use of spy see: https://pyserial.readthedocs.io/en/latest/url_handlers.html
    # wser        = serial.serial_for_url("spy://{}?file=Simul_GMCcounter.log".format(portsim), baudrate=0, timeout=0.1, bytesize=8, parity="N")
    wser        = serial.Serial(portsim, baudrate=115200, timeout=0.05)
    print("\nSerial Pointer: ", wser)
    print()
    print("Looping:")
    while True:
        wstart   = time.time()
        counter += 1

        brec = b""
        while True:
            cnt = wser.in_waiting
            if cnt > 0:     brec += wser.read(cnt)
            else:           break

        if brec > b"":
            # print(" ")
            print("\nReceived : {:30s}  on port '{}'".format(str(brec), portsim ))
            print("           ", end="")

            counter = 0

            if   brec == b"<GETCPM>>"                   : tag = getCounts("CPM")
            elif brec == b"<GETCPS>>"                   : tag = getCounts("CPS")
            elif brec == b"<GETCPML>>"                  : tag = getCounts("CPM1st")
            elif brec == b"<GETCPSL>>"                  : tag = getCounts("CPS1st")
            elif brec == b"<GETCPMH>>"                  : tag = getCounts("CPM2nd")
            elif brec == b"<GETCPSH>>"                  : tag = getCounts("CPS2nd")

            elif brec == b"<GETDATETIME>>"              : tag = getDatetime()        # return the counter's Datetime
            elif brec.startswith(b"<SETDATETIME")       : tag = setDatetime(brec)    # set the counter's Datetime (has no effect here)
            elif brec == b"<GETCFG>>"                   : tag = g.GMCcfg
            elif brec == b"<GETVER>>"                   : tag = g.GMCVersion
            elif brec == b'<POWERON>>'                  : tag = setPower("ON")
            elif brec == b'<POWEROFF>>'                 : tag = setPower("OFF")
            elif brec == b"<HEARTBEAT0>>"               : tag = b""                  # empty answer
            elif brec == b"<GetSPISA>>"                 : tag = b"\x01\x04\x6a\xaa"             # dummy answer
            elif brec == b"<ECFG>>"                     : tag = b"\xaa"
            elif brec.startswith(b"<WCFG")              : tag = b"\xaa"
            elif brec == b"<CFGUPDATE>>"                : tag = b"\xaa"
            elif brec == b"<GETSERIAL>>"                : tag = b"FAKE SN"
            elif brec == b"<DSID>>"                     : tag = b"FAKE DSID"

            else                                        : tag = b"SIMUL UNDEFINED"

            wser.write(tag)
            print("Answered : {} ".format(tag))

            print("exec in  : {:0.1f} ms".format(1000 * (time.time() - wstart) ))

        else:
            loopcount = 30000
            if counter % loopcount == 0 and counter > 0:
                dur = 1000 * (time.time() - start)
                print("   Loops: {} in {:0.1f} ms per loop".format(loopcount,  dur / loopcount), flush=True)
                start = time.time()
            else:
                print("\033[#D", end="", flush=True) # printing ANSI codes  https://gist.github.com/fnky/458719343aabd01cfb17a3a4f7296797

        time.sleep(0.001) # 1 ms resolution


def SimulGMCThreadTarget():
    """Get CPS every 1 second and add to the queue"""

    defname = "SimulGMCThreadTarget: "

    # fill the queue for full CPM from beginning
    for i in range(60):
        g.CPSqueueFirstTube .append(np.random.poisson(g.CPSmeanFirstTube))
        g.CPSqueueSecondTube.append(np.random.poisson(g.CPSmeanSecondTube))

    next = time.time()
    while g.SimulGMCThreadRun:
        if time.time() >= next:
            next += 1
            g.CPSqueueFirstTube .append(np.random.poisson(g.CPSmeanFirstTube))
            g.CPSqueueSecondTube.append(np.random.poisson(g.CPSmeanSecondTube))

        time.sleep(0.1)


def getVersion():
    """Available GMC version"""

    # GMCversion = b"GMC-300Re 3.20"
    # GMCversion = b"GMC-300Re 4.20"
    # GMCversion = b"GMC-300Re 4.22"

    # GMCversion = b"GMC-320Re 3.22"            # device used by user katze
    # GMCversion = b"GMC-320Re 4.19"
    # GMCversion = b"GMC-320Re 5.xx"            # with WiFi

    # GMCversion = b'GMC-320+V5\x00RRe 5.73'    # b'GMC-320+V5\x00RRe 5.73' # NULL within string!  from Tom Johnson's new GMC-320

    # S-versions
    # GMCversion = b"GMC-300SRe 1.03"           # my new GMC-300S
    # GMCversion = b"GMC-320SRe 1.03"           # user Ted Sled's GMC-320S

    # GMCversion = b"GMC-500Re 1.00"
    # GMCversion = b"GMC-500Re 1.08"

    # GMCversion = b"GMC-500+Re 1.0x"
    # GMCversion = b"GMC-500+Re 1.18"
    # GMCversion = b"GMC-500+Re 1.22"           # my version
    # GMCversion = b"GMC-500+Re 2.28"           # latest version as of 2021-10-20

    # GMCversion = b"GMC-600Re 1.xx"
    # GMCversion = b"GMC-600+Re 2.xx"           # fictitious device; not (yet) existing, simulates the bug in the 'GMC-500+Re 1.18'
    # GMCversion = b"GMC-600+Re 2.42"           # Ihab's 2nd GMC-600 counter
    # GMCversion = b"GMC-600+Re 2.45"           # latest update reported by Bobackman on 05/09/2023
    # GMCversion = b"GMC-600+Re 2.46"           # latest update reported by Bobackman
    # GMCversion = b"GMC-600+Re 2.52"           # latest update reported by Ihab17 and other (should have 6 calibration points)

    # GMCversion = b"GMC-800Re1.08"             # reported by user MaoBra, see: https://sourceforge.net/p/geigerlog/discussion/devel/thread/6870a473fd/

    if   g.GMCVersion == "GMC-300":     GMCversion = b"GMC-300Re 4.22"
    elif g.GMCVersion == "GMC-320":     GMCversion = b"GMC-320Re 4.22"
    elif g.GMCVersion == "GMC-300S":    GMCversion = b"GMC-300SRe 1.03"
    elif g.GMCVersion == "GMC-320S":    GMCversion = b"GMC-320SRe 1.03"
    elif g.GMCVersion == "GMC-500":     GMCversion = b"GMC-500+Re 1.22"
    elif g.GMCVersion == "GMC-600":     GMCversion = b"GMC-600+Re 2.46"
    elif g.GMCVersion == "GMC-600_252": GMCversion = b"GMC-600+Re 2.52"
    elif g.GMCVersion == "GMC-800":     GMCversion = b"GMC-800Re1.08"
    else                          :     GMCversion = b"GMC-500+Re 1.22"

    return GMCversion


def getCFG():
    """CFG from counter; by version"""

    cfg = b''           # set cfg

# 512 == GMC_configsize :
    if b"GMC-500" in g.GMCVersion:
        # GMC-500(non-plus) readout with 512 bytes configdtrecdtrec
        #
        # power is OFF:
        # cfg500str = "01 00 00 02 1F 00 00 64 00 3C 3E C7 AE 14 27 10 42 82 00 00 00 19 41 1C 00 00 00 3F 00 00 00 00 02 02 00 00 00 00 FF FF FF FF FF FF 00 01 00 78 0A FF FF 3C 00 05 FF 01 00 00 0A 00 01 0A 00 64 00 3F 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 77 77 77 2E 67 6D 63 6D 61 70 2E 63 6F 6D 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 6C 6F 67 32 2E 61 73 70 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 02 00 02 11 05 1E 10 34 05 FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF"
        cfg500    = [0x01,0x00,0x00,0x02,0x1F,0x00,0x00,0x64,0x00,0x3C,0x3E,0xC7,0xAE,0x14,0x27,0x10,0x42,0x82,0x00,0x00,0x00,0x19,0x41,0x1C,0x00,0x00,
                     0x00,0x3F,0x00,0x00,0x00,0x00,0x02,0x02,0x00,0x00,0x00,0x00,0xFF,0xFF,0xFF,0xFF,0xFF,0xFF,0x00,0x01,0x00,0x78,0x0A,0xFF,0xFF,0x3C,
                     0x00,0x05,0xFF,0x01,0x00,0x00,0x0A,0x00,0x01,0x0A,0x00,0x64,0x00,0x3F,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,
                     0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,
                     0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,
                     0x00,0x00,0x00,0x77,0x77,0x77,0x2E,0x67,0x6D,0x63,0x6D,0x61,0x70,0x2E,0x63,0x6F,0x6D,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,
                     0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x6C,0x6F,0x67,0x32,0x2E,0x61,0x73,0x70,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,
                     0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,
                     0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,
                     0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,
                     0x00,0x02,0x00,0x02,0x11,0x05,0x1E,0x10,0x34,0x05,0xFF,0xFF,0xFF,0xFF,0xFF,0xFF,0xFF,0xFF,0xFF,0xFF,0xFF,0xFF,0xFF,0xFF,0xFF,0xFF,
                     0xFF,0xFF,0xFF,0xFF,0xFF,0xFF,0xFF,0xFF,0xFF,0xFF,0xFF,0xFF,0xFF,0xFF,0xFF,0xFF,0xFF,0xFF,0xFF,0xFF,0xFF,0xFF,0xFF,0xFF,0xFF,0xFF,
                     0xFF,0xFF,0xFF,0xFF,0xFF,0xFF,0xFF,0xFF,0xFF,0xFF,0xFF,0xFF,0xFF,0xFF,0xFF,0xFF,0xFF,0xFF,0xFF,0xFF,0xFF,0xFF,0xFF,0xFF,0xFF,0xFF,
                     0xFF,0xFF,0xFF,0xFF,0xFF,0xFF,0xFF,0xFF,0xFF,0xFF,0xFF,0xFF,0xFF,0xFF,0xFF,0xFF,0xFF,0xFF,0xFF,0xFF,0xFF,0xFF,0xFF,0xFF,0xFF,0xFF,
                     0xFF,0xFF,0xFF,0xFF,0xFF,0xFF,0xFF,0xFF,0xFF,0xFF,0xFF,0xFF,0xFF,0xFF,0xFF,0xFF,0xFF,0xFF,0xFF,0xFF,0xFF,0xFF,0xFF,0xFF,0xFF,0xFF,
                     0xFF,0xFF,0xFF,0xFF,0xFF,0xFF,0xFF,0xFF,0xFF,0xFF,0xFF,0xFF,0xFF,0xFF,0xFF,0xFF,0xFF,0xFF,0xFF,0xFF,0xFF,0xFF,0xFF,0xFF,0xFF,0xFF,
                     0xFF,0xFF,0xFF,0xFF,0xFF,0xFF,0xFF,0xFF,0xFF,0xFF,0xFF,0xFF,0xFF,0xFF,0xFF,0xFF,0xFF,0xFF,0xFF,0xFF,0xFF,0xFF,0xFF,0xFF,0xFF,0xFF,
                     0xFF,0xFF,0xFF,0xFF,0xFF,0xFF,0xFF,0xFF,0xFF,0xFF,0xFF,0xFF,0xFF,0xFF,0xFF,0xFF,0xFF,0xFF,0xFF,0xFF,0xFF,0xFF,0xFF,0xFF,0xFF,0xFF,
                     0xFF,0xFF,0xFF,0xFF,0xFF,0xFF,0xFF,0xFF,0xFF,0xFF,0xFF,0xFF,0xFF,0xFF,0xFF,0xFF,0xFF,0xFF,0xFF,0xFF,0xFF,0xFF,0xFF,0xFF,0xFF,0xFF,
                     0xFF,0xFF,0xFF,0xFF,0xFF,0xFF,0xFF,0xFF,0xFF,0xFF,0xFF,0xFF,0xFF,0xFF,0xFF,0xFF,0xFF,0xFF]
        # cfg500    = cfg500str.split(' ')

        # power is ON:
        # cfg500    = ["0"] + cfg500[1:]
        #print("cfg500:\n", len(cfg500), cfg500)

        if g.GMCpowerIsON: cfg500 = [0] + cfg500[1:]    # power is ON
        else:              cfg500 = [1] + cfg500[1:]    # power is OFF
        # for a in cfg500: cfg += bytes([int(a, 16)]) # using hex data
        cfg = bytes(cfg500)


    elif b"GMC-600" in g.GMCVersion:
        # Ihab's 2nd GMC-600 counter
        #
        # power is ON:
        # next is 1st version
        # power is ON
        cfg600_242_1 = [0,0,0,0,241,0,0,150,1,164,63,128,0,0,16,104,65,32,0,0,164,16,66,200,0,0,1,63,0,0,0,1,1,3,0,0,0,0,255,255,255,255,
                        255,255,0,1,0,120,10,255,255,60,0,10,255,2,0,0,10,3,1,10,0,150,0,62,255,219,110,71,69,73,71,69,82,0,0,0,0,0,0,0,0,
                        0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,78,65,83,65,50,
                        48,50,49,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,
                        0,0,0,119,119,119,46,103,109,99,109,97,112,46,99,111,109,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,108,111,103,50,46,97,
                        115,112,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,48,51,52,51,56,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,
                        0,0,0,0,0,57,53,53,48,56,56,54,57,57,53,51,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,5,1,2,60,0,79,75,2,0,1,0,0,80,
                        0,200,0,100,0,150,5,1,1,252,161,22,28,12,15,49,14,22,28,12,15,49,18,22,27,12,23,32,13,22,28,12,2,25,36,1,8,82,0,0,0,
                        22,12,30,15,41,30,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,
                        255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,
                        255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,
                        255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,
                        255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255]

        # next is version from 2023-02-04:
        # power is ON
        cfg600_242_2 = [0,0,0,2,1,0,0,150,1,164,63,128,0,0,16,104,65,32,0,0,164,16,66,200,0,0,0,63,0,0,0,0,
                        1,3,0,0,0,0,255,255,255,255,255,255,0,1,0,120,10,0,73,60,0,10,255,0,0,0,10,3,1,10,0,
                        150,0,63,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,
                        0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,
                        0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,
                        0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,119,119,119,46,103,109,99,109,97,112,46,
                        99,111,109,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,108,111,103,50,46,97,115,112,0,0,0,
                        0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,
                        0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,
                        0,0,0,0,0,0,0,0,0,5,0,2,60,0,96,73,2,0,0,0,1,14,0,200,0,100,0,150,5,1,2,72,161,0,
                        0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,8,82,0,0,0,23,2,4,15,18,39,255,
                        255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,
                        255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,
                        255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,
                        255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,
                        255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,
                        255,255,255,255,255,255,255,255,255,255,255]


        # 'GMC-600+Re 2.46' from Bob on 2023-07-20
        cfg600Bob =    [0, 0, 0, 2, 181, 0, 0, 150, 16, 104, 65, 32, 0, 0, 164, 16, 66, 200, 0, 0, 52, 80, 67, 250, 0, 0, 0, 63, 0, 0, 0,
                        0, 0, 2, 0, 0, 0, 0, 255, 255, 255, 255, 255, 255, 0, 1, 0, 120, 10, 255, 255, 60, 0, 10, 255, 0, 0, 0, 10, 0, 0,
                        10, 0, 150, 0, 63, 0, 0, 0, 66, 83, 69, 32, 68, 73, 83, 69, 65, 83, 69, 0, 95, 53, 48, 53, 65, 0, 0, 0, 0, 0, 0,
                        0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                        0, 0, 0, 107, 97, 110, 106, 117, 105, 115, 98, 111, 98, 119, 97, 121, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                        0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 87, 87,
                        87, 46, 71, 77, 67, 77, 65, 80, 46, 67, 79, 77, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 108, 111, 103,
                        50, 46, 97, 115, 112, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 48, 53, 55, 49, 49, 0,
                        0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 51, 52, 48, 48, 50, 54, 52, 55, 54, 55,
                        49, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 60, 0, 83, 76, 2, 0, 1, 0, 0, 0, 0, 200,
                        0, 150, 4, 126, 5, 1, 1, 250, 161, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 104, 66,
                        0, 0, 0, 0, 0, 16, 104, 0, 0, 164, 16, 0, 3, 52, 80, 0, 6, 104, 160, 0, 12, 209, 64, 0, 32, 11, 32, 65, 32, 0, 0, 66,
                        200, 0, 0, 67, 250, 0, 0, 68, 122, 0, 0, 68, 250, 0, 0, 69, 156, 64, 0, 23, 7, 20, 12, 2, 47, 255, 255, 255, 255, 255,
                        255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255,
                        255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255,
                        255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255,
                        255, 255]

        # Ihab17 aus folder 2024-02-20
        cfg600_252_1 =  [  0,   0,   0,   0,   1,   0,   0, 150,  13, 213,  65,  32,   0,   0, 124, 126,  66, 200,   0,   0,
                        183, 200,  67, 250,   0,   0,   2,  63,   0,   0,   0,   0,   1,   3,   0,   0,   0,   0, 255, 255,
                        255, 255, 255, 255,   0,   1,   0, 120,  10,   0, 178,  60,   0,  10, 255,   0,   0,   0,  10,   3,
                        1,  10,   0, 150,   0,  63,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,
                        0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,
                        0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,
                        0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,
                        0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,
                        0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,
                        0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0, 119, 119, 119,
                        46, 103, 109,  99, 109,  97, 112,  46,  99, 111, 109,   0,   0,   0,   0,   0,   0,   0,   0,   0,
                        0,   0,   0,   0,   0,   0,   0,   0,   0, 108, 111, 103,  50,  46,  97, 115, 112,   0,   0,   0,
                        0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,
                        0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,
                        0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,
                        0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,
                        0,   0,   0,   0,   0,   5,   0,   2,  60,   0,  76,  72,   2,   0,   1,   0,   1,  14,   0, 200,
                        0, 100,   0, 150,   5,   1,   1, 251, 161,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,
                        0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   1, 192, 198,  45,   0,   0,   0,
                        0,  13, 213,   0,   0, 124, 126,   0,   1, 183, 200,   0,   2, 203, 203,   0,   3, 125, 122,   0,
                        4,  78, 195,  65,  32,   0,   0,  66, 200,   0,   0,  67, 250,   0,   0,  68, 122,   0,   0,  68,
                        250,   0,   0,  69, 156,  64,   0,   0,  24,   2,  16,  16,  39,  32, 255, 255, 255, 255, 255, 255,
                        255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255,
                        255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255,
                        255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255,
                        255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255]


        cfg600_252_2 =  [  1,   0,   0,   0,   1,   0,   0, 150,  13, 213,  65,  32,   0,   0, 124, 126,  66, 200,   0,   0,
                        183, 200,  67, 250,   0,   0,   2,  63,   0,   0,   0,   0,   1,   3,   0,   0,   0,   0, 255, 255,
                        255, 255, 255, 255,   0,   1,   0, 120,  10, 255, 255,  60,   0,  10, 255,   0,   0,   0,  10,   3,
                        1,  10,   0, 150,   0,  63,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,
                        0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,
                        0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,
                        0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,
                        0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,
                        0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,
                        0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0, 119, 119, 119,
                        46, 103, 109,  99, 109,  97, 112,  46,  99, 111, 109,   0,   0,   0,   0,   0,   0,   0,   0,   0,
                        0,   0,   0,   0,   0,   0,   0,   0,   0, 108, 111, 103,  50,  46,  97, 115, 112,   0,   0,   0,
                        0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,
                        0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,
                        0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,
                        0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,
                        0,   0,   0,   0,   0,   5,   0,   2,  60,   0,  76,  72,   2,   0,   1,   0,   1,  14,   0, 200,
                        0, 100,   0, 150,   5,   1,   1, 251, 161,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,
                        0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   1, 192, 198,  45,   0,   0,   0,
                        0,  13, 213,   0,   0, 124, 126,   0,   1, 183, 200,   0,   2, 203, 203,   0,   3, 125, 122,   0,
                        4,  78, 195,  65,  32,   0,   0,  66, 200,   0,   0,  67, 250,   0,   0,  68, 122,   0,   0,  68,
                        250,   0,   0,  69, 156,  64,   0,   0,  24,   4,  22,   8,  18,   0, 255, 255, 255, 255, 255, 255,
                        255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255,
                        255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255,
                        255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255,
                        255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255]


        for i in range(len(cfg600_252_1)):
            print("i={:3d}   #1 {:3d}   #2 {:3d}  #1-#2 {:3d}".format(i, cfg600_252_1[i], cfg600_252_2[i], cfg600_252_1[i] - cfg600_252_2[i]))

        lcfg = cfg600_252_2

        if g.GMCpowerIsON: lcfg = [0] + lcfg[1:]    # power is ON
        else:              lcfg = [1] + lcfg[1:]    # power is OFF

        # use only for scanning the configuration memory for calibration points
        scanCFG(lcfg)

        cfg = bytes(lcfg)


    elif b"GMC-800" in g.GMCVersion:
        # MaoBra's counter GMC-800
        #
        # power is ON:
        # next is 1st version
        # power is ON
        cfg800_108   = [  0,   1, 255,   0, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255,
                        255, 255, 255, 255, 255, 255,   1, 255, 255, 255, 255, 255,   2, 255, 255, 255, 255, 255, 255, 255,
                        255, 255, 255, 255,   1, 255, 255, 255, 255, 255, 255, 255,   0,   3, 255, 255, 255, 255, 255,   0,
                          1, 255, 255, 255, 255, 255, 255, 255, 255,   3, 255,  10,  44,   0,   0,   6,   2,   0,   0,  60,
                         20,   0,   0, 120,  40,   0,   1,  44, 100,   0,   2,  88, 200,   0,   4, 177, 144,  65,  32,   0,
                          0,  66, 200,   0,   0,  67,  72,   0,   0,  67, 250,   0,   0,  68, 122,   0,   0,  68, 250,   0,
                          0,   0,  10,   1,   1,   0,   0,   0, 100,   1, 255,   6, 255, 255, 255, 255, 255, 255, 255, 255,
                        255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255,
                        255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255,
                        255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255,
                        255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255,
                        255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255,
                        255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255,
                        255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255,
                        255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255,
                        255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255,
                        255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255,
                        255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255,
                        255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255,
                        255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255,
                        255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255,
                        255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255,
                        255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255,
                        255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255,
                        255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255,
                        255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255]


        # for i in range(len(cfg800_108)):
        #     print("i={:3d}   #1 {:3d}   #2 {:3d}  #1-#2 {:3d}".format(i, cfg800_108[i], cfg800_108[i], cfg800_108[i] - cfg800_108[i]))

        lcfg = cfg800_108

        if g.GMCpowerIsON: lcfg = [0] + lcfg[1:]    # power is ON
        else:              lcfg = [1] + lcfg[1:]    # power is OFF

        # # use only for scanning the configuration memory for calibration points
        # # the points are identified
        # scanCFG(lcfg)

        cfg = bytes(lcfg)


# 256 == configsize

    elif b"GMC-300SRe 1.03" in g.GMCVersion or b"GMC-320SRe 1.03" in g.GMCVersion :
        # First 0 indicates that power is ON
        cfg300S_103 = [0,1,1,0,1,1,0,100,0,105,102,102,38,63,4,26,0,0,208,64,41,4,0,0,130,66,9,0,0,0,63,0,1,2,0,0,0,0,255,255,255,255,255,255,0,1,
                       0,120,21,0,29,60,1,2,255,1,0,252,10,0,0,10,0,100,0,0,0,0,63,3,23,3,31,16,0,46,255,255,255,255,255,255,255,255,255,255,255,
                       255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,
                       255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,
                       255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,
                       255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,
                       255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,
                       255,255,255,255,255,255,255,255,255,255,255,255,255,255]

        # not tested:
        #   to simulate WiFi settings just fill up config up to 256 bytes
        #   cfg300SWiFi = (cfg300S[:69] + b'abcdefghijklmnopqrstuvwxyz0123456789' * 10)[:256]

        # for i in range(256):
        #     print("i={:3d}   #1 {:3d}   #2 {:3d}  #1-#2 {:3d}".format(i, cfg300S__103_1[i], cfg300S_103_2[i], cfg300S__103_1[i] - cfg300S_103_2[i]))


        if g.GMCpowerIsON: cfg300S_103 = [0] + cfg300S_103[1:]    # power is ON
        else:              cfg300S_103 = [1] + cfg300S_103[1:]    # power is OFF

        # for a in cfg300S_103: cfg += bytes([a]) # using dec data
        cfg = bytes(cfg300S_103)


    elif b"GMC-320Re 5." in g.GMCVersion :
        # 320v5 device (with WiFi)
        # to simulate WiFi settings just fill up config up to 256 bytes
        cfg320plus = [255, 0, 0, 2, 31, 0, 0, 100, 0, 60, 20, 174, 199, 62, 0, 240, 20, 174, 199, 63, 3, 232, 0, 0, 208, 64, 0, 0, 0, 0,
                      63, 0, 2, 2, 0, 0, 0, 0, 255, 255, 255, 255, 255, 255, 0, 1, 0, 120, 25, 255, 255, 60, 1, 8, 255, 1, 0, 254, 10, 0,
                      1, 10, 0, 100, 0, 0, 0, 0, 63, 17, 5, 23, 16, 46, 58, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255,
                      255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255,
                      255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255,
                      255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255,
                      255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255,
                      255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255,
                      255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255,
                      255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255,
                      255, 255, 255, 255, 255, 255, 255, 255]

        if g.GMCpowerIsON: cfg320plus = [0]   + cfg320plus[1:]    # power is ON
        else:              cfg320plus = [255] + cfg320plus[1:]    # power is OFF

        cfg320plusWiFi = (cfg320plus[:69] + b'abcdefghijklmnopqrstuvwxyz0123456789' * 10)[:256]

        # for a in cfg320plusWiFi: cfg += bytes([a]) # using dec data
        cfg = bytes(cfg320plusWiFi)


    else:
        # my 'GMC-300Re 4.54' device
        cfg300plus = [0, 0, 0, 2, 31, 0, 0, 100, 0, 60, 20, 174, 199, 62, 0, 240, 20, 174, 199, 63, 3, 232, 0, 0, 208, 64, 7, 0, 0, 0, 63, 0,
                      1, 0, 0, 0, 0, 0, 255, 255, 255, 255, 255, 255, 0, 1, 0, 120, 25, 255, 255, 60, 0, 8, 255, 1, 0, 252, 10, 0, 1, 10, 23,
                      7, 18, 13, 48, 27, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255,
                      255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255,
                      255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255,
                      255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255,
                      255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255,
                      255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255,
                      255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255,
                      255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255]

        if g.GMCpowerIsON: cfg300plus = [0]   + cfg300plus[1:]    # power is ON
        else:              cfg300plus = [255] + cfg300plus[1:]    # power is OFF
        cfg = bytes(cfg300plus)

        # config is from 320+ taken on: 2017-05-26 15:29:38
        # power is off:
        cfg320plus = [255,0,0,2,31,0,0,100,0,60,20,174,199,62,0,240,20,174,199,63,3,232,0,0,208,64,0,0,0,0,63,0,2,2,0,0,0,0,255,255,255,255,255,
                      255,0,1,0,120,25,255,255,60,1,8,255,1,0,254,10,0,1,10,0,100,0,0,0,0,63,17,5,23,16,46,58,255,255,255,255,255,255,255,255,
                      255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,
                      255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,
                      255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,
                      255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,
                      255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,
                      255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255]

        if g.GMCpowerIsON: cfg320plus = [0]   + cfg320plus[1:]    # power is ON
        else:              cfg320plus = [255] + cfg320plus[1:]    # power is OFF

        # for a in cfg320plus:  cfg += bytes([a])                   # using dec data
        cfg = bytes(cfg320plus)

    return cfg


def scanCFG(cfg):
    """scan the cfg for possible calibration points"""

    print("Scanning for possible calibration points")

    g.GMC_endianness = "big"    # use big-endian ---   500er, 600er

    print()
    print("Color Code:")
    print(TGREEN,  "matches CPM pre-selections", TDEFAULT)
    print(TCYAN,   "matches µSv pre-selections", TDEFAULT)
    print(BOLDRED, "sensitivity 1 ... 10 000", TDEFAULT)
    print("","sensitivity not reasonable", TDEFAULT)

    # 2-Bytes
    print("\nChecking for 2 Byte values")
    if g.GMC_endianness == "big":
        print("Endianness:            BIG")
        floatString = ">f"                                                    # use big-endian ---   500er, 600er:
        int16String = ">H"
    else:
        print("Endianness:            LITTLE")
        floatString = "<f"                                                    # use little-endian -- other than 500er and 600er
        int16String = "<H"

    bcfg = bytes(cfg)

    for i in range(len(cfg) - 5):
        cpm = struct.unpack(int16String, bcfg[i : i + 2])[0]
        usv = struct.unpack(floatString, bcfg[i + 2 : i + 2 + 4])[0]

        if cpm in (60, 240, 1000, 2000, 4000):
            sensitivity = cpm / usv
            calibration       = usv / cpm
            print(TGREEN, "Index: {:3d}  CPM: {:5d}  usv:{:12.3f}    Sens:{:12.3f}    Calib:{:12.6f}".format(i, cpm, usv, sensitivity, calibration), TDEFAULT)

        if usv in (0.30, 1.20, 5.00, 10.00, 20.00):
            sensitivity = cpm / usv
            calibration = usv / cpm
            print(TCYAN, "Index: {:3d}  CPM: {:5d}  usv:{:12.3f}    Sens:{:12.3f}    Calib:{:12.6f}".format(i, cpm, usv, sensitivity, calibration), TDEFAULT)

        if abs(usv) < 1e-7 or abs(usv) > 1e+7:
            usv = g.NAN
        sensitivity = cpm / usv

        if cpm == 0:    calibration = g.NAN
        else:           calibration = usv / cpm

        if sensitivity > 1 and sensitivity < 10000: color = BOLDRED
        else:                                       color = ""
        if color == BOLDRED: print(color, "Index: {:3d}  CPM: {:5d}  usv:{:12.3f}    Sens:{:12.3f}    Calib:{:12.6f}".format(i, cpm, usv, sensitivity, calibration), TDEFAULT)


    # 4 Bytes
        # GMC 600+ has 6 calibration points (seen from the counter)
        # 003541 CPM, 10 uSv/h      --> 354.1   CPM / (µSv/h)
        # 031870 CPM, 100 uSv/h     --> 318.7
        # 112584 CPM, 500 uSv/h     --> 225.168
        # 183243 CPM, 1000 uSv/h    --> 183.243
        # 228730 CPM, 2000 uSv/h    --> 114.365
        # 282307 CPM, 5000 uSv/h    -->  56.461

    print("\nChecking for 4 Byte values")

    if g.GMC_endianness == "big":
        print("Endianness:            BIG")
        floatString = ">f"                                                    # use big-endian ---   500er, 600er:
        int32String = ">L"
    else:
        print("Endianness:            LITTLE")
        floatString = "<f"                                                    # use little-endian -- other than 500er and 600er
        int32String = "<L"
    bcfg = bytes(cfg)
    for i in range(len(cfg) - 9):
        cpm = struct.unpack(int32String, bcfg[i     : i + 4])[0]
        usv = struct.unpack(floatString, bcfg[i + 4 : i + 4 + 4])[0]

        if cpm in (3541, 31870, 112584, 183243, 228730, 282307):
            sensitivity = cpm / usv
            calibration       = usv / cpm
            print(TGREEN, "Index: {:3d}  CPM: {:10d}  usv:{:12.3f}    Sens:{:12.5g}    Calib:{:12.6f}".format(i, cpm, usv, sensitivity, calibration), TDEFAULT)

        if cpm in (60, 240, 1000, 2000, 4000):
            sensitivity = cpm / usv
            calibration       = usv / cpm
            print(TGREEN, "Index: {:3d}  CPM: {:10d}  usv:{:12.3f}    Sens:{:12.5g}    Calib:{:12.6f}".format(i, cpm, usv, sensitivity, calibration), TDEFAULT)

        if usv in (10.00, 100.00, 500, 1000, 2000, 5000):
            sensitivity = cpm / usv
            calibration = usv / cpm
            print(TCYAN,  "Index: {:3d}  CPM: {:10d}  usv:{:12.3f}    Sens:{:12.5g}    Calib:{:12.6f}".format(i, cpm, usv, sensitivity, calibration), TDEFAULT)

        if abs(usv) < 1e-7 or abs(usv) > 1e+7:
            usv = g.NAN
        sensitivity = cpm / usv

        if cpm == 0:    calibration = g.NAN
        else:           calibration = usv / cpm


        if sensitivity > 1 and sensitivity < 10000: color = BOLDRED
        else:                                       color = ""
        if color == BOLDRED: print(color, "Index: {:3d}  CPM: {:10d}  usv:{:12.3f}    Sens:{:12.3f}    Calib:{:12.6f}".format(i, cpm, usv, sensitivity, calibration), TDEFAULT)

    # sys.exit(1)


def getCounts(cpmtype):

    defname = "getCounts({}): ".format(cpmtype)

    cpm1st = np.sum(g.CPSqueueFirstTube)
    cpm2nd = np.sum(g.CPSqueueSecondTube)
    cps1st = g.CPSqueueFirstTube[-1]
    cps2nd = g.CPSqueueSecondTube[-1]

    if   cpmtype == "CPM":     val = cpm1st + cpm2nd
    elif cpmtype == "CPS":     val = cps1st + cps2nd
    elif cpmtype == "CPM1st":  val = cpm1st
    elif cpmtype == "CPS1st":  val = cps1st
    elif cpmtype == "CPM2nd":  val = cpm2nd
    elif cpmtype == "CPS2nd":  val = cps2nd

    if b"GMC-3" in g.GMCVersion:
        if val < 2**16: bval = struct.pack(">H", val)             # 2 bytes for 300 series, limit is 2^16
        else:           bval = struct.pack(">H", 2**16 - 1)       #
    else:
        bval = struct.pack(">I", val)                             # 4 bytes for 500, 600, 800 series

    print(defname, "bval: {} --> {}     val: {}".format(bval, ", ".join(str(b) for b in bval), val))

    return bval


def getDatetime():
    """return a Datetime as the counter would"""

    defname = "getDatetime: "

    # convert Computer DateTime to byte sequence format needed by counter
    timelocal     = list(time.localtime())                          # timelocal: 2018-04-19 13:02:50 --> [2018, 4, 19, 13, 2, 50, 3, 109, 1]
    print(defname, "timelocal: ", timelocal)
    timelocal[0] -= 2000
    dtrec         = dt.datetime(timelocal[0] + 2000, timelocal[1], timelocal[2], timelocal[3], timelocal[4], timelocal[5])

    btimelocal    = b''
    for i in range(0, 6):  btimelocal += bytes([timelocal[i]])
    print(defname, "creating Datetime:  now:", timelocal[:6], ", coded:", btimelocal, "  ", dtrec)

    return btimelocal + b"\xaa"


def setDatetime(dt):
    """receive the Datetime as created by GeigerLog"""

    defname = "setDatetime: "
    print(defname, "receiving: ", dt)

    return b"\xaa"


def setPower(powerstate):
    """receive the Datetime as created by GeigerLog"""

    defname = "setPower: "
    print(defname, "New Powerstate: ", powerstate)
    if powerstate == "ON":  g.GMCpowerIsON = True
    else:                   g.GMCpowerIsON = False

    return b""


def clearTerminal():
    """clear the terminal"""

    os.system('cls' if os.name == 'nt' else 'clear')
    # print("os.name: ", os.name) # os.name:  'posix' (on Linux)


### end function code ################################################################################################

if __name__ == '__main__':

    try:
        clearTerminal()
        init()

    except KeyboardInterrupt:
        print()
        print("Exit by CTRL-C")
        print()
        os._exit(0)

