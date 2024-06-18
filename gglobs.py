#! /usr/bin/env python3
# -*- coding: UTF-8 -*-

"""
gglobs.py - GeigerLog's Super-Global Variables; can be read and modified in all scripts

include in programs with:
    import gglobs as g
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

__author__           = "ullix"
__copyright__        = "Copyright 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024"
__credits__          = [""]
__license__          = "GPL3"
__version__          = "1.5.0"             # version of next GeigerLog
__version__          = "1.5.0"             # final release



# constants
NAN                  = float('nan')        # 'not-a-number'; used as 'missing value'
PINF                 = float('inf')        # plus infinity
MINF                 = float('-inf')       # minus infinity
PI                   = 3.141592653589793   # Pi (decimals limited to max number that Python can handle)
EUL                  = 2.718281828459045   # Euler's Number (taken from numpy.exp(1))

GiB                  = 2**30               # 1 Gibi Byte = 1 073 741 824 Byte
MiB                  = 2**20               # 1 Mebi Byte =     1 048 576 Byte
KiB                  = 2**10               # 1 Kibi Byte =         1 024 Byte

# convert µSv/hour to mSv/annum
ush2msa              = 24 * 365.25 / 1000  # = 8.772 - conversion: 1 µSv/h * 8.772 => 8.772 mSv/a (NOTE: approx. Factor 10)


# Timezone, Time Zone
TimeZoneOffset       = 0                   # value in sec;  ADD this to a UTC time as found by julianday()
                                           # The UTC offsets range from UTC−12:00 to UTC+14:00 (https://en.wikipedia.org/wiki/Time_zone),
                                           # equiv to -12*3600 ... +14*3600 sec = -43200 ... 50400 sec
                                           # Germany winter: +1h, Summer: +2 h (+3600 sec ; +7200 sec)

# A Julian Day is the number of days since Nov 24, 4714 BC 12:00pm Greenwich time in the Gregorian calendar
JULIANUNIXZERO       = 2440587.5           # julianday('1970-01-01 00:00:00') (UNIX time start) (in UTC)
                     # 2440587.5416666665  # in localtime (@DE 19.5.23) ---  1 h difference (looks like timezone difference)

JULIAN111            = 1721425.5 - 1       # julianday('0001-01-01 00:00:00') (matplotlib time start) in UTC
                                           # Why this minus 1? strange but needed
                     # 1721425.5           # select julianday('0001-01-01 00:00:00'), res:(1721425.5,)


MPLDTIMECORRECTION   = None                # to be set in gsup_utils.py to -719163.0

GooColors            = ('#ea4335',         # Google color red      (234,  67,  53)
                        '#fbbc05',         # Google color yellow   (251, 188,   5)
                        '#34a853',         # Google color green    ( 52, 168,  83)
                        '#4285f4',         # Google color blue     ( 66, 133, 244)
                       )

# IDs
geigerlog_pid        = None                # GeigerLog PID


# Computer hardware
CPU_Model            = "Undefined"         # like: Intel(R) Core(TM) i7-4771 CPU @ 3.50GHz
CPU_Hardware         = "Undefined"         # like: BCM2835 for Raspi 4 (kein Wert bei Raspi 5)
CPU_Vendor           = "Undefined"         # like: GenuineIntel


# Logging
logging              = False               # flag for logging
LogCycle             = 1                   # time in seconds between calls in logging
LogThreadStartTime   = None                # time stamp of logging thread started
lasttime             = 0
nexttime             = 0                   # the begin of the next log cycle (set in LogThreadTarget())
nextnexttime         = 0                   # the begin of the log cycle after the next onw (set in LogThreadTarget())

# counters
xprintcounter        = 0                   # the count of dprint, vprint, and wprint commands
LogReadings          = 0                   # number of readings since last logging start; prints as index in log
LogReadingsFail      = 0                   # number of FAILED readings since last logging start


# messages
python_version       = ""                  # msg wrong Python version
startupProblems      = ""                  # msg configuration file missing or incorrect, Python problems, ...
importProblem        = ""                  # import problem (currently only with Telegram code)
configAlerts         = ""                  # msg ALERTs when reading config
notePadSearchText    = ""                  # last entered search text
SnapRecord           = ""                  # record to be used in snapLogValue(self)
LogHeaderText        = ""                  # The header for the LogPad: Time     M     S     M1    S1 ...
versions             = "undefined"         # becomes a dict with versions of all modules and more


# data storage
FibonacciSpeed       = None                # holds the Fibonacci Speed calculation done at entry
HashSpeed            = None                # holds the Hash Speed calculation done at entry
GLBenchmark          = None                # holds the GeigerLog Benchmark (GLBM) value
LimitFileSize        = 5e5                 # if proglog file reaches this size then zip it to archive
writeDevelproglog    = False               # if true write a separate geigerlog.proglog.devel file, duplicating geigerlog.proglog; is set in gmain.py
DurUpdate            = {}                  # duration of various update during logging
DurUpdate["MEM"]     = NAN                 #    - duration of a single memory update
DurUpdate["GRAPH"]   = NAN                 #    - duration of a single Graph update


# GeigerLog Manual
manual_filename      = "auto"              # name of the included GeigerLog Manual, like "GeigerLog-Manual-v1.5.pdf".
                                           # Can also have a path, like: "/path/to/GeigerLog-Manual-v1.5.pdf".
                                           # On 'auto' GL searches for a file with name beginning with 'GeigerLog-Manual'.
                                           # It first searches in the GeigerLog "gmanual" directory, then online.


# pointers
app                  = None                # points to app
exgg                 = None                # points to ggeiger
notePad              = None                # points to print into notePad area
logPad               = None                # points to print into logPad area
btn                  = None                # points to the cycle time OK button; for inactivation
plotAudioPointer     = None                # points to the dialog window of plotaudio
plotScatterPointer   = None                # points to the dialog window of plotscatter
plotScatterFigNo     = None                # points to the window number of plotscatter
iconGeigerLog        = None                # points to the QIcon pixmap for 'icon_geigerlog.png'
iconGeigerLogWeb     = None                # points to the 'icon_geigerlog.png' bin files for Web
bboxbtn              = None                # points to button box of GMC_popuo
monitorfig           = None                # points to the fig of Monitor
monitorax            = None                # points to the ax of Monitor
myarr                = None                # arrow of Monitor
monitorFigNo         = None
LogThread            = None                # Thread handle logging
LogThreadRunFlag     = False               # flag to signal stop for logging
# LogThreadStartTime   = None                # time stamp of logging thread started
CheckThread          = None                # Thread handle checking


FigMainGraph         = None                # pointer to main graph fig
dispLastValsWinPtr   = None                # pointer to Display Last Vals Window


# sql database
currentConn          = None                # connection to CURRENT database
logConn              = None                # connection to LOGGING database
hisConn              = None                # connection to HISTORY database


# flags
debug                = False               # helpful for debugging, use via command line
debugIndent          = ""                  # to indent printing by insering blanks
verbose              = False               # more detailed printing, use via command line
werbose              = False               # more verbose than verbose
devel                = False               # set some conditions for development CAREFUL !!!
traceback            = False               # to allow printout of Traceback under devel=True
CustomStyle          = None                # holder for any user-given Style (line Fusion, Windows,...)


# auto-start
autoLogFile          = "default.logdb"     # name of LogFile to be used
autoDevConnect       = False               # auto connect all activated devices
autoLogStart         = False               # auto start with current LogFile
autoLogLoad          = False               # auto load named LogFile
autoQuickStart       = False               # auto Quick Start

forcelw              = True                # True: line wrapping on lines longer than screen
stopPrinting         = False               # to stop long prints of data
LogClickSound        = False               # when true make a click sound on call to runLoggingCycle
startflag            = False               # for start by Web
stopflag             = False               # for stop by Web
quickflag            = False               # for quick starting from the web
plotIsBusy           = False               # makePlot is ongoing
savingPlotIsBusy     = False               # saving Plot is ongoing
needGraphUpdate      = False               # does the graph need update with new log data
MemDataQueue         = None                # becomes deque - the datalist to be saved to memory
SaveLogValuesQueue   = None                # becomes deque - the datalist to be saved to DB
LogPadQueue          = None                # becomes deque - the text to be shown on LogPad after a Log roll
qefprintMsgQueue     = None                # becomes deque - cannot fprint() from threads; so put msg in queue and do it from checkloop
SoundMsgQueue        = None                # becomes deque - likewise for sound

needDisplayUpdate    = False               # Flag to signal need to show display vars
logCycleBtnRequestOn = False               # request switching cycle button to "On"
LogCycleStart        = NAN                 # time the log cycle button was switched Off
durCheckActive       = 0                   # total time spend in runCheckCycle during 1 LogCycle
durCheckIdle         = 0                   # doing nothing in runCheckCycle during 1 LogCycle
countCheckActive     = 0                   # number of times the loop was passed idle
countCheckIdle       = 0                   # number of times the loop was passed active
runCheckIsBusy       = False               # flag to avoid restarting function when active

logCycleBtnTimeOn    = NAN                 # time the log cycle button was switched On
LogFileAppendBlocked = False               # if true, then block writing to log file
PoissCurveFit        = True                # when True will draw Histogram with Poisson curve and Residual
CumPoissCurveFit     = True                # when True will draw Histogram with cumulative Poisson curve
NormalPoissCurveFit  = False               # when True will draw Histogram with NORMAL curve with StdDev=sqr(mean)
NormalCurveFit       = False               # when True will draw Histogram with NORMAL curve with StdDev=from data
ProbDist             = True                # Probability Distribution
CumProbDist          = False               # Cumulative Probability Distribution

GraphFormula         = False               # Scaling for Graph, i.e. requiring arrays
scaleVname           = ""                  # the variable name (vname) currently being used in scaling calculations


#special flags
testing              = False               # if true then some testing constructs will be activated CAREFUL !!!
graphbold            = False               # if true then line properties will be modified for demo emphasis
graphConnectDots     = True                # if true then dots will be connected with lines
GraphAction          = True
timing               = False               # if true then allows info on timing to be written to Manu vars
lastLogLineClear     = False               # clears the last logpad line when true


# virtual enironment
VenvName             = None                # name of active venv (if there is one)
isSetVenv            = False               # flag showing venv is set
VenvMessage          = ""                  # Either: "Yes, running from venv" or "No, NOT running from venv"
useVenvDirectory     = False               # flag to signal the use (True) or not-use (False) of any venv in use
# useVenvDirectory     = True               # flag to signal the use (True) or not-use (False) of any venv in use

# dir & file paths
dataDirectory        = "data"              # the data subdirectory to the program directory
configDirectory      = "gconfig"           # directory for config files
gresDirectory        = "gres"              # location of the icons and sounds
webDirectory         = "gweb"              # location of html and js files
toolsDirectory       = "gtools"            # location of tools
manualDirectory      = "gmanual"           # location of GeigerLog manual

progName             = None                # program name geigerlog (or geigerlog.py)
progDir              = None                # path to program geigerlog file
dataDir              = None                # path to data dir  (created in GL main)
configDir            = None                # path to config dir  (created in GL main)
resDir               = None                # path to icons and sounds dir
webDir               = None                # path to web fles html, js
proglogFile          = None                # path to program log file geigerlog.proglog
configFile           = None                # path to configuration file geigerlog.cfg
settingsFile         = None                # path to settings file geigerlog.settings

logFilePath          = None                # file path of the log CSV file
hisFilePath          = None                # file path of the his CSV file
logDBPath            = None                # file path of the log database file
hisDBPath            = None                # file path of the his database file
currentDBPath        = None                # file path of the current DB file for either log or his

binFilePath          = None                # file path of the bin file (GMC device)
datFilePath          = None                # file path of the bin file (Gamma Scout device)
AMFilePath           = None                # file path of the bin file (AmbioMon device, either *CAM or *.CPS file)

activeDataSource     = None                # can be 'Log' or 'His'

blockDBwriting       = False               # a flag to signal that DB writing is in progress


# Data arrays and values
logTime              = None                # array: Time data from total file
logTimeDiff          = None                # array: Time data as time diff to first record in days
logTimeFirst         = None                # value: Time of first record of total file

logTimeSlice         = None                # array: selected slice out of logTime
logTimeDiffSlice     = None                # array: selected slice out of logTimeDiff
logSliceMod          = None

logDBData            = None                # 2dim numpy array with the log data
hisDBData            = None                # 2dim numpy array with the his data
currentDBData        = None                # 2dim numpy array with the currently plotted data

dataSlicerecmax      = None                # max record currently shown in plot

fileDialogDir        = None                # the default for the FileDialog starts

HistoryDataList      = []                  # where the DB data are stored by makeHist
HistoryParseList     = []                  # where the parse comments are stored by makeHist
HistoryCommentList   = []                  # where the DB comments are stored by makeHist

# Formula Interpreter
prevtimePointPara    = 0                   # used in PARA_POISSON
lasteventPara        = -1                  # used in PARA_POISSON
prevtimePointNopa    = 0                   # used in NOPA_POISSON
lasteventNopa        = -1                  # used in NOPA_POISSON
useGraphScaledData   = True                # used for calling Qualitytest functions: SuSt, Stats, etc

# GUI options
window_width         = 1366                # the standard screen of 1366 x 768 (16:9),
window_height        = 768                 #
window_size          = "auto"              # 'auto' or 'maximized'
windowStyle          = "auto"              # may also be defined in config file
displayLastValsIsOn  = False               # On True the displayLastValuesWindow windows is shown
displayLastValsGeom  = ("", "", "", "")    # posX, posY, sizeX, sizeY of displayLastValuesWindow
hidpi                = False               # if true the AA_EnableHighDpiScaling will be applied
hipix                = False               # if true the AA_UseHighDpiPixmaps will be applied
hidpiActivation      = True                # The PyQt5 commands hidpi and hipix will be applied
hidpiScaleMPL        = 100                 # 100 is the default dpi for matplotlib

# GUI Layout settings
WinSettingsDefault   = True                 # use the defaultsettings (if settingsfile could not be read)
SettingsNeedSaving   = True                 # save the settings when they are different from the old ones
WinGeomDefault       = [564, 27, 1366, 768]
WinGeom              = WinGeomDefault
NewWinGeom           = WinGeomDefault
WinSplitDefault      = (321,125, 1310, 702) # split on the left side, and on the full window
WinSplit             = WinSplitDefault
NewWinSplit          = WinSplitDefault
InitSettings         = None
InitSettingsOld      = None


# History Options
keepFF               = False                # Flag in startup-options
                                            # Keeps all hexadecimal FF (Decimal 255) values as a
                                            # real value and not an 'Empty' one. See manual in chapter
                                            # on parsing strategy
fullhist             = False                # On False break history recording when 8k FF is read
                                            # On True always read the whole history from memory

# Graphic Options
allowGraphUpdate     = True                 # to block updates on reading data

Xleft                = None                 # time min if entered
Xright               = None                 # time max if entered
Xunit                = "Time"               # time unit; can be Time, auto, second, minute, hour, day
XunitCurrent         = Xunit                # current time unit

Ymin                 = None                 # CPM min if entered
Ymax                 = None                 # CPM max if entered
Yunit                = "CPM"                # CPM unit; can be CPM, CPS, µSv/h
YunitCurrent         = Yunit                # current count unit

Y2min                = None                 # Ambient min if entered
Y2max                = None                 # Ambient max if entered
Y2unit               = "Amb"                # Ambient unit °C or °F
Y2unitCurrent        = Yunit                # current Ambient unit

avgChecked           = False                # Plot the lines Average, +/- 95% confidence, and Legend with average +/- StdDev value
mavChecked           = False                # Plot the Moving Average line, and Legend with MovAvg length ins seconds and data points
fitChecked           = False                # Plot a fit to the data of the selected variable
mav_initial          = 600                  # length of Moving Average period in seconds
mav                  = mav_initial          # currently selected mav period

# Plotstyle                                 # placeholder; don't change here - is set in config
linestyle            = 'solid'              # overwritten by VarsCopy
linecolor            = 'blue'               # overwritten by VarsCopy
linewidth            = '1.0'                # configurable in geigerlog.cfg
markersymbol         = 'o'                  # configurable in geigerlog.cfg
markersize           = '15'                 # configurable in geigerlog.cfg

#Graph Y-Limits                             # to calculate cursor position for left, right Y-axis
y1_limits            = (0, 1)               # (bottom, top) of y left
y2_limits            = (0, 1)               # (bottom, top) of y right


# Network
# SSID and Password length:
#   from IEEE specification:
#   "The length of an SSID should be a maximum of 32 characters (32 octets, normally ASCII
#   letters and digits, though the standard itself doesn't exclude values). Some access
#   point/router firmware versions use null-terminated strings and accept only 31 characters."
#   NOTE:           1 octet  = 1 byte of 8 bits  = 1 ASCII character
# Example:
#   WiFiSSID:     max: 32 octets:  123456789:123456789:123456789:12
#   WiFiPassword: max: 63 octets:  pp3456789:pp3456789:pp3456789:pp3456789:pp3456789:pp3456789:pp3
WiFiSSID                = None                 # WiFi SSID
WiFiPassword            = None                 # WiFi Password
GeigerLogIP             = None                 # IP of computer running GeigerLog


#
# WEB
#
# Monitor WebServer
MonServer                = None                # holds instance of (SSL-)http-server
MonServerAutostart       = True                # on True MonServer will be autostarted
MonServerIsActive        = False               # MonServer must first be activated
MonServerPorts           = "auto"              # list of Port numbers from which MonServer selects port to listen; auto defaults to one of 8080, ..., 8089
MonServerPort            = None                # the port number MonServer listens to
MonServerWebPage         = None                # the last web page displayed; for GL to return to
MonServerRefresh         = [1, 10, 3]          # the refresh timings for the web pages Monitor, Data, Graph in sec
MonServerThresholds      = (0.9, 6.0)          # Dose Rate Thresholds in µSv/h -- green-to-yellow and yellow-to-red
                                               # For reasons to chose these levels see GeigerLog manual, chapter:
                                               # "On what grounds do we set the radiation safety levels?"
MonServerColors          = (GooColors[2],      # Gauge color green   - ok
                            GooColors[1],      # Gauge color yellow  - warning
                            GooColors[0],      # Gauge color red     - danger
                           )
MonServerThread          = None                # Monitor Threads
MonServerMsg             = ""                  # any message created within Do_get()
# MonServerUTCcorr         = "auto"              # the correction to apply to compensate for UTC (Germany, summertime: -2*3600 sec)
MonServerSSL             = False               # using SSL (https://) or not (http://)
MonServerPlotLength      = 10                  # last X min of records to show in line plots
MonServerPlotTop         = 0                   # the variable number of the top plot     (0=CPM, ..., 11=Xtra)
MonServerPlotBottom      = 1                   # the variable number of the bottom plot  (0=CPM, ..., 11=Xtra)
MonServerPlotConfig      = "auto"              # combines Plot- Length, Top, Bottom
MonServerDataConfig      = "auto"              # combines Data table averageing periods in minutes


# Radiation World Map
RWMmapActivation         = False               # Radiation World Map Activation
RWMmapUpdateCycle        = 60                  # Radiation World Map Update Cycle in minutes
RWMmapVarSelected        = "CPM"               # name of the variable used to update Radiation world Map
RWMmapUpdate             = False               # on True an update of Radiation World Map is due
RWMmapLastUpdate         = 0                   # time of the last update of Radiation World Map

# gmcmap specific
gmcmapWebsite            = "www.gmcmap.com"
gmcmapURL                = "log2.asp"
gmcmapUserID             = "anyUserId"
gmcmapCounterID          = "anyCounterID"


##
## USB-To-Serial
##

# Python's pyserial enums
#     import serial :   NOT pyserial! But the module is pip-installed as 'pyserial'
#
#     finding parameters supported by pyserial :
#     myser  = serial.Serial()
#     print(myser.XYZ)
#     myser           : Serial<id=0x7f7a05b18d68, open=False>(port=None, baudrate=9600, bytesize=8, parity='N',
#                       stopbits=1, timeout=None, xonxoff=False, rtscts=False, dsrdtr=False)

#     myser.BAUDRATES : 50, 75, 110, 134, 150, 200, 300, 600, 1200, 1800, 2400, 4800, 9600,
#                       19200, 38400, 57600, 115200, 230400, 460800, 500000, 576000, 921600,
#                       1000000, 1152000, 1500000, 2000000, 2500000, 3000000, 3500000, 4000000
#     myser.BYTESIZES : 5, 6, 7, 8
#     myser.STOPBITS  : 1, 1.5, 2
#     myser.PARITIES  : 'N', 'E', 'O', 'M', 'S'
#                       serial.PARITY_NONE     = N
#                       serial.PARITY_EVEN     = E
#                       serial.PARITY_ODD      = O
#                       serial.PARITY_MARK     = M
#                       serial.PARITY_SPACE    = S

#
# Chips in use for USB-To-Serial:
#
# EmfDev:
#       Yes we are using the CH340 chip so far with all GMC-300+ and 500+ devices.
#       And just check with our latest one also has the VID:PID=0x1a86:0x7523
#     from: http://www.gqelectronicsllc.com/forum/topic.asp?TOPIC_ID=9784
#
#     gmc300E+ (von Jan 21)   device:       /dev/ttyUSB0    description:  USB Serial    vid:  0x1a86     pid:  0x7523
#     gmc300E+ (von ???   )   device:       /dev/ttyUSB0    description:  USB2.0-Serial vid:  0x1a86     pid:  0x7523
#     gmc500+  (2018?)        device:       /dev/ttyUSB0    description:  USB2.0-Serial vid:  0x1a86     pid:  0x7523
#     --> all 3 devices: chip  = CH340C
#     manufacturer: http://wch-ic.com/   http://wch-ic.com/products/CH340.html
#     Nanjing Qinheng Microelectronics Co., Ltd.
#     Main brand： WinChipHead (WCH)
#     "Full speed USB device interface, USB 2.0 compatible."
#     CH340 supports common baud rate: 50, 75, 100, 110, 134.5, 150, 300, 600, 900, 1200, 1800, 2400, 3600, 4800, 9600, 14400, 19200,
#     28800, 33600, 38400, 56000, 57600, 76800, 115200, 128000, 153600, 230400, 460800, 921600, 1500000, 2000000 etc.

GMCbaudrates         = [57600, 115200]
I2Cbaudrates         = [115200]
GSbaudrates          = [2400, 9600, 460800]

# Serial port for GMC devices
GMCser               = None                # GMC serial port pointer
GMC_usbport          = "auto"              # will be set in code
GMC_baudrate         = "auto"              # will be set in code
GMC_timeoutR         = "auto"              # will be set in code
GMC_timeoutW         = "auto"              # will be set in code
GMC_timeoutR_getData = "auto"              # will be set in code; serial timeout for reading, used for getting values
GMC_ID               = (None, None)        # Model, SerialNumber of device
fSVStringSet         = False               # when true there was an error

# Serial port for I2C devices
# I2Cser             = None                # not used! I2C serial use is Dongle-specific
I2Cusbport           = "auto"              # will be overwritten in code
I2Cbaudrate          = "auto"              # is used as fixed value
I2CtimeoutR          = "auto"              # will be  set in code
I2CtimeoutW          = "auto"              # will be  set in code
I2C_ID               = (None, None)        # not in use!!!   (Model, SerialNumber) of device

# Serial port for Gamma-Scout devices
GSser                = None                # Gamma-Scount serial port pointer
GSusbport            = "auto"              # will be set in code
GSbaudrate           = "auto"              # will be set in code
GStimeoutR           = "auto"              # will be set in code
GStimeoutW           = "auto"              # will be set in code
GS_ID                = (None, None)        # Model, SerialNumber of device
GSstopbits           = "auto"              # will be set in code    # used only by GammaScout
GSbytesize           = "auto"              # will be set in code    # used only by GammaScout
GSparity             = "auto"              # will be set in code    # used only by GammaScout


##
## TUBE SENSITIVITY
##
###############################################################################
## Beginning with version GeigerLog 1.0 the 'Calibration' is replaced with
## 'Sensitivity', which is defined as the inverse of the previous definitions,
## i.e. 0.0065 µSv/h/CPM becomes 1/0.065 => 153.85 CPM/(µSv/h).
## This is rounded to 154 CPM/(µSv/h) to use no more than 3 valid digits.
## For reasons for this change see the GeigerLog manual, but in short a tube with
## a higher number for Sensitivity now does have a higher sensitivity!
###############################################################################

# GMC Specifics:
# The GMC factory default so-called calibration factor is linear, i.e. the same
# for all 3 calibration points defined in a GMC counter. For a M4011 tube the
# calibration factor implemented in firmware is 0.0065 µSv/h/CPM.
# For a LND-7317 tube (GMC-600+) the sensitivity is 154 CPM / (µSv/h).
#
# For the 2nd tube in a GMC500+ device, different factors were seen:
# E.g.: from a calibration point #3 setting of '25 CPM=4.85µSv/h' the calibration
# factor is 0.194 µSv/h/CPM (5.15 CPM/(µSv/h)). While a calibration point #3 setting
# of '25CPM=9.75µSv/h' results in 0.39 µSv/h/CPM (2.56 CPM/(µSv/h))!
#
# However, these are significantly different from calibration factors determined
# in my own experiments as reported here:
# http://www.gqelectronicsllc.com/forum/topic.asp?TOPIC_ID=5369, see Reply #10,
# Quote: “With Thorium  = 0.468, and K40  = 0.494, I'd finally put the sensitivity
# of the 2nd tube, the SI3BG, to 0.48 µSv/h/CPM, which makes it 74 fold less
# sensitive than the M4011!”
#
# Others report even poorer values for the SI3BG:
# https://www.gqelectronicsllc.com/forum/topic.asp?TOPIC_ID=5554, Reply #17
# "The new correction factor for the primarily gamma tube is .881CPM/uSv/h or 1.135."
# This means sensitivity of that (2nd) tube  = 1.135 µSv/h/CPM

# Tube changes in GMC counters:
# see: topic: Is my GMC 500+ genuine? http://www.gqelectronicsllc.com/forum/topic.asp?TOPIC_ID=10006
# "The SI3-BG tube has been replaced with something called J707"

# Default Sensitivity
# A total of 4 tubes are available. They are strictly associated with the variables. So when
# a variable XYZ is configured for any device, then the sensitivity for variable XYZ will be used.
# However, in GMC counters their meaning is special.
#
# Tube No   used for variables    Default       Special associations in a GMC counter
#                                 Sensitivity
#                                 CPM/(µSv/h)
# --------------------------------------------------------------------------------------------
# Tube #0   CPM, CPS              154           Default tube in all GMC counters;
#                                               In a GMC-500+ counter the counts are the sum of 1st and
#                                               2nd tube, which is a meaningless value.
#
# Tube #1   CPM1st, CPS1st        154           In all GMC counters exactly the same as tube #0, except: in a
#                                               GMC-500+ counter this is the 1st or high-sensitivity tube.
#
# Tube #2   CPM2nd, CPS2nd        2.08          In all GMC counters exactly the same as tube #0, except: in a
#                                               GMC-500+ counter this is the 2nd or low-sensitivity tube.
#
# Tube #3   CPM3rd, CPS3rd        154           not used in GMC counters.
#
# Final setting is done in 'switchAllDeviceConnections()'
#
DefaultTubeSens         = [154, 154, 2.08, 154]
TubeSensitivity         = ["auto"] * 4
Sensitivity             = ["auto"] * 4


##########################################################################################
# DEVICES CONFIGURATION DETAILS
##########################################################################################

#
# GMC device
#
# details will be set once the version of the counter has been read from the device
GMC_DeviceName          = None                # to be detected in init; generic name like: "GMC Device"
GMC_DeviceDetected      = "Undefined"         # will be replaced after connection with full specific name as detected,
                                              # like 'GMC-300Re 4.20'. Had been 14 chars fixed, can now be any length
GMC_Model               = "Undefined"         # derived from GMC_DeviceDetected in getGMC_DeviceProperties()
GMC_FWVersion           = 0                   # derived from GMC_DeviceDetected in getGMC_DeviceProperties()
GMC_Variables           = "auto"              # which variables are supported
GMC_HasGyroCommand      = "auto"              # does NOT support GETGYRO command
GMC_ClockIsDead         = False               # when True the History time will NOT be parsed (clock defect on my GMC-500+ counter)
                                              # is set True only on Command Line with command 'clockisdead'
GMC_DatetimeMsg         = ""                  # the message returned for datetime
GMC_getInfoFlag         = 0                   # flag to signal to get the GMC_info even when logging; 0: no flag, 1:extended=False, 2:extenden=True
GMC_CountCalibPoints    = "auto"              # Number of Calib.Points, 3 or 6
GMC_savedatatypes       = "auto"              # Saving every sec, min, h, - thresholds eliminate  in GMC-300s, GMC-800
GMC_cfg                 = bytes(256)          # Configuration bytes of the counter. 256 bytes in 300 series, 512 bytes in 500, 600 series


# GMC Bugs and Settings
GMC_memory              = "auto"              # Can be configured for 64kB or 1 MB in the config file
GMC_SPIRpage            = "auto"              # size of page to read the history from device
GMC_SPIRbugfix          = "auto"              # if True then reading SPIR gives one byte more than requested  (True for GMC-300 series)
GMC_locationBug         = "auto"              # --> ["GMC-500+Re 1.18","GMC-500+Re 1.21"], see the FIRMWARE BUGS topic in the configuration file
GMC_endianness          = "auto"              # big- vs- little-endian for calibration value storage
GMC_configsize          = "auto"              # 256 bytes in 300 series, 512 bytes in 500/600 series
GMC_voltagebytes        = "auto"              # 1 byte in the 300 series, 5 bytes in the 500/600 series
GMC_Bytes               = "auto"              # the number of bytes ( 2 or 4) from the CPM and CPS calls, as well as the calls to 1st and 2nd tube
GMC_CfgHiIndex          = "auto"              # the index column in cfgKeyHi applicable for the current device
GMC_WiFiCapable         = "auto"              # does counter have WiFi?
GMC_WiFiIsON            = "auto"              # is WiFi switched ON at the counter (if the counter is wifi enabled)
GMC_WiFiPeriod          = "auto"              # min between WiFi uploads to gmcmap.com; default is 2 (min)
GMC_WiFiSwitch          = "auto"              # set the WiFi switch to ON | OFF
GMC_DualTube            = "auto"              # all are single tube, except 500, 500+, which ares double tube
GMC_FETenabled          = "auto"              # only 500 and 600 series seems enabled
GMC_FastEstTime         = "auto"              # if != 60 then false data will result (GMC: 3=dynamic, 5, 10, 15, 20, 30, 60=sec; firmware >= 2.28)
GMC_DeadTimeEnabled     = "auto"              # Dead time "Feature" in firmware 2.41 and later
GMC_TargetHVEnabled     = "auto"              # allows setting and reading of HV in firmware 2.41 and later
GMC_RTC_Offset          = "auto"              # the seconds to add to the clock every hour; value is from -59 to +59 seconds
GMC_HasRTC_Offset       = "auto"              # False or True to have RTC_OFFSET
GMC_savedatatype        = "Unknown - will become known once the device is connected"
GMC_savedataindex       = 1                   # index to save every second, ... minute, etc (1 == every second)
GMC_calls               = 0                   # total number of calls to any CP* variable at GMC
GMC_callsTimeoutCPM     = 0                   # total number of calls to any CPM* variable at GMC which went into timeout
GMC_callsTimeoutCPS     = 0                   # total number of calls to any CPS* variable at GMC which went into timeout
GMC_callsException      = 0                   # total number of calls to any CP* variable at GMC which went into Exception
GMC_callsWrongbyteCount = 0                   # total number of calls to any CP* variable at GMC which had WRONG bytecount
GMC_simul               = False               # when True a GMC counters is simulated; requires Simul_GMCcounter.py being run
GMC_NextCorrMin         = -1                  # the next minute value for setting the counter clock (0 ... 59)
GMC_GL_ClockCorrection  = "auto"              # the interval in minutes for setting the counter clock by GEIGERLOG

GMC_ThreadRun           = False               # flag to signal to keep running the thread
GMC_Thread              = None                # der GMC thread zum CP* calling
GMC_ThreadMessages      = ""                  # messages created during getting values for variables. Only the last one remains
GMC_Value               = {}                  # to keep the local vars
GMC_testing             = False               # set to True to activate certain testing in GMC code
GMC_callsExtrabyte      = 0                   # total number of calls to any CP* variable at GMC which had extrabyte in the pipeline


#
# AudioCounter device
#
AudioDevice             = None                # audiocard; to be set in init to (None, None) (could be USB, 9 and other)
AudioLatency            = "auto"              # to be set in init to (1.0, 1.0) sec latency
AudioPulseMax           = None                # +/- 32768 as maximum pulse height for 16bit signal
AudioPulseDir           = None                # False for negative; True for positive pulse
AudioThreshold          = None                # Percentage of pulse height to trigger a count
                                              # 60% of +/- 32768 => approx 20000
AudioRate               = None                # becomes 44100:  sampling rate audio; works for most sound cards
AudioChunk              = None                # becomes 32:     samples per read
AudioChannels           = None                # becomes (1,1):  1= Mono, 2=Stereo
AudioFormat             = None                # becomes (int16, int16): signed 16 bit resolution

AudioLastCpm            = 0                   # audio clicks CPM
AudioLastCps            = 0                   # audio clicks CPS
AudioLast60CPS          = None                # np array storing last 60 sec of CPS values
AudioThreadStop         = False               # True to stop the audio thread
AudioMultiPulses        = None                # stores the concatenated audio data for plotting
AudioRecording          = None                # stores the Recording
AudioPlotData           = None                # stores the data to be plotted
AudioOei                = None                # the eia storage label
AudioVariables          = "auto"              # default is CPM3rd, CPS3rd


#
# IoT device
#
IoTBrokerIP             = "auto"              # MQTT server IP, to which RadMon sends the data
IoTBrokerPort           = "auto"              # Port of the MQTT server, defaults to 1883
IoTTimeout              = 5                   # waiting for "successful connection" confirmation
IoTUsername             = "auto"              # the IoT broker username when using authorization
IoTPassword             = "auto"              # the IoT broker password when using authorization
IoTBrokerFolder         = "auto"              # The MQTT folder as defined in the RadMon+ device

IoTClientDataGL         = None                # config for GeigerLog device

IoTClientTasmotaGL1     = None                # Config for Tasmot Plug #1
IoTClientTasmotaGL2     = None                # Config for Tasmot Plug #2
IoTClientTasmotaGL3     = None                # Config for Tasmot Plug #3
IoTClientTasmotaGL4     = None                # Config for Tasmot Plug #4

IoTVariables            = "auto"              # a list of the variables to log, like: CPM3rd, Temp, Press, Humid,
IoTCycleTime            = 1                   # cycle time of the RadMon device
IoTconnectionState      = False
IoTconnectDuration      = ""

iot_client              = None                # to be set in gdev_radmon.initRadMon
iot_cpm                 = None                # temporary storage for CPM
iot_cps                 = None                # temporary storage for CPS
iot_temp                = None                # temporary storage for Temperature
iot_press               = None                # temporary storage for Pressure
iot_hum                 = None                # temporary storage for Humidity
iot_rssi                = None                # temporary storage for RSSI
iot_data                = None                # becomes {} with up to 12 vnames
iot_dataready           = False
### testing
iot_threadstart         = 0                   # to get duration of MQTT handshake
###



#
# RadMon device
#
RMServerIP              = "auto"              # MQTT server IP, to which RadMon sends the data
RMServerPort            = "auto"              # Port of the MQTT server, defaults to 1883
RMServerFolder          = "auto"              # The MQTT folder as defined in the RadMon+ device
RMVariables             = "auto"              # a list of the variables to log, like: CPM3rd, Temp, Press, Humid,
RMTimeout               = 5                   # waiting for "successful connection" confirmation
RMCycleTime             = 1                   # cycle time of the RadMon device
RMconnect               = (-99, "")           # flag to signal connection
RMdisconnect            = (-99, "")           # flag to signal dis-connection

rm_client               = None                # to be set in gdev_radmon.initRadMon
rm_cpm                  = None                # temporary storage for CPM
rm_temp                 = None                # temporary storage for Temperature
rm_press                = None                # temporary storage for Pressure
rm_hum                  = None                # temporary storage for Humidity
rm_rssi                 = None                # temporary storage for RSSI



#
# AmbioMon device
#
AmbioServerIP           = "auto"              # server Domain name or IP to which AmbioMon connects
AmbioDataType           = "auto"              # "LAST" or "AVG" for lastdata or lastavg
AmbioTimeout            = "auto"              # waiting for successful connection
AmbioVariables          = "auto"              # a list of the variables to log
AmbioValues             = {}                  # values received in a thread
AmbioThreadRun          = False               # flag to stop/run the thread
AmbioThread             = None                # to hold the AmbioMon thread
AmbioCPMpointer         = 2                   # pointer to the variable: CPM=2, CPM1st=4, CPM2nd=6, CPM3rd=nicht erlaubt!
AmbioCPSpointer         = 3                   # pointer to the variable: CPS=3, CPS1st=5, CPM2nd=7, CPS3rd=nicht erlaubt!
AmbioDataPage           = "empty"             # the return for reading lastData or lastAvg
AmbioCalibPage          = "empty"             # the return for reading calib
AmbioDevIDPage          = "empty"             # the return for reading devid

# settings for the remote AmbioMon device
AmbioCPUFrequency       = 0                   # read-only for the ESP32 CPU frequency
AmbioSelector           = 3                   # selector position from: 1,2,3 for A,B,C = Alpha, Beta, Gamma
AmbioVoltage            = 444.44              # voltage of the GM tube in the AmbioMon
AmbioFrequency          = 1500                # frequency of driving HV generator
AmbioPwm                = 0.5                 # Pulse Width Modulation of HV generator



#
# Gamma-Scout device
#
GS_DeviceDetected       = None                # to be set in GS init as: Old, Classic, Online
GSFirmware              = None                # to be set in GS init
GSSerialNumber          = None                # to be set in GS init
GSDateTime              = None                # to be set when setting DateTime
GSusedMemory            = 0                   # to be set when calling History
GSMemoryTotal           = 65280               # max memory acc to manual, page 16, but when mem was 64450 (830 bytes free), interval was already 7d!
GSCalibData             = None                # the Gamma-Scout internal calibration data
GScurrentMode           = None                # "Normal", "PC", "Online"
GSVariables             = "auto"
GS_simul                = False               # when True GS counters are simulated



#
# LabJack device
#
LabJackActivation       = False                # Not available if False
LJimportLJP             = False                # LabJackPython module was imported
LJimportU3              = False                # LabJack' U3 module was imported
LJversionLJP            = "not in use"         # version of LabJackPython
LJversionU3             = "not in use"         # version of U3
LJVariables             = "auto"               # a list of the variables to log; auto=Temp, Humid, Xtra

# EI1050 probe for Labjack
LJEI1050Activation      = False                # Not available if False
LJEI1050version         = "not in use"         # version of EI1050
LJimportEI1050          = False                # LabJack' EI1050 module was imported
LJEI1050status          = None                 # Status of probe EI1050



#
# MiniMon device
#
MiniMonActivation       = False                # Not available if False
MiniMonOS_Device        = "auto"               # OS device, like /dev/hidraw3
MiniMonInterval         = "auto"               # interval between forced savings
MiniMonVariables        = "auto"               # default is Temp, Xtra



#
# Formula device
#
FormulaActivation         = False              # Not available if False
FormulaVariables          = "auto"             # default is CPM3rd, CPS3rd



#
# Manu device
#
ManuActivation            = False              # Not available if False
ManuVariables             = "auto"             # default is "Temp, Press, Humid, Xtra"
ManuValue                 = {}                 # up to 12 manually entered values for variables



#
# WiFiServer device
#
WiFiServerActivation      = False              # Not available if False
WiFiServerList            = []                 # a max of 12 WiFiServers possible
WiFiServerTimeout         = "auto"             # waiting time for successful connection
WiFiServerVariables       = "auto"             # a list of the variables to log



#
# WiFiClient device
#
WiFiClientActivation        = False            # Not available if False
WiFiClientPort              = "auto"           # server port on which GL listens
WiFiClientType              = "Generic"        # options are "Generic" or "GMC"
WiFiClientVariables         = "auto"           # a list of the variables to log
WiFiClientVariablesGENERIC  = "auto"           # a list of the variables to log for a GENERIC device
WiFiClientVariablesGMC      = "auto"           # a list of the variables to log for a GMC device
WiFiClientVariablesMap      = {}               # a dict of the variables with mapping to the GMC device
WiFiClientMapping           = {}               # a str giving the mapping of counter vars to GeigerLog vars

WiFiClientServer            = None             # handle for the http webserver
WiFiClientThread            = None             # the thread
WiFiClientValues            = None             # the values read by WiFiClient



#
# I2C device - the Dongle
#
I2C_IOWDriverLoaded         = False                # Is the driver loaded? relevant only for IOW dongle
I2CDeviceDetected           = "Undefined"          # name like ELV..., IOW..., ISS...
I2CDongle                   = None                 # becomes instance of the I2C Dongle
I2CDongleCode               = None                 # becomes name of the I2C Dongle, like ISS, ELV, IOW
I2CVariables                = None                 # is set with the config of the sensors
I2CInfo                     = None                 # Info, to be set in init
I2CInfoExt                  = None                 # Info Extended, to be set in init
Sensors                     = None                 # is set by gedev_i2c

# I2C Sensors - connected via the Dongle
I2CSensor                   = {}                   # collector for sensors
I2CSensor["LM75"]           = [False, 0x48, None]  # Sensor LM75   (T)              at addr 0x48
I2CSensor["BME280"]         = [False, 0x76, None]  # Sensor BME280 (T, P, H)        at addr 0x76
I2CSensor["SCD30"]          = [False, 0x61, None]  # Sensor SCD30  (CO2 by NDIR)    at addr 0x61
I2CSensor["SCD41"]          = [False, 0x62, None]  # Sensor SCD41  (CO2 by Photoacoustic) at addr 0x62
I2CSensor["TSL2591"]        = [False, 0x29, None]  # Sensor TSL2591(Light vis + IR) at addr 0x29
I2CSensor["BH1750"]         = [False, 0x23, None]  # Sensor BH1750  (Light vis)      at addr 0x23
I2CSensor["GDK101"]         = [False, 0x18, None]  # Sensor GDK102 (CPM)            at addr 0x18



#
# Raspi Computer
#
isRaspi                     = False            # is a Raspi or not
RaspiVersion                = 0                # version no 1, 2, 3, 4, 5, ... Not a Raspi if 0
RaspiModel                  = "Not a Raspi"    # for Raspi 5: 'Raspberry Pi 5 Model B Rev 1.0'
RaspiGPIO_Info              = "Not a Raspi"    # GPIO.RPI_INFO = {'P1_REVISION': 3, 'REVISION': 'c04170', 'TYPE': 'Pi 5 Model B', 'MANUFACTURER': 'Sony UK', 'PROCESSOR': 'BCM2712', 'RAM': '4GB'}
RaspiGPIO_Version           = "Not a Raspi"    # GPIO.VERSION  = 0.7.2 (for rpi-lgpio=0.4)
RaspiSmbus_Version          = "Not a Raspi"    # smbus.__version__ e.g. 'smbus2 0.4.3'


#
# RaspiI2C device
#
RaspiI2CActivation          = False            # Not available if False
RaspiI2CSmbusHandle         = None             # handle for smbus(smbus2) on Raspi
RaspiI2Cvarlist             = None             # a list of the variables to log
RaspiI2CVariables           = "auto"           # a string listing the variables to log
RaspiI2CCumDur              = .1               # the longest duration of getting values from all I2C devices
RaspiI2CBMM150_device       = None             # handle for BMM150 Python module

# RaspiI2C Sensors - connectable to the Raspi
# LM75      : Temp
# BME280    : Temp, Press, Humid
# BH1750    : Light: vis
# TSL2591   : Light: vis + IR
# SCD30     : CO2 by NDIR,          Temperature, Humidity
# SCD41     : CO2 by Photoacoustic, Temperature, Humidity
# GDK101    : CPM, CPM_10min_avg, CycleTime           # ATTENTION: it does need a 5V supply, though signals are 3.3V
# VEML6075  : UV-A and UV-B, UV-A-corr, UV-B-corr, uvd: dark current, uvcomp1, uvcomp1)) # see rdataserver
# BMM150    : Magnetic Field X, Y, Z, Mafnitude (X,Y,Z), Heading

RaspiI2CSensor              = {
    # Sensor-     Def.I2C  Activation Connection Class   Var-   Vars                                        Burn-in Averaging Data
    # Name        Address  Status     Status     handle  count  list                                        cycles  cycles    Function
    # key         0        1          2          3       4      5                                           6       7         8
    "LM75"    : [ 0x48,    False,     False,     None,   1,     ["Temp",                                    ], 2,   9,        "T"                ],
    "BME280"  : [ 0x76,    False,     False,     None,   3,     ["Temp",   "Press",  "Humid"                ], 2,   3,        "T,P,H"            ],
    "BH1750"  : [ 0x23,    False,     False,     None,   1,     ["CPM3rd"                                   ], 2,   2,        "VIS"              ],
    "TSL2591" : [ 0x29,    False,     False,     None,   2,     ["CPM3rd", "CPS3rd"                         ], 2,   1,        "VIS,IR"           ],
    "SCD30"   : [ 0x61,    False,     False,     None,   3,     ["CPM2nd", "CPM3rd", "CPS3rd"               ], 2,   1,        "CO2,T,H"          ],
    "SCD41"   : [ 0x62,    False,     False,     None,   3,     ["CPM",    "CPM1st", "CPS1st"               ], 2,   1,        "CO2,T,H"          ],
    "GDK101"  : [ 0x18,    False,     False,     None,   3,     ["CPM",    "CPS",    "Temp"                 ], 2,   1,        "CPM,CPM,CTime"    ],
    "BMM150"  : [ 0x13,    False,     False,     None,   5,     ["Temp",   "Press",  "Humid", "Xtra", "CPM" ], 2,   3,        "MAG(X,Y,Z),M,H"   ],
    }
RaspiI2CDataStore          = {}



#
# RaspiPulse device
#
RaspiPulseActivation        = False            # Not available if False
RaspiPulseMode              = "auto"           # numbering mode: BCM or board
RaspiPulsePin               = "auto"           # hardware pin for interrupt in BCM numbering
RaspiPulseEdge              = "auto"           # options are "GPIO.RISING" or "GPIO.FALLING"
RaspiPulsePullUpDown        = "auto"           # options are "GPIO.PUD_DOWN" or "GPIO.PUD_UP"
RaspiPulseVariables         = "auto"           # a list of the variables to log

RaspiPulseCPS               = 0                # the cumulative 1 sec counts as CPS
RaspiPulseLast60CPS         = NAN              # becomes deque with len=60, space for 60 sec CPS data

RaspiPulseLastCPS           = NAN              # the last CPS value
RaspiPulseLastCPM           = NAN              # the last CPM value

# Raspi PWM settings
# a command 'pwm' on command line at start makes RaspiPulsePWM_Active =>True
RaspiPulsePWM_Active        = False            # to use PWM or not
RaspiPulsePWM_Handle        = None             # the handle for setting PWM:   'GPIO.PWM(g.RaspiPulsePWM_Pin, g.RaspiPulsePWM_Freq)'
RaspiPulsePWM_Pin           = 13               # the GPIO pin in BCM mode used for generating PWM signal
RaspiPulsePWM_Freq          = 10               # the PWM frequency; can be set via command line with '--pwmfreq=30'
RaspiPulsePWM_Period        = 1 / 10           # sec - 100 ms the PWM period; calculated from frequency
RaspiPulsePWM_PulseLength   = 150 * 1E-6       # sec - 150 µs the PWM pulse length
RaspiPulsePWM_DutyCycle     = 99.8500          # %  - duty cycle calculated from period and pulse length



#
# SerialPulse device
#
SerialPulseVariables        = "auto"           # default is CPM3rd, CPS3rd
SerialPulseUsbport          = "auto"           # to be defined in gdev_serialpulse.py
SerialPulseBaudrate         = "auto"           # to be defined in gdev_serialpulse.py
SerialPulseLastCPS          = None             # the last CPS value
SerialPulseLast60CPS        = None             # stores the last 60 CPS to allow creation of CPM
SerialPulseThreadRun        = False            # flag to signal to keep the thread running
SerialPulseThread           = None             # handle of the Pulse Thread
SerialPulseSerialConn       = None             # handle of the Pulse Serial connection

#
# RadPro device
#
RadProDevice                = None
RadProVariables             = "auto"           # default is CPM3rd, CPS3rd
RadProPort                  = "auto"           # to be defined in gdev_radpro.py
RadProBaud                  = 115200           #
RadProTimeoutR              = 0.5              # serial timeout for Read
RadProTimeoutW              = 0.5              # serial timeout for Write
RadProTimeoutRHist          = 4.0              # serial timeout for Read when reading Hist

RadProLast60CPS             = None             # stores the last 60 CPS to allow creation of CPM
RadProLast60CPSclean        = None             # the last 60 CPS when ignoring any non-poissonians
RadProValues                = {}               # gets the RadPro values in Thread cycle
RadProThreadRun             = False            # Flag to signal running thread
RadProThread                = None             # handle of the RadPro Thread

RadProHardwareId            = None
RadProSoftwareId            = None
RadProDeviceId              = None

RadProLastCPSTime           = NAN
RadProLastCPSPulseCount     = NAN

RadProSyncTime              = "auto"           # can be yes or no - to be defined in gdev_radpro.py
RadProClockCorrection       = "auto"           # to automatically set the clock of the RadPro Device
#GMC_NextCorrMin         = -1                  # the next minute value for setting the counter clock (0 ... 59)
RadProNextCorrMin           = -1               # the next minute value for setting the counter clock (0 ... 59)
RadProClockDrift            = 0                # difference ComputerTime minus DeviceTime
RadProClockDriftFrom        = 0                # DateTime when RadProClockDrift had been measured
RadProClockDriftMsg         = ""               # Msg of faster, slower, ...
RadProSerialBlocking        = False            # Blocks serial when in use

RadProFrequency             = 1250             # in Hz - PWM Frequency of the HV Generator
RadProDutyCycle             = 30.0             # in %  - PWM Duty cycle of the HV Generator

RadProDuties                = []               # list of duties to check, like: [1, 10, 20, 30, 40, 50, 60, 70, 80, 90]
RadProDindex                = 0                # index to duties
RadProPWM                   = False            # use only for evaluation of RadProPWM; set by 'radpropwm' on command line

# used in Radpro analysis
Bluetoothdur                = NAN
RadProGATT                  = NAN
BluepillDur                 = NAN              # duration of calling Bluepill for data in ms

# Voltmeter
DMMvoltage                  = NAN              # Voltage read from the DMM
DMMduration                 = NAN              # duration between 2 notifications
peripheral                  = None             # the Bluetooth address of the DMM
lasttime                    = None             # the lst time a DMM nitifcation hab been received

#
#ESP32
#
ESP32Serial                 = None             # for the ESP32


#
# Supported DEVICES and Attribs
#
#   Detected Names      : more specific names, like 'GMC-500+Re 1.22'
#   Varnames            : a Python list of varnames set for this device, like:
#                            ['CPM', 'CPS', 'Temp', 'Press', 'Humid', 'Xtra']
#   Activation Status   : True if set to active in config file
#   Connection Status   : True if connected
Devices = {
           # Device-        Detected-    Var-        Activation-  Connection-
           # Name           Names        Names       Status       Status
           #                0            1           2            3
           #                DNAME        VNAMES      ACTIV        CONN
            "GMC"        : [None,        None,       False,       False],    # 1
            "Audio"      : [None,        None,       False,       False],    # 2
            "IoT"        : [None,        None,       False,       False],    # 3
            "RadMon"     : [None,        None,       False,       False],    # 4
            "AmbioMon"   : [None,        None,       False,       False],    # 5
            "GammaScout" : [None,        None,       False,       False],    # 6
            "LabJack"    : [None,        None,       False,       False],    # 8
            "MiniMon"    : [None,        None,       False,       False],    # 9
            "Formula"    : [None,        None,       False,       False],    # 10
            "WiFiClient" : [None,        None,       False,       False],    # 11
            "WiFiServer" : [None,        None,       False,       False],    # 12
            "I2C"        : [None,        None,       False,       False],    # 7
            "RaspiI2C"   : [None,        None,       False,       False],    # 13
            "RaspiPulse" : [None,        None,       False,       False],    # 14
            "SerialPulse": [None,        None,       False,       False],    # 15
            "RadPro"     : [None,        None,       False,       False],    # 17
            "Manu"       : [None,        None,       False,       False],    # 16 - keep at last position to allow overwriting of other entries
          }

# columns Naming
DNAME  = 0    # Detected Name
VNAMES = 1    # Variable names as Python list
ACTIV  = 2    # Activation status
CONN   = 3    # Connection status

# count of DEVICES
DevicesActivated     = 0                   # count of activated devices; determined upon connecting
DevicesConnected     = 0                   # count of connected devices; determined upon connecting

#
# VARIABLES - names and style
#
# colors at:  https://matplotlib.org/users/colors.html
# linestyles: "solid", "dotted"
# NOTE: Medium Names became necessary for the database when the (Short) names for T, P, H, X were changed to Temp, etc
# do not modify this - use copy VarsCopy !!!!

VarsDefault  = {
           #                                             Units
           # Names,      Names,           Names          T: °C can be °F      Color            Line        Names
           # Short       Long             Very short     CP* can be µSv/h     Style            Style       Medium         Comment
           # key         0                1              2                    3                4           5              6
            "CPM"    : ["CPM",           "M",           "CPM",               "blue",          "solid",     "CPM"    ,     "CPM"    ],    # 1
            "CPS"    : ["CPS",           "S",           "CPS",               "magenta",       "solid",     "CPS"    ,     "CPS"    ],    # 2
            "CPM1st" : ["CPM1st",        "M1",          "CPM",               "deepskyblue",   "solid",     "CPM1st" ,     "CPM1st" ],    # 3
            "CPS1st" : ["CPS1st",        "S1",          "CPS",               "violet",        "solid",     "CPS1st" ,     "CPS1st" ],    # 4
            "CPM2nd" : ["CPM2nd",        "M2",          "CPM",               "cyan",          "solid",     "CPM2nd" ,     "CPM2nd" ],    # 5
            "CPS2nd" : ["CPS2nd",        "S2",          "CPS",               "#9b59b6",       "solid",     "CPS2nd" ,     "CPS2nd" ],    # 6 color: dark violet
            "CPM3rd" : ["CPM3rd",        "M3",          "CPM",               "brown",         "solid",     "CPM3rd" ,     "CPM3rd" ],    # 7
            "CPS3rd" : ["CPS3rd",        "S3",          "CPS",               "orange",        "solid",     "CPS3rd" ,     "CPS3rd" ],    # 8
            "Temp"   : ["Temperature",   "T",           "°C",                "red",           "solid",     "T"      ,     "Temp"   ],    # 9
            "Press"  : ["Pressure",      "P",           "hPa",               "black",         "solid",     "P"      ,     "Press"  ],    # 10
            "Humid"  : ["Humidity",      "H",           "%",                 "green",         "solid",     "H"      ,     "Humid"  ],    # 11
            "Xtra"   : ["Xtra",          "X",           "x",                 "#00ff00",       "solid",     "X"      ,     "Xtra"   ],    # 12 color: full green
          }

# Index,       DateTime,     CPM,     CPS,  CPM1st,  CPS1st,  CPM2nd,  CPS2nd,  CPM3rd,  CPS3rd,  Temp,   Press,   Humid,   Xtra
# Column No    0             1        2     3        4        5        6        7        8        9       10       11       12
datacolsDefault          = 1 + len(VarsDefault) # total of 13: DateTime plus 12 vars (index excluded; is not data),
VarsCopy                 = VarsDefault.copy()   # need a copy to allow reset as colorpicker may change color
VarsIndex                = {"DateTime":0, "CPM":1, "CPS":2, "CPM1st":3, "CPS1st":4, "CPM2nd":5, "CPS2nd":6, "CPM3rd":7, "CPS3rd":8,
                            "Temp":9, "Press":10, "Humid":11, "Xtra":12}
VarsUppercaseIndex       = {}
for key in VarsIndex: VarsUppercaseIndex[key.upper()] = VarsIndex[key]
# result: VarsUppercaseIndex = {'DATETIME': 0, 'CPM': 1, 'CPS': 2, 'CPM1ST': 3, 'CPS1ST': 4, 'CPM2ND': 5, 'CPS2ND': 6, 'CPM3RD': 7, 'CPS3RD': 8, 'TEMP': 9, 'PRESS': 10, 'HUMID': 11, 'XTRA': 12}

# for the LogPad
logHeaderTitle           = ["M ", "S ", "M1", "S1", "M2", "S2", "M3", "S3", "T ", "P ", "H ", "X "]     # all items are len=2

varAllFalse              = {}
varAllEmpty              = {}
varAllZero               = {}
lastLogValues            = {}                  # last log values received from devices
for vname in VarsCopy:
    varAllFalse  [vname] = False               # set all False
    varAllEmpty  [vname] = ""                  # set all empty
    varAllZero   [vname] = 0                   # set all to zero
    lastLogValues[vname] = NAN                 # set all values to NAN

devAllNone               = {}
for devname in Devices:
    devAllNone[devname]  = None                # set all None

# HOUSEKEEPING for VARIABLES
varsSetForCurrent        = varAllFalse.copy()  # variable is active in the current data set
varsSetForLogNew         = varAllFalse.copy()  # variable is active for current devices
varsSetForLog            = varAllFalse.copy()  # variable is active in the current Log
varsSetForHis            = varAllFalse.copy()  # variable is active in the current His

varChecked4PlotLog       = varAllFalse.copy()  # is variable checked for showing in plot for Log
varChecked4PlotHis       = varAllFalse.copy()  # is variable checked for showing in plot for History

varMapCount              = varAllZero .copy()  # holds counts of mapping of the variables
varStats                 = varAllEmpty.copy()  # info on avg, StdDev etc; will be set in gsup_plot, used for SuSt and tip for vars

DevVarsAsText            = devAllNone .copy()  # determined in switchAllDeviceConnections, Devices with associated variables

varMapCountTotal         = 0                   # determined in switchAllDeviceConnections; at least 1 needed for logging


# SCALING
# reset all vars to "no scaling"
#
# Value - Scaling - this modifies the measured variable; any modification will be stored to Database
ValueScale            = {}
for vname in VarsCopy:  ValueScale[vname]  = "VAL"
#
# Graph Sscaling - this does ONLY modify how the data is plotted; any modification will NOT be stored to Database
GraphScale            = {}
for vname in VarsCopy:  GraphScale[vname]  = "VAL"



###############################################################################
# Alarm
###############################################################################

AlarmActivation          = False
AlarmSound               = False
AlarmIdleCycles          = 30
AlarmMsg                 = ""
AlarmMsgAll              = ""
# AlarmUpdateInterval      = 3      # send alarm only when more than consecutive alarms occured in interval AlarmUpdateInterval (???)
AlarmCount               = 0      # number of consecutive alarms

AlarmLimits              = {}
for vname in VarsDefault:       AlarmLimits[vname]      = None

AlarmQueues              = {}
for vname in VarsDefault:       AlarmQueues[vname]      = None

LastAlarmQueues          = {}
for vname in VarsDefault:       LastAlarmQueues[vname]  = None



###############################################################################
# Email
###############################################################################

emailActivation             = False                 # set to true to enable email (done in gsub_config)
emailUsage                  = False                 # set to true to use email

emailReadFromFile           = ""                    # to be set with path to email config file
emailRequested                  = False                 # an alarm occured which could be sent to email

email                       = {}                    # Example fillings as in GL config
email["Protocol"]           = "SMTP_SSL"            # bad alternative: SMTP
email["Host"]               = "smtp.gmail.com"      # Google's mail server
email["Port"]               = 465                   # SMTP_SSL: 465 (secure)  SMTP: 587 (old)
email["From"]               = "johndoe@gmail.com"   # sender
email["To"]                 = "info@johndoe.com"    # recipient
email["Password"]           = "topsecret"           #



###############################################################################
# Telegram Messenger
###############################################################################

TelegramActivation       = False                # Telegram Activation
TelegramToken            = None                 # Telegram Token
TelegramUpdateCycle      = 3600                 # Telegram Update Cycle in seconds
TelegramLastUpdate       = 0                    # time of the last update of Telegram
TelegramBot              = None                 # pointer to instance of Telegram Bot
TelegramChatID           = None                 # Telegram Bot Chat ID
TelegramAlarm            = False                # sends an Alarm update to Telegram
TelegramUpdate           = False                # sends a cyclic update to Telegram
TelegramNeedsPic         = False                # True when a pic is needed to update Telegram
TelegramPicIsReady       = False                # True when a pic is available for sending to Telegram
TelegramPicBytes         = None                 # becomes io.BytesIO()
TelegramData             = [0, {}]              # holds (count of records, Last Log values)



###############################################################################
# HELP DETAILS
###############################################################################

helpOptions  = """
Usage:  on Linux, Mac:  ./GeigerLog.sh [Options] [Commands]
        on Windows:     GeigerLog.bat  [Options] [Commands]

Options:
    -h, --help          Show this help and exit.
    -d, --debug         Run with printing debug info.
                        Default is NOT printing debug info.
    -v, --verbose       Be more verbose.
                        Default is NOT printing verbose info.
    -w, --werbose       Be much more verbose.
                        Default is NOT printing werbose info.
    -l, --logfile       Defines the log file name to be used
                        with commands 'load' and 'start'.
    -s  --style name    Sets the style; see also GeigerLog manual
                        and Command: 'showstyles'. Default is set
                        by your system.
    -V, --Version       Show version status and exit.
    -L, --ListPorts     Show all USB-to-Serial ports and exit.
        --factoryreset  Reset GeigerLog to Factory conditions

Commands:
    showstyles          Show a list of styles available on your system
                        and exit. For usage details see manual.
    keepFF              GMC counters only: Keeps all hexadecimalFF (Decimal 255)
                        values as a real value and not as 'Empty' one. See
                        manual in chapter on parsing strategy.
    connect             After starting do "Connect Devices".
    load                After starting load the log file. If no log file is
                        defined by option '-l' use "default.logdb".
    start               After starting do "Connect Devices", then load log file,
                        then start logging.
                        If log file not defined by option '-l' use "default.logdb"
    quick               After starting do "Connect Devices", then do "Quick Log".

By default data files will be read-from / written-to the directory "data" as a
subdirectory to the program directory. This can be changed in the configuration
file 'geigerlog.cfg' located in the 'gconfig' directory.

To watch debug, verbose, werbose, and devel output, start the program from the
command line in a terminal. The output will print to the terminal.

For Debugging collect output with: Heigerlog -dvw devel trace
    on Linux, Mac:  ./GeigerLog.sh -dvw devel trace
    on Windows:     GeigerLog.bat  -dvw devel trace
"""


helpQuickstart  = """
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
<p>With a proper hardware setup all devices are auto-configurable by GeigerLog. On any problems
read chapter "Appendix B – Connecting Device and Com­puter using a Serial Connection" of the GeigerLog manual.

<h3>Start Logging</h3>
<p>This will create a database file to store newly acquired data from the devices.</p>
<ol>
<li>Only on GMC devices: Switch device power on<br>(menu: <b>Device -> GMC Series -> Switch Power ON</b>))</li>
<li>Load a log file<br>(menu: <b>Log -> Get Log File or Create New One</b>)<br>
In the Get Log File dialog enter a new filename and press Enter,
or select an existing file to <b>APPEND</b> new data to this file.</li>
<li>Start logging<br>(menu: <b>Log -> Start Logging</b>, or click the <b>Start Log</b> toolbar icon)</li>
</ol>

<h3>Get History</h3>
<p>(Only if the device has this option.) This will create a database file to store all data downloaded from the internal storage of a device.</p>
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


helpFirmwareBugs  = """
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


helpWorldMaps  = """
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
<li><a href='http://www.gmcmap.com' >gmcmap.com</a> - This is the one supported by GQ Electronics</li>
<li><a href='https://radmon.org'    >radmon.org</a> - Opened again after hacking episode</li>
<li><a href='https://safecast.org'  >safecast.org</a> - Accepting radiation as well as air quality data</li>
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


helpOccupationalRadiation  = """
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
<p>For convenience : <b>1 milliRem/hour = 10 microSievert/hour</b></p>
<br>

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
    <td >= equiv. to permanent exposure over year</td>
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
    <td >= equiv. to permanent exposure over life<br>(in 40 year work life)</td>
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

# use doubled curly brackets {} within CSS code
helpAbout  = """
<!doctype html>
<style>
    h3              {{ color: darkblue; margin:5px 0px 5px 0px; padding:0px;}}
    p, ol, ul, li   {{ margin:4px 0px 10px 0px; padding:0px; font-size:15px;}}
    td, th          {{ padding: 0px 30px 0px 0px;}}
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
and a sensor to moni&shy;tor CO2, with a connection by wire or wireless by WiFi.

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

<p><b>IoT (Internet of Things) Devices:</b>
<br>GeigerLog supports all hardware which can provide the GeigerLog variables
in a simple format. IoT-Server software for the Raspberry Pi is included.</p>

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

<p><b>Formula Devices:</b>
<br>Uses the formula interpreter to generate / collect data.</p>

<p><b>Manu Devices:</b>
<br>A Pseudo-Device which allows to enter values manually.</p>

<p><b>WiFiServer Devices:</b>
<br>GeigerLog acts as a client to request data from a device which is
acting as a server.</p>

<p><b>WiFiClient Devices:</b>
<br>GeigerLog acts as a server to which devices can connect and deliver data.</p>

<p><b>RaspiI2C Devices:</b>
<br>Only when GeigerLog is running on a Raspi: GeigerLog uses the Raspi I2C options to communicate wth
I2C devices connected to a Raspi.</p>

<p><b>RaspiPulse Devices:</b>
<br>Only when GeigerLog is running on a Raspi: GeigerLog counts pulses on a Raspi GPIO pin.</p>

<p style='text-align:center;'>-------------------------------------------------------------------</p>

<p>The most recent version of GeigerLog as well as an up-to-date
GeigerLog-Manual can be found at project GeigerLog at Sourceforge:
<a href="https://sourceforge.net/projects/geigerlog/">
https://sourceforge.net/projects/geigerlog/</a>.</p>

<p>References:</p>
<table>
<tr><td>&nbsp;&nbsp;Author:                         </td> <td>{}</td></tr>
<tr><td>&nbsp;&nbsp;Version GeigerLog:&nbsp;&nbsp;  </td> <td>{}</td></tr>
<tr><td>&nbsp;&nbsp;Copyright:                      </td> <td>{}</td></tr>
<tr><td>&nbsp;&nbsp;License:                        </td> <td>{}, see included
file 'COPYING' and <a href="http://www.gnu.org/licenses">http://www.gnu.org/licenses</a></td></tr>
</table>
<br>
"""
