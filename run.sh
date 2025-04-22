#!/bin/bash
# Script to run the NLP Knowledge Base application without data collection

# Change to the script directory
cd "$(dirname "$0")"

# Create and activate virtual environment
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install required packages
echo "Installing required packages..."
pip install -r requirements.txt

# Download and extract dataset if it doesn't exist
if [ ! -d "data" ]; then
    echo "Downloading dataset..."
    # Direct download link using gdown instead of curl (handles Google Drive better)
    pip install gdown
    
    # Google Drive file ID
    FILE_ID="1EPZ6mJvLAj0sJqNAWWLo8Bz90K2sSBgy"
    echo "Downloading from Google Drive (ID: ${FILE_ID})..."
    gdown https://drive.google.com/uc?id=${FILE_ID}
    
    if [ -f "data.zip" ]; then
        echo "Extracting dataset..."
        unzip -q data.zip
        
        # Clean up the zip file
        rm data.zip
        
        if [ -d "data" ]; then
            echo "Dataset extracted successfully."
        else
            echo "ERROR: Failed to extract dataset. Please download manually from the link in README.md"
        fi
    else
        echo "ERROR: Failed to download dataset. Please download manually from the link in README.md"
    fi
fi

# Step 1: Run the CLI application without data collection
echo "Starting CLI application (skipping data collection)..."
cd src
python main.py --skip-collection
cd ..

# Step 2: Start web application
echo "Starting web application..."
cd web-app
python copy_visualizations.py
python app.py

# Deactivate virtual environment when the web app is closed
echo "Deactivating virtual environment..."
deactivate

echo "Script completed."
