#! /usr/bin/env python3
# -*- coding: utf-8 -*-

"""
gdev_raspi.py - GeigerLog commands to handle the Geiger counter clicks as interrupts
                on a Raspi4 to serve as CPM/CPS input

not established - not working!
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


from   gsup_utils       import *


def initRaspi():
    """Start the thread to monitor the audio pulses for clicks"""

    fprint("Device Raspi is not implemented", debug=True)
    return

    gglobs.RaspiLast60CPS             = np.full(60, 0) # needed???

    fncname ="initRaspi: "
    dprint(fncname + "Initialzing RaspiCounter")
    setDebugIndent(1)

    errmsg  = ""                            # what errors can be here?
    gglobs.RaspiDeviceName     = "RaspiCounter"
    gglobs.RaspiDeviceDetected = gglobs.RaspiDeviceName
    gglobs.Devices["Raspi"][0] = gglobs.RaspiDeviceDetected

    if gglobs.RaspiPulseDir     == "auto": gglobs.RaspiPulseDir     = False             # False => negative, True => positive
    if gglobs.RaspiPulseMax     == "auto": gglobs.RaspiPulseMax     = 32768             # +/- 16 bit
    if gglobs.RaspiThreshold    == "auto": gglobs.RaspiThreshold    = 60                # % of max
    if gglobs.RaspiVariables    == "auto": gglobs.RaspiVariables    = "CPM2nd, CPS2nd"
    if gglobs.RaspiCalibration  == "auto": gglobs.RaspiCalibration  = 154               # CPM/(µSv/h), = 0.065 µSv/h/CPM

    setCalibrations(gglobs.RaspiVariables, gglobs.RaspiCalibration)
    setLoggableVariables("Raspi", gglobs.RaspiVariables)

    #import RPi.GPIO as GPIO
    #~GPIO.setmode(GPIO.BOARD)

    gglobs.RaspiDevice      = sd.default.device
    gglobs.RaspiFormat      = sd.default.dtype
    gglobs.RaspiFormatText  = sd.default.dtype
    gglobs.RaspiChannels    = sd.default.channels
    gglobs.RaspiRate        = sd.default.samplerate
    #gglobs.RaspiChunk       = 32                   # in gglobs defined
    gglobs.RaspiLatency     = sd.default.latency

    dprint(fncname + "DEVICE:{}, CHANNELS:{}, RATE:{}, CHUNK:{}, FORMAT:{}, Latency:{}"\
                    .format(
                            gglobs.RaspiDevice,
                            gglobs.RaspiChannels,
                            gglobs.RaspiRate,
                            gglobs.RaspiChunk,
                            gglobs.RaspiFormat,
                            gglobs.RaspiLatency
                           )
         )

    gglobs.RaspiConnection = True

    setDebugIndent(0)

    return errmsg


def terminateRaspi():
    """Stop the Raspi counting"""

    fncname ="terminateRaspi: "

    if not gglobs.RaspiConnection: return fncname + "No RaspiCounter connection"

    gglobs.RaspiConnection = False


def sounddevThreadTarget(Dummy):
    """The thread to read the sounddev input"""

    fncname = "sounddevThreadTarget: "

    #getThreadData           = True

    gglobs.RaspiLastCps     = 0
    gglobs.RaspiLastCpm     = 0
    cps_count               = 0
    llimit                  = gglobs.RaspiThreshold / 100 * gglobs.RaspiPulseMax
    ilimit                  = 10000                             # the |pulse| must NOT exceed this value on first count in order to be countesd
                                                                # higher values give MORE counts!

    gglobs.RaspiLast60CPS   = np.full(60, 0)                    # storing last 60 sec of CPS values
    gglobs.RaspiMultiPulses = np.array([0])                     # time courses for last ~40 of the pulses
    gglobs.RaspiRecording   = np.array([0])
    nandata                 = np.full(10, gglobs.NAN)           # creating a gap of 10 values
    chunks40                = (gglobs.RaspiChunk + 10) * 40     # the length of 40 single pulses with gaps

    CHUNKstream = sd.InputStream(blocksize=gglobs.RaspiChunk)   # no callback so we get blocking read
    CHUNKstream.start()
    cstart                  = time.time()                       # to record the 1 sec collection period

    while not gglobs.RaspiThreadStop:

        #~wstart = time.time()
        try:
            record, overflowed = CHUNKstream.read(gglobs.RaspiChunk)
            npdata = record.reshape(-1)     # convert from '[ [1] [0] [3] ...[2] ]'  to '[1, 0, 3, ..., 2]'
            gglobs.RaspiRecording = np.concatenate((gglobs.RaspiRecording, npdata))[-gglobs.RaspiRate:]
        except Exception as e:
            info = fncname + "Exception reading stream "
            exceptPrint(e, info)
            npdata = np.array([0])
        #~print("npdata:  ", type(npdata), npdata[:10])
        #~wdt = (time.time() - wstart) * 1000

        #~xstart = time.time()
        if overflowed:
            # Input overflow.
            # In a stream opened with blocksize=0, indicates that data prior to
            # the first sample of the input buffer was discarded due to an overflow,
            # possibly because the stream callback is using too much CPU time.
            #
            # In a stream opened with a non-zero blocksize, it indicates that
            # data prior to one or more samples in the input buffer was discarded.
            # This can happen in full-duplex and input-only streams (including
            # playrec() and rec()).
            pass
            dprint("'overflowed' HAPPENED: Stream calls: record len:{}, overflowed:{}".format(len(record), overflowed) )

        # Determine if there is a count
        # ignore records catching pulses when already down; they were probably
        # already counted during last record
        gotCount = False
        if gglobs.RaspiPulseDir:                        # True -> positive pulse
            if npdata[0] < +ilimit and npdata.max() > +llimit:
                gotCount = True
        else:                                           # False -> negative pulse
            if npdata[0] > -ilimit and npdata.min() < -llimit:
                gotCount = True

        if gotCount:
            cps_count  += 1
            gglobs.RaspiMultiPulses   = np.concatenate((gglobs.RaspiMultiPulses, nandata, npdata))[-chunks40:]
            #~print("RaspiMultiPulses: ", len(gglobs.RaspiMultiPulses), gglobs.RaspiMultiPulses)
            #print("got count: Stream calls: {:7.3f}ms, record len:{}, overflowed:{}".format(dt, len(record), overflowed) )

        deltat = time.time() - cstart
        if deltat >= 1:
            gglobs.RaspiLastCps   = cps_count / deltat  * 1.05 # correct for calc time
            gglobs.RaspiLast60CPS = np.append(gglobs.RaspiLast60CPS, gglobs.RaspiLastCps)[1:]
            cps_count             = 0
            cstart                = time.time()

        #~xdt = (time.time() - xstart) * 1000
        #print("wdt:{:0.3f}ms, xdt:{:0.3f}ms".format(wdt, xdt))

    CHUNKstream.stop()
    CHUNKstream.close()


def getRaspiInfo(extended = False):
    """Info on settings of the sounddev thread"""

    if not gglobs.RaspiConnection:   return "No connected device"

    RaspiInfo = """Connected Device:             '{}'
Configured Variables:         {}
Geiger Tube Sensitivity:      {:0.1f} CPM/(µSv/h) ({:0.4f} µSv/h/CPM)"""\
                .format(
                        gglobs.RaspiDeviceName,
                        gglobs.RaspiVariables,
                        gglobs.RaspiCalibration, 1 / gglobs.RaspiCalibration
                       )

    if extended == True:
        RaspiInfo += """
Sampling Details:
- DEVICE:                     Input:'{}', Output:'{}'
- FORMAT:                     Input:'{}', Output:'{}'
- CHANNELS (1=Mono,2=Stereo): Input:'{}', Output:'{}'
- LATENCY [sec]:              Input:'{}', Output:'{}'
- Host API Index              {}
- RATE:                       {} (Samples per second)
- CHUNK:                      {} (Samples per read)
- Pulse Height Max            {} (System reported max signal)
- Pulse Direction             {} (negative or positive)
- Pulse Threshold             {}% of Pulse Height Max to trigger count"""\
                .format(
                        sd.default.device[0],
                        sd.default.device[1],
                        sd.default.dtype[0],
                        sd.default.dtype[1],
                        sd.default.channels[0],
                        sd.default.channels[1],
                        sd.default.latency[0],
                        sd.default.latency[1],
                        sd.default.hostapi,
                        sd.default.samplerate,

                        gglobs.RaspiChunk,
                        gglobs.RaspiPulseMax,
                        "POSITIVE" if gglobs.RaspiPulseDir else "NEGATIVE",
                        gglobs.RaspiThreshold,
                       )
        RaspiInfo += "\nFull Device Query:\n"
        RaspiInfo += str(sd.query_devices())
        RaspiInfo += "\n"

    return RaspiInfo


def toggleRaspiPulseDir():
    """toggle which pulse direction is sensed"""

    gglobs.RaspiPulseDir = not gglobs.RaspiPulseDir

    fprint(header("Switching Pulse Direction of RaspiCounter"))
    if gglobs.RaspiPulseDir:  direction = "POSITIVE"
    else:                     direction = "NEGATIVE"
    gglobs.RaspiMultiPulses = gglobs.RaspiMultiPulses[-10:]

    fprint("New pulse direction setting: {}".format(direction))


def getRaspiValues(varlist):
    """Read all sounddev data; return empty dict when not available"""

#testing
    gglobs.RaspiLastCps     = int(np.random.poisson(10, size=1))
    gglobs.RaspiLast60CPS   = np.append(gglobs.RaspiLast60CPS, gglobs.RaspiLastCps)[1:]
###

    fncname   = "getRaspiValues: "
    alldata = {}

    for vname in varlist:
        if   vname in ("CPM", "CPM1st", "CPM2nd", "CPM3rd"):
            cpm             = int(round(np.sum(gglobs.RaspiLast60CPS), 0))
            cpm             = scaleVarValues(vname, cpm, gglobs.ValueScale[vname])
            alldata.update(  {vname: cpm})

        elif vname in ("CPS", "CPS1st", "CPS2nd", "CPS3rd"):
            cps             = int(round(gglobs.RaspiLastCps, 0))
            cps             = scaleVarValues(vname, cps, gglobs.ValueScale[vname] )
            alldata.update(  {vname: cps})

    #~vprint("{:22s} Variables:{}  Data:{}  ".format(fncname, varlist, alldata))

    printLoggedValues(fncname, varlist, alldata)


    return alldata


def printRaspiDevInfo(extended=False):
    """prints basic info on the Raspi device"""

    setBusyCursor()

    txt = "Raspi Device"
    if extended:  txt += " Extended"
    fprint(header(txt))
    fprint("Configured Connection:", "None")
    rinfo = getRaspiInfo(extended=extended)
    fprint(rinfo)

    setNormalCursor()



##############################################################################
# following only relevant for use via 'main()'

def plotDataT(RaspiMultiPulses, inversrate):
    """This one used to plot either RaspiPlotSingle or RaspiMultiPulses of sound data"""

    if len(RaspiMultiPulses) == 0: return

    fncname = "plotDataT: "
    #~print(fncname + "starting with RaspiMultiPulses, inversrate: ", RaspiMultiPulses, inversrate)

    # Set "QT_STYLE_OVERRIDE" to avoid this message:
    #~  QApplication: invalid style override 'gtk' passed, ignoring it.
    #~  Available styles: Windows, Fusion
    os.environ["QT_STYLE_OVERRIDE"] = ""

    #~fig = plt.figure("Total", figsize=(14, 6))
    fig = plt.figure("Total", figsize=(14, 6), dpi=gglobs.hidpiScaleMPL)
    vprint("plotDataT: open figs count: {}, current fig: #{}".format(len(plt.get_fignums()), plt.gcf().number))

    if True:    # accumulate the counts (don't delete the figure)
        pass
    else:       # show a fresh record every time
        fig.clf()

    #print("plotDataT: RaspiMultiPulses:", len(RaspiMultiPulses), RaspiMultiPulses)
    x = np.arange(len(gglobs.RaspiMultiPulses)) * inversrate * 1000
    #~print("plotDataT: x    :", len(x), x)
    plt.xlabel("millisec")
    plt.plot(x, gglobs.RaspiMultiPulses,  'k.', linestyle='solid', linewidth=0.3, markersize=0.5)
    plt.ylim(-35000, 35000)
    plt.pause(.5)


def main():

    gglobs.debug = True
    gglobs.verbose = True
    fncname = "gdev_raspi.py: main: "
    gglobs.proglogPath          = "dummy"
    duration                    = 10   # sec of recording
    inversrate                  = 1 / gglobs.RaspiRate
    gglobs.RaspiMultiPulses     = np.zeros(256)

    gglobs.devel                = True                # to allow sound
    gglobs.RaspiActivation      = True
    gglobs.RaspiDeviceName      = "None"              # set by init
    gglobs.RaspiPulseDir        = False               # False for negative; True for positive pulse
    gglobs.RaspiThreshold       = 60                  # Percentage of pulse height to trigger a count


    print("Available Devices")
    print(sd.query_devices())
    print()

    RESET  = sd.default.reset()
    DEVICE = sd.default.device      #~DEVICE = sd.default.device = None, None --> no device!
                                    #~DEVICE = sd.default.device = 8,8        --> device 8 for output, device 8 for input
    sd.default.dtype    = ('int16', 'int16')
    sd.default.channels = (1, 1)
    FORMAT              = sd.default.dtype[1]
    CHANNELS            = sd.default.channels[1]                 # Mono; for Stereo set: #CHANNELS = 2

    #RATE = 96000
    #RATE = 44100
    #RATE = 22050
    #RATE = 11025
    RATE = sd.default.samplerate = 2**15                        # = 32768

    #CHUNK = 64
    #CHUNK = 128
    CHUNK = 256
    #CHUNK = 512
    #CHUNK = 1024
    #CHUNK = 2048
    #CHUNK = 4096


    start = time.time()
    while (time.time() - start) <= duration:
        time.sleep(.15)
        now = time.time()

        #~mystream.start()
        #~mystream.stop()
        try:
            getLongChunk(1.1)
            #print("time: {:5.3f}, gglobs.RaspiLastCps: {:5.1f}, gglobs.RaspiLastCpm: {:5.1f}".format((now -start), gglobs.RaspiLastCps, gglobs.RaspiLastCpm ))
            plotDataT(gglobs.RaspiMultiPulses, inversrate)
        except Exception as e:
            print(fncname + "Exception :", e)

    #terminateRaspi()

    plotDataT(gglobs.RaspiMultiPulses, inversrate)
    print(fncname + "Habe fertig")
    plt.show()


if __name__ == '__main__':
    import matplotlib.pyplot as plt # plotting possible only when run as main
    main()
