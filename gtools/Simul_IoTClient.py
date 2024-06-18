#! /usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Simul_IoTClient.py - Demo MQTT Client to feed GeigerLog
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
__version__         = "1.0"
__version__         = "1.0.0pre03"

import sys, os, time                            # basic modules
import datetime                 as dt           # datetime
import numpy                    as np           # for Poisson data
import paho.mqtt.client         as mqtt         # for the IoT stuff
import json                                     # for DATA

# colors
TDEFAULT            = '\033[0m'                 # default, i.e greyish
TRED                = '\033[91m'                # red
BRED                = '\033[91;1m'              # bold red
TGREEN              = '\033[92m'                # light green
BGREEN              = '\033[92;1m'              # bold green
TYELLOW             = '\033[93m'                # yellow

# globals class
# Things to configure:
#   withAuthorization       (True or False)     RadMon needs False!
#   sendOnCommand           (cycle or SEND)     RadMon needs cycle!
#
class DemoIoTVars:
    """A class with the only task to make certain variables global"""

########################################################################################################################
# Options need to be configured
    # Authorization Option
    if 10: withAuthorization = True                         # select MQTT access with or without authorization
    else:  withAuthorization = False                        # select MQTT access with or without authorization

    # Data sending options:
    if  0:    sendOnCommand = True                          # True:  wait for a SEND command (coming from GeigerLog)
    else:     sendOnCommand = False                         # False: send data every 'cycle' seconds, ignore all SEND command

    # using RadMon options:
    if 10:    usingRadMon   = True                          # use code to simulate RadMon
    else:     usingRadMon   = False                         # no RadMon; support modern IoT
########################################################################################################################

    # set configuration
    IoTBrokerIP             = "test.mosquitto.org"          # for alternative see file 'geigerlog.cfg'
    IoTBrokerFolder         = "geigerlog/cmnd/GLdevice"     # expected by GeigerLog - this DEMO supports ONLY GeigerLog
    IoTTimeout              = 5                             # 3 sec is often NOT enough

    # special settings for classic RadMon Device
    if usingRadMon:
        withAuthorization   = False
        sendOnCommand       = False
        IoTBrokerFolder     = "geigerlog/"


    if not withAuthorization:
        # this configures the code for access to the broker WITHOUT authorization
        IoTBrokerPort       = 1883                          # 1884 with authorization; 1883 without
        IoTUsername         = ""                            # empty
        IoTPassword         = ""                            # empty

    else:
        # this configures the code for access to the broker WITH authorization
        IoTBrokerPort       = 1884                          # 1884 with authorization; 1883 without
        IoTUsername         = "rw"                          # with autorization, fixed when using 'test.mosquitto.org'
        IoTPassword         = "readwrite"                   # with autorization, fixed when using 'test.mosquitto.org'

    iot_connected           = False                         # flag to signal connection
    iot_on_publishID        = None                          # to hold the publöish ID to verify successful sending
    iot_topic               = None                          # to hold the topic

    CollectedData           = b""                           # like:  b'1733.0, 36.0, 1884.7, 30.2, 34.0, 34.2, 34.0, 0.0, 34.0, 32.3, 32.0, 2.0'
    sendDataFlag            = False                         # if True then sending data is due

    # constants
    NAN                     = float("NAN")                  # Not A Number, here: Missing value
    logfile                 = "_Simul_IoTClient.log"        # output from this program; file is deleted when starting


# instantiate globals
g = DemoIoTVars


###############################################################################
# BEGIN UTILS
###############################################################################

def stime():
    """Return current time as YYYY-MM-DD HH:MM:SS.fff with ms resolution"""

    return dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]


def dprint(*args):
    """print timestamp followed by args"""

    tag = ""
    for arg in args: tag += str(arg)

    if tag > "": tag = "{:20s} {}".format(stime(), tag)

    print(tag[11:])

    # remove any color code from the tag to be written to file
    # \x1B = ESC, followed by codes like:  ['\x1B[0m', '\x1B[96m', ...
    if "\x1B" in tag:
        codes = ['[0m', '[96m', '[93m', '[92;1m', "[92;1m30", "[92m", "[91;1m41", "[91;1m30", "[91m", "[91;1m", ]
        for c in codes:     tag = tag.replace("\x1B" + c, "")

    # append to logfile
    with open(g.logfile, "at") as f:   f.write(tag + " \n")


def rdprint(*args):
    dprint(TRED, *args, TDEFAULT)


def gdprint(*args):
    dprint(TGREEN, *args, TDEFAULT)


def edprint(*args):
    dprint(BRED, *args, TDEFAULT)


def exceptPrint(e, srcinfo):
    """Print exception details (errmessage, file, line no)"""

    exc_type, exc_obj, exc_tb = sys.exc_info()
    fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]    # which file?

    dprint(TYELLOW + stime() + " EXCEPTION: '{}' in file: '{}' in line {}".format(e, fname, exc_tb.tb_lineno), TDEFAULT)
    if srcinfo > "": dprint(stime() + " " + srcinfo)


def clearTerminal():
    """clear the terminal"""

    # The name of the operating system dependent module imported. The following
    # names have currently been registered: 'posix', 'nt', 'java'. (on Linux: posix)

    # if "LINUX" in platform.platform().upper():
    #     # clear the terminal
    #     os.system("export TERM=xterm-256color")     # needed to prep for clear (week, seems to work without it???)
    #     os.system("clear")                          # clear terminal

    os.system('cls' if os.name == 'nt' else 'clear')
    # print("os.name: ", os.name) # os.name:  posix (on Linux)


###############################################################################
# END UTILS
###############################################################################



###############################################################################
# BEGIN MQTT Callbacks
###############################################################################

# in all Callbacks
# Client:       is python object
# userdata:     as defined in Client call and modified in on_message
# msg:          the message coming from the IoT device
# flags:        a dict that contains response flags from the broker
# rc:           indicates the connecion / disconnection state
# mid:          the message ID
# granted_qos:  a list of integers that give the QoS level the broker has granted for each of the different subscription requests
#
# if publishing is more frequent than reading, only the last published data will be read


def on_connectMQTT(client, userdata, flags, rc):
    """The callback for when the client receives a CONNACK response from the Broker"""

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

    dprint(">IoT: " + defname + "connection attempt ended with: '{}'".format(strrc[rc]))
    g.iot_connected = True if rc == 0 else False

    # Subscribing
    # doing it within 'on_connect()' means that if we lose the connection and reconnect, the subscriptions will be renewed.
    g.iot_topic = g.IoTBrokerFolder + "/#"
    # g.iot_client.subscribe(g.iot_topic, qos=2)
    g.iot_client.subscribe(g.iot_topic, qos=1)


def on_disconnectMQTT (client, userdata, rc):
    """When the client has sent the disconnect message an on_disconnectMQTT() callback is generated"""

    # The rc parameter indicates the disconnection state.
    # If rc == MQTT_ERR_SUCCESS (0), the callback was called in response to a disconnect() call.
    # If any(!) other value the disconnection was unexpected, such as caused by a network error.
    # !!! -> rc can have ANY value 0 ... 255 !!!

    defname = "on_disconnectMQTT: "

    strrc = {
                0: "MQTT_ERR_SUCCESS",
                1: "Unexpected disconnection",
                # 1 - 255: "Unexpected disconnection"
            }

    g.iot_connected = False

    dprint(">IoT: " + defname + "disconnection attempt ended with: '{}'".format(strrc[0 if rc == 0 else 1]))


def on_subscribeMQTT(client, userdata, mid, granted_qos):
    """Callback when a subscribe has occured"""

    defname = "on_subscribe: "

    dprint(">IoT: on_subscribe: Topic subscribed: '{}'".format(g.iot_topic))
    dprint(">        {:20s}: {}".format("got userdata"     , userdata))
    dprint(">        {:20s}: {}".format("got mid"          , mid))
    dprint(">        {:20s}: {}".format("got granted_qos"  , granted_qos))


def on_publishMQTT(client, userdata, mid):
    """Callback called when a message that was sent using the publish() call has completed transmission to the broker"""

    # see: https://github.com/eclipse/paho.mqtt.python/issues/514
    # see: https://pypi.org/project/paho-mqtt/
    # topic: on_publish()
    #        cmd:  on_publish(client, userdata, mid)
    #
    # Called when a message that was to be sent using the publish() call has completed transmission to the
    # broker.
    # For messages with QoS levels 1 and 2, this means that the appropriate handshakes have completed.
    # For QoS 0, this simply means that the message has left the client. The mid variable matches the mid
    # variable returned from the corresponding publish() call, to allow outgoing messages to be tracked.
    # This callback is important because even if the publish() call returns success, it does not always mean
    # that the message has been sent. (!!!)
    #
    # duration of publish from start to confirmation is 15 ... ms, avg: 70ms

    defname = "on_publishMQTT: "

    # rdprint(defname, "mid: ", mid)
    g.iot_on_publishID = mid


def on_messageMQTT(client, userdata, msg):
    """The callback for when a PUBLISH message is received from the server"""

    defname = "on_message: "

    client.user_data_set(userdata + 1)

    if "geigerlog/cmnd/GLdevice" in msg.topic:
        # dprint(">IoT " + defname + "topic:   '{}'  qos:{}  retain:{}  userdata:{}".format(msg.topic, msg.qos, msg.retain, userdata))
        # dprint(">IoT " + defname + "payload: {}"                                  .format(msg.payload))
        if b'SEND' in msg.payload:
            g.sendDataFlag = True


def on_logMQTT(client, userdata, level, buf):
    rdprint("log: ",buf)


###############################################################################
# END MQTT Callbacks
###############################################################################


def init():
    """Initialize the client and set all Callbacks"""

    defname = "init: "

    # clear the screen
    clearTerminal()

    # header
    print(BGREEN + "*" * 150 + TDEFAULT)
    dprint(defname)

    # clean logfile
    with open(g.logfile, "wt") as f: f.write(stime() + " " + __file__ + "  version: " + __version__ + " \n")

    # set client
    # see: https://pypi.org/project/paho-mqtt/
    # protocol - the version of the MQTT protocol to use for this client. Can be either MQTTv31, MQTTv311 or MQTTv5
    #            3.1 and 3.11 can use same code
    #            5.0          requires DIFFERENT code!
    # userdata   can be anything
    #
    g.iot_client = mqtt.Client(client_id="", clean_session=True, userdata=None, protocol=mqtt.MQTTv311)
    g.iot_client.user_data_set(0)    # change userdata

    # set callbacks
    g.iot_client.on_connect       = on_connectMQTT
    g.iot_client.on_publish       = on_publishMQTT
    g.iot_client.on_disconnect    = on_disconnectMQTT
    g.iot_client.on_subscribe     = on_subscribeMQTT
    g.iot_client.on_message       = on_messageMQTT
    # g.iot_client.on_log           = on_logMQTT                   # set client logging

    # connect
    dprint(defname, "Connecting to:'{}'  Port:{}".format(g.IoTBrokerIP, g.IoTBrokerPort))

    # subscription is done inside 'on_connect'
    starttime = time.time()
    try:
        # a username > "" as signal for authorized access
        if g.IoTUsername > "": g.iot_client.username_pw_set(username=g.IoTUsername, password=g.IoTPassword)

        # "The keep alive processing can be turned off by setting the interval to 0 on connect."
        g.iot_client.connect(g.IoTBrokerIP, port=g.IoTBrokerPort, keepalive=60)

    except Exception as e:
        exceptPrint(e, defname + "ERROR: Connection to IoT Broker failed")
        g.iot_client = None
        errmsg  = ""
        errmsg += "\nERROR: Connection failed using: Broker IP='{}', port={}".format(g.IoTBrokerIP, g.IoTBrokerPort)
        errmsg += "\nERROR: '{}'".format(sys.exc_info()[1])
        errmsg += "\nIoT Device not connected. Is Broker offline? Verify Broker IP and Broker port"
        edprint(defname, errmsg)

    # must start loop to get 'on_connectMQTT' callback
    # it becomes a threaded loop; must be stopped on exit!
    dprint(defname + "Starting MQTT Client loop")
    g.iot_client.loop_start()

    # wait for confirmation of connection, but wait no longer than g.IoTTimeout sec
    timeout  = True
    stoptime = starttime  + g.IoTTimeout
    while time.time() < stoptime:
        if g.iot_connected:
            timeout = False
            dprint(defname + "Connection established; took: {:0.2f} sec".format((time.time() - starttime)))
            break
        time.sleep(0.05)

    if timeout:
        # got no callback signalling a connection, thus connection failed
        dprint(defname + "IoT connection timed out ({} sec)".format(g.IoTTimeout))


def terminateMQTT():
    """terminate MQTT; incl threads"""

    if g.iot_client is None: return

    defname = "terminateMQTT: "

    dprint(defname)

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
        if not g.iot_connected:
            timeout = False
            break
        time.sleep(0.05)

    if timeout:
        dprint("MQTT dis-connection timed out ({} sec)".format(g.IoTTimeout))
        dprint("ERROR: Dis-Connection from MQTT failed; MQTT inactivated nevertheless")

    dprint("Terminated MQTT client")


def publishMQTT(data):
    """publish data to MQTT"""

    defname = "publishMQTT: "

    g.iot_on_publishID = None                                                   # to reset any old ID; is updated by on_publish
    success, publishID = g.iot_client.publish(g.IoTBrokerFolder, data, qos=1)   # success==0 indicates success
    # rdprint(defname, "success:{}, publishID::{}  data:{}".format(success, publishID, data))

    if success == 0:
        # verify that publish succeeded by comparing publishID with on_publishID (received in callback)
        pstart  = time.time()

        timeout = True
        confirm = False
        while time.time() < (pstart  + g.IoTTimeout):
            if g.iot_on_publishID is not None:
                if g.iot_on_publishID == publishID: confirm = True          # the IDs are the same
                else:                               confirm = False         # the IDs are DIFFERENT
                timeout = False                                             # no timeout
                break                                                       # done
            time.sleep(0.005)                                               # 5 ms sleep

        dur = 1000 * (time.time() - pstart)

        cmdText = "SEND" if g.sendOnCommand else "CYCL"
        pmsg    = "CMD:{} topic:'{}' P:{} Payld:{:60s} {} @pID:{:4s} dur:{:3.0f} ms"
        sdata   = str(data).replace(" ", "").replace('"', "")                           # remove blanks and quote marks
        if not timeout: dprint(pmsg.format(cmdText, g.IoTBrokerFolder, g.IoTBrokerPort, sdata, "SUCCESS" if confirm else "FAILURE", str(publishID), dur))
        else:           dprint(pmsg.format(cmdText, g.IoTBrokerFolder, g.IoTBrokerPort, sdata, "TIMEOUT",                           "None",         dur))
    else:
        rdprint(defname, "Publishing failed - data: ", data)


def collectData():
    """prepare the data in the form needed by GeigerLog, i.e. 12 value items in json dict

    return:     data as json dict, like: b'{"DATA": {"CPM": 0, "CPS": 0, "CPM1st": 2, "CPS1st": 4, "CPM2nd": 7, "CPS2nd": 4,
                                            "CPM3rd": 7, "CPS3rd": 20, "Temp": 28, "Press": 94, "Humid": 298, "Xtra": 1026}}'
    total dur:  0.1 ms
    """

    defname  = "collectData: "

    # GeigerLog's 12 vars
    GLVarNames = ['CPM', 'CPS', 'CPM1st', 'CPS1st', 'CPM2nd', 'CPS2nd', 'CPM3rd', 'CPS3rd', 'Temp', 'Press', 'Humid', 'Xtra']

    # the Poisson means
    means      = (0.1, 0.3, 1, 3, 10, 30, 100, 300, 1000, 3000, 10000, 30000)

    values = {}
    for i, vname in enumerate(GLVarNames):
        values[vname] = np.random.poisson(means[i])

    sjson = json.dumps({"DATA" : values})
    rdprint(sjson)

    return sjson



    # Does NOT work with RadMon
    #
    # if not g.usingRadMon:
    #     values = {}
    #     for i, vname in enumerate(GLVarNames):
    #         values[vname] = np.random.poisson(means[i])
    #     sjson = json.dumps({"DATA" : values})
    #     rdprint(sjson)
    #     return sjson
    # else:
    #     values = {}
    #     for i, vname in enumerate(GLVarNames):
    #         values[vname] = np.random.poisson(means[i])
    #     # sjson = json.dumps({"DATA" : values})
    #     sjson = json.dumps(values)
    #     gdprint(sjson)
    #     return sjson


    # start = time.time()
    # N     = 1000000
    # sqrn  = np.sqrt(N)

    # for i in range(N):
    #     y = np.random.poisson(10)
    # stop1 = time.time()

    # for i in range(N):
    #     y = np.random.poisson(10000)
    # stop2 = time.time()

    # for i in range(N):
    #     y = np.random.poisson(means[i % 15])
    # stop3 = time.time()

    # for i in range(N):
    #     y = np.random.normal(10, sqrn)
    # stop4 = time.time()

    # for i in range(N):
    #     y = np.random.normal(10000, sqrn)
    # stop5 = time.time()

    # rdprint(defname, "Poisson 10:    {:0.3f} µs".format(1e6 / N * (stop1 -start)))
    # rdprint(defname, "Poisson 10000: {:0.3f} µs".format(1e6 / N * (stop2 -stop1)))
    # rdprint(defname, "Poisson means: {:0.3f} µs".format(1e6 / N * (stop3 -stop2)))

    # rdprint(defname, "Normal 10:     {:0.3f} µs".format(1e6 / N * (stop4 -stop3)))
    # rdprint(defname, "Normal 10000:  {:0.3f} µs".format(1e6 / N * (stop5 -stop4)))


###################################################################################################
if __name__ == '__main__':
    defname = "main: "
    try:
        init()
        if g.sendOnCommand:  # configure in the header
            gdprint(defname, "Waiting for 1st SEND command from GeigerLog\n\n")
            while True:
                if g.sendDataFlag:
                    g.sendDataFlag = False
                    publishMQTT(collectData())
                time.sleep(0.01)                    # 10 ms sleep

        else:
            rdprint(defname, "running on CYCLE\n\n")
            cycle     = 1.0                         # sec - even 0.03 does work!
            nextcycle = time.time() + cycle
            while True:
                if time.time() >= nextcycle:
                    nextcycle += cycle
                    if not g.usingRadMon:
                        publishMQTT(collectData())
                    else:
                        ret= g.iot_client.publish("geigerlog/temp",     np.random.normal(37, 0.5))
                        ret= g.iot_client.publish("geigerlog/pressure", np.random.normal(1000, 3))
                        ret= g.iot_client.publish("geigerlog/humid",    np.random.normal(50, 1.5))
                        ret= g.iot_client.publish("geigerlog/cpm",      np.random.poisson(300))
                        print("ret cpm: ", ret)

                time.sleep(0.01) # 10 ms sleep

    except KeyboardInterrupt:
        print()
        print("Exit by CTRL-C")
        terminateMQTT()
        print()
        os._exit(0)

