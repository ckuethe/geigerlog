#! /usr/bin/env python3
# -*- coding: UTF-8 -*-

"""
GLsermon.py - Serial Monitor to read from and write to a USB-to-Serial Connection

    Start with: 'GLsermon.py -h' for Help Info
    Start with: 'GLsermon.py -P <Port> -B <Baudrate>' to set Port and Baudrate
    Stop  with: CTRL-C

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
__copyright__       = "Copyright 2016, 2017, 2018, 2019, 2020, 2021"
__credits__         = [""]
__license__         = "GPL3"
__version__         = "1.0"

import sys, os, time                 # std tools
import serial                        # handling the serial port
import serial.tools.list_ports       # allows listing of serial ports
import threading                     # thread to read the keyboard
import getopt                        # parse command line for options and commands


helpOptions = """
Usage:  GLsermon.py [Options] [Commands]

All serial communication will be logged to file 'GLsermon.log'. You'll find it
in the directory where GLsermon was started from.

Options:
    -h, --help          Show this help and exit.
    -d, --debug         Run with printing debug info.
                           Default: no debug
    -V, --Version       Show version and exit.
    -P, --Port          Define USB-to-Serial port:
                           on Linux   = /dev/ttyUSBx, x = 0, 1, 2, ...
                           on Windows = COMx, x = 0, 1, 2, ...
                           Default: /dev/ttyUSB0
    -B, --Baudrate      Define Baudrate:
                           57600, 115200, ...
                           Default: 115200
    -L, --List          Show available USB-to-Serial ports
                           Ports existing only as Symlinks are also shown
    -T, --Term          Termination characters when sending:
                           'CR' for Carriage Return,
                           'LF' for Linefeed,
                           or for both 'CRLF' or 'LFCR'.
                           Default: No termination characters.

Commands:
    gmc                 To use GLsermon with GMC Geiger counters.

                          -----------------------
                                MINI MANUAL
Using GMC counters:
To use GLsermon.py with GMC counters start with:

            GLsermon.py -P <Port> -B <Baudrate> gmc

Note the 'gmc' at the end! This will generate some extra GLsermon output, which
makes it possible to not only read any ASCII text returned by the counters, but
also binary data! Note further that you MUST NOT specify any Termination
Character!

To send a command - e.g. '<GETVER>>' - to the counter enter <GETVER>> (without
quotes) and hit the enter key. GMC counter response is similar to:
    R-Bytes:  15: GMC-500+Re 2.24
    R-Values HEX: 0x47 0x4D 0x43 0x2D 0x35 0x30 0x30 0x2B 0x52 0x65 0x20 0x32 0x2E 0x32 0x34
    R-Values DEC:   71   77   67   45   53   48   48   43   82  101   32   50   46   50   52
    R-Values ASC:    G    M    C    -    5    0    0    +    R    e         2    .    2    4

And for command <GETCPM>> :
    R-Bytes:   4: 3
    R-Values HEX: 0x00 0x00 0x02 0x33
    R-Values DEC:    0    0    2   51       --> results in: CPM = 2 * 256 + 51 = 563
    R-Values ASC:                3


Runtime guidance:
Clear:      Some devices, in particular GMC counter, may become non-responsive
            under certain conditions. Try to overcome by entering 'clear'.

Reconnect:  If 'clear' does not help, try 'reconnect'.

Repeat once if no success.

Last resort is restarting the counter.
"""

ser         = None                   # the pointer to the serial connection
debug       = False                  # print output for debugging
Port        = "/dev/ttyUSB0"         # Port
Baud        = 115200                 # Baudrate
gmc         = False                  # flag to signal use of GMC counter
filename    = "GLsermon.log"         # file for saving all communication
Term        = ""                     # CR or LF or CR+LF (do NOT use for GMC counters!)



def printPortList(symlinks=True):
    """print serial port details. Include symlinks or not"""

    # Pyserial:
    # 'include_links (bool)' – include symlinks under /dev when they point to a serial port
    # lp = serial.tools.list_ports.comports(include_links=False) # default; no symlinks shown
    # lp = serial.tools.list_ports.comports(include_links=True)  # also shows symlinks like e.g. /dev/geiger

    fncname = "    "
    print("Listing all Ports:")

    try:
        if symlinks:    lp = serial.tools.list_ports.comports(include_links=True)  # symlinks shown
        else:           lp = serial.tools.list_ports.comports(include_links=False) # default; no symlinks shown
        lp.sort()
    except Exception as e:
        print(fncname + "Exception: ", e)
        print(fncname + "lp: ", lp)
        lp = []

    for p in lp:    print(fncname, p)


class KeyboardThread(threading.Thread):
    """keyboard-input-thread"""

    def __init__(self, input_cbk = None, name='keyboard-input-thread'):
        self._is_running = True
        self.input_cbk = input_cbk
        super(KeyboardThread, self).__init__(name=name)
        self.start()

    def run(self):
        while self._is_running:
            self.input_cbk(input()) #waits to get input + Return
        sys.exit()

    def stop(self):
        self._is_running = False


def input_callback(inp):
    """evaluate the keyboard input"""

    global ser

    if debug: print('You Entered:', inp)

    if inp.upper == "CLEAR":                  # Clear (read all bytes from pipeline)
        while ser.in_waiting:
            try:
                x = ser.read(1)
            except Exception as e:
                print("input_callback: Exception: ", e)

    elif inp.upper() == "RECONNECT":          # Reconnect (done in main loop)
        ser.close()
        ser = None

    else:                                     # write data to device and file
        ser.write(bytes(inp + Term, 'utf-8'))
        with open(filename, "a") as f:
            f.write("Command : {}\n".format(inp))


def serConnect():
    """
    connect to the serial device
    return: "OK" on success
            ""   otherwise
    """

    global ser

    try:
        ser  = serial.Serial(Port, Baud, timeout = 0.5, write_timeout=0.5)
        while ser.in_waiting:   # clean pipeline
            try:                    x = ser.read(1)
            except Exception as e:  print("serConnect: Exception: ", e)
        return "OK"

    except:
        return ""


def main():
    """on errors return with message to print out"""

    global Port, Baud, Term, debug, gmc, ser

    print("+" * 100)

    # parse command line options (sys.argv[0] is progname)
    try:
        opts, args = getopt.getopt(sys.argv[1:], "hdVLP:B:T:", ["help", "debug", "Version", "List", "Port=", "Baudrate=", "Term="])
    except getopt.GetoptError as errmessage :
        # errmessage like "option -a not recognized"; results in exit
        return "ERROR: '{}', use './geigerlog -h' for help".format(errmessage)

    # processing the options
    for opt, optval in opts:
        if opt in ("-h", "--help"):
            return helpOptions

        elif opt in ("-V", "--Version"):
            return "Version: " + __version__

        elif opt in ("-d", "--debug"):
            debug    = True

        elif opt in ("-L", "--List"):       # which ports are available?
            #printPortList(symlinks=False)  # not including Sylinks
            printPortList(symlinks=True)    # including Sylinks
            return ""

        elif opt in ("-P", "--Port"):       # Port
            Port = optval

        elif opt in ("-B", "--Baudrate"):   # Baudrate
            Baud = optval

        elif opt in ("-T", "--Term"):       # Termination character for sending
            Term = ""
            if "CR" in optval.upper():      Term += "\r"
            if "LF" in optval.upper():      Term += "\n"

    # processing the args
    for arg in args:
        if arg == "gmc":
            gmc = True


    print("Start with: 'GLsermon.py -h' for Help Info")
    print("Start with: 'GLsermon.py -P <Port> -B <Baudrate>' to set Port and Baudrate")
    print("Stop  with: CTRL-C")
    print()


    # Show command line
    if debug: print("{:20s}: sys.argv: {}".format("Command line", sys.argv))
    if debug: print("{:20s}: options: {}, commands: {}".format("   recognized", opts, args))

    print("Connecting with Port:", Port, ", Baudrate:", Baud)

    if serConnect() == "OK":  print("Connection successful")
    else:                     return "Connection NOT successful, exiting"
    if debug: print("Connection: ", ser)

    with open(filename, "w") as f:  # to empty the file
        pass

    #start the Keyboard thread
    kthread = KeyboardThread(input_callback)

    print()
    try:
        while True:
            val = b""
            while ser == None:
                print("No Serial-Connection --- reconnecting")
                if serConnect() == "OK": break
                time.sleep(1)

            while not os.access(Port , os.R_OK):
                print("Port: ", Port, " can NOT be read --- reconnecting")
                ser.close()
                time.sleep(1)
                if serConnect() == "OK": break

            if ser != None:
                while ser.in_waiting:
                    #~print(".", end="")
                    val += ser.read(1)
                    time.sleep(0.001)

            if(val > b""):
                if gmc: # adressing some GMC counter issues
                    print()

                    msg = "R-Bytes: {:3d}: ".format(len(val))
                    try:
                        msg += val.decode()
                    except:
                        msg += "(Non-decodeable) "
                        msg += str(val)

                    msg += "\nR-Values HEX: "
                    for a in val:   msg += "0x{:02X} ".format(a)
                    msg += "\nR-Values DEC: "
                    for a in val:   msg += "{:4d} ".format(a)
                    msg += "\nR-Values ASC: "
                    for a in val:   msg += "{:>4s} ".format(chr(a))
                    msg += "\n"

                    print(msg, end="")

                    with open(filename, "a") as f:
                        f.write(msg + "\n")
                    print()
                    #~input_callback("<GETDATETIME>>")  # auto repeat calls
                    #~time.sleep(1)

                else: # generic serial terminal
                    try:    msg  = val.decode()
                    except: msg  = "(Non-decodeable) " + str(val)
                    print(msg, end="")

                    with open(filename, "a") as f:
                        f.write(msg)

            time.sleep(0.01) # to reduce CPU load

    except Exception as e:
        return "Exception: " + str(e)

    except KeyboardInterrupt:
        kthread.stop()
        #~print("kthread._is_running:", kthread._is_running)
        return "KeyboardInterrupt"


if __name__ == "__main__":
    print(main())
    print("\n")
    os._exit(123) # sys.exit() not helping
