"""
Ages of Arda MCP Server Integration

This module integrates the Ages of Arda companion system with the MCP server,
providing hooks for the Angband game to interact with companions.
"""

import os
import json
import logging
from pathlib import Path
from ..companions.companion_handler import CompanionHandler

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class AgesOfArdaIntegration:
    """
    Integration module for the Ages of Arda variant with the MCP server.
    
    This class provides methods for the MCP server to interact with the
    Ages of Arda companion system, including dialogue generation, timeline
    advancement, and companion relationship tracking.
    """
    
    def __init__(self, memory_bank_path, llm_client=None):
        """
        Initialize the Ages of Arda integration.
        
        Args:
            memory_bank_path (str): Path to the memory bank directory
            llm_client: Client for LLM API calls (optional)
        """
        self.memory_bank_path = Path(memory_bank_path)
        self.companion_handler = CompanionHandler(memory_bank_path, llm_client)
        self.relationship_levels = self._load_relationship_levels()
        
        logger.info(f"Initialized AgesOfArdaIntegration with companion: {self.companion_handler.current_companion.get('name', 'Unknown')}")
    
    def _load_relationship_levels(self):
        """Load relationship levels from the memory bank."""
        relationship_path = self.memory_bank_path / "player" / "relationships.json"
        
        if not relationship_path.exists():
            # Create default relationship levels
            relationships = {
                "current": {}
            }
            
            # Ensure the directory exists
            relationship_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Save default relationships
            with open(relationship_path, 'w', encoding='utf-8') as f:
                json.dump(relationships, f, indent=2)
            
            return relationships
        
        # Load existing relationship levels
        with open(relationship_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def _save_relationship_levels(self):
        """Save relationship levels to the memory bank."""
        relationship_path = self.memory_bank_path / "player" / "relationships.json"
        
        # Ensure the directory exists
        relationship_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Save relationships
        with open(relationship_path, 'w', encoding='utf-8') as f:
            json.dump(self.relationship_levels, f, indent=2)
    
    def get_current_companion_name(self):
        """Get the name of the current companion."""
        return self.companion_handler.current_companion.get('name', 'Unknown')
    
    def get_current_age_and_year(self):
        """Get the current age and year."""
        return {
            "age": self.companion_handler.current_timeline.get('age', 'First Age'),
            "year": self.companion_handler.current_timeline.get('year', 1)
        }
    
    def get_relationship_level(self, companion_name=None):
        """
        Get the relationship level with a companion.
        
        Args:
            companion_name (str, optional): Name of the companion. If None, uses current companion.
            
        Returns:
            int: Relationship level (0-100)
        """
        if companion_name is None:
            companion_name = self.get_current_companion_name()
        
        # Get the relationship level from the current relationships
        return self.relationship_levels.get("current", {}).get(companion_name, 0)
    
    def update_relationship_level(self, change, companion_name=None):
        """
        Update the relationship level with a companion.
        
        Args:
            change (int): Amount to change the relationship level by
            companion_name (str, optional): Name of the companion. If None, uses current companion.
            
        Returns:
            int: New relationship level
        """
        if companion_name is None:
            companion_name = self.get_current_companion_name()
        
        # Ensure current relationships exist
        if "current" not in self.relationship_levels:
            self.relationship_levels["current"] = {}
        
        # Get current relationship level
        current_level = self.relationship_levels["current"].get(companion_name, 0)
        
        # Update relationship level, clamping to 0-100
        new_level = max(0, min(100, current_level + change))
        self.relationship_levels["current"][companion_name] = new_level
        
        # Save updated relationships
        self._save_relationship_levels()
        
        return new_level
    
    def generate_dialogue(self, context, prompt_type):
        """
        Generate dialogue for the current companion.
        
        Args:
            context (dict): Game context information
            prompt_type (str): Type of dialogue to generate
            
        Returns:
            str: Generated dialogue
        """
        # Get relationship level with current companion
        relationship_level = self.get_relationship_level()
        
        # Generate dialogue
        return self.companion_handler.generate_companion_dialogue(context, prompt_type, relationship_level)
    
    def handle_player_death(self):
        """
        Handle player death by advancing the timeline.
        
        Returns:
            dict: Information about the new timeline position
        """
        # Archive current relationships
        self._archive_relationships()
        
        # Advance the timeline
        new_timeline = self.companion_handler.advance_timeline()
        
        # Reset current relationships
        self.relationship_levels["current"] = {}
        self._save_relationship_levels()
        
        return {
            "age": new_timeline.get("age"),
            "year": new_timeline.get("year"),
            "companion": new_timeline.get("current_companion"),
            "player_generation": new_timeline.get("player_generation")
        }
    
    def _archive_relationships(self):
        """Archive current relationships when the timeline advances."""
        # Get the current player generation
        player_generation = self.companion_handler.current_timeline.get("player_generation", 1)
        
        # Archive current relationships under the player generation
        if "current" in self.relationship_levels and self.relationship_levels["current"]:
            self.relationship_levels[f"generation_{player_generation}"] = self.relationship_levels["current"].copy()
            self._save_relationship_levels()
    
    def get_companion_info(self, companion_name=None):
        """
        Get information about a companion.
        
        Args:
            companion_name (str, optional): Name of the companion. If None, uses current companion.
            
        Returns:
            dict: Companion information
        """
        if companion_name is None:
            return self.companion_handler.current_companion
        
        # Load the specified companion
        age_folder = self.companion_handler._get_age_folder(self.companion_handler.current_timeline.get("age", "First Age"))
        
        # Convert companion name to filename (lowercase, no spaces)
        filename = companion_name.split()[0].lower() + ".md"
        companion_path = self.companion_handler.companions_path / age_folder / filename
        
        if not companion_path.exists():
            logger.warning(f"Companion profile not found at {companion_path}")
            return {"name": companion_name, "personality": "Noble and wise"}
        
        # Parse the markdown file to extract companion information
        with open(companion_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Extract companion information from markdown
        companion = {"name": companion_name}
        
        # Extract basic information
        if "## Basic Information" in content:
            basic_info = content.split("## Basic Information")[1].split("##")[0]
            
            # Extract race
            if "**Race**:" in basic_info:
                companion["race"] = basic_info.split("**Race**:")[1].split("\n")[0].strip()
            
            # Extract title
            if "**Title**:" in basic_info:
                companion["title"] = basic_info.split("**Title**:")[1].split("\n")[0].strip()
        
        # Extract personality
        if "## Personality" in content:
            personality_section = content.split("## Personality")[1].split("##")[0]
            companion["personality"] = personality_section.strip()
        
        return companion
    
    def register_mcp_endpoints(self, mcp_server):
        """
        Register MCP endpoints for the Ages of Arda integration.
        
        Args:
            mcp_server: The MCP server instance
        """
        # Register endpoints
        mcp_server.register_endpoint("ages/companion/dialogue", self._handle_dialogue_request)
        mcp_server.register_endpoint("ages/companion/info", self._handle_companion_info_request)
        mcp_server.register_endpoint("ages/timeline/info", self._handle_timeline_info_request)
        mcp_server.register_endpoint("ages/relationship/update", self._handle_relationship_update_request)
        mcp_server.register_endpoint("ages/player/death", self._handle_player_death_request)
        
        logger.info("Registered Ages of Arda MCP endpoints")
    
    def _handle_dialogue_request(self, request):
        """Handle a dialogue generation request."""
        # Extract request parameters
        context = request.get("context", {})
        prompt_type = request.get("prompt_type", "greeting")
        
        # Generate dialogue
        dialogue = self.generate_dialogue(context, prompt_type)
        
        return {
            "dialogue": dialogue,
            "companion": self.get_current_companion_name(),
            "relationship_level": self.get_relationship_level()
        }
    
    def _handle_companion_info_request(self, request):
        """Handle a companion info request."""
        # Extract request parameters
        companion_name = request.get("companion_name")
        
        # Get companion info
        companion_info = self.get_companion_info(companion_name)
        
        return {
            "companion": companion_info,
            "relationship_level": self.get_relationship_level(companion_name)
        }
    
    def _handle_timeline_info_request(self, request):
        """Handle a timeline info request."""
        # Get current age and year
        timeline_info = self.get_current_age_and_year()
        
        # Add current companion
        timeline_info["companion"] = self.get_current_companion_name()
        
        # Add player generation
        timeline_info["player_generation"] = self.companion_handler.current_timeline.get("player_generation", 1)
        
        return timeline_info
    
    def _handle_relationship_update_request(self, request):
        """Handle a relationship update request."""
        # Extract request parameters
        change = request.get("change", 0)
        companion_name = request.get("companion_name")
        
        # Update relationship level
        new_level = self.update_relationship_level(change, companion_name)
        
        return {
            "companion": companion_name or self.get_current_companion_name(),
            "relationship_level": new_level
        }
    
    def _handle_player_death_request(self, request):
        """Handle a player death request."""
        # Handle player death
        new_timeline = self.handle_player_death()
        
        return new_timeline


# Example usage
if __name__ == "__main__":
    # Initialize the Ages of Arda integration
    integration = AgesOfArdaIntegration("../../memory-bank")
    
    # Example dialogue generation
    context = {
        "location": "A dark cavern",
        "enemies_nearby": True,
        "player_health": 50,
        "discovered_item": "Ancient sword"
    }
    
    dialogue = integration.generate_dialogue(context, "discovery")
    print(f"{integration.get_current_companion_name()}: {dialogue}")
    
    # Example relationship update
    new_level = integration.update_relationship_level(5)
    print(f"Relationship level with {integration.get_current_companion_name()}: {new_level}")
    
    # Example player death
    new_timeline = integration.handle_player_death()
    print(f"Advanced to: {new_timeline['age']} Year {new_timeline['year']} - {new_timeline['companion']}") 