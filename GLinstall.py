#! /usr/bin/python3
# -*- coding: utf-8 -*-

"""
glinstall.py - GeigerLog installer
start as administrator

"""

"""
Using pip as an imported module:  (not recommended, see at bottom of:
https://pip.pypa.io/en/stable/user_guide/

... if you decide that you do want to run pip from within your program. The most
... reliable approach, and the one that is fully supported, is to run pip in a
... subprocess. This is easily done using the standard subprocess module


from pip._internal import main as pipmain

def install(package):
    # test for presence of 'main' (older versions) or use pip._internal.main()
    if hasattr(pip, 'main'):
        pip.main(['install', package])
    else:
        pip._internal.main(['install', package])

pipmain(["list"])
<package name> = e.g. pip, pyserial, ...
pipmain(["show", <package name>])
pipmain(["install","--upgrade", <package name>])
"""

"""
to execute, no output
subprocess.check_call([sys.executable, '-m', 'pip', 'list'])
"""

import sys, subprocess


def pipShow(package):
    reqs = subprocess.check_output([sys.executable, '-m', 'pip', 'show', package])
    print(reqs.decode('UTF-8'))    # convert from bytes to str
    print()


def pipGetVersionFromShow(package):
    reqs = subprocess.check_output([sys.executable, '-m', 'pip', 'show', package])

    indx = reqs.find(b"Version:")
    if  indx != -1:
        ver = (reqs[indx + 8: reqs.find(b"\n", indx + 8)]).decode('UTF-8').strip()
        print("Version of {:12s} is: {}".format(package, ver))
    else:
        print("Version of {:12s} is: {}".format(package, "not defined"))


def pipInstall(package):
    try:
        res = subprocess.check_output([sys.executable, '-m', 'pip', 'install', '--upgrade', package])
        res = res.decode('UTF-8').strip()
    except Exception as e:
        res = e

    return res


def pipList():
    res = subprocess.check_output([sys.executable, '-m', 'pip', 'list'])
    return res.decode('UTF-8').strip()


def pipGetVersionFromList():
    reqs = subprocess.check_output([sys.executable, '-m', 'pip', 'list'])
    #print ("reqs:", reqs)

    nreqs = reqs.decode('UTF-8').strip().split("\n")
    #print ("nreqs:", nreqs)

    for nr in nreqs:
        p = nr[0:29].strip()
        v = nr[29:].strip()
        #print(">",p,"<",">",v,"<")

        if p in installs:
            print("         installed:  {:28s} {:20s}".format(p,v))
        else:
            pass
            #print("installed but not needed: {:28s} {:20s}".format(p,v))


def pipGetVersionFromOutdatedList():
    reqs = subprocess.check_output([sys.executable, '-m', 'pip', 'list', '--outdated'])
    #print ("reqs:", reqs)

    nreqs = reqs.decode('UTF-8').strip().split("\n")
    # e.g.:  'bottle             0.12.7   0.12.17  wheel',
    #print ("nreqs:", nreqs)

    print("Versions with available Upgrade:")
    counter = 0
    for nr in nreqs:
        #nrl = nr.strip().split(" ")
        #print("nrl: ", nrl)

        p = nr[0:18].strip()
        v = nr[18:27].strip()
        w = nr[26:35].strip()
       # print(">",p,"<",">",v,"<",">",w,"<")

        if p in installs:
            print("         installed:  {:28s} {:20s} {:20s}".format(p, v, w))
            counter += 1
        else:
            pass
            #print("installed but not needed: {:28s} {:20s}".format(p,v))
    if counter == 0: print("None available")


###############################################################################


print("++++++++++++++++++++++ sys.executable:", sys.executable)
print("++++++++++++++++++++++ Python version:", sys.version.replace('\n', ""))

# optional for pip:   pip install "SomeProject>=1,<2"

installs = {
            "pip"           : ("latest"     , "pypi"),
            "setuptools"    : ("latest"     , "pypi"),
            "matplotlib"    : ("==3.0.3"    , "pypi"),
            "numpy"         : (">=1.14"     , "pypi"),
            "scipy"         : ("latest"     , "pypi"),
            "pyserial"      : ("latest"     , "pypi"),
            "paho-mqtt"     : ("latest"     , "pypi"),
            "PyQt5"         : ("latest"     , "pypi"),
            "PyQt5-sip"     : ("latest"     , "pypi"),
            "pyqt5"         : ("latest"     , "pypi"),
            "pyqt5-sip"     : ("latest"     , "pypi"),
            }

line = "#######################################################################"
line2 = "----------------------------------------------------------------------"

pipGetVersionFromList()
pipGetVersionFromOutdatedList()

sys.exit()


print(line)
for pkg,vs in installs.items():

    v = vs[0]
    s = vs[1]  # source

    print("\nPackage: {}, Version: {} \t".format(pkg,v))

    if s == "pypi":
        if v == "latest":   pkg = pkg
        else:               pkg = pkg + v
        output = pipInstall(pkg)
        print(output)
    else:
        try:
            res = subprocess.check_output([sys.executable, '-m', 'pip', 'install', s])
            res = res.decode('UTF-8').strip()
        except Exception as e:
            print("Exception e:", e)
            res = e
        print(res)


pipGetVersionFromList()
