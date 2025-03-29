#!/usr/bin/env python3
"""
Utility script to copy visualization images from the data directory to the static directory.
This is adapted for Vercel deployment.
"""

import os
import shutil
import sys

def copy_visualizations():
    """Copy visualization images from data/visualizations to static/img"""
    # Define paths for Vercel deployment
    script_dir = os.path.dirname(os.path.abspath(__file__))
    data_viz_dir = os.path.join(os.path.dirname(script_dir), 'data', 'visualizations')
    static_img_dir = os.path.join(script_dir, 'static', 'img')
    
    # Create static/img directory if it doesn't exist
    os.makedirs(static_img_dir, exist_ok=True)
    
    # Check if data/visualizations exists, if not create a demo data folder
    if not os.path.exists(data_viz_dir):
        print(f"Visualizations directory not found at {data_viz_dir}, creating demo data...")
        os.makedirs(data_viz_dir, exist_ok=True)
        # Here you could add code to generate sample visualizations if needed
    
    # Get list of visualization files
    viz_files = [f for f in os.listdir(data_viz_dir) if f.endswith(('.png', '.jpg', '.jpeg'))]
    
    if not viz_files:
        print(f"No visualization images found in {data_viz_dir}")
        return
    
    # Copy each file
    for file_name in viz_files:
        src_path = os.path.join(data_viz_dir, file_name)
        dst_path = os.path.join(static_img_dir, file_name)
        
        try:
            # Check if source and destination are the same file
            if os.path.abspath(src_path) != os.path.abspath(dst_path):
                shutil.copy2(src_path, dst_path)
                print(f"Copied {file_name} to static folder")
            else:
                print(f"Skipping {file_name} as source and destination are the same")
        except Exception as e:
            print(f"Error copying {file_name}: {e}")
    
    print("Visualization copying complete.")

if __name__ == "__main__":
    copy_visualizations() 