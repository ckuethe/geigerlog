#! /usr/bin/env python3
# -*- coding: utf-8 -*-

"""
GLpipcheck.py - To check Pip version status of GeigerLog requirements
                is started by either 'PipCheck.sh' or 'PipCheck.bat'
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


# 2. Jan 2024:
# GeigerLog installed 'REQUIRED, BASE' packages and their versions
#    pip                 FOUND  : 23.3.2            REQUIRED, BASE
#    setuptools          FOUND  : 69.0.3            REQUIRED, BASE
#    PyQt5               FOUND  : 5.15.10           REQUIRED, BASE
#    PyQt5-sip           FOUND  : 12.13.0           REQUIRED, BASE
#    matplotlib          FOUND  : 3.8.2             REQUIRED, BASE
#    numpy               FOUND  : 1.26.2            REQUIRED, BASE
#    scipy               FOUND  : 1.11.4            REQUIRED, BASE
#    soundfile           FOUND  : 0.12.1            REQUIRED, BASE
#    sounddevice         FOUND  : 0.4.6             REQUIRED, BASE
#    pyserial            FOUND  : 3.5               REQUIRED, BASE
#    paho-mqtt           FOUND  : 1.6.1             REQUIRED, BASE
#    psutil              FOUND  : 5.9.7             REQUIRED, BASE
#    ntplib              FOUND  : 0.4.0             REQUIRED, BASE
#    py-cpuinfo          FOUND  : 9.0.0             REQUIRED, BASE

# GeigerLog installed 'OPTIONAL' packages and their versions
#    RPi.GPIO            MISSING:                   OPTIONAL, required for RaspiPulse Series.         Install ONLY on Raspberry Pi Computer!
#    smbus2              MISSING:                   OPTIONAL, required for RaspiI2C Series.           Install ONLY on Raspberry Pi Computer!
#    LabJackPython       FOUND  : 2.1.0             OPTIONAL, required for LabJack Series
#    pip-check           FOUND  : 2.8.1             OPTIONAL, recommended Pip tool
#    python-telegram-bot FOUND  : 13.15             OPTIONAL, required for Telegram Messenger         MUST remain on version 13.15
#    urllib3             FOUND  : 2.1.0             OPTIONAL, required for Telegram Messenger

# Checking for available updates ...

# GeigerLog installed 'REQUIRED, BASE' packages having upgrades available:
#    Package             Version           Latest     Type
#    <None>

# GeigerLog installed 'OPTIONAL' packages having upgrades available:
#    Package             Version           Latest     Type
#    python-telegram-bot 13.15             20.7       wheel


__author__          = "ullix"
__copyright__       = "Copyright 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024"
__credits__         = [""]
__license__         = "GPL3"
__version__         = "1.7.2"


import sys, os, subprocess
import getopt                                   # parse command line for options and commands

pythonexec = sys.executable

# colors
TDEFAULT                = '\033[0m'             # default, i.e greyish
TRED                    = '\033[91m'            # red
BRED                    = '\033[91;1m'          # bold red
TGREEN                  = '\033[92m'            # light green
BGREEN                  = '\033[92;1m'          # bold green
TYELLOW                 = '\033[93m'            # yellow

# NOTE: re: Mini-HOWTO - "Find all ..."
# Apparently this got reverted back to the original:
# Find    all available versions of package 'anypackage':      python3 -m pip --use-deprecated=legacy-resolver install anypackage==
# now again works as:
# Find    all available versions of package 'anypackage':      python3 -m pip install anypackage==

howto = """
Mini-HOWTO  for using 'pip': ----------------------------------------------------------------------------------------------

NOTE:   when 'pip' itself or 'setuptools' can be upgraded, upgrade 'pip' first, then 'setuptools', then any others
NOTE:   when using '=', '==', '>', '<' for version definition you need to use quotation marks around package designation
        like: "anypackage == 1.2.3",  "anypackage >=1, <2"
NOTE:   On some Operating Systems you may have to use 'python3' in lieu of just 'python'
NOTE:   If you want to see which modules have updates available, start with: './PipCheck.sh latest'.
        CAUTION: updating to those latest versions may result in GeigerLog NOT WORKING !  If this
                 happens, then you need to manually install the GeigerLog approved versions!

Install and/or update package 'anypackage':                  python -m pip install -U anypackage

Install and/or update multiple packages at once:             python -m pip install -U anypackage 2ndpackage 3rdpackage ...
        NOTE: On failure nothing at all may have been in-
        stalled! Continue with single-package installations.

Install package 'anypackage' in exactly version 1.2.3:       python -m pip install "anypackage == 1.2.3"

Install package 'anypackage' in version of
        at least 1 but not 2 or later:                       python -m pip install "anypackage >=1, <2"

Remove  package 'anypackage':                                python -m pip uninstall anypackage

Find    all available versions of package 'anypackage':      python -m pip install anypackage==

---------------------------------------------------------------------------------------------------------------------------
"""
###############################################################################

class localvars():
    req_installs = {
                    "pip"                     : ["REQUIRED, BASE"],
                    "setuptools"              : ["REQUIRED, BASE"],
                    "PyQt5"                   : ["REQUIRED, BASE"],
                    "PyQt5-sip"               : ["REQUIRED, BASE"],
                    "matplotlib"              : ["REQUIRED, BASE"],
                    "numpy"                   : ["REQUIRED, BASE"],
                    "scipy"                   : ["REQUIRED, BASE"],
                    "soundfile"               : ["REQUIRED, BASE"],    # in older versions it is 'SoundFile', in younger ones it is 'soundfile'
                    "sounddevice"             : ["REQUIRED, BASE"],
                    "pyserial"                : ["REQUIRED, BASE"],
                    "paho-mqtt"               : ["REQUIRED, BASE"],
                    "psutil"                  : ["REQUIRED, BASE"],
                    "ntplib"                  : ["REQUIRED, BASE"],
                    "py-cpuinfo"              : ["REQUIRED, BASE"],
                    }

    opt_installs = {
                    "RPi.GPIO"                : ["OPTIONAL, required for RaspiPulse Series.         Install ONLY on Raspberry Pi Computer Versions 1,2,3,4!"],
                    "rpi-lgpio"               : ["OPTIONAL, required for RaspiPulse Series.         Install ONLY on Raspberry Pi Computer Versions 5!"],
                    # "smbus"                 : ["OPTIONAL, required for RaspiI2C Series.           Install ONLY on Raspberry Pi Computer!"],
                    "smbus2"                  : ["OPTIONAL, required for RaspiI2C Series.           Install ONLY on Raspberry Pi Computer!"],
                    "LabJackPython"           : ["OPTIONAL, required for LabJack Series"            ],
                    "pip-check"               : ["OPTIONAL, recommended Pip tool"                   ],
                    # "python-telegram-bot"     : ["OPTIONAL, required for Telegram Messenger         MUST remain on version 13.15"          ],
                    # "urllib3"                 : ["OPTIONAL, required for Telegram Messenger"        ],       # required only for Telegram
                    }

    req_install             = []
    opt_install             = []
    pipdict                 = {}
    pipODdict               = {}

###############################################################################

# instantiate vars for this script only
lv = localvars


def removeSpaces(text):
    """no more than single space allowed"""

    while True:
        text2 = text.replace("  ", " ")           # replace 2 spaces with 1 space
        if len(text2) < len(text): text = text2
        else:                      return text2


def showPipList(piplist):
    """prints all from 'pip list'output"""

    print("Listing of all Pip-found packages:")

    for pl in piplist:  print("  ", pl)


def showPackages(ptype):    # ptype = "OPTIONAL" or "REQUIRED, BASE"
    """call pip list and search for required or optional packages and their version"""

    print("\nGeigerLog installed '{}' packages and their versions".format(ptype))

    if ptype == "REQUIRED, BASE":  installs = lv.req_installs
    else:                          installs = lv.opt_installs

    pf = "   {:19s} {:7s}: {:16s}  {}"
    for ins in installs:
        #print("ins: ", ins)
        if ins in lv.pipdict:   print(pf.format(ins, "FOUND",   lv.pipdict[ins],  installs[ins][0]))
        else:                   print(pf.format(ins, "MISSING", "",               installs[ins][0]))


def showVersionFromPipOutdatedList(ptype): # ptype = "OPTIONAL" or "REQUIRED, BASE"
    """Call 'pip list --outdated' """

    """
    Example output of call 'pip list --outdated':
    Package Version Latest Type
    ------- ------- ------ -----
    cffi    1.14.2  1.14.4 wheel
    idna    2.10    3.1    wheel
    """

    if ptype == "REQUIRED, BASE":  installs = lv.req_installs
    else:                          installs = lv.opt_installs

    pf       = "   {:19s} {:16s}  {:10s} {}"
    counter  = 0

    print("\nGeigerLog installed '{}' packages having upgrades available:".format(ptype))
    if len(lv.pipODdict) > 0:
        print("   Package             Version           Latest     Type")
        for ins in installs:
            # print("ins: ", ins)       # ins: pip, setuptools, ...
            if ins in lv.pipODdict:
                print(pf.format(ins, lv.pipODdict[ins][0], lv.pipODdict[ins][1], lv.pipODdict[ins][2]))
                counter += 1

        if counter == 0: print("   <None>")
    else:
        print("   -N.A.-")

###############################################################################

def main():

    latest = False

    # # header
    # print("\n" + BGREEN + "*" * 150 + TDEFAULT)

    # parse command line options
    # sys.argv[0] is progname
    try:
        opts, args = getopt.getopt(sys.argv[1:], "hV", ["help", "Version"])
    except getopt.GetoptError as e :
        # print info like "option -a not recognized", then exit
        msg = "\nFor Help use: ''PipCheck.sh -h' or 'PipCheck.bat -h'"
        print("ERROR: ", e, msg)
        return 1

    # processing the options
    for opt, optval in opts:
        if   opt in ("-h", "--help"):
            print(howto)
            return 0

        elif opt in ("-V", "--Version"):
            print("Version: ", __version__)
            print()
            return 0

    for arg in args:
        arg = arg.lower()
        if   arg == "latest":    latest = True  # set development mode


    print("GLpipcheck.py Version: ", __version__)
    print("Python Executable:     ", pythonexec)
    print("Python Version:        ", sys.version.replace('\n', " "))
    print()

    # create the 'pip list'
    pip_output = subprocess.check_output([pythonexec, '-m', 'pip', 'list'])
    piplist    = pip_output.decode('UTF-8').strip().split("\n")
    showPipList(piplist)

    for pl in piplist:
        snr = pl.split(" ", 1)
        # print("snr: ", snr)
        lv.pipdict.update({snr[0].strip(): snr[1].strip()})
    # print("lv.pipdict: ", lv.pipdict)

    showPackages("REQUIRED, BASE")
    showPackages("OPTIONAL")

    if latest:
        print()
        print("Checking for available updates ... ")

        # create the OD:  'pip list --outdated'
        pipOD_output = subprocess.check_output([pythonexec, '-m', 'pip', 'list', '--outdated'])
        pipODlist    = pipOD_output.decode('UTF-8').strip().split("\n")
        # print("pipODlist:", len(pipODlist), pipODlist)

        for pl in pipODlist:
            # print("pl: ", pl)
            snr = removeSpaces(pl).split(" ", 4)
            # print("snr: ", snr, "len(snr): ", len(snr))
            lv.pipODdict.update({snr[0].strip(): [snr[1].strip(), snr[2].strip(), snr[3].strip()]})
            # print("lv.pipODdict: ", lv.pipODdict)

        showVersionFromPipOutdatedList("REQUIRED, BASE")
        showVersionFromPipOutdatedList("OPTIONAL")

    print()
    print(howto)


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print()
        print("Exit by CTRL-C")
        print()
        os._exit(0)

