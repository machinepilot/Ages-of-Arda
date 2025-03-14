#!/usr/bin/env python
"""
Test Windows Documentation Generation
This script tests the Windows documentation generation functionality
"""

import os
import sys
import json
import time
import argparse
import subprocess
from datetime import datetime

def run_test(test_name, command, expected_output=None, expected_files=None):
    """Run a test and check the results."""
    print(f"\n=== Running Test: {test_name} ===")
    print(f"Command: {command}")
    
    # Create test output directory
    test_dir = f"test_output/{test_name}"
    os.makedirs(test_dir, exist_ok=True)
    
    # Run the command
    start_time = time.time()
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    end_time = time.time()
    
    # Save output
    with open(f"{test_dir}/stdout.txt", "w") as f:
        f.write(result.stdout)
    
    with open(f"{test_dir}/stderr.txt", "w") as f:
        f.write(result.stderr)
    
    # Check return code
    if result.returncode != 0:
        print(f"❌ Test failed with return code {result.returncode}")
        print("Error output:")
        print(result.stderr)
        return False
    
    # Check expected output
    if expected_output and expected_output not in result.stdout:
        print(f"❌ Expected output not found: {expected_output}")
        return False
    
    # Check expected files
    if expected_files:
        for file_path in expected_files:
            full_path = os.path.join(test_dir, file_path)
            if not os.path.exists(full_path):
                print(f"❌ Expected file not found: {full_path}")
                return False
    
    print(f"✅ Test passed in {end_time - start_time:.2f} seconds")
    return True

def test_windows_file_detection():
    """Test the Windows file detection functionality."""
    test_name = "windows_file_detection"
    command = f"python document-angband.py --windows-only --max-files 5 --output test_output/{test_name}"
    expected_output = "Filtered to"
    expected_files = ["files", "modules", "windows_compilation.md", "windows_index.md"]
    
    return run_test(test_name, command, expected_output, expected_files)

def test_windows_api_detection():
    """Test the Windows API detection functionality."""
    test_name = "windows_api_detection"
    command = f"python document-angband.py --file src/win/win-layout.c --output test_output/{test_name}"
    expected_output = "Processing src/win/win-layout.c"
    expected_files = ["files/win-layout.c.md"]
    
    success = run_test(test_name, command, expected_output, expected_files)
    
    # Check if the generated documentation contains Windows API information
    if success:
        doc_path = f"test_output/{test_name}/files/win-layout.c.md"
        if os.path.exists(doc_path):
            with open(doc_path, "r", encoding="utf-8") as f:
                content = f.read()
                if "Windows-Specific Notes" not in content:
                    print("❌ Windows API information not found in documentation")
                    return False
    
    return success

def test_windows_module_creation():
    """Test the Windows module creation functionality."""
    test_name = "windows_module_creation"
    command = f"python windows-module-creator.py && python document-angband.py --windows-only --max-files 1 --output test_output/{test_name}"
    expected_output = "Created Windows module page"
    expected_files = ["modules/windows.md", "modules/windows_metadata.json"]
    
    return run_test(test_name, command, expected_output, expected_files)

def test_visual_studio_project_documentation():
    """Test the Visual Studio project documentation functionality."""
    test_name = "vs_project_documentation"
    command = f"python document-angband.py --vs-project --output test_output/{test_name}"
    expected_output = "Filtered to"
    
    return run_test(test_name, command, expected_output)

def test_incremental_documentation():
    """Test the incremental documentation functionality."""
    test_name = "incremental_documentation"
    
    # First run to generate initial documentation
    command1 = f"python document-angband.py --windows-only --max-files 2 --output test_output/{test_name}"
    run_test(f"{test_name}_initial", command1)
    
    # Second run with incremental flag
    command2 = f"python document-angband.py --windows-only --incremental --output test_output/{test_name}"
    expected_output = "Filtered to"
    
    return run_test(f"{test_name}_incremental", command2, expected_output)

def test_html_conversion():
    """Test the HTML conversion functionality."""
    test_name = "html_conversion"
    command = f"python document-angband.py --windows-only --max-files 1 --format html --output test_output/{test_name}"
    expected_output = "Converting documentation to HTML"
    
    success = run_test(test_name, command, expected_output)
    
    # Check if HTML files were created
    if success:
        html_files = []
        for root, dirs, files in os.walk(f"test_output/{test_name}"):
            for file in files:
                if file.endswith(".html"):
                    html_files.append(os.path.join(root, file))
        
        if not html_files:
            print("❌ No HTML files were created")
            return False
        else:
            print(f"Found {len(html_files)} HTML files")
    
    return success

def main():
    """Main function to run the tests."""
    parser = argparse.ArgumentParser(description="Test Windows documentation generation")
    parser.add_argument("--test", type=str, choices=["all", "detection", "api", "module", "vs", "incremental", "html"], 
                        default="all", help="Which test to run")
    args = parser.parse_args()
    
    # Create test output directory
    os.makedirs("test_output", exist_ok=True)
    
    # Record test results
    results = {
        "test_date": datetime.now().isoformat(),
        "tests": {}
    }
    
    # Run selected tests
    if args.test in ["all", "detection"]:
        results["tests"]["windows_file_detection"] = test_windows_file_detection()
    
    if args.test in ["all", "api"]:
        results["tests"]["windows_api_detection"] = test_windows_api_detection()
    
    if args.test in ["all", "module"]:
        results["tests"]["windows_module_creation"] = test_windows_module_creation()
    
    if args.test in ["all", "vs"]:
        results["tests"]["vs_project_documentation"] = test_visual_studio_project_documentation()
    
    if args.test in ["all", "incremental"]:
        results["tests"]["incremental_documentation"] = test_incremental_documentation()
    
    if args.test in ["all", "html"]:
        results["tests"]["html_conversion"] = test_html_conversion()
    
    # Save test results
    with open("test_output/test_results.json", "w") as f:
        json.dump(results, f, indent=2)
    
    # Print summary
    print("\n=== Test Summary ===")
    total_tests = len(results["tests"])
    passed_tests = sum(1 for result in results["tests"].values() if result)
    
    print(f"Passed: {passed_tests}/{total_tests} tests")
    
    for test_name, result in results["tests"].items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {test_name}")
    
    # Return success if all tests passed
    return 0 if passed_tests == total_tests else 1

if __name__ == "__main__":
    sys.exit(main()) 