#!/usr/bin/python3
# -*- coding: UTF-8 -*-

"""
gutils.py - GeigerLog utilities

include in programs with:
    from utils include *
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
__copyright__       = "Copyright 2016, 2017, 2018"
__credits__         = [""]
__license__         = "GPL3"


import sys
import os
import io
import inspect
import time                         # time formatting and more
import datetime                     # date and time conversions
import matplotlib.dates as mpld     # used for datetime conversions
import configparser                 # parse configuration file geigerlog.cfg

from PyQt4 import QtGui             # for processEvents and beep

import gglobs                       # all global vars


# tricks
# For generic non full screen applications, you can turn off line wrapping by
# sending an appropriate escape sequence to the terminal:
#   tput rmam
# This mode can be cancelled with a similar escape:
#   tput smam
# also: https://tomayko.com/blog/2004/StupidShellTricks

#colors for the terminal
# https://gist.github.com/vratiu/9780109
TCYAN               = '\033[96m'            # cyan
tPURPLE             = '\033[95m'            # purple (dark)
tBLUE               = '\033[94m'            # blue (dark)
TGREEN              = '\033[92m'            # light green
TYELLOW             = '\033[93m'            # yellow
TRED                = '\033[91m'            # red
TDEFAULT            = '\033[0m'             # default, i.e greyish
BOLD                = '\033[1m'             # white (bright default)
UNDERLINE           = '\033[4m'             # underline
BOLDREDUL           = '\033[31;1;4m'        # bold, red, underline
BOLDRED             = '\033[31;1m'          # bold, red - but is same as TRED

NORMALCOLOR         = TDEFAULT              # normal printout
HILITECOLOR         = TGREEN                # hilite message
ERRORCOLOR          = TYELLOW               # error message


def getProgName():
    """Return program base name, i.e. 'geigerlog' even if it was named
    'geigerlog.py' """

    progname          = os.path.basename(sys.argv[0])
    progname_base     = os.path.splitext(progname)[0]

    return progname_base


def getProgPath():
    """Return full path of the program directory"""
    dp = os.path.dirname(os.path.realpath(__file__))
    return dp


def getDataPath():
    """Return full path of the data directory"""
    dp = os.path.join(getProgPath(), gglobs.dataDirectory)
    return dp


def getGresPath():
    """Return full path of the resource (icons, sounds) directory"""
    dp = os.path.join(getProgPath(), gglobs.gresDirectory)
    return dp


def getProglogPath():
    """Return full path of the geigerlog.proglog file"""
    dp = os.path.join(gglobs.dataPath, gglobs.progName + ".proglog")
    return dp


def getStdlogPath():
    """Return full path of the geigerlog.stdlog file"""
    dp = os.path.join(gglobs.dataPath, gglobs.progName + ".stdlog")
    return dp


def getConfigPath():
    """Return full path of the geigerlog.cfg file"""
    dp = os.path.join(gglobs.progPath, gglobs.progName + ".cfg")
    return dp


def stime():
    """Return current time as YYYY-MM-DD HH:MM:SS"""

    return longstime()[:-4]


def longstime():
    """Return current time as YYYY-MM-DD HH:MM:SS.mmm, (mmm=millisec)"""

    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3] # ms resolution


def datestr2num(string_date):
    """convert a Date&Time string in the form YYYY-MM-DD HH:MM:SS to a Unix
    timestamp in sec"""

    #print("datestr2num: string_date", string_date)
    try:
        dt=time.mktime(datetime.datetime.strptime(string_date, "%Y-%m-%d %H:%M:%S").timetuple())
    except:
        dprint(True, "ERROR in datestr2num: Date as String: '{}'".format(string_date))
        newstrdate = '2099-09-09 09:09:09'
        dprint(True, "                      replacing with: '{}'".format(newstrdate))
        dt=time.mktime(datetime.datetime.strptime(newstrdate, "%Y-%m-%d %H:%M:%S").timetuple())

    return dt


def MPLDdatestr2num(datetime):      # Date to Number
    """convert a Date&Time string in the form YYYY-MM-DD HH:MM:SS into a number
    being a timestamp in days"""
    # "2018-05-16 13:45:58" --> 736830.573587963

    dn = mpld.datestr2num(datetime)

    return dn


def MPLDnum2datestr(num):           # Number to Date
    """convert a number, i.e. a timestamp in days, into a Date&Time string
    in the form YYYY-MM-DD HH:MM:SS"""
    # 736830.573587963 --> '2018-05-16 13:45:58+00:00'
    # 736830.573587963 --> '2018-05-16 13:45:58'      # first 19 bytes

    nd = str(mpld.num2date(num))[:19]

    return nd


def BytesAsASCII(bytestring):
    """convert a bytes string into a string which has ASCII characters when
    printable and '.' else, with spaces every 10 bytes"""

    asc = ""
    if bytestring != None:
        for i in range(0, len(bytestring)):
            a = bytestring[i]
            if a < 128 and a > 31:
                asc += chr(bytestring[i])
            else:
                asc += "."

            if ((i + 1) % 10) == 0:
                asc += "  "

    return asc


def BytesAsHex(bytestring):
    """ convert a bytes string into a str of Hex values, with dash spaces
    every 10 bytes"""

    bah = ""
    for i in range(0, len(bytestring)):
        bah += "{:02X}  ".format(bytestring[i])
        if ((i + 1) % 10) == 0 :
            bah += "- "

    return bah


def BytesAsDec(bytestring):
    """convert a bytes string into a str of Dec values, with dash spaces
    every 10 bytes"""

    bad = ""
    for i in range(0, len(bytestring)):
        bad += "{:<3d} ".format(bytestring[i]) # {: 3d} results in leading space
        if ((i + 1) % 10) == 0 :
            bad += "- "

    return bad


def lineno():
    """Return the current line number."""

    return inspect.currentframe().f_back.f_lineno


def orig(thisfile):
    """Return name of calling program and line number of call
    requires that this routine is called by orig(__file__)"""

    lineno = inspect.currentframe().f_back.f_lineno
    fn = os.path.basename(thisfile)

    #print "orig:", inspect.currentframe().__name__
    #print "orig:", inspect.getmembers()
    #print "orig:",sys._getframe(1).f_code.co_name

    return fn, sys._getframe(1).f_code.co_name, lineno


def header(txt):
    """position txt within '====' string"""

    #return "\n==== {} {}".format(txt, "=" * max(0, (60 - len(txt))))
    return "<br>==== {} {}".format(txt, "=" * max(0, (60 - len(txt))))


def fprint(*args, error=False, debug=False, errsound=True):
    """print all args in the GUI"""

    ps = "{:35s}".format(str(args[0]))     # 1st arg
    for s in range(1, len(args)):          # skip 1st arg
        ps += str(args[s])

    if error :
        if errsound:             playMedia(error=True)
        gglobs.notePad.append("<span style='color:red;'>" + ps + "</span><span style='color:;'></span>")
        if errsound:             time.sleep(0.3) # wait for the end of sound
    else:
        gglobs.notePad.append(ps)

    QtGui.QApplication.processEvents()

    dprint(debug, ps)


def commonPrint(ptype, *args):
    """Printing function to vprint and dprint"""

    tag = "{:23s} {:7s}: ".format(longstime(), ptype) + gglobs.debugindent
    for arg in args: tag += str(arg)
    writeFileA(gglobs.proglogPath, tag)

    if gglobs.redirect:     print(tag)
    else:                   print(tag[11:])


def arrprint(text, array):
    """ prints an array """

    print(text)
    for a in array:
        print("{:10s}: ".format(a), array[a])


def vprint(verbose, *args):
    """verbose print:
    if verbose is true then:
    - Write timestamp and args as a single line to progname.proglog file
    - Print args as single line
    else
    - do nothing
    """

    if verbose:   commonPrint("VERBOSE", *args)


def dprint(debug, *args):
    """debug print:
    if debug is true then:
    - Write timestamp and args as a single line to progname.proglog file
    - Print args as single line
    else
    - do nothing
    """

    if debug:    commonPrint("DEBUG", *args)


def exceptPrint(e, excinfo, srcinfo):
    """Print exception details (errmessage, file, line no)"""

    # use: excinfo = sys.exc_info()
    exc_type, exc_obj, exc_tb = excinfo
    fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
    dprint(True, srcinfo)
    dprint(True, "ERROR: '{}' in file: '{}' in line {}".format(e, fname, exc_tb.tb_lineno))


def debugIndent(arg):
    """increases or decreased the indent of debug/verbose print"""

    if arg > 0:        gglobs.debugindent += "   "
    else:              gglobs.debugindent = gglobs.debugindent[:-3]


def clearProgramLogFile():
    """To clear the debug file at the beginning of each run"""

    # "Mµßiggang ist auch ein ° von Läßterei"
    tag      = "{:23s} PROGRAM: pid:{:d} ########### {:s}  ".format(longstime(), os.getpid(), "GeigerLog {} -- mit no meh pfupf underm füdli !".format(gglobs.__version__))
    line     = tag + "#" * 30

    if gglobs.redirect:
        # text with buffering=0 not possible in Python 3
        sys.stdout = open(gglobs.stdlogPath, 'w', buffering=1) # deletes content
        sys.stdout = open(gglobs.stdlogPath, 'a', buffering=1)
        sys.stderr = open(gglobs.stdlogPath, 'a', buffering=1)

    print(TYELLOW + line + TDEFAULT)         # goes to terminal  (and *.stdlog)
    writeFileW(gglobs.proglogPath, line )    # goes to *.proglog (and *.stdlog)


def readBinaryFile(path):
    """Read all of the file into data; return data as string"""

    data = b''

    try:
        with open(path, 'rb') as f:
            data = f.read()
    except:
        srcinfo = "readBinaryFile: ERROR reading file"
        exceptPrint(e, sys.exc_info(), srcinfo)
        data = b"ERROR: Could not read file: " + str.encode(path)

    vprint(gglobs.verbose, "readBinaryFile: type:{}, len:{}, data=[:100]:".format(type(data), len(data)), data[0:100])

    return data


def writeBinaryFile(path, data):
    """Create file and write data to it as binary"""

    with open(path, 'wb') as f:
        f.write(data)


def readFileLines(path):
    """Read all of the file into lines, ending with linefeed.
    return data as list of lines"""

    enc = None

    # is that really needed???
    #enc = detectFileType(path)
    #print "encoding determined:", enc

    if enc == None: enc = "utf_8"
    #print "encoding selected=", enc

    try:
        with open(path, 'rt', encoding= enc, errors='replace') as f:
            data = f.readlines()                    # data is list of lines
        #vprint(gglobs.verbose,  "readFileLines: type(data):", type(data), ", data=[:5]:\n", data[:5])
    except Exception as e:
        srcinfo = "ERROR: readFileLines: Could not read file: {} with encoding: {}".format(path, enc)
        exceptPrint(e, sys.exc_info(), srcinfo)
        try:
            # Using encoding="latin-1" should NEVER give an exception:
            # http://python-notes.curiousefficiency.org/en/latest/python3/text_file_processing.html
            enc = "latin-1"
            dprint(True, "Retrying with encoding:", enc)
            with open(gglobs.currentFilePath, "rt", encoding=enc) as f:
                data = f.readlines()                # data is list of lines
            #vprint(gglobs.verbose,  "readFileLines: type(data):", type(data), ", data=[:5]:\n", data[:5])
        except Exception as e:
            srcinfo = "ERROR: readFileLines: Could not read file: {} with Fallback encoding: {}".format(path, enc)
            exceptPrint(e, sys.exc_info(), srcinfo)
            data = [srcinfo]

    return data



# BOM for UTF-8 ???
# For example, a file with the first three bytes 0xEF,0xBB,0xBF is probably a UTF-8 encoded file.
# However, it might be an ISO-8859-1 file which happens to start with the characters ï»¿.
# Or it might be a different file type entirely.

def writeFileW(path, writestring, linefeed = True):
    """Create file if not available, and write to it if writestring
    is not empty; add linefeed unless excluded"""

    with open(path, 'wt', encoding="UTF-8", errors='replace', buffering = 1) as f:
        if writestring > "":
            if linefeed: writestring += "\n"
            f.write(writestring)


def writeFileA(path, writestring):
    """Write-Append data; add linefeed"""

    with open(path, 'at', encoding="UTF-8", errors='replace', buffering = 1) as f:
        f.write((writestring + "\n"))


def strFontInfo(origin, fi):
    """formats font information, returns string"""

    fontinfo = "Family:{}, fixed:{}, size:{}, style:{}, styleHint:{}, styleName:{}, weight:{}"\
    .format(fi.family(), fi.fixedPitch(), fi.pointSize(), fi.style(), fi.styleHint(), fi.styleName(), fi.weight())

    return fontinfo


def printVarsStatus(debug, origin = ""):
    """Print the current value of selected variables"""

    # not up-to-date!
    myVars  = ['gglobs.debug','gglobs.verbose', 'gglobs.dataPath', 'gglobs.mav' , 'gglobs.logcycle']
    myVars += ['gglobs.Xleft', 'gglobs.Xright', 'gglobs.Xunit', 'gglobs.Ymin', 'gglobs.Ymax', 'gglobs.Yunit', 'gglobs.cpmflag']

    dprint(gglobs.debug,"printVarsStatus: origin=", origin)
    for name in myVars:
        dprint(gglobs.debug,"     {:35s} =    {}".format(name, eval(name)))


    print( "Globals " + "-" * 100)
    item = ""
    g = globals()
    for item in g:
        print (item)
    for name in g:
        dprint(gglobs.debug,"  {:35s} =    {}".format(name, eval(name)))


    print( "Locals " + "-" * 100)
    g = locals()
    for item in g:
        print (item)
    for name in g:
        dprint(gglobs.debug,"  {:35s} =    {}".format(name, eval(name)))


def html_escape(text):
    """Produce entities within text."""

    html_escape_table = {
        "&": "&amp;",
        '"': "&quot;",
        "'": "&apos;",
        ">": "&gt;",
        "<": "&lt;",
        }

    return text
    return "".join(html_escape_table.get(c,c) for c in text)


def resetVars():
    """reset all gglobs variables with var data to None"""

    # from the gglobs.py file
    gglobs.logTime             = None                # array: Time data from total file
    gglobs.logTimeDiff         = None                # array: Time data as time diff to first record in days
    gglobs.logTimeFirst        = None                # value: Time of first record of total file
    gglobs.logTimeSlice        = None                # array: selected slice out of logTime
    gglobs.logTimeDiffSlice    = None                # array: selected slice out of logTimeDiff

    gglobs.logCPM              = None                # array: CPM Data from total file
    gglobs.logCPMSlice         = None                # array: selected slice out of logCPM
    gglobs.logSliceMod         = None

    gglobs.sizePlotSlice       = None                # value: size of plotTimeSlice

    gglobs.currentFileData     = None                # 2dim numpy array with the currently plotted data


def resetVarSettings():

    # prevent updating while selections are made
    gglobs.allowGraphUpdate    = False

    #for i, key in enumerate(gglobs.varnames):
    #    gglobs.varchecked       [key]           = False
    #    gglobs.ex.vbox          [key]           .setChecked(False)
    #    gglobs.ex.vbox          [key]           .setEnabled(False)
    #    gglobs.ex.select.model().item(i)        .setEnabled(False)

    for i, key in enumerate(gglobs.varnames):
        if gglobs.varlog[key]:
            gglobs.varchecked       [key]      = True
            gglobs.ex.vbox          [key]      .setChecked(True)
            gglobs.ex.vbox          [key]      .setEnabled(True)
            gglobs.ex.select.model().item(i)   .setEnabled(True)
        else:
            gglobs.varchecked       [key]      = False
            gglobs.ex.vbox          [key]      .setChecked(False)
            gglobs.ex.vbox          [key]      .setEnabled(False)
            gglobs.ex.select.model().item(i)   .setEnabled(False)

    gglobs.allowGraphUpdate    = True


# Configuration file reading
def readGeigerConfig():
    """reading the configuration file, return if not available.
    Not-available or illegal options are being ignored with only a debug message"""

    dprint(gglobs.debug, "readGeigerConfig: using config file: ", gglobs.configPath)
    debugIndent(1)

    infostr = "INFO: {:30s}: {}"
    while True:
        if not os.path.isfile(gglobs.configPath): # does the config file exist?
            dprint(True, "WARNING: Configuration file '{}' does not exist. Continuing with default values.".format(gglobs.configPath))
            break

        try:                                      # and can it be read?
            config = configparser.ConfigParser()
            config.readfp(open(gglobs.configPath))
        except Exception as e:
            srcinfo = TYELLOW + "ERROR reading the configuration file '{}'.".format(gglobs.configPath) + TDEFAULT
            exceptPrint(e, sys.exc_info(), srcinfo)
            dprint(True, "Please, review and correct")
            sys.exit(2)

    # Audio
        try:
            t = config.get("Audio", "phonon")
            if t.lower() == "active":  gglobs.phonon = "active"
            else:                      gglobs.phonon = "inactive"
            dprint(gglobs.debug, infostr.format("Audio phonon", gglobs.phonon))
        except:
            dprint(True, "WARNING: Config Audio phonon is not available")


    # Defaults
        # calibration 1st tube is 0.0065
        try:
            t = config.get("Defaults", "DEFcalibration")
            if float(t) > 0:    gglobs.DEFcalibration = float(t)
            else:               gglobs.DEFcalibration = 0.0065
            dprint(gglobs.debug, infostr.format("DEFcalibration", gglobs.DEFcalibration))
        except:
            dprint(True, "WARNING: Config DEFcalibration not available")

        # calibration 2nd tube is 0.194
        try:
            t = config.get("Defaults", "DEFcalibration2nd")
            if float(t) > 0:     gglobs.DEFcalibration2nd = float(t)
            else:                gglobs.DEFcalibration2nd = 0.194
            dprint(gglobs.debug, infostr.format("DEFcalibration 2nd tube", gglobs.DEFcalibration2nd))
        except:
            dprint(True, "WARNING: Config DEFcalibration2nd for 2nd tube not available")

        # calibration RadMon tube is 0.0065
        try:
            t = config.get("Defaults", "DEFRMcalibration")
            if float(t) > 0:    gglobs.DEFRMcalibration = float(t)
            else:               gglobs.DEFRMcalibration = 0.0065
            dprint(gglobs.debug, infostr.format("DEFRMcalibration", gglobs.DEFRMcalibration))
        except:
            dprint(True, "WARNING: Config DEFRMcalibration not available")


    # Serial Port
        try:
            gglobs.usbport = config.get("Serial Port", "port")
            dprint(gglobs.debug, infostr.format("Using port", gglobs.usbport))
        except:
            dprint(True, "WARNING: Config Serial Port not available")

        try:
            b = config.getint("Serial Port", "baudrate")
            if b in gglobs.baudrates:
                gglobs.baudrate = b
            dprint(gglobs.debug, infostr.format("Using baudrate", gglobs.baudrate))
        except:
            dprint(True, "WARNING: Config baudrate not available")

        try:
            t = config.getfloat("Serial Port", "timeout")
            if t > 0:
                gglobs.timeout = t
            else:
                gglobs.timeout = 3  # if zero or negative value given, set to 3

            dprint(gglobs.debug, infostr.format("Using timeout (sec)",gglobs.timeout))
        except:
            dprint(True, "WARNING: Config timeout not available")

        try:
            t = config.getfloat("Serial Port", "timeout_write")
            if t > 0:
                gglobs.timeout_write = t
            else:
                gglobs.timeout_write = 1  # if zero or negative value given, set to 1

            dprint(gglobs.debug, infostr.format("Using timeout_write (sec)",gglobs.timeout_write))
        except:
            dprint(True, "WARNING: Config timeout_write not available")


        try:
            t = config.get("Serial Port", "ttyS")
            if t.upper() == 'INCLUDE':
                gglobs.ttyS = 'include'
            else:
                gglobs.ttys = 'ignore'
            dprint(gglobs.debug, infostr.format("Ports of ttyS type", gglobs.ttys))
        except:
            dprint(True, "WARNING: Config ttyS not available")

    # Device
        # Device customdevice
        # not needed anymore
        """
        try:
            gglobs.customdevice = config.get("Device", "customdevice")
            dprint(gglobs.debug, "INFO: Custom Device is: ", gglobs.customdevice)
        except:
            gglobs.customdevice = None
            dprint(True, "WARNING: Custom device not available")
        """

        # Device memory
        try:
            t = config.get("Device", "memory")
            if t.upper() == '1MB':
                gglobs.memory     = 2**20

            elif t.upper() == '64KB':
                gglobs.memory     = 2**16

            else:                               # auto
                gglobs.memory   = 'auto'

            dprint(gglobs.debug, infostr.format("Memory", gglobs.memory))
        except:
            dprint(True, "WARNING: Config memory not available")


        # Device SPIRpage
        try:
            t = config.get("Device", "SPIRpage")
            if t.upper() == '2K':
                gglobs.SPIRpage     = 2048
                #gglobs.memoryMode = 'fixed'

            elif t.upper() == '4K':
                gglobs.SPIRpage     = 4096
                #gglobs.memoryMode = 'fixed'

            else:                               # auto
                gglobs.SPIRpage = 'auto'

            dprint(gglobs.debug, infostr.format("SPIRpage", gglobs.SPIRpage))
        except:
            dprint(True, "WARNING: Config SPIRpage not available")

        # Device SPIRbugfix
        try:
            t = config.get("Device", "SPIRbugfix")
            if t.upper() == 'YES':
                gglobs.SPIRbugfix     = True
                #gglobs.memoryMode = 'fixed'

            elif t.upper() == 'NO':
                gglobs.SPIRbugfix     = False
                #gglobs.memoryMode = 'fixed'

            else:                               # auto
                gglobs.SPIRbugfix = 'auto'

            dprint(gglobs.debug, infostr.format("SPIRbugfix", gglobs.SPIRbugfix))
        except:
            dprint(True, "WARNING: Config SPIRbugfix not available")

        # Device configsize
        try:
            t = config.get("Device", "configsize")
            if t.upper() == '256':
                gglobs.configsize     = 256

            elif t.upper() == '512':
                gglobs.configsize     = 512

            else:                               # auto
                gglobs.configsize = 'auto'

            dprint(gglobs.debug, infostr.format("configsize", gglobs.configsize))
        except:
            dprint(True, "WARNING: Config configsize not available")

        # Device calibration 1st tube
        # default in gglobs is 0.0065
        try:
            t = config.get("Device", "calibration")
            if t.upper() == 'AUTO': gglobs.calibration = "auto"
            else:
                if float(t) > 0:    gglobs.calibration = float(t)
                else:               gglobs.calibration = "auto"

            dprint(gglobs.debug, infostr.format("Calibration", gglobs.calibration))
        except:
            dprint(True, "WARNING: Config calibration not available")

        # Device calibration 2nd tube
        # default in gglobs is 0.194
        try:
            t = config.get("Device", "calibration2nd")
            if t.upper() == 'AUTO':  gglobs.calibration2nd = "auto"
            else:
                if float(t) > 0:     gglobs.calibration2nd = float(t)
                else:                gglobs.calibration2nd = "auto"

            dprint(gglobs.debug, infostr.format("Calibration 2nd tube", gglobs.calibration2nd))
        except:
            dprint(True, "WARNING: Config calibration for 2nd tube not available")

        # Device voltagebytes
        try:
            t = config.get("Device", "voltagebytes")
            if   t.upper() == '1':      gglobs.voltagebytes = 1
            elif t.upper() == '5':      gglobs.voltagebytes = 5
            else:                       gglobs.voltagebytes = 'auto'

            dprint(gglobs.debug, infostr.format("voltagebytes", gglobs.voltagebytes))
        except:
            dprint(True, "WARNING: Config voltagebytes not available")

        # Device endianness
        try:
            t = config.get("Device", "endianness")
            if   t.upper() == 'LITTLE': gglobs.endianness = 'little'
            elif t.upper() == 'BIG':    gglobs.endianness = 'big'
            else:                       gglobs.endianness = 'auto'

            dprint(gglobs.debug, infostr.format("endianness", gglobs.endianness))
        except:
            dprint(True, "WARNING: Config endianness not available")

        # Device variables
        try:
            t = config.get("Device", "variables")
            if t.upper() == "AUTO":     gglobs.GMCvariables = "auto"
            else:                       gglobs.GMCvariables = t.strip()

            dprint(gglobs.debug, infostr.format("variables", gglobs.GMCvariables))
        except:
            dprint(True, "WARNING: Config variables not available")

        # Device nbytes
        try:
            t = config.get("Device", "nbytes")
            if t.upper() == "AUTO":     gglobs.nbytes = "auto"
            else:
                nt = int(t.strip())
                if nt in (2, 4):
                    gglobs.nbytes = nt
                else:
                    gglobs.nbytes = 2

            dprint(gglobs.debug, infostr.format("nbytes", gglobs.nbytes))
        except:
            dprint(True, "WARNING: Config nbytes not available")


    # Folder data
        errmsg = "glaub ich nicht"
        try:
            t = config.get("Folder", "data")
            #print "gglobs.dataPath:", gglobs.dataPath
            if t == "":
                pass    # no change to default
            else:
                if os.path.isabs(t):  # is absolute path?
                    testpath = t
                else:
                    testpath = gglobs.dataPath + "/" + t

                #
                # Make sure that data directory exists; create it if needed
                # ignore if it cannot be made or is not writable
                #
                if os.access(testpath , os.F_OK):
                    # dir exists, ok
                    if not os.access(testpath , os.W_OK):
                        # dir exists, but is not writable
                        errmsg = "Configured data directory '{}' exists, but is not writable".format(testpath)
                        raise NameError
                    else:
                        # dir exists and is writable
                        gglobs.dataPath = testpath
                else:
                    # dir does not exist; make it
                    try:
                        os.mkdir(testpath)
                        gglobs.dataPath = testpath
                    except:
                        # dir cannot be made
                        errmsg = "Could not make configured data directory '{}'".format(testpath)
                        raise NameError

            dprint(gglobs.debug, infostr.format("Data directory", gglobs.dataPath))
        except:
            dprint(True, "WARNING: " + errmsg)

    # Logging
        try:
            t = config.getfloat("Logging", "logcycle")
            if t >= 0.1:
                gglobs.logcycle = t
            dprint(gglobs.debug, infostr.format("Logcycle (sec)", gglobs.logcycle))
        except:
            dprint(True, "WARNING: Config logcycle not available")

    # Graphic
        try:
            t = int(config.getfloat("Graphic", "mav_initial"))
            if t >= 1:
                gglobs.mav_initial = t
            dprint(gglobs.debug, infostr.format("Moving Average (sec)", int(gglobs.mav_initial)))
        except:
            dprint(True, "WARNING: Config mav_initial not available")

    # Plotstyle
        try:
            g1 = config.get("Plotstyle", "linestyle")
            g2 = config.get("Plotstyle", "linecolor")
            g3 = config.get("Plotstyle", "linewidth")
            g4 = config.get("Plotstyle", "markerstyle")
            g5 = config.get("Plotstyle", "markersize")
            gglobs.linestyle           = g1
            gglobs.linecolor           = g2
            gglobs.linewidth           = g3
            gglobs.markerstyle         = g4
            gglobs.markersize          = g5

        except:
            dprint(True, "WARNING: Could not recognize all plot style settings")

    # Window
        try:
            w = config.getint("Window", "width")
            h = config.getint("Window", "height")
            if w > 500 and w < 5000 and h > 100 and h < 5000:
                gglobs.window_width  = w
                gglobs.window_height = h
                dprint(gglobs.debug, infostr.format("Window dimensions", "{} x {} pixel".format(gglobs.window_width, gglobs.window_height)))
            else:
                dprint(True, "WARNING: Config Window dimension out-of-bound; ignored: {} x {} pixel".format(gglobs.window_width, gglobs.window_height))
        except:
            dprint(True, "WARNING: Config Window dimension not available")

    # Window size
        try:
            t = config.get("Window", "size")
            if t.upper() == 'MAXIMIZED':
                gglobs.window_size = 'maximized'
            else:
                gglobs.window_size = None
            dprint(gglobs.debug, infostr.format("Window Size", t))
        except:
            dprint(True, "WARNING: Window size not available")

    # Manual
        try:
            t = config.get("Manual", "manual_name")
            if t.upper() == 'AUTO' or t == "":
                gglobs.manual_filename = 'auto'
                dprint(gglobs.debug, infostr.format("Manual file", gglobs.manual_filename))
            else:
                manual_file = getProgPath() + "/" + t
                #print "readGeigerConfig manual_file:", manual_file
                if os.path.isfile(manual_file): # does the config file exist?
                    # it exists
                    gglobs.manual_filename = t
                    dprint(gglobs.debug, infostr.format("Manual file",t))
                else:
                    # it does not exist
                    gglobs.manual_filename = 'auto'
                    dprint(gglobs.debug, "WARNING: Manual file '{}' does not exist".format(t))
        except:
            dprint(True, "WARNING: Config for manual file not available")


    # Radiation World Maps
        try:
            t = config.get("Worldmaps", "GMCmapWebsite")
            gglobs.GMCmap["Website"] = t
            dprint(gglobs.debug, infostr.format("Worldmaps GMCmapWebsite", t ))
        except:
            gglobs.GMCmap["Website"] = ""
            dprint(True, "WARNING: Config for Worldmaps GMCmapWebsite not available")

        try:
            t = config.get("Worldmaps", "GMCmapURL")
            gglobs.GMCmap["URL"]  = t
            dprint(gglobs.debug, infostr.format("Worldmaps GMCmapURL", t ))
        except:
            gglobs.GMCmap["URL"] = ""
            dprint(True, "WARNING: Config for Worldmaps GMCmapURL not available")

        try:
            t = config.get("Worldmaps", "GMCmapSSID")
            gglobs.GMCmap["SSID"]  = t
            dprint(gglobs.debug, infostr.format("Worldmaps GMCmapSSID", t ))
        except:
            gglobs.GMCmap["SSID"] = ""
            dprint(True, "WARNING: Config for Worldmaps GMCmapSSID not available")

        try:
            t = config.get("Worldmaps", "GMCmapPassword")
            gglobs.GMCmap["Password"] = t
            dprint(gglobs.debug, infostr.format("Worldmaps GMCmapPassword", t ))
        except:
            gglobs.GMCmap["Password"] = ""
            dprint(True, "WARNING: Config for Worldmaps GMCmapPassword not available")

        try:
            t = config.get("Worldmaps", "GMCmapUserID")
            gglobs.GMCmap["UserID"] = t
            dprint(gglobs.debug, infostr.format("Worldmaps GMCmapUserID", t ))
        except:
            gglobs.GMCmap["UserID"] = ""
            dprint(True, "WARNING: Config for Worldmaps GMCmapUserID not available")

        try:
            t = config.get("Worldmaps", "GMCmapCounterID")
            gglobs.GMCmap["CounterID"] = t
            dprint(gglobs.debug, infostr.format("Worldmaps GMCmapCounterID", t ))
        except:
            gglobs.GMCmap["CounterID"] = ""
            dprint(True, "WARNING: Config for Worldmaps GMCmapCounterID not available")

        try:
            t = config.get("Worldmaps", "GMCmapPeriod")
            gglobs.GMCmap["Period"] = t
            dprint(gglobs.debug, infostr.format("Worldmaps GMCmapPeriod", t ))
        except:
            gglobs.GMCmap["Period"] = ""
            dprint(True, "WARNING: Config for Worldmaps GMCmapPeriod not available")


    # RadMonPlus
        # RadMon Server IP
        try:
            t = config.get("RadMonPlus", "RMserverIP")
            if t.strip().upper() == "NONE": gglobs.RMserverIP = None
            else:                           gglobs.RMserverIP = t.strip()
            dprint(gglobs.debug, infostr.format("RadMonPlus RMserverIP:", gglobs.RMserverIP ))
        except:
            gglobs.RMserverIP = None
            dprint(True, "WARNING: Config for RadMonPlus RMserverIP not available")

        # RadMon Server Port
        try:
            t = config.get("RadMonPlus", "RMserverPort")
            gglobs.RMserverPort = abs(int(t))
            dprint(gglobs.debug, infostr.format("RadMonPlus RMserverPort:", gglobs.RMserverPort ))
        except:
            gglobs.RMserverPort = 1883
            dprint(True, "WARNING: Config for RadMonPlus RMserverPort not available")

        # Radmon timeout
        try:
            t = config.getfloat("RadMonPlus", "RMtimeout")
            if t > 0: gglobs.RMtimeout = t
            else:     gglobs.RMtimeout = 3  # if zero or negative value given, the set to 3
            dprint(gglobs.debug, infostr.format("RadMonPlus timeout (sec)",gglobs.timeout))
        except:
            dprint(True, "WARNING: Config RMtimeout not available")

        # RadMon Server Folder
        try:
            t = config.get("RadMonPlus", "RMserverFolder")
            t = t.strip()
            if " " in t or t.upper() == "AUTO": # blank in folder name not allowed
                gglobs.RMserverFolder = "/"
            else:
                gglobs.RMserverFolder = t

            if gglobs.RMserverFolder[-1] != "/": gglobs.RMserverFolder += "/"

            dprint(gglobs.debug, infostr.format("RadMonPlus RMserverFolder:", gglobs.RMserverFolder ))
        except:
            gglobs.RMserverFolder = "/"
            dprint(True, "WARNING: Config for RadMonPlus RMserverFolder not available")

        # RadMon calibration tube
        # default in gglobs is 0.0065 µSv/h/CPM
        try:
            t = config.get("RadMonPlus", "RMcalibration")
            if t.upper() == 'AUTO': gglobs.RMcalibration = "auto"
            else:
                if float(t) > 0: gglobs.RMcalibration = float(t)
                else:            gglobs.RMcalibration = "auto"

            dprint(gglobs.debug, infostr.format("RadMonPlus Calibration", gglobs.RMcalibration))
        except:
            dprint(True, "WARNING: Config RadMonPlus calibration not available")

        # Radmon variables
        try:
            t = config.get("RadMonPlus", "RMvariables")
            if t.upper() == "AUTO":     gglobs.RMvariables = "auto"
            else:                       gglobs.RMvariables = t.strip()

            dprint(gglobs.debug, infostr.format("RadMonPlus variables", gglobs.RMvariables))
        except:
            dprint(True, "WARNING: Config RadMonPlus variables not available")


    # Scaling
    # GMC Variables
        try:
            t = config.get("Scaling", "ScaleCPM")
            t = t.strip().upper()
            if t == "":     pass                # use value from gglobs
            else:           gglobs.ScaleCPM = t

            dprint(gglobs.debug, infostr.format("Scaling ScaleCPM", gglobs.ScaleCPM))
        except:
            dprint(True, "WARNING: Config Scaling ScaleCPM not available")

        try:
            t = config.get("Scaling", "ScaleCPM1st")
            t = t.strip().upper()
            if t == "":     pass                # use value from gglobs
            else:           gglobs.ScaleCPM1st = t

            dprint(gglobs.debug, infostr.format("Scaling ScaleCPM1st", gglobs.ScaleCPM1st))
        except:
            dprint(True, "WARNING: Config Scaling ScaleCPM1st not available")

        try:
            t = config.get("Scaling", "ScaleCPM2nd")
            t = t.strip().upper()
            if t == "":     pass                # use value from gglobs
            else:           gglobs.ScaleCPM2nd = t

            dprint(gglobs.debug, infostr.format("Scaling ScaleCPM2nd", gglobs.ScaleCPM2nd))
        except:
            dprint(True, "WARNING: Config Scaling ScaleCPM2nd not available")

        try:
            t = config.get("Scaling", "ScaleCPS")
            t = t.strip().upper()
            if t == "":     pass                # use value from gglobs
            else:           gglobs.ScaleCPS = t

            dprint(gglobs.debug, infostr.format("Scaling ScaleCPS", gglobs.ScaleCPS))
        except:
            dprint(True, "WARNING: Config Scaling ScaleCPS not available")

        try:
            t = config.get("Scaling", "ScaleCPS1st")
            t = t.strip().upper()
            if t == "":     pass                # use value from gglobs
            else:           gglobs.ScaleCPS1st = t

            dprint(gglobs.debug, infostr.format("Scaling ScaleCPS1st", gglobs.ScaleCPS1st))
        except:
            dprint(True, "WARNING: Config Scaling ScaleCPS1st not available")

        try:
            t = config.get("Scaling", "ScaleCPS2nd")
            t = t.strip().upper()
            if t == "":     pass                # use value from gglobs
            else:           gglobs.ScaleCPS2nd = t

            dprint(gglobs.debug, infostr.format("Scaling ScaleCPS2nd", gglobs.ScaleCPS2nd))
        except:
            dprint(True, "WARNING: Config Scaling ScaleCPS2nd not available")


    # RadMon+ Variables
        try:
            t = config.get("Scaling", "ScaleT")
            t = t.strip().upper()
            if t == "":     pass                # use value from gglobs
            else:           gglobs.ScaleT = t

            dprint(gglobs.debug, infostr.format("Scaling ScaleT", gglobs.ScaleT))
        except:
            dprint(True, "WARNING: Config Scaling ScaleT not available")

        try:
            t = config.get("Scaling", "ScaleP")
            t = t.strip().upper()
            if t == "":     pass                # use value from gglobs
            else:           gglobs.ScaleP = t

            dprint(gglobs.debug, infostr.format("Scaling ScaleP", gglobs.ScaleP))
        except:
            dprint(True, "WARNING: Config Scaling ScaleP not available")

        try:
            t = config.get("Scaling", "ScaleH")
            t = t.strip().upper()
            if t == "":     pass                # use value from gglobs
            else:           gglobs.ScaleH = t

            dprint(gglobs.debug, infostr.format("Scaling ScaleH", gglobs.ScaleH))
        except:
            dprint(True, "WARNING: Config Scaling ScaleH not available")

        try:
            t = config.get("Scaling", "ScaleR")
            t = t.strip().upper()
            if t == "":     pass                # use value from gglobs
            else:           gglobs.ScaleR = t

            dprint(gglobs.debug, infostr.format("Scaling ScaleR", gglobs.ScaleR))
        except:
            dprint(True, "WARNING: Config Scaling ScaleR not available")



    # Style
        #try:
        #    t = config.get("Style", "style")
        #    s = [a.upper() for a in ('Breeze',  "Cleanlooks", "Windows", "Plastique")]
        #    if t.upper() in s :
        #        gglobs.style = t
        #    else:
        #        gglobs.style = None
        #except:
        #    dprint(True, "Config style not available")


        break # don't forget to break!

    debugIndent(0)



def version_status():
    """returns versions as list of various components"""

    python_version = sys.version.replace('\n', "")

    #https://wiki.python.org/moin/PyQt/Getting%20the%20version%20numbers%20of%20Qt%2C%20SIP%20and%20PyQt
    from PyQt4.QtCore   import QT_VERSION_STR       as qt_version
    from PyQt4.Qt       import PYQT_VERSION_STR     as pyqt_version
    from sip            import SIP_VERSION_STR      as sip_version
    from matplotlib     import __version__          as mpl_version
    from numpy          import version              as np_version
    from scipy          import __version__          as scipy_version
    from serial         import __version__          as serial_version
    from paho.mqtt      import __version__          as paho_version

    version_status = []
    version_status.append(["GeigerLog",    "{}".format(gglobs.__version__)])
    version_status.append(["Python",       "{}".format(python_version)])
    version_status.append(["pyserial",     "{}".format(serial_version)])
    version_status.append(["matplotlib",   "{}".format(mpl_version)])
    version_status.append(["numpy",        "{}".format(np_version.version)])
    version_status.append(["scipy",        "{}".format(scipy_version)])
    version_status.append(["Qt",           "{}".format(qt_version)])
    version_status.append(["PyQt",         "{}".format(pyqt_version)])
    version_status.append(["SIP",          "{}".format(sip_version)])
    version_status.append(["paho.mqtt",    "{}".format(paho_version)])

    return version_status


def beep():
    """do a system beep"""

    QtGui.QApplication.beep()
    QtGui.QApplication.processEvents()


def playMedia(error=False):
    """plays a sound, either normal sound or error sound, but only if the
    phonon module is active.
    If not active then the system beep will sound, but only on errors"""

    if gglobs.phonon == "inactive":
        if error:  beep()
        else:      pass                         # beeps only on errors
    else:
        if error:  gglobs.mediaErr.play()
        else:      gglobs.media.play()


def signal_handler(signal, frame):
    """Allows to handle the signals SIGINT, SIGTSTP, SIGQUIT, SIGUSR1, SIGUSR2"""

    # Requires these commands in main:
    # signal.signal(signal.SIGINT,  signal_handler)   # to handle CTRL-C
    # signal.signal(signal.SIGTSTP, signal_handler)   # to handle CTRL-Z
    # signal.signal(signal.SIGQUIT, signal_handler)   # to handle CTRL-\
    # signal.signal(signal.SIGUSR1, signal_handler)   # to handle user signal1
    # signal.signal(signal.SIGUSR2, signal_handler)   # to handle user signal2

    print()
    dprint(gglobs.debug, "signal_handler: signal: {}, frame: {}".format(signal, frame))

    if signal == 2:                 # SIGINT CTRL-C to shutdown
        dprint(gglobs.debug, 'signal_handler: received SIGINT from CTRL-C Keyboard Interrupt - Exiting')

    elif signal == 20:              # SIGTSTP CTRL-Z to shutdown
        dprint(gglobs.debug, 'signal_handler: received SIGTSTP from CTRL-Z - Exiting')

    else:                           # unexpected signal
        dprint(gglobs.debug, 'signal_handler: signal:', signal, ", Undefined signal action")
        return

    gradmon.terminateRadMon()
    sys.exit()                      # to exit on CTRL-C this is needed
                                    # the GeigerLog closeEvent is NOT activated!


def scaleValues(variable, value, scale):
    """
    Apply the 'Scaling' declared in configuration file geigerlog.cfg
    Return: the scaled value (or original in case of error)
    NOTE:   scale is in upper-case, but may be empty or NONE
    """

    if scale == "VAL" or scale == "" or scale == "NONE": return value

    # example: scale: LOG(VAL)+1000         # orig
    # becomes: ls   : np.log(value)+1000    # mod
    ls = scale
    ls = ls.replace("VAL",    "value")        # the data of that column
    ls = ls.replace("LOG",    "np.log")       # Log to base e; natural log
    ls = ls.replace("LOG10",  "np.log10")     # Log to base 10
    ls = ls.replace("LOG2",   "np.log2")      # Log to base 2
    ls = ls.replace("SIN",    "np.sin")       # sine
    ls = ls.replace("COS",    "np.cos")       # cosine
    ls = ls.replace("TAN",    "np.tan")       # tangent
    ls = ls.replace("SQRT",   "np.sqrt")      # square root
    ls = ls.replace("CBRT",   "np.cbrt")      # cube root
    ls = ls.replace("ABS",    "np.absolute")  # absolute value
    ls = ls.replace("INT",    "int")          # integer value

    try:
        scaledValue = eval(ls)
    except Exception as e:
        msg = "ERROR scaling variable:'{}' formula:'{}', errmsg: {}".format(variable, scale, e)
        dprint(True, msg)
        fprint(msg, error=True)
        fprint("Returning original value", error=True)
        scaledValue = value

    vprint(gglobs.verbose, "scaleValues: variable:{}, original value:{}, orig scale:{}, mod scale:'{}', scaled value:{}".format(variable, value, scale, ls, scaledValue))

    return round(scaledValue, 2)
