# Path Configuration System for Tolkien ePub Processing Framework

This document explains the standardized path configuration system implemented in `path_config.py`. This system ensures consistent path handling across all components of the Tolkien ePub Processing Framework, improving reliability and making the codebase easier to maintain.

## Overview

The path configuration system:

1. Defines all paths relative to the project root directory
2. Provides different path sets for different environments (production, test, development)
3. Includes helper functions for path resolution and manipulation
4. Centralizes log file management
5. Ensures directories exist when needed

## Key Components

### Environment Types

Three environments are supported:

- **PRODUCTION**: Used for normal processing operations
- **TEST**: Used during automated testing, with separate paths to avoid affecting production data
- **DEVELOPMENT**: Used during development work

### Path Types

Standard path types are defined for each environment:

- `processing`: Main processing directory
- `logs`: Log file directory
- `temp`: Temporary file directory
- `output`: Output directory for processed files
- `epub_content`: Directory containing ePub files to process
- `schemas`: JSON schema directory
- `consolidated`: Directory for consolidated entities
- `json_output`: Directory for JSON output files
- `memory_bank`: Memory bank root directory
- `checkpoints`: Directory for processing checkpoints
- `reports`: Test report directory (test environment only)

## Using the Path Configuration

### Basic Usage

```python
from processing.path_config import get_path, get_log_file_path

# Get the path to the output directory
output_dir = get_path('output')

# Get the log file path for a component
log_file = get_log_file_path('epub_processor')
```

### Setting the Environment

```python
from processing.path_config import set_environment, Environment

# Switch to test environment
set_environment(Environment.TEST)

# Now all paths will resolve to test directories
test_output = get_path('output')  # Returns test output directory
```

### Path Resolution

```python
from processing.path_config import resolve_path

# Resolve a path relative to a specific base path type
file_path = resolve_path('my_file.txt', 'output')

# Resolve an absolute path (returns it unchanged)
abs_path = resolve_path('/absolute/path/file.txt')
```

### Memory Bank Paths

```python
from processing.path_config import get_memory_bank_path

# Get path to a specific section of the memory bank
characters_path = get_memory_bank_path('first_age', 'characters')
```

## Integration with Components

### Logging Setup

```python
import logging
from processing.path_config import get_log_file_path

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(get_log_file_path('component_name')),
        logging.StreamHandler()
    ]
)
```

### Class Initialization

```python
from processing.path_config import get_path, resolve_path

class MyProcessor:
    def __init__(self, input_file, output_dir=None):
        self.input_file = resolve_path(input_file, 'epub_content')
        self.output_dir = resolve_path(output_dir) if output_dir else get_path('output')
        self.output_dir.mkdir(parents=True, exist_ok=True)
```

## Testing Support

The path configuration system makes testing easier by:

1. Providing separate directories for test data and output
2. Ensuring tests don't modify production data
3. Creating test directories automatically
4. Supporting standardized test report locations

## Migration Guide

When migrating existing code to use the path configuration system:

1. Replace hardcoded paths with `get_path()` calls
2. Update logging setup to use `get_log_file_path()`
3. Use `resolve_path()` for path arguments in functions and methods
4. Add `set_environment(Environment.TEST)` at the beginning of test scripts
5. Remove redundant directory creation code (handled by path_config)

## Benefits

Using this path configuration system provides several benefits:

- **Consistency**: All components use the same paths
- **Portability**: Works across different operating systems
- **Isolation**: Test environment doesn't affect production data
- **Maintainability**: Paths can be changed centrally
- **Reliability**: Directories are created when needed

## Example

See `path_config_usage_example.py` for detailed usage examples. 