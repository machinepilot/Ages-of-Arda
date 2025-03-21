"""
Test Pipeline for Ages of Arda ePub Processing Framework

This module provides a comprehensive testing infrastructure for all components
of the Tolkien ePub Processing Framework.
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

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join('logs', 'test.log')),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('test_pipeline')

# Import the modules to be tested
from epub_processor import EpubProcessor, process_epub_file
from entity_extractor import EntityExtractor, OllamaClient, EntityStore
from entity_consolidator import EntityConsolidator
from memory_bank_integrator import MemoryBankIntegrator
from validate import SchemaValidator, MemoryBankValidator
from main import Pipeline

class TestBase(unittest.TestCase):
    """Base class for all test cases, providing common setup and teardown."""
    
    def setUp(self):
        """Set up test environment with temporary directories."""
        self.test_dir = tempfile.mkdtemp()
        self.test_data_dir = os.path.join(self.test_dir, 'test_data')
        self.test_output_dir = os.path.join(self.test_dir, 'test_output')
        self.test_temp_dir = os.path.join(self.test_dir, 'test_temp')
        
        # Create necessary directories
        os.makedirs(self.test_data_dir, exist_ok=True)
        os.makedirs(self.test_output_dir, exist_ok=True)
        os.makedirs(self.test_temp_dir, exist_ok=True)
        
        # Set up test data
        self.setup_test_data()
        
    def tearDown(self):
        """Clean up temporary files and directories."""
        shutil.rmtree(self.test_dir)
        
    def setup_test_data(self):
        """Create sample test data - override in subclasses."""
        pass
    
    def create_test_epub(self, epub_path, content):
        """Create a simplified test ePub file structure."""
        # This is a simplified version - in real tests, create actual epub files
        os.makedirs(os.path.dirname(epub_path), exist_ok=True)
        with open(epub_path, 'w') as f:
            f.write(content)
            
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


class TestEpubProcessor(TestBase):
    """Tests for the ePub Processor component."""
    
    def setup_test_data(self):
        """Set up test ePub files."""
        self.test_epub_dir = os.path.join(self.test_data_dir, 'epubs')
        os.makedirs(self.test_epub_dir, exist_ok=True)
        
        # Create a simple mock ePub
        self.test_epub_path = os.path.join(self.test_epub_dir, 'test_book.epub')
        self.create_test_epub(self.test_epub_path, "Test ePub content")
        
    def test_init(self):
        """Test initialization of EpubProcessor."""
        processor = EpubProcessor(self.test_epub_path, self.test_output_dir, self.test_temp_dir)
        self.assertEqual(Path(self.test_epub_path), processor.epub_path)
        self.assertEqual(Path(self.test_output_dir), processor.output_dir)
        
    @patch('epub_processor.EpubProcessor.extract_epub')
    @patch('epub_processor.EpubProcessor.find_content_files')
    @patch('epub_processor.EpubProcessor.extract_text_from_content_files')
    @patch('epub_processor.EpubProcessor.save_chapters')
    def test_process(self, mock_save, mock_extract_text, mock_find, mock_extract):
        """Test the full processing pipeline with mocks."""
        # Configure mocks
        mock_extract.return_value = None
        mock_find.return_value = ['content1.html', 'content2.html']
        mock_extract_text.return_value = [
            {"title": "Chapter 1", "content": "Chapter 1 content"},
            {"title": "Chapter 2", "content": "Chapter 2 content"}
        ]
        mock_save.return_value = None
        
        # Test the process method
        processor = EpubProcessor(self.test_epub_path, self.test_output_dir, self.test_temp_dir)
        result = processor.process()
        
        # Verify all methods were called
        mock_extract.assert_called_once()
        mock_find.assert_called_once()
        mock_extract_text.assert_called_once()
        mock_save.assert_called_once()


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
            
    @patch('entity_extractor.OllamaClient')
    def test_entity_extraction(self, mock_ollama):
        """Test entity extraction from text."""
        # Configure the mock
        mock_ollama_instance = MagicMock()
        mock_ollama.return_value = mock_ollama_instance
        mock_ollama_instance.generate.return_value = json.dumps({
            "entities": [
                {
                    "name": "Frodo Baggins",
                    "type": "CHARACTER",
                    "subtype": "HOBBIT",
                    "confidence": 0.95,
                    "context": "Frodo Baggins lived in Bag End."
                },
                {
                    "name": "Bag End",
                    "type": "LOCATION",
                    "subtype": "STRUCTURE",
                    "confidence": 0.9,
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
                    "name": "Shire",
                    "type": "LOCATION",
                    "subtype": "REGION",
                    "confidence": 0.97,
                    "context": "Gandalf visited him in the Shire."
                }
            ]
        })
        
        # Create extractor with mocked client
        extractor = EntityExtractor(self.test_output_dir, ollama_client=mock_ollama_instance)
        
        # Call the extraction method
        with patch.object(extractor, '_extract_relationships', return_value=[]):
            result = extractor.extract_entities_from_text(
                "Frodo Baggins lived in Bag End. Gandalf visited him in the Shire.",
                {"book": "Test Book", "chapter": "Test Chapter"}
            )
        
        # Verify the results
        self.assertEqual(len(result["entities"]), 4)
        character_entities = [e for e in result["entities"] if e["type"] == "CHARACTER"]
        location_entities = [e for e in result["entities"] if e["type"] == "LOCATION"]
        self.assertEqual(len(character_entities), 2)
        self.assertEqual(len(location_entities), 2)


class TestEntityConsolidator(TestBase):
    """Tests for the Entity Consolidator component."""
    
    def setup_test_data(self):
        """Set up test data for entity consolidation."""
        # Create test entity files
        self.entity_dir = os.path.join(self.test_data_dir, 'entities')
        os.makedirs(self.entity_dir, exist_ok=True)
        
        # Create some test entities
        entities = [
            self.create_test_entity("CHARACTER", "Frodo Baggins", {"race": "Hobbit"}),
            self.create_test_entity("CHARACTER", "Frodo", {"race": "Hobbit"}),  # Duplicate
            self.create_test_entity("LOCATION", "Bag End", {"region": "The Shire"}),
            self.create_test_entity("CHARACTER", "Gandalf", {"race": "Maiar"}),
            self.create_test_entity("CHARACTER", "Gandalf the Grey", {"race": "Maiar"})  # Duplicate
        ]
        
        # Save test entities
        for i, entity in enumerate(entities):
            with open(os.path.join(self.entity_dir, f"entity_{i}.json"), 'w') as f:
                json.dump(entity, f)
    
    def test_entity_consolidation(self):
        """Test entity consolidation process."""
        consolidator = EntityConsolidator(self.entity_dir, self.test_output_dir)
        
        # Mock the methods that would require complex processing
        with patch.object(consolidator, '_load_entities', return_value=[
                self.create_test_entity("CHARACTER", "Frodo Baggins", {"race": "Hobbit"}),
                self.create_test_entity("CHARACTER", "Frodo", {"race": "Hobbit"}),
                self.create_test_entity("LOCATION", "Bag End", {"region": "The Shire"}),
                self.create_test_entity("CHARACTER", "Gandalf", {"race": "Maiar"}),
                self.create_test_entity("CHARACTER", "Gandalf the Grey", {"race": "Maiar"})
            ]):
            with patch.object(consolidator, '_find_duplicate_entities') as mock_find_duplicates:
                # Set up the mock to return some duplicate groupings
                mock_find_duplicates.return_value = [
                    [0, 1],  # Frodo Baggins and Frodo
                    [3, 4]   # Gandalf and Gandalf the Grey
                ]
                
                # Run consolidation
                result = consolidator.consolidate()
                
                # Verify results
                self.assertIsNotNone(result)
                # In a real test, we would check the actual consolidation logic
                # Here we're just verifying the method was called
                mock_find_duplicates.assert_called_once()


class TestMemoryBankIntegrator(TestBase):
    """Tests for the Memory Bank Integrator component."""
    
    def setup_test_data(self):
        """Set up test data for memory bank integration."""
        # Create test consolidated entities
        self.consolidated_dir = os.path.join(self.test_data_dir, 'consolidated')
        os.makedirs(self.consolidated_dir, exist_ok=True)
        
        # Create some test consolidated entities
        entities = [
            self.create_test_entity("CHARACTER", "Frodo Baggins", {"race": "Hobbit", "age": "Third Age"}),
            self.create_test_entity("LOCATION", "Bag End", {"region": "The Shire", "age": "Third Age"}),
            self.create_test_entity("CHARACTER", "Gandalf", {"race": "Maiar", "age": "All Ages"})
        ]
        
        # Add relationships
        for entity in entities:
            entity["relationships"] = []
        
        entities[0]["relationships"].append({
            "entity_id": entities[1]["id"],
            "relationship_type": "LIVES_IN",
            "confidence": 0.9
        })
        
        # Save test consolidated entities
        for i, entity in enumerate(entities):
            with open(os.path.join(self.consolidated_dir, f"consolidated_{i}.json"), 'w') as f:
                json.dump(entity, f)
    
    def test_memory_bank_integration(self):
        """Test memory bank integration process."""
        memory_bank_dir = os.path.join(self.test_output_dir, '.memory-bank')
        integrator = MemoryBankIntegrator(self.consolidated_dir, memory_bank_dir)
        
        # Run integration
        with patch.object(integrator, '_generate_entity_description', return_value="Test description"):
            result = integrator.integrate()
            
            # Verify memory bank structure
            self.assertTrue(os.path.exists(memory_bank_dir))
            self.assertTrue(os.path.exists(os.path.join(memory_bank_dir, 'Third Age')))
            
            # Verify entity files were created
            character_dir = os.path.join(memory_bank_dir, 'Third Age', 'CHARACTER')
            location_dir = os.path.join(memory_bank_dir, 'Third Age', 'LOCATION')
            
            # In a complete test, we would check the actual file contents
            self.assertTrue(os.path.exists(character_dir))
            self.assertTrue(os.path.exists(location_dir))


class TestSchemaValidation(TestBase):
    """Tests for the schema validation component."""
    
    def setup_test_data(self):
        """Set up test data for schema validation."""
        # Create test entities to validate
        self.entity_dir = os.path.join(self.test_data_dir, 'entities')
        os.makedirs(self.entity_dir, exist_ok=True)
        
        # Valid entity
        valid_entity = {
            "id": "character_frodo",
            "name": "Frodo Baggins",
            "type": "CHARACTER",
            "subtype": "HOBBIT",
            "attributes": {"race": "Hobbit"},
            "sources": [{"book": "Test Book", "chapter": "Test Chapter", "context": "Test context"}],
            "confidence": 0.9
        }
        
        # Invalid entity (missing required field)
        invalid_entity = {
            "id": "character_invalid",
            "name": "Invalid Character",
            "type": "CHARACTER",
            # Missing subtype
            "attributes": {},
            "sources": [],
            "confidence": 0.5
        }
        
        # Save test entities
        with open(os.path.join(self.entity_dir, "valid_entity.json"), 'w') as f:
            json.dump(valid_entity, f)
            
        with open(os.path.join(self.entity_dir, "invalid_entity.json"), 'w') as f:
            json.dump(invalid_entity, f)
    
    @patch('validate.SchemaValidator._load_schema')
    def test_schema_validation(self, mock_load_schema):
        """Test schema validation process."""
        # Mock schema loading
        mock_load_schema.return_value = {
            "type": "object",
            "required": ["id", "name", "type", "subtype"],
            "properties": {
                "id": {"type": "string"},
                "name": {"type": "string"},
                "type": {"type": "string"},
                "subtype": {"type": "string"}
            }
        }
        
        # Create validator
        validator = SchemaValidator()
        
        # Test validation
        valid_path = os.path.join(self.entity_dir, "valid_entity.json")
        invalid_path = os.path.join(self.entity_dir, "invalid_entity.json")
        
        with open(valid_path) as f:
            valid_entity = json.load(f)
            
        with open(invalid_path) as f:
            invalid_entity = json.load(f)
            
        # Validate entities
        valid_result = validator.validate_entity(valid_entity)
        invalid_result = validator.validate_entity(invalid_entity)
        
        # Check results
        self.assertTrue(valid_result["valid"])
        self.assertFalse(invalid_result["valid"])
        self.assertTrue("subtype" in invalid_result["errors"][0])


class TestIntegration(TestBase):
    """Integration tests for the complete pipeline."""
    
    def setup_test_data(self):
        """Set up test data for integration testing."""
        # Create test ePub directory
        self.test_epub_dir = os.path.join(self.test_data_dir, 'epubs')
        os.makedirs(self.test_epub_dir, exist_ok=True)
        
        # Create a mock ePub
        self.test_epub_path = os.path.join(self.test_epub_dir, 'test_book.epub')
        self.create_test_epub(self.test_epub_path, "Test ePub content")
    
    @patch('epub_processor.EpubProcessor.process')
    @patch('entity_extractor.EntityExtractor.process_all_books')
    @patch('entity_consolidator.EntityConsolidator.consolidate')
    @patch('memory_bank_integrator.MemoryBankIntegrator.integrate')
    @patch('validate.SchemaValidator.validate_directory')
    def test_full_pipeline(self, mock_validate, mock_integrate, mock_consolidate, 
                          mock_extract, mock_epub_process):
        """Test the full pipeline integration with mocks."""
        # Configure mocks
        mock_epub_process.return_value = True
        mock_extract.return_value = {"entities": 10, "relationships": 5}
        mock_consolidate.return_value = {"entities": 8, "duplicates": 2}
        mock_integrate.return_value = {"entities": 8, "memory_bank_files": 8}
        mock_validate.return_value = {"valid": 8, "invalid": 0}
        
        # Create pipeline
        pipeline = Pipeline(
            epub_dir=self.test_epub_dir,
            output_dir=self.test_output_dir,
            temp_dir=self.test_temp_dir
        )
        
        # Run pipeline
        result = pipeline.run()
        
        # Verify all steps were called
        mock_epub_process.assert_called()
        mock_extract.assert_called()
        mock_consolidate.assert_called()
        mock_integrate.assert_called()
        mock_validate.assert_called()
        
        # Verify pipeline completed
        self.assertTrue(result["success"])


def run_tests():
    """Run all tests and generate a report."""
    # Create test suite
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestEpubProcessor))
    suite.addTest(unittest.makeSuite(TestEntityExtractor))
    suite.addTest(unittest.makeSuite(TestEntityConsolidator))
    suite.addTest(unittest.makeSuite(TestMemoryBankIntegrator))
    suite.addTest(unittest.makeSuite(TestSchemaValidation))
    suite.addTest(unittest.makeSuite(TestIntegration))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Generate report
    test_base = TestBase()
    test_base.setUp()
    
    test_results = []
    for test_class in [TestEpubProcessor, TestEntityExtractor, TestEntityConsolidator,
                      TestMemoryBankIntegrator, TestSchemaValidation, TestIntegration]:
        test_name = test_class.__name__
        # In a real scenario, we would get actual results
        status = "PASS" if not result.failures and not result.errors else "FAIL"
        test_results.append({
            "test": test_name,
            "status": status,
            "details": "Test completed successfully" if status == "PASS" else "Test failed"
        })
    
    report_path = test_base.generate_test_report(test_results)
    test_base.tearDown()
    
    print(f"Test report generated at: {report_path}")
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1) 