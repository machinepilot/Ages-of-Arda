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
import re
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from collections import defaultdict

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


class EntityStore:
    """
    Store for managing entity data without using a database.
    Implements basic database-like functionality using file system.
    """
    
    def __init__(self, storage_dir):
        """
        Initialize the entity store.
        
        Args:
            storage_dir (str): Directory to store entity data
        """
        self.storage_dir = Path(storage_dir) / "entity_store"
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        
        # Create subdirectories for different entity types
        for entity_type in ["character", "location", "item", "event", "culture"]:
            (self.storage_dir / entity_type).mkdir(exist_ok=True)
        
        # Load reference entity lists
        self.reference_entities = self._load_reference_entities()
        
        # Initialize relationships store
        self.relationships_dir = self.storage_dir / "relationships"
        self.relationships_dir.mkdir(exist_ok=True)
    
    def _load_reference_entities(self) -> Dict[str, List[Dict]]:
        """
        Load reference entity lists from schema files.
        
        Returns:
            Dict[str, List[Dict]]: Dictionary of reference entities by type
        """
        reference_entities = {}
        schema_dir = Path("processing/schemas/entity_lists")
        
        if not schema_dir.exists():
            logger.warning(f"Reference entity schema directory not found: {schema_dir}")
            return {}
        
        # Load each entity type file if available
        for entity_file in ["characters.json", "locations.json", "items.json"]:
            file_path = schema_dir / entity_file
            
            if file_path.exists():
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        
                    # Extract entity type from filename
                    entity_type = os.path.splitext(entity_file)[0]
                    if entity_type.endswith('s'):  # Remove plural
                        entity_type = entity_type[:-1]
                    
                    # Store entities with their alternate names for easy lookup
                    reference_entities[entity_type] = data.get(entity_type + "s", [])
                    
                    logger.info(f"Loaded {len(reference_entities[entity_type])} reference {entity_type} entities")
                    
                except Exception as e:
                    logger.error(f"Error loading reference entities from {file_path}: {str(e)}")
        
        return reference_entities
    
    def store_entity(self, entity: Dict[str, Any], source_info: Dict[str, Any]) -> str:
        """
        Store an entity in the file system.
        
        Args:
            entity (Dict[str, Any]): Entity data
            source_info (Dict[str, Any]): Source information
            
        Returns:
            str: Entity ID
        """
        entity_type = entity.get("type", "unknown").lower()
        entity_name = entity.get("name", "unnamed")
        
        # Generate a unique ID for the entity
        entity_id = self._generate_entity_id(entity_type, entity_name)
        
        # Add source information
        if "sources" not in entity:
            entity["sources"] = []
        
        entity["sources"].append(source_info)
        
        # Store entity in appropriate directory
        entity_dir = self.storage_dir / entity_type
        entity_file = entity_dir / f"{entity_id}.json"
        
        with open(entity_file, 'w', encoding='utf-8') as f:
            json.dump(entity, f, indent=2, ensure_ascii=False)
        
        return entity_id
    
    def _generate_entity_id(self, entity_type: str, entity_name: str) -> str:
        """
        Generate a unique ID for an entity.
        
        Args:
            entity_type (str): Entity type
            entity_name (str): Entity name
            
        Returns:
            str: Entity ID
        """
        # Clean the name for use in filenames
        clean_name = re.sub(r'[^a-zA-Z0-9]', '_', entity_name).lower()
        clean_name = re.sub(r'_+', '_', clean_name)  # Replace multiple underscores with single
        
        # Truncate if needed
        if len(clean_name) > 50:
            clean_name = clean_name[:50]
        
        # Add timestamp to ensure uniqueness
        timestamp = int(time.time())
        
        return f"{clean_name}_{timestamp}"
    
    def store_relationship(self, entity_id1: str, entity_id2: str, relationship_type: str, 
                          confidence: float, source_info: Dict[str, Any]) -> None:
        """
        Store a relationship between two entities.
        
        Args:
            entity_id1 (str): First entity ID
            entity_id2 (str): Second entity ID
            relationship_type (str): Type of relationship
            confidence (float): Confidence score for the relationship
            source_info (Dict[str, Any]): Source information
        """
        # Create a unique ID for the relationship
        rel_id = f"{entity_id1}_{entity_id2}_{relationship_type}"
        rel_id = re.sub(r'[^a-zA-Z0-9]', '_', rel_id)
        
        relationship = {
            "entity1": entity_id1,
            "entity2": entity_id2,
            "type": relationship_type,
            "confidence": confidence,
            "source": source_info
        }
        
        # Store relationship
        rel_file = self.relationships_dir / f"{rel_id}.json"
        
        with open(rel_file, 'w', encoding='utf-8') as f:
            json.dump(relationship, f, indent=2, ensure_ascii=False)
    
    def get_entity_by_name(self, name: str, entity_type: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        Find an entity by name.
        
        Args:
            name (str): Entity name
            entity_type (str, optional): Entity type to limit search
            
        Returns:
            Optional[Dict[str, Any]]: Entity data or None if not found
        """
        # First check reference entities
        for ref_type, entities in self.reference_entities.items():
            if entity_type and entity_type.lower() != ref_type.lower():
                continue
                
            for entity in entities:
                if entity["name"].lower() == name.lower():
                    return entity
                
                # Check alternate names
                alt_names = entity.get("alternate_names", [])
                if any(alt.lower() == name.lower() for alt in alt_names):
                    return entity
        
        # Then check stored entities
        search_dirs = []
        if entity_type:
            type_dir = self.storage_dir / entity_type.lower()
            if type_dir.exists():
                search_dirs.append(type_dir)
        else:
            for subdir in self.storage_dir.iterdir():
                if subdir.is_dir() and subdir.name != "relationships":
                    search_dirs.append(subdir)
        
        for directory in search_dirs:
            for entity_file in directory.glob("*.json"):
                try:
                    with open(entity_file, 'r', encoding='utf-8') as f:
                        entity = json.load(f)
                    
                    if entity.get("name", "").lower() == name.lower():
                        return entity
                    
                    # Check alternate names
                    alt_names = entity.get("mentions", []) + entity.get("alternate_names", [])
                    if any(alt.lower() == name.lower() for alt in alt_names):
                        return entity
                        
                except Exception as e:
                    logger.error(f"Error reading entity file {entity_file}: {str(e)}")
        
        return None
    
    def infer_entity_type(self, entity_name: str, context: str) -> Tuple[str, float]:
        """
        Infer the entity type based on context and reference data.
        
        Args:
            entity_name (str): Name of the entity
            context (str): Text context where the entity appears
            
        Returns:
            Tuple[str, float]: Inferred entity type and confidence score
        """
        # First check if entity exists in reference data
        for entity_type, entities in self.reference_entities.items():
            for entity in entities:
                if entity["name"].lower() == entity_name.lower():
                    return entity_type, 1.0
                
                # Check alternate names
                alt_names = entity.get("alternate_names", [])
                if any(alt.lower() == entity_name.lower() for alt in alt_names):
                    return entity_type, 1.0
        
        # Context-based inference patterns
        type_patterns = {
            "character": [
                r"(?:he|she|they|his|her|their|him|himself|herself|themself)",
                r"(?:spoke|said|asked|replied|thought|felt|knew|believed)",
                r"(?:son of|daughter of|father of|mother of|brother|sister|king|queen|lord|lady)"
            ],
            "location": [
                r"(?:in|at|to|from|near|within|outside|beyond)",
                r"(?:land|realm|kingdom|city|town|forest|mountain|river|place|region)"
            ],
            "item": [
                r"(?:sword|ring|artifact|weapon|item|object|tool|armor|jewel|crown)",
                r"(?:forged|made|crafted|created|wielded|carried|wore|bearing)"
            ],
            "event": [
                r"(?:battle|war|council|meeting|journey|quest|celebration|ceremony)",
                r"(?:occurred|happened|took place|began|ended|during)"
            ]
        }
        
        # Count matches for each type pattern
        scores = {entity_type: 0 for entity_type in type_patterns}
        
        # Get a window of text around the entity mention for better context
        entity_pattern = re.escape(entity_name)
        context_window_match = re.search(r'.{0,200}' + entity_pattern + r'.{0,200}', context, re.IGNORECASE)
        
        if context_window_match:
            narrow_context = context_window_match.group(0)
            
            for entity_type, patterns in type_patterns.items():
                for pattern in patterns:
                    matches = re.findall(pattern, narrow_context, re.IGNORECASE)
                    scores[entity_type] += len(matches)
        
        # Find the type with the highest score
        if not any(scores.values()):
            return "unknown", 0.0
            
        max_score = max(scores.values())
        best_type = max(scores.items(), key=lambda x: x[1])[0]
        
        # Calculate confidence
        total_score = sum(scores.values())
        confidence = max_score / total_score if total_score > 0 else 0.0
        
        return best_type, confidence


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
            
        # Initialize entity store
        self.entity_store = EntityStore(output_dir)
    
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
                    
                    # Process entities for storage and relationship extraction
                    self._process_extracted_entities(entities, text, text_metadata)
                    
                    return entities
                
                logger.warning(f"Failed to parse entity response (attempt {attempt+1}/{max_retries})")
                time.sleep(2)  # Wait before retry
                
            except Exception as e:
                logger.error(f"Error extracting entities (attempt {attempt+1}/{max_retries}): {str(e)}")
                time.sleep(2)  # Wait before retry
        
        logger.error("Failed to extract entities after multiple attempts")
        return {}
    
    def _process_extracted_entities(self, entities, text, text_metadata):
        """
        Process extracted entities for storage and relationship extraction.
        
        Args:
            entities (dict): Extracted entities by type
            text (str): Source text
            text_metadata (dict): Metadata about the text
        """
        source_info = {
            "book_id": text_metadata.get("book_id", "unknown"),
            "chapter_title": text_metadata.get("chapter_title", "unknown"),
            "chapter_number": text_metadata.get("chapter_number", 0),
            "age": text_metadata.get("age", "unknown")
        }
        
        # Flatten entity list
        all_entities = []
        for entity_type, entity_list in entities.items():
            for entity in entity_list:
                entity_with_type = entity.copy()
                
                # Normalize type name (remove plural if present)
                if entity_type.endswith('s'):
                    entity_type = entity_type[:-1]
                
                entity_with_type["category"] = entity_type.upper()
                all_entities.append(entity_with_type)
        
        # Extract and store entities
        stored_entities = {}
        for entity in all_entities:
            entity_name = entity.get("name")
            
            # Infer entity type if not already known
            if "type" not in entity or entity["type"] == "unknown":
                inferred_type, confidence = self.entity_store.infer_entity_type(entity_name, text)
                entity["type"] = inferred_type
                entity["type_confidence"] = confidence
            
            # Store entity
            entity_id = self.entity_store.store_entity(entity, source_info)
            stored_entities[entity_name] = entity_id
            
            # Store alternate names/mentions
            mentions = entity.get("mentions", [])
            for mention in mentions:
                if mention != entity_name:
                    self.entity_store.store_relationship(
                        entity_id,
                        entity_id,  # Self-reference for alternate name
                        "alternate_name",
                        1.0,
                        source_info
                    )
        
        # Extract relationships between entities
        self._extract_relationships(all_entities, stored_entities, text, source_info)
    
    def _extract_relationships(self, entities, entity_ids, text, source_info):
        """
        Extract relationships between entities.
        
        Args:
            entities (list): List of entities
            entity_ids (dict): Dictionary of entity names to IDs
            text (str): Source text
            source_info (dict): Source information
        """
        # Create a graph of entity co-occurrences
        co_occurrences = defaultdict(lambda: defaultdict(int))
        
        for i, entity1 in enumerate(entities):
            name1 = entity1.get("name")
            
            # Skip if missing required data
            if not name1 or name1 not in entity_ids:
                continue
                
            # Check explicitly mentioned relationships
            related = entity1.get("related", [])
            for related_name in related:
                # Skip if missing required data
                if not related_name or related_name not in entity_ids:
                    continue
                    
                if name1 != related_name:  # Avoid self-relationships
                    co_occurrences[name1][related_name] += 5  # Higher weight for explicit relationships
            
            # Check for co-occurrence in same context window
            for j, entity2 in enumerate(entities):
                if i == j:
                    continue
                    
                name2 = entity2.get("name")
                
                # Skip if missing required data
                if not name2 or name2 not in entity_ids:
                    continue
                
                # Check for presence in same paragraph/context
                if self._are_in_same_context(name1, name2, text):
                    co_occurrences[name1][name2] += 1
        
        # Store relationships with confidence scores
        for name1, related_entities in co_occurrences.items():
            total_occurrences = sum(related_entities.values())
            
            for name2, count in related_entities.items():
                confidence = min(1.0, count / 10)  # Scale confidence, max at 1.0
                
                # Infer relationship type based on entity types
                entity1 = self.entity_store.get_entity_by_name(name1)
                entity2 = self.entity_store.get_entity_by_name(name2)
                
                if entity1 and entity2:
                    relationship_type = self._infer_relationship_type(entity1, entity2, text)
                else:
                    relationship_type = "related"
                
                # Store the relationship
                self.entity_store.store_relationship(
                    entity_ids[name1],
                    entity_ids[name2],
                    relationship_type,
                    confidence,
                    source_info
                )
    
    def _are_in_same_context(self, name1, name2, text, context_window=500):
        """
        Check if two entity names appear in the same context window.
        
        Args:
            name1 (str): First entity name
            name2 (str): Second entity name
            text (str): Source text
            context_window (int): Size of context window in characters
            
        Returns:
            bool: True if entities appear in same context window
        """
        # Find all occurrences of first name
        name1_positions = [m.start() for m in re.finditer(re.escape(name1), text)]
        
        # Find all occurrences of second name
        name2_positions = [m.start() for m in re.finditer(re.escape(name2), text)]
        
        # Check if any occurrences are within the context window
        for pos1 in name1_positions:
            start = max(0, pos1 - context_window // 2)
            end = min(len(text), pos1 + context_window // 2)
            
            for pos2 in name2_positions:
                if start <= pos2 <= end:
                    return True
        
        return False
    
    def _infer_relationship_type(self, entity1, entity2, text):
        """
        Infer the relationship type between two entities.
        
        Args:
            entity1 (dict): First entity
            entity2 (dict): Second entity
            text (str): Source text
            
        Returns:
            str: Inferred relationship type
        """
        type1 = entity1.get("type", "").lower()
        type2 = entity2.get("type", "").lower()
        
        # Define relationship mapping based on entity types
        relationship_map = {
            ("character", "character"): "associated_with",
            ("character", "location"): "located_at",
            ("location", "character"): "contains",
            ("character", "item"): "possesses",
            ("item", "character"): "possessed_by",
            ("character", "event"): "participated_in",
            ("event", "character"): "involved",
            ("location", "location"): "connected_to",
            ("location", "event"): "setting_for",
            ("event", "location"): "occurred_at",
            ("item", "item"): "related_to",
            ("item", "location"): "located_at",
            ("location", "item"): "contains",
            ("event", "event"): "related_to",
            ("item", "event"): "used_in",
            ("event", "item"): "featured"
        }
        
        # Get default relationship type
        default_relationship = "related_to"
        
        # Look up in the map
        relationship_type = relationship_map.get((type1, type2), default_relationship)
        
        return relationship_type
    
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
        
        # Export entities to JSON files organized by entity type and book
        self._export_entities_to_json(results)
        
        return results
    
    def _export_entities_to_json(self, results):
        """
        Export all entities to JSON files organized by type.
        
        Args:
            results (dict): Processing results
        """
        # Create export directory
        export_dir = self.output_dir / "exports"
        export_dir.mkdir(exist_ok=True)
        
        # Create a directory for each entity type
        entity_types = list(results.get('entity_counts', {}).keys())
        
        for entity_type in entity_types:
            type_dir = export_dir / entity_type
            type_dir.mkdir(exist_ok=True)
            
            # Collect all entities of this type
            entities = []
            
            # Search through entity store for this type
            store_dir = self.entity_store.storage_dir / entity_type.lower()
            if store_dir.exists():
                for entity_file in store_dir.glob("*.json"):
                    try:
                        with open(entity_file, 'r', encoding='utf-8') as f:
                            entity = json.load(f)
                            entities.append(entity)
                    except Exception as e:
                        logger.error(f"Error reading entity file {entity_file}: {str(e)}")
            
            # Export all entities of this type
            if entities:
                export_file = export_dir / f"{entity_type}_entities.json"
                with open(export_file, 'w', encoding='utf-8') as f:
                    json.dump({
                        "entity_type": entity_type,
                        "count": len(entities),
                        "entities": entities
                    }, f, indent=2, ensure_ascii=False)
                
                logger.info(f"Exported {len(entities)} {entity_type} entities to {export_file}")
        
        # Export relationships
        relationships = []
        if self.entity_store.relationships_dir.exists():
            for rel_file in self.entity_store.relationships_dir.glob("*.json"):
                try:
                    with open(rel_file, 'r', encoding='utf-8') as f:
                        relationship = json.load(f)
                        relationships.append(relationship)
                except Exception as e:
                    logger.error(f"Error reading relationship file {rel_file}: {str(e)}")
        
        if relationships:
            rel_export_file = export_dir / "relationships.json"
            with open(rel_export_file, 'w', encoding='utf-8') as f:
                json.dump({
                    "count": len(relationships),
                    "relationships": relationships
                }, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Exported {len(relationships)} relationships to {rel_export_file}")


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