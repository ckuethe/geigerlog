#! /usr/bin/env bash
# script: PipCheck.sh

# Clear Screen
clear

echo
echo "######################  GeigerLog  Pip-Check  ###################"
echo
echo "Checking for Virtual Environment"

if [ -f __venvGL1_5_0/bin/activate ];then
    echo "    Virtual Environment does already exist as '__venvGL1_5_0'"
    echo
else
    echo "    Virtual Environment does NOT exist - now creating it as: '__venvGL1_5_0'"

    # allow the use of system-site-packages (needed at least for Raspi)
    python3 -m venv --system-site-packages __venvGL1_5_0
    echo "    Done"
    echo
fi

# start GeigerLog; install modules if needed
__venvGL1_5_0/bin/python3 gtools/GLpipcheck.py $1
echo


