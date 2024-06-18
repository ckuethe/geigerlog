#! /usr/bin/env python3
# -*- coding: UTF-8 -*-

"""
RadMonPlus support using a MQTT connection
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
    mosquitto_sub -h test.mosquitto.org -t "geigerlog/#" -v

Publish in terminal 2:
    mosquitto_pub -h mysite.com -t ambiomon/temp -m "hello world"
    mosquitto_pub -h test.mosquitto.org -t geigerlog/temp -m "hello world"
You should see in terminal 1:
    ambiomon/temp hello world
    geigerlog/temp hello world
"""

__author__          = "ullix"
__copyright__       = "Copyright 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024"
__credits__         = [""]
__license__         = "GPL3"

from gsup_utils   import *


RMconnectionState = False
RMconnectDuration = ""

###############################################################################
# BEGIN MQTT Callbacks
###############################################################################

def on_connect(client, userdata, flags, rc):
    """The callback for when the client receives a CONNACK response from the server"""

    global RMconnectionState

    defname = "on_connect: "

    # The value of rc indicates success or not:
    strrc = {
                0: "Connection successful",
                1: "Connection refused - incorrect protocol version",
                2: "Connection refused - invalid g.rm_client identifier",
                3: "Connection refused - server unavailable",
                4: "Connection refused - bad username or password",
                5: "Connection refused - not authorised",
                # 6-255: Currently unused.
            }

    if rc < 6:     src = strrc[rc]
    else:          src = "Unexpected Connection Response"
    g.RMconnect = (rc, src)

    if rc == 0: RMconnectionState = True
    else:       RMconnectionState = False

    dprint(">RadMon: on_connect: Client connected:")
    dprint(">        {:20s}: {}".format("with userdata"     , userdata))
    dprint(">        {:20s}: {}".format("with flags"        , flags))
    dprint(">        {:20s}: {}".format("with result"       , src), " (Result Code: {})".format(rc))

    # Subscribing within 'on_connect()' means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    #g.rm_client.subscribe("$SYS/#") # gives huge amount of traffic! Careful!!!
    g.rm_client.subscribe(g.RMServerFolder + "#", qos=2)

    dprint(">RadMon: on_connect: RMconnectionState: ", RMconnectionState)


def on_disconnect (client, userdata, rc):
    """When the client has sent the disconnect message it generates an on_disconnect() callback."""

    global RMconnectionState

    defname = "on_disconnect: "

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
    g.RMdisconnect = (rc, src)

    RMconnectionState = False

    dprint(">RadMon: on_disconnect: Client disconnected:")
    dprint(">        {:20s}: {}".format("with userdata"     , userdata))
    dprint(">        {:20s}: {}".format("with result"       , src), "(Result Code: {})".format(rc))

    dprint(">RadMon: on_disconnect: RMconnectionState: ", RMconnectionState)


def on_subscribe(client, userdata, mid, granted_qos):
    """Callback when a subscribe has occured"""

    global RMconnectionState

    defname = "on_subscribe: "

    dprint(">RadMon: on_subscribe: Topic subscribed:")
    dprint(">        {:20s}: {}".format("with userdata"     , userdata))
    dprint(">        {:20s}: {}".format("with mid"          , mid))
    dprint(">        {:20s}: {}".format("with granted_qos"  , granted_qos))

    dprint(">RadMon: on_subscribe: RMconnectionState: ", RMconnectionState)


def on_message(client, userdata, msg):
    """The callback for when a PUBLISH message is received from the server"""
    # Client is object: <paho.mqtt.client.Client object at 0x7f241cdf3010>
    # msg is object   : <paho.mqtt.client.MQTTMessage object at 0x7f2417f06ea0>
    #      an instance of MQTTMessage.
    #      this is a class with members topic, payload, qos, retain.
    #      type of msg.payload: <class 'bytes'>

    global RMconnectionState

    defname = "on_message: "

    vprint(">RadMon: on_message: topic: {:20s}  qos: {}  retain: {}  payload: {:10s}".format(msg.topic, msg.qos, msg.retain, str(msg.payload)))

    try:
        if msg.payload > b"": msg_payload = float(msg.payload) # if msg.payload == '' (empty) then float failes!
        else:                 msg_payload = g.NAN
    except Exception as e:
        msg = "RadMon: on_message: float(msg.payload) failed, msg.payload ='{}'".format(msg.payload)
        exceptPrint(e, msg)
        msg_payload = g.NAN

    if type(msg) == "str":
        edprint(defname, "msg is string - has not topic!")
    else:
        try:
            if   msg.topic == g.RMServerFolder + "temp":     g.rm_temp   = msg_payload    # T
            elif msg.topic == g.RMServerFolder + "pressure": g.rm_press  = msg_payload    # P
            elif msg.topic == g.RMServerFolder + "humid":    g.rm_hum    = msg_payload    # H
            elif msg.topic == g.RMServerFolder + "cpm":      g.rm_cpm    = msg_payload    # CPM*
            elif msg.topic == g.RMServerFolder + "rssi":     g.rm_rssi   = msg_payload    # rssi
            else:  print("msg.topic: {}, msg.payload: {}".format(msg.topic, msg_payload)) # only does it not used
        except Exception as e:
            exceptPrint(e, "Failure in RadMon reading Payload")


    # cdprint(">RadMon: {} RMconnectionState: {} userdata: {}".format(defname, RMconnectionState, userdata))


def on_publish(client, userdata, mid):
    """ Called when a message that was to be sent using the publish() call
    has completed transmission to the broker"""
    # Client is object: <paho.mqtt.client.Client object at 0x7f241cdf3010>

    global RMconnectionState

    defname = "on_publish: "

    cdprint(">RadMon: {} RMconnectionState:{} userdata:{} messageID:{}".format(defname, RMconnectionState, userdata, mid))


###############################################################################
# END MQTT Callbacks
###############################################################################


def getValuesRadMon(varlist):
    """Read all RadMon data; return only when complete"""

    # ret= g.rm_client.publish("geigerlog/temp", 31.2345)
    # ret= g.rm_client.publish("geigerlog/pressure", 1031.2345)
    # ret= g.rm_client.publish("geigerlog/humid", 55.678)
    # ret= g.rm_client.publish("geigerlog/cpm", 123.4567)
    # time.sleep(0.1)

    start = time.time()

    defname = "getValuesRadMon: "

    alldata = {}

    dataIncomplete = False
    for vname in varlist:
        if   vname == "Temp" and g.rm_temp  is None :
            dataIncomplete = True
            break
        elif vname == "Press" and g.rm_press is None :
            dataIncomplete = True
            break
        elif vname == "Humid" and g.rm_hum   is None :
            dataIncomplete = True
            break
        elif vname in ("CPM", "CPM1st", "CPM2nd", "CPM3rd") and g.rm_cpm is None:
            dataIncomplete = True
            break

    if not dataIncomplete:
        for vname in varlist:
            if   vname == "Temp":
                Temp            = g.rm_temp
                Temp            = applyValueFormula(vname, Temp, g.ValueScale[vname])
                g.rm_temp  = None
                alldata.update({"Temp": Temp})

            elif vname == "Press":
                Press           = g.rm_press
                Press           = applyValueFormula(vname, Press, g.ValueScale[vname])
                g.rm_press = None
                alldata.update({"Press": Press})

            elif vname == "Humid":
                Hum             = g.rm_hum
                Hum             = applyValueFormula(vname, Hum, g.ValueScale[vname])
                g.rm_hum   = None
                alldata.update({"Humid": Hum})

            elif vname == "Xtra":
                Rssi            = g.rm_rssi
                Rssi            = applyValueFormula(vname, Rssi, g.ValueScale[vname])
                g.rm_rssi  = None
                alldata.update({"Xtra": Rssi})

            elif vname in ("CPM", "CPM1st", "CPM2nd", "CPM3rd"):
                cpm             = g.rm_cpm
                cpm             = applyValueFormula(vname, cpm, g.ValueScale[vname])
                g.rm_cpm   = None
                alldata.update({vname: cpm})

    vprintLoggedValues(defname, varlist, alldata, (time.time() - start) * 1000)

    return alldata


def initRadMon():
    """Initialize the client and set all Callbacks"""

    global RMconnectDuration

    defname = "initRadMon: "
    errmsg  = ""

    dprint(defname + "Initializing RadMon Device")
    setIndent(1)

    g.Devices["RadMon"][g.DNAME] = "RadMon+"

    # set configuration
    if g.RMServerIP     == "auto": g.RMServerIP     = "test.mosquitto.org" # before: "mqtt.eclipse.org"
    if g.RMServerPort   == "auto": g.RMServerPort   = 1883
    if g.RMServerFolder == "auto": g.RMServerFolder = "/"
    if g.RMTimeout      == "auto": g.RMTimeout      = 5

# set client
    # Client(client_id="", clean_session=True, userdata=None, protocol=MQTTv311)
    # protocol: Can be either MQTTv31 or MQTTv311
    # on Ubuntu 12.04.5 LTS  with kernel 2.6.32-042stab134.8 the
    # protocol MQTTv311 is NOT working: (does not make a connect)
    # g.rm_client = mqtt.Client(cname, True, None, mqtt.MQTTv311)
    # it is working when protocol MQTTv31 is used
    g.rm_client = mqtt.Client(client_id="", clean_session=True, userdata=None, protocol=mqtt.MQTTv31)

    # set callbacks
    g.rm_client.on_connect       = on_connect
    g.rm_client.on_subscribe     = on_subscribe
    g.rm_client.on_message       = on_message
    g.rm_client.on_publish       = on_publish
    g.rm_client.on_disconnect    = on_disconnect

    # connect
    dprint(defname + "connect to: RMServerIP: '{}', RMServerPort: {}".format(g.RMServerIP, g.RMServerPort))
    try:
        g.rm_client.connect(g.RMServerIP, port=g.RMServerPort, keepalive=60)
    except Exception as e:
        srcinfo = defname + "ERROR: Connection to IoT server failed"
        exceptPrint(e, srcinfo)
        g.rm_client     = None
        errmsg += "\nERROR: Connection failed using: server IP='{}', port={}".format(g.RMServerIP, g.RMServerPort)
        errmsg += "\nERROR: '{}'".format(sys.exc_info()[1])
        errmsg += "\n{} not connected. Is server offline? Verify server IP and server port".format(g.Devices["RadMon"][g.DNAME])

        setIndent(0)
        return errmsg

    #
    # start looping
    #
    ##  # keep as reminder - alternative looping
    ##  g.rm_client.loop_read()
    ##  for i in range(0,6):
    ##      g.rm_client.loop(timeout=.1)
    #g.rm_client.loop_forever()      # indeed forever, it hangs the system
    #                                     # CTRL-C will disconnect the g.rm_client
    #g.rm_client.loop(timeout=10.0)  # returns control after timeout

    g.rm_client.loop_start()         # threaded loop; must be stopped on exit!
    dprint(defname + "Threaded loop was started")

    # wait for confirmation of connection
    starttime = time.time()
    timeout   = True
    while time.time() < (starttime  + g.RMTimeout):
        #print("g.RMconnect:", time.time() - starttime, g.RMconnect)
        time.sleep(0.05)
        # if g.RMConnection:
        if RMconnectionState:
            timeout = False
            RMconnectDuration = "{:0.2f} sec".format(time.time() - starttime)
            dprint(defname + "Connected after: {}".format(RMconnectDuration))
            break

    if timeout:
        # no callback signalling a connection
        dprint(defname + "RadMon connection timed out ({} sec)".format(g.RMTimeout), debug=True)
        errmsg += "\nERROR: Connection to RadMon+ server failed; RadMon+ inactivated"
        RMconnectDuration = "Failure, timeout after {} sec".format(g.RMTimeout)
    else:
        # set only after successful AND confirmed connect!
        if g.RMVariables    == "auto":    g.RMVariables   = "CPM3rd, Temp, Press, Humid"

        g.RMVariables = setLoggableVariables("RadMon", g.RMVariables)

    g.Devices["RadMon"][g.CONN] = RMconnectionState

    setIndent(0)
    return errmsg


def terminateRadMon():
    """opposit of init ;-)"""

    if g.rm_client is None: return

    defname = "terminateRadMon: "

    dprint(defname)
    setIndent(1)

    g.rm_client.loop_stop()
    dprint(defname + "client.loop was stopped")

    g.rm_client.disconnect()    # output printed in callback
    dprint(defname + "client was disconnected")

    g.rm_client = None
    dprint(defname + "client was set to: None")

    # wait for confirmation of dis-connection
    starttime = time.time()
    timeout   = True
    while time.time() < (starttime  + g.RMTimeout):
        #print("g.RMdisconnect:", time.time() - starttime, g.RMdisconnect)
        time.sleep(0.05)
        if not RMconnectionState:
            #print("g.RMdisconnect:", time.time() - starttime, g.RMdisconnect)
            timeout = False
            break

    if timeout:
        dprint("RadMon dis-connection timed out ({} sec)".format(g.RMTimeout), debug=True)
        efprint("ERROR: Dis-Connection from RadMon+ server failed; RadMon+ inactivated")
        retval = ""
    else:
        retval = "RadMon+"

    g.Devices["RadMon"][g.CONN] = RMconnectionState

    dprint(defname + "Terminated")
    setIndent(0)



def getInfoRadMon(extended=False):
    """Info on the Radmon Device"""

    RMInfo = "Configured Connection:        MQTT on {}:{} topic:'{}'\n".\
        format(g.RMServerIP, g.RMServerPort, g.RMServerFolder)

    if not g.Devices["RadMon"][g.CONN]: return RMInfo + "<red>Device is not connected</red>"

    RMInfo += "Connected Device:             {}\n".format(g.Devices["RadMon"][g.DNAME])
    RMInfo += "Configured Variables:         {}\n".format(g.RMVariables)
    RMInfo += getTubeSensitivities(g.RMVariables)

    if extended == True:

        if g.rm_rssi    is None:   rssi = "Not available"
        else:                           rssi = str(g.rm_rssi)

        RMInfo += """
Connecting Duration:          {}
Folder:                       '{}'
Internal collection time:     60 s
Total cycle time (typical):   67 ... 70 s
Wireless signal strength:     {} (rssi)""".format(\
                                                  RMconnectDuration,     \
                                                  g.RMServerFolder, \
                                                  rssi)

    return RMInfo

