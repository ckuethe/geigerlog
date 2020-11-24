#!/usr/bin/python3
# -*- coding: UTF-8 -*-

"""
gglobs.py - GeigerLog's Super-Global Variables; can be read and modified
            in all scripts

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
__copyright__       = "Copyright 2016, 2017, 2018, 2019, 2020"
__credits__         = [""]
__license__         = "GPL3"
__version__         = "1.0"               # version of next GeigerLog
#__version__         = "1.0pre14"


# constants
NAN                 = float('nan')        # 'not-a-number'; used as 'missing value'
#INAN               = int('nan')          # gibt es nicht; int ist zwangsläufig immer definiert
JULIANUNIX          = 2440587.5416666665  # julianday('1970-01-01 00:00:00') (UNIX time start)
JULIAN111           = 1721425.5 - 1       # julianday('0001-01-01 00:00:00') (matplotlib time start)
                                          # Why this minus 1? strange but needed

# counters
xprintcounter       = 0                   # the count of dprint, vprint, and wprint commands

# messages
startup_failure     = ""                  # if configuration file is missing or
                                          # incorrect, this will hold error text to show

# pointers
exgg                = None                # pointer to ggeiger
notePad             = None                # pointer to print into notePad area
logPad              = None                # pointer to print into logPad area
btn                 = None                # the cycle time OK button; for inactivation
plotAudioPointer    = None                # points to the dialog window of plotaudio
plotScatterPointer  = None                # points to the dialog window of plotscatter
plotScatterFigNo    = None                # points to the window number of plotscatter
iconGeigerLog       = None                # points to the QIcon pixmap for 'icon_geigerlog.png'

# sql database
currentConn         = None                # connection to CURRENT database
logConn             = None                # connection to LOGGING database
hisConn             = None                # connection to HISTORY database

# flags
debug               = False               # helpful for debugging, use via command line
verbose             = False               # more detailed printing, use via command line
werbose             = False               # more verbose than verbose
devel               = False               # set some conditions for development CAREFUL !!!
devel1              = False               # =devel  + ADDITIONAL condition: load default db: default.logdb
devel2              = False               # =devel1 + ADDITIONAL condition: make connections
tput                = False               # to issue the tput command
redirect            = False               # on True redirects output from stdout and stderr to file stdlogPath
debugIndent         = ""                  # to indent printing

#special flags
testing             = False               # if true then some testing constructs will be activated CAREFUL !!!
GStesting           = False               # active only in module ggscout.py
test1               = False               # to run a specific test
test2               = False               # to run a specific test
test3               = False               # to run a specific test
test4               = False               # to run a specific test
stattest            = False               # when True display statistics on Normal in Poisson test

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
logDBPath           = None                # file path of the log database file

binFilePath         = None                # file path of the bin file (GMC device)
datFilePath         = None                # file path of the bin file (Gamma Scout device)
AMFilePath          = None                # file path of the bin file (AmbioMon device, either *CAM or *.CPS file)
hisFilePath         = None                # file path of the his file
hisDBPath           = None                # file path of the his database file
logDBPath           = None                # file path of the log database file
currentDBPath       = None                # file path of the current DB file for log or his

fileDialogDir       = None                # the default for the FileDialog starts

HistoryDataList     = []                  # where the DB data are stored by makeHist
HistoryParseList    = []                  # where the parse comments are stored by makeHist
HistoryCommentList  = []                  # where the DB comments are stored by makeHist
activeDataSource    = None                # can be 'Log' or 'His'

manual_filename     = "auto"              # name of the included manual file, like "GeigerLog-Manual-v0.9.93pre17.pdf"
                                          # on 'auto' GL searches for a file beginning with 'GeigerLog-Manual'

# GUI options
window_width        = 1366                # the standard screen of 1366 x 768 (16:9),
window_height       = 768                 #
window_size         = "auto"              # 'auto' or 'maximized'
windowStyle         = "auto"              # may also be defined in config file
displayLastValuesIsOn = False             # whether the displayLastValues windows is shown


## Serial ports

    # pyserial Parity parameters
    # import serial :
    # serial.PARITY_NONE    = N
    # serial.PARITY_EVEN    = E
    # serial.PARITY_ODD     = O
    # serial.PARITY_MARK    = M
    # serial.PARITY_SPACE   = S
    #
    # finding pyserial supported parameters:
    # myser = serial.Serial()
    # myser : Serial<id=0x7f7a05b18d68, open=False>(port=None, baudrate=9600, bytesize=8, parity='N',
    #               stopbits=1, timeout=None, xonxoff=False, rtscts=False, dsrdtr=False)
    # myser.BAUDRATES = 50, 75, 110, 134, 150, 200, 300, 600, 1200, 1800, 2400, 4800, 9600,
    #                   19200, 38400, 57600, 115200, 230400, 460800, 500000, 576000, 921600,
    #                   1000000, 1152000, 1500000, 2000000, 2500000, 3000000, 3500000, 4000000
    # myser.BYTESIZES = 5, 6, 7, 8
    # myser.PARITIES  = 'N', 'E', 'O', 'M', 'S'
    # myser.STOPBITS  = 1, 1.5, 2

GMCbaudrates        = [1200, 2400, 4800, 9600, 14400, 19200, 28800, 38400, 57600,        115200]
I2Cbaudrates        = [            4800, 9600,        19200,        38400, 57600, 76800, 115200, 230400]
GSbaudrates         = [      2400,       9600,                                                           460800]

# Serial port for GMC devices
GMCser              = None                # serial port pointer
GMCbaudrate         = 115200              # will be overwritten by a setting in geigerlog.cfg file
GMCusbport          = '/dev/ttyUSB0'      # will be overwritten by a setting in geigerlog.cfg file
GMCtimeout          = 3                   # will be overwritten by a setting in geigerlog.cfg file
GMCtimeout_write    = 3                   # will be overwritten by a setting in geigerlog.cfg file
GMCttyS             = "ignore"            # to 'ignore' or 'include' '/dev/ttySN', N=1,2,3,... ports on USB Autodiscovery

# Serial port for I2C devices
I2Cser              = None                # serial port pointer
I2Cbaudrate         = 115200              # will be overwritten by a setting in geigerlog.cfg file
I2Cusbport          = '/dev/ttyUSB1'      # will be overwritten by a setting in geigerlog.cfg file
I2Ctimeout          = 3                   # will be overwritten by a setting in geigerlog.cfg file
I2Ctimeout_write    = 3                   # will be overwritten by a setting in geigerlog.cfg file
I2CttyS             = "ignore"            # to 'ignore' or 'include' '/dev/ttySN', N=1,2,3,... ports on USB Autodiscovery

# Serial port for Gamma-Scout devices
# NOTE: some responses of Gamma-Scout take almost 1 sec, timeout setting must be well above 1 sec limit!
GSser               = None                # serial port pointer
GSbaudrate          = 9600                # will be overwritten by a setting in geigerlog.cfg file
GSusbport           = '/dev/ttyUSB2'      # will be overwritten by a setting in geigerlog.cfg file
GStimeout           = 3                   # will be overwritten by a setting in geigerlog.cfg file
GStimeout_write     = 3                   # will be overwritten by a setting in geigerlog.cfg file
GSttyS              = "ignore"            # to 'ignore' or 'include' '/dev/ttySN', N=1,2,3,... ports on USB Autodiscovery




## CALIBRATION

###############################################################################
## Beginning with version GeigerLog 0.9.94 the calibration is used as inverse of
## the previous definitions, i.e. 0.0065 µSv/h/CPM becomes 1/0.065 => 153.85 CPM/(µSv/h)
## This is rounded to 154 CPM/(µSv/h) to use no more than 3 valid digits.
###############################################################################

# The GMC factory default calibration factor is linear, i.e. the same
# for all 3 calibration points defined in a GMC counter.
# For a M4011 tube the calibration factor implemented in firmware is 0.0065 µSv/h/CPM
# For the 2nd tube in a GMC500+ device, different factors were seen:
# E.g.: from a calibration point #3 setting of 25CPM=4.85µSv/h the calibration
# factor is 0.194 µSv/h/CPM. While a calibration point #3 setting of
# 25CPM=9.75µSv/h results in 0.39 µSv/h/CPM!
# However, calibration determined in my own experiment reported here:
# http://www.gqelectronicsllc.com/forum/topic.asp?TOPIC_ID=5369
# see Reply #10, Quote: “With Thorium = 0.468, and K40 = 0.494,
# I'd finally put the calibration factor for the 2nd tube, the SI3BG,
# to 0.48 µSv/h/CPM. Which makes it 74 fold less sensitive than the M4011!”
# Others report even poorer values for the SI3BG:
# https://www.gqelectronicsllc.com/forum/topic.asp?TOPIC_ID=5554, Reply #17
# "The new correction factor for the primarily gamma tube is .881CPM/uSv/h or 1.135."
# This means calibration factor for that (2nd) tube = 1.135 µSv/h/CPM


# Default Calibration
# must be defined even if no connection exists. May be redefined in config.
DefaultCalibration1st   = 154             # CPM/(µSv/h), =  0.0065 in units of µSv/h/CPM
DefaultCalibration2nd   = 2.08            # CPM/(µSv/h), =  0.48   in units of µSv/h/CPM
DefaultCalibration3rd   = 154             # CPM/(µSv/h), =  0.0065 in units of µSv/h/CPM

# calibration of tubes #1, #2, #3
calibration1st      = "auto"              # calibration factor for the 1st tube
                                          # in most GMC counters this is the only tube
                                          # in a GMC-500+ counter this is the 1st or high sensitivity tube
calibration2nd      = "auto"              # calibration factor for the 2nd tube
                                          # in a GMC-500+ counter this is the 2nd or low-sensitivity tube
calibration3rd      = "auto"              # calibration factor for the 3rd tube
                                          # in the RadMon+ this is the only tube, set to 154 (0.0065) in InitRadMon



# GMC stuff                               # will be set after reading the version of the counter from the device
GMCActivation       = False               # To use or not use a GMC Device counter
GMCConnection       = False               # Not connected if False
GMCDeviceName       = None                # to be detected in init; generic name like: "GMC Device"
GMCdeviceDetected   = None                # will be replaced after connection with full specific
                                          # name as detected, like 'GMC-300Re 4.20'
                                          # had been 14 chars, can now be longer
GMCvariables        = "auto"              # which variables are natively supported

# GMC Bugs
locationBug         = ["GMC-500+Re 1.18", # see the FIRMWARE BUGS topic
                       "GMC-500+Re 1.21"] # in the configuration file

# GMC Other
GMCmemory           = "auto"              # Can be configured for 64kB or 1 MB in the config file
SPIRpage            = "auto"              # size of page to read the history from device
SPIRbugfix          = "auto"              # if True then reading SPIR gives one byte more than
                                          # requested  (True for GMC-300 series)
endianness          = "auto"              # big- vs- little-endian for calibration value storage
configsize          = "auto"              # 256 bytes in 300series, 512 bytes in 500/600 series
voltagebytes        = "auto"              # 1 byte in the 300 series, 5 bytes in the 500/600 series
variables           = "auto"              # a list of the variables to sample, CPM, CPS, 1st, 2nd
nbytes              = "auto"              # the number of bytes the CPM and CPS calls, as well as
                                          # the calls to 1st and 2nd tube deliver

cfg                 = None                # Configuration bytes of the counter. 256 bytes in 300series, 512 bytes in 500series
#cfgOffsetPower      = 0                   # Offset in config for Power status (0=OFF, 255= ON)
cfgOffsetAlarm      = 1                   # Offset in config for AlarmOnOff (0=OFF, 1=ON)
cfgOffsetSpeaker    = 2                   # Offset in config for SpeakerOnOff (0=OFF, 1=ON)
cfgOffsetSDT        = 32                  # Offset in config to Save Data Type
#cfgOffsetCalibration= 8                   # Offset in config for CPM / µSv/h calibration points
#cfgOffsetMaxCPM     = 49                  # A MaxCPM during what period? of values in Memory??? HiByte@49, LoByte@50
#cfgOffsetBattery    = 56                  # Battery Type: 1 is non rechargeable. 0 is chargeable.
savedatatypes       = (
                        "OFF (no history saving)",
                        "CPS, save every second",
                        "CPM, save every minute",
                        "CPM, save hourly average",
                        "CPS, save every second if exceeding threshold",
                        "CPM, save every minute if exceeding threshold",
                      )
savedatatype        = "Unknown - will become known when the device is connected"
savedataindex       = None


# AudioCounter
AudioActivation     = False               # Not available if False
AudioConnection     = False               # Not connected if False
AudioDevice         = "auto"              # to be set in init to (None, None)
AudioLatency        = "auto"              # to be set in init to (1.0, 1.0) sec latency
AudioDeviceName     = "None"              # to be set in init
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
AudioThreadStop     = False               # True to stop the audio thread
AudioVariables      = "auto"              #
AudioCalibration    = "auto"              # units: CPM / (µSv/h)
AudioMultiPulses    = None                # stores the concatenated audio data for plotting
AudioRecording      = None                # stores the Recording
AudioPlotData       = None                # stores the data to be plotted

# I2C stuff
I2CActivation       = False               # Not available if False; to be set via config
I2CConnection       = False               # Not connected if False
I2CDeviceName       = None                # to be assigned in I2c Init; now:
I2CDeviceDetected   = None              # to be assigned in I2C init with specific name,
I2CVariables        = "auto"
I2CThread           = None                # Thread used for I2C
I2CSensor1          = None                # the BME280
I2CSensor2          = None                # the TSL259
I2CFirmware         = None                # to be set in init, but included in DeviceDetected
I2CSerialNumber     = None                # to be set in init, but not available
I2CInfo             = None                # to be set in init

# I2C Dongles
ELVdongle           = "ELVdongle"         # ELV USB-I2C Dongle
elv                 = None                # becomes instance of the ELV USB-I2C device

# I2C Sensors and Modules
bme280              = {
                       "name": "BME280",
                       "feat": "Temperature, Pressure, Humidity",
                       "addr": 0x77,      # (d119)  addr: 0x76, 0x77
                       "type": 0x60,      # (d96)   BME280 has chip_ID 0x60
                       "hndl": None,      # handle
                       "dngl": None,      # connected with dongle
                      }

tsl2591             = {
                       "name": "TSL2591",
                       "feat": "Light (Vis, IR)",
                       "addr": 0x29,      # (d41)  addr: 0x29
                       "type": 0x50,      # Device ID 0x50
                       "hndl": None,      # handle
                       "dngl": None,      # connected with dongle
                      }


# Gamma-Scout stuff
GSActivation        = False               # Not available if False; to be set via config
GSConnection        = False               # Not connected if False
GSDeviceName        = None                # to be assigned in GS Init; now: "Gamma-Scout"
GSDeviceDetected    = None                # to be assigned in GS init with specific name, now same "Gamma-Scout"
GSVariables         = "auto"
GSCalibration       = "auto"              # auto will become 0.009 in initGammaScout
GSFirmware          = None                # to be set in GS init
GSSerialNumber      = None                # to be set in GS init
GSDateTime          = None                # to be set when setting DateTime
GSMemory            = 0                   # to be set when calling History
GSinPCmode          = False               # determines whether terminateGammaScout will attempt to


# RadMon stuff
RMActivation        = False               # must be true to use RadMon
RMConnection        = False               # True when initialized by GeigerLog
RMDeviceName        = None                # can currently be only RadMon+
RMDeviceDetected    = None                # can currently be only RadMon+
RMServerIP          = "auto"              # MQTT server IP, to which RadMon sends the data
RMServerPort        = "auto"              # Port of the MQTT server, defaults to 1883
RMServerFolder      = "auto"              # The MQTT folder as defined in the RadMon+ device
RMCalibration       = "auto"              # calibration factor for the tube used
RMVariables         = "auto"              # a list of the variables to log, T,P,H,R
RMTimeout           = 3                   # waiting for "successful connection" confirmation
RMCycleTime         = 1                   # cycle time of the RadMon device

RMconnect           = (-99, "")           # flag to signal connection
RMdisconnect        = (-99, "")           # flag to signal dis-connection

rm_client           = None                # to be set in gradmon.initRadMon
rm_cpm              = None                # temporary storage for CPM
rm_temp             = None                # temporary storage for Temperature
rm_press            = None                # temporary storage for Pressure
rm_hum              = None                # temporary storage for Humidity
rm_rssi             = None                # temporary storage for RSSI


# AmbioMon stuff
AmbioActivation     = False               # must be true to use AmbioMon++
AmbioConnection     = False               # True after being initialized by GeigerLog
AmbioDeviceName     = None                # can currently be only AmbioMon++
AmbioDeviceDetected = None                # can currently be only AmbioMon++
AmbioServerIP       = "auto"              # server Domain name or IP to which AmbioMon connects
AmbioAP_IP          = "auto"              # server IP address of Ambiomon in Access Point mode, Default = "192.168.4.1"
AmbioSSID           = "auto"              # SSID of user's WiFi network
AmbioSSIDPW         = "auto"              # Password of user's WiFi network
AmbioCalibration    = "auto"              # calibration factor for the tube used
AmbioVariables      = "auto"              # a list of the variables to log
AmbioDataType       = "auto"              # "LAST" or "AVG" for lastdata or lastavg
AmbioTimeout        = "auto"              # waiting for successful connection

# settings for the AmbioMon device
AmbioVoltage        = 444.44              # voltage of the GM tube in the AmbioMon
AmbioCycletime      = 1                   # cycle time of the AmbioMon device
AmbioFrequency      = 1500                # frequency of driving HV generator
AmbioPwm            = 0.5                 # Pulse Width Modulation of HV generator
AmbioSav            = "Yes"               # Switching into saving mode (Yes/No)



# LabJack stuff
LJActivation        = False
LJConnection        = False                     # True when initialized by GeigerLog
LJDeviceName        = "None"                    # LabJack U3 with probe EI1050
LJVariables         = "auto"                    # a list of the variables to log; auto=T,H,R
LJversionLJP        = "undefined until loaded"  # version of LabJackPython
LJversionU3         = "undefined until loaded"  # version of U3
LJversionEI1050     = "undefined until loaded"  # version of EI1050


# RaspiStuff
RaspiActivation     = False               # Not available if False
RaspiConnection     = False               # Not connected if False
RaspiDevice         = "None"              # to be set in init
RaspiDeviceName     = "None"              # to be set in init
RaspiPulseMax       = 2**15               # +/- 32768 as maximum pulse height for 16bit signal
RaspiPulseDir       = False               # False for negative; True for positive pulse
RaspiThreshold      = 60                  # Percentage of pulse height to trigger a count
                                          # 60% of +/- 32768 => approx 20000
RaspiRate           = 44100               # sampling rate audio; works for most sound cards
RaspiChunk          = 32                  # samples per read
RaspiChannels       = 1                   # 1= Mono, 2=Stereo
RaspiFormat         = None                # becomes (int16, int16)
RaspiLatency        = None                # becomes setting in sec

RaspiLastCpm        = 0                   # audio clicks CPM
RaspiLastCps        = 0                   # audio clicks CPS
RaspiThreadStop     = False               # True to stop the audio thread
RaspiVariables      = "auto"              #
RaspiCalibration    = "auto"              # units: CPM / (µSv/h)
RaspiMultiPulses    = None                # stores the concatenated audio data for plotting
RaspiRecording      = None                # stores the Recording
RaspiPlotData       = None                # stores the data to be plotted



#ESP32
terminal            = None                # for the ESP32


# Logging Options
cpm_counter         = 0                   # counts readings since last start logging; prints as index in log
logging             = False               # flag for logging
logcycle            = 3                   # time in seconds between CPM or CPS calls in logging
lastValues          = None                # last values received from device
lastRecord          = None                # last records received from devices

# History Options
keepFF              = False               # Flag in startup-options
                                          # Keeps all hexadecimal FF (Decimal 255) values as a
                                          # real value and not an 'Empty' one. See manual in chapter
                                          # on parsing strategy
fullhist            = False               # If False breaks history recording when 8k FF is read
                                          # if True reads the whole history from memory

# Graphic Options
#ruler:     = "## Index,            DateTime,     CPM,     CPS,  CPM1st,  CPS1st,  CPM2nd,  CPS2nd,    Temp,   Press,   Humid,   RMCPM"
varnames            = ( "CPM",
                        "CPS",
                        "CPM1st",
                        "CPS1st",
                        "CPM2nd",
                        "CPS2nd",
                        "CPM3rd",
                        "CPS3rd",
                        "T",
                        "P",
                        "H",
                        "X")              # 12 vars

datacolsDefault     = 1 + len(varnames)   # max number of data columns supported, currently = 13:
                                          # as : DateTime plus varnames above (index excluded; is not data),

vardict             = {# short,     long,            very short names
                        "CPM"    : ("CPM",           "M"  ),
                        "CPS"    : ("CPS",           "S"  ),
                        "CPM1st" : ("CPM1st",        "M1" ),
                        "CPS1st" : ("CPS1st",        "S1" ),
                        "CPM2nd" : ("CPM2nd",        "M2" ),
                        "CPS2nd" : ("CPS2nd",        "S2" ),
                        "CPM3rd" : ("CPM3rd",        "M3" ),
                        "CPS3rd" : ("CPS3rd",        "S3" ),
                        "T"      : ("Temperature",   "T"  ),
                        "P"      : ("Pressure",      "P"  ),
                        "H"      : ("Humidity",      "H"  ),
                        "X"      : ("Xtra",          "X"  ),
                      }

varunit             = {                      # units of Variable; CPM*, CPS*, T can change
                        "CPM"    :"CPM",     # can have unit: "µSv/h"
                        "CPS"    :"CPS",     # can have unit: "µSv/h"
                        "CPM1st" :"CPM",     # can have unit: "µSv/h"
                        "CPS1st" :"CPS",     # can have unit: "µSv/h"
                        "CPM2nd" :"CPM",     # can have unit: "µSv/h"
                        "CPS2nd" :"CPS",     # can have unit: "µSv/h"
                        "CPM3rd" :"CPM",     # can have unit: "µSv/h"
                        "CPS3rd" :"CPS",     # can have unit: "µSv/h"
                        "T"      :"°C",      # can have unit: "°F"
                        "P"      :"hPa",     # no unit change
                        "H"      :"%",       # no unit change
                        "X"      :"x",       # can have any unit
                      }

#print("vardict:", vardict)
#print("vardict.keys:", vardict.keys())
#print("vardict.values:", vardict.values())

# colors at: https://matplotlib.org/users/colors.html
varStyleDefault     = {
                        "CPM"    : ("blue",          "solid"),
                        "CPS"    : ("magenta",       "solid"),
                        "CPM1st" : ("deepskyblue",   "solid"),
                        "CPS1st" : ("violet",        "solid"),
                        "CPM2nd" : ("cyan",          "solid"),
                        #~"CPS2nd" : ("pink",          "solid"),
                        "CPS2nd" : ("#9b59b6",          "solid"),
                        #~"CPM3rd" : ("blue",          "dotted"),
                        #~"CPS3rd" : ("magenta",       "dotted"),
                        "CPM3rd" : ("brown",          "solid"),
                        #~"CPS3rd" : ("#c39bd3",       "solid"),
                        "CPS3rd" : ("#F9AF00",       "solid"),
                        "T"      : ("red",           "solid"),
                        "P"      : ("black",         "solid"),
                        "H"      : ("green",         "solid"),
                        "X"      : ("orange",        "solid"),
                      }
varStyle            = varStyleDefault.copy() # need a copy to allow reset as
                                             # colorpicker may change color

# Value - Scaling - this modifies the measured variable; the modification will be stored to DB
ValueScale           = {}
ValueScale["CPM"]    = "VAL"               # no scaling
ValueScale["CPS"]    = "VAL"               # no scaling
ValueScale["CPM1st"] = "VAL"               # no scaling
ValueScale["CPS1st"] = "VAL"               # no scaling
ValueScale["CPM2nd"] = "VAL"               # no scaling
ValueScale["CPS2nd"] = "VAL"               # no scaling
ValueScale["CPM3rd"] = "VAL"               # no scaling
ValueScale["CPS3rd"] = "VAL"               # no scaling
ValueScale["T"]      = "VAL"               # no scaling
ValueScale["P"]      = "VAL"               # no scaling
ValueScale["H"]      = "VAL"               # no scaling
ValueScale["X"]      = "VAL"               # no scaling


# Graph Sscaling - this does NOT modify the var value, only how it is plotted
GraphScale           = {}
GraphScale["CPM"]    = "VAL"               # no scaling
GraphScale["CPM1st"] = "VAL"               # no scaling
GraphScale["CPM2nd"] = "VAL"               # no scaling
GraphScale["CPS"]    = "VAL"               # no scaling
GraphScale["CPS1st"] = "VAL"               # no scaling
GraphScale["CPS2nd"] = "VAL"               # no scaling
GraphScale["CPM3rd"] = "VAL"               # no scaling
GraphScale["CPS3rd"] = "VAL"               # no scaling
GraphScale["T"]      = "VAL"               # no scaling
GraphScale["P"]      = "VAL"               # no scaling
GraphScale["H"]      = "VAL"               # no scaling
GraphScale["X"]      = "VAL"               # no scaling
GraphScale["X"]      = "VAL"               # no scaling


DevicesConnected     = 0                   # number of connected devices; determined upon connecting
DevicesNames         = ("GMC",
                        "Audio",
                        "I2C",
                        "RadMon",
                        "AmbioMon",
                        "LabJack",
                        "Gamma-Scout",
                        "Raspi")           # all supported devices

DevicesVars          = {                   # holder for varnames in all supported devices
                        "GMC"        : None,
                        "Audio"      : None,
                        "I2C"        : None,
                        "RadMon"     : None,
                        "AmbioMon"   : None,
                        "LabJack"    : None,
                        "Gamma-Scout": None,
                        "Raspi"      : None,
                       }

DevicesActive        = {                   # holder for activated status of all supported devices
                        "GMC"        : False,
                        "Audio"      : False,
                        "I2C"        : False,
                        "RadMon"     : False,
                        "AmbioMon"   : False,
                        "LabJack"    : False,
                        "Gamma-Scout": False,
                        "Raspi"      : False,
                       }

varcheckedCurrent   = {}                   # is variable checked for inclusion in plot
varcheckedLog       = {}                   # is variable checked for inclusion in plot for Log
varcheckedHis       = {}                   # is variable checked for inclusion in plot for History
varlabels           = {}                   # info on avg, StdDev etc; will be set in gplot
loggableVars        = {}                   # Vars which can be logged with current connections

for vname in varnames:
    varcheckedLog       [vname] = False    # set all false
    varcheckedHis       [vname] = False    # set all false
    varcheckedCurrent   [vname] = False    # set all false
    varlabels           [vname] = ""       # set all to empty
    loggableVars        [vname] = False    # set all False

#print("varchecked: ", varcheckedCurrent)
#print("varlabels:  ", varlabels)

activeVariables     = 0                     # determined in switchConnections; at least 1 needed
textDevVars         = ""                    # determined in switchConnections, Devices and associated variables
varMap              = {}                    # holds mapping of the variables

allowGraphUpdate    = True                # to block updates on reading data

Xleft               = None                # time min if entered
Xright              = None                # time max if entered
Xunit               = "Time"              # time unit; can be Time, auto, second, minute, hour, day
XunitCurrent        = Xunit               # current time unit

Ymin                = None                # CPM min if entered
Ymax                = None                # CPM max if entered
Yunit               = "CPM"               # CPM unit; can be CPM, CPS, µSv/h
YunitCurrent        = Yunit               # current count unit

Y2min               = None                # CPM min if entered
Y2max               = None                # CPM max if entered
Y2unit              = "Amb"               # CPM unit; can be CPM, CPS, µSv/h
Y2unitCurrent       = Yunit               # current count unit

avgChecked          = False               # Plot the lines Average, +/- 95% confidence, and Legend with average +/- StdDev value
mavChecked          = False               # Plot the Moving Average line, and Legend with MovAvg length ins seconds and data points
mav_initial         = 60                  # length of Moving Average period in seconds
mav                 = mav_initial         # currently selected mav period
fprintMAV           = False               # to print to NotePad the moving average comments

# Plotstyle                               # placeholder; don't change here - is set in config
linestyle           = 'solid'
linecolor           = 'blue'              # overwritten by varcolor anyway
linewidth           = '0.5'
markerstyle         = 'o'
markersize          = '10'

#Graph Y-Limits                           # to calculate cursor position for left, right Y-axis
y1_limits           = (0, 1)              # (bottom, top) of y left
y2_limits           = (0, 1)              # (bottom, top) of y right

# Data arrays and values
logTime             = None                # array: Time data from total file
logTimeDiff         = None                # array: Time data as time diff to first record in days
logTimeFirst        = None                # value: Time of first record of total file

logTimeSlice        = None                # array: selected slice out of logTime
logTimeDiffSlice    = None                # array: selected slice out of logTimeDiff
logSliceMod         = None

sizePlotSlice       = None                # value: size of plotTimeSlice

logDBData           = None                # 2dim numpy array with the log data
hisDBData           = None                # 2dim numpy array with the his data
currentDBData       = None                # 2dim numpy array with the currently plotted data

# Data read out from the device config
cfgLowKeys          = ( "Power",
                        "Alarm",
                        "Speaker",
                        "CalibCPM_0",
                        "CalibuSv_0",
                        "CalibCPM_1",
                        "CalibuSv_1",
                        "CalibCPM_2",
                        "CalibuSv_2",
                        "SaveDataType",
                        "MaxCPM",
                        "Baudrate",
                        "Battery",
                        "ThresholdMode",
                        "ThresholdCPM",
                        "ThresholduSv"
                      )

cfgLow = {                                         # common to all GMCs
          "Power"         : None ,
          "Alarm"         : None ,
          "Speaker"       : None ,
          "CalibCPM_0"    : None ,                 # calibration_0 CPM Hi+Lo Byte
          "CalibuSv_0"    : None ,                 # calibration_0 uSv 4 Byte
          "CalibCPM_1"    : None ,                 # calibration_1 CPM Hi+Lo Byte
          "CalibuSv_1"    : None ,                 # calibration_1 uSv 4 Byte
          "CalibCPM_2"    : None ,                 # calibration_2 CPM Hi+Lo Byte
          "CalibuSv_2"    : None ,                 # calibration_2 uSv 4 Byte
          "SaveDataType"  : None ,                 # History Save Data Type
          "MaxCPM"        : None ,                 # MaxCPM Hi + Lo Byte
          "Baudrate"      : None ,                 # Baudrate, coded differently for 300 and 500/600 series
          "Battery"       : None ,                 # Battery Type: 1 is non rechargeable. 0 is chargeable.
          "ThresholdMode" : None ,                 # Which Modes
          "ThresholdCPM"  : None ,                 # ??
          "ThresholduSv"  : None ,                 # ??
         }

cfgLowndx = {                                      # all GMCs
          "Power"         : (0,        0 + 1),
          "Alarm"         : (1,        1 + 1),
          "Speaker"       : (2,        2 + 1),
          "CalibCPM_0"    : (8,        8 + 2),     # calibration_0 CPM Hi+Lo Byte
          "CalibuSv_0"    : (10,      10 + 4),     # calibration_0 uSv 4 Byte
          "CalibCPM_1"    : (14,      14 + 2),     # calibration_1 CPM Hi+Lo Byte
          "CalibuSv_1"    : (16,      16 + 4),     # calibration_1 uSv 4 Byte
          "CalibCPM_2"    : (20,      20 + 2),     # calibration_2 CPM Hi+Lo Byte
          "CalibuSv_2"    : (22,      22 + 4),     # calibration_2 uSv 4 Byte
          "SaveDataType"  : (32,      32 + 1),     # History Save Data Type
          "MaxCPM"        : (49,      49 + 2),     # MaxCPM Hi + Lo Byte
          "Baudrate"      : (57,      57 + 1),     # Baudrate, coded differently for 300 and 500/600 series
          "Battery"       : (56,      56 + 1),     # Battery Type: 1 is non rechargeable. 0 is chargeable.
          "ThresholdMode" : (64,      64 + 1) ,    # Mode: 0:CPM, 1:µSv/h, 2:mR/h
          "ThresholdCPM"  : (62,      62 + 2) ,    # ??
          "ThresholduSv"  : (65,      65 + 4) ,    # ??
         }

# Radiation World maps
cfgMapKeys          =  ("Website", "URL", "SSID", "Password", "UserID", "CounterID", "Period", "WiFi")

GMCmap = {                                # as defined in configuration file
          "SSID"        : "",
          "Password"    : "",
          "Website"     : "",
          "URL"         : "",
          "UserID"      : "",
          "CounterID"   : "",
          "Period"      : "",
          "WiFi"        : "",
         }

cfgMap = {                               # as read out from the device
          "SSID"        : "" ,
          "Password"    : "" ,
          "Website"     : "" ,
          "URL"         : "" ,
          "UserID"      : "" ,
          "CounterID"   : "" ,
          "Period"      : "" ,
          "WiFi"        : "" ,
         }

cfg512ndx = {                                    # GMC-500/600
          "SSID"        : (69,     69 + 32),
          "Password"    : (101,   101 + 32),
          "Website"     : (133,   133 + 32),
          "URL"         : (165,   165 + 32),
          "UserID"      : (197,   197 + 32),
          "CounterID"   : (229,   229 + 32),
          "Period"      : (261,   261 +  1),     #
          "WiFi"        : (262,   262 +  1),     # WiFi OnOff
         }

cfg256ndx = {                                    # only GMC-320+V5
          "SSID"        : (69,     69 + 16),
          "Password"    : (85,     85 + 16),
          "Website"     : (101,   101 + 25),
          "URL"         : (126,   126 + 12),
          "UserID"      : (138,   138 + 12),
          "CounterID"   : (150,   150 + 12),
          "Period"      : (112,   112 +  1),     # 112
          "WiFi"        : (113,   113 +  1),     # 113 WiFi OnOff
         }


helpOptions = """
Usage:  geigerlog [Options] [Commands]

By default, data files will be read-from/written-to the
data directory "data", a subdirectory to the program
directory

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
    showstyles          Show a list of styles avail-
                        able on your system and exit.
                        For usage details see manual.
    keepFF              Keeps all hexadecimal FF
                        (Decimal 255) values as a
                        real value and not an 'Empty'
                        one. See manual in chapter
                        on parsing strategy.
    devel               Development settings; careful!
                        see program code

To watch debug and verbose output start the program from the
command line in a terminal. The output will print to the terminal.

With the Redirect option all output - including Python error
messages - will go into the redirect file geigerlog.stdlog.
"""

helpQuickstart = """
<!doctype html>
<style>
    h3          { color: darkblue; margin:10px 0px 5px 0px; padding:0px; }
    p, ol, ul   { margin:8px 0px 4px 0px; padding:0px;}
</style>
<H3>Mouse Help</H3><p>resting your mouse cursor briefly over an item of the window shows a ToolTip message providing info on the item!

<h3>USB Port and Baudrate</h3>
<p>Assuming a USB cable is connecting computer and device:</p>
<p>Start GeigerLog and from the menu choose <b>Help -> Show & Select USB Port and
Baudrate</b>, or press the blue <b>Help Port</b> toolbar button.
Select the proper settings for your device, and press ok.

<p>If you don't know the proper settings you may start the <b>USB Autodiscovery</b>
from the Help menu for your device, but it is strongly suggested that you first
read the manual in the chapters for your device and heed the CAUTION message popping up!</p>

<h3>Start Logging</h3>
<p>This will create a database file to store newly acquired data from the devices.</p>
<ol>
<li>Connect the computer with the devices<br>(menu: <b>Device -> Connect Devices</b>, or click the <b>Connect</b> button)</li>
<li>GMC device only: Switch device power on<br>(menu: <b>Device -> GMC Series -> Switch Power ON</b>))</li>
<li>Load a log file<br>(menu: <b>Log -> Get Log File or Create New One</b>)<br>
In the Get Log File dialog enter a new filename and press Enter,
or select an existing file to <b>APPEND</b> new data to this file.</li>
<li>Start logging<br>(menu: <b>Log -> Start Logging</b>, or click the <b>Start Log</b> toolbar icon)</li>
</ol>

<h3>Get History</h3>
<p>This will create a database file to store all data downloaded from the internal storage of the device.</p>
<ol>
<li>Connect the computer with the devices<br>(menu: <b>Device -> Connect Devices</b>, or click the <b>Connect</b> button)</li>
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

<p><b>Device Model Name:  GMC-500+</b></p>

<p>When this device is on firmware 1.18 it identifies itself with an empty identifier,
which prohibits use on GeigerLog. It should identify itself as 'GMC-500+Re 1.18'.</p>

<p>A work-around is to cycle the connection: ON -> OFF -> ON. Then it should work.</p>

<p>This bug is corrected with firmware 1.21. It is recommended to contact GMC support for an update.
The Geiger counter will then identify itself as 'GMC-500+Re 1.21'.</p>
<p>-------------------------------------------------------------------------------</p>
<p><b>Device Model Name:  GMC-500 / 600 series</b></p>

<p>Some firmware versions, at least 1.18 and 1.21, have a bug (location bug) which
results in errors in the parsing of the history file. It is advised to upgrade at least to
the 1.22 firmware!</p>
"""



helpWorldMaps = """
<!doctype html>
<style>
    h3          { color: darkblue; margin:5px 0px 5px 0px; padding:0px; }
    p, ol, ul   { margin:4px 0px 4px 0px; padding:0px;}
</style>

<H3>Radiation World Maps</H3>

<p>Several web sites exist, which attempt to show a worldwide map of the
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

<p>If you want to contibute to
<a href='http://www.gmcmap.com/' >gmcmap.com</a>, you need to register there.
This provides you with a UserID and a CounterID. Enter both into the
respective fields in the GeigerLog configuration file 'geigerlog.cfg' under
the heading 'Worldmaps'. That's it!</p>

<p>You need to be logging. Then the toolbar icon 'Map' turns blue, aka it
becomes enabled (as well as the menu entry Web -> Update Radiation World Map).
Click the icon and you'll be presented with a dialogue box, allowing you to
cancel or to send your data to the map. Obviously, for this to
succeed you need to have an active internet connection at your computer!</p>

<p>You will see a confirmation printed to GeigerLog's NotePad area, including
the response of the website.</p>

<H3>A word of caution:</H3>
<p>As far as I can see there is no quality control of the data! Nothing
prevents users from putting a strong radioactive source in front of their detector,
and pushing these data to the web. In fact, you don't even need a counter, and
don't even need GeigerLog, but can enter any data you wish manually!
Also, there does not seem to be a way to retract any inadvertently
sent data. Poor data will quickly destroy any value of those sites.</p>

<p>Even more subtle things may reduce the value of those websites: Geiger
counter readings fluktuate quite significantly. Thus when individual, single
readings are posted, the values maybe significantly higher or lower than the
average, suggesting changes that don't exist.</p>

<p>GeigerLog will always send the average of ALL data you see in the plot in
the moment you press the Map button. Thus you can easily select or cut out
data which have nothing to do with the background. And
GeigerLog uses this average for both CPM and ACPM, and calculates uSV based
on it. I suggest to have values assembled for at least 30 minutes,
more is better, before sending anything to the maps. Governmental sites like this
<a href='https://www.naz.ch/de/aktuell/tagesmittelwerte.shtml'>Swiss site</a>
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
  </tr>
  <tr>
    <td >Yearly exposure</td>
    <td >  20 mSv</td>
    <td >  50 mSv</td>
  </tr>
  <tr>
    <td >Lifelong exposure</td>
    <td > 400 mSv</td>
    <td >2350 mSv</td>
  </tr>
  <tr>
    <td >Links</td>
    <td><a href='https://www.bfs.de/DE/themen/ion/strahlenschutz/beruf/grenzwerte/grenzwerte.html'>BfS Grenzwerte</a></td>
    <td><a href='https://www.osha.gov/SLTC/radiationionizing/introtoionizing/ionizingattachmentsix.html'>OSHA</a></td>
  </tr>
</table>

<p>The differences are quite significant; see details in the links.</p>
"""


helpAbout = """
<!doctype html>
<style>
    h3              { color: darkblue; margin:5px 0px 5px 0px; padding:0px; }
    p, ol, ul, li   { margin:4px 0px 10px 0px; padding:0px;}
    td, th          { padding: 0px 30px 0px 0px;}
</style>

<p><span style='color:darkblue; font:bold; font-size:x-large;'>GeigerLog</span>
is a combination of data logger, data presenter, and data analyzer.</p>

<p>It is based on Python (Version 3), hence it runs on Linux, Windows, Macs,
and other systems.</p>

<p>GeigerLog had initially been developed for the sole use with Geiger counters,
but has now become a more universal tool, which equally well handles
environmental data like temperature, air-pressure, and humidity, and is prepared
for future sensors.</p>

<p>In its present state it can e.g. be deployed as a monitor for a remote
weather station, complemented with a Geiger counter to monitor radioactivity.</p>

<p><br>Currently Supported Devices:</p>

<p><b>GMC Devices:</b><br>GeigerLog continuous to support GQ Electronics's
GMC-3xx, GMC-5xx, and GMC-6xx line of classical Geiger counters, including the
variants with an additional 2nd Geiger tube.</p>

<p><b>AudioCounter Devices:</b>
<br>GeigerLog supports Geiger counters which only give an audio click for a
radioactive event.</p>

<p><b>I2C Devices:</b>
<br>GeigerLog supports devices connected by the I2C interface</p>

<p><b>RadMon Devices:</b>
<br>GeigerLog supports the RadMon+ hardware, which can provide a Geiger counter
as well as an environmental sensor for temperature, air-pressure
(atmospheric-pressure), and humidity.</p>

<p><b>AmbioMon Devices:</b>
<br>GeigerLog supports AmbioMon++ hardware, devices which can provide a Geiger
counter as well as an environmental sensor for temperature, air-pressure
(atmospheric-pressure), and humidity.</p>

<p><b>LabJack Devices:</b>
<br>GeigerLog supports the u3 and Ei1050 hardware from LabJack.</p>

<p><b>Gamma-Scout Devices:</b>
<br>GeigerLog supports the Geiger counters from Gamma-Scout.</p>

<p><br>The most recent version of GeigerLog as well as an up-to-date
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

