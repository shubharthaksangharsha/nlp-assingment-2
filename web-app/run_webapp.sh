#!/bin/bash
# Script to launch the NLP Knowledge Base web application with Gunicorn for better memory management

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

# Install required packages if needed
if ! pip show gunicorn > /dev/null 2>&1; then
    echo "Installing gunicorn..."
    pip install gunicorn
fi

# Memory management settings (for low-memory environments)
export PYTHONUNBUFFERED=1
export PYTHONOPTIMIZE=1

# Check available memory and set worker count accordingly
total_memory_mb=$(free -m | awk '/^Mem:/{print $2}')
echo "Total system memory: ${total_memory_mb}MB"

if [ "$total_memory_mb" -lt 1024 ]; then
    # Less than 1GB RAM, use 1 worker with 2 threads
    workers=1
    threads=2
    echo "Low memory environment detected. Using 1 worker with 2 threads."
else
    # Standard formula: 2 * CPUs + 1
    workers=$(( $(nproc) * 2 + 1 ))
    threads=1
    echo "Normal memory environment. Using ${workers} workers."
fi

# Run the Flask application with Gunicorn for better performance and memory management
echo "Starting the web application with Gunicorn..."
gunicorn --workers=$workers --threads=$threads \
    --worker-class=gthread \
    --worker-tmp-dir=/dev/shm \
    --log-level=info \
    --bind=0.0.0.0:5000 \
    --timeout=120 \
    --max-requests=1000 \
    --max-requests-jitter=100 \
    app:app

# Note: For production deployment, consider using a WSGI server like Gunicorn:
# gunicorn -w 4 -b 0.0.0.0:5000 app:app 