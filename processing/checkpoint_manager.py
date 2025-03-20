"""
Checkpoint Manager for Ages of Arda

This module provides functionality for saving and restoring processing state
to allow resumption of work if processing is interrupted.
"""

import os
import json
import logging
from pathlib import Path
from datetime import datetime

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join('processing', 'logs', 'checkpoint.log')),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('checkpoint_manager')

class CheckpointManager:
    """
    Manager for saving and restoring processing checkpoints.
    """
    
    def __init__(self, checkpoint_dir):
        """
        Initialize the checkpoint manager.
        
        Args:
            checkpoint_dir (str): Directory to store checkpoints
        """
        self.checkpoint_dir = Path(checkpoint_dir)
        self.checkpoint_dir.mkdir(parents=True, exist_ok=True)
    
    def save_checkpoint(self, process_name, state_data):
        """
        Save a checkpoint for a process.
        
        Args:
            process_name (str): Name of the process
            state_data (dict): Process state data to save
            
        Returns:
            str: Path to the saved checkpoint file
        """
        try:
            # Create checkpoint file
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            checkpoint_file = self.checkpoint_dir / f"{process_name}_{timestamp}.json"
            
            # Add metadata
            checkpoint_data = {
                "process_name": process_name,
                "timestamp": datetime.now().isoformat(),
                "state": state_data
            }
            
            # Save to file
            with open(checkpoint_file, 'w', encoding='utf-8') as f:
                json.dump(checkpoint_data, f, indent=2)
            
            # Create latest pointer
            latest_file = self.checkpoint_dir / f"{process_name}_latest.json"
            with open(latest_file, 'w', encoding='utf-8') as f:
                json.dump({"latest_checkpoint": str(checkpoint_file)}, f, indent=2)
            
            logger.info(f"Saved checkpoint for {process_name} to {checkpoint_file}")
            return str(checkpoint_file)
        
        except Exception as e:
            logger.error(f"Error saving checkpoint for {process_name}: {str(e)}")
            return None
    
    def load_checkpoint(self, process_name, checkpoint_file=None):
        """
        Load a checkpoint for a process.
        
        Args:
            process_name (str): Name of the process
            checkpoint_file (str, optional): Specific checkpoint file to load.
                                             If None, loads the latest checkpoint.
            
        Returns:
            dict: Process state data, or None if no checkpoint found
        """
        try:
            # If no specific file provided, try to load latest
            if checkpoint_file is None:
                latest_file = self.checkpoint_dir / f"{process_name}_latest.json"
                if not latest_file.exists():
                    logger.warning(f"No latest checkpoint found for {process_name}")
                    return None
                
                with open(latest_file, 'r', encoding='utf-8') as f:
                    latest_data = json.load(f)
                
                checkpoint_file = latest_data.get("latest_checkpoint")
                if not checkpoint_file:
                    logger.warning(f"Invalid latest checkpoint pointer for {process_name}")
                    return None
            
            # Load checkpoint data
            checkpoint_path = Path(checkpoint_file)
            if not checkpoint_path.exists():
                logger.warning(f"Checkpoint file not found: {checkpoint_file}")
                return None
            
            with open(checkpoint_path, 'r', encoding='utf-8') as f:
                checkpoint_data = json.load(f)
            
            logger.info(f"Loaded checkpoint for {process_name} from {checkpoint_file}")
            return checkpoint_data.get("state")
        
        except Exception as e:
            logger.error(f"Error loading checkpoint for {process_name}: {str(e)}")
            return None
    
    def list_checkpoints(self, process_name=None):
        """
        List available checkpoints.
        
        Args:
            process_name (str, optional): Filter by process name
            
        Returns:
            list: List of checkpoint information dictionaries
        """
        try:
            # Get all checkpoint files
            if process_name:
                checkpoint_files = list(self.checkpoint_dir.glob(f"{process_name}_*.json"))
                # Exclude latest pointer
                checkpoint_files = [f for f in checkpoint_files if not f.name.endswith("_latest.json")]
            else:
                checkpoint_files = list(self.checkpoint_dir.glob("*.json"))
                # Exclude latest pointers
                checkpoint_files = [f for f in checkpoint_files if not f.name.endswith("_latest.json")]
            
            checkpoints = []
            for checkpoint_file in checkpoint_files:
                try:
                    with open(checkpoint_file, 'r', encoding='utf-8') as f:
                        checkpoint_data = json.load(f)
                    
                    checkpoints.append({
                        "file": str(checkpoint_file),
                        "process_name": checkpoint_data.get("process_name"),
                        "timestamp": checkpoint_data.get("timestamp"),
                        "size": os.path.getsize(checkpoint_file)
                    })
                except Exception as e:
                    logger.warning(f"Error reading checkpoint file {checkpoint_file}: {str(e)}")
            
            # Sort by timestamp (newest first)
            checkpoints.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
            
            return checkpoints
        
        except Exception as e:
            logger.error(f"Error listing checkpoints: {str(e)}")
            return []
    
    def delete_checkpoint(self, checkpoint_file):
        """
        Delete a checkpoint file.
        
        Args:
            checkpoint_file (str): Path to checkpoint file
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            checkpoint_path = Path(checkpoint_file)
            if checkpoint_path.exists():
                checkpoint_path.unlink()
                logger.info(f"Deleted checkpoint file: {checkpoint_file}")
                return True
            else:
                logger.warning(f"Checkpoint file not found: {checkpoint_file}")
                return False
        
        except Exception as e:
            logger.error(f"Error deleting checkpoint file {checkpoint_file}: {str(e)}")
            return False
    
    def cleanup_old_checkpoints(self, process_name=None, keep_latest=5):
        """
        Clean up old checkpoints, keeping only the most recent ones.
        
        Args:
            process_name (str, optional): Filter by process name
            keep_latest (int): Number of most recent checkpoints to keep
            
        Returns:
            int: Number of deleted checkpoints
        """
        try:
            # Get all checkpoints
            checkpoints = self.list_checkpoints(process_name)
            
            # Keep the latest 'keep_latest' checkpoints
            to_delete = checkpoints[keep_latest:]
            
            # Delete old checkpoints
            deleted_count = 0
            for checkpoint in to_delete:
                if self.delete_checkpoint(checkpoint["file"]):
                    deleted_count += 1
            
            logger.info(f"Cleaned up {deleted_count} old checkpoints")
            return deleted_count
        
        except Exception as e:
            logger.error(f"Error cleaning up old checkpoints: {str(e)}")
            return 0


def get_checkpoint_manager():
    """
    Get a checkpoint manager instance.
    
    Returns:
        CheckpointManager: Checkpoint manager for the processing directory
    """
    checkpoint_dir = os.path.join('processing', 'checkpoints')
    return CheckpointManager(checkpoint_dir)


if __name__ == "__main__":
    # Example usage
    manager = get_checkpoint_manager()
    
    # List available checkpoints
    checkpoints = manager.list_checkpoints()
    print(f"Found {len(checkpoints)} checkpoints")
    
    for checkpoint in checkpoints:
        print(f"- {checkpoint['process_name']} ({checkpoint['timestamp']})") 