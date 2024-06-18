#!/usr/bin/python3
# -*- coding: UTF-8 -*-

"""
I2C sensor module BMM150 - Geomagnetic Sensor
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

from gsup_utils   import *

# manual:               BOSCH - bst-bmm150-ds001.pdf
# max I2C frequency:    400 kHz
# pip module bmm150:    https://bmm150.readthedocs.io/en/latest/


class SensorBMM150:
    """Code for the BMM150 sensors"""

    addr    = 0x13              # addr options: 0x10 | 0x11 | 0x12 | 0x13
    id      = 0x32
    name    = "BMM150"
    handle  = g.I2CDongle       # default for use by 'I2C' device; RaspiI2C defines its own


    def __init__(self, addr, I2Chandle=None):
        """Init SensorBMM150 class"""

        self.addr    = addr
        if I2Chandle is not None: self.handle = I2Chandle


    def SensorInit(self):
        """Check for presence of sensor"""

        defname = "SensorInit: " + self.name + ": "
        # dprint(defname)
        setIndent(1)
        success = False

        # check for presence of an I2C device at I2C address
        if self.handle.DongleIsSensorPresent(self.addr):
            # sensor device found
            gdprint(defname, "Found an I2C device at address 0x{:02X}".format(self.addr))
        else:
            # no device found
            setIndent(0)
            return  False, "Did not find any I2C device at address 0x{:02X}".format(self.addr)

        try:
            import bmm150
            g.RaspiI2CBMM150_device = bmm150.BMM150()
        except Exception as e:
            exceptPrint(e, "Failure at importing module 'bmm150'")
            dmsg     = "Found sensor but cannot import 'bmm150'."
            dmsg += "\nRedo the GeigerLog setup."
            return  False, dmsg
        else:
            success = True
            g.versions["bmm150"] = bmm150.__version__
            cdprint(defname, "Python module 'bmm150' has version: ", g.versions["bmm150"])


        ## check ID of sensor
        ## Chip ID = 0x32 from register 0x40 (can only be read if power control bit ="1")
        tmsg      = "checkID"
        register  = 0x40
        readbytes = 1
        data      = []
        answ      = self.handle.DongleWriteRead (self.addr, register, readbytes, data, addrScheme=1, msg=tmsg)
        if (len(answ) == readbytes and answ[0] == self.id):
            dmsg     = "sensor {:8s} at address 0x{:02X} with ID 0x{:02x}".format(self.name, self.addr, self.id)
            gdprint(defname, "Sensor has expected ID: 0x{:02X}".format(self.id))
        else:
            setIndent(0)
            dmsg = "Failure - Did find sensor, but ID: '{}' is not as expected: 0x{:02X}".format(answ, self.id)
            rdprint(defname, dmsg, "   Continuing anyway")

        # Sensor Reset
        gdprint(defname, self.SensorReset())

        setIndent(0)

        return (success, dmsg)


    def SensorgetValues(self):
        """get all 4 values X, Y, Z, heading"""

        start     = time.time()
        defname   = "SensorgetValues: {:10s}: ".format(self.name)
        # dprint(defname)
        setIndent(1)

        x, y, z   = g.RaspiI2CBMM150_device.read_mag_data()
        vec       = np.array([x, y, z])
        magnitude = np.sqrt(np.dot(vec, vec))
        heading   = np.degrees(np.arctan2(x, y))                 # in DEGrees
        # headingR  = np.degrees(np.arctan2(y, x))                 # reversed; any relevance???

        duration = (time.time() - start) * 1000
        # gdprint(defname, "X:{:<6.3f} µT  Y:{:<6.3f} µT  Z:{:<6.3f} µT  Magnitude:{:<6.3f} µT Heading: {:0.3f} DEG  HeadingR: {:0.3f} DEG  dur:{:<0.1f} ms  ".\
        #                   format(x, y, z, magnitude, heading, headingR, duration))
        gdprint(defname, "X:{:<6.3f} µT  Y:{:<6.3f} µT  Z:{:<6.3f} µT  Magnitude:{:<6.3f} µT Heading: {:0.3f} DEG  dur:{:<0.1f} ms  ".\
                          format(x, y, z, magnitude, heading, duration))
        # Example printout:
        # SensorgetValues: BMM150    : X:36.325 µT  Y:0.000  µT  Z:48.786 µT  Magnitude:60.825 µT Heading: 86.349 DEG  dur:1.2 ms

        setIndent(0)

        return (x, y, z, magnitude, heading)


    def SensorGetInfo(self):
        """BMM150 details"""

        info  = "{}\n"                             .format("Geomagnetic X, Y, Z, Heading")
        info += "- Address:         0x{:02X}\n"    .format(self.addr)
        info += "- ID:              0x{:02X}\n"    .format(self.id)
        info += "- Variables:       {}\n"          .format(", ".join("{}".format(x) for x in g.Sensors["BMM150"][5]))

        return info.split("\n")


    def SensorReset(self):
        """Reset BMM150 sensor - option does not exist"""

        defname = "SensorReset: "

        return defname + "(dummy reset)"


    def BMM150runAllFunctions(self):
        """ for BMM150 sensor """

        gdprint("BMM150runAllFunctions - nothing defined")


