#! /usr/bin/env python3
# -*- coding: utf-8 -*-

"""
gdev_raspipulse.py  - GeigerLog device for counting pulses on Raspi interrupts

include in programs with:
    import gdev_raspipulse
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

from gsup_utils   import *


def initRaspiPulse():
    """Inititalize the pulse counter"""

    global GPIO, R_Mode, R_Edge, R_PUD

    defname = "initRaspiPulse: "
    dprint(defname)

    g.Devices["RaspiPulse"][g.DNAME] = "RaspiPulse"

    # configuration Raspi hardware
    if g.RaspiPulseMode        == "auto":       g.RaspiPulseMode        = "BCM"         # numbering mode: options are: GPIO.BCM or GPIO.BOARD
    if g.RaspiPulsePin         == "auto":       g.RaspiPulsePin         = 17            # hardware pin for interrupt in BCM numbering: bcmpin=17 is on boardpin=11
    if g.RaspiPulseEdge        == "auto":       g.RaspiPulseEdge        = "FALLING"     # register transistion from 0 to 3.3V; options are "GPIO.RISING" or "GPIO.FALLING"
    if g.RaspiPulseVariables   == "auto":       g.RaspiPulseVariables   = "CPM, CPS"
    if g.RaspiPulseEdge        == "FALLING":    g.RaspiPulsePullUpDown  = "PUD_UP"      # "FALLING" is matched with "GPIO.PUD_UP"
    else:                                       g.RaspiPulsePullUpDown  = "PUD_DOWN"

    if not g.isRaspi:
        # computer is NOT a Raspi
        g.RaspiGPIO_Info       = "Not a Raspi"
        g.RaspiGPIO_Version    = "Not a Raspi"
        return "Not a Raspi. The RaspiPulse Device can be run only on a Raspberry Pi computer."


    # computer is a Raspi:
    try:
        import RPi.GPIO as GPIO             # is valid for both RPi.GPIO and rpi-lgpio !!!

    except ImportError as ie:
        # module 'RPi.GPIO' not found
        msg  = "The module 'RPi.GPIO' was not found but is required!"
        msg += "\nRedo the GeigerLog setup."
        exceptPrint(ie, msg)
        # setIndent(0)
        return msg

    except Exception as e:
        # module 'RPi.GPIO' was found, but cannot be run
        msg = "Failure on Importing 'RPi.GPIO'"
        exceptPrint(e, msg)
        # setIndent(0)
        return msg

    else:
        # GPIO.RPI_INFO = {'P1_REVISION': 3, 'REVISION': 'c04170', 'TYPE': 'Pi 5 Model B',
        #                  'MANUFACTURER': 'Sony UK', 'PROCESSOR': 'BCM2712', 'RAM': '4GB'}
        g.RaspiGPIO_Info    = str(GPIO.RPI_INFO).replace("'", "").replace("{", "").replace("}", "").replace(": ", ":")
        g.RaspiGPIO_Version = GPIO.VERSION
        g.versions["GPIO"]  = g.RaspiGPIO_Version


    R_Mode   = GPIO.BCM      if g.RaspiPulseMode       == "BCM"        else GPIO.BOARD
    R_Edge   = GPIO.FALLING  if g.RaspiPulseEdge       == "FALLING"    else GPIO.RISING
    R_PUD    = GPIO.PUD_UP   if g.RaspiPulsePullUpDown == "PUD_UP"     else GPIO.PUD_DOWN

    setIndent(1)
    g.RaspiPulseVariables = setLoggableVariables("RaspiPulse", g.RaspiPulseVariables)

    # reset RaspiPulse
    resetRaspiPulse("init")

    try:
        # GPIO.setwarnings(False)   # to eliminate warnings on "already in use channel" when - due to e.g. an exception - crash cleanup had not been done
        GPIO.setwarnings(True)      # helpful to have warnings???
        GPIO.setmode    (R_Mode)
        GPIO.setup      (g.RaspiPulsePin, GPIO.IN, pull_up_down=R_PUD)

    except Exception as e:
        exceptPrint(e, "when setting GPIO")
        setIndent(0)
        return "Cannot set GPIO"

    dprint("RaspiPulse Settings:")
    ptmplt = "   {:27s} : {}"
    dprint(ptmplt.format("Raspi Computer Model"   , g.RaspiModel))
    dprint(ptmplt.format("Raspi Hardware Info"    , g.RaspiGPIO_Info))
    dprint(ptmplt.format("Raspi SW GPIO Version"  , g.RaspiGPIO_Version))
    dprint(ptmplt.format("GPIO Mode"              , g.RaspiPulseMode))
    dprint(ptmplt.format("Pulse BCM Pin #"        , g.RaspiPulsePin))
    dprint(ptmplt.format("Pulse Pull up / down"   , g.RaspiPulsePullUpDown))
    dprint(ptmplt.format("Pulse Edge detection"   , g.RaspiPulseEdge))

    g.Devices["RaspiPulse"][g.CONN] = True

    ### PWM    -  use only when pwm given on command line
    if g.RaspiPulsePWM_Active: setupRaspiPWM()


    # setup and start thread
    g.RaspiPulseThreadStopFlag = False
    g.RaspiPulseThread         = threading.Thread(target = RaspiPulseThreadTarget)
    g.RaspiPulseThread.daemon  = True
    g.RaspiPulseThread.start()
    dprint("   {:27s} : {}".format("RaspiPulseThread.daemon"      , g.RaspiPulseThread.daemon))
    dprint("   {:27s} : {}".format("RaspiPulseThread.is_alive"    , g.RaspiPulseThread.is_alive()))


    def recordCount(bcmpin):
        """for each interrupt add 1 to total CPS"""
        g.RaspiPulseCPS += 1


    ### Do NOT use bouncetime: the shortest bouncetime of 1 ms is very long compared to pulses of only 150 µs!
    GPIO.add_event_detect(g.RaspiPulsePin, R_Edge, callback=recordCount)            # without bouncetime

    setIndent(0)
    return ""


def terminateRaspiPulse():
    """shuts down the pulse counter; cleanup is important!"""

    defname = "terminateRaspiPulse: "
    dprint(defname)
    setIndent(1)

    g.RaspiPulseThreadStopFlag = True

    if GPIO is not None:
        try:                   GPIO.cleanup()
        except Exception as e: exceptPrint(e, "Failure in GPIO.cleanup")

    g.Devices["RaspiPulse"][g.CONN] = False
    resetRaspiPulse(cmd = "terminate")

    dprint(defname + "Terminated")
    setIndent(0)


def RaspiPulseThreadTarget():
    """The Target function for the RaspiPulse thread"""
    # dur avg:12µs for inner getRaspiPulseCPS/CPM

    defname  = "RaspiPulseThreadTarget: "

    time.sleep(0.100)                                               # skip first 100 msec to let printouts finish
    nexttime = time.time()
    while not g.RaspiPulseThreadStopFlag:
        if time.time() >= nexttime:
            nexttime += 1
            # start = time.time()

            g.RaspiPulseLastCPS = getRaspiPulseCPS()
            g.RaspiPulseLastCPM = getCPMfromCPS(g.RaspiPulseLast60CPS)

            # stop  = time.time()
            # rdprint(defname, "dur: {:0.3f} ms".format(1000 * (stop - start)))  #

        dt = max(0.001, nexttime - time.time())
        # rdprint(defname, "dt: {:0.3f}".format(dt))
        time.sleep(dt)


# def recordCount(bcmpin):
#     """for each interrupt add 1 to total CPS"""

#     g.RaspiPulseCPS += 1


def getRaspiPulseCPS():
    """get CPS counts, clear CPS, add to CPM deque, and return as value"""

    defname = "getRaspiPulseCPS: "

    cps             = g.RaspiPulseCPS
    g.RaspiPulseCPS = 0
    g.RaspiPulseLast60CPS.append(cps)
    # rdprint(defname, "len(xxx60): ", len(g.RaspiPulseLast60CPS))

    return cps


def getValuesRaspiPulse(varlist):
    """get the data from Pulse"""

    start   = time.time()
    defname = "getValuesRaspiPulse: "
    alldata = {}                                        # empty dict for return data

    if g.LogReadings > 1:                               # ignore first reading

        # first, set all CPS
        cps = g.RaspiPulseLastCPS
        for vname in varlist:
            if vname.startswith("CPS"):
                cps = applyValueFormula(vname, cps, g.ValueScale[vname])
                alldata.update({vname: cps})
                # rdprint(defname, "vname: ", vname, " : ", cps)

        # second, set all CPM
        cpm = g.RaspiPulseLastCPM
        for vname in varlist:
            if vname.startswith("CPM"):
                cpm = applyValueFormula(vname, cpm, g.ValueScale[vname])
                alldata.update({vname: cpm})
                # rdprint(defname, "vname: ", vname, " : ", cpm)

    vprintLoggedValues(defname, varlist, alldata, (time.time() - start) * 1000)

    return alldata


def getInfoRaspiPulse(extended=False):
    """Info on the RaspiPulse Device"""

    Info          = "Configured Connection:        GeigerLog PlugIn\n"

    if not g.Devices["RaspiPulse"][g.CONN]:
        Info     += "<red>Device is not connected</red>"
    else:
        Info     += "Connected Device:             {}\n".format(g.Devices["RaspiPulse"][g.DNAME])
        Info     += "Configured Variables:         {}\n".format(g.RaspiPulseVariables)
        Info     += getTubeSensitivities(g.RaspiPulseVariables)
        Info     += "\n"
        if extended:
            # Info +=     "\n"
            Info +=     "Host Computer:\n"
            Info +=     "   Computer Model             {}\n".format(g.RaspiModel)
            Info +=     "   Hardware Info              {}\n".format(g.RaspiGPIO_Info)
            Info +=     "   Software GPIO Version      {}\n".format(g.RaspiGPIO_Version)

            Info +=     "Configured Pulse Detection settings: (valid only on Raspi)\n"
            Info +=     "   GPIO Mode:                 {}\n".format(g.RaspiPulseMode)               # options are: GPIO.BCM or GPIO.BOARD
            Info +=     "   Pulse BCM Pin No:          {}\n".format(g.RaspiPulsePin)
            Info +=     "   Pulse Pull up / down:      {}\n".format(g.RaspiPulsePullUpDown)
            Info +=     "   Pulse Edge detection:      {}\n".format(g.RaspiPulseEdge)

            if g.RaspiPulsePWM_Active:
                Info += "Configured PWM: (valid only on Raspi)\n"
                Info += "   PWM BCM Pin No:            {}\n"   .format(g.RaspiPulsePWM_Pin)
                Info += "   PWM Freq:                  {:0.3f} Hz\n".format(g.RaspiPulsePWM_Freq)
                Info += "   PWM Period:                {:0.3f} ms\n".format(g.RaspiPulsePWM_Period * 1e3)
                Info += "   PWM Pulselength:           {:0.3f} µs\n".format(g.RaspiPulsePWM_PulseLength * 1e6)
                Info += "   PWM Dutycycle:             {:0.3f} %\n" .format(g.RaspiPulsePWM_DutyCycle)

    return Info


def resetRaspiPulse(cmd=""):
    """resets device RaspiPulse"""

    defname  = "resetRaspiPulse: "
    dprint(defname)

    g.RaspiPulseCPS       = 0
    g.RaspiPulseLast60CPS = deque([], 60)

    if cmd == "Reset":
        fprint(header("Resetting RaspiPulse"))
        fprint ("Successful")


def setupRaspiPWM():
    """start PWM on Raspi"""

    # Using Raspi PWM output as a fake source for Pulse counting
    # Connect BOARD pin 33 (PWM output, BCM Pin 13) with BOARD pin 11 (Pulse counting input, BCM pin 17); nothing else connected!
    # Observation: much jitter in PWM, both in freq and pulse length
    # PWM frequency in [Hz] equiv to CPS (value must be > 0.0!)
    # max frequency is exactly 10000 Hz.    Set by the lib???
    # min frequency is exactly   0.1 Hz.    Set by the lib???
    # NOTE: to change values:
    #   g.RaspiPulsePWM_Handle.ChangeDutyCycle(10)            # (0.0 ... 100.0)
    #   g.RaspiPulsePWM_Handle.ChangeFrequency(freq)          # frequency (min: > 0.0; max: is ???)
    ###

    defname = "setupRaspiPWM: "

    # RaspiPulsePWM_Freq may have been (wrongly) set via command line
    # rdprint(defname, "g.RaspiPulsePWM_Freq: ", g.RaspiPulsePWM_Freq)
    if g.RaspiPulsePWM_Freq  < 0.1 or g.RaspiPulsePWM_Freq > 10000:
        msg = "Illegal PWM Frequency set: MUST be between 0.1 and 10000 Hz, incl! <br>Please restart within these limits."
        rdprint(defname, msg)
        efprint(msg)
        return "Wrong PWM Frequency Setting"

    g.RaspiPulsePWM_Pin         = 13                        # the GPIO pin in BCM mode used for generating PWM signal
    g.RaspiPulsePWM_PulseLength = 150 * 1E-6                # sec, = 150µs (length of M4011 tube pulse)
    g.RaspiPulsePWM_Period      = 1 / g.RaspiPulsePWM_Freq  # sec

    # on the USB-to-serial device: a "low" triggers the RX line and any RX-LED will become lit
    # --> good for visually tracking the pulse rate
    # "negative" pulses --> normally high, during pulse goes to low;  LED is ON  during pulse
    # the Raspi interrupt is preconfigured for FALLING edge (can be changed in config)
    if g.RaspiPulseEdge == "FALLING":
        g.RaspiPulsePWM_DutyCycle  = 100 * (1 - g.RaspiPulsePWM_PulseLength / g.RaspiPulsePWM_Period)
    else:
        # "positive" pulses --> normally low, during pulse goes to high; LED is OFF during pulse
        g.RaspiPulsePWM_DutyCycle  = 100 * (    g.RaspiPulsePWM_PulseLength / g.RaspiPulsePWM_Period)

    if g.RaspiPulsePWM_DutyCycle  < 0 or g.RaspiPulsePWM_DutyCycle > 100:
        msg = "For a pulse length of {:0.3g} µs the PWM frequency must be lower than {:0.6g} Hz."
        msg += "<br>Please restart within this limit."
        msg = msg.format(1E6 * g.RaspiPulsePWM_PulseLength, round(0.95 * (1 / g.RaspiPulsePWM_PulseLength), -2))
        rdprint(defname, msg)
        efprint(msg)
        return "Wrong PWM Frequency Setting"

    if g.isRaspi:
        GPIO.setup(g.RaspiPulsePWM_Pin, GPIO.OUT)                                           # define  PWM Pin as output
        if g.RaspiPulsePWM_Handle is None:
            g.RaspiPulsePWM_Handle = GPIO.PWM(g.RaspiPulsePWM_Pin, g.RaspiPulsePWM_Freq)    # set PWM at Pin with freq
            g.RaspiPulsePWM_Handle.start(g.RaspiPulsePWM_DutyCycle)                         # start PWM, includes setting duty cycle

    ptmplt = "   {:27s} : {}"
    dprint(ptmplt.format("PWM", "Freq: {:0.3f} Hz, Period: {:0.3f} ms, Pulse length: {:0.3f} µs, Duty Cycle: {:0.3f}%".
                                    format(g.RaspiPulsePWM_Freq,
                                        g.RaspiPulsePWM_Period * 1e3,
                                        g.RaspiPulsePWM_PulseLength * 1e6,
                                        g.RaspiPulsePWM_DutyCycle)
                                        ))


################################################################################################################################

    # Testing Performance Pulse-by-interrupt (RaspiPulse) and pulse via Serial (SerialPulse)
    # Pulses as PWM pulses from Raspi 5, NEGATIVE pulses, length 150 µs,  3.3V pulseamplitude
    #                                             RaspiPulse                              SerialPulse
    # Freq[Hz]  Duty[%]  Width[ms]    Volt[V]     CPS        CPM             CPS-Dev[%]   CPS        CPM             CPS-Dev[%]
    #      0.3  99.996   3333.333     3.3            0.297        17.948     -1.0             0.296       18.000     -1.4       old
    #      0.3  99.996   3333.333     3.3            0.298        17.981     -0.7             0.299       18.004     -0.3       new
    #      1.0  99.985   1000.000     3.3            1.000        60.000      0.0             1.000       18.000      0.0
    #      3.0  99.955    333.333     3.3            3.000       180.000      0.0             3.000      180.000      0.0
    #     10.0  99.850    100.000     3.3            9.955       597.574     -0.5            10.000      600.000      0.0
    #     30.0  99.550     33.333     3.3           29.729      1783.169     -0.9            30.043     1805.547     +0.1
    #     30.0  99.550     33.333     3.3           30.006      1800.387     +0.02           30.013     1800.964     +0.04
    #    100.0  98.500     10.000     3.3           99.909      5990.983     -0.09          100.000     6000.000      0.0
    #    300.0  95.500      3.333     3.3          299.488     17968.418     -0.2           300.024    18000.215     +0.01
    #   1000.0  85.000      1.000     3.3          997.986     59889.985     -0.2          1000.171    60016.554     +0.02
    #   3000.0  55.000      0.333     3.3         2997.861    179884.224     -0.07         3001.972   180092.439     +0.07
    #   5000.0  25.000      0.200     3.3         4990.892    299492.617     -0.2          4996.662   299849.317     -0.07
    #   6000.0  10.000      0.167     3.3         5974.761    358475.845     -0.4          5983.426   358940.845     -0.3
    #   6500.0   2.500      0.154     3.3         6474.333    388583.388     -0.4          6225.250   370934.403     -4.4
    #   6200.0   7.000      0.161     3.3         6196.519    371593.528     -0.06         6201.312   372050.111     +0.02
    # max is reached with 6500 Hz! CPS=0 when going higher
