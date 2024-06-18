#! /usr/bin/env python3
# -*- coding: utf-8 -*-

"""
rconfig.py - DataServer's configuration

include in programs with:
    import rconfig
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


#####################################################################################################
####################       Begin of CUSTOMIZE SECTION        ########################################
#####################################################################################################

# Lines beginning with '#' are comments and will be ignored


# cycletime
ccycletime      = 1

# TransferType   - Use WIFI (for WiFiServer) or MQTT (for MQTT client) or BOTH to transfer the
# data to the web. All traffic goes over WiFi or Ethernet, whatever the Raspi is set up for.
# For WIFI GeigerLog needs Raspi's IP of this connection and Port as specified below (like 4000).
# For MQTT GeigerLog needs the MQTT Broker IP, Port and Folder as specified below
# (like: "test.mosquitto.org", 1883, "/")
#
# Options:          "WIFI" | "MQTT" | "BOTH"
# cTransferType   = "BOTH"
# cTransferType   = "MQTT"
cTransferType     = "WIFI"

## WiFi - needed if cTransferType is "WiFi" or "BOTH":
#  Port Number on which the WiFiServer-Computer will listen
#  NOTE: make sure nothing else is using the port, otherwise connection fails
#        Use nmap to scan; available for Lin, Win, Mac, Raspi: https://nmap.org/
#        To scan all ports from 1 to 65535 the command is:
#                   nmap  <IP of computer running DataServer> -p1-65535
#           like:   nmap 10.0.0.100 -p1-65535
#
#  Option:        < a single number from:  1024 ... 65535 >
#  Default:       4000
cWiFiServerPort = 4000

## MQTT - needed if cTransferType is "MQTT" or "BOTH":
cIoTBrokerIP     = "test.mosquitto.org"
cIoTBrokerPort   = 1883
cIoTBrokerFolder = "/"
cIoTTimeout      = 5

## Display name for this setup
cDisplayName     = "Raspi-Data Server"

## Log files
# the log files will be saved into directory log, a subdirectory to the DataServer location
#
# Data Log File: a CSV file with all the recorded data. The file expands up to a
# max size of 10 mio bytes. Then recording stops, but the program continues
cDataLogFile     = ""                        # if set to empty this log file will NOT be written
cDataLogFile     = "DataServer.datalog"      # overrides default empty setting

# Program Log file: this saves the program's output as text. The file will be appended
# until a max size (100 k bytes)is reached; then data from after the startup-phase will
# be successively overwritten.
cProgLogFile     = ""                        # if set to empty this log file will NOT be written
cProgLogFile     = "DataServer.proglog"      # overrides default empty setting

#####################################################################################################
## GMC counter specific settings
#####################################################################################################
# use the GMC counter (True) or not (False)
# cGMCusage        = True
cGMCusage        = False

# The GMC counter should work properly with port and baudrate settings on 'auto'.
# If it doesn't, please report as bug and try defining the settings manually.
cGMCport         = "auto"                    # on Raspi:    likely port is '/dev/ttyUSB0'
#                                            # on Linux:    likely port is '/dev/ttyUSB0'
#                                            # on Windows:  likely port is 'COM3'
cGMCbaudrate     = "auto"                    # baudrate:    for the GMC 300 series:        57600
#                                            #              for GMC 320, 5XX, 6XX series: 115200

# select from one to all from "CPM, CPS, CPM1st, CPS1st, CPM2nd, CPS2nd"
cGMCvariables    = "auto"                    # "auto" defaults to "CPM1st, CPS1st, CPM2nd, CPS2nd"
cGMCvariables    = "CPM1st, CPS1st"          # custom selection (overrides default "auto")


#####################################################################################################
## I2C Sensor specific settings
#####################################################################################################
# use the I2C device (True) or not (False)
cI2Cusage           = False

# use from one to all I2C sensors; use it (True) or not (False)
cI2Cusage_LM75B     = False                 # T
cI2Cusage_BME280    = True                  # T, P, H
cI2Cusage_BH1750    = True                  # Vis
cI2Cusage_VEML6075  = False                 # UV-A and UV-B, and helper data
cI2Cusage_LTR390    = False                 # Vis and UV
cI2Cusage_GDK101    = False                 # "Geiger" counts
cI2Cusage_SCD30     = False                 # CO2
cI2Cusage_SCD41     = False                 # CO2

# define the I2C address your sensor is set to
cI2Caddr_LM75B      = 0x48                  # options: 0x48 | 0x49 | 0x4A | 0x4B | 0x4C | 0x4D | 0x4E | 0x4F
cI2Caddr_BME280     = 0x77                  # options: 0x76 | 0x77 NOTE: Bluedot breakout board has only 0x77; 0x76 is NOT available!
cI2Caddr_BH1750     = 0x23                  # options: 0x23 | 0x5C
cI2Caddr_VEML6075   = 0x10                  # options: 0x10 | (no other option)
cI2Caddr_LTR390     = 0x53                  # options: 0x53 | (no other option)
cI2Caddr_GDK101     = 0x18                  # options: 0x18 | 0x19 | 0x1A | 0x1B
cI2Caddr_SCD30      = 0x61                  # options: 0x61 | (no other option)
cI2Caddr_SCD41      = 0x62                  # options: 0x62 | (no other option)

# configure sensors: {"<GeigerLog target variable>" : <avg period in sec 1 ... 60> [, ...] }
#           example: {"CPM3rd":10, "Press":5, "Humid":5}
#
#   - <GeigerLog target variable>   : Can be any of GeigerLog's 12 variables:
#                                     CPM,CPS,CPM1st,CPS1st,CPM2nd,CPS2nd,CPM3rd,CPS3rd, Temp,Press,Humid,Xtra
#   - <avg period in sec 1 ... 60>  : The returned data will have been averaged over the given period in seconds
#                                     On "1" the very last measured single data point will be returned
#   - Can be repeated to use multiple averages, like: cI2Cvars_LM75B = {"Temp" : 60, "Press" : 20, "Humid" : 5}
#

# sensor LM75B - Temperature
cI2Cvars_LM75B      = {"CPS1st":10}

# sensor BME280 - Temperature, (barometric-) Pressure, Humidity
cI2Cvars_BME280     = {"Temp":3, "Press":3, "Humid":3}

# sensor BH1750 - Visible light intensity in Lux (recommended: 5 sec avg)
cI2Cvars_BH1750     = {"Xtra":1}

# sensor VEML6075 - UV light intensity (UV-A, UV-B, UV-A-corr, UV-B-corr, uvd (dark current), uvcomp1, uvcomp1)
cI2Cvars_VEML6075   = {"CPM2nd":1, "CPS2nd":1, "CPM3rd":1, "CPS3rd":1}

# sensor LTR390 -  Visible light intensity, UV light
cI2Cvars_LTR390     = {"CPM":1, "CPS":60 }

# sensor GDK101 - "Geiger counts by PIN diode"
# all target variables will get same value; avg is ignored
cI2Cvars_GDK101     = {"CPS1st":1}

# sensor SCD30 - CO2 (by NDIR), Temperature, and Humidity
# avg is ignored
cI2Cvars_SCD30      = {"CPM3rd":1}

# sensor SCD41 - CO2 (by Sound), Temperature, and Humidity
# avg is ignored
cI2Cvars_SCD41      = {"CPS3rd":1}


#####################################################################################################
## Pulse specific settings
#####################################################################################################
# use the Pulse device (True) or not (False)
cPulseUsage         = True

# configure Raspi GPIO pin
cPulseCountPin      = 17                    # 17 is default GPIO pin in BCM mode to be used for pulse counting
                                            # allowed: 5 ... 26;   VERIFY NO CONFLICTING OTHER USAGE OF SELECTED PIN !!!
                                            # BCM-Pin=17 is on BOARD-Pin=11

# select from one to all from "CPM,CPS,CPM1st,CPS1st,CPM2nd,CPS2nd,CPM3rd,CPS3rd".
# No more than one CPM* and one CPS* are meaningful, because all CPM* and CPS*, resp., will be the same!
# i.e.: CPM = CPM1st = CPM2nd = CPM3rd and CPS = CPS1st = CPS2nd = CPS3rd
# cPulseVariables   = "auto"                # "auto" defaults to "CPM, CPS"
cPulseVariables     = "CPM1st, CPS1st"      # custom selection

#####################################################################################################
####################   END of CUSTOMIZE SECTION   ###################################################
#####################################################################################################

