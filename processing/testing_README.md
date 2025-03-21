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

## Running Tests

To run the tests, use the `run_tests.py` script:

```bash
python processing/run_tests.py
```

### Command-line Options

- `--verbose` or `-v`: Enable verbose output
- `--report-dir` or `-r`: Specify the directory to store test reports (default: `processing/test_reports`)
- `--component` or `-c`: Specify a specific component to test (choices: `all`, `epub`, `entity`, `consolidation`, `memory`, `validation`)

Example:
```bash
python processing/run_tests.py --verbose --component entity
```

## Test Data

The test data is located in the `processing/test_data` directory and includes:

- Sample ePub files in simplified JSON format
- Sample entity data
- Sample relationship data
- Mock memory bank structure

## Test Reports

Test reports are generated in the specified report directory (default: `processing/test_reports`). The reports include:

- JSON reports for each test class
- A summary report in both JSON and text formats

## Adding New Tests

To add new tests:

1. Add a new test case class to `test_pipeline.py`
2. Add appropriate test methods
3. Add test data to the `test_data` directory
4. Add the new test class to the test suite in the `run_tests()` function

## Continuous Integration

These tests can be integrated into a CI/CD pipeline by running:

```bash
python processing/run_tests.py
```

The exit code will be 0 if all tests pass, or non-zero if any tests fail. 