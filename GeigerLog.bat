@echo OFF
@REM script: GeigerLog.bat


@REM Clear Screen
cls

echo. ############################################  GeigerLog  Startup  #############################################

@REM Working Dir
set mypwd=%cd%
echo. Checking for Working Directory
echo.     Current Directory: %mypwd%

if exist geigerlog.py (
    echo.     Found file 'geigerlog.py'; taking this as GeigerLog working directory!
) else (
    echo.
    echo.     This is NOT your working directory for GeigerLog!
    echo.     Please change into the GeigerLog working directory, and then start GeigerLog again.
    echo.
    exit 1
)


@REM Virtual Environment
set myvenv=__venvGL1_5_0
echo. Checking for Virtual Environment

@REM Checking for command 'setup'
if "%~1"=="" (
	@REM no param given on command line
) else (
    if "%~1"=="setup" (
        echo.     GeigerLog Auto-Setup
        if exist __venvGL1_5_0\Scripts\activate (
            echo.     A Virtual Environment does already exist as: '%myvenv%'
        ) else (
            echo.     A Virtual Environment does NOT exist - now creating it as: '%myvenv%'

            @REM allow the use of system-site-packages (needed at least for Raspi)
            python -m venv --system-site-packages __venvGL1_5_0
            echo.     Done
        )
    )
)

@REM if venv exists start GeigerLog; install modules if needed
@REM if command 'setup' had been given, it is still active!
if exist __venvGL1_5_0\Scripts\activate (
    echo.     Using Virtual Environment '%myvenv%'
    %myvenv%\Scripts\python geigerlog.py %1 %2 %3 %4 %5 %6 %7 %8 %9
) else (
    echo.     A Virtual Environment does NOT exist - Please, start GeigerLog with 'GeigerLog.bat setup'
)

echo.
