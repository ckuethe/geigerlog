#! /usr/bin/env python3
# -*- coding: utf-8 -*-

"""
rdev_i2c.py - DataServer's I2C device handler

include in programs with:
    import rdev_i2c
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
__copyright__       = "Copyright 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024"
__credits__         = [""]
__license__         = "GPL3"

from   rutils   import *


def initI2C():
    """Initialize I2C"""

    defname = "initI2C: "
    dprint(defname)
    setIndent(1)

    try:
        # Installation:
        # smbus:    pip install smbus       Debian based:   python3-smbus  # dead project? no longer in development
        # smbus2:   pip install smbus2      Debian based:   python3-smbus2
        SelectedBus = "smbus2"
        # import smbus2 as smbus
        import SelectedBus as smbus
        g.versions["smbus"] = smbus.__version__ + " (smbus2)"    # valid only for smbus2 !

        g.I2ConRaspi      = True

    except ImportError as e:
        exceptPrint(e, "")
        edprint("The module '{}' could not be imported, but is required.".format(SelectedBus))
        edprint("Cannot continue; will exit.")
        # if SelectedBus == "smbus":  edprint("Install with: 'sudo apt install Python-smbus'.")   # smbus
        # else:                       edprint("Install with 'python -m pip install -U smbus2'.")  # smbus2
        edprint("Install with 'python -m pip install -U smbus2'.")  # smbus2
        sys.exit()

    except Exception as e:
        exceptPrint(e, "")
        edprint("Unexpected error when importing {}. Cannot continue; will exit".format(SelectedBus))
        sys.exit()


    # use I2C-Bus #1
    g.I2Chandle = smbus.SMBus(1)
    g.I2Cinit = True

    dprint("{:27s} : {}".format("SMBus version", g.versions["smbus"]))

    # do a bus scan
    scanI2C()

    # init sensors and do first reads
    if g.I2Cusage_LM75B:
        g.lm75b    = SensorLM75B      (g.I2Caddr_LM75B)
        g.lm75b.initLM75B()

    if g.I2Cusage_BME280:
        g.bme280   = SensorBME280     (g.I2Caddr_BME280)
        g.bme280.initBME280()

    if g.I2Cusage_BH1750:
        g.bh1750   = SensorBH1750     (g.I2Caddr_BH1750)
        g.bh1750.initBH1750()

    if g.I2Cusage_VEML6075:
        g.veml6075 = SensorVEML6075   (g.I2Caddr_VEML6075)
        g.veml6075.initVEML6075()

    if g.I2Cusage_LTR390:
        g.ltr390   = SensorLTR390     (g.I2Caddr_LTR390)
        g.ltr390.initLTR390()

    if g.I2Cusage_GDK101:
        g.gdk101   = SensorGDK101     (g.I2Caddr_GDK101)
        g.gdk101.initGDK101()

    if g.I2Cusage_SCD30:
        g.scd30   = SensorSCD30       (g.I2Caddr_SCD30)
        g.scd30.initSCD30()

    if g.I2Cusage_SCD41:
        g.scd41   = SensorSCD41       (g.I2Caddr_SCD41)
        g.scd41.initSCD41()

    setIndent(0)

    return "Ok"


def terminateI2C():
    """closes I2C"""

    defname = "terminateI2C: "

    try:                    g.I2Chandle.close()
    except Exception as e:  exceptPrint(e, "I2C connection is not available")

    return "Terminate I2C: Done"


def scanI2C():
    """scans the I2C bus for I2C devices"""

    start = time.time()
    defname = "scanI2C: "

    cdprint("Scanning I2C Bus:")
    setIndent(1)
    cdprint("       0  1  2  3  4  5  6  7  8  9  A  B  C  D  E  F")
    dcnt    = 0                             # count of devices found on the bus
    scanfmt = "0x{:02X}  "
    scan    = scanfmt.format(0) + "-- "
    for addr in range(1, 128):              # skip address=0
        if addr % 16  == 0:
            cdprint(scan)
            scan = scanfmt.format(addr)

        try:
            rtest = g.I2Chandle.read_byte(addr)
            rdprint(defname, "addr: ", hex(addr), "  rtest: ", rtest)

            scan += "{:02X} ".format(addr)
            dcnt += 1
        except Exception as e:
            exceptPrint(e, defname + "addr: " + hex(addr))
            scan += "-- "

    cdprint(scan) # print last line

    dur = 1000 * (time.time() - start)
    cdprint("Found a total of {} I2C device(s) in {:0.1f} ms".format(dcnt, dur))
    setIndent(0)


def getI2CBytes(device, addr, reg, rbytes):
    """Read rbytes from reg at addr"""

    # on Raspi takes 0.5 ms typical, (0.5 ... 1.2 ms)

    # start   = time.time()
    defname = "getI2CBytes: "
    # rdprint(defname, "geti2cbytes i2chandle:", g.I2Chandle)

    for trial in range(5):  # try up to 5 times
        try:
            raw = g.I2Chandle.read_i2c_block_data(addr, reg, rbytes)
            break                                                     # break on first success
        except Exception as e:
            exceptPrint(e, defname + "{}  FAILURE I2C read: addr:{}, reg:{}, rbytes:{}".format(device, hex(addr), hex(reg), rbytes))
            raw = b"Fail"
            edprint(defname + "Fail in trial #{}, trying again.".format(trial))

    # dur = 1000 * (time.time() - start)
    # rdprint(defname + "  raw:{} dur: {:0.3f} ms".format(raw, dur))

    return raw


def getDataI2C():
    """get the data for the I2C device"""

    # LM75B     has a single Temp value
    # BH1750    has a single Lux value
    # VEML6075  has 2 UV values plus 3 compensation values
    # LTR390    has 2 values, 1 VIS value + 1 UV value
    # GDK101    has 2 values: a OneMin (1min) value and a TenMin (10min avg)
    #           value, but only OneMin is used here
    # SCD30     has 3 values: CO2, Temp, Humid, but only CO2 is used here
    # SCD41     has 3 values: CO2, Temp, Humid, but only CO2 is used here


    start   = time.time()
    defname = "getDataI2C: "

    I2CDict = {}

    # get Temp
    if g.I2Cusage_LM75B:
        for vname, vavg in g.I2Cvars_LM75B.items():
            # rdprint(defname, "vname, vavg: ", vname, "  ", vavg, " g.I2CstoreLM75B: ", g.I2CstoreLM75B)
            if vavg == 1:
                # get the last value read from sensor
                value = g.I2CstoreLM75B[-1]
            else:
                # get avg of last vavg values
                vavg     = clamp(vavg, 2, 60)
                lenStore = len(g.I2CstoreLM75B)             # number of values in queue
                Navg     = min(lenStore, vavg)              # number of values to avg

                newStore = list(g.I2CstoreLM75B)
                value    = sum(newStore[-Navg:])
                if Navg > 0:    value = round(value / Navg, 3)
                else:           value = g.NAN

            I2CDict.update({vname : value})


    # get Temp, Press, Humid
    if g.I2Cusage_BME280:
        for i, vs in enumerate(g.I2Cvars_BME280.items()):
            vname, vavg = vs
            # cdprint(defname, "i:{}, vname:{}, vavg:{}".format(i, vname, vavg))
            if vavg == 1:
                # the last value read from sensor
                value = round(g.I2CstoreBME280[-1][i], 3)
            else:
                # get avg of last vavg values
                vavg     = clamp(vavg, 2, 60)               # desired avg length of 2 ... 60
                lenStore = len(g.I2CstoreBME280)            # number of values in queue
                Navg     = min(lenStore, vavg)              # number of values available for avg
                # rdprint(defname, "vavg:{}, lenStore:{}, Navg:{} ".format(vavg, lenStore, Navg))

                newStore = list(g.I2CstoreBME280)           # need list because deque does not support slices
                newStore = [a[i] for a in newStore[-Navg:]] # get the first, second, ... value of the list
                # rdprint(defname, "newStore: ", newStore)

                value    = sum(newStore)

                if Navg > 0: value = round(value / Navg, 3)
                else:        value = g.NAN

            I2CDict.update({vname : value})
        # rdprint(defname, I2CDict)


    # get Lux
    if g.I2Cusage_BH1750:
        for vname, vavg in g.I2Cvars_BH1750.items():
            if vavg == 1:
                # the last value read from sensor
                value = g.I2CstoreBH1750[-1]
            else:
                # get avg of last vavg values
                vavg     = clamp(vavg, 2, 60)
                lenStore = len(g.I2CstoreBH1750)         # number of values in queue
                Navg     = min(lenStore, vavg)        # number of values to avg

                newStore = list(g.I2CstoreBH1750)
                value    = sum(newStore[-Navg:])
                if Navg > 0:    value = round(value / Navg, 3)
                else:           value = g.NAN

            I2CDict.update({vname : value})


    # get UVAB
    if g.I2Cusage_VEML6075:
        for i, vs in enumerate(g.I2Cvars_VEML6075.items()):
            vname, vavg = vs
            # cdprint(defname, "i:{}, vname:{}, vavg:{}".format(i, vname, vavg))
            if vavg == 1:
                # the last value read from sensor
                value = round(g.I2CstoreVEML6075[-1][i], 3)
            else:
                # get avg of last vavg values
                vavg     = clamp(vavg, 2, 60)               # desired avg length of 2 ... 60
                lenStore = len(g.I2CstoreVEML6075)              # number of values in queue
                Navg     = min(lenStore, vavg)              # number of values available to avg
                # rdprint(defname, "vavg:{}, lenStore:{}, Navg:{} ".format(vavg, lenStore, Navg))

                newStore = list(g.I2CstoreVEML6075)             # need list because deque does not support slices
                newStore = [a[i] for a in newStore[-Navg:]] # get the first, second, ... value of the list
                # rdprint(defname, "newStore: ", newStore)

                value    = sum(newStore)

                if Navg > 0: value = round(value / Navg, 3)
                else:        value = g.NAN

            I2CDict.update({vname : value})
        # rdprint(defname, I2CDict)


    # get visible + UV
    if g.I2Cusage_LTR390:
        for i, vs in enumerate(g.I2Cvars_LTR390.items()):
            vname, vavg = vs
            # cdprint(defname, "i:{}, vname:{}, vavg:{}".format(i, vname, vavg))
            if vavg == 1:
                # the last value read from sensor
                value = g.I2CstoreLTR390[-1][i]
            else:
                # get avg of last vavg values
                vavg     = clamp(vavg, 2, 60)                 # desired avg length of 2 ... 60
                lenStore = len(g.I2CstoreLTR390)              # number of values in queue
                Navg     = min(lenStore, vavg)                # number of values available to avg
                # rdprint(defname, "vavg:{}, lenStore:{}, Navg:{} ".format(vavg, lenStore, Navg))

                newStore = list(g.I2CstoreLTR390)             # need list because deque does not support slices
                newStore = [a[i] for a in newStore[-Navg:]]   # get the first, second, ... value of the list
                # rdprint(defname, "newStore: ", newStore)

                value    = sum(newStore)

                if Navg > 0: value = round(value / Navg, 3)
                else:        value = g.NAN

            I2CDict.update({vname : value})
        # rdprint(defname, I2CDict)


    # get Solid State CPM
    if g.I2Cusage_GDK101:
        # there is no avg for this sensor
        for vname, vavg in g.I2Cvars_GDK101.items():
            # rdprint(defname, "vname, vavg: ", vname, "  ", vavg, " g.I2CstoreGDK101: ", g.I2CstoreGDK101)
            I2CDict.update({vname : g.I2CstoreGDK101[0]})               # CPM (1 min) (taken from the only value in store)
            # getValGDK101("TenMin")                                    # CPM avg over 10 min

            # MT = getGDK101MeasTime()                                  # wofür ist das gut???
            # rdprint("Meas.Time: ",    "{:6.3f}".format(MT))           # print the Measurement Time


    # get CO2
    if g.I2Cusage_SCD30:
        # there is no avg for this sensor
        try:
            for vname, vavg in g.I2Cvars_SCD30.items():
                rdprint(defname, "vname:'{}', vavg:'{}' g.I2CstoreSCD30:'{}' ".format(vname, vavg, g.I2CstoreSCD30))
                I2CDict.update({vname : g.I2CstoreSCD30[0]})               # taken from the only value in store
        except Exception as e:
            exceptPrint(e, defname + "SCD30")


    # get CO2
    if g.I2Cusage_SCD41:
        # there is no avg for this sensor
        try:
            for vname, vavg in g.I2Cvars_SCD41.items():
                rdprint(defname, "vname:'{}', vavg:'{}' g.I2CstoreSCD41:'{}' ".format(vname, vavg, g.I2CstoreSCD41))
                I2CDict.update({vname : g.I2CstoreSCD41[0]})                # taken from the only value in store
        except Exception as e:
            exceptPrint(e, defname + "SCD41")


    duration = 1000 * (time.time() - start)
    dprint(defname + "  {} dur: {:0.3f} ms".format(I2CDict, duration))

    return I2CDict

#
# I2C for BME280 ################################################################
#
class SensorBME280:
    """Code for the BME280 sensors"""

    name    = "BME280"
    addr    = 0x76      # addr options: 0x76, 0x77. NOTE: Bluedot breakout board has only 0x77; 0x76 is NOT available!
    id      = 0x60


    def __init__(self, addr):
        """Init SensorBME280 class"""
        self.addr    = addr


    def initBME280(self):
        """Reset, check ID, set reg hum, get calibration, trigger measurement"""

        defname = "initBME280: "
        dprint(defname)

        g.I2Csensors.append(self.name)

        setIndent(1)

        # check ID
        tmsg      = "checkID"
        register  = 0xD0
        readbytes = 1
        data      = []
        answ      = getI2CBytes(tmsg, self.addr, register, readbytes)
        if len(answ) == readbytes and answ[0] == self.id:
            gdprint("Sensor {} at address 0x{:02X} has proper ID: 0x{:02X}".format(self.name, self.addr, self.id))
        else:
            setIndent(0)
            return (False, "Failure - Did find sensor, but ID: '{}' is not as expected: 0x{:02X}".format(answ, self.id))

        # soft reset
        # does NOT give a return!
        tmsg      = "Soft Reset"
        register  = 0xE0
        readbytes = 0
        data      = [0xB6]
        answ0     = g.I2Chandle.write_i2c_block_data(self.addr, register, data)

        # set ctrl-hum
        # b101 = 0x05 = oversampling * 16
        tmsg      = "Ctrl_hum"
        register  = 0xf2
        readbytes = 1
        data      = [0x05]
        answ0     = g.I2Chandle.write_i2c_block_data(self.addr, register, data)
        answ      = getI2CBytes(tmsg, self.addr, register, readbytes)

        # Calibration Data calib00...calib25 (0x88 ... 0x9F) 24 values
        tmsg      = "calib1 24"
        register  = 0x88
        readbytes = 24
        data      = []
        self.cal1 = getI2CBytes(tmsg, self.addr, register, readbytes)

        # Calibration Data calib26...calib41 (0xA1 ) 1 value
        tmsg      = "calib2 1"
        register  = 0xA1
        readbytes = 1
        data      = []
        self.cal2 = getI2CBytes(tmsg, self.addr, register, readbytes)

        # Calibration Data calib26...calib41 (0xe1 ... 0xe7) 7 values
        tmsg      = "calib3 7"
        register  = 0xe1
        readbytes = 7
        data      = []
        self.cal3 = getI2CBytes(tmsg, self.addr, register, readbytes)

        self.triggerMeasurementBME280()             # one-time call

        # cdprint("calib 1", self.cal1)
        # cdprint("calib 2", self.cal2)
        # cdprint("calib 3", self.cal3)

        self.getValBME280()                             # dump first value
        g.I2CstoreBME280.append(self.getValBME280())    # fill first value

        setIndent(0)


    def triggerMeasurementBME280(self):

        # trigger measurement
        try:
            fail      = False
            tmsg      = "ctrl_meas"
            register  = 0xf4
            readbytes = 1
            data      = [0xd6]
            answ0      = g.I2Chandle.write_i2c_block_data(self.addr, register, data)

            time.sleep(0.1) # needs delay of >= 100 ms (Nur estes Mal, oder immer?)

        except Exception as e:
            fail = True
            exceptPrint(e, "ctrl_meas")


    def getValBME280(self):
        """ get one measurement of Temp, Press, Humid"""
        # on dongle ISS:  T:25.050, P:996.343, H:33.799 duration:  avg: 3.3  (2.7 ...  4.1) ms
        # on Raspi: !faster than ISS!                   duration:  avg: 2.1  (1.9 ...  3.8) ms

        ## local def ##########################
        def BME280getRawData(rec):
            """calcs raw press, temp, hum"""

            msb, lsb, xlsb  = rec[0], rec[1], rec[2]
            press           = (msb << 16 | lsb << 8 | xlsb) >> 4

            msb, lsb, xlsb  = rec[3], rec[4], rec[5]
            temp            = (msb << 16 | lsb << 8 | xlsb) >> 4

            msb, lsb        = rec[6], rec[7]
            humid           = (msb <<  8 | lsb )

            return temp, press, humid
        ## end local def ########################

        start    = time.time()
        defname  = "getValBME280: "
        fail     = False
        response = (g.NAN,) * 3

        # trigger measurement
        try:
            tmsg      = "ctrl_meas"
            register  = 0xf4
            readbytes = 1
            data      = [0xd6]
            answ0     = g.I2Chandle.write_i2c_block_data(self.addr, register, data)
            answ      = getI2CBytes(tmsg, self.addr, register, readbytes)
            # rdprint(defname, "write: tmsg: ", tmsg, ", answ0: ", answ0 , ", answ: ", answ )
        except Exception as e:
            exceptPrint(e, "ctrl_meas")
            fail = True

        if fail or len(answ) != readbytes:
            rdprint(defname + tmsg + " failed, giving up")
            setIndent(0)
            return response

        # get raw data
        try:
            tmsg      = "getRawData"
            register  = 0xf7
            readbytes = 8
            data      = []
            answ      = getI2CBytes(tmsg, self.addr, register, readbytes)
            # rdprint(defname, "answ: ", answ )
        except Exception as e:
            exceptPrint(e, "get data F7..FE")
            fail = True

        # CAUTION: answ == [128, 0, 0, 128, 0, 0, 128, 0] does happen in first 1 or even first 2 calls
        if fail or len(answ) != readbytes or answ == [128, 0, 0, 128, 0, 0, 128, 0]:
            rdprint(defname + tmsg + " failed, giving up")
            setIndent(0)
            return response

        # convert raw data
        try:
            t_raw, p_raw, h_raw = BME280getRawData(answ)
            response = readBME280All(self.cal1, self.cal2, self.cal3, p_raw, t_raw, h_raw) # response = t, p, h
        except Exception as e:
            exceptPrint(e, "convert raw data")

        dur = 1000 * (time.time() - start)
        vprint("- {:17s}Temp:{:<6.3f}, Press:{:<6.3f}, Humid:{:<6.3f}  dur:{:0.2f} ms".format(defname, *response, dur))

        return response


    def resetBME280(self):
        """Soft Reset the BME280 sensor + Ctrl-hum=5 + Ctrl-Meas"""
        # on Raspi: duration: ca. 3 ms + 100 ms wait

        start = time.time()

        defname = "resetBME280: "
        dprint(defname)
        setIndent(1)

        # 5.4.2 Register 0xE0 “reset”
        # If the value 0xB6 is written to the register, the device is reset using the complete
        # power-on-reset procedure. Writing other values than 0xB6 has no effect. The readout
        # value is always 0x00.
        tmsg      = "Reset"
        register  = 0xe0
        readbytes = 1
        data      = [0xb6]
        answ0     = g.I2Chandle.write_i2c_block_data(self.addr, register, data)
        answ      = getI2CBytes(tmsg, self.addr, register, readbytes)

        # 5.4.3 Register 0xF2 “ctrl_hum”
        # The “ctrl_hum” register sets the humidity data acquisition options of the device. Changes
        # to this register only become effective after a write operation to “ctrl_meas”.
        # Bit 2, 1, 0  Controls oversampling of humidity data.
        # 101 (=0x05) : Humidity oversampling ×16
        tmsg      = "ctr_hum"
        register  = 0xf2
        readbytes = 1
        data      = [0x05]
        answ0     = g.I2Chandle.write_i2c_block_data(self.addr, register, data)
        answ      = getI2CBytes(tmsg, self.addr, register, readbytes)

        # trigger measurement
        try:
            tmsg      = "ctrl_meas"
            register  = 0xf4
            readbytes = 1
            data      = [0xd6]
            answ0     = g.I2Chandle.write_i2c_block_data(self.addr, register, data)
            answ      = getI2CBytes(tmsg, self.addr, register, readbytes)
            # rdprint(defname, "write: tmsg: ", tmsg, ", answ0: ", answ0 , ", answ: ", answ )
            time.sleep(0.1)
        except Exception as e:
            exceptPrint(e, "ctrl_meas")
            # fail = True

        duration  = 1000 * (time.time() - start)
        msg       = "Reset + Ctrl-hum = 5 + Ctrl-Meas - Done in {:0.1f} ms".format(duration)
        # rdprint(defname, msg)

        resetresp = "Ok"
        raw       = b"Dummy"

        g.I2CstoreBME280.clear()                            # clear deque
        g.bme280.getValBME280()                             # dump first value
        g.I2CstoreBME280.append(g.bme280.getValBME280())    # fill first value

        setIndent(0)
        return resetresp
### END Class SensorBME280 ########################################################

#
# BME280 calculation code #########################################################
#
# code adapted from file bme280.py
# Author : Matt Hawkins
# Date   : 25/07/2016
# http://www.raspberrypi-spy.co.uk/

from ctypes import c_short
from ctypes import c_byte
from ctypes import c_ubyte

def getShort(data, index):
    # return two bytes from data as a signed 16-bit value
    return c_short((data[index+1] << 8) + data[index]).value

def getUShort(data, index):
    # return two bytes from data as an unsigned 16-bit value
    return (data[index+1] << 8) + data[index]

def getChar(data,index):
    # return one byte from data as a signed char
    result = data[index]
    if result > 127:
        result -= 256
    return result

def getUChar(data,index):
    # return one byte from data as an unsigned char
    result =    data[index] & 0xFF
    return result

def readBME280All(cal1, cal2, cal3, pres_raw, t_raw, h_raw):

    # Convert byte data to word values
    dig_T1 = getUShort(cal1, 0)
    dig_T2 = getShort (cal1, 2)
    dig_T3 = getShort (cal1, 4)

    dig_P1 = getUShort(cal1, 6)
    dig_P2 = getShort (cal1, 8)
    dig_P3 = getShort (cal1, 10)
    dig_P4 = getShort (cal1, 12)
    dig_P5 = getShort (cal1, 14)
    dig_P6 = getShort (cal1, 16)
    dig_P7 = getShort (cal1, 18)
    dig_P8 = getShort (cal1, 20)
    dig_P9 = getShort (cal1, 22)

    dig_H1 = getUChar (cal2, 0)
    dig_H2 = getShort (cal3, 0)
    dig_H3 = getUChar (cal3, 2)
    dig_H4 = getChar  (cal3, 3)
    dig_H4 = (dig_H4 << 24) >> 20
    dig_H4 = dig_H4 | (getChar(cal3, 4) & 0x0F)
    dig_H5 = getChar  (cal3, 5)
    dig_H5 = (dig_H5 << 24) >> 20
    dig_H5 = dig_H5 | (getUChar(cal3, 4) >> 4 & 0x0F)
    dig_H6 = getChar  (cal3, 6)

    #Refine temperature
    var1 = ((((t_raw>>3)-(dig_T1<<1)))*(dig_T2)) >> 11
    var2 = (((((t_raw>>4) - (dig_T1)) * ((t_raw>>4) - (dig_T1))) >> 12) * (dig_T3)) >> 14
    t_fine = var1+var2
    temperature = float(((t_fine * 5) + 128) >> 8);

    # Refine pressure and adjust for temperature
    var1 = t_fine / 2 - 64000
    var2 = var1 * var1 * dig_P6 / 32768
    var2 = var2 + var1 * dig_P5 * 2
    var2 = var2 / 4 + dig_P4 * 65536
    var1 = (dig_P3 * var1 * var1 / 524288 + dig_P2 * var1) / 524288
    var1 = (1 + var1 / 32768) * dig_P1
    if var1 == 0:
        pressure=0
    else:
        pressure = 1048576 - pres_raw
        pressure = ((pressure - var2 / 4096.0) * 6250) / var1
        var1 = dig_P9 * pressure * pressure / 2147483648
        var2 = pressure * dig_P8 / 32768
        pressure = pressure + (var1 + var2 + dig_P7) / 16

    # Refine humidity
    humidity = t_fine - 76800
    humidity = (h_raw - (dig_H4 * 64.0 + dig_H5 / 16384.0 * humidity)) * (dig_H2 / 65536.0 * (1.0 + dig_H6 / 67108864.0 * humidity * (1.0 + dig_H3 / 67108864.0 * humidity)))
    humidity = humidity * (1.0 - dig_H1 * humidity / 524288.0)
    if humidity > 100:  humidity = 100
    elif humidity < 0:  humidity = 0

    return temperature/100, pressure/100, humidity
### END SensorBME280 code - class + calculation ################################


#
# I2C for LM75B ################################################################
#
class SensorLM75B:
    """Code for the LM75B sensor"""

    name        = "LM75B"
    addr        = 0x48          # options: 0x48 | 0x49 | 0x4A | 0x4B | 0x4C | 0x4D | 0x4E | 0x4F
    id          = 0x00          # ??

    def __init__(self, addr):
        """Init SensorLM75B class"""
        self.addr    = addr


    def initLM75B(self):
        """Fill 1st value and .... tbd"""

        defname = "initLM75B: "
        dprint(defname)
        setIndent(1)

        # check ID
        tmsg      = "checkID"
        register  = 0x00
        readbytes = 2
        answ      = getI2CBytes(tmsg, self.addr, register, readbytes)
        if len(answ) == readbytes:
            gdprint("Sensor {} at address 0x{:02X} has responded with: {}".format(self.name, self.addr, answ))
        else:
            edprint("FAILURE - Sensor {} at address 0x{:02X} has responded, but with wrong bytecount: {}".format(self.name, self.addr, answ))
            # was tun?

        self.getValLM75B()                               # dump first value
        g.I2CstoreLM75B.append(self.getValLM75B())       # fill first value
        g.I2Csensors.append(self.name)

        setIndent(0)


    def getValLM75B(self):
        """get Temp from I2C connected LM75B"""

        # running on Raspi: takes 0.55 ms typical, range: 0.5 ... 1.5 ms

        start = time.time()
        defname = "getValLM75B:  "

        try:
            register = 0x00
            rbytes   = 2
            raw      = getI2CBytes(self.name, self.addr, register, rbytes)
        except Exception as e:
            exceptPrint(e, defname)
            raw      = "Fail"

        if len(raw) == rbytes:
            temp1    = ((raw[0] << 8 | raw[1] ) >> 5)   # assuming LM75B with 11bit Temp resolution
            if temp1 & 0x400: temp1 = temp1 - 0x800     # 0x400 == 0b0100 0000 0000, 0x800 == 0b1000 0000 0000
            Temp     = temp1 * 0.125                    # deg Celsius for LM75B; +/- 128°C @11 bit => 0.125 °C per step
        else:
            Temp     = g.NAN

        dur = 1000 * (time.time() - start)
        vprint("- {:17s}{:7s}:{:9.3f}  raw:{:10s}  dur:{:0.2f} ms".format(defname, "Temp", Temp, str(raw), dur)) # vprint takes 0.1 ... 0.3 ms

        return Temp


    def resetLM75B(self):
        """Clears deque; the chip has no reset"""

        defname = "resetLM75B: "
        dprint(defname)
        setIndent(1)

        resetresp = "Ok"
        raw       = b"Dummy"

        g.I2CstoreLM75B.clear()                          # clear deque
        self.getValLM75B()                               # dump first value
        g.I2CstoreLM75B.append(self.getValLM75B())       # fill first value

        setIndent(0)
        return resetresp


#
# I2C for BH1750 (= GY-30) ###########################################################
#
class SensorBH1750:
    """Code for the BH1750 sensor"""

    name        = "BH1750"
    addr        = 0x23          # addr options: 0x23 | 0x5C
    id          = 0x00          # ??
    CalibFactor = 1.2           # official data: divide data by 1.2 to get value in Lux

    def __init__(self, addr):
        """Init SensorBH1750 class"""
        self.addr    = addr


    def initBH1750(self):
        """Reset, check ID, set .... tbd"""

        defname = "initBH1750: "
        dprint(defname)

        g.I2Csensors.append(self.name)

        setIndent(1)

        # check ID
        tmsg      = "checkID"
        register  = 0x00
        readbytes = 2
        answ      = getI2CBytes(tmsg, self.addr, register, readbytes)
        if len(answ) == readbytes:
            gdprint("Sensor {} at address 0x{:02X} has responded with: {}".format(self.name, self.addr, answ))
        else:
            edprint("FAILURE - Sensor {} at address 0x{:02X} has responded, but with wrong bytecount: {}".format(self.name, self.addr, answ))
            # was tun?

        self.getValBH1750()                                     # dump first value
        g.I2CstoreBH1750.append(self.getValBH1750())            # fill first value

        setIndent(0)


    def getValBH1750(self):
        """get Light intensity in Lux from I2C connected BH1750
        using one of the sensor's Resolution Modes"""
        # running on Raspi: takes < 1ms (0.6 ms typical)

        start = time.time()

        defname = "getValBH1750:  "

        try:
            # register = 0x10  # Continuously H-Resolution Mode;  Start measurement at 1lx resolution;   Measurement Time is typically 120ms
            # register = 0x11  # Continuously H-Resolution Mode2; Start measurement at 0.5lx resolution; Measurement Time is typically 120ms
            # register = 0x13  # Continuously L-Resolution Mode;  Start measurement at 4lx resolution;   Measurement Time is typically 16ms
            # register = 0x20  # One Time H-Resolution Mode;  Start measurement at 1lx resolution;   Measurement Time is typically 120ms
            register = 0x21    # One Time H-Resolution Mode2; Start measurement at 0.5lx resolution; Measurement Time is typically 120ms
            # register = 0x23  # One Time L-Resolution Mode;  Start measurement at 4lx resolution;   Measurement Time is typically 16ms
            rbytes   = 2
            raw      = getI2CBytes(self.name, self.addr, register, rbytes)
        except Exception as e:
            exceptPrint(e, defname)
            raw      = "Fail"

        if len(raw) == rbytes:  Lux = round((raw[0] << 8 | raw[1]) / self.CalibFactor, 3)
        else:                   Lux = g.NAN

        dur = 1000 * (time.time() - start)
        vprint("- {:17s}{:7s}:{:9.3f}  raw:{:10s}  dur:{:0.2f} ms".format(defname, "Lux", Lux, str(raw), dur)) # vprint takses 0.1 ... 0.2 ms

        return Lux


    def resetBH1750(self):
        """Reset the data register and clears deque"""

        # start   = time.time()
        defname = "resetBH1750: "
        dprint(defname)
        setIndent(1)

        try:
            raw      = b"Dummy"                                # there won't be a read of raw
            register = 0x07
            data     = []
            g.I2Chandle.write_i2c_block_data(self.addr, register, data)
            resetresp = "Ok"
        except Exception as e:
            exceptPrint(e, defname)
            resetresp = "FAILURE"

        g.I2CstoreBH1750.clear()                               # clear deque
        self.getValBH1750()                                    # dump first value
        g.I2CstoreBH1750.append(self.getValBH1750())           # fill first value

        # dur = 1000 * (time.time() - start)
        # vprint(defname + " Resp:{}  raw:{:10s}  dur:{:0.2f} ms".format(resetresp, str(raw), dur))

        setIndent(0)

        return resetresp


#
# I2C for VEML6075     ###########################################################
#
class SensorVEML6075:
    """Code for the VEML6075 sensor"""

    name        = "VEML6075"
    addr        = 0x10          # options: 0x10 | (no other option)
    id          = 0x00          # ???

    def __init__(self, addr):
        """Init SensorVEML6075 class"""
        self.addr    = addr


    def initVEML6075(self):
        """Reset, check ID, set .... tbd"""

        defname = "initVEML6075: "
        dprint(defname)

        g.I2Csensors.append(self.name)

        setIndent(1)

        # check ID
        tmsg      = "checkID"
        register  = 0x00
        readbytes = 2
        answ      = getI2CBytes(tmsg, self.addr, register, readbytes)
        if len(answ) == readbytes:
            gdprint("Sensor {} at address 0x{:02X} has responded with: {}".format(self.name, self.addr, answ))
        else:
            edprint("FAILURE - Sensor {} at address 0x{:02X} has responded, but with wrong bytecount: {}".format(self.name, self.addr, answ))
            # was tun?

        self.getValVEML6075()                                 # dump first value
        g.I2CstoreVEML6075.append(self.getValVEML6075())      # fill first value

        setIndent(0)


    def getValVEML6075(self):
        """get values for all supported variables"""

        defname = "getValVEML6075: "

        uva     = self.getRawVEML6075("UVA")
        uvb     = self.getRawVEML6075("UVB")
        uvd     = self.getRawVEML6075("UVD")       # UVD seems to always be 0 (zero)? now 67 and 68, auch 12,13,14
        uvcomp1 = self.getRawVEML6075("UVCOMP1")
        uvcomp2 = self.getRawVEML6075("UVCOMP2")

        # from Vishay Application Note:
        # UVA comp = ( UVA - UVD ) - a x ( UV comp1 - UVD ) - b x ( UV comp2 - UVD )
        # UVB comp = ( UVB - UVD ) - c x ( UV comp1 - UVD ) - d x ( UV comp2 - UVD )
        # UVI = (UVB comp x UVB resposivity [sic!] ) + ( UVA comp x UVA responsivity ) / 2
        # a = uva_a_coef= 3.33, which is the default value for the UVA VIS coefficient
        # b = uva_b_coef= 2.5,  which is the default value for the UVA IR coefficient
        # c = uvb_c_coef= 3.66, which is the default value for the UVB VIS coefficient
        # d = uvb_d_coef= 2.75, which is the default value for the UVB IR coefficient
        # Typical UVB responsivity = 0.00125 UVI/UVB calc counts.
        # Typical UVA responsivity = 0.0011  UVI/UVA calc counts.
        a = 3.33
        b = 2.5
        c = 3.66
        d = 2.75
        uva_resp = 0.0011
        uvb_resp = 0.00125


        # from Adafruit VEML6075 UVA / UVB / UV Index Sensor:
        # Last updated 2021-11-15
        a = 2.22
        b = 1.33
        c = 2.95
        d = 1.74
        uva_resp = 0.001461
        uvb_resp = 0.002591

        uva_corr = (uva - uvd) - a * (uvcomp1 - uvd) - b * (uvcomp2 - uvd)
        uvb_corr = (uvb - uvd) - c * (uvcomp1 - uvd) - d * (uvcomp2 - uvd)
        uvi      = 0.5 * (uva_corr * uva_resp + uvb_corr * uvb_resp)

        cdprint("- {:17s}UVAcorr: {:8.3f}".format(defname, uva_corr))
        cdprint("- {:17s}UVBcorr: {:8.3f}".format(defname, uvb_corr))
        cdprint("- {:17s}UVI    : {:8.3f}".format(defname, uvi))

        # cI2Cvars_VEML6075   = {"CPM2nd" :1, "CPS2nd":1, "CPM3rd":1, "CPS3rd":1, "CPS1st":1, "CPM":1, "CPS":1 }
        uvab = []
        uvab.append(uva)        # --> CPM2nd
        uvab.append(uvb)        # --> CPS2nd
        uvab.append(uva_corr)   # --> CPM3rd
        uvab.append(uvb_corr)   # --> CPS3rd
        uvab.append(uvd)        # --> CPS1st
        uvab.append(uvcomp1)    # --> CPM
        uvab.append(uvcomp2)    # --> CPS

        return uvab


    def getRawVEML6075(self, UVtype):
        """get intensity of UVtype (UV-A, UV-B, UV-other) from I2C connected VEML6075"""

        # running on Raspi:     takes  1 ... 2 ms

        start = time.time()
        defname = "getRawVEML6075: "

        try:
            register = 0x00
            data     = [0x00, 0x00]
            g.I2Chandle.write_i2c_block_data(self.addr, register, data)

            if   UVtype == "UVA":        register = 0x07 # UV-A data
            elif UVtype == "UVD":        register = 0x08 # UV-D data         # seems to always return zero
            elif UVtype == "UVB":        register = 0x09 # UV-B data
            elif UVtype == "UVCOMP1":    register = 0x0A # UV-comp1 data
            elif UVtype == "UVCOMP2":    register = 0x0B # UV-comp2 data
            else:                        return g.NAN

            rbytes   = 2
            raw      = getI2CBytes(self.name, self.addr, register, rbytes)
        except Exception as e:
            exceptPrint(e, defname)
            raw = b"Fail"

        if len(raw) == rbytes:  UVdata = (raw[1] << 8 | raw[0])
        else:                   UVdata = g.NAN

        dur = 1000 * (time.time() - start)
        vprint("- {:17s}{:7s}:{:9.3f}  raw:{:10s}  dur:{:0.2f} ms".format(defname, UVtype, UVdata, str(raw), dur))

        return UVdata


    def resetVEML6075(self):
        """Clears deque; the chip has no reset"""

        # start   = time.time()
        defname = "resetVEML6075: "
        dprint(defname)
        setIndent(1)

        resetresp = "Ok"
        raw       = b"Fake"

        g.I2CstoreVEML6075.clear()                              # clear deque
        self.getValVEML6075()                                   # dump first value
        g.I2CstoreVEML6075.append(self.getValVEML6075())        # fill first value

        # dur = 1000 * (time.time() - start)
        # vprint(defname + " Resp:{}  raw:{:10s}  dur:{:0.2f} ms".format(resetresp, str(raw), dur))

        setIndent(0)
        return resetresp


    def getIdVEML6075(self):
        """read ID of VEML6075; should be [0x26, 0x00]"""
        # return: [38, 0] = [0x26, 0x00] - Default by data sheet=[0x26, 0x00] -> ok!
        # runtime on Raspi: < 1 ms

        start   = time.time()
        defname = "getIdVEML6075: "

        register = 0x00
        data     = [0x00, 0x00]
        g.I2Chandle.write_i2c_block_data(self.addr, register, data)

        register = 0x0C
        rbytes   = 2
        raw      = getI2CBytes(self.name, self.addr, register, rbytes)

        if len(raw) == rbytes: idresp = raw[0]
        else:                  idresp = 0xFF

        dur = 1000 * (time.time() - start)
        vprint(defname + " ID:{}  raw:{:10s}  dur:{:0.2f} ms".format(idresp, str(raw), dur))

        return idresp


#
# I2C for LTR390     ###########################################################
#
class SensorLTR390:
    """Code for the LTR390 sensor"""

    name        = "LTR390"
    addr        = 0x53          # addr options: 0x53 (nothing else) (= 83)
    id          = 0xB2          # 0xB2 = 178
    reg_ctrl    = 0x00          # MAIN_CTRL     Register (Address: 0x00) (Read/Write)
    reg_partid  = 0x06          # PART_ID       Register (Address: 0x06) (Read Only)
    reg_status  = 0x07          # MAIN_STATUS   Register (Address: 0x07) (Read Only)
    reg_ALSdata = 0x0D          # The registers 0x0D, 0x0E & 0x0F contain ALS data, up to 20bits
    reg_UVSdata = 0x10          # The registers 0x10, 0x11 & 0x12 contain UVS data, up to 20bits
    gain_fac    = 3             # @ default gain
    int_fac     = 1             # @ default integration time (18-bit, 100ms)
    als_cmd     = 0b00000010    # = 0x02    - cmd to measure vis light
    uvs_cmd     = 0b00001010    # = 0x0A    - cmd to measure uv light

    def __init__(self, addr):
        """Init SensorLTR390 class"""
        self.addr    = addr


    def initLTR390(self):
        """Reset, check ID, set .... tbd"""

        defname = "initLTR390: "
        dprint(defname)
        setIndent(1)

        # get sensor id (should be 0xB2)
        id = self.getIdLTR390()
        if id == self.id:  msg = "Sensor {} at address {:#04x} has proper ID: {:#04x}"
        else:              msg = "Sensor {} at address {:#04x} has wrong ID: '{}'"
        gdprint(msg.format(self.name, self.addr, id))

        # is there any value to read the registers?
        # # read the MAIN_CTRL register
        # main = self.getMainRegLTR390()
        # rdprint("read Main Ctrl: {:#04x}".format(main))

        # # read the STATUS register; thereby clearing it
        status = self.getStatusRegLTR390()
        # rdprint("read Status1:   {:#04x}".format(status))

        # self.resetLTR390() # presently has only deque reset

        self.getValLTR390()                                     # dump first value
        g.I2CstoreLTR390.append(self.getValLTR390())            # fill first value

        g.I2Csensors.append(self.name)
        setIndent(0)


    def getStatusRegLTR390(self):
        """read the status byte at 0x07"""
        # NOTE: upon reading the MAIN_STATUS Register the UVS/ALS Data Status Bit (= Bit 3) is
        # reset to 0 the flag "new data" cannot be seen more than once for a given conversion

        defname      = "getStatusRegLTR390: "
        rbytes       = 1
        try:
            raw      = getI2CBytes(self.name, self.addr, self.reg_status, rbytes)
            status   = raw[0]
        except Exception as e:
            exceptPrint(e, defname)
            status   = 0xFF     # can never be result from the chip

        return status


    def getMainRegLTR390(self):
        """read the Main CTRL byte at 0x00"""

        defname = "getMainRegLTR390: "
        rbytes  = 1
        try:
            raw      = getI2CBytes(self.name, self.addr, self.reg_ctrl, rbytes)
            main     = raw[0]
        except Exception as e:
            exceptPrint(e, defname)
            main     = 0xFF     # can never be result from the chip

        return main


    def getValLTR390(self):
        """get both vis + uv"""

        # Datasheet:
        # 7.1 ALS Lux Formula
        # Lux_Calc is the calculated lux reading based on the output ADC from ALS DATA
        # regardless of light sources:
        #
        # LuxCalc = 0.6 × ALS_DATA × WFAC / (GAIN × INT)  => 0.6 * ALS-Data * 1 /(3 * 1)  => ALS-Data * 0.2
        # default: self.gain_fac == 3, self.int_fac == 1, WFAC = 1 for NO window / clear window glass
        #
        # 7.2 UVI Conversion Formula
        # UVICalc = UV Sensor Count × WFAC / UV Sensitivity
        # WFAC depends on the type of window used. WFAC=1 (no window)
        # 4.5. Characteristics UVS Sensor: UV Sensitivity: 2300Counts/UVI (Gain range = 18, 20-bit)

        defname = "getValLTR390: "

        vis     = self.getRawLTR390("VIS")
        uv      = self.getRawLTR390("UV")

        # convert vis to Lux, uv to UVI
        vis_Lux = round(0.6 * vis * 1.0 / (self.gain_fac * self.int_fac), 3)
        uvindex = round(uv * 1 / 2300, 3)                                        # not valid behind window

        dprint("- {:17s}Vis:{:<8.3f} vis_Lux:{:<8.3f}  UV:{:<8.3f} UVI:{:<8.3f}".format(defname, vis, vis_Lux, uv, uvindex))

        visuv = []
        visuv.append(vis_Lux)              # --> CPM
        visuv.append(uv)                   # --> CPS

        return visuv


    def getRawLTR390(self, ltype):
        """get intensity of vis and UV from I2C connected LTR390"""

        # Raspi: takes >~100 ms due to waiting for data (takes ~100 ms)

        start = time.time()
        defname = "getRawLTR390:  "

        if ltype == "VIS":                   # ALS data (visible light) -> active
            ctrl_cmd     = self.als_cmd
            val_register = self.reg_ALSdata
        elif ltype == "UV":                  # UVS data (UV light)  -> active
            ctrl_cmd     = self.uvs_cmd
            val_register = self.reg_UVSdata
        else:
            edprint(defname, "ERROR unknown ltype '{}'. Exiting".format(ltype))
            sys.exit()

        value = g.NAN
        raw   = b"Fail"

        while True:
            # write ctrl_cmd to the MAIN_CTRL register to start conversion
            try:
                data_list     = [ctrl_cmd]
                g.I2Chandle.write_i2c_block_data(self.addr, self.reg_ctrl, data_list)
                # rdprint("have written: ", data_list)
            except Exception as e:
                exceptPrint(e, defname + "write data to device")
                break

            # dump the status, if set it is an expired value anyway
            status = self.getStatusRegLTR390()
            # rdprint(defname, "status dump1: ", status)

            # now wait for ready status
            statusstart = time.time()
            time.sleep(0.09)
            while (time.time() - statusstart) < 0.5 : # try not longer than 500 ms
                status = self.getStatusRegLTR390()
                # rdprint(defname, "status real: ", status)
                if (status & 0b00001000):                            # test for bit#3 (value=8) set in status
                    dt = 1000 * (time.time() - statusstart)
                    # rdprint(defname, "STATUS:{}  {:0.1f} ms".format(status, dt))
                    break
                time.sleep(0.01)

            # get the data
            rbytes = 3
            try:
                raw      = getI2CBytes(self.name, self.addr, val_register, rbytes)
                value    = (raw[2] << 8 | raw[1]) << 8 | raw[0]
            except Exception as e:
                exceptPrint(e, defname)
                raw      = b"Fail"
                value    = g.NAN

            break

        dur = 1000 * (time.time() - start)
        # vprint("- {:17s}{:7s}:{:9.3f}  raw:{:10s}  dur:{:0.2f} ms".format(defname, ltype, value, str(raw), dur))

        return  value


    def resetLTR390(self):
        """Clears deque; resetting the chip does not work"""

        # start   = time.time()
        defname = "resetLTR390: "
        dprint(defname)
        setIndent(1)

        resetresp = "Ok"
        raw = "Dummy"

        # try:
        #     # write to the MAIN_CTRL register
        #     ctrl_cmd      = 0b00010000        # = 0x10
        #     # ctrl_cmd      = 0b00000000        # = 0x00

        #     data_list     = [ctrl_cmd]
        #     g.I2Chandle.write_i2c_block_data(self.addr, self.reg_ctrl, data_list)
        #     resetresp = "Ok"
        # except Exception as e:
        #     exceptPrint(e, defname)
        #     idresp   = g.NAN
        #     raw      = b"Fail"
        #     resetresp = "Fail"

        g.I2CstoreLTR390.clear()                                   # clear deque
        self.getValLTR390()                                        # dump first value
        g.I2CstoreLTR390.append(self.getValLTR390())               # fill first value

        # dur = 1000 * (time.time() - start)
        # vprint(defname + " Resp:{}  raw:{:10s}  dur:{:0.2f} ms".format(resetresp, str(raw), dur))

        setIndent(0)
        return resetresp


    def getIdLTR390(self):
        """read ID of LTR390; should be 0xB2 (=178)"""
        # runtime on Raspi: < 1 ms (0.56 ms)

        # start   = time.time()
        defname = "getIdLTR390: "

        try:
            rbytes   = 1
            raw      = getI2CBytes(self.name, self.addr, self.reg_partid, rbytes)
            idresp   = raw[0]
        except Exception as e:
            exceptPrint(e, defname)
            idresp   = g.NAN
            raw      = b"Fail"

        # dur = 1000 * (time.time() - start)
        # vprint(defname + " Resp:{}  raw:{:10s}  dur:{:0.2f} ms".format(idresp, str(raw), dur))

        return idresp


#
# I2C for GDK101 ##########################################################
#
class SensorGDK101:
    """Code for the GDK101 sensor"""

    name        = "GDK101"
    addr        = 0x18          # options: 0x18 | 0x19 | 0x1A | 0x1B
    id          = 0x00          # ??

    def __init__(self, addr):
        """Init SensorGDK101 class"""
        self.addr    = addr


    def initGDK101(self):
        """Reset, check ID, set .... tbd"""

        defname = "initGDK101: "
        dprint(defname)
        g.I2Csensors.append(self.name)

        setIndent(1)

        # check ID
        tmsg      = "checkID"
        register  = 0x00
        readbytes = 2
        answ      = getI2CBytes(tmsg, self.addr, register, readbytes)
        if len(answ) == readbytes:
            gdprint("Sensor {} at address 0x{:02X} has responded with: {}".format(self.name, self.addr, answ))
        else:
            edprint("FAILURE - Sensor {} at address 0x{:02X} has responded, but with wrong bytecount: {}".format(self.name, self.addr, answ))
            # was tun?

        self.getValGDK101("OneMin")                             # dump first value OneMin
        self.getValGDK101("TenMin")                             # dump first value TenMin
        g.I2CstoreGDK101.append(self.getValGDK101("OneMin"))    # fill first value - only OneMin; TenMin is ignored

        setIndent(0)


    def getValGDK101(self, ctype):
        """get data from GDK101
        - ctype is: "OneMin" => 0xB3: Counts per 1 min
        -       or: "TenMin" => 0xB2: Counts per 1 min derived from counting 10 min
        return: count rate in CPM terms"""

        start = time.time()
        defname = "getValGDK101: "

        register = 0xB2 if ctype == "TenMin" else 0xB3                 # default is 1 min == 0xB3
        rbytes   = 2
        raw      = getI2CBytes(self.name, self.addr, register, rbytes)

        #
        # # Vibration does NOT seem to have any effect on read-out value, so why bother with vibration???
        #
        # if getGDK101Status()[1] == 1:
        #     # detected vibration
        #     rdprint("saw vibration, reading anyway", )
        #     raw  = getI2CBytes(device, addr, register, rbytes)
        #     rdprint("saw vibration, raw: ", raw)
        #     raw  = b"Vibrate"
        #
        # else:
        #     # no vibration, valid data
        #     raw  = getI2CBytes(device, addr, register, rbytes)
        #     rdprint("without vibration, raw: ", raw)

        if len(raw) == rbytes:
            # Problem: double zero can be correct value, but also happens as erroneous reading
            # how to distinguish?
            usvvalue = raw[0] + (raw[1] / 100)
            cpmvalue = round(usvvalue * 8.3334, 3)
        else:
            edprint(defname + "raw does not have length of 2: {}".format(raw))
            usvvalue = g.NAN
            cpmvalue = g.NAN

        dur = 1000 * (time.time() - start)
        vprint("- {:17s}{:7s}:{:9.3f}  raw:{:10s}  dur:{:0.2f} ms  usv:{:0.2f}".format(defname, ctype, cpmvalue, str(raw), dur, usvvalue))

        return cpmvalue


    def getGDK101MeasTime(self):
        """get measurement time from GDK101; goes from 0 ... 11, then cycles within 10 ... 11.
        return: time in minutes"""

        start = time.time()
        defname = "getGDK101MeasTime: "

        ctype    = "MTime"
        register = 0xB1
        rbytes   = 2
        raw      = getI2CBytes(self.name, self.addr, register, rbytes)

        if len(raw) == rbytes:
            value    = round((raw[0] * 60 + raw[1]) / 60, 3)     # ((minutes * 60 + seconds) / 60)  ==>  minutes
        else:
            edprint(defname + "raw:{} does not have length of {}".format(raw, rbytes))
            value = g.NAN

        dur = 1000 * (time.time() - start)
        dprint("{:20s}{:6s}  raw:{:10s}  value:{:6.3f}  dur:{:0.2f} ms".format(defname, ctype, str(raw), value, dur))

        return value


    def getGDK101Firmware(self):
        """get firmware from GDK101
        return: major.minor firmware"""

        start = time.time()
        defname = "getGDK101Firmware: "
        ctype   = "FirmW"

        register = 0xB4
        rbytes   = 2
        raw      = getI2CBytes(self.name, self.addr, register, rbytes)

        if len(raw) == rbytes:
            firmw = "{}.{}".format(*raw)
        else:
            edprint(defname + "raw does not have length of {}: {}".format(rbytes, raw))
            firmw = "Failure"

        dur = 1000 * (time.time() - start)
        dprint("{:20s}{:6s}  raw:{:10s}  FirmW:{}  dur:{:0.2f} ms".format(defname, ctype, str(raw), firmw, dur))

        return firmw


    def getGDK101Status(self):
        """get status and vibration status from GDK101
        return: tuple: (status, vibratestatus)"""

        start = time.time()

        defname = "getGDK101Status: "
        ctype   = "Status"

        register = 0xB0
        rbytes   = 2
        raw      = getI2CBytes(self.name, self.addr, register, rbytes)

        if len(raw) == rbytes:
            status   = (raw[0], raw[1])
        else:
            edprint(defname + "raw does not have length of {}: {}".format(raw, rbytes))
            status = (g.NAN, g.NAN)

        dur = 1000 * (time.time() - start)
        dprint("-- {:20s}{:6s}  raw:{:10s}  dur:{:0.2f} ms".format(defname, ctype, str(raw), dur))

        return status


    def resetGDK101(self):
        """Resets the GDK101 by clearing count register
        return: resetresp"""

        # start = time.time()
        defname = "resetGDK101: "
        dprint(defname)
        setIndent(1)

        register = 0xA0
        rbytes   = 2
        raw      = getI2CBytes(self.name, self.addr, register, rbytes)

        if len(raw) == rbytes:
            if raw[0] == 1: resetresp = "Ok"    # check msb only
            else:           resetresp = "FAIL"
        else:
            edprint(defname + "raw does not have length of {}: {}".format(rbytes, raw))
            resetresp = "FAIL"

        self.getValGDK101("OneMin")                             # dump value
        self.getValGDK101("TenMin")                             # dump value

        # dur = 1000 * (time.time() - start)
        # vprint("{:20s} raw:{:10s}  Reset:{}  dur:{:0.2f} ms".format(defname, str(raw), resetresp, dur))
        setIndent(0)
        return resetresp



#
# I2C for SCD30 (CO2)  ##########################################################
#
class SensorSCD30:
    """Code for the SCD30 CO2 sensor"""

    name        = "SCD30"
    addr        = 0x61          # the only option for the SCD30
    id          = 0x00          # ??
    firmware    = "not set"     # my device: 3.66 (same as example from manual)
    measIntvl   = 5             # Measurement Interval in sec (default = 2)
    frc         = None          # Forced Recalibration value (FRC). Default is 400 [ppm]


    def __init__(self, addr):
        """Init SensorSCD30 class"""
        self.addr    = addr


    def initSCD30(self):
        """Reset, check ID, set .... tbd"""

        defname = "initSCD30: "
        dprint(defname)
        g.I2Csensors.append(self.name)

        setIndent(1)

        # # check ID
        # tmsg      = "checkID"
        # register  = 0x00
        # readbytes = 2
        # answ      = getI2CBytes(tmsg, self.addr, register, readbytes)
        # if len(answ) == readbytes:
        #     gdprint("Sensor {} at address 0x{:02X} has responded with: {}".format(self.name, self.addr, answ))
        # else:
        #     edprint("FAILURE - Sensor {} at address 0x{:02X} has responded, but with wrong bytecount: {}".format(self.name, self.addr, answ))
        #     # was tun?

        ## get firmware version
        cdprint(defname + "Get Firmware")
        gdprint(self.SCD30getFirmwareVersion())

        ## start auto measurements
        dprint(defname + "next is: SCD30MeasurementStart")
        gdprint(self.SCD30MeasurementStart())

        self.getValSCD30()                          # dump first value OneMin
        g.I2CstoreSCD30.append(self.getValSCD30())  # fill first value

        setIndent(0)


    def SCD30MeasurementStart(self):
        """needs to be done only once"""

        # 1.4.1 Trigger continuous measurement with optional ambient pressure compensation
        # Starts continuous measurement of the SCD30 to measure CO2 concentration, humidity
        # and temperature. Measurement data which is not read from the sensor will be overwritten.
        # The measurement interval is adjustable via the command documented in chapter 1.4.3,
        # initial measurement rate is 2s.
        # Continuous measurement status is saved in non-volatile memory. When the sensor is
        # powered down while continuous measurement mode is active SCD30 will measure
        # continuously after repowering without sending the measurement command. The CO2
        # measurement value can be compensated for ambient pressure by feeding the pressure value
        # in mBar to the sensor. Setting the ambient pressure will overwrite previous settings of
        # altitude compensation. Setting the argument to zero will deactivate the ambient pressure
        # compensation (default ambient pressure = 1013.25 mBar). For setting a new ambient pressure
        # when continuous measurement is running the whole command has to be written to SCD30.
        #
        # command: 0x0010 argument
        # argument: Format: uint16 Available range: 0 & [700 ... 1400]. Pressure in mBar.
        # argument: 0x00 0x00 0x81 : Start continuous measurement without ambient pressure compensation

        defname = "SCD30MeasurementStart: "

        tmsg      = "StartMeas"
        register  = 0x0010
        readbytes = 0
        data      = [0x00, 0x00, 0x81]
        # wrt       = g.I2CDongle.DongleWriteReg(self.addr, register, readbytes, data, addrScheme=3, msg=tmsg)
        g.I2Chandle.write_i2c_block_data(self.addr, register, data)
        # answ      = getI2CBytes(self.name, self.addr, register, readbytes)

        time.sleep(0.1)

        try:
            raw = g.I2Chandle.read_i2c_block_data(self.addr, register, readbytes)
        except Exception as e:
            exceptPrint(e, defname + "{}  FAILURE I2C read: addr:{}, reg:{}, rbytes:{}".format("SCD30", hex(self.addr), hex(register), readbytes))
            raw = b"Fail"
            edprint(defname + "Fail in trial #{}, trying again.".format(1))


        rdprint(defname, "raw: ", raw)
        return defname + "Done"




    def getValSCD30(self):
        """Read the CO2, Temp and Humid values if available"""

        defname = "getValSCD30: "

        # 1.4.5 Read measurement
        # When new measurement data is available it can be read out with the following command.
        # Note that the read header should be send with a delay of > 3ms following the write
        # sequence. Make sure that the measurement is completed by reading the data ready status
        # bit before read out.
        #
        # Command: 0x0300, no argument needed. Reads a single measurement of CO2 concentration. (But also the rest!)
        # Example with sensor returning:  CO2 Concentration = 439 PPM
        #                                 Humidity          = 48.8 %
        #                                 Temperature       = 27.2 °C
        # CO2  CO2       CO2  CO2       T    T         T    T         RH   RH        RH   RH
        # MMSB MLSB CRC  LMSB LLSB CRC  MMSB MLSB CRC  LMSB LLSB CRC  MMSB MLSB CRC  LMSB LLSB CRC
        # 0x43 0xDB 0xCB 0x8c 0x2e 0x8f 0x41 0xd9 0x70 0xe7 0xff 0xf5 0x42 0x43 0xbf 0x3a 0x1b 0x74
        # Example: The CO2 concentration 400 ppm corresponds to 0x43c80000 in Big-Endian notation.


        start   = time.time()
        sgvdata = (g.NAN,) * 3

        cdprint(defname)
        setIndent(1)

        dataReady = self.SCD30DataReady()

        if  dataReady == 1:
            # data are ready
            tmsg      = "getval"
            register  = 0x0300
            readbytes = 18
            data      = []
            wait      = 0.003       # wait 3 ms acc to datasheet:  Version 1.0 – D1 – May 2020
            # answ      = g.I2CDongle.DongleWriteRead (self.addr, register, readbytes, data, addrScheme=3, msg=tmsg, wait=wait)
            # answ       = getI2CBytes(self.name, self.addr, register, readbytes)

            g.I2Chandle.write_i2c_block_data(self.addr, register, data)
            # answ      = getI2CBytes(self.name, self.addr, register, readbytes)
            time.sleep(0.05)
            try:
                answ = g.I2Chandle.read_i2c_block_data(self.addr, register, readbytes)
            except Exception as e:
                exceptPrint(e, defname + "{}  FAILURE I2C read: addr:{}, reg:{}, rbytes:{}".format("SCD30", hex(self.addr), hex(register), readbytes))
                answ = b"Fail"
                edprint(defname + "Fail in trial #{}, trying again.".format(1))


            #####################################################################################################################
            # reference --> CO2 Concentration = 439 PPM, Temperature = 27.2 °C,  Humidity = 48.8 %
            # answ = [0x43, 0xDB, 0xCB, 0x8c, 0x2e, 0x8f, 0x41, 0xd9, 0x70, 0xe7, 0xff, 0xf5, 0x42, 0x43, 0xbf, 0x3a, 0x1b, 0x74]
            #####################################################################################################################

            if len(answ) == readbytes:
                # Big-Endian notation
                # must convert to float explicitely, because numpy data format creates blobs in the SQL database!

                data_bytes = np.array(answ[0:2]   + answ[3:5],   dtype=np.uint8)
                co2 = float(data_bytes.view(dtype='>f')[0])

                data_bytes = np.array(answ[6:8]   + answ[9:11],  dtype=np.uint8)
                temp = float(data_bytes.view(dtype='>f')[0])

                data_bytes = np.array(answ[12:14] + answ[15:17], dtype=np.uint8)
                humid = float(data_bytes.view(dtype='>f')[0])

                if co2 > 300:   sgvdata = (round(co2, 0), round(temp, 3), round(humid, 3))    # first value is most often CO2==0; should be >400, but give it room

                msg = True, defname + "CO2:{:6.3f}, Temp:{:6.3f}, Humid:{:6.3f}".format(co2, temp, humid)
            else:
                msg = False, defname + "Failure reading proper byte count"

        else:
            # data not ready
            msg = False, defname + "Data NOT ready, or failure to get status, or wrong bytecount"

        duration = (time.time() - start) * 1000
        if msg[0]:      gdprint(msg[1] + "  dur:{:0.2f} ms".format(duration))

        setIndent(0)
        return sgvdata[0]


    def SCD30DataReady(self):
        """get the data-ready status of sensor;
        return: 1 True      Data are ready
                0 False     Data are NOT ready
                -1          Improper response
        """

        # 1.4.4 Get data ready status
        # Data ready command is used to determine if a measurement can be read from the sensor’s
        # buffer. Whenever there is a measurement available from the internal buffer this command
        # returns 1 and 0 otherwise. As soon as the measurement has been read by the return value
        # changes to 0. Note that the read header should be send with a delay of > 3ms following
        # the write sequence.
        # It is recommended to use data ready status byte before readout of the measurement values.
        #
        # command: 0x0202, no argument needed
        # readbytes: 3;  MSB, LSB, CRC

        start   = time.time()
        defname = "SCD30DataReady: "
        # rdprint(defname)

        ready     = -1      # code for failure
        tmsg      = "Ready?"
        msg       = ""
        register  = 0x0202
        readbytes = 3
        data      = []
        wait      = 0.003           # wait 3 ms acc to datasheet:  Version 1.0 – D1 – May 2020
        # answ      = g.I2CDongle.DongleWriteRead (self.addr, register, readbytes, data, addrScheme=3, msg=tmsg, wait=wait)
        # answ       = getI2CBytes(self.name, self.addr, register, readbytes)

        g.I2Chandle.write_i2c_block_data(self.addr, register, data)

        # answ      = getI2CBytes(self.name, self.addr, register, readbytes)

        time.sleep(0.05)

        try:
            answ = g.I2Chandle.read_i2c_block_data(self.addr, register, readbytes)
        except Exception as e:
            exceptPrint(e, defname + "{}  FAILURE I2C read: addr:{}, reg:{}, rbytes:{}".format("SCD30", hex(self.addr), hex(register), readbytes))
            answ = b"Fail"
            edprint(defname + "Fail in trial #{}, trying again.".format(1))


        # rdprint(defname, "answ: ", answ)

        msg  = defname + "answ: {}".format(answ)
        msg1 = ""

        duration = (time.time() - start) * 1000

        if len(answ) == readbytes:
            word0 = answ[0] << 8 | answ[1]
            if    word0 == 1:
                ready = True        # Data are ready
                msg1  += "30  Data ready"
                color = BOLDGREEN
            else:
                ready = False       # Data are NOT ready
                msg1  += "30  Data NOT ready"
                color = BOLDRED

            msg += " " * 70 + "{}{}".format(color, msg1)

        elif len(answ) == 0:
            msg += BOLDRED + "30  No data returned: answ= '{}'".format(answ)

        else:
            msg += BOLDRED + "30  Improper data returned: answ= '{}'".format(answ)

        cdprint(msg + "  {:0.1f} ms".format(duration))

        return ready


    def SCD30getFirmwareVersion(self):
        """get the Firmware Version as Major.Minor"""

        # 1.4.9 Read firmware version
        # Command:  0xD100 , no argument needed
        # Wait None in datasheet Version 1.0 – D1 – May 2020
        # response: 3 bytes (2 b firmware + 1 bcrc) Firmware version: Major.Minor: 0x03, 0x42 => 3.66 (3.66 is also found on my chip)

        # Duration:
        # ISS: SCD30getFirmwareVersion: duration: 1.6 ms

        start = time.time()
        defname = "SCD30getFirmwareVersion: "

        tmsg      = "FirmWr"
        register  = 0xD100
        readbytes = 3
        data      = []
        wait      = 0
        # answ      = g.I2CDongle.DongleWriteRead (self.addr, register, readbytes, data, addrScheme=3, msg=tmsg, wait=wait)

        g.I2Chandle.write_i2c_block_data(self.addr, register, data)
        time.sleep(0.3)
        try:
            answ = g.I2Chandle.read_i2c_block_data(self.addr, register, readbytes)
            rdprint(defname, "ansW: ", answ)
        except Exception as e:
            exceptPrint(e, defname + "{}  FAILURE I2C read: addr:{}, reg:{}, rbytes:{}".format("SCD30", hex(self.addr), hex(register), readbytes))
            answ = b"Fail"
            edprint(defname + "Fail in trial #{}, trying again.".format(1))


        if len(answ) != readbytes:
            edprint(defname + "Failure reading Serial Number, reponse: ", answ)
            return "Not Found"

        self.firmware = "{}.{}".format(answ[0], answ[1])

        duration = (time.time() - start) * 1000
        msg = defname + "got firmware:{}  in:{:0.1f} ms".format(self.firmware, duration)

        return msg





#
# I2C for SCD41 (CO2, Temp, Humid)  ##########################################################
#
class SensorSCD41:
    """Code for the SCD41 CO2 sensor"""

    name        = "SCD41"
    addr        = 0x62          # the only option for the SCD41
    serno       = "not set"     # SCD41 Serial Number, like: 273.325.796.834.238

    # id          = 0x00          # ??
    # firmware    = "not set"     # my device: 3.66 (same as example from manual)
    # measIntvl   = 5             # Measurement Interval in sec (default = 2)
    # frc         = None          # Forced Recalibration value (FRC). Default is 400 [ppm]


    def __init__(self, addr):
        """Init SensorSCD41 class"""
        self.addr    = addr


    def initSCD41(self):
        """Reset, check ID, set .... tbd"""

        defname = "initSCD41: "
        dprint(defname)
        g.I2Csensors.append(self.name)

        setIndent(1)

        # # check ID
        # tmsg      = "checkID"
        # register  = 0x00
        # readbytes = 2
        # answ      = getI2CBytes(tmsg, self.addr, register, readbytes)
        # if len(answ) == readbytes:
        #     gdprint("Sensor {} at address 0x{:02X} has responded with: {}".format(self.name, self.addr, answ))
        # else:
        #     edprint("FAILURE - Sensor {} at address 0x{:02X} has responded, but with wrong bytecount: {}".format(self.name, self.addr, answ))
        #     # was tun?

        # ## get firmware version
        # cdprint(defname + "Get Firmware")
        # gdprint(self.SCD41getFirmwareVersion())

        # ## start auto measurements
        # dprint(defname + "next is: SCD41MeasurementStart")
        # gdprint(self.SCD41MeasurementStart())

        # self.getValSCD41()                          # dump first value OneMin
        # g.I2CstoreSCD41.append(self.getValSCD41())          # fill first value


        # # stop auto measurements (maybe active from last start!!)
        gdprint(defname + "stopping Auto-Measurement")
        wrt  = self.SCD41StopPeriodicMeasurement()

        # # # get serial number - requires that auto-measurement is stopped!
        # gdprint(defname + "Getting SerNo:")
        # self.serno = "{:n}".format(self.SCD41getSerialNumber())
        # gdprint(defname + "Got SerNo: " + self.serno)

        # # Trigger auto measurements
        gdprint(defname + "Triggering Auto-Measurement")
        wrt  = self.SCD41StartPeriodicMeasurement()

        setIndent(0)


    def SCD41StopPeriodicMeasurement(self):
        """needs to be done to stop activity"""

        # 3.5.3 stop_periodic_measurement
        # Note that the sensor will only respond to other commands after
        # waiting 500 ms after issuing the stop_periodic_measurement command.
        # Write 0x3f86
        # response: None

        defname = "SCD41StopPeriodicMeasurement: "

        tmsg      = "StopMeas"
        register  = 0x3f86
        readbytes = 0
        data      = []
        try:
            # wrt       = g.I2CDongle.DongleWriteReg(self.addr, register, readbytes, data, addrScheme=2, msg=tmsg)
            wrt = g.I2Chandle.write_i2c_block_data(self.addr, register, data)
            # answ      = getI2CBytes(self.name, self.addr, register, readbytes)
        except Exception as e:
            exceptPrint(e, defname)

        # Required wait 500 ms
        dprint(defname + "waiting 500 ms")
        time.sleep(0.5)

        return wrt


    def SCD41getSerialNumber(self):
        """get the Serial Number"""

        # CAUTION CAUTION CAUTION CAUTION CAUTION CAUTION CAUTION CAUTION
        #        must NOT be called with Auto-Measurement ongoing !!!!!
        # CAUTION CAUTION CAUTION CAUTION CAUTION CAUTION CAUTION CAUTION
        #
        # Write: 0x3682
        # Response: 9 bytes
        # Serial number = word[0] << 32 | word[1] << 16 | word[2]
        # Example:            0xf896 0x31  0x9f07 0xc2  0x3bbe 0x89       ==> 273’325’796’834’238
        # Max. command duration: 1 ms

        # my code on Example: [0xf8, 0x96, 0x31, 0x9f, 0x07, 0xc2, 0x3b, 0xbe, 0x89] ==> 273’325’796’834’238 ==> my code is ok
        # my device with:
        # ISS: SCD41getSerialNumber: answ: [13, 65, 205, 191, 7, 30, 59, 79, 58]  SerNo:  14.576.028.957.519
        # ELV: SCD41getSerialNumber: answ: [13, 65, 205, 191, 7, 30, 59, 79, 58]  SerNo:  14.576.028.957.519     # das isses wohl


        defname = "SCD41getSerialNumber: "

        tmsg      = "SerNo"
        register  = 0x3682
        readbytes = 9
        data      = []
        wait      = 0.001       # 1 ms wait suggested by manual (bei IOW: 100 ms reicht auch nicht)

        # try:
        #     # wrt       = g.I2CDongle.DongleWriteReg(self.addr, register, readbytes, data, addrScheme=2, msg=tmsg)
        #     wrt = g.I2Chandle.write_i2c_block_data(self.addr, register, data)
        #     # answ      = getI2CBytes(self.name, self.addr, register, readbytes)
        # except Exception as e:
        #     exceptPrint(e, defname)
        # answ      = g.I2CDongle.DongleWriteRead  (self.addr, register, readbytes, data, addrScheme=2, msg=tmsg, wait=wait)

        try:
            wrt = g.I2Chandle.write_i2c_block_data(self.addr, register, data)
        except Exception as e:
            exceptPrint(e, defname)

        time.sleep(0.1)
        try:
            answ = g.I2Chandle.read_i2c_block_data(self.addr, register, readbytes)
        except Exception as e:
            # exceptPrint(e, defname + "{}  FAILURE I2C read: addr:{:#04x}, reg:{:#04x}, rbytes:{}".format("SCD41", hex(self.addr), hex(register), readbytes))
            exceptPrint(e, defname + "{}  FAILURE I2C read: addr:{:#04x}, reg:{:#04x}, rbytes:{}".format("SCD41", self.addr, register, readbytes))
            answ = b"Fail"
            edprint(defname + "Fail in trial #{}.".format(1))


        # if    len(answ) != readbytes                                    \
        #    or answ == [128, 6, 4, 128, 6, 4, 128, 6, 4]                 \
        #    or answ == [255, 255, 255, 255, 255, 255, 255, 255, 255]:
        #     edprint(defname + "Failure reading Serial Number, reponse: ", answ)
        #     return g.NAN

        # check for correct crc
        words = 3
        if getCRC8((answ[0], answ[1])) == answ[2]:   words -= 1
        if getCRC8((answ[3], answ[4])) == answ[5]:   words -= 1
        if getCRC8((answ[6], answ[7])) == answ[8]:   words -= 1
        if words > 0:
            if getCRC8((answ[0], answ[1])) == answ[2]:   gdprint(defname + "Word0 has correct crc8")
            else:                                        edprint(defname + "Word0 has WRONG crc8")
            if getCRC8((answ[3], answ[4])) == answ[5]:   gdprint(defname + "Word1 has correct crc8")
            else:                                        edprint(defname + "Word1 has WRONG crc8")
            if getCRC8((answ[6], answ[7])) == answ[8]:   gdprint(defname + "Word2 has correct crc8")
            else:                                        edprint(defname + "Word2 has WRONG crc8")

        # answ = [0xf8, 0x96, 0x31, 0x9f, 0x07, 0xc2, 0x3b, 0xbe, 0x89] # example serial number
        # answ = [13, 65, 205, 191, 7, 30, 59, 79, 58]                  # my serial number
        word0 = answ[0] << 8 | answ[1]
        word1 = answ[3] << 8 | answ[4]
        word2 = answ[6] << 8 | answ[7]
        serialno = word0 << 32 | word1 << 16 | word2

        gdprint(defname + " "*68 + "SerNo: {:n}".format(serialno) )

        return serialno



    def SCD41StartPeriodicMeasurement(self):
        """needs to be done only once"""

        # 3.5.1 start_periodic_measurement
        # signal update interval is 5 seconds.
        # write 0x21b1
        # response: None

        defname = "SCD41StartPeriodicMeasurement: "

        tmsg      = "StartMeas"
        register  = 0x21b1
        readbytes = 0
        data      = []
        # wrt       = g.I2CDongle.DongleWriteReg(self.addr, register, readbytes, data, addrScheme=2, msg=tmsg)

        try:
            wrt = g.I2Chandle.write_i2c_block_data(self.addr, register, data)
        except Exception as e:
            exceptPrint(e, defname)


        return wrt


    def getValSCD41(self):
        """Read the CO2, Temp and Humid values if available"""

        # any result only after 5 sec after start and after EACH reading;
        # from Data sheet: "... the buffer is emptied upon read-out."

        # 3.5.2 read_measurement
        # write 0xec05
        # read 9 bytes
        # Example: read sensor output (500 ppm, 25 °C, 37 % RH)
        #          Response: 0x01f4 0x7b 0x6667 0xa2 0x5eb9 0x3c
        #
        # CO2 [ppm] = word[0]
        # T   [°C]  = word[1] / 2^16 * 175 - 45
        # RH  [%]   = word[2] / 2^16 * 100

        # measurement duration:
        #   with dongle ISS:  SCD41: CO2:829.000, Temp:24.182, Humid:32.088  duration:  4.3 ...  5.5 ms (avg: 4.8 ms)  1.0x
        #   with dongle ELV:  SCD41: CO2:922.000, Temp:24.524, Humid:31.822  duration: 11.7 ... 24.7 ms (avg:13.1 ms)  2,7x
        #   with dongle IOW:  SCD41: CO2:837.000, Temp:26.841, Humid:30.222  duration: 39.2 ... 40.4 ms (avg:39.9 ms)  8.3x
        #   with dongle FTD:  SCD41: CO2:837.000, Temp:26.841, Humid:30.222  duration: 65.8 ... 70.1 ms (avg:67.1 ms) 14.0x

        #   with dongle ISS:  100 kHz    SCD41:  duration:  4.3 ...  5.5 ms (avg: 4.8 ms)  1.0x
        #   with dongle ISS:  400 kHz    SCD41:  duration:  3.0 ...  5.9 ms (avg: 3.5 ms) 0.73x      1.37x

        # @ 9600 baud
        #   with dongle ISS:  100 kHz    SCD41:  duration:  4.5 ...  6.1 ms (avg: 5.2 ms)
        #   with dongle ISS:  400 kHz    SCD41:  duration:  2.9 ...  4.7 ms (avg: 3.3 ms)
        #   with dongle ISS: 1000 kHz    SCD41:  duration:  2.6 ...  5.0 ms (avg: 3.4 ms)  # slower!



        start   = time.time()
        defname = "getValSCD41: "
        sgvdata = (g.NAN,) * 3

        cdprint(defname)
        setIndent(1)

        dataReady = self.SCD41DataReady()
        # ################ test
        # dataReady = 1
        # ##########################

        if dataReady != 1:
            # data are NOT ready or failure to get ready status or not exactly 3 values received
            # debug print output already given in SCD41DataReady function
            pass

        else:
            # data are ready: dataReady == 1
            tmsg      = "getval"
            register  = 0xec05
            readbytes = 9
            data      = []
            answ      = g.I2CDongle.DongleWriteRead (self.addr, register, readbytes, data, addrScheme=2, msg=tmsg)

            try:
                answ = g.I2Chandle.read_i2c_block_data(self.addr, register, readbytes)
            except Exception as e:
                exceptPrint(e, defname + "{}  FAILURE I2C read: addr:{:#04x}, reg:{:#04x}, rbytes:{}".format("SCD41", self.addr, register, readbytes))
                answ = b"Fail"


            duration  = (time.time() - start) * 1000

            if len(answ) == readbytes:
                if set([0x80, 0x06, 0x04]).issubset(answ):  # check if 80 06 04 is in answ (Indicates wrong data)
                    msg = TYELLOW + defname + "Wrong data: ", answ

                else:
                    # data look ok
                    word0 = answ[0] << 8 | answ[1]  # answ[2] is CRC
                    word1 = answ[3] << 8 | answ[4]  # answ[5] is CRC
                    word2 = answ[6] << 8 | answ[7]  # answ[8] is CRC

                    p16     = 2 ** 16
                    co2     = word0
                    temp    = word1 / p16 * 175 - 45
                    humid   = word2 / p16 * 100
                    sgvdata = (co2, temp, humid)

                    msg = TGREEN + defname + "CO2:{:6.3f}, Temp:{:6.3f}, Humid:{:6.3f}  dur:{:0.2f} ms".format(*sgvdata, duration)
            else:
                msg = TYELLOW + defname + "Failure reading proper byte count"

            gdprint(msg)

        setIndent(0)

### testing
        # return sgvdata
        return sgvdata[0]
###



    def SCD41DataReady(self):
        """get the data-ready status of sensor;
        return: 1 True      Data are ready
                0 False     Data are NOT ready
                -1          Improper response
        """

        # 3.8.2 get_data_ready_status
        # write: 0xe4b8
        # Wait 1 ms
        # read:  3 bytes
        # If the least significant 11 bits of word[0] are 0 → data not ready
        # else → data ready for read-out
        # response should  be an 0x8XXX value

        start   = time.time()
        defname = "SCD41DataReady: "

        ready     = -1      # code for failure
        tmsg      = "Ready?"
        register  = 0xe4b8
        readbytes = 3
        data      = []
        wait      = 0.001       # Required wait 1 ms

        try:
            wrt = g.I2Chandle.write_i2c_block_data(self.addr, register, data)
        except Exception as e:
            exceptPrint(e, defname)

        time.sleep(0.1)

        try:
            answ = g.I2Chandle.read_i2c_block_data(self.addr, register, readbytes)
        except Exception as e:
            exceptPrint(e, defname + "{}  FAILURE I2C READ: addr:{:#04x}, reg:{:#04x}, rbytes:{}".format("SCD41", self.addr, register, readbytes))
            answ = b"Fail"


        duration = (time.time() - start) * 1000

        if len(answ) == readbytes:
            word0 = answ[0] << 8 | answ[1]
            if (word0 & 0x7FF) != 0:
                # Data are ready
                ready = True
                msg   = "41  Data ready"
                color = BOLDGREEN
            else:
                # Data are NOT ready
                ready = False
                msg   = "41  Data NOT ready"
                color = BOLDRED

            msg = defname + " "*70 + "{}{}".format(color, msg)

        elif len(answ) == 0:
            msg = BOLDRED + "41  No data returned: answ= '{}'".format(answ)

        else:
            msg = BOLDRED + "41  Improper data returned: answ= '{}'".format(answ)

        cdprint(msg + "  {:0.1f} ms".format(duration))

        return ready


    def SCD41getFirmwareVersion(self):
        """get the Firmware Version as Major.Minor"""

        # 1.4.9 Read firmware version
        # Command:  0xD100 , no argument needed
        # Wait None in datasheet Version 1.0 – D1 – May 2020
        # response: 3 bytes (2 b firmware + 1 bcrc) Firmware version: Major.Minor: 0x03, 0x42 => 3.66 (3.66 is also found on my chip)

        # Duration:
        # ISS: SCD30getFirmwareVersion: duration: 1.6 ms

        start = time.time()
        defname = "SCD41getFirmwareVersion: "

        tmsg      = "FirmWr"
        register  = 0xD100
        readbytes = 3
        data      = []
        wait      = 0
        # answ      = g.I2CDongle.DongleWriteRead (self.addr, register, readbytes, data, addrScheme=3, msg=tmsg, wait=wait)

        g.I2Chandle.write_i2c_block_data(self.addr, register, data)
        time.sleep(0.3)
        try:
            answ = g.I2Chandle.read_i2c_block_data(self.addr, register, readbytes)
            rdprint(defname, "ansW: ", answ)
        except Exception as e:
            exceptPrint(e, defname + "{}  FAILURE I2C read: addr:{}, reg:{}, rbytes:{}".
                            format("SCD41", hex(self.addr), hex(register), readbytes))
            answ = b"Fail"
            edprint(defname + "Fail in trial #{}, trying again.".format(1))


        if len(answ) != readbytes:
            edprint(defname + "Failure reading Serial Number, reponse: ", answ)
            return "Not Found"

        self.firmware = "{}.{}".format(answ[0], answ[1])

        duration = (time.time() - start) * 1000
        msg = defname + "got firmware:{}  in:{:0.1f} ms".format(self.firmware, duration)

        return msg
