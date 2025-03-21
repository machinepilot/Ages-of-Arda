"""
Entity Consolidator for Ages of Arda

This module provides functionality for consolidating entities extracted from
different chapters and books, resolving duplicates and merging related information.
"""

import os
import json
import logging
import re
from pathlib import Path
from collections import defaultdict
from typing import Dict, List, Any, Set, Tuple, Optional
import difflib

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join('processing', 'logs', 'entity_consolidation.log')),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('entity_consolidator')

class EntityConsolidator:
    """
    Consolidator for merging and deduplicating entities from multiple sources.
    """
    
    def __init__(self, input_dir, output_dir):
        """
        Initialize the entity consolidator.
        
        Args:
            input_dir (str): Directory containing extracted entity files
            output_dir (str): Directory to save consolidated entities
        """
        self.input_dir = Path(input_dir)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize entity dictionaries
        self.entities_by_type = defaultdict(dict)
        self.aliases = defaultdict(set)
        self.related_entities = defaultdict(set)
        self.entity_mentions = defaultdict(set)
        self.entity_descriptions = defaultdict(list)
        self.entity_sources = defaultdict(list)
        
        # Load age definitions
        self.age_definitions = self._load_age_definitions()
        
        # Load reference entity lists for canonical matching
        self.reference_entities = self._load_reference_entities()
        
        # Initialize similarity thresholds
        self.name_similarity_threshold = 0.85  # Threshold for name similarity
        self.desc_similarity_threshold = 0.6   # Threshold for description similarity
    
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
    
    def load_entities_from_extracted_data(self):
        """
        Load entities from the exported data produced by EntityExtractor.
        
        Returns:
            int: Number of entities loaded
        """
        exports_dir = self.input_dir / "exports"
        if not exports_dir.exists():
            logger.warning(f"Exports directory not found: {exports_dir}")
            return 0
        
        # Load entity type files
        entity_count = 0
        for entity_file in exports_dir.glob("*_entities.json"):
            try:
                entity_type = entity_file.stem.split('_')[0]  # Extract type from filename
                
                with open(entity_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                entities = data.get('entities', [])
                
                # Process each entity
                for entity in entities:
                    self.process_entity(entity, entity_type, {})
                    entity_count += 1
                
                logger.info(f"Loaded {len(entities)} {entity_type} entities from {entity_file}")
                
            except Exception as e:
                logger.error(f"Error loading entities from {entity_file}: {str(e)}")
        
        # Load relationships file if available
        relationships_file = exports_dir / "relationships.json"
        if relationships_file.exists():
            try:
                with open(relationships_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                relationships = data.get('relationships', [])
                
                # Process each relationship
                for relationship in relationships:
                    self.process_relationship(relationship)
                
                logger.info(f"Loaded {len(relationships)} relationships from {relationships_file}")
                
            except Exception as e:
                logger.error(f"Error loading relationships from {relationships_file}: {str(e)}")
        
        return entity_count
    
    def load_entities_from_entity_store(self):
        """
        Load entities directly from the EntityStore structure.
        
        Returns:
            int: Number of entities loaded
        """
        entity_store_dir = self.input_dir / "entity_store"
        if not entity_store_dir.exists():
            logger.warning(f"Entity store directory not found: {entity_store_dir}")
            return 0
        
        # Load entities by type
        entity_count = 0
        for type_dir in entity_store_dir.iterdir():
            if not type_dir.is_dir() or type_dir.name == "relationships":
                continue
            
            entity_type = type_dir.name
            
            # Process all entity files in this type directory
            for entity_file in type_dir.glob("*.json"):
                try:
                    with open(entity_file, 'r', encoding='utf-8') as f:
                        entity = json.load(f)
                    
                    self.process_entity(entity, entity_type, {})
                    entity_count += 1
                    
                except Exception as e:
                    logger.error(f"Error loading entity from {entity_file}: {str(e)}")
        
        # Load relationships if available
        relationship_dir = entity_store_dir / "relationships"
        if relationship_dir.exists():
            relationship_count = 0
            for rel_file in relationship_dir.glob("*.json"):
                try:
                    with open(rel_file, 'r', encoding='utf-8') as f:
                        relationship = json.load(f)
                    
                    self.process_relationship(relationship)
                    relationship_count += 1
                    
                except Exception as e:
                    logger.error(f"Error loading relationship from {rel_file}: {str(e)}")
            
            logger.info(f"Loaded {relationship_count} relationships from entity store")
        
        return entity_count
    
    def load_entities_from_file(self, entity_file):
        """
        Load entities from a single file.
        
        Args:
            entity_file (str): Path to entity JSON file
            
        Returns:
            tuple: (metadata, entities)
        """
        try:
            with open(entity_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            metadata = data.get('metadata', {})
            entities = data.get('entities', {})
            
            return metadata, entities
        except Exception as e:
            logger.error(f"Error loading entities from {entity_file}: {str(e)}")
            return {}, {}
    
    def process_entity(self, entity, entity_type, source_metadata):
        """
        Process a single entity and update the consolidated data.
        
        Args:
            entity (dict): Entity data
            entity_type (str): Type of entity (character, location, etc.)
            source_metadata (dict): Metadata about the source of this entity
        """
        if not entity or 'name' not in entity:
            return
        
        name = entity['name'].strip()
        if not name:
            return
        
        # Normalize entity name to lowercase for comparison
        name_key = name.lower()
        
        # If this is a new entity, add it to the dictionary
        if name_key not in self.entities_by_type[entity_type]:
            self.entities_by_type[entity_type][name_key] = {
                'name': name,
                'type': entity_type,
                'descriptions': [],
                'mentions': set(),
                'related': set(),
                'sources': [],
                'age': entity.get('age', 'unknown'),
                'subtype': entity.get('subtype', '')
            }
        
        # Add description
        if 'description' in entity and entity['description']:
            self.entities_by_type[entity_type][name_key]['descriptions'].append(entity['description'])
        
        # Add mentions/aliases
        mentions = []
        if 'mentions' in entity and entity['mentions']:
            mentions.extend(entity['mentions'])
        if 'alternate_names' in entity and entity['alternate_names']:
            mentions.extend(entity['alternate_names'])
            
        for mention in mentions:
            if mention and mention.strip() and mention.strip().lower() != name_key:
                self.entities_by_type[entity_type][name_key]['mentions'].add(mention.strip())
                # Map alias to canonical name
                self.aliases[mention.strip().lower()].add(name_key)
        
        # Add related entities
        if 'related' in entity and entity['related']:
            for related in entity['related']:
                if related and related.strip() and related.strip().lower() != name_key:
                    self.entities_by_type[entity_type][name_key]['related'].add(related.strip())
                    self.related_entities[name_key].add(related.strip().lower())
        
        # Add source
        if source_metadata:
            source = {
                'book_id': source_metadata.get('book_id', 'unknown'),
                'age': source_metadata.get('age', 'unknown'),
                'chapter_title': source_metadata.get('chapter_title', 'Unknown Chapter'),
                'chapter_number': source_metadata.get('chapter_number', 0)
            }
            self.entities_by_type[entity_type][name_key]['sources'].append(source)
        elif 'sources' in entity:
            # Copy existing sources
            self.entities_by_type[entity_type][name_key]['sources'].extend(entity['sources'])
    
    def process_relationship(self, relationship):
        """
        Process a relationship and update entity relationships.
        
        Args:
            relationship (dict): Relationship data
        """
        entity1_id = relationship.get('entity1', '')
        entity2_id = relationship.get('entity2', '')
        rel_type = relationship.get('type', '')
        
        if not entity1_id or not entity2_id or not rel_type:
            return
        
        # Extract entity names from IDs (simplified approach)
        # In a real implementation, we would need to map entity IDs to names
        entity1_name = self._entity_id_to_name(entity1_id)
        entity2_name = self._entity_id_to_name(entity2_id)
        
        if not entity1_name or not entity2_name:
            return
        
        # Add to related entities
        if rel_type != 'alternate_name':  # Skip alternate name relationships for this purpose
            for entity_type, entities in self.entities_by_type.items():
                if entity1_name.lower() in entities:
                    entities[entity1_name.lower()]['related'].add(entity2_name)
                if entity2_name.lower() in entities:
                    entities[entity2_name.lower()]['related'].add(entity1_name)
    
    def _entity_id_to_name(self, entity_id):
        """
        Convert an entity ID to an entity name.
        
        Args:
            entity_id (str): Entity ID
            
        Returns:
            str: Entity name
        """
        # Extract name part from entity ID
        # This is a simplified approach and might need to be improved
        name_part = entity_id.split('_')[0]
        name = name_part.replace('_', ' ').strip()
        
        # Try to find exact match
        for entity_type, entities in self.entities_by_type.items():
            for entity_key, entity in entities.items():
                if entity_key.startswith(name_part.lower()):
                    return entity['name']
        
        return name.capitalize()
    
    def load_all_entities(self):
        """
        Load all entity files from the input directory.
        
        Returns:
            int: Number of entities loaded
        """
        # Try to load from entity_store first
        entity_count = self.load_entities_from_entity_store()
        
        # If no entities found, try loading from exports
        if entity_count == 0:
            entity_count = self.load_entities_from_extracted_data()
        
        # If still no entities, try loading from individual entity files
        if entity_count == 0:
            entity_files = list(self.input_dir.glob('**/*_entities.json'))
            logger.info(f"Found {len(entity_files)} entity files in {self.input_dir}")
            
            # Process each file
            for entity_file in entity_files:
                try:
                    metadata, entities = self.load_entities_from_file(entity_file)
                    
                    # Process entities by type
                    for entity_type, entity_list in entities.items():
                        for entity in entity_list:
                            self.process_entity(entity, entity_type, metadata)
                            entity_count += 1
                    
                    logger.debug(f"Processed entities from {entity_file}")
                    
                except Exception as e:
                    logger.error(f"Error processing {entity_file}: {str(e)}")
        
        # Report entity counts by type
        for entity_type, entities in self.entities_by_type.items():
            logger.info(f"Loaded {len(entities)} unique {entity_type} entities")
        
        return entity_count
    
    def resolve_duplicates(self):
        """
        Resolve duplicate entities based on name similarity and aliases.
        
        Returns:
            int: Number of duplicates resolved
        """
        duplicates_resolved = 0
        
        # Process each entity type
        for entity_type, entities in self.entities_by_type.items():
            # Create a list of entity names for this type
            entity_names = list(entities.keys())
            
            # Check each pair of entities
            for i in range(len(entity_names)):
                name1 = entity_names[i]
                
                # Skip if this entity has already been merged
                if name1 not in entities:
                    continue
                
                for j in range(i + 1, len(entity_names)):
                    name2 = entity_names[j]
                    
                    # Skip if this entity has already been merged
                    if name2 not in entities:
                        continue
                    
                    # Check if they are aliases of each other
                    if name1 in self.aliases.get(name2, set()) or name2 in self.aliases.get(name1, set()):
                        # Merge entities
                        self._merge_entities(entity_type, name1, name2)
                        duplicates_resolved += 1
                        
                        # Remove the second entity as it's now merged
                        if name2 in entities:
                            del entities[name2]
                        continue
                    
                    # Check name similarity
                    if self._calculate_name_similarity(name1, name2) >= self.name_similarity_threshold:
                        # Names are similar, check if descriptions are also similar
                        if self._are_descriptions_similar(
                            entities[name1].get('descriptions', []),
                            entities[name2].get('descriptions', [])
                        ):
                            # Merge entities
                            self._merge_entities(entity_type, name1, name2)
                            duplicates_resolved += 1
                            
                            # Remove the second entity as it's now merged
                            if name2 in entities:
                                del entities[name2]
        
        logger.info(f"Resolved {duplicates_resolved} duplicate entities")
        return duplicates_resolved
    
    def _calculate_name_similarity(self, name1, name2):
        """
        Calculate similarity between two entity names.
        
        Args:
            name1 (str): First entity name
            name2 (str): Second entity name
            
        Returns:
            float: Similarity score (0.0-1.0)
        """
        return difflib.SequenceMatcher(None, name1, name2).ratio()
    
    def _are_descriptions_similar(self, descriptions1, descriptions2):
        """
        Check if two sets of descriptions are similar.
        
        Args:
            descriptions1 (list): First set of descriptions
            descriptions2 (list): Second set of descriptions
            
        Returns:
            bool: True if descriptions are similar
        """
        if not descriptions1 or not descriptions2:
            return False
        
        # Use the longest description from each set
        desc1 = max(descriptions1, key=len) if descriptions1 else ""
        desc2 = max(descriptions2, key=len) if descriptions2 else ""
        
        if not desc1 or not desc2:
            return False
        
        # Calculate similarity
        similarity = difflib.SequenceMatcher(None, desc1, desc2).ratio()
        return similarity >= self.desc_similarity_threshold
    
    def _merge_entities(self, entity_type, name1, name2):
        """
        Merge two entities.
        
        Args:
            entity_type (str): Type of the entities
            name1 (str): Name of the first entity (target)
            name2 (str): Name of the second entity (to be merged)
        """
        entities = self.entities_by_type[entity_type]
        if name1 not in entities or name2 not in entities:
            return
        
        entity1 = entities[name1]
        entity2 = entities[name2]
        
        # Merge descriptions
        entity1['descriptions'].extend(entity2['descriptions'])
        
        # Merge mentions
        entity1['mentions'].update(entity2['mentions'])
        
        # Merge related entities
        entity1['related'].update(entity2['related'])
        
        # Merge sources
        entity1['sources'].extend(entity2['sources'])
        
        # Update subtype if needed
        if not entity1['subtype'] and entity2['subtype']:
            entity1['subtype'] = entity2['subtype']
        
        # Update age if needed
        if entity1['age'] == 'unknown' and entity2['age'] != 'unknown':
            entity1['age'] = entity2['age']
        
        # Update aliases to point to the merged entity
        for alias in list(self.aliases.get(name2, [])):
            self.aliases[alias].remove(name2)
            self.aliases[alias].add(name1)
        
        # Update related entities references
        for related in list(self.related_entities.get(name2, [])):
            self.related_entities[related].remove(name2)
            self.related_entities[related].add(name1)
        
        logger.debug(f"Merged entities: {entity2['name']} -> {entity1['name']}")
    
    def generate_consolidated_entities(self):
        """
        Generate consolidated entity records.
        
        Returns:
            dict: Consolidated entities by type
        """
        consolidated = {}
        
        # Process each entity type
        for entity_type, entities in self.entities_by_type.items():
            consolidated[entity_type] = []
            
            # Process each entity
            for name_key, entity in entities.items():
                # Determine canonical status by matching with reference entities
                is_canonical = self._is_canonical_entity(entity, entity_type)
                
                # Select the best description
                descriptions = entity['descriptions']
                best_description = max(descriptions, key=len) if descriptions else ""
                
                # Determine age if not already set
                if entity['age'] == 'unknown':
                    entity['age'] = self._determine_entity_age(entity, entity_type)
                
                # Format data for output
                consolidated_entity = {
                    'name': entity['name'],
                    'type': entity_type.upper(),
                    'subtype': entity.get('subtype', ''),
                    'description': best_description,
                    'content': self._generate_content(entity, descriptions),
                    'mentions': list(entity['mentions']),
                    'related': list(entity['related']),
                    'sources': entity['sources'],
                    'source_reference': self._generate_source_reference(entity['sources']),
                    'age': entity['age'],
                    'is_canonical': is_canonical
                }
                
                consolidated[entity_type].append(consolidated_entity)
        
        return consolidated
    
    def _is_canonical_entity(self, entity, entity_type):
        """
        Determine if an entity is canonical by checking against reference entities.
        
        Args:
            entity (dict): Entity data
            entity_type (str): Type of entity
            
        Returns:
            bool: True if entity is canonical
        """
        # Check if entity name matches a reference entity
        if entity_type in self.reference_entities:
            entity_name = entity['name'].lower()
            
            for ref_entity in self.reference_entities[entity_type]:
                # Check primary name
                if ref_entity['name'].lower() == entity_name:
                    return True
                
                # Check alternate names
                alt_names = ref_entity.get('alternate_names', [])
                if any(alt.lower() == entity_name for alt in alt_names):
                    return True
        
        # If no match found, entity is not considered canonical
        return False
    
    def _determine_entity_age(self, entity, entity_type):
        """
        Determine the age to which an entity belongs.
        
        Args:
            entity (dict): Entity data
            entity_type (str): Type of entity
            
        Returns:
            str: Age identifier (FIRST_AGE, SECOND_AGE, etc.)
        """
        # First check if already assigned
        if entity.get('age') and entity['age'] != 'unknown':
            return entity['age']
        
        # Check if entity matches a reference entity with known age
        entity_name = entity['name'].lower()
        if entity_type in self.reference_entities:
            for ref_entity in self.reference_entities[entity_type]:
                # Check primary name
                if ref_entity['name'].lower() == entity_name:
                    if 'age' in ref_entity:
                        return ref_entity['age']
                
                # Check alternate names
                alt_names = ref_entity.get('alternate_names', [])
                if any(alt.lower() == entity_name for alt in alt_names):
                    if 'age' in ref_entity:
                        return ref_entity['age']
        
        # Check source information
        age_votes = defaultdict(int)
        for source in entity.get('sources', []):
            if 'age' in source and source['age'] != 'unknown':
                age_votes[source['age']] += 1
            
            # Check book references against age definitions
            book_id = source.get('book_id', '').lower()
            if book_id:
                for age_id, age_info in self.age_definitions.items():
                    books = [b.lower() for b in age_info.get('books', [])]
                    if any(book.lower() in book_id for book in books):
                        age_votes[age_id] += 1
        
        # Return the age with the most votes, or THIRD_AGE as a fallback
        # (since most of Tolkien's popular works are set in the Third Age)
        if age_votes:
            return max(age_votes.items(), key=lambda x: x[1])[0]
        else:
            return "THIRD_AGE"
    
    def _generate_content(self, entity, descriptions):
        """
        Generate detailed content text from descriptions.
        
        Args:
            entity (dict): Entity data
            descriptions (list): List of descriptions
            
        Returns:
            str: Generated content
        """
        if not descriptions:
            return ""
        
        # Use the longest description as the base content
        content = max(descriptions, key=len)
        
        # Append additional information if available
        if entity['mentions']:
            content += f"\n\nAlso known as: {', '.join(entity['mentions'])}."
        
        if entity['related']:
            content += f"\n\nRelated to: {', '.join(entity['related'])}."
        
        return content
    
    def _generate_source_reference(self, sources):
        """
        Generate a source reference string.
        
        Args:
            sources (list): List of source metadata
            
        Returns:
            str: Source reference string
        """
        if not sources:
            return "Unknown source"
        
        # Group by book
        books = {}
        for source in sources:
            book_id = source.get('book_id', 'unknown')
            chapter = source.get('chapter_title', 'Unknown Chapter')
            
            if book_id not in books:
                books[book_id] = set()
            
            books[book_id].add(chapter)
        
        # Format reference
        references = []
        for book_id, chapters in books.items():
            if len(chapters) <= 3:
                # List specific chapters
                book_ref = f"{book_id.capitalize()}, {', '.join(sorted(chapters))}"
            else:
                # Just mention the book
                book_ref = f"{book_id.capitalize()}, Various Chapters"
            
            references.append(book_ref)
        
        return "; ".join(references)
    
    def organize_by_age(self, consolidated):
        """
        Organize consolidated entities by age.
        
        Args:
            consolidated (dict): Consolidated entities by type
            
        Returns:
            dict: Entities organized by age
        """
        by_age = defaultdict(lambda: defaultdict(list))
        
        # Organize entities by age and type
        for entity_type, entities in consolidated.items():
            for entity in entities:
                age = entity.get('age', 'unknown').upper()
                by_age[age][entity_type].append(entity)
        
        return by_age
    
    def save_consolidated_entities(self, consolidated):
        """
        Save consolidated entities to JSON files.
        
        Args:
            consolidated (dict): Consolidated entities by type
        """
        # Save each entity type to its own file
        for entity_type, entities in consolidated.items():
            output_file = self.output_dir / f"{entity_type}s.json"
            
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(entities, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Saved {len(entities)} {entity_type} entities to {output_file}")
        
        # Save entities organized by age
        by_age = self.organize_by_age(consolidated)
        for age, age_entities in by_age.items():
            age_dir = self.output_dir / age.lower()
            age_dir.mkdir(exist_ok=True)
            
            # Save summary for this age
            age_summary = {
                'age': age,
                'name': self.age_definitions.get(age, {}).get('name', age),
                'entity_counts': {entity_type: len(entities) for entity_type, entities in age_entities.items()},
                'total_entities': sum(len(entities) for entities in age_entities.values())
            }
            
            summary_file = age_dir / "summary.json"
            with open(summary_file, 'w', encoding='utf-8') as f:
                json.dump(age_summary, f, indent=2, ensure_ascii=False)
            
            # Save each entity type for this age
            for entity_type, entities in age_entities.items():
                type_file = age_dir / f"{entity_type}s.json"
                with open(type_file, 'w', encoding='utf-8') as f:
                    json.dump(entities, f, indent=2, ensure_ascii=False)
        
        # Create a summary file
        summary = {
            'total_entities': sum(len(entities) for entities in consolidated.values()),
            'entity_counts': {entity_type: len(entities) for entity_type, entities in consolidated.items()},
            'entity_files': {entity_type: f"{entity_type}s.json" for entity_type in consolidated.keys()},
            'ages': {
                age: {
                    'name': self.age_definitions.get(age, {}).get('name', age),
                    'entity_count': sum(len(entities) for entities in age_entities.values())
                } for age, age_entities in by_age.items()
            }
        }
        
        summary_file = self.output_dir / "consolidated_summary.json"
        with open(summary_file, 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2)
        
        logger.info(f"Saved consolidation summary to {summary_file}")
    
    def consolidate(self):
        """
        Perform the full consolidation process.
        
        Returns:
            dict: Consolidation results
        """
        # Load all entity files
        entities_loaded = self.load_all_entities()
        
        # Resolve duplicates
        duplicates_resolved = self.resolve_duplicates()
        
        # Generate consolidated entities
        consolidated = self.generate_consolidated_entities()
        
        # Save consolidated entities
        self.save_consolidated_entities(consolidated)
        
        # Return results
        results = {
            'entities_loaded': entities_loaded,
            'duplicates_resolved': duplicates_resolved,
            'entity_counts': {entity_type: len(entities) for entity_type, entities in consolidated.items()},
            'total_entities': sum(len(entities) for entities in consolidated.values()),
            'ages': {
                age: sum(len(entities) for entities in age_entities.values())
                for age, age_entities in self.organize_by_age(consolidated).items()
            }
        }
        
        logger.info(f"Consolidation complete. {results['total_entities']} entities across {len(results['entity_counts'])} types.")
        
        return results


def consolidate_entities(input_dir, output_dir):
    """
    Consolidate entities from extracted entity files.
    
    Args:
        input_dir (str): Directory containing extracted entity files
        output_dir (str): Directory to save consolidated entities
        
    Returns:
        dict: Consolidation results
    """
    consolidator = EntityConsolidator(input_dir, output_dir)
    return consolidator.consolidate()


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Consolidate extracted entities")
    parser.add_argument("--input-dir", default="processing/json_output", help="Input directory containing extracted entities")
    parser.add_argument("--output-dir", default="processing/consolidated", help="Output directory for consolidated entities")
    args = parser.parse_args()
    
    consolidate_entities(args.input_dir, args.output_dir) 