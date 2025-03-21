"""
Entity Validation Module for Ages of Arda

This module validates entities against JSON schemas and provides
validation reports and summaries.
"""

import os
import json
import logging
import sys
from pathlib import Path
from collections import defaultdict
from typing import Dict, List, Any, Optional, Tuple

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join('processing', 'logs', 'validation.log')),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('validate')

# Import schema validator
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from processing.schema_validator import SchemaValidator

class EntityValidator:
    """
    Validator for Tolkien entities that provides detailed validation
    reports and supports different validation levels.
    """
    
    def __init__(self, schema_dir):
        """
        Initialize the entity validator.
        
        Args:
            schema_dir (str): Directory containing schema files
        """
        self.schema_validator = SchemaValidator(schema_dir)
        self.schema_dir = Path(schema_dir)
        
        # Define validation severity levels
        self.validation_levels = {
            'error': ['name', 'type'],  # Fields that must be valid
            'warning': ['description', 'content', 'age'],  # Fields that should be valid
            'info': ['alternate_names', 'relationships', 'attributes']  # Optional fields
        }
    
    def validate_entity(self, entity, entity_type=None, validation_level='error'):
        """
        Validate a single entity with custom validation level.
        
        Args:
            entity (dict): Entity data to validate
            entity_type (str, optional): Entity type (inferred from entity if None)
            validation_level (str): Validation level ('error', 'warning', 'info')
            
        Returns:
            Tuple[bool, List[Dict[str, Any]]]: (is_valid, list of validation issues)
        """
        # Use schema validator for basic validation
        is_valid, error_msg = self.schema_validator.validate_entity(entity, entity_type)
        
        # Create issues list with any schema validation errors
        issues = []
        if not is_valid:
            issues.append({
                'level': 'error',
                'message': error_msg,
                'field': 'schema'
            })
        
        # Perform additional validations based on level
        self._validate_additional_fields(entity, entity_type, issues)
        
        # Filter issues based on validation level
        filtered_issues = []
        for issue in issues:
            if issue['level'] == 'error' and validation_level in ['error', 'warning', 'info']:
                filtered_issues.append(issue)
            elif issue['level'] == 'warning' and validation_level in ['warning', 'info']:
                filtered_issues.append(issue)
            elif issue['level'] == 'info' and validation_level == 'info':
                filtered_issues.append(issue)
        
        # Entity is valid if there are no error-level issues
        is_valid = not any(issue['level'] == 'error' for issue in filtered_issues)
        
        return is_valid, filtered_issues
    
    def _validate_additional_fields(self, entity, entity_type, issues):
        """
        Perform additional validations beyond schema validation.
        
        Args:
            entity (dict): Entity data to validate
            entity_type (str): Entity type
            issues (list): List to add validation issues to
        """
        # Validate name field (not empty and reasonable length)
        name = entity.get('name', '')
        if not name:
            issues.append({
                'level': 'error',
                'message': 'Entity name is missing or empty',
                'field': 'name'
            })
        elif len(name) < 2:
            issues.append({
                'level': 'warning',
                'message': 'Entity name is unusually short',
                'field': 'name'
            })
        elif len(name) > 100:
            issues.append({
                'level': 'warning',
                'message': 'Entity name is unusually long',
                'field': 'name'
            })
        
        # Validate description (should be meaningful)
        description = entity.get('description', '')
        if not description:
            issues.append({
                'level': 'warning',
                'message': 'Entity description is missing or empty',
                'field': 'description'
            })
        elif len(description) < 10:
            issues.append({
                'level': 'warning',
                'message': 'Entity description is too short to be meaningful',
                'field': 'description'
            })
        
        # Validate content (should be substantial for important entities)
        if entity.get('is_canonical', False) and len(entity.get('content', '')) < 50:
            issues.append({
                'level': 'warning',
                'message': 'Canonical entity has minimal content',
                'field': 'content'
            })
        
        # Validate age field (should be recognized)
        age = entity.get('age', '').upper()
        valid_ages = ['FIRST_AGE', 'SECOND_AGE', 'THIRD_AGE', 'FOURTH_AGE']
        if age and age not in valid_ages:
            issues.append({
                'level': 'warning',
                'message': f'Unrecognized age value: {age}',
                'field': 'age'
            })
        
        # Entity type specific validations
        if entity_type == 'character':
            self._validate_character(entity, issues)
        elif entity_type == 'location':
            self._validate_location(entity, issues)
        elif entity_type == 'item':
            self._validate_item(entity, issues)
        elif entity_type == 'event':
            self._validate_event(entity, issues)
    
    def _validate_character(self, entity, issues):
        """
        Validate a character entity.
        
        Args:
            entity (dict): Character entity data
            issues (list): List to add validation issues to
        """
        # Check for race information
        if 'subtype' not in entity and 'race' not in entity.get('attributes', {}):
            issues.append({
                'level': 'info',
                'message': 'Character has no race or subtype information',
                'field': 'subtype'
            })
    
    def _validate_location(self, entity, issues):
        """
        Validate a location entity.
        
        Args:
            entity (dict): Location entity data
            issues (list): List to add validation issues to
        """
        # Check for location type information
        if 'subtype' not in entity:
            issues.append({
                'level': 'info',
                'message': 'Location has no subtype information',
                'field': 'subtype'
            })
    
    def _validate_item(self, entity, issues):
        """
        Validate an item entity.
        
        Args:
            entity (dict): Item entity data
            issues (list): List to add validation issues to
        """
        # Check for item type information
        if 'subtype' not in entity:
            issues.append({
                'level': 'info',
                'message': 'Item has no subtype information',
                'field': 'subtype'
            })
    
    def _validate_event(self, entity, issues):
        """
        Validate an event entity.
        
        Args:
            entity (dict): Event entity data
            issues (list): List to add validation issues to
        """
        # Events should have some temporal information
        time_keywords = ['year', 'age', 'time', 'era', 'during', 'after', 'before']
        
        has_time_info = False
        description = entity.get('description', '').lower()
        
        for keyword in time_keywords:
            if keyword in description:
                has_time_info = True
                break
        
        if not has_time_info:
            issues.append({
                'level': 'warning',
                'message': 'Event lacks temporal information',
                'field': 'description'
            })
    
    def validate_file(self, file_path, validation_level='error'):
        """
        Validate a JSON file containing entity data.
        
        Args:
            file_path (str): Path to the JSON file
            validation_level (str): Validation level
            
        Returns:
            Tuple[bool, Dict[str, Any]]: (is_valid, validation results)
        """
        try:
            file_path = Path(file_path)
            
            with open(file_path, 'r', encoding='utf-8') as f:
                entity = json.load(f)
            
            # Determine entity type from filename or entity data
            entity_type = None
            
            # Try to infer from filename (e.g., "characters.json" -> "character")
            stem = file_path.stem
            if stem.endswith('s') and len(stem) > 1:
                entity_type = stem[:-1]
            
            # If couldn't infer from filename, try to get from entity data
            if not entity_type:
                entity_type = entity.get('type', '').lower()
            
            is_valid, issues = self.validate_entity(entity, entity_type, validation_level)
            
            return is_valid, {
                'file': str(file_path),
                'entity_name': entity.get('name', 'Unknown'),
                'entity_type': entity_type,
                'is_valid': is_valid,
                'issues': issues
            }
        
        except Exception as e:
            logger.error(f"Error validating file {file_path}: {str(e)}")
            return False, {
                'file': str(file_path),
                'is_valid': False,
                'issues': [{
                    'level': 'error',
                    'message': f"Failed to validate file: {str(e)}",
                    'field': 'file'
                }]
            }
    
    def validate_directory(self, directory, recursive=True, validation_level='error'):
        """
        Validate all JSON files in a directory.
        
        Args:
            directory (str): Directory containing entity files
            recursive (bool): Whether to search subdirectories
            validation_level (str): Validation level
            
        Returns:
            Dict[str, Any]: Validation results
        """
        directory = Path(directory)
        pattern = '**/*.json' if recursive else '*.json'
        
        logger.info(f"Validating files in {directory}")
        
        # Find all JSON files
        json_files = list(directory.glob(pattern))
        
        if not json_files:
            logger.warning(f"No JSON files found in {directory}")
            return {
                'valid': [],
                'invalid': [],
                'summary': {
                    'total': 0,
                    'valid': 0,
                    'invalid': 0,
                    'issues_by_level': {'error': 0, 'warning': 0, 'info': 0},
                    'issues_by_field': {}
                }
            }
        
        results = {
            'valid': [],
            'invalid': [],
            'all_results': []
        }
        
        # Validate each file
        for file_path in json_files:
            is_valid, file_result = self.validate_file(file_path, validation_level)
            
            results['all_results'].append(file_result)
            
            if is_valid:
                results['valid'].append(file_result)
                logger.info(f"Valid: {file_path}")
            else:
                results['invalid'].append(file_result)
                logger.warning(f"Invalid: {file_path} - {len(file_result['issues'])} issues")
        
        # Generate summary
        results['summary'] = self._generate_summary(results['all_results'])
        
        logger.info(f"Validation complete: {results['summary']['valid']} valid, {results['summary']['invalid']} invalid")
        
        return results
    
    def _generate_summary(self, validation_results):
        """
        Generate a summary of validation results.
        
        Args:
            validation_results (list): List of validation results
            
        Returns:
            Dict[str, Any]: Summary statistics
        """
        summary = {
            'total': len(validation_results),
            'valid': sum(1 for r in validation_results if r['is_valid']),
            'invalid': sum(1 for r in validation_results if not r['is_valid']),
            'issues_by_level': defaultdict(int),
            'issues_by_field': defaultdict(int),
            'issues_by_type': defaultdict(int)
        }
        
        # Count issues by level, field, and entity type
        for result in validation_results:
            entity_type = result.get('entity_type', 'unknown')
            
            for issue in result.get('issues', []):
                level = issue.get('level', 'error')
                field = issue.get('field', 'unknown')
                
                summary['issues_by_level'][level] += 1
                summary['issues_by_field'][field] += 1
                summary['issues_by_type'][entity_type] += 1
        
        return summary
    
    def save_validation_results(self, results, output_file):
        """
        Save validation results to a JSON file.
        
        Args:
            results (dict): Validation results
            output_file (str): Path to save results to
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            output_file = Path(output_file)
            output_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Saved validation results to {output_file}")
            return True
            
        except Exception as e:
            logger.error(f"Error saving validation results: {str(e)}")
            return False
    
    def print_validation_summary(self, results):
        """
        Print a summary of validation results to the console.
        
        Args:
            results (dict): Validation results
        """
        summary = results['summary']
        
        print("\nValidation Summary:")
        print("===================")
        print(f"Total entities: {summary['total']}")
        print(f"Valid entities: {summary['valid']} ({summary['valid'] * 100 / summary['total']:.1f}%)")
        print(f"Invalid entities: {summary['invalid']} ({summary['invalid'] * 100 / summary['total']:.1f}%)")
        
        if summary['issues_by_level']:
            print("\nIssues by severity:")
            for level, count in summary['issues_by_level'].items():
                print(f"  {level.capitalize()}: {count}")
        
        if summary['issues_by_field']:
            print("\nIssues by field:")
            for field, count in sorted(summary['issues_by_field'].items(), key=lambda x: x[1], reverse=True)[:5]:
                print(f"  {field}: {count}")
        
        if summary['issues_by_type']:
            print("\nIssues by entity type:")
            for entity_type, count in sorted(summary['issues_by_type'].items(), key=lambda x: x[1], reverse=True):
                print(f"  {entity_type}: {count}")
        
        if results['invalid']:
            print("\nTop issues:")
            for i, invalid in enumerate(results['invalid'][:5]):
                print(f"  {i+1}. {invalid['entity_name']} ({invalid['entity_type']}): {len(invalid['issues'])} issues")
                for j, issue in enumerate(invalid['issues'][:3]):
                    print(f"     - {issue['level'].upper()}: {issue['message']}")


def validate_entities(input_dir, schema_dir, output_file=None, validation_level='error'):
    """
    Validate entities in the input directory against schemas.
    
    Args:
        input_dir (str): Directory containing entity files
        schema_dir (str): Directory containing schema files
        output_file (str, optional): File to save validation results
        validation_level (str): Validation level ('error', 'warning', 'info')
        
    Returns:
        Dict[str, Any]: Validation results
    """
    validator = EntityValidator(schema_dir)
    results = validator.validate_directory(input_dir, recursive=True, validation_level=validation_level)
    
    if output_file:
        validator.save_validation_results(results, output_file)
    
    validator.print_validation_summary(results)
    
    return results


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Validate entities against schemas")
    parser.add_argument("--input-dir", default="processing/json_output", help="Input directory containing entity files")
    parser.add_argument("--schema-dir", default="processing/schemas", help="Directory containing schema files")
    parser.add_argument("--output-file", default="processing/validation_results.json", help="File to save validation results")
    parser.add_argument("--level", choices=['error', 'warning', 'info'], default='error', help="Validation level")
    args = parser.parse_args()
    
    validate_entities(args.input_dir, args.schema_dir, args.output_file, args.level) 