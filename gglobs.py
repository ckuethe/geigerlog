#! /usr/bin/env python3
# -*- coding: UTF-8 -*-

"""
gglobs.py - GeigerLog's Super-Global Variables; can be read and modified in all scripts

include in programs with:
    import gglobs
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
__version__         = "1.3.0"             # version of next GeigerLog
#__version__         = "1.3.0pre35"        #


# constants
NAN                 = float('nan')        # 'not-a-number'; used as 'missing value'
                                          # A Julian Day is the number of days since
                                          # Nov 24, 4714 BC 12:00pm Greenwich time in the Gregorian calendar
JULIANUNIX          = 2440587.5416666665  # julianday('1970-01-01 00:00:00') (UNIX time start)
JULIAN111           = 1721425.5 - 1       # julianday('0001-01-01 00:00:00') (matplotlib time start)
                                          # Why this minus 1? strange but needed

# counters
xprintcounter       = 0                   # the count of dprint, vprint, and wprint commands

# messages
python_version      = ""                  # msg wrong Python version
startupProblems     = ""                  # msg configuration file missing or incorrect
configAlerts        = ""                  # msg ALERTs when reading config
notePadSearchText   = ""                  # last entered search text

# pointers
app                 = None                # points to app
exgg                = None                # points to ggeiger
notePad             = None                # points to print into notePad area
logPad              = None                # points to print into logPad area
btn                 = None                # points to the cycle time OK button; for inactivation
plotAudioPointer    = None                # points to the dialog window of plotaudio
plotScatterPointer  = None                # points to the dialog window of plotscatter
plotScatterFigNo    = None                # points to the window number of plotscatter
iconGeigerLog       = None                # points to the QIcon pixmap for 'icon_geigerlog.png'
iconGeigerLogWeb    = None                # points to the 'icon_geigerlog.png' bin files for Web
bboxbtn             = None                # points to button box of GMC_popuo
monitorfig          = None                # points to the fig of Monitor
monitorax           = None                # points to the ax of Monitor
myarr               = None                # arrow of Monitor
monitorFigNo        = None


# sql database
currentConn         = None                # connection to CURRENT database
logConn             = None                # connection to LOGGING database
hisConn             = None                # connection to HISTORY database

# flags
debug               = False               # helpful for debugging, use via command line
debugIndent         = ""                  # to indent printing
verbose             = False               # more detailed printing, use via command line
werbose             = False               # more verbose than verbose
devel               = False               # set some conditions for development CAREFUL !!!
devel1              = False               # =devel  + ADDITIONAL condition: load default db: default.logdb
devel2              = False               # =devel1 + ADDITIONAL condition: make connections
devel3              = False               # =devel2 + ADDITIONAL condition: quicklog
forcelw             = False               # True: line breaks on lines longer than screen
redirect            = False               # on True redirects output from stdout and stderr to file stdlogPath
stopPrinting        = False               # to stop long prints of data
runLogCycleIsBusy   = False               # flag is set when function runLoggingCycle() is busy
LogClickSound       = False               # when true make a click sound on call to runLoggingCycle
startflag           = False               # for start by Web
stopflag            = False               # for stop by Web
plotIsBusy          = False               # makePlot is ongoing
saveplotIsBusy      = False               # makePlot is ongoing
flagGetGraph        = False               # signals to get the graph as bytes
picbytes            = None                # holder for the graph
forceSaving         = False               # save all data that are available even if saving were otherwise delayed

#special flags
testing             = False               # if true then some testing constructs will be activated CAREFUL !!!
graphdemo           = False               # if true then handling of line properties of selected var will be modified for demo
stattest            = False               # when True then display statistics on Normal in Poisson test
test1               = False               # to run a specific test
test2               = False               # to run a specific test
test3               = False               # to run a specific test
test4               = False               # to run a specific test

# dir & file
dataDirectory       = "data"              # the data subdirectory to the program directory
gresDirectory       = "gres"              # where the icons and sounds reside
progName            = None                # program name geigerlog (or geigerlog.py)
progPath            = None                # path to program geigerlog file
dataPath            = None                # path to data dir
gresPath            = None                # path to icons and sounds dir
proglogPath         = None                # path to program log file geigerlog.proglog
stdlogPath          = None                # path to program log file geigerlog.stdlog
configPath          = None                # path to configuration file geigerlog.cfg

logFilePath         = None                # file path of the log file
hisFilePath         = None                # file path of the his file
logDBPath           = None                # file path of the log database file
hisDBPath           = None                # file path of the his database file
currentDBPath       = None                # file path of the current DB file for log or his

binFilePath         = None                # file path of the bin file (GMC device)
datFilePath         = None                # file path of the bin file (Gamma Scout device)
AMFilePath          = None                # file path of the bin file (AmbioMon device, either *CAM or *.CPS file)

activeDataSource    = None                # can be 'Log' or 'His'

fileDialogDir       = None                # the default for the FileDialog starts

HistoryDataList     = []                  # where the DB data are stored by makeHist
HistoryParseList    = []                  # where the parse comments are stored by makeHist
HistoryCommentList  = []                  # where the DB comments are stored by makeHist

manual_filename     = "auto"              # name of the included manual file, like "GeigerLog-Manual-v0.9.93pre17.pdf"
                                          # on 'auto' GL searches for a file beginning with 'GeigerLog-Manual'

# GUI options
window_width        = 1366                # the standard screen of 1366 x 768 (16:9),
window_height       = 768                 #
window_size         = "auto"              # 'auto' or 'maximized'
windowStyle         = "auto"              # may also be defined in config file
displayLastValsIsOn = False               # whether the displayLastValues windows is shown
hidpi               = False               # if true the AA_EnableHighDpiScaling will be applied
hipix               = False               # if true the AA_UseHighDpiPixmaps will be applied
hidpiActivation     = True                # The PyQt5 commands hidpi and hipix will be applied
hidpiScaleMPL       = 100                 # 100 is the default dpi for matplotlib

# Network
# from IEEE specification:
#   "The length of an SSID should be a maximum of 32 characters (32 octets, normally ASCII
#   letters and digits, though the standard itself doesn't exclude values). Some access
#   point/router firmware versions use null-terminated strings and accept only 31 characters."
# NOTE:           1 octet = 1 byte of 8 bits = 1 ASCII character
# Example:
#   WiFiSSID:     max: 32 octets:  123456789:123456789:123456789:12
#   WiFiPassword: max: 63 octets:  pp3456789:pp3456789:pp3456789:pp3456789:pp3456789:pp3456789:pp3
WiFiSSID            = None                # WiFi SSID
WiFiPassword        = None                # WiFi Password

#
# WEB
#
# Monitor WebServer
MonServer           = None                # holds instance of http-server
MonServerAutostart  = True                # MonServer will be autostarted
MonServerActive     = False               # MonServer is activated
MonServerIP         = None                # MonServer IP default
MonServerPort       = None                # Port number on which MonServer listens
MonServerWebPage    = None                # the last web page displayed
MonServerRefresh    = [1, 10, 3]          # the refresh timings for the web pages Monitor, Data, Graph in sec


# DOSE RATE
# For reasons to chose these levels see GeigerLog manual, chapter:
# "On what grounds do we set the radiation safety levels?"
#
DoseRateThreshold   = (0.9, 6.0)          # µSv/h Threshold green-to-yellow and yellow-to-red
DoseRateColors      = ( '#00C853',        # Google color green
                        '#ffe500',        # Google color yellow
                        '#EA4335',        # Google color red
                      )


MWSThread           = None
MWSThreadTarget     = None
MWSThreadStop       = None

# Radiation World Map
RWMmapActivation    = False               # Radiation World Map Activation
RWMmapUpdateCycle   = 60                  # Radiation World Map Update Cycle in minutes
RWMmapVarSelected   = "CPM"               # name of the variable used to update Radiation world Map
RWMmapLastUpdate    = None                # time of the last update of Radiation World Map

gmcmapUserID        = None                # User Id for GMC's gmcmap
gmcmapCounterID     = None                # Counter Id for GMC's gmcmap

# # Telegram
# TelegramToken       = None                # Telegram Token
# TelegramActivation  = False               # Telegram Activation
# TelegramUpdateCycle = 60                  # Telegram Update Cycle in minutes
# TelegramLastUpdate  = 0                   # time of the last update of Telegram
# TelegramBot         = None                # pointer to instance of Telegram Bot
# TelegramChatID      = None                # Telegram Bot Chat ID


## Serial ports
    # import serial :
    # pyserial Parity parameters
    #   serial.PARITY_NONE    = N
    #   serial.PARITY_EVEN    = E
    #   serial.PARITY_ODD     = O
    #   serial.PARITY_MARK    = M
    #   serial.PARITY_SPACE   = S
    #
    # finding pyserial supported parameters:
    # myser = serial.Serial()
    # myser           : Serial<id=0x7f7a05b18d68, open=False>(port=None, baudrate=9600, bytesize=8, parity='N',
    #                   stopbits=1, timeout=None, xonxoff=False, rtscts=False, dsrdtr=False)
    # myser.BAUDRATES : 50, 75, 110, 134, 150, 200, 300, 600, 1200, 1800, 2400, 4800, 9600,
    #                   19200, 38400, 57600, 115200, 230400, 460800, 500000, 576000, 921600,
    #                   1000000, 1152000, 1500000, 2000000, 2500000, 3000000, 3500000, 4000000
    # myser.BYTESIZES : 5, 6, 7, 8
    # myser.PARITIES  : 'N', 'E', 'O', 'M', 'S'
    # myser.STOPBITS  : 1, 1.5, 2

# EmfDev: "GMC wird immer CH340 chip benutzen"
    # from: http://www.gqelectronicsllc.com/forum/topic.asp?TOPIC_ID=9784
    # EmfDev:
    #   Yes we are using the CH340 chip so far with all GMC-300+ and 500+ devices. And just check with our
    #   latest one also has the VID:PID=0x1a86:0x7523
    # gmc300E+ (von Jan 21)   device:       /dev/ttyUSB0    description:  USB Serial    vid:  0x1a86     pid:  0x7523
    # gmc300E+ (von ???   )   device:       /dev/ttyUSB0    description:  USB2.0-Serial vid:  0x1A86     pid:  0x7523
    # gmc500+  (2018?)        device:       /dev/ttyUSB0    description:  USB2.0-Serial vid:  0x1a86     pid:  0x7523
    # all 3 devices: chip = CH340C
    # manufacturer: http://wch-ic.com/   http://wch-ic.com/products/CH340.html
    # Nanjing Qinheng Microelectronics Co., Ltd.
    # Main brand： WinChipHead (WCH)
    # "Full speed USB device interface, USB 2.0 compatible."
    # CH340 supports common baud rate: 50, 75, 100, 110, 134.5, 150, 300, 600, 900, 1200, 1800, 2400, 3600, 4800, 9600, 14400, 19200,
    # 28800, 33600, 38400, 56000, 57600, 76800, 115200, 128000, 153600, 230400, 460800, 921600, 1500000, 2000000 etc.

GMCbaudrates        = [57600, 115200]
I2Cbaudrates        = [115200]
GSbaudrates         = [2400, 9600, 460800]

# Serial port for GMC devices
GMCser              = None                # GMC serial port pointer
GMC_baudrate        = 115200              # will be overwritten by a setting in geigerlog.cfg file
GMC_usbport         = '/dev/ttyUSB0'      # will be overwritten by a setting in geigerlog.cfg file
GMC_timeout         = "auto"              # will be overwritten by a setting in geigerlog.cfg file
GMC_timeout_write   = "auto"              # will be overwritten by a setting in geigerlog.cfg file
GMC_ttyS            = "ignore"            # to 'ignore' or 'include' '/dev/ttySN', N=1,2,3,... ports on USB Autodiscovery

# Serial port for I2C devices
I2Cser              = None                # not used! is used Domgle-specific
I2Cbaudrate         = 115200              # is used as fixed value
I2Cusbport          = '/dev/ttyUSB1'      # will be overwritten in code
I2Ctimeout          = 3                   # will be overwritten by a setting in geigerlog.cfg file
I2Ctimeout_write    = 1                   # will be overwritten by a setting in geigerlog.cfg file
I2CttyS             = "ignore"            # to 'ignore' or 'include' '/dev/ttySN', N=1,2,3,... ports on USB Autodiscovery

# Serial port for Gamma-Scout devices
# NOTE: some responses of Gamma-Scout take almost 1 sec, timeout setting must be well above 1 sec limit!
GSser               = None                # Gamma-Scount serial port pointer
GSbaudrate          = 9600                # will be overwritten by a setting in geigerlog.cfg file
GSusbport           = '/dev/ttyUSB2'      # will be overwritten by a setting in geigerlog.cfg file
GStimeout           = 3                   # will be overwritten by a setting in geigerlog.cfg file
GStimeout_write     = 3                   # will be overwritten by a setting in geigerlog.cfg file
GSttyS              = "ignore"            # to 'ignore' or 'include' '/dev/ttySN', N=1,2,3,... ports on USB Autodiscovery
GSstopbits          = 1                   # generic in pyserial;     will not change in code
GSbytesize          = 7                   # specific to Gamma-Scout; will not change in code
GSparity            = "E"                 # specific to Gamma-Scout; will not change in code


## SENSITIVITY

###############################################################################
## Beginning with version GeigerLog 1.0 the 'Calibration' is replaced with
## 'Sensitivity', which is defined as the inverse of the previous definitions,
## i.e. 0.0065 µSv/h/CPM becomes 1/0.065 => 153.85 CPM/(µSv/h).
## This is rounded to 154 CPM/(µSv/h) to use no more than 3 valid digits.
## For reasons for this change see the GeigerLog manual, but in short a tube with
## a higher number for Sensitivity now does have a higher sensitivity!
###############################################################################

# The GMC factory default so-called calibration factor is linear, i.e. the same
# for all 3 calibration points defined in a GMC counter. For a M4011 tube the
# calibration factor implemented in firmware is 0.0065 µSv/h/CPM.
#
# For the 2nd tube in a GMC500+ device, different factors were seen:
# E.g.: from a calibration point #3 setting of '25 CPM=4.85µSv/h' the calibration
# factor is 0.194 µSv/h/CPM. While a calibration point #3 setting of '25CPM=9.75µSv/h'
# results in 0.39 µSv/h/CPM!
#
# However, these are significantly different from calibration factors determined
# in my own experiments as reported here:
# http://www.gqelectronicsllc.com/forum/topic.asp?TOPIC_ID=5369, see Reply #10,
# Quote: “With Thorium = 0.468, and K40 = 0.494, I'd finally put the sensitivity
# of the 2nd tube, the SI3BG, to 0.48 µSv/h/CPM, which makes it 74 fold less
# sensitive than the M4011!”
#
# Others report even poorer values for the SI3BG:
# https://www.gqelectronicsllc.com/forum/topic.asp?TOPIC_ID=5554, Reply #17
# "The new correction factor for the primarily gamma tube is .881CPM/uSv/h or 1.135."
# This means sensitivity of that (2nd) tube = 1.135 µSv/h/CPM


# Default Sensitivity
# Up to 4 tubes can be configured. They are defined here and may be redefined in config.
# They may be used in any device, but in the GMC counters their meaning is fixed:
# Tube #0 : used with CPM, CPS
# Tube #1 : used with CPM1st, CPS1st
# Tube #2 : used with CPM2nd, CPS2nd
# Tube #3 : used with CPM3rd, CPS3rd
#
# Special associations in a GMC counter:
# Tube #0       Default tube in all GMC counters;
#               in a GMC-500+ counter this gives the sum of 1st and 2nd tube (meaningless value).
# Tube #1       in all GMC counters exactly the same as tube #0 except in a GMC-500+;
#               in a GMC-500+ counter this is the 1st or high sensitivity tube.
# Tube #2       in all GMC counters exactly the same as tube #1 except in a GMC-500+;
#               in a GMC-500+ counter this is the 2nd or low-sensitivity tube.
# Tube #3       not used in GMC counters.


# Sensitivity of the tubes
DefaultSens         = [None] * 4
Sensitivity         = [None] * 4

DefaultSens[0]      = 154                 # CPM/(µSv/h)   (= 0.0065 in units of µSv/h/CPM)
DefaultSens[1]      = 154                 # CPM/(µSv/h)   (= 0.0065 in units of µSv/h/CPM)
DefaultSens[2]      = 2.08                # CPM/(µSv/h)   (= 0.48   in units of µSv/h/CPM)
DefaultSens[3]      = 154                 # CPM/(µSv/h)   (= 0.0065 in units of µSv/h/CPM)

# set Sensitivity[Tube No]
for i in range(4):
    Sensitivity[i]  = DefaultSens[i]


# GMC
# details will be set after reading the version of the counter from the device
GMCDeviceName       = None                # to be detected in init; generic name like: "GMC Device"
GMCDeviceDetected   = "None"              # will be replaced after connection with full specific
                                          # name as detected, like 'GMC-300Re 4.20',
                                          # had been 14 chars fixed, can now be longer
GMC_variables       = "auto"              # which variables are natively supported
GMCLast60CPS        = None                # storing last 60 sec of CPS values
GMCEstFET           = None                # storing last 60 sec of CPS values for estimating the FET effect

# GMC Bugs and settings
GMC_memory          = "auto"              # Can be configured for 64kB or 1 MB in the config file
GMC_SPIRpage        = "auto"              # size of page to read the history from device
GMC_SPIRbugfix      = "auto"              # if True then reading SPIR gives one byte more than requested  (True for GMC-300 series)
GMC_locationBug     = "auto"              # --> ["GMC-500+Re 1.18","GMC-500+Re 1.21"], see the FIRMWARE BUGS topic in the configuration file
GMC_FastEstTime     = "auto"              # if != 60 then false data will result
GMC_endianness      = "auto"              # big- vs- little-endian for calibration value storage
GMC_configsize      = "auto"              # 256 bytes in 300series, 512 bytes in 500/600 series
GMC_voltagebytes    = "auto"              # 1 byte in the 300 series, 5 bytes in the 500/600 series
GMC_nbytes          = "auto"              # the number of bytes ( 2 or 4) from the CPM and CPS calls, as well as the calls to 1st and 2nd tube
GMC_cfg             = None                # Configuration bytes of the counter. 256 bytes in 300series, 512 bytes in 500, 600 series
GMC_WifiIndex       = 0                   # the index column in cfgKeyHigh applicable for the current device
GMC_WifiEnabled     = False               # does the counter have WiFi or not
GMC_WiFiIsON        = False               # is WiFi switched ON at the counter (if the counter is wifi enabled)
GMC_DualTube        = "auto"              # all are single tube, except 500, 500+, which ares double tube
GMC_savedatatype    = "Unknown - will become known once the device is connected"
GMC_savedataindex   = 1


# AudioCounter
AudioDevice         = None                # audiocard; to be set in init to (None, None) (could be USB, 9 and other)
AudioLatency        = "auto"              # to be set in init to (1.0, 1.0) sec latency
AudioPulseMax       = None                # +/- 32768 as maximum pulse height for 16bit signal
AudioPulseDir       = None                # False for negative; True for positive pulse
AudioThreshold      = None                # Percentage of pulse height to trigger a count
                                          # 60% of +/- 32768 => approx 20000
AudioRate           = None                # becomes 44100:  sampling rate audio; works for most sound cards
AudioChunk          = None                # becomes 32:     samples per read
AudioChannels       = None                # becomes (1,1):  1= Mono, 2=Stereo
AudioFormat         = None                # becomes (int16, int16): signed 16 bit resolution

AudioLastCpm        = 0                   # audio clicks CPM
AudioLastCps        = 0                   # audio clicks CPS
AudioLast60CPS      = None                # np array storing last 60 sec of CPS values
AudioThreadStop     = False               # True to stop the audio thread
AudioSensitivity    = "auto"              # sensitivity of the used tube
AudioMultiPulses    = None                # stores the concatenated audio data for plotting
AudioRecording      = None                # stores the Recording
AudioPlotData       = None                # stores the data to be plotted
AudioOei            = None                # the eia storage label
AudioVariables      = "auto"              #


# RadMon
RMServerIP          = "auto"              # MQTT server IP, to which RadMon sends the data
RMServerPort        = "auto"              # Port of the MQTT server, defaults to 1883
RMServerFolder      = "auto"              # The MQTT folder as defined in the RadMon+ device
RMSensitivity       = "auto"              # sensitivity of the used tube
RMVariables         = "auto"              # a list of the variables to log, like: CPM3rd, Temp, Press, Humid,
RMTimeout           = 5                   # waiting for "successful connection" confirmation
RMCycleTime         = 1                   # cycle time of the RadMon device
RMconnect           = (-99, "")           # flag to signal connection
RMdisconnect        = (-99, "")           # flag to signal dis-connection

rm_client           = None                # to be set in gdev_radmon.initRadMon
rm_cpm              = None                # temporary storage for CPM
rm_temp             = None                # temporary storage for Temperature
rm_press            = None                # temporary storage for Pressure
rm_hum              = None                # temporary storage for Humidity
rm_rssi             = None                # temporary storage for RSSI


# AmbioMon
AmbioServerIP       = "auto"              # server Domain name or IP to which AmbioMon connects
AmbioSensitivity    = "auto"              # sensitivity of the used tube
AmbioDataType       = "auto"              # "LAST" or "AVG" for lastdata or lastavg
AmbioTimeout        = "auto"              # waiting for successful connection
AmbioVariables      = "auto"              # a list of the variables to log

# settings for the remote AmbioMon device
AmbioCPUFrequency   = 0                   # read-only for the ESP32 CPU frequency
AmbioManualValue    = 0                   # a value entered manually
AmbioVoltage        = 444.44              # voltage of the GM tube in the AmbioMon
AmbioCycletime      = 1                   # cycle time of the AmbioMon device
AmbioFrequency      = 1500                # frequency of driving HV generator
AmbioPwm            = 0.5                 # Pulse Width Modulation of HV generator
AmbioSav            = "Yes"               # Switching into saving mode (Yes/No)


# Gamma-Scout
GSSensitivity       = "auto"              # auto will become 108 for the LND712 tube in GS init
GStype              = None                # to be set in GS init as: Old, Classic, Online
GSFirmware          = None                # to be set in GS init
GSSerialNumber      = None                # to be set in GS init
GSDateTime          = None                # to be set when setting DateTime
GSusedMemory        = 0                   # to be set when calling History
GSMemoryTotal       = 65280               # max memory acc to manual, page 16, but when mem was 64450 (830 bytes free), interval was already 7d!
GSCalibData         = None                # the Gamma-Scout internal calibration data
GScurrentMode       = None                # "Normal", "PC", "Online"
GStesting           = False               # required to run GS under simulation; used only in module gdev_gscout.py,
GSVariables         = "auto"


# I2C
I2C_IOWDriverLoaded = False                # Is the driver loaded? relevant only for IOW dongle
I2CDongle           = None                 # becomes instance of the I2C Dongle
I2CDongleCode       = None                 # becomes name of the I2C Dongle, like ISS, ELV, IOW
I2CVariables        = None                 # is set with the config of the sensors
I2CInfo             = None                 # Info, to be set in init
I2CInfoExt          = None                 # Info Extended, to be set in init
Sensors             = None                 # is set by gedev_i2c

# I2C Sensors
I2CSensor           = {}                   # collector for sensors
I2CSensor["LM75"]   = [False, 0x48, None]  # use the Sensor LM75   (T) at addr 0x48
I2CSensor["BME280"] = [False, 0x76, None]  # use the Sensor BME280 (T, P, H) at addr 0x76
I2CSensor["SCD30"]  = [False, 0x61, None]  # use the Sensor SCD30  (CO2 by NDIR) at addr 0x61
I2CSensor["SCD41"]  = [False, 0x62, None]  # use the Sensor SCD41  (CO2 by Photoacoustic) at addr 0x62
I2CSensor["TSL2591"]= [False, 0x29, None]  # use the Sensor TSL2591(Light) at addr 0x29


# LabJack
LabJackActivation   = False                # Not available if False
LJimportLJP         = False                # LabJackPython module was imported
LJimportU3          = False                # LabJack' U3 module was imported
LJversionLJP        = "not in use"         # version of LabJackPython
LJversionU3         = "not in use"         # version of U3
LJVariables         = "auto"               # a list of the variables to log; auto=Temp, Humid, Xtra

# EI1050 probe for Labjack
LJEI1050Activation  = False                # Not available if False
LJEI1050version     = "not in use"         # version of EI1050
LJimportEI1050      = False                # LabJack' EI1050 module was imported
LJEI1050status      = None                 # Status of probe EI1050


# MiniMonCounter
MiniMonActivation   = False                # Not available if False
MiniMonOS_Device    = "auto"               # OS device, like /dev/hidraw3
MiniMonInterval     = "auto"               # interval between forced savings
MiniMonVariables    = "auto"               # default is Temp, Xtra


# Simul Device
SimulActivation     = False                # Not available if False
SimulMean           = "auto"               # mean value of the Poisson distribution as CPSmean=10
SimulSensitivity    = "auto"               # sensitivity of the used tube
SimulDeadtime       = "auto"               # units: µs
SimulPredictive     = False                # not making a CPM prediction
SimulPredictLimit   = 25                   # CPM must reach at least this count before making prediction
SimulVariables      = "auto"               # default is CPM3rd, CPS3rd


# Manu
ManuActivation      = False                # Not available if False
ManuSensitivity     = "auto"               # sensitivity of the used tube
ManuVariables       = "auto"               # default is "CPM3rd, CPS3rd"
ManuValues          = 0                    # number of variables used in Manu (<= 12)
ManuValue           = [NAN] * 12           # up to 12 manually entered values


# WiFiServer
WiFiServerActivation     = False           # Not available if False
WiFiServerIP             = "auto"          # server Domain name or IP to which WiFiServer connects
WiFiServerPort           = "auto"          # the port for IP:Port
WiFiServerFolder         = "auto"          # thr folder for IP:Port/folder; default: geigerlog
WiFiServerSensitivity    = "auto"          # sensitivity of the used tube
WiFiServerDataType       = "auto"          # "LAST" or "AVG" for lastdata or lastavg
WiFiServerTimeout        = "auto"          # waiting for successful connection
WiFiServerVariables      = "auto"          # a list of the variables to log


# WiFiClient
WiFiClientActivation     = False           # Not available if False
WiFiClientIP             = "auto"          # server Domain name or IP on which GL listens
WiFiClientPort           = "auto"          # server port on which GL listens
WiFiClientSensitivity    = "auto"          # sensitivity of the used tube
WiFiClientType           = "Generic"       # options are "Generic" or "GMC"
WiFiClientVariables      = "auto"          # a list of the variables to log


#ESP32
ESP32Serial         = None                 # for the ESP32


# Logging settings
logging             = False                # flag for logging
logCycle            = 3                    # time in seconds between calls in logging

# History Options
keepFF              = False                # Flag in startup-options
                                           # Keeps all hexadecimal FF (Decimal 255) values as a
                                           # real value and not an 'Empty' one. See manual in chapter
                                           # on parsing strategy
fullhist            = False                # If False breaks history recording when 8k FF is read
                                           # if True reads the whole history from memory

# Graphic Options
allowGraphUpdate    = True                 # to block updates on reading data

Xleft               = None                 # time min if entered
Xright              = None                 # time max if entered
Xunit               = "Time"               # time unit; can be Time, auto, second, minute, hour, day
XunitCurrent        = Xunit                # current time unit

Ymin                = None                 # CPM min if entered
Ymax                = None                 # CPM max if entered
Yunit               = "CPM"                # CPM unit; can be CPM, CPS, µSv/h
YunitCurrent        = Yunit                # current count unit

Y2min               = None                 # Ambio min if entered
Y2max               = None                 # Ambio max if entered
Y2unit              = "Amb"                # Ambio unit °C or °F
Y2unitCurrent       = Yunit                # current Ambio unit

avgChecked          = False                # Plot the lines Average, +/- 95% confidence, and Legend with average +/- StdDev value
mavChecked          = False                # Plot the Moving Average line, and Legend with MovAvg length ins seconds and data points
fitChecked          = False                # Plot a fit to the data of the selected variable
mav_initial         = 60                   # length of Moving Average period in seconds
mav                 = mav_initial          # currently selected mav period
printMavComments    = False                # print to NotePad the Moving Average Comments

# Plotstyle                                # placeholder; don't change here - is set in config
linestyle           = 'solid'              # overwritten by varsCopy
linecolor           = 'blue'               # overwritten by varsCopy
linewidth           = '1.0'                # configurable in geigerlog.cfg
markersymbol        = 'o'                  # configurable in geigerlog.cfg
markersize          = '15'                 # configurable in geigerlog.cfg

#Graph Y-Limits                            # to calculate cursor position for left, right Y-axis
y1_limits           = (0, 1)               # (bottom, top) of y left
y2_limits           = (0, 1)               # (bottom, top) of y right

# Data arrays and values
logTime             = None                 # array: Time data from total file
logTimeDiff         = None                 # array: Time data as time diff to first record in days
logTimeFirst        = None                 # value: Time of first record of total file

logTimeSlice        = None                 # array: selected slice out of logTime
logTimeDiffSlice    = None                 # array: selected slice out of logTimeDiff
logSliceMod         = None

sizePlotSlice       = None                 # value: size of plotTimeSlice

logDBData           = None                 # 2dim numpy array with the log data
hisDBData           = None                 # 2dim numpy array with the his data
currentDBData       = None                 # 2dim numpy array with the currently plotted data

#
# DEVICES
#
# supported devices with all attribs
#   Detected Names      : more specific names, like 'GMC-500+Re 1.22'
#   Varnames            : a list (pytype: list) of varnames set for this device, like:
#                         ['CPM', 'CPS', 'CPM1st', 'CPS1st', 'Temp', 'Press', 'Humid', 'Xtra']
#   Activation Status   : True if set in config file
#   Connection Status   : True if connected
Devices = {
           # Device-        Detected-    Var-        Activation-  Connection-
           # Name           Names        Names       Status       Status
           #                0            1           2            3
           #                DNAME        VNAME       ACTIV        CONN
            "GMC"        : [None,        None,       False,       False],    # 1
            "Audio"      : [None,        None,       False,       False],    # 2
            "RadMon"     : [None,        None,       False,       False],    # 3
            "AmbioMon"   : [None,        None,       False,       False],    # 4
            "GammaScout" : [None,        None,       False,       False],    # 5
            "I2C"        : [None,        None,       False,       False],    # 6
            "LabJack"    : [None,        None,       False,       False],    # 7
            "MiniMon"    : [None,        None,       False,       False],    # 8
            "Simul"      : [None,        None,       False,       False],    # 9
            "Manu"       : [None,        None,       False,       False],    # 10
            "WiFiClient" : [None,        None,       False,       False],    # 11
            "WiFiServer" : [None,        None,       False,       False],    # 12
          }

# columns Naming
DNAME = 0    # Detected Name
VNAME = 1    # Variable names as CSV list
ACTIV = 2    # Activation status
CONN  = 3    # Connection status

# count of DEVICES
DevicesActivated    = 0                   # count of activated devices; determined upon connecting
DevicesConnected    = 0                   # count of connected devices; determined upon connecting

#
# VARIABLES - names and style
#
# colors at:  https://matplotlib.org/users/colors.html
# linestyles: "solid", "dotted"
# NOTE: Medium Names became necessary for the database when the (Short) names for T, P, H, X were changed to Temp, etc
varsDefault = { # do not modify this - use copy varsCopy !!!!
#                                                        Units
#            (Short)     Long             Very short     CP* can be µSv/h     Style            Style       Medium
#            Names,      Names,           Names          T °C can be °F       Color            Line        Names
#            key         0                1              2                    3                4           5
            "CPM"    : ["CPM",           "M",           "CPM",               "blue",          "solid",     "CPM"    ],    # 1
            "CPS"    : ["CPS",           "S",           "CPS",               "magenta",       "solid",     "CPS"    ],    # 2
            "CPM1st" : ["CPM1st",        "M1",          "CPM",               "deepskyblue",   "solid",     "CPM1st" ],    # 3
            "CPS1st" : ["CPS1st",        "S1",          "CPS",               "violet",        "solid",     "CPS1st" ],    # 4
            "CPM2nd" : ["CPM2nd",        "M2",          "CPM",               "cyan",          "solid",     "CPM2nd" ],    # 5
            "CPS2nd" : ["CPS2nd",        "S2",          "CPS",               "#9b59b6",       "solid",     "CPS2nd" ],    # 6 color: dark violet
            "CPM3rd" : ["CPM3rd",        "M3",          "CPM",               "brown",         "solid",     "CPM3rd" ],    # 7
            "CPS3rd" : ["CPS3rd",        "S3",          "CPS",               "orange",        "solid",     "CPS3rd" ],    # 8
            "Temp"   : ["Temperature",   "T",           "°C",                "red",           "solid",     "T"      ],    # 9
            "Press"  : ["Pressure",      "P",           "hPa",               "black",         "solid",     "P"      ],    # 10
            "Humid"  : ["Humidity",      "H",           "%",                 "green",         "solid",     "H"      ],    # 11
            "Xtra"   : ["Xtra",          "X",           "x",                 "#8AE234",       "solid",     "X"      ],    # 12 color: lighter green
          }

# Index,       DateTime,     CPM,     CPS,  CPM1st,  CPS1st,  CPM2nd,  CPS2nd,  CPM3rd,  CPS3rd,  Temp,   Press,   Humid,   Xtra
# Column No    0             1        2     3        4        5        6        7        8        9       10       11       12
datacolsDefault         = 1 + len(varsDefault) # total of 13: DateTime plus 12 vars (index excluded; is not data),
varsCopy                = varsDefault.copy()   # need a copy to allow reset as colorpicker may change color

varAllFalse             = {}
varAllEmpty             = {}
devAllNone              = {}

lastLogValues           = {}                 # last log values received from devices

LogReadings             = 0                  # number of readings since last logging start; prints as index in log
runLogCycleDelta        = (0, "")            # the time delta in sec between start and finish of runLoggingCycle, and timing message

for vname in varsCopy:
    varAllFalse  [vname] = False              # set all False
    varAllEmpty  [vname] = ""                 # set all empty
    lastLogValues[vname] = NAN                # set all values to NAN

for devname in Devices:
    devAllNone[devname] = None               # set all None

# HOUSEKEEPING for VARIABLES
varsSetForCurrent       = varAllFalse.copy()  # variable is active in the current data set
varsSetForLog           = varAllFalse.copy()  # variable is active in the current Log
varsSetForHis           = varAllFalse.copy()  # variable is active in the current His

varChecked4PlotLog      = varAllFalse.copy()  # is variable checked for showing in plot for Log
varChecked4PlotHis      = varAllFalse.copy()  # is variable checked for showing in plot for History

varMap                  = varAllFalse.copy()  # holds mapping of the variables

varStats                = varAllEmpty.copy()  # info on avg, StdDev etc; will be set in gsup_plot, used for SuSt and tip for vars

DevVarsAsText           = devAllNone.copy()   # determined in switchAllConnections, Devices with associated variables

varMappedCount          = 0                   # determined in switchAllConnections; at least 1 needed for logging


# SCALING
# reset all vars to "no scaling"
#
# Value - Scaling - this modifies the measured variable;
# any modification will be stored to Database
ValueScale           = {}
for vname in varsCopy:  ValueScale[vname] = "VAL"
#
# Graph Sscaling - this does ONLY modify how the data is plotted
# any modification will NOT be stored to Database
GraphScale           = {}
for vname in varsCopy:  GraphScale[vname] = "VAL"


# HELP DETAILS

helpOptions = """
Usage:  geigerlog [Options] [Commands]

Options:
    -h, --help          Show this help and exit.
    -d, --debug         Run with printing debug info.
                        Default is debug = False
    -v, --verbose       Be more verbose.
                        Default is verbose = False.
    -w, --werbose       Be much more verbose.
                        Default is werbose = False.
    -V, --Version       Show version status and exit.
    -P, --Portlist      Show available USB-to-Serial ports
                        and exit.
    -R  --Redirect      Redirect stdout and stderr to
                        file geigerlog.stdlog (for debugging).
    -s  --style name    Sets the style; see also manual and
                        Command: 'showstyles'.
                        Default is set by your system

Commands:
    showstyles          Show a list of styles available on
                        your system and exit. For usage details see manual.
    keepFF              GMC counter only: Keeps all hexadecimalFF (Decimal 255)
                        values as a real value and not an 'Empty' one. See
                        manual in chapter on parsing strategy.

By default, data files will be read-from / written-to the data directory
"data", which is a subdirectory to the program directory.

To watch debug and verbose output, start the program from the
command line in a terminal. The output will print to the terminal.

With the Redirect option all output - including Python error
messages - will go only into the redirect file geigerlog.stdlog.
"""

helpQuickstart = """
<!doctype html>
<style>
    h3          { color: darkblue; margin:10px 0px 5px 0px; padding:0px; }
    p, ol, ul   { margin:8px 0px 4px 0px; padding:0px;}
</style>

<H3>Mouse Help</H3>
<p>Resting your mouse cursor briefly over an item of the
window shows a ToolTip message providing info on the item!

<h3>Connecting your Devices</h3>
<p>Assure that the required wired or wireless setup (USB cable, Audio cable, WiFi) is made.
Then connect GeigerLog with the devices via menu: <b>Device -> Connect Devices</b> or
click the <b>Connect</b> toolbar icon.

<h3>Plug and Play</h3>
<p>With a proper setup all devices should be auto-configurable by GeigerLog. However, this may fail on
new hardware. In this case read about <b>USB Autodiscovery</b> in chapter Appendix B of the manual.

<h3>Start Logging</h3>
<p>This will create a database file to store newly acquired data from the devices.</p>
<ol>
<li>GMC device only: Switch device power on<br>(menu: <b>Device -> GMC Series -> Switch Power ON</b>))</li>
<li>Load a log file<br>(menu: <b>Log -> Get Log File or Create New One</b>)<br>
In the Get Log File dialog enter a new filename and press Enter,
or select an existing file to <b>APPEND</b> new data to this file.</li>
<li>Start logging<br>(menu: <b>Log -> Start Logging</b>, or click the <b>Start Log</b> toolbar icon)</li>
</ol>

<h3>Get History</h3>
<p>This will create a database file to store all data downloaded from the internal storage of a device.</p>
<ol>
<li>Get history from device<br>(menu: <b>History -> &lt;Your device&gt; -> Get History from Device</b>)</li>
<li>Enter a new filename (e.g. enter 'myfile' and press Enter) or select an existing file
<br>Note: selecting an existing file will <b>OVERWRITE</b> this file!</li>
</ol>

<h3>Graphical Analysis</h3>
<p>To zoom into the graph either enter the Time Min and
Time Max values manually, or, much easier, do a mouse-left-click to the left
of the feature in the graph and right-click to the right, and then click the Apply button.</p>

<p>Use other features as detailed in the manual.</p>

<h3>GeigerLog Manual</h3>
<p>Available locally (menu: <b>Help -> GeigerLog Manual</b>) and <a href="https://sourceforge.net/projects/geigerlog/files/">online</a>
at SourceForge project GeigerLog: <a href="https://sourceforge.net/projects/geigerlog/">https://sourceforge.net/projects/geigerlog/</a></p>
"""


helpFirmwareBugs = """
<!doctype html>
<style>
    h3              { color: darkblue; margin:5px 0px 5px 0px; padding:0px; }
    p, ol, ul, li   { margin:4px 0px 10px 0px; padding:0px;}
    td, th          { padding: 0px 30px 0px 0px;}
</style>

<h3>Firmware bugs in some devices</h3>

<p><b>Device: GMC-500+</b></p>

<p>When this device is on firmware 1.18 it identifies itself with an empty identifier,
which prohibits use on GeigerLog. It should identify itself as 'GMC-500+Re 1.18'.</p>

<p>A work-around is to cycle the connection: ON -> OFF -> ON. Then it should work.</p>

<p>This bug is corrected with firmware 1.21. It is recommended to contact GMC support for an update.
The Geiger counter will then identify itself as 'GMC-500+Re 1.21'.</p>
<p>-------------------------------------------------------------------------------</p>
<p><b>Device: GMC-500 / 600 series</b></p>

<p>Some firmware versions, at least 1.18 and 1.21, have a bug (called 'location bug') which
results in errors in the parsing of the <b>history</b> file. It is advised to upgrade at least to
the 1.22 firmware!</p>
<p>-------------------------------------------------------------------------------</p>

<p><b>"Fast EstimateTime"</b></p>

<p>This mode is active by default in its worst setting! It invokes an algorithm
 - not disclosed by GQ - which results in a severe distortion of all CPM
 recordings, and may even create counts when there are none.</p>

<p>Present as a configuration setting in Device GMC-500+ version 2.24 and
likely in all other models with a firmware supporting this mode.</p>

<p>It has settings of 60, 30, 20, 15, 10 and 5 seconds, plus a 'dynamic' setting,
which apparently simply stands for 3 seconds. The latter is the default and the
worst setting.</p>

<p>It looks like this algorithm is switched off at 60 seconds, therefore that
setting is strongly recommended! GeigerLog gives a warning when a GMC counter is
activated with this setting at anything besides 60 seconds.</p>

<p>A firmware correction has NOT been announced.</p>
"""


helpWorldMaps = """
<!doctype html>
<style>
    h3          { color: darkblue; margin:5px 0px 5px 0px; padding:0px; }
    p, ol, ul   { margin:4px 0px 8px 0px; padding:0px;}
</style>

<H3>Radiation World Maps</H3>

<p>Several web sites exist which attempt to show a worldwide map of the
<b>BACKGROUND</b> radioactivity, hoping to be of help to the people in case of
a nuclear emergency, which will result in elevated levels of radioactivity.
Some are run by governments, others by enthusiastic hobbyists.</p>

<p>Among the latter ones are:</p>
<ul>
<li><a href='http://www.gmcmap.com/' >gmcmap.com</a> - This is the one supported by GQ Electronics</li>
<li><a href='https://radmon.org/index.php' >radmon.org</a> - Opened again after hacking episode</li>
<li><a href='https://blog.safecast.org/' >safecast.org</a> - Accepting radiation as well as air quality data</li>
</ul>

<p>Currently only GQ's GMCmap is supported by GeigerLog; others may follow.</p>

<p>GQ suggests to use your Geiger counter (versions with WiFi, i.e.
GMC-320+V5, GMC-500, GMC-600 series) to directly update their website.
See the GeigerLog manual for why this is actually not such a good idea.</p>

<p>But you can also support their worldmap using GeigerLog, and not only
provide more meanigful data, but use any of their non-WiFi counters just as
well.</p>

<p>If you want to contibute to <a href='http://www.gmcmap.com/' >gmcmap.com</a>,
you need to register there.
This provides you with a UserID and a CounterID. Enter both into the
respective fields in the GeigerLog configuration file 'geigerlog.cfg' under
the heading 'Worldmaps'. That's it!</p>

<p>Click the toolbar icon 'Map' and you'll be presented with a dialogue box,
allowing you to configure how you send your data to the map. Obviously, for this to
succeed you need to have an active internet connection at your computer!</p>

<p>You will see a confirmation printed to GeigerLog's NotePad area.<br></p>

<H3>A word of caution:</H3>
<p>As far as I can see there is no quality control of the data! Nothing
prevents users from putting a strong radioactive source in front of their detector,
and pushing these data to the web. In fact, you don't even need a counter, and
don't even need GeigerLog, but can enter any data you wish manually!
Also, there does not seem to be a way to re&shy;tract any inadvertently
sent data. Poor data will quickly destroy any value of those sites.</p>

<p>Even more subtle things may reduce the value of those websites: Geiger
counter readings fluktuate quite significantly. Thus when individual, single
readings are posted, the values maybe significantly higher or lower than the
average, suggesting changes that don't exist.</p>

<p>GeigerLog will always send the average of the data you configured in the update
cycle. And GeigerLog uses this average for both CPM and ACPM, and calculates
uSV based on it. I suggest to have values assembled for at least 30 minutes,
more is better, before sending anything to the maps. Governmental sites like this
<a href='https://www.naz.ch/de/aktuell/tagesmittelwerte'>Swiss site</a>
provide even only DAILY averages of quality controlled data! See the GeigerLog
manual for a broader discussion.
"""


helpOccupationalRadiation = """
<!doctype html>
<style>
    h3              { color: darkblue; margin:5px 0px 5px 0px; padding:0px; }
    p, ol, ul, li   { margin:4px 0px 10px 0px; padding:0px;}
    td, th          { padding: 0px 30px 0px 0px;}
</style>

<H3>Occupational Radiation Limits</H3>

<p>The exposure to radiation is strongly regulated all over the world. As examples,
the occupational limits are given for USA and Germany.</p>

<p>"Occupational" refers to people working in fields with typically higher exposure to radiation
compared to the average person, like medical people applying X-rays, workers in nuclear power plants,
people in aviation, people in mining.</p>

<p>Of the many limits specified, only the yearly and lifelong exposures are given
here; the links will guide you to sites with more extensive specifications.<br></p>

<table >
  <tr>
    <th >    </th>
    <td ><b>Germany</b></td>
    <td ><b>USA</b></td>
    <td ><b>USA:Ger</b></td>
  </tr>
  <tr>
    <td >Yearly exposure</td>
    <td >  20 mSv</td>
    <td >  50 mSv</td>
    <td >  2.5 x</td>
  </tr>
  <tr>
    <td >= equiv. to permanent over year</td>
    <td >  2.3 µSv/h</td>
    <td >  5.7 µSv/h</td>
  </tr>
  <tr>
    <td >Lifelong exposure</td>
    <td > 400 mSv</td>
    <td >2350 mSv</td>
    <td >5.9 x</td>
  </tr>
  <tr>
    <td >= equiv. to permanent over life<br>(in 40 year work life)</td>
    <td > 1.14 µSv/h</td>
    <td >6.71 µSv/h</td>
    <td ></td>
  </tr>
  <tr>
    <td ></td>
    <td><a href='https://www.bfs.de/DE/themen/ion/strahlenschutz/beruf/grenzwerte/grenzwerte.html'>Grenzwerte</a></td>
    <td><a href='https://www.osha.gov/SLTC/radiationionizing/introtoionizing/ionizingattachmentsix.html'>OSHA</a></td>
  </tr>
</table>

<p><br>The numbers reflect a <b>very</b> different view of the two countries towards radiation health effects!</p>
"""


helpAbout = """
<!doctype html>
<style>
    h3              { color: darkblue; margin:5px 0px 5px 0px; padding:0px; }
    p, ol, ul, li   { margin:4px 0px 10px 0px; padding:0px; font-size:15px;}
    td, th          { padding: 0px 30px 0px 0px;}
</style>

<p><span style='color:darkblue; font:bold; font-size:x-large;'>GeigerLog</span>
is a combination of data logger, data presenter, and data analyzer.</p>

<p>It is based on Python (Version 3), hence it runs on Linux, Windows, Macs,
and other systems.</p>

<p>GeigerLog had initially been developed for the sole use with Geiger counters,
but has now become a more universal tool, which equally well handles
environmental data like tem&shy;pera&shy;ture, barometric-pressure, humidity,
light-intensity, and CO2, and is prepared for future sensors.

<p>In its present state it can e.g. be deployed as a monitor for a remote
weather station, com&shy;ple&shy;mented with a Geiger counter to monitor radioactivity,
and a sensor to moni&shy;tor CO2.

<p>It can be connected by wire or wireless by WiFi.

<h3><br>Monitoring GeigerLog</h3>

<p>GeigerLog has now its own build-in <b>Web Server</b> allowing to monitor and
partially control GeigerLog with a <b>Smartphone</b>.</p>

<h3><br>Devices Currently Supported by GeigerLog:</h3>

<p><b>GMC Devices:</b><br>GeigerLog continuous to support GQ Electronics's
GMC-3xx, GMC-5xx, and GMC-6xx line of classical Geiger counters, including the
variants with an additional 2nd Geiger tube.</p>

<p><b>AudioCounter Devices:</b>
<br>GeigerLog supports Geiger counters which only give an audio click for a
radioactive event.</p>

<p><b>RadMon Devices:</b>
<br>GeigerLog supports the RadMon+ hardware, which can provide a Geiger counter
as well as an environmental sensor for temperature, barometric-pressure,
and humidity.</p>

<p><b>AmbioMon Devices:</b>
<br>GeigerLog supports AmbioMon++ hardware, which can provide a Geiger
counter as well as an environmental sensor for temperature, barometric-pressure,
and humidity.</p>

<p><b>Gamma-Scout Devices:</b>
<br>GeigerLog supports the Geiger counters from Gamma-Scout.</p>

<p><b>I2C Devices:</b>
<br>GeigerLog supports sensor devices connected by the I2C interface, such as those
for tem&shy;pera&shy;ture, barometric-pressure, humidity, light-intensity, and CO2.

<p><b>LabJack Devices:</b>
<br>GeigerLog supports the u3 and Ei1050 hardware from LabJack running on Linux (perhaps Mac).

<p><b>MiniMon Devices:</b>
<br>GeigerLog supports these In-house CO2 monitoring devices (Linux only)</p>

<p><b>Simul Devices:</b>
<br>A simulated Geiger counter getting its “counts” from a Poisson random
number generator.</p>

<p><b>Manu Devices:</b>
<br>A Pseudo-Device which allows to enter values manually.</p>

<p><b>WiFiServer Devices:</b>
<br>GeigerLog acts as a client to request data from a device which is
acting as a server.</p>

<p><b>WiFiClient Devices:</b>
<br>GeigerLog acts as a server to which devices can connect and deliver data.</p>

<p style='text-align:center;'>-------------------------------------------------------------------</p>

<p>The most recent version of GeigerLog as well as an up-to-date
GeigerLog-Manual can be found at project GeigerLog at Sourceforge:
<a href="https://sourceforge.net/projects/geigerlog/">
https://sourceforge.net/projects/geigerlog/</a>.</p>

<p>References:</p>
<table>
<tr><td>&nbsp;&nbsp;Author:                         </td> <td>%s</td></tr>
<tr><td>&nbsp;&nbsp;Version GeigerLog:&nbsp;&nbsp;  </td> <td>%s</td></tr>
<tr><td>&nbsp;&nbsp;Copyright:                      </td> <td>%s</td></tr>
<tr><td>&nbsp;&nbsp;License:                        </td> <td>%s see included
file 'COPYING' and <a href="http://www.gnu.org/licenses">http://www.gnu.org/licenses</a></td></tr>
</table>
<br>
"""
