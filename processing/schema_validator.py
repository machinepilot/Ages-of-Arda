"""
Schema Validator for Ages of Arda

This module provides functionality for validating generated JSON entities
against the defined schemas for the Ages of Arda Memory Bank system.
"""

import os
import json
import logging
from pathlib import Path

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join('processing', 'logs', 'schema_validation.log')),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('schema_validator')

class SchemaValidator:
    """
    Validator for ensuring generated JSON entities conform to the defined schemas.
    """
    
    def __init__(self, schema_dir):
        """
        Initialize the schema validator.
        
        Args:
            schema_dir (str): Directory containing schema files
        """
        self.schema_dir = Path(schema_dir)
        self.schemas = {}
        self._load_schemas()
    
    def _load_schemas(self):
        """Load all schema files from the schema directory"""
        try:
            schema_files = list(self.schema_dir.glob('*.json'))
            logger.info(f"Found {len(schema_files)} schema files in {self.schema_dir}")
            
            for schema_file in schema_files:
                schema_name = schema_file.stem
                with open(schema_file, 'r', encoding='utf-8') as f:
                    schema_data = json.load(f)
                    self.schemas[schema_name] = schema_data
                logger.info(f"Loaded schema: {schema_name}")
            
        except Exception as e:
            logger.error(f"Error loading schemas: {str(e)}")
    
    def get_schema_for_entity_type(self, entity_type):
        """
        Get the appropriate schema for a given entity type.
        
        Args:
            entity_type (str): Entity type (character, location, item, event)
            
        Returns:
            dict: Schema data for the entity type
        """
        schema_name = f"{entity_type}_schema"
        if schema_name in self.schemas:
            return self.schemas[schema_name]
        
        # Try alternative names
        if entity_type == "artifact" and "item_schema" in self.schemas:
            return self.schemas["item_schema"]
        
        logger.warning(f"No schema found for entity type: {entity_type}")
        return None
    
    def validate_entity(self, entity, entity_type=None):
        """
        Validate an entity against its schema.
        
        Args:
            entity (dict): Entity data to validate
            entity_type (str, optional): Entity type. If None, determined from entity data
            
        Returns:
            tuple: (is_valid, error_message)
        """
        # Determine entity type if not provided
        if entity_type is None:
            entity_type = entity.get('type', '').lower()
            if not entity_type:
                return False, "Entity has no type field"
        
        # Get schema for this entity type
        schema = self.get_schema_for_entity_type(entity_type)
        if not schema:
            return False, f"No schema available for type: {entity_type}"
        
        # Validate required fields
        if 'required' in schema:
            for field in schema['required']:
                if field not in entity:
                    return False, f"Missing required field: {field}"
        
        # Validate field types
        if 'properties' in schema:
            for field, field_schema in schema['properties'].items():
                if field in entity:
                    valid, error = self._validate_field(entity[field], field_schema, field)
                    if not valid:
                        return False, error
        
        return True, None
    
    def _validate_field(self, field_value, field_schema, field_name):
        """
        Validate a single field against its schema.
        
        Args:
            field_value: Value of the field
            field_schema (dict): Schema for the field
            field_name (str): Name of the field
            
        Returns:
            tuple: (is_valid, error_message)
        """
        # Check type
        if 'type' in field_schema:
            field_type = field_schema['type']
            
            # Handle union types
            if isinstance(field_type, list):
                valid_type = False
                for t in field_type:
                    if self._check_type(field_value, t):
                        valid_type = True
                        break
                if not valid_type:
                    return False, f"Field '{field_name}' with value '{field_value}' is not one of the allowed types: {field_type}"
            else:
                if not self._check_type(field_value, field_type):
                    return False, f"Field '{field_name}' with value '{field_value}' is not of type {field_type}"
        
        # Check enum values
        if 'enum' in field_schema and field_value not in field_schema['enum']:
            return False, f"Field '{field_name}' with value '{field_value}' is not one of the allowed values: {field_schema['enum']}"
        
        # Validate array items
        if field_schema.get('type') == 'array' and isinstance(field_value, list) and 'items' in field_schema:
            for i, item in enumerate(field_value):
                valid, error = self._validate_field(item, field_schema['items'], f"{field_name}[{i}]")
                if not valid:
                    return False, error
        
        # Validate object properties
        if field_schema.get('type') == 'object' and isinstance(field_value, dict) and 'properties' in field_schema:
            for prop_name, prop_schema in field_schema['properties'].items():
                if prop_name in field_value:
                    valid, error = self._validate_field(field_value[prop_name], prop_schema, f"{field_name}.{prop_name}")
                    if not valid:
                        return False, error
        
        return True, None
    
    def _check_type(self, value, expected_type):
        """
        Check if a value matches the expected type.
        
        Args:
            value: Value to check
            expected_type (str): Expected type name
            
        Returns:
            bool: True if the value matches the expected type
        """
        if expected_type == 'string':
            return isinstance(value, str)
        elif expected_type == 'number':
            return isinstance(value, (int, float)) and not isinstance(value, bool)
        elif expected_type == 'integer':
            return isinstance(value, int) and not isinstance(value, bool)
        elif expected_type == 'boolean':
            return isinstance(value, bool)
        elif expected_type == 'array':
            return isinstance(value, list)
        elif expected_type == 'object':
            return isinstance(value, dict)
        elif expected_type == 'null':
            return value is None
        
        return False
    
    def validate_file(self, file_path):
        """
        Validate a JSON file against its schema.
        
        Args:
            file_path (str): Path to JSON file
            
        Returns:
            tuple: (is_valid, error_message)
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                entity = json.load(f)
            
            return self.validate_entity(entity)
        except Exception as e:
            return False, f"Error validating file {file_path}: {str(e)}"
    
    def validate_directory(self, directory, recursive=True):
        """
        Validate all JSON files in a directory.
        
        Args:
            directory (str): Directory to validate
            recursive (bool): Whether to recursively validate subdirectories
            
        Returns:
            dict: Validation results
        """
        results = {
            'valid': [],
            'invalid': []
        }
        
        directory = Path(directory)
        
        # Find all JSON files
        pattern = '**/*.json' if recursive else '*.json'
        json_files = list(directory.glob(pattern))
        logger.info(f"Found {len(json_files)} JSON files in {directory}")
        
        for json_file in json_files:
            valid, error = self.validate_file(json_file)
            if valid:
                results['valid'].append(str(json_file))
                logger.info(f"Validated: {json_file}")
            else:
                results['invalid'].append({
                    'file': str(json_file),
                    'error': error
                })
                logger.warning(f"Validation failed for {json_file}: {error}")
        
        logger.info(f"Validation complete. Valid: {len(results['valid'])}, Invalid: {len(results['invalid'])}")
        return results


def validate_entities(entity_dir, schema_dir, output_file=None):
    """
    Validate all entity files in a directory.
    
    Args:
        entity_dir (str): Directory containing entity files
        schema_dir (str): Directory containing schema files
        output_file (str, optional): File to save validation results
        
    Returns:
        dict: Validation results
    """
    validator = SchemaValidator(schema_dir)
    results = validator.validate_directory(entity_dir)
    
    if output_file:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2)
        logger.info(f"Validation results saved to {output_file}")
    
    return results


if __name__ == "__main__":
    entity_directory = os.path.join('processing', 'json_output')
    schema_directory = os.path.join('processing', 'schemas')
    output_file = os.path.join('processing', 'validation_results.json')
    
    validate_entities(entity_directory, schema_directory, output_file) 