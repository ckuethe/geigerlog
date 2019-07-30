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
__copyright__       = "Copyright 2016, 2017, 2018"
__credits__         = [""]
__license__         = "GPL3"
__version__         = "0.9.08a"           # version of next GeigerLog
#__version__         = "0.9.09.rc1"

# supported plugins
phonon              = "inactive"          # allow the use of phonon (alt: active)


# pointers
ex                  = None                # a pointer to ggeiger
notePad             = None                # pointer to print into notePad area
btn                 = None                # the cycle time OK button; for inactivation

# constants
NAN                 = float('nan')        # 'not-a-number'; used as 'missing value'
datacolsDefault     = 11                  # max number of data columns supported, as:
                                          # index, DateTime,
                                          # CPM, CPS, CPM1st, CPM2nd, CPS1st, CPS2nd,
                                          # Temperature, Pressure, Humidity, RadMon CPM.

# for anything which must be defined even if no connection exists
DEFcalibration      = 0.0065              # in units of µSv/h/CPM
DEFcalibration2nd   = 0.194               # in units of µSv/h/CPM
DEFRMcalibration    = 0.0065              # in units of µSv/h/CPM

# scaling
ScaleCPM            = "VAL"               # no scaling
ScaleCPM1st         = "VAL"               # no scaling
ScaleCPM2nd         = "VAL"               # no scaling
ScaleCPS            = "VAL"               # no scaling
ScaleCPS1st         = "VAL"               # no scaling
ScaleCPS2nd         = "VAL"               # no scaling
ScaleT              = "VAL"               # no scaling
ScaleP              = "VAL"               # no scaling
ScaleH              = "VAL"               # no scaling
ScaleR              = "VAL"               # no scaling

# flags
debug               = False               # helpful for debugging, use via command line
verbose             = False               # more detailed printing, use via command line
devel               = False               # set some conditions for development CAREFUL !!!
devel1              = False               # set some ADDITIONAL conditions for development CAREFUL !!!
devel2              = False               # set some more ADDITIONAL conditions for development CAREFUL !!!
debugindent         = ""                  # to indent printing
redirect            = False               # on True redirects output from stdout and stderr to file stdlogPath
testing             = False               # if true then some testing constructs will be activated CAREFUL !!!

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
binFilePath         = None                # file path of the bin file
lstFilePath         = None                # file path of the lst file
hisFilePath         = None                # file path of the his file
currentFilePath     = None                # file path of the current log or his file; in plot
fileDialogDir       = None                # the default for the FileDialog starts

manual_filename     = "GeigerLog-Manual.pdf" # name of the included manual file

# GUI options
window_width        = 1366                # the standard screen of 1366 x 768 (16:9),
window_height       = 768                 #
window_size         = 'maximized'         # 'auto' or 'maximized'
style               = "Breeze"            # may also be defined in config file

# RadMon stuff
RMdevice            = "None"              # can currently be only RadMon+
RMconnect           = (-99, "")           # flag to signal connection
RMdisconnect        = (-99, "")           # flag to signal dis-connection
RMserverIP          = None                # Server IP of the MQTT server, to which
                                          # the RadMon sends the data
RMserverPort        = "auto"              # Port of the MQTT server, defaults to 1883
RMserverFolder      = "auto"              # The MQTT folder as defined in the RadMon+ device
RMcalibration       = "auto"              # calibration factor for the tube used
                                          # in the RadMon+ is set to 0.0065 in InitRadMon,
                                          # unless redefined in config
RMvariables         = "auto"              # a list of the variables to log, T,P,H,R
RMtimeout           = 3                   # waiting for "successful connection" confirmation

client              = None                # to be set elsewhere
rm_cpm              = None                # temporary storage for CPM
rm_temp             = None                # temporary storage for Temperature
rm_press            = None                # temporary storage for Pressure
rm_hum              = None                # temporary storage for Humidity
rm_rssi             = None                # temporary storage for RSSI


# Serial port
ser                 = None                # serial port pointer
baudrates           = [1200, 2400, 4800, 9600, 14400, 19200, 28800, 38400, 57600, 115200]
baudrate            = 115200              # will be overwritten by a setting in geigerlog.cfg file
#usbport             = '/dev/geiger'
usbport             = '/dev/ttyUSB0'      # will be overwritten by a setting in geigerlog.cfg file
timeout             = 3                   # will be overwritten by a setting in geigerlog.cfg file
timeout_write       = 1                   # will be overwritten by a setting in geigerlog.cfg file
ttyS                = "ignore"            # to 'ignore' or 'include' '/dev/ttySN', N=1,2,3,... ports on USB Autodiscovery

# Device Options                          # will be set after reading the version of the counter
deviceDetected      = "auto"              # will be replaced after connection with full
                                          # name as detected, like 'GMC-300Re 4.20'
                                          # had been 14 chars, can now be longer
memory              = "auto"              # Can be configured for 64kB or 1 MB in the config file
SPIRpage            = "auto"              # size of page to read the history from device
SPIRbugfix          = "auto"              # if True then reading SPIR gives one byte more than
                                          # requested  (True for GMC-300 series)
calibration         = "auto"              # factory default calibration factor in device is linear
                                          # i.e. the same for all 3 calibration points
calibration2nd      = "auto"              # calibration factor for the 2nd tube in a GMC-500+ counter
                                          # CPM * calibration => µSv/h
                                          # this is from a calibration point #3 setting
                                          # of 25CPM=4.85µSv/h
#calibration2nd     = 0.390               # there was a calibration point #3 setting
                                          # of 25CPM=9.75µSv/h =>0.39 µSv/h/CPM
#calibration2nd     = 0.480               # calibration determined in own experiment
                                          # http://www.gqelectronicsllc.com/forum/topic.asp?TOPIC_ID=5369
                                          # see Reply #10, Quote: “With Thorium = 0.468, and K40 = 0.494,
                                          # I'd finally put the calibration factor for the 2nd tube, the
                                          # SI3BG, to 0.48 µSv/h/CPM. Which makes it 74 fold less
                                          # sensitive than the M4011!”

endianness          = "auto"              # big- vs- little-endian for calibration value storage
configsize          = "auto"              # 256 bytes in 300series, 512 bytes in 500/600 series
voltagebytes        = "auto"              # 1 byte in the 300 series, 5 bytes in the 500/600 series
variables           = "auto"              # a list of the variables to sample, CPM, CPS, 1st, 2nd
nbytes              = "auto"              # the number of bytes the CPM and CPS calls, as well as
                                          # the calls to 1st and 2nd tube deliver
GMCvariables        = "auto"              # which variables are natively supported

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

#special flags
test1               = False               # to run a specific test; see gcommands
test2               = False               # to run a specific test; see gcommands
test3               = False               # to run a specific test; see gcommands
test4               = False               # to run a specific test; see gcommands

# Logging Options
cpm_counter         = 0                   # counts readings since last start logging; prints as index in log
logging             = False               # flag for logging
logcycle            = 1                   # time in seconds between CPM or CPS calls in logging
cpmflag             = True                # True if CPM, False if CPS
lastValues          = None                # last values received from device
lastRecord          = None                # last records received from devices
loggingBlocked      = False               # logging not permitted; read-only file, or old version of log file

# History Options
keepFF              = False               # Flag in startup-options
                                          # Keeps all hexadecimal FF (Decimal 255) values as a
                                          # real value and not an 'Empty' one. See manual in chapter
                                          # on parsing strategy
fullhist            = False               # If False breaks history recording when 8k FF is read
                                          # if True reads the whole history from memory

# Graphic Options
varnames            = ("CPM", "CPS", "CPM1st", "CPM2nd", "CPS1st", "CPS2nd", "T", "P", "H", "R")

vardict             = {                     # short and long names
                        "CPM"   :"CPM",
                        "CPS"   :"CPS",
                        "CPM1st":"CPM1st",
                        "CPM2nd":"CPM2nd",
                        "CPS1st":"CPS1st",
                        "CPS2nd":"CPS2nd",
                        "T"     :"Temperature",
                        "P"     :"Pressure",
                        "H"     :"Humidity",
                        "R"     :"RadMon CPM",
                      }

vardictshort        = {                     # short and very short names
                        "CPM"   :"M",
                        "CPS"   :"S",
                        "CPM1st":"M1",
                        "CPM2nd":"M2",
                        "CPS1st":"S1",
                        "CPS2nd":"S2",
                        "T"     :"T",
                        "P"     :"P",
                        "H"     :"H",
                        "R"     :"R",
                      }

varunit             = {                     # units of Variable; CPM*, CPS*, T can change
                        "CPM"   :"CPM",
                        "CPS"   :"CPS",
                        "CPM1st":"CPM",
                        "CPM2nd":"CPM",
                        "CPS1st":"CPS",
                        "CPS2nd":"CPS",
                        "T"     :"°C",
                        "P"     :"hPa",
                        "H"     :"%",
                        "R"     :"CPM",
                      }

#print("vardict:", vardict)
#print("vardict.keys:", vardict.keys())
#print("vardict.values:", vardict.values())

# colors at: https://matplotlib.org/users/colors.html
varcolor            = {
                        "CPM"   :"blue",
                        "CPS"   :"magenta",
                        "CPM1st":"cyan",
                        "CPM2nd":"deepskyblue",
                        "CPS1st":"pink",
                        "CPS2nd":"violet",
                        "T"     :"red",
                        "P"     :"black",
                        "H"     :"green",
                        "R"     :"orange",
                      }

vardevice           = {}                  # stores whether variable is avialble at the device
for vname in varnames:     vardevice[vname] = False # set all false
#print("vardevice:", vardevice)

varlog              = {}                  # stores whether variable needs to be logged
for vname in varnames:     varlog[vname] = False   # set all false
#print("vardevice:", vardevice)

varlabels           = {}                  # info on avg, StdDev etc; will be set in gplot
for vname in varnames:     varlabels[vname] = ""    # set all to empty
#print("varlabels:", varlabels)

varchecked          = {}                  # is variable checked for inclusion in plot
for vname in varnames:     varchecked[vname] = False    # set all to false
#print("varchecked:", varchecked)

varcheckedLog       = None #varchecked
varcheckedHis       = None #varchecked


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
mav_initial         = 120                 # length of Moving Average period in seconds
mav                 = mav_initial         # currently selected mav period

# Plotstyle                               # currently not used
linestyle           = 'solid'
linecolor           = 'blue'
linewidth           = '0.5'
markerstyle         = 'o'
markersize          = '10'

#Graph Y-Limits                           # to calculate cursor position for left, right Y-axis
y1_limits           = (0, 1)              # (bottom, top) of y left
y2_limits           = (0, 1)              # (bottom, top) of y right


# Data arrays and values
logTime             = None                # array: Time data from total file
logCPM              = None                # array: CPM Data from total file
logTimeDiff         = None                # array: Time data as time diff to first record in days
logTimeFirst        = None                # value: Time of first record of total file

logTimeSlice        = None                # array: selected slice out of logTime
logTimeDiffSlice    = None                # array: selected slice out of logTimeDiff
logCPMSlice         = None                # array: selected slice out of logCPM
logSliceMod         = None

sizePlotSlice       = None                # value: size of plotTimeSlice

logFileData         = None                # 2dim numpy array with the log data
hisFileData         = None                # 2dim numpy array with the his data
currentFileData     = None                # 2dim numpy array with the currently plotted data

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

cfgLow = {                                       # common to all GMCs
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
cfgMapKeys          =  ("SSID", "Password", "Website", "URL", "UserID", "CounterID", "Period", "WiFi")

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

cfg512ndx = {                                      # GMC-500/600
          "SSID"        : (69,     69 + 32),
          "Password"    : (101,   101 + 32),
          "Website"     : (133,   133 + 32),
          "URL"         : (165,   165 + 32),
          "UserID"      : (197,   197 + 32),
          "CounterID"   : (229,   229 + 32),
          "Period"      : (261,   261 +  1),     #
          "WiFi"        : (262,   262 +  1),     # WiFi OnOff
         }

cfg256ndx = {                                      # only GMC-320+V5
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
    -h, --help          Show this help and exit
    -d, --debug         Run with printing debug info
                        Default is debug = False
    -v, --verbose       Be more verbose
                        Default is verbose = False
    -V, --Version       Show version status and exit
    -p, --port name     Sets the USB-Port to name
                        Default is name = /dev/ttyUSB0
    -b, --baudrate N    Sets the baudrate to N
                        Default is N = 57600
    -R  --Redirect      Redirect stdout and stderr to
                        file geigerlog.stdlog (for debugging)
        -style name     Sets the style; see Commands:
                        'showstyles'
                        Default is set by your system

Commands:
    showstyles          Show a list of styles avail-
                        able on your system and exit.
                        For usage details see manual
    keepFF              Keeps all hexadecimal FF
                        (Decimal 255) values as a
                        real value and not an 'Empty'
                        one. See manual in chapter
                        on parsing strategy
    devel               Development settings; careful!
                        see program code

To watch debug and verbose output start the program from the
command line in a terminal. The output will print to the terminal.

With the Redirect option all output - including Python error
messages - will go into the redirect file geigerlog.stdlog.
"""

helpQuickstart = """
<style>h3 { color: darkblue; margin:5px 0px 5px 0px; padding:0px; } p, ol, ul { margin:4px 0px 4px 0px; padding:0px;} </style>
<H3>Mouse Help</H3><p>resting your mouse cursor briefly over an item of the window shows a ToolTip message providing info on the item!
<br><br>Assuming a USB cable is connecting computer and device:</p>
<h3>USB Port and Baudrate</h3>
<p>If you do know your USB Port and baudrate setting, start GeigerLog with these options:<br>
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
<span style="font-family:'Courier';margin:30px;">geigerlog -p yourport -b yourbaudrate</span>
<br>On a Linux system e.g.:
&nbsp;&nbsp;&nbsp;&nbsp;<span style="font-family:'Courier';margin:30px;">geigerlog -p /dev/ttyUSB0 -b 57600</span>

<br>On a Windows system e.g.:
&nbsp;&nbsp;<span style="font-family:'Courier';margin:30px;">geigerlog -p COM3 -b 57600</span></p>

<p>If you don't know your settings read the manual first in chapter 'Connecting GMC - Devices' before you start the <b>USB Autodiscovery</b> in the Help menu.</p>

<h3>Start Logging</h3>
<ol>
<li>Connect the computer with the devices<br>(menu: Device -> Connect Devices, or click the 'Connect' button)</li>
<li>Switch GMC device on (menu: Device -> GMC Series -> Switch Power ON)</li>
<li>Load a log file (menu: Logging -> Get Log File or Create New One)<br>
In the Get Log File dialog enter a new filename and press Enter,
<br>or select an existing file to <b>APPEND</b> new data to this file</li>
<li>Start logging (menu: Log -> Start Logging, or click the 'Start Log' toolbar icon)</li>
</ol>

<h3>Get History from Device</h3>
<ol>
<li>Connect the computer with the devices<br>(menu: Device -> Connect Devices, or click the 'Connect' button)</li>
<li>Get history from device (menu: History  -> Get History from Device)</li>
<li>Enter a new filename (e.g. enter 'myfile' and press Enter) or select an existing file
<br>Note: selecting an existing file will <b>OVERWRITE</b> this file!</li>
</ol>
&nbsp;&nbsp;This will download all data from the internal storage of the device and create three files:
<ul>
<li>a binary file 'myfile.bin' containing a duplicate of the internal data</li>
<li>a text file &nbsp;&nbsp;'myfile.lst' containing the binary data in a human readable format</li>
<li>a text file &nbsp;&nbsp;'myfile.his' containing data parsed from the binary</li>
</ul>
<h3>Graphical Analysis</h3>
<p>To zoom into the graph either enter the Time Min and
Time Max values manually, or much easier, do a mouse-left-click to the left
of the feature in the graph and right-click to the right, and then click the Apply button.
Use other features as detailed in the manual.</p>

<h3>More in the GeigerLog Manual</h3>
<p>Available locally (menu: Help -> GeigerLog Manual) and <a href="https://sourceforge.net/projects/geigerlog/files/GeigerLog-Manual.pdf">online</a>
at SourceForge project GeigerLog: <a href="https://sourceforge.net/projects/geigerlog/">https://sourceforge.net/projects/geigerlog/</a></p>
"""



helpWorldMaps = """
<style>h3 { color: darkblue; margin:5px 0px 5px 0px; padding:0px; } p, ol, ul, li { margin:4px 0px 10px 0px; padding:0px;} </style>

<H3>Radiation World Maps</H3>

<p>Several web sites exist, which attempt to show a worldwide map of the
<b>BACKGROUND</b> radioactivity, hoping to be of help to the people in case of
a nuclear emergency, which will result in elevated levels of radioactivity.
Some are run by governments, others by enthusiastic hobbyists.</p>

<p>Among the latter ones are:</p>

<ul>
<li><a href='http://www.gmcmap.com/' >gmcmap.com</a> - This is the one supported by GQ Electronics</li>
<li><a href='https://radmon.org/index.php' >radmon.org</a> - Presently closed for new users after being hacked</li>
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
    <th >Germany</th>
    <th >USA</th>
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
<p><span style='color:darkblue;'><b>GeigerLog</b></span> is a combination of data logger, data presenter, and data analyzer.</p>

<p>It is based on Python (Version 3), hence it runs on Linux, Windows, Macs, and other systems.</p>

<p>GeigerLog had initially been developed for the sole use with Geiger counters, but has now become
a more universal tool, which equally well handles environmental data like temperature, air-pressure,
and humidity, and is prepared for future sensors.</p>

<p>In its present state it can e.g. be deployed as a
monitor for a remote weather station, complemented with a Geiger counter to monitor radioactivity.</p>

<p><br>Currently Supported Devices:</p>

<p><b>GMC Devices:</b></p>
<p>GeigerLog continuous to support GQ Electronics's GMC-3xx, GMC-5xx, and GMC-6xx line
of classical Geiger counters, including the variants with an additional 2nd Geiger tube.</p>

<p><b>RadMon+ Devices:</b></p>
<p><b><span style='color: red;'>New: </span></b>Support of the RadMon+ hardware, which can provide a Geiger counter as well as an
environmental sensor for temperature, air-pressure (atmospheric-pressure), and humidity.</p>

<p><br>The most recent version of GeigerLog can be found at project GeigerLog at Sourceforge:
<a href="https://sourceforge.net/projects/geigerlog/">https://sourceforge.net/projects/geigerlog/</a>.
An up-to-date GeigerLog-Manual is there as well.</p>

<p>References:
<br>&nbsp;&nbsp;Author.............: {}
<br>&nbsp;&nbsp;Version GeigerLog..: {}
<br>&nbsp;&nbsp;Copyright..........: {}
<br>&nbsp;&nbsp;License............: {} see included file 'COPYING' and <a href="http://www.gnu.org/licenses">http://www.gnu.org/licenses</a>
"""


helpFirmwareBugs = """==== Help on Geiger Counter Firmware Bugs ====================================\n
This provides info on recently discovered bugs in the Geiger counters.

Device Model Name:  GMC-500+

When this device is on firmware 1.18 it identifies itself with an empty identifier,
which prohibits use on GeigerLog. It should identify itself as 'GMC-500+Re 1.18'.

A work-around is to cycle the connection: ON --> OFF --> ON. Then it should work.

This bug is corrected with firmware 1.21. It is recommended to contact GMC support for an update.
The Geiger counter will then identify itself as 'GMC-500+Re 1.21'.
"""
