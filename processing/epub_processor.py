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
        self.metadata = {}
        
        # Create directories if they don't exist
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.temp_dir.mkdir(parents=True, exist_ok=True)
        
        # Ensure logs directory exists
        logs_dir = Path('processing/logs')
        logs_dir.mkdir(parents=True, exist_ok=True)
        
        # Determine book_id and age from filename
        self._identify_book()
        
    def _identify_book(self):
        """Identify the book and set appropriate metadata"""
        filename = self.epub_path.name.lower()
        
        # Enhanced book identification with more precise patterns
        if re.search(r'hobbit|unexpected journey', filename):
            self.book_id = 'hobbit'
            self.age = 'THIRD_AGE'
            logger.info(f"Identified {self.epub_path.name} as The Hobbit (Third Age)")
        elif re.search(r'silmarillion', filename):
            self.book_id = 'silmarillion'
            self.age = 'FIRST_AGE'
            logger.info(f"Identified {self.epub_path.name} as The Silmarillion (First Age)")
        elif re.search(r'lord\s+of\s+the\s+rings|lotr|fellowship|two\s+towers|return\s+of\s+the\s+king', filename):
            self.book_id = 'lotr'
            self.age = 'THIRD_AGE'
            logger.info(f"Identified {self.epub_path.name} as The Lord of the Rings (Third Age)")
        elif re.search(r'children\s+of\s+hurin', filename):
            self.book_id = 'children_of_hurin'
            self.age = 'FIRST_AGE'
            logger.info(f"Identified {self.epub_path.name} as The Children of Húrin (First Age)")
        elif re.search(r'unfinished\s+tales', filename):
            self.book_id = 'unfinished_tales'
            self.age = 'MIXED_AGES'  # Contains stories from multiple ages
            logger.info(f"Identified {self.epub_path.name} as Unfinished Tales (Mixed Ages)")
        elif re.search(r'fall\s+of\s+gondolin', filename):
            self.book_id = 'fall_of_gondolin'
            self.age = 'FIRST_AGE'
            logger.info(f"Identified {self.epub_path.name} as The Fall of Gondolin (First Age)")
        elif re.search(r'beren\s+and\s+luthien', filename):
            self.book_id = 'beren_and_luthien'
            self.age = 'FIRST_AGE'
            logger.info(f"Identified {self.epub_path.name} as Beren and Lúthien (First Age)")
        else:
            self.book_id = 'unknown'
            self.age = 'UNKNOWN'
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
        except zipfile.BadZipFile:
            logger.error(f"File {self.epub_path.name} is not a valid ZIP/ePub file")
            return False
        except PermissionError:
            logger.error(f"Permission denied when extracting {self.epub_path.name}")
            return False
        except Exception as e:
            logger.error(f"Error extracting {self.epub_path.name}: {str(e)}")
            return False
    
    def find_content_files(self):
        """
        Find HTML content files in the extracted ePub.
        
        Returns:
            list: List of content file paths
            dict: Extracted metadata
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
            return content_files, {}
        
        try:
            # Parse the OPF file to find content files
            tree = ET.parse(opf_file)
            root = tree.getroot()
            
            # Extract namespace
            ns = {'': root.tag.split('}')[0].strip('{')} if '}' in root.tag else {}
            ns_prefix = '{' + next(iter(ns.values())) + '}' if ns else ''
            
            # Enhanced metadata extraction
            self._extract_metadata(root, ns_prefix)
            
            # Find the manifest element
            manifest = root.find('.//' + ns_prefix + 'manifest')
            if manifest is None:
                logger.error(f"Could not find manifest in OPF file: {opf_file}")
                return content_files, self.metadata
            
            # Get all items with MIME type for HTML
            html_items = []
            for item in manifest.findall('.//' + ns_prefix + 'item'):
                media_type = item.get('media-type')
                if media_type and ('html' in media_type or 'xhtml' in media_type):
                    html_items.append({
                        'id': item.get('id'),
                        'href': item.get('href')
                    })
            
            # Create a mapping of id to href
            id_to_item = {item['id']: item for item in html_items}
            
            # Try to find the spine to determine reading order
            spine = root.find('.//' + ns_prefix + 'spine')
            if spine is not None:
                # Get the itemrefs in order
                itemrefs = spine.findall('.//' + ns_prefix + 'itemref')
                
                for itemref in itemrefs:
                    idref = itemref.get('idref')
                    if idref in id_to_item:
                        # Get full path
                        opf_dir = os.path.dirname(opf_file)
                        content_path = os.path.normpath(os.path.join(opf_dir, id_to_item[idref]['href']))
                        content_files.append(content_path)
            
            # If no spine or couldn't resolve references, just use all HTML files
            if not content_files:
                logger.warning(f"Could not determine reading order, using all HTML files for {self.epub_path.name}")
                for html_item in html_items:
                    opf_dir = os.path.dirname(opf_file)
                    content_path = os.path.normpath(os.path.join(opf_dir, html_item['href']))
                    content_files.append(content_path)
            
            # If title wasn't found in metadata, try finding it in content
            if not self.book_title and self.metadata.get('title'):
                self.book_title = self.metadata['title']
                logger.info(f"Found book title from metadata: {self.book_title}")
            
            logger.info(f"Found {len(content_files)} content files in {self.epub_path.name}")
            return content_files, self.metadata
            
        except ET.ParseError:
            logger.error(f"Error parsing OPF file: {opf_file}")
            return content_files, self.metadata
        except Exception as e:
            logger.error(f"Error finding content files in {self.epub_path.name}: {str(e)}")
            return content_files, self.metadata
    
    def _extract_metadata(self, root, ns_prefix):
        """
        Extract enhanced metadata from OPF file.
        
        Args:
            root: XML root element
            ns_prefix: Namespace prefix
        """
        # Dublin Core metadata elements to extract
        dc_elements = {
            'title': 'title',
            'creator': 'author',
            'publisher': 'publisher',
            'date': 'publication_date',
            'language': 'language',
            'identifier': 'identifier',
            'description': 'description',
            'rights': 'rights',
            'subject': 'subject'
        }
        
        # Initialize metadata
        self.metadata = {
            'book_id': self.book_id,
            'age': self.age,
            'source_file': self.epub_path.name
        }
        
        # Extract Dublin Core metadata
        metadata_elem = root.find('.//' + ns_prefix + 'metadata')
        if metadata_elem is not None:
            for dc_name, meta_key in dc_elements.items():
                elem = metadata_elem.find('.//*[local-name()="' + dc_name + '"]')
                if elem is not None and elem.text:
                    if meta_key == 'title':
                        self.book_title = elem.text
                    
                    if meta_key == 'subject' and meta_key in self.metadata:
                        # Handle multiple subjects
                        if isinstance(self.metadata[meta_key], list):
                            self.metadata[meta_key].append(elem.text)
                        else:
                            self.metadata[meta_key] = [self.metadata[meta_key], elem.text]
                    else:
                        self.metadata[meta_key] = elem.text
        
        # If we found a title, update book_id if it was unknown
        if self.book_title and self.book_id == 'unknown':
            title_lower = self.book_title.lower()
            if 'hobbit' in title_lower:
                self.book_id = 'hobbit'
                self.age = 'THIRD_AGE'
            elif 'silmarillion' in title_lower:
                self.book_id = 'silmarillion'
                self.age = 'FIRST_AGE'
            elif any(term in title_lower for term in ['lord of the rings', 'fellowship', 'two towers', 'return of the king']):
                self.book_id = 'lotr'
                self.age = 'THIRD_AGE'
            
            # Update metadata with potentially new book_id
            self.metadata['book_id'] = self.book_id
            self.metadata['age'] = self.age
    
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
                soup = self._simple_html_parser(content)
                
                # Try to find chapter title
                title = self._extract_title(soup)
                
                # Extract main text
                text = self._extract_text(soup)
                
                # Extract special content
                special_content = self._extract_special_content(soup)
                
                if text.strip() or special_content:
                    chapter_number += 1
                    
                    # Determine if this is actually a chapter or some other content
                    content_type = "chapter"
                    if title:
                        title_lower = title.lower()
                        if any(word in title_lower for word in ['prologue', 'foreword', 'introduction', 'preface']):
                            content_type = "introduction"
                        elif any(word in title_lower for word in ['appendix', 'glossary', 'index']):
                            content_type = "appendix"
                    
                    chapter_data = {
                        'book_id': self.book_id,
                        'age': self.age,
                        'chapter_number': chapter_number,
                        'chapter_title': title if title else f"Chapter {chapter_number}",
                        'content_type': content_type,
                        'content': text,
                        'source_file': os.path.basename(file_path)
                    }
                    
                    # Add special content if found
                    if special_content:
                        chapter_data['special_content'] = special_content
                    
                    chapters.append(chapter_data)
                    logger.info(f"Extracted {content_type}: {chapter_data['chapter_title']}")
            except UnicodeDecodeError:
                logger.error(f"Unicode decode error in file {file_path}, trying with different encoding")
                try:
                    with open(file_path, 'r', encoding='latin-1') as file:
                        content = file.read()
                    # Process with alternative encoding...
                    # (Repeat extraction code or call a function)
                except Exception as inner_e:
                    logger.error(f"Failed to process {file_path} with alternative encoding: {str(inner_e)}")
            except FileNotFoundError:
                logger.error(f"Content file not found: {file_path}")
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
        h_tags = re.findall(r'<h[1-6][^>]*>(.*?)</h[1-6]>', body, re.IGNORECASE)
        
        # Extract paragraphs
        p_tags = re.findall(r'<p[^>]*>(.*?)</p>', body, re.IGNORECASE)
        
        # Find <div> or <span> elements with class or id indicating special content
        special_divs = re.findall(r'<div[^>]*(?:class|id)=["\'](?:poem|verse|song|quote)["\'][^>]*>(.*?)</div>', body, re.IGNORECASE | re.DOTALL)
        special_spans = re.findall(r'<span[^>]*(?:class|id)=["\'](?:poem|verse|song|quote)["\'][^>]*>(.*?)</span>', body, re.IGNORECASE | re.DOTALL)
        
        # Extract <blockquote> elements which often contain poems or songs
        blockquotes = re.findall(r'<blockquote[^>]*>(.*?)</blockquote>', body, re.IGNORECASE | re.DOTALL)
        
        # Find italicized blocks which might be poems/songs (common in Tolkien books)
        italic_blocks = re.findall(r'<(?:i|em)>((?:[^<]+|<(?!/?(?:i|em))[^>]*>)*)</(?:i|em)>', body, re.IGNORECASE | re.DOTALL)
        
        return {
            'headers': h_tags,
            'paragraphs': p_tags,
            'special_divs': special_divs,
            'special_spans': special_spans,
            'blockquotes': blockquotes,
            'italic_blocks': italic_blocks,
            'body': body
        }
    
    def _extract_title(self, soup):
        """
        Extract chapter title from parsed HTML.
        
        Args:
            soup (dict): Parsed HTML content
            
        Returns:
            str: Extracted title or None
        """
        if soup['headers']:
            # Try to find a header that looks like a chapter title
            for header in soup['headers']:
                # Clean HTML tags
                clean_header = re.sub(r'<[^>]+>', '', header)
                if clean_header.strip():
                    # Look for common chapter patterns
                    chapter_match = re.search(r'^(?:chapter|book)\s+([IVXLCDM0-9]+|\d+)', clean_header.strip(), re.IGNORECASE)
                    if chapter_match:
                        return clean_header.strip()
                    return clean_header.strip()
        
        return None
    
    def _extract_text(self, soup):
        """
        Extract main text content from parsed HTML.
        
        Args:
            soup (dict): Parsed HTML content
            
        Returns:
            str: Extracted text content
        """
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
    
    def _extract_special_content(self, soup):
        """
        Extract special content like poems, songs, and quotes.
        
        Args:
            soup (dict): Parsed HTML content
            
        Returns:
            list: List of special content items with type and text
        """
        special_content = []
        
        # Process special divs (with classes indicating poems/songs)
        for div in soup['special_divs']:
            clean_text = re.sub(r'<[^>]+>', ' ', div)
            clean_text = re.sub(r'\s+', ' ', clean_text).strip()
            if clean_text:
                special_content.append({
                    'type': self._determine_special_content_type(div),
                    'content': clean_text
                })
        
        # Process special spans
        for span in soup['special_spans']:
            clean_text = re.sub(r'<[^>]+>', ' ', span)
            clean_text = re.sub(r'\s+', ' ', clean_text).strip()
            if clean_text:
                special_content.append({
                    'type': self._determine_special_content_type(span),
                    'content': clean_text
                })
        
        # Process blockquotes which often contain poems or songs
        for quote in soup['blockquotes']:
            clean_text = re.sub(r'<[^>]+>', ' ', quote)
            clean_text = re.sub(r'\s+', ' ', clean_text).strip()
            if clean_text:
                special_content.append({
                    'type': self._determine_special_content_type(quote),
                    'content': clean_text
                })
        
        # Process italic blocks (common for poems in Tolkien)
        for italic in soup['italic_blocks']:
            clean_text = re.sub(r'<[^>]+>', ' ', italic)
            clean_text = re.sub(r'\s+', ' ', clean_text).strip()
            # Only consider longer italic blocks (at least 3 lines)
            if clean_text and clean_text.count('\n') >= 2:
                special_content.append({
                    'type': 'poem',  # Default to poem for italic blocks
                    'content': clean_text
                })
        
        # Look for other forms of special content in paragraphs
        for p in soup['paragraphs']:
            # Detect potential poetry by line breaks and indentation patterns
            if '<br' in p.lower() and (p.count('<br') >= 3 or '&nbsp;' in p):
                clean_text = re.sub(r'<[^>]+>', ' ', p)
                clean_text = re.sub(r'\s+', ' ', clean_text).strip()
                if clean_text:
                    special_content.append({
                        'type': 'poem',
                        'content': clean_text
                    })
        
        return special_content
    
    def _determine_special_content_type(self, content):
        """
        Determine the type of special content based on its characteristics.
        
        Args:
            content (str): HTML content string
            
        Returns:
            str: Content type ('poem', 'song', or 'quote')
        """
        content_lower = content.lower()
        
        # Check for explicit class/id indicators in the HTML
        if re.search(r'class=["\']poem["\']|id=["\']poem["\']', content_lower):
            return 'poem'
        if re.search(r'class=["\']song["\']|id=["\']song["\']', content_lower):
            return 'song'
        if re.search(r'class=["\']quote["\']|id=["\']quote["\']', content_lower):
            return 'quote'
        
        # Look for song indicators
        if re.search(r'sing|sang|sung|song', content_lower):
            return 'song'
        
        # Look for poetry indicators (line breaks, consistent indentation)
        if content_lower.count('<br') >= 3 or '&nbsp;' in content_lower:
            return 'poem'
        
        # Default to poem for special content (more common in Tolkien)
        return 'poem'
    
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
            
            # Initialize chapters info for metadata
            chapters_info = []
            
            # Save each chapter
            for chapter in chapters:
                chapter_file = book_dir / f"chapter_{chapter['chapter_number']:03d}.json"
                
                # Add timestamps to chapter data
                chapter['metadata'] = {
                    'extraction_date': datetime.now().isoformat(),
                    'processor_version': '1.1.0'
                }
                
                with open(chapter_file, 'w', encoding='utf-8') as f:
                    json.dump(chapter, f, indent=2, ensure_ascii=False)
                
                # Build chapter info for metadata
                chapters_info.append({
                    'number': chapter['chapter_number'],
                    'title': chapter['chapter_title'],
                    'type': chapter['content_type'],
                    'has_special_content': 'special_content' in chapter,
                    'file': f"chapter_{chapter['chapter_number']:03d}.json"
                })
            
            # Create enhanced metadata file
            metadata = {
                'book_id': self.book_id,
                'title': self.book_title or self.book_id.capitalize(),
                'age': self.age,
                'chapter_count': len(chapters),
                'chapters': chapters_info,
                'processed_date': datetime.now().isoformat(),
                'source_file': self.epub_path.name,
                'processor_version': '1.1.0'
            }
            
            # Add any extracted metadata
            if self.metadata:
                metadata.update({k: v for k, v in self.metadata.items() if k not in metadata})
            
            metadata_file = book_dir / "metadata.json"
            with open(metadata_file, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Saved {len(chapters)} chapters for {self.book_id} to {book_dir}")
            return True
        except PermissionError:
            logger.error(f"Permission denied when saving chapters for {self.book_id}")
            return False
        except Exception as e:
            logger.error(f"Error saving chapters for {self.book_id}: {str(e)}")
            return False
    
    def process(self):
        """
        Process the ePub file: extract, parse content, and save to output directory.
        
        Returns:
            bool: True if processing was successful, False otherwise
        """
        try:
            if not self.extract_epub():
                return False
            
            content_files, _ = self.find_content_files()
            if not content_files:
                logger.error(f"No content files found in {self.epub_path.name}")
                return False
            
            chapters = self.extract_text_from_content_files(content_files)
            if not chapters:
                logger.error(f"No chapters extracted from {self.epub_path.name}")
                return False
            
            return self.save_chapters(chapters)
        except Exception as e:
            logger.error(f"Unhandled exception during processing of {self.epub_path.name}: {str(e)}")
            return False


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