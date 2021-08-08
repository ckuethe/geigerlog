#! /usr/bin/env python3
# -*- coding: utf-8 -*-

"""
class ggeiger - A part of GeigerLog - cannot be used on its own
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

from   gsup_utils  import *

import gsup_sql
import gsup_tools
import gsup_plot

import gstat_poisson
import gstat_fft
import gstat_convfft
import gstat_synth

if gglobs.GMCActivation:                                # GMC counter
    import gdev_gmc
    import gdev_gmc_hist
if gglobs.AudioActivation:      import gdev_audio       # AudioCounter
if gglobs.RMActivation:         import gdev_radmon      # RadMon - then imports "paho.mqtt.client as mqtt"
if gglobs.AmbioActivation:      import gdev_ambiomon    # AmbioMon
if gglobs.GSActivation:         import gdev_scout      # GammaScout
if gglobs.I2CActivation:        import gdev_i2c         # I2C  - then imports dongles and sensor modules
if gglobs.LJActivation:         import gdev_labjack     # LabJack - then trys to import the LabJack modules
if gglobs.SimulActivation:      import gdev_simul       # SimulCounter
if gglobs.RaspiActivation:      import gdev_raspi       # Raspi
if gglobs.MiniMonActivation:    import gdev_minimon     # MiniMon

if gglobs.GMCActivation or gglobs.GSActivation or gglobs.I2CActivation: # GMC, GS, I2C
    import serial                       # serial port (module has name: 'pyserial'!)
    import serial.tools.list_ports      # allows listing of serial ports


class ggeiger(QMainWindow):

    def __init__(self):
        super(ggeiger, self).__init__()
        gglobs.exgg = self

        # hold the updated variable values in self.updateDisplayVariableValue()
        self.vlabels = [None] * len(gglobs.varsBook)


# font standard
        """
        # font standard
                #self.fontstd = QFont()
                #self.fontstd = QFont("Deja Vue", 10)
                #self.fontstd = QFont("pritzelbmpr", 10)
                #self.fontstd = QFont("Courier New", 10)
                #self.fontstd.setFamily('Monospace')         # options: 'Lucida'
                #self.fontstd.StyleHint(QFont.TypeWriter)   # options: QFont.Monospace, QFont.Courier
                #self.fontstd.StyleHint(QFont.Monospace)   # options: QFont.Monospace, QFont.Courier
                #self.fontstd.setStyleStrategy(QFont.PreferMatch)
                #self.fontstd.setFixedPitch(True)
                #self.fontstd.setPointSize(11) # 11 is too big
                #self.fontstd.setWeight(60)            # options: 0 (thin) ... 99 (very thick); 60:ok, 65:too fat

                gglobs.fontstd = self.fontstd
        """

        self.fatfont = QFontDatabase.systemFont(QFontDatabase.FixedFont) #
        self.fatfont.setWeight(99)            # options: 0 (thin) ... 99 (very thick); 60:ok, 65:too fat
        self.fatfont.setPointSize(12)

        #print("Platform: ", platform.platform())
        if "WINDOWS" in platform.platform().upper():
            dprint("WINDOWS: Setting QFontDatabase.FixedFont")
            self.fontstd = QFontDatabase.systemFont(QFontDatabase.FixedFont) # worked! got Courier New
            #self.fontstd = QFont("Consolas", 10) # alternative

        elif "LINUX" in platform.platform().upper():
            dprint("LINUX: Setting QFontDatabase.FixedFont")
            self.fontstd = QFontDatabase.systemFont(QFontDatabase.FixedFont) # worked! got DejaVu Sans Mono
            #self.fontstd = QFont("Mono") # alternative

        else:
            dprint("Other System: Setting QFontDatabase.FixedFont")
            self.fontstd = QFontDatabase.systemFont(QFontDatabase.FixedFont) # result ?
            #self.fontstd = QFont("Courier New") # alternative

        self.fontstd.setFixedPitch(True)
        self.fontstd.setWeight(60)

        gglobs.fontstd = self.fontstd

# window
    # icon
        self.iconGeigerLog    = QIcon(QPixmap(os.path.join(gglobs.gresPath, 'icon_geigerlog.png')))
        gglobs.iconGeigerLog  = self.iconGeigerLog
        self.setWindowIcon(gglobs.iconGeigerLog)

    #title
        wtitle = "GeigerLog v{}".format(gglobs.__version__)
        if gglobs.devel: wtitle += "  Python: {}  sys.argv: {}".format(sys.version[:6], sys.argv)
        self.setWindowTitle(wtitle)

    # screen
        screen_available = QDesktopWidget().availableGeometry()
        sw = min(gglobs.window_width  -  2, screen_available.width() )      # Frame of 1 pixel left and right
        sh = min(gglobs.window_height - 29, screen_available.height())      # Frame top + bottom + Window bar of 29 pixel
        x  = max(screen_available.width() - sw, 0)                          # should be >0 anyway
        y  = screen_available.y()

        if "WINDOWS" in platform.platform().upper(): y += 33                # some correction needed at least on Virtual Win8.1
        if "ARMV"    in platform.platform().upper(): y += 33                # some correction needed at least on Raspi 4

        self.setGeometry(x, y, sw, sh) # position window in upper right corner of screen
        #~dprint("screen Geometry: ", QDesktopWidget().screenGeometry()) # total hardware screen
        #~dprint("screen Available:", QDesktopWidget().availableGeometry()) # available screen


    #figure and its toolbar
        # a figure instance to plot on
        #~self.figure = plt.figure(facecolor = "#F9F4C9", edgecolor='lightgray', linewidth = 0.0) # light yellow face
        #~self.figure = plt.figure(facecolor = "#F9F4C9", edgecolor='lightgray', linewidth = 0.0) # light yellow face
        self.figure = plt.figure(facecolor = "#DFDEDD", edgecolor='lightgray', linewidth = 0.0, dpi=gglobs.hidpiScaleMPL) # lighter grayface
        #self.figure, self.ax1 = plt.subplots(facecolor='#DFDEDD') # lighter gray
        #plt.subplots(facecolor='#DFDEDD') # lighter gray
        plt.clf()  # must be done - clear figure or it will show an empty figure !!

        # canvas - this is the Canvas Widget that displays the `figure`
        # it takes the `figure` instance as a parameter to __init__
        # next command creates: Attribute Qt::AA_EnableHighDpiScaling must be set before QCoreApplication is created.
        self.canvas = FigureCanvas(self.figure)
        self.canvas.mpl_connect('motion_notify_event', self.updatecursorposition) # where the cursor is
        self.canvas.mpl_connect('button_press_event' , self.onclick)              # send a mouse click

        # this is the figure Navigation widget; it takes the Canvas widget and a parent
        self.navtoolbar = NavigationToolbar(self.canvas, self)
        self.navtoolbar.setToolTip("Graph Toolbar")
        self.navtoolbar.setIconSize(QSize(32,32))
        #print("self.navtoolbar.iconSize()", self.navtoolbar.iconSize())

    #self.menubar and statusbar and toolbar
        self.menubar = self.menuBar()
        self.menubar.setFocus()

        self.statusBar = QStatusBar()
        self.setStatusBar(self.statusBar)

        toolbar = self.addToolBar('File')
        toolbar.setToolTip("File Toolbar")
        toolbar.setOrientation(Qt.Horizontal) # is default; alt: Qt.Vertical
        toolbar.setIconSize(QSize(32,32))  # standard size is too small
        #print("toolbar.iconSize()", toolbar.iconSize())

    #file menu
        PlotLogAction = QAction('Plot Full Log', self)
        addMenuTip(PlotLogAction, 'Plot the complete Log file')
        PlotLogAction.triggered.connect(lambda: self.plotGraph('Log'))

        PlotHisAction = QAction('Plot Full History', self)
        addMenuTip(PlotHisAction, 'Plot the complete History file')
        PlotHisAction.triggered.connect(lambda: self.plotGraph('His'))

        editScalingAction = QAction('View and Edit Current Scaling ...', self)
        addMenuTip(editScalingAction, 'View and edit the current value- and graph-scaling settings')
        editScalingAction.triggered.connect(lambda: self.editScaling())

        PlotScatterAction = QAction('Show Scatterplot from Plot Data ...', self)
        addMenuTip(PlotScatterAction, 'Show an X-Y Scatter plot with optional polynomial fit, using data currently selected in the plot')
        PlotScatterAction.triggered.connect(lambda: gsup_tools.selectScatterPlotVars())

        PrintPlotDataAction = QAction('Show Plot Data', self)
        addMenuTip(PrintPlotDataAction, 'Show the DateTime and values of all variables as currently selected in Plot')
        PrintPlotDataAction.triggered.connect(lambda: self.showData("PlotData"))

        PrintSuStAction =  QAction('Show Plot Data Summary Statistics (SuSt)', self)
        addMenuTip(PrintSuStAction, "Shows Summary Statistics of all variables and data in the plot")
        PrintSuStAction.triggered.connect(lambda: gsup_tools.printSuSt())

        PrintStatsAction =  QAction('Show Plot Data Statistics', self)
        addMenuTip(PrintStatsAction, "Shows the Statistics of the data in the current plot")
        PrintStatsAction.triggered.connect(lambda: gsup_tools.printStats())

        PlotPoissonAction =  QAction("Show Plot Data Poisson Test", self)
        addMenuTip(PlotPoissonAction, "Shows a Poisson curve on a histogram of the data of the selected variable")
        PlotPoissonAction.triggered.connect(lambda: gstat_poisson.plotPoisson())

        PlotFFTAction =  QAction("Show Plot Data FFT && Autocorrelation", self)
        addMenuTip(PlotFFTAction, "Shows the FFT Spectra & an Autocorrelation of the data of the selected variable")
        PlotFFTAction.triggered.connect(lambda: gstat_fft.plotFFT())

#searchNotePad
        SearchNPAction = QAction("Search NotePad ...", self)
        SearchNPAction.setShortcut('Ctrl+F')
        addMenuTip(SearchNPAction, "Search NotePad for occurence of a text")
        SearchNPAction.triggered.connect(self.searchNotePad)

#saveNotePad
        SaveNPAction = QAction("Save NotePad to File", self)
        addMenuTip(SaveNPAction, "Save Content of NotePad as text file named <current filename>.notes")
        SaveNPAction.triggered.connect(self.saveNotePad)

#printNotePad
        PrintNPAction = QAction("Print NotePad ...", self)
        addMenuTip(PrintNPAction, "Print Content of NotePad to Printer or  PDF-File")
        PrintNPAction.triggered.connect(self.printNotePad)

        exitAction = QAction('Exit', self)
        exitAction.setIcon(QIcon(QPixmap(os.path.join(gglobs.gresPath, 'icon_exit.png')))) # Flat icon
        exitAction.setShortcut('Ctrl+Q')
        addMenuTip(exitAction, 'Exit the GeigerLog program')
        exitAction.triggered.connect(self.close)

        fileMenu = self.menubar.addMenu('&File')
        fileMenu.setToolTipsVisible(True)

        fileMenu.addAction(PlotLogAction)
        fileMenu.addAction(PlotHisAction)

        fileMenu.addSeparator()
        fileMenu.addAction(PrintPlotDataAction)
        fileMenu.addAction(PlotScatterAction)

        fileMenu.addSeparator()
        fileMenu.addAction(editScalingAction)
        fileMenu.addAction(PrintSuStAction)
        fileMenu.addAction(PrintStatsAction)
        fileMenu.addAction(PlotPoissonAction)
        fileMenu.addAction(PlotFFTAction)

        fileMenu.addSeparator()
        fileMenu.addAction(SearchNPAction)
        fileMenu.addAction(SaveNPAction)
        fileMenu.addAction(PrintNPAction)

        fileMenu.addSeparator()
        fileMenu.addAction(exitAction)
        #fileMenu.triggered[QAction].connect(self.processtrigger)

        toolbar.addAction(exitAction)

# Device menu
        self.toggleDeviceConnectionAction = QAction(QIcon(QPixmap(os.path.join(gglobs.gresPath, 'icon_plug_open.png'))), 'Connect / Disconnect Devices', self)
        addMenuTip(self.toggleDeviceConnectionAction, 'Toggle connection of GeigerLog with the devices')
        self.toggleDeviceConnectionAction.triggered.connect(self.toggleDeviceConnection)

        self.DeviceConnectAction = QAction(QIcon(QPixmap(os.path.join(gglobs.gresPath, 'icon_plug_open.png'))), 'Connect Devices', self)
        self.DeviceConnectAction.setShortcut('Ctrl+C')
        addMenuTip(self.DeviceConnectAction, 'Connect the computer to the devices')
        self.DeviceConnectAction.triggered.connect(lambda : self.switchConnections("ON"))

        self.DeviceDisconnectAction = QAction(QIcon(QPixmap(os.path.join(gglobs.gresPath, 'icon_plug_closed.png'))), 'Disconnect Devices', self, enabled = False)
        self.DeviceDisconnectAction.setShortcut('Ctrl+D')
        addMenuTip(self.DeviceDisconnectAction, 'Disconnect the computer from the devices')
        self.DeviceDisconnectAction.triggered.connect(lambda : self.switchConnections("OFF"))

        self.DeviceCalibAction = QAction('Set Sensitivities for Geiger Tubes ...', self, enabled = True)
        addMenuTip(self.DeviceCalibAction, 'Set sensitivities for all Geiger tubes temporarily')
        self.DeviceCalibAction.triggered.connect(self.setTubeSensitivities)

        self.DeviceMappingAction = QAction('Show Device Mappings', self, enabled = True)
        addMenuTip(self.DeviceMappingAction, 'Show the mapping of variables of the activated devices')
        self.DeviceMappingAction.triggered.connect(self.showDeviceMappings)

    # build the Device menu
        deviceMenu = self.menubar.addMenu('&Device')
        deviceMenu.setToolTipsVisible(True)

    # all devices
        deviceMenu.addAction(self.DeviceConnectAction)
        deviceMenu.addAction(self.DeviceDisconnectAction)

        deviceMenu.addSeparator()
        deviceMenu.addAction(self.DeviceMappingAction)
        deviceMenu.addAction(self.DeviceCalibAction)

        deviceMenu.addSeparator()
        # now following any device specific submenus

    # submenu GMC
        if gglobs.GMCActivation  :

            self.GMCInfoAction = QAction('Show Info', self, enabled=True)
            addMenuTip(self.GMCInfoAction, 'Show basic info on GMC device')
            self.GMCInfoAction.triggered.connect(lambda: gdev_gmc.fprintGMC_DeviceInfo(extended = False))

            self.GMCInfoActionExt = QAction('Show Extended Info', self, enabled=False)
            addMenuTip(self.GMCInfoActionExt, 'Show extended info on GMC device')
            self.GMCInfoActionExt.triggered.connect(lambda: gdev_gmc.fprintGMC_DeviceInfo(extended = True))

            self.GMCConfigEditAction = QAction("Set GMC Configuration ...", self, enabled=False)
            addMenuTip(self.GMCConfigEditAction, 'View, Edit and Set the GMC device configuration')
            self.GMCConfigEditAction.triggered.connect(lambda: gdev_gmc.editGMC_Configuration())

            self.GMCConfigAction = QAction('Show Configuration Memory', self, enabled=False)
            addMenuTip(self.GMCConfigAction, 'Show the GMC device configuration memory as binary in human readable format')
            self.GMCConfigAction.triggered.connect(gdev_gmc.printGMC_ConfigMemory)

            self.GMCONAction = QAction('Switch Power ON', self, enabled=False)
            addMenuTip(self.GMCONAction, 'Switch the GMC device power to ON')
            self.GMCONAction.triggered.connect(lambda: self.switchGMCPower("ON"))

            self.GMCOFFAction = QAction('Switch Power OFF', self, enabled=False)
            addMenuTip(self.GMCOFFAction, 'Switch the GMC device power to OFF')
            self.GMCOFFAction.triggered.connect(lambda: self.switchGMCPower("OFF"))

            self.GMCAlarmONAction = QAction('Switch Alarm ON', self, enabled=False)
            addMenuTip(self.GMCAlarmONAction, 'Switch the GMC device alarm ON')
            self.GMCAlarmONAction.triggered.connect(lambda: gdev_gmc.switchGMC_DeviceAlarm("ON"))

            self.GMCAlarmOFFAction = QAction('Switch Alarm OFF', self, enabled=False)
            addMenuTip(self.GMCAlarmOFFAction, 'Switch the GMC device alarm OFF')
            self.GMCAlarmOFFAction.triggered.connect(lambda: gdev_gmc.switchGMC_DeviceAlarm("OFF"))

            self.GMCSpeakerONAction = QAction('Switch Speaker ON', self, enabled=False)
            addMenuTip(self.GMCSpeakerONAction, 'Switch the GMC device speaker ON')
            self.GMCSpeakerONAction.triggered.connect(lambda: gdev_gmc.switchGMC_DeviceSpeaker("ON"))

            self.GMCSpeakerOFFAction = QAction('Switch Speaker OFF', self, enabled=False)
            addMenuTip(self.GMCSpeakerOFFAction, 'Switch the GMC device speaker OFF')
            self.GMCSpeakerOFFAction.triggered.connect(lambda: gdev_gmc.switchGMC_DeviceSpeaker("OFF"))

            self.GMCSavingStateAction = QAction(QIcon(QPixmap(os.path.join(gglobs.gresPath, ''))), 'Set History Saving Mode ...', self, enabled=False)
            addMenuTip(self.GMCSavingStateAction, 'Set History Saving Mode of GMC device to OFF, CPS, CPM, and CPM hourly average')
            self.GMCSavingStateAction.triggered.connect(gdev_gmc.setGMC_HistSaveMode)

            self.GMCSetTimeAction = QAction('Set Date+Time', self, enabled=False)
            addMenuTip(self.GMCSetTimeAction, 'Set the Date + Time of the GMC device to the computer time')
            self.GMCSetTimeAction.triggered.connect(gdev_gmc.setGMC_DateTime)

            self.GMCREBOOTAction = QAction('Reboot ...', self, enabled=False)
            addMenuTip(self.GMCREBOOTAction, 'Send REBOOT command to the GMC device')
            self.GMCREBOOTAction.triggered.connect(lambda: gdev_gmc.doREBOOT())

            self.GMCFACTORYRESETAction = QAction('FACTORYRESET ...', self, enabled=False)
            addMenuTip(self.GMCFACTORYRESETAction, 'Send FACTORYRESET command to the GMC device')
            self.GMCFACTORYRESETAction.triggered.connect(lambda: gdev_gmc.doFACTORYRESET(False))

            self.GMCFACTORYRESET_forceAction = QAction('FACTORYRESET force', self, enabled=True)
            addMenuTip(self.GMCFACTORYRESET_forceAction, 'Send FACTORYRESET command to the GMC device')
            self.GMCFACTORYRESET_forceAction.triggered.connect(lambda: gdev_gmc.doFACTORYRESET(True))

            deviceSubMenuGMC = deviceMenu.addMenu("GMC Series")
            deviceSubMenuGMC.setToolTipsVisible(True)
            deviceSubMenuGMC.addAction(self.GMCInfoAction)
            deviceSubMenuGMC.addAction(self.GMCInfoActionExt)
            deviceSubMenuGMC.addAction(self.GMCConfigEditAction)
            deviceSubMenuGMC.addAction(self.GMCConfigAction)

            if gglobs.devel:
                deviceSubMenuGMC.addAction(self.GMCONAction)
                deviceSubMenuGMC.addAction(self.GMCOFFAction)
                deviceSubMenuGMC.addAction(self.GMCAlarmONAction)
                deviceSubMenuGMC.addAction(self.GMCAlarmOFFAction)
                deviceSubMenuGMC.addAction(self.GMCSpeakerONAction)
                deviceSubMenuGMC.addAction(self.GMCSpeakerOFFAction)
                deviceSubMenuGMC.addAction(self.GMCSavingStateAction)

            deviceSubMenuGMC.addAction(self.GMCSetTimeAction)
            deviceSubMenuGMC.addAction(self.GMCREBOOTAction)
            deviceSubMenuGMC.addAction(self.GMCFACTORYRESETAction)
            if gglobs.devel:    # Factory Reset without checking
                deviceSubMenuGMC.addAction(self.GMCFACTORYRESET_forceAction)
            #deviceMenu.triggered[QAction].connect(self.processtrigger)

    # submenu AudioCounter
        if gglobs.AudioActivation :

            self.AudioInfoAction = QAction('Show Info', self, enabled=True)
            addMenuTip(self.AudioInfoAction, 'Show basic info on AudioCounter device')
            self.AudioInfoAction.triggered.connect(lambda: gdev_audio.printAudioDevInfo(extended = False))

            self.AudioInfoActionExt = QAction('Show Extended Info', self, enabled=False)
            addMenuTip(self.AudioInfoActionExt, 'Show extended info on AudioCounter device')
            self.AudioInfoActionExt.triggered.connect(lambda: gdev_audio.printAudioDevInfo(extended = True))

            self.AudioPlotAction = QAction("Plot Pulse", self, enabled=False)
            addMenuTip(self.AudioPlotAction, 'Plot the audio pulse recordings of the AudioCounter Device')
            self.AudioPlotAction.triggered.connect(lambda: gdev_audio.reloadAudioData("Recording"))

            self.AudioSignalAction = QAction("Show Live Audio Signal", self, enabled=False)
            addMenuTip(self.AudioSignalAction, 'Show the live, raw audio signal as received by the audio input')
            self.AudioSignalAction.triggered.connect(lambda: gdev_audio.showLiveAudioSignal())

            self.AudioEiaAction = QAction("Eia", self, enabled=False)
            self.AudioEiaAction.triggered.connect(lambda: gdev_audio.showAudioEia())

            deviceSubMenuAudio  = deviceMenu.addMenu("AudioCounter Series")
            deviceSubMenuAudio.setToolTipsVisible(True)
            deviceSubMenuAudio.addAction(self.AudioInfoAction)
            deviceSubMenuAudio.addAction(self.AudioInfoActionExt)
            deviceSubMenuAudio.addAction(self.AudioPlotAction)
            #deviceSubMenuAudio.addAction(self.AudioSignalAction)
            if gglobs.AudioOei:
                deviceSubMenuAudio.addAction(self.AudioEiaAction)

    # submenu RadMon
        if gglobs.RMActivation  :

            self.RMInfoAction = QAction('Show Info', self, enabled=True)
            addMenuTip(self.RMInfoAction, 'Show basic info on RadMon device')
            self.RMInfoAction.triggered.connect(lambda: gdev_radmon.printRMDevInfo(extended=False))

            self.RMInfoActionExt = QAction('Show Extended Info', self, enabled=False)
            addMenuTip(self.RMInfoActionExt, 'Show extended info on RadMon device')
            self.RMInfoActionExt.triggered.connect(lambda: gdev_radmon.printRMDevInfo(extended = True))

            deviceSubMenuRM  = deviceMenu.addMenu("RadMon Series")
            deviceSubMenuRM.setToolTipsVisible(True)
            deviceSubMenuRM.addAction(self.RMInfoAction)
            deviceSubMenuRM.addAction(self.RMInfoActionExt)

    # submenu AmbioMon
        if gglobs.AmbioActivation  :

            self.AmbioInfoAction = QAction('Show Info', self, enabled=True)
            addMenuTip(self.AmbioInfoAction, 'Show basic info on AmbioMon device')
            self.AmbioInfoAction.triggered.connect(lambda: gdev_ambiomon.printAmbioInfo(extended=False))

            self.AmbioInfoActionExt = QAction('Show Extended Info', self, enabled=False)
            addMenuTip(self.AmbioInfoActionExt, 'Show extended info on AmbioMon device')
            self.AmbioInfoActionExt.triggered.connect(lambda: gdev_ambiomon.printAmbioInfo(extended = True))

            self.AMsetServerIP = QAction('Set AmbioMon Device IP ...', self, enabled=True)
            addMenuTip(self.AMsetServerIP, 'Set the IP address or Domain Name of the AmbioMon device')
            self.AMsetServerIP.triggered.connect(gdev_ambiomon.setAmbioServerIP)

            self.AmbioDataModeAction = QAction('Select AmbioMon Data Type Mode ...', self, enabled=False)
            addMenuTip(self.AmbioDataModeAction, "Select what type of data the AmbioMon device sends during logging: 'LAST' for last available data value, or 'AVG' for last 1 minute average of values")
            self.AmbioDataModeAction.triggered.connect(gdev_ambiomon.setAmbioLogDatatype)

            deviceSubMenuAmbio  = deviceMenu.addMenu("AmbioMon Series")
            deviceSubMenuAmbio.setToolTipsVisible(True)
            deviceSubMenuAmbio.addAction(self.AmbioInfoAction)
            deviceSubMenuAmbio.addAction(self.AmbioInfoActionExt)
            deviceSubMenuAmbio.addAction(self.AMsetServerIP)
            deviceSubMenuAmbio.addAction(self.AmbioDataModeAction)


    # submenu Gamma-Scout counter
        if gglobs.GSActivation  :

            self.GSInfoAction = QAction('Show Info', self, enabled=True)
            addMenuTip(self.GSInfoAction, 'Show basic info on GS device')
            self.GSInfoAction.triggered.connect(lambda: gdev_scout.printGSDevInfo(extended = False))

            self.GSInfoActionExt = QAction('Show Extended Info', self, enabled=False)
            addMenuTip(self.GSInfoActionExt, 'Show extended info on GS device')
            self.GSInfoActionExt.triggered.connect(lambda: gdev_scout.printGSDevInfo(extended = True))

            self.GSResetAction = QAction('Set to Normal Mode', self, enabled=False)
            addMenuTip(self.GSResetAction, 'Set the Gamma-Scout counter to its Normal Mode')
            self.GSResetAction.triggered.connect(lambda: gdev_scout.GSsetMode("Normal"))

            self.GSSetPCModeAction = QAction('Set to PC Mode', self, enabled=False)
            addMenuTip(self.GSSetPCModeAction, 'Set the Gamma-Scout counter to its PC Mode')
            self.GSSetPCModeAction.triggered.connect(lambda: gdev_scout.GSsetMode("PC"))

            self.GSDateTimeAction = QAction('Set Date+Time', self, enabled=False)
            addMenuTip(self.GSDateTimeAction, 'Set the Gamma-Scout counter clock to the computer time')
            self.GSDateTimeAction.triggered.connect(lambda: gdev_scout.setGSDateTime())

            self.GSSetOnlineAction = QAction('Set to Online Mode ...', self, enabled=False)
            addMenuTip(self.GSSetOnlineAction, "Set the Gamma-Scout counter to its Online Mode\nAvailable only for 'Online' models")
            self.GSSetOnlineAction.triggered.connect(lambda: gdev_scout.GSsetMode("Online"))

            self.GSRebootAction = QAction('Reboot', self, enabled=False)
            addMenuTip(self.GSRebootAction, "Do a Gamma-Scout reboot as warm-start\nAvailable only for 'Online' models")
            self.GSRebootAction.triggered.connect(lambda: gdev_scout.GSreboot())

            deviceSubMenuGS  = deviceMenu.addMenu("Gamma-Scout Series")
            deviceSubMenuGS.setToolTipsVisible(True)
            deviceSubMenuGS.addAction(self.GSInfoAction)
            deviceSubMenuGS.addAction(self.GSInfoActionExt)
            deviceSubMenuGS.addAction(self.GSDateTimeAction)
            deviceSubMenuGS.addAction(self.GSResetAction)
            deviceSubMenuGS.addAction(self.GSSetPCModeAction)
            deviceSubMenuGS.addAction(self.GSSetOnlineAction)
            deviceSubMenuGS.addAction(self.GSRebootAction)

    # submenu LabJack
        if gglobs.LJActivation  :

            self.LJInfoAction = QAction('Show Info', self, enabled=True)
            addMenuTip(self.LJInfoAction, 'Show basic info on LabJack device')
            self.LJInfoAction.triggered.connect(lambda: gdev_labjack.printLJDevInfo(extended = False))

            self.LJInfoActionExt = QAction('Show Extended Info', self, enabled=False)
            addMenuTip(self.LJInfoActionExt, 'Show extended info on LabJack device')
            self.LJInfoActionExt.triggered.connect(lambda: gdev_labjack.printLJDevInfo(extended = True))

            deviceSubMenuLJ  = deviceMenu.addMenu("LabJack Series")
            deviceSubMenuLJ.setToolTipsVisible(True)
            deviceSubMenuLJ.addAction(self.LJInfoAction)
            deviceSubMenuLJ.addAction(self.LJInfoActionExt)

    # submenu I2CSensors
        if gglobs.I2CActivation :

            self.I2CInfoAction = QAction('Show Info', self, enabled=True)
            addMenuTip(self.I2CInfoAction, 'Show basic info on I2C device')
            self.I2CInfoAction.triggered.connect(lambda: gdev_i2c.printI2CDevInfo(extended = False))

            self.I2CInfoActionExt = QAction('Show Extended Info', self, enabled=False)
            addMenuTip(self.I2CInfoActionExt, 'Show extended info on I2C device')
            self.I2CInfoActionExt.triggered.connect(lambda: gdev_i2c.printI2CDevInfo(extended = True))

            self.I2CResetAction = QAction('Reset System', self, enabled=False)
            addMenuTip(self.I2CResetAction, 'Reset the I2C ELV dongle and sensors')
            self.I2CResetAction.triggered.connect(lambda: gdev_i2c.resetI2C())

            deviceSubMenuI2C  = deviceMenu.addMenu("I2CSensors Series")
            deviceSubMenuI2C.setToolTipsVisible(True)
            deviceSubMenuI2C.addAction(self.I2CInfoAction)
            deviceSubMenuI2C.addAction(self.I2CInfoActionExt)
            deviceSubMenuI2C.addAction(self.I2CResetAction)

    # submenu Raspi
        if gglobs.RaspiActivation  :

            self.RaspiInfoAction = QAction('Show Info', self, enabled=True)
            addMenuTip(self.RaspiInfoAction, 'Show basic info on Raspi device')
            self.RaspiInfoAction.triggered.connect(lambda: gdev_raspi.printRaspiDevInfo(extended = False))

            self.RaspiInfoActionExt = QAction('Show Extended Info', self, enabled=False)
            addMenuTip(self.RaspiInfoActionExt, 'Show extended info on Raspi device')
            self.RaspiInfoActionExt.triggered.connect(lambda: gdev_raspi.printRaspiDevInfo(extended = True))

            deviceSubMenuRaspi  = deviceMenu.addMenu("Raspi Series")
            deviceSubMenuRaspi.setToolTipsVisible(True)
            deviceSubMenuRaspi.addAction(self.RaspiInfoAction)
            deviceSubMenuRaspi.addAction(self.RaspiInfoActionExt)


    # submenu MiniMon
        if gglobs.MiniMonActivation :

            self.MiniMonInfoAction = QAction('Show Info', self, enabled=True)
            addMenuTip(self.MiniMonInfoAction, 'Show basic info on MiniMon device')
            self.MiniMonInfoAction.triggered.connect(lambda: gdev_minimon.printMiniMonInfo(extended = False))

            #~self.MiniMonInfoActionExt = QAction('Show Extended Info', self, enabled=False)
            #~addMenuTip(self.MiniMonInfoActionExt, 'Show extended info on MiniMonCounter device')
            #~self.MiniMonInfoActionExt.triggered.connect(lambda: gdev_simul.printMiniMonDevInfo(extended = True))

            deviceSubMenuMiniMon  = deviceMenu.addMenu("MiniMon Series")
            deviceSubMenuMiniMon.setToolTipsVisible(True)
            deviceSubMenuMiniMon.addAction(self.MiniMonInfoAction)


    # submenu SimulCounter
        if gglobs.SimulActivation :

            self.SimulInfoAction = QAction('Show Info', self, enabled=True)
            addMenuTip(self.SimulInfoAction, 'Show basic info on SimulCounter device')
            self.SimulInfoAction.triggered.connect(lambda: gdev_simul.fprintSimulCounterInfo(extended = False))

            #~self.SimulInfoActionExt = QAction('Show Extended Info', self, enabled=False)
            #~addMenuTip(self.SimulInfoActionExt, 'Show extended info on SimulCounter device')
            #~self.SimulInfoActionExt.triggered.connect(lambda: gdev_simul.fprintSimulCounterInfo(extended = True))

            self.SimulSettings = QAction("Set Properties ...", self, enabled=False)
            addMenuTip(self.SimulSettings, 'Set SimulCounter Parameters for Meand and Prediction Limit')
            self.SimulSettings.triggered.connect(gdev_simul.getSimulProperties)

            deviceSubMenuSimul  = deviceMenu.addMenu("SimulCounter Series")
            deviceSubMenuSimul.setToolTipsVisible(True)
            deviceSubMenuSimul.addAction(self.SimulInfoAction)
            deviceSubMenuSimul.addAction(self.SimulSettings)


    # widgets for device in toolbar
        devBtnSize = 60
        # !!! MUST NOT have a colon ':' after QPushButton !!!
        self.dbtnStyleSheetON    = "QPushButton {margin-right:5px; background-color: #12cc3d; border-radius: 2px; border:1px solid silver; color: black; font-size:14px; font-weight:bold}"
        self.dbtnStyleSheetOFF   = "QPushButton {margin-right:5px;  }"
        self.dbtnStyleSheetError = "QPushButton {margin-right:5px; background-color: #ff3333; border-radius: 2px; border:1px solid silver; color: black; font-size:14px; font-weight:bold}"

        self.dbtnGMCPower = QPushButton()
        self.dbtnGMCPower.setIcon(QIcon(QPixmap(os.path.join(gglobs.gresPath, 'icon_power-round_off.png'))))
        self.dbtnGMCPower.setFixedSize(32,33)
        self.dbtnGMCPower.setEnabled(False)
        self.dbtnGMCPower.setStyleSheet("QPushButton {margin-right:1px; border:0px; }")
        self.dbtnGMCPower.setIconSize(QSize(31,31))
        self.dbtnGMCPower.setToolTip ('Toggle GMC Device Power ON / OFF')
        self.dbtnGMCPower.setAutoFillBackground(True) # This is important!! Why???
        self.dbtnGMCPower.clicked.connect(lambda: self.toggleGMCPower())

        self.connectTextGMC = 'GMC'
        self.dbtnGMC = QPushButton(self.connectTextGMC)
        self.dbtnGMC.setFixedSize(devBtnSize,32)
        self.dbtnGMC.setToolTip("GMC Device - Turns green once a connection is made - click for info")
        self.dbtnGMC.setStyleSheet(self.dbtnStyleSheetOFF)
        self.dbtnGMC.setAutoFillBackground(True) # This is important!! Why???
        self.dbtnGMC.clicked.connect(lambda: gdev_gmc.fprintGMC_DeviceInfo(extended=False))

        self.connectTextAudio = 'Audio'
        self.dbtnAudio =  QPushButton(self.connectTextAudio)
        self.dbtnAudio.setFixedSize(devBtnSize, 32)
        self.dbtnAudio.setToolTip("AudioCounter Device - Turns green once a connection is made - click for info")
        self.dbtnAudio.setStyleSheet(self.dbtnStyleSheetOFF)
        self.dbtnAudio.setAutoFillBackground(True) # 'This is important!!'  Why???
        self.dbtnAudio.clicked.connect(lambda: gdev_audio.printAudioDevInfo())

        self.connectTextRM = 'RadM'
        self.dbtnRM =  QPushButton(self.connectTextRM)
        self.dbtnRM.setFixedSize(devBtnSize,32)
        self.dbtnRM.setToolTip("RadMon Device - Turns green once a connection is made - click for info")
        self.dbtnRM.setStyleSheet(self.dbtnStyleSheetOFF)
        self.dbtnRM.setAutoFillBackground(True) # 'This is important!!'  Why???
        self.dbtnRM.clicked.connect(lambda: gdev_radmon.printRMDevInfo())

        self.connectTextAmbio = 'Ambio'
        self.dbtnAmbio =  QPushButton(self.connectTextAmbio)
        self.dbtnAmbio.setFixedSize(devBtnSize, 32)
        self.dbtnAmbio.setToolTip("AmbioMon Device - Turns green once a connection is made - click for info")
        self.dbtnAmbio.setStyleSheet(self.dbtnStyleSheetOFF)
        self.dbtnAmbio.setAutoFillBackground(True) # 'This is important!!'  Why???
        self.dbtnAmbio.clicked.connect(lambda: gdev_ambiomon.printAmbioInfo())

        self.connectTextGS = 'GS'
        self.dbtnGS =  QPushButton(self.connectTextGS)
        self.dbtnGS.setFixedSize(devBtnSize, 32)
        self.dbtnGS.setToolTip("GS Device - Turns green once a connection is made - click for info")
        self.dbtnGS.setStyleSheet(self.dbtnStyleSheetOFF)
        self.dbtnGS.setAutoFillBackground(True) # 'This is important!!'  Why???
        self.dbtnGS.clicked.connect(lambda: gdev_scout.printGSDevInfo())

        self.connectTextI2C = 'I2C'
        self.dbtnI2C =  QPushButton(self.connectTextI2C)
        self.dbtnI2C.setFixedSize(devBtnSize, 32)
        self.dbtnI2C.setToolTip("I2C Device - Turns green once a connection is made - click for info")
        self.dbtnI2C.setStyleSheet(self.dbtnStyleSheetOFF)
        self.dbtnI2C.setAutoFillBackground(True) # 'This is important!!'  Why???
        self.dbtnI2C.clicked.connect(lambda: gdev_i2c.printI2CDevInfo())

        self.connectTextLJ = 'LabJ'
        self.dbtnLJ =  QPushButton(self.connectTextLJ)
        self.dbtnLJ.setFixedSize(devBtnSize, 32)
        self.dbtnLJ.setToolTip("LabJack Device - Turns green once a connection is made - click for info")
        self.dbtnLJ.setStyleSheet(self.dbtnStyleSheetOFF)
        self.dbtnLJ.setAutoFillBackground(True) # 'This is important!!'  Why???
        self.dbtnLJ.clicked.connect(lambda: gdev_labjack.printLJDevInfo())

        self.connectTextRaspi = 'Raspi'
        self.dbtnRaspi = QPushButton(self.connectTextRaspi)
        self.dbtnRaspi.setFixedSize(devBtnSize, 32)
        self.dbtnRaspi.setToolTip("RaspiCounter Device - Turns green once a connection is made - click for info")
        self.dbtnRaspi.setStyleSheet(self.dbtnStyleSheetOFF)
        self.dbtnRaspi.setAutoFillBackground(True) # 'This is important!!'  Why???
        self.dbtnRaspi.clicked.connect(lambda: gdev_raspi.printRaspiDevInfo())

        self.connectTextSimul = 'Simul'
        self.dbtnSimul =  QPushButton(self.connectTextSimul)
        self.dbtnSimul.setFixedSize(devBtnSize, 32)
        self.dbtnSimul.setToolTip("SimulCounter Device - Turns green once a connection is made - click for info")
        self.dbtnSimul.setStyleSheet(self.dbtnStyleSheetOFF)
        self.dbtnSimul.setAutoFillBackground(True) # 'This is important!!'  Why???
        self.dbtnSimul.clicked.connect(lambda: gdev_simul.fprintSimulCounterInfo())

        self.connectTextMiniMon = 'MiniM'
        self.dbtnMiniMon = QPushButton(self.connectTextMiniMon)
        self.dbtnMiniMon.setFixedSize(devBtnSize, 32)
        self.dbtnMiniMon.setToolTip("MiniMon Device - Turns green once a connection is made - click for info")
        self.dbtnMiniMon.setStyleSheet(self.dbtnStyleSheetOFF)
        self.dbtnMiniMon.setAutoFillBackground(True) # 'This is important!!'  Why???
        self.dbtnMiniMon.clicked.connect(lambda: gdev_minimon.printMiniMonInfo())

    # toolbar Devices
        toolbar = self.addToolBar('Devices')
        toolbar.setToolTip("Devices Toolbar")
        toolbar.setIconSize(QSize(32,32))    # standard size is too small

        toolbar.addAction(self.toggleDeviceConnectionAction) # Connect icon
        toolbar.addWidget(QLabel("   "))                # spacer

        if gglobs.GMCActivation  :
            toolbar.addWidget(self.dbtnGMCPower)        # GMC power icon
            toolbar.addWidget(self.dbtnGMC)             # GMC device display

        if gglobs.AudioActivation  :
            toolbar.addWidget(self.dbtnAudio)           # AudioCounter device display

        if gglobs.RMActivation  :
            toolbar.addWidget(self.dbtnRM)              # RadMon device display

        if gglobs.AmbioActivation  :
            toolbar.addWidget(self.dbtnAmbio)           # AmbioMon device display

        if gglobs.GSActivation  :
            toolbar.addWidget(self.dbtnGS)              # Gamma-Scout device display

        if gglobs.LJActivation  :
            toolbar.addWidget(self.dbtnLJ)              # LabJack device display

        if gglobs.I2CActivation  :
            toolbar.addWidget(self.dbtnI2C)             # I2C device display

        if gglobs.RaspiActivation  :
            toolbar.addWidget(self.dbtnRaspi)           # Raspi device display

        if gglobs.MiniMonActivation  :
            toolbar.addWidget(self.dbtnMiniMon)         # MiniMon device display

        if gglobs.SimulActivation  :
            toolbar.addWidget(self.dbtnSimul)           # Simul device display


#Log Menu
        self.logLoadFileAction = QAction(QIcon(QPixmap(os.path.join(gglobs.gresPath, 'icon_log_get.png'))), 'Get Log or Create New One ...', self)
        self.logLoadFileAction.setShortcut('Ctrl+L')
        addMenuTip(self.logLoadFileAction, 'Load database for logging or create new one, and plot')
        self.logLoadFileAction.triggered.connect(lambda: self.getLogFile(source="Database"))

        self.logLoadCSVAction = QAction(QIcon(QPixmap(os.path.join(gglobs.gresPath, 'icon_log_get_CSV.png'))), 'Get Log from CSV File ...', self)
        addMenuTip(self.logLoadCSVAction, 'Load existing *.log or other CSV file, convert to database, and plot')
        self.logLoadCSVAction.triggered.connect(lambda: self.getLogFile(source="CSV File"))

        self.startloggingAction = QAction(QIcon(QPixmap(os.path.join(gglobs.gresPath, 'icon_log_start.png'))), 'Start Logging', self, enabled=False)
        addMenuTip(self.startloggingAction, 'Start logging from devices')
        self.startloggingAction.triggered.connect(self.startLogging)

        self.stoploggingAction = QAction(QIcon(QPixmap(os.path.join(gglobs.gresPath, 'icon_log_stop.png'))), 'Stop Logging', self, enabled=False)
        addMenuTip(self.stoploggingAction, 'Stop logging from devices')
        self.stoploggingAction.triggered.connect(self.stopLogging)

        self.addCommentAction = QAction(QIcon(QPixmap(os.path.join(gglobs.gresPath, ''))), 'Add Comment to Log ...', self, enabled=False)
        #self.addCommentAction.setShortcut('Ctrl+A')
        addMenuTip(self.addCommentAction, 'Add a comment to the current log')
        self.addCommentAction.triggered.connect(lambda: self.addComment("Log"))

        self.showLogDataAction = QAction('Show Log Data', self)
        addMenuTip(self.showLogDataAction, 'Show all records from current log')
        self.showLogDataAction.triggered.connect(lambda: self.showData("Log", full= True))

        self.showLogTagsAction = QAction('Show Log Data Tags/Comments', self)
        addMenuTip(self.showLogTagsAction, 'Show only records from current log containing tags or comments')
        self.showLogTagsAction.triggered.connect(self.showLogTags)

        self.showLogExcerptAction = QAction('Show Log Data Excerpt', self)
        addMenuTip(self.showLogExcerptAction, 'Show first and last few records of current log')
        self.showLogExcerptAction.triggered.connect(lambda: self.showData("Log", full=False))

        self.quickLogAction = QAction(QIcon(QPixmap(os.path.join(gglobs.gresPath, 'icon_quick_log.png'))), 'Quick Log', self, enabled=False)
        addMenuTip(self.quickLogAction, 'One-click log. Saves always into database default.logdb; will be overwritten on next Quick Log click')
        self.quickLogAction.triggered.connect(self.quickLog)

        self.logSnapAction = QAction(QIcon(QPixmap(os.path.join(gglobs.gresPath, 'icon_log_snap.png'))), 'Snap a new log record', self, enabled=False)
        addMenuTip(self.logSnapAction, 'Get a new log record immediately')
        self.logSnapAction.triggered.connect(gsup_tools.snapLogValue)

        self.setLogTimingAction = QAction(QIcon(QPixmap(os.path.join(gglobs.gresPath, 'icon_log_options.png'))), 'Set Log Cycle ...', self, enabled=True)
        addMenuTip(self.setLogTimingAction, 'Set Log Cycle in seconds')
        self.setLogTimingAction.triggered.connect(self.setLogCycle)

        self.logSaveCSVAction = QAction('Save Log Data into CSV file', self)
        addMenuTip(self.logSaveCSVAction, "Save all records from current log into a CSV file with extension 'csv'")
        self.logSaveCSVAction.triggered.connect(lambda: gsup_sql.saveData("Log", full= True))

        loggingMenu = self.menubar.addMenu('&Log')
        loggingMenu.setToolTipsVisible(True)
        loggingMenu.addAction(self.logLoadFileAction)
        loggingMenu.addAction(self.logLoadCSVAction)
        loggingMenu.addAction(self.addCommentAction)

        loggingMenu.addSeparator()
        loggingMenu.addAction(self.setLogTimingAction)
        loggingMenu.addAction(self.startloggingAction)
        loggingMenu.addAction(self.stoploggingAction)
        loggingMenu.addAction(self.quickLogAction)

        loggingMenu.addSeparator()
        loggingMenu.addAction(self.showLogDataAction)
        loggingMenu.addAction(self.showLogExcerptAction)
        loggingMenu.addAction(self.showLogTagsAction)

        loggingMenu.addSeparator()
        loggingMenu.addAction(self.logSaveCSVAction)
        #loggingMenu.triggered[QAction].connect(self.processtrigger)

        toolbar = self.addToolBar('Log')
        toolbar.setToolTip("Log Toolbar")
        toolbar.setIconSize(QSize(32,32))  # standard size is too small
        toolbar.addAction(self.logLoadFileAction)
        toolbar.addAction(self.logLoadCSVAction)
        toolbar.addAction(self.startloggingAction)
        toolbar.addAction(self.quickLogAction)
        toolbar.addAction(self.logSnapAction)
        toolbar.addAction(self.stoploggingAction)


#History Menu
        # load from DB
        self.loadHistDBAction = QAction(QIcon(QPixmap(os.path.join(gglobs.gresPath, 'icon_hist_DB_active.svg.png'))), 'Get History from Database ...', self)
        self.loadHistDBAction.setShortcut('Ctrl+H')
        addMenuTip(self.loadHistDBAction, 'Load history data from database and plot')
        self.loadHistDBAction.triggered.connect(lambda: self.getHistory("Database"))

        # load from CSV file
        self.loadHistHisAction = QAction(QIcon(QPixmap(os.path.join(gglobs.gresPath, 'icon_hist_CSV.svg.png'))), 'Get History from CSV File ...', self)
        addMenuTip(self.loadHistHisAction, 'Load existing *.his or other CSV file, convert to database file, and plot')
        self.loadHistHisAction.triggered.connect(lambda: self.getHistory("Parsed File"))

        # add comment
        self.addHistCommentAction = QAction(QIcon(QPixmap(os.path.join(gglobs.gresPath, ''))), 'Add Comment to History ...', self, enabled=False)
        addMenuTip(self.addHistCommentAction, 'Add a comment to the current history')
        self.addHistCommentAction.triggered.connect(lambda: self.addComment("His"))

        historyMenu = self.menubar.addMenu('&History')
        historyMenu.setToolTipsVisible(True)

        historyMenu.addAction(self.loadHistDBAction)
        historyMenu.addAction(self.loadHistHisAction)
        historyMenu.addAction(self.addHistCommentAction)

        historyMenu.addSeparator()


### begin device specific #########################

    # valid for GMC only
        if gglobs.GMCActivation:
            # get his from device
            self.histGMCDeviceAction = QAction(QIcon(QPixmap(os.path.join(gglobs.gresPath, 'icon_hist_device_active.png'))), 'Get History from Device ...', self, enabled=False)
            addMenuTip(self.histGMCDeviceAction, 'Load history data from any GMC device, create database, and plot')
            self.histGMCDeviceAction.triggered.connect(lambda: self.getHistory("Device"))

            # get his from bin file
            self.loadHistBinAction = QAction(QIcon(QPixmap(os.path.join(gglobs.gresPath, 'icon_hist_bin_active.png'))), 'Get History from GMC Binary File ...', self)
            addMenuTip(self.loadHistBinAction, 'Load history data from a GMC format binary file and plot')
            self.loadHistBinAction.triggered.connect(lambda: self.getHistory("Binary File"))

            # show bin data bytecount
            self.showHistBinDataDetailAction = QAction('Show History Binary Data Bytecount', self)
            addMenuTip(self.showHistBinDataDetailAction, 'Show counts of bytes in history binary data')
            self.showHistBinDataDetailAction.triggered.connect(lambda: gdev_gmc_hist.printHistDetails())

            # show bin data
            self.showHistBinDataAction = QAction('Show History Binary Data', self)
            addMenuTip(self.showHistBinDataAction, 'Show history binary data in human readable form')
            self.showHistBinDataAction.triggered.connect(lambda: self.showData("HisBin"))

            # show bin data excerpt
            self.showHistBinDataExcerptAction = QAction('Show History Binary Data Excerpt', self)
            addMenuTip(self.showHistBinDataExcerptAction, 'Show first and last few lines of history binary data in human readable form')
            self.showHistBinDataExcerptAction.triggered.connect(lambda: self.showData("HisBin", full=False))

            # show FF map
            self.historyFFAction = QAction("Show History Binary Data as FF Map", self)
            addMenuTip(self.historyFFAction, "Show History Binary Data as a map highlighting the locations of bytes with FF value")
            self.historyFFAction.triggered.connect(lambda: gsup_sql.createFFmapFromDB())

            # save bin data to bin file
            self.showHistBinDataSaveAction = QAction('Save History Binary Data to File', self)
            addMenuTip(self.showHistBinDataSaveAction, 'Save the history binary data as a *.bin file')
            self.showHistBinDataSaveAction.triggered.connect(lambda: gdev_gmc_hist.saveHistBinaryData())

            historySubMenuGMC = historyMenu.addMenu("GMC Series")
            historySubMenuGMC.setToolTipsVisible(True)

            historySubMenuGMC.addAction(self.histGMCDeviceAction)
            historySubMenuGMC.addAction(self.loadHistBinAction)

            historySubMenuGMC.addSeparator()
            historySubMenuGMC.addAction(self.showHistBinDataDetailAction) # bytecount
            historySubMenuGMC.addAction(self.showHistBinDataAction)
            historySubMenuGMC.addAction(self.showHistBinDataExcerptAction)
            historySubMenuGMC.addAction(self.historyFFAction)

            historySubMenuGMC.addSeparator()
            historySubMenuGMC.addAction(self.showHistBinDataSaveAction)
            #historyMenu.triggered[QAction].connect(self.processtrigger)


    # valid for Gamma-Scout only
        if gglobs.GSActivation:
            self.histGSDeviceAction = QAction(QIcon(QPixmap(os.path.join(gglobs.gresPath, 'icon_hist_device_active.png'))), 'Get History from Device ...', self, enabled=False)
            addMenuTip(self.histGSDeviceAction, 'Load history data from any Gamma-Scout device, create database, and plot')
            self.histGSDeviceAction.triggered.connect(lambda: self.getHistory("GSDevice"))

            self.histGSDatFileAction = QAction(QIcon(QPixmap(os.path.join(gglobs.gresPath, 'icon_hist_device_active.png'))), 'Get History from Gamma-Scout Dat File ...', self)
            addMenuTip(self.histGSDatFileAction, 'Load history data from a Gamma-Scout dat file, create database, and plot')
            self.histGSDatFileAction.triggered.connect(lambda: self.getHistory("GSDatFile"))

            self.showHistDatDataAction = QAction('Show History Dat Data', self)
            addMenuTip(self.showHistDatDataAction, 'Show the history data in Gamma-Scout like *.dat file')
            self.showHistDatDataAction.triggered.connect(lambda: gdev_scout.GSshowDatData())

            self.showHistDatDataSaveAction = QAction('Save History Data to Dat File', self)
            addMenuTip(self.showHistDatDataSaveAction, 'Save the history data as Gamma-Scout *.dat format')
            self.showHistDatDataSaveAction.triggered.connect(lambda: gdev_scout.GSsaveDatDataToDatFile())

            historySubMenuGS = historyMenu.addMenu("Gamma Scout Series")
            historySubMenuGS.setToolTipsVisible(True)

            historySubMenuGS.addAction(self.histGSDeviceAction)
            historySubMenuGS.addAction(self.histGSDatFileAction)

            historySubMenuGS.addSeparator()
            historySubMenuGS.addAction(self.showHistDatDataAction)

            historySubMenuGS.addSeparator()
            historySubMenuGS.addAction(self.showHistDatDataSaveAction)


    # valid for Ambiomon only
        if gglobs.AmbioActivation:
            self.histAMDeviceCAMAction = QAction(QIcon(QPixmap(os.path.join(gglobs.gresPath, 'icon_hist_device_active.png'))), 'Get History Binary CAM data from Device', self, enabled=False)
            addMenuTip(self.histAMDeviceCAMAction, 'Load Counter & Ambient history data from AmbioMon device, create database, and plot')
            self.histAMDeviceCAMAction.triggered.connect(lambda: self.getHistory("AMDeviceCAM"))

            self.histAMDeviceCPSAction = QAction(QIcon(QPixmap(os.path.join(gglobs.gresPath, 'icon_hist_device_active.png'))), 'Get History Binary CPS data from Device', self, enabled=False)
            addMenuTip(self.histAMDeviceCPSAction, 'Load Counts Per Second history data from AmbioMon device, create database, and plot')
            self.histAMDeviceCPSAction.triggered.connect(lambda: self.getHistory("AMDeviceCPS"))

            self.histAMCAMFileAction = QAction(QIcon(QPixmap(os.path.join(gglobs.gresPath, 'icon_hist_device_active.png'))), 'Get History Binary CAM data from File ...', self)
            addMenuTip(self.histAMCAMFileAction, 'Load history data from an AmbioMon CAM file, create database, and plot')
            self.histAMCAMFileAction.triggered.connect(lambda: self.getHistory("AMFileCAM"))

            self.histAMCPSFileAction = QAction(QIcon(QPixmap(os.path.join(gglobs.gresPath, 'icon_hist_device_active.png'))), 'Get History Binary CPS data from File ...', self)
            addMenuTip(self.histAMCPSFileAction, 'Load history data from an AmbioMon CPS file, create database, and plot')
            self.histAMCPSFileAction.triggered.connect(lambda: self.getHistory("AMFileCPS"))

            #~ self.showHistDatDataAction = QAction('Show History Raw Data', self)
            #~ addMenuTip(self.showHistDatDataAction, 'Show the history data in AmbioMon like *.dat file')
            #~ self.showHistDatDataAction.triggered.connect(gdev_ambiomon.AMshowDatData)

            #~ self.showHistDatDataSaveAction = QAction('Save History Raw Data to .csv File', self)
            #~ addMenuTip(self.showHistDatDataSaveAction, 'Save the history data as AmbioMon *.csv format')
            #~ self.showHistDatDataSaveAction.triggered.connect(gdev_ambiomon.AMsaveHistDatData)

            historySubMenuAM = historyMenu.addMenu("AmbioMon Series")
            historySubMenuAM.setToolTipsVisible(True)

            historySubMenuAM.addAction(self.histAMDeviceCAMAction)
            historySubMenuAM.addAction(self.histAMDeviceCPSAction)
            historySubMenuAM.addAction(self.histAMCAMFileAction)
            historySubMenuAM.addAction(self.histAMCPSFileAction)

            #~ historySubMenuAM.addSeparator()
            #~ historySubMenuAM.addAction(self.showHistDatDataAction)

            #~ historySubMenuAM.addSeparator()
            #~ historySubMenuAM.addAction(self.showHistDatDataSaveAction)


##### end device specific ##############


        # show his data
        self.showHistHisDataAction = QAction('Show History Data', self)
        addMenuTip(self.showHistHisDataAction, 'Show history data as parsed from binary data')
        self.showHistHisDataAction.triggered.connect(lambda: self.showData("His", full=True))

        # show his data excerpt
        self.showHistHisDataExcerptAction = QAction('Show History Data Excerpt', self)
        addMenuTip(self.showHistHisDataExcerptAction, 'Show first and last few records of history data parsed from binary data')
        self.showHistHisDataExcerptAction.triggered.connect(lambda: self.showData("His", full=False))

        # show tags/comments
        self.showHistHisTagsAction = QAction('Show History Data Tags/Comments', self)
        addMenuTip(self.showHistHisTagsAction, 'Show only records from history containing tags or comments')
        self.showHistHisTagsAction.triggered.connect(self.showHisTags)

        # show with parse
        self.showHistParseAction = QAction("Show History Data with Parse Comments", self)
        addMenuTip(self.showHistParseAction, "Show History Data including extended Parse Comments")
        self.showHistParseAction.triggered.connect(lambda: self.showData("HisParse", full=True))

        # show with parse excerpt
        self.showHistParseExcerttAction = QAction("Show History Data with Parse Comments Excerpt", self)
        addMenuTip(self.showHistParseExcerttAction, "Show first and last few records of history Data including extended Parse Comments")
        self.showHistParseExcerttAction.triggered.connect(lambda: self.showData("HisParse", full=False))

        # save his data to csv file
        self.histSaveCSVAction = QAction('Save History Data into CSV file', self)
        addMenuTip(self.histSaveCSVAction, "Save all records from current history into a CSV file with extension 'csv'")
        self.histSaveCSVAction.triggered.connect(lambda: gsup_sql.saveData("His", full=True))

        historyMenu.addSeparator()
        historyMenu.addAction(self.showHistHisDataAction)
        historyMenu.addAction(self.showHistHisDataExcerptAction)
        historyMenu.addAction(self.showHistHisTagsAction)
        historyMenu.addAction(self.showHistParseAction)
        historyMenu.addAction(self.showHistParseExcerttAction)

        historyMenu.addSeparator()
        historyMenu.addAction(self.histSaveCSVAction)

        toolbar     = self.addToolBar('History')
        toolbar.setToolTip("History Toolbar")
        toolbar.setIconSize(QSize(32,32))  # standard size is too small
        toolbar.addAction(self.loadHistDBAction)
        toolbar.addAction(self.loadHistHisAction)

# Web menu
        # menu entry and toolbar button for Map access
        self.WebAction = QAction(QIcon(QPixmap(os.path.join(gglobs.gresPath, 'icon_map.png'))), 'Update Radiation World Maps ...', self, enabled=False)
        addMenuTip(self.WebAction, 'Update Radiation World Maps using average of data shown in the plot')
        self.WebAction.triggered.connect(lambda: gsup_tools.pushToWeb())

        webMenu = self.menubar.addMenu('&Web')
        webMenu.setToolTipsVisible(True)
        webMenu.addAction(self.WebAction)

        toolbar = self.addToolBar('Web')
        toolbar.setToolTip("Web Toolbar")
        toolbar.setIconSize(QSize(32,32))  # standard size is too small
        toolbar.addAction(self.WebAction)

#Help Menu
        self.helpQickStartAction = QAction('Quickstart', self)
        addMenuTip(self.helpQickStartAction, 'Guidance for an easy start')
        self.helpQickStartAction.triggered.connect(self.helpQuickStart)

        self.helpManualUrlAction = QAction('GeigerLog Manual', self)
        addMenuTip(self.helpManualUrlAction, 'Open the GeigerLog Manual (locally if available, or online)')
        self.helpManualUrlAction.triggered.connect(openManual)

        self.helpFirmwareBugAction = QAction("Devices' Firmware Bugs", self)
        addMenuTip(self.helpFirmwareBugAction, 'Info on Firmware Bugs of the Devices and Workarounds')
        self.helpFirmwareBugAction.triggered.connect(self.helpFirmwareBugs)

        self.helpWorldMapsAction = QAction('Radiation World Maps', self)
        addMenuTip(self.helpWorldMapsAction, 'Contributing to the Radiation World Maps')
        self.helpWorldMapsAction.triggered.connect(self.helpWorldMaps)

        self.helpOccupationalRadiationAction = QAction('Occupational Radiation Limits', self)
        addMenuTip(self.helpOccupationalRadiationAction, 'Occupational Radiation Limits in USA and Germany')
        self.helpOccupationalRadiationAction.triggered.connect(self.helpOccupationalRadiation)

        self.DeviceSetUSBportAction = QAction('Show && Select USB Port and Baudrate ...', self)
        self.DeviceSetUSBportAction.setIcon(QIcon(QPixmap(os.path.join(gglobs.gresPath, 'icon_help_USB.svg.png'))))
        addMenuTip(self.DeviceSetUSBportAction, 'Show all available USB-to-Serial Ports and allow selection of port and baudrate for each device')
        self.DeviceSetUSBportAction.triggered.connect(self.helpSetPort)

        self.helpAboutAction = QAction('About GeigerLog', self)
        addMenuTip(self.helpAboutAction, 'About the GeigerLog program')
        self.helpAboutAction.triggered.connect(self.helpAbout)

        #self.helpAboutQTAction = QAction('About Qt', self)
        #addMenuTip(self.helpAboutQTAction, 'About the Qt toolkit used by GeigerLog')
        #self.helpAboutQTAction.triggered.connect(QApplication.aboutQt)

        helpMenu = self.menubar.addMenu('Hel&p')
        helpMenu.setToolTipsVisible(True)
        helpMenu.addAction(self.helpQickStartAction)
        helpMenu.addAction(self.helpManualUrlAction)
        helpMenu.addAction(self.helpFirmwareBugAction)
        helpMenu.addAction(self.helpWorldMapsAction)
        helpMenu.addAction(self.helpOccupationalRadiationAction)

        helpMenu.addSeparator()
        helpMenu.addAction(self.DeviceSetUSBportAction)

        self.GMCDevicePortDiscoveryAction = QAction('GMC', self)
        addMenuTip(self.GMCDevicePortDiscoveryAction, 'Find the USB Port connected to a GMC Geiger counter and the Baudrate automatically')
        self.GMCDevicePortDiscoveryAction.triggered.connect(lambda: autoDiscoverUSBPort("GMC"))

        self.I2CDevicePortDiscoveryAction = QAction('I2C', self)
        addMenuTip(self.I2CDevicePortDiscoveryAction, 'Find the USB Port connected to an  I2C device and the Baudrate automatically')
        self.I2CDevicePortDiscoveryAction.triggered.connect(lambda: autoDiscoverUSBPort("I2C"))

        self.GSDevicePortDiscoveryAction = QAction('GS', self)
        addMenuTip(self.GSDevicePortDiscoveryAction, 'Find the USB Port connected to a Gamma-Scout Geiger counter and the Baudrate automatically')
        self.GSDevicePortDiscoveryAction.triggered.connect(lambda: autoDiscoverUSBPort("GS"))

        if not gglobs.GMCActivation: self.GMCDevicePortDiscoveryAction.setEnabled(False)
        if not gglobs.I2CActivation: self.I2CDevicePortDiscoveryAction.setEnabled(False)
        if not gglobs.GSActivation:  self.GSDevicePortDiscoveryAction. setEnabled(False)

        helpSubMenu = helpMenu.addMenu("Autodiscover USB Port for Device")
        helpSubMenu.setToolTipsVisible(True)
        helpSubMenu.addAction(self.GMCDevicePortDiscoveryAction)
        helpSubMenu.addAction(self.I2CDevicePortDiscoveryAction)
        helpSubMenu.addAction(self.GSDevicePortDiscoveryAction)

        helpMenu.addSeparator()
        #helpMenu.addAction(self.helpAboutQTAction)
        helpMenu.addAction(self.helpAboutAction)
        #helpMenu.triggered[QAction].connect(self.processtrigger)

        toolbar = self.addToolBar('Help')
        toolbar.setToolTip("Help Toolbar")
        toolbar.setIconSize(QSize(32,32))  # standard size is too small
        toolbar.addAction(self.DeviceSetUSBportAction)


# Devel Menu
        if gglobs.devel:
            showOptionsAction = QAction('Show Command Line Options', self)
            addMenuTip(showOptionsAction, 'Show command line options')
            showOptionsAction.triggered.connect(self.helpOptions)

            changeOptionsAction = QAction('Change Command Line Options', self)
            addMenuTip(changeOptionsAction, 'Allows to change some command line options during running')
            changeOptionsAction.triggered.connect(self.changeOptions)

            showSystemInfoAction = QAction('Show System Info', self)
            addMenuTip(showSystemInfoAction, 'Show Details on the Current Program Settings and Environment')
            showSystemInfoAction.triggered.connect(showSystemInfo)

            develIotaAction = QAction("Print Vars Status", self)
            develIotaAction.triggered.connect(lambda: printVarsStatus())

            develAlphaAction = QAction("Convolution FFT", self)
            develAlphaAction.triggered.connect(lambda: gstat_convfft.convFFT())

            develBetaAction = QAction("Create Synthetic Data", self)
            develBetaAction.triggered.connect(lambda: gstat_synth.createSyntheticData())

            develGammaAction = QAction("GMC Configuration", self)
            if gglobs.GMCActivation:
                develGammaAction.triggered.connect(lambda: gdev_gmc.editGMC_Configuration())

            develBingAction = QAction("Bip", self)
            develBingAction.triggered.connect(lambda: playWav(wtype = "ok"))

            develBurpAction = QAction("Burp", self)
            develBurpAction.triggered.connect(lambda: playWav(wtype = "burp"))

            develClickAction = QAction("Click", self)
            develClickAction.triggered.connect(lambda: playClick())

            develCounterAction = QAction("Counter", self)
            develCounterAction.triggered.connect(lambda: playCounter())

            develSineAction = QAction("Sine", self)
            develSineAction.triggered.connect(lambda: playSine())

            SaveRepairLogAction = QAction('Repair DateTime and Save Data into *.log file (CSV)', self)
            addMenuTip(SaveRepairLogAction, "Repair all records from current log and save into a CSV file with extension 'log'")
            SaveRepairLogAction.triggered.connect(lambda: gsup_sql.saveRepairData("Log", full= True))

            SaveRepairHisAction = QAction('Repair DateTime and Save Data into *.his file (CSV)', self)
            addMenuTip(SaveRepairHisAction, "Repair all records from current log and save into a CSV file with extension 'his'")
            SaveRepairHisAction.triggered.connect(lambda: gsup_sql.saveRepairData("His", full= True))

            develAudioAction = QAction("Show Audio Signal", self)
            develAudioAction.triggered.connect(lambda: gdev_audio.showLiveAudioSignal())


            develMenu = self.menubar.addMenu('D&evel')
            develMenu.setToolTipsVisible(True)

            develMenu.addAction(showOptionsAction)
            develMenu.addAction(changeOptionsAction)
            develMenu.addAction(showSystemInfoAction)

            develMenu.addSeparator()
            develMenu.addAction(develIotaAction)
            develMenu.addAction(develAlphaAction)
            develMenu.addAction(develBetaAction)
            develMenu.addAction(develGammaAction)
            develMenu.addAction(develBingAction)
            develMenu.addAction(develBurpAction)
            develMenu.addAction(develSineAction)
            develMenu.addAction(develClickAction)
            develMenu.addAction(develCounterAction)
            develMenu.addAction(SaveRepairLogAction)
            develMenu.addAction(SaveRepairHisAction)
            develMenu.addAction(develAudioAction)


# add navigation toolbar as last toolbar
        self.addToolBar(self.navtoolbar)

# DataOptions
        BigButtonWidth = 105

    # labels and entry fields
        dltitle  = QLabel("Data")
        #dltitle.setFont(QFont("system", weight=QFont.Bold))
        dltitle.setFont(self.fatfont)

        dlcf     = QLabel("Database Files")
        dlcf.setAlignment(Qt.AlignCenter)

        dlcy     = QLabel("Misc")
        dlcy.setAlignment(Qt.AlignCenter)
        dlcy.setFixedWidth(BigButtonWidth)

        dlnotepad   = QLabel("NotePad")
        dlnotepad.setAlignment(Qt.AlignCenter)
        dlnotepad.setFixedWidth(BigButtonWidth)

        dllog=QLabel("Log:")

        self.dcfLog=QLineEdit()
        self.dcfLog.setReadOnly(True)
        self.dcfLog.setStyleSheet("QLineEdit { background-color: #DFDEDD; color: rgb(80,80,80); }")
        self.dcfLog.setToolTip('The full path of the Log-File if any is loaded')

        self.dcycl  = QPushButton()
        self.dcycl.setToolTip('Current setting of log cycle in seconds')
        self.dcycl.clicked.connect(self.setLogCycle)
        self.dcycl.setFixedWidth(BigButtonWidth)
        self.dcycl.setStyleSheet("QPushButton {}")

        dlhist=QLabel("History:")
        self.dcfHis=QLineEdit()
        self.dcfHis.setReadOnly(True)
        self.dcfHis.setStyleSheet("QLineEdit { background-color : #DFDEDD; color : rgb(80,80,80); }")
        self.dcfHis.setToolTip('The full path of the History-File if any is loaded')

        dbtnPlotLog =  QPushButton('Plot')
        dbtnPlotLog.clicked.connect(lambda: self.plotGraph('Log'))
        dbtnPlotLog.setMaximumWidth(36)
        dbtnPlotLog.setToolTip("Plot the Log File")

        dbtnPlotHis =  QPushButton('Plot')
        dbtnPlotHis.clicked.connect(lambda: self.plotGraph('His'))
        dbtnPlotHis.setMaximumWidth(36)
        dbtnPlotHis.setToolTip("Plot the History File")

    # button: clear notepad
        clearbutton    =  QPushButton('Clear')
        clearbutton.clicked.connect(self.clearNotePad)
        clearbutton.setToolTip('Delete all content of the NotePad')
        clearbutton.setFixedWidth(BigButtonWidth)

    # button: print data excerpt to notepad
        self.printbutton    =  QPushButton('DataExcerpt')
        self.printbutton.clicked.connect(lambda: self.showData(full=False))
        self.printbutton.setToolTip('Print Log or His Data to the NotePad')
        self.printbutton.setFixedWidth(BigButtonWidth)

    # button: add comment
        self.btnAddComment =  QPushButton('Add Comment')
        self.btnAddComment.clicked.connect(lambda: self.addComment("Current"))
        self.btnAddComment.setFixedWidth(BigButtonWidth)
        self.btnAddComment.setEnabled(True)
        self.btnAddComment.setToolTip('Add comment to current database file')

    # separator lines - vertical
        vlinedB0 = QFrame()
        vlinedB0.setFrameShape(QFrame.VLine)

    # layout the Data Options
        dataOptions=QGridLayout()
        #dataOptions.setContentsMargins(*self.ContentsMargins)

        row = 0
        dataOptions.addWidget(dltitle,                 row, 0)
        # 1 is empty
        dataOptions.addWidget(dlcf,                    row, 2)
        dataOptions.addWidget(dlcy,                    row, 3)
        dataOptions.addWidget(vlinedB0,                row, 4, 4, 1)
        dataOptions.addWidget(dlnotepad,               row, 5)

        row = 1
        dataOptions.addWidget(dllog,                   row, 0)
        dataOptions.addWidget(dbtnPlotLog,             row, 1)
        dataOptions.addWidget(self.dcfLog,             row, 2)
        dataOptions.addWidget(self.dcycl,              row, 3)
        # 4 is empty (vline)
        dataOptions.addWidget(self.printbutton,        row, 5)

        row = 2
        dataOptions.addWidget(dlhist,                  row, 0)
        dataOptions.addWidget(dbtnPlotHis,             row, 1)
        dataOptions.addWidget(self.dcfHis,             row, 2)
        dataOptions.addWidget(self.btnAddComment,      row, 3)
        # 4 is empty (vline)
        dataOptions.addWidget(clearbutton,             row, 5)

        # group Data Options into Groupbox
        dataOptionsGroup = QGroupBox()
        dataOptionsGroup.setContentsMargins(0,0,0,0)
        dataOptionsGroup.setStyleSheet("QGroupBox {border-style:solid; border-width:1px; border-color:silver;}")
        dataOptionsGroup.setLayout(dataOptions)
        dataOptionsGroup.setMaximumHeight(200)  # not relevant as notepad gives stretch


# GraphOptions
        ewidth = 75

        ltitle  = QLabel("Graph")
        #~ltitle.setFont(QFont("system", weight=QFont.Bold))
        ltitle.setFont(self.fatfont)

        lmin    = QLabel("Min")
        lmin.setAlignment(Qt.AlignCenter)

        lmax    = QLabel("Max")
        lmax.setAlignment(Qt.AlignCenter)

        btnSetScaling =  QPushButton('Scaling')
        btnSetScaling.clicked.connect(self.editScaling)
        btnSetScaling.setFixedWidth(ewidth)
        btnSetScaling.setToolTip("View and edit scaling of the variables")

        lcounts = QLabel("Counter")
        ly2     = QLabel("Ambient")
        ltime   = QLabel("Time")

        self.ymin = QLineEdit()
        self.ymin.setToolTip('Minimum setting for Counter axis')

        self.ymax = QLineEdit()
        self.ymax.setToolTip('Maximum setting for Counter axis')

        self.yunit = QComboBox()
        self.yunit.addItems(["CPM", "µSv/h"])
        self.yunit.setMaximumWidth(ewidth)
        self.yunit.setToolTip('Select the Count Unit for the plot')
        self.yunit.currentIndexChanged.connect(self.changedGraphCountUnit)

        self.y2min=QLineEdit()
        self.y2min.setToolTip('Minimum setting for Ambient axis')

        self.y2max=QLineEdit()
        self.y2max.setToolTip('Maximum setting for Ambient axis')

        self.y2unit = QComboBox()
        self.y2unit.addItems(["°C", "°F"])
        self.y2unit.setMaximumWidth(ewidth)
        self.y2unit.setToolTip('Select the Temperature Unit')
        self.y2unit.currentIndexChanged.connect(self.changedGraphTemperatureUnit)

        self.xmin=QLineEdit()
        self.xmin.setToolTip('The minimum (left) limit of the time to be shown. Enter manuallly or by left-mouse-click on the graph')

        self.xmax=QLineEdit()
        self.xmax.setToolTip('The maximum (right) limit of the time to be shown. Enter manuallly or by right-mouse-click on the graph')

        self.xunit = QComboBox()
        self.xunit.addItems(["Time", "auto", "second", "minute", "hour", "day", "week", "month"])
        self.xunit.setMaximumWidth(ewidth)
        self.xunit.currentIndexChanged.connect(self.changedGraphTimeUnit)
        self.xunit.setToolTip('The time axis to be shown as Time-of-Day (Time) or time since first record in seconds, minutes, hours, days, weeks, months;\nauto selects most appropriate period')

        # The drop-down selector for selected variable
        self.select = QComboBox()
        self.select.setToolTip('The data to be selected for analysis')
        self.select.setEnabled(False)
        self.select.currentIndexChanged.connect(self.changedGraphSelectedVariable)
        self.select.setMaxVisibleItems(12)
        for vname in gglobs.varsDefault:
            self.select.addItems([gglobs.varsBook[vname][0]])

        # The checkboxes to select the displayed variables
        self.varDisplayCheckbox = {}
        for vname in gglobs.varsDefault:
            vshort = gglobs.varsBook[vname][1]
            vlong  = gglobs.varsBook[vname][0]

            self.varDisplayCheckbox[vname] = QCheckBox    (vshort)
            self.varDisplayCheckbox[vname].setToolTip     (vlong)
            self.varDisplayCheckbox[vname].setChecked     (False)
            self.varDisplayCheckbox[vname].setEnabled     (False)
            self.varDisplayCheckbox[vname].setTristate    (False)

            # "double lambda needed for closure" WTF???
            self.varDisplayCheckbox[vname].stateChanged.connect((lambda x: lambda: self.changedGraphDisplayCheckboxes(x))(vname))

        chk_width = 20
        btn_width = 50

        self.avgbox = QCheckBox("Avg")
        self.avgbox.setLayoutDirection(Qt.RightToLeft)
        self.avgbox.setChecked(gglobs.avgChecked)
        self.avgbox.setTristate (False)
        self.avgbox.setToolTip("If checked, Average and ±95% lines will be shown")
        self.avgbox.stateChanged.connect(self.changedGraphOptionsAvg)

        self.mavbox = QCheckBox("MvAvg")
        self.mavbox.setLayoutDirection(Qt.RightToLeft)
        self.mavbox.setChecked(gglobs.mavChecked)
        self.mavbox.setTristate (False)
        self.mavbox.setToolTip('If checked a Moving Average line will be drawn')
        self.mavbox.stateChanged.connect(self.changedGraphOptionsMav)

        self.mav=QLineEdit()
        self.mav.setMinimumWidth(btn_width)
        self.mav.setMaximumWidth(btn_width)
        self.mav.setToolTip('Enter the Moving Average smoothing period in seconds')
        self.mav.setText("{:0.0f}".format(gglobs.mav_initial))
        self.mav.textChanged.connect(self.changedGraphOptionsMavText)

        btnPoisson =  QPushButton('Poiss')
        btnPoisson.clicked.connect(lambda: gstat_poisson.plotPoisson())
        btnPoisson.setFixedWidth(btn_width)
        btnPoisson.setToolTip("Shows a plot of a Poisson curve on a histogram of the data in the current plot")

        btnFFT =  QPushButton('FFT')
        btnFFT.clicked.connect(lambda: gstat_fft.plotFFT())
        btnFFT.setFixedWidth(btn_width)
        btnFFT.setToolTip("Show a plot of FFT spectra & Autocorrelation of the data in the current plot")

        btnPlotStats =  QPushButton('Stats')
        btnPlotStats.clicked.connect(lambda: gsup_tools.printStats())
        btnPlotStats.setFixedWidth(btn_width)
        btnPlotStats.setToolTip("Shows the Statistics of the data in the current plot")

        btnQuickStats =  QPushButton('SuSt')
        btnQuickStats.clicked.connect(lambda: gsup_tools.printSuSt())
        btnQuickStats.setFixedWidth(btn_width)
        btnQuickStats.setToolTip("Shows Summary Statistics of all variables and data in the plot")

        btnReset  = QPushButton('Reset')
        btnReset.clicked.connect(self.reset_replotGraph)
        btnReset.setFixedWidth(btn_width)
        btnReset.setToolTip("Reset all Graph Options to Default conditions")

        btnClear  = QPushButton('Clear')
        btnClear.clicked.connect(self.clearGraphLimits)
        btnClear.setFixedWidth(btn_width)
        btnClear.setToolTip("Clear the Graph Limit Options to Default conditions")

        btnApplyGraph = QPushButton('Apply')
        btnApplyGraph.clicked.connect(self.applyGraphOptions)
        btnApplyGraph.setStyleSheet("background-color: lightblue")
        btnApplyGraph.setFixedWidth(btn_width)
        btnApplyGraph.setMinimumHeight(65)
        btnApplyGraph.setToolTip("Apply the Graph Options and replot")
        btnApplyGraph.setDefault(True)

        self.labelVar = QLabel("---")
        self.labelVar.setToolTip("Shows the variable value in additional units when logging")
        self.labelVar.setMinimumWidth(130)
        self.labelVar.setFont(QFont('sans', 13, QFont.Bold))
        self.labelVar.setStyleSheet('color:darkgray;')
        self.labelVar.setAlignment(Qt.AlignCenter)
        self.labelVar.mousePressEvent=gsup_tools.displayLastValues

    # separator lines
        vlineA0 = QFrame()
        vlineA0.setFrameShape(QFrame.VLine)

        hlineB3 = QFrame()
        hlineB3.setFrameShape(QFrame.HLine)

    # OFF / ON button
        btn_width = 35
        btnOFF = QPushButton('OFF')
        btnOFF .setToolTip("Uncheck all variables")
        btnOFF .clicked.connect(lambda: self.plotVarsOffOn("OFF"))
        btnOFF .setMaximumWidth(btn_width)

        btnON  = QPushButton('ON')
        btnON  .setToolTip("Check all avialable variables")
        btnON  .clicked.connect(lambda: self.plotVarsOffOn("ON"))
        btnON  .setMaximumWidth(btn_width)

    # layout of variables check boxes with OFF / ON button
        layoutH = QHBoxLayout()
        layoutH.addWidget(btnOFF)
        layoutH.addWidget(btnON)
        for vname in gglobs.varsBook:
            layoutH.addWidget(self.varDisplayCheckbox[vname])

    # color select button
        self.btnColorText = "Color of selected variable; click to change it. Current color:  "
        self.btnColor     = ClickLabel('Color')
        self.btnColor       .setAlignment(Qt.AlignCenter)
        self.btnColor       .setMaximumWidth(50)
        self.btnColor       .setStyleSheet("QLabel { border: 1px solid silver;  border-radius: 3px; }")
        addMenuTip(self.btnColor, self.btnColorText + "None")

    #layout the GraphOptions
        graphOptions=QGridLayout()
        graphOptions.setContentsMargins(5,5,5,5) #spacing around the graph options

        # stepping order
        # to define the order of stepping through by tab-key
        # row 1 .. 3, col 1+2 is put in front
        row = 1
        graphOptions.addWidget(self.ymin,       row, 1)
        graphOptions.addWidget(self.ymax,       row, 2)
        row = 2
        graphOptions.addWidget(self.y2min,      row, 1)
        graphOptions.addWidget(self.y2max,      row, 2)
        row = 3
        graphOptions.addWidget(self.xmin,       row, 1)
        graphOptions.addWidget(self.xmax,       row, 2)

        row = 0
        graphOptions.addWidget(ltitle,          row, 0)
        graphOptions.addWidget(lmin,            row, 1)
        graphOptions.addWidget(lmax,            row, 2)
        graphOptions.addWidget(btnReset,        row, 3)
        graphOptions.addWidget(btnSetScaling,   row, 4)
        graphOptions.addWidget(vlineA0,         row, 5, 4, 1)
        graphOptions.addWidget(self.select,     row, 6, 1, 2)
        graphOptions.addWidget(btnQuickStats,   row, 8)

        row = 1
        graphOptions.addWidget(lcounts,         row, 0)
        # see stepping order
        # see stepping order
        graphOptions.addWidget(btnClear,        row, 3)
        graphOptions.addWidget(self.yunit,      row, 4)
        # col 5 is empty (vert line)
        graphOptions.addWidget(self.mavbox,     row, 6)
        graphOptions.addWidget(self.mav,        row, 7)
        graphOptions.addWidget(btnPlotStats,    row, 8)

        row = 2
        graphOptions.addWidget(ly2,             row, 0)
        # see stepping order
        # see stepping order
        graphOptions.addWidget(btnApplyGraph,   row, 3, 2, 1)
        graphOptions.addWidget(self.y2unit,     row, 4)
        # col 5 is empty (vert line)
        graphOptions.addWidget(self.avgbox,     row, 6)
        graphOptions.addWidget(self.btnColor,   row, 7)
        graphOptions.addWidget(btnPoisson,      row, 8)

        row = 3
        graphOptions.addWidget(ltime,           row, 0)
        # see stepping order
        # see stepping order
        graphOptions.addWidget(self.xunit,      row, 4)
        # col 5 is empty (vert line)
        graphOptions.addWidget(self.labelVar,   row, 6, 1, 2)
        graphOptions.addWidget(btnFFT,          row, 8)

        row = 4
        graphOptions.addWidget(hlineB3,         row, 0, 1, 9)

        row = 5
        graphOptions.addLayout(layoutH,         row, 0, 1, 9)

    # group Graph Options into Groupbox
        graphOptionsGroup = QGroupBox()
        graphOptionsGroup.setContentsMargins(0,0,0,0)
        graphOptionsGroup.setMaximumHeight(200)   # relevant because no stretch from graphic!
        graphOptionsGroup.setStyleSheet("QGroupBox {border-style: solid; border-width: 1px; border-color: silver;}")
        graphOptionsGroup.setLayout(graphOptions)

# NotePad
        self.notePad = QTextEdit()
        self.notePad.setReadOnly(True)
        self.notePad.setFont(self.fontstd)
        self.notePad.setLineWrapMode(QTextEdit.NoWrap)
        self.notePad.setTextColor(QColor(40, 40, 40))
        #self.notePad.setStyleSheet("background-color:lightgreen;")

        gglobs.notePad = self.notePad # used for fprint in utils

# LogPad
        self.logPad = QTextEdit()
        self.logPad.setReadOnly(True)
        self.logPad.setFont(self.fontstd)
        self.logPad.setLineWrapMode(QTextEdit.NoWrap)
        self.logPad.setTextColor(QColor(40, 40, 40))
        #self.logPad.setStyleSheet("background-color:lightgreen;")

        gglobs.logPad = self.logPad # used for logPrint in utils

# set the layout - left side
        splitterPad = QSplitter(Qt.Vertical)
        splitterPad.addWidget(self.notePad)
        splitterPad.addWidget(self.logPad)
        splitterPad.setSizes([800, 300])

        layoutLeft = QVBoxLayout()
        layoutLeft.addWidget(dataOptionsGroup)
        layoutLeft.addWidget(splitterPad)
        layoutLeft.setContentsMargins(0,0,0,0)
        layoutLeft.setSpacing(0)

# set the layout - right side
        myLayout =  QVBoxLayout()     # to show canvas with frame
        myLayout.setContentsMargins(0,0,0,0) # left, top, right, bottom
        myLayout.setSpacing(0)
        myLayout.addWidget(self.canvas)

        myGroup = QGroupBox()
        myGroup.setLayout(myLayout)
        myGroup.setContentsMargins(0,0,0,0)
        myGroup.setStyleSheet("background-color:#DFDEDD;") # same color as canvas

        layoutRight = QVBoxLayout()
        layoutRight.addWidget(graphOptionsGroup)
        layoutRight.addWidget(self.canvas)      # add canvas directly, no frame
        layoutRight.setContentsMargins(0,0,0,0)
        layoutRight.setSpacing(0)

# set the layout - both
        leftWidget = QWidget()
        leftWidget.setLayout(layoutLeft)

        rightWidget = QWidget()
        rightWidget.setLayout(layoutRight)

        splitterBoth = QSplitter(Qt.Horizontal)
        splitterBoth.addWidget(leftWidget)
        splitterBoth.addWidget(rightWidget)
        splitterBoth.setSizes([800, 750])
        splitterBoth.setContentsMargins(5,0,5,0)

# centralwidget
        self.setCentralWidget(splitterBoth)

#timer for logging
        self.timer = QTimer()
        self.timer.timeout.connect(gsup_tools.getLogValues)

#show
        self.dcfLog.setText(str(gglobs.logFilePath))     # default is None
        self.dcfHis.setText(str(gglobs.hisFilePath))
        self.showTimingSetting (gglobs.logcycle)

        self.show()
        if gglobs.window_size == "maximized":   self.showMaximized()

        dprint("Fonts:  App     -",     strFontInfo("", gglobs.app.font()))  # print font info for QApplication
        dprint("Fonts:  menubar -",     strFontInfo("", self.menubar.fontInfo()))
        dprint("Fonts:  logPad  -",     strFontInfo("", self.logPad.fontInfo()))
        dprint("Fonts:  notePad -",     strFontInfo("", self.notePad.fontInfo()))
        dprint("Screen: Dimensions: ",  QDesktopWidget().screenGeometry()) # gives screen dimensions
        dprint("Screen: Available:  ",  screen_available)                        # gives screen dimensions available

        # Note on Window sizes:
        # "On X11, a window does not have a frame until the window manager decorates it."
        # see: http://doc.qt.io/qt-4.8/application-windows.html#window-geometry
        # self.geometry(),      : gives Windows dimensions but has the frame EXCLUDED!
        # self.frameGeometry()  : gives Windows dimensions including frame, but not on X11!
        dprint("Window: Dimensions: ",  self.geometry(),      " w/o Frame")
        dprint("Window: Dimensions: ",  self.frameGeometry(), " WITH Frame (not valid on X11)")

        # copyright message
        message = __copyright__ + ", by " + __author__ + ", License: " + __license__
        self.showStatusMessage(message, timing=0, error=False) # message remains until overwritten by next

        Qt_update()

        wprint("Data  Options group: height: {}, width: {}".format(dataOptionsGroup.height(), dataOptionsGroup.width()))
        wprint("Graph Options group: height: {}, width: {}".format(graphOptionsGroup.height(), graphOptionsGroup.width()))

        dprint(TGREEN + "Starting the GUI complete " + "-" * 100 + TDEFAULT + "\n")

        if gglobs.startupProblems > "":
            self.startupProblems(gglobs.startupProblems, closeGL = True)  # EXIT on Failure!

        if gglobs.python_failure  > "":
            self.startupProblems(gglobs.python_failure,  closeGL = True)  # EXIT on wrong Python version!

        if gglobs.configAlerts > "":
            msg  = "<b>Configuration File has Problems, please review:<br>"
            msg += "(without correction, defaults will be used)</b><br><br>"
            msg += gglobs.configAlerts
            self.startupProblems(msg,  closeGL = False)
            gglobs.configAlerts = ""

        if     gglobs.GMCActivation     or \
               gglobs.AudioActivation   or \
               gglobs.RMActivation      or \
               gglobs.AmbioActivation   or \
               gglobs.GSActivation      or \
               gglobs.I2CActivation     or \
               gglobs.LJActivation      or \
               gglobs.SimulActivation   or \
               gglobs.MiniMonActivation :

            isAnyDeviceActive = True
        else:
            isAnyDeviceActive = False
            self.fprintWarningMessage("WARNING: You have not activated any device!")
            # ~ efprint("WARNING: You have not activated any device!")
            # ~ fprint("<br>Neither Logging nor History downloads from device are possible, but")
            # ~ fprint("you can work on Log and History data loaded from file.")
            # ~ fprint("\nDevices are activated in the configuration file 'geigerlog.cfg'.")

        # Devel - start GeigerLog with command 'devel' e.g.: 'geigerlog -dv devel'
        # on devel  : make some extra commands available in devel menu
        # on devel1 : do devel and load database 'default.logdb' if available
        # on devel2 : do devel1 and make connections
        # on devel3 : do devel2 and start quicklog
        if gglobs.devel1:
            defaultFile = os.path.join(gglobs.dataPath, "default.logdb")
            if os.access(defaultFile , os.R_OK):
                self.getLogFile(defaultLogDBPath = defaultFile)
            else:
                dprint("Testfile '{}' not found".format(defaultFile), debug=True)

        if gglobs.devel2:
            self.switchConnections(new_connection = "ON")

        if gglobs.devel3:
            self.quickLog()

        playWav("ok")


#========== END __init__ ------------------#########################***********
#
#========== BEGIN Class Functions =============================================

    def fprintWarningMessage(self, message):
        efprint(header("WARNING: You have not activated any device!"))
        fprint("<br>Neither Logging nor History downloads from device are possible, but")
        fprint("you can work on Log and History data loaded from file.")
        fprint("\nDevices are activated in the configuration file 'geigerlog.cfg'.")

    def startupProblems(self, message, closeGL = True):
        """alert on problems like wrong Python version, configuration file
        missing, configuration file incorrect"""

        playWav("error")

        msg = QMessageBox()
        msg.setWindowIcon(self.iconGeigerLog)
        msg.setWindowTitle("STARTUP PROBLEM")
        msg.setText("<!doctype html>" + message)
        msg.setStandardButtons(QMessageBox.Ok)
        msg.setDefaultButton(QMessageBox.Ok)
        msg.setEscapeButton(QMessageBox.Ok)
        msg.setWindowModality(Qt.WindowModal)
        msg.exec()

        if closeGL:
            self.close() # End GeigerLog; may not result in exit, needs sys.exit()
            sys.exit(1)


    def searchNotePad(self):
        """Save Content of NotePad to file"""

        fncname = "searchNotePad: "

        qid = QInputDialog()
        stxt, ok = qid.getText(None, 'Search NotePad', 'Search Text:' + ' '*35, text=gglobs.notePadSearchText)
        if not ok: return

        gglobs.notePadSearchText = stxt
        #rint(fncname + "stxt = '{}'".format(stxt), type(stxt))

        flag = QTextDocument.FindBackward            # flag to search backwards
        found = self.notePad.find(stxt, flag)
        if found:  return
        else: # not found
            # set cursor to end and try again
            self.notePad.moveCursor(QTextCursor.End)
            found = self.notePad.find(stxt, flag)
            if found: return

        self.showStatusMessage("Search NotePad Content: Text '{}' not found".format(stxt))


    def saveNotePad(self):
        """Save Content of NotePad to file"""

        if gglobs.currentDBPath is None:
            self.showStatusMessage("No data available")
            return

        newFile = gglobs.currentDBPath + '.notes'
        fprint(header("Saving NotePad Content"))
        fprint("to File: {}\n".format(newFile))

        nptxt = self.notePad.toPlainText()  # Saving as Plain Text; all is b&W, no colors
        #nptxt = self.notePad.toHtml()      # Saving in HTML Format; preserves color
        #print("nptxt:", nptxt)

        with open(newFile, 'a') as f:
            f.write(nptxt)


#exit GeigerLog
    def closeEvent(self, event):
        """is called via self.close! Allow to Exit unless Logging is active"""

        fncname = "closeEvent: "
        # event: QEvent.Close = 19 : Widget was closed
        dprint("closeEvent: event type: {}".format(event.type()))
        setDebugIndent(1)

        if gglobs.logging :
            event.ignore()
            self.showStatusMessage("Cannot exit when logging! Stop logging first")
            dprint(fncname + "ignored; Cannot exit when logging! Stop logging first")

        else:
            event.accept()                           # allow closing the window
            dprint(fncname + "accepted")

            # terminate the devices
            if gglobs.GMCConnection     : gdev_gmc      .terminateGMC()
            if gglobs.AudioConnection   : gdev_audio    .terminateAudioCounter()
            if gglobs.RMConnection      : gdev_radmon   .terminateRadMon()
            if gglobs.AmbioConnection   : gdev_ambiomon .terminateAmbioMon()
            if gglobs.GSConnection      : gdev_scout   .terminateGammaScout()
            if gglobs.I2CConnection     : gdev_i2c      .terminateI2C()
            if gglobs.LJConnection      : gdev_labjack  .terminateLabJack()
            if gglobs.RaspiConnection   : gdev_raspi    .terminateRaspi()
            if gglobs.SimulConnection   : gdev_simul    .terminateSimulCounter()
            if gglobs.MiniMonConnection : gdev_minimon  .terminateMiniMon()

            # close the databases for Log and His
            gsup_sql.DB_closeDatabase("Log")
            gsup_sql.DB_closeDatabase("His")

            dprint(fncname + "exiting now")

            # The standard way to exit is sys.exit(n)
            # os._exit calls the C function _exit() which does an immediate program
            # termination. Note the statement "can never return".
            # sys.exit() is identical to raise SystemExit(). It raises a Python
            # exception which may be caught by the caller.
            sys.exit(0) # otherwise sub windows won't close

        setDebugIndent(0)


#GraphOptions

    def changedGraphSelectedVariable(self):
        """called from the select combo for variables"""

        self.applyGraphOptions()


    def changedGraphDisplayCheckboxes(self, value):
        """Graph varDisplayCheckbox Value has changed"""

        if not gglobs.allowGraphUpdate: return

        oldIndex = self.select.currentIndex()

        text    = gglobs.varsBook[value][0]
        index   = self.select.findText(text)
        #print("changedGraphDisplayCheckboxes: var:{}, longname:{}, index:{}".format(value, text, index))

        if self.varDisplayCheckbox[value].isChecked():
            # sets and enables the select combobox to the checked variable
            # thus making it to the selected variable
            self.select.model().item(index) .setEnabled(True)
            self.select                     .setCurrentIndex(index)

        else:
            # disables the unchecked variable on the select combobox,
            # and sets it to the first enabled entry. If none found then CPM is selected
            self.select.model().item(index) .setEnabled(False)
            foundSelVar = 0
            for i, key in enumerate(gglobs.varsBook):
                #print("i, key, self.select.model().item(i) .isEnabled():", i, key, self.select.model().item(i) .isEnabled())
                if self.select.model().item(i) .isEnabled():
                    foundSelVar = i
                    break
            if self.select.currentIndex() == index: self.select.setCurrentIndex(foundSelVar)

        #print("----self.select.model().item(index).isEnabled:", self.select.model().item(index).isEnabled())

        # if the index is not changed, then an update is needed; otherwise
        # a changed index results in an update anyway via changedGraphSelectedVariable
        if self.select.currentIndex() == oldIndex:  self.applyGraphOptions()


    def changedGraphOptionsAvg(self, i):
        """Graph Option Avg has changed"""

        #print("changedGraphOptionsAvg: i:", i)
        gglobs.avgChecked  = self.avgbox.isChecked()
        self.applyGraphOptions()


    def changedGraphOptionsMav(self, i):
        """Graph Option Mav has changed"""

        #print("changedGraphOptionsMav: i:", i)
        gglobs.mavChecked  = self.mavbox.isChecked()
        if gglobs.mavChecked: gglobs.fprintMAV = True
        self.applyGraphOptions()


    def changedGraphOptionsMavText(self, i):
        """Graph Option MavText has changed"""

        #print("changedGraphOptionsMavText: i:", i)
        if self.mavbox.isChecked():
            #print("self.mavbox.isChecked():", self.mavbox.isChecked())
            gglobs.fprintMAV = True

        self.applyGraphOptions()


    def changedGraphCountUnit(self, i):
        """counter unit Graph Options for left Y-axis was changed"""

        oldYunit            = gglobs.YunitCurrent
        gglobs.YunitCurrent = str(self.yunit.currentText())
        newYunit            = gglobs.YunitCurrent
        #print("changedGraphCountUnit: i:", i, ",  oldYunit:", oldYunit, ",  newYunit:", newYunit)

        # convert Y to CPM unit if not already CPM
        print("changedGraphCountUnit: gglobs.Ymin, gglobs.Ymax, gglobs.calibration1st", gglobs.Ymin, gglobs.Ymax, gglobs.calibration1st)
        if oldYunit == "µSv/h":
            if gglobs.Ymin != None: gglobs.Ymin = gglobs.Ymin / gglobs.calibration1st
            if gglobs.Ymax != None: gglobs.Ymax = gglobs.Ymax / gglobs.calibration1st

        # convert Y to µSv/h unit if not already µSv/h
        if newYunit == "µSv/h":
            if gglobs.Ymin != None: gglobs.Ymin = gglobs.Ymin * gglobs.calibration1st
            if gglobs.Ymax != None: gglobs.Ymax = gglobs.Ymax * gglobs.calibration1st

        if gglobs.Ymin == None: self.ymin.setText("")
        else:                   self.ymin.setText("{:.5g}".format(gglobs.Ymin))

        if gglobs.Ymax == None: self.ymax.setText("")
        else:                   self.ymax.setText("{:.5g}".format(gglobs.Ymax))

        if newYunit == "µSv/h":
            for vname in ("CPM", "CPS", "CPM1st", "CPS1st", "CPM2nd", "CPS2nd", "CPM3rd", "CPS3rd"):
                gglobs.varsBook[vname][2] = "µSv/h"

        else: # newYunit == CPM
            for vname in ("CPM", "CPM1st", "CPM2nd", "CPM3rd"):
                gglobs.varsBook[vname][2] = "CPM"

            for vname in ("CPS", "CPS1st", "CPS2nd", "CPS3rd"):
                gglobs.varsBook[vname][2] = "CPS"

        self.applyGraphOptions()


    def changedGraphTemperatureUnit(self, i):
        """Temperature unit Graph Options was changed"""

        #print("changedGraphTemperatureUnit: New T unit:  i:", i, str(self.y2unit.currentText()) )

        if   i == 0:    gglobs.varsBook["T"][2] = "°C"
        elif i == 1:    gglobs.varsBook["T"][2] = "°F"

        self.applyGraphOptions()


    def changedGraphTimeUnit(self, i):
        """recalc xmin, xmax on Time unit changes"""

        #print("-----------------------changedGraphTimeUnit: i:", i)

        if np.all(gglobs.logTime) == None: return

        gsup_plot.changeTimeUnitofPlot(self.xunit.currentText())

        #~oldXunit = gglobs.XunitCurrent
        #~#print("changedGraphTimeUnit: oldXunit: ", oldXunit)

        #~# convert all entries to days since start
        #~if   oldXunit == "Time":
            #~if gglobs.Xleft  != None: gglobs.Xleft  = gglobs.Xleft  - gglobs.logTimeFirst
            #~if gglobs.Xright != None: gglobs.Xright = gglobs.Xright - gglobs.logTimeFirst

        #~elif oldXunit == "month":
            #~if gglobs.Xleft  != None: gglobs.Xleft  = gglobs.Xleft  * 30.42 # 365 / 12 = 30.4167
            #~if gglobs.Xright != None: gglobs.Xright = gglobs.Xright * 30.42 # 365 / 12 = 30.4167

        #~elif oldXunit == "week":
            #~if gglobs.Xleft  != None: gglobs.Xleft  = gglobs.Xleft  * 7
            #~if gglobs.Xright != None: gglobs.Xright = gglobs.Xright * 7

        #~elif oldXunit == "day": # no changes all in days
            #~if gglobs.Xleft  != None: gglobs.Xleft  = gglobs.Xleft
            #~if gglobs.Xright != None: gglobs.Xright = gglobs.Xright

        #~elif oldXunit == "hour":
            #~if gglobs.Xleft  != None: gglobs.Xleft  = gglobs.Xleft  / 24.
            #~if gglobs.Xright != None: gglobs.Xright = gglobs.Xright / 24.

        #~elif oldXunit == "minute":
            #~if gglobs.Xleft  != None: gglobs.Xleft  = gglobs.Xleft  / 1440.
            #~if gglobs.Xright != None: gglobs.Xright = gglobs.Xright / 1440.

        #~elif oldXunit == "second":
            #~if gglobs.Xleft  != None: gglobs.Xleft  = gglobs.Xleft  / 86400.
            #~if gglobs.Xright != None: gglobs.Xright = gglobs.Xright / 86400.

        #~#gglobs.XunitCurrent = str(self.xunit.currentText())
        #~#print("changedGraphTimeUnit: gglobs.XunitCurrent: ", gglobs.XunitCurrent)
        #~#newXunit            = gglobs.XunitCurrent
        #~newXunit            = self.xunit.currentText()
        #~if newXunit == "auto":
            #~l = gglobs.logTime.max() - gglobs.logTime.min()
            #~#print "l=", l
            #~if   l         > 3:  Xunit = "day"
            #~elif l * 24.   > 3:  Xunit = "hour"
            #~elif l * 1440. > 3:  Xunit = "minute"
            #~else:                Xunit = "second"

            #~newXunit = Xunit

        #~gglobs.XunitCurrent = newXunit
        #~#print("changedGraphTimeUnit: gglobs.XunitCurrent: ", gglobs.XunitCurrent)
        #~gglobs.Xunit        = newXunit
        #~#print( "newXunit", newXunit)

        #~if newXunit == "Time":
            #~if gglobs.Xleft  != None: gglobs.Xleft =  (str(mpld.num2date((gglobs.Xleft  + gglobs.logTimeFirst))))[:19]
            #~if gglobs.Xright != None: gglobs.Xright = (str(mpld.num2date((gglobs.Xright + gglobs.logTimeFirst))))[:19]

        #~elif newXunit == "month":
            #~if gglobs.Xleft  != None: gglobs.Xleft  = gglobs.Xleft  / 30.42 # 365 / 12 = 30.4167
            #~if gglobs.Xright != None: gglobs.Xright = gglobs.Xright / 30.42 # 365 / 12 = 30.4167

        #~elif newXunit == "week":
            #~if gglobs.Xleft  != None: gglobs.Xleft  = gglobs.Xleft  / 7
            #~if gglobs.Xright != None: gglobs.Xright = gglobs.Xright / 7

        #~elif newXunit == "day": # no changes all in days
            #~if gglobs.Xleft  != None: gglobs.Xleft  = gglobs.Xleft
            #~if gglobs.Xright != None: gglobs.Xright = gglobs.Xright

        #~elif newXunit == "hour":
            #~if gglobs.Xleft  != None: gglobs.Xleft  = gglobs.Xleft  * 24.
            #~if gglobs.Xright != None: gglobs.Xright = gglobs.Xright * 24.

        #~elif newXunit == "minute":
            #~if gglobs.Xleft  != None: gglobs.Xleft  = gglobs.Xleft  * 1440.
            #~if gglobs.Xright != None: gglobs.Xright = gglobs.Xright * 1440.

        #~elif newXunit == "second":
            #~if gglobs.Xleft  != None: gglobs.Xleft  = gglobs.Xleft  * 86400.
            #~if gglobs.Xright != None: gglobs.Xright = gglobs.Xright * 86400.

        #~if gglobs.Xleft == None:
            #~self.xmin.setText("")
        #~else:
            #~try:    xl = "{:1.8f}".format(float(gglobs.Xleft))
            #~except: xl = gglobs.Xleft
            #~self.xmin.setText(xl)

        #~if gglobs.Xright == None:
            #~self.xmax.setText("")
        #~else:
            #~try:    xr = "{:1.8f}".format(float(gglobs.Xright))
            #~except: xr = gglobs.Xright
            #~self.xmax.setText(xr)

        self.applyGraphOptions()


    def keyPressEvent(self, event):
        """Apply Graph is only Button to accept Enter and Return key"""

        # from: http://pyqt.sourceforge.net/Docs/PyQt4/qt.html#Key-enum
        # Qt.Key_Return     0x01000004
        # Qt.Key_Enter      0x01000005  Typically located on the keypad. (= numeric keypad)
        #print("event.key():", event.key())

        if event.key() in (Qt.Key_Enter, Qt.Key_Return):
            self.applyGraphOptions()


    def plotVarsOffOn(self, newstate="OFF"): # alt: 'ON'
        """checks or unchecks all variables from plotting"""

        gglobs.allowGraphUpdate    = False
        if newstate == "OFF":
            for i, vname in enumerate(gglobs.varsBook):
                self.varDisplayCheckbox[vname].setChecked(False)
                self.select.model().item(i)   .setEnabled(False)
        else:
            for i, vname in enumerate(gglobs.varsBook):
                if gglobs.varcheckedCurrent[vname]:
                    self.varDisplayCheckbox[vname].setChecked(True)
                    self.varDisplayCheckbox[vname].setEnabled(True)
                    self.select.model().item(i)   .setEnabled(True)

        # makes the index of the first enabled variable as the currentindex of the
        # variable select drop-down box
        for i, vname in enumerate(gglobs.varsBook):
            #print("----i, self.select.model().item(i).isEnabled:", i, gglobs.exgg.select.model().item(i).isEnabled())
            if self.select.model().item(i).isEnabled():
                gglobs.exgg.select          .setCurrentIndex(i)
                break

        gglobs.allowGraphUpdate    = True
        self.applyGraphOptions() # not automatically done due to
                                 # blocking by gglobs.allowGraphUpdate


    def clearGraphLimits(self, fprintMAV = False):
        """resets all min, max graph options to empty and plots the graph"""

        dprint("clearGraphLimits:")
        setDebugIndent(1)

        gglobs.Xleft               = None
        gglobs.Xright              = None
        self.xmin.                   setText("")
        self.xmax.                   setText("")

        gglobs.Ymin                = None
        gglobs.Ymax                = None
        self.ymin.                   setText("")
        self.ymax.                   setText("")

        gglobs.Y2min               = None
        gglobs.Y2max               = None
        self.y2min.                  setText("")
        self.y2max.                  setText("")

        gsup_plot.makePlot()

        setDebugIndent(0)


    def reset_replotGraph(self, fprintMAV = False):
        """resets all graph options to start conditions and plots the graph"""

        dprint("reset_replotGraph:")
        setDebugIndent(1)

        gglobs.allowGraphUpdate    = False

        gglobs.Xleft               = None
        gglobs.Xright              = None
        gglobs.Xunit               = "Time"
        self.xmin.                   setText("")
        self.xmax.                   setText("")
        self.xunit.                  setCurrentIndex(0)

        gglobs.Ymin                = None
        gglobs.Ymax                = None
        gglobs.Yunit               = "CPM"
        self.ymin.                   setText("")
        self.ymax.                   setText("")
        self.yunit.                  setCurrentIndex(0)

        gglobs.Y2min               = None
        gglobs.Y2max               = None
        gglobs.Y2unit              = "°C"
        self.y2min.                  setText("")
        self.y2max.                  setText("")
        self.y2unit.                 setCurrentIndex(0)

        self.select.                 setCurrentIndex(0)
        self.select.                 setEnabled(True)

        gglobs.avgChecked          = False
        self.avgbox.                 setChecked(gglobs.avgChecked)

        gglobs.mavChecked          = False
        self.mavbox.                 setChecked(gglobs.mavChecked)

        gglobs.mav                 = gglobs.mav_initial
        self.mav.                    setText("{:0.0f}".format(gglobs.mav_initial))

        gglobs.varsBook            = gglobs.varsDefault.copy() # reset colors and linetype

        gglobs.allowGraphUpdate    = True

        self.updateDisplayVariableValue()
        self.plotVarsOffOn(newstate="ON")   # also does a plot with applyGraphOptions # just changed

        setDebugIndent(0)


    def applyGraphOptions(self):

        if gglobs.currentConn == None: return

        fncname = "applyGraphOptions: "

        #replace comma with dot, strip outer whitespace
        xmin  = (str(self.xmin.text()).replace(",", ".")).strip()
        xmax  = (str(self.xmax.text()).replace(",", ".")).strip()
        xunit = str(self.xunit.currentText())

        ymin  = (str(self.ymin.text()).replace(",", ".")).strip()
        ymax  = (str(self.ymax.text()).replace(",", ".")).strip()
        yunit = str(self.yunit.currentText())

        y2min = (str(self.y2min.text()).replace(",", ".")).strip()
        y2max = (str(self.y2max.text()).replace(",", ".")).strip()

        mav   = (str(self.mav.text()).replace(",", ".") ).strip()

        #~print(fncname + "X : xmin:'{}', xmax:'{}', xunit:'{}', gglobs.Xunit:'{}'".format(xmin, xmax, xunit, gglobs.Xunit))
        #~print(fncname + "Y : ymin:'{}', ymax:'{}', yunit:'{}', gglobs.Yunit:'{}'".format(ymin, ymax, yunit, gglobs.Yunit))
        #~print(fncname + "Y2: ymin:'{}', ymax:'{}'                      ".format(y2min, y2max))
        #~print(fncname + "mav:'{}'".format(mav))

    # x
        if  xmin == "":
            gglobs.Xleft  = None
        else:
            if gglobs.Xunit == "Time":
                try:
                    gglobs.Xleft = mpld.datestr2num(str(xmin))
                except:
                    gglobs.Xleft = None
                    efprint("Did not recognize Time Min")
            else:
                try:
                    gglobs.Xleft     = float(xmin)
                except:
                    gglobs.Xleft     = None
                    efprint("Did not recognize Time Min")

        if  xmax == "":
            gglobs.Xright = None
        else:
            if gglobs.Xunit == "Time":
                try:
                    gglobs.Xright = mpld.datestr2num(str(xmax))
                except:
                    gglobs.Xright = None
                    efprint("Did not recognize Time Max")
            else:
                try:
                    gglobs.Xright    = float(xmax)
                except:
                    gglobs.Xright    = None
                    efprint("Did not recognize Time Max")

        #print(fncname + "Xleft ", gglobs.Xleft,  ",  Xright", gglobs.Xright)

        if gglobs.Xleft != None and gglobs.Xright != None:
            if gglobs.Xleft >= gglobs.Xright:
                efprint("Wrong numbers: Time Min must be less than Time Max")
                return

        gglobs.Xunit     = xunit

    # y
        try:    gglobs.Ymin      = float(ymin)
        except: gglobs.Ymin      = None

        try:    gglobs.Ymax      = float(ymax)
        except: gglobs.Ymax      = None

        if gglobs.Ymin != None and gglobs.Ymax != None:
            if gglobs.Ymin >= gglobs.Ymax:
                efprint("Wrong numbers: Count Rate min must be less than Count Rate max")
                return

        gglobs.Yunit     = yunit

    # y2
        try:    gglobs.Y2min      = float(y2min)
        except: gglobs.Y2min      = None

        try:    gglobs.Y2max      = float(y2max)
        except: gglobs.Y2max      = None

        if gglobs.Y2min != None and gglobs.Y2max != None:
            if gglobs.Y2min >= gglobs.Y2max:
                efprint("Wrong numbers: Ambient min must be less than Ambient max")
                return

    # mav
        try:    gglobs.mav     = float(mav)
        except: gglobs.mav     = gglobs.mav_initial

    # color
        colorName = gglobs.varsBook[getNameSelectedVar()][3]
        self.btnColor.setText("")
        self.btnColor.setStyleSheet("QLabel { border: 1px solid silver;  border-radius: 3px; background-color: %s ; }" % (colorName))
        addMenuTip(self.btnColor, self.btnColorText + colorName)

    # replot
        gsup_plot.makePlot()
        self.updateDisplayVariableValue()


    def plotGraph(self, dataType):
        """Plots the data as graph; dataType is Log or His"""

        if  dataType == "Log" and gglobs.logConn == None or \
            dataType == "His" and gglobs.hisConn == None:
            self.showStatusMessage("No data available")
            return

        dprint("plotGraph: dataType:", dataType)
        setDebugIndent(1)

        if dataType == "Log":
            gglobs.activeDataSource     = "Log"
            gglobs.currentConn          = gglobs.logConn
            gglobs.currentDBPath        = gglobs.logDBPath
            gglobs.currentDBData        = gglobs.logDBData
            gglobs.varcheckedCurrent    = gglobs.varcheckedLog.copy()

            self.dcfLog.setText(gglobs.currentDBPath)
            self.dcfLog.setStyleSheet("QLineEdit { background-color: #F9F4C9; color: rgb(80,80,80); }")
            self.dcfHis.setStyleSheet("QLineEdit { background-color: #DFDEDD; color: rgb(80,80,80); }")

        elif dataType == 'His':
            gglobs.activeDataSource     = "His"
            gglobs.currentConn          = gglobs.hisConn
            gglobs.currentDBPath        = gglobs.hisDBPath
            gglobs.currentDBData        = gglobs.hisDBData
            gglobs.varcheckedCurrent    = gglobs.varcheckedHis.copy()

            self.dcfHis.setText(gglobs.currentDBPath)
            self.dcfHis.setStyleSheet("QLineEdit { background-color: #F9F4C9; color: rgb(80,80,80); }")
            self.dcfLog.setStyleSheet("QLineEdit { background-color: #DFDEDD; color: rgb(80,80,80); }")

        else:
            dprint("PROGRAMMING ERROR in geigerlog:plotGraph: var dataType is:", dataType, debug=True)
            sys.exit(1)

        #print("plotGraph: gglobs.activeDataSource:", gglobs.activeDataSource)
        #print("plotGraph: gglobs.currentDBPath, gglobs.logDBPath, gglobs.hisDBPath:\n", gglobs.currentDBPath, "\n", gglobs.logDBPath, "\n", gglobs.hisDBPath)
        #print("plotGraph: gglobs.currentConn, gglobs.logConn, gglobs.hisConn:\n", gglobs.currentConn, "\n", gglobs.logConn, "\n", gglobs.hisConn)
        #print("plotGraph: gglobs.varcheckedCurrent   ", gglobs.varcheckedCurrent)
        #print("plotGraph: gglobs.varcheckedLog", gglobs.varcheckedLog)
        #print("plotGraph: gglobs.varcheckedHis", gglobs.varcheckedHis)

        gglobs.allowGraphUpdate    = False
        for i, vname in enumerate(gglobs.varsBook):
            value  = gglobs.varcheckedCurrent[vname]   # bool
            #print("vname, values in gglobs.varcheckedCurrent.items():", vname, value)
            self.varDisplayCheckbox[vname]  .setChecked(value)
            self.varDisplayCheckbox[vname]  .setEnabled(value)
            self.select.model().item(i)     .setEnabled(value)
        gglobs.allowGraphUpdate    = True


        if gglobs.currentDBData.size > 0:
            fprint(header("Plot Data"))
            fprint("from: {}".format(gglobs.currentDBPath))

        self.figure.set_facecolor('#F9F4C9') # change colorbg in graph from gray to light yellow
        self.reset_replotGraph()

        setDebugIndent(0)


    def updatecursorposition(self, event):
        """when cursor inside plot, get position and print to statusbar"""
        # see: https://matplotlib.org/api/backend_bases_api.html#matplotlib.backend_bases.MouseEvent

        # calc based on:
        # gglobs.y1_limit = ax1.get_ylim    defined in gsup_plot.py
        # gglobs.y2_limit = ax2.get_ylim

        #print("updatecursorposition: event: ", event, ", event.inaxes: ", event.inaxes, end="   ")

        try: # results in non-breaking error messages when no data are displayed
            if event.inaxes:
                x  = event.xdata
                y2 = event.ydata
                #print("updatecursorposition: ", x, y2)
                y1 = (y2 - gglobs.y2_limit[0]) / (gglobs.y2_limit[1] - gglobs.y2_limit[0]) * (gglobs.y1_limit[1] - gglobs.y1_limit[0]) + gglobs.y1_limit[0]

                if gglobs.Xunit == "Time":
                    tod = (str(mpld.num2date(x)))[:19]          # time of day
                    t   = gsup_plot.getTimeSinceFirstRecord(gglobs.logTimeFirst, x)

                else:
                    tod = gsup_plot.getTimeOfDay(gglobs.logTimeFirst, x, gglobs.XunitCurrent)
                    t   = "{:0.3f} {}s".format(x, gglobs.XunitCurrent)

                message = "Time since 1st record: {}, Time: {}, Counter: {:0.3f}, Ambient: {:0.3f}".format(t, tod, y1, y2)
                self.showStatusMessage(message, timing=0, error=False) # message remains until overwritten by next
        except:
            #print("event not inaxes")
            pass


    def onclick(self, event):
        """on mouseclick in graph enter time coords into xmin, xmax
        left click = xmin, right click = xmax"""

        try: # if no data are shown, this may result in non-breaking error messages
            if event.inaxes:
                x = event.xdata
                y = event.ydata
                b = event.button
                #print event, x,y,b

                if gglobs.Xunit == "Time":
                    t = (str(mpld.num2date(x)))[:19]
                else:
                    t = "{:0.6f}".format(x)

                if b == 1:                  # left click, xmin
                    self.xmin.setText(t)
                elif b == 3:                # right click, xmax
                    self.xmax.setText(t)
                else:
                    pass
        except:
            pass


#history
    def getHistory(self, source = "Binary File"):
        """getHistory from source. source is one out of:
        - "Device"
        - "Database"
        - "Binary File"
        - "Parsed File"
        no return; data stored in global variables"""

    #
    # make the filedialog
    #
        # conditions
        if   source == "Database":
            # there must be an existing '*hisdb' file;
            # writing to it is not necessary; it will not be modified
            dlg=QFileDialog(caption = "Get History from Existing Database File", options=QFileDialog.DontUseNativeDialog)
            dlg.setFileMode(QFileDialog.ExistingFile)
            dlg.setNameFilter("History Files (*.hisdb)")

        elif source == "Binary File":
            # there must be an existing, readable '*.bin' file,
            # and it must be allowed to write .hisdb files
            # the bin file will remain unchanged
            dlg=QFileDialog(caption = "Get History from Existing Binary File", options=QFileDialog.DontUseNativeDialog)
            dlg.setFileMode(QFileDialog.ExistingFile)
            dlg.setNameFilter("History Files (*.bin)")

        elif source == "Parsed File":
            # there must be an existing, readable '*.his' file
            # and it must be allowed to write .hisdb files
            # the his file will remain unchanged
            dlg=QFileDialog(caption= "Get History from Existing *.his or other CSV File", options=QFileDialog.DontUseNativeDialog)
            dlg.setFileMode(QFileDialog.ExistingFile)
            dlg.setNameFilter("History Files (*.log *.his *.csv *.txt *.notes)")

        elif source == "Device":    # a GMC device
            if gglobs.logging:
                fprint(header("Get History from GMC Device"))
                efprint("Cannot load History when logging. Stop Logging first")
                return

            # may use existing or new .hisdb file, but must be allowed to overwrite this file
            # an existing hisdb file will be overwritten
            dlg=QFileDialog(caption = "Get History from GMC Device - enter new filename or select from existing", options=QFileDialog.DontUseNativeDialog)
            dlg.setFileMode(QFileDialog.AnyFile)
            dlg.setNameFilter("History Files (*.hisdb)")

        elif source == "GSDevice":  # a Gamma Scout device
            # may use existing or new .hisdb file, but must be allowed to overwrite this file
            # an existing hisdb file will be overwritten
            dlg=QFileDialog(caption = "Get History from Gamma-Scout Device - enter new filename or select from existing", options=QFileDialog.DontUseNativeDialog)
            dlg.setFileMode(QFileDialog.AnyFile)
            dlg.setNameFilter("History Files (*.hisdb)")

        elif source == "GSDatFile":
            # there must be an existing, readable '*.dat' file, created by
            # memory dumping of a Gamm Scout device,
            # and it must be allowed to write .hisdb files
            # the dat file will remain unchanged
            dlg=QFileDialog(caption = "Get History from Existing Gamma Scout *.dat File", options=QFileDialog.DontUseNativeDialog)
            dlg.setFileMode(QFileDialog.ExistingFile)
            dlg.setNameFilter("History Files (*.dat)")

        elif source == "AMDeviceCAM":  # an AmbioMon device for CAM data
            # may use existing or new .hisdb file, but must be allowed to overwrite this file
            # an existing hisdb file will be overwritten
            dlg=QFileDialog(caption = "Get History from AmbioMon Device - enter new filename or select from existing", options=QFileDialog.DontUseNativeDialog)
            dlg.setFileMode(QFileDialog.AnyFile)
            dlg.setNameFilter("History Files (*.hisdb)")

        elif source == "AMDeviceCPS":  # an AmbioMon device for CPS data
            # may use existing or new .hisdb file, but must be allowed to overwrite this file
            # an existing hisdb file will be overwritten
            dlg=QFileDialog(caption = "Get History from AmbioMon Device - enter new filename or select from existing", options=QFileDialog.DontUseNativeDialog)
            dlg.setFileMode(QFileDialog.AnyFile)
            dlg.setNameFilter("History Files (*.hisdb)")

        #~ elif source == "AMDatFile":
            #~ ####### not valid -- placeholder for AmbioMon !!!!!!!! ############
            #~ # wird es auch nicht geben, da CSV Files verwendet werden !!!
            #~ #
            #~ # there must be an existing, readable '*.dat' file, created by
            #~ # memory dumping of a Gamm Scout device,
            #~ # and it must be allowed to write .hisdb files
            #~ # the dat file will remain unchanged
            #~ dlg=QFileDialog(caption = "Get History from Existing Gamma Scout *.dat File", options=QFileDialog.DontUseNativeDialog)
            #~ dlg.setFileMode(QFileDialog.ExistingFile)
            #~ dlg.setNameFilter("History Files (*.dat)")

        elif source == "AMFileCAM":
            # there must be an existing, readable '*.CAM' file, created by
            # e.g. downloading from an AmbioMon device,
            # and it must be allowed to write .hisdb files
            # the *.CAM file will remain unchanged
            dlg=QFileDialog(caption = "Get History from Existing AmbioMon binary *.CAM File", options=QFileDialog.DontUseNativeDialog)
            dlg.setFileMode(QFileDialog.ExistingFile)
            dlg.setNameFilter("History Binary Files (*.CAM)")

        elif source == "AMFileCPS":
            # there must be an existing, readable '*.CPS' file, created by
            # e.g. downloading from an AmbioMon device,
            # and it must be allowed to write .hisdb files
            # the *.CPS file will remain unchanged
            dlg=QFileDialog(caption = "Get History from Existing AmbioMon binary *.CPS File", options=QFileDialog.DontUseNativeDialog)
            dlg.setFileMode(QFileDialog.ExistingFile)
            dlg.setNameFilter("History Binary Files (*.CPS)")

        else:
            printProgError("getHistory: Filedialog: Wrong source: ", source)

        dlg.setViewMode     (QFileDialog.Detail)
        dlg.setWindowIcon   (self.iconGeigerLog)
        dlg.setDirectory    (gglobs.fileDialogDir)

        dlg.setFixedSize(950, 550)

        # Execute dialog
        if dlg.exec_() == QDialog.Accepted:  pass     # QDialog Accepted
        else:                                return   # QDialog Rejected
    ### end filedialog -  a file was selected

    #
    # Process the selected file
    #
        while True:
            fprint(header("Get History from {}".format(source)))
            dprint("getHistory: from source: ", source)
            setDebugIndent(1)

            gglobs.fileDialogDir = dlg.directory().path() # remember the directory
            #print("getHistory: fileDialogDir:", gglobs.fileDialogDir)

            fnames      = dlg.selectedFiles()
            fname       = str(fnames[0])                # file path
            fext        = os.path.splitext(fname)[1]    # file ext
            fname_base  = os.path.splitext(fname)[0]    # file basename with path w/o ext
            dprint( "getHistory: fname: '{}', fname_base: '{}', fext: '{}'".format(fname, fname_base, fext))

            gglobs.binFilePath = None
            gglobs.hisFilePath = None
            gglobs.datFilePath = None

            if   source == "Database":
                gglobs.hisDBPath   = fname # already has extension ".hisdb"
                if not isFileReadable(gglobs.hisDBPath):     break

            elif source == "Binary File":
                gglobs.binFilePath = fname
                gglobs.hisDBPath   = fname_base + ".hisdb"
                if not isFileReadable (gglobs.binFilePath):  break
                if not isFileWriteable(gglobs.hisDBPath):    break

            elif source == "Parsed File":
                gglobs.hisFilePath = fname
                gglobs.hisDBPath   = fname_base + ".hisdb"
                if not isFileReadable (gglobs.hisFilePath):  break
                if not isFileWriteable(gglobs.hisDBPath):    break

            elif source in ("Device", "GSDevice", "AMDeviceCAM", "AMDeviceCPS"):
                if fext != ".hisdb":
                    gglobs.hisDBPath   = fname + ".hisdb" # file has any extension or none
                else:
                    gglobs.hisDBPath   = fname            # file already has .hisdb extension
                if not isFileWriteable(gglobs.hisDBPath):    break

            elif source == "GSDatFile":
                gglobs.datFilePath = fname
                gglobs.hisDBPath   = fname + ".hisdb"
                if not isFileReadable (gglobs.datFilePath):  break
                if not isFileWriteable(gglobs.hisDBPath):    break

            elif source in ("AMFileCAM", "AMFileCPS"):
                gglobs.AMFilePath = fname
                gglobs.hisDBPath   = fname + ".hisdb"
                if not isFileReadable (gglobs.AMFilePath):   break
                if not isFileWriteable(gglobs.hisDBPath):    break

            else:
                printProgError("getHistory: Processing Selected File: Wrong source: ", source)


            # Messagebox re Overwriting file
            if source in ("Device", "GSDevice", "AMDeviceCAM", "AMDeviceCPS"):
                if os.path.isfile(gglobs.hisDBPath):
                    msg = QMessageBox()
                    msg.setIcon(QMessageBox.Critical)
                    msg.setWindowTitle("CAUTION")
                    critical  = """You selected an existing file, which will be <b>OVERWRITTEN</b> if you continue. Please confirm with OK.
                                    <br><br>Otherwise click Cancel and enter a new filename in the Get History from Device dialog."""
                    msg.setText(critical)
                    msg.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
                    msg.setDefaultButton(QMessageBox.Cancel)
                    msg.setEscapeButton(QMessageBox.Cancel)
                    retval = msg.exec_()

                    if retval != 1024:
                        fprint("Get History is cancelled")
                        break

            gglobs.currentDBPath   = gglobs.hisDBPath

            #dprint("getHistory: gglobs.binFilePath:     ", gglobs.binFilePath)
            #dprint("getHistory: gglobs.hisFilePath:     ", gglobs.hisFilePath)
            #dprint("getHistory: gglobs.hisDBPath:       ", gglobs.hisDBPath)
            #dprint("getHistory: gglobs.currentDBPath:   ", gglobs.currentDBPath)

            self.setBusyCursor()
            fprint("History database: {}"        .format(gglobs.hisDBPath))
            dprint("getHistory: database file:{}".format(gglobs.hisDBPath))

            self.dcfHis.setText(gglobs.currentDBPath)
            self.clearLogPad()

            # an existing classic his, bin, or dat file was selected,
            # delete old database first
            if      gglobs.hisFilePath != None \
                or  gglobs.binFilePath != None \
                or  gglobs.datFilePath != None \
                or  gglobs.hisDBPath   != None and source in ("Device", "GSDevice", "AMDeviceCAM", "AMDeviceCPS") :

                gsup_sql.DB_deleteDatabase("His", gglobs.hisDBPath)

            # Open the database
            gglobs.hisConn = gsup_sql.DB_openDatabase  (gglobs.hisConn, gglobs.hisDBPath)

            if gglobs.hisFilePath != None:
                fprint("Creating from file {}".format(gglobs.hisFilePath))
                # read data from CSV file into database
                self.setNormalCursor()
                success = gsup_sql.getCSV(gglobs.hisFilePath)
                if success:
                    self.setBusyCursor()
                    gsup_sql.DB_convertCSVtoDB(gglobs.hisConn, gglobs.hisFilePath)
                else:
                    efprint("Database creation was cancelled")
                    return

            elif gglobs.binFilePath != None:
                fprint("Creating from file {}".format(gglobs.binFilePath))

            # Make Hist for source = GMC Device, GMC Binary File
            if source in ("Device", "Binary File"):
                error, message = gdev_gmc_hist.makeGMC_History(source)
                if error == -1:                                # a severe error
                    efprint(message)
                    break

            # Make Hist for source = Gamma Scout device or Gamma Scout *.dat File
            elif source in ("GSDevice", "GSDatFile"):
                error, message = gdev_scout.GSmakeHistory(source)
                if error == -1:                                # a severe error
                    efprint(message)
                    break

            # Make Hist for source = AmbioMon device
            elif source in ("AMDeviceCAM", "AMDeviceCPS"):
                error, message = gdev_ambiomon.makeAmbioHistory(source, gglobs.AmbioDeviceName)
                if error == -1:                                # a severe error
                    efprint(message)
                    break

            # Make Hist for source = AmbioMon binary file
            elif source in ("AMFileCAM", "AMFileCPS"):
                error, message = gdev_ambiomon.makeAmbioHistory(source, gglobs.AmbioDeviceName)
                if error == -1:                                # a severe error
                    efprint(message)
                    break

            gglobs.hisDBData, gglobs.varcheckedHis = gsup_sql.getDataFromDatabase() # also creates varchecked

            self.plotGraph("His")
            self.checkLoggingState()
            Qt_update() # to make Normal Cursor appear only after graph shown
            break

        self.setNormalCursor()

        setDebugIndent(0)


    def setLogCycle(self):
        """Set logcycle"""

        fncname = "setLogCycle: "

        if gglobs.devel:
            fprint("Cycle Dur: Get, Plot, Total:", "{:3.0f}, {:3.0f}, {:3.0f} [ms]".format(gglobs.LogGetValDur, gglobs.LogPlotDur, gglobs.LogTotalDur))

        dprint(fncname)
        setDebugIndent(1)

        lctime     = QLabel("Log Cycle [s]\n(0.1 ... 999)")
        lctime.setAlignment(Qt.AlignLeft)

        self.ctime  = QLineEdit()
        validator = QDoubleValidator(0.1, 999, 1, self.ctime)
        self.ctime.setValidator(validator)
        self.ctime.setToolTip('The log cycle in seconds')
        self.ctime.setText("{:0.3g}".format(gglobs.logcycle))

        graphOptions=QGridLayout()
        graphOptions.addWidget(lctime,                  0, 0)
        graphOptions.addWidget(self.ctime,              0, 1)

        graphOptionsGroup = QGroupBox()
        graphOptionsGroup.setLayout(graphOptions)

        d = QDialog() # set parent empty to popup in center of screen
        d.setWindowIcon(self.iconGeigerLog)
        d.setFont(self.fontstd)
        d.setWindowTitle("Set Log Cycle")
        d.setWindowModality(Qt.ApplicationModal)
        #d.setWindowModality(Qt.NonModal)
        #d.setWindowModality(Qt.WindowModal)

        self.bbox = QDialogButtonBox()
        self.bbox.setStandardButtons(QDialogButtonBox.Cancel | QDialogButtonBox.Ok )
        self.bbox.accepted.connect(lambda: d.done(0))
        self.bbox.rejected.connect(lambda: d.done(99))

        gglobs.btn = self.bbox.button(QDialogButtonBox.Ok)
        gglobs.btn.setEnabled(True)

        layoutV = QVBoxLayout(d)
        layoutV.addWidget(graphOptionsGroup)
        layoutV.addWidget(self.bbox)

        self.ctime.textChanged.connect(self.check_state) # last chance
        self.ctime.textChanged.emit   (self.ctime.text())

        if gglobs.logging:
            gglobs.btn.setEnabled(False)
            self.ctime.setEnabled(False)
            self.ctime.setStyleSheet('QLineEdit { background-color: %s;  }' % ("#e0e0e0",))

        retval = d.exec_()
        #print("reval:", retval)

        if retval == 99:
            dprint(fncname + "Escape, cycle time unchanged: ", gglobs.logcycle)
        else:
            # change the cycle time
            oldlogcycle = gglobs.logcycle
            logcycle    = self.ctime.text().replace(",", ".")  #replace comma with dot
            try:    lc  = round(float(logcycle), 1)
            except: lc  = oldlogcycle

            gglobs.logcycle = lc
            self.showTimingSetting(gglobs.logcycle)
            dprint(fncname + "ok, new cycle time: ", gglobs.logcycle)

            # update database with logcyle
            if gglobs.logConn != None:
                gsup_sql.DB_updateLogcycle(gglobs.logConn, gglobs.logcycle)

        setDebugIndent(0)


    def check_state(self, *args, **kwargs):

        sender = self.sender()

        #print("sender.text():", sender.text())
        #print("args:", args)
        #print("kwargs:", kwargs)

        try:
            v = float(sender.text().replace(",", "."))
            if   v < 0.1:   state = 0       # too low
            elif v > 999:   state = 0       # too high
            else:           state = 2       # ok
        except:
            state = 0           # wrong

        #~print("QValidator.Acceptable:", QValidator.Acceptable)

        # Value: QValidator.Acceptable == 2
        if state == QValidator.Acceptable:
            bgcolor = 'white' # white
            color   = 'black'
            gglobs.btn.setEnabled(True)
        #elif state == QValidator.Intermediate:
        #    color = '#fff79a' # yellow
        else:
            bgcolor = '#fff79a' # yellow
            color   = 'red'
            self.ctime.setFocus()
            gglobs.btn.setEnabled(False)

        sender.setStyleSheet('QLineEdit { background-color: %s; color: %s }' % (bgcolor, color))


#logging
    def startLogging(self):
        """Starts the logging"""

        dprint("startLogging:")
        setDebugIndent(1)

        fprint(header("Start Logging"))

        while True:

            # A logfile is not loaded
            # should never happen as the start button should be inactive
            if gglobs.logDBPath == None:
                efprint("WARNING: Cannot log; Logfile is not loaded")
                break

            # Logfile is either read-only, not writeable, or had been removed
            if not os.access(gglobs.logDBPath, os.W_OK):
                efprint("WARNING: Cannot log; Logfile is not available for writing!")
                break

            # No loggable variables
            if gglobs.activeVariables == 0:
                efprint("WARNING: No variables for logging available; Logging is not possible!")
                qefprint("Please check configuration if this is unexpected !")
                break

            # all clear, go for it
            gglobs.logging       = True          # set early, to allow threads to get data
            gglobs.LogReadings   = 0
            gglobs.currentDBPath = gglobs.logDBPath

            # make output like:
            #~#DEVICES, 2021-02-04 11:48:35, Connected: GMC         : CPM CPS
            #~#DEVICES, 2021-02-04 11:48:35, Connected: Audio       : CPM3rd CPS3rd
            #~#DEVICES, 2021-02-04 11:48:35, Connected: RadMon      : CPM2nd T P H X
            #~#DEVICES, 2021-02-04 11:48:35, Connected: AmbioMon    : CPM CPS CPM1st CPS1st CPM2nd CPS2nd CPM3rd CPS3rd T P H X
            #~#DEVICES, 2021-02-04 11:48:35, Connected: Gamma-Scout : CPM2nd
            #~#DEVICES, 2021-02-04 11:48:35, Connected: LabJack     : T H X
            #~#DEVICES, 2021-02-04 11:48:35, Connected: Simul       : CPM CPS CPM1st CPS1st CPM2nd CPS2nd CPM3rd CPS3rd T H X
            #~#DEVICES, 2021-02-04 11:48:35, Connected: MiniMon     : T H X
            #~#LOGGING, 2021-02-04 11:48:35, Start: Cycle: 1.0 sec
            comments  = []
            printcom  = ""
            for a in gglobs.textDevVars:
                if gglobs.textDevVars[a] != None:
                    cinfo     = "Connected: {:11s} : {}" .format(a, gglobs.textDevVars[a])
                    printcom += "#DEVICES, {}, {}\n"     .format(stime(), cinfo)
                    comments.append(["DEVICES", "NOW", "localtime", cinfo])

            cinfo     = "Start: Cycle: {} sec"   .format(gglobs.logcycle)
            printcom += "#LOGGING, {}, {}"       .format(stime(), cinfo)
            comments.append(["LOGGING", "NOW", "localtime", cinfo])

            logPrint(printcom)
            fprint  (printcom)

            gsup_sql.DB_insertComments(gglobs.logConn, comments)

            cleanupDevices("before")

            # a loaded file may contain variables, which are currently not loggable
            # but should be displayed. Make sure all old and all new vars can be displayed
            for vname in gglobs.varsDefault:
                gglobs.varcheckedLog[vname] = True if    gglobs.varcheckedLog[vname] \
                                                      or gglobs.loggableVars[vname]  \
                                              else False

        # STARTING
            self.timer.start(int(gglobs.logcycle * 1000)) # timer time is in ms; logcycle in sec
            dprint("startLogging: Logging now; Timer is started with cycle {} sec.".format(gglobs.logcycle))

            self.checkLoggingState()
            self.plotGraph("Log")     # initialize graph settings; getLogValues calls makePlot directly
            gsup_tools.getLogValues() # make first call now; timer fires only AFTER 1st period!

            break

        setDebugIndent(0)


    def stopLogging(self):
        """Stops the logging"""

        if not gglobs.logging: return

        fncname = "stopLogging: "
        dprint(fncname)
        setDebugIndent(1)

        fprint(header("Stop Logging"))
        self.timer.stop()
        gglobs.logging = False

        writestring  = "#LOGGING, {}, Stop".format(stime())
        logPrint(writestring)
        fprint(writestring)

        gsup_sql.DB_insertComments(gglobs.logConn, [["LOGGING", "NOW", "localtime", "Stop"]])

        cleanupDevices("after")

        self.checkLoggingState()
        self.labelVar.setStyleSheet('color:darkgray;')
        self.updateDisplayVariableValue()

        dprint(fncname + "Logging is stopped")
        setDebugIndent(0)


    def addComment(self, dataType):
        """Adds a comment to the current log"""

        if dataType == "Log":
            if gglobs.logConn is None:
                self.showStatusMessage("No LogFile available")
                return

        elif dataType == "His":
            if gglobs.hisConn is None:
                self.showStatusMessage("No HisFile available")
                return

        else:
            if gglobs.currentConn is None:
                self.showStatusMessage("No File available")
                return

            elif gglobs.currentConn == gglobs.logConn:  dataType = "Log"
            else:                                       dataType = "His"

        info        = ("Enter your comment to the {} file: " + " "*100).format(dataType)

        d           = QInputDialog()
        dtext, ok   = d.getText(None, 'Add a Comment', info)
        dtext       = str(dtext)

        if ok:
            ctype       = "COMMENT"
            cJulianday  = "NOW"
            cinfo       = dtext
            if dataType == "Log":
                fprint(header("Add Comment to Log"))
                logPrint("#COMMENT, {}, {}".format(stime(), dtext)) # to the LogPad
                fprint("#COMMENT, {}, {}".format(stime(), dtext))   # to the NotePad
                gsup_sql.DB_insertComments(gglobs.logConn, [[ctype, cJulianday, "localtime", cinfo]]) # to the DB

            else: # dataType == "His"
                fprint(header("Add Comment to History"))
                fprint("#COMMENT, {}, {}".format(stime(), dtext))   # to the NotePad
                cJulianday  = None
                gsup_sql.DB_insertComments(gglobs.hisConn, [[ctype, cJulianday, "localtime", cinfo]]) # to the db

        vprint("Add a Comment: text='{}', ok={}".format(dtext,ok))


    def addError(self, errtext):
        """Adds ERROR info from gdev_gmc as comment to the current log"""

        logPrint("#COMMENT, {}, {}".format(stime(), errtext))   # to the LogPad

        if not gglobs.logConn is None:                          # to the DB
            gsup_sql.DB_insertComments(gglobs.logConn, [["DevERROR", "NOW", "localtime", errtext]])


#
# Update the display
#
    def showTimingSetting(self, logcycle):
        """update the Timings shown under Data"""

        self.dcycl.setText("Cycle: {:0.3g} s".format(logcycle))


    def updateDisplayVariableValue(self):
        """update the variable value displayed in the Graph area"""

        #print("-------------updateDisplayVariableValue: ")

        if gglobs.lastValues == None:
            self.labelVar.setText(" --- ")
            self.labelVar.setToolTip("Shows Last Values when logging")
            self.labelVar.setStatusTip("Shows Last Values when logging")
            return

        # updates the variables shown in the DisplayVariables Window
        try:
            for i, vname in enumerate(gglobs.varsBook):
                if self.vlabels[i] is None: continue

                if not gglobs.varcheckedLog[vname]:
                    val = "{:>18s}".format("not mapped")
                else:
                    #if not np.isnan(gglobs.lastValues[vname][0]):
                    if not np.isnan(gglobs.lastValues[vname]):
                        #val = "{:>8.2f}".format(gglobs.lastValues[vname][0])
                        val = "{:>10.2f}".format(gglobs.lastValues[vname])
                    else:
                        val = "{:>10s}".format("  --- ")
                self.vlabels[i].setText(val)

                if gglobs.logging and gglobs.varcheckedLog[vname]:
                    self.vlabels[i].setStyleSheet("QLabel { background-color : #F4D345; color : black; }")
                elif not gglobs.logging and gglobs.varcheckedLog[vname]:
                    self.vlabels[i].setStyleSheet("QLabel {color:darkgray; }")
                else:
                    self.vlabels[i].setStyleSheet("QLabel {color:darkgray; font-size:14px;}")

        except Exception as e:
            wprint("------------updateDisplayVariableValue: 1st Exception:", e)
            pass

       # when logging with black on yellow background, else with dark.grey on grey
        if gglobs.logging and gglobs.activeDataSource == "Log":
            self.labelVar.setStyleSheet('color: black; background-color: #F4D345;')

        elif gglobs.activeDataSource == "His":
            self.labelVar.setText(" --- ")
            self.labelVar.setToolTip("Shows Last Values when logging")
            self.labelVar.setStatusTip("Shows Last Values when logging")
            self.labelVar.setStyleSheet('color:darkgray;')
            return

        selVar    = self.select.currentText()         # selected variable
        selUnit1  = self.yunit .currentText()
        selUnit2  = self.y2unit.currentText()
        varText   = " --- "
        statusTip = ""

        if gglobs.calibration1st == "auto":  scale1st = 1 / gglobs.DefaultSens1st
        else:                                scale1st = 1 / gglobs.calibration1st

        if gglobs.calibration2nd == "auto":  scale2nd = 1 / gglobs.DefaultSens2nd
        else:                                scale2nd = 1 / gglobs.calibration2nd

        if gglobs.calibration3rd == "auto":  scale3rd = 1 / gglobs.DefaultSens3rd
        else:                                scale3rd = 1 / gglobs.calibration3rd

        #~print("scale1st:", scale1st)
        #~print("scale2nd:", scale2nd)
        #~print("scale3rd:", scale3rd)

        while True:

            if   selVar == "CPM":
                value    = gglobs.lastValues["CPM"]
                if np.isnan(value):   break

                if selUnit1 == "CPM":
                    varText ="{:0.0f} CPM".format(value)
                else:
                    varText = "{:0.2f} µSv/h".format(value * scale1st)

                statusTip  = "{:0.2f} CPM"     .format(value)
                statusTip += " = {:0.2f} CPS"  .format(value / 60)
                statusTip += " = {:0.2f} µSv/h".format(value * scale1st)
                statusTip += " = {:0.2f} mSv/a".format(value * scale1st / 1000 * 24 * 365.25)

            elif selVar == "CPS":
                value    = gglobs.lastValues["CPS"]
                if np.isnan(value):   break

                if selUnit1 == "CPM":
                    varText = "{:0.0f} CPS".format(value)
                else:
                    varText = "{:0.2f} µSv/h".format(value * 60 * scale1st)

                statusTip  = "{:0.2f} CPS"     .format(value)
                statusTip += " = {:0.2f} CPM"  .format(value * 60)
                statusTip += " = {:0.2f} µSv/h".format(value * 60 * scale1st)
                statusTip += " = {:0.2f} mSv/a".format(value * 60 * scale1st / 1000 * 24 * 365.25)



            elif selVar == "CPM1st":
                value    = gglobs.lastValues["CPM1st"]
                if np.isnan(value):   break

                if selUnit1 == "CPM":
                    varText = "{:0.0f} CPM".format(value)
                else:
                    varText = "{:0.2f} µSv/h".format(value * scale1st)

                statusTip  = "{:0.2f} CPM"     .format(value)
                statusTip += " = {:0.2f} CPS"  .format(value / 60)
                statusTip += " = {:0.2f} µSv/h".format(value * scale1st)
                statusTip += " = {:0.2f} mSv/a".format(value * scale1st / 1000 * 24 * 365.25)

            elif selVar == "CPS1st":
                value    = gglobs.lastValues["CPS1st"]
                if np.isnan(value):   break

                if selUnit1 == "CPM":
                    varText = "{:0.0f} CPS".format(value)
                else:
                    varText = "{:0.2f} µSv/h".format(value * scale1st)

                statusTip  = "{:0.2f} CPS"     .format(value)
                statusTip += " = {:0.2f} CPM"  .format(value * 60)
                statusTip += " = {:0.2f} µSv/h".format(value * 60 * scale1st)
                statusTip += " = {:0.2f} mSv/a".format(value * 60 * scale1st / 1000 * 24 * 365.25)



            elif selVar == "CPM2nd":
                value    = gglobs.lastValues["CPM2nd"]
                if np.isnan(value):   break

                if selUnit1 == "CPM":
                    varText = "{:0.0f} CPM".format(value)
                else:
                    varText = "{:0.2f} µSv/h".format(value * scale2nd)

                statusTip  = "{:0.2f} CPM"     .format(value)
                statusTip += " = {:0.2f} CPS"  .format(value / 60)
                statusTip += " = {:0.2f} µSv/h".format(value * scale2nd)
                statusTip += " = {:0.2f} mSv/a".format(value * scale2nd / 1000 * 24 * 365.25)


            elif selVar == "CPS2nd":
                value    = gglobs.lastValues["CPS2nd"]
                if np.isnan(value):   break

                if selUnit1 == "CPM":
                    varText = "{:0.0f} CPM".format(value)
                else:
                    varText = "{:0.2f} µSv/h".format(value * scale2nd)

                statusTip  = "{:0.2f} CPS"     .format(value)
                statusTip += " = {:0.2f} CPM"  .format(value * 60)
                statusTip += " = {:0.2f} µSv/h".format(value * 60 * scale2nd)
                statusTip += " = {:0.2f} mSv/a".format(value * 60 * scale2nd / 1000 * 24 * 365.25)



            elif selVar == "CPM3rd":
                value    = gglobs.lastValues["CPM3rd"]
                if np.isnan(value):   break

                if selUnit1 == "CPM":
                    varText = "{:0.0f} CPM".format(value)
                else:
                    varText = "{:0.2f} µSv/h".format(value * scale2nd)

                statusTip  = "{:0.2f} CPM"     .format(value)
                statusTip += " = {:0.2f} CPS"  .format(value / 60)
                statusTip += " = {:0.2f} µSv/h".format(value * scale2nd)
                statusTip += " = {:0.2f} mSv/a".format(value * scale2nd / 1000 * 24 * 365.25)

            elif selVar == "CPS3rd":
                value    = gglobs.lastValues["CPS3rd"]
                if np.isnan(value):   break

                if selUnit1 == "CPM":
                    varText = "{:0.0f} CPM".format(value)
                else:
                    varText = "{:0.2f} µSv/h".format(value * scale2nd)

                statusTip  = "{:0.2f} CPS"     .format(value)
                statusTip += " = {:0.2f} CPM"  .format(value * 60)
                statusTip += " = {:0.2f} µSv/h".format(value * 60 * scale2nd)
                statusTip += " = {:0.2f} mSv/a".format(value * 60 * scale2nd / 1000 * 24 * 365.25)


            elif selVar == "Temperature":
                value    = gglobs.lastValues["T"]
                if np.isnan(value):   break

                if selUnit2 == "°C":
                    varText = "{:0.2f} °C".format(value)
                else:
                    varText = "{:0.2f} °F".format(value / 5 * 9 + 32)

                statusTip  = "{:0.2f} °C"     .format(value)
                statusTip += " = {:0.2f} °F"  .format(value / 5 * 9 + 32)

            elif selVar == "Pressure":
                value    = gglobs.lastValues["P"]
                if np.isnan(value):   break

                varText = "{:0.2f} hPa".format(value)

                statusTip  = "{:0.2f} hPa"      .format(value)
                statusTip += " = {:0.2f} mbar"  .format(value)

            elif selVar == "Humidity":
                value       = gglobs.lastValues["H"]
                if np.isnan(value):   break
                varText    = "{:0.2f} %".format(value)
                statusTip  = "{:0.2f} %".format(value)

            elif selVar == "Xtra":
                value    = gglobs.lastValues["X"]
                if np.isnan(value):   break

                varText    = "{:0.2f}".format(value)
                statusTip  = "{:0.2f}".format(value)

            break

        self.labelVar.setText(varText)
        self.labelVar.setToolTip(statusTip)
        self.labelVar.setStatusTip(statusTip)


#
# Get Log file
#
    def quickLog(self):
        """Starts logging with empty default log file 'default.log'"""

        fprint(header("Quick Log"))
        fprint("Start logging using Quick Log database 'default.logdb'")
        dprint("quickLog: using Quick Log database 'default.logdb'")
        setDebugIndent(1)

        gglobs.logDBPath   = os.path.join(gglobs.dataPath, "default.logdb")

        gsup_sql.DB_deleteDatabase("Log", gglobs.logDBPath)

        self.getLogFile(defaultLogDBPath = gglobs.logDBPath) # get default.logdb

        self.startLogging()

        setDebugIndent(0)


    def getLogFile(self, defaultLogDBPath = False, source="Database"):
        """Load existing file for logging, or create new one.
        source can be:
        - "Database" (which is *.logdb file )
        - "CSV File" (which is *.log or *.csv file)
        """

        #
        # Get logfile filename/path
        #
        # A default logfile is given; use it
        if defaultLogDBPath != False:
            gglobs.logFilePath      = None
            gglobs.logDBPath        = defaultLogDBPath
            #dprint("getLogFile: using defaultLogDBPath: ", gglobs.logDBPath)

        # A default logfile is NOT given; run dialog to get one
        else:
            if   source == "Database":
                # may use existing or new .logdb file, but must be allowed to overwrite this file
                # an existing logdb file will be appended with new data
                dlg=QFileDialog(caption= "Get LogFile - Enter New Filename or Select from Existing", options=QFileDialog.DontUseNativeDialog)
                dlg.setFileMode(QFileDialog.AnyFile)

                dlg.setNameFilter("Logging Files (*.logdb)")

            elif source == "CSV File":
                # there must be an existing, readable '*.log' or '*.csv' file
                # and it must be allowed to write .hisdb files
                # the log/csv file will remain unchanged

                dlg=QFileDialog(caption = "Get LogFile from Existing File", options=QFileDialog.DontUseNativeDialog)
                dlg.setFileMode(QFileDialog.ExistingFile)
                dlg.setNameFilter("Logging Files (*.log *.his *.csv *.txt *.notes)")

            else:
                dprint("getLogFile: Programming ERROR: undefined source:", source)
                sys.exit(1)

            dlg.setViewMode(QFileDialog.Detail)
            dlg.setWindowIcon(self.iconGeigerLog)
            dlg.setDirectory(gglobs.fileDialogDir)

            dlg.setFixedSize(950, 550)

            # Execute dialog
            if dlg.exec_() == QDialog.Accepted:  pass     # QDialog Accepted
            else:                                return   # QDialog Rejected
    ### end filedialog -  a file was selected

            gglobs.fileDialogDir = dlg.directory().path()
            #print("dlg.directory().path():", dlg.directory().path())

            fnames  = dlg.selectedFiles()
            fname   = str(fnames[0])                    # file path
            fext    = os.path.splitext(fname)[1]        # file extension
            fname_base  = os.path.splitext(fname)[0]    # file basename with path w/o ext

            if   source == "Database":  # extension is .logdb
                gglobs.logFilePath = None
                if fext != ".logdb":
                    gglobs.logDBPath   = fname + ".logdb" # file has any extension or none
                else:
                    gglobs.logDBPath   = fname            # file already has .hisdb extension

            elif source == "CSV File":  # extension is .log
                gglobs.logFilePath = fname
                gglobs.logDBPath   = fname_base + ".logdb"
                if not isFileReadable (gglobs.logFilePath):   return

            if source == "Database":
                if os.path.isfile(gglobs.logDBPath):
                    msg = QMessageBox()
                    msg.setIcon(QMessageBox.Warning)
                    msg.setWindowTitle("CAUTION")
                    critical  = """You selected an existing file, which will be modified \
        when logging by <b>APPENDING</b> new data to it. Please confirm with OK.
        <br><br>Otherwise click Cancel and enter a new filename in the Get Log File dialog."""
                    msg.setText(critical)
                    msg.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
                    msg.setDefaultButton(QMessageBox.Cancel)

                    msg.setEscapeButton(QMessageBox.Cancel)
                    retval = msg.exec_()

                    if retval != 1024:
                        return

        # Done getting LogFile   ##############################################

        self.setBusyCursor()

        gglobs.currentDBPath   = gglobs.logDBPath

        fprint(header("Get Log"))
        fprint("Log database: {}".                               format(gglobs.logDBPath))
        if defaultLogDBPath == False:
            dprint("getLogFile: use selected Log DB file: '{}'". format(gglobs.logDBPath))
        else:
            dprint("getLogFile: use default Log DB file: '{}'".  format(defaultLogDBPath))
        setDebugIndent(1)

        #dprint("getLogFile: gglobs.logFilePath:     ", gglobs.logFilePath)
        #dprint("getLogFile: gglobs.logDBPath:       ", gglobs.logDBPath)
        #dprint("getLogFile: gglobs.currentDBPath:   ", gglobs.currentDBPath)

        if gglobs.logging:   self.stopLogging()
        self.dcfLog.setText(gglobs.logDBPath)
        self.clearLogPad()

        # an existing classic log was selected. It will be converted to a database;
        # any previous conversion will be deleted first
        if gglobs.logFilePath != None:
            fprint("Created from file {}".format(gglobs.logFilePath))
            # delete old database
            #~gsup_sql.DB_deleteDatabase(gglobs.logConn, gglobs.logDBPath)
            gsup_sql.DB_deleteDatabase("Log", gglobs.logDBPath)

            # open new database
            gglobs.logConn      = gsup_sql.DB_openDatabase(gglobs.logConn, gglobs.logDBPath)

            # read data from CSV file into database
            self.setNormalCursor()

            if gsup_sql.getCSV(gglobs.logFilePath):
                self.setBusyCursor()
                gsup_sql.DB_convertCSVtoDB(gglobs.logConn, gglobs.logFilePath)
            else:
                efprint("Database creation was cancelled")
                return


        # a database file was selected
        else:
            # Database File does NOT exist; create new one
            if not os.path.isfile(gglobs.logDBPath):
                fprint("LogFile newly created - available for writing")

                linfo = "LogFile newly created as '{}'".format(os.path.basename(gglobs.logDBPath))
                logPrint("#HEADER , {}, ".format(stime()) + linfo)

                # open new database
                gglobs.logConn      = gsup_sql.DB_openDatabase(gglobs.logConn, gglobs.logDBPath)

                ctype       = "HEADER"
                cJulianday  = 'NOW'
                cinfo       = linfo
                gsup_sql.DB_insertComments(gglobs.logConn, [[ctype, cJulianday, "localtime", cinfo]])

                # data array for the variables
                gglobs.logDBData = np.empty([0, gglobs.datacolsDefault])

            # Database File does exist
            else:
                # Database File does exist and can read and write
                if os.access(gglobs.logDBPath, os.W_OK):
                    fprint("LogFile opened - available for writing")

                # DB File does exist but can read only
                elif os.access(gglobs.logDBPath, os.R_OK):
                    efprint("LogFile opened - WARNING: available ONLY FOR READING")

                gglobs.logConn    = gsup_sql.DB_openDatabase  (gglobs.logConn, gglobs.logDBPath)

        gglobs.logDBData, gglobs.varcheckedLog = gsup_sql.getDataFromDatabase()
        gglobs.lastValues                      = None


        # add the default logcycle as read from the database
        testcycle = gsup_sql.DB_readLogcycle(gglobs.logConn)    # testcycle is type float
        #print("testcycle:",testcycle, type(testcycle))
        if testcycle is None:       # old DB, may not have one
            gsup_sql.DB_insertLogcycle(gglobs.logConn, gglobs.logcycle)
        else:
            gglobs.logcycle = testcycle
            self.showTimingSetting(gglobs.logcycle)

        self.plotGraph("Log")
        self.checkLoggingState()
        QApplication.processEvents() # to make Normal Cursor appear only after graph shown
        self.setNormalCursor()

        setDebugIndent(0)


#
# Show data from Log, His, and Bin files ######################################
#
    def showData(self, dataSource=None, full=True):
        """Print Log or His Data to notepad, as full file or excerpt.
        dataSource can be 'Log' or 'His' or 'HisBin' (for binary data) or
        HisParse or PlotData"""

        #print("showData start, full: ", dataSource, full)

        if gglobs.activeDataSource == None:
            self.showStatusMessage("No data available")
            return

        textprintButtonOff = "DataExcerpt"
        textprintButtonOn  = "STOP"

        # stop printing
        if self.printbutton.text() == textprintButtonOn:
            gglobs.stopPrinting = True
            return

        # switch button mode to "STOP"
        self.printbutton.setStyleSheet('QPushButton {color: blue; background-color:white; font:bold;}')
        self.printbutton.setText(textprintButtonOn)

        if dataSource == None:
            if    gglobs.activeDataSource == "Log": dataSource = "Log"
            else:                                   dataSource = "His"

        if   dataSource == "Log":                   self.showLogData(full=full)
        elif dataSource == "His":                   self.showHisData(full=full)
        elif dataSource == "HisBin":                gsup_sql.createLstFromDB(full=full)
        elif dataSource == "HisParse":              gsup_sql.createParseFromDB(full=full)
        elif dataSource == "PlotData":              gsup_tools.printPlotData()              # to plot data as shown in plot

        # reset button mode to "DataExcerpt"
        self.printbutton.setStyleSheet('QPushButton {}')
        self.printbutton.setText(textprintButtonOff)


    def showLogData(self, full=True):
        """ print logged data to notepad"""

        if gglobs.logConn == None:
            self.showStatusMessage("No data available")
            return

        self.setBusyCursor()

        if full:    addp = ""
        else:       addp = " Excerpt"
        fprint(header("Show Log Data" + addp))
        fprint("from: {}\n".format(gglobs.logDBPath))

        sql, ruler = gsup_sql.getShowCompactDataSql(gglobs.varcheckedLog)

        fprint(ruler)

        if full:
            data = gsup_sql.DB_readData(gglobs.logConn, sql, limit=0)
            #print("showLogData data:", data)

            counter     = 0
            batch       = 50
            printstring = ""
            gglobs.stopPrinting = False
            for a in data:
                #print("showLogData a: ", a)
                if counter == batch:
                    fprint(printstring[:-1])
                    fprint(ruler)
                    printstring = ""
                    counter     = 0
                printstring += a + "\n"
                counter     += 1
                if gglobs.stopPrinting: break
            gglobs.stopPrinting = False
            fprint(printstring[:-1])
        else:
            fprint(self.getExcerptLines(sql, gglobs.logConn))

        fprint(ruler)

        self.setNormalCursor()


    def showLogTags(self):
        """print comments only from log data"""

        if gglobs.logConn == None:
            self.showStatusMessage("No data available")
            return

        self.setBusyCursor()

        fprint(header("Show Log Tags and Comments"))
        fprint("from: {}\n".format(gglobs.logDBPath))

        rows = gsup_sql.DB_readComments(gglobs.logConn)
        fprint("\n".join(rows))

        self.setNormalCursor()


    def showHisData(self, full=True):
        """print HIST parsed data"""

        if gglobs.hisConn == None:
            self.showStatusMessage("No data available")
            return

        self.setBusyCursor()

        if full:
            addp = ""
        else:
            addp = " Excerpt"
        fprint(header("Show History Data" + addp))
        fprint("from: {}\n".format(gglobs.hisDBPath))

        #print("showHisData: varcheckedHis: ", gglobs.varcheckedHis)
        sql, ruler = gsup_sql.getShowCompactDataSql(gglobs.varcheckedHis)

        fprint(ruler)

        if full:
            data = gsup_sql.DB_readData(gglobs.hisConn, sql, limit=0)
            #print("showHisData data:", data)
            counter     = 0
            batch       = 50
            printstring = ""
            gglobs.stopPrinting = False
            for a in data:
                #print("showHisData a:", a)
                if counter == batch:
                    fprint(printstring[:-1])
                    printstring = ""
                    counter     = 0
                    fprint(ruler)
                printstring += a + "\n"
                counter     += 1
                if gglobs.stopPrinting: break
            gglobs.stopPrinting = False
            fprint(printstring[:-1])
        else:
            fprint(self.getExcerptLines(sql, gglobs.hisConn))

        fprint(ruler)

        self.setNormalCursor()


    def showHisTags(self):
        """print comments only from his data"""

        if gglobs.hisConn == None:
            self.showStatusMessage("No data available")
            return

        self.setBusyCursor()

        fprint(header("Show History Tags and Comments"))
        fprint("from: {}\n".format(gglobs.hisDBPath))

        rows = gsup_sql.DB_readComments(gglobs.hisConn)
        fprint("\n".join(rows))

        self.setNormalCursor()


    def getExcerptLines(self, sql, DB_Conn, lmax=12):
        """get first and last lines from the db"""

        if DB_Conn == None:  return ""

        #start=time.time()

        excLines  = gsup_sql.DB_readData(DB_Conn, sql, limit=lmax)
        lenall    = len(excLines)
        if lenall == 0:      return ""      # no data

        plines = ""
        if lenall < lmax * 2:
            for i in range(0, int(lenall/2)):   plines += excLines[i] + "\n"

        else:
            for a in excLines[0:lmax]:          plines += a + "\n"
            plines +=                                     "     ...\n"
            for a in excLines[-lmax:]:          plines += a + "\n"

        #print("new getExcerptLines:", (time.time()-start)*1000)

        return plines[:-1] # remove "\n"


# printing to hardware printer or pdf file
    def printNotePad(self):
        """prints NotePad content to printer or pdf"""

        if gglobs.currentDBPath is None:
            self.showStatusMessage("No data available")
            return

        defaultPDF = gglobs.currentDBPath + '.pdf'
        vprint("printNotePad: default pdf file:", defaultPDF)

        mydoc = self.notePad.document()

        myprinter = QPrinter()
        wprint("printNotePad: default printer:          ", myprinter.printerName()) # default: HP-OfficeJet-Pro-8730-2
        #myprinter.setPrinterSelectionOption("pdf")
        #wprint("printNotePad: printerSelectionOption(): ", myprinter.printerSelectionOption() )
        myprinter.setOutputFormat(QPrinter.PdfFormat)
        myprinter.setOutputFileName(defaultPDF)
        #myprinter.setResolution(96)
        #myprinter.setPrinterName("Print to File (PDF)")

        dialog = QPrintDialog(myprinter, self)
        dialog.setOption(QAbstractPrintDialog.PrintToFile, on=True)
        if dialog.exec():  mydoc.print(dialog.printer())


    def setTubeSensitivities(self):
        """Set tube sensitivities for all tubes temporarily"""

        #
        # setting the scaling factor (needed if no device connected)
        #
        if gglobs.calibration1st == "auto":    scale1st = gglobs.DefaultSens1st
        else:                                  scale1st = gglobs.calibration1st

        if gglobs.calibration2nd == "auto":    scale2nd = gglobs.DefaultSens2nd
        else:                                  scale2nd = gglobs.calibration2nd

        if gglobs.calibration3rd == "auto":    scale3rd = gglobs.DefaultSens3rd
        else:                                  scale3rd = gglobs.calibration3rd

        dprint("setTubeSensitivities:")
        setDebugIndent(1)

        # Comment
        c = """Allows to set the sensitivities for all tubes
temporarily for this program run.

For a permanent change edit the GeigerLog
configuration file geigerlog.cfg.\n
Sensititivities are in units of CPM/(µSv/h).\n"""
        lcomment        = QLabel(c)

    # 1st tube
        ltube1st = QLabel("1st tube  ")
        ltube1st.setAlignment(Qt.AlignLeft | Qt.AlignCenter)

        etube1st = QLineEdit()
        etube1st.setToolTip('Code: M1')
        etube1st.setText("{:0.6g}".format(scale1st))

    # 2nd tube
        ltube2nd = QLabel("2nd tube  ")
        ltube2nd.setAlignment(Qt.AlignLeft | Qt.AlignCenter)

        etube2nd = QLineEdit()
        etube2nd.setToolTip('Code: M2')
        etube2nd.setText("{:0.6g}".format(scale2nd))

    # 3rd tube
        ltube3rd = QLabel("3rd tube  ")
        ltube3rd.setAlignment(Qt.AlignLeft | Qt.AlignCenter)

        etube3rd = QLineEdit()
        etube3rd.setToolTip('Code: M3')
        etube3rd.setText("{:0.6g}".format(scale3rd))

        graphOptions=QGridLayout()
        graphOptions.addWidget(lcomment,    0, 0, 1, 2) # from 0,0 over 1 row and 2 cols
        graphOptions.addWidget(ltube1st,    1, 0)
        graphOptions.addWidget(etube1st,    1, 1)
        graphOptions.addWidget(ltube2nd,    2, 0)
        graphOptions.addWidget(etube2nd,    2, 1)
        graphOptions.addWidget(ltube3rd,    3, 0)
        graphOptions.addWidget(etube3rd,    3, 1)

    # Dialog box
        d = QDialog() # set parent empty to popup in center of screen
        d.setWindowIcon(self.iconGeigerLog)
        d.setFont(self.fontstd)
        d.setWindowTitle("Set Temporary Sensitivities")

        #d.setWindowModality(Qt.ApplicationModal)   #all of them block other actions???
        #d.setWindowModality(Qt.NonModal)
        #d.setWindowModality(Qt.WindowModal)

    # Buttons
        self.bbox = QDialogButtonBox()
        self.bbox.setStandardButtons(QDialogButtonBox.Cancel | QDialogButtonBox.Ok)
        self.bbox.accepted.connect(lambda: d.done(0))
        self.bbox.rejected.connect(lambda: d.done(99))

        layoutV = QVBoxLayout(d)
        layoutV.addLayout(graphOptions)
        layoutV.addWidget(self.bbox)
        layoutV.addStretch()

        retval = d.exec()
        #print("reval:", retval)
        if retval == 99:
            # CANCEL
            dprint("setTubeSensitivities: CANCEL clicked, Sensitivities unchanged")

        else:
            # OK
            fprint(header("Set Sensitivities"))
            try:        ftube1st = float(etube1st.text().replace(",", "."))
            except:     ftube1st = 0
            try:        ftube2nd = float(etube2nd.text().replace(",", "."))
            except:     ftube2nd = 0
            try:        ftube3rd = float(etube3rd.text().replace(",", "."))
            except:     ftube3rd = 0

            if ftube1st > 0:     gglobs.calibration1st = ftube1st
            else:                efprint("1st tube: Illegal Value, >0 required, you entered: ", etube1st.text())

            if ftube2nd > 0:     gglobs.calibration2nd = ftube2nd
            else:                efprint("2nd tube: Illegal Value, >0 required, you entered: ", etube2nd.text())

            if ftube3rd > 0:     gglobs.calibration3rd = ftube3rd
            else:                efprint("3rd tube: Illegal Value, >0 required, you entered: ", etube3rd.text())

            fprint("1st tube:", "{}" .format(gglobs.calibration1st), debug = True)
            fprint("2nd tube:", "{}" .format(gglobs.calibration2nd), debug = True)
            fprint("3rd tube:", "{}" .format(gglobs.calibration3rd), debug = True)

            gsup_plot.makePlot()

        setDebugIndent(0)


    def showDeviceMappings(self):
        """Shows active devices and variables mapped to them and alerts on
        variables being mapped to more than one device"""

        fncname = "showDeviceMappings: "

        fprint(header("Device Mappings"))

        if gglobs.DevicesConnected == 0:
            fprint("Unknown until a connection is made. Use menu: Device -> Connect Devices")
            return

        fprint("The configuration is determined in the configuration file geigerlog.cfg")

        mapflag = False
        for vname in gglobs.varsDefault:
            if gglobs.varMap[vname] > 1:
                if mapflag == False:    # print only on first occurence
                    efprint("WARNING: Mapping problem of Variables")
                qefprint("Variable {}".format(vname), "is mapped to more than one device")
                mapflag = True

        dline = "{:12s}:  {:6s} {:6s} {:6s} {:6s} {:6s} {:6s} {:6s} {:6s}   {:3s} {:3s} {:3s} {:3s}"
        fprint("\n" + dline.format("Device", *list(gglobs.varsBook)))
        fprint("-" * 86)
        for devname in gglobs.Devices:
            #print(fncname + "devname: ", devname)
            #print(fncname + "gglobs.Devices[devname][1]: ", gglobs.Devices[devname][1])
            #print(fncname + "gglobs.Devices[devname][2]: ", gglobs.Devices[devname][2])
            checks = []
            if gglobs.Devices[devname][2]:
                checks.append(devname)
                for vname in gglobs.varsDefault:
                    try:
                        if vname in gglobs.Devices[devname][1]: checks.append("X")
                        else:                                   checks.append("-")
                    except:
                        checks.append("-")
                fprint(dline.format(*checks))

        if mapflag:
            qefprint("Measurements are made on devices from top to bottom, and for each according to configuration.")
            qefprint("If double-mapping of variables occurs, then the last measured variable will overwrite the")
            qefprint("previous one, almost always resulting in useless data.")
            playWav("error")
        else:
            fprint("Mapping is valid")
            playWav("ok")


    def toggleDeviceConnection(self):
        """if no connection exists, then make connection else disconnect"""

        if gglobs.logging:
            self.showStatusMessage("Cannot change when logging! Stop logging first")
            return

        if gglobs.DevicesConnected == 0:    self.switchConnections(new_connection="ON")
        else:                               self.switchConnections(new_connection="OFF")


    def switchConnections(self, new_connection="ON"):
        """
        if new_connection = ON:
            if no connection exists, then try to make connection (with verification
            of communication with device)
        if new_connection = OFF:
            if connection does exist, then disconnect
        """

        if gglobs.logging:
            self.showStatusMessage("Cannot change when logging! Stop logging first")
            return

        fncname = "switchConnections: "
        self.setBusyCursor()
        dprint(fncname + "--> {}. ".format(new_connection))
        setDebugIndent(1)

        # make all connections or disconnections if activated
        self.switchGMC_Connection       (new_connection=new_connection)    # GMC
        self.switchAudio_Connection     (new_connection=new_connection)    # Audio
        self.switchRM_Connection        (new_connection=new_connection)    # RadMon
        self.switchAmbio_Connection     (new_connection=new_connection)    # AmbioMon
        self.switchGS_Connection        (new_connection=new_connection)    # Gamma-Scout
        self.switchI2C_Connection       (new_connection=new_connection)    # I2C
        self.switchLJ_Connection        (new_connection=new_connection)    # LabJack
        self.switchRaspi_Connection     (new_connection=new_connection)    # Raspi
        self.switchSimul_Connection     (new_connection=new_connection)    # Simul
        self.switchMiniMon_Connection   (new_connection=new_connection)    # MiniMon

        # count the connected (not just activated!) devices;
        # after disconnections, all should be false
        gglobs.DevicesConnected = 0
        if gglobs.GMCConnection     :      gglobs.DevicesConnected += 1
        if gglobs.AudioConnection   :      gglobs.DevicesConnected += 1
        if gglobs.RMConnection      :      gglobs.DevicesConnected += 1
        if gglobs.AmbioConnection   :      gglobs.DevicesConnected += 1
        if gglobs.GSConnection      :      gglobs.DevicesConnected += 1
        if gglobs.I2CConnection     :      gglobs.DevicesConnected += 1
        if gglobs.LJConnection      :      gglobs.DevicesConnected += 1
        if gglobs.RaspiConnection   :      gglobs.DevicesConnected += 1
        if gglobs.SimulConnection   :      gglobs.DevicesConnected += 1
        if gglobs.MiniMonConnection :      gglobs.DevicesConnected += 1

        if gglobs.DevicesConnected > 0: # at least 1 is needed to show a closed (=green) plug
            self.toggleDeviceConnectionAction.setIcon(QIcon(QPixmap(os.path.join(gglobs.gresPath, 'icon_plug_closed.png')))) # green icon
        else:
            self.toggleDeviceConnectionAction.setIcon(QIcon(QPixmap(os.path.join(gglobs.gresPath, 'icon_plug_open.png'))))   # red icon
            #qefprint("<br>WARNING: No devices are connected")
            self.fprintWarningMessage("<br>WARNING: No devices are connected")

        wprint(fncname, "Connection Status: " )
        wprint("- gglobs.GMCConnection:     ", gglobs.GMCConnection)
        wprint("- gglobs.AudioConnection:   ", gglobs.AudioConnection)
        wprint("- gglobs.RMConnection:      ", gglobs.RMConnection)
        wprint("- gglobs.AmbioConnection:   ", gglobs.AmbioConnection)
        wprint("- gglobs.GSConnection:      ", gglobs.GSConnection)
        wprint("- gglobs.I2CConnection      ", gglobs.I2CConnection)
        wprint("- gglobs.LJConnection:      ", gglobs.LJConnection)
        wprint("- gglobs.RaspiConnection:   ", gglobs.RaspiConnection)
        wprint("- gglobs.SimulConnection:   ", gglobs.SimulConnection)
        wprint("- gglobs.MiniMonConnection: ", gglobs.MiniMonConnection)
        wprint("- gglobs.DevicesConnected:  ", gglobs.DevicesConnected)

        # determine the mapping and active variables
        if new_connection == "ON":
            gglobs.activeVariables = 0
            gglobs.varMap          = {}      # holds the mapping of variables
            gglobs.textDevVars     = {}      # holds the mapping of devices
            for vname in gglobs.varsDefault:  gglobs.varMap[vname] = 0
            for devname in gglobs.Devices:    gglobs.textDevVars[devname] = None

            for devname in gglobs.Devices:
                if gglobs.Devices[devname][1] != None:
                    textDevVars = ""
                    for vname in gglobs.Devices[devname][1]:
                        #print("                  : vname:", vname)
                        gglobs.varMap[vname]        += 1
                        gglobs.activeVariables      += 1
                        textDevVars                 += " {}".format(vname)
                        gglobs.loggableVars[vname]   = True
                    gglobs.textDevVars[devname] = textDevVars.strip()

            #~if gglobs.werbose:
                #~wprint("- activeVariables:         ", gglobs.activeVariables)
                #~wprint("- textDevVars:             ", gglobs.textDevVars)
                #~wprint("- gglobs.loggableVars:     ", getOrderedVars(gglobs.loggableVars))

            if gglobs.activeVariables == 0:
                efprint("<br>WARNING: No variables for logging available; Logging will not be possible!")
                qefprint ("Please check configuration if this is unexpected !")

            self.showDeviceMappings()

        self.checkLoggingState()
        self.notePad.setFocus() # to avoid having any device buttons in blue

        dprint(fncname + "completed:")
        for a in gglobs.textDevVars:
            if gglobs.textDevVars[a] != None: dprint("   {:11s} : {}".format(a, gglobs.textDevVars[a]))

        setDebugIndent(0)
        self.setNormalCursor()


    def switchGMC_Connection(self, new_connection = "ON"):
        """GMC connections"""

        if not gglobs.GMCActivation: return

        fncname = "switchGMC_Connection: "

        dprint(fncname + "--> {}. ".format(new_connection))
        setDebugIndent(1)

        self.setBusyCursor()

        if new_connection == "ON":
            if gglobs.GMCConnection:
                fprint(header("GMC Device"), debug=True)
                fprint("GMC Device is already connected")
            else:
                quickbaudrate = gdev_gmc.quickGMC_PortTest(gglobs.GMCusbport)
                #print("quickbaudrate:", quickbaudrate, type(quickbaudrate))
                #print("gglobs.GMCbaudrate:", gglobs.GMCbaudrate, type(gglobs.GMCbaudrate))
                if quickbaudrate > 0:
                    if int(gglobs.GMCbaudrate) != int(quickbaudrate):
                        efprint(header("GMC Device"))
                        qefprint("The configured baudrate {} does not match the detected baudrate {}.".format(gglobs.GMCbaudrate, quickbaudrate))
                        qefprint("Now switching configuration temporarily to detected baudrate {}.".format(quickbaudrate))
                        qefprint("It is recommended to change the baudrate in the configuration file accordingly")
                        gglobs.GMCbaudrate = quickbaudrate
                else:
                    dprint(fncname + "Failure with quickGMC_PortTest, got quickbaudrate={} ".format(quickbaudrate))

                # try to open the port; this is the ONLY place calling initGMC!
                # on errors gglobs.GMCConnection is false
                # otherwise, device is connected, and communication had been
                # verified with getGMC_VER(), getGMC_DeviceProperties were done,
                # and cfg was loaded
                errmessage = gdev_gmc.initGMC()
                if gglobs.GMCConnection:
                    self.dbtnGMC.setStyleSheet(self.dbtnStyleSheetON)
                    self.setEnableDeviceActions(new_enable = True, device="GMC")
                    self.dbtnGMCPower.setEnabled(True)
                    gdev_gmc.fprintGMC_DeviceInfo()

                    if gglobs.GMCcfg == None or len(gglobs.GMCcfg) != gglobs.GMC_configsize:
                        efprint("Could not read device configuration correctly")
                        efprint("Configuration dependent commands in menu Device are being inactivated!")
                        self.setDisableDeviceActions()

                    self.setGMCPowerIcon()

                else:
                    fprint(header("GMC Device"))
                    efprint ("Failure connecting with device: ", "'{}' with message:<br>{}".format(gglobs.GMCDeviceName, errmessage))
                    qefprint("<br>If you know that a GMC device is connected:<br>\
                            - Run 'Help'->'Show & Select USB Port and Baudrate', identify and select settings<br>\
                            - or: Run 'USB Autodiscovery' from menu Help and check for proper port and baudrate<br>\
                            - Look into topic: 'Help'->'Devices` Firmware Bugs' for bugs and workarounds.")
                    self.dbtnGMC.setText(self.connectTextGMC)
                    self.dbtnGMC.setStyleSheet(self.dbtnStyleSheetError)
                gdev_gmc.getGMC_HistSaveMode()

        else: # new_connection == OFF
            fprint(header("Disconnect GMC Device"))
            if not gglobs.GMCConnection:
                fprint("No connected GMC Device")
                self.dbtnGMC.setStyleSheet(self.dbtnStyleSheetOFF)
            else:
                gdev_gmc.terminateGMC()
                gglobs.GMCcfg = None
                self.setEnableDeviceActions(new_enable = False, device="GMC")
                fprint("Disconnected successfully:", "'{}'".format(gglobs.GMCDeviceDetected), debug=True)

            self.dbtnGMCPower.setEnabled(False)
            self.dbtnGMC.setStyleSheet(self.dbtnStyleSheetOFF)

        setDebugIndent(0)
        self.setNormalCursor()


    def switchAudio_Connection(self, new_connection = "ON"):
        """AudioCounter connections"""

        if not gglobs.AudioActivation:  return

        fncname = "switchAudio_Connection: "

        dprint(fncname + "--> {}. ".format(new_connection))
        setDebugIndent(1)

        self.setBusyCursor()

        if new_connection == "ON":
            errmsg = gdev_audio.initAudioCounter() # so far there is never an error in audio
            if gglobs.AudioConnection:
                # successful connect
                self.dbtnAudio.setStyleSheet(self.dbtnStyleSheetON)
                self.setEnableDeviceActions(new_enable = True, device="Audio")
                gdev_audio.printAudioDevInfo()
                dprint(fncname + "ON: for device: {}".format(gglobs.AudioDeviceName))
                self.AudioInfoActionExt .setEnabled(True)      # enable extended info
                self.AudioPlotAction    .setEnabled(True)      # enable audio plotting
                self.AudioSignalAction  .setEnabled(True)      # enable audio raw signal
                self.AudioEiaAction     .setEnabled(True)      # enable audio eia action

            else:
                # failure in connection
                fprint(header("AudioCounter Device"))
                efprint("Failure to connect with Device:", "'{}'".format(gglobs.AudioDeviceName))
                qefprint(errmsg)
                self.dbtnGMC.setStyleSheet(self.dbtnStyleSheetError)

        else: # new_connection == OFF
            fprint(header("Disconnect AudioCounter Device"))
            if not gglobs.AudioConnection:
                fprint("No connected Audio Device")
                #self.dbtnAudio.setStyleSheet(self.dbtnStyleSheetOFF)
            else:
                gdev_audio.terminateAudioCounter()
                # successful dis-connect
                self.AudioInfoActionExt .setEnabled(False)    # disable extended info
                self.AudioPlotAction    .setEnabled(False)    # disable audio plotting
                self.AudioSignalAction  .setEnabled(False)    # disable audio raw signal
                self.AudioEiaAction     .setEnabled(False)    # disable audio eia action
                fprint("Disconnected successfully:", "'{}'".format(gglobs.AudioDeviceName), debug=True)
                self.setEnableDeviceActions(new_enable = False, device="Audio")

            self.dbtnAudio.setStyleSheet(self.dbtnStyleSheetOFF)

        Qt_update()

        self.setNormalCursor()
        setDebugIndent(0)


    def switchI2C_Connection(self, new_connection = "ON"):
        """I2C connections"""

        if not gglobs.I2CActivation:  return

        fncname = "switchI2C_Connection: "

        dprint(fncname + "--> {}. ".format(new_connection))
        setDebugIndent(1)

        self.setBusyCursor()

        if new_connection == "ON":
            errmsg = gdev_i2c.initI2C()
            if gglobs.I2CConnection:
                # successful connect
                self.dbtnI2C.setStyleSheet(self.dbtnStyleSheetON)
                gdev_i2c.printI2CDevInfo()
                dprint(fncname + "ON: for device: {}".format(gglobs.I2CDeviceName))
                self.I2CInfoActionExt.setEnabled(True)      # enable extended info
                self.I2CResetAction.setEnabled(True)        # enable reset
            else:
                # failure in connection
                fprint(header("I2C Device"))
                efprint("Failure connecting with device: ", "'{}' with message:<br>{}".format(gglobs.I2CDeviceName, errmsg))
                self.dbtnI2C.setStyleSheet(self.dbtnStyleSheetError)

        else: # new_connection == OFF
            fprint(header("Disconnect I2C Device"))
            if gglobs.I2CConnection:
                errmsg = gdev_i2c.terminateI2C()
                if not gglobs.I2CConnection:
                    # successful dis-connect
                    self.I2CInfoActionExt.setEnabled(False)    # disable extended info
                    self.I2CResetAction.setEnabled(False)      # disable reset
                    fprint("Disconnected successfully:", "'{}'".format(gglobs.I2CDeviceName), debug=True)
                else:
                    efprint("Disconnection Error with Device: {} with message:<br>{}".format(gglobs.I2CDeviceName, errmsg))
            else:
                fprint("No connected device")
            self.dbtnI2C.setStyleSheet(self.dbtnStyleSheetOFF)

        Qt_update()

        self.setNormalCursor()
        setDebugIndent(0)


    def switchRM_Connection(self, new_connection = "ON"):
        """RadMon connections"""

        if not gglobs.RMActivation: return

        fncname = "switchRM_Connection: "

        dprint(fncname + "--> {}. ".format(new_connection))
        setDebugIndent(1)

        self.setBusyCursor()

        if new_connection == "ON":
            errmsg = gdev_radmon.initRadMon()
            if gglobs.RMConnection:
                # successful connect
                self.dbtnRM.setStyleSheet(self.dbtnStyleSheetON)
                gdev_radmon.printRMDevInfo()
                dprint(fncname + "ON: for device: {} with message: {}".format("RadMon+", gglobs.RMconnect[1]))
                self.RMInfoActionExt.setEnabled(True)       # enable extended info
            else:
                # failure in connection
                fprint(header("RadMon Device"))
                efprint("Failure connecting with device: '{}' {}".format(gglobs.RMDeviceName, errmsg))
                self.dbtnRM.setStyleSheet(self.dbtnStyleSheetError)

        else: # new_connection == OFF
            fprint(header("Disconnect RadMon Device"))
            if gglobs.RMConnection:
                gdev_radmon.terminateRadMon()
                if not gglobs.RMConnection:
                    # successful dis-connect
                    self.RMInfoActionExt.setEnabled(False)       # disable extended info
                    fprint("Disconnected successfully:", "'{}'".format(gglobs.RMDeviceName), debug=True)
                else:
                    # failure in disconnect
                    fprint("Disconnection Error with Device:", gglobs.RMDeviceName)
                    fprint("", gglobs.RMdisconnect[1])
            else:
                fprint("No connected device")
            self.dbtnRM.setStyleSheet(self.dbtnStyleSheetOFF)

        Qt_update()

        self.setNormalCursor()
        setDebugIndent(0)


    def switchAmbio_Connection(self, new_connection = "ON"):
        """AmbioMon connections"""

        if not gglobs.AmbioActivation: return

        fncname = "switchAmbio_Connection: "

        dprint(fncname + "--> {}. ".format(new_connection))
        setDebugIndent(1)

        self.setBusyCursor()

        if new_connection == "ON":
            errmsg = gdev_ambiomon.initAmbioMon()
            if gglobs.AmbioConnection:
                # successful connect
                self.setEnableDeviceActions(new_enable = True, device="Ambio")
                self.dbtnAmbio.setStyleSheet(self.dbtnStyleSheetON)
                gdev_ambiomon.printAmbioInfo()
                dprint(fncname + "ON: for device: {}".format("AmbioMon"))
                self.AmbioInfoActionExt.setEnabled(True)       # enable extended info
            else:
                # failure in connection
                fprint(header("AmbioMon Device"))
                efprint("Failure connecting with device: '{}' {}".format(gglobs.AmbioDeviceName, errmsg))
                self.dbtnAmbio.setStyleSheet(self.dbtnStyleSheetError)

        else: # new_connection == OFF
            fprint(header("Disconnect AmbioMon Device"))
            if gglobs.AmbioConnection:
                gdev_ambiomon.terminateAmbioMon()
                if not gglobs.AmbioConnection:
                    # successful dis-connect
                    self.setEnableDeviceActions(new_enable = False, device="Ambio")
                    self.AmbioInfoActionExt.setEnabled(False)       # enable extended info
                    fprint("Disconnected successfully:", "'{}'".format(gglobs.AmbioDeviceName), debug=True)
                else:
                    fprint("Disconnection Error with Device:", "AmbioMon+")
            else:
                fprint("No connected device")
            self.dbtnAmbio.setStyleSheet(self.dbtnStyleSheetOFF)

        Qt_update()

        self.setNormalCursor()
        setDebugIndent(0)


    def switchLJ_Connection(self, new_connection = "ON"):
        """LabJack connection"""

        if not gglobs.LJActivation:  return

        fncname = "switchLJ_Connection: "

        dprint(fncname + "--> {}. ".format(new_connection))
        setDebugIndent(1)

        self.setBusyCursor()

        if new_connection == "ON":
            errmsg = gdev_labjack.initLabJack()
            if gglobs.LJConnection:
                # successful connect
                self.dbtnLJ.setStyleSheet(self.dbtnStyleSheetON)
                gdev_labjack.printLJDevInfo()
                dprint(fncname + "ON: for device: {}".format(gglobs.LJDeviceName))
                self.LJInfoActionExt.setEnabled(True)       # enable extended info
            else:
                # failure in connection
                fprint(header("LabJack Device"))
                efprint("Failure connecting with device: '{}' with message:<br>{}".format(gglobs.LJDeviceName, errmsg))
                self.dbtnLJ.setStyleSheet(self.dbtnStyleSheetError)

        else: # new_connection == OFF
            fprint(header("Disconnect LabJack Device"))
            if gglobs.LJConnection:
                gdev_labjack.terminateLabJack()
                if not gglobs.LJConnection:
                    # successful dis-connect
                    fprint("Disconnected successfully:", "'{}'".format(gglobs.LJDeviceName), debug=True)
                else:
                    # failure in dis-connection
                    fprint("Disconnection error with device:", gglobs.LJDeviceName)
            else:
                fprint("No connected device")
            self.dbtnLJ.setStyleSheet(self.dbtnStyleSheetOFF)

        Qt_update()

        self.setNormalCursor()
        setDebugIndent(0)


    def switchGS_Connection(self, new_connection = "ON"):
        """GS connection"""

        if not gglobs.GSActivation:  return

        fncname = "switchGS_Connection: "

        dprint(fncname + "--> {}. ".format(new_connection))
        setDebugIndent(1)

        self.setBusyCursor()

        Qt_update()

        if new_connection == "ON":
            errmsg = gdev_scout.initGammaScout()
            if gglobs.GSConnection:
                # successful connect
                self.setEnableDeviceActions(new_enable = True, device="GS")
                self.dbtnGS.setStyleSheet(self.dbtnStyleSheetON)
                gdev_scout.printGSDevInfo(update = False)
                dprint(fncname + "ON: for device: {}".format(gglobs.GSDeviceDetected))
                self.GSInfoActionExt.setEnabled(True)       # enable extended info
                self.GSResetAction.setEnabled(True)         # enable reset
                self.GSSetPCModeAction.setEnabled(True)     # enable PC Mode
                self.GSDateTimeAction.setEnabled(True)      # enable set DateTime
                if gglobs.GStype == "Online":
                    self.GSSetOnlineAction.setEnabled(True) # enable Online mode
                    self.GSRebootAction.setEnabled(True)    # enable Reboot
                else:
                    self.GSSetOnlineAction.setEnabled(False)
                    self.GSRebootAction.setEnabled(False)

            else:
                # failure in connection
                fprint(header("GammaScout Device"))
                efprint("Failure connecting with device ", "'{}' with message:<br>{}<br>".format(gglobs.GSDeviceName, errmsg))
                self.dbtnGS.setStyleSheet(self.dbtnStyleSheetError)

        else: # new_connection == OFF
            fprint(header("Disconnect GammaScout Device"))
            if gglobs.GSConnection:
                errmsg = gdev_scout.terminateGammaScout()
                if not gglobs.GSConnection:
                    # successful dis-connect
                    self.setEnableDeviceActions(new_enable = False, device="GS")
                    self.GSInfoActionExt.setEnabled(False)    # disable extended info
                    self.GSResetAction.setEnabled(False)      # disable reset
                    self.GSSetPCModeAction.setEnabled(False)  # disable PC Mode
                    self.GSDateTimeAction.setEnabled(False)   # disable set DateTime
                    self.GSSetOnlineAction.setEnabled(False)  # disable Online Mode
                    self.GSRebootAction.setEnabled(False)     # disable Reboot
                    fprint("Disconnected successfully:", "'{}'".format(gglobs.GSDeviceName), debug=True)
                else:
                    efprint("Disconnection Error with Device: {} with message:<br>{}".format(gglobs.GSDeviceName, errmsg))
            else:
                fprint("No connected device")
            self.dbtnGS.setStyleSheet(self.dbtnStyleSheetOFF)

        Qt_update()

        self.setNormalCursor()
        setDebugIndent(0)


    def switchRaspi_Connection(self, new_connection = "ON"):
        """Raspi connection using interrupt"""

        if not gglobs.RaspiActivation:  return

        #~fncname = "switchRaspi_Connection: "
        fncname = sys._getframe().f_code.co_name +": "
        #~print( 'caller name:', inspect.stack()[1][3])
        #~print( 'fon name:', sys._getframe(  ).f_code.co_name)

        dprint(fncname + "--> {}. ".format(new_connection))
        setDebugIndent(1)

        self.setBusyCursor()

        if new_connection == "ON":
            errmsg = gdev_raspi.initRaspi()
            if gglobs.RaspiConnection:
                # successful connect
                self.dbtnRaspi.setStyleSheet(self.dbtnStyleSheetON)
                #~self.printRaspiDevInfo()
                gdev_raspi.printRaspiDevInfo()
                dprint(fncname + "ON: for device: {}".format(gglobs.RaspiDeviceName))
                self.RaspiInfoActionExt.setEnabled(True)       # enable extended info
            else:
                # failure in connection
                fprint(header("Raspi Device"))
                efprint("Failure connecting with device: '{}' with message:<br>{}".format(gglobs.RaspiDeviceName, errmsg))
                self.dbtnRaspi.setStyleSheet(self.dbtnStyleSheetError)

        else: # new_connection == OFF
            fprint(header("Disconnect Raspi Device"))
            if gglobs.RaspiConnection:
                gdev_raspi.terminateRaspi()
                if not gglobs.RaspiConnection:
                    # successful dis-connect
                    fprint("Disconnected successfully:", "'{}'".format(gglobs.RaspiDeviceName), debug=True)
                else:
                    # failure in dis-connection
                    fprint("Disconnection error with device:", gglobs.RaspiDeviceName)
            else:
                fprint("No connected device")
            self.dbtnRaspi.setStyleSheet(self.dbtnStyleSheetOFF)

        Qt_update()

        self.setNormalCursor()
        setDebugIndent(0)


    def switchSimul_Connection(self, new_connection = "ON"):
        """SimulCounter connections"""

        if not gglobs.SimulActivation:  return

        fncname = "switchSimul_Connection: "

        dprint(fncname + "--> {}. ".format(new_connection))
        setDebugIndent(1)

        self.setBusyCursor()

        if new_connection == "ON":
            errmsg = gdev_simul.initSimulCounter() # so far there is never an error in audio
            if gglobs.SimulConnection:
                # successful connect
                self.dbtnSimul.setStyleSheet(self.dbtnStyleSheetON)
                gdev_simul.fprintSimulCounterInfo()
                dprint(fncname + "ON: for device: {}".format(gglobs.SimulDeviceName))
                #~self.SimulInfoActionExt.setEnabled(True)      # enable extended info
                self.SimulSettings.setEnabled(True)       # enable settings
            else:
                # failure in connection
                fprint(header("SimulCounter Device"))
                efprint("Failure to connect with Device:", "'{}'".format(gglobs.SimulDeviceName))
                qefprint(errmsg)
                self.dbtnSimul.setStyleSheet(self.dbtnStyleSheetError)

        else: # new_connection == OFF
            fprint(header("Disconnect SimulCounter Device"))
            if gglobs.SimulConnection:
                gdev_simul.terminateSimulCounter()
                if not gglobs.SimulConnection:
                    # successful dis-connect
                    #~self.SimulInfoActionExt.setEnabled(False)    # disable extended info
                    self.SimulSettings.setEnabled(False)            # disable settings
                    fprint("Disconnected successfully:", "'{}'".format(gglobs.SimulDeviceName), debug=True)
                else:
                    fprint("Disconnection Error with Device:", gglobs.SimulDeviceName)
            else:
                fprint("No connected device")
            self.dbtnSimul.setStyleSheet(self.dbtnStyleSheetOFF)

        Qt_update()

        self.setNormalCursor()
        setDebugIndent(0)


    def switchMiniMon_Connection(self, new_connection = "ON"):
        """MiniMonCounter connections"""

        if not gglobs.MiniMonActivation:  return

        fncname = "switchMiniMon_Connection: "

        dprint(fncname + "--> {}. ".format(new_connection))
        setDebugIndent(1)

        self.setBusyCursor()

        if new_connection == "ON":
            errmsg = gdev_minimon.initMiniMon()
            if gglobs.MiniMonConnection:
                # successful connect
                self.dbtnMiniMon.setStyleSheet(self.dbtnStyleSheetON)
                gdev_minimon.printMiniMonInfo()
                dprint(fncname + "ON: for device: {}".format(gglobs.MiniMonDeviceName))
                #~self.MiniMonInfoActionExt.setEnabled(True)      # enable extended info
            else:
                # failure in connection
                fprint(header("MiniMon Device"))
                efprint("Failure to connect with Device:", "'{}'".format(gglobs.MiniMonDeviceName))
                qefprint(errmsg)
                self.dbtnMiniMon.setStyleSheet(self.dbtnStyleSheetError)

        else: # new_connection == OFF
            fprint(header("Disconnect MiniMonCounter Device"))
            if gglobs.MiniMonConnection:
                gdev_minimon.terminateMiniMon()
                if not gglobs.MiniMonConnection:
                    # successful dis-connect
                    #~self.MiniMonInfoActionExt.setEnabled(False)    # disable extended info
                    fprint("Disconnected successfully:", "'{}'".format(gglobs.MiniMonDeviceName), debug=True)
                else:
                    fprint("Disconnection Error with Device:", gglobs.MiniMonDeviceName)
            else:
                fprint("No connected device")
            self.dbtnMiniMon.setStyleSheet(self.dbtnStyleSheetOFF)

        Qt_update()

        self.setNormalCursor()
        setDebugIndent(0)


    def checkLoggingState(self):
        """enabling and disabling menu and toolbar entries"""

        # Logging
        if gglobs.logging:
            self.logLoadFileAction.         setEnabled(False)   # no loading of log files during logging
            self.logLoadCSVAction .         setEnabled(False)   # no loading of CSV log files during logging
            self.startloggingAction.        setEnabled(False)   # no start logging - it is running already
            self.stoploggingAction.         setEnabled(True)    # stopping is possible
            self.quickLogAction.            setEnabled(False)   # no quickstart of logging - it is running already
            self.WebAction.                 setEnabled(True)    # updating web map only during logging
            self.logSnapAction.             setEnabled(True)    # snaps are possible only during logging

            if gglobs.GMCActivation:                            # GMC
                self.histGMCDeviceAction.   setEnabled(False)   # no downloads during logging
            if gglobs.GSActivation:                             # GammaScout
                self.histGSDeviceAction.    setEnabled(False)   # no downloads during logging
            if gglobs.AmbioActivation:                          # AmbioMon
                self.histAMDeviceCAMAction. setEnabled(False)   # no downloads during logging
                self.histAMDeviceCPSAction. setEnabled(False)   # no downloads during logging

        # Not Logging
        else:
            self.logLoadFileAction.         setEnabled(True)    # can load log files
            self.logLoadCSVAction .         setEnabled(True)    # can load CSV log files
            self.startloggingAction.        setEnabled(True)    # can start logging (GMC powering need will be excluded later)
            self.stoploggingAction.         setEnabled(False)   # cannot stop - it is not running
            self.quickLogAction.            setEnabled(True)    # quickstart is possible (GMC powering need will be excluded later)
            self.WebAction.                 setEnabled(False)   # cannot update web when not logging
            self.logSnapAction.             setEnabled(False)   # cannot take snaps when not logging

            if gglobs.GMCActivation:                            # GMC
                self.histGMCDeviceAction.   setEnabled(True)    # can download from device when not logging even if powered off
                if gdev_gmc.isGMC_PowerOn() == "OFF" \
                   and gglobs.DevicesConnected == 1:            # GMC is NOT powered ON and is only device
                    self.startloggingAction.setEnabled(False)   # cannot start logging without power
                    self.quickLogAction.    setEnabled(False)   # quickstart is NOT possible without power

            if gglobs.GSActivation:                             # GammaScout
                self.histGSDeviceAction.    setEnabled(True)    # can download from device when not logging

            if gglobs.AmbioActivation:                          # AmbioMon
                self.histAMDeviceCAMAction. setEnabled(True)    # can download from device when not logging
                self.histAMDeviceCPSAction. setEnabled(True)    # can download from device when not logging

            if gglobs.logDBPath == None:
                self.startloggingAction.    setEnabled(False)   # no log file loaded

            if gglobs.DevicesConnected == 0:                    # no connected devices
                self.quickLogAction.        setEnabled(False)
                self.startloggingAction.    setEnabled(False)

        # adding Log comments allowed when a file is defined
        if gglobs.logDBPath != None: self.addCommentAction.     setEnabled(True)
        else:                        self.addCommentAction.     setEnabled(False)

        # adding History comments allowed when a file is defined
        if gglobs.hisDBPath != None: self.addHistCommentAction. setEnabled(True)
        else:                        self.addHistCommentAction. setEnabled(False)


    def setEnableDeviceActions(self, new_enable = True, device="" ):
        """Dis/Enable device specific device actions"""

        # Device
        self.DeviceConnectAction.        setEnabled(not new_enable)
        self.DeviceDisconnectAction.     setEnabled(new_enable)
        self.setLogTimingAction.         setEnabled(new_enable)

        # GMC counter
        if device == "GMC":
            # submenu GMC
            self.GMCInfoActionExt.       setEnabled(new_enable)
            self.GMCConfigAction.        setEnabled(new_enable)
            self.GMCConfigEditAction.    setEnabled(new_enable)
            self.GMCONAction.            setEnabled(new_enable)
            self.GMCOFFAction.           setEnabled(new_enable)
            self.GMCSetTimeAction.       setEnabled(new_enable)
            self.GMCREBOOTAction.        setEnabled(new_enable)
            self.GMCFACTORYRESETAction.  setEnabled(new_enable)

            # GMC Device functions using the config
            self.GMCSpeakerONAction.     setEnabled(new_enable)
            self.GMCSpeakerOFFAction.    setEnabled(new_enable)
            self.GMCAlarmONAction.       setEnabled(new_enable)
            self.GMCAlarmOFFAction.      setEnabled(new_enable)
            self.GMCSavingStateAction.   setEnabled(new_enable)

            #toolbar GMC Power Toggle
            self.dbtnGMCPower.           setEnabled(False)

            # History
            self.histGMCDeviceAction.    setEnabled(new_enable)

        # AudioCounter
        if device == "Audio":
            pass
            # no need???
            #~self.histAMDeviceCAMAction.  setEnabled(new_enable)
            #~self.histAMDeviceCPSAction.  setEnabled(new_enable)
            #~self.AmbioDataModeAction.    setEnabled(new_enable)

        # Gamma-Scout counter
        if device == "GS":
            self.histGSDeviceAction.     setEnabled(new_enable)

        # RadMon
        if device == "RadM":
            pass

        # AmbioMon
        if device == "Ambio":
            self.histAMDeviceCAMAction.  setEnabled(new_enable)
            self.histAMDeviceCPSAction.  setEnabled(new_enable)
            self.AmbioDataModeAction.    setEnabled(new_enable)


    def setDisableDeviceActions(self):
        """called only when GMC internal config is not usable"""

        self.GMCSpeakerONAction.        setEnabled(False)
        self.GMCSpeakerOFFAction.       setEnabled(False)
        self.GMCAlarmONAction.          setEnabled(False)
        self.GMCAlarmOFFAction.         setEnabled(False)
        self.GMCSavingStateAction.      setEnabled(False)


    def toggleGMCPower(self):
        """Toggle GMC device Power ON / OFF"""

        if gglobs.logging:
            self.showStatusMessage("Cannot change power when logging! Stop logging first")
            return

        if gdev_gmc.isGMC_PowerOn() == "ON": self.switchGMCPower("OFF")
        else:                                self.switchGMCPower("ON")


    def switchGMCPower(self, newstate = "ON"):
        """Switch power of GMC device to ON or OFF"""

        fprint(header("Switch GMC Device Power {}".format(newstate)), debug=True)

        self.setBusyCursor()
        if newstate == "ON":
            if gdev_gmc.isGMC_PowerOn() != "ON":
                gdev_gmc.setGMC_POWERON()
                time.sleep(3) # takes some time to settle!
        else:
            if gdev_gmc.isGMC_PowerOn() == "ON":
                if gglobs.logging: self.stopLogging()
                gdev_gmc.setGMC_POWEROFF()
                time.sleep(3) # takes some time to settle!

        gglobs.GMCcfg, error, errmessage     = gdev_gmc.getGMC_CFG()     # read config after power change

        if gdev_gmc.isGMC_PowerOn() == "ON": fprint("Power is ON")
        else:                               fprint("Power is OFF")
        self.setGMCPowerIcon()

        self.checkLoggingState()
        self.setNormalCursor()


    def setGMCPowerIcon(self):

        ipo = gdev_gmc.isGMC_PowerOn()
        #fprint("setGMCPowerIcon: Device Power State: ",  ipo)

        if   ipo == "ON":   self.dbtnGMCPower.setIcon(QIcon(QPixmap(os.path.join(gglobs.gresPath, 'icon_power-round_on.png'))))
        elif ipo == "OFF":  self.dbtnGMCPower.setIcon(QIcon(QPixmap(os.path.join(gglobs.gresPath, 'icon_power-round_off.png'))))
        else:               self.dbtnGMCPower.setIcon(QIcon(QPixmap(os.path.join(gglobs.gresPath, 'icon_power-round_on.png'))))


#help
    def helpQuickStart(self):
        """Quickstart item on the Help menu"""

        msg = QMessageBox()
        msg.setWindowIcon(self.iconGeigerLog)
        msg.setWindowTitle("Help - Quickstart")
        #msg.setFont(self.fontstd) # this will set Monospace font!
        msg.setText(gglobs.helpQuickstart)

        msg.setStandardButtons(QMessageBox.Ok)
        msg.setDefaultButton(QMessageBox.Ok)
        msg.setEscapeButton(QMessageBox.Ok)
        msg.setWindowModality(Qt.WindowModal)
        msg.setMinimumWidth(800)
        msg.setStyleSheet("QLabel{min-width:700px; font-size:12pt;}")

        msg.exec()


    def helpFirmwareBugs(self):
        """Geiger Counter Firmware Bugs info on the Help menu"""

        msg = QMessageBox()
        msg.setWindowIcon(self.iconGeigerLog)
        msg.setWindowTitle("Help - Firmware Bugs")
        #msg.setFont(self.fontstd) # this will set Monospace font!
        msg.setTextFormat(Qt.RichText)
        msg.setText(gglobs.helpFirmwareBugs)

        msg.setStandardButtons(QMessageBox.Ok)
        msg.setDefaultButton(QMessageBox.Ok)
        msg.setEscapeButton(QMessageBox.Ok)
        msg.setWindowModality(Qt.WindowModal)
        msg.setStyleSheet("QLabel{min-width:700px; font-size:11pt;}")

        msg.exec()


    def helpWorldMaps(self):
        """Using the Radiation World Map"""

        msg = QMessageBox()
        msg.setWindowIcon(self.iconGeigerLog)
        msg.setWindowTitle("Help - Radiation World Maps")
        #msg.setFont(self.fontstd) # this will set Monospace font!
        msg.setText(gglobs.helpWorldMaps)

        msg.setStandardButtons(QMessageBox.Ok)
        msg.setDefaultButton(QMessageBox.Ok)
        msg.setEscapeButton(QMessageBox.Ok)
        msg.setWindowModality(Qt.WindowModal)
        msg.setStyleSheet("QLabel{min-width:700px; font-size:12pt;}")

        msg.exec()


    def helpOccupationalRadiation(self):
        """Occupational Radiation Limits"""

        msg = QMessageBox()
        msg.setWindowIcon(self.iconGeigerLog)
        msg.setWindowTitle("Help - Occupational Radiation Limits")
        #msg.setFont(self.fontstd) # this will set Monospace font!
        msg.setText(gglobs.helpOccupationalRadiation)

        msg.setStandardButtons(QMessageBox.Ok)
        msg.setDefaultButton(QMessageBox.Ok)
        msg.setEscapeButton(QMessageBox.Ok)
        msg.setWindowModality(Qt.WindowModal)
        msg.setStyleSheet("QLabel{min-width:700px; font-size:12pt;}")

        msg.exec()


    def helpOptions(self):
        """Options item on the Help menu"""

        msg = QMessageBox()
        msg.setWindowIcon(self.iconGeigerLog)
        msg.setWindowTitle("Help - Options")
        msg.setFont(self.fontstd)   # required! is plain text, not HTML
        msg.setText(gglobs.helpOptions)

        msg.setStandardButtons(QMessageBox.Ok)
        msg.setDefaultButton(QMessageBox.Ok)
        msg.setEscapeButton(QMessageBox.Ok)
        msg.setWindowModality(Qt.WindowModal)
        msg.setStyleSheet("QLabel{min-width:800px; font-size:12pt;}")

        msg.exec()


    def helpAbout(self):
        """About item on the Help menu"""

        # the curly brackets {} used for Python's format() don't work when the
        # text has CSS formatting using {}!
        description = gglobs.helpAbout % (__author__, gglobs.__version__, __copyright__, __license__)

        licon   = QLabel() # label to hold the geigerlog icon
        licon.setPixmap(QPixmap(os.path.join(gglobs.gresPath, 'icon_geigerlog.png')))

        ltext   = QLabel() # label to hold the 'eigerlog' text as picture
        ltext.setPixmap(QPixmap(os.path.join(gglobs.gresPath, 'eigerlog.png')))

        labout  = QTextBrowser() # label to hold the description
        labout.setLineWrapMode(QTextEdit.WidgetWidth)
        labout.setText(description)
        labout.setOpenExternalLinks(True) # to open links in a browser
        labout.setTextInteractionFlags(Qt.LinksAccessibleByMouse|Qt.TextSelectableByMouse)
        labout.setMinimumWidth(700) # set the width:

        d = QDialog()
        d.setWindowIcon(self.iconGeigerLog)
        #d.setFont(self.fontstd)
        d.setWindowTitle("Help - About GeigerLog")
        #d.setWindowModality(Qt.ApplicationModal)
        d.setWindowModality(Qt.WindowModal)
        #d.setMinimumWidth(1800)
        screen_available = QDesktopWidget().availableGeometry()
        d.setMinimumHeight(min(screen_available.height(), gglobs.window_height + 220))

        bbox    = QDialogButtonBox()
        bbox.setStandardButtons(QDialogButtonBox.Ok)
        bbox.accepted.connect(lambda: d.done(0))

        layoutTop = QHBoxLayout()
        layoutTop.addWidget(licon)
        layoutTop.addWidget(ltext)
        layoutTop.addStretch()      # to keep the icons on the left

        layoutV   = QVBoxLayout(d)
        layoutV.addLayout(layoutTop)
        layoutV.addWidget(labout)
        layoutV.addWidget(bbox)

        d.exec()



    def helpSetPort(self):
        """sets the Port and Baud rate"""

        #lpAttribs = ["name", "hwid", "device", "description", "serial_number", "location", "manufacturer", "product", "interface", "vid", "pid"]

        dprint("helpSetPort:")
        setDebugIndent(1)

        selection_ports    = []
        selection_baudGMC  = list(map(str,sorted(gglobs.GMCbaudrates, reverse=True)))
        selection_baudI2C  = list(map(str,sorted(gglobs.I2Cbaudrates, reverse=True)))
        selection_baudGS   = list(map(str,sorted(gglobs.GSbaudrates,  reverse=True)))

        enableSelections = True

        lp = getPortList(symlinks=True) # ist in gutil
        #~print("-----------------lp:          : ", lp)

        hsp = "Available Ports:"
        hsp += "\n{:15s} {:40s}  {:14s}   {:s}\n{}\n".format("Port", "Name of USB-to-Serial Hardware", "Linked to Port", "VID :PID", "-"*82)

        if len(lp) == 0:
            errmessage = "ERROR: No available serial ports found"
            dprint("helpSetPort: " + errmessage, debug=True)
            hsp += errmessage + "\n" + "Is device connected? Check cable and plugs! Re-run in a few seconds." + "\n\n\n"
            enableSelections = False
        else:
            for p in lp:
                #~print("\np: ", p)
                try:
                    link = "No Link"
                    if hasattr(p, "hwid") and "LINK=" in p.hwid:
                        link1 = p.hwid.find("LINK=")
                        link2 = p.hwid.find("LINK=", link1 + 5)
                        #~print("device:", p.device, ",   hwid:", p.hwid)
                        #~print("link1: ", link1, ", link2: ", link2)
                        if link2 > 0:   link = p.hwid[link1 + 5 : link2]
                        else:           link = p.hwid[link1 + 5 : ]

                    p_device        = getattr(p, "device",      "None")
                    p_description   = getattr(p, "description", "None")
                    #~print("p_description: ", p_description)
                    if len(p_description) > 38: p_description = p_description[:37] + "..." # do not show complete length
                    #~print("p_device:      ", p_device)
                    #~print("p_description: ", p_description)

                    p_vid           = getattr(p, "vid",         0)
                    if p_vid is None:   strp_vid = "None"
                    else:               strp_vid = "{:04X}".format(p_vid)

                    p_pid           = getattr(p, "pid",         0)
                    if p_pid is None:   strp_pid = "None"
                    else:               strp_pid = "{:04X}".format(p_pid)

                    if p_device != "None":
                        selection_ports.append(p.device)
                        hsp += "{:15s} {:40s}  {:14s}   {}:{}\n".format(p_device, p_description, link, strp_vid, strp_pid)

                except Exception as e:
                    dprint("helpSetPort: Exception: {}  list_port: {}".format(e, p))
                    enableSelections = False

        if gglobs.GMCActivation or gglobs.I2CActivation or gglobs.GSActivation:
            isAnySerDeviceActivated = True
        else:
            isAnySerDeviceActivated = False

    # GMC
        # Combo Box Ports
        portCbBoxGMC = QComboBox(self)
        portCbBoxGMC.setEnabled(gglobs.GMCActivation)
        portCbBoxGMC.addItems(selection_ports)
        portCbBoxGMC.setToolTip('Select the USB-to-Serial port')
        portCbBoxGMC.setCurrentIndex(portCbBoxGMC.findText(gglobs.GMCusbport))

        # Combo Box Baudrates
        baudCbBoxGMC = QComboBox(self)
        baudCbBoxGMC.setEnabled(gglobs.GMCActivation)
        baudCbBoxGMC.addItems(selection_baudGMC)
        baudCbBoxGMC.setToolTip('Select the USB-to-Serial baudrate')
        baudCbBoxGMC.setCurrentIndex(baudCbBoxGMC.findText(str(gglobs.GMCbaudrate)))

        # H-Layout of Combo Boxes
        cblayoutGMC = QHBoxLayout()
        cblayoutGMC.addWidget(portCbBoxGMC)
        cblayoutGMC.addWidget(baudCbBoxGMC)


    # I2C
        # Combo Box Ports
        portCbBoxI2C = QComboBox(self)
        portCbBoxI2C.setEnabled(gglobs.I2CActivation)
        portCbBoxI2C.addItems(selection_ports)
        portCbBoxI2C.setToolTip('Select the USB-to-Serial port')
        portCbBoxI2C.setCurrentIndex(portCbBoxI2C.findText(gglobs.I2Cusbport))

        # Combo Box Baudrates
        baudCbBoxI2C = QComboBox(self)
        baudCbBoxI2C.setEnabled(gglobs.I2CActivation)
        baudCbBoxI2C.addItems(selection_baudI2C)
        baudCbBoxI2C.setToolTip('Select the USB-to-Serial baudrate')
        baudCbBoxI2C.setCurrentIndex(baudCbBoxI2C.findText(str(gglobs.I2Cbaudrate)))

        # H-Layout of Combo Boxes
        cblayoutI2C = QHBoxLayout()
        cblayoutI2C.addWidget(portCbBoxI2C)
        cblayoutI2C.addWidget(baudCbBoxI2C)


    # GammaScout
        # Combo Box Ports
        portCbBoxGS = QComboBox(self)
        portCbBoxGS.setEnabled(gglobs.GSActivation)
        portCbBoxGS.addItems(selection_ports)
        portCbBoxGS.setToolTip('Select the USB-to-Serial port')
        portCbBoxGS.setCurrentIndex(portCbBoxGS.findText(gglobs.GSusbport))

        # Combo Box Baudrates
        baudCbBoxGS = QComboBox(self)
        baudCbBoxGS.setEnabled(gglobs.GSActivation)
        baudCbBoxGS.addItems(selection_baudGS)
        baudCbBoxGS.setToolTip('Select the USB-to-Serial baudrate')
        baudCbBoxGS.setCurrentIndex(baudCbBoxGS.findText(str(gglobs.GSbaudrate)))

        # H-Layout of Combo Boxes
        cblayoutGS = QHBoxLayout()
        cblayoutGS.addWidget(portCbBoxGS)
        cblayoutGS.addWidget(baudCbBoxGS)


    # hsplabel set Port Listings Text
        hsplabel = QLabel()
        hsplabel.setText(hsp)

        # hsp2label
        hsp2  = "Select port and baudrate for each activated device, which is using a serial connection:\n"
        hsp2 += "(GeigerLog's current settings are preselected if available)\n"

        hsp2label = QLabel()
        hsp2label.setText(hsp2)

    # Device labels
        # GMCDevice Label
        GMCDevice = QLabel("GMC Device:")

        # GammaScout Device Label
        GSDevice = QLabel("GammaScout Device:")

        # I2CDevice Label
        I2CDevice = QLabel("I2C Device:")

    # hsp3label
        if isAnySerDeviceActivated:
            hsp3 = "\nWhen you press OK, any logging will be stopped, and all of GeigerLog's devices will\n"
            hsp3 += "first be disconnected, and then reconnected with the chosen, new settings!\n"
            hsp3 += "\nPress Cancel to close without making any changes."
        else:
            hsp3 = "\nNo activated device using a Serial Port was found\n"
            hsp3 += "\nPress Cancel to close."


        hsp3label = QLabel()
        hsp3label.setText(hsp3)

    # Dialog Box
        title = "Help - Show & Select USB Port and Baudrate"
        d = QDialog()
        d.setWindowIcon(self.iconGeigerLog)
        d.setFont(self.fontstd)
        d.setWindowTitle(title)
        #d.setWindowModality(Qt.ApplicationModal) # no effect of either setting
        #d.setWindowModality(Qt.WindowModal)

    # Button Box
        bbox      = QDialogButtonBox()
        if enableSelections and isAnySerDeviceActivated:
            bbox.setStandardButtons(QDialogButtonBox.Ok| QDialogButtonBox.Cancel)
            bbox.accepted.connect(lambda: d.done(1))     # ok
        else:
            bbox.setStandardButtons(QDialogButtonBox.Cancel)
            bbox.accepted.connect(lambda: d.done(1))     # ok
        bbox.rejected.connect(lambda: d.done(-1))    # cancel

    # dialog layout
        layoutV = QVBoxLayout(d)
        layoutV.addWidget(hsplabel)
        layoutV.addWidget(hsp2label)

        layoutV.addWidget(GMCDevice)
        layoutV.addLayout(cblayoutGMC)

        layoutV.addWidget(GSDevice)
        layoutV.addLayout(cblayoutGS)

        layoutV.addWidget(I2CDevice)
        layoutV.addLayout(cblayoutI2C)

        layoutV.addWidget(hsp3label)
        layoutV.addWidget(bbox)

        retval = d.exec()
        #print("---retval=",retval)

        if retval != 1:      # user has selected Cancel or pressed ESC
            dprint("helpSetPort: cancelled by user")

        else:
            fprint(header(title))
            if gglobs.GMCActivation:
                gglobs.GMCusbport  = portCbBoxGMC.currentText()
                gglobs.GMCbaudrate = int(baudCbBoxGMC.currentText())
                dprint("helpSetPort: GMC device: Port: {} with Baudrate: {}".format(gglobs.GMCusbport, gglobs.GMCbaudrate))
                fprint("GMC Device:")
                fprint("- USB-to-Serial Port:",   gglobs.GMCusbport)
                fprint("- Baudrate:",             gglobs.GMCbaudrate)

            if gglobs.GSActivation:
                gglobs.GSusbport  = portCbBoxGS.currentText()
                gglobs.GSbaudrate = int(baudCbBoxGS.currentText())
                dprint("helpSetPort: GammaScout device: Port: {} with Baudrate: {}".format(gglobs.GSusbport, gglobs.GSbaudrate))
                fprint("GS Device:")
                fprint("- USB-to-Serial Port:",   gglobs.GSusbport)
                fprint("- Baudrate:",             gglobs.GSbaudrate)

            if gglobs.I2CActivation:
                gglobs.I2Cusbport  = portCbBoxI2C.currentText()
                gglobs.I2Cbaudrate = int(baudCbBoxI2C.currentText())
                dprint("helpSetPort: I2C device: Port: {} with Baudrate: {}".format(gglobs.I2Cusbport, gglobs.I2Cbaudrate))
                fprint("I2C Device:")
                fprint("- USB-to-Serial Port:",   gglobs.I2Cusbport)
                fprint("- Baudrate:",             gglobs.I2Cbaudrate)

            self.stopLogging()
            self.switchConnections(new_connection = "OFF")
            self.switchConnections(new_connection = "ON")

        setDebugIndent(0)


    def changeOptions(self):
        """Switches State of some options"""

        options   = ("Verbose  = False",
                     "Verbose  = True",
                     "Debug    = False",
                     "Debug    = True",
                     "Redirect = False",
                     "Redirect = True",
                     "testing  = False",
                     "testing  = True",
                     "werbose  = False",
                     "werbose  = True",
                     "stattest = False",
                     "stattest = True",
                     )

        index         = 0
        text, ok      = QInputDialog().getItem(None, 'Switch Option', "Select new option setting and press ok:   ", options, index, False )
        vprint("changeOptions: text= '{}', ok={}".format( text, ok))

        if not ok: return      # user has selected Cancel

        newIndex    = options.index(text)

        fprint(header("Change Options"))
        fprint("New Option setting:", "{}".format(options[newIndex]))

    # The ranking is debug --> verbose --> werbose
    # if any is true, the higher one(s) must also be true
    # verbose
        if   newIndex == 0:
            gglobs.verbose  = False
            gglobs.werbose  = False

        elif newIndex == 1:
            gglobs.verbose  = True
            gglobs.debug    = True

    # debug
        elif newIndex == 2:
            gglobs.debug    = False
            gglobs.verbose  = False
            gglobs.werbose  = False
        elif newIndex == 3:
            gglobs.debug    = True

    # redirect
        elif newIndex == 4:
            gglobs.redirect = False
        elif newIndex == 5:
            gglobs.redirect = True

    # testing
        elif newIndex == 6:
            gglobs.testing  = False
        elif newIndex == 7:
            gglobs.testing  = True

    # werbose
        elif newIndex == 8:
            gglobs.werbose  = False
        elif newIndex == 9:
            gglobs.werbose  = True
            gglobs.verbose  = True
            gglobs.debug    = True

    # stattest
        elif newIndex == 10:
            gglobs.stattest  = False

        elif newIndex == 11:
            gglobs.stattest  = True


    def editScaling(self):
        """shows the current settings of [ValueScaling] and [GraphScaling]"""

    # value
        valueBox=QFormLayout()
        valueBox.setSizeConstraint (QLayout.SetFixedSize)
        #valueBox.setFieldGrowthPolicy (QFormLayout.AllNonFixedFieldsGrow)
        #valueBox.setFieldGrowthPolicy (QFormLayout.FieldsStayAtSizeHint)
        #valueBox.setFieldGrowthPolicy (QFormLayout.ExpandingFieldsGrow)

        #valueBox.RowWrapPolicy(QFormLayout.DontWrapRows)
        #valueBox.RowWrapPolicy(QFormLayout.WrapLongRows)
        #valueBox.RowWrapPolicy(QFormLayout.WrapAllRows)

        valueBox.addRow(QLabel("{:60s}".format("<b>ValueScaling</b> - it DOES modify the saved value!<br> ")))
        for vname in gglobs.varsDefault:
            valueBox.addRow(vname, QLineEdit(gglobs.ValueScale[vname]))

    # graph
        graphBox=QFormLayout()
        #graphBox.setFieldGrowthPolicy (QFormLayout.AllNonFixedFieldsGrow)
        #graphBox.setFieldGrowthPolicy (QFormLayout.FieldsStayAtSizeHint)
        graphBox.setFieldGrowthPolicy (QFormLayout.ExpandingFieldsGrow)

        graphBox.RowWrapPolicy(QFormLayout.DontWrapRows)
        #graphBox.RowWrapPolicy(QFormLayout.WrapAllRows)
        #graphBox.RowWrapPolicy(QFormLayout.WrapLongRows)

        graphBox.addRow(QLabel("{:60s}".format("<b>GraphScaling</b> - it does NOT modify the saved value, <br>only the plotted value")))
        for vname in gglobs.varsDefault:
            graphBox.addRow(vname, QLineEdit(gglobs.GraphScale[vname]))

        vgLayout = QHBoxLayout()
        vgLayout.addLayout(valueBox)
        vgLayout.addLayout(graphBox)

        self.dialog = QDialog()
        self.dialog.setWindowIcon(self.iconGeigerLog)
        #self.dialog.setFont(self.fontstd)
        self.dialog.setWindowTitle("View and Edit Current Scaling")
        self.dialog.setWindowModality(Qt.ApplicationModal)
        #~ self.dialog.setWindowModality(Qt.WindowModal)
        self.dialog.setMinimumWidth(700)
        self.dialog.setMaximumWidth(1000)
        #self.dialog.setMinimumHeight(gglobs.window_height + 50)

        # buttonbox: https://srinikom.github.io/pyside-docs/PySide/QtGui/QDialogButtonBox.html
        bbox = QDialogButtonBox()
        bbox.setStandardButtons(QDialogButtonBox.Ok|QDialogButtonBox.Cancel)
        bbox.accepted.connect(lambda: self.dialog.done(0))
        bbox.rejected.connect(lambda: self.dialog.done(1))

        layoutV = QVBoxLayout(self.dialog)
        layoutV.addWidget(QLabel("See GeigerLog manual in chapter <b>Configuration of GeigerLog</b>, topic <b>Scaling</b>, for guidance<br>"))
        layoutV.addLayout(vgLayout)
        layoutV.addWidget(bbox)

        resultdlg = self.dialog.exec()             # both seem to work the same

        if resultdlg == 0:
            #print("row count: ", valueBox.rowCount(), graphBox.rowCount())
            for i in range(0, len(gglobs.varsBook) + 1):
                if valueBox.itemAt(i, QFormLayout.LabelRole) is not None:
                    vvname = (valueBox.itemAt(i, QFormLayout.LabelRole).widget().text()).strip()
                    vval   = (valueBox.itemAt(i, QFormLayout.FieldRole).widget().text()).strip().replace(",", ".")
                    wprint("valueBox i: {:2d}  {:10s}  {}".format(i, vvname, vval))
                    gglobs.ValueScale[vvname] = vval

            for i in range(0, len(gglobs.varsBook) + 1):
                if graphBox.itemAt(i, QFormLayout.LabelRole) is not None:
                    gvname = (graphBox.itemAt(i, QFormLayout.LabelRole).widget().text()).strip()
                    gval   = (graphBox.itemAt(i, QFormLayout.FieldRole).widget().text()).strip().replace(",", ".")
                    wprint("graphBox i: {:2d}  {:10s}  {}".format(i, gvname, gval))
                    gglobs.GraphScale[gvname] = gval

        #print("gglobs.ValueScale: ", gglobs.ValueScale)
        #print("gglobs.GraphScale: ", gglobs.GraphScale)


#utilities in Class

    def clearNotePad(self):
        """Clear the notepad"""

        self.notePad.append("<span style='color:black;'>&nbsp;</span>")
        self.notePad.setStyleSheet("color: rgb(40, 40, 40)")
        self.notePad.clear()

        self.notePad.setTextColor(QColor(40, 40, 40))


    def clearLogPad(self):
        """Clear the logpad"""

        self.logPad.clear()


    def setBusyCursor(self):

        QApplication.setOverrideCursor(Qt.WaitCursor)
        Qt_update()


    def setNormalCursor(self):

        QApplication.restoreOverrideCursor()
        Qt_update()


    def showStatusMessage(self, message, timing=0, error=True):
        """shows message by flashing the Status Bar red for 0.5 sec, then switches back to normal"""

        if error == False:
            self.statusBar.setStyleSheet("QStatusBar { }")      # reset to default colors
            self.statusBar.showMessage(message, msecs=timing)   # message remains until overwritten by next status
        else:
            playWav("error")
            self.statusBar.showMessage(message, msecs=timing)   # message remains until overwritten by next status
            self.statusBar.setStyleSheet("QStatusBar { background-color:red; color:white; }")
            Qt_update()                                         # assure that things are visible
            time.sleep(0.5)                                     # stays red for 0.5 sec
            self.statusBar.setStyleSheet("QStatusBar { }")      # reset to default colors


######## class ggeiger ends ###################################################
