#! /usr/bin/python3
# -*- coding: utf-8 -*-

"""
gaudio.py - GeigerLog commands to handle the audio clicks as CPM/CPS input
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
__copyright__       = "Copyright 2016, 2017, 2018, 2019"
__credits__         = [""]
__license__         = "GPL3"


"""
Requires Python module pyaudio. Recommended installation is via pip. Make sure
to use the pip command for Python3 if you also have a Python2 installation:
      sudo -H pip install pyaudio --upgrade
or:   sudo -H pip3 install pyaudio --upgrade

Current version of pyaudio (Feb 2019): 0.2.11

To allow installation with pip any pyaudio installation on Linux with the
package manager (like apt-get on Ubuntu) must be un-installed first. Then you
may need to install files with the package manager:
- libjack-jackd2-dev
- portaudio19-dev
- python-all-dev.

There is no wheel (prebuilt package) for Python 3.7 on Windows (there is one
for Python 2.7 and 3.4 up to 3.6). Christoph Gohlke (University of California)
hosts Windows wheels for most popular packages for nearly all modern Python
versions, including latest PyAudio. You can find it here:
https://www.lfd.uci.edu/~gohlke/pythonlibs/ .
After download, just type pip install <downloaded file here>.

To overcome admin limits on Windows you may need to install with --user option:
    pip install pyaudio --upgrade --user
    pip3 install pyaudio --upgrade --user

"""

from   gutils       import *


def initAudio():
    """Start the thread to monitor the audio pulses for clicks"""

    global audioThread

    errmsg  = ""                            # there is no error possible here
    gglobs.AudioDeviceName = "AudioCounter"

    if gglobs.AudioPulseDir     == "auto": gglobs.AudioPulseDir     = False # negative
    if gglobs.AudioPulseMax     == "auto": gglobs.AudioPulseMax     = 32768
    if gglobs.AudioThreshold    == "auto": gglobs.AudioThreshold    = 60
    if gglobs.AudioVariables    == "auto": gglobs.AudioVariables    = "CPM3rd, CPS3rd"
    if gglobs.AudioCalibration  == "auto": gglobs.AudioCalibration  = 0.09

    # depending on where the AudioCounter is mapped to, the calibration of those
    # vars must also be set:
    if   "2nd" in gglobs.AudioVariables:                # CPM2nd, CPS2nd
        gglobs.calibration2nd = gglobs.AudioCalibration

    elif "3rd" in  gglobs.AudioVariables:               # CPM3rd, CPS3rd
        gglobs.Calibration3rd = gglobs.AudioCalibration

    else:                                               # CPM, CPS, CPM1st, CPS1st
        gglobs.calibration = gglobs.AudioCalibration

    DevVars = gglobs.AudioVariables.split(",")
    for i in range(0, len(DevVars)):  DevVars[i] = DevVars[i].strip()
    gglobs.DevicesVars["Audio"] = DevVars
    #print("DevicesVars:", gglobs.DevicesVars)

    FORMAT     = pyaudio.paInt16        # "16 bit int"
    CHANNELS = 1                        # Mono; for Stereo set: #CHANNELS = 2

    #RATE = 96000
    #RATE = 44100
    #RATE = 22050
    #RATE = 11025
    RATE = 2**15                        # = 32768

    #CHUNK = 64
    #CHUNK = 128
    CHUNK = 256
    #CHUNK = 512
    #CHUNK = 1024
    #CHUNK = 2048
    #CHUNK = 4096

    gglobs.AudioFormat   = FORMAT
    gglobs.AudioChannels = CHANNELS
    gglobs.AudioRate     = RATE
    gglobs.AudioChunk    = CHUNK

    # Portaudio Sample Formats
    # paFloat32, paInt32, paInt24, paInt16, paInt8, paUInt8, paCustomFormat
    if gglobs.AudioFormat == pyaudio.paInt16: gglobs.AudioFormatText = "16 bit int"
    else:                                     gglobs.AudioFormatText = "undefined"

    gglobs.AudioThreadStop = False
    audioThread = threading.Thread(target=audioThreadTarget, args=(None,))
    audioThread.start()

    gglobs.AudioConnection = True

    return errmsg


def terminateAudio():
    """Stop the thread to monitor the audio pulses for clicks"""

    global audioThread

    if not gglobs.AudioConnection: return "No AudioCounter connection"

    gglobs.AudioThreadStop = True

    # wait for thread to end, but wait not longer than 5 sec
    start = time.time()
    while audioThread.is_alive() and (time.time() - start) < 5:
        time.sleep(0.1)
        pass            # wait for thread to end
    dprint("terminateAudio: thread-status: is alive: ", audioThread.is_alive())

    gglobs.AudioConnection = False

    return "AudioCounter Terminated"


def getAudioInfo(extended = False):
    """Info on settings of the audio thread"""

    if not gglobs.AudioConnection:   return "No connected device"

    AudioInfo = """Connected Device:             {}
Sound:                        {} (auto-OFF during logging)
Configured Variables:         {}
Geiger tube calib. factor:    {} µSv/h/CPM""".format(  \
                                    gglobs.AudioDeviceName, \
                                    "ON" if gglobs.AudioWithSound else "OFF", \
                                    gglobs.AudioVariables,  \
                                    gglobs.AudioCalibration)
    if extended == True:
        AudioInfo += """
AudioCounter Sampling Details:
- FORMAT:                     {}
- CHANNELS:                   {} (1=Mono, 2=Stereo)
- RATE:                       {} (Samples per second)
- CHUNK:                      {} (Samples per read)
- Pulse Height Max            {} (System reported max signal)
- Pulse Direction             {} (negative or positive)
- Pulse Threshold             {}% of Pulse Height Max to trigger count""".format(\
                                    gglobs.AudioFormatText, \
                                    gglobs.AudioChannels,   \
                                    gglobs.AudioRate,       \
                                    gglobs.AudioChunk,      \
                                    gglobs.AudioPulseMax,   \
                                    ("POSITIVE" if gglobs.AudioPulseDir else "NEGATIVE"),\
                                    gglobs.AudioThreshold,  \
                                    )
    return AudioInfo


def toggleAudioSound():
    """toggle the click sound between OFF and ON"""

    gglobs.AudioWithSound = not gglobs.AudioWithSound

    fprint(header("Switching Sound Output of AudioCounter"))
    if gglobs.AudioWithSound: sound = "ON "
    else:                     sound = "OFF"

    fprint("New sound output setting: {}  (auto-OFF during logging)".format(sound))


def toggleAudioPulseDir():
    """toggle which pulse direction is sensed"""

    gglobs.AudioPulseDir = not gglobs.AudioPulseDir

    fprint(header("Switching Pulse Direction of AudioCounter"))
    if gglobs.AudioPulseDir:  direction = "POSITIVE"
    else:                     direction = "NEGATIVE"
    gglobs.AudioPlotTotal = gglobs.AudioPlotTotal[-10:]

    fprint("New pulse direction setting: {}".format(direction))


def getAudioValues(varlist):
    """Read all audio data; return empty dict when not available"""

    alldata = {}

    if not gglobs.AudioConnection: # AudioCounter is NOT connected!
        dprint("getAudioValues: AudioCounter is not connected")
        return alldata

    if varlist == None:
        return alldata

    for vname in varlist:
        if   vname in ("CPM", "CPM1st", "CPM2nd", "CPM3rd"):
            cpm             = gglobs.AudioLastCpm
            cpm             = scaleVarValues(vname, cpm, gglobs.ValueScale[vname])
            alldata.update(  {vname: cpm})

        elif vname in ("CPS", "CPS1st", "CPS2nd", "CPS3rd"):
            cps             = gglobs.AudioLastCps
            cps             = scaleVarValues(vname, cps, gglobs.ValueScale[vname] )
            alldata.update(  {vname: cps})

    vprint("{:20s}:  Variables:{}  Data:{}  ".format("getAudioValues", varlist, alldata))

    return alldata


def getLongChunk(duration):
    """record duration seconds of audio, no trigger applied"""

    FORMAT    = gglobs.AudioFormat
    CHANNELS  = gglobs.AudioChannels
    RATE      = gglobs.AudioRate
    CHUNK     = gglobs.AudioChunk

    audio     = pyaudio.PyAudio()
    instream  = audio.open(format=FORMAT, channels=CHANNELS, rate=RATE, frames_per_buffer=CHUNK, input =True)

    try: # get duration sec of recording for plotAudio
        record   = instream.read(int(RATE * duration), exception_on_overflow = False)
    except:
        # failure; just return some data
        duration = 0
        record   = np.full(256, 0)   # creating some data

    npdata                = np.frombuffer(record, dtype='<i2') # convert to np array
    gglobs.AudioPlotTotal = npdata

    return duration


def audioThreadTarget(Dummy):
    """The thread to read the audio input"""

    FORMAT    = gglobs.AudioFormat
    CHANNELS  = gglobs.AudioChannels
    RATE      = gglobs.AudioRate
    CHUNK     = gglobs.AudioChunk

    audio     = pyaudio.PyAudio()
    outstream = audio.open(format=FORMAT, channels=CHANNELS, rate=RATE, frames_per_buffer=CHUNK, output=True)
    instream  = audio.open(format=FORMAT, channels=CHANNELS, rate=RATE, frames_per_buffer=CHUNK, input =True)

    try: # discard 2 sec of recording to avoid the initial screech
        junk  = instream.read(int(RATE * 2), exception_on_overflow = False)
    except:
        pass

    gglobs.AudioLastCps     = 0
    gglobs.AudioLastCpm     = 0
    cps_count               = 0
    llimit                  = gglobs.AudioThreshold / 100 * gglobs.AudioPulseMax

    cpm_counter             = np.full(60, 0)            # storing last 60 sec of CPS values
    gglobs.AudioPlotTotal   = np.array([0])             # time courses for last ~40 of the pulses
    nandata                 = np.full(10, gglobs.NAN)   # creating a gap of 10 values
    cstart                  = time.time()
    chunks40                = (CHUNK + 10) * 40

    while not gglobs.AudioThreadStop:
        try:
            data   = instream.read(CHUNK, exception_on_overflow = False)
        except Exception as e:
            dprint("audioThreadTarget: Exception instream.read: e: ", e)
            data = b"\x00\x00"

        # allow sound activation during logging only when in development
        if gglobs.devel:                                    # in development
            if gglobs.AudioWithSound:
                outstream.write(data)
        else:                                               # NOT in development
            if not gglobs.logging:                          # NOT logging
                if gglobs.AudioWithSound:
                    outstream.write(data)

        npdata = np.frombuffer(data, dtype='<i2') # convert to np array for easy min/max

        gotCount = False
        if gglobs.AudioPulseDir:                  # True -> positive pulse
            if npdata.max() > llimit:
                gotCount = True
        else:                                     # False -> negative pulse
            if npdata.min() < -llimit:
                gotCount = True

        if gotCount:
            cps_count  += 1
            gglobs.AudioPlotTotal  = np.concatenate((gglobs.AudioPlotTotal, nandata, npdata))[-chunks40:]

        deltat = time.time() - cstart
        if deltat >= 1:
            gglobs.AudioLastCps     = int(round(cps_count / deltat, 0))
            cpm_counter             = np.append(cpm_counter, gglobs.AudioLastCps)[1:]
            gglobs.AudioLastCpm     = int(np.sum(cpm_counter))
            #print("                                             DeltaT:{},  CPM, CPS:".format(deltat), gglobs.AudioLastCpm, gglobs.AudioLastCps)
            cps_count               = 0
            cstart                  = time.time()

    instream    .stop_stream()
    outstream   .stop_stream()
    instream    .close()
    outstream   .close()

    audio.terminate()


##############################################################################
# following only relevant for use via 'main()'

def plotDataT(AudioPlotTotal, irate):
    """This one used to plot either AudioPlotSingle or AudioPlotTotal of sound data"""

    if len(AudioPlotTotal) == 0: return

    fig = plt.figure("Total", figsize=(14, 6))
    fig.clf()

    #print("plotDataT: AudioPlotTotal:", len(AudioPlotTotal), AudioPlotTotal)
    x = np.arange(len(AudioPlotTotal)) * irate * 1000
    #print("plotDataT: x    :", len(x), x)
    plt.xlabel("millisec")
    plt.plot(x, AudioPlotTotal,  'k.', linestyle='solid', linewidth=0.3, markersize=0.5)
    plt.ylim(-35000, 35000)
    plt.pause(.5)


def main():

    duration                = 39   # sec of recording
    irate                   = 1 / gglobs.AudioRate
    gglobs.AudioPlotTotal   = np.zeros(256)

    gglobs.devel               = True                # to allow sound
    gglobs.AudioActivation     = True
    gglobs.AudioDeviceName     = "None"              # set by init
    gglobs.AudioPulseDir       = False               # False for negative; True for positive pulse
    gglobs.AudioThreshold      = 60                  # Percentage of pulse height to trigger a count
                                                     # 60% of +/- 32768 (max for 16 bit signal) => ~20000
    print("initAudio:", initAudio())

    gglobs.AudioWithSound      = True

    start = time.time()
    while (time.time() - start) <= duration:
        time.sleep(.15)
        now = time.time()
        try:
            print("time: {:5.3f}, gglobs.AudioLastCps: {:5.1f}, gglobs.AudioLastCpm: {:5.1f}".format((now -start), gglobs.AudioLastCps, gglobs.AudioLastCpm ))
            plotDataT(gglobs.AudioPlotTotal, irate)
        except Exception as e:
            print("gaudio: main: Exception :", e)

    print("terminateAudio:", terminateAudio())

    plotDataT(gglobs.AudioPlotTotal, irate)
    plt.show()


if __name__ == '__main__':
    import matplotlib.pyplot as plt # plotting possible only when run as main
    main()
