"""
Companion Lore Integration Module for Ages of Arda

This module integrates the lore system with the companion dialogue system,
allowing companions to reference lore from Tolkien's works in their dialogue.
"""

import os
import sys
import logging
from pathlib import Path

# Add the parent directory to the Python path
sys.path.append(str(Path(__file__).parent.parent.parent))

# Import the lore manager
from memory_bank.lore.lore_integration import LoreManager

# Import the companion handler
try:
    from src.mcp.companions.companion_handler import CompanionHandler
    from src.mcp.server.ages_integration import AgesOfArdaIntegration
except ImportError:
    # If the companion handler is not found, create a mock class
    class CompanionHandler:
        def __init__(self, *args, **kwargs):
            pass
    
    class AgesOfArdaIntegration:
        def __init__(self, *args, **kwargs):
            pass

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class LoreEnhancedCompanionHandler(CompanionHandler):
    """
    Enhanced companion handler that incorporates lore into dialogue.
    """
    
    def __init__(self, memory_bank_path, llm_client=None):
        """
        Initialize the lore-enhanced companion handler.
        
        Args:
            memory_bank_path (str): Path to the memory bank directory
            llm_client: Client for LLM API calls (optional)
        """
        super().__init__(memory_bank_path, llm_client)
        
        # Initialize the lore manager
        lore_dir = Path(memory_bank_path) / "lore"
        self.lore_manager = LoreManager(lore_dir)
        
        logger.info(f"Initialized LoreEnhancedCompanionHandler with lore directory: {lore_dir}")
    
    def generate_companion_dialogue(self, context, prompt_type, relationship_level=0):
        """
        Generate dialogue for the current companion based on context and prompt type,
        enhanced with lore references.
        
        Args:
            context (dict): Game context information
            prompt_type (str): Type of dialogue to generate (e.g., "greeting", "combat", "discovery")
            relationship_level (int): Current relationship level with companion (0-100)
            
        Returns:
            str: Generated companion dialogue
        """
        # Generate base dialogue using the parent method
        dialogue = super().generate_companion_dialogue(context, prompt_type, relationship_level)
        
        # Enhance dialogue with lore references
        age_folder = self._get_age_folder(self.current_timeline.get("age", "First Age"))
        companion_name = self.current_timeline.get("current_companion", "Finrod Felagund")
        
        enhanced_dialogue = self.lore_manager.enhance_companion_dialogue(
            companion_name,
            age_folder,
            dialogue,
            context
        )
        
        return enhanced_dialogue
    
    def get_lore_for_topic(self, topic_type, topic_name):
        """
        Get lore for a specific topic.
        
        Args:
            topic_type (str): Type of topic (character, location, artifact)
            topic_name (str): Name of the topic
            
        Returns:
            dict: Lore data for the topic
        """
        age_folder = self._get_age_folder(self.current_timeline.get("age", "First Age"))
        
        if topic_type.lower() == "character":
            return self.lore_manager.get_character_lore(topic_name, age_folder)
        elif topic_type.lower() == "location":
            return self.lore_manager.get_location_lore(topic_name, age_folder)
        elif topic_type.lower() == "artifact":
            return self.lore_manager.get_artifact_lore(topic_name, age_folder)
        else:
            return {}
    
    def generate_lore_dialogue(self, topic_type, topic_name, relationship_level=0):
        """
        Generate dialogue specifically about a lore topic.
        
        Args:
            topic_type (str): Type of topic (character, location, artifact)
            topic_name (str): Name of the topic
            relationship_level (int): Current relationship level with companion (0-100)
            
        Returns:
            str: Generated lore dialogue
        """
        # Get lore for the topic
        lore_data = self.get_lore_for_topic(topic_type, topic_name)
        
        if not lore_data:
            return f"I know little of {topic_name}. Perhaps it is a tale yet untold."
        
        # Generate dialogue based on the lore
        age_folder = self._get_age_folder(self.current_timeline.get("age", "First Age"))
        companion_name = self.current_timeline.get("current_companion", "Finrod Felagund")
        
        # If we have an LLM client, use it to generate dialogue
        if self.llm_client:
            return self._generate_lore_dialogue_with_llm(topic_type, topic_name, lore_data, relationship_level)
        
        # Otherwise, use template-based dialogue
        return self._generate_lore_dialogue_from_templates(topic_type, topic_name, lore_data, relationship_level)
    
    def _generate_lore_dialogue_with_llm(self, topic_type, topic_name, lore_data, relationship_level):
        """
        Generate lore dialogue using the LLM client.
        
        Args:
            topic_type (str): Type of topic (character, location, artifact)
            topic_name (str): Name of the topic
            lore_data (dict): Lore data for the topic
            relationship_level (int): Current relationship level with companion
            
        Returns:
            str: Generated lore dialogue
        """
        import json
        
        companion = self.current_companion
        
        # Prepare the prompt
        prompt = f"""
[CHARACTER]
Name: {companion.get('name', 'Unknown')}
Race: {companion.get('race', 'Elf')}
Title: {companion.get('title', '')}
Personality: {companion.get('personality', 'Noble and wise')}
Speech Pattern: {companion.get('speech_pattern', 'Formal but warm')}
[/CHARACTER]

[RELATIONSHIP]
Level: {relationship_level}/100
Stage: {"Stranger" if relationship_level < 20 else "Acquaintance" if relationship_level < 50 else "Friend" if relationship_level < 80 else "Trusted Ally"}
[/RELATIONSHIP]

[LORE]
Topic Type: {topic_type}
Topic Name: {topic_name}
Lore Data: {json.dumps(lore_data, indent=2)}
[/LORE]

[INSTRUCTION]
Generate dialogue for {companion.get('name', 'the companion')} sharing knowledge about {topic_name}.
The dialogue should reflect the character's personality, speech pattern, and current relationship level with the player.
Incorporate specific details from the lore data provided.
Respond only with the character's dialogue, without any additional text or explanation.
[/INSTRUCTION]
"""
        
        try:
            # Call the LLM client
            response = self.llm_client.generate_text(prompt)
            return response.strip()
        except Exception as e:
            logger.error(f"Error generating lore dialogue with LLM: {e}")
            # Fall back to template-based dialogue
            return self._generate_lore_dialogue_from_templates(topic_type, topic_name, lore_data, relationship_level)
    
    def _generate_lore_dialogue_from_templates(self, topic_type, topic_name, lore_data, relationship_level):
        """
        Generate lore dialogue using templates.
        
        Args:
            topic_type (str): Type of topic (character, location, artifact)
            topic_name (str): Name of the topic
            lore_data (dict): Lore data for the topic
            relationship_level (int): Current relationship level with companion
            
        Returns:
            str: Generated lore dialogue
        """
        import random
        
        companion_name = self.current_timeline.get("current_companion", "Finrod Felagund")
        
        # Templates for different topic types
        character_templates = [
            f"Ah, {topic_name}. {random.choice(['A name from the ancient tales.', 'I have heard tales of this one.', 'The legends speak of such a one.'])} ",
            f"{topic_name}... {random.choice(['A figure of great importance in our history.', 'One whose deeds are remembered still.', 'A name that echoes through the ages.'])} "
        ]
        
        location_templates = [
            f"{topic_name}. {random.choice(['A place of great significance.', 'I have walked those lands in days past.', 'Many tales are told of that place.'])} ",
            f"You speak of {topic_name}. {random.choice(['A realm of wonder and peril.', 'Few now remember its glory.', 'Its name stirs memories long forgotten.'])} "
        ]
        
        artifact_templates = [
            f"The {topic_name}... {random.choice(['An artifact of great power.', 'Few have laid eyes upon such a treasure.', 'Its craftsmanship is beyond compare.'])} ",
            f"You ask of the {topic_name}? {random.choice(['A relic from an age long past.', 'Its story is woven into the fabric of our history.', 'Many have sought it, few have found it.'])} "
        ]
        
        # Select template based on topic type
        if topic_type.lower() == "character":
            template = random.choice(character_templates)
        elif topic_type.lower() == "location":
            template = random.choice(location_templates)
        elif topic_type.lower() == "artifact":
            template = random.choice(artifact_templates)
        else:
            template = f"You ask about {topic_name}? "
        
        # Add lore details
        lore_details = ""
        
        for source, info in lore_data.items():
            if isinstance(info, str):
                # Extract a quote from the markdown content
                import re
                quotes = re.findall(r'> (.*?)\n', info)
                
                if quotes:
                    lore_details += f"It is said that \"{quotes[0]}\" "
                    break
            elif isinstance(info, dict):
                if "excerpts" in info:
                    for chapter, excerpt in info["excerpts"].items():
                        # Extract a sentence
                        import re
                        sentences = re.split(r'(?<=[.!?])\s+', excerpt)
                        
                        if sentences:
                            lore_details += f"The lore tells us: \"{sentences[0]}\" "
                            break
                    
                    if lore_details:
                        break
                
                if not lore_details and "appearances" in info:
                    appearances = info["appearances"]
                    if appearances:
                        lore_details += f"The tales speak of {topic_name} in {appearances[0]}. "
        
        # Add a personal touch based on relationship level
        personal_touch = ""
        
        if relationship_level >= 80:
            personal_touch = random.choice([
                "I share this knowledge with you as a trusted friend.",
                "Few are those to whom I would speak so openly of such matters.",
                "I am pleased to share these ancient tales with one such as yourself."
            ])
        elif relationship_level >= 50:
            personal_touch = random.choice([
                "I am glad to share this knowledge with you.",
                "It pleases me to speak of the old tales.",
                "There is much more to learn, if you wish to hear it."
            ])
        elif relationship_level >= 20:
            personal_touch = random.choice([
                "Perhaps one day I shall tell you more.",
                "There are many such tales, if you have the patience to hear them.",
                "The lore of old is vast and deep."
            ])
        else:
            personal_touch = random.choice([
                "But that is all I will say for now.",
                "The full tale is not for all ears.",
                "There is much more, but now is not the time."
            ])
        
        return template + lore_details + personal_touch


class LoreEnhancedAgesOfArdaIntegration(AgesOfArdaIntegration):
    """
    Enhanced Ages of Arda integration that incorporates lore into dialogue.
    """
    
    def __init__(self, memory_bank_path, llm_client=None):
        """
        Initialize the lore-enhanced Ages of Arda integration.
        
        Args:
            memory_bank_path (str): Path to the memory bank directory
            llm_client: Client for LLM API calls (optional)
        """
        # Override the companion handler with our enhanced version
        self.memory_bank_path = Path(memory_bank_path)
        self.companion_handler = LoreEnhancedCompanionHandler(memory_bank_path, llm_client)
        self.relationship_levels = self._load_relationship_levels()
        
        logger.info(f"Initialized LoreEnhancedAgesOfArdaIntegration with companion: {self.companion_handler.current_companion.get('name', 'Unknown')}")
    
    def register_mcp_endpoints(self, mcp_server):
        """
        Register MCP endpoints for the Ages of Arda integration.
        
        Args:
            mcp_server: The MCP server instance
        """
        # Register standard endpoints
        super().register_mcp_endpoints(mcp_server)
        
        # Register lore-specific endpoints
        mcp_server.register_endpoint("ages/lore/character", self._handle_character_lore_request)
        mcp_server.register_endpoint("ages/lore/location", self._handle_location_lore_request)
        mcp_server.register_endpoint("ages/lore/artifact", self._handle_artifact_lore_request)
        
        logger.info("Registered lore-enhanced Ages of Arda MCP endpoints")
    
    def _handle_character_lore_request(self, request):
        """Handle a character lore request."""
        # Extract request parameters
        character_name = request.get("character_name")
        
        if not character_name:
            return {"error": "Character name is required"}
        
        # Generate lore dialogue
        dialogue = self.companion_handler.generate_lore_dialogue("character", character_name, self.get_relationship_level())
        
        return {
            "dialogue": dialogue,
            "companion": self.get_current_companion_name(),
            "relationship_level": self.get_relationship_level()
        }
    
    def _handle_location_lore_request(self, request):
        """Handle a location lore request."""
        # Extract request parameters
        location_name = request.get("location_name")
        
        if not location_name:
            return {"error": "Location name is required"}
        
        # Generate lore dialogue
        dialogue = self.companion_handler.generate_lore_dialogue("location", location_name, self.get_relationship_level())
        
        return {
            "dialogue": dialogue,
            "companion": self.get_current_companion_name(),
            "relationship_level": self.get_relationship_level()
        }
    
    def _handle_artifact_lore_request(self, request):
        """Handle an artifact lore request."""
        # Extract request parameters
        artifact_name = request.get("artifact_name")
        
        if not artifact_name:
            return {"error": "Artifact name is required"}
        
        # Generate lore dialogue
        dialogue = self.companion_handler.generate_lore_dialogue("artifact", artifact_name, self.get_relationship_level())
        
        return {
            "dialogue": dialogue,
            "companion": self.get_current_companion_name(),
            "relationship_level": self.get_relationship_level()
        }


# Example usage
if __name__ == "__main__":
    # Initialize the lore-enhanced Ages of Arda integration
    integration = LoreEnhancedAgesOfArdaIntegration("../../")
    
    # Example lore dialogue generation
    character_dialogue = integration.companion_handler.generate_lore_dialogue("character", "Finrod")
    print(f"{integration.get_current_companion_name()} on Finrod: {character_dialogue}")
    
    location_dialogue = integration.companion_handler.generate_lore_dialogue("location", "Nargothrond")
    print(f"{integration.get_current_companion_name()} on Nargothrond: {location_dialogue}")
    
    artifact_dialogue = integration.companion_handler.generate_lore_dialogue("artifact", "Silmaril")
    print(f"{integration.get_current_companion_name()} on Silmaril: {artifact_dialogue}") 