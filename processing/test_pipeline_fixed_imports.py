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

# Rest of the test_pipeline.py file would follow... 