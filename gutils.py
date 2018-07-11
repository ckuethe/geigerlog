#!/usr/bin/python
# -*- coding: UTF-8 -*-

"""
utilities
include in programs with:

from utils include *
"""

import sys
import os
import inspect
import codecs
import time         # time formatting and more
import datetime     # date and time conversions
import gglobs
from PyQt4 import QtGui

__author__      = "ullix"
__copyright__   = "Copyright 2016"
__credits__     = [""]
__license__     = "GPL"


def getProgPath():
    """Return full path of the program directory"""

    dp = os.path.dirname(os.path.realpath(__file__))

    return dp


def getDataPath(datadir):
    """Return full path of the data directory"""

    dp = getProgPath() + datadir

    return dp


def getIconPath(icondir):
    """Return full path of the icon directory"""

    dp = getProgPath() + icondir

    return dp


def stime():
    """Return current time as YYYY-MM-DD HH:MM:SS"""
    return time.strftime("%Y-%m-%d %H:%M:%S")


def datestr2num(string_date):
    """convert a Date&Time string in the form YYYY-MM-DD HH:MM:SS
    to a Unix timestamp"""

    #print "string_date", string_date
    dt=time.mktime(datetime.datetime.strptime(string_date, "%Y-%m-%d %H:%M:%S").timetuple())

    return dt

def convertBytesToAscii(bytestring):
    """get a bytestring with all bytes from 0...255, and convert to string
    which has ASCII characters when printable and '.' else"""

    asc = ""
    for i in range(0, len(bytestring)):
        a = ord(bytestring[i])
        if a < 128 and a > 31:
            asc += bytestring[i]
        else:
            asc += "."

    return asc


def lineno():
    """Return the current line number."""

    return inspect.currentframe().f_back.f_lineno


def orig(thisfile):
    """Return name of calling program and line number of call
    requires that this routine is called by orig(__file__)"""

    lineno = inspect.currentframe().f_back.f_lineno
    fn = os.path.basename(thisfile)

    return fn, lineno


def remove_trailing(rlist, remove_value=None):
    """remove trailing characters in a list"""

    i = len(rlist)
    while i>0 and rlist[i-1] == remove_value:
        i -= 1
    return rlist[:i]


def printruler():
    """to  give a measure for output formatting"""

    fprint("123456789-" * 10)


def header(txt):
    """position txt within '====' string"""

    return u"\n==== {} {}".format(txt, u"=" * max(0, (68 - len(txt))))


def fprint(*args):
    """print all args in the GUI"""

    forcedebug = False

    ps = u"{:35s}".format(unicode(args[0]))     # 1st arg
    for s in range(1, len(args)):               # skip 1st arg
        if args[s] == "debug":
            forcedebug = True
        else:
            ps += unicode(args[s])

    gglobs.NotePad.append(ps)
    QtGui.QApplication.processEvents()

    #dprint(forcedebug or gglobs.debug, ps)
    dprint(forcedebug, ps)


def strprint(self, *args):
    """return all args as a formatted string"""

    ps = "{:23s}".format(str(args[0]))
    for s in range(1, len(args)):
        ps += str(args[s])

    return ps + "\n"


def vprint(verbose, *args):
    """verbose print: if verbose is true then print all args"""

    if verbose:
        #line = "{:35s}".format(str(args[0]))
        line = u"{:35s}".format(args[0])
        for s in range(1, len(args)):
            #line += str(args[s])
            line += unicode(args[s])
        if sys.stdout.isatty(): print "VERBOSE:", line # print only if in console


def dprint(debug, *args):
    """debug print:
    if debug is true then:
    - Write timestamp, name of calling prog, process id, and
      args as a single line to progname.proglog file
    - Print args as single line
    else
    - do nothing
    """

    if debug:
        progname = os.path.basename(sys.argv[0])
        pid      = os.getpid()
        tag      = u"{:19s}  {:s}  {:d} ".format(stime(), progname, pid)
        line     = u""

        for arg in args:
            line += unicode(arg) + " "

        progname_base     = os.path.splitext(progname)[0]
        writeFileA(gglobs.dataPath + progname_base + ".proglog", tag + line)

        if sys.stdout.isatty(): print "DEBUG:  ", line  # print only if in console


def clearProgramLogFile():
    """To clear the debug file at the beginning of each run"""

    progname        = os.path.basename(sys.argv[0])
    progname_base   = os.path.splitext(progname)[0]
    writeFileW(gglobs.dataPath + progname_base + ".proglog", "")


def readFile(path):
    """Read all of the file into data; return data as string"""

    try:
        f = open(path, "r")
        #f = codecs.open(path, "r", 'utf-8')
        data = f.read()
        #print " data:", data
        f.close
        return data
    except:
        return "ERROR: Could not read file: " + path


def readFileLines(path):
    """Read all of the file into lines, ending with linefeed.
    return data as list of lines"""

    try:
        #f = open(path, "r")
        f = codecs.open(path,'r','utf-8')
        data = f.readlines()
        f.close
        return data
    except:
        data = [u"ERROR: Could not read file: " + path]
        return data


def writeFileW(path, writestring, linefeed = True):
    """Create file if not available, and write to it if writestring
    is not empty; add linefeed unless excluded"""
    writestring = unicode(writestring)

    f = open(path, "w", buffering=1)
    if writestring > "":
        if linefeed: writestring += "\n"
        #f.write(writestring)
        f.write(writestring.encode('utf8'))
    f.close


def writeFileA(path, writestring):
    """Write-Append data; add linefeed"""

    # buffering=0 to switch off buffering
    # buffering=1 to select line buffering (only usable in text mode)
    #f = open(path, "a", buffering=1)
    f = open(path, "a", buffering=0)
    f.write((writestring + "\n").encode("utf-8"))
    f.close


def beep():
    """make ping if on console and if no Qt4 sound"""

    if sys.stdout.isatty(): print "\7",


def printVarsStatus(debug, origin = ""):
    """Print the current value of selected variables"""

    # not up-to-date!
    myVars  = ['gglobs.debug','gglobs.verbose', 'gglobs.dataPath', 'gglobs.mav' , 'gglobs.logcycle']
    myVars += ['Xleft', 'Xright', 'Xunit', 'Xscale', 'Ymin', 'Ymax', 'Yunit', 'Yscale', 'cpmflag']

    dprint(gglobs.debug,"origin=", origin)
    for name in myVars:
        dprint(gglobs.debug,"     {:35s} =    {}".format(name, eval(name)))

    """
    print "Globals -----------------------"
    item = ""
    g = globals()
    for item in g:
        print item
    for name in g:
        dprint(gglobs.debug,"  {:35s} =    {}".format(name, eval(name)))


    print "Locals -----------------------"
    g = locals()
    for item in g:
        print item
    for name in g:
        dprint(gglobs.debug,"  {:35s} =    {}".format(name, eval(name)))
    """
