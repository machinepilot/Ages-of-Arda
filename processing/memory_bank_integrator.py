"""
Memory Bank Integrator for Ages of Arda

This module provides functionality for integrating consolidated entities
into the Ages of Arda Memory Bank system.
"""

import os
import sys
import json
import logging
import shutil
import re
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional, Set, Tuple
from collections import defaultdict

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join('processing', 'logs', 'memory_bank_integration.log')),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('memory_bank_integrator')

class MemoryBankIntegrator:
    """
    Integrator for adding consolidated entities to the Memory Bank system.
    """
    
    def __init__(self, consolidated_dir, memory_bank_dir, schema_dir=None):
        """
        Initialize the Memory Bank integrator.
        
        Args:
            consolidated_dir (str): Directory containing consolidated entities
            memory_bank_dir (str): Root directory of the Memory Bank
            schema_dir (str, optional): Directory containing schema files for validation
        """
        self.consolidated_dir = Path(consolidated_dir)
        self.memory_bank_dir = Path(memory_bank_dir)
        self.schema_dir = Path(schema_dir) if schema_dir else None
        
        # Mapping of entity types to Memory Bank subdirectories
        self.type_to_dir = {
            'character': 'characters',
            'location': 'locations',
            'item': 'items',
            'artifact': 'items',
            'weapon': 'items',
            'event': 'events',
            'culture': 'cultures',
            'creature': 'creatures',
            'concept': 'concepts',
            'language': 'languages',
            'race': 'races'
        }
        
        # Age mapping
        self.age_mapping = {
            'FIRST_AGE': 'first_age',
            'SECOND_AGE': 'second_age',
            'THIRD_AGE': 'third_age',
            'FOURTH_AGE': 'fourth_age',
            'first_age': 'first_age',
            'second_age': 'second_age',
            'third_age': 'third_age',
            'fourth_age': 'fourth_age',
            'unknown': 'third_age'  # Default to Third Age for unknown
        }
        
        # Load age definitions
        self.age_definitions = self._load_age_definitions()
        
        # Load reference entity lists for canonical matching
        self.reference_entities = self._load_reference_entities()
        
        # Relations mapping
        self.relationship_mapping = {
            'associated_with': 'associated with',
            'located_at': 'located at',
            'contains': 'contains',
            'possesses': 'possesses',
            'possessed_by': 'possessed by',
            'participated_in': 'participated in',
            'involved': 'involved',
            'connected_to': 'connected to',
            'setting_for': 'setting for',
            'occurred_at': 'occurred at',
            'related_to': 'related to',
            'used_in': 'used in',
            'featured': 'featured in',
            'created': 'created',
            'created_by': 'created by',
            'ruled': 'ruled',
            'ruled_by': 'ruled by',
            'parent_of': 'parent of',
            'child_of': 'child of',
            'allied_with': 'allied with',
            'enemy_of': 'enemy of'
        }
    
    def _load_age_definitions(self) -> Dict[str, Dict[str, Any]]:
        """
        Load age definitions from schema file.
        
        Returns:
            Dict[str, Dict[str, Any]]: Age definitions
        """
        age_schema_path = Path("processing/schemas/age_definitions.json")
        if not age_schema_path.exists():
            logger.warning(f"Age definitions schema not found: {age_schema_path}")
            return {}
        
        try:
            with open(age_schema_path, 'r', encoding='utf-8') as f:
                age_definitions = json.load(f)
            
            logger.info(f"Loaded {len(age_definitions)} age definitions")
            return age_definitions
        except Exception as e:
            logger.error(f"Error loading age definitions: {str(e)}")
            return {}
    
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
    
    def load_consolidated_entities(self):
        """
        Load consolidated entity files.
        
        Returns:
            dict: Loaded entities by type
        """
        entities = {}
        
        # First try to load from age-organized directories
        age_organized = False
        for age_name in self.age_mapping.keys():
            age_dir = self.consolidated_dir / age_name.lower()
            if age_dir.exists() and age_dir.is_dir():
                age_organized = True
                
                # Process each entity type file in the age directory
                for file_path in age_dir.glob('*.json'):
                    # Skip summary files
                    if 'summary' in file_path.name:
                        continue
                    
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            data = json.load(f)
                        
                        # Get entity type from filename (e.g., "characters.json" -> "character")
                        entity_type = file_path.stem
                        if entity_type.endswith('s'):
                            entity_type = entity_type[:-1]
                        
                        # Initialize the entity type list if needed
                        if entity_type not in entities:
                            entities[entity_type] = []
                        
                        # Add age information to each entity
                        for entity in data:
                            if 'age' not in entity or not entity['age']:
                                entity['age'] = age_name
                        
                        # Add entities to the list
                        entities[entity_type].extend(data)
                        logger.info(f"Loaded {len(data)} {entity_type} entities from {file_path.name} in {age_name}")
                        
                    except Exception as e:
                        logger.error(f"Error loading entities from {file_path}: {str(e)}")
        
        # If no age-organized files were found, try the flat structure
        if not age_organized:
            # Find all JSON files in the consolidated directory
            entity_files = list(self.consolidated_dir.glob('*.json'))
            
            for file_path in entity_files:
                # Skip summary files
                if 'summary' in file_path.name:
                    continue
                
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    
                    # Get entity type from filename (e.g., "characters.json" -> "character")
                    entity_type = file_path.stem
                    if entity_type.endswith('s'):
                        entity_type = entity_type[:-1]
                    
                    entities[entity_type] = data
                    logger.info(f"Loaded {len(data)} {entity_type} entities from {file_path.name}")
                    
                except Exception as e:
                    logger.error(f"Error loading entities from {file_path}: {str(e)}")
        
        return entities
    
    def prepare_memory_bank_directories(self):
        """
        Prepare directories in the Memory Bank for entity integration.
        
        Returns:
            dict: Dictionary of created directories
        """
        created_dirs = {}
        
        # Create lore directory if it doesn't exist
        lore_dir = self.memory_bank_dir / 'lore'
        lore_dir.mkdir(exist_ok=True)
        
        # Create age directories
        for age in self.age_mapping.values():
            age_dir = lore_dir / age
            age_dir.mkdir(exist_ok=True)
            created_dirs[age] = {}
            
            # Create entity type directories within each age
            for entity_type_dir in self.type_to_dir.values():
                type_dir = age_dir / entity_type_dir
                type_dir.mkdir(exist_ok=True)
                created_dirs[age][entity_type_dir] = type_dir
        
        logger.info(f"Prepared directory structure in {lore_dir}")
        
        # Create references directory for cross-references
        refs_dir = lore_dir / 'references'
        refs_dir.mkdir(exist_ok=True)
        
        return created_dirs
    
    def validate_entity(self, entity, entity_type):
        """
        Validate an entity against its schema.
        
        Args:
            entity (dict): Entity data
            entity_type (str): Type of entity
            
        Returns:
            bool: True if valid, False otherwise
        """
        # Skip validation if no schema directory was provided
        if not self.schema_dir:
            return True
        
        try:
            # Import schema validator if available
            sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            from processing.schema_validator import SchemaValidator
            
            validator = SchemaValidator(self.schema_dir)
            valid, _ = validator.validate_entity(entity, entity_type)
            
            return valid
            
        except ImportError:
            logger.warning("Schema validator not available, skipping validation")
            return True
        except Exception as e:
            logger.error(f"Error validating entity: {str(e)}")
            return True  # Default to valid on error
    
    def determine_discovery_depth(self, entity, entity_type):
        """
        Determine the discovery depth for an entity.
        
        Args:
            entity (dict): Entity data
            entity_type (str): Type of entity
            
        Returns:
            int: Discovery depth (1-4)
        """
        # Default to mid-level depth
        default_depth = 2
        
        # Check if entity is canonical (canonical entities are more accessible)
        is_canonical = entity.get('is_canonical', False)
        
        # Check if entity is a major figure in its age
        is_major_figure = False
        age = entity.get('age', 'unknown').upper()
        if age in self.age_definitions:
            major_figures = self.age_definitions[age].get('major_figures', [])
            if entity['name'] in major_figures:
                is_major_figure = True
        
        # Common/well-known canonical entities are surface level (depth 1)
        if is_canonical and (is_major_figure or self._is_common_entity(entity, entity_type)):
            return 1
        
        # Less common canonical entities are mid-level (depth 2)
        if is_canonical:
            return 2
        
        # Non-canonical entities related to canonical ones are deep level (depth 3)
        if self._has_canonical_relationships(entity):
            return 3
        
        # Everything else is hidden level (depth 4)
        return 4
    
    def _is_common_entity(self, entity, entity_type):
        """
        Check if an entity is commonly known in Tolkien's lore.
        
        Args:
            entity (dict): Entity data
            entity_type (str): Type of entity
            
        Returns:
            bool: True if the entity is common/well-known
        """
        # Check against a list of common entities
        common_entities = {
            'character': [
                'gandalf', 'frodo', 'aragorn', 'bilbo', 'galadriel', 'legolas', 'gimli',
                'sauron', 'saruman', 'elrond', 'gollum', 'sam', 'boromir', 'faramir'
            ],
            'location': [
                'mordor', 'gondor', 'rohan', 'the shire', 'rivendell', 'moria', 'isengard',
                'minas tirith', 'helm\'s deep', 'lothlorien', 'fangorn'
            ],
            'item': [
                'one ring', 'sting', 'glamdring', 'narsil', 'anduril', 'palantir'
            ]
        }
        
        # Check if the entity name is in the common list
        if entity_type in common_entities:
            if entity['name'].lower() in common_entities[entity_type]:
                return True
            
            # Check alternate names
            for mention in entity.get('mentions', []):
                if mention.lower() in common_entities[entity_type]:
                    return True
        
        return False
    
    def _has_canonical_relationships(self, entity):
        """
        Check if an entity has relationships to canonical entities.
        
        Args:
            entity (dict): Entity data
            
        Returns:
            bool: True if the entity has relationships to canonical entities
        """
        # Get related entities
        related = entity.get('related', [])
        
        # Check if any related entities are canonical
        for rel_name in related:
            # Simplified check - in a full implementation, we would need
            # to look up each related entity and check its canonical status
            for type_entities in self.reference_entities.values():
                for ref_entity in type_entities:
                    if ref_entity['name'].lower() == rel_name.lower():
                        return True
                    
                    # Check alternate names
                    alt_names = ref_entity.get('alternate_names', [])
                    if any(alt.lower() == rel_name.lower() for alt in alt_names):
                        return True
        
        return False
    
    def format_entity_for_memory_bank(self, entity, entity_type):
        """
        Format an entity for Memory Bank storage.
        
        Args:
            entity (dict): Entity data
            entity_type (str): Type of entity
            
        Returns:
            dict: Formatted entity
        """
        # Map age to memory bank format
        age = entity.get('age', 'unknown')
        memory_bank_age = self.age_mapping.get(age, 'third_age')
        
        # Determine discovery depth
        discovery_depth = self.determine_discovery_depth(entity, entity_type)
        
        # Format source information
        source_reference = entity.get('source_reference', entity.get('source', 'Unknown source'))
        
        # Extract canonical status
        is_canonical = entity.get('is_canonical', False)
        
        # Create memory bank entity
        memory_bank_entity = {
            "name": entity.get('name', 'Unknown'),
            "description": entity.get('description', ''),
            "content": self._enhance_content(entity),
            "source": source_reference,
            "metadata": {
                "entity_type": entity_type,
                "entity_subtype": entity.get('subtype', ''),
                "age": memory_bank_age,
                "discovery_depth": discovery_depth,
                "canonical": is_canonical,
                "last_updated": datetime.now().isoformat()
            },
            "references": {
                "relationships": self._format_relationships(entity)
            }
        }
        
        # Add alternate names
        if 'mentions' in entity and entity['mentions']:
            memory_bank_entity["alternate_names"] = entity['mentions']
        
        # Add timeline for events
        if entity_type == 'event':
            memory_bank_entity["timeline"] = self._create_event_timeline(entity)
        
        # Add type-specific fields to attributes
        memory_bank_entity["attributes"] = self._add_type_specific_attributes(entity, entity_type)
        
        return memory_bank_entity
    
    def _enhance_content(self, entity):
        """
        Enhance entity content with additional contextual information.
        
        Args:
            entity (dict): Entity data
            
        Returns:
            str: Enhanced content
        """
        # Start with the base content
        content = entity.get('content', '')
        
        # If content is empty, use description as a fallback
        if not content:
            content = entity.get('description', '')
            
            # If we still have no content, generate a placeholder
            if not content:
                content = f"Information about {entity.get('name', 'this entity')}."
        
        # Add canonical status note
        if entity.get('is_canonical', False):
            content += "\n\n*This entity is directly based on J.R.R. Tolkien's works.*"
        else:
            content += "\n\n*This entity is derived from or inspired by J.R.R. Tolkien's works.*"
        
        # Add source information if not already in the content
        source_ref = entity.get('source_reference', entity.get('source', ''))
        if source_ref and "Source:" not in content:
            content += f"\n\nSource: {source_ref}"
        
        return content
    
    def _format_relationships(self, entity):
        """
        Format relationship data for Memory Bank.
        
        Args:
            entity (dict): Entity data
            
        Returns:
            list: Formatted relationships
        """
        relationships = []
        
        # Process related entities
        related = entity.get('related', [])
        
        # Simple approach for now - we'd need more context to determine relationship types
        for rel_name in related:
            # Create a basic relationship entry
            relationship = {
                "entity": rel_name,
                "type": "related"  # Default type
            }
            
            relationships.append(relationship)
        
        return relationships
    
    def _extract_race(self, entity):
        """
        Extract race information from an entity.
        
        Args:
            entity (dict): Entity data
            
        Returns:
            str: Extracted race or default
        """
        # Check if subtype contains race information
        subtype = entity.get('subtype', '').lower()
        
        race_mapping = {
            'elf': 'Elf',
            'noldor': 'Elf (Noldor)',
            'sindar': 'Elf (Sindar)',
            'silvan': 'Elf (Silvan)',
            'dwarf': 'Dwarf',
            'man': 'Man',
            'human': 'Man',
            'numenorean': 'Man (Númenórean)',
            'dunedain': 'Man (Dúnedain)',
            'hobbit': 'Hobbit',
            'orc': 'Orc',
            'goblin': 'Orc',
            'uruk': 'Uruk-hai',
            'ent': 'Ent',
            'eagle': 'Eagle',
            'dragon': 'Dragon',
            'troll': 'Troll',
            'vala': 'Vala',
            'maia': 'Maia',
            'balrog': 'Maia (Balrog)',
            'istari': 'Maia (Istari)',
            'wizard': 'Maia (Istari)'
        }
        
        if subtype in race_mapping:
            return race_mapping[subtype]
        
        # Look for race in description or content
        description = entity.get('description', '').lower()
        content = entity.get('content', '').lower()
        
        for race_term, race_name in race_mapping.items():
            if race_term in description or race_term in content:
                return race_name
        
        return "Unknown"
    
    def _create_event_timeline(self, entity):
        """
        Create a timeline entry for an event entity.
        
        Args:
            entity (dict): Entity data
            
        Returns:
            list: Timeline entries
        """
        timeline = []
        
        # For now, just create a single timeline entry
        # In a more sophisticated implementation, we would extract multiple events
        timeline_entry = {
            "year": self._extract_year_from_entity(entity),
            "event": entity.get('description', f"{entity.get('name', 'Unknown event')} occurred."),
            "source": entity.get('source_reference', entity.get('source', ''))
        }
        
        timeline.append(timeline_entry)
        
        return timeline
    
    def _extract_year_from_entity(self, entity):
        """
        Extract year information from an entity.
        
        Args:
            entity (dict): Entity data
            
        Returns:
            str: Year or time period
        """
        # Look for year patterns in description or content
        description = entity.get('description', '')
        content = entity.get('content', '')
        
        # Common year patterns in Tolkien's works
        year_patterns = [
            r'(?:in|year) (\d+) (?:of the|of) (?:first|second|third|fourth) age',
            r'(?:in|year) (\w+) (\d+)',
            r'(?:in the year|year) (\d+)',
            r'(\d+) (?:FA|SA|TA|FO)'
        ]
        
        for text in [description, content]:
            for pattern in year_patterns:
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    return match.group(0)
        
        # Default to age if no specific year found
        age = entity.get('age', 'unknown')
        if age in self.age_definitions:
            return f"{self.age_definitions[age].get('name', age)}"
        
        return "Unknown date"
    
    def _add_type_specific_attributes(self, entity, entity_type):
        """
        Add type-specific attributes to entity.
        
        Args:
            entity (dict): Entity data
            entity_type (str): Type of entity
            
        Returns:
            dict: Type-specific attributes
        """
        attributes = {}
        
        if entity_type == 'character':
            attributes["race"] = self._extract_race(entity)
            attributes["titles"] = entity.get('mentions', [])
            
        elif entity_type == 'location':
            # Add location-specific attributes
            if 'mentions' in entity:
                attributes["alternate_names"] = entity.get('mentions', [])
                
            # Try to determine location type from subtype
            location_type = entity.get('subtype', '').lower()
            if location_type:
                attributes["location_type"] = location_type.capitalize()
            
        elif entity_type in ['item', 'artifact', 'weapon']:
            # Add item-specific attributes
            if 'mentions' in entity:
                attributes["alternate_names"] = entity.get('mentions', [])
                
            item_type = entity.get('subtype', '').lower()
            if item_type:
                attributes["item_type"] = item_type.capitalize()
        
        return attributes
    
    def save_entity_to_memory_bank(self, entity, entity_type, directories):
        """
        Save an entity to the Memory Bank.
        
        Args:
            entity (dict): Entity data
            entity_type (str): Type of entity
            directories (dict): Dictionary of Memory Bank directories
            
        Returns:
            str: Path to saved file, or None if failed
        """
        try:
            # Get memory bank age
            age = entity.get('age', 'unknown')
            memory_bank_age = self.age_mapping.get(age, 'third_age')
            
            # Get entity type directory
            entity_type_dir = self.type_to_dir.get(entity_type, entity_type + 's')
            
            # Get target directory
            if memory_bank_age not in directories or entity_type_dir not in directories[memory_bank_age]:
                logger.error(f"Directory not found for {memory_bank_age}/{entity_type_dir}")
                return None
            
            target_dir = directories[memory_bank_age][entity_type_dir]
            
            # Format entity for memory bank
            memory_bank_entity = self.format_entity_for_memory_bank(entity, entity_type)
            
            # Validate before saving
            if not self.validate_entity(memory_bank_entity, entity_type):
                logger.warning(f"Entity validation failed for {entity.get('name', 'unknown entity')}")
                # Continue anyway but log the issue
            
            # Create filename (sanitized entity name)
            filename = entity.get('name', 'unknown').lower()
            filename = ''.join(c if c.isalnum() or c == '_' else '_' for c in filename) + '.json'
            
            # Save to file
            target_file = target_dir / filename
            with open(target_file, 'w', encoding='utf-8') as f:
                json.dump(memory_bank_entity, f, indent=4, ensure_ascii=False)
            
            logger.debug(f"Saved {entity.get('name', 'unknown entity')} to {target_file}")
            
            return str(target_file)
            
        except Exception as e:
            logger.error(f"Error saving entity {entity.get('name', 'unknown')}: {str(e)}")
            return None
    
    def create_cross_references(self, processed_entities):
        """
        Create cross-reference files to help with entity lookup.
        
        Args:
            processed_entities (dict): Dictionary of processed entities
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Create references directory
            refs_dir = self.memory_bank_dir / 'lore' / 'references'
            refs_dir.mkdir(exist_ok=True)
            
            # Create name to path mapping
            name_mapping = {}
            for entity_info in processed_entities['successful']:
                name = entity_info.get('name', '').lower()
                if name:
                    name_mapping[name] = {
                        'path': entity_info.get('path', ''),
                        'type': entity_info.get('type', ''),
                        'age': entity_info.get('age', '')
                    }
            
            # Save name mapping
            name_map_file = refs_dir / 'name_mapping.json'
            with open(name_map_file, 'w', encoding='utf-8') as f:
                json.dump(name_mapping, f, indent=2, ensure_ascii=False)
            
            # Create type mapping
            type_mapping = defaultdict(list)
            for entity_info in processed_entities['successful']:
                entity_type = entity_info.get('type', '')
                if entity_type:
                    type_mapping[entity_type].append({
                        'name': entity_info.get('name', ''),
                        'path': entity_info.get('path', ''),
                        'age': entity_info.get('age', '')
                    })
            
            # Save type mapping
            type_map_file = refs_dir / 'type_mapping.json'
            with open(type_map_file, 'w', encoding='utf-8') as f:
                json.dump(dict(type_mapping), f, indent=2, ensure_ascii=False)
            
            logger.info(f"Created cross-reference files in {refs_dir}")
            return True
        
        except Exception as e:
            logger.error(f"Error creating cross-references: {str(e)}")
            return False
    
    def update_lore_index(self, processed_entities):
        """
        Update the Memory Bank lore index.
        
        Args:
            processed_entities (dict): Dictionary of processed entities by type and age
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Path to lore index
            lore_index_path = self.memory_bank_dir / 'lore' / 'lore_index.json'
            
            # Load existing index if it exists
            existing_index = {}
            if lore_index_path.exists():
                try:
                    with open(lore_index_path, 'r', encoding='utf-8') as f:
                        existing_index = json.load(f)
                except Exception as e:
                    logger.error(f"Error loading existing lore index: {str(e)}")
            
            # Ensure required sections exist
            if 'books' not in existing_index:
                existing_index['books'] = {}
            
            if 'entity_count' not in existing_index:
                existing_index['entity_count'] = {}
            
            # Update entity counts
            for age in processed_entities:
                age_key = age.lower()
                
                if age_key not in existing_index['entity_count']:
                    existing_index['entity_count'][age_key] = {}
                
                for entity_type, count in processed_entities[age].items():
                    existing_index['entity_count'][age_key][entity_type] = count
            
            # Calculate discovery depth counts
            depth_counts = {
                '1': 0,  # Surface level
                '2': 0,  # Mid-level
                '3': 0,  # Deep level
                '4': 0   # Hidden level
            }
            
            # Add depth information if available
            for entity_info in processed_entities.get('successful', []):
                entity_path = entity_info.get('path', '')
                if entity_path and Path(entity_path).exists():
                    try:
                        with open(entity_path, 'r', encoding='utf-8') as f:
                            entity_data = json.load(f)
                            depth = str(entity_data.get('metadata', {}).get('discovery_depth', 2))
                            depth_counts[depth] = depth_counts.get(depth, 0) + 1
                    except Exception:
                        pass
            
            existing_index['discovery_depth'] = depth_counts
            
            # Add total counts
            totals = {}
            for age_data in processed_entities.values():
                if isinstance(age_data, dict):
                    for entity_type, count in age_data.items():
                        totals[entity_type] = totals.get(entity_type, 0) + count
            
            existing_index['total_entities'] = sum(totals.values())
            existing_index['entity_count']['total'] = totals
            
            # Add last updated timestamp
            existing_index['last_updated'] = datetime.now().isoformat()
            
            # Save updated index
            with open(lore_index_path, 'w', encoding='utf-8') as f:
                json.dump(existing_index, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Updated lore index at {lore_index_path}")
            
            return True
            
        except Exception as e:
            logger.error(f"Error updating lore index: {str(e)}")
            return False
    
    def integrate(self):
        """
        Perform the full integration process.
        
        Returns:
            dict: Integration results
        """
        results = {
            'total_entities': 0,
            'entities_by_type': {},
            'entities_by_age': {},
            'entities_by_depth': {1: 0, 2: 0, 3: 0, 4: 0},
            'successful': [],
            'failed': []
        }
        
        # Load consolidated entities
        entities = self.load_consolidated_entities()
        
        # Prepare Memory Bank directories
        directories = self.prepare_memory_bank_directories()
        
        # Process by entity type
        processed_entities = {}
        
        for entity_type, entity_list in entities.items():
            type_count = 0
            results['entities_by_type'][entity_type] = 0
            
            for entity in entity_list:
                # Skip invalid entities
                if not entity or 'name' not in entity:
                    continue
                
                # Get age for this entity
                age = entity.get('age', 'unknown')
                memory_bank_age = self.age_mapping.get(age, 'third_age')
                
                # Initialize age counters if needed
                if memory_bank_age not in results['entities_by_age']:
                    results['entities_by_age'][memory_bank_age] = 0
                
                if memory_bank_age not in processed_entities:
                    processed_entities[memory_bank_age] = {}
                
                type_dir = self.type_to_dir.get(entity_type, entity_type + 's')
                if type_dir not in processed_entities[memory_bank_age]:
                    processed_entities[memory_bank_age][type_dir] = 0
                
                # Save to Memory Bank
                saved_path = self.save_entity_to_memory_bank(entity, entity_type, directories)
                
                if saved_path:
                    # Determine discovery depth
                    depth = self.determine_discovery_depth(entity, entity_type)
                    
                    results['successful'].append({
                        'name': entity.get('name', 'unknown'),
                        'type': entity_type,
                        'age': memory_bank_age,
                        'path': saved_path,
                        'depth': depth
                    })
                    
                    # Update counters
                    type_count += 1
                    results['total_entities'] += 1
                    results['entities_by_type'][entity_type] += 1
                    results['entities_by_age'][memory_bank_age] += 1
                    processed_entities[memory_bank_age][type_dir] += 1
                    results['entities_by_depth'][depth] += 1
                    
                else:
                    results['failed'].append({
                        'name': entity.get('name', 'unknown'),
                        'type': entity_type,
                        'age': memory_bank_age
                    })
            
            logger.info(f"Integrated {type_count} {entity_type} entities into Memory Bank")
        
        # Create cross-references
        self.create_cross_references(results)
        
        # Update lore index
        self.update_lore_index(processed_entities)
        
        # Create completion summary
        results['complete'] = True
        results['timestamp'] = datetime.now().isoformat()
        
        # Save summary to file
        summary_file = self.consolidated_dir / 'integration_summary.json'
        with open(summary_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Integration complete. Added {results['total_entities']} entities to Memory Bank.")
        logger.info(f"Results by type: {results['entities_by_type']}")
        logger.info(f"Results by age: {results['entities_by_age']}")
        logger.info(f"Results by discovery depth: {results['entities_by_depth']}")
        
        return results


def integrate_to_memory_bank(consolidated_dir, memory_bank_dir, schema_dir=None):
    """
    Integrate consolidated entities into the Memory Bank system.
    
    Args:
        consolidated_dir (str): Directory containing consolidated entities
        memory_bank_dir (str): Root directory of the Memory Bank
        schema_dir (str, optional): Directory containing schema files for validation
        
    Returns:
        dict: Integration results
    """
    integrator = MemoryBankIntegrator(consolidated_dir, memory_bank_dir, schema_dir)
    return integrator.integrate()


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Integrate entities into Memory Bank")
    parser.add_argument("--input-dir", default="processing/consolidated", help="Input directory containing consolidated entities")
    parser.add_argument("--memory-bank-dir", default=".memory-bank", help="Memory Bank root directory")
    parser.add_argument("--schema-dir", default="processing/schemas", help="Directory containing schema files")
    args = parser.parse_args()
    
    integrate_to_memory_bank(args.input_dir, args.memory_bank_dir, args.schema_dir) 