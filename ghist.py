#!/usr/bin/python3
# -*- coding: UTF-8 -*-

"""
ghist.py - GeigerLog commands to read and parse the history data from Geiger
counter device or from file.

Writes *.bin, *.lst and *.his file. *.his file can be used for graphing; it
has identical format as the *.log file
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
__credits__         = ["Phil Gillaspy"]
__license__         = "GPL3"

# credits:
# device command coding taken from:
# Phil Gillaspy, https://sourceforge.net/projects/gqgmc/
# and document 'GQ-RFC1201.txt'
# (GQ-RFC1201,GQ Geiger Counter Communication Protocol, Ver 1.40 Jan-2015)

import sys
import re                               # regex
from   operator import itemgetter       # used in sortHist

import gglobs                           # global settings
import gcommands                        # only getSPIR is used here
from   gutils import *                  # all utilities


def makeHIST(sourceHIST, binFilePath, lstFilePath, hisFilePath):
    """make the History by reading data either from file or from device,
    parse them, sort them by date&time, and write into files"""

    str_data_origin = u"Downloaded {} from device '{}'"
    #
    # get binary HIST data - either from file or from device
    #
    if sourceHIST == "Binary File":     # from file
        fprint("Reading data from binary file:", binFilePath)
        hist    = readBinaryFile(binFilePath)
        if b"ERROR" in hist[:6]: # hist contains error message
            error = -1
            return (error, "ERROR: Cannot Make History: " + hist)

        if hist[0:11] == b"DataOrigin:":
            data_origin = hist[11:128].rstrip(b' ').decode('UTF-8')
            vprint(gglobs.verbose, "DataOrigin: len:{}: {}".format(len(data_origin), data_origin))
            hist = hist[128:]

        else:
            data_origin = str_data_origin.format("<Date Unknown>", "<Device Unknown>")
            vprint(gglobs.verbose,  "no Data Origin label found, " + data_origin)

        # only for TESTING: to cut a short piece of bin data
        #writeBinaryFile(binFilePath + ".short", hist[0:100])

    elif sourceHIST == "Device":         # from device

        #data_origin = str_data_origin.format(shortstime(), gglobs.deviceDetected)
        data_origin = str_data_origin.format(stime(), gglobs.deviceDetected)
        fprint("Reading from connected device:", "{}".format(gglobs.deviceDetected))

        hist = b""

        page    = gglobs.SPIRpage # 4096 or 2048, see: getDeviceProperties
        FFpages = 0               # number of successive pages having only FF

        #
        # Cleaning pipeline BEFORE reading history
        #
        dprint(gglobs.debug, "makeHIST: Cleaning pipeline BEFORE reading history")
        extra = gcommands.getExtraByte()

#### TESTING
####        gglobs.memory = 2**13

        for address in range(0, gglobs.memory, page):       # prepare to read all memory
            time.sleep(0.1) # fails occasionally to read all data when
                            # sleep is only 0.1; still not ok at 0.2 sec
                            # wieder auf 0.1, da GQ Dataviewer deutlich scneller ist
            fprint("Reading page of size {} @address:".format(page)  , address)
            rec, error, errmessage = gcommands.getSPIR(address , page)
            if error == 0 or error == 1:
                hist += rec
                if error == 1: fprint("Reading error:", "Recovery succeeded")

                if rec.count(b'\xFF') == page:
                    #print "rec.count('\xFF'):", rec.count('\xFF')
                    FFpages += 1
                else:
                    FFpages  = 0

                if not gglobs.fullhist and FFpages * page >= 8192: # 8192 is 2 pages of 4096 byte each
                    txt = "Found {} successive {} B-pages (total {} B), as 'FF' only - ending reading".format(FFpages, page, FFpages * page)
                    dprint(gglobs.debug, txt)
                    fprint(txt)
                    break
            else: # error = -1
                # non-recovered error occured
                dprint(gglobs.debug, "ERROR: in makeHIST: ", errmessage, "; exiting from makeHist")
                return (error, "ERROR: Cannot Get History: " + errmessage)

        #
        # Cleaning pipeline AFTER reading history
        #
        dprint(gglobs.debug, "makeHIST: Cleaning pipeline AFTER reading history")
        extra = gcommands.getExtraByte()

    else:
        # "Parsed File" - is already *.his; does not need makeHIST
        return (0, "")


    histlen     = len(hist)          # Total length; should always be 64k or 1MB, now: could be any length!
    histFF      = hist.count(b'\xFF') # total count of FF bytes

    histRC      = hist.rstrip(b'\xFF')       # after right-clip FF (removal of all trailing 0xff)
    histRClen   = len(histRC)                # total byte count
    histRCFF    = histRC.count(b'\xFF')      # total count of FF in right-clipped data

    fprint("Count of bytes as read:"           , "{} Bytes".format(histlen))
    fprint("Count of data bytes:"              , "{} Bytes".format(histRClen))

    fprint("Count of FF bytes - Total:"        , "{} Bytes".format(histFF))
    fprint("Count of FF bytes - Trailing:"     , "{} Bytes".format(histlen - histRClen))
    fprint("Count of FF bytes - Within data:"  , "{} Bytes".format(histRCFF))

    # writing data from device as binary; add the device info to the beginning
    if sourceHIST == "Device":
        exthist = (b"DataOrigin:" + data_origin.encode() + b" " * 128 )[0:128] + hist
        vprint(gglobs.verbose, "hist: len:{}, exthist: len:{} exthist:{}".format(len(hist), len(exthist), exthist[:128]))
        fprint("Writing binary data to:", binFilePath, debug=True)
        try:
            writeBinaryFile(binFilePath, exthist)
        except Exception as e:
            error       = -1
            errmessage  = "ERROR writing *bin file"
            exceptPrint(e, sys.exc_info(), errmessage)
            return (error, "ERROR: Cannot Get History: " + errmessage)

# Preparing the *.lst file
    # prepare to write binary data to '*.lst' file (= lstFilePath) in human readable format
    lstlines  = "#History Download - Binary Data in Human-Readable Form\n"  # write header
    lstlines += "#{}\n".format(data_origin)
    lstlines += "#Format: bytes:  index:value  as: 'hex=dec :hex=dec|'\n"
    #print("histInt:", type(histRC), len(histRC), histRC)
    histInt   = list(histRC)                                        # convert string to list of int
    #print("histInt:", type(histInt), len(histInt), histInt)
    ppagesize = 1024                                                    # for the breaks in printing

    # This reads the full hist data, but clipped for FF, independent of the
    # memory setting of the currently selected counter
    for i in range(0, histRClen, ppagesize):
        for j in range(0, ppagesize, 4):
            lstline =""
            for k in range(0, 4):
                if j + k >= ppagesize:   break
                l  = i + j + k
                if l >= histRClen:         break
                lstline += "{:04x}={:<5d}:{:02x}={:<3d}|".format(l, l, histInt[l], histInt[l])
            lstlines += lstline[:-1] + "\n"
            if l >= histRClen:         break

        lstlines += "Reading Page {} of size {} bytes complete; next address: 0x{:04x}={:5d} {}\n".format(i/ppagesize, ppagesize, i+ppagesize, i+ppagesize, "-" * 6)
        #print "(l +1)", (l+1), "(l +1) % 4096", (l+1) % 4096
        if (l + 1) % 4096 == 0 :
            lstlines += "Reading Page {} of size {} Bytes complete {}\n".format(i/4096, 4096, "-" * 35)
        if l >= histRClen:         break

    if histRClen < histlen:
        lstlines += "Remaining {} Bytes to the end of history (size:{}) are all ff\n".format(histlen -histRClen, histlen)
    else:
        lstlines += "End of history reached\n"

    fprint("Writing data as list to:", lstFilePath)
    writeFileW(lstFilePath, lstlines, linefeed = False)
# end for *.lst file

# for Devel  - highlight the FF bytes in hist
    if gglobs.devel: FFbytes(hist, binFilePath)

# Prepare the *.his file
    # parse HIST data; preserve a copy with parsing comments if on debug
    fprint("Parsing binary file", debug=True)
    histLogList, histLogListComment = parseHIST(hist, hisFilePath)

    hisClines  = "#HEADER, File created from History Download Binary Data\n"  # header
    hisClines += "#ORIGIN: {}\n".format(data_origin)
    hisClines += "#FORMAT: '<#>ByteIndex, Date&Time, CPM, CPS' (Line beginning with '#' is comment)\n"

# write the *.parse file when debug = True
    if gglobs.debug:
        path = hisFilePath + ".parse"
        #fprint("Writing commented parsed data to:", path, debug=True)
        with open(path, 'wt', encoding="utf_8", errors='replace', buffering = 1) as f:
            f.write(hisClines)
            for line in histLogListComment:
                # ensure ASCII chars
                asc, ordasc, ordflag = getTrueASCII(line)
                f.write(asc + "\n")
                if ordflag :
                    f.write(ordasc + "\n")

# sort parsed data by date&time
    fprint("Sorting parsed data on time", debug=True)
    histLogList = sortHistLog(histLogList)

    """ Not relevant when all FF are ignored in parser!
    # remove trailing records if they have a count resulting from FF
    # i.e. 255 in CPM or 255*50 = 15300 in CPS mode
    trailFF = 0
    byteindex_first = None
    byteindex_last  = None
    while True:
        x, t, c = histLogList[-1].split(",", 2) #byteindex. time, count
        #print x,t,c, type(c), len(histLogList)
        try:
            intc = int(c)
        except:
            break
        if intc == 255 or intc == 15300:
            if trailFF == 0:
                byteindex_last  = x
            else:
                byteindex_first = x

            trailFF += 1
            histLogList.pop()
        else:
            break
    if trailFF > 0:
        fprint("Trailing FF records removed:", "{} records (ByteIndex{} to{})".format(trailFF, byteindex_first, byteindex_last))
    else:
        fprint("Trailing FF records removed:", "None found; nothing removed")
    """

    fprint("Writing parsed & sorted data to:", hisFilePath, debug=True)
    with open(hisFilePath, 'wt', encoding="utf_8", errors='replace', buffering = 1) as f:
        f.write(hisClines)
        for line in histLogList:
            # ensure ASCII chars
            asc, ordasc, ordflag = getTrueASCII(line)
            f.write(asc + "\n")
            if ordflag :
                f.write(ordasc + "\n")
                fprint("ERROR in History: Found non-ASCII characters: ", ordasc, error=True, debug=True)

# end for *.his file

    return (0, "")


def getTrueASCII(line):
    """gets line and returns true ASCII string plus info on ASCII failures"""

    asc     = ""
    ordasc  = "#"
    ordflag = False
    for i in range(0, len(line)):
        ai = ord(line[i])
        if ai < 128 and ai > 31:
            asc    += line[i]
            ordasc += line[i]
        else:
            ordflag = True
            asc    += "."
            ordasc += "[{}]".format(ai)

    return asc, ordasc, ordflag


def parseHIST(hist, hisFilePath):
    """Parse history
    return data in logfile format
    """

    global histCPSCum

    i               = 0     # counter for starting point byte number
    first           = 0     # byte index of first occurence of datetimetag
    cpms            = 0     # counter for CPMs read, so time can be adjusted
    cpxValid        = 1     # for CPM data = 1, for CPS data = 60 (all is recorded as CPM!)

    # search for first occurence of a Date&Time tag
    # must include re.DOTALL, otherwise a \x0a as in time 10h20:30 will
    # be considered as newline characters and ignored!
    DateTimeTag      = re.compile(b"\x55\xaa\x00......\x55\xaa[\x00\x01\x02\x03]", re.DOTALL)

    DateTimeTagList  = DateTimeTag.finditer(hist)
    for dtt in DateTimeTagList:
        first = dtt.start()
        break

    i = first                       # the new start point for the parse
    dprint(gglobs.debug, "parseHIST: byte index first Date&Time tag: {}".format(first))

    hist = hist + hist[:i]          # concat with the part missed due to overflow

    hist = hist.rstrip(b'\xff')     # right-clip FF (removal of all trailing 0xff)
    rec  = list(hist)               # convert string to list of int
    lh   = len(rec)

    histLogList         = []
    histLogListComment  = []
    histCPSCum          = [0] * 60  # cumulative values of CPS; initial set = all zero

    CPSmode             = True      # history saving mode is CPS by default

    CPSmodeFormat = " {:5d}, {:19s},       , {:6d}"  # CPS: empty value for CPM
    CPMmodeFormat = " {:5d}, {:19s}, {:6d},       "  # CPM: empty value for CPS

    # NOTE: ###################################################################
    # After reading the DateTime tag the next real count is assumed to come at
    # the time of the DateTime tag. That is why the cpms   += 1 command comes
    # as last command for each condition
    # may not be true; CPM save every minute seems to be off by ~30sec!

#    while i < lh - 3:  # if tag is ASCII bytes there will be a call of the 3rd byte
#                       # ???? what about 3 and 4 byte records???
    while i < lh:       #  range is: 0, 1, 2, ..., lh - 1

        r = rec[i]
        if r == 0x55:
            if rec[i+1] == 0xaa:

#TESTING (for the mess of GQ's redefinitions of the coding 55 AA sequences
                #if i > 150 and i < 300: rec[i+2] = 2

                if rec[i+2] == 0:   # timestamp coming
                    YY = rec[i+3]
                    MM = rec[i+4]
                    DD = rec[i+5]
                    hh = rec[i+6]
                    mm = rec[i+7]
                    ss = rec[i+8]
                    # rec[i+ 9] = 0x55 end marker bytes; always fixed
                    # rec[i+10] = 0xAA (actually unnecessary since length is fixed too)
                    rectime = "20{:02d}-{:02d}-{:02d} {:02d}:{:02d}:{:02d}".format( YY, MM, DD, hh, mm, ss)
                    rectimestamp = datestr2num(rectime)

                    dd = rec[i+11]   # saving tag
                    if   dd == 0:
                        savetext      = "history saving off"
                        saveinterval = 0
                        cpxValid     = 1
                        CPSmode      = True         # though there won't be any data
                        cpms         = 0

                    elif dd == 1:
                        savetext      = "CPS, save every second"
                        saveinterval = 1
                        cpxValid     = 1
                        CPSmode      = True
                        cpms         = 1

                    elif dd == 2:
                        # it looks like there is a ~30sec delay before the new
                        # timing loop sets in. NOT taken into account!
                        savetext      = "CPM, save every minute"
                        saveinterval = 60
                        cpxValid     = 1
                        CPSmode      = False
                        cpms         = 0

                    elif dd == 3:
                        # after changing to hourly saving the next value is saved an hour later
                        # so cpms must be set to plus 1!
                        savetext      = "CPM, save every hour as hourly average"
                        saveinterval = 3600
                        cpxValid     = 1
                        CPSmode      = False
                        cpms         = 1


                    elif dd == 4:
                        # save only if exceeding threshold
                        savetext      = "CPS, save every second if exceeding threshold"
                        saveinterval = 1
                        cpxValid     = 1
                        CPSmode      = True
                        cpms         = 1

                    elif dd == 5:
                        # save only if exceeding threshold
                        savetext      = "CPM, save every minute if exceeding threshold"
                        saveinterval = 60
                        cpxValid     = 1
                        CPSmode      = False
                        cpms         = 0

                    else:
                        # ooops. you were not supposed to be here
                        savetext      = "ERROR: FALSE READING OF HISTORY SAVE-INTERVALL = {:3d} (allowed is: 0,1,2,3,4,5)".format(dd)
                        dprint(True, savetext)
                        saveinterval = 0        # do NOT advance the time
                        cpxValid     = -1       # make all counts negative to mark illegitimate data
                        CPSmode      = True     # just to define the mode
                        cpms         = 0

                    rs = "#{:5d}, {:19s}, Date&Time Stamp; Type:'{:}', Interval:{:} sec".format(i, rectime, savetext, saveinterval)
                    histLogList.       append(rs)
                    histLogListComment.append(rs)

                    i   += 12

                elif rec[i+2] == 1: #double data byte coming
                    msb     = rec[i+3]
                    lsb     = rec[i+4]
                    cpx     = msb * 256 + lsb
                    if CPSmode: cpx = cpx & 0x3fff # count rate limit CPS = 14bit!
                    cpx     = cpx * cpxValid

                    parsecomment = ", ---double data bytes---"
                    parseValueAdder(i, cpx, CPSmode, rectimestamp, cpms, saveinterval, parsecomment, savetext, histLogList, histLogListComment)


                    i      += 5
                    cpms   += 1

                # the following is the consequence of the highly unprofessionall
                # mess created by GQ by redefining the definition of the meaning
                # of the coding:  in some firmware (likely 1.18 and 1.21 for
                # 500+ counters) different association.
                # Claimed to be changed "soon", yet leaves are permanent problem
                #
                # http://www.gqelectronicsllc.com/forum/topic.asp?TOPIC_ID=5331   Reply #50, 21.8.2016
                # Quote:
                #   Sorry, the fix is not out yet. The current official firmware still has
                #   55 AA 00: timestamp
                #   55 AA 01: double data byte
                #   55 AA 02: triple data byte
                #   55 AA 03: quadruple data byte
                #   55 AA 04: Note/Location text
                #   55 AA xx: anything else not used
                #   for 500 and 600+
                # End Quote

                elif rec[i+2] >= 5: # should NEVER be found as it is not used (currently)!
                                    # this is also not strictly correct, as for
                                    # counters other that 500+ the limit should not
                                    # be 5 but 3!

                    cpxValid = -1
                    cpx      = rec[i+3] * cpxValid

                    parsecomment = ", ---invalid qualifier for 0x55 0xAA sequence: '0x{:02X}' ---".format(rec[i+2])
                    parseValueAdder(i, cpx, CPSmode, rectimestamp, cpms, saveinterval, parsecomment, savetext, histLogList, histLogListComment)

                    i      += 1
                    cpms   += 1

                else:
                    # workaround for the mess created by GQ
                    if gglobs.deviceDetected in ("GMC-500+Re 1.18", "GMC-500+Re 1.21"):
                        histMess = {"ASCII" : 4,
                                    "Triple": 2,
                                    "Quad"  : 3,
                                   }
                    else: # 300series and else
                        histMess = {"ASCII" : 2,
                                    "Triple": 3,
                                    "Quad"  : 4,
                                   }

                    if  rec[i+2] == histMess["ASCII"]: #ascii bytes coming
                        cpmtime = datetime.datetime.fromtimestamp(rectimestamp + cpms * saveinterval).strftime('%Y-%m-%d %H:%M:%S')
                        count   = rec[i+3]
                        #print("i:", i, "count:", count)

                        if (i + 3 + count) <= lh:
                            asc     = ""
                            for c in range(0, count):
                                asc += chr(rec[i + 4 + c])
                            rs      = "#{:5d}, {:19s}, Note/Location: '{}' ({:d} Bytes) ".format(i, cpmtime, asc, count)
                        else:
                            rs      = "#{:5d} ,{:19s}, Note/Location: '{}' (expected {:d} Bytes, got only {}) ".format(i, cpmtime, "ERROR: not enough data in History", count, lh - i - 3)
                        histLogList.       append(rs)
                        histLogListComment.append(rs)

                        i      += count + 4

                    elif rec[i+2] == histMess["Triple"]: #triple data byte coming
                        msb     = rec[i+3]
                        isb     = rec[i+4]
                        lsb     = rec[i+5]
                        cpx     = (msb * 256 + isb) * 256 + lsb
                        cpx     = cpx * cpxValid

                        parsecomment = ", ---triple data bytes---"
                        parseValueAdder(i, cpx, CPSmode, rectimestamp, cpms, saveinterval, parsecomment, savetext, histLogList, histLogListComment)

                        i      += 6
                        cpms   += 1

                    elif rec[i+2] == histMess["Quad"]: #quadruple data byte coming
                        msb     = rec[i+3]
                        isb     = rec[i+4]
                        isb0    = rec[i+5]
                        lsb     = rec[i+6]
                        cpx     = ((msb * 256 + isb) * 256 + isb0) * 256 + lsb
                        cpx     = cpx * cpxValid

                        parsecomment = ", ---quadruple data bytes---"
                        parseValueAdder(i, cpx, CPSmode, rectimestamp, cpms, saveinterval, parsecomment, savetext, histLogList, histLogListComment)


                        i      += 7
                        cpms   += 1

            else: #0x55 is genuine cpm, no tag code
                cpx     = r * cpxValid

                parsecomment = ", ---0x55 is genuine, no tag code---"
                parseValueAdder(i, cpx, CPSmode, rectimestamp, cpms, saveinterval, parsecomment, savetext, histLogList, histLogListComment)

                i      += 1
                cpms   += 1

        elif r == 0xff: # real count or 'empty' value?
            if gglobs.keepFF:
                cpx     = r * cpxValid

                parsecomment = ", ---real count or 'empty' value?---"
                parseValueAdder(i, cpx, CPSmode, rectimestamp, cpms, saveinterval, parsecomment, savetext, histLogList, histLogListComment)
                cpms   += 1
            i += 1

        else:
            cpx     = r * cpxValid

            parsecomment = ", ---single digit---"
            parseValueAdder(i, cpx, CPSmode, rectimestamp, cpms, saveinterval, parsecomment, savetext, histLogList, histLogListComment)
            i      += 1
            cpms   += 1

    return histLogList, histLogListComment


def parseValueAdder(i, cpx, CPSmode, rectimestamp, cpms, saveinterval, parsecomment, savetext, histLogList, histLogListComment):
    """Add the parse results to the *.his list and commented *.his.parse list"""

    global histCPSCum

    cpmtime = datetime.datetime.fromtimestamp(rectimestamp + cpms * saveinterval).strftime('%Y-%m-%d %H:%M:%S')

    CPMmodeFormat = " {:5d}, {:19s}, {:6d},       " # CPM: empty value for CPS
    CPXmodeFormat = " {:5d}, {:19s}, {:6d}, {:6d}"  # CPX: values for both CPM and CPS
    if CPSmode: # measurement is CPS
        histCPSCum.append(cpx)          # add new data as 61st element (= #60)
        histCPSCum  = histCPSCum[1:]    # ignore element #0, get only 1...60
        cpm         = sum(histCPSCum)
        rs          = CPXmodeFormat.format(i, cpmtime, int(cpm), cpx)

    else: # CPM mode
        histCPSCum  = [0] * 60
        rs = CPMmodeFormat.format(i, cpmtime, cpx) # measurement is CPM

    histLogList.       append(rs)
    histLogListComment.append(rs + parsecomment + savetext)


def sortHistLog(histLogList):
    """The ringbuffer technology for the Geiger counter history buffer makes it
    possible that late data come first in the buffer. Time Sorting corrects this"""


    dprint(gglobs.debug, "sortHistLog:")
    debugIndent(1)

    # Extract the Date&Time col and put as new 1st col for sorting
    sortlines =[]
    for hline in histLogList:
        try:
            x, t, c = hline.split(",", 2) #byteindex. time, count cpm, count cps
        except Exception as e:
            srcinfo = "ERROR on split histLogList" + str(hline)
            exceptPrint(e, sys.exc_info(), srcinfo)
            return histLogList

        sortlines.append([t, hline])

    #print( "sortlines: len, type:", len(sortlines), type(sortlines))
    #for i in range(15): print( sortlines[i])

    # sort all records by the newly created Date-Time column
    newsortlines = sorted(sortlines, key=itemgetter(0))
    #print( "sorted lines: len, type:", len(newsortlines), type(newsortlines))
    #for i in range(15): print( newsortlines[i])

    # after sorting done on the first column, we need only the second column
    secondColumn = [row[1] for row in newsortlines]
    #print("secondColumn only: len, type:", len(secondColumn), type(secondColumn))
    #for i in range(15): print(secondColumn[i])

    debugIndent(0)

    return secondColumn


def FFbytes(hist, FilePath):
    """highlight the FF bytes of the bin history by creating a text file showing
    the memory layout as an ASCII graph with '.' as non-FF, and 'ÿ' as FF"""

    linelen   = 128
    lstlines  = "Mark FF values in hist file as 'ÿ', else with '.'; line length={}\n".format(linelen)
    lstlines += "_________|" * 12 + "________\n"
    lh        = len(hist)
    #print("hist:", hist)
    histInt   = list(hist)    # convert bytes to list of int
    #print("histInt:", histInt)

    for i in range(0, lh, linelen):
        lstline =""
        for j in range(0, linelen):
            l  = i + j
            if l >= lh: break

            if histInt[l] == 255:   s = "\xff"
            else:                   s = "."
            lstline += s

        lstlines += lstline + "\n"
    #print("lstlines:", lstlines)  # takes too much space in printout to terminal

    writeFileW(FilePath + ".FF", lstlines, linefeed = False)
