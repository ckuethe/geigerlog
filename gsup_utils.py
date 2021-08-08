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
__copyright__       = "Copyright 2016, 2017, 2018, 2019, 2020, 2021"
__credits__         = [""]
__license__         = "GPL3"

# BOM for UTF-8 Files ???
# For example, a file with the first three bytes 0xEF,0xBB,0xBF is probably a
# UTF-8 encoded file. However, it might be an ISO-8859-1 file which happens to
# start with the characters ï»¿. Or it might be a different file type entirely.

# modules available in std Python
import sys, os, io, time, datetime  # basic modules
import platform                     # info on OS, machine, architecture, ...
import traceback                    # for traceback on error; used in: exceptPrint
import inspect                      # findinf origin of f'on calls
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

# modules requiring installation via pip
#~import serial                       # serial port (module has name: 'pyserial'!)
#~import serial.tools.list_ports      # allows listing of serial ports
#~import paho.mqtt.client  as mqtt  # needed only by RadMon, installed in gdev_radmon.py
import sounddevice       as sd      # sound output input
import soundfile         as sf      # handling sound files; can read and write
import numpy             as np      # scientific computing with Python
import scipy.signal                 # a subpackage of scipy; needs separate import
import scipy.stats                  # a subpackage of scipy; needs separate import
import matplotlib                   # Visualization with Python

# matplotlib settings
matplotlib.use('Qt5Agg', force=False)           # use Qt5Agg, not the default TkAgg
import matplotlib.backends.backend_qt5agg       # MUST be done BEFORE importing pyplot!
from   matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg    as FigureCanvas
from   matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
import matplotlib.pyplot    as plt                 # MUST import AFTER 'matplotlib.use()'
import matplotlib.dates     as mpld
import matplotlib.animation as mplanim


# next lines are better done in other code,
# https://www.delftstack.com/de/howto/matplotlib/how-to-plot-and-save-a-graph-in-high-resolution/
# matplotlib.pyplot.figure(num=None, figsize=None, dpi=None, ...)
# dpi ersetzen mit dpi of current screen, see geigerlog lines ~370

#~print(matplotlib.rcParams['figure.figsize'])
#~print(matplotlib.rcParams['figure.dpi'])
#~print(matplotlib.rcParams['savefig.dpi'])
#~print(matplotlib.rcParams['font.size'])
#~print(matplotlib.rcParams['legend.fontsize'])
#~print(matplotlib.rcParams['figure.titlesize'])

#~matplotlib.rcParams['figure.figsize'] = [8.0, 6.0]
#~matplotlib.rcParams['figure.dpi'] = 50
#~matplotlib.rcParams['savefig.dpi'] = 100
#~matplotlib.rcParams['font.size'] = 12
#~matplotlib.rcParams['legend.fontsize'] = 'large'
#~matplotlib.rcParams['figure.titlesize'] = 'medium'

#~print(matplotlib.rcParams['figure.figsize'])
#~print(matplotlib.rcParams['figure.dpi'])
#~print(matplotlib.rcParams['savefig.dpi'])
#~print(matplotlib.rcParams['font.size'])
#~print(matplotlib.rcParams['legend.fontsize'])
#~print(matplotlib.rcParams['figure.titlesize'])

# PyQt install via pip, but sometimes via distribution package manager
from PyQt5.QtWidgets            import *
from PyQt5.QtGui                import *
from PyQt5.QtCore               import *
from PyQt5.QtPrintSupport       import *

import gglobs                       # all global vars


# colors for the terminal (do not put in gglobs, as this would require 'gglobs.' prefix!)
# https://gist.github.com/vratiu/9780109
TCYAN               = '\033[96m'            # cyan
TPURPLE             = '\033[95m'            # purple (dark)
TBLUE               = '\033[94m'            # blue (dark)
TRED                = '\033[91m'            # red
TDEFAULT            = '\033[0m'             # default, i.e greyish
TGREEN              = '\033[92m'            # light green
TYELLOW             = '\033[93m'            # yellow
BOLD                = '\033[1m'             # white (bright default)
UNDERLINE           = '\033[4m'             # underline
BOLDREDUL           = '\033[31;1;4m'        # bold, red, underline
BOLDRED             = '\033[31;1m'          # bold, red - but is same as TRED

if "WINDOWS" in platform.platform().upper(): # no terminal colors on Windows
    TDEFAULT = ""   # normal printout
    TGREEN   = ""   # hilite message
    TYELLOW  = ""   # error message

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
    # sollte auch damit gehen: return time.strftime("%Y-%m-%d %H:%M:%S")

    return longstime()[:-4]


def longstime():
    """Return current time as YYYY-MM-DD HH:MM:SS.mmm, (mmm=millisec)"""

    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3] # ms resolution


def datestr2num(string_date):
    """convert a Date&Time string in the form YYYY-MM-DD HH:MM:SS to a Unix
    timestamp in sec"""

    #print("datestr2num: string_date", string_date)
    try:    dt=time.mktime(datetime.datetime.strptime(string_date, "%Y-%m-%d %H:%M:%S").timetuple())
    except: dt = 0

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

    return "<br>==== {} {}".format(txt, "=" * max(0, (80 - len(txt))))


def logPrint(*args):
    """print all args in logPad area"""
    # NOTE: presently only the 1st argument will ever be requested

    line = "{:35s}".format(args[0])
    #for s in range(1, len(args)):   line += "{}".format(args[s])

    gglobs.logPad.append(line)


def efprint(*args, debug=False):
    """error fprint with err sound"""

    fprint(*args, error=True, debug=debug, errsound=True)


def qefprint(*args, debug=False):
    """quiet error fprint, error color but no errsound"""

    fprint(*args, error=True, debug=debug, errsound=False)


def fprint(*args, error=False, debug=False, errsound=False):
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
                                          # cursor on most-right position is visible
                                          # requires moving text to left; not helpful
    gglobs.notePad.verticalScrollBar().setValue(gglobs.notePad.verticalScrollBar().maximum())

    # on error print in red
    if error:   gglobs.notePad.append("<span style='color:red;'>" + ps + "</span>")
    else:
        gglobs.notePad.setFont(gglobs.fontstd)
        gglobs.notePad.setTextColor(QColor(40, 40, 40))
        gglobs.notePad.append(ps)

    dprint(ps.replace("&nbsp;", ""), debug=debug)


def commonPrint(ptype, *args, error=False):
    """Printing function to dprint, vprint, and wprint"""

    gglobs.xprintcounter += 1   # the count of dprint, vprint, wprint commands
    tag = "{:23s} {:7s}: {:.>6d} ".format(longstime(), ptype, gglobs.xprintcounter) + gglobs.debugIndent

    for arg in args: tag += str(arg)

    # last resort: "\x00" in text files results in geany (and other) not being able to open the file
    if "\x00" in tag: tag = tag.replace("\x00", "\x01")

    writeFileA(gglobs.proglogPath, tag)

    if not gglobs.redirect:  tag = tag[11:]
    if error:                tag = TYELLOW + tag + TDEFAULT

    print(tag)


def wprint(*args, werbose=None):
    """werbose print:
    if werbose is true then:
    - Write timestamp and args as a single line to progname.proglog file
    - Print args as single line
    else
    - do nothing
    """
    if werbose == None: werbose = gglobs.werbose
    if werbose:         commonPrint("werbose", *args)


def vprint(*args, verbose=None):
    """verbose print:
    if verbose is true then:
    - Write timestamp and args as a single line to progname.proglog file
    - Print args as single line
    else
    - do nothing
    """
    if verbose == None: verbose = gglobs.verbose
    if verbose:         commonPrint("VERBOSE", *args)


def dprint(*args, debug=None ):
    """debug print:
    if debug is true then:
    - Write timestamp and args as a single line to progname.proglog file
    - Print args as single line
    else
    - do nothing
    """
    if debug == None:   debug = gglobs.debug
    if debug:           commonPrint("DEBUG", *args)


def edprint(*args, debug=True):
    """edebug print:
    - Write timestamp and args as a single line to progname.proglog file
    - Print args as single line
    """
    commonPrint("DEBUG", *args, error=True)


def arrprint(text, array):
    """ prints an array """

    print(text)
    for a in array: print("{:10s}: ".format(a), array[a])


def exceptPrint(e, srcinfo):
    """Print exception details (errmessage, file, line no)"""

    exc_type, exc_obj, exc_tb = sys.exc_info()
    fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]    # which file?

    edprint("EXCEPTION: '{}' in file: '{}' in line {}".format(e, fname, exc_tb.tb_lineno))
    if srcinfo > "": edprint("{}".format(srcinfo), debug=True)
    if gglobs.redirect:
        edprint("EXCEPTION: Traceback:\n", traceback.format_exc(), debug=True) # more extensive info


def setDebugIndent(arg):
    """increases or decreased the indent of debug/verbose print"""

    if arg > 0:  gglobs.debugIndent += "   "
    else:        gglobs.debugIndent  = gglobs.debugIndent[:-3]


def cleanHTML(text):
    return str(text).replace("<", "").replace(">", "") # replace < and >


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

    print(TGREEN + line + TDEFAULT)         # goes to terminal  (and *.stdlog)
    writeFileW(gglobs.proglogPath, line )   # goes to *.proglog (and *.stdlog)


def readBinaryFile(path):
    """Read all of the file into data; return data as bytes"""

    #print("readBinaryFile: path: {} ".format(path))

    data = b''

    try:
        with open(path, 'rb') as f:
            data = f.read()
    except Exception as e:
        srcinfo = "ERROR reading file"
        exceptPrint("readBinaryFile: " + str(e), srcinfo)
        data = b"ERROR: Could not read file: " + str.encode(path)

    vprint("readBinaryFile: type:{}, len:{}, data=[:100]:".format(type(data), len(data)), data[0:100])

    return data


def writeBinaryFile(path, data):
    """Create file and write data to it as binary"""

    #print("writeBinaryFile: path: {}  data: not shown".format(path))

    with open(path, 'wb') as f:
        f.write(data)


def writeFileW(path, writestring, linefeed = True):
    """Create file if not available, and write to it if writestring
    is not empty; add linefeed unless excluded"""

    #print("writeFileW: path: {}  writestring: {}  linefeed: {}".format(path, writestring, linefeed))

    with open(path, 'wt', encoding="UTF-8", errors='replace', buffering = 1) as f:
        if writestring > "":
            if linefeed: writestring += "\n"
            f.write(writestring)


def writeFileA(path, writestring):
    """Write-Append data; add linefeed"""

    #print("writeFileA: path: {}  writestring: {}".format(path, writestring))

    with open(path, 'at', encoding="UTF-8", errors='replace', buffering = 1) as f:
        f.write((writestring + "\n"))


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
    # interpreted as HTML such than an b'<GETCPML>>' becomes an b'>' !

    html_escape_table = {
        "&": "&amp;",
        '"': "&quot;",
        "'": "&apos;",
        ">": "&gt;",
        "<": "&lt;",
        }

    return "".join(html_escape_table.get(c,c) for c in text)


def getOrderedVars(varlist):
    """Prints a dict in the right order"""

    ret = ""
    for vname in gglobs.varsDefault:
        ret += "{:>8s}:{:5s}".format(vname, str(varlist[vname])).strip() + "  "

    return ret


def getNameSelectedVar():
    """Get the name of the variable currently selected in the drop-down box in
    the graph options"""

    vindex      = gglobs.exgg.select.currentIndex()
    vnameselect = list(gglobs.varsBook)[vindex]
    #print("getNameSelectedVar: vindex, vnameselect:", vindex, vnameselect)

    return vnameselect


def getVersionStatus():
    """returns versions as list of various components"""

    """
    # Getting the version numbers of Qt, SIP and PyQt:
    # https://wiki.python.org/moin/PyQt/Getting%20the%20version%20numbers%20of%20Qt%2C%20SIP%20and%20PyQt

    sqlite3.version:                The version number of this module, as a string. This is not the version of the SQLite library.
    sqlite3.version_info:           The version number of this module, as a tuple of integers. This is not the version of the SQLite library.
    sqlite3.sqlite_version:         The version number of the run-time SQLite library, as a string.
    sqlite3.sqlite_version_info:    The version number of the run-time SQLite library, as a tuple of integers.
    """

    python_version = sys.version.replace('\n', "")

    from pip            import __version__          as pip_version
    from setuptools     import __version__          as setuptools_version
    from sip            import SIP_VERSION_STR
    from matplotlib     import __version__          as mpl_version
    from numpy          import __version__          as np_version
    from scipy          import __version__          as scipy_version
    from serial         import __version__          as serial_version     # alternartive  serial_version = serial.VERSION
    from paho.mqtt      import __version__          as paho_version

    from sqlite3        import version              as sql3version
    from sqlite3        import sqlite_version       as sql3libversion

    version_status = []
    version_status.append(["GeigerLog",         "{}".format(gglobs.__version__)])

    version_status.append(["Python",            "{}".format(sys.version.replace('\n', ""))])
    version_status.append(["pip",               "{}".format(pip_version)])
    version_status.append(["setupttools",       "{}".format(setuptools_version)])

    version_status.append(["PyQt",              "{}".format(PYQT_VERSION_STR)])
    version_status.append(["PyQt-Qt",           "{}".format(QT_VERSION_STR)])
    version_status.append(["PyQt-sip",          "{}".format(SIP_VERSION_STR)])

    version_status.append(["pyserial",          "{}".format(serial_version)])
    version_status.append(["matplotlib",        "{}".format(mpl_version)])
    version_status.append(["matplotlib backend","{}".format(matplotlib.get_backend())])
    version_status.append(["numpy",             "{}".format(np_version)])
    version_status.append(["numpy err handling","{}".format(np.geterr())])
    version_status.append(["scipy",             "{}".format(scipy_version)])
    version_status.append(["paho.mqtt",         "{}".format(paho_version)])
    version_status.append(["sounddevice",       "{}".format(sd.__version__)])
    version_status.append(["SoundFile",         "{}".format(sf.__version__)])
    version_status.append(["PortAudio",         "{} - {}".format(sd.get_portaudio_version()[0], sd.get_portaudio_version()[1])])

    # sqlite3 stuff
    version_status.append(["sqlite3 module",    "{}".format(sql3version)])
    version_status.append(["sqlite3 library",   "{}".format(sql3libversion)])

    # LabJack stuff
    version_status.append(["LabJackPython",     "{}".format(gglobs.LJversionLJP)])
    version_status.append(["U3",                "{}".format(gglobs.LJversionU3)])
    version_status.append(["EI1050",            "{}".format(gglobs.LJversionEI1050)])

    return version_status


def beep():
    """do a system beep"""

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
        status = sd.wait()
    except Exception as e:
        exceptPrint(e, "playWav failed")


def playSine():

#testing play sine wave:
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


def playClick():
    """play a Geiger counter like click sound"""

    # play sine wave
    samplerate = 44100              # samples per sec
    sounddur   = 0.01               # seconds
    soundfreq  = 1000 #1440         # 440Hz = Kammerton A
    soundamp   = 0.3                # amplitude; mit steigender Amplitude Verzerrungen 1.0 may be max?

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
    """play a Geiger counter like click sound"""

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

    scale = scale.strip().upper() # make sure it is upper

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
    ls = ls.replace("INT",    "int")          # integer value

    #print(fncname + "scaling variable:'{}' value:'{}', scale: {}".format(variable, value, scale))

    try:
        scaledValue = eval(ls)

    except Exception as e:
        msg  = "ERROR scaling Values: variable:'{}'<br>".format(variable)
        msg += "ERROR scaling Values: formula: '{}'<br>".format(scale)
        msg += "ERROR scaling Values: errmsg:  '{}'<br>".format(e)
        msg += "Continuing with original value<br>"
        exceptPrint(e, msg)
        efprint(msg)
        scaledValue = value

    #wprint("scaleVarValues: variable:{}, original value:{}, orig scale:{}, mod scale:'{}', scaled value:{}".format(variable, value, scale, ls, scaledValue))

    return np.round(scaledValue, 2) # is rounding necessary?


def readSerialConsole():
    """read the ESP32 terminal output"""

    return # results in problems when GMC counter is connected

    mypath = os.path.join(gglobs.dataPath, "esp32.termlog")
    dv  = "/dev/ttyUSB0" # device
    br  = 115200         # baudrate
    to  = 3              # timeout
    wto = 1              # write timeout
    byteswaiting = 0     # to avoid reference error

    if gglobs.terminal == None:
        gglobs.terminal = serial.Serial(dv, br, timeout=to, write_timeout=wto)
        with open(mypath, 'wt', encoding="UTF-8", errors='replace', buffering = 1) as f:
            f.write("Starting at: {}\n".format(longstime()))

    else:
        #while gglobs.terminal.in_waiting > 0:
        while True:
            try:
                bytesWaiting = gglobs.terminal.in_waiting
            except Exception as e:
                print("problem in byteswaiting, re-openeing terminal")
                gglobs.terminal.close()
                gglobs.terminal = serial.Serial(dv, br, timeout=to, write_timeout=wto)
            if bytesWaiting == 0: break

            #print("bytes waiting before readline: ", gglobs.terminal.in_waiting)
            try:
                rec    = gglobs.terminal.readline(500)
            except:
                rec = "exception readline"

            #print("bytes waiting after  readline: ", gglobs.terminal.in_waiting)
            try:
                rec = rec.decode('UTF-8')
            except Exception as e:
                print("can't decode.", end=" ")
                rec = str(rec)
                print("Re-opening terminal ... ", end="  ")
                gglobs.terminal.close()
                gglobs.terminal = serial.Serial(dv, br, timeout=to, write_timeout=wto)
                print("Done")

            if rec[-1] != "\n": rec += "\n" # add a linefeed if needed

            # print
            print("ESP32 b waiting: {:6d} : ".format(bytesWaiting), rec, end="")

            # save
            with open(mypath, 'at', encoding="UTF-8", errors='replace', buffering = 1) as f:
                f.write(rec)

        #print("Done")
        print()


# making a label click-sensitive
class ClickLabel(QLabel):
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
        gglobs.varsBook[vname][3] = color.name()
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


def getPortList(symlinks=True):
    """print serial port details. Include symlinks or not"""

    # Pyserial:
    # 'include_links (bool)' – include symlinks under /dev when they point to a serial port
    # https://github.com/pyserial/pyserial/blob/master/documentation/tools.rst
    #
    # lp = serial.tools.list_ports.comports(include_links=True)  # also shows e.g. /dev/geiger
    # lp = serial.tools.list_ports.comports(include_links=False) # default; no symlinks shown
    #
    # include_links gibt einen Fehler bei pyserial version pyserial: 3.0.1
    # print("serial.tools.list_ports:", serial.tools.list_ports)
    # print("serial.tools.list_ports:", serial.tools.list_ports.comports())

    import serial                       # serial port (module has name: 'pyserial'!)
    import serial.tools.list_ports      # allows listing of serial ports

    fncname = "getPortList: "

    wprint(fncname + "use symlinks: ", symlinks)
    setDebugIndent(1)

    try:
        if symlinks:    lp = serial.tools.list_ports.comports(include_links=True)  # symlinks shown
        else:           lp = serial.tools.list_ports.comports(include_links=False) # default; no symlinks shown
        lp.sort()
    except Exception as e:
        msg = fncname + "lp: {}".format(lp)
        exceptPrint(e, msg)
        dprint(fncname + "Exception: ", e, debug=True)
        dprint(fncname + "lp: ", lp, debug=True)
        lp = []

######## TESTING only ##############
#    lp.append("/dev/ttyS0 - ttyS0")    # add a ttyS* to the list of ports
####################################

# only Werbose printout
    lpAttribs = ["name", "hwid", "device", "description", "serial_number", "location", "manufacturer", "product", "interface", "vid", "pid"]
    try:
        wprint(fncname)
        for p in lp:    wprint("   ", p)
        wprint()

        for p in lp:
            wprint(fncname, p)
            for pA in lpAttribs:
                if pA == "vid" or pA == "pid":
                    x = getattr(p, pA, 0)
                    if x is None:   wprint("   {:16s} : None".format("p." + pA))
                    else:           wprint("   {:16s} : {:5d} (0x{:04X})".format("p." + pA, x, x))
                else:
                    wprint("   {:16s} : {}".format("p." + pA, getattr(p, pA, "None")))
            wprint()
    except Exception as e:
        dprint(fncname + "Exception: ", e , debug=True)
        dprint(fncname + "lp:        ", lp, debug=True)

    setDebugIndent(0)
    return lp



def executeTPUT(action = 'clean'):
    """set terminal output with or without linebreaks; works in Linux only
    use action = 'clean' or 'set'
    """
    # For generic non full screen applications, you can turn off line wrapping by
    # sending an appropriate escape sequence to the terminal:
    #   tput rmam
    # This mode can be cancelled with a similar escape:
    #   tput smam
    # also: https://tomayko.com/blog/2004/StupidShellTricks

    if not "LINUX" in platform.platform().upper(): return

    if action == 'set':
        #~print("setting")
        try:
            if gglobs.tput:
                subprocess.call(["tput", "rmam"]) # tput rmam: no line break on lines longer than screen
                dprint("{:28s}: {}".format("Linebreak (Linux)", "tput rmam was executed - no line break"))
            else:
                subprocess.call(["tput", "smam"]) # tput smam: do line break on lines longer than screen
                dprint("{:28s}: {}".format("Linebreak (Linux)", "tput smam was executed - break lines when longer than screen"))
        except Exception as e:
            dprint("{:28s}: {}".format("Linebreak (Linux)", "WARNING: tput rmam / tput smam command failed"), debug=True)

    else:
        #~print("cleaning")
        try:
            if gglobs.tput:
                subprocess.call(["tput", "smam"]) # tput smam: do line break on lines longer than screen
                dprint("{:28s}: {}".format("Linebreak (Linux)", "tput smam was executed - break lines longer than screen"))
        except Exception as e:
            dprint("{:28s}: {}".format("Linebreak (Linux)", "WARNING: tput rmam / tput smam command failed"), debug=True)


def autoPORT(device):
    """Tries to find a working port and baudrate by testing all serial
    ports for successful communication by auto discovery of baudrate.
    All available ports will be listed with the highest baudrate found.
    Ports are found as:
    /dev/ttyS0 - ttyS0              # a regular serial port
    /dev/ttyUSB0 - USB2.0-Serial    # a USB-to-Serial port
    device is:  "GMC", or "I2C", or "GS"
    """

    if   device == "GMC":   import gdev_gmc
    elif device == "I2C":   import gdev_i2c
    elif device == "GS":    import gdev_scout

    fncname = "autoPORT: "
    dprint(fncname + "Autodiscovery of USB-to-Serial Ports")
    setDebugIndent(1)

    time.sleep(0.5) # a freshly plugged in device, not fully recognized
                    # by system, sometimes produces errors

#    lp = getPortList(symlinks=True)    # get a list of all ports including symlinks
    lp = getPortList(symlinks=False)    # get a list of all ports, but ignore symlinks

    if len(lp) == 0:
        errmessage = fncname + "ERROR: No available serial ports found"
        dprint(errmessage, debug=True)
        setDebugIndent(0)
        return None, errmessage

    dprint(fncname + "Found these ports:", debug=True)
    ports =[]
    for p in lp :
        dprint("   ", p, debug=True)
        ports.append(str(p).split(" ",1)[0])
    ports.sort()
    ports_found = []

    includeFlag = False
    if   device == "GMC":   includeFlag = True if gglobs.GMCttyS == 'include' else False
    elif device == "I2C":   includeFlag = True if gglobs.I2CttyS == 'include' else False
    elif device == "GS":    includeFlag = True if gglobs.GSttyS  == 'include' else False

    dprint(fncname + "Testing all ports for communication:", debug=True)
    for port in ports:
        dprint(fncname + "Port:", port, debug=True)
        if "/dev/ttyS" in port:
            if includeFlag: dprint(fncname + "Include Flag is set for port: '{}'".format(port), debug=True)
            else:
                            dprint(fncname + "Ignore Flag is set for port: '{}'".format(port), debug=True)
                            continue

        if   device == "GMC":   abr = gdev_gmc.     autoGMC_BAUDRATE(port)
        elif device == "I2C":   abr = gdev_i2c.     I2CautoBAUDRATE(port)
        elif device == "GS":    abr = gdev_scout.   GSautoBaudrate(port)

        if   abr > 0:       ports_found.append((port, abr))
        elif abr == 0:      dprint(fncname + "Failure - no communication at any baudrate on port: '{}'".format(port), debug=True)
        elif abr == None:   dprint(fncname + "ERROR: Failure during Serial Communication on port: '{}'".format(port), debug=True)

    if len(ports_found) == 0:
        errmessage = "ERROR: No communication at any serial port and baudrate"
        ports_found = None
    else:
        errmessage = ""

    if errmessage > "": dprint(fncname + errmessage)
    setDebugIndent(0)

    return ports_found, errmessage


def autoDiscoverUSBPort(device="GMC"):
    """USB Autodiscovery with option to select any found connection.
    device options: GMC, GS, I2C"""

    rmself = gglobs.exgg    # access to ggeiger "remote self"

    fnc = "autoDiscoverUSBPort: "
    windowTitle = "Autodiscover USB-to-Serial Port for Device:  '{}'".format(device)

    if device not in ("GMC", "GS", "I2C"):
        printProgError(fnc + "incorrectly defined device: {}".format(device))

    if gglobs.logging :
        rmself.showStatusMessage("Cannot autoDiscover when logging! Stop logging first")
        dprint(fnc + "Cannot autodiscover when logging! Stop logging first")
        return


    msg = QMessageBox()
    msg.setIcon(QMessageBox.Critical)
    msg.setWindowTitle(windowTitle)
    #msg.setFont(gglobs.fontstd)
    critical = """                            C A U T I O N !

This discovery will write-to and read-from all available USB-to-Serial ports.

If any other program is communicating with these devices at the same time, both program and devices may be severely disturbed!

Note that this applies ONLY to USB-to-Serial port connections. Any other native USB de­vices (mouse, keyboard, printer, ...) won’t be impacted by the discovery!

It is advisable to stop all those other activities for the duration of this discovery, but leave the cables connected.

All devices under GeigerLog's control will automatically be disconnected by GeigerLog before the test starts.

Click OK to proceed with the discovery, otherwise click Cancel.
    """
    msg.setText(critical)
    msg.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
    msg.setDefaultButton(QMessageBox.Cancel)
    msg.setEscapeButton(QMessageBox.Cancel)
    if msg.exec() != 1024:      return

    dprint(fnc + "device: '{}'".format(device))
    setDebugIndent(1)

    # disconnect everything if anything is connected
    if gglobs.DevicesConnected > 0:
        rmself.switchConnections(new_connection = "OFF")
        Qt_update()

    setBusyCursor()
    rec, errmessage = autoPORT(device)
    setNormalCursor()

    msg = QMessageBox(rmself)
    msg.setWindowTitle(windowTitle)
    #msg.setFont(gglobs.fontstd)
    msg.setIcon(QMessageBox.Information)
    msg.setWindowIcon(gglobs.iconGeigerLog)

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

    msg.setText(txt1)

    txt1  = "-" * 100
    txt1 += "\nThe current settings of GeigerLog for device '{}' are: \n".format(device)
    if   device == "GMC":   txt1 += "\n     Port: {:20s}  \tBaudrate: {}".format(gglobs.GMCusbport, gglobs.GMCbaudrate)
    elif device == "GS":    txt1 += "\n     Port: {:20s}  \tBaudrate: {}".format(gglobs.GSusbport,  gglobs.GSbaudrate)
    elif device == "I2C":   txt1 += "\n     Port: {:20s}  \tBaudrate: {}".format(gglobs.I2Cusbport, gglobs.I2Cbaudrate)

    msg.setInformativeText(txt1)
    msg.setDefaultButton(QMessageBox.Cancel)
    msg.setEscapeButton (QMessageBox.Cancel)
    if flag == "fail":      msg.setStandardButtons(QMessageBox.Cancel)
    else:                   msg.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)

    if msg.exec() == 1024:
        dprint(fnc + "Accepting autodiscovered port settings; connecting now")
        if   device == "GMC":   gglobs.GMCusbport, gglobs.GMCbaudrate = str(rec[0][0]), str(rec[0][1])
        elif device == "GS":    gglobs.GSusbport,  gglobs.GSbaudrate  = str(rec[0][0]), str(rec[0][1])
        elif device == "I2C":   gglobs.I2Cusbport, gglobs.I2Cbaudrate = str(rec[0][0]), str(rec[0][1])
        rmself.switchConnections(new_connection = "ON")
    else:
        if flag != "fail": dprint(fnc + "User not accepting autodiscovered port settings; cancelling now")

    setDebugIndent(0)


def openManual():
    """Show the GeigerLog Manual, first try a local version, but if not
    present, then try the version on SourceForge"""

    rmself = gglobs.exgg    # access to ggeiger "remote self"

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
        efprint("The file 'GeigerLog-Manual-xyz', with xyz being a version number, is missing")
        qefprint("from the GeigerLog working directory 'geigerlog'.")
        fprint("Now trying to find the file online.")
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
            print(sys.exc_info())
            dprint("Failure Showing '{}' via xdg-open on Linux or via os.startfile on other OS".format(manual_file))

        try:
            if sys.platform.startswith('linux'):
                subprocess.call(["firefox", manual_file])
                dprint("Showing '{}' via firefox on Linux".format(manual_file))
            else:
                os.startfile(manual_file)
                dprint("Showing '{}' via os.startfile on other OS".format(manual_file))

            return
        except Exception as e:
            print(sys.exc_info())
            dprint("Failure Showing '{}' via firefox on Linux or via os.startfile on other OS".format(manual_file))

        try:
            import webbrowser
            webbrowser.open(manual_file)
            dprint("Showing '{}' via import webbrowser".format(manual_file))

            return
        except Exception as e:
            print(sys.exc_info())
            dprint("Failure Showing '{}' via import webbrowser".format(manual_file))


    try:
        shortv = gglobs.__version__.split("pre")[0]   # use only the version part before 'pre'
        #shortv: "1.0.1pre9" --> "1.0.1"
        print("shortv: ", shortv)

        url = QUrl('https://sourceforge.net/projects/geigerlog/files/GeigerLog-Manual-v{}.pdf'.format(shortv))
        if QDesktopServices.openUrl(url):
            dprint("Showing QUrl '{}'".format(url))
        else:
            QMessageBox.warning(rmself, 'GeigerLog Manual', 'Could not open GeigerLog Manual')
            dprint("Failure Showing manual with QUrl '{}'".format(url))
        return
    except Exception as e:
        msg = "Failure Showing manual with QUrl"
        exceptPrint("openManual: " + str(e), msg)

    efprint("Could not find GeigerLog-Manual, neither locally nor online!")


def showSystemInfo():
    """System Info on the Devel Menu"""

    from gdev_gmc import cfgKeyHigh

    global app

    rmself = gglobs.exgg    # access to ggeiger "remote self"

    screen           = QDesktopWidget().screenGeometry()
    screen_available = QDesktopWidget().availableGeometry()
    geom             = rmself.geometry()
    geom_frame       = rmself.frameGeometry()

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
    for a in getVersionStatus():
        si += fmt.format( "  {:}:".format(a[0]),         "{}".format( a[1]))

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
    si += fmt.format("  Flag tput:",                     str(gglobs.tput))
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
    si += fmt.format("   Active Font - Menubar:",        strFontInfo("", rmself.menubar.fontInfo()))
    si += fmt.format("   Active Font - NotePad:",        strFontInfo("", rmself.notePad.fontInfo()))
    si += fmt.format("   Active Font - LogPad:",         strFontInfo("", rmself.logPad.fontInfo()))

    # GMC device
    si += fmt.format("\nGMC Device:",                    "")
    si += fmt.format("  Model connected:",               str(gglobs.GMCDeviceDetected))

    try: # the comma-separator fails if gglobs.GMC_memory is still 'auto'
        si += fmt.format("  Memory (bytes):",            "{:,}".format(gglobs.GMC_memory))
    except:
        si += fmt.format("  Memory (bytes):",            "{:}".format(gglobs.GMC_memory))

    try: # the comma-separator fails if gglobs.GMC_SPIRpage is still 'auto'
        si += fmt.format("  SPIRpage Size (bytes):", "{:,}"    .format(gglobs.GMC_SPIRpage))
    except:
        si += fmt.format("  SPIRpage Size (bytes):", "{:}"    .format(gglobs.GMC_SPIRpage))

    si += fmt.format("  SPIRbugfix:",                "{:}"    .format(gglobs.GMC_SPIRbugfix))
    si += fmt.format("  configsize (bytes):",         "{:}"    .format(gglobs.GMC_configsize))
    si += fmt.format("  Sensitivity (CPM/(µSv/h)):",    str(gglobs.calibration1st))
    si += fmt.format("  Calibration2nd (CPM/(µSv/h)):", str(gglobs.calibration2nd))
    si += fmt.format("  voltagebytes (bytes):",       "{:}"    .format(gglobs.GMC_voltagebytes))
    si += fmt.format("  endianness:",                 "{:}"    .format(gglobs.GMC_endianness))
    si += fmt.format("  nbytes:",                     "{:}"    .format(gglobs.GMC_nbytes))
    si += fmt.format("  locationBug:",                "{:}"    .format(gglobs.GMC_locationBug))
    si += fmt.format("  History Saving Mode:",           str(gglobs.GMCsavedatatype))
    si += fmt.format("  FastEstimateTime:",              str(gglobs.GMC_FastEstTime))

    # Audio device
    si += fmt.format("\nAudio Device:",                  "")
    si += fmt.format("  Model connected:",               str(gglobs.AudioDeviceDetected))

    # Radmon device
    si += fmt.format("\nRadmon Device:",                  "")
    si += fmt.format("  Model connected:",               str(gglobs.RMDeviceDetected))

    # AmbioMon device
    si += fmt.format("\nAmbioMon Device:",               "")
    si += fmt.format("  Model connected:",               str(gglobs.AmbioDeviceDetected))

    # GS device
    si += fmt.format("\nGS Device:",                     "")
    si += fmt.format("  Model connected:",               str(gglobs.GSDeviceDetected))
    si += fmt.format("  Sensitivity (CPM/(µSv/h)):",   str(gglobs.GSSensitivity))
    si += fmt.format("  Firmware:",                      str(gglobs.GSFirmware))
    si += fmt.format("  Serial Number:",                 str(gglobs.GSSerialNumber))

    # I2C device
    si += fmt.format("\nI2C Device:",                     "")
    si += fmt.format("  Model connected:",               str(gglobs.I2CDeviceDetected))
    si += fmt.format("  Sensor: #1:",                    str(gglobs.I2CSensor1))
    si += fmt.format("  Sensor: #2:",                    str(gglobs.I2CSensor2))

    # Labjack device
    si += fmt.format("\nLabjack Device:",               "")
    si += fmt.format("  Model connected:",               str(gglobs.LJDeviceDetected))


    # Serial Ports
    si += fmt.format("\nUSB-to-Serial Port Settings:",   "")

    # GMC USB port
    si += fmt.format("  GMC Serial (USB) Port Settings:",  "")
    si += fmt.format("   Port:",                          str(gglobs.GMCusbport))
    si += fmt.format("   Baudrate:",                      "{:,}".format(int(gglobs.GMCbaudrate)))
    si += fmt.format("   Timeout: (Read)",                str(gglobs.GMCtimeout))
    si += fmt.format("   Timeout: (Write)",               str(gglobs.GMCtimeout_write))
    si += fmt.format("   ttyS:",                          str(gglobs.GMCttyS))

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
    for key in ("Website", "URL", "UserID", "CounterID", "SSID", "Password", "Period"):
        si += fmt.format("  " + key, cfgKeyHigh[key][0])

    lsysinfo = QTextBrowser()                              # to hold the text; allows copy
    lsysinfo.setLineWrapMode(QTextEdit.WidgetWidth)
    lsysinfo.setText(si)

    dlg = QDialog()
    dlg.setWindowIcon(gglobs.iconGeigerLog)
    dlg.setWindowTitle("Help - System Info")
    dlg.setFont(gglobs.fontstd)
    dlg.setWindowModality   (Qt.WindowModal)
    dlg.setMinimumWidth(1200)
    dlg.setMinimumHeight(690)

    bbox = QDialogButtonBox()
    bbox.setStandardButtons(QDialogButtonBox.Ok)
    bbox.accepted.connect(lambda: dlg.done(0))

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


def cleanupDevices(ctype="before"):
    """getExtrabyte for GMC devices; ctype is 'before' or 'after';
    so far only for GMC
    """

    from gdev_gmc import getGMC_ExtraByte

    if   ctype == "before":
        if gglobs.GMCConnection:
            dprint("startLogging: Cleaning pipeline before logging")
            getGMC_ExtraByte()

    elif ctype == "after":
        if gglobs.GMCConnection:
            dprint("stopLogging: Cleaning pipeline after logging")
            getGMC_ExtraByte()

    else:
        #whatever; just as placeholder
        if gglobs.GMCConnection:
            dprint("stopLogging: Cleaning pipeline ...")
            getGMC_ExtraByte()


def setLoggableVariables(device, DeviceVariables):
    """set the loggable variables"""

    fncname = "setLoggableVariables: "
    if DeviceVariables == None: return  # is None for current GammScout counter

    DevVars = DeviceVariables.split(",")
    for i in range(0, len(DevVars)):    DevVars[i] = DevVars[i].strip()
    gglobs.Devices[device][1] = DevVars
    wprint(fncname + "Device: ", device, ", Variables:", gglobs.Devices[device][1])


def setCalibrations(DeviceVariables, DeviceCalibration):
    """set the calibration for the defined variables"""

    fncname = "setCalibrations: "
    if DeviceVariables == None: return  # is None for current GammaScout counter --- not any more

    set1st = False
    set2nd = False
    set3rd = False

    devvar = DeviceVariables.split(",")
    for a in devvar:
        a = a.strip()
        if len(a) == 0: continue
        if   "1st" in a:
            gglobs.calibration1st = DeviceCalibration   # CPM1st, CPS1st
            set1st = True

        if   "2nd" in a:
            gglobs.calibration2nd = DeviceCalibration   # CPM2nd, CPS2nd
            set2nd = True

        if   "3rd" in a:
            gglobs.calibration3rd = DeviceCalibration   # CPM3rd, CPS3rd
            set3rd = True

        #~else:            gglobs.calibration1st = DeviceCalibration   # CPM, CPS, CPM1st, CPS1st
    if not set1st and not set2nd and not set3rd:
        gglobs.calibration1st = DeviceCalibration   # CPM, CPS, CPM1st, CPS1st

    wprint(fncname + "DeviceVariables: ", DeviceVariables)
    wprint(fncname + "calib 1st:",   gglobs.calibration1st)
    wprint(fncname + "calib 2nd:",   gglobs.calibration2nd)
    wprint(fncname + "calib 3rd:",   gglobs.calibration3rd)


def printLoggedValuesHeader():
    """print header for logged values"""

    # print like:
    #               Variables: CPM       CPS       CPM1st    CPS1st    CPM2nd    CPS2nd    CPM3rd    CPS3rd    T         P         H         X

    text = "{:<25s}".format("Variables: ")
    for a in gglobs.varsDefault:
        text += "{:<10s}".format(a)
    vprint(text)


def printLoggedValues(rfncname, varlist, alldata):
    """print formatted logged values"""

    # print like:
    # GMCgetValues:           176.00    4.00      176.00    4.00      0.00      0.00      -         -         -         -         -         -
    # getAudioValues:          -         -         -         -         -         -         0.00      0.00      -         -         -         -

    #~print("printLoggedValues: alldata: ", alldata)
    text = "{:<25s}".format(rfncname)
    for a in gglobs.varsDefault:
        if   a in alldata: newtext = "{:<10.2f}".format(alldata[a])
        else:              newtext = "{:<10s}".format("-")
        text += newtext
    vprint(text)



def fprintDeltaTimeMessage(deltatime, deviceDateTime):
    """determines difference between times of computer and device and gives message"""

    #fprint("Device Time:", "{}".format(deviceDateTime), debug=True)

    if   abs(deltatime) <= 1:    dtxt = "Device time is same as computer time within 1 sec"                     # uncertainty 1 sec
    elif np.isnan(deltatime):    dtxt = "Device time cannot be read"                                            # clock defect?
    elif deltatime >= +1:        dtxt = "Device is slower than computer by {:0.1f} sec".format(deltatime)       # delta positiv
    elif deltatime <= -1:        dtxt = "Device is faster than computer by {:0.1f} sec".format(abs(deltatime))  # delta negativ

    msg   = ("", "{}".format(dtxt))
    devDT = ("Device Time:", "{}".format(deviceDateTime))

    if abs(deltatime) > 5:
        efprint(*devDT)
        qefprint("Date & Time from computer:",  longstime())
        qefprint(*msg)

    elif np.isnan(deltatime):
        efprint(*msg)

    else:
        fprint(*devDT)
        fprint(*msg)


def getConfigEntry(section, parameter, ptype):

    #print("getConfigEntry: ", section, ", ", parameter, ", ", ptype, end="  ")
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
        errmesg = "Section: {}, Parameter: {}<br>Problem: has wrong value: {}".format(section, parameter, t)
        gglobs.configAlerts += errmesg + "<br><br>"
        edprint("WARNING: " + errmesg, debug=True)

        return "WARNING"

    except Exception as e:
        errmesg = "Section: {}, Parameter: {}<br>Problem: {}".format(section, parameter, e)
        gglobs.configAlerts += errmesg + "<br><br>"
        edprint("WARNING: " + errmesg, debug=True)

        return "WARNING"

###############################################################################



#
# Configuration file evaluation
#
def readGeigerLogConfig():
    """reading the configuration file, return if not available.
    Not-available or illegal options are being ignored with only a debug message"""

    global config # make config available to getConfigEntry()

    dprint("readGeigerLogConfig: using config file: ", gglobs.configPath)
    setDebugIndent(1)

    infostrHeader = "cfg: {:35s} {}"
    infostr       = "cfg:     {:35s}: {}"
    while True:

    # does the config file exist and can it be read?
        if not os.path.isfile(gglobs.configPath) or not os.access(gglobs.configPath, os.R_OK) :
            msg = """Configuration file <b>'geigerlog.cfg'</b> does not exist or is not readable."""
            edprint(msg, debug=True)
            msg += """<br><br>Please check and correct. Cannot continue, will exit."""
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
            msg += "<br><br>Note that duplicate entries are not allowed!"
            msg += "<br><br>ERROR Message:<br>" + str(sys.exc_info()[1])
            msg += "<br><br>Please check and correct. Cannot continue, will exit."
            gglobs.startupProblems = msg
            break

    # the config file exists and can be read:
        dprint(infostrHeader.format("Startup values", ""))

    #~# Logging
        #~t = getConfigEntry("Logging", "logcycle", "float" )
        #~gglobs.logcycle = 3
        #~if t != "WARNING":
            #~if float(t) >= 0.1:                 gglobs.logcycle = float(t)
        #~dprint(infostr.format("Logcycle (sec)", gglobs.logcycle))

    # Logging
        t = getConfigEntry("Logging", "logcycle", "upper" )
        gglobs.logcycle = 3
        if t != "WARNING":
            if t == "AUTO":                     gglobs.logcycle = 3
            else:
                try:    ft = float(t)
                except: ft = 3
                if      ft >= 0.1:              gglobs.logcycle = ft
                else:                           gglobs.logcycle = 3
        dprint(infostr.format("Logcycle (sec)", gglobs.logcycle))

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
        t = getConfigEntry("Manual", "manual_name", "str" )
        if t != "WARNING":
            if t.upper() == 'AUTO' or t == "":
                gglobs.manual_filename = 'auto'
                dprint(infostr.format("Manual file", gglobs.manual_filename))
            else:
                manual_file = getProgPath() + "/" + t
                #print "readGeigerLogConfig manual_file:", manual_file
                if os.path.isfile(manual_file):     # does the file exist?
                    # it exists
                    gglobs.manual_filename = t
                    dprint(infostr.format("Manual file", gglobs.manual_filename))
                else:
                    # it does not exist
                    gglobs.manual_filename = 'auto'
                    dprint("WARNING: Manual file '{}' does not exist".format(t))



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
        w = getConfigEntry("Window", "width", "int" )
        h = getConfigEntry("Window", "height", "int" )
        if w != "WARNING" and h != "WARNING":
            if w > 500 and w < 5000 and h > 100 and h < 5000:
                gglobs.window_width  = w
                gglobs.window_height = h
                dprint(infostr.format("Window dimensions (pixel)", "{} x {}".format(gglobs.window_width, gglobs.window_height)))
            else:
                dprint("WARNING: Config Window dimension out-of-bound; ignored: {} x {} pixel".format(gglobs.window_width, gglobs.window_height), debug=True)

    # Window size
        t = getConfigEntry("Window", "size", "upper" )
        if t != "WARNING":
            if    t == 'MAXIMIZED':    gglobs.window_size = 'maximized'
            else:                      gglobs.window_size = 'auto'
            dprint(infostr.format("Window Size ", gglobs.window_size))

    # Window Style
        t = getConfigEntry("Window", "windowStyle", "str" )
        if t != "WARNING":
            available_style = QStyleFactory.keys()
            #print("readGeigerLogConfig: WindowStyle available: ", available_style)
            if t in available_style:    gglobs.windowStyle = t
            else:                       gglobs.windowStyle = "auto"
            dprint(infostr.format("Window Style ", gglobs.windowStyle))


    # Graphic
        dprint(infostrHeader.format("Graphic", ""))

        # Graphic mav_initial
        t = getConfigEntry("Graphic", "mav_initial", "float" )
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

        # markerstyle
        t = getConfigEntry("Plotstyle", "markerstyle", "str" )
        if t != "WARNING":
            if t in "osp*h+xD" :             gglobs.markerstyle = t
            else:                            gglobs.markerstyle = "o"
        dprint(infostr.format("markerstyle", gglobs.markerstyle))

        # markersize
        t = getConfigEntry("Plotstyle", "markersize", "str" )
        if t != "WARNING":
            try:                            gglobs.markersize = float(t)
            except:                         gglobs.markersize = 15
        dprint(infostr.format("markersize", gglobs.markersize))


    # Defaults
        dprint(infostrHeader.format("Defaults", ""))

        # calibration 1st tube is 154 CPM/(µSv/h), =  0.0065 in units of µSv/h/CPM
        t = getConfigEntry("Defaults", "DefaultSens1st", "str" )
        if t != "WARNING":
            try:                                gglobs.DefaultSens1st = float(t)
            except:                             gglobs.DefaultSens1st = 154
        if gglobs.DefaultSens1st <= 0:         gglobs.DefaultSens1st = 154
        dprint(infostr.format("DefaultSens1st", gglobs.DefaultSens1st))

        # calibration 2nd tube is 2.08 CPM/(µSv/h), =  0.48 in units of µSv/h/CPM
        t = getConfigEntry("Defaults", "DefaultSens2nd", "str" )
        if t != "WARNING":
            try:                                gglobs.DefaultSens2nd = float(t)
            except:                             gglobs.DefaultSens2nd = 2.08
        if gglobs.DefaultSens2nd <= 0:         gglobs.DefaultSens2nd = 2.08
        dprint(infostr.format("DefaultSens2nd", gglobs.DefaultSens2nd))

        # calibration 3rd tube is 154 CPM/(µSv/h), =  0.0065 in units of µSv/h/CPM
        t = getConfigEntry("Defaults", "DefaultSens3rd", "str" )
        if t != "WARNING":
            try:                                gglobs.DefaultSens3rd = float(t)
            except:                             gglobs.DefaultSens3rd = 154
        if gglobs.DefaultSens3rd <= 0:         gglobs.DefaultSens3rd = 154
        dprint(infostr.format("DefaultSens3rd", gglobs.DefaultSens3rd))


    #
    # ValueScaling - it DOES modify the variable value!
    #
    # infostr = "INFO: {:35s}: {}"
        dprint(infostrHeader.format("ValueScaling", ""))
        for vname in gglobs.varsDefault:
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
        for vname in gglobs.varsDefault:
            t = getConfigEntry("GraphScaling", vname, "upper" )
            if t != "WARNING":
                if t == "":     pass                    # use value from gglobs
                else:           gglobs.GraphScale[vname] = t
                dprint(infostr.format("GraphScale['{}']".format(vname), gglobs.GraphScale[vname]))


    # GMCDevice
        dprint(infostrHeader.format("GMCDevice", ""))

        # GMCDevice Configuration
        t = getConfigEntry("GMCDevice", "GMCActivation", "upper" )
        if t != "WARNING":
            if t == "YES":                  gglobs.GMCActivation = True
            dprint(infostr.format("GMCActivation", gglobs.GMCActivation))

        if gglobs.GMCActivation: # show the other stuff only if activated
            gglobs.Devices["GMC"][2] = True

            # GMCDevice Firmware Bugs
            #fwb = "GMC-500+Re 1.18, GMC-500+Re 1.21"
            t = getConfigEntry("GMCDevice", "GMC_locationBug", "str" )
            if t != "WARNING":
                if t.upper() == "AUTO":     gglobs.GMC_locationBug = "auto"
                else:                       gglobs.GMC_locationBug = t
                dprint(infostr.format("Location Bug", gglobs.GMC_locationBug))

            # GMCDevice Firmware Bugs - GMC_FastEstimateTime
            t = getConfigEntry("GMCDevice", "GMC_FastEstTime", "str" )
            if t != "WARNING":
                try:    temp = int(float(t))
                except: temp = "dummy"
                if   t.upper() == "AUTO":           gglobs.GMC_FastEstTime = "auto"
                elif t.upper() == "DYNAMIC":        gglobs.GMC_FastEstTime = 3
                elif temp in (3,5,10,15,20,30,60):  gglobs.GMC_FastEstTime = temp
                else:                               gglobs.GMC_FastEstTime = "auto"
                dprint(infostr.format("FastEstTime", gglobs.GMC_FastEstTime))

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
#TESTING
                #~else:               gglobs.GMC_SPIRpage = 2048      # @ 16k speed: 8287 B/sec
                                                                #~# @  8k speed: 7908 B/sec
                                                                #~# @  4k speed: 7140 B/sec
                                                                #~# @  2k speed: 6057 B/sec

############
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

            # GMCDevice calibration 1st tube
            t = getConfigEntry("GMCDevice", "GMC_sensitivity", "upper" )
            if t != "WARNING":
                if t == 'AUTO':             gglobs.calibration1st = "auto"
                else:
                    try:
                        if float(t) > 0:    gglobs.calibration1st = float(t)
                        else:               gglobs.calibration1st = "auto"
                    except:                 gglobs.calibration1st = "auto"
                dprint(infostr.format("Sensitivity", gglobs.calibration1st))

            # GMCDevice calibration 2nd tube
            t = getConfigEntry("GMCDevice", "GMC_sensitivity2nd", "upper" )
            if t != "WARNING":
                if t == 'AUTO':             gglobs.calibration2nd = "auto"
                else:
                    try:
                        if float(t) > 0:    gglobs.calibration2nd = float(t)
                        else:               gglobs.calibration2nd = "auto"
                    except:                 gglobs.calibration2nd = "auto"
                dprint(infostr.format("Sensitivity 2nd tube", gglobs.calibration2nd))

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
                if   t == "AUTO":             gglobs.GMC_WifiIndex = "auto"
                elif t == "NONE":             gglobs.GMC_WifiIndex = None #"none"
                elif t in  ["2", "3", "4"]:   gglobs.GMC_WifiIndex = t
                else:                         gglobs.GMC_WifiIndex = "auto"
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
                else:                       gglobs.GMC_variables = t
                dprint(infostr.format("Variables", gglobs.GMC_variables))


        # GMCSerialPort
            dprint(infostrHeader.format("  GMCSerialPort", ""))

            t = getConfigEntry("GMCSerialPort", "GMCusbport", "str" )
            if t != "WARNING":
                gglobs.GMCusbport = t
                dprint(infostr.format("Using usbport", gglobs.GMCusbport))

            t = getConfigEntry("GMCSerialPort", "GMCbaudrate", "int" )
            if t != "WARNING":
                if t in gglobs.GMCbaudrates:            gglobs.GMCbaudrate = t
                dprint(infostr.format("Using baudrate", gglobs.GMCbaudrate))

            t = getConfigEntry("GMCSerialPort", "GMCtimeout", "float" )
            if t != "WARNING":
                if t > 0:   gglobs.GMCtimeout = t
                else:       gglobs.GMCtimeout = 3  # if zero or negative value given, set to 3
                dprint(infostr.format("Using timeout (sec)", gglobs.GMCtimeout))

            t = getConfigEntry("GMCSerialPort", "GMCtimeout_write", "float" )
            if t != "WARNING":
                if t > 0:   gglobs.GMCtimeout_write = t
                else:       gglobs.GMCtimeout_write = 1  # if zero or negative value given, set to 1
                dprint(infostr.format("Using timeout_write (sec)", gglobs.GMCtimeout_write))

            t = getConfigEntry("GMCSerialPort", "GMCttyS", "upper" )
            if t != "WARNING":
                if   t == 'INCLUDE':  gglobs.GMCttyS = 'include'
                else:                 gglobs.GMCttyS = 'ignore'
                dprint(infostr.format("Ports of ttyS type", gglobs.GMCttyS))


    # AudioCounter
        dprint(infostrHeader.format("AudioCounter", ""))
        # AudioCounter Activation
        t = getConfigEntry("AudioCounter", "AudioActivation", "upper" )
        if t != "WARNING":
            if t == "YES":              gglobs.AudioActivation = True
            #else:                       gglobs.AudioActivation = False
            dprint(infostr.format("AudioActivation", gglobs.AudioActivation))

        if gglobs.AudioActivation: # show the other stuff only if activated
            gglobs.Devices["Audio"][2] = True

            # AudioCounter DEVICE
            t = getConfigEntry("AudioCounter", "AudioDevice", "str" )
            if t != "WARNING":
                if   t.upper() == "AUTO":   gglobs.AudioDevice = "auto"
                elif not ("," in t):        gglobs.AudioDevice = "auto" # must have 2 items separated by comma
                else:
                    t = t.split(",", 1)
                    t[0] = t[0].strip()
                    t[1] = t[1].strip()
                    if t[0].isdecimal():   t[0] = int(t[0])
                    if t[1].isdecimal():   t[1] = int(t[1])
                    gglobs.AudioDevice = tuple(t)
                dprint(infostr.format("AudioDevice", gglobs.AudioDevice))

            # AudioCounter LATENCY
            t = getConfigEntry("AudioCounter", "AudioLatency", "str" )
            if t != "WARNING":
                if   t.upper() == "AUTO":   gglobs.AudioLatency = "auto"
                elif not ("," in t):        gglobs.AudioLatency = "auto" # must have 2 items separated by comma
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
                    except:                         gglobs.AudioPulseMax = 32768
                    if gglobs.AudioPulseMax <= 0:   gglobs.AudioPulseMax = 32768
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
                else:                       gglobs.AudioVariables = t
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
        dprint(infostrHeader.format("RadMonPlusDevice", ""))

        # RadMon Activation
        t = getConfigEntry("RadMonPlusDevice", "RMActivation", "upper" )
        if t != "WARNING":
            if t == "YES":                  gglobs.RMActivation = True
            #else:                           gglobs.RMActivation = False
            dprint(infostr.format("RMActivation", gglobs.RMActivation ))

        if gglobs.RMActivation: # show the other stuff only if activated
            gglobs.Devices["RadMon"][2] = True

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
                        else:                           gglobs.RMTimeout = 3  # if zero or negative value given, then set to 3
                    except:                             gglobs.RMTimeout = 3
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
                    gglobs.RMVariables = t
                    if gglobs.RMVariables.count("CPM") > 1 or gglobs.RMVariables.count("CPS") > 0:
                        edprint("WARNING: Improper configuration of variables: ", gglobs.RMVariables)
                        edprint("WARNING: Only a single CPM* is allowed, and no CPS*")
                        gglobs.RMVariables = "auto"
                        edprint("WARNING: RadMon variables are reset to: ", gglobs.RMVariables)
                dprint(infostr.format("RMVariables",    gglobs.RMVariables))


    # AmbioMon
        dprint(infostrHeader.format("AmbioMonDevice", ""))

        # AmbioMon Activation
        t = getConfigEntry("AmbioMonDevice", "AmbioActivation", "upper" )
        if t != "WARNING":
            if t == "YES":                      gglobs.AmbioActivation = True
            #else:                               gglobs.AmbioActivation = False
            dprint(infostr.format("AmbioActivation", gglobs.AmbioActivation ))

        if gglobs.AmbioActivation: # show the other stuff only if activated
            gglobs.Devices["AmbioMon"][2] = True

            # AmbioMon Server IP
            t = getConfigEntry("AmbioMonDevice", "AmbioServerIP", "str" )
            if t != "WARNING":
                if t.upper() == 'AUTO':                 gglobs.AmbioServerIP = "auto"
                else:                                   gglobs.AmbioServerIP = t
                dprint(infostr.format("AmbioServerIP",  gglobs.AmbioServerIP ))

            # AmbioMon timeout
            t = getConfigEntry("AmbioMonDevice", "AmbioTimeout", "upper" )
            if t != "WARNING":
                if t == 'AUTO':                         gglobs.AmbioTimeout = "auto"
                else:
                    try:
                        if float(t) > 0:                gglobs.AmbioTimeout = float(t)
                        else:                           gglobs.AmbioTimeout = 3  # if zero or negative value given, then set to 3
                    except:                             gglobs.AmbioTimeout = 3
                dprint(infostr.format("AmbioTimeout",   gglobs.AmbioTimeout))

            # AmbioMon calibration
            t = getConfigEntry("AmbioMonDevice", "AmbioCalibration", "upper" )
            if t != "WARNING":
                if t == 'AUTO':                         gglobs.AmbioCalibration = "auto"
                else:
                    try:
                        if float(t) > 0:                gglobs.AmbioCalibration = float(t)
                        else:                           gglobs.AmbioCalibration = "auto"
                    except:                             gglobs.AmbioCalibration = "auto"
                dprint(infostr.format("AmbioCalibration", gglobs.AmbioCalibration))

            # AmbioMon variables
            t = getConfigEntry("AmbioMonDevice", "AmbioVariables", "str" )
            if t != "WARNING":
                if t.upper() == "AUTO":                 gglobs.AmbioVariables = "auto"
                else:                                   gglobs.AmbioVariables = t
                dprint(infostr.format("AmbioVariables", gglobs.AmbioVariables))

            # AmbioMon DataType
            t = getConfigEntry("AmbioMonDevice", "AmbioDataType", "str" )
            if t != "WARNING":
                if   t.upper() == "AUTO":               gglobs.AmbioDataType = "auto"
                elif t.upper() == "AVG":                gglobs.AmbioDataType = "AVG"
                else:                                   gglobs.AmbioDataType = "LAST"
                dprint(infostr.format("AmbioVariables", gglobs.AmbioDataType))



    # Gamma-Scout counter
        dprint(infostrHeader.format("GammaScoutDevice", ""))
        # Gamma-Scout Activation
        t = getConfigEntry("GammaScoutDevice", "GSActivation", "upper" )
        if t != "WARNING":
            if t == "YES":                              gglobs.GSActivation = True
            #else:                                       gglobs.GSActivation = False
            dprint(infostr.format("GSActivation",       gglobs.GSActivation ))

        if gglobs.GSActivation: # show the other stuff only if activated
            gglobs.Devices["Gamma-Scout"][2] = True

            # Gamma-Scout variables
            t = getConfigEntry("GammaScoutDevice", "GSVariables", "str" )
            if t != "WARNING":
                if t.upper() == "AUTO":                 gglobs.GSVariables = "auto"
                else:                                   gglobs.GSVariables = t
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
                gglobs.GSusbport = t
                dprint(infostr.format("Using GSusbport", gglobs.GSusbport))

            t = getConfigEntry("GammaScoutSerialPort", "GSbaudrate", "int" )
            if t != "WARNING":
                if t in gglobs.GSbaudrates: gglobs.GSbaudrate = t
                dprint(infostr.format("Using GSbaudrate", gglobs.GSbaudrate))

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

            t = getConfigEntry("GammaScoutSerialPort", "GSttyS", "upper" )
            if t != "WARNING":
                if    t == 'INCLUDE':  gglobs.GSttyS = 'include'
                else:                  gglobs.GSttyS = 'ignore'
                dprint(infostr.format("Ports of ttyS type", gglobs.GSttyS))


    # I2C ELV with BME280
        dprint(infostrHeader.format("I2CSensors", ""))
        # I2C Activation
        t = getConfigEntry("I2CSensors", "I2CActivation", "upper" )
        if t != "WARNING":
            if t == "YES":             gglobs.I2CActivation = True
            #else:                      gglobs.I2CActivation = False
            dprint(infostr.format("I2CActivation", gglobs.I2CActivation ))

        if gglobs.I2CActivation: # show the other stuff only if activated
            gglobs.Devices["I2C"][2] = True

            # I2C variables
            t = getConfigEntry("I2CSensors", "I2CVariables", "str" )
            if t != "WARNING":
                if t.upper() == "AUTO":     gglobs.I2CVariables = "auto"
                else:                       gglobs.I2CVariables = t
                dprint(infostr.format("I2CVariables", gglobs.I2CVariables))

        # I2CSerialPort
            dprint(infostrHeader.format("  I2CSerialPort", ""))

            t = getConfigEntry("I2CSerialPort", "I2Cusbport", "str" )
            if t != "WARNING":
                gglobs.I2Cusbport = t
                dprint(infostr.format("Using I2Cusbport", gglobs.I2Cusbport))

            t = getConfigEntry("I2CSerialPort", "I2Cbaudrate", "int" )
            if t != "WARNING":
                if t in gglobs.GMCbaudrates:                  gglobs.I2Cbaudrate = t
                dprint(infostr.format("Using I2Cbaudrate", gglobs.I2Cbaudrate))

            t = getConfigEntry("I2CSerialPort", "I2Ctimeout", "float" )
            if t != "WARNING":
                if t > 0:   gglobs.I2Ctimeout = t
                else:       gglobs.I2Ctimeout = 3  # if zero or negative value given, set to 3
                dprint(infostr.format("Using I2Ctimeout (sec)",gglobs.I2Ctimeout))

            t = getConfigEntry("I2CSerialPort", "I2Ctimeout_write", "float" )
            if t != "WARNING":
                if t > 0:   gglobs.I2Ctimeout_write = t
                else:       gglobs.I2Ctimeout_write = 1  # if zero or negative value given, set to 1
                dprint(infostr.format("Using I2Ctimeout_write (sec)",gglobs.I2Ctimeout_write))

            t = getConfigEntry("I2CSerialPort", "I2CttyS", "upper" )
            if t != "WARNING":
                if    t == 'INCLUDE':  gglobs.I2CttyS = 'include'
                else:                  gglobs.I2Cttys = 'ignore'
                dprint(infostr.format("Ports of ttyS type", gglobs.I2Cttys))




    # LabJack U3 with probe EI1050
        dprint(infostrHeader.format("LabJackDevice", ""))
        # LabJack Activation
        t = getConfigEntry("LabJackDevice", "LJActivation", "upper" )
        if t != "WARNING":
            if t == "YES":              gglobs.LJActivation = True
            #else:                       gglobs.LJActivation = False
            dprint(infostr.format("LJActivation", gglobs.LJActivation ))

        if gglobs.LJActivation: # show the other stuff only if activated
            gglobs.Devices["LabJack"][2] = True

            # LabJack variables
            t = getConfigEntry("LabJackDevice", "LJVariables", "str" )
            if t != "WARNING":
                if t.upper() == "AUTO":     gglobs.LJVariables = "auto"
                else:                       gglobs.LJVariables = t
                dprint(infostr.format("LJVariables", gglobs.LJVariables))

###############################################################################
# testing
# Raspi preliminary - is NOT in the geigerlog.cfg!
# Raspi Activation ( is done per 'raspi' on Command line
# do not show in debug list
    # Raspi
        #dprint(infostrHeader.format("RaspiDevice", ""))
        if gglobs.RaspiActivation: # show the other stuff only if activated
            gglobs.Devices["Raspi"][2] = True
###############################################################################

    # SimulCounter
        dprint(infostrHeader.format("SimulCounter", ""))
        # SimulCounter Activation
        t = getConfigEntry("SimulCounter", "SimulActivation", "upper" )
        if t != "WARNING":
            if t == "YES":              gglobs.SimulActivation = True
            #~else:                       gglobs.SimulActivation = False
            dprint(infostr.format("SimulActivation", gglobs.SimulActivation))

        if gglobs.SimulActivation: # show the other stuff only if activated
            gglobs.Devices["Simul"][2] = True

            # SimulCounter MEAN
            t = getConfigEntry("SimulCounter", "SimulMean", "upper" )
            if t != "WARNING":
                if   t == "AUTO":                   gglobs.SimulMean = "auto"
                else:
                    try:
                        gglobs.SimulMean = float(t)
                        if gglobs.SimulMean < 0:    gglobs.SimulMean = "auto"
                    except:                         gglobs.SimulMean = "auto"
                dprint(infostr.format("SimulMean",  gglobs.SimulMean))

            # inactive. config file code in module gdev_simul.py
            #
            #~t = getConfigEntry("SimulCounter", "SimulPredictive", "upper" )
            #~if t != "WARNING":
                #~if t == "YES":                      gglobs.SimulPredictive = True
                #~else:                               gglobs.SimulPredictive = False
                #~dprint(infostr.format("SimulPredictive", gglobs.SimulPredictive))

            #~t = getConfigEntry("SimulCounter", "SimulPredictLimit", "str" )
            #~if t != "WARNING":
                #~if t.upper() == "AUTO":             gglobs.SimulPredictLimit = "auto"
                #~try:
                    #~gglobs.SimulPredictLimit = int(float(t))
                    #~if gglobs.SimulPredictLimit < 0:gglobs.SimulPredictLimit = "auto"
                #~except:                             gglobs.SimulPredictLimit = "auto"
                #~dprint(infostr.format("SimulPredictLimit", gglobs.SimulPredictLimit))

            # SimulCounter Variables
            t = getConfigEntry("SimulCounter", "SimulVariables", "str" )
            if t != "WARNING":
                if t.upper() == "AUTO":             gglobs.SimulVariables = "auto"
                else:                               gglobs.SimulVariables = t
                dprint(infostr.format("SimulVariables", gglobs.SimulVariables))


            # SimulCounter Sensitivity
            t = getConfigEntry("SimulCounter", "SimulSensitivity", "str" )
            if t != "WARNING":
                if t.upper() == "AUTO":                   gglobs.SimulSensitivity = "auto"
                else:
                    try:
                        gglobs.SimulSensitivity = float(t)
                        if gglobs.SimulSensitivity <= 0:  gglobs.SimulSensitivity = "auto"
                    except:                               gglobs.SimulSensitivity = "auto"
                dprint(infostr.format("SimulSensitivity", gglobs.SimulSensitivity))


    # MiniMon
        dprint(infostrHeader.format("MiniMon", ""))

        t = getConfigEntry("MiniMon", "MiniMonActivation", "upper" )
        if t != "WARNING":
            if t == "YES":                                  gglobs.MiniMonActivation = True
            dprint(infostr.format("MiniMonActivation",      gglobs.MiniMonActivation))

        if gglobs.MiniMonActivation: # show the other stuff only if activated
            gglobs.Devices["MiniMon"][2] = True

            # MiniMon Device
            t = getConfigEntry("MiniMon", "MiniMonDevice", "str" )
            if t != "WARNING":
                if t.upper() == "AUTO":                     gglobs.MiniMonDevice = "auto"
                else:                                       gglobs.MiniMonDevice = t
                dprint(infostr.format("MiniMonDevice",      gglobs.MiniMonDevice))

            # MiniMon Variables
            t = getConfigEntry("MiniMon", "MiniMonVariables", "str" )
            if t != "WARNING":
                if t.upper() == "AUTO":                     gglobs.MiniMonVariables = "auto"
                else:                                       gglobs.MiniMonVariables = t
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


    # Radiation World Maps
        from gdev_gmc import cfgKeyHigh

        dprint(infostrHeader.format("Worldmaps", ""))

        t = getConfigEntry("Worldmaps", "GMCmapSSID", "str" )
        if t != "WARNING":
            cfgKeyHigh["SSID"][0]  = t
            gglobs.GMCmapSSID      = t

        t = getConfigEntry("Worldmaps", "GMCmapPassword", "str" )
        if t != "WARNING":
            cfgKeyHigh["Password"][0] = t
            gglobs.GMCmapPassword     = t

        t = getConfigEntry("Worldmaps", "GMCmapWebsite", "str" )
        if t != "WARNING":
            cfgKeyHigh["Website"][0] = t
            gglobs.GMCmapWebsite     = t

        t = getConfigEntry("Worldmaps", "GMCmapURL", "str" )
        if t != "WARNING":
            cfgKeyHigh["URL"][0]  = t
            gglobs.GMCmapURL      = t

        t = getConfigEntry("Worldmaps", "GMCmapUserID", "str" )
        if t != "WARNING":
            cfgKeyHigh["UserID"][0] = t
            gglobs.GMCmapUserID     = t

        t = getConfigEntry("Worldmaps", "GMCmapCounterID", "str" )
        if t != "WARNING":
            cfgKeyHigh["CounterID"][0] = t
            gglobs.GMCmapCounterID     = t

        t = getConfigEntry("Worldmaps", "GMCmapPeriod", "str" )
        if t != "WARNING":
            cfgKeyHigh["Period"][0] = t
            gglobs.GMCmapPeriod     = t

        cfgKeyHigh["WiFi"][0] = "unknown"

        for key in "SSID", "Password", "Website", "URL", "UserID", "CounterID", "Period", "WiFi":
            dprint(infostr.format(key, cfgKeyHigh[key][0]))


        break # don't forget to break!

    setDebugIndent(0)
