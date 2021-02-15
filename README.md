# README.md:

<!--:~$ grip README.md -->

#### NOTE: All **articles** are relocated into the FOLDER named 'Articles'
---

## GeigerLog 1.1 has been released!

Some major internal refactoring - hopefully not noticable by any user ;-) - to
prepare for the future,

New features were added:

> GeigerLog now supports HiDPI monitors, it is now running well on an 8k monitor

<!--![GLMM](/Monitor8k.png "GeigerLog on an 8k monitor")
![GLMM](/MiniMon-GL.png "GeigerLog running integrated MiniMon device")-->

> GeigerLog now supports the MiniMon CO2 Monitors for CO2 measurements in your
room or office (only on Linux). A standalone version of MiniMon is found
elsewhere on my site:
https://sourceforge.net/projects/minimon/

> An improvement for users of a GMC counter: GeigerLog has now got a dialogue to
edit the counter's internal configuration memory, allowing to enter SSIDs, WiFi
passwords, websites, IDs from the computer keyboard.

---

### Bug Reports for GeigerLog 1.0:

A little bug had surfaced in GeigerLog 1.0.
However, it impacts only users of the AudioCounter device under certain
conditions. Others may update GeigerLog; no harm will be done.

To update, download file **amc-bug.zip** from the **testing** folder and unzip.
It contains only the two files *geigerlog* and *gutils.py*. Replace your
existing files with them.

---

## GeigerLog 1.0 has been released!

GeigerLog has finally left the beta-stage. Little is new, except for the definition
of the Calibration Factor - it is now
the invers of the previous definitions. Read in the manual why this was done.

And a HOWTO for the installation and use of GeigerLog on the Raspberry Pi
has been added.

---

## What files to find on this site?

### GeigerLog-Program
- latest release of full GUI version
- simple Non-GUI programs available as well

### GeigerLog-Manual
- the manual to GeigerLog
  (specific for each version)


### Articles on the use and physics of Geiger counter and radioactivity:

- GeigerLog-Potty Training for Your Geiger Counter
  (using household items with Potassium to measure radioactivity)

- GeigerLog-Going Banana
  (measure the Potassium in bananas with a Geiger counter;
   Data provided)

- Review of Semiconductor Geiger Counter Smart Geiger Pro (SGP-001)
  (new technology for the broader public)

- Support for Audio Counters in GeigerLog
  (old technology audio-clicks counter now supported in GeigerLog

- GeigerLog-Radiation-v1.1(CAJOE)-Support
  (using the low-cost CAJOE Geiger counter)


### HOWTOs
- HOWTO - Read-Write permission in Linux for the serial port

- HOWTO - Using Python in a virtual Environment on Linux
  (very helpful when you use more than one Python version!)

- HOWTO - Using PyQt5 and matplotlib on HiDPI monitors (Python3)


### Data
- from the banana experiment
- from international flights
- synthetic data


### Supporting documents
- like spec sheets of tubes, documents on Geiger-Müller tubes, etc.

