#!/usr/bin/python3
# -*- coding: UTF-8 -*-

"""
ggscout.py - GeigerLog commands to handle the Gamma-Scout Geiger counter

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
__copyright__       = "Copyright 2016, 2017, 2018, 2019"
__credits__         = [""]
__license__         = "GPL3"

"""
Gamma-Scout_Communication_Interface_V1.7.txt
from: https://www.gamma-scout.com/wp-content/uploads/Gamma-Scout_Communication_Interface_V1.7.txt

The contents of the protocol memory consists of either 2 byte pulse entries or
special codes. It must be interpreted byte by byte. Special codes start with a
byte with its high-nibble being 0xF. If the high-nibble is not 0xF, this byte
will be the first byte of a 2 byte pulse entry.

This 2 byte pulse entry represents the number of pulses collected during the
last protocol interval (or the number of pulse during an out-of-band protocol
interval, see below). The highest 5 bits contain the exponent, the lower 11
bits the mantissa. E.g.:

0x3E27 = %0011111000100111 = 2^7 (exponent) * 1575 (mantissa) = 201600
"""


from   gutils       import *
import gsql                             # database handling



# intervals in sec as used in GammaScout
protokoll_interval  = {
  0x00 : 7 * 24 * 60 * 60,  #   User selected a protocol interval of 1 week
  0x01 : 3 * 24 * 60 * 60,  #   User selected a protocol interval of 3 days
  0x02 : 1 * 24 * 60 * 60,  #   User selected a protocol interval of 1 day
  0x03 :     12 * 60 * 60,  #   User selected a protocol interval of 12 hours
  0x04 :      2 * 60 * 60,  #   User selected a protocol interval of 2 hours
  0x05 :      1 * 60 * 60,  #   User selected a protocol interval of 1 hour
  0x06 :          30 * 60,  #   User selected a protocol interval of 30 minutes
  0x07 :          10 * 60,  #   User selected a protocol interval of 10 minutes
  0x08 :           5 * 60,  #   User selected a protocol interval of 5 minutes
  0x09 :           2 * 60,  #   User selected a protocol interval of 2 minutes
  0x0A :           1 * 60,  #   User selected a protocol interval of 1 minute
  0x0B :               30,  #   User selected a protocol interval of 30 seconds
  0x0C :               10,  #   User selected a protocol interval of 10 seconds
  }


def showDatData(*args):
    """Show Gamma-Scout type Dat Data from the database table bin"""

    if gglobs.hisConn == None:
        gglobs.exgg.showStatusMessage("No data available")
        return

    fprint(header("Show History Dat Data"))
    hist    = gsql.DB_readBinblob(gglobs.hisConn)
    #print("createLstFromDB: hist:", hist)
    if hist == None:
        fprint("No Dat data found in this database", error=True)
        return

    if isinstance(hist, str):
        gglobs.exgg.setBusyCursor()
        fprint(hist)
        gglobs.exgg.setNormalCursor()

    elif isinstance(hist, bytes):
        gglobs.exgg.setBusyCursor()
        fprint(hist.decode("UTF-8"))
        gglobs.exgg.setNormalCursor()

    else:
        fprint("Cannot read the Dat data; possibly not of Gamma-Scout origin")


def getValue(raw):
    """Gamma-Scout_Communication_Interface; raw is a 2 byte value. The highest
    5 bits contain the exponent, the lower 11 bits the mantissa. E.g.:
    0x3E27 = %00111 110 00100111 = 2^7 (exponent) * 1575 (mantissa) = 201600
    """

    #print("raw: {:6d}  0x{:04X} 0b{:016b} {} {}".format(raw, raw, raw, "{:016b}".format(raw)[0:5], "{:016b}".format(raw)[5:]), end= "  ")

    exponent = (raw) >> 11
    mantissa = (raw & 0b0000011111111111)
    #print("exponent: {:3d},  mantissa: {:5d}".format(exponent, mantissa ), end ="  ")

    counts = mantissa * (2 ** exponent)
    #print("counts: {:17,d}".format(counts), end="  ")

    return counts


def getDateByte(raw):
    """hex value to be interpreted as alphanumeric: 0x37 = decimal 37!"""

    rdate = 10 * (raw  >> 4) + (raw & 0x0f)
    return "{:02d}".format(rdate)


def num2datstr(timestamp):

    dt = datetime.datetime.fromtimestamp(timestamp)

    return str(dt)


def parseCommentAdder(i, rectime, dbtype):

    datalist     = [None] * 4   # 4 x None
    datalist[0]  = i            # byte index
    datalist[1]  = rectime      # Date&Time
    datalist[2]  = "0 hours"    # the modifier for julianday; here: no modification
    datalist[3]  = dbtype       # Date&Time Stamp Info
    #print("#{:5d}, {:19s}, {:}".format(i, rectime, dbtype))

    gglobs.HistoryCommentList.append(datalist)


def parseValueAdder(i, rectime, counts, parsecomment, cpm_calc, interval):
    """Add the parse results to the *.his list and commented *.his.parse list"""

    # create the data for the database; datalist covers:
    # Index, DateTime, <modifier>,  CPM, CPS, CPM1st, CPS1st, CPM2nd, CPS2nd,  CPM3rd, CPS3rd, Temp, Press, Humid, X
    # 0      1         2            3    4    5       6       7        8       9       10      11    12     13     14
    datalist     = [None] * (gglobs.datacolsDefault + 2)   # (13 + 2)=15 x None
    datalist[0]  = i                    # byte index
    datalist[1]  = rectime              # Date&Time
    datalist[2]  = "0 hours"            # the modifier for julianday; here: no modification
    datalist[5]  = counts               # the counts in whatever the interval had been
    datalist[7]  = round(cpm_calc, 1)   # the cpm CALCULATED from counts and interval
    datalist[14] = interval             # the interval of counting
    #print("parseValueAdder: datalist: ", datalist)

    gglobs.HistoryDataList.append (datalist)
    gglobs.HistoryParseList.append([i, parsecomment])


def getParsedHistory(hisbytes, maxbytes=0xFFFF):
    """Parse the history as bytes dump and create CSV *.his file"""

    vprint("Parsing History:")
    try:
        index       = hisbytes.index(0xF5) # =245 =start location of history
    except Exception as e:
        dprint("Error: Exception: {}: Start of history with byte value 0xF5 (=245) not found in binary data!".format(e))
        return

    parsecounter = 0
    interval     = 0
    countertime  = 0
    timestamp    = 0
    datestr      = ""
    while True:
        raw = hisbytes[index]       # raw is SINGLE byte!

    # Special code - Dose overflow
        if   raw == 0xFA:
            dbtype = "{:20s}: 0x{:02X} ({:3d}): Dose rate overflowed (> 1000 uSv/h) during the current protocol interval at least once.".format("Special Code", raw, raw)
            wprint(dbtype)
            rectime = num2datstr(countertime)
            parseCommentAdder(index, rectime, dbtype)
            index += 1

    # Out-of-band protocol interval
    # relevant only for firmware up to 6.016   (5.43 < fw <= 6.016,  and for fw <= 5.43)
    # https://www.gamma-scout.com/wp-content/uploads/Gamma-Scout_Communication_Interface_V1.7.txt
    #    elif raw == 0xFF:
    #        print("{:20s} @{:<5d}: 0x{:02X} ({:3d}): ".format("   Out-of-band protocol interval, see above. ", index, raw, raw))
    #        nextbyte1 = hisbytes[index + 1]
    #        nextbyte2 = hisbytes[index + 2]
    #        writeFileA(filepath_his, "#{:5d}, {:19s}, 0x{:02X} : OLD VERSION Out-of-band protocol interval, next two bytes: 0x{:02X}{:02X}".format(index, num2datstr(countertime), raw, nextbyte1, nextbyte2) )
    #        index += 1 + 2

    # Special code - Flag for more
        elif raw == 0xF5:
            dbtype = "{:20s}: 0x{:02X} ({:3d}): Generic special code. The following byte determines the meaning:".format("Special Code", raw, raw)
            wprint(dbtype)
            rectime = num2datstr(countertime)
            parseCommentAdder(index, rectime, dbtype)

            index += 1
            raw = hisbytes[index]       # raw is SINGLE byte!

        # interval
            if raw >= 0x00 and raw <= 0x0c:
                interval = protokoll_interval[raw]
                dbtype = "{:20s}: 0x{:02X} ({:3d}): ".format("   Protocol Interval", raw, raw) + "Protocol Interval: {:<5d} sec".format(interval)
                wprint(dbtype)
                rectime = num2datstr(countertime)
                parseCommentAdder(index, rectime, dbtype)

                index += 1

        # ignore debug
            elif raw >= 0xF0 and raw <= 0xFE:
                dbtype = "{:20s} must be ignored: 0x{:02X} ({:3d}): ".format("debug flags", raw, raw)
                wprint(dbtype)
                rectime = num2datstr(countertime)
                parseCommentAdder(index, rectime, dbtype)

                index += 1

        # out of band
            elif raw == 0xEE:
                dbtype = "{:20s}: 0x{:02X} ({:3d}): ".format("   Out-of-band protocol interval.", raw, raw)
                nextbyte1 = hisbytes[index + 1]  # nextbyte1 and 2 give number of 10 sec intervalls to be added to time
                nextbyte2 = hisbytes[index + 2]
                wprint(dbtype)
                rectime = num2datstr(countertime)
                parseCommentAdder(index, rectime, dbtype)

                addedtime = (nextbyte2 * 256 + nextbyte1) * 10 # multiples of 10 sec

                raw1 = hisbytes[index + 3]
                raw2 = hisbytes[index + 4]
                count = getValue(raw1 << 8 | raw2)
                dbtype = "{:20s}: 0x{:02X}{:02X} count:{}".format("   next: pulse entry bytes", raw1, raw2, count)
                wprint(dbtype)
                rectime = num2datstr(countertime)
                parseCommentAdder(index, rectime, dbtype)

                parsecounter += 1
                if addedtime > 0:
                    dbtype = "{:19s}, {:10d}, {:9,.1f}, {:8d} ".format(num2datstr(countertime), count, count/addedtime * 60, addedtime)
                    wprint(dbtype)
                    rectime = num2datstr(countertime)
                    parseValueAdder     (index, rectime, count, dbtype, count/addedtime * 60, addedtime)

                countertime += addedtime
                index += 1 + 4

        # timestamp
            elif raw == 0xEF:
                wprint("{:20s}: 0x{:02X} ({:3d}): 5 bytes following: mmhhDDMMYY.".format("   Timestamp", raw, raw))
                mm = getDateByte(hisbytes[index + 1])
                hh = getDateByte(hisbytes[index + 2])
                DD = getDateByte(hisbytes[index + 3])
                MM = getDateByte(hisbytes[index + 4])
                YY = getDateByte(hisbytes[index + 5])
                ss = "00" # added here, not defined in firmware
                tbytes = "hexbytes:"
                for i in range(1, 6):   tbytes += " {:02x}".format( hisbytes[index + i])
                tstamp = "20{}-{}-{} {}:{}:{}".format(YY, MM, DD, hh, mm, ss)
                countertime = datestr2num(tstamp)
                dbtype = "{:19s}, 0x{:02X} : Timestamp: {} ({})".format(num2datstr(countertime), raw, tstamp, tbytes)
                wprint(dbtype)
                rectime = num2datstr(countertime)
                parseCommentAdder(index, rectime, dbtype)

                index += 1 + 5

        # counts
        else:
            raw1  = hisbytes[index    ]
            raw2  = hisbytes[index + 1]
            count = getValue(raw1 << 8 | raw2)
            parsecounter += 1
            dbtype = "{:19s}, {:10d}, {:9,.1f}, {:8d}, # raw bytes: 0x{:02X}{:02X}".format(num2datstr(countertime), count, count/interval * 60, interval, raw1, raw2)
            if parsecounter < 100: wprint(dbtype)

            parsecomment = "# raw bytes: 0x{:02X}{:02X}".format(raw1, raw2)
            rectime = num2datstr(countertime)
            parseValueAdder     (index, rectime, count, parsecomment, count/interval * 60, interval)

            countertime += interval
            index += 1 + 1


        if index >= maxbytes:
            dbtype = "# maxbytes reached or exceeded: index:{}, maxbytes:{} (0x{:04X})".format(index, maxbytes, maxbytes)
            wprint(dbtype)
            rectime = num2datstr(countertime)
            parseCommentAdder(index, rectime, dbtype)
            break

        if index >= len(hisbytes) - 1:
            break


def GSreadFromFile(dat_path):
    """read an ASCII file as readlines and return as list of byte values"""

    fncname = "GSreadFromFile: "
    wprint(fncname)
    setDebugIndent(1)

    try:
        with open(dat_path) as f:
            filedata = f.readlines()     # reads data as list of STRINGS
                                         # last char in each line is LF (value: 0x10)
    except Exception as e:
        dprint(fncname + "Exception at f.readlines(): ", e)
        return []
    #print("GSreadFromFile: filedata: type:{}, lines:{}".format(type(filedata), len(filedata)))

    # write *.dat data to database
    gsql.DB_insertBin           (gglobs.hisConn, "".join(filedata))

    dumpdata = []
    for a in filedata:    # remove last char LF
        #dumpdata.append(a.replace('\n', ''))
        dumpdata.append(a[:-1])

    wprint(fncname + "dumpdata: type:{}, lines:{}".format(type(dumpdata), len(dumpdata)))
    wprint(fncname + "-"*20)
    for a in dumpdata[:15]: wprint(a)
    wprint(fncname + "-"*20)

    setDebugIndent(0)
    return dumpdata


def convertDumpToBinList(dumpdata):
    """take ascii coded hex values from readlines str data and convert to list of bytes"""

    # e,g,: dumpdata[12]: len=67: f5ef5923130819f507f5ee0300000af50c00020001000100050004000500030096
    # ends with '96' as LF or CR+LF has been removed!

    len_dumpdata = len(dumpdata)

    vprint("convertDumpToBinList(dumpdata) len: {}".format(len_dumpdata))
    if len_dumpdata == 0: return []

    index = 0
    # search for text "GAMMA-SCOUT Protokoll"
    for i in range(0, len_dumpdata):
        if dumpdata[i].startswith("GAMMA-SCOUT Protokoll"):
            index = i
            break

    # search for text "f5" beginning at "GAMMA-SCOUT Protokoll"
    for i in range(index, len_dumpdata):
        if dumpdata[i].startswith("f5"):
            index = i
            break

    # convert double-chr to byte and add to list
    listdumpdata = []
    for i in range(index, len_dumpdata):
        lendata = len(dumpdata[i])

        # limited printout
        if i < index + 10 or i > (len_dumpdata - 4):

            #wprint("i={:5d} dumpdata[i]: {}  lendata:{}".format(i, dumpdata[i], lendata))
            strwprint  = "i={:5d} dumpdata[i]: {}  lendata:{}".format(i, dumpdata[i], lendata)
            try:
                checksum = 0
                for j in range(0, lendata - 2):
                    checksum += int(dumpdata[i][j], 16)
                    #print("checksum: {}  {:3d}  0x{:02X}".format(dumpdata[i][j], checksum, checksum))

                #wprint("Checksum: 0x{:02X}".format(checksum))
                strwprint += "Checksum: 0x{:02X}".format(checksum)
                #wprint("delta: dec:{}".format(checksum- int(dumpdata[i][-2:], 16)))
                strwprint += "delta: dec:{}".format(checksum- int(dumpdata[i][-2:], 16))
            except Exception as e:
                edprint("Checksum calculation gave Exception: ", e)
            wprint(strwprint)

        # get byte data from ASCII list
        for j in range(0, lendata - 2, 2):
            #print("j={}".format(j), end=" ")
            try:
                lbyte = int(dumpdata[i][j : j + 2], 16)
            except Exception as e:
                edprint("convertDumpToBinList: Exception in 'lbyte = int(dumpdata[i][j : j + 2], 16)':", e, ", j=",j)
                lbyte = 0xFA # overflow single byte value
            listdumpdata.append(lbyte)

    wprint("listdumpdata : len: {} (0x{:04X}) ".format(len(listdumpdata), len(listdumpdata)))
    wprint("first 50     : ", listdumpdata[:50])
    wprint("last 50      : ", listdumpdata[-50:])

    return listdumpdata


def makeGSHistory(source, device):  # source == "GSDevice" oder "GSDatFile"
    """read the history from a Gamma-Scout device or dump-file"""

    fncname = "getGSHistory: "

    if not gglobs.GSActivation:
        dprint(fncname + "Gamma-Scout device not activated")
        return "Gamma-Scout device not activated"

    dprint(fncname + "getting Gamma-Scout history from: ", source)
    setDebugIndent(1)

    error           = 0         # default: no error
    message         = ""        # default: no message


# get data from Gamma-Scout device
    if source == "GSDevice":

        data_originDB   = (stime(), gglobs.GSDeviceName)

        # find the maxbytes value
        res, error, message = GSget_v2_response(device)
        if error < 0:
            edprint(fncname + "Failure getting v2 response")
            return error, message

        # when in PC mode: 'b' dumps protocol memory (up to fw 6.1x; but apparently in all other modes too!)
        ok = GSwriteToDevice(b'b', device)    # correct

        dumpdata = GSreadFromDevice(device, saveToBin=True)

        dbheader = "File created by dumping history from device"
        dborigin = "Download from device"
        dbdevice = "{}".format(data_originDB[1])


# get data from a GammaScout *.dat file
    elif source == "GSDatFile":

        data_originDB   = (stime(), gglobs.datFilePath)

        vprint("Get History as Database *.hisdb file from GS dump *.dat file: ", gglobs.datFilePath)

        dumpdata = GSreadFromFile(gglobs.datFilePath)
        for a in dumpdata[:15]: wprint(a)

        # get version and more
        version_result, fw_version, serial_no, maxbytes, strtime = GSextractDetails(dumpdata[0])
        #version_result, fw_version, serial_no, maxbytes, strtime = GSextractDetails(v2_result[1])
        gglobs.GSFirmware       = fw_version
        gglobs.GSMemory         = maxbytes
        gglobs.GSSerialNumber   = serial_no
        gglobs.GSDateTime       = strtime
        dbheader = "This file created from History Dump *.dat Data from file"
        dborigin = gglobs.datFilePath
        dbdevice = "<from file>"


# Programming error
    else:
        printProgError(fncname + "Programming Error - wrong source: ", source)


    wprint("CounterFirmware: {}".format(gglobs.GSFirmware))
    wprint("SerialNumber:    {}".format(gglobs.GSSerialNumber))
    wprint("maxbytes:        {} (0x{:04X})".format(gglobs.GSMemory, gglobs.GSMemory))
    wprint("DateTime:        {}".format(gglobs.GSDateTime))

    hisbytes = convertDumpToBinList(dumpdata)

    if len(hisbytes) == 0:
        error   = -1
        message = "No valid data found!"
        dprint(message)

    else:
    # parse HIST data
        gglobs.HistoryDataList      = []
        gglobs.HistoryParseList     = []
        gglobs.HistoryCommentList   = []

        getParsedHistory(hisbytes, maxbytes=gglobs.GSMemory)

    # add headers
        dbhisClines    = [None] * 3
        #                  ctype    jday, jday modifier to use time unmodified
        dbhisClines[0] = ["HEADER", None, "0 hours", dbheader]
        dbhisClines[1] = ["ORIGIN", None, "0 hours", dborigin]
        dbhisClines[2] = ["DEVICE", None, "0 hours", dbdevice]

    # write to database
        gsql.DB_insertDevice        (gglobs.hisConn, *data_originDB)
        gsql.DB_insertComments      (gglobs.hisConn, dbhisClines)
        gsql.DB_insertComments      (gglobs.hisConn, gglobs.HistoryCommentList)
        gsql.DB_insertData          (gglobs.hisConn, gglobs.HistoryDataList)
        gsql.DB_insertParse         (gglobs.hisConn, gglobs.HistoryParseList)

        fprint("Got memory dump of {} bytes; found {} records".format(gglobs.GSMemory, len(gglobs.HistoryDataList) ))
        fprint("Database is created", debug=gglobs.debug)

    setDebugIndent(0)
    return error, message


def saveHistDatData():
    """get the Gamma-Scout dump data from the database and save to *.dat file"""

    if gglobs.hisConn == None:
        gglobs.exgg.showStatusMessage("No data available")
        return

    fncname = "saveHistDatData: "
    fprint(header("Save History Dump Data to File"))
    fprint("from: {}\n".format(gglobs.hisDBPath))

    hist    = gsql.DB_readBinblob(gglobs.hisConn)
    if hist == None:
        fprint("No dump data found in this database", error=True)
        return
    vprint(fncname + "hist: type: ", type(hist))

    newpath = gglobs.hisDBPath + ".dat"
    if isinstance(hist, str):
        gglobs.exgg.setBusyCursor()
        #fprint(hist)
        writeBinaryFile(newpath, bytes(hist, 'utf-8'))
        gglobs.exgg.setNormalCursor()

    elif isinstance(hist, bytes):
        gglobs.exgg.setBusyCursor()
        #fprint(hist.decode("UTF-8"))
        writeBinaryFile(newpath, hist)
        gglobs.exgg.setNormalCursor()

    vprint(fncname + "saved as file: " + newpath)
    fprint("saved as file: " + newpath)


def GScleanPipeline(device):
    """Cleaning pipeline"""

    fncname = "GScleanPipeline: "
    wprint(fncname + "Cleaning pipeline of device: '{}'".format(device))
    setDebugIndent(1)

    if gglobs.GSser.in_waiting > 0: cleaned_data = GSreadFromDevice(device)
    else:                           cleaned_data = "No data found waiting for cleaning"
    wprint(fncname + "Cleaned data: ", cleaned_data)

    setDebugIndent(0)


def setGammaScoutToNormalMode(device):
    """calls the counter with 'X' to switch back from PC Mode to Normal Mode;
    returns: ['', 'PC-Mode beendet'] when given when in PC Mode
    returns: nothing                 when given when in Normal Mode
    valid up to fw 6.1x"""

    fncname = "setGammaScoutToNormalMode: "

    wprint(fncname + "of device: '{}'".format(device))
    setDebugIndent(1)

    ok          = GSwriteToDevice(b'X', device)
    X_result    = GSreadFromDevice(device)
    wprint(fncname + "X result: ", X_result)
    gglobs.GSinPCmode = False # not checked that X_result is valid, but what else can I do?

    setDebugIndent(0)

    if len(X_result) > 0:   return X_result[1], 0, ""
    else:                   return None,       -1, "No response on 'X' request"


def setGammaScoutToPCMode(device):
    """Set Gamma-Scout into PC Mode by sending P to device
    (same as pressing PC button at device)
    return: on success: True
            else      : False
    """

    fncname = "GSsetPCMode: "
    gglobs.GSinPCmode = False

    ok = GSwriteToDevice(b'P', device)
    if not ok: return False

    P_result = GSreadFromDevice(device) # expected: ['', 'PC-Mode gestartet']
    wprint(fncname + "P_result: ", P_result)

    if len(P_result) == 0:                      return False
    elif P_result[1] == 'PC-Mode gestartet':
        gglobs.GSinPCmode = True
        return True
    else:                                       return False


def GSget_v2_response(device):
    """writing 'v' to the counter, while in PC Mode, to return Details:
    like: ['', 'Version 6.10 d93683 4213 18.08.19 17:42:05']
    - fw version
    - SN
    - number of used bytes in the protocol memory
    - date and time
    Valid in PC mode up to fw 6.1x
    """

    wprint("GSget_v2_response of device: '{}'".format(device))
    setDebugIndent(1)

    if not gglobs.GSinPCmode:   None, -1, "Device is NOT in PC Mode"

    ok = GSwriteToDevice(b'v', device)
    if not ok: return None, -1, "Failure writing 'v2' request"

    v2_result = GSreadFromDevice(device)
    wprint("GSget_v2_response: v2_result: ", v2_result)

    version_result, fw_version, serial_no, maxbytes, strtime = GSextractDetails(v2_result[1])

    gglobs.GSFirmware       = fw_version
    gglobs.GSMemory         = maxbytes
    gglobs.GSSerialNumber   = serial_no
    gglobs.GSDateTime       = strtime

    return v2_result, 0, ""


def GSget_v1_response(device):
    """writes 'v' to the counter while in NormalMode,
    expected return: ['', 'Standard']
    """

    fncname = "GSget_v1_response: "
    wprint(fncname + "of device: '{}'".format(device))
    setDebugIndent(1)

    ok = GSwriteToDevice(b'v', device)
    if not ok:
        edprint(fncname + "Failure writing 'v' for v1 request to device ", device)
        return None, -1, "Could not write 'v' to the device"

    v1_result = GSreadFromDevice(device)
    wprint(fncname + "Data received: ", v1_result)

    setDebugIndent(0)

    if len(v1_result) > 0:  return v1_result[1], 0, ""
    else:
        edprint(fncname + "No response on 'v1' request")
        return None,        -1, "Device did not responsd to 'v' request"


def GSextractDetails(dataline):
    """to extract device data info from
    dataline = e.g. 'Version 6.10 d93683 4217 18.08.19 17:43:57' """

    fncname  = "GSextractDetails: "
    defaults = (dataline, "Failure", "Failure", 2**16 - 1, "Failure")

    wprint(fncname + "dataline: ", dataline)

    if len(dataline) == 0:
        wprint(fncname + "no data in dataline: ", dataline)
        return defaults
    else:
        version_result  = dataline.split(" ")  # e.g.: ['Version', '6.10', 'd93683', '4217', '18.08.19', '17:43:57']
        if len(version_result) < 6:
            wprint(fncname + "not enough details in data in dataline: ", dataline)
            return defaults
        else:
            fw_version      = version_result[1]                             # 6.10
            serial_no       = version_result[2]                             # d93683
            dtcombo         = version_result[4] + " " + version_result[5]   # 14.08.2019 18:37:00
            try:
                maxbytes        = int(version_result[3], 16)                    # 16919 (0x4217)
            except Exception as e:
                edprint(fncname +  "Exception maxbytes: ", e)
                maxbytes = 2**16 - 1

        # convert: 14.08.2019 18:37:00   -->   2019-08-14 18:37:00
        timestamp = time.mktime(datetime.datetime.strptime(dtcombo, "%d.%m.%y %H:%M:%S").timetuple())
        strtime   = datetime.datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')

        details = version_result, fw_version, serial_no, maxbytes, strtime
        wprint(fncname + "Details: ", details)
        return details


def GSreadFromDevice(device, saveToBin=False):
    """read data from the Gamma Scout device 'device';
    argument 'device' currently not used
    (GSDeviceName = 'Gamma-Scout' is set in init"""

    fncname = "GSreadFromDevice: "

    wprint(fncname)
    setDebugIndent(1)

    start = time.time()
    try:
        devicedata = gglobs.GSser.readlines()   # reads data as list of BYTES
                                                # devicedata:  [b'\r\n', b'ELV USB-I2C-Interface v1.8 (Cal:5E)\r\n', ...
                                                # last bytes in each line are CR + LF (value: 0x13 0x10)
    except Exception as e:
        edprint(fncname + "Exception at GSser.readlines(): ", e)
        return []
    wprint(fncname + "Reading from device: {:0.3f} sec".format(time.time() - start))

    if saveToBin:
        # write device data to database on memory dump
        gsql.DB_insertBin           (gglobs.hisConn, b"".join(devicedata))

    wprint(fncname + "devicedata: type:{}, lines:{}, total length:{}".format(type(devicedata), len(devicedata), len(b"".join(devicedata))))

    dumpdata = []
    for a in devicedata:    # remove last chars CR + LF, then decode
        dumpdata.append(a.replace(b'\r\n', b'').decode("UTF-8"))

    wprint(fncname + "dumpdata  : type:{}, lines:{}, total length:{}".format(type(dumpdata), len(dumpdata), len("".join(dumpdata))))
    wprint(fncname + "Begin" + "-"*20)
    for a in dumpdata[:15]: wprint(fncname + a)
    wprint(fncname + "End--" + "-"*20)
    setDebugIndent(0)

    return dumpdata


def GSwriteToDevice(wdata, device):
    """writing wdata to device; type(wdata)=bytes, type(device)=str
    returns True if ok, otherwise False"""

    fncname         = "GSwriteToDevice: "

    if gglobs.GSser is None:
        edprint(fncname + "Serial Port is closed; cannot write to it!")
        return False

    waiting_time    = 4                     # sec wait for data in serial port

    start           = time.time()
    try:
        bytesWritten    = gglobs.GSser.write(wdata) # this line writes the data to the port
    except Exception as e:
        edprint(fncname + "Exception writing to port: ", e)
        return False

    stop            = time.time()
    deltams         = (stop - start)

    if bytesWritten == len(wdata):
        ok = True
        wprint(fncname + "Writing data {} to device; result: OK, done in {:0.3f} sec".format(wdata, deltams))

        while time.time() < (stop + waiting_time):
            bw = gglobs.GSser.in_waiting
            if bw > 0:  break
            time.sleep(0.001)

        stop2 = time.time()
        wprint(fncname + "Found {} bytes waiting after: {:0.3f} sec".format(bw, (stop2 - stop)))

    else:
        ok = False
        wprint(fncname + "Writing to device FAILURE in {:0.3f} ms : {} bytes written, but write data {} has length {}".format(deltams, bytesWritten, wdata, len(wdata)))

    return ok


def getGammaScoutValues(varlist):
    """get the values for all vars - but for the non-live counters there aren't any"""

    alldata = {}

    if not gglobs.GSConnection:
        dprint("getGammaScoutValues: NO Gamma-Scout connection")
        return alldata

    return alldata # this device cannot log


def getGammaScoutInfo(extended = False):
    """Info on the Gamma-Scout Device"""

    if gglobs.GSActivation == False:
        dprint("getGammaScoutInfo: Gamma-Scout device not activated")
        return "Gamma-Scout device not activated"

    if not gglobs.GSConnection:
        dprint("getGammaScoutInfo: Gamma-Scout device not connected")
        return "Gamma-Scout device not connected"

    GSInfo = """Connected Device:             {}
Configured Variables:         {}
Geiger tube calib. factor:    {} µSv/h/CPM
Device status:                {}
""".format(\
                                       gglobs.GSDeviceName, \
                                       gglobs.GSVariables,\
                                       gglobs.calibration2nd,\
                                       "PC Mode" if gglobs.GSinPCmode else "Normal Mode",\
                                    )
    if extended == True:
        GSget_v2_response(gglobs.GSDeviceName)
        GSInfo += """
Firmware Version:             {}
Serial Number:                {}
Used Memory:                  {} (0x{:04X}), {:0.0f}% of total memory
DateTime:                     {}""".format(\
                                        gglobs.GSFirmware , \
                                        gglobs.GSSerialNumber , \
                                        gglobs.GSMemory , gglobs.GSMemory , gglobs.GSMemory/2**15 * 100, \
                                        gglobs.GSDateTime , \
                                    )
    return GSInfo


def terminateGammaScout(device):
    """opposit of init ;-)"""

    if not gglobs.GSActivation: return

    fncname = "terminateGammaScout: "
    dprint(fncname + "Terminating device:", device)

    if gglobs.GSser != None:
        if gglobs.GSinPCmode:   setGammaScoutToNormalMode(device)
        try:
            gglobs.GSser.close()
        except Exception as e:
            edprint(fncname + "Failed trying to terminate Gamma-Scout, Exception: ", e)
        gglobs.GSser  = None

    gglobs.GSConnection = False


def initGammaScout():
    """Initialize Gamma-Scout; switches device into PC Mode."""

    # Gamma-Scout info on firmware & serial port settings.
    # Set the baudrate in configuration file; other parameters are fixed
    # type #1: FW < 6.00:              2400,7,e,1
    # type #2: 6.00 <= FW < 6.90:      9600,7,e,1
    # type #3: FW >= 6.90:           460800,7,e,1

    fncname = "initGammaScout: "

    if not gglobs.GSActivation:
        dprint(fncname + "Gamma-Scout device not activated")
        return "Gamma-Scout device not activated"

    dprint(fncname + "Initialzing Gamma-Scout")
    setDebugIndent(1)

    gglobs.GSDeviceName = "Gamma-Scout"

    gglobs.GSser = None
    error        = 0
    errmessage   = ""
    errmessage1  = "Connection failed: "
    errmessage1  = ""

    port         = gglobs.GSusbport         # default in config = /dev/ttyUSB2/
    baudrate     = gglobs.GSbaudrate        # default in config = 9600
    timeoutRead  = gglobs.GStimeout         # default in config = 3 sec
    timeoutWrite = gglobs.GStimeout_write   # default in config = 3 sec

    stopbits     = 1                        # generic in pyserial

    bytesize     = 7                        # specific to Gamma-Scout
    parity       = serial.PARITY_EVEN       # specific to Gamma-Scout

    while True:
        # try to make the serial connection
        try:
            # testing is blocked!!!!!!!!!
            if 0 and gglobs.testing:
                # for Gamma Scout SIMULATOR  gglobs.GSser is like:
                # Serial<id=0x7f2014d371d0, open=True>
                # (port='/dev/pts/5', baudrate=9600, bytesize=8, parity='N',
                # stopbits=1, timeout=3.0, xonxoff=False, rtscts=F)
                # this is due to socal command:
                # socat -d -d  pty,b9600,cs8,raw,echo=0    pty,b9600,cs8,raw,echo=0
                # so far unknown how to set bytesize=7 and parity=E :-(
                gglobs.GSser = serial.Serial(port           = port,
                                             baudrate       = baudrate,
                                             bytesize       = 8, #bytesize,
                                             parity         = "N", #parity,
                                             stopbits       = stopbits,
                                             timeout        = timeoutRead,
                                             write_timeout  = timeoutWrite)
            else:
                # for Gamma Scout   gglobs.GSser is like:
                # Serial<id=0x7f2014d371d0, open=True>
                # (port='/dev/ttyUSB0',  baudrate=9600, bytesize=7, parity='E',
                # stopbits=1, timeout=3, xonxoff=False, rtscts=False, dsrdtr=False)
                gglobs.GSser = serial.Serial(port           = port,
                                             baudrate       = baudrate,
                                             bytesize       = bytesize,
                                             parity         = parity,
                                             stopbits       = stopbits,
                                             timeout        = timeoutRead,
                                             write_timeout  = timeoutWrite)
        except serial.SerialException as e:
            edprint(fncname + "serialException: {}".format(e))
            exceptPrint(e, sys.exc_info(), fncname + "Exception: ")
            terminateGammaScout(gglobs.GSDeviceName)
            errmessage1 += "ERROR: {}".format(e)
            break

        except Exception as e:
            edprint(fncname + "Exception: {}".format(e))
            exceptPrint(e, sys.exc_info(), fncname + "Exception: ")
            terminateGammaScout(gglobs.GSDeviceName)
            errmessage1 += "ERROR: {}".format(e)
            break

        # Connection is made. Now test for successful communication with a
        # Gamma Scout counter, because the device port can be opened without
        # error even when no communication can be done, e.g. due to wrong
        # baudrate or wrong device
        dprint(fncname + "Serial Port: ", gglobs.GSser)
        dprint(fncname + "Port opened ok, now verifying communication")

        # clear any bytes in pipeline
        GScleanPipeline(gglobs.GSDeviceName)

        setGammaScoutToNormalMode(gglobs.GSDeviceName)


        # v1 response: write 'v' to get the Normal Mode response, = 'Standard'
        try:
            ver, error, errmessage = GSget_v1_response(gglobs.GSDeviceName)
        except Exception as e:
            edprint(fncname + "Exception: ", e)
            errmessage1  = "ERROR: Port opened ok, but Communication failed. Is baudrate correct?"
            edprint(fncname + errmessage1)
            terminateGammaScout(gglobs.GSDeviceName)
            break

        if error < 0:
            errmessage1  = "ERROR: Communication problem: " + errmessage
            edprint(fncname + errmessage1, debug=True)
            terminateGammaScout(gglobs.GSDeviceName)
            break

        else:
            # Got something back like: 'Standard'
            if ver.startswith("Standard"):  deviceDetected = gglobs.GSDeviceName
            else:
                err  = "<br>INFO: No Gamma-Scout device detected. While a connected device was found, it <br>"
                err += "identified itself with this unknown signature: '{}'.".format(ver)
                errmessage1 += err
                dprint(fncname + err, debug=True)
                terminateGammaScout(gglobs.GSDeviceName)

        break # completed; continue

    if gglobs.GSser == None:
        gglobs.GSConnection = False
        #rmsg = "{}".format(errmessage1.replace('[Errno 2]', '<br>'))
        rmsg = "{}".format(errmessage1.replace('[Errno 2]', ''))

    else:
        gglobs.GSConnection = True
        dprint(fncname + "Communication ok with device: '{}'".format(deviceDetected))
        rmsg = ""

        # now try to set PC mode
        #gglobs.GSinPCmode = GSsetPCMode(gglobs.GSDeviceName)
        setGammaScoutToPCMode(gglobs.GSDeviceName)
        if gglobs.GSinPCmode:   dprint(fncname + "Device is in PC Mode")
        else:                   edprint(fncname + "FAILURE switching device in PC Mode")

        # CPM1st will have default calibration of 0.0065 µSv/h/CPM
        # Only CPM2nd will have calibration of 0.009 µSv/h/CPM as determined for Gamma-Scout!
        if gglobs.GSCalibration  == "auto":
            gglobs.GSCalibration  = 0.009   # 0.009 µSv/h/CPM as determined by ullix
            gglobs.calibration2nd = gglobs.GSCalibration

        #######################################################################
        # Activate this segment when Logging is possible with the Live counters!
        #DevVars = gglobs.GSVariables.split(",")
        #for i in range(0, len(DevVars)):  DevVars[i] = DevVars[i].strip()
        #gglobs.DevicesVars["Gamma-Scout"] = DevVars

        # work around for non-loggable couters:
        gglobs.GSVariables                  = None
        gglobs.DevicesVars["Gamma-Scout"]   = None
        wprint("initGammaScout: DevicesVars:", gglobs.DevicesVars)
        #######################################################################

    setDebugIndent(0)

    return rmsg
