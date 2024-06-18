#! /usr/bin/env python3
# -*- coding: utf-8 -*-

"""
rmain.py - DataServer's main entry file

include in programs with:
    import rmain
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


# start X11vnc on raspi:  sudo x11vnc -httpport 80 -httpdir /usr/share/novnc/ -no6 -xkb -repeat -auth guess -display WAIT:0 -forever -shared


from   rutils   import *


import rwifis               # WiFi Server
import rmqttc               # MQTT Client
import rdev_gmc             # GMC
import rdev_i2c             # I2C
import rdev_pulse           # Pulse



def clearTerminal():
    """clear the terminal"""

    # The name of the operating system dependent module imported. The following
    # names have currently been registered: 'posix', 'nt', 'java'.
    if "LINUX" in platform.platform().upper():
        # clear the terminal
        os.system("export TERM=xterm-256color")     # needed to prep for clear
        os.system("clear")                          # clear terminal
    os.system('cls' if os.name == 'nt' else 'clear')
    # print("os.name: ", os.name) # os.name:  posix (on Linux)


def main():
    """main"""

    ### local def ########################
    def checkInitInfo(device, initresp, sensors):
        hmsg = "   {:27s} : {}".format("Init {} Devices:".format(device), "{}, {}".format(initresp, sensors))
        if initresp == "Ok":
            gdprint(hmsg)
            return True
        else:
            edprint(hmsg)
            return False

    def terminateAll():
        """Switch down everything on CTRL-C or other exception"""

        dprint()
        dprint(rwifis.terminateWiFiServer())
        rmqttc.terminateMQTT()

        if g.GMCusage:   dprint(rdev_gmc.terminateGMC())
        if g.I2Cusage:   dprint(rdev_i2c.terminateI2C())
        if g.Pulseusage: dprint(rdev_pulse.terminatePulse())
    ######################################

    defname = "main: "

    clearTerminal()

    print("=" * 150)

    try: # wg keyboardinterrupt

        # get Program Name & Path, log files dir & path. Make log dirs if needed
        g.ProgName      = getProgName()
        g.ProgPath      = getPathToProgDir()
        g.DataLogDir    = os.path.join(g.ProgPath, "log")
        g.ProgLogDir    = os.path.join(g.ProgPath, "log")
        g.DataLogPath   = os.path.join(g.DataLogDir, g.DataLogFile)
        g.ProgLogPath   = os.path.join(g.ProgLogDir, g.ProgLogFile)
        if not os.path.exists(g.DataLogDir): os.mkdir(g.DataLogDir)
        if not os.path.exists(g.ProgLogDir): os.mkdir(g.ProgLogDir)

        # check if computer is Raspi and return if not
        CheckIfRaspberryPi()
        if not g.isRaspberryPi:
            returnflag = False
            if g.I2Cusage:
                edprint()
                edprint("You have activated I2C usage, which REQUIRES that this script is run on a Raspberry Pi")
                edprint("computer, but your computer is a different one. Cannot continue; will exit.")
                edprint("If you can't use a Raspi computer, then inactivate I2C usage in the 'Customize Section'")
                edprint("in the file 'rconfig.py' by setting:  'cI2Cusage = False'")
                edprint()
                returnflag = True

            if g.Pulseusage:
                edprint()
                edprint("You have activated Pulse usage, which REQUIRES that this script is run on a Raspberry Pi")
                edprint("computer, but your computer is a different one. Cannot continue; will exit.")
                edprint("If you can't use a Raspi computer, then inactivate Pulse usage in the 'Customize Section'")
                edprint("in the file 'rconfig.py' by setting:  'cPulseUsage = False'")
                edprint()
                returnflag = True

            if returnflag: return

        rDevices  = ""
        rDevices += "GMC  "   if g.GMCusage   else ""
        rDevices += "I2C  "   if g.I2Cusage   else ""
        rDevices += "Pulse"   if g.Pulseusage else ""

        # prep system docu
        sysdoc  = ""
        sysdoc += "# {:28s} : {}\n".format("Version of {}".format(g.ProgName), g.__version__)
        sysdoc += "# {:28s} : {}\n".format("Version of Python", sys.version.replace("\n", " "))
        sysdoc += "# {:28s} : {}\n".format("Version of Operating System", platform.platform())
        sysdoc += "# {:28s} : {}, {}\n".format("Machine, Architecture", platform.machine(), platform.architecture()[0])
        sysdoc += "# {:28s} : {}\n".format("Computer Model", g.computer)
        sysdoc += "# {:28s} : {}\n".format("Working Directory", g.ProgPath)
        sysdoc += "# {:28s} : {}\n".format("LogFile Prog", g.ProgLogFile if g.ProgLogFile > "" else "None")
        sysdoc += "# {:28s} : {}\n".format("LogFile Data", g.DataLogFile if g.DataLogFile > "" else "None")
        sysdoc += "# {:28s} : {}\n".format("Supported Devices", "GMC  I2C  Pulse")
        sysdoc += "# {:28s} : {}\n".format("Activated Devices", rDevices)
        if not "WINDOWS" in platform.platform().upper():
            sysdoc += "\n# {:28s} : {}\n".format("Getting Help", "Press key 'h'")

        print("# DataServer System Documentation\n" + sysdoc)

        # init ProgLogFile (must come BEFORE init DataLogFile!)
        msg  = "# ProgLogFile by program: '{}'\n".format(g.ProgName)
        msg += sysdoc
        createProgLogFile(msg)

        # init DataLogFile
        msg  = "# DataLogFile by program: '{}'\n".format(g.ProgName)
        msg += sysdoc
        msg += "\n"
        msg += "# Index,                DateTime,      CPM,     CPS,  CPM1st,  CPS1st,  CPM2nd,  CPS2nd,  CPM3rd,  CPS3rd,    Temp,   Press,   Humid,    Xtra,  Duration[ms]"
        createDataLogFile(msg)

        # init Devices
        # on any failure exit program
        dprint("{:33s} : {}".format("Init Devices activated in configuration", ""))
        setIndent(1)

        if g.GMCusage:
            dprint()
            if not checkInitInfo("GMC", rdev_gmc.initGMC(), g.GMCcounterversion):
                return

        if g.I2Cusage:
            dprint()
            if not checkInitInfo("I2C", rdev_i2c.initI2C(), "Sensors: " + str(g.I2Csensors)):
                return

        if g.Pulseusage:
            dprint()
            if not checkInitInfo("Pulse", rdev_pulse.initPulse(), "BCM-Pin: {}".format(g.PulseCountPin)):
                return

        setIndent(0)
        # init Devices all done

        # init Transfer Types
        # on any failure exit program
        dprint()
        dprint("{:33s} : {}".format("Init Transfer Type (MQTT, WiFi, BOTH) as activated in configuration", ""))
        setIndent(1)

        if g.TransferType in ["WIFI", "BOTH"]:
            # init WiFi Server; on failure exit
            dprint()
            WSsuccess, WSresponse = rwifis.initWiFiServer()
            WSmsg = "{:33s} : {}".format("Init WiFi Server", WSresponse)
            if WSsuccess:
                gdprint(WSmsg)
            else:
                edprint(WSmsg)
                return

        if g.TransferType in ["MQTT", "BOTH"]:
            # init MQTT Client, on failure exit
            dprint()
            MSsuccess, MSresponse = rmqttc.initMQTT()
            MSmsg = "{:33s} : {}".format("Init MQTT", MSresponse)
            if MSsuccess:
                gdprint(MSmsg)
            else:
                edprint(MSmsg)
                return

        setIndent(0)
        # init Transfer Type all done

        dprint()

        # Loop forever; break with CTRL-C
        # Use simple timer to create cycletime sec intervals for getting values into resp. data store
        next = time.time()                                      # now
        while True:
            if time.time() >= next:
                next   = next + cycletime                       # set start of next cycle
                g.CycleOngoing = True

                if g.ResetOngoing == False:
                    vprint("")

                    # GMC
                    if g.GMCusage:               g.GMCstoreCounts    .append(rdev_gmc.getValGMC())

                    # I2C
                    if g.I2Cusage:
                        if g.I2Cusage_LM75B:     g.I2CstoreLM75B     .append(g.lm75b    .getValLM75B())
                        if g.I2Cusage_BME280:    g.I2CstoreBME280    .append(g.bme280   .getValBME280())
                        if g.I2Cusage_BH1750:    g.I2CstoreBH1750    .append(g.bh1750   .getValBH1750())
                        if g.I2Cusage_VEML6075:  g.I2CstoreVEML6075  .append(g.veml6075 .getValVEML6075())
                        if g.I2Cusage_LTR390:    g.I2CstoreLTR390    .append(g.ltr390   .getValLTR390())
                        if g.I2Cusage_GDK101:    g.I2CstoreGDK101    .append(g.gdk101   .getValGDK101("OneMin"))
                        if g.I2Cusage_SCD30:     g.I2CstoreSCD30     .append(g.scd30    .getValSCD30())
                        if g.I2Cusage_SCD41:     g.I2CstoreSCD41     .append(g.scd41    .getValSCD41())


                    # Pulse
                    if g.Pulseusage:

                        ### Testing varying Pulse rates in Poisson shape #####
                        if 0:
                            poissonvalue = getPoissonValue(g.PWMFreq)
                            rfreq = max(0.1, poissonvalue) # freq must be > 0.0 !

                            cdprint("new rfreq: {:0.3f}".format(rfreq))

                            # change pulserate  -  "frequency must be greater than 0.0"
                            if g.PWMHandle is not None: g.PWMHandle.ChangeFrequency(rfreq)
                        #####################################

                        g.PulseStore        .append(rdev_pulse.getValPulse())

                    # collect all data that were just created
                    g.CollectedData = collectData()

                    # send collected data by MQTT if configured
                    if g.TransferType in ("MQTT", "BOTH"):  rmqttc.publishMQTT()

                    # Startup-Phase completed
                    if g.ProgLogFilePhase == 0:
                        g.ProgLogFilePhase = 1
                        dprint()
                        gdprint("Startup-Phase completed " + "-" *80 + "\n")

                g.CycleOngoing = False

            if not 'win32' in sys.platform:  KeyChecker()       # any keys pressed? (Linux only)

            time.sleep(0.2)


    except KeyboardInterrupt as e:
        # exceptPrint(e, defname + "Keyboard-Interrupt Exception")
        dprint("Keyboard-Interrupt - Terminating")
        terminateAll()

    except Exception as e:
        # Last resort
        exceptPrint(e, defname + "Non-Keyboard-Interrupt Exception - Terminating")
        terminateAll()

