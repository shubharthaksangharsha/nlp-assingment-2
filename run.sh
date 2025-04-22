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
