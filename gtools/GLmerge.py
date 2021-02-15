#! /usr/bin/env python3
# -*- coding: utf-8 -*-

"""
GLmerge.py - To merge 2 CSV files into 1
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
__copyright__       = "Copyright 2016, 2017, 2018, 2019, 2020, 2021"
__credits__         = [""]
__license__         = "GPL3"

"""
fileone.csv:
#Date (GMT+1:00),CPM,ACPM,uSv/h,Latitude,Longitude
2021-01-12 16:07:54,282,129.13,0.81,41.792933,12.61027559
2021-01-12 16:06:52,334,129.10,0.95,41.792933,12.61027559
2021-01-12 16:05:50,306,129.07,0.87,41.792933,12.61027559
2021-01-12 16:04:48,283,129.03,0.81,41.792933,12.61027559
2021-01-12 16:03:46,357,129.00,1.02,41.792933,12.61027559

filetwo.csv:
# LOGGING,                    , 2018-05-29 11:36:06.485, Start:  cycle: 60.0 sec, mode: 'CPM'
# LOGGING,                    , 2018-05-29 11:36:06.485, Connected Device: 'GMC-300Re 4.22'
# LOGGING,                    , 2018-05-29 12:11:18.672, Stop
#  HEADER, 2018-05-29 11:35:46, Logfile newly created as 'radmon-vergleich-medium.log'
        1, 2018-05-29 11:36:06,   117.0
        2, 2018-05-29 11:37:06,   132.0
        3, 2018-05-29 11:38:06,   120.0
        4, 2018-05-29 11:39:06,   131.0
        5, 2018-05-29 11:40:06,   121.0
        6, 2018-05-29 11:41:06,   120.0
"""


def main():
    """combine 2 CSV files into 1, sort the records acc to DateTime, and put
    records with same datetime into single record.
    CPM is any type of data; could be CPM, CPS or anything. And not necessarily
    the same type in both files, like CPM in 1st file, and Temp in 2nd file
    Resulting file has 4 columns DateTime, one_cpm, two_cpm, origin (file 1, 2, 1+2)

    DateTime : is required. Must be present in both files. I will become the first column
    CPM      : anything
    filenames: onfile and twofile
    one_cpm  : column number in first  file (starting with 0 for 1st column)
    two_cpm  : column number in second file (starting with 0 for 1st column)

    """

    #~onefile   = "./data/fileone.csv"
    #~one_date    = 0
    #~one_cpm     = 1

    #~twofile   = "./data/filetwo.csv"
    #~two_date    = 1
    #~two_cpm     = 2


    onefile     = "./data/20210125-csv.csv"
    one_date    = 0
    one_cpm     = 3

    twofile     = "./data/20210125-bin.hisdb.csv"
    two_date    = 1
    two_cpm     = 2

    mergefile   = "./data/filemerge.csv"


    print("\n------------------------ GLmerge.py ----------------------------")
    print()

# Load File One
    print("Load File One --------------------------------------------------------")
    mergelist1  = []
    with open(onefile, "r") as handle:
        for line in handle:
            #print(line, end='')
            rec = line.strip().split(",")
            try:
                dt  = rec[one_date].strip()
                cpm = rec[one_cpm].strip()
            except: continue
            if dt == '' or cpm == '' or dt[0] == "#" or "Stamp" in cpm: continue
            dt  = (dt + ":00")[0:19]            # add the seconds if not present
            mergelist1.append([dt, cpm, "nan", "1"])
            #print("one", mergelist1[-1])
    mergelist1 = sorted(mergelist1)

    last = mergelist1[0]
    for i in range(1, len(mergelist1)):
        new = mergelist1[i]
        #print("i: {} new  {}".format(i, new))
        if last[0] == new[0]:
            print("i: {:6d} duplicate: last {}".format(i, last))
            print("i: {:6d}            new  {}".format(i, new))
        last = new

    writeFile(mergefile + ".one", mergelist1)

    #sys.exit()

# Load File Two
    print("Load File Two --------------------------------------------------------")
    mergelist2  = []
    with open(twofile, "r") as handle:
        for line in handle:
            #print(line, end='')
            rec = line.strip().split(",")
            try:
                dt  = rec[two_date].strip()
                cpm = rec[two_cpm].strip()
            except: continue
            if dt == '' or cpm == '' or dt[0] == "#" or "Stamp" in cpm: continue
            dt  = (dt + ":00")[0:19]            # add the seconds if not present
            mergelist2.append([dt, "nan", cpm, "2"])

    mergelist2 = sorted(mergelist2)

    last = mergelist2[0]
    for i in range(1, len(mergelist2)):
        new = mergelist2[i]
        if last[0] == new[0]:
            print("i: {:6d} duplicate: last {}".format(i, last))
            print("i: {:6d}            new  {}".format(i, new))
        last = new

    writeFile(mergefile + ".two", mergelist2)

# Mix both
    print("Mix Both  --------------------------------------------------------")
    mergelist = sorted(mergelist1 + mergelist2)

    last = mergelist[0]
    for i in range(1, len(mergelist)):
        new = mergelist[i]
        if last[0] == new[0]:
            print("i: {} duplicate: last {}".format(i, last))
            print("i: {}            new  {}".format(i, new))
        last = new

    writeFile(mergefile + ".mix", mergelist)

    #sys.exit()

# Put duplicate dates into single rec
    newmergelist = []
    last = mergelist[0]
    for i in range(1, len(mergelist)):
        new = mergelist[i]
        if last[0] == new[0]:
            print(i)
            print("i: {}, last    : {}".format(i-1, last))
            print("i: {}, new     : {}".format(i, new))
            if new[1]  == 'nan': nonan = new[2]
            else:                nonan = new[1]
            if last[1] == 'nan': last[1] = nonan
            else:                last[2] = nonan

            last[3] = "1+2"
            print("i: {}, last    : {}".format(i, last))
            print("i: {}, ml[i-1] : {}".format(i-1, mergelist[i -1]))
            print("i: {}, ml[i]   : {}".format(i, mergelist[i]))
        else:
            newmergelist.append(last)
            last = new

    print("check Mix for duplicates ------------------------------------------")
    last = newmergelist[0]
    for i in range(1, len(newmergelist)):
        new = newmergelist[i]
        if last[0] == new[0]:
            print("i: {} duplicate: last {}".format(i, last))
            print("i: {}            new  {}".format(i, new))
        last = new

# Write final file
    print("Write to final file ----------------------------------------------")
    writeFile(mergefile, newmergelist)



def writeFile(filename, flist):
    counter = 0
    cmax    = len(flist)
    limit   = 10

    with open(filename, "wt") as handle:
        for a in flist:
            wstr = "{:20s}, {:>5s}, {:>5s}, {:>5s}\n".format(a[0], a[1], a[2], a[3])
            handle.write(wstr)

            if counter < limit or counter > (cmax - limit) or (counter % int(0.37 * (cmax / limit)) == 0):
                print("{:6d}".format(counter), wstr, end="")
            if counter == limit or counter == cmax - limit: print()
            counter += 1


if __name__ == '__main__':
    main()
