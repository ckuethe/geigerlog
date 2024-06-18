#! /usr/bin/env python3
# -*- coding: UTF-8 -*-

"""
DMMWiFiClient.py - a utility which acts like a WiFiClient device by calling GeigerLog's
                   built-in web server with a GET message carrying the data.

                   It gets the voltage from an OWOL OW18E DMM, and sends it as WiFiClient

Start with:        DMMWiFiClient.py
                   DMMWiFiClient.py -h  for Help Info on configuration
Stop with:         CTRL-C

ATTENTION:         This works only with an OWON OW18E device
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

###############################################################################

# This code uses simplepyble !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

# https://simpleble.readthedocs.io/en/latest/simplepyble/usage.html
# pip install simplepyble
# Please take into consideration that when using this library on Linux, you will need to have the following dependencies installed:
# sudo apt-get install libdbus-1-dev
###############################################################################


__author__              = "ullix"
__copyright__           = "Copyright 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024"
__credits__             = [""]
__license__             = "GPL3"
__version__             = "1.0"


# importing modules - available in std Python
import sys, os, time                            # basic modules
import datetime         as dt                   # date and time
import urllib.request                           # making Web calls
import getopt                                   # parsing command line options
import socket                                   # for finding the IP address
import ipaddress                                # for checking for valid IP address
import simplepyble                              # the Bluetooth lib


# colors
TDEFAULT                = '\033[0m'             # default, i.e greyish
TRED                    = '\033[91m'            # red
BRED                    = '\033[91;1m'          # bold red
TGREEN                  = '\033[92m'            # light green
BGREEN                  = '\033[92;1m'          # bold green
TYELLOW                 = '\033[93m'            # yellow

###############################################################################################
# specific for OW18E
# ADDRESS = "A6:C0:80:E3:85:9D"
# CHARACTERISTIC_UUID = "0000fff4-0000-1000-8000-00805f9b34fb"        # Output: 23 f0 04 00 5b 0f
# CHARACTERISTIC_UUID = "00001801-0000-1000-8000-00805f9b34fb"      # Generic Attribute
# CHARACTERISTIC_UUID = '00001800-0000-1000-8000-00805f9b34fb'      # Generic Access
# CHARACTERISTIC_UUID = '0000180a-0000-1000-8000-00805f9b34fb'      # Device Information
# CHARACTERISTIC_UUID = '0000fff0-0000-1000-8000-00805f9b34fb'      # Unknown
# CHARACTERISTIC_UUID = '00010203-0405-0607-0809-0a0b0c0d1911'      # Proprietary
###############################################################################################


# globals
class Voltage_WiFiClientVars:
    """A class with the only task to make certain variables global"""

    #######  Do **NOT** change these WiFi* variables here; change via Command Line !! #############################
    #######  like:  DMMWiFiClient.py -I 10.0.0.20 -P 8000 -c 1 -T GMC   #######################################

    WiFiTargetIP        = "0.0.0.0"             # IP of computer to RECEIVE data from this VoltageWiFiClient
    WiFiTargetPort      = 4000                  # for GeigerLog the TargetPort should be 4000
    WiFiClientType      = "OW18E"               # so far "OW18E" is the only option
    WiFiCycleTime       = 1                     # default = 1 sec, but 1 sec is too fast when GLrelay uses delay of 1 sec
    ################################################################################################################

    # constants
    NAN                 = float("nan")

    # flags
    devel               = False

    # loop
    loop                = None
    lastupload          = time.time() #0             # a time.time()
    lasttime            = time.time()
    GETcalls            = 0
    durtime             = NAN
    tDurAvg             = 0

    # data
    DMMvoltage          = NAN
    DMMduration         = NAN


    helpOptions  = """
            Usage:  VoltageWiFiClient.py [Options]

            Start:  VoltageWiFiClient.py
            Stop:   CTRL-C

            Options:
                -h, --help          Show this help and exit
                -V, --Version       Show version status and exit
                -c, --cycle         Set the cycle time in sec (default 1 sec)
                -I, --TargetIP      Set the IP of the target computer
                -P, --TargetPort    Set the Port of the target computer (default 8000)
                -T, --Type          Set the Type of client to simulate 'GMC' (default) or 'GENERIC'

            Example: start VoltageWiFiClient.py with options:
                # set cycle time = 3 sec, and Target Address to '10.0.0.20:8000'
                # both commands do exactly the same
                VoltageWiFiClient.py --cycle 3 --TargetIP=10.0.0.20 --TargetPort=8000
            or: VoltageWiFiClient.py -c 3 -I 10.0.0.20 -P 8000 -T GMC
    """


g = Voltage_WiFiClientVars      # initiate global vars


def longstime():
    """Return current time as YYYY-MM-DD HH:MM:SS.mmm, (mmm = millisec)"""

    return dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3] # ms resolution


def dprint(*args):
    tag = ""
    for arg in args: tag += str(arg)

    if tag > "": tag = f"{longstime():23s} " + tag

    print(tag)


def rdprint(*args):
    args = (TRED,) + args + (TDEFAULT,)
    dprint(*args)


def exceptPrint(e, srcinfo):
    """Print exception details (errmessage, file, line no)"""

    exc_type, exc_obj, exc_tb = sys.exc_info()
    fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]    # which file?

    print(TYELLOW, end="")
    dprint("EXCEPTION: '{}' in file: '{}' in line {}".format(e, fname, exc_tb.tb_lineno), TDEFAULT)
    if srcinfo > "": dprint(srcinfo)


def clearTerminal():
    """clear the terminal"""

    # dprint("os.name: ", os.name)                           # os.name:  posix (on Linux)
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


def isValidIP(ip):
    """determine validity of given IP address"""

    defname = "isValidIP: "

    try:
        ipaddress.ip_address(ip)
        return True
    except Exception as e:
        # exceptPrint(e, defname)
        return False


def main():
    """Prepare the config as needed"""

    defname = "main: "

    # clear screen
    clearTerminal()

    # header
    print(BGREEN + "*" * 150 + TDEFAULT)

    # get and set the default IPs
    # expected to run on the same computer as GeigerLog
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


def DMMsetup():
    """Setup the DMM for Notify"""

    defname = "DMMsetup: "
    dprint(defname)

    adapters = simplepyble.Adapter.get_adapters()
    adapter  = adapters[0] # I have only 1
    dprint(defname, f"Selected adapter: {adapter.identifier()} [{adapter.address()}]")

    adapter.set_callback_on_scan_start(lambda: dprint(defname, "Scan started."))
    adapter.set_callback_on_scan_stop (lambda: dprint(defname, "Scan complete."))
    adapter.set_callback_on_scan_found(lambda peripheral: dprint(defname, f"Found {peripheral.identifier()} [{peripheral.address()}]"))

    adapter.scan_for(1000)                      # Scan for N milliseconds (Default=10 sec)
    peripherals = adapter.scan_get_results()

    BDMfound = False
    for g.peripheral in peripherals:
        if g.peripheral.identifier() == "BDM":
            BDMfound = True
            break

    if not BDMfound:
        dprint(defname, "Peripheral BDM not found - giving up")
        return False

    dprint(f"Connecting to: {g.peripheral.identifier()} [{g.peripheral.address()}]")
    g.peripheral.connect()

    services = g.peripheral.services()
    service_characteristic_pair = []
    for service in services:
        for characteristic in service.characteristics():
            service_characteristic_pair.append((service.uuid(), characteristic.uuid()))

    g.lasttime = time.time()
    try:
        choice = 7
        service_uuid, characteristic_uuid = service_characteristic_pair[choice]
        g.peripheral.notify(service_uuid, characteristic_uuid, lambda data: handleData(data))
    except Exception as e:
        exceptPrint(e, defname)

    return True


def handleData(data):

    defname = "handleData: "
    pstuff  = ""

    nowtime         = time.time()
    g.DMMduration   = 1000 * (nowtime - g.lasttime)     # duration in ms between 2 notifications
    g.lasttime      = nowtime
    pstuff         += f"{defname}Dur:{g.DMMduration:3.0f} ms  OW18E:'{data.hex(' ')}'"

    # Owon meter logic (from: https://github.com/sercona/Owon-Multimeters/blob/main/owon_multi_cli.c)
    # convert bytes to 'reading' array
    reading =  [0, 0, 0]
    reading[0] = data[1] << 8 | data[0]
    reading[1] = data[3] << 8 | data[2]
    reading[2] = data[5] << 8 | data[4]

    # Extract data items from first field
    function = (reading[0] >> 6) & 0x0f
    scale    = (reading[0] >> 3) & 0x07
    decimal  = reading[0]        & 0x07

    # Extract and convert measurement value (sign)
    if (reading[2] < 0x7fff):     measurement = reading[2]
    else:                         measurement = -1 * (reading[2] & 0x7fff)
    pstuff += f"  meas: {measurement}  fon: {function}  scl: {scale}  dec: {decimal}"

    g.DMMvoltage = measurement / 10**decimal
    pstuff += f"  Volt: {g.DMMvoltage:0.3f}"

    dprint(pstuff)

    uploadData()


def uploadData():
    """upload the data to GeigerLog via GET call"""

    defname = "uploadData: "

    now = time.time()
    if now - g.lastupload < g.WiFiCycleTime: return

    g.lastupload = g.lastupload + g.WiFiCycleTime

    # make the data url
    numbers     = [g.NAN] * 12                  # reset numbers
    numbers[10] = round(g.DMMduration, 3)       # --> Humid
    numbers[11] = round(g.DMMvoltage,  3)       # --> Xtra

    baseurl     = "http://{}:{}".format(g.WiFiTargetIP, g.WiFiTargetPort)
    dataurl     = "/GENERIC?M={}&S={}&M1={}&S1={}&M2={}&S2={}&M3={}&S3={}&T={}&P={}&H={}&X={}".format(*numbers)
    answer      = ""
    status      = -1
    try:
        tstart = time.time()
        with urllib.request.urlopen(baseurl + dataurl) as response:
            answer = response.read()
            status = response.status
        tdur   = 1000 * (time.time() - tstart)

        g.tDurAvg   = (g.tDurAvg * g.GETcalls + tdur ) / (g.GETcalls + 1)
        g.GETcalls += 1
        dprint(defname + "{:5d}  {:65s}  answer:{}{:30s}{}  status:{}  dur:{:0.1f} ms  durAvg:{:0.1f} ms".format(g.GETcalls, dataurl.replace("nan", "."), BRED, str(answer), TDEFAULT, status, tdur, g.tDurAvg))

    except Exception as e:
        emsg = "Target could NOT be reached with URL: {}".format(dataurl)
        exceptPrint(e, "")
        rdprint(defname, emsg)

        if g.WiFiTargetPort < 1024: msg = f"As TargetPort {g.WiFiTargetPort} is privileged you must be running VoltageWiFiClient with ADMINISTRATIVE RIGHTS!"
        else:                       msg = f"Is GeigerLog both RUNNING AND LOGGING?"
        rdprint(defname, msg)
        rdprint()


if __name__ == "__main__":
    try:
        main()

        if DMMsetup():
            while True:           # Loop
                time.sleep(1)     # stop with CTRL C

    except KeyboardInterrupt:
        dprint()
        dprint("Exit by CTRL-C")
        print("Disconnecting BDM: ", end=" ", flush=True)
        try:
            g.peripheral.disconnect()
        except Exception as e:
            exceptPrint(e, "KeyboardInterrupt")

        print("Done")


