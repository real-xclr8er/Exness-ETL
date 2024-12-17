"""
scripts/build_executable.py

Build script to create executable for tick collector
"""

import PyInstaller.__main__
import os
from pathlib import Path

def build_collector():
    # Get the project root directory (one level up from scripts)
    root_dir = Path(__file__).parent.parent
    
    # Set the paths relative to root directory
    collector_path = str(root_dir / 'src' / 'collectors' / 'tick_collector.py')
    configs_path = str(root_dir / 'configs')
    
    PyInstaller.__main__.run([
        collector_path,
        '--onefile',
        '--noconsole',  # Runs without console window
        '--name', 'tick_collector',
        '--add-data', f'{configs_path};configs',  # Include config files if we add them later
    ])

if __name__ == "__main__":
    build_collector()