#! /usr/bin/env python3
# -*- coding: UTF-8 -*-

"""
GLsermon.py - Serial Monitor to read from and write to a USB-to-Serial Connection
              with Extra-Support for GMC counter

    Start with: 'GLsermon.py -h'                          to get Help Info")
    Start with: 'GLsermon.py -P <Port> -B <Baudrate>'     to set Port and Baudrate")
    Start with: 'GLsermon.py -P <Port> -B <Baudrate> gmc' to set Port and Baudrate for any GMC counter")
    Stop  with: CTRL-C")
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
__version__         = "1.3"

import sys, os, io, time, datetime      # basic modules
import serial                           # handling the serial port
import serial.tools.list_ports          # allows listing of serial ports
import threading                        # thread to read the keyboard
import getopt                           # parse command line for options and commands
import traceback                        # for traceback on error; used in: exceptPrint


# global vars
ser         = None                      # the pointer to the serial connection
debug       = False                     # print output for debugging
traceback   = False                     # detailed exception output
Port        = "/dev/ttyUSB0"            # Port
Baud        = 115200                    # Baudrate
gmc         = False                     # flag to signal use of GMC counter
waiting     = False                     # to select between reading data and just printint queue size
filename    = "GLsermon.log"            # file for saving all communication
Term        = ""                        # CR or LF or both (will be reset to "" for GMC counters!)


helpOptions = \
"""
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
    -L, --List          Print full details of available USB-to-Serial ports.
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

Runtime guidance:
    Some devices, in particular GMC counters, may become non-responsive under
    certain conditions; commands 'clear' and 'reconnect' may be of help..

    clear:      Clears the serial connection pipeline (GMC only)
    reconnect:  If 'clear' does not help, try 'reconnect'. Repeat if no success.
                    Last resort is restarting the device.
    cmds:       Prints a list of all GMC commands
    help:       Prints out this help information during a run
    list:       Prints full details of available USB-to-Serial ports.
                    Ports existing only as Symlinks are also shown


Using GMC counters:
    To use GLsermon.py with GMC counters start with: (Note the 'gmc' at the end!)

            GLsermon.py -P <Port> -B <Baudrate> gmc

    This will activate some helpful extra GLsermon code when using GMC counters.

    *   No Termination characters are allowed and will automatically be suppressed.
    *   Enter commands in small caps and leave out all enclosing brackets.
        GLsermon will format them so that a command given as 'getver' will be send
        to the counter as '<GETVER>>' when you press the Enter key.
    *   Since GMC counters not only return ASCII text, but also binary data, the
        output becomes hard to read. GLsermon shows human-readable text (when
        possible), HEX values, Decimal values.

    Examples:
    The GMC counter response to 'getver'+ ENTER is similar to:
        Receive-Bytes:  15: GMC-500+Re 2.24
        Receive-Values HEX: 0x47 0x4D 0x43 0x2D 0x35 0x30 0x30 0x2B 0x52 0x65 0x20 0x32 0x2E 0x32 0x34
        Receive-Values DEC:   71   77   67   45   53   48   48   43   82  101   32   50   46   50   52
        Receive-Values ASC:    G    M    C    -    5    0    0    +    R    e         2    .    2    4

    command 'getcpm' + ENTER becomes <GETCPM>> and results in a response like:
        Receive-Bytes:   4: 3
        Receive-Values HEX: 0x00 0x00 0x02 0x33
        Receive-Values DEC:    0    0    2   51       --> results in: CPM = 2 * 256 + 51 = 563
        Receive-Values ASC:                  3

    command 'spir,0,0,0,16,0' becomes binary coded <SPIRXYZAB>> with X, Y, Z, A, B being bytes with a
        value from 0 ... 255. It will read the first 4k bytes of memory beginning at address 0x000.
        It results in a response like:
        Receive-Bytes: 4096: (Non-decodeable)
        Receive-Values HEX:
        01  01  00  00  02  01  00  01  02  00  00  02  00  00  01  01  01  00  00  00  00  00  00  55  AA  00  00  00  00  00  00  00
        55  AA  01  01  02  00  00  00  01  02  00  00  01  00  01  01  00  00  01  01  00  03  00  03  01  01  01  00  01  00  01  01
        00  01  00  01  03  00  00  01  00  00  01  00  00  00  00  00  00  00  01  00  01  02  00  01  01  00  01  01  03  00  00  00
        ... plus 61 more lines, folowed by DEC and ASCII lines

"""

gmc_commands = \
"""
GMC Counter Command List:
see: GQ-RFC1801 GMC Communication Protocol,
https://www.gqelectronicsllc.com/comersus/store/download.asp

Parameter Count: 0
    getcpm          # get CPM
    getcpmh         # get CPM from Low  Sensitivity tube; that should be the 2nd tube in the 500+
    getcpml         # get CPM from High Sensitivity tube; that should be the 1st tube in the 500+
    getcps          # get CPS
    getcpsh         # get CPS from Low  Sensitivity tube; that should be the 2nd tube in the 500+
    getcpsl         # get CPS from High Sensitivity tube; that should be the 1st tube in the 500+

    getdatetime     # get counter's DateTime
    getgyro         # get motion sensor
    getserial       # get serial number of counter
    gettemp         # get temperature (not supported anymore)
    getver          # get version of firmware
    getvolt         # get battery voltage
    heartbeat0      # heartbeat Off  (nothing returned)
    heartbeat1      # heartbeat On   (starts returning of byte values in 1 sec intervals)
    poweron         # switch power On
    poweroff        # switch power Off

    getcfg          # get the cpnfiguration
    ecfg            # erase the configuration
    cfgupdate       # update the configuration
    reboot          # reboot the counter
    factoryreset    # do a factory reset

Parameter Count: 1
    No commands

Parameter Count: 2  for counter 3XX series (2 Bytes)
    wcfg,A0,Ch                  A0 - address
                                Ch - Byte to write

Parameter Count: 3  for counter 5XX, 6XX series (3 bytes)
    wcfg,Hi,Lo,Ch               Hi - High byte, Lo - Low byte of address
                                Ch - Byte to write

Parameter Count: 5
    spir,A2,A1,A0,L1,L0         A2,A1,A0 are three bytes address data, from MSB to LSB
                                L1,L0 are the data length requested, from MSB to LSB
                                The length normally not exceed 4096 bytes in each request.
                                for the first 2048 bytes use:    spir{0,0,0,8,0}
Parameter Count: 6
    setdatetime,Y,M,D,h,m,s     for: 2021-04-19 13:02:50 use:    setdatetime{21,4,19,13,2,50}

"""


def longstime():
    """Return current time as YYYY-MM-DD HH:MM:SS.mmm, (mmm=millisec)"""

    return dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3] # trim down to ms resolution


def exceptPrint(e, srcinfo):
    """Print exception details (errmessage, file, line no)"""

    exc_type, exc_obj, exc_tb = sys.exc_info()
    fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]    # which file?

    print("EXCEPTION: '{}' in file: '{}' in line {}".format(e, fname, exc_tb.tb_lineno))
    if srcinfo > "": print("{}".format(srcinfo))
    if traceback:  print("EXCEPTION: Traceback:\n", traceback.format_exc()) # more extensive info


def getPortList(symlinks=True, full=False):
    """print serial port details. Include symlinks or not"""

    # Pyserial:
    # 'include_links (bool)' – include symlinks under /dev when they point to a serial port
    # lp = serial.tools.list_ports.comports(include_links=False) # default; no symlinks shown
    # lp = serial.tools.list_ports.comports(include_links=True)  # also shows symlinks like e.g. /dev/geiger

    defname   = "getPortList: "
    PortList  = ""
    PortList += "All Ports Listing{}:".format(" (with Symlinks)" if symlinks else "") + " - Type 'List' for full details\n"

    lp = []
    try:
        lp = serial.tools.list_ports.comports(include_links=symlinks)
    except Exception as e:
        msg = defname + "lp: {}".format(lp)
        exceptPrint(e, msg)
    lp.sort()                 # sorted by device /dev/ttyUSB0, /dev/ttyUSB1, ...

    if len(lp) == 0:
        PortList += "   None\n"
    else:
        # example output:
        #   Ports detected:
        #       /dev/ttyACM0 - USB-ISS.
        #       /dev/ttyUSB0 - USB2.0-Serial
        for p in lp:    PortList += "   " + str(p) + "\n"

    if full and len(lp) > 0:
            PortList += ""
            PortList += "All Ports detailed:"

            # complete list of attributes for serial.tools.list_ports.comports()
            lpAttribs = ["device", "name", "hwid", "description", "serial_number", "location", "manufacturer", "product", "interface", "vid", "pid"]
            try:
                for p in lp:
                    PortList += str(p)
                    for pA in lpAttribs:
                        if pA == "vid" or pA == "pid":
                            x = getattr(p, pA, 0)
                            if x is None:   PortList += "   {:16s} : None\n".format("p." + pA)
                            else:           PortList += "   {:16s} : {:5d} (0x{:04X})\n".format("p." + pA, x, x)
                        else:
                            PortList += "   {:16s} : {}\n".format("p." + pA, getattr(p, pA, "None"))
                    PortList += "\n"
            except Exception as e:
                msg = defname + "lp: {}".format(lp)
                exceptPrint(e, msg)
            PortList += "\n"

    return PortList


class KeyboardThread(threading.Thread):
    """keyboard-input-thread"""
    # initiate with: kthread = KeyboardThread(input_callback)

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
    # use in: kthread = KeyboardThread(input_callback)

    global ser

    if debug: print("You Entered: '{}'".format(inp))
    inpUP = inp.upper()
    # if debug: print("Uppered    : '{}'".format(inpUP))
    # if debug: print("len(inp): {} len(inpUP): {} ".format(len(inp), len(inpUP)))

    if   "CLEAR" in inpUP:                      # Clear (read all bytes from pipeline)
        clearPipeline()

    elif "RECONNECT" in inpUP:                  # Reconnect (done in main loop)
        clearPipeline()
        print("About to reconnect")
        ser = None

    elif "HELP" in inpUP:                       # print Help info
        print(helpOptions)

    elif "LIST" in inpUP:                       # print detailed port info
        print(getPortList(symlinks=True, full=True))

    elif "CMDS" in inpUP:                       # print GMC commands set
        if not gmc: print("COMMANDS VALID ONLY FOR GMC")
        print(gmc_commands)

    else:                                       # write data to device and file
        if gmc:
            bw     = inpUP.strip().replace(" ", "")
            binval = ""
            if "," in bw:
                if debug: print("',' is at pos: ", bw.find(","))
                cmd = bw[0 : bw.find(",")]
                par = bw[bw.find(",") + 1 : ] # cut out segment to the right of first ','
                if debug: print("bw:'{}',  cmd:'{}', par:'{}'".format(bw, cmd, par))

                par = par.split(",")                      # split to list
                for b in par: binval += chr(int(b))       # combine to string
            else:
                cmd = bw

            sendb = "<" + cmd + binval + ">>"
            if debug: print("cmd:   {}   binval: '{}'".format(cmd, binval))
            print(">>>>> NOTE: Byte values printed to a Terminal may look incomplete! Compare Length with expected length! <<<<<")

        else:
            sendb = inp + Term                         # other devices than GMC may need low cap!

        print("Sending: '{}'  (Length:{})".format(sendb.replace("\n", "LF").replace("\r", "CR"), len(sendb)))
        ser.write(bytes(sendb, 'utf-8'))
        with open(filename, "a") as f:
            f.write("Sending : {}\n".format(sendb))


def clearPipeline():
    """read all bytes from serial until no more bytes"""

    defname = "clearPipeline: "

    br     = b""                # bytes_record
    bw     = 0                  # bytes_waiting
    sumbw  = 0                  # sum of all bw

    try:
        time.sleep(0.1)         # allow some last bytes to get into queue
        i = -1
        while True:
            i     += 1
            bw     = ser.in_waiting
            sumbw += bw
            if bw == 0: break
            br = ser.read(bw)
            if debug: print("i: {}  bytes waiting: {:<6d}  total bytes to clear: {:<6d}  len(bytes read): {:<6d}".format(i, bw, sumbw, len(br)))
            time.sleep(0.001)             # allow some last bytes to get into queue

    except Exception as e:
        msg = defname + "Exception on reading from Serial"
        exceptPrint(e, msg)

    print("Cleared Pipeline from {} bytes".format(sumbw))


def serConnect():
    """
    connect to the serial device
    return: True  : on success
            False : otherwise
    """

    global ser

    defname   = "serConnect: "
    ConnectOk = False

    try:
        if not os.path.exists(Port):
            # den shit gibbes nich  -   kann passieren, wenn nach Start der USB Stecker gezogen wird!
            emsg = "FAILURE: Serial port '{}' does not exist. ".format(Port)
            print(defname, emsg)

        ser  = serial.Serial(Port, Baud, timeout=0.5, write_timeout=0.5)
        # buffer questions
        # Linux see:   https://github.com/pyserial/pyserial/issues/691
        # Windows see: https://stackoverflow.com/questions/12302155/how-to-expand-input-buffer-size-of-pyserial
        # set buffer only on Windows: ser.set_buffer_size(rx_size = 12800, tx_size = 12800)
        # buffer size in Linux: on CH340C:  4095 (= max no of bytes waiting?)
        #                                   7097 (in_waiting still showed only 4095?!)
        #                                   50000 ! how is this possible?
        ConnectOk = True

    except Exception as e:
        exceptPrint(e, defname)

    return ConnectOk


def main():
    """on errors return with message to print out"""

    global ser, Port, Baud, Term, debug, gmc, waiting

    defname  = "main: "
    logInfo  = "\n"

    logInfo += "+" * 100 + "\n"
    logInfo += "{:13s}:  {}\n".format("GLsermon.py",  "Version: {}".format(__version__))
    logInfo += "{:13s}:  sys.argv: {}\n".format("Command line", sys.argv)
    print(logInfo, end="")

    # Clear Logfile and save
    with open(filename, "wt") as f:  # to empty the file
        f.write(logInfo)
    print("{:13s}:  {}".format("Logfile", "created as '{}'".format(filename)))

    # parse command line options (sys.argv[0] is progname)
    try:
        opts, args = getopt.getopt(sys.argv[1:], "hdVP:B:T:", ["help", "debug", "Version", "Port=", "Baudrate=", "Term="])
    except getopt.GetoptError as errmessage :
        # errmessage like "option -a not recognized"; results in exit
        return "ERROR: '{}', use './geigerlog -h' for help".format(errmessage)

    # processing the options
    for opt, optval in opts:
        # if opt in ("-h", "--help"):
        #     return helpOptions

        if opt in ("-V", "--Version"):
            return "Version: " + __version__

        elif opt in ("-d", "--debug"):
            debug = True

        elif opt in ("-P", "--Port"):                               # Port
            Port = optval

        elif opt in ("-B", "--Baudrate"):                           # Baudrate
            Baud = optval

        elif opt in ("-T", "--Term"):                               # Termination character for sending
            Term = ""                                               # use Term = ""; none used for GMC counter
            if "CR" in optval.upper(): Term += "\r"
            if "LF" in optval.upper(): Term += "\n"

    # processing the args
    for arg in args:
        if arg.upper() == "GMC":
            gmc  = True
            Term = ""

        if arg.upper() == "WAITING":
            waiting = True
            # Term = ""                                               # no Termination character when sending to GMC!

    logInfo = "\n"

    # Show recognized command line options, cmds
    if debug: logInfo += "{:13s}:  options: {}, commands: {}\n\n".format("Settings", opts, args)

    logInfo += "Mini Help:\n"
    logInfo += "   Type 'Help' for more Help\n"
    logInfo += "\n"
    logInfo += "   Start with: 'GLsermon.py -P <Port> -B <Baudrate>'     to set Port and Baudrate\n"
    logInfo += "   Start with: 'GLsermon.py -P <Port> -B <Baudrate> gmc' to set Port and Baudrate for any GMC counter\n"
    logInfo += "   Stop  with: CTRL-C\n"
    logInfo += "\n"

    logInfo += getPortList(symlinks=True)    # including Symlinks
    logInfo += "\n"

    logInfo += "{:13s}:  Serial Connection: Port: '{}', Baudrate: {}\n".format("Configured", Port, Baud)

    # append to log file
    with open(filename, "a") as f:
        f.write(logInfo)

    print(logInfo, end="")

    #start the Keyboard thread
    kthread = KeyboardThread(input_callback)
    if debug: print("{:13s}:  {}".format("Keyboard",  "Thread started"))
    print()

    try:
        while True:
            val = b""
            while ser is None:
                print("Making Serial-Connection: ", end=" ")
                if serConnect():
                    print("successful\n")
                    break
                else:
                    print("NOT successful - waiting 1 sec befor retry\n")
                    time.sleep(1)

            while not os.access(Port , os.R_OK):
                print("Port: {} can NOT be read --> closing Serial-Connection".format(Port))
                ser.close()
                ser = None
                time.sleep(1)
                break

            if ser is not None:
                # print("ser is not None")
                try:
                    last_waiting = ser.in_waiting

                    if waiting:
                        deltatime = 1              # sec
                        delta     = 0
                        startt = time.time()
                        while True:
                            # get length of waiting queue and print
                            newt = time.time()
                            if newt - startt >= deltatime:
                                startt += deltatime
                                cum_waiting = 0

                                cc=time.time()
                                this_waiting = ser.in_waiting
                                cum_waiting += this_waiting
                                delta        = this_waiting - last_waiting
                                last_waiting = this_waiting

                                if cum_waiting == 4095: ser.read(4095)

                                cumdur = 1000 * (time.time() - cc)

                                msg = "{}  cum_dur: {:0.3f} ms   cum_waiting: {:<5d} Changed by: {:<+5d}  {}".format(longstime(), cumdur, cum_waiting, delta, "#" * int((delta / 1)))
                                print(msg)
                                with open(filename, "a") as f:          # append one line
                                    f.write(msg + "\n")

                            time.sleep(0.001)                           # keep ms precision

                    else:
                        while True:
                            # read bytes waiting; read as single byte

                            sbyte = ser.read(1)
                            if sbyte == b"": break                      # break while-loop when nothing to read left
                            # print("sbyte: ", sbyte)

                            # GMC counter
                            if gmc:
                                val += sbyte                            # assemble byte-sequence

                            # Generic Serial Terminal
                            else:
                                val  = sbyte                            # use each byte individually
                                nval = ord(val)                         # convert to int value
                                # print(nval,  end=" ", flush=True)       # print out w/o LF
                                try:
                                    print(val.decode("utf-8") ,  end="", flush=True)       # print out w/o LF
                                except Exception as e:
                                    print(str(val), "(" + str(nval) + ")", end="")
                                with open(filename, "a") as f:          # write as one byte value plus 1 space
                                    f.write(str(nval) + " ")

                    # print("while break")

                except OSError as e:
                    exceptPrint(e, "OSError")
                    print(defname + "OSError: ERRNO:{} ERRtext:'{}'".format(e.errno, e.strerror))
                    if e.errno == 5:
                        msg = defname + "Serial connectiomn was lost"
                        print(msg)

                except Exception as e:
                    msg = defname + "Failure in getting data"
                    exceptPrint(e, msg)


                # print("val: ", val)
                if gmc and (val > b""):                             # detailing communication with GMC counter
                        print()

                        flag = ""
                        msg  = longstime()
                        msg += " :\nReceive-Bytes: {:3d}: {}  ".format(len(val), val)
                        try:
                            msg += "Decoded: " + val.decode()
                        except:
                            msg += "Non-decodeable"
                            flag = "\n"

                        msg += "\nReceive-Values HEX: " + flag
                        for i, a in enumerate(val):
                            msg += " {:02X} ".format(a)
                            if i % 32 == 31: msg += flag
                        msg += flag

                        msg += "\nReceive-Values DEC: " + flag
                        for i, a in enumerate(val):
                            msg += "{:3d} ".format(a)
                            if i % 32 == 31: msg += flag
                        msg += flag

                        msg += "\nReceive-Values ASC: " + flag
                        for i, a in enumerate(val):
                            if a > 0:   msg += "{:>3s} ".format(chr(a)) # an a == 0x00 results in 3 instead of 4 spaces???
                            else:       msg += "    "                   # a == 0x00
                            if i % 32 == 31: msg += flag
                        msg += flag

                        msg += "\n"

                        print(msg, end="")

                        with open(filename, "a") as f:
                            f.write(msg + "\n")
                        print()

            time.sleep(0.01) # to reduce CPU load

    except Exception as e:
        msg = "Main loop"
        exceptPrint(e, msg)
        return "Exception: " + str(e)

    except KeyboardInterrupt:
        kthread.stop()
        # print("kthread._is_running ?:", kthread._is_running)
        return "KeyboardInterrupt"


if __name__ == "__main__":
    print("\n", main())
    print("\n")
    os._exit(123) # sys.exit() not helping wg threading, requires to press Return key

