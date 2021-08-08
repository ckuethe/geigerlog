#! /usr/bin/env python3
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
__copyright__       = "Copyright 2016, 2017, 2018, 2019, 2020, 2021"
__credits__         = [""]
__license__         = "GPL3"
__version__         = "1.2.1"             # version of next GeigerLog
#__version__         = "1.2pre9"         #


# constants
NAN                 = float('nan')        # 'not-a-number'; used as 'missing value'
JULIANUNIX          = 2440587.5416666665  # julianday('1970-01-01 00:00:00') (UNIX time start)
JULIAN111           = 1721425.5 - 1       # julianday('0001-01-01 00:00:00') (matplotlib time start)
                                          # Why this minus 1? strange but needed

# counters
xprintcounter       = 0                   # the count of dprint, vprint, and wprint commands

# messages
python_failure      = ""                  # msg wrong Python version
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
bboxbtn             = None                # points to button box of GMC_popuo

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
devel3              = False               # =devel2 + ADDITIONAL condition: quicklog
tput                = False               # to issue the tput command
redirect            = False               # on True redirects output from stdout and stderr to file stdlogPath
debugIndent         = ""                  # to indent printing
stopPrinting        = False               # to stop long prints of data

#special flags
testing             = False               # if true then some testing constructs will be activated CAREFUL !!!
graphdemo           = False               # if true then handling of line properties of selected var will be modified for demo
stattest            = False               # when True display statistics on Normal in Poisson test
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
displayLastValsIsOn = False               # whether the displayLastValues windows is shown
hidpi               = False               # if true the AA_EnableHighDpiScaling will be applied
hipix               = False               # if true the AA_UseHighDpiPixmaps will be applied
hidpiActivation     = True                # The PyQt5 commands hidpi and hipix will be applied
hidpiScaleMPL       = 100                 # 100 is the default dpi for matplotlib


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
    # myser           : Serial<id=0x7f7a05b18d68, open=False>(port=None, baudrate=9600, bytesize=8, parity='N',
    #                   stopbits=1, timeout=None, xonxoff=False, rtscts=False, dsrdtr=False)
    # myser.BAUDRATES : 50, 75, 110, 134, 150, 200, 300, 600, 1200, 1800, 2400, 4800, 9600,
    #                   19200, 38400, 57600, 115200, 230400, 460800, 500000, 576000, 921600,
    #                   1000000, 1152000, 1500000, 2000000, 2500000, 3000000, 3500000, 4000000
    # myser.BYTESIZES : 5, 6, 7, 8
    # myser.PARITIES  : 'N', 'E', 'O', 'M', 'S'
    # myser.STOPBITS  : 1, 1.5, 2

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
GSstopbits          = 1                   # generic in pyserial;     will not change in code
GSbytesize          = 7                   # specific to Gamma-Scout; will not change in code
GSparity            = "E"                 # specific to Gamma-Scout; will not change in code


## CALIBRATION

###############################################################################
## Beginning with version GeigerLog 1.0 the calibration is used as inverse of
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
DefaultSens1st     = 154                 # CPM/(µSv/h), =  0.0065 in units of µSv/h/CPM
DefaultSens2nd     = 2.08                # CPM/(µSv/h), =  0.48   in units of µSv/h/CPM
DefaultSens3rd     = 154                 # CPM/(µSv/h), =  0.0065 in units of µSv/h/CPM

# calibration of tubes #1, #2, #3
calibration1st      = DefaultSens1st     # calibration factor for the 1st tube
                                          # in most counters this is the only tube
                                          # in a GMC-500+ counter this is the 1st or high sensitivity tube
calibration2nd      = DefaultSens2nd     # calibration factor for the 2nd tube
                                          # in a GMC-500+ counter this is the 2nd or low-sensitivity tube
calibration3rd      = DefaultSens3rd     # calibration factor for the 3rd tube
                                          # to use more than 1 counter simultaneously; mapping set in config

# DEVICES

DevicesConnected    = 0                   # number of connected devices; determined upon connecting

# GMC                                     # will be set after reading the version of the counter from the device
GMCActivation       = False               # To use or not use a GMC Device counter
GMCConnection       = False               # Not connected if False
GMCDeviceName       = None                # to be detected in init; generic name like: "GMC Device"
GMCDeviceDetected   = None                # will be replaced after connection with full specific
                                          # name as detected, like 'GMC-300Re 4.20',
                                          # had been 14 chars fixed, can now be longer
GMC_variables       = "auto"              # which variables are natively supported
GMCLast60CPS        = None                # storing last 60 sec of CPS values
GMCEstFET           = None                # storing last 60 sec of CPS values for estimating the FET effect

# GMC Bugs and settings
GMC_memory          = "auto"              # Can be configured for 64kB or 1 MB in the config file
GMC_SPIRpage        = "auto"              # size of page to read the history from device
GMC_SPIRbugfix      = "auto"              # if True then reading SPIR gives one byte more than
                                          # requested  (True for GMC-300 series)
GMC_locationBug     = ["GMC-500+Re 1.18", # see the FIRMWARE BUGS topic
                       "GMC-500+Re 1.21"] # in the configuration file
GMC_FastEstTime     = "auto"              # if != 60 then false data will result
GMC_endianness      = "auto"              # big- vs- little-endian for calibration value storage
GMC_configsize      = "auto"              # 256 bytes in 300series, 512 bytes in 500/600 series
GMC_voltagebytes    = "auto"              # 1 byte in the 300 series, 5 bytes in the 500/600 series
GMC_nbytes          = "auto"              # the number of bytes the CPM and CPS calls, as well as
                                          # the calls to 1st and 2nd tube deliver ( 2 or 4)
GMCcfg              = None                # Configuration bytes of the counter. 256 bytes in 300series, 512 bytes in 500series
GMC_WifiIndex       = 0                   # the index column in cfgKeyHigh applicable for the current device
GMCsavedatatype     = "Unknown - will become known once the device is connected"
GMCsavedataindex    = None
GMC_WifiEnabled     = False               # does the counter have WiFi or not
GMC_SingleTube      = True                # all are single tube, except 500+, which is doublle tube


# AudioCounter
AudioActivation     = False               # Not available if False
AudioConnection     = False               # Not connected if False
AudioDeviceName     = None                # to be set in init
AudioDeviceDetected = None
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
AudioVariables      = "auto"              #
AudioSensitivity    = "auto"              # units: CPM / (µSv/h)
AudioMultiPulses    = None                # stores the concatenated audio data for plotting
AudioRecording      = None                # stores the Recording
AudioPlotData       = None                # stores the data to be plotted
AudioOei            = None                # the eia storage label


# RadMon stuff
RMActivation        = False               # must be true to use RadMon
RMConnection        = False               # True when initialized by GeigerLog
RMDeviceName        = None                # can currently be only RadMon+
RMDeviceDetected    = None                # can currently be only RadMon+
RMServerIP          = "auto"              # MQTT server IP, to which RadMon sends the data
RMServerPort        = "auto"              # Port of the MQTT server, defaults to 1883
RMServerFolder      = "auto"              # The MQTT folder as defined in the RadMon+ device
RMSensitivity       = "auto"              # calibration factor for the tube used
RMVariables         = "auto"              # a list of the variables to log, T,P,H,R
RMTimeout           = 3                   # waiting for "successful connection" confirmation
RMCycleTime         = 1                   # cycle time of the RadMon device
RMconnect           = (-99, "")           # flag to signal connection
RMdisconnect        = (-99, "")           # flag to signal dis-connection

rm_client           = None                # to be set in gdev_radmon.initRadMon
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
#AmbioAP_IP          = "auto"              # IP address of Ambiomon in Access Point mode, Default = "192.168.4.1"
#AmbioSSID           = "auto"              # SSID of user's WiFi network
#AmbioSSIDPW         = "auto"              # Password of user's WiFi network
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


# Gamma-Scout stuff
GSActivation        = False               # Not available if False; to be set via config
GSConnection        = False               # Not connected if False
GSDeviceName        = None                # to be assigned in GS Init; now: "Gamma-Scout"
GSDeviceDetected    = None                # to be assigned in GS init with specific name, now same "Gamma-Scout"
GSVariables         = "auto"
GSSensitivity       = "auto"              # auto will become 108 in init for the LND712 tube
GStype              = None                # to be set in GS init as: Old, Classic, Online
GSFirmware          = None                # to be set in GS init
GSSerialNumber      = None                # to be set in GS init
GSDateTime          = None                # to be set when setting DateTime
GSusedMemory        = 0                   # to be set when calling History
GSMemoryTotal       = 65280               # max memory acc to manual, page 16, but when mem was 64450 (830 bytes free), interval was already 7d!
GSCalibData         = None                # the Gamma-Scout internal calibration data
GScurrentMode       = None                # "Normal", "PC", "Online"
GStesting           = False               # required to run GS under simulation; used only in module gdev_scout.py,


# I2C stuff
I2CActivation       = False               # Not available if False; to be set via config
I2CConnection       = False               # Not connected if False
I2CDeviceName       = None                # to be assigned in I2c Init; now:
I2CDeviceDetected   = None                # to be assigned in I2C init with specific name,
I2CVariables        = "auto"
I2CThread           = None                # Thread used for I2C
I2CSensor1          = None                # the BME280
I2CSensor2          = None                # the TSL259
I2CFirmware         = None                # to be set in init, but included in DeviceDetected
I2CSerialNumber     = None                # to be set in init, but not available
I2CInfo             = None                # to be set in init

# I2C Dongles
elv                 = None                # becomes instance of the ELV USB-I2C device

# I2C Sensors and Modules
#~bme280              = {
                       #~"name": "BME280",
                       #~"feat": "Temperature, Pressure, Humidity",
                       #~"addr": 0x77,      # (d119)  addr: 0x76, 0x77
                       #~"type": 0x60,      # (d96)   BME280 has chip_ID 0x60
                       #~"hndl": None,      # handle
                       #~"dngl": None,      # connected with dongle
                      #~}

#~tsl2591             = {
                       #~"name": "TSL2591",
                       #~"feat": "Light (Vis, IR)",
                       #~"addr": 0x29,      # (d41)  addr: 0x29
                       #~"type": 0x50,      # Device ID 0x50
                       #~"hndl": None,      # handle
                       #~"dngl": None,      # connected with dongle
                      #~}


# LabJack stuff
LJActivation        = False                     # Not available if False
LJConnection        = False                     # True when initialized by GeigerLog
LJDeviceName        = "None"                    # LabJack U3 with probe EI1050
LJDeviceDetected    = "None"                    # LabJack U3 with probe EI1050
LJVariables         = "auto"                    # a list of the variables to log; auto=T,H,R
LJversionLJP        = "undefined until loaded"  # version of LabJackPython
LJversionU3         = "undefined until loaded"  # version of U3
LJversionEI1050     = "undefined until loaded"  # version of EI1050


# RaspiStuff
RaspiActivation     = False                # Not available if False
RaspiConnection     = False                # Not connected if False
RaspiDevice         = "None"               # to be set in init (the 'audio'device)
RaspiDeviceName     = "None"               # to be set in init
RaspiPulseMax       = 2**15                # +/- 32768 as maximum pulse height for 16bit signal
RaspiPulseDir       = False                # False for negative; True for positive pulse
RaspiThreshold      = 60                   # Percentage of pulse height to trigger a count
                                           # 60% of +/- 32768 => approx 20000
RaspiRate           = 44100                # sampling rate audio; works for most sound cards
RaspiChunk          = 32                   # samples per read
RaspiChannels       = 1                    # 1= Mono, 2=Stereo
RaspiFormat         = None                 # becomes (int16, int16)
RaspiLatency        = None                 # becomes setting in sec

RaspiLastCpm        = 0                    # audio clicks CPM
RaspiLastCps        = 0                    # audio clicks CPS
RaspiLast60CPS      = None                 # np array storing last 60 sec of CPS values
RaspiThreadStop     = False                # True to stop the audio thread
RaspiVariables      = "auto"               #
RaspiCalibration    = "auto"               # units: CPM / (µSv/h)
RaspiMultiPulses    = None                 # stores the concatenated audio data for plotting
RaspiRecording      = None                 # stores the Recording
RaspiPlotData       = None                 # stores the data to be plotted


# SimulCounter
SimulActivation     = False                # Not available if False
SimulConnection     = False                # Not connected if False
SimulDeviceName     = "auto"               # to be set in init
SimulDeviceDetected = "auto"               # to be set in init
SimulMean           = "auto"               # mean value of the Poisson distribution as CPSmean=10
SimulVariables      = "auto"               # default is CPM3rd, CPS3rd
SimulSensitivity    = "auto"               # units: CPM / (µSv/h)
#SimulPredictive     = False                # not making a CPM prediction
#SimulPredictLimit   = 25                   # CPM must reach at least this count before making prediction


# MiniMonCounter
MiniMonActivation     = False              # Not available if False
MiniMonConnection     = False              # Not connected if False
MiniMonDeviceName     = "auto"             # to be set in init
MiniMonDeviceDetected = "auto"             # to be set in init
MiniMonVariables      = "auto"             # default is T, X


#ESP32
terminal            = None                 # for the ESP32


# Logging Options
logging             = False                # flag for logging
logcycle            = 3                    # time in seconds between CPM or CPS calls in logging
lastValues          = None                 # last values received from device
lastRecord          = None                 # last records received from devices
LogReadings         = 0                    # counts readings since last logging start; prints as index in log
LogGetValDur        = NAN                  # duration to get all logged values
LogPlotDur          = NAN                  # duration to plot all logged values
LogTotalDur         = NAN                  # duration to get and plot all logged values

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
mav_initial         = 60                   # length of Moving Average period in seconds
mav                 = mav_initial          # currently selected mav period
fprintMAV           = False                # to print to NotePad the moving average comments

# Plotstyle                                # placeholder; don't change here - is set in config
linestyle           = 'solid'              # overwritten by varsDefault
linecolor           = 'blue'               # overwritten by varsDefault
linewidth           = '1.0'                # configurable in geigerlog.cfg
markerstyle         = 'o'                  # configurable in geigerlog.cfg
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

# DEVICES properties

# holder for devices  of all supported devices with all attribs
Devices = {
           # Device-        Detected-    Var-        Active-
           # Name           Names        Names       Status
            "GMC"        : [None,        None,       False],    # 1
            "Audio"      : [None,        None,       False],    # 2
            "RadMon"     : [None,        None,       False],    # 3
            "AmbioMon"   : [None,        None,       False],    # 4
            "Gamma-Scout": [None,        None,       False],    # 5
            "I2C"        : [None,        None,       False],    # 6
            "LabJack"    : [None,        None,       False],    # 7
            "Raspi"      : [None,        None,       False],    # 8
            "MiniMon"    : [None,        None,       False],    # 9
            "Simul"      : [None,        None,       False],    # 10
          }

# VARIABLES - names and style

# colors at:  https://matplotlib.org/users/colors.html
# linestyles: "solid", "dotted"
varsDefault = { # do not modify this - use copy varsBook !!!!
#                                                        Units
#            (Short)     Long             Very short     CP* can be µSv/h     Style            Style
#            Names,      Names,           Names          T °C can be °F       Color            Line
#            key         0                1              2                    3                4
            "CPM"    : ["CPM",           "M",           "CPM",               "blue",          "solid" ],    # 1
            "CPS"    : ["CPS",           "S",           "CPS",               "magenta",       "solid" ],    # 2
            "CPM1st" : ["CPM1st",        "M1",          "CPM",               "deepskyblue",   "solid" ],    # 3
            "CPS1st" : ["CPS1st",        "S1",          "CPS",               "violet",        "solid" ],    # 4
            "CPM2nd" : ["CPM2nd",        "M2",          "CPM",               "cyan",          "solid" ],    # 5
            "CPS2nd" : ["CPS2nd",        "S2",          "CPS",               "#9b59b6",       "solid" ],    # 6
            "CPM3rd" : ["CPM3rd",        "M3",          "CPM",               "brown",         "solid" ],    # 7
            "CPS3rd" : ["CPS3rd",        "S3",          "CPS",               "orange",        "solid" ],    # 8
            "T"      : ["Temperature",   "T",           "°C",                "red",           "solid" ],    # 9
            "P"      : ["Pressure",      "P",           "hPa",               "black",         "solid" ],    # 10
            "H"      : ["Humidity",      "H",           "%",                 "green",         "solid" ],    # 11
            "X"      : ["Xtra",          "X",           "x",                 "#8AE234",       "solid" ],    # 12
          }

varsBook            = varsDefault.copy()   # need a copy to allow reset as colorpicker may change color

# Index,            DateTime,     CPM,     CPS,  CPM1st,  CPS1st,  CPM2nd,  CPS2nd,  CPM3rd,  CPS3rd,  Temp,   Press,   Humid,   X
# Column No         0             1        2     3        4        5        6        7        8        9       10       11       12
datacolsDefault     = 1 + len(varsDefault) # total of 13: DateTime plus 12 vars (index excluded; is not data),
#print("datacolsDefault: ",datacolsDefault)


# HOUSEKEEPING for VARIABLES

varcheckedCurrent   = {}                   # is variable checked for inclusion in plot
varcheckedLog       = {}                   # is variable checked for inclusion in plot for Log
varcheckedHis       = {}                   # is variable checked for inclusion in plot for History
varlabels           = {}                   # info on avg, StdDev etc; will be set in gsup_plot
loggableVars        = {}                   # Vars which can be logged with current connections

for vname in varsBook.keys():
    varcheckedLog       [vname] = False    # set all false
    varcheckedHis       [vname] = False    # set all false
    varcheckedCurrent   [vname] = False    # set all false
    varlabels           [vname] = ""       # set all to empty
    loggableVars        [vname] = False    # set all False

activeVariables     = 0                    # determined in switchConnections; at least 1 needed for logging
textDevVars         = ""                   # determined in switchConnections, Devices with associated variables
varMap              = {}                   # holds mapping of the variables


# SCALING

# Value - Scaling - this modifies the measured variable;
# the modification will be stored to Database
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

# Graph Sscaling - this does ONLY modify how the data it is plotted
# the modification will NOT be stored to Database
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

By default, data files will be read-from/written-to the data directory
"data", which is a subdirectory to the program directory

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
<p>This will create a database file to store all data downloaded from the internal storage of a device.</p>
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

<p><b>Device: GMC-500+</b></p>

<p>When this device is on firmware 1.18 it identifies itself with an empty identifier,
which prohibits use on GeigerLog. It should identify itself as 'GMC-500+Re 1.18'.</p>

<p>A work-around is to cycle the connection: ON -> OFF -> ON. Then it should work.</p>

<p>This bug is corrected with firmware 1.21. It is recommended to contact GMC support for an update.
The Geiger counter will then identify itself as 'GMC-500+Re 1.21'.</p>
<p>-------------------------------------------------------------------------------</p>
<p><b>Device: GMC-500 / 600 series</b></p>

<p>Some firmware versions, at least 1.18 and 1.21, have a bug (called 'location bug') which
results in errors in the parsing of the history file. It is advised to upgrade at least to
the 1.22 firmware!</p><p>-------------------------------------------------------------------------------</p>

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

<p>A firmare correction has NOT been announced.</p>

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
    <td >(equiv. to permanent:</td>
    <td >  2.3 µSv/h</td>
    <td >  5.7 µSv/h)</td>
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
weather station, complemented with a Geiger counter to monitor radioactivity,
and an In-house CO2 monitoring system.</p>

<p><br>Currently Supported Devices:</p>

<p><b>GMC Devices:</b><br>GeigerLog continuous to support GQ Electronics's
GMC-3xx, GMC-5xx, and GMC-6xx line of classical Geiger counters, including the
variants with an additional 2nd Geiger tube.</p>

<p><b>AudioCounter Devices:</b>
<br>GeigerLog supports Geiger counters which only give an audio click for a
radioactive event.</p>

<p><b>RadMon Devices:</b>
<br>GeigerLog supports the RadMon+ hardware, which can provide a Geiger counter
as well as an environmental sensor for temperature, air-pressure
(atmospheric-pressure), and humidity.</p>

<p><b>AmbioMon Devices:</b>
<br>GeigerLog supports AmbioMon++ hardware, devices which can provide a Geiger
counter as well as an environmental sensor for temperature, air-pressure
(atmospheric-pressure), and humidity.</p>

<p><b>Gamma-Scout Devices:</b>
<br>GeigerLog supports the Geiger counters from Gamma-Scout.</p>

<p><b>LabJack Devices:</b>
<br>GeigerLog supports the u3 and Ei1050 hardware from LabJack.</p>

<p><b>I2C Devices:</b>
<br>GeigerLog supports devices connected by the I2C interface</p>

<p><b>MiniMon Devices - CO2 Monitoring:</b>
<br>GeigerLog supports these In-house CO2 monitoring devices (Linux only)</p>

<p><b>SimulCounter Devices:</b>
<br>A simulated Geiger counter getting its “counts” from a Poisson random
number generator.</p>

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
