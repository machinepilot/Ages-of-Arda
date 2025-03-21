---
title: "Path Handling Guide for Contributors"
id: "dev-path-handling"
section: "development"
category: "guides"
created: "2025-03-21"
updated: "2025-03-21"
version: "1.0.0"
contributors: ["Development Team"]
tags: ["path", "configuration", "testing", "beginners"]
related: ["dev-testing", "dev-process-pipeline"]
---

# Path Handling Guide for Contributors

This guide explains the path handling system used in the Tolkien ePub Processing Framework and provides instructions for how to use it correctly in your contributions.

## Key Principles

When working with files and directories in this project, remember these key principles:

1. **Never use hardcoded paths** - Always use the path configuration system
2. **Always respect the environment setting** - Different paths are used in different environments
3. **Use pathlib.Path for manipulations** - Don't use string concatenation or os.path functions
4. **Directories are automatically created** - No need for explicit os.makedirs() calls
5. **Log files should use the standardized location** - Use get_log_file_path() for all logging

## Using the Path Configuration System

### Basic Import

Start by importing the path configuration module:

```python
from processing.path_config import get_path, resolve_path, get_log_file_path
```

### Getting Standard Paths

To get a path that's defined in the path configuration:

```python
output_dir = get_path('output')
temp_dir = get_path('temp')
schema_dir = get_path('schemas')
```

### Working with Files in These Directories

```python
# Create a file path
output_file = get_path('output') / "my_result.json"

# Read a file
with open(get_path('schemas') / "entity_schema.json", 'r') as f:
    schema = json.load(f)
    
# Write a file
with open(get_path('output') / "processed_data.json", 'w') as f:
    json.dump(data, f)
```

### Handling User-Provided Paths

When a function accepts a path as an argument, use `resolve_path()` to handle it consistently:

```python
def process_file(input_file, output_dir=None):
    # Resolve against a specific base type
    input_path = resolve_path(input_file, 'epub_content')
    
    # Use default if not provided
    output_path = resolve_path(output_dir, 'output') if output_dir else get_path('output')
    
    # Process the file...
```

### Setting Up Logging

Always use the standard logging setup with the path configuration:

```python
import logging
from processing.path_config import get_log_file_path

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(get_log_file_path('my_component')),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('my_component')
```

## Working in Different Environments

### Production Environment

This is the default. All paths resolve to the standard production directories:

```
processing/
├── logs/
├── temp/
├── output/
├── epub_content/
├── schemas/
├── consolidated/
└── json_output/
```

### Test Environment

For testing, set the environment to TEST:

```python
from processing.path_config import set_environment, Environment

# Set test environment
set_environment(Environment.TEST)
```

This changes all paths to use test-specific directories:

```
processing/
├── test_logs/
├── test_temp/
├── test_output/
├── test_data/
│   └── sample_epubs/
├── schemas/
└── test_reports/
```

### Development Environment

Similar to production but with some paths optimized for development workflow:

```python
# Set development environment
set_environment(Environment.DEVELOPMENT)
```

## Path Handling in Tests

When writing tests, follow these guidelines:

1. Always set the environment to TEST at the start of the test module
2. Use paths from the path configuration in your test setup
3. Clean up test directories in tearDown methods if needed

Example test setup:

```python
import unittest
from processing.path_config import set_environment, Environment, get_path

# Set test environment
set_environment(Environment.TEST)

class MyTest(unittest.TestCase):
    def setUp(self):
        # Use standard test directories
        self.test_dir = get_path('temp')
        self.output_dir = get_path('output')
        
        # Create test data
        with open(self.test_dir / "test_data.json", 'w') as f:
            json.dump(TEST_DATA, f)
            
    def test_my_function(self):
        # Run test using standard paths
        result = my_function(
            input_file=self.test_dir / "test_data.json",
            output_dir=self.output_dir
        )
        
        # Verify results
        self.assertTrue((self.output_dir / "result.json").exists())
```

## Troubleshooting Common Path Issues

### Issue: File Not Found

If you get a "file not found" error:

1. Check which environment is active
2. Verify that you're using get_path() correctly
3. Make sure the file exists in the expected directory for that environment

### Issue: Path Type Not Defined

If you get a "path type X not defined" error:

1. Check that you're using a valid path type from PATH_TEMPLATES
2. If you need a new path type, add it to all environments in path_config.py

### Issue: Permission Errors

If you get permission errors:

1. Check that your application has write access to the directories
2. Consider using temp directories for tests with tempfile.mkdtemp()

## Adding New Path Types

If you need to add a new path type:

1. Edit path_config.py
2. Add the new path to all three environment configurations
3. Ensure the paths follow the environment-specific pattern
4. Update this documentation to reference the new path type

## Converting Existing Code

When updating old code to use the path configuration:

1. Replace string paths with get_path() calls
2. Replace os.path operations with pathlib.Path methods
3. Replace manual os.makedirs() calls with automatic directory creation
4. Update logging to use get_log_file_path()
5. Add environment setting in test modules

### Before:

```python
import os

# Create directories
os.makedirs("processing/output", exist_ok=True)
os.makedirs("processing/temp", exist_ok=True)

# Process a file
input_file = os.path.join("processing", "epub_content", "my_file.epub")
output_file = os.path.join("processing", "output", "my_file.json")

with open(input_file, 'r') as f_in, open(output_file, 'w') as f_out:
    # Process data
```

### After:

```python
from processing.path_config import get_path

# Directories are created automatically

# Process a file
input_file = get_path('epub_content') / "my_file.epub"
output_file = get_path('output') / "my_file.json"

with open(input_file, 'r') as f_in, open(output_file, 'w') as f_out:
    # Process data
```

## Further Information

For more detailed information on the path configuration system, refer to:

- [Path Configuration System Documentation](../../../wiki/developer-guides/tolkien-epub-processing-path-system.html)
- [Testing Framework Guide](../../../processing/testing_README.md)
- [Python Code Style Guidelines](../../../.cursor/rules/code-style/python-style.mdc)

## History

- **2025-03-21**: Initial document creation 