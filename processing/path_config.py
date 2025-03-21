"""
Path Configuration for Tolkien ePub Processing Framework

This module provides a centralized configuration for all paths used in the framework,
ensuring consistency across components and environments (test vs. production).
"""

import os
from pathlib import Path
from typing import Dict, Union, Optional
from enum import Enum


class Environment(Enum):
    """Enum representing different execution environments."""
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
    Set the current environment.
    
    Args:
        env: The environment to set (PRODUCTION, TEST, or DEVELOPMENT)
    """
    global CURRENT_ENV
    CURRENT_ENV = env
    
    # Ensure all directories for the current environment exist
    create_directories()


def get_path(path_type: str) -> Path:
    """
    Get a path based on the current environment.
    
    Args:
        path_type: The type of path to retrieve (e.g., 'logs', 'temp', 'output')
        
    Returns:
        Path object for the requested path type
        
    Raises:
        ValueError: If the path_type is not defined
    """
    if path_type not in PATH_TEMPLATES[CURRENT_ENV]:
        raise ValueError(f"Path type '{path_type}' not defined for environment {CURRENT_ENV.value}")
        
    return PATH_TEMPLATES[CURRENT_ENV][path_type]


def create_directories() -> None:
    """Create all directories defined in the current environment."""
    for path in PATH_TEMPLATES[CURRENT_ENV].values():
        path.mkdir(parents=True, exist_ok=True)


def get_log_file_path(component_name: str) -> Path:
    """
    Get the path to a log file for a specific component.
    
    Args:
        component_name: Name of the component (e.g., 'epub_processor', 'entity_extractor')
        
    Returns:
        Path to the log file
    """
    logs_path = get_path('logs')
    return logs_path / f"{component_name}.log"


def resolve_path(path_str: Union[str, Path], base_type: Optional[str] = None) -> Path:
    """
    Resolve a path string or Path object to an absolute Path.
    If path_str is already absolute, it is returned as is.
    If path_str is relative, it is resolved relative to the specified base_type.
    
    Args:
        path_str: The path to resolve
        base_type: The base path type to resolve relative paths against (e.g., 'output', 'temp')
        
    Returns:
        Absolute Path object
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
    
    Args:
        age: The age (e.g., 'first_age', 'second_age')
        entity_type: The entity type (e.g., 'characters', 'locations')
        
    Returns:
        Path to the memory bank section
    """
    memory_bank_path = get_path('memory_bank')
    return memory_bank_path / age / entity_type


def get_relative_path(path: Union[str, Path], base_path: Optional[Union[str, Path]] = None) -> Path:
    """
    Get a path relative to a base path or project root.
    
    Args:
        path: The path to convert to relative
        base_path: The base path to make it relative to (defaults to project root)
        
    Returns:
        Relative path
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