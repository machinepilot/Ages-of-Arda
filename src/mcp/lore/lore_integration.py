"""
Lore Integration Module

This module integrates the lore manager and narrative generator with the MCP server,
providing a unified API for lore-driven gameplay functionality.
"""

import os
import sys
import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional

# Import the narrative generator
from .narrative_generator import NarrativeGenerator

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class LoreIntegration:
    """
    Integrates lore management and narrative generation with the MCP server.
    Serves as the main entry point for lore-driven gameplay features.
    """
    
    def __init__(self, memory_bank_path: str, llm_client=None):
        """
        Initialize the lore integration.
        
        Args:
            memory_bank_path: Path to the memory bank directory
            llm_client: Client for LLM API calls (optional)
        """
        self.memory_bank_path = Path(memory_bank_path)
        self.llm_client = llm_client
        
        # Initialize the narrative generator
        self.narrative_generator = NarrativeGenerator(memory_bank_path, llm_client)
        
        # Load current age from memory bank
        self.current_age = self._load_current_age()
        
        logger.info(f"Lore integration initialized with memory bank at {memory_bank_path}")
        logger.info(f"Current age: {self.current_age}")
    
    def _load_current_age(self) -> str:
        """
        Load the current age from the memory bank.
        
        Returns:
            Current age (e.g., 'first_age', 'third_age')
        """
        timeline_file = self.memory_bank_path / "ages" / "current_timeline.md"
        
        if not timeline_file.exists():
            logger.warning(f"Timeline file not found at {timeline_file}, defaulting to third_age")
            return "third_age"
        
        try:
            with open(timeline_file, "r", encoding="utf-8") as f:
                content = f.read()
                
                # Parse the file to extract the current age
                if "First Age" in content or "first_age" in content:
                    return "first_age"
                elif "Third Age" in content or "third_age" in content:
                    return "third_age"
                else:
                    logger.warning("Could not determine current age from timeline file")
                    return "third_age"  # Default to Third Age
                
        except IOError as e:
            logger.error(f"Error reading timeline file: {e}")
            return "third_age"  # Default to Third Age
    
    def set_current_age(self, age: str) -> bool:
        """
        Set the current age for the game.
        
        Args:
            age: The age to set as current (e.g., 'first_age', 'third_age')
            
        Returns:
            True if successful, False otherwise
        """
        if age not in ["first_age", "third_age"]:
            logger.error(f"Invalid age: {age}")
            return False
        
        self.current_age = age
        logger.info(f"Current age set to {age}")
        return True
    
    def get_location_description(self, location_name: str, age: Optional[str] = None, 
                                context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Get a description for a location based on lore.
        
        Args:
            location_name: Name of the location
            age: Age to get the description for (defaults to current age)
            context: Additional context for description generation
            
        Returns:
            Dictionary with location description and metadata
        """
        if age is None:
            age = self.current_age
        
        description = self.narrative_generator.generate_location_description(location_name, age, context)
        
        return {
            "description": description,
            "location": location_name,
            "age": age
        }
    
    def get_companion_dialogue(self, companion_name: str, topic: Optional[str] = None,
                              relationship_level: int = 0, age: Optional[str] = None,
                              context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Get dialogue for a companion based on lore and context.
        
        Args:
            companion_name: Name of the companion
            topic: Optional topic for the dialogue
            relationship_level: Level of relationship with the player (0-5)
            age: Age to get the dialogue for (defaults to current age)
            context: Additional context about the player, game state, etc.
            
        Returns:
            Dictionary with companion dialogue and metadata
        """
        if age is None:
            age = self.current_age
        
        dialogue = self.narrative_generator.generate_companion_dialogue(
            companion_name, age, topic, relationship_level, context
        )
        
        return {
            "dialogue": dialogue,
            "companion": companion_name,
            "age": age,
            "topic": topic
        }
    
    def generate_quest(self, quest_type: str, location: str, target: Optional[str] = None,
                      age: Optional[str] = None, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Generate a quest based on lore and game context.
        
        Args:
            quest_type: Type of quest (e.g., "rescue", "retrieve", "defeat")
            location: Location name where the quest takes place
            target: Optional target of the quest (character, item, enemy)
            age: Age to generate the quest for (defaults to current age)
            context: Additional context about the player, game state, etc.
            
        Returns:
            Dictionary with quest data
        """
        if age is None:
            age = self.current_age
        
        quest = self.narrative_generator.generate_quest_description(
            quest_type, location, age, target, context
        )
        
        return {
            "title": quest.get("title"),
            "description": quest.get("description"),
            "quest_type": quest_type,
            "location": location,
            "age": age,
            "target": target
        }
    
    def get_random_lore(self, topic_type: Optional[str] = None, 
                       age: Optional[str] = None) -> Dict[str, Any]:
        """
        Get a random piece of lore related to the current game state.
        
        Args:
            topic_type: Optional topic type (character, location, event, etc.)
            age: Age to get lore from (defaults to current age)
            
        Returns:
            Dictionary with lore content and metadata
        """
        # This would be implemented by querying the narrative generator
        # For now, return a placeholder
        return {
            "content": "A piece of lore about Middle-earth...",
            "topic_type": topic_type or "general",
            "age": age or self.current_age
        }
    
    def register_mcp_endpoints(self, mcp_server) -> None:
        """
        Register lore-related endpoints with the MCP server.
        
        Args:
            mcp_server: The MCP server instance
        """
        # Register narrative generation endpoints
        self.narrative_generator.register_mcp_endpoints(mcp_server)
        
        # Register additional lore integration endpoints
        mcp_server.register_endpoint("ages/lore/age/set", self._handle_set_age_request)
        mcp_server.register_endpoint("ages/lore/age/get", self._handle_get_age_request)
        mcp_server.register_endpoint("ages/lore/random", self._handle_random_lore_request)
    
    def _handle_set_age_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle MCP request to set the current age.
        
        Args:
            request: The MCP request data
            
        Returns:
            Response indicating success or failure
        """
        age = request.get("age")
        
        if not age:
            return {"error": "Missing required parameter: age"}
        
        success = self.set_current_age(age)
        
        if success:
            return {"status": "success", "age": age}
        else:
            return {"error": f"Invalid age: {age}"}
    
    def _handle_get_age_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle MCP request to get the current age.
        
        Args:
            request: The MCP request data
            
        Returns:
            Response with the current age
        """
        return {"age": self.current_age}
    
    def _handle_random_lore_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle MCP request for random lore.
        
        Args:
            request: The MCP request data
            
        Returns:
            Response with random lore
        """
        topic_type = request.get("topic_type")
        age = request.get("age", self.current_age)
        
        lore = self.get_random_lore(topic_type, age)
        
        return lore


def initialize_lore_integration(memory_bank_path: str, mcp_server, llm_client=None) -> LoreIntegration:
    """
    Initialize and register the lore integration with the MCP server.
    
    Args:
        memory_bank_path: Path to the memory bank directory
        mcp_server: The MCP server instance
        llm_client: Client for LLM API calls (optional)
        
    Returns:
        Initialized LoreIntegration instance
    """
    integration = LoreIntegration(memory_bank_path, llm_client)
    integration.register_mcp_endpoints(mcp_server)
    
    logger.info("Lore integration registered with MCP server")
    return integration 