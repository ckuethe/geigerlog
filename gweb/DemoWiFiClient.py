#! /usr/bin/env python3
# -*- coding: UTF-8 -*-

"""
DemoWiFiClient.py - a utility which acts like a WiFiClient device
                    by calling GeigerLog's built-in web server with
                    a GET message carrying the data

Start with:     DemoWiFiClient.py
Stop with:      CTRL-C
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


import sys, os, io, time, datetime  # basic modules
import urllib.request               # calling a web server

#############################################
# adapt to your situation
serverIP   = "10.0.0.20"    # IP of computer running GeigerLog
serverPort = "8000"         # Port where GeigerLog will be listening
#############################################

def main():

    baseurl = "http://{}:{}".format(serverIP, serverPort)

    # Get the ID of GL's server
    try:
        idurl       = baseurl + "/id"
        page        = urllib.request.urlopen(idurl, timeout=3)
        answer      = page.read()
        print("idurl: ", idurl, "    answer: ", answer)
    except Exception as e:
        print(e)

    # upload the data via GET call
    dataurl = baseurl + "/GENERIC"
    numbers = range(10, 23)
    callurl = dataurl + "?M={}&S={}&M1={}&S1={}&M2={}&S2={}&M3={}&S3={}&T={}&P={}&H={}&X={}".format(*numbers)
    while True:
        try:
            page        = urllib.request.urlopen(callurl, timeout=3)
            answer      = page.read()
            print("callurl: ", callurl, "    answer[:50]: ", answer.strip()[:50])
        except Exception as e:
            print("Exception: ", e, callurl)
            time.sleep(2)

        time.sleep(1)


if __name__ == '__main__':
    main()

