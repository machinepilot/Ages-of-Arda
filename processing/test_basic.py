"""
Basic Test for Ages of Arda ePub Processing Framework

This is a simplified test to verify that the testing framework is working.
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

# Import and configure path_config first
from processing.path_config import set_environment, Environment, get_path, get_log_file_path

# Set test environment at the start
set_environment(Environment.TEST)

# Set up logging using path_config
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(get_log_file_path('test_basic')),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('test_basic')

class TestBase(unittest.TestCase):
    """Base class for all test cases, providing common setup and teardown."""
    
    def setUp(self):
        """Set up test environment with temporary directories."""
        self.test_dir = tempfile.mkdtemp()
        self.test_data_dir = os.path.join(self.test_dir, 'test_data')
        self.test_output_dir = os.path.join(self.test_dir, 'test_output')
        
        # Create necessary directories
        os.makedirs(self.test_data_dir, exist_ok=True)
        os.makedirs(self.test_output_dir, exist_ok=True)
        
    def tearDown(self):
        """Clean up temporary files and directories."""
        shutil.rmtree(self.test_dir)

class TestPathConfig(TestBase):
    """Tests for the path configuration module."""
    
    def test_environment_setup(self):
        """Test that the environment is properly set to TEST."""
        from processing.path_config import CURRENT_ENV
        self.assertEqual(CURRENT_ENV, Environment.TEST)
        
    def test_get_path(self):
        """Test retrieving paths for the current environment."""
        logs_path = get_path('logs')
        self.assertTrue(logs_path.exists())
        self.assertTrue('test_logs' in str(logs_path))

if __name__ == '__main__':
    unittest.main() 