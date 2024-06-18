#! /usr/bin/env python3
# -*- coding: utf-8 -*-

"""
rmqttc.py - DataServer's MQTT Client

include in programs with:
    import rmqttc
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

from   rutils   import *


def initMQTT():
    """Initialize the client and set all Callbacks"""

    defname = "initMQTT: "
    errmsg  = ""

    dprint(defname)
    setIndent(1)

    # import the paho-mqtt module
    try:
        # https://pypi.org/project/paho-mqtt/
        import paho.mqtt.client as mqtt
        from paho.mqtt      import __version__  as paho_version
        # print("paho-mqtt version", paho_version)
        g.versions["paho-mqtt"] = paho_version

    except Exception as e:
        msg  = "\nPython module 'paho-mqtt' was not found\n"
        msg += "In order to run Raspi as IoT device this module is required\n"
        msg += "Verify that 'paho-mqtt' is installed"
        exceptPrint(e, msg)
        edprint("Halting DataServer")
        sys.exit()

    # set configuration
    if g.IoTBrokerIP     == "auto": g.IoTBrokerIP     = "test.mosquitto.org"
    if g.IoTBrokerPort   == "auto": g.IoTBrokerPort   = 1883
    if g.IoTBrokerFolder == "auto": g.IoTBrokerFolder = "/"
    if g.IoTTimeout      == "auto": g.IoTTimeout      = 5

    # set client
    # see: https://pypi.org/project/paho-mqtt/
    # protocol - the version of the MQTT protocol to use for this client. Can be either MQTTv31, MQTTv311 or MQTTv5
    #            3.1 and 3.11 can use same code; only Broker is different
    #            5.0          requires DIFFERENT code!
    # userdata   can be anything
    #
    # g.iot_client = mqtt.Client(client_id="", clean_session=True, userdata=None, protocol=mqtt.MQTTv311)
    g.iot_client = mqtt.Client(client_id="", clean_session=True, userdata="DataServer", protocol=mqtt.MQTTv311)

    # set callbacks
    g.iot_client.on_connect       = on_connectMQTT
    g.iot_client.on_publish       = on_publishMQTT
    g.iot_client.on_disconnect    = on_disconnectMQTT

    # connect
    try:
        g.iot_client.connect(g.IoTBrokerIP, port=g.IoTBrokerPort, keepalive=60)
        errmsg += "Ok, connected to:'{}'  Port:{}".format(g.IoTBrokerIP, g.IoTBrokerPort)
        success = True
    except Exception as e:
        srcinfo = defname + "ERROR: Connection to IoT Broker failed"
        exceptPrint(e, srcinfo)
        g.iot_client     = None
        errmsg += "\nERROR: Connection failed using: Broker IP='{}', port={}".format(g.IoTBrokerIP, g.IoTBrokerPort)
        errmsg += "\nERROR: '{}'".format(sys.exc_info()[1])
        errmsg += "\nIoT Device not connected. Is Broker offline? Verify Broker IP and Broker port"
        success = False

    # must start loop to get on_connectMQTT callback
    # threaded loop; must be stopped on exit!
    g.iot_client.loop_start()
    dprint(defname + "Threaded loop was started")

    # wait for confirmation of connection
    starttime = time.time()
    timeout   = True
    while time.time() < (starttime  + g.IoTTimeout):
        if g.IoTconnected:
            timeout = False
            # dprint(defname + "Connected after: {:0.2f} sec".format((time.time() - starttime)))
            errmsg += "  after:{:0.3f} sec".format((time.time() - starttime))
            break
        time.sleep(0.05)

    if timeout:
        # got no callback signalling a connection
        dprint(defname + "IoT connection timed out ({} sec)".format(g.IoTTimeout))
        errmsg += "\nERROR: Connection to IoT Broker failed; IoT+ inactivated"

    setIndent(0)
    return (success, errmsg)


def on_connectMQTT(client, userdata, flags, rc):
    """The callback for when the client receives a CONNACK response from the Broker"""
    # userdata as defined in Client call
    # flags is a dict that contains response flags from the broker

    defname = "on_connectMQTT: "

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

    # dprint(">IoT: " + defname + "userdata: ", userdata)
    omsg = ">IoT: " + defname + "Client connection attempt ended with result: '{}'".format(strrc[rc])
    if rc == 0: gdprint(omsg)
    else:       rdprint(omsg)

    g.IoTconnected = True if rc == 0 else False


def on_disconnectMQTT (client, userdata, rc):
    """When the client has sent the disconnect message an on_disconnectMQTT() callback is generated"""

    # userdata as defined in Client call
    # The rc parameter indicates the disconnection state.
    # If MQTT_ERR_SUCCESS (0), the callback was called in response to a disconnect() call.
    # If any(!) other value the disconnection was unexpected, such as caused by a network error.
    # !!! -> rc can have ANY value 1 ... 255 !!!

    defname = "on_disconnectMQTT: "

    strrc = {
                0: "MQTT_ERR_SUCCESS",
                1: "Unexpected disconnection",
                # 1 - 255: "Unexpected disconnection"
            }

    # dprint(">IoT: " + defname + "userdata: ", userdata)
    omsg = ">IoT: " + defname + "Client disconnection attempt ended with result: '{}'".format(strrc[0 if rc == 0 else 1])
    if rc == 0: gdprint(omsg)
    else:       rdprint(omsg)

    g.IoTconnected = False if rc == 0 else True


def on_publishMQTT(client, userdata, mid):
    """Callback called when a message that was sent using the publish() call has completed transmission to the broker"""
    # Client is python object
    # userdata as defined in Client call
    # if publishing is more frequent than reading, only the last published data will be read

    defname = "on_publishMQTT: "
    g.iot_CallbackID = mid


def publishMQTT():
    """publish data to MQTT"""

    # see: https://github.com/eclipse/paho.mqtt.python/issues/514
    # see: https://pypi.org/project/paho-mqtt/
    # topic: on_publish()
    #        cmd:  on_publish(client, userdata, mid)
    # Called when a message that was to be sent using the publish() call has completed transmission to the
    # broker. For messages with QoS levels 1 and 2, this means that the appropriate handshakes have completed.
    # For QoS 0, this simply means that the message has left the client. The mid variable matches the mid
    # variable returned from the corresponding publish() call, to allow outgoing messages to be tracked.
    # This callback is important because even if the publish() call returns success, it does not always mean
    # that the message has been sent. (!!!)
    #
    # duration of publish from start to confirmation is 15 ...ms, avg: 70ms

    defname = "publishMQTT: "

    bdata = g.CollectedData  # gets the last-collected data

# ### testing ##########################
#     #replace original Xtra value with last publish_duration
#     # rdprint(defname, "orig bdata: ", bdata)
#     bdata = bdata [:bdata.rfind(b",")] + bytes(",{:0.2f}".format(g.iot_publishDur), "utf-8")
#     # rdprint(defname, "new  bdata: ", bdata)
# ######################################

    success, publishID  = g.iot_client.publish("geigerlog/data", bdata, qos=1) # ret==0 indicates success

    # verify publish succeeded by comparing publishID with callbackID
    pstart  = time.time()
    timeout = True
    confirm = False
    while time.time() < (pstart  + g.IoTTimeout):
        if g.iot_CallbackID is not None:
            if g.iot_CallbackID == publishID:   confirm = True
            else:                               confirm = False
            g.iot_CallbackID = None
            timeout = False
            break
        time.sleep(0.005)
    dur = 1000 * (time.time() - pstart)

    g.iot_publishDur = dur

    pmsg = defname
    if not timeout: pmsg += " {}  @id:{}  Data:{} dur:{:0.1f} ms".format("SUCCESS" if confirm else "FAILURE", publishID, bdata, dur)
    else:           pmsg += " {}  @id:{}  Data:{} dur:{:0.1f} ms".format("TIMEOUT", "is missing", bdata, dur)

    if confirm:     gdprint(pmsg )
    else:           rdprint(pmsg )


def terminateMQTT():
    """terminate MQTT; incl threads"""

    if g.iot_client == None: return

    defname = "terminateMQTT: "

    dprint(defname)
    setIndent(1)

    dprint(defname + "stopping MQTT client loop")
    g.iot_client.loop_stop()

    dprint(defname + "disconnecting MQTT client")
    g.iot_client.disconnect()    # output printed in callback

    dprint(defname + "setting MQTT client to None")
    g.iot_client = None

    # wait for confirmation of dis-connection
    starttime = time.time()
    timeout   = True
    while time.time() < (starttime  + g.IoTTimeout):
        if not g.IoTconnected:
            timeout = False
            break
        time.sleep(0.05)

    if timeout:
        dprint("MQTT dis-connection timed out ({} sec)".format(g.IoTTimeout))
        edprint("ERROR: Dis-Connection from MQTT failed; MQTT inactivated nevertheless")

    dprint("Terminated MQTT client")

    setIndent(0)

