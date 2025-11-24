# Convert PNG to ICO for Windows shortcut
from PIL import Image
import sys
import os

def convert_png_to_ico(png_path, ico_path):
    """Convert PNG image to ICO format for Windows shortcuts"""
    try:
        img = Image.open(png_path)
        
        # Convert to RGBA if not already
        if img.mode != 'RGBA':
            img = img.convert('RGBA')
        
        # Get image dimensions
        width, height = img.size
        
        # Resize to fill entire icon area with no padding
        canvas_size = 256
        img_resized = img.resize((canvas_size, canvas_size), Image.Resampling.LANCZOS)
        new_img = img_resized
        
        # Save as ICO with multiple sizes for maximum visibility
        new_img.save(ico_path, format='ICO', sizes=[(256, 256), (128, 128), (96, 96), (64, 64), (48, 48), (32, 32), (24, 24), (16, 16)])
        print(f"Successfully converted {png_path} to {ico_path}")
        return True
    except Exception as e:
        print(f"Error converting icon: {e}")
        return False

if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.abspath(__file__))
    png_path = os.path.join(script_dir, "desktop_icon.png")
    ico_path = os.path.join(script_dir, "stride_icon.ico")
    
    if os.path.exists(png_path):
        convert_png_to_ico(png_path, ico_path)
    else:
        print(f"Error: {png_path} not found")
        sys.exit(1)
