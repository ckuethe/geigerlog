#! /usr/bin/env python3
# -*- coding: utf-8 -*-

"""
GLgpxToCSV.py - Converting GPS data in gpx format to GeigerLog CSV format

        start program with:  GLgpxToCSV.py mygpsfile.gpx
        program stops after creating CSV file 'mygpsfile.gpx.csv'
        in this format:

        # datetime,           latitude,   longitude,  elevation
        2013-06-19 13:09:32, 52.858636,    5.699969,  -3.375
        2013-06-19 13:13:26, 52.858666,    5.699985,   5.432

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

import sys

try:
    import gpxpy                    # Version 1.6.2
    import gpxpy.gpx
except Exception as e:
    print("Exception: ", e)
    print("The python module 'gpxpy' must be installed.")
    print("Install with pip:  pip install gpxpy")
    print("see: https://pypi.org/project/gpxpy/")
    print()
    sys.exit(1)


# Convering an existing *.gpx file: (try file: demo.gpx)
# ... gives this output in a CSV file:
#   # datetime,           latitude,   longitude,  elevation
#   2013-06-19 13:09:32, 52.858636,    5.699969,  -3.375
#   2013-06-19 13:13:26, 52.858666,    5.699985,   5.432


# get gpx filename from command line,
# like: 'GLgpxToCSV.py demo.gpx'
if len(sys.argv) == 1: gpx_file_name   = 'demo.gpx'                 # no file name on command line
else:                  gpx_file_name   = (sys.argv[1]).strip()

gpx_file        = open(gpx_file_name, 'r')
gpx             = gpxpy.parse(gpx_file)

# create this CSV file
csv_file_name   = gpx_file_name + ".csv"
csv_file        = open(csv_file_name, "w")

header          = f'# {"datetime"},           {"latitude"},   {"longitude"},  {"elevation"}'
print(header)
csv_file.write(header + "\n")
for track in gpx.tracks:
    for segment in track.segments:
        for point in segment.points:
            datetime = str(point.time)[0:19]
            record   = f'{datetime}, {point.latitude:9.6f},  {point.longitude:10.6f},  {point.elevation:6.3f}'
            print(record)
            csv_file.write(record + "\n")

#
# Unused options:
#
# print("========================gpx.waypoints: ", gpx.waypoints)
# for waypoint in gpx.waypoints:
#     print(f'waypoint {waypoint.name} -> ({waypoint.latitude},{waypoint.longitude})')

# print("------------------------gpx.routes: ", gpx.routes)
# for route in gpx.routes:
#     print('Route:')
#     for point in route.points:
#         print(f'Point at ({point.latitude},{point.longitude}) -> {point.elevtion}')

