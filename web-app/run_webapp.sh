#!/bin/bash
# Script to launch the NLP Knowledge Base web application

# Make sure script is executable
# chmod +x run_webapp.sh

# Ensure we're in the script directory
cd "$(dirname "$0")"

# Copy visualization images to static directory
echo "Copying visualization images to static directory..."
if [ -f "copy_visualizations.py" ]; then
    python3 copy_visualizations.py
else
    echo "Warning: copy_visualizations.py not found, skipping visualization copy"
fi

# Run the Flask application
echo "Starting the web application..."
python3 app.py

# Note: For production deployment, consider using a WSGI server like Gunicorn:
# gunicorn -w 4 -b 0.0.0.0:5000 app:app 