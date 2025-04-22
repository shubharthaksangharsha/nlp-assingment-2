@echo off
REM Script to launch the NLP Knowledge Base web application with memory optimizations

REM Ensure we're in the script directory
cd /d "%~dp0"

REM Copy visualization images to static directory
echo Copying visualization images to static directory...
if exist copy_visualizations.py (
    python copy_visualizations.py
) else (
    echo Warning: copy_visualizations.py not found, skipping visualization copy
)

REM Set memory optimization environment variables
set PYTHONUNBUFFERED=1
set PYTHONOPTIMIZE=1

REM Check if waitress is installed, if not install it (memory efficient WSGI server for Windows)
python -c "import waitress" 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo Installing waitress server...
    pip install waitress
)

REM Run the Flask application with waitress for better memory management
echo Starting the web application with waitress-serve...
python -m waitress --host=0.0.0.0 --port=5000 --threads=2 --connection-limit=200 app:app

REM For development, uncomment the line below and comment the waitress line above
REM python app.py 