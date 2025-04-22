#!/bin/bash

# Replace with your actual API key
API_KEY="rl_QSELmsmpZPK2JvKfEHYZ8Pa9e"

# Define the list of tags you want to collect data for
# Add or remove tags as needed
TAGS=("nlp" "python" "machine-learning" "tensorflow" "pytorch" "nltk")

# Set the maximum number of questions per tag collection run
MAX_QUESTIONS=500

# Loop through each tag in the TAGS array
for TAG in "${TAGS[@]}"
do
  echo "=== Starting data collection for tag: $TAG ==="
  # Execute your main.py script for the current tag
  python main.py --api-key "$API_KEY" --max-questions "$MAX_QUESTIONS" --tag "$TAG" --force-collection

  # Optional: Add a small delay between collecting data for different tags
  # This can help avoid hitting API limits if the script finishes very quickly
  # sleep 5
done

echo "=== Finished data collection for all specified tags ==="
