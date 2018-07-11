#!/usr/bin/python
# -*- coding: UTF-8 -*-

"""
gplot.py - to plot data from Geiger Counter
available in the form:

#BIndx Date&Time            CPM
    12,2017-01-11 11:01:33, 17
    13,2017-01-11 11:02:33, 20

(no space to the left and right of Date&Time!)
"""

import sys
import os
import time
import numpy as np

import matplotlib.pyplot as plt
import matplotlib.dates as mpld
#import matplotlib.dates  as mdates     # special for axes formatting
#import matplotlib.ticker as ticker     # special for axes formatting
from matplotlib.ticker import FuncFormatter

import gglobs
from   gutils import *

__author__          = "ullix"
__copyright__       = "Copyright 2016"
__credits__         = [""]
__license__         = "GPL"


# used for the plots
color = {}
color['avg']        = 'black'          # line for average
color['cpm']        = 'blue'           # CPM, CPS count data
color['mav']        = 'red'            # Moving Average
color['mavbg']      = 'yellow'         # Moving Average Background

legendPlacement = {0:'upper left', 1:'upper center', 2:'upper right', 3:'center right', 4:'lower right', 5:'lower center', 6:'lower left', 7:'center left', 8:'center'}


def printDataProp(alldata = True):

    if gglobs.logging: # due to plot updates not updating the arrays need to call makePlot
        if gglobs.currentFilePath == gglobs.logFilePath:
            makePlot()

    if alldata:
        logTime  = gglobs.logTime
        cpm      = gglobs.logCPM
    else:
        logTime  = gglobs.logTimeSlice
        cpm      = gglobs.logCPMSlice

    try:
        sizeSlice    = cpm.size # fails if cpm not built for lack of data
    except:
        return

    if gglobs.Yunit == 'CPM':
        count_factor = 1.0
        count_text   = "CPM"

    elif gglobs.Yunit == 'CPS':
        count_factor = 1.0 / 60.0
        count_text   = "CPS"

    else:
        count_factor = gglobs.calibration
        count_text   = u"µSv/h"

    count           = cpm * count_factor

    count_max       = count.max()
    count_min       = count.min()
    count_avg       = np.mean(count)
    count_med       = np.median(count)
    count_var       = np.var(count)
    count_std       = np.std(count)
    count_err       = count_std / np.sqrt(count.size)
    count_sqrt      = np.sqrt(count_avg)
    count_95        = count_std * 1.96   # 95% confidence range

    logtime_size    = logTime.size
    logtime_max     = logTime.max()
    logtime_min     = logTime.min()
    logtime_delta   = logtime_max - logtime_min # in days

    fprint("Totals")
    fprint("  Records = {:8,.0f}     Filesize = {:,} Bytes".format(sizeSlice, os.path.getsize(gglobs.currentFilePath)))
    fprint("  Counts  = {:8,.0f}     Counts calculated as: Average CPM * Log Duration[min]\n".format(np.mean(cpm) * logtime_delta * 24 * 60))

    fprint(u"{:<5s}                    of avg".format(count_text))
    fprint("  Average   ={:8.2f}      100%       Min  ={:8.0f}        Max  ={:8.0f}" .format(count_avg,                              count_min,          count_max)          )
    fprint("  Variance  ={:8.2f} {:8.0f}%"                                          .format(count_var,  count_var  / count_avg * 100.))
    fprint("  Std.Dev.  ={:8.2f} {:8.0f}%       LoLim={:8.0f}        HiLim={:8.0f}" .format(count_std,  count_std  / count_avg * 100.,  count_avg-count_std,  count_avg+count_std)  )
    fprint("  Sqrt(Avg) ={:8.2f} {:8.0f}%       LoLim={:8.0f}        HiLim={:8.0f}" .format(count_sqrt, count_sqrt / count_avg * 100.,  count_avg-count_sqrt, count_avg+count_sqrt) )
    fprint("  Std.Err.  ={:8.2f} {:8.0f}%       LoLim={:8.0f}        HiLim={:8.0f}" .format(count_err,  count_err  / count_avg * 100.,  count_avg-count_err,  count_avg+count_err) )
    fprint("  Median    ={:8.2f} {:8.0f}%       P_5% ={:8.0f}        P_95%={:8.0f}" .format(count_med,  count_med  / count_avg * 100., np.percentile(count, 5), np.percentile(count, 95)))
    fprint("  95% Conf*)={:8.2f} {:8.0f}%       LoLim={:8.0f}        HiLim={:8.0f}" .format(count_95,   count_95   / count_avg * 100.,  count_avg-count_95,   count_avg+count_95)   )
    fprint("  *)Valid only for Normal Distribution\n")

    oldest   = (str(mpld.num2date(logtime_min)))[:19]
    youngest = (str(mpld.num2date(logtime_max)))[:19]

    fprint("Time")
    fprint("  Oldest rec    = {}  (time={:0.3f} d)".format(oldest,   0))
    fprint("  Youngest rec  = {}  (time={:0.3f} d)".format(youngest, logtime_max - logtime_min))
    fprint("  Duration      = {:0.0f} s   ={:0.1f} m   ={:0.2f} h   ={:0.3f} d".format(logtime_delta *86400., logtime_delta*1440., logtime_delta *24., logtime_delta))
    fprint("  Cycle average = {:0.2f} s".format(logtime_delta *86400./ (sizeSlice -1)))

    r = min (sizeSlice, 3)
    fprint("\nFirst and last {} records:".format(r))
    fprint(u"      RecNo  Date&Time                CPM         CPS       µSv/h")
    for i in range(0, r):
        fprint("   {:8d}  {:s} {:8.0f}    {:8.2f}    {:8.2f}".format(i, (str(mpld.num2date(logTime[i])))[:19], cpm[i], cpm[i] / 60.0, cpm[i] * gglobs.calibration))
    for i in range(logtime_size - r, logtime_size):
        fprint("   {:8d}  {:s} {:8.0f}    {:8.2f}    {:8.2f}".format(i, (str(mpld.num2date(logTime[i])))[:19], cpm[i], cpm[i] / 60.0, cpm[i] * gglobs.calibration))


def getTsr(Tfirst, Tdelta):
    """Get Time since first record in best unit"""

    l = Tdelta - Tfirst

    if l > 3:
        unit = "day"
        t = l
    elif l * 24. > 3:
        unit = "hour"
        t = l * 24.
    elif l * 1440. > 3:
        unit = "minute"
        t = l * 1440.
    else:
        unit = "second"
        t = l * 86400.

    #print "t, unit:", t, unit
    return "{:0.3f} {}s".format(t, unit)


def getToD(Tfirst, delta, deltaUnit):
    """From time of first record = Tfirst plus the delta time in days
    return TimeOfDay"""

    #print "gglobs.XunitCurrent", gglobs.XunitCurrent
    if deltaUnit == "hour":
        x = delta / 24.
    elif deltaUnit == "minute":
        x = delta / 24. / 60.
    elif deltaUnit == "second":
        x = delta / 24. / 60. / 60.
    else:
        x = delta # delta is in the correct unit day

    ret = str(mpld.num2date(Tfirst + x))[:19]
    #print "ret:", ret
    return ret


def getXLabelsToD():
    global plotTime, strFirstRecord

    totalDays     = (plotTime.max() - plotTime.min()) # in days
    # find proper label for x-axis and x-ticks
    if totalDays > 5:
        #print 1
        tformat = '%Y-%m-%d  %H:%M:%S'
    elif totalDays > 1:
        #print 2
        tformat = '%Y-%m-%d  %H:%M:%S'
    elif totalDays * 24. > 1:
        #print 3
        tformat = '%Y-%m-%d  %H:%M:%S'
    elif totalDays * 24. * 60. > 1:
        #print 4
        tformat = '%H:%M:%S'
    elif totalDays * 24. * 60. * 60. > 1:
        #print 5
        tformat = '%H:%M:%S'
    else:
        #print 6
        tformat = '%Y-%m-%d  %H:%M:%S'

    return tformat, 'Time (First Record: {})'.format(strFirstRecord)


def getXLabelsSince(Xunit):
    global plotTime, strFirstRecord

    if Xunit == "auto":
        l = plotTime.max() - plotTime.min()
        #print l
        if l > 3:
            Xunit = "day"
        elif l * 24. > 3:
            #print l * 24.
            Xunit = "hour"
        elif l * 1440. > 3:
            #print l *1440.
            Xunit = "minute"
        else:
            Xunit = "second"

    gglobs.XunitCurrent = Xunit

    # now we have the new Xunit or "auto" was not requested
    # rescale the time and prepare label for the x axis
    if Xunit == "minute":
        plotTime = plotTime * 1440.     # convert to minutes
        xlabel = '[min]'
    elif Xunit == "hour":
        plotTime = plotTime * 24.       # convert to hours
        xlabel = '[hours]'
    elif Xunit == "day":
        plotTime = plotTime             # is in days convert to days
        xlabel = '[days]'
    else:
        # Xunit == "s", time is in days
        # or no Xunit given
        #Xunit = "second"
        plotTime = plotTime * 86400.
        xlabel = '[seconds]'

    return 'time {} since first record: {}'.format(xlabel, strFirstRecord)


def updatePlot(filePath, timetag, cpm):
#def updatePlot(timetag, cpm):
    """updates an existing plot (made by makePlot) with last record"""

    start= time.time()

    try:
        x = gglobs.logTime[0]   # logTime is defined only after 1st plot
    except:
        print "updatePlot, no gglobs.logTimeSlice.size"
        return

    if gglobs.XunitCurrent == "Time":
        # plot versus Date&Time of day
        ptime = mpld.datestr2num(timetag)
    else:
        # Plot vs DiffTime (time since first record)
        # XunitCurrent is one of second, minute, hour day
        ptime = mpld.datestr2num(timetag) - gglobs.logTime[0]

    # rescale for X-axis
    if gglobs.XunitCurrent   == "second":
        ptime = ptime * 86400.              # convert to seconds
    elif gglobs.XunitCurrent == "minute":
        ptime = ptime * 1440.               # convert to minutes
    elif gglobs.XunitCurrent == "hour":
        ptime = ptime * 24.                 # convert to hours
    elif gglobs.XunitCurrent == "day":
        pass                                # is in days already
    else:
        pass                                # gglobs.XunitCurrent is "Time"

    # rescale for Y-axis
    if gglobs.Yunit == "CPS":
        cpm /= 60.

    #print "ptime:", ptime, "cpm:", cpm

    rdplt.set_xdata(np.append(rdplt.get_xdata(), ptime))
    rdplt.set_ydata(np.append(rdplt.get_ydata(), cpm))

    gglobs.sizePlotSlice += 1

    plotSubTitle = 'File:' + os.path.basename(filePath) + "  Recs:" + str(gglobs.sizePlotSlice)
    plt.title(plotSubTitle, fontsize=12, fontweight='normal', loc = 'right')

    ax = plt.gca()
    ax.relim()              # recompute the ax.dataLim
    ax.autoscale_view()     # update ax.viewLim using the new dataLim

    #plt.draw()   # seems to be unnecessary

    stop = time.time()
    dprint(gglobs.debug, "makePlot: update: {:0.1f} ms Total".format( (stop - start) * 1000.))


def makePlot(fprintMAV = False):
    """Plots the data in array gglobs.currentFileData vs. time-of-day or
    vs time since start, observing plot settings;
    using matplotlib date functions which begin at the epoch, i.e. year 0001

    Return: nothing
    """

    global plotTime, strFirstRecord, rdplt, fig

    try:
        if gglobs.currentFileData.size == 0:
            dprint(gglobs.debug, "makePlot: no records; nothing to plot")
            fig = plt.figure(1)
            plt.clf()                                    # clear figure
            fig.canvas.draw_idle()
            return
    except:
        # if there is no gglobs.currentFileData then .size results in error
        # but then there is also nothing to plot
        dprint(gglobs.debug, "makePlot: except: no 'gglobs.currentFileData', nothing to plot")
        fig = plt.figure(1)
        plt.clf()                                    # clear figure
        fig.canvas.draw_idle()
        return

    start                   = time.time()            # timing durations

    filePath                = gglobs.currentFilePath
    gglobs.logTime          = gglobs.currentFileData[:,0]           # time data of total file
    gglobs.logCPM           = gglobs.currentFileData[:,1]           # CPM data of total file
    gglobs.logTimeFirst     = gglobs.logTime[0]                     # time of first record in total file
    gglobs.logTimeDiff      = gglobs.logTime - gglobs.logTimeFirst  # using time diff to first record in days

    strFirstRecord = (str(mpld.num2date(gglobs.logTimeFirst)))[:19]

    if gglobs.Xunit == "Time" :
        plotTime  = gglobs.logTime
        xFormatStr, xLabelStr = getXLabelsToD()
    else:
        plotTime  = gglobs.logTimeDiff
        xLabelStr = getXLabelsSince(gglobs.Xunit)

    gglobs.plotTime = plotTime

    # confine limits to what is available
    Xleft = gglobs.Xleft
    Xright= gglobs.Xright

    #dprint(gglobs.debug, "before re-setting limits: Xleft, Xright, plotTime.min, plotTime.max   {}   {}   {}   {}".format(gglobs.Xleft, gglobs.Xright, plotTime.min(), plotTime.max()))
    if Xright == None or Xright > plotTime.max():    Xright = plotTime.max()
    if                   Xright < plotTime.min():    Xright = plotTime.min()
    if Xleft  == None or Xleft  < plotTime.min():    Xleft  = plotTime.min()
    if                   Xleft  > plotTime.max():    Xleft  = plotTime.max()
    #dprint(gglobs.debug, "after                                                                 {}   {}   {}   {}".format(Xleft, Xright, plotTime.min(), plotTime.max()))

    # find the records, where the time limits apply
    recmin = np.where(plotTime >= Xleft )[0][0]
    recmax = np.where(plotTime <= Xright)[0].max() # excludes recs > gglobs.Xleft, and takes max of remaining
    #dprint(gglobs.debug, "recmin, recmax:", recmin, recmax)

    # slice the arrays; include record #recmax (thus +1)
    gglobs.logTimeSlice      = gglobs.logTime     [recmin:recmax + 1 ]
    gglobs.logTimeDiffSlice  = gglobs.logTimeDiff [recmin:recmax + 1 ]
    gglobs.logCPMSlice       = gglobs.logCPM      [recmin:recmax + 1 ]
    gglobs.plotTimeSlice     = gglobs.plotTime    [recmin:recmax + 1 ]

    gglobs.sizePlotSlice = gglobs.plotTimeSlice.size
    #dprint(gglobs.debug, "gglobs.sizePlotSlice:", gglobs.sizePlotSlice)


    if gglobs.sizePlotSlice == 0:
        fprint("ALERT: No records in selected range")
        return

    stopprep   = time.time()
    stopwatch  = "makePlot: {:6.1f}ms for data load and prep, ".format((stopprep - start) * 1000.)

    ###########################################################################
    # prepare the graph
    ###########################################################################
    fig = plt.figure(1)                          # need fig for later
    plt.clf()                                    # clear figure
    plt.grid(True)
    ax  = plt.gca()
    #plt.title('Count Rate History', fontsize=16, fontweight='bold', loc = 'left')
    plt.title('Count Rate History', fontsize=14, fontweight='bold', loc = 'left')
    plotSubTitle = 'File:' + os.path.basename(filePath) + "  Recs:" + str(gglobs.sizePlotSlice)
    #plt.title(plotSubTitle, fontsize=12, fontweight='normal', loc = 'right')
    plt.title(plotSubTitle, fontsize=10, fontweight='normal', loc = 'right')
    #plt.subplots_adjust(hspace=None, wspace=.2 , left=.12, top=0.93, bottom=0.10, right=.97)
    plt.subplots_adjust(hspace=None, wspace=.2 , left=.12, top=0.93, bottom=0.15, right=.97)


    plt.ticklabel_format(useOffset=False)       # avoids showing scale in exponential units
                                                # works at least on Y-axis

    #
    # Fixed plot limits for x- and y-axis only when requested and possible
    #
    # X-axis
    if gglobs.Xleft == None or gglobs.Xleft == None or gglobs.Xscale == "auto" :
        pass # autoscale
        #print "autoscale", gglobs.Xleft, gglobs.Xleft, gglobs.Xunit, gglobs.Xscale
    else:
        plt.xlim(xmin = gglobs.Xleft, xmax = gglobs.Xright)

    # Y-axis
    if gglobs.Ymin == None or gglobs.Ymax == None or gglobs.Yscale == "auto":
        pass # autoscale
        #print "autoscale", gglobs.Ymin, gglobs.Ymax, gglobs.Yunit, gglobs.Yscale
    else:
        plt.ylim(ymin = gglobs.Ymin, ymax = gglobs.Ymax)

    #
    # add labels to the axis
    #
    # add a label to the X-axis
    plt.xlabel(xLabelStr, fontsize=12, fontweight='bold')
    # add a label to the Y-axis; rescale if needed
    if gglobs.Yunit == "CPM":
        # data are handled as CPM even if measured as CPS
        plotCPMSlice = gglobs.logCPMSlice
        ylabel = "CPM"
    elif gglobs.Yunit == "CPS":
        plotCPMSlice = gglobs.logCPMSlice / 60.0
        ylabel = "CPS"
    else:
        plotCPMSlice = gglobs.logCPMSlice * gglobs.calibration
        ylabel = u"µSv/h"

    plt.ylabel(ylabel, fontsize=16, fontweight='bold')

    #
    # plot the data
    #
    # differs by plt.plot vs  plt.plot_date
    plotstyle        = {'color'             : gglobs.linecolor,
                        'linestyle'         : gglobs.linestyle,
                        'linewidth'         : gglobs.linewidth,
                        'label'             : "",
                        'markeredgecolor'   : gglobs.linecolor,
                        'marker'            : gglobs.markerstyle,
                        'markersize'        : gglobs.markersize,
                        }

    plotstyleDefault = {'color'             : 'blue',
                        'linestyle'         : 'solid',
                        'linewidth'         : .5,
                        'label'             : "",
                        'markeredgecolor'   : 'blue',
                        'marker'            : "o",
                        'markersize'        : 2,
                        }

    plotErrMsg = "ERROR Plotting: Unrecognized style; check configuration file: "
    if gglobs.Xunit == "Time":
        ax.xaxis_date()
        fig.autofmt_xdate(rotation = 15)
        locator     = mpld.AutoDateLocator()
        formatter   = mpld.AutoDateFormatter(locator)
        xfmt        = mpld.DateFormatter(xFormatStr)
        ax.xaxis.set_major_formatter(xfmt)
        ax.xaxis.set_label_coords(0.5, -0.2)
        ax.xaxis.set_tick_params(labelsize=8)

        try:
            rdplt, = plt.plot_date(gglobs.plotTimeSlice, plotCPMSlice, **plotstyle)
        except Exception as e:
            fprint(plotErrMsg, e)
            rdplt, = plt.plot_date(gglobs.plotTimeSlice, plotCPMSlice, **plotstyleDefault)
    else:
        try:
            rdplt, = plt.plot     (gglobs.plotTimeSlice, plotCPMSlice, **plotstyle)
        except Exception as e:
            fprint(plotErrMsg, e)
            rdplt, = plt.plot     (gglobs.plotTimeSlice, plotCPMSlice, **plotstyleDefault)

    ax.format_coord = lambda x, y: "" # to hide the cursor position in the toolbar

    #
    # Plot the Moving Average
    #
    if gglobs.mavChecked:
        # Plot the moving average over N datapoints with red line on yellow.
        # Do the average over no more than N/2 data points.
        # Determine N from time delta between first and last record and the number of records.
        # Note: improper with long periods of no data, or changing cycle time!
        # In plot skip the first and last N/2 data points, which are meaningless due to averaging.
        logCycle    = (gglobs.logTimeSlice.max() - gglobs.logTimeSlice.min()) / gglobs.sizePlotSlice # apparent cycle time in days
        logCycle   *= 86400.0               # apparent cycle time in sec

        Nmav        = round(gglobs.mav / logCycle) # e.g. 100 sec / 2 sec -> 50 datapoints; rounding to integer value

        if fprintMAV:
            fprint("\nINFO: Moving Average requested over:", "{:0.2f} seconds; @ {:0.3f} seconds average".format(gglobs.mav, logCycle))
            fprint("INFO: cycle time this equals {:0.1f} datapoints. Current maximum for MovAvg".format(Nmav))
            fprint("INFO: is half of {} records = {} datapoints or {:0.0f} seconds".format(gglobs.sizePlotSlice, gglobs.sizePlotSlice/2, gglobs.sizePlotSlice/2 * logCycle))

        if Nmav < 1.0:
            Nmav   = 1
            fprint("ALERT: Moving Average of less than 1 datapoint requested")
            fprint("ALERT: Corrected to 1 - still not useful!")

        N           = int(min(len(gglobs.plotTimeSlice) / 2, Nmav)) # take the smaller of N and half of records
        new_mav     = N * logCycle

        lower       = int(N/2)
        upper       = int(gglobs.plotTimeSlice.size - N/2 )
        #dprint(gglobs.debug, "lower, upper, delta:", lower, upper, upper - lower)
        if upper - lower > 2: # needs more than a single record
            plt.plot(gglobs.plotTimeSlice[lower:upper], np.convolve(plotCPMSlice, np.ones((N,))/N, mode='same')[lower:upper], color=color['mavbg'], linewidth=4, label ="")
            plt.plot(gglobs.plotTimeSlice[lower:upper], np.convolve(plotCPMSlice, np.ones((N,))/N, mode='same')[lower:upper], color=color['mav']  , linewidth=1, label ="MovAvg, N={:0.0f} ({:0.0f}sec)".format(N, new_mav))
        else:
            fprint("ALERT: Not enough data to plot Moving Average")


    #
    # plot the horizontal line for the overall average, and +/- Std.Dev.
    #
    if gglobs.avgChecked:
        cpm_avg = np.mean(plotCPMSlice)
        cpm_std = np.std (plotCPMSlice)
        cpm_err = cpm_std / np.sqrt(plotCPMSlice.size)
        avCPM   = [cpm_avg, cpm_avg]
        avTime  = [gglobs.plotTimeSlice[0], gglobs.plotTimeSlice[-1]]
        plt.plot(avTime, avCPM,                  color=color['avg'], linewidth=2, label= u"Avg={:<3.1f}±{:<3.1f} (Err=±{:<3.1f})".format(cpm_avg, cpm_std, cpm_err))
        if (cpm_avg - cpm_std * 1.96) > 0: # negative lower bound indicates invalid data; do not draw neither lower nor upper limit
            plt.plot(avTime, avCPM - cpm_std * 1.96, color=color['avg'], linewidth=2, linestyle= '--')
            plt.plot(avTime, avCPM + cpm_std * 1.96, color=color['avg'], linewidth=2, linestyle= '--')

    #
    # plot the legend; position set in ggeiger class
    #
    if gglobs.avgChecked or gglobs.mavChecked:
        plt.legend(bbox_to_anchor=(1.01, .9), loc=2, borderaxespad=0.)
        plotLegend()

    # placing free text. positioning is difficult!
    #x= -0.1
    #y= -0.15
    #s= gglobs.deviceDetected
    #plt.text(x, y, s, fontsize=12,  transform=ax.transAxes, bbox=dict(facecolor='red', alpha=0.5))

    # refresh the figure
    fig.canvas.draw_idle()

    stopdone   = time.time()
    stopwatch += "+ {:6.1f}ms graph draw".format((stopdone - stopprep) * 1000.)
    stopwatch += " = {:6.1f}ms Total".format((stopdone - start) * 1000.)
    vprint(gglobs.verbose, stopwatch)


def plotLegend():
    """Plots the legend to the position defined by the GUI;
    used also in ggeiger class to move the legend"""

    fig = plt.figure(1)
    plt.legend(loc=legendPlacement[gglobs.legendPos], fontsize=10)
    fig.canvas.draw_idle()


def my_format_function(x, pos=None):
    """from: http://matplotlib.org/api/dates_api.html """
    # does not work. bug? https://github.com/matplotlib/matplotlib/issues/1343/

    beep()
    print "my_format_function"

    x = mpld.num2date(x)
    if pos == 0:
        #fmt = '%D %H:%M:%S.%f'
        fmt = '%D %H:%M:%S'
    else:
        #fmt = '%H:%M:%S.%f'
        fmt = '%H:%M:%S'
    label = x.strftime(fmt)
    label = label.rstrip("0")
    label = label.rstrip(".")
    print "label:", label

    #return label
    return "mist"

