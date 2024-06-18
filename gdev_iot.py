#! /usr/bin/env python3
# -*- coding: UTF-8 -*-

"""
gdev_iot.py     IoT Device support using a MQTT connection
                including support of Tasmota devices
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


"""
Installing MQTT on Ubuntu:
see: https://www.digitalocean.com/community/tutorials/how-to-install-and-secure-the-mosquitto-mqtt-messaging-broker-on-ubuntu-16-04
site includes steps to set up secure server!

To install the software on a Linux system:
    sudo apt-get install mosquitto mosquitto-clients

Testing MQTT, assuming mosqitto running on mysite.com:
Subscribe in terminal 1:
    mosquitto_sub -v -h mysite.com -t ambiomon/#
    example: mosquitto_sub -h test.mosquitto.org -t "geigerlog/#" -v

Publish in terminal 2:
    mosquitto_pub -h mysite.com -t ambiomon/temp -m "hello world"
    example: mosquitto_pub -h test.mosquitto.org -t geigerlog/temp -m "hello world"

You should see in terminal 1:
    ambiomon/temp hello world
    geigerlog/temp hello world

    or with GLDataServer running on Raspi with current setting:
        geigerlog/data 456,2.933,25,3.425121,,,,,21.9,1017.697,41.201,607.5

To use test.mosquitto.org with user and password:
mosquitto_sub -h test.mosquitto.org -t "geigerlog/#" -u rw -P readwrite -p 1884 -v

Important consideration paho-mqtt
see:  https://github.com/eclipse/paho.mqtt.python/issues/514

Tasmota Device Manager:
https://github.com/jziolkowski/tdm
GUI application to discover and monitor devices flashed with https://github.com/arendst/Sonoff-Tasmota

install:    pip install tdmgr       (broader: https://github.com/jziolkowski/tdm/wiki/Prerequisites-installation-and-running)
CAUTION:    Successfully uninstalled PyQt5-5.15.9, Successfully installed PyQt5-5.14.2 tdmgr-0.2.11
            Installing tdmgr.py is Downgrading PyQt5 !!!
start:      tdmgr.py

Tasmota Usage with test.mosquitto.org with user and pw
mosquitto_sub -h test.mosquitto.org -t "cmnd/tasmota_switch/#" -u rw -P readwrite -p 1884 -v
mosquitto_sub -h test.mosquitto.org -t "stat/tasmota_switch/#" -u rw -P readwrite -p 1884 -v
mosquitto_sub -h test.mosquitto.org -t "tele/tasmota_switch/#" -u rw -P readwrite -p 1884 -v

Calibration Procedure:
    Verify the Power reading in the web UI (optionally with the power meter as well) for the expected wattage. Adjust
    the power offset if needed (in Watts):
    PowerSet 60.0
    If you're using something other than a 60W bulb, enter your load's power rating

    Verify the Voltage reading. Adjust the voltage offset if needed (in Volts):
    VoltageSet <voltage>
    Replace <voltage> with your standard voltage or with reading on your multi-meter if you have one. Your voltage
    will vary depending on the electrical standards and your electrical grid

Configuring Tasmota Plug:
    - in tablet select WLAN tasmota-xyz....
    - in browser enter 192.168.4.1 and select own network
    - in tablet WLAN config select own network
    - in browser enter ip of new plug and configure
"""

__author__          = "ullix"
__copyright__       = "Copyright 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024"
__credits__         = [""]
__license__         = "GPL3"

from gsup_utils   import *


def initIoT():
    """Initialize the client and set all Callbacks"""

    defname = "initIoT: "
    dprint(defname)
    setIndent(1)

    g.Devices["IoT"][g.DNAME] = "IoT Device"
    errmsg                    = ""                                  # to be returned; no error if empty
    g.iot_data                = {}                                  # holds the new data
    for vname in g.VarsCopy:  g.iot_data[vname] = g.NAN             # fill with NANs

    # set auto configuration; default is WITHOUT authorization
    if g.IoTBrokerIP         == "auto": g.IoTBrokerIP           = "test.mosquitto.org"
    if g.IoTBrokerPort       == "auto": g.IoTBrokerPort         = 1883
    if g.IoTTimeout          == "auto": g.IoTTimeout            = 5
    if g.IoTUsername         == "auto": g.IoTUsername           = ""
    if g.IoTPassword         == "auto": g.IoTPassword           = ""
    if g.IoTBrokerFolder     == "auto": g.IoTBrokerFolder       = "geigerlog/"

    # set client devices to default if on auto
    #                                                             activ, cmnd topic,                       cmnd payload, variables
    if g.IoTClientDataGL     == "auto": g.IoTClientDataGL       = "y,    geigerlog/cmnd/GLdevice,          SEND,         CPM, CPS, CPM1st, CPS1st, CPM2nd, CPS2nd, CPM3rd, CPS3rd, Temp, Press, Humid, Xtra"
    if g.IoTClientTasmotaGL1 == "auto": g.IoTClientTasmotaGL1   = "y,    geigerlog/cmnd/tasmotaGL1/Status, 8,            CPM, CPS, CPM1st"
    if g.IoTClientTasmotaGL2 == "auto": g.IoTClientTasmotaGL2   = "y,    geigerlog/cmnd/tasmotaGL2/Status, 8,            CPS1st, CPM2nd, CPS2nd"
    if g.IoTClientTasmotaGL3 == "auto": g.IoTClientTasmotaGL3   = "y,    geigerlog/cmnd/tasmotaGL3/Status, 8,            CPM3rd, CPS3rd, Temp"
    if g.IoTClientTasmotaGL4 == "auto": g.IoTClientTasmotaGL4   = "y,    geigerlog/cmnd/tasmotaGL4/Status, 8,            Press, Humid, Xtra"

    # reconfigure Client config
    # limit to max=3 splits to have all variables in one single value (to avoid further split by comma)
    g.IoTClientConfig = {}
    g.IoTClientConfig["client#0"] = g.IoTClientDataGL       .split(",", 3)
    g.IoTClientConfig["client#1"] = g.IoTClientTasmotaGL1   .split(",", 3)
    g.IoTClientConfig["client#2"] = g.IoTClientTasmotaGL2   .split(",", 3)
    g.IoTClientConfig["client#3"] = g.IoTClientTasmotaGL3   .split(",", 3)
    g.IoTClientConfig["client#4"] = g.IoTClientTasmotaGL4   .split(",", 3)
    # for clc in g.IoTClientConfig: rdprint(defname, "clc: ", clc, "  IoTClientConfig: ", g.IoTClientConfig[clc])

    for clc in g.IoTClientConfig:
        # rdprint(defname, "clc: ", clc)
        g.IoTClientConfig[clc][0] = True if "y" in g.IoTClientConfig[clc][0] else False         # active
        g.IoTClientConfig[clc][1] = g.IoTClientConfig[clc][1].strip()                           # topic
        g.IoTClientConfig[clc][2] = g.IoTClientConfig[clc][2].strip()                           # cmnd
        g.IoTClientConfig[clc][3] = g.IoTClientConfig[clc][3].strip().replace(" ", "")          # Variables
        dprint(defname, "clc: ", clc, "  IoTClientConfig: ", g.IoTClientConfig[clc])

    # set mqtt client
    # protocol: Can be either MQTTv31 or MQTTv311; MQTTv31 is deprecated - do NOT use!
    g.iot_client = mqtt.Client(client_id="", clean_session=True, userdata=None, protocol=mqtt.MQTTv311)
    g.iot_client.user_data_set(0)    # change userdata

    # set callbacks
    g.iot_client.on_connect       = on_connect
    g.iot_client.on_subscribe     = on_subscribe
    g.iot_client.on_message       = on_message
    g.iot_client.on_publish       = on_publish
    g.iot_client.on_disconnect    = on_disconnect
    # g.iot_client.on_log           = on_log # set client logging

    # connect
    dprint(defname + "connecting to: IoTBrokerIP: '{}', IoTBrokerPort: {}".format(g.IoTBrokerIP, g.IoTBrokerPort))
    try:
        # if username is set, then configure for login with username + pw
        if g.IoTUsername > "":  g.iot_client.username_pw_set(username=g.IoTUsername, password=g.IoTPassword)

        # "The keep alive processing can be turned off by setting the interval to 0 on connect."
        # g.iot_client.connect(g.IoTBrokerIP, port=g.IoTBrokerPort, keepalive=60)
        g.iot_client.connect(g.IoTBrokerIP, port=g.IoTBrokerPort, keepalive=180)

    except Exception as e:
        srcinfo = defname + "ERROR: Connection to IoT server failed"
        exceptPrint(e, srcinfo)
        g.iot_client     = None
        errmsg += "\nERROR: Connection failed using: server IP='{}', port={}".format(g.IoTBrokerIP, g.IoTBrokerPort)
        errmsg += "\nERROR: '{}'".format(sys.exc_info()[1])
        errmsg += "\n{} not connected. Is server offline? Verify server IP, server port, username, and password".format(g.Devices["IoT"][g.DNAME])

        setIndent(0)
        return errmsg

    # start the loop
    g.iot_client.loop_start()                                                                   # threaded loop; must be stopped on exit!
    dprint(defname + "Threaded loop was started")

    # wait for confirmation of connection
    starttime = time.time()
    timeout   = True
    while time.time() < (starttime  + g.IoTTimeout):
        if g.IoTconnectionState:
            timeout = False
            g.IoTconnectDuration = "{:0.2f} sec".format(time.time() - starttime)
            dprint(defname + "Connected after: {}".format(g.IoTconnectDuration))
            break
        time.sleep(0.05)

    if timeout:
        # no callback received; i.e. no connection
        dprint(defname + "IoT connection timed out ({} sec)".format(g.IoTTimeout), debug=True)
        errmsg += "\nERROR: Connection to IoT server failed; IoT inactivated"
        g.IoTconnectDuration = "Failure, timeout after {} sec".format(g.IoTTimeout)             # for use in info
    else:
        # successful AND confirmed connect!
        varlist = ""
        for clc in g.IoTClientConfig:                                                           # each device
            if g.IoTClientConfig[clc][0]:                                                       # activated?
                varlist += ", ".join(a for a in g.IoTClientConfig[clc][3].split(",")) + ", "
        g.IoTVariables = setLoggableVariables("IoT", varlist)

    g.Devices["IoT"][g.CONN] = g.IoTconnectionState

    g.IoTThreadRun         = True
    g.IoTThread            = threading.Thread(target = IoTThreadTarget)
    g.IoTThread.daemon     = True                                                               # must come before start: makes threads stop on exit!
    g.IoTThread.start()

    setIndent(0)
    return errmsg


def terminateIoT():
    """opposit of init ;-)"""

    if g.iot_client is None: return

    defname = "terminateIoT: "

    dprint(defname)
    setIndent(1)

    # stop MQTT thread
    dprint(defname + "stopping MQTT client.loop")
    g.iot_client.loop_stop()

    # disconnect MQTT client
    dprint(defname + "disconnecting MQTT client")
    g.iot_client.disconnect()    # output printed in callback

    # shut down IoT thread
    dprint(defname, "stopping IoT thread")
    g.IoTThreadRun        = False
    g.IoTThread.join()                 # "This blocks the calling thread until the thread
                                       #  whose join() method is called is terminated."

    dprint(defname + "setting MQTT client to: None")
    g.iot_client = None

    # wait for confirmation of dis-connection
    starttime = time.time()
    timeout   = True
    while time.time() < (starttime  + g.IoTTimeout):
        if not g.IoTconnectionState:
            timeout = False
            break
        time.sleep(0.05)

    # verify that IoT thread has ended, but wait not longer than 5 sec (takes 0.006...0.016 ms)
    start = time.time()
    while g.IoTThread.is_alive() and (time.time() - start) < 5:
        pass
    msgalive = "Yes" if g.IoTThread.is_alive() else "No"
    dprint(defname, "IoT thread-status: alive: {}, waiting took:{:0.1f} ms".format(msgalive, 1000 * (time.time() - start)))

    if timeout:
        dprint(defname, "IoT dis-connection timed out ({} sec)".format(g.IoTTimeout), debug=True)
        QueuePrint("ERROR: Dis-Connection from IoT server failed; IoT inactivated")
        retval = "timeout"
    else:
        retval = ""

    g.Devices["IoT"][g.CONN] = g.IoTconnectionState

    dprint(defname, "Terminated")
    setIndent(0)

    return retval


def getInfoIoT(extended=False):
    """Info on the IoT Device"""

    IoTInfo = "Configured Connection:        MQTT on '{}':{}  topic:'{}'\n".\
        format(g.IoTBrokerIP, g.IoTBrokerPort, g.IoTBrokerFolder)

    if not g.Devices["IoT"][g.CONN]: return IoTInfo + "<red>Device is not connected</red>"

    IoTInfo     += "Connected Device:             {}\n".format(g.Devices["IoT"][g.DNAME])
    IoTInfo     += "Configured Variables overall: {}\n".format(g.IoTVariables)
    IoTInfo     += "Client Devices:               {}\n".format("")
    for i, clc in enumerate(g.IoTClientConfig):
        # rdprint(defname, "clc: ", clc)
        if g.IoTClientConfig[clc][0]:  IoTInfo     += "   Client Device #{}:          {}\n".format(i, "Topic: '{}' Cmnd: '{}' Variables: '{}'".format(g.IoTClientConfig[clc][1], g.IoTClientConfig[clc][2], g.IoTClientConfig[clc][3]))
        else:                          IoTInfo     += "   Client Device #{}:          {}\n".format(i, "Not activated")

    IoTInfo     += getTubeSensitivities(g.IoTVariables)

    if extended == True:
        IoTInfo += "\n"
        IoTInfo += "MQTT Timeout:                 {} sec\n".format(g.IoTTimeout)
        IoTInfo += "MQTT Username:                {}\n".format(g.IoTUsername)
        IoTInfo += "MQTT Password:                {}\n".format(g.IoTPassword)
        IoTInfo += "Duration of connecting:       {}\n".format(g.IoTconnectDuration)

    return IoTInfo


def IoTThreadTarget():
    """Thread triggers readings about some e.g. 300ms before next cycle is due"""

    defname = "IoTThreadTarget: "

    # find the count of active devices
    activeCount = 0
    for clc in g.IoTClientConfig:
        if g.IoTClientConfig[clc][0]: activeCount += 1

    # set margin of headstart at 100 ms as base, plus 50 ms more for each active device
    headstart = 0.100 + activeCount * 0.050

    while g.IoTThreadRun:

        # go to sleep until some ms before next cycle begins
        # time.sleep(max(0, g.nexttime - time.time() - 0.3015))     # for Tasmota
                                                                    # Bei einem Stecker:
                                                                    # Dauer 60 ... 120 nahezu gleichmäßig verteilt. Einzelne Escapes
                                                                    # bis 185 ms
                                                                    #       Avg    ±StdDev    ±SDev%  Variance     Min ... Max
                                                                    #       91.292 ±19.024    ±20.8%    361.91  58.295  184.31
                                                                    # Bei 4 Steckern:
                                                                    # zweigipfelige Verteilung, 1. Gipfel bei 120 ms, 2.Gipfel bei 180 ms (??)
                                                                    #       Avg     ±StdDev    ±SDev%  Variance     Min ... Max
                                                                    #       130.997 ±31.073    ±23.7%    965.56  84.192  299.94
                                                                    # --> 300 ms ausreichend: 100 ms Basis + 50 ms für jedes device
                                                                    #     100 + 4 * 50 = 300 ms !

        # time.sleep(max(0, g.nexttime - time.time() - 0.120))      # for GeigerLog calls of Simul_IoTClient.py
                                                                    # minimale Dauer ist 45 ms. Allerdings sehr häufige Exkusions
                                                                    # bis über 100 ms. Daher 120 ms gewählt
                                                                    #       Avg    ±StdDev    ±SDev%  Variance     Min ... Max
                                                                    #       52.338 ±16.131    ±30.8%    260.22  41.192     107

        time.sleep(max(0, g.nexttime - time.time() - headstart))    # for GeigerLog calls AND all 4 Tasmota plugs
                                                                    # Dauer ist 90 ... 300 ms; Ausreißer bis 700 ms
                                                                    # zweigipfelige Verteilung, 1. Gipfel bei 110 ms, 2.Gipfel bei 190 ms (??)
                                                                    #       Avg     ±StdDev    ±SDev%  Variance     Min ... Max
                                                                    #       139.230 ±41.765    ±30.0%    1744.3  87.107   675.9
                                                                    # --> 350 ms ausreichend: 100 ms Basis + 50 ms für jedes device
                                                                    #     100 + 5 * 50 = 350 ms!



        oldnexttime = g.nexttime

        # command the devices to send data; but only if logging
        if g.logging:
            g.iot_threadstart = time.time()
            # mdprint("to go: {:0.0f} ms".format(1000 * (g.nexttime - time.time())))
            # full for-loop takes 1 ... 6 ms
            for clc in g.IoTClientConfig:
                if g.IoTClientConfig[clc][0]:                           # send command only if activated
                    topic = g.IoTClientConfig[clc][1]
                    payld = g.IoTClientConfig[clc][2]
                    if payld != "None":
                        success, publishID = g.iot_client.publish(topic, payld, qos=1, retain=False)
                        sucfail = "Yes" if success == 0 else "No"
                        mdprint(defname, "PUBLISH:  topic: {}  payld: {}  success: {}  publishID: {}".format(topic, payld, sucfail, publishID))
                    else:
                        mdprint(defname, "PUBLISH:  topic: {}  payld: {}  - No need for any publishing".format(topic, payld))
            # mdprint(defname, "dur: {:0.3f} ms".format(1000 * (time.time() - g.iot_threadstart)))        # 1 ... 6 ms

        # wait until the next cycle is underway; i.e. g.nexttime changes
        while oldnexttime == g.nexttime:
            if not g.IoTThreadRun: break
            time.sleep(0.010)


def getValuesIoT(varlist):
    """Read all IoT data from the buffer g.iot_data"""

    start = time.time()

    defname = "getValuesIoT: "

    alldata = {}
    for vname in varlist:
        alldata[vname]    = applyValueFormula(vname, g.iot_data[vname], g.ValueScale[vname])
        g.iot_data[vname] = g.NAN   # reset value to NAN

    vprintLoggedValues(defname, varlist, alldata, (time.time() - start) * 1000)

    return alldata


###############################################################################
# BEGIN MQTT Callbacks
###############################################################################

# in all Callbacks:
#
# Client:       is a python object
# userdata:     as defined in Client call and modified in on_message
#               its type is as defined initially: can be Nonetype, str, int, float, ...
# msg:          the message coming from the IoT device; an instance of MQTTMessage, a
#               class with members topic, payload, qos, retain.
#                   type of msg.topic:   <class 'str'>
#                   type of msg.payload: <class 'bytes'>
#                   type of msg.qos:     <class 'int'>
#                   type of msg.retain:  <class 'int'>
# flags:        a dict that contains response flags from the broker
# rc:           indicates the connecion / disconnection state
# mid:          the message ID
# granted_qos:  a list of integers that give the QoS level the broker has granted for each of the different subscription requests
#
# NOTE: if publishing is more frequent than reading, only the last published data will be read


def on_message(client, userdata, msg):
    """The callback for when a PUBLISH message is received from the server"""

    #################################################################################################################################
    def printMsg(msg):
        mdprint(">IoT " + defname + "topic:   {}  qos:{}  retain:{}  userdata:{}".format(msg.topic, msg.qos, msg.retain, userdata))
        mdprint(">IoT " + defname + "payload: {}"                                .format(msg.payload))
    #################################################################################################################################

    defname = "on_message: "

    # rdprint(defname, "Userdata: ", userdata, type(userdata))
    client.user_data_set(userdata + 1)

    # ignore everything coming when not logging
    if not g.logging: return

    # data coming in GeigerLog format, like from: Simul_IoTClient.py
    if "GLdevice" in msg.topic and b"DATA" in msg.payload:                # accepts only 'DATA' payload on 'GLdevice'!

        if g.IoTClientConfig["client#0"][0]:  # is activated?
            printMsg(msg)
            pljson = json.loads(msg.payload)
            # rdprint("pljson: ", pljson)

            for vname in g.IoTClientConfig["client#0"][3].split(","):
                # rdprint("vname: ", vname)
                try:                    g.iot_data[vname] = pljson["DATA"][vname]
                except Exception as e:  g.iot_data[vname] = g.NAN

    # data coming from tasmota socket
    elif "tasmota" in msg.topic and b"ENERGY" in msg.payload and b"StatusSNS" in msg.payload:   # only the STATUS8 response

        if   "tasmotaGL1" in msg.topic: client = "client#1"
        elif "tasmotaGL2" in msg.topic: client = "client#2"
        elif "tasmotaGL3" in msg.topic: client = "client#3"
        elif "tasmotaGL4" in msg.topic: client = "client#4"

        if g.IoTClientConfig[client][0]:  # is activated?
            printMsg(msg)
            pljson = json.loads(msg.payload)

            sensor = ["Voltage", "Current", "Power"]
            vars   = g.IoTClientConfig[client][3].split(",")
            for i, devvname in enumerate(vars):
                devvname = devvname.strip()
                try:
                    if devvname in g.VarsCopy:
                        g.iot_data[devvname] = float(pljson["StatusSNS"]["ENERGY"][sensor[i]])
                except Exception as e:
                    exceptPrint(e, "tasmota: topic: " + msg.topic + "  devvname: " + devvname)
                    g.iot_data[devvname] = g.NAN


def on_connect(client, userdata, flags, rc):
    """The callback for when the client receives a CONNACK response from the server"""

    defname = "on_connect: "

    # The value of rc indicates success or not:
    strrc = {
                0: "Connection successful",
                1: "Connection refused - incorrect protocol version",
                2: "Connection refused - invalid g.iot_client identifier",
                3: "Connection refused - server unavailable",
                4: "Connection refused - bad username or password",
                5: "Connection refused - not authorised",
                # 6-255: Currently unused.
            }

    src = strrc[min(5, rc)]

    if rc == 0: g.IoTconnectionState = True
    else:       g.IoTconnectionState = False

    dprint(">IoT: on_connect: Client connected:")
    dprint(">        {:20s}: {}".format("with userdata"     , userdata))
    dprint(">        {:20s}: {}".format("with flags"        , flags))
    dprint(">        {:20s}: {}".format("with result"       , src), " (Result Code: {})".format(rc))

    # Subscribing within 'on_connect()' means that if we lose the connection and
    # reconnect, then subscriptions will be renewed.
    # g.iot_client.subscribe("$SYS/#") # gives huge amount of traffic! Careful!!!
    g.iot_client.subscribe(g.IoTBrokerFolder + "#", qos=2)

    dprint(">IoT: ", defname, "IoTconnectionState: ", g.IoTconnectionState)


def on_disconnect (client, userdata, rc):
    """When the client has sent the disconnect message it generates an on_disconnect() callback."""

    defname = "on_disconnect: "

    # The rc parameter indicates the disconnection state.
    # If MQTT_ERR_SUCCESS (0), the callback was called in response to a disconnect() call.
    # If any other value the disconnection was unexpected, such as might be
    # caused by a network error."""

    strrc = {
                0: "MQTT_ERR_SUCCESS",
                1: "Unexpected disconnection",
            }

    src = strrc[min(1, rc)]

    g.IoTconnectionState = False # whatever the cause - it is disconnected

    dprint(">IoT: on_disconnect: Client disconnected:")
    dprint(">        {:20s}: {}".format("with userdata"     , userdata))
    dprint(">        {:20s}: {}".format("with result"       , src), "(Result Code: {})".format(rc))

    dprint(">IoT: ", defname, "IoTconnectionState: ", g.IoTconnectionState)


def on_subscribe(client, userdata, mid, granted_qos):
    """Callback when a subscribe has occured"""

    defname = "on_subscribe: "

    dprint(">IoT: on_subscribe: Topic subscribed:")
    dprint(">        {:20s}: {}".format("with userdata"     , userdata))
    dprint(">        {:20s}: {}".format("with mid"          , mid))
    dprint(">        {:20s}: {}".format("with granted_qos"  , granted_qos))

    dprint(">IoT: ", defname, "IoTconnectionState: ", g.IoTconnectionState)


def on_publish(client, userdata, mid):
    """ Called when a message that was to be sent using the publish() call has completed transmission to the broker"""

    defname = "on_publish: "

    # mdprint(">IoT ", defname, "userdata:{}  publishID:{}".format(userdata, mid))
    mdprint(">IoT ", defname, "Ok for publishID:{}".format(mid))


def on_log(client, userdata, level, buf):
    rdprint("log: ",buf)


###############################################################################
# END MQTT Callbacks
###############################################################################

