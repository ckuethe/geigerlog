#! /usr/bin/env python3
# -*- coding: UTF-8 -*-

"""
gsup_utils.py - GeigerLog utilities with imports

include in programs with:
    from gsup_utils include *
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
__copyright__       = "Copyright 2016, 2017, 2018, 2019, 2020, 2021, 2022"
__credits__         = [""]
__license__         = "GPL3"


# Function names:
# print(fncname)
# print(__name__) # gibt modul namen, like 'util'
# print(sys._getframe().f_code.co_name) # gibt korrekten Namen der Funktion

# get extensive output on crashes
# python3 -q -X faulthandler

#
# modules - available in std Python
#
import sys, os, io, time, datetime  # basic modules
import warnings                     # warning messages
import platform                     # info on OS, machine, architecture, ...
import traceback                    # for traceback on error; used in: exceptPrint
import inspect                      # finding origin of f'on calls
import copy                         # make shallow and deep copies
import threading                    # higher-level threading interfaces
import queue                        # queue for threading
import re                           # regex
import configparser                 # parse configuration file geigerlog.cfg
import urllib.request               # for ambiomon web transfer and Radiation World Map
import urllib.parse                 # for use with Radiation World Map
import struct                       # packing numbers into chars (needed by gdev_gmc.py)
import sqlite3                      # sudo -H pip3 install  pysqlite3; but should be part of python3 (needed by gsup_sql.py)
import getopt                       # parse command line for options and commands
import signal                       # handling signals like CTRL-C and other
import subprocess                   # to allow terminal commands tput rmam / tput smam
import socket                       # finding IP Adress
import http.server                  # web server

#
# modules - requiring installation via pip
#
import serial                       # make it a required installation, since serial.tools.list_ports is anyway
import serial.tools.list_ports      # allows listing of serial ports and searching within; needed by getSerialConfig, getPortList
import numpy             as np      # scientific computing with Python

import scipy                        # all of scipy
import scipy.signal                 # a subpackage of scipy; needs separate import
import scipy.stats                  # a subpackage of scipy; needs separate import
import scipy.optimize               # needed for deadtime correction with paralysation
import sounddevice       as sd      # sound output input
import soundfile         as sf      # handling sound files; can read and write

# PyQt - install via pip, but sometimes must use distribution package manager
# print("Importing PyQt")
from PyQt5.QtWidgets                import *
from PyQt5.QtGui                    import *
from PyQt5.QtCore                   import *
from PyQt5.QtPrintSupport           import *

# matplotlib importing and settings
# print("Importing matplotlib")
import matplotlib                               # Visualization with Python
matplotlib.use('Qt5Agg', force=False)           # use Qt5Agg, not the default TkAgg
import matplotlib.backends.backend_qt5agg       # MUST be done BEFORE importing pyplot! requires PyQt!
from   matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg    as FigureCanvas
from   matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar

import matplotlib.pyplot    as plt              # MUST import AFTER 'matplotlib.use()'
import matplotlib.dates     as mpld
import matplotlib.animation as mplanim
import matplotlib.patches   as mpat

# next lines are better done in other code,
# matplotlib.pyplot.figure(num=None, figsize=None, dpi=None, ...)
# dpi ersetzen mit dpi of current screen, see geigerlog lines ~370

#~matplotlib.rcParams['figure.figsize']     = [8.0, 6.0]
#~matplotlib.rcParams['figure.dpi']         = 50
#~matplotlib.rcParams['savefig.dpi']        = 100
#~matplotlib.rcParams['font.size']          = 12
#~matplotlib.rcParams['legend.fontsize']    = 'large'
#~matplotlib.rcParams['figure.titlesize']   = 'medium'

#~print(matplotlib.rcParams['figure.figsize'])
#~print(matplotlib.rcParams['figure.dpi'])
#~print(matplotlib.rcParams['savefig.dpi'])
#~print(matplotlib.rcParams['font.size'])
#~print(matplotlib.rcParams['legend.fontsize'])
#~print(matplotlib.rcParams['figure.titlesize'])

import gglobs                               # all global vars

#
# Getting Version numbers
#
# # Getting the version numbers of Qt, SIP and PyQt:
# # https://wiki.python.org/moin/PyQt/Getting%20the%20version%20numbers%20of%20Qt%2C%20SIP%20and%20PyQt
#     from PyQt4.QtCore import QT_VERSION_STR
#     from PyQt4.Qt import PYQT_VERSION_STR
#     from sip import SIP_VERSION_STR
#     print("Qt version:", QT_VERSION_STR)
#     print("SIP version:", SIP_VERSION_STR)
#     print("PyQt version:", PYQT_VERSION_STR)
#
# sqlite3.version:                The version number of this module, as a string. This is not the version of the SQLite library.
# sqlite3.version_info:           The version number of this module, as a tuple of integers. This is not the version of the SQLite library.
# sqlite3.sqlite_version:         The version number of the run-time SQLite library, as a string.
# sqlite3.sqlite_version_info:    The version number of the run-time SQLite library, as a tuple of integers.
#
# Use of pkg_resources is discouraged in favor of importlib.resources, importlib.metadata,
# and their backports (resources, metadata).
#   import pkg_resources
#   setuptools_version = pkg_resources.get_distribution('setuptools').version

notfound            = "Not found"
pyqt5sip_version    = notfound
ntplib_version      = notfound
setuptools_version  = notfound
pip_version         = notfound

if sys.version_info >= (3, 8):    # only Python version >= v3.8
    import importlib.metadata

    try:    pyqt5sip_version    = importlib.metadata.version('PyQt5-sip')
    except: pass

    try:    ntplib_version      = importlib.metadata.version('ntplib')
    except: pass

    try:    setuptools_version  = importlib.metadata.version('setuptools')
    except: pass

    try:    pip_version         = importlib.metadata.version('pip')
    except: pass

else:
    from pip            import __version__          as pip_version


from sip import SIP_VERSION_STR

gglobs.versions                         = {}
gglobs.versions["GeigerLog"]            = gglobs.__version__
gglobs.versions["Python"]               = sys.version.replace('\n', "")
gglobs.versions["pip"]                  = pip_version
gglobs.versions["setuptools"]           = setuptools_version

gglobs.versions["PyQt"]                 = PYQT_VERSION_STR
gglobs.versions["PyQt-Qt"]              = QT_VERSION_STR
gglobs.versions["PyQt-sip"]             = pyqt5sip_version
gglobs.versions["SIP"]                  = SIP_VERSION_STR

gglobs.versions["matplotlib"]           = matplotlib.__version__
gglobs.versions["matplotlib backend"]   = matplotlib.get_backend()
gglobs.versions["numpy"]                = np.__version__
gglobs.versions["numpy float-errors"]   = np.geterr()                       # Get the current way of handling floating-point errors.
gglobs.versions["scipy"]                = scipy.__version__

gglobs.versions["sqlite3 module"]       = sqlite3.version
gglobs.versions["sql3lib library"]      = sqlite3.sqlite_version

gglobs.versions["sounddevice"]          = sd.__version__
gglobs.versions["SoundFile"]            = sf.__version__
gglobs.versions["PortAudio"]            = sd.get_portaudio_version()
gglobs.versions["pyserial"]             = serial.__version__

udul = "undefined until loaded"

gglobs.versions["paho-mqtt"]            = udul    # paho.mqtt.__version__
gglobs.versions["LabJackPython"]        = udul    # LabJackPython.__version__
gglobs.versions["U3"]                   = udul    # this has no version!
gglobs.versions["EI1050"]               = udul    # ei1050.__version__
gglobs.versions["ntplib"]               = udul    # ntplib_version


# colors for the terminal (do not put in gglobs, as this would require 'gglobs.' prefix!)
# https://gist.github.com/vratiu/9780109
# https://stackoverflow.com/questions/5947742/how-to-change-the-output-color-of-echo-in-linux
# '90' values are supposed to be high intensity
TDEFAULT            = '\033[0m'             # default, i.e greyish
TRED                = '\033[91m'            # red
TGREEN              = '\033[92m'            # light green
TYELLOW             = '\033[93m'            # yellow
TBLUE               = '\033[94m'            # blue (dark)
TMAGENTA            = '\033[95m'            # magenta
TCYAN               = '\033[96m'            # cyan
TWHITE              = '\033[97m'            # high intensity white
BOLDRED             = '\033[91;1m'          # bold, red
# BOLDRED           = '\033[31;1m'          # bold, red, (low intens?)
BOLDGREEN           = '\033[92;1m'          # bold, light green

BOLD                = '\033[1m'             # white (bright default)
UNDERLINE           = '\033[4m'             # underline
# BOLDREDUL         = '\033[31;1;4m'        # bold, red, underline, low intens?
# BOLDREDUL         = '\033[91;1;4m'        # bold, red, underline, high intens?


if "WINDOWS" in platform.platform().upper():# no terminal colors on Windows
    TDEFAULT = ""   # normal printout
    TRED     = ""   # (dark) red
    TGREEN   = ""   # hilite message
    TYELLOW  = ""   # error message
    TBLUE    = ""   #
    TMAGENTA = ""   # devel message
    TCYAN    = ""   # devel message
    BOLDRED  = ""   # devel message
    BOLDGREEN= ""   # devel message

NORMALCOLOR         = TDEFAULT              # normal printout
HILITECOLOR         = TGREEN                # hilite message
# ERRORCOLOR          = TYELLOW               # error message

# Devices columns naming - doing it here allows for shorter names w/o 'gglobs'
DNAME               = gglobs.DNAME          # = 0 : Device Name as Detected
VNAME               = gglobs.VNAME          # = 1 : Variables associated with this device
ACTIV               = gglobs.ACTIV          # = 2 : Device is activated in config
CONN                = gglobs.CONN           # = 3 : Device is connected


def getProgName():
    """Return program_base, i.e. 'geigerlog' even if named 'geigerlog.py' """

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
    # sollte auch damit gehen: return time.strftime("%Y-%m-%d %H:%M:%S")

    return longstime()[:-4]


def longstime():
    """Return current time as YYYY-MM-DD HH:MM:SS.mmm, (mmm=millisec)"""

    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3] # ms resolution


def datestr2num(string_date):
    """convert a Date&Time string in the form YYYY-MM-DD HH:MM:SS to a Unix timestamp in sec"""

    #print("datestr2num: string_date", string_date)
    try:    dt=time.mktime(datetime.datetime.strptime(string_date, "%Y-%m-%d %H:%M:%S").timetuple())
    except: dt = 0

    return dt


def num2datestr(timestamp):
    """convert a Unix timestamp in sec to a Date&Time string in the form YYYY-MM-DD HH:MM:SS"""

    # print("num2datestr: timestamp", timestamp)
    dt = datetime.datetime.fromtimestamp(timestamp)

    return dt


def sortDict(myDict):
    """sorts a dict by key"""

    return dict(sorted(myDict.items()))


def clamp(n, minn, maxn):
    """limit return value to be within minn and maxn"""

    return min(max(n, minn), maxn)


def IntToChar(intval):

    if intval < 128 and intval > 31:    char = chr(intval)
    else:                               char = " "

    return char


def BytesAsASCII(bytestring):
    """convert a bytes string into a string which has ASCII characters when
    printable and '.' else, with spaces every 10 bytes"""

    asc = ""
    if bytestring != None:
        for i in range(0, len(bytestring)):
            a = bytestring[i]
            if a < 128 and a > 31:  asc += chr(bytestring[i])
            else:                   asc += "."

            if ((i + 1) % 10) == 0: asc += "  "
            if ((i + 1) % 50) == 0: asc += "\n"

    return asc


def BytesAsASCIIFF(bytestring):
    """convert a bytes string into a string which has ASCII characters when
    printable and '.' else, with spaces every 10 bytes"""

    if bytestring == None:
        return ""

    else:
        asc = "  0:000   "
        for i in range(0, len(bytestring)):
            a = bytestring[i]
            if   a < 128 and a > 31:    asc += chr(bytestring[i])
            elif a == 255:              asc += "F"
            else:                       asc += "."

            if ((i + 1) % 10) == 0: asc += "    "
            if ((i + 1) % 50) == 0: asc += "\n{:3d}:{:03X}   ".format(i + 1, i + 1)

        return asc


def BytesAsHex(bytestring):
    """convert a bytes string into a str of Hex values, with dash spaces
    every 10 bytes and LF every 50"""

    bah = ""
    for i in range(0, len(bytestring)):
        bah += "{:02X} ".format(bytestring[i])

        if   ((i + 1) % 50) == 0 : bah += "\n"  # no '- '
        elif ((i + 1) % 10) == 0 : bah += "- "

    return bah


def BytesAsDec(bytestring):
    """convert a bytes string into a str of Dec values, with dash spaces
    every 10 bytes and LF every 50"""

    bad = ""
    for i in range(0, len(bytestring)):
        bad += "{:3d} ".format(bytestring[i])
        if   ((i + 1) % 50) == 0 : bad += "\n"  # no '- '
        elif ((i + 1) % 10) == 0 : bad += "- "

    return bad


def convertB2Hex(bseq):
    """Convert bytes sequence to Hex string"""

    return "{:25s} == ".format(str(bseq)) + "".join("{:02X} ".format(arg) for arg in bseq)


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
    """position txt within '==...==' string"""

    return "\n==== {} {}".format(txt, "=" * max(1, (80 - len(txt))))


def logPrint(arg):
    """print arg into logPad"""

    gglobs.logPad.append(arg)


def efprint(*args, debug=False):
    """error fprint with err sound"""

    fprint(*args, error="ERR", debug=debug, errsound=True)


def qefprint(*args, debug=False):
    """quiet error fprint, error color but no errsound"""

    fprint(*args, error="ERR", debug=debug, errsound=False)


def fprint(*args, error="", debug=False, errsound=False):
    """print all args in the notePad area; print in red on error"""

    if errsound:  playWav("error")

    # 1st arg; on error pad with &nbsp;
    arg0 = str(args[0])
    if error:   arg0 = arg0 + "&nbsp;" * (30 - len(arg0))
    ps = "{:30s}".format(arg0)

    # skip 1st arg
    for s in range(1, len(args)): ps += str(args[s])

    # jump to the end of text --> new text will always become visible
    #gglobs.notePad.ensureCursorVisible() # does work, but moves text to left, so that
                                          # cursor on most-right position becomes visible
                                          # requires moving text to left; not helpful
    gglobs.notePad.verticalScrollBar().setValue(gglobs.notePad.verticalScrollBar().maximum())

    # on error print in red
    if error == "ERR":
        ps = cleanHTML(ps)    # exchange "<", ">" with gt, lt
        ps = ps.replace("\n", "<br>")
        gglobs.notePad.append("<span style='color:red;'>" + ps + "</span>")
    else:
        gglobs.notePad.setFont(gglobs.fontstd)
        gglobs.notePad.setTextColor(QColor(40, 40, 40))
        gglobs.notePad.append(ps)

    if debug: dprint(ps.replace("&nbsp;", ""))


def commonPrint(ptype, *args, error=""):
    """Printing function to dprint, vprint, and wprint"""

    gglobs.xprintcounter += 1   # the count of dprint, vprint, wprint commands
    tag = "{:23s} {:7s}: {:.>6d} ".format(longstime(), ptype, gglobs.xprintcounter) + gglobs.debugIndent

    for arg in args: tag += str(arg)

    # last resort: "\x00" in text files results in geany (and other) not being able to open the file
    if "\x00" in tag: tag = tag.replace("\x00", "\x01")

    writeFileA(gglobs.proglogPath, tag)

    if not gglobs.redirect:  tag = tag[8:]

    if   error == "" or error == "ERR":
        print(tag + TDEFAULT)
    elif gglobs.devel:
        if   error == "yellow":         tag = TYELLOW   + tag
        elif error == "green":          tag = TGREEN    + tag
        elif error == "cyan":           tag = TCYAN     + tag
        elif error == "magenta":        tag = TMAGENTA  + tag
        elif error == "red":            tag = BOLDRED   + tag   # TRED  ist zu dunkel

        print(tag + TDEFAULT)


def wprint(*args, forcewerbose=False):
    """werbose print:
    if werbose is true then:
    - Write timestamp and args as a single line to progname.proglog file
    - Print args as single line
    else
    - do nothing
    """
    if forcewerbose or gglobs.werbose: commonPrint("werbose", *args)


def vprint(*args, forceverbose=False):
    """verbose print:
    if forceverbose or gglobs.verbose is true then:
    - Write timestamp and args as a single line to progname.proglog file
    - Print args as single line
    else
    - do nothing
    """
    if forceverbose or gglobs.verbose: commonPrint("VERBOSE", *args)


def dprint(*args, debug=False ):
    """debug print:
    if debug or gglobs.debug is true then:
    - Write timestamp and args as a single line to progname.proglog file
    - Print args as single line
    else
    - do nothing
    """
    if debug or gglobs.debug: commonPrint("DEBUG", *args)
    # if debug == None:   debug = gglobs.debug
    # if debug:           commonPrint("DEBUG", *args)


#print in yellow
def edprint(*args, debug=True):
    """edebug print:
    - Write timestamp and args as a single line to progname.proglog file
    - Print args as single line
    """
    commonPrint("DEVEL", *args, error="yellow")


# print in green
def gdprint(*args, debug=True):
    """edebug print:
    - Write timestamp and args as a single line to progname.proglog file
    - Print args as single line
    """

    commonPrint("DEVEL", *args, error="green")


# print in cyan
def cdprint(*args, debug=True):
    """edebug print:
    - Write timestamp and args as a single line to progname.proglog file
    - Print args as single line
    """

    commonPrint("DEVEL", *args, error="cyan")


# print in magenta
def mdprint(*args, debug=True):
    """edebug print:
    - Write timestamp and args as a single line to progname.proglog file
    - Print args as single line
    """

    commonPrint("DEVEL", *args, error="magenta")


# print in red
def rdprint(*args, debug=True):
    """edebug print:
    - Write timestamp and args as a single line to progname.proglog file
    - Print args as single line
    """

    commonPrint("DEVEL", *args, error="red")


def arrprint(text, array):
    """ prints an array """

    print(text)
    for a in array: print("{:10s}: ".format(a), array[a])


def exceptPrint(e, srcinfo):
    """Print exception details (errmessage, file, line no)"""

    exc_type, exc_obj, exc_tb = sys.exc_info()
    fname                     = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]    # which file?

    # edprint("EXCEPTION: '{}' {} in file: '{}' in line {}".format(e, srcinfo, fname, exc_tb.tb_lineno))
    edprint("EXCEPTION: {} ({}), in file: {}, in line: {}".format(e, srcinfo, fname, exc_tb.tb_lineno))

    if gglobs.redirect:
        edprint("EXCEPTION: Traceback:\n", traceback.format_exc(), debug=True) # more extensive info


def setDebugIndent(arg):
    """increases or decreased the indent of debug/verbose print"""

    if arg > 0:  gglobs.debugIndent += "   "
    else:        gglobs.debugIndent  = gglobs.debugIndent[:-3]


def cleanHTML(text):
    """replace < and > with printable chars"""

    return str(text).replace("<", "&lt;").replace(">", "&gt;")


def clearProgramLogFile():
    """To clear the ProgramLogFile at the beginning of each run"""

    # "Mµßiggang ist auch ein ° von Läßterei"
    tag  = "{:23s} PROGRAM: pid:{:d} ########### {:s}  ".format(longstime(), os.getpid(), "GeigerLog {} -- mit no meh pfupf underm füdli !".format(gglobs.__version__))
    line = tag + "#" * 30

    if gglobs.redirect:
        # text with buffering=0 not possible in Python 3
        sys.stdout = open(gglobs.stdlogPath, 'w', buffering=1) # deletes content
        sys.stdout = open(gglobs.stdlogPath, 'a', buffering=1) # set for append
        sys.stderr = open(gglobs.stdlogPath, 'a', buffering=1) # direct err to same file

    gdprint(line)
    writeFileW(gglobs.proglogPath, line )   # goes to *.proglog (and *.stdlog)


def readBinaryFile(path):
    """Read all of the file into data; return data as bytes"""

    fncname = "readBinaryFile: "
    #print(fncname + "path: {} ".format(path))

    data = b''

    try:
        with open(path, 'rb') as f:
            data = f.read()

    except Exception as e:
        srcinfo = "ERROR reading file"
        exceptPrint(fncname + str(e), srcinfo)
        data = b"ERROR: Could not read file: " + str.encode(path)

    vprint(fncname + "len:{}, data[:30]: ".format(len(data)), data[0:30])

    return data


def writeBinaryFile(path, data):
    """Create file and write data to it as binary"""

    #print("writeBinaryFile: path: {}  data: not shown".format(path))

    with open(path, 'wb') as f:
        f.write(data)


def writeFileW(path, writestring, linefeed=True):
    """Create file if not available, and write to it if writestring
    is not empty; add linefeed unless excluded"""

    #print("writeFileW: path: {}  writestring: {}  linefeed: {}".format(path, writestring, linefeed))

    with open(path, 'wt', encoding="UTF-8", errors='replace', buffering = 1) as f:
        if writestring > "":
            if linefeed: writestring += "\n"
            f.write(writestring)


def writeFileA(path, writestring):
    """Write-Append data; add linefeed"""
    # duration is less than 0.2 ms even at 12MB file

    #print("writeFileA: path: {}  writestring: {}".format(path, writestring))
    # start = time.time()

    with open(path, 'at', encoding="UTF-8", errors='replace', buffering = 1) as f:
        f.write((writestring + "\n"))

    # duration = 1000 * (time.time() - start)
    # print(TRED + "writeFileA duration: {:0.3f} ms".format(duration), TDEFAULT)


def isFileReadable(filepath):
    """is filepath readable"""

    #print("isFileReadable: filepath: {}".format(filepath))

    if not os.access(filepath, os.R_OK) :
        efprint("File exists but cannot be read - check permission of file: {}".format(filepath))
        return False
    else:
        return True


def isFileWriteable(filepath):
    """As the dir can be written to, this makes only sense for existing files"""

    #print("isFileWriteable: filepath: {}".format(filepath))

    if os.path.isfile(filepath) and not os.access(filepath, os.W_OK) :
        efprint("File {}".format(filepath))
        qefprint("exists but cannot be written to - check permission of file")
        return False
    else:
        return True


def addMenuTip(var, text):
    """add menu tip and status tip; works only on PyQt5, not PyQt4"""

    # e.g.:   PlotLogAction.setStatusTip('Plot the Log file')
    #         PlotLogAction.setToolTip('Plot the Log file')
    #     --> addMenuTip(PlotLogAction, 'Plot the Log file')

    #print("addMenuTip:", var, text)
    var.setStatusTip(text)
    var.setToolTip(text)


def strFontInfo(origin, fi):
    """formats font information, returns string"""

    fontinfo = "Family:{}, fixed:{}, size:{}, style:{}, styleHint:{}, styleName:{}, weight:{}, exactMatch:{}"\
    .format(fi.family(), fi.fixedPitch(), fi.pointSize(), fi.style(), fi.styleHint(), fi.styleName(), fi.weight(), fi.exactMatch())

    return fontinfo


def printVarsStatus():
    """Print the current value of variables"""

    print(TDEFAULT) # reset to white color
    print( "\n============================================ Globals " + "-" * 100)
    g = globals()
    for name in g:
        if name[0] != "Q": # exclude Qt stuff
            print("name:     {:35s} =    {}".format(name, eval(name)))
    print(TDEFAULT) # reset to white color

    # gives only the locals in this printVarsStatus function
    #~print( "\n============================================= Locals " + "-" * 100)
    #~g = locals()
    #~for name in g:
        #~if name[0] != "Q":
            #~print("name:     {:35s} =    {}".format(name, eval(name)))
    #~print(TDEFAULT) # reset to white color


def html_escape(text):
    """Produce entities within text."""

    # when printing in error mode the < and > chars in the GMC commands may be
    # interpreted as HTML such that an b'<GETCPML>>' becomes an b'>' !

    html_escape_table = {
        "&": "&amp;",
        '"': "&quot;",
        "'": "&apos;",
        ">": "&gt;",
        "<": "&lt;",
        }

    return "".join(html_escape_table.get(c, c) for c in text)


def getOrderedVars(varlist):
    """Prints a dict in the right order"""

    ret = ""
    for vname in gglobs.varsCopy:
        ret += "{:>8s}:{:5s}".format(vname, str(varlist[vname])).strip() + "  "

    return ret


def getNameSelectedVar():
    """Get the name of the variable currently selected in the drop-down box in
    the graph options"""

    vindex      = gglobs.exgg.select.currentIndex()
    vnameselect = list(gglobs.varsCopy)[vindex]
    #print("getNameSelectedVar: vindex, vnameselect:", vindex, vnameselect)

    return vnameselect


def beep():
    """do a system beep"""
    # Nope, no sound output on my system???
    # https://askubuntu.com/questions/19906/beep-in-shell-script-not-working
    #print("beep by print\7")

    QApplication.beep()
    QApplication.processEvents()


def playWav(wtype = "ok"):
    """Play a wav message, either 'ok' or 'err' """

    fncname = "playWav: "

    if    wtype.lower() == "ok": path = os.path.join(gglobs.gresPath, 'bip2.wav') # wtype = "ok"
    else:                        path = os.path.join(gglobs.gresPath, 'burp.wav') # wtype = "err" or anything else

    # Play
    try:
        data, samplerate = sf.read(path)
        #print("samplerate: ", samplerate)
        sd.play(data, samplerate, latency='low')
        status = sd.wait() # may result in scraches when missing!
    except Exception as e:
        exceptPrint(e, "playWav failed")


def playSine():
    """testing play sine wave"""

    # play sine wave
    samplerate = 44100          # samples per sec
    sounddur   = 0.3            # seconds
    soundfreq  = 27.5           # Kammerton A abgeleitet (27.5 *sqrt(256) = 440)
    soundamp   = 1              # amplitude; mit steigender Amplitude Verzerrungen

    # create the time base
    t = (np.arange(samplerate * sounddur)) / samplerate
    #~print("t: ", t)

    # create the data
    for i in list(range(0, 15)) + list(range(15, -1, -1)):
        freq = soundfreq * (np.sqrt(2) **i)
        print("Freq: {:9.4f}".format(freq))
        outdata = soundamp * np.sin(2 * np.pi * freq * t)   # Tonleiter
        #~print("outdata raw: ", outdata)
        sd.play(outdata, samplerate * 2, latency='low')
        status = sd.wait()
        time.sleep(0.1)


def click():
    """play a long click"""

    # play sine wave
    samplerate = 44100              # samples per sec
    sounddur   = 0.1                # seconds
    soundfreq  = 1000 #1440         # 440Hz = Kammerton A
    soundamp   = 0.1                # amplitude; mit steigender Amplitude Verzerrungen 1.0 may be max?

    # create the time base
    t = (np.arange(samplerate * sounddur)) / samplerate
    #print("t: len:", len(t))

    # create the data
    outdata = soundamp * (np.sin(2 * np.pi * soundfreq * t))
    sd.play(outdata, samplerate, latency=0.05)
    # status = sd.wait() # if called then block until completion


def playClick():
    """play a Geiger counter like click sound"""

    # play sine wave
    samplerate = 44100              # samples per sec
    # sounddur   = 0.02               # seconds
    sounddur   = 0.04               # seconds
    soundfreq  = 440 #1000 #1440         # 440Hz = Kammerton A
    soundamp   = 0.1                # amplitude; mit steigender Amplitude Verzerrungen 1.0 may be max?

    # create the time base
    t = (np.arange(samplerate * sounddur)) / samplerate
    #print("t: len:", len(t))

    # create the data
    outdata = soundamp * (np.sin(2 * np.pi * soundfreq * t))
    #~print("outdata raw: ", outdata)
    #~print("outdata max: ", np.max(outdata))
    #~print("outdata min: ", np.min(outdata))
    sd.play(outdata, samplerate, latency=0.05)
    #status = sd.wait() # if called then block until completion


def playCounter():
    """play Geiger counter with increasing mean count rate"""

    duration = 5
    for mean in [0.3, 1, 3, 10, 30, 100, 300, 1000]:
        print("mean: ", mean)
        counts   = 0
        ttot     = 0
        start    = time.time()
        while time.time() < (start + duration):
            t = np.random.exponential(1 / mean)
            #print("mean= {:0.0f}, t= {:0.3f} ttot= {:0.3f}  counts= {:0.0f}".format(mean, t, ttot, counts))
            time.sleep(t )
            playClick()
            ttot += t
            counts += 1

    print("finished")


def scaleVarValues(variable, value, scale):
    """
    Apply the 'Scaling' declared in configuration file geigerlog.cfg. Can be
    used both for value scaling as for graph scaling.
    Return: the scaled value (or original in case of error)
    NOTE:   scale is in upper-case, but may be empty or NONE
    """

    fncname = "scaleVarValues: "
    #print(fncname + "scaling variable:'{}' value:'{}', scale: {}".format(variable, value, scale))

    scale = scale.strip().upper()             # make sure it is upper

    if scale == "VAL" or scale == "" or scale == "NONE": return value

    # example: scale: LOG(VAL)+1000           # orig
    # becomes: ls   : np.log(value)+1000      # mod
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
    ls = ls.replace("INT",    "np.int")       # integer value
    # ls = ls.replace("PADEC",  "PADEC")        # Paralyzing Dead Time Correction
    # ls = ls.replace("NOPADEC","NOPADEC")      # Non-Paralyzing Dead Time Correction

    try:
        scaledValue = eval(ls)

    except Exception as e:
        msg  = "ERROR scaling Values: variable:'{}'\n".format(variable)
        msg += "ERROR scaling Values: formula: '{}'\n".format(scale)
        msg += "ERROR scaling Values: errmsg:  '{}'\n".format(e)
        msg += "Continuing with original value\n"
        exceptPrint(e, msg)
        efprint(msg)
        scaledValue = value

    # print(fncname + "variable:'{}', orig scale:'{}', mod scale:'{}', value:{}, v-scaled:{}".format(variable, scale, ls, value, scaledValue))

    return scaledValue


def DeadTimeBalance(N, *args):
    """
    The difference between M (observed counts) and formula for Calculation of M from N (True counts)
    -> CPM_obs = CPM_true * exp(- CPM_true * deadtime)
    """

    M       = args[0]
    tau     = args[1]

    # balance = np.log(M) - (np.log(N) - N * tau)       # based on the log version of the equation
    balance = M - (N * np.exp(-N * tau))                # based on the exp
    # print("M:{}, tau:{}, N:{:0.0f} balance:{:0.6f}".format(M, tau, N, balance))

    return balance


def NOPADEC(cps, deadtime):
    """
    Non-Paralyzing Deadtime correction (analytical solution)
    in GeigerLog notation: # localValueScale = "VAL / (1 - VAL * {})".format(dt)
    cps:        cps_observed,
    deadtime:   deadtime of tube in microsecond
    Formula:    CPS_true = CPS_obs / (1 - CPS_obs * deadtime[s])
    """

    fncname = "nopadec: "

    tau = deadtime / 1E6    # we need deadtime in second
    N   = cps / (1 - cps * tau)

    # print(fncname + "cps:{}, deadtime:{} retval:{:0.3f}".format(cps, deadtime, N))

    return N


def PADEC(cps, deadtime):
    """
    Paralyzing Deadtime correction (iterative solution)
    cps:        cps_observed,
    deadtime:   deadtime of tube in microsecond
    Formula:    CPS_obs = CPS_true * exp(- CPS_true * deadtime)
    """

    fncname = "PADEC: "

    tau    = deadtime / 1E6    # we need deadtime in second

    try:
        lower_bracket = 0
        upper_bracket = 1 / tau     # the count rate limit is 1/tau; (e.g. at 125µs max CPS=8000)
        res = scipy.optimize.root_scalar(DeadTimeBalance, args=(cps, tau), x0=cps, x1=cps*2, xtol=0.1, method='bisect', bracket=[lower_bracket, upper_bracket] )
        # print(fncname + "vars(res):{}, Ratio N/M:{:0.2f}".format(vars(res), res.root/cps))
        if res.converged:   retval = res.root
        else:               retval = gglobs.NAN

    except Exception as e:
        msg = fncname + "Iteration failure with: cps:{}, deadtime:{}".format(cps, deadtime)
        efprint("Deadtime Correction with " + msg)
        exceptPrint(e, msg)
        retval = gglobs.NAN

    # print(fncname + "cps:{}, deadtime:{} retval:{:0.3f} Ratio retval/cps:{:0.2f}".format(cps, deadtime, retval, retval/cps))

    return retval


class ClickLabel(QLabel):
    """making a label click-sensitive"""

    def __init__(self, parent):
        QLabel.__init__(self, parent)

    def mousePressEvent(self, event):
        colorPicker()


def colorPicker():
    """Changes color of the selected variable.
    Called by the color picker button in the graph options. """

    if gglobs.currentConn == None: return # no color change unless something is loaded

    colorDial   = QColorDialog()
    color       = colorDial.getColor()
    if color.isValid():
        vprint("colorPicker: new color picked:", color.name())
        gglobs.exgg.btnColor.setStyleSheet("QLabel { border: 1px solid silver;  border-radius: 3px; background-color: %s ; }" % color.name())
        addMenuTip(gglobs.exgg.btnColor, gglobs.exgg.btnColorText + str(color.name()))
        gglobs.exgg.btnColor.setText("")

        vname = getNameSelectedVar()
        gglobs.varsCopy[vname][3] = color.name()
        gglobs.exgg.applyGraphOptions()

    gglobs.exgg.notePad.setFocus()


def printProgError(*args):
    print("PROGRAMMING ERROR !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
    dprint(*args, debug=True)
    setNormalCursor()
    sys.exit(-1)


def Qt_update():
    """updates the Qt window"""

    QApplication.processEvents()


def executeTPUT(action = 'allow_line_wrapping'):
    """
    set terminal output with or without linebreaks; works in Linux only
    use action = 'allow_line_wrapping' or 'no_line_wrapping'
    """
    # For generic non full screen applications, you can turn off line wrapping by
    # sending an appropriate escape sequence to the terminal:
    #   tput rmam
    # This mode can be cancelled with a similar escape:
    #   tput smam
    # also: https://tomayko.com/blog/2004/StupidShellTricks

    if not "LINUX" in platform.platform().upper(): return

    if action == 'allow_line_wrapping' or gglobs.forcelw:
        tputcommand = "rmam"                # tput rmam: no line break on lines longer than screen
        tputmsg     = "(line wrapping turned OFF)"

    else:   # 'no_line_wrapping'
        tputcommand = "smam"                # tput smam: do line break on lines longer than screen
        tputmsg     = "(line wrapping turned ON)"

    try:
        # raise Exception("tput command")
        subprocess.call(["tput", tputcommand])
        dprint("{:28s}: {}".format("LineWrapping (Linux)", "SUCCESS executing tput {} - {}".format(tputcommand, tputmsg)))
    except Exception as e:
        msg = ""
        exceptPrint(e, msg)
        edprint("{:28s}: {}".format("LineWrapping (Linux)", "FAILURE executing tput {} - {}".format(tputcommand, tputmsg)), debug=True)


def openManual():
    """Show the GeigerLog Manual, first try a local version, but if not
    present, then try the version on SourceForge"""

    fncname = "openManual: "
    manual_file = None

    if gglobs.manual_filename != 'auto':
        # if filename is defined in config file, use that name. File does exist,
        # because if not, gglobs.manual_filename would have been
        # overwritten with 'auto' when reading the config
        manual_file = getProgPath() + "/" + gglobs.manual_filename
    else:
        # if NOT defined in config file, use first found file which begins
        # with 'GeigerLog-Manual'
        path = getProgPath() + "/"
        for filename in os.listdir(path):
            #print("filename: ", filename)
            if re.match("GeigerLog-Manual", filename):
                #print "filename", filename
                manual_file = getProgPath() + "/" + filename
                break                   # manual found, exit for loop

    if manual_file == None:
        efprint ("The file 'GeigerLog-Manual-xyz', with xyz being a version number, is missing")
        qefprint("from the GeigerLog working directory 'geigerlog'.")
        fprint  ("Now trying to find the file online.")
    else:
        dprint("Using Manual_file: ", manual_file)

    if manual_file != None:
        try:
            if sys.platform.startswith('linux'):
                # xdg-open command in the Linux system is used to open a file
                # or URL in the user’s preferred application.
                subprocess.call(["xdg-open", manual_file])
                dprint("Showing '{}' via xdg-open on Linux".format(manual_file))
            else:
                os.startfile(manual_file)
                dprint("Showing '{}' via os.startfile on other OS".format(manual_file))

            return

        except Exception as e:
            msg = "Failure Showing '{}' via xdg-open on Linux or via os.startfile on other OS".format(manual_file)
            #print(sys.exc_info())
            exceptPrint(fncname + str(e), msg)
            dprint(msg)

        try:
            if sys.platform.startswith('linux'):
                subprocess.call(["firefox", manual_file])
                dprint("Showing '{}' via firefox on Linux".format(manual_file))
            else:
                os.startfile(manual_file)
                dprint("Showing '{}' via os.startfile on other OS".format(manual_file))

            return

        except Exception as e:
            msg = "Failure Showing '{}' via firefox on Linux or via os.startfile on other OS".format(manual_file)
            #print(sys.exc_info())
            exceptPrint(fncname + str(e), msg)
            dprint(msg)

        try:
            import webbrowser
            webbrowser.open(manual_file)
            dprint("Showing '{}' via import webbrowser".format(manual_file))

            return

        except Exception as e:
            msg = "Failure Showing '{}' via import webbrowser".format(manual_file)
            #print(sys.exc_info())
            exceptPrint(fncname + str(e), msg)
            dprint(msg)


    try:
        shortv = gglobs.__version__.split("pre")[0]   # use only the version part before 'pre'
        #shortv: "1.0.1pre9" --> "1.0.1"
        print("shortv: ", shortv)

        url = QUrl('https://sourceforge.net/projects/geigerlog/files/GeigerLog-Manual-v{}.pdf'.format(shortv))
        if QDesktopServices.openUrl(url):
            dprint("Showing QUrl '{}'".format(url))
        else:
            QMessageBox.warning(gglobs.exgg, 'GeigerLog Manual', 'Could not open GeigerLog Manual')
            dprint("Failure Showing manual with QUrl '{}'".format(url))
        return
    except Exception as e:
        msg = "Failure Showing manual with QUrl"
        exceptPrint("openManual: " + str(e), msg)

    efprint("Could not find GeigerLog-Manual, neither locally nor online!")


def showSystemInfo():
    """System Info on the Devel Menu"""

    screen           = QDesktopWidget().screenGeometry()
    screen_available = QDesktopWidget().availableGeometry()
    geom             = gglobs.exgg.geometry()
    geom_frame       = gglobs.exgg.frameGeometry()

    fmt              = "{:35s}{}\n"
    si               = ""

    # user
    si += fmt.format("Username:",                        "{}".format(os.environ.get('USER')))

    # platform
    si += fmt.format("\nPlatform:",                      "")
    si += fmt.format("  Operating System:",              "{}".format(platform.platform()))
    si += fmt.format("  Machine:",                       "{}, {}".format(platform.machine(), platform.architecture()[0]))
    si += fmt.format("  Byte Order:",                    "{}".format(sys.byteorder))

    # versions
    si += fmt.format("\nVersion status:",                "")
    for ver in gglobs.versions:
        si += fmt.format( "  " + ver,                    gglobs.versions[ver])

    # runtime
    si += fmt.format("\nRuntime settings:",              "")
    si += fmt.format("  Flag DEBUG:",                    str(gglobs.debug))
    si += fmt.format("  Flag VERBOSE:",                  str(gglobs.verbose))
    si += fmt.format("  Flag werbose:",                  str(gglobs.werbose))
    si += fmt.format("  Flag KeepFF:",                   str(gglobs.keepFF))
    si += fmt.format("  Flag Redirect:",                 str(gglobs.redirect))
    si += fmt.format("  Flag Devel:",                    str(gglobs.devel))
    si += fmt.format("  Flag Devel1:",                   str(gglobs.devel1))
    si += fmt.format("  Flag Devel2:",                   str(gglobs.devel2))
    si += fmt.format("  Flag Testing:",                  str(gglobs.testing))
    si += fmt.format("  Flag GSTesting:",                str(gglobs.GStesting))
    si += fmt.format("  Flag ForceLineWrapping:",        str(gglobs.forcelw))
    si += fmt.format("  GeigerLog Program Directory:",   str(getProgPath()))
    si += fmt.format("  GeigerLog Data Directory:",      str(gglobs.dataPath))
    si += fmt.format("  GeigerLog Resource Directory:",  str(gglobs.gresPath))
    si += fmt.format("  GeigerLog Manual:",              str(gglobs.manual_filename))

    # GUI
    si += fmt.format("\nGUI:",                           "")
    si += fmt.format("  Monitor:",                       "")
    si += fmt.format("   Screen size - Hardware:",       "{}x{}".format(screen.width(), screen.height()))
    si += fmt.format("   Screen size - Available:",      "{}x{}, at position: x={}, y={}".format(screen_available.width(), screen_available.height(), screen_available.x(), screen_available.y()))
    si += fmt.format("   Current window size:",          "{}x{} including window frame (w/o frame: {}x{})".format(geom_frame.width(), geom_frame.height(), geom.width(), geom.height()))
    si += fmt.format("  Styles:",                        "")
    si += fmt.format("   Styles available on System:",   QStyleFactory.keys())
    si += fmt.format("   Active Style (internal name):", str(gglobs.app.style().metaObject().className()))
    si += fmt.format("  Fonts:",                         "")
    si += fmt.format("   Active Font - Application:",    strFontInfo("", gglobs.app.font()))
    si += fmt.format("   Active Font - Menubar:",        strFontInfo("", gglobs.exgg.menubar.fontInfo()))
    si += fmt.format("   Active Font - NotePad:",        strFontInfo("", gglobs.exgg.notePad.fontInfo()))
    si += fmt.format("   Active Font - LogPad:",         strFontInfo("", gglobs.exgg.logPad.fontInfo()))

    # Devices
    si += "\n"
    si += fmt.format("Devices:",                         "Model connected:")
    for dname in gglobs.Devices:
        si += fmt.format("   " + dname,                  gglobs.Devices[dname][DNAME])

    # Serial Ports
    si += fmt.format("\nUSB-to-Serial Port Settings:",   "")

    # GMC USB port
    si += fmt.format("  GMC Serial (USB) Port Settings:",  "")
    si += fmt.format("   Port:",                          str(gglobs.GMC_usbport))
    si += fmt.format("   Baudrate:",                      str(gglobs.GMC_baudrate))
    si += fmt.format("   Timeout: (Read)",                str(gglobs.GMC_timeout))
    si += fmt.format("   Timeout: (Write)",               str(gglobs.GMC_timeout_write))
    si += fmt.format("   ttyS:",                          str(gglobs.GMC_ttyS))

    # I2C USB port
    si += fmt.format("  I2C Serial (USB) Port Settings:",  "")
    si += fmt.format("   Port:",                          str(gglobs.I2Cusbport))
    si += fmt.format("   Baudrate:",                      "{:,}".format(int(gglobs.I2Cbaudrate)))
    si += fmt.format("   Timeout: (Read)",                str(gglobs.I2Ctimeout))
    si += fmt.format("   Timeout: (Write)",               str(gglobs.I2Ctimeout_write))
    si += fmt.format("   ttyS:",                          str(gglobs.I2CttyS))

    # GS USB port
    si += fmt.format("  GS Serial (USB) Port Settings:",  "")
    si += fmt.format("   Port:",                          str(gglobs.GSusbport))
    si += fmt.format("   Baudrate:",                      "{:,}".format(int(gglobs.GSbaudrate)))
    si += fmt.format("   Timeout: (Read)",                str(gglobs.GStimeout))
    si += fmt.format("   Timeout: (Write)",               str(gglobs.GStimeout_write))
    si += fmt.format("   ttyS:",                          str(gglobs.GSttyS))

    # worldmaps
    si += fmt.format("\nWorldmaps Settings:", "")
    si += fmt.format("  SSID",                            gglobs.WiFiSSID)
    si += fmt.format("  Password",                        gglobs.WiFiPassword)
    si += fmt.format("  Website",                         gglobs.gmcmapWebsite)
    si += fmt.format("  URL",                             gglobs.gmcmapURL)
    si += fmt.format("  UserID",                          gglobs.gmcmapUserID)
    si += fmt.format("  CounterID",                       gglobs.gmcmapCounterID)
    si += fmt.format("  Period",                          gglobs.gmcmapPeriod)
    si += fmt.format("  WiFi",                            "unknown")

    lsysinfo = QTextBrowser()                              # to hold the text; allows copy
    lsysinfo.setLineWrapMode(QTextEdit.WidgetWidth)
    lsysinfo.setText(si)

    dlg = QDialog()
    dlg.setWindowIcon(gglobs.iconGeigerLog)
    dlg.setWindowTitle("Help - System Info")
    dlg.setFont(gglobs.fontstd)
    dlg.setWindowModality(Qt.WindowModal)
    dlg.setMinimumWidth(1200)
    dlg.setMinimumHeight(690)

    bbox = QDialogButtonBox()
    bbox.setStandardButtons(QDialogButtonBox.Ok)
    bbox.accepted.connect(lambda: dlg.done(100))

    layoutV = QVBoxLayout(dlg)
    layoutV.addWidget(lsysinfo)
    layoutV.addWidget(bbox)

    dlg.exec()


def setNormalCursor():

    gglobs.exgg.setNormalCursor()


def setBusyCursor():

    gglobs.exgg.setBusyCursor()


def showStatusMessage(msg):

    gglobs.exgg.showStatusMessage(msg)


def cleanupDevices(ctype):
    """ctype is 'before' or 'after'; so far same action and only for GMC's getGMC_ExtraByte()"""

    if gglobs.Devices["GMC"][CONN] :
        from gdev_gmc import getGMC_ExtraByte
        dprint("cleanupDevices: '{}': Cleaning pipeline {} logging".format(gglobs.GMCDeviceDetected, ctype))
        if   ctype == "before":
            getGMC_ExtraByte()

        elif ctype == "after":
            getGMC_ExtraByte()

        else:
            #whatever; just as placeholder
            getGMC_ExtraByte()
    else:
        # so far no other device needs cleaning
        pass


def setLoggableVariables(device, DeviceVariables):
    """set the loggable variables"""

    fncname = "setLoggableVariables: "
    if DeviceVariables == None: return

    DevVars = DeviceVariables.split(",")
    for i in range(0, len(DevVars)):
        DevVars[i] = DevVars[i].strip()     # remove any white space for all variables
    gglobs.Devices[device][VNAME] = DevVars
    wprint(fncname + "Device: ", device, ", Variables:", gglobs.Devices[device][VNAME])


def setTubeSensitivities(DeviceVariables, DeviceSensitivity):
    """set the sensitivity for the of the device's tube according to the defined variables"""

    fncname = "setTubeSensitivities: "

    if DeviceVariables == None: return  # could be None if user enters wrong values

    devvar = DeviceVariables.split(",")
    for a in devvar:
        a = a.strip()
        if   a == "CPM"    or a == "CPS" :      gglobs.Sensitivity[0] = DeviceSensitivity
        elif a == "CPM1st" or a == "CPS1st":    gglobs.Sensitivity[1] = DeviceSensitivity
        elif a == "CPM2nd" or a == "CPS2nd":    gglobs.Sensitivity[2] = DeviceSensitivity
        elif a == "CPM3rd" or a == "CPS3rd":    gglobs.Sensitivity[3] = DeviceSensitivity

    # cdprint(fncname + "DeviceVariables: ", DeviceVariables)
    # cdprint(fncname + "Def:",   gglobs.Sensitivity[0])
    # cdprint(fncname + "1st:",   gglobs.Sensitivity[1])
    # cdprint(fncname + "2nd:",   gglobs.Sensitivity[2])
    # cdprint(fncname + "3rd:",   gglobs.Sensitivity[3])


def getLoggedValuesHeader():
    """print header for logged values"""

    # print like:
    # Variables:       Dur[ms] CPM       CPS       CPM1st    CPS1st    CPM2nd    CPS2nd    CPM3rd    CPS3rd    T         P         H         X

    text  = "{:<25s}" .format("Variables: ")
    text += "{:<10s} ".format(" Dur[ms]")
    for a in gglobs.varsCopy:
        text += "{:<10s}".format(a)

    return text


def printLoggedValues(rfncname, varlist, alldata, duration=None, forceprint=False):
    """print formatted logged values"""

    # print like:
    # getValuesGMC:           176.00    4.00      176.00    4.00      0.00      0.00      -         -         -         -         -         -
    # getValuesAudio:          -         -         -         -         -         -         0.00      0.00      -         -         -         -

    #~print("printLoggedValues: alldata: ", alldata)
    text = "{:<21s}".format(rfncname)
    if duration is not None: text += "{:8.2f}       ".format(duration)
    else:                    text += "{:<10s} ".format(" --- ")

    for a in gglobs.varsCopy:
        if   a in alldata: newtext = "{:<10.3f}".format(alldata[a])
        else:              newtext = "{:<10s}"  .format("-")
        text += newtext
    vprint(text, forceverbose=forceprint)


def getDeltaTimeMessage(deltatime, deviceDateTime):
    """determines difference between times of computer and device and gives message"""

    def wrapHTML(text):
        return "<html><span style='color:red;'>" + text + "</span>"

    dtxt = ""
    if   np.isnan(deltatime):    dtxt += "Device clock cannot be read"                                           # clock defect?
    elif abs(deltatime) <= 1:    dtxt += "Device clock is same as computer clock within 1 sec"                   # uncertainty 1 sec
    elif deltatime >= +1:        dtxt += "Device is slower than computer by {:0.1f} sec".format(deltatime)       # delta positiv
    elif deltatime <= -1:        dtxt += "Device is faster than computer by {:0.1f} sec".format(abs(deltatime))  # delta negativ

    dtfd  = "{:30s}".format("Date & Time from Device:")
    dtfg  = "{:30s}".format("Date & Time from GeigerLog:")
    DTM   = ""
    if   np.isnan(deltatime):
            # efprint(dtfd, dtxt)
            DTM += dtfd + dtxt + "\n"

    elif abs(deltatime) > 5:
            # efprint( dtfd, deviceDateTime)
            # qefprint(dtfg, longstime())
            # qefprint("", dtxt)
            DTM += dtfd + str(deviceDateTime) + "\n"
            DTM += dtfg + str(longstime()) + "\n"
            DTM += " "*30 + dtxt + "\n"

    else:
            # fprint(dtfd, deviceDateTime)
            # fprint("", dtxt)
            DTM += dtfd + str(deviceDateTime) + "\n"
            DTM += " "*30 + dtxt + "\n"

    return DTM

###############################################################################


def getConfigEntry(section, parameter, ptype):
    """utility for readGeigerLogConfig"""

    # print("getConfigEntry: ", section, ", ", parameter, ", ", ptype, end="  ")
    try:
        t = config.get(section, parameter)
        #print(", t: ", t)

        t = t.strip()
        if   ptype == "float":    t = float(t)
        elif ptype == "int":      t = int(float(t))
        elif ptype == "str":      t = t
        elif ptype == "upper":    t = t.upper()

        return t

    except ValueError: # e.g. failure to convert to float
        errmesg = "Section: {}, Parameter: {}\nProblem: has wrong value: {}".format(section, parameter, t)
        gglobs.configAlerts += errmesg + "\n\n"
        edprint("WARNING: " + errmesg, debug=True)

        return "WARNING"

    except Exception as e:
        errmesg = "Section: {}, Parameter: {}\nProblem: {}".format(section, parameter, e)
        gglobs.configAlerts += errmesg + "\n\n"
        edprint("WARNING: " + errmesg, debug=True)

        return "WARNING"


#
# Configuration file evaluation
#
def readGeigerLogConfig():
    """reading the configuration file, return if not available.
    Not-available or illegal options are being ignored with only a debug message"""

    global config # make config available to getConfigEntry()

    fncname = "readGeigerLogConfig: "

    dprint(fncname + "using config file: ", gglobs.configPath)
    setDebugIndent(1)

    infostrHeader = "cfg: {:35s} {}"
    infostr       = "cfg:     {:35s}: {}"
    while True:

    # does the config file exist and can it be read?
        if not os.path.isfile(gglobs.configPath) or not os.access(gglobs.configPath, os.R_OK) :
            msg = """Configuration file <b>'geigerlog.cfg'</b> does not exist or is not readable."""
            edprint(msg, debug=True)
            msg += "\n\nPlease check and correct. Cannot continue, will exit."
            gglobs.startupProblems = msg
            break

    # is it error free?
        try:
            config = configparser.ConfigParser()
            with open(gglobs.configPath) as f:
               config.read_file(f)
        except Exception as e:
            msg = "Configuration file <b>'geigerlog.cfg'</b> cannot be interpreted."
            exceptPrint(e, msg)
            msg += "\n\nNote that duplicate entries are not allowed!"
            msg += "\n\nERROR Message:\n" + str(sys.exc_info()[1])
            msg += "\n\nPlease check and correct. Cannot continue, will exit."
            gglobs.startupProblems = msg.replace("\n", "<br>")
            break

    # the config file exists and can be read:
        dprint(infostrHeader.format("Startup values", ""))

    # Logging
        t = getConfigEntry("Logging", "logCycle", "upper" )
        gglobs.logCycle = 3
        if t != "WARNING":
            if t == "AUTO":                     gglobs.logCycle = 3
            else:
                try:    ft = float(t)
                except: ft = 3
                if      ft >= 0.1:              gglobs.logCycle = ft
                else:                           gglobs.logCycle = 3
        dprint(infostr.format("Logcycle (sec)", gglobs.logCycle))

    # Folder data
        t = getConfigEntry("Folder", "data", "str" )
        if t != "WARNING":
            errmsg = "WARNING: "
            try:
                if t.upper() == "AUTO":
                    pass                        # no change to default = 'data'
                else:
                    if os.path.isabs(t):        # is it absolute path?
                        testpath = t            # yes
                        #print("absolute path:", testpath)

                    else:                       # it is relative path
                        testpath = gglobs.dataPath + "/" + t
                        #print("relative path:", testpath)

                    # Make sure the data directory exists; create it if needed
                    # ignore if it cannot be made or is not writable
                    #
                    if os.access(testpath , os.F_OK):
                        # dir exists, ok
                        if not os.access(testpath , os.W_OK):
                            # dir exists, but is not writable
                            errmsg += "Configured data directory '{}' exists, but is not writable".format(testpath)
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
                            errmsg += "Could not make configured data directory '{}'".format(testpath)
                            raise NameError

                dprint(infostr.format("Data directory", gglobs.dataPath))
            except Exception as e:
                dprint(errmsg, "; Exception:", e, debug=True)

    # Manual
        t = getConfigEntry("Manual", "ManualName", "str" )
        if t != "WARNING":
            if t.upper() == 'AUTO' or t == "":
                gglobs.manual_filename = 'auto'
                dprint(infostr.format("Manual file", gglobs.manual_filename))
            else:
                manual_file = getProgPath() + "/" + t
                if os.path.isfile(manual_file):     # does the file exist?
                    # it exists
                    gglobs.manual_filename = t
                    dprint(infostr.format("Manual file", gglobs.manual_filename))
                else:
                    # it does not exist
                    gglobs.manual_filename = 'auto'
                    dprint("WARNING: Manual file '{}' does not exist".format(t))


    # Monitor Server
        dprint(infostrHeader.format("Monitor Server", ""))

        # MonServer Autostart
        t = getConfigEntry("MonServer", "MonServerAutostart", "upper" )
        if t != "WARNING":
            if     t == "NO":                              gglobs.MonServerAutostart = False
            else:                                          gglobs.MonServerAutostart = True
            dprint(infostr.format("MonServerAutostart",    gglobs.MonServerAutostart))

        # MonServer Port
        t = getConfigEntry("MonServer", "MonServerPort", "upper" )
        if t != "WARNING":
            if t == "AUTO":                                gglobs.MonServerPort = 8008
            else:
                wp = int(float(t))
                if 1024 <= wp  <= 65535:                   gglobs.MonServerPort = wp
                else:                                      gglobs.MonServerPort = 8008
            dprint(infostr.format("MonServer Port",        gglobs.MonServerPort))

        # MonServer Refresh
        t = getConfigEntry("MonServer", "MonServerRefresh", "upper" )
        if t != "WARNING":
            if t == "AUTO":                                gglobs.MonServerRefresh = "auto"
            else:
                ts = t.split(",")
                gglobs.MonServerRefresh = [1, 10, 3]
                try:
                    gglobs.MonServerRefresh[0] = int(ts[0])
                    gglobs.MonServerRefresh[1] = int(ts[1])
                    gglobs.MonServerRefresh[2] = int(ts[2])
                except Exception as e:
                    exceptPrint(e, "MonServer Refresh")
                    gglobs.MonServerRefresh = [1, 10, 3]
            dprint(infostr.format("MonServer Refresh",     gglobs.MonServerRefresh))



        # DoseRateThreshold (low, high)
        t = getConfigEntry("MonServer", "DefDoseRateThreshold", "str" )
        if t != "WARNING":
            default = False
            ts = t.split(",")
            if len(ts) == 2:
                try:
                    lo = float(ts[0])
                    hi = float(ts[1])
                    if lo > 0 and hi > lo:  gglobs.DoseRateThreshold = (lo, hi)
                    else:                   default = True
                except:
                    default = True
            else:
                default = True

            if default : gglobs.DoseRateThreshold = (0.9, 6.0)

            dprint(infostr.format("MonServer DoseRateThreshold",     gglobs.DoseRateThreshold))



    # Window
        dprint(infostrHeader.format("Window", ""))

    # Window HiDPIactivation
        t = getConfigEntry("Window", "HiDPIactivation", "upper" )
        if t != "WARNING":
            if    t == 'AUTO':         gglobs.hidpiActivation = "auto"
            elif  t == 'YES':          gglobs.hidpiActivation = "yes"
            elif  t == 'NO':           gglobs.hidpiActivation = "no"
            else:                      gglobs.hidpiActivation = "auto"
            dprint(infostr.format("Window HiDPIactivation", gglobs.hidpiActivation))

    # Window HiDPIscaleMPL
        t = getConfigEntry("Window", "HiDPIscaleMPL", "upper" )
        if t != "WARNING":
            if    t == 'AUTO':         gglobs.hidpiScaleMPL = "auto"
            try:                       gglobs.hidpiScaleMPL = int(float(t))
            except:                    gglobs.hidpiScaleMPL = "auto"
            dprint(infostr.format("Window HiDPIscaleMPL", gglobs.hidpiScaleMPL))

    # Window dimensions
        w = getConfigEntry("Window", "windowWidth", "int" )
        h = getConfigEntry("Window", "windowHeight", "int" )
        if w != "WARNING" and h != "WARNING":
            if w > 500 and w < 5000 and h > 100 and h < 5000:
                gglobs.window_width  = w
                gglobs.window_height = h
                dprint(infostr.format("Window dimensions (pixel)", "{} x {}".format(gglobs.window_width, gglobs.window_height)))
            else:
                dprint("WARNING: Config Window dimension out-of-bound; ignored: {} x {} pixel".format(gglobs.window_width, gglobs.window_height), debug=True)

    # Window Size
        t = getConfigEntry("Window", "windowSize", "upper" )
        if t != "WARNING":
            if    t == 'MAXIMIZED':    gglobs.window_size = 'maximized'
            else:                      gglobs.window_size = 'auto'
            dprint(infostr.format("Window Size ", gglobs.window_size))

    # Window Style
        t = getConfigEntry("Window", "windowStyle", "str" )
        if t != "WARNING":
            available_style = QStyleFactory.keys()
            if t in available_style:    gglobs.windowStyle = t
            else:                       gglobs.windowStyle = "auto"
            dprint(infostr.format("Window Style ", gglobs.windowStyle))

    # WINDOW PAD COLORS cannot be used due to a bug in PyQt5
    # # from the geigerlog.cfg file:
    # # WINDOW PAD COLORS:
    # # Sets the background color of NotePad and LogPad. Default is a
    # # very light green for NotePad, and very light blue for LogPad.
    # # Colors can be given as names (red, green, lightblue,...) - not
    # # all names will work - or #<red><green><blue> with red, green, blue
    # # in HEX notation.
    # # Example: #FFFFFF is pure white, #FF0000 is pure red, #00FF00 is pure green,
    # # #CCCCFF is a blueish grey, and #000000 is pure black.
    # #
    # # Option auto defaults to: '#FaFFFa, #FaFaFF'
    # #
    # # Options:       auto | <color name, color name>
    # # Default      = auto
    # windowPadColor = auto
    # # windowPadColor = #FaFFFa, #e0e0FF
    #
    # # Window Pad Color
    #     t = getConfigEntry("Window", "windowPadColor", "str" )
    #     if t != "WARNING":
    #         if t.upper() == "AUTO":     gglobs.windowPadColor = ("#FaFFFa", "#FaFaFF")
    #         else:
    #             ts = t.split(",")
    #             Np = ts[0].strip()
    #             Lp = ts[1].strip()
    #             gglobs.windowPadColor      = (Np, Lp)
    #         dprint(infostr.format("Window Pad BG-Color ", gglobs.windowPadColor))


    # Graphic
        dprint(infostrHeader.format("Graphic", ""))

        # Graphic MovingAverage
        t = getConfigEntry("Graphic", "MovingAverage", "float" )
        if t != "WARNING":
            if   t >= 1:  gglobs.mav_initial = t
            else:         gglobs.mav_initial = 60
            gglobs.mav = gglobs.mav_initial
            dprint(infostr.format("Moving Average Initial (sec)", int(gglobs.mav_initial)))


    # Plotstyle
        dprint(infostrHeader.format("Plotstyle", ""))

        # linewidth
        t = getConfigEntry("Plotstyle", "linewidth", "str" )
        if t != "WARNING":
            try:    gglobs.linewidth           = float(t)
            except: gglobs.linewidth           = 1
        dprint(infostr.format("linewidth", gglobs.linewidth))

        # markersymbol
        t = getConfigEntry("Plotstyle", "markersymbol", "str" )
        if t != "WARNING":
            if t in "osp*h+xD" :              gglobs.markersymbol = t
            else:                             gglobs.markersymbol = 'o'
        dprint(infostr.format("markersymbol", gglobs.markersymbol))

        # markersize
        t = getConfigEntry("Plotstyle", "markersize", "str" )
        if t != "WARNING":
            try:                            gglobs.markersize = float(t)
            except:                         gglobs.markersize = 15
        dprint(infostr.format("markersize", gglobs.markersize))


    # Defaults
        dprint(infostrHeader.format("Defaults", ""))

        # sensitivity Def tube is 154 CPM/(µSv/h), =  0.0065 in units of µSv/h/CPM
        t = getConfigEntry("Defaults", "DefaultSensDef", "str" )
        if t != "WARNING":
            try:                                gglobs.DefaultSensDef = float(t)
            except:                             gglobs.DefaultSensDef = 154
        if gglobs.DefaultSensDef <= 0:          gglobs.DefaultSensDef = 154
        dprint(infostr.format("DefaultSensDef", gglobs.DefaultSensDef))

        # sensitivity 1st tube is 154 CPM/(µSv/h), =  0.0065 in units of µSv/h/CPM
        t = getConfigEntry("Defaults", "DefaultSens1st", "str" )
        if t != "WARNING":
            try:                                gglobs.DefaultSens1st = float(t)
            except:                             gglobs.DefaultSens1st = 154
        if gglobs.DefaultSens1st <= 0:          gglobs.DefaultSens1st = 154
        dprint(infostr.format("DefaultSens1st", gglobs.DefaultSens1st))

        # sensitivity 2nd tube is 2.08 CPM/(µSv/h), =  0.48 in units of µSv/h/CPM
        t = getConfigEntry("Defaults", "DefaultSens2nd", "str" )
        if t != "WARNING":
            try:                                gglobs.DefaultSens2nd = float(t)
            except:                             gglobs.DefaultSens2nd = 2.08
        if gglobs.DefaultSens2nd <= 0:          gglobs.DefaultSens2nd = 2.08
        dprint(infostr.format("DefaultSens2nd", gglobs.DefaultSens2nd))

        # sensitivity 3rd tube is 154 CPM/(µSv/h), =  0.0065 in units of µSv/h/CPM
        t = getConfigEntry("Defaults", "DefaultSens3rd", "str" )
        if t != "WARNING":
            try:                                gglobs.DefaultSens3rd = float(t)
            except:                             gglobs.DefaultSens3rd = 154
        if gglobs.DefaultSens3rd <= 0:          gglobs.DefaultSens3rd = 154
        dprint(infostr.format("DefaultSens3rd", gglobs.DefaultSens3rd))


    # Network
        dprint(infostrHeader.format("Network", ""))

        # WiFi SSID
        t = getConfigEntry("Network", "WiFiSSID", "str" )
        if t != "WARNING":  gglobs.WiFiSSID       = t
        dprint(infostr.format("WiFiSSID", gglobs.WiFiSSID))

        # WiFi Password
        t = getConfigEntry("Network", "WiFiPassword", "str" )
        if t != "WARNING":  gglobs.WiFiPassword       = t
        dprint(infostr.format("WiFiPassword", gglobs.WiFiPassword))


    # Radiation World Maps
        dprint(infostrHeader.format("Worldmaps", ""))

        t = getConfigEntry("Worldmaps", "gmcmapWebsite", "str" )
        if t != "WARNING":  gglobs.gmcmapWebsite    = t

        t = getConfigEntry("Worldmaps", "gmcmapURL", "str" )
        if t != "WARNING":  gglobs.gmcmapURL        = t

        t = getConfigEntry("Worldmaps", "gmcmapUserID", "str" )
        if t != "WARNING":  gglobs.gmcmapUserID     = t

        t = getConfigEntry("Worldmaps", "gmcmapCounterID", "str" )
        if t != "WARNING":  gglobs.gmcmapCounterID  = t

        t = getConfigEntry("Worldmaps", "gmcmapPeriod", "upper" )
        if t != "WARNING":
            if t == "AUTO":                             gglobs.gmcmapPeriod = "auto"
            else:
                try:
                    gglobs.gmcmapPeriod = int(float(t))
                    if gglobs.gmcmapPeriod < 0:         gglobs.gmcmapPeriod = "auto"
                except:                                 gglobs.gmcmapPeriod = "auto"

        t = getConfigEntry("Worldmaps", "gmcmapWiFiSwitch", "upper" )
        if t != "WARNING":
            if t == "ON":                               gglobs.gmcmapWiFiSwitch = True
            else:                                       gglobs.gmcmapWiFiSwitch = False
            # dprint(infostr.format("gmcmapWiFiSwitch",   "ON" if gglobs.gmcmapWiFiSwitch else "OFF"))

        if gglobs.Devices["GMC"][2]: # fill cfgKeyHigh only if GMC is activated
            from gdev_gmc import cfgKeyHigh
            # from gdev_gmc import cfgKeyHighDefault as cfgKeyHigh
            cfgKeyHigh["SSID"][0]       = str(gglobs.WiFiSSID)
            cfgKeyHigh["Password"][0]   = str(gglobs.WiFiPassword)
            cfgKeyHigh["Website"][0]    = str(gglobs.gmcmapWebsite)
            cfgKeyHigh["URL"][0]        = str(gglobs.gmcmapURL)
            cfgKeyHigh["UserID"][0]     = str(gglobs.gmcmapUserID)
            cfgKeyHigh["CounterID"][0]  = str(gglobs.gmcmapCounterID)
            cfgKeyHigh["Period"][0]     = str(gglobs.gmcmapPeriod)
            # cfgKeyHigh["WiFi"][0]       = "unknown"
            cfgKeyHigh["WiFi"][0]       = str(gglobs.gmcmapWiFiSwitch)

            #~for key in "SSID", "Password", "Website", "URL", "UserID", "CounterID", "Period", "WiFi":
                #~dprint(infostr.format(key, cfgKeyHigh[key][0]))

        # dprint(infostr.format("SSID",       gglobs.WiFiSSID))
        # dprint(infostr.format("Password",   gglobs.WiFiPassword))
        dprint(infostr.format("Website",    gglobs.gmcmapWebsite))
        dprint(infostr.format("URL",        gglobs.gmcmapURL))
        dprint(infostr.format("UserID",     gglobs.gmcmapUserID))
        dprint(infostr.format("CounterID",  gglobs.gmcmapCounterID))
        dprint(infostr.format("Period",     gglobs.gmcmapPeriod))
        dprint(infostr.format("WiFi",       "ON" if gglobs.gmcmapWiFiSwitch else "OFF"))



    #
    # ValueScaling - it DOES modify the variable value!
    #
    # infostr = "INFO: {:35s}: {}"
        dprint(infostrHeader.format("ValueScaling", ""))
        for vname in gglobs.varsCopy:
            t = getConfigEntry("ValueScaling", vname, "upper" )
            if t != "WARNING":
                if t == "":     pass                    # use value from gglobs
                else:           gglobs.ValueScale[vname] = t
                dprint(infostr.format("ValueScale['{}']".format(vname), gglobs.ValueScale[vname]))


    #
    # GraphScaling - it does NOT modify the variable value, only the plot value
    #
    # infostr = "INFO: {:35s}: {}"
        dprint(infostrHeader.format("GraphScaling", ""))
        for vname in gglobs.varsCopy:
            t = getConfigEntry("GraphScaling", vname, "upper" )
            if t != "WARNING":
                if t == "":     pass                    # use value from gglobs
                else:           gglobs.GraphScale[vname] = t
                dprint(infostr.format("GraphScale['{}']".format(vname), gglobs.GraphScale[vname]))


    # GMCDevice
        dprint(infostrHeader.format("GMC Device", ""))

        # GMCDevice Configuration
        t = getConfigEntry("GMCDevice", "GMC_Activation", "upper" )
        if t != "WARNING":
            if t == "YES":
                gglobs.Devices["GMC"][2] = True
            dprint(infostr.format("GMC_Activation",      gglobs.Devices["GMC"][2]))

        if gglobs.Devices["GMC"][2]: # show the other stuff only if activated

            # GMCDevice Firmware Bugs
            #fwb = "GMC-500+Re 1.18, GMC-500+Re 1.21"
            t = getConfigEntry("GMCDevice", "GMC_locationBug", "str" )
            if t != "WARNING":
                if t.upper() == "AUTO":                 gglobs.GMC_locationBug = "auto"
                else:                                   gglobs.GMC_locationBug = t
                dprint(infostr.format("Location Bug",   gglobs.GMC_locationBug))

            # GMCDevice Firmware Bugs - GMC_FastEstimateTime
            t = getConfigEntry("GMCDevice", "GMC_FastEstTime", "str" )
            if t != "WARNING":
                try:    temp = int(float(t))
                except: temp = "dummy"
                if   t.upper() == "AUTO":               gglobs.GMC_FastEstTime = "auto"
                elif t.upper() == "DYNAMIC":            gglobs.GMC_FastEstTime = 3
                elif temp in (3,5,10,15,20,30,60):      gglobs.GMC_FastEstTime = temp
                else:                                   gglobs.GMC_FastEstTime = "auto"
                dprint(infostr.format("FastEstTime",    gglobs.GMC_FastEstTime))

            # GMCDevice memory
            t = getConfigEntry("GMCDevice", "GMC_memory", "upper" )
            if t != "WARNING":
                if   t ==  '1MB':       gglobs.GMC_memory = 2**20   # 1 048 576
                elif t == '64KB':       gglobs.GMC_memory = 2**16   #    65 536
                else:                   gglobs.GMC_memory = 'auto'
                dprint(infostr.format("Memory", gglobs.GMC_memory))

            # GMCDevice GMC_SPIRpage
            t = getConfigEntry("GMCDevice", "GMC_SPIRpage", "upper" )
            if t != "WARNING":
                if   t == '2K':     gglobs.GMC_SPIRpage = 2048
                elif t == '4K':     gglobs.GMC_SPIRpage = 4096
                elif t == '8K':     gglobs.GMC_SPIRpage = 4096 * 2
                elif t == '16K':    gglobs.GMC_SPIRpage = 4096 * 4
                else:               gglobs.GMC_SPIRpage = "auto"
                # TESTING
                # else:             gglobs.GMC_SPIRpage = 2048  # @ 16k speed: 8287 B/sec
                                                                # @  8k speed: 7908 B/sec
                                                                # @  4k speed: 7140 B/sec
                                                                # @  2k speed: 6057 B/sec

                # END TESTING
                dprint(infostr.format("SPIRpage", gglobs.GMC_SPIRpage))

            # GMCDevice GMC_SPIRbugfix
            t = getConfigEntry("GMCDevice", "GMC_SPIRbugfix", "upper" )
            if t != "WARNING":
                if   t == 'YES':  gglobs.GMC_SPIRbugfix = True
                elif t == 'NO':   gglobs.GMC_SPIRbugfix = False
                else:             gglobs.GMC_SPIRbugfix = 'auto'
                dprint(infostr.format("SPIRbugfix", gglobs.GMC_SPIRbugfix))

            # GMCDevice GMC_configsize
            t = getConfigEntry("GMCDevice", "GMC_configsize", "upper" )
            if t != "WARNING":
                t = config.get("GMCDevice", "GMC_configsize")
                if   t == '256':  gglobs.GMC_configsize = 256
                elif t == '512':  gglobs.GMC_configsize = 512
                else:             gglobs.GMC_configsize = 'auto'
                dprint(infostr.format("Configsize", gglobs.GMC_configsize))

            # GMCDevice calibration Def tube is same as 1st tube
            t = getConfigEntry("GMCDevice", "GMC_sensitivity", "upper" )
            if t != "WARNING":
                if t == 'AUTO':             gglobs.Sensitivity[0] = "auto"
                else:
                    try:
                        if float(t) > 0:    gglobs.Sensitivity[0] = float(t)
                        else:               gglobs.Sensitivity[0] = "auto"
                    except:                 gglobs.Sensitivity[0] = "auto"

                gglobs.Sensitivity[1] = gglobs.Sensitivity[0]               # tube 1 same as tube 0/Def

                dprint(infostr.format("Sensitivity Def Tube", gglobs.Sensitivity[0]))
                dprint(infostr.format("Sensitivity 1st Tube", gglobs.Sensitivity[1]))

            # GMCDevice calibration 2nd tube
            t = getConfigEntry("GMCDevice", "GMC_sensitivity2nd", "upper" )
            if t != "WARNING":
                if t == 'AUTO':             gglobs.Sensitivity[2] = "auto"
                else:
                    try:
                        if float(t) > 0:    gglobs.Sensitivity[2] = float(t)
                        else:               gglobs.Sensitivity[2] = "auto"
                    except:                 gglobs.Sensitivity[2] = "auto"
                dprint(infostr.format("Sensitivity 2nd Tube", gglobs.Sensitivity[2]))

            # GMCDevice GMC_voltagebytes
            t = getConfigEntry("GMCDevice", "GMC_voltagebytes", "upper" )
            if t != "WARNING":
                if   t == '1':              gglobs.GMC_voltagebytes = 1
                elif t == '5':              gglobs.GMC_voltagebytes = 5
                else:                       gglobs.GMC_voltagebytes = 'auto'
                dprint(infostr.format("Voltagebytes", gglobs.GMC_voltagebytes))

            # GMCDevice GMC_endianness
            t = getConfigEntry("GMCDevice", "GMC_endianness", "upper" )
            if t != "WARNING":
                if   t == 'LITTLE':         gglobs.GMC_endianness = 'little'
                elif t == 'BIG':            gglobs.GMC_endianness = 'big'
                else:                       gglobs.GMC_endianness = 'auto'
                dprint(infostr.format("Endianness", gglobs.GMC_endianness))


            # GMCDevice GMC_WifiIndex
            t = getConfigEntry("GMCDevice", "GMC_WifiIndex", "upper" )
            if t != "WARNING":
                if   t == "AUTO":           gglobs.GMC_WifiIndex = "auto"
                elif t == "NONE":           gglobs.GMC_WifiIndex = None #"none"
                elif t in  ["2", "3", "4"]: gglobs.GMC_WifiIndex = t
                else:                       gglobs.GMC_WifiIndex = "auto"
                dprint(infostr.format("WifiIndex", gglobs.GMC_WifiIndex))


            # GMCDevice GMC_nbytes
            t = getConfigEntry("GMCDevice", "GMC_nbytes", "upper" )
            if t != "WARNING":
                if t == "AUTO":             gglobs.GMC_nbytes = "auto"
                else:
                    nt = int(t)
                    if nt in (2, 4):        gglobs.GMC_nbytes = nt
                    else:                   gglobs.GMC_nbytes = 2
                dprint(infostr.format("Nbytes", gglobs.GMC_nbytes))


            # GMCDevice variables
            t = getConfigEntry("GMCDevice", "GMC_variables", "str" )
            if t != "WARNING":
                if t.upper() == "AUTO":     gglobs.GMC_variables = "auto"
                else:                       gglobs.GMC_variables = correctVariableCaps(t)
                dprint(infostr.format("Variables", gglobs.GMC_variables))


        # GMCSerialPort
            dprint(infostrHeader.format("  GMCSerialPort", ""))

            t = getConfigEntry("GMCSerialPort", "GMC_usbport", "str" )
            if t != "WARNING":
                if   t.upper() == "AUTO":               gglobs.GMC_usbport = "auto"
                else:                                   gglobs.GMC_usbport = t
                dprint(infostr.format("Using usbport",  gglobs.GMC_usbport))

            t = getConfigEntry("GMCSerialPort", "GMC_baudrate", "upper" )
            if t != "WARNING":
                if t == "AUTO":                         gglobs.GMC_baudrate = "auto"
                else:
                    try:
                        t = int(float(t))
                        if    t in gglobs.GMCbaudrates: gglobs.GMC_baudrate = t
                    except:
                        gglobs.GMC_baudrate = "auto"
                dprint(infostr.format("Using baudrate", gglobs.GMC_baudrate))


            t = getConfigEntry("GMCSerialPort", "GMC_timeout", "upper" )
            if t != "WARNING":
                if t == "AUTO":                         gglobs.GMC_timeout = "auto"
                else:
                    try:
                        t = float(t)
                        if    t > 0:                    gglobs.GMC_timeout = t
                        else:                           gglobs.GMC_timeout = "auto"
                    except:
                        gglobs.GMC_timeout = "auto"
                dprint(infostr.format("Using timeout (sec)",  gglobs.GMC_timeout))


            t = getConfigEntry("GMCSerialPort", "GMC_timeout_write", "upper" )
            if t != "WARNING":
                if t == "AUTO":                         gglobs.GMC_timeout_write = "auto"
                else:
                    try:
                        t = float(t)
                        if    t > 0:                    gglobs.GMC_timeout_write = t
                        else:                           gglobs.GMC_timeout_write = "auto"
                    except:
                        gglobs.GMC_timeout = "auto"
                dprint(infostr.format("Using timeout_write (sec)",  gglobs.GMC_timeout_write))


            # t = getConfigEntry("GMCSerialPort", "GMC_ttyS", "upper" )
            # if t != "WARNING":
            #     if   t == 'INCLUDE':  gglobs.GMC_ttyS = 'include'
            #     else:                 gglobs.GMC_ttyS = 'ignore'
            #     dprint(infostr.format("Ports of ttyS type", gglobs.GMC_ttyS))


    # AudioCounter
        dprint(infostrHeader.format("AudioCounter Device", ""))
        # AudioCounter Activation
        t = getConfigEntry("AudioCounter", "AudioActivation", "upper" )
        if t != "WARNING":
            if t == "YES":
                gglobs.Devices["Audio"][2] = True
            dprint(infostr.format("AudioActivation",    gglobs.Devices["Audio"][2]))

        if gglobs.Devices["Audio"][2]: # show the other stuff only if activated

            # AudioCounter DEVICE
            t = getConfigEntry("AudioCounter", "AudioDevice", "str" )
            if t != "WARNING":
                if   t.upper() == "AUTO":               gglobs.AudioDevice = "auto"
                elif not ("," in t):                    gglobs.AudioDevice = "auto" # must have 2 items separated by comma
                else:
                    t = t.split(",", 1)
                    t[0] = t[0].strip()
                    t[1] = t[1].strip()
                    if t[0].isdecimal():   t[0] = int(t[0])
                    if t[1].isdecimal():   t[1] = int(t[1])
                    gglobs.AudioDevice = tuple(t)
                dprint(infostr.format("AudioDevice",    gglobs.AudioDevice))

            # AudioCounter LATENCY
            t = getConfigEntry("AudioCounter", "AudioLatency", "str" )
            if t != "WARNING":
                if   t.upper() == "AUTO":               gglobs.AudioLatency = "auto"
                elif not ("," in t):                    gglobs.AudioLatency = "auto" # must have 2 items separated by comma
                else:
                    t = t.split(",", 1)
                    try:    t[0] = float(t[0])
                    except: t[0] = 1.0
                    try:    t[1] = float(t[1])
                    except: t[1] = 1.0
                    gglobs.AudioLatency = tuple(t)
                dprint(infostr.format("AudioLatency", gglobs.AudioLatency))

            # AudioCounter PULSE Dir
            t = getConfigEntry("AudioCounter", "AudioPulseDir", "upper" )
            if t != "WARNING":
                if   t == "AUTO":           gglobs.AudioPulseDir = "auto"
                elif t == "NEGATIVE":       gglobs.AudioPulseDir = False
                elif t == "POSITIVE":       gglobs.AudioPulseDir = True
                else:                       pass # unchanged from default False
                dprint(infostr.format("AudioPulseDir", gglobs.AudioPulseDir))

            # AudioCounter PULSE Max
            t = getConfigEntry("AudioCounter", "AudioPulseMax", "upper" )
            if t != "WARNING":
                if t == "AUTO":                     gglobs.AudioPulseMax = "auto"
                else:
                    try:                            gglobs.AudioPulseMax = int(float(t))
                    except:                         gglobs.AudioPulseMax = "auto"
                    if gglobs.AudioPulseMax <= 0:   gglobs.AudioPulseMax = "auto"
                dprint(infostr.format("AudioPulseMax", gglobs.AudioPulseMax))

            # AudioCounter LIMIT
            t = getConfigEntry("AudioCounter", "AudioThreshold", "upper" )
            if t != "WARNING":
                if t == "AUTO":             gglobs.AudioThreshold = "auto"
                else:
                    try:                    gglobs.AudioThreshold = int(float(t))
                    except:                 gglobs.AudioThreshold = 60
                    if gglobs.AudioThreshold < 0 or gglobs.AudioThreshold > 100:
                                            gglobs.AudioThreshold = 60
                dprint(infostr.format("AudioThreshold", gglobs.AudioThreshold))

            # AudioCounter Variables
            t = getConfigEntry("AudioCounter", "AudioVariables", "str" )
            if t != "WARNING":
                if t.upper() == "AUTO":     gglobs.AudioVariables = "auto"
                else:                       gglobs.AudioVariables = correctVariableCaps(t)
                dprint(infostr.format("AudioVariables", gglobs.AudioVariables))


            # AudioCounter Sensitivity
            t = getConfigEntry("AudioCounter", "AudioSensitivity", "str" )
            if t != "WARNING":
                if t.upper() == "AUTO":                 gglobs.AudioSensitivity = "auto"
                else:
                    try:
                        gglobs.AudioSensitivity = float(t)
                        if gglobs.AudioSensitivity <= 0:    gglobs.AudioSensitivity = "auto"
                    except:                                 gglobs.AudioSensitivity = "auto"
                dprint(infostr.format("AudioSensitivity", gglobs.AudioSensitivity))


    # RadMonPlus
        dprint(infostrHeader.format("RadMonPlus Device", ""))

        # RadMon Activation
        t = getConfigEntry("RadMonPlusDevice", "RMActivation", "upper" )
        if t != "WARNING":
            if t == "YES":
                gglobs.Devices["RadMon"][2] = True
            dprint(infostr.format("RMActivation", gglobs.Devices["RadMon"][2] ))

        if gglobs.Devices["RadMon"][2]: # show the other stuff only if activated

            # RadMon Server IP
            t = getConfigEntry("RadMonPlusDevice", "RMServerIP", "str" )
            if t != "WARNING":
                if t.upper() == 'AUTO':                 gglobs.RMServerIP = "auto"
                else:                                   gglobs.RMServerIP = t
                dprint(infostr.format("RMServerIP",     gglobs.RMServerIP ))

            # RadMon Server Port
            t = getConfigEntry("RadMonPlusDevice", "RMServerPort", "str" )
            if t != "WARNING":
                if t.upper() == 'AUTO':                 gglobs.RMServerPort = "auto"
                else:
                    try:    gglobs.RMServerPort = abs(int(t))
                    except: gglobs.RMServerPort = "auto"
                dprint(infostr.format("RMServerPort",   gglobs.RMServerPort))

            # Radmon timeout
            t = getConfigEntry("RadMonPlusDevice", "RMTimeout", "upper" )
            if t != "WARNING":
                if t == 'AUTO':                         gglobs.RMTimeout = "auto"
                else:
                    try:
                        if float(t) > 0:                gglobs.RMTimeout = float(t)
                        else:                           gglobs.RMTimeout = "auto"  # if zero or negative value given
                    except:                             gglobs.RMTimeout = "auto"
                dprint(infostr.format("RMTimeout",      gglobs.RMTimeout))

            # RadMon Server Folder
            t = getConfigEntry("RadMonPlusDevice", "RMServerFolder", "str" )
            if t != "WARNING":
                # blank in folder name not allowed
                if " " in t or t.upper() == "AUTO":     gglobs.RMServerFolder = "auto"
                else:
                    gglobs.RMServerFolder = t
                    if gglobs.RMServerFolder[-1] != "/":gglobs.RMServerFolder += "/"
                dprint(infostr.format("RMServerFolder", gglobs.RMServerFolder ))

            # RadMon calibration tube
            t = getConfigEntry("RadMonPlusDevice", "RMSensitivity", "upper")
            if t != "WARNING":
                if t == 'AUTO':                         gglobs.RMSensitivity = "auto"
                else:
                    if float(t) > 0:                    gglobs.RMSensitivity = float(t)
                    else:                               gglobs.RMSensitivity = "auto"
                dprint(infostr.format("RMSensitivity",  gglobs.RMSensitivity))

            # Radmon variables
            t = getConfigEntry("RadMonPlusDevice", "RMVariables", "str" )
            if t != "WARNING":
                if t.upper() == "AUTO":                 gglobs.RMVariables = "auto"
                else:
                    gglobs.RMVariables = correctVariableCaps(t)
                    if gglobs.RMVariables.count("CPM") > 1 or gglobs.RMVariables.count("CPS") > 0:
                        edprint("WARNING: Improper configuration of variables: ", gglobs.RMVariables)
                        edprint("WARNING: Only a single CPM* is allowed, and no CPS*")
                        gglobs.RMVariables = "auto"
                        edprint("WARNING: RadMon variables are reset to: ", gglobs.RMVariables)
                dprint(infostr.format("RMVariables",    gglobs.RMVariables))


    # AmbioMon
        dprint(infostrHeader.format("AmbioMon Device", ""))

        # AmbioMon Activation
        t = getConfigEntry("AmbioMonDevice", "AmbioActivation", "upper" )
        if t != "WARNING":
            if t == "YES":
                gglobs.Devices["AmbioMon"][2] = True
            dprint(infostr.format("AmbioActivation",    gglobs.Devices["AmbioMon"][2]))

        if gglobs.Devices["AmbioMon"][2]: # show the other stuff only if activated

            # AmbioMon Server IP
            t = getConfigEntry("AmbioMonDevice", "AmbioServerIP", "str" )
            if t != "WARNING":
                if t.upper() == 'AUTO':                 gglobs.AmbioServerIP = "auto"
                else:                                   gglobs.AmbioServerIP = t
                dprint(infostr.format("AmbioServerIP",  gglobs.AmbioServerIP ))

            # AmbioMon Server Port
            t = getConfigEntry("AmbioMonDevice", "AmbioServerPort", "upper" )
            if t != "WARNING":
                if t == "AUTO":                             gglobs.AmbioServerPort = "auto"
                else:
                    wp = int(float(t))
                    if 0 <= wp  <= 65535:                   gglobs.AmbioServerPort = wp
                    else:                                   gglobs.AmbioServerPort = "auto"
                dprint(infostr.format("AmbioServerPort",    gglobs.AmbioServerPort ))

            # AmbioMon timeout
            t = getConfigEntry("AmbioMonDevice", "AmbioTimeout", "upper" )
            if t != "WARNING":
                if t == 'AUTO':                         gglobs.AmbioTimeout = "auto"
                else:
                    try:
                        if float(t) > 0:                gglobs.AmbioTimeout = float(t)
                        else:                           gglobs.AmbioTimeout = "auto"  # if zero or negative value given
                    except:                             gglobs.AmbioTimeout = "auto"
                dprint(infostr.format("AmbioTimeout",   gglobs.AmbioTimeout))

            # AmbioMon calibration
            t = getConfigEntry("AmbioMonDevice", "AmbioSensitivity", "upper" )
            if t != "WARNING":
                if t == 'AUTO':                         gglobs.AmbioSensitivity = "auto"
                else:
                    try:
                        if float(t) > 0:                gglobs.AmbioSensitivity = float(t)
                        else:                           gglobs.AmbioSensitivity = "auto"
                    except:                             gglobs.AmbioSensitivity = "auto"
                dprint(infostr.format("AmbioSensitivity", gglobs.AmbioSensitivity))

            # AmbioMon DataType
            t = getConfigEntry("AmbioMonDevice", "AmbioDataType", "str" )
            if t != "WARNING":
                if   t.upper() == "AUTO":               gglobs.AmbioDataType = "auto"
                elif t.upper() == "AVG":                gglobs.AmbioDataType = "AVG"
                else:                                   gglobs.AmbioDataType = "LAST"
                dprint(infostr.format("AmbioDataType",  gglobs.AmbioDataType))

            # AmbioMon variables
            t = getConfigEntry("AmbioMonDevice", "AmbioVariables", "str" )
            if t != "WARNING":
                if t.upper() == "AUTO":                 gglobs.AmbioVariables = "auto"
                else:                                   gglobs.AmbioVariables = correctVariableCaps(t)
                dprint(infostr.format("AmbioVariables", gglobs.AmbioVariables))

    # Gamma-Scout counter
        dprint(infostrHeader.format("GammaScout Device", ""))
        # Gamma-Scout Activation
        t = getConfigEntry("GammaScoutDevice", "GSActivation", "upper" )
        if t != "WARNING":
            if t == "YES":
                gglobs.Devices["GammaScout"][2] = True
            dprint(infostr.format("GSActivation",       gglobs.Devices["GammaScout"][2] ))

        if gglobs.Devices["GammaScout"][2]: # show the other stuff only if activated

            # Gamma-Scout variables
            t = getConfigEntry("GammaScoutDevice", "GSVariables", "str" )
            if t != "WARNING":
                if t.upper() == "AUTO":                 gglobs.GSVariables = "auto"
                else:                                   gglobs.GSVariables = correctVariableCaps(t)
                dprint(infostr.format("GSVariables",    gglobs.GSVariables))

            # Gamma-Scout Sensitivity
            t = getConfigEntry("GammaScoutDevice", "GSSensitivity", "upper" )
            if t != "WARNING":
                if t == "AUTO":                         gglobs.GSSensitivity = "auto"
                else:
                    try:
                        gglobs.GSSensitivity = float(t)
                        if gglobs.GSSensitivity <= 0:   gglobs.GSSensitivity = "auto"
                    except:                             gglobs.GSSensitivity = "auto"
                dprint(infostr.format("GSSensitivity",  gglobs.GSSensitivity))


        # GammaScoutSerialPort
            dprint(infostrHeader.format("  GammaScoutSerialPort", ""))

            t = getConfigEntry("GammaScoutSerialPort", "GSusbport", "str" )
            if t != "WARNING":
                if   t.upper() == "AUTO":                   gglobs.GSusbport = "auto"
                else:                                       gglobs.GSusbport = t
                dprint(infostr.format("Using GSusbport",    gglobs.GSusbport))

            t = getConfigEntry("GammaScoutSerialPort", "GSbaudrate", "int" )
            if t != "WARNING":
                if t in gglobs.GSbaudrates:                 gglobs.GSbaudrate = t
                dprint(infostr.format("Using GSbaudrate",   gglobs.GSbaudrate))

            t = getConfigEntry("GammaScoutSerialPort", "GStimeout", "float" )
            if t != "WARNING":
                if t > 0:   gglobs.GStimeout = t
                else:       gglobs.GStimeout = 3  # if zero or negative value given, set to 3
                dprint(infostr.format("Using GStimeout (sec)",gglobs.GStimeout))

            t = getConfigEntry("GammaScoutSerialPort", "GStimeout_write", "float" )
            if t != "WARNING":
                if t > 0:   gglobs.GStimeout_write = t
                else:       gglobs.GStimeout_write = 3  # if zero or negative value given, set to 3
                dprint(infostr.format("Using GStimeout_write (sec)",gglobs.GStimeout_write))

            # t = getConfigEntry("GammaScoutSerialPort", "GSttyS", "upper" )
            # if t != "WARNING":
            #     if    t == 'INCLUDE':  gglobs.GSttyS = 'include'
            #     else:                  gglobs.GSttyS = 'ignore'
            #     dprint(infostr.format("Ports of ttyS type", gglobs.GSttyS))


    # I2C
        dprint(infostrHeader.format("I2CSensor Device", ""))

        # I2C Activation
        t = getConfigEntry("I2C", "I2CActivation", "upper" )
        if t != "WARNING":
            if t == "YES":
                gglobs.Devices["I2C"][2] = True
            dprint(infostr.format("I2CActivation",          gglobs.Devices["I2C"][2] ))

        if gglobs.Devices["I2C"][2]: # show the other stuff only if activated

            # I2C Dongle - ISS, ELV, IOW
            t = getConfigEntry("I2C", "I2CDongle", "upper" )
            if t != "WARNING":
                t = t.strip()
                try:
                    # if t in ["ISS", "ELV", "IOW", "FTD"]:   gglobs.I2CDongleCode = t  # no FTD support
                    if t in ["ISS", "ELV", "IOW"]:          gglobs.I2CDongleCode = t
                    else:                                   gglobs.I2CDongleCode = "ISS"
                except:
                    gglobs.I2CDongleCode = "ISS"
                dprint(infostr.format("I2CDongle",   gglobs.I2CDongleCode))

            # I2C variables:  included in sensors settings

            # I2C Sensors Options (3 sep by comma):  < yes | no > , <Sensor Addr in hex>, <variables>
            # like: I2CSensorBME280  = y, 0x76, Temp, Press, Humid
            # here 'y' and 'n' can be used for 'yes' and 'no'

            # I2C Sensors - LM75, addr 0x48 | 0x49 | 0x4A | 0x4B | 0x4C | 0x4E | 0x4F
            t = getConfigEntry("I2C", "I2CSensorLM75", "str" )
            if t != "WARNING":
                t = t.strip().split(",")
                try:
                    if "Y" in t[0].strip().upper():        gglobs.I2CSensor["LM75"][0] = True
                    else:                                  gglobs.I2CSensor["LM75"][0] = False
                    gglobs.I2CSensor["LM75"][1] = int(t[1], 16)
                except:
                    gglobs.I2CSensor["LM75"][0] = False
                    gglobs.I2CSensor["LM75"][1] = 0x48
                gglobs.I2CSensor["LM75"][2] = t[2:]
                dprint(infostr.format("I2CSensorLM75]",   gglobs.I2CSensor["LM75"]))

            # I2C Sensors - BME280, addr 0x76 | 0x77
            # I2CSensorBME280 : [True, 118, [' Temp', ' Press', ' Humid']]
            t = getConfigEntry("I2C", "I2CSensorBME280", "str" )
            if t != "WARNING":
                t = t.strip().split(",")
                try:
                    if "Y" in t[0].strip().upper():        gglobs.I2CSensor["BME280"][0] = True
                    else:                                  gglobs.I2CSensor["BME280"][0] = False
                    gglobs.I2CSensor["BME280"][1] = int(t[1], 16)
                except:
                    gglobs.I2CSensor["BME280"][0] = False
                    gglobs.I2CSensor["BME280"][1] = 0x76
                gglobs.I2CSensor["BME280"][2] = t[2:]
                dprint(infostr.format("I2CSensorBME280", gglobs.I2CSensor["BME280"]))

            # I2C Sensors - SCD41, addr 0x62
            t = getConfigEntry("I2C", "I2CSensorSCD41", "str" )
            if t != "WARNING":
                t = t.strip().split(",")
                try:
                    if "Y" in t[0].strip().upper():        gglobs.I2CSensor["SCD41"][0] = True
                    else:                                  gglobs.I2CSensor["SCD41"][0] = False
                    gglobs.I2CSensor["SCD41"][1] = int(t[1], 16)
                except:
                    gglobs.I2CSensor["SCD41"][0] = False
                    gglobs.I2CSensor["SCD41"][1] = 0x29
                gglobs.I2CSensor["SCD41"][2] = t[2:]
                dprint(infostr.format("I2CSensorSCD41", gglobs.I2CSensor["SCD41"]))

            # I2C Sensors - SCD30, addr 0x61
            t = getConfigEntry("I2C", "I2CSensorSCD30", "str" )
            if t != "WARNING":
                t = t.strip().split(",")
                try:
                    if "Y" in t[0].strip().upper():        gglobs.I2CSensor["SCD30"][0] = True
                    else:                                  gglobs.I2CSensor["SCD30"][0] = False
                    gglobs.I2CSensor["SCD30"][1] = int(t[1], 16)
                except:
                    gglobs.I2CSensor["SCD30"][0] = False
                    gglobs.I2CSensor["SCD30"][1] = 0x29
                gglobs.I2CSensor["SCD30"][2] = t[2:]
                dprint(infostr.format("I2CSensorSCD30", gglobs.I2CSensor["SCD30"]))

            # I2C Sensors - TSL2591, addr 0x29
            t = getConfigEntry("I2C", "I2CSensorTSL2591", "str" )
            if t != "WARNING":
                t = t.strip().split(",")
                try:
                    if "Y" in t[0].strip().upper():        gglobs.I2CSensor["TSL2591"][0] = True
                    else:                                  gglobs.I2CSensor["TSL2591"][0] = False
                    gglobs.I2CSensor["TSL2591"][1] = int(t[1], 16)
                except:
                    gglobs.I2CSensor["TSL2591"][0] = False
                    gglobs.I2CSensor["TSL2591"][1] = 0x29
                gglobs.I2CSensor["TSL2591"][2] = t[2:]
                dprint(infostr.format("I2CSensorTSL2591", gglobs.I2CSensor["TSL2591"]))


        # I2CSerialPort
        # now reocated to the I2C category
            dprint(infostrHeader.format("  I2CSerialPort", ""))

            t = getConfigEntry("I2C", "I2Cusbport", "str" )
            if t != "WARNING":
                if t.upper() == "AUTO":                     gglobs.I2Cusbport = "auto"
                else:                                       gglobs.I2Cusbport = t
                dprint(infostr.format("Using I2Cusbport",   gglobs.I2Cusbport))

            # baudrate is now fixed at 115200
            # t = getConfigEntry("I2CSerialPort", "I2Cbaudrate", "int" )
            # if t != "WARNING":
            #     if t in gglobs.GMCbaudrates:                gglobs.I2Cbaudrate = t
            #     dprint(infostr.format("Using I2Cbaudrate",  gglobs.I2Cbaudrate))
            # dprint(infostr.format("Using I2Cbaudrate",      gglobs.I2Cbaudrate))

            # t = getConfigEntry("I2CSerialPort", "I2Ctimeout", "float" )
            # if t != "WARNING":
            #     if t > 0:   gglobs.I2Ctimeout = t
            #     else:       gglobs.I2Ctimeout = 3  # if zero or negative value given, set to 3
            # dprint(infostr.format("Using I2Ctimeout (sec)",gglobs.I2Ctimeout))

            # t = getConfigEntry("I2CSerialPort", "I2Ctimeout_write", "float" )
            # if t != "WARNING":
            #     if t > 0:   gglobs.I2Ctimeout_write = t
            #     else:       gglobs.I2Ctimeout_write = 1  # if zero or negative value given, set to 1
            # dprint(infostr.format("Using I2Ctimeout_write (sec)",gglobs.I2Ctimeout_write))

            # t = getConfigEntry("I2CSerialPort", "I2CttyS", "upper" )
            # if t != "WARNING":
            #     if    t == 'INCLUDE':                       gglobs.I2CttyS = 'include'
            #     else:                                       gglobs.I2Cttys = 'ignore'
            #     dprint(infostr.format("Ports of ttyS type", gglobs.I2Cttys))




    # LabJack U3 (type U3B, perhaps with probe EI1050)
        dprint(infostrHeader.format("LabJack Device", ""))
        # LabJack Activation
        t = getConfigEntry("LabJackDevice", "LJActivation", "upper" )
        if t != "WARNING":
            if t == "YES":
                gglobs.Devices["LabJack"][2] = True
            dprint(infostr.format("LJActivation",           gglobs.Devices["LabJack"][2]))

        if gglobs.Devices["LabJack"][2]: # show the other stuff only if activated

            # LabJack  EI1050 Activation
            t = getConfigEntry("LabJackDevice", "LJEI1050Activation", "upper" )
            if t != "WARNING":
                if t == "YES":                              gglobs.LJEI1050Activation = True
                dprint(infostr.format("LJEI1050Activation", gglobs.LJEI1050Activation))

            # LabJack variables
            t = getConfigEntry("LabJackDevice", "LJVariables", "str" )
            if t != "WARNING":
                if t.upper() == "AUTO":                     gglobs.LJVariables = "auto"
                else:                                       gglobs.LJVariables = correctVariableCaps(t)
                dprint(infostr.format("LJVariables",        gglobs.LJVariables))


    # MiniMon
        dprint(infostrHeader.format("MiniMon Device", ""))

        t = getConfigEntry("MiniMon", "MiniMonActivation", "upper" )
        if t != "WARNING":
            if t == "YES":
                gglobs.Devices["MiniMon"][2] = True
            dprint(infostr.format("MiniMonActivation",      gglobs.Devices["MiniMon"][2]))

        if gglobs.Devices["MiniMon"][2]: # show the other stuff only if activated

            # MiniMon Device
            t = getConfigEntry("MiniMon", "MiniMonOS_Device", "str" )
            if t != "WARNING":
                if t.upper() == "AUTO":                     gglobs.MiniMonOS_Device = "auto"
                else:                                       gglobs.MiniMonOS_Device = t
                dprint(infostr.format("MiniMonOS_Device",      gglobs.MiniMonOS_Device))

            # MiniMon Variables
            t = getConfigEntry("MiniMon", "MiniMonVariables", "str" )
            if t != "WARNING":
                if t.upper() == "AUTO":                     gglobs.MiniMonVariables = "auto"
                else:                                       gglobs.MiniMonVariables = correctVariableCaps(t)
                dprint(infostr.format("MiniMonVariables",   gglobs.MiniMonVariables))

            # MiniMon Interval
            t = getConfigEntry("MiniMon", "MiniMonInterval", "str" )
            if t != "WARNING":
                if t.upper() == "AUTO":                     gglobs.MiniMonInterval = "auto"
                else:
                    try:
                        gglobs.MiniMonInterval = float(t)
                        if gglobs.MiniMonInterval < 0:      gglobs.MiniMonInterval = "auto"
                    except:                                 gglobs.MiniMonInterval = "auto"
                dprint(infostr.format("MiniMonInterval",    gglobs.MiniMonInterval))


    # Simul Device
        dprint(infostrHeader.format("Simul Device", ""))
        # Simul Device Activation
        t = getConfigEntry("Simul", "SimulActivation", "upper" )
        if t != "WARNING":
            if t == "YES":
                gglobs.Devices["Simul"][2] = True
            dprint(infostr.format("SimulActivation",        gglobs.Devices["Simul"][2]))

        if gglobs.Devices["Simul"][2]: # show the other stuff only if activated

            # Simul Device MEAN
            t = getConfigEntry("Simul", "SimulMean", "upper" )
            if t != "WARNING":
                if   t == "AUTO":                           gglobs.SimulMean = "auto"
                else:
                    try:
                        gglobs.SimulMean = float(t)
                        if gglobs.SimulMean < 0:            gglobs.SimulMean = "auto"
                    except:                                 gglobs.SimulMean = "auto"
                dprint(infostr.format("SimulMean",          gglobs.SimulMean))

            # inactive. config file code in module gdev_simul.py
            #
            #~t = getConfigEntry("Simul", "SimulPredictive", "upper" )
            #~if t != "WARNING":
                #~if t == "YES":                      gglobs.SimulPredictive = True
                #~else:                               gglobs.SimulPredictive = False
                #~dprint(infostr.format("SimulPredictive", gglobs.SimulPredictive))

            #~t = getConfigEntry("Simul", "SimulPredictLimit", "str" )
            #~if t != "WARNING":
                #~if t.upper() == "AUTO":             gglobs.SimulPredictLimit = "auto"
                #~try:
                    #~gglobs.SimulPredictLimit = int(float(t))
                    #~if gglobs.SimulPredictLimit < 0:gglobs.SimulPredictLimit = "auto"
                #~except:                             gglobs.SimulPredictLimit = "auto"
                #~dprint(infostr.format("SimulPredictLimit", gglobs.SimulPredictLimit))


            # Simul Device Sensitivity
            t = getConfigEntry("Simul", "SimulSensitivity", "str" )
            if t != "WARNING":
                if t.upper() == "AUTO":                     gglobs.SimulSensitivity = "auto"
                else:
                    try:
                        gglobs.SimulSensitivity = float(t)
                        if gglobs.SimulSensitivity <= 0:    gglobs.SimulSensitivity = "auto"
                    except:                                 gglobs.SimulSensitivity = "auto"
                dprint(infostr.format("SimulSensitivity",   gglobs.SimulSensitivity))

            # Simul Device Deadtime
            t = getConfigEntry("Simul", "SimulDeadtime", "str" )
            if t != "WARNING":
                if t.upper() == "AUTO":                     gglobs.SimulDeadtime = "auto"
                else:
                    try:
                        gglobs.SimulDeadtime = float(t)
                        if gglobs.SimulDeadtime < 0:        gglobs.SimulDeadtime = "auto"
                    except:                                 gglobs.SimulDeadtime = "auto"
                dprint(infostr.format("SimulDeadtime",      gglobs.SimulDeadtime))

            # Simul Device Variables
            t = getConfigEntry("Simul", "SimulVariables", "str" )
            if t != "WARNING":
                if t.upper() == "AUTO":                     gglobs.SimulVariables = "auto"
                else:                                       gglobs.SimulVariables = correctVariableCaps(t)
                dprint(infostr.format("SimulVariables",     gglobs.SimulVariables))


    # Manu
        dprint(infostrHeader.format("Manu Device", ""))

        t = getConfigEntry("Manu", "ManuActivation", "upper" )
        if t != "WARNING":
            if t == "YES":
                gglobs.Devices["Manu"][2] = True
            dprint(infostr.format("ManuActivation",         gglobs.Devices["Manu"][2]))

        if gglobs.Devices["Manu"][2]: # show the other stuff only if activated

            # Manu Sensitivity
            t = getConfigEntry("Manu", "ManuSensitivity", "upper" )
            if t != "WARNING":
                if t == "AUTO":                             gglobs.ManuSensitivity = "auto"
                else:
                    try:
                        gglobs.ManuSensitivity = float(t)
                        if gglobs.ManuSensitivity <= 0:     gglobs.ManuSensitivity = "auto"
                    except:                                 gglobs.ManuSensitivity = "auto"
                dprint(infostr.format("ManuSensitivity",    gglobs.ManuSensitivity))

            # Manu RecordStyle
            t = getConfigEntry("Manu", "ManuRecordStyle", "upper" )
            if t != "WARNING":
                if t == "AUTO":                             gglobs.ManuRecordStyle = "auto"
                else:
                    if      t == "POINT":                   gglobs.ManuRecordStyle = "Point"
                    elif    t == "STEP":                    gglobs.ManuRecordStyle = "Step"
                    else:                                   gglobs.ManuRecordStyle = "auto"
                dprint(infostr.format("ManuRecordStyle",    gglobs.ManuRecordStyle))

            # Manu Variables
            t = getConfigEntry("Manu", "ManuVariables", "str" )
            if t != "WARNING":
                if t.upper() == "AUTO" :                    gglobs.ManuVariables = "auto"
                else:                                       gglobs.ManuVariables = correctVariableCaps(t)
                dprint(infostr.format("ManuVariables",      gglobs.ManuVariables))


    # WiFiServer
        dprint(infostrHeader.format("WiFiServer Device", ""))

        # WiFiServer Activation
        t = getConfigEntry("WiFiServerDevice", "WiFiServerActivation", "upper" )
        if t != "WARNING":
            if t == "YES":
                gglobs.Devices["WiFiServer"][ACTIV] = True
            dprint(infostr.format("WiFiServerActivation",    gglobs.Devices["WiFiServer"][ACTIV]))

        if gglobs.Devices["WiFiServer"][ACTIV]: # show the other stuff only if activated

            # WiFiServer IP
            t = getConfigEntry("WiFiServerDevice", "WiFiServerIP", "str" )
            if t != "WARNING":
                if t.upper() == "AUTO":                     gglobs.WiFiServerIP = "auto"
                else:                                       gglobs.WiFiServerIP = t
                dprint(infostr.format("WiFiServerIP",       gglobs.WiFiServerIP))

            # WiFiServer Port
            t = getConfigEntry("WiFiServerDevice", "WiFiServerPort", "upper" )
            if t != "WARNING":
                if t == "AUTO":                             gglobs.WiFiServerPort = "auto"
                else:
                    wp = int(float(t))
                    if 0 <= wp  <= 65535:                   gglobs.WiFiServerPort = wp
                    else:                                   gglobs.WiFiServerPort = "auto"
                dprint(infostr.format("WiFiServerPort",     gglobs.WiFiServerPort ))

            # WiFiServer Folder
            t = getConfigEntry("WiFiServerDevice", "WiFiServerFolder", "str" )
            if t != "WARNING":
                if t.upper() == 'AUTO':                     gglobs.WiFiServerFolder = "auto"
                else:                                       gglobs.WiFiServerFolder = t.replace("\\", "").replace("/", "")
                dprint(infostr.format("WiFiServerFolder",   gglobs.WiFiServerFolder ))

            # WiFiServer timeout
            t = getConfigEntry("WiFiServerDevice", "WiFiServerTimeout", "upper" )
            if t != "WARNING":
                if t == 'AUTO':                             gglobs.WiFiServerTimeout = "auto"
                else:
                    try:
                        if float(t) > 0:                    gglobs.WiFiServerTimeout = float(t)
                        else:                               gglobs.WiFiServerTimeout = "auto"  # if zero or negative value given
                    except:                                 gglobs.WiFiServerTimeout = "auto"
                dprint(infostr.format("WiFiServerTimeout",  gglobs.WiFiServerTimeout))

            # WiFiServer calibration
            t = getConfigEntry("WiFiServerDevice", "WiFiServerSensitivity", "upper" )
            if t != "WARNING":
                if t == 'AUTO':                             gglobs.WiFiServerSensitivity = "auto"
                else:
                    try:
                        if float(t) > 0:                    gglobs.WiFiServerSensitivity = float(t)
                        else:                               gglobs.WiFiServerSensitivity = "auto"
                    except:                                 gglobs.WiFiServerSensitivity = "auto"
                dprint(infostr.format("WiFiServerSensitivity", gglobs.WiFiServerSensitivity))

            # WiFiServer DataType
            t = getConfigEntry("WiFiServerDevice", "WiFiServerDataType", "str" )
            if t != "WARNING":
                if   t.upper() == "AUTO":                   gglobs.WiFiServerDataType = "auto"
                elif t.upper() == "AVG":                    gglobs.WiFiServerDataType = "AVG"
                else:                                       gglobs.WiFiServerDataType = "LAST"
                dprint(infostr.format("WiFiServerDataType", gglobs.WiFiServerDataType))

            # WiFiServer variables
            t = getConfigEntry("WiFiServerDevice", "WiFiServerVariables", "str" )
            if t != "WARNING":
                if t.upper() == "AUTO":                     gglobs.WiFiServerVariables = "auto"
                else:                                       gglobs.WiFiServerVariables = correctVariableCaps(t)
                dprint(infostr.format("WiFiServerVariables",gglobs.WiFiServerVariables))


    # WiFiClient
        dprint(infostrHeader.format("WiFiClient Device", ""))

        # WiFiClient Activation
        t = getConfigEntry("WiFiClientDevice", "WiFiClientActivation", "upper" )
        if t != "WARNING":
            if t == "YES":
                gglobs.Devices["WiFiClient"][2] = True
            dprint(infostr.format("WiFiClientActivation",    gglobs.Devices["WiFiClient"][2] ))

        if gglobs.Devices["WiFiClient"][2]: # show the other stuff only if activated

            # WiFiClient Server Port
            t = getConfigEntry("WiFiClientDevice", "WiFiClientPort", "upper" )
            if t != "WARNING":
                if t == 'AUTO':                             gglobs.WiFiClientPort = "auto"
                else:
                    try:
                        if float(t) > 0:                    gglobs.WiFiClientPort = int(float(t))
                        else:                               gglobs.WiFiClientPort = "auto"  # if zero or negative value given
                    except:                                 gglobs.WiFiClientPort = "auto"
                dprint(infostr.format("WiFiClientPort",     gglobs.WiFiClientPort ))


            # WiFiClient Type
            t = getConfigEntry("WiFiClientDevice", "WiFiClientType", "upper" )
            if t != "WARNING":
                if t == "GMC":                              gglobs.WiFiClientType = "GMC"
                else:                                       gglobs.WiFiClientType = "GENERIC"
                dprint(infostr.format("WiFiClientType",     gglobs.WiFiClientType))


            # WiFiClient sensitivity
            t = getConfigEntry("WiFiClientDevice", "WiFiClientSensitivity", "upper" )
            if t != "WARNING":
                if t == 'AUTO':                         gglobs.WiFiClientSensitivity = "auto"
                else:
                    try:
                        if float(t) > 0:                gglobs.WiFiClientSensitivity = float(t)
                        else:                           gglobs.WiFiClientSensitivity = "auto"
                    except:                             gglobs.WiFiClientSensitivity = "auto"
                dprint(infostr.format("WiFiClientSensitivity", gglobs.WiFiClientSensitivity))

            # WiFiClient variables
            t = getConfigEntry("WiFiClientDevice", "WiFiClientVariables", "str" )
            if t != "WARNING":
                if t.upper() == "AUTO":                 gglobs.WiFiClientVariables = "auto"
                else:                                   gglobs.WiFiClientVariables = correctVariableCaps(t)
                dprint(infostr.format("WiFiClientVariables", gglobs.WiFiClientVariables))

        break # still in while loop, don't forget to break!

    setDebugIndent(0)
# End Configuration file evaluation #############################################################################
#################################################################################################################


def correctVariableCaps(devicevars):
    """correct any small caps in variables"""

    fncname = "correctVariableCaps: "

    newt = ""
    for uppvname in devicevars.upper().split(","):
        a = uppvname.strip()
        if   a == "CPM"   :   newt += "CPM, "
        elif a == "CPS"   :   newt += "CPS, "
        elif a == "CPM1ST":   newt += "CPM1st, "
        elif a == "CPS1ST":   newt += "CPS1st, "
        elif a == "CPM2ND":   newt += "CPM2nd, "
        elif a == "CPS2ND":   newt += "CPS2nd, "
        elif a == "CPM3RD":   newt += "CPM3rd, "
        elif a == "CPS3RD":   newt += "CPS3rd, "
        elif a == "TEMP"  :   newt += "Temp, "
        elif a == "PRESS" :   newt += "Press, "
        elif a == "HUMID" :   newt += "Humid, "
        elif a == "XTRA"  :   newt += "Xtra, "
        else:                 pass              # if it does not fit, ignore it
        # print(fncname + "a: ", a, "newt: ", newt)

    newt = newt[:-2]

    # on wrong entries newt will be empty
    if newt == "": newt = "auto"

    return newt


def readPrivateConfig():
    """reads the private.cfg file if present, and adds the definitions
    if not present the geigerlog.cfg settings remain in use"""

    # the private file uses this format:
    # gglobs.WiFiSSID, gglobs.WiFiPassword, gglobs.gmcmapUserID, gglobs.gmcmapCounterID, gglobs.TelegramToken
    # like: mySSID, myPW, 012345, 01234567890,

    fncname  = "readPrivateConfig: "
    filepath = os.path.join(gglobs.progPath, "../private.cfg")
    dprint(fncname)
    setDebugIndent(1)

    if not os.access(filepath, os.R_OK) :
        edprint("{:25s}: {}".format(fncname, "Private file not found"))
    else:
        try:
            # raise Exception("test readPrivateConfig")
            with open(filepath) as f:
                filecfg = f.readlines()
                # gdprint(filecfg)

            foundData = False
            for i, line in enumerate(filecfg):
                a = line.strip()
                # gdprint(i,a[:-1])
                if   a.startswith("#"): continue
                elif a == "":           continue
                else:
                    data = a.split(",")
                    # gdprint(data)
                    gglobs.WiFiSSID         = data[0].strip()
                    gglobs.WiFiPassword     = data[1].strip()
                    gglobs.gmcmapUserID     = data[2].strip()
                    gglobs.gmcmapCounterID  = data[3].strip()
                    # gglobs.TelegramToken    = data[4].strip()
                    # gdprint("File: '{}' : WiFiSSID:'{}' WiFiPassword:'{}' gmcmapUserID:'{}' gmcmapCounterID:'{}' TelegramToken:'{}'".\
                    #      format(filepath,
                    #             gglobs.WiFiSSID,
                    #             gglobs.WiFiPassword,
                    #             gglobs.gmcmapUserID,
                    #             gglobs.gmcmapCounterID,
                    #             gglobs.TelegramToken))
                    foundData = True
                    break

            if not foundData:
                dprint(fncname + "No data in Private file")
            else:
                if gglobs.Devices["GMC"][ACTIV]: # fill cfgKeyHigh with private data, but only if GMC is activated
                    from gdev_gmc import cfgKeyHigh
                    cfgKeyHigh["SSID"][0]           = str(gglobs.WiFiSSID)
                    cfgKeyHigh["Password"][0]       = str(gglobs.WiFiPassword)
                    cfgKeyHigh["UserID"][0]         = str(gglobs.gmcmapUserID)
                    cfgKeyHigh["CounterID"][0]      = str(gglobs.gmcmapCounterID)
                    # cfgKeyHigh["TelegramToken"][0]  = str(gglobs.TelegramToken)

                infostr = "cfg:     {:35s}: {}"
                dprint(infostr.format("SSID", gglobs.WiFiSSID))
                dprint(infostr.format("Password", gglobs.WiFiPassword))
                dprint(infostr.format("UserID", gglobs.gmcmapUserID))
                dprint(infostr.format("CounterID", gglobs.gmcmapCounterID))
                # dprint(infostr.format("TelegramToken", gglobs.TelegramToken))

                # for key in "SSID", "Password", "Website", "URL", "UserID", "CounterID", "Period", "WiFi":
                #         dprint(infostr.format(key, cfgKeyHigh[key][0]))

        except Exception as e:
            msg = fncname + "Private file could not be read"
            exceptPrint(e, msg)

    setDebugIndent(0)


def ping(host):
    """
    Returns True if host responds to a ping request.
    Remember that a host may not respond to a ping (ICMP)
    request even if the host name is valid!
    """

    # Option for the number of packets as a function of operating system
    param = '-n' if platform.system().lower()=='windows' else '-c'

    command     = ['ping', param, '1', host]    # Building the command. Ex: "ping -c 1 google.com"
    popen       = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    popencomm   = popen.communicate()
    psuccess    = (popen.returncode == 0)       # MUST come after communicate() !
    popencout   = popencomm[0].decode("utf-8")  # use stdout
    popencerr   = popencomm[1].decode("utf-8")  # use stderr
    ptime       = "time not found"
    for a in popencout.split("\n"):
        if "time=" in a: ptime = a[a.find("time="):]

    vprint("Ping stdout:\n", popencout)
    vprint("Ping stderr:\n", popencerr)

    return psuccess, ptime


def fixGarbledAudio():
    """On Linux only: fix garbled audio sound"""

    # Linux       with garbled sound and message in the terminal:
    #                 "ALSA lib pcm.c:7963:(snd_pcm_recover) underrun occurred"
    #             execute 'pulseaudio -k' as regular user (not sudo!) this should solve it

    if not "LINUX" in platform.platform().upper(): return

    fncname = "fixGarbledAudio: "

    try:
        subprocess.call(["pulseaudio", "-k"])
        msg = fncname + "executed: 'pulseaudio -k'"
        dprint(msg)
        fprint(msg)
        # raise Exception("test fixGarbledAudio")
    except Exception as e:
        msg = "Exception: failure in 'subprocess.call(pulseaudio -k)'"
        exceptPrint(e, fncname + msg)
        efprint(msg)


def setupRadWorldMap():
    """Setup Radiation World Map properties"""

    fncname = "setupRadWorldMap: "
    dprint(fncname)
    setDebugIndent(1)

    title  = "Radiation World Map Properties"

    # set properties
    retval = setRadWorldMapProperties()

    if retval == 0:
        msg = "Cancelled, properties unchanged"

    else:
        fprint(header(title))
        fprint("Activation:",           "{}"    .format("Yes" if gglobs.RWMmapActivation else "No"))
        fprint("Update Cycle:",         "{} min".format(gglobs.RWMmapUpdateCycle))
        fprint("Selected Variable:",    "{}"    .format(gglobs.RWMmapVarSelected))
        if gglobs.RWMmapActivation:
            if gglobs.RWMmapLastUpdate is None: msg = "No - will wait for expiry of update cycle time"
            else:                               msg = "Yes - will update immediately when logging"
        else:
            msg = "N/A - No Activation"

        fprint("Update immediately:",   "{}"    .format(msg))

        msg = "ok, new settings: Activation:{}, UpdateCycle:{} min, Variable:{} Update Now:{}".format(
                    gglobs.RWMmapActivation,
                    gglobs.RWMmapUpdateCycle,
                    gglobs.RWMmapVarSelected,
                    gglobs.RWMmapLastUpdate,
                )

        # Update after next log call
        if gglobs.RWMmapActivation and gglobs.RWMmapLastUpdate == 0 and not gglobs.logging:
            fprint("Currently not logging; Radiation World Map will be updated after first logging cycle")

    dprint(fncname + msg)
    setDebugIndent(0)


def setRadWorldMapProperties():
    """Set activation and cycle time"""

    fncname = "setRadWorldMapProperties: "

    lmean = QLabel("Activate Updates")
    lmean.setAlignment(Qt.AlignLeft)
    lmean.setMinimumWidth(200)

    r01=QRadioButton("Yes")
    r02=QRadioButton("No")
    r01.setToolTip("Check 'Yes' to send Updates to Radiation World Map in regular intervals")
    r02.setToolTip("Check 'No' to never send Updates to Radiation World Map")
    if gglobs.RWMmapActivation:
        r01.setChecked(True)
        r02.setChecked(False)
    else:
        r01.setChecked(False)
        r02.setChecked(True)
    powergroup = QButtonGroup()
    powergroup.addButton(r01)
    powergroup.addButton(r02)
    hbox0=QHBoxLayout()
    hbox0.addWidget(r01)
    hbox0.addWidget(r02)
    hbox0.addStretch()

    lctime = QLabel("Update Cycle Time [minutes]\n(at least 1 min)")
    lctime.setAlignment(Qt.AlignLeft)
    ctime  = QLineEdit()
    ctime.setToolTip('Enter X to update Radiation World Map every X minutes')
    ctime.setText("{:0.5g}".format(gglobs.RWMmapUpdateCycle))

    lavars = QLabel("Select Var for Map Update")
    lavars.setAlignment(Qt.AlignLeft)

    # The drop-down selector for selected variable
    avars = QComboBox()
    avars.setToolTip('The data to be selected for analysis')
    avars.setEnabled(True)
    avars.setMaxVisibleItems(12)
    for index, vname in enumerate(gglobs.varsCopy):
        avars.addItems([vname])
        if gglobs.varsSetForLog[vname]: avars.model().item(index) .setEnabled(True)
        else:                          avars.model().item(index) .setEnabled(False)

    avars.setCurrentIndex(avars.findText(gglobs.RWMmapVarSelected))


    # The checkboxes to select the displayed variables
    lckbox = QLabel("Do first update immediately")
    ckbox = QCheckBox    ()
    ckbox.setToolTip     ("A first update will be done immediately after button OK is pressed")
    ckbox.setChecked     (False)
    ckbox.setEnabled     (True)
    ckbox.setTristate    (False)

    graphOptions=QGridLayout()
    graphOptions.addWidget(lmean,          0, 0)
    graphOptions.addLayout(hbox0,          0, 1)
    graphOptions.addWidget(lctime,         1, 0)
    graphOptions.addWidget(ctime,          1, 1)
    graphOptions.addWidget(lavars,         2, 0)
    graphOptions.addWidget(avars,          2, 1)
    graphOptions.addWidget(lckbox,         3, 0)
    graphOptions.addWidget(ckbox,          3, 1)

    graphOptions.addWidget(QLabel(""),     4, 0)

    d = QDialog() # set parent to None to popup in center of screen
    d.setWindowIcon(gglobs.iconGeigerLog)
    d.setFont(gglobs.fontstd)
    d.setWindowTitle("Set up Radiation World Map")
    # d.setWindowModality(Qt.WindowModal)
    # d.setWindowModality(Qt.ApplicationModal)
    d.setWindowModality(Qt.NonModal)
    d.setMinimumWidth(300)

    bbox = QDialogButtonBox()
    bbox.setStandardButtons(QDialogButtonBox.Cancel | QDialogButtonBox.Ok )
    bbox.accepted.connect(lambda: d.done(100))
    bbox.rejected.connect(lambda: d.done(0))

    layoutV = QVBoxLayout(d)
    layoutV.addLayout(graphOptions)
    layoutV.addWidget(bbox)

    retval = d.exec()
    # print("retval:", retval)

    if retval != 0:
        # Activation
        if r01.isChecked():
            gglobs.RWMmapActivation = True
            gglobs.exgg.GMCmapAction.setIcon(QIcon(QPixmap(os.path.join(gglobs.gresPath, 'icon_world_v2.png'))))
        else:
            gglobs.RWMmapActivation = False
            gglobs.exgg.GMCmapAction.setIcon(QIcon(QPixmap(os.path.join(gglobs.gresPath, 'icon_world_v2_inactive.png'))))

        # update cycletime
        uctime = ctime.text().replace(",", ".")  #replace any comma with dot
        try:    dt  = max(round(abs(float(uctime)), 2), 0.1)
        except: dt  = gglobs.RWMmapUpdateCycle
        gglobs.RWMmapUpdateCycle = dt

        # Variable
        index = avars.currentIndex()
        text  = str(avars.currentText())
        # print("index: ", index, " text: ", text)
        gglobs.RWMmapVarSelected = text

        # Checkbox update now
        if ckbox.isChecked():   gglobs.RWMmapLastUpdate = 0
        else:                   gglobs.RWMmapLastUpdate = None

    return retval


def getRadWorldMapURL():
    """assemble the data into the url and return url and data msg"""

    fncname = "getRadWorldMapURL: "

    try:
        # raise Exception(fncname + "testing")
        DeltaT  = gglobs.RWMmapUpdateCycle   # DeltaT in minutes, RWMmapUpdateCycle in min
        cpmdata, deltaTime = getDataInLimits(gglobs.RWMmapVarSelected, DeltaT)
        # gdprint("cpmdata", cpmdata)
        # gdprint("gglobs.RWMmapVarSelected: ", gglobs.RWMmapVarSelected)
        CPM     = np.nanmean(cpmdata)
        ACPM    = CPM
        if   gglobs.RWMmapVarSelected in ("CPM",    "CPS"):         sens = gglobs.Sensitivity[0]
        elif gglobs.RWMmapVarSelected in ("CPM1st", "CPS1st"):      sens = gglobs.Sensitivity[1]
        elif gglobs.RWMmapVarSelected in ("CPM2nd", "CPS2nd"):      sens = gglobs.Sensitivity[2]
        elif gglobs.RWMmapVarSelected in ("CPM3rd", "CPS3rd"):      sens = gglobs.Sensitivity[3]
        else:                                                       sens = gglobs.NAN
        uSV     = CPM / sens

    except Exception as e:
        srcinfo = "No proper data available"
        exceptPrint(fncname + str(e), srcinfo)
        return "", srcinfo                      # blank url is used for testing

    data         = {}
    data['AID']  = gglobs.gmcmapUserID
    data['GID']  = gglobs.gmcmapCounterID
    data['CPM']  = "{:3.1f}".format(CPM)
    data['ACPM'] = "{:3.1f}".format(ACPM)
    data['uSV']  = "{:3.2f}".format(uSV)

    dmsg         = "CPM:{}  ACPM:{}  uSV:{}".format(data['CPM'],data['ACPM'],data['uSV'])

    baseURL      = gglobs.gmcmapWebsite + "/" + gglobs.gmcmapURL
    gmcmapURL    = "http://" + baseURL + "?" + urllib.parse.urlencode(data) # must use 'http://' in front!

    return gmcmapURL, dmsg


def updateRadWorldMap():
    """get a new data set and send as message to GMCmap"""

    fncname = "updateRadWorldMap: "
    title   = "Update Radiation World Map"

    dprint(fncname)
    setDebugIndent(1)

    gmcmapURL, dmsg = getRadWorldMapURL()    # gmcmapURL has the url with data as GET
    dprint(fncname + "URL:  " + gmcmapURL)
    dprint(fncname + "dmsg: " + dmsg)

    fprint(header(title))
    if gmcmapURL > "":
        try:
            fprint("Sending Data   : {}  {}".format(stime(), dmsg))
            with urllib.request.urlopen(gmcmapURL) as response:
                answer = response.read()
            dprint(fncname + "RAW Server Response: ", answer)

        except Exception as e:
            answer  = b"Bad URL"
            srcinfo = "Bad URL: " + gmcmapURL
            exceptPrint("pushToWeb: " + str(e), srcinfo)

        # remove the HTML code from answer
        cleanAnswer = "{}".format((re.sub('<[^<]+?>', '', answer.decode('UTF-8'))).strip())
        # dprint("Server Response cleaned: ", cleanAnswer)
        msg1        = "Updating got server response: '{}' ".format(cleanAnswer)
        msg2        = "on URL: {}".format(gmcmapURL)

        # Evaluate server answer
        if b"ERR0" in answer:
            # Success
            # b"ERR0" in answer     => Ok
            gglobs.exgg.addMsgToLog("Success", msg1 + msg2)
            fprint("Server Response: OK")

        else:
            # Failure
            # b"ERR1" in answer     => wrong userid
            # b"ERR2" in answer     => wrong counterid
            # b"Bad URL" in answer  => misformed URL => typo in GeigerLog config?
            # other                 => other errors, including ERR3 (when wrong url was used)
            efprint ("{} FAILURE".format(stime()))
            qefprint(msg1)
            qefprint(msg2)
            gglobs.exgg.addMsgToLog("FAILURE", msg1 + msg2)
    else:
        efprint ("{} FAILURE".format(stime()))
        qefprint(dmsg)
        gglobs.exgg.addMsgToLog("FAILURE", "Updating Radiation World Map: " + dmsg)

    setDebugIndent(0)


def getDataInLimits(varname, DeltaT):

    plotTime  = gglobs.logTime                              # plottime in days!
    # print("plotTime: ", plotTime)
    if plotTime is None : return [gglobs.NAN, gglobs.NAN]   # no database

    DeltaT_Days = DeltaT / 60 / 24                          # DeltaT in minutes => days

    plotTimeDelta = (plotTime[-1] - plotTime[0]) * 24 * 60  # Delta in min
    if plotTimeDelta > DeltaT:  plotTimeDelta = DeltaT

    # split multi-dim np.array into 12 single-dim np.arrays like log["CPM"] = [<var data>]
    log = {}
    for i, vname in enumerate(gglobs.varsCopy):
        log[vname] = gglobs.currentDBData[:, i + 1]
        # print("{}: log[{}]: {}".format(i, vname, log[vname]))

    # confine limits
    Xleft  = max(plotTime.max() - DeltaT_Days, plotTime.min())

    # find the record, where the left time limit applies
    recmin = np.where(plotTime >= Xleft )[0][0]
    # print("recmin: ", recmin)

    # slice the array
    vardata = log[varname] [recmin : ]
    # print(vardata)

    return (vardata, plotTimeDelta)


def getGeigerLogIP():
    """get the IP of the computer running GeigerLog"""

    st = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        st.connect(('10.255.255.255', 1))
        IP = st.getsockname()[0]
    except Exception as e:
        IP = '127.0.0.1'
        srcinfo = "Bad socket connect, IP:" + IP
        exceptPrint(fncname + str(e), srcinfo)
    finally:
        st.close()

    return IP


# is a socket open or not?
        # import socket
        # location = (MonServerIP, MonServerPort)
        # a_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # result_of_check = a_socket.connect_ex(location)
        # if result_of_check == 0:
        #     print("mid: Port is open")
        #     a_socket.close()
        #     # a_socket.shutdown(socket.SHUT_RDWR)
        # else:
        #     print("mid Port is not open")
        #     a_socket.close()


def blendColor(color1, color2, f):

    return 10, 100, 200
    fncname = "blendColor: "
    print(fncname + "c1, c2, f:  ", color1, color2, f)

    r1 = int(color1[1 : 3], 16)
    g1 = int(color1[3 : 5], 16)
    b1 = int(color1[5 : 7], 16)

    r2 = int(color2[1 : 3], 16)
    g2 = int(color2[3 : 5], 16)
    b2 = int(color2[5 : 7], 16)

    r = r1 + (r2 - r1) * f
    g = g1 + (g2 - g1) * f
    b = b1 + (b2 - b1) * f
    return r, g, b


def getEasyDictPrint(mydict):

    return str(mydict).replace(" ", "").replace("'", "").replace(",", " ").replace("True", TYELLOW + "True " + TGREEN)


def printLoggable(msg = ""):
    if msg > "": gdprint(msg)
    gdprint("varsSetForLog     ",     getEasyDictPrint(gglobs.varsSetForLog))
    gdprint("varsSetForHis     ",     getEasyDictPrint(gglobs.varsSetForHis))
    gdprint("varsSetForCurrent ",     getEasyDictPrint(gglobs.varsSetForCurrent))


def saveGraphToFile():
    """save the main graph to a (png) file"""

    figpath = gglobs.currentDBPath
    if figpath is None:
        gglobs.exgg.showStatusMessage("No data available")
        return

    while gglobs.plotIsBusy:
        print("Wait", end=" ", flush=True)
        pass

    pngpath = figpath + ("_" + stime() + ".png").replace(" ", "_").replace(":", "_") # change blank and : to underscore (for Windows)
    plt.savefig(pngpath)
    fprint(header("Save Graph to File"))
    msg = "The current graph was saved to file: "
    fprint(msg + "\n", pngpath)
    dprint(msg       , pngpath)


def getCRC8(data):
    """calculates 8-Bit checksum as defined by Sensirion """

    # Adapted from Sensirion code - must clip crc to 8 bit (uint8)
    # in depth: https://barrgroup.com/embedded-systems/how-to/crc-calculation-c-code
    # // Original Sensirion C code:
    # // Example:       CRC(0xBEEF) = 0x92  (dec:146)
    # // my examples:   CRC(0x0000) = 0x81  (dec:129)
    # //
    # #define CRC8_POLYNOMIAL 0x31
    # #define CRC8_INIT 0xFF

    # uint8_t sensirion_common_generate_crc(const uint8_t* data, uint16_t count) {
    #     uint16_t    current_byte;
    #     uint8_t     crc = CRC8_INIT;
    #     uint8_t     crc_bit;
    #     /* calculates 8-Bit checksum with given polynomial */
    #     for (current_byte = 0; current_byte < count; ++current_byte) {
    #         crc ^= (data[current_byte]);
    #         for (crc_bit = 8; crc_bit > 0; --crc_bit) {
    #             if (crc & 0x80)
    #                 crc = (crc << 1) ^ CRC8_POLYNOMIAL;
    #             else
    #                 crc = (crc << 1);
    #         }
    #     }
    #     return crc;
    # }

    CRC8_POLYNOMIAL = 0x31
    CRC8_INIT       = 0xFF

    count           = len(data)
    crc             = CRC8_INIT
    for dbyte in data:
        # print("dbyte: ", dbyte)
        crc = (crc ^ dbyte) & 0xFF                                  # limit to uint8
        for i in range(0, 8):
            if crc & 0x80:  crc = (crc << 1) ^ CRC8_POLYNOMIAL
            else:           crc = crc << 1
            crc = crc & 0xFF                                        # limit to uint8
            # print("i: ", i, ", crc: ", crc)

    return crc


def getSerialConfig(device):
    """
    gets the USB-to-Serial port name and baudrate for the 'device'.
    This tests for a match of USB's vid + pid associated with device. If match found,
    then it tests for proper communication checking with specific call/answers
    """

    fncname   = "getSerialConfig: " + device + ": "
    dprint(fncname)

    # ports is a list of one item per found port, like:
    # for 2 ports: [<serial.tools.list_ports_linux.SysFS object at 0x7fab98078cd0>,
    #               <serial.tools.list_ports_linux.SysFS object at 0x7fab98078d60>]
    # port attributes = ["name", "hwid", "device", "description", "serial_number", "location", "manufacturer", "product", "interface", "vid", "pid"]
    ports      = serial.tools.list_ports.comports(include_links=False)  # do NOT show symlinks
    portfound  = None
    baudfound  = None
    porttmplt  = "Checking Port: {},  device: {}, product: {}, vid: {}, pid: {}"
    foundtmplt = "Found: Port:{}, Baud:{}, description:{}, vid:0x{:02X}, pid:0x{:02X}"
    foundmatch = "Found vid + pid match"

    # getPortList(symlinks=True)

    for port in ports:
        pdevice         = "None" if port.device         is None else port.device
        pdescription    = "None" if port.description    is None else port.description
        pproduct        = "None" if port.product        is None else port.product
        pvid            = "None" if port.vid            is None else hex(port.vid)
        ppid            = "None" if port.pid            is None else hex(port.pid)
        cdprint(fncname + porttmplt.format(pdevice, pdescription, pproduct, pvid, ppid))

        if device == "GMC":
            if  port.vid == 0x1a86 and port.pid == 0x7523:
                cdprint(fncname, foundmatch)
                from gdev_gmc import GMCautoBaudrate
                baudrate = GMCautoBaudrate(port.device)
                if baudrate is not None and baudrate > 0:
                    portfound = port.device
                    baudfound = baudrate
                    break

        elif device == "GS":
            # The chip doing the conver­sion between USB and Serial signals is an
            # FTDI chip (Vendor=0x0403, Product=0xd678).
            # lsusb output: https://www.johannes-bauer.com/linux/gammascout/
            #   bcdUSB               2.00
            #   idVendor           0x0403 Future Technology Devices International, Ltd
            #   idProduct          0xd678
            #   iManufacturer           1 Dr Mirow
            #   iProduct                2 GammaScout USB
            if  port.vid == 0x0403 and port.pid == 0xd678:
                cdprint(fncname, foundmatch)
                from gdev_gscout import GSautoBaudrate
                baudrate = GSautoBaudrate(port.device)
                if baudrate is not None and baudrate > 0:
                    portfound = port.device
                    baudfound = baudrate
                    break

        elif device == "ELV":
            if  port.vid == 0x10C4 and port.pid == 0xEA60:
                cdprint(fncname, foundmatch)
                from gdev_i2c import I2CautoBaudrate
                baudrate = I2CautoBaudrate(port.device)
                if baudrate is not None and baudrate > 0:
                    portfound = port.device
                    baudfound = baudrate
                    break

        elif device == "ISS":
            if  port.vid == 0x04D8 and port.pid == 0xFFEE:
                cdprint(fncname, foundmatch)
                from gdev_i2c import I2CautoBaudrate
                baudrate = I2CautoBaudrate(port.device)
                if baudrate is not None and baudrate > 0:
                    portfound = port.device
                    baudfound = baudrate
                    break

        if portfound is not None: gdprint(fncname + foundtmplt.format(portfound, baudfound, port.description, port.vid, port.pid))

    # edprint(fncname + "Returning: ", (portfound, baudfound))
    return (portfound, baudfound)


def autoPORT(device):
    """
    device is:  "GMC", or "I2C", or "GS"

    Tries to find a working port and baudrate by testing all serial
    ports for successful communication by auto discovery of baudrate.
    All available ports will be listed with the highest baudrate found.
    Ports are found as:
        /dev/ttyS0 - ttyS0              # a regular serial port
        /dev/ttyUSB0 - USB2.0-Serial    # a USB-to-Serial port
    """

    if   device == "GMC":   import gdev_gmc
    elif device == "I2C":   import gdev_i2c
    elif device == "GS":    import gdev_gscout

    fncname = "autoPORT: "
    dprint(fncname + "Autodiscovery of USB-to-Serial Ports")
    setDebugIndent(1)

    time.sleep(0.5) # a freshly plugged in device, not fully recognized
                    # by system, sometimes produces errors

    lp = getPortList(symlinks=False)    # get a list of all ports, but ignore symlinks

    if len(lp) == 0:
        errmessage = "FAILURE: No available serial ports found"
        dprint(fncname + errmessage, debug=True)
        setDebugIndent(0)
        return None, "Autodiscover " + errmessage

    dprint(fncname + "Found these ports:", debug=True)
    ports =[]
    for p in lp :
        dprint("   ", p, debug=True)
        ports.append(str(p).split(" ",1)[0])
    ports.sort()
    ports_found = []

    includeFlag = False
    if   device == "GMC":   includeFlag = True if gglobs.GMC_ttyS == 'include' else False
    elif device == "I2C":   includeFlag = True if gglobs.I2CttyS  == 'include' else False
    elif device == "GS":    includeFlag = True if gglobs.GSttyS   == 'include' else False

    dprint(fncname + "Testing all ports for communication:", debug=True)
    for port in ports:
        dprint(fncname + "Port:", port, debug=True)
        if "/dev/ttyS" in port:
            if includeFlag: dprint(fncname + "Include Flag is set for port: '{}'".format(port), debug=True)
            else:
                            dprint(fncname + "Ignore Flag is set for port: '{}'".format(port), debug=True)
                            continue

        if   device == "GMC":   abr = gdev_gmc.     GMCautoBaudrate(port)
        elif device == "I2C":   abr = gdev_i2c.     I2CautoBaudrate(port)
        elif device == "GS":    abr = gdev_gscout.  GSautoBaudrate(port)

        if   abr == None:   dprint(fncname + "ERROR: Failure during Serial Communication on port: '{}'".format(port), debug=True)
        elif abr == 0:      dprint(fncname + "Failure - no communication at any baudrate on port: '{}'".format(port), debug=True)
        elif abr >  0:      ports_found.append((port, abr))

    if len(ports_found) == 0:
        errmessage = "ERROR: No communication at any serial port and baudrate"
        ports_found = None
    else:
        errmessage = ""

    if errmessage > "": dprint(fncname + errmessage)
    setDebugIndent(0)

    return ports_found, errmessage


def autoDiscoverUSBPort(device):
    """USB Autodiscovery with option to select any found connection.
    device: GMC, GS, I2C"""

    fncname = "autoDiscoverUSBPort: "

    if gglobs.logging :
        msg = "Cannot autodiscover when logging! Stop logging first"
        gglobs.exgg.showStatusMessage(msg)
        dprint(fncname + msg)
        return

    windowTitle = "Autodiscover Port for Device:  '{}'".format(device)
    critical    = """                            C A U T I O N !

This discovery will write-to and read-from all available USB-to-Serial ports.

If any other program is communicating with these devices at the same time, both program and devices may be severely disturbed!

Note that this applies ONLY to USB-to-Serial port connections. Any other native USB de­vices (mouse, keyboard, printer, ...) won’t be impacted by the discovery!

It is advisable to stop all those other activities for the duration of this discovery, but leave the cables connected.

All devices under GeigerLog's control will automatically be disconnected by GeigerLog before the test starts.

Click OK to proceed with the discovery, otherwise click Cancel.
    """

    msg = QMessageBox()
    msg.setIcon(QMessageBox.Critical)
    msg.setWindowTitle(windowTitle)
    msg.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
    msg.setDefaultButton(QMessageBox.Cancel)
    msg.setEscapeButton(QMessageBox.Cancel)
    msg.setText(critical)

    if msg.exec() != 1024:      return

    dprint(fncname + "device: '{}'".format(device))
    setDebugIndent(1)

    # disconnect everything if anything is connected
    if gglobs.DevicesConnected > 0:
        gglobs.exgg.switchAllConnections(new_connection = "OFF")
        Qt_update()

    setBusyCursor()
    rec, errmessage = autoPORT(device)
    setNormalCursor()

    if rec == None:
        flag = "fail"
        txt1 = errmessage + "\n\nIs device connected? Check cable and plugs! Re-run in a few seconds."
    else:
        if len(rec) == 1:
            flag  = "success"
            txt1  = "A device '{}' was found at:\n".format(device)
            txt1 += "\n     Port: {:20s}  \tBaudrate: {}".format(rec[0][0], rec[0][1])
            txt1 += "\n\nPress OK to make this your new setting and connect, Cancel otherwise."
            txt1 += "\n\nTo make this permanent, edit the configuration file geigerlog.cfg\nand enter above settings in respective SerialPort section."

        else:
            flag  = "fail"
            txt1  = "The following ports and baudrates have connected devices:\n"
            for i in rec: txt1 += "\n     Port: {:20s}  \tBaudrate: {}".format(i[0], i[1])
            txt1 += "\n\nGeigerLog can handle only a single connected device of each type."
            txt1 += "\n\nEither remove all devices except one now and re-run 'USB Autodiscovery', or "
            txt1 += "edit the configuration file geigerlog.cfg in the respective Serial Port section to define your device."


    txt2  = "-" * 100
    txt2 += "\nThe current settings of GeigerLog for device '{}' are: \n".format(device)
    if   device == "GMC":   txt2 += "\n     Port: {:20s}  \tBaudrate: {}".format(str(gglobs.GMC_usbport), gglobs.GMC_baudrate)
    elif device == "GS":    txt2 += "\n     Port: {:20s}  \tBaudrate: {}".format(str(gglobs.GSusbport),   gglobs.GSbaudrate)
    elif device == "I2C":   txt2 += "\n     Port: {:20s}  \tBaudrate: {}".format(str(gglobs.I2Cusbport),  gglobs.I2Cbaudrate)

    msg = QMessageBox(gglobs.exgg)
    msg.setWindowTitle(windowTitle)
    msg.setIcon(QMessageBox.Information)
    msg.setWindowIcon(gglobs.iconGeigerLog)
    msg.setDefaultButton(QMessageBox.Cancel)
    msg.setEscapeButton (QMessageBox.Cancel)
    if flag == "fail":      msg.setStandardButtons(QMessageBox.Cancel)
    else:                   msg.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)

    msg.setText(txt1)
    msg.setInformativeText(txt2)

    if msg.exec() == 1024:
        dprint(fncname + "Accepting autodiscovered port settings; connecting now")
        if   device == "GMC":   gglobs.GMC_usbport, gglobs.GMC_baudrate = str(rec[0][0]), str(rec[0][1])
        elif device == "GS":    gglobs.GSusbport,   gglobs.GSbaudrate   = str(rec[0][0]), str(rec[0][1])
        elif device == "I2C":   gglobs.I2Cusbport,  gglobs.I2Cbaudrate  = str(rec[0][0]), str(rec[0][1])
        gglobs.exgg.switchAllConnections(new_connection = "ON")
    else:
        if flag != "fail": dprint(fncname + "User not accepting autodiscovered port settings; cancelling now")

    setDebugIndent(0)


def getPortList(symlinks=True):
    """print serial port details. Include symlinks or not"""

    # Pyserial:
    # 'include_links (bool)' – include symlinks under /dev when they point to a serial port
    # symlinks=False: symlinks NOT shown, default
    # symlinks=True:  symlinks shown, like /dev/geiger
    # https://github.com/pyserial/pyserial/blob/master/documentation/tools.rst

    # #
    # # on Linux
    # #
    # # GMC-300E+
    # /dev/ttyUSB0 - USB Serial
    #     p.name           : ttyUSB0
    #     p.hwid           : USB VID:PID=1A86:7523 LOCATION=3-1
    #     p.device         : /dev/ttyUSB0
    #     p.description    : USB Serial
    #     p.serial_number  : None
    #     p.location       : 3-1
    #     p.manufacturer   : None
    #     p.product        : USB Serial
    #     p.interface      : None
    #     p.vid            :  6790 (0x1A86)
    #     p.pid            : 29987 (0x7523)

    # # GMC-500+
    # /dev/ttyUSB1 - USB2.0-Serial
    #     p.name           : ttyUSB1
    #     p.hwid           : USB VID:PID=1A86:7523 LOCATION=3-1
    #     p.device         : /dev/ttyUSB1
    #     p.description    : USB2.0-Serial
    #     p.serial_number  : None
    #     p.location       : 3-1
    #     p.manufacturer   : None
    #     p.product        : USB2.0-Serial
    #     p.interface      : None
    #     p.vid            :  6790 (0x1A86)
    #     p.pid            : 29987 (0x7523)


    # /dev/ttyACM0 - USB-ISS.
    #     p.name           : ttyACM0
    #     p.hwid           : USB VID:PID=04D8:FFEE SER=00027171 LOCATION=3-11:1.0
    #     p.device         : /dev/ttyACM0
    #     p.description    : USB-ISS.
    #     p.serial_number  : 00027171
    #     p.location       : 3-11:1.0
    #     p.manufacturer   : Devantech Ltd.
    #     p.product        : USB-ISS.
    #     p.interface      : None
    #     p.vid            :  1240 (0x04D8)
    #     p.pid            : 65518 (0xFFEE)

    # /dev/ttyUSB0 - ELV USB-I2C-Interface - ELV USB-I2C-Interface
    #     p.name           : ttyUSB0
    #     p.hwid           : USB VID:PID=10C4:EA60 SER=TL4E6D5KBAHDFQF0 LOCATION=3-1
    #     p.device         : /dev/ttyUSB0
    #     p.description    : ELV USB-I2C-Interface - ELV USB-I2C-Interface
    #     p.serial_number  : TL4E6D5KBAHDFQF0
    #     p.location       : 3-1
    #     p.manufacturer   : Silicon Labs
    #     p.product        : ELV USB-I2C-Interface
    #     p.interface      : ELV USB-I2C-Interface
    #     p.vid            :  4292 (0x10C4)
    #     p.pid            : 60000 (0xEA60)

    # #
    # # on windows
    # #
    # # gmc-500+
    # COM3 - USB-SERIAL CH340 (COM3)
    #     p.name           : COM3
    #     p.hwid           : USB VID:PID=1A86:7523 SER= LOCATION=1-1.4
    #     p.device         : COM3
    #     p.description    : USB-SERIAL CH340 (COM3)
    #     p.serial_number  :
    #     p.location       : 1-1.4
    #     p.manufacturer   : wch.cn
    #     p.product        : None
    #     p.interface      : None
    #     p.vid            :  6790 (0x1A86)
    #     p.pid            : 29987 (0x7523)

    # # gmc-300E+
    # COM3 - USB-SERIAL CH340 (COM3)
    #     p.name           : COM3
    #     p.hwid           : USB VID:PID=1A86:7523 SER= LOCATION=1-1.4
    #     p.device         : COM3
    #     p.description    : USB-SERIAL CH340 (COM3)
    #     p.serial_number  :
    #     p.location       : 1-1.4
    #     p.manufacturer   : wch.cn
    #     p.product        : None
    #     p.interface      : None
    #     p.vid            :  6790 (0x1A86)
    #     p.pid            : 29987 (0x7523)

    # # ELV
    # COM7 - Silicon Labs CP210x USB to UART Bridge (COM7)
    #     p.name           : COM7
    #     p.hwid           : USB VID:PID=10C4:EA60 SER=TL4E6D5KBAHDFQF0 LOCATION=1-1.4
    #     p.device         : COM7
    #     p.description    : Silicon Labs CP210x USB to UART Bridge (COM7)
    #     p.serial_number  : TL4E6D5KBAHDFQF0
    #     p.location       : 1-1.4
    #     p.manufacturer   : Silicon Labs
    #     p.product        : None
    #     p.interface      : None
    #     p.vid            :  4292 (0x10C4)
    #     p.pid            : 60000 (0xEA60)


    # # USB-ISS
    # COM8 - Serielles USB-Gerät (COM8)
    #     p.name           : COM8
    #     p.hwid           : USB VID:PID=04D8:FFEE SER=00027171 LOCATION=1-1.2
    #     p.device         : COM8
    #     p.description    : Serielles USB-Gerät (COM8)
    #     p.serial_number  : 00027171
    #     p.location       : 1-1.2
    #     p.manufacturer   : Microsoft
    #     p.product        : None
    #     p.interface      : None
    #     p.vid            :  1240 (0x04D8)
    #     p.pid            : 65518 (0xFFEE)


    if symlinks:    msg = "(with symlinks)"
    else:           msg = "(without symlinks)"
    fncname = "getPortList: " + msg
    dprint(fncname)
    setDebugIndent(1)

    lp = [] # define in case serial.tools.list_ports.comports fails
    try:
        lp = serial.tools.list_ports.comports(include_links=symlinks)
    except Exception as e:
        msg = fncname + "lp: {}".format(lp)
        exceptPrint(e, msg)
    lp.sort()       # sorted by device

    ######## TESTING only ##############
    #    lp.append("/dev/ttyS0 - ttyS0")    # add a ttyS* to the list of ports
    ####################################

    # only devel printout
    if gglobs.devel:
        # complete list of attributes for serial.tools.list_ports.comports()
        lpAttribs = ["device", "name", "hwid", "description", "serial_number", "location", "manufacturer", "product", "interface", "vid", "pid"]
        try:
            cdprint("Ports detected:")
            for p in lp:    cdprint("   ",  p)
            if len(lp) == 0:    cdprint("   None")
            cdprint()

            for p in lp:
                cdprint(p)
                for pA in lpAttribs:
                    if pA == "vid" or pA == "pid":
                        x = getattr(p, pA, 0)
                        if x is None:   cdprint("   {:16s} : None".format("p." + pA))
                        else:           cdprint("   {:16s} : {:5d} (0x{:04X})".format("p." + pA, x, x))
                    else:
                        cdprint("   {:16s} : {}".format("p." + pA, getattr(p, pA, "None")))
                cdprint()
        except Exception as e:
            msg = fncname + "lp: {}".format(lp)
            exceptPrint(e, msg)

    setDebugIndent(0)
    return lp

