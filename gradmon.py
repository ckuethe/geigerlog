#!/usr/bin/python3
# -*- coding: UTF-8 -*-

"""
RadMonPlus support
"""

import sys, time
import traceback                            # for traceback on error
import paho.mqtt.client as mqtt             # https://pypi.org/project/paho-mqtt/

import gglobs
from   gutils   import *


###############################################################################
# BEGIN MQTT Callbacks
###############################################################################

def on_connect(client, userdata, flags, rc):
    """The callback for when the client receives a CONNACK response from the server"""

    # The value of rc indicates success or not:
    strrc = {
            0: "Connection successful",
            1: "Connection refused - incorrect protocol version",
            2: "Connection refused - invalid gglobs.client identifier",
            3: "Connection refused - server unavailable",
            4: "Connection refused - bad username or password",
            5: "Connection refused - not authorised",
            # 6-255: Currently unused.
            }

    if rc < 6:     src = strrc[rc]
    else:          src = "Unexpected Connection Response"

    gglobs.RMconnect = (rc, src)

    dprint(gglobs.debug, "on_connect: Client connected:")
    dprint(gglobs.debug, "                 {:33s}: {}".format("with userdata"     , userdata))
    dprint(gglobs.debug, "                 {:33s}: {}".format("with flags"        , flags))
    dprint(gglobs.debug, "                 {:33s}: {}".format("with result"       , src), " (Result Code: {})".format(rc))

    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    #gglobs.client.subscribe("$SYS/#")
    gglobs.client.subscribe(gglobs.RMserverFolder + "#", qos=2)


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

    dprint(gglobs.debug, "on_disconnect: Client disconnected:")
    dprint(gglobs.debug, "                    {:33s}: {}".format("with userdata"     , userdata))
    dprint(gglobs.debug, "                    {:33s}: {}".format("with result"       , src), "(Result Code: {})".format(rc))


def on_subscribe(client, userdata, mid, granted_qos):
    """Callback when a subscribe has occured"""

    dprint(gglobs.debug, "on_subscribe: Topic subscribed:")
    dprint(gglobs.debug, "                 {:33s}: {}".format("with userdata"     , userdata))
    dprint(gglobs.debug, "                 {:33s}: {}".format("with mid"          , mid))
    dprint(gglobs.debug, "                 {:33s}: {}".format("with granted_qos"  , granted_qos))


def on_message(client, userdata, msg):
    """The callback for when a PUBLISH message is received from the server"""
    # message: an instance of MQTTMessage.
    # This is a class with members topic, payload, qos, retain.

    vprint(gglobs.verbose, "on_message: topic: {:15s}, payload: {:10s}, qos: {}, retain: {}".format(msg.topic, str(msg.payload), msg.qos, msg.retain))

    if   msg.topic == gglobs.RMserverFolder + "temp":     gglobs.rm_temp   = float(msg.payload)    # T
    elif msg.topic == gglobs.RMserverFolder + "pressure": gglobs.rm_press  = float(msg.payload)    # P
    elif msg.topic == gglobs.RMserverFolder + "humid":    gglobs.rm_hum    = float(msg.payload)    # H
    elif msg.topic == gglobs.RMserverFolder + "cpm":      gglobs.rm_cpm    = float(msg.payload)    # R
    elif msg.topic == gglobs.RMserverFolder + "rssi":     gglobs.rm_rssi   = float(msg.payload)    #
    #else:                                                 print("msg.payload:", msg.payload) # any


def on_publish(client, userdata, mid):
    """ Called when a message that was to be sent using the publish() call
    has completed transmission to the broker.  """

    dprint(gglobs.debug, "on_publish: messageID: mid: ", mid)


###############################################################################
# END MQTT Callbacks
###############################################################################


def getRadMonData(varname):
    """Read the RadMon data and return"""

    ### keep as reminder - alternative looping
    #gglobs.client.loop_read()
    #for i in range(0,6):
    #    gglobs.client.loop(timeout=.1)

    #vprint(gglobs.verbose, "getRadMonData({})".format(varname))
    #debugIndent(1)

    nulldata = (gglobs.NAN, 0, "")


    if gglobs.client == None: # RadMon is NOT active!
        data = nulldata
        dprint(gglobs.debug, "getRadMonData: NO RadMon CLIENT")

    elif varname == "R":
        if gglobs.rm_cpm   != None:
            R               = gglobs.rm_cpm
            R               = scaleValues("R", R, gglobs.ScaleR)
            gglobs.rm_cpm   = None
            data = (R, 0, "")
        else:
            data = nulldata

    elif varname == "T":
        if gglobs.rm_temp  != None:
            Temp            = gglobs.rm_temp
            Temp            = scaleValues("T", Temp, gglobs.ScaleT)
            gglobs.rm_temp  = None
            data = (Temp, 0, "")
        else:
            data = nulldata

    elif varname == "P":
        if gglobs.rm_press != None:
            Press           = gglobs.rm_press
            Press           = scaleValues("P", Press, gglobs.ScaleP)
            gglobs.rm_press = None
            data = (Press, 0, "")
        else:
            data = nulldata

    elif varname == "H":
        if gglobs.rm_hum   != None:
            Hum             = gglobs.rm_hum
            Hum             = scaleValues("H", Hum, gglobs.ScaleH)
            gglobs.rm_hum   = None
            data = (Hum, 0, "")
        else:
            data = nulldata

    vprint(gglobs.verbose, "getRadMonData({}{}): {}".format(gglobs.RMserverFolder, varname, data))
    #debugIndent(0)

    return data


def getRadMonInfo():
    """Info on the Radmon Device"""

    if gglobs.client  == None:       return "No connected device"

    if gglobs.rm_rssi == None:       rssi = "Not available"
    else:                            rssi = str(gglobs.rm_rssi)

    RMInfo = """Connected Device:                  {}
Connection:                        wireless, MQTT server {}, port:{}
Folder                             '{}'
Variables configured:              {}
Geiger tube calibration factor:    {} µSv/h/CPM
Internal count collection time:    60 s
Total cycle time (typical):        67 ... 70 s
Wireless signal strength (rssi):   {}""".format(gglobs.RMdevice, gglobs.RMserverIP, gglobs.RMserverPort, gglobs.RMserverFolder, gglobs.RMvariables, gglobs.RMcalibration, rssi)

    return RMInfo


def terminateRadMon():
    """opposit of init ;-)"""

    if gglobs.client == None: return

    dprint(gglobs.debug, "terminateRadMon: Terminating RadMon")
    debugIndent(1)

    gglobs.client.loop_stop()
    dprint(gglobs.debug, "terminateRadMon: client.loop was stopped")

    gglobs.client.disconnect()    # output printed in callback
    dprint(gglobs.debug, "terminateRadMon: client was disconnected")

    #print("terminateRadMon: gglobs.client", gglobs.client)
    gglobs.client = None
    dprint(gglobs.debug, "terminateRadMon: client was set to: None")

    # wait for confirmation of dis-connection
    starttime = time.time()
    timeout   = True
    while time.time() < (starttime  + gglobs.RMtimeout):
        #print("gglobs.RMdisconnect:", time.time() - starttime, gglobs.RMdisconnect)
        time.sleep(0.05)
        if gglobs.RMdisconnect[0] != -99:
            #print("gglobs.RMdisconnect:", time.time() - starttime, gglobs.RMdisconnect)
            timeout = False
            break

    if timeout:
        dprint(True, "RadMon dis-connection timed out ({} sec)".format(gglobs.RMtimeout))
        fprint("<br>ERROR: Dis-Connection from RadMon+ server failed; RadMon+ inactivated", error=True)
        debugIndent(0)
        retval = ""
    else:
        retval = "RadMon+"

    debugIndent(0)

    return retval


def initRadMon():
    """Initialize the client and set all Callbacks"""

    #print("initRadMon: gglobs.RMserverIP:", gglobs.RMserverIP)
    if gglobs.RMserverIP == None:
        dprint(gglobs.debug, "initRadMon: RadMon device not configured")
        return "RadMon device not configured"

    dprint(gglobs.debug, "initRadMon: Initialzing RadMon")
    debugIndent(1)

    # set client and callbacks
    gglobs.client                  = mqtt.Client()
    gglobs.client.on_connect       = on_connect
    gglobs.client.on_subscribe     = on_subscribe
    gglobs.client.on_message       = on_message
    gglobs.client.on_publish       = on_publish
    gglobs.client.on_disconnect    = on_disconnect

    # connect
    dprint(gglobs.debug, "initRadMon: connect to: RMserverIP: '{}', RMserverPort: {}".format(gglobs.RMserverIP, gglobs.RMserverPort))
    try:
        gglobs.client.connect(gglobs.RMserverIP, port=gglobs.RMserverPort, keepalive=60)
    except Exception as e:
        srcinfo = "initRadMon: ERROR: Connection to server failed"
        exceptPrint(e, sys.exc_info(), srcinfo)
        dprint(True, "initRadMon: ERROR: Connection to server failed")
        #dprint(True, traceback.format_exc()) # more extensive info
        #gglobs.RMserverIP = None
        gglobs.client     = None
        fprint("ERROR: Connection failed using server='{}', port={}".format(gglobs.RMserverIP, gglobs.RMserverPort), error=True)
        fprint("ERROR: Message: '{}'".format(sys.exc_info()[1]), error=True, errsound=False)
        fprint("")
        fprint("RadMon+ not activated. Verify server IP and server port", error=True, errsound=False)

        debugIndent(0)
        return ""

    # start looping
    #dprint(gglobs.debug, "initRadMon:", "starting loop")
    #gglobs.client.loop_forever()      # indeed forever, it hangs the system
                                       # CTRL-C will disconnect the gglobs.client
    #gglobs.client.loop(timeout=10.0)  # returns control after timeout
    gglobs.client.loop_start()         # threaded loop; must be stopped on exit!
    dprint(gglobs.debug, "initRadMon: Loop was started")

    if gglobs.RMvariables    == "auto":      gglobs.RMvariables    = "T, P, H, R"
    if gglobs.RMcalibration  == "auto":      gglobs.RMcalibration  = 0.0065
    if gglobs.RMserverFolder == "auto":      gglobs.RMserverFolder = "/"

    # wait for confirmation of connection
    starttime = time.time()
    timeout   = True
    while time.time() < (starttime  + gglobs.RMtimeout):
        #print("gglobs.RMconnect:", time.time() - starttime, gglobs.RMconnect)
        time.sleep(0.05)
        if gglobs.RMconnect[0] != -99:
            #print("gglobs.RMconnect:", time.time() - starttime, gglobs.RMconnect)
            timeout = False
            break

    if timeout:
        dprint(True, "RadMon connection timed out ({} sec)".format(gglobs.RMtimeout))
        fprint("<br>ERROR: Connection to RadMon+ server failed; RadMon+ inactivated", error=True)
        retval = ""
    else:
        retval = "RadMon+"

    debugIndent(0)

    return retval # on success return "RadMon+", else ""
