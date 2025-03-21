"""
Test Utilities for Tolkien ePub Processing Framework

This module provides utility functions for testing the framework,
including test discovery, execution, and reporting.
"""

import os
import sys
import json
import unittest
import logging
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional, Union

# Import path configuration
from processing.path_config import get_path, get_log_file_path, set_environment, Environment

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(get_log_file_path('test_utils')),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('test_utils')

def discover_tests(test_dir: Optional[str] = None, pattern: str = "test_*.py") -> unittest.TestSuite:
    """
    Discover and load tests from the specified directory.
    
    Args:
        test_dir: Directory to search for tests (defaults to processing directory)
        pattern: File pattern for test modules
        
    Returns:
        TestSuite containing all discovered tests
    """
    if test_dir is None:
        test_dir = str(get_path('processing'))
        
    logger.info(f"Discovering tests in {test_dir} with pattern {pattern}")
    return unittest.defaultTestLoader.discover(test_dir, pattern=pattern)

def run_tests(test_suite: Optional[unittest.TestSuite] = None, 
              test_dir: Optional[str] = None,
              pattern: str = "test_*.py") -> unittest.TestResult:
    """
    Run tests and return the result.
    
    Args:
        test_suite: TestSuite to run (if None, discovers tests)
        test_dir: Directory to search for tests if test_suite is None
        pattern: File pattern for test modules if test_suite is None
        
    Returns:
        TestResult with test execution results
    """
    if test_suite is None:
        test_suite = discover_tests(test_dir, pattern)
        
    runner = unittest.TextTestRunner(verbosity=2)
    logger.info(f"Running {test_suite.countTestCases()} tests")
    return runner.run(test_suite)

def generate_test_report(result: unittest.TestResult, 
                        output_dir: Optional[str] = None) -> str:
    """
    Generate a JSON report from test results.
    
    Args:
        result: TestResult from running tests
        output_dir: Directory to save the report (defaults to test_reports path)
        
    Returns:
        Path to the generated report file
    """
    if output_dir is None:
        output_dir = str(get_path('reports'))
        os.makedirs(output_dir, exist_ok=True)
        
    # Create report data
    report = {
        "timestamp": datetime.now().isoformat(),
        "total_tests": result.testsRun,
        "passed": result.testsRun - len(result.failures) - len(result.errors),
        "failed": len(result.failures),
        "errors": len(result.errors),
        "skipped": len(result.skipped) if hasattr(result, 'skipped') else 0,
        "failures": [
            {
                "test": str(test),
                "message": msg
            } for test, msg in result.failures
        ],
        "errors": [
            {
                "test": str(test),
                "message": msg
            } for test, msg in result.errors
        ]
    }
    
    # Save report
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_filename = f"test_report_{timestamp}.json"
    report_path = os.path.join(output_dir, report_filename)
    
    with open(report_path, 'w') as f:
        json.dump(report, f, indent=2)
        
    logger.info(f"Test report saved to {report_path}")
    return report_path

def run_and_report(test_dir: Optional[str] = None, 
                  pattern: str = "test_*.py",
                  output_dir: Optional[str] = None) -> Dict[str, Any]:
    """
    Run tests, generate a report, and return a summary.
    
    Args:
        test_dir: Directory to search for tests
        pattern: File pattern for test modules
        output_dir: Directory to save the report
        
    Returns:
        Dictionary with test summary and report path
    """
    # Make sure we're in TEST environment
    set_environment(Environment.TEST)
    
    # Discover and run tests
    test_suite = discover_tests(test_dir, pattern)
    result = run_tests(test_suite)
    
    # Generate report
    report_path = generate_test_report(result, output_dir)
    
    # Create summary
    summary = {
        "total": result.testsRun,
        "passed": result.testsRun - len(result.failures) - len(result.errors),
        "failed": len(result.failures),
        "errors": len(result.errors),
        "skipped": len(result.skipped) if hasattr(result, 'skipped') else 0,
        "success": len(result.failures) == 0 and len(result.errors) == 0,
        "report_path": report_path
    }
    
    return summary

if __name__ == "__main__":
    # When run as a script, run all tests and print summary
    set_environment(Environment.TEST)
    summary = run_and_report()
    
    print("\nTest Summary:")
    print(f"Total Tests: {summary['total']}")
    print(f"Passed: {summary['passed']}")
    print(f"Failed: {summary['failed']}")
    print(f"Errors: {summary['errors']}")
    print(f"Report saved to: {summary['report_path']}")
    
    # Exit with success if all tests passed
    sys.exit(0 if summary['success'] else 1) 