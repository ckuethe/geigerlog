#! /usr/bin/env python3
# -*- coding: UTF-8 -*-

"""
rglobs.py - DataServers's Super-Global Variables; can be read and modified in all scripts

include in programs with:
    import rglobs as g
"""

#####################################################################################################
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
#####################################################################################################

__author__              = "ullix"
__copyright__           = "Copyright 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024"
__credits__             = [""]
__license__             = "GPL3"

__version__             = "4.0"                 # of this script
__version__             = "4.0.2pre03"


# Generics
DisplayName             = "Undefined"           # display name for this DataServer
NAN                     = float('nan')          # 'not-a-number'; used as 'missing value'

# cycletime in sec
cycletime               = 1

# GeigerLog's 12 vars
GLVarNames              = ['CPM', 'CPS', 'CPM1st', 'CPS1st', 'CPM2nd', 'CPS2nd', 'CPM3rd', 'CPS3rd',
                           'Temp', 'Press', 'Humid', 'Xtra']

# versions
versions                = {}                    # software versions
versions["GPIO"]        = "Undefined"
versions["paho-mqtt"]   = "Undefined"
versions["smbus"]       = "Undefined"
ProgName                = "undefined"           # will be determined later

# Data Traffic
TransferType            = "BOTH"                # "WiFi" | "MQTT" | "BOTH"
CollectedData           = b""                   # collected by call to collectData()

# class holders
lm75b                   = None
bme280                  = None
bh1750                  = None
veml6075                = None
ltr390                  = None
gdk101                  = None

# Admin
debug                   = True                  # print output as debug
verbose                 = True                  # print output as verbose
tracebackFlag           = False                 # if true then print traceback info on exception
ResetOngoing            = False                 # True when Reset in progress
CycleOngoing            = False                 # True when Cycle in progress

# log files
DataLogFile             = "DataServer.datalog"  # give a name to your log file; if set to empty this log file will NOT be written
DataLogPath             = None                  # defined in main
DataLogFileWriteOK      = True                  # WOK=Write OK: no further writing on False
DataLogFileMax          = 1E7                   # max size of DataLogFile in bytes
DataLogFileMaxMsg       = "DataLogFile has reached maximum size of {:3,.0f} bytes - No further data will be written\n"\
                            .format(DataLogFileMax)

ProgLogFile             = "DataServer.proglog"  # saves the program's output; if set to empty this log file will NOT be written
ProgLogPath             = None                  # defined in main
ProgLogFileWOK          = True                  # WOK=Write OK: no further writing on False
ProgLogFilePos          = 0                     # pos in file after last writing
ProgLogFilePosMin       = 0                     # is set by code - minimal pos (about 5000) to be kept in file after start
ProgLogFilePosMax       = 1E6                   # (1M) maximal file size allowed
# ProgLogFilePosMax       = 10000                # for testing
ProgLogFilePhase        = 0                     # Phases from 0 to 3

# printing
PrintIndent             = ""                    # indentation of log msg
PrintCounter            = 0                     # the count of dprint, vprint, xdprint commands

# hardware
computer                = None                  # becomes "Raspi ..." or "Unknown (Not a Raspi Computer)"
isRaspberryPi           = False                 # to be set in main()

# WiFi Server
WiFiServerPort          = 4000                  # allowed from:  1024 ... 65535 (incl.); default is 4000
WiFiIndex               = 0                     # number of WiFi calls
WiFigetmsg              = ""                    # web server msg
WiFiError               = False                 # on a 404
WiFiServer              = None                  # the HTTP Web server
WiFiServerThread        = None                  # thread handle
WiFiServerThreadStop    = None                  # flag to stop thread

# MQTT Broker
IoTconnected            = False                 # needed?
IoTBrokerIP             = "test.mosquitto.org"
IoTBrokerPort           = 1883
IoTBrokerFolder         = "/"
IoTTimeout              = 5
IoTconnectDuration      = ""

iot_client              = None
iot_CallbackID          = None
iot_publishDur          = NAN                   # duration in ms of a publish call until confirmation


# GMC
GMCusage                = False                 # use GMC or not
GMCinit                 = False                 # true if initialized
GMCser                  = None                  # handle
GMCcounterversion       = "Undefined"           # becomes like: 'GMC-300Re 4.54'
GMCtimeout              = "auto"                # timeout in sec for the serial port; default is 1 sec
GMCbytes                = 0                     # 2 or 4 bytes returned on CPM*/CPS* calls; set in init
GMCvarsAll              = GLVarNames[0:6]       # only the first 6 vars can be used for GMC counter
GMCport                 = "auto"                # ports like: '/dev/ttyUSB0' (Linux), 'COM3' (Windows)
GMCbaudrate             = "auto"                # baudrate;     57600:  for the GMC 300 series
                                                #              115200:  for GMC 320, 5XX, 6XX series
GMCvariables            = "auto"                # from one to all of: ['CPM','CPS','CPM1st','CPS1st','CPM2nd','CPS2nd']
                                                # "auto" defaults to ['CPM1st', 'CPS1st', 'CPM2nd', 'CPS2nd']
GMCstoreCounts          = None                  # queue for max of 1 values of CPM from GMC Geiger counter
GMCcallduration         = NAN                   # for testing only: duration of a CPX call

# I2C
I2Cusage                = False                 # use I2C or not
I2Cinit                 = False                 # true if initialized
I2ConRaspi              = False                 # Flag to signal I2C running on Raspi (True) or Simulation (False)
I2Chandle               = None                  # handle for smbus
I2Csensors              = []                    # will be set to e.g. ["LM75B", "BH1750", "GDK101"]

I2CstoreLM75B           = None                  # queue for max of 60 values of Temperature
I2CstoreBME280          = None                  # queue for max of 60 values of Temp, Press, Humid
I2CstoreBH1750          = None                  # queue for max of 60 values of Light
I2CstoreVEML6075        = None                  # queue for max of 60 values of [UV-A, UV-B, other]
I2CstoreLTR390          = None                  # queue for max of 60 values of [visible, UV]
I2CstoreGDK101          = None                  # queue for max of  1 values of CPM from Solid State Geiger counter
I2CstoreSCD30           = None                  # queue for max of  1 values of CPM from Solid State Geiger counter
I2CstoreSCD41           = None                  # queue for max of  1 values of CPM from Solid State Geiger counter

# use from one to or all I2C sensors; use it (True) or not (False)
I2Cusage_LM75B          = False                 # T
I2Cusage_BME280         = True                  # T, P, H
I2Cusage_BH1750         = True                  # Vis
I2Cusage_VEML6075       = False#True                  # UV-A and UV-B, and helper data
I2Cusage_LTR390         = True                  # Vis and UV
I2Cusage_GDK101         = False                 # "Geiger" counts
I2Cusage_SCD30          = False                 # CO2
I2Cusage_SCD41          = False                 # CO2

# define the current I2C address of your sensor
I2Caddr_LM75B           = 0x48                  # options: 0x48 | 0x49 | 0x4A | 0x4B | 0x4C | 0x4D | 0x4E | 0x4F
I2Caddr_BME280          = 0x77                  # options: 0x76 | 0x77 NOTE: Bluedot breakout board has only 0x77; 0x76 is NOT available!
I2Caddr_BH1750          = 0x23                  # options: 0x23 | 0x5C
I2Caddr_VEML6075        = 0x10                  # options: 0x10 | (no other option)
I2Caddr_LTR390          = 0x53                  # options: 0x53 | (no other option)
I2Caddr_GDK101          = 0x18                  # options: 0x18 | 0x19 | 0x1A | 0x1B
I2Caddr_SCD30           = 0x61                  # options: 0x61 | (no other option)
I2Caddr_SCD41           = 0x62                  # options: 0x62 | (no other option)

# sensor LM75B - Temperature
I2Cvars_LM75B      = {"CPS1st":10}

# sensor BME280 - Temperature, (barometric-) Pressure, Humidity
I2Cvars_BME280     = {"Temp":3, "Press":3, "Humid":3}

# sensor BH1750 - Visible light intensity in Lux (recommended: 5 sec avg)
I2Cvars_BH1750     = {"Xtra":1}

# sensor VEML6075 - UV light intensity (UV-A, UV-B, UV-A-corr, UV-B-corr, uvd (dark current), uvcomp1, uvcomp1)
# cI2Cvars_VEML6075   = {"CPM2nd":10, "CPS2nd":10, "CPM3rd":10, "CPS3rd":10, "CPS1st":1, "CPM":10, "CPS":10 }
I2Cvars_VEML6075   = {"CPM2nd":1, "CPS2nd":1, "CPM3rd":1, "CPS3rd":1}

# sensor LTR390 -  Visible light intensity, UV light
I2Cvars_LTR390     = {"CPM":1, "CPS":60 }       # even at cps:10 big fluctuations due to single-digit values

# sensor GDK101 - "Geiger counts by PIN diode"
# all target variables will get same value; avg is ignored
I2Cvars_GDK101     = {"CPS1st":1}

# sensor SCD30 - CO2
I2Cvars_SCD30      = {"Xtra":1}

# sensor SCD41 - CO2
I2Cvars_SCD41      = {"Xtra":1}



# Pulse
Pulseusage              = False                 # use Pulse or not
PulseInit               = False                 # true if initialized
PulseStore              = None                  # empty queue for max of 60 values for last 60 sec of CPS
PulseCount              = 0                     # holds counts within 1 sec period
PulseCountTotal         = 0                     # sum of all counts since start or reset
PulseCountStart         = 0                     # time of start or reset (set in initPulse)
PulseVarsAll            = GLVarNames[0:8]       # only the first 8 CP* vars can be used for Pulse counter
PulseCountPin           = 17                    # the GPIO pulse counting pin in BCM mode used for counting;
                                                # allowed: 5 ... 26;   VERIFY NO CONFLICTING OTHER USAGE ON THIS PIN !!!
                                                # BCM GPIO pin=17 is on BOARD pin=11
PulseVariables          = "auto"                # one or all from ['CPM', 'CPS', 'CPM1st', 'CPS1st', 'CPM2nd', 'CPS2nd', 'CPM3rd', 'CPS3rd']
                                                # but note that all CPM* and CPS*, resp., will be the same!
                                                # i.e.: CPM = CPM1st = CPM2nd = CPM3rd and CPS = CPS1st = CPS2nd = CPS3rd
                                                # "auto" defaults to ['CPM', 'CPS']


# PWM
# to use Raspi PWM output as a fake source for Pulse counting, connect
# BOARD pin 33 (PWM output) with BOARD pin 11 (Pulse counting input)
PWM_usage                = True                 # use PWM or not
PWM_Handle               = None                 # the handle for the PWM settings
PWM_Pin                  = 13                   # the GPIO pin in BCM mode used for generating PWM signal
                                                # BCM GPIO pin=13 is on BOARD pin=33
PWM_Freq                 = 10                   # [Hz] must be > 0.0! start with 10 Hz -> CPS=10 -> CPM=600
                                                #
                                                # on Raspi 4:
                                                # ATTENTION: PWM might be off - looks like it is lower than set to!
                                                # 1000 Hz is far too much; CPM is in the low 50000s (should be 60000)
                                                #  500 Hz is far too much; CPM is in the low 28000s (should be 30000)
                                                #  300 Hz is     too much; CPM is in the low 17200s (should be 18000)
                                                #  100 Hz is     too much; CPM is in the low  5900s (should be  6000)
                                                #   10 Hz is (almost) ok ; CPM is (18h) 508 ... 639 (should be   600)
                                                #                          CPS is (18h)   0 ...  50 (should be    10)
# PWM_DutyCycle          = 5                    # [%]  Duty cycle 0 ... 100 %

period                   = 1 / PWM_Freq    # sec
pulse_length             = 0.00005         # sec, = 50µs
PWM_DutyCycle            = pulse_length / period # duty cycle to result in 50 µs pulse
# print("-"*200)
# print("rglobs: Duty cycle: ", PWM_DutyCycle)
# print("-"*200)


#
# on Raspi 5:
#
# PWMFreq = 10  (Osci: 10.0 Hz)
# Variable  [Unit]       Avg ±StdDev    ±SDev%  Variance     Min ... Max    Recs    Last
# CPM1st  : [CPM]    599.996 ±1.0558    ±0.2%     1.1147     598     602    3505     601
# CPS1st  : [CPS]     10.000 ±0.37883   ±3.8%    0.14351       8      11    3505      10
#
# PWMFreq = 30  (Osci: 29.9 ... 30.1 Hz)
# Variable  [Unit]       Avg ±StdDev    ±SDev%  Variance     Min ... Max    Recs    Last
# CPM1st  : [CPM]   1800.021 ±3.0345    ±0.2%     9.2081    1795    1804    2426    1803
# CPS1st  : [CPS]     30.002 ±0.9758    ±3.3%    0.95218      24      31    2426      30
#
# PWMFreq = 100  (Osci: 100 Hz)
# Variable  [Unit]       Avg ±StdDev    ±SDev%  Variance     Min ... Max    Recs    Last
# CPM1st  : [CPM]   5999.928 ±10.167    ±0.2%     103.37    5987    6011    1477    6009
# CPS1st  : [CPS]     99.999 ±3.1311    ±3.1%     9.8037      80     101    1477     101
#
# PWMFreq = 300  (Osci: 294 ... 303 Hz)
# Variable  [Unit]       Avg ±StdDev    ±SDev%  Variance     Min ... Max    Recs    Last
# CPM1st  : [CPM]  18001.768 ±29.929    ±0.2%     895.76   17961   18040    1334   17969
# CPS1st  : [CPS]    300.000 ±9.2215    ±3.1%     85.036     241     309    1334     241
#
# PWMFreq = 1000  (Osci: 1.00 kHz)
# Variable  [Unit]       Avg ±StdDev    ±SDev%  Variance     Min ... Max    Recs    Last
# CPM1st  : [CPM]  59996.355 ±95.308    ±0.2%     9083.7   59849   60091    1568   59879
# CPS1st  : [CPS]    999.823 ±30.431    ±3.0%     926.02     801    1008    1568    1004
#
# PWMFreq = 3000  (Osci: 3.00 ... 3.02 kHz)
# Variable  [Unit]       Avg ±StdDev    ±SDev%  Variance     Min ... Max    Recs    Last
# CPM1st  : [CPM] 180152.107 ±285.36    ±0.2%      81432 1.797e+05 1.8041e+05     801 1.8034e+05
# CPS1st  : [CPS]   3002.411 ±89.455    ±3.0%     8002.2    2408    3043     801    3015
#
# PWMFreq = 10000  (Osci: 9.95 ... 10.05 kHz)  DIRTY PULSES !!!!
# Variable  [Unit]       Avg ±StdDev    ±SDev%  Variance     Min ... Max    Recs    Last
# CPM1st  : [CPM] 599798.974 ±746.44    ±0.1%   5.5717e+05 5.9777e+05 6.0034e+05     801 6.0007e+05
# CPS1st  : [CPS]   9998.039 ±272.64    ±2.7%      74333    7983   10065     801   10036
#
