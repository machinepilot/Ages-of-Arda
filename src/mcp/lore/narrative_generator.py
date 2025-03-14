"""
Narrative Generator Module

This module provides tools for generating narrative content based on lore from
the memory bank. It integrates with the MCP server to provide lore-driven
narrative generation capabilities.
"""

import os
import sys
import json
import logging
import random
from pathlib import Path
from typing import Dict, List, Optional, Union, Any

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class NarrativeGenerator:
    """
    Generates narrative content based on lore from the memory bank.
    Provides tools for the MCP server to create lore-driven gameplay elements.
    """
    
    def __init__(self, memory_bank_path: str, llm_client=None):
        """
        Initialize the narrative generator.
        
        Args:
            memory_bank_path: Path to the memory bank directory
            llm_client: Client for LLM API calls (optional)
        """
        self.memory_bank_path = Path(memory_bank_path)
        self.llm_client = llm_client
        self.lore_cache = {}
        self.template_cache = {}
        
        # Load narrative templates
        self._load_templates()
    
    def _load_templates(self) -> None:
        """Load narrative templates from the memory bank."""
        template_dir = self.memory_bank_path / "templates"
        
        if not template_dir.exists():
            logger.warning(f"Template directory not found at {template_dir}")
            return
        
        for template_file in template_dir.glob("*.json"):
            try:
                with open(template_file, "r", encoding="utf-8") as f:
                    templates = json.load(f)
                    template_type = template_file.stem
                    self.template_cache[template_type] = templates
                    logger.info(f"Loaded {len(templates)} templates for {template_type}")
            except (json.JSONDecodeError, IOError) as e:
                logger.error(f"Error loading template file {template_file}: {e}")
    
    def _load_lore_for_age(self, age: str) -> Dict[str, Any]:
        """
        Load lore for a specific age.
        
        Args:
            age: The age identifier (e.g., 'first_age', 'third_age')
            
        Returns:
            Dictionary of lore data for the age
        """
        if age in self.lore_cache:
            return self.lore_cache[age]
        
        lore_path = self.memory_bank_path / "lore" / age
        
        if not lore_path.exists():
            logger.warning(f"Lore directory for {age} not found at {lore_path}")
            return {}
        
        lore_data = {
            "characters": {},
            "locations": {},
            "artifacts": {},
            "events": {}
        }
        
        # Load character lore
        char_dir = lore_path / "characters"
        if char_dir.exists():
            for char_file in char_dir.glob("*.json"):
                try:
                    with open(char_file, "r", encoding="utf-8") as f:
                        character = json.load(f)
                        character_name = char_file.stem
                        lore_data["characters"][character_name] = character
                except (json.JSONDecodeError, IOError) as e:
                    logger.error(f"Error loading character file {char_file}: {e}")
        
        # Load location lore (similar pattern for other lore types)
        loc_dir = lore_path / "locations"
        if loc_dir.exists():
            for loc_file in loc_dir.glob("*.json"):
                try:
                    with open(loc_file, "r", encoding="utf-8") as f:
                        location = json.load(f)
                        location_name = loc_file.stem
                        lore_data["locations"][location_name] = location
                except (json.JSONDecodeError, IOError) as e:
                    logger.error(f"Error loading location file {loc_file}: {e}")
        
        # Cache the loaded lore
        self.lore_cache[age] = lore_data
        return lore_data
    
    def generate_location_description(self, location_name: str, age: str, context: Dict[str, Any] = None) -> str:
        """
        Generate a description for a location based on lore.
        
        Args:
            location_name: Name of the location
            age: Current age (first_age, third_age, etc.)
            context: Additional context about the player, game state, etc.
            
        Returns:
            A narrative description of the location
        """
        # Get lore for the location
        lore_data = self._load_lore_for_age(age)
        location_lore = lore_data.get("locations", {}).get(location_name)
        
        if not location_lore:
            logger.warning(f"No lore found for location {location_name} in {age}")
            return self._generate_fallback_description("location", location_name, age)
        
        # Attempt to generate with LLM if available
        if self.llm_client:
            return self._generate_location_description_with_llm(location_name, location_lore, age, context)
        
        # Fall back to template-based generation
        return self._generate_location_description_from_template(location_name, location_lore, age)
    
    def _generate_location_description_with_llm(self, location_name: str, location_lore: Dict[str, Any], 
                                               age: str, context: Dict[str, Any] = None) -> str:
        """
        Generate a location description using the LLM.
        
        Args:
            location_name: Name of the location
            location_lore: Lore data for the location
            age: Current age
            context: Additional context about the player, game state, etc.
            
        Returns:
            A narrative description of the location
        """
        try:
            # Create a prompt for the LLM
            prompt = f"""
            [LOCATION_NAME]
            {location_name}
            [/LOCATION_NAME]
            
            [LOCATION_LORE]
            {json.dumps(location_lore, indent=2)}
            [/LOCATION_LORE]
            
            [AGE]
            {age}
            [/AGE]
            """
            
            if context:
                prompt += f"""
                [CONTEXT]
                {json.dumps(context, indent=2)}
                [/CONTEXT]
                """
            
            prompt += """
            [INSTRUCTION]
            Generate a vivid, atmospheric description of this location from Tolkien's world.
            The description should be 2-3 paragraphs long and include sensory details.
            Stay true to the lore and the feel of the age. Focus on creating a mood that
            reflects the history and significance of the place.
            [/INSTRUCTION]
            """
            
            # Call the LLM
            response = self.llm_client.generate(prompt)
            
            # Extract just the description from the response
            # This assumes the LLM follows instructions and provides just the description
            description = response.strip()
            
            return description
            
        except Exception as e:
            logger.error(f"Error generating location description with LLM: {e}")
            return self._generate_location_description_from_template(location_name, location_lore, age)
    
    def _generate_location_description_from_template(self, location_name: str, 
                                                   location_lore: Dict[str, Any], age: str) -> str:
        """
        Generate a location description using templates.
        
        Args:
            location_name: Name of the location
            location_lore: Lore data for the location
            age: Current age
            
        Returns:
            A narrative description of the location
        """
        templates = self.template_cache.get("location_descriptions", [])
        
        if not templates:
            return f"You see {location_name}, a location from {age}."
        
        # Select a template based on location type if available
        location_type = location_lore.get("type", "unknown")
        matching_templates = [t for t in templates if t.get("type") == location_type]
        
        if not matching_templates:
            matching_templates = templates
        
        template = random.choice(matching_templates)
        description = template["template"]
        
        # Replace placeholders with actual data
        replacements = {
            "{name}": location_name,
            "{age}": age.replace("_", " ").title(),
            "{description}": location_lore.get("description", ""),
            "{history}": location_lore.get("history", ""),
            "{notable_features}": location_lore.get("notable_features", "")
        }
        
        for placeholder, value in replacements.items():
            description = description.replace(placeholder, value)
        
        return description
    
    def _generate_fallback_description(self, entity_type: str, entity_name: str, age: str) -> str:
        """
        Generate a fallback description when no lore is available.
        
        Args:
            entity_type: Type of entity (location, character, artifact)
            entity_name: Name of the entity
            age: Current age
            
        Returns:
            A simple fallback description
        """
        age_name = age.replace("_", " ").title()
        
        if entity_type == "location":
            return f"You see {entity_name}, a mysterious place from the {age_name}."
        elif entity_type == "character":
            return f"This is {entity_name}, a figure from the {age_name}."
        elif entity_type == "artifact":
            return f"Before you is {entity_name}, an item of power from the {age_name}."
        else:
            return f"You encounter {entity_name} from the {age_name}."
    
    def generate_companion_dialogue(self, companion_name: str, age: str, 
                                   topic: str = None, relationship_level: int = 0,
                                   context: Dict[str, Any] = None) -> str:
        """
        Generate dialogue for a companion based on lore and context.
        
        Args:
            companion_name: Name of the companion
            age: Current age
            topic: Optional topic for the dialogue
            relationship_level: Level of relationship with the player (0-5)
            context: Additional context about the player, game state, etc.
            
        Returns:
            Dialogue text for the companion
        """
        # Get lore for the companion
        lore_data = self._load_lore_for_age(age)
        companion_lore = lore_data.get("characters", {}).get(companion_name)
        
        if not companion_lore:
            logger.warning(f"No lore found for companion {companion_name} in {age}")
            return f"{companion_name}: I don't have much to say about that."
        
        # Try LLM generation if available
        if self.llm_client:
            return self._generate_dialogue_with_llm(companion_name, companion_lore, 
                                                  age, topic, relationship_level, context)
        
        # Fall back to template-based generation
        return self._generate_dialogue_from_template(companion_name, companion_lore, 
                                                   age, topic, relationship_level)
    
    def _generate_dialogue_with_llm(self, companion_name: str, companion_lore: Dict[str, Any],
                                  age: str, topic: str = None, relationship_level: int = 0,
                                  context: Dict[str, Any] = None) -> str:
        """
        Generate companion dialogue using the LLM.
        
        Args:
            companion_name: Name of the companion
            companion_lore: Lore data for the companion
            age: Current age
            topic: Optional topic for the dialogue
            relationship_level: Level of relationship with the player (0-5)
            context: Additional context about the player, game state, etc.
            
        Returns:
            Dialogue text for the companion
        """
        try:
            # Create a prompt for the LLM
            prompt = f"""
            [COMPANION]
            {companion_name}
            [/COMPANION]
            
            [COMPANION_LORE]
            {json.dumps(companion_lore, indent=2)}
            [/COMPANION_LORE]
            
            [AGE]
            {age}
            [/AGE]
            
            [RELATIONSHIP_LEVEL]
            {relationship_level} (0=stranger, 5=close ally)
            [/RELATIONSHIP_LEVEL]
            """
            
            if topic:
                prompt += f"""
                [TOPIC]
                {topic}
                [/TOPIC]
                """
            
            if context:
                prompt += f"""
                [CONTEXT]
                {json.dumps(context, indent=2)}
                [/CONTEXT]
                """
            
            prompt += """
            [INSTRUCTION]
            Generate a single dialogue line for this companion that feels authentic to their
            character in Tolkien's world. The dialogue should reflect their personality,
            background, and relationship with the player. If a topic is specified, the
            dialogue should address that topic. Keep the response concise and in character.
            Format the response as: "{Character_Name}: {Dialogue text}"
            [/INSTRUCTION]
            """
            
            # Call the LLM
            response = self.llm_client.generate(prompt)
            
            # Clean up the response
            dialogue = response.strip()
            
            # Ensure proper formatting
            if ":" not in dialogue:
                dialogue = f"{companion_name}: {dialogue}"
            
            return dialogue
            
        except Exception as e:
            logger.error(f"Error generating dialogue with LLM: {e}")
            return self._generate_dialogue_from_template(companion_name, companion_lore, 
                                                      age, topic, relationship_level)
    
    def _generate_dialogue_from_template(self, companion_name: str, companion_lore: Dict[str, Any],
                                       age: str, topic: str = None, relationship_level: int = 0) -> str:
        """
        Generate companion dialogue using templates.
        
        Args:
            companion_name: Name of the companion
            companion_lore: Lore data for the companion
            age: Current age
            topic: Optional topic for the dialogue
            relationship_level: Level of relationship with the player (0-5)
            
        Returns:
            Dialogue text for the companion
        """
        templates = self.template_cache.get("companion_dialogue", [])
        
        if not templates:
            return f"{companion_name}: Well met, traveler."
        
        # Filter templates by relationship level and topic
        matching_templates = [t for t in templates 
                             if t.get("min_relationship", 0) <= relationship_level 
                             and (not topic or t.get("topic") == topic or t.get("topic") == "general")]
        
        if not matching_templates:
            matching_templates = [t for t in templates if t.get("topic") == "general"]
        
        if not matching_templates:
            matching_templates = templates
        
        template = random.choice(matching_templates)
        dialogue = template["template"]
        
        # Replace placeholders with actual data
        replacements = {
            "{name}": companion_name,
            "{race}": companion_lore.get("race", ""),
            "{profession}": companion_lore.get("profession", ""),
            "{home}": companion_lore.get("home", ""),
            "{age}": age.replace("_", " ").title(),
            "{backstory}": companion_lore.get("backstory", "")
        }
        
        for placeholder, value in replacements.items():
            dialogue = dialogue.replace(placeholder, str(value))
        
        return f"{companion_name}: {dialogue}"
    
    def generate_quest_description(self, quest_type: str, location: str, 
                                  age: str, target: str = None,
                                  context: Dict[str, Any] = None) -> Dict[str, str]:
        """
        Generate a quest description based on lore and game context.
        
        Args:
            quest_type: Type of quest (e.g., "rescue", "retrieve", "defeat")
            location: Location name where the quest takes place
            age: Current age
            target: Optional target of the quest (character, item, enemy)
            context: Additional context about the player, game state, etc.
            
        Returns:
            Dictionary with quest title and description
        """
        # Attempt to generate with LLM if available
        if self.llm_client:
            return self._generate_quest_with_llm(quest_type, location, age, target, context)
        
        # Fall back to template-based generation
        return self._generate_quest_from_template(quest_type, location, age, target)
    
    def _generate_quest_with_llm(self, quest_type: str, location: str, 
                               age: str, target: str = None,
                               context: Dict[str, Any] = None) -> Dict[str, str]:
        """
        Generate a quest using the LLM.
        
        Args:
            quest_type: Type of quest
            location: Location name
            age: Current age
            target: Optional quest target
            context: Additional context
            
        Returns:
            Dictionary with quest title and description
        """
        try:
            # Get lore data
            lore_data = self._load_lore_for_age(age)
            location_lore = lore_data.get("locations", {}).get(location, {})
            
            target_lore = {}
            if target:
                target_lore = (lore_data.get("characters", {}).get(target) or 
                             lore_data.get("artifacts", {}).get(target) or {})
            
            # Create a prompt for the LLM
            prompt = f"""
            [QUEST_TYPE]
            {quest_type}
            [/QUEST_TYPE]
            
            [LOCATION]
            {location}
            [/LOCATION]
            
            [LOCATION_LORE]
            {json.dumps(location_lore, indent=2)}
            [/LOCATION_LORE]
            
            [AGE]
            {age}
            [/AGE]
            """
            
            if target:
                prompt += f"""
                [TARGET]
                {target}
                [/TARGET]
                
                [TARGET_LORE]
                {json.dumps(target_lore, indent=2)}
                [/TARGET_LORE]
                """
            
            if context:
                prompt += f"""
                [CONTEXT]
                {json.dumps(context, indent=2)}
                [/CONTEXT]
                """
            
            prompt += """
            [INSTRUCTION]
            Generate a quest appropriate for Tolkien's Middle-earth based on the provided information.
            The quest should include:
            1. A title (short and evocative)
            2. A description (1-2 paragraphs explaining the quest)
            
            Format your response as a JSON object with "title" and "description" fields.
            Make sure the quest feels authentic to the age and location in Tolkien's world.
            [/INSTRUCTION]
            """
            
            # Call the LLM
            response = self.llm_client.generate(prompt)
            
            # Parse the JSON response
            try:
                quest_data = json.loads(response)
                if "title" in quest_data and "description" in quest_data:
                    return quest_data
            except json.JSONDecodeError:
                # If response is not valid JSON, extract title and description manually
                lines = response.strip().split("\n")
                title = lines[0].strip().replace("#", "").strip()
                description = "\n".join(lines[1:]).strip()
                return {"title": title, "description": description}
            
            logger.warning("Failed to parse LLM response for quest generation")
            return self._generate_quest_from_template(quest_type, location, age, target)
            
        except Exception as e:
            logger.error(f"Error generating quest with LLM: {e}")
            return self._generate_quest_from_template(quest_type, location, age, target)
    
    def _generate_quest_from_template(self, quest_type: str, location: str, 
                                    age: str, target: str = None) -> Dict[str, str]:
        """
        Generate a quest using templates.
        
        Args:
            quest_type: Type of quest
            location: Location name
            age: Current age
            target: Optional quest target
            
        Returns:
            Dictionary with quest title and description
        """
        templates = self.template_cache.get("quests", [])
        
        if not templates:
            return {
                "title": f"{quest_type.title()} Quest",
                "description": f"A quest to {quest_type} in {location}."
            }
        
        # Filter templates by quest type and age
        matching_templates = [t for t in templates 
                             if t.get("type") == quest_type 
                             and (not t.get("age") or t.get("age") == age)]
        
        if not matching_templates:
            matching_templates = [t for t in templates if t.get("type") == quest_type]
        
        if not matching_templates:
            matching_templates = templates
        
        template = random.choice(matching_templates)
        
        title = template.get("title_template", "{quest_type} at {location}")
        description = template.get("description_template", "A quest to {quest_type} in {location}.")
        
        # Replace placeholders
        replacements = {
            "{quest_type}": quest_type.lower(),
            "{location}": location,
            "{age}": age.replace("_", " ").title(),
            "{target}": target if target else "the target"
        }
        
        for placeholder, value in replacements.items():
            title = title.replace(placeholder, value)
            description = description.replace(placeholder, value)
        
        return {
            "title": title,
            "description": description
        }
    
    def register_mcp_endpoints(self, mcp_server) -> None:
        """
        Register narrative generation endpoints with the MCP server.
        
        Args:
            mcp_server: The MCP server instance
        """
        mcp_server.register_endpoint("ages/narrative/location", self._handle_location_description_request)
        mcp_server.register_endpoint("ages/narrative/companion", self._handle_companion_dialogue_request)
        mcp_server.register_endpoint("ages/narrative/quest", self._handle_quest_generation_request)
    
    def _handle_location_description_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle MCP request for location description.
        
        Args:
            request: The MCP request data
            
        Returns:
            Response with the generated description
        """
        location_name = request.get("location_name")
        age = request.get("age")
        context = request.get("context", {})
        
        if not location_name or not age:
            return {"error": "Missing required parameters: location_name and age"}
        
        description = self.generate_location_description(location_name, age, context)
        
        return {
            "description": description,
            "location": location_name,
            "age": age
        }
    
    def _handle_companion_dialogue_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle MCP request for companion dialogue.
        
        Args:
            request: The MCP request data
            
        Returns:
            Response with the generated dialogue
        """
        companion_name = request.get("companion_name")
        age = request.get("age")
        topic = request.get("topic")
        relationship_level = request.get("relationship_level", 0)
        context = request.get("context", {})
        
        if not companion_name or not age:
            return {"error": "Missing required parameters: companion_name and age"}
        
        dialogue = self.generate_companion_dialogue(companion_name, age, topic, relationship_level, context)
        
        return {
            "dialogue": dialogue,
            "companion": companion_name,
            "age": age,
            "topic": topic
        }
    
    def _handle_quest_generation_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle MCP request for quest generation.
        
        Args:
            request: The MCP request data
            
        Returns:
            Response with the generated quest
        """
        quest_type = request.get("quest_type")
        location = request.get("location")
        age = request.get("age")
        target = request.get("target")
        context = request.get("context", {})
        
        if not quest_type or not location or not age:
            return {"error": "Missing required parameters: quest_type, location, and age"}
        
        quest = self.generate_quest_description(quest_type, location, age, target, context)
        
        return {
            "title": quest.get("title"),
            "description": quest.get("description"),
            "quest_type": quest_type,
            "location": location,
            "age": age,
            "target": target
        } 