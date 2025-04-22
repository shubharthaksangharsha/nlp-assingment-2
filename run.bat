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

rem Download and extract dataset if it doesn't exist
if not exist data (
    echo Downloading dataset...
    
    rem Install gdown to handle Google Drive downloads
    pip install gdown
    
    rem Google Drive file ID
    set FILE_ID=1EPZ6mJvLAj0sJqNAWWLo8Bz90K2sSBgy
    echo Downloading from Google Drive (ID: %FILE_ID%)...
    python -c "import gdown; gdown.download('https://drive.google.com/uc?id=%FILE_ID%', 'data.zip', quiet=False)"
    
    if exist data.zip (
        echo Extracting dataset...
        powershell -command "Expand-Archive -Path data.zip -DestinationPath . -Force"
        
        rem Clean up the zip file
        del data.zip
        
        if exist data (
            echo Dataset extracted successfully.
        ) else (
            echo ERROR: Failed to extract dataset. Please download manually from the link in README.md
        )
    ) else (
        echo ERROR: Failed to download dataset. Please download manually from the link in README.md
    )
)

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