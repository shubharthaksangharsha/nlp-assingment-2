@echo off
REM Script to launch the NLP Knowledge Base web application on Windows

REM Ensure we're in the script directory
cd /d "%~dp0"

echo Copying visualization images to static directory...
python copy_visualizations.py

echo Starting the web application...
python app.py

REM Note: For production deployment, consider using a WSGI server like Waitress:
REM pip install waitress
REM python -m waitress --listen=0.0.0.0:5000 app:app 