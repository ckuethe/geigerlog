#! /usr/bin/env python3
# -*- coding: utf-8 -*-

"""
gdev_audio.py - GeigerLog commands to handle the audio-clicks as CPM/CPS input
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
__copyright__       = "Copyright 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024"
__credits__         = [""]
__license__         = "GPL3"


# NOTE:
# Raspi:      on Raspi module sounddevice cannot be installed until libffi-dev is installed
#             per 'sudo apt install libffi-dev'
# Windows:    make sure the soundsettings for input and output are set for 'standard'
#             using Windows settings
# Linux       with garbled sound and message in the terminal:
#                 "ALSA lib pcm.c:7963:(snd_pcm_recover) underrun occurred"
#             execute 'pulseaudio -k' as regular user (not sudo!) this should solve it
#
#             if not enough: look into '/etc/pulse/daemon.conf'. It may have lines:
#                 ; default-fragments = 4
#                 ; default-fragment-size-msec = 25
#             uncommenting, and changing to:
#                 default-fragments = 5
#                 default-fragment-size-msec = 2
#             might help


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

# tested on Manu 4 with USB dongle "ID 1b3f:2008 Generalplus Technology Inc. "
# sd.default.latency  = (1.0, 1.0)       --> works, few 'overflowed' observed over >30sec !


from gsup_utils   import *


def initAudio():
    """Start the thread to monitor the audio pulses for clicks"""

    global AudioCounterThread

    defname ="initAudio: "
    dprint(defname)
    setIndent(1)

    errmsg = ""                                                                 # potential errors:  no input device!
    g.Devices["Audio"][g.DNAME] = "Audio"

    if g.AudioDevice       == "auto": g.AudioDevice       = (None, None)        # the system's defaults
    if g.AudioLatency      == "auto": g.AudioLatency      = (1.0, 1.0)          # seems like a generic
    if g.AudioPulseMax     == "auto": g.AudioPulseMax     = 32768               # +/- 15 bit
    if g.AudioPulseDir     == "auto": g.AudioPulseDir     = False               # => negative
    if g.AudioThreshold    == "auto": g.AudioThreshold    = 50                  # % of max
    if g.AudioVariables    == "auto": g.AudioVariables    = "CPM3rd, CPS3rd"    # to not conflict with the GMC-counter variables

    g.AudioVariables = setLoggableVariables("Audio", g.AudioVariables)

    # print sound driver settings
    vprint(defname + "Query Devices: \n",   sd.query_devices() )
    vprint(defname + "Query Host Apis:")
    if g.verbose:
        for a in sd.query_hostapis(index=None):
            vprint("   ", a)

    # samplerate, device, latency take only one single value,
    # but others (dtype, channels) need 2 values: 1st=input, 2nd=output
    sd.default.reset()                              # clear all settings to default
    sd.default.device       = g.AudioDevice         # set the AudioDevice defaults
    sd.default.latency      = g.AudioLatency        # set latency values in sec, like (1.0, 1.0)
    sd.default.dtype        = ('int16', 'int16')    # choose from: 'float32', 'int32', 'int16', 'int8', 'uint8'
    sd.default.channels     = (1, 1)                # options: 1, 2, more
    sd.default.samplerate   = 44100                 # options: 96000, 48000, 44100, 22050, 11025

    try:
        defaultDevice = sd.default.device
        dprint(defname + "Default Device (Input, Output): {}".format(defaultDevice))

        if defaultDevice[1] != -1 :
            sdqd = sd.query_devices(device=None, kind='output')
            vprint(defname  + "Output Device: ")
            for key in sdqd: vprint("   {:30s} : {}".format(key, sdqd[key]))
        else:
            edprint(defname + "Output Device: ", "No Default Output Device!")

        if defaultDevice[0] != -1 :
            sdqd = sd.query_devices(device=None, kind='input')
            vprint(defname  + "Input Device : ")
            for key in sdqd: vprint("   {:30s} : {}".format(key, sdqd[key]))
        else:
            edprint(defname + "Input Device : ", "No Default Input Device!")

    except Exception as e:
        info = defname + "Exception in querying default devices"
        exceptPrint(e, info)

    if defaultDevice[0] != -1:
        g.AudioFormat      = sd.default.dtype           # like: ('int16', 'int16')
        g.AudioChannels    = sd.default.channels        # like: (1, 1)
        g.AudioRate        = sd.default.samplerate      # like: 44100
        g.AudioChunk       = 64                         # Samples per read

        #testing #########
        # Varying g.AudioChunk
        # results:  g.AudioChunk = 16   : at CPM=~2850 per Serial, audio is approx  6.0% less !!!   # @16 a GMC-300S pulse is covering about 2/3 of the AudioChunk
        #           g.AudioChunk = 32   : at CPM=~2850 per Serial, audio is approx  1.9% less
        #           g.AudioChunk = 32   : at CPM=~2850 per Serial, audio is approx  1.7% less
        #           g.AudioChunk = 32   : at CPM=~2850 per Serial, audio is approx  1.9% less
        #           g.AudioChunk = 64   : at CPM=~2850 per Serial, audio is approx  1.2% less
        #           g.AudioChunk = 64   : at CPM=~2850 per Serial, audio is approx  1.2% less       # gemessen über > 14h!
        #           g.AudioChunk = 128  : at CPM=~2850 per Serial, audio is approx  3%   less !
        #           g.AudioChunk = 256  : at CPM=~2850 per Serial, audio is approx 10%   less !!
        #           g.AudioChunk = 512  : at CPM=~2850 per Serial, audio is approx 25%   less !!!
        # --> shorter AudioChunk gives more counts!
        # --> g.AudioChunk = 64 seems best compromise
        # end testing

        dprint(defname + "DEVICE:{}, CHANNELS:{}, FORMAT:{}, Latency:{}, Host API Index:{}, RATE:{}, CHUNK:{}"\
                        .format(
                                g.AudioDevice,
                                g.AudioChannels,
                                g.AudioFormat,
                                g.AudioLatency,
                                sd.default.hostapi,
                                g.AudioRate,
                                g.AudioChunk,
                               )
              )

        g.Devices["Audio"][g.CONN] = True

        g.AudioThreadStop  = False

        AudioCounterThread = threading.Thread(target=AudioCounterThreadTarget, args=(None,))
        AudioCounterThread.start()
        dprint(defname + "Thread-status: is alive: ", AudioCounterThread.is_alive())

    else:
        errmsg  = "No Sound Input Device detected! Is there a proper connection?"

    setIndent(0)

    return errmsg


def terminateAudio():
    """Stop the thread to monitor the sounddev pulses for clicks"""

    global AudioCounterThread

    defname ="terminateAudio: "

    dprint(defname)
    setIndent(1)

    dprint(defname + "stopping thread")
    g.AudioThreadStop = True
    AudioCounterThread.join() # "This blocks the calling thread until the thread
                              #  whose join() method is called is terminated."

    # verify that thread has ended, but wait not longer than 5 sec (takes 0.006...0.016 ms)
    start = time.time()
    while AudioCounterThread.is_alive() and (time.time() - start) < 5:
        pass

    dprint(defname + "thread-status: is alive: {}, waiting took:{:0.1f} ms".format(AudioCounterThread.is_alive(), 1000 * (time.time() - start)))
    g.Devices["Audio"][g.CONN] = False

    dprint(defname + "Terminated")
    setIndent(0)


def AudioCounterThreadTarget(Dummy):
    """The thread to read the sounddev input"""

    defname = "AudioCounterThreadTarget: "

    g.AudioLastCps     = 0
    g.AudioLastCpm     = 0
    cps_count          = 0
    llimit             = g.AudioThreshold / 100 * g.AudioPulseMax
    ilimit             = 10000                              # the |pulse| must NOT exceed this value on first count in order to be counted
                                                            # higher values give MORE counts!

    g.AudioLast60CPS   = np.full(60, 0)                     # storing last 60 sec of CPS values
    g.AudioMultiPulses = np.array([0])                      # time courses for last ~40 of the pulses
    g.AudioRecording   = np.array([0])
    nandata            = np.full(10, g.NAN)                 # creating a gap of 10 values
    chunks40           = (g.AudioChunk + 10) * 40           # the length of 40 single pulses with gaps

    cstart             = time.time()                        # to record the 1 sec collection period

    try:
        CHUNKstream = sd.InputStream(blocksize=g.AudioChunk)   # no callback so we get blocking read
        CHUNKstream.start()
    except Exception as e:
        msg = "Audio cannot be activated. Is an input device missing?"
        exceptPrint(e, msg)
        g.AudioThreadStop = True
        return

    while not g.AudioThreadStop:
        try:
            record, overflowed = CHUNKstream.read(g.AudioChunk)
            npdata = record.reshape(-1)     # convert from '[ [1] [0] [3] ...[2] ]'  to '[1, 0, 3, ..., 2]'
            g.AudioRecording = np.concatenate((g.AudioRecording, npdata))[-g.AudioRate:]
        except Exception as e:
            info = defname + "Exception reading stream "
            exceptPrint(e, info)
            npdata = np.array([0])

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
        if g.AudioPulseDir:                        # True -> positive pulse
            if npdata[0] < +ilimit and npdata.max() > +llimit:
                gotCount = True
        else:                                           # False -> negative pulse
            if npdata[0] > -ilimit and npdata.min() < -llimit:
                gotCount = True

        if gotCount:
            cps_count  += 1
            g.AudioMultiPulses   = np.concatenate((g.AudioMultiPulses, nandata, npdata))[-chunks40:]

        deltat = time.time() - cstart
        if deltat >= 1:
            g.AudioLastCps   = cps_count / deltat  * 1.02                        # correct for calc time
            g.AudioLast60CPS = np.append(g.AudioLast60CPS, g.AudioLastCps)[1:]
            cps_count        = 0
            cstart           = time.time()

    CHUNKstream.stop()
    CHUNKstream.close()


def getInfoAudio(extended = False):
    """Info on settings of the sounddev thread"""

    AudioInfo  = "Configured Connection:        Default Audio Input\n"

    if not g.Devices["Audio"][g.CONN]: return AudioInfo + "<red>Device is not connected</red>"

    AudioInfo += "Connected Device:             {}\n".format(g.Devices["Audio"][g.DNAME])
    AudioInfo += "Configured Variables:         {}\n".format(g.AudioVariables)
    AudioInfo += getTubeSensitivities(g.AudioVariables)

    if extended == True:
        AudioInfo += "Sampling Details:\n"
        AudioInfo += "- DEVICE:                     Input:'{}', Output:'{}'\n"                  .format(sd.default.device[0], sd.default.device[1])
        AudioInfo += "- FORMAT:                     Input:'{}', Output:'{}'\n"                  .format(sd.default.dtype[0],sd.default.dtype[1])
        AudioInfo += "- CHANNELS (1=Mono,2=Stereo): Input:'{}', Output:'{}'\n"                  .format(sd.default.channels[0], sd.default.channels[1],)
        AudioInfo += "- LATENCY [sec]:              Input:'{}', Output:'{}'\n"                  .format(sd.default.latency[0], sd.default.latency[1])
        AudioInfo += "- Host API Index              {}\n"                                       .format(sd.default.hostapi)
        AudioInfo += "- RATE:                       {} (Samples per second)\n"                  .format(sd.default.samplerate)
        AudioInfo += "- CHUNK:                      {} (Samples per read)\n"                    .format(g.AudioChunk)
        AudioInfo += "- Pulse Height Max            {} (System reported max signal)\n"          .format(g.AudioPulseMax)
        AudioInfo += "- Pulse Direction             {} (negative or positive)\n"                .format("POSITIVE" if g.AudioPulseDir else "NEGATIVE")
        AudioInfo += "- Pulse Threshold             {}% of Pulse Height Max to trigger count\n" .format(g.AudioThreshold)
        AudioInfo += "\nFull Device Query:\n"
        AudioInfo += str(sd.query_devices())
        AudioInfo += "\n"

    return AudioInfo


def toggleAudioCounterPulseDir():
    """toggle which pulse direction is sensed"""

    g.AudioPulseDir = not g.AudioPulseDir

    fprint(header("Switching Pulse Direction of AudioCounter"))
    if g.AudioPulseDir:  direction = "POSITIVE"
    else:                direction = "NEGATIVE"
    g.AudioMultiPulses = g.AudioMultiPulses[-10:]

    fprint("New pulse direction setting: {}".format(direction))


def getValuesAudio(varlist):
    """Read all sounddev data; return empty dict when not available"""

    start = time.time()

    defname = "getValuesAudio: "
    alldata = {}

    if g.LogReadings > 2:           # skip first 2 readings; they are 0 and medium value
        for vname in varlist:
            if   vname in ("CPM", "CPM1st", "CPM2nd", "CPM3rd"):
                    cpm             = int(round(np.sum(g.AudioLast60CPS), 0))
                    cpm             = applyValueFormula(vname, cpm, g.ValueScale[vname])
                    alldata.update(  {vname: cpm})

            elif vname in ("CPS", "CPS1st", "CPS2nd", "CPS3rd"):
                    cps             = int(round(g.AudioLastCps, 0))
                    cps             = applyValueFormula(vname, cps, g.ValueScale[vname] )
                    alldata.update(  {vname: cps})

    vprintLoggedValues(defname, varlist, alldata, (time.time() - start) * 1000)

    return alldata


def plotAudio(dtype="Single Pulse", duration=None):
    """Plotting an audio plot"""

    defname = "plotAudio: "
    print(defname + "dtype:{}".format(dtype))

    data = g.AudioPlotData / 32768 * 100                            # to scale to -100 ... +100
    print(defname + "data:{}".format(data))

    subTitle = dtype

    if   dtype == "Single Pulse":
        pass

    elif dtype == "Multi Pulse":
        count     = len(data) / (g.AudioChunk + 10) # 10 is: nan values as gap
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
    fig2 = plt.figure(99, facecolor = "#E7cccc", dpi=g.hidpiScaleMPL)
    wprint(defname + "open figs count: {}, current fig: #{}".format(len(plt.get_fignums()), plt.gcf().number))

    plt.title("AudioCounter Device\n", fontsize=14, loc='center')
    plt.title("Audio Input", fontsize=10, fontweight='normal', loc = 'left')
    plt.title(subTitle, fontsize=10, fontweight='normal', loc = 'right')

    plt.grid(visible=True, which='major')
    plt.minorticks_on()
    plt.subplots_adjust(hspace=None, wspace=.2 , left=.11, top=0.85, bottom=0.15, right=.97)
    plt.ticklabel_format(useOffset=False)


    # hide the cursor position from showing in the Nav toolbar
    ax1 = plt.gca()
    ax1.format_coord = lambda x, y: ""

    # canvas - this is the Canvas Widget that displays the `figure`
    # it takes the `figure` instance as a parameter to __init__
    canvas2 = FigureCanvas(fig2)
    canvas2.setFixedSize(1000, 550)
    navtoolbar = NavigationToolbar(canvas2, g.exgg)

    labout = QTextBrowser()                  # label to hold the description
    labout.setFont(g.fontstd)           # my std font for easy formatting
    labout.setText("")

    mtext1  =   "Device:           Input:'{}', Output:'{}'" .format(sd.default.device[0], sd.default.device[1])
    mtext1 += "\nSample Format:    {}"                      .format(g.AudioFormat)
    mtext1 += "\nSampled Channels: {} (1=Mono, 2=Stereo)"   .format(g.AudioChannels)
    mtext1 += "\nSampling rate:    {} per second"           .format(g.AudioRate)
    mtext1 += "\nSamples:          {} per read"             .format(g.AudioChunk)
    mtext1 += "\nPulse Height Max: ±{} "                    .format(g.AudioPulseMax)
    mtext1 += "\nPulse Threshold:  {} %"                    .format(g.AudioThreshold)
    mtext1 += "\nPulse Direction:  {} "                     .format(("POSITIVE" if g.AudioPulseDir else "NEGATIVE"))

    if   dtype == "Single Pulse":
        labout.append("Showing the last detected AudioCounter pulse")

    elif dtype == "Multi Pulse":
        labout.append("Showing the last (up to 40) detected AudioCounter pulses")

    elif dtype == "Recording":
        labout.append("Showing a straight recording of {} second - no pulse detection applied".format(duration))

    labout.append(mtext1)

    d = QDialog()
    g.plotAudioPointer = d
    d.setWindowIcon(g.iconGeigerLog)
    d.setWindowTitle("AudioCounter Device")
    #d.setMinimumHeight(700)
    d.setWindowModality(Qt.WindowModal)

    okButton = QPushButton("OK")
    okButton.setAutoDefault(True)
    okButton.clicked.connect(lambda:  d.done(0))

    singleButton = QPushButton("Single Pulse")
    singleButton.setAutoDefault(False)
    singleButton.clicked.connect(lambda: reloadAudioData("Single Pulse"))

    multiButton = QPushButton("Multi Pulse")
    multiButton.setAutoDefault(False)
    multiButton.clicked.connect(lambda: reloadAudioData("Multi Pulse"))

    recordButton = QPushButton("Recording")
    recordButton.setAutoDefault(False)
    recordButton.clicked.connect(lambda: reloadAudioData("Recording"))

    togglePulseDirButton = QPushButton("Toggle Pulse Direction")
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
    plt.ylabel("Amplitude [% of 32768]", fontsize=14)
    # plt.ylim(-35000, 35000)
    plt.ylim(-100, 100)

    x = np.arange(len(data)) * 1 / g.AudioRate * 1000 # create the x-axis data
    plt.plot(x, data,  **plotstyle)
    #d.update() # "Updates the widget unless updates are disabled or the widget is hidden."

    fig2.canvas.draw_idle()
    bip()
    d.exec()


def reloadAudioData(dtype):
    """closes the dialog and reopens"""

    #print("reloadAudioData: ", dtype)

    try: # fails if it had never been opened; but then it is closed anyway
        g.plotAudioPointer.close()
    except:
        pass

    # when a recording was last, then g.AudioMultiPulses will be 44100 samples long,
    # but even Multi needs only 40*(single pulse + 10) => 1680. Therfore crop it,
    # otherwise next Multi will show samples from recording
    if len(g.AudioMultiPulses) > (40 * (g.AudioChunk + 10)):
        #~g.AudioMultiPulses = g.AudioMultiPulses[-(g.AudioChunk + 10):]
        g.AudioMultiPulses =  np.array([0])

    duration = None

    if   dtype == "Single Pulse":
        g.AudioPlotData = g.AudioMultiPulses[-(g.AudioChunk):] # last pulse only without nan
        #g.AudioMultiPulses = g.AudioMultiPulses[-(g.AudioChunk):] # last pulse only without nan

    elif dtype == "Multi Pulse":
        pass    # will show all, i.e. up to last 40 pulses
        g.AudioPlotData = g.AudioMultiPulses

    elif dtype == "Recording":
        setBusyCursor()
        duration = 1 # seconds
        #gdev_audio.getLongChunk(duration)
        g.AudioPlotData = g.AudioRecording
        setNormalCursor()

    else: # dtype == "Toggle":
        #~gdev_audio.toggleAudioCounterPulseDir()
        toggleAudioCounterPulseDir()
        dtype = "Recording"
        duration = 1 # seconds
        #~g.AudioPlotData = g.AudioMultiPulses[-(g.AudioChunk):] # last pulse only without nan
        g.AudioMultiPulses = np.array([0]) # set to empty as old pulses do not make sense
        g.AudioPlotData    = g.AudioRecording

    plotAudio(dtype, duration)


def audio_callback(indata, frames, time, status):
    """This is called (from a separate thread) for each audio block."""

    global liveq

    defname = "audio_callback: "
    # print(defname + "np.shape(indata): ", np.shape(indata), ", frames: ", frames, ", time: ", time, ", status: ", status)
    # print("indata: \n", indata)

    if status:
        cdprint(defname + "status: '{}'  type(status): '{}'".format(status, type(status)))

    # Fancy indexing with mapping creates a (necessary!) copy:
    liveq.put(indata[:, 0])


def updateAnimationPlot(frame):
    """This is called by matplotlib for each animated plot update.

    Typically, audio callbacks happen more frequently than plot updates,
    therefore the queue tends to contain multiple blocks of audio data.
    """
    global liveq, plotdata

    defname = "updateAnimationPlot: "
    # print(defname + "frame", frame)

    while True:
        try:
            data = liveq.get_nowait()
        except queue.Empty as e:
            # exceptPrint(e, defname + "queue.Empty")
            break

        shift    = len(data)
        plotdata = np.roll(plotdata, -shift)
        plotdata[-shift:] = data

        lines[0].set_ydata(plotdata)
        # break

    return lines


def makeEnde():
    global ende

    ende = True


def showLiveAudioSignal():
    """Plotting a rolling audio plot"""

    defname = "showLiveAudioSignal: "

    global liveq, lines, plotdata, ende
    global args_device, args_channels, args_samplerate

    liveq = queue.Queue()
    ende  = False

    try:
        #print(defname + "Audio Devices found on system:\n{}".format(sd.query_devices()))

        args_samplerate = None
        args_window     = 20000     # 5000
        args_downsample = 1
        args_channels   = 1
        args_interval   = 50
        args_device     = None

        if args_samplerate is None:
            device_info = sd.query_devices(args_device, 'input')
            args_samplerate = device_info['default_samplerate']
        #print(defname + "parameters: ", args_samplerate, args_window, args_downsample, args_channels, args_interval, args_device)

        length   = int(args_window * args_samplerate / (1000 * args_downsample)) # time length in ms
        plotdata = np.zeros((length))                        # create buffer of required length
        # print("length: ", length)                          # 20000 * 44100 / (1000 * 1) = 882000
        # print("plotdata: ", plotdata)                      # [[0.] [0.] [0.] ... [0.] [0.] [0.]]
        # print("np.shape(plotdata): ", np.shape(plotdata))  # np.shape(plotdata):  (441000, 1)

    except Exception as e:
        srcinfo = defname + "Exception: "
        exceptPrint(e, srcinfo)

    plt.close(77)
    fig77 = plt.figure(77, facecolor = "#E7cccc", dpi=g.hidpiScaleMPL) # light red
    vprint(defname + "open figs count: {}, current fig: #{}".format(len(plt.get_fignums()), plt.gcf().number))

    lines = plt.plot(plotdata) # creates a plot array x=0,1,2,..., (882000 - 1);  y=0,0,0,..., 0
    # for column, line in enumerate(lines):
    #     print("column: ", column, ", lines: ", lines, column, line)
    #     print("x: ", line.get_xdata(orig=True), "\ny: ", line.get_ydata(orig=True))

    plt.title("AudioCounter Device\n", fontsize=14, loc='center')
    plt.title("Live Audio Signal", fontsize=10, fontweight='normal', loc = 'left')

    plt.grid(True)
    plt.subplots_adjust(hspace=None, wspace=.2 , left=.11, top=0.85, bottom=0.15, right=.97)
    plt.ticklabel_format(useOffset=False)

    # do not draw x ticks and x labels
    plt.tick_params(
        axis='x',          # changes apply to the x-axis
        which='both',      # both major and minor ticks are affected
        bottom=False,      # ticks along the bottom edge are off
        top=False,         # ticks along the top edge are off
        labelbottom=False) # labels along the bottom edge are off

    # hide the cursor position from showing in the Nav toolbar
    ax1 = plt.gca()
    ax1.format_coord = lambda x, y: ""

    # canvas - this is the Canvas Widget that displays the `figure`
    # it takes the `figure` instance as a parameter to __init__
    canvas77 = FigureCanvas(fig77)
    canvas77.setFixedSize(1000, 550)
    navtoolbar = NavigationToolbar(canvas77, g.exgg)

    d = QDialog()
    g.plotAudioPointer = d
    d.setWindowIcon(g.iconGeigerLog)
    d.setWindowTitle("AudioCounter Device")
    #d.setMinimumHeight(700)
    d.setWindowModality(Qt.WindowModal)

    okButton = QPushButton("OK")
    okButton.setAutoDefault(True)
    okButton.clicked.connect(lambda:  makeEnde())

    bbox    = QDialogButtonBox()
    bbox.addButton(okButton,                QDialogButtonBox.ActionRole)

    layoutH = QHBoxLayout()
    layoutH.setAlignment(Qt.AlignLeft);
    layoutH.addWidget(bbox)
    layoutH.addWidget(navtoolbar)
    layoutH.addStretch() # all stretches needed, very odd!
    layoutH.addStretch()
    layoutH.addStretch()
    layoutH.addStretch()
    layoutH.addStretch()
    layoutH.addStretch()
    layoutH.addStretch()
    layoutH.addStretch()
    layoutH.addStretch()

    layoutV = QVBoxLayout(d)
    layoutV.addLayout(layoutH)
    layoutV.addWidget(canvas77)

    plt.xlabel("\nTime", fontsize=14)
    plt.ylabel("Amplitude [rel]", fontsize=14)
    plt.ylim(-35000, 35000)

    # https://stackoverflow.com/questions/16732379/stop-start-pause-in-python-matplotlib-animation
    #
    # /home/ullix/geigerlog/geigerlog/gdev_audio.py:741: UserWarning: frames=None which we can infer
    # the length of, did not pass an explicit *save_count* and passed cache_frame_data=True.  To avoid
    # a possibly unbounded cache, frame data caching has been disabled. To suppress this warning either
    # pass `cache_frame_data=False` or `save_count=MAX_FRAMES`.

    # ani = mplanim.FuncAnimation(fig77, updateAnimationPlot, interval=args_interval, blit=True)
    # ani = mplanim.FuncAnimation(fig77, updateAnimationPlot, interval=args_interval, blit=False)
    # ani = mplanim.FuncAnimation(fig77, updateAnimationPlot, interval=args_interval, blit=False, cache_frame_data=False)
    # ani = mplanim.FuncAnimation(fig77, updateAnimationPlot, interval=args_interval, blit=False, save_count=matplotlib.MAX_FRAMES) # module 'matplotlib' has no attribute 'MAX_FRAMES'
    # ani = mplanim.FuncAnimation(fig77, updateAnimationPlot, interval=args_interval, blit=False, save_count=mplanim.MAX_FRAMES)      # module 'matplotlib.animation' has no attribute 'MAX_FRAMES'
    ani = mplanim.FuncAnimation(fig77, updateAnimationPlot, interval=args_interval, blit=False, save_count=1000) # scheint ok

    bip()

    d.open()    # needed!

    while True: # one cycle is about 350 ms (300 ... 400 ms)
        # start = time.time()

        with sd.InputStream(device=args_device, channels=args_channels, samplerate=args_samplerate, callback=audio_callback):
            pass
            QtUpdate() # ohne dies nur leerer Fensterrahmen

        # d.show() # kein Zusatznutzen; ohne QtUpdate nur leeres Bild
        # cdprint("time delta: {:0.3f} ms".format(1000*(time.time() -start)))

        if ende: break

    d.close()
    ani.event_source.stop() # ouff, this stops the animation!


def turnEia(tdir, mmovie):

    turnDir = tdir
    mmovie.stop()
    time.sleep(0.3)
    mmovie.start()


def showAudioEia():
    """https://www.gqelectronicsllc.com/forum/topic.asp?TOPIC_ID=9517&#7803"""

    defname = "showAudioEia: "

    from PyQt5.QtGui import QMovie

    d = QDialog()

    d.setWindowIcon(g.iconGeigerLog)
    d.setWindowTitle("Eia")
    d.setWindowModality(Qt.WindowModal)

    okButton = QPushButton("OK")
    okButton.setAutoDefault(True)
    okButton.clicked.connect(lambda:  d.close())

    singleButton = QPushButton("Left Turn")
    singleButton.setAutoDefault(False)
    singleButton.clicked.connect(lambda: turnEia("Left", movie))

    rightButton = QPushButton("Right Turn")
    rightButton.setAutoDefault(False)
    rightButton.clicked.connect(lambda: turnEia("Right", movie))

    bbox    = QDialogButtonBox()
    bbox.addButton(okButton,                QDialogButtonBox.ActionRole)
    bbox.addButton(singleButton,            QDialogButtonBox.ActionRole)
    bbox.addButton(rightButton,             QDialogButtonBox.ActionRole)


    peia = "".join(map(chr, [101, 105, 97, 46, 103, 105, 102]))
    dp = os.path.join(getPathToProgDir(), g.gresDirectory, peia)

    label = QLabel()
    movie = QMovie(dp)
    label.setMovie(movie)
    movie.start()

    layoutH = QHBoxLayout()
    layoutH.addWidget(bbox)
    layoutH.addStretch()

    layoutV = QVBoxLayout(d)
    layoutV.addLayout(layoutH)
    layoutV.addWidget(label)

    bip()

    d.exec()



##############################################################################
# following code is only relevant for use via 'main()'
# like: 'python3 geigerlog/gdev_audio.py 7'


def getLongChunk(duration, recno):
    """record duration seconds of audio"""

    print("#{} - Recording for {} sec".format(recno, duration))

    reclen = int(sd.default.samplerate * duration)
    mystream = sd.InputStream(blocksize=reclen)
    mystream.start()
    record, overflowed = mystream.read(reclen) # get one record
    g.AudioMultiPulses = record.reshape(-1)
    mystream.stop()


def plotDataT(AudioMultiPulses, inversrate):
    """plot record of sound data"""

    if len(AudioMultiPulses) == 0: return

    # Set "QT_STYLE_OVERRIDE" to avoid this message:
    #   QApplication: invalid style override 'gtk' passed, ignoring it.
    #   Available styles: Windows, Fusion
    os.environ["QT_STYLE_OVERRIDE"] = ""

    fig = plt.figure("Total", figsize=(14, 6), dpi=g.hidpiScaleMPL)

    show = 0    # 1: accumulate the counts (don't delete the figure)
                # 0: delete last figure, and show a fresh record every time
    if    show: pass
    else:       fig.clf()

    x = np.arange(len(g.AudioMultiPulses)) * inversrate * 1000 # create X-axis values
    y = g.AudioMultiPulses                                     # Y-axis values
    #~print("plotDataT: x    :", len(x), x)
    #~print("plotDataT: y    :", len(y), y)
    plt.plot(x, y,  'k.', linestyle='solid', linewidth=0.3, markersize=0.5)
    plt.xlabel("millisec")
    plt.ylim(-35000, 35000)
    plt.pause(.5)


def main():
    """
    Start with: 'python3 gdev_audio.py'   : to get a list of available Sound Devices
    Start with: 'python3 gdev_audio.py N' : to get a list of available Sound Devices, followed
                                            by N recordings and plots from the default device
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
    g.AudioMultiPulses = np.zeros(256)

    try:
        recs = abs(int(sys.argv[1])) # if none given on command line, an exception will be raised
    except:
        recs = 0

    for i in range(0, recs):
        try:
            getLongChunk(1.0, i + 1)
            plotDataT(g.AudioMultiPulses, inversrate)
        except Exception as e:
            print("gdev_audio.py: main: Exception :", e)

    if recs > 0:
        plotDataT(g.AudioMultiPulses, inversrate)
        print("Done recording. To Exit close graph, or press CTRL-C in terminal")
        plt.show()


#####################################################################################################
if __name__ == '__main__':
    """
    Start with: 'python3 gdev_audio.py' to get a list of available Sound Devices
    Start with: 'python3 gdev_audio.py N' to get a list of available Sound Devices, followed
                                          by N recordings and plots from the default device
    like: 'python3 geigerlog/gdev_audio.py 7
    """
    import matplotlib.pyplot as plt # plotting possible only when run as main

    try:
        main()

    except KeyboardInterrupt:
        print()
        print("Exit by CTRL-C")
        print()

