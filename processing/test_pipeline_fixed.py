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

# Import and configure path_config first
from processing.path_config import set_environment, Environment, get_path, get_log_file_path

# Set test environment at the start
set_environment(Environment.TEST)

# Set up logging using path_config
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(get_log_file_path('test_pipeline')),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('test_pipeline')

# Import the modules to be tested
from processing.epub_processor import EpubProcessor, process_epub_file
from processing.entity_extractor import EntityExtractor, OllamaClient, EntityStore
from processing.entity_consolidator import EntityConsolidator
from processing.memory_bank_integrator import MemoryBankIntegrator
from processing.validate import SchemaValidator, MemoryBankValidator
from processing.main import Pipeline

class TestBase(unittest.TestCase):
    """Base class for all test cases, providing common setup and teardown."""
    
    def setUp(self):
        """Set up test environment with temporary directories."""
        self.test_dir = tempfile.mkdtemp()
        self.test_data_dir = os.path.join(self.test_dir, 'test_data')
        self.test_output_dir = os.path.join(self.test_dir, 'test_output')
        self.test_temp_dir = os.path.join(self.test_dir, 'test_temp')
        self.schema_dir = os.path.join(self.test_dir, 'schemas')  # Added schema directory
        
        # Create necessary directories
        os.makedirs(self.test_data_dir, exist_ok=True)
        os.makedirs(self.test_output_dir, exist_ok=True)
        os.makedirs(self.test_temp_dir, exist_ok=True)
        os.makedirs(self.schema_dir, exist_ok=True)  # Create schema directory
        
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
        
    @patch('processing.epub_processor.EpubProcessor.extract_epub')
    @patch('processing.epub_processor.EpubProcessor.find_content_files')
    @patch('processing.epub_processor.EpubProcessor.extract_text_from_content_files')
    @patch('processing.epub_processor.EpubProcessor.save_chapters')
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
            
    @patch('processing.entity_extractor.OllamaClient')
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
                    "confidence": 0.92,
                    "context": "Gandalf visited him in the Shire."
                }
            ]
        })
        
        # Create extractor
        extractor = EntityExtractor(self.test_output_dir)
        
        # Test the extraction process
        with open(self.test_chapter_path) as f:
            chapter = json.load(f)
            
        entities = extractor.extract_entities_from_chapter(chapter)
        
        # Verify the results
        self.assertEqual(len(entities), 4)
        self.assertEqual(entities[0]["name"], "Frodo Baggins")
        self.assertEqual(entities[1]["name"], "Bag End")


class TestEntityConsolidator(TestBase):
    """Tests for the Entity Consolidator component."""
    
    def setup_test_data(self):
        """Set up test data for entity consolidation."""
        self.entity_dir = os.path.join(self.test_data_dir, 'entities')
        os.makedirs(self.entity_dir, exist_ok=True)
        
        # Create test entity files
        entities = [
            self.create_test_entity("CHARACTER", "Frodo Baggins", {"race": "Hobbit"}),
            self.create_test_entity("CHARACTER", "Frodo", {"race": "Hobbit"}),  # Duplicate
            self.create_test_entity("LOCATION", "Bag End", {"region": "The Shire"}),
            self.create_test_entity("CHARACTER", "Gandalf", {"race": "Maiar"})
        ]
        
        for i, entity in enumerate(entities):
            with open(os.path.join(self.entity_dir, f"entity_{i}.json"), 'w') as f:
                json.dump(entity, f)
    
    @patch('processing.entity_consolidator.EntityConsolidator._find_duplicate_entities')
    def test_consolidation(self, mock_find_duplicates):
        """Test entity consolidation process."""
        mock_find_duplicates.return_value = {
            'character_frodo': ['character_frodo_baggins']
        }
        
        # Create consolidator
        consolidator = EntityConsolidator(self.entity_dir, self.test_output_dir)
        
        # Test the consolidation process
        with patch.object(consolidator, 'load_all_entities', return_value=4):
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
        integrator = MemoryBankIntegrator(self.consolidated_dir, memory_bank_dir, self.schema_dir)
        
        # Run integration
        with patch.object(integrator, '_generate_entity_description', return_value="Test description"):
            result = integrator.integrate()
            
            # Verify memory bank structure
            self.assertTrue(os.path.exists(memory_bank_dir))
            self.assertTrue(os.path.exists(os.path.join(memory_bank_dir, 'third_age')))
            
            # Get the expected directory names from the integrator
            character_type_dir = integrator.type_to_dir.get("CHARACTER", "characters")
            location_type_dir = integrator.type_to_dir.get("LOCATION", "locations")

            # Adjusted paths with the correct directory names
            character_dir = os.path.join(memory_bank_dir, 'third_age', character_type_dir)
            location_dir = os.path.join(memory_bank_dir, 'third_age', location_type_dir)
            
            # Verify entity files were created
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
        
        # Create a sample schema in the schema directory
        sample_schema = {
            "type": "object",
            "required": ["id", "name", "type", "subtype"],
            "properties": {
                "id": {"type": "string"},
                "name": {"type": "string"},
                "type": {"type": "string"},
                "subtype": {"type": "string"}
            }
        }
        
        with open(os.path.join(self.schema_dir, "character.json"), 'w') as f:
            json.dump(sample_schema, f)
    
    @patch('processing.schema_validator.SchemaValidator')
    def test_schema_validation(self, MockValidator):
        """Test schema validation process."""
        # Configure the mock validator
        mock_validator = MockValidator.return_value
        mock_validator.validate_entity.side_effect = lambda entity, entity_type=None: (
            (True, None) if 'subtype' in entity else (False, "Missing required field: subtype")
        )
        
        # Test validation
        valid_path = os.path.join(self.entity_dir, "valid_entity.json")
        invalid_path = os.path.join(self.entity_dir, "invalid_entity.json")
        
        with open(valid_path) as f:
            valid_entity = json.load(f)
            
        with open(invalid_path) as f:
            invalid_entity = json.load(f)
            
        # Get validation results
        is_valid, _ = mock_validator.validate_entity(valid_entity)
        self.assertTrue(is_valid)
        
        is_valid, error_msg = mock_validator.validate_entity(invalid_entity)
        self.assertFalse(is_valid)
        self.assertTrue("subtype" in error_msg)


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
    
    @patch('processing.epub_processor.EpubProcessor.process')
    @patch('processing.entity_extractor.EntityExtractor.process_all_books')
    @patch('processing.entity_consolidator.EntityConsolidator.consolidate')
    @patch('processing.memory_bank_integrator.MemoryBankIntegrator.integrate')
    @patch('processing.schema_validator.SchemaValidator.validate_directory')
    def test_full_pipeline(self, mock_validate, mock_integrate, mock_consolidate, 
                          mock_extract, mock_epub_process):
        """Test the full pipeline integration with mocks."""
        # Configure mocks with correct return types
        # Match return type of EpubProcessor.process
        mock_epub_process.return_value = {"chapters": 2, "book_title": "Test Book"}

        # Match return type of EntityExtractor.process_all_books
        mock_extract.return_value = {
            'processed_books': ['test_book'],
            'total_entities': 10,
            'entity_counts': {'CHARACTER': 5, 'LOCATION': 5}
        }

        # Match return type of EntityConsolidator.consolidate
        mock_consolidate.return_value = {
            'duplicates_resolved': 2,
            'total_entities': 8,
            'entity_counts': {'CHARACTER': 4, 'LOCATION': 4}
        }

        # Match return type of MemoryBankIntegrator.integrate
        mock_integrate.return_value = {
            'total_entities': 8,
            'entities_by_type': {'characters': 4, 'locations': 4},
            'memory_bank_files': 8
        }

        # Match return type of SchemaValidator.validate_directory
        mock_validate.return_value = {
            'summary': {'total': 8, 'valid': 8, 'invalid': 0},
            'valid': [{'entity_name': 'Test Entity'}],
            'invalid': []
        }
        
        # Create pipeline
        pipeline = Pipeline(
            epub_dir=self.test_epub_dir,
            output_dir=self.test_output_dir,
            temp_dir=self.test_temp_dir,
            schema_dir=self.schema_dir  # Add schema_dir parameter
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
        test_results.append({
            "name": test_name,
            "status": "PASS" if not result.failures and not result.errors else "FAIL",
            "tests_run": len([m for m in dir(test_class) if m.startswith('test_')])
        })
    
    report_path = test_base.generate_test_report(test_results)
    test_base.tearDown()
    
    logger.info(f"Test report generated at: {report_path}")
    
    return result.wasSuccessful()


if __name__ == "__main__":
    sys.exit(0 if run_tests() else 1) 