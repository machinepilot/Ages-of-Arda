#!/usr/bin/env python3
"""
Test Runner for Ages of Arda ePub Processing Framework

This script runs the tests in the test_pipeline.py module and generates reports.
"""

import os
import sys
import json
import logging
import argparse
from pathlib import Path
from datetime import datetime

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join('logs', 'test_runner.log')),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('test_runner')

# Import the test module
from test_pipeline import run_tests


def setup_logging_directory():
    """Set up logging directory if it doesn't exist."""
    os.makedirs('logs', exist_ok=True)


def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description='Run tests for the Ages of Arda ePub Processing Framework')
    parser.add_argument('--verbose', '-v', action='store_true', help='Enable verbose output')
    parser.add_argument('--report-dir', '-r', default='processing/test_reports', help='Directory to store test reports')
    parser.add_argument('--component', '-c', choices=['all', 'epub', 'entity', 'consolidation', 'memory', 'validation'],
                        default='all', help='Specific component to test')
    
    return parser.parse_args()


def create_report_directory(report_dir):
    """Create report directory if it doesn't exist."""
    os.makedirs(report_dir, exist_ok=True)
    return report_dir


def generate_summary_report(report_dir, success):
    """Generate a summary report of all tests."""
    # Create timestamp for the report
    timestamp = datetime.now().isoformat()
    
    # Collect all test reports in the directory
    report_files = [f for f in os.listdir(report_dir) if f.endswith('.json')]
    
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
    summary_path = os.path.join(report_dir, "summary_report.json")
    with open(summary_path, 'w') as f:
        json.dump(summary, f, indent=2)
    
    # Also save a human-readable version
    readable_path = os.path.join(report_dir, "summary_report.txt")
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
    # Set up logging
    setup_logging_directory()
    
    # Parse arguments
    args = parse_arguments()
    
    # Set log level based on verbosity
    if args.verbose:
        logger.setLevel(logging.DEBUG)
    
    # Create report directory
    report_dir = create_report_directory(args.report_dir)
    
    logger.info(f"Running tests for component: {args.component}")
    logger.info(f"Test reports will be saved to: {report_dir}")
    
    # Run tests
    success = run_tests()
    
    # Generate summary report
    summary_path = generate_summary_report(report_dir, success)
    
    logger.info(f"Test summary report generated at: {summary_path}")
    
    # Return success status as exit code
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main()) 