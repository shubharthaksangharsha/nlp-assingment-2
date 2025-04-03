"""
Setup script to initialize data and configuration for Vercel deployment
"""

import os
import shutil
import sys

def setup_for_vercel():
    """Prepare the application for Vercel deployment"""
    # Get the root directory (parent of web-app)
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    # Create necessary directories in root
    data_dir = os.path.join(base_dir, 'data')
    categories_dir = os.path.join(data_dir, 'categories')
    visualizations_dir = os.path.join(data_dir, 'visualizations')
    
    os.makedirs(categories_dir, exist_ok=True)
    os.makedirs(visualizations_dir, exist_ok=True)
    
    # Create static directories in web-app
    web_app_dir = os.path.dirname(os.path.abspath(__file__))
    os.makedirs(os.path.join(web_app_dir, 'static', 'img'), exist_ok=True)
    os.makedirs(os.path.join(web_app_dir, 'static', 'css'), exist_ok=True)
    os.makedirs(os.path.join(web_app_dir, 'static', 'js'), exist_ok=True)
    
    print("Directory structure set up for Vercel deployment")
    
    # Debug information
    print("\nChecking data directory contents:")
    if os.path.exists(categories_dir):
        print("\nCategories directory contents:")
        for root, dirs, files in os.walk(categories_dir):
            print(f"\nDirectory: {root}")
            print("Files:", files)
    else:
        print("Categories directory does not exist!")
    
    print("\nVercel setup completed successfully")

if __name__ == "__main__":
    setup_for_vercel() 