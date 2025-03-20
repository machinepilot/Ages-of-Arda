"""
Entity Consolidator for Ages of Arda

This module provides functionality for consolidating entities extracted from
different chapters and books, resolving duplicates and merging related information.
"""

import os
import json
import logging
from pathlib import Path
from collections import defaultdict

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
                'sources': []
            }
        
        # Add description
        if 'description' in entity and entity['description']:
            self.entities_by_type[entity_type][name_key]['descriptions'].append(entity['description'])
        
        # Add mentions/aliases
        if 'mentions' in entity and entity['mentions']:
            for mention in entity['mentions']:
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
    
    def load_all_entities(self):
        """
        Load all entity files from the input directory.
        
        Returns:
            int: Number of files processed
        """
        # Find all entity files
        entity_files = list(self.input_dir.glob('**/*_entities.json'))
        logger.info(f"Found {len(entity_files)} entity files in {self.input_dir}")
        
        # Process each file
        processed_count = 0
        for entity_file in entity_files:
            try:
                metadata, entities = self.load_entities_from_file(entity_file)
                
                # Process entities by type
                for entity_type, entity_list in entities.items():
                    for entity in entity_list:
                        self.process_entity(entity, entity_type, metadata)
                
                processed_count += 1
                logger.debug(f"Processed entities from {entity_file}")
                
            except Exception as e:
                logger.error(f"Error processing {entity_file}: {str(e)}")
        
        logger.info(f"Processed {processed_count} entity files")
        
        # Report entity counts by type
        for entity_type, entities in self.entities_by_type.items():
            logger.info(f"Found {len(entities)} unique {entity_type} entities")
        
        return processed_count
    
    def resolve_duplicates(self):
        """
        Resolve duplicate entities based on name similarity and aliases.
        
        Returns:
            int: Number of duplicates resolved
        """
        # This is a simplified approach to duplicate resolution
        # A more sophisticated approach might use fuzzy matching, edit distance, etc.
        
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
        
        logger.info(f"Resolved {duplicates_resolved} duplicate entities")
        return duplicates_resolved
    
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
                # Select the best description
                descriptions = entity['descriptions']
                best_description = max(descriptions, key=len) if descriptions else ""
                
                # Format data for output
                consolidated_entity = {
                    'name': entity['name'],
                    'type': entity_type,
                    'description': best_description,
                    'content': self._generate_content(entity, descriptions),
                    'mentions': list(entity['mentions']),
                    'related': list(entity['related']),
                    'sources': entity['sources'],
                    'source': self._generate_source_reference(entity['sources']),
                    'age': self._determine_primary_age(entity['sources']),
                    'is_canonical': True  # All extracted entities are considered canonical
                }
                
                consolidated[entity_type].append(consolidated_entity)
        
        return consolidated
    
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
    
    def _determine_primary_age(self, sources):
        """
        Determine the primary age for an entity.
        
        Args:
            sources (list): List of source metadata
            
        Returns:
            str: Primary age
        """
        if not sources:
            return "unknown"
        
        # Count occurrences of each age
        age_counts = {}
        for source in sources:
            age = source.get('age', 'unknown')
            age_counts[age] = age_counts.get(age, 0) + 1
        
        # Return the most common age
        return max(age_counts, key=age_counts.get)
    
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
        
        # Create a summary file
        summary = {
            'total_entities': sum(len(entities) for entities in consolidated.values()),
            'entity_counts': {entity_type: len(entities) for entity_type, entities in consolidated.items()},
            'entity_files': {entity_type: f"{entity_type}s.json" for entity_type in consolidated.keys()}
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
        files_processed = self.load_all_entities()
        
        # Resolve duplicates
        duplicates_resolved = self.resolve_duplicates()
        
        # Generate consolidated entities
        consolidated = self.generate_consolidated_entities()
        
        # Save consolidated entities
        self.save_consolidated_entities(consolidated)
        
        # Return results
        results = {
            'files_processed': files_processed,
            'duplicates_resolved': duplicates_resolved,
            'entity_counts': {entity_type: len(entities) for entity_type, entities in consolidated.items()},
            'total_entities': sum(len(entities) for entities in consolidated.values())
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