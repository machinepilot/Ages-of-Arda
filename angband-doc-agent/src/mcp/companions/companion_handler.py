"""
Companion Dialogue Handler for Ages of Arda

This module handles the generation of companion dialogue and interactions
based on the current game state, companion profile, and relationship status.
"""

import os
import json
import markdown
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class CompanionHandler:
    """Handles companion dialogue and interactions for the Ages of Arda variant."""
    
    def __init__(self, memory_bank_path, llm_client=None):
        """
        Initialize the companion handler.
        
        Args:
            memory_bank_path (str): Path to the memory bank directory
            llm_client: Client for LLM API calls (optional)
        """
        self.memory_bank_path = Path(memory_bank_path)
        self.companions_path = self.memory_bank_path / "companions"
        self.ages_path = self.memory_bank_path / "ages"
        self.llm_client = llm_client
        self.current_timeline = self._load_current_timeline()
        self.current_companion = self._load_current_companion()
        
        logger.info(f"Initialized CompanionHandler with current companion: {self.current_companion.get('name', 'Unknown')}")
    
    def _load_current_timeline(self):
        """Load the current timeline state from the memory bank."""
        timeline_path = self.ages_path / "current_timeline.md"
        
        if not timeline_path.exists():
            logger.warning(f"Timeline file not found at {timeline_path}")
            return {
                "age": "First Age",
                "year": 1,
                "current_companion": "Finrod Felagund",
                "player_generation": 1
            }
        
        # Parse the markdown file to extract timeline information
        with open(timeline_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Simple parsing of the markdown content
        timeline = {}
        
        if "## Active Timeline Position" in content:
            position_section = content.split("## Active Timeline Position")[1].split("##")[0]
            
            # Extract age
            if "Age:" in position_section:
                timeline["age"] = position_section.split("Age:")[1].split("\n")[0].strip()
            
            # Extract year
            if "Year:" in position_section:
                try:
                    timeline["year"] = int(position_section.split("Year:")[1].split("\n")[0].strip())
                except ValueError:
                    timeline["year"] = 1
            
            # Extract current companion
            if "Current Companion:" in position_section:
                timeline["current_companion"] = position_section.split("Current Companion:")[1].split("\n")[0].strip()
            
            # Extract player generation
            if "Player Generation:" in position_section:
                try:
                    timeline["player_generation"] = int(position_section.split("Player Generation:")[1].split("\n")[0].strip())
                except ValueError:
                    timeline["player_generation"] = 1
        
        return timeline
    
    def _load_current_companion(self):
        """Load the current companion profile based on the timeline."""
        age_folder = self._get_age_folder(self.current_timeline.get("age", "First Age"))
        companion_name = self.current_timeline.get("current_companion", "Finrod Felagund")
        
        # Convert companion name to filename (lowercase, no spaces)
        filename = companion_name.split()[0].lower() + ".md"
        companion_path = self.companions_path / age_folder / filename
        
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
        
        # Extract speech pattern
        if "## Speech Pattern" in content:
            speech_section = content.split("## Speech Pattern")[1].split("##")[0]
            companion["speech_pattern"] = speech_section.strip()
        
        # Extract dialogue examples
        if "## Dialogue Examples" in content:
            dialogue_section = content.split("## Dialogue Examples")[1]
            companion["dialogue_examples"] = dialogue_section.strip()
        
        return companion
    
    def _get_age_folder(self, age):
        """Convert age name to folder name."""
        age_map = {
            "First Age": "first_age",
            "Second Age": "second_age",
            "Third Age": "third_age"
        }
        return age_map.get(age, "first_age")
    
    def generate_companion_dialogue(self, context, prompt_type, relationship_level=0):
        """
        Generate dialogue for the current companion based on context and prompt type.
        
        Args:
            context (dict): Game context information
            prompt_type (str): Type of dialogue to generate (e.g., "greeting", "combat", "discovery")
            relationship_level (int): Current relationship level with companion (0-100)
            
        Returns:
            str: Generated companion dialogue
        """
        # If we have an LLM client, use it to generate dialogue
        if self.llm_client:
            return self._generate_dialogue_with_llm(context, prompt_type, relationship_level)
        
        # Otherwise, use template-based dialogue
        return self._generate_dialogue_from_templates(context, prompt_type, relationship_level)
    
    def _generate_dialogue_with_llm(self, context, prompt_type, relationship_level):
        """Generate dialogue using the LLM client."""
        # Prepare the prompt
        prompt = self._prepare_dialogue_prompt(context, prompt_type, relationship_level)
        
        try:
            # Call the LLM client
            response = self.llm_client.generate_text(prompt)
            return response.strip()
        except Exception as e:
            logger.error(f"Error generating dialogue with LLM: {e}")
            # Fall back to template-based dialogue
            return self._generate_dialogue_from_templates(context, prompt_type, relationship_level)
    
    def _prepare_dialogue_prompt(self, context, prompt_type, relationship_level):
        """Prepare a prompt for the LLM to generate companion dialogue."""
        companion = self.current_companion
        
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

[CONTEXT]
{json.dumps(context, indent=2)}
[/CONTEXT]

[INSTRUCTION]
Generate dialogue for {companion.get('name', 'the companion')} responding to a {prompt_type} situation.
The dialogue should reflect the character's personality, speech pattern, and current relationship level with the player.
Respond only with the character's dialogue, without any additional text or explanation.
[/INSTRUCTION]
"""
        return prompt
    
    def _generate_dialogue_from_templates(self, context, prompt_type, relationship_level):
        """Generate dialogue using templates from the companion profile."""
        companion = self.current_companion
        
        # Extract dialogue examples from companion profile
        dialogue_examples = companion.get("dialogue_examples", "")
        
        # Default responses for different prompt types
        default_responses = {
            "greeting": f"Well met, adventurer. I am {companion.get('name', 'your companion')}.",
            "combat": "Stand firm! We shall face this foe together.",
            "discovery": "This is a most interesting find.",
            "lore": "There are many tales of such things in the lore of my people.",
            "danger": "Beware! There is peril ahead.",
            "victory": "A well-earned triumph. You fought with valor.",
            "defeat": "We must retreat and recover our strength.",
            "artifact": "This item bears the mark of ancient craft.",
            "rest": "Let us rest a while and recover our strength."
        }
        
        # Try to find a matching dialogue example
        if prompt_type.lower() in dialogue_examples.lower():
            # Find the section that matches the prompt type
            sections = dialogue_examples.split("###")
            for section in sections:
                if prompt_type.lower() in section.lower():
                    # Extract the dialogue (everything after the first line)
                    lines = section.strip().split("\n")
                    if len(lines) > 1:
                        return "\n".join(lines[1:]).strip().strip('"')
        
        # Fall back to default response
        return default_responses.get(prompt_type.lower(), "I have nothing specific to say about that.")
    
    def advance_timeline(self):
        """
        Advance the timeline to the next companion after player death.
        
        Returns:
            dict: Updated timeline information
        """
        # Load the current timeline
        timeline = self._load_current_timeline()
        
        # Increment player generation
        timeline["player_generation"] = timeline.get("player_generation", 1) + 1
        
        # Determine the next companion based on the timeline
        age = timeline.get("age", "First Age")
        year = timeline.get("year", 1)
        
        # First Age: years 1-590
        if age == "First Age":
            if year < 540:  # Not at the end of First Age yet
                # Advance to next companion in First Age
                next_year = year + 60
                timeline["year"] = next_year
                
                # Determine companion based on year
                if next_year <= 60:
                    timeline["current_companion"] = "Beleg Cúthalion"
                elif next_year <= 120:
                    timeline["current_companion"] = "Mablung of the Heavy Hand"
                elif next_year <= 180:
                    timeline["current_companion"] = "Huan"
                elif next_year <= 240:
                    timeline["current_companion"] = "Húrin Thalion"
                elif next_year <= 300:
                    timeline["current_companion"] = "Maedhros"
                elif next_year <= 360:
                    timeline["current_companion"] = "Azaghâl"
                elif next_year <= 420:
                    timeline["current_companion"] = "Tuor"
                elif next_year <= 480:
                    timeline["current_companion"] = "Eärendil"
                else:  # next_year <= 540
                    timeline["current_companion"] = "Elrond"
            else:
                # Move to Second Age
                timeline["age"] = "Second Age"
                timeline["year"] = 350
                timeline["current_companion"] = "Celebrimbor"
        
        # Second Age: years 1-3441
        elif age == "Second Age":
            if year < 3400:  # Not at the end of Second Age yet
                # Advance to next companion in Second Age
                if year <= 350:
                    timeline["year"] = 700
                    timeline["current_companion"] = "Tar-Aldarion"
                elif year <= 700:
                    timeline["year"] = 1050
                    timeline["current_companion"] = "Narvi"
                elif year <= 1050:
                    timeline["year"] = 1400
                    timeline["current_companion"] = "Galadriel"
                elif year <= 1400:
                    timeline["year"] = 1750
                    timeline["current_companion"] = "Círdan"
                elif year <= 1750:
                    timeline["year"] = 2100
                    timeline["current_companion"] = "Glorfindel"
                elif year <= 2100:
                    timeline["year"] = 2450
                    timeline["current_companion"] = "Elendil"
                elif year <= 2450:
                    timeline["year"] = 2800
                    timeline["current_companion"] = "Isildur"
                elif year <= 2800:
                    timeline["year"] = 3150
                    timeline["current_companion"] = "Anárion"
                elif year <= 3150:
                    timeline["year"] = 3400
                    timeline["current_companion"] = "Gil-galad"
            else:
                # Move to Third Age
                timeline["age"] = "Third Age"
                timeline["year"] = 300
                timeline["current_companion"] = "Eärnur"
        
        # Third Age: years 1-3021
        elif age == "Third Age":
            if year < 3000:  # Not at the end of Third Age yet
                # Advance to next companion in Third Age
                if year <= 300:
                    timeline["year"] = 600
                    timeline["current_companion"] = "Fram"
                elif year <= 600:
                    timeline["year"] = 900
                    timeline["current_companion"] = "Thorin I"
                elif year <= 900:
                    timeline["year"] = 1200
                    timeline["current_companion"] = "Arveleg I"
                elif year <= 1200:
                    timeline["year"] = 1500
                    timeline["current_companion"] = "Malbeth the Seer"
                elif year <= 1500:
                    timeline["year"] = 1800
                    timeline["current_companion"] = "Aragorn I"
                elif year <= 1800:
                    timeline["year"] = 2100
                    timeline["current_companion"] = "Gandalf"
                elif year <= 2100:
                    timeline["year"] = 2400
                    timeline["current_companion"] = "Thorin Oakenshield"
                elif year <= 2400:
                    timeline["year"] = 2700
                    timeline["current_companion"] = "Denethor I"
                elif year <= 2700:
                    timeline["year"] = 3000
                    timeline["current_companion"] = "Aragorn II/Strider"
            else:
                # End of timeline, reset to First Age
                timeline["age"] = "First Age"
                timeline["year"] = 1
                timeline["current_companion"] = "Finrod Felagund"
        
        # Save the updated timeline
        self._save_timeline(timeline)
        
        # Reload the current companion
        self.current_timeline = timeline
        self.current_companion = self._load_current_companion()
        
        return timeline
    
    def _save_timeline(self, timeline):
        """Save the updated timeline to the memory bank."""
        timeline_path = self.ages_path / "current_timeline.md"
        
        # Format the timeline as markdown
        content = f"""# Current Timeline State

## Active Timeline Position
- Age: {timeline.get('age', 'First Age')}
- Year: {timeline.get('year', 1)}
- Current Companion: {timeline.get('current_companion', 'Finrod Felagund')}
- Player Generation: {timeline.get('player_generation', 1)}

## Timeline Progression
- First Age: {self._calculate_age_progress(timeline, 'First Age')}/10 heroes completed
- Second Age: {self._calculate_age_progress(timeline, 'Second Age')}/10 heroes completed
- Third Age: {self._calculate_age_progress(timeline, 'Third Age')}/10 heroes completed
"""
        
        # Add the rest of the original content
        original_path = self.ages_path / "current_timeline.md"
        if original_path.exists():
            with open(original_path, 'r', encoding='utf-8') as f:
                original_content = f.read()
                
                # Extract the companions lists
                if "## Next Companions in Timeline" in original_content:
                    companions_section = original_content.split("## Next Companions in Timeline")[1]
                    content += f"\n## Next Companions in Timeline{companions_section}"
        
        # Write the updated timeline
        with open(timeline_path, 'w', encoding='utf-8') as f:
            f.write(content)
    
    def _calculate_age_progress(self, timeline, age):
        """Calculate how many heroes have been completed in a given age."""
        current_age = timeline.get('age', 'First Age')
        current_year = timeline.get('year', 1)
        
        if current_age == age:
            # For the current age, calculate based on the year
            if age == "First Age":
                # First Age has 10 companions at years 1, 60, 120, 180, 240, 300, 360, 420, 480, 540
                return min(10, max(0, (current_year - 1) // 60))
            elif age == "Second Age":
                # Second Age years are more spread out
                year_thresholds = [350, 700, 1050, 1400, 1750, 2100, 2450, 2800, 3150, 3400]
                for i, threshold in enumerate(year_thresholds):
                    if current_year <= threshold:
                        return i
                return 10
            elif age == "Third Age":
                # Third Age years are also spread out
                year_thresholds = [300, 600, 900, 1200, 1500, 1800, 2100, 2400, 2700, 3000]
                for i, threshold in enumerate(year_thresholds):
                    if current_year <= threshold:
                        return i
                return 10
        elif current_age == "First Age" and age == "Second Age":
            # Haven't reached Second Age yet
            return 0
        elif current_age == "First Age" and age == "Third Age":
            # Haven't reached Third Age yet
            return 0
        elif current_age == "Second Age" and age == "First Age":
            # Completed First Age
            return 10
        elif current_age == "Second Age" and age == "Third Age":
            # Haven't reached Third Age yet
            return 0
        elif current_age == "Third Age" and age == "First Age":
            # Completed First Age
            return 10
        elif current_age == "Third Age" and age == "Second Age":
            # Completed Second Age
            return 10
        
        return 0


# Example usage
if __name__ == "__main__":
    # Initialize the companion handler
    handler = CompanionHandler("../../memory-bank")
    
    # Generate dialogue
    context = {
        "location": "A dark cavern",
        "enemies_nearby": True,
        "player_health": 50,
        "discovered_item": "Ancient sword"
    }
    
    dialogue = handler.generate_companion_dialogue(context, "discovery", 30)
    print(dialogue)
    
    # Advance the timeline
    new_timeline = handler.advance_timeline()
    print(f"Advanced to: {new_timeline['age']} Year {new_timeline['year']} - {new_timeline['current_companion']}") 