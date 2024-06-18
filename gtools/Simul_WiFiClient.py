#! /usr/bin/env python3
# -*- coding: UTF-8 -*-

"""
Simul_WiFiClient.py - a utility which acts like a WiFiClient device by calling GeigerLog's
                    built-in web server with a GET message carrying the data.

                    It can act either as    WiFiClientType = GENERIC
                                   or as    WiFiClientType = GMC

                    -   As GENERIC it will be sending all of the possible 12
                        GeigerLog variables, with each value being a random number.

                    -   As GMC     it will be sending 3 variables with each value
                        being a number as it might have come from a GMC counter.

                    You can also test the GLrelay.py program with this Simul_WiFiClient
                    by setting the below python variable TargetPort to the port
                    where GLrelay will be listeing. This will be typically be
                    port 80, as this mimicks a GMC counter sending data.

Start with:     Simul_WiFiClient.py
                Simul_WiFiClient.py -h  for Help Info on configuration
Stop with:      CTRL-C
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


__author__              = "ullix"
__copyright__           = "Copyright 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024"
__credits__             = [""]
__license__             = "GPL3"
__version__             = "1.0"


# importing modules - available in std Python
import sys, os, time, datetime      # basic modules
import urllib.request               # making Web calls
import getopt                       # parsing command line options
import socket                       # for finding the IP address
import ipaddress                    # for checking for valid IP address
import psutil                       # to find running scripts


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
class Simul_WiFiClientVars:
    """A class with the only task to make certain variables global"""

    #######  Do **NOT** change these WiFi* variables here ! change via Command Line !! #############################
    #######  like:  Simul_WiFiClient.py -I 10.0.0.20 -P 8000 -c 1 -T GMC   ###########################################

    WiFiTargetIP        = "0.0.0.0"             # IP of computer to RECEIVE data from this Simul_WiFiClient;
                                                # this is either:    GeigerLog, then TargetPort should be 8000
                                                #                 or GLrelay,   then TargetPort should be 80
    WiFiTargetPort      = 80                    # see above 2 lines, likely either '80' or '8000'
    WiFiClientType      = "GMC"                 # use "GMC" or "GENERIC"
    WiFiCycleTime       = 1                     # default = 1 sec, but 1 sec is too fast when GLrelay uses delay of 1 sec
    ################################################################################################################

    # flags
    devel               = False
    RunningScripts      = {}
    RunningScripts["geigerlog"] = False
    RunningScripts["GLrelay"]   = False

    helpOptions  = """
            Usage:  Simul_WiFiClient.py [Options]

            Start:  Simul_WiFiClient.py
            Stop:   CTRL-C

            Options:
                -h, --help          Show this help and exit
                -V, --Version       Show version status and exit
                -c, --cycle         Set the cycle time in sec (default 1 sec)
                -I, --TargetIP      Set the IP of the target computer
                -P, --TargetPort    Set the Port of the target computer (default 8000)
                -T, --Type          Set the Type of client to simulate 'GMC' (default) or 'GENERIC'

            Example: start Simul_WiFiClient.py with options:
                Simul_WiFiClient.py --cycle 3 --TargetIP=10.0.0.20 --TargetPort=8000  # set cycle time = 3 sec, and Target Address to '10.0.0.20:8000'
            or: Simul_WiFiClient.py -c 3 -I 10.0.0.20 -P 8000 -T GMC                  # same, and also set Type
    """


g = Simul_WiFiClientVars      # initiate global vars


def longstime():
    """Return current time as YYYY-MM-DD HH:MM:SS.mmm, (mmm = millisec)"""

    return dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3] # ms resolution


def exceptPrint(e, srcinfo):
    """Print exception details (errmessage, file, line no)"""

    exc_type, exc_obj, exc_tb = sys.exc_info()
    fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]    # which file?

    print(longstime(), "EXCEPTION: '{}' in file: '{}' in line {}".format(e, fname, exc_tb.tb_lineno))
    if srcinfo > "": print(longstime(), srcinfo)


try:
    # import modules - requiring installation via pip
    import numpy           as np        # for random f'ons
except Exception as e:
    print()
    print("#" * 100)
    exceptPrint(e, "")
    print("To run Simul_WiFiClient.py these additional modules are required:")
    print(" - numpy")
    print("Please install with:  'python -m pip install -U <module name>'")
    sys.exit()


def clearTerminal():
    """clear the terminal"""

    # The name of the operating system dependent module imported. The following
    # names have currently been registered: 'posix', 'nt', 'java'. (on Linux: posix)

    # if "LINUX" in platform.platform().upper():
    #     # clear the terminal
    #     os.system("export TERM=xterm-256color")     # needed to prep for clear (week, seems to work without it???)
    #     os.system("clear")                          # clear terminal

    os.system('cls' if os.name == 'nt' else 'clear')
    # print("os.name: ", os.name) # os.name:  posix (on Linux)


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


def isValidIP(ip):
    """determine validity of given IP address"""

    defname = "isValidIP: "

    try:
        ipaddress.ip_address(ip)
        return True
    except Exception as e:
        # exceptPrint(e, defname)
        return False


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

    if g.WiFiTargetPort == 80 and not g.RunningScripts["GLrelay"]:
        print(TRED + "You have configured WiFiPort = 80, but GLrelay is not running. This will fail!" + TDEFAULT)
        x = input("press Enter to continue anyway")
    elif not g.RunningScripts["geigerlog"] and not g.RunningScripts["GLrelay"]:
        print(TRED + "Neither GeigerLog nor GLrelay is running. There is no listener for this Simul_WiFiClient!" + TDEFAULT)
        x = input("Press Enter to continue anyway")
    print()


def main():
    """Loop until stopped by CTRL-C"""

    defname = "main: "

    # clear screen
    clearTerminal()

    # header
    print(BGREEN + "*" * 150 + TDEFAULT)

    # get and set the default IPs
    # by default GLrelay.py and GeigerLog are running on the same computer having the same IP; change with command line options
    g.WiFiTargetIP   = getIP()

    if "devel" in sys.argv: g.devel = True

    # parse command line options
    try:
        # sys.argv[0] is progname
        opts, args = getopt.getopt(sys.argv[1:], "hdVc:I:P:T:", ["help", "debug", "Version", "cycle=", "TargetIP=", "TargetPort=", "Type="])
    except getopt.GetoptError as e :
        # print info like "option -x not recognized", then exit
        msg = "For Help use: './Simul_WiFiClient.py -h'"
        exceptPrint(e, msg)
        return 1

    # process the options
    for opt, optval in opts:

        if   opt in ("-h", "--help"):                       # show the help info
            print(g.helpOptions)
            return 1

        elif opt in ("-V", "--Version"):                    # show the Simul_WiFiClient.py version
            print("Simul_WiFiClient.py Version:", __version__)
            return 1

        elif opt in ("-c", "--cycle"):                      # set the cycle time in sec
            try:    ct = float(optval)
            except: ct = -1
            if ct > 0:
                g.WiFiCycleTime = ct
            else:
                print("The configured cycle time of '{}' sec is not valid.".format(optval))
                print("It can be any number greater than zero")
                return 1

        elif opt in ("-I", "--TargetIP"):                   # re-define the Target IP address
            if isValidIP(optval):
                g.WiFiTargetIP = optval
            else:
                print("The configured Target IP address '{}' is not valid. See: https://en.wikipedia.org/wiki/IP_address".format(optval))
                print("As example, this computer has the IP address: '{}'".format(g.WiFiTargetIP))
                return 1

        elif opt in ("-P", "--TargetPort"):                 # re-define the Target Port number
            try:    pnum = int(float(optval))
            except: pnum = -1
            if pnum >= 1 and pnum <= 65535:
                g.WiFiTargetPort = pnum                         # valid port
            else:
                print("The configured Target Port number '{}' is not valid".format(optval))
                print("Allowed range for Port numbers is 1 ... 65535 (incl.)")
                return 1

        elif opt in ("-T", "--Type"):                       # re-define the Client Type as "GMC" or "GENERIC"
            if optval in ("GMC", "GENERIC"):
                g.WiFiClientType = optval
            else:
                print("The configured Client Type '{}' is not valid".format(optval))
                print("Only 'GMC' and 'GENERIC' are allowed")
                return 1

    getRunningScripts()


    baseurl  = "http://{}:{}".format(g.WiFiTargetIP, g.WiFiTargetPort)
    numbers  = [0] * 12              # THIS IS FOR THE GENERIC DEVICE
    answer   = ""
    status   = 0
    GETcalls = 0
    tDurAvg  = 0

    while True:
        tstart = time.time()

        # make the data
        if g.WiFiClientType == "GENERIC":
            # THIS IS FOR THE GENERIC DEVICE - a bunch of random normal numbers
            for i in range(12): numbers[i] = round(np.random.normal(i + 10, 0.5), 2)
            dataurl = baseurl + "/GENERIC" + "?M={}&S={}&M1={}&S1={}&M2={}&S2={}&M3={}&S3={}&T={}&P={}&H={}&X={}".format(*numbers)

        else:
            # THIS IS FOR THE GMC DEVICE - a single poisson, an average of poissons over 1 h, and a uSv value calculated from CPM
            meanCPM = 30
            cpm     = np.random.poisson(meanCPM)
            acpm    = round(np.average(np.random.poisson(meanCPM, size= 60)), 2)   # average of data over 1 hour
            usv     = round(cpm / 154, 2)
            dataurl = baseurl + "/GMC" + "?CPM={}&ACPM={}&uSV={}".format(cpm, acpm, usv)

        # upload the data via GET call
        try:
            with urllib.request.urlopen(dataurl) as response:
                answer = response.read()
                status = response.status

            tdur      = 1000 * (time.time() - tstart)
            tDurAvg   = (tDurAvg * GETcalls + tdur ) / (GETcalls +1)
            GETcalls += 1
            print(longstime() + " Simul_WiFiClient: {:5d}  {:65s} answer: {}{:30s}{}  status: {}   dur: {:5.2f} ms  durAvg: {:5.2f} ms".format(GETcalls, dataurl, BRED, str(answer), TDEFAULT, status, tdur, tDurAvg))

        except Exception as e:
            emsg = "Target could NOT be reached with URL: {}".format(dataurl)
            if g.devel: exceptPrint(e, "")
            print(emsg)
            if g.WiFiTargetPort < 1024: print(TRED + "As TargetPort {} is privileged you must be running GLrelay AND running it with ADMINISTRATIVE RIGHTS!".format(g.WiFiTargetPort), TDEFAULT)
            else:                       print(TRED + "Is GeigerLog both RUNNING AND LOGGING?", TDEFAULT)
            print()
            time.sleep(2)                               # 2 sec sleep on failure

        time.sleep(g.WiFiCycleTime)


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print()
        print("Exit by CTRL-C")

    print()
