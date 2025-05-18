"""
Script to copy all necessary templates and static files to the disaster_app directory.
"""
import shutil
import os

# Base directories
src_root = r'c:\Data\PROJECTS\Disaster-Tweet-Analyzer'
dst_root = os.path.join(src_root, 'disaster_app')

# Create necessary directories if they don't exist
os.makedirs(os.path.join(dst_root, 'models'), exist_ok=True)
os.makedirs(os.path.join(dst_root, 'templates'), exist_ok=True)
os.makedirs(os.path.join(dst_root, 'static', 'css'), exist_ok=True)
os.makedirs(os.path.join(dst_root, 'static', 'js'), exist_ok=True)
os.makedirs(os.path.join(dst_root, 'static', 'images'), exist_ok=True)

# Copy model files
model_files = ['lr_model.pkl', 'vectorizer.pkl', 'scaler.pkl']
for model_file in model_files:
    src_path = os.path.join(src_root, model_file)
    dst_path = os.path.join(dst_root, 'models', model_file)
    if os.path.exists(src_path):
        shutil.copy2(src_path, dst_path)
        print(f"Copied {model_file} to models directory")

# Copy all templates
src_templates = os.path.join(src_root, 'templates')
dst_templates = os.path.join(dst_root, 'templates')
if os.path.exists(src_templates):
    for filename in os.listdir(src_templates):
        src_file = os.path.join(src_templates, filename)
        dst_file = os.path.join(dst_templates, filename)
        if os.path.isfile(src_file):
            shutil.copy2(src_file, dst_file)
            print(f"Copied template {filename}")

# Copy all static files (CSS, JS, images)
src_static = os.path.join(src_root, 'static')
dst_static = os.path.join(dst_root, 'static')
if os.path.exists(src_static):
    # CSS files
    css_dir = os.path.join(src_static, 'css')
    if os.path.exists(css_dir):
        for filename in os.listdir(css_dir):
            src_file = os.path.join(css_dir, filename)
            dst_file = os.path.join(dst_static, 'css', filename)
            if os.path.isfile(src_file):
                shutil.copy2(src_file, dst_file)
                print(f"Copied CSS file {filename}")

    # JS files
    js_dir = os.path.join(src_static, 'js')
    if os.path.exists(js_dir):
        for filename in os.listdir(js_dir):
            src_file = os.path.join(js_dir, filename)
            dst_file = os.path.join(dst_static, 'js', filename)
            if os.path.isfile(src_file):
                shutil.copy2(src_file, dst_file)
                print(f"Copied JS file {filename}")

    # Image files
    img_dir = os.path.join(src_static, 'images')
    if os.path.exists(img_dir):
        for filename in os.listdir(img_dir):
            src_file = os.path.join(img_dir, filename)
            dst_file = os.path.join(dst_static, 'images', filename)
            if os.path.isfile(src_file):
                shutil.copy2(src_file, dst_file)
                print(f"Copied image file {filename}")
            # Handle subdirectories
            elif os.path.isdir(src_file):
                dst_subdir = os.path.join(dst_static, 'images', filename)
                if not os.path.exists(dst_subdir):
                    os.makedirs(dst_subdir)
                for subfile in os.listdir(src_file):
                    src_subfile = os.path.join(src_file, subfile)
                    dst_subfile = os.path.join(dst_subdir, subfile)
                    if os.path.isfile(src_subfile):
                        shutil.copy2(src_subfile, dst_subfile)
                        print(f"Copied image file {filename}/{subfile}")

print("File copying completed.")
