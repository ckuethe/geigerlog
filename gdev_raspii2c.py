#! /usr/bin/env python3
# -*- coding: UTF-8 -*-

"""
gdev_raspii2c.py - GeigerLog device to be used on Raspi for I2C

include in programs with:
    import gdev_raspii2c.py
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

# Pseudo-dongle needs global access
RaspiI2CDongle  = None

# the local storage every second for alldata
RaspiI2Calldata = {}

# Index into g.RaspiI2CSensor dict
I2CADDR    = 0      # I2C address
I2CACTIV   = 1      # Activations status
I2CCONN    = 2      # Connection status
I2CHNDL    = 3      # Handle
I2CVCNT    = 4      # Var Count
I2CVARS    = 5      # Var List
I2CRUNS    = 6      # Burn-in cycles
I2CAVG     = 7      # Averaging cycles
I2CFUNC    = 8      # Functions (short notation, like T,P,H)



def initRaspiI2C():
    """Initialize Raspi I2C"""

    global RaspiI2CDongle

    defname = "initRaspiI2C: "
    dprint(defname)

    g.Devices["RaspiI2C"][g.DNAME] = "RaspiI2C"
    g.Devices["RaspiI2C"][g.CONN]  = False          # default to no connection

    # computer is NOT a Raspi
    if not g.isRaspi:
        # NOT on Raspi
        g.RaspiI2CSmbusHandle      = None
        g.RaspiSmbus_Version       = "Not a Raspi"
        return "Not a Raspi. The RaspiI2C Device can be run only on a Raspberry Pi computer."

    # computer is a Raspi
    try:
        # for smbus2 see:  https://github.com/kplindegaard/smbus2
        import smbus2 as smbus

    except ImportError as ie:
        msg  = "The module 'smbus2' could not be imported, but is required."
        exceptPrint(ie, msg)
        msg += "\nRedo the GeigerLog setup."
        return msg + str(e)

    except Exception as e:
        msg = "Failure on Importing 'smbus2' "
        exceptPrint(e, msg)
        return msg + str(e)

    else:
        g.RaspiSmbus_Version = smbus.__version__
        g.versions["smbus2"] = g.RaspiSmbus_Version


    # init the I2C-Bus #1
    try:
        g.RaspiI2CSmbusHandle  = smbus.SMBus(1)
        g.RaspiI2CdirectHandle = smbus.i2c_msg()  # used for Reset code below

    except Exception as e:
        msg = "Failure initializing I2C-Bus - is it activated in the Raspi Interfaces?"
        exceptPrint(e, defname + msg)
        return msg + str(e)


    ### init dongle and all sensors ######################
    setIndent(1)
    cdprint(defname, "Init & Connect dongle and all activated sensors")
    setIndent(1)

    # instantiate Pseudo-Dongle
    RaspiI2CDongle = RaspiDongle()
    cdprint("Dongle: ", RaspiDongle.name)
    RaspiI2CDongle.DongleInit()

    SensorCount = 0
    for sensor in g.RaspiI2CSensor:
        if g.RaspiI2CSensor[sensor][1]:
            cdprint("Sensor: ", sensor)
        else:
            cdprint("Sensor: {:8s} - not activated".format(sensor) )
            continue

        setIndent(1)

        ### set the I2C handle for the current sensor
        address = g.RaspiI2CSensor[sensor][I2CADDR]

        # LM75 - I2C sensor Temperature
        if   sensor == "LM75"      :
            import gdev_i2c_Sensor_LM75         as LM75
            g.RaspiI2CSensor[sensor][I2CHNDL] = LM75    .SensorLM75     (address, RaspiI2CDongle)

        # BME280 - I2C sensor Temperature, Pressure, Humidity
        elif sensor == "BME280"    :
            import gdev_i2c_Sensor_BME280       as BME280
            g.RaspiI2CSensor[sensor][I2CHNDL] = BME280  .SensorBME280   (address, RaspiI2CDongle)

        # BH1750 - I2C sensor Ambient-Light-Sensor (Visible Light)
        elif sensor == "BH1750"    :
            import gdev_i2c_Sensor_BH1750       as BH1750
            g.RaspiI2CSensor[sensor][I2CHNDL] = BH1750  .SensorBH1750   (address, RaspiI2CDongle)

        # TSL2591 - I2C sensor Light Intensity Visible + Infrared
        elif sensor == "TSL2591"   :
            import gdev_i2c_Sensor_TSL2591      as TSL2591
            g.RaspiI2CSensor[sensor][I2CHNDL] = TSL2591 .SensorTSL2591  (address, RaspiI2CDongle)

        # BMM150 - I2C sensor Geomagnetic
        elif sensor == "BMM150"   :
            import gdev_i2c_Sensor_BMM150       as BMM150
            g.RaspiI2CSensor[sensor][I2CHNDL] = BMM150  .SensorBMM150   (address, RaspiI2CDongle)

        # SCD30 - I2C sensor CO2 (by NDIR) + Temperature + Humidity
        elif sensor == "SCD30"   :
            import gdev_i2c_Sensor_SCD30        as SCD30
            g.RaspiI2CSensor[sensor][I2CHNDL] = SCD30   .SensorSCD30    (address, RaspiI2CDongle)

        # SCD41 - I2C sensor CO2 by Photoacoustic, Temperature, Humidity
        elif sensor == "SCD41"   :
            import gdev_i2c_Sensor_SCD41        as SCD41
            g.RaspiI2CSensor[sensor][I2CHNDL] = SCD41   .SensorSCD41    (address, RaspiI2CDongle)

        # GDK101 - I2C sensor Radioactivity
        # --- ATTENTION:  it does need a 5V supply! ---
        elif sensor == "GDK101"  :
            import gdev_i2c_Sensor_GDK101       as GDK101
            g.RaspiI2CSensor[sensor][I2CHNDL] = GDK101  .SensorGDK101   (address, RaspiI2CDongle)


        # Init current sensor
        found, msg = g.RaspiI2CSensor[sensor][I2CHNDL].SensorInit()
        if found:
            SensorCount += 1
            g.RaspiI2CSensor[sensor][I2CCONN]  = True        # connected
            msg = "Initialized and connected " + msg
            fprint(msg)
            dprint(msg)

        else:
            g.RaspiI2CSensor[sensor][I2CCONN]  = False       # NOT connected
            msg1 = "Failed initializing sensor {};  response: ".format(sensor)
            efprint(msg1 + "\n" + msg)
            rdprint(msg1 + msg)

        setIndent(0)

    setIndent(0)
    ###### end sensor-init loop ######################

    if SensorCount == 0:
        returnmsg = "No Sensors found"

    else:
        returnmsg = ""
        g.Devices["RaspiI2C"][g.CONN]  = True
        fprint("RaspiI2C device is connected with {} sensor(s)".format(SensorCount))

        # get the variables from all sensors combined
        allvars = []    # list to hold the vnames
        for sensor in g.RaspiI2CSensor:
            # rdprint(defname, "sensor: ", sensor, "   ",  g.RaspiI2CSensor[sensor])
            if g.RaspiI2CSensor[sensor][I2CACTIV]:
                temp = []
                for vname in g.RaspiI2CSensor[sensor][I2CVARS]:
                    cvname = correctVariableCaps(vname)
                    if cvname != "" and cvname != "auto":   temp.append(cvname)

                g.RaspiI2CSensor[sensor][I2CVARS] = temp[0 : g.RaspiI2CSensor[sensor][I2CVCNT]] # limit to configured number of vars
                allvars += g.RaspiI2CSensor[sensor][I2CVARS]

        g.RaspiI2CVariables = setLoggableVariables("RaspiI2C", ", ".join(allvars))      # RaspiI2CVariables is a string
        g.RaspiI2Cvarlist   = g.RaspiI2CVariables.replace(" ", "").split(",")

        for vname in g.RaspiI2CVariables.replace(" ", "").split(","):
            # g.RaspiI2CDataStore[vname] = []
            g.RaspiI2CDataStore[vname] = deque([], 60)

    # burn-in
    RaspiSensorsBurnIn()

    # reset
    resetRaspiI2C()

    # setup thread
    g.RaspiI2CThreadStopFlag = False
    g.RaspiI2CThread         = threading.Thread(target = RaspiI2CThreadTarget)
    g.RaspiI2CThread.daemon  = True
    g.RaspiI2CThread.start()

    # printout RaspiI2C Settings
    ptmplt = "   {:27s} : {}"
    dprint("RaspiI2C Settings:")
    dprint(ptmplt.format("Raspi Computer Model"     , g.RaspiModel))
    dprint(ptmplt.format("Raspi SW smbus2 Version"  , g.RaspiSmbus_Version))
    dprint(ptmplt.format("RaspiI2C Sensors Defined" , ""))
    for sensor in g.RaspiI2CSensor:
        sadd = "None" if g.RaspiI2CSensor[sensor][I2CADDR] is None else hex(g.RaspiI2CSensor[sensor][I2CADDR])
        scon = "connected"  if g.RaspiI2CSensor[sensor][I2CCONN] else "---"
        dprint("   {:27s} : {:10s} address:{}  {}".format("   Sensor", sensor, sadd, scon))

    dprint("   {:27s} : {}".format("RaspiI2CThread.daemon"      , g.RaspiI2CThread.daemon))
    dprint("   {:27s} : {}".format("RaspiI2CThread.is_alive"    , g.RaspiI2CThread.is_alive()))

    setIndent(0)
    return returnmsg


def terminateRaspiI2C():
    """closes RaspiI2C handle"""

    defname = "terminateRaspiI2C: "
    dprint(defname)
    setIndent(1)

    g.RaspiI2CThreadStopFlag = True

    time.sleep(0.5) # to let all I2C devices finish

    if g.RaspiI2CSmbusHandle is not None:
        try:                   g.RaspiI2CSmbusHandle.close()
        except Exception as e: exceptPrint(e, "RaspiI2C connection is not available")

    g.RaspiI2CSmbusHandle = None
    g.Devices["RaspiI2C"][g.CONN] = False

    dprint(defname + "Terminated")
    setIndent(0)


def RaspiI2CThreadTarget():
    """The Target function for the RaspiI2C thread"""

    global RaspiI2Calldata

    defname  = "THREAD_RaspiI2CThreadTarget: "

    nexttime = time.time() + 1                                  # give it some delay before starting
    if g.nextnexttime is None:  g.nextnexttime = nexttime + 1   # weil g.logging früher gesetzt wird als g.nextnexttime :-/
    while not g.RaspiI2CThreadStopFlag:
        if time.time() >= nexttime:
            RaspiI2Calldata = RaspiI2CThreadgetData(g.RaspiI2Cvarlist)

            if not g.logging: nexttime += 1
            # else:             nexttime  = g.nextnexttime - 0.1   # start 100 ms before next after next logcycle starts
            # else:             nexttime  = g.nextnexttime - 0.4   # start 400 ms before next after next logcycle starts
            #                                                      # TSL2591 braucht 380 ms !!!
            else:             nexttime  = g.nextnexttime - g.RaspiI2CCumDur

        dt = max(0.001, nexttime - time.time())
        time.sleep(dt)


def RaspiI2CThreadgetData(varlist):
    """collect all I2C data"""

    gDstart = time.time()

    defname = "THREAD_RaspiI2CThreadgetData: "
    # rdprint(defname, varlist)
    setIndent(1)

    # set sensor values for all vars to NAN
    SensorValues = {}
    for vname in g.VarsCopy:    SensorValues[vname] = g.NAN

    # get the data from each sensor
    tsstart  = time.time()
    cdur     = 100
    for sensor in g.RaspiI2CSensor:
        if g.RaspiI2CSensor[sensor][I2CCONN]:
            sstart     = time.time()
            dur1st     = 0
            avglen     = g.RaspiI2CSensor[sensor][7]                            # avglen = the number of 1 sec values to average
            SensorVals = g.RaspiI2CSensor[sensor][I2CHNDL].SensorgetValues()    # SensorVals is tuple with 1 ... 3 values
            # mdprint(defname + "sensor: ", sensor, "  values: ", SensorVals)

            # get data for each var in a sensor
            for i in range(g.RaspiI2CSensor[sensor][I2CVCNT]):
                vname = g.RaspiI2CSensor[sensor][I2CVARS][i]
                if vname != "None":
                    g.RaspiI2CDataStore[vname].append(SensorVals[i])

                    liststore           = list(g.RaspiI2CDataStore[vname])      # make it a Python list to allow slicing
                    lenliststore        = len(liststore)
                    SensorValues[vname] = sum(liststore[-avglen : ]) / min(avglen, lenliststore)

                    # durations
                    sdur = 1000 * (time.time() - sstart) - dur1st
                    cdur = 1000 * (time.time() - tsstart)

                    # print only when logging
                    if g.logging:
                        if i == 0: dur1st = sdur
                        rdprint(defname, "{:10s} {:6s} orig:{:<10.3f}  avg:{:<10.3f}  Navg:{:<2d}  storelen:{}  dur:{:5.1f} ms  cum:{:5.1f} ms".format(
                                          sensor, vname, SensorVals[i], SensorValues[vname], avglen, lenliststore, sdur, cdur))

    g.RaspiI2CCumDur = cdur / 1000 + 0.01

    # scale values and save to alldata
    alldata = {}
    for vname in varlist:
        scaled_SensorVals  = round(applyValueFormula(vname, SensorValues[vname], g.ValueScale[vname]), 3)
        alldata.update({vname: scaled_SensorVals})

    setIndent(0)
    # vprintLoggedValues(defname, varlist, alldata, 1000 * (time.time() - gDstart))

    return alldata


def getValuesRaspiI2C(varlist):
    """return the within thread collected values"""

    start   = time.time()
    defname = "getValuesRaspiI2C: "

    vprintLoggedValues(defname, varlist, RaspiI2Calldata, 1000 * (time.time() - start))

    return RaspiI2Calldata


def getInfoRaspiI2C(extended=False):
    """Info on the RaspiI2C Device"""

    Info =          "Configured Connection:        GeigerLog PlugIn\n"

    if not g.Devices["RaspiI2C"][g.CONN]:
        Info +=     "<red>Device is not connected</red>"

    else:
        Info +=     "Connected Device:             {}\n".format(g.Devices["RaspiI2C"][g.DNAME])
        Info +=     "Configured Variables:         {}\n".format(g.RaspiI2CVariables)
        Info +=     getTubeSensitivities(g.RaspiI2CVariables)
        Info +=     "\n"

        Info +=     "Connected RaspiI2C Sensors:\n"
        Info +=     "   {:<10s} {:15s} {}   {:2s}    {}\n".format("Sensor", "Function", "Adress", "Averaging", "Variables")
        for sensor in g.RaspiI2CSensor:
            if g.RaspiI2CSensor[sensor][I2CCONN]:
                saddr = g.RaspiI2CSensor[sensor][I2CHNDL].addr
                svars = ", ".join(g.RaspiI2CSensor[sensor][5])
                sfunc = g.RaspiI2CSensor[sensor][I2CFUNC]
                Info += "   {:<10s} {:<15s} 0x{:2X}     {:<2d}           {}\n".format(sensor, sfunc, saddr, g.RaspiI2CSensor[sensor][7], svars)

        if extended:
            Info += "Host Computer:\n"
            Info += "   Computer Model             {}\n".format(g.RaspiModel)
            Info += "   Software smbus2 Version    {}\n".format(g.RaspiSmbus_Version)

            Info += "RaspiI2C Scan Result:\n"
            Info += scanRaspiI2C()
            Info +=     "\n"

    return Info


def resetRaspiI2C():
    """Reset the sensors"""

    defname = "resetRaspiI2C: "
    setBusyCursor()

    dprint(defname + "---------------------------------------------------")
    setIndent(1)

    fprint(header("Resetting RaspiI2C System"))
    fprint("In progress ...")
    QtUpdate()

    # reset the dongle
    try:
        msg = RaspiI2CDongle.DongleReset()
        dprint(defname, "Dongle: {:12s} - {}".format(RaspiI2CDongle.name, msg))
    except Exception as e:
        exceptPrint(e, defname + "DongleReset failed")

    # reset all sensors
    for sensor in g.RaspiI2CSensor:
        # cdprint(defname, "sensor: ", sensor)
        if g.RaspiI2CSensor[sensor][I2CCONN]:
            try:
                msg = g.RaspiI2CSensor[sensor][I2CHNDL].SensorReset()
                dprint(defname, "Sensor: {:12s} - {}".format(sensor, msg))
            except Exception as e:
                exceptPrint(e, defname + "Resetting sensor {} failed".format(sensor))

    fprint("RaspiI2C Reset done")
    # dprint(defname, "Done")

    setNormalCursor()
    setIndent(0)


def RaspiSensorsBurnIn():
    """Burn-in as First Values may be invalid"""

    defname = "RaspiSensorsBurnIn: "
    dprint(defname)
    setIndent(1)

    for sensor in g.RaspiI2CSensor:
        # rdprint(defname + "sensor: ", sensor)
        if g.RaspiI2CSensor[sensor][I2CCONN]:       # use connected sensors only
            # make measurements and discard
            for i in range(0, g.RaspiI2CSensor[sensor][I2CRUNS]):
                # print(defname, sensor, i)
                val = g.RaspiI2CSensor[sensor][I2CHNDL].SensorgetValues()
                vprint(defname, "Sensor:{:10s}  Cycle:{}  Value:{}".format(sensor, i, val))
                time.sleep(0.05)

    setIndent(0)


def scanRaspiI2C():
    """scan all addresses by reading from them at register 0"""

    defname = "scanRaspiI2C: "

    response     = "   -- : 00 01 02 03 04 05 06 07 08 09 0A 0B 0C 0D 0E 0F\n"
    response    += "   00 : .. "

    if g.RaspiI2CSmbusHandle is None:
        burp()
        response = "<red>   Computer has no accessible I2C system"

    else:
        device_count = 0
        for address in range(1, 128):
            if (address % 16) == 0:
                response += "\n   "
                response += "{:02X} : ".format(address)

            found = False
            try:
                # g.RaspiI2CSmbusHandle.write_byte(address, 0)       # by writing
                g.RaspiI2CSmbusHandle.read_byte_data(address, 0)     # by reading
                # print("{} Found {}".format(address, hex(address)))
                device_count += 1
                found = True

            except IOError as e:
                # exceptPrint(e, "device: {}  i2cscan IOError".format(address))
                pass

            except Exception as e: # exception if read_byte fails
                exceptPrint(e, defname + "Exception")

            if found: response += "{:02X} ".format(address)
            else:     response += ".. "

        response += "   Found {} I2C devices".format(device_count)

    return response



###
### Raspi "Dongle"
###
class RaspiDongle():
    """To make it similar to the Dongle I2C routines"""

    name    = "RaspiDongle"


    def __init__(self):
        """Init RaspiDongle"""

        pass


    def DongleInit(self):
        """just some formal init"""

        defname = "DongleInit: " + self.name + ": "
        # dprint(defname)
        setIndent(1)
        setIndent(1)

        # reset
        gdprint(defname, self.DongleReset())

        dmsg     = "Dongle {:8s} initialized".format(self.name)
        setIndent(0)
        setIndent(0)

        return (True,  dmsg)


    def DongleWriteRead(self, addr, register, readbytes, data, addrScheme=1, msg="", wait=0):
        """combines
        def DongleWriteReg(self, addr, register, readbytes, data, addrScheme=1, msg=""):
        def DongleGetData (self, addr, register, readbytes, data, addrScheme=1, msg=""):
        into one, with error checking after write
        wait is wait phase between write and read call
        """

        defname = "DongleWriteRead: "
        # dprint(defname)

        success = self.DongleWriteReg(addr, register, readbytes, data, addrScheme=addrScheme, msg=msg)
        if not success: return [] # failure in writing - return empty list

        # Write succeeded; wait as configured
        # time.sleep(wait)
        time.sleep(wait*30)

        # now get data
        answ = self.DongleGetData (addr, register, readbytes, data, addrScheme=addrScheme, msg=msg)

        return answ


    def DongleWriteByte(self, addr, register, readbytes, data, addrScheme=1, msg=""):
        """write a single byte"""

        defname = "DongleWriteByte: "
        # dprint(defname)
        # dprint(defname, "data: ", data)

        try:
            g.RaspiI2CSmbusHandle.write_byte_data(addr, register, data[0])
            success = True
        except Exception as e:
            exceptPrint(e, defname + msg)
            success = False

        # if not success: rdprint(defname, "{}  {:15s} success:{}".format(hex(addr), msg, success))
        # else:           cdprint(defname, "{}  {:15s} success:{}".format(hex(addr), msg, success))     # print only on failure

        return success


    def DongleWriteI2CDirect(self, addr, register, readbytes, data, addrScheme=1, msg=""):
        """write a single byte"""

        defname = "DongleWriteI2CDirect: "
        # dprint(defname)
        # dprint(defname, "data: ", data)

        try:
            g.RaspiI2CdirectHandle.write(addr, data)
            success = True
        except Exception as e:
            exceptPrint(e, defname + msg)
            success = False

        # if not success: rdprint(defname, "{}  {:15s} success:{}".format(hex(addr), msg, success))
        # else:           cdprint(defname, "{}  {:15s} success:{}".format(hex(addr), msg, success))     # print only on failure

        return success


    def DongleWriteReg(self, addr, register, readbytes, data, addrScheme=1, msg=""):
        """Writes to register of dongle, perhaps with data"""

        # addr     : the 7 bit address of sensor
        # register : sensor internal register address, 1 byte or 2 byte, like 0x00, 0x3345
        # readbytes: number of bytes to read (not relevant here)
        # data     : any data bytes to write as list

        defname = "DongleWriteReg: "
        # dprint(defname, "data: ", data)

        try:
            # rdprint(defname, "addr:{} register:{} data:{} ".format(addr, register, data))
            g.RaspiI2CSmbusHandle.write_i2c_block_data(addr, register, data)   # return is always None
            success = True
        except Exception as e:
            exceptPrint(e, defname + msg)
            success = False

        # if not success: rdprint(defname, "{}  {:15s} success:{}".format(hex(addr), msg, success))   # print only on failure
        # # else:         cdprint(defname, "{}  {:15s} success:{}".format(hex(addr), msg, success))

        return success


    def DongleGetData(self, addr, register, readbytes, data, addrScheme=1, msg=""):
        """reads data as list"""

        # addr     : the 7 bit address of sensor
        # register : sensor internal register address, 1 byte or 2 byte, like 0x00, 0x3345 (not relevant here)
        # readbytes: number of bytes to read
        # data     : any data bytes to write (not relevant here)
        # return   : list of bytes of len = readbytes, or empty list on failure

        defname = "DongleGetData:  "
        # dprint(defname)

        try:
            lrec  = g.RaspiI2CSmbusHandle.read_i2c_block_data(addr, register, readbytes)
        except Exception as e:
            exceptPrint(e, defname + msg)
            lrec  = []

        wprint(defname, "{}  {:15s} len(lrec):{:<2n}  {}".format(hex(addr), msg, len(lrec), lrec))

        return lrec


    def DongleIsSensorPresent(self, addr):
        """reads from a single address register 0; if exception then no device at address 'addr'"""

        # addr     : the 7 bit address of sensor
        # register : hard coded for 0
        # return   : True when found; False otherwise

        defname = "DongleIsSensorPresent: "
        # dprint(defname)
        setIndent(1)

        foundSensor = False
        try:
            ### testing with read from reg 0
            g.RaspiI2CSmbusHandle.read_byte_data(addr, 0)
            foundSensor = True

        except IOError as e:
            if g.devel: exceptPrint(e, defname + "Device NOT present. IOError reading address: 0x{:02X}".format(addr))

        except Exception as e:
            exceptPrint(e, "i2c_read Exception on address: 0x{:02X}".format(addr))

        setIndent(0)

        return foundSensor


    def DongleReset(self):
        """Reset the Raspi dongle - Dummy"""

        defname = "DongleReset: "

        return defname + "(dummy reset)"


