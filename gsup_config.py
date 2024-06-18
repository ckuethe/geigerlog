#! /usr/bin/env python3
# -*- coding: UTF-8 -*-

"""
gsup_config.py - GeigerLog support file to evaluate the configuration

include in programs with:
    import gsup_config
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


def readGeigerLogConfig():
    """reading the configuration file, return if not available.
    Not-available or illegal options are being ignored with only a debug message"""

    ######  local function  ###########################################################
    def getConfigEntry(section, parameter, ptype):
        """utility for readGeigerLogConfig"""

        defname = "getConfigEntry: "
        # mdprint(defname, "section: '{}'  parameter: '{}'    ptype: '{}'".format(section, parameter, ptype))

        errmsg  = "\n\n<b>Problems in GeigerLog Configuration File</b>\n"
        errmsg += "(if possible will continue using defaults):\n\n"
        errmsg += "-" * 100

        try:
            t = config.get(section, parameter).strip()
            # mdprint(defname, "t: '{}' end of t".format(t))

            # t = t.strip()
            t = t.strip().replace(" ", "")
            if   ptype == "float":    t = float(t)
            elif ptype == "int":      t = int(float(t))
            elif ptype == "str":      t = t
            elif ptype == "upper":    t = t.upper()

            return t

        except ValueError: # e.g. failure to convert to float
            errmsg += "Section: {}, Parameter: {}\nProblem: has wrong value: '{}'".format(section, parameter, t)
            g.configAlerts += errmsg + "\n\n"
            edprint("WARNING: " + errmsg, debug=True)

            return "WARNING"

        except Exception as e:
            errmsg += "Section: {}, Parameter: {}\n\nProblem: {}".format(section, parameter, e)
            g.configAlerts += errmsg + "\n\n"
            edprint("WARNING: " + errmsg, debug=True)

            return "WARNING"

    ##################################################################################

    defname = "readGeigerLogConfig: "

    dprint(defname)
    setIndent(1)

    infostrHeader = "cfg: {:35s} {}"
    infostr       = "cfg:     {:35s}: {}"
    while True:

    # does the config file exist and can it be read?
        # print(defname, "config.file: ", g.configFile)
        if not os.path.isfile(g.configFile) or not os.access(g.configFile, os.R_OK) :
            msg = """Configuration file <b>'geigerlog.cfg'</b> does not exist or is not readable."""
            edprint(msg, debug=True)
            msg += "<br><br>Please check and correct. Cannot continue, will exit."
            g.startupProblems = msg
            break

    # is it error free?
        try:
            config = configparser.ConfigParser()
            with open(g.configFile) as f:
               config.read_file(f)
        except Exception as e:
            msg = "Configuration file <b>'geigerlog.cfg'</b> cannot be interpreted."
            exceptPrint(e, msg)
            msg += "\n\nNote that duplicate entries are not allowed!"
            msg += "\n\nERROR Message:\n" + str(sys.exc_info()[1])
            msg += "\n\nPlease check and correct. Cannot continue, will exit."
            g.startupProblems = msg.replace("\n", "<br>")
            break

    # the config file exists and can be read:
        dprint(infostrHeader.format("Startup values", ""))


    # Logging
        t = getConfigEntry("Logging", "LogCycle", "upper" )
        if t != "WARNING":
            if t == "AUTO":                     g.LogCycle = 1
            else:
                try:    ft = float(t)
                except: ft = 1
                if      ft >= 0.1:              g.LogCycle = ft
                else:                           g.LogCycle = 1
        dprint(infostr.format("Logcycle (sec)", g.LogCycle))


    # DataDirectory
        t = getConfigEntry("DataDirectory", "DataDir", "str" )
        # edprint("DataDirectory: g.dataDir:", g.dataDir)
        if t != "WARNING":
            errmsg = "WARNING: "
            try:
                if t.upper() == "AUTO":
                    pass                        # no change to default = 'data'
                else:
                    if os.path.isabs(t): testpath = t                           # is it absolute path? yes
                    else:                testpath = g.dataDir + "/" + t   # it is relative path? yes
                    #cdprint("path:", testpath)

                    # Make sure the data directory exists; create it if needed
                    # ignore if it cannot be made or is not writable
                    if os.access(testpath, os.F_OK):
                        # dir exists, ok
                        if not os.access(testpath , os.W_OK):
                            # dir exists, but is not writable
                            errmsg += "Configured data directory '{}' exists, but is not writable".format(testpath)
                            raise NameError
                        else:
                            # dir exists and is writable
                            g.dataDir = testpath
                    else:
                        # dir does not exist; make it
                        try:
                            os.mkdir(testpath)
                            g.dataDir = testpath
                        except:
                            # dir cannot be made
                            errmsg += "Could not make configured data directory '{}'".format(testpath)
                            raise NameError

            except Exception as e:
                dprint(errmsg, "; Exception:", e, debug=True)

        dprint(infostr.format("Data directory", g.dataDir))


    # USEVENVSUBDIR
        t = getConfigEntry("DataDirectory", "UseVenvSubDir", "upper" )
        if t != "WARNING":
            if   t == "AUTO":                     g.useVenvDirectory = False
            elif t == "YES":                      g.useVenvDirectory = True
            else:                                 g.useVenvDirectory = False
        dprint(infostr.format("UseVenvSubDir",    g.useVenvDirectory))


# [TimeZone]
# # UTC Correction
# # The time difference between time at your location and UTC time is recognized
# # by GeigerLog automatically.
# #
# # However, browsers like Firefox and Chrome have the unfortunate property of converting
# # all Javascript time formats as if they were UTC times. Other browsers may respond
# # differently, so if the automatic correction fails, you can enter the desired
# # correction here.
# #
# # The value entered here is ADDED to the times found by the browsers. E.g., Germany
# # has a (negative) 1 h offset to UTC in wintertime, and 2h in summertime.
# # So, in summertime correct with  -2 * 3600 (= minus 7200) sec.
# #
# # NOTE: For some odd political reasons the maximum plus time zone is indeed 14h and
# # not 12h! (https://en.wikipedia.org/wiki/Time_zone)
# #
# # Option auto (recommended) defaults to the automatic calculation.
# #
# # Options:        auto | <any number from -43200 (=-12*3600) to +50400 (=+14*3600)>
# # Default       = auto
# TimeZoneUTCcorr = auto


    # TimeZone Offset to UTC
        t = getConfigEntry("TimeZone", "TimeZoneOffset", "upper" )
        if t != "WARNING":
            if t == "AUTO":                                 g.TimeZoneOffset = "auto"
            else:
                try:
                    tzuc = int(float(t))
                    if -12 * 3600 <= tzuc <= +14 * 3600:    g.TimeZoneOffset = tzuc
                    else:                                   g.TimeZoneOffset = "auto"
                except Exception as e:
                    exceptPrint(e, "TimeZoneOffset has non-numeric value: '{}'".format(t))
                    g.TimeZoneOffset = "auto"

            dprint(infostr.format("TimeZone Offset",        g.TimeZoneOffset))


    # # Manual
    #     t = getConfigEntry("Manual", "ManualName", "str" )
    #     if t != "WARNING":
    #         if t.upper() == "AUTO" or t == "":
    #             g.manual_filename = "auto"
    #             dprint(infostr.format("Filename GeigerLog Manual",      g.manual_filename))
    #         else:
    #             pathisabs = os.path.isabs(t)
    #             if pathisabs: manual_file = t
    #             else:         manual_file = os.path.join(getPathToProgDir(), t)
    #             if os.path.isfile(manual_file):     # does the file exist?
    #                 # it exists
    #                 g.manual_filename = t
    #                 dprint(infostr.format("Filename GeigerLog Manual",  g.manual_filename))
    #             else:
    #                 # it does not exist
    #                 g.manual_filename = "auto"
    #                 dprint("WARNING: Filename GeigerLog Manual '{}' does not exist".format(t))


    # Monitor Server
        dprint(infostrHeader.format("Monitor Server", ""))

        # MonServer Autostart
        t = getConfigEntry("MonServer", "MonServerAutostart", "upper" )
        if t != "WARNING":
            if     t == "NO":                              g.MonServerAutostart = False
            else:                                          g.MonServerAutostart = True
            dprint(infostr.format("MonServer Autostart",   g.MonServerAutostart))

        # MonServer SSL
        t = getConfigEntry("MonServer", "MonServerSSL", "upper" )
        if t != "WARNING":
            if     t == "YES":                             g.MonServerSSL = True
            else:                                          g.MonServerSSL = False
            dprint(infostr.format("MonServer SSL",         g.MonServerSSL))

        # MonServer Port
        t = getConfigEntry("MonServer", "MonServerPort", "upper" )
        if t != "WARNING":
            if t == "AUTO":                                g.MonServerPorts = "auto"
            else:
                default = False
                mspraw = t.split(",")
                # edprint("mspraw: ", mspraw)
                MSPorts = []
                for pn in mspraw:
                    pn = pn.strip()
                    if pn == "":    continue
                    try:
                        tport = int(float(pn))
                        # edprint("tport: ", tport)
                        if 1024 <= tport <= 65535:
                            MSPorts.append(tport)
                        else:
                            default = True
                            break
                    except Exception as e:
                        exceptPrint(e, "MonServerPort has non-numeric value")
                        default = True
                        break

                if default: g.MonServerPorts = "auto"
                else:       g.MonServerPorts = MSPorts

            dprint(infostr.format("MonServer Port",         g.MonServerPorts))

        # MonServerThresholds (low, high)
        t = getConfigEntry("MonServer", "MonServerThresholds", "upper" )
        if t != "WARNING":
            if t == "AUTO":                                         g.MonServerThresholds = "auto"
            else:
                ts = t.split(",")
                if len(ts) == 2:
                    try:
                        lo = float(ts[0])
                        hi = float(ts[1])
                        if lo > 0 and hi > lo:                      g.MonServerThresholds = (lo, hi)
                        else:                                       g.MonServerThresholds = "auto"
                    except:
                        g.MonServerThresholds = "auto"
                else:
                    g.MonServerThresholds = "auto"

            dprint(infostr.format("MonServer Thresholds",   g.MonServerThresholds))

        # MonServerPlotConfig       (Default:  10, 0, 1)
        t = getConfigEntry("MonServer", "MonServerPlotConfig", "upper" )
        if t != "WARNING":
            # edprint("config: t: ", t)
            if t == "AUTO":                                         g.MonServerPlotConfig = "auto"
            else:
                ts = t.split(",")
                # edprint("config: ts: ", ts)
                if len(ts) == 3:
                    try:
                        plotlen = clamp(float(ts[0]), 0.1, 1500)
                        plottop = clamp(int(float(ts[1])), 0, 11)
                        plotbot = clamp(int(float(ts[2])), 0, 11)
                        g.MonServerPlotConfig = (plotlen, plottop, plotbot)
                    except:
                        exceptPrint(e, "config MonServerPlotConfig")
                        g.MonServerPlotConfig = "auto"
                else:
                    g.MonServerPlotConfig = "auto"

            dprint(infostr.format("MonServer PlotConfig",   g.MonServerPlotConfig))

        # MonServerDataConfig       (Default:  1, 3, 10)
        t = getConfigEntry("MonServer", "MonServerDataConfig", "upper" )
        if t != "WARNING":
            # edprint("config: t: ", t)
            if t == "AUTO":                                         g.MonServerDataConfig = "auto"
            else:
                ts = t.split(",")
                # edprint("config: ts: ", ts)
                if len(ts) == 3:
                    try:
                        dataA = clamp(float(ts[0]), 1, 1000)
                        dataB = clamp(float(ts[1]), 2, 1000)
                        dataC = clamp(float(ts[2]), 3, 1000)
                        g.MonServerDataConfig = (dataA, dataB, dataC)
                    except:
                        exceptPrint(e, "config MonServerDataConfig")
                        g.MonServerDataConfig = "auto"
                else:
                    g.MonServerDataConfig = "auto"

            dprint(infostr.format("MonServer DataConfig",   g.MonServerDataConfig))

#inactive ####################
    # #from geigerlog.cfg
    #     # MonServer REFRESH
    #     # This sets the refresh timings for the web pages Monitor, Data, Graph. The
    #     # numbers give the seconds after which the site will be refreshed. Numbers
    #     # must be separated by comma.
    #     #
    #     # Option auto defaults to 1, 10, 3
    #     #
    #     # Options:         auto | < <Monitor Refresh> , <Data Refresh> , <Graph Refresh> >
    #     # Default        = auto
    #     # MonServerRefresh = auto
    #     MonServerRefresh = 1, 10, 1

    # # from here
    #     # # MonServer Refresh
    #     # t = getConfigEntry("MonServer", "MonServerRefresh", "upper" )
    #     # if t != "WARNING":
    #     #     if t == "AUTO":                                 g.MonServerRefresh = "auto"
    #     #     else:
    #     #         ts = t.split(",")
    #     #         try:
    #     #             g.MonServerRefresh[0] = int(ts[0])
    #     #             g.MonServerRefresh[1] = int(ts[1])
    #     #             g.MonServerRefresh[2] = int(ts[2])
    #     #         except Exception as e:
    #     #             exceptPrint(e, "MonServer Refresh defined improperly")
    #     #             g.MonServerRefresh  = "auto"
    #     #     dprint(infostr.format("MonServer Refresh",     g.MonServerRefresh))
# end inactive ####################



    # Window
        dprint(infostrHeader.format("Window", ""))

    # Window HiDPIactivation
        t = getConfigEntry("Window", "HiDPIactivation", "upper" )
        if t != "WARNING":
            if    t == 'AUTO':         g.hidpiActivation = "auto"
            elif  t == 'YES':          g.hidpiActivation = "yes"
            elif  t == 'NO':           g.hidpiActivation = "no"
            else:                      g.hidpiActivation = "auto"
            dprint(infostr.format("Window HiDPIactivation", g.hidpiActivation))

    # Window HiDPIscaleMPL
        t = getConfigEntry("Window", "HiDPIscaleMPL", "upper" )
        if t != "WARNING":
            if    t == 'AUTO':         g.hidpiScaleMPL = "auto"
            try:                       g.hidpiScaleMPL = int(float(t))
            except:                    g.hidpiScaleMPL = "auto"
            dprint(infostr.format("Window HiDPIscaleMPL", g.hidpiScaleMPL))

    # Window dimensions
        w = getConfigEntry("Window", "windowWidth",  "int" )
        h = getConfigEntry("Window", "windowHeight", "int" )
        # rdprint("Window dimension: ", w, "  ", h)
        if w != "WARNING" and h != "WARNING":
            if w > 500 and w < 5000 and h > 100 and h < 5000:
                g.window_width  = w
                g.window_height = h
                dprint(infostr.format("Window dimensions (pixel)", "{} x {}".format(g.window_width, g.window_height)))
            else:
                dprint("WARNING: Config Window dimension out-of-bound; ignored: {} x {} pixel".format(g.window_width, g.window_height), debug=True)

    # Window Size
        t = getConfigEntry("Window", "windowSize", "upper" )
        if t != "WARNING":
            if    t == 'MAXIMIZED':    g.window_size = 'maximized'
            else:                      g.window_size = 'auto'
            dprint(infostr.format("Window Size ", g.window_size))

    # Window Style
        t = getConfigEntry("Window", "windowStyle", "str" )
        if t != "WARNING":
            available_style = QStyleFactory.keys()
            if t in available_style:    g.windowStyle = t
            else:                       g.windowStyle = "auto"
            dprint(infostr.format("Window Style ", g.windowStyle))

    # WINDOW PAD COLORS cannot be used due to a bug in PyQt5
    # # from the geigerlog.cfg file:
    # # WINDOW PAD COLORS:
    # # Sets the background color of NotePad and LogPad. Default is a
    # # very light green for NotePad, and very light blue for LogPad.
    # # Colors can be given as names (red, green, lightblue,...) - not
    # # all names will work - or #<red><green><blue> with red, green, blue
    # # in HEX notation.
    # # Example: #FFFFFF is pure white, #FF0000 is pure red, #00FF00 is pure green,
    # # #CCCCFF is a blueish grey, and #000000 is pure black.
    # #
    # # Option auto defaults to: '#FaFFFa, #FaFaFF'
    # #
    # # Options:       auto | <color name, color name>
    # # Default      = auto
    # windowPadColor = auto
    # # windowPadColor = #FaFFFa, #e0e0FF
    #
    # # Window Pad Color
    #     t = getConfigEntry("Window", "windowPadColor", "str" )
    #     if t != "WARNING":
    #         if t.upper() == "AUTO":     g.windowPadColor = ("#FaFFFa", "#FaFaFF")
    #         else:
    #             ts = t.split(",")
    #             Np = ts[0].strip()
    #             Lp = ts[1].strip()
    #             g.windowPadColor      = (Np, Lp)
    #         dprint(infostr.format("Window Pad BG-Color ", g.windowPadColor))


    # Graphic
        dprint(infostrHeader.format("Graphic", ""))

        # Graphic MovingAverage
        t = getConfigEntry("Graphic", "MovingAverage", "float" )
        if t != "WARNING":
            if   t >= 1:                        g.mav_initial = t
            else:                               g.mav_initial = 600
            g.mav =                        g.mav_initial
            dprint(infostr.format("Moving Average Initial (sec)", int(g.mav_initial)))


    # Graphic Plotstyle
        # dprint(infostrHeader.format("Plotstyle", ""))

        # Graphic Plotstyle linewidth
        # t = getConfigEntry("Plotstyle", "linewidth", "str" )
        t = getConfigEntry("Graphic", "linewidth", "str" )
        if t != "WARNING":
            try:    g.linewidth           = float(t)
            except: g.linewidth           = 1
        dprint(infostr.format("linewidth", g.linewidth))

        # Graphic Plotstyle markersymbol
        # t = getConfigEntry("Plotstyle", "markersymbol", "str" )
        t = getConfigEntry("Graphic", "markersymbol", "str" )
        if t != "WARNING":
            t = t[0]
            if t in "osp*h+xD" :                g.markersymbol = t
            else:                               g.markersymbol = 'o'
        dprint(infostr.format("markersymbol",   g.markersymbol))

        # Graphic Plotstyle markersize
        # t = getConfigEntry("Plotstyle", "markersize", "str" )
        t = getConfigEntry("Graphic", "markersize", "str" )
        if t != "WARNING":
            try:                                g.markersize = float(t)
            except:                             g.markersize = 15
        dprint(infostr.format("markersize",     g.markersize))


    # Network
        dprint(infostrHeader.format("Network", ""))

        # WiFi SSID
        t = getConfigEntry("Network", "WiFiSSID", "str" )
        if t != "WARNING":                      g.WiFiSSID = t
        dprint(infostr.format("WiFiSSID",       g.WiFiSSID))

        # WiFi Password
        t = getConfigEntry("Network", "WiFiPassword", "str" )
        if t != "WARNING":                      g.WiFiPassword = t
        dprint(infostr.format("WiFiPassword",   g.WiFiPassword))


    # Radiation World Maps
        dprint(infostrHeader.format("Worldmaps", ""))

        t = getConfigEntry("Worldmaps", "gmcmapWebsite", "str" )
        if t != "WARNING":                      g.gmcmapWebsite = t
        dprint(infostr.format("Website",        g.gmcmapWebsite))

        t = getConfigEntry("Worldmaps", "gmcmapURL", "str" )
        if t != "WARNING":                      g.gmcmapURL = t
        dprint(infostr.format("URL",            g.gmcmapURL))

        t = getConfigEntry("Worldmaps", "gmcmapUserID", "str" )
        if t != "WARNING":                      g.gmcmapUserID = t
        dprint(infostr.format("UserID",         g.gmcmapUserID))

        t = getConfigEntry("Worldmaps", "gmcmapCounterID", "str" )
        if t != "WARNING":                      g.gmcmapCounterID = t
        dprint(infostr.format("CounterID",      g.gmcmapCounterID))


    #
    # ValueFormula - it DOES modify the variable value!
    #
    # infostr = "INFO: {:35s}: {}"
        dprint(infostrHeader.format("ValueFormula", ""))
        for vname in g.VarsCopy:
            t = getConfigEntry("ValueFormula", vname, "upper" )
            if t != "WARNING":
                if t == "":     pass                    # use value from gglobs
                else:           g.ValueScale[vname] = t
                dprint(infostr.format("ValueScale['{}']".format(vname), g.ValueScale[vname]))


    #
    # GraphFormula - it does NOT modify the variable value, only the plot value
    #
        dprint(infostrHeader.format("GraphFormula", ""))
        for vname in g.VarsCopy:
            t = getConfigEntry("GraphFormula", vname, "upper" )
            if t != "WARNING":
                if t == "":                         pass                    # use value from gglobs
                else:                               g.GraphScale[vname] = t
                dprint(infostr.format("GraphScale['{}']".format(vname), g.GraphScale[vname]))


###
### TubeSensitivities
###
        dprint(infostrHeader.format("TubeSensitivities", ""))

        t = getConfigEntry("TubeSensitivities", "TubeSensitivityDef", "str" )
        # rdprint(defname, "t Def: ", t)
        if t != "WARNING":
            if    t.upper() == 'AUTO':              g.TubeSensitivity[0] = "auto"
            else:
                try:
                    tf = float(t)
                    if tf > 0:                      g.TubeSensitivity[0] = tf
                    else:                           g.TubeSensitivity[0] = "auto"
                except:                             g.TubeSensitivity[0] = "auto"
        dprint(infostr.format("TubeSensitivityDef", g.TubeSensitivity[0]))

        t = getConfigEntry("TubeSensitivities", "TubeSensitivity1st", "str" )
        # rdprint(defname, "t 1st: ", t)
        if t != "WARNING":
            if    t.upper() == 'AUTO':              g.TubeSensitivity[1] = "auto"
            else:
                try:
                    tf = float(t)
                    if tf > 0:                      g.TubeSensitivity[1] = tf
                    else:                           g.TubeSensitivity[1] = "auto"
                except:                             g.TubeSensitivity[1] = "auto"
        dprint(infostr.format("TubeSensitivity1st", g.TubeSensitivity[1]))

        t = getConfigEntry("TubeSensitivities", "TubeSensitivity2nd", "str" )
        # rdprint(defname, "t 2nd: ", t)
        if t != "WARNING":
            if    t.upper() == 'AUTO':              g.TubeSensitivity[2] = "auto"
            else:
                try:
                    tf = float(t)
                    if tf > 0:                      g.TubeSensitivity[2] = tf
                    else:                           g.TubeSensitivity[2] = "auto"
                except:                             g.TubeSensitivity[2] = "auto"
        dprint(infostr.format("TubeSensitivity2nd", g.TubeSensitivity[2]))

        t = getConfigEntry("TubeSensitivities", "TubeSensitivity3rd", "str" )
        # rdprint(defname, "t 3rd: ", t)
        if t != "WARNING":
            if    t.upper() == 'AUTO':              g.TubeSensitivity[3] = "auto"
            else:
                try:
                    tf = float(t)
                    if tf > 0:                      g.TubeSensitivity[3] = tf
                    else:                           g.TubeSensitivity[3] = "auto"
                except:                             g.TubeSensitivity[3] = "auto"
        dprint(infostr.format("TubeSensitivity3rd", g.TubeSensitivity[3]))


###
### DEVICES
###

        dprint(infostrHeader.format("Activated Devices", ""))

        # re-definition for increased indentation
        infostrHeader = "cfg:     {:31s} {}"
        infostr       = "cfg:         {:31s}: {}"

    # GMC_Device
        t = getConfigEntry("GMC_Device", "GMC_Activation", "upper" )
        if t != "WARNING":
            if t == "YES":
                g.Devices["GMC"][2] = True

        if g.Devices["GMC"][2]: # show only if activated
            dprint(infostrHeader.format("GMC Device", ""))

            # GMC_Device Firmware Bugs
            # location bug: "GMC-500+Re 1.18, GMC-500+Re 1.21"
            t = getConfigEntry("GMC_Device", "GMC_locationBug", "str" )
            if t != "WARNING":
                if t.upper() == "AUTO":                 g.GMC_locationBug = "auto"
                else:                                   g.GMC_locationBug = t
                dprint(infostr.format("Location Bug",   g.GMC_locationBug))

            # GMC_Device Firmware Bugs
            # FET bug: GMC_FastEstTime
            t = getConfigEntry("GMC_Device", "GMC_FastEstTime", "upper" )
            if t != "WARNING":
                if   t == "AUTO":                       g.GMC_FastEstTime = "auto"
                elif t == "DYNAMIC":                    g.GMC_FastEstTime = 3
                else:
                    try:    tFET = int(float(t))
                    except: tFET = 0
                    if   tFET in (3,5,10,15,20,30,60):  g.GMC_FastEstTime = tFET
                    else:                               g.GMC_FastEstTime = "auto"
                dprint(infostr.format("FET",            g.GMC_FastEstTime))


            # GMC_Device RTC_OFFSET
            t = getConfigEntry("GMC_Device", "GMC_RTC_Offset", "upper" )
            if t != "WARNING":
                if   t == "AUTO":                       g.GMC_RTC_Offset = "auto"
                else:
                    try:    rtcos = clamp(int(float(t)), -59, 59)
                    except: rtcos = 0
                    g.GMC_RTC_Offset = rtcos
                dprint(infostr.format("RTC_OFFSET",     g.GMC_RTC_Offset))


            # GMC_Device CLOCK_CORRECTION
            t = getConfigEntry("GMC_Device", "GMC_GL_ClockCorrection", "upper" )
            # rdprint(defname, "GMC_GL_ClockCorrection: ", g.GMC_GL_ClockCorrection)
            if t != "WARNING":
                if   t == "AUTO":                               g.GMC_GL_ClockCorrection = "auto"
                else:
                    try:    rtcos = clamp(int(float(t)), 0, 59)
                    except: rtcos = "auto"
                    if 1:                                       g.GMC_GL_ClockCorrection = rtcos
                dprint(infostr.format("CLOCK_CORRECTION",       g.GMC_GL_ClockCorrection))


            # GMC_Device memory
            t = getConfigEntry("GMC_Device", "GMC_memory", "upper" )
            if t != "WARNING":
                if   t ==  '1MB':                       g.GMC_memory = 2**20   # 1 048 576
                elif t == '64KB':                       g.GMC_memory = 2**16   #    65 536
                else:                                   g.GMC_memory = 'auto'
                dprint(infostr.format("Memory",         g.GMC_memory))

            # GMC_Device GMC_SPIRpage
            t = getConfigEntry("GMC_Device", "GMC_SPIRpage", "upper" )
            if t != "WARNING":
                if   t == '2K':                         g.GMC_SPIRpage = 2048     # @ 2k speed: 6057 B/sec
                elif t == '4K':                         g.GMC_SPIRpage = 4096     # @ 4k speed: 7140 B/sec
                elif t == '8K':                         g.GMC_SPIRpage = 4096 * 2 # @ 8k speed: 7908 B/sec
                elif t == '16K':                        g.GMC_SPIRpage = 4096 * 4 # @16k speed: 8287 B/sec
                else:                                   g.GMC_SPIRpage = "auto"
                dprint(infostr.format("SPIRpage",       g.GMC_SPIRpage))

            # GMC_Device GMC_SPIRbugfix
            t = getConfigEntry("GMC_Device", "GMC_SPIRbugfix", "upper" )
            if t != "WARNING":
                if   t == 'YES':                        g.GMC_SPIRbugfix = True
                elif t == 'NO':                         g.GMC_SPIRbugfix = False
                else:                                   g.GMC_SPIRbugfix = 'auto'
                dprint(infostr.format("SPIRbugfix",     g.GMC_SPIRbugfix))

            # GMC_Device GMC_configsize
            t = getConfigEntry("GMC_Device", "GMC_configsize", "upper" )
            if t != "WARNING":
                t = config.get("GMC_Device", "GMC_configsize")
                if   t == '256':                        g.GMC_configsize = 256
                elif t == '512':                        g.GMC_configsize = 512
                else:                                   g.GMC_configsize = 'auto'
                dprint(infostr.format("Configsize",     g.GMC_configsize))

            # GMC_Device GMC_voltagebytes
            t = getConfigEntry("GMC_Device", "GMC_voltagebytes", "upper" )
            if t != "WARNING":
                if   t == '1':                          g.GMC_voltagebytes = 1
                elif t == '5':                          g.GMC_voltagebytes = 5
                elif t == 'NONE':                       g.GMC_voltagebytes = None
                else:                                   g.GMC_voltagebytes = 'auto'
                dprint(infostr.format("Voltagebytes",   g.GMC_voltagebytes))

            # GMC_Device GMC_endianness
            t = getConfigEntry("GMC_Device", "GMC_endianness", "upper" )
            if t != "WARNING":
                if   t == 'LITTLE':                     g.GMC_endianness = 'little'
                elif t == 'BIG':                        g.GMC_endianness = 'big'
                else:                                   g.GMC_endianness = 'auto'
                dprint(infostr.format("Endianness",     g.GMC_endianness))


            # GMC_Device GMC_CfgHiIndex
            t = getConfigEntry("GMC_Device", "GMC_CfgHiIndex", "upper" )
            if t != "WARNING":
                if   t == "AUTO":                       g.GMC_CfgHiIndex = "auto"
                elif t in  range(0, 8):                 g.GMC_CfgHiIndex = int(t)
                else:                                   g.GMC_CfgHiIndex = "auto"
                dprint(infostr.format("cfgHiIndex",     g.GMC_CfgHiIndex))


            # GMC_Device GMC_WiFiPeriod
            t = getConfigEntry("GMC_Device", "GMC_WiFiPeriod", "upper" )
            if t != "WARNING":
                if t == "AUTO":                             g.GMC_WiFiPeriod = "auto"
                else:
                    try:
                        ift = int(float(t))
                        if ift > 0 and ift < 256:           g.GMC_WiFiPeriod = ift
                        else:                               g.GMC_WiFiPeriod = "auto"
                    except:                                 g.GMC_WiFiPeriod = "auto"
            dprint(infostr.format("WiFiPeriod",             g.GMC_WiFiPeriod))


            # GMC_Device GMC_WiFiSwitch
            t = getConfigEntry("GMC_Device", "GMC_WiFiSwitch", "upper" )
            if t != "WARNING":
                if t == "AUTO":                             g.GMC_WiFiSwitch = "auto"
                else:
                    if t == "ON":                           g.GMC_WiFiSwitch = 1
                    else:                                   g.GMC_WiFiSwitch = 0
                dprint(infostr.format("WiFiSwitch",         g.GMC_WiFiSwitch))


            # GMC_Device GMC_Bytes
            t = getConfigEntry("GMC_Device", "GMC_Bytes", "upper" )
            if t != "WARNING":
                if t == "AUTO":                             g.GMC_Bytes = "auto"
                else:
                    try:
                        nt = int(t)
                        if nt in (2, 4):                    g.GMC_Bytes = nt
                        else:                               g.GMC_Bytes = "auto"
                    except Exception as e:
                        exceptPrint(e, "GMC_Device GMC_Bytes")
                        g.GMC_Bytes = "auto"

                dprint(infostr.format("Bytes",              g.GMC_Bytes))


            # GMC_Device variables
            t = getConfigEntry("GMC_Device", "GMC_Variables", "str" )
            if t != "WARNING":
                if t.upper() == "AUTO":                     g.GMC_Variables = "auto"
                else:                                       g.GMC_Variables = correctVariableCaps(t)
                dprint(infostr.format("Variables",          g.GMC_Variables))


            # GMC USB port
            t = getConfigEntry("GMC_Device", "GMC_usbport", "str" )
            if t != "WARNING":
                if   t.upper() == "AUTO":                   g.GMC_usbport = "auto"
                else:                                       g.GMC_usbport = t
                dprint(infostr.format("USB Serial Port",    g.GMC_usbport))


            # GMC Device ID (Model, Serial No)
            t = getConfigEntry("GMC_Device", "GMC_ID", "str" )
            if t != "WARNING":
                if   t.upper() == "AUTO":                   g.GMC_ID = "auto"
                else:
                    ts = t.split(",")
                    if len(ts) != 2:                        g.GMC_ID = "auto"
                    else:
                        ts[0] = ts[0].strip()
                        ts[1] = ts[1].strip()
                        if ts[0].upper() == "NONE": ts[0] = None
                        if ts[1].upper() == "NONE": ts[1] = None
                        g.GMC_ID = ts
                dprint(infostr.format("Device IDs",         g.GMC_ID))



    # AudioCounter
        t = getConfigEntry("AudioCounter", "AudioActivation", "upper" )
        if t != "WARNING":
            if t == "YES":
                g.Devices["Audio"][2] = True

        if g.Devices["Audio"][2]: # show only if activated
            dprint(infostrHeader.format("AudioCounter Device", ""))

            # AudioCounter DEVICE
            t = getConfigEntry("AudioCounter", "AudioDevice", "str" )
            if t != "WARNING":
                if   t.upper() == "AUTO":                   g.AudioDevice = "auto"
                elif not ("," in t):                        g.AudioDevice = "auto" # must have 2 items separated by comma
                else:
                    t = t.split(",", 1)
                    t[0] = t[0].strip()
                    t[1] = t[1].strip()
                    if t[0].isdecimal():   t[0] = int(t[0])
                    if t[1].isdecimal():   t[1] = int(t[1])
                    g.AudioDevice = tuple(t)
                dprint(infostr.format("AudioDevice",        g.AudioDevice))

            # AudioCounter LATENCY
            t = getConfigEntry("AudioCounter", "AudioLatency", "str" )
            if t != "WARNING":
                if   t.upper() == "AUTO":                   g.AudioLatency = "auto"
                elif not ("," in t):                        g.AudioLatency = "auto" # must have 2 items separated by comma
                else:
                    t = t.split(",", 1)
                    try:    t[0] = float(t[0])
                    except: t[0] = 1.0
                    try:    t[1] = float(t[1])
                    except: t[1] = 1.0
                    g.AudioLatency = tuple(t)
                dprint(infostr.format("AudioLatency",       g.AudioLatency))

            # AudioCounter PULSE Dir
            t = getConfigEntry("AudioCounter", "AudioPulseDir", "upper" )
            if t != "WARNING":
                if   t == "AUTO":           g.AudioPulseDir = "auto"
                elif t == "NEGATIVE":       g.AudioPulseDir = False
                elif t == "POSITIVE":       g.AudioPulseDir = True
                else:                       pass # unchanged from default False
                dprint(infostr.format("AudioPulseDir", g.AudioPulseDir))

            # AudioCounter PULSE Max
            t = getConfigEntry("AudioCounter", "AudioPulseMax", "upper" )
            if t != "WARNING":
                if t == "AUTO":                     g.AudioPulseMax = "auto"
                else:
                    try:                            g.AudioPulseMax = int(float(t))
                    except:                         g.AudioPulseMax = "auto"
                    if g.AudioPulseMax <= 0:   g.AudioPulseMax = "auto"
                dprint(infostr.format("AudioPulseMax", g.AudioPulseMax))

            # AudioCounter LIMIT
            t = getConfigEntry("AudioCounter", "AudioThreshold", "upper" )
            if t != "WARNING":
                if t == "AUTO":             g.AudioThreshold = "auto"
                else:
                    try:                    g.AudioThreshold = int(float(t))
                    except:                 g.AudioThreshold = 60
                    if g.AudioThreshold < 0 or g.AudioThreshold > 100:
                                            g.AudioThreshold = 60
                dprint(infostr.format("AudioThreshold", g.AudioThreshold))

            # AudioCounter Variables
            t = getConfigEntry("AudioCounter", "AudioVariables", "str" )
            if t != "WARNING":
                if t.upper() == "AUTO":                 g.AudioVariables = "auto"
                else:                                   g.AudioVariables = correctVariableCaps(t)
                dprint(infostr.format("AudioVariables", g.AudioVariables))


    # SerialPulse Device (e.g. Audio-To-Serial Device)
        t = getConfigEntry("SerialPulseDevice", "SerialPulseActivation", "upper" )
        if t != "WARNING":
            if t == "YES":
                g.Devices["SerialPulse"][2] = True

        if g.Devices["SerialPulse"][2]:       # show next lines only if Pulse device is activated
            dprint(infostrHeader.format("SerialPulse Device", ""))

        # AudioToSerial USB Port
            t = getConfigEntry("SerialPulseDevice", "SerialPulseUsbport", "str" )
            if t != "WARNING":
                if t.upper() == "AUTO":                 g.SerialPulseUsbport = "auto"
                else:                                   g.SerialPulseUsbport = t
                dprint(infostr.format("Serial Port",    g.SerialPulseUsbport))

        # AudioToSerial variables
            t = getConfigEntry("SerialPulseDevice", "SerialPulseVariables", "str" )
            if t != "WARNING":
                if t.upper() == "AUTO":                 g.SerialPulseVariables = "auto"
                else:                                   g.Pulse                = correctVariableCaps(t)
                dprint(infostr.format("Variables",      g.SerialPulseVariables))


    # IoT Device
        # IoT Activation
        t = getConfigEntry("IoTDevice", "IoTActivation", "upper" )
        if t != "WARNING":
            if t == "YES":
                g.Devices["IoT"][2] = True

        if g.Devices["IoT"][2]: # show the other stuff only if activated
            dprint(infostrHeader.format("IoT Device", ""))

            # IoT Server IP
            t = getConfigEntry("IoTDevice", "IoTBrokerIP", "str" )
            if t != "WARNING":
                if t.upper() == 'AUTO':                 g.IoTBrokerIP = "auto"
                else:                                   g.IoTBrokerIP = t
                dprint(infostr.format("IoTBrokerIP",     g.IoTBrokerIP ))

            # IoT Server Port
            t = getConfigEntry("IoTDevice", "IoTBrokerPort", "str" )
            if t != "WARNING":
                if t.upper() == 'AUTO':                 g.IoTBrokerPort = "auto"
                else:
                    try:    g.IoTBrokerPort = abs(int(t))
                    except: g.IoTBrokerPort = "auto"
                dprint(infostr.format("IoTBrokerPort",   g.IoTBrokerPort))

            # IoT IoTUsername
            t = getConfigEntry("IoTDevice", "IoTUsername", "str" )
            if t != "WARNING":
                if t.upper() == 'AUTO':                 g.IoTUsername = "auto"
                else:                                   g.IoTUsername = t
                dprint(infostr.format("IoTUsername",    g.IoTUsername))

            # IoT IoTPassword
            t = getConfigEntry("IoTDevice", "IoTPassword", "str" )
            if t != "WARNING":
                if t.upper() == 'AUTO':                 g.IoTPassword = "auto"
                else:                                   g.IoTPassword = t
                dprint(infostr.format("IoTPassword",    g.IoTPassword))

            # IoT timeout
            t = getConfigEntry("IoTDevice", "IoTTimeout", "upper" )
            if t != "WARNING":
                if t == 'AUTO':                         g.IoTTimeout = "auto"
                else:
                    try:
                        if float(t) > 0:                g.IoTTimeout = float(t)
                        else:                           g.IoTTimeout = "auto"  # if zero or negative value given
                    except:                             g.IoTTimeout = "auto"
                dprint(infostr.format("IoTTimeout",     g.IoTTimeout))

            # IoT Server Folder
            t = getConfigEntry("IoTDevice", "IoTBrokerFolder", "str" )
            if t != "WARNING":
                # blank in folder name not allowed
                if t == "" or " " in t or t.upper() == "AUTO":      g.IoTBrokerFolder = "auto"
                else:
                    g.IoTBrokerFolder = t
                    if g.IoTBrokerFolder[-1] != "/":                g.IoTBrokerFolder += "/"
                dprint(infostr.format("IoTBrokerFolder",            g.IoTBrokerFolder ))


            # IoT Client configs: IoTClientDataGL
            t = getConfigEntry("IoTDevice", "IoTClientDataGL", "str" )
            if t != "WARNING":
                if t.upper() == "AUTO":                     g.IoTClientDataGL = "auto"
                else:                                       g.IoTClientDataGL = t
                dprint(infostr.format("IoTClientDataGL",    g.IoTClientDataGL))


            # IoT Client configs: IoTClientTasmotaGL1
            t = getConfigEntry("IoTDevice", "IoTClientTasmotaGL1", "str" )
            if t != "WARNING":
                if t.upper() == "AUTO":                     g.IoTClientTasmotaGL1 = "auto"
                else:                                       g.IoTClientTasmotaGL1 = t
                dprint(infostr.format("IoTClientTasmotaGL1",g.IoTClientTasmotaGL1))


            # IoT Client configs: IoTClientTasmotaGL2
            t = getConfigEntry("IoTDevice", "IoTClientTasmotaGL2", "str" )
            if t != "WARNING":
                if t.upper() == "AUTO":                     g.IoTClientTasmotaGL2 = "auto"
                else:                                       g.IoTClientTasmotaGL2 = t
                dprint(infostr.format("IoTClientTasmotaGL2",g.IoTClientTasmotaGL2))


            # IoT Client configs: IoTClientTasmotaGL3
            t = getConfigEntry("IoTDevice", "IoTClientTasmotaGL3", "str" )
            if t != "WARNING":
                if t.upper() == "AUTO":                     g.IoTClientTasmotaGL3 = "auto"
                else:                                       g.IoTClientTasmotaGL3 = t
                dprint(infostr.format("IoTClientTasmotaGL3",g.IoTClientTasmotaGL3))


            # IoT Client configs: IoTClientTasmotaGL4
            t = getConfigEntry("IoTDevice", "IoTClientTasmotaGL4", "str" )
            if t != "WARNING":
                if t.upper() == "AUTO":                     g.IoTClientTasmotaGL4 = "auto"
                else:                                       g.IoTClientTasmotaGL4 = t
                dprint(infostr.format("IoTClientTasmotaGL4",g.IoTClientTasmotaGL4))



    # RadMonPlus
        # RadMon Activation
        t = getConfigEntry("RadMonPlusDevice", "RMActivation", "upper" )
        if t != "WARNING":
            if t == "YES":
                g.Devices["RadMon"][2] = True

        if g.Devices["RadMon"][2]: # show the other stuff only if activated
            dprint(infostrHeader.format("RadMonPlus Device", ""))

            # RadMon Server IP
            t = getConfigEntry("RadMonPlusDevice", "RMServerIP", "str" )
            if t != "WARNING":
                if t.upper() == 'AUTO':                 g.RMServerIP = "auto"
                else:                                   g.RMServerIP = t
                dprint(infostr.format("RMServerIP",     g.RMServerIP ))

            # RadMon Server Port
            t = getConfigEntry("RadMonPlusDevice", "RMServerPort", "str" )
            if t != "WARNING":
                if t.upper() == 'AUTO':                 g.RMServerPort = "auto"
                else:
                    try:    g.RMServerPort = abs(int(t))
                    except: g.RMServerPort = "auto"
                dprint(infostr.format("RMServerPort",   g.RMServerPort))

            # Radmon timeout
            t = getConfigEntry("RadMonPlusDevice", "RMTimeout", "upper" )
            if t != "WARNING":
                if t == 'AUTO':                         g.RMTimeout = "auto"
                else:
                    try:
                        if float(t) > 0:                g.RMTimeout = float(t)
                        else:                           g.RMTimeout = "auto"  # if zero or negative value given
                    except:                             g.RMTimeout = "auto"
                dprint(infostr.format("RMTimeout",      g.RMTimeout))

            # RadMon Server Folder
            t = getConfigEntry("RadMonPlusDevice", "RMServerFolder", "str" )
            if t != "WARNING":
                # blank in folder name not allowed
                if " " in t or t.upper() == "AUTO":     g.RMServerFolder = "auto"
                else:
                    g.RMServerFolder = t
                    if g.RMServerFolder[-1] != "/":g.RMServerFolder += "/"
                dprint(infostr.format("RMServerFolder", g.RMServerFolder ))

            # Radmon variables
            t = getConfigEntry("RadMonPlusDevice", "RMVariables", "str" )
            if t != "WARNING":
                if t.upper() == "AUTO":                 g.RMVariables = "auto"
                else:
                    g.RMVariables = correctVariableCaps(t)
                    if g.RMVariables.count("CPM") > 1 or g.RMVariables.count("CPS") > 0:
                        edprint("WARNING: Improper configuration of variables: ", g.RMVariables)
                        edprint("WARNING: Only a single CPM* is allowed, and no CPS*")
                        g.RMVariables = "auto"
                        edprint("WARNING: RadMon variables are reset to: ", g.RMVariables)
                dprint(infostr.format("RMVariables",    g.RMVariables))


    # AmbioMon
        t = getConfigEntry("AmbioMonDevice", "AmbioActivation", "upper" )
        if t != "WARNING":
            if t == "YES":
                g.Devices["AmbioMon"][2] = True

        if g.Devices["AmbioMon"][2]: # show the other stuff only if activated
            dprint(infostrHeader.format("AmbioMon Device", ""))

            # AmbioMon Server IP
            t = getConfigEntry("AmbioMonDevice", "AmbioServerIP", "str" )
            if t != "WARNING":
                if t.upper() == 'AUTO':                 g.AmbioServerIP = "auto"
                else:                                   g.AmbioServerIP = t
                dprint(infostr.format("AmbioServerIP",  g.AmbioServerIP ))

            # AmbioMon Server Port
            t = getConfigEntry("AmbioMonDevice", "AmbioServerPort", "upper" )
            if t != "WARNING":
                if t == "AUTO":                             g.AmbioServerPort = "auto"
                else:
                    wp = int(float(t))
                    if 0 <= wp  <= 65535:                   g.AmbioServerPort = wp
                    else:                                   g.AmbioServerPort = "auto"
                dprint(infostr.format("AmbioServerPort",    g.AmbioServerPort ))

            # AmbioMon timeout
            t = getConfigEntry("AmbioMonDevice", "AmbioTimeout", "upper" )
            if t != "WARNING":
                if t == 'AUTO':                         g.AmbioTimeout = "auto"
                else:
                    try:
                        if float(t) > 0:                g.AmbioTimeout = float(t)
                        else:                           g.AmbioTimeout = "auto"  # if zero or negative value given
                    except:                             g.AmbioTimeout = "auto"
                dprint(infostr.format("AmbioTimeout",   g.AmbioTimeout))

            # AmbioMon DataType
            t = getConfigEntry("AmbioMonDevice", "AmbioDataType", "str" )
            if t != "WARNING":
                if   t.upper() == "AUTO":               g.AmbioDataType = "auto"
                elif t.upper() == "AVG":                g.AmbioDataType = "AVG"
                else:                                   g.AmbioDataType = "LAST"
                dprint(infostr.format("AmbioDataType",  g.AmbioDataType))

            # AmbioMon variables
            t = getConfigEntry("AmbioMonDevice", "AmbioVariables", "str" )
            if t != "WARNING":
                if t.upper() == "AUTO":                 g.AmbioVariables = "auto"
                else:                                   g.AmbioVariables = correctVariableCaps(t)
                dprint(infostr.format("AmbioVariables", g.AmbioVariables))

    # Gamma-Scout counter
        # Gamma-Scout Activation
        t = getConfigEntry("GammaScoutDevice", "GSActivation", "upper" )
        if t != "WARNING":
            if t == "YES":
                g.Devices["GammaScout"][2] = True

        if g.Devices["GammaScout"][2]: # show the other stuff only if activated
            dprint(infostrHeader.format("GammaScout Device", ""))

            # Gamma-Scout variables
            t = getConfigEntry("GammaScoutDevice", "GSVariables", "str" )
            if t != "WARNING":
                if t.upper() == "AUTO":                 g.GSVariables = "auto"
                else:                                   g.GSVariables = correctVariableCaps(t)
                dprint(infostr.format("Variables",      g.GSVariables))

            # Gamma-Scout USB Port
            t = getConfigEntry("GammaScoutDevice", "GSusbport", "str" )
            if t != "WARNING":
                if   t.upper() == "AUTO":               g.GSusbport = "auto"
                else:                                   g.GSusbport = t
                dprint(infostr.format("Serial Port",    g.GSusbport))



    # LabJack U3 (type U3B, perhaps with probe EI1050)
        # LabJack Activation
        t = getConfigEntry("LabJackDevice", "LJActivation", "upper" )
        if t != "WARNING":
            if t == "YES":
                g.Devices["LabJack"][2] = True

        if g.Devices["LabJack"][2]: # show the other stuff only if activated
            dprint(infostrHeader.format("LabJack Device", ""))

            # LabJack  EI1050 Activation
            t = getConfigEntry("LabJackDevice", "LJEI1050Activation", "upper" )
            if t != "WARNING":
                if t == "YES":                              g.LJEI1050Activation = True
                dprint(infostr.format("LJEI1050Activation", g.LJEI1050Activation))

            # LabJack variables
            t = getConfigEntry("LabJackDevice", "LJVariables", "str" )
            if t != "WARNING":
                if t.upper() == "AUTO":                     g.LJVariables = "auto"
                else:                                       g.LJVariables = correctVariableCaps(t)
                dprint(infostr.format("LJVariables",        g.LJVariables))


    # MiniMon
        t = getConfigEntry("MiniMon", "MiniMonActivation", "upper" )
        if t != "WARNING":
            if t == "YES":
                g.Devices["MiniMon"][2] = True

        if g.Devices["MiniMon"][2]: # show the other stuff only if activated
            dprint(infostrHeader.format("MiniMon Device", ""))

            # MiniMon Device
            t = getConfigEntry("MiniMon", "MiniMonOS_Device", "str" )
            if t != "WARNING":
                if t.upper() == "AUTO":                     g.MiniMonOS_Device = "auto"
                else:                                       g.MiniMonOS_Device = t
                dprint(infostr.format("MiniMonOS_Device",   g.MiniMonOS_Device))

            # MiniMon Variables
            t = getConfigEntry("MiniMon", "MiniMonVariables", "str" )
            if t != "WARNING":
                if t.upper() == "AUTO":                     g.MiniMonVariables = "auto"
                else:                                       g.MiniMonVariables = correctVariableCaps(t)
                dprint(infostr.format("MiniMonVariables",   g.MiniMonVariables))

            # MiniMon Interval
            t = getConfigEntry("MiniMon", "MiniMonInterval", "str" )
            if t != "WARNING":
                if t.upper() == "AUTO":                     g.MiniMonInterval = "auto"
                else:
                    try:
                        g.MiniMonInterval = float(t)
                        if g.MiniMonInterval < 0:      g.MiniMonInterval = "auto"
                    except:                                 g.MiniMonInterval = "auto"
                dprint(infostr.format("MiniMonInterval",    g.MiniMonInterval))


    # Formula Device
        # Formula Device Activation
        t = getConfigEntry("Formula", "FormulaActivation", "upper" )
        if t != "WARNING":
            if t == "YES":
                g.Devices["Formula"][2] = True

        if g.Devices["Formula"][2]: # show the other stuff only if activated
            dprint(infostrHeader.format("Formula Device", ""))

            # Formula Device Variables
            t = getConfigEntry("Formula", "FormulaVariables", "str" )
            if t != "WARNING":
                if t.upper() == "AUTO":                     g.FormulaVariables = "auto"
                else:                                       g.FormulaVariables = correctVariableCaps(t)
                dprint(infostr.format("FormulaVariables",   g.FormulaVariables))


    # Manu
        t = getConfigEntry("Manu", "ManuActivation", "upper" )
        if t != "WARNING":
            if t == "YES":
                g.Devices["Manu"][2] = True

        if g.Devices["Manu"][2]: # show the other stuff only if activated
            dprint(infostrHeader.format("Manu Device", ""))

            # Manu Variables
            t = getConfigEntry("Manu", "ManuVariables", "str" )
            if t != "WARNING":
                if t.upper() == "AUTO" :                    g.ManuVariables = "auto"
                else:                                       g.ManuVariables = correctVariableCaps(t)
                dprint(infostr.format("ManuVariables",      g.ManuVariables))


    # WiFiServer
        section = "WiFiServerDevice"
        WiFiServerErrmsg  = "\n<b>Problems in Configuration File</b>\n"
        t = getConfigEntry(section, "WiFiServerActivation", "upper" )
        if t != "WARNING":
            if t == "YES":
                g.Devices["WiFiServer"][g.ACTIV] = True

        if g.Devices["WiFiServer"][g.ACTIV]: # show the other stuff only if activated
            dprint(infostrHeader.format("WiFiServer Device", ""))

            # WiFiServer
            wsl = []
            option = "WiFiServer"
            if config.has_option(section, option):      # check if option WiFiServer exists
                t = getConfigEntry(section, option, "str" )
                if t != "WARNING":
                    wsl = t.split("\n")[:12]            # no more than 12 lines
            else:
                dprint(infostr.format("WiFiServer", "Option does not exist"))
                if g.configAlerts == "":
                    g.configAlerts += WiFiServerErrmsg
                option = "WiFiServer"
                errmsg = "Section: {}, Option: {}\nProblem: WiFiServer is activated, but has no configuration\n\n".format(section, option)
                g.configAlerts += errmsg

            # print("wsl: ", wsl)
            # for a in wsl: print("-----wsl: ", a)

            WiFiServerCount = len(wsl)
            if wsl[0] == "":
                dprint(infostr.format("WiFiServer", "No WiFiservers were defined"))
                if g.configAlerts == "":
                    g.configAlerts += WiFiServerErrmsg
                option = "WiFiServer"
                errmsg = "Section: {}, Option: {}\nProblem: WiFiServer is activated, but no WiFiServers were defined\n\n".format(section, option)
                g.configAlerts += errmsg

            for i in range(WiFiServerCount):

                wsList = wsl[i].replace(" ", "").split(",", 4)
                # print("wsList: ", wsList)

                if "y" in wsList[0]: # check only if current WiFiServer is activated
                # Port check
                    if 0 <= int(wsList[2]) <= 65535:
                        pass
                        # print("valid Port")
                    else:
                        rdprint("INVALID Port")
                        if g.configAlerts == "":
                            g.configAlerts += WiFiServerErrmsg
                        option = "WiFiServer#" + str(i)
                        errmsg = "Section: {}, Option: {}\nProblem: has invalid Port: {}\n\n".format(section, option, wsList[2])
                        g.configAlerts += errmsg

                # Folder cleanup
                    wsList[3] = wsList[3].replace(" ", "").strip("/")

                # checking vars
                    VarsAsList = []
                    for i, cVars in enumerate(wsList[4].split(",")):
                        cname = cVars.strip()
                        if  cname in g.VarsCopy:
                            # Variable name is ok
                            pass
                        else:
                            # Variable name is NOT ok
                            rdprint("Unknown Variable {} ".format(cname))
                            if g.configAlerts == "":   g.configAlerts += WiFiServerErrmsg
                            option = "WiFiServer#" + str(i)
                            errmsg = "Section: {}, Option: {}\nProblem: has wrong value:".format(section, option)
                            g.configAlerts += errmsg + "  ILLEGAL Variable {} ".format(cname)
                            cname = "None"

                        VarsAsList.append(cname)

                    wsList[4] = VarsAsList
                    g.WiFiServerList.append(wsList)

            # printout
            for w in g.WiFiServerList:
                dprint(infostr.format("WiFiServer", w))


    # WiFiClient
        t = getConfigEntry("WiFiClientDevice", "WiFiClientActivation", "upper" )
        if t != "WARNING":
            if t == "YES":
                g.Devices["WiFiClient"][2] = True

        if g.Devices["WiFiClient"][2]: # show the other stuff only if activated
            dprint(infostrHeader.format("WiFiClient Device", ""))

            # WiFiClient Server Port
            t = getConfigEntry("WiFiClientDevice", "WiFiClientPort", "upper" )
            if t != "WARNING":
                if t == 'AUTO':                             g.WiFiClientPort = "auto"
                else:
                    try:
                        if float(t) > 0:                    g.WiFiClientPort = int(float(t))
                        else:                               g.WiFiClientPort = "auto"  # if zero or negative value given
                    except:                                 g.WiFiClientPort = "auto"
                dprint(infostr.format("WiFiClientPort",     g.WiFiClientPort ))


            # WiFiClient Type
            t = getConfigEntry("WiFiClientDevice", "WiFiClientType", "upper" )
            if t != "WARNING":
                if t == "GENERIC":                          g.WiFiClientType = "GENERIC"
                else:                                       g.WiFiClientType = "GMC"
                dprint(infostr.format("WiFiClientType",     g.WiFiClientType))

            # GENERIC  - WiFiClient variables for WiFiClientType = "GENERIC"
            if g.WiFiClientType == "GENERIC":
                t = getConfigEntry("WiFiClientDevice", "WiFiClientVariablesGENERIC", "str" )
                if t != "WARNING":
                    if t.upper() == "AUTO":                     g.WiFiClientVariables = "auto"
                    else:                                       g.WiFiClientVariables = correctVariableCaps(t)
                    dprint(infostr.format("WiFiClientVariables",g.WiFiClientVariables))

            # GMC  - WiFiClient variables for WiFiClientType = "GMC"
            else:
                t = getConfigEntry("WiFiClientDevice", "WiFiClientVariablesGMC", "str" )
                if t != "WARNING":
                    if t.upper() == "AUTO":                     g.WiFiClientMapping = "auto"
                    else:                                       g.WiFiClientMapping = t
                    dprint(infostr.format("WiFiClientMapping",  g.WiFiClientMapping))



    # RaspiPulse
        # RaspiPulse Activation
        t = getConfigEntry("RaspiPulseDevice", "RaspiPulseActivation", "upper" )
        if t != "WARNING":
            if t == "YES":
                g.Devices["RaspiPulse"][2] = True

        if g.Devices["RaspiPulse"][2]: # show the other stuff only if activated
            dprint(infostrHeader.format("RaspiPulse Device", ""))

            # RaspiPulse Server Pin
            t = getConfigEntry("RaspiPulseDevice", "RaspiPulsePin", "upper" )
            if t != "WARNING":
                if t == 'AUTO':                             g.RaspiPulsePin = "auto"
                else:
                    try:
                        if float(t) > 0:                    g.RaspiPulsePin = int(float(t))
                        else:                               g.RaspiPulsePin = "auto"  # if zero or negative value given
                    except:                                 g.RaspiPulsePin = "auto"
                dprint(infostr.format("RaspiPulsePin",      g.RaspiPulsePin))

            # RaspiPulse Edge
            t = getConfigEntry("RaspiPulseDevice", "RaspiPulseEdge", "upper" )
            if t != "WARNING":
                if   t == "AUTO":                           g.RaspiPulseEdge = "auto"
                elif t in ("RISING", "FALLING"):            g.RaspiPulseEdge = t
                else:                                       g.RaspiPulseEdge = "auto"
                dprint(infostr.format("RaspiPulseEdge",     g.RaspiPulseEdge))

            # RaspiPulse variables
            t = getConfigEntry("RaspiPulseDevice", "RaspiPulseVariables", "str" )
            if t != "WARNING":
                if t.upper() == "AUTO":                     g.RaspiPulseVariables = "auto"
                else:                                       g.RaspiPulseVariables = correctVariableCaps(t)
                dprint(infostr.format("RaspiPulseVariables", g.RaspiPulseVariables))



    # I2CDevice
        # I2C variables:  included in sensors settings
        t = getConfigEntry("I2CDevice", "I2CActivation", "upper" )
        if t != "WARNING":
            if t == "YES":
                g.Devices["I2C"][2] = True

        if g.Devices["I2C"][2]: # show the other stuff only if activated
            dprint(infostrHeader.format("I2CSensor Device", ""))

            # I2C Dongle - ISS, ELV, IOW
            t = getConfigEntry("I2CDevice", "I2CDongle", "upper" )
            if t != "WARNING":
                t = t.strip()
                try:
                    # if t in ["ISS", "ELV", "IOW", "FTD"]:   g.I2CDongleCode = t  # no FTD support
                    if t in ["ISS", "ELV", "IOW"]:          g.I2CDongleCode = t
                    else:                                   g.I2CDongleCode = "ISS"
                except:
                    g.I2CDongleCode = "ISS"
                dprint(infostr.format("Dongle",   g.I2CDongleCode))


            # I2C usbport
            t = getConfigEntry("I2CDevice", "I2Cusbport", "str" )
            if t != "WARNING":
                if t.upper() == "AUTO":                     g.I2Cusbport = "auto"
                else:                                       g.I2Cusbport = t
                dprint(infostr.format("Serial Port",        g.I2Cusbport))


            # I2C Sensors Options (3 sep by comma):  < yes | no > , <Sensor Addr in hex>, <variables>
            # like: I2CSensorBME280  = y, 0x76, Temp, Press, Humid
            # here 'y' and 'n' can be used for 'yes' and 'no'

            # I2C Sensors - LM75, addr 0x48 | 0x49 | 0x4A | 0x4B | 0x4C | 0x4E | 0x4F
            # like: I2CSensorLM75      = yn, 0x48, CPS3rd
            t = getConfigEntry("I2CDevice", "I2CSensorLM75", "str" )
            if t != "WARNING":
                t = t.split(",")
                try:
                    if "Y" in t[0].strip().upper():         g.I2CSensor["LM75"][0] = True
                    else:                                   g.I2CSensor["LM75"][0] = False
                    g.I2CSensor["LM75"][1] = int(t[1], 16)
                except:
                    g.I2CSensor["LM75"][0] = False
                    g.I2CSensor["LM75"][1] = 0x48
                g.I2CSensor["LM75"][2] = t[2:]
                dprint(infostr.format("SensorLM75",         g.I2CSensor["LM75"]))


            # I2C Sensors - BME280, addr 0x76 | 0x77
            # I2CSensorBME280 : [True, 118, [' Temp', ' Press', ' Humid']]
            t = getConfigEntry("I2CDevice", "I2CSensorBME280", "str" )
            if t != "WARNING":
                t = t.split(",")
                try:
                    if "Y" in t[0].strip().upper():         g.I2CSensor["BME280"][0] = True
                    else:                                   g.I2CSensor["BME280"][0] = False
                    g.I2CSensor["BME280"][1] = int(t[1], 16)
                except:
                    g.I2CSensor["BME280"][0] = False
                    g.I2CSensor["BME280"][1] = 0x76
                g.I2CSensor["BME280"][2] = t[2:]
                dprint(infostr.format("SensorBME280",       g.I2CSensor["BME280"]))


            # I2C Sensors - SCD41, addr 0x62
            t = getConfigEntry("I2CDevice", "I2CSensorSCD41", "str" )
            if t != "WARNING":
                t = t.split(",")
                try:
                    if "Y" in t[0].strip().upper():         g.I2CSensor["SCD41"][0] = True
                    else:                                   g.I2CSensor["SCD41"][0] = False
                    g.I2CSensor["SCD41"][1] = int(t[1], 16)
                except:
                    g.I2CSensor["SCD41"][0] = False
                    g.I2CSensor["SCD41"][1] = 0x29
                g.I2CSensor["SCD41"][2] = t[2:]
                dprint(infostr.format("SensorSCD41",        g.I2CSensor["SCD41"]))

            # I2C Sensors - SCD30, addr 0x61
            t = getConfigEntry("I2CDevice", "I2CSensorSCD30", "str" )
            if t != "WARNING":
                t = t.split(",")
                try:
                    if "Y" in t[0].strip().upper():         g.I2CSensor["SCD30"][0] = True
                    else:                                   g.I2CSensor["SCD30"][0] = False
                    g.I2CSensor["SCD30"][1] = int(t[1], 16)
                except:
                    g.I2CSensor["SCD30"][0] = False
                    g.I2CSensor["SCD30"][1] = 0x61
                g.I2CSensor["SCD30"][2] = t[2:]
                dprint(infostr.format("SensorSCD30",        g.I2CSensor["SCD30"]))

            # I2C Sensors - TSL2591, addr 0x29
            t = getConfigEntry("I2CDevice", "I2CSensorTSL2591", "str" )
            if t != "WARNING":
                t = t.split(",")
                try:
                    if "Y" in t[0].strip().upper():         g.I2CSensor["TSL2591"][0] = True
                    else:                                   g.I2CSensor["TSL2591"][0] = False
                    g.I2CSensor["TSL2591"][1] = int(t[1], 16)
                except:
                    g.I2CSensor["TSL2591"][0] = False
                    g.I2CSensor["TSL2591"][1] = 0x29
                g.I2CSensor["TSL2591"][2] = t[2:]
                dprint(infostr.format("SensorTSL2591",      g.I2CSensor["TSL2591"]))


            # I2C Sensors - BH1750, addr 0x23 oder 0x5C
            t = getConfigEntry("I2CDevice", "I2CSensorBH1750", "str" )
            if t != "WARNING":
                t = t.split(",")
                try:
                    if "Y" in t[0].strip().upper():         g.I2CSensor["BH1750"][0] = True
                    else:                                   g.I2CSensor["BH1750"][0] = False
                    g.I2CSensor["BH1750"][1] = int(t[1], 16)
                except:
                    g.I2CSensor["BH1750"][0] = False
                    g.I2CSensor["BH1750"][1] = 0x23
                g.I2CSensor["BH1750"][2] = t[2:]
                dprint(infostr.format("SensorBH1750",       g.I2CSensor["BH1750"]))


            # I2C Sensors - GDK101, addr 0x18
            t = getConfigEntry("I2CDevice", "I2CSensorGDK101", "str" )
            if t != "WARNING":
                t = t.split(",")
                try:
                    if "Y" in t[0].strip().upper():         g.I2CSensor["GDK101"][0] = True
                    else:                                   g.I2CSensor["GDK101"][0] = False
                    g.I2CSensor["GDK101"][1] = int(t[1], 16)
                except:
                    g.I2CSensor["GDK101"][0] = False
                    g.I2CSensor["GDK101"][1] = 0x18
                g.I2CSensor["GDK101"][2] = t[2:]           # the variables
                dprint(infostr.format("SensorGDK101",        g.I2CSensor["GDK101"]))



    # RaspiI2C
        # RaspiI2C Activation
        t = getConfigEntry("RaspiI2CDevice", "RaspiI2CActivation", "upper" )
        if t != "WARNING":
            if t == "YES":
                g.Devices["RaspiI2C"][g.ACTIV] = True

        if g.Devices["RaspiI2C"][2]: # show the other stuff only if activated
            dprint(infostrHeader.format("RaspiI2C Device", ""))


            # in config find:
            #    I2C Sensors Options (4 sep by comma):  < yes | no > , <Sensor Addr in hex>, <avg cycles>, <variables sep. by comma>
            #    like: I2CSensorBME280  = yn, 0x76, 3, Temp, Press, Humid
            #    TIP: the presence of "y" in the first column makes it a "yes"; its absence a "no"

            # RaspiI2C Sensors - LM75, addr 0x48 | 0x49 | 0x4A | 0x4B | 0x4C | 0x4E | 0x4F
            t = getConfigEntry("RaspiI2CDevice", "RaspiI2CSensorLM75", "str" )
            if t != "WARNING":
                t = t.split(",")
                try:
                    if "Y" in t[0].strip().upper():         g.RaspiI2CSensor["LM75"][1] = True
                    else:                                   g.RaspiI2CSensor["LM75"][1] = False
                    g.RaspiI2CSensor["LM75"][0] = int(t[1], 16)
                except:
                    g.RaspiI2CSensor["LM75"][1] = False
                    g.RaspiI2CSensor["LM75"][0] = 0x48
                try:
                    g.RaspiI2CSensor["LM75"][7] = int(float(t[2]))
                except:
                    pass

                g.RaspiI2CSensor["LM75"][5] = t[3:]
                dprint(infostr.format("SensorLM75",         g.RaspiI2CSensor["LM75"]))


            # RaspiI2C Sensors - BME280, addr 0x76 | 0x77
            t = getConfigEntry("RaspiI2CDevice", "RaspiI2CSensorBME280", "str" )
            if t != "WARNING":
                t = t.split(",")
                try:
                    if "Y" in t[0].strip().upper():         g.RaspiI2CSensor["BME280"][1] = True
                    else:                                   g.RaspiI2CSensor["BME280"][1] = False
                    g.RaspiI2CSensor["BME280"][0] = int(t[1], 16)
                except:
                    g.RaspiI2CSensor["BME280"][1] = False
                    g.RaspiI2CSensor["BME280"][0] = 0x76
                try:
                    g.RaspiI2CSensor["BME280"][7] = int(float(t[2]))
                except:
                    pass
                g.RaspiI2CSensor["BME280"][5] = t[3:]
                dprint(infostr.format("SensorBME280",       g.RaspiI2CSensor["BME280"]))


            # RaspiI2C Sensors - BH1750, addr 0x23 oder 0x5C
            t = getConfigEntry("RaspiI2CDevice", "RaspiI2CSensorBH1750", "str" )
            if t != "WARNING":
                t = t.split(",")
                try:
                    if "Y" in t[0].strip().upper():         g.RaspiI2CSensor["BH1750"][1] = True
                    else:                                   g.RaspiI2CSensor["BH1750"][1] = False
                    g.RaspiI2CSensor["BH1750"][0] = int(t[1], 16)
                except:
                    g.RaspiI2CSensor["BH1750"][1] = False
                    g.RaspiI2CSensor["BH1750"][0] = 0x23
                try:
                    g.RaspiI2CSensor["BH1750"][7] = int(float(t[2]))
                except:
                    pass
                g.RaspiI2CSensor["BH1750"][5] = t[3:]
                dprint(infostr.format("SensorBH1750",       g.RaspiI2CSensor["BH1750"]))


            # RaspiI2C Sensors - TSL2591, addr 0x29
            t = getConfigEntry("RaspiI2CDevice", "RaspiI2CSensorTSL2591", "str" )
            if t != "WARNING":
                t = t.split(",")
                try:
                    if "Y" in t[0].strip().upper():         g.RaspiI2CSensor["TSL2591"][1] = True
                    else:                                   g.RaspiI2CSensor["TSL2591"][1] = False
                    g.RaspiI2CSensor["TSL2591"][0] = int(t[1], 16)
                except:
                    g.RaspiI2CSensor["TSL2591"][1] = False
                    g.RaspiI2CSensor["TSL2591"][0] = 0x29
                try:
                    g.RaspiI2CSensor["TSL2591"][7] = int(float(t[2]))
                except:
                    pass
                g.RaspiI2CSensor["TSL2591"][5] = t[3:]
                dprint(infostr.format("SensorTSL2591",      g.RaspiI2CSensor["TSL2591"]))


            # RaspiI2C Sensors - BMM150, addr 0x10
            t = getConfigEntry("RaspiI2CDevice", "RaspiI2CSensorBMM150", "str" )
            if t != "WARNING":
                t = t.split(",")
                try:
                    if "Y" in t[0].strip().upper():         g.RaspiI2CSensor["BMM150"][1] = True
                    else:                                   g.RaspiI2CSensor["BMM150"][1] = False
                    g.RaspiI2CSensor["BMM150"][0] = int(t[1], 16)
                except:
                    g.RaspiI2CSensor["BMM150"][1] = False
                    g.RaspiI2CSensor["BMM150"][0] = 0x29
                try:
                    g.RaspiI2CSensor["BMM150"][7] = int(float(t[2]))
                except:
                    pass
                g.RaspiI2CSensor["BMM150"][5] = t[3:]
                dprint(infostr.format("SensorBMM150",      g.RaspiI2CSensor["BMM150"]))


            # RaspiI2C Sensors - SCD30, addr 0x61
            t = getConfigEntry("RaspiI2CDevice", "RaspiI2CSensorSCD30", "str" )
            if t != "WARNING":
                t = t.split(",")
                try:
                    if "Y" in t[0].strip().upper():         g.RaspiI2CSensor["SCD30"][1] = True
                    else:                                   g.RaspiI2CSensor["SCD30"][1] = False
                    g.RaspiI2CSensor["SCD30"][0] = int(t[1], 16)
                except:
                    g.RaspiI2CSensor["SCD30"][1] = False
                    g.RaspiI2CSensor["SCD30"][0] = 0x29
                try:
                    g.RaspiI2CSensor["SCD30"][7] = int(float(t[2]))
                except:
                    pass
                g.RaspiI2CSensor["SCD30"][5] = t[3:]
                dprint(infostr.format("SensorSCD30",      g.RaspiI2CSensor["SCD30"]))


            # RaspiI2C Sensors - SCD41, addr 0x62
            t = getConfigEntry("RaspiI2CDevice", "RaspiI2CSensorSCD41", "str" )
            if t != "WARNING":
                t = t.split(",")
                try:
                    if "Y" in t[0].strip().upper():         g.RaspiI2CSensor["SCD41"][1] = True
                    else:                                   g.RaspiI2CSensor["SCD41"][1] = False
                    g.RaspiI2CSensor["SCD41"][0] = int(t[1], 16)
                except:
                    g.RaspiI2CSensor["SCD41"][1] = False
                    g.RaspiI2CSensor["SCD41"][0] = 0x29
                try:
                    g.RaspiI2CSensor["SCD41"][7] = int(float(t[2]))
                except:
                    pass
                g.RaspiI2CSensor["SCD41"][5] = t[3:]
                dprint(infostr.format("SensorSCD41",      g.RaspiI2CSensor["SCD41"]))


            # RaspiI2C Sensors - GDK101, addr 0x18
            t = getConfigEntry("RaspiI2CDevice", "RaspiI2CSensorGDK101", "str" )
            if t != "WARNING":
                t = t.split(",")
                try:
                    if "Y" in t[0].strip().upper():         g.RaspiI2CSensor["GDK101"][1] = True
                    else:                                   g.RaspiI2CSensor["GDK101"][1] = False
                    g.RaspiI2CSensor["GDK101"][0] = int(t[1], 16)
                except:
                    g.RaspiI2CSensor["GDK101"][1] = False
                    g.RaspiI2CSensor["GDK101"][0] = 0x29
                try:
                    g.RaspiI2CSensor["GDK101"][7] = int(float(t[2]))
                except:
                    pass
                g.RaspiI2CSensor["GDK101"][5] = t[3:]
                dprint(infostr.format("SensorGDK101",      g.RaspiI2CSensor["GDK101"]))


    # RadPro
        # RadPro Activation
        t = getConfigEntry("RadProDevice", "RadProActivation", "upper" )
        if t != "WARNING":
            if t == "YES":
                g.Devices["RadPro"][g.ACTIV] = True

        if g.Devices["RadPro"][g.ACTIV]: # show the other stuff only if activated
            dprint(infostrHeader.format("RadPro Device", ""))


            # RadProPort
            t = getConfigEntry("RadProDevice", "RadProPort", "str" )
            if t != "WARNING":
                if t.upper() == "AUTO":                  g.RadProPort = "auto"
                else:                                    g.RadProPort = t
                dprint(infostr.format("RadProPort",      g.RadProPort))


            # RadProClockCorrection
            t = getConfigEntry("RadProDevice", "RadProClockCorrection", "str" )
            if t != "WARNING":
                if t.upper() == "AUTO":                  g.RadProClockCorrection = "auto"
                else:
                    try:
                        intt = int(t)
                        if 0 <= intt < 60:               g.RadProClockCorrection = int(t)
                        else:                            g.RadProClockCorrection = "auto"
                    except Exception as e:
                        exceptPrint(e, "RadProClockCorrection t:'{t}'")
                        g.RadProClockCorrection = "auto"
                dprint(infostr.format("RadProClockCorrection",  g.RadProClockCorrection))


            # RadProVariables
            t = getConfigEntry("RadProDevice", "RadProVariables", "str" )
            if t != "WARNING":
                if t.upper() == "AUTO":                  g.RadProVariables = "auto"
                else:                                    g.RadProVariables = correctVariableCaps(t)
                dprint(infostr.format("RadProVariables", g.RadProVariables))


    # End Devices *************************************************************************************

        infostrHeader = "cfg: {:35s} {}"            # back to original settings
        infostr       = "cfg:     {:35s}: {}"

#alarm
    # Alarm
        section = "Alarm"
        dprint(infostrHeader.format("Alarm", ""))

        # Alarm Activation
        t = getConfigEntry(section, "AlarmActivation", "upper" )
        # rdprint(defname, "t: ", t)
        if t != "WARNING":
            if t == "YES":                                  g.AlarmActivation = True
            else:                                           g.AlarmActivation = False

        if not g.AlarmActivation:
            dprint(infostr.format(section, "is NOT activated"))

        else:                           # show the other stuff only if activated
            # Alarm AlarmSound
            t = getConfigEntry(section, "AlarmSound", "upper" )
            if t != "WARNING":
                if t in ("YES", "NO"):                      g.AlarmSound = True if t == "YES" else False
                else:                                       g.AlarmSound = False
            dprint(infostr.format("AlarmSound",             g.AlarmSound))


            # Alarm IdleCycles
            t = getConfigEntry(section, "AlarmIdleCycles", "int" )
            if t != "WARNING":
                if t >= 0:                                  g.AlarmIdleCycles = t
            dprint(infostr.format("AlarmIdleCycles",        g.AlarmIdleCycles))


            # Alarm AlarmLimits
            for vname in g.AlarmLimits:
                avname = section + vname
                cealarm = getConfigEntry(section, avname, "upper" ).strip()
                if cealarm == "NONE" or cealarm == "":
                    g.AlarmLimits[vname] = None
                else:
                    cealarm = cealarm.split(",")
                    if len(cealarm) < 3:
                        msg  = "Section: {},  Parameter: {}<br>".format(section, avname)
                        msg += "Problem: Configuration: '{}' has not enough values<br>".format(avname)
                        msg += "Alarm will be inactivated!"
                        g.AlarmActivation = False

                        g.configAlerts += "-" * 100 + "<br>" + msg + "\n\n"
                    else:
                        try:
                            AlarmN     = clamp(int(cealarm[0]), 1, 60)
                            AlarmLower = None if cealarm[1].strip() == "NONE" else float(cealarm[1])
                            AlarmUpper = None if cealarm[2].strip() == "NONE" else float(cealarm[2])
                        except Exception as e:
                            exceptPrint(e, defname + "AlarmConfig vname: '{}".format(vname))
                            AlarmN, AlarmLower, AlarmUpper = (g.NAN, g.NAN, g.NAN)
                            msg  = "Section: {},  Parameter: {}<br>".format(section, avname)
                            msg += "Problem: Configuration: '{}' values must be numeric<br>".format(avname)
                            msg += "Alarm will be inactivated!"
                            g.AlarmActivation = False
                            g.configAlerts += "-" * 100 + "<br>" + msg + "\n\n"

                        g.AlarmLimits[vname] = [AlarmN, AlarmLower, AlarmUpper]

                dprint(infostr.format(avname, g.AlarmLimits[vname]))


    # EMAIL
        cfgnames  = ["Protocol", "Host", "Port", "From", "To", "Password" ]
        section   = "Email"

        dprint(infostrHeader.format(section, ""))

        # Email Activation
        t = getConfigEntry(section, "emailActivation", "upper" )
        if t != "WARNING":
            if t == "YES":
                g.emailActivation = True
                g.emailUsage      = True       # for convenience; also set for usage
        # rdprint(defname, "1   g.emailActivation: ", g.emailActivation)

        if not g.emailActivation:
            dprint(infostr.format(section, "is NOT activated"))
            # rdprint(defname, "2   g.emailActivation: ", g.emailActivation)

        else:                           # show the other stuff only if activated
            # rdprint(defname, "3   else g.emailActivation: ", g.emailActivation)
            parameter = "emailReadFromFile"
            t = getConfigEntry(section, parameter, "str" )
            # rdprint(defname, "emailReadFromFile: ", t)
            if t != "WARNING" and t > "":
                try:
                    g.emailReadFromFile = t
                    with open(t) as f:
                        while True:
                            t1 = f.readline().strip()
                            if t1 > "" and not t1.startswith("#"): break

                except Exception as e:
                    exceptPrint(e, "emailReadFromFile failed with exception")
                    msg  = "\n<b>Problems in GeigerLog Configuration File</b>\n\n"
                    msg += "Section: {},  Parameter: {}<br>".format(section, parameter)
                    msg += "Problem: File not found or not readable:<br>File: &nbsp; {}<br><br>".format(t)
                    msg += "Email will be inactivated!"
                    g.configAlerts += "-" * 100 + "<br>" + msg + "\n\n"
                    g.emailActivation = False  # inactivate due to errors in config

                else:
                    dprint(infostr.format("Read email cfg from file", g.emailReadFromFile))
                    cfgvals     = t1.strip().replace(" ", "").split(',')
                    # rdprint(defname, "cfgvals: ", cfgvals)
                    for i, emailprop in enumerate(cfgnames):
                        if i != 2:  g.email[emailprop] = cfgvals[i]                        # all strings
                        else:       g.email[emailprop] = int(cfgvals[i])                   # except Port is integer

                        if i < 5: dprint(infostr.format(emailprop, cfgvals[i]))            # show all props except password
                        else:     dprint(infostr.format(emailprop, "*********"))           # show Password only as hidden


            # t=='WARNING' - land here only if an emailReadFromFile is NOT defined
            else:
                try:
                    # emailProtocol (SMTP or SMTP_SSL)
                    g.email["Protocol"] = getConfigEntry(section, "emailProtocol",  "str" )
                    dprint(infostr.format("emailProtocol", g.email["Protocol"]))

                    # emailHost     (like: smtp.johndoe.com)
                    g.email["Host"]     = getConfigEntry(section, "emailHost",      "str" )
                    dprint(infostr.format("emailHost", g.email["Host"]))

                    # emailPort     (like: 465 (preferred) or 587 (old))
                    g.email["Port"]     = getConfigEntry(section, "emailPort",      "int" )
                    dprint(infostr.format("emailPort", g.email["Port"]))

                    # emailFrom     (Sender)
                    g.email["From"]     = getConfigEntry(section, "emailFrom",      "str" )
                    dprint(infostr.format("emailFrom", g.email["From"]))

                    # emailTo       (Recipient)
                    g.email["To"]       = getConfigEntry(section, "emailTo",        "str" )
                    dprint(infostr.format("emailTo", g.email["To"]))

                    # emailPassword (like: topsecret)
                    g.email["Password"] = getConfigEntry(section, "emailPassword",  "str" )
                    dprint(infostr.format("emailPassword", "*********"))                         # Password is: g.email["Password"]))
                except Exception as e:
                    exceptPrint(e, "bummer")


            # verify proper email settings; emailcfgOk > 0 means error
            emailcfgOk = 0
            if g.email["Protocol"] not in ("SMTP", "SMTP_SSL"): emailcfgOk += 1
            if g.email["Host"]     == ""                      : emailcfgOk += 2
            if g.email["Port"]     not in (465, 587)          : emailcfgOk += 4
            if g.email["From"]     == ""                      : emailcfgOk += 8
            if g.email["To"]       == ""                      : emailcfgOk += 16
            if g.email["Password"] == ""                      : emailcfgOk += 32

            # emailcfgOk = 255 # for testing
            if emailcfgOk > 0:
                # inactivate email since an error in config was found
                g.emailActivation = False

                # output for both terminal and HTML
                msg  = "\n<b>Problems in GeigerLog Configuration File</b>\n\n"
                msg += "Problem: Email configuration has improper settings.\n"
                msg += "Section: {}, see all Parameters marked with arrow\n".format(section)
                msg += "Email will be inactivated!\n"
                msg += "\nCurrent configuration:\n"

                # output for terminal
                cfgmsg = ""
                for i, emailprop in enumerate(cfgnames):
                    cfgmsg += "    {:10s} : {:20s}  {}\n".format(emailprop, str(g.email[emailprop]), "<---- " if (emailcfgOk & (2**i)) else "")
                edprint(msg + cfgmsg)

                # output for HTML
                cfgmsg = "<table>"
                for i, emailprop in enumerate(cfgnames):
                    cfgmsg += "<tr><td>"
                    cfgmsg += "&nbsp;" * 5 + "{:10s}</td><td> : {:20s}</td><td>{}".format(emailprop, str(g.email[emailprop]), "&lt;---- " if (emailcfgOk & (2**i)) else "")
                    cfgmsg += "</td></tr>"
                cfgmsg += "</table>"
                g.configAlerts += "-" * 100 + "<br>" + msg + cfgmsg + "\n\n"

    #### removed from code !!!!!!!!!!
    # # Telegram
    #     section   = "Telegram"
    #     dprint(infostrHeader.format(section, ""))

    #     # Telegram Activation
    #     t = getConfigEntry(section, "TelegramActivation", "upper" )
    #     if t != "WARNING":
    #         if t == "YES":                          g.TelegramActivation = True
    #     # rdprint(defname, "1   g.TelegramActivation: ", g.TelegramActivation)

    #     if not g.TelegramActivation:
    #         dprint(infostr.format(section, "is NOT activated"))
    #         # rdprint(defname, "2   g.TelegramActivation: ", g.TelegramActivation)

    #     else:
    #         # Telegram Token
    #         t = getConfigEntry(section, "TelegramToken", "str" )
    #         if t != "WARNING":
    #             g.TelegramToken = t.strip()
    #         dprint(infostr.format("TelegramToken",          g.TelegramToken))


    #         # Telegram UpdateCycle
    #         t = getConfigEntry(section, "TelegramUpdateCycle", "upper" )
    #         if t != "WARNING":
    #             if t == "AUTO":                             g.TelegramUpdateCycle = 3600
    #             else:
    #                 try:    g.TelegramUpdateCycle = float(t)
    #                 except: g.TelegramUpdateCycle = 3600
    #         dprint(infostr.format("TelegramUpdateCycle",    g.TelegramUpdateCycle))


    #         # Telegram ChatID
    #         t = getConfigEntry(section, "TelegramChatID", "str" )
    #         if t != "WARNING":
    #             g.TelegramChatID = t.strip
    #         dprint(infostr.format("TelegramChatID",    g.TelegramChatID))


#custom
    # Custom Names
        section = "Comment"
        dprint(infostrHeader.format(section, ""))

        for vname in g.VarsCopy:
            Customvname = section + vname
            t = getConfigEntry(section, Customvname, "str" )
            # rdprint(defname, "t: ", t)
            if t != "WARNING":
                g.VarsCopy[vname][6] = t[0:12]

            dprint(infostr.format(Customvname, g.VarsCopy[vname][6]))


        break # still in while loop, don't forget to break!

    setIndent(0)

# End Configuration file evaluation #############################################################################
#################################################################################################################


def readPrivateConfig():
    """reads the private.cfg file if present, and adds the definitions to the config.
    If not present, the geigerlog.cfg settings remain in use unmodified"""

    # the private file uses this format:
    # g.WiFiSSID, g.WiFiPassword, g.gmcmapUserID, g.gmcmapCounterID, g.TelegramToken
    # like:
    #       mySSID, myPW, 012345, 01234567890, 2008102243:AAHGv...kG9Pg1rfVY

    defname  = "readPrivateConfig: "
    dprint(defname)
    setIndent(1)

    filepath = os.path.join(g.progDir, "../private.cfg")
    if not os.access(filepath, os.R_OK) :
        dprint("{:25s}: {}".format(defname, "Private file is not readable"))
    else:
        dprint("{:25s}: {}".format(defname, "Private file is readable"))
        try:
            with open(filepath) as f:
                pfilecfg = f.readlines()

        except Exception as e:
            exceptPrint(e, defname + "FAILURE reading Private file")

        else:
            try:
                foundData = False
                for i, line in enumerate(pfilecfg):
                    a = line.strip()
                    if   a.startswith("#"): continue
                    elif a == "":           continue
                    else:
                        # gdprint("{:25s}: {}".format(defname, "line: {}:  {}".format(i, a[:-1])))
                        data = a.split(",")
                        if len(data) >= 4:                          # telegram token allowed to be absent
                            g.WiFiSSID         = data[0].strip()
                            g.WiFiPassword     = data[1].strip()
                            g.gmcmapUserID     = data[2].strip()
                            g.gmcmapCounterID  = data[3].strip()
                            g.TelegramToken    = data[4].strip()
                            g.TelegramChatID   = data[5].strip()
                            foundData = True
                        else:
                            dprint("{:25s}: {}".format(defname, "Not enough data in Private file"))

                if not foundData:
                    dprint("{:25s}: {}".format(defname, "Invalid Private file"))

            except Exception as e:
                exceptPrint(e, defname + "FAILURE interpreting Private file")

    setIndent(0)



