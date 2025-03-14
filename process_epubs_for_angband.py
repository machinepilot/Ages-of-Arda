#!/usr/bin/env python
"""
process_epubs_for_angband.py

This script processes EPUB files containing Tolkien's works and extracts their content
for integration into the Angband game's memory system. It parses the EPUB files,
extracts the text content, and formats it for use in the Ages of Arda companion system.

Usage:
    python process_epubs_for_angband.py

The script expects the EPUB files to be located in the 'raw_inputs/New Files' directory
and will output the processed data to the 'memory-bank/lore' directory.
"""

import os
import sys
import json
import re
import logging
from pathlib import Path
from collections import defaultdict

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

try:
    import ebooklib
    from ebooklib import epub
    from bs4 import BeautifulSoup
except ImportError:
    logger.error("Required libraries not found. Please install them using:")
    logger.error("pip install ebooklib beautifulsoup4")
    sys.exit(1)

# Constants
INPUT_DIR = Path("raw_inputs/New Files")
OUTPUT_DIR = Path("memory-bank/lore")
BOOKS = {
    "The Hobbit by J.R.R. Tolkien.epub": {
        "title": "The Hobbit",
        "short_name": "hobbit",
        "age": "third_age",
        "year": 2941,
        "characters": ["Bilbo", "Gandalf", "Thorin", "Smaug"],
        "locations": ["Erebor", "Mirkwood", "Rivendell", "Lonely Mountain"],
        "artifacts": ["Arkenstone", "Sting", "The One Ring"]
    },
    "The Lord of the Rings by J.R.R. Tolkien.epub": {
        "title": "The Lord of the Rings",
        "short_name": "lotr",
        "age": "third_age",
        "year": 3018,
        "characters": ["Frodo", "Gandalf", "Aragorn", "Sauron", "Gollum"],
        "locations": ["Mordor", "Gondor", "Rohan", "Shire", "Rivendell", "Moria"],
        "artifacts": ["The One Ring", "Andúril", "Palantír", "Phial of Galadriel"]
    },
    "The Silmarillion by J.R.R. Tolkien.epub": {
        "title": "The Silmarillion",
        "short_name": "silmarillion",
        "age": "first_age",
        "year": 1,
        "characters": ["Fëanor", "Morgoth", "Beren", "Lúthien", "Túrin", "Finrod"],
        "locations": ["Valinor", "Beleriand", "Gondolin", "Nargothrond", "Angband"],
        "artifacts": ["Silmarils", "Nauglamír", "Ring of Barahir", "Anglachel"]
    }
}

def clean_html_content(html_content):
    """
    Clean HTML content by removing HTML tags and normalizing whitespace.
    
    Args:
        html_content (str): HTML content to clean
        
    Returns:
        str: Cleaned text content
    """
    # Parse HTML with BeautifulSoup
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Remove script and style elements
    for script in soup(["script", "style"]):
        script.extract()
    
    # Get text content
    text = soup.get_text()
    
    # Normalize whitespace
    lines = (line.strip() for line in text.splitlines())
    chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
    text = '\n'.join(chunk for chunk in chunks if chunk)
    
    return text

def extract_epub_content(epub_path):
    """
    Extract content from an EPUB file.
    
    Args:
        epub_path (Path): Path to the EPUB file
        
    Returns:
        dict: Dictionary containing the book's content organized by chapters
    """
    logger.info(f"Extracting content from {epub_path}")
    
    try:
        # Read EPUB file
        book = epub.read_epub(str(epub_path))
        
        # Extract content
        chapters = []
        chapter_content = {}
        
        # Process each item in the book
        for item in book.get_items():
            if item.get_type() == ebooklib.ITEM_DOCUMENT:
                # Get content
                content = item.get_content().decode('utf-8')
                
                # Clean content
                text = clean_html_content(content)
                
                # Skip empty content
                if not text.strip():
                    continue
                
                # Extract chapter title (if available)
                soup = BeautifulSoup(content, 'html.parser')
                title_tag = soup.find(['h1', 'h2', 'h3'])
                title = title_tag.get_text().strip() if title_tag else f"Chapter {len(chapters) + 1}"
                
                # Add chapter
                chapters.append(title)
                chapter_content[title] = text
        
        return {
            "chapters": chapters,
            "content": chapter_content
        }
    
    except Exception as e:
        logger.error(f"Error extracting content from {epub_path}: {e}")
        return None

def process_book_for_memory_system(book_data, book_content, book_info):
    """
    Process book content for the memory system.
    
    Args:
        book_data (dict): Book metadata
        book_content (dict): Book content
        book_info (dict): Additional book information
        
    Returns:
        dict: Processed data for the memory system
    """
    # Initialize memory data
    memory_data = {
        "title": book_data["title"],
        "age": book_data["age"],
        "year": book_data["year"],
        "chapters": book_content["chapters"],
        "content": {},
        "entities": {
            "characters": defaultdict(list),
            "locations": defaultdict(list),
            "artifacts": defaultdict(list)
        }
    }
    
    # Process each chapter
    for chapter_title, chapter_text in book_content["content"].items():
        # Add chapter content
        memory_data["content"][chapter_title] = chapter_text
        
        # Extract entities
        for character in book_data["characters"]:
            if character in chapter_text:
                memory_data["entities"]["characters"][character].append(chapter_title)
        
        for location in book_data["locations"]:
            if location in chapter_text:
                memory_data["entities"]["locations"][location].append(chapter_title)
        
        for artifact in book_data["artifacts"]:
            if artifact in chapter_text:
                memory_data["entities"]["artifacts"][artifact].append(chapter_title)
    
    # Convert defaultdicts to regular dicts
    memory_data["entities"]["characters"] = dict(memory_data["entities"]["characters"])
    memory_data["entities"]["locations"] = dict(memory_data["entities"]["locations"])
    memory_data["entities"]["artifacts"] = dict(memory_data["entities"]["artifacts"])
    
    return memory_data

def create_lore_files(memory_data, book_data):
    """
    Create lore files for the memory system.
    
    Args:
        memory_data (dict): Processed memory data
        book_data (dict): Book metadata
        
    Returns:
        list: List of created file paths
    """
    created_files = []
    
    # Create age directory if it doesn't exist
    age_dir = OUTPUT_DIR / book_data["age"]
    age_dir.mkdir(parents=True, exist_ok=True)
    
    # Create book metadata file
    metadata_file = age_dir / f"{book_data['short_name']}_metadata.json"
    with open(metadata_file, 'w', encoding='utf-8') as f:
        json.dump({
            "title": memory_data["title"],
            "age": memory_data["age"],
            "year": memory_data["year"],
            "chapters": memory_data["chapters"],
            "entities": memory_data["entities"]
        }, f, indent=2)
    created_files.append(metadata_file)
    
    # Create chapter files
    chapters_dir = age_dir / f"{book_data['short_name']}_chapters"
    chapters_dir.mkdir(exist_ok=True)
    
    for chapter_title, chapter_text in memory_data["content"].items():
        # Create a safe filename
        safe_title = re.sub(r'[^\w\s-]', '', chapter_title).strip().lower()
        safe_title = re.sub(r'[-\s]+', '_', safe_title)
        
        chapter_file = chapters_dir / f"{safe_title}.md"
        with open(chapter_file, 'w', encoding='utf-8') as f:
            f.write(f"# {chapter_title}\n\n")
            f.write(chapter_text)
        created_files.append(chapter_file)
    
    # Create companion reference files
    for character in book_data["characters"]:
        if character in memory_data["entities"]["characters"]:
            character_file = age_dir / f"{book_data['short_name']}_{character.lower()}.md"
            with open(character_file, 'w', encoding='utf-8') as f:
                f.write(f"# {character} in {memory_data['title']}\n\n")
                f.write(f"## Appearances\n\n")
                
                for chapter in memory_data["entities"]["characters"][character]:
                    f.write(f"- {chapter}\n")
                
                f.write("\n## Notable Quotes and Descriptions\n\n")
                
                # Extract some quotes or descriptions
                for chapter in memory_data["entities"]["characters"][character][:3]:  # Limit to first 3 chapters
                    chapter_text = memory_data["content"][chapter]
                    
                    # Find sentences containing the character name
                    sentences = re.split(r'(?<=[.!?])\s+', chapter_text)
                    character_sentences = [s for s in sentences if character in s][:2]  # Limit to 2 sentences per chapter
                    
                    if character_sentences:
                        f.write(f"### From {chapter}\n\n")
                        for sentence in character_sentences:
                            f.write(f"> {sentence.strip()}\n\n")
            
            created_files.append(character_file)
    
    return created_files

def main():
    """Main function to process EPUB files for Angband."""
    logger.info("Starting EPUB processing for Angband memory system")
    
    # Check if input directory exists
    if not INPUT_DIR.exists():
        logger.error(f"Input directory '{INPUT_DIR}' not found")
        return False
    
    # Create output directory if it doesn't exist
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    # Process each book
    all_files_processed = True
    processed_files = []
    
    for filename, book_data in BOOKS.items():
        epub_path = INPUT_DIR / filename
        
        # Check if file exists
        if not epub_path.exists():
            logger.error(f"EPUB file '{filename}' not found in '{INPUT_DIR}'")
            all_files_processed = False
            continue
        
        # Extract content
        book_content = extract_epub_content(epub_path)
        if not book_content:
            all_files_processed = False
            continue
        
        # Process for memory system
        memory_data = process_book_for_memory_system(book_data, book_content, {})
        
        # Create lore files
        created_files = create_lore_files(memory_data, book_data)
        processed_files.extend(created_files)
        
        logger.info(f"Processed '{filename}' and created {len(created_files)} files")
    
    # Create index file
    index_file = OUTPUT_DIR / "lore_index.json"
    with open(index_file, 'w', encoding='utf-8') as f:
        index_data = {
            "books": {
                book_data["short_name"]: {
                    "title": book_data["title"],
                    "age": book_data["age"],
                    "year": book_data["year"],
                    "path": f"{book_data['age']}/{book_data['short_name']}_metadata.json"
                }
                for filename, book_data in BOOKS.items()
                if (INPUT_DIR / filename).exists()
            }
        }
        json.dump(index_data, f, indent=2)
    
    processed_files.append(index_file)
    
    # Create README file
    readme_file = OUTPUT_DIR / "README.md"
    with open(readme_file, 'w', encoding='utf-8') as f:
        f.write("# Lore Database for Ages of Arda\n\n")
        f.write("This directory contains lore extracted from Tolkien's works for use in the Ages of Arda companion system.\n\n")
        f.write("## Structure\n\n")
        f.write("- `lore_index.json`: Index of all books in the lore database\n")
        f.write("- `first_age/`: Lore from the First Age\n")
        f.write("- `second_age/`: Lore from the Second Age\n")
        f.write("- `third_age/`: Lore from the Third Age\n\n")
        f.write("## Books\n\n")
        
        for filename, book_data in BOOKS.items():
            if (INPUT_DIR / filename).exists():
                f.write(f"- {book_data['title']} ({book_data['age'].replace('_', ' ').title()}, Year {book_data['year']})\n")
    
    processed_files.append(readme_file)
    
    # Print summary
    logger.info(f"Processing complete. Created {len(processed_files)} files.")
    logger.info(f"Output directory: {OUTPUT_DIR.absolute()}")
    
    if all_files_processed:
        logger.info("All files processed successfully")
    else:
        logger.warning("Some files could not be processed. Check the log for details.")
    
    return all_files_processed

if __name__ == "__main__":
    main() 