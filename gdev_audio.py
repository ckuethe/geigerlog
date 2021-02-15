#! /usr/bin/env python3
# -*- coding: utf-8 -*-

"""
gdev_audio.py - GeigerLog commands to handle the audio clicks as CPM/CPS input
                using module sounddevice
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
NOTES:
Raspi:      on Raspi sounddevice cannot be installed until libffi-dev is installed per 'sudo apt install libffi-dev'
Windows:    on Windows: make sure the soundsettings for input and output are set for 'standard' using Windows settings
Linux       with garbled sound and message in the terminal:
                "ALSA lib pcm.c:7963:(snd_pcm_recover) underrun occurred"
            execute 'pulseaudio -k' as regular user (not sudo!) this should solve it

            if not enough: look into '/etc/pulse/daemon.conf'. It may have lines:
                ; default-fragments = 4
                ; default-fragment-size-msec = 25
            uncommenting, and changing to:
                default-fragments = 5
                default-fragment-size-msec = 2
            might help
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
#~sd.default.latency  = (0.5, 0.5)       --> works, no 'overflowed' observed over >30sec !

# tested on Raspi 4 with USB dongle "ID 1b3f:2008 Generalplus Technology Inc. "
# sd.default.latency  = (1.0, 1.0)       --> works, few 'overflowed' observed over >30sec !


from   gsup_utils       import *


def initAudioCounter():
    """Start the thread to monitor the audio pulses for clicks"""

    global AudioCounterThread

    fncname ="initAudioCounter: "

    dprint(fncname + "Initialzing AudioCounter")
    setDebugIndent(1)

    errmsg  = ""                            # what errors can be here?
    gglobs.AudioDeviceName      = "AudioCounter"
    gglobs.AudioDeviceDetected  = gglobs.AudioDeviceName
    gglobs.Devices["Audio"][0]  = gglobs.AudioDeviceDetected

    if gglobs.AudioDevice       == "auto": gglobs.AudioDevice       = (None, None)      # the system's defaults
    if gglobs.AudioLatency      == "auto": gglobs.AudioLatency      = (1.0, 1.0)        # seems like a generic
    if gglobs.AudioPulseMax     == "auto": gglobs.AudioPulseMax     = 32768             # +/- 15 bit
    if gglobs.AudioPulseDir     == "auto": gglobs.AudioPulseDir     = False             # => negative
    if gglobs.AudioThreshold    == "auto": gglobs.AudioThreshold    = 60                # % of max
    if gglobs.AudioCalibration  == "auto": gglobs.AudioCalibration  = 154               # CPM/(µSv/h), = 0.065 µSv/h/CPM
    if gglobs.AudioVariables    == "auto": gglobs.AudioVariables    = "CPM3rd, CPS3rd"

    setCalibrations(gglobs.AudioVariables, gglobs.AudioCalibration)

    setLoggableVariables("Audio", gglobs.AudioVariables)


#Sound Driver settings

    dprint(fncname + "Query Devices: \n", sd.query_devices() )
    dprint(fncname + "Query Host Apis: \n", sd.query_hostapis(index=None))

    # in defaults with 2 allowed values: 1st=input, 2nd=output
    # samplerate has only one single int value
    sd.default.reset()                              # clear all settings to default
    sd.default.device       = gglobs.AudioDevice    # set the AudioDevice defaults
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

    AudioCounterThread = threading.Thread(target=AudioCounterThreadTarget, args=(None,))
    gglobs.AudioThreadStop = False
    AudioCounterThread.start()
    dprint(fncname + "Thread-status: is alive: ", AudioCounterThread.is_alive())

    setDebugIndent(0)

    return errmsg


def terminateAudioCounter():
    """Stop the thread to monitor the sounddev pulses for clicks"""

    global AudioCounterThread

    fncname ="terminateAudioCounter: "
    dprint(fncname + "Terminating AudioCounter")
    if not gglobs.AudioConnection: return fncname + "No AudioCounter connection"

    setDebugIndent(1)
    dprint(fncname + "stopping thread")
    gglobs.AudioThreadStop = True
    AudioCounterThread.join() # "This blocks the calling thread until the thread
                              #  whose join() method is called is terminated."

    # verify that thread has ended, but wait not longer than 5 sec (takes 0.006...0.016 ms)
    start = time.time()
    while AudioCounterThread.is_alive() and (time.time() - start) < 5:
        pass

    dprint(fncname + "thread-status: is alive: {}, waiting took:{:0.3f}ms".format(AudioCounterThread.is_alive(), 1000 * (time.time() - start)))
    gglobs.AudioConnection = False

    setDebugIndent(0)


def AudioCounterThreadTarget(Dummy):
    """The thread to read the sounddev input"""

    fncname = "AudioCounterThreadTarget: "

    gglobs.AudioLastCps     = 0
    gglobs.AudioLastCpm     = 0
    cps_count               = 0
    llimit                  = gglobs.AudioThreshold / 100 * gglobs.AudioPulseMax
    ilimit                  = 10000                             # the |pulse| must NOT exceed this value on first count in order to be countesd
                                                                # higher values give MORE counts!

    gglobs.AudioLast60CPS   = np.full(60, 0)                    # storing last 60 sec of CPS values
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
            gglobs.AudioLastCps   = cps_count / deltat  * 1.05 # correct for calc time
            gglobs.AudioLast60CPS = np.append(gglobs.AudioLast60CPS, gglobs.AudioLastCps)[1:]
            cps_count             = 0
            cstart                = time.time()

        #~xdt = (time.time() - xstart) * 1000
        #print("wdt:{:0.3f}ms, xdt:{:0.3f}ms".format(wdt, xdt))

    CHUNKstream.stop()
    CHUNKstream.close()


def getAudioCounterInfo(extended = False):
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


def toggleAudioCounterPulseDir():
    """toggle which pulse direction is sensed"""

    gglobs.AudioPulseDir = not gglobs.AudioPulseDir

    fprint(header("Switching Pulse Direction of AudioCounter"))
    if gglobs.AudioPulseDir:  direction = "POSITIVE"
    else:                     direction = "NEGATIVE"
    gglobs.AudioMultiPulses = gglobs.AudioMultiPulses[-10:]

    fprint("New pulse direction setting: {}".format(direction))


def getAudioValues(varlist):
    """Read all sounddev data; return empty dict when not available"""

    fncname   = "getAudioValues: "
    alldata = {}

    for vname in varlist:
        if   vname in ("CPM", "CPM1st", "CPM2nd", "CPM3rd"):
            cpm             = int(round(np.sum(gglobs.AudioLast60CPS), 0))
            cpm             = scaleVarValues(vname, cpm, gglobs.ValueScale[vname])
            alldata.update(  {vname: cpm})

        elif vname in ("CPS", "CPS1st", "CPS2nd", "CPS3rd"):
            cps             = int(round(gglobs.AudioLastCps, 0))
            cps             = scaleVarValues(vname, cps, gglobs.ValueScale[vname] )
            alldata.update(  {vname: cps})

    printLoggedValues(fncname, varlist, alldata)

    return alldata


def printAudioDevInfo(extended=False):
    """prints basic info on the AudioCounter device"""

    setBusyCursor()

    txt = "AudioCounter Device Info"
    if extended:  txt += " Extended"
    fprint(header(txt))
    fprint("Configured Connection:", "Default Audio Input")
    fprint(getAudioCounterInfo(extended=extended))

    setNormalCursor()




def plotAudio(dtype="Single Pulse", duration=None):
    """Plotting an audio plot"""

    fncname = "plotAudio: "

    data = gglobs.AudioPlotData
    #print(fncname + "dtype:{}, data:{}".format(dtype, data))

    subTitle = dtype

    if   dtype == "Single Pulse":
        pass

    elif dtype == "Multi Pulse":
        count     = len(data) / (gglobs.AudioChunk + 10) # 10 is: nan values as gap
        subTitle += " - {:1.0f} pulses shown".format(count)

    elif dtype == "Recording":
        subTitle += " - {:1.0f} second".format(duration)


    # Plotstyle
    plotstyle        = {'color'             : 'black',
                        'linestyle'         : 'solid',
                        'linewidth'         : '0.5',
                        'label'             : 'my label',
                        'markeredgecolor'   : 'black',
                        'marker'            : 'o',
                        'markersize'        : '1',
                        'alpha'             : 1,
                        }
    plt.close(99)

    #~fig2 = plt.figure(99, facecolor = "#E7F9C9")
    fig2 = plt.figure(99, facecolor = "#E7F9C9", dpi=gglobs.hidpiScaleMPL)
    vprint(fncname + "open figs count: {}, current fig: #{}".format(len(plt.get_fignums()), plt.gcf().number))

    plt.title("AudioCounter Device\n", fontsize=14, loc='center')
    plt.title("Audio Input", fontsize=10, fontweight='normal', loc = 'left')
    plt.title(subTitle, fontsize=10, fontweight='normal', loc = 'right')

    plt.grid(True)
    plt.subplots_adjust(hspace=None, wspace=.2 , left=.11, top=0.85, bottom=0.15, right=.97)
    plt.ticklabel_format(useOffset=False)

    # hide the cursor position from showing in the Nav toolbar
    ax1 = plt.gca()
    ax1.format_coord = lambda x, y: ""

    # canvas - this is the Canvas Widget that displays the `figure`
    # it takes the `figure` instance as a parameter to __init__
    canvas2 = FigureCanvas(fig2)
    canvas2.setFixedSize(1000, 550)
    navtoolbar = NavigationToolbar(canvas2, gglobs.exgg)

    labout = QTextBrowser()                  # label to hold the description
    labout.setFont(gglobs.fontstd)           # my std font for easy formatting
    labout.setText("")

    mtext1  =   "Device:           Input:'{}', Output:'{}'" .format(sd.default.device[0], sd.default.device[1])
    mtext1 += "\nSample Format:    {}"                      .format(gglobs.AudioFormat)
    mtext1 += "\nSampled Channels: {} (1=Mono, 2=Stereo)"   .format(gglobs.AudioChannels)
    mtext1 += "\nSampling rate:    {} per second"           .format(gglobs.AudioRate)
    mtext1 += "\nSamples:          {} per read"             .format(gglobs.AudioChunk)
    mtext1 += "\nPulse Height Max: ±{} "                    .format(gglobs.AudioPulseMax)
    mtext1 += "\nPulse Threshold:  {} %"                    .format(gglobs.AudioThreshold)
    mtext1 += "\nPulse Direction:  {} "                     .format(("POSITIVE" if gglobs.AudioPulseDir else "NEGATIVE"))

    if   dtype == "Single Pulse":
        labout.append("Showing the last detected AudioCounter pulse")

    elif dtype == "Multi Pulse":
        labout.append("Showing the last (up to 40) detected AudioCounter pulses")

    elif dtype == "Recording":
        labout.append("Showing a straight recording of {} second - no pulse detection applied".format(duration))

    labout.append(mtext1)

    d = QDialog()
    gglobs.plotAudioPointer = d
    d.setWindowIcon(gglobs.iconGeigerLog)
    d.setWindowTitle("AudioCounter Device")
    #d.setMinimumHeight(700)
    #d.setWindowModality(Qt.ApplicationModal)
    #d.setWindowModality(Qt.NonModal)
    d.setWindowModality(Qt.WindowModal)

    okButton = QPushButton("OK")
    okButton.setCheckable(True)
    okButton.setAutoDefault(True)
    okButton.clicked.connect(lambda:  d.done(0))

    singleButton = QPushButton("Single Pulse")
    singleButton.setCheckable(True)
    singleButton.setAutoDefault(False)
    singleButton.clicked.connect(lambda: reloadAudioData("Single Pulse"))

    multiButton = QPushButton("Multi Pulse")
    multiButton.setCheckable(True)
    multiButton.setAutoDefault(False)
    multiButton.clicked.connect(lambda: reloadAudioData("Multi Pulse"))

    recordButton = QPushButton("Recording")
    recordButton.setCheckable(True)
    recordButton.setAutoDefault(False)
    recordButton.clicked.connect(lambda: reloadAudioData("Recording"))

    togglePulseDirButton = QPushButton("Toggle Pulse Direction")
    togglePulseDirButton.setCheckable(True)
    togglePulseDirButton.setAutoDefault(False)
    togglePulseDirButton.clicked.connect(lambda: reloadAudioData("Toggle"))

    bbox    = QDialogButtonBox()
    bbox.addButton(okButton,                QDialogButtonBox.ActionRole)
    bbox.addButton(recordButton,            QDialogButtonBox.ActionRole)
    bbox.addButton(singleButton,            QDialogButtonBox.ActionRole)
    bbox.addButton(multiButton,             QDialogButtonBox.ActionRole)
    bbox.addButton(togglePulseDirButton,    QDialogButtonBox.ActionRole)

    layoutH = QHBoxLayout()
    layoutH.addWidget(bbox)
    layoutH.addWidget(navtoolbar)
    layoutH.addStretch()

    layoutV = QVBoxLayout(d)
    layoutV.addLayout(layoutH)
    layoutV.addWidget(canvas2)
    layoutV.addWidget(labout)

    plt.xlabel("Time [millisec]", fontsize=14)
    plt.ylabel("Amplitude [rel]", fontsize=14)
    plt.ylim(-35000, 35000)

    x = np.arange(len(data)) * 1 / gglobs.AudioRate * 1000 # create the x-axis data
    plt.plot(x, data,  **plotstyle)
    #d.update() # "Updates the widget unless updates are disabled or the widget is hidden."

    fig2.canvas.draw_idle()
    playWav("ok")
    d.exec_()


def reloadAudioData(dtype):
    """closes the dialog and reopens"""

    #print("reloadAudioData: ", dtype)

    try: # fails if it had never been opened; but then it is closed anyway
        gglobs.plotAudioPointer.close()
    except:
        pass

    # when a recording was last, then gglobs.AudioMultiPulses will be 44100 samples long,
    # but even Multi needs only 40*(single pulse + 10) => 1680. Therfore crop it,
    # otherwise next Multi will show samples from recording
    if len(gglobs.AudioMultiPulses) > (40 * (gglobs.AudioChunk + 10)):
        #~gglobs.AudioMultiPulses = gglobs.AudioMultiPulses[-(gglobs.AudioChunk + 10):]
        gglobs.AudioMultiPulses =  np.array([0])

    duration = None

    if   dtype == "Single Pulse":
        gglobs.AudioPlotData = gglobs.AudioMultiPulses[-(gglobs.AudioChunk):] # last pulse only without nan
        #gglobs.AudioMultiPulses = gglobs.AudioMultiPulses[-(gglobs.AudioChunk):] # last pulse only without nan

    elif dtype == "Multi Pulse":
        pass    # will show all, i.e. up to last 40 pulses
        gglobs.AudioPlotData = gglobs.AudioMultiPulses

    elif dtype == "Recording":
        setBusyCursor()
        duration = 1 # seconds
        #gdev_audio.getLongChunk(duration)
        gglobs.AudioPlotData = gglobs.AudioRecording
        setNormalCursor()

    else: # dtype == "Toggle":
        #~gdev_audio.toggleAudioCounterPulseDir()
        toggleAudioCounterPulseDir()
        dtype = "Recording"
        duration = 1 # seconds
        #~gglobs.AudioPlotData = gglobs.AudioMultiPulses[-(gglobs.AudioChunk):] # last pulse only without nan
        gglobs.AudioMultiPulses = np.array([0]) # set to empty as old pulses do not make sense
        gglobs.AudioPlotData    = gglobs.AudioRecording

    plotAudio(dtype, duration)

















##############################################################################
# following only relevant for use via 'main()'
# like: 'python3 geigerlog/gdev_audio.py 7'


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

    #~fig = plt.figure("Total", figsize=(14, 6))
    fig = plt.figure("Total", figsize=(14, 6), dpi=gglobs.hidpiScaleMPL)

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
    Start with: 'python3 gdev_audio.py' to get a list of available Sound Devices
    Start with: 'python3 gdev_audio.py N' to get a list of available Sound Devices,
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
            print("gdev_audio.py: main: Exception :", e)

    if recs > 0:
        plotDataT(gglobs.AudioMultiPulses, inversrate)
        print("Done recording. To Exit close graph, or press CTRL-C in terminal")
        plt.show()


if __name__ == '__main__':
    import matplotlib.pyplot as plt # plotting possible only when run as main
    main()
    print()

