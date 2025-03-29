"""
Setup script to initialize data and configuration for Vercel deployment
"""

import os
import shutil
import sys

def setup_for_vercel():
    """Prepare the application for Vercel deployment"""
    # Create necessary directories
    os.makedirs('data/categories', exist_ok=True)
    os.makedirs('data/visualizations', exist_ok=True)
    os.makedirs('web-app/static/img', exist_ok=True)
    os.makedirs('web-app/static/css', exist_ok=True)
    os.makedirs('web-app/static/js', exist_ok=True)
    
    print("Directory structure set up for Vercel deployment")
    
    # Copy static assets if needed
    # You might want to add more code here to copy default data or generate placeholders
    
    # Run visualization copy script
    try:
        from web_app.copy_visualizations_vercel import copy_visualizations
        copy_visualizations()
    except Exception as e:
        print(f"Error setting up visualizations: {e}")
    
    print("Vercel setup completed successfully")

if __name__ == "__main__":
    setup_for_vercel() 