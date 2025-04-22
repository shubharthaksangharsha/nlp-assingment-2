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
echo Activating virtual environment...
call venv\Scripts\activate.bat

rem Install required packages
echo Installing required packages...
pip install -r requirements.txt

rem Step 1: Run the CLI application without data collection
echo Starting CLI application (skipping data collection)...
cd src
python main.py --skip-collection
cd ..

rem Step 2: Start web application
echo Starting web application...
cd web-app
python copy_visualizations.py
python app.py

rem Deactivate virtual environment when the web app is closed
echo Deactivating virtual environment...
call venv\Scripts\deactivate.bat

echo Script completed.

endlocal 