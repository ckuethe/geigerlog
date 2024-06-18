#! /usr/bin/env python3
# -*- coding: utf-8 -*-

"""
rdev_pulse.py - DataServer's Pulse device handler

include in programs with:
    import rdev_pulse
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

from   rutils   import *


def initPulse():
    """Initialize Pulse Counter"""

    global GPIO     # needed in terminatePulse

    defname = "initPulse: "
    dprint(defname)
    setIndent(1)

    # check PulseVariables
    if g.PulseVariables == "auto" : pv = "CPM, CPS"
    else:                           pv = g.PulseVariables
    g.PulseVariables = []
    for vname in pv.split(","):
        pvar = vname.strip()
        if pvar in g.PulseVarsAll:
            g.PulseVariables.append(pvar)
        else:
            edprint("ERROR: '{}' is not a possible variable for Pulse.".format(pvar))
            edprint("Allowed is: {}".format(g.PulseVarsAll))
            setIndent(0)
            return "ERROR"

    try:
        import RPi.GPIO as GPIO         # can be imported ONLY on Raspi, fails elsewhere

    except ImportError as ie:
        msg  = "The module 'RPi.GPIO' was not found but is required."
        msg += "\nInstall with: 'python -m pip install -U rpi-lgpio'"
        exceptPrint(ie, msg)
        setIndent(0)
        return msg

    except Exception as e:
        msg = "Unexpected failure on importing 'RPi.GPIO'"
        exceptPrint(e, msg)
        setIndent(0)
        return msg

    else:
        g.versions["GPIO"] = GPIO.VERSION
        rdprint(defname, "GPIO.VERSION: ", g.versions["GPIO"])

    try:
        # to eliminate warnings on "already in use channel" when, due to
        # an exception, crash cleanup had not been done
        GPIO.setwarnings(False)

        # using BCM mode; use GPIO.setmode(GPIO.BOARD) for boardpin usage
        GPIO.setmode(GPIO.BCM)


        # configure PWM
        if g.PWM_usage:
            rdprint("-"*200)
            rdprint("rglobs: Duty cycle: ", g.PWM_DutyCycle)
            rdprint("-"*200)

            GPIO.setup(g.PWM_Pin, GPIO.OUT)                      # define PWM_Pin as output
            g.PWM_Handle = GPIO.PWM(g.PWM_Pin, g.PWM_Freq)         # set PWM at pin and freq; PWM is not precise
            g.PWM_Handle.start(g.PWM_DutyCycle)                   # start, includes setting duty cycle
            # g.PWM_Handle.ChangeDutyCycle(10)                   # (0.0 ... 100.0)
            # g.PWM_Handle.ChangeFrequency(freq)                 # frequency (min: > 1.0; max: is ???)
            # g.PWM_Handle.ChangeFrequency(0)                 # frequency (min: > 1.0; max: is ???)

        # configure Pulse counting
        ## set falling edge
        ## GPIO.setup(g.PulseCountPin, GPIO.IN, pull_up_down = GPIO.PUD_UP)
        ## GPIO.add_event_detect(g.PulseCountPin, GPIO.FALLING, callback=incrementPulseCounts)
        #
        # set rising edge
        GPIO.setup(g.PulseCountPin, GPIO.IN, pull_up_down = GPIO.PUD_DOWN)
        GPIO.add_event_detect(g.PulseCountPin, GPIO.RISING, callback=incrementPulseCounts)   # counting starts!

        dprint("Pulse Settings:")
        dprint("   {:24s} : {}"   .format("RPi.GPIO Version"       , g.versions["GPIO"]))
        dprint("   {:24s} : {}"   .format("Pin Mode"               , "GPIO.BCM"))
        dprint("   {:24s} : {}"   .format("Pulse BCM Pin #"        , g.PulseCountPin))
        dprint("   {:24s} : {}"   .format("Pulse Pull up / down"   , "GPIO.PUD_DOWN"))
        dprint("   {:24s} : {}"   .format("Pulse Edge detection"   , "GPIO.RISING"))
        dprint("   {:24s} : {}"   .format("PWM Pin "               , g.PWM_Pin))
        dprint("   {:24s} : {} %" .format("PWM Duty Cycle "        , g.PWM_DutyCycle))
        dprint("   {:24s} : {} Hz".format("PWM Frequency "         , g.PWM_Freq))

        # set start time
        g.PulseCountStart           = time.time()

        # add first CPS value to 60 sec store
        time.sleep(1)                                   # let counts accumulate for 1 sec, before ...
        g.PulseStore.append(getValPulse())              # ... filling first value

        g.PulseInit = True

    except Exception as e:
        exceptPrint(e, defname)
        return "Failure"

    setIndent(0)

    return "Ok"


def terminatePulse():
    """shuts down the pulse counter; cleanup is important!"""

    defname = "terminatePulse: "

    try:
        GPIO.remove_event_detect(g.PulseCountPin)
        rdprint(defname, "remove event done")
        if g.PWM_usage:  g.PWM_Handle.stop()
        GPIO.cleanup()  # cleans up only the channels used by THIS program
        rdprint(defname, "cleanup done")
    except Exception as e:
        exceptPrint(e, defname + "Failure in GPIO actions")

    return "Terminate Pulse: Done"


def resetPulse():
    """Reset the Pulse counter"""

    defname = "resetPulse: "
    dprint(defname)
    setIndent(1)

    resetresp = "Ok"

    g.PulseStore.clear()                                  # clear deque
    g.PulseCountStart = time.time()                       # reset to "now"
    g.PulseCountTotal = 0
    g.PulseCount      = 0

    # get the first value to store
    time.sleep(1)                                         # collect pulses for 1 sec before ...
    g.PulseStore.append(getValPulse())                    # ... filling first value

    setIndent(0)
    return resetresp


def incrementPulseCounts(BCMpin):
    """increment Pulse counter"""
    # NOTE: BCMpin is the PulseCountPin as BCM pin number (e.g.: 17)

    # print("incrementPulseCounts called, PulseCount: ", g.PulseCount)
    # print("incrementPulseCounts called, BCMpin: ", BCMpin)

    g.PulseCount += 1


def getValPulse():
    """gets the CPS Pulses and resets counts to zero"""
    # on Raspi:      3 ...  5 mikro sec (!)

    start   = time.time()
    defname = "getValPulse: "

    lcl_PulseCount      = g.PulseCount
    g.PulseCount        = 0
    g.PulseCountTotal  += lcl_PulseCount

    dur = 1000 * (time.time() - start)
    vprint("- {:17s}{}:{:5.0f}  (dur:{:0.3f} ms)".format(defname, "CPS", lcl_PulseCount, dur))

    return lcl_PulseCount


def getCPSPulse():
    """get last CPS counts and return as value"""

    return g.PulseStore[-1]


def getCPMPulse():
    """get CPM counts and return as value"""

    # rdprint("getCPMPulse: ", len(g.PulseStore), "  ", g.PulseStore)
    lenstore = len(g.PulseStore)

    if   lenstore == 60: CPM = sum(g.PulseStore)
    elif lenstore <= 3:  CPM = g.NAN                                            # return CPM=NAN if there are no more than 3 CPS values
    else:                CPM = int(round(sum(g.PulseStore) / lenstore * 60, 0)) # estimate CPM from less than 60 CPS for the first 1 min

    return CPM


def getDataPulse():
    """get the data from Pulse"""

    start     = time.time()
    defname   = "getDataPulse: "
    PulseDict = {}
    M         = getCPMPulse()
    S         = getCPSPulse()
    for vname in g.PulseVarsAll:
        # edprint(defname, "vname: ", vname)
        if vname in g.PulseVariables:
            # rdprint(defname, "vname: ", vname)
            if   "CPM" in vname:  PulseDict.update({vname: M})
            elif "CPS" in vname:  PulseDict.update({vname: S})

    dur = 1000 * (time.time() - start)
    dprint(defname + "{}  dur: {:0.3f} ms".format(PulseDict, dur))

    return PulseDict

