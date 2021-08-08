#! /usr/bin/env python3
# -*- coding: utf-8 -*-

"""
GLpipcheck.py - To check Pip version status of GeigerLog requirements
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
__version__         = "1.1"


"""
optional for pip:
to force installation limited to certain versions:
   pip install SomeProject >=1,<2

To view all available packages, this is NO LONGER working!
    python -m pip install pip==

Workaraound:
    python -m pip --use-deprecated=legacy-resolver install pip==
"""


import sys, subprocess


def removeSpaces(text):
    """no more than single space allowed"""

    while True:
        text2 = text.replace("  ", " ")           # replace 2 space with 1 space
        if len(text2) < len(text): text = text2
        else:                      return text2


def showPipList(piplist):
    """prints all from 'pip list'output"""

    print("Listing of all Pip-found packages:")

    for pl in piplist:  print("  ", pl)


def showPackages(ptype):    # ptype = "OPTIONAL" or "REQUIRED"
    """call pip list and find packages required by GeigerLog and their version"""

    print("\nGeigerLog {} packages and their version status".format(ptype))

    if ptype == "REQUIRED":  installs = req_installs
    else:                    installs = opt_installs

    pf = "   {:18s} {:16s}  {:10s} {}"
    for ins in installs:
        #print("ins: ", ins)
        if ins in pipdict:
            print(pf.format(ins, pipdict[ins], "OK",      installs[ins][1]))
        else:
            print(pf.format(ins, ""          , "MISSING", installs[ins][1]))


def showVersionFromPipOutdatedList(ptype): # ptype = "OPTIONAL" or "REQUIRED"
    """Call 'pip list --outdated' """

    """
    Example output of call 'pip list --outdated':
    Package Version Latest Type
    ------- ------- ------ -----
    cffi    1.14.2  1.14.4 wheel
    idna    2.10    3.1    wheel
    """

    msg = "\nGeigerLog {} packages having upgrades available:".format(ptype)

    if ptype == "REQUIRED":  installs = req_installs
    else:                    installs = opt_installs

    pf       = "   {:18s} {:16s}  {:10s} {}"

    counter  = 0
    ins      = "Package"
    print(msg)
    print(pf.format(ins, pipODdict[ins][0], pipODdict[ins][1], pipODdict[ins][2]))
    for ins in installs:
        #print("ins: ", ins)
        if ins in pipODdict:
            print(pf.format(ins, pipODdict[ins][0], pipODdict[ins][1], pipODdict[ins][2]))
            counter += 1
    if counter == 0: print("   None")


###############################################################################

def main():
    """
    # February 2021:
        GeigerLog REQUIRED packages and their version status
           pip                21.0.1            OK
           setuptools         53.0.0            OK
           PyQt5              5.15.2            OK
           PyQt5-sip          12.8.1            OK
           numpy              1.20.0            OK
           scipy              1.6.0             OK
           matplotlib         3.3.4             OK
           sounddevice        0.4.1             OK
           SoundFile          0.10.3.post1      OK

        GeigerLog OPTIONAL packages and their version status
           pyserial           3.5               OK         REQUIRED for GMC, GS, I2C Series
           paho-mqtt          1.5.1             OK         REQUIRED for RadMon Series
           LabJackPython      2.0.0             OK         REQUIRED for LabJack Series
           pip-check          2.6               OK         recommended Pip tool

        GeigerLog REQUIRED packages having upgrades available:
           Package            Version           Latest     Type
           None

        GeigerLog OPTIONAL packages having upgrades available:
           Package            Version           Latest     Type
           LabJackPython      2.0.0             2.0.4      wheel
    """

    global req_installs, opt_installs, pipdict, pipODdict

    print("\n---------------------- GLpipcheck.py ---------------------------")
    print("Python Executable: ", sys.executable)
    print("Python Version:    ", sys.version.replace('\n', " "))
    print()

    req_installs = {
                "pip"           : ["latest"     , "", False],
                "setuptools"    : ["latest"     , "", False],
                "PyQt5"         : ["latest"     , "", False],
                "PyQt5-Qt"      : ["latest"     , "", False],
                "PyQt5-sip"     : ["latest"     , "", False],
                "numpy"         : ["latest"     , "", False],
                "scipy"         : ["latest"     , "", False],
                "matplotlib"    : ["latest"     , "", False],
                "sounddevice"   : ["latest"     , "", False],
                "SoundFile"     : ["latest"     , "", False],
                }

    opt_installs = {
                "pyserial"      : ["latest"     , "REQUIRED for GMC, GS, I2C Series", False],
                "paho-mqtt"     : ["latest"     , "REQUIRED for RadMon Series"      , False],
                "LabJackPython" : ["latest"     , "REQUIRED for LabJack Series"     , False],
                "pip-check"     : ["latest"     , "recommended Pip tool"            , False],
                }

    # create the 'pip list'
    piplist = subprocess.check_output([sys.executable, '-m', 'pip', 'list'])
    piplist = piplist.decode('UTF-8').strip().split("\n")
    #print("piplist: \n", piplist)
    showPipList(piplist)

    pipdict = {}
    for pl in piplist:
        snr = removeSpaces(pl).split(" ", 1)
        #print("snr: ", snr)
        pipdict.update({snr[0].strip(): snr[1].strip()})
    showPackages("REQUIRED")
    showPackages("OPTIONAL")


     # create the 'pip list --outdated'
    pipODlist = subprocess.check_output([sys.executable, '-m', 'pip', 'list', '--outdated'])
    pipODlist = pipODlist.decode('UTF-8').strip().split("\n")
    #print("pipODlist:", len(pipODlist), pipODlist)

    pipODdict = {}
    for pl in pipODlist:
        snr = removeSpaces(pl).split(" ", 4)
        #print("snr: ", snr)
        pipODdict.update({snr[0].strip(): [snr[1].strip(), snr[2].strip(), snr[3].strip()]})
    showVersionFromPipOutdatedList("REQUIRED")
    showVersionFromPipOutdatedList("OPTIONAL")

    ###############

    print()
    print("HOWTO: " + "-" * 80)
    print("To install and/or update package 'anypackage' use:\n      python3 -m pip install -U anypackage")
    print("To remove package 'anypackage' use:\n      python3 -m pip uninstall anypackage")
    print("To install version 1.2.3 of package 'anypackage' use:\n      python3 -m pip install anypackage==1.2.3")
    print("To find all available versions of package 'anypackage' use:\n      python3 -m pip --use-deprecated=legacy-resolver install anypackage==")
    print()


if __name__ == '__main__':
    main()
