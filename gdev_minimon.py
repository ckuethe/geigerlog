#! /usr/bin/env python3
# -*- coding: utf-8 -*-

"""
gdev_minimon.py - GeigerLog commands to handle the MiniMon device

MiniMon is a CO2 monitor available from multiple distributors, e.g. also from
TFA Drostman. On Amazon as https://www.amazon.de/gp/product/B00TH3OW4Q/
Or: https://www.co2meter.com/products/co2mini-co2-indoor-air-quality-monitor

The USB ID by lsusb is:     ID 04d9:a052 Holtek Semiconductor, Inc.

Datasheet:
http://co2meters.com/Documentation/AppNotes/AN146-RAD-0401-serial-communication.pdf

Software:
https://hackaday.io/project/5301-reverse-engineering-a-low-cost-usb-co-monitor
https://github.com/heinemml/CO2Meter/blob/master/CO2Meter.py

uderv rules:
see details also on line 300ff:
put into folder '/etc/udev/rules.d' a file named '90-co2mini.rules' with this content:

    # To activate use command:   sudo udevadm control --reload-rules
    # then unplug and replug MiniMon

    ACTION=="remove", GOTO="minimon_end"

    # Use this line if you have several MiniMons.
    # The name /dev/minimon will be attached with numbers depending on the hidraw dev it is linked to, like: /dev/minimon1, /dev/minimon2, etc
    #SUBSYSTEMS=="usb", KERNEL=="hidraw*", ATTRS{idVendor}=="04d9", ATTRS{idProduct}=="a052", GROUP="plugdev", MODE="0660", SYMLINK+="co2mini%n", GOTO="minimon_end"

    # Use this line if you have only a single MiniMon
    # The name /dev/minimon will never change
    SUBSYSTEMS=="usb", KERNEL=="hidraw*", ATTRS{idVendor}=="04d9", ATTRS{idProduct}=="a052", GROUP="plugdev", MODE="0660", SYMLINK+="minimon", GOTO="minimon_end"

    LABEL="minimon_end"

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


import fcntl
from   gsup_utils       import *


def initMiniMon():
    """Start the MiniMon"""

    global fp, key, values, MiniMonThread, MiniMonThreadStop, old_alldata, old_time

    fncname ="initMiniMon: "

    dprint(fncname + "Initialzing MiniMon")
    setDebugIndent(1)

    errmsg  = "" # what errors can be here?
    gglobs.MiniMonDeviceName     = "MiniMon"
    gglobs.MiniMonDeviceDetected = gglobs.MiniMonDeviceName # no difference so far
    gglobs.Devices["MiniMon"][0] = gglobs.MiniMonDeviceDetected

    if gglobs.MiniMonVariables  == "auto": gglobs.MiniMonVariables = "T, X"         # T=Temperatur, X=CO2, (H=Humidity)
    if gglobs.MiniMonDevice     == "auto": gglobs.MiniMonDevice    = "/dev/minimon" # requires udev rule
    if gglobs.MiniMonInterval   == "auto": gglobs.MiniMonInterval  = 60             # force saving after  60 seconds

    if not os.access(gglobs.MiniMonDevice , os.W_OK):
        msg = "Could not find MiniMon device - is it connected and powered?"
        edprint(msg)
        setDebugIndent(0)
        return msg

    try:
        fp = open(gglobs.MiniMonDevice, "a+b",  0)
    except Exception as e:
        msg = "Could not open MiniMon device - is it connected and powered?"
        exceptPrint(e, msg)
        setDebugIndent(0)
        return msg

    # key needed for decryption in readMiniMonData
    key                 = [0xc4, 0xc6, 0xc0, 0x92, 0x40, 0x23, 0xdc, 0x96]
    HIDIOCSFEATURE_9    = 0xC0094806
    set_report3         = b"\x00" + bytearray(key)

    fcntl.ioctl(fp, HIDIOCSFEATURE_9, set_report3)
    #fp.close() # Caution:  MUST NOT close the connection!!! Why???

    setLoggableVariables("MiniMon", gglobs.MiniMonVariables)

    # set to start defaults
    values      = {}
    old_alldata = {"T" : float('nan'), "H" : float('nan'), "X" : float('nan')}
    old_time    = 0

    MiniMonThreadStop = False

    MiniMonThread = threading.Thread(target = MiniMonThreadTarget)
    #MiniMonThread.daemon = True
    #edprint("MiniMonThread.daemon: ", MiniMonThread.daemon) # MiniMonThread.daemon: False
    MiniMonThread.start()

    setDebugIndent(0)

    gglobs.MiniMonConnection = True

    return errmsg


def MiniMonThreadTarget():
    """Thread that constantly triggers readings from the usb device."""

    global values, MiniMonThreadStop

    def printlostmsg():
        global values, MiniMonThreadStop
        # must NOT use fprint - because thread - but use print ok

        msg = "Lost connection to MiniMon device; stopping MiniMon. Continue after reconnection"
        dprint(msg, debug=True)
        MiniMonThreadStop = True
        values = {}
        values["error"] = msg

    fncname = "MiniMonThreadTarget: "

    while not MiniMonThreadStop:
        start = time.time()

        if os.access(gglobs.MiniMonDevice , os.R_OK):
            #dprint(fncname + "os:  {} is readable".format(gglobs.MiniMonDevice))
            try:
                fpr = fp.read(8)
                extractMiniMonData(fpr)

            except Exception as e:
                stre = str(e)
                exceptPrint("readMiniMonData: " + stre, "Failure in: data = list(fp.read(8))")
                if "[Errno 5]" in stre: # [Errno 5] = input/output error
                    printlostmsg()

        else:
            edprint(fncname + "os:  {} is NOT readable".format(gglobs.MiniMonDevice))
            printlostmsg()

        minsleep = 0.05
        maxsleep = 3
        tsleep   = gglobs.logcycle * 0.5 # sleep for half a logcycle
        tsleep   = max(tsleep, minsleep) # but at least 50 ms = 0.1 sec * 0.5
        tsleep   = min(tsleep, maxsleep) # sleep no longer than 3 sec
        time.sleep(tsleep)


def extractMiniMonData(fpr):
    """
    Function that reads one record from the device, decodes it, validates the
    checksum and, if valid, overwrites 'values' with the new data.
    """

    global values, MiniMonThreadStop

    fncname = "readMiniMonData: "

    data  = list(fpr)
    #print(fncname + "original  data: {}  hexlist: {}".format(decList(data), hexList(data)))

    if data[4] != 0x0d:
        # see: https://github.com/heinemml/CO2Meter/issues/4
        # newer devices don't encrypt the data, if byte 4 != 0x0d assume
        # encrypted data
        # could result in wrong data sometimes?!
        data = decrypt(key, data)

    # must be decrypted first
    checksum = sum(data[:3]) & 0xff
    #print(fncname + "decrypted data: {}  hexlist: {}  checksum: {}  {}".format(decList(data), hexList(data), hex(checksum), checksum == data[3]))

    # at this stage data[4]==13 or there is an error
    if data[4] != 0x0d:
        edprint(fncname + "Byte[4] error: {}".format(hexList(data)))

    # verify checksum
    elif checksum != data[3]:
        edprint(fncname + "Checksum error: {}   checksum: {}".format(hexList(data), hex(checksum)))

    # ok, good data
    else:
        op = data[0]
        if op in [0x50, 0x42, 0x41]:              # co2=0x50==80, temp=0x42==66, humid=0x41==65
            val         = data[1] << 8 | data[2]
            values[op]  = val
            #~print(fncname + f"op: {op:3d}, val: {val:5d}   values: {sortDict(values)}")

        #if op == 0x50: playWav()
        pass


def terminateMiniMon():
    """Stop the MiniMon"""

    global MiniMonThread, MiniMonThreadStop

    fncname ="terminateMiniMon: "
    dprint(fncname)
    if not gglobs.MiniMonConnection: return fncname + "No MiniMon connection"

    setDebugIndent(1)
    dprint(fncname + "stopping thread")
    MiniMonThreadStop = True
    MiniMonThread.join() # "This blocks the calling thread until the thread
                         #  whose join() method is called is terminated."

    # verify that thread has ended, but wait not longer
    # than 5 sec (takes 0.006...0.016 ms)
    start = time.time()
    while MiniMonThread.is_alive() and (time.time() - start) < 5:
        pass

    dprint(fncname + "thread-status: is alive: {}, waiting took: {:0.3f} ms".format(MiniMonThread.is_alive(), 1000 * (time.time() - start)))

    gglobs.MiniMonConnection = False
    #dprint(fncname + "is stopped")
    setDebugIndent(0)


def getMiniMonInfo(extended = False):
    """Info on the MiniMon"""

    if not gglobs.MiniMonConnection:   return "No connected device"

    MiniMonInfo = "Connected Device:             '{}'\n"\
                  "Configured Variables:         {}\n".\
                  format(gglobs.MiniMonDeviceName, gglobs.MiniMonVariables)

    if extended:
        MiniMonInfo += "No Extended Info\n"

    return MiniMonInfo


def printMiniMonInfo(extended=False):
    """prints basic info on the MiniMon device"""

    setBusyCursor()

    txt = "MiniMon Device"
    if extended:  txt += " Extended"
    fprint(header(txt))
    fprint("Configured Connection:", gglobs.MiniMonDevice)
    fprint(getMiniMonInfo(extended=extended))

    setNormalCursor()


def getMiniMonValues(varlist):
    """Read all data; return empty dict when not available"""

    global values, old_alldata, old_time

    fncname = "getMiniMonValues: "
    alldata = {"T" : float('nan'), "H" : float('nan'), "X" : float('nan')}

    new_time = time.time()

    if "error" in values:
        playWav("err")
        efprint(values["error"])
        values = {}

    else:
        for vname in varlist:
            if   vname in ("T"):
            # Temperature
                if 0x42 in values:
                    temp  = round(values[0x42] / 16.0 - 273.15, 2)   # 0x42 = 66
                    temp  = scaleVarValues(vname, temp, gglobs.ValueScale[vname])
                    alldata.update(  {vname: temp})

            elif vname in ("H"):
            # Humidity
                if 0x41 in values:
                    humid = round(values[0x41] / 100.0        , 2)   # 0x41 = 65 # !not 0x44! as in original code
                    humid = scaleVarValues(vname, humid, gglobs.ValueScale[vname])
                    alldata.update(  {vname: humid})

            elif vname in ("X"):
            # CO2
                if 0x50 in values:
                    co2   = values[0x50]                             # 0x50 = 80
                    co2   = scaleVarValues(vname, co2, gglobs.ValueScale[vname])
                    alldata.update(  {vname: co2})

    if (new_time - old_time) >= gglobs.MiniMonInterval:
        # forced saving; even if no values have changed
        old_time = new_time

    else:
        # do not save if all values are NAN or same as last reading
        if (np.isnan(alldata["T"]) or old_alldata["T"] == alldata["T"]) and \
           (np.isnan(alldata["H"]) or old_alldata["H"] == alldata["H"]) and \
           (np.isnan(alldata["X"]) or old_alldata["X"] == alldata["X"]):
                alldata = {}
        else:
                old_alldata = alldata
                old_time    = new_time

    printLoggedValues(fncname, varlist, alldata)

    return alldata


def decrypt(key,  data):
    cstate = [0x48,  0x74,  0x65,  0x6D,  0x70,  0x39,  0x39,  0x65]
    shuffle = [2, 4, 0, 7, 1, 6, 5, 3]

    phase1 = [0] * 8
    for i, o in enumerate(shuffle):
        phase1[o] = data[i]

    phase2 = [0] * 8
    for i in range(8):
        phase2[i] = phase1[i] ^ key[i]

    phase3 = [0] * 8
    for i in range(8):
        phase3[i] = ( (phase2[i] >> 3) | (phase2[ (i-1+8)%8 ] << 5) ) & 0xff

    ctmp = [0] * 8
    for i in range(8):
        ctmp[i] = ( (cstate[i] >> 4) | (cstate[i]<<4) ) & 0xff

    out = [0] * 8
    for i in range(8):
        out[i] = (0x100 + phase3[i] - ctmp[i]) & 0xff

    return out


def hexList(d):
    return " ".join("%02X" % e for e in d)


def decList(d):
    return " ".join("%3d" % e for e in d)




# *****************************************************************************
# ************  MiniMon  Version 1.0 ******************************************
# *****************************************************************************
#
# is a Python3 program to read data for CO2, Temperature, and Humidity (if
# available) from a "CO2 Monitor" distributed by various suppliers.
#
# The program was adapted to Python3 by ullix.
#
# The original version is by: Henryk Plötz, (2015):
# https://hackaday.io/project/5301-reverse-engineering-a-low-cost-usb-co-monitor/log/17909-all-your-base-are-belong-to-us
#
# MiniMon was verified to work on a device distributed by TFA Drostmann,
# obtained from Amazon:
# https://www.amazon.de/gp/product/B00TH3OW4Q/ref=ppx_yo_dt_b_asin_title_o02_s00?ie=UTF8&psc=1
#
# The device is used with the HIDRAW driver, which is the kernel interface for
# Raw Access to USB and Bluetooth Human Interface Devices.
#
# Find out to which driver-address your MiniMon-device has connected by issuing
# from the command line, before and after you connect the MiniMon-device to your
# computer:
#                        ls -al /dev/hidraw*
#
# The newly appearing one is the one to choose, e.g. /dev/hidraw1
#
# Start MiniMon program with:   ./minimon.py deviceaddr
#                          e.g. ./minimon.py /dev/hidraw1
#
#
# Depending on permissions settings on your computer, you may may have to start
# as sudo (root). To overcome this, put a udev rule on your computer by putting
# into folder '/etc/udev/rules.d' a file named '90-co2mini.rules' with this
# 3-line content:
#
#   ACTION=="remove", GOTO="co2mini_end"
#   SUBSYSTEMS=="usb", KERNEL=="hidraw*", ATTRS{idVendor}=="04d9", ATTRS{idProduct}=="a052", GROUP="plugdev", MODE="0660", SYMLINK+="co2mini%n", GOTO="co2mini_end"
#   LABEL="co2mini_end"
#
# Then restart your computer or issue the command:
#                       sudo udevadm control --reload-rules
#
# Then unplug and replug your MiniMon-device.
#
# This will a) allow the group plugdev (change as appropriate, or put your user
# into that group) access to the device node and b) symlink the hidraw devices
# of all connected CO₂ monitors.
#
# You will now always find your MiniMon-device at /dev/co2miniN, with N being
# a number 0, 1, 2, ...
#
# The data will be logged to a CSV (Comma Separated Values) file 'minmonlog.csv'
# in your current directory. If you want a different one, change this in the
# code (approx line 85ff).
#
# A timestamp is added to the data:
#           2020-06-01 16:08:27     CO2: 502 ppm,   T: 28.04 °C
#
#
# Example output in a normal office setting:
#    CO2: 501 ppm,  T: 26.29 °C
#    CO2: 501 ppm,  T: 26.29 °C
#    CO2: 501 ppm,  T: 26.29 °C
#    CO2: 502 ppm,  T: 26.29 °C
#    CO2: 502 ppm,  T: 26.29 °C
#    CO2: 502 ppm,  T: 26.29 °C
#
# after exhaling towards the backside of the MiniMon-device, you may find this
# output, while the display on the device itself only shows 'Hi' with the
# red LED on
#    CO2: 9723 ppm,  T: 26.85 °C
#    CO2: 9723 ppm,  T: 26.85 °C
#    CO2: 9723 ppm,  T: 26.85 °C
#    CO2: 9723 ppm,  T: 26.85 °C
#    CO2: 9723 ppm,  T: 26.85 °C
#    CO2: 7824 ppm,  T: 26.85 °C
#    CO2: 7824 ppm,  T: 26.85 °C
#    CO2: 7824 ppm,  T: 26.85 °C
#



def appendToFile(path, writestring):
    """Write-Append data; add linefeed"""

    with open(path, 'at', encoding="UTF-8", errors='replace', buffering = 1) as f:
        f.write((writestring + "\n"))


if __name__ == "__main__":
    """if the minimon is called directly without GeigerLog"""

    ##########################################
    # Define the full path to your log file
    logFile = "./minimonlog.csv"
    ##########################################

    # Key retrieved from /dev/random, guaranteed to be random ;)
    key = [0xc4, 0xc6, 0xc0, 0x92, 0x40, 0x23, 0xdc, 0x96]

    if len(sys.argv) < 2:
        print("ERROR: you must provide a hidraw device name. Start like:\n"\
              "\t./gdev_minimon.py /dev/minimon"
              "\nor\t./gdev_minimon.py /dev/hidraw1"
             )
        sys.exit()

    devname = sys.argv[1]
    fp = open(devname, "a+b",  0)

    HIDIOCSFEATURE_9 = 0xC0094806
    set_report3 = b"\x00" + bytearray(key)

    fcntl.ioctl(fp, HIDIOCSFEATURE_9, set_report3)

    values = {}
    co2 = temp = humid = float('nan')
    counter = 0
    appendToFile(logFile, "#DateTime,              CO2, Temperature")
    while True:
        counter += 1
        #print(counter, " -"*50)

        data    = list(fp.read(8))
        #print(f"raw data:  ", decList(data))

        if data[4] != 0x0d:
            # see: https://github.com/heinemml/CO2Meter/issues/4
            # some (newer?) devices don't encrypt the data, if byte 4 != 0x0d
            # assume encrypted data
            # ??? might result in wrong data sometimes?!!!
            decrypted = decrypt(key, data)
        else:
            decrypted = data

        if decrypted[4] != 0x0d or (sum(decrypted[:3]) & 0xff) != decrypted[3]:
            print (hexList(data), " => ", hexList(decrypted),  "Checksum error")

        else:
            op  = decrypted[0]
            val = decrypted[1] << 8 | decrypted[2]

            values[op] = val
            #print("values: ", values)

            # Output all data, mark just received value with asterisk
            #print( ", ".join( "%s%02X: %04X %5i" % ([" ", "*"][op==k], k, v, v) for (k, v) in sorted(values.items())), "  ",)

            if 0x50 in values:      co2   = values[0x50]                    # 0x50 = 80
            if 0x42 in values:      temp  = values[0x42] / 16.0 - 273.15    # 0x42 = 66
            if 0x41 in values:      humid = values[0x41] / 100.0            # 0x41 = 65 Note: old value 0x44 is wrong! (if no H sensor, then this will be 0

            logstring = "{:s}, {:5.0f}, {:6.2f}, {:6.2f}".format(stime(), co2, temp, humid)
            appendToFile(logFile, logstring)
            print(logstring)


"""
            key |value| chk  CR
decrypted:   66  18 175   3  13   0   0   0 #
decrypted:  109  12 189  54  13   0   0   0
decrypted:  110  53 251 158  13   0   0   0
decrypted:  113   2 170  29  13   0   0   0
decrypted:   80   2 171 253  13   0   0   0 #
decrypted:   87  31 145   7  13   0   0   0
decrypted:   86  44  74 204  13   0   0   0
decrypted:   65   0   0  65  13   0   0   0 #
decrypted:   67  14  50 131  13   0   0   0
decrypted:   66  18 175   3  13   0   0   0 #
decrypted:  109  12 189  54  13   0   0   0
decrypted:  110  53 251 158  13   0   0   0
decrypted:  113   2 170  29  13   0   0   0
decrypted:   80   2 171 253  13   0   0   0 #
decrypted:   79  33 137 249  13   0   0   0
decrypted:   82  44  71 197  13   0   0   0
decrypted:   65   0   0  65  13   0   0   0 #
decrypted:   67  14  51 132  13   0   0   0
decrypted:   66  18 175   3  13   0   0   0 #
decrypted:  109  12 189  54  13   0   0   0
decrypted:  110  53 251 158  13   0   0   0
decrypted:  113   2 170  29  13   0   0   0
decrypted:   80   2 171 253  13   0   0   0 #
decrypted:   87  31 143   5  13   0   0   0
decrypted:   86  44  76 206  13   0   0   0
decrypted:   65   0   0  65  13   0   0   0 #
decrypted:   67  14  50 131  13   0   0   0
decrypted:   66  18 175   3  13   0   0   0 #
decrypted:  109  12 189  54  13   0   0   0
decrypted:  110  53 251 158  13   0   0   0
decrypted:  113   2 170  29  13   0   0   0
decrypted:   80   2 171 253  13   0   0   0 #
decrypted:   79  33 129 241  13   0   0   0
decrypted:   82  44  64 190  13   0   0   0
decrypted:   65   0   0  65  13   0   0   0 #
decrypted:   67  14  53 134  13   0   0   0
decrypted:   66  18 175   3  13   0   0   0 #
decrypted:  109  12 189  54  13   0   0   0
decrypted:  110  53 251 158  13   0   0   0
decrypted:  113   2 170  29  13   0   0   0
decrypted:   80   2 171 253  13   0   0   0 #
decrypted:   87  31 144   6  13   0   0   0
decrypted:   86  44  76 206  13   0   0   0
decrypted:   65   0   0  65  13   0   0   0 #
decrypted:   67  14  53 134  13   0   0   0
decrypted:   66  18 175   3  13   0   0   0 #

raw data:   112 228 238  32 252  70 191  42
raw data:   170 228 254  32 106  70 191  98
raw data:   246 228 246  32  14  70 191  66
raw data:    88 228  78  33  94  70 191 242
raw data:    91 228  87  33  36  70 191  34
raw data:    63 228 110  33 137  70 191   2
raw data:   198 228 102  32 142  70 191   2
raw data:    62 228  95  32 128  70 191 234
raw data:    44 228 119  32  90  70 191  74
raw data:   112 228 238  32 252  70 191  42
raw data:   170 228 254  32 106  70 191  98
raw data:   246 228 246  32  14  70 191  66
raw data:    88 228  78  33  94  70 191 242
raw data:    91 228  87  33  36  70 191  34
raw data:    63 228 110  33 137  70 191   2
raw data:   198 228 102  32 142  70 191   2
raw data:   246 228  31  32 241  70 191 114
raw data:   253 228  23  32  91  70 191 218
raw data:   112 228 238  32 252  70 191  42
raw data:   170 228 254  32 106  70 191  98
raw data:   246 228 246  32  14  70 191  66
raw data:    88 228  78  33  94  70 191 242
raw data:    83 228  87  33  36  70 191  58
raw data:    63 228 110  33 137  70 191   2
raw data:   198 228 102  32 142  70 191   2
raw data:    22 228  95  32 128  70 191 194
raw data:    36 228 119  32  90  70 191  66

"""
