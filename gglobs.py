#!/usr/bin/python
# -*- coding: UTF-8 -*-

"""
some super global variables; can be read and modified in all scripts
include with:     import gglobs
"""

# flags
debug               = False               # helpful for debugging, use via command line
verbose             = False               # more detailed printing, use via command line
devel               = False               # set some conditions for development
debugindent         = ""                  # to indent printing
redirect            = False               # on True redirects output from stdout and stderr to file plogPath

# dir & file
dataDirectory       = "data"              # the data subdirectory to the program directory
gresDirectory       = "gres"              # where the icons and sounds reside
progName            = None                # program name geigerlog (or geigerlog.py)
progPath            = None                # path to program geigerlog file
dataPath            = None                # path to data dir
gresPath            = None                # path to icons and sounds dir
proglogPath         = None                # path to program log file geigerlog.proglog
plogPath            = None                # path to program log file geigerlog.stdlog
configPath          = None                # path to configuration file geigerlog.cfg
logFilePath         = None                # file path of the log file
binFilePath         = None                # file path of the bin file
lstFilePath         = None                # file path of the lst file
hisFilePath         = None                # file path of the his file
currentFilePath     = None                # file path of the current log or his file; in plot

manual_filename     = "GeigerLog-Manual.pdf" # name of the included manual file

# GUI options
window_width        = 1366                # the standard screen of 1366 x 768 (16:9),
window_height       = 768                 #
window_size         = 'maximized'         # 'auto' or 'maximized'
ThemeSearchPath     = "/usr/share/icons"  # path to the theme names
                                          # in Ubuntu Mate 16.04 all found
                                          # in /usr/share/icons
ThemeName           = "mate"              # the (only!) theme to be used
                                          # must be a directory name under
                                          # the ThemeSearchPath
style               = "Breeze"            # may also be defined in config file

# Serial port
ser                 = None                # serial port pointer
baudrates           = [1200, 2400, 4800, 9600, 14400, 19200, 28800, 38400, 57600, 115200]
baudrate            = 57600               # will be overwritten by a setting in geigerlog.cfg file
#usbport             = '/dev/geiger'
usbport             = '/dev/ttyUSB0'      # will be overwritten by a setting in geigerlog.cfg file
timeout             = 5                   # will be overwritten by a setting in geigerlog.cfg file
ttyS                = "ignore"            # to ignore or include '/dev/ttySN', N=1,2,3,... ports on USB Autodiscovery

# Device Options
# GMC-300           found to work with firmware 3.20
# GMC-300E          does not seem to exist
# GMC-300E+         found to work with firmware 4.20, 4.22
# GMC-320           found to work with firmware ---unknown---
# GMC-320+          found to work with firmware ---unknown---
# GMC-500           found to work with firmware ---unknown---
# GMC-500+          found to work with firmware ---unknown---
# GMC-600           found to work with firmware ---unknown---
# GMC-600+          found to work with firmware ---unknown---

devices             = [ u"GMC-300" ,
                        u"GMC-300E+",      # default
                        u"GMC-320" ,
                        u"GMC-320+" ,
                        u"GMC-500" ,
                        u"GMC-500+",
                        u"GMC-600" ,
                        u"GMC-600+",
                      ]
devicesIndexDefault = 1                   # default is GMC-300E+
devicesIndex        = devicesIndexDefault
device              = devices[devicesIndex]
deviceDetected      = "None Detected"
cleanPipelineFlag   = False               # if True will attempt to read bytes from Serial Port
                                          # until no more bytes received (appears relevant obl for 500 series)
memoryMode          = "auto"              # auto  : memory defined by device chosen in this config file
                                          # fixed : memory defined in this config file
memory              = 2**16               # 64kB. Can be configured for 64kB or 1 MB in the config file
page                = 4096                # size of page to read the history from device
                                          # different page sizes are set in SPIR
                                          # command if required by different firmware!
calibrationMode     = 'auto'              # if auto then will use device specific calibration
                                          # if fixed will use value provided for all devices
calibration         = 0.0065              # factory default calibration factor in device is linear
                                          # i.e. the same for all 3 calibration points
                                          # CPM * calibration => µSv/h
cfg                 = None                # Configuration bytes of the counter. 256 bytes in 300series, 512 bytes in 500series
cfgOffsetPower      = 0                   # Offset in config for Power status (0=OFF, 255= ON)
cfgOffsetAlarm      = 1                   # Offset in config for AlarmOnOff (0=OFF, 1=ON)
cfgOffsetSpeaker    = 2                   # Offset in config for SpeakerOnOff (0=OFF, 1=ON)
cfgOffsetSDT        = 32                  # Offset in config to Save Data Type
cfgOffsetCalibration= 8                   # Offset in config for CPM / µSv/h calibration points
cfgOffsetMaxCPM     = 49                  # A MaxCPM during what period? of values in Memory??? HiByte@49, LoByte@50
powerstate          = None                # will be "ON" or "OFF" or "unknown"
savedatatypes       = (
                        "OFF (no history saving)",
                        "CPS, save every second",
                        "CPM, save every minute",
                        "CPM, save hourly average"
                      )
savedatatype        = "Unknown, run 'Device'->'Switch Saving Mode of Device' to get Mode info"

# Logging Options
cpm_counter         = 0                   # counts readings since last start logging; prints as index in log
logging             = False               # flag for logging
logcycle            = 3.0                 # time in seconds between CPM or CPS calls in logging
cpmflag             = True                # True if CPM, False if CPS
lastCPM             = None                # last CPM received from device

# History Options
keepFF              = False               # Flag in startup-options
                                          # Keeps all hexadecimal FF (Decimal 255) values as a
                                          # real value and not an 'Empty' one. See manual in chapter
                                          # on parsing strategy
fullhist            = False               # If False breaks history recording when 8k FF is read
                                          # if True reads the whole history from memory

# scratch pads
NotePad             = None                # pointer to print into notepad area

# Graphic Options
legendPos           = 0                   # legend placed into upper left corner of graph
Xleft               = None                # time min if entered
Xright              = None                # time max if entered
Xunit               = "Time"              # time unit; can be Time, auto, second, minute, hour, day
XunitCurrent        = Xunit               # current time unit
Xscale              = "auto"              # time scale; can be auto or fix
Ymin                = None                # CPM min if entered
Ymax                = None                # CPM max if entered
Yunit               = "CPM"               # CPM unit; can be CPM, CPS, µSv/h
Yscale              = "auto"              # CPM scale; can be auto or fix
mav_initial         = 60                  # length of Moving Average period in seconds
mav                 = mav_initial         # currently selected mav period
mavChecked          = False               # Plot the Moving Average line, and Legend with MovAvg length ins seconds and data points
avgChecked          = True                # Plot the lines Average, +/- 95% confidence, and Legend with average +/- StdDev value

# Plotstyle
linestyle           = 'solid'
linecolor           = 'blue'
linewidth           = '0.5'
markerstyle         = 'o'
markersize          = '2'


# Data arrays and values
logTime             = None                # array: Time data from total file
logCPM              = None                # array: CPM Data from total file
logTimeDiff         = None                # array: Time data as time diff to first record in days
logTimeFirst        = None                # value: Time of first record of total file

logTimeSlice        = None                # array: selected slice out of logTime
logTimeDiffSlice    = None                # array: selected slice out of logTimeDiff
logCPMSlice         = None                # array: selected slice out of logCPM

plotTime            = None                # array: either logTime or logTimeDiff depending on time unit;
                                          #        if Diff then in unit second, minute, hour, day
plotTimeSlice       = None                # array: selected slice out of plotTime
sizePlotSlice       = None                # value: size of plotTimeSlice

logFileData         = None                # 2dim numpy array with the log data
hisFileData         = None                # 2dim numpy array with the his data
currentFileData     = None                # 2dim numpy array with the currently plotted data

# Artificial Data                         # to be used for testing in FFT and Histogram
getArtificialData   = False               #
t                   = 0                   # the time sequence
sigt                = 0                   # the signal sequence


# Versions and infos
python_version      = "2.7.x"             # will be overwritten with auto-determined version in startup
__author__          = "ullix"
__copyright__       = "Copyright 2016"
__credits__         = [""]
__license__         = "GPL"
__version__         = "0.9.06.rc6"
