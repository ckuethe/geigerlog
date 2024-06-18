#! /usr/bin/env python3
# -*- coding: UTF-8 -*-

"""
gsup_plot.py - GeigerLog commands to plot data collected from from Geiger Counter

include in programs with:
    include gsup_plot

Data in the form:
    #Index  DateTime              CPM, CPS, ...
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
__copyright__       = "Copyright 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024"
__credits__         = [""]
__license__         = "GPL3"

from gsup_utils   import *

# keep - had been used for legend placement
# legendPlacement = {0:'upper left',   1:'upper center', 2:'upper right',
#                    3:'center right', 4:'lower right',  5:'lower center',
#                    6:'lower left',   7:'center left',  8:'center'}


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


def getTimeOfDay(Tfirst, delta, deltaUnit):
    """From time of first record = Tfirst plus the delta time in days
    return TimeOfDay; used only in function updatecursorposition"""

    if   deltaUnit == "hour":       x = delta / 24.
    elif deltaUnit == "minute":     x = delta / 24. / 60.
    elif deltaUnit == "second":     x = delta / 24. / 60. / 60.
    else:                           x = delta # delta is in the correct unit day

    ret = str(mpld.num2date(Tfirst + x))[:19]
    #print("getToD: ret:", ret)

    return ret

# not used any more - keep (just in case)
# def getXLabelsToD():
#     """find proper label for x-axis and x-ticks when g.Xunit == "Time";
#     used only in gsup_plot.makePlot"""

#     global plotTime, strFirstRecord

#     #~totalDays     = (plotTime.max() - plotTime.min()) # in days

#     #~if   totalDays                  > 5:    tformat = '%Y-%m-%d'            # > 5 d
#     #~elif totalDays                  > 1:    tformat = '%Y-%m-%d  %H:%M:%S'  # > 1 d
#     #~elif totalDays * 24             > 1:    tformat = '%Y-%m-%d  %H:%M:%S'  # > 1 h
#     #~elif totalDays * 24 * 60        > 1:    tformat = '%H:%M:%S'            # > 1 min
#     #~elif totalDays * 24 * 60 * 60   > 1:    tformat = '%H:%M:%S'            # > 1 sec
#     #~else:                                   tformat = '%Y-%m-%d  %H:%M:%S'  # else
#     #~#print("getXLabelsToD: ret: ", tformat, 'Time (First Record: {})'.format(strFirstRecord))

#     tformat = '%Y-%m-%d  %H:%M:%S'  # always the same full format
#     return tformat, 'Time (First Record: {})'.format(strFirstRecord)


def getXLabelsSince(Xunit):
    """find proper label for x-axis and x-ticks when g.Xunit other than "Time";
    used only in gsup_plot.makePlot"""

    global plotTime, strFirstRecord

    #print("getXLabelsSince: g.XunitCurrent:", g.XunitCurrent)

    oldXunit = g.XunitCurrent
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

    g.XunitCurrent = newXunit

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
        if g.Xleft is not None:
            try:
                xleft = float(g.Xleft)
                g.Xleft = xleft / oldfactor * newfactor # convert all to days, then to new unit
            except Exception as e:
                exceptPrint(e, "xleft")
                g.Xleft = None

        if g.Xright is not None:
            try:
                xright = float(g.Xright)
                g.Xright = xright / oldfactor * newfactor # convert all to days, then to new unit
            except Exception as e:
                exceptPrint(e, "xright")
                g.Xright = None

        strxl = "{:1.8f}".format(float(g.Xleft) ) if g.Xleft  is not None else ""
        strxr = "{:1.8f}".format(float(g.Xright)) if g.Xright is not None else ""
        g.exgg.xmin.setText(strxl)
        g.exgg.xmax.setText(strxr)

    return 'time {} since first record: {}'.format(xlabel, strFirstRecord)


def changeTimeUnitofPlot(newXunit):
    """recalc xmin, xmax on Time unit changes"""

    #print("-----------------------changedGraphTimeUnit: i:", i)

    if np.all(g.logTime) is None: return

    oldXunit = g.XunitCurrent
    #print("changedGraphTimeUnit: oldXunit: ", oldXunit)

    # convert all entries to days since start
    if   oldXunit == "Time":
        if g.Xleft  is not None: g.Xleft  = g.Xleft  - g.logTimeFirst
        if g.Xright is not None: g.Xright = g.Xright - g.logTimeFirst

    elif oldXunit == "month":
        if g.Xleft  is not None: g.Xleft  = g.Xleft  * 30.42 # 365 / 12 = 30.4167
        if g.Xright is not None: g.Xright = g.Xright * 30.42 # 365 / 12 = 30.4167

    elif oldXunit == "week":
        if g.Xleft  is not None: g.Xleft  = g.Xleft  * 7
        if g.Xright is not None: g.Xright = g.Xright * 7

    elif oldXunit == "day": # no changes all in days
        if g.Xleft  is not None: g.Xleft  = g.Xleft
        if g.Xright is not None: g.Xright = g.Xright

    elif oldXunit == "hour":
        if g.Xleft  is not None: g.Xleft  = g.Xleft  / 24.
        if g.Xright is not None: g.Xright = g.Xright / 24.

    elif oldXunit == "minute":
        if g.Xleft  is not None: g.Xleft  = g.Xleft  / 1440.
        if g.Xright is not None: g.Xright = g.Xright / 1440.

    elif oldXunit == "second":
        if g.Xleft  is not None: g.Xleft  = g.Xleft  / 86400.
        if g.Xright is not None: g.Xright = g.Xright / 86400.

    #~g.XunitCurrent = str(self.xunit.currentText())
    #~print("changedGraphTimeUnit: g.XunitCurrent: ", g.XunitCurrent)
    #~newXunit            = g.XunitCurrent
    #newXunit            = self.xunit.currentText()
    if newXunit == "auto":
        l = g.logTime.max() - g.logTime.min()
        #print "l=", l
        if   l         > 3:  Xunit = "day"
        elif l * 24.   > 3:  Xunit = "hour"
        elif l * 1440. > 3:  Xunit = "minute"
        else:                Xunit = "second"

        newXunit = Xunit

    g.XunitCurrent = newXunit
    #~print("changedGraphTimeUnit: g.XunitCurrent: ", g.XunitCurrent)
    g.Xunit        = newXunit
    #print( "newXunit", newXunit)

    if newXunit == "Time":
        if g.Xleft  is not None: g.Xleft =  (str(mpld.num2date((g.Xleft  + g.logTimeFirst))))[:19]
        if g.Xright is not None: g.Xright = (str(mpld.num2date((g.Xright + g.logTimeFirst))))[:19]

    elif newXunit == "month":
        if g.Xleft  is not None: g.Xleft  = g.Xleft  / 30.42 # 365 / 12 = 30.4167
        if g.Xright is not None: g.Xright = g.Xright / 30.42 # 365 / 12 = 30.4167

    elif newXunit == "week":
        if g.Xleft  is not None: g.Xleft  = g.Xleft  / 7
        if g.Xright is not None: g.Xright = g.Xright / 7

    elif newXunit == "day": # no changes all in days
        if g.Xleft  is not None: g.Xleft  = g.Xleft
        if g.Xright is not None: g.Xright = g.Xright

    elif newXunit == "hour":
        if g.Xleft  is not None: g.Xleft  = g.Xleft  * 24
        if g.Xright is not None: g.Xright = g.Xright * 24

    elif newXunit == "minute":
        if g.Xleft  is not None: g.Xleft  = g.Xleft  * 1440
        if g.Xright is not None: g.Xright = g.Xright * 1440

    elif newXunit == "second":
        if g.Xleft  is not None: g.Xleft  = g.Xleft  * 86400
        if g.Xright is not None: g.Xright = g.Xright * 86400

    if g.Xleft is None:
        g.exgg.xmin.setText("")
    else:
        try:    xl = "{:1.8f}".format(float(g.Xleft))
        except: xl = g.Xleft
        g.exgg.xmin.setText(xl)

    if g.Xright is None:
        g.exgg.xmax.setText("")
    else:
        try:    xr = "{:1.8f}".format(float(g.Xright))
        except: xr = g.Xright
        g.exgg.xmax.setText(xr)


#mmm
def makePlot(halt=False):
    """Plots the data in array g.currentDBData vs. time-of-day or vs time-since-start,
    observing plot settings; using matplotlib date functions

    Return: "" or PlotMsg
    """

    # local function ###########################################
    def clearFigure():
        """löscht die main fig"""

        # DEVEL  : ...503    clearFigure() 1: takes: 0.042 ms
        # DEVEL  : ...504    clearFigure() 2: takes: 36.701 ms

        global fig

        defname = "clearFigure: "

        # start = time.time()
        fig = plt.figure(1)
        # cdprint(defname, "1: takes: {:0.3f} ms".format(1000 * (time.time() - start)))

        g.FigMainGraph = fig

        # start = time.time()
        plt.clf()                                # is REQUIRED, kostet 30 ... 50 ms
        # cdprint(defname, "2: takes: {:0.3f} ms".format(1000 * (time.time() - start)))

        # start = time.time()
        fig.canvas.draw_idle()                   # is REQUIRED. kostet 0.04 ms
        # cdprint(defname, "draw idle: takes: {:0.3f} ms".format(1000 * (time.time() - start)))
    # end local function ###########################################


    global plotTime, strFirstRecord, rdplt, fig, ax1, ax2, xFormatStr

    startMkPlt = time.time()            # timing durations
    defname    = "makePlot: "
    # rdprint(defname)

    if not g.allowGraphUpdate : return ""
    if not g.GraphAction      : return defname + "Graph Update is HALTED; click button 'Graph' to continue"

    # print(defname, "-"*100)
    # print(defname + "  g.currentDBData.shape:",  g.currentDBData.shape)
    # print(defname + "  g.currentDBData:\n",      g.currentDBData)
    # print(defname + "  g.logDBData:\n",          g.logDBData)
    # print(defname + "  g.hisDBData:\n",          g.hisDBData)

    if np.all(g.currentDBData) is None   : return ""

    # rdprint(defname, "sizeof g.currentDBData: {:0,.0f} Byte".format(sys.getsizeof(g.currentDBData))) # = no of records * 104 + 128

    try:
        if g.currentDBData.size == 0:
            dprint(defname + "no records; nothing to plot")
            clearFigure()
            return ""
    except Exception as e:
        # if there is no g.currentDBData then .size results in error
        # but then there is also nothing to plot
        msg = defname + "no 'g.currentDBData', nothing to plot"
        exceptPrint(e, msg)
        efprint(msg)
        clearFigure()
        return ""

    # clear the checkboxes' by settinb default ToolTip of the vname only
    for vname in g.VarsCopy:
        g.exgg.varDisplayCheckbox[vname].setToolTip(g.VarsCopy[vname][0])

    # NOTE: see: https://matplotlib.org/stable/api/dates_api.html
    # Quote:"
    #   Before Matplotlib 3.3, the epoch was 0000-12-31T00:00:00 which lost modern microsecond
    #   precision and also made the default axis limit of 0 an invalid datetime.
    #   In 3.3 time the epoch was changed to 1970-01-01T00:00:00 with 0.35 microsecond resolution.
    #   To convert old ordinal floats to the new epoch, users can do:
    #      new_ordinal = old_ordinal + mdates.date2num(np.datetime64('0000-12-31'))
    # "end quote
    #
    # On my system the default is:  "1970-01-01T00:00"
    # set epoch, see: https://matplotlib.org/stable/api/dates_api.html#matplotlib.dates.set_epoch
    # print("print(matplotlib.dates.get_epoch())")
    # print(matplotlib.dates.get_epoch())               # --> "1970-01-01T00:00" the default is set already
    # matplotlib.dates.set_epoch("1970-01-01T00:00")    # not needed; is default already
    #

    # g.MPLDTIMECORRECTION:  Matplotlib TimeBaseCorrection is set in gsup_utils to: -719163.0
    g.logTime          = g.currentDBData[:, 0] + g.MPLDTIMECORRECTION    # time data of total file
    g.logTimeFirst     = g.logTime[0]                                    # time of first record in total file
    g.logTimeDiff      = g.logTime - g.logTimeFirst                      # using time diff to first record in days

    # get time of first record
    try:
        ltf = (mpld.num2date(g.logTimeFirst, tz=None))
    except Exception as e:
        msg = defname + "ERROR: incorrect value in 'g.logTimeFirst', cannot plot"
        exceptPrint(e, msg)
        efprint(msg)
        clearFigure()
        return ""

    # rounding the time
    # mpld.num2date(g.logTimeFirst) delivers date with sec fractions, like: 2019-01-02 18:05:00.999980+00:00
    # but does not allow rounding to a second. Therefore cutting off after 19 chars (before the '.')
    # may yield a time too low by 1 second, like:
    #   2019-01-02 18:05:00 instead of:
    #   2019-01-02 18:05:01
    F0 = ltf.strftime("%Y-%m-%d %H:%M:%S.%f")
    # rdprint(defname, "F0: ", F0)
    try:
        # good! 2020-08-18 16:34:11.609016 -> 2020-08-18 16:34:12
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
    if g.Xunit == "Time" :
        plotTime                = g.logTime
        xFormatStr              = "%Y-%m-%d  %H:%M:%S"      # always the same full format,
                                                            # not using XLabelsToD()!
        xLabelStr               = "Time (First Record: {})".format(strFirstRecord)
    else:
        plotTime                = g.logTimeDiff
        xLabelStr               = getXLabelsSince(g.Xunit)

    # split multi-dim np.array into 10 single-dim np.arrays like log["CPM"] = [<var data>]
    log = {}
    for i, vname in enumerate(g.VarsCopy):
        log[vname] = g.currentDBData[:, i + 1]
        #print("{}: log[{}]: {}".format(i, vname, log[vname]))

    # is the temperature to be shown in °C or °F ? (data are in °C )
    if g.VarsCopy["Temp"][2] == "°F":        log["Temp"] = log["Temp"] / 5 * 9 + 32

    # confine limits to what is available
    Xleft = g.Xleft
    Xright= g.Xright

    #dprint("before re-setting limits: Xleft, Xright, plotTime.min, plotTime.max   {}   {}   {}   {}".format(g.Xleft, g.Xright, plotTime.min(), plotTime.max()))
    if Xright is None or Xright > plotTime.max():    Xright = plotTime.max()
    if                   Xright < plotTime.min():    Xright = plotTime.min()
    if Xleft  is None or Xleft  < plotTime.min():    Xleft  = plotTime.min()
    if                   Xleft  > plotTime.max():    Xleft  = plotTime.max()
    #dprint("after                                                                 {}   {}   {}   {}".format(Xleft, Xright, plotTime.min(), plotTime.max()))

    # find the records, where the time limits apply
    recmin = np.where(plotTime >= Xleft )[0][0]
    recmax = np.where(plotTime <= Xright)[0].max() # excludes recs > g.Xleft, and takes max of remaining
    #dprint("recmin, recmax:", recmin, recmax)

    # slice the arrays; include record #recmax (thus +1)
    g.logTimeSlice         = g.logTime     [recmin:recmax + 1 ]
    g.logTimeDiffSlice     = g.logTimeDiff [recmin:recmax + 1 ]
    x                      = plotTime      [recmin:recmax + 1 ]   # plotTime is either Time or TimeDiff

    if g.logTimeSlice.size == 0:
        fprint("ALERT: No records in selected range")
        return ""

    logSlice        = {}
    for vname in g.VarsCopy:
        logSlice[vname] = log[vname][recmin:recmax + 1 ]
    g.logSlice = logSlice
    g.dataSlicerecmax = recmax


    stopprep   = time.time()
    stopwatch  = "{:0.0f} ms data load and prep".format((stopprep - startMkPlt) * 1000)

    ###########################################################################
    # prepare the graph
    ###########################################################################

    g.plotIsBusy = True

    while g.savingPlotIsBusy:   # wait as long as plt is being saved
        rdprint(defname, "savingPlotIsBusy-------------------------------")

    clearFigure()

    # get/set left and right Y-axis
    ax1 = plt.gca()                           # left Y-axis
    ax2 = ax1.twinx()                         # right Y-Axis

    vnameselect   = list(g.VarsCopy)[g.exgg.select.currentIndex()]              # get the selected Variable

    # The 'b' parameter of grid() has been renamed 'visible' since Matplotlib 3.5;
    # support for the old name will be dropped two minor releases later.
    if vnameselect in ("CPM", "CPS", "CPM1st", "CPS1st", "CPM2nd", "CPS2nd", "CPM3rd", "CPS3rd"):
        ax1.grid(visible=True, axis="both")         # left Y-axis grid + X-grid
    else:
        ax1.grid(visible=True, axis="x")            # X-axis grid
        ax2.grid(visible=True, axis="y")            # right Y-axis grid

    mysubTitle = os.path.basename(g.currentDBPath) + "   " + "Recs:" + str(g.logTimeSlice.size)
    plt.title(mysubTitle, fontsize= 9, fontweight='normal', loc='right')
    plt.subplots_adjust(hspace=None, wspace=None , left=0.15, top=0.84, bottom=0.10, right=.87)

    # avoid "offset" and "scientific notation" on the Y-axis, i.e. showing scale in exponential units
    # https://stackoverflow.com/questions/28371674/prevent-scientific-notation-in-matplotlib-pyplot
    ax1.ticklabel_format(useOffset=False, style='plain', axis='x')
    ax1.ticklabel_format(useOffset=False, style='plain', axis='y')
    ax2.ticklabel_format(useOffset=False, style='plain', axis='x')
    ax2.ticklabel_format(useOffset=False, style='plain', axis='y')

    # # make ticks red
    # # for larger numbers use option: "labelsize='medium'"
    # ax2.tick_params(axis='y', colors='red')

    # hide the cursor position from showing in the toolbar
    ax1.format_coord = lambda x, y: ""
    ax2.format_coord = lambda x, y: ""

    #
    # add labels to all three axis
    #
    # X-axis
    ax1.set_xlabel(xLabelStr, fontsize=10, fontweight='bold')

    # Y1-axis
    if g.Yunit == "CPM":        ylabel = "Counter  [CPM or CPS]"
    else:                       ylabel = "Counter  [µSv/h]"
    ax1.set_ylabel(ylabel,  fontsize=12, fontweight='bold')

    # Y2-axis
    y2label = "Ambient"
    ax2.set_ylabel(y2label, fontsize=12, fontweight='bold')

    #
    # set the µSv-scaling factor
    #
    # g.Yunit == "CPM":
    scaleFactor = {"CPM":1, "CPS":1, "CPM1st":1, "CPS1st":1, "CPM2nd":1, "CPS2nd":1, "CPM3rd":1, "CPS3rd":1, "Temp":1, "Press":1, "Humid":1, "Xtra":1}
    # rdprint("scaleFactor:", type(scaleFactor), scaleFactor)

    if g.Yunit == "µSv/h":
        scale = [None] * 4
        burps = []
        for i in range(0, 4):
            if type(g.Sensitivity[i]) in (int, float):
                scale[i] = 1 / g.Sensitivity[i]
            else:
                scale[i] = g.NAN
                burps.append(i)

        if len(burps) > 0:
            msg = "Switching Counter Dose rate from CPM to µSv/h"
            fprint(header(msg))
            dprint(msg)
            msgfmt = "Sensitivity undefined: {:30s}{}\n"
            msg = "\n"
            # rdprint(defname, "burps: ", burps)
            if   0 in burps:  msg += msgfmt.format("Tube CPM/CPS:",       "{} CPM / (µSv/h)" .format(g.Sensitivity[0]))
            if   1 in burps:  msg += msgfmt.format("Tube CPM1st/CPS1st:", "{} CPM / (µSv/h)" .format(g.Sensitivity[1]))
            if   2 in burps:  msg += msgfmt.format("Tube CPM2nd/CPS2nd:", "{} CPM / (µSv/h)" .format(g.Sensitivity[2]))
            if   3 in burps:  msg += msgfmt.format("Tube CPM3rd/CPS3rd:", "{} CPM / (µSv/h)" .format(g.Sensitivity[3]))
            qefprint(msg)
            dprint(msg)
            burp()

        for vname in scaleFactor:
            # rdprint(defname, "vname: ", vname)
            if   vname in ("CPM", "CPS"):
                    scaleFactor[vname]    = scale[0]
                    scaleFactor['CPS']    = scale[0] * 60

            elif vname in ("CPM1st", "CPS1st"):
                    scaleFactor[vname]    = scale[1]
                    scaleFactor['CPS1st'] = scale[1] * 60

            elif vname in ("CPM2nd", "CPS2nd"):
                    scaleFactor[vname]    = scale[2]
                    scaleFactor["CPS2nd"] = scale[2] * 60

            elif vname in ("CPM3rd", "CPS3rd"):
                    scaleFactor[vname]    = scale[3]
                    scaleFactor["CPS3rd"] = scale[3] * 60

    # mdprint("scaleFactor:", type(scaleFactor), scaleFactor)

    #
    # set the plotting style
    #
    # each variable gets a copy of the plotstyle, which is then corrected for
    # the color chosen for each variable
    plotalpha        = 1.0
    plotstyle        = {'color'             : g.linecolor,      # overwritten by Style from VarsCopy
                        'linestyle'         : g.linestyle,      # overwritten by Style from VarsCopy
                        'linewidth'         : g.linewidth,
                        'label'             : "",
                        'markeredgecolor'   : g.linecolor,      # overwritten by Style from VarsCopy
                        'marker'            : g.markersymbol,
                        'markersize'        : g.markersize,
                        'alpha'             : plotalpha,
                        }

    varPlotStyle    = {}                                        # holds the plotstyle for each variable
    for i, vname in enumerate(g.VarsCopy):
        varPlotStyle[vname]                       = plotstyle.copy()
        varPlotStyle[vname]['color']              = g.VarsCopy[vname][3]
        varPlotStyle[vname]['markeredgecolor']    = g.VarsCopy[vname][3]
        varPlotStyle[vname]['linestyle']          = g.VarsCopy[vname][4]


    # Halting the Updates
    if halt:
        plt.text(0.50, 0.63, "Graph Updates are Halted",                fontsize=20, fontweight=1000, horizontalalignment="center")
        plt.text(0.50, 0.53, "Logging does continue",                   fontsize=16, fontweight=700,  horizontalalignment="center")
        plt.text(0.50, 0.43, "Press button 'Graph' to resume updating", fontsize=16, fontweight=100,  horizontalalignment="center")
        return "Halted"

    #
    # Emphasize the selected variable by color and line thickness and draw last (on top)
    #
    # the selected var will be drawn with thicker lines and full brightness, other lines
    # will be dimmed in color via alpha setting.
    # Plot the selected variable last, i.e. on top of all others, by ordering varnames
    vname_ordered = ()
    # vnameselect   = list(g.VarsCopy)[g.exgg.select.currentIndex()]    # ist bereits definiert

    # start GL with command 'graphbold' to get the demo variations of alpha and lw
    # which is:     alpha     = 1 -> not transparent
    #               linewidth = 2 -> all lines same big width
    if not g.graphbold:
        corr_alpha  = 0.7
        corr_lw_sel = 2
        # corr_lw_sel = 3     # noch dickere Linie... zu dick
        corr_lw_oth = 1
    else:
        corr_alpha  = 1
        corr_lw_sel = 2
        corr_lw_oth = 2


    for i, vname in enumerate(g.VarsCopy):
        if g.exgg.varDisplayCheckbox[vname].isChecked():
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

    if g.exgg.varDisplayCheckbox[vnameselect].isChecked():
        vname_ordered += (vnameselect,) # plot var select as last over all else, but only if it is checked
        #print("------vname_ordered:", vname_ordered)

    #
    # apply the Y-Limits
    #
    if   g.Ymin  is not None and g.Ymax  is not None:  ax1.set_ylim(bottom = g.Ymin,     top = g.Ymax)
    elif g.Ymin  is not None:                          ax1.set_ylim(bottom = g.Ymin)
    elif                         g.Ymax  is not None:  ax1.set_ylim(                     top = g.Ymax)

    if   g.Y2min is not None and g.Y2max is not None:  ax2.set_ylim(bottom = g.Y2min,    top = g.Y2max)
    elif g.Y2min is not None:                          ax2.set_ylim(bottom = g.Y2min)
    elif                         g.Y2max is not None:  ax2.set_ylim(                     top = g.Y2max)

    # # limits are needed for calculation of the mouse pointer w respect to counter Y-axis
    # # see: def updatecursorposition(self, event)
    # g.y1_limit = ax1.get_ylim()
    # g.y2_limit = ax2.get_ylim()
    # #print("g.y1_limit:", g.y1_limit, ", g.y2_limit:", g.y2_limit)


    #
    # plot the data
    #
    varlines       = {}            # lines objects for legend
    g.logSliceMod  = {}            # data; will be used by Stat, Poiss, FFT

    # arrprint(defname + "logSlice:", logSlice)
    # arrprint(defname + "scaleFactor:", scaleFactor)

    t0 = time.time()
    for vname in vname_ordered:
        # rdprint(defname, "plot vname: ", vname)
        # rdprint("logSlice[vname]:", type(logSlice[vname]), logSlice[vname] )
        # rdprint("vname: {}  scaleFactor[vname]: type:{}   {}".format(vname, type(scaleFactor[vname]), scaleFactor[vname] ))

        g.logSliceMod[vname]        = logSlice[vname] * scaleFactor[vname]      # will be used by Stat, Poiss, FFT
        y                           = g.logSliceMod[vname]

        ymask                       = np.isfinite(y)                            # mask for nan values
        var_y                       = y[ymask]                                  # var_y has nan removed
        var_x                       = x[ymask]                                  # var_x has all elements removed where y had a nan
        var_size                    = var_y.size
        # rdprint(defname, "var_size y: ", var_y.size)
        # rdprint(defname, "var_size x: ", var_x.size)
        if var_size == 0: continue                                              # no data after all nan were removed

        # set the Tips to the checkboxes
        Tip, SuSt = getSuStStats(vname, var_y)
        g.exgg.varDisplayCheckbox[vname].setToolTip  (Tip)
        g.exgg.varDisplayCheckbox[vname].setStatusTip(Tip)

        # set markersize to 0 with more than 100 datapoints
        if var_size > 100: msize = 0
        else:              msize = float(plotstyle['markersize']) / np.sqrt(var_size)

        if not g.graphConnectDots:
            varPlotStyle[vname]['linewidth'] = 0
            msize = 1

        varPlotStyle[vname]['markersize'] = msize

        # finally plot the line
        # using x produces gaps, where a nan value occured; using var_x had the nan values masked out,
        # so that no gaps are visible - preferred, otherwise any lonely dots become invisible over time
        varlines[vname] = plotLine(var_x, var_y, g.Xunit, vname, **varPlotStyle[vname])
        # rdprint(defname, "plot vname: ", vname)


    durplotAllLines = 1000 * (time.time() - t0)

    #
    # Plot the Moving Average
    #
    t0 = time.time()
    plotMovingAverage(x, logSlice, scaleFactor, varPlotStyle)
    durplotMovingAverage = 1000 * (time.time() - t0)


    #
    # Plot the Average and +/- 95% as horizontal lines
    #
    t0 = time.time()
    plotAverage(x, logSlice, scaleFactor, varPlotStyle)
    durplotAverage = 1000 * (time.time() - t0)


    #
    # Plot the LinFit
    #
    t0 = time.time()
    plotLinFit(x, logSlice, scaleFactor, varPlotStyle)
    durplotLinFit = 1000 * (time.time() - t0)


    #
    # Plot the Legend
    #
    pp = ()
    pl = ()
    for vname in g.VarsCopy:
        p   = plt.Rectangle((0, 0), 1, 1, fc=g.VarsCopy[vname][3], ec="black", lw=0.2)
        pp += (p,)
        pl += (g.VarsCopy[vname][0],)
    plt.figlegend(pp, pl, shadow=False, mode="expand", handlelength=1.6, ncol=6, framealpha=0)
    # testing


    #
    # refresh the figure
    #
    # start = time.time()
    # fig.canvas.draw_idle() # is that needed at all????  costs only  0.003 ... 0.005 ms
    # rdprint(defname, "Delta: {:0.3f} ms".format((time.time() - start)*1000))   # 0.003 ... 0.005 ms
    figdone    = time.time()
    stopwatch += " + {:0.0f} ms graph draw".format((figdone - stopprep) * 1000)

    # finish
    durplotTotal = 1000 * (time.time() - startMkPlt)                                        # dur in ms
    stopwatch    = "{} {:0.0f} ms = {}".format(defname + "Total:", durplotTotal, stopwatch)
    stopwatch   += " (Lines:{:0.0f} ms"  .format(durplotAllLines)
    stopwatch   += "  LinFit:{:0.0f} ms" .format(durplotLinFit)
    stopwatch   += "  MovAvg:{:0.0f} ms" .format(durplotMovingAverage)
    stopwatch   += "  Avg:{:0.0f} ms)"   .format(durplotAverage)

    if not g.logging: vprint(stopwatch)

# ### testing the update function: (not working) ########
#     # for vname in vname_ordered:
#     #     if g.exgg.varDisplayCheckbox[vname].isChecked():
#     for vname in ("CPM", "CPS", "CPM1st", "CPS1st"):
#             rdplt = varlines[vname]
#             timetag = x[-1] +0.01
#             cpm     = y[-1] * 0.5
#             updatePlot("testing", timetag, cpm)
# ### end testing #######################################


    # make pic used by Telegram and Monitor
    if g.TelegramNeedsPic:
        g.TelegramNeedsPic   = False
        g.TelegramData[0]    = g.logTime.size           # index of last record
        g.TelegramData[1]    = g.currentDBData[-1][1:]  # last record (without datetime)
        g.TelegramPicBytes   = io.BytesIO()
        makePicFromGraph(g.TelegramPicBytes)
        g.TelegramPicIsReady = True


    g.plotIsBusy = False

    # limits are needed for calculation of the mouse pointer w respect to counter Y-axis
    # see: def updatecursorposition(self, event)
    g.y1_limit = ax1.get_ylim()
    g.y2_limit = ax2.get_ylim()
    #print("g.y1_limit:", g.y1_limit, ", g.y2_limit:", g.y2_limit)


    return stopwatch
#mmm makeplot


def plotLine(x, y, xunit="Time", vname="CPM", drawlegend=False, **plotstyle):
    """plots a single line of data"""

    # ATTENTION:
    # Different definitions for "plot" and "plot_date":
    #     matplotlib.pyplot.plot     (*args, scalex=True, scaley=True, data=None, **kwargs)
    #     matplotlib.pyplot.plot_date(x, y, fmt='o', tz=None, xdate=True, ydate=False, *, data=None, **kwargs)
    # Note that plot_date has "fmt='0'", while plot has not!
    # Using "**plotstyle" results in Warning:
    #     UserWarning: marker is redundantly defined by the 'marker' keyword argument and the fmt string "o"
    #     (-> marker='o'). The keyword argument will take precedence.
    # --> must handle the two plot types differently

    global xFormatStr

    defname = "plotLine: "

    # rdprint(defname, "vname: ", vname)

    # select Y-axis
    vc = ("CPM", "CPS", "CPM1st", "CPS1st", "CPM2nd", "CPS2nd", "CPM3rd", "CPS3rd")
    if vname in vc: yaxis  = ax1  # CP*
    else:           yaxis  = ax2  # Temp, Press, Humid, Xtra

    ### testing
    # if vname == "CPM3rd": yaxis = ax2
    # if vname == "CPM3rd": yaxis = ax1
    ###

    #
    # Graph scaling:  applyValueFormula(variable, value, scale, graph=True)
    # NOTE: variable       is a name like "CPM"
    #       value (here y) is always an np.ndarray!
    #       scale is like: 'LOG10(val)'
    #       graph=True     required to force np.ndarray calculation
    y = applyGraphFormula(vname,    y,     g.GraphScale[vname], info=defname)

    if xunit == "Time":
        fig.autofmt_xdate(rotation = 15)
        #formatter   = mpld.AutoDateFormatter(mpld.AutoDateLocator()) # What for?
        yaxis.xaxis.set_major_formatter(mpld.DateFormatter(xFormatStr))
        ax1.xaxis.set_tick_params(labelsize=8)   # ax1 defines the size of the labels
        # ax2.xaxis.set_tick_params(labelsize=8)  # ax2 appears to be not relevant

        # X-Label positioning: (the label like: Time (First Record: ...)
        # you can move the location of axis labels using set_label_coords.
        # The coords you give it are x and y, and by default the transform
        # is the axes coordinate system: so (0,0) is (left,bottom), (0.5, 0.5)
        # is in the middle, etc.
        #    yaxis.xaxis.set_label_coords(0.5, -0.25)

        # correction of plotstyle:
        psc = plotstyle.copy()                                              # make a copy
        del psc["marker"]                                                   # remove marker
        # print("plotLine: Time plotstyle: markersize", psc["markersize"])
        # print("plotLine: Time plotstyle: marker    ", psc["marker"])      # "marker" is gone

        try:
            line,  = yaxis.plot_date (x, y, fmt=g.markersymbol, **psc)      # add markersymbol to 'fmt'
        except Exception as e:
            exceptPrint(e, defname)
            edprint("t:\n", g.logTime)
            edprint("x:\n", x)
            edprint("y:\n", y)
            line = None

        # print("plotLine: Time plotstyle:", psc)                           # "marker" is gone
        # --> psc: {'color': 'deepskyblue', 'linestyle': 'solid', 'linewidth': 2.0, 'label': '', 'markeredgecolor': 'deepskyblue', 'markersize': 6.123724356957946, 'alpha': 0.9}

    else:
        line,  = yaxis.plot      (x, y, **plotstyle)
        # print("plotLine: auto plotstyle:", plotstyle)                     # "marker" is present
        # --> plotstyle: {'color': 'deepskyblue', 'linestyle': 'solid', 'linewidth': 2.0, 'label': '', 'markeredgecolor': 'deepskyblue', 'marker': 'o', 'markersize': 6.123724356957946, 'alpha': 0.9}

    if drawlegend: yaxis.legend()

    return line


#xyz
def plotLinFit(x, logSlice, scaleFactor, varPlotStyle):
    """Plot a Linear Fit to the selected variable data"""

    defname = "plotLinFit: "

    # return when fit was NOT checked
    if not g.fitChecked: return

    # which is the selected var
    vname   = list(g.VarsCopy)[g.exgg.select.currentIndex()]

    # is the selected var checked? sollte eigentlich nicht passieren können
    if not g.exgg.varDisplayCheckbox[vname].isChecked(): return

    lSM_mask        = np.isfinite(logSlice[vname])          # mask for nan values
    logSliceNoNAN   = logSlice[vname][lSM_mask]             # all NANs removed
    if logSliceNoNAN.size < 3 : return                      # either no data at all, or not enough --> return

    x_NoNAN         = x[lSM_mask]                           # remove all x where data is nan
    xshort          = np.array([x_NoNAN[0], x_NoNAN[-1]])   # for linear fit draw only first and last point
    logSliceMod     = logSliceNoNAN * scaleFactor[vname]

    # print("x_NoNAN: ", x_NoNAN)
    # print("logSliceMod:", logSliceMod)


    try:
        FitSelector = 1                                     # linear fit
        # t0   = time.time()
        polfit = np.polynomial.polynomial.polyfit(x_NoNAN, logSliceMod, FitSelector)    # @1M recs: 39 ms
        # t1   = time.time()
        # rdprint(defname, "#2a polfit: ", polfit, "   type(polfit): ", type(polfit))   # type(polfit): <class 'numpy.ndarray'>

        # testing

        # xshort = np.array([x[0], x[-1]])
        # t2 = time.time()
        yshort = np.polynomial.polynomial.polyval(xshort, polfit)                       # @1M recs:  0.055 ms
        # t3 = time.time()
        # rdprint(defname, "#2c dur: polfit: {:0.3f} ms   polyval: {:0.3f} ms ".format(1000 * (t1 - t0), 1000 * (t3 - t2)))
        # rdprint(defname, "#2d polyval: ", yshort)

        deltatime  = x_NoNAN[-1] - x_NoNAN[0]
        deltavalue = polfit[1] * deltatime
        # rdprint(defname, "#2e Linfit= {}  Delta plot: {:<+6.3g}".format(polfit, deltavalue))

    except Exception as e:
        msg = defname + "fitting: Failure with Exception"
        exceptPrint(e, msg)
        efprint("\nFailure plotting LinFit. Exception: {}".format(e))
        return

    fit_plotstyle                = varPlotStyle[vname].copy()
    fit_plotstyle["linewidth"]   = 2
    fit_plotstyle["markersize"]  = 0

    fit_plotstyle2               = varPlotStyle[vname].copy()
    fit_plotstyle2["linewidth"]  = 5
    fit_plotstyle2["color"]      = "yellow"
    fit_plotstyle2["markersize"] = 0

    fit_plotstyle['label']       = "LinFit: {:0.4g} + {:0.4g} * time  [Delta plot: {:<+6.3g}]".format(polfit[0], polfit[1], deltavalue)


    # t2 = time.time()
    plotLine(xshort, yshort, g.Xunit, vname,                  **fit_plotstyle2)   # make yellow shadow under line; plot first to keep it below line
    plotLine(xshort, yshort, g.Xunit, vname, drawlegend=True, **fit_plotstyle)    # 140 ... 150 ms --> drawing legend has barely any duration impact
    # t3 = time.time()
    # rdprint(defname, "#2f dur: plotLines: {:0.3f} ms   ".format(1000 * (t3 - t2)))



def plotAverage(x, logSlice, scaleFactor, varPlotStyle):
    """Plot the Average and +/- 95% as horizontal lines"""

    if not g.avgChecked: return


    vname     = list(g.VarsCopy)[g.exgg.select.currentIndex()]
    #print("average: vname, g.exgg.varDisplayCheckbox[vname].isChecked():", vname, g.exgg.varDisplayCheckbox[vname].isChecked())
    if g.exgg.varDisplayCheckbox[vname].isChecked():
        avg_Time                     = np.array([x[0], x[-1]])
        #print("plotAverage: avg_Time: ", avg_Time)

        logSliceMod                  = logSlice[vname] * scaleFactor[vname]
        #print("logSliceMod:", logSliceMod)

        avg_avg                      = np.nanmean(logSliceMod)

        if avg_avg >= 0:    avg_std = np.sqrt(avg_avg)  # this is std.dev derived from avg!
        else:               avg_std = g.NAN             # not valid for neg numbers
        #print("---Avg: {}, StdDev of Data: {:6.3f}, SQRT(avg): {:6.3f}".format(avg_avg, np.nanstd (logSliceMod), avg_std))

        # limit 2 sigma: https://en.wikipedia.org/wiki/68%E2%80%9395%E2%80%9399.7_rule
        #                https://en.wikipedia.org/wiki/1.96
        avg_CPMS                     = np.array([avg_avg, avg_avg]) # MUST use np.array!
        avg_plotHiLo = False
        if avg_avg >= 0:
            avg_CPMS_lo              = avg_CPMS - avg_std * 1.96
            avg_CPMS_hi              = avg_CPMS + avg_std * 1.96
            avg_plotHiLo             = (avg_avg - avg_std * 1.96) > 0 # flag to plot 95%

        if vname in ("Temp", "Press", "Humid"): avg_plotHiLo = False # no limits drawn for Temp, Press, Humid

        avg_plotstyle                = varPlotStyle[vname].copy()
        avg_plotstyle["linewidth"]   = 2
        avg_plotstyle["markersize"]  = 0
        avg_plotstyle['label']       = "Avg: {:0.4g}  ".format(avg_avg)

        avg_plotstyle2               = varPlotStyle[vname].copy()
        avg_plotstyle2["linewidth"]  = 5
        avg_plotstyle2["color"]      = "yellow"
        avg_plotstyle2["markersize"] = 0
        avg_plotstyle2['label']       = None

        plotLine(avg_Time, avg_CPMS, g.Xunit, vname, drawlegend=False, **avg_plotstyle2) # make yellow shadow under line
        plotLine(avg_Time, avg_CPMS, g.Xunit, vname, drawlegend=True,  **avg_plotstyle)


        if avg_plotHiLo :
            # plot dashed lin color of var, interrupted by white dots
            # makes it visible on white and on var color
            avg_plotstyle["linestyle"]  = "--"
            avg_plotstyle['label']       = None
            plotLine(avg_Time, avg_CPMS_lo, g.Xunit, vname, drawlegend=False, **avg_plotstyle)
            plotLine(avg_Time, avg_CPMS_hi, g.Xunit, vname, drawlegend=False, **avg_plotstyle)

            avg_plotstyle["color"]      = "white"
            avg_plotstyle["linestyle"]  = ":"
            plotLine(avg_Time, avg_CPMS_lo, g.Xunit, vname, drawlegend=False, **avg_plotstyle)
            plotLine(avg_Time, avg_CPMS_hi, g.Xunit, vname, drawlegend=False, **avg_plotstyle)


def plotMovingAverage(x, logSlice, scaleFactor, varPlotStyle):
    """Plot the Moving Average"""

    # Plot the moving average over with a thin line in the variable's color on a yellow thick line background.
    # Do the average over no more than N/2 data points. Determine N from time delta between first and last
    # record and the number of records.
    # Note: improper with long periods of no data, or changing cycle time!
    # In plot skip the first and last N/2 data points, which are meaningless due to averaging.

    defname = "plotMovingAverage: "

    # is MvAvg checked?
    if not g.mavChecked: return

    # enough data?
    logTimeDelta    = g.logTimeSlice.max() - g.logTimeSlice.min()   # total log time in days
    if logTimeDelta == 0: return                                              # not enough data, return

    # selected variable
    vname           = list(g.VarsCopy)[g.exgg.select.currentIndex()]

    # enough non-NAN data?
    lSM_mask        = np.isfinite(logSlice[vname])      # mask for nan values
    logSliceNoNAN   = logSlice[vname][lSM_mask]         # all NANs removed
    if logSliceNoNAN.size == 0:      return             # no data remaining for vname, return

    # apply scale factor
    logSliceMod     = logSliceNoNAN * scaleFactor[vname]

    # get max/min averaging period
    x_mav           = x[lSM_mask]
    x_mav_size      = x_mav.size                        # no of records
    logTime         = 86400.0 * logTimeDelta            # total log time in sec
    logCycleSec     = logTime / x_mav_size              # average cycle time in sec
    minMvAvgSec     = logCycleSec * 1                   # min sec for MvAvg, -> 1 datapoint
    maxMvAvgSec     = logCycleSec * (x_mav_size / 2)    # max sec for MvAvg, -> half of max datapoints
    # print("x_mav_size {}, logTime {}, logCycleSec {}, minMvAvgSec {}, maxMvAvgSec {}".format(x_mav_size, logTime, logCycleSec, minMvAvgSec, maxMvAvgSec))

    if   g.mav < minMvAvgSec:  mvsecs = minMvAvgSec
    elif g.mav > maxMvAvgSec:  mvsecs = maxMvAvgSec
    else:                           mvsecs = g.mav

    Nmav     = max(1, round(mvsecs / minMvAvgSec))
    newMvAvg = Nmav * logCycleSec
    #dprint("Currently set limit: N={:0.0f} datapoints".format(Nmav))

    try:
        MvAvgEntry = g.exgg.mav.text().replace(",", ".").replace("-", "")
        val = float(MvAvgEntry)  # can value be converted to float?
    except Exception as e:
        MvAvgFail       = True
        if MvAvgEntry > "": # ignore blank entries
            msg = "MvAvg: Enter numeric values >0 for Moving Average period in seconds!"
            exceptPrint(e, defname + msg)
            efprint(msg)

    lower    = int(Nmav/2)
    upper    = int(x_mav_size - (Nmav / 2))
    #dprint("Nmav: {}, lower: {}, upper: {}, delta:: {}".format(Nmav, lower, upper, upper - lower))


    if upper - lower > 2: # needs more than a single record
        if g.exgg.varDisplayCheckbox[vname].isChecked():

            mav_x = x_mav[lower:upper]

            mav_y =   np.convolve(logSliceMod,     np.ones((Nmav,))/Nmav, mode='same')[lower:upper]
            # mav_y = np.convolve(logSliceMod,     np.ones((Nmav,))/Nmav, mode='full')[lower:upper]
            # mav_y = np.convolve(logSliceMod,     np.ones((Nmav,))/Nmav, mode='valid')[lower:upper]

            mav_plotstyle               = varPlotStyle[vname].copy()
            mav_plotstyle['markersize'] = 0

            # draw yellow background
            mav_plotstyle['color']      = 'yellow'
            mav_plotstyle['linewidth']  = 5
            plotLine(mav_x, mav_y, g.Xunit, vname, **mav_plotstyle)

            # draw line in vname color
            mav_plotstyle['color']      = varPlotStyle[vname]['color']
            mav_plotstyle['linewidth']  = 2
            mav_plotstyle['label']      = "MvAvg {:0.4g} sec (N={:0.0f})".format(newMvAvg, Nmav)
            plotLine(mav_x, mav_y, g.Xunit, vname, drawlegend=True, **mav_plotstyle)   # line

    else:
        fprint("ALERT: Not enough data to plot Moving Average")



###############################################################################
# NOT IN USE! so far not working correctly
def updatePlot(filePath, timetag, cpm):
    """updates an existing plot (made by makePlot) with last record"""
    # caution: not active; not tested for current code!!!

    start= time.time()

    # try:
    #     x = g.logTime[0]   # logTime is defined only after 1st plot
    # except:
    #     print("updatePlot, no g.logTimeSlice.size")
    #     return

    # if g.XunitCurrent == "Time":
    #     # plot versus DateTime of day
    #     ptime = mpld.datestr2num(timetag)
    # else:
    #     # Plot vs DiffTime (time since first record)
    #     # XunitCurrent is one of second, minute, hour day
    #     ptime = mpld.datestr2num(timetag) - g.logTime[0]

    # # rescale for X-axis
    # if g.XunitCurrent   == "second":
    #     ptime = ptime * 86400.              # convert to seconds
    # elif g.XunitCurrent == "minute":
    #     ptime = ptime * 1440.               # convert to minutes
    # elif g.XunitCurrent == "hour":
    #     ptime = ptime * 24.                 # convert to hours
    # elif g.XunitCurrent == "day":
    #     pass                                # is in days already
    # else:
    #     pass                                # g.XunitCurrent is "Time"

    # rescale for Y-axis
    if g.Yunit == "CPS":        cpm /= 60.
    #print "ptime:", ptime, "cpm:", cpm
#xxx

    # rdplt.set_xdata(np.append(rdplt.get_xdata(), ptime))
    rdplt.set_xdata(np.append(rdplt.get_xdata(), timetag))
    rdplt.set_ydata(np.append(rdplt.get_ydata(), cpm))

    # g.sizePlotSlice += 1
    g.sizePlotSlice = 111

    subTitle = 'File:' + os.path.basename(filePath) + "  Recs:" + str(g.sizePlotSlice)
    plt.title(subTitle, fontsize=12, fontweight='normal', loc = 'right')

    ax = plt.gca()
    ax.relim()              # recompute the ax.dataLim
    ax.autoscale_view()     # update ax.viewLim using the new dataLim

    #plt.draw()   # seems to be unnecessary

    stop = time.time()
    dprint("updatePlot: update: {:0.1f} ms Total".format( (stop - start) * 1000))

# end of not in use
###############################################################################
