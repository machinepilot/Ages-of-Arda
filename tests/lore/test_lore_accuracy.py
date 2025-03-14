#!/usr/bin/env python3
"""
test_lore_accuracy.py - Tests for the lore management system accuracy
"""

import os
import sys
import json
import unittest
from pathlib import Path

# Add the src directory to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../src')))

try:
    from mcp.lore.lore_integration import LoreIntegration
except ImportError:
    print("Error: Could not import LoreIntegration. Make sure the src directory is in your Python path.")
    sys.exit(1)

class TestLoreAccuracy(unittest.TestCase):
    """Test suite for validating lore accuracy and consistency"""
    
    @classmethod
    def setUpClass(cls):
        """Set up the test environment once for all tests"""
        # Get the path to the memory bank
        cls.memory_bank_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../memory-bank'))
        
        # Initialize the lore integration
        cls.lore = LoreIntegration(memory_bank_path=cls.memory_bank_path)
        
        # Scan the lore directory to find all lore entries
        cls.lore_entries = {}
        cls.scan_lore_entries()
    
    @classmethod
    def scan_lore_entries(cls):
        """Scan the lore directory to find all lore entries"""
        lore_dir = os.path.join(cls.memory_bank_path, 'lore')
        
        for age_dir in os.listdir(lore_dir):
            age_path = os.path.join(lore_dir, age_dir)
            
            if not os.path.isdir(age_path) or age_dir.startswith('.'):
                continue
                
            cls.lore_entries[age_dir] = {
                'characters': [],
                'locations': [],
                'artifacts': [],
                'events': []
            }
            
            # Scan each entity type directory
            for entity_type in cls.lore_entries[age_dir].keys():
                entity_dir = os.path.join(age_path, entity_type)
                
                if not os.path.exists(entity_dir) or not os.path.isdir(entity_dir):
                    continue
                    
                for entry_file in os.listdir(entity_dir):
                    if entry_file.endswith('.json'):
                        entry_path = os.path.join(entity_dir, entry_file)
                        try:
                            with open(entry_path, 'r', encoding='utf-8') as f:
                                entry_data = json.load(f)
                                cls.lore_entries[age_dir][entity_type].append(entry_data)
                        except json.JSONDecodeError:
                            print(f"Warning: Could not parse JSON in {entry_path}")
    
    def test_character_lore_retrieval(self):
        """Test that character lore can be retrieved correctly"""
        # Test for each age and character
        for age, entities in self.lore_entries.items():
            for character_data in entities['characters']:
                character_name = character_data['name']
                
                # Get the character lore using the API
                retrieved_lore = self.lore.get_character_lore(character_name, age=age)
                
                # Verify the lore was retrieved
                self.assertIsNotNone(retrieved_lore, f"Could not retrieve lore for {character_name} in {age}")
                
                # Verify key fields match
                self.assertEqual(retrieved_lore['name'], character_data['name'])
                self.assertEqual(retrieved_lore['description'], character_data['description'])
                self.assertEqual(retrieved_lore['source'], character_data['source'])
                self.assertEqual(retrieved_lore['is_canonical'], character_data['is_canonical'])
    
    def test_location_lore_retrieval(self):
        """Test that location lore can be retrieved correctly"""
        # Test for each age and location
        for age, entities in self.lore_entries.items():
            for location_data in entities['locations']:
                location_name = location_data['name']
                
                # Get the location lore using the API
                retrieved_lore = self.lore.get_location_lore(location_name, age=age)
                
                # Verify the lore was retrieved
                self.assertIsNotNone(retrieved_lore, f"Could not retrieve lore for {location_name} in {age}")
                
                # Verify key fields match
                self.assertEqual(retrieved_lore['name'], location_data['name'])
                self.assertEqual(retrieved_lore['description'], location_data['description'])
                self.assertEqual(retrieved_lore['source'], location_data['source'])
                self.assertEqual(retrieved_lore['is_canonical'], location_data['is_canonical'])
    
    def test_lore_source_attribution(self):
        """Test that all lore entries have proper source attribution"""
        for age, entities in self.lore_entries.items():
            for entity_type, entries in entities.items():
                for entry in entries:
                    # Verify source field exists and is not empty
                    self.assertIn('source', entry, f"Missing source in {entry['name']}")
                    self.assertTrue(entry['source'], f"Empty source in {entry['name']}")
    
    def test_canonical_flag_consistency(self):
        """Test that the canonical flag is consistent with the source"""
        for age, entities in self.lore_entries.items():
            for entity_type, entries in entities.items():
                for entry in entries:
                    # Verify is_canonical field exists
                    self.assertIn('is_canonical', entry, f"Missing is_canonical in {entry['name']}")
                    
                    # If source is from Tolkien's works, it should be canonical
                    if any(source in entry['source'] for source in 
                          ['The Silmarillion', 'The Lord of the Rings', 'The Hobbit', 
                           'Unfinished Tales', 'The Children of Húrin']):
                        self.assertTrue(entry['is_canonical'], 
                                       f"{entry['name']} should be canonical with source {entry['source']}")

if __name__ == '__main__':
    unittest.main() 