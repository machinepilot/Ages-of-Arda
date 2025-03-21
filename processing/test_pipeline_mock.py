"""
Test Pipeline for Ages of Arda ePub Processing Framework (Mock Version)

This module provides a comprehensive testing infrastructure for the framework
using mock implementations to avoid external dependencies.
"""

import os
import sys
import json
import unittest
import tempfile
import shutil
import logging
from pathlib import Path
from datetime import datetime
from unittest.mock import patch, MagicMock

# Import and configure path_config first
from processing.path_config import set_environment, Environment, get_path, get_log_file_path

# Set test environment at the start
set_environment(Environment.TEST)

# Set up logging using path_config
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(get_log_file_path('test_pipeline_mock')),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('test_pipeline_mock')

# Import the mock entity extractor
from processing.mock_entity_extractor import EntityExtractor, OllamaClient, EntityStore

class TestBase(unittest.TestCase):
    """Base class for all test cases, providing common setup and teardown."""
    
    def setUp(self):
        """Set up test environment with temporary directories."""
        self.test_dir = tempfile.mkdtemp()
        self.test_data_dir = os.path.join(self.test_dir, 'test_data')
        self.test_output_dir = os.path.join(self.test_dir, 'test_output')
        self.test_temp_dir = os.path.join(self.test_dir, 'test_temp')
        self.schema_dir = os.path.join(self.test_dir, 'schemas')
        
        # Create necessary directories
        os.makedirs(self.test_data_dir, exist_ok=True)
        os.makedirs(self.test_output_dir, exist_ok=True)
        os.makedirs(self.test_temp_dir, exist_ok=True)
        os.makedirs(self.schema_dir, exist_ok=True)
        
        # Set up test data
        self.setup_test_data()
        
    def tearDown(self):
        """Clean up temporary files and directories."""
        shutil.rmtree(self.test_dir)
        
    def setup_test_data(self):
        """Create sample test data - override in subclasses."""
        pass
    
    def create_test_entity(self, entity_type, name, attributes=None):
        """Create a test entity dictionary."""
        if attributes is None:
            attributes = {}
            
        entity = {
            "id": f"{entity_type.lower()}_{name.lower().replace(' ', '_')}",
            "name": name,
            "type": entity_type,
            "attributes": attributes,
            "sources": [{"book": "Test Book", "chapter": "Test Chapter", "context": "Test context"}],
            "confidence": 0.9
        }
        return entity
        
    def generate_test_report(self, test_results):
        """Generate a test report."""
        report = {
            "timestamp": datetime.now().isoformat(),
            "total_tests": len(test_results),
            "passed": sum(1 for result in test_results if result["status"] == "PASS"),
            "failed": sum(1 for result in test_results if result["status"] == "FAIL"),
            "results": test_results
        }
        
        report_path = os.path.join(self.test_output_dir, "test_report.json")
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2)
            
        return report_path


class TestEntityExtractor(TestBase):
    """Tests for the Entity Extractor component."""
    
    def setup_test_data(self):
        """Set up test data for entity extraction."""
        self.test_chapter_dir = os.path.join(self.test_data_dir, 'chapters')
        os.makedirs(self.test_chapter_dir, exist_ok=True)
        
        # Create test chapter file
        chapter_content = {
            "title": "The Fellowship of the Ring",
            "content": "Frodo Baggins lived in Bag End. Gandalf visited him in the Shire.",
            "metadata": {
                "book": "The Lord of the Rings",
                "chapter_number": 1,
                "age": "Third Age"
            }
        }
        
        self.test_chapter_path = os.path.join(self.test_chapter_dir, 'chapter1.json')
        with open(self.test_chapter_path, 'w') as f:
            json.dump(chapter_content, f)
            
    def test_entity_extraction(self):
        """Test entity extraction from text."""
        # Create extractor (no mocking needed - using our mock implementation)
        extractor = EntityExtractor(self.test_output_dir)
        
        # Test the extraction process
        with open(self.test_chapter_path) as f:
            chapter = json.load(f)
            
        entities = extractor.extract_entities_from_chapter(chapter)
        
        # Verify the results
        self.assertGreater(len(entities), 0)
        # Our mock implementation should return Frodo and Gandalf entities
        character_names = [e["name"] for e in entities if e["type"] == "CHARACTER"]
        self.assertIn("Frodo Baggins", character_names)
        self.assertIn("Gandalf", character_names)


class TestOllamaClient(TestBase):
    """Tests for the Ollama client."""
    
    def test_generate(self):
        """Test text generation using the mock Ollama client."""
        client = OllamaClient()
        
        # Test character prompt
        character_response = client.generate("Extract character entities from text")
        self.assertIn("Frodo Baggins", character_response)
        self.assertIn("Gandalf", character_response)
        
        # Test location prompt
        location_response = client.generate("Extract location entities from text")
        self.assertIn("Bag End", location_response)
        self.assertIn("Shire", location_response)
        
    def test_is_available(self):
        """Test checking if Ollama is available."""
        client = OllamaClient()
        self.assertTrue(client.is_available())  # Mock always returns True


class TestEntityStore(TestBase):
    """Tests for the Entity Store."""
    
    def test_add_entity(self):
        """Test adding an entity to the store."""
        store = EntityStore(self.test_output_dir)
        
        entity = self.create_test_entity("CHARACTER", "Frodo Baggins", {"race": "Hobbit"})
        entity_id = store.add_entity(entity)
        
        # Verify entity was added
        stored_entity = store.get_entity(entity_id)
        self.assertEqual(stored_entity["name"], "Frodo Baggins")
        self.assertEqual(stored_entity["type"], "CHARACTER")
        
    def test_get_entities_by_type(self):
        """Test retrieving entities by type."""
        store = EntityStore(self.test_output_dir)
        
        # Add entities
        store.add_entity(self.create_test_entity("CHARACTER", "Frodo Baggins"))
        store.add_entity(self.create_test_entity("CHARACTER", "Gandalf"))
        store.add_entity(self.create_test_entity("LOCATION", "Bag End"))
        
        # Get entities by type
        characters = store.get_entities_by_type("CHARACTER")
        self.assertEqual(len(characters), 2)
        
        locations = store.get_entities_by_type("LOCATION")
        self.assertEqual(len(locations), 1)


if __name__ == '__main__':
    unittest.main() 