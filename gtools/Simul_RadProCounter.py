#!/usr/bin/python3
# -*- coding: UTF-8 -*-

"""
Simul_RadProCounter.py - GeigerLog's Simulator for a counter with RadPro firmware

use with GeigerLog to simulate responses of a RadPro Geiger counter. See more in
the header of file gdev_radpro.py located in the GeigerLog folder.

- MUST start as SUDO (!):                      sudo ./Simul_RadProCounter.py
- pyserial must have been installed as root:   sudo python -m pip install -U pyserial
- socat must have been installed as root:      sudo apt install socat

The communication between GeigerLog and the Pseudo device is logged into file
Simul_RadProCounter.log
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
__version__         = "1.0pre01"

import sys, os, io, time
import datetime                  as dt
import subprocess
import serial                               # serial port
import serial.tools.list_ports              # allows listing of serial ports
import numpy                     as np      # for Poisson values
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
# inverted colors
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
    """vars - global for this file only"""

    NAN                     = float("nan")
    RadProHardwareVersion   = "FNIRSI GC-01 (CH32F103C8)"
    RadProSoftwareVersion   = "Rad Pro 2.0rc2"
    RadProDeviceID          = "88eb5698"

    Simul_RadProThreadRun   = False
    Simul_RadProThread      = None

    CPSqueue                = deque([], 60)     # size limited to 60 CPS values
    CPSmean                 = 100
    CPStotalCounts          = 0

    helpOptions             = """
            Usage:  Simul_RadProCounter.py [Options]

            Start:  Simul_RadProCounter.py
            Stop:   CTRL-C

            Options:
                -h, --help          Show this help and exit
                -V, --Version       Show version status and exit
                -C, --Counter       Set the counter name (FNIRSI GC-01)                Default: GC-01
                                    (No other counter defined so far)

            Example: starting Simul_WiFiClient.py with options:
                                 Simul_RadProCounter.py --Counter=GC-01
            or with same result: Simul_RadProCounter.py -C GC-01
    """

# instantiate class vars
g = globalvars()

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
    """Init the Simul_RadProCounter, start checking the Serial for requests, and answer"""

    defname = "init: "

    print("\n----------------------------- Simul_RadProCounter.py ------------------------------------")
    print("Program File:         ", __file__)

    # parse command line options
    try:
        # sys.argv[0] is progname
        opts, args = getopt.getopt(sys.argv[1:], "hdVC:F:S:", ["help", "debug", "Version", "Counter=", "FirstTube=", "SecondTube="])
    except getopt.GetoptError as e :
        # print info like "option -x not recognized", then exit
        msg = "For Help use: './Simul_RadProCounter.py -h'"
        exceptPrint(e, msg)
        return 1

    # process the options
    for opt, optval in opts:

        if   opt in ("-h", "--help"):                       # show the help info
            print(g.helpOptions)
            return 1

        elif opt in ("-V", "--Version"):                    # show the Simul_WiFiClient.py version
            print("Simul_RadProCounter.py Version:", __version__)
            return 1

        elif opt in ("-C", "--Counter"):                    # set the counter name
            g.RadProVersion = optval.strip()



    print("Config:")
    print("   Hardware:          ", g.RadProHardwareVersion)
    print("   Software:          ", g.RadProSoftwareVersion)
    print("   Device ID:         ", g.RadProDeviceID)
    print("   CPSmean:           ", g.CPSmean)
    print()

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

    time.sleep(0.01) # socat needs ~0.001 sec to complete its action; but then keeps running

    print("\nDevice permissions:")
    try:
        print("   /dev/ttyS90: ", oct(os.stat('/dev/ttyS90')[0]))
        print("   /dev/ttyS91: ", oct(os.stat('/dev/ttyS91')[0]))
    except Exception as e:
        print("Listing permissions failed with Exception: ", e)
        print("??????????   Forgot to start program with 'sudo'  ???????????\n\n")
        sys.exit()

    # print("\nChanging permission with os.chmod on: ", '/dev/ttyS90', '/dev/ttyS91', 'to 0o777')
    # start = time.time()
    while True:
        try:
            os.chmod('/dev/ttyS90', 0o777)
            os.chmod('/dev/ttyS91', 0o777)
            break
        except:
            pass
    # print("   success after {:0.3f} ms".format((time.time() - start) * 1000))

    print("\nDevice permissions after changing:")
    print("   /dev/ttyS90: ", oct(os.stat('/dev/ttyS90')[0]))
    print("   /dev/ttyS91: ", oct(os.stat('/dev/ttyS91')[0]))

    print("\nList of Ports found on system (including linked ports): ")
    lps = serial.tools.list_ports.comports(include_links=True)
    lps.sort()
    for lp in lps:  print(" ", lp)

    g.Simul_RadProThreadRun         = True
    g.Simul_RadProThread            = threading.Thread(target = Simul_RadProThreadTarget)
    g.Simul_RadProThread.daemon     = True   # must come before start: makes threads stop on exit!
    g.Simul_RadProThread.start()

    start           = time.time()
    counter         = 0
    portsim         = "/dev/ttyS91"
    loopcount       = 3000

    # create serial connection
    # for use of spy see: https://pyserial.readthedocs.io/en/latest/url_handlers.html
    # wser        = serial.serial_for_url("spy://{}?file=Simul_RadProCounter.log".format(portsim), baudrate=0, timeout=0.1, bytesize=8, parity="N")
    wser        = serial.Serial(portsim, baudrate=115200, timeout=0.05)
    print("\nSerial Handle: ", wser)
    print()
    print("Looping:")
    while True:
        wstart   = time.time()
        counter += 1
        brec = b""
        while True:
            # read the input - if there is any - for command
            cnt = wser.in_waiting
            if cnt > 0:     brec += wser.read(cnt)
            else:           break

        if brec > b"":
            # getting a request
            print("\nRequest  : {:30s}  on port '{}'".format(str(brec), portsim ))

            counter = 1

            if   brec.startswith(b"GET tubePulseCount"):                tag = bytes("OK {}\n".format(getCounts("CPS")), "ASCII")
            elif brec.startswith(b"GET tubeRate"):                      tag = bytes("OK {}\n".format(getCounts("CPM")), "ASCII")
            elif brec.startswith(b"GET deviceBatteryVoltage"):          tag = b"OK 4.567\n"
            elif brec.startswith(b"GET tubeTime"):                      tag = b"OK 115294\n"
            elif brec.startswith(b"GET tubeConversionFactor"):          tag = b"OK 153\n"
            elif brec.startswith(b"GET tubeDeadTime"):                  tag = b"OK 0.0001470\n"
            elif brec.startswith(b"GET tubeDeadTimeCompensation"):      tag = b"OK 1.234\n"
            elif brec.startswith(b"GET tubeBackgroundCompensation"):    tag = b"OK None\n"
            elif brec.startswith(b"GET tubeHVFrequency"):               tag = b"OK 9207.16\n"
            elif brec.startswith(b"GET tubeHVDutyCycle"):               tag = b"OK 0.7500\n"
            elif brec.startswith(b"GET tubeTime"):                      tag = b"OK 2024\n"
            elif brec.startswith(b"GET deviceTime"):                    tag = b"OK 1711988409\n"
            elif brec.startswith(b"GET deviceId"):                      tag = b"OK FNIRSI GC-01 (CH32F103C8);Rad Pro 2.0rc2;88eb5698;\n"
            elif brec.startswith(b"SET deviceTime"):                    tag = b"OK \n"
            else:                                                       tag = b"OK SIMUL UNDEFINED;shit;mist;kaese\n"

            wser.write(tag)
            print("Response : {} ".format(tag))
            print("Dur      : {:0.1f} ms".format(1000 * (time.time() - wstart) ))

        else:
            # no request coming in
            if counter % loopcount == 0:
                dur = 1000 * (time.time() - start)
                print("   Loops: {} in {:0.1f} ms per loop".format(loopcount,  dur / loopcount), flush=True)
                start = time.time()
            else:
                print("\033[#D", end="", flush=True) # printing ANSI codes  https://gist.github.com/fnky/458719343aabd01cfb17a3a4f7296797

        time.sleep(0.01) # 10 ms resolution


def Simul_RadProThreadTarget():
    """Get CPS every 1 second and add to the queue"""

    defname = "Simul_RadProThreadTarget: "

    # fill the queue for full CPM from beginning of recording
    for i in range(60):
        g.CPSqueue .append(np.random.poisson(g.CPSmean))

    # add CPSvalue every 1 sec to the queue and total CPS
    nexttime = time.time() + 1
    while g.Simul_RadProThreadRun:
        if time.time() >= nexttime:
            nexttime += 1
            newCPS    = np.random.poisson(g.CPSmean)
            g.CPSqueue .append(newCPS)
            g.CPStotalCounts += 100   #newCPS
        dt = (nexttime - time.time()) - 0.01
        time.sleep(max(0.001, dt))


def getCounts(cpmtype):

    defname = "getCounts({}): ".format(cpmtype)

    if   cpmtype == "CPM":  val = np.sum(g.CPSqueue)
    # else:                 val = g.CPSqueue[-1]
    else:                   val = g.CPStotalCounts

    # print("          ", defname, "val: {}".format(val))

    return val


def clearTerminal():
    """clear the terminal"""

    # print("os.name: ", os.name) # os.name:  'posix' (on Linux), 'nt' on Windows
    os.system('cls' if os.name == 'nt' else 'clear')


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

