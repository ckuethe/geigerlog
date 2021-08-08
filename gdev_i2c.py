#! /usr/bin/env python3
# -*- coding: utf-8 -*-

"""
gdev_i2c.py - I2C support; limited to dongle ELV with Sensors BME280 and TSL2591

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

from   gsup_utils       import *

import gdev_i2c_Dngl_ELV            as ELV      # I2C dongle
import gdev_i2c_Sensor_BME280       as BME280   # I2C sensor
import gdev_i2c_Sensor_TSL2591      as TSL2591  # I2C sensor

try:
    import serial                       # serial port (module has name: 'pyserial'!)
    import serial.tools.list_ports      # allows listing of serial ports
except Exception as e:
    msg  = "gdev_i2c: Module 'serial' could not be loaded\n"
    msg += "Verify that 'pyserial' is installed using gtools/GLpipcheck.py"
    exceptPrint(e, msg)
    edprint("Halting GeigerLog")
    playWav("err")
    sys.exit()


ELVdongle           = "ELVdongle"         # ELV USB-I2C Dongle

# I2C Sensors and Modules
bme280              = {
                       "name"   : "BME280",
                       "active" : False,                # TESTING
                       "feat"   : "Temperature, Pressure, Humidity",
                       "addr"   : 0x77,      # (d119)  addr: 0x76, 0x77
                       "type"   : 0x60,      # (d96)   BME280 has chip_ID 0x60
                       "hndl"   : None,      # handle
                       "dngl"   : None,      # connected with dongle
                      }

tsl2591             = {
                       "name"   : "TSL2591",
                       "active" : False,                # TESTING
                       "feat"   : "Light (Vis, IR)",
                       "addr"   : 0x29,      # (d41)  addr: 0x29
                       "type"   : 0x50,      # Device ID 0x50
                       "hndl"   : None,      # handle
                       "dngl"   : None,      # connected with dongle
                      }


def initI2C():
    """Init the ELV dongle with the BME280 sensor"""

    gglobs.I2CConnection     = False
    gglobs.I2CDeviceName     = "I2CSensors"
    gglobs.I2CDeviceDetected = gglobs.I2CDeviceName
    gglobs.Devices["I2C"][0] = gglobs.I2CDeviceDetected

    # init the ELV dongle
    gglobs.elv            = ELV.ELVdongle()
    success, msg          = gglobs.elv.ELVinit()
    if not success:
        msg2 = "Failure initializing dongle {}: {}".format(gglobs.elv.name, msg)
        edprint(msg2, debug=True)
        return msg2

    tmplts               = "Failure initializing sensor {} on dongle {} with message:<br>{}"

    # init sensor BME280 after linking with ELV dongle
    if bme280["active"]:
        bme280["dngl"] = ELVdongle
        bme280['hndl'] = BME280.SensorBME280(bme280)
        response       = bme280['hndl'].BME280Init()
        if response > "":
            return tmplts.format(bme280["name"], bme280["dngl"], response)

    # init sensor TSL2591 after linking with ELV dongle
    if tsl2591["active"]:
        tsl2591["dngl"] = ELVdongle
        tsl2591['hndl'] = TSL2591.SensorTSL2591(tsl2591)
        response               = tsl2591['hndl'].TSL2591Init()
        if response > "":
            return tmplts.format(bme280["name"], bme280["dngl"], response)

    gglobs.I2CConnection = True

    # setup the queues
    gglobs.QueueBME280  = queue.Queue()
    gglobs.QueueTSL2591 = queue.Queue()

    # setup the thread and start it
    gglobs.I2CThread = I2CReader(gglobs.QueueBME280, gglobs.QueueTSL2591)
    gglobs.I2CThread.start()

    # determine the variables (X is for vis light)
    if gglobs.I2CVariables == "auto": gglobs.I2CVariables    = "T, P, H, X"

    setLoggableVariables("I2C", gglobs.I2CVariables)

    # Save the info to avoid serial port call in conflict with thread!
    gglobs.I2CInfo         = getI2CInfo(extended=False, first=True)
    gglobs.I2CInfoExtended = getI2CInfo(extended=True,  first=True)

    return ""


def terminateI2C():
    """shutting down thread, closing ELV, resetting connection flag"""

    if gglobs.I2CThread != None:
        gglobs.I2CThread.stop() # fist stop threads, then close port!
        # wait for thread to end, but wait not longer than 5 sec
        start = time.time()
        while gglobs.I2CThread.is_alive() and (time.time() - start) < 5:
            time.sleep(0.1)
            pass            # wait for thread to end
        wprint("terminateI2C: thread-status: is alive: ", gglobs.I2CThread.is_alive())

    if gglobs.elv       != None: gglobs.elv.ELVclose()

    gglobs.I2CConnection = False

    return ""


def getI2CValues(varlist):
    """Read all I2C data"""

    fncname = "getI2CValues: "
    alldata = {}

    t, p, h, vis, ir = gglobs.NAN, gglobs.NAN, gglobs.NAN, gglobs.NAN, gglobs.NAN

    while not gglobs.QueueBME280.empty():
        latestReading = gglobs.QueueBME280.get()
        wprint (fncname + "Queue  B    latestReading:{}".format(latestReading))
        t, p, h = latestReading[1:]

    while not gglobs.QueueTSL2591.empty():
        latestReading = gglobs.QueueTSL2591.get()
        wprint (fncname + "Queue  T    latestReading:{}".format(latestReading))
        vis, ir, visraw, irraw, gainFct, inttime = latestReading[1:]

    #print("t:{}, p:{}, h:{}, vis:{}, ir:{}".format(t, p, h, vis, ir))

    for vname in varlist:
        if   vname in ("T"):
            vt                  = round(scaleVarValues(vname, t,   gglobs.ValueScale[vname]), 2)
            alldata.update(       {vname: vt})

        elif vname in ("P"):
            vp                  = round(scaleVarValues(vname, p,   gglobs.ValueScale[vname]), 2)
            alldata.update(       {vname: vp})

        elif vname in ("H"):
            vh                  = round(scaleVarValues(vname, h,   gglobs.ValueScale[vname]), 2)
            alldata.update(       {vname: vh})

        elif vname in ("X"):
            vvis                = round(scaleVarValues(vname, vis, gglobs.ValueScale[vname]), 2)
            alldata.update(       {vname: vvis})

        elif vname in ("CPS3rd"):
            vir                 = round(scaleVarValues(vname, ir , gglobs.ValueScale[vname]), 2)
            alldata.update(       {vname: vir})

    printLoggedValues(fncname, varlist, alldata)

    return alldata


def getI2CInfo(extended = False, first=False):
    """currently on ELV only"""

    if not gglobs.I2CConnection:   return "No connected device"

    if first:
        # on first call query the devices
        ELVinfo     = gglobs.elv.ELVgetInfo()
        try:
            BME280info  = bme280['hndl'].BME280getInfo()
        except:
            BME280info  = ("BME280 sensor not found", "")

        try:
            TSL2591info = tsl2591['hndl'].TSL2591getInfo()
        except:
            TSL2591info = ("TSL2591 sensor not found", "")

        gglobs.I2CDeviceDetected = ELVinfo[0]

        info  = "{:30s}{}\n"  .format("Connected Device:", "Dongle: {}".format(ELVinfo[0]))
        info += "{:30s}{}\n"  .format("Configured Variables:", gglobs.I2CVariables)
        if extended: info += "\n".join(ELVinfo[1:]) + "\n"

        info += "{:30s}{}\n".format("with Sensor:", BME280info[0])
        if extended: info += "\n".join(BME280info[1:])
        gglobs.I2CSensor1 = BME280info[0]

        info += "{:30s}{}".format("with Sensor:", TSL2591info[0])
        if extended: info += "\n".join(TSL2591info[1:])
        gglobs.I2CSensor2 = TSL2591info[0]

        vprint(info.replace("\n", "  "))
    else:
        # on 2nd and later calls do NOT query the devices, but take stored values
        # because conflict wuth serial calls
        if extended:    info = gglobs.I2CInfoExtended
        else:           info = gglobs.I2CInfo

    return info



def I2CautoBAUDRATE(usbport):
    """Tries to find a proper baudrate by testing for successful serial
    communication at up to all possible baudrates, beginning with the
    highest"""

    """
    NOTE: the device port can be opened without error at any baudrate, even
    when no communication can be done, e.g. due to wrong baudrate. Therfore we
    test for successful communication by checking for the return string
    containing 'ELV'.
    On success, this baudrate will be returned. A baudrate=0 will be returned
    when all communication fails. On a serial error, baudrate=None will be returned.
    """

    fncname = "I2CautoBAUDRATE: "

    dprint(fncname + "Autodiscovery of baudrate on port: '{}'".format(usbport))
    setDebugIndent(1)

    baudrates = gglobs.I2Cbaudrates
    baudrates.sort(reverse=True) # to start with highest baudrate
    for baudrate in baudrates:
        dprint(fncname + "Trying baudrate:", baudrate, debug=True)
        try:
            ABRser = serial.Serial(usbport, baudrate, timeout=0.5, write_timeout=0.5)
            ABRser.write(b'<y30?')
            rec = ABRser.read(140)
            #print("---------------------" + fncname + "rec: ", rec)

            while True:
                try:
                    cnt = ABRser.in_waiting
                except Exception as e:
                    exceptPrint(e, fncname + "ABRser.in_waiting Exception")
                    cnt = 0
                if cnt == 0: break
                ABRser.read(1)
                time.sleep(0.1)

            ABRser.close()
            if b"ELV" in rec:
                dprint(fncname + "Success with {}".format(baudrate), debug=True)
                break

        except Exception as e:
            errmessage1 = fncname + "ERROR: autoBAUDRATE: Serial communication error on finding baudrate"
            exceptPrint(e, errmessage1)
            baudrate = None
            break

        baudrate = 0

    dprint(fncname + "Found baudrate: {}".format(baudrate))
    setDebugIndent(0)

    return baudrate


class I2CReader(threading.Thread):
    """A simple threading class to read I2C values"""

    def __init__(self, QueueBME280, QueueTSL2591, readingDelay=1.0):
        try:
            self.readingDelay       = readingDelay  # How long to wait between reads (in sec)
            self.QueueBME280        = QueueBME280   # The queue into which BME280 readings will be placed
            self.QueueTSL2591       = QueueTSL2591  # The queue into which TSL2591 readings will be placed
            self.running            = False
            threading.Thread.__init__(self, group=None)
        except Exception as e:
            srcinfo = "I2CReader: init: "
            exceptPrint(e, srcinfo)


    def stop(self):
        """Stops this thread's activity. Note: this may not be immediate"""

        #print(ERRORCOLOR + "------------------------I2CReader: stop: invoked" + NORMALCOLOR)
        self.running = False


    def run(self):
        """invoked by starting thread"""

        print(TCYAN + "------------------------I2CReader: run: invoked" + NORMALCOLOR)
        self.running = True

        while self.running:
            #print("self.QueueBME280.qsize():", self.QueueBME280.qsize())
            try:
                if self.QueueBME280.qsize()  < 3: self.QueueBME280.put(bme280  ['hndl'].BME280getTPH())
            except Exception as e:
                srcinfo = "I2CReader: run: QueueBME280" + str(bme280)
                exceptPrint(e, srcinfo)
                self.QueueBME280.put( ("BME280", 22, 1033, 66))  # TESTING

            #print("self.QueueTSL2591.qsize():", self.QueueTSL2591.qsize())
            try:
                if self.QueueTSL2591.qsize() < 3: self.QueueTSL2591.put(tsl2591['hndl'].TSL2591getLumAuto())
            except Exception as e:
                srcinfo = "I2CReader: run: QueueTSL2591" + str(tsl2591)
                exceptPrint(e, srcinfo)
                self.QueueTSL2591.put(("TSL2591", 44, 55, 77, 88, 99, 111))  # TESTING

            time.sleep(self.readingDelay)



def printI2CDevInfo(extended=False):
    """prints basic info on the I2C device"""

    setBusyCursor()

    txt = "I2CSensors Device"
    if extended:  txt += " Extended"
    fprint(header(txt))
    fprint("Configured Connection:", "port:'{}' baud:{} timeoutR:{}s timeoutW:{}s".\
                     format(gglobs.I2Cusbport, gglobs.I2Cbaudrate, gglobs.I2Ctimeout, gglobs.I2Ctimeout_write))

    fprint(getI2CInfo(extended=extended))

    setNormalCursor()


def resetI2C():
    """Reset the ELV dongle and sensors"""

    setBusyCursor()
    fprint(header("Resetting I2C System"))

    fprint("Waiting ...")
    Qt_update()

    try:    gglobs.elv.ELVreset()                           # takes >=2 sec!
    except: edprint("I2C ELV Reset failed", debug=True)

    try:    bme280 ['hndl'].BME280Reset()
    except: edprint("I2C BME280 Reset failed", debug=True)

    try:    tsl2591['hndl'].TSL2591Reset()
    except: edprint("I2C TSL2591 Reset failed", debug=True)

    fprint("I2C Reset done")
    setNormalCursor()
