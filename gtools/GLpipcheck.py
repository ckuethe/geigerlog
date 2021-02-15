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

"""
optional for pip:
to force installation limited to certain versions:
   pip install SomeProject >=1,<2

Using pip as an imported module:  (not recommended, see at bottom of:
https://pip.pypa.io/en/stable/user_guide/

... if you decide that you do want to run pip from within your program. The most
... reliable approach, and the one that is fully supported, is to run pip in a
... subprocess. This is easily done using the standard subprocess module

from pip._internal import main as pipmain

def install(package):
    # test for presence of 'main' (older versions) or use pip._internal.main()
    if hasattr(pip, 'main'):
        pip.main(['install', package])
    else:
        pip._internal.main(['install', package])

pipmain(["list"])
<package name> = e.g. pip, pyserial, ...
pipmain(["show", <package name>])
pipmain(["install","--upgrade", <package name>])
"""


import sys, subprocess


def removeSpaces(text):
    """no more than single space allowed"""

    while True:
        text2 = text.replace("  ", " ")
        if len(text2) < len(text):
            text = text2
        else:
            return text2


def showPipList():
    """Executes 'pip list' and prints all"""

    print("Listing of all Pip-found packages:")

    nreqs = piplist.decode('UTF-8').split("\n")
    for nr in nreqs:
        print("  ", nr)


def showInstalledPackages():
    """call pip list and find packages required by GeigerLog and their version"""

    print("\nGeigerLog required packages and their currently installed versions:")

    nreqs = piplist.decode('UTF-8').strip().split("\n")
    #print ("nreqs:", nreqs)

    print("               Package            Version")
    for nr in nreqs:
        snr = removeSpaces(nr).split(" ", 1)
        #print("snr: ", snr)

        p = snr[0].strip()
        v = snr[1].strip()
        #print("nr: >{}< >{}<".format(p, v))

        if p in installs:
            print("   installed:  {:18s} {:20s}".format(p, v))
            installs[p][2] = True
        else:
            pass
            #~print("installed but not needed: {:28s} {:20s}".format(p, v))


def showMissingPackages():
    """Packages needed by GeigerLog but not installed"""

    print("\nGeigerLog required packages missing:")
    counter = 0
    for pkg in installs:
        #print("         pkg:  {:28s}".format(pkg), pkg)
        if installs[pkg][2] == False:       # False or True is set by showInstalledPackages
            print("   missing:    {:18s}".format(pkg))
            counter += 1
        else:
            pass
            #print("         found:    {:28s}".format(pkg))

    if counter == 0: print("   None")


def showVersionFromPipOutdatedList():
    """Call 'pip list --outdated' """

    print("\nGeigerLog required packages having Upgrades available:")

    reqs  = subprocess.check_output([sys.executable, '-m', 'pip', 'list', '--outdated'])
    nreqs = reqs.decode('UTF-8').strip().split("\n")    # e.g.:  'bottle             0.12.7   0.12.17  wheel',
    #print("nreqs:", len(nreqs), nreqs)

    counter = 0
    print("               Package            Version     Latest      Type")
    for nr in nreqs:
        if len(nr) == 0: continue
        #print("nr: ", len(nr), nr)

        snr = removeSpaces(nr).split(" ", 3)
        #print(snr)

        p = snr[0].strip()
        v = snr[1].strip()
        w = snr[2].strip()
        x = snr[3].strip()
        #~print("nr: >{}< >{}< >{}<".format(p, v, w))

        if p in installs:
            print("   installed:  {:18s} {:11s} {:11s} {:20s}".format(p, v, w, x))
            counter += 1
        else:
            pass
            #~print("installed but not needed: {:28s} {:20s}".format(p,v))

    if counter == 0: print("   None")


###############################################################################

def main():
    """
    # October 9, 2020:
    GeigerLog required packages and their currently installed versions:
                   Package            Version
       installed:  matplotlib         3.3.2
       installed:  numpy              1.19.2
       installed:  paho-mqtt          1.5.1
       installed:  pip                20.2.3
       installed:  pip-check          2.6
       installed:  PyQt5              5.15.1
       installed:  PyQt5-sip          12.8.1
       installed:  pyserial           3.4
       installed:  scipy              1.5.2
       installed:  setuptools         50.3.0
       installed:  sounddevice        0.4.1
       installed:  SoundFile          0.10.3.post1
    """

    global installs, piplist

    print("\n---------------------- GLpipcheck.py ---------------------------")
    print("Python Executable: ", sys.executable)
    print("Python Version:    ", sys.version.replace('\n', " "))
    print()

    installs = {
                "pip"           : ["latest"     , "pypi", False],
                "setuptools"    : ["latest"     , "pypi", False],
                "PyQt5"         : ["latest"     , "pypi", False],
                "PyQt5-sip"     : ["latest"     , "pypi", False],
                "numpy"         : ["latest"     , "pypi", False],
                "scipy"         : ["latest"     , "pypi", False],
                "matplotlib"    : ["latest"     , "pypi", False],
                "pyserial"      : ["latest"     , "pypi", False],
                "paho-mqtt"     : ["latest"     , "pypi", False],
                "sounddevice"   : ["latest"     , "pypi", False],
                "SoundFile"     : ["latest"     , "pypi", False],
                "pip-check"     : ["latest"     , "pypi", False],
                }

    # create the 'pip list'
    piplist = subprocess.check_output([sys.executable, '-m', 'pip', 'list'])

    showPipList()
    showInstalledPackages()
    showMissingPackages()
    showVersionFromPipOutdatedList()
    print()
    print("HOWTO: To install and/or update package 'anypackage' use:\n   python3 -m pip install -U anypackage")
    print()


if __name__ == '__main__':
    main()
