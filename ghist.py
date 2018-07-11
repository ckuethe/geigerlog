#!/usr/bin/python
# -*- coding: UTF-8 -*-

"""
ghist.py - reads and parses the history data from device or file
and writes to bin, lst and his file. His file can be used for graphing; it
has identical format to the log file

device command coding taken from:
Phil Gillaspy, https://sourceforge.net/projects/gqgmc/
and document 'GQ-RFC1201.txt'
(GQ-RFC1201,GQ Geiger Counter Communication Protocol, Ver 1.40 Jan-2015)
"""

import sys
import re           # regex
from operator import itemgetter

import gglobs       # global settings
import gcommands    # only getSPIR is used here
from gutils import *

__author__      = "ullix"
__copyright__   = "Copyright 2016"
__credits__     = ["Phil Gillaspy"]
__license__     = "GPL"


def makeHIST(ser, sourceHIST, binFilePath, lstFilePath, hisFilePath):
    """make the History by reading data either from file or from device,
    parse them, sort them by date&time, and write into files"""

    #
    # get binary HIST data - either from file or from device
    #
    if sourceHIST == "Binary File":     # from file
        fprint("Reading data from binary file:", binFilePath)

        hist    = readFile(binFilePath)
        if "ERROR" in hist[:6]:
            return (-1, "ERROR: Cannot Make History: " + hist)

        # only for testing: to cut a short piece of bin data
        #writeFileW(binFilePath + ".short", hist[0:100], linefeed = False)

    elif sourceHIST == "Device":         # from device
        fprint("Reading data from:"             , "device: {}".format(gglobs.device))

        hist    = ""
        page    = gglobs.page # e.g. 4096, or 2048, see: defineDevice(index)
        FFpages = 0           # number of successive pages having only FF

        #
        # Cleaning pipeline BEFORE reading history - relevant at least for GMC-500
        #
        dprint(gglobs.debug, "makeHIST: Cleaning pipeline BEFORE reading history")
        extra = gcommands.getExtraByte(gglobs.ser)

        for address in range(0, gglobs.memory, page):       # prepare to read all memory
            time.sleep(0.1) # fails occasionally to read all data when
                            # sleep is only 0.1; still not ok at 0.2 sec
                            #wieder auf 0.1, da GQ Datavier deutlich scneller ist
            fprint("Reading page of size {} @address:".format(page)  , address)
            rec, error, errmessage = gcommands.getSPIR(ser, address , page)
            if error == 0 or error == 1:
                hist += rec
                if error == 1: fprint("Reading error:", "Recovery succeeded")

                if rec.count('\xFF') == page:
                    #print "rec.count('\xFF'):", rec.count('\xFF')
                    FFpages += 1
                else:
                    FFpages  = 0

                if not gglobs.fullhist and FFpages * page >= 8192: # 8192 is 2 pages of 4096 byte each
                    txt = "Found {} successive {} B-pages (total {} B), as 'FF' only - ending reading".format(FFpages, page, FFpages * page)
                    dprint(gglobs.debug, txt)
                    fprint(txt)
                    break
            else:
                # non-recovered error occured
                fprint("History: Reading error:", "Recovery failed; cannot continue. Error:", errmessage)
                dprint(gglobs.debug, "ERROR: in makeHIST: ", errmessage, "; exiting from makeHist")
                return (error, "ERROR: Cannot Make History: " + errmessage)

        #
        # Cleaning pipeline AFTER reading history - relevant at least for GMC-500
        #
        dprint(gglobs.debug, "makeHIST: Cleaning pipeline AFTER reading history")
        extra = gcommands.getExtraByte(gglobs.ser)

    else:
        # "Parsed File" - is already *.his; does not need makeHIST
        return (0, "")

    histlen  = len(hist)          # Total length; should always be 64k or 1MB, now: could be any length!
    histFF   = hist.count('\xFF') # total count of FF bytes

    fprint("Length as read:"                   , "{} Bytes".format(histlen))
    fprint("Count of FF bytes - Total:"        , "{} Bytes".format(histFF))

    histRC    = hist.rstrip(chr(0xff))     # after right-clip FF (removal of all trailing 0xff)
    histRClen = len(histRC)                # total byte count
    histRCFF  = histRC.count('\xFF')       # total count of FF in right-clipped data

    fprint("Count of FF bytes - Trailing:"     , "{} Bytes".format(histlen - histRClen))
    fprint("Count of data bytes:"              , "{} Bytes".format(histRClen))
    fprint("Count of FF bytes within data:"    , "{} Bytes".format(histRCFF))

    if sourceHIST == "Device":
        # writing data as binary
        fprint("Writing data as binary to:", binFilePath)
        f = open(binFilePath, "w", buffering=1)
        f.write(hist)
        f.close

    # prepare to write binary data to '*.lst' file (= lstFilePath) in human readable format
    lstlines  = "#Binary History Data - created {}\n".format(stime())   # write header
    lstlines += "#Format: byte_index hex=dec : value hex=dec | \n"
    histInt   = map(ord, histRC)                                        # convert string to list of int
    pagesize  = 1024                                                    # for the breaks in printing

    # This reads the full history independent of the memory setting of the currently
    # selected counter
    for i in range(0, histRClen, pagesize):
        for j in range(0, pagesize, 4):
            lstline =""
            for k in range(0, 4):
                if j + k >= pagesize:   break
                l  = i + j + k
                if l >= histRClen:         break
                lstline += "{:04x}={:<5d}:{:02x}={:<3d}|".format(l, l, histInt[l], histInt[l])
            lstlines += lstline[:-1] + "\n"
            if l >= histRClen:         break

        lstlines += "Reading Page {} of size {} bytes complete; next address: 0x{:04x}={:5d} {}\n".format(i/pagesize, pagesize, i+pagesize, i+pagesize, "-" * 6)
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

    # for testing only - highlicht the FF bytes
    #testwrite(hist, lstFilePath)

    # parse HIST data, preserve a copy with parsing comments
    fprint("Parsing binary file")
    histLogList, histLogListComment = parseHIST(hist, hisFilePath)

    # sort parsed data by date&time
    fprint("Sorting parsed file on time")
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

    # write result to '*.his' file
    fprint("Writing parsed & sorted data to:", hisFilePath)
    f = open(hisFilePath, "w")
    for i in histLogList:
        f.write(i + "\n")
    f.close

    return (0, "")


def parseHIST(hist, hisFilePath):
    """Parse history
    return data in logfile format
    """

    i               = 0     # counter for starting point byte number
    first           = 0     # byte index of first occurence of datetimetag
    cpms            = 0     # counter for CPMs read, so time can be adjusted
    cpmfactor       = 1     # for CPM data = 1, for CPS data = 60 (all is recorded as CPM!)

    # search for first occurence of a Date&Time tag
    # must include re.DOTALL, otherwise a \x0a as in time 10h20:30 will
    # be considered as newline characters and ignored!
    DateTimeTag      = re.compile(r"\x55\xaa\x00......\x55\xaa[\x00\x01\x02\x03]", re.DOTALL)
    DateTimeTagList  = DateTimeTag.finditer(hist)
    for dtt in DateTimeTagList:
        first = dtt.start()
        break

    i = first               # the new start point for the parse
    dprint(gglobs.debug, "parseHIST: byte index first Date&Time tag: {}".format(first))

    hist = hist + hist[:i]          # concat with the part missed due to overflow
    hist = hist.rstrip(chr(0xff))   # right-clip FF (removal of all trailing 0xff)
    rec  = map(ord, hist)           # convert string to list of int
    lh   = len(rec)

    histLogList         = []
    histLogListComment  = []

    rs                  = "#HEADER,{}, File created; Format: ByteIndex,Date&Time, CPM".format(stime())  # header
    histLogList.       append(rs)
    histLogListComment.append(rs)

    if gglobs.debug:
        f = open(hisFilePath + ".parse", "w", buffering=1)

    while i < lh -2:
        #print i,
        if gglobs.debug:
            f.write(histLogListComment[-1] + "\n")

        r = rec[i]
        if r == 0x55:
            if rec[i+1] == 0xaa:
                if rec[i+2] == 0:   # timestamp coming
                    YY = rec[i+3]
                    MM = rec[i+4]
                    DD = rec[i+5]
                    hh = rec[i+6]
                    mm = rec[i+7]
                    ss = rec[i+8]
                    # rec[i+ 9] = 0x55 end marker bytes; always fixed
                    # rec[i+10] = 0xAA (actually unnecessary since length is fixed too)
                    rectime = "20{:02d}-{:02d}-{:02d} {:02d}:{:02d}:{:02d}".format( YY,MM,DD,hh,mm,ss)
                    rectimestamp = datestr2num(rectime)

                    dd = rec[i+11]   # saving tag
                    if dd == 0:
                        savetxt = "history saving off"
                        saveinterval = 0
                    elif dd == 1:
                        savetxt = "CPS, save every second"
                        saveinterval = 1
                        cpmfactor    = 60
                    elif dd == 2:
                        savetxt = "CPM, save every minute"
                        saveinterval = 60
                        cpmfactor    = 1
                    elif dd == 3:
                        savetxt = "CPM, save every hour as hourly average"
                        saveinterval = 3600
                        cpmfactor    = 1
                    else:
                        savetxt = "ERROR: FALSE READING OF HISTORY SAVE-INTERVALL = {:3d} (allowed is: 0,1,2,3)".format(dd)
                        saveinterval = 0    # do NOT advance the time
                        cpmfactor    = -1   # make all counts negative to mark illegitimate data
                        dprint(True, savetxt)

                    rs = "#{:5d},{:19s}, Date&Time Stamp; Type:'{:}', Interval:{:} sec".format(i, rectime, savetxt, saveinterval)
                    histLogList.       append(rs)
                    histLogListComment.append(rs)

                    cpms = 0
                    i   += 11

                elif rec[i+2] == 1: #double data byte coming
                    cpms   += 1
                    msb     = rec[i+3]
                    lsb     = rec[i+4]
                    cpm     = msb * 256 + lsb
                    if cpmfactor == 60: #measurement is CPS, count rate limit applies!
                        cpm = cpm & 0x3fff
                    cpm     = cpm * cpmfactor

                    cpmtime = datetime.datetime.fromtimestamp(rectimestamp + cpms * saveinterval).strftime('%Y-%m-%d %H:%M:%S')
                    rs      = " {:5d},{:19s}, {:6d}".format(i,cpmtime, cpm)
                    histLogList.       append(rs)
                    histLogListComment.append(rs + ", ---double data bytes---" + savetxt)
                    i      += 4

                elif rec[i+2] == 2: #ascii bytes coming
                    cpmtime = datetime.datetime.fromtimestamp(rectimestamp + cpms * saveinterval).strftime('%Y-%m-%d %H:%M:%S')
                    count   = rec[i+3]
                    asc     = ""
                    for c in range(0,count):
                        asc += chr(rec[i + 4 + c])
                    rs      = "#{:5d},{:19s}, Note/Location: '{}' ({:d} Bytes) ".format(i, cpmtime, asc, count)
                    histLogList.       append(rs)
                    histLogListComment.append(rs)
                    i      += c + 4

            else: #0x55 is genuine cpm, no tag code
                cpms   += 1
                cpm     = r * cpmfactor
                cpmtime = datetime.datetime.fromtimestamp(rectimestamp + cpms * saveinterval).strftime('%Y-%m-%d %H:%M:%S')
                rs      = " {:5d},{:19s}, {:6d}".format(i,cpmtime, cpm)
                histLogList.       append(rs)
                histLogListComment.append(rs + ", ---0x55 is genuine, no tag code---" + savetxt)

        elif r == 0xff: # real count or 'empty' value?
            if gglobs.keepFF:
                cpms   += 1
                cpm     = r * cpmfactor
                cpmtime = datetime.datetime.fromtimestamp(rectimestamp + cpms * saveinterval).strftime('%Y-%m-%d %H:%M:%S')
                rs      = " {:5d},{:19s}, {:6d}".format(i,cpmtime, cpm)
                histLogList.       append(rs)
                histLogListComment.append(rs + ", ---real count or 'empty' value?---" + savetxt)

        else:
            cpms   += 1
            cpm     = r * cpmfactor
            cpmtime = datetime.datetime.fromtimestamp(rectimestamp + cpms * saveinterval).strftime('%Y-%m-%d %H:%M:%S')
            rs      = " {:5d},{:19s}, {:6d}".format(i,cpmtime, cpm)
            histLogList.       append(rs)
            histLogListComment.append(rs + ", ---single digit---" + savetxt)

        i += 1

    if gglobs.debug:
        f.close

    return histLogList, histLogListComment


def sortHistLog(histLogList):
    """The ringbuffer technology for the history buffer makes it possible that
    late data come first in the buffer. Sorting corrects this"""

    # Extract the Date&Time and put as new 1st col for sorting
    sortlines =[]
    for hline in histLogList:
        try:
            x, t, c = hline.split(",", 2) #byteindex. time, count
        except:
            dprint(True, "ERROR on split histLogList", hline)
            return histLogList
        sortlines.append([t, hline])

    # if a HEADER line exists, don't sort it
    # can only be the first line!
    if "#HEADER" in sortlines[0][1]:
        start = 1
    else:
        start = 0

    # sort all records by the newly created Date-Time column
    newsortlines = sorted(sortlines[start:], key = itemgetter(0))

    # add the HEADER line back as 1st line in sorted list
    if start == 1:
        newsortlines.insert(0,sortlines[0])

    # move back to list with only the log records as 3 csv columns
    # it works, but the function freaks me out :-(
    histLogListsorted = list(zip(*newsortlines)[1])

    return histLogListsorted


def testwrite(hist, lstFilePath):
    """highlight the FF bytes in bin file"""

    lstlines = ""
    lh       = len(hist)
    histInt  = map(ord, hist)    # convert string to list of int

    for i in range(0, 2**16, 512):
        lstline =""
        for j in range(0, 512):
            l  = i + j
            if l >= lh: break

            if histInt[l] == 255:
                s = "@"
            else:
                s = "."
            lstline += s
        lstlines += lstline + "\n"
    #print lstlines

    writeFileW(lstFilePath + ".test", lstlines, linefeed = False)
