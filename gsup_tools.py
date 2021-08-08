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
__copyright__       = "Copyright 2016, 2017, 2018, 2019, 2020, 2021"
__credits__         = [""]
__license__         = "GPL3"

from   gsup_utils       import *

import gsup_sql

xt, yt, vline, zero, FitFlag, FitSelector = 0, 0, True, "None", True, "Prop"


def printSuSt():
    """Prints an overview of data from all variables"""

    if gglobs.logTimeSlice is None:
        gglobs.exgg.showStatusMessage("No data available")
        return

    timespan_total = gglobs.logTime[-1] - gglobs.logTime[0]
    timespan_plot  = gglobs.logTimeSlice[-1] - gglobs.logTimeSlice[0]
    size_total     = gglobs.logTime.size
    size_plot      = gglobs.logTimeSlice.size
    cycle_total    = timespan_total / size_total * 86400 # sec
    cycle_plot     = timespan_plot  / size_plot  * 86400 # sec

    fprint(header("Summary Statistics of Variables selected in Plot"))
    fprint("File       = {}".format(gglobs.currentDBPath))
    if os.access(gglobs.currentDBPath , os.R_OK):
        fprint("Filesize   = {:10,.0f} Bytes".format(os.path.getsize(gglobs.currentDBPath)))
    else:
        fprint("Filesize   = File not found!")
    fprint("Records    = {:10,.0f} total,   {:10,.0f} shown in Plot"    .format(size_total, size_plot))
    fprint("Time Span  = {:10,.5f} d total, {:10,.5f} d shown in Plot"  .format(timespan_total, timespan_plot))
    fprint("Avg. Cycle = {:10,.1f} s total, {:10,.1f} s shown in Plot"  .format(cycle_total, cycle_plot))

    fprint("          [Unit]      Avg ±StdDev     Variance          Range            Recs  Last Value")
    for i, vname in enumerate(gglobs.varsBook):
        if gglobs.varcheckedCurrent:
            try:    fprint( gglobs.varlabels[vname])
            except: pass


def getlstats(logTime, logVar, vname):
    """get the text for the QTextBrowser in printStats"""

    vnameFull        = gglobs.varsBook[vname][0]

    logSize          = logTime.size
    logtime_max      = logTime.max()
    logtime_min      = logTime.min()
    logtime_delta    = logtime_max - logtime_min # in days

    records_nonnan   = np.count_nonzero(~np.isnan(logVar))

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
        logVar_text      = "(in units of: {})".format(gglobs.Yunit)

    elif vname in ("CPS",  "CPS1st", "CPS2nd", "CPS3rd"):
        if gglobs.Yunit == "CPM":   unitText = "CPS"
        else:                       unitText = gglobs.Yunit
        logVar_text      = "(in units of: {})".format(unitText)

    else:
        logVar_text      = ""

    ltext = []
    ltext.append("Variable: {} {}\n".format(vnameFull, logVar_text))
    ltext.append("  Recs      = {:10,.0f}  Records".format(records_nonnan))

    if   gglobs.Yunit == "CPM" and (vname in ("CPM", "CPM1st", "CPM2nd", "CPM3rd")):
        ltext.append("  Counts    = {:10,.0f}  Counts calculated as: Average CPM * Log-Duration[min]\n".format(logVar_avg * logtime_delta * 24 * 60))

    elif gglobs.Yunit == "CPM" and (vname in ("CPS", "CPS1st", "CPS2nd", "CPS3rd")):
        ltext.append("  Counts    = {:10,.0f}  Counts calculated as: Average CPS * Log-Duration[sec]\n".format(logVar_avg * logtime_delta * 24 * 60 * 60))

    else:
        ltext.append("")

    #~print("----------------vname: ", vname)
    ltext.append("                       % of avg")
    ltext.append("  Average   ={:8.2f}      100%       Min  ={:8.2f}        Max  ={:8.2f}" .format(logVar_avg,                              logVar_min,          logVar_max)          )
    if logVar_avg != 0:
        ltext.append("  Variance  ={:8.2f} {:8.2f}%"                                          .format(logVar_var,  logVar_var  / logVar_avg * 100))
        ltext.append("  Std.Dev.  ={:8.2f} {:8.2f}%       LoLim={:8.2f}        HiLim={:8.2f}" .format(logVar_std,  logVar_std  / logVar_avg * 100,  logVar_avg-logVar_std,         logVar_avg+logVar_std)  )
        ltext.append("  Sqrt(Avg) ={:8.2f} {:8.2f}%       LoLim={:8.2f}        HiLim={:8.2f}" .format(logVar_sqrt, logVar_sqrt / logVar_avg * 100,  logVar_avg-logVar_sqrt,        logVar_avg+logVar_sqrt) )
        ltext.append("  Std.Err.  ={:8.2f} {:8.2f}%       LoLim={:8.2f}        HiLim={:8.2f}" .format(logVar_err,  logVar_err  / logVar_avg * 100,  logVar_avg-logVar_err,         logVar_avg+logVar_err) )
        ltext.append("  Median    ={:8.2f} {:8.2f}%       P_5% ={:8.2f}        P_95%={:8.2f}" .format(logVar_med,  logVar_med  / logVar_avg * 100,  np.nanpercentile(logVar, 5),   np.nanpercentile(logVar, 95)))
        ltext.append("  95% Conf*)={:8.2f} {:8.2f}%       LoLim={:8.2f}        HiLim={:8.2f}" .format(logVar_95,   logVar_95   / logVar_avg * 100,  logVar_avg-logVar_95,          logVar_avg+logVar_95)   )
    else:
        ltext.append("  Variance  ={:8.2f}  {:>8s}"                                             .format(logVar_var,  "N.A."))
        ltext.append("  Std.Dev.  ={:8.2f}  {:>8s}       LoLim={:8.2f}        HiLim={:8.2f}"   .format(logVar_std,  "N.A."                         ,  logVar_avg-logVar_std,         logVar_avg+logVar_std)  )
        ltext.append("  Sqrt(Avg) ={:8.2f}  {:>8s}       LoLim={:8.2f}        HiLim={:8.2f}"   .format(logVar_sqrt, "N.A."                         ,  logVar_avg-logVar_sqrt,        logVar_avg+logVar_sqrt) )
        ltext.append("  Std.Err.  ={:8.2f}  {:>8s}       LoLim={:8.2f}        HiLim={:8.2f}"   .format(logVar_err,  "N.A."                         ,  logVar_avg-logVar_err,         logVar_avg+logVar_err) )
        ltext.append("  Median    ={:8.2f}  {:>8s}       P_5% ={:8.2f}        P_95%={:8.2f}"   .format(logVar_med,  "N.A."                         ,  np.nanpercentile(logVar, 5),   np.nanpercentile(logVar, 95)))
        ltext.append("  95% Conf*)={:8.2f}  {:>8s}       LoLim={:8.2f}        HiLim={:8.2f}"   .format(logVar_95,   "N.A."                         ,  logVar_avg-logVar_95,          logVar_avg+logVar_95)   )

    return "\n".join(ltext)


def printStats():
    """Printing statistics - will always show only data in current plot"""

    logTime          = gglobs.logTimeSlice           # time data

    if gglobs.logTime is None:
        gglobs.exgg.showStatusMessage("No data available") # when called without a loaded file
        return

    setBusyCursor()

    logSize          = logTime.size
    logtime_size     = logTime.size
    logtime_max      = logTime.max()
    logtime_min      = logTime.min()
    logtime_delta    = logtime_max - logtime_min # in days

    oldest   = (str(mpld.num2date(logtime_min)))[:19]
    youngest = (str(mpld.num2date(logtime_max)))[:19]

    lstats   = QTextBrowser()      # label to hold the description
    lstats.setLineWrapMode(QTextEdit.NoWrap)
    lstats.setTextInteractionFlags(Qt.LinksAccessibleByMouse|Qt.TextSelectableByMouse)

    lstats.append("Data from file: {}\n".format(gglobs.currentDBPath))
    lstats.append("Totals")
    lstats.append("  Filesize  = {:12,.0f} Bytes".format(os.path.getsize(gglobs.currentDBPath)))
    lstats.append("  Records   = {:12,.0f} shown in current plot".format(logSize))
    lstats.append("")
    lstats.append("Legend:   *): Approximately valid for a Poisson Distribution when Average > 10\n")
    lstats.append("="*100)

    lstats.append("Time")
    lstats.append("  Oldest rec    = {}  (time = {:.3f} d)".format(oldest,   0))
    lstats.append("  Youngest rec  = {}  (time = {:.3f} d)".format(youngest, logtime_max - logtime_min))
    lstats.append("  Duration      = {:.1f} s   = {:.3f} m   = {:.3f} h   = {:.3f} d".format(logtime_delta *86400, logtime_delta*1440, logtime_delta *24, logtime_delta))
    lstats.append("  Cycle average = {:0.2f} s".format(logtime_delta *86400/ (logSize -1)))
    lstats.append("="*100)

    for i, vname in enumerate(gglobs.varsBook):
        if gglobs.varcheckedCurrent:
            try:
                logVar  = gglobs.logSliceMod[vname]     # var data
            except:
                continue
            getlstatstext =  getlstats(logTime, logVar, vname)
            lstats.append(getlstatstext)
            lstats.append("="*100)

    lstats.append("First and last few records:\n")
    sql, ruler = gsup_sql.getShowCompactDataSql(gglobs.varcheckedCurrent)
    lstats.append(ruler)
    lstats.append(gglobs.exgg.getExcerptLines(sql, gglobs.currentConn, lmax=7))
    lstats.append(ruler)

    lstats.moveCursor(QTextCursor.Start)

    d = QDialog()
    d.setWindowIcon(gglobs.iconGeigerLog)
    d.setFont(gglobs.fontstd)
    d.setWindowTitle("Statistics on Checked Variables")
    d.setWindowModality(Qt.WindowModal) #Qt.ApplicationModal, Qt.NonModal
    d.setMinimumWidth(1100)
    d.setMinimumHeight(750)

    bbox    = QDialogButtonBox()
    bbox.setStandardButtons(QDialogButtonBox.Ok)
    bbox.accepted.connect(lambda: d.done(0))

    layoutV = QVBoxLayout(d)
    layoutV.addWidget(lstats)
    layoutV.addWidget(bbox)

    setNormalCursor()

    d.exec_()


def selectScatterPlotVars():
    """Selecting the vars for the scatter plot and display and fit options"""

    global xt, yt, vline, zero, FitFlag, FitSelector # to keep the selectios

    if gglobs.logTime is None:              # when called without a loaded file
        gglobs.exgg.showStatusMessage("No data available")
        return

    # X-axis and Y-axis vars
    xlist = QListWidget()
    xlist.setSelectionMode(QAbstractItemView.SingleSelection)
    xlist.addItem("time")
    ylist = QListWidget()
    ylist.setSelectionMode(QAbstractItemView.SingleSelection)
    ylist.addItem("time")
    for i, vname in enumerate(gglobs.varsBook):
        if gglobs.varcheckedCurrent[vname]:
            #~print("gglobs.varcheckedCurrent[vname]: ", vname,  gglobs.varcheckedCurrent[vname])
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
    b0 = QRadioButton("Show Optimal ")             # this is default
    b1 = QRadioButton("Show X=0")
    b2 = QRadioButton("Show Y=0")
    b3 = QRadioButton("Show X,Y=0")

    if   zero == "None"      : b0.setChecked(True)
    elif zero == "x"         : b1.setChecked(True)
    elif zero == "y"         : b2.setChecked(True)
    elif zero == "x and y"   : b3.setChecked(True)
    else                     : b0.setChecked(True)

    # draw connecting lines?
    checkb  = QCheckBox("Connecting Line")      # default is yes
    checkb.setChecked(vline)

    layoutT = QHBoxLayout()
    layoutT.addWidget(b3)
    layoutT.addWidget(b1)
    layoutT.addWidget(b2)
    layoutT.addWidget(b0)
    layoutT.addStretch()

    # add polynomial fit?                         default is yes
    checkF = QCheckBox("Add Polynomial Fit of order:")
    checkF.setChecked(FitFlag)

    # selector for order of fit                   default is 1st order = linear
    comboboxF = QComboBox()
    comboboxF.addItems(["Prop", "0", "1", "2", "3", "4", "5", "6", "7"])
    comboboxF.setMaximumWidth(70)
    comboboxF.setToolTip('Select the degree of the polynomial fit')

    #~print("-------------FitSelector: ", FitSelector)
    if FitSelector == "Prop":   comboboxF.setCurrentIndex(0)
    else:                       comboboxF.setCurrentIndex(int(FitSelector) + 1)

    layoutF = QHBoxLayout()
    layoutF.addWidget(checkb)
    layoutF.addWidget(checkF)
    layoutF.addWidget(comboboxF)
    layoutF.addStretch()

    bbox = QDialogButtonBox()
    bbox.setStandardButtons(QDialogButtonBox.Cancel | QDialogButtonBox.Ok )
    bbox.accepted.connect(lambda: d.done(100)) # ESC key produces 0 (zero)!
    bbox.rejected.connect(lambda: d.done(-1))

    layoutH0 = QHBoxLayout()
    layoutH0.addWidget(QLabel("X"))
    layoutH0.addWidget(QLabel("Y"))

    layoutH = QHBoxLayout()
    layoutH.addWidget(xlist)
    layoutH.addWidget(ylist)

    d = QDialog()
    d.setWindowIcon(gglobs.iconGeigerLog)
    d.setFont(gglobs.fontstd)
    d.setWindowTitle("Select Variables for Scatter Plot")
    d.setWindowModality(Qt.ApplicationModal)
    d.setMinimumHeight(350)
    #d.setWindowModality(Qt.NonModal)
    #d.setWindowModality(Qt.WindowModal)
    #d.setStyleSheet("QLabel { background-color:#DFDEDD; color:rgb(40,40,40); font-size:30px; font-weight:bold;}")

    layoutV = QVBoxLayout(d)
    layoutV.addLayout(layoutH0)
    layoutV.addLayout(layoutH)
    layoutV.addLayout(layoutT)
    layoutV.addLayout(layoutF)
    layoutV.addWidget(bbox)

    retval = d.exec()
    #print("reval:", retval)
    if retval != 100: return  # ESC key produces 0

    #~print("xlist.currentItem(): ", xlist.currentItem().text())
    #~print("ylist.currentItem(): ", ylist.currentItem().text())
    xt          = xlist.currentItem().text()
    yt          = ylist.currentItem().text()
    vline       = checkb.isChecked()
    FitFlag     = checkF.isChecked()
    FitSelector = comboboxF.currentText()

    if   b0.isChecked():  zero = "None"
    elif b1.isChecked():  zero = "x"
    elif b2.isChecked() : zero = "y"
    elif b3.isChecked() : zero = "x and y"
    else                : zero = "None"

    plotScatter(xt, yt, vline, zero, FitFlag, FitSelector)


def plotScatter(vx, vy, vline, zero, FitFlag, FitSelector):
    """Plotting a Scatter plot"""

    vprint("plotScatter: x:{}, y:{}, vline:{}, zero:{}, FitFlag:{}, FitSelector:{}".format(vx, vy, vline, zero, FitFlag, FitSelector))

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

    if gglobs.currentDBPath is None: DataSrc = "No Data source!"
    else:                            DataSrc = os.path.basename(gglobs.currentDBPath)

    localvardict = gglobs.varsBook.copy()
    localvardict.update( {'time' : ('time [d]', 'time') } )

    #~print("gglobs.logTimeDiffSlice: ", gglobs.logTimeDiffSlice)
    #~print("gglobs.logSlice: ", gglobs.logSlice)
    #print("vx: ", vx)
    if vx == "time":
        x0 = gglobs.logTimeDiffSlice
    else:
        try:
            x0 = gglobs.logSlice[vx]
        except Exception as e:
            fprint(header("Plot Scatter X"))
            fprint("ERROR in plotScatter: Exception: ", e)
            return

    #print("vy: ", vy)
    if vy == "time":
        y0 = gglobs.logTimeDiffSlice
    else:
        try:
            y0 = gglobs.logSlice[vy]
        except Exception as e:
            fprint(header("Plot Scatter Y"))
            fprint("ERROR in plotScatter: Exception: ", e)
            return

    ymask                   = np.isfinite(y0)      # mask for nan values
    y1                      = y0[ymask]
    x1                      = x0[ymask]

    xmask                   = np.isfinite(x1)      # mask for nan values
    y                       = y1[xmask]
    x                       = x1[xmask]

    if y.size > 0:  plotstyle['markersize'] = float(plotstyle['markersize']) / np.sqrt(y.size)
    else:           plotstyle['markersize'] = 3

    fig2 = plt.figure(facecolor = "#E7F9C9", dpi=gglobs.hidpiScaleMPL)
    gglobs.plotScatterFigNo = plt.gcf().number
    vprint("plotScatter: open figs count: {}, current fig: #{}".format(len(plt.get_fignums()), plt.gcf().number))

    plt.title("Scatter Plot\n", fontsize=12, loc='center')
    subTitleLeft  = DataSrc
    subTitleRight = "Recs:" + str(len(x))
    plt.title(subTitleLeft,  fontsize=10, fontweight='normal', loc = 'left')
    plt.title(subTitleRight, fontsize=10, fontweight='normal', loc = 'right')

    plt.xlabel("x = " + localvardict[vx][0], fontsize=12)
    plt.ylabel("y = " + localvardict[vy][0], fontsize=12)

    plt.grid(True)
    plt.subplots_adjust(hspace=None, wspace=.2 , left=.15, top=0.90, bottom=0.1, right=.97)
    plt.ticklabel_format(useOffset=False)

    # hide the cursor position from showing in the Nav toolbar
    ax1 = plt.gca()
    ax1.format_coord = lambda x, y: ""
    #fig2.canvas.toolbar.set_message = lambda x: "" # suppress all messages???

    # canvas - this is the Canvas Widget that displays the `figure`
    # it takes the `figure` instance as a parameter to __init__
    canvas2 = FigureCanvas(fig2)
    canvas2.setFixedSize(700, 600)
    navtoolbar = NavigationToolbar(canvas2, gglobs.exgg)

    labout  = QTextBrowser() # label to hold the description
    labout.setFont(gglobs.fontstd)
    labout.setMinimumHeight(210)
    txtlines  = "Connecting lines are {}drawn".format("" if vline else "not ")
    txtorigin = "an origin of zero is enforced for {}".format(zero)
    labout.setText("Scatter Plot of y = {} versus x = {}.".format(localvardict[vy][0], localvardict[vx][0]))
    labout.append("{}; {}.".format(txtlines, txtorigin))

    d = QDialog()
    gglobs.plotScatterPointer = d
    d.setWindowIcon(gglobs.iconGeigerLog)
    d.setWindowTitle("Scatter Plot")
    #d.setWindowModality(Qt.ApplicationModal)
    #d.setWindowModality(Qt.NonModal)
    d.setWindowModality(Qt.WindowModal)

    okButton = QPushButton("OK")
    #okButton.setCheckable(True)
    okButton.setAutoDefault(True)
    okButton.clicked.connect(lambda:  d.done(0))

    selectButton = QPushButton("Select")
    #selectButton.setCheckable(True)
    selectButton.setAutoDefault(False)
    selectButton.clicked.connect(lambda:  nextScatterPlot())

    bbox = QDialogButtonBox()
    bbox.addButton(okButton,      QDialogButtonBox.ActionRole)
    bbox.addButton(selectButton,  QDialogButtonBox.ActionRole)

    layoutH = QHBoxLayout()
    layoutH.addWidget(bbox)
    layoutH.addWidget(navtoolbar)
    layoutH.addStretch()
    layoutH.addStretch() # double stretch needed in Py3.6, Py3.9 (others not checked)

    layoutV = QVBoxLayout(d)
    layoutV.addLayout(layoutH)
    layoutV.addWidget(canvas2)
    layoutV.addWidget(labout)

    plt.plot(x, y, **plotstyle) # need to plot first, so xlim, ylim become available!

    xlim = ax1.get_xlim()       # xlim is tuple
    ylim = ax1.get_ylim()

    labout.append("\nPolynomial Coefficients of the Least-Squares-Regression Fit:")
    labout.append("Lowest power first: y = #0 + #1 * x + #2 * x² + #3 * x³ + ...")

    if FitFlag:
        if x.size != 0 and y.size != 0:
            #print("size(x), (y): ", x.size, " ", y.size)

            if FitSelector != "Prop":
                try:
                    pfit = np.polyfit(x, y, int(FitSelector))
                    dprint("plotScatter: pfit: ", pfit)
                    for i,f in enumerate(np.flip(pfit)):
                        labout.append("#{:d} : {: .4g}".format(i, f))

                    p  = np.poly1d(pfit)
                    xs = sorted(x)
                    plt.plot(xs, p(xs), color="red", marker=None, linestyle="solid", linewidth=2)
                except Exception as e:
                    dprint("plotScatter: pfit: Failure with exception: ", e)
                    labout.append("\nFailure to plot. Exception: {}".format(e))
                    playWav("err")

            else:
                def func(x, a):
                    return a * x

                from scipy.optimize import curve_fit
                try:
                    popt, pcov = curve_fit(func, x, y)
                    dprint("plotScatter: curve_fit: popt, pcov, perr: ", popt, pcov, np.sqrt(np.diag(pcov)))
                    labout.append("#0 : {: .4g} (Prop)".format(0))
                    labout.append("#1 : {: .4g}".format(popt[0]))
                    plt.plot(x, func(x, *popt), color="red", marker=None, linestyle="solid", linewidth=2)
                except Exception as e:
                    dprint("plotScatter: curve_fit: Failure with exception: ", e)
                    labout.append("\nFailure to plot. Exception: {}".format(e))
                    playWav("err")
        else:
            dprint("plotScatter: no data in either x or y: x:\n", x, "\ny:\n", y)
            labout.append("\nFailure to plot:")
            if x.size == 0: labout.append("   No data in x")
            if y.size == 0: labout.append("   No data in y")
            playWav("err")

    if   zero == "x" :      plt.xlim(left   = 0)
    elif zero == "y" :      plt.ylim(bottom = 0)
    elif zero == "x and y":
        plt.ylim(bottom = 0)
        plt.xlim(left   = 0)
    elif zero == "None":    pass

    # show window
    fig2.canvas.draw_idle()
    d.exec()
    plt.close(gglobs.plotScatterFigNo)


def nextScatterPlot():
    """closes the dialog and reopens the var selection """

    #print("nextScatter: ")
    gglobs.plotScatterPointer.close()   # closes the dialog
    plt.close(gglobs.plotScatterFigNo)  # closes the figure
    selectScatterPlotVars()


def displayLastValues(self):
    """Displays the last values in big letters"""
    # For the updating see updateDisplayVariableValue()

    # print("+++++++++++++++++++++++++++++++++++++displayLastValues was called")

    if gglobs.logConn == None:          return
    if gglobs.displayLastValsIsOn :   return
    if gglobs.lastValues == None:       return

    gglobs.displayLastValsIsOn = True

    d = QDialog()
    d.setWindowIcon(gglobs.iconGeigerLog)
    d.setFont(gglobs.fontstd)
    d.setWindowTitle("Display Last Log Values")
    d.setWindowModality(Qt.WindowModal)       # can click anywhere, but also can have open many windows
    #d.setWindowModality(Qt.ApplicationModal) # only one window can be open, but can't click anywhere else
    #d.setWindowModality(Qt.NonModal)         # only one window can be open, but can't click anywhere else
    d.setMinimumWidth(420)
    d.setStyleSheet("QLabel {background-color:#DFDEDD; color:rgb(80,80,80);}")

    bbox    = QDialogButtonBox()
    bbox.setStandardButtons(QDialogButtonBox.Ok)
    bbox.accepted.connect(lambda: d.done(0))

    gridlo  = QGridLayout()
    gridlo.setVerticalSpacing(10) # more than default, 5 is about normal?
    layoutV = QVBoxLayout(d)
    lenvn   = len(gglobs.varsBook)
    klabels = [None] * lenvn   # variable names
    dlabels = [None] * lenvn   # device names
    vlabels = [None] * lenvn   # variable values

    t1 = QLabel("Variable")
    t1.setStyleSheet("QLabel {color: #111111; font-size:20px; font-weight:bold;}")
    t2 = QLabel("Device")
    t2.setStyleSheet("QLabel {color: #111111; font-size:20px; font-weight:bold; qproperty-alignment:AlignCenter;}")
    t3 = QLabel("Value")
    t3.setStyleSheet("QLabel {color: #111111; font-size:20px; font-weight:bold; qproperty-alignment:AlignCenter;}")

    gridlo.addWidget(t1,    0, 0)
    gridlo.addWidget(t2,    0, 1)
    gridlo.addWidget(t3,    0, 2)
    gridlo.setColumnStretch(2, 1) # give more space to value col

    for i, vname in enumerate(gglobs.varsBook):
           #print("---i, vname:", i, vname)
            klabels[i] = QLabel(gglobs.varsBook[vname][0])
            klabels[i].setFont((QFont("Sans", 12, weight=QFont.Bold)))
            dlabels[i] = QLabel(" ")

            if not gglobs.varcheckedLog[vname]:
                val = "{:>18s}".format("not mapped")
            else:
                if not np.isnan(gglobs.lastValues[vname]):
                    val = "{:>10.2f}".format(gglobs.lastValues[vname])
                else:
                    val = "{:>10s}".format("  --- ")
            gglobs.exgg.vlabels[i] = QLabel(val)
            gglobs.exgg.vlabels[i].setFont(QFont("Monospace", 22, weight=QFont.Black))
            if gglobs.logging and gglobs.varcheckedLog[vname]:
                gglobs.exgg.vlabels[i].setStyleSheet("QLabel {background-color:#F4D345; color:black; }")
            elif not gglobs.logging and gglobs.varcheckedLog[vname]:
                gglobs.exgg.vlabels[i].setStyleSheet("QLabel {color:darkgray; }")
            else:
                gglobs.exgg.vlabels[i].setStyleSheet("QLabel {color:darkgray; font-size:14px;}")

            for dname in gglobs.Devices:
                #print("dname:", dname, ", vname:", vname)
                if not gglobs.Devices[dname][1] is None:
                    if vname in gglobs.Devices[dname][1]:
                        dlabels[i] = QLabel(dname)
                dlabels[i].setAlignment(Qt.AlignCenter)
                dlabels[i].setStyleSheet("QLabel {color:#111111; font-size:14px;}")

            gridlo.addWidget(klabels[i],             i + 1, 0)
            gridlo.addWidget(dlabels[i],             i + 1, 1)
            gridlo.addWidget(gglobs.exgg.vlabels[i], i + 1, 2)

    layoutV.addLayout(gridlo)

    layoutV.addWidget(bbox)

    d.exec_()
    gglobs.displayLastValsIsOn = False


def printPlotData():
    """Print Data to Notepad as selected in Plot. Data are taken from the plot,
    not from the database!"""

    t0 = gglobs.logTimeSlice

    if t0 is None or len(t0) == 0:
        gglobs.exgg.showStatusMessage("No data available")
        return

    setBusyCursor()

    header = "{:5s}, {:19s}".format("#No", "Datetime")
    for vname in gglobs.varsDefault:
        if gglobs.exgg.varDisplayCheckbox[vname].isChecked():
            header += ", {:>8s}".format(vname)
    fprint(header)

    for i in range(len(t0)):
        vcc = "{:>5d}, {:<19s}".format(i, str(mpld.num2date(t0[i]))[:19])
        for vname in gglobs.varsDefault:
            if gglobs.exgg.varDisplayCheckbox[vname].isChecked():
                vi = gglobs.logSlice[vname][i]
                if    np.isnan(vi): vcc += ", {:>8s}".format("nan")
                else:               vcc += ", {:>8.2f}".format(gglobs.logSlice[vname][i])
        fprint(vcc)
        if gglobs.stopPrinting: break
        Qt_update()

    gglobs.stopPrinting = False

    fprint(header)

    setNormalCursor()


def getLogValues():
    """
    Reads variables CPM, ... etc. from devices, saves it in log file, and
    prints record into LogPad.
    Called by the timer once the timer is started
    """

    start = time.time()

    if not gglobs.logging:      return    # currently not logging
    if gglobs.logConn == None:  return    # no connection defined

    fncname = "getLogValues: "

    import gsup_plot

    gglobs.exgg.dcycl.setStyleSheet("QPushButton {background-color:#F4D345; color:rgb(0,0,0);}")
    Qt_update()

    if gglobs.GMCActivation:        import gdev_gmc         # GMC
    if gglobs.AudioActivation:      import gdev_audio       # AudioCounter
    if gglobs.RMActivation:         import gdev_radmon      # RadMon - then imports "paho.mqtt.client as mqtt"
    if gglobs.AmbioActivation:      import gdev_ambiomon    # AmbioMon
    if gglobs.GSActivation:         import gdev_scout      # GammaScout
    if gglobs.I2CActivation:        import gdev_i2c         # I2C  - then imports dongles and sensor modules
    if gglobs.LJActivation:         import gdev_labjack     # LabJack - then trys to import the LabJack modules
    if gglobs.RaspiActivation:      import gdev_raspi       # Raspi
    if gglobs.SimulActivation:      import gdev_simul       # SimulCounter
    if gglobs.MiniMonActivation:    import gdev_minimon     # MiniMon

    if gglobs.verbose: print()                              # empty line to terminal only
    vprint(fncname + "saving to:", gglobs.logDBPath)
    setDebugIndent(1)

    printLoggedValuesHeader()

    timeJulian, timetag = gsup_sql.DB_getLocaltime() # e.g.: 2458512.928904213, '2019-01-29 10:17:37'
    #~print(fncname + "timetag:", timetag, ",  timeJulian:",timeJulian)

# Reset the logValues to NAN
    logValue = {}                              # logvalue dict
    for vname in gglobs.varsDefault:
        logValue[vname] = gglobs.NAN           # set all to NAN

# get the new values for each device (if active)
    # gglobs.Devices : ("GMC", "Audio", "I2C", "RadMon", "AmbioMon", "LabJack", "Gamma-Scout",  "Raspi", "Simul")
    # e.g.: gglobs.Devices['GMC'][1]    : ['CPM', 'CPS']
    # e.g.: gglobs.Devices['RadMon'][1] : ['T', 'P', 'H', 'R']

    for devname in gglobs.Devices:
        #print("devname:", devname)
        if   devname == "GMC"           and gglobs.GMCConnection:
            logValue.update(gdev_gmc.GMCgetValues(gglobs.Devices[devname][1]))

        elif devname == "Audio"         and gglobs.AudioConnection:
            logValue.update(gdev_audio.getAudioValues(gglobs.Devices[devname][1]))

        elif devname == "RadMon"        and gglobs.RMConnection:
            logValue.update(gdev_radmon.getRadMonValues(gglobs.Devices[devname][1]))

        elif devname == "AmbioMon"      and gglobs.AmbioConnection:
            logValue.update(gdev_ambiomon.getAmbioValues(gglobs.Devices[devname][1]))

        elif devname == "Gamma-Scout"   and gglobs.GSConnection:
            logValue.update(gdev_scout.GSgetValues(gglobs.Devices[devname][1]))

        elif devname == "I2C"           and gglobs.I2CConnection:
            logValue.update(gdev_i2c.getI2CValues(gglobs.Devices[devname][1]))

        elif devname == "LabJack"       and gglobs.LJConnection:
            logValue.update(gdev_labjack.getLabJackValues(gglobs.Devices[devname][1]))

        elif devname == "Raspi"         and gglobs.RaspiConnection:
            logValue.update(gdev_raspi.getRaspiValues(gglobs.Devices[devname][1]))

        elif devname == "Simul"         and gglobs.SimulConnection:
            logValue.update(gdev_simul.getSimulCounterValues(gglobs.Devices[devname][1]))

        elif devname == "MiniMon"       and gglobs.MiniMonConnection:
            logValue.update(gdev_minimon.getMiniMonValues(gglobs.Devices[devname][1]))

# create the Log printstring and print to LogPad
    # Example: 1162 11:43:40   M=143  S=1  M1=  S1=  M2=128.0  S2=3.0  T=25.0  P=983.63  H=24.0  R=18.0
    # timetag: cut-off Date, use time only  '2018-07-14 12:00:52' --> '12:00:52'
    printstring = "{:2.7g} {:8s} " .format(gglobs.LogReadings, timetag[11:])
    for vname in gglobs.varsDefault:
        if gglobs.varcheckedLog[vname]:
            printstring     += " {}=".format(gglobs.varsBook[vname][1])
            #print(fncname + "vname, logValue[vname]: ", vname, logValue[vname])

            if not np.isnan(logValue[vname]):
                printstring += "{:<7.6g}".format(logValue[vname]) # can print 6 digit number as integer
                #~printstring += "{:<6.2f}".format(logValue[vname])
            else:
                printstring += " " * 6
    logPrint(printstring)
    gglobs.lastRecord   = printstring    # needed when a record was snapped
    #print("----------------printstring:", printstring)

# create the database insert and update in-memory data
    datalist     = [None] * (gglobs.datacolsDefault + 1) # (12 + 1) x None
    datalist[0]  = gglobs.LogReadings
    datalist[1]  = "NOW"

    # check for all data being nan
    nanOnly      = True
    for i, vname in enumerate(gglobs.varsBook):
        if not np.isnan(logValue[vname]):
            nanOnly         = False
            datalist[i + 2] = logValue[vname]
    #print("----------------datalist:", datalist)

    # save data, but only if at least one variable is not nan
    if not nanOnly:
        # Write to database
        gsup_sql.DB_insertData(gglobs.logConn, [datalist[0:2] + ["localtime"] + datalist[2:]])

        # update the logDBData array; time is set to matplotlib time
        gglobs.logDBData = np.append(gglobs.logDBData, \
                                                    [[
                                                      timeJulian - gglobs.JULIAN111, \
                                                      logValue["CPM"],    \
                                                      logValue["CPS"],    \
                                                      logValue["CPM1st"], \
                                                      logValue["CPS1st"], \
                                                      logValue["CPM2nd"], \
                                                      logValue["CPS2nd"], \
                                                      logValue["CPM3rd"], \
                                                      logValue["CPS3rd"], \
                                                      logValue["T"],      \
                                                      logValue["P"],      \
                                                      logValue["H"],      \
                                                      logValue["X"],      \
                                                    ]],    \
                                                    axis=0)

# update index (=LogReadings)
    gglobs.LogReadings += 1

# print get values&save duration
    gglobs.LogGetValDur = (time.time() - start)  * 1000
    vprint("{:<25s}{:0.1f} ms".format("get all values and save:", gglobs.LogGetValDur))

# reset cycle button color
    gglobs.exgg.dcycl.setStyleSheet("QPushButton {}")
    Qt_update()

# update the lastValues
    if gglobs.lastValues == None:           # occurs only right after start
        gglobs.lastValues = logValue
    else:
        for vname in gglobs.varsDefault:
            # update only if not nan
            if not np.isnan(logValue[vname]):  gglobs.lastValues[vname] = logValue[vname]
    #print("gglobs.lastValues:",gglobs.lastValues)

# update Value Displays
    gglobs.exgg.updateDisplayVariableValue()   # display lastValues
    Qt_update()

# before graph
    before = time.time()

# update graph, only if graph is the current one!
    if gglobs.activeDataSource == "Log":
        gglobs.currentDBData = gglobs.logDBData       # the data!
        gsup_plot.makePlot()                          # direct plot; slightly quicker than PlotGraph

# before graph: about 20ms with this: Connected: GMC( CPM CPS ); RadMon( T P H R ); Audio( CPM2nd CPS2nd );
# after  graph: about 90...140ms with this: Connected: GMC( CPM CPS ); RadMon( T P H R ); Audio( CPM2nd CPS2nd );
    #~vprint(fncname + "duration up to graph: {:5.1f} ms".format((before      - start)  * 1000))
    #~vprint(fncname + "duration for   graph: {:5.1f} ms".format((time.time() - before) * 1000))
    gglobs.LogPlotDur  = (time.time() - before)  * 1000
    gglobs.LogTotalDur = (time.time() - start)  * 1000

    vprint("{:<25s}{:0.1f} ms".format("Total get & plot:", (time.time() - start)  * 1000))

# relevant only when ESP32 is connected (maybe in conflict with other USB-To Serial devices!)
    #~readSerialConsole()

    setDebugIndent(0)

# end getLogValues##############################################################


def snapLogValue(event):
    """Take a measurement when toolbar icon Snap is clicked"""

    if not gglobs.logging: return

    fncname = "snapLogValue: "
    vprint(fncname)
    setDebugIndent(1)

    getLogValues()

    fprint(header("Snapped Log Values"))
    fprint(gglobs.lastRecord)
    vprint(fncname + gglobs.lastRecord)

    # comment to the DB
    ctype       = "COMMENT"
    cJulianday  = "NOW"
    cinfo       = "Snapped log values: {}".format(gglobs.lastRecord)
    gsup_sql.DB_insertComments(gglobs.logConn, [[ctype, cJulianday, "localtime", cinfo]])

    setDebugIndent(0)



def pushToWeb():
    """Send countrate info to web
    - Presently only the GMC website is supported
    """

    """
    Info on GMCmap:
    from: http://www.gmcmap.com/AutomaticallySubmitData.asp

    Auto submit data URL format:
    http://www.GMCmap.com/log2.asp?AID=UserAccountID&GID=GeigerCounterID &CPM=nCPM&ACPM=nACPM&uSV=nuSV
    At lease one reading data has to be submitted.
        UserAccountID:   user account ID. This ID is assigned once a user registration is completed.
        GeigerCounterID: a global unique ID for each registered Geiger Counter.
        nCPM:  Count Per Minute reading from this Geiger Counter.
        nACPM: Average Count Per Minute reading from this Geiger Counter(optional).
        nuSv:  uSv/h reading from this Geiger Counter(optional).

    Followings are valid data submission examples:
        http://www.GMCmap.com/log2.asp?AID=0230111&GID=0034021&CPM=15&ACPM=13.2&uSV=0.075
        http://www.GMCmap.com/log2.asp?AID=0230111&GID=0034021&CPM=15&ACPM=0&uSV=0
        http://www.GMCmap.com/log2.asp?AID=0230111&GID=0034021&CPM=15&ACPM=0&uSV=0
        http://www.GMCmap.com/log2.asp?AID=0230111&GID=0034021&CPM=15
        http://www.GMCmap.com/log2.asp?AID=0230111&GID=0034021&CPM=15&ACPM=13.2

    The submission result will be returned immediately. Followings are the returned result examples:
        OK.
        Error! User is not found.ERR1.
        Error! Geiger Counter is not found.ERR2.
        Warning! The Geiger Counter location changed, please confirm the location.
     """

    # Button and menu will be greyed out anyway; this can never be reached
    if gglobs.logging == False:
        efprint("Must be logging to update radiation maps")
        return

    # Dialog
    msgbox = QMessageBox()
    msgbox.setWindowIcon(gglobs.iconGeigerLog)
    msgbox.setIcon(QMessageBox.Warning)
    msgbox.setFont(gglobs.fontstd)
    msgbox.setWindowTitle("Updating Radiation World Maps")
    msgbox.setStandardButtons(QMessageBox.Ok)
    msgbox.setDefaultButton(QMessageBox.Ok)
    msgbox.setEscapeButton(QMessageBox.Ok)

    # Exit if no DataSource or His DataSource; need Log DataSource
    if gglobs.activeDataSource == None or gglobs.activeDataSource == "His":
        datatext = "Must show a Log Plot, not His Plot, to update Radiation Maps"
        msgbox.setText(datatext)
        retval = msgbox.exec_()
        return

    cpmdata = gglobs.logSlice["CPM"]
    #print("cpmdata:", cpmdata)
    ymask   = np.isfinite(cpmdata)      # mask for nan values
    cpmdata = cpmdata[ymask]
    #print("cpmdata:", cpmdata)

    lendata = len(cpmdata)
    CPM     = np.mean(cpmdata)
    ACPM    = CPM
    uSV     = CPM / gglobs.calibration1st

    #~# Defintions valid for cfgKeyHigh[key][0] (0=zero)
    #~# holding the definitions of the geigerlog,cfg file!
    #~data         = {}
    #~data['AID']  = cfgKeyHigh["UserID"][0]
    #~data['GID']  = cfgKeyHigh["CounterID"][0]
    #~data['CPM']  = "{:3.1f}".format(CPM)
    #~data['ACPM'] = data['CPM']
    #~data['uSV']  = "{:3.2f}".format(uSV)
    #~gmcmapURL    = cfgKeyHigh["Website"][0] + "/" + cfgKeyHigh["URL"][0]  + '?' + urllib.parse.urlencode(data)

    # Defintions valid for cfgKeyHigh[key][0] (0=zero)
    # holding the definitions of the geigerlog,cfg file!
    data         = {}
    data['AID']  = gglobs.GMCmapUserID
    data['GID']  = gglobs.GMCmapCounterID
    data['CPM']  = "{:3.1f}".format(CPM)
    data['ACPM'] = data['CPM']
    data['uSV']  = "{:3.2f}".format(uSV)
    gmcmapURL    = gglobs.GMCmapWebsite + "/" + gglobs.GMCmapURL + '?' + urllib.parse.urlencode(data)

    strdata = ""
    mapform = "   {:11s}: {}\n"
    strdata += mapform.format("CPM",        data['CPM'])
    strdata += mapform.format("ACPM",       data['ACPM'])
    strdata += mapform.format("uSV",        data['uSV'])
    strdata += mapform.format("UserID",     data['AID'])
    strdata += mapform.format("CounterID",  data['GID'])
    strdata  = strdata[:-1] # remove last linefeed

    # Dialog Confirm Sending
    #~datatext  = "Calling server: " + cfgKeyHigh["Website"][0] + "/" + cfgKeyHigh["URL"][0]
    datatext  = "Calling server: " + gglobs.GMCmapWebsite + "/" + gglobs.GMCmapURL
    datatext += "\nwith these data based on {} datapoints:\n\n".format(lendata)
    datatext += strdata + "\n\nPlease confirm with OK, or Cancel"
    msgbox.setText(datatext)
    msgbox.setStandardButtons(QMessageBox.Ok|QMessageBox.Cancel)
    msgbox.setDefaultButton(QMessageBox.Ok)
    msgbox.setEscapeButton(QMessageBox.Cancel)
    retval = msgbox.exec_()
    if retval != 1024:   return

    msg = "Updating Radiation World Maps"
    fprint(header(msg))
    dprint(msg + " - " +  gmcmapURL)
    setDebugIndent(1)

    # dprint the data which go to web
    for a in data:  dprint("{:5s}: {}".format(a, data[a]))

    try:
        with urllib.request.urlopen(gmcmapURL) as response:
            answer = response.read()
        dprint("Server Response: ", answer)
    except Exception as e:
        answer  = b"Bad URL"
        srcinfo = "Bad URL: " + gmcmapURL
        exceptPrint("pushToWeb: " + str(e), srcinfo)

    # possible gmcmap server responses:
    #   on proper credentials:                    b'\r\n<!--  sendmail.asp-->\r\n\r\nWarrning! Please update/confirm your location.<BR>OK.ERR0'
    #   on wrong credentials:                     b'\r\n<!--  sendmail.asp-->\r\n\r\nError! User not found.ERR1.'
    #   on proper userid but wrong counterid:     b'\r\n<!--  sendmail.asp-->\r\n\r\nError! Geiger Counter not found.ERR2.'
    #   something wrong in the data part of URL:  b'\r\n<!--  sendmail.asp-->\r\n\r\nError! Data Error!(CPM)ERR4.'

    # ERR0 = Ok
    if   b"ERR0" in answer:
        fprint("Successfully updated Radiation World Maps with these data:")
        fprint(strdata)
        fprint("Website response:", answer.decode('UTF-8'))

    # ERR1 or ERR2 - wrong userid  or wrong counterid
    elif b"ERR1" in answer or b"ERR2" in answer :
        efprint("Failure updating Radiation World Maps.")
        qefprint("Website response: ", answer.decode('UTF-8'))

    # misformed URL - wrong entry into config?
    elif b"Bad URL" in answer:
        efprint("Failure updating Radiation World Maps.")
        qefprint(" ERROR: ", "Bad URL: " + gmcmapURL)

    # other errors
    else:
        efprint("Unexpected response updating Radiation World Maps.")
        qefprint("Website response: ", answer.decode('UTF-8'))


    setDebugIndent(0)
