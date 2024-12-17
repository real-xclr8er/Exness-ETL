"""
src/utils/cleanup.py

Utility to clean up test data files from the project
"""

from pathlib import Path
import logging
import shutil
import os
import time

def setup_logging():
    """Configure logging"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )

def force_delete(file_path: Path, retries: int = 3, delay: float = 1.0):
    """
    Attempt to force delete a file with retries
    
    Args:
        file_path: Path to file to delete
        retries: Number of times to retry
        delay: Delay between retries in seconds
    """
    logger = logging.getLogger(__name__)
    
    for attempt in range(retries):
        try:
            if file_path.exists():
                os.chmod(file_path, 0o777)  # Give full permissions
                file_path.unlink()
                return True
        except Exception as e:
            if attempt < retries - 1:
                logger.warning(f"Retry {attempt + 1}/{retries} for {file_path}: {str(e)}")
                time.sleep(delay)
            else:
                logger.error(f"Failed to delete {file_path} after {retries} attempts: {str(e)}")
    return False

def clean_data_directory(base_path: Path):
    """Clean up old test data files"""
    logger = logging.getLogger(__name__)
    
    try:
        if base_path.exists():
            logger.info(f"Cleaning directory: {base_path}")
            
            # File patterns to clean
            patterns = ['**/*.parquet', '**/*.csv', '**/*.log']
            
            for pattern in patterns:
                for file in base_path.glob(pattern):
                    logger.info(f"Attempting to remove: {file}")
                    if force_delete(file):
                        logger.info(f"Successfully removed: {file}")
                    else:
                        logger.warning(f"Could not remove: {file} - may require manual deletion")
            
            logger.info("Cleanup completed")
        else:
            logger.warning(f"Directory does not exist: {base_path}")
            
    except Exception as e:
        logger.error(f"Error during cleanup: {str(e)}")

def main():
    """Main function to run cleanup"""
    setup_logging()
    logger = logging.getLogger(__name__)
    
    # Define paths to clean
    paths_to_clean = [
        Path("C:/DevProjects/trading_system/data"),
        Path("C:/DevProjects/trading_system/src/utils")
    ]
    
    logger.info("Starting cleanup process")
    
    for path in paths_to_clean:
        clean_data_directory(path)
    
    logger.info("Cleanup process completed")

if __name__ == "__main__":
    main()