"""
Entity Extractor for Ages of Arda

This module provides functionality for extracting entities from text content
using the Ollama API to access local Language Models.
"""

import os
import json
import logging
import requests
import time
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join('processing', 'logs', 'entity_extraction.log')),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('entity_extractor')

class OllamaClient:
    """
    Client for interacting with the Ollama API.
    """
    
    def __init__(self, base_url="http://localhost:11434", model="llama3"):
        """
        Initialize the Ollama client.
        
        Args:
            base_url (str): Base URL for Ollama API
            model (str): Default model to use
        """
        self.base_url = base_url
        self.model = model
    
    def generate(self, prompt, system=None, model=None, max_tokens=None):
        """
        Generate text using the Ollama API.
        
        Args:
            prompt (str): The prompt to send to the model
            system (str, optional): System message to set context
            model (str, optional): Model to use (defaults to self.model)
            max_tokens (int, optional): Maximum tokens to generate
            
        Returns:
            str: Generated text
        """
        model = model or self.model
        url = f"{self.base_url}/api/generate"
        
        payload = {
            "model": model,
            "prompt": prompt,
            "stream": False
        }
        
        if system:
            payload["system"] = system
        
        if max_tokens:
            payload["options"] = {"num_predict": max_tokens}
        
        try:
            response = requests.post(url, json=payload)
            response.raise_for_status()
            return response.json().get('response', '')
        except requests.exceptions.RequestException as e:
            logger.error(f"Error calling Ollama API: {str(e)}")
            return ""
    
    def is_available(self):
        """
        Check if Ollama is available.
        
        Returns:
            bool: True if Ollama is available, False otherwise
        """
        try:
            response = requests.get(f"{self.base_url}/api/tags")
            return response.status_code == 200
        except requests.exceptions.RequestException:
            return False


class EntityExtractor:
    """
    Extractor for identifying and extracting entities from text.
    """
    
    def __init__(self, output_dir, ollama_client=None):
        """
        Initialize the entity extractor.
        
        Args:
            output_dir (str): Directory to save extracted entities
            ollama_client (OllamaClient, optional): Ollama client instance
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize Ollama client
        self.ollama = ollama_client or OllamaClient()
        
        # Check if Ollama is available
        if not self.ollama.is_available():
            logger.warning("Ollama is not available. Make sure the Ollama server is running.")
    
    def extract_entities_from_text(self, text, text_metadata=None, entity_types=None):
        """
        Extract entities from text using Ollama.
        
        Args:
            text (str): Text to extract entities from
            text_metadata (dict, optional): Metadata about the text (book, chapter, etc.)
            entity_types (list, optional): Types of entities to extract
            
        Returns:
            dict: Dictionary of extracted entities by type
        """
        if not text.strip():
            logger.warning("Empty text provided for entity extraction")
            return {}
        
        # Default entity types to extract
        entity_types = entity_types or ["character", "location", "item", "event"]
        
        # Create prompt for entity extraction
        prompt = self._create_entity_extraction_prompt(text, text_metadata, entity_types)
        
        # Set system message for context
        system_message = """You are an expert in J.R.R. Tolkien's works, specializing in extracting named entities from text. Extract only entities that are explicitly mentioned in the provided text. Do not infer or add entities that aren't directly referenced."""
        
        # Generate response from Ollama
        max_retries = 3
        for attempt in range(max_retries):
            try:
                response = self.ollama.generate(prompt, system=system_message, max_tokens=2000)
                
                # Try to parse the JSON response
                entities = self._parse_entity_response(response)
                
                if entities:
                    logger.info(f"Extracted {sum(len(entities.get(t, [])) for t in entities)} entities from text")
                    return entities
                
                logger.warning(f"Failed to parse entity response (attempt {attempt+1}/{max_retries})")
                time.sleep(2)  # Wait before retry
                
            except Exception as e:
                logger.error(f"Error extracting entities (attempt {attempt+1}/{max_retries}): {str(e)}")
                time.sleep(2)  # Wait before retry
        
        logger.error("Failed to extract entities after multiple attempts")
        return {}
    
    def _create_entity_extraction_prompt(self, text, text_metadata=None, entity_types=None):
        """
        Create a prompt for entity extraction.
        
        Args:
            text (str): Text to extract entities from
            text_metadata (dict, optional): Metadata about the text
            entity_types (list, optional): Types of entities to extract
            
        Returns:
            str: Formatted prompt
        """
        # Construct metadata context
        metadata_context = ""
        if text_metadata:
            metadata_context = "Context information:\n"
            for key, value in text_metadata.items():
                metadata_context += f"- {key}: {value}\n"
        
        # Construct entity type instructions
        entity_type_instructions = "Extract the following types of entities:\n"
        entity_descriptions = {
            "character": "Characters (people, beings, creatures)",
            "location": "Locations (places, regions, landmarks)",
            "item": "Items (objects, artifacts, weapons)",
            "event": "Events (battles, councils, journeys)",
            "culture": "Cultures (groups, races, peoples)"
        }
        
        for entity_type in entity_types:
            description = entity_descriptions.get(entity_type, entity_type.capitalize())
            entity_type_instructions += f"- {description}\n"
        
        # Construct the full prompt
        prompt = f"""
{metadata_context}

{entity_type_instructions}

For each entity, provide the following information:
1. Name: The primary name of the entity
2. Type: The type of entity (character, location, item, event)
3. Description: A brief description based ONLY on information in this text
4. Mentions: All variants of the name used in the text
5. Related: Other entities that are directly related to this entity in the text

Format your response as JSON like this:
```json
{{
  "characters": [
    {{
      "name": "Gandalf",
      "type": "character",
      "description": "A wizard who guides the company",
      "mentions": ["Gandalf", "Mithrandir", "the Grey Pilgrim"],
      "related": ["Bilbo", "Thorin"]
    }}
  ],
  "locations": [
    {{
      "name": "Rivendell",
      "type": "location",
      "description": "An elven refuge where the company rests",
      "mentions": ["Rivendell", "the Last Homely House"],
      "related": ["Elrond"]
    }}
  ]
}}
```

TEXT TO ANALYZE:
{text}

JSON RESPONSE:
"""
        
        return prompt
    
    def _parse_entity_response(self, response):
        """
        Parse the entity extraction response.
        
        Args:
            response (str): Response from Ollama
            
        Returns:
            dict: Dictionary of extracted entities
        """
        try:
            # Try to find JSON in the response
            json_start = response.find('{')
            json_end = response.rfind('}') + 1
            
            if json_start == -1 or json_end == 0:
                logger.warning("No JSON found in response")
                return {}
            
            json_text = response[json_start:json_end]
            
            # Parse the JSON
            entities = json.loads(json_text)
            
            # Validate structure
            if not isinstance(entities, dict):
                logger.warning("Response is not a dictionary")
                return {}
            
            # Return the parsed entities
            return entities
            
        except json.JSONDecodeError as e:
            logger.error(f"Error parsing JSON response: {str(e)}")
            logger.debug(f"Response: {response}")
            return {}
        except Exception as e:
            logger.error(f"Unexpected error parsing response: {str(e)}")
            return {}
    
    def process_chapter(self, chapter_file):
        """
        Process a single chapter file for entity extraction.
        
        Args:
            chapter_file (str): Path to chapter JSON file
            
        Returns:
            dict: Extracted entities
        """
        try:
            # Load chapter data
            with open(chapter_file, 'r', encoding='utf-8') as f:
                chapter_data = json.load(f)
            
            # Extract text content
            text = chapter_data.get('content', '')
            
            # Prepare metadata
            metadata = {
                'book_id': chapter_data.get('book_id', 'unknown'),
                'age': chapter_data.get('age', 'unknown'),
                'chapter_title': chapter_data.get('chapter_title', 'Unknown Chapter'),
                'chapter_number': chapter_data.get('chapter_number', 0)
            }
            
            # Extract entities
            entities = self.extract_entities_from_text(text, metadata)
            
            # Save extracted entities
            output_file = self.output_dir / f"{os.path.basename(chapter_file).replace('.json', '_entities.json')}"
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump({
                    'metadata': metadata,
                    'entities': entities
                }, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Saved entities for {metadata['chapter_title']} to {output_file}")
            
            return entities
            
        except Exception as e:
            logger.error(f"Error processing chapter {chapter_file}: {str(e)}")
            return {}
    
    def process_book(self, book_dir):
        """
        Process all chapters in a book directory.
        
        Args:
            book_dir (str): Path to book directory
            
        Returns:
            dict: Book-level entity statistics
        """
        book_dir = Path(book_dir)
        logger.info(f"Processing book in {book_dir}")
        
        # Find all chapter files
        chapter_files = list(book_dir.glob('chapter_*.json'))
        chapter_files.sort()  # Sort to process in order
        
        if not chapter_files:
            logger.warning(f"No chapter files found in {book_dir}")
            return {}
        
        # Process each chapter
        all_entities = {}
        entities_by_chapter = {}
        
        for chapter_file in chapter_files:
            logger.info(f"Processing chapter {chapter_file.name}")
            
            # Extract entities from this chapter
            chapter_entities = self.process_chapter(chapter_file)
            
            # Store by chapter
            entities_by_chapter[chapter_file.name] = chapter_entities
            
            # Aggregate entities
            for entity_type, entities in chapter_entities.items():
                if entity_type not in all_entities:
                    all_entities[entity_type] = []
                
                all_entities[entity_type].extend(entities)
        
        # Find book metadata
        metadata_file = book_dir / "metadata.json"
        book_metadata = {}
        
        if metadata_file.exists():
            try:
                with open(metadata_file, 'r', encoding='utf-8') as f:
                    book_metadata = json.load(f)
            except Exception as e:
                logger.error(f"Error reading book metadata: {str(e)}")
        
        # Save book-level entity summary
        book_summary = {
            'metadata': book_metadata,
            'entity_counts': {entity_type: len(entities) for entity_type, entities in all_entities.items()},
            'total_entities': sum(len(entities) for entities in all_entities.values()),
            'entities_by_type': all_entities
        }
        
        summary_file = self.output_dir / f"{book_dir.name}_entity_summary.json"
        with open(summary_file, 'w', encoding='utf-8') as f:
            json.dump(book_summary, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Saved book entity summary to {summary_file}")
        
        return book_summary
    
    def process_all_books(self, epub_content_dir):
        """
        Process all books in the ePub content directory.
        
        Args:
            epub_content_dir (str): Path to ePub content directory
            
        Returns:
            dict: Processing results
        """
        epub_content_dir = Path(epub_content_dir)
        logger.info(f"Processing all books in {epub_content_dir}")
        
        # Find all book directories
        book_dirs = [d for d in epub_content_dir.glob('*') if d.is_dir()]
        
        if not book_dirs:
            logger.warning(f"No book directories found in {epub_content_dir}")
            return {}
        
        # Process each book
        results = {
            'processed_books': [],
            'failed_books': [],
            'total_entities': 0,
            'entity_counts': {}
        }
        
        for book_dir in book_dirs:
            try:
                logger.info(f"Processing book: {book_dir.name}")
                book_summary = self.process_book(book_dir)
                
                if book_summary:
                    results['processed_books'].append(book_dir.name)
                    
                    # Aggregate entity counts
                    for entity_type, count in book_summary.get('entity_counts', {}).items():
                        if entity_type not in results['entity_counts']:
                            results['entity_counts'][entity_type] = 0
                        results['entity_counts'][entity_type] += count
                    
                    results['total_entities'] += book_summary.get('total_entities', 0)
                else:
                    results['failed_books'].append(book_dir.name)
                    
            except Exception as e:
                logger.error(f"Error processing book {book_dir.name}: {str(e)}")
                results['failed_books'].append(book_dir.name)
        
        # Save overall results
        results_file = self.output_dir / "entity_extraction_results.json"
        with open(results_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2)
        
        logger.info(f"Entity extraction complete. Extracted {results['total_entities']} entities from {len(results['processed_books'])} books.")
        logger.info(f"Entity counts by type: {results['entity_counts']}")
        
        return results


def extract_entities(epub_content_dir, output_dir):
    """
    Extract entities from all books in the ePub content directory.
    
    Args:
        epub_content_dir (str): Directory containing processed ePub content
        output_dir (str): Directory to save extracted entities
        
    Returns:
        dict: Processing results
    """
    # Initialize entity extractor
    extractor = EntityExtractor(output_dir)
    
    # Process all books
    return extractor.process_all_books(epub_content_dir)


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Extract entities from processed ePub content")
    parser.add_argument("--input-dir", default="processing/epub_content", help="Input directory containing processed ePub content")
    parser.add_argument("--output-dir", default="processing/json_output", help="Output directory for extracted entities")
    args = parser.parse_args()
    
    extract_entities(args.input_dir, args.output_dir) 