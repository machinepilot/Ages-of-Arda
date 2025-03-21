"""
Path Configuration Usage Examples

This module demonstrates how to use the path_config module in different components 
of the Tolkien ePub Processing Framework.
"""

import logging
from pathlib import Path

# Import the path_config module
from processing.path_config import (
    set_environment, Environment, get_path, get_log_file_path,
    resolve_path, get_memory_bank_path, get_relative_path
)

# Example 1: Setting up logging in a component
def setup_component_logging(component_name: str) -> logging.Logger:
    """Set up logging for a component using standardized log paths."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(get_log_file_path(component_name)),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger(component_name)

# Example 2: Class initialization with proper paths
class ExampleProcessor:
    """Example class showing path handling in initialization."""
    
    def __init__(self, input_path=None, output_dir=None, temp_dir=None):
        """
        Initialize with proper path resolution.
        
        Args:
            input_path: Path to input file 
            output_dir: Output directory
            temp_dir: Temporary directory
        """
        # Resolve paths using the path_config functions
        self.input_path = resolve_path(input_path, 'epub_content') if input_path else None
        self.output_dir = resolve_path(output_dir, 'output') if output_dir else get_path('output')
        self.temp_dir = resolve_path(temp_dir, 'temp') if temp_dir else get_path('temp')
        
        # Create directories if needed
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.temp_dir.mkdir(parents=True, exist_ok=True)

# Example 3: Setting up test environment
def setup_test_environment():
    """Configure the environment for testing."""
    # Switch to test environment
    set_environment(Environment.TEST)
    
    # Now all paths will resolve to test directories
    test_output = get_path('output')
    test_logs = get_path('logs')
    test_data = get_path('epub_content')
    
    print(f"Test environment configured:")
    print(f"- Test output: {test_output}")
    print(f"- Test logs: {test_logs}")
    print(f"- Test data: {test_data}")

# Example 4: Working with memory bank paths
def process_memory_bank_entity(age: str, entity_type: str, entity_id: str):
    """Process an entity in the memory bank."""
    # Get the path to the entity directory
    entity_dir = get_memory_bank_path(age, entity_type)
    
    # Construct the path to the specific entity file
    entity_file = entity_dir / f"{entity_id}.json"
    
    # Print relative path for debugging
    relative_path = get_relative_path(entity_file)
    print(f"Processing entity at relative path: {relative_path}")
    
    # Use the entity file...
    return entity_file

# Example 5: Command-line argument handling for paths
def handle_path_argument(arg_path: str, path_type: str) -> Path:
    """
    Handle a path provided as a command-line argument.
    
    Args:
        arg_path: Path from command-line argument
        path_type: Default path type if arg_path is None
        
    Returns:
        Resolved Path object
    """
    if arg_path:
        return resolve_path(arg_path)
    else:
        return get_path(path_type)

# Usage examples
if __name__ == "__main__":
    # Example of setting up logging
    logger = setup_component_logging("example_component")
    logger.info("Logging configured using path_config")
    
    # Example of initializing a processor
    processor = ExampleProcessor()
    logger.info(f"Processor initialized with output dir: {processor.output_dir}")
    
    # Example of setting up test environment
    setup_test_environment()
    
    # Example of working with memory bank paths
    entity_file = process_memory_bank_entity("first_age", "characters", "turin_turambar")
    logger.info(f"Entity file path: {entity_file}")
    
    # Example of handling command-line arguments
    import sys
    output_path = handle_path_argument(sys.argv[1] if len(sys.argv) > 1 else None, "output")
    logger.info(f"Using output path: {output_path}") 