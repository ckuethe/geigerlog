#! /usr/bin/env bash
# script: GeigerLog.sh
# desktop-file-validate /home/ullix/Desktop/gtest.desktop

# Clear Screen
clear

echo "############################################  GeigerLog  Startup  #############################################"

### Working Dir
echo "Checking for Working Directory"
printf '    %s' "Current Directory: "
pwd

if [ -f geigerlog.py ];then
    echo "    Found file 'geigerlog.py'; taking this as GeigerLog working directory!"
else
    echo
    echo "    This is NOT your working directory for GeigerLog!"
    echo "    Please change into the GeigerLog working directory, and then start GeigerLog again."
    echo
    exit 1
fi


# Virtual Environment
myvenv='__venvGL1_5_0'
echo "Checking for Virtual Environment"

### Checking for command 'setup'
if  [ "$#" -gt "0" ];then
    if [ $1 == "setup" ];then
        echo "    GeigerLog Auto-Setup"
        if [ -f __venvGL1_5_0/bin/activate ];then
            echo "        A Virtual Environment does exist as '$myvenv'."
        else
            echo "        A Virtual Environment does NOT exist - now creating it as: '$myvenv'."

            # allow the use of system-site-packages (needed at least for Raspi)
            python3 -m venv --system-site-packages $myvenv
            echo "        Done"
        fi
    fi
fi



# if venv exists start GeigerLog; install modules if needed
# if command 'setup' had been given, it is still active!
if [ -f $myvenv/bin/activate ];then
    echo "    Using Virtual Environment '$myvenv'"
    $myvenv/bin/python3 geigerlog.py $1 $2 $3 $4 $5 $6 $7 $8 $9
else
    echo "    A Virtual Environment does NOT exist - Please, start GeigerLog with './GeigerLog.sh setup'"
fi

echo
