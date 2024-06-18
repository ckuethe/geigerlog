#! /usr/bin/env python3
# -*- coding: UTF-8 -*-

"""
gsup_tools.py - GeigerLog tools

include in programs with:
    include gsup_tools
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

import gsup_sql
# import gsup_gauge # is not used

xt, yt, vline, zero, FitFlag, LogFlag, FitSelector = 0, 0, True, "None", True, False, "1"


def fprintSuSt():
    """Prints an overview of data from all variables"""

    def getTimespanText(timespan):
        """get optimal duration representation"""

        ts = timespan
        if ts > 1 : return "{:10,.2f} d".format(ts)
        ts = ts * 24
        if ts > 1 : return "{:10,.2f} h".format(ts)
        ts = ts * 60
        if ts > 1 : return "{:10,.2f} m".format(ts)
        ts = ts * 60
        return "{:10,.2f} s".format(ts)


    if g.logTimeSlice is None:
        g.exgg.showStatusMessage("No data available")
        return

    timespan_total = (g.logTime[-1]      - g.logTime[0])          # days
    timespan_plot  = (g.logTimeSlice[-1] - g.logTimeSlice[0])     # days
    size_total     = g.logTime.size
    size_plot      = g.logTimeSlice.size
    cycle_total    = "{:10,.1f} s".format((timespan_total * 86400) / (size_total  - 1)) if size_total > 1 else "        NA  "
    cycle_plot     = "{:10,.1f} s".format((timespan_plot  * 86400) / (size_plot   - 1)) if size_plot  > 1 else "        NA  "

    fprint(header("Summary Statistics of Variables selected in Plot"))
    fprint("File       = {}".format(g.currentDBPath))
    if os.path.exists(g.currentDBPath):
        FileSize       = os.path.getsize(g.currentDBPath)
    else:
        efprint(f"File not found! Renamed or deleted?")
        return

    BytesPerRecord = FileSize / size_total if size_total > 0 else g.NAN
    if os.access(g.currentDBPath , os.R_OK):   fprint("Filesize   = {:10,.0f} Bytes".format(FileSize))
    else:                                           fprint("Filesize   = File not found!")
    fprint("Records    = {:10,.0f}   total,{:10,.0f}   shown in Plot, Bytes / Record: {:0.1f} "  .format(size_total, size_plot, BytesPerRecord))
    fprint("Time Span  = {:10s} total,{:10s} shown in Plot"            .format(getTimespanText(timespan_total), getTimespanText(timespan_plot)))
    fprint("Avg. Cycle = {:>10s} total,{:>10s} shown in Plot"          .format(cycle_total,    cycle_plot))

    fprint("")
    fprint("Variable  [Unit]       Avg ±StdDev    ±SDev%  Variance     Min ... Max    Recs    Last")
    # like: Temp    : [°C]      1.435 ±0.788    ±54.9%    0.622 0.77367  5.6682    1775  1.4219

    for vname in g.VarsCopy:
        if vname in g.logSliceMod:                                     # print info only for the vars shown in current plot
            tip, label = getSuStStats(vname, g.logSliceMod[vname])     # shows data as plotted. To see data as recorded hold CTRL button when clicking
            if label > "":  fprint(label)
            else:           fprint("{:8s}: No Data".format(vname))


def getDataForshowStats(logTime, logVar, vname):
    """get the text for the QTextBrowser in showStats"""

    defname = "getDataForshowStats: "

    vnameFull        = g.VarsCopy[vname][0]

    logSize          = logTime.size
    logtime_max      = logTime.max()
    logtime_min      = logTime.min()
    logtime_delta    = logtime_max - logtime_min # in days

    records_nonnan   = np.count_nonzero(~np.isnan(logVar))

    # return when all data are nan
    if np.isnan(logVar).all():
        allnan = "Variable: {}: No Data\n".format(vname)
        return allnan

    logVar_max       = np.nanmax    (logVar)
    logVar_min       = np.nanmin    (logVar)
    logVar_avg       = np.nanmean   (logVar)
    logVar_med       = np.nanmedian (logVar)
    logVar_var       = np.nanvar    (logVar)
    logVar_std       = np.nanstd    (logVar)

    logVar_err       = logVar_std / np.sqrt(logVar.size)
    logVar_sqrt      = np.sqrt(logVar_avg)
    logVar_95        = logVar_std * 1.96   # 95% confidence range

    if vname in ("CPM", "CPM1st", "CPM2nd", "CPM3rd"):
        logVar_text      = "(in units of: {})".format(g.Yunit)

    elif vname in ("CPS",  "CPS1st", "CPS2nd", "CPS3rd"):
        if g.Yunit == "CPM":   unitText = "CPS"
        else:                       unitText = g.Yunit
        logVar_text      = "(in units of: {})".format(unitText)

    else:
        logVar_text      = ""

    ltext = []
    ltext.append("Variable: {} {}\n".format(vnameFull, logVar_text))
    ltext.append(    "  Recs        = {:10,.0f}  Records".format(records_nonnan))

    if   g.Yunit == "CPM" and (vname in ("CPM", "CPM1st", "CPM2nd", "CPM3rd")):
        ltext.append("  Counts      = {:10,.0f}  Counts calculated as: Average CPM * Log-Duration[min]\n".format(logVar_avg * logtime_delta * 24 * 60))

    elif g.Yunit == "CPM" and (vname in ("CPS", "CPS1st", "CPS2nd", "CPS3rd")):
        ltext.append("  Counts      = {:10,.0f}  Counts calculated as: Average CPS * Log-Duration[sec]\n".format(logVar_avg * logtime_delta * 24 * 60 * 60))

    else:
        ltext.append("")

    #~print("----------------vname: ", vname)
    ltext.append(    "                          % of avg")
    ltext.append(    "  Average     = {:8.2f}      100%       Min   ={:8.2f}        Max   ={:8.2f}" .format(logVar_avg,                              logVar_min,          logVar_max)          )
    if logVar_avg != 0:
        ltext.append("  Variance    = {:8.2f} {:8.2f}%"                                          .format(logVar_var,  logVar_var  / logVar_avg * 100))
        ltext.append("  Std.Dev.    = {:8.2f} {:8.2f}%       LoLim ={:8.2f}        HiLim ={:8.2f}" .format(logVar_std,  logVar_std  / logVar_avg * 100,  logVar_avg-logVar_std,         logVar_avg+logVar_std)  )
        ltext.append("  Sqrt(Avg)   = {:8.2f} {:8.2f}%       LoLim ={:8.2f}        HiLim ={:8.2f}" .format(logVar_sqrt, logVar_sqrt / logVar_avg * 100,  logVar_avg-logVar_sqrt,        logVar_avg+logVar_sqrt) )
        ltext.append("  Std.Err.    = {:8.2f} {:8.2f}%       LoLim ={:8.2f}        HiLim ={:8.2f}" .format(logVar_err,  logVar_err  / logVar_avg * 100,  logVar_avg-logVar_err,         logVar_avg+logVar_err) )
        ltext.append("  Median      = {:8.2f} {:8.2f}%       P_5%  ={:8.2f}        P_95% ={:8.2f}" .format(logVar_med,  logVar_med  / logVar_avg * 100,  np.nanpercentile(logVar, 5),   np.nanpercentile(logVar, 95)))
        ltext.append("  95% Conf *) = {:8.2f} {:8.2f}%       LoLim ={:8.2f}        HiLim ={:8.2f}" .format(logVar_95,   logVar_95   / logVar_avg * 100,  logVar_avg-logVar_95,          logVar_avg+logVar_95)   )
    else:
        ltext.append("  Variance    = {:8.2f}  {:>8s}"                                           .format(logVar_var,  "N.A."))
        ltext.append("  Std.Dev.    = {:8.2f}  {:>8s}       LoLim ={:8.2f}        HiLim ={:8.2f}"  .format(logVar_std,  "N.A."                        ,  logVar_avg-logVar_std,         logVar_avg+logVar_std)  )
        ltext.append("  Sqrt(Avg)   = {:8.2f}  {:>8s}       LoLim ={:8.2f}        HiLim ={:8.2f}"  .format(logVar_sqrt, "N.A."                        ,  logVar_avg-logVar_sqrt,        logVar_avg+logVar_sqrt) )
        ltext.append("  Std.Err.    = {:8.2f}  {:>8s}       LoLim ={:8.2f}        HiLim ={:8.2f}"  .format(logVar_err,  "N.A."                        ,  logVar_avg-logVar_err,         logVar_avg+logVar_err) )
        ltext.append("  Median      = {:8.2f}  {:>8s}       P_5%  ={:8.2f}        P_95% ={:8.2f}"  .format(logVar_med,  "N.A."                        ,  np.nanpercentile(logVar, 5),   np.nanpercentile(logVar, 95)))
        ltext.append("  95% Conf *) = {:8.2f}  {:>8s}       LoLim ={:8.2f}        HiLim ={:8.2f}"  .format(logVar_95,   "N.A."                        ,  logVar_avg-logVar_95,          logVar_avg+logVar_95)   )

    return "\n".join(ltext)


def showStats():
    """Printing statistics - will always show only data in current plot"""

    defname = "showStats: "

    logTimeTotal     = g.logTime           # time data
    logTime          = g.logTimeSlice      # time data

    if g.logTime is None:
        g.exgg.showStatusMessage("No data available") # when called without a loaded file
        return

    setBusyCursor()

    logSize          = logTime.size
    logSizeTotal     = logTimeTotal.size

    filesize         = os.path.getsize(g.currentDBPath)
    bpr              = filesize / logSizeTotal if logSizeTotal > 0 else g.NAN

    logtime_size     = logTime.size
    logtime_max      = logTime.max()
    logtime_min      = logTime.min()
    logtime_delta    = logtime_max - logtime_min # in days

    oldest   = (str(mpld.num2date(logtime_min)))[:19]
    youngest = (str(mpld.num2date(logtime_max)))[:19]

    lstats   = QTextBrowser()      # label to hold the description
    lstats.setLineWrapMode(QTextEdit.NoWrap)
    lstats.setTextInteractionFlags(Qt.LinksAccessibleByMouse|Qt.TextSelectableByMouse)

    lstats.append("Data from file: {}\n".format(g.currentDBPath))
    lstats.append("Totals")
    lstats.append("  Filesize      = {:12,.0f} Bytes".format(filesize))
    lstats.append("  Records       = {:12,.0f} Total, {:0,.0f} shown in Plot   Bytes per Record: {:0.1f}".format(logSizeTotal, logSize, bpr))
    lstats.append("")
    lstats.append("Legend:   *): Approximately valid for a Poisson Distribution when Average > 10")
    lstats.append("NOTE:     Requirement for Poisson: Average = Variance")
    lstats.append("="*100)

    lstats.append("Time")
    lstats.append("  Oldest rec    = {}  (time = {:.3f} d)".format(oldest,   0))
    lstats.append("  Youngest rec  = {}  (time = {:.3f} d)".format(youngest, logtime_max - logtime_min))
    lstats.append("  Duration      = {:.1f} s   = {:.1f} m   = {:.1f} h   = {:.1f} d".format(logtime_delta *86400, logtime_delta*1440, logtime_delta *24, logtime_delta))
    lstats.append("  Cycle average = {:0.2f} s".format(logtime_delta *86400/ (logSize -1)))
    lstats.append("="*100)

    for i, vname in enumerate(g.VarsCopy):
        if g.varsSetForCurrent[vname]:
            try:
                if vname in g.logSliceMod:         # else the var had not been checked for the plot
                    rdprint(defname, "g.useGraphScaledData: ", g.useGraphScaledData)
                    # if   g.useGraphScaledData:  logVar = applyValueFormula(vname, g.logSliceMod[vname], g.GraphScale[vname], info=defname)
                    if   g.useGraphScaledData:  logVar = applyGraphFormula(vname, g.logSliceMod[vname], g.GraphScale[vname], info=defname)
                    else:                       logVar = g.logSliceMod[vname]
                    # logVar = g.logSliceMod[vname]  # var data

                    getlstatstext =  getDataForshowStats(logTime, logVar, vname)
                    lstats.append("")
                    lstats.append(getlstatstext)
                    lstats.append("="*100)
            except Exception as e:
                exceptPrint(e, "")

    lstats.append("First and last few records:\n")
    sql, ruler = gsup_sql.getShowCompactDataSql(g.varsSetForCurrent)
    lstats.append(ruler)
    lstats.append(g.exgg.getExcerptLines(sql, g.currentConn, lmax=10))
    lstats.append(ruler)

    lstats.moveCursor(QTextCursor.Start)

    d = QDialog()
    d.setWindowIcon(g.iconGeigerLog)
    d.setFont(g.fontstd)
    d.setWindowTitle("Statistics on Checked Variables")
    d.setWindowModality(Qt.WindowModal)
    d.setMinimumWidth(1100)
    d.setMinimumHeight(750)

    bbox    = QDialogButtonBox()
    bbox.setStandardButtons(QDialogButtonBox.Ok)
    bbox.accepted.connect(lambda: d.done(0))

    layoutV = QVBoxLayout(d)
    layoutV.addWidget(lstats)
    layoutV.addWidget(bbox)

    setNormalCursor()

    d.exec()


def selectScatterPlotVars():
    """Selecting the vars for the scatter plot and display and fit options"""

    global xt, yt, vline, zero, FitFlag, LogFlag, FitSelector # to keep the selectios

    defname = "selectScatterPlotVars: "

    if g.logTime is None:              # when called without a loaded file
        g.exgg.showStatusMessage("No data available")
        return

    # check for at least 1 variable data point
    # cdprint(defname, "g.varsSetForCurrent", g.varsSetForCurrent, " len:", len(g.varsSetForCurrent))
    if not True in g.varsSetForCurrent.values():
        g.exgg.showStatusMessage("No value data available")
        return

    # X-axis and Y-axis vars
    xlist = QListWidget()
    xlist.setSelectionMode(QAbstractItemView.SingleSelection)
    xlist.addItem("time")
    ylist = QListWidget()
    ylist.setSelectionMode(QAbstractItemView.SingleSelection)
    ylist.addItem("time")
    for i, vname in enumerate(g.VarsCopy):
        if g.varsSetForCurrent[vname]:
            #~print("g.varsSetForCurrent[vname]: ", vname,  g.varsSetForCurrent[vname])
            xlist.addItem(vname)
            ylist.addItem(vname)

    if xt == 0:
        xlist.setCurrentRow(0)
        ylist.setCurrentRow(0)
    else:
        for i in range(len(xlist)):
            if xlist.item(i).text() == xt: xlist.setCurrentRow(i)
            if ylist.item(i).text() == yt: ylist.setCurrentRow(i)

    # force origin to zero?
    originB0 = QRadioButton("Show Optimal")             # this is default
    originB1 = QRadioButton("Show X=0")
    originB2 = QRadioButton("Show Y=0")
    originB3 = QRadioButton("Show X,Y=0")

    # if   zero == "None"      : originB0.setChecked(True)
    # elif zero == "x"         : originB1.setChecked(True)
    if   zero == "x"         : originB1.setChecked(True)
    elif zero == "y"         : originB2.setChecked(True)
    elif zero == "x and y"   : originB3.setChecked(True)
    else                     : originB0.setChecked(True)    # default

    # draw connecting lines?
    checkbConnLine  = QCheckBox("Connecting Line")      # default is yes
    checkbConnLine.setChecked(vline)

    layoutLine1 = QHBoxLayout()
    layoutLine1.addWidget(originB3)
    layoutLine1.addWidget(originB1)
    layoutLine1.addWidget(originB2)
    layoutLine1.addWidget(originB0)
    layoutLine1.addStretch()
    layoutLine1.addWidget(checkbConnLine)

    # add polynomial fit?                         default is yes
    checkPolFit = QCheckBox("Show Fit using method/degree of polynomial:")
    checkPolFit.setChecked(FitFlag)

    # selector for order of fit                   default is 1st order = linear
    comboboxFitType = QComboBox()
    comboboxFitType.addItems(["EXP_trf", "EXP_dog", "EXP_lm", "Prop", "0", "1", "2", "3", "4", "5", "6", "7"])
    comboboxFitType.setMaximumWidth(80)
    comboboxFitType.setToolTip('Select method of fit or degree of polynomial fit')

    # FitSelector choice
    if   FitSelector == "EXP_trf":   comboboxFitType.setCurrentIndex(0)
    elif FitSelector == "EXP_dog":   comboboxFitType.setCurrentIndex(1)
    elif FitSelector == "EXP_lm":    comboboxFitType.setCurrentIndex(2)
    elif FitSelector == "Prop":      comboboxFitType.setCurrentIndex(3)
    else:                            comboboxFitType.setCurrentIndex(int(FitSelector) + 4)

    # select Log Scale for Y?
    checkLogLin = QCheckBox("Log Scale for Y-Axis")
    checkLogLin.setChecked(LogFlag)

    layoutLine2 = QHBoxLayout()
    layoutLine2.addWidget(checkLogLin)
    layoutLine2.addStretch()
    layoutLine2.addWidget(checkPolFit)
    layoutLine2.addWidget(comboboxFitType)

    # bbox = QDialogButtonBox()
    # bbox.setStandardButtons(QDialogButtonBox.Cancel | QDialogButtonBox.Ok )
    # bbox.accepted.connect(lambda: d.done(100)) # ESC key produces 0 (zero)!
    # # bbox.rejected.connect(lambda: d.done(-1))
    # bbox.rejected.connect(lambda: d.done(0))

    okButton = QPushButton("OK")
    okButton.setAutoDefault(True)
    okButton.clicked.connect(lambda:  d.done(0))

    selectButton = QPushButton("Plot")
    selectButton.setStyleSheet("QPushButton {font:bold; font-size:12px;}")
    selectButton.setAutoDefault(False)
    selectButton.clicked.connect(lambda:  d.done(100))

    bbox = QDialogButtonBox()
    bbox.addButton(selectButton,  QDialogButtonBox.ActionRole)
    bbox.addButton(okButton,      QDialogButtonBox.ActionRole)


    layoutHeader = QHBoxLayout()
    layoutHeader.addWidget(QLabel("X"))
    layoutHeader.addWidget(QLabel("Y"))

    layoutList = QHBoxLayout()
    layoutList.addWidget(xlist)
    layoutList.addWidget(ylist)

    d = QDialog()
    d.setWindowIcon(g.iconGeigerLog)
    d.setFont(g.fontstd)
    d.setWindowTitle("Select Variables for Scatter Plot")
    d.setMinimumHeight(400)
    d.setMinimumWidth(600)
    #d.setStyleSheet("QLabel { background-color:#DFDEDD; color:rgb(40,40,40); font-size:30px; font-weight:bold;}")

    d.setWindowModality(Qt.WindowModal)       # default alles andere kann bedient werden
    # d.setWindowModality(Qt.NonModal)          #         alles andere blockiert
    # d.setWindowModality(Qt.ApplicationModal)  #         alles andere blockiert
    # nothing set                               #         alles andere blockiert
    # d.setModal(False)                         #         alles andere blockiert!
    # d.setModal(True)                          #         alles andere blockiert

    layoutV = QVBoxLayout(d)
    layoutV.addLayout(layoutHeader)
    layoutV.addLayout(layoutList)
    layoutV.addLayout(layoutLine1)
    layoutV.addLayout(layoutLine2)
    layoutV.addWidget(bbox)

    retval = d.exec()
    #print("reval:", retval)

    if retval == 100:             # ESC key produces 0
        #~print("xlist.currentItem(): ", xlist.currentItem().text())
        #~print("ylist.currentItem(): ", ylist.currentItem().text())
        xt          = xlist.currentItem().text()
        yt          = ylist.currentItem().text()
        vline       = checkbConnLine.isChecked()
        FitFlag     = checkPolFit.isChecked()
        FitSelector = comboboxFitType.currentText()
        LogFlag     = checkLogLin.isChecked()

        if   originB0.isChecked(): zero = "None"
        elif originB1.isChecked(): zero = "x"
        elif originB2.isChecked(): zero = "y"
        elif originB3.isChecked(): zero = "x and y"
        else                     : zero = "None"

        plotScatter(xt, yt, vline, zero, FitFlag, LogFlag, FitSelector)

#yyy
def plotScatter(vx, vy, vline, zero, FitFlag, LogFlag, FitSelector):
    """Plotting a Scatter plot"""

    defname = "plotScatter: "
    vprint(defname, "x:{}, y:{}, vline:{}, zero:{}, FitFlag:{}, LogFlag:{}, FitSelector:{}".format(vx, vy, vline, zero, FitFlag, LogFlag, FitSelector))
    setIndent(1)

    setBusyCursor()

    # Plotstyle
    plotstyle        = {'color'             : 'black',
                        'linestyle'         : 'solid' if vline else 'none',
                        'linewidth'         : '0.5',
                        'label'             : 'testlabel',
                        'markeredgecolor'   : 'black',
                        'marker'            : 'o',
                        'markersize'        : '60',
                        'alpha'             : 1,
                        }

    if g.currentDBPath is None: DataSrc = "No Data source!"
    else:                       DataSrc = os.path.basename(g.currentDBPath)

    localvardict = g.VarsCopy.copy()
    localvardict.update( {'time' : ('time [d]', 'time') } )

    # print("g.logTimeDiffSlice: ", g.logTimeDiffSlice)
    # print("g.logSlice: ", g.logSlice)
    # print("vx: ", vx)
    vprint(defname, "g.useGraphScaledData: ", g.useGraphScaledData)

    if vx == "time":
        x0 = g.logTimeDiffSlice
    else:
        try:
            # if   g.useGraphScaledData:  x0 = applyValueFormula(vy, g.logSlice[vx], g.GraphScale[vx], info=defname)
            if   g.useGraphScaledData:  x0 = applyGraphFormula(vy, g.logSlice[vx], g.GraphScale[vx], info=defname)
            else:                       x0 = g.logSlice[vx]

        except Exception as e:
            fprint(header("Plot Scatter X"))
            fprint("ERROR in plotScatter: Exception: ", e)
            setIndent(0)
            setNormalCursor()
            return

    # print("vy: ", vy)
    if vy == "time":
        y0 = g.logTimeDiffSlice
    else:
        try:
            # if   g.useGraphScaledData:  y0 = applyValueFormula(vy, g.logSlice[vy], g.GraphScale[vy], info=defname)
            if   g.useGraphScaledData:  y0 = applyGraphFormula(vy, g.logSlice[vy], g.GraphScale[vy], info=defname)
            else:                       y0 = g.logSlice[vy]

        except Exception as e:
            fprint(header("Plot Scatter Y"))
            fprint("ERROR in plotScatter: Exception: ", e)
            setIndent(0)
            setNormalCursor()
            return

    # clean the data from nan:
    # - first clean all data pairs where y is nan
    ymask                   = np.isfinite(y0)      # mask for nan values in y
    y1                      = y0[ymask]
    x1                      = x0[ymask]

    # - second clean all remaining data pairs where x is nan
    xmask                   = np.isfinite(x1)      # mask for nan values in x
    ydata                   = y1[xmask]
    xdata                   = x1[xmask]
    # mdprint("xdata: \n", xdata)
    # mdprint("ydata: \n", ydata)
    # mdprint("xmask: \n", xmask)
    # mdprint("sizes: x: {} type:{}  type:{}  y: {} type:{}  type:{}  ".format(xdata.size, type(xdata), type(xdata[0]), ydata.size, type(ydata), type(ydata[0])))

    if xdata.size == 0 or ydata.size == 0:
        vprint("plotScatter: no data in either x or y: x:\n", xdata, "\ny:\n", ydata)
        fprint(header("Scatter Plot"))
        if xdata.size == 0: qefprint("Error:   No data in x")
        if ydata.size == 0: qefprint("Error:   No data in y")
        burp()
        setIndent(0)
        setNormalCursor()
        return

    plotstyle['markersize'] = float(plotstyle['markersize']) / np.sqrt(ydata.size)

    # make the figure
    fig2 = plt.figure(facecolor = "#E7F9C9", dpi=g.hidpiScaleMPL)
    g.plotScatterFigNo = plt.gcf().number
    mdprint("plotScatter: open figs count: {}, current fig: #{}".format(len(plt.get_fignums()), plt.gcf().number))

    plt.title("Scatter Plot\n", fontsize=12, loc='center')
    subTitleLeft  = DataSrc
    subTitleRight = "Recs:" + str(len(xdata))
    plt.title(subTitleLeft,  fontsize=10, fontweight='normal', loc = 'left')
    plt.title(subTitleRight, fontsize=10, fontweight='normal', loc = 'right')

    plt.xlabel("x = " + localvardict[vx][0], fontsize=12)
    if LogFlag:  plt.ylabel("y = ln (" + localvardict[vy][0] + ")", fontsize=12)
    else:        plt.ylabel("y = "     + localvardict[vy][0]      , fontsize=12)

    plt.grid(True)
    plt.subplots_adjust(hspace=None, wspace=.2 , left=.15, top=0.90, bottom=0.1, right=.97)
    plt.ticklabel_format(useOffset=False)

    # show the cursor x, y position in the Nav toolbar
    ax1 = plt.gca()
    ax1.format_coord = lambda x,y: "x={:.1f}, y={:.1f}".format(x, y)    # to hide use: lambda x, y: ""

    d = QDialog()
    g.plotScatterPointer = d
    d.setWindowIcon(g.iconGeigerLog)
    d.setWindowTitle("Scatter Plot")
    d.setWindowModality(Qt.WindowModal)          # multiple windows open, all runs, all is clickable

    # canvas - this is the Canvas Widget that displays the `fig2`
    # it takes the `figure` instance as a parameter to __init__
    canvas2 = FigureCanvas(fig2)
    canvas2.setFixedSize(700, 600)
    navtoolbar = NavigationToolbar(canvas2, g.exgg)

    labout  = QTextBrowser() # label to hold the description
    labout.setFont(g.fontstd)
    labout.setMinimumHeight(250)

    if LogFlag:
        labout.append("\n<span style='font-weight:bold; font-size:20px;'>Y-Axis in Logarithmic Scale.</span>")
        labout.setText("Scatter Plot of y = ln({}) versus x = {}.".format(localvardict[vy][0], localvardict[vx][0]))
    else:
        # labout.setText("Scatter Plot of y = {} versus x = {}.".format(localvardict[vy][0], localvardict[vx][0]))
        labout.setText("<b>Scatter Plot: </b> y = {} versus x = {}.".format(localvardict[vy][0], localvardict[vx][0]))

    txtlines  = "Connecting lines are {}drawn".format("" if vline else "not ")
    txtorigin = "an origin of zero is enforced for {}".format(zero)
    labout.append("{}; {}.".format(txtlines, txtorigin))

    okButton = QPushButton("OK")
    okButton.setAutoDefault(True)
    okButton.clicked.connect(lambda:  d.done(0))

    selectButton = QPushButton("Select")
    selectButton.setStyleSheet("QPushButton {font:bold;}")
    selectButton.setAutoDefault(False)
    selectButton.clicked.connect(lambda:  nextScatterPlot())

    bbox = QDialogButtonBox()
    bbox.addButton(selectButton,  QDialogButtonBox.ActionRole)
    bbox.addButton(okButton,      QDialogButtonBox.ActionRole)

    layoutV = QVBoxLayout(d)
    layoutV.addWidget(navtoolbar)
    layoutV.addWidget(canvas2)
    layoutV.addWidget(bbox)
    layoutV.addWidget(labout)

    ##############################################

    # in numpy 'log' is the NATURAL logarithm 'ln'!
    ln = np.log

    # get R-squared
    def appendRsquared(ydata, ymodel):
        """Calculate r-squared based on ydata and ymodel"""

        ss_res = np.sum((ydata - ymodel)         ** 2)  # residual sum of squares to mmodel
        ss_tot = np.sum((ydata - np.mean(ydata)) ** 2)  # total sum of squares to average
        r2 = 1 - (ss_res / ss_tot)                      # r-squared

        labout.append(" R² : {:0.3f} ".format(r2))
        labout.append("")

        mdprint(defname, "ss_res: ", ss_res, "  ss_tot: ", ss_tot, "  R2: ", r2)

    ##################################################

    # mdprint(defname, "x: size:{} type:{} {}  y: size:{} type:{} {}".format(xdata.size, type(xdata), type(xdata[0]), ydata.size, type(ydata), type(ydata[0])))
    # mdprint(defname, "x first 6: ",      str(xdata[:6]) .replace("\n", " "))
    # mdprint(defname, "y first 6: ",      str(ydata[:6]) .replace("\n", " "))
    # mdprint(defname, "x last  6: ",      str(xdata[-6:]).replace("\n", " "))
    # mdprint(defname, "y last  6: ",      str(ydata[-6:]).replace("\n", " "))
    # mdprint(defname, "FitSelector: ", FitSelector)

    if LogFlag: plt.plot(xdata, ln(ydata), **plotstyle)
    else:       plt.plot(xdata, ydata,     **plotstyle)

    # set the origin (must do AFTER plot, or xlim ylim is not available)
    if   "x" in zero: plt.xlim(left   = 0)
    if   "y" in zero: plt.ylim(bottom = 0)

    if FitFlag:
        if FitSelector in ["0", "1", "2", "3", "4", "5", "6", "7"]:
            lcoeff      = ["a", "b", "c", "d", "e", "f", "g", "h"]
            pdeg        = int(FitSelector)

            labout.append("\nCoefficients of a Least-Squares-Regression Fit with a <b>Polynome of degree {}:</b>".format(pdeg))
            labout.append("<span style='font-weight:bold; font-size:20px;'>y = a + b * x + c * x² + d * x³ + ... </span><br>")

            try:
                pcoeffs, stats = np.polynomial.polynomial.polyfit(xdata, ydata, pdeg, full=True)
                mdprint(defname, "Fit result: coeffs: ", str(pcoeffs).replace("\n", " "))
                # mdprint(defname, "Fit result: stats: ",  stats)                         # stats[0] (=residuals) == ss_res !

                pFon = np.polynomial.polynomial.Polynomial(pcoeffs)

                for i, pcf in enumerate(pcoeffs):
                    labout.append("({:d}) : {:s} = {: .6g}".format(i, lcoeff[i], pcf))

                appendRsquared(ydata, pFon(xdata))

                xplotdata = np.sort(xdata)
                if LogFlag: plt.plot(xplotdata, ln(pFon(xplotdata)), color="red", marker=None, linestyle="solid", linewidth=2)
                else:       plt.plot(xplotdata,    pFon(xplotdata),  color="red", marker=None, linestyle="solid", linewidth=2)

            except Exception as e:
                exceptPrint(e, defname)
                labout.append("\nFailure to plot. Exception: {}".format(e))
                burp()


        elif FitSelector == "Prop":
            ###################
            def func(x, a):
                return a * x
            ###################

            labout.append("\nCoefficient of a Least-Squares-Regression Fit with a <b>Proportional Constant:</b>")
            labout.append("<span style='font-weight:bold; font-size:20px;'>y = b * x </span><br>")

            try:
                popt, pcov = scipy.optimize.curve_fit(func, xdata, ydata)

                # rdprint(defname, "curve_fit: popt: ", popt)
                # rdprint(defname, "curve_fit: pcov: ", str(pcov).replace("\n", ""))  # made string to keep all 4 values on single line
                # rdprint(defname, "curve_fit: perr: ", np.sqrt(np.diag(pcov)))

                labout.append("({:d}) : {:s} = {: .6g}".format(1, "b", popt[0]))

                appendRsquared(ydata, func(xdata, *popt))

                xplotdata = np.sort(xdata)
                if LogFlag: plt.plot(xplotdata, ln(func(xplotdata, *popt)), color="red", marker=None, linestyle="solid", linewidth=2)
                else:       plt.plot(xplotdata,    func(xplotdata, *popt),  color="red", marker=None, linestyle="solid", linewidth=2)

            except Exception as e:
                exceptPrint(e, defname + "Fitselector = Prop")
                labout.append("\nFailure to plot. Exception: {}".format(e))
                burp()


        elif FitSelector in ("EXP_trf", "EXP_dog", "EXP_lm"):
            #########################################
            def func(x, a, b, c):
                return a * np.exp(-ln(2) / b * x) + c
            #########################################

            labout.append("\nCoefficients of a Least-Squares-Regression Fit using <b>method: '{}'</b>".format(FitSelector))
            labout.append("<span style='font-weight:bold; font-size:20px;'>y = a * exp( -ln(2) / b * x ) + c</span><br>")

            try:
                if   FitSelector == "EXP_trf":  popt, pcov = scipy.optimize.curve_fit(func, xdata, ydata, method='trf',    bounds=([0, 0, -np.inf], [np.inf, np.inf, np.inf]))
                elif FitSelector == "EXP_dog":  popt, pcov = scipy.optimize.curve_fit(func, xdata, ydata, method='dogbox', bounds=([0, 0, -np.inf], [np.inf, np.inf, np.inf]))
                elif FitSelector == "EXP_lm":   popt, pcov = scipy.optimize.curve_fit(func, xdata, ydata, method='lm')     # no bounds allowed

                # rdprint(defname, "curve_fit: popt: ", popt)
                # rdprint(defname, "curve_fit: pcov: ", str(pcov).replace("\n", ""))  # made string to keep all 4 values on single line
                # rdprint(defname, "curve_fit: perr: ", np.sqrt(np.diag(pcov)))

                labout.append("(0) : a = {}".format(customformat(popt[0], 10, 4, thousand=True)))
                labout.append("(1) : b = {}".format(customformat(popt[1], 10, 4, thousand=True)))
                labout.append("(2) : c = {}".format(customformat(popt[2], 10, 4, thousand=True)))

                appendRsquared(ydata, func(xdata, *popt))

                strtauday  = customformat(popt[1]          , 10, 4, thousand=True)
                strtauhour = customformat(popt[1] * 24     , 10, 4, thousand=True)
                strtaumin  = customformat(popt[1] * 24 * 60, 10, 4, thousand=True)
                labout.append("<span style='font-weight:bold; font-size:20px;'>Half-life: {} days = {} hours = {} min</span>".format(strtauday, strtauhour, strtaumin))
                labout.append("Half-life References: Iodine-131: 8.0197 days, Radon-222: 3.824 days")

                xplotdata = np.sort(xdata)
                if LogFlag: plt.plot(xplotdata, ln(func(xplotdata, *popt)), color="red", marker=None, linestyle="solid", linewidth=2)
                else:       plt.plot(xplotdata,    func(xplotdata, *popt),  color="red", marker=None, linestyle="solid", linewidth=2)

            except Exception as e:
                exceptPrint(e, defname + "Fitselector = EXPonential curve_fit: {}".format(FitSelector))
                labout.append("\nFailure getting a curve fit for FitSelector: '{}'".format(FitSelector))
                labout.append("\nException: '{}'".format(e))
                burp()

        else:
            # undefined FitSelector
            printProgError(defname, "Undefined 'FitSelector' was used")

    # show window
    fig2.canvas.draw_idle() # scheint nicht notwendig zu sein

    setNormalCursor()

    d.exec()
    # plt.close(g.plotScatterFigNo)

    setIndent(0)


def nextScatterPlot():
    """closes the dialog and reopens the var selection """

    #print("nextScatterPlot: ")
    g.plotScatterPointer.close()   # closes the dialog
    plt.close(g.plotScatterFigNo)  # closes the figure
    selectScatterPlotVars()


class DispWinDialog(QDialog):
    """Dialog to allow checking events"""

    def __init__(self, parent=None):
        super(DispWinDialog, self).__init__(parent)

        # when you want to destroy the dialog set this to True
        self._want_to_close = False


    def resizeEvent(self, event):
        """the window was resized and may have been moved"""

        defname = "resizeEvent: "

        # rdprint(defname, "event: ", event)

        g.SettingsNeedSaving = True


    def reShow(self):
        # self.showMinimized()
        self.setWindowState(self.windowState() and (not Qt.WindowMinimized or Qt.WindowActive))


    # def closeEvent(self, evnt):
    #     if self._want_to_close:
    #         super(DispWinDialog, self).closeEvent(evnt)
    #     else:
    #         evnt.ignore()
    #         self.setWindowState(QtCore.Qt.WindowMinimized)


def displayLastValuesWindow():
    """
    This makes the Window structure for the last values and Graph values.
    It does NOT fill-in the data!
    """

    # For updating see updateDisplayLastValuesWindow() in file ggeiger
    # the data structure is created in ggeiger as vlabels and svlabels
    # see approx line 85

    # start = time.time()

    defname = "displayLastValuesWindow: "

    if g.displayLastValsIsOn:              # already showing in the back; bring to front
        g.dispLastValsWinPtr.reShow()
        return

    if g.logConn    is None:               # no database
        msg = "No data available"
        g.exgg.showStatusMessage(msg, timing=0, error=True)
        return

    g.displayLastValsIsOn = True

    d = DispWinDialog()
    d.setWindowIcon(g.iconGeigerLog)
    d.setWindowTitle("Display Last Values")
    d.setWindowModality(Qt.WindowModal)     # can click everywhere
    d.setMinimumWidth(540)
    d.setStyleSheet("QLabel {background-color:#DFDEDD; color:rgb(80,80,80);}")

    if g.displayLastValsGeom[0] != "":
        # rdprint(defname, "g.displayLastValsGeom: ", g.displayLastValsGeom)
        x, y, w, h = g.displayLastValsGeom                      # all values are STRINGS
        d.setGeometry(int(x), int(y), int(w), int(h))
    else:
        mdprint(defname, "Ooooops g.displayLastValsGeom[0] is empty")

    g.dispLastValsWinPtr = d    # pointer to this dialog window

    bbox = QDialogButtonBox()
    bbox.setStandardButtons(QDialogButtonBox.Ok)
    bbox.accepted.connect(lambda: d.done(0))

    gridlo = QGridLayout()
    gridlo.setVerticalSpacing(10) # more than default, 5 is about normal?

    layoutV = QVBoxLayout(d)
    layoutV.addLayout(gridlo)
    layoutV.addWidget(bbox)

    # widthValCol = 134
    widthValCol = 120

    t1 = QLabel("Variable")
    t1.setStyleSheet("QLabel {color: #111111; font-size:18px; font-weight:bold;}")

    t2 = QLabel("Device")
    t2.setStyleSheet("QLabel {color: #111111; font-size:18px; font-weight:bold; qproperty-alignment:AlignCenter;}")

    t5 = QLabel("Comment")
    t5.setStyleSheet("QLabel {color: #111111; font-size:18px; font-weight:bold; qproperty-alignment:AlignCenter;}")

    t3 = QLabel("Value")
    t3.setStyleSheet("QLabel {color: #111111; font-size:18px; font-weight:bold; qproperty-alignment:AlignCenter;}")
    t3.setMinimumWidth(widthValCol)
    # t3.setMaximumWidth(widthValCol)

    t4 = QLabel("Graph")
    t4.setStyleSheet("QLabel {color: #111111; font-size:18px; font-weight:bold; qproperty-alignment:AlignCenter;}")
    t4.setMinimumWidth(widthValCol)
    # t4.setMaximumWidth(widthValCol)

    gridlo.addWidget(t1,    0, 0)
    gridlo.addWidget(t2,    0, 1)
    gridlo.addWidget(t5,    0, 2)
    gridlo.addWidget(t3,    0, 3)
    gridlo.addWidget(t4,    0, 4)
    # gridlo.setColumnStretch(3, 1) # give more space to value col
    # gridlo.setColumnStretch(4, 1) # give more space to Graph col

    # reset labels
    g.exgg.vlabels  = {}
    g.exgg.svlabels = {}
    for vname in g.VarsCopy:
        # setup orig values
        g.exgg.vlabels[vname] = QLabel()
        g.exgg.vlabels[vname].setAlignment(Qt.AlignRight)
        g.exgg.vlabels[vname].setFont(QFont("Monospace", 16, weight=QFont.Black))
        # g.exgg.vlabels[vname].setMinimumWidth(widthValCol)

        # setup Graph values
        g.exgg.svlabels[vname] = QLabel()
        g.exgg.svlabels[vname].setAlignment(Qt.AlignRight)
        g.exgg.svlabels[vname].setFont(QFont("Monospace", 16, weight=QFont.Black))
        # g.exgg.svlabels[vname].setMinimumWidth(widthValCol)

    #
    # setup  table
    #
    lenvn       = len(g.VarsCopy)
    vlabels     = [None] * lenvn   # variable names
    dlabels     = [None] * lenvn   # device names
    clabels     = [None] * lenvn   # custom names

    for i, vname in enumerate(g.VarsCopy):
        #print("---i, vname:", i, vname)

        # set the var name
        vlabels[i] = QLabel(vname)
        vlabels[i].setFont((QFont("Sans", 12, weight=QFont.Bold)))

        # set the device name if it supports this variable
        dlabels[i] = QLabel()
        dlabels[i].setAlignment(Qt.AlignCenter)
        dlabels[i].setStyleSheet("QLabel {color:#111; font-size:14px; font-weight:bold;}")
        for dname in g.Devices:
            #print("dname:", dname, ", vname:", vname)
            if g.Devices[dname][1] is None: continue                   # no vars defined
            if vname in g.Devices[dname][1]:
                dlabels[i].setText(dname) # this var is defined

        # set the custom var name
        cvname = g.VarsCopy[vname][6]
        clabels[i] = QLabel(cvname)
        clabels[i].setStyleSheet("QLabel {color:#111; font-size:14px; font-weight:normal;}")

        gridlo.addWidget(vlabels[i],                i + 1, 0)   # variable
        gridlo.addWidget(dlabels[i],                i + 1, 1)   # device
        gridlo.addWidget(clabels[i],                i + 1, 2)   # comment
        gridlo.addWidget(g.exgg.vlabels[vname],     i + 1, 3)   # value
        gridlo.addWidget(g.exgg.svlabels[vname],    i + 1, 4)   # graph value

    # set the values and scaled values
    g.needDisplayUpdate = True

    ### testing - switchinbg it off
    # g.exgg.runCheckCycle()

    # takes 10 ... 20 ms
    # duration = (time.time() - start) * 1000
    # cdprint(defname + "duration: {:0.3f} ms".format(duration))

    g.SettingsNeedSaving = True

    d.exec()    # blocks until Ok button pushed

    g.displayLastValsIsOn = False
    g.dispLastValsWinPtr  = None


def fprintPlotData():
    """Print Plot Data to Notepad. Data are taken from the plot, not from the database!"""

    defname = "fprintPlotData: "

    t0 = g.logTimeSlice

    if t0 is None or len(t0) == 0:
        g.exgg.showStatusMessage("No data available")
        return

    fprint(header("Print Plot-Data"))
    setBusyCursor()

    dataheader = "{:6s}, {:19s}".format("#Index", "DateTime")
    for vname in g.VarsCopy:
        if g.exgg.varDisplayCheckbox[vname].isChecked():
            dataheader += ",{:>8s}".format(vname)
    fprint(dataheader)
    QtUpdate()

    printstring    = ""
    printlinecount = 0
    printlineMax   = 20

    for i in range(len(t0)):
        vcc = "{:>6d}, {:<19s}".format(i, str(mpld.num2date(t0[i]))[:19])   # Index, DateTime
        NonNANCount = 0

        for vi, vname in enumerate(g.VarsCopy):
            if g.exgg.varDisplayCheckbox[vname].isChecked():
                varvalue = g.logSlice[vname][i]

                if not np.isnan(varvalue):
                    NonNANCount += 1
                    if  vi < 8 and (isinstance(varvalue, int) or varvalue.is_integer()): decs = 0                # it is of integer value
                    else:                                                                decs = 3                # it has decimals
                    vcc += ",{:>8s}".format(customformat(varvalue, 8, decs, thousand=False))
                else:
                    vcc += ",{:>8s}".format("nan")

        # add to print-string only if there is at least 1 non-nan value in this line
        if NonNANCount > 0:
            printstring    += vcc + "\n"
            printlinecount += 1

            if printlinecount > printlineMax:
                fprint(printstring[:-1])
                printstring    = ""
                printlinecount = 0
                printlineMax  += 30
                QtUpdate()

        if i % 200 == 0:
            QtUpdate()  # required for testing on stopPrinting!
            if g.stopPrinting: break

    # print but remove last LF
    if printstring > "":
        fprint(printstring[:-1])
        fprint(dataheader)
    else:
        qefprint("No data")

    g.stopPrinting = False
    setNormalCursor()


# not used
def plotMonitor():
    """Plot the Monitor"""

    """
        if not g.debug: return

    defname = "plotMonitor: "

    # get the last value
    if g.lastLogValues is None:
        lastvalue = 316
    else:
        lastvalue = g.lastLogValues["CPM"]

    # the speedometer with matplotlib
    canvasMon = getMonGraph(lastvalue)

    labout  = QTextBrowser() # label to hold the description
    labout.setFont(g.fontstd)
    labout.setFixedHeight(80)
    labout.append("lastvalue:        {}".format(lastvalue))
    labout.append("log10(lastvalue): {:0.2f}".format(np.log10(lastvalue)))

    okButton = QPushButton("OK")
    okButton.setAutoDefault(True)
    okButton.clicked.connect(lambda:  d.done(0))

    bbox = QDialogButtonBox()
    bbox.addButton(okButton,      QDialogButtonBox.ActionRole)

    # makes the Qt speedometer graph
    my_gauge = gsup_gauge.AnalogGaugeWidget()
    my_gauge.scale_angle_start_value = 180          # 0 is east
    my_gauge.scale_angle_size = 180                 # 180 is west =270 grad
    my_gauge.angle_offset = 0
    my_gauge.gauge_color_inner_radius_factor = 0.75 # set thickness of arc hiher numer -> thinner arc
    my_gauge.enable_fine_scaled_marker = False      # minor marker a problem in log scale
    my_gauge.text_radius_factor = 1.15              # place numeric value -=bottom half += top half
    my_gauge.initial_scale_fontsize = 18            # scale labels
    my_gauge.setStyleSheet("border: 1px solid red; background-color:pink;") # nothing
    my_gauge.needle_scale_factor = 0.75              # length of needle 0.55  #0.8
    my_gauge.value = lastvalue

    layoutV = QVBoxLayout()
    layoutV.addWidget(canvasMon)
    layoutV.addWidget(labout)
    layoutV.addWidget(my_gauge)
    layoutV.addWidget(bbox)

    d = QDialog()
    d.setWindowIcon(g.iconGeigerLog)
    d.setWindowTitle("Monitor")
    d.setWindowModality(Qt.WindowModal)          # multiple Windows open, all runs, all is clickable
    d.setLayout(layoutV)

    # show window
    # figMon.canvas.draw_idle()
    d.exec()
    plt.close(g.monitorFigNo)

"""


# not used
def getMonGraph(lastvalue):
    """makes the matplotlib speedometer graph"""

    """
    defname = "getMonGraph: "

    if g.monitorfig is not None: plt.close(g.monitorfig)

    figMon, ax = plt.subplots(facecolor = "#E7F9C9", dpi=g.hidpiScaleMPL)
    g.monitorfig = figMon
    g.monitorax  = ax
    g.monitorFigNo = plt.gcf().number

    vprint(defname + "open figs count: {}, current fig: #{}".format(len(plt.get_fignums()), plt.gcf().number))

    lowThreshholdColor  = '#00C853' # green
    defaultColor        = '#ffe500' # yellow
    highThreshholdColor = '#EA4335' # red

    # get the threshold nunbers
    lowThreshhold  = 150
    highThreshhold = 1070

    # make the wedges
    wwidth = 0.10   # wedge width
    Valmin = np.log10(0.5)
    Valmax = np.log10(50000)
    ValTLo = 180 - np.log10(lowThreshhold) / (Valmax - Valmin) * 180
    ValTHi = 180 - np.log10(highThreshhold) / (Valmax - Valmin) * 180

    # print("Valmin, Valmax, ValTLo, ValTHi", Valmin, Valmax, ValTLo, ValTHi)

    # class matplotlib.patches.Wedge(center, r, theta1, theta2, width=None, **kwargs)
    # drawing goes counterclockwise, beginning at 0 = East
    wedge1 = mpat.Wedge((0.5,0.0), 0.5, 0,      ValTHi, zorder=0, width=wwidth, facecolor=highThreshholdColor)    # red
    wedge2 = mpat.Wedge((0.5,0.0), 0.5, ValTHi, ValTLo, zorder=0, width=wwidth, facecolor=defaultColor)           # yellow
    wedge3 = mpat.Wedge((0.5,0.0), 0.5, ValTLo, 180,    zorder=0, width=wwidth, facecolor=lowThreshholdColor)     # green

    ax.axis('off')
    ax.set_ylim([-0.1, 0.5])
    ax.set_xlim([0, 1])

    ax.add_artist(wedge1)
    ax.add_artist(wedge2)
    ax.add_artist(wedge3)

    # calc and make arrow
    arrow_length = 0.45
    # arrow_angle = np.log10(lastvalue)           # 180 * (1 - lastvalue / 100)
    arrow_angle = 180 - np.log10(lastvalue) / (Valmax - Valmin) * 180
    arrow_dy    = np.sin(np.pi * arrow_angle / 180) * arrow_length
    arrow_dx    = np.cos(np.pi * arrow_angle / 180) * arrow_length
    # print(defname + "lastvalue {:5.2f} arrow_angle {:5.2f}  dx {:5.2f}  dy {:5.2f}".format(lastvalue, arrow_angle, arrow_dx, arrow_dy) )
    myarr = ax.arrow(0.5, 0.0, arrow_dx, arrow_dy, width=0.03, color="k", head_length=0.37, length_includes_head=True, head_width=0.095, overhang=-0.2)
    g.myarr = myarr

    # canvas - this is the Canvas Widget that displays the `figure`
    # it takes the `figure` instance as a parameter to __init__
    canvasMon = FigureCanvas(figMon)
    canvasMon.setFixedSize(240, 144)
    # navtoolbar = NavigationToolbar(canvasMon, g.exgg)

    return canvasMon
"""


# not used
def plotpgGraph():
    """Plot the Time course graph in pyqtgraph,    pyqtgraph as alternative to matplotlib    """

    """

    if not g.debug: return

    # pyqtgraph stuff
    # import pyqtgraph            as pg
    # pg.setConfigOption('background', 'pink')
    # pg.setConfigOption('foreground', 'k')

    # y2 = np.random.normal(size=(3, 1000))
    # plotWidget = pg.plot(title="Three plot curves")
    # plotWidget.setMinimumHeight(300)
    # for i in range(3):
    #     plotWidget.plot(x[:1000], y2[i], pen=(i,3))  ## setting pen=(i,3) automaticaly creates three different-colored pens
    # plotWidget.plot(x[:1000],y[:1000])
    # plotWidget.plot(x[:1000],y[1000:2000])
    # plotWidget.plot(x[:1000],y[2000:3000])

    defname = "plotpgGraph: "

    import pyqtgraph as pg

    start = time.time()

    # textbrowser
    labout  = QTextBrowser() # label to hold the description
    labout.setFont(g.fontstd)
    labout.setFixedHeight(180)

    # print("start", start, "stop", stop)

    stop = time.time()
    labout.append("labout time: {:0.6f} ms".format((stop - start) * 1000))

    # buttonbox
    bbox = QDialogButtonBox()
    # bbox.setStandardButtons(QDialogButtonBox.Cancel | QDialogButtonBox.Ok )
    bbox.setStandardButtons(QDialogButtonBox.Ok )
    bbox.accepted.connect(lambda: d.done(1))
    # bbox.rejected.connect(lambda: d.done(-1))

    stop = time.time()
    labout.append("labout  + bbox time: {:0.6f} ms".format((stop - start) * 1000))

    # pggraph
    pg.setConfigOption('background', 'pink')
    pg.setConfigOption('foreground', 'k')

    plotWidget = pg.PlotWidget(title="My plot curves")
    plotWidget.setMinimumHeight(300)

    # data
    x = g.logTime
    # print("x:\n", x)

    try:
        for i in (0,1,2,3,4,5,6,7,8,10,11):
            y = g.currentDBData[:, i + 1]
            # print("y:\n", y)
            plotWidget.plot(x,y, pen=(i, 13))
    except Exception as e:
        msg = "Show PgGraph: No data"
        exceptPrint(e, msg)
        efprint(msg)
        return

    stop = time.time()
    labout.append("labout  + bbox + plotwidget time: {:0.6f} ms".format((stop - start) * 1000))

    layoutV = QVBoxLayout()
    layoutV.addWidget(labout)
    layoutV.addWidget(plotWidget)
    layoutV.addWidget(bbox)
    stop = time.time()
    labout.append("labout  + bbox + plotwidget + lV time: {:0.6f} ms".format((stop - start) * 1000))


    d = QDialog()
    d.setWindowIcon(g.iconGeigerLog)
    d.setWindowTitle("Monitor")
    d.setWindowModality(Qt.WindowModal)          # multiple Windows open, all runs, all is clickable
    d.setLayout(layoutV)

    stop = time.time()
    labout.append("labout  + bbox + plotwidget + lV + dialog time: {:0.6f} ms".format((stop - start) * 1000))

    # show window
    d.exec()
"""


def handleEmail(subject, message):
    """assemble Email, send, print"""

    defname = "handleEmail: "

    # create Email message object
    emsg             = EmailMessage()
    emsg['From']     = g.email["From"]
    emsg['To']       = g.email["To"]
    emsg['Subject']  = subject
    emsg.set_content(message)

    # only on werbose
    try:
        wprint(defname, "Email is prepared as:")
        wprint("=" * 40 + " BEGIN Content of Email message " + "=" * 40)
        etext = quopri.decodestring(emsg.as_string()).decode("ascii", errors='replace')
        # rdprint(defname, "etext: ", etext)
        etext = etext.split("\n")
        # rdprint(defname, "etext: ", etext)
        for et in etext:
            if et == "": et += "  "
            wprint(et)  # skip empty lines
        wprint("=" * 41 + " END Content of Email message "   + "=" * 41)
    except Exception as e:
        exceptPrint(e, "Email message has wrong char")

    success, ee = sendEmail(emsg)

    return (success, ee)


def sendEmail(emsg):
    """sending an email"""

    ###############################################
    def authobject(challenge=None):
        # return bytes("initial-response", "ASCII")
        # return "initial-response"
        # return "AUTH"
        # return "initial_response_ok"
        # return None                             ('NoneType' object has no attribute 'encode')
        # return 'auth_' + "XOAUTH".lower().replace('-', '_')
        # response = encode_base64("XOAUTH".encode('ascii'), eol='')
        # response = encode_base64("XOAUTH2".encode('ascii'), eol='')
        # return response
        return "="

    ###############################################
    defname = "sendEmail: "
    success = False
    ee      = ""

    from email.base64mime import body_encode as encode_base64
    rdprint(defname, f"server_host:: '{g.email['Host']}'  server_Port: {g.email['Port']}")

# SMTP:
# standard protocol: Simple Mail Transfer Protocol, Port: 587
    if g.email["Protocol"] == "SMTP":
        rdprint(defname, "Using SMTP  Simple Mail Transfer Protocol")
        try:
            server = smtplib.SMTP(host=g.email["Host"], port=g.email["Port"])
            server.starttls()
        except Exception as e:
            exceptPrint(e, defname + "Sending Email with smtplib.SMTP")
            return (success, ee)

# SMTP_SSL:
# enhanced protocol: Simple Mail Transfer Protocol, Port: 465
    else:
        rdprint(defname, "Using SMTP_SSL - enhanced Simple Mail Transfer Protocol")
        server = None
        try:

            # opens a Thunderbird email, but sending is not possibel :-(())
            # cmde = "thunderbird -compose \"to=" + g.email["To"] +",subject=" + "subjecttest" + ",body=" + "testing" + "\""
            # rdprint(defname, "cmde: ", cmde)
            # os.system(cmde)

            server = smtplib.SMTP_SSL(g.email["Host"], g.email["Port"])
            # print("server-help:", server.help())                        # prints: server-help: b'2.0.0  https://www.google.com/search?btnI&q=RFC+5321 2-20020a05600c22c200b003f42328b5d9sm10283815wmg.39 - gsmtp'

            server.ehlo_or_helo_if_needed()

            # server.esmtp_features:
            # mdprint("esmtp_features: ", server.esmtp_features)
            # for google: smtp.gmail.com
            # esmtp_features:
            # {'size': '35882577', '8bitmime': '',
            # 'auth': ' LOGIN PLAIN XOAUTH2 PLAIN-CLIENTTOKEN OAUTHBEARER XOAUTH',
            # 'enhancedstatuscodes': '', 'pipelining': '', 'chunking': '', 'smtputf8': ''}
            #
            # for strato:
            # esmtp_features: {'enhancedstatuscodes': '', 'pipelining': '', '8bitmime': '',
            # 'deliverby': '', 'size': '104857600', 'auth': ' PLAIN LOGIN CRAM-MD5 DIGEST-MD5',
            # 'requiretls': '', 'help': ''}


            # server.auth("XOAUTH2", authobject, initial_response_ok=True) # 501, b'5.5.2 Cannot Decode response n2-20020a5d4c42000000b003063db8f45bsm16832132wrt.23 - gsmtp
            # server.auth("LOGIN", authobject)                             # 535, b'5.7.8 Username and Password not accepted.
            # server.starttls()                                            # Exception: "STARTTLS extension not supported by server"


        except Exception as e:
            errmsg = defname + "Setting-up Email server: 'smtplib.SMTP_SSL' : e:"
            exceptPrint(e, errmsg)
            if server is not None: server.quit()                                               # end the smtpserver connection
            return (success, ee)

    try:
        server.login(g.email["From"], g.email["Password"])  # Login to server
        server.send_message(emsg)                           # send the message
        server.quit()                                       # quit connection
        ee = "Email was sent successfully"
        success = True

    except smtplib.SMTPHeloError as e:
        exceptPrint(e, "SMTPHeloError")
        ee = e

    except smtplib.SMTPAuthenticationError as e:
        exceptPrint(e, "SMTPAuthenticationError")
        ee = e

    except smtplib.SMTPNotSupportedError as e:
        exceptPrint(e, "SMTPNotSupportedError")
        ee = e

    except smtplib.SMTPException as e:
        exceptPrint(e, "SMTPException")
        ee = e

    except Exception as e:
        exceptPrint(e, "Default Exception sending Email")
        ee = e

    rdprint(defname, f"{ee}")

    return (success, ee)


#xyz
def setAlarmConfiguration():
    """Edit the configuration of the Alarm Settings"""

    defname = "setAlarmConfiguration: "

    vprint(defname)
    setIndent(1)

    fbox = QFormLayout()

# Alarm Activation
    r11 = QRadioButton("Yes")
    r12 = QRadioButton("No")
    r11.setChecked(False)
    r12.setChecked(False)
    alarmgroup = QButtonGroup()
    alarmgroup.addButton(r11)
    alarmgroup.addButton(r12)
    hbox1 = QHBoxLayout()
    hbox1.addWidget(r11)
    hbox1.addWidget(r12)
    hbox1.addStretch()
    fbox.addRow(QLabel("Alarm Activation"), hbox1)
    if g.AlarmActivation: r11.setChecked(True)
    else:                 r12.setChecked(True)

# Alarm Sound
    r21 = QRadioButton("Yes")
    r22 = QRadioButton("No")
    r21.setChecked(False)
    r22.setChecked(False)
    speakergroup = QButtonGroup()
    speakergroup.addButton(r21)
    speakergroup.addButton(r22)
    hbox2 = QHBoxLayout()
    hbox2.addWidget(r21)
    hbox2.addWidget(r22)
    hbox2.addStretch()
    fbox.addRow(QLabel("Alarm Sound"), hbox2)
    if g.AlarmSound:   r21.setChecked(True)
    else:              r22.setChecked(True)

# Alarm Idle Cycles
    g.exgg.cal1_cpm = QLineEdit(str(g.AlarmIdleCycles))
    g.exgg.cal1_cpm.setFont(g.fontstd)
    # g.exgg.cal1_cpm.setValidator (QIntValidator(*cpmlimit))
    g.exgg.cal1_cpm.setToolTip("Values 1 ... 60 possible")
    fbox.addRow("Alarm Idle Cycles",    g.exgg.cal1_cpm)


# On Alarm Action - Sent Email
    alarmSentEmail = QCheckBox("Send Email")
    alarmSentEmail.setChecked(g.emailUsage)
    alarmSentEmail.setToolTip("To enable usage activate in config 'geigerLog.cfg'")
    fbox.addRow("On Alarm", alarmSentEmail)
    if not g.emailActivation: alarmSentEmail.setEnabled(False)


### Telegram is not active
# # On Alarm Action - Sent Telegram
#     alarmSentMsg   = QCheckBox("Send Msg to Telegram")
#     alarmSentMsg  .setChecked(g.TelegramActivation)
#     fbox.addRow("",            alarmSentMsg)


# separator blank line
    fbox.addRow(QLabel(""))

# variables
    # headerVariable       :
    fbox.addRow(QLabel("Alarm Limits"), QLabel("None | N,  min,  max"))
    fbox.addRow(QLabel(""), QLabel("   N:   1 ... 60"))
    fbox.addRow(QLabel(""), QLabel("   min: None | <any value>"))
    fbox.addRow(QLabel(""), QLabel("   max: None | <any value>"))
    vartext = {}
    for vname in g.AlarmLimits:
        # rdprint(defname, "alarmlimits: ", g.AlarmLimits[vname])
        if g.AlarmLimits[vname] is not None:    alimits = ", ".join( "{}".format(lim) for lim in  g.AlarmLimits[vname])
        else:                                   alimits = "None"
        vartext[vname] = QLineEdit(alimits)
        fbox.addRow("   " + vname, vartext[vname] )

# final blank line
    fbox.addRow(QLabel(""))

# create dialog
    dialog = QDialog()
    dialog.setWindowIcon(g.iconGeigerLog)
    dialog.setFont(g.fontstd)
    dialog.setWindowTitle("Set Alarm Configuration")
    dialog.setWindowModality(Qt.WindowModal)
    dialog.setMinimumWidth(400)

    bbox = QDialogButtonBox()
    bbox.setStandardButtons(QDialogButtonBox.Ok|QDialogButtonBox.Cancel)
    bbox.rejected.connect           (lambda: dialog.done(0))    # cancel, ESC key
    bbox.accepted.connect           (lambda: dialog.done(1))    # ok

    layoutV = QVBoxLayout(dialog)
    layoutV.addLayout(fbox)
    layoutV.addWidget(bbox)

# show dialog
    # rdprint(defname, "Executing Dialog")
    alarmdlg = dialog.exec()

# check dialog result
    errmsg = ""
    if alarmdlg == 0:
        errmsg = "Cancelled"
        vprint(defname, errmsg)

    else:
    # get data
        g.AlarmActivation       = True if r11.isChecked() else False
        g.AlarmSound            = True if r21.isChecked() else False

        # g.emailActivation       = True if alarmSentEmail.isChecked() else False
        g.emailUsage            = True if alarmSentEmail.isChecked() else False
        # g.TelegramActivation    = True if alarmSentMsg  .isChecked() else False

        # AlarmIdleCycles
        try:
            aic = int(g.exgg.cal1_cpm.text())
        except Exception as e:
            exceptPrint(e, "g.AlarmIdleCycles")
            aic = 30
        else:
            aic = clamp(aic, 1, 60)
        g.AlarmIdleCycles = aic

        # Alarmlimits
        for vname in g.AlarmLimits:
            ltext = vartext[vname].text().strip()
            if ltext.upper() == "NONE" or ltext.upper() == "":
                g.AlarmLimits[vname] = None
            else:
                limits = ltext.split(",")
                for i, l in enumerate(limits): limits[i] = limits[i].strip()
                if len(limits) < 3:
                    continue
                else:
                    try:
                        AlarmN     = clamp(int(limits[0]), 1, 60)
                        AlarmLower = None if limits[1].upper() == "NONE" else float(limits[1])
                        AlarmUpper = None if limits[2].upper() == "NONE" else float(limits[2])
                    except Exception as e:
                        exceptPrint(e, defname + "AlarmConfig vname: '{}".format(vname))
                        errmsg += "AlarmConfig Ignoring illegal entry '{}' for {}\n".format(ltext, vname)
                    else:
                        g.AlarmLimits[vname] = [AlarmN, AlarmLower, AlarmUpper]

            vprint("{:6s} :  {}".format(vname, g.AlarmLimits[vname]))

    setIndent(0)

    return errmsg

