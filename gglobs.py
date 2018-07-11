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
__version__         = "0.9.07"            # version of next GeigerLog
#__version__         = "0.9.07.rc17"


# Versions
python_version      = "3.5.2"             # at time of development; will be
                                          # overwritten with auto-determined version in startup

# flags
debug               = False               # helpful for debugging, use via command line
verbose             = False               # more detailed printing, use via command line
devel               = False               # set some conditions for development CAREFUL !!!
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
timeout             = 3                   # will be overwritten by a setting in geigerlog.cfg file
ttyS                = "ignore"            # to 'ignore' or 'include' '/dev/ttySN', N=1,2,3,... ports on USB Autodiscovery

# Device Options
deviceDetected      = "auto"              # will be replaced after connection with full
                                          # name as detected, like 'GMC-300Re 4.20'
                                          # had been 14 chars, can now be longer
memory              = 2**16               # 64kB. Can be configured for 64kB or 1 MB in the config file
SPIRpage            = 4096                # size of page to read the history from device
calibration         = 0.0065              # factory default calibration factor in device is linear
                                          # i.e. the same for all 3 calibration points
                                          # CPM * calibration => µSv/h
endianness          = "little"            # big- vs- little-endian for calibration value storage
configsize          = 256                 # 256 bytes in 300series, 512 bytes in 500/600 series
voltagebytes        = 1                   # 1 byte in the 300 series, 5 bytes in the 500/600 series

cfg                 = None                # Configuration bytes of the counter. 256 bytes in 300series, 512 bytes in 500series
cfgOffsetPower      = 0                   # Offset in config for Power status (0=OFF, 255= ON)
cfgOffsetAlarm      = 1                   # Offset in config for AlarmOnOff (0=OFF, 1=ON)
cfgOffsetSpeaker    = 2                   # Offset in config for SpeakerOnOff (0=OFF, 1=ON)
cfgOffsetSDT        = 32                  # Offset in config to Save Data Type
cfgOffsetCalibration= 8                   # Offset in config for CPM / µSv/h calibration points
cfgOffsetMaxCPM     = 49                  # A MaxCPM during what period? of values in Memory??? HiByte@49, LoByte@50
savedatatypes       = (
                        "OFF (no history saving)",
                        "CPS, save every second",
                        "CPM, save every minute",
                        "CPM, save hourly average"
                      )
savedatatype        = "Unknown, run 'Device' -> 'Show Device Info' to get Mode info"

#special flags
test1               = False               # to run a specific test; see gcommands
test2               = False               # to run a specific test; see gcommands
test3               = False               # to run a specific test; see gcommands
test4               = False               # to run a specific test; see gcommands

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
avgChecked          = True                # Plot the lines Average, +/- 95% confidence, and Legend with average +/- StdDev value
mavChecked          = False               # Plot the Moving Average line, and Legend with MovAvg length ins seconds and data points
logChecked          = False               # Plot the Log of the Count Rate
cumChecked          = False               # Plot the Cumulative Average of the Count Rate
ccdChecked          = False               # Plot the Cumulative Count Rate


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

# Radiation World maps
GMCmapURL           = ""                  # to be set in configuration file
UserID              = ""                  # UserID on gmcmap.com
CounterID           = ""                  # CounterID on gmcmap.com




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
messages - will go into the redirect file.
"""

helpQuickstart = """
<style>h3 { color: darkblue; margin:5px 0px 5px 0px; padding:0px; } p, ol, ul { margin:4px 0px 4px 0px; padding:0px;} </style>
<H3>Mouse Help</H3><p>pointing your mouse cursor over an item of the window shows a status message
in the<br><b>Statusbar</b> (bottom of the window) providing info on the item!
<br><br>Assuming a USB cable is connecting computer and device:</p>
<h3>USB Port and Baudrate</h3>
<p>Start GeigerLog with command <span style="font-family:'Courier';">geigerlog</span>
 and in the Help menu select <b>USB Autodiscovery</b>. Take a note of the discovered <b>Port</b> and <b>Baudrate</b> settings. Click OK to use them for the current session.</p>

<p>Once you know the settings, use them with your device by starting GeigerLog with these options:<br>
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
<span style="font-family:'Courier';margin:30px;">geigerlog -p yourport -b yourbaudrate</span>
<br>On a Linux system e.g.:
&nbsp;&nbsp;&nbsp;&nbsp;<span style="font-family:'Courier';margin:30px;">geigerlog -p /dev/ttyUSB0 -b 57600</span>

<br>On a Windows system e.g.:
&nbsp;&nbsp;<span style="font-family:'Courier';margin:30px;">geigerlog -p COM3 -b 57600</span></p>

<p>If these settings will be your standard settings, you might want to modify the configuration file <b>geigerlog.cfg</b>
in section <b>Serial Port</b> accordingly, and start GeigerLog without options as <span style="font-family:'Courier';">geigerlog</span>.</p>

<h3>Start Logging</h3>
<ol>
<li>Connect the computer with the device<br>(menu: Device -> Connect Device, or click the 'Click for Connection' button)</li>
<li>Switch device on (menu: Device -> Switch Power ON)</li>
<li>Load a log file (menu: Logging -> Get Log File or Create New One)<br>
In the Get Log File dialog enter a new filename and press Enter,
<br>or select an existing file to <b>APPEND</b> new data to this file</li>
<li>Start logging (menu: Log -> Start Logging, or click the 'Start Log' toolbar icon)</li>
</ol>

<h3>Get History from Device</h3>
<ol>
<li>Connect the computer with the device<br>(menu: Device -> Connect Device, or click the 'Click for Connection' button)</li>
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
<p><span style='color:darkblue;'><b>GeigerLog</b></span> is a Python based program for use with GQ Electronic's
GMC-3xx, GMC-5xx, and GMC-6xx line of Geiger counters. It was developed on Linux Ubuntu Mate 16.04
but should also work on Windows, Mac and other, as long as a Python 3 with PyQt4 environment is available.
</p>

<p>The program allows reading of Geiger counter data, printing to screen and logging to \
file. Comments can be added to the log file during logging. The history stored on the Geiger \
counter can be extracted and converted into files that can be printed and analyzed.</p>

<p>From all data - Log data or History data - graphs can be created and shown as Count Rate History versus time.
 The Count Rate can be shown in units of CPM or CPS or µSv/h. The time can be shown as time-of-day, or
  time since first record in units of sec, min, hours, days, or auto-selected in auto mode.
  During logging the graph is live auto-updated. Both graph axes can be in either
  fixed scale or auto-scaled mode. The graphs can be stretched, shifted, and zoomed for details, and saved as pictures
in various formats (png, jpg, tif, svg, ...).</p>

<p>Time ranges can be set to analyze statistical properties of the data \
set within that range and be plotted within that range. The ranges can be entered manually or by
left and right mouse clicks for left (min) and right (max) range limits. All manipulations \
can be done during ongoing logging without disturbing it.</p>

<p>Some Geiger counter functions can be controlled from GeigerLog, and changes made without interrupting logging. All
communication with the device is checked for errors, which unfortunately do occur occasionally. The program
attempts to auto-recover from an error, and continues if successful, which it is in most cases.</p>

<p>The USB port used and its baudrate for the connection with the device can be auto-discovered.</p>

<p>Genuine recordings of Geiger counter data are included. One is from an international flight,
showing count rate increase with altitude, and reduction of cosmic rays when going from northern
latitudes towards the equator.</p>

<p>The most recent version of GeigerLog can be found at project GeigerLog at Sourceforge:
<a href="https://sourceforge.net/projects/geigerlog/">https://sourceforge.net/projects/geigerlog/</a>.
A <a href="https://sourceforge.net/projects/geigerlog/files/GeigerLog-Manual.pdf">GeigerLog-Manual(pdf)</a> is there as well.</p>

<p>References:
<br>&nbsp;&nbsp;Author.............: {}
<br>&nbsp;&nbsp;Version GeigerLog..: {}
<br>&nbsp;&nbsp;Credits............: <a href="https://sourceforge.net/projects/gqgmc/">Phil Gillaspy for extended documentation</a> of Geiger counter commands
<br>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
<a href="http://www.gqelectronicsllc.com/">GQ Electronics LLC</a> for documentation
<br>&nbsp;&nbsp;Copyright..........: {}
<br>&nbsp;&nbsp;License............: {} see included file 'COPYING' and <a href="http://www.gnu.org/licenses">http://www.gnu.org/licenses</a>
"""
