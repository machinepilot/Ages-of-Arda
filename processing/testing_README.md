# Tolkien ePub Processing Framework Testing Infrastructure

This directory contains the testing infrastructure for the Tolkien ePub Processing Framework. The tests are designed to ensure that all components of the processing pipeline function correctly.

## Test Components

The testing infrastructure includes tests for the following components:

1. **ePub Processor** - Tests for extracting content from ePub files
2. **Entity Extractor** - Tests for identifying and extracting entities from text
3. **Entity Consolidator** - Tests for deduplicating and consolidating entities
4. **Memory Bank Integrator** - Tests for integrating entities into the memory bank
5. **Schema Validator** - Tests for validating entity data against schemas
6. **Integration Tests** - End-to-end tests for the complete pipeline
7. **Path Configuration** - Tests for the centralized path management system

## Getting Started with Testing (For Beginners)

If you're new to unit testing, follow these steps to get started:

### Step 1: Set Up Your Environment

Make sure you have a Python environment with the required dependencies:

```bash
# Activate your virtual environment (if using one)
# Windows:
.venv\Scripts\activate.bat
# Linux/Mac:
# source .venv/bin/activate

# Install required packages
pip install requests jsonschema ebooklib beautifulsoup4
```

### Step 2: Understanding the Test Structure

Our tests are organized as follows:
- `test_basic.py` - Simple tests for path configuration
- `test_pipeline_mock.py` - Tests using mock implementations to avoid external dependencies
- `test_utils.py` - Utilities for discovering, running, and reporting on tests

### Step 3: Running Your First Test

Start with our basic test to make sure everything is working:

```bash
python -m processing.test_basic
```

This runs a simple test for the path configuration system. If you see output ending with "OK", your test environment is working correctly.

### Step 4: Using the Mock Testing Framework

For more complex components, we use mock implementations to avoid external dependencies:

```bash
python -m processing.test_pipeline_mock
```

This approach allows you to test functionality without needing services like Ollama running.

### Step 5: Running All Tests and Generating Reports

To run all tests and generate a comprehensive report:

```bash
python -m processing.test_utils
```

This will discover all test modules, run them, and generate a JSON report in the test reports directory.

## Running Tests

To run tests, you can use any of the following methods:

### Method 1: Using the test_utils module

```bash
python -m processing.test_utils
```

### Method 2: Using unittest directly

```bash
python -m unittest processing.test_basic
python -m unittest processing.test_pipeline_mock
```

### Method 3: Using the run_tests.py script

```bash
python processing/run_tests.py
```

### Command-line Options for run_tests.py

- `--verbose` or `-v`: Enable verbose output
- `--report-dir` or `-r`: Specify the directory to store test reports (default: `processing/test_reports`)
- `--component` or `-c`: Specify a specific component to test (choices: `all`, `epub`, `entity`, `consolidation`, `memory`, `validation`, `path`)

Example:
```bash
python processing/run_tests.py --verbose --component entity
```

## Test Environments and Path Configuration

All tests use the special TEST environment setting from the path configuration system. This ensures that:

1. Tests run in isolated directories
2. Tests don't affect production data
3. Test directories are created automatically
4. Test logs are stored separately

The test environment is activated in each test module with:

```python
from processing.path_config import set_environment, Environment
set_environment(Environment.TEST)
```

## Test Data

The test data is located in the `processing/test_data` directory and includes:

- Sample ePub files in simplified JSON format
- Sample entity data
- Sample relationship data
- Mock memory bank structure

## Dealing with External Dependencies

For components that depend on external services like Ollama, we provide:

1. **Mock Implementations**: `mock_entity_extractor.py` provides a drop-in replacement for testing
2. **Test Stubs**: Components that require complex dependencies use stubbed versions
3. **Dependency Injection**: Tests can pass mock objects to isolate components

## Test Reports

Test reports are generated in the specified report directory (default: `processing/test_reports`). The reports include:

- JSON reports for each test class
- A summary report in both JSON and text formats

## Adding New Tests

To add new tests:

1. Create a new test case class that inherits from `TestBase`
2. Add appropriate test methods (prefix with `test_`)
3. Add test data to the `test_data` directory
4. Add the new test class to the discovery pattern in `test_utils.py`

Example:

```python
class TestMyComponent(TestBase):
    def test_my_feature(self):
        # Test implementation
        self.assertTrue(result)
```

## Troubleshooting Tests

If you encounter issues:

1. Check that your virtual environment is active
2. Verify all dependencies are installed
3. Check logs in the test_logs directory
4. Try running with verbose output: `python -m unittest -v processing.test_basic`
5. For dependency errors, consider using the mock implementations

## Continuous Integration

These tests can be integrated into a CI/CD pipeline by running:

```bash
python processing/run_tests.py
```

The exit code will be 0 if all tests pass, or non-zero if any tests fail. 