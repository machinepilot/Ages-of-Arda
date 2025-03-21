"""
Main Processing Script for Ages of Arda

This script coordinates the processing of ePub files into the Memory Bank system,
integrating all components of the processing workflow.
"""

import os
import sys
import argparse
import logging
import json
from pathlib import Path
import time
import shutil

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join('processing', 'logs', 'main.log')),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('main')

# Import our modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from processing.epub_processor import process_all_epubs
from processing.entity_extractor import extract_entities
from processing.entity_consolidator import consolidate_entities
from processing.memory_bank_integrator import integrate_to_memory_bank
from processing.validate import validate_entities
from processing.schema_validator import SchemaValidator
from processing.checkpoint_manager import get_checkpoint_manager

def setup_directories():
    """
    Set up the necessary directories for processing.
    Following cross-platform directory creation guidelines.
    
    Returns:
        dict: Dictionary of directory paths
    """
    dirs = {
        'temp': Path('processing/temp'),
        'output': Path('processing/output'),
        'logs': Path('processing/logs'),
        'epub_content': Path('processing/epub_content'),
        'json_output': Path('processing/json_output'),
        'schemas': Path('processing/schemas'),
        'checkpoints': Path('processing/checkpoints'),
        'consolidated': Path('processing/consolidated'),
        'validation': Path('processing/validation')
    }
    
    # Create directories with proper error handling
    for name, dir_path in dirs.items():
        try:
            dir_path.mkdir(parents=True, exist_ok=True)
            logger.info(f"Ensured directory exists: {dir_path}")
        except Exception as e:
            logger.error(f"Failed to create directory {dir_path}: {str(e)}")
    
    return dirs

def process_epubs(epub_dir, output_dir, checkpoint_manager, force=False):
    """
    Process all ePub files in the specified directory.
    
    Args:
        epub_dir (str): Directory containing ePub files
        output_dir (str): Directory to save extracted content
        checkpoint_manager: Checkpoint manager for saving progress
        force (bool): Whether to force processing even if already complete
        
    Returns:
        dict: Processing results
    """
    logger.info(f"Processing ePubs from {epub_dir}")
    
    # Check for existing checkpoint
    checkpoint = checkpoint_manager.load_checkpoint("epub_processing")
    if checkpoint and not force:
        logger.info(f"Found existing checkpoint for ePub processing")
        # Check if all books are already processed
        if checkpoint.get("status") == "complete":
            logger.info("ePub processing already complete, skipping")
            return checkpoint.get("results", {})
    
    # Process ePubs
    results = process_all_epubs(epub_dir, output_dir)
    
    # Save checkpoint
    checkpoint_data = {
        "status": "complete",
        "epub_dir": str(epub_dir),
        "output_dir": str(output_dir),
        "timestamp": time.time(),
        "results": results
    }
    checkpoint_manager.save_checkpoint("epub_processing", checkpoint_data)
    
    return results

def extract_entities_from_books(input_dir, output_dir, checkpoint_manager, force=False):
    """
    Extract entities from processed ePub content.
    
    Args:
        input_dir (str): Directory containing processed ePub content
        output_dir (str): Directory to save extracted entities
        checkpoint_manager: Checkpoint manager for saving progress
        force (bool): Whether to force processing even if already complete
        
    Returns:
        dict: Extraction results
    """
    logger.info(f"Extracting entities from {input_dir}")
    
    # Check for existing checkpoint
    checkpoint = checkpoint_manager.load_checkpoint("entity_extraction")
    if checkpoint and not force:
        logger.info(f"Found existing checkpoint for entity extraction")
        # Check if extraction is already complete
        if checkpoint.get("status") == "complete":
            logger.info("Entity extraction already complete, skipping")
            return checkpoint.get("results", {})
    
    # Extract entities
    results = extract_entities(input_dir, output_dir)
    
    # Save checkpoint
    checkpoint_data = {
        "status": "complete",
        "input_dir": str(input_dir),
        "output_dir": str(output_dir),
        "timestamp": time.time(),
        "results": results
    }
    checkpoint_manager.save_checkpoint("entity_extraction", checkpoint_data)
    
    return results

def consolidate_extracted_entities(input_dir, output_dir, checkpoint_manager, force=False):
    """
    Consolidate extracted entities.
    
    Args:
        input_dir (str): Directory containing extracted entities
        output_dir (str): Directory to save consolidated entities
        checkpoint_manager: Checkpoint manager for saving progress
        force (bool): Whether to force processing even if already complete
        
    Returns:
        dict: Consolidation results
    """
    logger.info(f"Consolidating entities from {input_dir}")
    
    # Check for existing checkpoint
    checkpoint = checkpoint_manager.load_checkpoint("entity_consolidation")
    if checkpoint and not force:
        logger.info(f"Found existing checkpoint for entity consolidation")
        # Check if consolidation is already complete
        if checkpoint.get("status") == "complete":
            logger.info("Entity consolidation already complete, skipping")
            return checkpoint.get("results", {})
    
    # Consolidate entities
    results = consolidate_entities(input_dir, output_dir)
    
    # Save checkpoint
    checkpoint_data = {
        "status": "complete",
        "input_dir": str(input_dir),
        "output_dir": str(output_dir),
        "timestamp": time.time(),
        "results": results
    }
    checkpoint_manager.save_checkpoint("entity_consolidation", checkpoint_data)
    
    return results

def validate_entity_data(input_dir, schema_dir, output_dir, checkpoint_manager, validation_level='error', force=False):
    """
    Validate entity data against schemas.
    
    Args:
        input_dir (str): Directory containing entity data
        schema_dir (str): Directory containing schema files
        output_dir (str): Directory to save validation results
        checkpoint_manager: Checkpoint manager for saving progress
        validation_level (str): Validation level (error, warning, info)
        force (bool): Whether to force validation even if already complete
        
    Returns:
        dict: Validation results
    """
    logger.info(f"Validating entities in {input_dir}")
    
    # Check for existing checkpoint
    checkpoint = checkpoint_manager.load_checkpoint("entity_validation")
    if checkpoint and not force:
        logger.info(f"Found existing checkpoint for entity validation")
        # Check if validation is already complete
        if checkpoint.get("status") == "complete" and checkpoint.get("validation_level") == validation_level:
            logger.info("Entity validation already complete, skipping")
            return checkpoint.get("results", {})
    
    # Create output file path
    output_file = os.path.join(output_dir, f"validation_results_{validation_level}.json")
    
    # Validate entities
    results = validate_entities(input_dir, schema_dir, output_file, validation_level)
    
    # Save checkpoint
    checkpoint_data = {
        "status": "complete",
        "input_dir": str(input_dir),
        "schema_dir": str(schema_dir),
        "output_file": output_file,
        "validation_level": validation_level,
        "timestamp": time.time(),
        "results": results
    }
    checkpoint_manager.save_checkpoint("entity_validation", checkpoint_data)
    
    return results

def integrate_to_memory_system(input_dir, memory_bank_dir, schema_dir, checkpoint_manager, force=False):
    """
    Integrate consolidated entities into the Memory Bank system.
    
    Args:
        input_dir (str): Directory containing consolidated entities
        memory_bank_dir (str): Root directory of the Memory Bank
        schema_dir (str): Directory containing schema files
        checkpoint_manager: Checkpoint manager for saving progress
        force (bool): Whether to force integration even if already complete
        
    Returns:
        dict: Integration results
    """
    logger.info(f"Integrating entities into Memory Bank at {memory_bank_dir}")
    
    # Check for existing checkpoint
    checkpoint = checkpoint_manager.load_checkpoint("memory_bank_integration")
    if checkpoint and not force:
        logger.info(f"Found existing checkpoint for Memory Bank integration")
        # Check if integration is already complete
        if checkpoint.get("status") == "complete":
            logger.info("Memory Bank integration already complete, skipping")
            return checkpoint.get("results", {})
    
    # Integrate entities
    results = integrate_to_memory_bank(input_dir, memory_bank_dir, schema_dir)
    
    # Save checkpoint
    checkpoint_data = {
        "status": "complete",
        "input_dir": str(input_dir),
        "memory_bank_dir": str(memory_bank_dir),
        "schema_dir": str(schema_dir),
        "timestamp": time.time(),
        "results": results
    }
    checkpoint_manager.save_checkpoint("memory_bank_integration", checkpoint_data)
    
    return results

def run_pipeline(args, dirs):
    """
    Run the complete processing pipeline.
    
    Args:
        args: Command line arguments
        dirs (dict): Dictionary of directory paths
        
    Returns:
        dict: Processing results
    """
    # Initialize checkpoint manager
    checkpoint_manager = get_checkpoint_manager()
    
    # Initialize results
    results = {
        "epub_processing": None,
        "entity_extraction": None,
        "entity_consolidation": None,
        "entity_validation": None,
        "memory_bank_integration": None
    }
    
    # Process ePubs
    if args.skip_to == 'none' or args.skip_to == 'epub':
        epub_results = process_epubs(args.epub_dir, dirs['epub_content'], checkpoint_manager, args.force)
        results["epub_processing"] = {
            "successful": len(epub_results.get('successful', [])),
            "failed": len(epub_results.get('failed', []))
        }
    
    # Extract entities
    if args.skip_to in ['none', 'epub', 'extract']:
        entity_results = extract_entities_from_books(dirs['epub_content'], dirs['json_output'], checkpoint_manager, args.force)
        results["entity_extraction"] = {
            "total_entities": entity_results.get('total_entities', 0),
            "entity_counts": entity_results.get('entity_counts', {})
        }
    
    # Consolidate entities
    if args.skip_to in ['none', 'epub', 'extract', 'consolidate']:
        consolidation_results = consolidate_extracted_entities(dirs['json_output'], dirs['consolidated'], checkpoint_manager, args.force)
        results["entity_consolidation"] = {
            "total_entities": consolidation_results.get('total_entities', 0),
            "entity_counts": consolidation_results.get('entity_counts', {}),
            "duplicates_resolved": consolidation_results.get('duplicates_resolved', 0)
        }
    
    # Validate entities
    if args.skip_to in ['none', 'epub', 'extract', 'consolidate', 'validate']:
        validation_results = validate_entity_data(
            dirs['consolidated'], 
            dirs['schemas'], 
            dirs['validation'], 
            checkpoint_manager,
            args.validation_level, 
            args.force
        )
        results["entity_validation"] = {
            "total": validation_results.get('summary', {}).get('total', 0),
            "valid": validation_results.get('summary', {}).get('valid', 0),
            "invalid": validation_results.get('summary', {}).get('invalid', 0)
        }
        
        # Check if validation passed (if using strict mode)
        if args.strict and validation_results.get('summary', {}).get('invalid', 0) > 0:
            logger.error("Validation failed in strict mode. Pipeline halted.")
            return results
    
    # Integrate to Memory Bank
    if args.skip_to in ['none', 'epub', 'extract', 'consolidate', 'validate', 'integrate']:
        integration_results = integrate_to_memory_system(
            dirs['consolidated'], 
            args.memory_bank_dir, 
            dirs['schemas'], 
            checkpoint_manager,
            args.force
        )
        results["memory_bank_integration"] = {
            "total_entities": integration_results.get('total_entities', 0),
            "entities_by_type": integration_results.get('entities_by_type', {}),
            "entities_by_age": integration_results.get('entities_by_age', {})
        }
    
    return results

def print_results_summary(results):
    """
    Print a summary of processing results.
    
    Args:
        results (dict): Processing results
    """
    print("\nProcessing Summary:")
    print("===================")
    
    if results.get("epub_processing"):
        print("\nePub Processing:")
        print(f"  Successful: {results['epub_processing']['successful']}")
        print(f"  Failed: {results['epub_processing']['failed']}")
    
    if results.get("entity_extraction"):
        print("\nEntity Extraction:")
        print(f"  Total entities: {results['entity_extraction']['total_entities']}")
        for entity_type, count in results['entity_extraction'].get('entity_counts', {}).items():
            print(f"  {entity_type}: {count}")
    
    if results.get("entity_consolidation"):
        print("\nEntity Consolidation:")
        print(f"  Total entities: {results['entity_consolidation']['total_entities']}")
        print(f"  Duplicates resolved: {results['entity_consolidation']['duplicates_resolved']}")
        for entity_type, count in results['entity_consolidation'].get('entity_counts', {}).items():
            print(f"  {entity_type}: {count}")
    
    if results.get("entity_validation"):
        print("\nEntity Validation:")
        print(f"  Total entities: {results['entity_validation']['total']}")
        print(f"  Valid: {results['entity_validation']['valid']} ({results['entity_validation']['valid'] * 100 / max(1, results['entity_validation']['total']):.1f}%)")
        print(f"  Invalid: {results['entity_validation']['invalid']} ({results['entity_validation']['invalid'] * 100 / max(1, results['entity_validation']['total']):.1f}%)")
    
    if results.get("memory_bank_integration"):
        print("\nMemory Bank Integration:")
        print(f"  Total entities integrated: {results['memory_bank_integration']['total_entities']}")
        for entity_type, count in results['memory_bank_integration'].get('entities_by_type', {}).items():
            print(f"  {entity_type}: {count}")
    
    print("\nProcessing pipeline complete!")

def main():
    """
    Main processing function that coordinates all steps.
    """
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Process ePubs for the Ages of Arda Memory Bank")
    parser.add_argument("--epub-dir", default="raw_inputs/New Files", help="Directory containing ePub files")
    parser.add_argument("--memory-bank-dir", default=".memory-bank", help="Root directory of the Memory Bank")
    parser.add_argument("--skip-existing", action="store_true", help="Skip processing if output already exists")
    parser.add_argument("--clean", action="store_true", help="Clean output directories before processing")
    parser.add_argument("--force", action="store_true", help="Force processing even if already complete")
    parser.add_argument("--validation-level", choices=['error', 'warning', 'info'], default='error', 
                        help="Validation level (error, warning, info)")
    parser.add_argument("--strict", action="store_true", help="Stop pipeline if validation fails")
    parser.add_argument("--skip-to", choices=['none', 'epub', 'extract', 'consolidate', 'validate', 'integrate'], 
                        default='none', help="Skip to a specific processing stage")
    args = parser.parse_args()
    
    logger.info("Starting Ages of Arda ePub processing pipeline")
    
    # Set up directories
    dirs = setup_directories()
    
    # Check if we should clean output directories
    if args.clean:
        logger.info("Cleaning output directories")
        
        # Define which directories to clean based on skip_to argument
        dirs_to_clean = []
        
        if args.skip_to == 'none':
            dirs_to_clean = ['temp', 'output', 'epub_content', 'json_output', 'consolidated', 'validation']
        elif args.skip_to == 'epub':
            dirs_to_clean = ['temp', 'json_output', 'consolidated', 'validation']
        elif args.skip_to == 'extract':
            dirs_to_clean = ['consolidated', 'validation']
        elif args.skip_to == 'consolidate':
            dirs_to_clean = ['validation']
        
        # Clean the directories
        for dir_name in dirs_to_clean:
            dir_path = dirs[dir_name]
            for item in dir_path.glob("*"):
                if item.is_file():
                    item.unlink()
                elif item.is_dir():
                    shutil.rmtree(item)
            
            logger.info(f"Cleaned directory: {dir_path}")
    
    # Run the pipeline
    results = run_pipeline(args, dirs)
    
    # Print results summary
    print_results_summary(results)
    
    # Save overall results
    results_file = os.path.join(dirs['output'], 'pipeline_results.json')
    with open(results_file, 'w', encoding='utf-8') as f:
        json.dump({
            'timestamp': time.time(),
            'results': results
        }, f, indent=2)
    
    logger.info(f"Results saved to {results_file}")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logger.exception(f"Unhandled exception in main process: {str(e)}")
        print(f"Error: {str(e)}")
        sys.exit(1) 