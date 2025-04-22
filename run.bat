@echo off
setlocal

rem Change to the script directory
cd /d "%~dp0"

rem Create and activate virtual environment
if not exist venv (
    echo Creating virtual environment...
    python -m venv venv
)

rem Activate virtual environment
call venv\Scripts\activate.bat

rem Install required packages
echo Installing required packages...
pip install -r requirements.txt

rem Check if API key is provided
if "%~1"=="" (
    echo No API key provided. Running with default settings.
    echo For better rate limits, register at https://stackapps.com/apps/oauth/register
    echo and provide your API key as the first argument to this script.
    cd src
    python main.py
) else (
    set API_KEY=%~1
    echo Using provided API key: %API_KEY%
    cd src
    python main.py --api-key "%API_KEY%"
)

rem Deactivate virtual environment
call venv\Scripts\deactivate.bat

echo Script completed.

endlocal 