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
from PyQt4 import QtGui

import gglobs


# tricks
# For generic non full screen applications, you can turn off line wrapping by
# sending an appropriate escape sequence to the terminal:
#   tput rmam
# This mode can be cancelled with a similar escape:
#   tput smam
# also: https://tomayko.com/blog/2004/StupidShellTricks



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
    return time.strftime("%Y-%m-%d %H:%M:%S")


def datestr2num(string_date):
    """convert a Date&Time string in the form YYYY-MM-DD HH:MM:SS
    to a Unix timestamp in sec"""

    #print "string_date", string_date
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
    # 736830.573587963 --> '2018-05-16 13:45:58'           # first 19 bytes

    nd = str(mpld.num2date(num))[:19]

    return nd


def xxxconvertBytesToAscii(bytestring):
    """get a string with all bytes from 0...255, and convert to string
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


def xxxgetUnicodeString(arg):
    try:
        arg1 = str(arg)
    except:
        arg1 = convertBytesToAscii(arg) # in some strange circumstances

    return arg1


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

    spanstop = "<span style='color:black;'></span><br>"
    return spanstop + "==== {} {}".format(txt, "=" * max(0, (68 - len(txt))))


def bell():
    """ring a bell when in the terminal """

    print("\7")


def fprint(*args, error = False):
    """print all args in the GUI"""

    forcedebug = False

    ps = "{:35s}".format(str(args[0]))     # 1st arg
    for s in range(1, len(args)):          # skip 1st arg
        if args[s] == "debug":
            forcedebug = True
        else:
            #ps += getUnicodeString(args[s])
            ps += str(args[s])

    if error :
        gglobs.mediaErr.play()
        gglobs.NotePad.append("<span style='color:red;'>" + ps + "</span> ")
    else:
        gglobs.NotePad.append(ps)

    QtGui.QApplication.processEvents()

    dprint(forcedebug, ps)


def commonPrint(ptype, *args):
    """Printing function to vprint and dprint"""

    tag      = "{:19s} {:7s}: ".format(stime(), ptype)+ gglobs.debugindent
    for arg in args:
        #s1 = str(arg)
        #s2 = getUnicodeString(arg)
        #if s1 != s2:
        #    print("------------------------------------------------------s1=s2:", s1 == s2, "'{}'   '{}'".format(s1, s2))
        #tag += getUnicodeString(arg)
        tag += str(arg)
    writeFileA(gglobs.proglogPath, tag)

    if gglobs.redirect:
        print(tag)
    else:
        print(tag[11:])



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

    if arg > 0:
        gglobs.debugindent += "   "
    else:
        gglobs.debugindent = gglobs.debugindent[:-3]


def clearProgramLogFile():
    """To clear the debug file at the beginning of each run"""

    # "Mµßiggang ist ein ° von Läßterei"
    tag      = "{:19s} PROGRAM: pid:{:d} ########### {:s}  ".format(stime(), os.getpid(), "GeigerLog {} -- mi no mär pfupf underm füdli !".format(gglobs.__version__))
    line     = tag + "#" * 50

    if gglobs.redirect:
        # text with buffering=0 not possible in Python 3
        sys.stdout = open(gglobs.stdlogPath, 'w', buffering=1) # deletes content
        sys.stdout = open(gglobs.stdlogPath, 'a', buffering=1)
        sys.stderr = open(gglobs.stdlogPath, 'a', buffering=1)

    print(line)                             # goes to terminal (and *.stdlog)
    writeFileW(gglobs.proglogPath, line )   # goes to *.proglog only


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


def xxxdetectFileType(path):
    """using chardet to determine the encoding of a file"""

    try:
        import chardet
        detector  = chardet.universaldetector.UniversalDetector()
        detector.reset()
        linecount = 0
        starttime = time.time()

        with open(path, 'rb') as f:      # binary read!
            data = f.readlines()
        linecount_total = len(data)
        #for i in range(10): print(1, data[i])

        for line in data:
            #print "line:", line[:-1]
            detector.feed(line)
            linecount += 1
            if detector.done:
                print("----------------------detector.done:", detector.done)
                break
            #if (time.time() - starttime) > 2: break
        detector.close()
        dprint(gglobs.debug, "detectFileType: Path:{}, Linecounts: Total:{}, at Break:{}, Result:{}".format(path, linecount_total, linecount, detector.result))

        return detector.result['encoding']

    except Exception as e:
        srcinfo = "Problem with using filetype detector chardet"
        exceptPrint(e, sys.exc_info(), srcinfo)
        dprint(gglobs.debug, "Detector chardet can be installed via: 'pip install chardet' from the CMD line")
        return None


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

    #writestring = unicode(writestring)
    #print "writeFileW: path:", path, ", write: '", writestring, "'", type(writestring)
    with open(path, 'wt', encoding="UTF-8", errors='replace', buffering = 1) as f:
        #utf8sign = chr(0xEF) + chr(0xBB) + chr(0xBF)
        # geht nicht, wird als UTF-8 codiert :-))
        # ï»¿2018-05-08 19:34:23  PROGRAM pi
        #f.write('\xEF\xBB\xBF')
        #f.write(utf8sign)
        if writestring > "":
            if linefeed: writestring += "\n"
            f.write(writestring)


def writeFileA(path, writestring):
    """Write-Append data; add linefeed"""

    #writestring = unicode(writestring)
    #print "writeFileA: path:", path, ", write: '", writestring, "'", type(writestring)
    with open(path, 'at', encoding="UTF-8", errors='replace', buffering = 1) as f:
        f.write((writestring + "\n"))


def beep():
    """make ping if on console and if no Qt4 sound"""

    print("\7")


def printVarsStatus(debug, origin = ""):
    """Print the current value of selected variables"""

    # not up-to-date!
    myVars  = ['gglobs.debug','gglobs.verbose', 'gglobs.dataPath', 'gglobs.mav' , 'gglobs.logcycle']
    myVars += ['gglobs.Xleft', 'gglobs.Xright', 'gglobs.Xunit', 'gglobs.Xscale', 'gglobs.Ymin', 'gglobs.Ymax', 'gglobs.Yunit', 'gglobs.Yscale', 'gglobs.cpmflag']

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
