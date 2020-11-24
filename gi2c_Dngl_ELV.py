#!/usr/bin/python3
# -*- coding: UTF-8 -*-

"""
Code for the ELV USB-I2C Dongle
(adapted from file: I2Cpytools_dgl_ELV.py)
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
__copyright__       = "Copyright 2016, 2017, 2018, 2019, 2020"
__credits__         = [""]
__license__         = "GPL3"

from   gutils       import *


class ELVdongle:
    """Code for the ELV USB-I2C Dongle"""

    #              ELV name    xX   time   reqB   wrt/rec   info     rec
    pTemplate   = "ELV {:7s} {:2s} {:10s} [{:3d}] [{:3d}]  {:20s} == {}"

    def __init__(self):
        """make instance of dongle"""

        self.name        = "ELVdongle"
        self.short       = "dongle"


    def ELVinit(self):
        """opening the serial port and testing for correct dongle"""

        # open serial port
        msg = "port: {} (baudrate:{}, timeout:{}s, timeout_write:{}s)"\
                  .format(gglobs.I2Cusbport, gglobs.I2Cbaudrate, gglobs.I2Ctimeout, gglobs.I2Ctimeout_write)
        try:
            gglobs.I2Cser = serial.Serial(gglobs.I2Cusbport, gglobs.I2Cbaudrate, timeout=gglobs.I2Ctimeout, write_timeout=gglobs.I2Ctimeout_write)
            dprint("ELV dongle opened at " + msg)
        except Exception as e:
            exceptPrint(e, sys.exc_info(), "ERROR Serial port for ELV dongle could not be opened")
            return False, msg

        # stop macro with '<' and set 'y30' in order to NOT get ACK and NACK
        # and then get info by '?', all in single command
        self.ELVwriteAdmin(b'<y30?', name=self.short, info="Init Dongle")
        rec = self.ELVreadAdmin(140, name=self.short, info="").strip()
        if rec.startswith(b"ELV"):
            return True, ""                        # ought to be an ELV dongle
        else:
            return False, "Not an ELV dongle!<br>at {}".format(msg) # not an ELV dongle


    def ELVreset(self):
        """Reset the ELV dongle (takes 2 sec!)"""

        #print("\n---- Reset")
        self.ELVwriteAdmin(b'z4b', name=self.short, info="Reset Dongle")
        time.sleep(2) # 1 sec is NOT enough
        rec = self.ELVreadAdmin(name=self.short, info="")
        #print(rec.decode("utf-8") )


    def ELVgetInfo(self):
        """Show the startup info"""

        self.ELVwriteAdmin(b'?', name=self.short, info="Show Info")
        rec = self.ELVreadAdmin(140, name=self.short, info="").strip()

        return rec.decode("utf-8").split("\r\n")


    def ELVgetMacro(self):
        """ Print the Macro in Memory """

        self.ELVwriteAdmin(b'U', name=self.short, info="Show Macrocode" )
        rec = self.ELVreadAdmin(255+26, name=self.short, info="")
        rd = (rec.decode("utf-8")).split("\r\n")

        return rec.decode("utf-8")


    def ELVwriteAdmin (self, command, name= "-", info = "no info"):
        """write to the ELV USB-I2C - only for its interal admin functions"""

        command = command.upper()
        wrt     = gglobs.I2Cser.write(command)  # wrt = no of bytes written
    #    print( self.pTemplate.format(name, "TA", stime()[11:], len(command), wrt, info, command))


    def ELVreadAdmin (self, length = 100, name = "-", info = "no info"):
        """read from the ELV USB-I2C - only for its internal admin functions"""

        rec = gglobs.I2Cser.read(length)
        cnt = gglobs.I2Cser.in_waiting
        if cnt > 0:
            print("ELVreadAdmin: Bytes waiting:", cnt)
            while True:            # read single byte until nothing is returned
                x = gglobs.I2Cser.read(1)
                if len(x) == 0: break
                rec += x
    #    print("ELVreadAdmin: len(rec), rec:", len(rec), rec)
        rec = rec.strip()
    #    print( self.pTemplate.format(name, "RA", stime()[11:], length, len(rec), info, rec))

        return rec


    def ELVaskDongle(self, addr, data, rbytes, name="no name", info="no info", doPrint=True, end="\n"):
        """ Function doc """

        doPrint = False

        self.ELVwriteData(addr, data, name=name, info=info, doPrint=doPrint)
        if rbytes > 0:
            self.ELVinitializeRead(addr, rbytes, name=name, doPrint=doPrint)
            answ = self.ELVreadData(length=rbytes, name=name, doPrint=doPrint)
            if doPrint: print(end=end)
        else:
            answ = None

        return answ


    def ELVwriteData (self, addr, data, name="", info ="", doPrint=True):
        """write commands for the sensors via the ELV USB-I2C"""

        doPrint = False

        wA      = "{:02X}".format((addr << 1) + 0)
        wdata   = ""
        for a in data: wdata += " {:02X}".format(a) # puts a space at the beginning

        command = bytes('S {}{} P'.format(wA, wdata), 'ASCII').upper()
        wrt     = gglobs.I2Cser.write(command)  # wrt = no of bytes written
        if doPrint: print(self.pTemplate.format(name, "TX", stime()[11:], len(command), wrt, info, command))


    def ELVinitializeRead(self, addr, rbytes, name="", info="", doPrint=True):
        """initialize reading from the sensor via the ELV USB-I2C"""

        doPrint = False

        rA      = "{:02X}".format((addr << 1) + 1)  # read address
        rb      = "{:02X}".format(rbytes)           # no of bytes
        command = bytes('S {} {} P'.format(rA, rb), 'ASCII').upper()
        wrt     = gglobs.I2Cser.write(command)  # wrt = no of bytes written
        if doPrint: print(self.pTemplate.format("", "iR", stime()[11:], len(command), wrt, info, command))


    def ELVreadData (self, length=1, name="", info="", doPrint=True):
        """ read data from the ELV USB-I2C """

        doPrint=False

        rec = gglobs.I2Cser.read(length * 3 + 2) # 3 chars per byte('FF ') + CR, LF
        cnt = gglobs.I2Cser.in_waiting
        if cnt > 0:
            print("ELVreadData Bytes waiting:", cnt)
            while True:                # read single byte until nothing is returned
                x = gglobs.I2Cser.read(1)
                if len(x) == 0: break
                rec += x

        rec = rec.rstrip(b"\r\n")       # remove carridge return, linefeed, keep last space

        if doPrint: print( self.pTemplate.format("", "RX", stime()[11:], length, len(rec), info, rec), end="")

        if not rec.strip().startswith(b"Solve ") or \
           not rec.strip().startswith(b"Err: "):        # conversion unless an error msg from dongle
            rlist = self.__getListfromRec(rec)
            return rlist
        else:
            return rec


    def ELVclose(self):
        """ Close the serial port """

        gglobs.I2Cser.close()
        wprint("ELV is closed")


    def __getListfromRec(self, rec):
        """ convert ASCII string from terminal to list of integer """
        # rec    : b'BE 6E 9A 69 32 00 ...'
        # returns: [190, 110, 154, 105, 50, 0, ...]

        rlist = []
        if len(rec) >= 3:
            for i in range(0, len(rec), 3):
                rlist.append(int(rec[i:i+3], 16))
        else: # empty record
            pass

        return rlist

