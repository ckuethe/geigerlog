 #! /usr/bin/env python3
# -*- coding: utf-8 -*-

"""
GeigerLog - A combination of data logger, data presenter, and data analyzer
            to handle Geiger counters as well as environmental sensors for
            Temperature, Pressure, Humidity, CO2, and else

Start as 'geigerlog -h' for help on available options and commands.
Use document 'GeigerLog-Manual-v<version number>.pdf' for further details.

This file serves as front-end to verify that Python is installed in proper
version before real GeigerLog is started.
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

########################################################################################################
# RASPI
#
# Raspi 5 does NOT boot when creating an SD image with 32bit-Debian Bullseye. Message:
# --> set os_check=0 in config.txt  --> keine Meldung mehr, aber Raspi 5 bootet gar nicht erst???
# telegram install
# had to remove apt-installed python-telegram-bot and then make pip-install in venv!!!
#
# pyqt5 install - always fails when done in venv on Raspi
# but an apt-installed version can be used when pip command gets --system-site-packages=True  option set


########################################################################################################
# VIRTUAL ENVIRONMENT (venv):
# 2 Options for creating a Virtual Environment for GeigerLog
#
# Option 1 : (NOT recommended) creating a venv and activating it
#
# ~$ python -m venv /home/ullix/geigerlog/geigerlog/venvGL                         # creating the venv venvGL from any directory by giving full path
# Activating the venv:
#   <venv> must be replaced by the path to the directory containing the virtual environment):
#   POSIX:                    source <venv>/bin/activate
#   Windows: cmd.exe:         C:\> <venv>\Scripts\activate.bat
#   Windows: PowerShell:      PS C:\> <venv>\Scripts\Activate.ps1
# De-Activating the venv:
#   all systems:              deactivate
#
# Breaking System:
# see:  https://stackoverflow.com/questions/75608323/how-do-i-solve-error-externally-managed-environment-every-time-i-use-pip-3
# However if you really want to install packages that way, then there are a couple of solutions:
#    use pip's argument --break-system-packages,
#
# alternatively allow system-site-packages by flag in venv call:     python -m venv --system-site-packages venvGL
#
# No '--user' available in venv!
#   -->  b"ERROR: Can not perform a '--user' install. User site-packages are not visible in this virtualenv.\n"
#
# Example for a Linux system:
#   cd /home/ullix/geigerlog/geigerlog                                          # change into the GeigerLog working directory
#   python -m venv venvGL                                                       # create the venv 'venvGL' - NOT  using flag: --system-site-packages
#   python -m venv --system-site-packages venvGL                                # create the venv 'venvGL' - WITH using flag: --system-site-packages
#   source venvGL/bin/activate                                                  # activate
#   (venvGL) ullix@urkam:~/geigerlog/geigerlog$                                 # --> this is the result
#   (venvGL) ullix@urkam:~/geigerlog/geigerlog$ ./geigerlog                     # starting GeigerLog (all Py modules have been installed for a successful start)
#   (venvGL) ullix@urkam:~/geigerlog/geigerlog$ deactivate                      # optional - deactivate the venv
#   ullix@urkam:~/geigerlog/geigerlog$                                          # --> result; back to normal
#
#
# Option 2 : (RECOMMENDED) using the bash and bat scripts
#
# ullix@urkam:~/geigerlog/geigerlog$ ./setupGeigerLog.sh                        # starting GeigerLog setup; includes auto-installation
#   should end with:
#       GeigerLog Setup was successful. No need to repeat it. From now on
#       simply start GeigerLog with command:  ./GeigerLog.sh
#
# ullix@urkam:~/geigerlog/geigerlog$ ./GeigerLog.sh -dvw devel connect load     # starting GeigerLog with options
# NOTE: no need for any deactivation


########################################################################################################

# VSCODE:
# "files to exclude: " *.proglog, *.stdlog, *data/*, *misc, COPYING, backup*, *.notes
#
# Wiggly red lines under all imports
# see vscode Settings: python.languageserver
#       Default     (-->Pylance if available, fallback is Jedi)
#       Jedi        (nach Neustart: KEINE wiggly lines under imports, aber auch KEINE wrong functions detected! Scheint abgeschaltet)
#       Pylance     (wiggly lines under imports; wrong functions are detected)
#       None        (nirgends wiggly lines, auch nicht bei falschen Funktionen!)
#
# Wiggle lines come both in regular Python call and in VENV call
# when both "code ." is called in Py3.8 venv, dann keine Wiggle lines
# jetzt geht es wieder, egal ob venv oder nicht ???? languageserver ist auf Default (=Pylance)


########################################################################################################
# compiling Python 3.11:
# Build Instructions
# ------------------
# On Unix, Linux, BSD, macOS, and Cygwin::
#     ./configure
#     make
#     make test
# don't do this:  #     sudo make install
# don't do this:  #     This will install Python as ``python3``.
# instead do:     #     sudo make altinstall
#
# Installing multiple versions
# ----------------------------
# On Unix and Mac systems if you intend to install multiple versions of Python
# using the same installation prefix (``--prefix`` argument to the configure
# script) you must take care that your primary python executable is not
# overwritten by the installation of a different version.  All files and
# directories installed using ``make altinstall`` contain the major and minor
# version and can thus live side-by-side.  ``make install`` also creates
# ``${prefix}/bin/python3`` which refers to ``${prefix}/bin/python3.X``.  If you
# intend to install multiple versions using the same prefix you must decide which
# version (if any) is your "primary" version.  Install that version using ``make
# install``.  Install all other versions using ``make altinstall``.

# For example, if you want to install Python 2.7, 3.6, and 3.11 with 3.11 being the
# primary version, you would execute ``make install`` in your 3.11 build directory
# and ``make altinstall`` in the others.


__author__              = "ullix"
__copyright__           = "Copyright 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024"
__credits__             = [""]
__license__             = "GPL3"

import os, sys, subprocess, platform, pathlib, shutil
import gglobs as g                                  # import all global vars

# colors
TDEFAULT                = '\033[0m'                 # default, i.e greyish
TRED                    = '\033[91m'                # red
BRED                    = '\033[91;1m'              # bold red
TGREEN                  = '\033[92m'                # light green
BGREEN                  = '\033[92;1m'              # bold green
TYELLOW                 = '\033[93m'                # yellow
TCYAN                   = '\033[96m'                # cyan


class globalvars():
    """Variables to use globally"""

    # Status:  Jan 2, 2024 (produced with GeigerLog tool ''PipCheck.sh'')
    # GeigerLog installed 'REQUIRED, BASE' packages and their versions
    # pip                 FOUND  : 23.3.2            REQUIRED, BASE
    # setuptools          FOUND  : 69.0.3            REQUIRED, BASE
    # PyQt5               FOUND  : 5.15.10           REQUIRED, BASE
    # PyQt5-sip           FOUND  : 12.13.0           REQUIRED, BASE
    # matplotlib          FOUND  : 3.8.2             REQUIRED, BASE
    # numpy               FOUND  : 1.26.2            REQUIRED, BASE
    # scipy               FOUND  : 1.11.4            REQUIRED, BASE
    # soundfile           FOUND  : 0.12.1            REQUIRED, BASE
    # sounddevice         FOUND  : 0.4.6             REQUIRED, BASE
    # pyserial            FOUND  : 3.5               REQUIRED, BASE
    # paho-mqtt           FOUND  : 1.6.1             REQUIRED, BASE
    # psutil              FOUND  : 5.9.7             REQUIRED, BASE
    # ntplib              FOUND  : 0.4.0             REQUIRED, BASE
    # py-cpuinfo          FOUND  : 9.0.0             REQUIRED, BASE

    # GeigerLog installed 'OPTIONAL' packages and their versions
    # RPi.GPIO            MISSING:                   OPTIONAL, required for RaspiPulse Series.         Install ONLY on Raspberry Pi Computer!
    # smbus2              MISSING:                   OPTIONAL, required for RaspiI2C Series.           Install ONLY on Raspberry Pi Computer!
    # LabJackPython       FOUND  : 2.1.0             OPTIONAL, required for LabJack Series
    # pip-check           FOUND  : 2.8.1             OPTIONAL, recommended Pip tool
    # python-telegram-bot FOUND  : 13.15             OPTIONAL, required for Telegram Messenger         MUST remain on version 13.15
    # urllib3             FOUND  : 2.1.0             OPTIONAL, required for Telegram Messenger

    # Checking for available updates ...

    # GeigerLog installed 'REQUIRED, BASE' packages having upgrades available:
    # Package             Version           Latest     Type
    # <None>

    # GeigerLog installed 'OPTIONAL' packages having upgrades available:
    # Package             Version           Latest     Type
    # python-telegram-bot 13.15             20.7       wheel


    # *********************
    # ***** WARNINGS: *****
    # *********************
    #   numpy  - Do NOT use numpy 1.25.0 or 1.25.1 as there is a bug!!!   Use older 1.24.4, or later 1.26.1 and 1.26.2
    #   smbus  - dead project? - last update: 8. März 2019 to version '1.1.post2'
    #   smbus2 - alive project - last update 25. Aug. 2023 to version: 0.4.3
    #
    #   seen on Raspi 4:
    #      pyserial           version: 3.5b0    # ?3.5b0 is < 3.5 ???    pyserial== (from versions: 2.3, 2.4, 2.5, 2.6, 2.7, 3.0, 3.0.1, 3.1, 3.1.1, 3.2, 3.2.1, 3.3, 3.4, 3.5b0, 3.5)
    #
    #   seen on Raspi 5:
    #      RPi.GPIO           version: 0.7.1a4
    #      smbus2             version: 0.4.2
    #   new needed for Raspi 5:
    #      rpi-lgpio          version: 0.4



###
### Linux install: python3-venv must have been installed
### matplotlib 3.5.0 konnte NICHT installiert werden - auch nicht manuell - aber 3.6.0 konnte ???
### libportaudio2 musste manuell installiert werden
#   dev_gmc: 3896 cfgkeyhi(rtc offset is None, not string)
#            2507: lcb5.setEnabled(g.GMC_FETenabled) None, not string###

# NOTE: "PyQt5" in versions 5.15.2 bis 5.15.9 gibt Depreaction warning (somewhere)
#       erst mit 5.15.10 ist Ruhe!
# war da nicht ein Raspi Problem mit version 5.15.10???

    GLinstalls_Base = {
        # name                     version       comment                                         # purpose
        "pip"                   : [[23,  3,  2], "required, Base"],                              # module handling
        "setuptools"            : [[69,  0,  3], "required, Base"],                              # module handling
        "PyQt5"                 : [[ 5, 15,  2], "required, Base"],                              # GUI
        "PyQt5-sip"             : [[12,  8,  1], "required, Base"],                              # GUI
        # "matplotlib"            : [[ 3,  5,  0], "required, Base"],                            # plotting  # all before 3.5.0 does NOT build???
        "matplotlib"            : [[ 3,  8,  3], "required, Base"],                              # plotting  # 3.5.0 also did NOT build; 3.8.3 did (on AMD MiniPC)


        "numpy"                 : [[ 1, 26,  2], "required, Base"],                              # math and stats
        "scipy"                 : [[ 1, 10,  1], "required, Base"],                              # math and stats

        "soundfile"             : [[ 0, 12,  1], "required, Base"],                              # Sound playing, bips and nurps
                                                                                                 # on Linux Mint 21 Vanessa I got no sound with  0.11.0!
        "sounddevice"           : [[ 0,  4,  6], "required, Base"],                              # Sound making / playing, AudioCounter Series

        "pyserial"              : [[ 3,  5,   ], "required, Base"],                              # Serial Port for GMC, GammaScout, I2C, Ambiomon, Pulse
                                                                                                 # platformio 6.1.11 requires pyserial==3.5.* !!!

        "paho-mqtt"             : [[ 1,  6,  1], "required, Base"],                              # mqtt for IoT Series, RadMon Series
        "psutil"                : [[ 5,  8,  0], "required, Base"],                              # system details (CPU, Memory, ...)
        "ntplib"                : [[ 0,  3,  4], "required, Base"],                              # Network Time Protocol Check
        "py-cpuinfo"            : [[ 9,  0,  0], "required, Base"],                              # CPU info

        "bmm150"                : [[ 0,  2,  2], "required, Base"],                              # Handling I2C BMM150 Geomagnetic device


        "LabJackPython"         : [[ 2,  1,  0], "optional, required for LabJack Series"],       # required for LabJack device
        # "python-telegram-bot"   : [[13, 15,   ], "optional, required for Telegram Messenger"],   # required for using Telegram; MUST (!!!) stay at version 13.15
        # "urllib3"               : [[ 2,  1,  0], "optional, required for Telegram Messenger"],   # required for using Telegram; also elsewhere???
        "pip-check"             : [[ 2,  8,  1], "optional, recommended tool for Pip"],          # convenient tool
    }

    GLinstalls_Raspi = {
        "RPi.GPIO"              : [[ 0,  7,  1], "optional, required for RaspiPulse Series - install ONLY on Raspberry Pi Versions 1,2,3,4"   ], # reading Raspi pins
        "smbus2"                : [[ 0,  4,  3], "optional, required for RaspiI2C Series   - install ONLY on Raspberry Pi"   ], # improved alternative to smbus
    }

    GLinstalls_Raspi5 = {
        "rpi-lgpio"             : [[ 0,  4,   ], "optional, required for RaspiPulse Series - install ONLY on Raspberry Pi Version 5"   ], # reading Raspi pins
        "smbus2"                : [[ 0,  4,  3], "optional, required for RaspiI2C Series   - install ONLY on Raspberry Pi"   ], # improved alternative to smbus
    }

    GLinstalls              = GLinstalls_Base
    pythonexec              = sys.executable        # getting the full path to Python in venv
                                                    # like: pythonexec:  /home/ullix/geigerlog/geigerlog/venvGL/bin/python3
    pipdict                 = {}
    devel                   = True
    setup                   = False
    computer                = "Undefined"

### end of class globalvars()

# instantiate globalvars for this script only
gv = globalvars


######################################################################################################

def clearTerminal():
    """clear the terminal"""

    # os.name:  "posix" (on Linux), "nt" on Windows
    # gprint("os.name: ", os.name)
    # 'clear' for posix, 'cls' for Windows
    os.system('cls' if os.name == 'nt' else 'clear')


def removeModules(myremoves):
    """###CAREFUL! -- this may remove all modules except pip and setuptools ###################################"""

    defname = "removeModules: "

    gprint("\nRemoving Python Modules - but keeping pip and setuptools")

    for pname in gv.GLinstalls:
        gprint("module: {:20s} :".format(pname), end="")
        if pname == "pip" or pname == "setuptools":
            gprint("don't kill yourself! - keeping:", pname)
            continue
        elif pname in myremoves:
            gprint("uninstall: ", pname)
            pip_output = subprocess.run([gv.pythonexec, '-m', 'pip', 'uninstall', '-y', pname], capture_output=True)
            for a in pip_output.stdout.decode('UTF-8').strip().split("\n"):
                gprint(" "*8 + a)
            gprint()
        else:
            gprint("keeping:   ", pname)

    return False


def getPyVersionOk():
    """
    Check for sufficient Python version;
    currently (2023-12-10) at least Py 3.8 is needed
    """

    svi          = sys.version_info       # this Python's version
    minPyVersion = (3, 8)                 # needed at least

    if svi < minPyVersion:
        msg = """
            The current GeigerLog program requires Python in version {}.{} or
            later, but your Python version is only: {}.{}.{}.

            You can download a new version of Python from:
            https://www.python.org/downloads/

            The preferred way is to upgrade your Python. If you can't do that,
            you can download an older copy of GeigerLog, which still runs on your
            old Python version, from: https://sourceforge.net/projects/geigerlog/.

            Check the respective GeigerLog manuals to see which Python versions
            can be used.

            The last version of GeigerLog for Python 2 is GeigerLog 0.9.06.
            All later versions are only for Python 3.
            """.format(*minPyVersion, *svi)

        gprint(msg)
        return False
    else:
        return True


def is_raspberrypi():
    """check if it is a Raspberry Pi computer"""

    defname = "is_raspberrypi: "

    g.RaspiVersion = 0
    g.RaspiModel   = "Not a Raspi"

    try:
        with open('/sys/firmware/devicetree/base/model', 'r') as m:
            g.RaspiModel = m.read().strip().replace("\x00", "")         # apparently a C string; must remove \x00 ending

        mread = g.RaspiModel.lower()
        # gprint("Raspi Model: ", g.RaspiModel)
        if   'raspberry pi 5' in mread:   g.RaspiVersion = 5            # on Raspi 5: 'Raspberry Pi 5 Model B Rev 1.0'
        elif 'raspberry pi 4' in mread:   g.RaspiVersion = 4
        elif 'raspberry pi 3' in mread:   g.RaspiVersion = 3            # on Raspi 3: 'Raspberry Pi 3 Model B Plus Rev 1.3'
        elif 'raspberry pi 2' in mread:   g.RaspiVersion = 2
        elif 'raspberry pi 1' in mread:   g.RaspiVersion = 1
        else: return False

    except Exception as e:
        # gprint("    This is not a Raspberry Pi computer")
        # gprint("    This is a regular computer")
        return False

    gprint("    This is a Raspberry Pi computer, model:", g.RaspiModel)

    return True


def createPipCommand(pname, latest=False):
    """Create a pip command for install with/without update"""

    if latest:
        # '-U' for update
        pipcmd = [gv.pythonexec, '-m', 'pip', 'install', '-U', pname]

    else:
        # forcing predefined version (as part of pname, like: '==1.2.3')
        pipcmd = [gv.pythonexec, '-m', 'pip', 'install',       pname]

    return pipcmd


def executePipCommand(command):
    """Execute any command on shell"""

    gprint("    Installing with Command:", command)
    gprint("                           :", " ".join(c for c in command))

    pip_output = subprocess.run(command, capture_output=True)
    # gprint("    pipoutput: ", pip_output, "  on command:", command)

    for pipout in pip_output.stdout.decode('UTF-8').split("\n"):
        gprint("    pipout: " + pipout)

    if pip_output.stderr > b"":
        gprint(TRED + "    ERROR or WARNING on pip-install" + TDEFAULT)

        for piperr in pip_output.stderr.decode('UTF-8').split("\n"):
            gprint("    piperr: " + piperr)

    if pip_output.returncode == 0:
        gprint(TGREEN + "    Sussessful" + TDEFAULT + "\n")
        return True
    else:
        gprint(TRED   + "    FAILURE"    + TDEFAULT + "\n")
        return False


def showPipList(piplist):
    """prints all from 'pip list'output"""

    gprint("Listing of all Pip-found packages:")

    for pl in piplist:  gprint("  ", pl)


def showPackages():
    """call pip list and search for required or optional packages and their version"""

    gprint("\nPython packages for GeigerLog and their versions")

    installs = gv.GLinstalls

    pf = "   {:19s} {:16s}: {:16s}"
    for modul in installs:
        #gprint("modul: ", modul)
        if modul in gv.pipdict:
            gprint(pf.format(modul, "Found installed",  gv.pipdict[modul]))
        else:
            gprint(pf.format(modul, "MISSING",          "",              ))


# def removeSpaces(text):
#     """no more than single space allowed"""

#     while True:
#         text2 = text.replace("  ", " ")           # replace 2 spaces with 1 space
#         if len(text2) < len(text): text = text2
#         else:                      return text2


def installLatestModulesAll():
    """update all modules which can be updated to the latest"""

    defname = "installLatestModulesAll: "

    gprint(TCYAN + "Updating modules to their latest version" + TDEFAULT)

    gprint("\nModule Status:")
    for pname in gv.GLinstalls:
        gprint("Module: {:20s}".format(pname))

        # handle Telegram:
        # module = pname
        # if pname == "python-telegram-bot":
        #     gprint(TRED + "    Version MUST stay frozen at 13.15!" + TDEFAULT)
        #     module = pname + "==13.15"

        pipcmd  = createPipCommand(pname, latest=True)
        success = executePipCommand(pipcmd)

    return success


def installLatestModules():
    """update only 'pip' and 'setuptools' as the latest version"""

    defname = "installLatestModules: "

    gprint(TCYAN + "Updating modules 'Pip' and 'setuptools' to their latest version" + TDEFAULT)

    gprint("\nModule Status:")
    for pname in ("pip", "setuptools"):
        gprint("Module: {:20s}".format(pname))

        pipcmd = [gv.pythonexec, '-m', 'pip', 'install', '-U', pname]
        success = executePipCommand(pipcmd)

    return success


def getPipList():
    """get and return 'pip list'"""

    pip_output = subprocess.check_output([gv.pythonexec, '-m', 'pip', 'list'])
    piplist    = pip_output.decode('UTF-8').strip().split("\n")
    # for pl in piplist:  gprint("  ", pl)

    for pl in piplist:
        snr = pl.split(" ", 1)
        # gprint("snr: ", snr)
        gv.pipdict.update({snr[0].strip(): snr[1].strip()})

    return piplist


def checkForRPi_GPIO():
    pip_output = subprocess.check_output([gv.pythonexec, '-m', 'pip', 'list'])
    smodule = b"RPi.GPIO"
    if smodule in pip_output:
        # gprint("Did find ", smodule)
        return True
    else:
        # gprint("Did NOT find ", smodule)
        return False


def getPlatform():
    """get computer"""

    # Python Doc: Returns the system/OS name, such as 'Linux', 'Darwin', 'Java', 'Windows'.
    #             An empty string is returned if the value cannot be determined.

    myplatform  = platform.system().upper()

    if "LINUX" in myplatform:
        g.isRaspi = False
        if is_raspberrypi():                                    # checking for Raspi
                                    g.isRaspi = True
                                    computer  = g.RaspiModel    # like: on Raspi 5: 'Raspberry Pi 5 Model B Rev 1.0'
        else:                       computer  = "Linux"
    elif "WINDOWS" in myplatform:   computer  = "Windows"
    elif "DARWIN"  in myplatform:   computer  = "Mac"
    else:                           computer  = "Unknown"

    return computer


def installDefaultModules():
    """
    Checks for complete installation and installs modules where needed
    return: True on success
            False on failure
    """

    defname = "installDefaultModules: "

    needInstall = {}

    # check which modules need update
    gprint("Checking Module Installation:")

    getPipList()

    gprint("    Module Status:")
    for pname in gv.GLinstalls:
        gprint("        Module: {:20s}".format(pname), end="   ")
        minversion = ".".join(str(x) for x in gv.GLinstalls[pname][0])

        if pname in gv.pipdict:                                     # does the key == modul exist?
            pipv = gv.pipdict[pname]
            # gprint("pipv: ", pipv)                                 # pipv:  23.3.2

            lnpipv = []                                             # holder for list of numbers
            for i, tt in enumerate(pipv.split(".")):                # convert to list of numbers if possible
                try:    lnpipv.append(int(tt))
                except: lnpipv.append(tt.strip())                   # does seem to contain alphanumerics
            # gprint("\n  pipv: ", pipv, "  lnpipv: ", lnpipv)

            gprint("Installed Version: {:15s}  Min Version: {:15s}".format(pipv, minversion), end=" ")

            checklen = min (len(lnpipv), len(gv.GLinstalls[pname][0]))
            needUpdate = False
            # gprint()
            for i in range(checklen):
                # gprint("i:{}   found: {}    need: {}".format(i, lnpipv[i], gv.GLinstalls[pname][0][i]))
                if isinstance(lnpipv[i], (int, float)) and isinstance(gv.GLinstalls[pname][0][i], (int, float)):
                    if lnpipv[i] < gv.GLinstalls[pname][0][i]:
                        needUpdate = True
                        break
                    if lnpipv[i] > gv.GLinstalls[pname][0][i]:
                        needUpdate = False
                        break
                else:
                    needUpdate = True
                    break

            if needUpdate:
                gprint("{:10s}".format(": Needs version {:10s}".format(minversion)), end="")
                needInstall.update({pname : True})
            else:
                gprint("{:10s}".format(": Ok"), end="")

        else: # pname NOT found in gv.pipdict
            gprint("Installed Version: {:15s}  Min Version: {:15s} {:10s}".format("None", minversion, ": MISSING"), end=" ")
            needInstall.update({pname : True})

        # # add msg to printout - only for python-telegram-bot
        # if pname == "python-telegram-bot":
        #     # gprint(pipv, "  ", minversion, end="  -  ")
        #     if pipv != minversion:
        #         needInstall.update({pname : True})
        #         gprint("{:10s}".format(": Needs version {:10s}".format(minversion)), end="")
        #     gprint("NOTE: Module '" + pname + "' MUST stay frozen at version 13.15", end="")

        gprint()


    if len(needInstall) == 0:
        # nothing needs to be installed
        print(TGREEN + "Installation is complete; no errors." + TDEFAULT)
        success = True

    else:
        # needs one or more installs
        gprint(TCYAN + "Some modules need installation or update:" + TDEFAULT)
        failures = 0
        for pname in needInstall:
            gprint("Module: {:20s}".format(pname), end="   ")
            pnameversion = ".".join(str(x) for x in gv.GLinstalls[pname][0])
            gprint("    Forcing Version: " + pnameversion)
            pipcmd  = createPipCommand(pname + "==" + pnameversion)
            failures += not (executePipCommand(pipcmd))

        if failures == 0:
            print(TCYAN + "Installation is now complete; no errors." + TDEFAULT)
            success = True
        else:
            gprint(TRED + "Installation or update had errors; cannot continue!")
            gprint("Please, verify installation manually.")
            gprint("This GeigerLog tool 'PipCheck.sh' or 'PipCheck.bat' may be of help.")
            gprint(TDEFAULT)
            success = False

    return success


def gprint(*stuff, end="\n"):
    if gv.devel:     print(*stuff, end=end)


def main():

    # setup mode
    # print("sys.argv: ", sys.argv)
    if len(sys.argv) > 1 and "setup" in sys.argv[1]: gv.setup = True


    # check Python version
    PyVersionOk = getPyVersionOk()
    if not PyVersionOk: return False


    # checking for computer type
    gprint("Checking for computer type")
    gv.computer = getPlatform()
    gprint(f"    This is a {gv.computer} computer")


    # checking for venv
    if sys.prefix != sys.base_prefix:
        g.isSetVenv     = True
        g.VenvName      = pathlib.Path(sys.prefix).parts[-1]
        # print("main: ", "g.VenvName: ", g.VenvName)
        g.VenvMessage   = f"Yes, running within venv: '{g.VenvName}'"
    else:
        g.VenvMessage   = "No, NOT running from a venv"


    # show pip list only
    if "piplist" in sys.argv:
        gprint("\nPIP Listing of available Python Modules")
        piplist = getPipList()
        for pl in piplist:  gprint("  ", pl)
        return False


    # remove modules
    elif "remove" in sys.argv:
        myremoves  = ("numpy", "psutil", "urllib3", "pyserial", "paho-mqtt", "matplotlib")  # limit the deletions to these modules
        myremoves  = ("psutil", "urllib3", "pyserial", "paho-mqtt", )                       # limit the deletions to these modules
        # myremoves  = gv.GLinstalls                                                        # alles (ausser pip und setuptools)
        removeModules(myremoves)
        return False


    # update to latest modules
    # CAUTION - better to NOT use - may result in conflicting versions!
    elif "latest" in sys.argv:
        success = installLatestModulesAll()


    # doing default install
    else:
        success = True
        if gv.setup:
            gprint("Checking System")
            gprint("    Computer type:       ", gv.computer)
            gprint("    Python version:      ", "{}.{}.{}".format(*sys.version_info))
            gprint("    Python executable:   ", gv.pythonexec)
            gprint("    Virtual Environment: ", g.VenvMessage)
            gprint("        sys.base_prefix: ", sys.base_prefix)
            gprint("        sys.prefix:      ", sys.prefix)
            gprint()

            success = installLatestModules()
            success = installDefaultModules()  # install GeigerLog-specified module minimal versions

    gprint()
    return success


#####################################################################################################
if __name__ == '__main__':
    try:
        success = main()
        if success:
            if gv.setup:
                try:
                    progDir           = os.path.dirname(os.path.realpath(__file__))                 # /home/ullix/geigerlog/geigerlog
                    configDir         = g.configDirectory                                           # "gconfig"
                    settingsFile      = os.path.join(progDir, configDir, "geigerlog.settings")      # /home/ullix/geigerlog/geigerlog/gconfig/geigerlog.settings
                    configFile        = os.path.join(progDir, configDir, "geigerlog.cfg")           # /home/ullix/geigerlog/geigerlog/gconfig/geigerlog.cfg
                    configFileDefault = os.path.join(progDir, configDir, ".geigerlog.DEFAULT.cfg")  # hidden!

                    # print("progDir:           ", progDir)
                    # print("configDir:         ", configDir)
                    # print("settingsFile:      ", settingsFile)
                    # print("configFile:        ", configFile)
                    # print("configFileDefault: ", configFileDefault)

                    # remove settingsFile
                    if os.path.exists(settingsFile):
                        os.remove(settingsFile)

                    # recreate config file from file "geigerlog.DEFAULT.cfg"
                    if os.path.exists(configFileDefault):
                        shutil.copy2(configFileDefault, configFile)

                except Exception as e:
                    exc_type, exc_obj, exc_tb = sys.exc_info()
                    if exc_tb is None:
                        fname  = "'filename unknown'"
                        lineno = "'lineno unknown'"
                    else:
                        fname  = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]    # which file?
                        lineno = exc_tb.tb_lineno
                    print("EXCEPTION: {} (e:'{}') in file: {} in line: {}".format("resetting config", e, fname, lineno))

                if gv.computer == "Windows":   command = "GeigerLog.bat"
                else:                          command = "./GeigerLog.sh"
                gprint("GeigerLog has been set up. From now on start GeigerLog with: {}".format(BGREEN + command + TDEFAULT))
            else:
                # continue to GeigerLog main program
                import gmain
                status = gmain.main()

    except KeyboardInterrupt:
        gprint()
        gprint("Exit by CTRL-C")
        gprint()

