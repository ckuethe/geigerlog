#! /usr/bin/env python3
# -*- coding: UTF-8 -*-

"""
gsup_plot.py - GeigerLog commands to plot data collected from from Geiger Counter

include in programs with:
    include gsup_plot

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
__copyright__       = "Copyright 2016, 2017, 2018, 2019, 2020, 2021"
__credits__         = [""]
__license__         = "GPL3"

from   gsup_utils       import *

# keep - had been used for legend placement
#legendPlacement = {0:'upper left',   1:'upper center', 2:'upper right',
#                   3:'center right', 4:'lower right',  5:'lower center',
#                   6:'lower left',   7:'center left',  8:'center'}


#~def getTsr(Tfirst, Tdelta):
def getTimeSinceFirstRecord(Tfirst, Tdelta):
    """Get Time since first record in best unit;
    used only in function updatecursorposition"""

    l = Tdelta - Tfirst

    if   l              > 3:
        unit = "day"
        t = l
    elif l * 24         > 3:
        unit = "hour"
        t = l * 24
    elif l * 1440       > 3:
        unit = "minute"
        t = l * 1440
    else:
        unit = "second"
        t = l * 86400

    #print "t, unit:", t, unit

    return "{:0.3f} {}s".format(t, unit)


#~def getToD(Tfirst, delta, deltaUnit):
def getTimeOfDay(Tfirst, delta, deltaUnit):
    """From time of first record = Tfirst plus the delta time in days
    return TimeOfDay; used only in function updatecursorposition"""

    #print "gglobs.XunitCurrent", gglobs.XunitCurrent
    if   deltaUnit == "hour":       x = delta / 24.
    elif deltaUnit == "minute":     x = delta / 24. / 60.
    elif deltaUnit == "second":     x = delta / 24. / 60. / 60.
    else:                           x = delta # delta is in the correct unit day

    ret = str(mpld.num2date(Tfirst + x))[:19]
    #print("getToD: ret:", ret)

    return ret


def xxxgetXLabelsToD():
    """find proper label for x-axis and x-ticks when gglobs.Xunit == "Time";
    used only in gsup_plot.makePlot"""

    global plotTime, strFirstRecord

    #~totalDays     = (plotTime.max() - plotTime.min()) # in days

    #~if   totalDays                  > 5:    tformat = '%Y-%m-%d'            # > 5 d
    #~elif totalDays                  > 1:    tformat = '%Y-%m-%d  %H:%M:%S'  # > 1 d
    #~elif totalDays * 24             > 1:    tformat = '%Y-%m-%d  %H:%M:%S'  # > 1 h
    #~elif totalDays * 24 * 60        > 1:    tformat = '%H:%M:%S'            # > 1 min
    #~elif totalDays * 24 * 60 * 60   > 1:    tformat = '%H:%M:%S'            # > 1 sec
    #~else:                                   tformat = '%Y-%m-%d  %H:%M:%S'  # else
    #~#print("getXLabelsToD: ret: ", tformat, 'Time (First Record: {})'.format(strFirstRecord))

    tformat = '%Y-%m-%d  %H:%M:%S'  # always the same full format
    return tformat, 'Time (First Record: {})'.format(strFirstRecord)


def getXLabelsSince(Xunit):
    """find proper label for x-axis and x-ticks when gglobs.Xunit other than "Time";
    used only in gsup_plot.makePlot"""

    global plotTime, strFirstRecord

    #print("getXLabelsSince: gglobs.XunitCurrent:", gglobs.XunitCurrent)

    oldXunit = gglobs.XunitCurrent
    newXunit = Xunit

    if Xunit == "auto":
        l = plotTime.max() - plotTime.min()
        #print l

        if   l / 30.42  > 3:       newXunit = "month"
        elif l / 7      > 3:       newXunit = "week"
        elif l          > 3:       newXunit = "day"
        elif l * 24     > 3:       newXunit = "hour"
        elif l * 1440   > 3:       newXunit = "minute"
        else:                      newXunit = "second"

    gglobs.XunitCurrent = newXunit

    # now we have the new Xunit or "auto" was not requested
    # rescale the time and prepare label for the x axis
    # plotTime is in days
    if   newXunit == "second":
        plotTime = plotTime * 86400
        xlabel = '[seconds]'

    elif newXunit == "minute":
        plotTime = plotTime * 1440      # convert to minutes
        xlabel = '[minutes]'

    elif newXunit == "hour":
        plotTime = plotTime * 24        # convert to hours
        xlabel = '[hours]'

    elif newXunit == "day":
        plotTime = plotTime             # is in days already
        xlabel = '[days]'

    elif newXunit == "week":
        plotTime = plotTime / 7         # is in days convert to weeks
        xlabel = '[weeks]'

    elif newXunit == "month":
        plotTime = plotTime / 30.42     # is in days convert to months; 365 / 12 = 30.4167
        xlabel = '[months]'

    else:
        # no change
        plotTime = plotTime
        xlabel = '[days]'


    if newXunit != oldXunit:
        factorlookup = {"second":86400, "minute":1440, "hour":24, "day":1, "week":1/7, "month":1/30.42}
        oldfactor    = factorlookup[oldXunit]
        newfactor    = factorlookup[newXunit]
        if gglobs.Xleft != None:
            try:
                xleft = float(gglobs.Xleft)
                gglobs.Xleft = xleft / oldfactor * newfactor # convert all to days, then to new unit
            except Exception as e:
                exceptPrint(e, "xleft")
                gglobs.Xleft = None

        if gglobs.Xright != None:
            try:
                xright = float(gglobs.Xright)
                gglobs.Xright = xright / oldfactor * newfactor # convert all to days, then to new unit
            except Exception as e:
                exceptPrint(e, "xright")
                gglobs.Xright = None

        strxl = "{:1.8f}".format(float(gglobs.Xleft) ) if gglobs.Xleft  != None else ""
        strxr = "{:1.8f}".format(float(gglobs.Xright)) if gglobs.Xright != None else ""
        gglobs.exgg.xmin.setText(strxl)
        gglobs.exgg.xmax.setText(strxr)

    return 'time {} since first record: {}'.format(xlabel, strFirstRecord)




def changeTimeUnitofPlot(newXunit):
    """recalc xmin, xmax on Time unit changes"""

    #print("-----------------------changedGraphTimeUnit: i:", i)

    if np.all(gglobs.logTime) == None: return

    oldXunit = gglobs.XunitCurrent
    #print("changedGraphTimeUnit: oldXunit: ", oldXunit)

    # convert all entries to days since start
    if   oldXunit == "Time":
        if gglobs.Xleft  != None: gglobs.Xleft  = gglobs.Xleft  - gglobs.logTimeFirst
        if gglobs.Xright != None: gglobs.Xright = gglobs.Xright - gglobs.logTimeFirst

    elif oldXunit == "month":
        if gglobs.Xleft  != None: gglobs.Xleft  = gglobs.Xleft  * 30.42 # 365 / 12 = 30.4167
        if gglobs.Xright != None: gglobs.Xright = gglobs.Xright * 30.42 # 365 / 12 = 30.4167

    elif oldXunit == "week":
        if gglobs.Xleft  != None: gglobs.Xleft  = gglobs.Xleft  * 7
        if gglobs.Xright != None: gglobs.Xright = gglobs.Xright * 7

    elif oldXunit == "day": # no changes all in days
        if gglobs.Xleft  != None: gglobs.Xleft  = gglobs.Xleft
        if gglobs.Xright != None: gglobs.Xright = gglobs.Xright

    elif oldXunit == "hour":
        if gglobs.Xleft  != None: gglobs.Xleft  = gglobs.Xleft  / 24.
        if gglobs.Xright != None: gglobs.Xright = gglobs.Xright / 24.

    elif oldXunit == "minute":
        if gglobs.Xleft  != None: gglobs.Xleft  = gglobs.Xleft  / 1440.
        if gglobs.Xright != None: gglobs.Xright = gglobs.Xright / 1440.

    elif oldXunit == "second":
        if gglobs.Xleft  != None: gglobs.Xleft  = gglobs.Xleft  / 86400.
        if gglobs.Xright != None: gglobs.Xright = gglobs.Xright / 86400.

    #~gglobs.XunitCurrent = str(self.xunit.currentText())
    #~print("changedGraphTimeUnit: gglobs.XunitCurrent: ", gglobs.XunitCurrent)
    #~newXunit            = gglobs.XunitCurrent
    #newXunit            = self.xunit.currentText()
    if newXunit == "auto":
        l = gglobs.logTime.max() - gglobs.logTime.min()
        #print "l=", l
        if   l         > 3:  Xunit = "day"
        elif l * 24.   > 3:  Xunit = "hour"
        elif l * 1440. > 3:  Xunit = "minute"
        else:                Xunit = "second"

        newXunit = Xunit

    gglobs.XunitCurrent = newXunit
    #~print("changedGraphTimeUnit: gglobs.XunitCurrent: ", gglobs.XunitCurrent)
    gglobs.Xunit        = newXunit
    #print( "newXunit", newXunit)

    if newXunit == "Time":
        if gglobs.Xleft  != None: gglobs.Xleft =  (str(mpld.num2date((gglobs.Xleft  + gglobs.logTimeFirst))))[:19]
        if gglobs.Xright != None: gglobs.Xright = (str(mpld.num2date((gglobs.Xright + gglobs.logTimeFirst))))[:19]

    elif newXunit == "month":
        if gglobs.Xleft  != None: gglobs.Xleft  = gglobs.Xleft  / 30.42 # 365 / 12 = 30.4167
        if gglobs.Xright != None: gglobs.Xright = gglobs.Xright / 30.42 # 365 / 12 = 30.4167

    elif newXunit == "week":
        if gglobs.Xleft  != None: gglobs.Xleft  = gglobs.Xleft  / 7
        if gglobs.Xright != None: gglobs.Xright = gglobs.Xright / 7

    elif newXunit == "day": # no changes all in days
        if gglobs.Xleft  != None: gglobs.Xleft  = gglobs.Xleft
        if gglobs.Xright != None: gglobs.Xright = gglobs.Xright

    elif newXunit == "hour":
        if gglobs.Xleft  != None: gglobs.Xleft  = gglobs.Xleft  * 24
        if gglobs.Xright != None: gglobs.Xright = gglobs.Xright * 24

    elif newXunit == "minute":
        if gglobs.Xleft  != None: gglobs.Xleft  = gglobs.Xleft  * 1440
        if gglobs.Xright != None: gglobs.Xright = gglobs.Xright * 1440

    elif newXunit == "second":
        if gglobs.Xleft  != None: gglobs.Xleft  = gglobs.Xleft  * 86400
        if gglobs.Xright != None: gglobs.Xright = gglobs.Xright * 86400

    if gglobs.Xleft == None:
        gglobs.exgg.xmin.setText("")
    else:
        try:    xl = "{:1.8f}".format(float(gglobs.Xleft))
        except: xl = gglobs.Xleft
        gglobs.exgg.xmin.setText(xl)

    if gglobs.Xright == None:
        gglobs.exgg.xmax.setText("")
    else:
        try:    xr = "{:1.8f}".format(float(gglobs.Xright))
        except: xr = gglobs.Xright
        gglobs.exgg.xmax.setText(xr)

    #self.applyGraphOptions()





def makePlot():
    """Plots the data in array gglobs.currentDBData vs. time-of-day or
    vs time since start, observing plot settings;
    using matplotlib date functions

    Return: nothing
    """

    def clearFigure():
        global fig

        fig = plt.figure(1)
        plt.clf()                                    # clear figure
        fig.canvas.draw_idle()


    global plotTime, strFirstRecord, rdplt, fig, ax1, ax2, xFormatStr

    fncname = "makePlot: "
    #print(fncname, "-"*100)

    #~print(fncname + "  gglobs.currentDBData.shape:",   gglobs.currentDBData.shape)
    #~print(fncname + "  gglobs.currentDBData:\n",       gglobs.currentDBData)
    #~print(fncname + "  gglobs.logDBData:\n",           gglobs.logDBData)
    #~print(fncname + "  gglobs.hisDBData:\n",           gglobs.hisDBData)

    #~print(fncname + "  gglobs.varcheckedCurrent:",     gglobs.varcheckedCurrent)
    #~print(fncname + "  gglobs.varcheckedLog:    ",     gglobs.varcheckedLog)
    #~print(fncname + "  gglobs.varcheckedHis:    ",     gglobs.varcheckedHis)

    if np.all(gglobs.currentDBData) == None   : return
    if not gglobs.allowGraphUpdate            : return

    #print(fncname + "ENTRY: gglobs.XunitCurrent:", gglobs.XunitCurrent, time.time())

    try:
        if gglobs.currentDBData.size == 0:
            dprint(fncname + "no records; nothing to plot")
            clearFigure()
            return

    except Exception as e:
        # if there is no gglobs.currentDBData then .size results in error
        # but then there is also nothing to plot
        msg = fncname + "no 'gglobs.currentDBData', nothing to plot"
        exceptPrint(e, msg)
        efprint(msg)
        clearFigure()
        return

    start                   = time.time()            # timing durations

    #clear the checkboxes' default ToolTip
    for vname in gglobs.varsDefault:
        gglobs.exgg.varDisplayCheckbox[vname].setToolTip(gglobs.varsBook[vname][0])


    # NOTE:
    # Before Matplotlib 3.3, the epoch was 0000-12-31T00:00:00 which lost
    # modern microsecond precision and also made the default axis limit of 0
    # an invalid datetime.
    # In 3.3 time the epoch was changed to 1970-01-01T00:00:00 with
    # 0.35 microsecond resolution.
    # To convert old ordinal floats to the new epoch, users can do:
    #     new_ordinal = old_ordinal + mdates.date2num(np.datetime64('0000-12-31'))
    TimeBaseCorrection      = mpld.date2num(np.datetime64('0000-12-31'))        # = -719163.0
    #print("makePlot: TimeBaseCorrection: ", TimeBaseCorrection)
    gglobs.logTime          = gglobs.currentDBData[:,0] + TimeBaseCorrection    # time data of total file
    gglobs.logTimeFirst     = gglobs.logTime[0]                                 # time of first record in total file
    gglobs.logTimeDiff      = gglobs.logTime - gglobs.logTimeFirst              # using time diff to first record in days


    # get time of first record, properly rounded
    try:
        # get the time of first record
        ltf = (mpld.num2date(gglobs.logTimeFirst))
    except Exception as e:
        msg = fncname + "ERROR: incorrect value in 'gglobs.logTimeFirst', cannot plot"
        exceptPrint(e, msg)
        efprint(msg)
        clearFigure()
        return

    # rounding the time
    # mpld.num2date(gglobs.logTimeFirst) delivers date with sec fractions, like:
    # 2019-01-02 18:05:00.999980+00:00
    # but does not allow rounding to a second. Therefore cutting off after 19
    # chars (before the '.')  may yield a time too low by 1 second, like:
    # 2019-01-02 18:05:00 instead of:
    # 2019-01-02 18:05:01
    F0 = ltf.strftime("%Y-%m-%d %H:%M:%S.%f")
    #print("F0: ", F0)
    try:
        # good! 2020-08-18 16:34:11.609016 -> 2020-08-18 16:34:12
        # has been rounded up
        strFirstRecord = "{}{:02.0f}".format(F0[:17], float(F0[17:])) # good!

    except Exception as e:
        #exceptPrint(e, "TEST")
        # bad! 2020-08-18 16:34:11.609016 -> 2020-08-18 16:34:11
        # should have been rounded up
        strFirstRecord = F0[:19]
    #~print("F0: ", F0, "reduced to: ", strFirstRecord)


    # define the data source and label for the X-axis,
    # either Time-since-epoch 0001-01-01 or Time-since-start in days
    # labels need strFirstRecord !
    if gglobs.Xunit == "Time" :
        plotTime                = gglobs.logTime
        #~xFormatStr, xLabelStr   = getXLabelsToD()
        xFormatStr              = '%Y-%m-%d  %H:%M:%S'  # always the same full format
        xLabelStr               = 'Time (First Record: {})'.format(strFirstRecord)
    else:
        plotTime                = gglobs.logTimeDiff
        xLabelStr               = getXLabelsSince(gglobs.Xunit)

    # split multi-dim np.array into 10 single-dim np.arrays like log["CPM"] = [<var data>]
    log = {}
    for i, vname in enumerate(gglobs.varsBook):
        log[vname] = gglobs.currentDBData[:, i + 1]
        #print("{}: log[{}]: {}".format(i, vname, log[vname]))

    # is the temperature to be shown in °C or °F ? (data are in °C )
    if gglobs.varsBook["T"][2] == "°F":        log["T"] = log["T"] / 5 * 9 + 32

    # confine limits to what is available
    Xleft = gglobs.Xleft
    Xright= gglobs.Xright

    #dprint("before re-setting limits: Xleft, Xright, plotTime.min, plotTime.max   {}   {}   {}   {}".format(gglobs.Xleft, gglobs.Xright, plotTime.min(), plotTime.max()))
    if Xright == None or Xright > plotTime.max():    Xright = plotTime.max()
    if                   Xright < plotTime.min():    Xright = plotTime.min()
    if Xleft  == None or Xleft  < plotTime.min():    Xleft  = plotTime.min()
    if                   Xleft  > plotTime.max():    Xleft  = plotTime.max()
    #dprint("after                                                                 {}   {}   {}   {}".format(Xleft, Xright, plotTime.min(), plotTime.max()))

    # find the records, where the time limits apply
    recmin = np.where(plotTime >= Xleft )[0][0]
    recmax = np.where(plotTime <= Xright)[0].max() # excludes recs > gglobs.Xleft, and takes max of remaining
    #dprint("recmin, recmax:", recmin, recmax)

    # slice the arrays; include record #recmax (thus +1)
    gglobs.logTimeSlice         = gglobs.logTime     [recmin:recmax + 1 ]
    gglobs.logTimeDiffSlice     = gglobs.logTimeDiff [recmin:recmax + 1 ]
    x                           = plotTime           [recmin:recmax + 1 ]   # plotTime is either Time or TimeDiff

    if gglobs.logTimeSlice.size == 0:
        fprint("ALERT: No records in selected range")
        return

    logSlice        = {}
    for vname in gglobs.varsDefault:
        logSlice[vname] = log[vname][recmin:recmax + 1 ]
    gglobs.logSlice = logSlice

    stopprep   = time.time()
    stopwatch  = "{:0.1f} ms for data load and prep, ".format((stopprep - start) * 1000)

    ###########################################################################
    # prepare the graph
    ###########################################################################
    clearFigure()

    # get/set left and right Y-axis
    ax1 = plt.gca()                           # left Y-axis
    ax2 = ax1.twinx()                         # right Y-Axis

    vnameselect   = list(gglobs.varsBook)[gglobs.exgg.select.currentIndex()]
    if vnameselect in ("CPM", "CPS", "CPM1st", "CPS1st", "CPM2nd", "CPS2nd", "CPM3rd", "CPS3rd"):
        ax1.grid(b=True, axis="both")         # left Y-axis grid + X-grid
    else:
        ax1.grid(b=True, axis="x")            # X-axis grid
        ax2.grid(b=True, axis="y")            # right Y-axis grid

    mysubTitle = os.path.basename(gglobs.currentDBPath) + "   " + "Recs:" + str(gglobs.logTimeSlice.size)
    plt.title(mysubTitle, fontsize= 9, fontweight='normal', loc = 'right')

    plt.subplots_adjust(hspace=None, wspace=None , left=0.15, top=0.80, bottom=None, right=.87)

    # avoid "offset" and "scientific notation" on the Y-axis
    # i.e. showing scale in exponential units
    # https://stackoverflow.com/questions/28371674/prevent-scientific-notation-in-matplotlib-pyplot
    ax1.ticklabel_format(useOffset=False, style='plain', axis='x')
    ax1.ticklabel_format(useOffset=False, style='plain', axis='y')
    ax2.ticklabel_format(useOffset=False, style='plain', axis='x')
    ax2.ticklabel_format(useOffset=False, style='plain', axis='y')

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

    # Y1-axis
    if gglobs.Yunit == "CPM":   ylabel = "Counter  [CPM or CPS]"
    else:                       ylabel = "Counter  [µSv/h]"
    ax1.set_ylabel(ylabel,      fontsize=12, fontweight='bold')

    # Y2-axis
    ax2.set_ylabel("Ambient",   fontsize=12, fontweight='bold')

    #
    # set the µSv-scaling factor
    #
    if gglobs.calibration1st == "auto":  scale1st = 1 / gglobs.DefaultSens1st
    else:                                scale1st = 1 / gglobs.calibration1st

    if gglobs.calibration2nd == "auto":  scale2nd = 1 / gglobs.DefaultSens2nd
    else:                                scale2nd = 1 / gglobs.calibration2nd

    if gglobs.calibration3rd == "auto":  scale3rd = 1 / gglobs.DefaultSens3rd
    else:                                scale3rd = 1 / gglobs.calibration3rd

    scaleFactor = {}
    for i, vname in enumerate(gglobs.varsBook):
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

        elif vname in ("CPM3rd", "CPS3rd"):
            if gglobs.Yunit == "CPM":
                scaleFactor[vname] = 1.0
            else: # gglobs.Yunit == "µSv/h"
                scaleFactor[vname]    = scale3rd
                scaleFactor["CPS3rd"] = scale3rd * 60

        elif vname in ("R"):
            if gglobs.Yunit == "CPM":
                scaleFactor[vname] = 1.0
            else: # gglobs.Yunit == "µSv/h"
                scaleFactor[vname] = scale3rd

        else:
            scaleFactor[vname] = 1.0
    #print("scaleFactor:", type(scaleFactor), scaleFactor)

    #
    # set the plotting style
    #
    # each variable gets a copy of the plotstyle, which is then corrected for
    # the color choosen for each variable
    plotalpha        = 0.9
    plotstyle        = {'color'             : gglobs.linecolor, # overwritten by Style from varsBook
                        'linestyle'         : gglobs.linestyle, # overwritten by Style from varsBook
                        'linewidth'         : gglobs.linewidth,
                        'label'             : "",
                        'markeredgecolor'   : gglobs.linecolor, # overwritten by Style from varsBook
                        'marker'            : gglobs.markerstyle,
                        'markersize'        : gglobs.markersize,
                        'alpha'             : plotalpha,
                        }

    varPlotStyle    = {}    # holds the plotstyle for each variable
    for i, vname in enumerate(gglobs.varsBook):
        varPlotStyle[vname]                       = plotstyle.copy()
        varPlotStyle[vname]['color']              = gglobs.varsBook[vname][3]
        varPlotStyle[vname]['markeredgecolor']    = gglobs.varsBook[vname][3]
        varPlotStyle[vname]['linestyle']          = gglobs.varsBook[vname][4]

    #
    # Emphasize the selected variable by color and line thickness and draw last (on top)
    #
    # the selected var will be drawn with thicker lines and full brightness
    # other lines will be dimmed in color via alpha setting
    # plot the selected variable last, i.e. on top of all others, by ordering varnames
    vname_ordered = ()
    vnameselect   = list(gglobs.varsBook)[gglobs.exgg.select.currentIndex()]

    # start GL with command 'graphdemo' to get the demo variations of alpha and lw
    if not gglobs.graphdemo:
        #~corr_alpha  = 0.5
        corr_alpha  = 0.7
        corr_lw_sel = 2
        corr_lw_oth = 1
    else:
        corr_alpha  = 1
        corr_lw_sel = 2
        corr_lw_oth = 2

    for i, vname in enumerate(gglobs.varsBook):
        # emphasize: select var in brighter, wider line
        if vname == vnameselect:
            varPlotStyle[vname]['alpha']     = plotalpha
            varPlotStyle[vname]['linewidth'] = float(varPlotStyle[vname]['linewidth']) * corr_lw_sel

        # de-emphasize: non-select var in dimmer, thinner line
        else:
            varPlotStyle[vname]['alpha']     = plotalpha * corr_alpha
            varPlotStyle[vname]['linewidth'] = float(varPlotStyle[vname]['linewidth']) * corr_lw_oth
            vname_ordered                   += (vname,)
        #print("----------vname, alpha, linewidth:", vname, varPlotStyle[vname]['alpha'], varPlotStyle[vname]['linewidth'])

    vname_ordered += (vnameselect,)
    #print("------vname_ordered:", vname_ordered)

    #
    # plot the data
    #
    varlines            = {}            # lines objects for legend
    varlabels           = {}            # labels for legend
    logSliceMod         = {}            # data of the variables

    gglobs.logSliceMod  = {}            # data; will be used by Stat, Poiss, FFT

    # used like:       VarName  Unit   Avg      StdDev     Variance          Range         Recs   LastValue
    fmtLineLabel     = "{:8s}: {:7s}{:>8.2f} ±{:<8.3g}   {:>8.2f}   {:>7.6g} ... {:<7.6g}  {:7d}    {}"
    fmtLineLabelTip  = "{:s}: [{}]  Avg: {:<8.2f}  StdDev: {:<0.3g}   Variance: {:<0.3g}   Range: {:>0.6g} ... {:<0.6g}  Recs: {}   Last Value: {}"

    #arrprint(fncname + "logSlice:", logSlice)
    #arrprint(fncname + "scaleFactor:", scaleFactor)
    for vname in vname_ordered:
#        print("plot the data: vname:", vname)
        if gglobs.exgg.varDisplayCheckbox[vname].isChecked():
            #print("logSlice[vname]:", type(logSlice[vname]), logSlice[vname] )
            #print("scaleFactor[vname]:", type(scaleFactor[vname]), scaleFactor[vname] )
            y                           = logSlice[vname] * scaleFactor[vname]
            ymask                       = np.isfinite(y)      # mask for nan values
            var_y                       = y[ymask]
            var_x                       = x[ymask]

            gglobs.logSliceMod[vname]   = y  # will be used by Stat, Poiss, FFT

            var_size                    = var_y.size
            #print("vname: var_size:", vname, var_size)
            if var_size == 0: continue

            var_avg                     = np.nanmean(var_y)
            var_std                     = np.nanstd (var_y)
            var_var                     = np.nanvar (var_y)
            var_max                     = np.nanmax (var_y)
            var_min                     = np.nanmin (var_y)
            var_size                    = var_y.size
            var_err                     = var_std / np.sqrt(var_size)
            var_recs                    = np.count_nonzero(~np.isnan(var_y))
            if gglobs.lastValues == None:   var_lastval = "    N.A."
            else:                           var_lastval = "{:>8.2f}".format(gglobs.lastValues[vname])
            #print("var_lastval:", var_lastval)

            var_unit                    = gglobs.varsBook[vname][2]

            varlabels[vname]            = fmtLineLabel   .format(vname, "[" + var_unit + "]", var_avg, var_std, var_var, var_min, var_max, var_recs, var_lastval)
            Tip                         = fmtLineLabelTip.format(gglobs.varsBook[vname][0], var_unit, var_avg, var_std, var_var, var_min, var_max, var_recs, var_lastval)
            gglobs.exgg.varDisplayCheckbox[vname].setToolTip  (Tip)
            gglobs.exgg.varDisplayCheckbox[vname].setStatusTip(Tip)

            varPlotStyle[vname]['markersize'] = float(plotstyle['markersize']) / np.sqrt(var_size)
            varlines[vname] = plotLine(var_x, var_y, gglobs.Xunit, vname, **varPlotStyle[vname])

    # fill the globals
    gglobs.varlabels = varlabels

    #
    # Plot the Moving Average
    #
    plotMovingAverage(x, logSlice, scaleFactor, varPlotStyle)

    #
    # Plot the Average and +/- 95% as horizontal lines
    #
    plotAverage(x, logSlice, scaleFactor, varPlotStyle)

    #
    # apply the Y-Limits
    #
    if   gglobs.Ymin  != None and gglobs.Ymax  != None:  ax1.set_ylim(bottom = gglobs.Ymin,     top = gglobs.Ymax)
    elif gglobs.Ymin  != None:                           ax1.set_ylim(bottom = gglobs.Ymin)
    elif                          gglobs.Ymax  != None:  ax1.set_ylim(                          top = gglobs.Ymax)

    if   gglobs.Y2min != None and gglobs.Y2max != None:  ax2.set_ylim(bottom = gglobs.Y2min,    top = gglobs.Y2max)
    elif gglobs.Y2min != None:                           ax2.set_ylim(bottom = gglobs.Y2min)
    elif                          gglobs.Y2max != None:  ax2.set_ylim(                          top = gglobs.Y2max)

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
    for vname in gglobs.varsDefault:
        p   = plt.Rectangle((0, 0), 1, 1, fc=gglobs.varsBook[vname][3], ec="black", lw=0.2)
        pp += (p,)
        pl += (gglobs.varsBook[vname][0],)
    plt.figlegend(pp, pl, shadow=False, mode="expand", handlelength=1.6, ncol=6, framealpha=0)

    #
    # refresh the figure
    #
    fig.canvas.draw_idle()

    # finish
    stopdone   = time.time()
    stopwatch += "+ {:6.1f} ms graph draw".format((stopdone - stopprep) * 1000)
    stopwatch  = "{:<25s}{:0.1f} ms   ({})".format("Total " + fncname, (stopdone - start) * 1000, stopwatch)
    vprint(stopwatch)

    #print(fncname + "EXIT : gglobs.XunitCurrent:", gglobs.XunitCurrent)


def plotAverage(x, logSlice, scaleFactor, varPlotStyle):
    """Plot the Average and +/- 95% as horizontal lines"""

    if not gglobs.avgChecked: return

    vname     = list(gglobs.varsBook)[gglobs.exgg.select.currentIndex()]
    #print("average: vname, gglobs.exgg.varDisplayCheckbox[vname].isChecked():", vname, gglobs.exgg.varDisplayCheckbox[vname].isChecked())
    if gglobs.exgg.varDisplayCheckbox[vname].isChecked():
        avg_Time                     = np.array([x[0], x[-1]])
        #print("plotAverage: avg_Time: ", avg_Time)

        logSliceMod                  = logSlice[vname] * scaleFactor[vname]
        #print("logSliceMod:", logSliceMod)

        avg_avg                      = np.nanmean(logSliceMod)

        if avg_avg >= 0:    avg_std = np.sqrt(avg_avg)  # this is std.dev derived from avg!
        else:               avg_std = gglobs.NAN        # not valid for neg numbers
        #print("---Avg: {}, StdDev of Data: {:6.3f}, SQRT(avg): {:6.3f}".format(avg_avg, np.nanstd (logSliceMod), avg_std))

        # limit 2 sigma: https://en.wikipedia.org/wiki/68%E2%80%9395%E2%80%9399.7_rule
        #                https://en.wikipedia.org/wiki/1.96
        avg_CPMS                     = np.array([avg_avg, avg_avg]) # MUST use np.aray!
        avg_plotHiLo = False
        if avg_avg >= 0:
            avg_CPMS_lo              = avg_CPMS - avg_std * 1.96
            avg_CPMS_hi              = avg_CPMS + avg_std * 1.96
            avg_plotHiLo             = (avg_avg - avg_std * 1.96) > 0 # flag to plot 95%

        if vname in ("T", "P", "H"): avg_plotHiLo = False # no limits drawn for T,P,H

        avg_plotstyle                = varPlotStyle[vname].copy()
        avg_plotstyle["linewidth"]   = 2
        avg_plotstyle["markersize"]  = 0

        avg_plotstyle2               = varPlotStyle[vname].copy()
        avg_plotstyle2["linewidth"]  = 5
        avg_plotstyle2["color"]      = "yellow"
        avg_plotstyle2["markersize"] = 0

        plotLine(avg_Time, avg_CPMS, gglobs.Xunit, vname, **avg_plotstyle2) # makey yellow shadow around line
        plotLine(avg_Time, avg_CPMS, gglobs.Xunit, vname, **avg_plotstyle)

        if avg_plotHiLo :
            # plot dashed lin color of var, interrupted by white dots
            # makes it visible on white and on var color
            avg_plotstyle["linestyle"]  = "--"
            plotLine(avg_Time, avg_CPMS_lo, gglobs.Xunit, vname, **avg_plotstyle)
            plotLine(avg_Time, avg_CPMS_hi, gglobs.Xunit, vname, **avg_plotstyle)

            avg_plotstyle["color"]      = "white"
            avg_plotstyle["linestyle"]  = ":"
            plotLine(avg_Time, avg_CPMS_lo, gglobs.Xunit, vname, **avg_plotstyle)
            plotLine(avg_Time, avg_CPMS_hi, gglobs.Xunit, vname, **avg_plotstyle)


def plotMovingAverage(x, logSlice, scaleFactor, varPlotStyle):
    """Plot the Moving Average"""

    if not gglobs.mavChecked: return

    # Plot the moving average over N datapoints with a thin line in the
    # variable's color on a yellow thick line.
    # Do the average over no more than N/2 data points. Determine N from time
    # delta between first and last record and the number of records.
    # Note: improper with long periods of no data, or changing cycle time!
    # In plot skip the first and last N/2 data points, which are meaningless
    # due to averaging.

    vname           = list(gglobs.varsBook)[gglobs.exgg.select.currentIndex()]

    lSM_mask        = np.isfinite(logSlice[vname])          # mask for nan values
    logSliceNoNAN   = logSlice[vname][lSM_mask]             # all NANs removed

    if logSliceNoNAN.size == 0: return                      # no data, return

    logSliceMod     = logSliceNoNAN * scaleFactor[vname]

    x_mav           = x[lSM_mask]
    x_mav_size      = x_mav.size
    x_mav_max       = x_mav.max()
    x_mav_min       = x_mav.min()

    logCycle        = (gglobs.logTimeSlice.max() - gglobs.logTimeSlice.min()) / x_mav_size
    logCycle       *= 86400.0                      # apparent cycle time in sec
    Nmav            = round(gglobs.mav / logCycle) # e.g. 100 sec / 2 sec -> 50 datapoints; rounding to integer value

    if gglobs.fprintMAV:
        gglobs.fprintMAV = False # print only once after a change
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
    #dprint("lower, upper, delta:", lower, upper, upper - lower)

    if upper - lower > 2: # needs more than a single record
        if gglobs.exgg.varDisplayCheckbox[vname].isChecked():

            mav_label                   = "MvAvg, N={:0.0f} ({:0.0f}sec)".format(N, new_mav)

            mav_x = x_mav[lower:upper]
            mav_y = np.convolve(logSliceMod,     np.ones((N,))/N, mode='same')[lower:upper]

            mav_plotstyle               = varPlotStyle[vname].copy()
            mav_plotstyle['color']      = 'yellow'
            mav_plotstyle['linewidth']  = 4
            mav_plotstyle['markersize'] = 0
            plotLine(mav_x, mav_y, gglobs.Xunit, vname, **mav_plotstyle)

            mav_plotstyle['color']      = varPlotStyle[vname]['color']
            mav_plotstyle['linewidth']  = 2
            mav_plotstyle['label']       = mav_label
            mav_line = plotLine(mav_x, mav_y, gglobs.Xunit, vname, drawlegend=True, **mav_plotstyle)

    else:
        fprint("ALERT: Not enough data to plot Moving Average")


def plotLine(x, y, xunit="Time", vname="CPM", drawlegend=False, **plotstyle):
    """plots a single line of data"""

    global xFormatStr

    #print("plotLine: xunit:", xunit, ", x: ", x, ", y: ", y, "\nplotstyle:", plotstyle)

    if vname in ("CPM", "CPS", "CPM1st", "CPS1st", "CPM2nd", "CPS2nd", "CPM3rd", "CPS3rd"):
        yaxis  = ax1
    else: # T, P, H, X
        yaxis  = ax2

    #   scaleVarValues(variable, value, scale); scale like: LOG10(val)
    y = scaleVarValues(vname,    y,     gglobs.GraphScale[vname])
    #print("plotLine: xunit:", xunit, ", x: ", x, ", y: ", y)

    if xunit == "Time":
        fig.autofmt_xdate(rotation = 15)
        #formatter   = mpld.AutoDateFormatter(mpld.AutoDateLocator()) # What for?
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


###############################################################################
# NOT IN USE!
#~def updatePlot(filePath, timetag, cpm):
    #~"""updates an existing plot (made by makePlot) with last record"""
    #~# caution: not active; not tested for current code!!!

    #~start= time.time()

    #~try:
        #~x = gglobs.logTime[0]   # logTime is defined only after 1st plot
    #~except:
        #~print("updatePlot, no gglobs.logTimeSlice.size")
        #~return

    #~if gglobs.XunitCurrent == "Time":
        #~# plot versus Date&Time of day
        #~ptime = mpld.datestr2num(timetag)
    #~else:
        #~# Plot vs DiffTime (time since first record)
        #~# XunitCurrent is one of second, minute, hour day
        #~ptime = mpld.datestr2num(timetag) - gglobs.logTime[0]

    #~# rescale for X-axis
    #~if gglobs.XunitCurrent   == "second":
        #~ptime = ptime * 86400.              # convert to seconds
    #~elif gglobs.XunitCurrent == "minute":
        #~ptime = ptime * 1440.               # convert to minutes
    #~elif gglobs.XunitCurrent == "hour":
        #~ptime = ptime * 24.                 # convert to hours
    #~elif gglobs.XunitCurrent == "day":
        #~pass                                # is in days already
    #~else:
        #~pass                                # gglobs.XunitCurrent is "Time"

    #~# rescale for Y-axis
    #~if gglobs.Yunit == "CPS":        cpm /= 60.
    #~#print "ptime:", ptime, "cpm:", cpm

    #~rdplt.set_xdata(np.append(rdplt.get_xdata(), ptime))
    #~rdplt.set_ydata(np.append(rdplt.get_ydata(), cpm))

    #~gglobs.sizePlotSlice += 1

    #~subTitle = 'File:' + os.path.basename(filePath) + "  Recs:" + str(gglobs.sizePlotSlice)
    #~plt.title(subTitle, fontsize=12, fontweight='normal', loc = 'right')

    #~ax = plt.gca()
    #~ax.relim()              # recompute the ax.dataLim
    #~ax.autoscale_view()     # update ax.viewLim using the new dataLim

    #~#plt.draw()   # seems to be unnecessary

    #~stop = time.time()
    #~dprint("updatePlot: update: {:0.1f} ms Total".format( (stop - start) * 1000))

# end of not in use
###############################################################################
