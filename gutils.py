#!/usr/bin/python3
# -*- coding: UTF-8 -*-

"""
gutils.py - GeigerLog utilities with imports

include in programs with:
    from gutils include *
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
__copyright__       = "Copyright 2016, 2017, 2018, 2019, 2020"
__credits__         = [""]
__license__         = "GPL3"


import sys, os, io, time, datetime

import platform                     # info on OS, machine, architecture, ...
import traceback                    # for traceback on error; used in: exceptPrint
import inspect                      # findinf origin of f'on calls
import copy                         # make shallow and deep copies
import threading
import queue                        # queue for threading
import re                           # regex
import configparser                 # parse configuration file geigerlog.cfg

import sounddevice       as sd
import soundfile         as sf

import serial                       # serial port
import serial.tools.list_ports      # allows listing of serial ports
import urllib.request               # for ambiomon web transfer

import numpy             as np
import matplotlib
import struct                       # packing numbers into chars (needed by gcommands.py)
import paho.mqtt.client  as mqtt    # https://pypi.org/project/paho-mqtt/ (needed by gambiomon.py und gradmon.py)
import sqlite3                      # sudo -H pip3 install  pysqlite3; but should be part of python3 (needed by gsql.py)

import getopt                       # parse command line for options and commands
import signal                       # handling signals like CTRL-C and other
import subprocess                   # to allow terminal commands tput rmam / tput smam
import scipy.signal                 # a subpackage of scipy; needs separate import
import scipy.stats                  # a subpackage of scipy; needs separate import

import gglobs                       # all global vars


# Installing PyQt5
# http://pyqt.sourceforge.net/Docs/PyQt5/installation.html easy with Pip:
# pip3 install pyqt5
from PyQt5.QtWidgets            import *
from PyQt5.QtGui                import *
from PyQt5.QtCore               import *
from PyQt5.QtPrintSupport       import *

##~matplotlib.use('Qt5Agg', warn=True, force=False) # use Qt5Agg, not the default TkAgg
##~matplotlib.use(backend, warn=<deprecated parameter>, force=True)[source]
matplotlib.use('Qt5Agg', force=False) # use Qt5Agg, not the default TkAgg für Py3.7 erforderlich


import matplotlib.backends.backend_qt5agg        # MUST be done BEFORE importing pyplot!
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg    as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar

import matplotlib.pyplot as plt # MUST import AFTER 'matplotlib.use()' / matplotlib-backend!!!
import matplotlib.dates  as mpld


# tricks for Linux:
# For generic non full screen applications, you can turn off line wrapping by
# sending an appropriate escape sequence to the terminal:
#   tput rmam
# This mode can be cancelled with a similar escape:
#   tput smam
# also: https://tomayko.com/blog/2004/StupidShellTricks

#colors for the terminal
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
    # sollte auch damit gehen:     return time.strftime("%Y-%m-%d %H:%M:%S")

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
        dprint("ERROR in datestr2num: Date as String: '{}'".format(string_date), debug=True)
        newstrdate = '2099-09-09 09:09:09'
        dprint("                      replacing with: '{}'".format(newstrdate), debug=True)
        dt=time.mktime(datetime.datetime.strptime(newstrdate, "%Y-%m-%d %H:%M:%S").timetuple())

    return dt


def clamp(n, minn, maxn):
    """limit return value to be within minn and maxn"""

    return min(max(n, minn), maxn)


def IntToChar(intval):

    if intval < 128 and intval > 31:
        char = chr(intval)
    else:
        char = " "

    return char


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

    return "<br>==== {} {}".format(txt, "=" * max(0, (75 - len(txt))))


def logPrint(*args):
    """print all args in logPad area"""

    line = "{:35s}".format(args[0])
    for s in range(1, len(args)):   line += "{}".format(args[s])

    gglobs.logPad.append(line)
    #QApplication.processEvents() # if this is present then execution stops when
                                  # the DisplayLastLogValues is called. Strange!
    return


def efprint(*args, error=False, debug=False, errsound=True):
    """error fprint"""

    fprint(*args, error=True, debug=debug, errsound=errsound)


def qefprint(*args, error=False, debug=False, errsound=False):
    """quiet error fprint"""

    fprint(*args, error=True, debug=debug, errsound=errsound)


def fprint(*args, error=False, debug=False, errsound=True):
    """print all args in the notePad area"""

    ps = "{:30s}".format(str(args[0]))     # 1st arg
    for s in range(1, len(args)):          # skip 1st arg
        ps += str(args[s])

    # jump to the end of text --> new text will always become visible
    #gglobs.notePad.ensureCursorVisible() # does work, but moves text to left, so than
                                          # cursor on most-right position is visible
                                          # requires moving text to left; not helpful
    gglobs.notePad.verticalScrollBar().setValue(gglobs.notePad.verticalScrollBar().maximum())

    if error :
        if errsound:  playWav("error")
        gglobs.notePad.append("<span style='color:red;'>"   + ps + "</span>")
    else:
        gglobs.notePad.setTextColor(QColor(60, 60, 60))
        gglobs.notePad.append(ps)

    Qt_update()

    dprint(ps, debug=debug)


def commonPrint(ptype, *args, error=False):
    """Printing function to dprint, vprint, and wprint"""

    gglobs.xprintcounter       += 1   # the count of dprint and vprint commands
    tag = "{:23s} {:7s}: {:.>6d} ".format(longstime(), ptype, gglobs.xprintcounter) + gglobs.debugIndent

    for arg in args: tag += str(arg)

    writeFileA(gglobs.proglogPath, tag)

    if not gglobs.redirect:  tag = tag[11:]
    if error:                tag = TYELLOW + tag + TDEFAULT

    print(tag)



def arrprint(text, array):
    """ prints an array """

    print(text)
    for a in array:
        print("{:10s}: ".format(a), array[a])


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
    if verbose:   commonPrint("VERBOSE", *args)


def dprint(*args, debug=None ):
    """debug print:
    if debug is true then:
    - Write timestamp and args as a single line to progname.proglog file
    - Print args as single line
    else
    - do nothing
    """
    if debug == None: debug = gglobs.debug
    if debug:    commonPrint("DEBUG", *args)


def edprint(*args, debug=True ):
    """debug print:
    if debug is true then:
    - Write timestamp and args as a single line to progname.proglog file
    - Print args as single line
    else
    - do nothing
    """
    commonPrint("DEBUG", *args, error=True)


def exceptPrint(e, excinfo, srcinfo):
    """Print exception details (errmessage, file, line no)"""

    exc_type, exc_obj, exc_tb = excinfo         # use: excinfo = sys.exc_info()
    fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1] # which file?
    print(ERRORCOLOR, end='')
    dprint("{}".format(srcinfo), debug=True)
    dprint("EXCEPTION: '{}' in file: '{}' in line {}".format(e, fname, exc_tb.tb_lineno), NORMALCOLOR)
    if gglobs.devel:
        print(ERRORCOLOR, end='')
        dprint("EXCEPTION: Traceback:\n", traceback.format_exc(), NORMALCOLOR, debug=True) # more extensive info


def setDebugIndent(arg):
    """increases or decreased the indent of debug/verbose print"""

    if arg > 0:        gglobs.debugIndent += "   "
    else:              gglobs.debugIndent = gglobs.debugIndent[:-3]


def cleanHTML(text):
    return str(text).replace("<", "").replace(">", "") # replace < and >


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

    print(TGREEN + line + TDEFAULT)         # goes to terminal  (and *.stdlog)
    writeFileW(gglobs.proglogPath, line )   # goes to *.proglog (and *.stdlog)


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

    vprint("readBinaryFile: type:{}, len:{}, data=[:100]:".format(type(data), len(data)), data[0:100])

    return data


def writeBinaryFile(path, data):
    """Create file and write data to it as binary"""

    with open(path, 'wb') as f:
        f.write(data)


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


def isFileReadable(filepath):
    """is filepath readable"""

    if not os.access(filepath, os.R_OK) :
        fprint("File exists but cannot be read - check permission of file: {}".format(filepath), error=True)
        return False
    else:
        return True


def isFileWriteable(filepath):
    """As the dir can be written to, this makes only sense for existing files"""

    if os.path.isfile(filepath) and not os.access(filepath, os.W_OK) :
        #fprint(lheader)
        fprint("File {}".format(filepath), error=True)
        fprint("exists but cannot be written to - check permission of file", error=True)
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

    #~fontinfo = "Family:{}, fixed:{}, size:{}, style:{}, styleHint:{}, styleName:{}, weight:{}"\
    #~.format(fi.family(), fi.fixedPitch(), fi.pointSize(), fi.style(), fi.styleHint(), fi.styleName(), fi.weight())

    fontinfo = "Family:{}, fixed:{}, size:{}, style:{}, styleHint:{}, styleName:{}, weight:{}, exactMatch:{}"\
    .format(fi.family(), fi.fixedPitch(), fi.pointSize(), fi.style(), fi.styleHint(), fi.styleName(), fi.weight(), fi.exactMatch())

    return fontinfo


def printVarsStatus(origin = ""):
    """Print the current value of variables"""

    # not up-to-date!
    myVars  = ['gglobs.debug','gglobs.verbose', 'gglobs.dataPath', 'gglobs.mav' , 'gglobs.logcycle']
    myVars += ['gglobs.Xleft', 'gglobs.Xright', 'gglobs.Xunit', 'gglobs.Ymin', 'gglobs.Ymax', 'gglobs.Yunit']

    print("printVarsStatus: origin=", origin)
    for name in myVars:
        print("     {:35s} =    {}".format(name, eval(name)))


    print( "\n============================================ Globals " + "-" * 100)
    g = globals()
    for name in g:
        if name[0] != "Q": # exclude Qt stuff
            print("name:     {:35s} =    {}".format(name, eval(name)))


    print( "\n============================================= Locals " + "-" * 100)
    g = locals()
    for name in g:
        if name[0] != "Q":
            print("name:     {:35s} =    {}".format(name, eval(name)))


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
    for vname in gglobs.varnames:
        ret += "{:>8s}:{:5s}".format(vname, str(varlist[vname])).strip() + "  "

    return ret


def getNameSelectedVar():
    """Get the name of the variable currently selected in the drop-down box in
    the graph options"""

    vindex      = gglobs.exgg.select.currentIndex()
    vnameselect = gglobs.varnames[vindex]
    #print("vindex, vnameselect:", vindex, vnameselect)

    return vnameselect


def getConfigEntry(section, parameter, ptype):

    try:
        t = config.get(section, parameter).strip()
        if   ptype == "float":                  t = float(t)
        elif ptype == "int":                    t = int(float(t))
        elif ptype == "str":                    t = t
        elif ptype == "upper":                  t = t.upper()

        return t

    except:
        errmesg = "ALERT: Config {} {} not available".format(section, parameter)
        dprint(errmesg, debug=True)
        return "WARNING"


#
# Configuration file evaluation
#
def readGeigerLogConfig():
    """reading the configuration file, return if not available.
    Not-available or illegal options are being ignored with only a debug message"""

    global config # make config available to getConfigEntry()

    dprint("readGeigerLogConfig: using config file: ", gglobs.configPath)
    setDebugIndent(1)

    infostrHeader = "INFO: {:35s} {}"
    infostr       = "INFO:     {:35s}: {}"
    while True:

    # does the config file exist and can it be read?
        if not os.path.isfile(gglobs.configPath) or not os.access(gglobs.configPath, os.R_OK) :
            msg = """Configuration file <b>'geigerlog.cfg'</b> does not exist or is not readable.
                     <br><br>Please check and correct. Cannot continue, will exit."""
            gglobs.startup_failure = msg
            break

    # is it error free?
        try:
            config = configparser.ConfigParser()
            with open(gglobs.configPath) as f:
               config.read_file(f)
        except Exception as e:
            srcinfo = "Configuration file <b>'geigerlog.cfg'</b> cannot be interpreted."
            exceptPrint(e, sys.exc_info(), srcinfo)
            srcinfo += "<br><br>Note that duplicate entries are not allowed!"
            srcinfo += "<br><br>ERROR Message:<br>" + str(sys.exc_info()[1])
            srcinfo += "<br><br>Please check and correct. Cannot continue, will exit."
            gglobs.startup_failure = srcinfo
            break

    # the config file exists and can be read:
        vprint(infostrHeader.format("Startup values", ""))


    # Logging
        t = getConfigEntry("Logging", "logcycle", "float" )
        if t != "WARNING":
            if t >= 0.1:                            gglobs.logcycle = t
            vprint(infostr.format("Logcycle (sec)", gglobs.logcycle))


    # Folder data
        t = getConfigEntry("Folder", "data", "str" )
        if t != "WARNING":
            errmsg = "WARNING: "
            t = t.strip()
            try:
                if t == "":
                    pass                        # no change to default
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

                vprint(infostr.format("Data directory", gglobs.dataPath))
            except Exception as e:
                dprint(errmsg, "; Exception:", e, debug=True)



    # Window dimensions
        w = getConfigEntry("Window", "width", "int" )
        h = getConfigEntry("Window", "height", "int" )
        if w != "WARNING" and h != "WARNING":
            if w > 500 and w < 5000 and h > 100 and h < 5000:
                gglobs.window_width  = w
                gglobs.window_height = h
                vprint(infostr.format("Window dimensions (pixel)", "{} x {}".format(gglobs.window_width, gglobs.window_height)))
            else:
                vprint("WARNING: Config Window dimension out-of-bound; ignored: {} x {} pixel".format(gglobs.window_width, gglobs.window_height), debug=True)

    # Window size
        t = getConfigEntry("Window", "size", "upper" )
        if t != "WARNING":
            if    t == 'MAXIMIZED':    gglobs.window_size = 'maximized'
            #else:                      gglobs.window_size = None
            else:                      gglobs.window_size = 'auto'
            vprint(infostr.format("Window Size ", gglobs.window_size))

    # Window Style
        t = getConfigEntry("Window", "windowStyle", "upper" )
        if t != "WARNING":
            available_style = QStyleFactory.keys()
            #print("readGeigerLogConfig: WindowStyle available: ", available_style)
            if t in available_style:    gglobs.windowStyle = t
            else:                       gglobs.windowStyle = "auto"
            vprint(infostr.format("Window Style ", gglobs.windowStyle))


    # Manual
        t = getConfigEntry("Manual", "manual_name", "str" )
        if t != "WARNING":
            if t.upper() == 'AUTO' or t == "":
                gglobs.manual_filename = 'auto'
                vprint(infostr.format("Manual file", gglobs.manual_filename))
            else:
                manual_file = getProgPath() + "/" + t
                #print "readGeigerLogConfig manual_file:", manual_file
                if os.path.isfile(manual_file):     # does the file exist?
                    # it exists
                    gglobs.manual_filename = t
                    vprint(infostr.format("Manual file", gglobs.manual_filename))
                else:
                    # it does not exist
                    gglobs.manual_filename = 'auto'
                    vprint("WARNING: Manual file '{}' does not exist".format(t))


    # Graphic mav_initial
        t = getConfigEntry("Graphic", "mav_initial", "float" )
        if t != "WARNING":
            if   t >= 1:  gglobs.mav_initial = t
            else:         gglobs.mav_initial = 60
            gglobs.mav = gglobs.mav_initial
            vprint(infostr.format("Moving Average Initial (sec)", int(gglobs.mav_initial)))


    # Plotstyle
        vprint(infostrHeader.format("Plotstyle", ""))
        t = getConfigEntry("Plotstyle", "linewidth", "str" )
        if t != "WARNING":
            gglobs.linewidth           = t
            vprint(infostr.format("linewidth", gglobs.linewidth))

        t = getConfigEntry("Plotstyle", "markerstyle", "str" )
        if t != "WARNING":
            gglobs.markerstyle         = t
            vprint(infostr.format("markerstyle", gglobs.markerstyle))

        t = getConfigEntry("Plotstyle", "markersize", "str" )
        if t != "WARNING":
            gglobs.markersize          = t
            vprint(infostr.format("markersize", gglobs.markersize))


    # Defaults
        vprint(infostrHeader.format("Defaults", ""))

        # calibration 1st tube is 154 CPM/(µSv/h), =  0.0065 in units of µSv/h/CPM
        t = getConfigEntry("Defaults", "DefaultCalibration1st", "float" )
        if t != "WARNING":
            if t > 0:    gglobs.DefaultCalibration1st = t
            else:        gglobs.DefaultCalibration1st = 154 # CPM/(µSv/h), =  0.0065 in units of µSv/h/CPM
            vprint(infostr.format("DefaultCalibration1st", gglobs.DefaultCalibration1st))

        # calibration 2nd tube is 2.08 CPM/(µSv/h), =  0.48 in units of µSv/h/CPM
        t = getConfigEntry("Defaults", "DefaultCalibration2nd", "float" )
        if t != "WARNING":
            if t > 0:     gglobs.DefaultCalibration2nd = t
            else:         gglobs.DefaultCalibration2nd = 2.08 # CPM/(µSv/h), =  0.48 in units of µSv/h/CPM
            vprint(infostr.format("DefaultCalibration2nd", gglobs.DefaultCalibration2nd))

        # calibration 3rd tube is 154 CPM/(µSv/h), =  0.0065 in units of µSv/h/CPM
        t = getConfigEntry("Defaults", "DefaultCalibration3rd", "float" )
        if t != "WARNING":
            if t > 0:    gglobs.DefaultCalibration3rd = t
            else:        gglobs.DefaultCalibration3rd = 154 # CPM/(µSv/h), =  0.0065 in units of µSv/h/CPM
            vprint(infostr.format("DefaultCalibration3rd", gglobs.DefaultCalibration3rd))


    #
    # ValueScaling - it DOES modify the variable value!
    #
    # infostr = "INFO: {:35s}: {}"
        vprint(infostrHeader.format("ValueScaling", ""))
        for vname in gglobs.varnames:
            t = getConfigEntry("ValueScaling", vname, "upper" )
            if t != "WARNING":
                t = t.strip()
                if t == "":     pass                    # use value from gglobs
                else:           gglobs.ValueScale[vname] = t
                vprint(infostr.format("ValueScale['{}']".format(vname), gglobs.ValueScale[vname]))


    #
    # GraphScaling - it does NOT modify the variable value, only the plot value
    #
    # infostr = "INFO: {:35s}: {}"
        vprint(infostrHeader.format("GraphScaling", ""))
        for vname in gglobs.varnames:
            t = getConfigEntry("GraphScaling", vname, "upper" )
            if t != "WARNING":
                t = t.strip()
                if t == "":     pass                    # use value from gglobs
                else:           gglobs.GraphScale[vname] = t
                vprint(infostr.format("GraphScale['{}']".format(vname), gglobs.GraphScale[vname]))


    # GMCDevice
        vprint(infostrHeader.format("GMCDevice", ""))

        # GMCDevice Configuration
        t = getConfigEntry("GMCDevice", "GMCActivation", "upper" )
        if t != "WARNING":
            if t.strip() == "YES":          gglobs.GMCActivation = True
            else:                           gglobs.GMCActivation = False
            vprint(infostr.format("GMCActivation", gglobs.GMCActivation))

        if gglobs.GMCActivation: # show the other stuff only if activated
            gglobs.DevicesActive["GMC"] = True

            # GMCDevice Firmware Bugs
            t = getConfigEntry("GMCDevice", "locationBug", "str" )
            if t != "WARNING":
                ts = t.split(",")
                for i in range(0, len(ts)):   ts[i] = ts[i].strip()
                #print("ts:", ts)
                gglobs.locationBug     = ts
                vprint(infostr.format("Location Bug", gglobs.locationBug))

            # GMCDevice memory
            t = getConfigEntry("GMCDevice", "memory", "upper" )
            if t != "WARNING":
                if   t ==  '1MB':       gglobs.GMCmemory = 2**20   # 1 048 576
                elif t == '64KB':       gglobs.GMCmemory = 2**16   #    65 536
                else:                   gglobs.GMCmemory = 'auto'
                vprint(infostr.format("Memory", gglobs.GMCmemory))

            # GMCDevice SPIRpage
            t = getConfigEntry("GMCDevice", "SPIRpage", "upper" )
            if t != "WARNING":
                if   t == '2K':     gglobs.SPIRpage = 2048
                elif t == '4K':     gglobs.SPIRpage = 4096
                else:               gglobs.SPIRpage = 'auto'
                vprint(infostr.format("SPIRpage", gglobs.SPIRpage))

            # GMCDevice SPIRbugfix
            t = getConfigEntry("GMCDevice", "SPIRbugfix", "upper" )
            if t != "WARNING":
                if   t == 'YES':  gglobs.SPIRbugfix = True
                elif t == 'NO':   gglobs.SPIRbugfix = False
                else:             gglobs.SPIRbugfix = 'auto'
                vprint(infostr.format("SPIRbugfix", gglobs.SPIRbugfix))

            # GMCDevice configsize
            t = getConfigEntry("GMCDevice", "configsize", "upper" )
            if t != "WARNING":
                t = config.get("GMCDevice", "configsize")
                if   t == '256':  gglobs.configsize = 256
                elif t == '512':  gglobs.configsize = 512
                else:             gglobs.configsize = 'auto'
                vprint(infostr.format("configsize", gglobs.configsize))

            # GMCDevice calibration 1st tube
            # default in gglobs is 0.0065
            t = getConfigEntry("GMCDevice", "calibration", "upper" )
            if t != "WARNING":
                if t.strip() == 'AUTO': gglobs.calibration1st = "auto"
                else:
                    if float(t) > 0:    gglobs.calibration1st = float(t)
                    else:               gglobs.calibration1st = "auto"
                vprint(infostr.format("Calibration", gglobs.calibration1st))

            # GMCDevice calibration 2nd tube
            # default in gglobs is 0.194
            t = getConfigEntry("GMCDevice", "calibration2nd", "upper" )
            if t != "WARNING":
                if t.strip() == 'AUTO':  gglobs.calibration2nd = "auto"
                else:
                    if float(t) > 0:     gglobs.calibration2nd = float(t)
                    else:                gglobs.calibration2nd = "auto"
                vprint(infostr.format("Calibration 2nd tube", gglobs.calibration2nd))

            # GMCDevice voltagebytes
            t = getConfigEntry("GMCDevice", "voltagebytes", "upper" )
            if t != "WARNING":
                if   t.strip() == '1':      gglobs.voltagebytes = 1
                elif t.strip() == '5':      gglobs.voltagebytes = 5
                else:                       gglobs.voltagebytes = 'auto'
                vprint(infostr.format("voltagebytes", gglobs.voltagebytes))

            # GMCDevice endianness
            t = getConfigEntry("GMCDevice", "endianness", "upper" )
            if t != "WARNING":
                if   t.strip() == 'LITTLE': gglobs.endianness = 'little'
                elif t.strip() == 'BIG':    gglobs.endianness = 'big'
                else:                       gglobs.endianness = 'auto'
                vprint(infostr.format("endianness", gglobs.endianness))

            # GMCDevice variables
            t = getConfigEntry("GMCDevice", "variables", "str" )
            if t != "WARNING":
                if t.strip().upper() == "AUTO":     gglobs.GMCvariables = "auto"
                else:                               gglobs.GMCvariables = t.strip()
                vprint(infostr.format("variables", gglobs.GMCvariables))

            # GMCDevice nbytes
            t = getConfigEntry("GMCDevice", "nbytes", "upper" )
            if t != "WARNING":
                if t.strip() == "AUTO":     gglobs.nbytes = "auto"
                else:
                    nt = int(t.strip())
                    if nt in (2, 4):        gglobs.nbytes = nt
                    else:                   gglobs.nbytes = 2
                vprint(infostr.format("nbytes", gglobs.nbytes))


        # GMCSerialPort
            vprint(infostrHeader.format("  GMCSerialPort", ""))

            t = getConfigEntry("GMCSerialPort", "usbport", "str" )
            if t != "WARNING":
                gglobs.GMCusbport = t.strip()
                vprint(infostr.format("Using usbport", gglobs.GMCusbport))

            t = getConfigEntry("GMCSerialPort", "baudrate", "int" )
            if t != "WARNING":
                if t in gglobs.GMCbaudrates:               gglobs.GMCbaudrate = t
                vprint(infostr.format("Using baudrate", gglobs.GMCbaudrate))

            t = getConfigEntry("GMCSerialPort", "timeout", "float" )
            if t != "WARNING":
                if t > 0:   gglobs.GMCtimeout = t
                else:       gglobs.GMCtimeout = 3  # if zero or negative value given, set to 3
                vprint(infostr.format("Using timeout (sec)", gglobs.GMCtimeout))

            t = getConfigEntry("GMCSerialPort", "timeout_write", "float" )
            if t != "WARNING":
                if t > 0:   gglobs.GMCtimeout_write = t
                else:       gglobs.GMCtimeout_write = 1  # if zero or negative value given, set to 1
                vprint(infostr.format("Using timeout_write (sec)", gglobs.GMCtimeout_write))

            t = getConfigEntry("GMCSerialPort", "ttyS", "upper" )
            if t != "WARNING":
                if   t == 'INCLUDE':  gglobs.GMCttyS = 'include'
                else:                 gglobs.GMCttyS = 'ignore'
                vprint(infostr.format("Ports of ttyS type", gglobs.GMCttyS))


    # AudioCounter
        vprint(infostrHeader.format("AudioCounter", ""))
        # AudioCounter Activation
        t = getConfigEntry("AudioCounter", "AudioActivation", "upper" )
        if t != "WARNING":
            if t.strip() == "YES":      gglobs.AudioActivation = True
            else:                       gglobs.AudioActivation = False
            vprint(infostr.format("AudioActivation", gglobs.AudioActivation))

        if gglobs.AudioActivation: # show the other stuff only if activated
            gglobs.DevicesActive["Audio"] = True

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
                vprint(infostr.format("AudioDevice", gglobs.AudioDevice))

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
                vprint(infostr.format("AudioLatency", gglobs.AudioLatency))

            # AudioCounter PULSE Dir
            t = getConfigEntry("AudioCounter", "AudioPulseDir", "upper" )
            if t != "WARNING":
                if   t == "AUTO":           gglobs.AudioPulseDir = "auto"
                elif t == "NEGATIVE":       gglobs.AudioPulseDir = False
                elif t == "POSITIVE":       gglobs.AudioPulseDir = True
                else:                       pass # unchanged from default False
                vprint(infostr.format("AudioPulseDir", gglobs.AudioPulseDir))

            # AudioCounter PULSE Max
            t = getConfigEntry("AudioCounter", "AudioPulseMax", "upper" )
            if t != "WARNING":
                if t == "AUTO":             gglobs.AudioPulseMax = "auto"
                else:
                    t = float(t)
                    if t > 0 :              gglobs.AudioPulseMax = t
                    else:                   gglobs.AudioPulseMax = 32768
                vprint(infostr.format("AudioPulseMax", gglobs.AudioPulseMax))

            # AudioCounter LIMIT
            t = getConfigEntry("AudioCounter", "AudioThreshold", "upper" )
            if t != "WARNING":
                if t == "AUTO":             gglobs.AudioThreshold = "auto"
                else:
                    t = float(t)
                    if t > 0 and t < 100:   gglobs.AudioThreshold = t
                    else:                   gglobs.AudioThreshold = 60
                vprint(infostr.format("AudioThreshold", gglobs.AudioThreshold))

            # AudioCounter Variables
            t = getConfigEntry("AudioCounter", "AudioVariables", "str" )
            if t != "WARNING":
                if t.upper() == "AUTO":     gglobs.AudioVariables = "auto"
                else:                       gglobs.AudioVariables = t
                vprint(infostr.format("AudioVariables", gglobs.AudioVariables))


    # Gamma-Scout counter
        vprint(infostrHeader.format("GammaScoutDevice", ""))
        # Gamma-Scout Activation
        t = getConfigEntry("GammaScoutDevice", "GSActivation", "upper" )
        if t != "WARNING":
            if t.strip() == "YES":      gglobs.GSActivation = True
            else:                       gglobs.GSActivation = False
            vprint(infostr.format("GSActivation", gglobs.GSActivation ))

        if gglobs.GSActivation: # show the other stuff only if activated
            gglobs.DevicesActive["Gamma-Scout"] = True

            # Gamma-Scout variables
            t = getConfigEntry("GammaScoutDevice", "GSVariables", "str" )
            if t != "WARNING":
                if t.upper() == "AUTO":     gglobs.GSVariables = "auto"
                else:                       gglobs.GSVariables = t.strip()
                vprint(infostr.format("GSVariables", gglobs.GSVariables))

            # Gamma-Scout Calibration
            t = getConfigEntry("GammaScoutDevice", "GSCalibration", "str" )
            if t != "WARNING":
                if t.upper() == "AUTO":     gglobs.GSCalibration = "auto"
                else:
                    try:
                        tf = float(t.strip())
                        gglobs.GSCalibration = tf
                    except:
                        gglobs.GSCalibration = "auto"
                vprint(infostr.format("GSCalibration", gglobs.GSCalibration))


        # GammaScoutSerialPort
            vprint(infostrHeader.format("  GammaScoutSerialPort", ""))

            t = getConfigEntry("GammaScoutSerialPort", "GSusbport", "str" )
            if t != "WARNING":
                gglobs.GSusbport = t.strip()
                vprint(infostr.format("Using GSusbport", gglobs.GSusbport))

            t = getConfigEntry("GammaScoutSerialPort", "GSbaudrate", "int" )
            if t != "WARNING":
                if t in gglobs.GMCbaudrates: gglobs.GSbaudrate = t
                vprint(infostr.format("Using GSbaudrate", gglobs.GSbaudrate))

            t = getConfigEntry("GammaScoutSerialPort", "GStimeout", "float" )
            if t != "WARNING":
                if t > 0:   gglobs.GStimeout = t
                else:       gglobs.GStimeout = 3  # if zero or negative value given, set to 3
                vprint(infostr.format("Using GStimeout (sec)",gglobs.GStimeout))

            t = getConfigEntry("GammaScoutSerialPort", "GStimeout_write", "float" )
            if t != "WARNING":
                if t > 0:   gglobs.GStimeout_write = t
                else:       gglobs.GStimeout_write = 3  # if zero or negative value given, set to 3
                vprint(infostr.format("Using GStimeout_write (sec)",gglobs.GStimeout_write))

            t = getConfigEntry("GammaScoutSerialPort", "GSttyS", "upper" )
            if t != "WARNING":
                if    t == 'INCLUDE':  gglobs.GSttyS = 'include'
                else:                  gglobs.GSttyS = 'ignore'
                vprint(infostr.format("Ports of ttyS type", gglobs.GSttyS))


    # I2C ELV with BME280
        vprint(infostrHeader.format("I2CSensors", ""))
        # I2C Activation
        t = getConfigEntry("I2CSensors", "I2CActivation", "upper" )
        if t != "WARNING":
            if t.strip() == "YES":      gglobs.I2CActivation = True
            else:                       gglobs.I2CActivation = False
            vprint(infostr.format("I2CActivation", gglobs.I2CActivation ))

        if gglobs.I2CActivation: # show the other stuff only if activated
            gglobs.DevicesActive["I2C"] = True

            # I2C variables
            t = getConfigEntry("I2CSensors", "I2CVariables", "str" )
            if t != "WARNING":
                if t.upper() == "AUTO":     gglobs.I2CVariables = "auto"
                else:                       gglobs.I2CVariables = t.strip()
                vprint(infostr.format("I2CVariables", gglobs.I2CVariables))

        # I2CSerialPort
            vprint(infostrHeader.format("  I2CSerialPort", ""))

            t = getConfigEntry("I2CSerialPort", "I2Cusbport", "str" )
            if t != "WARNING":
                gglobs.I2Cusbport = t.strip()
                vprint(infostr.format("Using I2Cusbport", gglobs.I2Cusbport))

            t = getConfigEntry("I2CSerialPort", "I2Cbaudrate", "int" )
            if t != "WARNING":
                if t in gglobs.GMCbaudrates:                  gglobs.I2Cbaudrate = t
                vprint(infostr.format("Using I2Cbaudrate", gglobs.I2Cbaudrate))

            t = getConfigEntry("I2CSerialPort", "I2Ctimeout", "float" )
            if t != "WARNING":
                if t > 0:   gglobs.I2Ctimeout = t
                else:       gglobs.I2Ctimeout = 3  # if zero or negative value given, set to 3
                vprint(infostr.format("Using I2Ctimeout (sec)",gglobs.I2Ctimeout))

            t = getConfigEntry("I2CSerialPort", "I2Ctimeout_write", "float" )
            if t != "WARNING":
                if t > 0:   gglobs.I2Ctimeout_write = t
                else:       gglobs.I2Ctimeout_write = 1  # if zero or negative value given, set to 1
                vprint(infostr.format("Using I2Ctimeout_write (sec)",gglobs.I2Ctimeout_write))

            t = getConfigEntry("I2CSerialPort", "I2CttyS", "upper" )
            if t != "WARNING":
                if    t == 'INCLUDE':  gglobs.I2CttyS = 'include'
                else:                  gglobs.I2Cttys = 'ignore'
                vprint(infostr.format("Ports of ttyS type", gglobs.I2Cttys))



    # RadMonPlus
        vprint(infostrHeader.format("RadMonPlusDevice", ""))

        # RadMon Activation
        t = getConfigEntry("RadMonPlusDevice", "RMActivation", "upper" )
        if t != "WARNING":
            if t == "YES":                  gglobs.RMActivation = True
            else:                           gglobs.RMActivation = False
            vprint(infostr.format("RMActivation", gglobs.RMActivation ))

        if gglobs.RMActivation: # show the other stuff only if activated
            gglobs.DevicesActive["RadMon"] = True

            # RadMon Server IP
            t = getConfigEntry("RadMonPlusDevice", "RMServerIP", "str" )
            if t != "WARNING":
                if t.upper() == 'AUTO':         gglobs.RMServerIP = "auto"
                else:                           gglobs.RMServerIP = t.strip()
                vprint(infostr.format("RMServerIP", gglobs.RMServerIP ))

            # RadMon Server Port
            t = getConfigEntry("RadMonPlusDevice", "RMServerPort", "str" )
            if t != "WARNING":
                if t.upper() == 'AUTO':         gglobs.RMServerPort = "auto"
                else:                           gglobs.RMServerPort = abs(int(t))
                vprint(infostr.format("RMServerPort", gglobs.RMServerPort))

            # Radmon timeout
            t = getConfigEntry("RadMonPlusDevice", "RMTimeout", "upper" )
            if t != "WARNING":
                if t == 'AUTO':                    gglobs.RMTimeout = "auto"
                else:
                    if float(t) > 0:               gglobs.RMTimeout = float(t)
                    else:                          gglobs.RMTimeout = 3  # if zero or negative value given, then set to 3
                vprint(infostr.format("RMTimeout", gglobs.RMTimeout))

            # RadMon Server Folder
            t = getConfigEntry("RadMonPlusDevice", "RMServerFolder", "str" )
            if t != "WARNING":
                t = t.strip()
                # blank in folder name not allowed
                if " " in t or t.upper() == "AUTO":         gglobs.RMServerFolder = "auto"
                else:
                    gglobs.RMServerFolder = t
                    if gglobs.RMServerFolder[-1] != "/":    gglobs.RMServerFolder += "/"
                vprint(infostr.format("RMServerFolder", gglobs.RMServerFolder ))

            # RadMon calibration tube
            t = getConfigEntry("RadMonPlusDevice", "RMCalibration", "upper" )
            if t != "WARNING":
                if t.strip() == 'AUTO':         gglobs.RMCalibration = "auto"
                else:
                    if float(t) > 0:            gglobs.RMCalibration = float(t)
                    else:                       gglobs.RMCalibration = "auto"
                vprint(infostr.format("RMCalibration", gglobs.RMCalibration))

            # Radmon variables
            t = getConfigEntry("RadMonPlusDevice", "RMVariables", "str" )
            if t != "WARNING":
                if t.strip().upper() == "AUTO": gglobs.RMVariables = "auto"
                else:                           gglobs.RMVariables = t.strip()
                vprint(infostr.format("RMVariables", gglobs.RMVariables))


    # AmbioMon
        vprint(infostrHeader.format("AmbioMonDevice", ""))

        # AmbioMon Activation
        t = getConfigEntry("AmbioMonDevice", "AmbioActivation", "upper" )
        if t != "WARNING":
            if t == "YES":                      gglobs.AmbioActivation = True
            else:                               gglobs.AmbioActivation = False
            vprint(infostr.format("AmbioActivation", gglobs.AmbioActivation ))

        if gglobs.AmbioActivation: # show the other stuff only if activated
            gglobs.DevicesActive["AmbioMon"] = True

            # AmbioMon Server IP
            t = getConfigEntry("AmbioMonDevice", "AmbioServerIP", "str" )
            if t != "WARNING":
                if t.upper() == 'AUTO':         gglobs.AmbioServerIP = "auto"
                else:                           gglobs.AmbioServerIP = t.strip()
                vprint(infostr.format("AmbioServerIP", gglobs.AmbioServerIP ))

            #~ # AmbioMon Server Port
            #~ t = getConfigEntry("AmbioMonDevice", "AmbioServerPort", "upper" )
            #~ if t != "WARNING":
                #~ if t == 'AUTO':                 gglobs.AmbioServerPort = "auto"
                #~ else:                           gglobs.AmbioServerPort = abs(int(t))
                #~ vprint(infostr.format("AmbioServerPort", gglobs.AmbioServerPort ))

            # AmbioMon timeout
            t = getConfigEntry("AmbioMonDevice", "AmbioTimeout", "upper" )
            if t != "WARNING":
                if t == 'AUTO':                     gglobs.AmbioTimeout = "auto"
                else:
                    if float(t) > 0:                gglobs.AmbioTimeout = float(t)
                    else:                           gglobs.AmbioTimeout = 3  # if zero or negative value given, then set to 3
                vprint(infostr.format("AmbioTimeout",gglobs.AmbioTimeout))

            #~ # AmbioMon Server Folder
            #~ t = getConfigEntry("AmbioMonDevice", "AmbioServerFolder", "str" )
            #~ if t != "WARNING":
                #~ t = t.strip()
                #~ # blank in folder name not allowed
                #~ if " " in t or t.upper() == "AUTO": gglobs.AmbioServerFolder = "auto"
                #~ else:
                    #~ gglobs.AmbioServerFolder = t
                    #~ if gglobs.AmbioServerFolder[-1] != "/": gglobs.AmbioServerFolder += "/"
                #~ vprint(infostr.format("AmbioServerFolder", gglobs.AmbioServerFolder ))

            # AmbioMon calibration
            # default in gglobs is 0.0065 µSv/h/CPM
            t = getConfigEntry("AmbioMonDevice", "AmbioCalibration", "upper" )
            if t != "WARNING":
                if t == 'AUTO':         gglobs.AmbioCalibration = "auto"
                else:
                    if float(t) > 0:    gglobs.AmbioCalibration = float(t)
                    else:               gglobs.AmbioCalibration = "auto"
                vprint(infostr.format("AmbioCalibration", gglobs.AmbioCalibration))

            # AmbioMon variables
            t = getConfigEntry("AmbioMonDevice", "AmbioVariables", "str" )
            if t != "WARNING":
                if t.upper() == "AUTO":     gglobs.AmbioVariables = "auto"
                else:                       gglobs.AmbioVariables = t
                vprint(infostr.format("AmbioVariables", gglobs.AmbioVariables))


    # LabJack U3 with probe EI1050
        vprint(infostrHeader.format("LabJackDevice", ""))
        # LabJack Activation
        t = getConfigEntry("LabJackDevice", "LJActivation", "upper" )
        if t != "WARNING":
            if t.strip() == "YES":      gglobs.LJActivation = True
            else:                       gglobs.LJActivation = False
            vprint(infostr.format("LJActivation", gglobs.LJActivation ))

        if gglobs.LJActivation: # show the other stuff only if activated
            gglobs.DevicesActive["LabJack"] = True

            # LabJack variables
            t = getConfigEntry("LabJackDevice", "LJVariables", "str" )
            if t != "WARNING":
                if t.upper() == "AUTO":     gglobs.LJVariables = "auto"
                else:                       gglobs.LJVariables = t
                vprint(infostr.format("LJVariables", gglobs.LJVariables))


#~#testing Raspi preliminary
    #~# Raspi
        #~vprint(infostrHeader.format("RaspiDevice", ""))
        #~# Raspi Activation
        #~gglobs.RaspiActivation = True
        #~gglobs.DevicesActive["Raspi"] = True



    # Radiation World Maps
        vprint(infostrHeader.format("Worldmaps", ""))
        t = getConfigEntry("Worldmaps", "GMCmapWebsite", "str" )
        if t != "WARNING":
            gglobs.GMCmap["Website"] = t.strip()

        t = getConfigEntry("Worldmaps", "GMCmapURL", "str" )
        if t != "WARNING":
            gglobs.GMCmap["URL"]  = t.strip()

        t = getConfigEntry("Worldmaps", "GMCmapSSID", "str" )
        if t != "WARNING":
            gglobs.GMCmap["SSID"]  = t.strip()

        t = getConfigEntry("Worldmaps", "GMCmapPassword", "str" )
        if t != "WARNING":
            gglobs.GMCmap["Password"] = t.strip()

        t = getConfigEntry("Worldmaps", "GMCmapUserID", "str" )
        if t != "WARNING":
            gglobs.GMCmap["UserID"] = t.strip()

        t = getConfigEntry("Worldmaps", "GMCmapCounterID", "str" )
        if t != "WARNING":
            gglobs.GMCmap["CounterID"] = t.strip()

        t = getConfigEntry("Worldmaps", "GMCmapPeriod", "str" )
        if t != "WARNING":
            gglobs.GMCmap["Period"] = t.strip()

        for a in gglobs.cfgMapKeys:
            vprint(infostr.format(a, gglobs.GMCmap[a]))


        break # don't forget to break!

    setDebugIndent(0)


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
    version_status.append(["Qt",                "{}".format(QT_VERSION_STR)])
    version_status.append(["PyQt",              "{}".format(PYQT_VERSION_STR)])
    version_status.append(["SIP",               "{}".format(SIP_VERSION_STR)])

    version_status.append(["pyserial",          "{}".format(serial_version)])
    version_status.append(["matplotlib",        "{}".format(mpl_version)])
    version_status.append(["numpy",             "{}".format(np_version)])
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


def playWav(stype = "ok"):
    """Play a wav message, either 'ok' or 'err' """

    _stype = stype.lower()
    if    _stype == "ok": path = os.path.join(gglobs.gresPath, 'bip2.wav') # stype = "ok"
    else:                 path = os.path.join(gglobs.gresPath, 'burp.wav') # stype = "err"

    # Play
    try:
        data, samplerate = sf.read(path)
        #print("samplerate: ", samplerate)

        sd.play(data, samplerate, latency='high')
        status = sd.wait()
    except Exception as e:
        dprint("playWav failed: Exception: ", e, debug=True)

    return

#testing play sine wave:
    # play sine wave
    samplerate = 44100          # samples per sec
    sounddur   = 0.3            # seconds
    soundfreq  = 440            # Kammerton A
    soundamp   = 0.5            # amplitude; mit steigender Amplitude Verzerrungen

    # create the time base
    t = (np.arange(samplerate * sounddur)) / samplerate
    #~print("t: ", t)

    for i in range(1, 5):
        # create the data
        outdata = soundamp * (np.sin(2 * np.pi * soundfreq*(1.414**i) * t))   # Tonleiter
        #~print("outdata raw: ", outdata)
        sd.play(outdata, samplerate * 2, latency='high')
        status = sd.wait()
        time.sleep(0.2)


def signal_handler(signal, frame):
    """Allows to handle the signals SIGINT, SIGTSTP, SIGQUIT, SIGUSR1, SIGUSR2"""

    # Requires these commands in main:
    # signal.signal(signal.SIGINT,  signal_handler)   # to handle CTRL-C
    # signal.signal(signal.SIGTSTP, signal_handler)   # to handle CTRL-Z
    # signal.signal(signal.SIGQUIT, signal_handler)   # to handle CTRL-\
    # signal.signal(signal.SIGUSR1, signal_handler)   # to handle user signal1
    # signal.signal(signal.SIGUSR2, signal_handler)   # to handle user signal2

    print()
    dprint("signal_handler: signal: {}, frame: {}".format(signal, frame))

    if signal == 2:                 # SIGINT CTRL-C to shutdown
        dprint('signal_handler: received SIGINT from CTRL-C Keyboard Interrupt - Exiting')

    elif signal == 20:              # SIGTSTP CTRL-Z to shutdown
        dprint('signal_handler: received SIGTSTP from CTRL-Z - Exiting')

    else:                           # unexpected signal
        dprint('signal_handler: signal:', signal, ", Undefined signal action")
        return

    gradmon.terminateRadMon()
    sys.exit()                      # to exit on CTRL-C this is needed
                                    # the GeigerLog closeEvent is NOT activated!


def scaleVarValues(variable, value, scale):
    """
    Apply the 'Scaling' declared in configuration file geigerlog.cfg
    Return: the scaled value (or original in case of error)
    NOTE:   scale is in upper-case, but may be empty or NONE
    """
    scale = scale.upper()

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
        dprint(msg, debug=True)
        fprint(msg, error=True)
        fprint("Returning original value", error=True)
        scaledValue = value

    wprint("scaleVarValues: variable:{}, original value:{}, orig scale:{}, mod scale:'{}', scaled value:{}".format(variable, value, scale, ls, scaledValue))

    return round(scaledValue, 2)


def scaleGraphValues(variable, value, scale):
    """
    Apply the 'Scaling' declared in configuration file geigerlog.cfg
    Return: the scaled value (or original in case of error)
    NOTE:   scale is in upper-case, but may be empty or NONE
    """
    # example:   cpm = scaleVarValues("CPM2nd", cpm,   gglobs.ValueScale["CPM2nd"])
    #            P   = scaleGraphValues("P",    press, gglobs.GraphScale['P'])

    scale = scale.upper()
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
        #~print("++++++++++++++++++getting scaled value")
        # a divide by zero in the formula only results in this warning:
        # <string>:1: RuntimeWarning: divide by zero encountered in true_divide
        scaledValue = eval(ls)
        #~print("++++++++++++++++++got      scaled value")
    except Exception as e:
        msg = "ERROR scaling variable:'{}' formula:'{}', errmsg: {}".format(variable, scale, e)
        dprint(msg, debug=True)
        fprint(msg, error=True)
        fprint("Returning original value", error=True)
        scaledValue = value

    wprint("scaleGraphValues: variable:{}, original value:\n{} \nand more..."                 .format(variable, value[:5]))
    wprint("scaleGraphValues: orig scale:{}, mod scale:'{}', scaled value:\n{} \nand more..." .format(scale, ls, scaledValue[:5]))

    return scaledValue


def readSerialConsole():
    """read the ESP32 terminal output"""

    return # results in problems when GMC counter is connected

    mypath = os.path.join(gglobs.dataPath, "esp32.termlog")
    dv = "/dev/ttyUSB0" # device
    br = 115200         # baudrate
    to = 3              # timeout
    wto = 1             # write timeout
    byteswaiting = 0    # to avoid reference error

    if gglobs.terminal == None:
        gglobs.terminal = serial.Serial(dv, br, timeout=to, write_timeout=wto)
        with open(mypath, 'wt', encoding="UTF-8", errors='replace', buffering = 1) as f:
            f.write("Starting at: {}\n".format(longstime()))

    else:
        #while gglobs.terminal.in_waiting > 0:
        while True:
            try:
                bytesWaiting = gglobs.terminal.in_waiting
            except:
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
            except:
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


def setTime():
    # to be defined

    print("------------------------getLogValues")
    print("timetag:", timetag)
    print("time.gmtime():", time.gmtime())
    print("time.time() / 86400.0:", time.time() / 86400.0)
    print("time.mktime(time.gmtime()) / 86400.0:", time.mktime(time.gmtime()) / 86400.0)
    print("timeJULIAN:", timeJULIAN)


    print("gglobs.JULIAN111:", gglobs.JULIAN111)

    #print("datetime.tzinfo:", datetime.tzinfo)

    #print("datetime.timezone:", datetime.timezone)
    print("datetime.timezone.utc:", datetime.timezone.utc)  # datetime.timezone.utc: UTC+00:00


    print("time.strftime('%z', .time.gmtime()):", time.strftime("%z", time.gmtime()))
    #time.strftime('%z', .time.gmtime()): +0000 NOTE: %z (small cap) is deprecated

    print("time.strftime('%z', .time.localtime()):", time.strftime("%z", time.localtime()))
    # time.strftime('%z', .time.localtime()): +0100 NOTE: %z (small cap) is deprecated

    print("time.strftime('%Z', .time.gmtime()):", time.strftime("%Z", time.gmtime()))
    # time.strftime('%Z', .time.gmtime()): GMT

    print("time.strftime('%Z', .time.localtime()):", time.strftime("%Z", time.localtime()))
    # time.strftime('%Z', .time.localtime()): CET

    print("time.tzname:", time.tzname)
    # time.tzname: ('CET', 'CEST')

    print("time.timezone:", time.timezone)
    # time.timezone: -3600


# making a label click-sensitive
class ClickLabel(QLabel):
    def __init__(self, parent):
        QLabel.__init__(self, parent)

    def mousePressEvent(self, event):
        colorPicker()


def colorPicker():
    """Called by the color picker button in the graph options.
    Changes color of the selected variable"""

    if gglobs.currentConn == None: return # no color change unless something is loaded

    colorDial   = QColorDialog()
    color       = colorDial.getColor()
    if color.isValid():
        vprint("colorPicker: new color picked:", color.name())
        gglobs.exgg.btnColor.setStyleSheet("QLabel { border: 1px solid silver;  border-radius: 3px; background-color: %s ; }" % (color.name()))
        addMenuTip(gglobs.exgg.btnColor, gglobs.exgg.btnColorText + str(color.name()))
        gglobs.exgg.btnColor.setText("")
        QApplication.processEvents()

        # tuples cannot be changed, but dicts can
        vname                  = getNameSelectedVar()
        gglobs.varStyle[vname] = (color.name(), gglobs.varStyle[vname][1])
        gglobs.exgg.applyGraphOptions()

    gglobs.exgg.notePad.setFocus()



def printProgError(*args):
    print("PROGRAMMING ERROR !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
    dprint(*args, debug=True)
    sys.exit(-1)


def Qt_update():
    """updates the Qt window"""

    QApplication.processEvents()
    #~if gglobs.devel: wprint("--------------------Qt_update: QApplication.processEvents()")


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

    fncname = "getPortList: "

    wprint(fncname + "use symlinks: ", symlinks)
    setDebugIndent(1)

    try:
        if symlinks:    lp = serial.tools.list_ports.comports(include_links=True)  # symlinks shown
        else:           lp = serial.tools.list_ports.comports(include_links=False) # default; no symlinks shown
        lp.sort()
    except Exception as e:
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

