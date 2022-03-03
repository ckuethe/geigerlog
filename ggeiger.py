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
__copyright__       = "Copyright 2016, 2017, 2018, 2019, 2020, 2021, 2022"
__credits__         = [""]
__license__         = "GPL3"

from   gsup_utils  import *

import gsup_sql
import gsup_tools
import gsup_plot
import gweb_monserv

import gstat_poisson
import gstat_fft
import gstat_convfft
import gstat_synth

if gglobs.Devices["GMC"][ACTIV]  :      import gdev_gmc         # both needed
if gglobs.Devices["GMC"][ACTIV]  :      import gdev_gmc_hist    # both needed
if gglobs.Devices["Audio"][ACTIV]:      import gdev_audio       #
if gglobs.Devices["RadMon"][ACTIV]:     import gdev_radmon      # RadMon -  then imports "paho.mqtt.client as mqtt"
if gglobs.Devices["AmbioMon"][ACTIV]:   import gdev_ambiomon    #
if gglobs.Devices["GammaScout"][ACTIV]: import gdev_gscout      #
if gglobs.Devices["I2C"][ACTIV]:        import gdev_i2c         # I2C  -    then imports dongles and sensor modules
if gglobs.Devices["LabJack"][ACTIV]:    import gdev_labjack     # LabJack - then imports the LabJack modules
if gglobs.Devices["Simul"][ACTIV]:      import gdev_simul       #
if gglobs.Devices["Manu"][ACTIV]:       import gdev_manu        #
if gglobs.Devices["MiniMon"][ACTIV]:    import gdev_minimon     #
if gglobs.Devices["WiFiClient"][ACTIV]: import gdev_wificlient  #
if gglobs.Devices["WiFiServer"][ACTIV]: import gdev_wifiserver  #



class ggeiger(QMainWindow):

    def __init__(self):
        super(ggeiger, self).__init__()
        gglobs.exgg = self

        # hold the updated variable values in self.updateDisplayVariableValue()
        self.vlabels  = [None] * len(gglobs.varsCopy)
        self.svlabels = [None] * len(gglobs.varsCopy)

        # default font type
        # custom_font = QFont()
        # custom_font.setWeight(18);
        # QApplication.setFont(custom_font, "QLabel")
        # set the font for the top level window (and any of its children):
        # self.window().setFont(someFont)
        # # set the font for *any* widget created in this QApplication:
        # QApplication.instance().setFont(QFont("Deja Vue"))
        # QApplication.instance().setFont(QFont("Helvetica"))


        # edprint(QFont.family())
        edprint(QApplication.instance().font())
        edprint(QApplication.font())
        self.window().setFont(QFont("Sans Serif"))


        # font standard
        """
        # font standard
                #self.fontstd = QFont()
                #self.fontstd = QFont("Deja Vue", 10)
                #self.fontstd = QFont("pritzelbmpr", 10)
                #self.fontstd = QFont("Courier New", 10)
                #self.fontstd.setFamily('Monospace')         # options: 'Lucida'
                #self.fontstd.StyleHint(QFont.TypeWriter)    # options: QFont.Monospace, QFont.Courier
                #self.fontstd.StyleHint(QFont.Monospace)     # options: QFont.Monospace, QFont.Courier
                #self.fontstd.setStyleStrategy(QFont.PreferMatch)
                #self.fontstd.setFixedPitch(True)
                #self.fontstd.setPointSize(11) # 11 is too big
                #self.fontstd.setWeight(60)                  # options: 0 (thin) ... 99 (very thick); 60:ok, 65:too fat

                gglobs.fontstd = self.fontstd
        """

        # self.fatfont = QFontDatabase.systemFont(QFontDatabase.FixedFont) #
        # self.fatfont = QFontDatabase.systemFont(QFontDatabase.FixedFont) #
        self.fatfont = QFont("Deja Vue")
        # self.fatfont.setWeight(99)            # options: 0 (thin) ... 99 (very thick); 60:ok, 65:too fat
        self.fatfont.setWeight(65)            # options: 0 (thin) ... 99 (very thick); 60:ok, 65:too fat
        # self.fatfont.setPointSize(12)
        self.fatfont.setPointSize(11)

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
        iconpath = os.path.join(gglobs.gresPath, 'icon_geigerlog.png')
        self.iconGeigerLog    = QIcon(QPixmap(iconpath))
        gglobs.iconGeigerLog  = self.iconGeigerLog
        self.setWindowIcon(gglobs.iconGeigerLog)

        # this is used for Web sites
        with open(iconpath, 'rb') as file_handle:
            gglobs.iconGeigerLogWeb = file_handle.read()

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
        if "ARMV"    in platform.platform().upper(): y += 33                # some correction needed at least on Manu 4

        self.setGeometry(x, y, sw, sh)                                      # position window in upper right corner of screen
        #~dprint("screen Geometry: ", QDesktopWidget().screenGeometry())    # total hardware screen
        #~dprint("screen Available:", QDesktopWidget().availableGeometry()) # available screen


    #figure and its toolbar
        # a figure instance to plot on
        # figsize=(18, 18) in plt.figure() hat keine Auswirkungen
        # self.figure = plt.figure(facecolor = "#DFDEDD", edgecolor='lightgray',  linewidth = 0.0, dpi=gglobs.hidpiScaleMPL) # lighter grayface
        self.figure = plt.figure(facecolor = "#DFDEDD", edgecolor='#b8b8b8',  linewidth = 0.1, dpi=gglobs.hidpiScaleMPL) # lighter grayface
        #self.figure, self.ax1 = plt.subplots(facecolor='#DFDEDD') # lighter gray
        #plt.subplots(facecolor='#DFDEDD') # lighter gray
        plt.clf()  # must be done - clear figure or it will show an empty figure !!

        # canvas - this is the Canvas Widget that displays the `figure`
        # it takes the `figure` instance as a parameter to __init__
        # next command creates: Attribute Qt::AA_EnableHighDpiScaling must be set before QCoreApplication is created.
        self.canvas = FigureCanvas(self.figure)
        self.canvas.mpl_connect('motion_notify_event', self.updatecursorposition) # where the cursor is
        self.canvas.mpl_connect('button_press_event' , self.onclick)              # send a mouse click
        self.canvas.setContentsMargins(10,10,10,10)
        self.canvas.setMinimumHeight(500)

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

    #clearNotePad
        clearNPAction = QAction("Clear NotePad", self)
        addMenuTip(clearNPAction, "Delete all content of the NotePad")
        clearNPAction.triggered.connect(self.clearNotePad)

    #searchNotePad
        SearchNPAction = QAction("Search NotePad ...", self)
        SearchNPAction.setShortcut('Ctrl+F')
        addMenuTip(SearchNPAction, "Search NotePad for occurence of a text (Shortcut: CTRL-F)")
        SearchNPAction.triggered.connect(self.searchNotePad)

    #saveNotePad
        SaveNPAction = QAction("Save NotePad to File", self)
        addMenuTip(SaveNPAction, "Save Content of NotePad as text file named <current filename>.notes")
        SaveNPAction.triggered.connect(self.saveNotePad)

    #printNotePad
        PrintNPAction = QAction("Print NotePad ...", self)
        addMenuTip(PrintNPAction, "Print Content of NotePad to Printer or  PDF-File")
        PrintNPAction.triggered.connect(self.printNotePad)

    # exit
        exitAction = QAction('Exit', self)
        exitAction.setIcon(QIcon(QPixmap(os.path.join(gglobs.gresPath, 'icon_exit.png')))) # Flat icon
        exitAction.setShortcut('Ctrl+Q')
        addMenuTip(exitAction, 'Exit the GeigerLog program')
        exitAction.triggered.connect(self.close)

        fileMenu = self.menubar.addMenu('&File')
        fileMenu.setToolTipsVisible(True)

        fileMenu.addAction(clearNPAction)
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
        self.DeviceConnectAction.triggered.connect(lambda : self.switchAllConnections("ON"))

        self.DeviceDisconnectAction = QAction(QIcon(QPixmap(os.path.join(gglobs.gresPath, 'icon_plug_closed.png'))), 'Disconnect Devices', self, enabled = False)
        self.DeviceDisconnectAction.setShortcut('Ctrl+D')
        addMenuTip(self.DeviceDisconnectAction, 'Disconnect the computer from the devices')
        self.DeviceDisconnectAction.triggered.connect(lambda : self.switchAllConnections("OFF"))

        self.DeviceCalibAction = QAction("Geiger Tubes ...", self, enabled = True)
        addMenuTip(self.DeviceCalibAction, "Set sensitivities for all Geiger tubes temporarily")
        self.DeviceCalibAction.triggered.connect(self.setTemporaryTubeSensitivities)

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
        if gglobs.Devices["GMC"][ACTIV]  :

            self.GMCInfoAction = QAction('Show Info', self, enabled=True)
            addMenuTip(self.GMCInfoAction, 'Show basic info on GMC device')
            self.GMCInfoAction.triggered.connect(lambda: self.fprintDeviceInfo("GMC", extended = False))

            self.GMCInfoActionExt = QAction('Show Extended Info', self, enabled=False)
            addMenuTip(self.GMCInfoActionExt, 'Show extended info on GMC device')
            self.GMCInfoActionExt.triggered.connect(lambda: self.fprintDeviceInfo("GMC", extended = True))

            self.GMCConfigEditAction = QAction("Set GMC Configuration ...", self, enabled=False)
            addMenuTip(self.GMCConfigEditAction, 'View, Edit and Set the GMC device configuration')
            self.GMCConfigEditAction.triggered.connect(lambda: gdev_gmc.editGMC_Configuration())

            self.GMCConfigAction = QAction('Show Configuration Memory', self, enabled=False)
            addMenuTip(self.GMCConfigAction, 'Show the GMC device configuration memory as binary in human readable format')
            self.GMCConfigAction.triggered.connect(gdev_gmc.fprintGMC_ConfigMemory)

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
            self.GMCSetTimeAction.triggered.connect(gdev_gmc.GMCsetDateTime)

            self.GMCREBOOTAction = QAction('Reboot ...', self, enabled=False)
            addMenuTip(self.GMCREBOOTAction, 'Send REBOOT command to the GMC device')
            self.GMCREBOOTAction.triggered.connect(lambda: gdev_gmc.doREBOOT())

            self.GMCFACTORYRESETAction = QAction('FACTORYRESET ...', self, enabled=False)
            addMenuTip(self.GMCFACTORYRESETAction, 'Send FACTORYRESET command to the GMC device')
            self.GMCFACTORYRESETAction.triggered.connect(lambda: gdev_gmc.doFACTORYRESET(False))

            self.GMCFACTORYRESET_forceAction = QAction('Devel FACTORYRESET', self, enabled=True)
            addMenuTip(self.GMCFACTORYRESET_forceAction, 'Send FACTORYRESET command to the GMC device')
            self.GMCFACTORYRESET_forceAction.triggered.connect(lambda: gdev_gmc.doFACTORYRESET(True))

            deviceSubMenuGMC = deviceMenu.addMenu("GMC Series")
            deviceSubMenuGMC.setToolTipsVisible(True)
            deviceSubMenuGMC.addAction(self.GMCInfoAction)
            deviceSubMenuGMC.addAction(self.GMCInfoActionExt)
            deviceSubMenuGMC.addAction(self.GMCConfigEditAction)
            deviceSubMenuGMC.addAction(self.GMCConfigAction)
            deviceSubMenuGMC.addAction(self.GMCSetTimeAction)
            deviceSubMenuGMC.addAction(self.GMCREBOOTAction)
            deviceSubMenuGMC.addAction(self.GMCFACTORYRESETAction)
            if gglobs.devel:    # Factory Reset without checking
                deviceSubMenuGMC.addAction(self.GMCFACTORYRESET_forceAction)

            # if 0 and gglobs.devel:
            #     # do not use
            #     deviceSubMenuGMC.addAction(self.GMCONAction)
            #     deviceSubMenuGMC.addAction(self.GMCOFFAction)
            #     deviceSubMenuGMC.addAction(self.GMCAlarmONAction)
            #     deviceSubMenuGMC.addAction(self.GMCAlarmOFFAction)
            #     deviceSubMenuGMC.addAction(self.GMCSpeakerONAction)
            #     deviceSubMenuGMC.addAction(self.GMCSpeakerOFFAction)
            #     deviceSubMenuGMC.addAction(self.GMCSavingStateAction)

            #deviceMenu.triggered[QAction].connect(self.processtrigger)

    # submenu AudioCounter
        if gglobs.Devices["Audio"][ACTIV] :

            self.AudioInfoAction = QAction('Show Info', self, enabled=True)
            addMenuTip(self.AudioInfoAction, 'Show basic info on AudioCounter device')
            self.AudioInfoAction.triggered.connect(lambda: self.fprintDeviceInfo("Audio", extended = False))

            self.AudioInfoActionExt = QAction('Show Extended Info', self, enabled=False)
            addMenuTip(self.AudioInfoActionExt, 'Show extended info on AudioCounter device')
            self.AudioInfoActionExt.triggered.connect(lambda: self.fprintDeviceInfo("Audio", extended = True))

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
        if gglobs.Devices["RadMon"][ACTIV]  :

            self.RMInfoAction = QAction('Show Info', self, enabled=True)
            addMenuTip(self.RMInfoAction, 'Show basic info on RadMon device')
            self.RMInfoAction.triggered.connect(lambda: self.fprintDeviceInfo("RadMon", extended=False))

            self.RMInfoActionExt = QAction('Show Extended Info', self, enabled=False)
            addMenuTip(self.RMInfoActionExt, 'Show extended info on RadMon device')
            self.RMInfoActionExt.triggered.connect(lambda: self.fprintDeviceInfo("RadMon", extended = True))

            deviceSubMenuRM  = deviceMenu.addMenu("RadMon Series")
            deviceSubMenuRM.setToolTipsVisible(True)
            deviceSubMenuRM.addAction(self.RMInfoAction)
            deviceSubMenuRM.addAction(self.RMInfoActionExt)

    # submenu AmbioMon
        if gglobs.Devices["AmbioMon"][ACTIV]  :

            self.AmbioInfoAction = QAction('Show Info', self, enabled=True)
            addMenuTip(self.AmbioInfoAction, 'Show basic info on AmbioMon device')
            self.AmbioInfoAction.triggered.connect(lambda: self.fprintDeviceInfo("AmbioMon", extended=False))

            self.AmbioInfoActionExt = QAction('Show Extended Info', self, enabled=False)
            addMenuTip(self.AmbioInfoActionExt, 'Show extended info on AmbioMon device')
            self.AmbioInfoActionExt.triggered.connect(lambda: self.fprintDeviceInfo("AmbioMon", extended = True))

            self.AmbioSetServerIP = QAction('Set AmbioMon Device IP ...', self, enabled=True)
            addMenuTip(self.AmbioSetServerIP, 'Set the IP Adress or Domain Name of the AmbioMon device')
            self.AmbioSetServerIP.triggered.connect(gdev_ambiomon.setAmbioServerIP)

            self.AmbioDataModeAction = QAction('Select AmbioMon Data Type Mode ...', self, enabled=False)
            addMenuTip(self.AmbioDataModeAction, "Select what type of data the AmbioMon device sends during logging: 'LAST' for last available data value, or 'AVG' for last 1 minute average of values")
            self.AmbioDataModeAction.triggered.connect(gdev_ambiomon.setAmbioLogDatatype)

            AmbioPingAction = QAction("Ping AmbioMon Server", self)
            addMenuTip(AmbioPingAction, 'Ping AmbioMon Server and report success or failure')
            AmbioPingAction.triggered.connect(lambda: gdev_ambiomon.pingAmbioServer())

            AmbioSerialAction = QAction("Send Message to AmbioMon via Serial", self)
            addMenuTip(AmbioSerialAction, "Send Message to AmbioMon via a USB-To-Serial Connection  ")
            AmbioSerialAction.triggered.connect(lambda: gdev_ambiomon.sendToSerial())

            deviceSubMenuAmbio  = deviceMenu.addMenu("Ambiomon Series")
            deviceSubMenuAmbio.setToolTipsVisible(True)
            deviceSubMenuAmbio.addAction(self.AmbioInfoAction)
            deviceSubMenuAmbio.addAction(self.AmbioInfoActionExt)
            deviceSubMenuAmbio.addAction(self.AmbioSetServerIP)
            deviceSubMenuAmbio.addAction(self.AmbioDataModeAction)
            deviceSubMenuAmbio.addAction(AmbioPingAction)
            deviceSubMenuAmbio.addAction(AmbioSerialAction)

    # submenu Gamma-Scout counter
        if gglobs.Devices["GammaScout"][ACTIV]  :

            self.GSInfoAction = QAction('Show Info', self, enabled=True)
            addMenuTip(self.GSInfoAction, 'Show basic info on GS device')
            self.GSInfoAction.triggered.connect(lambda: self.fprintDeviceInfo("GammaScout", extended = False))

            self.GSInfoActionExt = QAction('Show Extended Info', self, enabled=False)
            addMenuTip(self.GSInfoActionExt, 'Show extended info on GS device')
            self.GSInfoActionExt.triggered.connect(lambda: self.fprintDeviceInfo("GammaScout", extended = True))

            self.GSResetAction = QAction('Set to Normal Mode', self, enabled=False)
            addMenuTip(self.GSResetAction, 'Set the Gamma-Scout counter to its Normal Mode')
            self.GSResetAction.triggered.connect(lambda: gdev_gscout.GSsetMode("Normal"))

            self.GSSetPCModeAction = QAction('Set to PC Mode', self, enabled=False)
            addMenuTip(self.GSSetPCModeAction, 'Set the Gamma-Scout counter to its PC Mode')
            self.GSSetPCModeAction.triggered.connect(lambda: gdev_gscout.GSsetMode("PC"))

            self.GSDateTimeAction = QAction('Set Date+Time', self, enabled=False)
            addMenuTip(self.GSDateTimeAction, 'Set the Gamma-Scout counter clock to the computer time')
            self.GSDateTimeAction.triggered.connect(lambda: gdev_gscout.setGSDateTime())

            self.GSSetOnlineAction = QAction('Set to Online Mode ...', self, enabled=False)
            addMenuTip(self.GSSetOnlineAction, "Set the Gamma-Scout counter to its Online Mode\nAvailable only for 'Online' models")
            self.GSSetOnlineAction.triggered.connect(lambda: gdev_gscout.GSsetMode("Online"))

            self.GSRebootAction = QAction('Reboot', self, enabled=False)
            addMenuTip(self.GSRebootAction, "Do a Gamma-Scout reboot as warm-start\nAvailable only for 'Online' models")
            self.GSRebootAction.triggered.connect(lambda: gdev_gscout.GSreboot())

            deviceSubMenuGS  = deviceMenu.addMenu("Gamma-Scout Series")
            deviceSubMenuGS.setToolTipsVisible(True)
            deviceSubMenuGS.addAction(self.GSInfoAction)
            deviceSubMenuGS.addAction(self.GSInfoActionExt)
            deviceSubMenuGS.addAction(self.GSDateTimeAction)
            deviceSubMenuGS.addAction(self.GSResetAction)
            deviceSubMenuGS.addAction(self.GSSetPCModeAction)
            deviceSubMenuGS.addAction(self.GSSetOnlineAction)
            deviceSubMenuGS.addAction(self.GSRebootAction)

    # submenu I2C
        if gglobs.Devices["I2C"][ACTIV] :

            self.I2CInfoAction = QAction('Show Info', self, enabled=True)
            addMenuTip(self.I2CInfoAction, 'Show basic info on I2C device')
            self.I2CInfoAction.triggered.connect(lambda: self.fprintDeviceInfo("I2C", extended = False))

            self.I2CInfoActionExt = QAction('Show Extended Info', self, enabled=False)
            addMenuTip(self.I2CInfoActionExt, 'Show extended info on I2C device')
            self.I2CInfoActionExt.triggered.connect(lambda: self.fprintDeviceInfo("I2C", extended = True))

            self.I2CForceCalibAction = QAction('Calibrate CO2 Sensor', self, enabled=True)
            addMenuTip(self.I2CForceCalibAction, 'Force a CO2 calibration of the SCD41 sensor')
            self.I2CForceCalibAction.triggered.connect(lambda: gdev_i2c.forceCalibration())

            self.I2CScanAction = QAction('Scan I2C Bus', self, enabled=True)
            addMenuTip(self.I2CScanAction, 'Scan I2C bus for any sensors and report to NotePad (only when not-logging)')
            self.I2CScanAction.triggered.connect(lambda: gdev_i2c.scanI2CBus())

            self.I2CResetAction = QAction('Reset System', self, enabled=True)
            addMenuTip(self.I2CResetAction, 'Reset the I2C ELV dongle and attached sensors (only when not-logging)')
            self.I2CResetAction.triggered.connect(lambda: gdev_i2c.resetI2C())

            deviceSubMenuI2C  = deviceMenu.addMenu("I2C Series")
            deviceSubMenuI2C.setToolTipsVisible(True)
            deviceSubMenuI2C.addAction(self.I2CInfoAction)
            deviceSubMenuI2C.addAction(self.I2CInfoActionExt)
            deviceSubMenuI2C.addAction(self.I2CForceCalibAction)
            deviceSubMenuI2C.addAction(self.I2CScanAction)
            deviceSubMenuI2C.addAction(self.I2CResetAction)


    # submenu LabJack
        if gglobs.Devices["LabJack"][ACTIV]  :

            self.LJInfoAction = QAction('Show Info', self, enabled=True)
            addMenuTip(self.LJInfoAction, 'Show basic info on LabJack device')
            self.LJInfoAction.triggered.connect(lambda: self.fprintDeviceInfo("LabJack", extended = False))

            self.LJInfoActionExt = QAction('Show Extended Info', self, enabled=False)
            addMenuTip(self.LJInfoActionExt, 'Show extended info on LabJack device')
            self.LJInfoActionExt.triggered.connect(lambda: self.fprintDeviceInfo("LabJack", extended = True))

            deviceSubMenuLJ  = deviceMenu.addMenu("LabJack Series")
            deviceSubMenuLJ.setToolTipsVisible(True)
            deviceSubMenuLJ.addAction(self.LJInfoAction)
            deviceSubMenuLJ.addAction(self.LJInfoActionExt)


    # submenu MiniMon
        if gglobs.Devices["MiniMon"][ACTIV] :

            self.MiniMonInfoAction = QAction('Show Info', self, enabled=True)
            addMenuTip(self.MiniMonInfoAction, 'Show basic info on MiniMon device')
            self.MiniMonInfoAction.triggered.connect(lambda: self.fprintDeviceInfo("MiniMon", extended = False))

            deviceSubMenuMiniMon  = deviceMenu.addMenu("MiniMon Series")
            deviceSubMenuMiniMon.setToolTipsVisible(True)
            deviceSubMenuMiniMon.addAction(self.MiniMonInfoAction)


    # submenu Simul Device
        if gglobs.Devices["Simul"][ACTIV] :

            self.SimulInfoAction = QAction('Show Info', self, enabled=True)
            addMenuTip(self.SimulInfoAction, 'Show basic info on Simul device')
            self.SimulInfoAction.triggered.connect(lambda: self.fprintDeviceInfo("Simul", extended = False))

            self.SimulInfoActionExt = QAction('Show Extended Info', self, enabled=False)
            addMenuTip(self.SimulInfoActionExt, 'Show extended info on Simul device')
            self.SimulInfoActionExt.triggered.connect(lambda: self.fprintDeviceInfo("Simul", extended = True))

            self.SimulSettings = QAction("Set Properties ...", self, enabled=False)
            addMenuTip(self.SimulSettings, 'Set Simul Device Parameters for Meand and Prediction Limit')
            self.SimulSettings.triggered.connect(gdev_simul.getSimulProperties)

            deviceSubMenuSimul  = deviceMenu.addMenu("Simul Device Series")
            deviceSubMenuSimul.setToolTipsVisible(True)
            deviceSubMenuSimul.addAction(self.SimulInfoAction)
            deviceSubMenuSimul.addAction(self.SimulSettings)


    # submenu Manu
        if gglobs.Devices["Manu"][ACTIV]  :

            self.ManuInfoAction = QAction('Show Info', self, enabled=True)
            addMenuTip(self.ManuInfoAction, 'Show basic info on Manu device')
            self.ManuInfoAction.triggered.connect(lambda: self.fprintDeviceInfo("Manu", extended = False))

            self.ManuInfoActionExt = QAction('Show Extended Info', self, enabled=False)
            addMenuTip(self.ManuInfoActionExt, 'Show extended info on Manu device')
            self.ManuInfoActionExt.triggered.connect(lambda: self.fprintDeviceInfo("Manu", extended = True))

            self.ManuValAction = QAction('Enter Values Manually', self, enabled=True)
            addMenuTip(self.ManuValAction, "Enter Values Manually")
            self.ManuValAction.triggered.connect(gdev_manu.setManuValue)

            deviceSubMenuManu  = deviceMenu.addMenu("Manu Series")
            deviceSubMenuManu.setToolTipsVisible(True)
            deviceSubMenuManu.addAction(self.ManuInfoAction)
            #deviceSubMenuManu.addAction(self.ManuInfoActionExt)
            deviceSubMenuManu.addAction(self.ManuValAction)


    # submenu WiFiServer
        if gglobs.Devices["WiFiServer"][ACTIV] :

            self.WiFiInfoAction = QAction('Show Info', self, enabled=True)
            addMenuTip(self.WiFiInfoAction, 'Show basic info on WiFiServer device')
            self.WiFiInfoAction.triggered.connect(lambda: self.fprintDeviceInfo("WiFiServer", extended=False))

            # self.WiFiInfoActionExt = QAction('Show Extended Info', self, enabled=False)
            # addMenuTip(self.WiFiInfoActionExt, 'Show extended info on WiFiServer device')
            # self.WiFiInfoActionExt.triggered.connect(lambda: self.fprintDeviceInfo("WiFiServer", extended = True))

            # self.WiFiSettingsAction = QAction('Set WiFiServer Properties ...', self, enabled=True)
            # addMenuTip(self.WiFiSettingsAction, "Set properties like IP and data type")
            # self.WiFiSettingsAction.triggered.connect(gdev_wifiserver.setWiFiServerProperties)

            self.WiFiSettingsAction = QAction('Set WiFiServer Data Type ...', self, enabled=True)
            addMenuTip(self.WiFiSettingsAction, "Set data type LAST or AVG")
            self.WiFiSettingsAction.triggered.connect(gdev_wifiserver.setWiFiServerProperties)

            self.WiFiPingAction = QAction("Ping WiFiServer Device", self)
            addMenuTip(self.WiFiPingAction, 'Ping WiFiServer Device and report success or failure')
            self.WiFiPingAction.triggered.connect(lambda: gdev_wifiserver.pingWiFiServer())

            deviceSubMenuWiFi  = deviceMenu.addMenu("WiFiServer Series")
            deviceSubMenuWiFi.setToolTipsVisible(True)
            deviceSubMenuWiFi.addAction(self.WiFiInfoAction)
            # deviceSubMenuWiFi.addAction(self.WiFiInfoActionExt)
            deviceSubMenuWiFi.addAction(self.WiFiPingAction)
            deviceSubMenuWiFi.addAction(self.WiFiSettingsAction)


    # submenu WiFiClient
        if gglobs.Devices["WiFiClient"][ACTIV]  :

            self.WiFiClientInfoAction = QAction('Show Info', self, enabled=True)
            addMenuTip(self.WiFiClientInfoAction, 'Show basic info on WiFiClient device')
            self.WiFiClientInfoAction.triggered.connect(lambda: self.fprintDeviceInfo("WiFiClient", extended=False))

            # self.WiFiClientInfoActionExt = QAction('Show Extended Info', self, enabled=False)
            # addMenuTip(self.WiFiClientInfoActionExt, 'Show extended info on WiFiClient device')
            # self.WiFiClientInfoActionExt.triggered.connect(lambda: self.fprintDeviceInfo("WiFiClient", extended = True))

            # self.WiFiClientSettingsAction = QAction('Set WiFiClient Properties ...', self, enabled=True)
            # addMenuTip(self.WiFiClientSettingsAction, "Set properties like IP and data type")
            # self.WiFiClientSettingsAction.triggered.connect(gdev_wificlient.setWiFiClientProperties)

            deviceSubMenuWiFiClient  = deviceMenu.addMenu("WiFiClient Series")
            deviceSubMenuWiFiClient.setToolTipsVisible(True)
            deviceSubMenuWiFiClient.addAction(self.WiFiClientInfoAction)
            # deviceSubMenuWiFiClient.addAction(self.WiFiClientInfoActionExt)       # presently no extended info
            # deviceSubMenuWiFiClient.addAction(self.WiFiClientSettingsAction)



    # widgets for device in toolbar
        devBtnSize = 65

        # !!! MUST NOT have a colon ':' after QPushButton !!!
        self.dbtnStyleSheetON    = "QPushButton {margin-right:5px; background-color: #12cc3d; border-radius: 2px; border:1px solid silver; color: black; font-size:14px; font-weight:bold}"
        self.dbtnStyleSheetOFF   = "QPushButton {margin-right:5px;  }"
        self.dbtnStyleSheetError = "QPushButton {margin-right:5px; background-color: #ff3333; border-radius: 2px; border:1px solid silver; color: black; font-size:14px; font-weight:bold}"

        self.dbtnGMCPower = QPushButton()
        self.dbtnGMCPower.setIcon(QIcon(QPixmap(os.path.join(gglobs.gresPath, 'icon_power-round_off.png'))))
        self.dbtnGMCPower.setFixedSize(32, 33)
        self.dbtnGMCPower.setEnabled(False)
        self.dbtnGMCPower.setStyleSheet("QPushButton {margin-right:1px; border:0px; }")
        self.dbtnGMCPower.setIconSize(QSize(31, 31))
        self.dbtnGMCPower.setToolTip ('Toggle GMC Device Power ON / OFF')
        self.dbtnGMCPower.setAutoFillBackground(True) # This is important!! Why???
        self.dbtnGMCPower.clicked.connect(lambda: self.toggleGMCPower())

        self.connectTextGMC = 'GMC'
        self.dbtnGMC = QPushButton(self.connectTextGMC)
        self.dbtnGMC.setFixedSize(devBtnSize, 32)
        self.dbtnGMC.setToolTip("GMC Device - Turns green once a connection is made - click for info")
        self.dbtnGMC.setStyleSheet(self.dbtnStyleSheetOFF)
        self.dbtnGMC.setAutoFillBackground(True) # This is important!! Why???
        self.dbtnGMC.clicked.connect(lambda: self.fprintDeviceInfo("GMC", extended=False))

        self.connectTextAudio = 'Audio'
        self.dbtnAudio =  QPushButton(self.connectTextAudio)
        self.dbtnAudio.setFixedSize(devBtnSize, 32)
        self.dbtnAudio.setToolTip("AudioCounter Device - Turns green once a connection is made - click for info")
        self.dbtnAudio.setStyleSheet(self.dbtnStyleSheetOFF)
        self.dbtnAudio.setAutoFillBackground(True)
        self.dbtnAudio.clicked.connect(lambda: self.fprintDeviceInfo(self.connectTextAudio, extended = False))

        self.connectTextRM = 'RadM'
        self.dbtnRM =  QPushButton(self.connectTextRM)
        self.dbtnRM.setFixedSize(devBtnSize,32)
        self.dbtnRM.setToolTip("RadMon Device - Turns green once a connection is made - click for info")
        self.dbtnRM.setStyleSheet(self.dbtnStyleSheetOFF)
        self.dbtnRM.setAutoFillBackground(True)
        self.dbtnRM.clicked.connect(lambda: self.fprintDeviceInfo("RadMon"))

        self.connectTextAmbio = 'Ambio'
        self.dbtnAmbio =  QPushButton(self.connectTextAmbio)
        self.dbtnAmbio.setFixedSize(devBtnSize, 32)
        self.dbtnAmbio.setToolTip("Manu Device - Turns green once a connection is made - click for info")
        self.dbtnAmbio.setStyleSheet(self.dbtnStyleSheetOFF)
        self.dbtnAmbio.setAutoFillBackground(True)
        self.dbtnAmbio.clicked.connect(lambda: self.fprintDeviceInfo("AmbioMon"))

        self.connectTextWiFi = 'WiFiS'
        self.dbtnWServer = QPushButton(self.connectTextWiFi)
        self.dbtnWServer.setFixedSize(devBtnSize, 32)
        self.dbtnWServer.setToolTip("WiFiServer Device - Turns green once a connection is made - click for info")
        self.dbtnWServer.setStyleSheet(self.dbtnStyleSheetOFF)
        self.dbtnWServer.setAutoFillBackground(True)
        self.dbtnWServer.clicked.connect(lambda: self.fprintDeviceInfo("WiFiServer"))

        self.connectTextServ = 'WiFiC'
        self.dbtnWClient = QPushButton(self.connectTextServ)
        self.dbtnWClient.setFixedSize(devBtnSize, 32)
        self.dbtnWClient.setToolTip("WiFiClient Device - Turns green once a connection is made - click for info")
        self.dbtnWClient.setStyleSheet(self.dbtnStyleSheetOFF)
        self.dbtnWClient.setAutoFillBackground(True)
        self.dbtnWClient.clicked.connect(lambda: self.fprintDeviceInfo("WiFiClient"))

        # self.connectTextGS = 'GS'
        self.connectTextGS = 'GScout'
        self.dbtnGS =  QPushButton(self.connectTextGS)
        self.dbtnGS.setFixedSize(devBtnSize, 32)
        self.dbtnGS.setToolTip("GS Device - Turns green once a connection is made - click for info")
        self.dbtnGS.setStyleSheet(self.dbtnStyleSheetOFF)
        self.dbtnGS.setAutoFillBackground(True)
        self.dbtnGS.clicked.connect(lambda: self.fprintDeviceInfo("GammaScout"))

        self.connectTextI2C = 'I2C'
        self.dbtnI2C =  QPushButton(self.connectTextI2C)
        self.dbtnI2C.setFixedSize(devBtnSize, 32)
        self.dbtnI2C.setToolTip("I2C Device - Turns green once a connection is made - click for info")
        self.dbtnI2C.setStyleSheet(self.dbtnStyleSheetOFF)
        self.dbtnI2C.setAutoFillBackground(True)
        self.dbtnI2C.clicked.connect(lambda: self.fprintDeviceInfo("I2C" ))

        self.connectTextLJ = 'LabJck'
        self.dbtnLJ =  QPushButton(self.connectTextLJ)
        self.dbtnLJ.setFixedSize(devBtnSize, 32)
        self.dbtnLJ.setToolTip("LabJack Device - Turns green once a connection is made - click for info")
        self.dbtnLJ.setStyleSheet(self.dbtnStyleSheetOFF)
        self.dbtnLJ.setAutoFillBackground(True)
        self.dbtnLJ.clicked.connect(lambda: self.fprintDeviceInfo("LabJack"))

        self.connectTextManu = 'Manu'
        self.dbtnManu = QPushButton(self.connectTextManu)
        self.dbtnManu.setFixedSize(devBtnSize, 32)
        self.dbtnManu.setToolTip("Manu Device - Turns green once a connection is made - click for info")
        self.dbtnManu.setStyleSheet(self.dbtnStyleSheetOFF)
        self.dbtnManu.setAutoFillBackground(True)
        self.dbtnManu.clicked.connect(lambda: self.fprintDeviceInfo("Manu"))

        self.connectTextSimul = 'Simul'
        self.dbtnSimul =  QPushButton(self.connectTextSimul)
        self.dbtnSimul.setFixedSize(devBtnSize, 32)
        self.dbtnSimul.setToolTip("Simul Device - Turns green once a connection is made - click for info")
        self.dbtnSimul.setStyleSheet(self.dbtnStyleSheetOFF)
        self.dbtnSimul.setAutoFillBackground(True)
        self.dbtnSimul.clicked.connect(lambda: self.fprintDeviceInfo(self.connectTextSimul))

        self.connectTextMiniMon = 'MiniM'
        self.dbtnMiniMon = QPushButton(self.connectTextMiniMon)
        self.dbtnMiniMon.setFixedSize(devBtnSize, 32)
        self.dbtnMiniMon.setToolTip("MiniMon Device - Turns green once a connection is made - click for info")
        self.dbtnMiniMon.setStyleSheet(self.dbtnStyleSheetOFF)
        self.dbtnMiniMon.setAutoFillBackground(True)
        self.dbtnMiniMon.clicked.connect(lambda: self.fprintDeviceInfo("MiniMon"))

    # toolbar Devices
        toolbar = self.addToolBar('Devices')
        toolbar.setToolTip("Devices Toolbar")
        toolbar.setIconSize(QSize(32,32))    # standard size is too small

        toolbar.addAction(self.toggleDeviceConnectionAction) # Connect icon
        toolbar.addWidget(QLabel("   "))                # spacer

        if gglobs.Devices["GMC"][ACTIV]         : toolbar.addWidget(self.dbtnGMCPower)        # GMC power icon
        if gglobs.Devices["GMC"][ACTIV]         : toolbar.addWidget(self.dbtnGMC)             # GMC device display
        if gglobs.Devices["Audio"][ACTIV]       : toolbar.addWidget(self.dbtnAudio)           # AudioCounter device display
        if gglobs.Devices["RadMon"][ACTIV]      : toolbar.addWidget(self.dbtnRM)              # RadMon device display
        if gglobs.Devices["AmbioMon"][ACTIV]    : toolbar.addWidget(self.dbtnAmbio)           # Manu device display
        if gglobs.Devices["GammaScout"][ACTIV]  : toolbar.addWidget(self.dbtnGS)              # Gamma-Scout device display
        if gglobs.Devices["I2C"][ACTIV]         : toolbar.addWidget(self.dbtnI2C)             # I2C device display
        if gglobs.Devices["LabJack"][ACTIV]     : toolbar.addWidget(self.dbtnLJ)              # LabJack device display
        if gglobs.Devices["MiniMon"][ACTIV]     : toolbar.addWidget(self.dbtnMiniMon)         # MiniMon device display
        if gglobs.Devices["Simul"][ACTIV]       : toolbar.addWidget(self.dbtnSimul)           # Simul device display
        if gglobs.Devices["Manu"][ACTIV]        : toolbar.addWidget(self.dbtnManu)            # Manu device display
        if gglobs.Devices["WiFiClient"][ACTIV]  : toolbar.addWidget(self.dbtnWClient)         # WiFiClient device display
        if gglobs.Devices["WiFiServer"][ACTIV]  : toolbar.addWidget(self.dbtnWServer)         # WiFiServer device display

#Log Menu
        self.logLoadFileAction = QAction(QIcon(QPixmap(os.path.join(gglobs.gresPath, 'icon_Log_DB.svg.png'))), 'Get Log from Database or Create New One ...', self)
        self.logLoadFileAction.setShortcut('Ctrl+L')
        addMenuTip(self.logLoadFileAction, 'Load or Create database for logging, and plot')
        self.logLoadFileAction.triggered.connect(lambda: self.getFileLog(source="Database"))

        self.logLoadCSVAction = QAction(QIcon(QPixmap(os.path.join(gglobs.gresPath, 'icon_Log_CSV.svg.png'))), 'Get Log from CSV File ...', self)
        addMenuTip(self.logLoadCSVAction, 'Load existing *.log or other CSV file, convert to database, and plot')
        self.logLoadCSVAction.triggered.connect(lambda: self.getFileLog(source="CSV File"))

        self.startloggingAction = QAction(QIcon(QPixmap(os.path.join(gglobs.gresPath, 'icon_log_start.png'))), 'Start Logging', self, enabled=False)
        addMenuTip(self.startloggingAction, 'Start logging from devices')
        self.startloggingAction.triggered.connect(self.startLogging)

        self.stoploggingAction = QAction(QIcon(QPixmap(os.path.join(gglobs.gresPath, 'icon_log_stop.png'))), 'Stop Logging', self, enabled=False)
        addMenuTip(self.stoploggingAction, 'Stop logging from devices')
        self.stoploggingAction.triggered.connect(self.stopLogging)

        # add comment
        self.addCommentAction = QAction('Add Comment to Log ...', self, enabled=False)
        addMenuTip(self.addCommentAction, 'Add a comment to the current log')
        self.addCommentAction.triggered.connect(lambda: self.addComment("Log"))

        self.showLogDataAction = QAction('Show Log Data', self)
        addMenuTip(self.showLogDataAction, 'Show all records from current log')
        self.showLogDataAction.triggered.connect(lambda: self.showData("Log", full=True))

        self.showLogTagsAction = QAction('Show Log Data Tags/Comments', self)
        addMenuTip(self.showLogTagsAction, 'Show only records from current log containing tags or comments')
        self.showLogTagsAction.triggered.connect(lambda: self.showDBTags("Log"))

        self.showLogExcerptAction = QAction('Show Log Data Excerpt', self)
        addMenuTip(self.showLogExcerptAction, 'Show first and last few records of current log')
        self.showLogExcerptAction.triggered.connect(lambda: self.showData("Log", full=False))

        self.quickLogAction = QAction(QIcon(QPixmap(os.path.join(gglobs.gresPath, 'icon_quick_log.png'))), 'Quick Log', self, enabled=False)
        addMenuTip(self.quickLogAction, 'One-click log. Saves always into database default.logdb; will be overwritten on next Quick Log click')
        self.quickLogAction.triggered.connect(self.quickLog)

        self.logSnapAction = QAction(QIcon(QPixmap(os.path.join(gglobs.gresPath, 'icon_log_snap.png'))), 'Snap a new log record', self, enabled=False)
        addMenuTip(self.logSnapAction, 'Get a new log record immediately')
        self.logSnapAction.triggered.connect(self.snapLogValue)

        self.setLogTimingAction = QAction('Set Log Cycle ...', self, enabled=True)
        self.setLogTimingAction.setIcon(QIcon(QPixmap(os.path.join(gglobs.gresPath, 'icon_log_options.png'))))
        addMenuTip(self.setLogTimingAction, 'Set Log Cycle in seconds')
        self.setLogTimingAction.triggered.connect(self.setLogCycle)

        self.logSaveCSVAction = QAction('Save Log Data into CSV file', self)
        addMenuTip(self.logSaveCSVAction, "Save all records from current log into a CSV file with extension 'csv'")
        self.logSaveCSVAction.triggered.connect(lambda: gsup_sql.saveDataToCSV("Log", full= True))

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
        self.loadHistDBAction.triggered.connect(lambda: self.getFileHistory("Database"))

        # load from CSV file
        self.loadHistHisAction = QAction(QIcon(QPixmap(os.path.join(gglobs.gresPath, 'icon_hist_CSV.svg.png'))), 'Get History from CSV File ...', self)
        addMenuTip(self.loadHistHisAction, 'Load existing *.his or other CSV file, convert to database file, and plot')
        self.loadHistHisAction.triggered.connect(lambda: self.getFileHistory("Parsed File"))

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
        if gglobs.Devices["GMC"][ACTIV] :
            # get his from device
            self.histGMCDeviceAction = QAction(QIcon(QPixmap(os.path.join(gglobs.gresPath, 'icon_hist_device_active.png'))), 'Get History from Device ...', self, enabled=False)
            addMenuTip(self.histGMCDeviceAction, 'Load history data from any GMC device, create database, and plot')
            self.histGMCDeviceAction.triggered.connect(lambda: self.getFileHistory("Device"))

            # get his from bin file
            self.loadHistBinAction = QAction(QIcon(QPixmap(os.path.join(gglobs.gresPath, 'icon_hist_bin_active.png'))), 'Get History from GMC Binary File ...', self)
            addMenuTip(self.loadHistBinAction, 'Load history data from a GMC format binary file and plot')
            self.loadHistBinAction.triggered.connect(lambda: self.getFileHistory("Binary File"))

            # show bin data bytecount
            self.showHistBinDataDetailAction = QAction('Show History Binary Data Bytecount', self)
            addMenuTip(self.showHistBinDataDetailAction, 'Show counts of bytes in history binary data')
            self.showHistBinDataDetailAction.triggered.connect(lambda: gdev_gmc_hist.fprintHistDetails())

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
            addMenuTip(self.historyFFAction, "Show History Binary Data as a map highlighting the locations of bytes with FF value (FF=empty value)")
            self.historyFFAction.triggered.connect(lambda: gsup_sql.createByteMapFromDB(0xFF))

            # show AA map
            self.historyAAAction = QAction("Show History Binary Data as AA Map", self)
            addMenuTip(self.historyAAAction, "Show History Binary Data as a map highlighting the locations of bytes with AA value (AA=DateTime String)")
            self.historyAAAction.triggered.connect(lambda: gsup_sql.createByteMapFromDB(0xAA))

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
            historySubMenuGMC.addAction(self.historyAAAction)
            historySubMenuGMC.addAction(self.historyFFAction)

            historySubMenuGMC.addSeparator()
            historySubMenuGMC.addAction(self.showHistBinDataSaveAction)
            #historyMenu.triggered[QAction].connect(self.processtrigger)


    # valid for Gamma-Scout only
        if gglobs.Devices["GammaScout"][ACTIV]:
            self.histGSDeviceAction = QAction(QIcon(QPixmap(os.path.join(gglobs.gresPath, 'icon_hist_device_active.png'))), 'Get History from Device ...', self, enabled=False)
            addMenuTip(self.histGSDeviceAction, 'Load history data from any Gamma-Scout device, create database, and plot')
            self.histGSDeviceAction.triggered.connect(lambda: self.getFileHistory("GSDevice"))

            self.histGSDatFileAction = QAction(QIcon(QPixmap(os.path.join(gglobs.gresPath, 'icon_hist_device_active.png'))), 'Get History from Gamma-Scout Dat File ...', self)
            addMenuTip(self.histGSDatFileAction, 'Load history data from a Gamma-Scout dat file, create database, and plot')
            self.histGSDatFileAction.triggered.connect(lambda: self.getFileHistory("GSDatFile"))

            self.showHistDatDataAction = QAction('Show History Dat Data', self)
            addMenuTip(self.showHistDatDataAction, 'Show the history data in Gamma-Scout like *.dat file')
            self.showHistDatDataAction.triggered.connect(lambda: gdev_gscout.GSshowDatData())

            self.showHistDatDataSaveAction = QAction('Save History Data to Dat File', self)
            addMenuTip(self.showHistDatDataSaveAction, 'Save the history data as Gamma-Scout *.dat format')
            self.showHistDatDataSaveAction.triggered.connect(lambda: gdev_gscout.GSsaveDatDataToDatFile())

            historySubMenuGS = historyMenu.addMenu("Gamma Scout Series")
            historySubMenuGS.setToolTipsVisible(True)

            historySubMenuGS.addAction(self.histGSDeviceAction)
            historySubMenuGS.addAction(self.histGSDatFileAction)

            historySubMenuGS.addSeparator()
            historySubMenuGS.addAction(self.showHistDatDataAction)

            historySubMenuGS.addSeparator()
            historySubMenuGS.addAction(self.showHistDatDataSaveAction)


    # valid for AmbioMon only
        if gglobs.Devices["AmbioMon"][ACTIV] :
            self.histAMDeviceCAMAction = QAction(QIcon(QPixmap(os.path.join(gglobs.gresPath, 'icon_hist_device_active.png'))), 'Get History Binary CAM data from Device', self, enabled=False)
            addMenuTip(self.histAMDeviceCAMAction, 'Load Counter & Ambient history data from AmbioMon device, create database, and plot')
            self.histAMDeviceCAMAction.triggered.connect(lambda: self.getFileHistory("AMDeviceCAM"))

            self.histAMDeviceCPSAction = QAction(QIcon(QPixmap(os.path.join(gglobs.gresPath, 'icon_hist_device_active.png'))), 'Get History Binary CPS data from Device', self, enabled=False)
            addMenuTip(self.histAMDeviceCPSAction, 'Load Counts Per Second history data from AmbioMon device, create database, and plot')
            self.histAMDeviceCPSAction.triggered.connect(lambda: self.getFileHistory("AMDeviceCPS"))

            self.histAMCAMFileAction = QAction(QIcon(QPixmap(os.path.join(gglobs.gresPath, 'icon_hist_device_active.png'))), 'Get History Binary CAM data from File ...', self)
            addMenuTip(self.histAMCAMFileAction, 'Load history data from an AmbioMon CAM file, create database, and plot')
            self.histAMCAMFileAction.triggered.connect(lambda: self.getFileHistory("AMFileCAM"))

            self.histAMCPSFileAction = QAction(QIcon(QPixmap(os.path.join(gglobs.gresPath, 'icon_hist_device_active.png'))), 'Get History Binary CPS data from File ...', self)
            addMenuTip(self.histAMCPSFileAction, 'Load history data from an AmbioMon CPS file, create database, and plot')
            self.histAMCPSFileAction.triggered.connect(lambda: self.getFileHistory("AMFileCPS"))

            #~ self.showHistDatDataAction = QAction('Show History Raw Data', self)
            #~ addMenuTip(self.showHistDatDataAction, 'Show the history data in Manu like *.dat file')
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
        self.showHistHisTagsAction.triggered.connect(lambda: self.showDBTags("History"))

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
        self.histSaveCSVAction.triggered.connect(lambda: gsup_sql.saveDataToCSV("His", full=True))

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
        # menu entry and toolbar button for Show IP Address
        self.IPAddrAction = QAction('Show IP Status', self, enabled=True)
        self.IPAddrAction.setIcon(QIcon(QPixmap(os.path.join(gglobs.gresPath, 'icon_ip_address.png'))))
        addMenuTip(self.IPAddrAction, "Show GeigerLog's current IP Address and Ports in use")
        self.IPAddrAction.triggered.connect(lambda: self.showIPStatus())

        # menu entry and toolbar button for Web Server access
        self.MonServerAction = QAction('Set up Monitor Server ...', self, enabled=True)
        self.MonServerAction.setIcon(QIcon(QPixmap(os.path.join(gglobs.gresPath, 'icon_monserver_inactive.png'))))
        addMenuTip(self.MonServerAction, "Set Properties of Monitor Server")
        self.MonServerAction.triggered.connect(lambda: gweb_monserv.initMonServer())

        # # menu entry and toolbar button for Telegram access
        # self.TelegramAction = QAction(QIcon(QPixmap(os.path.join(gglobs.gresPath, 'icon_Telegram_inactive.png'))), 'Set up Telegram Messenger ...', self, enabled=True)
        # addMenuTip(self.TelegramAction, 'Set Properties of Telegram Messenger Updating')
        # self.TelegramAction.triggered.connect(lambda: gsup_tools.setupTelegram())

        # menu entry and toolbar button for GMC Map access
        self.GMCmapAction = QAction('Set up Radiation World Map ...', self, enabled=True)
        self.GMCmapAction.setIcon(QIcon(QPixmap(os.path.join(gglobs.gresPath, 'icon_world_v2_inactive.png'))))
        addMenuTip(self.GMCmapAction, 'Set Properties of Radiation World Map Updating')
        self.GMCmapAction.triggered.connect(lambda: setupRadWorldMap())

        webMenu = self.menubar.addMenu('&Web')
        webMenu.setToolTipsVisible(True)
        webMenu.addAction(self.IPAddrAction)
        webMenu.addAction(self.MonServerAction)
        # webMenu.addAction(self.TelegramAction)
        webMenu.addAction(self.GMCmapAction)

        toolbar = self.addToolBar('Web')
        toolbar.setToolTip("Web Toolbar")
        toolbar.setIconSize(QSize(32,32))  # standard size is too small
        toolbar.addAction(self.IPAddrAction)
        toolbar.addAction(self.MonServerAction)
        # toolbar.addAction(self.TelegramAction)
        toolbar.addAction(self.GMCmapAction)

# Tools menu
        # menu entry and toolbar button for tools

        PlotLogAction = QAction('Plot Full Log', self)
        addMenuTip(PlotLogAction, 'Plot the complete Log file')
        PlotLogAction.triggered.connect(lambda: self.plotGraph('Log', full=False))

        PlotHisAction = QAction('Plot Full History', self)
        addMenuTip(PlotHisAction, 'Plot the complete History file')
        PlotHisAction.triggered.connect(lambda: self.plotGraph('His', full=False))

        fprintSuStAction =  QAction('Show SuSt (Summary Statistics) of Plot Data ', self)
        addMenuTip(fprintSuStAction, "Shows Summary Statistics of all variables and data in the plot")
        fprintSuStAction.triggered.connect(lambda: gsup_tools.fprintSuSt())

        showStatsAction =  QAction('Show Statistics of Plot Data ', self)
        addMenuTip(showStatsAction, "Shows the Statistics of the data in the current plot")
        showStatsAction.triggered.connect(lambda: gsup_tools.showStats())

        PlotScatterAction = QAction('Show Scatterplot from Plot Data ...', self)
        addMenuTip(PlotScatterAction, 'Show an X-Y Scatter plot with optional polynomial fit, using data in the plot')
        PlotScatterAction.triggered.connect(lambda: gsup_tools.selectScatterPlotVars())

        PlotPoissonAction =  QAction("Show Poisson Test of Plot Data", self)
        addMenuTip(PlotPoissonAction, "Shows a Poisson curve on a histogram of the data in the plot for the selected variable")
        PlotPoissonAction.triggered.connect(lambda: gstat_poisson.plotPoisson())

        PlotFFTAction =  QAction("Show FFT && Autocorrelation of Plot Data", self)
        addMenuTip(PlotFFTAction, "Shows the FFT Spectra & an Autocorrelation of the data in the plot for the selected variable")
        PlotFFTAction.triggered.connect(lambda: gstat_fft.plotFFT())

        editScalingAction = QAction('Scaling ...', self)
        addMenuTip(editScalingAction, "Scaling - View and edit current settings for value- and graph-scaling")
        editScalingAction.triggered.connect(lambda: self.editScaling())

        SaveGraph2FileAction = QAction("Save Graph to File", self)
        addMenuTip(SaveGraph2FileAction, "Save the graph as a 'PNG' file")
        SaveGraph2FileAction.triggered.connect(lambda: saveGraphToFile())

        fprintPlotDataAction = QAction('Show Plot Data', self)
        addMenuTip(fprintPlotDataAction, 'Show the DateTime and values of all variables as currently selected in Plot')
        fprintPlotDataAction.triggered.connect(lambda: self.showData("PlotData"))

        DisplayLastValAction = QAction('Display Last Values', self)
        addMenuTip(DisplayLastValAction, 'Show a table with the variables and their last value, including scaled value')
        DisplayLastValAction.triggered.connect(lambda: gsup_tools.displayLastValues())

        self.DeviceSetUSBportAction = QAction('Set Port ...', self)
        self.DeviceSetUSBportAction.setIcon(QIcon(QPixmap(os.path.join(gglobs.gresPath, 'icon_SetPort.png'))))
        addMenuTip(self.DeviceSetUSBportAction, 'Show all available USB-to-Serial Ports and allow selection of port and setting of baudrate for each device')
        self.DeviceSetUSBportAction.triggered.connect(self.setSerialPort)

        self.GMCDevicePortDiscoveryAction = QAction('GMC', self)
        addMenuTip(self.GMCDevicePortDiscoveryAction, 'Find the USB Port connected to a GMC Geiger counter and its Baudrate automatically')
        self.GMCDevicePortDiscoveryAction.triggered.connect(lambda: autoDiscoverUSBPort("GMC"))
        if not gglobs.Devices["GMC"][ACTIV]:
            self.GMCDevicePortDiscoveryAction.setEnabled(False)

        self.I2CDevicePortDiscoveryAction = QAction('I2C', self)
        addMenuTip(self.I2CDevicePortDiscoveryAction, 'Find the USB Port connected to an I2C device and its Baudrate automatically')
        self.I2CDevicePortDiscoveryAction.triggered.connect(lambda: autoDiscoverUSBPort("I2C"))
        if not gglobs.Devices["I2C"][ACTIV]:
            self.I2CDevicePortDiscoveryAction.setEnabled(False)

        self.GSDevicePortDiscoveryAction = QAction('GS', self)
        addMenuTip(self.GSDevicePortDiscoveryAction, 'Find the USB Port connected to a Gamma-Scout Geiger counter and its Baudrate automatically')
        self.GSDevicePortDiscoveryAction.triggered.connect(lambda: autoDiscoverUSBPort("GS"))
        if not gglobs.Devices["GammaScout"][ACTIV]:
            self.GSDevicePortDiscoveryAction. setEnabled(False)


        toolsMenu = self.menubar.addMenu('&Tools')
        toolsMenu.setToolTipsVisible(True)

        toolsMenu.addAction(PlotLogAction)
        toolsMenu.addAction(PlotHisAction)

        # toolsMenu.addSeparator()
        # toolsMenu.addAction(fprintPlotDataAction)

        toolsMenu.addSeparator()
        toolsMenu.addAction(fprintSuStAction)
        toolsMenu.addAction(showStatsAction)
        toolsMenu.addAction(PlotScatterAction)
        toolsMenu.addAction(PlotPoissonAction)
        toolsMenu.addAction(PlotFFTAction)

        toolsMenu.addSeparator()
        toolsMenu.addAction(editScalingAction)
        toolsMenu.addAction(SaveGraph2FileAction)
        toolsMenu.addAction(fprintPlotDataAction)
        toolsMenu.addAction(DisplayLastValAction)

        toolsMenu.addSeparator()
        toolsMenu.addAction(self.DeviceSetUSBportAction)

        toolsSubMenu = toolsMenu.addMenu("Autodiscover Port for Device")
        toolsSubMenu.setToolTipsVisible(True)
        toolsSubMenu.addAction(self.GMCDevicePortDiscoveryAction)
        toolsSubMenu.addAction(self.I2CDevicePortDiscoveryAction)
        toolsSubMenu.addAction(self.GSDevicePortDiscoveryAction)

        toolbar = self.addToolBar('Tools')
        toolbar.setToolTip("Tools Toolbar")
        toolbar.setIconSize(QSize(32,32))  # standard size is too small
        toolbar.addAction(self.DeviceSetUSBportAction)


#Help Menu
        # menu entries for Help
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
        #helpMenu.addAction(self.helpAboutQTAction)
        helpMenu.addAction(self.helpAboutAction)
        #helpMenu.triggered[QAction].connect(self.processtrigger)


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

            develLogClickAction = QAction("Toggle Click Sound for Log Calls", self)
            develLogClickAction.triggered.connect(lambda: self.toggleLogClick())

            # SaveRepairLogAction = QAction('Repair DateTime and Save Data into *.log file (CSV)', self)
            # addMenuTip(SaveRepairLogAction, "Repair all records from current log and save into a CSV file with extension 'log'")
            # SaveRepairLogAction.triggered.connect(lambda: gsup_sql.saveRepairData("Log", full= True))

            # SaveRepairHisAction = QAction('Repair DateTime and Save Data into *.his file (CSV)', self)
            # addMenuTip(SaveRepairHisAction, "Repair all records from current log and save into a CSV file with extension 'his'")
            # SaveRepairHisAction.triggered.connect(lambda: gsup_sql.saveRepairData("His", full= True))

            develAudioAction = QAction("Show Audio Signal", self)
            develAudioAction.triggered.connect(lambda: gdev_audio.showLiveAudioSignal())

            develFixAudioAction = QAction("Fix garbled audio", self)
            develFixAudioAction.triggered.connect(lambda: fixGarbledAudio())

            # MonitorAction = QAction('Show Monitor', self)
            # addMenuTip(MonitorAction, 'Show a Monitor ')
            # MonitorAction.triggered.connect(lambda: gsup_tools.plotMonitor())

            # pggraphAction = QAction('Show PgGraph', self)
            # addMenuTip(pggraphAction, 'Show a pg graph comparison ')
            # pggraphAction.triggered.connect(lambda: gsup_tools.plotpgGraph())


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
            # develMenu.addAction(SaveRepairLogAction)
            # develMenu.addAction(SaveRepairHisAction)
            develMenu.addAction(develAudioAction)
            develMenu.addAction(develLogClickAction)
            # develMenu.addAction(MonitorAction)
            # develMenu.addAction(pggraphAction)

            if "LINUX" in platform.platform().upper():
                develMenu.addAction(develFixAudioAction)


# add navigation toolbar as last toolbar
        self.addToolBar(self.navtoolbar)

# DataOptions
# row Data
        BigButtonWidth  = 110
        PlotButtonWidth = 50
        col0width       = 70

    # col 0
        # labels and entry fields
        dltitle  = QLabel("Data")
        dltitle.setFont(self.fatfont)
        # dllog=QLabel("Log:")
        # dlhist=QLabel("History:")
        dlDevice  = QLabel("Device")
        dlDevice.setFont(self.fatfont)

    # col 1
        dbtnPlotLog =  QPushButton('Plot Log')
        dbtnPlotLog.setFixedWidth(col0width)
        dbtnPlotLog.setToolTip("Plot the Log File with Default settings")
        dbtnPlotLog.clicked.connect(lambda: self.plotGraph('Log', full=False))

        dbtnPlotHis =  QPushButton('Plot Hist')
        dbtnPlotHis.setFixedWidth(col0width)
        dbtnPlotHis.setToolTip("Plot the History File with Default settings")
        dbtnPlotHis.clicked.connect(lambda: self.plotGraph('His', full=False))

    # col 2, 3, 4
        # dlcf     = QLabel("Database Files")
        # dlcf.setAlignment(Qt.AlignCenter)

        self.dcfLog=QLineEdit()
        self.dcfLog.setReadOnly(True)
        self.dcfLog.setStyleSheet("QLineEdit { background-color: #DFDEDD; color: rgb(80,80,80); }")
        self.dcfLog.setToolTip('The full path of the Log-File if any is loaded')
        # self.dcfLog.setMinimumWidth(450)

        self.dcfHis=QLineEdit()
        self.dcfHis.setReadOnly(True)
        self.dcfHis.setStyleSheet("QLineEdit { background-color : #DFDEDD; color : rgb(80,80,80); }")
        self.dcfHis.setToolTip('The full path of the History-File if any is loaded')
        # self.dcfHis.setMinimumWidth(450)

    # col 5
        # vertical line

    # col 6
        # Geiger Tubes
        self.dtube  = QPushButton("Geiger Tubes")
        self.dtube.setToolTip("Set sensitivities for all Geiger tubes temporarily")
        self.dtube.setFixedWidth(BigButtonWidth)
        self.dtube.clicked.connect(self.setTemporaryTubeSensitivities)

        # button: Mapping
        self.btnMapping = QPushButton('Dev Mapping')
        self.btnMapping.setFixedWidth(BigButtonWidth)
        self.btnMapping.setEnabled(True)
        self.btnMapping.setToolTip('Show Device Mappings')
        self.btnMapping.clicked.connect(lambda: self.showDeviceMappings())


# Row Data
        DataButtonWidth = BigButtonWidth + 35

    # # button Scaling
    #     self.btnSetScaling =  QPushButton('Scaling')
    #     self.btnSetScaling.clicked.connect(self.editScaling)
    #     self.btnSetScaling.setFixedWidth(DataButtonWidth)
    #     self.btnSetScaling.setToolTip("Scaling - View and edit current settings for value- and graph-scaling")

    # button: add comment
        self.btnAddComment = QPushButton('Add Comment')
        self.btnAddComment.setFixedWidth(DataButtonWidth)
        self.btnAddComment.setEnabled(False)
        self.btnAddComment.setToolTip('Add a comment to current database file')
        self.btnAddComment.clicked.connect(lambda: self.addComment("Current"))

    # button: Log Cycle
        self.btnSetCycle = QPushButton()
        self.btnSetCycle.setFixedWidth(DataButtonWidth)
        self.btnSetCycle.setToolTip('Current setting of log cycle in seconds')
        self.btnSetCycle.setStyleSheet("QPushButton {}")
        self.btnSetCycle.clicked.connect(self.setLogCycle)

        DataLayout = QHBoxLayout()
        # DataLayout.addStretch()
        # graphOptions.addWidget(btnSetScaling,   row, 3)
        # DataLayout.addWidget(self.btnSetScaling)
        DataLayout.addWidget(self.btnAddComment)
        DataLayout.addWidget(self.btnSetCycle)

# Row Notepad
        NPButtonWidth = 70
    # header
        dlnotepad = QLabel("NotePad")
        dlnotepad.setFixedWidth(col0width)
        dlnotepad.setFont(self.fatfont)

    # button: print notepad to printer / pdf
        self.btnPrint2Printer = QPushButton('Print')
        self.btnPrint2Printer.clicked.connect(lambda: self.printNotePad())
        self.btnPrint2Printer.setToolTip("Print Content of NotePad to printer or pdf-file")
        self.btnPrint2Printer.setFixedWidth(NPButtonWidth)

    # button: save notepad to file
        self.btnSaveNotePad = QPushButton('Save')
        self.btnSaveNotePad.clicked.connect(lambda: self.saveNotePad())
        self.btnSaveNotePad.setToolTip("Save Content of NotePad as text file named <current filename>.notes")
        self.btnSaveNotePad.setFixedWidth(NPButtonWidth)

    # button: search notepad
        self.btnSearchNotePad = QPushButton("Search")
        self.btnSearchNotePad.clicked.connect(lambda: self.searchNotePad())
        self.btnSearchNotePad.setToolTip("Search NotePad for occurence of a text (Shortcut: CTRL-F)")
        self.btnSearchNotePad.setFixedWidth(NPButtonWidth)

    # button: print plot data
        self.btnPrintPlotData = QPushButton('Data Plt')
        self.btnPrintPlotData.setFixedWidth(NPButtonWidth)
        self.btnPrintPlotData.setToolTip("Print variables as in the current plot to the Npotepad")
        self.btnPrintPlotData.clicked.connect(lambda: self.showData("PlotData"))

    # button: print full data to notepad
        self.btnPrintFullData = QPushButton('Data')
        self.btnPrintFullData.clicked.connect(lambda: self.showData(full=True))
        self.btnPrintFullData.setToolTip('Print Full Log or His Data to the NotePad')
        self.btnPrintFullData.setFixedWidth(NPButtonWidth)

    # button: print data excerpt to notepad
        self.btnPrintExceptData = QPushButton('Data Exc')
        self.btnPrintExceptData.clicked.connect(lambda: self.showData(full=False))
        self.btnPrintExceptData.setToolTip('Print Excerpt of Log or His Data to the NotePad')
        self.btnPrintExceptData.setFixedWidth(NPButtonWidth)

    # button: clear notepad
        clearbutton = QPushButton('Clear')
        clearbutton.clicked.connect(self.clearNotePad)
        clearbutton.setToolTip('Delete all content of the NotePad')
        clearbutton.setFixedWidth(BigButtonWidth)

        NPLayout = QHBoxLayout()
        NPLayout.addStretch()
        NPLayout.addWidget(self.btnPrint2Printer)
        NPLayout.addWidget(self.btnSaveNotePad)
        NPLayout.addWidget(self.btnSearchNotePad)
        NPLayout.addWidget(self.btnPrintFullData)
        NPLayout.addWidget(self.btnPrintPlotData)
        NPLayout.addWidget(self.btnPrintExceptData)
        NPLayout.addStretch()
        NPLayout.addWidget(clearbutton)

    # separator lines - vertical / horizontal
        vlinedB0 = QFrame()
        vlinedB0.setFrameShape(QFrame.VLine)
        hlinedB1 = QFrame()
        hlinedB1.setFrameShape(QFrame.HLine)

    # layout the Data Options
        dataOptions=QGridLayout()
        dataOptions.setContentsMargins(5,5,5,5) #spacing around the data options

        dataOptions.setRowStretch    (4, 1)
        dataOptions.setColumnStretch (0, 0)
        dataOptions.setColumnStretch (1, 10000)
        dataOptions.setColumnStretch (2, 10000)
        dataOptions.setColumnStretch (3, 10000)
        dataOptions.setColumnStretch (4, 0)
        dataOptions.setColumnStretch (5, 0)

        dataOptions.setColumnMinimumWidth(1, 140)
        dataOptions.setColumnMinimumWidth(2, 140)
        dataOptions.setColumnMinimumWidth(3, 140)

        row = 0
        dataOptions.addWidget(dltitle,                 row, 0)
        # dataOptions.addWidget(self.btnPrintPlotData,           row, 1, alignment=Qt.AlignLeft)
        # dataOptions.addWidget(self.btnAddComment,      row, 2, alignment=Qt.AlignCenter)
        # dataOptions.addWidget(self.btnAddComment,      row, 2, alignment=Qt.AlignRight)
        # dataOptions.addWidget(self.btnSetCycle,              row, 3, alignment=Qt.AlignRight)

        dataOptions.addLayout(DataLayout,              row, 1, 1, 3)
        dataOptions.addWidget(vlinedB0,                row, 4, 3, 1)
        dataOptions.addWidget(dlDevice,                row, 5)

        row = 1 # Log
        dataOptions.addWidget(dbtnPlotLog,             row, 0)
        dataOptions.addWidget(self.dcfLog,             row, 1, 1, 3)
        # col 5 is empty (vline)
        dataOptions.addWidget(self.btnMapping,         row, 5)

        row = 2 # History
        dataOptions.addWidget(dbtnPlotHis,             row, 0)
        dataOptions.addWidget(self.dcfHis,             row, 1, 1, 3)
        # col 5 is empty (vline)
        dataOptions.addWidget(self.dtube,              row, 5)

        row = 3 # hline
        dataOptions.addWidget(hlinedB1,                row, 0, 1, 6)

        row = 4 # NotePad
        dataOptions.addWidget(dlnotepad,               row, 0)
        dataOptions.addLayout(NPLayout,                row, 1, 1, 5)

        # group Data Options into Groupbox
        dataOptionsGroup = QGroupBox()
        dataOptionsGroup.setContentsMargins(0,0,0,0)
        dataOptionsGroup.setStyleSheet("QGroupBox {border-style:solid; border-width:1px; border-color:silver;}")
        dataOptionsGroup.setLayout(dataOptions)
        dataOptionsGroup.setFixedHeight(155)  # to match height with graph options (needed here: 143)


# GraphOptions
        ltitle  = QLabel("Graph")
        ltitle.setFont(self.fatfont)

        lmin    = QLabel("Min")
        lmin.setAlignment(Qt.AlignCenter)

        lmax    = QLabel("Max")
        lmax.setAlignment(Qt.AlignCenter)

        lcounts = QLabel("Counter")
        ly2     = QLabel("Ambient")
        ltime   = QLabel("Time")

        self.ymin = QLineEdit()
        self.ymin.setToolTip('Minimum setting for Counter axis')

        self.ymax = QLineEdit()
        self.ymax.setToolTip('Maximum setting for Counter axis')

        self.y2min=QLineEdit()
        self.y2min.setToolTip('Minimum setting for Ambient axis')

        self.y2max=QLineEdit()
        self.y2max.setToolTip('Maximum setting for Ambient axis')

        self.xmin=QLineEdit()
        self.xmin.setToolTip('The minimum (left) limit of the time to be shown. Enter manuallly or by left-mouse-click on the graph')

        self.xmax=QLineEdit()
        self.xmax.setToolTip('The maximum (right) limit of the time to be shown. Enter manuallly or by right-mouse-click on the graph')

    # col 3:
        col3width = 75

        self.btnClear = QPushButton('Clear')
        self.btnClear.setFixedWidth(col3width)
        self.btnClear.setToolTip("Clear the Graph Limit Options to Default conditions")
        self.btnClear.clicked.connect(self.clearGraphLimits)

        self.yunit = QComboBox()
        self.yunit.addItems(["CPM", "µSv/h"])
        self.yunit.setMaximumWidth(col3width)
        self.yunit.setToolTip('Select the Count Unit for the plot')
        self.yunit.currentIndexChanged.connect(self.changedGraphCountUnit)

        self.y2unit = QComboBox()
        self.y2unit.addItems(["°C", "°F"])
        self.y2unit.setMaximumWidth(col3width)
        self.y2unit.setToolTip('Select the Temperature Unit')
        self.y2unit.currentIndexChanged.connect(self.changedGraphTemperatureUnit)

        self.xunit = QComboBox()
        self.xunit.addItems(["Time", "auto", "second", "minute", "hour", "day", "week", "month"])
        self.xunit.setMaximumWidth(col3width)
        self.xunit.currentIndexChanged.connect(self.changedGraphTimeUnit)
        self.xunit.setToolTip('The time axis to be shown as Time-of-Day (Time) or time since first record in seconds, minutes, hours, days, weeks, months;\nauto selects most appropriate period')

    # col 4:
        col4width = 50

        btnReset  = QPushButton('Reset')
        btnReset.setFixedWidth(col4width)
        btnReset.setToolTip("Reset all Graph Options to Default conditions")
        btnReset.clicked.connect(lambda: self.reset_replotGraph(full=True))

        btnSetScaling =  QPushButton('Scale')
        btnSetScaling.setFixedWidth(col4width)
        btnSetScaling.setToolTip("Scaling - View and edit current settings for value- and graph-scaling")
        btnSetScaling.clicked.connect(self.editScaling)

        btnSaveFig =  QPushButton('Save')
        btnSaveFig.setFixedWidth(col4width)
        btnSaveFig.setToolTip("Save graph to file")
        btnSaveFig.clicked.connect(saveGraphToFile)

        btnApplyGraph = QPushButton('Apply')
        btnApplyGraph.setFixedWidth(col4width)
        btnApplyGraph.setToolTip("Apply the Graph Options and replot")
        btnApplyGraph.setStyleSheet("background-color: lightblue")
        # btnApplyGraph.setMinimumHeight(51)
        # btnApplyGraph.setMinimumHeight(76)
        btnApplyGraph.setDefault(True)
        btnApplyGraph.clicked.connect(self.applyGraphOptions)

    # col 5: vertical line

    # col 6:
        col6width = 80

        # The drop-down selector for selected variable
        self.select = QComboBox()
        self.select.setToolTip('The data to be selected for handling')
        self.select.setMaximumWidth(col6width)
        self.select.setMinimumWidth(col6width)
        self.select.setEnabled(False)
        self.select.currentIndexChanged.connect(self.changedGraphSelectedVariable)
        self.select.setMaxVisibleItems(12)
        for vname in gglobs.varsCopy:
            self.select.addItems([vname])

        # The checkboxes to select the displayed variables
        self.varDisplayCheckbox = {}
        for vname in gglobs.varsCopy:
            vshort = gglobs.varsCopy[vname][1]
            vlong  = gglobs.varsCopy[vname][0]

            self.varDisplayCheckbox[vname] = QCheckBox    (vshort)
            self.varDisplayCheckbox[vname].setToolTip     (vlong)
            self.varDisplayCheckbox[vname].setChecked     (False)
            self.varDisplayCheckbox[vname].setEnabled     (False)
            self.varDisplayCheckbox[vname].setTristate    (False)

            # "double lambda needed for closure" WTF???
            self.varDisplayCheckbox[vname].stateChanged.connect((lambda x: lambda: self.changedGraphDisplayCheckboxes(x))(vname))

        chk_width = 20

        self.mavbox = QCheckBox("MvAvg  s:")
        # self.mavbox.setLayoutDirection(Qt.RightToLeft)
        self.mavbox.setLayoutDirection(Qt.LeftToRight)
        self.mavbox.setChecked(gglobs.mavChecked)
        self.mavbox.setMaximumWidth(col6width)
        self.mavbox.setTristate (False)
        self.mavbox.setToolTip('If checked a Moving Average line will be drawn')
        self.mavbox.stateChanged.connect(self.changedGraphOptionsMav)

        self.avgbox = QCheckBox("Avg")
        # self.avgbox.setLayoutDirection(Qt.RightToLeft)
        self.avgbox.setLayoutDirection(Qt.LeftToRight)
        self.avgbox.setMaximumWidth(col6width)
        self.avgbox.setChecked(gglobs.avgChecked)
        self.avgbox.setTristate (False)
        self.avgbox.setToolTip("If checked, Average and ±95% lines will be shown")
        self.avgbox.stateChanged.connect(self.changedGraphOptionsAvg)

    # col 7:
        col7width = 55

        # this starts in col 6 and extends to col 7
        self.labelSelVar = QLabel("---")
        self.labelSelVar.setToolTip("Shows the last value of the Selected Variable when logging\nClick to show all values in separate window")
        self.labelSelVar.setMinimumWidth(col6width + col7width)
        self.labelSelVar.setFont(QFont('sans', 12, QFont.Bold))
        self.labelSelVar.setStyleSheet('color:darkgray;')
        self.labelSelVar.setAlignment(Qt.AlignCenter)
        self.labelSelVar.mousePressEvent=(lambda x: gsup_tools.displayLastValues())


        # color select button
        self.btnColorText = "Color of selected variable; click to change it. Current color:  "
        self.btnColor     = ClickLabel('Color')
        self.btnColor       .setAlignment(Qt.AlignCenter)
        self.btnColor       .setMaximumWidth(col7width)
        self.btnColor       .setMinimumWidth(col7width)
        self.btnColor       .setStyleSheet("QLabel { border: 1px solid silver;  border-radius: 3px; }")
        addMenuTip(self.btnColor, self.btnColorText + "None")

        self.mav=QLineEdit()
        self.mav.setMinimumWidth(col7width)
        self.mav.setMaximumWidth(col7width)
        self.mav.setToolTip('Enter the Moving Average smoothing period in seconds')
        self.mav.setText("{:0.0f}".format(gglobs.mav_initial))
        self.mav.textChanged.connect(self.changedGraphOptionsMavText)

        self.fitbox = QCheckBox("LinFit")
        # self.fitbox.setLayoutDirection(Qt.RightToLeft)
        self.fitbox.setLayoutDirection(Qt.LeftToRight)
        self.fitbox.setMaximumWidth(col7width)
        self.fitbox.setChecked(gglobs.fitChecked)
        self.fitbox.setTristate (False)
        self.fitbox.setToolTip("A Linear Regression will be applied to the Selected Variable and shown")
        self.fitbox.stateChanged.connect(self.changedGraphOptionsLinFit)

    # col 9:

        col9width = 60

        # SuSt
        btnQuickStats =  QPushButton('SuSt')
        btnQuickStats.setFixedWidth(col9width)
        btnQuickStats.setToolTip("Shows Summary Statistics of variables and data as in the current plot")
        btnQuickStats.clicked.connect(lambda: gsup_tools.fprintSuSt())

        # Stats
        btnPlotStats =  QPushButton('Stats')
        btnPlotStats.setFixedWidth(col9width)
        btnPlotStats.setToolTip("Shows Detailed Statistics of variables and data as in the current plot")
        btnPlotStats.clicked.connect(lambda: gsup_tools.showStats())

        # Scatterplot
        btnScat =  QPushButton('Scat')
        btnScat.setToolTip('Show an X-Y Scatter plot with optional polynomial fit, using data currently selected in the plot')
        btnScat.setFixedWidth(col9width)
        btnScat.clicked.connect(lambda: gsup_tools.selectScatterPlotVars())

        # Poiss
        btnPoisson =  QPushButton('Poiss')
        btnPoisson.setFixedWidth(col9width)
        btnPoisson.setToolTip("Shows a plot of a Poisson curve on a histogram of the selected variable data as in the current plot")
        btnPoisson.clicked.connect(lambda: gstat_poisson.plotPoisson())

        # FFT
        btnFFT =  QPushButton('FFT')
        btnFFT.setFixedWidth(col9width)
        btnFFT.setToolTip("Show a plot of FFT spectra & Autocorrelation of the selected variable data as in the current plot")
        btnFFT.clicked.connect(lambda: gstat_fft.plotFFT())

    # separator lines
        vlineA0 = QFrame()
        vlineA0.setFrameShape(QFrame.VLine)

        vlineC0 = QFrame()
        vlineC0.setFrameShape(QFrame.VLine)

    # OFF / ON button
        btn_width = 35
        btnOFF = QPushButton('OFF')
        btnOFF .setToolTip("Uncheck all variables")
        btnOFF .clicked.connect(lambda: self.setPlotVarsOnOff("OFF"))
        btnOFF .setMaximumWidth(btn_width)

        btnON  = QPushButton('ON')
        btnON  .setToolTip("Check all avialable variables")
        btnON  .clicked.connect(lambda: self.setPlotVarsOnOff("ON"))
        btnON  .setMaximumWidth(btn_width)

    # layout of variables check boxes with OFF / ON button
        layoutH = QHBoxLayout()
        layoutH.addWidget(btnOFF)
        layoutH.addWidget(btnON)
        for vname in gglobs.varsCopy:
            layoutH.addWidget(self.varDisplayCheckbox[vname])

    #layout the GraphOptions
        graphOptions=QGridLayout()
        graphOptions.setContentsMargins(5,9,5,5) # spacing around the graph options top=9 is adjusted for fit!

        # STEPPING ORDER ##############################
        # to define the order of stepping through by tab-key
        # row 1 .. 3, col 1 + 2 is put in front
        row = 1
        graphOptions.addWidget(self.ymin,       row, 1)
        graphOptions.addWidget(self.ymax,       row, 2)
        row = 2
        graphOptions.addWidget(self.y2min,      row, 1)
        graphOptions.addWidget(self.y2max,      row, 2)
        row = 3
        graphOptions.addWidget(self.xmin,       row, 1)
        graphOptions.addWidget(self.xmax,       row, 2)
        # stepping end ###############################

        row = 0
        graphOptions.addWidget(ltitle,          row, 0)
        graphOptions.addWidget(lmin,            row, 1)
        graphOptions.addWidget(lmax,            row, 2)
        graphOptions.addWidget(self.btnClear,   row, 3)
        graphOptions.addWidget(btnReset,        row, 4)
        graphOptions.addWidget(vlineA0,         row, 5, 4, 1)
        graphOptions.addWidget(self.select,     row, 6)
        graphOptions.addWidget(self.btnColor,   row, 7)
        graphOptions.addWidget(vlineC0,         row, 8, 5, 1) # vertical line across all 6 rows
        graphOptions.addWidget(btnQuickStats,   row, 9)

        row = 1
        graphOptions.addWidget(lcounts,         row, 0)
        # see stepping order
        # see stepping order
        graphOptions.addWidget(self.yunit,      row, 3)
        graphOptions.addWidget(btnSetScaling,   row, 4)
        # col 5 is empty (vert line)
        graphOptions.addWidget(self.mavbox,     row, 6)
        graphOptions.addWidget(self.mav,        row, 7)
        # col 8 is empty (vert line)
        graphOptions.addWidget(btnPlotStats,    row, 9)

        row = 2
        graphOptions.addWidget(ly2,             row, 0)
        # see stepping order
        # see stepping order
        graphOptions.addWidget(self.y2unit,     row, 3)
        graphOptions.addWidget(btnSaveFig,      row, 4)

        # col 5 is empty (vert line)
        graphOptions.addWidget(self.avgbox,     row, 6)
        graphOptions.addWidget(self.fitbox,     row, 7)
        # col 8 is empty (vert line)
        graphOptions.addWidget(btnScat,         row, 9)

        row = 3
        graphOptions.addWidget(ltime,           row, 0)
        # see stepping order
        # see stepping order
        graphOptions.addWidget(self.xunit,      row, 3)
        graphOptions.addWidget(btnApplyGraph,   row, 4)
        # col 5 is empty (vert line)
        graphOptions.addWidget(self.labelSelVar,   row, 6, 1, 2)
        # col 7 is empty
        # col 8 is empty (vert line)
        graphOptions.addWidget(btnPoisson,      row, 9)

        row = 4
        graphOptions.addLayout(layoutH,         row, 0, 1, 8)
        graphOptions.addWidget(btnFFT,          row, 9)


    # group Graph Options into Groupbox
        graphOptionsGroup = QGroupBox()
        graphOptionsGroup.setContentsMargins(0,0,0,0)
        graphOptionsGroup.setStyleSheet("QGroupBox {border-style: solid; border-width: 1px; border-color: silver;}")
        graphOptionsGroup.setLayout(graphOptions)
        graphOptionsGroup.setFixedHeight(155)  # min height needed

# NotePad
        self.notePad = QTextEdit()
        self.notePad.setReadOnly(True)
        self.notePad.setFont(self.fontstd)
        self.notePad.setLineWrapMode(QTextEdit.NoWrap)
        self.notePad.setTextColor(QColor(40, 40, 40))
        # self.notePad.setStyleSheet("background-color:%s;" % gglobs.windowPadColor[0])

        gglobs.notePad = self.notePad # pointer used for fprint in utils

# LogPad
        self.logPad = QTextEdit()
        self.logPad.setReadOnly(True)
        self.logPad.setFont(self.fontstd)
        self.logPad.setLineWrapMode(QTextEdit.NoWrap)
        self.logPad.setTextColor(QColor(40, 40, 40))
        # self.logPad.setStyleSheet("background-color:%s;" % gglobs.windowPadColor[1])

        gglobs.logPad = self.logPad # pointer used for logPrint in utils

# set the layout - left side
        splitterPad = QSplitter(Qt.Vertical)
        splitterPad.addWidget(self.notePad)
        splitterPad.addWidget(self.logPad)
        splitterPad.setSizes([800, 250])

        layoutLeft = QVBoxLayout()
        layoutLeft.addWidget(dataOptionsGroup)
        layoutLeft.addWidget(splitterPad)
        layoutLeft.setContentsMargins(0,0,0,0)
        layoutLeft.setSpacing(0)

# set the layout - right side
        layoutRight = QVBoxLayout()
        layoutRight.addWidget(graphOptionsGroup)
        # layoutRight.addStretch()
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
        self.timer0 = QTimer()
        # self.timer0.timeout.connect(self.runCycle)
        self.timer0.timeout.connect(self.runLoggingCycle)


#timer2 for checking
        self.timer1 = QTimer()
        # self.timer1.start(500)                          # 500 millisec
        # self.timer1.start(100)                          # 100 millisec
        self.timer1.start(10)                             # 10 millisec
        self.timer1.timeout.connect(self.runCheckCycle)   # checks for start/stop coming from web page, logPad size, PNG request

#show
        self.dcfLog.setText(str(gglobs.logFilePath))    # default is None
        self.dcfHis.setText(str(gglobs.hisFilePath))
        self.showTimingSetting (gglobs.logCycle)

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

        gdprint("Starting the GUI complete " + "-" * 100 + "\n")

        if gglobs.startupProblems > "":
            self.startupProblems(gglobs.startupProblems, closeGL=True)  # EXIT on Failure!

        if gglobs.python_version  > "":
            self.startupProblems(gglobs.python_version,  closeGL=True)  # EXIT on wrong Python version!

        if gglobs.configAlerts > "":
            msg  = "<b>Configuration File has Problems, please review:\n"
            msg += "(without correction, defaults will be used)</b>\n\n"
            msg += gglobs.configAlerts
            self.startupProblems(msg,  closeGL = False)
            gglobs.configAlerts = ""

        # at least one activated device?
        isAnyDeviceActive = False
        for DevName in gglobs.Devices:
            if gglobs.Devices[DevName][ACTIV]:
                isAnyDeviceActive = True
                break

        if not isAnyDeviceActive:
            self.fprintWarningMessage("WARNING: You have not activated any device!", configFlag=True)

        if gglobs.MonServerAutostart:
            gweb_monserv.initMonServer(force=True)

        # Devel - start GeigerLog with command 'devel' e.g.: 'geigerlog -dv devel'
        # on devel  : make some extra commands available in devel menu
        # on devel1 : do devel and load database 'default.logdb' if available
        # on devel2 : do devel1 and make connections
        # on devel3 : do devel2 and start quicklog
        if gglobs.devel:
            crctest = (0x80, 0x06)
            crctest = (0xFF, 0xFF)
            cdprint("crc test: {} => {} ".format(crctest, getCRC8(crctest)))

        if gglobs.devel1:
            self.switchAllConnections(new_connection = "ON")

        if gglobs.devel2:
            defaultFile = os.path.join(gglobs.dataPath, "default.logdb")
            if os.access(defaultFile , os.R_OK):
                self.getFileLog(defaultLogDBPath = defaultFile)
            else:
                dprint("Testfile '{}' not found".format(defaultFile), debug=True)

        if gglobs.devel3:
            self.quickLog()

        playWav("ok")


#========== END __init__ ------------------***********
#
#========== BEGIN Class Functions =============================================

    def runCheckCycle(self):
        """triggered by timer1, checks for start/stop set via web page and more"""

        fncname = "runCheckCycle: "

        # check for startflag from web
        if gglobs.startflag:
            gglobs.startflag = False
            if not gglobs.logging: self.startLogging()

        # check for stopflag from web
        if gglobs.stopflag:
            gglobs.stopflag = False
            if gglobs.logging:     self.stopLogging()

        # check for cycletime overrun
        if gglobs.runLogCycleDelta[0] > gglobs.logCycle:
            msg = " Getting Log data took longer ({:0.3f} sec) than cycle ({:0.3f} sec)!".format(gglobs.runLogCycleDelta[0], gglobs.logCycle)
            qefprint(stime() + msg)
            edprint(msg)
            edprint(gglobs.runLogCycleDelta[1])
            gglobs.runLogCycleDelta = (0, "")  # runCheckCycle would catch it twice with its 500ms cycle

        # Truncate logPad
        # limit the amount of text stored in the logPad
        # clear + append is MUCH faster than setText or setPlainText !!! (5000 ms vs 200 ms)
        # Character count: 5 + 8 + 7 * 12 = 97 round up to 100
        # 100char/sec * 3600sec/h = 360 000 per h ==> 1 mio in 2.8h = ~3h
        # 10000 char / 100char/sec ==> 100 sec, ~2min
        # in overnight run the limit was done some 600 times; maximum duration was 0.237 sec!
        lpstart   = time.time()
        oldlptext = gglobs.logPad.toPlainText()
        lenOld    = len(oldlptext)
        lpmax     = 1e5                                       # max no of chars in logPad
        if lenOld > lpmax:
            lpshort   = oldlptext[-int(lpmax - 10000):]       # exclude first 10000+ chars
            LFindex   = lpshort.find("\n")                    # find position of first LF in remaining text
            newlptext = lpshort[LFindex + 1:]
            lenNew    = len(newlptext)
            Delta     = lenOld - lenNew
            self.logPad.clear()
            gglobs.logPad.append(newlptext)                   # append shortened text to logPad

        # prepare pic in memory
        #
        # prepare a JPG in memory
        # gglobs.picbytes = io.BytesIO()
        # plt.savefig(gglobs.picbytes, format="jpg")

        # matplotlib offers some optional export options that are only
        # available to .jpg files. For example, quality (default 95),
        # optimize (default: false), and progressive (default: false).
        # plt.savefig('line_plot.jpg', dpi=300, quality=80, optimize=True, progressive=True)
        # MatplotlibDeprecationWarning: The 'quality' parameter of print_jpg()
        # was deprecated in Matplotlib 3.3 and will be removed two minor releases
        # later. Use pil_kwargs={'quality': ...} instead. If any parameter follows
        # 'quality', they should be passed as keyword, not positionally.

        # gglobs.picbytes = io.BytesIO()
        # plt.savefig(gglobs.picbytes, format="jpg", pil_kwargs={'quality':80})

        # prepare a PNG, SVG, JPG in memory
        # with a MiniMon File of 20MB, 665000 records!
        # DEBUG  : ...232 runCheckCycle: Make JPG:   915.4 ms
        # DEBUG  : ...233 runCheckCycle: Make SVG: 36627.4 ms  # using SVG makes the generation time explode!
        # DEBUG  : ...234 runCheckCycle: Make PNG:   933.0 ms
        # DEBUG  : ...233 runCheckCycle: Make JPG:   945.2 ms  # Qual=80; quality reduction bringt nichts:

        # mit 720 records:
        # Vorteil PNG über SVG bleibt
        # DEBUG  : ...268 runCheckCycle: Make JPG:  85.9 ms
        # DEBUG  : ...269 runCheckCycle: Make SVG: 152.2 ms
        # DEBUG  : ...270 runCheckCycle: Make PNG:  99.3 ms
        # DEBUG  : ...244 runCheckCycle: Make JPG:  90.4 ms    # Qual=80; quality reduction bringt nichts

        if gglobs.flagGetGraph:
            gglobs.flagGetGraph = False

            # get and save the pic into memory
            startpng = time.time()
            gglobs.picbytes = io.BytesIO()
            plt.savefig(gglobs.picbytes, format="png")
            duration = (time.time() - startpng) * 1000 # ms
            cdprint(fncname + "Make PNG: {:0.1f} ms".format(duration))

        # removed when Telegram had a code change
        # # update Telegram Messenger
        # if gglobs.TelegramActivation:
        #     now = time.time()
        #     # print("now - gglobs.TelegramLastUpdate: ", now - gglobs.TelegramLastUpdate)
        #     if now - gglobs.TelegramLastUpdate > gglobs.TelegramUpdateCycle * 60:
        #         gglobs.TelegramLastUpdate = now
        #         updateTelegram()

        # update GMCmap when RWMmapUpdateCycle expires
        if gglobs.RWMmapActivation:
            now = time.time()
            if gglobs.RWMmapLastUpdate is None:
                gglobs.RWMmapLastUpdate = now
            else:
                # print("now - gglobs.RWMmapLastUpdate: ", now - gglobs.RWMmapLastUpdate)
                if now - gglobs.RWMmapLastUpdate > gglobs.RWMmapUpdateCycle * 60:
                    gglobs.RWMmapLastUpdate = now
                    updateRadWorldMap()


    def runLoggingCycle(self):
        """Fetch the values from the devices, save to database, and update Display and Plot"""

        if not gglobs.logging:            return  # currently not logging
        # if gglobs.logConn == None:        return  # no connection defined
        if gglobs.runLogCycleIsBusy:      return  # called while still active

        gglobs.runLogCycleIsBusy = True

        # play Click
        if gglobs.LogClickSound: playClick()

        start_runLogCycle = time.time()

        fncname             = "runLoggingCycle: "
        msgfmt              = "{:<25s}   {:6.3f} "
        msg                 = []
        gglobs.LogReadings += 1                                 # update index (=LogReadings)

        if gglobs.verbose:  print()                             # print empty line to terminal only

        vprint(fncname + "saving to:", gglobs.logDBPath)
        setDebugIndent(1)
        vprint(getLoggedValuesHeader())                         # must come before fetchLogValues!

        # set the time for this record
        timeJulian, timetag = gsup_sql.DB_getLocaltime() # e.g.: 2458512.928904213, '2019-01-29 10:17:37'
        #~print(fncname + "timetag:", timetag, ",  timeJulian:",timeJulian)

        # For LogPad remove Date, use time only  '2018-07-14 12:00:52' --> '12:00:52'
        # Example: Index     Time   vars and data
        #           1162 11:43:40   M=143  S=1  M1=  S1=  M2=128.0  S2=3.0  M3=128.0  S3=3.0  T=25.0  P=983.63  H=24.0  X=18.0
        msgLogPad = "{:2.7g} {:8s} ".format(gglobs.LogReadings, timetag[11:])

        # fetch the data
        # Example logvalue: {'CPM': 18110.0, 'CPS': 297.0, 'CPM1st': nan, 'CPS1st': nan, 'CPM2nd': nan, 'CPS2nd': nan, 'CPM3rd': nan, 'CPS3rd': nan, 'Temp': 295, 'Press': 293.8, 'Humid': 277, 'Xtra': 18}
        s1 = time.time()
        logValues = self.fetchLogValues()
        duration  = 1000 * (time.time() - s1)
        msg.append(msgfmt.format("getValues Total:", duration))
        vprint(msg[-1])

        # check for all NAN, and update lastLogValues with logValues, but only if new value is not NAN
        nanOnly = True
        for vname in gglobs.varsCopy:
            if not np.isnan(logValues[vname]):
                nanOnly                     = False
                gglobs.lastLogValues[vname] = logValues[vname]

        if nanOnly:
            logPrint(msgLogPad + " No data")            # no saving, no display, no graph
        else:
            # save the data
            s1 = time.time()
            save_msg = self.saveLogValues(timeJulian, logValues)
            duration  = 1000 * (time.time() - s1)
            # gglobs.ManuValue[0] = round(duration, 3)
            msg.append(msgfmt.format("save Data:", duration) + save_msg)
            vprint(msg[-1])
            if duration > 0.1 * gglobs.logCycle * 1000:
                edprint(fncname + "Save Data took very long: {:0.3f} ms. Of this: {}".format(duration, save_msg))
                # playClick()


            # update the LogPad
            # Example: Index     Time   vars=values ...
            #           1162 11:43:40   M=143  S=1  M1=  S1=  M2=128.0  S2=3.0  M3=128.0  S3=3.0  T=25.0  P=983.63  H=24.0  X=18.0
            s1 = time.time()
            # get values for all loggable variables
            for vname in gglobs.varsCopy:
                if gglobs.varsSetForLog[vname]:
                    msgLogPad += " {}=".format(gglobs.varsCopy[vname][1])
                    if not np.isnan(logValues[vname]):  msgLogPad += "{:<7.6g}".format(logValues[vname]) # can print 6 digit number still as integer
                    else:                               msgLogPad += " " * 7
            logPrint(msgLogPad)
            duration  = 1000 * (time.time() - s1)
            msg.append(msgfmt.format("update LogPad:", duration))
            vprint(msg[-1])

            # update Displays
            # - "Last value" of the Selected Variable in the Graph area (~0.3 ms)
            # - "Display Last Values" window                            (~1 ms)
            s1 = time.time()
            self.updateDisplayVariableValue()
            duration  = 1000 * (time.time() - s1)
            msg.append(msgfmt.format("update Displays:", duration))
            vprint(msg[-1])


            # update graph, but only if current graph is the log graph!
            s1 = time.time()
            PlotMsg = ""
            if gglobs.activeDataSource == "Log":
                gglobs.currentDBData = gglobs.logDBData         # the data!
                PlotMsg = gsup_plot.makePlot()  # direct plot; slightly quicker than plotGraph

            duration  = 1000 * (time.time() - s1)
            msg.append("{:<25s}   {:5.1f}  {}".format("update Graph:", duration, PlotMsg))
            vprint(msg[-1])


        totaldur  = 1000 * (time.time() - start_runLogCycle)
        msg.append(msgfmt.format(fncname + "Total:", totaldur))
        vprint(msg[-1])

        setDebugIndent(0)

        gglobs.runLogCycleIsBusy = False
        gglobs.runLogCycleDelta  = (totaldur / 1000, ", ".join(msg))

        gglobs.forceSaving = False

        return msgLogPad # used in snap record


    def fetchLogValues(self):
        """Reads all variables from all activated devices and returns as logValues dict"""

        fncname = "fetchLogValues: "

        # logValues is dict like: (in Python > 3.6 always ordered CPM .... Xtra!)
        # {'CPM':93.0,'CPS':2.0,'CPM1st':45,'CPS1st':3,'CPM2nd':0,'CPS2nd':0,'CPM3rd':nan,'CPS3rd':nan,'Temp':3.0,'Press':4.0,'Humid':5.0,'Xtra':12}
        logValues = {}
        for vname in gglobs.varsCopy:
            logValues[vname] = gglobs.NAN   # NAN is needed later for testing

        # fetch the new values for each device (if active)
        #   gglobs.Devices keys: "GMC", "Audio", "RadMon", "AmbioMon", "GammaScout", "I2C", "LabJack", "MiniMon", "Simul", "Manu", "WiFi"
        #   e.g.: gglobs.Devices['GMC']   [VNAME] : ['CPM', 'CPS']              # VNAME == 1
        #   e.g.: gglobs.Devices['RadMon'][VNAME] : ['T', 'P', 'H', 'X']
        for DevName in gglobs.Devices:
            if gglobs.Devices[DevName][CONN]: # look only at connected devices
                devvars = gglobs.Devices[DevName][VNAME]    #   == ['T', 'P', 'H', 'X']
                if   DevName == "GMC"       : logValues.update(gdev_gmc         .getValuesGMC        (devvars))
                elif DevName == "Audio"     : logValues.update(gdev_audio       .getValuesAudio      (devvars))
                elif DevName == "RadMon"    : logValues.update(gdev_radmon      .getValuesRadMon     (devvars))
                elif DevName == "AmbioMon"  : logValues.update(gdev_ambiomon    .getValuesAmbioMon   (devvars))
                elif DevName == "GammaScout": logValues.update(gdev_gscout      .getValuesGammaScout (devvars))

                elif DevName == "I2C"       : logValues.update(gdev_i2c         .getValuesI2C        (devvars))
                elif DevName == "LabJack"   : logValues.update(gdev_labjack     .getValuesLabJack    (devvars))
                elif DevName == "MiniMon"   : logValues.update(gdev_minimon     .getValuesMiniMon    (devvars))
                elif DevName == "Simul"     : logValues.update(gdev_simul       .getValuesSimul      (devvars))
                elif DevName == "Manu"      : logValues.update(gdev_manu        .getValuesManu       (devvars))

                elif DevName == "WiFiClient": logValues.update(gdev_wificlient  .getValuesWiFiClient (devvars))
                elif DevName == "WiFiServer": logValues.update(gdev_wifiserver  .getValuesWiFiServer (devvars))

        return logValues


    def saveLogValues(self, timeJulian, logValues):
        """Save data to database, and update data in memory"""

        fncname = "saveLogValues: "

        datalist     = [None] * (gglobs.datacolsDefault + 2)        # (12 + 2) x None; 2 wg Julianday
        datalist[0]  = gglobs.LogReadings                           # store the index
        datalist[1]  = "NOW"                                        # time stamp
        datalist[2]  = "localtime"                                  # modifier for time stamp

        # check for all data being nan
        nanOnly      = True
        for i, vname in enumerate(gglobs.varsCopy):
            if not np.isnan(logValues[vname]):
                nanOnly         = False
                datalist[3 + i] = logValues[vname]                  # data into datalist[3 + following]

        # rdprint(fncname + "datalist: ", datalist)

        # save data, but only if at least one variable is not nan
        timing = ""
        if nanOnly:
            timing += " all NAN, not saving"

        else:
        # Write to database file
            # in >50000 writes average was 15.6 ms, Stddev = 3.0, maximum 300ms(!)
            wdbstart = time.time()
            gsup_sql.DB_insertData(gglobs.logConn, [datalist])
            duration = (time.time() - wdbstart) * 1000
            timing += " to db file: {:0.1f} ms".format(duration)
            # gglobs.ManuValue[0] = round(duration, 3)    # -> Temp

        # Write to memory
            # time is set to matplotlib time
            datalist = [
                                                            # no index
                        timeJulian - gglobs.JULIAN111,      # time is set to matplotlib time
                        logValues["CPM"],
                        logValues["CPS"],
                        logValues["CPM1st"],
                        logValues["CPS1st"],
                        logValues["CPM2nd"],
                        logValues["CPS2nd"],
                        logValues["CPM3rd"],
                        logValues["CPS3rd"],
                        logValues["Temp"],
                        logValues["Press"],
                        logValues["Humid"],
                        logValues["Xtra"],
                       ]

            # gglobs.logDBData = np.append       (gglobs.logDBData, [datalist],  axis=0)        # max = 10000 ms
            # gglobs.logDBData = np.concatenate ((gglobs.logDBData, [datalist]), axis=0)        # max = 12000 ms
            # gglobs.logDBData = np.vstack      ((gglobs.logDBData, [datalist])        )        # max =  9000 ms

            wmstart = time.time()
            gglobs.logDBData = np.vstack ((gglobs.logDBData, [datalist]))
            duration = (time.time() - wmstart) * 1000
            # rdprint("np.vstack ((gglobs.logDBData, [datalist])): {:0.3f} ms".format(duration))

            # gglobs.ManuValue[1] = round(duration, 3)    # -> Press
            timing += ",  to memory: {:0.1f} ms".format(duration)

        return timing


    def snapLogValue(self):
        """Take a measurement when toolbar icon Snap is clicked"""

        if not gglobs.logging: return

        fncname = "snapLogValue: "
        vprint(fncname)
        setDebugIndent(1)

        snaprecord = self.runLoggingCycle() # do an extra logging cycle

        fprint(header("Snapped Log Record"))
        fprint(snaprecord)
        vprint(fncname + snaprecord)

        # comment to the DB
        ctype       = "COMMENT"
        cJulianday  = "NOW"
        cinfo       = "Snapped log record: '{}'".format(snaprecord)
        gsup_sql.DB_insertComments(gglobs.logConn, [[ctype, cJulianday, "localtime", cinfo]])

        setDebugIndent(0)


#####################################################################################################

    def toggleLogClick(self):
        """toggle making a click at avery log cycle"""

        gglobs.LogClickSound = not gglobs.LogClickSound
        fprint(header("Toggle Log Click"))
        fprint("Toggle Log Click", "is ON" if gglobs.LogClickSound else "is OFF")


    # def flashCycleButton(self, mode):

    #     if mode == "ON":    stylesheetcode = "QPushButton {background-color:#F4D345; color:rgb(0,0,0);}" # yellow button bg
    #     else:               stylesheetcode = "QPushButton {}"                                            # std grey button bg
    #     self.btnSetCycle.setStyleSheet(stylesheetcode)
    #     # Qt_update()                                     # without it no flashing at all


    def fprintWarningMessage(self, message, configFlag=False):
        """Warning No Device Activated"""

        efprint(header(message))
        if configFlag:  qefprint("Devices are activated in the configuration file 'geigerlog.cfg'.\n")
        qefprint("Neither Logging nor History downloads from device are possible, but you can work on\n\
                  existing Log and History data loaded from file.")


    def startupProblems(self, message, closeGL = True):
        """alert on problems like wrong Python version, configuration file missing,
        configuration file incorrect"""

        playWav("error")

        msg = QMessageBox()
        msg.setWindowIcon(self.iconGeigerLog)
        msg.setWindowTitle("STARTUP PROBLEM")

        msg.setText("<!doctype html>" + message)    # message must be html coded text

        msg.setStandardButtons  (QMessageBox.Ok)
        msg.setDefaultButton    (QMessageBox.Ok)
        msg.setEscapeButton     (QMessageBox.Ok)
        msg.setWindowModality   (Qt.WindowModal)
        msg.exec()

        if closeGL:
            self.close() # End GeigerLog; may not result in exit, needs sys.exit()
            sys.exit(1)


    def showIPStatus(self):

        fncname = "showIPStatus"
        # dprint(fncname)

    # GeigerLog's IP Address
        lglip = QLabel("GeigerLog's IP Address:")
        lglip.setMinimumWidth(200)

        IPfont = QFont()
        IPfont.setPixelSize(30)

        glip  = QLabel()
        glip.setToolTip('IP Address of computer running GeigerLog')
        glip.setFont(IPfont)
        glip.setText(getGeigerLogIP())

    # Monitor Server
        lmonserve = QLabel("GeigerLog's Monitor Server:")
        lmonserve.setAlignment(Qt.AlignLeft)

        monserve = QLabel()
        monserve.setToolTip('Monitor Server:   IP : Port')
        if gglobs.MonServerActive: addr = (gglobs.MonServerIP, gglobs.MonServerPort)
        else:                           addr = ("auto", "auto")
        monserve.setText("{} : {}".format(*addr))

    # WiFiClient Server
        lwific = QLabel("GeigerLog's WiFiClient Server:")
        lwific.setAlignment(Qt.AlignLeft)

        wific = QLabel()
        wific.setToolTip('WiFiClient Server:   IP : Port')
        wific.setText("{} : {}".format(gglobs.WiFiClientIP, gglobs.WiFiClientPort))


        ipoptions=QGridLayout()
        ipoptions.addWidget(lglip,                          0, 0)
        ipoptions.addWidget(glip,                           0, 1)
        ipoptions.addWidget(QLabel(""),                     1, 0)
        ipoptions.addWidget(QLabel("IP Address : Port"),    2, 1)
        ipoptions.addWidget(lmonserve,                      3, 0)
        ipoptions.addWidget(monserve,                       3, 1)
        ipoptions.addWidget(lwific,                         4, 0)
        ipoptions.addWidget(wific,                          4, 1)
        ipoptions.addWidget(QLabel(""),                     6, 1)

    # Dialog box
        d = QDialog() # set parent empty to popup in center of screen
        d.setWindowIcon(self.iconGeigerLog)
        d.setWindowTitle("Show IP Status")
        d.setWindowModality(Qt.WindowModal)

    # Buttons
        self.bbox = QDialogButtonBox()
        self.bbox.setStandardButtons(QDialogButtonBox.Ok)
        self.bbox.accepted.connect(lambda: d.done(100))

    # VLayout to d
        layoutV = QVBoxLayout(d)
        layoutV.addLayout(ipoptions)
        layoutV.addWidget(self.bbox)

        d.exec()


    def searchNotePad(self):
        """Search Content of NotePad for occurence of text"""

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
            if found or stxt == "": return

        self.showStatusMessage("Search NotePad Content: Text '{}' not found".format(stxt))


    def saveNotePad(self):
        """Save Content of NotePad to file"""

        nptxt = self.notePad.toPlainText()  # Saving as Plain Text; all is b&W, no colors
        #nptxt = self.notePad.toHtml()      # Saving in HTML Format; preserves color
        #print("nptxt:", nptxt)

        if gglobs.currentDBPath is None:
            newFile = defaultFile = os.path.join(gglobs.dataPath, "notepad.notes")
        else:
            newFile = gglobs.currentDBPath + '.notes'

        fprint(header("Saving NotePad Content"))
        fprint("to File: {}\n".format(newFile))

        with open(newFile, 'a') as f:
            f.write(nptxt)


#exit GeigerLog
    def closeEvent(self, event):
        """is called via self.close! Allow to Exit unless Logging is active"""
        # event: QEvent.Close = 19 : Widget was closed

        fncname = "closeEvent: "

        setBusyCursor()

        dprint("closeEvent: event type: {}".format(event.type()))
        setDebugIndent(1)

        if gglobs.logging :
            event.ignore()
            self.showStatusMessage("Cannot exit when logging! Stop logging first")
            dprint(fncname + "ignored; Cannot exit when logging! Stop logging first")

        else:
            event.accept()                           # allow closing the window
            dprint(fncname + "accepted")

            # terminate all connected devices
            for DevName in gglobs.Devices:
                # print(fncname + "DevName: {:10s},  Connection: {}".format(DevName, gglobs.Devices[DevName][CONN]))
                if gglobs.Devices[DevName][CONN] :  self.terminateDevice(DevName)

            # close the databases for Log and His
            gsup_sql.DB_closeDatabase("Log")
            gsup_sql.DB_closeDatabase("His")

            dprint(fncname + "exiting now")

            # Force Exit
            # The standard way to exit is sys.exit(n). sys.exit() is identical to
            # raise SystemExit(). It raises a Python exception which may be caught
            # by the caller.
            # os._exit calls the C function _exit() which does an immediate program
            # termination. Note the statement "can never return".
            sys.exit(0) # otherwise sub windows won't close

        setDebugIndent(0)
        setNormalCursor()


#GraphOptions

    def changedGraphSelectedVariable(self):
        """called from the select combo for variables"""

        self.applyGraphOptions()


    def changedGraphDisplayCheckboxes(self, vname):
        """Graph varDisplayCheckbox vname has changed"""

        if not gglobs.allowGraphUpdate: return

        fncname  = "changedGraphDisplayCheckboxes: "
        oldIndex = self.select.currentIndex() # index of dropdown box selected variable
        index    = self.select.findText(vname)
        vIsChkd  = self.varDisplayCheckbox[vname].isChecked()
        # gdprint(fncname + "var:{}, longname:{}, index:{} status Chk:{}".format(vname, vname, index, vIsChkd))

        if gglobs.activeDataSource == "Log" : gglobs.varChecked4PlotLog[vname] = vIsChkd
        else:                                 gglobs.varChecked4PlotHis[vname] = vIsChkd
        # gdprint("varChecked4PlotLog", getEasyDictPrint(gglobs.varChecked4PlotLog))

        # if self.varDisplayCheckbox[vname].isChecked():
        if vIsChkd:
            # sets and enables the select combobox to the checked variable
            # thus making it to the selected variable
            self.select.model().item(index) .setEnabled(True)
            self.select                     .setCurrentIndex(index)

        else:
            # disables the unchecked variable on the select combobox,
            # and sets combobox to the first enabled entry. If none found then CPM is selected
            self.select.model().item(index) .setEnabled(False)
            foundSelVar = 0
            for i, vname in enumerate(gglobs.varsCopy):
                #print("i, vname, self.select.model().item(i) .isEnabled():", i, vname, self.select.model().item(i) .isEnabled())
                if self.select.model().item(i) .isEnabled():
                    foundSelVar = i
                    break
            if self.select.currentIndex() == index:
                self.select.setCurrentIndex(foundSelVar)

        #print("----self.select.model().item(index).isEnabled:", self.select.model().item(index).isEnabled())

        # if the index is not changed, then an explicit update is needed; otherwise
        # a changed index results in an update anyway via changedGraphSelectedVariable
        if self.select.currentIndex() == oldIndex:
            self.applyGraphOptions()


    def changedGraphOptionsMav(self, i):
        """Graph Option Mav checkbox check-status has changed"""

        #print("changedGraphOptionsMav: i:", i)
        gglobs.mavChecked  = self.mavbox.isChecked()

        if gglobs.mavChecked:           gglobs.printMavComments = True

        self.applyGraphOptions()


    def changedGraphOptionsMavText(self, i):
        """Graph Option Mav Value has changed"""

        # print("changedGraphOptionsMavText: i:", i)

        try:
            mav_val = self.mav.text().replace(",", ".").replace("-", "")
            self.mav.setText(mav_val)
            val = float(mav_val)  # can value be converted to float?
            gglobs.mav = val
        except Exception as e:
            # exceptPrint(e, "changedGraphOptionsMavText: MvAvg permits numeric values only")
            pass

        if self.mavbox.isChecked():     gglobs.printMavComments = True

        self.applyGraphOptions()


    def changedGraphOptionsAvg(self, i):
        """Graph Option Avg has changed"""

        #print("changedGraphOptionsAvg: i:", i)
        gglobs.avgChecked  = self.avgbox.isChecked()
        self.applyGraphOptions()


    def changedGraphOptionsLinFit(self, i):
        """Graph Option LinFit has changed"""

        #print("changedGraphOptionsLinFit: i:", i)
        gglobs.fitChecked = self.fitbox.isChecked()
        self.applyGraphOptions()


    def changedGraphCountUnit(self, i):
        """counter unit Graph Options for left Y-axis was changed"""

        oldYunit            = gglobs.YunitCurrent
        gglobs.YunitCurrent = str(self.yunit.currentText())
        newYunit            = gglobs.YunitCurrent
        # print("changedGraphCountUnit: i:", i, ",  oldYunit:", oldYunit, ",  newYunit:", newYunit)

        # convert Y to CPM unit if not already CPM
        # print("changedGraphCountUnit: gglobs.Ymin, gglobs.Ymax, gglobs.Sensitivity[0]", gglobs.Ymin, gglobs.Ymax, gglobs.Sensitivity[0])
        if oldYunit == "µSv/h":
            if gglobs.Ymin != None: gglobs.Ymin = gglobs.Ymin * gglobs.Sensitivity[0]
            if gglobs.Ymax != None: gglobs.Ymax = gglobs.Ymax * gglobs.Sensitivity[0]

        # convert Y to µSv/h unit if not already µSv/h
        if newYunit == "µSv/h":
            if gglobs.Ymin != None: gglobs.Ymin = gglobs.Ymin / gglobs.Sensitivity[0]
            if gglobs.Ymax != None: gglobs.Ymax = gglobs.Ymax / gglobs.Sensitivity[0]

        if gglobs.Ymin == None: self.ymin.setText("")
        else:                   self.ymin.setText("{:.5g}".format(gglobs.Ymin))

        if gglobs.Ymax == None: self.ymax.setText("")
        else:                   self.ymax.setText("{:.5g}".format(gglobs.Ymax))

        if newYunit == "µSv/h":
            for vname in ("CPM", "CPS", "CPM1st", "CPS1st", "CPM2nd", "CPS2nd", "CPM3rd", "CPS3rd"):
                gglobs.varsCopy[vname][2] = "µSv/h"

        else: # newYunit == CPM
            for vname in ("CPM", "CPM1st", "CPM2nd", "CPM3rd"):
                gglobs.varsCopy[vname][2] = "CPM"

            for vname in ("CPS", "CPS1st", "CPS2nd", "CPS3rd"):
                gglobs.varsCopy[vname][2] = "CPS"

        self.applyGraphOptions()


    def changedGraphTemperatureUnit(self, i):
        """Temperature unit Graph Options was changed"""

        #print("changedGraphTemperatureUnit: New T unit:  i:", i, str(self.y2unit.currentText()) )

        if   i == 0:    gglobs.varsCopy["Temp"][2] = "°C"
        elif i == 1:    gglobs.varsCopy["Temp"][2] = "°F"

        self.applyGraphOptions()


    def changedGraphTimeUnit(self, i):
        """recalc xmin, xmax on Time unit changes"""

        #print("-----------------------changedGraphTimeUnit: i:", i)

        if np.all(gglobs.logTime) == None: return

        gsup_plot.changeTimeUnitofPlot(self.xunit.currentText())

        self.applyGraphOptions()


    def keyPressEvent(self, event):
        """Apply Graph is only Button to accept Enter and Return key"""

        # from: http://pyqt.sourceforge.net/Docs/PyQt4/qt.html#Key-enum
        # Qt.Key_Return     0x01000004
        # Qt.Key_Enter      0x01000005  Typically located on the keypad. (= numeric keypad)
        #print("event.key():", event.key())

        if event.key() in (Qt.Key_Enter, Qt.Key_Return):
            self.applyGraphOptions()


    def setPlotVarsOnOff(self, newstate="OFF"): # 'OFF' 'ON'
        """checks or unchecks all variables from plotting"""

        gglobs.allowGraphUpdate    = False  # prevents auto-updating at every variable
        if newstate == "OFF":
            for i, vname in enumerate(gglobs.varsCopy):
                if gglobs.varsSetForCurrent[vname]:
                    self.varDisplayCheckbox[vname].setEnabled(True)     # the checkbox at the bottom of Graph dashboard - always enabled
                    self.varDisplayCheckbox[vname].setChecked(False)    # the checkbox at the bottom of Graph dashboard - unchecked
                    self.select.model().item(i)   .setEnabled(False)    # the dropdown selector for Selected Variable

                    if gglobs.activeDataSource == "Log" : gglobs.varChecked4PlotLog[vname] = False
                    else:                                 gglobs.varChecked4PlotHis[vname] = False

        else:
            for i, vname in enumerate(gglobs.varsCopy):
                if gglobs.varsSetForCurrent[vname]:
                    self.varDisplayCheckbox[vname].setEnabled(True)     # the checkbox at the bottom of Graph dashboard - always enabled
                    self.varDisplayCheckbox[vname].setChecked(True)
                    self.select.model().item(i)   .setEnabled(True)

        # makes the index of the first enabled variable as the currentindex
        # of the variable select drop-down box
        for i, vname in enumerate(gglobs.varsCopy):
            #print("----i, self.select.model().item(i).isEnabled:", i, gglobs.exgg.select.model().item(i).isEnabled())
            if self.select.model().item(i).isEnabled():
                gglobs.exgg.select.setCurrentIndex(i)
                break

        gglobs.allowGraphUpdate    = True
        self.applyGraphOptions() # not automatically done due to
                                 # blocking by gglobs.allowGraphUpdate


    def clearGraphLimits(self, printMavComments=False):
        """resets all min, max graph options to empty and plots the graph"""

        vprint("clearGraphLimits:")
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


    def plotGraph(self, dataType, full=True):
        """Plots the data as graph; dataType is Log or His"""

        if  dataType == "Log" and gglobs.logConn == None or \
            dataType == "His" and gglobs.hisConn == None:
            self.showStatusMessage("No data available")
            return

        vprint("plotGraph: dataType:", dataType)
        setDebugIndent(1)

        if dataType == "Log":
            gglobs.activeDataSource     = "Log"
            gglobs.currentConn          = gglobs.logConn
            gglobs.currentDBPath        = gglobs.logDBPath
            gglobs.currentDBData        = gglobs.logDBData
            gglobs.varsSetForCurrent    = gglobs.varsSetForLog.copy()
            varsChecked4Plot            = gglobs.varChecked4PlotLog

            self.dcfLog.setText(gglobs.currentDBPath)
            self.dcfLog.setStyleSheet("QLineEdit { background-color: #F9F4C9; color: rgb(80,80,80); }")
            self.dcfHis.setStyleSheet("QLineEdit { background-color: #DFDEDD; color: rgb(80,80,80); }")

        elif dataType == 'His':
            gglobs.activeDataSource     = "His"
            gglobs.currentConn          = gglobs.hisConn
            gglobs.currentDBPath        = gglobs.hisDBPath
            gglobs.currentDBData        = gglobs.hisDBData
            gglobs.varsSetForCurrent    = gglobs.varsSetForHis.copy()
            varsChecked4Plot            = gglobs.varChecked4PlotHis

            self.dcfHis.setText(gglobs.currentDBPath)
            self.dcfLog.setStyleSheet("QLineEdit { background-color: #DFDEDD; color: rgb(80,80,80); }")
            self.dcfHis.setStyleSheet("QLineEdit { background-color: #F9F4C9; color: rgb(80,80,80); }")

        else:
            edprint("PROGRAMMING ERROR in geigerlog:plotGraph: var dataType is:", dataType, debug=True)
            sys.exit(1)

        gglobs.allowGraphUpdate    = False  # otherwise a replot at every var happens!
        for i, vname in enumerate(gglobs.varsCopy):
            self.select.model().item(i)         .setEnabled(False)
            if gglobs.varsSetForCurrent[vname]:
                value = varsChecked4Plot[vname]   # bool
                self.varDisplayCheckbox[vname]  .setChecked(value)
                self.varDisplayCheckbox[vname]  .setEnabled(True)
                self.select.model().item(i)     .setEnabled(value)
            else:
                self.varDisplayCheckbox[vname]  .setChecked(False)
                self.varDisplayCheckbox[vname]  .setEnabled(False)
        gglobs.allowGraphUpdate    = True


        if gglobs.currentDBData is not None:
            if gglobs.currentDBData.size > 0:
                fprint(header("Plot Data"))
                fprint("from: {}".format(gglobs.currentDBPath))

        self.figure.set_facecolor('#F9F4C9') # change colorbg in graph from gray to light yellow

        self.reset_replotGraph(full=full)

        setDebugIndent(0)


    def reset_replotGraph(self, printMavComments=False, full=True):
        """resets all graph options to start conditions and plots the graph"""

        fncname = "reset_replotGraph: "

        vprint(fncname + "full: {}".format(full))
        setDebugIndent(1)

        gglobs.allowGraphUpdate    = False

        if full:
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

            self.select.                 setCurrentIndex(0) # in case no data
            self.select.                 setEnabled(True)   # required

        # if full reset to start condition
        if full:
            for i, vname in enumerate(gglobs.varsCopy):
                # cdprint("i:{:2d} vname: {:10s} varDisplayCheckbox[vname].isEnabled(): {}".format(i, vname, self.varDisplayCheckbox[vname].isEnabled()))
                if self.varDisplayCheckbox[vname].isEnabled():
                    self.varDisplayCheckbox[vname].setChecked(True)

        # Find the first enabled var and set this as selected var in dropdown box
        for i, vname in enumerate(gglobs.varsCopy):
            # cdprint("i:{:2d} vname: {:10s} select.model().item(i).isEnabled: {}".format(i, vname, gglobs.exgg.select.model().item(i).isEnabled()))
            if self.select.model().item(i).isEnabled():
                self.select.setCurrentIndex(i)
                break

        gglobs.mavChecked          = False
        self.mavbox.                 setChecked(gglobs.mavChecked)

        gglobs.mav                 = gglobs.mav_initial
        self.mav.                    setText("{:0.0f}".format(gglobs.mav_initial))

        gglobs.avgChecked          = False
        self.avgbox.                 setChecked(gglobs.avgChecked)

        gglobs.fitChecked          = False
        self.fitbox.                 setChecked(gglobs.fitChecked)

        gglobs.varsCopy            = gglobs.varsDefault.copy() # reset colors and linetype

        gglobs.allowGraphUpdate    = True

        self.updateDisplayVariableValue()

        self.applyGraphOptions()

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
                efprint("Graph: Wrong numbers: Time Min must be less than Time Max")
                return

        gglobs.Xunit     = xunit

    # y
        try:    gglobs.Ymin      = float(ymin)
        except: gglobs.Ymin      = None

        try:    gglobs.Ymax      = float(ymax)
        except: gglobs.Ymax      = None

        if gglobs.Ymin != None and gglobs.Ymax != None:
            if gglobs.Ymin >= gglobs.Ymax:
                efprint("Graph: Wrong numbers: Count Rate min must be less than Count Rate max")
                return

        gglobs.Yunit     = yunit

    # y2
        try:    gglobs.Y2min      = float(y2min)
        except: gglobs.Y2min      = None

        try:    gglobs.Y2max      = float(y2max)
        except: gglobs.Y2max      = None

        if gglobs.Y2min != None and gglobs.Y2max != None:
            if gglobs.Y2min >= gglobs.Y2max:
                efprint("Graph: Wrong numbers: Ambient min must be less than Ambient max")
                return

    # # mav
    #     try:    gglobs.mav     = float(mav)
    #     except: gglobs.mav     = gglobs.mav_initial

    # color
        colorName = gglobs.varsCopy[getNameSelectedVar()][3]
        self.btnColor.setText("")
        self.btnColor.setStyleSheet("QLabel { border: 1px solid silver;  border-radius: 3px; background-color: %s ; }" % (colorName))
        addMenuTip(self.btnColor, self.btnColorText + colorName)

    # replot
        gsup_plot.makePlot()
        self.updateDisplayVariableValue()

        gglobs.flagGetGraph = True


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
    def getFileHistory(self, source):
        """getFileHistory from source. source is one out of:
        - "Device"
        - "Database"
        - "Binary File"
        - "Parsed File"
        no return; data stored in global variables"""

        fncname = "getFileHistory: "

    #
    # make the filedialog
    #
        # conditions
        if   source == "Database":
            # there must be an existing '*hisdb' file;
            # writing to it is not necessary; it will not be modified
            dlg=QFileDialog(caption = "Get History - Select from Existing Database File", options=QFileDialog.DontUseNativeDialog)
            dlg.setFileMode(QFileDialog.ExistingFile)
            dlg.setNameFilter("History Files (*.hisdb);;Log Files (*.logdb);;History or Log Files (*.hisdb *.logdb)")

        elif source == "Binary File":
            # there must be an existing, readable '*.bin' file,
            # and it must be allowed to write .hisdb files
            # the bin file will remain unchanged
            dlg=QFileDialog(caption = "Get History - Select from Existing Binary File", options=QFileDialog.DontUseNativeDialog)
            dlg.setFileMode(QFileDialog.ExistingFile)
            dlg.setNameFilter("History Files (*.bin *.gmc)")

        elif source == "Parsed File":
            # there must be an existing, readable '*.his' file
            # and it must be allowed to write .hisdb files
            # the his file will remain unchanged
            dlg=QFileDialog(caption= "Get History - Select from Existing *.his or other CSV File", options=QFileDialog.DontUseNativeDialog)
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
            dlg=QFileDialog(caption = "Get History - Select from Existing Gamma Scout *.dat File", options=QFileDialog.DontUseNativeDialog)
            dlg.setFileMode(QFileDialog.ExistingFile)
            dlg.setNameFilter("History Files (*.dat)")

        elif source == "AMDeviceCAM":  # an Manu device for CAM data
            # may use existing or new .hisdb file, but must be allowed to overwrite this file
            # an existing hisdb file will be overwritten
            dlg=QFileDialog(caption = "Get History from Manu Device - enter new filename or select from existing", options=QFileDialog.DontUseNativeDialog)
            dlg.setFileMode(QFileDialog.AnyFile)
            dlg.setNameFilter("History Files (*.hisdb)")

        elif source == "AMDeviceCPS":  # an Manu device for CPS data
            # may use existing or new .hisdb file, but must be allowed to overwrite this file
            # an existing hisdb file will be overwritten
            dlg=QFileDialog(caption = "Get History from Manu Device - enter new filename or select from existing", options=QFileDialog.DontUseNativeDialog)
            dlg.setFileMode(QFileDialog.AnyFile)
            dlg.setNameFilter("History Files (*.hisdb)")

        #~ elif source == "AMDatFile":
            #~ ####### not valid -- placeholder for Manu !!!!!!!! ############
            #~ # wird es auch nicht geben, da CSV Files verwendet werden !!!
            #~ #
            #~ # there must be an existing, readable '*.dat' file, created by
            #~ # memory dumping of a Gamm Scout device,
            #~ # and it must be allowed to write .hisdb files
            #~ # the dat file will remain unchanged
            #~ dlg=QFileDialog(caption = "Get History - Select from Existing Gamma Scout *.dat File", options=QFileDialog.DontUseNativeDialog)
            #~ dlg.setFileMode(QFileDialog.ExistingFile)
            #~ dlg.setNameFilter("History Files (*.dat)")

        elif source == "AMFileCAM":
            # there must be an existing, readable '*.CAM' file, created by
            # e.g. downloading from an Manu device,
            # and it must be allowed to write .hisdb files
            # the *.CAM file will remain unchanged
            dlg=QFileDialog(caption = "Get History - Select from Existing Manu binary *.CAM File", options=QFileDialog.DontUseNativeDialog)
            dlg.setFileMode(QFileDialog.ExistingFile)
            dlg.setNameFilter("History Binary Files (*.CAM)")

        elif source == "AMFileCPS":
            # there must be an existing, readable '*.CPS' file, created by
            # e.g. downloading from an Manu device,
            # and it must be allowed to write .hisdb files
            # the *.CPS file will remain unchanged
            dlg=QFileDialog(caption = "Get History - Select from Existing Manu binary *.CPS File", options=QFileDialog.DontUseNativeDialog)
            dlg.setFileMode(QFileDialog.ExistingFile)
            dlg.setNameFilter("History Binary Files (*.CPS)")

        else:
            printProgError("getFileHistory: Filedialog: Wrong source: ", source)

        dlg.setViewMode     (QFileDialog.Detail)
        dlg.setWindowIcon   (self.iconGeigerLog)
        dlg.setDirectory    (gglobs.fileDialogDir)

        dlg.setFixedSize(950, 550)

        # Execute dialog
        if dlg.exec() == QDialog.Accepted:  pass     # QDialog Accepted
        else:                                return   # QDialog Rejected
    ### end filedialog -  a file was selected

    #
    # Process the selected file
    #
        while True:
            fprint(header("Get History from {}".format(source)))
            dprint(fncname + "from source: ", source)
            setDebugIndent(1)

            gglobs.fileDialogDir = dlg.directory().path() # remember the directory
            #print("getFileHistory: fileDialogDir:", gglobs.fileDialogDir)

            fnames      = dlg.selectedFiles()
            fname       = str(fnames[0])                # file path
            fext        = os.path.splitext(fname)[1]    # file ext
            fname_base  = os.path.splitext(fname)[0]    # file basename with path w/o ext

            vprint(fncname + "file name:   '{}'"                   .format(fname))
            wprint(fncname + "fname_base:  '{}', fname_ext: '{}'"  .format(fname_base, fext))

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
                printProgError(fncname + "Processing Selected File: Wrong source: ", source)


            # Messagebox re Overwriting file
            if source in ("Device", "GSDevice", "AMDeviceCAM", "AMDeviceCPS"):
                if os.path.isfile(gglobs.hisDBPath):
                    msg = QMessageBox()
                    msg.setIcon(QMessageBox.Critical)
                    msg.setWindowTitle("CAUTION")
                    critical  = """You selected an existing file, which will be <b>OVERWRITTEN</b> if you continue. Please confirm with OK.
                                    \n\nOtherwise click Cancel and enter a new filename in the Get History from Device dialog."""
                    msg.setText(critical)
                    msg.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
                    msg.setDefaultButton(QMessageBox.Cancel)
                    msg.setEscapeButton(QMessageBox.Cancel)
                    retval = msg.exec()

                    if retval != 1024:
                        fprint("Get History is cancelled")
                        break

            gglobs.currentDBPath   = gglobs.hisDBPath

            #dprint("getFileHistory: gglobs.binFilePath:     ", gglobs.binFilePath)
            #dprint("getFileHistory: gglobs.hisFilePath:     ", gglobs.hisFilePath)
            #dprint("getFileHistory: gglobs.hisDBPath:       ", gglobs.hisDBPath)
            #dprint("getFileHistory: gglobs.currentDBPath:   ", gglobs.currentDBPath)

            self.setBusyCursor()
            hidbp = "History database: {}"      .format(gglobs.hisDBPath)
            fprint(hidbp)
            dprint(fncname + hidbp)

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
                    fprint("Database creation was cancelled")
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
                error, message = gdev_gscout.GSmakeHistory(source)
                if error == -1:                                # a severe error
                    efprint(message)
                    break

            # Make Hist for source = AmbioMon device
            elif source in ("AMDeviceCAM", "AMDeviceCPS"):
                # error, message = gdev_Manu.makeAmbioHistory(source, gglobs.AmbioDeviceName)
                error, message = gdev_Manu.makeAmbioHistory(source, gglobs.Devices["AmbioMon"][DNAME])
                if error == -1:                                # a severe error
                    efprint(message)
                    break

            # Make Hist for source = AmbioMon binary file
            elif source in ("AMFileCAM", "AMFileCPS"):
                # error, message = gdev_Manu.makeAmbioHistory(source, gglobs.AmbioDeviceName)
                error, message = gdev_Manu.makeAmbioHistory(source, gglobs.Devices["AmbioMon"][DNAME])
                if error == -1:                                # a severe error
                    efprint(message)
                    break

            gglobs.hisDBData, varsFromDB = gsup_sql.getDataFromDatabase("His") # also creates varchecked
            for vname in gglobs.varsCopy:
                if varsFromDB[vname]:           gglobs.varsSetForHis[vname] = True
                if gglobs.varsSetForHis[vname]: gglobs.varChecked4PlotHis[vname] = True

            self.plotGraph("His")

            self.checkLoggingState()
            break

        self.setNormalCursor()

        setDebugIndent(0)


    def setLogCycle(self):
        """Set logCycle"""

        fncname = "setLogCycle: "

        dprint(fncname)
        setDebugIndent(1)

        lctime     = QLabel("Log Cycle [s]  \n(0.100 ... 1000)   ")
        lctime.setAlignment(Qt.AlignLeft)

        self.ctime = QLineEdit()
        validator  = QDoubleValidator(0.1, 1000, 3, self.ctime)
        self.ctime.setValidator(validator)
        self.ctime.setToolTip('The log cycle in seconds. Changeable only when not logging.')
        self.ctime.setText("{:0.5g}".format(gglobs.logCycle))

        graphOptions=QGridLayout()
        graphOptions.addWidget(lctime,                  0, 0)
        graphOptions.addWidget(self.ctime,              0, 1)

        d = QDialog() # set parent empty to popup in center of screen
        d.setWindowIcon(self.iconGeigerLog)
        d.setWindowTitle("Set Log Cycle")
        d.setWindowModality(Qt.WindowModal)

        self.bbox = QDialogButtonBox()
        self.bbox.setStandardButtons(QDialogButtonBox.Cancel | QDialogButtonBox.Ok )
        self.bbox.accepted.connect(lambda: d.done(100))
        self.bbox.rejected.connect(lambda: d.done(0))

        gglobs.btn = self.bbox.button(QDialogButtonBox.Ok)
        gglobs.btn.setEnabled(True)

        layoutV = QVBoxLayout(d)
        layoutV.addLayout(graphOptions)
        layoutV.addWidget(self.bbox)

        self.ctime.textChanged.connect(self.check_state) # last chance
        self.ctime.textChanged.emit   (self.ctime.text())

        if gglobs.logging:
            gglobs.btn.setEnabled(False)
            self.ctime.setEnabled(False)
            self.ctime.setStyleSheet('QLineEdit { background-color: %s;  }' % ("#e0e0e0",))

        retval = d.exec()
        #print("retval:", retval)

        if retval == 0:
            dprint(fncname + "Cancel. Cycle time unchanged: ", gglobs.logCycle) # Cancel or ESC
        else:
            # change the cycle time
            oldlogCycle = gglobs.logCycle
            logCycle    = self.ctime.text().replace(",", ".")  #replace comma with dot
            try:    lc  = round(float(logCycle), 3)
            except: lc  = oldlogCycle

            gglobs.logCycle = lc
            self.showTimingSetting(gglobs.logCycle)
            dprint(fncname + "ok, new cycle time: ", gglobs.logCycle)

            # update database with logcyle
            if gglobs.logConn != None:
                gsup_sql.DB_updateLogcycle(gglobs.logConn, gglobs.logCycle)

        setDebugIndent(0)


    def check_state(self, *args, **kwargs):

        sender = self.sender()

        print("sender.text():", sender.text())
        print("args:", args)
        print("kwargs:", kwargs)

        try:
            v = float(sender.text().replace(",", "."))
            if   v < 0.1:       state = 0   # too low
            elif v > 1000:      state = 0   # too high
            else:               state = 2   # ok
        except:
            state = 0                       # wrong data

        # print("QValidator.Acceptable:", QValidator.Acceptable)

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
            if gglobs.varMappedCount == 0:
                efprint("WARNING: No variables for logging available; Logging is not possible!")
                qefprint("Please check configuration if this is unexpected !")
                break

            # all clear, go for it
            gglobs.logging       = True          # set early, to allow threads to get data
            gglobs.LogReadings   = 0
            gglobs.currentDBPath = gglobs.logDBPath

            # make output like:
            #~#DEVICES, 2021-02-04 11:48:35, Connected: GMC         : CPM CPS
            #~#DEVICES, 2021-02-04 11:48:35, Connected: Simul       : CPM CPS CPM1st CPS1st CPM2nd CPS2nd CPM3rd CPS3rd
            #~#DEVICES, 2021-02-04 11:48:35, Connected: MiniMon     : Temp Humid Xtra
            #~#LOGGING, 2021-02-04 11:48:35, Start @Cycle: 1.0 sec
            comments  = []
            printcom  = ""
            for DevName in gglobs.Devices:
                if gglobs.DevVarsAsText[DevName] != None:
                    cinfo     = "Connected: {:11s} : {}" .format(DevName, gglobs.DevVarsAsText[DevName])
                    comments.append(["DEVICES", "NOW", "localtime", cinfo])
                    printcom += "#DEVICES, {}, {}\n"     .format(stime(), cinfo)

            cinfo     = "Start @Cycle: {} sec"   .format(gglobs.logCycle)
            comments.append(["LOGGING", "NOW", "localtime", cinfo])
            printcom += "#LOGGING, {}, {}"       .format(stime(), cinfo)

            gsup_sql.DB_insertComments(gglobs.logConn, comments)
            logPrint(printcom)
            fprint  (printcom)

            cleanupDevices("before")

        # STARTING
            self.checkLoggingState()
            self.plotGraph("Log", full=False)                   # initialize graph settings
            self.timer0.start(int(gglobs.logCycle * 1000))      # timer time is in ms; logCycle in sec
            self.runLoggingCycle()                                  # make first call now; timer fires only AFTER 1st period!
            dprint("startLogging: Logging now; Timer is started with cycle {} sec.".format(gglobs.logCycle))

            break

        setDebugIndent(0)


    def stopLogging(self):
        """Stops the logging"""

        if not gglobs.logging: return

        fncname = "stopLogging: "
        dprint(fncname)
        setDebugIndent(1)

        fprint(header("Stop Logging"))
        self.timer0.stop()
        gglobs.logging = False
        dprint(fncname + "Logging is stopped")

        writestring  = "#LOGGING, {}, Stop".format(stime())
        logPrint(writestring)
        fprint(writestring)

        gsup_sql.DB_insertComments(gglobs.logConn, [["LOGGING", "NOW", "localtime", "Stop"]])

        cleanupDevices("after")

        self.checkLoggingState()
        self.labelSelVar.setStyleSheet('color:darkgray;')
        self.updateDisplayVariableValue()

        # For the the Rad World Map update - will make it wait for full cycle
        gglobs.RWMmapLastUpdate = None

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

        info        = ("Enter your comment to the <b>{}</b> file: " + "&nbsp;"*100).format(dataType)

        d           = QInputDialog()
        # it looks like QInputDialog() always blocks outside clicking????
        #d.setWindowModality(Qt.WindowModal) #Qt.ApplicationModal, Qt.NonModal          # no clicking outside
        #d.setWindowModality(Qt.ApplicationModal) #Qt.ApplicationModal, Qt.NonModal     # no clicking outside
        d.setWindowModality(Qt.NonModal) #Qt.ApplicationModal,                          # no clicking outside
        dtext, ok   = d.getText(None, 'Add a Comment', info)

        if ok:
            dtext       = str(dtext)
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


    def addGMC_Error(self, errtext):
        """Adds ERROR info from gdev_gmc as comment to the current log"""

        logPrint("#GMC_ERROR, {}, {}".format(stime(), errtext))   # to the LogPad

        if not gglobs.logConn is None:                            # to the DB
            gsup_sql.DB_insertComments(gglobs.logConn, [["DevERROR", "NOW", "localtime", errtext]])


    def addMsgToLog(self, type, msg):
        """Adds message to the current log
        type: like 'Success', 'Failure'"""

        logPrint("#{}, {}, {}".format(type, stime(), msg))        # to the LogPad
        if not gglobs.logConn is None:                            # to the DB
            gsup_sql.DB_insertComments(gglobs.logConn, [[type, "NOW", "localtime", msg]])


#
# Update the Timing setting in the dashboard
#
    def showTimingSetting(self, logCycle):
        """update the Timings shown under Data"""

        # self.btnSetCycle.setText("Cycle: {:0.3g} s".format(logCycle))
        # self.btnSetCycle.setText("Log Cycle: {:0.3g} s".format(logCycle))
        self.btnSetCycle.setText("Log Cycle: {:0.5g} s".format(logCycle))
        # self.btnSetCycle.setText("Log Cycle: {:0.3f} s".format(logCycle))


#
# Update the display
#
    def updateDisplayVariableValue(self):
        """
        update: the Selected Variable value displayed in the Graph LastValue box
        and   : the Display Last Log Values window
        return: nothing
        """

        #***********************************************************************************************

        def getStatusTip(counttype, svalue, scaleIndex):

            if counttype == "M": value = svalue         # CPM
            else:                value = svalue * 60    # CPS

            statusTip  = "{:0.2f} CPM"     .format(value)
            statusTip += " = {:0.2f} CPS"  .format(value / 60)
            statusTip += " = {:0.2f} µSv/h".format(value * scale[scaleIndex])
            statusTip += " = {:0.2f} mSv/a".format(value * scale[scaleIndex] / 1000 * 24 * 365.25)

            return statusTip

        def getVarText(selUnit1, value, scaleIndex, counttype):

            # if selUnit1 == "CPM":   varText = "{:0.0f} CP{}".format(value, counttype)
            if selUnit1 == "CPM":   varText = "{:0.5g} CP{}".format(value, counttype)
            else:                   varText = "{:0.5g} µSv/h".format(value * 60 * scale[scaleIndex])
            # if selUnit1 == "CPM":   varText = "{:0.3g} CP{}".format(value, counttype)
            # else:                   varText = "{:0.3g} µSv/h".format(value * 60 * scale[scaleIndex])

            return varText

        #***********************************************************************************************

        fncname = "updateDisplayVariableValue: "

        if gglobs.lastLogValues == None:
            self.labelSelVar.setText(" --- ")
            addMenuTip(self.labelSelVar, "Shows Last Value of the Selected Variable when logging")
            return

        # updates DisplayVariables Window
        # see function displayLastValues() in gsup_tools.py
        if gglobs.displayLastValsIsOn:
            try:
                for vi, vname in enumerate(gglobs.varsCopy):
                    # print("vi", vi, "vname: ", vname, ", self.vlabels[vi]", self.vlabels[vi])
                    if self.vlabels[vi] is None: continue
                    gsup_tools.setLastValues(vi, vname)

            except Exception as e:
                msg = "Exception updateDisplayVariableValue:"
                exceptPrint(e, msg)

        # selected variable: when logging: black on yellow background, else with dark.grey on grey
        if gglobs.logging and gglobs.activeDataSource == "Log":
            self.labelSelVar.setStyleSheet('color: black; background-color: #F4D345;')

        elif gglobs.activeDataSource == "His":
            self.labelSelVar.setText(" --- ")
            self.labelSelVar.setStyleSheet('color:darkgray;')
            addMenuTip(self.labelSelVar, "")
            return

        selVar    = self.select.currentText()         # selected variable
        selUnit1  = self.yunit .currentText()
        selUnit2  = self.y2unit.currentText()
        varText   = " --- "

        scale = [None] * 4
        for i in range(0, 4):
            if gglobs.Sensitivity[i] == "auto":  scale[i] = 1 / gglobs.DefaultSens[i]
            else:                                scale[i] = 1 / gglobs.Sensitivity[i]
            # print(fncname + "scale[{}]: {}".format(i, scale[i]))

        value       = gglobs.lastLogValues[selVar]
        statusTip   = ""
        if not np.isnan(value):               # on NAN no update, keep the old value

            if   selVar == "CPM":
                varText   = getVarText(selUnit1, value, 0, "M")
                statusTip = getStatusTip("M", value, 0)

            elif selVar == "CPS":
                varText   = getVarText(selUnit1, value, 0, "S")
                statusTip = getStatusTip("S", value, 0)

            elif selVar == "CPM1st":
                varText   = getVarText(selUnit1, value, 1, "M")
                statusTip = getStatusTip("M", value, 1)

            elif selVar == "CPS1st":
                varText   = getVarText(selUnit1, value, 1, "S")
                statusTip = getStatusTip("S", value, 1)

            elif selVar == "CPM2nd":
                varText   = getVarText(selUnit1, value, 2, "M")
                statusTip = getStatusTip("M", value, 2)

            elif selVar == "CPS2nd":
                varText   = getVarText(selUnit1, value, 2, "S")
                statusTip = getStatusTip("S", value, 2)

            elif selVar == "CPM3rd":
                varText   = getVarText(selUnit1, value, 3, "M")
                statusTip = getStatusTip("M", value, 3)

            elif selVar == "CPS3rd":
                varText   = getVarText(selUnit1, value, 3, "S")
                statusTip = getStatusTip("S", value, 3)

            elif selVar == "Temp":
                if selUnit2 == "°C":  varText = "{:0.2f} °C".format(value)
                else:                 varText = "{:0.2f} °F".format(value / 5 * 9 + 32)
                statusTip  = "{:0.2f} °C = {:0.2f} °F".format(value, value / 5 * 9 + 32)

            elif selVar == "Press":
                varText   = "{:0.2f} hPa".format(value)
                statusTip = "{:0.2f} hPa = {:0.2f} mbar".format(value, value)

            elif selVar == "Humid":
                varText   = "{:0.2f} %".format(value)
                statusTip = "{:0.2f} %".format(value)

            elif selVar == "Xtra":
                varText   = "{:0.2f}".format(value)
                statusTip = "{:0.2f}".format(value)

        self.labelSelVar.setText(varText)
        addMenuTip(self.labelSelVar, statusTip)

#
# Get Log file
#
    def quickLog(self):
        """Starts logging with empty default log file 'default.log'"""

        fncname = "quickLog: "

        fprint(header("Quick Log"))
        msg = "Start logging using Quick Log database 'default.logdb'"
        fprint(msg)
        dprint(fncname + msg)
        setDebugIndent(1)

        gglobs.logDBPath   = os.path.join(gglobs.dataPath, "default.logdb")
        gsup_sql.DB_deleteDatabase("Log", gglobs.logDBPath)
        self.getFileLog(defaultLogDBPath = gglobs.logDBPath) # get default.logdb
        self.startLogging()

        setDebugIndent(0)


    def getFileLog(self, defaultLogDBPath = False, source="Database"):
        """Load existing file for logging, or create new one.
        source can be:
        - "Database" (which is *.logdb file )
        - "CSV File" (which is *.log or *.csv file)
        """

        #
        # Get logfile filename/path
        #
        # If a default logfile is given; use it
        if defaultLogDBPath != False:
            gglobs.logFilePath      = None
            gglobs.logDBPath        = defaultLogDBPath
            #dprint("getFileLog: using defaultLogDBPath: ", gglobs.logDBPath)

        # else run dialog to get one
        else:
            if   source == "Database":
                # may use existing or new .logdb file, but must be allowed to overwrite this file
                # an existing logdb file allows appending with new data
                dlg=QFileDialog(caption= "Get Log - Enter New Filename or Select from Existing", options=QFileDialog.DontUseNativeDialog)
                dlg.setFileMode(QFileDialog.AnyFile)

                dlg.setNameFilter("Log Files (*.logdb)")

            elif source == "CSV File":
                # there must be an existing, readable csv file with extension '*.log' or '*.csv' or '*.txt' or '*.notes' file
                # the csv file will remain unchanged
                dlg=QFileDialog(caption = "Get Log - Select from Existing *.log or other CSV File", options=QFileDialog.DontUseNativeDialog)
                dlg.setFileMode(QFileDialog.ExistingFile)
                dlg.setNameFilter("Log Files (*.log *.csv *.txt *.notes)")

            else:
                printProgError("undefined source:", source)

            dlg.setViewMode(QFileDialog.Detail)
            dlg.setWindowIcon(self.iconGeigerLog)
            dlg.setDirectory(gglobs.fileDialogDir)

            dlg.setFixedSize(950, 550)

            # Execute dialog
            if dlg.exec() == QDialog.Accepted:  pass     # QDialog Accepted
            else:                               return   # QDialog Rejected

            ### end filedialog -  a file was selected

            gglobs.fileDialogDir = dlg.directory().path()
            #print("dlg.directory().path():", dlg.directory().path())

            fnames      = dlg.selectedFiles()
            fname       = str(fnames[0])                    # file path
            fext        = os.path.splitext(fname)[1]        # file extension
            fname_base  = os.path.splitext(fname)[0]        # file basename with path w/o ext

            if   source == "Database":  # extension is .logdb
                gglobs.logFilePath = None
                if fext != ".logdb":    gglobs.logDBPath   = fname + ".logdb" # file has any extension or none
                else:                   gglobs.logDBPath   = fname            # file already has .logdb extension

            elif source == "CSV File":  # extension is .log, .csv, .txt
                gglobs.logFilePath = fname
                gglobs.logDBPath   = fname_base + ".logdb"
                if not isFileReadable (gglobs.logFilePath):   return

            if source == "Database":
                # if file exists, give warning on overwriting
                if os.path.isfile(gglobs.logDBPath):
                    msg = QMessageBox()
                    msg.setIcon(QMessageBox.Warning)
                    msg.setWindowTitle("CAUTION")
                    critical  = """You selected an existing file, which will be modified \
                                when logging by <b>APPENDING</b> new data to it.
                                \n\nPlease confirm with OK.
                                \n\nOtherwise click Cancel and enter a new filename in the Get Log dialog."""
                    msg.setText(critical)
                    msg.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
                    msg.setDefaultButton(QMessageBox.Cancel)

                    msg.setEscapeButton(QMessageBox.Cancel)
                    retval = msg.exec()

                    if retval != 1024:
                        return

        # Done getting LogFile   ##############################################

        self.setBusyCursor()

        gglobs.currentDBPath   = gglobs.logDBPath

        fprint(header("Get Log"))
        fprint("Log database: {}".                               format(gglobs.logDBPath))
        if defaultLogDBPath == False:
            dprint("getFileLog: use selected Log DB file: '{}'". format(gglobs.logDBPath))
        else:
            dprint("getFileLog: use default Log DB file: '{}'".  format(defaultLogDBPath))
        setDebugIndent(1)

        #dprint("getFileLog: gglobs.logFilePath:     ", gglobs.logFilePath)
        #dprint("getFileLog: gglobs.logDBPath:       ", gglobs.logDBPath)
        #dprint("getFileLog: gglobs.currentDBPath:   ", gglobs.currentDBPath)

        if gglobs.logging:   self.stopLogging()
        self.dcfLog.setText(gglobs.logDBPath)
        self.clearLogPad()

        # an existing classic log was selected. It will be converted to a database;
        # any previous conversion will be deleted first
        if gglobs.logFilePath != None:
            fprint("Created from file {}".format(gglobs.logFilePath))
            # delete old database
            gsup_sql.DB_deleteDatabase("Log", gglobs.logDBPath)

            # open new database
            gglobs.logConn      = gsup_sql.DB_openDatabase(gglobs.logConn, gglobs.logDBPath)

            # read data from CSV file into database
            self.setNormalCursor()

            if gsup_sql.getCSV(gglobs.logFilePath):
                self.setBusyCursor()
                gsup_sql.DB_convertCSVtoDB(gglobs.logConn, gglobs.logFilePath)
            else:
                fprint("Database creation was cancelled")
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
################
        gglobs.logDBData, varsFromDB = gsup_sql.getDataFromDatabase("Log")
        for vname in gglobs.varsCopy:
            if varsFromDB[vname]:           gglobs.varsSetForLog[vname] = True
            if gglobs.varsSetForLog[vname]: gglobs.varChecked4PlotLog[vname] = True

        # add the default logCycle as read from the database
        testcycle = gsup_sql.DB_readLogcycle(gglobs.logConn)    # testcycle is type float
        #print("testcycle:",testcycle, type(testcycle))
        if testcycle is None:       # old DB may not have one
            gsup_sql.DB_insertLogcycle(gglobs.logConn, gglobs.logCycle)
        else:
            gglobs.logCycle = testcycle
            self.showTimingSetting(gglobs.logCycle)

        self.plotGraph("Log")
        self.checkLoggingState()
        self.setNormalCursor()

        setDebugIndent(0)


#
# Show data from Log, His, and Bin files ######################################
#
    def showData(self, dataSource=None, full=True):
        """Print Log or His Data to notepad, as full file or excerpt.
        dataSource can be 'Log' or 'His' or 'HisBin' (for binary data) or
        HisParse or PlotData"""

        # print("showData dataSource: {}, fullflag: {}".format(dataSource, full))
        if dataSource == None:
            if    gglobs.activeDataSource == "Log": dataSource = "Log"
            else:                                   dataSource = "His"
        # print("\n\nshowData dataSource: {}, fullflag: {}".format(dataSource, full))

        if gglobs.activeDataSource == None:
            self.showStatusMessage("No data available")
            return

        textprintButtonDef  = "Data"
        textprintButtonStop = "STOP"

        # stop printing
        if self.btnPrintFullData.text() == textprintButtonStop:
            gglobs.stopPrinting = True
            # print("gglobs.stopPrinting: ", gglobs.stopPrinting)
            return

        if full:
            # switch button mode to "STOP"
            self.btnPrintFullData.setStyleSheet('QPushButton {color: blue; background-color:white; font:bold;}')
            self.btnPrintFullData.setText(textprintButtonStop)

        if   dataSource == "Log":          self.showDBData(DBtype="Log",     DBpath=gglobs.logDBPath, DBconn=gglobs.logConn, varchecked=gglobs.varsSetForLog, full=full)
        elif dataSource == "His":          self.showDBData(DBtype="History", DBpath=gglobs.hisDBPath, DBconn=gglobs.hisConn, varchecked=gglobs.varsSetForHis, full=full)
        elif dataSource == "HisBin":       gsup_sql.createLstFromDB(full=full)
        elif dataSource == "HisParse":     gsup_sql.createParseFromDB(full=full)
        elif dataSource == "PlotData":     gsup_tools.fprintPlotData()              # print data as shown in plot

        # reset button to default
        self.btnPrintFullData.setStyleSheet('QPushButton {}')
        self.btnPrintFullData.setText(textprintButtonDef)


    def showDBData(self, DBtype=None, DBpath=None, DBconn=None, varchecked=None, full=True):
        """ print logged data from Log or Hist to notepad"""

        fncname = "showDBData: "

        if DBconn == None:
            self.showStatusMessage("No data available")
            return

        self.setBusyCursor()

        if full:    addp = ""
        else:       addp = " Excerpt"
        fprint(header("Show {} Data".format(DBtype) + addp))
        fprint("from: {}\n".format(DBpath))

        sql, ruler = gsup_sql.getShowCompactDataSql(varchecked)

        fprint(ruler)
        # dprint(fncname + "ruler: ", ruler)

        if full:
            data = gsup_sql.DB_readData(DBconn, sql, limit=0)
            # for a in data:   print(fncname + "sql dataline:", a)

            counter      = 0
            counter_max  = 100
            update       = 900
            update_max   = 1000
            datastring   = ""
            gglobs.stopPrinting = False
            for a in data:
                datastring += a + "\n"
                if counter >= counter_max:
                    fprint(datastring[:-1])
                    fprint(ruler)
                    datastring = ""
                    counter    = 0

                if update >= update_max:
                    Qt_update()
                    update = 0

                if gglobs.stopPrinting: break
                counter     += 1
                update      += 1

            gglobs.stopPrinting = False
            fprint(datastring[:-1])

        else:
            fprint(self.getExcerptLines(sql, DBconn))

        fprint(ruler)

        self.setNormalCursor()


    def showDBTags(self, DBtype=None):
        """print comments from DB, either DBtype=Log or =History"""

        if DBtype == "Log":
            DBConn = gglobs.logConn
            DBPath = gglobs.logDBPath
        else:   # "History"
            DBConn = gglobs.hisConn
            DBPath = gglobs.hisDBPath

        if DBConn == None:
            self.showStatusMessage("No data available")
            return

        self.setBusyCursor()

        fprint(header("Show {} Tags and Comments".format(DBtype)))
        fprint("from: {}\n".format(DBPath))
        rows = gsup_sql.DB_readComments(DBConn)
        fprint("\n".join(rows))

        self.setNormalCursor()


    def getExcerptLines(self, sql, DB_Conn, lmax=10):
        """get first and last lines from the db"""

        if DB_Conn == None:  return ""

        excLines  = gsup_sql.DB_readData(DB_Conn, sql, limit=lmax)
        # for a in excLines: print(a)

        lenall    = len(excLines)
        # print("lenall", lenall)
        if lenall == 0:      return ""      # no data

        plines = ""
        if lenall < lmax * 2:
            for i in range(0, lenall):   plines += excLines[i] + "\n"

        else:
            for a in excLines[0:lmax]:   plines += a + "\n"
            plines +=                         "      ...\n"
            for a in excLines[-lmax:]:   plines += a + "\n"

        return plines[:-1] # remove "\n"


# printing to hardware printer or pdf file
    def printNotePad(self):
        """prints NotePad content to printer or pdf"""

        if gglobs.currentDBPath is None:
            defaultPDF = defaultFile = os.path.join(gglobs.dataPath, "notepad.pdf")
        else:
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


    def setTemporaryTubeSensitivities(self):
        """Dialog to set tube sensitivities for all tubes temporarily"""

        fncname = "setTemporaryTubeSensitivities: "

        # setting the scaling factor (needed if no device connected)
        scale = [None] * 4
        for i in range(0, 4):
            if gglobs.Sensitivity[i] == "auto":    scale[i] = gglobs.DefaultSens[i]
            else:                                  scale[i] = gglobs.Sensitivity[i]

        dprint(fncname)
        setDebugIndent(1)

        # Comment
        intro = """
<p>Allows to set the sensitivities for all Geiger tubes.
<p>This is temporary for this run only. For a permanent change edit the GeigerLog configuration file 'geigerlog.cfg'.
<p>Sensititivities are in units of <b>CPM / (µSv/h) </b>.
<p><b>NOTE:</b>
If no data for the tube's sensitivity arre avail&shy;able, then take guidance
from the following numbers. Find details in the GeigerLog manual - Chapter Calibration.</p>
<p>For a tube like M4011 and a radiation scenario like:
<pre>
    Cs-137 : 154 CPM / (µSv/h)  (100%)
    Co-60  : 132 CPM / (µSv/h)  ( 86%)
    Ra-226 : 174 CPM / (µSv/h)  (113%)

</pre>
</p>
"""

    # Intro
        lcomment = QLabel(intro)
        lcomment.setMaximumWidth(400)
        lcomment.setWordWrap(True)

    # Def tube
        ltubeDef = QLabel("CPM / CPS  ")
        ltubeDef.setAlignment(Qt.AlignLeft)

        etubeDef = QLineEdit()
        etubeDef.setToolTip('Code: M / S')
        etubeDef.setText("{:0.6g}".format(scale[0]))

    # 1st tube
        ltube1st = QLabel("CPM1st / CPS1st")
        ltube1st.setAlignment(Qt.AlignLeft)

        etube1st = QLineEdit()
        etube1st.setToolTip('Code: M1 / S1')
        etube1st.setText("{:0.6g}".format(scale[1]))

    # 2nd tube
        ltube2nd = QLabel("CPM2nd / CPS2nd  ")
        ltube2nd.setAlignment(Qt.AlignLeft)

        etube2nd = QLineEdit()
        etube2nd.setToolTip('Code: M2 / S2')
        etube2nd.setText("{:0.6g}".format(scale[2]))

    # 3rd tube
        ltube3rd = QLabel("CPM3rd / CPS3rd  ")
        ltube3rd.setAlignment(Qt.AlignLeft)

        etube3rd = QLineEdit()
        etube3rd.setToolTip('Code: M3 / S3')
        etube3rd.setText("{:0.6g}".format(scale[3]))

        tubeOptions=QGridLayout()
        tubeOptions.addWidget(lcomment,    0, 0, 1, 2) # from 0,0 over 1 row and 2 cols
        tubeOptions.addWidget(ltubeDef,    1, 0)
        tubeOptions.addWidget(etubeDef,    1, 1)
        tubeOptions.addWidget(ltube1st,    2, 0)
        tubeOptions.addWidget(etube1st,    2, 1)
        tubeOptions.addWidget(ltube2nd,    3, 0)
        tubeOptions.addWidget(etube2nd,    3, 1)
        tubeOptions.addWidget(ltube3rd,    4, 0)
        tubeOptions.addWidget(etube3rd,    4, 1)

    # Dialog box
        d = QDialog() # set parent empty to popup in center of screen
        d.setWindowIcon(self.iconGeigerLog)
        d.setWindowTitle("Set Geiger Tube Sensitivities")
        d.setWindowModality(Qt.WindowModal)
        # d.setMaximumWidth(200)

    # Buttons
        self.bbox = QDialogButtonBox()
        self.bbox.setStandardButtons(QDialogButtonBox.Cancel | QDialogButtonBox.Ok)
        self.bbox.accepted.connect(lambda: d.done(100))
        self.bbox.rejected.connect(lambda: d.done(0))

        layoutV = QVBoxLayout(d)
        layoutV.addLayout(tubeOptions)
        layoutV.addWidget(self.bbox)
        layoutV.addStretch()

        retval = d.exec()
        #print("reval:", retval)
        if retval == 0:
            # CANCEL
            dprint(fncname + "CANCEL clicked, Sensitivities unchanged")

        else:
            # OK
            fprint(header("Set Geiger Tube Sensitivities"))
            try:        ftubeDef = float(etubeDef.text().replace(",", "."))
            except:     ftubeDef = 0
            try:        ftube1st = float(etube1st.text().replace(",", "."))
            except:     ftube1st = 0
            try:        ftube2nd = float(etube2nd.text().replace(",", "."))
            except:     ftube2nd = 0
            try:        ftube3rd = float(etube3rd.text().replace(",", "."))
            except:     ftube3rd = 0

            if ftubeDef > 0:     gglobs.Sensitivity[0] = ftubeDef
            else:                efprint("1st tube: Illegal Value, >0 required, you entered: ", etubeDef.text())

            if ftube1st > 0:     gglobs.Sensitivity[1] = ftube1st
            else:                efprint("1st tube: Illegal Value, >0 required, you entered: ", etube1st.text())

            if ftube2nd > 0:     gglobs.Sensitivity[2] = ftube2nd
            else:                efprint("2nd tube: Illegal Value, >0 required, you entered: ", etube2nd.text())

            if ftube3rd > 0:     gglobs.Sensitivity[3] = ftube3rd
            else:                efprint("3rd tube: Illegal Value, >0 required, you entered: ", etube3rd.text())

            fprint("Def tube:", "{} CPM / (µSv/h)" .format(gglobs.Sensitivity[0]), debug = True)
            fprint("1st tube:", "{} CPM / (µSv/h)" .format(gglobs.Sensitivity[1]), debug = True)
            fprint("2nd tube:", "{} CPM / (µSv/h)" .format(gglobs.Sensitivity[2]), debug = True)
            fprint("3rd tube:", "{} CPM / (µSv/h)" .format(gglobs.Sensitivity[3]), debug = True)

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

        if gglobs.DevicesConnected > 0 and gglobs.varMappedCount == 0:
            efprint("WARNING: No mapped variables found although a device is connected.\
                     \nLogging will not be possible! Please check configuration if this is unexpected !")
            return

        fprint("Shows the variables mapped to each device as configured. The configuration is set in")
        fprint("GeigerLog's configuration file geigerlog.cfg")

        mapflag = False
        for vname in gglobs.varsCopy:
            if gglobs.varMap[vname] > 1:
                if mapflag == False:    # print only on first occurence
                    efprint("WARNING: Mapping problem of Variables")
                qefprint("Variable {}".format(vname), "is mapped to more than one device")
                mapflag = True

        dline = "{:10s}: {:4s} {:4s} {:6s} {:6s} {:6s} {:6s} {:6s} {:6s} {:5s} {:5s} {:5s} {:5s}"
        fprint("\n" + dline.format("Device", *list(gglobs.varsCopy)))
        fprint("-" * 86)
        for DevName in gglobs.Devices:              # Device?
            checklist = []
            if gglobs.Devices[DevName][CONN]:       # connected?
                checklist.append(DevName)
                for vname in gglobs.varsCopy:       # Var?
                    try:
                        if vname in gglobs.Devices[DevName][VNAME]: checklist.append("M")   # option:("ʘ", "X")
                        else:                                       checklist.append("-")
                    except:
                        checklist.append("-")
                fprint(dline.format(*checklist))

        if mapflag:
            qefprint("Measurements are made on devices from top to bottom, and for each from left to right.")
            qefprint("If double-mapping of variables occurs, then the last measured variable will overwrite")
            qefprint("the previous one, almost always resulting in useless data.")
            qefprint("Tube Sensitivities may be overwritten as well!\n")
        else:
            fprint("Mapping is valid")
            playWav("ok")


    def fprintDeviceInfo(self, DevName, extended=False):
        """prints basic / extended info on the device"""

        setBusyCursor()
        fncname = "fprintDeviceInfo: "
        dprint(fncname + "DevName: {:10s}, extended: {}".format(DevName, extended))

        txt = DevName + " Device Info"
        if extended:  txt += " Extended"
        fprint(header(txt))

        if   DevName == "GMC"         : info = gdev_gmc         .getInfoGMC        (extended=extended)
        elif DevName == "Audio"       : info = gdev_audio       .getInfoAudio      (extended=extended)
        elif DevName == "RadMon"      : info = gdev_radmon      .getInfoRadMon     (extended=extended)
        elif DevName == "AmbioMon"    : info = gdev_ambiomon    .getInfoAmbioMon   (extended=extended)
        elif DevName == "GammaScout"  : info = gdev_gscout      .getInfoGammaScout (extended=extended)
        elif DevName == "I2C"         : info = gdev_i2c         .getInfoI2C        (extended=extended)
        elif DevName == "LabJack"     : info = gdev_labjack     .getInfoLabJack    (extended=extended)
        elif DevName == "Simul"       : info = gdev_simul       .getInfoSimul      (extended=extended)
        elif DevName == "MiniMon"     : info = gdev_minimon     .getInfoMiniMon    (extended=extended)
        elif DevName == "Manu"        : info = gdev_manu        .getInfoManu       (extended=extended)
        elif DevName == "WiFiClient"  : info = gdev_wificlient  .getInfoWiFiClient (extended=extended)
        elif DevName == "WiFiServer"  : info = gdev_wifiserver  .getInfoWiFiServer (extended=extended)
        else:                           info = "incorrect Device Name '{}'".format(DevName)
        fprint(info)

        setNormalCursor()


    def toggleDeviceConnection(self):
        """if no connection exists, then make connection else disconnect"""

        if gglobs.logging:
            self.showStatusMessage("Cannot change when logging! Stop logging first")
            return

        if gglobs.DevicesConnected == 0:    self.switchAllConnections(new_connection="ON")
        else:                               self.switchAllConnections(new_connection="OFF")


    def switchAllConnections(self, new_connection="ON"):
        """
        if new_connection == ON:
            if no connection exists, then try to make connection (with verification
            of communication with device)
        if new_connection == OFF:
            if connection does exist, then disconnect
        """

        if gglobs.logging:
            self.showStatusMessage("Cannot change when logging! Stop logging first")
            return

        fncname = "switchAllConnections: "
        self.setBusyCursor()
        dprint(fncname + "--> {}. ".format(new_connection))
        setDebugIndent(1)

        #
        # Connect /Dis-Connect all devices which are activated
        #
        for DevName in gglobs.Devices:
            if gglobs.Devices[DevName][ACTIV]:
                self.switchDeviceConnection (DevName, new_connection=new_connection)
                Qt_update()

        #
        # Print all Devices and their states
        #
        gglobs.DevicesActivated = 0
        gglobs.DevicesConnected = 0
        dprint(fncname + "Device Status:")
        for i, DevName in enumerate(gglobs.Devices):
            DevVars      = gglobs.Devices[DevName][VNAME]   # var names with this device
            DevActvState = gglobs.Devices[DevName][ACTIV]   # device activated?
            DevConnState = gglobs.Devices[DevName][CONN]    # device connected?

            if DevActvState:  gglobs.DevicesActivated += 1
            if DevConnState:  gglobs.DevicesConnected += 1
            if DevVars is not None:    svs = ", ".join(DevVars)   # the variables
            else:                      svs = "None"
            dprint("   Device #{:<2d}: {:10s}  Activation: {:6s} Connection: {}{:6s}  Vars: {}".
                    format(i, DevName, str(DevActvState), TGREEN if DevConnState else "", str(DevConnState), svs))

        dprint("   Number of Devices activated: {}".format(gglobs.DevicesActivated))
        dprint("   Number of Devices connected: {}".format(gglobs.DevicesConnected))

        #
        # set plug-icon green on >= 1 connected devices (at least 1 needed for a closed (=green) plug)
        #
        if gglobs.DevicesConnected > 0:
            self.toggleDeviceConnectionAction.setIcon(QIcon(QPixmap(os.path.join(gglobs.gresPath, 'icon_plug_closed.png')))) # green icon
        else:
            self.toggleDeviceConnectionAction.setIcon(QIcon(QPixmap(os.path.join(gglobs.gresPath, 'icon_plug_open.png'))))   # red icon
            self.fprintWarningMessage("WARNING: No devices are connected")

        #
        # determine the mapping and active variables on new connections
        #
        if new_connection == "ON" and gglobs.DevicesConnected > 0:
            gglobs.varMappedCount = 0
            for vname   in gglobs.varsCopy:  gglobs.varMap[vname] = 0
            for DevName in gglobs.Devices:   gglobs.DevVarsAsText[DevName] = None

            # Scan all devices for loggable variables
            for DevName in gglobs.Devices:                                  # scan all devices
                # rdprint("DevName: ", DevName)
                if gglobs.Devices[DevName][VNAME] != None:                  # those with variables named
                    tmpDevVarsAsText = ""
                    for vname in gglobs.Devices[DevName][VNAME]:            # scan all their variables
                        # print("                  : vname:", vname)
                        if vname == "Unused" or vname == "auto": continue
                        gglobs.varMap[vname]        += 1
                        gglobs.varMappedCount       += 1
                        tmpDevVarsAsText            += " {}".format(vname)  # like: CPM1st CPS1st CPM2nd ...
                        gglobs.varsSetForLog[vname]  = True                 # and mark them active for this log

                    # gdprint("tmpDevVarsAsText: ", tmpDevVarsAsText)
                    gglobs.DevVarsAsText[DevName] = tmpDevVarsAsText.strip() # like: {'GMC': 'CPM1st CPS1st CPM2nd CPS2nd Humid', 'Audio': None,
                    # gdprint("gglobs.DevVarsAsText: ", gglobs.DevVarsAsText)

            self.showDeviceMappings()

        # cleanup
        self.checkLoggingState()

        setDebugIndent(0)
        self.setNormalCursor()


    def setStyleSheetTBButton(self, button, stylesheetflag):
        """set toolbar button of devices to grey, green or red"""

        if   stylesheetflag == "ON"    : button.setStyleSheet(self.dbtnStyleSheetON)        # green
        elif stylesheetflag == "OFF"   : button.setStyleSheet(self.dbtnStyleSheetOFF)       # grey
        elif stylesheetflag == "ERR"   : button.setStyleSheet(self.dbtnStyleSheetError)     # red


    # def setDisableDeviceActions(self):
    #     """called only when GMC internal config is not usable"""

    #     self.GMCSpeakerONAction.        setEnabled(False)
    #     self.GMCSpeakerOFFAction.       setEnabled(False)
    #     self.GMCAlarmONAction.          setEnabled(False)
    #     self.GMCAlarmOFFAction.         setEnabled(False)
    #     self.GMCSavingStateAction.      setEnabled(False)

    def initDevice(self, DevName):

        # gdprint("NEW initDevice: ", DevName)

        if   DevName == "GMC":          errmsg = gdev_gmc       .initGMC()
        elif DevName == "Audio":        errmsg = gdev_audio     .initAudio()
        elif DevName == "RadMon":       errmsg = gdev_radmon    .initRadMon()
        elif DevName == "AmbioMon":     errmsg = gdev_ambiomon  .initAmbioMon()
        elif DevName == "GammaScout":   errmsg = gdev_gscout    .initGammaScout()
        elif DevName == "I2C":          errmsg = gdev_i2c       .initI2C()
        elif DevName == "LabJack":      errmsg = gdev_labjack   .initLabJack()
        elif DevName == "Simul":        errmsg = gdev_simul     .initSimul()
        elif DevName == "MiniMon":      errmsg = gdev_minimon   .initMiniMon()
        elif DevName == "Manu":         errmsg = gdev_manu      .initManu()
        elif DevName == "WiFiClient":   errmsg = gdev_wificlient.initWiFiClient()
        elif DevName == "WiFiServer":   errmsg = gdev_wifiserver.initWiFiServer()

        return errmsg


    def terminateDevice(self, DevName):

        # gdprint("NEW terminateDevice: ", DevName)

        if   DevName == "GMC":          errmsg = gdev_gmc       .terminateGMC()
        elif DevName == "Audio":        errmsg = gdev_audio     .terminateAudio()
        elif DevName == "RadMon":       errmsg = gdev_radmon    .terminateRadMon()
        elif DevName == "AmbioMon":     errmsg = gdev_ambiomon  .terminateAmbioMon()
        elif DevName == "GammaScout":   errmsg = gdev_gscout    .terminateGammaScout()
        elif DevName == "I2C":          errmsg = gdev_i2c       .terminateI2C()
        elif DevName == "LabJack":      errmsg = gdev_labjack   .terminateLabJack()
        elif DevName == "Simul":        errmsg = gdev_simul     .terminateSimul()
        elif DevName == "MiniMon":      errmsg = gdev_minimon   .terminateMiniMon()
        elif DevName == "Manu":         errmsg = gdev_manu      .terminateManu()
        elif DevName == "WiFiClient":   errmsg = gdev_wificlient.terminateWiFiClient()
        elif DevName == "WiFiServer":   errmsg = gdev_wifiserver.terminateWiFiServer()

        return errmsg


    def setEnableDeviceActions(self, new_enable = True, device="", stylesheetflag="ON"):
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

            # # GMC Device functions using the config
            # self.GMCSpeakerONAction.     setEnabled(new_enable)
            # self.GMCSpeakerOFFAction.    setEnabled(new_enable)
            # self.GMCAlarmONAction.       setEnabled(new_enable)
            # self.GMCAlarmOFFAction.      setEnabled(new_enable)
            # self.GMCSavingStateAction.   setEnabled(new_enable)

            #toolbar GMC Power Toggle
            self.dbtnGMCPower.           setEnabled(new_enable)

            # History
            self.histGMCDeviceAction.    setEnabled(new_enable)

            self.setStyleSheetTBButton(self.dbtnGMC, stylesheetflag)
            self.setGMCPowerIcon()


        # AudioCounter
        elif device == "Audio":
            self.AudioInfoActionExt .setEnabled(new_enable)             # extended info
            self.AudioPlotAction    .setEnabled(new_enable)             # audio plotting
            self.AudioSignalAction  .setEnabled(new_enable)             # audio raw signal
            self.AudioEiaAction     .setEnabled(new_enable)             # audio eia action
            self.setStyleSheetTBButton(self.dbtnAudio, stylesheetflag)

        # RadMon
        elif device == "RadMon":
            self.RMInfoActionExt.setEnabled(new_enable)                 # enable extended info
            self.setStyleSheetTBButton(self.dbtnRM, stylesheetflag)

        # AmbioMon
        elif device == "AmbioMon":
            #needed???
            self.histAMDeviceCAMAction.  setEnabled(new_enable)
            self.histAMDeviceCPSAction.  setEnabled(new_enable)
            self.AmbioDataModeAction.    setEnabled(new_enable)
            ##
            self.AmbioInfoActionExt.     setEnabled(new_enable)         # enable extended info
            self.setStyleSheetTBButton(self.dbtnAmbio, stylesheetflag)


        # Gamma-Scout counter
        elif device == "GammaScout":
            self.setStyleSheetTBButton(self.dbtnGS, stylesheetflag)
            self.histGSDeviceAction.    setEnabled(new_enable)
            self.GSInfoActionExt.       setEnabled(new_enable)          # enable extended info
            self.GSResetAction.         setEnabled(new_enable)          # enable reset
            self.GSSetPCModeAction.     setEnabled(new_enable)          # enable PC Mode
            self.GSDateTimeAction.      setEnabled(new_enable)          # enable set DateTime
            self.GSSetOnlineAction.     setEnabled(False)               # set True next lines
            self.GSRebootAction.        setEnabled(False)               # or remains false
            if gglobs.GStype == "Online":
                self.GSSetOnlineAction. setEnabled(new_enable)          # enable Online mode
                self.GSRebootAction.    setEnabled(new_enable)          # enable Reboot

        # I2C
        elif device == "I2C":
            self.I2CInfoActionExt.setEnabled(new_enable)                # extended info
            # self.I2CResetAction.setEnabled(new_enable)                  # reset
            self.setStyleSheetTBButton(self.dbtnI2C, stylesheetflag)

        # LabJack
        elif device == "LabJack":
            self.LJInfoActionExt.setEnabled(new_enable)                 # enable extended info
            self.setStyleSheetTBButton(self.dbtnLJ, stylesheetflag)

        # MiniMon
        elif device == "MiniMon":
            self.setStyleSheetTBButton(self.dbtnMiniMon, stylesheetflag)

        # Simul
        elif device == "Simul":
            self.SimulSettings.setEnabled(new_enable)                   # enable settings
            self.setStyleSheetTBButton(self.dbtnSimul, stylesheetflag)

        # Manu
        elif device == "Manu":
            self.ManuInfoActionExt.setEnabled(new_enable)               # enable extended info
            self.setStyleSheetTBButton(self.dbtnManu, stylesheetflag)

        # WiFiServer
        elif device == "WiFiServer":
            # self.WiFiInfoActionExt.setEnabled(new_enable)             # enable extended info
            self.setStyleSheetTBButton(self.dbtnWServer, stylesheetflag)

        # WiFiClient
        elif device == "WiFiClient":
            # self.WiFiClientInfoActionExt.setEnabled(new_enable)       # enable extended info
            self.setStyleSheetTBButton(self.dbtnWClient, stylesheetflag)



    # GENERIC
    def switchDeviceConnection(self, DevName, new_connection = "ON"):
        """generic handler for connections"""

        fncname = "switchDeviceConnection: "

        dprint(fncname + "Device: {} --> {}. ".format(DevName, new_connection))
        setDebugIndent(1)
        self.setBusyCursor()

        #
        # INIT
        #
        if new_connection == "ON":
            fprint(header("Connect {} Device".format(DevName)))
            Qt_update()
            if gglobs.Devices[DevName][CONN]:
                fprint("Already connected")
                self.fprintDeviceInfo(DevName)

            else:
                errmsg = self.initDevice(DevName)
                if gglobs.Devices[DevName][CONN] :
                    # successful connect
                    self.setEnableDeviceActions(new_enable = True, device=DevName, stylesheetflag="ON")
                    fprint("Device successfully connected")
                    dprint(fncname + "Status: ON: for device: {}".format(gglobs.Devices[DevName][DNAME]))

                else:
                    # failure connecting
                    self.setEnableDeviceActions(new_enable = False, device=DevName, stylesheetflag="ERR")
                    msg = "Failure connecting with Device: '{}' for reason:\n{}".format(DevName, errmsg) # tuple of 2 parts
                    efprint(msg)
                    edprint((fncname + "Status: " + msg).replace("\n", " "))

        #
        # TERMINATE
        #
        else: # new_connection == OFF
            fprint(header("Disconnect {} Device".format(DevName)))
            if not gglobs.Devices[DevName][CONN]:
                # is already de-connected
                fprint("No connected {} Device".format(DevName))
                self.setEnableDeviceActions(new_enable=False, device=DevName, stylesheetflag="OFF")

            else:
                # is connected; now deconnecting
                errmsg = self.terminateDevice(DevName)
                if not gglobs.Devices[DevName][CONN] :
                    # successful dis-connect
                    fprint("Device successfully disconnected", debug=True)
                    self.setEnableDeviceActions(new_enable=False, device=DevName, stylesheetflag="OFF")
                else:
                    # failure dis-connecting
                    self.setEnableDeviceActions(new_enable=False, device=DevName, stylesheetflag="ERR")
                    efprint("Failure disconnecting:", "'{}'".format(gglobs.Devices[DevName][0] ), debug=True)
                    qefprint(errmsg)

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
            self.logSnapAction.             setEnabled(True)    # snaps are possible only during logging

            # self.setLogTimingAction.        setEnabled(False)   # log cycle change only when logging
            # self.btnSetCycle.               setEnabled(False)   # log cycle change only when logging

            if gglobs.Devices["GMC"][ACTIV]:                    # GMC
                self.histGMCDeviceAction.   setEnabled(False)   #   no downloads during logging

            if gglobs.Devices["GammaScout"][ACTIV]:             # GammaScout
                self.histGSDeviceAction.    setEnabled(False)   #   no downloads during logging

            if gglobs.Devices["AmbioMon"][ACTIV]:               # AmbioMon
                self.histAMDeviceCAMAction. setEnabled(False)   #   no downloads during logging
                self.histAMDeviceCPSAction. setEnabled(False)   #   no downloads during logging

            if gglobs.Devices["I2C"][ACTIV]:                    # I2C
                self.I2CScanAction.         setEnabled(False)   #   can scan only when not logging
                self.I2CForceCalibAction.   setEnabled(False)   #   can calibrate only when not logging
                self.I2CResetAction.        setEnabled(False)   #   can reset only when not logging

        # Not Logging
        else:
            self.logLoadFileAction.         setEnabled(True)    # can load log files
            self.logLoadCSVAction.          setEnabled(True)    # can load CSV log files
            self.startloggingAction.        setEnabled(True)    # can start logging (GMC powering need will be excluded later)
            self.stoploggingAction.         setEnabled(False)   # cannot stop - it is not running
            self.quickLogAction.            setEnabled(True)    # quickstart is possible (GMC powering need will be excluded later)
            self.logSnapAction.             setEnabled(False)   # cannot take snaps when not logging

            # self.setLogTimingAction.        setEnabled(True)    # log cycle change only when logging
            # self.btnSetCycle.               setEnabled(True)    # log cycle change only when logging

            if gglobs.Devices["GMC"][ACTIV]:                    # GMC
                self.histGMCDeviceAction.   setEnabled(True)    #   can download from device when not logging even if powered off
                if gdev_gmc.isGMC_PowerOn() == "OFF" \
                   and gglobs.DevicesConnected == 1:            # GMC is NOT powered ON and is only device
                    self.startloggingAction.setEnabled(False)   #   cannot start logging without power
                    self.quickLogAction.    setEnabled(False)   #   quickstart is NOT possible without power

            if gglobs.Devices["GammaScout"][ACTIV]:             # GammaScout
                self.histGSDeviceAction.    setEnabled(True)    #   can download from device when not logging

            if gglobs.Devices["AmbioMon"][ACTIV]:               # AmbioMon
                self.histAMDeviceCAMAction. setEnabled(True)    #   can download from device when not logging
                self.histAMDeviceCPSAction. setEnabled(True)    #   can download from device when not logging

            if gglobs.Devices["I2C"][ACTIV]:                    # I2C
                self.I2CScanAction.         setEnabled(True)    #   can scan only when not logging
                self.I2CForceCalibAction.   setEnabled(True)    #   can calibrate only when not logging
                self.I2CResetAction.        setEnabled(True)    #   can reset only when not logging

            if gglobs.logDBPath == None:
                self.startloggingAction.    setEnabled(False)   # no log file loaded, no logging start

            if gglobs.DevicesConnected == 0:                    # no connected devices
                self.quickLogAction.        setEnabled(False)   #   no quick Log
                self.startloggingAction.    setEnabled(False)   #   no start log


        # adding Log comments allowed when a file is defined
        if gglobs.logDBPath != None:    self.addCommentAction.      setEnabled(True)
        else:                           self.addCommentAction.      setEnabled(False)

        # adding History comments allowed when a file is defined
        if gglobs.hisDBPath != None:    self.addHistCommentAction.  setEnabled(True)
        else:                           self.addHistCommentAction.  setEnabled(False)

        # general add comment butto enabled if either Log or Hist is available
        if gglobs.logDBPath != None or gglobs.hisDBPath != None: self.btnAddComment.setEnabled(True)
        else:                                                    self.btnAddComment.setEnabled(False)   # neither DB is loaded

    def toggleGMCPower(self):
        """Toggle GMC device Power ON / OFF"""

        if gglobs.logging:
            self.showStatusMessage("Cannot change power when logging! Stop logging first")
            return

        if gdev_gmc.isGMC_PowerOn() == "ON": self.switchGMCPower("OFF")
        else:                                self.switchGMCPower("ON")


    def switchGMCPower(self, newstate = "ON"):
        """Switch power of GMC device to ON or OFF"""

        fncname = "switchGMCPower: "
        dprint(fncname + "--> {}".format(newstate))
        fprint(header("Switch GMC Device Power to: {}".format(newstate)))

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

        gglobs.GMC_cfg, error, errmessage     = gdev_gmc.getGMC_CFG()     # read config after power change

        if gdev_gmc.isGMC_PowerOn() == "ON": fprint("Power is ON")
        else:                                fprint("Power is OFF")
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
        msg.setTextFormat(Qt.RichText)
        msg.setText(gglobs.helpFirmwareBugs)

        msg.setStandardButtons(QMessageBox.Ok)
        msg.setDefaultButton(QMessageBox.Ok)
        msg.setEscapeButton(QMessageBox.Ok)
        msg.setWindowModality(Qt.WindowModal)
        msg.setStyleSheet("QLabel{min-width:700px; font-size:11pt;}")
        msg.setMinimumWidth(800)

        msg.exec()


    def helpWorldMaps(self):
        """Using the Radiation World Map"""

        msg = QMessageBox()
        msg.setWindowIcon(self.iconGeigerLog)
        msg.setWindowTitle("Help - Radiation World Maps")
        msg.setText(gglobs.helpWorldMaps)

        msg.setStandardButtons(QMessageBox.Ok)
        msg.setDefaultButton(QMessageBox.Ok)
        msg.setEscapeButton(QMessageBox.Ok)
        msg.setWindowModality(Qt.WindowModal)
        msg.setStyleSheet("QLabel{min-width:700px; font-size:12pt;}")
        msg.setMinimumWidth(800)

        msg.exec()


    def helpOccupationalRadiation(self):
        """Occupational Radiation Limits"""

        msg = QMessageBox()
        msg.setWindowIcon(self.iconGeigerLog)
        msg.setWindowTitle("Help - Occupational Radiation Limits")
        msg.setText(gglobs.helpOccupationalRadiation)

        msg.setStandardButtons(QMessageBox.Ok)
        msg.setDefaultButton(QMessageBox.Ok)
        msg.setEscapeButton(QMessageBox.Ok)
        msg.setWindowModality(Qt.WindowModal)
        msg.setStyleSheet("QLabel{min-width:700px; font-size:12pt;}")
        msg.setMinimumWidth(800)

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
        msg.setMinimumWidth(800)

        msg.exec()


    def helpAbout(self):
        """About item on the Help menu"""

        # the curly brackets {} used for Python's format() don't work when the text has
        # CSS formatting using {}!
        description = gglobs.helpAbout % (__author__, gglobs.__version__, __copyright__, __license__)


        p = QPixmap(os.path.join(gglobs.gresPath, 'icon_geigerlog.png')) # the icon is 512 x 512
        w = 100
        h = 100
        licon   = QLabel()                                  # label to hold the geigerlog icon
        licon.setPixmap(p.scaled(w,h,Qt.KeepAspectRatio))   # set a scaled pixmap to a w x h window keeping its aspect ratio

        ltext   = QLabel()                                  # label to hold the 'eigerlog' text as picture
        ltext.setPixmap(QPixmap(os.path.join(gglobs.gresPath, 'eigerlog.png')))

        labout  = QTextBrowser() # label to hold the description
        labout.setLineWrapMode(QTextEdit.WidgetWidth)
        labout.setText(description)
        labout.setOpenExternalLinks(True) # to open links in a browser
        labout.setTextInteractionFlags(Qt.LinksAccessibleByMouse|Qt.TextSelectableByMouse)
        labout.setMaximumWidth(800) # set the width:

        d = QDialog()
        d.setWindowIcon(self.iconGeigerLog)
        d.setWindowTitle("Help - About GeigerLog")
        d.setWindowModality(Qt.WindowModal)
        d.setMaximumWidth(800)
        d.setMinimumWidth(750)
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


    def setSerialPort(self):
        """sets the Serial Port and its Baud rate"""

        # see: getPortList() for list of attributes to Portlist

        fncname = "setSerialPort: "
        dprint(fncname)
        setDebugIndent(1)

        GMC_Activation = True if gglobs.Devices["GMC"]          [ACTIV] else False
        I2CActivation  = True if gglobs.Devices["I2C"]          [ACTIV] else False
        GSActivation   = True if gglobs.Devices["GammaScout"]   [ACTIV] else False

        setPortWidth = 680

        selection_ports    = []
        selection_baudGMC  = list(map(str,sorted(gglobs.GMCbaudrates, reverse=True)))
        selection_baudI2C  = list(map(str,sorted(gglobs.I2Cbaudrates, reverse=True)))
        selection_baudGS   = list(map(str,sorted(gglobs.GSbaudrates,  reverse=True)))

        enableSelections = True

        lp = getPortList(symlinks=True) # ist in gsup_utils.py
        #~print("-----------------lp:          : ", lp)

        hsp = "<b>Available Ports:</b><pre>"
        hsp += "\n{:15s} {:40s}  {:14s}   {:s}\n{}\n".format("Port", "Name of USB-to-Serial Hardware", "Linked to Port", "VID :PID", "-" * 84)

        if len(lp) == 0:
            errmessage = "FAILURE: No available serial ports found"
            dprint(fncname + errmessage, debug=True)
            hsp += errmessage + "\n" + "Is any device connected? Check cable and plugs! Re-run in a few seconds." + "\n\n\n"
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
                    dprint(fncname + "Exception: {}  list_port: {}".format(e, p))
                    enableSelections = False

        if GMC_Activation or I2CActivation or GSActivation:
            isAnySerDeviceActivated = True
        else:
            isAnySerDeviceActivated = False

        hsp += "</pre>"

    # GMC
        # Combo Box Ports
        portCbBoxGMC = QComboBox(self)
        portCbBoxGMC.setEnabled(GMC_Activation)
        portCbBoxGMC.addItems(selection_ports)
        portCbBoxGMC.setToolTip('Select the USB-to-Serial port')
        portCbBoxGMC.setCurrentIndex(portCbBoxGMC.findText(gglobs.GMC_usbport))

        # Combo Box Baudrates
        baudCbBoxGMC = QComboBox(self)
        baudCbBoxGMC.setEnabled(GMC_Activation)
        baudCbBoxGMC.addItems(selection_baudGMC)
        baudCbBoxGMC.setToolTip('Select the USB-to-Serial baudrate')
        baudCbBoxGMC.setCurrentIndex(baudCbBoxGMC.findText(str(gglobs.GMC_baudrate)))

        # H-Layout of Combo Boxes
        cblayoutGMC = QHBoxLayout()
        cblayoutGMC.addWidget(portCbBoxGMC)
        cblayoutGMC.addWidget(baudCbBoxGMC)


    # I2C
        # Combo Box Ports
        portCbBoxI2C = QComboBox(self)
        portCbBoxI2C.setEnabled(I2CActivation)
        portCbBoxI2C.addItems(selection_ports)
        portCbBoxI2C.setToolTip('Select the USB-to-Serial port')

        edprint(fncname + "i2cusbport: ", gglobs.I2Cusbport)
        portCbBoxI2C.setCurrentIndex(portCbBoxI2C.findText(gglobs.I2Cusbport))

        # Combo Box Baudrates
        baudCbBoxI2C = QComboBox(self)
        baudCbBoxI2C.setEnabled(I2CActivation)
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
        portCbBoxGS.setEnabled(GSActivation)
        portCbBoxGS.addItems(selection_ports)
        portCbBoxGS.setToolTip('Select the USB-to-Serial port')
        portCbBoxGS.setCurrentIndex(portCbBoxGS.findText(gglobs.GSusbport))

        # Combo Box Baudrates
        baudCbBoxGS = QComboBox(self)
        baudCbBoxGS.setEnabled(GSActivation)
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
        hsplabel.setWordWrap(True)
        hsplabel.setMaximumWidth(setPortWidth)

        # hsp2label
        hsp2  = """
        <p><br>Select port and baudrate for each activated device which is using a serial connection:
        <br>(GeigerLog's current settings are pre-selected if available.)<br>"""

        hsp2label = QLabel()
        hsp2label.setText(hsp2)
        hsp2label.setWordWrap(True)
        hsp2label.setMaximumWidth(setPortWidth)

    # Device labels
        GMCDevice = QLabel("GMC Device:")
        GSDevice  = QLabel("GammaScout Device:")
        I2CDevice = QLabel("I2C Device:")

    # hsp3label
        if isAnySerDeviceActivated:
            hsp3 = """
            <p><br>When you press OK, any logging will be stopped, and all of GeigerLog's devices will
            first be disconnected, and then reconnected with the selected, new settings!
            <p>Press Cancel to close without making any changes."""
        else:
            hsp3 = """
            <p><br>No activated device using a Serial Port was found.
            <p>Press Cancel to close."""

        hsp3label = QLabel()
        hsp3label.setText(hsp3)
        hsp3label.setWordWrap(True)
        hsp3label.setMaximumWidth(setPortWidth)

    # Dialog Box
        title = "Set Port"
        d = QDialog()
        d.setWindowIcon(self.iconGeigerLog)
        d.setWindowTitle(title)
        d.setWindowModality(Qt.WindowModal)
        d.setMaximumWidth(setPortWidth)

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
            vprint(fncname + "cancelled by user")

        else:
            fprint(header(title))
            if gglobs.Devices["GMC"][ACTIV]:
                if baudCbBoxGMC.currentText() != "":
                    gglobs.GMC_usbport  = portCbBoxGMC.currentText()
                    gglobs.GMC_baudrate = int(baudCbBoxGMC.currentText())
                    dprint(fncname + "GMC device: Port: {} with Baudrate: {}".format(gglobs.GMC_usbport, gglobs.GMC_baudrate))
                    fprint("GMC Device:")
                    fprint("- USB-to-Serial Port:",   gglobs.GMC_usbport)
                    fprint("- Baudrate:",             gglobs.GMC_baudrate)

            if gglobs.Devices["GammaScout"][ACTIV]:
                if baudCbBoxGS.currentText() != "":
                    gglobs.GSusbport  = portCbBoxGS.currentText()
                    gglobs.GSbaudrate = int(baudCbBoxGS.currentText())
                    dprint(fncname + "GammaScout device: Port: {} with Baudrate: {}".format(gglobs.GSusbport, gglobs.GSbaudrate))
                    fprint("GammaScout Device:")
                    fprint("- USB-to-Serial Port:",   gglobs.GSusbport)
                    fprint("- Baudrate:",             gglobs.GSbaudrate)

            if gglobs.Devices["I2C"][ACTIV]:
                if baudCbBoxI2C.currentText() != "":
                    gglobs.I2Cusbport  = portCbBoxI2C.currentText()
                    gglobs.I2Cbaudrate = int(baudCbBoxI2C.currentText())
                    dprint(fncname + "I2C device: Port: {} with Baudrate: {}".format(gglobs.I2Cusbport, gglobs.I2Cbaudrate))
                    fprint("I2C Device:")
                    fprint("- USB-to-Serial Port:",   gglobs.I2Cusbport)
                    fprint("- Baudrate:",             gglobs.I2Cbaudrate)

            self.stopLogging()
            self.switchAllConnections(new_connection = "OFF")
            self.switchAllConnections(new_connection = "ON")

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
    # if any is true, the higher one(s) must also be set true
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
        valueBox.RowWrapPolicy(QFormLayout.DontWrapRows)
        valueBox.addRow(QLabel("{:60s}".format("<b>ValueScaling</b> - it DOES modify the saved value!<br> ")))
        for vname in gglobs.varsCopy:
            valueBox.addRow(vname, QLineEdit(gglobs.ValueScale[vname]))

        # graph
        graphBox=QFormLayout()
        graphBox.setFieldGrowthPolicy (QFormLayout.ExpandingFieldsGrow)
        graphBox.RowWrapPolicy(QFormLayout.DontWrapRows)
        graphBox.addRow(QLabel("{:60s}".format("<b>GraphScaling</b> - it does NOT modify the saved value, <br>only the plotted value")))
        for vname in gglobs.varsCopy:
            graphBox.addRow(vname, QLineEdit(gglobs.GraphScale[vname]))

        vgLayout = QHBoxLayout()
        vgLayout.addLayout(valueBox)
        vgLayout.addLayout(graphBox)

        self.dialog = QDialog()
        self.dialog.setWindowIcon(self.iconGeigerLog)
        self.dialog.setWindowTitle("View and Edit Current Scaling")
        #~self.dialog.setWindowModality(Qt.WindowModal)
        self.dialog.setWindowModality(Qt.ApplicationModal)
        self.dialog.setMinimumWidth(700)
        self.dialog.setMaximumWidth(1000)

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
            for i in range(0, len(gglobs.varsCopy) + 1):
                if valueBox.itemAt(i, QFormLayout.LabelRole) is not None:
                    vvname = (valueBox.itemAt(i, QFormLayout.LabelRole).widget().text()).strip()
                    vval   = (valueBox.itemAt(i, QFormLayout.FieldRole).widget().text()).strip().replace(",", ".")
                    wprint("valueBox i: {:2d}  {:10s}  {}".format(i, vvname, vval))
                    gglobs.ValueScale[vvname] = vval

            for i in range(0, len(gglobs.varsCopy) + 1):
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

        # self.notePad.append("<span style='color:black;'>&nbsp;</span>")
        # self.notePad.setStyleSheet("color: rgb(40, 40, 40)")
        self.notePad.clear()
        self.notePad.setTextColor(QColor(40, 40, 40))


    def clearLogPad(self):
        """Clear the logPad"""

        self.logPad.clear()


    def setBusyCursor(self):

        QApplication.setOverrideCursor(Qt.WaitCursor)


    def setNormalCursor(self):

        QApplication.restoreOverrideCursor()


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
