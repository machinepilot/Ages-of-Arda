"""
Main Processing Script for Ages of Arda

This script coordinates the processing of ePub files into the Memory Bank system,
integrating all components of the processing workflow.
"""

import os
import sys
import argparse
import logging
from pathlib import Path

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join('processing', 'logs', 'main.log')),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('main')

# Import our modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from processing.epub_processor import process_all_epubs
from processing.schema_validator import SchemaValidator
from processing.checkpoint_manager import get_checkpoint_manager

def setup_directories():
    """
    Set up the necessary directories for processing.
    Following cross-platform directory creation guidelines.
    
    Returns:
        dict: Dictionary of directory paths
    """
    dirs = {
        'temp': Path('processing/temp'),
        'output': Path('processing/output'),
        'logs': Path('processing/logs'),
        'epub_content': Path('processing/epub_content'),
        'json_output': Path('processing/json_output'),
        'schemas': Path('processing/schemas'),
        'checkpoints': Path('processing/checkpoints'),
        'consolidated': Path('processing/consolidated')
    }
    
    # Create directories with proper error handling
    for name, dir_path in dirs.items():
        try:
            dir_path.mkdir(parents=True, exist_ok=True)
            logger.info(f"Ensured directory exists: {dir_path}")
        except Exception as e:
            logger.error(f"Failed to create directory {dir_path}: {str(e)}")
    
    return dirs

def process_epubs(epub_dir, output_dir):
    """
    Process all ePub files in the specified directory.
    
    Args:
        epub_dir (str): Directory containing ePub files
        output_dir (str): Directory to save extracted content
        
    Returns:
        dict: Processing results
    """
    logger.info(f"Processing ePubs from {epub_dir}")
    checkpoint_manager = get_checkpoint_manager()
    
    # Check for existing checkpoint
    checkpoint = checkpoint_manager.load_checkpoint("epub_processing")
    if checkpoint:
        logger.info(f"Found existing checkpoint for ePub processing")
        # Check if all books are already processed
        if checkpoint.get("status") == "complete":
            logger.info("ePub processing already complete, skipping")
            return checkpoint.get("results", {})
    
    # Process ePubs
    results = process_all_epubs(epub_dir, output_dir)
    
    # Save checkpoint
    checkpoint_data = {
        "status": "complete",
        "epub_dir": str(epub_dir),
        "output_dir": str(output_dir),
        "results": results
    }
    checkpoint_manager.save_checkpoint("epub_processing", checkpoint_data)
    
    return results

def main():
    """
    Main processing function that coordinates all steps.
    """
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Process ePubs for the Ages of Arda Memory Bank")
    parser.add_argument("--epub-dir", default="raw_inputs/New Files", help="Directory containing ePub files")
    parser.add_argument("--skip-existing", action="store_true", help="Skip processing if output already exists")
    parser.add_argument("--clean", action="store_true", help="Clean output directories before processing")
    args = parser.parse_args()
    
    logger.info("Starting Ages of Arda ePub processing")
    
    # Set up directories
    dirs = setup_directories()
    
    # Check if we should clean output directories
    if args.clean:
        logger.info("Cleaning output directories")
        for dir_name in ['temp', 'output', 'epub_content', 'json_output']:
            dir_path = dirs[dir_name]
            for item in dir_path.glob("*"):
                if item.is_file():
                    item.unlink()
                elif item.is_dir():
                    import shutil
                    shutil.rmtree(item)
    
    # Process ePubs
    epub_results = process_epubs(args.epub_dir, dirs['epub_content'])
    
    logger.info("Processing complete.")
    logger.info(f"Successful: {len(epub_results.get('successful', []))} files")
    logger.info(f"Failed: {len(epub_results.get('failed', []))} files")
    
    # Output summary
    print("\nProcessing Summary:")
    print("===================")
    print(f"Processed {len(epub_results.get('successful', [])) + len(epub_results.get('failed', []))} ePub files")
    print(f"Successful: {len(epub_results.get('successful', []))}")
    print(f"Failed: {len(epub_results.get('failed', []))}")
    
    # List successful files
    if epub_results.get('successful'):
        print("\nSuccessfully processed:")
        for file in epub_results.get('successful', []):
            print(f"- {file}")
    
    # List failed files
    if epub_results.get('failed'):
        print("\nFailed to process:")
        for file in epub_results.get('failed', []):
            print(f"- {file}")
    
    # Provide next steps
    print("\nNext Steps:")
    print("1. Review extracted content in 'processing/epub_content'")
    print("2. Run entity extraction script to identify characters, locations, etc.")
    print("3. Validate extracted entities against schemas")
    print("4. Generate final JSON files for Memory Bank integration")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logger.exception(f"Unhandled exception in main process: {str(e)}")
        print(f"Error: {str(e)}")
        sys.exit(1) 