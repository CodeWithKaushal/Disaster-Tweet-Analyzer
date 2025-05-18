"""
Script to clean up unwanted files and organize the project structure.
"""
import os
import shutil

print("Starting cleanup process...")

# Root directory of the project
root_dir = r'c:\Data\PROJECTS\Disaster-Tweet-Analyzer'

# Files that are needed in the root directory
needed_files = [
    'run.py',
    'Procfile',
    'README.md',
    'requirements.txt',
    '.gitignore',
    'disaster_app',
    'copy_files.py',
    'cleanup.py'
]

# Create necessary directories
data_dir = os.path.join(root_dir, 'disaster_app', 'data')
models_dir = os.path.join(root_dir, 'disaster_app', 'models')
os.makedirs(data_dir, exist_ok=True)
os.makedirs(models_dir, exist_ok=True)

# List all files in the root directory
for item in os.listdir(root_dir):
    item_path = os.path.join(root_dir, item)

    # Skip directories and needed files
    if item in needed_files or os.path.isdir(item_path) and item != '__pycache__':
        print(f"Keeping: {item}")
        continue

    # Print a message for handled files
    print(f"Found file: {item}")

print("Cleanup reporting completed. No files were moved to avoid overwrite prompts.")
