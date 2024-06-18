#! /usr/bin/env python3
# -*- coding: UTF-8 -*-

"""
gsup_utils.py - GeigerLog utilities with imports

include in programs with:
    from gsup_utils include *
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


# Function names:
# print(defname)
# print(__name__) # gibt modul name, like 'util'
# print(sys._getframe().f_code.co_name) # gibt korrekten Namen der Funktion

# get extensive output on crashes
# python3 -q -X faulthandler

# grep -inRsH "Text to be searched"  /path/to/dir (it can be '.')
#     i stands for ignore case distinctions
#     R stands for recursive and it also include symlinks. Better to use 'R' instead 'r'
#     n stands for "it will print line number".
#     s stands for "suppress error messages"
#     H stands for "it will print the file name for each match"


# install Python from source
# https://docs.rstudio.com/resources/install-python-source/
# ./configure \
#     --prefix=/opt/python/${PYTHON_VERSION} \
#     --enable-shared \
#     --enable-optimizations \
#     --enable-ipv6 \
#     LDFLAGS=-Wl,-rpath=/opt/python/${PYTHON_VERSION}/lib,--disable-new-dtags
#
# make
# sudo make altinstall
# remember:
# "The altinstall target will make sure the default Python on your machine is not touched,
#  or to avoid overwriting the system Python."


# "I wrote a Python script to automatically convert short-form PyQt5-style enums into
# fully qualified names. I thought it could be interesting to share:"
# https://stackoverflow.com/a/72658216/6178507

# getting keyboard presses
# works well under Linux X-Server; problems everywhere else
# Linux Wayland
# Windows unclear
# under mac must be run as root !!!!!
# # https://pynput.readthedocs.io/en/latest/limitations.html
#
# from pynput import keyboard
#
# def on_press(key):
#     if key == keyboard.Key.ctrl:
#         g.useGraphScaledData = True
#         rdprint(defname, "CTRL pressed")
#     # try:
#     #     print('alphanumeric key {0} pressed'.format(key.char))    # like a,B,C,1,5,9....
#     # except AttributeError:
#     #     print('special key {0} pressed'.format(key))              # like CRTL, SHIFT, ...
#
# def on_release(key):
#     if key == keyboard.Key.ctrl:
#         g.useGraphScaledData = False
#         rdprint(defname, "CTRL released")
#
# # in a non-blocking fashion:
# listener = keyboard.Listener(on_press=on_press, on_release=on_release)
# listener.start()



# colors for the terminal (do not put in gglobs, as this would require 'g.' prefix!)
# https://gist.github.com/vratiu/9780109
# https://stackoverflow.com/questions/5947742/how-to-change-the-output-color-of-echo-in-linux
# '90' values are supposed to be high intensity
TDEFAULT            = '\033[0m'             # default, i.e greyish
TRED                = '\033[91m'            # red
# TGREEN              = '\033[92m'            # light green
TGREEN              = '\033[92;1m'          # ist ja eigentlich 'bold green'
TYELLOW             = '\033[93m'            # yellow
TBLUE               = '\033[94m'            # blue (dark)
TMAGENTA            = '\033[95m'            # magenta
TCYAN               = '\033[96m'            # cyan
TWHITE              = '\033[97m'            # high intensity white

INVMAGENTA          = '\033[45m'            # invers magenta looks ok
INVBOLDMAGENTA      = '\033[45;1m'          # invers magenta with bold white

# BOLDxyz are brighter colors
BOLDRED             = '\033[91;1m'          # bold red
BOLDGREEN           = '\033[92;1m'          # bold green
BOLDYELLOW          = '\033[93;1m'          # bold yellow
BOLDBLUE            = '\033[94;1m'          # bold blue
BOLDMAGENTA         = '\033[95;1m'          # bold magenta
BOLDCYAN            = '\033[96;1m'          # bold cyan
BOLDWHITE           = '\033[97;1m'          # bold white

# UNDERLINE         = '\033[4m'             # underline
# BOLDREDUL         = '\033[31;1;4m'        # bold, red, underline, low intens?
# BOLDREDUL         = '\033[91;1;4m'        # bold, red, underline, high intens?
# BOLDRED           = '\033[31;1m'          # bold, red, (low intens?)

# if "WINDOWS" in platform.platform().upper():# no terminal colors on Windows uhmm - jetzt aber doch??
#     TDEFAULT        = ""                    # normal printout
#     TRED            = ""                    # (dark) red
#     TGREEN          = ""                    # hilite message
#     TYELLOW         = ""                    # error message
#     TBLUE           = ""                    #
#     TMAGENTA        = ""                    # devel message
#     TCYAN           = ""                    # devel message
#     TWHITE          = ""                    # unused

#     INVMAGENTA      = ""                    # devel message
#     INVBOLDMAGENTA  = ""                    # unused

#     BOLDRED         = ""                    # devel message
#     BOLDGREEN       = ""                    # devel message
#     BOLDYELLOW      = ""                    #
#     BOLDBLUE        = ""                    #
#     BOLDMAGENTA     = ""                    # unused
#     BOLDCYAN        = ""                    #
#     BOLDWHITE       = ""                    #


import gglobs as g                      # all global vars


#
# modules - available in std Python
#
import sys, os, io, time                # basic modules
import datetime as dt                   # datetime
import configparser                     # parse configuration file geigerlog.cfg
import copy                             # make shallow and deep copies
import getopt                           # parse command line for options and commands
import http.server                      # web server
import inspect                          # finding origin of f'on calls
import json                             # for SourceForge downloads, and IoT stuff, and settings
import platform                         # info on OS, machine, architecture, ...
import queue                            # queue for threading
import re                               # regex
import shutil                           # for copying files
import signal                           # handling signals like CTRL-C and other
import socket                           # finding IP Adress
import struct                           # packing numbers into chars (needed by gdev_gmc.py)
import ssl                              # for secure SSL server used in MonServer
import subprocess                       # to allow terminal commands tput rmam / tput smam
import threading                        # higher-level threading interfaces
import traceback                        # for traceback on error; used in: exceptPrint
import urllib.request                   # for web requests(AmbioMon, Radiation World Map, WiFiServer, ...)
import urllib.parse                     # for use with Radiation World Map
import urllib.error                     # needed extra?
import warnings                         # warning messages
import zipfile                          # creation of zip files
import sqlite3                          # needed by gsup_sql.py
import pathlib                          # needed in handling the virtual env
import gc                               # garbage collection
import webbrowser                       # used for loading manuals, e.g. in FireFox

# email related
import smtplib                          # email sending server
import quopri                           # Encode and decode MIME quoted-printable data
from email.message import EmailMessage  # sending emails

# queuing data
from collections   import deque         # used for queuing e.g. log data

# *.proglog, *.stdlog, *data/*, *misc, COPYING, backup*, *.notes

#
# modules - requiring installation via pip
#
try:
    import serial                       # make it a required installation, since serial.tools.list_ports is anyway
    import serial.tools.list_ports      # allows listing of serial ports and searching within; needed by *getSerialConfig, getPortList
    import numpy             as np      # scientific computing with Python
    import scipy                        # all of scipy
    import scipy.signal                 # a subpackage of scipy; needs separate import
    import scipy.stats                  # a subpackage of scipy; needs separate import
    import scipy.optimize               # needed for deadtime correction with paralysation
    # import playsound                  # playing *.wav and .mp3 sound files; can play only
                                        # --- kann auf Win 10 nicht installiert werden
                                        # --- kann auf Win 11 nicht installiert werden
                                        # --- 'pip install wheel' then 'pip install playsound' fixed the issue!
    import soundfile                    # playing *.wav sound files; can read and write

    import cpuinfo                      # cmd: cpuinfo.get_cpu_info()
    # import cpuid                        # to get CPU name and Vendor name
    import psutil                       # to get CPU, Memory and other system details
    import paho.mqtt.client  as mqtt    # for iot, RadMon, Raspi
    import ntplib                       # NTP Time server

    # PyQt - install via pip, but sometimes must use distribution package manager
    from PyQt5.QtWidgets                import *
    from PyQt5.QtGui                    import *
    from PyQt5.QtCore                   import *
    from PyQt5.QtPrintSupport           import *
    #from PyQt5.sip                     import *      # not needed for sip version; is present in any PyQt5.xyz

    # matplotlib importing and settings
    # next lines are better done in other code,
    # matplotlib.pyplot.figure(num=None, figsize=None, dpi=None, ...)
    # dpi ersetzen mit dpi of current screen, see gmain.py lines HiDPI et al.
    #
    #~matplotlib.rcParams['figure.figsize']     = [8.0, 6.0]
    #~matplotlib.rcParams['figure.dpi']         = 50
    #~matplotlib.rcParams['savefig.dpi']        = 100
    #~matplotlib.rcParams['font.size']          = 12
    #~matplotlib.rcParams['legend.fontsize']    = 'large'
    #~matplotlib.rcParams['figure.titlesize']   = 'medium'
    import matplotlib
    matplotlib.use('Qt5Agg', force=False)                                                               # use Qt5Agg, not the default TkAgg
    from   matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg    as FigureCanvas
    from   matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
    import matplotlib.pyplot                                              as plt                # MUST import AFTER 'matplotlib.use()'
    import matplotlib.dates                                               as mpld
    import matplotlib.animation                                           as mplanim            # it is used in gedev_audio!!!
    # import matplotlib.patches                                           as mpat               # currently unused (in: getMonGraph())

    # set epoch, see: https://matplotlib.org/stable/api/dates_api.html#matplotlib.dates.set_epoch
    # print("print(matplotlib.dates.get_epoch())")
    # print(matplotlib.dates.get_epoch())               # --> "1970-01-01T00:00" the default is set already
    # matplotlib.dates.set_epoch("1970-01-01T00:00")
    g.MPLDTIMECORRECTION                = mpld.date2num(np.datetime64('0000-12-31'))     # = -719163.0 matplotlib timebase corection

except Exception as e:
    exc_type, exc_obj, exc_tb = sys.exc_info()
    fname                     = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]            # filename of this script

    print(BOLDRED + "\nGeigerLog Installation Problem:", TDEFAULT)
    print(TYELLOW + "    EXCEPTION when importing Python modules: '{}' in file: {} in line: {}".format(e, fname, exc_tb.tb_lineno), TDEFAULT)
    # print(TYELLOW, traceback.format_exc(), TDEFAULT)
    print("""
    No access to one or more Python modules required by GeigerLog. Cannot continue, will exit!

    Did you do a full setup after installation? Try starting GeigerLog with this command:

          on Linux, Mac: ./GeigerLog.sh setup
          on Windows:    GeigerLog.bat setup

    More details can be found in chapter 'Appendix I - Installation' of the GeigerLog manual.
    """)

    print(TDEFAULT)
    sys.exit()

try:
    import sounddevice       as sd      # sound output & input
                                        # When an error “OSError: PortAudio library not found” 1) comes up,
                                        # you may have to install these programs: (thanks to user engelbert!)
                                        #   sudo apt install libportaudio2      # das reicht aus! ja, gerade wieder auf Raspi passiert; auch auf Raspi 5
                                        #   sudo apt install libasound-dev      # nicht benötigt
except Exception as e:
    exc_type, exc_obj, exc_tb = sys.exc_info()
    fname                     = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]            # filename of this script
    print(BOLDRED + "\nGeigerLog Installation Problem:", TDEFAULT)
    print(TYELLOW + "    EXCEPTION when importing module 'sounddevice' : '{}' in file: {} in line: {}".format(e, fname, exc_tb.tb_lineno), TDEFAULT)
    # print(TYELLOW, traceback.format_exc(), TDEFAULT)

    print(TYELLOW + "\n    Verify that package 'libportaudio2' is installed using your distribution's tools. If missing, please, install it,")
    print("    E.g., if you are on a Debian-like system, this would be by command:")
    print("        'sudo apt install libportaudio2'")
    print("\n    Cannot continue, will exit!", TDEFAULT)

    sys.exit()

#
# Getting Version numbers
#
# # Getting the version numbers of Qt, SIP and PyQt:
# # https://wiki.python.org/moin/PyQt/Getting%20the%20version%20numbers%20of%20Qt%2C%20SIP%20and%20PyQt
#     from PyQt4.QtCore     import QT_VERSION_STR
#     from PyQt4.Qt         import PYQT_VERSION_STR
#     from sip              import SIP_VERSION_STR
#     print("Qt version:",  QT_VERSION_STR)
#     print("SIP version:", SIP_VERSION_STR)
#     print("PyQt version:",PYQT_VERSION_STR)
from PyQt5.sip import SIP_VERSION_STR     # vscode is wrong, this does NOT give an error

# sqlite3.version:                The version number of this module, as a string. This is not the version of the SQLite library.
# sqlite3.version_info:           The version number of this module, as a tuple of integers. This is not the version of the SQLite library.
# sqlite3.sqlite_version:         The version number of the run-time SQLite library, as a string.
# sqlite3.sqlite_version_info:    The version number of the run-time SQLite library, as a tuple of integers.
#

notfound            = "Not found"
pyqt5sip_version    = notfound
ntplib_version      = notfound
setuptools_version  = notfound
# playsound_version   = notfound

from matplotlib       import __version__        as mpl_version
from paho.mqtt        import __version__        as paho_version
from pip              import __version__        as pip_version

if sys.version_info >= (3, 8):    # only Python version >= v3.8
    # Use of pkg_resources is discouraged in favor of importlib.resources, importlib.metadata,
    # and their backports (resources, metadata).
    # Do NOT use:
    #   import pkg_resources
    #   setuptools_version = pkg_resources.get_distribution('setuptools').version
    import importlib.metadata

    try:    pyqt5sip_version    = importlib.metadata.version('PyQt5-sip')
    except: pass

    try:    ntplib_version      = importlib.metadata.version('ntplib')
    except: pass

    # try:    playsound_version   = importlib.metadata.version('playsound')
    # except: pass

    # from setuptools  import __version__ as setuptools_version # this fails; maybe because it is installed by debian?
    try:    setuptools_version  = importlib.metadata.version('setuptools')
    except: pass

g.versions                         = {}
g.versions["GeigerLog"]            = g.__version__
g.versions["Python"]               = sys.version.replace('\n', "")
g.versions["pip"]                  = pip_version
g.versions["setuptools"]           = setuptools_version

g.versions["PyQt"]                 = PYQT_VERSION_STR
g.versions["Qt"]                   = QT_VERSION_STR
g.versions["SIP"]                  = SIP_VERSION_STR
g.versions["PyQt5-sip"]            = pyqt5sip_version

g.versions["matplotlib"]           = matplotlib.__version__
g.versions["matplotlib backend"]   = matplotlib.get_backend()
g.versions["numpy"]                = np.__version__
g.versions["numpy float-errors"]   = np.geterr()                        # Get the current way of handling floating-point errors.
g.versions["scipy"]                = scipy.__version__

g.versions["sqlite3 module"]       = sqlite3.version
g.versions["sql3lib library"]      = sqlite3.sqlite_version

# g.versions["playsound"]          = playsound_version
g.versions["soundfile"]            = soundfile.__version__
g.versions["sounddevice"]          = sd.__version__
g.versions["PortAudio"]            = sd.get_portaudio_version()
g.versions["pyserial"]             = serial.__version__
g.versions["paho-mqtt"]            = paho_version
g.versions["psutil"]               = psutil.__version__
g.versions["ntplib"]               = ntplib_version

udul = "undefined until loaded"
# g.versions["telegram"]             = udul                               # telegram_version
g.versions["urllib3"]              = udul                               # urllib3.__version__
g.versions["LabJackPython"]        = udul                               # LabJackPython.__version__
g.versions["U3"]                   = udul                               # this has no version!
g.versions["EI1050"]               = udul                               # ei1050.__version__
g.versions["RPi.GPIO"]             = udul                               # GPIO.VERSION,      see gdev_raspipulse
g.versions["smbus2"]               = udul                               # smbus.__version__, see gdev_raspii2c
g.versions["bmm150"]               = udul                               # version of I2C module BMM150


# # colors for the terminal (do not put in gglobs, as this would require 'g.' prefix!)
# # https://gist.github.com/vratiu/9780109
# # https://stackoverflow.com/questions/5947742/how-to-change-the-output-color-of-echo-in-linux
# # '90' values are supposed to be high intensity
# TDEFAULT            = '\033[0m'             # default, i.e greyish
# TRED                = '\033[91m'            # red
# TGREEN              = '\033[92m'            # light green
# TYELLOW             = '\033[93m'            # yellow
# TBLUE               = '\033[94m'            # blue (dark)
# TMAGENTA            = '\033[95m'            # magenta
# TCYAN               = '\033[96m'            # cyan
# TWHITE              = '\033[97m'            # high intensity white

# INVMAGENTA          = '\033[45m'            # invers magenta looks ok
# INVBOLDMAGENTA      = '\033[45;1m'          # invers magenta with bold white

# # BOLDxyz are brighter colors
# BOLDRED             = '\033[91;1m'          # bold red
# BOLDGREEN           = '\033[92;1m'          # bold green
# BOLDYELLOW          = '\033[93;1m'          # bold yellow
# BOLDBLUE            = '\033[94;1m'          # bold blue
# BOLDMAGENTA         = '\033[95;1m'          # bold magenta
# BOLDCYAN            = '\033[96;1m'          # bold cyan
# BOLDWHITE           = '\033[97;1m'          # bold white

# # UNDERLINE         = '\033[4m'             # underline
# # BOLDREDUL         = '\033[31;1;4m'        # bold, red, underline, low intens?
# # BOLDREDUL         = '\033[91;1;4m'        # bold, red, underline, high intens?
# # BOLDRED           = '\033[31;1m'          # bold, red, (low intens?)

# # if "WINDOWS" in platform.platform().upper():# no terminal colors on Windows uhmm - jetzt aber doch??
# #     TDEFAULT        = ""                    # normal printout
# #     TRED            = ""                    # (dark) red
# #     TGREEN          = ""                    # hilite message
# #     TYELLOW         = ""                    # error message
# #     TBLUE           = ""                    #
# #     TMAGENTA        = ""                    # devel message
# #     TCYAN           = ""                    # devel message
# #     TWHITE          = ""                    # unused

# #     INVMAGENTA      = ""                    # devel message
# #     INVBOLDMAGENTA  = ""                    # unused

# #     BOLDRED         = ""                    # devel message
# #     BOLDGREEN       = ""                    # devel message
# #     BOLDYELLOW      = ""                    #
# #     BOLDBLUE        = ""                    #
# #     BOLDMAGENTA     = ""                    # unused
# #     BOLDCYAN        = ""                    #
# #     BOLDWHITE       = ""                    #

gglred              = g.GooColors[0]        # Google colors
gglyellow           = g.GooColors[1]
gglgreen            = g.GooColors[2]
gglblue             = g.GooColors[3]

### define the queues

# logcycle queues
g.MemDataQueue       = deque()              # datalist to be saved to memory;               unlimited size
g.SaveLogValuesQueue = deque()              # datalist to be saved to DB;                   unlimited size
g.LogPadQueue        = deque()              # text to be shown on LogPad after a Log roll;  unlimited size

# msg queues
g.qefprintMsgQueue   = deque()              # text to be printed to terminal;               unlimited size
g.SoundMsgQueue      = deque()              # sound clip to be played;                      unlimited size

# Alarm queues
for vname in g.AlarmQueues: g.AlarmQueues[vname] = deque([], 60)                            # size limited to 60


# seed the random number generator with a develish sequence
# sequence of random values is always the same!
np.random.seed(666)


def getProgName():
    """Return program_base, i.e. 'geigerlog' even if named 'geigerlog.py' """

    progname          = os.path.basename(sys.argv[0])
    progname_base     = os.path.splitext(progname)[0]

    return progname_base


def getPathToProgDir():
    """Return full path of the program directory"""

    dp = os.path.dirname(os.path.realpath(__file__))
    return dp


def getPathToDataDir():
    """Return full path of the data directory"""

    dp = os.path.join(getPathToProgDir(), g.dataDirectory)
    return dp


def getPathToConfigDir():
    """Return full path of the config directory"""

    dp = os.path.join(getPathToProgDir(), g.configDirectory)
    return dp


def getPathToResDir():
    """Return full path of the resource (icons, sounds) directory"""

    dp = os.path.join(getPathToProgDir(), g.gresDirectory)
    return dp


def getPathToWebDir():
    """Return full path of the web (html, js) directory"""

    dp = os.path.join(getPathToProgDir(), g.webDirectory)
    return dp


def getPathToProglogFile():
    """Return full path of the geigerlog.proglog file"""

    dp = os.path.join(g.dataDir, g.progName + ".proglog")
    return dp


def getPathToConfigFile():
    """Return full path of the geigerlog.cfg file"""

    dp = os.path.join(g.progDir, g.configDirectory, g.progName + ".cfg")
    return dp


def getPathToSettingsFile():
    """Return full path of the geigerlog.settings file"""

    dp = os.path.join(g.progDir, g.configDirectory, g.progName + ".settings")
    return dp


def stime():
    """Return current time as YYYY-MM-DD HH:MM:SS"""

    # sollte beides gehen:
    #       return time.strftime("%Y-%m-%d %H:%M:%S")
    #       return longstime()[:-4]

    return time.strftime("%Y-%m-%d %H:%M:%S")                               # 1 sec resolution


def medstime():
    """Return current time as HH:MM:SS.m, (m= 100 millisec)"""

    return dt.datetime.now().strftime("%H:%M:%S.%f")[:-5]             # 100 ms resolution


def getFullHour():
    """return just the hour value"""

    return int(dt.datetime.now().strftime("%H"))


def getMinute():
    """return just the minute value"""

    return int(dt.datetime.now().strftime("%M"))


def longstime():
    """Return current time as YYYY-MM-DD HH:MM:SS.mmm, (mmm=millisec)"""

    return dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]    # 1 ms resolution


def datestr2num(string_date):
    """convert a DateTime string in the form YYYY-MM-DD HH:MM:SS to a Unix timestamp in sec"""

    #print("datestr2num: string_date", string_date)
    try:    dtn = time.mktime(dt.datetime.strptime(string_date, "%Y-%m-%d %H:%M:%S").timetuple())
    except: dtn = 0

    return dtn


def num2datestr(timestamp):
    """convert a Unix timestamp in sec to a DateTime string in the form YYYY-MM-DD HH:MM:SS"""

    ndt = dt.datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d %H:%M:%S")
    # rdprint("num2datestr: timestamp: '{}'   ndt: '{}'".format(timestamp, ndt))

    return ndt


def num2datestrMS(timestamp):   # with ms!
    """convert a Unix timestamp in sec to a DateTime string in the form YYYY-MM-DD HH:MM:SS.mmm"""

    ndt = dt.datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d %H:%M:%S.%f")
    # rdprint("num2datestr: timestamp: '{}'   ndt: '{}'".format(timestamp, ndt))

    return ndt


def longnum2datestr(timestamp):
    """convert a Unix timestamp in sec to a DateTime string in the form YYYY-MM-DD HH:MM:SS.%f"""

    longdt = dt.datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]    # 1 ms resolution
    # print("num2datestr: timestamp", timestamp, ", longdt: ", longdt)

    return longdt


def sortDict(myDict):
    """sorts a dict by key"""

    return dict(sorted(myDict.items()))


def clamp(n, minn, maxn):
    """limit return value to be within minn and maxn, including"""

    return min(max(n, minn), maxn)


def IntToChar(intval):

    if intval < 128 and intval > 31:    char = chr(intval)
    else:                               char = " "

    return char


# for the dprint output
def BytesAsASCIIFF(bytestring):
    """convert a bytes string into a string which has ASCII characters when
    printable and '.' else, with spaces every 10 bytes"""

    if bytestring is None: return ""

    asc = "  0:0x000 "
    gap = " " * 3
    for i in range(0, len(bytestring)):
        a = bytestring[i]
        if   a > 31 and a < 128:    asc += gap + chr(a)
        elif a == 255:              asc += gap + "F"
        else:                       asc += gap + " "

        if   ((i + 1) % 40) == 0: asc += "\n{:3d}:0x{:03X} ".format(i + 1, i + 1)
        elif ((i + 1) % 10) == 0: asc += "   "

    return asc


# for the fprint output
def fBytesAsASCIIFF(bytestring):
    """convert a bytes string into a string which has ASCII characters when
    printable and '.' else, with spaces every 10 bytes"""

    if bytestring is None: return ""

    asc = "  0:0x000   "
    for i in range(0, len(bytestring)):
        a = bytestring[i]
        if   a < 128 and a > 31:    asc += chr(a)
        elif a == 255:              asc += "F"
        else:                       asc += "."

        if   ((i + 1) % 50) == 0: asc += "\n{:3d}:0x{:03X}   ".format(i + 1, i + 1)
        elif ((i + 1) % 10) == 0: asc += "    "
        elif ((i + 1) %  5) == 0: asc += " "

    return asc


def BytesAsHex(bytestring):
    """convert a bytes string into a str of Hex values, with dash spaces
    every 10 bytes and LF every 50"""

    bah = ""
    if bytestring is None: return bah

    bah += "{:3n}:0x{:03X} ".format(0, 0)
    for i in range(0, len(bytestring)):
        bah += "  {:02X}".format(bytestring[i])

        if   ((i + 1) % 40) == 0 :
            bah += "\n"
            bah += "{:3n}:0x{:03X} ".format(i + 1, i + 1)
        elif ((i + 1) % 10) == 0 :
            bah += "   "

    return bah


# this one has only 40 values per line
def BytesAsDec(bytestring):
    """convert a bytes string into a str of Dec values, with dash spaces
    every 10 bytes and LF every 40"""

    bad = ""
    if bytestring is None: return bad

    bad += "{:3n}:0x{:03X} ".format(0, 0)
    for i in range(0, len(bytestring)):
        bad += " {:3d}".format(bytestring[i])
        if   ((i + 1) % 40) == 0 :
            bad += "\n"  # no '- '
            bad += "{:3n}:0x{:03X} ".format(i + 1, i + 1)

        elif ((i + 1) % 10) == 0 :
            bad += "   "

    return bad


def convertB2Hex(bseq):
    """Convert bytes sequence to Hex string"""

    return "{:25s} == ".format(str(bseq)) + "".join("{:02X} ".format(arg) for arg in bseq)


def orig(thisfile):
    """Return name of calling program and line number of call
    requires that this routine is called by orig(__file__)"""

    lineno = inspect.currentframe().f_back.f_lineno     # get the current line number
    fn     = os.path.basename(thisfile)

    #print "orig:", inspect.currentframe().__name__
    #print "orig:", inspect.getmembers()
    #print "orig:", sys._getframe(1).f_code.co_name

    return fn, sys._getframe(1).f_code.co_name, lineno


def header(txt):
    """position txt within '==...==' string"""

    return "<br>==== {} {}".format(txt, "=" * max(1, (80 - len(txt))))


def logPrint(arg, clear=False):
    """print arg into logPad"""

    if clear:
        g.lastLogLineClear = False
        cursor = g.logPad.textCursor()
        cursor.movePosition(QTextCursor.End)
        cursor.select(QTextCursor.LineUnderCursor)
        cursor.removeSelectedText()
        cursor.deletePreviousChar()         # Added to trim the newline char when removing last line
        # g.logPad.setTextCursor(cursor)    # always sets cursor to the end --> you can't scroll up and read

    g.logPad.append(arg)


def efprint(*args, debug=False):
    """error fprint with err sound"""

    fprint(*args, error="ERR", errsound=True)
    QtUpdate()


def qefprint(*args, debug=False):
    """quiet error fprint, error color but no errsound"""

    fprint(*args, error="ERR", errsound=False)


def fprintInColor(text, color):
    """print to notepad a single line text in color using implied HTML coding"""

    # use allowed colors only
    colortuple = ("black", "red", "orange", "yellow", "green", "blue", "magenta", "purple", "violet", gglred, gglgreen, gglyellow, gglblue)
    if not color in colortuple:  color = "black"

    newtext = "<span style='color:{};'>{}</span>".format(color, text)

    g.notePad.append(newtext)


def fprint(*args, error="", errsound=False):
    """print all args into the notePad; print in red on error"""

    #### local    #######################################################
    def getColorText(item):
        if   "<blue>"  in item: color = "blue"
        elif "<red>"   in item: color = "red"
        elif "<green>" in item: color = "green"
        else:                   color = "black"

        text = item.replace("<{}>".format(color), "").replace("</{}>".format(color), "")
        text = "{:30s}".format(text).replace(" ", "&nbsp;")

        return (color, text)
    #### end local #######################################################

    if errsound:  burp()

    # handle the leftmost arg
    arg0      = str(args[0])
    splitarg0 = arg0.strip("\n").split("\n")

    if len(splitarg0) == 1:
        # the arg0 is only a single line item, perhaps followed
        # by other args for printing in the same line
        for item in splitarg0:
            color, text = getColorText(item)
            if error == "ERR":      color = "red"   # override the color on errorflag

        # add any other args beyond arg0
        for s in range(1, len(args)):   text += str(args[s]).replace(" ", "&nbsp;")

        # print 1 full line in all same color
        fprintInColor(text, color)

    else:
        # when arg0 is multiline, there MUST NOT be any other args following!
        for item in splitarg0:
            color, text = getColorText(item)
            if error == "ERR":      color = "red"   # override the color on errorflag

            # print each line individually in its color
            fprintInColor(text, color)              # complete line all in same color

    # g.notePad.ensureCursorVisible()           # works by moving text to left, so that
                                                # cursor on right-most position becomes visible.
                                                # but then requires moving text to left; not helpful
                                                # also: when text is scrolled upwards, new text
                                                # does not become visible!

    # jump to the end of text --> new text will always become visible
    g.notePad.verticalScrollBar().setValue(g.notePad.verticalScrollBar().maximum())


def commonPrint(ptype, *args, error=""):
    """Printing function to dprint, vprint, wprint, and xdprint
    ptype : DEBUG, VERBOSE, werbose, DEVEL
    args  : anything to be printed
    error : "" or "ERR" or color_codeword (like:green)
    return: nothing
    """

    if ptype == "DEVEL" and not g.devel: return  # no printing DEVEL unless g.devel is true

    # create the error markers
    if   error == "":         col = ("",            "")
    elif error == "ERR":      col = (TYELLOW,       TDEFAULT)
    elif error == "yellow":   col = (TYELLOW,       TDEFAULT)
    # elif error == "green":    col = (TGREEN,        TDEFAULT)
    elif error == "green":    col = (BOLDGREEN,     TDEFAULT)
    elif error == "cyan":     col = (TCYAN,         TDEFAULT)
    elif error == "magenta":  col = (INVMAGENTA,    TDEFAULT)
    elif error == "red":      col = (BOLDRED,       TDEFAULT)    # TRED  ist zu dunkel
    else:                     col = (TDEFAULT,      "")

    g.xprintcounter += 1                         # the count of dprint, vprint, wprint, xdprint commands
    tag = ""
    for arg in args: tag += str(arg)

    if tag == "":
        # if all args are empty, write blank line both to terminal and log file, and return
        print()
        # writeFileA(g.proglogFile, " ")

    else: # tab > ""
        # something will be printed and saved

        # last resort: any "\x00" in text files results in geany (and others), not being able to open the file; replace with "?"
        if "\x00" in tag: tag = tag.replace("\x00", "?")

        # make line:  '2023-07-12 09:20:27.745 DEVEL  : 123456  <tag>'
        tag  = "{:23s} {:7s}: {:.>6d} ".format(longstime(), ptype, g.xprintcounter) + g.debugIndent + tag

        # print to terminal with any color code; shorten the datetime to show day + time only
        # becomes:  '12 09:20:27.745 DEVEL  : 123456  <tag>'
        # NOTE: on a Raspi3 this failed with "UnicodeEncodeError: 'latin-1' codec can't encode character '\u2265' "
        #       because there was Unicode-Zeichen „≥“ (U+2265) in the text. Strange, has never happend elsewhere???
        try:
            # raise("printing")
            print(col[0] + tag[8:] + col[1])
        except Exception as e:
            print(TYELLOW + str(bytes(tag[8:], "UTF-8")) + col[1])

        # remove any color code from the tag to be written to file; \x1B = ESC, followed by codes like:  ['\x1B[0m', '\x1B[96m', ...
        if "\x1B" in tag:
            codes = ['[0m', '[92;1m', '[96m', "[92;1m41", "[92;1m30", "[92m", "[91;1m41", "[91;1m30", "[91m", "[91;1m", ]
            for c in codes:     tag = tag.replace("\x1B" + c, "")

        # writeFileA(g.proglogFile, tag)  # ohne colors

    writeFileA(g.proglogFile, tag)
    if g.writeDevelproglog:  writeFileA(g.proglogFile + ".devel", tag)  # Exact Duplicate of geigerlog.prohlog up to g.LimitFileSize


def wprint(*args, forcewerbose=False):
    """werbose print:
    if werbose is true then:
    - Write timestamp and args as a single line to progname.proglog file
    - Print args as single line
    else
    - do nothing
    """
    if forcewerbose or g.werbose: commonPrint("werbose", *args)


def vprint(*args, forceverbose=False):
    """verbose print: if forceverbose or g.verbose is true then:
            - Write timestamp and args as a single line to progname.proglog file
            - Print args as single line
    else
            - do nothing
    """
    if forceverbose or g.verbose: commonPrint("VERBOSE", *args)


def dprint(*args, debug=False ):
    """debug print:
    if debug or g.debug is true then:
    - Write timestamp and args as a single line to progname.proglog file
    - Print args as single line
    else
    - do nothing
    """
    if debug or g.debug: commonPrint("DEBUG", *args)


#print as debug error yellow
def edprint(*args, debug=True):
    """debug print in error yellow"""

    commonPrint("DEBUG", *args, error="ERR")


#print in yellow
def ydprint(*args, debug=True):
    """debug print"""

    commonPrint("DEVEL", *args, error="yellow")


# print in green
def gdprint(*args, debug=True):
    """debug print"""

    commonPrint("DEVEL", *args, error="green")


# print in cyan
def cdprint(*args, debug=True):
    """debug print"""

    commonPrint("DEVEL", *args, error="cyan")


# print in magenta
def mdprint(*args, debug=True):
    """debug print"""

    commonPrint("DEVEL", *args, error="magenta")


# print in red
def rdprint(*args, debug=True):
    """debug print"""

    commonPrint("DEVEL", *args, error="red")


def arrprint(text, array):
    """ prints an array """

    print(text)
    for a in array: print("{:10s}: ".format(a), array[a])


def exceptPrint(e, srcinfo):
    """Print exception details (errmessage, file, line no)"""

    defname = "exceptPrint: "

    exc_type, exc_obj, exc_tb = sys.exc_info()
    # rdprint(defname, "sys.exc_info(): ", sys.exc_info(), type(sys.exc_info()), type(exc_type), type(exc_obj), type(exc_tb) )
    # rdprint(defname, "exc_type, exc_obj, exc_tb : ", exc_type, exc_obj, exc_tb,  type(exc_type), type(exc_obj), type(exc_tb) )
    # rdprint(defname, "srcinfo: ", srcinfo)
    if exc_tb is None:
        fname  = "'filename unknown'"
        lineno = "'lineno unknown'"
    else:
        fname  = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]    # which file?
        lineno = exc_tb.tb_lineno

    edprint("EXCEPTION: {} (e:'{}') in file: {} in line: {}".format(srcinfo.replace("\n", " "), e, fname, lineno))
    if g.traceback:
        ydprint(traceback.format_exc(), debug=True) # print only on devel & trace


def setIndent(arg):
    """increases or decreased the indent of debug/verbose print"""

    if arg > 0:  g.debugIndent += "   "
    else:        g.debugIndent  = g.debugIndent[:-3]


def cleanHTML(text):
    """replace chars with special HTML meaning with HTML-printable chars"""

    # when printing in error mode the < and > chars in the GMC commands may be
    # interpreted as HTML such that an b'<GETCPML>>' becomes a b'>' !

    defname = "cleanHTML: "

    html_escape_table = {
                        "&": "&amp;",
                        '"': "&quot;",
                        "'": "&apos;",
                        ">": "&gt;",
                        "<": "&lt;",
                        }
    try:
        if type(text) in (str,): modtext = text
        else:                    modtext = str(text)
        cleantext = "".join(html_escape_table.get(c, c) for c in modtext)
    except Exception as e:
        cleantext = "Unknown ERROR"
        exceptPrint(e, defname + cleantext)

    return cleantext


def writeSettingsFile():
    """write the entire settings file"""

    # runtime < 2   ms when writing
    #         < 0.1 ms when NOT writing

    # wsfStart = time.time()
    defname = "writeSettingsFile: "

    # json settings
    settings = {}
    settings["geom"]  = ("{},{},{},{}".format(*g.NewWinGeom ))
    settings["split"] = ("{},{},{},{}".format(*g.NewWinSplit))

    if g.dispLastValsWinPtr is not None:
        dpos  = g.dispLastValsWinPtr.pos()
        dsize = g.dispLastValsWinPtr.size()
        g.displayLastValsGeom = (dpos.x(), dpos.y(), dsize.width(), dsize.height())

    # DiLaVa : displayLastValsGeom
    settings["DiLaVa"] = ("{},{},{},{}".format(* g.displayLastValsGeom)) # uses last known geometry if no new one defined

    # last filename
    settings["LastLogfile"] = g.autoLogFile


    if settings != g.InitSettingsOld:
        g.InitSettingsOld = settings
        with open(g.settingsFile, "wt") as fsettings:
            fsettings.write("# Settings File is controlled by GeigerLog - Do not edit!\n")
            fsettings.write("# You may safely delete this file.\n")
            json.dump(settings, fsettings)

    # dur = 1000 * (time.time() - wsfStart)
    # rdprint(defname, "dur: {:0.3f} ms".format(dur))

    g.SettingsNeedSaving = False


def readSettingsFile():
    """Read the entire settings file"""

    defname = "readSettingsFile: "
    dprint(defname)
    setIndent(1)

    if not os.access(g.settingsFile , os.R_OK):
        dprint("{:25s}: {}".format("Settings File", "cannot be read"))
        setIndent(0)
        return

    # load all lines from settings file
    try:
        with open(g.settingsFile, "r") as fsettings:
            settinglines = fsettings.readlines()

    except Exception as e:
        msg = "Cannot load Settings file; continuing with default settings."
        exceptPrint(e, msg)
        g.WinSettingsDefault = True

    else:
        try:
            for setline in settinglines:
                setline = setline.strip()
                # rdprint(setline)
                if setline.startswith("{"):
                    json_object = json.loads(setline)
                    # rdprint(json_object, "  ", type(json_object))

                    rl2 = json_object["geom"].split(",")
                    dprint("{:25s}: {}".format("WinGeom", rl2))
                    g.WinGeom = [int(rl2[0]), int(rl2[1]), int(rl2[2]), int(rl2[3])]

                    rl2 = json_object["split"].split(",")
                    dprint("{:25s}: {}".format("WinSplit", rl2))
                    g.WinSplit =[int(rl2[0]), int(rl2[1]), int(rl2[2]), int(rl2[3])]

                    rl2 = json_object["DiLaVa"].split(",")
                    dprint("{:25s}: {}".format("DiLaVa", rl2))
                    g.displayLastValsGeom =[rl2[0], rl2[1], rl2[2], rl2[3]]     # each item can be 'None'

                    g.autoLogFile = json_object["LastLogfile"]
                    dprint("{:25s}: {}".format("LastLogfile", g.autoLogFile))

        except Exception as e:
            msg = "Settings file is invalid; continuing with default settings."
            exceptPrint(e, msg)
            g.WinSettingsDefault = True

        else:
            g.WinSettingsDefault = False

    setIndent(0)


def clearProgramLogFiles():
    """clear the Program LogFiles at the beginning of each run"""

    defname = "clearProgramLogFiles: "

    # delete the geigerlog.proglog file
    try:    os.remove(g.proglogFile)
    except: pass

    # delete the geigerlog.proglog.devel file
    try:    os.remove(g.proglogFile + ".devel")
    except: pass

    # delete the geigerlog.proglog.zip file
    try:    os.remove(g.proglogFile + ".zip")
    except: pass

    # make init line
    # "Mµßiggang ist auch ein ° von Läßterei"
    tag  = "{:23s} PROGRAM: pid:{:d} ########### {:s}  ".format(longstime(), os.getpid(), "GeigerLog {} -- mit no meh pfupf underm füdli !".format(g.__version__))
    line = tag + "#" * 30

    # print to terminal ALWAYS
    print(TGREEN + line + TDEFAULT)     # goes to terminal in green

    # create geigerlog.proglog file ALWAYS
    writeFileW(g.proglogFile, line)     # goes to *.proglog

    # create geigerlog.proglog.devel file only when devel is set
    if g.writeDevelproglog:  writeFileW(g.proglogFile + ".devel", line)


def readBinaryFile(path):
    """Read all of the file into data; return data as bytes"""

    defname = "readBinaryFile: "
    # print(defname + "path: {} ".format(path))

    try:
        with open(path, "rb") as f:
            data = f.read()
    except Exception as e:
        data = b''
        srcinfo = "ERROR reading file"
        exceptPrint(defname + str(e), srcinfo)
        data = b"ERROR: Could not read file: " + str.encode(path)

    vprint(defname + "len: {}, data[:30]: ".format(len(data)), data[0:30])

    return data


def writeBinaryFile(path, data):
    """Create file and write data to it as binary"""

    defname = "writeBinaryFile: "
    # print(defname + "path: {}".format(path))

    try:
        with open(path, "wb") as f:
            f.write(data)
    except Exception as e:
        exceptPrint(e, defname + "FAILURE when writing file")


def writeFileW(path, writestring, linefeed=True):
    """Force a new file creation, emptying it if already existing, then write
    to it if writestring is not empty; add linefeed unless linefeed=False"""

    defname = "writeFileW: "
    # print(defname + "path: {}  writestring: {}  linefeed: {}".format(path, writestring, linefeed))

    try:
        with open(path, "wt", encoding="UTF-8", errors='replace', buffering = 1) as f:
            if writestring > "":
                if linefeed: writestring += "\n"
                f.write(writestring)
    except Exception as e:
        exceptPrint(e, defname + "Failure when writing file")


#xyz
def writeFileA(path, writestring):
    """Append writestring to file after adding linefeed"""

    defname = "writeFileA: "
    # print(defname + "path:        {}\n            writestring: {}".format(path, writestring))

    # duration: less than 0.5 ms
    try:
        with open(path, "at", encoding="UTF-8", errors='replace', buffering=-1) as f:
            f.write(writestring + "\n")
    except Exception as e:
        print(TYELLOW + longstime()[8:], "EXCEPTION in WriteFileA appending: ", e, TDEFAULT)


def appendToZipArchive():
    """if size of geigerlog.proglog is > g.LimitFileSize, then zip it, and attach to archive
    and redefine g.LimitFileSize if this limit is reached for the first time"""

    # NOTE: is used only in runCheckCycle() in ggeiger.py
    # NOTE: if initial g.LimitFileSize is reached, then g.LimitFileSize will be set new according
    #       to GLBM Benchmark, and no longer will the geigerlog.proglog.devel file be written

    # duration of making and saving ZIP file:
    #  1 ...  3 ms für   10k portions; avg ~ 1.2 ms                                         1.2/10 = 0.12
    #  1 ...  4 ms für   15k portions; avg ~ 1.3 ms                                         1.3/15 = 0.09
    #  3 ...  7 ms für   50k portions; avg ~ 4 ms                                           4 / 50 = 0.08
    #  7 ... 17 ms für  100k portions; avg ~12 ms    new: avg:  9 ms (range 5 ... 25)       9 / 100 = 0.09
    # 30 ... 40 ms für  500k portions; avg ~34 ms                                           34/ 500 = 0.07
    # 30 ...125 ms für  500k portions; avg ~38 ms                                           38/ 500 = 0.08
    #                  1000k portions;               new: avg:  51 ms (range 41 ... 74)     51/1000 = 0.05
    #                 10000k portions;               new: avg: 416 ms (range 405  ... 436)  416/10000 = 0.04    # too long!
    #
    # overnight on urkam: LimitFileSize: 1,000,000
    # duration:  avg 39,11 ms, (min	22, max	107)


    defname = "appendToZipArchive: "
    path    = g.proglogFile
    # rdprint(defname, "path: ", path)

    # get file size of geigerlog.proglog file - takes less than 50 µs
    try:
        FileSize = os.path.getsize(path)
    except Exception as e:
        exceptPrint(e, defname + "FAILURE in getting filesize of file {}".format(path))
        return

    # when file reaches LimitFileSize then ZIP file and append to ZIP archive
    # and set g.writeDevelproglog to False, so the geigerlog.proglog.devel file will no longer be updated
    if FileSize > g.LimitFileSize:
        # set g.writeDevelproglog to False, so the geigerlog.proglog.devel file will no longer be updated
        if g.writeDevelproglog: g.writeDevelproglog = False

        try:
            zipstart = time.time()

            # zipping
            #   zip the path file, and append to zipped-log archive
            #   A value of 1 (Z_BEST_SPEED) is fastest and produces the least compression, while
            #   a value of 9 (Z_BEST_COMPRESSION) is slowest and produces the most compression. (= my choice)
            #   Write the file named tmppath to the archive, giving it the archive name arcname
            timestamp = stime().replace(":", "-").replace(" ", "_")     # short timestamp
            arcname   = "geigerlog.proglog-{}.log".format(timestamp)    # geigerlog.prolog portions separated by arcname in archive
            zippath   = path + ".zip"                                   # the archive file to be created (it is a file, NOT a folder!)
            with zipfile.ZipFile(zippath, 'a', zipfile.ZIP_DEFLATED, compresslevel=9) as zipObj:
                zipObj.write(path, arcname=arcname)

            # reset proglog file by making new, empty one
            writeFileW(path, "", linefeed=True)

            zipdur  = 1000 * (time.time() - zipstart)

        except Exception as e:
            exceptPrint(e, defname + "FAILURE zipping log file")
            zipdur = -99

        # print to log
        rdprint(defname, "ZIPPING duration: {:0.1f} ms for LimitFileSize: {:,.0f}".format(zipdur, g.LimitFileSize))

        return True
    else:
        return False


def isFileReadable(filepath):
    """is filepath readable"""

    #print("isFileReadable: filepath: {}".format(filepath))

    if not os.access(filepath, os.R_OK) :
        QueuePrint("File  {} exists but cannot be read - check file permission".format(filepath))
        return False
    else:
        return True


def isFileWriteable(filepath):
    """As the dir can be written to, this makes only sense for existing files"""

    #print("isFileWriteable: filepath: {}".format(filepath))

    if os.path.isfile(filepath) and not os.access(filepath, os.W_OK) :
        QueuePrint("File {} exists but cannot be written to - check permission of file".format(filepath))
        return False
    else:
        return True


def addMenuTip(var, text):
    """add both menu tip and status tip to an action"""

    # e.g.:   PlotLogAction.setStatusTip('Plot the Log file')
    #         PlotLogAction.setToolTip  ('Plot the Log file')
    #     --> addMenuTip(PlotLogAction, 'Plot the Log file')

    #print("addMenuTip:", var, text)
    var.setStatusTip(text)
    var.setToolTip(text)


def strFontInfo(origin, fi):
    """formats font information, returns string"""

    fontinfo = "Family:{:16s}, fixed:{}, size:{}, style:{}, styleHint:{}, styleName:{}, weight:{}, exactMatch:{}"\
    .format(fi.family(), fi.fixedPitch(), fi.pointSize(), fi.style(), fi.styleHint(), fi.styleName(), fi.weight(), fi.exactMatch())

    return fontinfo


def printVarsStatus():
    """Print the current value of variables defined in gglobs"""

    clearTerminal()

    totalsize = 0
    for key, value in vars(g).items():      # important to give the value "g" (make it use all variable defined in gglobs)
                                            # without "g" it behaves like locals()
        # if "builtins" in key: continue    # builtins are only in globals(), not in gglobs!
        try:
            valuesize  = sys.getsizeof(value)
            totalsize += valuesize
            print("key: {:30s}  size: {:11n}  eval: {}".format(key, valuesize, str(eval("g." + key)).replace("\n", "??")))
        except Exception as e:
            print("e: ", e)

    rdprint("Totalsize: {:12n} Byte".format(totalsize))

    # if same Id then it has been double counted:
    # 04 16:45:12.947 DEVEL  : ...229 id logDBData:     139941174721392
    # 04 16:45:12.947 DEVEL  : ...230 id currentDBData: 139941174721392 same ID: -> double counted in totalsize
    cdprint("id logDBData:     ", id(g.logDBData))
    cdprint("id currentDBData: ", id(g.currentDBData))
    cdprint("is logDBData === currentDBData? ", "Yes" if id(g.currentDBData) == id(g.logDBData) else "no" )


def getNameSelectedVar():
    """Get the name of the variable currently selected in the drop-down box in
    the graph options"""

    vindex      = g.exgg.select.currentIndex()
    vnameselect = list(g.VarsCopy)[vindex]
    #print("getNameSelectedVar: vindex, vnameselect:", vindex, vnameselect)

    return vnameselect


def QueuePrint(text, color="red"):
    """print into print queue; printing occurs in runCheckCycle(self)"""

    g.qefprintMsgQueue.append(color + text)


def QueuePrintDVL(text):
    """print into print queue, but only in Devel mode; printing occurs in runCheckCycle(self)"""

    # if g.devel: QueuePrint("DVL {} {}".format(longstime(), text))
    if g.devel: QueuePrint("{} {}".format(longstime(), text))


def QueueSound(sndtype):
    """put sound into sound queue; playing occurs in runCheckCycle(self)"""

    g.SoundMsgQueue.append(sndtype)


def QueueSoundDVL(sndtype):
    """put sound into sound queue; playing occurs in runCheckCycle(self), but only in Devel mode"""

    if g.devel: QueueSound(sndtype)


def playSndClip(sndtype):
    """Play a soundclip using soundfile: Bip, DoubleBip, Cocoo, alarm, or Burp for everything else"""

    #soundfile: at least version 0.12.1 required!  on Linux Mint Vanessa I got no sound with  0.11.0!

    defname = "playSndClip: "

    if      sndtype.lower() == "bip":         path = os.path.join(g.resDir, 'bip.wav')
    elif    sndtype.lower() == "doublebip":   path = os.path.join(g.resDir, 'doublebip.wav')
    elif    sndtype.lower() == "cocoo":       path = os.path.join(g.resDir, 'cocoo.wav')
    elif    sndtype.lower() == "alarm":       path = os.path.join(g.resDir, 'alarm.wav')
    else:                                     path = os.path.join(g.resDir, 'burp.wav')


    # Play
    try:
        if os.path.exists(path):
            data, samplerate = soundfile.read(path)
            #print("samplerate: ", samplerate)
            pstart = time.time()
            sd.play(data, samplerate, latency='low', blocking=True)
            # pdur = 1000 * (time.time() - pstart)
            # rdprint(defname, "Dur1: {}".format(pdur))
            # # status = sd.wait()                          # may result in scratches when missing!
            #                                               # appears to be NOT needed with a sleep() after the play
            # # time.sleep(0.2)                        ???  # appears to be necessary to avoid "ALSA underrun" message

            # pdur2 = 1000 * (time.time() - pstart)
            # rdprint(defname, "Dur2: {}".format(pdur2))

    except Exception as e:
        exceptPrint(e, defname + "playing SoundClip '{}' failed".format(sndtype))


def bip():
    playSndClip(sndtype = "bip")


def burp():
    playSndClip(sndtype = "burp")


def doublebip():
    """sound formed from bip.wav"""

    playSndClip(sndtype = "doublebip")


def cocoo():
    """sound formed from download"""

    playSndClip(sndtype = "cocoo")


def soundAlarm():
    """sound formed from download"""

    playSndClip(sndtype = "alarm")


def playSingleSine(duration):
    """play a single sine wave for duration sec"""

    # play sine wave
    samplerate = 44100          # samples per sec
    sounddur   = duration       # seconds
    soundfreq  = 27.5           # Kammerton A abgeleitet (27.5 *sqrt(256) = 440)
    soundamp   = 1              # amplitude; mit steigender Amplitude Verzerrungen

    # create the time base
    t = (np.arange(samplerate * sounddur)) / samplerate
    #~print("t: ", t)

    # create the data
    freq = soundfreq * (np.sqrt(256))
    # print("Freq: {:9.4f}".format(freq))
    outdata = soundamp * np.sin(2 * np.pi * freq * t)
    #~print("outdata raw: ", outdata)
    sd.play(outdata, samplerate * 2, latency='low')
    status = sd.wait()  # without wait it becomes scratchy!


def playSineScale():
    """play sine wave scale"""

    samplerate = 44100          # samples per sec
    sounddur   = 0.3            # seconds
    soundfreq  = 27.5           # Kammerton A abgeleitet (27.5 *sqrt(256) = 440)
    soundamp   = 1              # amplitude; mit steigender Amplitude Verzerrungen

    # create the time base
    t = (np.arange(samplerate * sounddur)) / samplerate
    #~print("t: ", t)

    # create the data
    for i in list(range(0, 15)) + list(range(15, -1, -1)):
        freq = soundfreq * (np.sqrt(2) **i)
        print("Freq: {:9.4f}".format(freq))
        outdata = soundamp * np.sin(2 * np.pi * freq * t)   # Tonleiter
        #~print("outdata raw: ", outdata)
        sd.play(outdata, samplerate * 2, latency='low')
        status = sd.wait()
        time.sleep(0.1)


def playGeigerClick():
    """play a single Geiger counter like click sound as a sine wave"""

    samplerate = 44100              # samples per sec
    sounddur   = 0.05               # seconds
    soundfreq  = 440                # 440Hz = Kammerton A
    soundamp   = 0.1                # amplitude; mit steigender Amplitude Verzerrungen 1.0 may be max?

    # create the time base
    t = (np.arange(samplerate * sounddur)) / samplerate
    #print("t: len:", len(t))

    # create the data
    outdata = soundamp * (np.sin(2 * np.pi * soundfreq * t))
    sd.play(outdata, samplerate, latency=0.05)
    status = sd.wait()              # block until completion


def playGeigerCounter():
    """play Geiger counter with increasing mean count rate"""

    duration = 3
    for mean in [0.3, 1, 3, 10, 30, 100, 300, 1000, 3000]:
        print("mean: ", mean)
        counts   = 0
        ttot     = 0
        start    = time.time()
        while time.time() < (start + duration):
            t = np.random.exponential(1 / mean)
            #print("mean= {:0.0f}, t= {:0.3f} ttot= {:0.3f}  counts= {:0.0f}".format(mean, t, ttot, counts))
            time.sleep(t)
            playGeigerClick()
            ttot += t
            counts += 1

    print("finished")


def makePicFromGraph(memstream):
    """take the 'memstream' object and save pic into memory"""

    # prepare pic in memory

    # matplotlib offers some optional export options that are ONLY available to .jpg files.
    # For example, quality (default 95), optimize (default: false), progressive (default: false):
    # like:   plt.savefig('line_plot.jpg', dpi=300, quality=80, optimize=True, progressive=True)
    #
    # MatplotlibDeprecationWarning:
    # The 'quality' parameter of print_jpg() was deprecated in Matplotlib 3.3 and will be removed
    # two minor releases later. Use pil_kwargs={'quality': ...} instead.
    # like:
    #       picbytes = io.BytesIO()
    #       plt.savefig(picbytes, format="jpg", pil_kwargs={'quality':80})
    # If any parameter follows 'quality', they should be passed as keyword, not positionally.

    # timing: prepare a PNG, SVG, JPG in memory
    # with a MiniMon File of 20MB, 665000 records!
    # DEBUG  : ...233 runCheckCycle: Make SVG: 36627.4 ms  # using SVG makes the generation time explode!
    # DEBUG  : ...234 runCheckCycle: Make PNG:   933.0 ms
    # DEBUG  : ...233 runCheckCycle: Make JPG:   945.2 ms  # Qual=80; quality reduction bringt nichts:

    # mit 720 records:
    # Vorteil PNG über SVG bleibt
    # DEBUG  : ...269 runCheckCycle: Make SVG: 152.2 ms
    # DEBUG  : ...270 runCheckCycle: Make PNG:  99.3 ms
    # DEBUG  : ...244 runCheckCycle: Make JPG:  90.4 ms    # Qual=80; quality reduction bringt nichts

    defname = "makePicFromGraph: "

    t0 = time.time()
    plt.savefig(memstream, format="png")
    t1 = time.time()

    vprint(defname + "PNG: size:{} duration:{:0.1f} ms".format(sys.getsizeof(memstream), (t1 - t0) * 1000))    # size: 46 k ... 52 k, 90 ... 150 ms


def getSuStStats(vname, vardata):
    """Prduces Tip for varDisplayCheckbox und SuSt Text"""

    defname = "getSuStStats: "

    # rdprint(defname, "vname: ", vname, "  np.isnan(vardata).all(): ", np.isnan(vardata).all())

    if  np.isnan(vardata).all(): return ("", "")

    # rdprint(defname, "vname: ", vname, "  vardata: len: ", len(vardata), "\n", vardata)
    # if   g.useGraphScaledData:  var_y = applyValueFormula(vname, vardata, g.GraphScale[vname], info=defname)  # WRONG !!! use of valueformula
    if   g.useGraphScaledData:  var_y = applyGraphFormula(vname, vardata, g.GraphScale[vname], info=defname)
    else:                       var_y = vardata

    var_avg                     = np.nanmean(var_y)
    var_std                     = np.nanstd (var_y)
    if var_avg != 0: var_stdpct = var_std / var_avg
    else:            var_stdpct = g.NAN
    var_var                     = np.nanvar (var_y)
    var_max                     = np.nanmax (var_y)
    var_min                     = np.nanmin (var_y)
    var_recs                    = np.count_nonzero(~np.isnan(var_y))
    var_unit                    = g.VarsCopy[vname][2]
    var_lastval                 = "{:>7.5g}".format(g.lastLogValues[vname])

    # use in SuSt like:"Variable  [Unit]      Avg ±StdDev   Variance     Min ... Max    Recs     Last")
    fmtLineSuSt = "{:8s}: {:7s}{:>9.3f} ±{:<9.5g} ±{:<6.1%} {:>8.5g} {:>7.5g} {:>7.5g} {:7d} {}"
    fmtLineTip  = "{:s}: [{}]  Avg: {:<8.3f}  StdDev: {:<0.3g} ±{:<5.1%}    Variance: {:<0.3g}   Range: {:>0.6g} ... {:<0.6g}  Recs: {}   Last Value: {}"

    Tip                         = fmtLineTip .format(g.VarsCopy[vname][0], var_unit, var_avg, var_std, var_stdpct, var_var, var_min, var_max, var_recs, var_lastval)
    SuSt                        = fmtLineSuSt.format(vname, "[" + var_unit + "]", var_avg, var_std, var_stdpct, var_var, var_min, var_max, var_recs, var_lastval)

    return (Tip, SuSt)


# Value Scaling
def applyValueFormula(vname, value, scale, info="no info"):
    """
    Apply the 'Scaling' declared in configuration file geigerlog.cfg. Can be
    used both for value scaling as for graph scaling. - Immer noch ???
    Input:  vname:    variable name     string,           like: CPM, CPS, ..., Temp,...
            value:    value             int, float        like: 2, 3.14,                    # it CANNOT be an array!
            scale:    formula           string            like: log(val)+1000               # will be stripped and converted to upper case

    Return: the scaled value (or original in case of error)
    NOTE:   scale is already in upper-case, but may be empty
    """

    defname      = "applyValueFormula: "
    g.scaleVname = vname
    ls           = FormulaReplacer(scale)
    # rdprint(defname, "ls: ", ls)
    if ls == "value": return value      # no changes need to be applied

    # rdprint(defname, "{}  vname: {:6s}   scale: '{}'  ls: '{}'  info: '{}'".format("Table", vname, scale, ls, info))

    try:
        scaledValue = eval(ls)              # <<< evaluating formula <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
    except Exception as e:
        msg  = "SCALING FAILURE: {:6s}  formula: '{}'. Continuing with original value. ".format(vname, ls)
        exceptPrint(e, defname + msg)
        QueuePrint(msg)
        scaledValue = value         # continuing with orig value

    # rdprint(defname, "type(scaledvalue ): ", scaledValue, "  ", type(scaledValue))
    if type(scaledValue) not in (int, float, np.float64): scaledValue = g.NAN


    # rdprint(defname, "eval done: ls: '{}'   eval: '{}'".format(ls, scaledValue))
    # mdprint(defname + "vname:'{}', orig scale:'{}', mod scale:'{}', value:{}, v-scaled:{}".format(vname, scale, ls, value, scaledValue))

    return scaledValue


# Graph Scaling
def applyGraphFormula(vname, value, scale, info="no info"):
    """
    Apply the 'Scaling' declared in configuration file geigerlog.cfg. Can be
    used ONLY for graph scaling.
    Input:  vname:    variable name     string,           like: CPM, CPS, ..., Temp,...
            value:    value             int, float, array like: 2, 3.14, [1, 2, 3, ...]
            scale:    formula           string            like: log(val)+1000 # will be stripped and converted to upper case

    Return: the scaled value (or original in case of error) - if only a SINGLE value it will be converted to an array

    NOTE:   scale is already in upper-case, but may be empty
    """

    defname      = "applyGraphFormula: "
    g.scaleVname = vname
    ls           = FormulaReplacer(scale)
    if ls == "value": return value      # no changes need to be applied

    # msg          = "{}  vname: {:6s}   scale: '{}'  ls: '{}'  info: '{}'".format("Graph", vname, scale, ls, info)
    # rdprint(defname, msg)

    ls = ls.replace("MAKECPM", "GRAPHCPM")

    try:
        scaledValue = eval(ls)              # <<< evaluating formula <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
    except Exception as e:
        msg  = "SCALING FAILURE: {:6s}  formula: '{}'. Continuing with original value. ".format(vname, ls)
        exceptPrint(e, defname + msg)
        QueuePrint(msg)
        scaledValue = value         # continuing with orig value

    # gdprint(defname, "type(scaledvalue ): ", scaledValue, "  ", type(scaledValue))
    if type(scaledValue) not in (int, float, np.float64, np.ndarray): scaledValue = g.NAN

    # rdprint(defname, "eval done: ls: '{}'   eval: '{}'".format(ls, scaledValue))

    # make an array if needed and it not already is
    if type(scaledValue) is not np.ndarray:
        scaledValue = np.full_like(value, scaledValue)

    # mdprint(defname + "vname:'{}', orig scale:'{}', mod scale:'{}', value:{}, v-scaled:{}".format(vname, scale, ls, value, scaledValue))

    return scaledValue



def FormulaReplacer(ls):
    """replaces GL names with Python names"""

    # example: ls: LG(VAL)+1000                     # orig
    # becomes: ls: np.log(value)+1000               # mod

    ls = ls.strip().upper()

    if ls in ("VAL", ""): return "value"            # don't do anything if ls has only "VAL" or ""(empty)

    ls = ls.replace("VAL",          "value")        # the data of the column holding this formula

    ls = ls.replace("EXPONENTIAL",  "tempEX")       # replacing EXPONENTIAL with tempEX to avoid replacement with np.exp

    ls = ls.replace("LN",           "np.log")       # Log to base e; natural log
    ls = ls.replace("LG",           "np.log10")     # Log to base 10
    ls = ls.replace("LG2",          "np.log2")      # Log to base 2
    ls = ls.replace("EXP",          "np.exp")       # exponential

    ls = ls.replace("SIN",          "np.sin")       # sine
    ls = ls.replace("COS",          "np.cos")       # cosine
    ls = ls.replace("TAN",          "np.tan")       # tangent

    ls = ls.replace("SQRT",         "np.sqrt")      # square root
    ls = ls.replace("CBRT",         "np.cbrt")      # cube root
    ls = ls.replace("ABS",          "np.absolute")  # absolute value
    ls = ls.replace("INT",          "np.int")       # integer value

    ls = ls.replace("tempEX",       "EXPONENTIAL")  # back-replacing tempEX with EXPONENTIAL

    return ls

#para
    # next functions are already upper case, and also need no replacement
    #
    # POISSON           (CPS)                                   random Poisson value
    # NORMAL            (CPS)                                   random NORMAL value # stddev=sqrt(mean)
    # EXPONENTIAL       (CPS)                                   random EXPONENTIAL value

    # PARA_POISSON      (CPS, <deadtime in µs>)                 random Poisson, but with values removed which are pulse overlapping, and pulse extending
    # NOPA_POISSON      (CPS, <deadtime in µs>)                 random Poisson, but with values removed which are pulse overlapping
    # PARA_CORR         (Val, <deadtime in µs>)                 Paralyzing Deadtime Correction
    # NOPA_CORR         (Val, <deadtime in µs>)                 Non-Paralyzing Deadtime Correction
    # MAKECPM           (Val, <source for CPS data>)            make CPM out of CPS data
    # GRAPHCPM          (Val, <source for CPS data>)            make CPM out of CPS data
    # SUMVV             (<source for data>, <source for data>)  sum of two variable
    # COUNTER           (factor)                                count of records times factor
    # VARSUM            (<source for data>)                     sum of all values
    # CPMWITHFET        (vname, fet)                            calculates CPM from CPS with FET "correction"

    # LOADAVG           (TYPE)                                  returns load average for Type= 0, 1, 2 meaning average over 1, 5, 15 min
    # DURUPDATE         ("MEM")                                 duration of updating the memory
    # DURUPDATE         ("GRAPH")                               duration of updating the graph
    # MEMORYTOTAL       ()                                      total memory of computer in MByte
    # MEMORYPERCENT     ()                                      percent memory of computer used by process
    # MEMORYUSED        ()                                      memory in MByte used by process
    # CPUPERCENT        ()                                      percent CPU usage
    # DBSIZE            ()                                      size of database in MB
    # NTPOFFSET         ()                                      get the NTP Time server offset in ms to current computer time
    # DELTACYCLETIME    ()                                      time difference to last log cycle
    # LOGCYCLE          ()                                      length of log cycle in sec

    # PI                ()                                      Pi = 3.14 ...
    # EULER             ()                                      e  = 2.71 ...

    # SFDLDS            (days=1)                                count of SourceForge dwonloads for number of last days

    # RadPro-only functions
    # RADPROCPM         ()                                      uses the RadPro function 'GET tubeRate' to get a "CPM" value
    # RADPROHISTLEN     ()                                      downloads the RadPro Hist and returns the len of Hist (takes up to 4 sec!)
    # RADPROCLOCKDRIFT  ()                                      get the RadPro clock difference to the computer in full sec
    # RADPROFREQ        ()                                      getRadProFreq
    # RADPRODUTY        ()                                      getRadProDuty

    # BLUEPILLVOLTAGE   (port="/dev/ttyACM1")                   read voltage from BluePill Board
    # DMM Multimeter Voltcraft VC850, OW18E
    # DMMVOLTAGE        ("VC850")                               read voltage from Voltcraft VC850 with serial connection
    # DMMVOLTAGE        ("OW18E")                               read voltage from Voltcraft VC850 with Bluetooth connection
    #                                                     Note: "OW18E" can also be read from WiFiClient program DMMWiFiClient.py

    ## inactive: # GLG10             (Val)                      uses np.log10 but replaces a 0 value with g.NAN


# ergibt keinen sinn ...
# def GLG10(value):
#     """geht nur für ValueFormula"""

#     defname = "GLG10: "

#     if value > 0:
#         try:
#             nvalue = np.log10(value)
#         except Exception as e:
#             nvalue = g.NAN
#     else:
#         nvalue = g.NAN

#     print(nvalue)

#     return nvalue


### RadPro specific formulas

def RADPROCPM():
    """Use the RadPro command "GET tubeRate" to get its CPM"""

    if g.RadProHardwareId is None: return g.NAN

    import gdev_radpro
    return gdev_radpro.getRadProCPM()


def RADPROHISTLEN():
    """Use the RadPro command "GET datalog 0" to get Hist and returns len of Hist"""

    if g.RadProHardwareId is None: return g.NAN

    import gdev_radpro
    Hist, _, _ = gdev_radpro.getRadProHist(0)

    return len(Hist)


def RADPROCLOCKDRIFT():
    """Use the RadPro clock difference to the computer in full sec"""

    if g.RadProHardwareId is None: return g.NAN

    import gdev_radpro
    clockdrift = gdev_radpro.getRadProDeltaTime()

    return clockdrift


def RADPROFREQ():
    """get the RadPro PWM Frequency in Hz"""

    if g.RadProHardwareId is None: return g.NAN

    import gdev_radpro
    freq = gdev_radpro.getRadProFreq()

    return freq


def RADPRODUTY():
    """get the RadPro PWM Frequency in Hz"""

    if g.RadProHardwareId is None: return g.NAN

    import gdev_radpro
    duty = gdev_radpro.getRadProDuty() * 100

    return duty


# DMM Multimeter Voltcraft VC850, OW18E
def DMMVOLTAGE(MODEL):
    if   MODEL == "VC850": return getVC850Voltage()
    elif MODEL == "OW18E": return getOW18EVoltage()
    else:                  return g.NAN


def LOGCYCLE():
    """Get the length of the log cycle ins sec"""

    return g.LogCycle


def DELTACYCLETIME():
    """Get the time delta in ms to the last Log Cycle call"""

    defname = "DELTACYCLETIME: "

    now  = time.time()
    last = g.lasttime
    dt   = now - last
    # rdprint(defname, f"now:{now} last:{last}  dt:{dt:+0.3f} sec ")

    return dt


def MEMORYTOTAL():
    """gets total Mem in Mega-Bytes"""
    # like: 33518.006272 MByte for urkam
    # Duration: <=  µs

    defname = "MEMORYTOTAL: "
    mem     = psutil.virtual_memory().total
    # rdprint(defname, "mem: ", mem, "  ", mem / 1E6)

    return  mem / 1e6


def MEMORYPERCENT():
    """gets % Mem used by process"""
    # like: 19.200% for GeigerLog on urkam
    # Duration: <=  µs

    defname = "MEMORYPERCENT: "

    return psutil.virtual_memory().percent


def MEMORYUSED():
    """gets Mem used by process in Mega-Bytes"""
    # like:  6468.975 MByte for GeigerLog on urkam
    # Duration: <=  µs

    defname = "MEMORYUSED: "
    mem     = psutil.virtual_memory().total * psutil.virtual_memory().percent / 100
    # rdprint(defname, "mem: ", mem, "  ", mem / 1E6, " MB")

    return  mem / 1e6


def CPUPERCENT():
    """gets  % CPU Usage"""
    # Duration: <=  µs

    defname = "CPUPERCENT: "

    return psutil.cpu_percent()


def LOADAVG(type):
    """gets the load average for type=0,1,2 --> 1, 5, 15 min"""
    # Duration: <= 100 µs

    defname = "LOADAVG: "

    if type not in (0, 1, 2):
        val = g.NAN
    else:
        cpucount = psutil.cpu_count()
        lavg     = psutil.getloadavg()
        val      = lavg[type] / cpucount * 100

    return val


# def DURGRAPH():
#     """duration of updating the graph in ms"""

#     return g.DurUpdate["GRAPH"]


def COUNTER(factor=1):
    """Returns the number of records times a factor for a monotonically increasing variable"""

    defname = "COUNTER: "
    # gdprint(defname)

    try:
        counts = g.currentDBData[:, 0].size * factor
    except Exception as e:
        exceptPrint(e, defname + "factor: '{}'".format(factor))
        counts = g.NAN

    return counts


def PI():
    """Returns the number Pi"""

    defname = "PI: "
    # gdprint(defname)

    return np.pi


def EULER():
    """Returns the number e (Euler's number)"""

    defname = "EULER: "
    # gdprint(defname)

    return np.exp(1)


# def MEMORY(unit="MB"):
#     """Returns the memory used by the process GeigerLog in the unit given"""

#     defname = "MEMORY: "
#     # gdprint(defname)

#     try:
#         used_mem = round(getMemoryUsed(unit), 3)
#     except Exception as e:
#         exceptPrint(e, defname)
#         used_mem = g.NAN

#     # rdprint(defname, "used_mem: ", used_mem)

#     return used_mem


def DURUPDATE(type = ""):
    """Returns the duration in ms of updating various actions during logging"""

    defname = "DURUPDATE: "
    # gdprint(defname)

    if   type.upper() == "MEM":    dur = round(g.DurUpdate["MEM"], 3)
    elif type.upper() == "GRAPH":  dur = round(g.DurUpdate["GRAPH"], 3)
    else:                          dur = g.NAN

    return dur


def DBSIZE(unit="MB"):
    """Returns the database file size in Bytes"""

    defname = "DBSIZE: "
    # gdprint(defname, g.logDBPath)

    factor = getFactor(unit = unit)

    try:
        dbsize = os.path.getsize(g.logDBPath) / factor
    except Exception as e:
        exceptPrint(e, defname)
        dbsize = g.NAN

    return dbsize


### NICHT OK +++++++++++++++++++++++++++++++++++++++++++++++++
def VARSUM(vardata):
    """Sum up all data for variable vardata; vardata can be "VAL" or a vname, like  "CPM"
       return: a single value int or float
    """

    defname = "VARSUM: "

    rdprint(defname, "type(vardata): ", type(vardata))
    lvname = "MIST"

# VAL_obs is np.ndarray
    if type(vardata) is np.ndarray:     # e.g. when "val" is used in formula
        sumdata = np.nansum(vardata)
        lvname = "VAL"

# VAL_obs is string
    elif type(vardata) is str:          # when variable name (vname) is used in formula
        if vardata in g.VarsCopy:
            lvname = vardata
            sumdata = np.nansum(g.logSlice[vardata])
            # if g.GraphFormula:
            #     CPS_true = NOPA_CORRcalc(CPS_obs, deadtime)
            # else:
            #     # NOT graphscaling
            #     sumdata = np.nansum(g.logSlice[vardata])
        else:
            sumdata = g.NAN

    elif type(vardata) in (int, float, np.double, np.float64, np.int64) :
        sumdata = np.nansum(vardata)

    mdprint(defname, " data from: {:6s}  fill into: {:6s}  newCPMval: {}  ".format(lvname, g.scaleVname, sumdata))
    return sumdata


# def CPMWITHFET(vname, fet):
def CPMWITHFET(VNAME, FET):
    """
    calculate CPM from the last fet values of CPS; fet being "FET", the "Fast Estimate Time" in sec,
    like: FET = 3, 5, 10, 15, 20, 30, 60  (as used in GMC counters)
    vname is interpreted as a CPS(!) variable
    """

    # from: http://www.gqelectronicsllc.com/forum/topic.asp?TOPIC_ID=9506
    # reply#29, EmfDev:
    #
    #     The calculation for fast Estimate is:
    #     Let X = duration in seconds
    #     Estimated CPM = SUM(Last X seconds CPS reading) * (60/X)
    #     e.g. for 5 sec fast estimate. (e.g. [1, 0, 1, 0, 2] ==> sum = 4)
    #     Estimated CPM = 4 * 60/5 = 4*12 = 48.
    #
    #     for Dynamic Fast Estimate:
    #     x varies depending on how stable the data is from 3 seconds to 60 seconds.
    #     If the latest few CPS is significantly higher than the average CPS then the
    #     x goes to 3 for 3 seconds and then starts going to 60 as long as the CPS is
    #     stable or around certain range from the average CPS. If dynamic estimate
    #     reaches 60 seconds reading then it becomes the same as 60 second reading,
    #     then when there is sudden change in CPS again it will trigger to change
    #     back to estimate faster.
    #
    #     These numbers are called "estimate" for a reason and so the accuracy is not
    #     that great. Some users who survey the unknown do not want to put the unit
    #     there for too long and just wants to get an estimate or check if there is
    #     radiation.

    defname = "CPMWITHFET: "
    # rdprint(defname)

    FET = int(FET)                                          # sec to base estimate on

    index    = g.VarsUppercaseIndex[VNAME]
    cpsdata  = g.currentDBData[:, index]

    FETdata  = cpsdata[-FET:]
    lFETdata = FETdata.size
    # rdprint(defname, "lenFETdata: ", lFETdata)

    if lFETdata == 0: return g.NAN                          # no data at all for this variable

    try:
        rFET = int(np.nansum(FETdata) * 60 / lFETdata)      # without int() a blob is saved to DB!
    except Exception as e:
        exceptPrint(e, defname + "FET: '{}'  len(FETdata): {}".format(FET, lFETdata))
        rFET = g.NAN

    return rFET


def POISSON(mean):
    """
    Returns a random value from a Poisson distribution with given mean
    the return value will be of type 'int'
    """

    defname = "POISSON: "

    try:
        poissval = np.random.poisson(mean)
    except Exception as e:
        exceptPrint(e, defname + "mean: '{}'".format(mean))
        poissval = g.NAN

    # rdprint(defname, "poissval: ", poissval)

    return poissval


def NORMAL(mean):
    """
    Returns a random value from a Poisson distribution with given mean
    the return value will be of type 'float' rounded to 1 decimal
    """

    defname = "NORMAL: "

    try:
        stddev  = np.sqrt(mean)
        normval = round(np.random.normal(mean, stddev), 1)
    except Exception as e:
        exceptPrint(e, defname + "mean: '{}'  StdDev: {}".format(mean, stddev))
        normval = g.NAN

    # rdprint(defname, "normval: ", normval)

    return normval


def EXPONENTIAL(cps):
    """
    Returns a random value from an Exponential distribution with given rate cps,
    return value will be microseconds of type 'float'
    """
    # val = np.random.exponential(1 / CPS) * 1E6  # duration before next pulse in µs

    defname = "EXPONENTIAL: "

    tau     = 1 / cps * 1E6
    try:
        expval = np.random.exponential(tau) / 1000  # --> millisec
    except Exception as e:
        exceptPrint(e, defname + "mean: {} CPS  (=tau: {:0.1f} µs".format(cps, tau))
        expval = g.NAN

    # rdprint(defname, "CPS mean: {}  tau: {:0.1f} µs".format(mean, tau ))

    return expval


def SUMVV(var1, var2):
    """Return the sum of two variables"""

    defname = "SUMVV: "

    typevar1 = type(var1)
    typevar2 = type(var2)
    mdprint(defname, "var1: {}, type: {}   var2: {} {}".format(var1, typevar1, var2, typevar2)) # TABLE: SUMVV(VAL, "CPS2ND"): type: v1: <class 'int'>  v2: <class 'str'>
                                                                        # GRAPH: SUMVV(VAL, "CPM"):    type: v1: <class 'numpy.ndarray'>  v2: <class 'str'>
    # var1
    if   typevar1 is str:
        index    = g.VarsUppercaseIndex[var1]
        var1data = g.currentDBData[:, index]

        isarray1 = True

    elif typevar1 is np.ndarray:
        var1data = var1
        isarray1  = True

    elif typevar1 in (int, float, np.double, np.float64, np.int64) :
        var1data = var1
        isarray1 = False

    # var2
    if   typevar2 is str:
        index    = g.VarsUppercaseIndex[var2]
        var2data = g.currentDBData[:, index]

        isarray2 = True

    elif typevar2 is np.ndarray:
        var2data = var2
        isarray2 = True

    elif typevar2 in (int, float, np.double, np.float64, np.int64) :
        var2data = var2
        isarray2 = False

    try:
        newdata = var1data + var2data
        # mdprint(defname, "1 newdata: ", newdata )
        if not g.GraphFormula:
            try:
                if type(newdata) is np.ndarray: newdata = newdata[-1]   # on empty list index -1 is not defined
            except Exception as e:
                newdata = g.NAN

            # mdprint(defname, "not graph newdata: ", newdata )
    except Exception as e:
        exceptPrint(e, defname)
        if isarray1 and isarray2: newdata = np.full_like(var1, g.NAN)
        else:                     newdata = g.NAN

    mdprint(defname, "newdata: ", newdata )
    return newdata


# use this for applyValueFormula - it returns a single value (int, float)
def MAKECPM(vname):
    """Make CPM data from CPS data (=variable vname) by summing up the last 60 sec of CPS data
       and fill into variable where this formula is defined
       input:  the name of the variable from which the last up to 60 values are being used
       return: a single value int or float
    """

    defname = "MAKECPM: "

    try:
        index  = g.VarsUppercaseIndex[vname]
        vdata  = g.currentDBData[:, index][-60:]
        if np.isnan(vdata).all() or vdata.size == 0: return g.NAN

        # rdprint(defname, "g.currentDBData[:, index][-60:]: ", g.currentDBData[:, index][-60:])
        newdata = np.nansum(vdata)
        # mdprint(defname, "newdata: ", newdata)
    except Exception as e:
        exceptPrint(e, defname)
        newdata = g.NAN

    # mdprint(defname, " CPS data from: {:6s}  fill into: {:6s}  newCPMval: {}  ".format(vname, g.scaleVname, newdata))
    return newdata


#ggg
# replace MAKECPM with GRAPHCPM for scaling Graph values - it returns a np array
# NOT WORKING CORRECTLY !!!!! Do NOT use
def GRAPHCPM(VNAME):
    """
    Make CPM data from CPS data (=variable vname) by summing up the last 60 sec of CPS data
    return: an array of type np.ndarray
    """

    defname = "GRAPHCPM: "
    cdprint(defname, "VNAME: ", VNAME)

    try:
        index       = g.VarsUppercaseIndex[VNAME]
        cvdata      = g.currentDBData[:, index][:g.dataSlicerecmax + 1]
        vname       = list(g.VarsCopy)[index]

        # rdprint(defname, "index: ", index)
        # rdprint(defname, g.VarsCopy.keys())
        # rdprint(defname, list(g.VarsCopy))
        # rdprint(defname, g.VarsCopy.keys()[index])

        rdprint(defname, "g.logSlice: ", g.logSlice[vname])
        logdata     = g.logSlice[vname]
        newdata     = np.zeros_like(logdata)
        # newdata     = np.zeros_like(cvdata)

        lencvdata   = len(cvdata)
        lenlogdata  = len(logdata)
        # lenlogdata  = len(cvdata)
        # lendelta    = lencvdata - lenlogdata

        # if np.array_equal(cvdata, logdata) : msg = BOLDGREEN + " - data are the same" + TDEFAULT
        # else                               : msg = BOLDRED   + " - data NOT the same" + TDEFAULT
        # dprint(defname, "cvdata:  len: {:<3d}  data[-10:]: {}".format(lencvdata,  cvdata [-10:]))
        # dprint(defname, "logdata: len: {:<3d}  data[-10:]: {}".format(lenlogdata, logdata[-10:]), msg)
        # dprint(defname, "lendelta: ", lendelta)                                                    # expected to never be negative

        for i in range(0, lenlogdata):
            bis         = lencvdata - lenlogdata  + i
            von         = int(max(bis - 60, 0))                # cumulative period of 60 sec to convert CPS to CPM
            vdata       = cvdata[von : bis]
            newdata[i]  = np.nansum(vdata)

            ### print first and last number of "di" lines
            di  = 5
            if i < di or i > lenlogdata - di:
                xtxt = TDEFAULT + "  i: {}  ".format(i) + INVMAGENTA
                mdprint(defname, xtxt, "vdata: von: {} bis: {}  len: {}  {} ... {}".format(von, bis, len(vdata), vdata[:10], vdata[-10:]))

        mdprint(defname, "newdata: len: {}  {} ... {}".format(len(newdata), newdata[0:10], newdata[-10:]))

    except Exception as e:
        exceptPrint(e, defname)

    # mdprint(defname, " CPS data from: {:6s}  fill into: {:6s}  newCPMval: {}  ".format(vname, g.scaleVname, newdata))
    return newdata


def NOPA_CORR(VAL_obs, deadtime):
    """
    Non-Paralyzing Deadtime Correction - like **NOT** for Geiger counter
    (analytical solution)
    VAL_obs:    can be 1 of 3 things:
                1) a single value (int or float)
                2) an ndarray of values
                3) a string giving the name of the variable to be used (CPM, CPS, ..., Temp, ...)
    deadtime:   deadtime of tube in microsecond
    return:     CPS_true  by Formula:            CPS_true = CPS_obs / (1 - CPS_obs * deadtime[s])
                          in GeigerLog notation: "VAL / (1 - VAL * {})".format(deadtime)
    """

    #### begin local defs of NOPA_CORR ###################################################################################
    def NOPA_CORRcalc(CPS_obs, deadtime):
        """calc of NOPA_CORR corrected count rate
           CPS_obs:     can be 1 of 2 things:
                        1) a single value (int or float)
                        2) an ndarray of values
            return:     CPS_true (either as single value or ndarray)
        """

        defname     = "NOPA_CORRcalc: "
        tau         = deadtime / 1E6                                    # we need deadtime in second
        denominator = (1 - CPS_obs * tau)                               # must be > 0  or error!
        exceedLimit = False

        CPS_true    = CPS_obs
        try:
            if type(denominator) is np.ndarray:
                if np.all(denominator > 0):
                    msg        = TDEFAULT + BOLDGREEN + " all denominator are positiv"
                    CPS_true   = np.round(CPS_obs / denominator, 0)

                else:
                    msg        = TDEFAULT + BOLDRED   + " NOT all denominator are positiv!!!"
                    # rdprint(defname, msg)
                    # rdprint(defname, "denominator: ", denominator)

                    mdenominator = denominator
                    mdenominator [denominator <= 0] = np.nan
                    # rdprint(defname, "mdenominator: ", mdenominator)

                    CPS_true     = np.round(CPS_obs / mdenominator, 0)
                    # rdprint(defname, "CPS_true: ", CPS_true)

                    exceedLimit = True
                    lastVals   = "... "+ str(CPS_obs[-5:])
                # mdprint(defname, "ARRAY  tau: {} sec  denominator: {} -{}".format(tau, denominator[-5:], msg))

            elif type(denominator) in (int, float):
                if denominator > 0:
                    msg        = TDEFAULT + BOLDGREEN + " denominator is positiv"
                    CPS_true   = round(CPS_obs / denominator, 0)
                else:
                    msg        = TDEFAULT + BOLDRED   + " denominator is NOT positiv"
                    CPS_true   = g.PINF
                    exceedLimit = True
                    lastVals   = str(CPS_obs)
                # mdprint(defname, "SINGLE  tau: {} sec  denominator: {} -{}".format(tau, denominator, msg))

        except Exception as e:
            exceptPrint(e, defname)

        if exceedLimit:
            ref = "Graph" if g.GraphFormula else "Table"
            msg = "{}-{:6s}: NOPA_CORR impossible as raw counts exceed theoretical maximum".format(ref, g.scaleVname)
            QueuePrint(msg)
            dprint(defname, msg, " lastVals: ", lastVals)

        return CPS_true
    #### end local defs of NOPA_CORR ###############################################################################

    defname     = "NOPA_CORR: "

    try:
        # mdprint(defname, "VAL_obs: {}   Deadtime: value: {} type: '{}'  ".format(VAL_obs, deadtime, type(deadtime)))

# is the value for the deadtime acceptable?
        if not (type(deadtime) in (int, float, np.double, np.float64, np.int64)):
            msg = "Deadtime in NOPA_CORR formula must be type 'int' or 'float', but is: '{}' ({})".format(deadtime, type(deadtime))
            rdprint(defname, msg)
            QueuePrint(cleanHTML(msg))
            return g.NAN

# VAL_obs is np.ndarray
        if type(VAL_obs) is np.ndarray:     # e.g. when "val" is used in formula
            CPS_obs  = VAL_obs
            CPS_true = NOPA_CORRcalc(CPS_obs, deadtime)

# VAL_obs is string
        elif type(VAL_obs) is str:          # when variable name (vname) is used in formula
            if VAL_obs in g.VarsCopy:
                CPS_obs = g.logSlice[VAL_obs]
                if g.GraphFormula:
                    CPS_true = NOPA_CORRcalc(CPS_obs, deadtime)

                else:
                    # NOT graphscaling
                    CPS_obs  = float(CPS_obs[-1])
                    CPS_true = NOPA_CORRcalc(CPS_obs, deadtime)
            else:
                CPS_true = np.full_like(g.logTimeSlice, g.NAN)


# VAL_obs is int or float
        elif type(VAL_obs) in (int, float, np.double, np.float64, np.int64) :
            CPS_obs  = VAL_obs
            CPS_true = NOPA_CORRcalc(CPS_obs, deadtime)

# programming error
        else:
            dprint(defname, "UNEXPECTED type(VAL_obs): ", type(VAL_obs), "  ", "VAL_obs: ", VAL_obs)
            CPS_true = g.NAN

    except Exception as e:
        exceptPrint(e, defname)
        CPS_true = g.NAN

    # mdprint(defname, "CPS_true: ", CPS_true)

    return CPS_true


def PARA_CORR(VAL_obs, deadtime):
    """
    Paralyzing Deadtime correction - like for Geiger counter
    (iterative solution)
    VAL_obs:    can be 1 of 3 things:
            1) a single value (int or float)
            2) an ndarray of values
            3) a string giving the name of the variable to be used (CPM, CPS, ..., Temp, ...)
    deadtime: deadtime of tube in microsecond
    Formula:  CPS_obs = CPS_true * exp(- CPS_true * deadtime)
    """

    ###############################################################################
    # Deadtime Correction
    # die nicht verlängerbare und die verlängerbare Totzeit.
    # see:      https://de.wikipedia.org/wiki/Totzeit_(Teilchenmesstechnik)
    #           https://en.wikipedia.org/wiki/Dead_time
    # NOPA:     non-paralyzable dead time
    # PARA:     paralyzable dead time (like in Geiger counters)
    ###############################################################################


    ###################################################################################################
    def DeadTimeBalance(N, *args):
        """
        The difference between M (observed counts) and formula for Calculation of M from N (True counts)
        -> CPM_obs = CPM_true * exp(- CPM_true * deadtime)  # this formula may be called 20 times for a single value
        """

        M       = args[0]   # observed count rate
        tau     = args[1]   # deadtime

        # balance = np.log(M) - (np.log(N) - N * tau)       # based on the log version of the equation (needs 2 log() calcs)
        balance = M - (N * np.exp(-N * tau))                # based on the exp                         (needs 1 exp() calcs)
        # gdprint("M:{}, tau:{}, N:{:0.0f} balance:{:0.6f}".format(M, tau, N, balance))  # saw 20 cycles of calculation

        return balance


    def PARA_CORRcalc(val, deadtime):
        """val must be an int or a float"""
        # https://docs.scipy.org/doc/scipy/reference/generated/scipy.optimize.root.html

        defname   = "PARA_CORRcalc: "
        msg       = ""
        val_padec = g.PINF

        if np.isnan(val): return g.NAN                                  # if val is NAN, then return NAN

        try:
            tau           = deadtime / 1E6                              # we need deadtime in second
            lower_bracket = 0                                           # the count rate lower limit is 0
            if tau > 0:     upper_bracket = 1 / tau                     # the count rate upper limit is 1/tau; (e.g. at 125µs max CPS=8000)
            else:           upper_bracket = 1E9                         # Let's take 1 GHz as upper_bracket

            # Option 1: prevent exception
            DTlow         = DeadTimeBalance(lower_bracket, val, tau)    # if the two are same sign then calc cannot be made
            DTupp         = DeadTimeBalance(upper_bracket, val, tau)    # -"-
            if np.sign(DTlow) != np.sign(DTupp):
                res = scipy.optimize.root_scalar(DeadTimeBalance, args=(val, tau), x0=val, x1=val*2, xtol=0.1, method='bisect', bracket=[lower_bracket, upper_bracket] )
                if res.converged: val_padec = np.round(res.root, 0)
                else:             msg       = "Var: {:6s}: PARA_CORR did NOT converge with: val:{}, deadtime:{} µs".format(g.scaleVname, val, deadtime)
            else:
                msg = "Var: {:6s}: PARA_CORR impossible with: val:{}, deadtime:{} µs".format(g.scaleVname, val, deadtime)

            # # Option 2: allow exception
            # res = scipy.optimize.root_scalar(DeadTimeBalance, args=(val, tau), x0=val, x1=val*2, xtol=0.1, method='bisect', bracket=[lower_bracket, upper_bracket] )
            # if res.converged:   val_padec = np.round(res.root, 0)
            # else:               msg = "Var: {:6s}: PARA_CORR did NOT converge with: val:{}, deadtime:{} µs".format(g.scaleVname, val, deadtime)

        except Exception as e:
            msg = "Var: {:6s}: PARA_CORR fails with: val:{}, deadtime:{} µs".format(g.scaleVname, val, deadtime)
            exceptPrint(e, defname + msg)

        if msg > "":
            QueuePrint(msg)
            rdprint(defname, msg)

        return val_padec
    ###################################################################################################

    defname = "PARA_CORR: "
    # mdprint(defname, "  ", "type(VAL_obs): ", type(VAL_obs), "  ", "VAL_obs: ", VAL_obs, "  GraphFormula: ", g.GraphFormula)

    try:
        # is the value for the deadtime acceptable?
        if not (type(deadtime) in (int, float, np.double, np.float64, np.int64)):
            msg = "Deadtime in PARA_CORR formula must be type 'int' or 'float', but is: '{}'  value: '{}'".format(type(deadtime), deadtime)
            rdprint(defname, msg)
            QueuePrint(cleanHTML(msg))
            return g.NAN

# VAL_obs is np.ndarray
        if type(VAL_obs) is np.ndarray:                             # when variable name (vname) is used in formula
            CPS_obs  = VAL_obs
            CPS_true = np.ndarray(len(VAL_obs))
            for i, cpsval in enumerate(CPS_obs):
                ccps = PARA_CORRcalc(cpsval, deadtime)
                CPS_true[i] = np.round(ccps, 0)

# VAL_obs is string
        elif type(VAL_obs) is str:
            if g.GraphFormula:
                # graphscaling
                CPS_obs     = g.logSlice[VAL_obs]

                CPS_true = np.ndarray(len(CPS_obs))
                for i, cpsval in enumerate(CPS_obs):
                    ccps = PARA_CORRcalc(cpsval, deadtime)
                    CPS_true[i] = np.round(ccps, 0)

            else:
                # not graphscaling
                index       = g.VarsUppercaseIndex[VAL_obs]
                CPS_obs     = g.currentDBData[:, index][-1:]

                if CPS_obs.size > 0 and np.isnan(CPS_obs):
                    CPS_true = g.NAN
                else:
                    if len(CPS_obs) > 0:
                        CPS_obs  = float(CPS_obs[0])
                        CPS_true = PARA_CORRcalc(CPS_obs, deadtime)
                    else:
                        CPS_true = g.NAN        # no data, can only be NAN, not inf

# VAL_obs is int or float (=double)
        elif type(VAL_obs) in (int, float, np.double, np.float64, np.int64) :
            CPS_obs  = VAL_obs
            CPS_true = PARA_CORRcalc(CPS_obs, deadtime)

# programming error
        else:
            dprint(defname, "UNEXPECTED type(VAL_obs): ", type(VAL_obs), "  ", "VAL_obs: ", VAL_obs)
            CPS_true = g.NAN

    except Exception as e:
        exceptPrint(e, defname)
        CPS_true = g.NAN

    # if type(CPS_true) is np.ndarray: mdprint(defname, "CPS_true: ", CPS_true[:10], "...", CPS_true[-10:])
    # else:                            mdprint(defname, "CPS_true: ", CPS_true)
    return CPS_true


def PARA_POISSON(mean, deadtime):
    """
    Random samples from a Poisson distribution which loses counts due to Paralyzing effects
    a cycle of 1 sec is assumed
    input:  mean:    CPS
            deadtime in µs
    return: int or float value
    """

    # NOTES:  Tube LND 7317  https://www.lndinc.com/products/geiger-mueller-tubes/7317/
    #         GAMMA SENSITIVITY Cs-137 (CPS/mR/HR)	58
    #         MINIMUM DEAD TIME (MICRO SEC)	40

    defname = "PARA_POISSON: "

    dtm           = deadtime / 1E6          # deadtime[second] converted from given deadtime[µs]
    cps_counted   = 0                       # counts detected within present collection cycle
    cps_missed    = 0                       # counts UN-detected because too soon after last
    timePoint     = g.prevtimePointPara     # duration in sec of this current second of collection; starting with leftover from last cycle

    # mdprint(defname, "mean={:0.2f}  dtm:{}µs  timePoint={:9.6f}s  lasteventPara:{:9.6f}  prevtimePointPara:{:9.6f}s ".format(mean, deadtime, timePoint, g.lasteventPara, g.prevtimePointPara))

    if g.prevtimePointPara >= 1:                                # no events during more than one cycle; return 0 (zero)
        # rdprint(defname, "timePoint={:9.6f}s  lasteventPara:{:9.6f}  prevtimePointPara:{:9.6f}s ".format(timePoint, g.lasteventPara, g.prevtimePointPara))
        g.prevtimePointPara -= 1
    else:
        if g.prevtimePointPara > 0:
            cps_counted += 1                                    # count coming from last cycle

        while True:
            gap        = np.random.exponential(1 / mean)        # gap between two pulse-starts in sec
            timePoint += gap                                    # timepoint may be >1sec, then count will be counted in next cycle

            if timePoint > 1:                                   # count up to 1 sec only; then events will be counted in next cycle
                # gdprint(defname, "timePoint={:9.6f}s  lasteventPara:{:9.6f}  prevtimePointPara:{:9.6f}s ".format(timePoint, g.lasteventPara, g.prevtimePointPara))
                g.prevtimePointPara = timePoint - 1             # the pulse extends into next counting cycle
                g.lasteventPara    -= 1
                break                                           # counting for this cycle is over
            else:    # timePoint <= 1 sec                       # still in the current cycle
                if (timePoint - g.lasteventPara) >= dtm:
                    # cdprint(defname, "timePoint={:9.6f}s  lasteventPara:{:9.6f}  prevtimePointPara:{:9.6f}s ".format(timePoint, g.lasteventPara, g.prevtimePointPara))
                    cps_counted += 1                            # if time to last pulse is > deadtime then count it as CPS
                    g.lasteventPara = timePoint

                else:
                    # rdprint(defname, "timePoint={:9.6f}s  lasteventPara:{:9.6f}  prevtimePointPara:{:9.6f}s ".format(timePoint, g.lasteventPara, g.prevtimePointPara))
                    cps_missed += 1                             # otherwise increment missed CPS!
                    g.lasteventPara = timePoint                 # but ALSO extent duration, as the Para event has increased the deadtime!
        # end while

    # mdprint(defname, "mean={:0.2f}  dtm:{}µs  CPScounted: {}  CPSmissed: {}".format(mean, deadtime, cps_counted, cps_missed))
    return cps_counted


def NOPA_POISSON(mean, deadtime):
    """
    Random samples from a Poisson distribution which loses counts due to NON-Paralyzing effects (not applicable to Geiger counters!)
    a cycle of 1 sec is assumed
    input:  mean:    CPS
            deadtime in µs
    return: int or float value
    """

    defname       = "NOPA_POISSON: "

    dtm           = deadtime / 1E6          # deadtime[second] converted from given deadtime[µs]
    cps_counted   = 0                       # counts detected within present collection cycle
    cps_missed    = 0                       # counts UN-detected because too soon after last
    timePoint     = g.prevtimePointNopa     # duration in sec of this current second of collection; starting with leftover from last cycle

    # mdprint(defname, "mean={:0.2f}  dtm:{}µs  timePoint={:9.6f}s  lasteventPara:{:9.6f}  prevtimePointNopa:{:9.6f}s ".format(mean, deadtime, timePoint, g.lasteventNopa, g.prevtimePointNopa))

    if g.prevtimePointNopa >= 1:                            # more than 1 sec; skip counting for this 1 sec interval
        # rdprint(defname, "timePoint={:9.6f}s  lasteventPara:{:9.6f}  prevtimePointPara:{:9.6f}s ".format(mean, deadtime, timePoint, g.lasteventNopa, g.prevtimePointNopa))
        g.prevtimePointNopa -= 1
    else:
        if g.prevtimePointNopa > 0:
            cps_counted += 1                                # count set in last cycle

        while True:
            gap        = np.random.exponential(1 / mean)    # gap between two pulse starts in sec
            timePoint += gap
            if timePoint > 1:                               # count up to 1 sec only; beyond 1 sec events will be counted in next cycle
                # gdprint(defname, "timePoint={:9.6f}s  lasteventNopa:{:9.6f}  prevtimePointNopa:{:9.6f}s ".format(timePoint, g.lasteventNopa, g.prevtimePointNopa))
                g.prevtimePointNopa = timePoint - 1         # The pulse begins in next cycle
                g.lasteventNopa    -= 1                     # subtract 1 sec to have last event at proper position
                break                                       # nothing more to do in this cycle

            else:  # timePoint <= 1 sec                     # still in the current cycle
                if (timePoint - g.lasteventNopa) >= dtm:    # and time to last pulse is > deadtime,
                    # cdprint(defname, "timePoint={:9.6f}s  lasteventNopa:{:9.6f}  prevtimePointNopa:{:9.6f}s ".format(timePoint, g.lasteventNopa, g.prevtimePointNopa))
                    cps_counted += 1                        # so count it as CPS, ...
                    g.lasteventNopa = timePoint             # make this to the last pulse time point

                else:
                    # rdprint(defname, "timePoint={:9.6f}s  lasteventNopa:{:9.6f}  prevtimePointNopa:{:9.6f}s ".format(timePoint, g.lasteventNopa, g.prevtimePointNopa))
                    cps_missed += 1                         # ... otherwise count it as missed CPS!
                                                            # NOTE: lasteventNopa has NOT changed, as a non-paralyzing event!
        # end while

    # mdprint(defname, "mean={:0.2f}  dtm:{}µs  CPScounted: {}  CPSmissed: {}".format(mean, deadtime, cps_counted, cps_missed)) # total CPS would be (cps_counted + cps_missed)
    return cps_counted


#sss2
def SFDLDS(days=1):
    """get the SourceForge GeigerLog site downloads for the last 'days' days"""

    defname = "SFDLDS: "
    # gdprint(defname)
    start = time.time()

    # time period to cover is 'days' ago
    now       = time.time()                                     # today
    ago       = now - (days * 24 * 3600)                        # 'days' ago
    startdate = time.strftime("%Y-%m-%d", time.localtime(ago))  # like: 2022-10-14
    enddate   = time.strftime("%Y-%m-%d", time.localtime(now))  # like: 2022-10-21

    # https://sourceforge.net/projects/geigerlog/files/stats/json?start_date=2022-10-21&end_date=2023-01-11
    # es gehen nur Tage, keine h,m,s
    FullURL = "https://sourceforge.net/projects/geigerlog/files/stats/json?start_date={}&end_date={}".format(startdate, enddate)
    try:
        with urllib.request.urlopen(FullURL, timeout=3) as page:
            response = page.read().strip().decode("UTF-8")

        value = json.loads(response)["total"]
        msg   = "From:{}, To:{}, Downloads Value:{}".format(startdate, enddate, value)

    except Exception as e:
        value = g.NAN
        msg = "Exception: " + str(e) + "  value: {}".format(value)

    duration = 1000 * (time.time() - start)
    gdprint(defname, msg, " Dur:{:0.1f} ms  GraphFormula: {}".format(duration, g.GraphFormula))

    return value


def NTPOFFSET():
    """get the NTP Time server offset to current computer time"""

    defname = "NTPOFFSET: "
    vprint(defname)
    setIndent(1)

    start = time.time()

    offset, ntpserver = getNTPDateTime()

    duration = 1000 * (time.time() - start)
    vprint(defname, "Offset: {:+0.1f} ms    Dur:{:0.1f} ms  GraphFormula: {}".format(offset, duration, g.GraphFormula))

    setIndent(0)
    return offset


class ClickQLabel(QLabel):
    """making a label click-sensitive"""

    def __init__(self, parent):
        QLabel.__init__(self, parent)

    def mousePressEvent(self, event):
        """Changes color of the selected variable.
        Called by the color picker button in the graph options. """

        if g.currentConn is None: return # no color change unless something is loaded

        colorDial = QColorDialog()

        # rdprint("currentColor: ", colorDial.currentColor().value()) # ???
        # rdprint("currentColor: ", colorDial.currentColor().name())
        # rdprint("options: ", colorDial.options())
        # rdprint("testoption: Alpha:   ", colorDial.testOption(QColorDialog.ShowAlphaChannel))          # has no effect
        # rdprint("testoption: Buttons: ", colorDial.testOption(QColorDialog.NoButtons))                 # has no effect
        # rdprint("testoption: Nativ:   ", colorDial.testOption(QColorDialog.DontUseNativeDialog))       # has no effect

        color = colorDial.getColor()                      # shows the color dialog
        if color.isValid():
            vprint("colorPicker: new color picked:", color.name())
            g.exgg.btnColor.setStyleSheet("QLabel { border: 1px solid silver;  border-radius: 3px; background-color: %s;}" % color.name())
            addMenuTip(g.exgg.btnColor, g.exgg.btnColorText + str(color.name()))
            g.exgg.btnColor.setText("")

            vname = getNameSelectedVar()
            g.VarsCopy[vname][3] = color.name()
            g.exgg.applyGraphOptions()

        g.exgg.notePad.setFocus()


def printProgError(*args):
    print("PROGRAMMING ERROR !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
    dprint(*args, debug=True)
    setNormalCursor()
    sys.exit(-1)


def QtUpdate():
    """updates the Qt window immediately"""

    QApplication.processEvents()


def executeTPUT(action = 'allow_line_wrapping'):
    """
    set terminal output with or without linebreaks; works in Linux only
    use action = 'allow_line_wrapping' or 'no_line_wrapping'
    """
    # For generic non full screen applications, you can turn off line wrapping by
    # sending an appropriate escape sequence to the terminal:
    #   tput rmam
    # This mode can be cancelled with a similar escape:
    #   tput smam
    # also: https://tomayko.com/blog/2004/StupidShellTricks

    defname = "executeTPUT: "

    if "LINUX" in platform.platform().upper():
        if (action == 'allow_line_wrapping' or g.forcelw):
            tputcommand = "smam"                            # tput smam: turns on line wrapping on the terminal.app (set ..)
            tputmsg     = "(line wrapping is now turned ON)"

        else:   # 'no_line_wrapping'
            tputcommand = "rmam"                            # tput rmam: turns off line wrapping on the terminal.app (remove ..)
            tputmsg     = "(line wrapping is now turned OFF)"

        try:
            subprocess.call(["tput", tputcommand])
        except Exception as e:
            exceptPrint(e, "")
            edprint("{:28s}: {}".format("LineWrapping", "FAILURE executing tput {} - {}".format(tputcommand, tputmsg)), debug=True)
        else:
            dprint("{:28s}: {}" .format("LineWrapping", "SUCCESS executing tput {} - {}".format(tputcommand, tputmsg)))
    else:
        dprint("{:28s}: {}".format("LineWrapping", "Not supported on this computer (needs Linux Platform)"))


def openManual(manual_name):
    """Show the GeigerLog Manual, first try a local version, but if not present try SourceForge"""

    defname = "openManual: "
    dprint(defname)
    setIndent(1)

    fprint(header("Showing the GeigerLog Manual"))

    manual_file = None
    path = os.path.join(getPathToProgDir(), g.manualDirectory)
    if os.path.exists(path):
        for filename in os.listdir(path):
            # rdprint(defname, "filename: ", filename)
            if filename.startswith(manual_name):
                manual_file = os.path.join(path, filename)
                break                                       # file manual_name* found, exit for-loop

    if manual_file is not None:
        dprint("Using Manual_file: ", manual_file)
        # while True:
        if 1:
            # try:
            #     if sys.platform.startswith('linux'):
            #         # xdg-open command in the Linux system is used to open a file or URL in the user’s preferred application.
            #         subprocess.call(["xdg-open", manual_file])
            #         dprint("Showing via xdg-open on Linux")
            #     else:
            #         # only available on windows
            #         os.startfile(manual_file)
            #         dprint("Showing via os.startfile on other OS: '{}'".format(manual_file))
            #     break
            # except Exception as e:
            #     msg = "Failure Showing via xdg-open on Linux or via os.startfile on other OS"
            #     exceptPrint(e, defname + msg)
            #     dprint(msg)

            # try:
            #     if sys.platform.startswith('linux'):
            #         subprocess.call(["firefox", manual_file])
            #         dprint("Showing via firefox on Linux")
            #     else:
            #         os.startfile(manual_file)
            #         dprint("Showing via os.startfile on other OS")
            #     break
            # except Exception as e:
            #     msg = "Failure Showing '{}' via firefox on Linux or via os.startfile on other OS".format(manual_file)
            #     exceptPrint(e, defname + msg)
            #     dprint(msg)

            try:
                webbrowser.open(manual_file, new=2, autoraise=True)
                dprint("Showing via webbrowser")
                # break
            except Exception as e:
                msg = "Failure Showing '{}' via import webbrowser".format(manual_file)
                exceptPrint(e, defname + msg)
                dprint(msg)

    else: # manual_file is None:
        # no file has been found locally; try it online
        dprint( "A Manual_file was not found")
        efprint("A GeigerLog-Manual has not been found in the directory 'geigerlog/manual'.")
        fprint ("Now trying to find the file online; you may have to select it manually.")

        try:
            shortv = g.__version__.split("pre")[0]   # use only the version part before 'pre', like: "1.0.1pre9" --> "1.0.1"
            cdprint(defname, "g.__version__: ", g.__version__, "  --> shortv: ", shortv)

            url  = 'https://sourceforge.net/projects/geigerlog/files/GeigerLog-Manual-v{}.pdf'.format(shortv)
            if QDesktopServices.openUrl(QUrl(url)):
                dprint("Showing url: '{}'".format(url))
            else:
                QMessageBox.warning(g.exgg, 'GeigerLog Manual', 'Could not open GeigerLog Manual')
                dprint("Failure Showing manual with url: '{}'".format(url))
        except Exception as e:
            msg = "Failure Showing manual online with url: " + url
            exceptPrint(e, defname + msg)

    # efprint("Could not find GeigerLog-Manual, neither locally nor online!")

    setIndent(0)


def showSystemInfo(target = "window"):          # alternative: Terminal
    """Show System Info on the Devel Menu"""

    defname = "showSystemInfo: "

    screen           = QDesktopWidget().screenGeometry()
    screen_available = QDesktopWidget().availableGeometry()
    geom             = g.exgg.geometry()
    geom_frame       = g.exgg.frameGeometry()

    fmt              = "{:38s}{}\n"
    si               = ""

    # user
    si += fmt.format("Username:",                        "{}".format(os.environ.get('USER')))

    # platform
    si += fmt.format("\nPlatform:",                      "")
    si += fmt.format("  Operating System:",              "{}".format(platform.platform()))
    si += fmt.format("  OS Name:",                       "{}".format(os.name)) # os.name: posix (on Linux), 'nt' (on Windows), 'java' (on ?)
    si += fmt.format("  Byte Order:",                    "{}".format(sys.byteorder))
    si += fmt.format("  XDG Windowing System",           str(os.getenv("XDG_SESSION_TYPE")) + "  (Linux, Mac: x11, Wayland; Windows: None)")
                                                            # Linux:    X11 or Wayland
                                                            # Mac:      X11 or Wayland
                                                            # Windows:  None
    # Process
    si += fmt.format("\nProcess Info:",                  "")
    si += fmt.format("  PID:",                           "{}".format(g.geigerlog_pid))
    si += fmt.format("  Virtual Environment:",           "{}".format(g.VenvMessage))
    si += fmt.format("     sys.base_prefix:",            "{}".format(sys.base_prefix))
    si += fmt.format("     sys.prefix:",                 "{}".format(sys.prefix))

    # System
    try:
        si += fmt.format("\nSystem Info:",               "")
        si += fmt.format("  CPU Model",                  g.CPU_Model)
        si += fmt.format("  CPU Vendor",                 g.CPU_Vendor)
        si += fmt.format("  CPU Hardware",               g.CPU_Hardware)
        si += fmt.format("  Machine:",                   "{}, {}".format(platform.machine(), platform.architecture()[0]))

        si += fmt.format("  CPU cores:",                 "{} "          .format(psutil.cpu_count(logical=False)))
        si += fmt.format("  CPU logical cores:",         "{} "          .format(psutil.cpu_count(logical=True )))
        si += fmt.format("  CPU Frequency:",             "{} "          .format(psutil.cpu_freq()))
        si += fmt.format("  CPU Load Avg:",              "{} (last 1, 5 and 15 minutes)".format(psutil.getloadavg()))
        si += fmt.format("  CPU Usage:",                 "{:4.1f} %"    .format(psutil.cpu_percent()))
        si += fmt.format("  Machine Total Memory:",      "{:5.1f} GiB = {:5.1f} GB = {:14,.0f} B".format(getMemoryTotal("GiB"), getMemoryTotal("GB"), getMemoryTotal("B")))
        si += fmt.format("  GeigerLog Used Memory:",     "{:5.1f} MiB = {:5.1f} MB = {:14,.0f} B".format(getMemoryUsed ("MiB"), getMemoryUsed ("MB"), getMemoryUsed ("B")))
        si += fmt.format("  Fibonacci Speed:",           "{:4.1f} ms"   .format(g.FibonacciSpeed))
        si += fmt.format("  Hash Speed:",                "{:4.1f} ms"   .format(g.HashSpeed))
        si += fmt.format("  GeigerLog Benchmark (GLBM):","GLBM = {:3.0f}".format(g.GLBenchmark))
    except Exception as e:
        exceptPrint(e, "psutil problem; is it missing?")
        si += fmt.format("\nSystem Info:",               "module psutil not available")

    # versions
    si += fmt.format("\nVersion status:",                "")
    for ver in g.versions:
        si += fmt.format( "  " + ver,                    g.versions[ver])

    # runtime
    si += fmt.format("\nRuntime flags:",              "")
    si += fmt.format("  Flag DEBUG:",                    str(g.debug))
    si += fmt.format("  Flag VERBOSE:",                  str(g.verbose))
    si += fmt.format("  Flag werbose:",                  str(g.werbose))
    si += fmt.format("  Flag KeepFF:",                   str(g.keepFF))
    si += fmt.format("  Flag Devel:",                    str(g.devel))
    si += fmt.format("  Flag Generic Testing:",          str(g.testing))
    si += fmt.format("  Flag Simulation GMC:",           str(g.GMC_simul))
    si += fmt.format("  Flag Simulation Gammascout:",    str(g.GS_simul))
    si += fmt.format("  Flag ForceLineWrapping:",        str(g.forcelw))
    si += fmt.format("  Flag Timing:",                   str(g.timing))

    si += fmt.format("\nAutostart settings:",              "")
    si += fmt.format("  File autoLogFile:",              str(g.autoLogFile))
    si += fmt.format("  Flag autoDevConnect:",           str(g.autoDevConnect))
    si += fmt.format("  Flag autoLogStart:",             str(g.autoLogStart))
    si += fmt.format("  Flag autoLogLoad:",              str(g.autoLogLoad))
    si += fmt.format("  Flag autoQuickStart:",           str(g.autoQuickStart))

    si += fmt.format("\nDirs and Files:",              "")
    si += fmt.format("  Dir  GeigerLog Program Directory:",   str(getPathToProgDir()))
    si += fmt.format("  Dir  GeigerLog Data Directory:",      str(g.dataDir))
    si += fmt.format("  Dir  GeigerLog Resource Directory:",  str(g.resDir))
    si += fmt.format("  Dir  GeigerLog Web Directory:",       str(g.webDir))
    si += fmt.format("  File GeigerLog Config File:",         str(g.configFile))
    si += fmt.format("  File GeigerLog Settings File:",       str(g.settingsFile))
    si += fmt.format("  File GeigerLog Manual:",              str(g.manual_filename))

    # GUI
    si += fmt.format("\nGUI:",                           "")
    si += fmt.format("  Monitor:",                       "")
    si += fmt.format("   Screen size - Hardware:",       "{}x{}".format(screen.width(), screen.height()))
    si += fmt.format("   Screen size - Available:",      "{}x{}, at position: x={}, y={}".format(screen_available.width(), screen_available.height(), screen_available.x(), screen_available.y()))
    si += fmt.format("   Current window size:",          "{}x{} including window frame (w/o frame: {}x{})".format(geom_frame.width(), geom_frame.height(), geom.width(), geom.height()))
    si += fmt.format("  Styles:",                        "")
    si += fmt.format("   Styles available on System:",   QStyleFactory.keys())
    si += fmt.format("   Active Style (internal name):", str(g.app.style().metaObject().className()))
    si += fmt.format("  Fonts:",                         "")
    si += fmt.format("   Active Font - Application:",    strFontInfo("", g.app.font()))
    si += fmt.format("   Active Font - Menubar:",        strFontInfo("", g.exgg.menubar.fontInfo()))
    si += fmt.format("   Active Font - NotePad:",        strFontInfo("", g.exgg.notePad.fontInfo()))
    si += fmt.format("   Active Font - LogPad:",         strFontInfo("", g.exgg.logPad.fontInfo()))

    # Devices
    si += "\n"
    si += fmt.format("Devices:",                         "Activated Connected Model")
    for i, DevName in enumerate(g.Devices):
        si += fmt.format("   {:2n} {}".format(i + 1, DevName), "{:9s} {:9s} {}".format(str(g.Devices[DevName][g.ACTIV]), str(g.Devices[DevName][g.CONN]), str(g.Devices[DevName][g.DNAME])))

    # Serial Ports
    si += fmt.format("\nUSB-to-Serial Port Settings:",   "")

    # GMC USB port
    si += fmt.format("  GMC Serial (USB) Port Settings:",  "")
    si += fmt.format("   Port:",                          str(g.GMC_usbport))
    si += fmt.format("   Baudrate:",                      str(g.GMC_baudrate))
    si += fmt.format("   Timeout: (Read)",                str(g.GMC_timeoutR))
    si += fmt.format("   Timeout: (Write)",               str(g.GMC_timeoutW))

    # I2C USB port
    si += fmt.format("  I2C Serial (USB) Port Settings:",  "")
    si += fmt.format("   Port:",                          str(g.I2Cusbport))
    si += fmt.format("   Baudrate:",                      str(g.I2Cbaudrate))
    si += fmt.format("   Timeout: (Read)",                str(g.I2CtimeoutR))
    si += fmt.format("   Timeout: (Write)",               str(g.I2CtimeoutW))

    # GS USB port
    si += fmt.format("  GS Serial (USB) Port Settings:",  "")
    si += fmt.format("   Port:",                          str(g.GSusbport))
    si += fmt.format("   Baudrate:",                      str(g.GSbaudrate))
    si += fmt.format("   Timeout: (Read)",                str(g.GStimeoutR))
    si += fmt.format("   Timeout: (Write)",               str(g.GStimeoutW))

    # worldmaps
    si += fmt.format("\nWorldmaps Settings:", "")
    si += fmt.format("  SSID",                            g.WiFiSSID)
    # si += fmt.format("  Password",                        g.WiFiPassword)
    si += fmt.format("  Password",                        "*********")
    si += fmt.format("  Website",                         g.gmcmapWebsite)
    si += fmt.format("  URL",                             g.gmcmapURL)
    si += fmt.format("  UserID",                          g.gmcmapUserID)
    si += fmt.format("  CounterID",                       g.gmcmapCounterID)
    si += fmt.format("  Period",                          g.GMC_WiFiPeriod)
    si += fmt.format("  WiFi",                            "ON" if g.GMC_WiFiSwitch == 1 else "OFF")


    if target == "window":
        # open a window with the info
        lsysinfo = QTextBrowser()                             # to hold the text; allows copy
        lsysinfo.setLineWrapMode(QTextEdit.WidgetWidth)
        lsysinfo.setText(si)

        dlg = QDialog()
        dlg.setWindowIcon(g.iconGeigerLog)
        dlg.setWindowTitle("Help - System Info")
        dlg.setFont(g.fontstd)
        dlg.setWindowModality(Qt.WindowModal)
        dlg.setMinimumWidth(1200)
        dlg.setMinimumHeight(690)

        bbox = QDialogButtonBox()
        bbox.setStandardButtons(QDialogButtonBox.Ok)
        bbox.accepted.connect(lambda: dlg.done(100))

        layoutV = QVBoxLayout(dlg)
        layoutV.addWidget(lsysinfo)
        layoutV.addWidget(bbox)

        dlg.exec()
    else:
        # return the info; to be printed in the terminal
        return si


def setNormalCursor():

    g.exgg.setNormalCursor()


def setBusyCursor():

    g.exgg.setBusyCursor()


def showStatusMessage(msg):

    g.exgg.showStatusMessage(msg)


def cleanupDevices(ctype):
    """ctype is 'before' or 'after'; so far only for GMC"""

    for DevName in g.Devices:
        if DevName == "GMC":
            from gdev_gmc import cleanupGMC
            cleanupGMC(ctype)
        else:
            pass                # so far no other device needs cleaning


def correctVariableCaps(devicevars):
    """correct any small caps in variables"""

    defname = "correctVariableCaps: "

    newt = ""
    for uppvname in devicevars.upper().split(","):
        a = uppvname.strip()
        if   a == "CPM"   :   newt += "CPM, "
        elif a == "CPS"   :   newt += "CPS, "
        elif a == "CPM1ST":   newt += "CPM1st, "
        elif a == "CPS1ST":   newt += "CPS1st, "
        elif a == "CPM2ND":   newt += "CPM2nd, "
        elif a == "CPS2ND":   newt += "CPS2nd, "
        elif a == "CPM3RD":   newt += "CPM3rd, "
        elif a == "CPS3RD":   newt += "CPS3rd, "
        elif a == "TEMP"  :   newt += "Temp, "
        elif a == "PRESS" :   newt += "Press, "
        elif a == "HUMID" :   newt += "Humid, "
        elif a == "XTRA"  :   newt += "Xtra, "
        elif a == "NONE"  :   newt += "None, "      # oh, oh
        else:                 pass                  # if it does not fit, ignore it
        # rdprint(defname + "a: ", a, "newt: ", newt)

    newt = newt[:-2]    # remove ", " at end

    # on wrong entries or empty entries newt will be empty
    if newt == "": newt = "auto"

    return newt


def setLoggableVariables(device, DeviceVariables):
    """set the loggable variables as list, making sure there is no whitespace, proper order, and no duplication
    device:             like: 'GMC'                   a Python string
    DeviceVariables:    like: 'CPM1st, CPS1st'        a Python string
    """

    defname = "setLoggableVariables: "
    # rdprint(defname, "Input DeviceVariables: ", DeviceVariables)

    g.Devices[device][g.VNAMES] = []

    if DeviceVariables is None or DeviceVariables == "":
        # this should never happen; should be caught in config
        rdprint(defname, "Unexpected Setting: No Variables are defined for device '{}'".format(device))
        NewDevVars = ""

    else:
        # Split vars into list, ...
        DevVars = DeviceVariables.split(",")

        # ..., clean up by removing any white space
        for i in range(len(DevVars)):   DevVars[i] = DevVars[i].strip()

        # put vnames into correct order, but only if vname is present in reference
        for vname in g.VarsCopy:
            if vname in DevVars: g.Devices[device][g.VNAMES].append(vname)

        NewDevVars = ", ".join(g.Devices[device][g.VNAMES])

        dprint(defname, "Device: '{}'   Variables: '{}'  --> '{}'".format(device, g.Devices[device][g.VNAMES], NewDevVars))

    return NewDevVars


def getTubeSensitivities(DeviceVariables):
    """get the sensitivity for the device's tube according to the defined variables"""

    defname = "getTubeSensitivities: "
    # rdprint(defname, "g.Sensitivity: {}".format(g.Sensitivity))

    if DeviceVariables is None: return  ""  # could be None if user enters wrong values

    TLTitle  = "Applicable Tube Sensitivity:\n"
    TubeList = ""
    devvar   = DeviceVariables.split(",")
    CPX      = [False] * 4
    for a in devvar:
        # otherwise there would be a printout of both CPM* and CPS* although it is the same tube
        a = a.strip()
        if   a == "CPM"    or a == "CPS" :      CPX[0] = True
        elif a == "CPM1st" or a == "CPS1st":    CPX[1] = True
        elif a == "CPM2nd" or a == "CPS2nd":    CPX[2] = True
        elif a == "CPM3rd" or a == "CPS3rd":    CPX[3] = True

    ttmplt     = "   {:27s}{} CPM / (µSv/h)\n"
    if CPX[0]: TubeList += ttmplt.format("CPM / CPS:",       g.Sensitivity[0])
    if CPX[1]: TubeList += ttmplt.format("CPM1st / CPS1st:", g.Sensitivity[1])
    if CPX[2]: TubeList += ttmplt.format("CPM2nd / CPS2nd:", g.Sensitivity[2])
    if CPX[3]: TubeList += ttmplt.format("CPM3rd / CPS3rd:", g.Sensitivity[3])

    if TubeList == "": TubeList = "   No Tube-supporting Variables defined\n"
    TubeList = TLTitle + TubeList

    cdprint(defname, "Tube 1...4: ",        g.Sensitivity)
    cdprint(defname, "DeviceVariables: ",   DeviceVariables)
    cdprint(defname, "TubeList: \n",        TubeList)

    return TubeList


def getLoggedValuesHeader():
    """get header for logged values"""

    # header is:
    # ....... ... .......  CPM       CPS       CPM1st    CPS1st    CPM2nd    CPS2nd    CPM3rd    CPS3rd    Temp      Press     Humid     Xtra
    text = ("{:<33s}   ".format("." * 33))[:38]
    for a in g.VarsCopy: text += "{:<10s}".format(a)

    return text


def vprintLoggedValues(rfncname, varlist, alldata, duration=None, forceprint=False):
    """vprint formatted logged values for a SINGLE device"""

    # print like: (1st line from getLoggedValuesHeader())
    # Cycle #318 ............ Dur[ms]   CPM       CPS       CPM1st    CPS1st    CPM2nd    CPS2nd    CPM3rd    CPS3rd    Temp      Press     Humid     Xtra
    # getValuesGMC:           176.00    4.00      176.00    4.00      0.00      0.00      -         -         -         -         -         -         -
    # getValuesAudio:         -         -         -         -         -         -         -         0.00      0.00      -         -         -         -

    defname = "vprintLoggedValues: "

    # text = "{:<22s}".format(rfncname)
    # if duration is not None: text += "{:8.3f} ms   ".format(duration)
    # else:                    text += "{:<8s}      " .format(" --- ")

    text = "{:<25s}".format(rfncname)
    if duration is not None: text += "{:8.2f}   ".format(duration)
    else:                    text += "{:<8s}      " .format(" --- ")

    for vname in g.VarsCopy:
        try:
            if vname in alldata:
                # rdprint(defname, "vname: '{:<6s}'  alldata: {}".format(vname, alldata))
                text += "{:<10.3f}".format(alldata[vname])
            else:
                text += "{:<10s}".format("-")
        except Exception as e:
            exceptPrint(e, defname)
            text += "{:<10s}".format("X")

    vprint(text, TDEFAULT, forceverbose=forceprint)


def getDeltaTimeMessage(deltatime, deviceDateTime):
    """determines difference between times of computer and device and gives message"""

    DTM  = ""
    dtxt = ""
    dtfd = "{:30s}".format("DateTime Device:")
    dtfg = "{:30s}".format("DateTime Computer:")

    if   np.isnan(deltatime):    dtxt += "Device clock cannot be read"                                           # clock defect?
    elif abs(deltatime) <= 1:    dtxt += "Device clock is same as computer clock within 1 sec"                   # uncertainty 1 sec
    elif deltatime >= +1:        dtxt += "Device is slower than computer by {:0.1f} sec".format(deltatime)       # delta positiv
    elif deltatime <= -1:        dtxt += "Device is faster than computer by {:0.1f} sec".format(abs(deltatime))  # delta negativ

    if   np.isnan(deltatime):
        # no clock
        DTM += "<red>" + dtfd + dtxt + "\n"

    elif abs(deltatime) > 5:
        # big difference
        DTM += dtfg + str(longstime()) + "\n"               # new line, not in red
        DTM += "<red>" +dtfd + str(deviceDateTime) + "\n"   # in red
        DTM += "<red>" + " "*30 + dtxt + "\n"               # in red

    else:
        # all ok
        DTM += dtfg + str(longstime()) + "\n"               # new line, not in red
        DTM += dtfd + str(deviceDateTime) + "\n"
        DTM += " " * 30 + dtxt + "\n"

    return DTM


def ping(host):
    """
    Returns (True, Time=...) if host responds to a ping request
    (False, Time not found) otherwise.
    Remember that a host may not respond to a ping (ICMP) request
    even if the host name is valid!
    """

    defname = "ping: "

    # Option for the number of packets as a function of operating system
    param = '-n' if platform.system().lower()=='windows' else '-c'

    command     = ['ping', param, '1', host]    # Building the command. Ex: "ping -c 1 google.com"
    popen       = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    popencomm   = popen.communicate()
    psuccess    = (popen.returncode == 0)       # MUST come after communicate() !
    popencout   = popencomm[0].decode("utf-8")  # use stdout
    popencerr   = popencomm[1].decode("utf-8")  # use stderr
    ptime       = "Name or service not known"
    for a in popencout.split("\n"):
        if "time=" in a: ptime = a[a.find("time=") + 5:]
        rdprint(defname, "ptime: ", ptime)

    vprint("Ping stdout: '{}'".format(popencout.replace("\n", "")))
    vprint("Ping stderr: '{}'".format(popencerr.replace("\n", "")))

    return psuccess, ptime


def fixGarbledAudio(quiet=False):
    """On Linux only, but NOT on Raspi: fix garbled audio sound"""

    # Linux   with garbled sound and message in the terminal: "ALSA lib pcm.c:7963:(snd_pcm_recover) underrun occurred"
    #         execute 'pulseaudio -k' as regular user (not sudo!). This should solve it

    defname = "fixGarbledAudio: "

    response = header("Fix Garbled Audio")  + "\n"

    if not "LINUX" in platform.platform().upper():
        response += defname + "Applicable only under Linux\n"
        dprint("{:28s}: {}".format("fixGarbledAudio", "Not supported on this computer"))
    else:
        if g.RaspiVersion != 5:
            try:
                command     = ["pulseaudio", "-k"]
                popen       = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                popencomm   = popen.communicate()
                psuccess    = (popen.returncode == 0)       # MUST come after communicate() !
                popencout   = popencomm[0].decode("utf-8")  # use stdout
                popencerr   = popencomm[1].decode("utf-8")  # use stderr

                if psuccess: msg = "Successfully executed: 'pulseaudio -k'"
                else:        msg = "FAILURE to execute 'pulseaudio -k' {}".format(popencerr)
                response  += msg + "\n"

                dprint("{:28s}: {}".format("fixGarbledAudio", msg))

            except Exception as e:
                msg = "FAILURE: Exception when trying to fix garbled audio with 'subprocess.call(pulseaudio -k)'"
                exceptPrint(e, defname + msg)
                response += "<red>" + msg + "\n"
        else:
            dprint("{:28s}: {}".format("fixGarbledAudio", "Not supported on this computer"))

    if not quiet: # when called as menu command
        for r in response.split("\n"):  fprint(r)


def getTimeCourseInLimits(varname, DeltaT):
    """get the (time, value) pairs for the last DeltaT minutes for variable varname"""

    defname = "getTimeCourseInLimits: "
    # edprint(defname + "varname: ", varname)

    dummy   = (np.array([g.NAN]), np.array([g.NAN]), np.float64(g.NAN))

    try:
        DBData = g.logDBData

        if np.all(DBData) is None : return dummy  # no database

        # NOTE: (see gup_plot.py for explanation of correction)
        # TimeBaseCorrection  = mpld.date2num(np.datetime64('0000-12-31'))      # = -719163.0
        #print(defname + "TimeBaseCorrection: ", TimeBaseCorrection)
        logTime             = DBData[:,0] + g.MPLDTIMECORRECTION                # time data of total file

        if len(logTime) == 0:
            return dummy
        else:
            DeltaT_Days = DeltaT / 60 / 24                                      # DeltaT in minutes => days

            plotTimeDelta = (logTime[-1] - logTime[0]) * 24 * 60                # Delta in min
            if plotTimeDelta > DeltaT:  plotTimeDelta = DeltaT

            # split multi-dim np.array into 12 single-dim np.arrays like log["CPM"] = [<var data>]
            log = {}
            for i, vname in enumerate(g.VarsCopy):
                log[vname] = DBData[:, i + 1]
                # print("{}: log[{}]: {}".format(i, vname, log[vname]))

            # confine limits
            Xleft  = max(logTime.max() - DeltaT_Days, logTime.min())

            # find the record, where the left time limit applies
            recmin = np.where(logTime >= Xleft )[0][0]
            # print("recmin: ", recmin)

            # slice the array
            vardata  = log[varname] [recmin : ]
            timedata = logTime      [recmin : ]
            # print(vardata)

            varmask  = np.isfinite(vardata)         # mask for nan values
            vardata  = vardata[varmask]             # remove the nan values
            timedata = timedata[varmask]            # remove the nan values

            return (timedata, vardata, plotTimeDelta)

    except Exception as e:
        exceptPrint(e, defname)



def getGeigerLogIP():
    """get the IP of the computer running GeigerLog"""

    defname = "getGeigerLogIP: "

    # st = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        st = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        st.connect(('8.8.8.8', 80))
        IP = st.getsockname()[0]
    except Exception as e:
        IP = '127.0.0.1'
        srcinfo = "Bad socket connect, IP set to:" + IP
        exceptPrint(defname + str(e), srcinfo)
    finally:
        st.close()

    return IP


def isValidIP(ipaddr):
    """check if ipaddr is a valid IP addr"""

    # works only with numeric addresses, not domain name addresses!
    try:
        socket.inet_aton(ipaddr)
        # legal
        return True
    except socket.error:
        # Not legal
        return False


def is_ipv4(string):
    import ipaddress
    try:
        ipaddress.IPv4Network(string)
        return True
    except ValueError:
        return False


# is a socket open or not?
        # import socket
        # location = (GeigerLogIP, MonServerPort)
        # a_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # result_of_check = a_socket.connect_ex(location)
        # if result_of_check == 0:
        #     print("mid: Port is open")
        #     a_socket.close()
        #     # a_socket.shutdown(socket.SHUT_RDWR)
        # else:
        #     print("mid Port is not open")
        #     a_socket.close()


def blendColor(color1, color2, f):

    return 10, 100, 200

    defname = "blendColor: "
    print(defname + "c1, c2, f:  ", color1, color2, f)

    r1 = int(color1[1 : 3], 16)
    g1 = int(color1[3 : 5], 16)
    b1 = int(color1[5 : 7], 16)

    r2 = int(color2[1 : 3], 16)
    g2 = int(color2[3 : 5], 16)
    b2 = int(color2[5 : 7], 16)

    r = r1 + (r2 - r1) * f
    g = g1 + (g2 - g1) * f
    b = b1 + (b2 - b1) * f
    return r, g, b


def getEasyDictPrint(mydict):

    return str(mydict).replace(" ", "").replace("'", "").replace(",", " ").replace("True", TYELLOW + "True " + TGREEN)


def printLoggable(msg = ""):
    if msg > "": gdprint(msg)
    gdprint("varsSetForLog     ",     getEasyDictPrint(g.varsSetForLog))
    gdprint("varsSetForHis     ",     getEasyDictPrint(g.varsSetForHis))
    gdprint("varsSetForCurrent ",     getEasyDictPrint(g.varsSetForCurrent))


def saveGraphToFile():
    """save the main graph to a (png) file"""

    figpath = g.currentDBPath
    if figpath is None:
        g.exgg.showStatusMessage("No data available")
        return

    while g.plotIsBusy:
        print("Wait", end=" ", flush=True)
        pass

    pngpath = figpath + ("_" + stime() + ".png").replace(" ", "_").replace(":", "_") # change blank and : to underscore (for Windows)
    plt.savefig(pngpath)
    fprint(header("Save Graph to File"))
    msg = "The current graph was saved to file: "
    fprint(msg + "\n", pngpath)
    vprint(msg       , pngpath)


def showResultCRC8():
    """Enter 2 bytes and print CRC8 checksum"""

    defname = "showResultCRC8: "

    crcbytes, okPressed = QInputDialog.getText(None, "Show CRC8 Result","Enter 2 Byte values, separeted by comma\nlike: {}".format("123, 234"))
    if okPressed:
        fprint(header("CRC8 Result"))
        try:
            crcbytelist = crcbytes.split(",")
            if len(crcbytelist) >= 2:
                crcbyte0    = int(float(crcbytelist[0]))
                crcbyte1    = int(float(crcbytelist[1]))
                crctest     = (crcbyte0, crcbyte1)
                msg         = "Bytes: {}  =>  CRC8: {} ".format(crcbytes, getCRC8(crctest))
                fprint(msg)
                dprint(defname + msg)
            else:
                msg = "Please enter 2 Byte values, separated by comma; you entered: '{}'".format(crcbytes)
                efprint(msg)
                edprint(defname + msg)

        except Exception as e:
            exceptPrint(e, "showResultCRC8: " + crcbytes)


def getCRC8(data):
    """
    calculates 8-Bit checksum as defined by Sensirion
    data:   tuple of 2 bytes
    return: CRC8 of data
    """

    # Adapted from Sensirion code - must clip crc to 8 bit (uint8)
    # in depth: https://barrgroup.com/embedded-systems/how-to/crc-calculation-c-code
    # // Original Sensirion C code:
    # // Example:       CRC(0xBEEF) = 0x92  (dec:146)
    # // my examples:   CRC(0x0000) = 0x81  (dec:129)
    # //
    # #define CRC8_POLYNOMIAL 0x31
    # #define CRC8_INIT 0xFF

    # uint8_t sensirion_common_generate_crc(const uint8_t* data, uint16_t count) {
    #     uint16_t    current_byte;
    #     uint8_t     crc = CRC8_INIT;
    #     uint8_t     crc_bit;
    #     /* calculates 8-Bit checksum with given polynomial */
    #     for (current_byte = 0; current_byte < count; ++current_byte) {
    #         crc ^= (data[current_byte]);
    #         for (crc_bit = 8; crc_bit > 0; --crc_bit) {
    #             if (crc & 0x80)
    #                 crc = (crc << 1) ^ CRC8_POLYNOMIAL;
    #             else
    #                 crc = (crc << 1);
    #         }
    #     }
    #     return crc;
    # }

    CRC8_POLYNOMIAL = 0x31
    CRC8_INIT       = 0xFF

    count           = len(data)
    crc             = CRC8_INIT
    for dbyte in data:
        # print("dbyte: ", dbyte)
        crc = (crc ^ dbyte) & 0xFF                                  # limit to uint8
        for i in range(0, 8):
            if crc & 0x80:  crc = (crc << 1) ^ CRC8_POLYNOMIAL
            else:           crc = crc << 1
            crc = crc & 0xFF                                        # limit to uint8
            # print("i: ", i, ", crc: ", crc)

    return crc


def getPortList(symlinks=True):
    """
    print serial port info. Include symlinks or not
    return: list of ports
    """

    # Pyserial:
    # 'include_links (bool)' – include symlinks under /dev when they point to a serial port
    # symlinks=False: symlinks NOT shown, default
    # symlinks=True:  symlinks shown, like /dev/geiger
    # https://github.com/pyserial/pyserial/blob/master/documentation/tools.rst

    # listofports example:
    #       [<serial.tools.list_ports_linux.SysFS object at 0x7f55fe582080>,
    #        <serial.tools.list_ports_linux.SysFS object at 0x7f55fe5826b0>]
    #
    # port attributes = ["name", "hwid", "device", "description", "serial_number",
    #                    "location", "manufacturer", "product", "interface", "vid", "pid"]

    # #
    # # on Linux
    # #
    # # GMC-300E+
    # /dev/ttyUSB0 - USB Serial
    #     p.name           : ttyUSB0
    #     p.hwid           : USB VID:PID=1A86:7523 LOCATION=3-1
    #     p.device         : /dev/ttyUSB0
    #     p.description    : USB Serial
    #     p.serial_number  : None
    #     p.location       : 3-1
    #     p.manufacturer   : None
    #     p.product        : USB Serial
    #     p.interface      : None
    #     p.vid            :  6790 (0x1A86)
    #     p.pid            : 29987 (0x7523)

    # # GMC-500+
    # /dev/ttyUSB1 - USB2.0-Serial
    #     p.name           : ttyUSB1
    #     p.hwid           : USB VID:PID=1A86:7523 LOCATION=3-1
    #     p.device         : /dev/ttyUSB1
    #     p.description    : USB2.0-Serial
    #     p.serial_number  : None
    #     p.location       : 3-1
    #     p.manufacturer   : None
    #     p.product        : USB2.0-Serial
    #     p.interface      : None
    #     p.vid            :  6790 (0x1A86)
    #     p.pid            : 29987 (0x7523)

    # # UBS-ISS
    # /dev/ttyACM0 - USB-ISS.
    #     p.name           : ttyACM0
    #     p.hwid           : USB VID:PID=04D8:FFEE SER=00027171 LOCATION=3-11:1.0
    #     p.device         : /dev/ttyACM0
    #     p.description    : USB-ISS.
    #     p.serial_number  : 00027171
    #     p.location       : 3-11:1.0
    #     p.manufacturer   : Devantech Ltd.
    #     p.product        : USB-ISS.
    #     p.interface      : None
    #     p.vid            :  1240 (0x04D8)
    #     p.pid            : 65518 (0xFFEE)

    # # ELV
    # /dev/ttyUSB0 - ELV USB-I2C-Interface - ELV USB-I2C-Interface
    #     p.name           : ttyUSB0
    #     p.hwid           : USB VID:PID=10C4:EA60 SER=TL4E6D5KBAHDFQF0 LOCATION=3-1
    #     p.device         : /dev/ttyUSB0
    #     p.description    : ELV USB-I2C-Interface - ELV USB-I2C-Interface
    #     p.serial_number  : TL4E6D5KBAHDFQF0
    #     p.location       : 3-1
    #     p.manufacturer   : Silicon Labs
    #     p.product        : ELV USB-I2C-Interface
    #     p.interface      : ELV USB-I2C-Interface
    #     p.vid            :  4292 (0x10C4)
    #     p.pid            : 60000 (0xEA60)

    # #
    # # on windows
    # #
    # # gmc-500+
    # COM3 - USB-SERIAL CH340 (COM3)
    #     p.name           : COM3
    #     p.hwid           : USB VID:PID=1A86:7523 SER= LOCATION=1-1.4
    #     p.device         : COM3
    #     p.description    : USB-SERIAL CH340 (COM3)
    #     p.serial_number  :
    #     p.location       : 1-1.4
    #     p.manufacturer   : wch.cn
    #     p.product        : None
    #     p.interface      : None
    #     p.vid            :  6790 (0x1A86)
    #     p.pid            : 29987 (0x7523)

    # # gmc-300E+
    # COM3 - USB-SERIAL CH340 (COM3)
    #     p.name           : COM3
    #     p.hwid           : USB VID:PID=1A86:7523 SER= LOCATION=1-1.4
    #     p.device         : COM3
    #     p.description    : USB-SERIAL CH340 (COM3)
    #     p.serial_number  :
    #     p.location       : 1-1.4
    #     p.manufacturer   : wch.cn
    #     p.product        : None
    #     p.interface      : None
    #     p.vid            :  6790 (0x1A86)
    #     p.pid            : 29987 (0x7523)

    # # ELV
    # COM7 - Silicon Labs CP210x USB to UART Bridge (COM7)
    #     p.name           : COM7
    #     p.hwid           : USB VID:PID=10C4:EA60 SER=TL4E6D5KBAHDFQF0 LOCATION=1-1.4
    #     p.device         : COM7
    #     p.description    : Silicon Labs CP210x USB to UART Bridge (COM7)
    #     p.serial_number  : TL4E6D5KBAHDFQF0
    #     p.location       : 1-1.4
    #     p.manufacturer   : Silicon Labs
    #     p.product        : None
    #     p.interface      : None
    #     p.vid            :  4292 (0x10C4)
    #     p.pid            : 60000 (0xEA60)

    # # USB-ISS
    # COM8 - Serielles USB-Gerät (COM8)
    #     p.name           : COM8
    #     p.hwid           : USB VID:PID=04D8:FFEE SER=00027171 LOCATION=1-1.2
    #     p.device         : COM8
    #     p.description    : Serielles USB-Gerät (COM8)
    #     p.serial_number  : 00027171
    #     p.location       : 1-1.2
    #     p.manufacturer   : Microsoft
    #     p.product        : None
    #     p.interface      : None
    #     p.vid            :  1240 (0x04D8)
    #     p.pid            : 65518 (0xFFEE)


    if symlinks:    msg = "(with symlinks)"
    else:           msg = "(without symlinks)"

    defname = "getPortList: "
    vprint(defname, msg)
    setIndent(1)

    portlist = []
    try:                   portlist = serial.tools.list_ports.comports(include_links=symlinks)
    except Exception as e: exceptPrint(e, defname + "portlist: {}".format(portlist))
    portlist.sort()                                                                                         # sorted by device
    # mdprint(defname, "portlist: ", portlist)

    pmsg = ""
    for p in portlist:
        # print("p: ", p)
        pmsg += "   " + str(p) + "\n"

    for p in pmsg.split("\n")[:-1]:
        vprint("Port: '{}'".format(p.strip()))

    setIndent(0)
    return portlist


def getSerialPortListingHTML():
    """get Port Listing in HTML Format and as list"""
    # NOTE: see: getPortList() for list of attributes

    defname = "getSerialPortListingHTML: "

    selection_ports    = []

    lp = getPortList(symlinks=True) # ist in gsup_utils.py

    hsp = "<b>Available Ports:</b><pre>"
    hsp += "\n{:15s} {:40s}  {:14s}   {:s}\n{}\n".format("Port",
                                                         "Name of USB-to-Serial Hardware",
                                                         "Linked to Port",
                                                         "VID :PID",
                                                         "-" * 84)

    if len(lp) == 0:
        errmessage = "FAILURE: No Available Ports found"
        dprint(defname, errmessage, debug=True)
        hsp += "<span style='color:red;'>" + errmessage + "\nIs any device connected? Check cable and plugs! Re-run in a few seconds.</span>" + "\n\n\n"
    else:
        for p in lp:
            #~print("\np: ", p)
            try:
                link = "(Not linked)"
                if hasattr(p, "hwid") and "LINK=" in p.hwid:
                    link1 = p.hwid.find("LINK=")
                    link2 = p.hwid.find("LINK=", link1 + 5)
                    #~print("device:", p.device, ",   hwid:", p.hwid)
                    #~print("link1: ", link1, ", link2: ", link2)
                    if link2 > 0:   link = p.hwid[link1 + 5 : link2]
                    else:           link = p.hwid[link1 + 5 : ]

                p_device        = getattr(p, "device",      "None")
                p_description   = getattr(p, "description", "None")
                dprint(defname, "p_description: '{}'  len:{}".format(p_description, len(p_description)))
                if len(p_description) > 40: p_description = p_description[:37].strip() + "..." # do not show complete length

                p_vid           = getattr(p, "vid",         0)
                if p_vid is None:   strp_vid = "None"
                else:               strp_vid = "{:04X}".format(p_vid)

                p_pid           = getattr(p, "pid",         0)
                if p_pid is None:   strp_pid = "None"
                else:               strp_pid = "{:04X}".format(p_pid)

                if p_device != "None":
                    selection_ports.append(p.device)
                    hsp += "{:15s} {:40s}  {:14s}   {}:{}\n".format(p_device, p_description, link, strp_vid, strp_pid)

            except Exception as e:
                dprint(defname + "Exception: {}  list_port: {}".format(e, p))

    hsp += "</pre>"

    # rdprint(defname, selection_ports)

    return (hsp, selection_ports)


def showPortDetails():
    """Full Details on USB Ports shown in Message Box"""

    defname = "showPortDetails: "

    portlist = getPortList(symlinks=True)                   # portlist is object; not human readable
    # rdprint(defname, "len(portlist): ", len(portlist))    # gives correct length

    pmsg = "\n"
    if len(portlist) > 0:
        # complete list of attributes for serial.tools.list_ports.comports()
        lpAttribs = ["device", "name", "hwid", "description", "serial_number", "location", "manufacturer", "product", "interface", "vid", "pid"]
        try:
            for p in portlist:
                pmsg += "Port: " + str(p) + "\n"
                for pA in lpAttribs:
                    if pA == "vid" or pA == "pid":
                        x = getattr(p, pA, 0)
                        if x is None:   pmsg += "   {:16s} : None\n".format(pA)
                        else:           pmsg += "   {:16s} : {:5d} (0x{:04X})\n".format(pA, x, x)
                    else:
                        pmsg += "   {:16s} : {}\n".format(pA, getattr(p, pA, "None"))
                pmsg += "\n"

        except Exception as e:
            exceptPrint(e, defname + "portlist: {}".format(portlist))
    else:
        pmsg += "Port: None found\n"

    pmsg += "\n"
    vprint(defname, "\n{}".format(pmsg))

    msg = QMessageBox()
    msg.setWindowIcon(g.exgg.iconGeigerLog)
    msg.setWindowTitle("Port Details")
    msg.setFont(g.exgg.fontstd)   # required!!! must set to get plain text, not HTML
    msg.setText(pmsg)

    msg.setStandardButtons(QMessageBox.Ok)
    msg.setDefaultButton(QMessageBox.Ok)
    msg.setEscapeButton(QMessageBox.Ok)
    msg.setWindowModality(Qt.WindowModal)
    msg.setStyleSheet("QLabel{min-width:800px; font-size:10pt;}")

    msg.exec()


def setDeviceSerialPort(DevName, USBport):
    """sets the GMC Device Serial Port and its Baud rate"""

    defname = "setDeviceSerialPort: "

    dprint(defname)
    setIndent(1)

    hsp1, selection_ports = getSerialPortListingHTML()

    # pushbutton help
    PortDetailsButton = QPushButton("Port Details")
    PortDetailsButton.setToolTip ('Show all details on USB-to-Serial Ports')
    PortDetailsButton.clicked.connect(lambda: showPortDetails())

    # ComboBox Ports
    portCbBoxGMC = QComboBox()
    portCbBoxGMC.addItems(["auto"])
    portCbBoxGMC.addItems(selection_ports)
    portCbBoxGMC.setToolTip("Select the USB-to-Serial port for device '{}'".format(DevName))
    portCbBoxGMC.setMaximumWidth(200)

    if portCbBoxGMC.findText(USBport) == -1:    portCbBoxGMC.setCurrentIndex(0)
    else:                                       portCbBoxGMC.setCurrentIndex(portCbBoxGMC.findText(USBport))

    # hsp1label: Ports Listing Text
    hsp1label = QLabel()
    hsp1label.setText(hsp1)
    hsp1label.setWordWrap(True)

    # hsp2label
    hsp2  = "<p><br>Select the Serial (USB) port for your device. \
                GeigerLog's current settings are pre-selected <b>if available</b>.<br>"
    hsp2label = QLabel()
    hsp2label.setText(hsp2)
    hsp2label.setWordWrap(True)

    # H-Layout
    cblayoutGMC = QHBoxLayout()
    cblayoutGMC.addWidget(hsp2label)
    cblayoutGMC.addWidget(portCbBoxGMC)
    cblayoutGMC.addWidget(PortDetailsButton)


    # hsp3label
    hsp3text = "<p>After pressing OK all of GeigerLog's devices will become disconnected.\
                (Re-)connect and (re-)start logging after all port settings are completed.\
                <p>Press Cancel to close without making any changes. "
    hsp3label = QLabel()
    hsp3label.setText(hsp3text)
    hsp3label.setWordWrap(True)

    # Dialog Box
    title = "Set Serial Port of Device '{}'".format(DevName)
    d = QDialog()
    d.setWindowIcon(g.exgg.iconGeigerLog)
    d.setWindowTitle(title)
    d.setWindowModality(Qt.WindowModal)

    # Button Box
    bbox = QDialogButtonBox()
    bbox.setStandardButtons(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)   # set Ok + Cancel button
    bbox.accepted       .connect(lambda: d.done(1))     # ok
    bbox.rejected       .connect(lambda: d.done(0))     # cancel, same for ESC, close window

    # dialog layout
    layoutV = QVBoxLayout(d)
    layoutV.addWidget(hsp1label)
    layoutV.addLayout(cblayoutGMC)
    layoutV.addWidget(hsp3label)
    layoutV.addWidget(bbox)

    retval = d.exec()               # returns 1 for Ok, 0 for Cancel, ESC, window close
    # print("---retval=",retval)

    if retval == 0:
        vprint(defname + "cancelled by user")
        USBport = None

    else:
        g.exgg.switchAllDeviceConnections(new_connection = "OFF")

        fprint(header(title))

        USBport = portCbBoxGMC.currentText()
        msg     = f"New Serial Port: {USBport}"
        dprint(defname, msg)
        fprint(msg)
        fprint("<br><blue><b>INFO:</b> All devices have been disconnected. Reconnect if needed.")

        if   DevName == "GMC":          g.GMC_usbport           = USBport
        elif DevName == "I2C":          g.I2Cusbport            = USBport
        elif DevName == "GammaScout":   g.GSusbport             = USBport
        elif DevName == "SerialPulse":  g.SerialPulseUsbport    = USBport
        elif DevName == "RadPro":       g.RadProPort            = USBport

    setIndent(0)


def showPortSettings():
    """Show Settings of Serial Ports for all activated devices using Serial port"""

    fprint(header("Device Port Settings"))
    fprint("Port configuration of all activated devices using a serial port:")

    devtmplt   = "Device: {}  Port: {:15s}  Baudrate: {}\n"
    devsetting = ""
    devcount   = 0
    for devname in ["GMC", "I2C", "GammaScout", "SerialPulse"]:
        if g.Devices[devname][g.ACTIV]:
            devcount += 1
            if   devname == "GMC":         devsetting += devtmplt.format(devname, g.GMC_usbport,        g.GMC_baudrate)
            elif devname == "I2C":         devsetting += devtmplt.format(devname, g.I2Cusbport,         g.I2Cbaudrate)
            elif devname == "GammaScout":  devsetting += devtmplt.format(devname, g.GSusbport,          g.GSbaudrate)
            elif devname == "SerialPulse": devsetting += devtmplt.format(devname, g.SerialPulseUsbport, g.SerialPulseBaudrate)

    if devcount == 0: devsetting = "There are no devices using a Serial Port"
    fprint(devsetting)
    rdprint(devsetting)

    hsp, selection_ports = getSerialPortListingHTML()
    fprint("")
    fprint(hsp.replace("pre", ""))      # remove the <pre></pre> to avoid extra blank lines


def initLogThread():
    """initialize and start the Log Thread"""

    defname = "initLogThread: "
    dprint(defname)
    setIndent(1)

    g.LogThreadRunFlag      = True

    g.LogThread             = threading.Thread(target = LogThreadTarget)
    g.LogThread.daemon      = True
    g.LogThread.start()

    dprint("LogThread.daemon:      ", g.LogThread.daemon)
    dprint("LogThread.is_alive:    ", g.LogThread.is_alive())

    setIndent(0)


def terminateLogThread():
    """end the Log thread"""

    defname = "terminateLogThread: "
    dprint(defname)
    setIndent(1)

    start = time.time()

    g.LogThreadRunFlag = False
    g.LogThread.join()
    dprint("LogThread alive?    ", g.LogThread.is_alive())
    while g.LogThread.is_alive() and time.time() < start + 5:
        dprint("LogThread alive?    ", g.LogThread.is_alive())
        time.sleep(0.01)

    dprint(defname + "done ({:0.3f} ms)".format(1000 * (time.time() - start)))

    setIndent(0)

#ttt
def LogThreadTarget():
    """The Target function for the logging thread"""

    defname  = "LogThreadTarget: "

    # sleep is now in function 'startLogging()'
    # time.sleep(0.01)                                    # skip first 10 msec to let initLogThread printouts finish


    g.nexttime     = g.LogThreadStartTime
    g.nextnexttime = g.nexttime + g.LogCycle
    g.lasttime     = g.nexttime - g.LogCycle
    # g.logging       = True          # set early, to allow threads to get data
    while g.LogThreadRunFlag:
        if time.time() >= g.nexttime:                   # start right away

            g.nexttime     += g.LogCycle
            g.nextnexttime  = g.nexttime + g.LogCycle
            runLogCycle()
            g.lasttime     += g.LogCycle

        time.sleep(0.005)                               # gives a 5 ms precision of calling the runLogCycle
                                                        # better not asking for too much?!


def getTimeJulian():
    """get NOW in Juliantime"""

    return g.JULIANUNIXZERO + (time.time() + g.TimeZoneOffset) / 86400


#rlc
def runLogCycle():
    """run 1 cycle of fetch, save, request flags setting"""

    defname   = "runLogCycle: "
    msgfmt    = "{:<25s} {:7.2f} "
    getDur    = g.NAN
    totalDur  = g.NAN

    vprint("")  # print empty line
    vprint("{:<13s}#{:<10d}     Dur[ms]   {}  {} ".format(defname, g.LogReadings, "saving to: ", g.logDBPath))
    setIndent(1)


# print the total checkcycle consumed time
    msg   = msgfmt.format("Last CheckCycle Active:", g.durCheckActive) + "  count:{:<3.0f}".format(g.countCheckActive)
    cdlogprint(msg, duration=g.durCheckActive, force=True)

    sumai = g.countCheckIdle + g.countCheckActive
    if sumai > 0:
        p_sumA = g.countCheckActive / sumai
        p_sumI = g.countCheckIdle   / sumai
    else:
        p_sumA = g.NAN
        p_sumI = g.NAN

    msg   = msgfmt.format("Last CheckCycle Idle:", g.durCheckIdle) + "  count:{:<3.0f}  Count Total A+I:{}  A:{:0.0%}  I:{:0.0%}".format(g.countCheckIdle, sumai, p_sumA, p_sumI)
    cdlogprint(msg, duration=g.durCheckIdle, force=True)

    g.durCheckActive   = 0
    g.countCheckActive = 0
    g.durCheckIdle     = 0
    g.countCheckIdle   = 0


#
# begin new cycle
#

# update index (=LogReadings)
    g.LogReadings += 1


# set the timestamps for this record
    g.LogCycleStart = time.time()
    timeLogpad      = longstime()[11:]     # LogPad uses no date, only time with 1 ms:  '2018-07-14 12:00:52.342' --> '12:00:52.342'
    timeJulian      = getTimeJulian()


# fetch the data from all devices
    # Example logvalues:
    # {'CPM': 18110.0, 'CPS': 297.0, 'CPM1st': nan, 'CPS1st': nan, 'CPM2nd': nan, 'CPS2nd': nan, 'CPM3rd': nan, 'CPS3rd': nan,
    #  'Temp': 295, 'Press': 293.8, 'Humid': 277, 'Xtra': 18}
    getstart  = time.time()
    # header is:
    # Cycle #318 .............. Dur[ms]   CPM       CPS       CPM1st    CPS1st    CPM2nd    CPS2nd    CPM3rd    CPS3rd    Temp      Press     Humid     Xtra
    vprint(getLoggedValuesHeader())
    logValues = g.exgg.getAllLogValues()
    getDur    = 1000 * (time.time() - getstart)
    vprint(msgfmt.format("getValues Total:",  getDur))
    # rdprint(defname, "get logValues: ", logValues)


# update Database and Memory queues
    # If all Log values are NAN, then do nothing except posting "No data" to LogPad.
    # If at least one value is non-NAN, then append Log values to database queue,
    # and update those "lastLogValues" with new logValues where new value is not NAN
    nanOnly = True
    for vname in g.VarsCopy:
        if not np.isnan(logValues[vname]):
            nanOnly                = False
            lvvname                = logValues[vname]
            g.lastLogValues[vname] = lvvname
            g.AlarmQueues[vname]     .append(lvvname)

    if not nanOnly:
        # at least one value is not nan
        saveLogValuesToDBQueue    (timeJulian, logValues)   # update database
        saveLogValuesToMemoryQueue(timeJulian, logValues)   # update Memory queue (takes under 1 ms)


# update LogPad queue
    g.LogPadQueue.append((timeLogpad, logValues))


# update the display - Selected Variable and Last Values Window
    g.needDisplayUpdate = True


# total duration
    totalDur = 1000 * (time.time() -  g.LogCycleStart)            # in millisec
    vprint(msgfmt.format("runLogCycle Total:",  totalDur))


# check for log cycletime overrun
    # rdprint(defname, "totalDur: ", totalDur)
    # rdprint(defname, "g.LogCycle: ", g.LogCycle)
    if totalDur > g.LogCycle * 1000:
        msg  = f"LogCycle OVERRUN - Duration:{totalDur / 1000:0.3f} sec  LogCycle:{g.LogCycle} sec"
        QueuePrint(stime() + " " + msg)
        dprint(BOLDRED + msg + TDEFAULT)


# done
    setIndent(0)

#rlc end runLogCycle() ##############################


def saveLogValuesToDBQueue(timeJulian, logValues):
    """Save data to database"""

    defname = "saveLogValuesToDBQueue: "

    datalist     = [None] * (g.datacolsDefault + 1)        # (13 + 1) x None; + 1 wg index
    datalist[0]  = g.LogReadings                           # store the index
    datalist[1]  = timeJulian                              # time stamp

    for i, vname in enumerate(g.VarsCopy):
        datalist[2 + i] = logValues[vname]                 # data into datalist[2 + following]

    # append to Queue
    g.SaveLogValuesQueue.append(datalist)


def saveLogValuesToMemoryQueue(timeJulian, logValues):
    """Save data to memory queue for later saving to memory"""

    defname = "saveLogValuesToMemoryQueue: "

    datalist = [
                                               # no index
                timeJulian - g.JULIAN111,      # time is set to matplotlib time
                logValues["CPM"],
                logValues["CPS"],
                logValues["CPM1st"],
                logValues["CPS1st"],
                logValues["CPM2nd"],
                logValues["CPS2nd"],
                logValues["CPM3rd"],
                logValues["CPS3rd"],
                logValues["Temp"],
                logValues["Press"],
                logValues["Humid"],
                logValues["Xtra"],
                ]

    # append to memory data queue
    g.MemDataQueue.append(datalist)


# is not used
def get_julian_datetime(date):
    """
    Convert a datetime object into julian float.
    Args:
        date: datetime-object of date in question

    Returns: float - Julian calculated datetime.
    Raises:
        TypeError : Incorrect parameter type
        ValueError: Date out of range of equation
    """

    # from: https://stackoverflow.com/questions/31142181/calculating-julian-date-in-python/52431241#52431241

    import math

    # usage:
    # mydatetime = dt.datetime.now()
    # timeJulian, timetag = get_julian_datetime(mydatetime), mydatetime.strftime("%Y-%m-%d %H:%M:%S")
    # print("timeJulian, timetag: ", timeJulian, timetag)

    # Ensure correct format
    if not isinstance(date, dt.datetime):  raise TypeError('Invalid type for parameter "date" - expecting datetime')
    elif date.year < 1801 or date.year > 2099:   raise ValueError('DateTime must be between year 1801 and 2099')

    # Perform the calculation
    julian_datetime = 367 * date.year - int((7 * (date.year + int((date.month + 9) / 12.0))) / 4.0) + int(
        (275 * date.month) / 9.0) + date.day + 1721013.5 + (
                          date.hour + date.minute / 60.0 + date.second / math.pow(60,2)) / 24.0 - 0.5 * math.copysign(
        1, 100 * date.year + date.month - 190002.5) + 0.5

    return julian_datetime


def printColorCodesToTerminal():

    #   TBLUE               = '\033[94m'            # blue (dark)
    #   BOLDRED             = '\033[91;1m'          # bold, red

    # 41 ... 47 (7x) und 100 ... 107 (8x) alles weisse Schrift auf Farbe
    for i in range(0, 108): # all the same plain white text AND black background from 108 onwards
        print("\033["+ str(i) + "m", end="")
        print("'\\033[{:n}m'      Der süße Björn macht ständig Ärger".format(i), TDEFAULT)

        # alle ';1m' sind heller, da bold
        print("\033["+ str(i) + ";1m", end="")
        print("'\\033[{:n};1m'    Der süße Björn macht ständig Ärger".format(i), TDEFAULT)


def clearTerminal():
    """clear the terminal"""

    # The name of the operating system dependent module imported. The following
    # names have currently been registered: 'posix', 'nt', 'java'.
    if "LINUX" in platform.platform().upper():
        # clear the terminal
        os.system("export TERM=xterm-256color")     # needed(?) to prep for clear
        os.system("clear")                          # clear terminal

    os.system('cls' if os.name == 'nt' else 'clear')
    # print("os.name: ", os.name) # os.name:  posix (on Linux)


def Fibonacci(n):
    """Calculate a Fibonacci number"""
    # https://realpython.com/fibonacci-sequence-python/

    if n in {0, 1}:  return n                   # Base case
    return Fibonacci(n - 1) + Fibonacci(n - 2)  # Recursive case


def cdlogprint(msg, duration=1E999, force=False, alarm=False):
    """print if duration > limit ms or or force or alarm. If flag g.GMC_testing save to special log"""

    limit = 0.5

    if duration >= limit or force or alarm:
        if not alarm:   cdprint(msg.replace(",", ""))
        else:           rdprint(msg.replace(",", ""))

    if g.GMC_testing: writeSpecialLog(msg)


def writeSpecialLog(specialmsg, clearflag=False):
    """Write a special msg to a special file but only on devel"""

    defname = "writeSpecialLog: "

    # path_speciallog = g.dataDir + "/GLspecial.log"
    path_speciallog = os.path.join(g.dataDir, "/GLspecial.log")

    if g.devel:
        # rdprint(defname, "clearflag: ", clearflag)
        if clearflag:
            if os.path.exists(path_speciallog): os.remove(path_speciallog)
        else:
            try:
                with open(path_speciallog, "at", encoding="UTF-8", errors='replace', buffering=-1) as f:
                    msg = "{} {}\n".format(longstime(), specialmsg)
                    f.write(msg)
            except Exception as e:
                exceptPrint(e, "EXCEPTION: " + defname + specialmsg)


def getNTPDateTime(NTPversion = 4):
    """Call NTP server and return offset in milli-seconds as reported by NTP"""

    # typical offset is in the order of 10 milli second (offset = +/- 0.010
    # latest NTP version is now: 4;     working versions are 2, 3, 4 (not 1!)

    # see my topic:  https://stackoverflow.com/questions/65549802/what-time-from-an-ntp-time-server-should-be-used-to-set-my-clock
    # quote: "As the offset is already given by the lib, so all you do is add(!, not subtract) this signed offset to your computer's time."
    #
    # https://www.ntppool.org/de/use.html
    # https://www.eecis.udel.edu/~mills/ntp/html/release.html
    # NTP document by IETF:       https://tools.ietf.org/html/rfc5905
    # see: page 23, Figure 7 for functions, and ff for details
    #
    # ntplib: def request(self, host, version=2, port='ntp', timeout=5):
    #
    #
    # Reference Timestamp:
    # Time when the system clock was last set or corrected, in NTP timestamp format.
    #
    # Origin Timestamp (org):
    # Time at the client when the request departed for the server, in NTP timestamp format.
    #
    # Receive Timestamp (rec):
    # Time at the server when the request arrived from the client, in NTP timestamp format.
    #
    # Transmit Timestamp (xmt):
    # Time at the server when the response left for the client, in NTP timestamp format.
    #
    # Destination Timestamp (dst):
    # Time at the client when the reply arrived from the server, in NTP timestamp format.

    # if not ntplib_available:
    #     edprint("Cannot call NTP Server as ntplib is not available!")
    #     return g.NAN


    # use only the generic server; it will search for nearest NTP server
    NTP_SERVERS = [
                    'pool.ntp.org',
                    # 'asia.pool.ntp.org',
                    # 'oceania.pool.ntp.org',
                    # 'north-america.pool.ntp.org',
                    # 'south-america.pool.ntp.org',
                    # 'europe.pool.ntp.org',
                    # 'de.pool.ntp.org',
                    # '0.de.pool.ntp.org',
                    # '1.de.pool.ntp.org',
                    # '2.de.pool.ntp.org',
                    # '3.de.pool.ntp.org',
                    # 'uk.pool.ntp.org',
                    # '0.uk.pool.ntp.org',
                  ]

    defname     = "getNTPDateTime: "
    wprint(defname)
    setIndent(1)

    orig   = recv = dest = offset = g.NAN
    for ntpserver in NTP_SERVERS:
        try:
            ntpclient = ntplib.NTPClient()
            response  = ntpclient.request(ntpserver, version=NTPversion, timeout=0.3)
        except Exception as e:
            msg = defname + "NTPversion:{} ".format(NTPversion)
            exceptPrint(e, msg)
        else:
            orig   = response.orig_time     # all times in seconds
            recv   = response.recv_time
            tx     = response.tx_time
            dest   = response.dest_time
            offset = response.offset

            ntps   = []
            ntps.append( ["orig"        , orig - orig]) # always zero
            ntps.append( ["recv"        , recv - orig])
            ntps.append( ["tx  "        , tx   - orig])
            ntps.append( ["dest"        , dest - orig])
            ntps.append( ["offset"      , offset])
            ntps.append( ["calc offset" , ((recv - orig) + (tx - dest)) / 2])

            # wprint for each server
            if g.werbose:
                for a in ntps:
                    wprint("NTP Version: {}  {:20s}  {:15s}  {:10.3f} ".format(NTPversion, ntpserver, a[0], a[1]))
                print("")

            break           # on first successful server

    setIndent(0)

    return (round(offset * 1000, 3), ntpserver)       # return offset in ms and first successful server


def fprintNTPDateTime():
    """prints the offset to NTPtime to the notepad"""

    defname = "fprintNTPDateTime: "
    dprint(defname)
    setIndent(1)

    offset, currentServer = getNTPDateTime()

    fprint(header("Network Time Protocol Check"))
    server = "Server '{}' ".format(currentServer)
    if np.isnan(offset): msg = server, "did not respond"
    else:                msg = server, "offset: <b>{:+0.1f} ms</b> - to be added to your computer's time ".format(offset)
    fprint(*msg)
    dprint(*msg)
    setIndent(0)


def getMemoryTotal(unit = "MB"):
    """Using psutil to determine total memory of machine"""

    # see: https://psutil.readthedocs.io/en/latest/index.html?highlight=used#psutil.Process.num_threads

    defname = "getMemoryTotal: "

    factor = getFactor(unit = unit)
    try:
        mem_total = psutil.virtual_memory().total / factor
    except Exception as e:
        exceptPrint(e, defname)
        mem_total = g.NAN

    return mem_total


def getMemoryUsed(unit = "MB"):
    """returning psutil's 'uss' as memory used by GeigerLog in MiB"""

    # GiB   = 2**30    # 1 Gibi Byte = 1 073 741 824 Byte   = 1024 Mebi Byte
    # MiB   = 2**20    # 1 Mebi Byte =     1 048 576 Byte   = 1024 Kibi Byte
    # KiB   = 2**10    # 1 Kibi Byte =         1 024 Byte

    # see: https://psutil.readthedocs.io/en/latest/index.html?highlight=used#psutil.Process.num_threads
    # mem_info_full:  uss (Linux, macOS, Windows): aka “Unique Set Size”, this is the memory which is
    # unique to a process and which would be freed if the process was terminated right now.
    #
    # Note:  uss is probably the most representative metric for determining how much memory is actually
    # being used by a process. It represents the amount of memory that would be freed if the process
    # was terminated right now.

    defname = "getMemoryUsed: "

    factor = getFactor(unit = unit)
    try:
        psuss               = psutil.Process().memory_full_info().uss
        mem_info_full_uss   = round(psuss / factor, 1)
    except Exception as e:
        exceptPrint(e, defname)
        mem_info_full_uss = g.NAN

    return mem_info_full_uss


def getFactor(unit = "MB"):
    """converts unit as string into numeric factor as return"""

    unit = unit.upper()

    if   unit == "GB":    factor = 1E9      # GB
    elif unit == "MB":    factor = 1E6      # MB
    elif unit == "KB":    factor = 1E3      # kB
    elif unit == "B":     factor = 1        #  B
    elif unit == "GIB":   factor = g.GiB    # GiB = 2**30
    elif unit == "MIB":   factor = g.MiB    # MiB = 2**20
    elif unit == "KIB":   factor = g.KiB    # Kib = 2**10
    else:
        unit   = "B"                        # B   = 2**0
        factor = 1

    return factor


def customformat(value, total, dec, thousand=True):
    """my universal format ???"""

    ####################
    def getF_Format(total, dec):
        if thousand:    myformat = f"{{:{total}_.{dec}f}}"  # --> "{:10,.3f}"   # with ',' as thousand-separator
        else:           myformat = f"{{:{total}.{dec}f}}"   # --> "{:10.3f}"    # without a thousand-separator
        return myformat

    def getMax(total, dec):
        maxval   = 10**(total - dec)                        # für 10 and 3 --> 10**(10 - 3) = 10 mio
        return maxval
    ####################

    defname = "customformat: "

    try:
        if np.isnan(value): return str(g.NAN)

        g_format = "{:0.2E}"

        # use g_format for abs < 0.1 but not zero
        if -0.1 < value < 0 or 0 < value < 0.1:       return (g_format.format(value)).strip()

        # make f_format
        rvalue  = np.round(value, dec)                             # round
        mysign  = "" if np.sign(rvalue) >= 0 else "-"           # sign
        arvalue = abs(rvalue)                                   # abs
        for idec in range(dec, -1, -1):
            # print("i:{} total/dec: {}/{}   value: {}".format(i, total, dec, value))
            if arvalue < getMax(total, idec):  return mysign + (getF_Format(total, idec).format(arvalue)).strip().replace("_", " ")

        # use g_format if too big for f_format
        return (g_format.format(value)).strip()

    except Exception as e:
        exceptPrint(e, defname)


# signal handling
def printSysInfo(a, b):
    """Print System Info to terminal"""
    print()
    print("a: ", a)
    print("b: ", b)
    if g.devel:
        rdprint("Show System Info")
        print(showSystemInfo(target = "terminal"))
    else:
        print("GeigerLog PID: ", os.getpid())
    rdprint("Done Showing System Info")


# signal handling
def getmeout(a, b):
    """Shutdown GeigerLog immediately"""

    print()
    print("Interruption with keyboard generated signal")
    sys.exit()


# def getCPU_ID():
#     """Get CPU name and CPU Vendor"""

#     def cpu_vendor(cpu):
#         _, b, c, d = cpu(0)
#         return struct.pack("III", b, d, c).decode("utf-8")

#     def cpu_name(cpu):
#         name = "".join((struct.pack("IIII", *cpu(0x80000000 + i)).decode("utf-8")
#                         for i in range(2, 5)))
#         return name.split('\x00', 1)[0]

#     cpu          = cpuid.CPUID()
#     g.CPU_Model  = cpu_name(cpu)     # --> : Intel(R) Core(TM) i7-4771 CPU @ 3.50GHz
#     g.CPU_Vendor = cpu_vendor(cpu)


def getCPU_Info():
    """Get the CPU Model, like:
        -- Intel(R) Core(TM) i7-4771 CPU @ 3.50GHz
        -- Raspberry Pi 4 Model B Rev 1.1
       Get the Hardware info, like:
        -- BCM2835 for Raspi 4 (kein Wert bei Raspi 5)

       Duration: 1.1 sec!
    """
    # based on module py-cpuinfo

    defname = "getCPU_Info: "
    cdprint(defname + "Using cpuinfo.get_cpu_info()")

    # all CPU info
    try:
        t0 = time.time()
        myCPUinfo   = cpuinfo.get_cpu_info()
        # rdprint(defname, "Duration: {:0.3f} ms".format(1000 * (time.time() - t0))) # duration=1.15 sec
        # this long duratiopn is due to a 1 sec sleep in code: https://github.com/workhorsy/py-cpuinfo/issues/205#issuecomment-1833653828
    except Exception as e:
        # exceptPrint(e, defname)
        vprint(defname, "Failure getting: CPUinfo")

    for key, ci in myCPUinfo.items():
        print("{:20s} : {}".format(key, ci))

    # # Model
    # try:
    #     g.CPU_Model  = myCPUinfo["brand_raw"]
    # except Exception as e:
    #     # exceptPrint(e, defname)
    #     vprint(defname, "Failure getting: CPUinfo['brand_raw']")

    # # Hardware
    # try:
    #     g.CPU_Hardware = myCPUinfo["hardware_raw"]
    # except Exception as e:
    #     # exceptPrint(e, defname)
    #     vprint(defname, "Failure getting: CPUinfo['hardware_raw']")


def getLinuxPROCINFO():
    """Read '/proc/cpuinfo'"""
    # --> NOT useable in Windows

    defname = "getLinuxPROCINFO: "

    if 'linux' in sys.platform:
        proc_cpuinfo = "Not readable"
        try:
            with open("/proc/cpuinfo") as f:
                proc_cpuinfo = f.read()
        except Exception as e:
            exceptPrint(e, defname)

        # cdprint(defname, "\n", proc_cpuinfo)
        cdprint(defname)
        print(proc_cpuinfo)

        # for cir in proc_cpuinfo.split("\n"):
        #     # print("cir: ", cir)
        #     if "hardware" in cir.lower():
        #         print(cir)
        #         g.CPU_Hardware = cir.split(":")[1].strip()
        #     else:
        #         print(".", end="")
        # print()

    else:
        dprint(defname, "Linux only - no data on Windows, Mac")


def getAllCPUInfo():
    """Call both CPU info functions"""

    getLinuxPROCINFO()
    getCPU_Info()


# https://stackoverflow.com/questions/4842448/getting-processor-information-in-python
# Here's a hackish bit of code that should consistently find the name of the processor on the three platforms
# that I have any reasonable experience.
def getCPU_Details():
    """Cross-platform CPU info"""

    defname = "getCPU_Details: "

    if platform.system() == "Windows":
        g.CPU_Model = platform.processor()                                              # like: Intel64 Family 6 Model 190 Stepping 0, GenuineIntel

    elif platform.system() == "Darwin":
        os.environ['PATH'] = os.environ['PATH'] + os.pathsep + '/usr/sbin'
        command ="sysctl -n machdep.cpu.brand_string"
        g.CPU_Model = subprocess.check_output(command).strip()                          # like: ???

    elif platform.system() == "Linux":
        # command  = "cat /proc/cpuinfo"
        # all_info = subprocess.check_output(command, shell=True).decode().strip()

        proc_cpuinfo = "Not readable"
        try:
            with open("/proc/cpuinfo") as f:
                proc_cpuinfo = f.read()
        except Exception as e:
            exceptPrint(e, defname)

        for line in proc_cpuinfo.split("\n"):
            # rdprint(defname, "line: ", line)
            if "model name" in line:                                                    # Linux Mint 21.2
                g.CPU_Model = re.sub( ".*model name.*:", "", line, 1).strip()           # like:  Intel(R) Core(TM) i7-4771 CPU @ 3.50GHz
                                                                                        #

            elif "Model" in line:                                                       # Linux on Raspi4
                g.CPU_Model = re.sub( ".*Model.*:", "", line, 1).strip()                # like: Raspberry Pi 4 Model B Rev 1.1

            elif "Hardware" in line:                                                    # Linux on Raspi4
                g.CPU_Hardware = re.sub( ".*Hardware.*:", "", line, 1).strip()          # BCM2835 for Raspi 4 (kein Wert bei Raspi 5)

            elif "vendor_id" in line:                                                   # Linux Mint 21.2
                g.CPU_Vendor = re.sub( ".*vendor_id.*:", "", line, 1).strip()           # like: GenuineIntel


    # all CPU info
    myCPUinfo   = cpuinfo.get_cpu_info()

    # Model
    try:
        g.CPU_BrandRaw  = myCPUinfo["brand_raw"]
    except Exception as e:
        # exceptPrint(e, defname)
        vprint(defname, "Failure getting: CPUinfo['brand_raw']")


def getCPMfromCPS(List60CPS):
    """get CPM from list of CPS"""
    # List60CPS MUST have length > 0!

    ### Option #1: make estimate of 60s cpm
    ### at 10 counts->StdDev= 32%; 20 counts->StdDev= 22%
    lenL6C = len(List60CPS)
    sumL6C = sum(List60CPS)
    if   lenL6C == 60:               cpm = sumL6C
    elif lenL6C > 5 and sumL6C > 20: cpm = round(sumL6C / lenL6C * 60, 0)
    else:                            cpm = g.NAN

    ### Option #2: make current cpm even if based on < 60 sec
    # cpm                                = sum(List60CPS)

    ### Option #3: make value only after 60 sec
    # if len(List60CPS) == 60:       cpm = sum(List60CPS)
    # else:                          cpm = g.NAN

    return cpm


def getVC850Voltage():
    """Query the Voltcraft VC850 DMM via RS232 Serial for a single Value"""

    defname  = "getVC850Voltage: "

    # setIndent(1)

    try:
        rstart   = time.time()
        with serial.Serial( port       = "/dev/ttyUSB0",
                            baudrate      = 2400,
                            timeout       = 3,
                            write_timeout = 1,
                            ) as RPser:

            try:
                RPser.reset_input_buffer()    # clear pipeline
                brec     = RPser.readline()                                         # waits for LF; timeoutR when no LF received, but download Hist takes > 2 sec, yet works?
            except Exception as e:
                exceptPrint(e, defname + f"FAILURE reading serial ")
                time.sleep(0.1)
                brec     = b""

            rdur = 1000 * (time.time() - rstart)                            # in ms

            if (len(brec) == 14) and (brec[5] == 0x20):
                try:
                    value = float( brec[0:5].decode("ascii") )

                    if   brec[6] == 0x31:       value /= 1000       # == 1
                    elif brec[6] == 0x32:       value /= 100        # == 2
                    elif brec[6] == 0x33:       value /= 10         # == 3
                    elif brec[6] == 0x34:       value /= 10         # == 4

                except:
                    value = g.PINF

                if   (brec[9] & 0x80) != 0:     prefix = "µ"
                elif (brec[9] & 0x40) != 0:     prefix = "m"
                elif (brec[9] & 0x20) != 0:     prefix = "k"
                elif (brec[9] & 0x20) != 0:     prefix = "M"
                else:                           prefix = ""

                if   (brec[10] & 0x80) != 0:    unit = "V"
                elif (brec[10] & 0x40) != 0:    unit = "A"
                elif (brec[10] & 0x20) != 0:    unit = "Ω"
                elif (brec[10] & 0x10) != 0:    unit = "hFE"
                elif (brec[10] & 0x08) != 0:    unit = "Hz"
                elif (brec[10] & 0x04) != 0:    unit = "F"
                elif (brec[10] & 0x02) != 0:    unit = "℃"
                elif (brec[10] & 0x01) != 0:    unit = "℉"
                else:                           unit = ""

                ydprint(defname, f"Dur:{rdur:0.1f} ms  brec:{brec}   Len:{len(brec)}  value: {value} {prefix}{unit}")

            else:
                value = g.NAN
                ydprint(defname, f"Dur:{rdur:0.1f} ms  response with incorrect format: brec:{brec}")

    except Exception as e:
        emsg = f"FAILURE writing/reading serial "
        exceptPrint(e, defname + emsg)
        QueuePrint(defname, "Failure: " + e.strerror)
        value = g.NAN
        time.sleep(0.1)

    # setIndent(0)
    return value


def getOW18EVoltage():
    """Query the OWON OW18E DMM via Bluetooth for a single Value"""
    # cmd:  gtools/owon_multi_cli -a A6:C0:80:E3:85:9D -t ow18e -1

    defname  = "getOW18EVoltage: "
    # rdprint(defname)
    # setIndent(1)

    bstart      = time.time()
    scmd        = ["gtools/owon_multi_cli", '-a', 'A6:C0:80:E3:85:9D', '-t', 'ow18e', "-1"]
    suboutput   = b"No Output"
    try:
        suboutput = subprocess.run(scmd, capture_output=True, timeout=2)
        if suboutput.returncode != 1:                                           # default returncode seems 1; should be zero
            rdprint(defname, "suboutput: ", suboutput)
            QueueSoundDVL("alarm")
            time.sleep(0.1)

    except subprocess.TimeoutExpired as e:
        emsg = f"Bluetooth Timeout"
        exceptPrint(e, defname + emsg)
        QueueSoundDVL("burp")
        value = g.NAN
        time.sleep(0.1)

    except subprocess.CalledProcessError as e:
        emsg = f"Bluetooth CalledProcessError"
        exceptPrint(e, defname + emsg)
        QueueSoundDVL("alarm")
        value = g.NAN
        time.sleep(0.1)


    except Exception as e:
        emsg = f"FAILURE writing/reading Bluetooth"
        exceptPrint(e, defname + emsg)
        QueuePrint(defname, "Failure: " + str(e))
        value = g.NAN
        time.sleep(0.1)

    else:
        raw      = suboutput.stdout
        response = raw.decode('UTF-8').strip().split(" ")
        # rdprint(defname, "suboutput.stdout: ", suboutput.stdout)

        if len(response) == 4:
            value = float(response[1])
        else:
            edprint(defname, f"Wrong Bluetooth output: {raw}  response: {response}")
            QueueSoundDVL("cocoo")
            value = g.NAN

    bdur        = 1000 * (time.time() - bstart)
    sop         = (str(suboutput)).replace("CompletedProcess", "")
    gdprint(defname,  f"Dur:{bdur:0.1f} ms  sop:{sop}  value:{value}")

    g.Bluetoothdur = bdur
    # setIndent(0)

    return value


def BLUEPILLVOLTAGE(port="/dev/ttyACM1"):
    """Query the BluePill STM32 board for ADC Voltage"""

    defname  = "BLUEPILLVOLTAGE: "
    # rdprint(defname)
    # setIndent(1)

    if   "ACM" in port:  port = port.replace("/DEV/TTY", "/dev/tty")
    elif "USB" in port:  port = port.replace("/DEV/TTY", "/dev/tty")

    try:
        ### using serial port with context manager ########################
        brec = b""
        with serial.Serial( port          = port,
                            baudrate      = 115200,
                            timeout       = 1,
                            write_timeout = 3,                 ) as RPser:

        # write - takes about 0.1 ms
            # wstart   = time.time()
            try:
                wcnt     = RPser.write(b"\xff")                                         # wcnt= no of Bytes written
            except serial.SerialTimeoutException as e:                                  # this exception only with timeout on WRITE !
                exceptPrint(e, defname + f"FAILURE TimeoutException on WRITING")
                return g.NAN
            except Exception as e:
                exceptPrint(e, defname + f"FAILURE writing serial ")
                return g.NAN
            # wdur = 1000 * (time.time() - wstart)
            # rdprint(defname, f"Writing took: {wdur:0.3f} ms")


        # wait for data in the pipeline but wait no longer than 5 sec - takes <1 ms
            beginwait = time.time()
            while RPser.in_waiting == 0:
                dtime = time.time() - beginwait
                if (dtime) > 5:
                    rdprint(defname, f"Waited: {dtime:0.3f} sec")
                    setIndent(0)
                    return g.NAN
            # rdprint(defname, f"Waited: {dtime:0.3f} sec")

        # read - takes 1.7 ... 2.3 ms
            rstart   = time.time()
            try:
                brec     = RPser.readline()                                             # waits for LF; timeoutR when no LF received, but download Hist takes > 2 sec, yet works?
            except Exception as e:
                exceptPrint(e, defname + f"FAILURE reading serial ")
                # brec     = b""
        ### serial port is now CLOSED  ###################################

    except Exception as e:
        exceptPrint(e, defname + f"FAILURE writing/reading serial ")
        QueuePrint(defname, "Failure: " + e.strerror)
        return g.NAN

    rdur = 1000 * (time.time() - rstart)
    mdprint(defname, f"brec: {brec}   Py-read-dur: {rdur:0.1f} ms")

    try:
        # Example for BluePill output captured in brec:
        # 100µs wait: BLUEPILLVOLTAGE: brec: b'2418 2411 2415 2413 2420 2421 2400 2419 2415 2416 CPU Time: 1396064 ms  ADCVOLT: 1.945 V   DurADCVolt: 2.0 ms  \r\n'
        # 200µs wait: BLUEPILLVOLTAGE: brec: b'2432 2449 2449 2447 2449 2447 2441 2412 2448 2450 CPU Time: 177845 ms  ADCVOLT: 1.967 V   DurADCVolt: 3.1 ms  \r\n'


        index    = brec.find(b"ADCVOLT:") + 8
        voltage  = brec[index:].strip().split(b" ")

        try:    voltage = float(voltage[0])
        except: voltage = g.NAN
    except Exception as e:
        exceptPrint(e, "voltage stuff")

    # g.BluepillDur = rdur
    # g.BluePillVal = voltage

    # setIndent(0)
    return voltage     # voltage is type float

