#! /usr/bin/env python3
# -*- coding: utf-8 -*-

"""
gdev_manu.py - GeigerLog commands to handle the manual entry of data
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
__copyright__       = "Copyright 2016, 2017, 2018, 2019, 2020, 2021, 2022"
__credits__         = [""]
__license__         = "GPL3"


from   gsup_utils       import *


def initManu():
    """Start the device"""

    fncname ="initManu: "
    dprint(fncname + "Initializing Manu Device")
    setDebugIndent(1)

    errmsg  = ""                            # what errors can be here?
    gglobs.Devices["Manu"][DNAME] = "GeigerLog " + "Manu"

    if gglobs.ManuVariables    == "auto": gglobs.ManuVariables    = "Temp, Press, Humid, Xtra"
    if gglobs.ManuSensitivity  == "auto": gglobs.ManuSensitivity  = 154               # CPM/(µSv/h), = 0.065 µSv/h/CPM
    if gglobs.ManuRecordStyle  == "auto": gglobs.ManuRecordStyle  = "Point"           # alt: Step

    # bring vars into order and make sure no more than 1 of each is present
    gglobs.ManuValues = 0
    ManuVars          = gglobs.ManuVariables.split(",")
    mvs               = ""
    for i, mv in enumerate(ManuVars):   ManuVars[i] = mv.strip() # remove blanks
    for vname in gglobs.varsCopy:
        if vname in ManuVars:
            mvs += "{}, ".format(vname)
            gglobs.ManuValues += 1
    gglobs.ManuVariables = mvs[:-2]

    setTubeSensitivities(gglobs.ManuVariables, gglobs.ManuSensitivity)
    setLoggableVariables("Manu", gglobs.ManuVariables)
    # edprint(fncname + " gglobs.ManuVariables: ",  gglobs.ManuVariables)

    # device is connected
    gglobs.Devices["Manu"][CONN] = True

    setDebugIndent(0)

    return errmsg


def terminateManu():
    """Stop the Manu counting"""

    fncname ="terminateManu: "

    dprint(fncname)
    setDebugIndent(1)

    gglobs.Devices["Manu"][CONN]  = False

    dprint(fncname + "Terminated")
    setDebugIndent(0)


def getValuesManu(varlist):
    """provide entered values"""

    start = time.time()
    fncname = "getValuesManu: "
    # print(fncname + "varlist: ", varlist)

    alldata = {}
    for i, vname in enumerate(varlist):
        alldata.update({vname:   gglobs.ManuValue[i]})                          # manually entered value#i
        if gglobs.ManuRecordStyle == "Point":
            gglobs.ManuValue[i] = gglobs.NAN  # reset after read-out

    printLoggedValues(fncname, varlist, alldata, (time.time() - start) * 1000)

    return alldata


def setManuValue():
    """Enter a value manually"""

    fncname = "setManuValue: "

    dprint(fncname)
    setDebugIndent(1)

    lv = [None] * gglobs.ManuValues
    v  = [None] * gglobs.ManuValues
    for i in range(gglobs.ManuValues):
        lv[i] = QLabel("Value #{:<2n} for Variable: {}".format(i + 1, gglobs.Devices["Manu"][VNAME][i]))
        lv[i].setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        v[i]  = QLineEdit()
        v[i].setToolTip("Enter a value manually for variable #{}".format(i))
        v[i].setText("")

    lvR = QLabel("Select Record Style")
    lvR.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
    rR1=QRadioButton("Point")
    rR1.setToolTip("A single point is drawn")
    rR2=QRadioButton("Step")
    rR2.setToolTip("The value is repeated until changed")
    enstyle = True if (gglobs.ManuRecordStyle == "Point" or gglobs.ManuRecordStyle == "auto") else False
    rR1.setChecked(enstyle)
    rR2.setChecked(not enstyle)
    rR1.setEnabled(True)
    rR2.setEnabled(True)
    rstylegroup = QButtonGroup()
    rstylegroup.addButton(rR1)
    rstylegroup.addButton(rR2)
    hboxR=QHBoxLayout()
    hboxR.addWidget(rR1)
    hboxR.addWidget(rR2)
    hboxR.addStretch()

    graphOptions=QGridLayout()
    graphOptions.setContentsMargins(10,10,10,10) # spacing around the graph options

    for i in range(gglobs.ManuValues):
        graphOptions.addWidget(lv[i],     i, 0)
        graphOptions.addWidget(v[i],      i, 1)

    graphOptions.addWidget(lvR,     i + 1, 0)
    graphOptions.addLayout(hboxR,   i + 1, 1)

    # Dialog box
    d = QDialog()
    d.setWindowIcon(gglobs.iconGeigerLog)
    d.setFont(gglobs.fontstd)
    d.setWindowTitle("Enter Manual Value")
    d.setWindowModality(Qt.WindowModal)
    d.setMinimumWidth(400)

    # Buttons
    bbox = QDialogButtonBox()
    bbox.setStandardButtons(QDialogButtonBox.Cancel | QDialogButtonBox.Ok )
    bbox.accepted.connect(lambda: d.done(1))
    bbox.rejected.connect(lambda: d.done(-1))

    gglobs.btn = bbox.button(QDialogButtonBox.Ok)
    gglobs.btn.setEnabled(True)

    layoutV = QVBoxLayout(d)
    layoutV.addLayout(graphOptions)
    layoutV.addWidget(bbox)

    retval = d.exec()
    #print("reval:", retval)

    if retval != 1:
        # ESCAPE pressed or Cancel Button
        dprint(fncname + "Canceling; no changes made")

    else:
        # OK pressed
        for i in range(gglobs.ManuValues):
            mval = v[i].text().strip().replace(",", ".")
            if mval > "":
                try:    nval = float(mval)
                except: nval = gglobs.NAN
                gglobs.ManuValue[i] = nval

        gglobs.forceSaving = True   # make MiniMon save even if not due for the other conditions

        if rR1.isChecked():     gglobs.ManuRecordStyle = "Point"
        else:                   gglobs.ManuRecordStyle = "Step"

        msg = ""
        for i in range(gglobs.ManuValues):
            msg += "Value #{:<2d} for Variable: {:6s} : {:0.3f}\n".format(i + 1, gglobs.Devices["Manu"][VNAME][i], gglobs.ManuValue[i])
        msg +=     "Record Style: {}\n".format(gglobs.ManuRecordStyle)

        fprint(header("Manual Values"))
        fprint(msg)
        dprint(msg.replace("\n", "  "))

    setDebugIndent(0)


def getInfoManu(extended = False):
    """Info on settings of the sounddev thread"""

    ManuInfo  = "Configured Connection:        GeigerLog Manu Device\n"
    if not gglobs.Devices["Manu"][CONN]: return ManuInfo + "Device is not connected"

    ManuInfo += "Connected Device:             '{}'\n"  .format(gglobs.Devices["Manu"][DNAME])
    ManuInfo += "Configured Variables:         {}\n"    .format(gglobs.ManuVariables)
    ManuInfo += "Configured Tube Sensitivity:  {:0.1f} CPM/(µSv/h) ({:0.4f} µSv/h/CPM)\n".format(gglobs.ManuSensitivity, 1 / gglobs.ManuSensitivity)

    if extended == True:
        ManuInfo += ""

    return ManuInfo

