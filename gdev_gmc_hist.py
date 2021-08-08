#! /usr/bin/env python3
# -*- coding: UTF-8 -*-

"""
gdev_gmc_hist.py - GeigerLog commands to read and parse the history data from Geiger
counter device or from file and create database.
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
__credits__         = ["Phil Gillaspy"]
__license__         = "GPL3"

# credits:
# device command coding taken from:
# Phil Gillaspy, https://sourceforge.net/projects/gqgmc/
# and document 'GQ-RFC1201.txt'
# (GQ-RFC1201,GQ Geiger Counter Communication Protocol, Ver 1.40 Jan-2015)

from   gsup_utils       import *            # all utilities

import gsup_sql                             # database handling
import gdev_gmc                             # getGMC_SPIR, getExtrabyte are used here
#~from gdev_gmc import getGMC_SPIR                         # only getGMC_SPIR is used here



def makeGMC_History(sourceHist):
    """make the History by reading data either from file or from device,
    parse them, sort them by date&time, and write into files"""

    fncname = "makeGMC_History: "

    str_data_origin = u"Downloaded {} from device '{}'"

    #
    # get binary HIST data - either from file or from device
    #
    if   sourceHist == "Parsed File":
        return (0, "")

    elif sourceHist == "Database":
        return (0, "")

    elif sourceHist == "Binary File":
        hist    = readBinaryFile(gglobs.binFilePath)

        if b"ERROR" in hist[:6]: # hist contains error message
            error = -1
            return (error, "ERROR: Cannot Make History: " + hist)

        if hist[0:11] == b"DataOrigin:":
            data_origin = hist[11:128].rstrip(b' ').decode('UTF-8')
            data_originDB = (data_origin[11:30], data_origin[30+12:])
            vprint("DataOrigin: len:{}: {}".format(len(data_origin), data_origin))
            hist = hist[128:]

        else:
            data_origin = str_data_origin.format("<Date Unknown>", "<Device Unknown>")
            data_originDB = ("<Date Unknown>", "<Device Unknown>")
            vprint("No Data-Origin label found")
            fprint("No Data-Origin label found")

            # Test auf die Bin File Länge. Wenn mit GQ's DV eingelesen
            # dann sind 256 Bytes ((512 for > GMC500series) zuviel eingelesen!!
            lenhistold = len(hist)
            #print("len(hist):", lenhistold)
            if len(hist) > 2**20:   hist = hist[0: 2**20]
            else:                   hist = hist[0: 2**16]

            dprint("Removed {} bytes from end of orginal *.bin file of {} bytes".format(lenhistold - len(hist), lenhistold))
            fprint("Removed {} bytes from end of orginal *.bin file of {} bytes".format(lenhistold - len(hist), lenhistold))

    elif sourceHist == "Device":
        data_origin   = str_data_origin.format(stime(), gglobs.GMCDeviceDetected)
        data_originDB = (stime(), gglobs.GMCDeviceDetected)
        fprint("Reading data from connected device: {}".format(gglobs.GMCDeviceDetected))

        hist    = b""
        page    = gglobs.GMC_SPIRpage # 4096 or 2048, see: getGMC_DeviceProperties
        FFpages = 0               # number of successive pages having only FF

        # Cleaning pipeline BEFORE reading history
        dprint(fncname + "Cleaning pipeline BEFORE reading history")
        extra = gdev_gmc.getGMC_ExtraByte()

        start = time.time()
        #testing
        vprint("makeGMC_History: gglobs.GMC_memory, page: ", gglobs.GMC_memory, " ", page)
        ########
        for address in range(0, gglobs.GMC_memory, page): # prepare to read all memory
            time.sleep(0.1) # fails occasionally to read all data when
                            # sleep is only 0.1; still not ok at 0.2 sec
                            # wieder auf 0.1, da GQ Dataviewer deutlich scneller ist
            fprint("Reading page of size {} @address:".format(page), address)

#newnewnew
#REMEMBER: AFTER Factoryreset rewrite the saving mode (showed cpm, although it was CPS!)

            QApplication.processEvents()
            QApplication.processEvents()
            rec, error, errmessage = gdev_gmc.getGMC_SPIR(address, page)
            if error in (0, 1):
                hist += rec
                if error == 1: fprint("Reading error:", "Recovery succeeded")

                if rec.count(b'\xFF') == page:
                    #print "rec.count('\xFF'):", rec.count('\xFF')
                    FFpages += 1
                else:
                    FFpages  = 0

                if not gglobs.fullhist and FFpages * page >= 8192: # 8192 is 2 pages of 4096 byte each
                    txt = "Found {} successive {} B-pages (total {} B), as 'FF' only - ending reading".format(FFpages, page, FFpages * page)
                    dprint(txt)
                    fprint(txt)
                    break

            else: # error = -1
                # non-recovered error occured
                dprint(fncname + "ERROR: ", errmessage, "; exiting from makeGMC_History")
                return (error, "ERROR: Cannot Get History: " + errmessage)

        stop = time.time()
        dtime = (stop - start)
        timing = "Total time: {:0.1f} sec, Total Bytes: {:d} --> {:0.1f} kBytes/s".format(dtime, len(hist), len(hist) / dtime / 1000)
        dprint(timing)
        fprint(timing)

        # Cleaning pipeline AFTER reading history
        dprint(fncname + "Cleaning pipeline AFTER reading history")
        extra = gdev_gmc.getGMC_ExtraByte()
    ### end if   sourceHist== #################################################

    printHistDetails(hist)

    # parse HIST data
    gglobs.HistoryDataList      = []
    gglobs.HistoryParseList     = []
    gglobs.HistoryCommentList   = []

    fprint("Parsing binary data", debug=gglobs.debug)
    parseHIST(hist)

    dbhisClines    = [None] * 2
    #                  ctype    jday, jday modifier to use time unmodified
    dbhisClines[0] = ["HEADER", None, "0 hours", "File created from History Download Binary Data"]
    dbhisClines[1] = ["ORIGIN", None, "0 hours", "{}".format(data_origin)]

# write to database
    gsup_sql.DB_insertBin           (gglobs.hisConn, hist)
    gsup_sql.DB_insertDevice        (gglobs.hisConn, *data_originDB)
    gsup_sql.DB_insertComments      (gglobs.hisConn, dbhisClines)
    gsup_sql.DB_insertComments      (gglobs.hisConn, gglobs.HistoryCommentList)
    gsup_sql.DB_insertData          (gglobs.hisConn, gglobs.HistoryDataList)
    gsup_sql.DB_insertParse         (gglobs.hisConn, gglobs.HistoryParseList)

    fprint("Database is created", debug=gglobs.debug)

    return (0, "")


def printHistDetails(hist=False):
    """ """

    #print("printHistDetails: hist:", hist)
    if hist == False:
        if gglobs.hisConn == None:
            gglobs.exgg.showStatusMessage("No data available")
            return

        fprint(header("Show History Binary Data Details"))
        fprint("from: {}\n".format(gglobs.hisDBPath))

        hist    = gsup_sql.DB_readBinblob(gglobs.hisConn)
        if hist == None:
            efprint("No binary data found in this database")
            return

    histlen     = len(hist)                  # Total length; could be any length e.g. when read from file
    histFF      = hist.count(b'\xFF')        # total count of FF bytes

    histRC      = hist.rstrip(b'\xFF')       # after right-clip FF (removal of all trailing 0xff)
    histRClen   = len(histRC)                # total byte count
    histRCFF    = histRC.count(b'\xFF')      # total count of FF in right-clipped data

    fprint("Binary data total byte count:"     , "{} Bytes".format(histlen))
    fprint("Count of data bytes:"              , "{} Bytes".format(histRClen))
    fprint("Count of FF bytes - Total:"        , "{} Bytes".format(histFF))
    fprint("Count of FF bytes - Trailing:"     , "{} Bytes".format(histlen - histRClen))
    fprint("Count of FF bytes - Within data:"  , "{} Bytes".format(histRCFF))



def parseHIST(hist):
    """Parse history hist"""

    global histCPSCum, tubeSelected

    fncname = "parseHIST: "

    i               = 0     # counter for starting point byte number
    first           = 0     # byte index of first occurence of datetimetag
    cpms            = 0     # counter for CPMs read, so time can be adjusted
    cpxValid        = 1     # for CPM data = 1, for CPS data = 60 (all is recorded as CPM!)
    tubeSelected    = 0     # the tube(s) selected for measurements: 00 = both, 1 = tube1, and 2 is tube2.

    # search for first occurence of a Date&Time tag
    # must include re.DOTALL, otherwise a \x0a as in time 10h20:30 will
    # be considered as newline characters and ignored!
    DateTimeTag      = re.compile(b"\x55\xaa\x00......\x55\xaa[\x00\x01\x02\x03]", re.DOTALL)

    DateTimeTagList  = DateTimeTag.finditer(hist)
    for dtt in DateTimeTagList:
        first = dtt.start()
        break

    i = first                       # the new start point for the parse
    dprint(fncname + "byte index of first Date&Time tag: {}".format(first))

    hist = hist + hist[:i]          # concat with the part missed due to overflow

    hist = hist.rstrip(b'\xff')     # right-clip FF (removal of all trailing 0xff)
    rec  = list(hist)               # convert string to list of int
    lh   = len(rec)

    histCPSCum          = [0] * 60  # cumulative values of CPS; initial set = all zero

    CPSmode             = True      # history saving mode is CPS by default

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
                        #saveinterval = 1
                        #~saveinterval = 0.99 # to compensate for the clock running too slow
                                            #~# timetag is normally sooner than expected from
                                            #~# advancing by 1 sec increments. Gives problems
                                            #~# in sorting order
                        saveinterval = 1 # to compensate for the clock running too slow
                                            # timetag is normally sooner than expected from
                                            # advancing by 1 sec increments. Gives problems
                                            # in sorting order
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
                        dprint(savetext, debug=True)
                        saveinterval = 0        # do NOT advance the time
                        cpxValid     = -1       # make all counts negative to mark illegitimate data
                        CPSmode      = True     # just to define the mode
                        cpms         = 0

                    rs     = "#{:5d}, {:19s}, Date&Time Stamp; Type:'{:}', Interval:{:} sec".format(i, rectime, savetext, saveinterval)
                    dbtype = "Date&Time Stamp; Type:'{:}', Interval:{:} sec".format(savetext, saveinterval)
                    parseCommentAdder(i, rectime, dbtype)

                    i   += 12

                elif rec[i+2] == 1: #double data byte coming
                    # user https://sourceforge.net/u/ckuethe/profile/send_message at sourceforge
                    # observed a bug and suggested these changes. He never answered my questions
                    # on what actually happened, like were all subsequent readings wrong?
                    # was it a reading error or a firmware error?
                    #~try:
                        #~msb = rec[i+3]
                        #~lsb = rec[i+4]
                    #~except IndexError:
                        #~pass

                    msb     = rec[i+3]
                    lsb     = rec[i+4]
                    cpx     = msb * 256 + lsb
                    if CPSmode: cpx = cpx & 0x3fff # count rate limit CPS = 14bit!
                    cpx     = cpx * cpxValid

                    parsecomment = "---double data bytes---"
                    parseValueAdder(i, cpx, CPSmode, rectimestamp, cpms, saveinterval, parsecomment, savetext)

                    i      += 5
                    cpms   += 1

                elif rec[i+2] == 5: # tube selection: 55 AA 05 followed with tube ID, and 00 = both, 1 = tube1, and 2 is tube2
                    tubeSelected = rec[i+3]

                    rs     = "#{:5d}, {:19s}, Tube Selected is:{:}  [0=both, 1=tube1, 2=tube2]".format(i, rectime, tubeSelected)
                    dbtype = "Tube Selected is:{:}  [0=both, 1=tube1, 2=tube2]".format(tubeSelected)
                    parseCommentAdder(i, rectime, dbtype)

                    i      += 4
                    cpms   = 0

                    #print("rs:", rs)


                # the following is the consequence of the highly unprofessionall
                # mess created by GQ by redefining the definition of the meaning
                # of the coding:  in some firmware (likely 1.18 and 1.21 for
                # 500+ counters) different association.
                # Claimed to be changed "soon", yet leaves a permanent problem
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

                elif rec[i+2] >= 6: # should NEVER be found as it is not used (currently)!
                    cpxValid = -1
                    cpx      = rec[i+3] * cpxValid

                    parsecomment = "---invalid qualifier for 0x55 0xAA sequence: '0x{:02X}' ---".format(rec[i+2])
                    parseValueAdder(i, cpx, CPSmode, rectimestamp, cpms, saveinterval, parsecomment, savetext)

                    i      += 1
                    cpms   += 1

                else:
                    # workaround for the mess created by GQ
                    # gglobs.GMC_locationBug: default: "GMC-500+Re 1.18", "GMC-500+Re 1.21"
                    if gglobs.GMCDeviceDetected in gglobs.GMC_locationBug:
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
                            dbtype  = "Note/Location: '{}' ({:d} Bytes) ".format(asc, count)
                        else:
                            rs      = "#{:5d} ,{:19s}, Note/Location: '{}' (expected {:d} Bytes, got only {}) ".format(i, cpmtime, "ERROR: not enough data in History", count, lh - i - 3)
                            dbtype  = "Note/Location: '{}' (expected {:d} Bytes, got only {}) ".format("ERROR: not enough data in History", count, lh - i - 3)
                        parseCommentAdder(i, cpmtime, dbtype)

                        i      += count + 4

                    elif rec[i+2] == histMess["Triple"]: #triple data byte coming
                        msb     = rec[i+3]
                        isb     = rec[i+4]
                        lsb     = rec[i+5]
                        cpx     = (msb * 256 + isb) * 256 + lsb
                        cpx     = cpx * cpxValid

                        parsecomment = "---triple data bytes---"
                        parseValueAdder(i, cpx, CPSmode, rectimestamp, cpms, saveinterval, parsecomment, savetext)

                        i      += 6
                        cpms   += 1

                    elif rec[i+2] == histMess["Quad"]: #quadruple data byte coming
                        msb     = rec[i+3]
                        isb     = rec[i+4]
                        isb0    = rec[i+5]
                        lsb     = rec[i+6]
                        cpx     = ((msb * 256 + isb) * 256 + isb0) * 256 + lsb
                        cpx     = cpx * cpxValid

                        parsecomment = "---quadruple data bytes---"
                        parseValueAdder(i, cpx, CPSmode, rectimestamp, cpms, saveinterval, parsecomment, savetext)

                        i      += 7
                        cpms   += 1

            else: #0x55 is genuine cpm, no tag code
                cpx     = r * cpxValid

                parsecomment = "---0x55 is genuine, no tag code---"
                parseValueAdder(i, cpx, CPSmode, rectimestamp, cpms, saveinterval, parsecomment, savetext)

                i      += 1
                cpms   += 1

        elif r == 0xff: # real count or 'empty' value?
            if gglobs.keepFF:
                cpx     = r * cpxValid

                parsecomment = "---real count or 'empty' value?---"
                parseValueAdder(i, cpx, CPSmode, rectimestamp, cpms, saveinterval, parsecomment, savetext)
                cpms   += 1
            i += 1

        else:
            cpx     = r * cpxValid

            parsecomment = "---single digit---"
            parseValueAdder(i, cpx, CPSmode, rectimestamp, cpms, saveinterval, parsecomment, savetext)
            i      += 1
            cpms   += 1


def parseValueAdder(i, cpx, CPSmode, rectimestamp, cpms, saveinterval, parsecomment, savetext):
    """Add the parse results to the *.his list and commented *.his.parse list"""

    global histCPSCum, tubeSelected

    cpxValid = 1
    cpmtime  = datetime.datetime.fromtimestamp(rectimestamp + cpms * saveinterval).strftime('%Y-%m-%d %H:%M:%S')

    if CPSmode: # measurement is CPS
        histCPSCum.append(cpx)          # add new data as 61st element (= #60)
        histCPSCum  = histCPSCum[1:]    # ignore element #0, get only 1...60
        cpm         = sum(histCPSCum)

    else: # CPM mode
        histCPSCum  = [0] * 60

    # create the data for the database
    # Index, DateTime, CPM, CPS, CPM1st, CPS1st, CPM2nd, CPS2nd,  Temp, Press, Humid, RMCPM
    datalist     = [None] * (gglobs.datacolsDefault + 2) # 13 x None
    datalist[0]  = i
    datalist[1]  = cpmtime
    datalist[2]  = "0 hours"

    if   tubeSelected == 0: pointer = 3
    elif tubeSelected == 1: pointer = 5
    elif tubeSelected == 2: pointer = 7
    else:
        efprint("ERROR: detected tubeSelected={}, but only 0,1,2 is permitted".format(tubeSelected), debug=True)
        pointer  = 3
        cpxValid = -1

    if CPSmode: # CPS mode
        datalist[pointer]       = int(cpm) * cpxValid
        datalist[pointer + 1]   = cpx * cpxValid

    else:        # CPM mode
        datalist[pointer]       = cpx * cpxValid

    gglobs.HistoryDataList.append (datalist)
    gglobs.HistoryParseList.append([i, parsecomment + savetext])


def parseCommentAdder(i, rectime, dbtype):

    datalist     = [None] * 4  # 4 x None
    datalist[0]  = i            # byte index
    datalist[1]  = rectime      # Date&Time
    datalist[2]  = "0 hours"    # the modifier for julianday; here: no modification
    datalist[3]  = dbtype       # Date&Time Stamp Info
    #print("#{:5d}, {:19s}, {:}".format(i, rectime, dbtype))

    gglobs.HistoryCommentList.append(datalist)


def saveHistBinaryData():
    """get the binary data from the database and save to *.bin file"""

    if gglobs.hisConn == None:
        gglobs.exgg.showStatusMessage("No data available")
        return

    fprint(header("Save History Binary Data to File"))
    fprint("from: {}\n".format(gglobs.hisDBPath))

    hist    = gsup_sql.DB_readBinblob(gglobs.hisConn)
    if hist == None:
        efprint("No binary data found in this database")
        return

    newpath = gglobs.hisDBPath + ".bin"
    writeBinaryFile(newpath, hist)

    fprint("saved as file: " + newpath)

