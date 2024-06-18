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
__copyright__       = "Copyright 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024"
__credits__         = [""]
__license__         = "GPL3"

from gsup_utils   import *

import gsup_sql
import gsup_tools
import gsup_plot
# if g.TelegramActivation: import gsup_telegram

import gweb_monserv
import gweb_radworld

import gstat_poisson
import gstat_fft
import gstat_convfft
import gstat_synth

if g.Devices["GMC"]        [g.ACTIV]: import gdev_gmc         # both needed
if g.Devices["GMC"]        [g.ACTIV]: import gdev_gmc_hist    # both needed
if g.Devices["Audio"]      [g.ACTIV]: import gdev_audio       #
if g.Devices["IoT"]        [g.ACTIV]: import gdev_iot         # IoT Device
if g.Devices["RadMon"]     [g.ACTIV]: import gdev_radmon      # RadMon
if g.Devices["AmbioMon"]   [g.ACTIV]: import gdev_ambiomon    #
if g.Devices["GammaScout"] [g.ACTIV]: import gdev_gammascout  #
if g.Devices["I2C"]        [g.ACTIV]: import gdev_i2c         # I2C  -    then imports dongles and sensor modules
if g.Devices["LabJack"]    [g.ACTIV]: import gdev_labjack     # LabJack - then imports the LabJack modules
if g.Devices["Formula"]    [g.ACTIV]: import gdev_formula     #
if g.Devices["MiniMon"]    [g.ACTIV]: import gdev_minimon     #
if g.Devices["WiFiClient"] [g.ACTIV]: import gdev_wificlient  #
if g.Devices["WiFiServer"] [g.ACTIV]: import gdev_wifiserver  #
if g.Devices["RaspiI2C"]   [g.ACTIV]: import gdev_raspii2c    #
if g.Devices["RaspiPulse"] [g.ACTIV]: import gdev_raspipulse  #
if g.Devices["SerialPulse"][g.ACTIV]: import gdev_serialpulse # to support pulse counting via USB-to-Serial adapter
if g.Devices["Manu"]       [g.ACTIV]: import gdev_manu        #
if g.Devices["RadPro"]     [g.ACTIV]: import gdev_radpro      #


# Modality
# Qt: A modal dialog is a dialog that blocks input to other visible windows in the same application.
#
# Modale Dialoge sperren den Rest der Anwendung (oder sogar der Benutzeroberfläche), solange der Dialog angezeigt wird.
# Nichtmodale Dialoge erlauben auch Eingaben in der Applikation außerhalb des Dialogs.
#
# vergleiche Menu Show IP und MonServer: gleiche Programmierung, anderes Verhalten???
#
#   d.setWindowModality(Qt.WindowModal)
#   d.setWindowModality(Qt.ApplicationModal)    # The window is modal to the application and blocks input to all windows.
#   d.setWindowModality(Qt.NonModal)            # The window is not modal and does not block input to other windows.

class ggeiger(QMainWindow):

    def __init__(self):
        """init the ggeiger class"""

        defname = "ggeiger__init__: "

        super().__init__()
        g.exgg = self

        # hold the updated variable values
        self.vlabels  = None
        self.svlabels = None

        # from email: John Thornton <dev@gnipsel.com> to: pyqt@riverbankcomputing.com from: 13.12.2023, 22:54
        sys.excepthook = self.excepthook


        #
        # getting font(s)
        #
        #
        # default font type
        # custom_font = QFont()
        # custom_font.setWeight(18);
        # QApplication.setFont(custom_font, "QLabel")
        # set the font for the top level window (and any of its children):
        # self.window().setFont(someFont)
        # # set the font for *any* widget created in this QApplication:
        # QApplication.instance().setFont(QFont("Deja Vue"))
        # QApplication.instance().setFont(QFont("Helvetica"))
        #
        # edprint(QFont.family())
        # edprint(QApplication.instance().font())
        # edprint(QApplication.font())
        self.window().setFont(QFont("Sans Serif"))
        #
        # platform dependent!
        # cdprint("Platform: ", platform.platform())
            # Raspi: Bullseye      Platform: Linux-5.15.32-v8+-aarch64-with-glibc2.31
            # Intel: Ubuntu 16.04: Platform: Linux-4.15.0-142-generic-x86_64-with-glibc2.23

        if "WINDOWS" in platform.platform().upper():
            dprint("WINDOWS: Setting QFontDatabase.FixedFont")
            self.fontstd = QFontDatabase.systemFont(QFontDatabase.FixedFont) # worked! got Courier New
            #self.fontstd = QFont("Consolas", 10) # alternative

        elif "LINUX" in platform.platform().upper():
            dprint("LINUX: Setting QFontDatabase.FixedFont")
            self.fontstd = QFont("Mono", 9)

        else:
            dprint("Other System: Setting QFontDatabase.FixedFont")
            self.fontstd = QFontDatabase.systemFont(QFontDatabase.FixedFont) # result ?
            #self.fontstd = QFont("Courier New") # alternative

        #
        # # font standard
        #         #self.fontstd = QFont()
        #         #self.fontstd = QFont("Deja Vue", 10)
        #         #self.fontstd = QFont("pritzelbmpr", 10)
        #         #self.fontstd = QFont("Courier New", 10)
        #         #self.fontstd.setFamily('Monospace')         # options: 'Lucida'
        #         #self.fontstd.StyleHint(QFont.TypeWriter)    # options: QFont.Monospace, QFont.Courier
        #         #self.fontstd.StyleHint(QFont.Monospace)     # options: QFont.Monospace, QFont.Courier
        #         #self.fontstd.setStyleStrategy(QFont.PreferMatch)
        #         #self.fontstd.setFixedPitch(True)
        #         #self.fontstd.setPointSize(11) # 11 is too big
        #         #self.fontstd.setWeight(60)                  # options: 0 (thin) ... 99 (very thick); 60:ok, 65:too fat
        #         g.fontstd = self.fontstd
        #
        # self.fontstd = QFontDatabase.systemFont(QFontDatabase.FixedFont) # did NOT work on Raspi!

        self.fontstd.setFixedPitch(True)
        self.fontstd.setWeight(45)          # "Qt uses a weighting scale from 0 to 99"
                                            #  options: 0 (thin) ... 99 (very thick); 60:ok, 65:fat NOTE: >60 wirkt matschig
        g.fontstd = self.fontstd

        # fatfont used for HEADINGS: Data, Device, Graph
        self.fatfont = QFont("Deja Vue")
        self.fatfont.setWeight(65)
        self.fatfont.setPointSize(11)

    # window
        # ?

    # icon
        iconpath = os.path.join(g.resDir, 'icon_geigerlog.png')
        self.iconGeigerLog    = QIcon(QPixmap(iconpath))
        # rdprint("availableSizes:", self.iconGeigerLog.availableSizes())

        g.iconGeigerLog  = self.iconGeigerLog
        self.setWindowIcon(g.iconGeigerLog)

        # this is used for Web sites
        try:
            with open(iconpath, "rb") as file_handle:
                g.iconGeigerLogWeb = file_handle.read()
        except Exception as e:
            exceptPrint(e, defname + "reading binary from iconpath")

    #title
        wtitle = "GeigerLog v{}".format(g.__version__)
        if g.devel: wtitle += "  Python: {}  sys.argv: {}  venv: {}".format(sys.version[:6], sys.argv, g.VenvName)
        self.setWindowTitle(wtitle)

    #figure and its toolbar
        # weder figsize=(18, 18) noch figsize=(18, 18) in plt.figure() hat Auswirkungen auf die Plot Größe
        self.figure = plt.figure(facecolor = "#DFDEDD", edgecolor='#b8b8b8', linewidth = 0.1, dpi=g.hidpiScaleMPL)   # facecolor in lighter gray
        plt.clf()  # clear figure or it will show an empty figure !!

        # canvas - this is the Canvas Widget that displays the `figure`
        self.canvas = FigureCanvas(self.figure)
        self.canvas.mpl_connect('motion_notify_event', self.updatecursorposition) # where the cursor is
        self.canvas.mpl_connect('button_press_event' , self.onclick)              # send a mouse click
        self.canvas.setContentsMargins(10,10,10,10)
        # self.canvas.setMinimumHeight(450)
        self.canvas.setMinimumHeight(408)

        # rdprint(defname, "self.canvas.__sizeof__: ", self.canvas.__sizeof__())  # --> ggeiger__init__: self.canvas.__sizeof__: 120 ???
        # rdprint(defname, "self.canvas.size(): ", self.canvas.size())              # --> ggeiger__init__: self.canvas.size(): PyQt5.QtCore.QSize(640, 480)

        # this is the figure Navigation widget; it takes the Canvas widget and a parent
        self.navtoolbar = NavigationToolbar(self.canvas, self)
        self.navtoolbar.setToolTip("Graph Toolbar - available only when NOT logging")
        self.navtoolbar.setIconSize(QSize(32,32))
        self.navtoolbar.setEnabled(True)
        # self.navtoolbar.setStyleSheet("background-color:lightgreen;")
        #print("self.navtoolbar.iconSize()", self.navtoolbar.iconSize())

    # menubar, statusbar, and toolbar
        self.menubar = self.menuBar()
        self.menubar.setFocus()
        self.menubar.setFont(QFont("Deja Vu Sans", 11))

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
        addMenuTip(SaveNPAction, "Save Content of NotePad as text file named <current filename>.txt")
        SaveNPAction.triggered.connect(self.saveNotePad)

    #printNotePad
        PrintNPAction = QAction("Print NotePad ...", self)
        addMenuTip(PrintNPAction, "Print Content of NotePad to Printer or  PDF-File")
        PrintNPAction.triggered.connect(self.printNotePad)

    # exit
        exitAction = QAction('Exit', self)
        exitAction.setIcon(QIcon(QPixmap(os.path.join(g.resDir, 'icon_exit.png')))) # Flat icon
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
        self.toggleDeviceConnectionAction = QAction(QIcon(QPixmap(os.path.join(g.resDir, 'icon_plug_open.png'))), 'Connect / Disconnect Devices', self)
        addMenuTip(self.toggleDeviceConnectionAction, 'Toggle connection of GeigerLog with the devices')
        self.toggleDeviceConnectionAction.triggered.connect(self.toggleDeviceConnection)

        self.DeviceConnectAction = QAction(QIcon(QPixmap(os.path.join(g.resDir, 'icon_plug_open.png'))), 'Connect Devices', self)
        self.DeviceConnectAction.setShortcut('Ctrl+C')
        addMenuTip(self.DeviceConnectAction, 'Connect the computer to the devices')
        self.DeviceConnectAction.triggered.connect(lambda : self.switchAllDeviceConnections("ON"))

        self.DeviceDisconnectAction = QAction(QIcon(QPixmap(os.path.join(g.resDir, 'icon_plug_closed.png'))), 'Disconnect Devices', self, enabled = False)
        self.DeviceDisconnectAction.setShortcut('Ctrl+D')
        addMenuTip(self.DeviceDisconnectAction, 'Disconnect the computer from the devices')
        self.DeviceDisconnectAction.triggered.connect(lambda : self.switchAllDeviceConnections("OFF"))

        self.DeviceMappingAction = QAction('Show Device Mappings', self, enabled = True)
        addMenuTip(self.DeviceMappingAction, 'Show the mapping of variables of the activated devices')
        self.DeviceMappingAction.triggered.connect(self.showDeviceMappings)

        self.DevicePortSettingAction = QAction('Show Device Port Settings', self, enabled = True)
        addMenuTip(self.DevicePortSettingAction, 'Show the port settings for all activated devices')
        self.DevicePortSettingAction.triggered.connect(lambda : showPortSettings())

        self.DeviceCalibAction = QAction("Geiger Tubes ...", self, enabled = True)
        addMenuTip(self.DeviceCalibAction, "Set sensitivities for all Geiger tubes temporarily")
        self.DeviceCalibAction.triggered.connect(self.setTemporaryTubeSensitivities)

    # build the Device menu
        deviceMenu = self.menubar.addMenu('&Device')
        deviceMenu.setToolTipsVisible(True)

    # all devices
        deviceMenu.addAction(self.DeviceConnectAction)
        deviceMenu.addAction(self.DeviceDisconnectAction)

        deviceMenu.addSeparator()
        deviceMenu.addAction(self.DeviceMappingAction)
        deviceMenu.addAction(self.DevicePortSettingAction)
        deviceMenu.addAction(self.DeviceCalibAction)

        deviceMenu.addSeparator()

    # now following all device specific submenus

    # submenu GMC
        if g.Devices["GMC"][g.ACTIV]  :

            self.GMCInfoAction = QAction('Show Info', self, enabled=True)
            addMenuTip(self.GMCInfoAction, 'Show basic info on GMC device')
            self.GMCInfoAction.triggered.connect(lambda: self.fprintDeviceInfo("GMC"))

            self.GMCInfoActionExt = QAction('Show Extended Info', self, enabled=False)
            addMenuTip(self.GMCInfoActionExt, 'Show extended info on GMC device')
            self.GMCInfoActionExt.triggered.connect(lambda: self.fprintDeviceInfo("GMC", extended = True))

            self.GMCConfigEditAction = QAction("Set GMC Configuration ...", self, enabled=False)
            addMenuTip(self.GMCConfigEditAction, 'View, Edit and Set the GMC device configuration')
            self.GMCConfigEditAction.triggered.connect(lambda: gdev_gmc.editGMC_Configuration())

            self.GMCConfigMemoryAction = QAction('Show Configuration Memory', self, enabled=False)
            addMenuTip(self.GMCConfigMemoryAction, 'Show the GMC device configuration memory as binary in human readable format')
            self.GMCConfigMemoryAction.triggered.connect(gdev_gmc.fprintGMC_ConfigMemory)

            self.GMCONAction = QAction('Switch Power ON', self, enabled=False)
            addMenuTip(self.GMCONAction, 'Switch the GMC device power to ON')
            self.GMCONAction.triggered.connect(lambda: self.switchGMCPower("ON"))

            self.GMCOFFAction = QAction('Switch Power OFF', self, enabled=False)
            addMenuTip(self.GMCOFFAction, 'Switch the GMC device power to OFF')
            self.GMCOFFAction.triggered.connect(lambda: self.switchGMCPower("OFF"))

            self.GMCSetTimeAction = QAction('Set GMC DateTime to GeigerLog DateTime', self, enabled=False)
            addMenuTip(self.GMCSetTimeAction, "Set the Date and Time of the GMC device to GeigerLog's Date and Time")
            self.GMCSetTimeAction.triggered.connect(gdev_gmc.GMC_setDateTime)

            self.GMCEraseSavedDataAction = QAction('Erase Saved Data ...', self, enabled=False)
            addMenuTip(self.GMCEraseSavedDataAction, 'Erase all data from the History memory of the GMC device')
            self.GMCEraseSavedDataAction.triggered.connect(lambda: gdev_gmc.doEraseSavedData())

            self.GMCREBOOTAction = QAction('Reboot ...', self, enabled=False)
            addMenuTip(self.GMCREBOOTAction, 'Reboot the GMC device')
            self.GMCREBOOTAction.triggered.connect(lambda: gdev_gmc.doREBOOT(False))

            self.GMCFACTORYRESETAction = QAction('FACTORYRESET ...', self, enabled=False)
            addMenuTip(self.GMCFACTORYRESETAction, 'Reset the GMC device to factory configuration')
            self.GMCFACTORYRESETAction.triggered.connect(lambda: gdev_gmc.doFACTORYRESET(False))

            self.GMCSerialAction = QAction('Set Serial Port ...', self, enabled=True)
            addMenuTip(self.GMCSerialAction, 'Manually set the serial port of the GMC device')
            self.GMCSerialAction.triggered.connect(lambda: setDeviceSerialPort("GMC", g.GMC_usbport))


            self.GMCREBOOT_forceAction = QAction('DVL Force Reboot', self, enabled=True)
            addMenuTip(self.GMCREBOOT_forceAction, 'Force a Reboot of the GMC device')
            self.GMCREBOOT_forceAction.triggered.connect(lambda: gdev_gmc.doREBOOT(True))

            self.GMCFACTORYRESET_forceAction = QAction('DVL Force FACTORYRESET', self, enabled=True)
            addMenuTip(self.GMCFACTORYRESET_forceAction, 'Force a Reset of the GMC device to factory configuration')
            self.GMCFACTORYRESET_forceAction.triggered.connect(lambda: gdev_gmc.doFACTORYRESET(True))

            deviceSubMenuGMC = deviceMenu.addMenu("GMC Series")
            deviceSubMenuGMC.setToolTipsVisible(True)
            deviceSubMenuGMC.addAction(self.GMCInfoAction)
            deviceSubMenuGMC.addAction(self.GMCInfoActionExt)
            deviceSubMenuGMC.addAction(self.GMCConfigEditAction)
            deviceSubMenuGMC.addAction(self.GMCConfigMemoryAction)
            deviceSubMenuGMC.addAction(self.GMCSetTimeAction)
            deviceSubMenuGMC.addAction(self.GMCEraseSavedDataAction)
            deviceSubMenuGMC.addAction(self.GMCONAction)
            deviceSubMenuGMC.addAction(self.GMCOFFAction)
            deviceSubMenuGMC.addAction(self.GMCREBOOTAction)
            deviceSubMenuGMC.addAction(self.GMCFACTORYRESETAction)
            deviceSubMenuGMC.addAction(self.GMCSerialAction)

            if g.devel:    # on devel allow Factory Reset without checking
                deviceSubMenuGMC.addAction(self.GMCREBOOT_forceAction)
                deviceSubMenuGMC.addAction(self.GMCFACTORYRESET_forceAction)

            # if 0 and g.devel:
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
        if g.Devices["Audio"][g.ACTIV] :

            self.AudioInfoAction = QAction('Show Info', self, enabled=True)
            addMenuTip(self.AudioInfoAction, 'Show basic info on AudioCounter device')
            self.AudioInfoAction.triggered.connect(lambda: self.fprintDeviceInfo("Audio"))

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
            if g.devel:
                deviceSubMenuAudio.addAction(self.AudioSignalAction)
            if g.AudioOei:
                deviceSubMenuAudio.addAction(self.AudioEiaAction)


    # submenu SerialPulseCounter
        if g.Devices["SerialPulse"][g.ACTIV] :

            self.PulseInfoAction = QAction('Show Info', self, enabled=True)
            addMenuTip(self.PulseInfoAction, 'Show basic info on SerialPulse device')
            self.PulseInfoAction.triggered.connect(lambda: self.fprintDeviceInfo("SerialPulse"))

            # self.PulseInfoActionExt = QAction('Show Extended Info', self, enabled=False)
            # addMenuTip(self.PulseInfoActionExt, 'Show extended info on PulseCounter device')
            # self.PulseInfoActionExt.triggered.connect(lambda: self.fprintDeviceInfo("SerialPulse", extended = True))

            self.PulseSerialAction = QAction('Set Serial Port ...', self, enabled=True)
            addMenuTip(self.PulseSerialAction, 'Manually set the serial port of the SerialPulse device')
            self.PulseSerialAction.triggered.connect(lambda: setDeviceSerialPort("SerialPulse", g.SerialPulseUsbport))

            deviceSubMenuPulse  = deviceMenu.addMenu("SerialPulseCounter Series")
            deviceSubMenuPulse.setToolTipsVisible(True)
            deviceSubMenuPulse.addAction(self.PulseInfoAction)
            deviceSubMenuPulse.addAction(self.PulseSerialAction)
            # deviceSubMenuPulse.addAction(self.PulseInfoActionExt)


    # submenu IoT
        if g.Devices["IoT"][g.ACTIV]  :

            self.IoTInfoAction = QAction('Show Info', self, enabled=True)
            addMenuTip(self.IoTInfoAction, 'Show basic info on IoT device')
            self.IoTInfoAction.triggered.connect(lambda: self.fprintDeviceInfo("IoT"))

            self.IoTInfoActionExt = QAction('Show Extended Info', self, enabled=False)
            addMenuTip(self.IoTInfoActionExt, 'Show extended info on IoT device')
            self.IoTInfoActionExt.triggered.connect(lambda: self.fprintDeviceInfo("IoT", extended = True))

            deviceSubMenuIoT  = deviceMenu.addMenu("IoT Series")
            deviceSubMenuIoT.setToolTipsVisible(True)
            deviceSubMenuIoT.addAction(self.IoTInfoAction)
            deviceSubMenuIoT.addAction(self.IoTInfoActionExt)

    # submenu RadMon
        if g.Devices["RadMon"][g.ACTIV]  :

            self.RMInfoAction = QAction('Show Info', self, enabled=True)
            addMenuTip(self.RMInfoAction, 'Show basic info on RadMon device')
            self.RMInfoAction.triggered.connect(lambda: self.fprintDeviceInfo("RadMon"))

            self.RMInfoActionExt = QAction('Show Extended Info', self, enabled=False)
            addMenuTip(self.RMInfoActionExt, 'Show extended info on RadMon device')
            self.RMInfoActionExt.triggered.connect(lambda: self.fprintDeviceInfo("RadMon", extended = True))

            deviceSubMenuRM  = deviceMenu.addMenu("RadMon Series")
            deviceSubMenuRM.setToolTipsVisible(True)
            deviceSubMenuRM.addAction(self.RMInfoAction)
            deviceSubMenuRM.addAction(self.RMInfoActionExt)

    # submenu AmbioMon
        if g.Devices["AmbioMon"][g.ACTIV]  :

            self.AmbioInfoAction = QAction('Show Info', self, enabled=True)
            addMenuTip(self.AmbioInfoAction, 'Show basic info on AmbioMon device')
            self.AmbioInfoAction.triggered.connect(lambda: self.fprintDeviceInfo("AmbioMon"))

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
        if g.Devices["GammaScout"][g.ACTIV]  :

            self.GSInfoAction = QAction('Show Info', self, enabled=True)
            addMenuTip(self.GSInfoAction, 'Show basic info on GS device')
            self.GSInfoAction.triggered.connect(lambda: self.fprintDeviceInfo("GammaScout"))

            self.GSInfoActionExt = QAction('Show Extended Info', self, enabled=False)
            addMenuTip(self.GSInfoActionExt, 'Show extended info on GS device')
            self.GSInfoActionExt.triggered.connect(lambda: self.fprintDeviceInfo("GammaScout", extended = True))

            self.GSResetAction = QAction('Set to Normal Mode', self, enabled=False)
            addMenuTip(self.GSResetAction, 'Set the Gamma-Scout counter to its Normal Mode')
            self.GSResetAction.triggered.connect(lambda: gdev_gammascout.GSsetMode("Normal"))

            self.GSSetPCModeAction = QAction('Set to PC Mode', self, enabled=False)
            addMenuTip(self.GSSetPCModeAction, 'Set the Gamma-Scout counter to its PC Mode')
            self.GSSetPCModeAction.triggered.connect(lambda: gdev_gammascout.GSsetMode("PC"))

            self.GSDateTimeAction = QAction("Set Gamma-Scout DateTime to GeigerLog's DateTime", self, enabled=False)
            addMenuTip(self.GSDateTimeAction, "Set the Gamma-Scout counter clock to the GeigerLog Date and Time")
            self.GSDateTimeAction.triggered.connect(lambda: gdev_gammascout.setGSDateTime())

            self.GSSetOnlineAction = QAction('Set to Online Mode ...', self, enabled=False)
            addMenuTip(self.GSSetOnlineAction, "Set the Gamma-Scout counter to its Online Mode\nAvailable only for 'Online' models")
            self.GSSetOnlineAction.triggered.connect(lambda: gdev_gammascout.GSsetMode("Online"))

            self.GSRebootAction = QAction('Reboot', self, enabled=False)
            addMenuTip(self.GSRebootAction, "Do a Gamma-Scout reboot as warm-start\nAvailable only for 'Online' models")
            self.GSRebootAction.triggered.connect(lambda: gdev_gammascout.GSreboot())

            self.GSSerialAction = QAction('Set Serial Port ...', self, enabled=True)
            addMenuTip(self.GSSerialAction, 'Manually set the serial port of the I2C device')
            # self.GSSerialAction.triggered.connect(lambda: gdev_gammascout.setGS_SerialPort())
            self.GSSerialAction.triggered.connect(lambda: setDeviceSerialPort("GammaScout", g.GSusbport))

            deviceSubMenuGS  = deviceMenu.addMenu("Gamma-Scout Series")
            deviceSubMenuGS.setToolTipsVisible(True)
            deviceSubMenuGS.addAction(self.GSInfoAction)
            deviceSubMenuGS.addAction(self.GSInfoActionExt)
            deviceSubMenuGS.addAction(self.GSDateTimeAction)
            deviceSubMenuGS.addAction(self.GSResetAction)
            deviceSubMenuGS.addAction(self.GSSetPCModeAction)
            deviceSubMenuGS.addAction(self.GSSetOnlineAction)
            deviceSubMenuGS.addAction(self.GSRebootAction)
            deviceSubMenuGS.addAction(self.GSSerialAction)

    # submenu I2C
        if g.Devices["I2C"][g.ACTIV] :

            self.I2CInfoAction = QAction('Show Info', self, enabled=True)
            addMenuTip(self.I2CInfoAction, 'Show basic info on I2C device')
            self.I2CInfoAction.triggered.connect(lambda: self.fprintDeviceInfo("I2C"))

            self.I2CInfoActionExt = QAction('Show Extended Info', self, enabled=False)
            addMenuTip(self.I2CInfoActionExt, 'Show extended info on I2C device')
            self.I2CInfoActionExt.triggered.connect(lambda: self.fprintDeviceInfo("I2C", extended = True))

            self.I2CForceCalibAction = QAction('Calibrate CO2 Sensor', self, enabled=False)
            addMenuTip(self.I2CForceCalibAction, 'Force a CO2 calibration of the SCD41 sensor')
            self.I2CForceCalibAction.triggered.connect(lambda: gdev_i2c.forceCalibration())

            self.I2CScanAction = QAction('Scan I2C Bus', self, enabled=False)
            addMenuTip(self.I2CScanAction, 'Scan I2C bus for any sensors and report to NotePad (only when not-logging)')
            self.I2CScanAction.triggered.connect(lambda: gdev_i2c.scanI2CBus())

            self.I2CResetAction = QAction('Reset System', self, enabled=False)
            addMenuTip(self.I2CResetAction, 'Reset the I2C ELV dongle and attached sensors (only when not-logging)')
            self.I2CResetAction.triggered.connect(lambda: gdev_i2c.resetI2C())

            self.I2CSerialAction = QAction('Set Serial Port ...', self, enabled=True)
            addMenuTip(self.I2CSerialAction, 'Manually set the serial port of the I2C device')
            self.I2CSerialAction.triggered.connect(lambda: setDeviceSerialPort("I2C", g.I2Cusbport))

            deviceSubMenuI2C  = deviceMenu.addMenu("I2C Series")
            deviceSubMenuI2C.setToolTipsVisible(True)
            deviceSubMenuI2C.addAction(self.I2CInfoAction)
            deviceSubMenuI2C.addAction(self.I2CInfoActionExt)
            deviceSubMenuI2C.addAction(self.I2CForceCalibAction)
            deviceSubMenuI2C.addAction(self.I2CScanAction)
            deviceSubMenuI2C.addAction(self.I2CResetAction)
            deviceSubMenuI2C.addAction(self.I2CSerialAction)


    # submenu LabJack
        if g.Devices["LabJack"][g.ACTIV]  :

            self.LJInfoAction = QAction('Show Info', self, enabled=True)
            addMenuTip(self.LJInfoAction, 'Show basic info on LabJack device')
            self.LJInfoAction.triggered.connect(lambda: self.fprintDeviceInfo("LabJack"))

            self.LJInfoActionExt = QAction('Show Extended Info', self, enabled=False)
            addMenuTip(self.LJInfoActionExt, 'Show extended info on LabJack device')
            self.LJInfoActionExt.triggered.connect(lambda: self.fprintDeviceInfo("LabJack", extended = True))

            deviceSubMenuLJ  = deviceMenu.addMenu("LabJack Series")
            deviceSubMenuLJ.setToolTipsVisible(True)
            deviceSubMenuLJ.addAction(self.LJInfoAction)
            deviceSubMenuLJ.addAction(self.LJInfoActionExt)


    # submenu MiniMon
        if g.Devices["MiniMon"][g.ACTIV] :

            self.MiniMonInfoAction = QAction('Show Info', self, enabled=True)
            addMenuTip(self.MiniMonInfoAction, 'Show basic info on MiniMon device')
            self.MiniMonInfoAction.triggered.connect(lambda: self.fprintDeviceInfo("MiniMon"))

            deviceSubMenuMiniMon  = deviceMenu.addMenu("MiniMon Series")
            deviceSubMenuMiniMon.setToolTipsVisible(True)
            deviceSubMenuMiniMon.addAction(self.MiniMonInfoAction)


    # submenu Formula
        if g.Devices["Formula"][g.ACTIV] :

            self.FormulaInfoAction = QAction('Show Info', self, enabled=True)
            addMenuTip(self.FormulaInfoAction, 'Show basic info on Formula device')
            self.FormulaInfoAction.triggered.connect(lambda: self.fprintDeviceInfo("Formula"))

            deviceSubMenuFormula  = deviceMenu.addMenu("Formula Device Series")
            deviceSubMenuFormula.setToolTipsVisible(True)
            deviceSubMenuFormula.addAction(self.FormulaInfoAction)


    # submenu Manu
        if g.Devices["Manu"][g.ACTIV]  :

            self.ManuInfoAction = QAction('Show Info', self, enabled=True)
            addMenuTip(self.ManuInfoAction, 'Show basic info on Manu device')
            self.ManuInfoAction.triggered.connect(lambda: self.fprintDeviceInfo("Manu"))

            # self.ManuInfoActionExt = QAction('Show Extended Info', self, enabled=False)
            # addMenuTip(self.ManuInfoActionExt, 'Show extended info on Manu device')
            # self.ManuInfoActionExt.triggered.connect(lambda: self.fprintDeviceInfo("Manu", extended = True))

            # self.ManuValAction = QAction('Enter Values Manually', self, enabled=False)
            self.ManuValAction = QAction('Enter Values Manually', self, enabled=True)
            addMenuTip(self.ManuValAction, "Enter Values Manually")
            self.ManuValAction.triggered.connect(gdev_manu.setManuValue)

            deviceSubMenuManu  = deviceMenu.addMenu("Manu Series")
            deviceSubMenuManu.setToolTipsVisible(True)
            deviceSubMenuManu.addAction(self.ManuInfoAction)
            #deviceSubMenuManu.addAction(self.ManuInfoActionExt)
            deviceSubMenuManu.addAction(self.ManuValAction)


    # submenu WiFiServer
        if g.Devices["WiFiServer"][g.ACTIV] :

            self.WiFiInfoAction = QAction('Show Info', self, enabled=True)
            addMenuTip(self.WiFiInfoAction, 'Show basic info on WiFiServer device')
            self.WiFiInfoAction.triggered.connect(lambda: self.fprintDeviceInfo("WiFiServer"))

            # self.WiFiInfoActionExt = QAction('Show Extended Info', self, enabled=False)
            # addMenuTip(self.WiFiInfoActionExt, 'Show extended info on WiFiServer device')
            # self.WiFiInfoActionExt.triggered.connect(lambda: self.fprintDeviceInfo("WiFiServer", extended = True))

            self.WiFiPingAction = QAction("Ping WiFiServer Device", self)
            addMenuTip(self.WiFiPingAction, 'Ping WiFiServer Device and report success or failure')
            self.WiFiPingAction.triggered.connect(lambda: gdev_wifiserver.pingWiFiServer())

            # self.WiFiSettingsAction = QAction('Set WiFiServer Data Type ...', self, enabled=True)
            # addMenuTip(self.WiFiSettingsAction, "Set data type LAST or AVG")
            # self.WiFiSettingsAction.triggered.connect(gdev_wifiserver.setWiFiServerProperties)

            # self.WiFiResetServerAction = QAction("Reset WiFiServer", self)
            # addMenuTip(self.WiFiResetServerAction, 'Reset the WiFiServer itself, but not the devices')
            # self.WiFiResetServerAction.triggered.connect(lambda: gdev_wifiserver.resetWiFiServer())

            self.WiFiResetDevicesAction = QAction("Reset WiFiServer Devices", self)
            addMenuTip(self.WiFiResetDevicesAction, 'Reset all WiFiServer Devices, but not the WiFiServer itself')
            self.WiFiResetDevicesAction.triggered.connect(lambda: gdev_wifiserver.resetWiFiServerDevices())

            deviceSubMenuWiFi  = deviceMenu.addMenu("WiFiServer Series")
            deviceSubMenuWiFi.setToolTipsVisible(True)
            deviceSubMenuWiFi.addAction(self.WiFiInfoAction)
            # deviceSubMenuWiFi.addAction(self.WiFiInfoActionExt)
            deviceSubMenuWiFi.addAction(self.WiFiPingAction)
            # deviceSubMenuWiFi.addAction(self.WiFiSettingsAction)
            # deviceSubMenuWiFi.addAction(self.WiFiResetServerAction)
            deviceSubMenuWiFi.addAction(self.WiFiResetDevicesAction)


    # submenu WiFiClient
        if g.Devices["WiFiClient"][g.ACTIV]  :

            self.WiFiClientInfoAction = QAction('Show Info', self, enabled=True)
            addMenuTip(self.WiFiClientInfoAction, 'Show basic info on WiFiClient device')
            self.WiFiClientInfoAction.triggered.connect(lambda: self.fprintDeviceInfo("WiFiClient"))

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


    # submenu RaspiPulse
        if g.Devices["RaspiPulse"][g.ACTIV]  :

            self.RaspiPulseInfoAction = QAction('Show Info', self, enabled=True)
            addMenuTip(self.RaspiPulseInfoAction, 'Show basic info on RaspiPulse device')
            self.RaspiPulseInfoAction.triggered.connect(lambda: self.fprintDeviceInfo("RaspiPulse"))

            self.RaspiPulseInfoActionExt = QAction('Show Extended Info', self, enabled=False)
            addMenuTip(self.RaspiPulseInfoActionExt, 'Show extended info on RaspiPulse device')
            self.RaspiPulseInfoActionExt.triggered.connect(lambda: self.fprintDeviceInfo("RaspiPulse", extended = True))

            self.RaspiPulseResetAction = QAction("Reset RaspiPulse Device", self)
            addMenuTip(self.RaspiPulseResetAction, 'Reset RaspiPulse Device')
            self.RaspiPulseResetAction.triggered.connect(lambda: gdev_raspipulse.resetRaspiPulse("Reset"))

            deviceSubMenuRaspiPulse  = deviceMenu.addMenu("RaspiPulse Series")
            deviceSubMenuRaspiPulse.setToolTipsVisible(True)
            deviceSubMenuRaspiPulse.addAction(self.RaspiPulseInfoAction)
            deviceSubMenuRaspiPulse.addAction(self.RaspiPulseInfoActionExt)
            deviceSubMenuRaspiPulse.addAction(self.RaspiPulseResetAction)


    # submenu RaspiI2C
        if g.Devices["RaspiI2C"][g.ACTIV]  :

            self.RaspiI2CInfoAction = QAction('Show Info', self, enabled=True)
            addMenuTip(self.RaspiI2CInfoAction, 'Show basic info on RaspiI2C device')
            self.RaspiI2CInfoAction.triggered.connect(lambda: self.fprintDeviceInfo("RaspiI2C"))

            self.RaspiI2CInfoActionExt = QAction('Show Extended Info', self, enabled=False)
            addMenuTip(self.RaspiI2CInfoActionExt, 'Show extended info on RaspiI2C device')
            self.RaspiI2CInfoActionExt.triggered.connect(lambda: self.fprintDeviceInfo("RaspiI2C", extended = True))

            # self.RaspiI2CResetAction = QAction("Reset RaspiI2C Device", self)
            # addMenuTip(self.RaspiI2CResetAction, 'Reset RaspiI2C Device')
            # self.RaspiI2CResetAction.triggered.connect(lambda: gdev_raspii2c.resetRaspiI2C())

            self.RaspiI2CResetAction = QAction("Reset RaspiI2C Device", self, enabled=False)
            addMenuTip(self.RaspiI2CResetAction, 'Reset RaspiI2C Device')
            self.RaspiI2CResetAction.triggered.connect(lambda: gdev_raspii2c.resetRaspiI2C())

            deviceSubMenuRaspiI2C  = deviceMenu.addMenu("RaspiI2C Series")
            deviceSubMenuRaspiI2C.setToolTipsVisible(True)
            deviceSubMenuRaspiI2C.addAction(self.RaspiI2CInfoAction)
            deviceSubMenuRaspiI2C.addAction(self.RaspiI2CInfoActionExt)
            deviceSubMenuRaspiI2C.addAction(self.RaspiI2CResetAction)


    # submenu RadPro
        if g.Devices["RadPro"][g.ACTIV] :

            self.RadProInfoAction = QAction('Show Info', self, enabled=True)
            addMenuTip(self.RadProInfoAction, 'Show basic info on RadPro device')
            self.RadProInfoAction.triggered.connect(lambda: self.fprintDeviceInfo("RadPro"))

            self.RadProInfoExtAction = QAction('Show Info', self, enabled=True)
            addMenuTip(self.RadProInfoExtAction, 'Show basic info on RadPro device')
            self.RadProInfoExtAction.triggered.connect(lambda: self.fprintDeviceInfo("RadPro", extended = False))

            self.RadProInfoExtAction = QAction('Show Extended Info', self, enabled=False)
            addMenuTip(self.RadProInfoExtAction, 'Show extended info on RaspiI2C device')
            self.RadProInfoExtAction.triggered.connect(lambda: self.fprintDeviceInfo("RadPro", extended = True))

            self.RadProSetTimeAction = QAction('Set RadPro DateTime to GeigerLog DateTime', self, enabled=False)
            addMenuTip(self.RadProSetTimeAction, "Set the Date and Time of the RadPro device to GeigerLog's Date and Time")
            self.RadProSetTimeAction.triggered.connect(lambda: gdev_radpro.setRadProDateTime())

            self.RadProConfigAction = QAction('Set RadPro Config for Anode Voltage', self, enabled=False)
            addMenuTip(self.RadProConfigAction, "Set the Frequency and Duty Cycle of the Anode-High-Voltage Generator")
            self.RadProConfigAction.triggered.connect(lambda: gdev_radpro.editRadProConfig())

            self.RadProSetSerialPortAction = QAction('Set Serial Port ...', self, enabled=True)
            addMenuTip(self.RadProSetSerialPortAction, 'Manually set the serial port of the RadPro device')
            self.RadProSetSerialPortAction.triggered.connect(lambda: setDeviceSerialPort("RadPro", g.RadProPort))

            deviceSubMenuRadPro  = deviceMenu.addMenu("RadPro Series")
            deviceSubMenuRadPro.setToolTipsVisible(True)
            deviceSubMenuRadPro.addAction(self.RadProInfoAction)
            deviceSubMenuRadPro.addAction(self.RadProInfoExtAction)
            deviceSubMenuRadPro.addAction(self.RadProSetTimeAction)
            deviceSubMenuRadPro.addAction(self.RadProConfigAction)
            deviceSubMenuRadPro.addAction(self.RadProSetSerialPortAction)



    # widgets for device in toolbar
        # devBtnSize = 65
        devBtnSize = 70

        #  '#00C853',        # Google color green
        #  '#ffe500',        # Google color yellow
        #  '#EA4335',        # Google color red
        # !!! MUST NOT have a colon ':' after QPushButton !!!
        self.dbtnStyleSheetOFF   = "QPushButton {margin-right:5px;  }"
        self.dbtnStyleSheetError = "QPushButton {margin-right:5px; background-color: #EA4335; border-radius: 2px; border:1px solid silver; color: black; font-size:14px; font-weight:bold}"
        self.dbtnStyleSheetSimul = "QPushButton {margin-right:5px; background-color: #ffe500; border-radius: 2px; border:1px solid silver; color: black; font-size:14px; font-weight:bold}"
        self.dbtnStyleSheetON    = "QPushButton {margin-right:5px; background-color: #00C853; border-radius: 2px; border:1px solid silver; color: black; font-size:14px; font-weight:bold}"

        # Power button (for GMC only)
        self.dbtnGMCPower = QPushButton()
        self.dbtnGMCPower.setIcon(QIcon(QPixmap(os.path.join(g.resDir, 'icon_power-round_off.png'))))
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
        self.dbtnGMC.setToolTip("GMC Device - Click Button for Device Info")
        self.dbtnGMC.setStyleSheet(self.dbtnStyleSheetOFF)
        self.dbtnGMC.setAutoFillBackground(True) # This is important!! Why???
        self.dbtnGMC.clicked.connect(lambda: self.fprintDeviceInfo("GMC"))

        self.connectTextAudio = 'Audio'
        self.dbtnAudio = QPushButton(self.connectTextAudio)
        self.dbtnAudio.setFixedSize(devBtnSize, 32)
        self.dbtnAudio.setToolTip("AudioCounter Device - Click Button for Device Info")
        self.dbtnAudio.setStyleSheet(self.dbtnStyleSheetOFF)
        self.dbtnAudio.setAutoFillBackground(True)
        self.dbtnAudio.clicked.connect(lambda: self.fprintDeviceInfo(self.connectTextAudio))

        self.connectTextPulse = 'SPulse'
        self.dbtnPulse = QPushButton(self.connectTextPulse)
        self.dbtnPulse.setFixedSize(devBtnSize, 32)
        self.dbtnPulse.setToolTip("SerialPulseCounter Device - Click Button for Device Info")
        self.dbtnPulse.setStyleSheet(self.dbtnStyleSheetOFF)
        self.dbtnPulse.setAutoFillBackground(True)
        # self.dbtnPulse.clicked.connect(lambda: self.fprintDeviceInfo(self.connectTextPulse))
        self.dbtnPulse.clicked.connect(lambda: self.fprintDeviceInfo("SerialPulse"))

        self.connectTextIoT = 'IoT'
        self.dbtnIoT = QPushButton(self.connectTextIoT)
        self.dbtnIoT.setFixedSize(devBtnSize,32)
        self.dbtnIoT.setToolTip("IoT Device - Click Button for Device Info")
        self.dbtnIoT.setStyleSheet(self.dbtnStyleSheetOFF)
        self.dbtnIoT.setAutoFillBackground(True)
        self.dbtnIoT.clicked.connect(lambda: self.fprintDeviceInfo("IoT"))

        self.connectTextRM = 'RadM'
        self.dbtnRM = QPushButton(self.connectTextRM)
        self.dbtnRM.setFixedSize(devBtnSize,32)
        self.dbtnRM.setToolTip("RadMon Device - Click Button for Device Info")
        self.dbtnRM.setStyleSheet(self.dbtnStyleSheetOFF)
        self.dbtnRM.setAutoFillBackground(True)
        self.dbtnRM.clicked.connect(lambda: self.fprintDeviceInfo("RadMon"))

        self.connectTextAmbio = 'Ambio'
        self.dbtnAmbio = QPushButton(self.connectTextAmbio)
        self.dbtnAmbio.setFixedSize(devBtnSize, 32)
        self.dbtnAmbio.setToolTip("AmbioMon++ Device - Click Button for Device Info")
        self.dbtnAmbio.setStyleSheet(self.dbtnStyleSheetOFF)
        self.dbtnAmbio.setAutoFillBackground(True)
        self.dbtnAmbio.clicked.connect(lambda: self.fprintDeviceInfo("AmbioMon"))

        self.connectTextGS = 'GScout'
        self.dbtnGS = QPushButton(self.connectTextGS)
        self.dbtnGS.setFixedSize(devBtnSize, 32)
        self.dbtnGS.setToolTip("GammaScout Device - Click Button for Device Info")
        self.dbtnGS.setStyleSheet(self.dbtnStyleSheetOFF)
        self.dbtnGS.setAutoFillBackground(True)
        self.dbtnGS.clicked.connect(lambda: self.fprintDeviceInfo("GammaScout"))

        self.connectTextI2C = 'I2C'
        self.dbtnI2C = QPushButton(self.connectTextI2C)
        self.dbtnI2C.setFixedSize(devBtnSize, 32)
        self.dbtnI2C.setToolTip("I2C Device - Click Button for Device Info")
        self.dbtnI2C.setStyleSheet(self.dbtnStyleSheetOFF)
        self.dbtnI2C.setAutoFillBackground(True)
        self.dbtnI2C.clicked.connect(lambda: self.fprintDeviceInfo("I2C" ))

        self.connectTextLJ = 'LabJck'
        self.dbtnLJ = QPushButton(self.connectTextLJ)
        self.dbtnLJ.setFixedSize(devBtnSize, 32)
        self.dbtnLJ.setToolTip("LabJack Device - Click Button for Device Info")
        self.dbtnLJ.setStyleSheet(self.dbtnStyleSheetOFF)
        self.dbtnLJ.setAutoFillBackground(True)
        self.dbtnLJ.clicked.connect(lambda: self.fprintDeviceInfo("LabJack"))

        self.connectTextMiniMon = 'MiniM'
        self.dbtnMiniMon = QPushButton(self.connectTextMiniMon)
        self.dbtnMiniMon.setFixedSize(devBtnSize, 32)
        self.dbtnMiniMon.setToolTip("MiniMon Device - Click Button for Device Info")
        self.dbtnMiniMon.setStyleSheet(self.dbtnStyleSheetOFF)
        self.dbtnMiniMon.setAutoFillBackground(True)
        self.dbtnMiniMon.clicked.connect(lambda: self.fprintDeviceInfo("MiniMon"))

        self.connectTextFormula = 'Forml'
        self.dbtnFormula = QPushButton(self.connectTextFormula)
        self.dbtnFormula.setFixedSize(devBtnSize, 32)
        self.dbtnFormula.setToolTip("Formula Device - Click Button for Device Info")
        self.dbtnFormula.setStyleSheet(self.dbtnStyleSheetOFF)
        self.dbtnFormula.setAutoFillBackground(True)
        self.dbtnFormula.clicked.connect(lambda: self.fprintDeviceInfo("Formula"))

        self.connectTextWiFiClient = 'WiFiC'
        self.dbtnWClient = QPushButton(self.connectTextWiFiClient)
        self.dbtnWClient.setFixedSize(devBtnSize, 32)
        self.dbtnWClient.setToolTip("WiFiClient Device - Click Button for Device Info")
        self.dbtnWClient.setStyleSheet(self.dbtnStyleSheetOFF)
        self.dbtnWClient.setAutoFillBackground(True)
        self.dbtnWClient.clicked.connect(lambda: self.fprintDeviceInfo("WiFiClient"))

        self.connectTextWiFiServer = 'WiFiS'
        self.dbtnWServer = QPushButton(self.connectTextWiFiServer)
        self.dbtnWServer.setFixedSize(devBtnSize, 32)
        self.dbtnWServer.setToolTip("WiFiServer Device - Click Button for Device Info")
        self.dbtnWServer.setStyleSheet(self.dbtnStyleSheetOFF)
        self.dbtnWServer.setAutoFillBackground(True)
        self.dbtnWServer.clicked.connect(lambda: self.fprintDeviceInfo("WiFiServer"))

        self.connectTextRaspiI2C = 'RI2C'
        self.dbtnRI2C = QPushButton(self.connectTextRaspiI2C)
        self.dbtnRI2C.setFixedSize(devBtnSize, 32)
        self.dbtnRI2C.setToolTip("Raspi I2C Device - Click Button for Device Info")
        self.dbtnRI2C.setStyleSheet(self.dbtnStyleSheetOFF)
        self.dbtnRI2C.setAutoFillBackground(True)
        self.dbtnRI2C.clicked.connect(lambda: self.fprintDeviceInfo("RaspiI2C"))

        self.connectTextRaspiPulse = 'RPuls'
        self.dbtnRPulse = QPushButton(self.connectTextRaspiPulse)
        self.dbtnRPulse.setFixedSize(devBtnSize, 32)
        self.dbtnRPulse.setToolTip("Raspi Pulse Device - Click Button for Device Info")
        self.dbtnRPulse.setStyleSheet(self.dbtnStyleSheetOFF)
        self.dbtnRPulse.setAutoFillBackground(True)
        self.dbtnRPulse.clicked.connect(lambda: self.fprintDeviceInfo("RaspiPulse"))

        self.connectTextManu = 'Manu'
        self.dbtnManu = QPushButton(self.connectTextManu)
        self.dbtnManu.setFixedSize(devBtnSize, 32)
        self.dbtnManu.setToolTip("Manu Device - Click Button for Device Info")
        self.dbtnManu.setStyleSheet(self.dbtnStyleSheetOFF)
        self.dbtnManu.setAutoFillBackground(True)
        self.dbtnManu.clicked.connect(lambda: self.fprintDeviceInfo("Manu"))

        self.connectTextRadPro = "RadPro"
        self.dbtnRadPro =  QPushButton(self.connectTextRadPro)
        self.dbtnRadPro.setFixedSize(devBtnSize, 32)
        self.dbtnRadPro.setToolTip("RadPro Device - Click for Device Info")
        self.dbtnRadPro.setStyleSheet(self.dbtnStyleSheetOFF)
        self.dbtnRadPro.setAutoFillBackground(True)
        self.dbtnRadPro.clicked.connect(lambda: self.fprintDeviceInfo("RadPro"))


    # toolbar Device
        toolbar = self.addToolBar('Device')
        toolbar.setToolTip("Device Toolbar")
        toolbar.setIconSize(QSize(32,32))                       # standard size is too small

        toolbar.addAction(self.toggleDeviceConnectionAction)    # Connect icon
        toolbar.addWidget(QLabel("   "))                        # spacer

        if g.Devices["GMC"]         [g.ACTIV]  : toolbar.addWidget(self.dbtnGMCPower)        # GMC power icon
        if g.Devices["GMC"]         [g.ACTIV]  : toolbar.addWidget(self.dbtnGMC)             # GMC device display
        if g.Devices["Audio"]       [g.ACTIV]  : toolbar.addWidget(self.dbtnAudio)           # AudioCounter device display
        if g.Devices["SerialPulse"] [g.ACTIV]  : toolbar.addWidget(self.dbtnPulse)           # Pulse Counter by USB-to-Serial adapter
        if g.Devices["IoT"]         [g.ACTIV]  : toolbar.addWidget(self.dbtnIoT)             # IoT device display
        if g.Devices["RadMon"]      [g.ACTIV]  : toolbar.addWidget(self.dbtnRM)              # RadMon device display
        if g.Devices["AmbioMon"]    [g.ACTIV]  : toolbar.addWidget(self.dbtnAmbio)           # Manu device display
        if g.Devices["GammaScout"]  [g.ACTIV]  : toolbar.addWidget(self.dbtnGS)              # Gamma-Scout device display
        if g.Devices["I2C"]         [g.ACTIV]  : toolbar.addWidget(self.dbtnI2C)             # I2C device display
        if g.Devices["LabJack"]     [g.ACTIV]  : toolbar.addWidget(self.dbtnLJ)              # LabJack device display
        if g.Devices["MiniMon"]     [g.ACTIV]  : toolbar.addWidget(self.dbtnMiniMon)         # MiniMon device display
        if g.Devices["Formula"]     [g.ACTIV]  : toolbar.addWidget(self.dbtnFormula)         # Formula device display
        if g.Devices["WiFiClient"]  [g.ACTIV]  : toolbar.addWidget(self.dbtnWClient)         # WiFiClient device display
        if g.Devices["WiFiServer"]  [g.ACTIV]  : toolbar.addWidget(self.dbtnWServer)         # WiFiServer device display
        if g.Devices["RaspiI2C"]    [g.ACTIV]  : toolbar.addWidget(self.dbtnRI2C)            # RaspiI2C device display
        if g.Devices["RaspiPulse"]  [g.ACTIV]  : toolbar.addWidget(self.dbtnRPulse)          # RaspiPulse device display
        if g.Devices["Manu"]        [g.ACTIV]  : toolbar.addWidget(self.dbtnManu)            # Manu device display
        if g.Devices["RadPro"]      [g.ACTIV]  : toolbar.addWidget(self.dbtnRadPro)          # RadPro device display


#Log Menu
        self.logLoadFileAction = QAction(QIcon(QPixmap(os.path.join(g.resDir, 'icon_Log_DB.svg.png'))), 'Get Log from Database or Create New One ...', self)
        self.logLoadFileAction.setShortcut('Ctrl+L')
        addMenuTip(self.logLoadFileAction, 'Load or Create database for logging, and plot')
        self.logLoadFileAction.triggered.connect(lambda: self.getFileLog(source="Database"))

        self.logLoadCSVAction = QAction(QIcon(QPixmap(os.path.join(g.resDir, 'icon_Log_CSV.svg.png'))), 'Get Log from CSV File ...', self)
        addMenuTip(self.logLoadCSVAction, 'Load existing CSV file, convert to database, and plot')
        self.logLoadCSVAction.triggered.connect(lambda: self.getFileLog(source="CSV File"))

        self.startloggingAction = QAction(QIcon(QPixmap(os.path.join(g.resDir, 'icon_log_start.png'))), 'Start Logging', self, enabled=False)
        addMenuTip(self.startloggingAction, 'Start logging from devices')
        self.startloggingAction.triggered.connect(self.startLogging)

        self.stoploggingAction = QAction(QIcon(QPixmap(os.path.join(g.resDir, 'icon_log_stop.png'))), 'Stop Logging', self, enabled=False)
        addMenuTip(self.stoploggingAction, 'Stop logging from devices')
        self.stoploggingAction.triggered.connect(self.stopLogging)

        # add comment
        self.addCommentAction = QAction('Add Comment to Log ...', self, enabled=False)
        addMenuTip(self.addCommentAction, 'Add a comment to the current log')
        self.addCommentAction.triggered.connect(lambda: self.addComment("Log"))

        # clear Log File
        self.clearLogfileAction = QAction('Clear Log File ...', self, enabled=False)
        addMenuTip(self.clearLogfileAction, 'Set the log file to empty state')
        self.clearLogfileAction.triggered.connect(lambda: self.clearLogfile())

        self.showLogDataAction = QAction('Show Log Data', self)
        addMenuTip(self.showLogDataAction, 'Show all records from current log')
        self.showLogDataAction.triggered.connect(lambda: self.showData("Log", full=True))

        self.showLogTagsAction = QAction('Show Log Data Tags/Comments', self)
        addMenuTip(self.showLogTagsAction, 'Show only records from current log containing tags or comments')
        self.showLogTagsAction.triggered.connect(lambda: self.showDBTags("Log"))

        self.showLogExcerptAction = QAction('Show Log Data Excerpt', self)
        addMenuTip(self.showLogExcerptAction, 'Show first and last few records of current log')
        self.showLogExcerptAction.triggered.connect(lambda: self.showData("Log", full=False))

        self.quickLogAction = QAction(QIcon(QPixmap(os.path.join(g.resDir, 'icon_quick_log.png'))), 'Quick Log', self, enabled=False)
        addMenuTip(self.quickLogAction, 'One-click log. Saves always into database default.logdb; will be overwritten on next Quick Log click')
        self.quickLogAction.triggered.connect(self.quickLog)

        self.logSnapAction = QAction(QIcon(QPixmap(os.path.join(g.resDir, 'icon_log_snap.png'))), 'Snap a new log record', self, enabled=False)
        addMenuTip(self.logSnapAction, 'Get a new log record immediately')
        self.logSnapAction.triggered.connect(self.snapLogValue)

        self.setLogTimingAction = QAction('Set LogCycle ...', self, enabled=True)
        self.setLogTimingAction.setIcon(QIcon(QPixmap(os.path.join(g.resDir, 'icon_log_options.png'))))
        addMenuTip(self.setLogTimingAction, 'Set LogCycle duration in seconds')
        self.setLogTimingAction.triggered.connect(self.setLogCycle)

        self.logSaveCSVAction = QAction('Save Log Data into CSV file', self)
        addMenuTip(self.logSaveCSVAction, "Save all records from current log into a CSV file with extension 'csv'")
        self.logSaveCSVAction.triggered.connect(lambda: gsup_sql.saveDataToCSV("Log", full= True))

        loggingMenu = self.menubar.addMenu('&Log')
        loggingMenu.setToolTipsVisible(True)
        loggingMenu.addAction(self.logLoadFileAction)
        loggingMenu.addAction(self.logLoadCSVAction)
        loggingMenu.addAction(self.addCommentAction)
        loggingMenu.addAction(self.clearLogfileAction)

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

        # loggingMenu.triggered[QAction].connect(self.processtrigger) # just for testing; no action done

        toolbar = self.addToolBar('Log')
        toolbar.setToolTip("Log Toolbar")
        toolbar.setIconSize(QSize(32,32))  # standard size is too small
        toolbar.addAction(self.logLoadFileAction)
        toolbar.addAction(self.startloggingAction)
        toolbar.addAction(self.quickLogAction)
        toolbar.addAction(self.logSnapAction)
        toolbar.addAction(self.stoploggingAction)



    # progress bar
        self.btnProgress = QProgressBar(self)
        # self.btnProgress.setFixedWidth(DataButtonWidth)
        self.btnProgress.setEnabled(True)
        self.btnProgress.setToolTip('Progress Bar for Log Cycle')
        self.btnProgress.setFormat('Log Progress')
        self.btnProgress.setStyleSheet("QProgressBar::chunk {background-color:#F4D345; width:1px; margin:0px;} \
                                        QProgressBar{background-color:#F7F7F7; font-weight:bold; font-size:10px; color:rgb(0,0,0); border:1px solid #AE9731; text-align:center; width:80px;height:30px;}")

        # self.btnProgress.clicked.connect(lambda: self.setLogCycle()) # cannot click progress bar
        # self.btnProgress.setMinimum(0)
        # self.btnProgress.setMaximum(0)
        self.btnProgress.setInvertedAppearance(False)

        toolbar.addSeparator()
        toolbar.addWidget(self.btnProgress)



#History Menu
        # load from DB
        self.loadHistDBAction = QAction(QIcon(QPixmap(os.path.join(g.resDir, 'icon_hist_DB_active.svg.png'))), 'Get History from Database ...', self)
        self.loadHistDBAction.setShortcut('Ctrl+H')
        addMenuTip(self.loadHistDBAction, 'Load history data from database and plot')
        self.loadHistDBAction.triggered.connect(lambda: self.getFileHistory("Database"))

        # load from CSV file
        self.loadHistHisAction = QAction(QIcon(QPixmap(os.path.join(g.resDir, 'icon_hist_CSV.svg.png'))), 'Get History from CSV File ...', self)
        addMenuTip(self.loadHistHisAction, 'Load existing CSV file, convert to database file, and plot')
        self.loadHistHisAction.triggered.connect(lambda: self.getFileHistory("Parsed File"))

        # add comment
        self.addHistCommentAction = QAction(QIcon(QPixmap(os.path.join(g.resDir, ''))), 'Add Comment to History ...', self, enabled=False)
        addMenuTip(self.addHistCommentAction, 'Add a comment to the current history')
        self.addHistCommentAction.triggered.connect(lambda: self.addComment("His"))

        historyMenu = self.menubar.addMenu('&History')
        historyMenu.setToolTipsVisible(True)

        historyMenu.addAction(self.loadHistDBAction)
        historyMenu.addAction(self.loadHistHisAction)
        historyMenu.addAction(self.addHistCommentAction)

        historyMenu.addSeparator()


### begin device specific History actions #########################

    # valid for GMC only
        if g.Devices["GMC"][g.ACTIV] :
            # get his from device
            self.histGMCDeviceAction = QAction(QIcon(QPixmap(os.path.join(g.resDir, 'icon_hist_device_active.png'))), 'Get History from Device ...', self, enabled=False)
            addMenuTip(self.histGMCDeviceAction, 'Load history data from any GMC device, create database, and plot\n(when NOT logging)')
            self.histGMCDeviceAction.triggered.connect(lambda: self.getFileHistory("Device"))

            # get his from bin file
            self.loadHistBinAction = QAction(QIcon(QPixmap(os.path.join(g.resDir, 'icon_hist_bin_active.png'))), 'Get History from GMC Binary File ...', self)
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

            # show AA / FF map
            self.historyFFAction = QAction("Show History Binary Data as AA / FF Map", self)
            addMenuTip(self.historyFFAction, "Show History Binary Data as a map highlighting the locations of bytes with FF value (FF=empty value)")
            self.historyFFAction.triggered.connect(lambda: gsup_sql.createByteMapFromDB(0xFF))

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
        if g.Devices["GammaScout"][g.ACTIV]:
            self.histGSDeviceAction = QAction(QIcon(QPixmap(os.path.join(g.resDir, 'icon_hist_device_active.png'))), 'Get History from Device ...', self, enabled=False)
            addMenuTip(self.histGSDeviceAction, 'Load history data from any Gamma-Scout device, create database, and plot\n(when NOT logging)')
            self.histGSDeviceAction.triggered.connect(lambda: self.getFileHistory("GSDevice"))

            self.histGSDatFileAction = QAction(QIcon(QPixmap(os.path.join(g.resDir, 'icon_hist_device_active.png'))), 'Get History from Gamma-Scout Dat File ...', self)
            addMenuTip(self.histGSDatFileAction, 'Load history data from a Gamma-Scout dat file, create database, and plot')
            self.histGSDatFileAction.triggered.connect(lambda: self.getFileHistory("GSDatFile"))

            self.showHistDatDataAction = QAction('Show History Dat Data', self)
            addMenuTip(self.showHistDatDataAction, 'Show the history data in Gamma-Scout like *.dat file')
            self.showHistDatDataAction.triggered.connect(lambda: gdev_gammascout.GSshowDatData())

            self.showHistDatDataSaveAction = QAction('Save History Data to Dat File', self)
            addMenuTip(self.showHistDatDataSaveAction, 'Save the history data as Gamma-Scout *.dat format')
            self.showHistDatDataSaveAction.triggered.connect(lambda: gdev_gammascout.GSsaveDatDataToDatFile())

            historySubMenuGS = historyMenu.addMenu("Gamma Scout Series")
            historySubMenuGS.setToolTipsVisible(True)

            historySubMenuGS.addAction(self.histGSDeviceAction)
            historySubMenuGS.addAction(self.histGSDatFileAction)

            historySubMenuGS.addSeparator()
            historySubMenuGS.addAction(self.showHistDatDataAction)

            historySubMenuGS.addSeparator()
            historySubMenuGS.addAction(self.showHistDatDataSaveAction)


    # valid for AmbioMon only
        if g.Devices["AmbioMon"][g.ACTIV] :
            self.histAMDeviceCAMAction = QAction(QIcon(QPixmap(os.path.join(g.resDir, 'icon_hist_device_active.png'))), 'Get History Binary CAM data from Device', self, enabled=False)
            addMenuTip(self.histAMDeviceCAMAction, 'Load Counter & Ambient history data from AmbioMon device, create database, and plot')
            self.histAMDeviceCAMAction.triggered.connect(lambda: self.getFileHistory("AMDeviceCAM"))

            self.histAMDeviceCPSAction = QAction(QIcon(QPixmap(os.path.join(g.resDir, 'icon_hist_device_active.png'))), 'Get History Binary CPS data from Device', self, enabled=False)
            addMenuTip(self.histAMDeviceCPSAction, 'Load Counts Per Second history data from AmbioMon device, create database, and plot')
            self.histAMDeviceCPSAction.triggered.connect(lambda: self.getFileHistory("AMDeviceCPS"))

            self.histAMCAMFileAction = QAction(QIcon(QPixmap(os.path.join(g.resDir, 'icon_hist_device_active.png'))), 'Get History Binary CAM data from File ...', self)
            addMenuTip(self.histAMCAMFileAction, 'Load history data from an AmbioMon CAM file, create database, and plot')
            self.histAMCAMFileAction.triggered.connect(lambda: self.getFileHistory("AMFileCAM"))

            self.histAMCPSFileAction = QAction(QIcon(QPixmap(os.path.join(g.resDir, 'icon_hist_device_active.png'))), 'Get History Binary CPS data from File ...', self)
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



    # valid for RadPro only
        if g.Devices["RadPro"][g.ACTIV] :
            # get all history from device
            self.histRadProLoadAllAction = QAction(QIcon(QPixmap(os.path.join(g.resDir, 'icon_hist_device_active.png'))), 'Get History from Device ...', self, enabled=False)
            addMenuTip(self.histRadProLoadAllAction, 'Load history data from any RadPro device, create database, and plot\n(when NOT logging)')
            self.histRadProLoadAllAction.triggered.connect(lambda: self.getFileHistory("RadPro"))

            # # get new history from device
            # self.histRadProLoadNewAction = QAction(QIcon(QPixmap(os.path.join(g.resDir, 'icon_hist_device_active.png'))), 'Get New History from Device ...', self, enabled=False)
            # addMenuTip(self.histRadProLoadNewAction, 'Load new history data from any RadPro device, create database, and plot\n(when NOT logging)')
            # self.histRadProLoadNewAction.triggered.connect(lambda: self.getFileHistory("RadPro Device (new)"))

            historySubMenuRadPro = historyMenu.addMenu("RadPro Series")
            historySubMenuRadPro.setToolTipsVisible(True)

            historySubMenuRadPro.addAction(self.histRadProLoadAllAction)
            # historySubMenuRadPro.addAction(self.histRadProLoadNewAction)


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

        toolbar = self.addToolBar('History')
        toolbar.setToolTip("History Toolbar")
        toolbar.setIconSize(QSize(32, 32))  # standard size is too small
        toolbar.addAction(self.loadHistDBAction)

# Web menu
        # menu entry and toolbar button for Show IP Address
        self.IPAddrAction = QAction('Show IP Status', self, enabled=True)
        self.IPAddrAction.setIcon(QIcon(QPixmap(os.path.join(g.resDir, 'icon_ip_address.png'))))
        addMenuTip(self.IPAddrAction, "Show GeigerLog's current IP Address and Ports usage")
        self.IPAddrAction.triggered.connect(lambda: self.showIPStatus())

        # menu entry and toolbar button for Web Server access
        self.MonServerAction = QAction('Set up Monitor Server ...', self, enabled=True)
        self.MonServerAction.setIcon(QIcon(QPixmap(os.path.join(g.resDir, 'icon_monserver_inactive.png'))))
        addMenuTip(self.MonServerAction, "Set Properties of Monitor Server")
        self.MonServerAction.triggered.connect(lambda: gweb_monserv.initMonServer())

        # # menu entry and toolbar button for Telegram access
        # self.TelegramAction = QAction(QIcon(QPixmap(os.path.join(g.resDir, 'icon_Telegram_inactive.png'))), 'Set up Telegram Messenger ...', self, enabled=True)
        # addMenuTip(self.TelegramAction, 'Set Properties of Telegram Messenger Updating')
        # self.TelegramAction.triggered.connect(lambda: gsup_telegram.initTelegram())

        # menu entry and toolbar button for GMC Map access
        self.GMCmapAction = QAction('Set up Radiation World Map ...', self, enabled=True)
        self.GMCmapAction.setIcon(QIcon(QPixmap(os.path.join(g.resDir, 'icon_world_v2_inactive.png'))))
        addMenuTip(self.GMCmapAction, 'Set Properties of Radiation World Map Updating')
        self.GMCmapAction.triggered.connect(lambda: gweb_radworld.setupRadWorldMap())

        webMenu = self.menubar.addMenu('&Web')
        webMenu.setToolTipsVisible(True)
        webMenu.addAction(self.IPAddrAction)
        webMenu.addAction(self.MonServerAction)
        # if g.TelegramActivation: webMenu.addAction(self.TelegramAction)
        webMenu.addAction(self.GMCmapAction)

        toolbar = self.addToolBar('Web')
        toolbar.setToolTip("Web Toolbar")
        toolbar.setIconSize(QSize(32,32))  # standard size is too small
        toolbar.addAction(self.IPAddrAction)
        toolbar.addAction(self.MonServerAction)
        # if g.TelegramActivation: toolbar.addAction(self.TelegramAction)
        toolbar.addAction(self.GMCmapAction)

# Tools menu
        # menu entry and toolbar button for tools

        PlotLogAction = QAction('Plot Full Log', self)
        addMenuTip(PlotLogAction, 'Plot the complete Log file')
        PlotLogAction.triggered.connect(lambda: self.plotGraph('Log', full=False))

        PlotHisAction = QAction('Plot Full History', self)
        addMenuTip(PlotHisAction, 'Plot the complete History file')
        PlotHisAction.triggered.connect(lambda: self.plotGraph('His', full=False))

        # separator

        showSystemInfoAction = QAction('Show System Info', self)
        addMenuTip(showSystemInfoAction, 'Show Details on the Current Program Settings and Environment')
        showSystemInfoAction.triggered.connect(lambda: showSystemInfo())

        # separator

        fprintSuStAction =  QAction('Show SuSt (Summary Statistics) of Plot Data ', self)
        addMenuTip(fprintSuStAction, "Shows Summary Statistics of variables and data as in the current plot.<br><br>To see stats for UNSCALED data hold CTRL while clicking.")
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

        # separator

        editFormulasAction = QAction('Value and Graph Formula ...', self)
        addMenuTip(editFormulasAction, "Formula - View and edit current settings for value- and graph-formulas")
        editFormulasAction.triggered.connect(lambda: self.editFormulas())

        SaveGraph2FileAction = QAction("Save Graph to File", self)
        addMenuTip(SaveGraph2FileAction, "Save the graph as a 'PNG' file")
        SaveGraph2FileAction.triggered.connect(lambda: saveGraphToFile())

        fprintPlotDataAction = QAction('Show Plot Data', self)
        addMenuTip(fprintPlotDataAction, 'Show the DateTime and values of all variables as currently selected in Plot')
        fprintPlotDataAction.triggered.connect(lambda: self.showData("PlotData"))

        deleteDataAction = QAction('Delete Data from Database', self)
        addMenuTip(deleteDataAction, "Delete Data from the 'Selected Variable' from the Database")
        deleteDataAction.triggered.connect(lambda: self.deleteDataFromDB())

        DisplayLastValAction = QAction('Display Last Values', self)
        addMenuTip(DisplayLastValAction, 'Show a table with the variables and their last value, including scaled value')
        DisplayLastValAction.triggered.connect(lambda: gsup_tools.displayLastValuesWindow())

        CopyVar2VarAction = QAction("Copy One Variable to Another ...", self)
        addMenuTip(CopyVar2VarAction, "Copy one variable to any other")
        CopyVar2VarAction.triggered.connect(self.copyVar2Var)

        # separator

        BoldLinesAction = QAction('Toggle Boldness of all Main Graph Lines', self)
        addMenuTip(BoldLinesAction, 'Changes the boldness of all plotted lines in the main graph')
        BoldLinesAction.triggered.connect(lambda: self.toggleBoldLines())

        ResetLayoutAction = QAction('Reset Window Layout to Default State', self)
        addMenuTip(ResetLayoutAction, 'Sets the layout of the window (position, size) to the state it has by default')
        ResetLayoutAction.triggered.connect(lambda: self.setDefaultLayout())

        FixGarbledAudioAction = QAction("Fix garbled audio", self)
        addMenuTip(FixGarbledAudioAction, 'Fix for a Linux-only PulseAudio bug resulting in garbled audio')
        FixGarbledAudioAction.triggered.connect(lambda: fixGarbledAudio())

        NTPServerAction = QAction("Check Time with 'Network Time Protocol'", self)
        addMenuTip(NTPServerAction, "Comparing computer time with time from 'Network Time Protocol' server")
        NTPServerAction.triggered.connect(lambda: fprintNTPDateTime())


        toolsMenu = self.menubar.addMenu('&Tools')
        toolsMenu.setToolTipsVisible(True)

        toolsMenu.addAction(PlotLogAction)
        toolsMenu.addAction(PlotHisAction)

        toolsMenu.addSeparator()

        toolsMenu.addAction(showSystemInfoAction)
        toolsMenu.addAction(ResetLayoutAction)
        toolsMenu.addAction(NTPServerAction)

        if "LINUX" in platform.platform().upper() and g.RaspiVersion != 5:
            toolsMenu.addAction(FixGarbledAudioAction)

        toolsMenu.addSeparator()

        toolsMenu.addAction(editFormulasAction)
        toolsMenu.addAction(CopyVar2VarAction)
        toolsMenu.addAction(deleteDataAction)
        toolsMenu.addAction(fprintPlotDataAction)
        toolsMenu.addAction(SaveGraph2FileAction)
        toolsMenu.addAction(DisplayLastValAction)
        toolsMenu.addAction(BoldLinesAction)

        toolsMenu.addSeparator()

        toolsMenu.addAction(fprintSuStAction)
        toolsMenu.addAction(showStatsAction)
        toolsMenu.addAction(PlotScatterAction)
        toolsMenu.addAction(PlotPoissonAction)
        toolsMenu.addAction(PlotFFTAction)


#Help Menu
        # menu entries for Help
        self.helpQickStartAction = QAction('Quickstart', self)
        addMenuTip(self.helpQickStartAction, 'Guidance for an easy start')
        self.helpQickStartAction.triggered.connect(self.helpQuickStart)

        self.helpManualUrlAction = QAction('GeigerLog Manual', self)
        addMenuTip(self.helpManualUrlAction, 'Open the GeigerLog Manual (locally if available, or online)')
        self.helpManualUrlAction.triggered.connect(lambda: openManual("GeigerLog-Manual"))

        self.helpGLrelayManualUrlAction = QAction("GeigerLog GLrelay Manual", self)
        addMenuTip(self.helpGLrelayManualUrlAction, "Open the GeigerLog GLrelay Manual")
        self.helpGLrelayManualUrlAction.triggered.connect(lambda: openManual("GeigerLog-GLrelay"))

        self.helpCalibrationGuidanceUrlAction = QAction("GeigerLog Calibration Guidance", self)
        addMenuTip(self.helpCalibrationGuidanceUrlAction, "Open the GeigerLog Calibration Guidance")
        self.helpCalibrationGuidanceUrlAction.triggered.connect(lambda: openManual("GeigerLog-Calibration"))

        self.helpFirmwareBugAction = QAction("Devices' Firmware Bugs", self)
        addMenuTip(self.helpFirmwareBugAction, 'Info on Firmware Bugs of the Devices and Workarounds')
        self.helpFirmwareBugAction.triggered.connect(self.helpFirmwareBugs)

        self.helpWorldMapsAction = QAction('Radiation World Maps', self)
        addMenuTip(self.helpWorldMapsAction, 'Contributing to the Radiation World Maps')
        self.helpWorldMapsAction.triggered.connect(self.helpWorldMaps)

        self.helpOccupationalRadiationAction = QAction('Occupational Radiation Limits', self)
        addMenuTip(self.helpOccupationalRadiationAction, 'Occupational Radiation Limits in USA and Germany')
        self.helpOccupationalRadiationAction.triggered.connect(self.helpOccupationalRadiation)

        self.showCmdLineOptionsAction = QAction('Show Command Line Help', self)
        addMenuTip(self.showCmdLineOptionsAction, 'Show command line options and Commands')
        self.showCmdLineOptionsAction.triggered.connect(self.helpOptions)

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
        helpMenu.addAction(self.helpGLrelayManualUrlAction)
        helpMenu.addAction(self.helpCalibrationGuidanceUrlAction)
        helpMenu.addAction(self.helpFirmwareBugAction)
        helpMenu.addAction(self.helpWorldMapsAction)
        helpMenu.addAction(self.helpOccupationalRadiationAction)
        helpMenu.addAction(self.showCmdLineOptionsAction)

        helpMenu.addSeparator()
        #helpMenu.addAction(self.helpAboutQTAction)
        helpMenu.addAction(self.helpAboutAction)

        # helpMenu.triggered[QAction].connect(self.processtrigger)


# Devel Menu
        if g.devel:
            changeCmdLineOptionsAction = QAction('Change Command Line Options', self)
            addMenuTip(changeCmdLineOptionsAction, 'Allows to change some command line options while running')
            changeCmdLineOptionsAction.triggered.connect(self.changeCmdLineOptions)

            develIotaAction = QAction("Print Vars Status", self)
            develIotaAction.triggered.connect(lambda: printVarsStatus())

            develAlphaAction = QAction("Convolution FFT", self)
            develAlphaAction.triggered.connect(lambda: gstat_convfft.convFFT())

            develBetaAction = QAction("Create Synthetic Data", self)
            develBetaAction.triggered.connect(lambda: gstat_synth.createSyntheticData())

            develGammaAction = QAction("GMC Testing", self)
            develGammaAction.triggered.connect(lambda: gdev_gmc.GMC_TESTING())

            develBipAction = QAction("Play Bip", self)
            develBipAction.triggered.connect(lambda: bip())

            develBurpAction = QAction("Play Burp", self)
            develBurpAction.triggered.connect(lambda: burp())

            develDoubleBipAction = QAction("Play Double-Bip", self)
            develDoubleBipAction.triggered.connect(lambda: doublebip())

            develCocooAction = QAction("Play Cocoo", self)
            develCocooAction.triggered.connect(lambda: cocoo())

            develClickAction = QAction("Play Geiger Click", self)
            develClickAction.triggered.connect(lambda: playGeigerClick())

            develCounterAction = QAction("Play Geiger Counter", self)
            develCounterAction.triggered.connect(lambda: playGeigerCounter())

            develSineAction = QAction("Play Sine Scale", self)
            develSineAction.triggered.connect(lambda: playSineScale())

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

            develCRC8Action = QAction("Show CRC8 result", self)
            develCRC8Action.triggered.connect(lambda: showResultCRC8())

            develColorAction = QAction("Print color codes to Terminal", self)
            develColorAction.triggered.connect(lambda: printColorCodesToTerminal())

            develClearTerminalAction = QAction("Clear the Terminal", self)
            develClearTerminalAction.triggered.connect(lambda: clearTerminal())


            # MonitorAction = QAction('Show Monitor', self)
            # addMenuTip(MonitorAction, 'Show a Monitor ')
            # MonitorAction.triggered.connect(lambda: gsup_tools.plotMonitor())

            # pggraphAction = QAction('Show PgGraph', self)
            # addMenuTip(pggraphAction, 'Show a pg graph comparison ')
            # pggraphAction.triggered.connect(lambda: gsup_tools.plotpgGraph())

            develCPUInfoAction = QAction('Show CPU Info', self)
            addMenuTip(develCPUInfoAction, 'Show CPU Info')
            develCPUInfoAction.triggered.connect(lambda: getAllCPUInfo())


            develMenu = self.menubar.addMenu('D&evel')
            develMenu.setToolTipsVisible(True)

            develMenu.addAction(changeCmdLineOptionsAction)
            develMenu.addSeparator()

            develMenu.addAction(develIotaAction)
            develMenu.addAction(develAlphaAction)
            develMenu.addAction(develBetaAction)
            develMenu.addAction(develGammaAction)
            develMenu.addAction(develBipAction)
            develMenu.addAction(develBurpAction)
            develMenu.addAction(develDoubleBipAction)
            develMenu.addAction(develCocooAction)
            develMenu.addAction(develSineAction)
            develMenu.addAction(develClickAction)
            develMenu.addAction(develCounterAction)
            develMenu.addAction(develCPUInfoAction)

            # develMenu.addAction(SaveRepairLogAction)
            # develMenu.addAction(SaveRepairHisAction)

            if "gdev_audio" in sys.modules:     # only when audio device is activated
                develMenu.addAction(develAudioAction)

            # develMenu.addAction(develLogClickAction)  # inactive
            # develMenu.addAction(MonitorAction)
            # develMenu.addAction(pggraphAction)

            develMenu.addAction(develCRC8Action)
            develMenu.addAction(develColorAction)
            develMenu.addAction(develClearTerminalAction)


# add navigation toolbar as last toolbar
        self.addToolBar(self.navtoolbar)

        # to make a placeholder to the right of navtoolbar, so any
        # navtoolbar's color does not spill into the rest of the menubar
        dummytoolbar = self.addToolBar('')  # empty
        self.addToolBar(dummytoolbar)


# DataOptions
# row Data
        # BigButtonWidth  = 110
        # BigButtonWidth  = 100
        BigButtonWidth  = 95
        col0width       = 70

    # col 0
        # labels and entry fields
        dltitle  = QLabel("Data")
        dltitle.setFont(self.fatfont)
        dlDevice  = QLabel("Device")
        dlDevice.setFont(self.fatfont)

    # col 1
        dbtnPlotLog = QPushButton('Plot Log')
        dbtnPlotLog.setFixedWidth(col0width)
        dbtnPlotLog.setToolTip("Plot the Log File with Default settings")
        dbtnPlotLog.clicked.connect(lambda: self.plotGraph('Log', full=False))

        dbtnPlotHis = QPushButton('Plot Hist')
        dbtnPlotHis.setFixedWidth(col0width)
        dbtnPlotHis.setToolTip("Plot the History File with Default settings")
        dbtnPlotHis.clicked.connect(lambda: self.plotGraph('His', full=False))

    # col 2, 3, 4
        self.dcfLog=QLineEdit()
        self.dcfLog.setReadOnly(True)
        self.dcfLog.setStyleSheet("QLineEdit { background-color: #DFDEDD; color: rgb(80,80,80);}")
        self.dcfLog.setToolTip('The full path of the Log-File if any is loaded')
        font = self.dcfLog.font()
        font.setPointSize(10)
        self.dcfLog.setFont(font)
        # self.dcfLog.setMinimumWidth(400)
        # self.dcfLog.setMaximumWidth(420)

        self.dcfHis=QLineEdit()
        self.dcfHis.setReadOnly(True)
        self.dcfHis.setStyleSheet("QLineEdit { background-color: #DFDEDD; color: rgb(80,80,80); }")
        self.dcfHis.setToolTip('The full path of the History-File if any is loaded')
        font = self.dcfHis.font()
        font.setPointSize(10)
        self.dcfHis.setFont(font)
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
        # DataButtonWidth = BigButtonWidth - 5
        # DataButtonWidth = BigButtonWidth - 10
        # DataButtonWidth = BigButtonWidth + 5
        DataButtonWidth = BigButtonWidth + 5

    # button: clear log file
        self.btnClearLogfile = QPushButton('Clear Log File')
        self.btnClearLogfile.setFixedWidth(DataButtonWidth)
        self.btnClearLogfile.setEnabled(False)
        self.btnClearLogfile.setToolTip('Remove all content from current log file')
        self.btnClearLogfile.setStyleSheet("QPushButton {}")
        self.btnClearLogfile.clicked.connect(lambda: self.clearLogfile())

    # button: add comment
        self.btnAddComment = QPushButton('Add Comment')
        self.btnAddComment.setFixedWidth(DataButtonWidth)
        self.btnAddComment.setEnabled(False)
        self.btnAddComment.setToolTip('Add a comment to current database')
        self.btnAddComment.setStyleSheet("QPushButton {}")
        self.btnAddComment.clicked.connect(lambda: self.addComment("Current"))

    # button: Alarm
        self.btnAlarm = QPushButton('Set Alarm')
        self.btnAlarm.setFixedWidth(DataButtonWidth)
        self.btnAlarm.setToolTip('Current Alarm Settings')
        self.btnAlarm.setStyleSheet("QPushButton {}")
        self.btnAlarm.clicked.connect(lambda: self.setAlarmStatus("list"))

    # button: Log Cycle
        self.btnSetCycle = QPushButton("Set Cycle")
        self.btnSetCycle.setFixedWidth(DataButtonWidth)
        self.btnSetCycle.setToolTip('Setting the LogCycle with current duration in seconds')
        self.btnSetCycle.setStyleSheet("QPushButton {}")
        self.btnSetCycle.clicked.connect(self.setLogCycle)


    # H layout for comment and logcycle
        DataLayout = QHBoxLayout()
        DataLayout.addWidget(self.btnClearLogfile)
        DataLayout.addWidget(self.btnAddComment)
        DataLayout.addWidget(self.btnAlarm)
        DataLayout.addWidget(self.btnSetCycle)

# Row Notepad
        # NPButtonWidth = 65
        # NPButtonWidth = 70
        NPButtonWidth = 65

    # header
        dlnotepad = QLabel("NotePad")
        dlnotepad.setFixedWidth(col0width)
        dlnotepad.setFont(self.fatfont)

    # button: print notepad to printer / pdf
        self.btnPrint2Printer = QPushButton('Print')
        self.btnPrint2Printer.clicked.connect(lambda: self.printNotePad())
        self.btnPrint2Printer.setToolTip("Print Content of NotePad to Printer or  PDF-File")
        self.btnPrint2Printer.setFixedWidth(NPButtonWidth)

    # button: save notepad to file
        self.btnSaveNotePad = QPushButton('Save')
        self.btnSaveNotePad.setToolTip("Save Content of NotePad as Text File named <current filename>.txt")
        self.btnSaveNotePad.setFixedWidth(NPButtonWidth)
        self.btnSaveNotePad.clicked.connect(lambda: self.saveNotePad())

    # button: search notepad
        self.btnSearchNotePad = QPushButton("Search")
        self.btnSearchNotePad.clicked.connect(lambda: self.searchNotePad())
        self.btnSearchNotePad.setToolTip("Search NotePad for Occurence of a Text (Shortcut: CTRL-F)")
        self.btnSearchNotePad.setFixedWidth(NPButtonWidth)

    # button: print plot data
        self.btnPrintPlotData = QPushButton('DataPlt')
        self.btnPrintPlotData.setFixedWidth(NPButtonWidth)
        self.btnPrintPlotData.setToolTip("Print variables as in the current plot to the Notepad")
        self.btnPrintPlotData.clicked.connect(lambda: self.showData("PlotData"))

    # button: print full data to notepad
        self.btnPrintFullData = QPushButton('Data')
        self.btnPrintFullData.clicked.connect(lambda: self.showData(full=True))
        self.btnPrintFullData.setToolTip('Print Full Log or His Data to the NotePad')
        self.btnPrintFullData.setFixedWidth(NPButtonWidth)

    # button: print data excerpt to notepad
        self.btnPrintExceptData = QPushButton('DataExc')
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
        dataOptions.addWidget(dltitle,          row, 0)
        dataOptions.addLayout(DataLayout,       row, 1, 1, 3)
        dataOptions.addWidget(vlinedB0,         row, 4, 3, 1)
        dataOptions.addWidget(dlDevice,         row, 5)

        row = 1 # Plot Log
        dataOptions.addWidget(dbtnPlotLog,      row, 0)
        dataOptions.addWidget(self.dcfLog,      row, 1, 1, 3)
        # col 5 is empty (vline)
        dataOptions.addWidget(self.btnMapping,  row, 5)

        row = 2 # Plot Hist
        dataOptions.addWidget(dbtnPlotHis,      row, 0)
        dataOptions.addWidget(self.dcfHis,      row, 1, 1, 3)
        # col 5 is empty (vline)
        dataOptions.addWidget(self.dtube,       row, 5)

        row = 3 # hline
        dataOptions.addWidget(hlinedB1,         row, 0, 1, 6)

        row = 4 # NotePad
        dataOptions.addWidget(dlnotepad,        row, 0)
        dataOptions.addLayout(NPLayout,         row, 1, 1, 5)

        # group Data Options into Groupbox
        dataOptionsGroup = QGroupBox()
        dataOptionsGroup.setContentsMargins(0,0,0,0)
        dataOptionsGroup.setStyleSheet("QGroupBox {border-style:solid; border-width:1px; border-color:silver;}")
        dataOptionsGroup.setLayout(dataOptions)
        dataOptionsGroup.setFixedHeight(155)  # to match height with graph options (needed here: 143)
        # dataOptionsGroup.setStyleSheet("background-color:%s;" % "#FaFF00") # macht alles gelb


# GraphOptions

        # ltitle  = QLabel("Graph")
        # ltitle.setFont(self.fatfont)

        self.btnGraph = QPushButton('Graph')
        self.btnGraph.setFixedWidth(col0width)
        self.btnGraph.setFont(self.fatfont)
        # self.btnGraph.setToolTip("Activate (gold) or Halt (gray) updating the Graph .")
        self.btnGraph.setToolTip("Updating the Graph is Active (gold) or Halted (gray)")
        self.btnGraph.clicked.connect(lambda: self.toggleGraphAction())
        self.btnGraph.setStyleSheet("QPushButton {background-color:#F4D345; color:rgb(0,0,0);}")  # yellow button bg, black text

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

        btnReset = QPushButton('Reset')
        btnReset.setFixedWidth(col4width)
        btnReset.setToolTip("Reset all Graph Options to Default conditions")
        btnReset.clicked.connect(lambda: self.reset_replotGraph(full=True))

        btnSetScaling = QPushButton('Forml')
        btnSetScaling.setFixedWidth(col4width)
        btnSetScaling.setToolTip("Formula - View and edit current settings for value- and graph-formulas")
        btnSetScaling.clicked.connect(self.editFormulas)

        btnSaveFig = QPushButton('Save')
        btnSaveFig.setFixedWidth(col4width)
        btnSaveFig.setToolTip("Save graph to file")
        btnSaveFig.clicked.connect(saveGraphToFile)

        btnApplyGraph = QPushButton('Apply')
        btnApplyGraph.setFixedWidth(col4width)
        btnApplyGraph.setToolTip("Apply the Graph Options and replot")
        btnApplyGraph.setStyleSheet("background-color: lightblue")
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
        for vname in g.VarsCopy:
            self.select.addItems([vname])

        # The checkboxes to select the displayed variables
        self.varDisplayCheckbox = {}
        for vname in g.VarsCopy:
            vshort = g.VarsCopy[vname][1]
            vlong  = g.VarsCopy[vname][0]

            self.varDisplayCheckbox[vname] = QCheckBox    (vshort)
            self.varDisplayCheckbox[vname].setToolTip     (vlong)
            self.varDisplayCheckbox[vname].setChecked     (False)
            self.varDisplayCheckbox[vname].setEnabled     (False)
            self.varDisplayCheckbox[vname].setTristate    (False)

            # "double lambda needed for closure" WTF???
            self.varDisplayCheckbox[vname].stateChanged.connect((lambda x: lambda: self.changedGraphDisplayCheckboxes(x))(vname))

        self.mavbox = QCheckBox("MvAvg  s:")
        # self.mavbox.setLayoutDirection(Qt.RightToLeft)
        self.mavbox.setLayoutDirection(Qt.LeftToRight)
        self.mavbox.setChecked(g.mavChecked)
        self.mavbox.setMaximumWidth(col6width)
        self.mavbox.setTristate (False)
        self.mavbox.setToolTip('If checked a Moving Average line will be drawn')
        self.mavbox.stateChanged.connect(self.changedGraphOptionsMav)

        self.avgbox = QCheckBox("Avg")
        # self.avgbox.setLayoutDirection(Qt.RightToLeft)
        self.avgbox.setLayoutDirection(Qt.LeftToRight)
        self.avgbox.setMaximumWidth(col6width)
        self.avgbox.setChecked(g.avgChecked)
        self.avgbox.setTristate (False)
        self.avgbox.setToolTip("If checked, Average and ±95% lines will be shown")
        self.avgbox.stateChanged.connect(self.changedGraphOptionsAvg)

    # col 7:
        col7width = 55

        # this starts in col 6 and extends to col 7
        self.labelSelVar = QLabel("---")
        self.labelSelVar.setToolTip("Shows the last value of the Selected Variable when logging\nClick to show all values in separate window")
        self.labelSelVar.setMinimumWidth(col6width + col7width)
        # self.labelSelVar.setFont(QFont('sans', 12, QFont.Bold))
        self.labelSelVar.setFont(QFont('sans', 11, QFont.Bold))
        self.labelSelVar.setStyleSheet('color:darkgray;')
        self.labelSelVar.setAlignment(Qt.AlignCenter)
        self.labelSelVar.mousePressEvent=(lambda x: gsup_tools.displayLastValuesWindow())


        # color select button
        self.btnColorText = "Color of selected variable; click to change it. Current color: "
        self.btnColor     = ClickQLabel('Color')
        self.btnColor       .setAlignment(Qt.AlignCenter)
        self.btnColor       .setMaximumWidth(col7width)
        self.btnColor       .setMinimumWidth(col7width)
        self.btnColor       .setStyleSheet("QLabel { border: 1px solid silver;  border-radius: 3px; }")
        addMenuTip(self.btnColor, self.btnColorText + "None")

        self.mav=QLineEdit()
        self.mav.setMinimumWidth(col7width)
        self.mav.setMaximumWidth(col7width)
        self.mav.setToolTip('Enter the Moving Average smoothing period in seconds')
        self.mav.setText("{:0.0f}".format(g.mav_initial))
        self.mav.textChanged.connect(self.changedGraphOptionsMavText)

        self.fitbox = QCheckBox("LinFit")
        # self.fitbox.setLayoutDirection(Qt.RightToLeft)
        self.fitbox.setLayoutDirection(Qt.LeftToRight)
        self.fitbox.setMaximumWidth(col7width)
        self.fitbox.setChecked(g.fitChecked)
        self.fitbox.setTristate (False)
        self.fitbox.setToolTip("A Linear Regression will be applied to the Selected Variable and shown")
        self.fitbox.stateChanged.connect(self.changedGraphOptionsLinFit)

    # col 9:

        col9width = 50

        # SuSt Button
        btnQuickStats = QPushButton('SuSt')
        btnQuickStats.setFixedWidth(col9width)
        btnQuickStats.setToolTip("Shows Summary Statistics of variables and data as in the current plot.<br><br>To see stats for UNSCALED data hold CTRL while clicking.")
        btnQuickStats.clicked.connect(lambda: gsup_tools.fprintSuSt())

        # Stats Button
        btnPlotStats = QPushButton('Stats')
        btnPlotStats.setFixedWidth(col9width)
        btnPlotStats.setToolTip("Shows Detailed Statistics of variables and data as in the current plot")
        btnPlotStats.clicked.connect(lambda: gsup_tools.showStats())

        # Scatterplot Button
        btnScat = QPushButton('Scat')
        btnScat.setToolTip('Show an X-Y Scatter plot with optional polynomial fit, using data currently selected in the plot')
        btnScat.setFixedWidth(col9width)
        btnScat.clicked.connect(lambda: gsup_tools.selectScatterPlotVars())

        # Poiss Button
        btnPoisson = QPushButton('Poiss')
        btnPoisson.setFixedWidth(col9width)
        btnPoisson.setToolTip("Shows a plot of a Poisson curve on a histogram of the selected variable data as in the current plot")
        btnPoisson.clicked.connect(lambda: gstat_poisson.plotPoisson())

        # FFT Button
        btnFFT = QPushButton('FFT')
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
        for vname in g.VarsCopy:
            layoutH.addWidget(self.varDisplayCheckbox[vname])

    #layout the GraphOptions
        graphOptions=QGridLayout()
        graphOptions.setContentsMargins(5,9,5,5) # spacing around the graph options top=9 is adjusted for fit!

        # STEPPING ORDER ##############################
        # to define the order of stepping through by tab-key
        # row 1 ... 3, col 1 + 2 is put in front
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
        # graphOptions.addWidget(ltitle,        row, 0)
        graphOptions.addWidget(self.btnGraph,   row, 0)
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
        graphOptions.addWidget(self.labelSelVar,row, 6, 1, 2)
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
        # graphOptionsGroup.setStyleSheet("background-color:%s;" % "#FaFF00")
        graphOptionsGroup.setLayout(graphOptions)
        graphOptionsGroup.setFixedHeight(155)  # min height needed

# NotePad
        self.notePad = QTextEdit()
        self.notePad.setReadOnly(True)
        self.notePad.setFont(self.fontstd)
        self.notePad.setLineWrapMode(QTextEdit.NoWrap)          # alt: QTextOption::WordWrap
        self.notePad.setTextColor(QColor(40, 40, 40))
        # self.notePad.setStyleSheet("background-color:%s;" % "#FaFF00")

        g.notePad = self.notePad # pointer used for fprint in utils

# LogPad
        # limit the amount of text stored in the logPad.
        # clear + append is MUCH faster than setText or setPlainText !!! (5000 ms vs 200 ms)
        # Character count: 5 + 8 + 7 * 12 = 97 round up to 100 per line
        # 100char/sec * 3600sec/h = 360 000 per h ==> 1 mio in 2.8h = ~3h
        # 10000 char / 100char/sec ==> 100 sec, ~2min
        # in overnight run the limit was done some 600 times; maximum duration was 0.237 sec!

        self.logPad = QTextEdit()
        self.logPad.setReadOnly(True)
        self.logPad.setFont(self.fontstd)
        self.logPad.setLineWrapMode(QTextEdit.NoWrap)
        self.logPad.setTextColor(QColor(40, 40, 40))
        self.logPad.document().setMaximumBlockCount(3600)  # Limit total output to approx 1 hour: 1 Block = 1 Zeile; at 1 sec cycle -> 3600 per hour

        g.logPad = self.logPad # pointer used for logPrint in utils

# set the layout - left side
        self.splitterPad = QSplitter(Qt.Vertical)
        self.splitterPad.addWidget(self.notePad)
        self.splitterPad.addWidget(self.logPad)
        self.splitterPad.setSizes (g.WinSplit[0:2])
        # self.splitterPad.setContentsMargins(5,0,5,0)  # margins are too big

        layoutLeft = QVBoxLayout()
        layoutLeft.addWidget(dataOptionsGroup)
        layoutLeft.addWidget(self.splitterPad)
        layoutLeft.setContentsMargins(0,0,0,0)
        layoutLeft.setSpacing(0)

# set the layout - right side
        layoutRight = QVBoxLayout()
        layoutRight.addWidget(graphOptionsGroup)
        layoutRight.addWidget(self.canvas)          # add canvas directly, no frame
        layoutRight.setContentsMargins(0,0,0,0)
        layoutRight.setSpacing(0)

# set the layout - both sides
        leftWidget = QWidget()
        leftWidget.setLayout(layoutLeft)

        rightWidget = QWidget()
        rightWidget.setLayout(layoutRight)

        self.splitterBoth = QSplitter(Qt.Horizontal)
        self.splitterBoth.addWidget(leftWidget)
        self.splitterBoth.addWidget(rightWidget)
        self.splitterBoth.setSizes(g.WinSplit[2:])
        self.splitterBoth.setContentsMargins(5,0,5,0)

# Window size, position and Layout
        if g.WinSettingsDefault:
            self.setDefaultLayout()
        else:
            self.setGeometry(*g.WinGeom)

# centralwidget
        self.setCentralWidget(self.splitterBoth)

# timerCheck for running check cycle
        self.timerCheck = QTimer()
        self.timerCheck.timeout.connect(self.runCheckCycle)     # checks various requests
        self.timerCheck.start(5)                                # doc: "Starts or restarts the timer with a timeout interval of msec milliseconds."
                                                                # even at only 1 ms there is no "g.runCheckIsBusy:" printout!?
                                                                # nothing overlaps???


# # timerLoad for running LoadAverage
#         self.timerLoad = QTimer()
#         self.timerLoad.timeout.connect(self.runLoadCycle)       # calls the Load Averages
#         self.timerLoad.start(10000)                             # alle 10 sec doc: "Starts or restarts the timer with a timeout interval of msec milliseconds."


# show
        self.dcfLog.setText(str(g.logFilePath))                 # default is "None" for filepath
        self.dcfHis.setText(str(g.hisFilePath))                 # default is "None" for filepath
        self.showTimingSetting (g.LogCycle)                     # default is 1 (sec)

        self.show()
        if g.window_size == "maximized":   self.showMaximized()

        dprint("Fonts:  App     -",     strFontInfo("", g.app.font()))              # print font info for QApplication
        dprint("Fonts:  menubar -",     strFontInfo("", self.menubar.fontInfo()))
        dprint("Fonts:  logPad  -",     strFontInfo("", self.logPad.fontInfo()))
        dprint("Fonts:  notePad -",     strFontInfo("", self.notePad.fontInfo()))
        dprint("Screen: Dimensions: ",  QDesktopWidget().screenGeometry())          # gives screen dimensions
        dprint("Screen: Available:  ",  QDesktopWidget().availableGeometry())       # gives screen dimensions available

        # NOTE on window sizes:
        # "On X11, a window does not have a frame until the window manager decorates it."
        # see: http://doc.qt.io/qt-4.8/application-windows.html#window-geometry
        # self.geometry(),      : gives windows dimensions but has the frame EXCLUDED!
        # self.frameGeometry()  : gives windows dimensions including frame, but not on X11!
        dprint("Window: Dimensions: ",  self.geometry(),      " w/o Frame")
        dprint("Window: Dimensions: ",  self.frameGeometry(), " WITH Frame (not valid on X11)")

        # copyright message
        message = __copyright__ + ", by " + __author__ + ", License: " + __license__
        self.showStatusMessage(message, timing=0, error=False) # message remains until overwritten by next

        QtUpdate()

        cdprint("Data  Options group: height: {}, width: {}".format(dataOptionsGroup.height(), dataOptionsGroup.width()))
        cdprint("Graph Options group: height: {}, width: {}".format(graphOptionsGroup.height(), graphOptionsGroup.width()))

        dprint(TGREEN + "Starting the GUI is complete " + "-" * 100 + TDEFAULT + "\n")

        # Python problems - wrong version --> EXIT
        if g.python_version  > "":
            self.startupProblems(g.python_version,  closeGL=True)

        # Startup problems --> EXIT
        if g.startupProblems > "":
            self.startupProblems(g.startupProblems, closeGL=True)

        if g.importProblem > "":
            self.startupProblems(g.importProblem, closeGL=False)

        # Config problems --> Continue
        if g.configAlerts > "":
            msg  = g.configAlerts.replace("\n", "<br>")
            self.startupProblems(msg,  closeGL=False)
            g.configAlerts = ""

        # at least one activated device?  if not warn but continue
        ### local def #########################################
        def isAnyDeviceActive():
            for DevName in g.Devices:
                if g.Devices[DevName][g.ACTIV]: return True
            return False
        ### end local def #####################################
        if not isAnyDeviceActive():
            dprint("No Devices are Activated !")
            self.warnMissingDeviceActivations()

        # MonServer autostart
        if g.MonServerAutostart:
            gweb_monserv.initMonServer(force=True)
            # time.sleep(1)


        # # Telegram activation
        # if g.TelegramActivation:
        #     gsup_telegram.initTelegram(force=True)
        #     self.TelegramAction.setIcon(QIcon(QPixmap(os.path.join(g.resDir, 'icon_Telegram.png'))))


        ##
        ## GeigerLog autostart
        ##
        # make autoLogPath
        autoLogPath = os.path.join(g.dataDir, g.autoLogFile)

        # rdprint(defname, "autoDevConnect: ", g.autoDevConnect)
        # rdprint(defname, "autoLogLoad:    ", g.autoLogLoad)
        # rdprint(defname, "autoLogStart:   ", g.autoLogStart)
        # rdprint(defname, "autoQuickStart: ", g.autoQuickStart)

        # rdprint(defname, "g.dataDir:      ", g.dataDir)
        # rdprint(defname, "g.autoLogFile:  ", g.autoLogFile)
        # rdprint(defname, "autoLogPath:    ", autoLogPath)

        if g.autoQuickStart or g.autoLogStart or g.autoDevConnect or g.autoLogLoad:
            fprint(header("Auto-Starting"))
            if g.autoQuickStart:
                # quickstart - takes precedence
                fprint("Doing Quick Log")
                self.switchAllDeviceConnections(new_connection = "ON")
                self.quickLog()
            else:
                if g.autoLogStart:
                    # autoLogStart
                    fprint("Starting Logging with Last-Loaded Database")
                    QtUpdate()
                    self.switchAllDeviceConnections(new_connection = "ON")
                    self.getFileLog(defaultLogDBPath=autoLogPath)
                    self.startLogging()
                else:
                    # want auto Connect and/or auto Load?
                    if g.autoDevConnect:    fprint("Auto-Connecting")
                    if g.autoLogLoad:       fprint("Auto-Loading Last-Loaded Database")
                    QtUpdate()
                    if g.autoDevConnect:    self.switchAllDeviceConnections(new_connection = "ON")
                    if g.autoLogLoad:       self.getFileLog(defaultLogDBPath=autoLogPath)


        signal.signal(signal.SIGTERM,  self.forceClose)
        signal.signal(signal.SIGINT,   self.forceClose)
        if not "WINDOWS" in platform.platform().upper(): signal.signal(signal.SIGQUIT,  printSysInfo) # SIGQUIT (CTRL+\) to show SystemInfo in terminal

        self.setAlarmStatus("start")

        dprint(TGREEN + "GeigerLog is initiated " + "-" * 100 + TDEFAULT + "\n")


#========== END __init__ ======================================================
#
#========== BEGIN Class Functions =============================================

    # from email: John Thornton <dev@gnipsel.com> to: pyqt@riverbankcomputing.com from: 13.12.2023, 22:54
    def excepthook(self, exc_type, exc_value, tb):
        # extract the stack summary
        summary = traceback.extract_tb(tb)
        for frame_summary in summary:
            filename = frame_summary.filename
            frame_summary.filename = os.path.relpath(filename)

        # rebuild the traceback and build the error message
        # msg = f'Mesact Version: {VERSION} Build Date: {BUILD_DATE}\n'
        # msg += ''.join(traceback.format_list(StackSummary.from_list(summary)))
        msg  = ""
        msg += ''.join(traceback.format_list(summary))
        msg += f'{exc_type.__name__}\n'
        msg += f'{exc_value}\n'
        msg += 'Please file an issue at\n'
        msg += 'https://github.com/jethornton/mesact/issues'
        print(msg)
        # dialogs.errorMsgOk(msg, 'PROGRAM ERROR' )
        error_dialog = QErrorMessage()
        error_dialog.showMessage(msg)


    def deleteDataFromDB(self):
        """Delete data from Selected Variable in range selected in Graph"""

        defname = "deleteDataFromDB: "
        dprint(defname)
        setIndent(1)

        if g.logTimeSlice is None:
            msg = "No data available"
            g.exgg.showStatusMessage(msg)
            vprint(defname, msg)
            setIndent(0)
            return

        selectedVar = getNameSelectedVar()
        leftdate    = str(mpld.num2date(g.logTimeSlice[0],            tz=None))[0:19]
        rightdate   = str(mpld.num2date(g.logTimeSlice[-1] + 1/86400, tz=None))[0:19]       # add  1sec

        vprint(defname, "Database: '{}' variable: '{}'".format(g.currentDBPath, selectedVar))
        vprint(defname, "tmin ", leftdate, "  tmax ", rightdate)

        retval = 1024
        # Issue Warning message when more than 100 are selected for deletion
        if len(g.logTimeSlice) > 100:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Warning)
            msg.setText("You have selected to delete {:n} data points. Are you sure? \nPress Ok to continue, or Cancel.".format(len(g.logTimeSlice)))
            msg.setWindowTitle("WARNING")
            msg.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
            retval = msg.exec_()

        if retval == 1024:
            setBusyCursor()

            linfo     = QLabel("These data will be deleted from database:\n'{}'\n".format(g.currentDBPath))
            lreminder = QLabel("\nModified data will be visible in the Graph only after you reload the database!")

            labout = QTextBrowser()
            labout.setFont(g.fontstd)
            labout.setLineWrapMode(QTextEdit.NoWrap)
            labout.setTextInteractionFlags(Qt.LinksAccessibleByMouse|Qt.TextSelectableByMouse)
            labout.setMinimumHeight(300)

            for i, dt in enumerate(g.logTimeSlice):
                datetime = str(mpld.num2date(dt, tz=None))[0:19]
                value    = g.logSlice[selectedVar][i]
                labout.append("{:<4d} : {}   {}   {}".format(i + 1, selectedVar, datetime, value))

            d = QDialog()
            # d.setWindowIcon(g.iconGeigerLog)  # GL icon kommt trotzdem, warum???
            d.setWindowTitle("Delete Variable Values from Database")
            d.setWindowModality(Qt.WindowModal)          # multiple windows open, all runs, all is clickable
            d.setMinimumWidth(400)

            bbox = QDialogButtonBox()
            bbox.setStandardButtons(QDialogButtonBox.Cancel | QDialogButtonBox.Ok )
            bbox.accepted.connect(lambda: d.done(100)) # ESC key produces 0 (zero)!
            bbox.rejected.connect(lambda: d.done(0))

            layoutV = QVBoxLayout(d)
            layoutV.addWidget(linfo)
            layoutV.addWidget(labout)
            layoutV.addWidget(lreminder)
            layoutV.addWidget(bbox)

            setNormalCursor()
            retval = d.exec()

            if retval == 100:
                # do deletion
                # # sql database
                #   currentConn          =                # connection to CURRENT database
                #   logConn              =                # connection to LOGGING database
                #   hisConn              =                # connection to HISTORY database
                dprint(defname, "Deleting ", g.currentConn, selectedVar, leftdate, rightdate)
                gsup_sql.DB_setValuesToNull(g.currentConn, selectedVar, leftdate, rightdate)
            else:
                # cancel deletion
                vprint(defname, "Database variable deletion cancelled")

        else:
            vprint(defname, "Database variable deletion cancelled")

        setIndent(0)


    def toggleGraphAction(self):
        """toggles the Graph for updating or Halting"""

        newGraphAction = not g.GraphAction

        if newGraphAction == False:
            # Graph updating to be HALTED
            stylesheetcode = "QPushButton {}"                                            # std grey button bg
            gsup_plot.makePlot(halt=True)                                                # must run before g.GraphAction == False
        else:
            # Graph updating to be resumed
            stylesheetcode = "QPushButton {background-color:#F4D345; color:rgb(0,0,0);}" # yellow button bg, black text

        g.GraphAction = newGraphAction
        self.applyGraphOptions()

        self.btnGraph.setStyleSheet(stylesheetcode)


    def toggleBoldLines(self):
        """toggles the boldness of the line in the main graph"""

        g.graphbold    = not g.graphbold


    def setDefaultLayout(self):
        """Set the Default startup layout conditions"""

        defname = "setDefaultLayout: "

        screen_available = QDesktopWidget().availableGeometry()
        # rdprint(defname, "screen_available: ", screen_available)
        # rdprint(defname, "g.window_width: ", g.window_width, "   g.window_height: ", g.window_height)

        sw   = min(g.window_width  - 2,      screen_available.width() )     # Frame of 1 pixel left and right
        sh   = min(g.window_height - 2 - 22, screen_available.height())     # Frame top + bottom + Window bar

        xpos = max(screen_available.width() - sw, 0)                        # should be >0 anyway
        ypos = screen_available.y()                                         # the upper end of the screen
        # rdprint(defname, "xpos:{}  ypos:{}  sw: {}  sh:{} platform.platform().upper(): '{}'".format(xpos, ypos, sw, sh, platform.platform().upper()))

        # ypos corrections
        if   "AARCH64" in platform.platform().upper():
            ypos += 28           # some correction needed at least on Raspi64 (still aarch64 on Raspi 5)
            xpos -= 26           # strangely, needed even for x with Raspi 5 on X11
        elif "WINDOWS" in platform.platform().upper(): ypos += 33           # some correction needed at least on Virtual Win8.1
        elif "ARMV"    in platform.platform().upper(): ypos += 33           # some correction needed at least on Manu 4
        elif "LINUX"   in platform.platform().upper(): ypos += 1            # just to make it visible
        # fprint("platform.platform().upper(): ", platform.platform().upper())

        # set main window position and size
        self.setGeometry(xpos, ypos, sw, sh)                                # position window in upper right corner of screen
        rdprint(defname, "xpos:{}  ypos:{}  sw: {}  sh:{} platform.platform().upper(): '{}'".format(xpos, ypos, sw, sh, platform.platform().upper()))

        # set splitter divisions
        self.splitterPad.setSizes  (g.WinSplitDefault[:2])
        self.splitterBoth.setSizes (g.WinSplitDefault[2:])

        # reset Display Last Values window to default position and size
        g.displayLastValsGeom  = ("", "", "", "")
        if g.dispLastValsWinPtr is not None: g.dispLastValsWinPtr.done(0)


    def paintEvent(self, event):
        """the window was painted for whatever reason"""

        defname = "paintEvent: "

        g.NewWinGeom  = [self.geometry().x(), self.geometry().y(), self.geometry().width(), self.geometry().height()]   # type list
        g.NewWinSplit = self.splitterPad.sizes() + self.splitterBoth.sizes()                                            # type list

        # mdprint(defname, " event.type(): ", event.type(), "  split: ", g.NewWinSplit)
        # mdprint(defname, " event.type(): ", event.type(), "  geom:  ", g.NewWinGeom)

        g.SettingsNeedSaving = True


    # error: self.splitterPad anstelle von self geht nicht
    # def resizeEvent(self.splitterPad, event):
    #     """the window was resized and may have been moved"""

    #     defname = "resizeEvent: "

    #     g.NewWinGeom = [self.geometry().x(), self.geometry().y(), self.geometry().width(), self.geometry().height()]
    #     rdprint(defname, "event.type(): ", event.type(), "  Geom: ", g.NewWinGeom)

    #     g.SettingsNeedSaving = True


    # def resizeEvent(self, event):
    #     """the window was resized and may have been moved"""

    #     defname = "resizeEvent: "

    #     g.NewWinGeom = [self.geometry().x(), self.geometry().y(), self.geometry().width(), self.geometry().height()]
    #     # rdprint(defname, "event.type(): ", event.type(), "  Geom: ", g.NewWinGeom)

    #     g.SettingsNeedSaving = True


    # def moveEvent(self, event):
    #     """the window was moved but not changed in size"""

    #     defname = "moveEvent: "

    #     g.NewWinGeom = [self.geometry().x(), self.geometry().y(), self.geometry().width(), self.geometry().height()]
    #     # cdprint(defname, "  event.type(): ", event.type(), " pos: Geom: ", g.NewWinGeom)

    #     g.SettingsNeedSaving = True


    def processtrigger(self, q):
        """Demo for processtrigger"""

        rdprint("'{}' was triggered".format(q.text()))


    def updateProgressbar(self):
        """refresh position of progressbar"""
        # duration : avg: 0.070 ms (min: 0.009 ... 0.167 ms)

        # t0 = time.time()
        defname = "updateProgressbar: "

        # ### ???? is this the cause of Segmentation faults????
        # return # switching off the progress bar

        if np.isnan(g.LogCycleStart) : dprog = 0
        else:                          dprog = 100 * (time.time() - g.LogCycleStart) / g.LogCycle
        prog = int(np.ceil(dprog)) if dprog < 95 else 100

        if g.logging: self.btnProgress.setValue(prog)
        else:         self.btnProgress.setValue(0)


#rcc
    #############################################################################################################
    def runLoadCycle(self):
        """triggered by timerLoad"""

        defname = "runLoadCycle: "
        if g.logging:
            cpucount = psutil.cpu_count()
            lavg     = psutil.getloadavg()
            l1  = lavg[0] / cpucount * 100            #    % CPU Load Avg  --> 0-->over last 1 min
            l5  = lavg[1] / cpucount * 100            #    % CPU Load Avg  --> 1-->over last 5 min
            l15 = lavg[2] / cpucount * 100            #    % CPU Load Avg  --> 2-->over last 15 min
            rdprint(defname, "CPU count: {}  Load Average: Last1min: {:<0.1f}%  Last5min: {:<0.1f}%  Last15min: {:<0.1f}%".format(cpucount, l1, l5, l15))


    def runCheckCycle(self):
        """triggered by timerCheck"""

        defname = "runCheckCycle: "

        if g.runCheckIsBusy :
            rdprint(defname, "g.runCheckIsBusy: ", g.runCheckIsBusy, "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx")

        g.runCheckIsBusy = True
        msgfmt           = "{:<14s}{:7.2f}   "
        idleloop         = 0                        # passing the loop without doing anything
        rCCstart         = time.time()              # excluding progressbar from duration

        self.updateProgressbar()                    # i.e. wird jeden checkcycle start updated!


    # update DB
        if len(g.SaveLogValuesQueue) > 0:
            while len(g.SaveLogValuesQueue) > 0:

                datalist = g.SaveLogValuesQueue.popleft()

                # Write to database file
                gsup_sql.DB_insertData(g.logConn, [datalist])

            duration = 1000 * (time.time() - rCCstart)
            msg      = msgfmt.format("update DB:", duration)
            cdlogprint(defname + msg, duration=duration)


    # update mem
        elif len(g.MemDataQueue) > 0:
            while len(g.MemDataQueue) > 0:
                # upload to mem as long there is something in the queue
                datalist = g.MemDataQueue.popleft()
                # rdprint(defname, "datalist: ", datalist)

                try:
                    # update options for np.array:
                    # g.logDBData = np.append      ( g.logDBData, [datalist],  axis=0)          # duration:  47.4 (16 ...  97) ms
                    # g.logDBData = np.vstack      ((g.logDBData, [datalist])        )          # duration:  42.7 (14 ... 103) ms
                    # g.logDBData = np.concatenate ((g.logDBData, [datalist]), axis=0)          # duration:  28.5 (15 ...  98) ms - using  ~500 records

                    g.logDBData = np.concatenate   ((g.logDBData, [datalist]), axis=0)          # duration:  19.6 (13 ...  99) ms - using 54520 records
                except Exception as e:
                    exceptPrint(e, defname)
                    efprint(longstime() + " " + defname + str(e))

            duration = 1000 * (time.time() - rCCstart)
            msg      = msgfmt.format("update Mem:", duration)
            g.DurUpdate["MEM"] = duration
            cdlogprint(defname + msg, duration=duration)

            # if g.devel and duration > 500: efprint("DVL {} {} ms {}".format(longstime(), msg, " - long duration"))
            if g.devel and duration > 500: efprint("{} {} ms {}".format(longstime(), msg, " - long duration"))

            # make graphupdate in next pass
            g.needGraphUpdate = True   # the only place where this is set to True


    # update LogPad
        elif len(g.LogPadQueue) > 0:
            LogPadStart = time.time()
            while len(g.LogPadQueue) > 0:
                msgLogPad, logValues   = g.LogPadQueue.popleft()
                # rdprint(defname, "msgLogPad: ", msgLogPad, "  logvalues: ", logValues)

                # extract values for all variables
                g.LogHeaderText = "Time         "
                for i, vname in enumerate(g.VarsCopy):
                    val  = logValues[vname]
                    if val is None or np.isnan(val):
                        sval = " {:<3s}".format(".")
                    else:
                        if  i < 8 and (isinstance(val, int) or val.is_integer()):  decs = 0  # integer value - do only with CPX variables
                        else:                                                      decs = 3  # T, P, H, X always with 3 decs
                        sval = " {:<3s}".format(customformat(val, 9, decs, thousand=False))

                    msgLogPad += sval
                    g.LogHeaderText += "{}".format(g.logHeaderTitle[i]) + " " * (max(1, (len(sval) - 2)))

                logPrint(msgLogPad, clear=g.lastLogLineClear)           # print the LogPad msg; clear the header first if "clear"
                logPrint(g.LogHeaderText)                               # print the header at the bottom of LogPad
                g.lastLogLineClear = True                               # signals to next logPrint that last line must be deleted first

                duration = 1000 * (time.time() - LogPadStart)
                msg      = msgfmt.format("update LogPad:", duration)
                # msg     += "Log: " + msgLogPad
                cdlogprint(defname + msg, duration=duration)
                # rdprint(msg)

                g.SnapRecord = msgLogPad                                # saving in case it was called by snaprecord


    # update Displays
        elif g.needDisplayUpdate :
            g.needDisplayUpdate = False

        # update Selected Variable
            uDstart = time.time()
            self.updateDisplaySelectedVariable()
            durationSV = 1000 * (time.time() - uDstart)
            # msg         = msgfmt.format("update DspSV:", duration)
            # cdlogprint(defname + msg, duration=duration)

        # uodate Last Values Window
            uDstart = time.time()
            self.updateDisplayLastValuesWindow()
            durationLVW = 1000 * (time.time() - uDstart)

        # print summary
            msg         = msgfmt.format("update Disp:", durationSV + durationLVW) + "Selected Var: {:0.2f} ms  Last-Values Window: {:0.2f} ms".format(durationSV, durationLVW)
            cdlogprint(defname + msg, duration=durationSV + durationLVW, force=True)


    # update graph
        # plot the log data but only if Log (and not His) is displayed
        elif g.needGraphUpdate:

            graphstart = time.time()
            g.needGraphUpdate = False

            if g.activeDataSource == "Log":
                # displaying Log
                g.currentDBData = g.logDBData           # make the log data current!
                makePlotMsg     = gsup_plot.makePlot()  # direct plot; slightly quicker than plotGraph
            else:
                # displaying His
                makePlotMsg     = "No graph update; His is displayed"

            duration = 1000 * (time.time() - graphstart)

            g.DurUpdate["GRAPH"]  = duration
            msg       = msgfmt.format("update Graph:", g.DurUpdate["GRAPH"]) + makePlotMsg
            cdlogprint(defname + msg, duration=duration, force=True)


        # print memory usage message after graph and only on devel
            # duration is 6 ... 10 ms
            # to limit frequency do this only after graph update
            if g.devel:
                memstart = time.time()
                memused  = getMemoryUsed("MB")

                duration = 1000 * (time.time() - memstart)
                msg      = msgfmt.format("Memory Useage:", duration) + "Mem used: {:4.1f} MB"  .format(memused)
                cdlogprint(defname + msg, duration=duration, force=True)

#aaa
        # alarm check
            # to limit frequency do this only after graph update
            if g.AlarmActivation:                                   # this is the activation in the config file
                astart = time.time()

                if g.LogReadings >= g.AlarmIdleCycles:
                    if g.AlarmQueues != g.LastAlarmQueues:          # prevent double reporting if the Queue hasn't changed
                        AlarmMsg      = ""
                        g.AlarmMsgAll = ""
                        alarminfo     = ""
                        for vname in g.AlarmQueues:
                            # rdprint(defname, "AlarmLimits[{:6s}]:  {}".format(vname, g.AlarmLimits[vname]))
                            if g.AlarmLimits[vname] is not None:
                                AlarmN, AlarmLower, AlarmUpper = g.AlarmLimits[vname]

                                aqlist    = list(g.AlarmQueues[vname])[-AlarmN:]
                                lenaqlist = len(aqlist)
                                if lenaqlist > 0: value = sum(aqlist) / lenaqlist
                                else:             value = g.NAN
                                mdprint(defname, "AlarmQueues: '{}' avg:{:0.5g}  len:{}  Queue:{}".format(vname, value, len(aqlist), aqlist))

                                if   AlarmUpper is not None and value > AlarmUpper:
                                    alarm = "HI-ALARM"
                                    almsg = "is {:0.3f} above {}".format(value - AlarmUpper, AlarmUpper)
                                elif AlarmLower is not None and value < AlarmLower:
                                    alarm = "LO-ALARM"
                                    almsg = "is {:0.3f} below {}".format(abs(value - AlarmLower), AlarmLower)
                                else:
                                    alarm = ""
                                    almsg = ""

                                if alarm > "":
                                    AlarmMsg += "{} {}  {}={:>8s} {}".format(alarm, stime(), vname, customformat(value, 6, 3, thousand=False), almsg)


                            if AlarmMsg > "":
                                qefprint(AlarmMsg)

                                # sound alarm
                                if g.AlarmSound: soundAlarm()

                                # requesting email
                                if g.emailUsage: g.emailRequested = True

                                g.AlarmMsgAll += AlarmMsg + "\n"
                                AlarmMsg       = ""

                        g.LastAlarmQueues = copy.deepcopy(g.AlarmQueues)

                    else:
                        # queue has not changed; no further processing
                        alarminfo = "Alarm records have not changed"

                else:
                    alarminfo = "No Checking during Startup-Idle-Cycles"

                duration = 1000 * (time.time() - astart)
                msg      = msgfmt.format("check Alarm:", duration) + (alarminfo if g.AlarmMsgAll == "" else g.AlarmMsgAll)
                cdlogprint(defname + msg, duration=duration, force=True)


    # efprint thread message
        # cannot fprint directly when origin is in different thread (e.g. MiniMon)
        # so must use queue and print here
        elif len(g.qefprintMsgQueue) > 0:
            while len(g.qefprintMsgQueue) > 0:
                getmsg = g.qefprintMsgQueue.popleft()
                if getmsg.startswith("red"): qefprint(getmsg[3:])
                else:                        fprint  (getmsg)


    # play thread sound
        # cannot play sound in threads
        elif len(g.SoundMsgQueue) > 0:
            while len(g.SoundMsgQueue) > 0:
                playSndClip(g.SoundMsgQueue.popleft())


    ### Begin Web stuff #####################################################

    # check for start-flag from web
        elif g.startflag:
            g.startflag = False
            if not g.logging: self.startLogging()


    # check for stop-flag from web
        elif g.stopflag:
            g.stopflag = False
            if g.logging:     self.stopLogging()


    # check for quick-flag from web
        elif g.quickflag:
            g.quickflag = False
            if not g.logging: self.quickLog()


    # send email on alarm
        elif g.emailRequested:
            # rdprint(defname, f"##TESTING##  email is requested for messages: '{g.AlarmMsgAll}'", )
            emailstart   = time.time()
            g.emailRequested = False

            success, ee = gsup_tools.handleEmail("Alarm Message from GeigerLog", g.AlarmMsgAll)
            duration = 1000 * (time.time() - rCCstart)

            if success: pass #gdprint(defname, "Alarm Email was sent successfully in {:0.1f} ms".format(duration))
            else:       edprint(defname, "FAILURE sending Alarm Email: '{}' in {:0.1f} ms".format(ee, duration))

            duration = 1000 * (time.time() - emailstart)
            msg      = msgfmt.format("send email:", duration)
            cdlogprint(defname + msg, duration=duration)


    # # alarm update Telegram Messenger
    #     elif g.TelegramAlarm:
    #         tgalarmstart       = time.time()
    #         g.TelegramAlarm    = False
    #         g.TelegramNeedsPic = True

    #         success = gsup_telegram.sendTextToMessenger(g.AlarmMsg)
    #         duration = 1000 * (time.time() - rCCstart)

    #         if success: pass    # gdprint(defname, "Telegram updated with Alarm Message in {:0.0f} ms".format(duration))
    #         else:       edprint(defname, "FAILURE updating Telegram with Alarm Message in {:0.0f} ms".format(duration))

    #         duration = 1000 * (time.time() - tgalarmstart)
    #         msg      = msgfmt.format("send Tgram A:", duration)
    #         cdlogprint(defname + msg, duration=duration)


    # # update Telegram Messenger with cyclic message, request graph
    #     elif g.TelegramUpdate:
    #         tgmsgstart         = time.time()
    #         g.TelegramUpdate   = False
    #         g.TelegramNeedsPic = True

    #         text  = "Cycle Message - Update Cycle: {} sec\n".format(g.TelegramUpdateCycle)
    #         text += "by Computer: {} {} {}".format(g.CPU_Model, platform.node(), socket.gethostname())
    #         success  = gsup_telegram.sendTextToMessenger(text=text, parse_mode = "HTML")

    #         if success: pass # gdprint(defname, "Telegram updated with Cycle Message")
    #         else:       edprint(defname, "FAILURE updating Telegram with Cycle Message")

    #         duration = 1000 * (time.time() - tgmsgstart)
    #         msg      = msgfmt.format("send Tgram M:", duration)
    #         cdlogprint(defname + msg, duration=duration)


    # # graph + data update Telegram Messenger
    #     elif g.TelegramPicIsReady:
    #         tgpicstart = time.time()
    #         g.TelegramPicIsReady = False

    #         # graph
    #         success = gsup_telegram.sendGraphToMessenger()

    #         if success: pass #gdprint(defname, "Telegram updated with Graph Message")
    #         else:       edprint(defname, "FAILURE updating Telegram with Graph Message")

    #         # data
    #         success = gsup_telegram.sendDataToMessenger()

    #         if success: pass #gdprint(defname, "Telegram updated with Data  Message")
    #         else:       edprint(defname, "FAILURE updating Telegram with Data Message")

    #         duration = 1000 * (time.time() - tgpicstart)
    #         msg      = msgfmt.format("send Tgram GD:", duration)
    #         cdlogprint(defname + msg, duration=duration)


    # # request Telegramupdate
    #     elif g.TelegramActivation and (rCCstart - g.TelegramLastUpdate) > g.TelegramUpdateCycle:
    #         g.TelegramUpdate     = True
    #         g.TelegramLastUpdate = rCCstart


    # need updating RadWorldMap
        elif g.RWMmapActivation   and (rCCstart - g.RWMmapLastUpdate) > (g.RWMmapUpdateCycle * 60):
            rwmapstart = time.time()
            g.RWMmapLastUpdate = rCCstart
            gweb_radworld.updateRadWorldMap()

            duration = 1000 * (time.time() - rwmapstart)
            msg      = msgfmt.format("update RadWorldMap:", duration)
            cdlogprint(defname + msg, duration=duration)

    ### end web stuff ####################################################


    # update the Settings file
        elif g.SettingsNeedSaving:
            settingstart = time.time()
            writeSettingsFile()
            duration = 1000 * (time.time() - settingstart)
            if duration > 1:
                msg      = msgfmt.format("update Settng file: {:0.3f} ms", duration)
                cdlogprint(defname + msg, duration=duration)


    # do this when nothing else was needed
        else:
            # check for zipping need
            zipstart = time.time()
            zipped   = appendToZipArchive()
            if zipped:
                duration = 1000 * (time.time() - zipstart)
                msg      = msgfmt.format("update Zip:", duration) + "   LimitFileSize: {:,.0f}".format(g.LimitFileSize)
                cdlogprint(defname + msg, duration=duration, force=True)
            else:
                idleloop += 1

    ######## end of if - elif - else

        if idleloop > 0:
            g.durCheckIdle     += 1000 * (time.time() - rCCstart)
            g.countCheckIdle   += 1
        else:
            g.durCheckActive   += 1000 * (time.time() - rCCstart)
            g.countCheckActive += 1

        g.runCheckIsBusy = False

    ##### End runCheckCycle(self): #############################################################################
#rcc


    def getAllLogValues(self):
        """Reads all variables from all activated devices and returns as logValues dict"""

        # logValues is dict, always ordered, like:
        # {'CPM':93.0,'CPS':2.0,'CPM1st':45,'CPS1st':3,'CPM2nd':0,'CPS2nd':0,'CPM3rd':nan,'CPS3rd':nan,'Temp':3.0,'Press':4.0,'Humid':5.0,'Xtra':12}

        defname = "getAllLogValues: "

        # # header is:
        # # Cycle #318 .............. Dur[ms]   CPM       CPS       CPM1st    CPS1st    CPM2nd    CPS2nd    CPM3rd    CPS3rd    Temp      Press     Humid     Xtra
        # vprint(getLoggedValuesHeader())

        # set all logValues items to NAN
        logValues = {}
        for vname in g.VarsCopy:
            logValues[vname] = g.NAN   # NAN is needed later for testing

        # fetch the new values for each device (if connected)
        #    g.Devices keys: "GMC", "Audio", "RadMon", "AmbioMon", "GammaScout", "I2C", "LabJack", "MiniMon", ...
        #    e.g.: g.Devices['GMC']   [g.VNAMES] : ['CPM', 'CPS']              # note: g.VNAMES == 1
        #    e.g.: g.Devices['RadMon'][g.VNAMES] : ['T', 'P', 'H', 'X']
        for DevName in g.Devices:
            if g.Devices[DevName][g.CONN]: # look only at connected devices; # Connection status: CONN = 3
                devvars = g.Devices[DevName][g.VNAMES]    #  e.g. == ['CPM', 'T', 'X']
                if   DevName == "GMC"         : logValues.update(gdev_gmc         .getValuesGMC        (devvars))
                elif DevName == "Audio"       : logValues.update(gdev_audio       .getValuesAudio      (devvars))
                elif DevName == "IoT"         : logValues.update(gdev_iot         .getValuesIoT        (devvars))
                elif DevName == "RadMon"      : logValues.update(gdev_radmon      .getValuesRadMon     (devvars))
                elif DevName == "AmbioMon"    : logValues.update(gdev_ambiomon    .getValuesAmbioMon   (devvars))
                elif DevName == "GammaScout"  : logValues.update(gdev_gammascout  .getValuesGammaScout (devvars))

                elif DevName == "I2C"         : logValues.update(gdev_i2c         .getValuesI2C        (devvars))
                elif DevName == "LabJack"     : logValues.update(gdev_labjack     .getValuesLabJack    (devvars))
                elif DevName == "MiniMon"     : logValues.update(gdev_minimon     .getValuesMiniMon    (devvars))
                elif DevName == "Formula"     : logValues.update(gdev_formula     .getValuesFormula    (devvars))

                elif DevName == "WiFiClient"  : logValues.update(gdev_wificlient  .getValuesWiFiClient (devvars))
                elif DevName == "WiFiServer"  : logValues.update(gdev_wifiserver  .getValuesWiFiSrvAll (devvars))

                elif DevName == "RaspiI2C"    : logValues.update(gdev_raspii2c    .getValuesRaspiI2C   (devvars))
                elif DevName == "RaspiPulse"  : logValues.update(gdev_raspipulse  .getValuesRaspiPulse (devvars))

                elif DevName == "SerialPulse" : logValues.update(gdev_serialpulse .getValuesSerialPulse(devvars))

                elif DevName == "Manu"        : logValues.update(gdev_manu        .getValuesManu       (devvars))
                elif DevName == "RadPro"      : logValues.update(gdev_radpro      .getValuesRadPro     (devvars))

        # cdprint(defname, "logValues: ", logValues)
        return logValues


    def snapLogValue(self):
        """Take an out-of-order measurement (like when toolbar icon Snap is clicked)"""

        if not g.logging: return

        defname = "snapLogValue: "

        vprint(defname)
        setIndent(1)

        runLogCycle() # do an extra logging cycle

        fprint(header("Snapped Log Record"))
        fprint(g.LogHeaderText)
        fprint(g.SnapRecord)
        dprint(defname + g.SnapRecord)

        # send comment to the DB
        ctype       = "COMMENT"
        cJulianday  = getTimeJulian()
        cinfo       = "Snapped log record: '{}'".format(g.SnapRecord)
        gsup_sql.DB_insertComments(g.logConn, [[ctype, cJulianday, cinfo]])

        setIndent(0)


    def toggleLogClick(self):
        """toggle making a click at avery log cycle"""

        g.LogClickSound = not g.LogClickSound
        fprint(header("Toggle Log Click"))
        fprint("Toggle Log Click", "is ON" if g.LogClickSound else "is OFF")


    def flashCycleButton(self, mode):
        """make LogCycle button yellow during a log call, and grey otherwise"""

        # t0 = time.time()
        defname = "flashCycleButton: "

        if mode == "On":
            stylesheetcode = "QPushButton {font-size:12px; background-color:#F4D345; color:rgb(0,0,0);}" # yellow button bg, black text
            g.logCycleBtnTimeOn  = time.time()
        else:
            stylesheetcode = "QPushButton {font-size:12px;}"                                            # std grey button bg
            g.LogCycleStart = time.time()

        self.btnSetCycle.setStyleSheet(stylesheetcode)

        # t1 = time.time()
        # rdprint(defname, "duration: {:0.3f} ms".format(1000 * (t1 - t0)))


    def warnMissingDeviceActivations(self):
        """Warning on no-Devices-activated"""

        message  = "<b>You have not activated any devices!</b><br><br>\
                    You can work on existing data from Log or History loaded from database or CSV file,\
                    but you cannot create new data, neither by Logging nor by History download from device, until a device is activated.\
                    <br><br>Devices are activated in GeigerLog's configuration file <b>geigerlog.cfg</b>, which you find in GeigerLog's \
                    'gconfig' directory.\
                    <br><br>Search in the file for the word <b>DEVICES</b>, then scroll down to find your \
                    device <b>[XYZ]</b>, and set its <b>XYZActivation = yes</b>.<br><br>\
                    <b>Example</b>: To activate a GMC counter find <b>[GMC_Device]</b> and set: <b>GMC_Activation = yes</b>.<br><br>\
                    For more see chapter 'Configuration of GeigerLog' in the GeigerLog manual.<br>"

        msg = QMessageBox()
        msg.setWindowIcon       (self.iconGeigerLog)
        msg.setWindowTitle      ("Missing Device Activation")
        msg.setIcon             (QMessageBox.Warning)
        msg.setStandardButtons  (QMessageBox.Ok)
        msg.setDefaultButton    (QMessageBox.Ok)
        msg.setEscapeButton     (QMessageBox.Ok)
        msg.setWindowModality   (Qt.WindowModal)
        # msg.setText("<!doctype html>" + message)    # message must be html coded text
        msg.setInformativeText("<!doctype html>" + message)    # message must be html coded text # box is wider than with setText???

        burp()

        msg.exec()


    def startupProblems(self, message, closeGL=True):
        """Warning on serious problems like wrong Python version, configuration file missing,
        configuration file incorrect"""

        msg = QMessageBox()
        msg.setWindowIcon(self.iconGeigerLog)
        msg.setWindowTitle("STARTUP PROBLEM")
        msg.setIcon(QMessageBox.Warning)
        msg.setStandardButtons  (QMessageBox.Ok)
        msg.setDefaultButton    (QMessageBox.Ok)
        msg.setEscapeButton     (QMessageBox.Ok)
        msg.setWindowModality   (Qt.WindowModal)

        msg.setText("<!doctype html>" + message.replace("\n", "<br>"))    # message must be html coded text

        burp()

        msg.exec()

        if closeGL:
            self.close() # End GeigerLog; may not result in exit, needs sys.exit()
            sys.exit(1)


    def showIPStatus(self):

        defname = "showIPStatus"
        # dprint(defname)

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
        monserve.setToolTip('Monitor Server:   IP:Port')
        if g.MonServerSSL: ssl = "https://"
        else:                   ssl = "http://"
        monserve.setText("{}{} : {}".format(ssl, g.GeigerLogIP, g.MonServerPort))

    # WiFiClient Server
        if g.Devices["WiFiClient"][g.ACTIV]:
            lwific = QLabel("GeigerLog's WiFiClient Server:")
            lwific.setAlignment(Qt.AlignLeft)

            wific = QLabel()
            wific.setToolTip('WiFiClient Server:   IP:Port')
            ssl = "http://"
            wific.setText("{}{} : {}".format(ssl, g.GeigerLogIP, g.WiFiClientPort))
        else:
            lwific = QLabel("")
            wific  = QLabel("")

        ipoptions=QGridLayout()
        ipoptions.addWidget(lglip,                          0, 0)
        ipoptions.addWidget(glip,                           0, 1)
        ipoptions.addWidget(QLabel(""),                     1, 0)
        ipoptions.addWidget(QLabel("        IP Address :   Port"),    2, 1)
        ipoptions.addWidget(lmonserve,                      3, 0)               # MonServer
        ipoptions.addWidget(monserve,                       3, 1)
        ipoptions.addWidget(lwific,                         4, 0)               # WiFiClient
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

        defname = "searchNotePad: "

        qid = QInputDialog()
        stxt, ok = qid.getText(None, 'Search NotePad', 'Search Text:' + ' ' * 35, text=g.notePadSearchText)
        if not ok: return

        g.notePadSearchText = stxt
        # cdprint(defname + "stxt = '{}'".format(stxt), type(stxt))

        flag  = QTextDocument.FindBackward            # flag to search backwards
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

        defname = "saveNotePad: "

        nptxt = self.notePad.toPlainText()  # Saving as Plain Text; all is B&W, no colors
        #nptxt = self.notePad.toHtml()      # Saving in HTML Format; preserves color
        #mdprint(defname, "nptxt:", nptxt)

        if g.currentDBPath is None: newFile = os.path.join(g.dataDir, "notepad.txt")
        else:                       newFile = g.currentDBPath + '.txt'

        fprint(header("Saving NotePad Content"))
        fprint("appendingto File: {}\n".format(newFile))

        try:
            with open(newFile, 'a') as f:
                f.write(nptxt)
        except Exception as e:
            exceptPrint(e, defname + "save nptxt")


# force exit GeigerLog
    def forceClose(self, arg1, arg2):
        """force closure of GeigerLog upon SIGTERM or SIGINT signal"""

        defname = "forceClose: "
        # print(defname,  "arg1: ", arg1,  type(arg1), "   arg2: ", arg2,  type(arg2))

        if    arg1 == 2:  cmsg = "Force Closing GeigerLog per signal SIGINT = {}"           .format(arg1)
        elif  arg1 == 15: cmsg = "Force Closing GeigerLog per signal SIGTERM = {}"          .format(arg1)
        else:             cmsg = "Force Closing GeigerLog attempt with unknown signal= {}"  .format(arg1)
        cdprint(defname, cmsg)

        self.stopLogging()
        self.closeEvent(QCloseEvent())


# exit GeigerLog
    def closeEvent(self, event):
        """is called via self.close! Allow to Exit unless Logging is active"""
        # Qt event: QEvent.Close = 19 : Widget was closed

        defname = "closeEvent: "

        setBusyCursor()

        dprint("closeEvent: event type: {}".format(event.type()))
        setIndent(1)

        if g.logging :
            event.ignore()
            msg = "Cannot exit when logging! Stop logging first"
            self.showStatusMessage(msg)
            dprint(defname + "ignored; " + msg)

        else:
            event.accept()                           # allow closing the window
            dprint(defname + "accepted")

            # terminate threads
            gweb_monserv.terminateMonServer()

            # terminate all connected devices
            for DevName in g.Devices:
                # rdprint(defname, "DevName: {:10s},  Connection: {}".format(DevName, g.Devices[DevName][g.CONN]))
                if g.Devices[DevName][g.CONN]:  self.terminateNamedDevice(DevName)

            # close the databases for Log and His
            gsup_sql.DB_closeDatabase("Log")
            gsup_sql.DB_closeDatabase("His")

            dprint(defname + "exiting now")

            # Force Exit
            # The standard way to exit is sys.exit(n). sys.exit() is identical to
            # raise SystemExit(). It raises a Python exception which may be caught
            # by the caller.
            # os._exit(X) calls the C function _exit() which does an immediate program
            # termination. Note the statement "can never return".
            #
            # Excerpt from the book "The linux Programming Interface":
            # Programs generally don’t call _exit() directly, but instead call the exit() library
            # function, which performs various actions before calling _exit().
            #   -  Exit handlers (functions registered with at_exit() and on_exit()) are called,
            #      in reverse order of their registration
            #   -  The stdio stream buffers are flushed.
            #   -  The _exit() system call is invoked, using the value supplied in status.
            #
            # Instead of calling exit(), the child can call _exit(), so that it doesn’t flush stdio
            # buffers. This technique exemplifies a more general principle: in an application that
            # creates child processes, typically only one of the processes (most often the parent)
            # should terminate via exit(), while the other processes should terminate via _exit().
            # This ensures that only one process calls exit handlers and flushes stdio buffers,
            # which is usually desirable
            #
            # no plain os.exit() available in Python:
            # >>> os.exit()
            # AttributeError: module 'os' has no attribute 'exit'
            # >>> os._exit(6)  # does an exit

            # otherwise sub windows won't close
            os._exit(9) # reicht immer (na???)
            sys.exit(0) # reicht nicht immer

        # update the settings file
        g.SettingsNeedSaving = True

        setIndent(0)
        setNormalCursor()


#GraphOptions

    def changedGraphSelectedVariable(self):
        """called from the select combo for variables"""

        self.applyGraphOptions()


    def changedGraphDisplayCheckboxes(self, vname):
        """Graph varDisplayCheckbox vname has changed"""

        if not g.allowGraphUpdate: return

        defname  = "changedGraphDisplayCheckboxes: "
        oldIndex = self.select.currentIndex() # index of dropdown box selected variable
        index    = self.select.findText(vname)
        vIsChkd  = self.varDisplayCheckbox[vname].isChecked()
        # gdprint(defname + "var:{}, longname:{}, index:{} status Chk:{}".format(vname, vname, index, vIsChkd))

        if g.activeDataSource == "Log" : g.varChecked4PlotLog[vname] = vIsChkd
        else:                            g.varChecked4PlotHis[vname] = vIsChkd
        # gdprint("varChecked4PlotLog", getEasyDictPrint(g.varChecked4PlotLog))

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
            for i, vname in enumerate(g.VarsCopy):
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
        g.mavChecked  = self.mavbox.isChecked()

        self.applyGraphOptions()


    def changedGraphOptionsMavText(self, i):
        """Graph Option Mav Value has changed"""

        # print("changedGraphOptionsMavText: i:", i)

        try:
            mav_val = self.mav.text().replace(",", ".").replace("-", "")
            self.mav.setText(mav_val)
            val = float(mav_val)  # can value be converted to float?
            g.mav = val
        except Exception as e:
            # exceptPrint(e, "changedGraphOptionsMavText: MvAvg permits numeric values only")
            pass

        self.applyGraphOptions()


    def changedGraphOptionsAvg(self, i):
        """Graph Option Avg has changed"""

        #print("changedGraphOptionsAvg: i:", i)
        g.avgChecked  = self.avgbox.isChecked()
        self.applyGraphOptions()


    def changedGraphOptionsLinFit(self, i):
        """Graph Option LinFit has changed"""

        #print("changedGraphOptionsLinFit: i:", i)
        g.fitChecked = self.fitbox.isChecked()
        self.applyGraphOptions()


    def changedGraphCountUnit(self, i):
        """counter unit Graph Options for left Y-axis was changed"""

        oldYunit            = g.YunitCurrent
        g.YunitCurrent = str(self.yunit.currentText())
        newYunit            = g.YunitCurrent
        # print("changedGraphCountUnit: i:", i, ",  oldYunit:", oldYunit, ",  newYunit:", newYunit)

        # convert Y to CPM unit if not already CPM
        # print("changedGraphCountUnit: g.Ymin, g.Ymax, g.Sensitivity[0]", g.Ymin, g.Ymax, g.Sensitivity[0])
        if oldYunit == "µSv/h":
            if g.Ymin is not None: g.Ymin = g.Ymin * g.Sensitivity[0]
            if g.Ymax is not None: g.Ymax = g.Ymax * g.Sensitivity[0]

        # convert Y to µSv/h unit if not already µSv/h
        if newYunit == "µSv/h":
            if g.Ymin is not None: g.Ymin = g.Ymin / g.Sensitivity[0]
            if g.Ymax is not None: g.Ymax = g.Ymax / g.Sensitivity[0]

        if g.Ymin is None: self.ymin.setText("")
        else:                   self.ymin.setText("{:.5g}".format(g.Ymin))

        if g.Ymax is None: self.ymax.setText("")
        else:                   self.ymax.setText("{:.5g}".format(g.Ymax))

        if newYunit == "µSv/h":
            for vname in ("CPM", "CPS", "CPM1st", "CPS1st", "CPM2nd", "CPS2nd", "CPM3rd", "CPS3rd"):
                g.VarsCopy[vname][2] = "µSv/h"

        else:
            # newYunit == CPM
            for vname in ("CPM", "CPM1st", "CPM2nd", "CPM3rd"):
                g.VarsCopy[vname][2] = "CPM"

            for vname in ("CPS", "CPS1st", "CPS2nd", "CPS3rd"):
                g.VarsCopy[vname][2] = "CPS"

        self.applyGraphOptions()


    def changedGraphTemperatureUnit(self, i):
        """Temperature unit Graph Options was changed"""

        #print("changedGraphTemperatureUnit: New T unit:  i:", i, str(self.y2unit.currentText()) )

        if   i == 0:    g.VarsCopy["Temp"][2] = "°C"
        elif i == 1:    g.VarsCopy["Temp"][2] = "°F"

        self.applyGraphOptions()


    def changedGraphTimeUnit(self, i):
        """recalc xmin, xmax on Time unit changes"""

        #print("-----------------------changedGraphTimeUnit: i:", i)

        if np.all(g.logTime) is None: return

        gsup_plot.changeTimeUnitofPlot(self.xunit.currentText())

        self.applyGraphOptions()


    def keyPressEvent(self, event):
        """Apply Graph is only Button to accept Enter and Return key"""

        defname = "keyPressEvent: "

        # from: http://pyqt.sourceforge.net/Docs/PyQt4/qt.html#Key-enum
        # Qt.Key_Return         0x01000004
        # Qt.Key_Enter          0x01000005  Typically located on the keypad. (= numeric keypad)
        # Qt.Key_Control 	    0x01000021 	On Mac OS X, this corresponds to the Command keys.

        # rdprint(defname, "event.key():", hex(event.key()))

        if   event.key() in (Qt.Key_Enter, Qt.Key_Return):
            self.applyGraphOptions()
        # elif event.key() in (Qt.Key_Control, ):
        #     rdprint(defname, "CTRL pressed")
        #     g.useGraphScaledData = False


    def keyReleaseEvent(self, event):
        """Apply Graph is only Button to accept Enter and Return key"""

        defname = "keyReleaseEvent: "

        # rdprint(defname, "event.key():", hex(event.key()))

        if   event.key() in (Qt.Key_Enter, Qt.Key_Return):
            pass
        # elif event.key() in (Qt.Key_Control, ):
        #     rdprint(defname, "CTRL released")
        #     g.useGraphScaledData = True


    def setPlotVarsOnOff(self, newstate="OFF"): # 'OFF' 'ON'
        """checks or unchecks all variables from plotting"""

        g.allowGraphUpdate    = False  # prevents auto-updating at every variable

        if newstate == "OFF":
            for i, vname in enumerate(g.VarsCopy):
                if g.varsSetForCurrent[vname]:
                    self.varDisplayCheckbox[vname].setEnabled(True)     # the checkbox at the bottom of Graph dashboard - always enabled
                    self.varDisplayCheckbox[vname].setChecked(False)    # the checkbox at the bottom of Graph dashboard - unchecked
                    self.select.model().item(i)   .setEnabled(False)    # the dropdown selector for Selected Variable

                    if g.activeDataSource == "Log" : g.varChecked4PlotLog[vname] = False
                    else:                            g.varChecked4PlotHis[vname] = False

        else:
            for i, vname in enumerate(g.VarsCopy):
                if g.varsSetForCurrent[vname]:
                    self.varDisplayCheckbox[vname].setEnabled(True)     # the checkbox at the bottom of Graph dashboard - always enabled
                    self.varDisplayCheckbox[vname].setChecked(True)
                    self.select.model().item(i)   .setEnabled(True)

        # makes the index of the first enabled variable as the currentindex
        # of the variable select drop-down box
        for i, vname in enumerate(g.VarsCopy):
            #print("----i, self.select.model().item(i).isEnabled:", i, g.exgg.select.model().item(i).isEnabled())
            if self.select.model().item(i).isEnabled():
                g.exgg.select.setCurrentIndex(i)
                break

        g.allowGraphUpdate    = True
        self.applyGraphOptions() # not automatically done due to blocking by g.allowGraphUpdate


    def clearGraphLimits(self):
        """resets all min, max graph options to empty and plots the graph"""

        vprint("clearGraphLimits:")
        setIndent(1)

        g.Xleft               = None
        g.Xright              = None
        self.xmin.              setText("")
        self.xmax.              setText("")

        g.Ymin                = None
        g.Ymax                = None
        self.ymin.              setText("")
        self.ymax.              setText("")

        g.Y2min               = None
        g.Y2max               = None
        self.y2min.             setText("")
        self.y2max.             setText("")

        gsup_plot.makePlot()

        setIndent(0)


    def plotGraph(self, dataType, full=True):
        """Plots the data as graph; dataType is Log or His"""

        if  dataType == "Log" and g.logConn is None or \
            dataType == "His" and g.hisConn is None:
            self.showStatusMessage("No data available")
            return

        dprint("plotGraph: dataType: ", dataType)
        setIndent(1)

        if dataType == "Log":
            g.activeDataSource     = "Log"
            g.currentConn          = g.logConn
            g.currentDBPath        = g.logDBPath
            g.currentDBData        = g.logDBData
            g.varsSetForCurrent    = g.varsSetForLog.copy()
            varsChecked4Plot       = g.varChecked4PlotLog

            self.dcfLog.setText(g.currentDBPath)
            self.dcfLog.setStyleSheet("QLineEdit { background-color: #F9F4C9; color: rgb(80,80,80); }")
            self.dcfHis.setStyleSheet("QLineEdit { background-color: #DFDEDD; color: rgb(80,80,80); }")

        elif dataType == 'His':
            g.activeDataSource     = "His"
            g.currentConn          = g.hisConn
            g.currentDBPath        = g.hisDBPath
            g.currentDBData        = g.hisDBData
            g.varsSetForCurrent    = g.varsSetForHis.copy()
            varsChecked4Plot       = g.varChecked4PlotHis

            self.dcfHis.setText(g.currentDBPath)
            self.dcfLog.setStyleSheet("QLineEdit { background-color: #DFDEDD; color: rgb(80,80,80); }")
            self.dcfHis.setStyleSheet("QLineEdit { background-color: #F9F4C9; color: rgb(80,80,80); }")

        else:
            edprint("PROGRAMMING ERROR in geigerlog:plotGraph: var dataType is:", dataType, debug=True)
            sys.exit(1)

        g.allowGraphUpdate    = False  # otherwise a replot at every var happens!
        for i, vname in enumerate(g.VarsCopy):
            self.select.model().item(i)         .setEnabled(False)
            if g.varsSetForCurrent[vname]:
                value = varsChecked4Plot[vname]   # bool
                self.varDisplayCheckbox[vname]  .setChecked(value)
                self.varDisplayCheckbox[vname]  .setEnabled(True)
                self.select.model().item(i)     .setEnabled(value)
            else:
                self.varDisplayCheckbox[vname]  .setChecked(False)
                self.varDisplayCheckbox[vname]  .setEnabled(False)
        g.allowGraphUpdate    = True

        if g.currentDBData is not None:
            if g.currentDBData.size > 0:
                fprint(header("Plot Data"))
                fprint("from: {}".format(g.currentDBPath))

        self.figure.set_facecolor('#F9F4C9') # change colorbg in graph from gray to light yellow

        self.reset_replotGraph(full=full)

        setIndent(0)


    def reset_replotGraph(self, full=True):
        """resets all graph options to start conditions and plots the graph"""

        defname = "reset_replotGraph: "

        dprint(defname + "full: {}".format(full))
        setIndent(1)

        g.allowGraphUpdate    = False

        if full:
            g.Xleft               = None
            g.Xright              = None
            g.Xunit               = "Time"
            self.xmin.              setText("")
            self.xmax.              setText("")
            self.xunit.             setCurrentIndex(0)

            g.Ymin                = None
            g.Ymax                = None
            g.Yunit               = "CPM"
            self.ymin.              setText("")
            self.ymax.              setText("")
            self.yunit.             setCurrentIndex(0)

            g.Y2min               = None
            g.Y2max               = None
            g.Y2unit              = "°C"
            self.y2min.             setText("")
            self.y2max.             setText("")
            self.y2unit.            setCurrentIndex(0)

            self.select.            setCurrentIndex(0) # in case no data
            self.select.            setEnabled(True)   # required

            # reset to start condition
            for i, vname in enumerate(g.VarsCopy):
                # cdprint("i:{:2d} vname: {:10s} varDisplayCheckbox[vname].isEnabled(): {}".format(i, vname, self.varDisplayCheckbox[vname].isEnabled()))
                if self.varDisplayCheckbox[vname].isEnabled():
                    self.varDisplayCheckbox[vname].setChecked(True)
                    self.select.model().item(i).setEnabled(True)

        # Find the first enabled var and set this as selected var in dropdown box
        for i, vname in enumerate(g.VarsCopy):
            # cdprint("i:{:2d} vname: {:10s} select.model().item(i).isEnabled: {}".format(i, vname, g.exgg.select.model().item(i).isEnabled()))
            if self.select.model().item(i).isEnabled():
                self.select.setCurrentIndex(i)
                break

        g.mavChecked          = False
        self.mavbox.            setChecked(g.mavChecked)

        g.mav                 = g.mav_initial
        self.mav.               setText("{:0.0f}".format(g.mav_initial))

        g.avgChecked          = False
        self.avgbox.            setChecked(g.avgChecked)

        g.fitChecked          = False
        self.fitbox.            setChecked(g.fitChecked)

        g.VarsCopy            = g.VarsDefault.copy() # reset colors and linetype

        g.allowGraphUpdate    = True

        self.updateDisplayLastValuesWindow()
        self.updateDisplaySelectedVariable()

        self.applyGraphOptions()

        setIndent(0)


    def applyGraphOptions(self):

        if g.currentConn is None: return

        defname = "applyGraphOptions: "

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

        #~print(defname + "X : xmin:'{}', xmax:'{}', xunit:'{}', g.Xunit:'{}'".format(xmin, xmax, xunit, g.Xunit))
        #~print(defname + "Y : ymin:'{}', ymax:'{}', yunit:'{}', g.Yunit:'{}'".format(ymin, ymax, yunit, g.Yunit))
        #~print(defname + "Y2: ymin:'{}', ymax:'{}'                      ".format(y2min, y2max))
        #~print(defname + "mav:'{}'".format(mav))

    # x
        if  xmin == "":
            g.Xleft  = None
        else:
            if g.Xunit == "Time":
                try:
                    g.Xleft = mpld.datestr2num(str(xmin))
                except:
                    g.Xleft = None
                    # efprint("Did not recognize Time Min")
                    efprint("Cannot read Time Min")
            else:
                try:
                    g.Xleft     = float(xmin)
                except:
                    g.Xleft     = None
                    # efprint("Did not recognize Time Min")
                    efprint("Cannot read Time Min")

        if  xmax == "":
            g.Xright = None
        else:
            if g.Xunit == "Time":
                try:
                    g.Xright = mpld.datestr2num(str(xmax))
                except:
                    g.Xright = None
                    # efprint("Did not recognize Time Max")
                    efprint("Cannot read Time Max")
            else:
                try:
                    g.Xright    = float(xmax)
                except:
                    g.Xright    = None
                    # efprint("Did not recognize Time Max")
                    efprint("Cannot read Time Max")

        #print(defname + "Xleft ", g.Xleft,  ",  Xright", g.Xright)

        if g.Xleft is not None and g.Xright is not None:
            if g.Xleft >= g.Xright:
                efprint("Graph: Wrong numbers: Time Min must be less than Time Max")
                return

        g.Xunit     = xunit

    # y
        try:    g.Ymin      = float(ymin)
        except: g.Ymin      = None

        try:    g.Ymax      = float(ymax)
        except: g.Ymax      = None

        if g.Ymin is not None and g.Ymax is not None:
            if g.Ymin >= g.Ymax:
                efprint("Graph: Wrong numbers: Count Rate min must be less than Count Rate max")
                return

        g.Yunit     = yunit

    # y2
        try:    g.Y2min      = float(y2min)
        except: g.Y2min      = None

        try:    g.Y2max      = float(y2max)
        except: g.Y2max      = None

        if g.Y2min is not None and g.Y2max is not None:
            if g.Y2min >= g.Y2max:
                efprint("Graph: Wrong numbers: Ambient min must be less than Ambient max")
                return

    # color
        colorName = g.VarsCopy[getNameSelectedVar()][3]
        self.btnColor.setText("")
        self.btnColor.setStyleSheet("QLabel { border: 1px solid silver;  border-radius: 3px; background-color: %s ; }" % (colorName))
        addMenuTip(self.btnColor, self.btnColorText + colorName)

    # replot
        gsup_plot.makePlot()
        self.updateDisplayLastValuesWindow()
        self.updateDisplaySelectedVariable()


    def updatecursorposition(self, event):
        """when cursor inside plot, get position and print to statusbar"""
        # see: https://matplotlib.org/api/backend_bases_api.html#matplotlib.backend_bases.MouseEvent

        # calc based on:
        # g.y1_limit = ax1.get_ylim    defined in gsup_plot.py
        # g.y2_limit = ax2.get_ylim

        defname = "updatecursorposition: "

        # ydprint(defname, "g.y1_limit:", g.y1_limit, ", g.y2_limit:", g.y2_limit)
        # rdprint(defname, "event: ", event, ", event.inaxes: ", event.inaxes)

        try: # results in non-breaking error messages when no data are displayed
            if event.inaxes:
                x  = event.xdata
                y2 = event.ydata
                y1 = (y2 - g.y2_limit[0]) / (g.y2_limit[1] - g.y2_limit[0]) * (g.y1_limit[1] - g.y1_limit[0]) + g.y1_limit[0]
                # rdprint(defname, f"updatecursorposition: x:{x:0.10f} y1:{y1:0.3f}  y2:{y2:0.3f}")

                if g.Xunit == "Time":
                    tod = (str(mpld.num2date(x)))[:19]          # time of day
                    t   = gsup_plot.getTimeSinceFirstRecord(g.logTimeFirst, x)
                else:
                    tod = gsup_plot.getTimeOfDay(g.logTimeFirst, x, g.XunitCurrent)
                    t   = "{:0.3f} {}s".format(x, g.XunitCurrent)

                message = f"Time since 1st record: {t}, Time: {tod}, Counter: {y1:0.3f}, Ambient: {y2:0.3f}"
                self.showStatusMessage(message, timing=0, error=False) # message remains until overwritten by next
        except:
            #print("event not inaxes")
            pass


    def onclick(self, event):
        """on mouseclick in graph enter time coords into xmin, xmax;
        left click = xmin, right click = xmax"""

        try: # if no data are shown, this may result in non-breaking error messages
            if event.inaxes:
                x = event.xdata
                y = event.ydata
                b = event.button
                #print event, x,y,b

                if g.Xunit == "Time":
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

        defname = "getFileHistory: "

    #
    # make the filedialog
    #
        # conditions
        if   source == "Database":
            # there must be an existing '*hisdb' file;
            # writing to it is not necessary; it will not be modified
            dlg=QFileDialog(caption = "Get History - Select from Existing Database File", options=QFileDialog.DontUseNativeDialog)
            # dlg=QFileDialog(caption = "Get History - Select from Existing Database File")
            dlg.setFileMode(QFileDialog.ExistingFile)
            dlg.setNameFilter("History or Log Files (*.hisdb *.logdb);;Only History Files (*.hisdb);;Only Log Files (*.logdb);;Any Files (*)")

        elif source == "Binary File":
            # there must be an existing, readable '*.bin' file, and it must be allowed to write .hisdb files;
            # the bin file will remain unchanged
            dlg=QFileDialog(caption = "Get History - Select from Existing Binary File", options=QFileDialog.DontUseNativeDialog)
            # dlg=QFileDialog(caption = "Get History - Select from Existing Binary File")
            dlg.setFileMode(QFileDialog.ExistingFile)
            dlg.setNameFilter("History Files (*.bin *.gmc);;Any Files (*)")

        elif source == "Parsed File":
            # there must be an existing, readable csv file and it must be allowed to write .hisdb files;
            # the his file will remain unchanged
            dlg=QFileDialog(caption= "Get History - Select from Existing CSV File", options=QFileDialog.DontUseNativeDialog)
            # dlg=QFileDialog(caption= "Get History - Select from Existing CSV File")
            dlg.setFileMode(QFileDialog.ExistingFile)
            dlg.setNameFilter("History Files (*.csv *.txt *.log *.his *.notes);;Any Files (*)")

        elif source == "Device":    # a GMC device
            if g.logging:
                fprint(header("Get History from GMC Device"))
                efprint("Cannot load History when logging. Stop Logging first")
                return

            # may use existing or new .hisdb file, but must be allowed to overwrite this file;
            # an existing hisdb file will be overwritten
            dlg=QFileDialog(caption = "Get History from GMC Device - enter new filename or select from existing", options=QFileDialog.DontUseNativeDialog)
            # dlg=QFileDialog(caption = "Get History from GMC Device - enter new filename or select from existing")
            dlg.setFileMode(QFileDialog.AnyFile)
            dlg.setNameFilter("History Files (*.hisdb);;Any Files (*)")

        elif source == "GSDevice":  # a Gamma Scout device
            # may use existing or new .hisdb file, but must be allowed to overwrite this file;
            # an existing hisdb file will be overwritten
            dlg=QFileDialog(caption = "Get History from Gamma-Scout Device - enter new filename or select from existing", options=QFileDialog.DontUseNativeDialog)
            # dlg=QFileDialog(caption = "Get History from Gamma-Scout Device - enter new filename or select from existing")
            dlg.setFileMode(QFileDialog.AnyFile)
            dlg.setNameFilter("History Files (*.hisdb);;Any Files (*)")

        elif source == "GSDatFile":
            # there must be an existing, readable '*.dat' file, created by memory dumping of
            # a Gamma Scout device, and it must be allowed to write .hisdb files;
            # the dat file will remain unchanged
            dlg=QFileDialog(caption = "Get History - Select from Existing Gamma Scout *.dat File", options=QFileDialog.DontUseNativeDialog)
            dlg.setFileMode(QFileDialog.ExistingFile)
            # dlg.setNameFilter("History Files (*.dat);;Any Files (*)")
            dlg.setNameFilter("History Files (*.dat)")

        elif source == "AMDeviceCAM":  # an AmbioMon device for CAM data
            # may use existing or new .hisdb file, but must be allowed to overwrite this file;
            # an existing hisdb file will be overwritten
            dlg=QFileDialog(caption = "Get History from Manu Device - enter new filename or select from existing", options=QFileDialog.DontUseNativeDialog)
            # dlg=QFileDialog(caption = "Get History from Manu Device - enter new filename or select from existing")
            dlg.setFileMode(QFileDialog.AnyFile)
            dlg.setNameFilter("History Files (*.hisdb);;Any Files (*)")

        elif source == "AMDeviceCPS":  # an AmbioMon device for CPS data
            # may use existing or new .hisdb file, but must be allowed to overwrite this file;
            # an existing hisdb file will be overwritten
            dlg=QFileDialog(caption = "Get History from Manu Device - enter new filename or select from existing", options=QFileDialog.DontUseNativeDialog)
            # dlg=QFileDialog(caption = "Get History from Manu Device - enter new filename or select from existing")
            dlg.setFileMode(QFileDialog.AnyFile)
            dlg.setNameFilter("History Files (*.hisdb);;Any Files (*)")

        elif source == "AMFileCAM":
            # there must be an existing, readable '*.CAM' file, created by e.g. downloading
            # from an AmbioMon device, and it must be allowed to write .hisdb files
            # the *.CAM file will remain unchanged
            dlg=QFileDialog(caption = "Get History - Select from Existing AmbioMon binary *.CAM File", options=QFileDialog.DontUseNativeDialog)
            # dlg=QFileDialog(caption = "Get History - Select from Existing AmbioMon binary *.CAM File")
            dlg.setFileMode(QFileDialog.ExistingFile)
            dlg.setNameFilter("History Binary Files (*.CAM *.data);;Any Files (*)")

        elif source == "AMFileCPS":
            # there must be an existing, readable '*.CPS' file, created by e.g. downloading
            # from an AmbioMon device, and it must be allowed to write .hisdb files
            # the *.CPS file will remain unchanged
            dlg=QFileDialog(caption = "Get History - Select from Existing AmbioMon binary *.CPS File", options=QFileDialog.DontUseNativeDialog)
            # dlg=QFileDialog(caption = "Get History - Select from Existing AmbioMon binary *.CPS File")
            dlg.setFileMode(QFileDialog.ExistingFile)
            dlg.setNameFilter("History Binary Files (*.CPS *.data);;Any Files (*)")


        # elif source == "RadPro Device (new)":
        #     # may use existing or new .hisdb file, but must be allowed to overwrite this file
        #     # an existing hisdb file will be overwritten
        #     dlg=QFileDialog(caption = "Get New History from RadPro Device - enter new filename or select from existing", options=QFileDialog.DontUseNativeDialog)
        #     dlg.setFileMode(QFileDialog.AnyFile)
        #     dlg.setNameFilter("History Files (*.hisdb);;Any Files (*)")

        elif source == "RadPro":
            # may use existing or new .hisdb file, but must be allowed to overwrite this file
            # an existing hisdb file will be overwritten
            dlg=QFileDialog(caption = "Get History from RadPro Device - enter new filename or select from existing", options=QFileDialog.DontUseNativeDialog)
            dlg.setFileMode(QFileDialog.AnyFile)
            dlg.setNameFilter("History Files (*.hisdb);;Any Files (*)")

        else:
            printProgError(defname, f"Filedialog: Wrong source: '{source}'")

        dlg.setViewMode     (QFileDialog.Detail)
        dlg.setWindowIcon   (self.iconGeigerLog)
        dlg.setDirectory    (g.fileDialogDir)
        dlg.setFixedSize    (950, 550)

        # Execute dialog
        if dlg.exec() == QDialog.Accepted:  pass     # QDialog Accepted
        else:                               return   # QDialog Rejected
    ### end filedialog -  a file was selected

    #
    # Process the selected file
    #
        while True:
            fprint(header("Get History from {}".format(source)))
            dprint(defname + "from source: ", source)
            setIndent(1)
            QtUpdate()

            g.fileDialogDir = dlg.directory().path() # remember the directory
            #print("getFileHistory: fileDialogDir:", g.fileDialogDir)

            fnames      = dlg.selectedFiles()
            fname       = str(fnames[0])                # file path
            fext        = os.path.splitext(fname)[1]    # file ext
            fname_base  = os.path.splitext(fname)[0]    # file basename with path w/o ext

            vprint(defname + "file name:   '{}'"                   .format(fname))
            wprint(defname + "fname_base:  '{}', fname_ext: '{}'"  .format(fname_base, fext))

            g.binFilePath = None
            g.hisFilePath = None
            g.datFilePath = None

            if   source == "Database":
                g.hisDBPath   = fname # already has extension ".hisdb"
                if not isFileReadable(g.hisDBPath):     break

            elif source == "Binary File":
                g.binFilePath = fname
                g.hisDBPath   = fname_base + ".hisdb"
                if not isFileReadable (g.binFilePath):  break
                if not isFileWriteable(g.hisDBPath):    break

            elif source == "Parsed File":
                g.hisFilePath = fname
                g.hisDBPath   = fname_base + ".hisdb"
                if not isFileReadable (g.hisFilePath):  break
                if not isFileWriteable(g.hisDBPath):    break

            elif source in ("Device", "GSDevice", "AMDeviceCAM", "AMDeviceCPS", "RadPro"):
                if fext != ".hisdb":
                    g.hisDBPath   = fname + ".hisdb" # file has any extension or none
                else:
                    g.hisDBPath   = fname            # file already has .hisdb extension
                if not isFileWriteable(g.hisDBPath):    break

            elif source == "GSDatFile":
                g.datFilePath = fname
                g.hisDBPath   = fname + ".hisdb"
                if not isFileReadable (g.datFilePath):  break
                if not isFileWriteable(g.hisDBPath):    break

            elif source in ("AMFileCAM", "AMFileCPS"):
                g.AMFilePath = fname
                g.hisDBPath   = fname + ".hisdb"
                if not isFileReadable (g.AMFilePath):   break
                if not isFileWriteable(g.hisDBPath):    break

            else:
                printProgError(defname, f"Processing Selected File: Wrong source: '{source}'")


            # Messagebox re Overwriting file
            if source in ("Device", "GSDevice", "AMDeviceCAM", "AMDeviceCPS", "RadPro"):
                if os.path.isfile(g.hisDBPath):
                    msg = QMessageBox()
                    msg.setIcon(QMessageBox.Critical)
                    msg.setWindowTitle("CAUTION")
                    critical  = """You selected an existing file, which will be <b>OVERWRITTEN</b> if you continue.<br><br>Please confirm with OK.
                                    <br><br>Otherwise click Cancel and enter a new filename in the Get History from Device dialog."""
                    msg.setText(critical)
                    msg.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
                    msg.setDefaultButton(QMessageBox.Cancel)
                    msg.setEscapeButton(QMessageBox.Cancel)
                    retval = msg.exec()

                    if retval != 1024:
                        fprint("Get History is cancelled")
                        break

            g.currentDBPath   = g.hisDBPath

            #dprint("getFileHistory: g.binFilePath:     ", g.binFilePath)
            #dprint("getFileHistory: g.hisFilePath:     ", g.hisFilePath)
            #dprint("getFileHistory: g.hisDBPath:       ", g.hisDBPath)
            #dprint("getFileHistory: g.currentDBPath:   ", g.currentDBPath)

            self.setBusyCursor()
            hidbp = "History database: {}"      .format(g.hisDBPath)
            fprint(hidbp)
            QtUpdate()

            dprint(defname + hidbp)

            self.dcfHis.setText(g.currentDBPath)
            self.clearLogPad()

            g.varsSetForHis        = g.varAllFalse.copy()  # variable is active in the current His
            g.varChecked4PlotHis   = g.varAllFalse.copy()  # is variable checked for showing in plot for History

            # an existing classic his, bin, or dat file was selected,
            # delete old database first
            if      g.hisFilePath is not None \
                or  g.binFilePath is not None \
                or  g.datFilePath is not None \
                or  g.hisDBPath   is not None and source in ("Device", "GSDevice", "AMDeviceCAM", "AMDeviceCPS", "RadPro"):

                gsup_sql.DB_deleteDatabase("His", g.hisDBPath)

            # Open the database
            g.hisConn = gsup_sql.DB_openDatabase  (g.hisConn, g.hisDBPath)

            if g.hisFilePath is not None:
                fprint("Creating from file {}".format(g.hisFilePath))
                # read data from CSV file into database
                self.setNormalCursor()
                success = gsup_sql.getCSV(g.hisFilePath)
                if success:
                    self.setBusyCursor()
                    gsup_sql.DB_convertCSVtoDB(g.hisConn, g.hisFilePath)
                else:
                    fprint("Database creation was cancelled")
                    return

            elif g.binFilePath is not None:
                fprint("Creating from file {}".format(g.binFilePath))

            # Make Hist for source = GMC Device, GMC Binary File
            if source in ("Device", "Binary File"):
                error, message = gdev_gmc_hist.makeGMC_History(source)
                if error == -1:                                # a severe error
                    efprint(message)
                    break

            # Make Hist for source = Gamma Scout device or Gamma Scout *.dat File
            elif source in ("GSDevice", "GSDatFile"):
                error, message = gdev_gammascout.GSmakeHistory(source)
                if error == -1:                                # a severe error
                    efprint(message)
                    break

            # Make Hist for source = AmbioMon device
            elif source in ("AMDeviceCAM", "AMDeviceCPS"):
                # error, message = gdev_Manu.makeAmbioHistory(source, g.AmbioDeviceName)
                error, message = gdev_ambiomon.makeAmbioHistory(source, g.Devices["AmbioMon"][g.DNAME])
                if error == -1:                                # a severe error
                    efprint(message)
                    break

            # Make Hist for source = AmbioMon binary file
            elif source in ("AMFileCAM", "AMFileCPS"):
                # error, message = gdev_Manu.makeAmbioHistory(source, g.AmbioDeviceName)
                error, message = gdev_ambiomon.makeAmbioHistory(source, g.Devices["AmbioMon"][g.DNAME])
                if error == -1:                                # a severe error
                    efprint(message)
                    break


            # Make Hist for source = RadPro device
            elif source in ("RadPro"):
                error, message = gdev_radpro.loadHistoryRadPro(source)
                if error == -1:                                # a severe error
                    efprint(message)
                    break


            g.hisDBData, varsFromDB = gsup_sql.getDataFromDatabase("His") # also creates varchecked
            for vname in g.VarsCopy:
                if varsFromDB[vname]:           g.varsSetForHis[vname] = True
                if g.varsSetForHis[vname]: g.varChecked4PlotHis[vname] = True

            self.plotGraph("His")

            self.checkLoggingState()
            break

        self.setNormalCursor()

        setIndent(0)

#clf
    def clearLogfile(self):
        """Delete the logfile database and recreate it"""

        defname = "clearLogfile: "

        msg = QMessageBox()
        msg.setWindowIcon(g.iconGeigerLog)
        msg.setIcon(QMessageBox.Critical)
        msg.setWindowTitle("Clear Log File")
        msg.setText("You will loose all data in this database.<br><br>Please confirm with OK, or Cancel\n")
        msg.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
        msg.setDefaultButton(QMessageBox.Cancel)
        msg.setEscapeButton(QMessageBox.Cancel)
        retval = msg.exec()

        if retval == QMessageBox.Ok:                        # QMessageBox.Ok == 1024
            dprint(defname)
            setIndent(1)
            self.btnClearLogfile.setEnabled(False)

            # rdprint(defname, "logDBPath: ", g.logDBPath)

            self.stopLogging()
            gsup_sql.DB_deleteDatabase("Log", g.logDBPath)
            self.getFileLog(defaultLogDBPath=g.logDBPath)

            self.btnClearLogfile.setEnabled(True)
            setIndent(0)


    def setAlarmStatus(self, action):
        """Configure Alarm setting and print to Notepad"""

        if   action == "list":
            errmsg = gsup_tools.setAlarmConfiguration()
            if errmsg != "Cancelled":
                tmplt = "{:20s} : {}"
                fprint(header("Alarm Status"))
                fprint(tmplt.format("Alarm Activation",     "Yes" if g.AlarmActivation      else "No"))
                # fprint(tmplt.format("Alarm Usage",          "Yes" if g.AlarmActivation      else "No"))
                fprint(tmplt.format("Alarm Sound",          "Yes" if g.AlarmSound           else "No"))
                fprint(tmplt.format("Alarm Idle Cycles",    g.AlarmIdleCycles))
                fprint(tmplt.format("Send Alarm-Email",     "Yes" if g.emailActivation      else "No"))
                # fprint(tmplt.format("Send Alarm-Telegram",  "Yes" if g.TelegramActivation   else "No"))
                fprint("")
                fprint("Alarm Limits:")
                tmplt = "   {:17s} : {}"
                for vname in g.AlarmLimits:
                    if g.AlarmLimits[vname] is not None: alimits = ", ".join( "{}".format(lim) for lim in  g.AlarmLimits[vname])
                    else:                                alimits = "None"
                    fprint(tmplt.format(vname, alimits))
                if errmsg > "":  efprint(errmsg)

        yb = "QPushButton {font-size:12px; background-color:#F4D345; color:rgb(0,0,0);}" # yellow button bg, black text
        gb = "QPushButton {font-size:12px;}"                                            # std grey button bg
        if g.AlarmActivation:
            # same at all actions
            if   action == "start": stylesheetcode = yb
            elif action == "stop":  stylesheetcode = yb
            else:                   stylesheetcode = yb
        else:
            stylesheetcode = gb
        self.btnAlarm.setStyleSheet(stylesheetcode)


    def setLogCycle(self):
        """Set Log Cycle"""

        defname = "setLogCycle: "

        vprint(defname)
        setIndent(1)

        title = "Set LogCycle Duration"

        lctime     = QLabel("LogCycle [s]  \n(0.1 ... 1000)   ")
        lctime.setAlignment(Qt.AlignLeft)

        self.ctime = QLineEdit()
        validator  = QDoubleValidator(0.1, 1000, 1, self.ctime)        # 100 ms
        self.ctime.setValidator(validator)
        # self.ctime.setToolTip('The log cycle in seconds. Changeable only when not logging.')
        self.ctime.setToolTip('The LogCycle duration in seconds.')
        self.ctime.setText("{:0.5g}".format(g.LogCycle))

        graphOptions=QGridLayout()
        graphOptions.addWidget(lctime,                  0, 0)
        graphOptions.addWidget(self.ctime,              0, 1)

        d = QDialog() # set parent empty to popup in center of screen
        d.setWindowIcon(self.iconGeigerLog)
        d.setWindowTitle(title)
        d.setWindowModality(Qt.WindowModal)

        self.bbox = QDialogButtonBox()
        self.bbox.setStandardButtons(QDialogButtonBox.Cancel | QDialogButtonBox.Ok )
        self.bbox.accepted.connect(lambda: d.done(100))
        self.bbox.rejected.connect(lambda: d.done(0))

        g.btn = self.bbox.button(QDialogButtonBox.Ok)
        g.btn.setEnabled(True)

        layoutV = QVBoxLayout(d)
        layoutV.addLayout(graphOptions)
        layoutV.addWidget(self.bbox)

        self.ctime.textChanged.connect(self.check_state) # last chance
        self.ctime.textChanged.emit   (self.ctime.text())

        # if g.logging:
        #     g.btn.setEnabled(False)
        #     self.ctime.setEnabled(False)
        #     self.ctime.setStyleSheet('QLineEdit { background-color: %s;  }' % ("#e0e0e0",))

        retval = d.exec()
        #print("retval:", retval)

        if retval == 0:
            vprint(defname + "Cancel. Cycle time unchanged: ", g.LogCycle) # Cancel or ESC
        else:
            # change the cycle time
            oldlogCycle = g.LogCycle
            newLogCycle = self.ctime.text().replace(",", ".")  #replace comma with dot

            try:    g.LogCycle = round(float(newLogCycle), 1)
            except: g.LogCycle = oldlogCycle

            self.showTimingSetting(g.LogCycle)
            msg = "New LogCycle duration: {} sec".format(g.LogCycle)

            # update database with logcyle
            if g.logConn is not None:
                gsup_sql.DB_updateLogcycle(g.logConn, g.LogCycle)

            ctype       = "LOGGING"
            cJulianday  = getTimeJulian()
            cinfo       = msg
            logPrint("#LOGGING, {}, {}\n".format(stime(), msg)) # to the LogPad
            gsup_sql.DB_insertComments(g.logConn, [[ctype, cJulianday, cinfo]]) # to the DB

            vprint(defname, msg)
            fprint(header(title))
            fprint(msg)

        setIndent(0)


    def check_state(self, *args, **kwargs):

        sender = self.sender()

        # print("sender.text():", sender.text())
        # print("args:", args)
        # print("kwargs:", kwargs)

        try:
            v = float(sender.text().replace(",", "."))
            # if   v < 0.1:       state = 0   # too low
            if   v < 0.01:       state = 0   # too low
            elif v > 1000:      state = 0   # too high
            else:               state = 2   # ok
        except:
            state = 0                       # wrong data

        # print("QValidator.Acceptable:", QValidator.Acceptable)

        # Value: QValidator.Acceptable == 2
        if state == QValidator.Acceptable:
            bgcolor = 'white' # white
            color   = 'black'
            g.btn.setEnabled(True)

        #elif state == QValidator.Intermediate:
        #    color = '#fff79a' # yellow

        else:
            bgcolor = '#fff79a' # yellow
            color   = 'red'
            self.ctime.setFocus()
            g.btn.setEnabled(False)

        sender.setStyleSheet('QLineEdit { background-color: %s; color: %s }' % (bgcolor, color))


# start logging
    def startLogging(self):
        """Starts the logging"""

        if g.logging: return            # kann das vorkommen?

        defname = "startLogging: "
        dprint(defname)

        fprint(header("Start Logging"))

        # A logfile is not loaded
        # should never happen as the start button should be inactive
        if g.logDBPath is None:
            efprint("WARNING: Cannot log; Logfile is not loaded")
            return

        # Logfile is either read-only, not writeable, or had been removed
        if not os.access(g.logDBPath, os.W_OK):
            efprint("WARNING: Cannot log; Logfile is not available for writing!")
            return

        # No loggable variables
        if g.varMapCountTotal == 0:
            efprint("WARNING: No variables for logging available; Logging is not possible!")
            qefprint("Please check configuration if this is unexpected !")
            return

    # all clear, go for it

        setIndent(1)

        g.logging       = True          # set early, to allow threads to get data
        g.LogReadings   = 0
        g.currentDBPath = g.logDBPath

        # make comment lines like:
        #   DEVICES, 2022-06-06 15:54:46, Connected: GMC : GMC-300Re 4.54 : CPS
        #   DEVICES, 2022-06-06 15:54:46, Connected: Manu : GeigerLog Manu : Temp Press Humid Xtra
        #   LOGGING, 2022-06-06 15:54:46, Start @LogCycle: 1.0 sec
        comments  = []
        printcom  = ""
        for DevName in g.Devices:
            if g.DevVarsAsText[DevName] is not None:
                cinfo     = "Connected: {} : {} : {}" .format(DevName, g.Devices[DevName][0], g.DevVarsAsText[DevName])
                printcom += "#DEVICES, {}, {}\n"     .format(stime(), cinfo)
                cJulianday  = getTimeJulian()
                comments.append(["DEVICES", cJulianday, cinfo])

        cinfo     = "Start @LogCycle: {} sec"   .format(g.LogCycle)
        printcom += "#LOGGING, {}, {}"       .format(stime(), cinfo)
        cJulianday  = getTimeJulian()
        comments.append(["LOGGING", cJulianday, cinfo])

        gsup_sql.DB_insertComments(g.logConn, comments)
        logPrint(printcom)
        fprint  (printcom)

        cleanupDevices("before logging")

        # Navtoolbar is not useful when logging, as graph will be overwritten on every update
        self.navtoolbar.setEnabled(False)
        # self.navtoolbar.setStyleSheet("background-color:lightGray;") # not easy to see

    # STARTING
        self.checkLoggingState()
        self.plotGraph("Log", full=False)                   # initialize graph settings
        g.logCycleBtnRequestOn = True
        g.LogCycleStart = g.NAN

        self.updateDisplayLastValuesWindow()
        self.updateDisplaySelectedVariable()


    # Now start logging
        # g.LogThreadStartTime = time.time()
        g.LogThreadStartTime = time.time() + 0.01                 # skip first 10 msec to let initLogThread printouts finish
        initLogThread()
        dprint(defname, "Logging Timer was started with cycle of {} sec  at: {}".format(g.LogCycle, longnum2datestr(g.LogThreadStartTime)))

        # self.setAlarmStatus("start")
        self.flashCycleButton("On")

        setIndent(0)

        dprint(TGREEN + "Logging has started " + "#" * 130 + TDEFAULT)


# stop logging
    def stopLogging(self):
        """Stops the logging"""

        if not g.logging: return

        defname = "stopLogging: "
        dprint(defname)
        setIndent(1)

        fprint(header("Stop Logging"))

        # cdprint(defname + "about to call terminateLogThread()")
        terminateLogThread()

        g.logging = False
        dprint(defname, "Logging is stopped")

        writestring  = "#LOGGING, {}, Stop".format(stime())
        logPrint(writestring)
        fprint(writestring)

        cJulianday  = getTimeJulian()
        gsup_sql.DB_insertComments(g.logConn, [["LOGGING", cJulianday, "Stop"]])

        cleanupDevices("after logging")

        # Navtoolbar is useful only when NOT logging, as graph will be overwritten during logging
        self.navtoolbar.setEnabled(True)
        # self.navtoolbar.setStyleSheet("background-color:lightgreen;") # ugly

        self.checkLoggingState()
        self.labelSelVar.setStyleSheet('color:darkgray;')
        self.updateDisplayLastValuesWindow()
        self.updateDisplaySelectedVariable()

        # For the the Rad World Map update - will make it wait for full cycle
        # g.RWMmapLastUpdate = None
        g.RWMmapLastUpdate = 0

        # g.logCycleBtnRequestOn = False
        self.flashCycleButton("Off")

        self.setAlarmStatus("stop")

        setIndent(0)


    def addComment(self, dataType):
        """Adds a comment to the current log"""

        if dataType == "Log":
            if g.logConn is None:
                self.showStatusMessage("No LogFile available")
                return

        elif dataType == "His":
            if g.hisConn is None:
                self.showStatusMessage("No HisFile available")
                return

        else:
            if g.currentConn is None:
                self.showStatusMessage("No File available")
                return
            elif g.currentConn == g.logConn:  dataType = "Log"
            else:                                       dataType = "His"

        info        = ("Enter your comment to the <b>{}</b> file: " + "&nbsp;"*40).format(dataType)

        d           = QInputDialog()
        # it looks like QInputDialog() always blocks outside clicking????
        d.setWindowModality(Qt.NonModal)                                      # no clicking outside
        dtext, ok   = d.getText(None, 'Add a Comment', info)

        if ok:
            dtext       = str(dtext)
            ctype       = "COMMENT"
            cJulianday  = getTimeJulian()
            cinfo       = dtext
            if dataType == "Log":
                fprint(header("Add Comment to Log"))
                logPrint("#COMMENT, {}, {}".format(stime(), dtext)) # to the LogPad
                fprint("#COMMENT, {}, {}".format(stime(), dtext))   # to the NotePad
                gsup_sql.DB_insertComments(g.logConn, [[ctype, cJulianday, cinfo]]) # to the DB

            else: # dataType == "His"
                fprint(header("Add Comment to History"))
                fprint("#COMMENT, {}, {}".format(stime(), dtext))   # to the NotePad
                cJulianday  = None
                gsup_sql.DB_insertComments(g.hisConn, [[ctype, cJulianday, cinfo]]) # to the db

            vprint("Add a Comment: text='{}', ok={}".format(dtext,ok))


    def addGMC_Error(self, errtext):
        """Adds ERROR info from gdev_gmc as comment to the current log"""

        logPrint("#GMC_ERROR, {}, {}".format(stime(), errtext))   # to the LogPad

        if not g.logConn is None:                            # to the DB
            # gsup_sql.DB_insertComments(g.logConn, [["DevERROR", "NOW", "localtime", errtext]])
            # gsup_sql.DB_insertComments(g.logConn, [["DevERROR", "NOW", errtext]])
            cJulianday  = getTimeJulian()
            gsup_sql.DB_insertComments(g.logConn, [["DevERROR", cJulianday, errtext]])


    def addMsgToLog(self, type, msg):
        """Adds message to the current log
        type: like 'Success', 'Failure'
        msg : any text
        """

        logPrint("#{}, {}, {}".format(type, stime(), msg))          # to the LogPad

        if not g.logConn is None:                                   # to the DB
            cJulianday  = getTimeJulian()
            gsup_sql.DB_insertComments(g.logConn, [[type, cJulianday, msg]])


#
# Update the LogCycle setting in the dashboard
#
    def showTimingSetting(self, LogCycle):
        """update the LogCycle duration shown on the LogCycle button"""

        # text = "LogCycle:{:0.5g}s".format(LogCycle)
        text = "Cycle:{:0.5g}s".format(LogCycle)
        self.btnSetCycle.setText(text)
        # self.btnProgress.setFormat(text)



#
# Update the Selected Variable
#
    def updateDisplaySelectedVariable(self):
        """
        update: the Selected Variable Value displayed in the Graph LastValue box
        return: nothing
        """

        ### local defs ##################################################################################

        def getTubeIndex(selVar):
            """getting TubeIndex from selected Var name"""

            if   "1" in selVar:   TubeIndex = 1
            elif "2" in selVar:   TubeIndex = 2
            elif "3" in selVar:   TubeIndex = 3
            else:                 TubeIndex = 0

            return TubeIndex


        def getStatusTip(selVar, svalue):
            """the status tip to show on the last variable field"""

            if "M" in selVar: value = svalue         # CPM
            else:             value = svalue * 60    # CPS

            TubeIndex  = getTubeIndex(selVar)
            statusTip  =    "{:0.2f} CPM"  .format(value)
            statusTip += " = {:0.2f} CPS"  .format(value / 60)
            statusTip += " = {:0.2f} µSv/h".format(value / g.Sensitivity[TubeIndex])
            statusTip += " = {:0.2f} mSv/a".format(value / g.Sensitivity[TubeIndex] * g.ush2msa)  # ush2msa = 24 * 365.25 / 1000 = 8.772: conversion: µSv/h * 8.772 => mSv/a

            return statusTip


        def getVarText(selVar, selUnitYleft, svalue):
            """the text to show in the last variable field"""

            if selUnitYleft == "CPM":
                # selected unit is "CPM / CPS"
                varVal  = svalue
                varUnit = selVar[0:3]
                if  (isinstance(varVal, int) or varVal.is_integer()): dec = 0  # integer value - do only with CPX variables
                else:                                                 dec = 3  # T, P, H, X always with 3 decs

            else:
                # selected unit is "µSv/h"
                TubeIndex = getTubeIndex(selVar)
                if "M" in selVar: value = svalue         # CPM
                else:             value = svalue * 60    # CPS
                varVal  = value / g.Sensitivity[TubeIndex]
                varUnit = "µSv/h"
                dec     = 3

            return "{} {}".format(customformat(varVal, 7, dec), varUnit)

        ### end local defs ################################################################################

        defname = "updateDisplaySelectedVariable: "

        if g.lastLogValues is None:
            self.labelSelVar.setText(" --- ")
            addMenuTip(self.labelSelVar, "Shows Last Value of the Selected Variable when logging")
            return

        if g.activeDataSource == "His":
            # when not logging or His data: dark.grey on grey
            self.labelSelVar.setText(" --- ")
            self.labelSelVar.setStyleSheet('color:darkgray;')
            addMenuTip(self.labelSelVar, "No Values shown for His Data")

        elif g.activeDataSource == "Log" and g.logging:
            # when logging: black on yellow background
            self.labelSelVar.setStyleSheet('color: black; background-color: #F4D345;')

            selVar        = self.select.currentText()       # selected variable
            selUnitYleft  = self.yunit .currentText()       # selected Unit "CPM / CPS" or "µSv/h"
            selUnitYright = self.y2unit.currentText()       # selected Unit "°C" or "°F" for Temp only
            varText       = " --- "

            value         = g.lastLogValues[selVar]
            statusTip     = ""
            if not np.isnan(value):                         # on NAN no update, keep the old value

                if selVar in ['CPM', 'CPS', 'CPM1st', 'CPS1st', 'CPM2nd', 'CPS2nd', 'CPM3rd', 'CPS3rd']:
                    varText   = getVarText      (selVar, selUnitYleft, value)
                    statusTip = getStatusTip    (selVar, value)

                elif selVar == "Temp":
                    fvalue = value / 5 * 9 + 32 # convert °C to °F
                    if selUnitYright == "°C":  varText = "{:<10.6g} °C" .format(value)
                    else:                      varText = "{:<10.6g} °F" .format(fvalue)
                    statusTip = "{:<10.6g}°C = {:<10.6g}°F"             .format(value, fvalue)

                elif selVar == "Press":
                    varText   = "{:<10.6g}hPa"                          .format(value)
                    statusTip = "{:<10.6g}hPa = {:<10.6g}mbar"          .format(value, value)

                elif selVar == "Humid":
                    varText   = "{:<10.6g}%RH"                          .format(value)
                    statusTip = "{:<10.6g}%RH"                          .format(value)

                elif selVar == "Xtra":
                    varText   = "{:<10.6g}"                             .format(value)
                    statusTip = "{:<10.6g}"                             .format(value)

            self.labelSelVar.setText(varText)
            addMenuTip(self.labelSelVar, statusTip)


#
# Update the Display-Last-Values Window
#
    def updateDisplayLastValuesWindow(self):
        """
        update: the values in Value and Graph
                the text for Variable, Device, Comment is filled in at creation of window
                see function: displayLastValuesWindow() in gsup_tools.py for the creation of the window
        return: nothing
        """

        defname = "updateDisplayLastValuesWindow: "

        if g.displayLastValsIsOn:
            for vname in g.VarsCopy:
                lastval = g.lastLogValues[vname]
                # rdprint(defname, "vname: {:6s}  lastval: {}".format(vname, lastval))

                textvvalue  = "not mapped"
                textsvvalue = "not mapped"
                total       = 7
                dec         = 3

                if       g.logging and g.varsSetForLog[vname]:
                    vsheet  = "QLabel {background-color:#F4D345; color:black; }" # black on yellow
                    svsheet = "QLabel {background-color:#F4D345; color:black; }" # black on yellow
                elif not g.logging and g.varsSetForLog[vname]:
                    vsheet  = "QLabel {color:darkgray; }"                        # darkgrey on light grey
                    svsheet = "QLabel {color:darkgray; }"                        # darkgrey on light grey
                else:
                    vsheet  = "QLabel {color:darkgray; font-size:14px;}"         # darkgrey on light grey and in smaller size letters
                    svsheet = "QLabel {color:darkgray; font-size:14px;}"         # darkgrey on light grey and in smaller size letters

                if g.varsSetForLog[vname]:
                    # rdprint(defname, "g.varsSetForLog[vname]: true")
                    try:
                        if np.isnan(lastval):
                            # is nan
                            textvvalue      = "---"
                            if g.GraphScale[vname].upper().strip() in ("VAL", ""):      # same as Value
                                textsvvalue = "same"
                                # svsheet = "QLabel {color:darkgray; font-size:20px;}"    # darkgrey on light grey and in medium size letters
                                svsheet = "QLabel {color:darkgray; font-size:16px;}"    # darkgrey on light grey and in medium size letters
                            else:
                                textsvvalue = "---"

                        else:
                            # is not nan
                            if  ("CP" in vname) and (isinstance(lastval, int) or lastval.is_integer()): dec = 0  # integer value - do only with CPX variables
                            else:                                                                       dec = 3  # T, P, H, X always with 3 decs
                            textvvalue = customformat(lastval, total, dec)

                            if g.GraphScale[vname].upper().strip() in ("VAL", ""): # same as Value
                                textsvvalue = "same"
                                # svsheet     = "QLabel {color:darkgray; font-size:20px;}"         # darkgrey on light grey and in smaller size letters
                                svsheet     = "QLabel {color:darkgray; font-size:16px;}"         # darkgrey on light grey and in smaller size letters
                            else:
                                # svvalue     = applyValueFormula(vname, lastval, g.GraphScale[vname])
                                svvalue     = applyGraphFormula(vname, lastval, g.GraphScale[vname])
                                if  ("CP" in vname) and (isinstance(svvalue, int) or svvalue.is_integer()): dec = 0  # integer value - do only with CPX variables
                                else:                                                                       dec = 3  # T, P, H, X always with 3 decs
                                textsvvalue = customformat(svvalue, total, dec)

                            # rdprint("updateDisplayLastValuesWindow: lastval: {}  dec: {}  textsvvalue: {}".format(lastval, dec, textsvvalue))

                    except Exception as e:
                        exceptPrint(e, defname)

                # rdprint(defname, "self.vlabels: ", self.vlabels)
                # rdprint(defname, "self.svlabels: ", self.svlabels)
                try:
                    self.vlabels [vname] .setText(textvvalue)
                    self.svlabels[vname] .setText(textsvvalue)

                    self.vlabels [vname] .setStyleSheet(vsheet)
                    self.svlabels[vname] .setStyleSheet(svsheet)

                except Exception as e:
                    exceptPrint(e, defname + "vname: {}".format(vname))


#
# Get QuickLog file
#
    def quickLog(self):
        """Starts logging with empty default log file 'default.log'"""

        defname = "quickLog: "
        dprint(defname)
        setIndent(1)

        fprint(header("Quick Log"))
        msg = "Start logging using Quick Log database 'default.logdb'"
        fprint(msg)
        # gdprint(defname + msg)
        # setIndent(1)

        # set up default.logdb
        g.logDBPath = os.path.join(g.dataDir, "default.logdb")
        gsup_sql.DB_deleteDatabase("Log", g.logDBPath)     # close any existing db, and then delete file
        self.getFileLog(defaultLogDBPath=g.logDBPath)      # make a new one

        setIndent(0)
        self.startLogging()


#
# Get Log file
#
    def getFileLog(self, defaultLogDBPath=False, source="Database"):
        """Load existing file for logging, or create new one.
        source can be:
        - "Database" (which is *.logdb file )
        - "CSV File" (which is any csv file)
        """

        defname = "getFileLog: "
        dprint(defname)
        setIndent(1)

        #
        # Get logfile filename/path
        #
        # If a default logfile is given; use it
        if defaultLogDBPath != False:
            g.logFilePath      = None
            g.logDBPath        = defaultLogDBPath
            cdprint(defname, "using defaultLogDBPath: ", g.logDBPath)

        # else run dialog to get one
        else:
            if   source == "Database":
                # may use existing or new .logdb file, but must be allowed to overwrite this file;
                # an existing logdb file allows appending with new data
                dlg=QFileDialog(caption= "Get Log - Enter New Filename or Select from Existing", options=QFileDialog.DontUseNativeDialog)
                # dlg=QFileDialog(caption= "Get Log - Enter New Filename or Select from Existing")
                dlg.setFileMode(QFileDialog.AnyFile)
                dlg.setNameFilter("Log Files (*.logdb)")  # do NOT allow to load other files, in particular not *.hisdb files!

            elif source == "CSV File":
                # there must be an existing, readable csv file; the csv file will remain unchanged
                dlg=QFileDialog(caption = "Get Log - Select from Existing CSV File", options=QFileDialog.DontUseNativeDialog)
                # dlg=QFileDialog(caption = "Get Log - Select from Existing CSV File")
                dlg.setFileMode(QFileDialog.ExistingFile)
                dlg.setNameFilter("Log Files (*.log *.csv *.txt *.notes);;Any Files (*)")

            else:
                printProgError("undefined source:", source)

            dlg.setViewMode(QFileDialog.Detail)
            dlg.setWindowIcon(self.iconGeigerLog)
            dlg.setDirectory(g.fileDialogDir)

            dlg.setFixedSize(950, 550)

            # Execute dialog
            if dlg.exec() == QDialog.Accepted:  pass     # QDialog Accepted
            else:                               return   # QDialog Rejected

        ### end filedialog -  a file was selected

            g.fileDialogDir = dlg.directory().path()
            # print("dlg.directory().path():", dlg.directory().path())

            fnames      = dlg.selectedFiles()
            fname       = str(fnames[0])                    # file path
            fext        = os.path.splitext(fname)[1]        # file extension
            fname_base  = os.path.splitext(fname)[0]        # file basename with path w/o ext

            if   source == "Database":  # extension is .logdb
                g.logFilePath = None
                if fext != ".logdb":    g.logDBPath   = fname + ".logdb" # file has any extension or none
                else:                   g.logDBPath   = fname            # file already has .logdb extension

            elif source == "CSV File":  # extension is .log, .csv, .txt
                g.logFilePath = fname
                g.logDBPath   = fname_base + ".logdb"
                if not isFileReadable (g.logFilePath):   return

            if source == "Database":
                # if file exists, give warning on overwriting
                if os.path.isfile(g.logDBPath):
                    msg = QMessageBox()
                    msg.setIcon(QMessageBox.Warning)
                    msg.setWindowTitle("CAUTION")
                    critical  = """You selected an existing file, which will be modified \
                                when logging by <b>APPENDING</b> new data to it.
                                <br><br>Please confirm with OK.
                                <br><br>Otherwise click Cancel and enter a new filename in the Get Log dialog."""
                    msg.setText(critical)
                    msg.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
                    msg.setDefaultButton(QMessageBox.Cancel)

                    msg.setEscapeButton(QMessageBox.Cancel)
                    retval = msg.exec()

                    if retval != 1024:
                        return

        # Done getting LogFile   ##############################################

        self.setBusyCursor()

        g.currentDBPath = g.logDBPath
        g.autoLogFile   = g.logDBPath

### testing
### uncomment the following
# ######################################################
#         # does this interfere with His????
#         # scheint ok, hilft aber nicht on var use

        g.logTime             = None                 # array: Time data from total file
        g.logTimeDiff         = None                 # array: Time data as time diff to first record in days
        g.logTimeFirst        = None                 # value: Time of first record of total file

        g.logTimeSlice        = None                 # array: selected slice out of logTime
        g.logTimeDiffSlice    = None                 # array: selected slice out of logTimeDiff
        g.logSliceMod         = None

        g.sizePlotSlice       = None                 # value: size of plotTimeSlice

        g.logDBData           = None                 # 2dim numpy array with the log data
        g.hisDBData           = None                 # 2dim numpy array with the his data
        g.currentDBData       = None                 # 2dim numpy array with the currently plotted data

# ######################################################
### end testing


        fprint(header("Get Log"))
        fprint("Log Database: {}".                           format(g.logDBPath))
        if defaultLogDBPath == False: cdprint("getFileLog: use selected Log DB file: '{}'". format(g.logDBPath))
        QtUpdate()

        # setIndent(1)

        dprint(defname, "g.logFilePath:     ", g.logFilePath)
        dprint(defname, "g.logDBPath:       ", g.logDBPath)
        dprint(defname, "g.currentDBPath:   ", g.currentDBPath)

        if g.logging:   self.stopLogging()
        self.dcfLog.setText(g.logDBPath)
        self.clearLogPad()

        g.varsSetForLog            = g.varAllFalse.copy()
        g.varChecked4PlotLog       = g.varAllFalse.copy()  # is variable checked for showing in plot for Log

        # an existing classic log was selected. It will be converted to a database;
        # any previous conversion will be deleted first
        if g.logFilePath is not None:
            fprint("Created from file {}".format(g.logFilePath))
            # delete old database
            gsup_sql.DB_deleteDatabase("Log", g.logDBPath)

            # open new database
            g.logConn      = gsup_sql.DB_openDatabase(g.logConn, g.logDBPath)

            # read data from CSV file into database
            self.setNormalCursor()

            if gsup_sql.getCSV(g.logFilePath):
                self.setBusyCursor()
                gsup_sql.DB_convertCSVtoDB(g.logConn, g.logFilePath)
            else:
                fprint("Database creation was cancelled")
                return


        # a database file was selected
        else:
            if not os.path.isfile(g.logDBPath):
                # Database File does NOT exist; create new one

                # fprint("LogFile newly created - available for writing")

                # linfo = "LogFile newly created as '{}'".format(os.path.basename(g.logDBPath))
                # logPrint("#HEADER , {}, ".format(stime()) + linfo)

                # # open new database
                # g.logConn      = gsup_sql.DB_openDatabase(g.logConn, g.logDBPath)

                # ctype       = "HEADER"
                # cJulianday  = getTimeJulian()
                # cinfo       = linfo
                # gsup_sql.DB_insertComments(g.logConn, [[ctype, cJulianday, cinfo]])

                # # data array for the variables
                # g.logDBData = np.empty([0, g.datacolsDefault])
                # # edprint(defname + "g.logDBData empty: ", g.logDBData)


                # open new database
                g.logConn      = gsup_sql.DB_openDatabase(g.logConn, g.logDBPath)

                # create data array for the variables
                g.logDBData = np.empty([0, g.datacolsDefault])

                # create file comment and save to db
                cinfo = "Log Database created as '{}'".format(os.path.basename(g.logDBPath))
                fprint(cinfo)
                logPrint("#HEADER , {}, ".format(stime()) + cinfo)
                ctype       = "HEADER"
                cJulianday  = getTimeJulian()
                # cinfo       = linfo
                gsup_sql.DB_insertComments(g.logConn, [[ctype, cJulianday, cinfo]])

                # create version comment and save to db
                cinfo = "GeigerLog: {}; Python: {}.{}.{}".format(g.__version__, *sys.version_info)
                fprint(cinfo)
                logPrint("#HEADER , {}, ".format(stime()) + cinfo)
                # ctype       = "HEADER"
                # cJulianday  = getTimeJulian()
                # cinfo       = linfo
                gsup_sql.DB_insertComments(g.logConn, [[ctype, cJulianday, cinfo]])

            else:
                # Database File does exist
                if os.access(g.logDBPath, os.W_OK):
                    fprint("LogFile opened - available for writing")                # Database File does exist and can read and write
                elif os.access(g.logDBPath, os.R_OK):
                    efprint("LogFile opened - WARNING: available ONLY FOR READING") # DB File does exist but can read only

                g.logConn    = gsup_sql.DB_openDatabase  (g.logConn, g.logDBPath)

        ## end of else ##############
        # bip()
        g.logDBData, varsFromDB = gsup_sql.getDataFromDatabase("Log")               # this reads the all data in one go; no increments for progress bar
        # bip()
        g.varsSetForLog = g.varsSetForLogNew.copy()                                 # reset to default device dependent setting
        for vname in g.VarsCopy:
            if varsFromDB[vname]: g.varsSetForLog[vname] = True                     # this adds vars from DEB which are no longer active!
            if g.varsSetForLog[vname]: g.varChecked4PlotLog[vname] = True

        # set the Log Cycle as read from the database (if present)
        DefLogCycle = gsup_sql.DB_readLogcycle(g.logConn)                           # DefLogCycle is type float
        #print("Default LogCycle:",DefLogCycle, type(DefLogCycle))
        if DefLogCycle is None:                                                     # old DB may not have one
            gsup_sql.DB_insertLogcycle(g.logConn, g.LogCycle)
        else:
            g.LogCycle = DefLogCycle
            self.showTimingSetting(g.LogCycle)

        self.plotGraph("Log")
        self.checkLoggingState()
        self.setNormalCursor()

        setIndent(0)


#
# Show data from Log, His, and Bin files ######################################
#
    def showData(self, dataSource=None, full=True):
        """Print Log or His Data to notepad, as full file or excerpt.
        dataSource can be 'Log', 'His', 'HisBin' (for binary data), HisParse, or PlotData"""

        # print("showData dataSource: {}, fullflag: {}".format(dataSource, full))
        if dataSource is None:
            if    g.activeDataSource == "Log": dataSource = "Log"
            else:                              dataSource = "His"
        # print("\n\nshowData dataSource: {}, fullflag: {}".format(dataSource, full))

        if g.activeDataSource is None:
            self.showStatusMessage("No data available")
            return

        textprintButtonDef  = "Data"
        textprintButtonStop = "STOP"

        # stop printing
        if self.btnPrintFullData.text() == textprintButtonStop:
            g.stopPrinting = True
            # print("g.stopPrinting: ", g.stopPrinting)
            return

        if full:
            # switch button mode to "STOP"
            self.btnPrintFullData.setStyleSheet('QPushButton {color: blue; background-color:white; font:bold;}')
            self.btnPrintFullData.setText(textprintButtonStop)

        if   dataSource == "Log":          self.showDBData(DBtype="Log",     DBpath=g.logDBPath, DBconn=g.logConn, varchecked=g.varsSetForLog, full=full)
        elif dataSource == "His":          self.showDBData(DBtype="History", DBpath=g.hisDBPath, DBconn=g.hisConn, varchecked=g.varsSetForHis, full=full)
        elif dataSource == "HisBin":       gsup_sql.createLstFromDB(full=full)
        elif dataSource == "HisParse":     gsup_sql.createParseFromDB(full=full)
        elif dataSource == "PlotData":     gsup_tools.fprintPlotData()              # print data as shown in plot

        # reset button to default
        self.btnPrintFullData.setStyleSheet('QPushButton {font-size:11px;}')
        self.btnPrintFullData.setText(textprintButtonDef)


    def showDBData(self, DBtype=None, DBpath=None, DBconn=None, varchecked=None, full=True):
        """ print logged data from Log or Hist to notepad"""

        defname = "showDBData: "

        if DBconn is None:
            self.showStatusMessage("No data available")
            return

        self.setBusyCursor()

        if full:    addp = ""
        else:       addp = " Excerpt"
        fprint(header("Show {} Data".format(DBtype) + addp))
        fprint("from: {}\n".format(DBpath))

        sql, ruler = gsup_sql.getShowCompactDataSql(varchecked)

        fprint(ruler)
        # dprint(defname + "ruler: ", ruler)

        if full:
            data = gsup_sql.DB_readData(DBconn, sql, limit=0)
            # ### testing
            # for a in data:   print(defname + "sql dataline:", a)
            # ###

            counter      = 0
            counter_max  = 100
            update       = 900
            update_max   = 1000
            datastring   = ""
            g.stopPrinting = False
            for a in data:
                datastring += a + "\n"
                if counter >= counter_max:
                    fprint(datastring[:-1])
                    fprint(ruler)
                    datastring = ""
                    counter    = 0

                if update >= update_max:
                    QtUpdate()
                    update = 0

                if g.stopPrinting: break
                counter     += 1
                update      += 1

            g.stopPrinting = False
            fprint(datastring[:-1])

        else:
            fprint(self.getExcerptLines(sql, DBconn))

        fprint(ruler)

        self.setNormalCursor()


    def showDBTags(self, DBtype=None):
        """print comments from DB, either DBtype=Log or =History"""

        if DBtype == "Log":
            DBConn = g.logConn
            DBPath = g.logDBPath
        else:   # "History"
            DBConn = g.hisConn
            DBPath = g.hisDBPath

        if DBConn is None:
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

        if DB_Conn is None:  return ""

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

        defname = "printNotePad: "

        if g.currentDBPath is None: defaultOutputFile = os.path.join(g.dataDir, "notepad.pdf")
        else:                            defaultOutputFile = g.currentDBPath + '.pdf'
        # vprint(defname + "default output file:", defaultOutputFile)

        myprinter = QPrinter()
        myprinter.  setOutputFormat(QPrinter.PdfFormat)
        myprinter.  setOutputFileName(defaultOutputFile)

        dialog = QPrintDialog(myprinter, self)
        dialog.setOption(QAbstractPrintDialog.PrintToFile, on=True)

        if dialog.exec():
            mydoc = self.notePad.document()
            mydoc.print(dialog.printer())

# tubes
    def setTemporaryTubeSensitivities(self):
        """Dialog to set tube sensitivities for all tubes temporarily"""

        ### local defs ###################################################
        def printTubeSensitivities(errmsg=""):
            """Print a list of Tube sensitivities to terminal and notepad"""

            msgfmt = "{:30s}{}"
            msg  = msgfmt.format("Tube CPM/CPS:",       "{} CPM / (µSv/h)\n" .format(g.Sensitivity[0]))
            msg += msgfmt.format("Tube CPM1st/CPS1st:", "{} CPM / (µSv/h)\n" .format(g.Sensitivity[1]))
            msg += msgfmt.format("Tube CPM2nd/CPS2nd:", "{} CPM / (µSv/h)\n" .format(g.Sensitivity[2]))
            msg += msgfmt.format("Tube CPM3rd/CPS3rd:", "{} CPM / (µSv/h)\n" .format(g.Sensitivity[3]))

            fprint(header("Set Geiger Tube Sensitivities"))
            if errmsg > "": efprint(errmsg)
            fprint(msg)
            print(msg)

        ### end local defs ###################################################

        defname = "setTemporaryTubeSensitivities: "
        vprint(defname)

        if g.DevicesConnected == 0:
            printTubeSensitivities(errmsg = "Tube Sensitivities can only be configured after devices are connected!")
            return

        setIndent(1)

    # Comment
        intro = """
            <p>Allows to set the sensitivities for all Geiger tubes.
            <p>This is temporary for this run only. For a permanent change edit the GeigerLog configuration file 'geigerlog.cfg'.</p>
            <p>Find more details in chapter <b>Appendix G – Calibration</b> of the GeigerLog manual.</p>
            <p>Sensititivities are in units of <b>CPM / (µSv/h) </b>.
            """

    # Intro
        lcomment = QLabel(intro)
        lcomment.setMaximumWidth(400)
        lcomment.setMinimumWidth(390)
        lcomment.setWordWrap(True)

    # Def tube
        ltubeDef = QLabel("CPM / CPS  ")
        ltubeDef.setAlignment(Qt.AlignLeft)

        etubeDef = QLineEdit()
        etubeDef.setToolTip('Code: M / S')
        etubeDef.setText("{:0.6g}".format(g.Sensitivity[0]))
        # etubeDef.setText("{}".format(TubeSens[0]))

    # 1st tube
        ltube1st = QLabel("CPM1st / CPS1st")
        ltube1st.setAlignment(Qt.AlignLeft)

        etube1st = QLineEdit()
        etube1st.setToolTip('Code: M1 / S1')
        etube1st.setText("{:0.6g}".format(g.Sensitivity[1]))
        # etube1st.setText("{}".format(TubeSens[1]))

    # 2nd tube
        ltube2nd = QLabel("CPM2nd / CPS2nd  ")
        ltube2nd.setAlignment(Qt.AlignLeft)

        etube2nd = QLineEdit()
        etube2nd.setToolTip('Code: M2 / S2')
        etube2nd.setText("{:0.6g}".format(g.Sensitivity[2]))
        # etube2nd.setText("{}".format(TubeSens[2]))

    # 3rd tube
        ltube3rd = QLabel("CPM3rd / CPS3rd  ")
        ltube3rd.setAlignment(Qt.AlignLeft)

        etube3rd = QLineEdit()
        etube3rd.setToolTip('Code: M3 / S3')
        etube3rd.setText("{:0.6g}".format(g.Sensitivity[3]))
        # etube3rd.setText("{}".format(TubeSens[3]))

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
            vprint(defname + "CANCEL clicked, Sensitivities unchanged")

        else:
            # OK
            # fprint(header("Set Geiger Tube Sensitivities"))
            try:        ftubeDef = float(etubeDef.text().replace(",", "."))
            except:     ftubeDef = g.NAN
            try:        ftube1st = float(etube1st.text().replace(",", "."))
            except:     ftube1st = g.NAN
            try:        ftube2nd = float(etube2nd.text().replace(",", "."))
            except:     ftube2nd = g.NAN
            try:        ftube3rd = float(etube3rd.text().replace(",", "."))
            except:     ftube3rd = g.NAN
            # rdprint(defname, "ftube*: {}  {}  {}  {}  ".format(ftubeDef, ftube1st, ftube2nd, ftube3rd))

            badvalue = "Tube {:13s}: Bad Value, required is a numeric value > 0; you entered: '{}'"

            # to catch both zero values and bad entries
            if ftubeDef > 0:            g.Sensitivity[0] = ftubeDef
            else:                       efprint(badvalue.format("CPM/CPS", etubeDef.text()))

            if ftube1st > 0:            g.Sensitivity[1] = ftube1st
            else:                       efprint(badvalue.format("CPM1st/CPS1st", etube1st.text()))

            if ftube2nd > 0:            g.Sensitivity[2] = ftube2nd
            else:                       efprint(badvalue.format("CPM2nd/CPS2nd", etube2nd.text()))

            if ftube3rd > 0:            g.Sensitivity[3] = ftube3rd
            else:                       efprint(badvalue.format("CPM3rd/CPS3rd", etube3rd.text()))

            printTubeSensitivities()
            gsup_plot.makePlot()

        setIndent(0)


    def showDeviceMappings(self):
        """Shows active devices and variables mapped to them and alerts on
        variables being mapped to more than one device"""

        defname = "showDeviceMappings: "

        fprint(header("Device Mappings"))

        if g.DevicesConnected == 0:
            fprint("Unknown until a connection is made. Use menu: Device -> Connect Devices")
            return

        if g.DevicesConnected > 0 and g.varMapCountTotal == 0:
            efprint("<b>WARNING: </b>No mapped variables found although a device is connected.\
                     \nLogging will not be possible! Please check configuration if this is unexpected !")
            return

        fprint("Mappings as configured in GeigerLog's configuration file geigerlog.cfg.")

        BadMappingFlag = False
        for vname in g.VarsCopy:
            if g.varMapCount[vname] > 1:
                if BadMappingFlag == False:                                                         # print only on first occurence
                    qefprint("<b>WARNING: </b>Mapping problem of Variables")
                qefprint("Variable {:7s} {}".format(vname, "is mapped to more than one device"))
                BadMappingFlag = True

        dline = "{:11s}: {:4s} {:4s} {:6s} {:6s} {:6s} {:6s} {:6s} {:6s} {:5s} {:5s} {:5s} {:5s}"
        fprint("\n" + dline.format("Device", *list(g.VarsCopy)))
        fprint("-" * 86)
        for DevName in g.Devices:              # Device?
            checklist = []
            if g.Devices[DevName][g.ACTIV]:      # connected?
                checklist.append(DevName)
                for vname in g.VarsCopy:       # Var?
                    try:
                        if vname in g.Devices[DevName][g.VNAMES]: checklist.append("M")
                        else:                                   checklist.append("-")
                    except:
                        checklist.append("?")
                fprint(dline.format(*checklist))

        if BadMappingFlag:
            # Mapping is bad
            msg  = "<b>INFO: </b>"
            msg += "Measurements are made on devices from top to bottom, and for each from left to<br>"
            msg += "right. If double-mapping of variables occurs, then the last measured variable will<br>"
            msg += "overwrite the previous one, almost always resulting in useless data. "
            fprintInColor(msg, "blue")
            QtUpdate()
            burp()

        else:
            # Mapping is good
            fprintInColor("Mapping is valid", "green")
            QtUpdate()
            bip()


    def fprintDeviceInfo(self, DevName, extended=False):
        """prints basic / extended info on the device DevName"""
        # called ONLY from the menu or the device toolbar button

        defname = "fprintDeviceInfo: "
        dprint(defname + "DevName: {}  extended: {}".format(DevName, extended))
        setIndent(1)
        setBusyCursor()

        txt = DevName + " Device Info"
        if extended:  txt += " Extended"
        fprint(header(txt))

        if   DevName == "GMC"         : info = gdev_gmc         .getInfoGMC        (extended=extended)
        elif DevName == "Audio"       : info = gdev_audio       .getInfoAudio      (extended=extended)
        elif DevName == "IoT"         : info = gdev_iot         .getInfoIoT        (extended=extended)
        elif DevName == "RadMon"      : info = gdev_radmon      .getInfoRadMon     (extended=extended)
        elif DevName == "AmbioMon"    : info = gdev_ambiomon    .getInfoAmbioMon   (extended=extended)
        elif DevName == "GammaScout"  : info = gdev_gammascout  .getInfoGammaScout (extended=extended)

        elif DevName == "I2C"         : info = gdev_i2c         .getInfoI2C        (extended=extended)
        elif DevName == "LabJack"     : info = gdev_labjack     .getInfoLabJack    (extended=extended)
        elif DevName == "Formula"     : info = gdev_formula     .getInfoFormula    (extended=extended)
        elif DevName == "MiniMon"     : info = gdev_minimon     .getInfoMiniMon    (extended=extended)
        elif DevName == "Manu"        : info = gdev_manu        .getInfoManu       (extended=extended)
        elif DevName == "WiFiClient"  : info = gdev_wificlient  .getInfoWiFiClient (extended=extended)
        elif DevName == "WiFiServer"  : info = gdev_wifiserver  .getInfoWiFiServer (extended=extended)

        elif DevName == "RaspiPulse"  : info = gdev_raspipulse  .getInfoRaspiPulse (extended=extended)
        elif DevName == "RaspiI2C"    : info = gdev_raspii2c    .getInfoRaspiI2C   (extended=extended)
        elif DevName == "SerialPulse" : info = gdev_serialpulse .getInfoSerialPulse(extended=extended)

        elif DevName == "RadPro"      : info = gdev_radpro      .getInfoRadPro     (extended=extended)

        else:                           info = "incorrect Device Name '{}'".format(DevName)

        fprint(info)
        cdprint(defname + "\n" + info)

        setNormalCursor()
        setIndent(0)


    def toggleDeviceConnection(self):
        """if no connection exists, then make connection else disconnect"""

        if g.logging:
            self.showStatusMessage("Cannot change when logging! Stop logging first")
            return

        if g.DevicesConnected == 0:    self.switchAllDeviceConnections(new_connection="ON")
        else:                          self.switchAllDeviceConnections(new_connection="OFF")


    def switchAllDeviceConnections(self, new_connection="ON"):
        """
        if new_connection == ON:    if no connection exists, then try to make connection
                                    (with verification of communication with device)
        if new_connection == OFF:   if connection does exist, then disconnect
        """

        defname = "switchAllDeviceConnections: "

        if g.logging:
            self.showStatusMessage("Cannot change when logging! Stop logging first")
            return

        self.setBusyCursor()

        devs = ""
        for DevName in g.Devices:
            if g.Devices[DevName][g.ACTIV]: devs += DevName + ", "

        dprint(defname + "--> {}".format(new_connection), "   -   Active Devices to be switched: ", devs[:-2])
        setIndent(1)

        #
        # Connect / Dis-Connect all devices which are activated
        #
        for DevName in g.Devices:
            # rdprint(defname, "DevName: ", DevName)
            if g.Devices[DevName][g.ACTIV]:
                self.switchSingleDeviceConnection (DevName, new_connection=new_connection)
                QtUpdate()

        #
        # Print all Devices and their states
        #
        g.DevicesActivated = 0
        g.DevicesConnected = 0
        dprint(defname, "Final Device Status:")
        setIndent(1)
        for i, DevName in enumerate(g.Devices):
            DevVars      = g.Devices[DevName][g.VNAMES]          # list of var names with this device
            DevActvState = g.Devices[DevName][g.ACTIV]           # device activated?
            DevConnState = g.Devices[DevName][g.CONN]            # device connected?

            if DevActvState:  g.DevicesActivated += 1
            if DevConnState:  g.DevicesConnected += 1
            if DevVars is not None:    svs = ", ".join(DevVars)     # the variables
            else:                      svs = "None"
            coloruse = ""
            if DevConnState :                       coloruse = TGREEN
            if DevActvState and not DevConnState:   coloruse = BOLDRED

            dprint("   Device #{:<2d}: {:13s}  Activation: {:6s} Connection: {}{:6s}  Vars: {}".
                    format(i, DevName, str(DevActvState), coloruse, str(DevConnState), svs), TDEFAULT)

        dprint("   Devices Activated: {}".format(g.DevicesActivated))
        dprint("   Devices Connected: {}".format(g.DevicesConnected))
        setIndent(0)

        if g.DevicesActivated == 0:
            self.setNormalCursor()
            self.warnMissingDeviceActivations()

        #
        # set plug-icon green on at least 1 connected device
        #
        if g.DevicesConnected > 0: plugicon = 'icon_plug_closed.png'   # green icon
        else:                      plugicon = 'icon_plug_open.png'     # red icon
        self.toggleDeviceConnectionAction.setIcon(QIcon(QPixmap(os.path.join(g.resDir, plugicon))))

        #
        # determine the mapping and active variables on new connections
        #
        if new_connection == "ON" and g.DevicesConnected > 0:
            g.varMapCountTotal = 0
            for vname   in g.VarsCopy:  g.varMapCount[vname] = 0
            for DevName in g.Devices:   g.DevVarsAsText[DevName] = None

            # Scan all devices for loggable variables
            for DevName in g.Devices:                                       # scan all devices
                # rdprint("DevName: ", DevName)
                if g.Devices[DevName][g.VNAMES] is not None:                  # use only those with variables named
                    tmpDevVarsAsText = ""
                    for vname in g.Devices[DevName][g.VNAMES]:                # scan all vars of this device
                        # rdprint("                  : vname: ", vname)
                        if vname == "Unused" or vname == "auto" or vname == "None": continue
                        g.varMapCount[vname]   += 1
                        g.varMapCountTotal     += 1
                        tmpDevVarsAsText            += " {}".format(vname)  # like: CPM1st CPS1st CPM2nd ...
                        g.varsSetForLogNew[vname] = True                    # and mark them active for this log
                        g.varsSetForLog.update({vname : True})
                        g.varChecked4PlotLog   [vname] = True

                    g.DevVarsAsText[DevName] = tmpDevVarsAsText.strip()     # like: {'GMC': 'CPM1st CPS1st CPM2nd CPS2nd Humid', 'Audio': None,

            self.showDeviceMappings()

        # cleanup
        self.checkLoggingState()

        # finally set all tubes to default which have not been set by the devices themselves
        for i in range(0, 4):
            if g.Sensitivity[i] == "auto":    g.Sensitivity[i] = g.DefaultTubeSens[i] if g.TubeSensitivity[i] == "auto" else g.TubeSensitivity[i]

        dprint(defname, "Tube Sensitivities: ", g.Sensitivity)

        setIndent(0)
        self.setNormalCursor()

        dprint(TGREEN + "All qualifying Devices are connected " + "-" * 100 + TDEFAULT + "\n")


    def setStyleSheetTBButton(self, button, stylesheetflag):
        """set toolbar button of devices to grey, green, red, or yellow"""

        if   stylesheetflag == "ON"    : button.setStyleSheet(self.dbtnStyleSheetON)        # green
        elif stylesheetflag == "OFF"   : button.setStyleSheet(self.dbtnStyleSheetOFF)       # grey
        elif stylesheetflag == "ERR"   : button.setStyleSheet(self.dbtnStyleSheetError)     # red
        elif stylesheetflag == "SIM"   : button.setStyleSheet(self.dbtnStyleSheetSimul)     # yellow - simulation


    def initNamedDevice(self, DevName):
        """init the device DevName"""

        # NOTE: errmsg will be "" unless there was an error in an initXYZ

        defname = "initNamedDevice: " + DevName
        # dprint(defname)
        # setIndent(1)

        if   DevName == "GMC":          errmsg = gdev_gmc           .initGMC()
        elif DevName == "Audio":        errmsg = gdev_audio         .initAudio()
        elif DevName == "IoT":          errmsg = gdev_iot           .initIoT()
        elif DevName == "RadMon":       errmsg = gdev_radmon        .initRadMon()
        elif DevName == "AmbioMon":     errmsg = gdev_ambiomon      .initAmbioMon()
        elif DevName == "GammaScout":   errmsg = gdev_gammascout    .initGammaScout()
        elif DevName == "I2C":          errmsg = gdev_i2c           .initI2C()
        elif DevName == "LabJack":      errmsg = gdev_labjack       .initLabJack()
        elif DevName == "Formula":      errmsg = gdev_formula       .initFormula()
        elif DevName == "MiniMon":      errmsg = gdev_minimon       .initMiniMon()
        elif DevName == "Manu":         errmsg = gdev_manu          .initManu()
        elif DevName == "WiFiClient":   errmsg = gdev_wificlient    .initWiFiClient()
        elif DevName == "WiFiServer":   errmsg = gdev_wifiserver    .initWiFiServer()
        elif DevName == "RaspiPulse":   errmsg = gdev_raspipulse    .initRaspiPulse()
        elif DevName == "RaspiI2C":     errmsg = gdev_raspii2c      .initRaspiI2C()
        elif DevName == "SerialPulse":  errmsg = gdev_serialpulse   .initSerialPulse()
        elif DevName == "RadPro":       errmsg = gdev_radpro        .initRadPro()

        # rdprint(defname, "complete")
        # setIndent(0)

        return errmsg


    def terminateNamedDevice(self, DevName):
        """terminate the device DevName"""

        errmsg = "Error: Undefined"

        if   DevName == "GMC":          errmsg = gdev_gmc           .terminateGMC()
        elif DevName == "Audio":        errmsg = gdev_audio         .terminateAudio()
        elif DevName == "IoT":          errmsg = gdev_iot           .terminateIoT()
        elif DevName == "RadMon":       errmsg = gdev_radmon        .terminateRadMon()
        elif DevName == "AmbioMon":     errmsg = gdev_ambiomon      .terminateAmbioMon()
        elif DevName == "GammaScout":   errmsg = gdev_gammascout    .terminateGammaScout()
        elif DevName == "I2C":          errmsg = gdev_i2c           .terminateI2C()
        elif DevName == "LabJack":      errmsg = gdev_labjack       .terminateLabJack()
        elif DevName == "Formula":      errmsg = gdev_formula       .terminateFormula()
        elif DevName == "MiniMon":      errmsg = gdev_minimon       .terminateMiniMon()
        elif DevName == "Manu":         errmsg = gdev_manu          .terminateManu()
        elif DevName == "WiFiClient":   errmsg = gdev_wificlient    .terminateWiFiClient()
        elif DevName == "WiFiServer":   errmsg = gdev_wifiserver    .terminateWiFiServer()
        elif DevName == "RaspiPulse":   errmsg = gdev_raspipulse    .terminateRaspiPulse()
        elif DevName == "RaspiI2C":     errmsg = gdev_raspii2c      .terminateRaspiI2C()
        elif DevName == "SerialPulse":  errmsg = gdev_serialpulse   .terminateSerialPulse()
        elif DevName == "RadPro":       errmsg = gdev_radpro        .terminateRadPro()

        return errmsg

    # not in use
    def startDevices(self):
        """start all devices"""

        errmsg = "Error: Undefined"

        for DevName in g.Devices:
            if g.Devices[DevName][g.CONN]: # look only at connected devices; # Connection status: CONN = 3
                # devvars = g.Devices[DevName][g.VNAMES]    #  e.g. == ['CPM', 'T', 'X']

                # if   DevName == "GMC":          errmsg = gdev_gmc           .startGMC()
                # elif DevName == "Audio":        errmsg = gdev_audio         .startAudio()
                # elif DevName == "IoT":          errmsg = gdev_iot           .startIoT()
                # elif DevName == "RadMon":       errmsg = gdev_radmon        .startRadMon()
                # elif DevName == "AmbioMon":     errmsg = gdev_ambiomon      .startAmbioMon()
                # elif DevName == "GammaScout":   errmsg = gdev_gammascout    .startGammaScout()
                # elif DevName == "I2C":          errmsg = gdev_i2c           .startI2C()
                # elif DevName == "LabJack":      errmsg = gdev_labjack       .startLabJack()
                # elif DevName == "Formula":      errmsg = gdev_formula       .startFormula()
                # elif DevName == "MiniMon":      errmsg = gdev_minimon       .startMiniMon()
                # elif DevName == "Manu":         errmsg = gdev_manu          .startManu()
                # elif DevName == "WiFiClient":   errmsg = gdev_wificlient    .startWiFiClient()
                # elif DevName == "WiFiServer":   errmsg = gdev_wifiserver    .startWiFiServer()
                # elif DevName == "RaspiPulse":   errmsg = gdev_raspipulse    .startRaspiPulse()
                # elif DevName == "RaspiI2C":     errmsg = gdev_raspii2c      .startRaspiI2C()
                # elif DevName == "SerialPulse":  errmsg = gdev_serialpulse   .startSerialPulse()

                if DevName == "RaspiPulse":   errmsg = gdev_raspipulse    .startRaspiPulse()

        return errmsg


    # not in use
    def stopDevices(self):
        """stop all devices"""

        errmsg = "Error: Undefined"

        for DevName in g.Devices:
            if g.Devices[DevName][g.CONN]: # look only at connected devices; # Connection status: CONN = 3
                # devvars = g.Devices[DevName][g.VNAMES]    #  e.g. == ['CPM', 'T', 'X']

                # if   DevName == "GMC":          errmsg = gdev_gmc           .stopGMC()
                # elif DevName == "Audio":        errmsg = gdev_audio         .stopAudio()
                # elif DevName == "IoT":          errmsg = gdev_iot           .stopIoT()
                # elif DevName == "RadMon":       errmsg = gdev_radmon        .stopRadMon()
                # elif DevName == "AmbioMon":     errmsg = gdev_ambiomon      .stopAmbioMon()
                # elif DevName == "GammaScout":   errmsg = gdev_gammascout    .stopGammaScout()
                # elif DevName == "I2C":          errmsg = gdev_i2c           .stopI2C()
                # elif DevName == "LabJack":      errmsg = gdev_labjack       .stopLabJack()
                # elif DevName == "Formula":      errmsg = gdev_formula       .stopFormula()
                # elif DevName == "MiniMon":      errmsg = gdev_minimon       .stopMiniMon()
                # elif DevName == "Manu":         errmsg = gdev_manu          .stopManu()
                # elif DevName == "WiFiClient":   errmsg = gdev_wificlient    .stopWiFiClient()
                # elif DevName == "WiFiServer":   errmsg = gdev_wifiserver    .stopWiFiServer()
                # elif DevName == "RaspiPulse":   errmsg = gdev_raspipulse    .stopRaspiPulse()
                # elif DevName == "RaspiI2C":     errmsg = gdev_raspii2c      .stopRaspiI2C()
                # elif DevName == "SerialPulse":  errmsg = gdev_serialpulse   .stopSerialPulse()

                if DevName == "RaspiPulse":   errmsg = gdev_raspipulse    .stopRaspiPulse()

        return errmsg


    def setEnableDeviceActions(self, new_enable=True, device="", stylesheetflag="ON"):
        """Dis/Enable device specific device actions"""

        defname = "setEnableDeviceActions: "
        dprint(defname)
        setIndent(1)

        # Device
        self.DeviceConnectAction.        setEnabled(not new_enable)
        self.DeviceDisconnectAction.     setEnabled(new_enable)
        self.setLogTimingAction.         setEnabled(new_enable)

        # GMC counter
        if device == "GMC":
            if g.Devices["GMC"][g.CONN]:
                self.GMCInfoActionExt.       setEnabled(new_enable)
                self.GMCConfigMemoryAction.  setEnabled(new_enable)
                self.GMCConfigEditAction.    setEnabled(new_enable)
                self.GMCSetTimeAction.       setEnabled(new_enable)
                self.GMCEraseSavedDataAction.setEnabled(new_enable)
                self.GMCREBOOTAction.        setEnabled(new_enable)
                self.GMCFACTORYRESETAction.  setEnabled(new_enable)
                self.GMCONAction.            setEnabled(new_enable)
                self.GMCOFFAction.           setEnabled(new_enable)

                # # GMC Device functions using the config now
                # # replaced by setGMCconfiguration()
                # self.GMCSpeakerONAction.     setEnabled(new_enable)
                # self.GMCSpeakerOFFAction.    setEnabled(new_enable)
                # self.GMCAlarmONAction.       setEnabled(new_enable)
                # self.GMCAlarmOFFAction.      setEnabled(new_enable)
                # self.GMCSavingStateAction.   setEnabled(new_enable)

                #toolbar GMC Power Toggle
                self.dbtnGMCPower.           setEnabled(new_enable)
                self.setGMCPowerIcon(getconfig=True)

                # History
                self.histGMCDeviceAction.    setEnabled(new_enable)

            self.setStyleSheetTBButton(self.dbtnGMC, stylesheetflag)

        # AudioCounter
        elif device == "Audio":
            self.AudioInfoActionExt .setEnabled(new_enable)             # extended info
            self.AudioPlotAction    .setEnabled(new_enable)             # audio plotting
            self.AudioSignalAction  .setEnabled(new_enable)             # audio raw signal
            self.AudioEiaAction     .setEnabled(new_enable)             # audio eia action
            self.setStyleSheetTBButton(self.dbtnAudio, stylesheetflag)

        # SerialPulse device
        elif device == "SerialPulse":
            # self.AudioInfoActionExt .setEnabled(new_enable)           # extended info
            self.setStyleSheetTBButton(self.dbtnPulse, stylesheetflag)

        # IoT
        elif device == "IoT":
            self.IoTInfoActionExt.setEnabled(new_enable)                # enable extended info
            self.setStyleSheetTBButton(self.dbtnIoT, stylesheetflag)

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
            self.AmbioInfoActionExt.     setEnabled(new_enable)         # enable extended info
            self.setStyleSheetTBButton(self.dbtnAmbio, stylesheetflag)

        # Gamma-Scout counter
        elif device == "GammaScout":
            self.histGSDeviceAction.    setEnabled(new_enable)
            self.GSInfoActionExt.       setEnabled(new_enable)          # enable extended info
            self.GSResetAction.         setEnabled(new_enable)          # enable reset
            self.GSSetPCModeAction.     setEnabled(new_enable)          # enable PC Mode
            self.GSDateTimeAction.      setEnabled(new_enable)          # enable set DateTime
            if g.GS_DeviceDetected == "Online":
                self.GSSetOnlineAction. setEnabled(new_enable)          # enable Online mode
                self.GSRebootAction.    setEnabled(new_enable)          # enable Reboot
            else:
                self.GSSetOnlineAction.     setEnabled(False)           # set True if "online" device
                self.GSRebootAction.        setEnabled(False)           # or leave false
            self.setStyleSheetTBButton(self.dbtnGS, stylesheetflag)

        # I2C
        elif device == "I2C":                                           # I2C
            self.I2CInfoActionExt.          setEnabled(new_enable)      #   extended info
            self.I2CScanAction.             setEnabled(new_enable)      #   can scan only when not logging
            self.I2CForceCalibAction.       setEnabled(new_enable)      #   can calibrate only when not logging
            self.I2CResetAction.            setEnabled(new_enable)      #   can reset only when not logging
            # self.I2CSerialAction.           setEnabled(new_enable)    #   always enabled
            self.setStyleSheetTBButton(self.dbtnI2C, stylesheetflag)

        # LabJack
        elif device == "LabJack":
            self.LJInfoActionExt.setEnabled(new_enable)                 # enable extended info
            self.setStyleSheetTBButton(self.dbtnLJ, stylesheetflag)

        # MiniMon
        elif device == "MiniMon":
            self.setStyleSheetTBButton(self.dbtnMiniMon, stylesheetflag)

        # Formula
        elif device == "Formula":
            # self.FormulaSettings.setEnabled(new_enable)                # enable settings
            self.setStyleSheetTBButton(self.dbtnFormula, stylesheetflag)

        # Manu
        elif device == "Manu":
            # self.ManuInfoActionExt.setEnabled(new_enable)              # enable extended info
            self.ManuValAction.setEnabled(new_enable)                    # enable manual data entry
            self.setStyleSheetTBButton(self.dbtnManu, stylesheetflag)

        # WiFiServer
        elif device == "WiFiServer":
            # self.WiFiInfoActionExt.setEnabled(new_enable)              # enable extended info
            self.setStyleSheetTBButton(self.dbtnWServer, stylesheetflag)

        # WiFiClient
        elif device == "WiFiClient":
            # self.WiFiClientInfoActionExt.setEnabled(new_enable)        # enable extended info
            self.setStyleSheetTBButton(self.dbtnWClient, stylesheetflag)

        # RaspiPulse
        elif device == "RaspiPulse":
            self.RaspiPulseInfoActionExt.setEnabled(new_enable)          # enable extended info
            self.setStyleSheetTBButton(self.dbtnRPulse, stylesheetflag)

        # RaspiI2C
        elif device == "RaspiI2C":
            self.RaspiI2CInfoActionExt.setEnabled(new_enable)            # enable extended info
            self.RaspiI2CResetAction  .setEnabled(new_enable)            # enable reset
            self.setStyleSheetTBButton(self.dbtnRI2C, stylesheetflag)


        # Rad Pro
        elif device == "RadPro":
            self.RadProInfoExtAction.setEnabled(new_enable)              # enable extended info
            self.RadProSetTimeAction.setEnabled(new_enable)              # enable time setting
            self.RadProConfigAction .setEnabled(new_enable)              # enable config setting
            # self.histRadProLoadNewAction.setEnabled(new_enable)          # enable load new history
            self.histRadProLoadAllAction.setEnabled(new_enable)          # enable load history
            self.setStyleSheetTBButton(self.dbtnRadPro, stylesheetflag)

        setIndent(0)


    # GENERIC
    def switchSingleDeviceConnection(self, DevName, new_connection = "ON"):
        """generic handler for connections"""

        defname = "switchSingleDeviceConnection: "

        dprint(defname, "Device: {} --> {}. ".format(DevName, new_connection))
        setIndent(1)

        self.setBusyCursor()

        #
        # INIT
        #
        if new_connection == "ON":
            fprint(header("Connect {} Device".format(DevName)))
            QtUpdate()

            if g.Devices[DevName][g.CONN]:
                fprint("Already connected")
                self.fprintDeviceInfo(DevName)
            else:
                errmsg = self.initNamedDevice(DevName)
                if g.Devices[DevName][g.CONN]:
                    # successful connect
                    if   errmsg == "":    self.setEnableDeviceActions(new_enable = True, device=DevName, stylesheetflag="ON")
                    elif errmsg == "SIM": self.setEnableDeviceActions(new_enable = True, device=DevName, stylesheetflag="SIM")
                    fprintInColor("Device successfully connected", "green")
                    gdprint(defname + "New Status: ON: for device: '{}'".format(g.Devices[DevName][g.DNAME]))

                else:
                    # failure connecting
                    # rdprint(defname, "failure connecting")
                    self.setEnableDeviceActions(new_enable = False, device=DevName, stylesheetflag="ERR")
                    msg = "Failure connecting with Device: '{}' for reason:\n'{}'".format(DevName, str(errmsg)) # tuple of 2 parts
                    efprint(msg)
                    edprint(defname, "New Status: " + msg.replace("\n", " "))

        #
        # TERMINATE
        #
        else: # new_connection == OFF
            fprint(header("Disconnect {} Device".format(DevName)))
            if not g.Devices[DevName][g.CONN]:
                # is already de-connected
                fprint("No connected {} Device".format(DevName))
                self.setEnableDeviceActions(new_enable=False, device=DevName, stylesheetflag="OFF")

            else:
                # is connected; now deconnecting
                errmsg = self.terminateNamedDevice(DevName)
                if not g.Devices[DevName][g.CONN] :
                    # successful dis-connect
                    msg = "Device {} successfully disconnected".format(DevName)
                    fprint(msg)
                    gdprint(msg)
                    self.setEnableDeviceActions(new_enable=False, device=DevName, stylesheetflag="OFF")
                else:
                    # failure dis-connecting
                    self.setEnableDeviceActions(new_enable=False, device=DevName, stylesheetflag="ERR")
                    efprint("Failure disconnecting:", "'{}'".format(g.Devices[DevName][0] ), debug=True)
                    qefprint(errmsg)
                    edprint(errmsg)

        self.setNormalCursor()
        setIndent(0)


    def checkLoggingState(self):
        """enabling and disabling menu and toolbar entries"""

        defname = "checkLoggingState: "
        dprint(defname)
        setIndent(1)

        # Logging
        if g.logging:
            self.logLoadFileAction.             setEnabled(False)  # no loading of log files during logging
            self.logLoadCSVAction .             setEnabled(False)  # no loading of CSV log files during logging
            self.startloggingAction.            setEnabled(False)  # no start logging - it is running already
            self.stoploggingAction.             setEnabled(True)   # stopping is possible
            self.quickLogAction.                setEnabled(False)  # no quickstart of logging - it is running already
            self.logSnapAction.                 setEnabled(True)   # snaps are possible only during logging

            if g.Devices["GMC"][g.ACTIV]:                          # GMC
                self.histGMCDeviceAction.       setEnabled(False)  #   no downloads during logging

              # self.GMCInfoActionExt.          setEnabled(False)  #
                self.GMCInfoActionExt.          setEnabled(True)   #
                self.GMCConfigEditAction.       setEnabled(False)  #
                self.GMCConfigMemoryAction.     setEnabled(False)  #
                self.GMCSetTimeAction.          setEnabled(False)  #
                self.GMCEraseSavedDataAction.   setEnabled(False)  #
                self.GMCREBOOTAction.           setEnabled(False)  #
                self.GMCFACTORYRESETAction.     setEnabled(False)  #
                self.GMCONAction.               setEnabled(False)
                self.GMCOFFAction.              setEnabled(False)
                self.GMCSerialAction.           setEnabled(False)  #


            if g.Devices["Audio"][g.ACTIV]:                        # Audio is activated; may NOT be connected
                self.AudioInfoActionExt.        setEnabled(True)   #
                self.AudioSignalAction.         setEnabled(False)  # audio raw signal
                self.AudioPlotAction.           setEnabled(False)
                self.AudioEiaAction.            setEnabled(False)  # audio eia action


            if g.Devices["GammaScout"][g.ACTIV]:                   # GammaScout
                self.histGSDeviceAction.        setEnabled(False)  #   no downloads during logging
                self.GSSerialAction.            setEnabled(False)  #   no serial port settings during logging

                self.GSResetAction.             setEnabled(False)  #   disable reset
                self.GSSetPCModeAction.         setEnabled(False)  #   disable PC Mode
                self.GSDateTimeAction.          setEnabled(False)  #   disable set DateTime
                self.GSSerialAction.            setEnabled(False)  #


            if g.Devices["AmbioMon"][g.ACTIV]:                     # AmbioMon
                self.histAMDeviceCAMAction.     setEnabled(False)  #   no downloads during logging
                self.histAMDeviceCPSAction.     setEnabled(False)  #   no downloads during logging


            if g.Devices["I2C"][g.ACTIV] :                         # I2C - Activated
                self.I2CScanAction.             setEnabled(False)  #   can scan only when not logging
                self.I2CForceCalibAction.       setEnabled(False)  #   can calibrate only when not logging
                self.I2CResetAction.            setEnabled(False)  #   can reset only when not logging
                self.I2CSerialAction.           setEnabled(False)  #


            if g.Devices["RadPro"][g.ACTIV] and g.Devices["RadPro"][g.CONN]: # RadPro
                # self.histRadProLoadNewAction.   setEnabled(False)  #   cannot download while logging
                self.histRadProLoadAllAction.   setEnabled(False)  #   dito
                self.RadProSetTimeAction.       setEnabled(False)  #   enable time setting
                self.RadProInfoExtAction.       setEnabled(False)  #   enable extended info
                self.RadProConfigAction.        setEnabled(False)  #   enable config setting


            if g.Devices["Manu"][g.ACTIV] :                        # Manu - Activated
                self.ManuValAction.             setEnabled(True)   #   can enter data only when logging

        # Not Logging
        else:
            self.logLoadFileAction.             setEnabled(True)   # can load log files
            self.logLoadCSVAction.              setEnabled(True)   # can load CSV log files
            self.startloggingAction.            setEnabled(True)   # can start logging (GMC powering need will be excluded later)
            self.stoploggingAction.             setEnabled(False)  # cannot stop - it is not running
            self.quickLogAction.                setEnabled(True)   # quickstart is possible (GMC powering need will be excluded later)
            self.logSnapAction.                 setEnabled(False)  # cannot take snaps when not logging

            if g.Devices["GMC"][g.ACTIV] \
                and g.Devices["GMC"][g.CONN]:                      # GMC - Activated AND Connected

                self.histGMCDeviceAction.       setEnabled(True)   #   can download from device when not logging even if powered off

                if gdev_gmc.isGMC_PowerOn(getconfig=True) == "OFF"\
                   and g.DevicesConnected == 1:                    #   GMC is NOT powered ON and is only device
                    self.startloggingAction.    setEnabled(False)  #   cannot start logging without power and no other devices connected
                    self.quickLogAction.        setEnabled(False)  #   quickstart is NOT possible without power and no other devices connected

                self.GMCInfoActionExt.          setEnabled(True)   #
                self.GMCConfigEditAction.       setEnabled(True)   #
                self.GMCConfigMemoryAction.     setEnabled(True)   #
                self.GMCSetTimeAction.          setEnabled(True)   #
                self.GMCEraseSavedDataAction.   setEnabled(True)   #
                self.GMCREBOOTAction.           setEnabled(True)   #
                self.GMCFACTORYRESETAction.     setEnabled(True)   #
                self.GMCSerialAction.           setEnabled(True)   #
                self.GMCONAction.               setEnabled(True)   #   switch power on
                self.GMCOFFAction.              setEnabled(True)   #   switch power off

            if g.Devices["Audio"][g.ACTIV]:                        # Audio is activated; may NOT be connected
                self.AudioInfoActionExt.        setEnabled(True)   #
                self.AudioSignalAction.         setEnabled(True)   # audio raw signal
                self.AudioPlotAction.           setEnabled(True)
                self.AudioEiaAction.            setEnabled(True)   # audio eia action

            if g.Devices["GammaScout"][g.ACTIV]:                   # GammaScout is activated; may NOT be connected
                self.GSSerialAction.            setEnabled(True)   #

            if g.Devices["GammaScout"][g.ACTIV] and g.Devices["GammaScout"][g.CONN]: # GammaScout - is activated AND Connected
                self.histGSDeviceAction.        setEnabled(True)   #   can download from device when not logging
                self.GSResetAction.             setEnabled(True)   #   enable reset
                self.GSSetPCModeAction.         setEnabled(True)   #   enable PC Mode
                self.GSDateTimeAction.          setEnabled(True)   #   enable set DateTime
                self.GSSerialAction.            setEnabled(True)   #

            if g.Devices["AmbioMon"][g.ACTIV]:                     # AmbioMon
                self.histAMDeviceCAMAction.     setEnabled(True)   #   can download from device when not logging
                self.histAMDeviceCPSAction.     setEnabled(True)   #   can download from device when not logging

            if g.Devices["I2C"][g.ACTIV] and g.Devices["I2C"][g.CONN]: # I2C - Activated AND Connected:
                self.I2CScanAction.             setEnabled(True)   #   can scan only when not logging AND connected
                self.I2CForceCalibAction.       setEnabled(True)   #   can calibrate only when not logging AND connected
                self.I2CResetAction.            setEnabled(True)   #   can reset only when not logging AND connected
                self.I2CSerialAction.           setEnabled(True)   #   can set serial when Activated


            if g.Devices["RadPro"][g.ACTIV] and g.Devices["RadPro"][g.CONN]: # RadPro - Activated AND Connected:
                # self.histRadProLoadNewAction.   setEnabled(True)   #   allow downloading when not logging
                self.histRadProLoadAllAction.   setEnabled(True)   #   dito
                self.RadProSetTimeAction.       setEnabled(True)   #   enable time setting
                self.RadProConfigAction.        setEnabled(True)   #   enable config setting
                self.RadProInfoExtAction.       setEnabled(True)   #   enable extended info


            if g.Devices["Manu"][g.ACTIV] :                        # Manu - Activated
                self.ManuValAction.             setEnabled(True)   #   can enter data only when logging

            if g.logDBPath is None:
                self.startloggingAction.        setEnabled(False)  # no log file loaded, cannot start logging

            if g.DevicesConnected == 0:                            # no connected devices
                self.quickLogAction.            setEnabled(False)  #   no quick Log
                self.startloggingAction.        setEnabled(False)  #   no start log

        # adding Log comments allowed when a file is defined
        if g.logDBPath is not None:    self.addCommentAction.      setEnabled(True)
        else:                          self.addCommentAction.      setEnabled(False)

        # clear Log file (make it empty)
        if g.logDBPath is not None:    self.clearLogfileAction.    setEnabled(True)
        else:                          self.clearLogfileAction.    setEnabled(False)

        # adding History comments allowed when a file is defined
        if g.hisDBPath is not None:    self.addHistCommentAction.  setEnabled(True)
        else:                          self.addHistCommentAction.  setEnabled(False)

        # general add comment button enabled if either Log or Hist file is available
        if g.logDBPath is not None or g.hisDBPath is not None: self.btnAddComment.setEnabled(True)    # either or both DBs are loaded
        else:                                                  self.btnAddComment.setEnabled(False)   # neither DB is loaded

        # general empty Log File button enabled if either Log or Hist file is available
        if g.logDBPath is not None or g.hisDBPath is not None: self.btnClearLogfile.setEnabled(True)    # either or both DBs are loaded
        else:                                                  self.btnClearLogfile.setEnabled(False)   # neither DB is loaded

        dprint(defname, "Complete")
        setIndent(0)


    def toggleGMCPower(self):
        """Toggle GMC device Power ON / OFF"""

        if g.logging:
            self.showStatusMessage("Cannot change power when logging! Stop logging first")
            return

        if gdev_gmc.isGMC_PowerOn(getconfig=True) == "ON":  self.switchGMCPower("OFF")
        else:                                               self.switchGMCPower("ON")


    def switchGMCPower(self, newstate="ON"):
        """Switch power of GMC device to ON or OFF"""

        defname = "switchGMCPower: "
        self.setBusyCursor()

        dprint(defname + "--> {}".format(newstate))
        setIndent(1)

        fprint(header("Switch GMC Device Power"))
        QtUpdate()

        # faster to set Power than first reading config to check whether necessary
        if newstate == "ON":
            # set power "ON"
            gdev_gmc.setGMC_POWERON()

        else:
            # set power "OFF"
            if g.logging: self.stopLogging()
            gdev_gmc.setGMC_POWEROFF()

        ipo = self.setGMCPowerIcon(getconfig=True)

        fprint("Current Power State: GMC Power is ", ipo)

        self.checkLoggingState()
        self.setNormalCursor()
        setIndent(0)


    def setGMCPowerIcon(self, getconfig=False):
        """Sets the GMC Power-Icon in the toolbar"""

        return gdev_gmc.isGMC_PowerOn(getconfig=getconfig) # includes the actual setting of the Power-Icon


#help
    def helpQuickStart(self):
        """Quickstart item on the Help menu"""

        msg = QMessageBox()
        msg.setWindowIcon(self.iconGeigerLog)
        msg.setWindowTitle("Help - Quickstart")
        msg.setText(g.helpQuickstart)

        msg.setStandardButtons(QMessageBox.Ok)
        msg.setDefaultButton(QMessageBox.Ok)
        msg.setEscapeButton(QMessageBox.Ok)
        msg.setWindowModality(Qt.WindowModal)
        msg.setMinimumWidth(1000)
        msg.setStyleSheet("QLabel{min-width:800px; font-size:12pt;}")

        msg.exec()


    def helpFirmwareBugs(self):
        """Geiger Counter Firmware Bugs info on the Help menu"""

        msg = QMessageBox()
        msg.setWindowIcon(self.iconGeigerLog)
        msg.setWindowTitle("Help - Firmware Bugs")
        msg.setTextFormat(Qt.RichText)
        msg.setText(g.helpFirmwareBugs)

        msg.setStandardButtons(QMessageBox.Ok)
        msg.setDefaultButton(QMessageBox.Ok)
        msg.setEscapeButton(QMessageBox.Ok)
        msg.setWindowModality(Qt.WindowModal)
        msg.setStyleSheet("QLabel{min-width:800px; font-size:11pt;}")
        msg.setMinimumWidth(1000)

        msg.exec()


    def helpWorldMaps(self):
        """Using the Radiation World Map"""

        msg = QMessageBox()
        msg.setWindowIcon(self.iconGeigerLog)
        msg.setWindowTitle("Help - Radiation World Maps")
        msg.setText(g.helpWorldMaps)

        msg.setStandardButtons(QMessageBox.Ok)
        msg.setDefaultButton(QMessageBox.Ok)
        msg.setEscapeButton(QMessageBox.Ok)
        msg.setWindowModality(Qt.WindowModal)
        msg.setStyleSheet("QLabel{min-width:800px; font-size:12pt;}")
        msg.setMinimumWidth(1000)

        msg.exec()


    def helpOccupationalRadiation(self):
        """Occupational Radiation Limits"""

        msg = QMessageBox()
        msg.setWindowIcon(self.iconGeigerLog)
        msg.setWindowTitle("Help - Occupational Radiation Limits")
        msg.setText(g.helpOccupationalRadiation)

        msg.setStandardButtons(QMessageBox.Ok)
        msg.setDefaultButton(QMessageBox.Ok)
        msg.setEscapeButton(QMessageBox.Ok)
        msg.setWindowModality(Qt.WindowModal)
        msg.setStyleSheet("QLabel{min-width:800px; font-size:12pt;}")
        msg.setMinimumWidth(1000)

        msg.exec()


    def helpOptions(self):
        """Options item on the Help menu"""

        msg = QMessageBox()
        msg.setWindowIcon(self.iconGeigerLog)
        msg.setWindowTitle("Help - Command Line Options and Commands")
        msg.setFont(self.fontstd)   # required! must det to plain text, not HTML
        msg.setText(g.helpOptions)

        msg.setStandardButtons(QMessageBox.Ok)
        msg.setDefaultButton(QMessageBox.Ok)
        msg.setEscapeButton(QMessageBox.Ok)
        msg.setWindowModality(Qt.WindowModal)
        # msg.setStyleSheet("QLabel{min-width:800px; font-size:12pt;}")
        msg.setStyleSheet("QLabel{min-width:850px; font-size:12pt;}")
        msg.setMinimumWidth(1900)

        msg.exec()


    def helpAbout(self):
        """About item on the Help menu"""

        # the curly brackets {} used for Python's format() don't work when the text has CSS formatting using {}!
        # --> solution: use double quotes for what is NOT part of format (i.e. for the CSS)
        description = g.helpAbout.format(__author__, g.__version__, __copyright__, __license__)


        p = QPixmap(os.path.join(g.resDir, 'icon_geigerlog.png')) # the icon is 512 x 512
        w = 100
        h = 100
        licon = QLabel()                                  # label to hold the geigerlog icon
        licon.setPixmap(p.scaled(w,h,Qt.KeepAspectRatio))   # set a scaled pixmap to a w x h window keeping its aspect ratio

        ltext = QLabel()                                  # label to hold the 'eigerlog' text as picture
        ltext.setPixmap(QPixmap(os.path.join(g.resDir, 'eigerlog.png')))

        labout = QTextBrowser()                                                                # label to hold the description
        labout.setLineWrapMode(QTextEdit.WidgetWidth)
        labout.setText(description)
        labout.setOpenExternalLinks(True)                                                       # to open links in a browser
        labout.setTextInteractionFlags(Qt.LinksAccessibleByMouse|Qt.TextSelectableByMouse)
        labout.setMaximumWidth(850)                                                             # set the width:

        d = QDialog()
        d.setWindowIcon(self.iconGeigerLog)
        d.setWindowTitle("Help - About GeigerLog")
        d.setWindowModality(Qt.WindowModal)
        d.setMaximumWidth(1290)
        d.setMinimumWidth(850)
        screen_available = QDesktopWidget().availableGeometry()
        d.setMinimumHeight(min(screen_available.height(), g.window_height + 220))

        bbox      = QDialogButtonBox()
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


    def changeCmdLineOptions(self):
        """Switches State of some command line options"""

        defname = "changeCmdLineOptions: "

    # left column:

        # debug
        checkDebug = QCheckBox("Debug")
        checkDebug.setLayoutDirection(Qt.LeftToRight)
        checkDebug.setChecked(g.debug)

        # verbose
        checkVerbose = QCheckBox("Verbose")
        checkVerbose.setLayoutDirection(Qt.LeftToRight)
        checkVerbose.setChecked(g.verbose)

        # werbose
        checkWerbose = QCheckBox("Werbose")
        checkWerbose.setLayoutDirection(Qt.LeftToRight)
        checkWerbose.setChecked(g.werbose)

        # devel
        checkDevel = QCheckBox("Devel")
        checkDevel.setLayoutDirection(Qt.LeftToRight)
        checkDevel.setChecked(g.devel)

        # trace
        checkTrace = QCheckBox("Trace")
        checkTrace.setLayoutDirection(Qt.LeftToRight)
        checkTrace.setChecked(g.traceback)
        checkTrace.setToolTip("Prints traceback in devel mode")


    # middle column:
        # timing
        checkTiming = QCheckBox("Timing")
        checkTiming.setLayoutDirection(Qt.LeftToRight)
        checkTiming.setChecked(g.timing)
        checkTiming.setToolTip("Writes timing values to Manu device")

        # graphboldasis
        checkBold = QCheckBox("Graph Bold Lines")
        checkBold.setLayoutDirection(Qt.LeftToRight)
        checkBold.setChecked(g.graphbold)
        checkBold.setToolTip("Plot lines with full, thick linewidth")

        # graph_dot_connect
        checkDotConnect = QCheckBox("Graph Connect Lines")
        checkDotConnect.setLayoutDirection(Qt.LeftToRight)
        checkDotConnect.setChecked(g.graphConnectDots)
        checkDotConnect.setToolTip("Plot lines without connecting line between dots")

    # right column:

        # testing
        checkTesting = QCheckBox("Testing Generic")
        checkTesting.setLayoutDirection(Qt.LeftToRight)
        checkTesting.setChecked(g.testing)
        checkTesting.setToolTip("To activate anything for testing purposes")

        # GMC_simul
        checkGMC = QCheckBox("Simulation GMC")
        checkGMC.setLayoutDirection(Qt.LeftToRight)
        checkGMC.setChecked(g.GMC_simul)
        checkGMC.setToolTip("Allows to simulate a GMC Device; needs Simul_GMCcounter.py being run")

        # GS_simul
        checkGS = QCheckBox("Simulation GammaScout")
        checkGS.setLayoutDirection(Qt.LeftToRight)
        checkGS.setChecked(g.GS_simul)
        checkGS.setToolTip("Allows to simulate a GammaScout Device; needs Simul_GScounter.py being run")

        # Force Line Wrapping
        checkflw = QCheckBox("Force Line Wrap")
        checkflw.setLayoutDirection(Qt.LeftToRight)
        checkflw.setChecked(g.forcelw)
        checkflw.setToolTip("Activate Line Wrapping in the Terminal")

        # geht so nicht; erfordert Neustart
        # # Telegram Usage
        # checkTgU = QCheckBox("Telegram Usage")
        # checkTgU.setLayoutDirection(Qt.LeftToRight)
        # checkTgU.setChecked(g.TelegramActivation)
        # checkTgU.setToolTip("Using Telegram Messaging")


        layoutL = QVBoxLayout()         # left
        layoutL.addWidget(checkDebug)
        layoutL.addWidget(checkVerbose)
        layoutL.addWidget(checkWerbose)
        layoutL.addWidget(checkDevel)
        layoutL.addWidget(checkTrace)
        layoutL.addStretch()

        layoutM = QVBoxLayout()         # middle
        layoutM.addWidget(checkTiming)
        layoutM.addWidget(checkBold)
        layoutM.addWidget(checkDotConnect)
        layoutM.addStretch()

        layoutR = QVBoxLayout()         # right
        layoutR.addWidget(checkTesting)
        layoutR.addWidget(checkGMC)
        layoutR.addWidget(checkGS)
        layoutR.addWidget(checkflw)
        # layoutR.addWidget(checkTgU)

        layoutR.addStretch()

        layoutB = QHBoxLayout()         # set cols left, middle, right
        layoutB.addLayout(layoutL)
        layoutB.addLayout(layoutM)
        layoutB.addLayout(layoutR)

        bbox = QDialogButtonBox()
        bbox.setStandardButtons(QDialogButtonBox.Cancel | QDialogButtonBox.Ok )
        bbox.accepted.connect(lambda: d.done(100))
        bbox.rejected.connect(lambda: d.done(0))   # ESC key produces 0 (zero)!

        d = QDialog()
        d.setWindowIcon(g.iconGeigerLog)
        d.setWindowTitle("Change Command Line Options")
        d.setWindowModality(Qt.WindowModal)
        d.setMinimumWidth(320)

        layoutV = QVBoxLayout(d)
        layoutV.addLayout(layoutB)
        layoutV.addWidget(bbox)

        retval = d.exec()
        #print("reval:", retval)
        if retval != 100: return

        #
        # The ranking is debug --> verbose --> werbose
        # if any is true, the higher one(s) must also be set true
        # trace requires debug
        if checkDebug.isChecked():
            g.debug     = True
        else:
            g.debug     = False
            g.verbose   = False
            g.werbose   = False

        if checkVerbose.isChecked():
            g.verbose   = True
            g.debug     = True
        else:
            g.verbose   = False
            g.werbose   = False

        if checkWerbose.isChecked():
            g.werbose   = True
            g.verbose   = True
            g.debug     = True
        else:
            g.werbose   = False

        if checkTrace.isChecked():
            g.traceback = True
            g.debug     = True
        else:
            g.traceback = False

        g.devel              = True if checkDevel     .isChecked() else False

        g.timing             = True if checkTiming    .isChecked() else False
        g.graphbold          = True if checkBold      .isChecked() else False
        g.graphConnectDots   = True if checkDotConnect.isChecked() else False

        g.testing            = True if checkTesting   .isChecked() else False
        g.GMC_simul          = True if checkGMC       .isChecked() else False
        g.GS_simul           = True if checkGS        .isChecked() else False
        g.forcelw            = True if checkflw       .isChecked() else False
        # g.TelegramActivation = True if checkTgU       .isChecked() else False

        if g.forcelw:   executeTPUT(action = 'allow_line_wrapping')
        else:           executeTPUT(action = 'no_line_wrapping')

        fprint(header("Change Command Line Options"))
        setfrmt   = "   {:27s}{}\n"
        settings  = "Current settings:\n"

        settings += setfrmt.format("Debug:",               g.debug)
        settings += setfrmt.format("Verbose:",             g.verbose)
        settings += setfrmt.format("Werbose:",             g.werbose)
        settings += setfrmt.format("Devel:",               g.devel)
        settings += setfrmt.format("Trace:",               g.traceback)

        settings += setfrmt.format("Timing:",              g.timing)
        settings += setfrmt.format("Graph Bold Lines:",    g.graphbold)
        settings += setfrmt.format("Connect Dots:",        g.graphConnectDots)

        settings += setfrmt.format("Testing:",             g.testing)
        settings += setfrmt.format("GMC Simul:",           g.GMC_simul)
        settings += setfrmt.format("GS Simul:",            g.GS_simul)
        settings += setfrmt.format("Force Line Wrap:",     g.forcelw)

        fprint(settings)
        dprint(defname + settings)


    def editFormulas(self):
        """shows the current settings of [ValueFormula] and [GraphFormula]"""

        defname = "editFormulas: "

        # Comment
        customBox=QFormLayout()
        customBox.setSizeConstraint (QLayout.SetFixedSize)
        customBox.RowWrapPolicy(QFormLayout.DontWrapRows)
        customBox.addRow(QLabel("{:60s}".format("<b>Comment</b><br>")))
        vcl  = QLabel("max 12 char")
        vcl.setMinimumHeight(24)
        customBox.addRow(vcl)
        for vname in g.VarsCopy:
            qle = QLineEdit(g.VarsCopy[vname][6])
            qle.setMaximumWidth(100)
            qle.setStyleSheet("QLineEdit {font-size:10pt;}")
            customBox.addRow(qle)

        # value formulas
        valueBox=QFormLayout()
        valueBox.setSizeConstraint (QLayout.SetFixedSize)
        valueBox.RowWrapPolicy(QFormLayout.DontWrapRows)
        valueBox.addRow(QLabel("{:60s}".format("<b>ValueFormula</b> - this <b>DOES</b> modify the saved value!<br>   ")))
        vcl  = QLabel("  ")
        vcl.setMinimumHeight(24)
        valueBox.addRow(vcl)

        for vname in g.VarsCopy:
            qle = QLineEdit(g.ValueScale[vname])
            qle.setStyleSheet("QLineEdit {font-size:10pt;}")
            valueBox.addRow(vname, qle)

        # graph formulas
        # scl  = QLabel("Use the Graph-Formula data for <b>Stats and Plots</b>: ")
        scl  = QLabel("Use these data for <b>Stats and Plots</b>: ")
        scb0 = QRadioButton("Yes")             # this is default
        scb0.setChecked(g.useGraphScaledData)
        scb1 = QRadioButton("No")
        scb1.setChecked(not g.useGraphScaledData)
        scaleCalc = QHBoxLayout()
        scaleCalc.addWidget(scl)
        scaleCalc.addWidget(scb0)
        scaleCalc.addWidget(scb1)

        graphBox=QFormLayout()
        graphBox.setFieldGrowthPolicy (QFormLayout.ExpandingFieldsGrow)
        graphBox.RowWrapPolicy(QFormLayout.DontWrapRows)
        graphBox.addRow(QLabel("{:60s}".format("<b>GraphFormula</b> - this <b>does NOT</b> modify the saved value,<br>onlythe plotted value")))
        graphBox.addRow(scaleCalc)
        for vname in g.VarsCopy:
            qle = QLineEdit(g.GraphScale[vname])
            qle.setStyleSheet("QLineEdit {font-size:10pt;}")

            # graphBox.addRow(vname, QLineEdit(g.GraphScale[vname]))
            graphBox.addRow(vname, qle)

        vgLayout = QHBoxLayout()
        vgLayout.addLayout(customBox)
        vgLayout.addStretch()
        vgLayout.addLayout(valueBox)
        vgLayout.addStretch()
        vgLayout.addLayout(graphBox)

        # When an application modal dialog is opened, the user must finish interacting with the dialog and close it before
        # they can access any other window in the application. Window modal dialogs only block access to the window associated
        # with the dialog, allowing the user to continue to use other windows in an application.
        # d.setWindowModality(Qt.WindowModal)                   #
        # d.setWindowModality(Qt.ApplicationModal)              # The window is modal to the application and blocks input to all windows.
        # d.setWindowModality(Qt.NonModal)                      # The window is not modal and does not block input to other windows.
        # self.dialog.setWindowModality(Qt.ApplicationModal)    # The window is modal to the application and blocks input to all windows.
        # self.dialog.setWindowModality(Qt.WindowModal)         # Strange - this allows input to other functions but chrashes when multiple win were opened and closed

        self.dialog = QDialog()
        self.dialog.setWindowIcon(self.iconGeigerLog)
        self.dialog.setWindowTitle("View and Edit Current Formulas")
        self.dialog.setWindowModality(Qt.NonModal)            # behaves exactly like AppliacationModal ???
        # self.dialog.setWindowModality(Qt.WindowModal)           # allows to open other windows
        self.dialog.setMinimumWidth(900)
        self.dialog.setMaximumWidth(1200)

        bbox = QDialogButtonBox()
        bbox.setStandardButtons(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        bbox.accepted.connect(lambda: self.dialog.done(0))
        bbox.rejected.connect(lambda: self.dialog.done(1))

        layoutV = QVBoxLayout(self.dialog)
        layoutV.addWidget(QLabel("See GeigerLog manual chapter <b>ValueFormula and GraphFormula</b>.<br>"))
        layoutV.addLayout(vgLayout)
        layoutV.addWidget(bbox)

        resultdlg = self.dialog.exec()

        if resultdlg == 0:

            ############################################################################
            ### Must NOT replace "," with ".", as "," is needed for 2-parameter entries!
            ############################################################################

            for i, vname in enumerate(g.VarsCopy):
                    vval   = (customBox.itemAt(i + 2, QFormLayout.FieldRole).widget().text()).strip()
                    vprint("customBox i: {:2d} vname:{:10s} vval:{}".format(i + 2, vname, vval))
                    g.VarsCopy[vname][6] = vval[0:12]

            for i in range(0, len(g.VarsCopy) + 2):
                if valueBox.itemAt(i, QFormLayout.LabelRole) is not None:
                    vvname = (valueBox.itemAt(i, QFormLayout.LabelRole).widget().text()).strip()
                    vval   = (valueBox.itemAt(i, QFormLayout.FieldRole).widget().text()).strip()
                    vprint("valueBox  i: {:2d} vvname:{:10s} vval:{}".format(i, vvname, vval))
                    g.ValueScale[vvname] = vval

            for i in range(0, len(g.VarsCopy) + 2):
                if graphBox.itemAt(i, QFormLayout.LabelRole) is not None:
                    gvname = (graphBox.itemAt(i, QFormLayout.LabelRole).widget().text()).strip()
                    gval   = (graphBox.itemAt(i, QFormLayout.FieldRole).widget().text()).strip()
                    vprint("graphBox  i: {:2d} gvname:{:10s} gval:{}".format(i, gvname, gval))
                    g.GraphScale[gvname] = gval

            if scb0.isChecked():    g.useGraphScaledData = True
            else:                   g.useGraphScaledData = False

            self.applyGraphOptions()    # update the graph


    #vvv
    def copyVar2Var(self):
        """copy one variable to another via SQL command"""

        # copying via SQL:
        # This is a very simple task: update T set y=x; where x is the source and y is the target.

        defname = "copyVar2Var: "
        dprint(defname)
        setIndent(1)

        # Donor Variable
        DonorBox=QFormLayout()
        DonorBox.setSizeConstraint (QLayout.SetFixedSize)
        DonorBox.RowWrapPolicy(QFormLayout.DontWrapRows)
        # DonorBox.addRow(QLabel("{:30s}".format("<b>Donor Variable</b>")))
        DonorBox.addRow(QLabel("<b>Donor Variable</b>"))
        for vname in g.VarsCopy:
            DonorBox.addRow(vname, QRadioButton())

        # Recipient Variable(s)
        RecipBox=QFormLayout()
        RecipBox.setFieldGrowthPolicy (QFormLayout.ExpandingFieldsGrow)
        RecipBox.RowWrapPolicy(QFormLayout.DontWrapRows)
        # RecipBox.addRow(QLabel("{:30s}".format("<b>Recipient Variable(s)</b>")))
        RecipBox.addRow(QLabel("<b>Recipient Variable(s)</b>"))
        for vname in g.VarsCopy:
            RecipBox.addRow(vname, QCheckBox())

        vgLayout = QHBoxLayout()
        vgLayout.addLayout(DonorBox)
        vgLayout.addLayout(RecipBox)

        self.dialog = QDialog()
        self.dialog.setWindowIcon(self.iconGeigerLog)
        self.dialog.setWindowTitle("Copy One Variable to Others")
        self.dialog.setWindowModality(Qt.ApplicationModal)      # The window is modal to the application and blocks input to all windows.
        # self.dialog.setWindowModality(Qt.WindowModal)         # Strange - this allows input to other functions but chrashes when multiple win were opened and closed
        # self.dialog.setWindowModality(Qt.NonModal)            # behaves exactly like AppliacationModal ???
        self.dialog.setMinimumWidth(350)
        self.dialog.setMaximumWidth(600)

        bbox = QDialogButtonBox()
        bbox.setStandardButtons(QDialogButtonBox.Ok|QDialogButtonBox.Cancel)
        bbox.accepted.connect(lambda: self.dialog.done(0))
        bbox.rejected.connect(lambda: self.dialog.done(1))

        infoLabel = QLabel("For guidance see chapter <b>Configuration</b>, topic <b>Copying Variables</b> in GeigerLog manual.<br>")
        infoLabel.setWordWrap(True)

        layoutV = QVBoxLayout(self.dialog)
        layoutV.addWidget(infoLabel)
        layoutV.addLayout(vgLayout)
        layoutV.addStretch(100)
        layoutV.addWidget(bbox)

        resultdlg = self.dialog.exec()

        donorVar = None
        recipVar = []

        if resultdlg == 0:
            for i in range(1, len(g.VarsCopy) + 1):
                dvname = DonorBox.itemAt(i, QFormLayout.LabelRole).widget().text()
                dval   = DonorBox.itemAt(i, QFormLayout.FieldRole).widget().isChecked()
                if dval:
                    # donorVar = i - 1
                    donorVar = dvname
                    break
                mdprint("DonorBox i: {:2d}  {:10s}  {}".format(i, dvname, dval))

            for i in range(1, len(g.VarsCopy) + 1):
                rvname = (RecipBox.itemAt(i, QFormLayout.LabelRole).widget().text())
                rval   = (RecipBox.itemAt(i, QFormLayout.FieldRole).widget().isChecked())
                if rval:
                    # recipVar.append(i - 1)
                    recipVar.append(rvname)
                mdprint("RecipBox i: {:2d}  {:10s}  {}".format(i, rvname, rval))

            rdprint(defname, "Donor: ", donorVar)
            rdprint(defname, "Recip: ", recipVar)


        # if g.hisFilePath is not None: rdprint(defname, "g.hisFilePath is not None: ", g.hisFilePath)

        # rdprint(defname, "g.hisFilePath is ", g.hisFilePath)
        # rdprint(defname, "g.hisConn is     ", g.hisConn)

        if g.hisConn     is not None:
            # rdprint(defname, "g.hisConn is not None:     ", g.hisConn)
            DB_Connection = g.hisConn

            basesql = "update data set {{}}={}".format(donorVar)
            rdprint(defname, "baseSQL:", basesql)

            for vname in recipVar:
                rdprint(defname, "vname: ", vname)
                # sql = basesql + g.VarsCopy[vname][5]
                sql = basesql.format(g.VarsCopy[vname][5])
                rdprint(defname, "SQL:", sql)
                try:
                    DB_Connection.execute(sql)
                except Exception as e:
                    srcinfo = defname + "Exception:" + sql
                    exceptPrint(e, "")
                    edprint(srcinfo)

            from gsup_sql import DB_commit
            DB_commit(DB_Connection)
        else:
            dprint(defname, "Cannot copy variables - no database connection")

        setIndent(0)


#utilities in Class

    def clearNotePad(self):
        """Clear the notepad"""

        self.notePad.clear()
        self.notePad.setTextColor(QColor(40, 40, 40))


    def clearLogPad(self):
        """Clear the logPad"""

        self.logPad.clear()
        # self.logPad.append("noch ne clear zeile")



    def setBusyCursor(self):
        "Change cursor to rotating clock"
        QApplication.setOverrideCursor(Qt.WaitCursor)
        # rdprint("setBusyCursor: called")


    def setNormalCursor(self):
        "Change cursor to normal (arrow or insert"
        QApplication.restoreOverrideCursor()


    def showStatusMessage(self, message, timing=0, error=True):
        """shows message by flashing the Status Bar red for 0.5 sec, then switches back to normal"""

        if error == False:
            self.statusBar.setStyleSheet("QStatusBar { }")      # reset to default colors
            self.statusBar.showMessage(message, msecs=timing)   # message remains until overwritten by next status
        else:
            pass
            # burp()
            # self.statusBar.showMessage(message, msecs=timing)   # message remains until overwritten by next status
            # self.statusBar.setStyleSheet("QStatusBar { background-color:red; color:white; }")
            # QtUpdate()                                         # assure that things are visible
            # time.sleep(0.5)                                     # stays red for 0.5 sec
            # self.statusBar.setStyleSheet("QStatusBar { }")      # reset to default colors

        if error == False:
            # fprint(message)
            pass
        else:
            efprint(message)

######## class ggeiger ends ###################################################

