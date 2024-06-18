@echo OFF
REM script: PipCheck.bat

@REM Clear Screen
cls

echo.
echo ######################  GeigerLog  Pip-Check  ###################
echo.
echo. Checking for Virtual Environment

if exist __venvGL1_5_0\Scripts\activate (
    echo.     Virtual Environment does already exist as: '__venvGL1_5_0'
    echo.
) else (
    echo.     Virtual Environment does NOT exist - now creating it as: '__venvGL1_5_0'

    @REM allow the use of system-site-packages (needed at least for Raspi)
    python -m venv --system-site-packages __venvGL1_5_0
    echo.     Done
    echo.
)

@REM start GLpipcheck
venvGL\Scripts\python gtools/GLpipcheck.py %1
echo.

