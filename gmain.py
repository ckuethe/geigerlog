#! /usr/bin/env python3
# -*- coding: utf-8 -*-

"""
gmain.py - GeigerLog main entry file

include in programs with:
    import gmain
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

import  gsup_config
from    gsup_utils   import *


def verifyPythonVersion():
    """Verify proper Python version"""

    # currently (2023-12-10)  at least 3.8 is needed

    # Python 3.5
    #   Python 3.5 reached end of life on September 13th, 2020.
    #   pip 21.0 will drop support for Python 3.5 in January 2021.
    #   Python 3.5 does NOT support ordered dicts, resulting in major problems!
    # Python 3.6
    #   Python 3.6 reached end of life on 23 Dec 2021
    #   Python 3.6 has no threading HTTP server
    # Python 3.7  reached end of life on 27 Jun 2023
    #   cannot install PyQt5 anymore

    # Python 3.8  will reach end of life on 14 Oct 2024
    # Python 3.9  will reach end of life on 05 Oct 2025
    # Python 3.10 will reach end of life on 04 Oct 2026
    # Python 3.11 will reach end of life on    Oct 2027
    # Python 3.12 will reach end of life on    Oct 2028
    # Python 3.13 will reach end of life on    Oct 2029
    #

    defname          = "verifyPythonVersion: "
    svi              = sys.version_info
    currentPyVersion = "{}.{}.{}".format(svi[0], svi[1], svi[2])

    if svi < (3, 8):    # Python version >= v3.8 is required.
        msg = """
            GeigerLog Version {} requires<br><br><b>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Python in version 3.8 or later,</b><br><br>
            but your Python version is only: {}.<br><br>
            See chapter "Appendix I – Installation" in the GeigerLog manual for upgrade options.
            <br><br>
            Cannot continue, will exit.
            """.format(g.__version__, currentPyVersion)

    else: # Python has proper version
        msg = ""

    # print(defname, msg)
    return msg


def main():
    """GeigerLog Main File"""

    defname = "main: "
    # print(defname, "START")

# clear the terminal
    # clearTerminal()

# proper Python version?
    # result will be handled in ggeiger.py
    g.python_version = verifyPythonVersion()

# set directories and file names
    # name
    g.progName         = getProgName          ()      # 'geigerlog' even if prog is named 'geigerlog.py'

    # dir names with path
    g.progDir          = getPathToProgDir     ()      # WorkDir of GeigerLog:  /home/ullix/geigerlog/geigerlog
    g.dataDir          = getPathToDataDir     ()      # dir where all logging and history data will be saved to
    g.configDir        = getPathToConfigDir   ()      # dir where all logging and history data will be saved to
    g.resDir           = getPathToResDir      ()      # dir where all resources (like icons) are stored
    g.webDir           = getPathToWebDir      ()      # dir where all web files (html, JS) are located
    # g.fileDialogDir    = g.dataDir

    # file names with path
    g.proglogFile      = getPathToProglogFile ()
    g.configFile       = getPathToConfigFile  ()
    g.settingsFile     = getPathToSettingsFile()


# Virtual environment

    if g.isSetVenv:

        # shortcut: use separate directories for venv by putting 'venv' in command line
        if "venv" in sys.argv: g.useVenvDirectory = True

        if g.useVenvDirectory:
            # rdprint(defname, "USING venv dir")

            # update the data dir
            g.dataDir    = os.path.join(g.dataDir, g.VenvName)

            # update the path to the proglog file
            g.proglogFile = os.path.join(g.dataDir, g.progName + ".proglog")

            # update the path to the config dir
            newconfigDir  = os.path.join(g.configDir, g.VenvName)

            if not os.path.exists(newconfigDir):
                try:
                    os.mkdir(newconfigDir)
                except:
                    pass
                else:
                    shutil.copy2(g.configFile,   newconfigDir)
                    # shutil.copy2(g.settingsFile, newconfigDir)

            g.configFile   = os.path.join(newconfigDir, g.progName + ".cfg")
            g.settingsFile = os.path.join(newconfigDir, g.progName + ".settings")


# reset - remove settings file after an autoinstall
    if "factoryreset" in sys.argv:
        try:
            # remove settingsFile
            if os.path.exists(g.settingsFile):
                os.remove(g.settingsFile)

            # recreate config file from hidden file ".DO_NOT_MODIFY"
            default_cfg = os.path.join(g.configDir, ".DO_NOT_MODIFY")
            if os.path.exists(default_cfg):
                shutil.copy2(default_cfg, g.configFile)

        except Exception as e:
            exceptPrint(e, "factoryreset execution")


# set the dialogs dir (maybe changed within the dialog!)
    g.fileDialogDir    = g.dataDir


# set GeigerLog's IP
    g.GeigerLogIP      = getGeigerLogIP()


# data directory: Make sure it exists; create it if needed
    # exit if it cannot be made or is not writable
    if os.access(g.dataDir , os.F_OK): # test for file exists
        # dir exists, ok
        if not os.access(g.dataDir , os.W_OK):
            # dir exists, but is not writable
            print("ERROR: main: Data directory '{}' exists, but is not writable".format(g.dataDirectory))
            return 1
    else:
        # dir does not exist; make it
        try:
            os.mkdir(g.dataDir )
        except Exception as e:
            # dir cannot be made
            print("ERROR: main: Could not make data directory '{}'".format(g.dataDirectory))
            return 1

# gres directory: Make sure it exists and is readable
    if os.access(g.resDir , os.F_OK):
        # dir exists, ok
        if not os.access(g.dataDir , os.R_OK):
            # dir exists, but is not readable
            print("ERROR: main: GeigerLog resource directory {} exists but is not readable".format(g.resDir))
            return 1
    else:
        print("ERROR: main: GeigerLog resource directory {} does not exist. You may have to reinstall GeigerLog".format(g.resDir))
        return 1

# gweb directory: Make sure it exists and is readable
    if os.access(g.webDir , os.F_OK):
        # dir exists, ok
        if not os.access(g.dataDir , os.R_OK):
            # dir exists, but is not readable
            print("ERROR: main: GeigerLog web directory {} exists but is not readable".format(g.webDir))
            return 1
    else:
        print("ERROR: main: GeigerLog web directory {} does not exist. You may have to reinstall GeigerLog".format(g.webDir))
        return 1

# parse command line options
    try:
        # sys.argv[0] is progname
        opts, args = getopt.getopt(sys.argv[1:], "hdvwl:VLs:", ["help", "debug", "verbose", "logfile=", "werbose", "Version", "ListPorts", "style=", "pwmfreq="])
        # print(defname, "opts, args: ", opts, args)
    except getopt.GetoptError as e :
        # print info like: "option -x not recognized", then exit
        msg = "For Help use: './geigerlog -h'"
        exceptPrint(e, msg)
        return 1

    # processing the options
    for opt, optval in opts:
        if   opt in ("-h", "--help"):
            print("\nHELP - Command Line Options and Commands")
            print(g.helpOptions)
            return 0

        elif opt in ("-V", "--Version"):    # show the GeigerLog and modules versions
            print("\nVersion status:")
            for ver in g.versions:
                print("   {:25s}: {}".format(ver, g.versions[ver]))
            return 0

        elif opt in ("-L", "--ListPorts"):   # which ports are available?
            print("\nAvailable USB-to-Serial ports (with symlinks):")
            lp = serial.tools.list_ports.comports(include_links=True)  # default; include_links=True also shows symlinks
            getPortList(symlinks=True)
            return 0

        elif opt in ("-d", "--debug"):
            g.debug    = True

        elif opt in ("-v", "--verbose"):
            g.verbose  = True
            g.debug    = True                   # giving verbose implies debug

        elif opt in ("-w", "--werbose"):
            g.werbose  = True
            g.verbose  = True                   # giving werbose implies verbose
            g.debug    = True                   # giving verbose implies debug

        elif opt in ("-s", "--style"):          # style cannot be set now, only AFTER QApplication is defined, see below
            g.CustomStyle = optval

        elif opt in ("-l", "--logfile"):
            g.autoLogFile = optval.strip().replace(" ", "") + ".logdb"  # remove any space

        elif opt in ("--pwmfreq"):
            try:
                g.RaspiPulsePWM_Freq = float(optval)
            except Exception as e:
                exceptPrint(e, "RaspiPulsePWM_Freq could not be set; now setting to 30")
                g.RaspiPulsePWM_Freq = 30


    # processing the args as commands
    for arg in args:

        arg = arg.lower()

        # devel
        if   arg == "devel":         g.devel                = True  # set development mode
        elif arg == "trace":         g.traceback            = True  # to printout traceback info

        # autostart
        elif arg == "connect":       g.autoDevConnect       = True  # auto connect after start
        elif arg == "load":          g.autoLogLoad          = True  # auto load last default file
        elif arg == "start":         g.autoLogStart         = True  # auto start last default file
        elif arg == "quick":         g.autoQuickStart       = True  # auto quick start

        # flags
        elif arg == "fullhist":      g.fullhist             = True  # download the full GMC counter memory
        elif arg == "keepff":        g.keepFF               = True  # keep the FF values
        elif arg == "forcelw":       g.forcelw              = True  # force line wrapping on lines longer than screen
        elif arg == "forcenolw":     g.forcelw              = False # on True allows longer lines which flow out of screen
        elif arg == "testing":       g.testing              = True  # generic testing
        elif arg == "simulgmc":      g.GMC_simul            = True  # only for GMC device, simulating other counter types
        elif arg == "gmctesting":    g.GMC_testing          = True  # only for GMC device, to activate GMC specific testing
        elif arg == "simulgs":       g.GS_simul             = True  # only for GammaScout device, simulation a connected counter
        elif arg == "timing":        g.timing               = True  # print extra timing info
        elif arg == "osterei":       g.AudioOei             = True  # print audiodei
        elif arg == "clockisdead":   g.GMC_ClockIsDead      = True  # used to NOT parse the time in History of a GMC counter (for my broken GMC-500)
        # elif arg == "tele":        g.TelegramActivation   = True  # activate Telegram
        elif "bold" in arg:          g.graphbold            = True  # thick lines for all vars
        elif arg == "nolines":       g.graphConnectDots     = False # no connection of dots with lines
        elif arg == "pwm":           g.RaspiPulsePWM_Active = True  #
        elif arg == "radpropwm":     g.RadProPWM            = True  # when testing PWM Efffect on HV of RadPro
        elif arg == "showstyles":                                   # show all GUI styles found on system
            print("\nHELP - Styles found on system: ")
            for a in QStyleFactory.keys():  print("   " + a)
            return 0

        if g.devel:
            # g.graphbold                                   = True  # for development make thick lines for all vars
            g.writeDevelproglog                             = True  # for development create a geigerlog.proglog.devel file
            # g.traceback                                   = True  # to printout traceback info

        # device commands
        if   arg == "gmc":        g.Devices["GMC"]         [g.ACTIV] = True     # 1
        elif arg == "audio":      g.Devices["Audio"]       [g.ACTIV] = True     # 2
        elif arg == "iot":        g.Devices["IoT"]         [g.ACTIV] = True     # 3
        elif arg == "radmon":     g.Devices["RadMon"]      [g.ACTIV] = True     # 4
        elif arg == "ambio":      g.Devices["AmbioMon"]    [g.ACTIV] = True     # 5
        elif arg == "gscout":     g.Devices["GammaScout"]  [g.ACTIV] = True     # 6
        elif arg == "i2c":        g.Devices["I2C"]         [g.ACTIV] = True     # 7
        elif arg == "labjack":    g.Devices["LabJack"]     [g.ACTIV] = True     # 8
        elif arg == "minimon":    g.Devices["MiniMon"]     [g.ACTIV] = True     # 9
        elif arg == "formula":    g.Devices["Formula"]     [g.ACTIV] = True     # 10
        elif arg == "wific":      g.Devices["WiFiClient"]  [g.ACTIV] = True     # 11
        elif arg == "wifis":      g.Devices["WiFiServer"]  [g.ACTIV] = True     # 12
        elif arg == "ri2c":       g.Devices["RaspiI2C"]    [g.ACTIV] = True     # 13
        elif arg == "rpulse":     g.Devices["RaspiPulse"]  [g.ACTIV] = True     # 14
        elif arg == "spulse":     g.Devices["SerialPulse"] [g.ACTIV] = True     # 15
        elif arg == "manu":       g.Devices["Manu"]        [g.ACTIV] = True     # 16
        elif arg == "radpro":     g.Devices["RadPro"]      [g.ACTIV] = True     # 17
        elif arg == "all":
            for key in g.Devices: g.Devices[key]           [g.ACTIV] = True     # activate ALL devices

        elif arg == "dummy":      g.Devices["Formula"]     [g.ACTIV] = True     # 10 # make a formula device and later sets some ValueFormulas

# showing warnings or not
    # see: https://docs.python.org/3/library/warnings.html#module-warnings
    # sys.warnoptions == []             on all starts of Python as:           'python'
    # sys.warnoptions == ['default']    when Python started with '-W' option: 'python -W default'
    # rdprint("sys.warnoptions: ", sys.warnoptions)
    # warnoptions: "error", "ignore", "always", "default", "module", "once"
    if g.devel:
        # under devel show all warnings
        if not sys.warnoptions:
            warnings.simplefilter("default")            # Change the filter in this process
            os.environ["PYTHONWARNINGS"] = "default"    # Also affect subprocesses; print with shell comannd: printenv
    else:
        # hide all warnings when in regular use, i.e. non-devel use
        if not sys.warnoptions:
            warnings.simplefilter("ignore")             # show nothing

# clear files 'geigerlog.proglog' and 'geigerlog.proglog.zip', and initialize file 'geigerlog.proglog'
    clearProgramLogFiles()

# clear the special log file
    writeSpecialLog("Clear Special Log File", clearflag=True)

# command line
    dprint("{:28s}: sys.argv: {}"               .format("Command line", sys.argv))

# pid
    g.geigerlog_pid = os.getpid()
    dprint("{:28s}: {}".format("GeigerLog PID", g.geigerlog_pid))

# X11 or Wayland
    # $ echo $XDG_SESSION_TYPE
    dprint("{:28s}: {}".format("XDG Windowing System", os.getenv("XDG_SESSION_TYPE")))

# virtual environment
    dprint("{:28s}: {}".format("Virtual Environment:", "{}".format(g.VenvMessage)   ))             # already includes g.VenvName
    dprint("{:28s}: {}".format("   sys.base_prefix:",  "{}".format(sys.base_prefix) ))
    dprint("{:28s}: {}".format("   sys.prefix:",       "{}".format(sys.prefix)      ))


# set terminal output with or without line wrapping (works in Linux only)
    executeTPUT(action = 'no_line_wrapping')

# as precaution: Fix Garbled Audio with command "pulseaudio -k"
    fixGarbledAudio(quiet=True)

# PID
    # to kill a process by pid from Python:
    # >>> import os, signal
    # >>> os.kill(2050061, signal.SIGINT)


#
# using SIGNALs
#
# Signal handlers
#   on Linux: see: https://www.computerhope.com/unix/signals.htm
    if g.devel:
        # Printing supported signals :
        # import signal is needed
        valid_signals = signal.valid_signals()  # requires python 3.9.0; returns a SET
        # cdprint('Number of Available Signals ->', len(valid_signals))
        # cdprint("   signal.SIG_DFL: ", signal.SIG_DFL, " = ", signal.SIG_DFL * 1)    # DFL = 0
        # cdprint("   signal.SIG_IGN: ", signal.SIG_IGN, " = ", signal.SIG_IGN * 1)    # IGN = 1
        wprint('Number of Available Signals: ', len(valid_signals))
        wprint("   signal.SIG_DFL: ", signal.SIG_DFL, " = ", signal.SIG_DFL * 1)    # DFL = 0
        wprint("   signal.SIG_IGN: ", signal.SIG_IGN, " = ", signal.SIG_IGN * 1)    # IGN = 1

        # for i, vs in enumerate(valid_signals):
        #     try:
        #         cdprint("   i: {:2n}  signal.valid_signals: {:20s}  signal.getsignal(): {}".format(i + 1, str(vs),  str(signal.getsignal(i + 1))))
        #     except ValueError as e:
        #         edprint(": i: {:2d}, signal.getsignal({:2d}): ValueError: '{}'".format(i, i, e))
        #     except Exception as e:
        #         edprint(": i: {:2d}, signal.getsignal({:2d}): Exception:  '{}'".format(i, i, e))


        for i, vs in enumerate(valid_signals):
            try:
                wprint ("   #: {:2n}  signal.valid_signals: {:20s}  signal.getsignal(): {}".format(i + 1, str(vs),  str(signal.getsignal(i + 1))))
            except ValueError as e:
                edprint("   #: {:2d}, signal.getsignal({:2d}): ValueError: '{}'".format(i, i, e))
            except Exception as e:
                edprint("   #: {:2d}, signal.getsignal({:2d}): Exception:  '{}'".format(i, i, e))


    # On my Linux computer:
    # Number of Available Signals -> 62
    #   signal.SIG_DFL: Handlers.SIG_DFL  = 0
    #   signal.SIG_IGN: Handlers.SIG_IGN  = 1
    #                                                                                                                       on Windows no signals except
    #    i:  1  signal.valid_signals: Signals.SIGHUP        signal.getsignal(): Handlers.SIG_DFL
    #    i:  2  signal.valid_signals: Signals.SIGINT        signal.getsignal(): <built-in function default_int_handler>         yes
    #    i:  3  signal.valid_signals: Signals.SIGQUIT       signal.getsignal(): Handlers.SIG_DFL
    #    i:  4  signal.valid_signals: Signals.SIGILL        signal.getsignal(): Handlers.SIG_DFL                                yes
    #    i:  5  signal.valid_signals: Signals.SIGTRAP       signal.getsignal(): Handlers.SIG_DFL
    #    i:  6  signal.valid_signals: Signals.SIGABRT       signal.getsignal(): Handlers.SIG_DFL                                yes
    #    i:  7  signal.valid_signals: Signals.SIGBUS        signal.getsignal(): Handlers.SIG_DFL
    #    i:  8  signal.valid_signals: Signals.SIGFPE        signal.getsignal(): Handlers.SIG_DFL                                yes
    #    i:  9  signal.valid_signals: Signals.SIGKILL       signal.getsignal(): Handlers.SIG_DFL
    #    i: 10  signal.valid_signals: Signals.SIGUSR1       signal.getsignal(): Handlers.SIG_DFL
    #    i: 11  signal.valid_signals: Signals.SIGSEGV       signal.getsignal(): Handlers.SIG_DFL                                yes
    #    i: 12  signal.valid_signals: Signals.SIGUSR2       signal.getsignal(): Handlers.SIG_DFL
    #    i: 13  signal.valid_signals: Signals.SIGPIPE       signal.getsignal(): Handlers.SIG_IGN ***
    #    i: 14  signal.valid_signals: Signals.SIGALRM       signal.getsignal(): Handlers.SIG_DFL
    #    i: 15  signal.valid_signals: Signals.SIGTERM       signal.getsignal(): Handlers.SIG_DFL                                yes
    #    i: 16  signal.valid_signals: 16                    signal.getsignal(): Handlers.SIG_DFL
    #    i: 17  signal.valid_signals: Signals.SIGCHLD       signal.getsignal(): Handlers.SIG_DFL
    #    i: 18  signal.valid_signals: Signals.SIGCONT       signal.getsignal(): Handlers.SIG_DFL
    #    i: 19  signal.valid_signals: Signals.SIGSTOP       signal.getsignal(): Handlers.SIG_DFL
    #    i: 20  signal.valid_signals: Signals.SIGTSTP       signal.getsignal(): Handlers.SIG_DFL
    #    i: 21  signal.valid_signals: Signals.SIGTTIN       signal.getsignal(): Handlers.SIG_DFL
    #    i: 22  signal.valid_signals: Signals.SIGTTOU       signal.getsignal(): Handlers.SIG_DFL
    #    i: 23  signal.valid_signals: Signals.SIGURG        signal.getsignal(): Handlers.SIG_DFL
    #    i: 24  signal.valid_signals: Signals.SIGXCPU       signal.getsignal(): Handlers.SIG_DFL
    #    i: 25  signal.valid_signals: Signals.SIGXFSZ       signal.getsignal(): Handlers.SIG_IGN ***
    #    i: 26  signal.valid_signals: Signals.SIGVTALRM     signal.getsignal(): Handlers.SIG_DFL
    #    i: 27  signal.valid_signals: Signals.SIGPROF       signal.getsignal(): Handlers.SIG_DFL
    #    i: 28  signal.valid_signals: Signals.SIGWINCH      signal.getsignal(): Handlers.SIG_DFL
    #    i: 29  signal.valid_signals: Signals.SIGIO         signal.getsignal(): Handlers.SIG_DFL
    #    i: 30  signal.valid_signals: Signals.SIGPWR        signal.getsignal(): Handlers.SIG_DFL
    #    i: 31  signal.valid_signals: Signals.SIGSYS        signal.getsignal(): Handlers.SIG_DFL
    #    i: 32  signal.valid_signals: Signals.SIGRTMIN      signal.getsignal(): None             ***
    #    i: 33  signal.valid_signals: 35                    signal.getsignal(): None             ***
    #    i: 34  signal.valid_signals: 36                    signal.getsignal(): Handlers.SIG_DFL
    #    i: 35  signal.valid_signals: 37                    signal.getsignal(): Handlers.SIG_DFL
    #    i: 36  signal.valid_signals: 38                    signal.getsignal(): Handlers.SIG_DFL
    #    i: 37  signal.valid_signals: 39                    signal.getsignal(): Handlers.SIG_DFL
    #    i: 38  signal.valid_signals: 40                    signal.getsignal(): Handlers.SIG_DFL
    #    i: 39  signal.valid_signals: 41                    signal.getsignal(): Handlers.SIG_DFL
    #    i: 40  signal.valid_signals: 42                    signal.getsignal(): Handlers.SIG_DFL
    #    i: 41  signal.valid_signals: 43                    signal.getsignal(): Handlers.SIG_DFL
    #    i: 42  signal.valid_signals: 44                    signal.getsignal(): Handlers.SIG_DFL
    #    i: 43  signal.valid_signals: 45                    signal.getsignal(): Handlers.SIG_DFL
    #    i: 44  signal.valid_signals: 46                    signal.getsignal(): Handlers.SIG_DFL
    #    i: 45  signal.valid_signals: 47                    signal.getsignal(): Handlers.SIG_DFL
    #    i: 46  signal.valid_signals: 48                    signal.getsignal(): Handlers.SIG_DFL
    #    i: 47  signal.valid_signals: 49                    signal.getsignal(): Handlers.SIG_DFL
    #    i: 48  signal.valid_signals: 50                    signal.getsignal(): Handlers.SIG_DFL
    #    i: 49  signal.valid_signals: 51                    signal.getsignal(): Handlers.SIG_DFL
    #    i: 50  signal.valid_signals: 52                    signal.getsignal(): Handlers.SIG_DFL
    #    i: 51  signal.valid_signals: 53                    signal.getsignal(): Handlers.SIG_DFL
    #    i: 52  signal.valid_signals: 54                    signal.getsignal(): Handlers.SIG_DFL
    #    i: 53  signal.valid_signals: 55                    signal.getsignal(): Handlers.SIG_DFL
    #    i: 54  signal.valid_signals: 56                    signal.getsignal(): Handlers.SIG_DFL
    #    i: 55  signal.valid_signals: 57                    signal.getsignal(): Handlers.SIG_DFL
    #    i: 56  signal.valid_signals: 58                    signal.getsignal(): Handlers.SIG_DFL
    #    i: 57  signal.valid_signals: 59                    signal.getsignal(): Handlers.SIG_DFL
    #    i: 58  signal.valid_signals: 60                    signal.getsignal(): Handlers.SIG_DFL
    #    i: 59  signal.valid_signals: 61                    signal.getsignal(): Handlers.SIG_DFL
    #    i: 60  signal.valid_signals: 62                    signal.getsignal(): Handlers.SIG_DFL
    #    i: 61  signal.valid_signals: 63                    signal.getsignal(): Handlers.SIG_DFL
    #    i: 62  signal.valid_signals: Signals.SIGRTMAX      signal.getsignal(): Handlers.SIG_DFL
    # --- End Linux signals -----------------------------------------------------------------------
    #
    # on Windows, Attention :
    #   see: https://docs.microsoft.com/en-us/previous-versions/xdkz3x12(v=vs.140)
    #   ??? SIGINT :  CTRL+C signal, but: "SIGINT is not supported for any Win32 application."
    #   ??? SIGTSTP:  CTRL-Z signal, NOT supported on Windows!!!
    #
    # Windows Signal Info:
    #           sig value 	    Description
    # Windows:  SIGABRT 	    Abnormal termination
    # Windows:  SIGFPE 	        Floating-point error
    # Windows:  SIGILL 	        Illegal instruction
    # Windows:  SIGINT 	        CTRL+C signal
    # Windows:  SIGSEGV 	    Illegal storage access
    # Windows:  SIGTERM 	    Termination request
    # -------------------------------------------------
    # Auf meinem MSI Win10 Rechner ist zusätzlichvorhanden:
    #           SIGBREAK        NOT supported by Linux
    # -------------------------------------------------

    #
    # using SIGNALs
    #
    # signal SIGINT  (CTRL-C) can be used on Linux and Windows
    # signal SIGTERM (CTRL-C) can be used on Linux and Windows
    # signal SIGQUIT (CTRL+\) can be used on Linux but NOT on Windows
    # signal SIGTSTP (CTRL+Z) can be used on Linux but NOT on Windows
    #
    # Linux, (Mac), NOT Windows:
    if not "WINDOWS" in platform.platform().upper():
        try:
            signal.signal(signal.SIGQUIT, getmeout)               # SIGQUIT (CTRL+\) to show SystemInfo in terminal
            dprint("{:28s}: SIGQUIT: {:2d}, getsignal(SIGQUIT): {}".format("SIGNAL SIGQUIT set",         signal.SIGQUIT, signal.getsignal(signal.SIGQUIT)))
            signal.signal(signal.SIGTSTP, signal.SIG_IGN)         # SIGTSTP (CTRL-Z) signal will be ignored
            dprint("{:28s}: SIGTSTP: {:2d}, getsignal(SIGTSTP): {}".format("SIGNAL SIGTSTP set ignored", signal.SIGTSTP, signal.getsignal(signal.SIGTSTP)))
        except Exception as e:
            exceptPrint(e, "SIGNAL SIGTSTP setting failed on platform: '{}'".format(platform.platform()))

    # Linux, Windows, (Mac)
    # using signal SIGTERM (CTRL-C) for shutting down GeigerLog
    # Will be changed later (at end of ggeiger) to "forced orderly closure" !
    signal.signal(signal.SIGINT,   getmeout)
    signal.signal(signal.SIGTERM,  getmeout)


# Command line
    dprint("{:28s}: options: {}, commands: {}"  .format("Options, Commands", opts, args))


# CPU Infos - CPU & Machine
    getCPU_Details()

    dprint("{:28s}: {}"     .format("CPU Model",    g.CPU_Model))
    dprint("{:28s}: {}"     .format("CPU Brand",    g.CPU_BrandRaw))         #g.CPU_BrandRaw  = myCPUinfo["brand_raw"]
    dprint("{:28s}: {}"     .format("CPU Vendor",   g.CPU_Vendor))
    dprint("{:28s}: {}"     .format("CPU Hardware", g.CPU_Hardware))

    dprint("{:28s}: {}, {}" .format("Machine", platform.machine(), platform.architecture()[0]))
    dprint("{:28s}: {}"     .format("Machine Total Memory",  "{:5.1f} GiB = {:5.1f} GB = {:14,.0f} B".format(getMemoryTotal("GiB"), getMemoryTotal("GB"), getMemoryTotal("B"))))
    dprint("{:28s}: {}"     .format("GeigerLog Used Memory", "{:5.1f} MiB = {:5.1f} MB = {:14,.0f} B".format(getMemoryUsed ("MiB"), getMemoryUsed ("MB"), getMemoryUsed ("B"))))


# Platform
    dprint("{:28s}: {}"     .format("Operating System",     platform.platform()))
    dprint("{:28s}: {}"     .format("Implemented Python",   platform.python_implementation()))


# Python garbage collection
    # https://stackify.com/python-garbage-collection/

    ### Testing - disable garbage collection ###
    # gc.disable()
    ############################################

    dprint("{:28s}: {}"     .format("Python Garbage Collection", "Enabled" if gc.isenabled() else "Disabled"))


# Computing Power (estimated by Fibonacci series)
    fbstart = time.time()
    fbrange = 26
    fbnum   = [Fibonacci(n) for n in range(fbrange)]
    fbdur   = 1000 * (time.time() - fbstart)
    g.FibonacciSpeed = fbdur
    if g.devel: dprint("{:28s}: {}".format("Fibonacci({}) Speed".format(fbrange), "Dur: {:<5.1f}ms   - A 'Good Computer' is <=50 ms; lower number means better".format(fbdur)))


# Computing Power (estimated by hash() on random string)
    hstart = time.time()
    for i in range(600):
        rbytes = ", ".join(str(r) for r in np.random.rand(100))
        hnum   = hash(rbytes)
    hdur   = 1000 * (time.time() - hstart)
    g.HashSpeed = hdur
    if g.devel: dprint("{:28s}: {}".format("Hash Speed", "Dur: {:<5.1f}ms   - A 'Good Computer' is <= 50ms; lower number means better".format(hdur)))

# GeigerLog Benchmark (GLBM)
    #               System         Fibonacci        Hash    Sum         GLBM          # GLBM = 1/sum * 10 000
    # speed result: Linux urkam:     47.0 ms     49.3 ms    96          104
    # speed result: Linux DELL:      76.6 ms     64.8 ms    141          71
    # speed result: Fast Server:     80.8 ms     59.1 ms    140          71           # user Simon's Fast Server
    # speed result: Win10 MSI:      140.6 ms    109.4 ms    250          40
    # speed result: Linux Raspi5:   187.6 ms    207.7 ms    102.7        97
    # speed result: Linux Raspi4:    54.8 ms     47.9 ms    395          25
    # speed result: Linux Raspi3:   464.1 ms    280.7 ms    744.8        13
    # speed result: Linux VM:       547.8 ms    634.7 ms   1183           8           # user Simon with Linux VM on ??

    g.GLBenchmark = round(1e4 / (g.FibonacciSpeed + g.HashSpeed), 0)                  # makes urkam come out as ~100
    dprint("{:28s}: {}".format("GeigerLog Benchmark", "GLBM = {:<3.0f}     - A 'Good Computer' is GLBM >= 100; higher number means faster computer (compare with Raspis: Pi5=100; Pi4=25; Pi3=12)".format(g.GLBenchmark)))

    # set file size according to GLBM Benchmark to limit length of zipping calculation
    # GLBM = 100 as reference, higher is faster
    if   g.GLBenchmark >=  90:   g.LimitFileSize = 1E6         # 1 mio                # works ok on urkam
    elif g.GLBenchmark >=  50:   g.LimitFileSize = 5E5         # 500 k
    elif g.GLBenchmark >=  10:   g.LimitFileSize = 1E5         # 100 k
    else:                        g.LimitFileSize = 1E4         #  10 k
    dprint("{:28s}: {}".format("GeigerLog LimitFileSize", "{:0,.0f} Bytes".format(g.LimitFileSize)))

# Versions
    dprint("Version status: ")
    for ver in g.versions:
        dprint("   {:25s}: {}".format(ver, g.versions[ver]))

# Python Search Path
    dprint("Python Search Paths:")
    # sys.path.append('pfad/zu/irgend/was')                 # to extend Python's search path
    for a in sys.path:
        dprint("   {:25s}: {}".format("sys.path", a))

# Program Paths
    dprint("Program Paths:")
    dprint("   {:25s}: {}".format("progName",       g.progName))
    dprint("   {:25s}: {}".format("progDir",        g.progDir))
    dprint("   {:25s}: {}".format("configDir",      g.configDir))
    dprint("   {:25s}: {}".format("resDir",         g.resDir))
    dprint("   {:25s}: {}".format("webDir",         g.webDir))
    dprint("   {:25s}: {}".format("dataDir",        g.dataDir))
    dprint("   {:25s}: {}".format("proglogFile",    g.proglogFile))
    dprint("   {:25s}: {}".format("configFile",     g.configFile))
    dprint("   {:25s}: {}".format("settingsFile",   g.settingsFile))


# Read the configuration file
    # - its settings will override defaults in gglobs.py
    gsup_config.readGeigerLogConfig()   # geigerlog.cfg file MUST be present
    gsup_config.readPrivateConfig()     # ../private.cfg file is ignored if not present

# Read the settings file
    readSettingsFile()

# add some default formulas to the dummy device (==formula)
    if "dummy" in sys.argv:
        g.ValueScale["CPM3rd"] = "Poisson(123.456)"
        g.ValueScale["CPS3rd"] = "Poisson(12.3456)"

# Timezone Offset
    # rdprint(defname, "g.TimeZoneOffset: ", g.TimeZoneOffset)

    # ts = time.time()
    # local = dt.datetime.fromtimestamp(ts, tz=None)
    # utc   = dt.datetime.fromtimestamp(ts, tz=dt.timezone.utc)
    # rdprint(defname, "local:    ", local)
    # rdprint(defname, "utc:      ", utc)

    # ts_local = dt.datetime.strptime(str(local)[0:19], "%Y-%m-%d %H:%M:%S").timestamp()
    # ts_utc   = dt.datetime.strptime(str(utc)  [0:19], "%Y-%m-%d %H:%M:%S").timestamp()
    # rdprint(defname, "ts_local: ", ts_local)
    # rdprint(defname, "ts_utc:   ", ts_utc)

    # if g.TimeZoneOffset == "auto":
    #     # calc diff in sec; this has to ADDED to the Juliandate
    #     g.TimeZoneOffset = ts_local - ts_utc

    if g.TimeZoneOffset == "auto":
        g.TimeZoneOffset = dt.datetime.now().astimezone().utcoffset().total_seconds()
        dprint("{:28s}: {}"          .format("Time Zone", ""))
        dprint("{:28s}: {}"          .format("    Local Time Zone",          dt.datetime.now().astimezone().tzinfo))       # CET
        dprint("{:28s}: {} [h:m:s]"  .format("    Local Offset from UTC",    dt.datetime.now().astimezone().utcoffset()))  # 1:00:00
        dprint("{:28s}: {:+0.0f} sec".format("    Local Offset in sec",      g.TimeZoneOffset))                            # +3600 sec
    else:
        rdprint("{:28s}: {:+0.0f} sec".format("User Configured Time Offset", g.TimeZoneOffset))                            # e.g. +3600 sec


# comment for web
# workaround #1
# import datetime as dt
# ts = time.time()
# utc   = dt.datetime.fromtimestamp(ts, tz=datetime.timezone.utc)						# 2023-11-06 11:49:30.154083+00:00
# local = dt.datetime.fromtimestamp(ts, tz=None)										# 2023-11-06 12:49:30.154083
# ts_utc   = dt.datetime.strptime(str(utc)  [0:19], "%Y-%m-%d %H:%M:%S").timestamp()	# 1699267770.0
# ts_local = dt.datetime.strptime(str(local)[0:19], "%Y-%m-%d %H:%M:%S").timestamp()	# 1699271370.0	# more by 3600 sec
# TimeZoneOffset = ts_local - ts_utc													# +3600 (sec)

# # workaround #2
# TimeZoneOffset = dt.datetime.now().astimezone().utcoffset().total_seconds()			# +3600 (sec)


###############################################################################
# Starting PyQt
#
# QT_STYLE_OVERRIDE
    # app = QApplication([]) -> results in message: (only on PyQt5, not on PyQt4!)
    #    QApplication: invalid style override passed, ignoring it.
    #            Available styles: Windows, Fusion
    # unless a '-style <valid style>' is in sys.argv.
    #   app = QApplication([None, "-style", "Windows"])   # ok!
    #   app = QApplication([None, "-style", "Fusion"])    # ok!
    #   app = QApplication([None, "-style", ""])          # ok!
    #
    # This results from the setting of:  QT_STYLE_OVERRIDE="gtk" in the OS. (printenv | grep QT)
    # Can be removed on the shell:  export QT_STYLE_OVERRIDE="" -> then the message disappears
    # preferred: remove from within Python:
    os.environ["QT_STYLE_OVERRIDE"] = ""

# HiDPI screen
    # MUST be done before QApplication is started!
    # see my article: HOWTO - Using PyQt5 and matplotlib on HiDPI monitors (Python3).pdf
    #
    # QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    # !!!! im Raspi führte diese Anweisung zu einer Bildschirmgröße von 960x540,
    # !!!! obwohl Bildschirm auf 1920x1080 steht! -->unbrauchbar für Raspi
    #
    dprint("{:28s}".format("High DPI Scaling:"))
    if g.hidpiActivation == "auto" or g.hidpiActivation == "yes" :
        ehds = "EnableHighDpiScaling"
        uhdp = "UseHighDpiPixmaps"
        try:
            if hasattr(Qt, 'AA_EnableHighDpiScaling'):
                QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
                dprint("   {:25s}: {}".format(ehds, "Enabled"))
            else:
                edprint("   {:25s}: {}".format(ehds, "Attribute not available"))
        except Exception as e:
            edprint("   {:25s}: {} Exception: {}".format(ehds, "Failure!", e))

        try:
            if hasattr(Qt, 'AA_UseHighDpiPixmaps'):
                QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
                dprint("   {:25s}: {}".format(uhdp, "Enabled"))
            else:
                edprint("   {:25s}: {}".format(uhdp, "Attribute not available"))
        except Exception as e:
            edprint("   {:25s}: {} Exception: {}".format(uhdp, "Failure!", e))
    else:
        dprint("   {:25s}: {}".format("High DPI Scaling", "Deselected"))

# Locale setting
    # if the system's local is used, then e.g. Germany's local is used
    # this makes the double validator use komma as period !!
    #
    # QLocale.OmitGroupSeparator        0x01
    # If this option is set, the number-to-string functions will not insert group
    # separators in their return values. The default is to insert group separators.
    # QLocale.RejectGroupSeparator  0x02
    # If this option is set, the string-to-number functions will fail if they
    # encounter group separators in their input. The default is to accept numbers
    # containing correctly placed group separators.
    mylocal = QLocale()
    mylocal.setDefault(QLocale(QLocale.English, QLocale.UnitedStates));
    mylocal.setNumberOptions(QLocale.OmitGroupSeparator | QLocale.RejectGroupSeparator);
    #print("QLocale.numberOptions (self): ", mylocal.numberOptions()) # is an object :-(

# QApplication
    # app = QApplication(sys.argv)   # conflicts in syntax with getopt (single vs double dash)
    g.app = QApplication([])
    g.app.setWindowIcon           (QIcon(QPixmap(os.path.join(g.resDir, 'icon_geigerlog.png')))) # sets the icon for the whole app
    g.app.setApplicationName      ("GeigerLog")               # sets the name 'GeigerLog' as the application name
    g.app.setApplicationVersion   (g.__version__)             # sets the GL version
    g.app.setFont                 (QFont("Deja Vu Sans", 10)) # setting the application font size (default looks close to 11)
    ### setFont darf nicht größer sein als 10 !!!

    # g.app.setDesktopFileName("raspi")   # wo soll das zu sehen sein?


    # allows copy&Paste also on Win, but makes all Messageboxes as HTML coding
    # cumbersome with using space and tabs for formatting; do not use
    # g.app.setStyleSheet("QMessageBox { messagebox-text-interaction-flags: 5; }")

    dprint("QCore Application:")
    dprint("   {:25s}: {}".format("applicationName()"     , QCoreApplication.applicationName()))
    dprint("   {:25s}: {}".format("applicationVersion()"  , QCoreApplication.applicationVersion()))
    dprint("   {:25s}: {}".format("applicationDirPath()"  , QCoreApplication.applicationDirPath()))
    dprint("   {:25s}: {}".format("applicationFilePath()" , QCoreApplication.applicationFilePath()))

# Library paths
    dprint("QCore Library paths:")
    #QCoreApplication.addLibraryPath(g.progDir + "/custom_libs/") # will be listed only if folder exists
    #QCoreApplication.addLibraryPath("./");
    # needed? -> https://stackoverflow.com/questions/21268558/application-failed-to-start-because-it-could-not-find-or-load-the-qt-platform-pl
    libPaths    = QCoreApplication.libraryPaths()
    libPathStr  = "libraryPaths()"
    if len(libPaths) == 0:
        dprint("   {:25s}: {}".format(libPathStr, "No Library Paths"))
    else:
        for a in libPaths: dprint("   {:25s}: {}".format(libPathStr, a))

# QScreen
    # see: https://doc.qt.io/qt-5/qscreen.html#physicalDotsPerInch-prop
    # requires app.primaryScreen(), which is only available after app was started
    gaps = g.app.primaryScreen()
    dprint("Connected Screen:")
    dprint("   {:25s}: {}"          .format("manufacturer",           QScreen.manufacturer        (gaps)))
    dprint("   {:25s}: {}"          .format("model       ",           QScreen.model               (gaps)))
    dprint("   {:25s}: {}"          .format("name        ",           QScreen.name                (gaps)))
    dprint("   {:25s}: {} pixel"    .format("size        ",           QScreen.size                (gaps)))
    dprint("   {:25s}: {} pixel"    .format("geometry    ",           QScreen.geometry            (gaps)))
    dprint("   {:25s}: {}"          .format("depth       ",           QScreen.depth               (gaps)))
    dprint("   {:25s}: {} mm x mm"  .format("physicalSize",           QScreen.physicalSize        (gaps)))
    dprint("   {:25s}: {} dpi"      .format("physicalDotsPerInch",    QScreen.physicalDotsPerInch (gaps)))
    dprint("   {:25s}: {} dpi"      .format("physicalDotsPerInchX",   QScreen.physicalDotsPerInchX(gaps)))
    dprint("   {:25s}: {} dpi"      .format("physicalDotsPerInchY",   QScreen.physicalDotsPerInchY(gaps)))
    dprint("   {:25s}: {}"          .format("orientation ",           QScreen.orientation         (gaps)))
    dprint("   {:25s}: {}"          .format("devicePixelRatio",       QScreen.devicePixelRatio    (gaps)))
    dprint("   {:25s}: {}"          .format("refreshRate ",           QScreen.refreshRate         (gaps)))


# find the terminal size in columns, lines
    dprint("{:28s}: {}".format("Terminal Size",  shutil.get_terminal_size()))    # os.terminal_size(columns=238, lines=63)

# matplotlib HiDPI adjustment
    dprint("HiDPI MPL Scale:")
    if g.hidpiScaleMPL == "auto":
        g.hidpiScaleMPL = 100 / int(QScreen.devicePixelRatio(gaps))
    dprint("   {:25s}: {}".format("HiDPI MPL Scale",      g.hidpiScaleMPL))

# Style
    # latest news for PyQt5:
    # https://blog.qt.io/blog/2012/10/30/cleaning-up-styles-in-qt5-and-adding-fusion/
    # Summary: Default Qt5 has removed all styles except Windows (maybe) and added Fusion
    #
    # QStyleFactory::keys() returns a list of valid keys;
    # order of my preference; first is best: PyQt5: ['Fusion', 'Windows'] (PyQt5 has only 2)

    dprint("Styles:")
    dprint("   {:25s}: {}".format("Default",                g.app.style().metaObject().className()))
    dprint("   {:25s}: {}".format("Styles found on system", QStyleFactory.keys()))

    if g.CustomStyle is not None:
        available_styles = QStyleFactory.keys()
        if g.CustomStyle in available_styles:
            g.windowStyle = g.CustomStyle
            dprint("   {:25s}: '{}' - overrides default".format("Style per command line", g.windowStyle))
        else:
            g.windowStyle = "auto"
            dprint("   {:25s}: '{}' - Style not available (check spelling, capitalization); ignoring".format("Style per command line", g.CustomStyle))


    if g.windowStyle != "auto":    # existence of style had been verified
        result = g.app.setStyle(g.windowStyle)
        if result is None:  dprint("   Selected Style '{}' could not be applied".format(g.windowStyle))
    dprint("   {:25s}: {}".format("Active Style is", g.app.style().metaObject().className()))

# get the GUI
    from  ggeiger import ggeiger

# starting the GUI
    dprint(TCYAN + "Starting the GUI " + "-" * 110 + TDEFAULT)
    ex     = ggeiger()                                                  # an instance of ggeiger; runs init and draws window
    status = g.app.exec()                                               # starts the QApplication([]); run the GUI until closure
    gdprint("Exited GUI with status of: {} ".format(status) + "-" * 97)

# cleanup before exit
    executeTPUT(action = 'allow_line_wrapping')

    return status



# #####################################################################################################
# if __name__ == '__main__':
#     try:
#         main()

#     except KeyboardInterrupt:
#         print()
#         print("Exit by CTRL-C")
#         print()

