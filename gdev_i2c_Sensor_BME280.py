#! /usr/bin/env python3
# -*- coding: UTF-8 -*-

"""
I2C module BME280
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

"""
Barometric pressure: (use for altitude correction)
Sea level standard pressure:  1013.25 hPa
Barometric formula: p = p0 * exp(- H / H0), with H0 =7990m
p @ Altitude 85m:  p= 1013.25 * exp(-85/7990) = 1013.25 * 0,98942  = 1002,53

Info on Sensor Module Bluedot:
https://www.bluedot.space/bme280-tsl2591/
Vendor Reference: BME280 + TSL2591, ASIN: B0795WWXX8
"Please note that the BME280 is hardwired to use the I2C Address 0x77. The
alternative Address (0x76) is not available! "
"""

class SensorBME280:
    """Code for the BME280 sensors"""

# =============================================================================
# comparison of results obtained with the different dongles
# all calibration points agree


# Calibration Data for the BlueDot module BME280 + TSL2591
# validation: data identical between the 2 dongles
#
# via ELV dongle
# ELV BME280 TX 11:04:16   [   ] [ 17]  get cal1             == b'S EE 88 S EF 18 P'
# ELV        RX 11:04:16   [ 24] [ 72]                       == b'BE 6E 9A 69 32 00 77 92 CE D6 D0 0B 00 22 A4 FF F9 FF AC 26 0A D8 BD 10 '
# ELV BME280 TX 11:04:16   [   ] [ 17]  get cal2             == b'S EE A1 S EF 01 P'
# ELV        RX 11:04:16   [  1] [  3]                       == b'4B '
# ELV BME280 TX 11:04:16   [   ] [ 17]  get cal3             == b'S EE E1 S EF 07 P'
# ELV        RX 11:04:16   [  7] [ 21]                       == b'6B 01 00 13 2D 03 1E '

# via IOW dongle
# IOW BME280 TX 11:57:37   [  2] [  8]  get cal1             == 02 C2 EE 88 00 00 00 00
# IOW BME280 RX 11:57:37   [ 24] [  8]                       == 02 02 00 00 00 00 00 00 ACK
# IOW BME280 tx 11:57:37   [ 24] [  8]                       == 03 18 EF 00 00 00 00 00
# IOW BME280 RX 11:57:37   [ 24] [  8]                       == 03 06 BE 6E 9A 69 32 00 ok, Bytes received: 6
# IOW BME280 RX 11:57:37   [ 24] [  8]                       == 03 06 77 92 CE D6 D0 0B ok, Bytes received: 12
# IOW BME280 RX 11:57:37   [ 24] [  8]                       == 03 06 00 22 A4 FF F9 FF ok, Bytes received: 18
# IOW BME280 RX 11:57:37   [ 24] [  8]                       == 03 06 AC 26 0A D8 BD 10 ok, Bytes received: 24
# IOW BME280 RX 11:57:37   [ 24] [ 24]      Final            == BE 6E 9A 69 32 00 77 92 CE D6 D0 0B 00 22 A4 FF F9 FF AC 26 0A D8 BD 10
# IOW BME280 TX 11:57:37   [  2] [  8]  get cal2             == 02 C2 EE A1 00 00 00 00
# IOW BME280 RX 11:57:37   [  1] [  8]                       == 02 02 00 00 00 00 00 00 ACK
# IOW BME280 tx 11:57:37   [  1] [  8]                       == 03 01 EF 00 00 00 00 00
# IOW BME280 RX 11:57:37   [  1] [  8]                       == 03 01 4B 00 00 00 00 00 ok, Bytes received: 6
# IOW BME280 RX 11:57:37   [  1] [  1]      Final            == 4B
# IOW BME280 TX 11:57:37   [  2] [  8]  get cal3             == 02 C2 EE E1 00 00 00 00
# IOW BME280 RX 11:57:37   [  7] [  8]                       == 02 02 00 00 00 00 00 00 ACK
# IOW BME280 tx 11:57:37   [  7] [  8]                       == 03 07 EF 00 00 00 00 00
# IOW BME280 RX 11:57:37   [  7] [  8]                       == 03 06 6B 01 00 13 2D 03 ok, Bytes received: 6
# IOW BME280 RX 11:57:37   [  7] [  8]                       == 03 01 1E 01 00 13 2D 03 ok, Bytes received: 12
# IOW BME280 RX 11:57:37   [  7] [  7]      Final            == 6B 01 00 13 2D 03 1E

# ISS BME280  i1 14:40:32   [ 24] [  4]  get cal1            == b'U\xef\x88\x18'           == 55 EF 88 18
# ISS         RX 14:40:32   [ 24] [ 24]                      == b'\xben\x9ai2\x00w\x92\xce\xd6\xd0\x0b\x00"\xa4\xff\xf9\xff\xac&\n\xd8\xbd\x10'
#                                                                                          == BE 6E 9A 69 32 00 77 92 CE D6 D0 0B 00 22 A4 FF F9 FF AC 26 0A D8 BD 10
# ISS BME280  i1 14:40:32   [  1] [  4]  get cal2            == b'U\xef\xa1\x01'           == 55 EF A1 01
# ISS         RX 14:40:32   [  1] [  1]                      == b'K'                       == 4B
# ISS BME280  i1 14:40:32   [  7] [  4]  get cal3            == b'U\xef\xe1\x07'           == 55 EF E1 07
# ISS         RX 14:40:32   [  7] [  7]                      == b'k\x01\x00\x13-\x03\x1e'  == 6B 01 00 13 2D 03 1E

# =============================================================================
# Calling problems with ISS dongle due to non-standard way of reading from device
# preparations

#activating BME280 on ELVdongle +++++++++++++++++++++++++++++++++++++++++++
#ELV BME280  TX 14:12:42   [  9] [  9]  get ID               == b'S EE D0 P'
#ELV         iR 14:12:42   [  9] [  9]                       == b'S EF 01 P'
#ELV BME280  RX 14:12:42   [  1] [  3]                       == b'60 '
#                                                            Found Sensor BME280

#activating BME280 on IOW24-DG +++++++++++++++++++++++++++++++++++++++++++
#IOW BME280  TX 14:04:43   [  2] [  8]  get ID               == 02 C2 EE D0 00 00 00 00
#IOW         RX 14:04:43   [  1] [  8]                       == 02 02 00 00 00 00 00 00 ACK
#IOW         iR 14:04:43   [  1] [  8]                       == 03 01 EF 00 00 00 00 00
#IOW         RX 14:04:43   [  1] [  8]                       == 03 01 60 00 00 00 00 00 ok, Bytes received: 6
#                                                   Answer:  == 60
#                                                            Found Sensor BME280

#activating BME280 on ISSdongle +++++++++++++++++++++++++++++++++++++++++++
# the I2C official way, NOT working !!!
#ISS BME280  TX 15:01:05   [  3] [  3]  get ID               == b'U\xee\xd0'     == 55 EE D0    # send 2 bytes, addr ee + D0
#ISS         iR 15:01:05   [  1] [  3]                       == b'U\xef\x01'     == 55 EF 01    # prep for reading 1 byte from addr EF
#ISS         RX 15:01:06   [  1] [  0]                       == b'' ==                          # Failure, no bytes returned
#
# with ISS specific workaraound
#ISS BME280  TX 14:15:07   [  3] [  3]  get ID               == b'U\xee\xd0'     == 55 EE D0    # send 2 bytes, addr ee + D0
#ISS BME280  i1 14:15:07   [  1] [  4]  get ID               == b'U\xef\xd0\x01' == 55 EF D0 01 # prep for reading 1 byte from addr EF, but RESEND the register D0
#ISS         RX 14:15:07   [  1] [  1]                       == b'`' == 60                      # success
#                                                            Found Sensor BME280

# when not one but two registered need to be addressed, the ELV and IOW work unmodifyied
# but the ISS requires that a different command be used (56 instead of 55)!
# the ISS has no option for 3 byte commands, while the ELV and IOW would work unmodified
# using ELV dongle
#ELV BME280  TX 10:24:11   [ 12] [ 12]  ctrl_meas            == b'S EE F4 D6 P'                         # send 3 bytes, addr ee + F4 D6
#ELV         iR 10:24:11   [  9] [  9]                       == b'S EF 01 P'                            # prep for reading 1 byte from addr EF
#ELV         RX 10:24:11   [  1] [  3]                       == b'D6 '                                  # success

# using ISS dongle
#ISS BME280  TX 10:31:53   [  4] [  4]  ctrl_meas            == b'U\xee\xf4\xd6'     == 55 EE F4 D6     # send 3 bytes, addr ee + F4 D6
#ISS         iR 10:31:53   [  1] [  3]                       == b'U\xef\x01'         == 55 EF 01        # prep for reading 1 byte from addr EF
#ISS         RX 10:31:53   [  1] [  0]                       == b''                  ==                 # Failure, no bytes returned

#ISS BME280  TX 10:27:16   [  4] [  4]  ctrl_meas            == b'U\xee\xf4\xd6'     == 55 EE F4 D6     # send 3 bytes, addr ee + F4 D6
#ISS         ii 10:27:16   [  1] [  5]                       == b'U\xef\xf4\xd6\x01' == 55 EF F4 D6 01  # prep for reading 1 byte from addr EF, resending F4 D6
#ISS         RX 10:27:16   [  1] [  0]                       == b''                  ==                 # Failure, no bytes returned

#ISS BME280  TX 10:47:54   [  4] [  4]  ctrl_meas            == b'U\xee\xf4\xd6'     == 55 EE F4 D6     # send 3 bytes, addr ee + F4 D6
#ISS         ii 10:47:54   [  1] [  5]                       == b'V\xef\xf4\xd6\x01' == 56 EF F4 D6 01  # using CMD=56 (not 55): prep for reading 1 byte from addr EF, resending F4 D6
#ISS         RX 10:47:54   [  1] [  1]                       == b'\xd6'              == D6              # success


    def __init__(self, bme280):
        self.dongle  = bme280["dngl"]    # "ELVdongle", "IOW24-DG", "ISSdongle"
        self.addr    = bme280["addr"]    # 0x76, 0x77
        self.subtype = bme280["type"]    # chip_ID: 0x60
        self.name    = bme280["name"]    # BME280


    def BME280Init(self):
        """Reset, check ID, set reg hum, get calibration, trigger measurement"""

        # soft reset
        data    = [0xE0, 0xB6]
        rbytes  = 0
        answ =        gglobs.elv.ELVaskDongle(self.addr, data, rbytes, name=self.name, info="Soft Reset")

        # check ID
        data    = [0xD0]
        rbytes  = 1
        answ =        gglobs.elv.ELVaskDongle(self.addr, data, rbytes, name=self.name, info="get ID")
        if answ[0] == self.subtype:
            #fprint("Success - Found Sensor BME280")
            pass
        else:
            #~efprint("Failure - Did NOT find Sensor BME280")
            #~return False
            response = "Failure - Did NOT find Sensor BME280"
            return response

        # set ctrl-hum
        # 101 = 5 = oversampling * 16
        data    = [0xf2, 0x05]
        rbytes  = 1
        answ =        gglobs.elv.ELVaskDongle(self.addr, data, rbytes, name=self.name, info="ctrl_hum")

        # Calibration Data calib00...calib25 (0x88 ... 0x9F) 24 values
        data    = [0x88]
        rbytes  = 24
        self.cal1 =        gglobs.elv.ELVaskDongle(self.addr, data, rbytes, name=self.name, info="get cal1")

        # Calibration Data calib26...calib41 (0xA1 ) 1 value
        data    = [0xA1]
        rbytes  = 1
        self.cal2 =        gglobs.elv.ELVaskDongle(self.addr, data, rbytes, name=self.name, info="get cal2")

        # Calibration Data calib26...calib41 (0xe1 ... 0xe7) 7 values
        data    = [0xe1]
        rbytes  = 7
        self.cal3 =        gglobs.elv.ELVaskDongle(self.addr, data, rbytes, name=self.name, info="get cal3")

        # make one measurement to discard (on ISS dongle sometimes measuremnt was wrong)
        self.BME280getTPH()

        #~return True
        return ""


    def BME280getTPH(self):
        """ get one measurement of T, P, H """

        # trigger measurement with: ctrl_meas
        # makes one measurement, then waits for next trigger due to forced mode
        # 0b 101 101 10  = D6 = P oversampling * 16, T oversampling * 16,  forced mode
        data    = [0xf4, 0xd6]
        rbytes  = 1
        answ =        gglobs.elv.ELVaskDongle(self.addr, data, rbytes, name=self.name, info="ctrl_meas")
        #time.sleep(0.05) # appears to be insufficient, occasional faulty result, though it should be plenty:
        #                   BOSCH: t measure,max = 1.25 + [2.3 ⋅ 1] + [2.3 ⋅ 4 + 0.575] + [0] = 13.325 ms
        time.sleep(0.1)

        data    = [0xf7]
        rbytes  = 8
        answ =        gglobs.elv.ELVaskDongle(self.addr, data, rbytes, name=self.name, info="Get data F7...FE", end="")
        #print("BME280getTPH: answ:", answ)

        t_raw, p_raw, h_raw = self.__BME280getRawData(answ)
        t, p, h             = readBME280All(self.cal1, self.cal2, self.cal3, p_raw, t_raw, h_raw)
        wprint("Final Result:  T: {:6.2f}, P: {:6.2f}, H: {:6.2f}".format(t, p, h)) # geht sowieso ins logprint!

        return ("BME280", t, p, h)


    def __BME280getRawData(self, rec):
        """calcs raw press, temp, hum"""

        msb, lsb, xlsb  = rec[0], rec[1], rec[2]
        press           = (msb << 16 | lsb << 8 | xlsb) >> 4

        msb, lsb, xlsb  = rec[3], rec[4], rec[5]
        temp            = (msb << 16 | lsb << 8 | xlsb) >> 4

        msb, lsb        = rec[6], rec[7]
        hum             = (msb <<  8 | lsb )

        return temp, press, hum


    def BME280Reset(self):
        """Soft Reset the BME280 sensor"""

        # 5.4.2 Register 0xE0 “reset”
        # If the value 0xB6 is written to the register, the device is reset
        # using the complete power-on-reset procedure. Writing other values
        # than 0xB6 has no effect. The readout value is always 0x00.
        data    = [0xE0, 0xB6]
        rbytes  = 1
        answ =         gglobs.elv.ELVaskDongle(self.addr, data, rbytes, name=self.name, info="Soft Reset")

        # set ctrl-hum
        # 101 = 5 = oversampling * 16
        data    = [0xf2, 0x05]
        rbytes  = 1
        answ =        gglobs.elv.ELVaskDongle(self.addr, data, rbytes, name=self.name, info="ctrl_hum")



    def BME280getInfo(self):

        info = """{} (Category: {})
- DeviceID:   0x{:02X}
- Address:    0x{:02X}
""".format(self.name, "Temperature, Pressure, Humidity", self.subtype, self.addr)

        return info.split("\n")



    def BME280runAllFunctions(self):
        """ for BME280 sensor """

        # not running until the "answ    = util.askDongle(..." are exchanged for
        #                      " answ    = gglobs.elv.ELVaskDongle(..."
        return

        # Reference Document: "TSL2591 Datasheet - Apr. 2013 - ams163.5"
        # e.g.: https://www.manualshelf.com/manual/adafruit/1980/datasheet-english.html

        # 5.4.1 Register 0xD0 “id”
        # The “id” register contains the chip identification number
        # chip_id[7:0], which is 0x60. This number can be read as soon as the
        # device finished the power-on-reset.
        data    = [0xD0]
        rbytes  = 1
        answ    = util.askDongle(self.dongle, self.addr, data, rbytes, name=self.name, info="get ID")

        # 5.4.2 Register 0xE0 “reset”
        # If the value 0xB6 is written to the register, the device is reset
        # using the complete power-on-reset procedure. Writing other values
        # than 0xB6 has no effect. The readout value is always 0x00.
        data    = [0xE0, 0xB6]
        rbytes  = 1
        answ    = util.askDongle(self.dongle, self.addr, data, rbytes, name=self.name, info="Soft Reset")

        # 5.4.3 Register 0xF2 “ctrl_hum”
        # The “ctrl_hum” register sets the humidity data acquisition options of the device. Changes to this
        # register only become effective after a write operation to “ctrl_meas”.
        # 101 = 5 = oversampling * 16
        data    = [0xf2, 0x05]
        rbytes  = 1
        answ    = util.askDongle(self.dongle, self.addr, data, rbytes, name=self.name, info="ctrl_hum")

        # 5.4.4 Register 0xF3 “status”
        # The “status” register contains two bits which indicate the status of the device.
        # Bit 0 and Bit 3 (when set, something is ongoing
        data    = [0xf3]
        rbytes  = 1
        answ    = util.askDongle(self.dongle, self.addr, data, rbytes, name=self.name, info="status")

        # 5.4.5 Register 0xF4 “ctrl_meas”
        # The “ctrl_meas” register sets the pressure and temperature data acquisition options of the device.
        # The register needs to be written after changing “ctrl_hum” for the changes to become effective.
        # for read out only:
        data    = [0xf4]
        rbytes  = 1
        answ    = util.askDongle(self.dongle, self.addr, data, rbytes, name=self.name, info="ctrl_meas")

        # for write new value:
        # 0b 101 101 10  = D6 = P oversampling * 16, T oversampling * 16,  forced mode
        data    = [0xf4, 0xd6]
        rbytes  = 1
        answ    = util.askDongle(self.dongle, self.addr, data, rbytes, name=self.name, info="ctrl_meas")
        time.sleep(0.1) # wait for measurement complete (never saw a status bit set even w/o sleep)

        # 5.4.6 Register 0xF5 “config”
        # The “config” register sets the rate, filter and interface options of the device. Writes to the “config”
        # register in normal mode may be ignored. In sleep mode writes are not ignored.
        data    = [0xf5]
        rbytes  = 1
        answ    = util.askDongle(self.dongle, self.addr, data, rbytes, name=self.name, info="get config")

        # Read calibration data
        # Calibration Data calib00...calib25 (0x88 ... 0x9F) 24 values
        data    = [0x88]
        rbytes  = 24
        self.cal1    = util.askDongle(self.dongle, self.addr, data, rbytes, name=self.name, info="get cal1")

        # Calibration Data calib26...calib41 (0xA1 ) 1 value
        data    = [0xA1]
        rbytes  = 1
        self.cal2    = util.askDongle(self.dongle, self.addr, data, rbytes, name=self.name, info="get cal2")

        # Calibration Data calib26...calib41 (0xe1 ... 0xe7) 7 values
        data    = [0xe1]
        rbytes  = 7
        self.cal3    = util.askDongle(self.dongle, self.addr, data, rbytes, name=self.name, info="get cal3")


        # when cycling:

        # Since forced mode was chosen, a cycle must begin with ctrl_meas.
        # Must be written to; reading not sufficient
        # 0b 101 101 10  = D6 = P oversampling * 16, T oversampling * 16,  forced mode
        # ctrl_hum is at oversampling * 16 also
        data    = [0xf4, 0xd6]
        rbytes  = 1
        answ    = util.askDongle(self.dongle, self.addr, data, rbytes, name=self.name, info="ctrl_meas")

        # wait until measurement complete
        time.sleep(0.05)

        # get all 8 bytes for T, P, H from F7 onwards
        data    = [0xf7]
        rbytes  = 8
        answ    = util.askDongle(self.dongle, self.addr, data, rbytes, name=self.name, info="data F7...FE")

#--------------------------------------
# code adapted from file bme280.py
# Author : Matt Hawkins
# Date     : 25/07/2016
# http://www.raspberrypi-spy.co.uk/
#--------------------------------------

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
    if humidity > 100:
        humidity = 100
    elif humidity < 0:
        humidity = 0

    return temperature/100, pressure/100, humidity
