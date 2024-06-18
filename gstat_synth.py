#! /usr/bin/env python3
# -*- coding: UTF-8 -*-

"""
gstat_synth.py - GeigerLog tools for the generation of synthetic data

include in programs with:
    include gstat_synth
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



def createSyntheticData():
    """Create synthetic data and save in log format. All times in SECONDS"""

    ### local def ###############################
    def shd(d):
        return " ".join("%0.2f" % e for e in d)
    ### end local def ###########################

    defname = "createSyntheticData: "

    default_meanlist    = (0.3, 1, 3, 10, 30, 100, 300, 1000, 3000, 10000)
    records             = 200000
    mean                = 20
    # cycletime           = 1.0       # in seconds
    cycletime           = 60.0       # in seconds

    # Dialog to input single mean value, or input 0 to use default list
    mean, okPressed = QInputDialog.getDouble(None, "Create Synthetic Log","CPS Mean: Enter desired mean value, \
                                             \nor 0 to use this default list for CPS mean:\
                                             \n{}\
                                             \n\nFor EXPonential decay enter Tau in days".format(default_meanlist), 20, min=0, max=1000000, decimals=5)
    # gdprint("mean", mean)
    if okPressed:
        if mean > 0:    meanlist = (mean,)
        else:           meanlist = default_meanlist
    else:
        return

    setBusyCursor()

    msg1 = header("Create Synthetic Log CSV file")
    msg2 = "Create logs for mean(s):", "{}\n".format(shd(meanlist))
    fprint(msg1)
    fprint(*msg2)
    dprint(msg1)
    dprint(*msg2)

    QtUpdate() # needed to show fprints

    for mean in meanlist:
    # get array with times
        t = np.float64(np.array(list(range(0, records + 60)))) * cycletime
        dprint(defname + "get time: size: {}, Delta_t: {} sec, Delta_total: {:0.3f} days".format(t.size, (t[1] - t[0]), (t[-1] - t[0]) / 86400))
        dprint(defname + "time data: ", np.int_(t))

    # convert time in sec to datetime strings
        strt0 = "2026-11-13 00:00:00"          # nominal default start datetime - "doomsday equation" https://en.wikipedia.org/wiki/Heinz_von_Foerster
        t0    = mpld.datestr2num(strt0)        # time zero
        td    = np.empty(records, dtype='U19') # holds strings of max length 19
        #print("td, len:", td.size, td)
        for i in range(records):
            td[i] = mpld.num2date(t0 + t[i] / 86400.) # clipped after 19 chars by U19 def

        dprint(defname + "First 3 DateTimes:", td[:3])
        dprint(defname + "Last  3 DateTimes:", td[-3:])


    # get data - select the distribution you want
        stddev = np.sqrt(mean)

        sigt, DataSrc     = getExpPoissonDecay(records + 60, t, mean)                        # exponential decay with tau= mean in days
        # sigt, DataSrc     = getExpDecay(records + 60, t, mean)                             # exponential decay with tau= mean in days
        # sigtM, sigtS, DataSrc     = getDeltaTimePoisson(records + 60, mean)                # delta time between 2 counts (exponential dist)
        # sigt, DataSrc     = getWhiteNoisePoisson(records + 60, mean)                       # White Noise from Poisson Distribution
        # sigt, DataSrc    = getWhiteNoiseNormal(records, mean, stddev)                      # White Noise from Normal Distribution
        # sigt, DataSrc    = getSinus(records, t)                                            # Sine (one or more)
        # sigt, DataSrc    = getWhiteNoiseSine(records, t)                                   # White Noise with Sine
        # sigt, DataSrc    = getConstantData(records, t)                                     # constant + breaks
        # sigt, DataSrc    = getAutocorr(records)                                            # Autocorr as time function
        # sigt, DataSrc    = getRectangle(records)                                           # Rectangle of 20 samples @ 3sec = 1min
        # sigt, DataSrc    = getWhiteNoisePoissonAutocorr(records, mean, cycletime)          # Autocorrelated Poisson Noise !! perhaps problem
        # sigt, DataSrc    = getRandomData(records, mean, stddev)                            # Radom Data

        # Mean=17, followed by mean=29
        #~sigt1, DataSrc     = getWhiteNoisePoisson(int(records / 2), mean=17)                    # White Noise from Poisson Distribution
        #~sigt2, DataSrc2    = getWhiteNoisePoisson(int(records / 2), mean=29)                    # White Noise from Poisson Distribution
        #~sigt = np.concatenate((sigt1 , sigt2))
        #~print("len(sigt):", len(sigt))
        #~DataSrc = "WhiteNoisePoisson,mean=17&29CPM"

        # Mean=17, added to mean=29
        #~sigt1, DataSrc     = getWhiteNoisePoisson(int(records), mean=17)                    # White Noise from Poisson Distribution
        #~sigt2, DataSrc2    = getWhiteNoisePoisson(int(records), mean=29)                    # White Noise from Poisson Distribution
        #~sigt = sigt1 + sigt2
        #~print("len(sigt):", len(sigt))
        #~DataSrc = "WhiteNoisePoisson,mean=17+29CPM"


    # write to csv file
        path = os.path.join(g.dataDir, DataSrc + ".csv")

        with open(path, "wt") as fcsv:
            fcsv.write("#HEADER , {}, SYNTHETIC data: {}\n".format(strt0, DataSrc))
            fcsv.write("#LOGGING, {}, Start @LogCycle: {} sec device 'SYNTHETIC'\n".format(strt0, cycletime))

            maxprints = 10
            for i in range(60, records + 60):                                            # skip the first 60 records to have CPM start with proper values
                dt          = td[i - 60]                                                 # DateTime
                cps         = sigt[i]                                                    # CPS
                # cpm         = int(np.nansum(sigt[max(0, i - 60): i]))                    # CPM as sum of last 60 CPS
                cpm         = np.nansum(sigt[max(0, i - 60): i])                    # CPM as sum of last 60 CPS
                writestring = " {:7d}, {:19s}, {:}, {:}".format(i - 60 + 1, dt, cpm, cps)
                fcsv.write(writestring + "\n")
                if i < 60 + maxprints or i >= (records + 60 - maxprints): print(writestring)

            msg = "Saved to file: {}\n".format(path)
            fprint(msg)
            dprint(msg)


        # for : getDeltaTimePoisson
        # with open(path, "wt") as fcsv:
        #     fcsv.write("#HEADER , {}, SYNTHETIC data: {}\n".format(strt0, DataSrc))
        #     fcsv.write("#LOGGING, {}, Start @LogCycle: {} sec device 'SYNTHETIC'\n".format(strt0, cycletime))

        #     npsigtM     = np.array(sigtM)
        #     npsigtS     = np.array(sigtS)

        #     maxprints = 10
        #     for i in range(60, records + 60):                                            # skip the first 60 records to have CPM start with proper values
        #         dt          = td[i - 60]                                                 # DateTime
        #         cps         = npsigtS[i]                                                 # CPS
        #         # cpm         = int(np.nansum(npsigt[max(0, i - 60): i]))                # CPM as sum of last 60 CPS
        #         cpm         = npsigtM[i]                                                 # CPM
        #         writestring = " {:7d}, {:19s}, {:}, {:}".format(i - 60 + 1, dt, cpm, cps)
        #         fcsv.write(writestring + "\n")
        #         if i < 60 + maxprints or i >= (records + 60 - maxprints): print(writestring)

        #     msg = "Saved to file: {}\n".format(path)
        #     fprint(msg)
        #     dprint(msg)

    setNormalCursor()


def getDeltaTimePoisson(records, mean):
    """The length of the intervall of two successive Poisson events
    records: number of records to return
    mean:    in CPS
    return:  distribution with times in µs
    """

    defname = "getDeltaTimePoisson_"
    DataSrc = "DeltaTimePoisson_CPSmean={}".format(mean)

    cpm     = np.random.poisson(mean * 60, size=records)             # true CPM
    cps     = np.random.exponential(1 / mean, size=records) * 1E6    # CPS as duration before next pulse in µs

    msgM     = "Resulting Data:", defname + "CPM:  size:{}, mean={:0.4f}, var={:0.4f}".format(cpm.size, np.mean(cpm), np.var(cpm))
    msgS     = "Resulting Data:", defname + "CPS:  size:{}, mean={:0.4f}, var={:0.4f}".format(cps.size, np.mean(cps), np.var(cps))
    fprint(*msgM)
    fprint(*msgS)
    dprint(*msgM)
    dprint(*msgS)

    return cpm, cps, DataSrc


def getExpPoissonDecay(records, time, taudays):
    """Exponential decay data half-life taudays in days"""

    defname = "getExpPoissonDecay: "
    DataSrc = defname + "tau={} days".format(taudays)
    tau     = taudays * 24 * 60 * 60                                # tau: days ---> sec
    xmean   = 1000 * np.exp(-np.log(2) / tau * (time - 60)) + 5     # get the exp function; add a background of 5 for CPS
    x       = np.random.poisson(xmean)                              # overlay poisson random

    msg     = "Resulting Data:",   defname + "size:{}, mean={:0.4f}, var={:0.4f}".format(x.size, np.mean(x), np.var(x))
    fprint(*msg)
    dprint(*msg)

    return x, DataSrc


def getExpDecay(records, time, taud):
    """Exponential decay data tau in days"""

    defname = "getExpDecay"
    DataSrc = defname + "tau={} days".format(taud)
    tau     = taud * 24 * 60 * 60           # days ---> sec
    x       = 1000 * np.exp(-np.log(2) / tau * (time - 60))

    xtext   = defname + "size:{}, mean={:0.4f}, var={:0.4f}".format(x.size, np.mean(x), np.var(x))
    msg     = "Resulting Data:", xtext
    fprint(*msg)
    dprint(*msg)

    return x, DataSrc


def getWhiteNoisePoisson(records, mean):
    """White noise data drawn from Poisson distribution"""

    defname = "getWhiteNoisePoisson_"
    DataSrc = defname + "CPSmean={}".format(mean)

    x       = np.random.poisson(mean, size=records)

    xtext   = defname + "size:{}, mean={:0.4f}, var={:0.4f}".format(x.size, np.mean(x), np.var(x))
    msg     = "Resulting Data:", xtext
    fprint(*msg)
    dprint(*msg)

    return x, DataSrc


def getWhiteNoiseNormal(records, mean, stddev):
    """White noise data drawn from Normal distribution"""

    defname = "getWhiteNoiseNormal_"
    DataSrc = defname + "CPSmean={}_std={:3.2f}".format(mean, stddev)

    x       = np.random.normal(mean, stddev, size=records)

    xtext   = defname + "size:{}, mean={:0.3f}, var={:0.3f}, std={:0.3f}".format(x.size, np.mean(x), np.var(x), np.std(x))
    msg = "Resulting Data:", xtext
    fprint(*msg)
    dprint(*msg)

    return x, DataSrc


def getWhiteNoisePoissonAutocorr(records, mean, cycletime):
    """White noise data drawn from Poisson distribution"""
    # review results before using!!!

    DataSrc = "Autocorrelated Poisson Noise, CPM={}, cycle={}sec".format(mean, cycletime)

    x    = np.random.poisson(mean / 60., size=records * 60 + 60 )
    print("x.size, x.mean, x.var, x.std. :", x.size, np.mean(x), np.var(x), np.std(x))
    print(x)

    x2   = np.zeros(records)
    print("all zeros: x2.size, x2.mean, x2.var, x2.std. :", x2.size, np.mean(x2), np.var(x2), np.std(x2))

    for i in range(0, records):
        j = i * cycletime
        x2[i] = np.sum(x[j : j + 60])

    print("x2.size, x2.mean, x2.var, x2.std. :", x2.size, np.mean(x2), np.var(x2), np.std(x2))

    return x2, DataSrc


def getSinus(records, t):
    """
    sinus data
    All times in seconds
    """

    DataSrc = "Sinus"
    pi2     = 2.0 * np.pi

    x   = 10.0 + 5.0 * np.sin(t * pi2 / (100  * 60 +  0)  ) # periode von 100   min
    x  +=  0.0 + 5.0 * np.sin(t * pi2 / (400  * 60 +  0)  ) # periode von 400   min
    x  +=  0.0 + 5.0 * np.sin(t * pi2 / ( 30  * 60 +  0)  ) # periode von  50   min
    x  +=  0.0 + 5.0 * np.sin(t * pi2 / (  3  * 60 +  4)  ) # periode von   3.x min
    x  +=  0.0 + 5.0 * np.sin(t * pi2 / (  3  * 60 +  9)  ) # periode von   3.y min
    x  +=  0.0 + 5.0 * np.sin(t * pi2 / (  3  * 60 + 13)  ) # periode von   3.z min
    x  +=  0.0 + 5.0 * np.sin(t * pi2 / (  1           )  ) # periode von   1   sec
    x  +=  0.0 + 5.0 * np.sin(t * pi2 / (  0.5         )  ) # periode von   0.5 sec

    return x, DataSrc


def getConstantData(records, t):
    """
    constant data
    All times in seconds
    """

    DataSrc = "Constant + Breaks"
    x       = np.ones(records) * 1000

    for i in range(0, records - 10, 20):
        x[i]     = 500
        x[i + 1] = -10
        x[i + 2] =   1

    return x, DataSrc


def getAutocorr(records):
    """
    The autocorrelation function as time series to use as input
    All times in seconds
    """

    DataSrc = "Autocorrelation as time series - 1st point=1"

    # a small random component
    mean = 0
    std  = 0.01
    x    = np.random.normal(mean, std, size=records)

    #for a 1 sec cycle time the first 60 records will show a linear down curve
    #for i in range (0, 20):
    #    x[i] = 1 - i * 1/20

    x[0] = 1


    return x, DataSrc


def getRectangle(records):
    """
    A rectangle 1 min long with 20 samples @assumed 3sec cycle, otherwise zeros
    """

    DataSrc = "Rectangle_1min"
    x       = np.zeros(records)
    #print x
    for i in range(20): x[i] = 1
    print("x: len:", len(x), x)

    return x, DataSrc


def getWhiteNoiseSine(records, t):
    """
    White noise with Sine data
    """

    DataSrc = "WhiteNoiseNormal + Sine"
    pi2     = 2.0 * np.pi

    mean = 2500
    std  = np.sqrt(mean)
    x    = np.random.normal(mean, std, size=records)
    p1   = (100 * 60 + 1.4) / 60  # 100,0333 min
    print("getWhiteNoiseSinusData: p1:", p1)
    x   +=  40 * std * (np.sin(t * pi2 / p1 ))
    x   +=  10 * std * (np.sin(t * pi2 / 11 ))

    return x, DataSrc


def getRandomData(records, mean, stddev):
    """random data from a uniform range of 0 ... 2*mean"""

    DataSrc = "Random Data_mean={}_postive_uniform_range0...{}".format(mean, 2 * mean)

    x = mean * 2 * np.random.rand(records)
    print(DataSrc, x)

    return x, DataSrc
