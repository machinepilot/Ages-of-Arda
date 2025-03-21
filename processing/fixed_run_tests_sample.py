#!/usr/bin/env python3
"""
Test Runner for Ages of Arda ePub Processing Framework

This script runs the tests in the test_pipeline.py module and generates reports.
Sample showing how to update run_tests.py to use the path_config system.
"""

import os
import sys
import json
import logging
import argparse
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
        logging.FileHandler(get_log_file_path('test_runner')),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('test_runner')

# Import the test module
from processing.test_pipeline import run_tests


def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description='Run tests for the Ages of Arda ePub Processing Framework')
    parser.add_argument('--verbose', '-v', action='store_true', help='Enable verbose output')
    parser.add_argument('--report-dir', '-r', default=None, help='Directory to store test reports')
    parser.add_argument('--component', '-c', 
                        choices=['all', 'epub', 'entity', 'consolidation', 'memory', 'validation'],
                        default='all', help='Specific component to test')
    
    return parser.parse_args()


def create_report_directory(report_dir=None):
    """Create report directory if it doesn't exist."""
    if report_dir:
        # If a custom directory was provided, use it
        report_path = Path(report_dir)
    else:
        # Otherwise use the configured reports path
        report_path = get_path('reports')
        
    report_path.mkdir(parents=True, exist_ok=True)
    return report_path


def generate_summary_report(report_dir, success):
    """Generate a summary report of all tests."""
    # Create timestamp for the report
    timestamp = datetime.now().isoformat()
    
    # Ensure report_dir is a Path object
    report_path = Path(report_dir)
    
    # Collect all test reports in the directory
    report_files = [f.name for f in report_path.glob('*.json')]
    
    # Create summary data
    summary = {
        "timestamp": timestamp,
        "overall_success": success,
        "report_files": report_files,
        "components_tested": ["epub_processor", "entity_extractor", "entity_consolidator", 
                             "memory_bank_integrator", "schema_validator"],
        "summary": f"Test suite {'passed' if success else 'failed'} at {timestamp}"
    }
    
    # Save summary report
    summary_path = report_path / "summary_report.json"
    with open(summary_path, 'w') as f:
        json.dump(summary, f, indent=2)
    
    # Also save a human-readable version
    readable_path = report_path / "summary_report.txt"
    with open(readable_path, 'w') as f:
        f.write(f"Test Suite Summary - {timestamp}\n")
        f.write(f"Overall Status: {'PASSED' if success else 'FAILED'}\n\n")
        f.write("Components Tested:\n")
        for component in summary["components_tested"]:
            f.write(f"- {component}\n")
        f.write(f"\nDetailed Reports: {len(report_files)} files\n")
        for report_file in report_files:
            f.write(f"- {report_file}\n")
    
    return summary_path


def main():
    """Main function to run tests and generate reports."""
    # Parse arguments
    args = parse_arguments()
    
    # Set log level based on verbosity
    if args.verbose:
        logger.setLevel(logging.DEBUG)
    
    # Create report directory
    report_dir = create_report_directory(args.report_dir)
    
    logger.info(f"Running tests for component: {args.component}")
    logger.info(f"Test reports will be saved to: {report_dir}")
    
    # Set the selected component in the environment for run_tests to access
    os.environ['TEST_COMPONENT'] = args.component
    os.environ['TEST_REPORT_DIR'] = str(report_dir)
    
    # Run tests (assuming run_tests doesn't take arguments in the original code)
    success = run_tests()
    
    # Generate summary report
    summary_path = generate_summary_report(report_dir, success)
    
    logger.info(f"Test summary report generated at: {summary_path}")
    
    # Return success status as exit code
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main()) 