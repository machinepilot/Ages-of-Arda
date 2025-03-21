#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Test script for verifying the NLP setup for Tolkien ePub processing.

This script:
1. Verifies all dependencies are properly installed
2. Checks that spaCy models are downloaded
3. Confirms entity list files are created
"""

import os
import sys
import importlib
import logging
from pathlib import Path

# Initialize logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("test_setup")

def test_dependencies():
    """Test that all required dependencies are installed."""
    dependencies = [
        "ebooklib",
        "bs4",  # beautifulsoup4
        "spacy",
        "networkx",
        "tqdm",
        "pandas",
        "nltk",
        "jsonschema",
        "lxml"
    ]
    
    missing_deps = []
    
    for dep in dependencies:
        try:
            importlib.import_module(dep)
            logger.info(f"✓ {dep} is installed")
        except ImportError:
            missing_deps.append(dep)
            logger.error(f"✗ {dep} is NOT installed")
    
    if missing_deps:
        logger.error(f"Missing dependencies: {', '.join(missing_deps)}")
        logger.error("Run: pip install -r processing/requirements.txt")
        return False
    
    return True

def test_spacy_model():
    """Test that the spaCy model is properly installed."""
    try:
        import spacy
        model_name = "en_core_web_lg"
        
        # Try to load the model
        nlp = spacy.load(model_name)
        logger.info(f"✓ SpaCy model {model_name} is installed")
        
        # Test a simple sentence with the model
        doc = nlp("Frodo Baggins carried the One Ring to Mount Doom in Mordor.")
        entities = [(ent.text, ent.label_) for ent in doc.ents]
        logger.info(f"Detected entities: {entities}")
        
        return True
    except Exception as e:
        logger.error(f"✗ SpaCy model test failed: {str(e)}")
        return False

def test_entity_lists():
    """Test that entity list files are created."""
    entity_lists_dir = Path("processing/schemas/entity_lists")
    expected_files = [
        "character_list.txt",
        "location_list.txt",
        "item_list.txt",
        "event_list.txt",
        "race_list.txt",
        "language_list.txt"
    ]
    
    missing_files = []
    
    for filename in expected_files:
        file_path = entity_lists_dir / filename
        if file_path.exists():
            # Count entries in the file
            with open(file_path, 'r', encoding='utf-8') as f:
                entries = [line.strip() for line in f if line.strip()]
                logger.info(f"✓ {filename} exists with {len(entries)} entries")
        else:
            missing_files.append(filename)
            logger.error(f"✗ {filename} is missing")
    
    if missing_files:
        logger.error(f"Missing entity list files: {', '.join(missing_files)}")
        logger.error("Run: python processing/setup_nlp.py")
        return False
    
    return True

def run_tests():
    """Run all setup tests."""
    logger.info("Testing Tolkien ePub processing setup...")
    
    # Test dependencies
    deps_ok = test_dependencies()
    if not deps_ok:
        logger.error("Dependency test failed")
        return False
    
    # Test spaCy model
    spacy_ok = test_spacy_model()
    if not spacy_ok:
        logger.error("SpaCy model test failed")
        return False
    
    # Test entity lists
    lists_ok = test_entity_lists()
    if not lists_ok:
        logger.error("Entity lists test failed")
        return False
    
    logger.info("All tests passed successfully!")
    return True

if __name__ == "__main__":
    success = run_tests()
    
    if success:
        logger.info("Setup verification completed successfully")
        sys.exit(0)
    else:
        logger.error("Setup verification failed")
        sys.exit(1) 