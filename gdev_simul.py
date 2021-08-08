#! /usr/bin/env python3
# -*- coding: utf-8 -*-

"""
gdev_simul.py - GeigerLog commands to handle the simul device, which simulates
                counts using a synthetic Poisson number generator
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


"""
from the config file; currently not used

################ NOT IN USE ###################################################
# SimulCounter PREDICTIVE
# Determines whether CPM is let to accumulate or a prediction is made after
# first counts.
#
# Option auto defaults to 'no'
#
# Options:        auto | yes | no
# Default       = auto
#~SimulPredictive   = auto
SimulPredictive   = no


# SimulCounter PREDICTLIMIT
# Sets the count limit which CPM must have reached before a first CPM-prediction
# is given. Before CPM will be reported as NAN.
# Statistical certainty from Std.Dev = Sqrt(N) (valid for Poisson):
# CPM =  10:   ~30%
# CPM =  25:    20%
# CPM = 100:    10%
#
# Option auto defaults to 25
#
# Options:          auto | <any number >= 0 >
# Default         = auto
SimulPredictLimit = auto
###############################################################################
"""



import ntplib


def getNTPDateTime(NTPversion = 4):
    """Call NTP server and return offset in seconds as reported by NTP"""
    # typical offset is in the order of 10 milli second (offset = +/- 0.010

    # latest NTP version is now: 4;     working versions are 2, 3, 4 (not 1!)
    # https://www.eecis.udel.edu/~mills/ntp/html/release.html
    #
    # ntplib: def request(self, host, version=2, port='ntp', timeout=5):
    #
    # NTP document by IETF:       https://tools.ietf.org/html/rfc5905
    # see: page 23, Figure 7 for functions, and ff for details
    #
    # Reference Timestamp:
    # Time when the system clock was last set or corrected, in NTP timestamp format.
    #
    # Origin Timestamp (org):
    # Time at the client when the request departed for the server, in NTP timestamp format.
    #
    # Receive Timestamp (rec):
    # Time at the server when the request arrived from the client, in NTP timestamp format.
    #
    # Transmit Timestamp (xmt):
    # Time at the server when the response left for the client, in NTP timestamp format.
    #
    # Destination Timestamp (dst):
    # Time at the client when the reply arrived from the server, in NTP timestamp format.

    NTP_SERVERS = [ #'pool.ntp.org',
                    #'asia.pool.ntp.org',
                    #~'oceania.pool.ntp.org',
                    #'north-america.pool.ntp.org',
                    #~'south-america.pool.ntp.org',
                    #'europe.pool.ntp.org',
                    'de.pool.ntp.org',
                    #~'0.de.pool.ntp.org',
                    #~'1.de.pool.ntp.org',
                    #~'2.de.pool.ntp.org',
                    #~'3.de.pool.ntp.org',
                    #~'uk.pool.ntp.org',
                    #~'0.uk.pool.ntp.org',
                  ]

    fncname     = "getNTPDateTime: "
    vprint(fncname)
    setDebugIndent(1)
    orig = recv = dest = offset = gglobs.NAN

    client = ntplib.NTPClient()
    for ntpserver in NTP_SERVERS:
        ntps     = []
        try:
            response = client.request(ntpserver, version=NTPversion, timeout=0.2)
        except Exception as e:
            msg = fncname + "NTPversion:{} ".format(NTPversion)
            exceptPrint(e, msg)
            setDebugIndent(0)
            #return gglobs.NAN
            continue

        #print("response.orig_time: ", response.orig_time) # like: 1614266943.3662605

        orig   = response.orig_time     # all times in seconds
        recv   = response.recv_time
        tx     = response.tx_time
        dest   = response.dest_time
        offset = response.offset

        ntps.append( ["orig"     , orig - orig]) # always zero
        ntps.append( ["recv"     , recv - orig])
        ntps.append( ["tx  "     , tx   - orig])
        ntps.append( ["dest"     , dest - orig])
        ntps.append( ["offset"   , offset])
        #ntps.append( ["calc offset"   , ((recv - orig) + (tx - dest)) / 2])

        # vprint for each server
        if gglobs.verbose:
            for  a in ntps: vprint("NTP Version: {}  {:20s}  {:15s}  {:10.3f} ".format(NTPversion, ntpserver, a[0], a[1]))
            print("")

    setDebugIndent(0)

    return offset # offset in seconds


# NTP
###############################################################################
# SimulCounter


def initSimulCounter():
    """Start the simulator"""

    global cps_record, SimulCounterCalls

    fncname ="initSimulCounter: "

    dprint(fncname + "Initialzing SimulCounter")
    setDebugIndent(1)

    errmsg  = "" # what errors can be here?
    gglobs.SimulDeviceName      = "SimulCounter"
    gglobs.SimulDeviceDetected  = gglobs.SimulDeviceName # no difference so far
    gglobs.Devices["Simul"][0]  = gglobs.SimulDeviceDetected

    if gglobs.SimulMean         == "auto": gglobs.SimulMean         = 0.3                       # "background"
    if gglobs.SimulSensitivity  == "auto": gglobs.SimulSensitivity  = 154                       # CPM/(µSv/h), = 0.065 µSv/h/CPM
    if gglobs.SimulVariables    == "auto": gglobs.SimulVariables    = "CPM, CPS"                # non-predictive;
    #if gglobs.SimulPredictive   == "auto": gglobs.SimulPredictive   = False                     # let CPM accumulate
    #if gglobs.SimulPredictLimit == "auto": gglobs.SimulPredictLimit = 25                        # CPM prediction after this count was reached

    setCalibrations(gglobs.SimulVariables, gglobs.SimulSensitivity)
    setLoggableVariables("Simul", gglobs.SimulVariables)

    gglobs.SimulConnection = True

    np.random.seed(int(time.time()))               # seed the random number generator
    cps_record        = np.full(60, gglobs.NAN)    # for storing last 60 sec of CPS values, fill with NANs
    SimulCounterCalls = 0                          # how many times the get data routine was called

    setDebugIndent(0)

    return errmsg


def terminateSimulCounter():
    """Stop the SimulCounter"""

    fncname ="terminateSimulCounter: "
    if not gglobs.SimulConnection: return fncname + "No SimulCounter connection"

    dprint(fncname)
    gglobs.SimulConnection = False


def xxxxxxxx___getSimulCounterValues(varlist):
    """Read all data; return empty dict when not available"""

    global cps_record, SimulCounterCalls

    fncname = "getSimulCounterValues: "
    alldata = {}

    # take as many samples as the logcycle has sec to cover full cps
    size               = int(max(1, gglobs.logcycle))
    simulcps           = np.random.poisson(gglobs.SimulMean, size=size) # generates the "CPS counts"
    cps_record         = np.append(cps_record, simulcps)[-60:]          # append, but take last 60 values only
    SimulCounterCalls += size
    #~print("--------size: ", size, ", simulcps:", simulcps)
    #~print("cps_record: nansum", np.nansum(cps_record), "cps_record:\n", cps_record)

    for vname in varlist:
        if   vname in ("CPM"):
        # CPM non-predictive
            cpm             = int(np.nansum(cps_record))        # must use int or blob will be stored
            cpm             = round(scaleVarValues(vname, cpm, gglobs.ValueScale[vname]), 2)
            alldata.update(  {vname: cpm})

        elif   vname in ("CPM1st"):
        # CPM1st trying the GQ Fast Estimate Time
            cpm             = np.nanmean(cps_record[-3:]) # 1ast 3
            cpm             = int(cpm * 60)
            cpm             = round(scaleVarValues(vname, cpm, gglobs.ValueScale[vname]), 2)
            alldata.update(  {vname: cpm})

        elif vname in ("T"):
        # old: T as (NTP time offset in ms), NTPversion=2
        # T as (NTP time offset in ms), NTPversion=4
            #~t             = getNTPDateTime(NTPversion=2) * 1000
            t             = getNTPDateTime(NTPversion=4) * 1000
            t             = round(scaleVarValues(vname, t, gglobs.ValueScale[vname]), 2)
            alldata.update(  {vname: t})


        elif vname in ("P"):
        # P as (NTP time offset in ms), NTPversion=3
            x             = getNTPDateTime(NTPversion=3) * 1000
            x             = round(scaleVarValues(vname, x, gglobs.ValueScale[vname]), 2)
            alldata.update(  {vname: x})


        elif vname in ("H"):
        # H as (NTP time offset in ms), NTPversion=3
            x             = getNTPDateTime(NTPversion=3) * 1000
            x             = round(scaleVarValues(vname, x, gglobs.ValueScale[vname]), 2)
            alldata.update(  {vname: x})


        elif vname in ("X"):
        # X as (NTP time offset in ms), NTPversion=4
            x             = getNTPDateTime(NTPversion=4) * 1000
            x             = round(scaleVarValues(vname, x, gglobs.ValueScale[vname]), 2)
            alldata.update(  {vname: x})

        elif vname in ("CPS", "CPS1st", "CPS2nd", "CPS3rd"):
        # CPS - predictive not relevant here
            cps             = int(cps_record[-1])       # must use int or blob will be stored
            cps             = round(scaleVarValues(vname, cps, gglobs.ValueScale[vname] ))
            alldata.update(  {vname: cps})

        elif vname in ("CPM2nd", "CPM3rd"):
        # CPM - predictive
            #~limit   4 --> 50% Stddev
            #~limit  11 --> 30% Stddev
            #~limit  25 --> 20% Stddev
            #~limit 100 --> 10% Stddev

            continue # to not use predictive

            cpm             = int(np.nansum(cps_record)) # must use int or 'blob' will be stored in db
            # make the prediction but only while not a full 60 secs counted
            if SimulCounterCalls < 60:
                if cpm <= gglobs.SimulPredictLimit: cpm = gglobs.NAN
                else:                               cpm = int(cpm / SimulCounterCalls * 60)
            else:
                c1mean = np.nanmean(cps_record[:30]) # 1st 30
                c1stdd = np.nanstd (cps_record[:30])
                c2mean = np.nanmean(cps_record[30:]) # last 30
                c2stdd = np.nanstd (cps_record[30:])
                print("Predict: c1mean: ", c1mean, ", c2mean: ", c2mean)
                print("Predict: c1stdd: ", c1stdd, ", c2stdd: ", c2stdd)
                if abs(c1mean - c2mean) > (c1stdd + c2stdd):
                    cpm = int((c2mean * 30) / 30 * 60)

            cpm             = round(scaleVarValues(vname, cpm, gglobs.ValueScale[vname]), 2)
            alldata.update(  {vname: cpm})
            #~#if gglobs.SimulCounterCalls < 70: print("----------------gglobs.SimulCounterCalls   : ", gglobs.SimulCounterCalls,    " CPM: ", cpm)
            #if gglobs.SimulCounterCalls < 70: print("---------------- SimulCounterCalls   : ", SimulCounterCalls,    " CPM: ", cpm)

    printLoggedValues(fncname, varlist, alldata)

    return alldata



def getSimulCounterValues(varlist):
    """Read all data; return empty dict when not available"""

    global cps_record, SimulCounterCalls

    fncname = "getSimulCounterValues: "
    alldata = {}

    # take as many samples as the logcycle has sec to cover full cps
    size               = int(max(1, gglobs.logcycle))
    simulcps           = np.random.poisson(gglobs.SimulMean, size=size) # generates the "CPS counts"
    cps_record         = np.append(cps_record, simulcps)[-60:]          # append, but take last 60 values only
    SimulCounterCalls += size
    #~print("--------size: ", size, ", simulcps:", simulcps)
    #~print("cps_record: nansum", np.nansum(cps_record), "cps_record:\n", cps_record)

    for vname in varlist:
        if   vname in ("CPM", "CPM1st", "CPM2nd", "CPM3rd"):
        # CPM
            cpm             = int(np.nansum(cps_record))        # must use int or blob will be stored
            cpm             = round(scaleVarValues(vname, cpm, gglobs.ValueScale[vname]), 2)
            alldata.update(  {vname: cpm})

        elif vname in ("CPS", "CPS1st", "CPS2nd", "CPS3rd"):
        # CPS
            cps             = int(cps_record[-1])               # must use int or blob will be stored
            cps             = round(scaleVarValues(vname, cps, gglobs.ValueScale[vname] ))
            alldata.update(  {vname: cps})

        elif vname in ("T"):
        # old: T as (NTP time offset in ms), NTPversion=2
        # T as (NTP time offset in ms), NTPversion=4
            #~t             = getNTPDateTime(NTPversion=2) * 1000
            t             = getNTPDateTime(NTPversion=4) * 1000 # in milli-seconds
            t             = round(scaleVarValues(vname, t, gglobs.ValueScale[vname]), 2)
            alldata.update(  {vname: t})

    printLoggedValues(fncname, varlist, alldata)

    return alldata


def getSimulProperties():
    """Set mean and predictive limit"""

    fncname = "getSimulProperties: "
    dprint(fncname)
    setDebugIndent(1)

    lmean = QLabel("CPS Mean\n(0 ... 10000)")
    lmean.setAlignment(Qt.AlignLeft)
    mean = QLineEdit()
    mean.setToolTip('The mean of the Poisson distribution for the CPS variable')
    mean.setText("{:0.3g}".format(gglobs.SimulMean))

    lplimit = QLabel("Prediction Limit\n(not negative)")
    lplimit.setAlignment(Qt.AlignLeft)
    plimit  = QLineEdit()
    plimit.setToolTip('The limit for prediction')
    plimit.setText("{:0.3g}".format(gglobs.SimulPredictLimit))

    graphOptions=QGridLayout()
    graphOptions.addWidget(lmean,           0, 0)
    graphOptions.addWidget(mean,            0, 1)
    #~graphOptions.addWidget(lplimit,         1, 0)
    #~graphOptions.addWidget(plimit,          1, 1)

    d = QDialog() # set parent to None to popup in center of screen
    d.setWindowIcon(gglobs.iconGeigerLog)
    d.setFont(gglobs.fontstd)
    d.setWindowTitle("SimulCounter Properties")
    d.setWindowModality(Qt.ApplicationModal)
    #d.setWindowModality(Qt.NonModal)
    #d.setWindowModality(Qt.WindowModal)
    d.setMinimumWidth(300)

    bbox = QDialogButtonBox()
    bbox.setStandardButtons(QDialogButtonBox.Cancel | QDialogButtonBox.Ok )
    bbox.accepted.connect(lambda: d.done(100))
    bbox.rejected.connect(lambda: d.done(0))

    layoutV = QVBoxLayout(d)
    layoutV.addLayout(graphOptions)
    layoutV.addWidget(bbox)

    retval = d.exec_()
    #print("reval:", retval)

    if retval == 0:
        dprint(fncname + "Cancelled, Properties unchanged")
        #fprint("\nSet Properties: Cancelled, Properties unchanged")
    else:
    # mean
        mean        = mean.text().replace(",", ".")    #replace any comma with dot
        try:    lm  = round(abs(float(mean)), 1)
        except: lm  = gglobs.SimulMean
        if lm <= 10000: gglobs.SimulMean = lm
        else:           efprint("Illegal entry for mean: ", lm)

    # plimit
        plimit      = plimit.text().replace(",", ".")  #replace any comma with dot
        try:    lp  = round(abs(float(plimit)), 1)
        except: lp  = gglobs.SimulPredictLimit
        gglobs.SimulPredictLimit = lp

        dprint(fncname + "ok, new settings: ", gglobs.SimulMean, " ", gglobs.SimulPredictLimit)

        fprintSimulCounterInfo(extended=False)

    setDebugIndent(0)


def fprintSimulCounterInfo(extended=False):
    """prints basic info on the SimulCounter device"""

    setBusyCursor()

    txt = "SimulCounter Device"
    if extended:  txt += " Extended"
    fprint(header(txt))
    fprint("Configured Connection:", "Poisson Generator")
    fprint(getSimulCounterInfo(extended=extended))

    setNormalCursor()


# only when predictive is used
#~def extendedgetSimulCounterInfo(extended = False):
    #~"""Info on the SimulCounter"""

    #~if not gglobs.SimulConnection:   return "No connected device"

    #~SimulInfo = """Connected Device:             '{}'
#~Configured Variables:         {}
#~Geiger Tube Sensitivity:      {:0.1f} CPM/(µSv/h) ({:0.4f} µSv/h/CPM)
#~Distribution Mean:            {:0.1f} CPS, = {:0.1f} CPM
#~Predictive:                   {}
#~Predictive Limit:             {}
#~"""\
                #~.format(
                        #~gglobs.SimulDeviceName,
                        #~gglobs.SimulVariables,
                        #~gglobs.SimulSensitivity, 1 / gglobs.SimulSensitivity,
                        #~gglobs.SimulMean, gglobs.SimulMean * 60,
                        #~"Yes" if gglobs.SimulPredictive else "No",
                        #~gglobs.SimulPredictLimit,
                       #~)

    #~if extended == True:
        #~SimulInfo += """
#~{}
#~"""\
                #~.format("None")
        #~SimulInfo += "\n"

    #~return SimulInfo


def getSimulCounterInfo(extended = False):
    """Info on the SimulCounter"""

    if not gglobs.SimulConnection:   return "No connected device"

    SimulInfo = """Connected Device:             '{}'
Configured Variables:         {}
Geiger Tube Sensitivity:      {:0.1f} CPM/(µSv/h) ({:0.4f} µSv/h/CPM)
Distribution Mean:            {:0.1f} CPS, = {:0.1f} CPM
"""\
                .format(
                        gglobs.SimulDeviceName,
                        gglobs.SimulVariables,
                        gglobs.SimulSensitivity, 1 / gglobs.SimulSensitivity,
                        gglobs.SimulMean, gglobs.SimulMean * 60,
                       )

    return SimulInfo

