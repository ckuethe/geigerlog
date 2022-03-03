#! /usr/bin/env python3
# -*- coding: UTF-8 -*-

"""
ELV USB-I2C Dongle
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
__copyright__       = "Copyright 2016, 2017, 2018, 2019, 2020, 2021, 2022"
__credits__         = [""]
__license__         = "GPL3"


from   gsup_utils       import *


class ELVdongle:
    """Code for the ELV USB-I2C Dongle"""

    name            = "ELV USB-I2C"

    # Serial port
    DongleSer       = None                      # serial port pointer
    usbport         = gglobs.I2Cusbport
    baudrate        = gglobs.I2Cbaudrate
    timeout         = gglobs.I2Ctimeout
    timeout_write   = gglobs.I2Ctimeout_write


    def __init__(self):
        """make instance of dongle"""
        pass


    def DongleInit(self):
        """opening the serial port and testing for correct dongle"""

        fncname = "DongleInit: {}: ".format(self.name)

        dprint(fncname)
        setDebugIndent(1)

        # open serial port
        success, portmsg = self.ELVOpenPort()
        if not success:
            setDebugIndent(0)
            return success, portmsg

        # get info:
        #   - send b'?'
        #   - read ~179 bytes:
        #           b'\r\nELV USB-I2C-Interface v1.8 (Cal:5E)
        #             \r\nLast Adress:0xC5
        #             \r\nBaudrate:115200 bit/s
        #             \r\nI2C-Clock:99632 Hz
        #             \r\nY00
        #             \r\nY10
        #             \r\nY20
        #             \r\nY30
        #             \r\nY40
        #             \r\nY50
        #             \r\nY60
        #             \r\nY70
        #             \r\n'
        wrt  = self.ELVwriteBytes(b'?')     # request info
        rec  = self.ELVreadBytes(100)       # get info (~179 bytes, depending on some settings)
        rec  = rec.strip()
        if b"ELV USB-I2C" in rec:

            # # Reset Dongle
            # Factory Reset takes >3 sec
            # gdprint(fncname + "Factory-Reset dongle")
            # self.DongleReset(type="Factory")

            # set dongle defaults
            gdprint(fncname + "Setting dongle defaults")
            wrt = self.ELVwriteBytes(b'<')     # stop macro with '<' (Should be default)
            wrt = self.ELVwriteBytes(b'y30')   # set 'y30' in order to NOT get ACK and NACK (is default)

            msg = True,  "Initialized Dongle " + self.name            # an ELV dongle

        else:
            msg = False, "Failure - Not an {} dongle!\nat {}".format(self.name, portmsg)   # not an ELV dongle

        setDebugIndent(0)

        return msg


    def DongleTerminate(self):
        """Close the I2C serial port and set serial handle to None"""

        fncname = "DongleTerminate: "
        msg     = "Closing Serial Port of Dongle {}".format(self.name)
        try:
            gglobs.I2CDongle.DongleSer.close()
        except Exception as e:
            msg = "Exception " + msg
            exceptPrint(e, msg)

        gglobs.I2CDongle.DongleSer = None # will be renewed on next init

        return fncname + msg


    def DongleReset(self, type="Factory"):
        """Reset the ELV dongle"""

        # returns: Factory: b'\r\nFull Init...'   (14 bytes) # takes ~7.2 ms
        #          else:    b'\r\nReset...'       (10 bytes) # takes ~6.9 ms
        # HOWEVER: this is followed in both commands by:
        #                   b'\r\nELV USB-I2C-Interface v1.8 (Cal:5E)\r\n'
        # but it takes seconds before this second part is sent. If another
        # command is issued in that time, it interferes with that new command!
        # The total duration on my system is:
        #                   ZAA Factory Reset:  takes 3.25 sec
        #                   Z4B Reset:          takes 1.80 sec

        start   = time.time()
        fncname = "DongleReset: "
        gdprint(fncname + "type: ", type)

        if      type == "Factory": code = b"ZAA"    # 1.) Setzt alle Einstellungen auf den Auslieferungszustand zurück.
                                                    # 2.) Löscht den Makrospeicher.
                                                    # 3.) Führt einen Reset aus.
        else:                      code = b"Z4B"    # Führt sofort einen Reset aus (alle Einstellungen bleiben).

        wrt  = self.ELVwriteBytes(code)
        brec = self.ELVreadBytes(10)                # brec: b'\r\nELV USB-I2C-Interface v1.8 (Cal:5E)\r\n00 \r\n'

        time.sleep(1)                               # 1 sec wait allows both reset types to complete within 3 sec timeout

        while True and (time.time() - start) < 5:
            wbrec = self.ELVreadBytes(10)           # wbrec: b'\r\nELV USB-I2C-Interface v1.8 (Cal:5E)\r\n00 \r\n'
            # cdprint(fncname + "while loop, wbrec: ", wbrec)
            if b"ELV" in wbrec:
                brec += wbrec
                break

        # edprint(fncname + "total dur: {:0.1f} ms".format((time.time() - start)*1000))
        duration = 1000 * (time.time() - start)

        return str(brec) + "  Total dur: {:0.1f} ms".format(duration)


    def DongleGetInfo(self):
        """get the ELV's startup info"""

        wrt  = self.ELVwriteBytes(b'?')
        brec = self.ELVreadBytes(100)
        srec = (brec.strip().decode() + "\n\n").replace("\r", "")

        portmsg = "Port: {} Baud: {} TimeoutR: {}s TimeoutW: {}s".format(self.usbport, self.baudrate, self.timeout, self.timeout_write)

        info  = "- Connection:      {}\n"               .format(portmsg)
        info += srec

        return info.split("\n")


    def DongleScanPrep(self, type):
        """Only the ELV dongle needs this prep done before any scans!
        NOTE its use in gdev_i2c !
        type = "Start" or "END"
        """

        fncname = "DongleScanPrep: "

        if    type == "Start": code = b'y31'
        else:                  code = b'y30'
        wrt = self.ELVwriteBytes(code)


    def DongleIsSensorPresent(self, addr):
        """check a single address for presence of I2C device with address 'addr'"""
        # only ELV needs the DongleScanPrep!

        self.DongleScanPrep("Start")
        response = self.DongleAddrIsUsed(addr)
        self.DongleScanPrep("End")

        return response


    def DongleAddrIsUsed(self, addr):
        """Check for presence of I2C device with address 'addr'"""
        # use when checking multiple addr in a row
        # write Start-Addr-Stop and check for ACK or NACK

        # start = time.time()
        fncname = "DongleAddrIsUsed: "

        readbytes = 1
        saddr     = "{:02X}".format((addr << 1) + 0)                      # note: +0!
        bcommand  = bytes('S {} P'.format(saddr), 'ASCII')
        wrt       = self.ELVwriteBytes(bcommand)
        answ      = self.ELVreadBytes(readbytes)

        # duration2 = 1000 * (time.time() - start)
        # edprint(fncname + "dur chk: {:0.2f}".format(duration2))

        msg = fncname + "command: {:12s}  addr: 0x{:02X}  answ: {}".format(str(bcommand), addr, answ)
        if   answ == b"N":  # NACK
            rdprint(msg)
            return False

        elif answ == b"K":  # ACK
            cdprint(msg)
            return True

        else:               # crap
            playWav("err")
            edprint(fncname + "Wow this should not have happened! Please, try restarting GeigerLog")
            sys.exit(1)


    def DongleWriteRead(self, addr, register, readbytes, data, addrScheme=1, msg="", wait=0):
        """combines
        def DongleWriteReg(self, addr, register, readbytes, data, addrScheme=1, msg=""):
        def DongleGetData (self, addr, register, readbytes, data, addrScheme=1, msg=""):
        into one, with error checking after write
        wait it wait phase between write and read call
        """

        wrt       = self.DongleWriteReg(addr, register, readbytes, data, addrScheme=addrScheme, msg=msg)
        if wrt == -99:
            # failure in writing
            return []
        else:
            # get the data after a wait, and only if the Write succeeded
            time.sleep(wait)
            return self.DongleGetData (addr, register, readbytes, data, addrScheme=addrScheme, msg=msg)


    def DongleWriteReg(self, addr, register, readbytes, data, addrScheme=1, msg=""):
        """Writes to register of dongle, perhaps with data"""

        fncname = "   {:15s}: {:15s} ".format("DongleWriteReg", msg)
        # dprint(fncname)

        # write to register with data (if there are any)
        saddr       = "{:02X}".format((addr << 1) + 0)                      # NOTE: +0!
        sreg        = "{:02X}".format(register)
        if addrScheme == 1: sreg        = "{:02X}".format(register)
        else:               sreg        = "{:04X}".format(register)         # if reg is 0x0123 then the zero is not shown unless :04X is chosen!
        sdata       = "".join("%02X " % d for d in data)
        bcommand    = bytes('S {} {} {} P'.format(saddr, sreg, sdata), 'ASCII')
        wrt         = self.ELVwriteBytes(bcommand)

        cdprint(fncname + "wrt:{:2n}  {:45s} expect readbytes: {}".format(wrt, str(bcommand), readbytes))

        return wrt


    def DongleGetData(self, addr, register, readbytes, data, addrScheme=1, msg=""):
        """writes inits reading, then reads data
        return: list of int values
        """

        fncname = "   {:15s}: {:15s} ".format("DongleGetData", msg)
        # dprint(fncname)

        if readbytes == 0: return []

        # read init command (doesn't use register!)
        saddr       = "{:02X}".format((addr << 1) + 1)                      # read address, note: +1!
        sreadbytes  = "{:02X}".format(readbytes)                            # no of bytes to read
        bcommand    = bytes('S {} {} P'.format(saddr, sreadbytes), 'ASCII')
        wrt         = self.ELVwriteBytes(bcommand)

        # read bytes
        brec        = self.ELVreadBytes(readbytes)     # besser weniger als zuviel --- read byte sequence:  3 chars per byte('FF ') + 2 (CR + LF)
        srec        = brec.strip().decode()
        # cdprint(fncname + "wrt:{:2n}  {:45s} bexp:{:2n} brcvd:{:2n} srec: {}".format(wrt, str(brec), readbytes, len(brec), srec))

        # check for Err messages
        if  "Exception"         in srec or  \
            "Err"               in srec or  \
            "Buffer"            in srec or  \
            "Solve"             in srec or  \
            "USB-I2C-Interface" in srec:
            edprint(fncname + "ELV ERROR message in byterec: " + str(brec))
            return []

        else:
            # convert string to list of int values
            srecs = srec.split(" ")
            if len(srecs) == 0: lrec = []
            else:               lrec = [int(x, 16) for x in srec.split(" ")]
            cdprint(fncname + "wrt:{:2n}  {:45s} brcvd: {}".format(wrt, str(bcommand), brec))
            return lrec


    def ELVwriteBytes(self, writebytes, msg=""):
        """write to the ELV dongle"""

        fncname = "   {:15s}: {:15s} ".format("ELVwriteBytes", msg)

        # start = time.time()
        try:
            wrt  = gglobs.I2CDongle.DongleSer.write(writebytes)  # wrt  = no of bytes written
        except Exception as e:
            exceptPrint(e, fncname)
            wrt  = -99

        # duration = (time.time() - start ) * 1000
        # dprint(fncname + "wrt:{:2d}  {}, dur:{:0.3f} ms".format(wrt, writebytes, duration))

        return wrt


    def ELVreadBytes(self, bytecount, msg=""):
        """read from the dongle"""

        fncname = "   {:15s}: {:15s} ".format("ELVreadBytes", msg)

        # start = time.time()
        try:
            rec = gglobs.I2CDongle.DongleSer.read(bytecount)
            # dprint("ELVreadBytes:  bytecount: ", bytecount, ", rec: ", rec)

            while True:
                wcount = gglobs.I2CDongle.DongleSer.in_waiting
                # print("wcount: ", wcount, ", bytecount: ", bytecount)
                if wcount == 0: break
                rec += gglobs.I2CDongle.DongleSer.read(wcount)
                time.sleep(0.005)

        except Exception as e:
            exceptPrint(e, fncname)
            rec = "ELVreadBytes Exception Failure"

        # duration = (time.time() - start ) * 1000
        # dprint(fncname + "bytecount: {:2d}, rec:{}, dur:{:0.1f} ms".format(bytecount, rec, duration))

        return rec  # return bytes sequence


    # not used anywhere
    def ELVgetMacro(self):
        """ Print the Macrocode in the memory """

        wrt  = self.ELVwriteBytes(b'U')
        rec  = self.ELVreadBytes(255+26)

        return rec


    def ELVOpenPort(self):
        """open serial port for ELV dongle"""
        # on Linux this is a "/dev/ttyUSB*" port

        fncname = "ELVOpenPort: "

        if self.usbport == "auto":
            # in auto mode try to find port and baud
            port, baud = getSerialConfig("ELV")
            if port is None or baud is None:
                return (False,  "No such dongle detected")
            else:
                self.usbport  = port
                self.baudrate = baud
                fprint("A {} dongle was detected at port: {} and baudrate: {}".format(self.name, self.usbport, self.baudrate), debug=True)
        else:
            # in non-auto mode take the configured value for port and baud
            self.usbport  = gglobs.I2Cusbport
            self.baudrate = gglobs.I2Cbaudrate


        portmsg = "Port:{} Baud:{} TimeoutR:{}s TimeoutW:{}s".format(self.usbport, self.baudrate, self.timeout, self.timeout_write)
        try:
            gglobs.I2CDongle.DongleSer = serial.Serial(self.usbport, self.baudrate, timeout=self.timeout, write_timeout=self.timeout_write)
            gglobs.I2CDongle.DongleSer.flushInput() # helful?

            msg = "Serial device opened at {}".format(portmsg)
            gdprint(msg)
            return (True,  portmsg)
        except Exception as e:
            exceptPrint(e, fncname + "ERROR Serial port for dongle {} could not be opened".format(self.name))
            errmsg = "No such dongle detected at:\n{}".format(portmsg)
            return (False,  errmsg)

