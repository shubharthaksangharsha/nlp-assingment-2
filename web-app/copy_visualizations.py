import os
import shutil

def copy_visualizations():
    """Copy visualization images from data/visualizations to static/img"""
    # Get the current directory (web-app)
    current_dir = os.path.dirname(os.path.abspath(__file__))
    # Get the parent directory
    parent_dir = os.path.dirname(current_dir)
    
    # Source and destination paths
    src_dir = os.path.join(parent_dir, 'data', 'visualizations')
    dest_dir = os.path.join(current_dir, 'static', 'img')
    
    # Create destination directory if it doesn't exist
    os.makedirs(dest_dir, exist_ok=True)
    
    # Check if source directory exists
    if not os.path.exists(src_dir):
        print(f"Source directory not found: {src_dir}")
        return
        
    # Copy visualization files
    for filename in os.listdir(src_dir):
        if filename.endswith(('.png', '.jpg', '.jpeg')):
            src_file = os.path.join(src_dir, filename)
            dest_file = os.path.join(dest_dir, filename)
            shutil.copy2(src_file, dest_file)
            print(f"Copied {filename} to static/img/")

if __name__ == "__main__":
    copy_visualizations() 