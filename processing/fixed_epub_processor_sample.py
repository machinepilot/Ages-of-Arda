"""
Sample snippet showing how epub_processor.py should be fixed to use the new path_config system.
This is not a complete file but demonstrates the key changes needed.
"""

import os
import zipfile
import xml.etree.ElementTree as ET
import re
import json
import logging
from pathlib import Path
from datetime import datetime

# Import from path_config
from processing.path_config import get_path, get_log_file_path, resolve_path

# Set up logging using path_config
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(get_log_file_path('epub_processor')),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('epub_processor')

class EpubProcessor:
    """
    Processor for extracting content from ePub files and organizing it for further processing.
    """
    
    def __init__(self, epub_path, output_dir=None, temp_dir=None):
        """
        Initialize the ePub processor.
        
        Args:
            epub_path (str): Path to the ePub file
            output_dir (str, optional): Directory to save the extracted content
            temp_dir (str, optional): Temporary directory for extraction
        """
        # Use resolve_path to handle both absolute and relative paths
        self.epub_path = resolve_path(epub_path, 'epub_content')
        
        # Use get_path if not provided, otherwise resolve the provided path
        self.output_dir = resolve_path(output_dir, 'output') if output_dir else get_path('output')
        self.temp_dir = resolve_path(temp_dir, 'temp') if temp_dir else get_path('temp')
        
        # No need to create directories explicitly as path_config ensures they exist
        
        self.book_title = None
        self.book_id = None
        self.age = None
        self.metadata = {}
        
    def extract_epub(self):
        """Extract the ePub file to the temporary directory."""
        logger.info(f"Extracting ePub: {self.epub_path}")
        
        # Create a unique subdirectory for this book
        book_temp_dir = self.temp_dir / self.epub_path.stem
        book_temp_dir.mkdir(parents=True, exist_ok=True)
        
        # Extract the ePub (which is a ZIP file)
        with zipfile.ZipFile(self.epub_path, 'r') as zip_ref:
            zip_ref.extractall(book_temp_dir)
            
        logger.info(f"Extracted to: {book_temp_dir}")
        return book_temp_dir
        
    def process(self):
        """Process the ePub file and extract its content."""
        # Extract the ePub
        extracted_dir = self.extract_epub()
        
        # Find content files
        content_files = self.find_content_files(extracted_dir)
        
        # Extract text from content files
        chapters = self.extract_text_from_content_files(content_files)
        
        # Save chapters to output
        self.save_chapters(chapters)
        
        return {
            "book_title": self.book_title,
            "book_id": self.book_id,
            "age": self.age,
            "chapters": len(chapters)
        }
    
    # Rest of the class implementation would follow...


def process_epub_file(epub_path, output_dir=None, temp_dir=None):
    """
    Process a single ePub file.
    
    Args:
        epub_path (str): Path to the ePub file
        output_dir (str, optional): Directory to save output
        temp_dir (str, optional): Temporary directory
        
    Returns:
        dict: Processing results
    """
    processor = EpubProcessor(epub_path, output_dir, temp_dir)
    return processor.process()


def process_all_epubs(epub_dir=None, output_dir=None, temp_dir=None):
    """
    Process all ePub files in a directory.
    
    Args:
        epub_dir (str, optional): Directory containing ePub files
        output_dir (str, optional): Directory to save output
        temp_dir (str, optional): Temporary directory
        
    Returns:
        list: List of processing results
    """
    # Use get_path if directories not provided
    epub_dir = resolve_path(epub_dir, 'epub_content') if epub_dir else get_path('epub_content')
    output_dir = resolve_path(output_dir, 'output') if output_dir else get_path('output')
    temp_dir = resolve_path(temp_dir, 'temp') if temp_dir else get_path('temp')
    
    results = []
    
    # Process each ePub file
    for epub_file in epub_dir.glob("*.epub"):
        logger.info(f"Processing ePub file: {epub_file}")
        result = process_epub_file(epub_file, output_dir, temp_dir)
        results.append(result)
        
    logger.info(f"Processed {len(results)} ePub files")
    return results 