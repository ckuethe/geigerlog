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

    str_data_origin = b"Downloaded {} from device '{}'"
    #
    # get binary HIST data - either from file or from device
    #
    if sourceHIST == "Binary File":     # from file
        fprint("Reading data from binary file:", binFilePath)
        hist    = readBinaryFile(binFilePath)
        if "ERROR" in hist[:6]: # hist contains error message
            error = -1
            return (error, "ERROR: Cannot Make History: " + hist)

        if hist[0:11] == "DataOrigin:":
            data_origin = hist[11:128].rstrip(" ")
            vprint(gglobs.verbose, "'{}', len:{}".format(data_origin, len(data_origin)))
            hist = hist[128:]
        else:
            data_origin = str_data_origin.format("<Date Unknown>", "<Device Unknown>")
            vprint(gglobs.verbose,  "no Data Origin label found, " + data_origin)

        # only for testing: to cut a short piece of bin data
        #writeBinaryFile(binFilePath + ".short", hist[0:100])

    elif sourceHIST == "Device":         # from device

        gglobs.deviceDetected, error, errmessage = gcommands.getVER(ser)
        if error < 0: # getVER gave an error message
            return (error, "ERROR: Cannot Make History: " + errmessage)

        data_origin = str_data_origin.format(stime(), gglobs.deviceDetected)
        fprint("Reading from detected device:", "{}".format(gglobs.deviceDetected))

        hist = ""

        page    = gglobs.page # e.g. 4096, or 2048, see: defineDevice(index)
        FFpages = 0           # number of successive pages having only FF

        #
        # Cleaning pipeline BEFORE reading history - relevant at least for GMC-500
        # and perhaps relevant for the GMC-600
        #
        dprint(gglobs.debug, "makeHIST: Cleaning pipeline BEFORE reading history")
        extra = gcommands.getExtraByte(gglobs.ser)

        for address in range(0, gglobs.memory, page):       # prepare to read all memory
            time.sleep(0.1) # fails occasionally to read all data when
                            # sleep is only 0.1; still not ok at 0.2 sec
                            # wieder auf 0.1, da GQ Dataviewer deutlich scneller ist
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
        # Cleaning pipeline AFTER reading history - perhaps relevant for GMC-500
        # and perhaps the GMC-600
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

    # writing data from device as binary; add the device info to the beginning
    if sourceHIST == "Device":
        exthist = ("DataOrigin:" + data_origin + " " * 128 )[0:128] + hist
        vprint(gglobs.verbose, "hist: len():{}, exthist: len:{} exthist:{}".format(len(hist), len(exthist), exthist[:140]))
        writeBinaryFile(binFilePath, exthist)

# Preparing the *.lst file
    # prepare to write binary data to '*.lst' file (= lstFilePath) in human readable format
    lstlines  = u"#History Download - Binary Data in Human-Readable Form\n"  # write header
    lstlines += u"#{}\n".format(data_origin)
    lstlines += u"#Format: bytes:  index:value  as: 'hex=dec :hex=dec|'\n"
    histInt   = map(ord, histRC)                                        # convert string to list of int
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

        lstlines += u"Reading Page {} of size {} bytes complete; next address: 0x{:04x}={:5d} {}\n".format(i/ppagesize, ppagesize, i+ppagesize, i+ppagesize, "-" * 6)
        #print "(l +1)", (l+1), "(l +1) % 4096", (l+1) % 4096
        if (l + 1) % 4096 == 0 :
            lstlines += u"Reading Page {} of size {} Bytes complete {}\n".format(i/4096, 4096, "-" * 35)
        if l >= histRClen:         break

    if histRClen < histlen:
        lstlines += u"Remaining {} Bytes to the end of history (size:{}) are all ff\n".format(histlen -histRClen, histlen)
    else:
        lstlines += u"End of history reached\n"

    fprint("Writing data as list to:", lstFilePath)
    writeFileW(lstFilePath, lstlines, linefeed = False)
# end for *.lst file

    # for testing only - highlicht the FF bytes
    #testwrite(hist, lstFilePath)

# Prepare the *.his file
    # parse HIST data; preserve a copy with parsing comments if on debug
    fprint("Parsing binary file", "debug")
    histLogList, histLogListComment = parseHIST(hist, hisFilePath)

    hisClines  = u"#HEADER, File created from History Download Binary Data\n"  # header
    hisClines += u"#ORIGIN: {}\n".format(data_origin)
    hisClines += u"#FORMAT: '<#>ByteIndex,Date&Time, CPM' (Line beginning with '#' is comment)\n"

    if gglobs.debug:
        path = hisFilePath + ".parse"
        fprint("Writing commented parsed data to:", path, "debug")
        with io.open(path, 'wt', encoding="utf_8", errors='replace', buffering = 1) as f:
        #with io.open(path, 'wt', errors='replace', buffering = 1) as f:
            f.write(hisClines)
            for a in histLogListComment:
                # ensure ASCII chars
                asc     = ""
                ordasc  = ""
                ordflag = False
                for i in range(0, len(a)):
                    ai = ord(a[i])
                    if ai < 128 and ai > 31:
                        asc    += a[i]
                        ordasc += a[i]
                    else:
                        ordflag = True
                        asc    += "."
                        ordasc += "[{}]".format(ai)
                #print "a  :", a
                #print "asc:", asc
                #f.write(a + u"\n")
                f.write(asc + u"\n")
                if ordflag :
                    f.write(ordasc + u"\n")
                    print "ordasc:", ordasc

    # sort parsed data by date&time
    fprint("Sorting parsed data on time", "debug")
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

    fprint("Writing parsed & sorted data to:", hisFilePath, "debug")
    with io.open(hisFilePath, 'wt', encoding="utf_8", errors='replace', buffering = 1) as f:
        f.write(hisClines)
        for a in histLogList:
            # ensure ASCII chars
            asc     = ""
            ordasc  = ""
            ordflag = False
            for i in range(0, len(a)):
                ai = ord(a[i])
                if ai < 128 and ai > 31:
                    asc    += a[i]
                    ordasc += a[i]
                else:
                    ordflag = True
                    asc    += "."
                    ordasc += "[{}]".format(ai)
            #print "a  :", a
            #print "asc:", asc
            #f.write(a + u"\n")
            f.write(asc + u"\n")
            if ordflag :
                f.write(ordasc + u"\n")
                print "ordasc:", ordasc


# end for *.his file

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

    #while i < lh - 2:
    while i < lh - 3:  # if tag is ASCII bytes there will be a call of the 3rd byte

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
                    print "i:", i, "count:", count

                    if (i + 3 + count) <= lh:
                        asc     = ""
                        for c in range(0, count):
                            asc += chr(rec[i + 4 + c])
                        rs      = "#{:5d},{:19s}, Note/Location: '{}' ({:d} Bytes) ".format(i, cpmtime, asc, count)
                    else:
                        rs      = "#{:5d},{:19s}, Note/Location: '{}' (expected {:d} Bytes, got only {}) ".format(i, cpmtime, "ERROR: not enough data in History", count, lh - i - 3)
                    histLogList.       append(rs)
                    histLogListComment.append(rs)
                    i      += count + 3

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

    #print "sortlines: len():", len(sortlines)
    #for i in range(5): print sortlines[i]

    # sort all records by the newly created Date-Time column
    newsortlines = sorted(sortlines, key = itemgetter(0))
    #print "newsortlines: len():", len(newsortlines)
    #for i in range(5): print newsortlines[i]

    # move back to list with only the log records as 3 csv columns
    # it works, but the function freaks me out :-(
    histLogListsorted = list(zip(*newsortlines)[1])

    #print "histLogListsorted: len():", len(histLogListsorted)
    #for i in range(5): print histLogListsorted[i]

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
