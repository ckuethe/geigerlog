#!/usr/bin/python
# -*- coding: UTF-8 -*-

"""
utilities
include in programs with:

from utils include *
"""

import sys
import os
import io
import inspect
import time         # time formatting and more
import datetime     # date and time conversions
from PyQt4 import QtGui

import gglobs

__author__      = "ullix"
__copyright__   = "Copyright 2016"
__credits__     = [""]
__license__     = "GPL"


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
    """Return full path of the proglog file"""
    dp = os.path.join(gglobs.dataPath, gglobs.progName + ".proglog")
    return dp


def getPlogPath():
    """Return full path of the geigerlog.plog file"""
    dp = os.path.join(gglobs.dataPath, gglobs.progName + ".stdlog")
    return dp


def getConfigPath():
    """Return full path of the geigerlog.cfg file"""
    dp = os.path.join(gglobs.progPath, gglobs.progName + ".cfg")
    return dp


def stime():
    """Return current time as YYYY-MM-DD HH:MM:SS"""
    return time.strftime("%Y-%m-%d %H:%M:%S")


def datestr2num(string_date):
    """convert a Date&Time string in the form YYYY-MM-DD HH:MM:SS
    to a Unix timestamp"""

    #print "string_date", string_date
    try:
        dt=time.mktime(datetime.datetime.strptime(string_date, "%Y-%m-%d %H:%M:%S").timetuple())
    except:
        dprint(True, "ERROR in datestr2num: Date as String: '{}'".format(string_date))
        newstrdate = '2099-09-09 09:09:09'
        dprint(True, "                      replacing with: '{}'".format(newstrdate))
        dt=time.mktime(datetime.datetime.strptime(newstrdate, "%Y-%m-%d %H:%M:%S").timetuple())

    return dt


def convertBytesToAscii(bytestring):
    """get a bytestring with all bytes from 0...255, and convert to string
    which has ASCII characters when printable and '.' else"""

    asc = ""
    if bytestring != None:
        for i in range(0, len(bytestring)):
            a = ord(bytestring[i])
            if a < 128 and a > 31:
                asc += bytestring[i]
            else:
                asc += "."

    return asc


def cleanStringToAscii(string):
    """get a string with all bytes from 0...255, and convert to string
    which has ASCII characters from ord=0 ...128 and '.' else"""

    asc = ""
    for i in range(0, len(string)):
        a = ord(string[i])
        if a < 128:
            asc += string[i]
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

    #print "orig:", inspect.currentframe().__name__
    #print "orig:", inspect.getmembers()
    #print "orig:",sys._getframe(1).f_code.co_name

    return fn, sys._getframe(1).f_code.co_name, lineno


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


def getUnicodeString(arg):
    try:
        arg1 = unicode(arg)
    except:
        arg1 = convertBytesToAscii(arg) # in some strange circumstances

    return arg1


def fprint(*args):
    """print all args in the GUI"""

    forcedebug = False

    ps = u"{:35s}".format(unicode(args[0]))     # 1st arg
    for s in range(1, len(args)):               # skip 1st arg
        if args[s] == "debug":
            forcedebug = True
        else:
            ps += getUnicodeString(args[s])

    gglobs.NotePad.append(ps)
    QtGui.QApplication.processEvents()

    dprint(forcedebug, ps)


def strprint(self, *args):
    """return all args as a formatted string"""

    ps = "{:23s}".format(str(args[0]))
    for s in range(1, len(args)):
        #ps += str(args[s])
        ps += getUnicodeString(args[s])

    return ps + "\n"


def vprint(verbose, *args):
    """verbose print:
    if verbose is true then:
    - Write timestamp and args as a single line to progname.proglog file
    - Print args as single line
    else
    - do nothing
    """

    if verbose:
        tag      = u"{:19s}  VERBOSE ".format(stime())
        line     = u""
        #line     = u"{:35s}".format(args[0])
        #for s in range(1, len(args)):
        for s in range(0, len(args)):
            line += getUnicodeString(args[s])

        line = gglobs.debugindent + line
        writeFileA(gglobs.proglogPath, tag + line)

        if gglobs.redirect:
            line = cleanStringToAscii(line)
            print tag + line
        else:
            print "VERBOSE:", line


def dprint(debug, *args):
    """debug print:
    if debug is true then:
    - Write timestamp and args as a single line to progname.proglog file
    - Print args as single line
    else
    - do nothing
    """

    if debug:
        tag      = u"{:19s}  DEBUG   ".format(stime())
        line     = u""

        for arg in args:
            line += getUnicodeString(arg) + u" "

        line = gglobs.debugindent + line
        writeFileA(gglobs.proglogPath, tag + line)

        #if sys.stdout.isatty(): print "DEBUG:  ", line  # print only if in console macht Problem in Windows
        if gglobs.redirect:
            line = cleanStringToAscii(line)
            print tag + line
        else:
            print "DEBUG  :", line


def exceptPrint(e, excinfo, srcinfo):
    """Print exception details (errmessage, file, line no)"""

    exc_type, exc_obj, exc_tb = excinfo
    fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
    dprint(True, "ERROR: '{}' in file: '{}' in line {}".format(e, fname, exc_tb.tb_lineno))
    dprint(True, srcinfo)


def debugIndent(arg):
    if arg > 0:
        gglobs.debugindent += "   "
    else:
        gglobs.debugindent = gglobs.debugindent[:-3]


def clearProgramLogFile():
    """To clear the debug file at the beginning of each run"""

    tag      = u"{:19s}  PROGRAM {:s}  pid: {:d} ".format(stime(), gglobs.progName, os.getpid())
    line     = tag + u"#"*100

    if gglobs.redirect:
        sys.stdout = open(gglobs.plogPath, 'w', buffering=0)
        sys.stdout = open(gglobs.plogPath, 'a', buffering=0)
        sys.stderr = open(gglobs.plogPath, 'a', buffering=0)

    writeFileW(gglobs.proglogPath, line )

    print line


def readBinaryFile(path):
    """Read all of the file into data; return data as string"""

    try:
        with io.open(path, 'rb') as f:
            data = f.read()
        vprint(gglobs.verbose, "readBinaryFile: data=[:100]:", data[:100])
        return data
    except:
        dprint(True, "sys.exc_info():", sys.exc_info())
        return "ERROR: Could not read file: " + path


def writeBinaryFile(path, data):
    """Create file and write data to it as binary"""

    with io.open(path, 'wb') as f:
        f.write(data)


def detectFileType(path):

    try:
        import chardet
        detector = chardet.universaldetector.UniversalDetector()
        detector.reset()
        linecount = 0
        starttime = time.time()
        for line in file(path, 'rb'):
            #print "line:", line[:-1]
            detector.feed(line)
            linecount += 1
            if detector.done: break
            if (time.time() - starttime) > 2: break
        detector.close()
        dprint(gglobs.debug, "detectFileType: Path:{}, Linecounts:{}, Result:{}".format(path, linecount, detector.result))

        if detector.result['confidence'] > 0.7:
            return detector.result['encoding']
        else:
            return None
    except:
        dprint(gglobs.debug, "Problem with using detector chardet: ", sys.exc_info())
        dprint(gglobs.debug, "Detector chardet can be installed via: 'pip install chardet' from the CMD line")
        return None


def readFile(path):
    """Read all of the file into data; return data as string"""

    enc = detectFileType(path)
    #print "encoding determined:", enc

    if enc == None: enc = "utf_8"
    #print "encoding selected=", enc

    try:
        with io.open(path, 'rt', encoding=enc, errors='replace') as f:
            data = f.read()
        vprint(gglobs.verbose, "readFile: data=[:100]:\n", data[:100])
        return data
    except:
        data = [u"ERROR: readFile: Could not read file: " + path]
        dprint(True, sys.exc_info())
        return data


def readFileLines(path):
    """Read all of the file into lines, ending with linefeed.
    return data as list of lines"""

    enc = detectFileType(path)
    #print "encoding determined:", enc
    if enc == None: enc = "utf_8"
    #print "encoding selected=", enc

    try:
        with io.open(path, 'rt', encoding= enc, errors='replace') as f:
            data = f.readlines()
        #vprint(gglobs.verbose,  "readFileLines: data=[:5]:\n", data[:5])
        return data
    except:
        data = [u"ERROR: readFileLines: Could not read file: " + path]
        dprint(True, sys.exc_info())
        return data


def writeFileW(path, writestring, linefeed = True):
    """Create file if not available, and write to it if writestring
    is not empty; add linefeed unless excluded"""

    #writestring = unicode(writestring)
    #print "writeFileW: path:", path, ", write: '", writestring, "'", type(writestring)
    with io.open(path, 'wt', encoding="utf_8", errors='replace', buffering = 1) as f:
        if writestring > "":
            if linefeed: writestring += "\n"
            f.write(writestring)


def writeFileA(path, writestring):
    """Write-Append data; add linefeed"""

    #writestring = unicode(writestring)
    #print "writeFileA: path:", path, ", write: '", writestring, "'", type(writestring)
    with io.open(path, 'at', encoding="utf_8", errors='replace', buffering = 1) as f:
        f.write((writestring + u"\n"))



def beep():
    """make ping if on console and if no Qt4 sound"""

    print "\7"


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
