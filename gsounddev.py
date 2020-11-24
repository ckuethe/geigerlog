#! /usr/bin/python3
# -*- coding: utf-8 -*-

"""
gsounddev.py - GeigerLog commands to handle the audio clicks as CPM/CPS input
using sounddevice
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
__copyright__       = "Copyright 2016, 2017, 2018, 2019, 2020"
__credits__         = [""]
__license__         = "GPL3"



"""
NOTE:
Raspi:      on Raspi sounddevice cannot be installed until libffi-dev is installed per 'sudo apt install libffi-dev'
Windows:    sound on Windows: make sure the soundsettings for input and output are set for standard using Windows settings
"""

# LATENCY:
#
# Suggested input/output latency in seconds.
#
# The special values 'low' and 'high' can be used to select the default
# low/high latency of the chosen device. 'high' is typically more robust
# (i.e. buffer under-/overflows are less likely), but the latency may be
# too large for interactive applications.
#
# NOTE: latencies are given in millisec!
# on my Desktop:
# 'default_high_input_latency':  0.034829931972789115   --> 35 ms
# 'default_low_input_latency'  : 0.008707482993197279   -->  9 ms
# 'default_high_output_latency': 0.034829931972789115   --> 35 ms
# 'default_low_output_latency':  0.008707482993197279   -->  9 ms
#
# on MSI (low power) computer: using Input: 'Mikrofon (2- High Definition Au'
# 'default_high_input_latency':  0.18                   --> 180 ms
# 'default_low_input_latency':   0.09                   -->  90 ms
# 'default_high_output_latency': 0.18                   --> 180 ms
# 'default_low_output_latency':  0.09                   -->  90 ms

# tested on MSI (low power) computer on Windows 10 :
#~sd.default.latency  = ('low', 'low')   --> results in poor, low counts
#~sd.default.latency  = ('high', 'high') --> results in higher counts, but still less than digital on GMC300E+
#~sd.default.latency  = (100, 100)       --> results in same counts as digital on GMC300E+
#~sd.default.latency  = 1000, or 10000 works, but no improvement
#~sd.default.latency  = (1, 1)           --> works just as well!!!
#~sd.default.latency  = (0.1, 0.1)       --> getting 'overflowed' !
#~sd.default.latency  = (0.3, 0.3)       --> getting some 'overflowed' !
##sd.default.latency    = (0.5, 0.5)      #--> works, no 'overflowed' observed over >30sec !

# tested on Raspi 4 with USB dongle "ID 1b3f:2008 Generalplus Technology Inc. "
##sd.default.latency    = (1.0, 1.0)      #--> works, few 'overflowed' observed over >30sec !


from   gutils       import *


def initSounddev():
    """Start the thread to monitor the audio pulses for clicks"""

    global sounddevThread

    fncname ="initSounddev: "

    dprint(fncname + "Initialzing AudioCounter")
    setDebugIndent(1)

    errmsg  = ""                            # what errors can be here?
    gglobs.AudioDeviceName = "AudioCounter"

    if gglobs.AudioDevice       == "auto": gglobs.AudioDevice       = (None, None)      # the system's defaults
    if gglobs.AudioLatency      == "auto": gglobs.AudioLatency      = (1.0, 1.0)        # seems like a generic
    if gglobs.AudioPulseMax     == "auto": gglobs.AudioPulseMax     = 32768             # +/- 15 bit
    if gglobs.AudioPulseDir     == "auto": gglobs.AudioPulseDir     = False             # => negative
    if gglobs.AudioThreshold    == "auto": gglobs.AudioThreshold    = 60                # % of max
    if gglobs.AudioCalibration  == "auto": gglobs.AudioCalibration  = 154               # CPM/(µSv/h), = 0.065 µSv/h/CPM
    if gglobs.AudioVariables    == "auto": gglobs.AudioVariables    = "CPM3rd, CPS3rd"

    # the calibration of those vars must also be set, according to the set AudioVariables
    if   "2nd" in gglobs.AudioVariables:   gglobs.calibration2nd    = gglobs.AudioCalibration   # CPM2nd, CPS2nd
    elif "3rd" in gglobs.AudioVariables:   gglobs.calibration3rd    = gglobs.AudioCalibration   # CPM3rd, CPS3rd
    else:                                  gglobs.calibration1st    = gglobs.AudioCalibration   # CPM, CPS, CPM1st, CPS1st

    DevVars = gglobs.AudioVariables.split(",")
    for i in range(0, len(DevVars)):  DevVars[i] = DevVars[i].strip()
    gglobs.DevicesVars["Audio"] = DevVars


#Sound Driver settings

    dprint(fncname + "Query Devices: \n", sd.query_devices() )
    dprint(fncname + "Query Host Apis: \n", sd.query_hostapis(index=None))

    # in defaults with 2 allowed values: 1st=input, 2nd=output
    # samplerate has only one single int value
    sd.default.reset()                              # clear all settings to default
    sd.default.device       = gglobs.AudioDevice    # set the sounddevice defaults
    sd.default.latency      = gglobs.AudioLatency   # set latency values in sec, like (1.0, 1.0)
    sd.default.dtype        = ('int16', 'int16')    # choose from: 'float32', 'int32', 'int16', 'int8', 'uint8'
    sd.default.channels     = (1, 1)                # options: 1, 2, more
    sd.default.samplerate   = 44100                 # options: 96000, 48000, 44100, 22050, 11025

    print()
    try:
        dprint(fncname + "Properties Default Device: {}\n".format(sd.default.device),
                          sd.query_devices(device=None,
                          kind='input')) # exactly same result for kind='output'
    except Exception as e:
        info = fncname + "Exception"
        exceptPrint(e, sys.exc_info(), info)
    print()


    gglobs.AudioFormat      = sd.default.dtype
    gglobs.AudioChannels    = sd.default.channels
    gglobs.AudioRate        = sd.default.samplerate
    gglobs.AudioChunk       = 32

    dprint(fncname + "DEVICE:{}, CHANNELS:{}, FORMAT:{}, Latency:{}, Host API Index:{}, RATE:{}, CHUNK:{}"\
                    .format(
                            gglobs.AudioDevice,
                            gglobs.AudioChannels,
                            gglobs.AudioFormat,
                            gglobs.AudioLatency,
                            sd.default.hostapi,
                            gglobs.AudioRate,
                            gglobs.AudioChunk,
                           )
         )

    gglobs.AudioConnection = True

    sounddevThread = threading.Thread(target=sounddevThreadTarget, args=(None,))
    gglobs.AudioThreadStop = False
    sounddevThread.start()
    dprint(fncname + "Thread-status: is alive: ", sounddevThread.is_alive())

    setDebugIndent(0)

    return errmsg


def terminateSounddev():
    """Stop the thread to monitor the sounddev pulses for clicks"""

    global sounddevThread

    fncname ="terminateSounddev: "
    dprint(fncname + "stopping thread")
    if not gglobs.AudioConnection: return fncname + "No AudioCounter connection"

    gglobs.AudioThreadStop = True

    sounddevThread.join() # "This blocks the calling thread until the thread
                          #  whose join() method is called is terminated."

    # verify that thread has ended, but wait not longer than 5 sec (takes 0.006...0.016 ms)
    start = time.time()
    while sounddevThread.is_alive() and (time.time() - start) < 5:
        pass

    dprint(fncname + "thread-status: is alive: {}, waiting took:{:0.3f}ms".format(sounddevThread.is_alive(), 1000 * (time.time() - start)))
    gglobs.AudioConnection = False


def sounddevThreadTarget(Dummy):
    """The thread to read the sounddev input"""

    #~global cpm_counter, getThreadData
    global cpm_counter

    fncname = "sounddevThreadTarget: "

    gglobs.AudioLastCps     = 0
    gglobs.AudioLastCpm     = 0
    cps_count               = 0
    llimit                  = gglobs.AudioThreshold / 100 * gglobs.AudioPulseMax
    ilimit                  = 10000                             # the |pulse| must NOT exceed this value on first count in order to be countesd
                                                                # higher values give MORE counts!

    cpm_counter             = np.full(60, 0)                    # storing last 60 sec of CPS values
    gglobs.AudioMultiPulses = np.array([0])                     # time courses for last ~40 of the pulses
    gglobs.AudioRecording   = np.array([0])
    nandata                 = np.full(10, gglobs.NAN)           # creating a gap of 10 values
    chunks40                = (gglobs.AudioChunk + 10) * 40     # the length of 40 single pulses with gaps

    CHUNKstream = sd.InputStream(blocksize=gglobs.AudioChunk)   # no callback so we get blocking read
    CHUNKstream.start()
    cstart                  = time.time()                       # to record the 1 sec collection period

    while not gglobs.AudioThreadStop:

        #~wstart = time.time()
        try:
            record, overflowed = CHUNKstream.read(gglobs.AudioChunk)
            npdata = record.reshape(-1)     # convert from '[ [1] [0] [3] ...[2] ]'  to '[1, 0, 3, ..., 2]'
            gglobs.AudioRecording = np.concatenate((gglobs.AudioRecording, npdata))[-gglobs.AudioRate:]
        except Exception as e:
            info = fncname + "Exception reading stream "
            exceptPrint(e, sys.exc_info(), info)
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
        if gglobs.AudioPulseDir:                        # True -> positive pulse
            if npdata[0] < +ilimit and npdata.max() > +llimit:
                gotCount = True
        else:                                           # False -> negative pulse
            if npdata[0] > -ilimit and npdata.min() < -llimit:
                gotCount = True

        if gotCount:
            cps_count  += 1
            gglobs.AudioMultiPulses   = np.concatenate((gglobs.AudioMultiPulses, nandata, npdata))[-chunks40:]
            #~print("AudioMultiPulses: ", len(gglobs.AudioMultiPulses), gglobs.AudioMultiPulses)
            #print("got count: Stream calls: {:7.3f}ms, record len:{}, overflowed:{}".format(dt, len(record), overflowed) )

        deltat = time.time() - cstart
        if deltat >= 1:
            gglobs.AudioLastCps  = cps_count / deltat  * 1.05 # correct for calc time
            cpm_counter          = np.append(cpm_counter, gglobs.AudioLastCps)[1:]
            cps_count            = 0
            cstart               = time.time()

        #~xdt = (time.time() - xstart) * 1000
        #print("wdt:{:0.3f}ms, xdt:{:0.3f}ms".format(wdt, xdt))

    CHUNKstream.stop()
    CHUNKstream.close()


def getSounddevInfo(extended = False):
    """Info on settings of the sounddev thread"""

    if not gglobs.AudioConnection:   return "No connected device"

    AudioInfo = """Connected Device:             '{}'
Configured Variables:         {}
Geiger tube calib. factor:    {:0.1f} CPM/(µSv/h) ({:0.4f} µSv/h/CPM)"""\
                .format(
                        gglobs.AudioDeviceName,
                        gglobs.AudioVariables,
                        gglobs.AudioCalibration, 1 / gglobs.AudioCalibration
                       )

    if extended == True:
        AudioInfo += """
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

                        gglobs.AudioChunk,
                        gglobs.AudioPulseMax,
                        "POSITIVE" if gglobs.AudioPulseDir else "NEGATIVE",
                        gglobs.AudioThreshold,
                       )
        AudioInfo += "\nFull Device Query:\n"
        AudioInfo += str(sd.query_devices())
        AudioInfo += "\n"

    return AudioInfo


def toggleSounddevPulseDir():
    """toggle which pulse direction is sensed"""

    gglobs.AudioPulseDir = not gglobs.AudioPulseDir

    fprint(header("Switching Pulse Direction of AudioCounter"))
    if gglobs.AudioPulseDir:  direction = "POSITIVE"
    else:                     direction = "NEGATIVE"
    gglobs.AudioMultiPulses = gglobs.AudioMultiPulses[-10:]

    fprint("New pulse direction setting: {}".format(direction))


def getSounddevValues(varlist):
    """Read all sounddev data; return empty dict when not available"""

    global cpm_counter

    fncname   = "getSounddevValues: "
    alldata = {}

    if not gglobs.AudioConnection: # AudioCounter is NOT connected!
        dprint(fncname + "AudioCounter is not connected")
        return alldata

    if varlist == None:
        return alldata

    for vname in varlist:
        if   vname in ("CPM", "CPM1st", "CPM2nd", "CPM3rd"):
            cpm             = int(round(np.sum(cpm_counter), 0))
            cpm             = scaleVarValues(vname, cpm, gglobs.ValueScale[vname])
            alldata.update(  {vname: cpm})

        elif vname in ("CPS", "CPS1st", "CPS2nd", "CPS3rd"):
            cps             = int(round(gglobs.AudioLastCps, 0))
            cps             = scaleVarValues(vname, cps, gglobs.ValueScale[vname] )
            alldata.update(  {vname: cps})

    vprint("{:22s} Variables:{}  Data:{}  ".format(fncname, varlist, alldata))

    return alldata


##############################################################################
# following only relevant for use via 'main()'
# like: 'python3 geigerlog/gsounddev.py 7'


def getLongChunk(duration, recno):
    """record duration seconds of audio"""

    print("#{} - Recording for {} sec".format(recno, duration))

    reclen = int(sd.default.samplerate * duration)
    mystream = sd.InputStream(blocksize=reclen)
    mystream.start()
    record, overflowed = mystream.read(reclen) # get one record
    gglobs.AudioMultiPulses = record.reshape(-1)
    mystream.stop()


def plotDataT(AudioMultiPulses, inversrate):
    """plot record of sound data"""

    if len(AudioMultiPulses) == 0: return

    # Set "QT_STYLE_OVERRIDE" to avoid this message:
    #   QApplication: invalid style override 'gtk' passed, ignoring it.
    #   Available styles: Windows, Fusion
    os.environ["QT_STYLE_OVERRIDE"] = ""

    fig = plt.figure("Total", figsize=(14, 6))

    show = 0    # 1: accumulate the counts (don't delete the figure)
                # 0: delete last figure, and show a fresh record every time
    if    show: pass
    else:       fig.clf()

    x = np.arange(len(gglobs.AudioMultiPulses)) * inversrate * 1000 # create X-axis values
    y = gglobs.AudioMultiPulses                                     # Y-axis values
    #~print("plotDataT: x    :", len(x), x)
    #~print("plotDataT: y    :", len(y), y)
    plt.plot(x, y,  'k.', linestyle='solid', linewidth=0.3, markersize=0.5)
    plt.xlabel("millisec")
    plt.ylim(-35000, 35000)
    plt.pause(.5)


def main():
    """
    Start with: 'python3 gsounddev.py' to get a list of available Sound Devices
    Start with: 'python3 gsounddev.py N' to get a list of available Sound Devices,
                followed by N recordings and recoding plots from the default device
    """

    print("Available Sound Devices:")
    print(sd.query_devices())
    print()

    # Setting the soundcard
    sd.default.reset()
    sd.default.device       = (None, None)              # selects the default device
    sd.default.latency      = (1.0, 1.0)                # selects the default device
    sd.default.dtype        = ('int16', 'int16')        # signed 16 bit resolution for both input and output
    sd.default.channels     = (1, 1)                    # Mono for both input and output
    sd.default.samplerate   = 44100                     # options: 96000, 48000, 44100, 22050, 11025

    print("Sound Driver Settings:\n    DEVICE:{}, CHANNELS:{}, FORMAT:{}, Latency:{}, RATE:{}, Host API Index:{}"\
                    .format(
                            sd.default.device,
                            sd.default.channels,
                            sd.default.dtype,
                            sd.default.latency,
                            sd.default.samplerate,
                            sd.default.hostapi,
                           )
         )

    inversrate              = 1 / sd.default.samplerate
    gglobs.AudioMultiPulses = np.zeros(256)

    try:
        recs = abs(int(sys.argv[1])) # if none given on command line, an exception will be raised
    except:
        recs = 0

    for i in range(0, recs):
        try:
            getLongChunk(1.0, i + 1)
            plotDataT(gglobs.AudioMultiPulses, inversrate)
        except Exception as e:
            print("gsounddev.py: main: Exception :", e)

    if recs > 0:
        plotDataT(gglobs.AudioMultiPulses, inversrate)
        print("Done recording. To Exit close graph, or press CTRL-C in terminal")
        plt.show()


if __name__ == '__main__':
    import matplotlib.pyplot as plt # plotting possible only when run as main
    main()
    print()

