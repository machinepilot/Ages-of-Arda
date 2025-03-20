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
from pathlib import Path
from datetime import datetime

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
            'concept': 'concepts'
        }
        
        # Age mapping
        self.age_mapping = {
            'first_age': 'first_age',
            'second_age': 'second_age',
            'third_age': 'third_age',
            'fourth_age': 'fourth_age',
            'unknown': 'third_age'  # Default to Third Age for unknown
        }
    
    def load_consolidated_entities(self):
        """
        Load consolidated entity files.
        
        Returns:
            dict: Loaded entities by type
        """
        entities = {}
        
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
        
        # Create memory bank entity
        memory_bank_entity = {
            "name": entity.get('name', 'Unknown'),
            "description": entity.get('description', ''),
            "content": entity.get('content', ''),
            "source": entity.get('source', 'Unknown source'),
            "year": 1,  # Default year
            "is_canonical": entity.get('is_canonical', True),
            "type": entity_type
        }
        
        # Add type-specific fields
        if entity_type == 'character':
            # Add character-specific fields
            memory_bank_entity["race"] = self._extract_race(entity)
            
            if 'mentions' in entity and entity['mentions']:
                memory_bank_entity["titles"] = entity['mentions']
            
            if 'related' in entity and entity['related']:
                memory_bank_entity["relations"] = self._format_relations(entity['related'])
        
        elif entity_type == 'location':
            # Add location-specific fields
            if 'mentions' in entity and entity['mentions']:
                memory_bank_entity["aliases"] = entity['mentions']
        
        elif entity_type in ['item', 'artifact', 'weapon']:
            # Add item-specific fields
            if 'mentions' in entity and entity['mentions']:
                memory_bank_entity["aliases"] = entity['mentions']
        
        return memory_bank_entity
    
    def _extract_race(self, entity):
        """
        Extract race information from an entity.
        
        Args:
            entity (dict): Entity data
            
        Returns:
            str: Extracted race or default
        """
        # Look for race in description or content
        description = entity.get('description', '').lower()
        content = entity.get('content', '').lower()
        
        races = [
            'elf', 'elves', 'elven', 'ñoldor', 'noldor', 'sindar', 'silvan', 
            'dwarf', 'dwarves', 'dwarven', 'man', 'men', 'human', 'humans',
            'hobbit', 'hobbits', 'halfling', 'orc', 'orcs', 'goblin', 'goblins',
            'maiar', 'maia', 'valar', 'vala', 'ainu', 'ainur', 'dragon', 'dragons',
            'ent', 'ents', 'eagle', 'eagles', 'troll', 'trolls'
        ]
        
        for race in races:
            if race in description or race in content:
                # Map to canonical race name
                race_map = {
                    'elves': 'Elf', 'elven': 'Elf', 'ñoldor': 'Elf (Noldor)', 'noldor': 'Elf (Noldor)',
                    'sindar': 'Elf (Sindar)', 'silvan': 'Elf (Silvan)',
                    'dwarves': 'Dwarf', 'dwarven': 'Dwarf',
                    'men': 'Man', 'human': 'Man', 'humans': 'Man',
                    'hobbits': 'Hobbit', 'halfling': 'Hobbit',
                    'orcs': 'Orc', 'goblin': 'Orc', 'goblins': 'Orc',
                    'maia': 'Maia', 'valar': 'Vala', 'vala': 'Vala', 'ainu': 'Ainu', 'ainur': 'Ainu',
                    'dragons': 'Dragon', 'ents': 'Ent', 'eagles': 'Eagle', 'trolls': 'Troll'
                }
                
                return race_map.get(race, race.capitalize())
        
        return "Unknown"
    
    def _format_relations(self, related_entities):
        """
        Format related entities into relations object.
        
        Args:
            related_entities (list): List of related entities
            
        Returns:
            dict: Formatted relations
        """
        # Simple approach: just create a generic "related" relationship
        relations = {}
        
        if related_entities:
            relations["related"] = related_entities
        
        return relations
    
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
            
            # Ensure the books section exists
            if 'books' not in existing_index:
                existing_index['books'] = {}
            
            # Ensure entity_count section exists
            if 'entity_count' not in existing_index:
                existing_index['entity_count'] = {}
            
            # Update entity counts
            for age in processed_entities:
                age_key = age.lower()
                
                if age_key not in existing_index['entity_count']:
                    existing_index['entity_count'][age_key] = {}
                
                for entity_type, count in processed_entities[age].items():
                    existing_index['entity_count'][age_key][entity_type] = count
            
            # Add total counts
            totals = {}
            for age_data in processed_entities.values():
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
                    results['successful'].append({
                        'name': entity.get('name', 'unknown'),
                        'type': entity_type,
                        'age': memory_bank_age,
                        'path': saved_path
                    })
                    
                    # Update counters
                    type_count += 1
                    results['total_entities'] += 1
                    results['entities_by_type'][entity_type] += 1
                    results['entities_by_age'][memory_bank_age] += 1
                    processed_entities[memory_bank_age][type_dir] += 1
                    
                else:
                    results['failed'].append({
                        'name': entity.get('name', 'unknown'),
                        'type': entity_type,
                        'age': memory_bank_age
                    })
            
            logger.info(f"Integrated {type_count} {entity_type} entities into Memory Bank")
        
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