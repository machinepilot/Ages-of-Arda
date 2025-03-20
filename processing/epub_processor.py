"""
ePub Processor for Ages of Arda

This module provides functionality for extracting and processing content from ePub files
for integration into the Ages of Arda Memory Bank system.
"""

import os
import zipfile
import xml.etree.ElementTree as ET
import re
import json
import logging
from pathlib import Path
from datetime import datetime

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join('processing', 'logs', 'epub_processing.log')),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('epub_processor')

class EpubProcessor:
    """
    Processor for extracting content from ePub files and organizing it for further processing.
    """
    
    def __init__(self, epub_path, output_dir, temp_dir=None):
        """
        Initialize the ePub processor.
        
        Args:
            epub_path (str): Path to the ePub file
            output_dir (str): Directory to save the extracted content
            temp_dir (str, optional): Temporary directory for extraction
        """
        self.epub_path = Path(epub_path)
        self.output_dir = Path(output_dir)
        self.temp_dir = Path(temp_dir) if temp_dir else Path('processing/temp')
        self.book_title = None
        self.book_id = None
        self.age = None
        
        # Create directories if they don't exist
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.temp_dir.mkdir(parents=True, exist_ok=True)
        
        # Determine book_id and age from filename
        self._identify_book()
        
    def _identify_book(self):
        """Identify the book and set appropriate metadata"""
        filename = self.epub_path.name.lower()
        
        if 'hobbit' in filename:
            self.book_id = 'hobbit'
            self.age = 'third_age'
            logger.info(f"Identified {self.epub_path.name} as The Hobbit (Third Age)")
        elif 'silmarillion' in filename:
            self.book_id = 'silmarillion'
            self.age = 'first_age'
            logger.info(f"Identified {self.epub_path.name} as The Silmarillion (First Age)")
        elif 'lord of the rings' in filename or 'lotr' in filename:
            self.book_id = 'lotr'
            self.age = 'third_age'
            logger.info(f"Identified {self.epub_path.name} as The Lord of the Rings (Third Age)")
        else:
            self.book_id = 'unknown'
            self.age = 'unknown'
            logger.warning(f"Could not identify book type for {self.epub_path.name}")
    
    def extract_epub(self):
        """
        Extract the ePub file contents to the temporary directory.
        
        Returns:
            bool: True if extraction was successful, False otherwise
        """
        try:
            # Extract to temp directory
            extraction_dir = self.temp_dir / self.book_id
            extraction_dir.mkdir(exist_ok=True)
            
            with zipfile.ZipFile(self.epub_path, 'r') as zip_ref:
                zip_ref.extractall(extraction_dir)
            
            logger.info(f"Extracted {self.epub_path.name} to {extraction_dir}")
            return True
        except Exception as e:
            logger.error(f"Error extracting {self.epub_path.name}: {str(e)}")
            return False
    
    def find_content_files(self):
        """
        Find HTML content files in the extracted ePub.
        
        Returns:
            list: List of content file paths
        """
        extraction_dir = self.temp_dir / self.book_id
        content_files = []
        
        # Find the OPF file (content.opf or package.opf typically)
        opf_file = None
        for root, _, files in os.walk(extraction_dir):
            for file in files:
                if file.endswith('.opf'):
                    opf_file = os.path.join(root, file)
                    break
            if opf_file:
                break
        
        if not opf_file:
            logger.error(f"Could not find OPF file in {self.epub_path.name}")
            return content_files
        
        try:
            # Parse the OPF file to find content files
            tree = ET.parse(opf_file)
            root = tree.getroot()
            
            # Extract namespace
            ns = {'': root.tag.split('}')[0].strip('{')} if '}' in root.tag else {}
            ns_prefix = '{' + next(iter(ns.values())) + '}' if ns else ''
            
            # Find the manifest element
            manifest = root.find('.//' + ns_prefix + 'manifest')
            if manifest is None:
                logger.error(f"Could not find manifest in OPF file: {opf_file}")
                return content_files
            
            # Get all items with MIME type for HTML
            html_items = []
            for item in manifest.findall('.//' + ns_prefix + 'item'):
                media_type = item.get('media-type')
                if media_type and ('html' in media_type or 'xhtml' in media_type):
                    html_items.append(item.get('href'))
            
            # Try to find the spine to determine reading order
            spine = root.find('.//' + ns_prefix + 'spine')
            if spine is not None:
                # Get the itemrefs in order
                itemrefs = spine.findall('.//' + ns_prefix + 'itemref')
                id_to_href = {item.get('id'): item.get('href') for item in manifest.findall('.//' + ns_prefix + 'item')}
                
                for itemref in itemrefs:
                    idref = itemref.get('idref')
                    if idref in id_to_href and id_to_href[idref] in html_items:
                        # Get full path
                        opf_dir = os.path.dirname(opf_file)
                        content_path = os.path.normpath(os.path.join(opf_dir, id_to_href[idref]))
                        content_files.append(content_path)
            
            # If no spine or couldn't resolve references, just use all HTML files
            if not content_files:
                logger.warning(f"Could not determine reading order, using all HTML files for {self.epub_path.name}")
                for html_item in html_items:
                    opf_dir = os.path.dirname(opf_file)
                    content_path = os.path.normpath(os.path.join(opf_dir, html_item))
                    content_files.append(content_path)
            
            # Extract book title
            title_elem = root.find('.//' + ns_prefix + 'title')
            if title_elem is not None and title_elem.text:
                self.book_title = title_elem.text
                logger.info(f"Found book title: {self.book_title}")
            
            logger.info(f"Found {len(content_files)} content files in {self.epub_path.name}")
            return content_files
            
        except Exception as e:
            logger.error(f"Error finding content files in {self.epub_path.name}: {str(e)}")
            return content_files
    
    def extract_text_from_content_files(self, content_files):
        """
        Extract text content from HTML files.
        
        Args:
            content_files (list): List of content file paths
            
        Returns:
            list: List of chapter data dictionaries
        """
        chapters = []
        chapter_number = 0
        
        for file_path in content_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as file:
                    content = file.read()
                
                # Extract chapter title and text
                # This is a simple approach and might need customization for different book formats
                soup = self._simple_html_parser(content)
                
                # Try to find chapter title
                title = self._extract_title(soup)
                
                # Extract main text
                text = self._extract_text(soup)
                
                if text.strip():
                    chapter_number += 1
                    chapter_data = {
                        'book_id': self.book_id,
                        'age': self.age,
                        'chapter_number': chapter_number,
                        'chapter_title': title if title else f"Chapter {chapter_number}",
                        'content': text,
                        'source_file': os.path.basename(file_path)
                    }
                    chapters.append(chapter_data)
                    logger.info(f"Extracted chapter: {chapter_data['chapter_title']}")
            except Exception as e:
                logger.error(f"Error processing content file {file_path}: {str(e)}")
        
        return chapters
    
    def _simple_html_parser(self, html_content):
        """
        Simple HTML parser to extract content without BeautifulSoup dependency.
        
        Args:
            html_content (str): HTML content string
            
        Returns:
            dict: Dictionary with simple parsed structure
        """
        # Clean HTML to simplify parsing
        content = html_content.replace('\n', ' ')
        
        # Extract body
        body_match = re.search(r'<body[^>]*>(.*?)</body>', content, re.IGNORECASE | re.DOTALL)
        body = body_match.group(1) if body_match else content
        
        # Find headers for title
        h_tags = re.findall(r'<h[1-3][^>]*>(.*?)</h[1-3]>', body, re.IGNORECASE)
        
        # Extract paragraphs
        p_tags = re.findall(r'<p[^>]*>(.*?)</p>', body, re.IGNORECASE)
        
        return {
            'headers': h_tags,
            'paragraphs': p_tags,
            'body': body
        }
    
    def _extract_title(self, soup):
        """Extract chapter title from parsed HTML"""
        if soup['headers']:
            # Try to find a header that looks like a chapter title
            for header in soup['headers']:
                # Clean HTML tags
                clean_header = re.sub(r'<[^>]+>', '', header)
                if clean_header.strip():
                    return clean_header.strip()
        
        return None
    
    def _extract_text(self, soup):
        """Extract main text content from parsed HTML"""
        text = ""
        
        # Extract paragraphs
        for p in soup['paragraphs']:
            # Clean HTML tags
            clean_p = re.sub(r'<[^>]+>', '', p)
            if clean_p.strip():
                text += clean_p.strip() + "\n\n"
        
        # If no paragraphs found, try extracting from body
        if not text.strip() and soup['body']:
            # Remove all HTML tags and extract text
            body_text = re.sub(r'<[^>]+>', ' ', soup['body'])
            # Normalize whitespace
            body_text = re.sub(r'\s+', ' ', body_text).strip()
            text = body_text
        
        return text
    
    def save_chapters(self, chapters):
        """
        Save extracted chapters to JSON files.
        
        Args:
            chapters (list): List of chapter data dictionaries
            
        Returns:
            bool: True if saving was successful, False otherwise
        """
        try:
            # Create book directory
            book_dir = self.output_dir / self.book_id
            book_dir.mkdir(exist_ok=True)
            
            # Save each chapter
            for chapter in chapters:
                chapter_file = book_dir / f"chapter_{chapter['chapter_number']:03d}.json"
                with open(chapter_file, 'w', encoding='utf-8') as f:
                    json.dump(chapter, f, indent=2, ensure_ascii=False)
            
            # Create metadata file
            metadata = {
                'book_id': self.book_id,
                'title': self.book_title or self.book_id.capitalize(),
                'age': self.age,
                'chapter_count': len(chapters),
                'chapters': [
                    {
                        'number': chapter['chapter_number'],
                        'title': chapter['chapter_title'],
                        'file': f"chapter_{chapter['chapter_number']:03d}.json"
                    }
                    for chapter in chapters
                ],
                'processed_date': datetime.now().isoformat(),
                'source_file': self.epub_path.name
            }
            
            metadata_file = book_dir / "metadata.json"
            with open(metadata_file, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Saved {len(chapters)} chapters for {self.book_id} to {book_dir}")
            return True
        except Exception as e:
            logger.error(f"Error saving chapters for {self.book_id}: {str(e)}")
            return False
    
    def process(self):
        """
        Process the ePub file: extract, parse content, and save to output directory.
        
        Returns:
            bool: True if processing was successful, False otherwise
        """
        if not self.extract_epub():
            return False
        
        content_files = self.find_content_files()
        if not content_files:
            logger.error(f"No content files found in {self.epub_path.name}")
            return False
        
        chapters = self.extract_text_from_content_files(content_files)
        if not chapters:
            logger.error(f"No chapters extracted from {self.epub_path.name}")
            return False
        
        return self.save_chapters(chapters)


def process_epub_file(epub_path, output_dir):
    """
    Process a single ePub file.
    
    Args:
        epub_path (str): Path to the ePub file
        output_dir (str): Directory to save the extracted content
        
    Returns:
        bool: True if processing was successful, False otherwise
    """
    processor = EpubProcessor(epub_path, output_dir)
    return processor.process()


def process_all_epubs(epub_dir, output_dir):
    """
    Process all ePub files in a directory.
    
    Args:
        epub_dir (str): Directory containing ePub files
        output_dir (str): Directory to save the extracted content
        
    Returns:
        dict: Dictionary with processing results
    """
    results = {
        'successful': [],
        'failed': []
    }
    
    epub_dir = Path(epub_dir)
    output_dir = Path(output_dir)
    
    # Create output directory if it doesn't exist
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Find all ePub files
    epub_files = list(epub_dir.glob('*.epub'))
    logger.info(f"Found {len(epub_files)} ePub files in {epub_dir}")
    
    for epub_file in epub_files:
        logger.info(f"Processing {epub_file.name}")
        if process_epub_file(epub_file, output_dir):
            results['successful'].append(epub_file.name)
        else:
            results['failed'].append(epub_file.name)
    
    logger.info(f"Processing complete. Successful: {len(results['successful'])}, Failed: {len(results['failed'])}")
    
    # Save processing report
    report = {
        'timestamp': datetime.now().isoformat(),
        'epub_directory': str(epub_dir),
        'output_directory': str(output_dir),
        'total_files': len(epub_files),
        'successful_count': len(results['successful']),
        'failed_count': len(results['failed']),
        'successful_files': results['successful'],
        'failed_files': results['failed']
    }
    
    report_file = output_dir / 'processing_report.json'
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2)
    
    logger.info(f"Processing report saved to {report_file}")
    
    return results


if __name__ == "__main__":
    epub_directory = os.path.join('raw_inputs', 'New Files')
    output_directory = os.path.join('processing', 'epub_content')
    
    process_all_epubs(epub_directory, output_directory) 