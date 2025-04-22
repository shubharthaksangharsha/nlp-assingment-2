#!/bin/bash
# Script to run the NLP Knowledge Base application

# Change to the script directory
cd "$(dirname "$0")"

# Default values
API_KEY=""
RUN_WEB=false

# Process command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --api_key)
            API_KEY="$2"
            shift 2
            ;;
        --web)
            RUN_WEB=true
            shift
            ;;
        *)
            echo "Unknown option: $1"
            echo "Usage: ./run.sh [--api_key API_KEY] [--web]"
            exit 1
            ;;
    esac
done

# Create and activate virtual environment
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install required packages with error handling
echo "Installing required packages..."
# This approach installs packages one by one to handle potential errors
while IFS= read -r requirement || [ -n "$requirement" ]; do
    # Skip comments and empty lines
    [[ $requirement =~ ^#.* || -z $requirement ]] && continue
    
    # Remove exact version requirements for problematic packages
    if [[ $requirement == wordcloud==* ]]; then
        echo "Installing wordcloud with compatible version..."
        pip install wordcloud --no-cache-dir || echo "Warning: Could not install wordcloud"
    elif [[ $requirement == numpy==* ]]; then
        echo "Installing numpy with compatible version..."
        pip install numpy --no-cache-dir || echo "Warning: Could not install numpy"
    else
        echo "Installing: $requirement"
        pip install "$requirement" --no-cache-dir || echo "Warning: Could not install $requirement"
    fi
done < requirements.txt

# Run the application based on mode
if [ "$RUN_WEB" = true ]; then
    echo "Starting web application..."
    cd web-app
    python copy_visualizations.py
    python app.py
else
    # Run the CLI application
    echo "Starting CLI application..."
    cd src
    if [ -z "$API_KEY" ]; then
        echo "No API key provided. Running with default settings."
        echo "For better rate limits, register at https://stackapps.com/apps/oauth/register"
        echo "and provide your API key with --api_key parameter."
        python main.py
    else
        echo "Using provided API key: $API_KEY"
        python main.py --api-key "$API_KEY"
    fi
fi

# Deactivate virtual environment
echo "Deactivating virtual environment..."
deactivate

echo "Script completed."
