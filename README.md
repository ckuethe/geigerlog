# README.md:
<!--
localhost:
~$ grip README.md
include pics:
![GLMM](/Monitor8k.png "GeigerLog on an 8k monitor")
![GLMM](/MiniMon-GL.png "GeigerLog running integrated MiniMon device")
-->

#### NOTE: All **articles** are relocated into the FOLDER named 'Articles'
---

## GeigerLog 1.2.1 has been released!

> GeigerLog now supports all current Gamma-Scout Counters, including the lat­est “Online” model, the only one of the breed which allows logging.

> A SimulCounter has been added, which creates its “counts” with a Poisson random number generator. Helpful for understanding the workings of a Geiger counter and GeigerLog.

> Search the entire NotePad for the occurrence of a text like ‘abc’ or ‘123.456’

> The tool GLpipcheck was improved

> The Easter Holidays are approaching, and fittingly, an Easter egg can now be found in GeigerLog. Do your best – perhaps you will see a dancing GEIGERA?

---

## BUG - Alert

you may experience a Python bug on all operating systems if you have updated to
the latest versions of the Python packages. The error message is "ImportError:
Failed to import any qt binding" and GeigerLog won't start at all.

For a workaround run these commands in a terminal/command window :

- python -m pip uninstall  PyQt5 PyQt5-Qt PyQt5-sip
- python -m pip install  PyQt5
- python -m pip install --force-reinstall  PyQt5-Qt

Remember that depending on your installation you may have to use 'python3'
instead of plain 'python' !

At the end you will have these versions installed:
<br>   PyQt5            5.15.3
<br>   PyQt5-Qt         5.15.2
<br>   PyQt5-sip        12.8.1

---


## GeigerLog 1.2 has been released!

and withdrawn due to a nasty Windows 10 bug

---


## GeigerLog 1.1 has been released!

Some major internal refactoring - hopefully not noticable by any user ;-) - to
prepare for the future,

New features were added:

> GeigerLog now supports HiDPI monitors, it is now running well on an 8k monitor

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

