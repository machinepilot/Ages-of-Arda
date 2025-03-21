"""
Mock Entity Extractor for Ages of Arda

This module provides a mock implementation of the entity extractor
for testing purposes without requiring external dependencies.
"""

import os
import json
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from collections import defaultdict

# Import the path configuration
from processing.path_config import get_log_file_path

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(get_log_file_path('mock_entity_extractor')),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('mock_entity_extractor')

class OllamaClient:
    """
    Mock client for simulating the Ollama API.
    """
    
    def __init__(self, base_url="http://localhost:11434", model="llama3"):
        """
        Initialize the mock Ollama client.
        
        Args:
            base_url (str): Base URL for Ollama API (not used in mock)
            model (str): Default model to use (not used in mock)
        """
        self.base_url = base_url
        self.model = model
        logger.info(f"Initialized mock OllamaClient with model {model}")
    
    def generate(self, prompt, system=None, model=None, max_tokens=None):
        """
        Generate mock text response.
        
        Args:
            prompt (str): The prompt (used to determine mock response)
            system (str, optional): System message (not used in mock)
            model (str, optional): Model to use (not used in mock)
            max_tokens (int, optional): Maximum tokens (not used in mock)
            
        Returns:
            str: Mock generated text based on prompt content
        """
        logger.info(f"Mock generating text for prompt: {prompt[:50]}...")
        
        # Always return some entities for testing purposes
        return json.dumps({
            "entities": [
                {
                    "name": "Frodo Baggins",
                    "type": "CHARACTER",
                    "subtype": "HOBBIT",
                    "confidence": 0.95,
                    "context": "Frodo Baggins lived in Bag End."
                },
                {
                    "name": "Gandalf",
                    "type": "CHARACTER",
                    "subtype": "MAIAR",
                    "confidence": 0.98,
                    "context": "Gandalf visited him in the Shire."
                },
                {
                    "name": "Bag End",
                    "type": "LOCATION",
                    "subtype": "STRUCTURE",
                    "confidence": 0.9,
                    "context": "Frodo Baggins lived in Bag End."
                },
                {
                    "name": "Shire",
                    "type": "LOCATION",
                    "subtype": "REGION",
                    "confidence": 0.92,
                    "context": "Gandalf visited him in the Shire."
                }
            ]
        })
    
    def is_available(self):
        """
        Check if Ollama is available (mock always returns True).
        
        Returns:
            bool: Always True in mock implementation
        """
        return True


class EntityStore:
    """
    Mock store for managing entity data.
    """
    
    def __init__(self, storage_dir):
        """
        Initialize the mock entity store.
        
        Args:
            storage_dir (str): Directory to store entities (created in mock)
        """
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        self.entities = defaultdict(list)
        logger.info(f"Initialized mock EntityStore at {storage_dir}")
    
    def add_entity(self, entity):
        """
        Add an entity to the mock store.
        
        Args:
            entity (dict): Entity to add
            
        Returns:
            str: ID of the added entity
        """
        entity_type = entity.get("type", "UNKNOWN")
        entity_id = entity.get("id", f"{entity_type.lower()}_{len(self.entities[entity_type])}")
        
        # Ensure entity has an ID
        if "id" not in entity:
            entity["id"] = entity_id
            
        self.entities[entity_type].append(entity)
        
        # Write to disk to simulate persistent storage
        type_dir = self.storage_dir / entity_type.lower()
        type_dir.mkdir(exist_ok=True)
        
        with open(type_dir / f"{entity_id}.json", 'w') as f:
            json.dump(entity, f, indent=2)
            
        logger.info(f"Added entity {entity_id} of type {entity_type}")
        return entity_id
    
    def get_entity(self, entity_id, entity_type=None):
        """
        Get an entity from the mock store.
        
        Args:
            entity_id (str): ID of the entity to retrieve
            entity_type (str, optional): Type of the entity
            
        Returns:
            dict: The entity if found, None otherwise
        """
        if entity_type:
            for entity in self.entities[entity_type]:
                if entity.get("id") == entity_id:
                    return entity
        else:
            for entity_list in self.entities.values():
                for entity in entity_list:
                    if entity.get("id") == entity_id:
                        return entity
        return None
    
    def get_entities_by_type(self, entity_type):
        """
        Get all entities of a specific type.
        
        Args:
            entity_type (str): Type of entities to retrieve
            
        Returns:
            list: List of entities of the specified type
        """
        return self.entities[entity_type]
    
    def get_all_entities(self):
        """
        Get all entities in the store.
        
        Returns:
            dict: Dictionary mapping entity types to lists of entities
        """
        return dict(self.entities)


class EntityExtractor:
    """
    Mock implementation of the entity extractor.
    """
    
    def __init__(self, output_dir, ollama_url="http://localhost:11434", ollama_model="llama3"):
        """
        Initialize the mock entity extractor.
        
        Args:
            output_dir (str): Directory to store extracted entities
            ollama_url (str, optional): URL for Ollama API (not used in mock)
            ollama_model (str, optional): Model to use (not used in mock)
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.ollama_client = OllamaClient(ollama_url, ollama_model)
        self.entity_store = EntityStore(self.output_dir / "entities")
        logger.info(f"Initialized mock EntityExtractor with output directory {output_dir}")
    
    def extract_entities_from_chapter(self, chapter):
        """
        Extract entities from a chapter (mock implementation).
        
        Args:
            chapter (dict): Chapter data with content
            
        Returns:
            list: List of extracted entities
        """
        content = chapter.get("content", "")
        title = chapter.get("title", "Unknown Chapter")
        metadata = chapter.get("metadata", {})
        
        logger.info(f"Extracting entities from chapter: {title}")
        
        # Create a prompt with the chapter content (just for logging in mock)
        prompt = f"Extract all Tolkien entities from the following text:\n\n{content[:500]}..."
        
        # Get mock entities based on content
        response = self.ollama_client.generate(prompt)
        try:
            result = json.loads(response)
            entities = result.get("entities", [])
        except json.JSONDecodeError:
            logger.error(f"Error parsing mock response: {response}")
            entities = []
        
        # Process entities
        processed_entities = []
        for entity in entities:
            # Create a full entity record
            entity_record = {
                "id": f"{entity['type'].lower()}_{entity['name'].lower().replace(' ', '_')}",
                "name": entity["name"],
                "type": entity["type"],
                "subtype": entity.get("subtype", ""),
                "confidence": entity.get("confidence", 0.8),
                "sources": [{
                    "book": metadata.get("book", "Unknown Book"),
                    "chapter": title,
                    "context": entity.get("context", ""),
                    "age": metadata.get("age", "Unknown Age")
                }],
                "attributes": {}
            }
            
            # Add to store and processed list
            self.entity_store.add_entity(entity_record)
            processed_entities.append(entity_record)
        
        return processed_entities
    
    def process_chapters(self, chapters_dir):
        """
        Process all chapters in a directory (mock implementation).
        
        Args:
            chapters_dir (str): Directory containing chapter files
            
        Returns:
            dict: Statistics about the extraction process
        """
        chapters_path = Path(chapters_dir)
        stats = {
            "processed_chapters": 0,
            "extracted_entities": 0,
            "entity_types": defaultdict(int)
        }
        
        if not chapters_path.exists():
            logger.error(f"Chapters directory not found: {chapters_dir}")
            return stats
        
        for chapter_file in chapters_path.glob("*.json"):
            try:
                with open(chapter_file) as f:
                    chapter = json.load(f)
                
                entities = self.extract_entities_from_chapter(chapter)
                
                stats["processed_chapters"] += 1
                stats["extracted_entities"] += len(entities)
                
                for entity in entities:
                    stats["entity_types"][entity["type"]] += 1
                    
            except Exception as e:
                logger.error(f"Error processing chapter {chapter_file}: {str(e)}")
        
        logger.info(f"Processed {stats['processed_chapters']} chapters, extracted {stats['extracted_entities']} entities")
        return stats 