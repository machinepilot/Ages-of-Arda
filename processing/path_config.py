"""
Path Configuration for Tolkien ePub Processing Framework

This module provides a centralized configuration for all paths used in the framework,
ensuring consistency across components and environments (test vs. production).

The path configuration system solves several common problems:
1. Eliminates hardcoded paths throughout the codebase
2. Ensures consistent directory structure across environments
3. Automatically creates required directories
4. Simplifies path resolution and manipulation
5. Centralizes environment-specific path configurations

Usage:
    from processing.path_config import get_path, set_environment, Environment
    
    # Set environment if needed (defaults to PRODUCTION)
    set_environment(Environment.TEST)
    
    # Get a standard path
    log_dir = get_path('logs')
    
    # Resolve a user-provided path
    user_path = resolve_path('my_data/input.txt', base_type='temp')
"""

import os
from pathlib import Path
from typing import Dict, Union, Optional
from enum import Enum


class Environment(Enum):
    """
    Enum representing different execution environments.
    
    Environments:
        PRODUCTION: Normal operation environment, uses real data and standard paths
        TEST: Testing environment with isolated paths to prevent data corruption
        DEVELOPMENT: Development environment, may have additional debug paths
    """
    PRODUCTION = "production"
    TEST = "test"
    DEVELOPMENT = "development"


# Get absolute path to the project root directory
# This ensures paths are resolved correctly regardless of execution directory
MODULE_DIR = Path(__file__).parent.resolve()
PROJECT_ROOT = MODULE_DIR.parent

# Current environment (default to production, can be changed at runtime)
CURRENT_ENV = Environment.PRODUCTION

# Define path templates for different environments
PATH_TEMPLATES = {
    Environment.PRODUCTION: {
        "processing": PROJECT_ROOT / "processing",
        "logs": PROJECT_ROOT / "processing" / "logs",
        "temp": PROJECT_ROOT / "processing" / "temp",
        "output": PROJECT_ROOT / "processing" / "output",
        "epub_content": PROJECT_ROOT / "processing" / "epub_content",
        "schemas": PROJECT_ROOT / "processing" / "schemas",
        "consolidated": PROJECT_ROOT / "processing" / "consolidated",
        "json_output": PROJECT_ROOT / "processing" / "json_output",
        "memory_bank": PROJECT_ROOT / ".memory-bank",
        "checkpoints": PROJECT_ROOT / "processing" / "checkpoints",
    },
    Environment.TEST: {
        "processing": PROJECT_ROOT / "processing",
        "logs": PROJECT_ROOT / "processing" / "test_logs",
        "temp": PROJECT_ROOT / "processing" / "test_temp",
        "output": PROJECT_ROOT / "processing" / "test_output",
        "epub_content": PROJECT_ROOT / "processing" / "test_data" / "sample_epubs",
        "schemas": PROJECT_ROOT / "processing" / "schemas",
        "consolidated": PROJECT_ROOT / "processing" / "test_output" / "consolidated",
        "json_output": PROJECT_ROOT / "processing" / "test_output" / "json_output",
        "memory_bank": PROJECT_ROOT / "processing" / "test_data" / "memory_bank_structure",
        "reports": PROJECT_ROOT / "processing" / "test_reports",
    },
    Environment.DEVELOPMENT: {
        "processing": PROJECT_ROOT / "processing",
        "logs": PROJECT_ROOT / "processing" / "logs",
        "temp": PROJECT_ROOT / "processing" / "temp",
        "output": PROJECT_ROOT / "processing" / "output",
        "epub_content": PROJECT_ROOT / "processing" / "epub_content",
        "schemas": PROJECT_ROOT / "processing" / "schemas",
        "consolidated": PROJECT_ROOT / "processing" / "consolidated",
        "json_output": PROJECT_ROOT / "processing" / "json_output",
        "memory_bank": PROJECT_ROOT / ".memory-bank",
        "checkpoints": PROJECT_ROOT / "processing" / "checkpoints",
    }
}


def set_environment(env: Environment) -> None:
    """
    Set the current environment and ensure all required directories exist.
    
    This function changes the global environment setting, affecting all subsequent
    path operations. It also automatically creates all directories defined for
    the selected environment.
    
    Args:
        env: The environment to set (PRODUCTION, TEST, or DEVELOPMENT)
        
    Example:
        >>> from processing.path_config import set_environment, Environment
        >>> set_environment(Environment.TEST)  # Switch to test environment
    """
    global CURRENT_ENV
    CURRENT_ENV = env
    
    # Ensure all directories for the current environment exist
    create_directories()


def get_path(path_type: str) -> Path:
    """
    Get a path based on the current environment.
    
    This function returns a Path object for the requested path type in the current
    environment. The returned directory is guaranteed to exist.
    
    Args:
        path_type: The type of path to retrieve (e.g., 'logs', 'temp', 'output')
        
    Returns:
        Path object for the requested path type
        
    Raises:
        ValueError: If the path_type is not defined in the current environment
        
    Example:
        >>> from processing.path_config import get_path
        >>> log_dir = get_path('logs')
        >>> output_file = get_path('output') / 'results.json'
    """
    if path_type not in PATH_TEMPLATES[CURRENT_ENV]:
        raise ValueError(f"Path type '{path_type}' not defined for environment {CURRENT_ENV.value}")
        
    return PATH_TEMPLATES[CURRENT_ENV][path_type]


def create_directories() -> None:
    """
    Create all directories defined in the current environment.
    
    This function is called automatically when the module is imported and
    whenever the environment is changed. It ensures all directories defined
    in PATH_TEMPLATES for the current environment exist.
    
    No parameters or return values.
    """
    for path in PATH_TEMPLATES[CURRENT_ENV].values():
        path.mkdir(parents=True, exist_ok=True)


def get_log_file_path(component_name: str) -> Path:
    """
    Get the path to a log file for a specific component.
    
    This is a convenience function that constructs a log file path in the
    standard logs directory for a given component.
    
    Args:
        component_name: Name of the component (e.g., 'epub_processor', 'entity_extractor')
        
    Returns:
        Path to the log file
        
    Example:
        >>> from processing.path_config import get_log_file_path
        >>> log_path = get_log_file_path('entity_extractor')
        >>> # Use with logging
        >>> import logging
        >>> logging.basicConfig(filename=str(log_path), level=logging.INFO)
    """
    logs_path = get_path('logs')
    return logs_path / f"{component_name}.log"


def resolve_path(path_str: Union[str, Path], base_type: Optional[str] = None) -> Path:
    """
    Resolve a path string or Path object to an absolute Path.
    
    This function handles both absolute and relative paths:
    - If path_str is already absolute, it is returned as is
    - If path_str is relative and base_type is provided, it is resolved relative to that base path
    - If path_str is relative and no base_type is provided, it is resolved relative to PROJECT_ROOT
    
    Args:
        path_str: The path to resolve (string or Path object)
        base_type: The base path type to resolve relative paths against (e.g., 'output', 'temp')
        
    Returns:
        Absolute Path object
        
    Example:
        >>> from processing.path_config import resolve_path
        >>> # Resolve a relative path against the 'temp' directory
        >>> temp_file = resolve_path('data.json', 'temp')
        >>> # Resolve an absolute path (remains unchanged)
        >>> abs_path = resolve_path('/absolute/path/file.txt')
    """
    path = Path(path_str)
    
    if path.is_absolute():
        return path
        
    if base_type:
        return get_path(base_type) / path
    
    # Default to project root for relative paths without a base_type
    return PROJECT_ROOT / path


def get_memory_bank_path(age: str, entity_type: str) -> Path:
    """
    Get the path to a specific section of the memory bank.
    
    This function constructs a path to a specific section of the memory bank
    based on age and entity type, following the memory bank's organizational structure.
    
    Args:
        age: The age (e.g., 'first_age', 'second_age', 'third_age')
        entity_type: The entity type (e.g., 'characters', 'locations', 'items')
        
    Returns:
        Path to the memory bank section
        
    Example:
        >>> from processing.path_config import get_memory_bank_path
        >>> characters_path = get_memory_bank_path('first_age', 'characters')
        >>> # Now you can list or access files in this directory
        >>> character_files = list(characters_path.glob('*.json'))
    """
    memory_bank_path = get_path('memory_bank')
    return memory_bank_path / age / entity_type


def get_relative_path(path: Union[str, Path], base_path: Optional[Union[str, Path]] = None) -> Path:
    """
    Get a path relative to a base path or project root.
    
    This function converts an absolute path to a path relative to the specified base.
    If the path cannot be made relative to the base, the original path is returned.
    
    Args:
        path: The path to convert to relative
        base_path: The base path to make it relative to (defaults to project root)
        
    Returns:
        Relative path if possible, otherwise the original path
        
    Example:
        >>> from processing.path_config import get_relative_path, get_path
        >>> abs_path = get_path('logs') / 'processor.log'
        >>> rel_path = get_relative_path(abs_path)  # Relative to project root
        >>> rel_to_logs = get_relative_path(abs_path, get_path('logs'))  # Just filename
    """
    full_path = Path(path).resolve()
    base = Path(base_path).resolve() if base_path else PROJECT_ROOT
    
    try:
        return full_path.relative_to(base)
    except ValueError:
        # If path is not relative to base, return the absolute path
        return full_path


# Initialize directories when the module is imported
create_directories() 