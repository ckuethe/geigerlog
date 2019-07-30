#!/usr/bin/python3
# -*- coding: UTF-8 -*-

"""
gplot.py - GeigerLog commands to plot data collected from from Geiger Counter

Data in the form:
    #Index  Date&Time             CPM, CPS, ...
        12, 2017-01-11 11:01:33,  117,   2, ...
        13, 2017-01-11 11:02:33,  120,   3, ...
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
__copyright__       = "Copyright 2016, 2017, 2018"
__credits__         = [""]
__license__         = "GPL3"

import sys, os, time
import copy
import numpy as np

import matplotlib.pyplot as plt
import matplotlib.dates as mpld
#import matplotlib.dates  as mdates     # special for axes formatting
#import matplotlib.ticker as ticker     # special for axes formatting
#from matplotlib.ticker import FuncFormatter

import gglobs
from   gutils import *

# keep - had been used for legend placement
#legendPlacement = {0:'upper left', 1:'upper center', 2:'upper right', 3:'center right', 4:'lower right', 5:'lower center', 6:'lower left', 7:'center left', 8:'center'}


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
    """updates an existing plot (made by makePlot) with last record"""

    start= time.time()

    try:
        x = gglobs.logTime[0]   # logTime is defined only after 1st plot
    except:
        print("updatePlot, no gglobs.logTimeSlice.size")
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
    if gglobs.Yunit == "CPS":        cpm /= 60.
    #print "ptime:", ptime, "cpm:", cpm

    rdplt.set_xdata(np.append(rdplt.get_xdata(), ptime))
    rdplt.set_ydata(np.append(rdplt.get_ydata(), cpm))

    gglobs.sizePlotSlice += 1

    subTitle = 'File:' + os.path.basename(filePath) + "  Recs:" + str(gglobs.sizePlotSlice)
    plt.title(subTitle, fontsize=12, fontweight='normal', loc = 'right')

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

    global plotTime, strFirstRecord, rdplt, fig, ax1, ax2, xFormatStr

    if np.all(gglobs.currentFileData) == None   : return
    if not gglobs.allowGraphUpdate      : return

    #print("makePlot:  gglobs.currentFileData:", gglobs.currentFileData)
    #print("makePlot:  gglobs.logFileData:", gglobs.logFileData)
    #print("makePlot:  gglobs.hisFileData:", gglobs.hisFileData)

    #print("makePlot: gglobs.varchecked:   ", gglobs.varchecked)
    #print("        : gglobs.varcheckedLog:", gglobs.varcheckedLog)
    #print("        : gglobs.varcheckedHis:", gglobs.varcheckedHis)
    #print("        : gglobs.varlog:",        gglobs.varlog)

    try:
        if gglobs.currentFileData.size == 0:
            dprint(gglobs.debug, "makePlot: no records; nothing to plot")
            fprint("Graph: no records; nothing to plot")
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

    gglobs.logTime          = gglobs.currentFileData[:,0]           # time data of total file
    gglobs.logTimeFirst     = gglobs.logTime[0]                     # time of first record in total file
    gglobs.logTimeDiff      = gglobs.logTime - gglobs.logTimeFirst  # using time diff to first record in days

    strFirstRecord          = (str(mpld.num2date(gglobs.logTimeFirst)))[:19]

    # define the data source and label for the X-axis
    if gglobs.Xunit == "Time" :
        plotTime  = gglobs.logTime
        xFormatStr, xLabelStr = getXLabelsToD()
    else:
        plotTime  = gglobs.logTimeDiff
        xLabelStr = getXLabelsSince(gglobs.Xunit)


    gglobs.allowGraphUpdate = False     # prevent graph updates due to setting check boxes
    varcount        = gglobs.currentFileData.shape[1] - 1 # subtract 1 for the x axis
    gglobs.varcount = varcount
    #print("makePlot: gglobs.currentFileData.shape[1], varcount:", gglobs.currentFileData.shape[1], varcount)
    log             = {}
    for i in range(0, varcount):
        a       = gglobs.varnames[i]
        #print("next a:", a)
        log[a]  = gglobs.currentFileData[:, i + 1]
    gglobs.allowGraphUpdate = True
    #print("log:", log)


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
    gglobs.logTimeSlice         = gglobs.logTime     [recmin:recmax + 1 ]
    gglobs.logTimeDiffSlice     = gglobs.logTimeDiff [recmin:recmax + 1 ]
    plotTimeSlice               = plotTime           [recmin:recmax + 1 ]   # plotTime had been scaled for the x-axis!
    x                           = plotTimeSlice # abbreviation for all plot commands

    logSlice        = {}
    gglobs.logSlice = {}
    for i in range(varcount):
        vname = gglobs.varnames[i]
        #logSlice[gglobs.varnames[i]] = log[gglobs.varnames[i]][recmin:recmax + 1 ]
        logSlice[vname]         = log[vname][recmin:recmax + 1 ]
        gglobs.logSlice[vname]  = logSlice[vname]

    gglobs.sizePlotSlice        = gglobs.logTimeSlice.size
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
    plt.grid(True)                               # draw grid

    # get/set left and right Y-axis
    ax1 = plt.gca()                              # left Y-axis
    # set 2nd Y-axis
    ax2 = ax1.twinx()                            # right Y-Axis

    plt.title('Time Course', fontsize=13, fontweight='bold', loc = 'left')
    subTitle = os.path.basename(gglobs.currentFilePath) + "  Recs:" + str(gglobs.sizePlotSlice)
    plt.title(subTitle, fontsize= 9, fontweight='normal', loc = 'right', backgroundcolor='#F9F4C9', va='bottom')

    #plt.subplots_adjust(hspace=None, wspace=None , left=.15, top=0.75, bottom=0.15, right=.85)
    #plt.subplots_adjust(hspace=None, wspace=None , left=None, top=0.80, bottom=None, right=None)
    plt.subplots_adjust(hspace=None, wspace=None , left=None, top=0.80, bottom=None, right=.87)

    # avoid "offset" and "scientific notation" on the Y-axis
    # i.e. showing scale in exponential units
    # https://stackoverflow.com/questions/28371674/prevent-scientific-notation-in-matplotlib-pyplot
    ax1.ticklabel_format(useOffset=False, style='plain', axis='y')
    ax2.ticklabel_format(useOffset=False, style='plain', axis='y')
    ax1.ticklabel_format(useOffset=False, style='plain', axis='x')
    ax2.ticklabel_format(useOffset=False, style='plain', axis='x')

    # make ticks red
    # for larger numbers use option: "labelsize='medium'"
    #ax2.tick_params(axis='y', colors='red')

    # hide the cursor position from showing in the toolbar
    ax1.format_coord = lambda x, y: ""
    ax2.format_coord = lambda x, y: ""

    #
    # add labels to all three axis
    #
    # X-axis
    ax1.set_xlabel(xLabelStr, fontsize=10, fontweight='bold')
    # Y-axis
    if gglobs.Yunit == "CPM":   ylabel = "Counter  [CPM or CPS]"
    else:                       ylabel = "Counter  [µSv/h]"
    ax1.set_ylabel(ylabel,      fontsize=12, fontweight='bold')
    ax2.set_ylabel("Ambient",   fontsize=12, fontweight='bold')


    #
    # setting the scaling factor
    #
    if gglobs.calibration    == "auto":  scale1st = gglobs.DEFcalibration
    else:                                scale1st = gglobs.calibration

    if gglobs.calibration2nd == "auto":  scale2nd = gglobs.DEFcalibration2nd
    else:                                scale2nd = gglobs.calibration2nd

    if gglobs.RMcalibration  == "auto":  scaleRM  = gglobs.DEFRMcalibration
    else:                                scaleRM  = gglobs.RMcalibration

    scaleFactor = {}
    for i in range(0, varcount):
        vname = gglobs.varnames[i]
        if vname in ("CPM", "CPS", "CPM1st", "CPS1st"):
            if gglobs.Yunit == "CPM":
                scaleFactor[vname] = 1.0

            else: # gglobs.Yunit == "µSv/h"
                scaleFactor[vname]    = scale1st
                scaleFactor['CPS']    = scale1st * 60
                scaleFactor['CPS1st'] = scale1st * 60

        elif vname in ("CPM2nd", "CPS2nd"):
            if gglobs.Yunit == "CPM":
                scaleFactor[vname] = 1.0

            else: # gglobs.Yunit == "µSv/h"
                scaleFactor[vname]    = scale2nd
                scaleFactor["CPS2nd"] = scale2nd * 60

        elif vname in ("R"):
            if gglobs.Yunit == "CPM":
                scaleFactor[vname] = 1.0

            else: # gglobs.Yunit == "µSv/h"
                scaleFactor[vname] = scaleRM

        else:
            scaleFactor[vname] = 1.0
    #print("scaleFactor:", type(scaleFactor), scaleFactor)

    #
    # setting the plotting style
    #
    # each variable gets a copy of the plotstyle, which is then corrected for
    # the color choosen for each variable
    plotalpha        = 0.9
    plotstyle        = {'color'             : gglobs.linecolor,
                        'linestyle'         : gglobs.linestyle,
                        'linewidth'         : gglobs.linewidth,
                        'label'             : "",
                        'markeredgecolor'   : gglobs.linecolor,
                        'marker'            : gglobs.markerstyle,
                        'markersize'        : gglobs.markersize,
                        'alpha'             : plotalpha,
                        }

    varPlotStyle    = {}    # holds the plotstyle for each variable
    for i in range(varcount):
        vname = gglobs.varnames[i]
        varPlotStyle[vname] = plotstyle.copy()
        varPlotStyle[vname]['color']              = gglobs.varcolor[vname]
        varPlotStyle[vname]['markeredgecolor']    = gglobs.varcolor[vname]

    vindex      = gglobs.ex.select.currentIndex()
    vnameselect = gglobs.varnames[vindex]
    #print("vnameselect:", vnameselect)

    # the selected var will be drawn with thicker lines and full brightness
    # other lines will be dimmed in color via alpha setting
    for i in range(varcount):
        vname = gglobs.varnames[i]
        if vname == vnameselect:
            varPlotStyle[vname]['alpha']     = plotalpha
            #varPlotStyle[vname]['linewidth'] = int(varPlotStyle[vname]['linewidth']) * 2.0
            varPlotStyle[vname]['linewidth'] = float(varPlotStyle[vname]['linewidth']) * 2.0
            #print("vname, linewidth:", vname, varPlotStyle[vname]['linewidth'])
        else:
            varPlotStyle[vname]['alpha']     = plotalpha * 0.5

    #
    # plot the data
    #
    varlines            = {}            # lines objects for legend
    varlabels           = {}            # labels for legend
    gglobs.varlabels    = {}            # labels for legend
    logSliceMod         = {}            # data of the variables
    gglobs.logSliceMod  = {}            # data; will be used by Stat, Poiss, FFT

    # used like:       VarName  Unit   Avg      StdDev     Variance          Range         LastValue
    fmtLineLabel     = "{:8s}: {:7s}{:>8.2f} ±{:<8.3g}   {:>8.2f}   {:>7.6g} ... {:<7.6g}    {}"
    fmtLineLabelTip  = "{:s}: [{}]  Avg: {:<8.2f}  StdDev: {:<0.3g}   Variance: {:<0.3g}   Range: {:>0.6g} ... {:<0.6g}   Last Value: {}"

    # order varnames to have selected variable plot last, i.e. on top of all others
    vname_ordered = ()
    for i in range(varcount):
        vname = gglobs.varnames[i]
        if vname == vnameselect:
            continue    # add at the end
        else:
            vname_ordered += (vname,)
    vname_ordered += (vnameselect,)
    #print("vname, vname_ordered:", vname, vname_ordered)

    #arrprint("MakePlot: logSlice:", logSlice)
    #arrprint("MakePlot: scaleFactor:", scaleFactor)
    for vname in vname_ordered:
        #print("plot the data: vname:", vname)

        if gglobs.ex.vbox[vname].isChecked():
            #print("logSlice[vname]:", type(logSlice[vname]), logSlice[vname] )
            #print("scaleFactor[vname]:", type(scaleFactor[vname]), scaleFactor[vname] )
            y                           = logSlice[vname] * scaleFactor[vname]
            ymask                       = np.isfinite(y)      # mask for nan values
            var_y                       = y[ymask]
            var_x                       = x[ymask]

            if vname == "T" and gglobs.ex.y2unit.currentText() == "°F":  # °C to °F
                var_y = var_y / 5 * 9 + 32

            gglobs.logSliceMod[vname]   = y  # wozu wird das benötigt???????? y oder var_y

            var_size                    = var_y.size
            #print("vanme: var_size:", vname, var_size)
            if var_size == 0: continue

            var_avg                     = np.nanmean(var_y)
            var_std                     = np.nanstd (var_y)
            var_var                     = np.nanvar (var_y)
            var_max                     = np.nanmax (var_y)
            var_min                     = np.nanmin (var_y)
            var_size                    = var_y.size
            var_err                     = var_std / np.sqrt(var_size)
            if gglobs.lastValues == None:
                var_lastval = "    N.A."
            else:
                var_lastval = "{:>8.2f}".format(gglobs.lastValues[vname][0])
            #print("var_lastval:", var_lastval)
            var_unit                    = gglobs.varunit[vname]

            if vname in ("CPM", "CPS", "CPM1st", "CPS1st", "CPM2nd", "CPS2nd", "R"):
                if gglobs.Yunit == "CPM":
                    var_unit                    = gglobs.varunit[vname]
                else:
                    var_unit                    = "µSv/h"

            if vname in ("T"):
                if gglobs.ex.y2unit.currentText() == "°C":
                    var_unit                    = gglobs.varunit[vname]
                else:
                    var_unit                    = "°F"

            varlabels[vname]            = fmtLineLabel   .format(vname, "[" + var_unit + "]", var_avg, var_std, var_var, var_min, var_max, var_lastval)
            gglobs.varlabels[vname]     = varlabels[vname]
            Tip                         = fmtLineLabelTip.format(gglobs.vardict[vname], var_unit, var_avg, var_std, var_var, var_min, var_max, var_lastval)
            gglobs.ex.vbox[vname].setToolTip  (Tip)
            gglobs.ex.vbox[vname].setStatusTip(Tip)

            varPlotStyle[vname]['markersize'] = float(plotstyle['markersize']) / np.sqrt(var_size)
            varlines[vname] = plotLine(var_x, var_y, gglobs.Xunit, varname=vname, **varPlotStyle[vname])

    #
    # Plot the Moving Average
    #
    plotMovingAverage(x, logSlice, scaleFactor, varPlotStyle, fprintMAV)

    #
    # Plot the Average and +/- 95% as horizontal lines
    #
    plotAverage(x, logSlice, scaleFactor, varPlotStyle)

    #
    # apply the Y-Limits
    #
    if   gglobs.Ymin  != None and gglobs.Ymax  != None:  ax1.set_ylim(ymin = gglobs.Ymin,  ymax = gglobs.Ymax)
    elif gglobs.Ymin  != None:                           ax1.set_ylim(ymin = gglobs.Ymin)
    elif                          gglobs.Ymax  != None:  ax1.set_ylim(                     ymax = gglobs.Ymax)

    if   gglobs.Y2min != None and gglobs.Y2max != None:  ax2.set_ylim(ymin = gglobs.Y2min, ymax = gglobs.Y2max)
    elif gglobs.Y2min != None:                           ax2.set_ylim(ymin = gglobs.Y2min)
    elif                          gglobs.Y2max != None:  ax2.set_ylim(                     ymax = gglobs.Y2max)

    # limits are needed for calculation of the mouse pointer w respect to counter Y-axis
    # see: def updatecursorposition(self, event)
    gglobs.y1_limit = ax1.get_ylim()
    gglobs.y2_limit = ax2.get_ylim()
    #print("gglobs.y1_limit:", gglobs.y1_limit, ", gglobs.y2_limit:", gglobs.y2_limit)

    #
    # plot the legend
    #
    pp = ()
    pl = ()
    for vname in gglobs.varnames:
        p   = plt.Rectangle((0, 0), 1, 1, fc=gglobs.varcolor[vname], ec="black", lw=0.2)
        pp += (p,)
        pl += (gglobs.vardict[vname],)

    plt.figlegend(pp, pl, shadow=False, mode="expand", handlelength=2, ncol=5, framealpha=0)

    #
    # refresh the figure
    #
    fig.canvas.draw_idle()

    # finish
    stopdone   = time.time()
    stopwatch += "+ {:6.1f}ms graph draw".format((stopdone - stopprep) * 1000.)
    stopwatch += " = {:6.1f}ms Total".format((stopdone - start) * 1000.)
    vprint(gglobs.verbose, stopwatch)


def plotAverage(x, logSlice, scaleFactor, varPlotStyle):
    """Plot the Average and +/- 95% as horizontal lines"""

    if not gglobs.avgChecked: return

    vindex    = gglobs.ex.select.currentIndex()
    vname     = gglobs.varnames[vindex]
    #print("average: vname, gglobs.ex.vbox[vname].isChecked():", vname, gglobs.ex.vbox[vname].isChecked())
    if gglobs.ex.vbox[vname].isChecked():
        avg_Time                     = [x[0], x[-1]]
        logSliceMod                  = logSlice[vname] * scaleFactor[vname]
        #print("logSliceMod:", logSliceMod)

        if vname == "T" and gglobs.ex.y2unit.currentText() == "°F":  # °C to °F
            logSliceMod = logSliceMod / 5 * 9 + 32

        avg_avg                      = np.nanmean(logSliceMod)
        avg_std                      = np.nanstd (logSliceMod)

        avg_CPMS                     = [avg_avg, avg_avg]
        avg_CPMS_lo                  = avg_CPMS - avg_std * 1.96
        avg_CPMS_hi                  = avg_CPMS + avg_std * 1.96
        avg_plotHiLo                 = (avg_avg - avg_std * 1.96) > 0 # flag to plot 95%

        if vname in ("T", "P", "H"): avg_plotHiLo = False # no limits drawn for T,P,H

        avg_plotstyle                = varPlotStyle[vname].copy()
        avg_plotstyle["linewidth"]   = 2
        avg_plotstyle["markersize"]  = 0

        avg_plotstyle2                = varPlotStyle[vname].copy()
        avg_plotstyle2["linewidth"]   = 4
        avg_plotstyle2["color"]       = "yellow"
        avg_plotstyle2["markersize"]  = 0

        plotLine(avg_Time, avg_CPMS, gglobs.Xunit, varname=vname, **avg_plotstyle2)
        plotLine(avg_Time, avg_CPMS, gglobs.Xunit, varname=vname, **avg_plotstyle)

        if avg_plotHiLo :
            avg_plotstyle["linestyle"]  = "--"
            plotLine(avg_Time, avg_CPMS_lo, gglobs.Xunit, varname=vname, **avg_plotstyle)
            plotLine(avg_Time, avg_CPMS_hi, gglobs.Xunit, varname=vname, **avg_plotstyle)

            avg_plotstyle["color"]      = "white"
            avg_plotstyle["linestyle"]  = ":"
            plotLine(avg_Time, avg_CPMS_lo, gglobs.Xunit, varname=vname, **avg_plotstyle)
            plotLine(avg_Time, avg_CPMS_hi, gglobs.Xunit, varname=vname, **avg_plotstyle)


def plotMovingAverage(x, logSlice, scaleFactor, varPlotStyle, fprintMAV):
    """Plot the Moving Average"""

    if not gglobs.mavChecked: return

    # Plot the moving average over N datapoints with a thin line in the
    # variable's color on a yellow thick line.
    # Do the average over no more than N/2 data points.
    # Determine N from time delta between first and last record and the number of records.
    # Note: improper with long periods of no data, or changing cycle time!
    # In plot skip the first and last N/2 data points, which are meaningless due to averaging.

    vindex          = gglobs.ex.select.currentIndex()
    vname           = gglobs.varnames[vindex]

    lSM_mask        = np.isfinite(logSlice[vname])          # mask for nan values
    logSliceNoNAN   = logSlice[vname][lSM_mask]             # all NANs removed

    if logSliceNoNAN.size == 0: return                      # no data, return

    logSliceMod     = logSliceNoNAN * scaleFactor[vname]

    if vname == "T" and gglobs.ex.y2unit.currentText() == "°F":  # °C to °F
        logSliceMod = logSliceMod / 5 * 9 + 32

    x_mav           = x[lSM_mask]
    x_mav_size      = x_mav.size
    x_mav_max       = x_mav.max()
    x_mav_min       = x_mav.min()

    logCycle        = (gglobs.logTimeSlice.max() - gglobs.logTimeSlice.min()) / x_mav_size
    logCycle       *= 86400.0                      # apparent cycle time in sec
    Nmav            = round(gglobs.mav / logCycle) # e.g. 100 sec / 2 sec -> 50 datapoints; rounding to integer value

    if fprintMAV:
        fprint("\nINFO:")
        fprint("Moving Average requested over: {:0.2f} seconds; with {:0.1f} seconds".format(gglobs.mav, logCycle))
        fprint("average cycle time this equals {:0.0f} datapoints. Current maximum for".format(Nmav))
        fprint("MovAvg is half of {} datapoints = {} datapoints or {:0.0f} seconds".format(x_mav_size, x_mav_size / 2, x_mav_size / 2 * logCycle))

    if Nmav < 1.0:
        Nmav   = 1
        fprint("ALERT: Moving Average of less than 1 datapoint requested")
        fprint("ALERT: Corrected to 1 - still not useful!")

    N           = int(min(len(x_mav) / 2, Nmav)) # take the smaller of N and half of records
    new_mav     = N * logCycle

    lower       = int(N/2)
    upper       = int(x_mav_size - N / 2 )
  #  lower       = 0
  #  upper       = int(x_mav_size - N  )
  #  lower       = int(N)
  #  upper       = int(x_mav_size)

    #dprint(gglobs.debug, "lower, upper, delta:", lower, upper, upper - lower)

    if upper - lower > 2: # needs more than a single record
        if gglobs.ex.vbox[vname].isChecked():

            mav_label                   = "MvAvg, N={:0.0f} ({:0.0f}sec)".format(N, new_mav)

            mav_x = x_mav[lower:upper]
            mav_y = np.convolve(logSliceMod,     np.ones((N,))/N, mode='same')[lower:upper]

            mav_plotstyle               = varPlotStyle[vname].copy()
            mav_plotstyle['color']      = 'yellow'
            mav_plotstyle['linewidth']  = 4
            mav_plotstyle['markersize'] = 0
            plotLine(mav_x, mav_y, gglobs.Xunit, varname=vname, **mav_plotstyle)

            mav_plotstyle['color']      = varPlotStyle[vname]['color']
            mav_plotstyle['linewidth']  = 2
            mav_plotstyle['label']       = mav_label
            mav_line = plotLine(mav_x, mav_y, gglobs.Xunit, varname=vname, drawlegend=True, **mav_plotstyle)

    else:
        fprint("ALERT: Not enough data to plot Moving Average")


def plotLine(x,y, xunit="Time", varname="CPM", drawlegend=False, **plotstyle):
    """plots a single line of data"""

    global xFormatStr

    #print("plotLine: xunit:", xunit, ", plotstyle:", plotstyle)

    if varname in ("CPM", "CPS", "CPM1st", "CPM2nd", "CPS1st", "CPS2nd", "R"): yaxis  = ax1
    else:                                                                      yaxis  = ax2

    p_1000 = np.mean([1000]) # creating a value, which can be subtracted from array
    if varname == "P"  : y = y - p_1000     # scaling pressure to zero at 1000 hPa

    #co2_100  = np.mean([100]) # creating a value, which can be applied to array
    #if varname == "CO2": y = y / co2_100      # scaling CO2 to values up to ~100

    if xunit == "Time":
    #    yaxis.xaxis_date()    # needed ???
        fig.autofmt_xdate(rotation = 15)
    #    formatter   = mpld.AutoDateFormatter(mpld.AutoDateLocator()) # What for?
        yaxis.xaxis.set_major_formatter(mpld.DateFormatter(xFormatStr))
        ax1.xaxis.set_tick_params(labelsize=8)  # ax1 defines the size of the labels
        #ax2.xaxis.set_tick_params(labelsize=8)  # appears to be not relevant

        # X-Label positioning: (the label like: Time (First Record: ...)
        # you can move the location of axis labels using set_label_coords.
        # The coords you give it are x and y, and by default the transform
        # is the axes coordinate system: so (0,0) is (left,bottom), (0.5, 0.5)
        # is in the middle, etc.
    #    yaxis.xaxis.set_label_coords(0.5, -0.25)

        line,  = yaxis.plot_date (x, y, **plotstyle)
    else:
        line,  = yaxis.plot      (x, y, **plotstyle)

    if drawlegend: yaxis.legend()

    return line

