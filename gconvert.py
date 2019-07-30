#! /usr/bin/python3
# -*- coding: utf-8 -*-

"""
gconvert.py - A program to convert log files from one CSV format to a different one

use to convert CSV log files from other sources to work with GeigerLog
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
__copyright__       = "Copyright 2016, 2017, 2018"
__credits__         = [""]
__license__         = "GPL3"
__version__         = "0.1"


import sys, os
import getopt                   # parse command line for options and commands

helpOptions = """
Usage:  gconvert.py [Options]
Options:
    -h, --help          Show this help and exit
    -v, --verbose       Be more verbose; print out OLD and NEW records
                        Default is verbose = False
    -f, --from          Name with path of file to read
    -t, --to            Name with path of file to write
    -c, --columns       Column indexes to write in that order; see NOTE

NOTE:
GeigerLog (v0.9.08) needs the data columns as CSV (Comma Separated Values)
strictly(!) in this order:
0      1         2    3    4       5       6       7       8            9         10        11
index, DateTime, CPM, CPS, CPM1st, CPM2nd, CPS1st, CPS2nd, Temperature, Pressure, Humidity, R


whereby:
index       : used for internal purposes (may have any value)
DateTime    : is in a format like: 2018-05-26 13:14:53 (GeigerLog may handle other formats)
CPM:        : the regular CPM readout of the counter
CPS:        : the regular CPS readout of the counter
CPM1st      : CPM data from the first tube
CPM2nd      : CPM data from the second tube
CPS1st      : CPS data from the first tube
CPS2nd      : CPS data from the second tube
T           : Temperature from a RadMon+ with sensor BME280
P           : Pressure    from a RadMon+ with sensor BME280
H           : Humidity    from a RadMon+ with sensor BME280
R           : CPM         from a RadMon+ with Geiger Tube

Any missing column can be created and filled with "missing value" by using 'd'
for dummy column.

Examples:

To convert from a log file created with 'geigerlog_simple_500plus.py' version 0.1,
which has these columns (the index column is missing):
0         1    2    3       4
DateTime, CPS, CPM, CPM1st, CPM2nd
use:  gconvert.py -f <path/to/simplefile> -t <path/to/newfile> -c "d,0,2,1,3,4,d,d,d,d,d,d"


To convert from a log file created with 'geigerlog_simple_500plus.py' version 0.2,
which has these columns (T, P, H, R missing):
0      1         2    3    4       5       6       7
Index, DateTime, CPM, CPS, CPM1st, CPM2nd, CPS1st, CPS2nd
use:  gconvert.py -f <path/to/simplefile> -t <path/to/newfile> -c "0,1,2,3,4,5,6,7,d,d,d,d"


To convert from a RadMon+ file, which has these columns:
0      1         2     3        4       5       6
index, DateTime, CPM,  T[°C],   H[%],   P[hPa], rssi
use:  gconvert.py -f <path/to/RMfile> -t <path/to/newfile> -c "0,1,d,d,d,d,d,d,3,5,4,2"

"""


verbose  = False
fromfile = ""
tofile   = ""
columns  = ""

#
# parse command line options
# sys.argv[0] is progname
try:
    opts, args = getopt.getopt(sys.argv[1:], "hvf:t:c:", ["help", "verbose", "from", "to", "columns" ])
except getopt.GetoptError as errmessage :
    # print info like "option -a not recognized", then continue
    dprint(True, "ERROR: '{}', use './convert -h' for help".format(errmessage) )
    sys.exit()

# processing the options
for opt, optval in opts:
    if opt in ("-h", "--help"):
        print (helpOptions)
        sys.exit()

    elif opt in ("-v", "--verbose"):
        verbose = True

    elif opt in ("-f", "--from"):
        fromfile = optval

    elif opt in ("-t", "--to"):
        tofile = optval

    elif opt in ("-c", "--columns"):
        columns = optval


if fromfile == "" or tofile == "" or columns == "":
    print("\7ERROR: insufficient options! Use 'convert -h' for help")
    sys.exit()

print("FROM file:", fromfile)
print("TO   file:", tofile)
print("Columns  :", columns)
cols = columns.split(",")
#print("cols:   ", cols)

with open(fromfile, 'r') as f:
    fromdata = f.readlines()
    for i in range(0, len(fromdata)):
        fromdata[i] = fromdata[i][:-1]  # remove linefeed '\n' from each line


with open(tofile, 'w') as t:
    for a in fromdata:
        if verbose: print('OLD: "{}"'.format(a), end="")
        if len(a.strip()) == 0: continue
        if a.strip()[0] == "#":
            t.write(a + "\n")

        else:
            data = a.split(",")
            newdata = ""
            for b in cols:
                if b.upper() == "D":
                    #newdata += "nan, "
                    newdata += ", "
                else:
                    newdata += data[int(b)] + ", "

            newdata = newdata[:-2] + "\n"       # last characters are ' \n'
            t.write(newdata)
            if verbose: print('         NEW: "{}"'.format(newdata[:-1]))

