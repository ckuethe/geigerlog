#!/usr/bin/python3
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
see header of ambiomon for installing and communicating with MQTT server

Installing MQTT on Ubuntu:
see: https://www.digitalocean.com/community/tutorials/how-to-install-and-secure-the-mosquitto-mqtt-messaging-broker-on-ubuntu-16-04
site includes steps to set up secure server!

To install the software:
    sudo apt-get install mosquitto mosquitto-clients

Testing MQTT, assuming mosqitto running on mysite.com:
Subscribe in terminal 1:
    mosquitto_sub -v -h mysite.com -t ambiomon/#
Publish in terminal 2:
    mosquitto_pub -h mysite.com -t ambiomon/temp -m "hello world"
You should see in terminal 1:
    ambiomon/temp hello world
"""


__author__          = "ullix"
__copyright__       = "Copyright 2016, 2017, 2018, 2019, 2020"
__credits__         = [""]
__license__         = "GPL3"

from   gutils       import *


###############################################################################
# BEGIN MQTT Callbacks
###############################################################################

def on_connect(client, userdata, flags, rc):
    """The callback for when the client receives a CONNACK response from the server"""

    # The value of rc indicates success or not:
    strrc = {
            0: "Connection successful",
            1: "Connection refused - incorrect protocol version",
            2: "Connection refused - invalid gglobs.rm_client identifier",
            3: "Connection refused - server unavailable",
            4: "Connection refused - bad username or password",
            5: "Connection refused - not authorised",
            # 6-255: Currently unused.
            }

    if rc < 6:     src = strrc[rc]
    else:          src = "Unexpected Connection Response"
    gglobs.RMconnect = (rc, src)

    if rc == 0:
        gglobs.RMConnection = True
    else:
        gglobs.RMConnection = False

    dprint(">RadMon: on_connect: Client connected:")
    dprint(">        {:20s}: {}".format("with userdata"     , userdata))
    dprint(">        {:20s}: {}".format("with flags"        , flags))
    dprint(">        {:20s}: {}".format("with result"       , src), " (Result Code: {})".format(rc))

    # Subscribing within 'on_connect()' means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    #gglobs.rm_client.subscribe("$SYS/#") # gives huge amount of traffic! Careful!!!
    gglobs.rm_client.subscribe(gglobs.RMServerFolder + "#", qos=2)


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
    gglobs.RMdisconnect = (rc, src)

    gglobs.RMConnection = False         # it is disconnected in any case

    dprint(">RadMon: on_disconnect: Client disconnected:")
    dprint(">        {:20s}: {}".format("with userdata"     , userdata))
    dprint(">        {:20s}: {}".format("with result"       , src), "(Result Code: {})".format(rc))


def on_subscribe(client, userdata, mid, granted_qos):
    """Callback when a subscribe has occured"""

    dprint(">RadMon: on_subscribe: Topic subscribed:")
    dprint(">        {:20s}: {}".format("with userdata"     , userdata))
    dprint(">        {:20s}: {}".format("with mid"          , mid))
    dprint(">        {:20s}: {}".format("with granted_qos"  , granted_qos))


def on_message(client, userdata, msg):
    """The callback for when a PUBLISH message is received from the server"""

    # message: an instance of MQTTMessage.
    # This is a class with members topic, payload, qos, retain.
    vprint(">RadMon: on_message: topic: {:20s}, payload: {:10s}, qos: {}, retain: {}".format(msg.topic, str(msg.payload), msg.qos, msg.retain))
    #print("type of msg.payload:", type(msg.payload))

    if   msg.topic == gglobs.RMServerFolder + "temp":     gglobs.rm_temp   = float(msg.payload)    # T
    elif msg.topic == gglobs.RMServerFolder + "pressure": gglobs.rm_press  = float(msg.payload)    # P
    elif msg.topic == gglobs.RMServerFolder + "humid":    gglobs.rm_hum    = float(msg.payload)    # H
    elif msg.topic == gglobs.RMServerFolder + "cpm":      gglobs.rm_cpm    = float(msg.payload)    # CPM*
    elif msg.topic == gglobs.RMServerFolder + "rssi":     gglobs.rm_rssi   = float(msg.payload)    # rssi
    #else:                                                print("msg.payload:", msg.payload)       # any


def on_publish(client, userdata, mid):
    """ Called when a message that was to be sent using the publish() call
    has completed transmission to the broker.  """

    #dprint("on_publish: messageID: mid: ", mid)
    pass


###############################################################################
# END MQTT Callbacks
###############################################################################

def getRadMonValues(varlist):
    """Read all RadMon data; return only when complete"""

    #vprint("getRadMonValues({})".format(varname))
    #setDebugIndent(1)

    alldata = {}

    if not gglobs.RMConnection: # RadMon is NOT connected!
        dprint("getRadMonValues: RadMon is NOT connected")
        return alldata

    if varlist == None:
        return alldata

    dataIncomplete = False
    for vname in varlist:
        if   vname == "T" and gglobs.rm_temp  == None :
            dataIncomplete = True
            break
        elif vname == "P" and gglobs.rm_press == None :
            dataIncomplete = True
            break
        elif vname == "H" and gglobs.rm_hum   == None :
            dataIncomplete = True
            break
        elif vname in ("CPM", "CPM1st", "CPM2nd", "CPM3rd") and gglobs.rm_cpm == None:
            dataIncomplete = True
            break

    if not dataIncomplete:
        for vname in varlist:
            if   vname == "T":
                Temp            = gglobs.rm_temp
                Temp            = scaleVarValues(vname, Temp, gglobs.ValueScale[vname])
                gglobs.rm_temp  = None
                alldata.update({"T": Temp})

            elif vname == "P":
                Press           = gglobs.rm_press
                Press           = scaleVarValues(vname, Press, gglobs.ValueScale[vname])
                gglobs.rm_press = None
                alldata.update({"P": Press})

            elif vname == "H":
                Hum             = gglobs.rm_hum
                Hum             = scaleVarValues(vname, Hum, gglobs.ValueScale[vname])
                gglobs.rm_hum   = None
                alldata.update({"H": Hum})

            elif vname in ("CPM", "CPM1st", "CPM2nd", "CPM3rd"):
                cpm             = gglobs.rm_cpm
                cpm             = scaleVarValues(vname, cpm, gglobs.ValueScale[vname])
                gglobs.rm_cpm   = None
                alldata.update({vname: cpm})

    vprint("{:20s}:  Variables:{}  Data:{}  Folder:'{}'".format("getRadMonValues", varlist, alldata, gglobs.RMServerFolder))
    #setDebugIndent(0)

    return alldata


def getRadMonInfo(extended=False):
    """Info on the Radmon Device"""

    if gglobs.rm_client  == None:       return "No connected device"

    if gglobs.rm_rssi == None:       rssi = "Not available"
    else:                            rssi = str(gglobs.rm_rssi)

    RMInfo = """Connected Device:             '{}'
Configured Variables:         {}
Geiger tube calib. factor:    {:0.1f} CPM/(µSv/h) ({:0.4f} µSv/h/CPM)
""".format(\
                                                  gglobs.RMDeviceDetected, \
                                                  gglobs.RMVariables, \
                                                  #~ gglobs.RMCalibration )
                                                  gglobs.RMCalibration, 1 / gglobs.RMCalibration)

    if extended == True:
        RMInfo += """
Connection:                   wireless, MQTT server {}, port:{}
Folder:                       '{}'
Internal collection time:     60 s
Total cycle time (typical):   67 ... 70 s
Wireless signal strength:     {} (rssi)""".format(\
                                                  gglobs.RMServerIP, \
                                                  gglobs.RMServerPort, \
                                                  gglobs.RMServerFolder, \
                                                  rssi)

    return RMInfo


def terminateRadMon():
    """opposit of init ;-)"""

    if gglobs.rm_client == None: return

    dprint("terminateRadMon: Terminating RadMon")
    setDebugIndent(1)

    gglobs.rm_client.loop_stop()
    dprint("terminateRadMon: client.loop was stopped")

    gglobs.rm_client.disconnect()    # output printed in callback
    dprint("terminateRadMon: client was disconnected")

    #print("terminateRadMon: gglobs.rm_client", gglobs.rm_client)
    gglobs.rm_client = None
    dprint("terminateRadMon: client was set to: None")

    # wait for confirmation of dis-connection
    starttime = time.time()
    timeout   = True
    while time.time() < (starttime  + gglobs.RMTimeout):
        #print("gglobs.RMdisconnect:", time.time() - starttime, gglobs.RMdisconnect)
        time.sleep(0.05)
        if not gglobs.RMConnection:
            #print("gglobs.RMdisconnect:", time.time() - starttime, gglobs.RMdisconnect)
            timeout = False
            break

    if timeout:
        dprint("RadMon dis-connection timed out ({} sec)".format(gglobs.RMTimeout), debug=True)
        fprint("<br>ERROR: Dis-Connection from RadMon+ server failed; RadMon+ inactivated", error=True)
        setDebugIndent(0)
        retval = ""
    else:
        retval = "RadMon+"

    setDebugIndent(0)


def initRadMon():
    """Initialize the client and set all Callbacks"""

    fncname = "initRadMon: "
    errmsg  = ""

    if not gglobs.RMActivation:
        dprint(fncname + "RadMon device not activated")
        return errmsg

    dprint(fncname + "Initialzing RadMon")
    setDebugIndent(1)

    gglobs.RMDeviceName = "RadMon+"
    gglobs.RMDeviceDetected  = gglobs.RMDeviceName # no difference so far

    # set configuration
    if gglobs.RMServerIP     == "auto":      gglobs.RMServerIP     = "mqtt.eclipse.org"
    if gglobs.RMServerPort   == "auto":      gglobs.RMServerPort   = 1883
    if gglobs.RMServerFolder == "auto":      gglobs.RMServerFolder = "/"
    if gglobs.RMTimeout      == "auto":      gglobs.RMTimeout      = 3

# set client
    # Client(client_id="", clean_session=True, userdata=None, protocol=MQTTv311)
    # protocol: Can be either MQTTv31 or MQTTv311
    # on Ubuntu 12.04.5 LTS  with kernel 2.6.32-042stab134.8 the
    # protocol MQTTv311 is NOT working: (does not make a connect)
    # gglobs.rm_client = mqtt.Client(cname, True, None, mqtt.MQTTv311)
    # it is working when protocol MQTTv31 is used
    gglobs.rm_client = mqtt.Client(client_id="", clean_session=True, userdata=None, protocol=mqtt.MQTTv31)

    # set callbacks
    gglobs.rm_client.on_connect       = on_connect
    gglobs.rm_client.on_subscribe     = on_subscribe
    gglobs.rm_client.on_message       = on_message
    gglobs.rm_client.on_publish       = on_publish
    gglobs.rm_client.on_disconnect    = on_disconnect

    # connect
    dprint(fncname + "connect to: RMServerIP: '{}', RMServerPort: {}".format(gglobs.RMServerIP, gglobs.RMServerPort))
    try:
        gglobs.rm_client.connect(gglobs.RMServerIP, port=gglobs.RMServerPort, keepalive=60)
    except Exception as e:
        srcinfo = fncname + "ERROR: Connection to IoT server failed"
        exceptPrint(e, sys.exc_info(), srcinfo)
        gglobs.rm_client     = None
        errmsg += "<br>ERROR: Connection failed using server IP='{}', port={}".format(gglobs.RMServerIP, gglobs.RMServerPort)
        errmsg += "<br>ERROR: '{}'".format(sys.exc_info()[1])
        errmsg += "<br>{} not connected. Is server offline? Verify server IP and server port".format(gglobs.RMDeviceName)

        setDebugIndent(0)
        return errmsg

    #
    # start looping
    #
    ##  # keep as reminder - alternative looping
    ##  gglobs.rm_client.loop_read()
    ##  for i in range(0,6):
    ##      gglobs.rm_client.loop(timeout=.1)
    #gglobs.rm_client.loop_forever()      # indeed forever, it hangs the system
    #                                     # CTRL-C will disconnect the gglobs.rm_client
    #gglobs.rm_client.loop(timeout=10.0)  # returns control after timeout

    gglobs.rm_client.loop_start()         # threaded loop; must be stopped on exit!
    dprint(fncname + "Threaded loop was started")

    # wait for confirmation of connection
    starttime = time.time()
    timeout   = True
    while time.time() < (starttime  + gglobs.RMTimeout):
        #print("gglobs.RMconnect:", time.time() - starttime, gglobs.RMconnect)
        time.sleep(0.05)
        if gglobs.RMConnection:
            #print("gglobs.RMconnect:", time.time() - starttime, gglobs.RMconnect)
            timeout = False
            break

    if timeout:
        # no callback signalling a connection
        dprint(fncname + "RadMon connection timed out ({} sec)".format(gglobs.RMTimeout), debug=True)
        errmsg += "<br>ERROR: Connection to RadMon+ server failed; RadMon+ inactivated"
    else:
        # set only after successful AND confirmed connect!
        if gglobs.RMCalibration  == "auto":    gglobs.RMCalibration  = 154  # inverse of 0.0065
        defaultRMVariables = "T, P, H, CPM3rd"
        if gglobs.RMVariables    == "auto":    gglobs.RMVariables    = defaultRMVariables

        if gglobs.RMVariables.count("CPM") > 1:
            efprint("ALERT: Improper definition of RadMon variables: ", gglobs.RMVariables)
            qefprint("ALERT: Correct in configuration file!")
            gglobs.RMVariables    = defaultRMVariables
            qefprint("ALERT: RadMon variables are reset to: ", gglobs.RMVariables)

        # set the loggable variables
        DevVars = gglobs.RMVariables.split(",")
        for i in range(0, len(DevVars)):  DevVars[i] = DevVars[i].strip()
        gglobs.DevicesVars["RadMon"] = DevVars
        #print("DevicesVars:", gglobs.DevicesVars)

    setDebugIndent(0)
    return errmsg
