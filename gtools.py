#!/usr/bin/python3
# -*- coding: UTF-8 -*-

"""
gtools.py - GeigerLog tools

include in programs with:
    include gtools
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
__copyright__       = "Copyright 2016, 2017, 2018, 2019, 2020"
__credits__         = [""]
__license__         = "GPL3"

from   gutils       import *

import urllib.request           # for use with Radiation World Map
import urllib.parse             # for use with Radiation World Map

import gsql
#import gaudio
import gsounddev

#~xt, yt, vline, zero, FitFlag, FitSelector = 0, 0, True, "None", True, 1
xt, yt, vline, zero, FitFlag, FitSelector = 0, 0, True, "None", True, "Prop"


def printSuSt():
    """Prints an overview of data from all variables"""


    if gglobs.logTimeSlice is None:
        gglobs.exgg.showStatusMessage("No data available")
        return

    fprint(header("Summary Statistics of Variables selected in Plot"))
    fprint("File      = {}".format(gglobs.currentDBPath))
    fprint("Filesize  = {:10,.0f} Bytes".format(os.path.getsize(gglobs.currentDBPath)))
    fprint("Records   = {:10,.0f} shown in Plot" .format(gglobs.logTimeSlice.size))

    fprint("          [Unit]      Avg  StdDev     Variance          Range         Last Value")
    for i, vname in enumerate(gglobs.varnames):
        if gglobs.varcheckedCurrent:
            try:
                fprint( gglobs.varlabels[vname])
            except:
                pass


def getlstats(logTime, logVar, vname):
    """get the text for the QTextBrowser in printStats"""

    vnameFull   = gglobs.vardict[vname][0]

    logSize          = logTime.size
    logtime_max      = logTime.max()
    logtime_min      = logTime.min()
    logtime_delta    = logtime_max - logtime_min # in days

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
        ltext.append("  Variance  ={:8.2f} {:8.2f}%"                                          .format(logVar_var,  logVar_var  / logVar_avg * 100.))
        ltext.append("  Std.Dev.  ={:8.2f} {:8.2f}%       LoLim={:8.2f}        HiLim={:8.2f}" .format(logVar_std,  logVar_std  / logVar_avg * 100.,  logVar_avg-logVar_std,         logVar_avg+logVar_std)  )
        ltext.append("  Sqrt(Avg) ={:8.2f} {:8.2f}%       LoLim={:8.2f}        HiLim={:8.2f}" .format(logVar_sqrt, logVar_sqrt / logVar_avg * 100.,  logVar_avg-logVar_sqrt,        logVar_avg+logVar_sqrt) )
        ltext.append("  Std.Err.  ={:8.2f} {:8.2f}%       LoLim={:8.2f}        HiLim={:8.2f}" .format(logVar_err,  logVar_err  / logVar_avg * 100.,  logVar_avg-logVar_err,         logVar_avg+logVar_err) )
        ltext.append("  Median    ={:8.2f} {:8.2f}%       P_5% ={:8.2f}        P_95%={:8.2f}" .format(logVar_med,  logVar_med  / logVar_avg * 100.,  np.nanpercentile(logVar, 5),   np.nanpercentile(logVar, 95)))
        ltext.append("  95% Conf*)={:8.2f} {:8.2f}%       LoLim={:8.2f}        HiLim={:8.2f}" .format(logVar_95,   logVar_95   / logVar_avg * 100.,  logVar_avg-logVar_95,          logVar_avg+logVar_95)   )
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

    gglobs.exgg.setBusyCursor()

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
    lstats.append("  Oldest rec    = {}  (time={:.3g} d)".format(oldest,   0))
    lstats.append("  Youngest rec  = {}  (time={:.3g} d)".format(youngest, logtime_max - logtime_min))
    lstats.append("  Duration      = {:.4g} s   ={:.4g} m   ={:.4g} h   ={:.4g} d".format(logtime_delta *86400., logtime_delta*1440., logtime_delta *24., logtime_delta))
    lstats.append("  Cycle average = {:0.2f} s".format(logtime_delta *86400./ (logSize -1)))
    lstats.append("="*100)

    for i, vname in enumerate(gglobs.varnames):
        if gglobs.varcheckedCurrent:
            try:
                logVar  = gglobs.logSliceMod[vname]     # var data
            except:
                continue
            getlstatstext =  getlstats(logTime, logVar, vname)
            lstats.append(getlstatstext)
            lstats.append("="*100)

    lstats.append("First and last few records:\n")
    sql, ruler = gsql.getShowCompactDataSql(gglobs.varcheckedCurrent)
    lstats.append(ruler)
    lstats.append(gglobs.exgg.getExcerptLines(sql, gglobs.currentConn, lmax=7))
    lstats.append(ruler)

    lstats.moveCursor(QTextCursor.Start)

    d = QDialog()
    d.setWindowIcon(gglobs.exgg.iconGeigerLog)
    d.setFont(gglobs.exgg.fontstd)
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

    gglobs.exgg.setNormalCursor()

    d.exec_()


def pushToWeb():
    """Send countrate info to website"""

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

    The submition result will be returned immediately. Followings are the returned result examples:
        OK.
        Error! User is not found.ERR1.
        Error! Geiger Counter is not found.ERR2.
        Warning! The Geiger Counter location changed, please confirm the location.
     """

    if gglobs.logging == False:
        fprint("Must be logging to update radiation maps", error=True, errsound=True)
        return

    if gglobs.activeDataSource == None or gglobs.activeDataSource == "His":
        # Dialog
        msg = QMessageBox()
        msg.setWindowIcon(gglobs.exgg.iconGeigerLog)
        msg.setIcon(QMessageBox.Warning)
        msg.setFont(gglobs.exgg.fontstd)
        msg.setWindowTitle("Updating Radiation World Maps")
        datatext = "Must show a Log Plot to update Radiation Maps"
        msg.setText(datatext)
        msg.setStandardButtons(QMessageBox.Ok)
        msg.setDefaultButton(QMessageBox.Ok)
        msg.setEscapeButton(QMessageBox.Ok)
        retval = msg.exec_()
        return

    cpmdata = gglobs.logSlice["CPM"]
    #print("cpmdata:", cpmdata)
    ymask   = np.isfinite(cpmdata)      # mask for nan values
    cpmdata = cpmdata[ymask]
    #print("cpmdata:", cpmdata)

    lendata = len(cpmdata)
    CPM     = np.mean(cpmdata)
    ACPM    = CPM

    if gglobs.calibration1st == "auto":
        uSV = 0
    else:
        uSV = CPM / gglobs.calibration1st  # gglobs.calibration1st, 2nd, 3rd may be 'auto' if no device connected!
    #~print("gglobs.calibration1st:", gglobs.calibration1st, "CPM:", CPM, "ACPM:", ACPM, "uSV:", uSV)

    #Defintions valid only for GMCmap.com
    data         = {}
    data['AID']  = gglobs.GMCmap["UserID"]
    data['GID']  = gglobs.GMCmap["CounterID"]
    data['CPM']  = "{:3.1f}".format(CPM)
    data['ACPM'] = data['CPM']
    data['uSV']  = "{:3.2f}".format(uSV)
    gmcmapURL    = gglobs.GMCmap["Website"] + "/" + gglobs.GMCmap["URL"]  + '?' + urllib.parse.urlencode(data)

    strdata = ""
    mapform = "   {:11s}: {}\n"
    strdata += mapform.format("CPM",        data['CPM'])
    strdata += mapform.format("ACPM",       data['ACPM'])
    strdata += mapform.format("uSV",        data['uSV'])
    strdata += mapform.format("UserID",     data['AID'])
    strdata += mapform.format("CounterID",  data['GID'])
    strdata  = strdata[:-1] # remove last linefeed

    # Dialog Confirm Sending
    msg = QMessageBox()
    msg.setWindowIcon(gglobs.exgg.iconGeigerLog)
    msg.setIcon(QMessageBox.Information)
    msg.setFont(gglobs.exgg.fontstd)
    msg.setWindowTitle("Updating Radiation World Maps")
    datatext = "Calling server: " + gglobs.GMCmap["Website"] + "/" + gglobs.GMCmap["URL"]
    datatext += "\nwith these data based on {} datapoints:                                          \n\n".format(lendata)
    datatext += strdata + "\n\nPlease confirm with OK, or Cancel"
    msg.setText(datatext)
    msg.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
    msg.setDefaultButton(QMessageBox.Cancel)
    msg.setEscapeButton(QMessageBox.Cancel)
    retval = msg.exec_()
    if retval != 1024:   return

    fprint(header("Updating Radiation World Maps"))

    dprint("Updating Radiation World Maps - " +  gmcmapURL)
    for a in ("AID", "GID", "CPM", "ACPM", "uSV"): # ordered print
        dprint("{:5s}: {}".format(a, data[a]))

    try:
        with urllib.request.urlopen(gmcmapURL) as response:
            answer = response.read()
        dprint("Server Response:", answer)
    except Exception as e:
        answer  = b"Bad URL"
        srcinfo = "Bad URL: " + gmcmapURL
        exceptPrint(e, sys.exc_info(), srcinfo)

    # gmcmap server responses:
    # on proper credentials:                    b'\r\n<!--  sendmail.asp-->\r\n\r\nWarrning! Please update/confirm your location.<BR>OK.ERR0'
    # on wrong credentials:                     b'\r\n<!--  sendmail.asp-->\r\n\r\nError! User not found.ERR1.'
    # on proper userid but wrong counterid:     b'\r\n<!--  sendmail.asp-->\r\n\r\nError! Geiger Counter not found.ERR2.'
    # something wrong in the data part of URL:  b'\r\n<!--  sendmail.asp-->\r\n\r\nError! Data Error!(CPM)ERR4.'

    # ERR0 = 0k
    if   b"ERR0" in answer:
        fprint("Successfully updated Radiation World Maps with these data:")
        fprint(strdata)
        fprint("Website says:")
        fprint(answer.decode('UTF-8'))

    # ERR1 or ERR2 - wrong userid  or wrong counterid
    elif b"ERR1" in answer or b"ERR2" in answer :
        fprint("Failure updating Radiation World Maps. Website says:")
        efprint(answer.decode('UTF-8'))

    # misformed URL - programming error
    elif b"Bad URL" in answer:
        fprint("Failure updating Radiation World Maps. ERROR:")
        efprint("Bad URL: " + gmcmapURL)

    # other errors
    else:
        fprint("Unexpected response updating Radiation World Maps; Website says:")
        efprint(answer.decode('UTF-8'))


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
    for i, vname in enumerate(gglobs.varnames):
        if gglobs.varcheckedCurrent[vname]:
            #~print("gglobs.varcheckedCurrent[vname]: ", vname,  gglobs.varcheckedCurrent[vname])
            xlist.addItem(gglobs.vardict[vname][0])
            ylist.addItem(gglobs.vardict[vname][0])

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

    layoutT.addWidget(checkb)
    layoutT.addStretch()

    # add polynomial fit?                         default is yes
    checkF = QCheckBox("Add Polynomial Fit   of order:")
    checkF.setChecked(FitFlag)

    # selector for order of fit                   default is 1st order = linear
    cboxF = QComboBox()
    cboxF.addItems(["Prop", "0", "1", "2", "3", "4", "5", "6", "7"])
    cboxF.setMaximumWidth(70)
    cboxF.setToolTip('Select the degree of the polynomial fit')
    #~print("-------------FitSelector: ", FitSelector)

    if FitSelector == "Prop":
        cboxF.setCurrentIndex(0)
    else:
        cboxF.setCurrentIndex(int(FitSelector) + 1)

    layoutF = QHBoxLayout()
    layoutF.addWidget(checkF)
    layoutF.addWidget(cboxF)
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
    d.setWindowIcon(gglobs.exgg.iconGeigerLog)
    d.setFont(gglobs.exgg.fontstd)
    d.setWindowTitle("Select Variables for Scatter Plot")
    d.setWindowModality(Qt.ApplicationModal)
    d.setMinimumHeight(350)
    #d.setWindowModality(Qt.NonModal)
    #d.setWindowModality(Qt.WindowModal)
    d.setStyleSheet("QLabel { background-color:#DFDEDD; color:rgb(40,40,40); font-size:30px; font-weight:bold;}")

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
    FitSelector = cboxF.currentText()

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

    localvardict = gglobs.vardict
    localvardict.update( {'time' : ('time [d]', 'time') } )

    if vx == "time":
        x0 = gglobs.logTimeDiffSlice
    else:
        try:
            x0 = gglobs.logSlice[vx]
        except Exception as e:
            fprint(header("Plot Scatter"))
            fprint("ERROR in plotScatter: Exception: e:", e)
            return

    if vy == "time":
        y0 = gglobs.logTimeDiffSlice
    else:
        try:
            y0 = gglobs.logSlice[vy]
        except Exception as e:
            fprint(header("Plot Scatter"))
            fprint("ERROR in plotScatter: Exception: e:", e)
            return

    ymask                   = np.isfinite(y0)      # mask for nan values
    y1                      = y0[ymask]
    x1                      = x0[ymask]

    xmask                   = np.isfinite(x1)      # mask for nan values
    y                       = y1[xmask]
    x                       = x1[xmask]

    if y.size > 0:  plotstyle['markersize'] = float(plotstyle['markersize']) / np.sqrt(y.size)
    else:           plotstyle['markersize'] = 3

    fig2 = plt.figure(facecolor = "#E7F9C9")
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
    labout.setFont(gglobs.exgg.fontstd)
    labout.setMinimumHeight(210)
    txtlines  = "Connecting lines are {}drawn".format("" if vline else "not ")
    txtorigin = "an origin of zero is enforced for {}".format(zero)
    labout.setText("Scatter Plot of y = {} versus x = {}.".format(localvardict[vy][0], localvardict[vx][0]))
    labout.append("{}; {}.".format(txtlines, txtorigin))

    d = QDialog()
    gglobs.plotScatterPointer = d
    d.setWindowIcon(gglobs.exgg.iconGeigerLog)
    d.setWindowTitle("Scatter Plot")
    #d.setWindowModality(Qt.ApplicationModal)
    #d.setWindowModality(Qt.NonModal)
    d.setWindowModality(Qt.WindowModal)

    okButton = QPushButton("OK")
    okButton.setCheckable(True)
    okButton.setAutoDefault(True)
    okButton.clicked.connect(lambda:  d.done(0))

    selectButton = QPushButton("Select")
    selectButton.setCheckable(True)
    selectButton.setAutoDefault(False)
    selectButton.clicked.connect(lambda:  nextScatterPlot())

    bbox = QDialogButtonBox()
    bbox.addButton(okButton,                QDialogButtonBox.ActionRole)
    bbox.addButton(selectButton,            QDialogButtonBox.ActionRole)

    layoutH = QHBoxLayout()
    layoutH.addWidget(bbox)
    layoutH.addWidget(navtoolbar)
    layoutH.addStretch()
    layoutH.addStretch()        # not enough with single stretch !!!

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
        if FitSelector != "Prop":
            pfit = np.polyfit(x, y, int(FitSelector))
            dprint("plotScatter: pfit: ", pfit)
            for i,f in enumerate(np.flip(pfit)):
                labout.append("#{:d} : {: .4g}".format(i, f))

            p  = np.poly1d(pfit)
            xs = sorted(x)
            plt.plot(xs, p(xs), color="red", marker=None, linestyle="solid", linewidth=2)
        else:
            def func(x, a):
                return a * x

            from scipy.optimize import curve_fit
            popt, pcov = curve_fit(func, x, y)
            dprint("plotScatter: curve_fit: popt, pcov, perr: ", popt, pcov, np.sqrt(np.diag(pcov)))
            labout.append("#0 : {: .4g} (Prop)".format(0))
            labout.append("#1 : {: .4g}".format(popt[0]))

            #~plt.plot(x, func(x, *popt), color="green", marker=None, linestyle="solid", linewidth=2)
            plt.plot(x, func(x, *popt), color="red", marker=None, linestyle="solid", linewidth=2)


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


def plotAudio(dtype="Single Pulse", duration=None):
    """Plotting an audio plot"""

    fncname = "plotAudio: "

    #~data = gglobs.AudioMultiPulses
    data = gglobs.AudioPlotData
    #print(fncname + "dtype:{}, data:{}".format(dtype, data))
    #print(fncname + "dtype: {}".format(dtype))

    # if a recording, then crop it otherwise next Multi will show recording space
    # doesn't this curt recordings also??????
    #~if len(data) > 40 * (gglobs.AudioChunk +10):
        #~gglobs.AudioMultiPulses = gglobs.AudioMultiPulses[-(gglobs.AudioChunk + 10):]

    subTitle = dtype
    #~flag     = False

    #~if data is None :
        #~data     = [0] * gglobs.AudioChunk
        #~subTitle = "No data"
        #~flag     = True

    #~else:
    #~if dtype == "Toggle": dtype = "Multi Pulse"

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

    fig2 = plt.figure(99, facecolor = "#E7F9C9")
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

    labout = QTextBrowser()                       # label to hold the description
    labout.setFont(gglobs.exgg.fontstd)           # my std font for easy formatting
    labout.setText("")

    mtext1  =   "Device:           Input:'{}', Output:'{}'" .format(sd.default.device[0], sd.default.device[1])
    mtext1 += "\nSample Format:    {}"                      .format(gglobs.AudioFormat)
    mtext1 += "\nSampled Channels: {} (1=Mono, 2=Stereo)"   .format(gglobs.AudioChannels)
    mtext1 += "\nSampling rate:    {} per second"           .format(gglobs.AudioRate)
    mtext1 += "\nSamples:          {} per read"             .format(gglobs.AudioChunk)
    mtext1 += "\nPulse Height Max: ±{} "                    .format(gglobs.AudioPulseMax)
    mtext1 += "\nPulse Threshold:  {} %"                    .format(gglobs.AudioThreshold)
    mtext1 += "\nPulse Direction:  {} "                     .format(("POSITIVE" if gglobs.AudioPulseDir else "NEGATIVE"))

    #~if flag:
        #~labout.append("No data; is the AudioCounter Device connected? Try the Recording button")
    #~else:
    if   dtype == "Single Pulse":
        labout.append("Showing the last detected AudioCounter pulse")
        #~labout.append(mtext1)

    elif dtype == "Multi Pulse":
        labout.append("Showing the last (up to 40) detected AudioCounter pulses")
        #~labout.append(mtext1)

    elif dtype == "Recording":
        #~if duration == 0:
            #~labout.append("FAILURE - try the Recording button again")
        #~else:
        labout.append("Showing a straight recording of {} second - no pulse detection applied".format(duration))
        #~labout.append(mtext1)

    labout.append(mtext1)

        #~else:
            #~subTitle = "programming error - undefined dtype: '{}'".format(dtype)
            #~labout.append(subTitle)

    d = QDialog()
    gglobs.plotAudioPointer = d
    d.setWindowIcon(gglobs.exgg.iconGeigerLog)
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
    singleButton.clicked.connect(lambda: reloaddata("Single Pulse"))

    multiButton = QPushButton("Multi Pulse")
    multiButton.setCheckable(True)
    multiButton.setAutoDefault(False)
    multiButton.clicked.connect(lambda: reloaddata("Multi Pulse"))

    recordButton = QPushButton("Recording")
    recordButton.setCheckable(True)
    recordButton.setAutoDefault(False)
    recordButton.clicked.connect(lambda: reloaddata("Recording"))

    togglePulseDirButton = QPushButton("Toggle Pulse Direction")
    togglePulseDirButton.setCheckable(True)
    togglePulseDirButton.setAutoDefault(False)
    togglePulseDirButton.clicked.connect(lambda: reloaddata("Toggle"))

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


def reloaddata(dtype):
    """closes the dialog and reopens"""

    #print("reloaddata: ", dtype)

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
        gglobs.exgg.setBusyCursor()
        duration = 1 # seconds
        #gsounddev.getLongChunk(duration)
        gglobs.AudioPlotData = gglobs.AudioRecording
        gglobs.exgg.setNormalCursor()

    else: # dtype == "Toggle":
        gsounddev.toggleSounddevPulseDir()
        dtype = "Recording"
        duration = 1 # seconds
        #~gglobs.AudioPlotData = gglobs.AudioMultiPulses[-(gglobs.AudioChunk):] # last pulse only without nan
        gglobs.AudioMultiPulses = np.array([0]) # set to empty as old pulses do not make sense
        gglobs.AudioPlotData    = gglobs.AudioRecording

    plotAudio(dtype, duration)


def displayLastValues(self):
    """Displays the last values in big letters"""
    # For the updating see updateDisplayVariableValue()

    # print("+++++++++++++++++++++++++++++++++++++displayLastValues was called")

    if gglobs.logConn == None:          return
    if gglobs.displayLastValuesIsOn :   return
    if gglobs.lastValues == None:       return

    gglobs.displayLastValuesIsOn = True

    d = QDialog()
    d.setWindowIcon(gglobs.exgg.iconGeigerLog)
    d.setFont(gglobs.exgg.fontstd)
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
    klabels = [None] * len(gglobs.varnames)   # variable names
    dlabels = [None] * len(gglobs.varnames)   # device names
    vlabels = [None] * len(gglobs.varnames)   # variable values
    #print("gglobs.DevicesNames:", gglobs.DevicesNames)
    #print("gglobs.DevicesVars:", gglobs.DevicesVars)

    t1 = QLabel("Variable")
    t1.setStyleSheet("QLabel {color: #111111; font-size:20px; font-weight:bold;}")
    t2 = QLabel("Device")
    t2.setStyleSheet("QLabel {color: #111111; font-size:20px; font-weight:bold; qproperty-alignment:AlignCenter;}")
    t3 = QLabel("Value")
    t3.setStyleSheet("QLabel {color: #111111; font-size:20px; font-weight:bold; qproperty-alignment:AlignCenter;}")
    #~ t3.setStyleSheet("QLabel {color: #111111; font-size:20px; font-weight:bold; qproperty-alignment:AlignRight;}")
    gridlo.addWidget(t1,    0, 0)
    gridlo.addWidget(t2,    0, 1)
    gridlo.addWidget(t3,    0, 2)
    gridlo.setColumnStretch(2, 1) # give more space to value col

    for i, vname in enumerate(gglobs.varnames):
           #print("---i, vname:", i, vname)
            klabels[i] = QLabel(gglobs.vardict[vname][0])
            klabels[i].setFont((QFont("Sans", 12, weight=QFont.Bold)))
            dlabels[i] = QLabel(" ")

            if not gglobs.varcheckedLog[vname]:
                val = "{:>18s}".format("not mapped")
            else:
                #if not np.isnan(gglobs.lastValues[vname][0]):
                if not np.isnan(gglobs.lastValues[vname]):
                    #val = "{:>8.2f}".format(gglobs.lastValues[vname][0])
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

            for dname in gglobs.DevicesNames:
                #print("dname:", dname, ", vname:", vname)
                if not gglobs.DevicesVars[dname] is None:
                    if vname in gglobs.DevicesVars[dname]:
                        dlabels[i] = QLabel(dname)
                dlabels[i].setAlignment(Qt.AlignCenter)
                dlabels[i].setStyleSheet("QLabel {color:#111111; font-size:14px;}")

            gridlo.addWidget(klabels[i],             i + 1, 0)
            gridlo.addWidget(dlabels[i],             i + 1, 1)
            gridlo.addWidget(gglobs.exgg.vlabels[i], i + 1, 2)

    layoutV.addLayout(gridlo)

    layoutV.addWidget(bbox)

    d.exec_()
    gglobs.displayLastValuesIsOn = False


def printPlotData():
    """Print Data as selected in Plot. Data are taken from the plot, not from
    the database!"""

    t0 = gglobs.logTimeSlice

    if t0 is None or len(t0) == 0:
        gglobs.exgg.showStatusMessage("No data available")
        return

    gglobs.exgg.setBusyCursor()

    header = "{:5s}, {:19s}".format("#No", "Datetime")
    for vname in gglobs.varnames:
        if gglobs.exgg.varDisplayCheckbox[vname].isChecked():
            header += ", {:>8s}".format(vname)

    fprint(header)
    for i in range(len(t0)):
        vcc = "{:>5d}, {:<19s}".format(i, str(mpld.num2date(t0[i]))[:19])
        for vname in gglobs.varnames:
            if gglobs.exgg.varDisplayCheckbox[vname].isChecked():
                vi = gglobs.logSlice[vname][i]
                if np.isnan(vi):
                    vcc += ", {:>8s}".format(" ")
                else:
                    vcc += ", {:>8.2f}".format(gglobs.logSlice[vname][i])
        fprint(vcc)
    fprint(header)

    gglobs.exgg.setNormalCursor()
