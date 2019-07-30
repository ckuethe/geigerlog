#!/usr/bin/python3
# -*- coding: UTF-8 -*-

"""
AmbioMon++ support for a MQTT connection
"""

"""
Installing MQTT on Ubuntu:
see: https://www.digitalocean.com/community/tutorials/how-to-install-and-secure-the-mosquitto-mqtt-messaging-broker-on-ubuntu-16-04
site includes steps to set up secure server!

To install the software:
    sudo apt-get install mosquitto mosquitto-clients

Testing MQTT, assuming mosqitto running on urkam.de:
Subscribe in terminal 1:
    mosquitto_sub -v -h urkam.de -t ambiomon/#
Publish in terminal 2:
    mosquitto_pub -h urkam.de -t ambiomon/temp -m "hello world"
You should see in terminal 1:
    ambiomon/temp hello world
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
__copyright__       = "Copyright 2016, 2017, 2018, 2019"
__credits__         = [""]
__license__         = "GPL3"

from   gutils           import *

import paho.mqtt.client as mqtt     # https://pypi.org/project/paho-mqtt/


###############################################################################
# BEGIN MQTT Callbacks
###############################################################################

def on_connect(client, userdata, flags, rc):
    """The callback for when the client receives a CONNACK response from the server"""

    # The value of rc indicates success or not:
    strrc = {
            0: "Connection successful",
            1: "Connection refused - incorrect protocol version",
            2: "Connection refused - invalid gglobs.ambio_client identifier",
            3: "Connection refused - server unavailable",
            4: "Connection refused - bad username or password",
            5: "Connection refused - not authorised",
            # 6-255: Currently unused.
            }

    if rc < 6:     src = strrc[rc]
    else:          src = "Unexpected Connection Response"
    gglobs.AmbioConnect = (rc, src)

    if rc == 0:
        gglobs.AmbioConnection = True
    else:
        gglobs.AmbioConnection = False

    dprint(">AmbioMon: on_connect: Client connected:")
    dprint(">          {:20s}: {}".format("with userdata"     , userdata))
    dprint(">          {:20s}: {}".format("with flags"        , flags))
    dprint(">          {:20s}: {}".format("with result"       , src), " (Result Code: {})".format(rc))

    # Subscribing on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    #gglobs.ambio_client.subscribe("$SYS/#")
    gglobs.ambio_client.subscribe(gglobs.AmbioServerFolder + "#", qos=2)


def on_disconnect (client, userdata, rc):
    """When the client has sent the disconnect message it generates an on_disconnect() callback."""

    # The rc parameter indicates the disconnection state.
    # If MQTT_ERR_SUCCESS (0), the callback was called in response to a
    # disconnect() call.
    # If any other value the disconnection was unexpected, such as might be
    # caused by a network error."""

    strrc = {
            0: "MQTT_ERR_SUCCESS",
            1: "Unexpected disconnection",
            }

    if rc == 0:     src = strrc[rc]
    else:           src = strrc[1]
    gglobs.AmbioDisconnect = (rc, src)

    gglobs.AmbioConnection = False         # it is disconnected in any case

    dprint(">AmbioMon: on_disconnect: Client disconnected:")
    dprint(">          {:20s}: {}".format("with userdata"     , userdata))
    dprint(">          {:20s}: {}".format("with result"       , src), "(Result Code: {})".format(rc))


def on_subscribe(client, userdata, mid, granted_qos):
    """Callback when a subscribe has occured"""

    dprint(">AmbioMon: on_subscribe: Topic subscribed:")
    dprint(">          {:20s}: {}".format("with userdata"     , userdata))
    dprint(">          {:20s}: {}".format("with mid"          , mid))
    dprint(">          {:20s}: {}".format("with granted_qos"  , granted_qos))


def on_message(client, userdata, msg):
    """The callback for when a PUBLISH message is received from the server"""

    # message: an instance of MQTTMessage.
    # This is a class with members topic, payload, qos, retain.

    vprint(">AmbioMon: on_message: topic: {:20s}, payload: {:10s}, qos: {}, retain: {}".format(msg.topic, str(msg.payload), msg.qos, msg.retain))
    print("type of msg.payload:", type(msg.payload))

    if   msg.topic == gglobs.AmbioServerFolder + "temp":     gglobs.ambio_temp   = float(msg.payload)    # T
    elif msg.topic == gglobs.AmbioServerFolder + "pressure": gglobs.ambio_press  = float(msg.payload)    # P
    elif msg.topic == gglobs.AmbioServerFolder + "humid":    gglobs.ambio_hum    = float(msg.payload)    # H
    elif msg.topic == gglobs.AmbioServerFolder + "cpm":      gglobs.ambio_cpm    = float(msg.payload)    # R
    elif msg.topic == gglobs.AmbioServerFolder + "rssi":     gglobs.ambio_rssi   = float(msg.payload)    # rssi
    #else:                                                print("msg.payload:", msg.payload)       # any


def on_publish(client, userdata, mid):
    """ Called when a message that was to be sent using the publish() call
    has completed transmission to the broker"""

    dprint("on_publish: messageID: mid: ", mid)
    pass


###############################################################################
# END MQTT Callbacks
###############################################################################


def configureAmbioMon():
    """Set settings for Ambiomon"""

    dprint("configureAmbioMon:")
    debugIndent(1)

    # AM Voltage
    lavolt     = QLabel("Anode voltage [V]\n(0 ... 999 V)")
    lavolt.setAlignment(Qt.AlignLeft)
    avolt  = QLineEdit()
    validator = QDoubleValidator(0, 999, 1, avolt)
    avolt.setValidator(validator)
    avolt.setToolTip('The anode voltage in volt')
    avolt.setText("{:0.6g}".format(gglobs.AmbioVoltage))

    # AM Cycle Time
    lctime     = QLabel("Cycle time [s]\n(at least 1 s)")
    lctime.setAlignment(Qt.AlignLeft)
    ctime  = QLineEdit()
    validator = QDoubleValidator(0, 999, 1, ctime)
    ctime.setValidator(validator)
    ctime.setToolTip('The cycle time of the AmbioMon device in seconds')
    ctime.setText("{:0.6g}".format(gglobs.AmbioCycletime))

    # AM Frequency
    lfreq     = QLabel("Frequency HV gen [Hz]\n(0 ... 99999 Hz)")
    lfreq.setAlignment(Qt.AlignLeft)
    freq  = QLineEdit()
    validator = QDoubleValidator(0, 99999, 1, freq)
    freq.setValidator(validator)
    freq.setToolTip('The frequency used in the anode voltage generator of the AmbioMon device in Hertz')
    freq.setText("{:0.6g}".format(gglobs.AmbioFrequency))

    # AM PWM
    lpwm     = QLabel("PWM fraction\n(0.000 ... 1.000)")
    lpwm.setAlignment(Qt.AlignLeft)
    pwm  = QLineEdit()
    validator = QDoubleValidator(0.00, 1.00, 1, pwm)
    pwm.setValidator(validator)
    pwm.setToolTip('The Pulse Width Modulation fraction of the AmbioMon device')
    pwm.setText("{:0.6g}".format(gglobs.AmbioPwm))

    graphOptions=QGridLayout()
    graphOptions.addWidget(lavolt,          0, 0)
    graphOptions.addWidget(avolt,           0, 1)
    graphOptions.addWidget(lctime,          1, 0)
    graphOptions.addWidget(ctime,           1, 1)
    graphOptions.addWidget(lfreq,           2, 0)
    graphOptions.addWidget(freq,            2, 1)
    graphOptions.addWidget(lpwm,            3, 0)
    graphOptions.addWidget(pwm,             3, 1)

    graphOptionsGroup = QGroupBox()
    graphOptionsGroup.setLayout(graphOptions)

    # Dialog box
    d = QDialog()       # set parent self to popup in center of geigerlog window
    d.setWindowIcon(gglobs.iconGeigerLog)
    d.setFont(gglobs.fontstd)
    d.setWindowTitle("Configure AmbioMon")
    d.setWindowModality(Qt.ApplicationModal)
    #d.setWindowModality(Qt.NonModal)
    #d.setWindowModality(Qt.WindowModal)

    # Buttons
    bbox = QDialogButtonBox()
    bbox.setStandardButtons(QDialogButtonBox.Cancel | QDialogButtonBox.Ok )
    bbox.accepted.connect(lambda: d.done(1))
    bbox.rejected.connect(lambda: d.done(-1))

    gglobs.btn = bbox.button(QDialogButtonBox.Ok)
    gglobs.btn.setEnabled(True)

    layoutV = QVBoxLayout(d)
    layoutV.addWidget(graphOptionsGroup)
    layoutV.addWidget(bbox)

#### needs to change !!!!!
#        ctime.textChanged.connect(check_state) # last chance
#        ctime.textChanged.emit   (ctime.text())
#######

#TESTING
    #if gglobs.logging:
    if 0 and gglobs.logging:
        setbgcolor = 'QLineEdit { background-color: %s;  }' % ("#e0e0e0",)
        gglobs.btn  .setEnabled(False)
        ctime  .setEnabled(False)
        ctime  .setStyleSheet(setbgcolor)
        avolt  .setEnabled(False)
        avolt  .setStyleSheet(setbgcolor)
        freq   .setEnabled(False)
        freq   .setStyleSheet(setbgcolor)
        pwm    .setEnabled(False)
        pwm    .setStyleSheet(setbgcolor)

    retval = d.exec_()
    #print("reval:", retval)

    if retval != 1:
        # ESCAPE pressed or Cancel Button
        dprint("configureAmbioMon: Settings unchanged")

    else:
        # OK pressed

        # change the voltage setting
        oldvoltage = gglobs.AmbioVoltage
        voltage    = avolt.text().replace(",", ".")  #replace comma with dot
        try:
            lc  = round(float(voltage), 0)
            if lc > 999: lc = 999
            if lc < 0:   lc = 0
        except: lc  = oldvoltage
        gglobs.AmbioVoltage = lc

        # change the cycle time
        oldcycletime = gglobs.AmbioCycletime
        cycletime    = ctime.text().replace(",", ".")  #replace comma with dot
        try:
            lc  = round(float(cycletime), 2)
            if lc < 0: lc = 0
        except: lc  = oldcycletime
        gglobs.AmbioCycletime = lc

        # change the frequency
        oldfrequency = gglobs.AmbioFrequency
        frequency    = freq.text().replace(",", ".")  #replace comma with dot
        try:
            lc  = round(float(frequency), 0)
            if lc > 99999: lc = 99999
            if lc < 0:     lc = 0
        except: lc  = oldfrequency
        gglobs.AmbioFrequency = lc

        # change the pwm
        oldpwm = gglobs.AmbioPwm
        pwm    = pwm.text().replace(",", ".")  #replace comma with dot
        try:
            lc  = round(float(pwm), 3)
            if lc > 1: lc = 1
            if lc < 0: lc = 0
        except: lc  = oldpwm
        gglobs.AmbioPwm = lc


        setAmbioMonSettings(gglobs.AmbioVoltage, gglobs.AmbioCycletime, gglobs.AmbioFrequency, gglobs.AmbioPwm)

        dprint("configureAmbioMon: new voltage: "       , gglobs.AmbioVoltage)
        dprint("configureAmbioMon: new cycle time: "    , gglobs.AmbioCycletime)
        dprint("configureAmbioMon: new frequency: "     , gglobs.AmbioFrequency)
        dprint("configureAmbioMon: new PWM: "           , gglobs.AmbioPwm)

        fprint(header("Configure AmbioMon Device"))
        fprint("Anode voltage setting:" , "{} V"    .format(gglobs.AmbioVoltage))
        fprint("Cycle time setting:"    , "{} s"    .format(gglobs.AmbioCycletime))
        fprint("Frequency HV gen:"      , "{} Hz"   .format(gglobs.AmbioFrequency))
        fprint("PWM fraction:"          , "{}"      .format(gglobs.AmbioPwm))

    debugIndent(0)


def setAmbioMonSettings(voltage, cycletime, frequency, pwm):
    """Set Settings like the anode voltage on the AmbioMon Device"""

    if gglobs.ambio_client  == None:       return "No connected device"

    gglobs.ambio_client.publish(gglobs.AmbioServerFolder + "Settings/Volt",      voltage)
    gglobs.ambio_client.publish(gglobs.AmbioServerFolder + "Settings/Cycletime", cycletime)
    gglobs.ambio_client.publish(gglobs.AmbioServerFolder + "Settings/Frequency", frequency)
    gglobs.ambio_client.publish(gglobs.AmbioServerFolder + "Settings/PWM",       pwm)

    var = 60
    gglobs.ambio_client.publish(gglobs.AmbioServerFolder + "Settings/Sinus", var)


def getAmbioMonValues(varlist):
    """Read all AmbioMon data; return only when complete"""

    #vprint("getAmbioMonValues({})".format(varname))
    #debugIndent(1)

    alldata = {}

    if not gglobs.AmbioConnection: # AmbioMon is NOT connected!
        dprint("getAmbioMonValues: NO AmbioMon connection")
        return alldata

    if varlist == None:
        return alldata

    dataIncomplete = False
    for vname in varlist:
        if   vname == "T" and gglobs.ambio_temp  == None :
            dataIncomplete = True
            break
        elif vname == "P" and gglobs.ambio_press == None :
            dataIncomplete = True
            break
        elif vname == "H" and gglobs.ambio_hum   == None :
            dataIncomplete = True
            break
        elif vname in ("CPM", "CPM1st", "CPM2nd", "CPM3rd", "X") and gglobs.ambio_cpm == None:
            dataIncomplete = True
            break

    if not dataIncomplete:
        for vname in varlist:
            if   vname == "T":
                Temp            = gglobs.ambio_temp
                Temp            = scaleVarValues("T", Temp, gglobs.ValueScale["T"])
                gglobs.ambio_temp  = None
                alldata.update({vname: Temp})

            elif vname == "P":
                Press           = gglobs.ambio_press
                Press           = scaleVarValues("P", Press, gglobs.ValueScale["P"])
                gglobs.ambio_press = None
                alldata.update({vname: Press})

            elif vname == "H":
                Hum             = gglobs.ambio_hum
                Hum             = scaleVarValues("H", Hum, gglobs.ValueScale["H"])
                gglobs.ambio_hum   = None
                alldata.update({vname: Hum})

            elif vname in ("CPM", "CPM1st", "CPM2nd", "CPM3rd", "X"):
                cpm             = gglobs.ambio_cpm
                cpm             = scaleVarValues(vname, cpm, gglobs.ValueScale[vname])
                gglobs.ambio_cpm   = None
                alldata.update({vname: cpm})

    vprint("{:20s}:  Variables:{}  Data:{}  Folder:'{}' ".format("getAmbioMonValues", varlist, alldata, gglobs.AmbioServerFolder))
    #debugIndent(0)

    return alldata


def getAmbioMonInfo(extended=False):
    """Info on the AmbioMon Device"""

    if not gglobs.AmbioConnection: return "No connected device"

    if gglobs.ambio_rssi   == None:  rssi = "Not available"
    else:                            rssi = str(gglobs.ambio_rssi)

    AmbioInfo = """Connected Device:             {}
Configured Variables:         {}
Geiger tube calib. factor:    {} µSv/h/CPM""".format(\
                                                gglobs.AmbioDeviceName, \
                                                gglobs.AmbioVariables, \
                                                gglobs.AmbioCalibration)

    if extended == True:
        AmbioInfo += """
Connection:                   wireless, MQTT server {}, port:{}
Folder:                       '{}'
Internal collection time:     60 s
Total cycle time (typical):   67 ... 70 s
Geiger tube voltage setting:  {} Volt
Wireless signal strength:     {} (rssi)""".format(\
                                                gglobs.AmbioServerIP, \
                                                gglobs.AmbioServerPort, \
                                                gglobs.AmbioServerFolder, \
                                                gglobs.AmbioVoltage, \
                                                rssi)
    return AmbioInfo


def terminateAmbioMon():
    """opposit of init ;-)"""

    if not gglobs.AmbioConnection: return

    dprint("terminateAmbioMon: Terminating AmbioMon")
    debugIndent(1)

    gglobs.ambio_client.loop_stop()
    dprint("terminateAmbioMon: client.loop was stopped")

    gglobs.ambio_client.disconnect()    # output printed in callback
    dprint("terminateAmbioMon: client was disconnected")

    gglobs.ambio_client = None
    dprint("terminateAmbioMon: client was set to: None")

    # wait for confirmation of dis-connection
    starttime = time.time()
    timeout   = True
    while time.time() < (starttime  + gglobs.AmbioTimeout):
        #print("gglobs.Ambiodisconnect:", time.time() - starttime, gglobs.Ambiodisconnect)
        time.sleep(0.05)
        if not gglobs.AmbioConnection:
            #print("gglobs.Ambiodisconnect:", time.time() - starttime, gglobs.Ambiodisconnect)
            timeout = False
            break

    if timeout:
        dprint("AmbioMon dis-connection timed out ({} sec)".format(gglobs.AmbioTimeout), debug=True)
        fprint("<br>ERROR: Dis-Connection from AmbioMon+ server failed", error=True)

    gglobs.AmbioConnection = False  # inconsistent - is set even after timeout

    debugIndent(0)


def initAmbioMon():
    """Initialize the client and set all Callbacks"""

    fncname = "initAmbioMon: "
    errmsg  = ""

    if not gglobs.AmbioActivation:
        dprint(fncname + "Initialzing AmbioMon not possible as AmbioMon device is not activated")
        return errmsg

    dprint(fncname + "Initialzing AmbioMon")
    debugIndent(1)

    gglobs.AmbioDeviceName = "AmbioMon++"

    # set configuration
    if gglobs.AmbioServerIP     == "auto":      gglobs.AmbioServerIP     = "iot.eclipse.org"
    if gglobs.AmbioServerPort   == "auto":      gglobs.AmbioServerPort   = 1883
    if gglobs.AmbioServerFolder == "auto":      gglobs.AmbioServerFolder = "/"
    if gglobs.AmbioTimeout      == "auto":      gglobs.AmbioTimeout      = 3

# set client
    # Client(client_id="", clean_session=True, userdata=None, protocol=MQTTv311)
    # protocol: Can be either MQTTv31 or MQTTv311
    # on Ubuntu 12.04.5 LTS  with kernel 2.6.32-042stab134.8 the
    # protocol MQTTv311 is NOT working: (does not make a connect)
    # gglobs.ambio_client = mqtt.Client(cname, True, None, mqtt.MQTTv311)
    # it is working when protocol MQTTv31 is used
    gglobs.ambio_client = mqtt.Client(client_id="", clean_session=True, userdata=None, protocol=mqtt.MQTTv31)

    # set callbacks
    gglobs.ambio_client.on_connect       = on_connect
    gglobs.ambio_client.on_subscribe     = on_subscribe
    gglobs.ambio_client.on_message       = on_message
    gglobs.ambio_client.on_publish       = on_publish
    gglobs.ambio_client.on_disconnect    = on_disconnect

    # connect
    dprint(fncname + "connect to: AmbioServerIP: '{}', AmbioServerPort: {}".format(gglobs.AmbioServerIP, gglobs.AmbioServerPort))
    try:
        gglobs.ambio_client.connect(gglobs.AmbioServerIP, port=gglobs.AmbioServerPort, keepalive=60)
    except Exception as e:
        srcinfo = fncname + "ERROR: Connection to IoT server failed"
        exceptPrint(e, sys.exc_info(), srcinfo)
        gglobs.ambio_client = None
        errmsg += "<br>ERROR: Connection failed using server IP='{}', port={}".format(gglobs.AmbioServerIP, gglobs.AmbioServerPort)
        errmsg += "<br>ERROR: '{}'".format(sys.exc_info()[1])
        errmsg += "<br>{} not connected. Is server offline? Verify server IP and server port".format(gglobs.AmbioDeviceName)

        debugIndent(0)
        return errmsg

    #
    # start looping
    #
    ##  # keep as reminder - alternative looping
    ##  gglobs.ambio_client.loop_read()
    ##  for i in range(0,6):
    ##      gglobs.ambio_client.loop(timeout=.1)
    ##  gglobs.ambio_client.loop_forever()      # indeed forever, it hangs the system
    ##                                          # CTRL-C will disconnect the gglobs.ambio_client
    ##  gglobs.ambio_client.loop(timeout=10.0)  # returns control after timeout

    gglobs.ambio_client.loop_start()            # threaded loop; must be stopped on exit!
    dprint(fncname + "Threaded loop was started")

    # wait for confirmation of connection
    starttime = time.time()
    timeout   = True
    while time.time() < (starttime  + gglobs.AmbioTimeout):
        #print("gglobs.AmbioConnect: time:{:1.2f}".format(time.time() - starttime), gglobs.AmbioConnect)
        time.sleep(0.05)
        if gglobs.AmbioConnection:
            #print("gglobs.AmbioConnect: time:{:1.2f}".format(time.time() - starttime), gglobs.AmbioConnect)
            timeout = False
            break

    if timeout:
        # no callback signalling a connection
        dprint(fncname + "AmbioMon connection timed out ({} sec)".format(gglobs.AmbioTimeout), debug=True)
        errmsg += "ERROR: Connection to {} server failed; AmbioMon inactivated".format(gglobs.AmbioDeviceName)
    else:
        # set only after successful and confirmed connect!
        if gglobs.AmbioCalibration  == "auto":      gglobs.AmbioCalibration  = 0.0065
        if gglobs.AmbioVariables    == "auto":      gglobs.AmbioVariables    = "T, P, H, CPM3rd"

        # set the loggable variables
        DevVars = gglobs.AmbioVariables.split(",")
        for i in range(0, len(DevVars)):  DevVars[i] = DevVars[i].strip()
        gglobs.DevicesVars["AmbioMon"] = DevVars
        #print("DevicesVars:", gglobs.DevicesVars)

    debugIndent(0)
    return errmsg

