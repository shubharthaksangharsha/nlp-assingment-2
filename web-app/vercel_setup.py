"""
Setup script to initialize data and configuration for Vercel deployment
"""

import os
import shutil
import sys
import json
import pandas as pd

def ensure_dir(directory):
    """Create directory if it doesn't exist"""
    if not os.path.exists(directory):
        os.makedirs(directory)
        print(f"Created directory: {directory}")

def copy_data_files(src_dir, dest_dir):
    """Copy data files from source to destination directory"""
    if not os.path.exists(src_dir):
        print(f"Source directory does not exist: {src_dir}")
        return
        
    ensure_dir(dest_dir)
    
    for item in os.listdir(src_dir):
        src_path = os.path.join(src_dir, item)
        # For Vercel, use /var/task path
        dest_path = os.path.join('/var/task', dest_dir, item)
        
        if os.path.isfile(src_path):
            shutil.copy2(src_path, dest_path)
            print(f"Copied file: {item} to {dest_path}")
        elif os.path.isdir(src_path):
            if not os.path.exists(dest_path):
                os.makedirs(dest_path)
            copy_data_files(src_path, dest_path)

def setup_for_vercel():
    """Prepare the application for Vercel deployment"""
    print("Starting Vercel setup...")
    
    # Get the root directory (parent of web-app)
    web_app_dir = os.path.dirname(os.path.abspath(__file__))
    base_dir = os.path.dirname(web_app_dir)
    
    # Define directory paths
    data_dir = os.path.join(base_dir, 'data')
    categories_dir = os.path.join(data_dir, 'categories')
    visualizations_dir = os.path.join(data_dir, 'visualizations')
    
    # Create necessary directories
    ensure_dir(data_dir)
    ensure_dir(categories_dir)
    ensure_dir(visualizations_dir)
    
    # Create static directories in web-app
    ensure_dir(os.path.join(web_app_dir, 'static', 'img'))
    ensure_dir(os.path.join(web_app_dir, 'static', 'css'))
    ensure_dir(os.path.join(web_app_dir, 'static', 'js'))
    
    # Copy data files from source to Vercel environment
    vercel_data_dir = os.path.join(os.getcwd(), 'data')
    copy_data_files(data_dir, vercel_data_dir)
    
    # Verify data files
    print("\nVerifying data files:")
    for root, dirs, files in os.walk(vercel_data_dir):
        print(f"\nDirectory: {root}")
        print("Files:", files)
        
        # Check CSV and JSON files
        for file in files:
            if file.endswith(('.csv', '.json')):
                file_path = os.path.join(root, file)
                try:
                    if file.endswith('.csv'):
                        df = pd.read_csv(file_path)
                        print(f"Successfully verified CSV file: {file} ({len(df)} rows)")
                    else:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            data = json.load(f)
                            print(f"Successfully verified JSON file: {file}")
                except Exception as e:
                    print(f"Error verifying {file}: {str(e)}")
    
    print("\nVercel setup completed successfully")

if __name__ == "__main__":
    setup_for_vercel() 