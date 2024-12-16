# cleanup.py

from pathlib import Path
from config import SYMBOLS, Timeframe, DATA_FOLDER
import os
import glob

def cleanup_old_files():
    """Remove old test files from data directories"""
    total_removed = 0
    
    # Get all CSV files with the test pattern
    pattern = str(Path(DATA_FOLDER) / "raw" / "**" / "*_20241117_20241217.csv")
    test_files = glob.glob(pattern, recursive=True)
    
    for file in test_files:
        try:
            print(f"Removing: {file}")
            os.remove(file)
            total_removed += 1
        except Exception as e:
            print(f"Error removing {file}: {e}")
            
    print(f"\nCleanup complete. Removed {total_removed} test files.")

if __name__ == "__main__":
    cleanup_old_files()