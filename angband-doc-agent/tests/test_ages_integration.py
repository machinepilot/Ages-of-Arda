"""
Test script for the Ages of Arda integration.

This script tests the functionality of the Ages of Arda integration,
including companion dialogue generation, timeline advancement, and
relationship tracking.
"""

import os
import sys
import json
import unittest
from pathlib import Path

# Add the src directory to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.mcp.companions.companion_handler import CompanionHandler
from src.mcp.server.ages_integration import AgesOfArdaIntegration

class MockMCPServer:
    """Mock MCP server for testing."""
    
    def __init__(self):
        self.endpoints = {}
    
    def register_endpoint(self, endpoint, handler):
        """Register an endpoint with the server."""
        self.endpoints[endpoint] = handler
    
    def call_endpoint(self, endpoint, request):
        """Call an endpoint with a request."""
        if endpoint not in self.endpoints:
            raise ValueError(f"Endpoint {endpoint} not registered")
        
        return self.endpoints[endpoint](request)


class TestAgesOfArdaIntegration(unittest.TestCase):
    """Test cases for the Ages of Arda integration."""
    
    def setUp(self):
        """Set up the test environment."""
        # Create a temporary memory bank directory
        self.memory_bank_path = Path("test_memory_bank")
        self.memory_bank_path.mkdir(exist_ok=True)
        
        # Create necessary subdirectories
        (self.memory_bank_path / "companions" / "first_age").mkdir(parents=True, exist_ok=True)
        (self.memory_bank_path / "companions" / "second_age").mkdir(parents=True, exist_ok=True)
        (self.memory_bank_path / "companions" / "third_age").mkdir(parents=True, exist_ok=True)
        (self.memory_bank_path / "ages").mkdir(parents=True, exist_ok=True)
        (self.memory_bank_path / "player").mkdir(parents=True, exist_ok=True)
        
        # Create a sample companion profile
        self._create_sample_companion_profile()
        
        # Create a sample timeline file
        self._create_sample_timeline()
        
        # Initialize the integration
        self.integration = AgesOfArdaIntegration(str(self.memory_bank_path))
        
        # Initialize the mock MCP server
        self.mcp_server = MockMCPServer()
        self.integration.register_mcp_endpoints(self.mcp_server)
    
    def tearDown(self):
        """Clean up after the test."""
        # Remove the temporary memory bank directory
        import shutil
        shutil.rmtree(self.memory_bank_path)
    
    def _create_sample_companion_profile(self):
        """Create a sample companion profile for testing."""
        finrod_profile = """# Finrod Felagund

## Basic Information
**Full Name**: Finrod Felagund
**Race**: Noldorin Elf
**Birth**: Years of the Trees
**Title**: King of Nargothrond, Friend of Men
**Family**: Son of Finarfin and Eärwen, brother to Galadriel
**Fate**: Died defending Beren in the dungeons of Tol-in-Gaurhoth

## Personality
Finrod is wise, noble, and compassionate. He possesses a deep curiosity about other races and cultures, especially Men. He is known for his generosity and willingness to sacrifice for those he considers friends. His oath to Barahir and his descendants demonstrates his unwavering loyalty and honor.

## Speech Pattern
Finrod speaks with formal eloquence befitting his noble upbringing, yet maintains a warm and approachable tone. He often includes poetic musings and references to the history and lore of the Eldar. When deeply moved, he may slip into phrases of Quenya, the ancient tongue of his people. His speech carries the weight of one who has seen the light of Valinor.

## Dialogue Examples

### First Meeting
"Well met, traveler. I am Finrod Felagund, Lord of Nargothrond. These are perilous times to wander alone through these lands. What quest brings you to these shadows?"

### Discovering Artifact
"This bears the mark of elder days... perhaps even of Valinor itself. Such craftsmanship is rare in these diminished times. Handle it with reverence, for it carries memories of a world now lost to us."

### Combat Preparation
"Steel yourself, my friend. The servants of the Enemy approach. Remember that darkness cannot endure the light of courage. Stand firm, and I shall stand with you."

### Growing Trust
"Few mortals have earned the trust I place in you. You remind me of Bëor, first of Men I encountered long ago. There is the same fire in your eyes—a determination that defies the shadow."

### Final Sacrifice
"The oath I swore binds me still. Go forward and complete what we began—I will hold them here. Fear not for me; death is not the end for the Children of Ilúvatar. Perhaps we shall meet again, beyond the circles of the world."
"""
        
        # Write the profile to a file
        with open(self.memory_bank_path / "companions" / "first_age" / "finrod.md", "w", encoding="utf-8") as f:
            f.write(finrod_profile)
    
    def _create_sample_timeline(self):
        """Create a sample timeline file for testing."""
        timeline_content = """# Current Timeline State

## Active Timeline Position
- Age: First Age
- Year: 1
- Current Companion: Finrod Felagund
- Player Generation: 1

## Timeline Progression
- First Age: 0/10 heroes completed
- Second Age: 0/10 heroes completed
- Third Age: 0/10 heroes completed

## Next Companions in Timeline

### First Age Companions
1. Finrod Felagund (Year 1)
2. Beleg Cúthalion (Year 60)
3. Mablung of the Heavy Hand (Year 120)
4. Huan (Year 180)
5. Húrin Thalion (Year 240)
6. Maedhros (Year 300)
7. Azaghâl (Year 360)
8. Tuor (Year 420)
9. Eärendil (Year 480)
10. Elrond (Year 540)

### Second Age Companions
1. Celebrimbor (Year 350)
2. Tar-Aldarion (Year 700)
3. Narvi (Year 1050)
4. Galadriel (Year 1400)
5. Círdan (Year 1750)
6. Glorfindel (Year 2100)
7. Elendil (Year 2450)
8. Isildur (Year 2800)
9. Anárion (Year 3150)
10. Gil-galad (Year 3400)

### Third Age Companions
1. Eärnur (Year 300)
2. Fram (Year 600)
3. Thorin I (Year 900)
4. Arveleg I (Year 1200)
5. Malbeth the Seer (Year 1500)
6. Aragorn I (Year 1800)
7. Gandalf (Year 2100)
8. Thorin Oakenshield (Year 2400)
9. Denethor I (Year 2700)
10. Aragorn II/Strider (Year 3000)
"""
        
        # Write the timeline to a file
        with open(self.memory_bank_path / "ages" / "current_timeline.md", "w", encoding="utf-8") as f:
            f.write(timeline_content)
    
    def test_get_current_companion(self):
        """Test getting the current companion."""
        companion_name = self.integration.get_current_companion_name()
        self.assertEqual(companion_name, "Finrod Felagund")
    
    def test_get_current_age_and_year(self):
        """Test getting the current age and year."""
        age_and_year = self.integration.get_current_age_and_year()
        self.assertEqual(age_and_year["age"], "First Age")
        self.assertEqual(age_and_year["year"], 1)
    
    def test_relationship_level(self):
        """Test relationship level tracking."""
        # Initial relationship level should be 0
        initial_level = self.integration.get_relationship_level()
        self.assertEqual(initial_level, 0)
        
        # Update relationship level
        new_level = self.integration.update_relationship_level(10)
        self.assertEqual(new_level, 10)
        
        # Check that the relationship level was saved
        saved_level = self.integration.get_relationship_level()
        self.assertEqual(saved_level, 10)
        
        # Test clamping to 0-100
        self.integration.update_relationship_level(100)
        self.assertEqual(self.integration.get_relationship_level(), 100)
        
        self.integration.update_relationship_level(-200)
        self.assertEqual(self.integration.get_relationship_level(), 0)
    
    def test_generate_dialogue(self):
        """Test dialogue generation."""
        context = {
            "location": "A dark cavern",
            "enemies_nearby": True,
            "player_health": 50,
            "discovered_item": "Ancient sword"
        }
        
        # Test dialogue generation for different prompt types
        dialogue_discovery = self.integration.generate_dialogue(context, "discovery")
        self.assertIsInstance(dialogue_discovery, str)
        self.assertTrue(len(dialogue_discovery) > 0)
        
        dialogue_combat = self.integration.generate_dialogue(context, "combat")
        self.assertIsInstance(dialogue_combat, str)
        self.assertTrue(len(dialogue_combat) > 0)
        
        dialogue_greeting = self.integration.generate_dialogue(context, "greeting")
        self.assertIsInstance(dialogue_greeting, str)
        self.assertTrue(len(dialogue_greeting) > 0)
    
    def test_handle_player_death(self):
        """Test handling player death."""
        # Update relationship level before death
        self.integration.update_relationship_level(20)
        self.assertEqual(self.integration.get_relationship_level(), 20)
        
        # Handle player death
        new_timeline = self.integration.handle_player_death()
        
        # Check that the timeline advanced
        self.assertEqual(new_timeline["age"], "First Age")
        self.assertEqual(new_timeline["year"], 60)
        self.assertEqual(new_timeline["companion"], "Beleg Cúthalion")
        self.assertEqual(new_timeline["player_generation"], 2)
        
        # Check that the relationship level was reset
        self.assertEqual(self.integration.get_relationship_level(), 0)
        
        # Check that the old relationship was archived
        self.assertIn("generation_1", self.integration.relationship_levels)
        self.assertEqual(self.integration.relationship_levels["generation_1"]["Finrod Felagund"], 20)
    
    def test_mcp_endpoints(self):
        """Test MCP endpoints."""
        # Test dialogue endpoint
        dialogue_request = {
            "context": {
                "location": "A dark cavern",
                "enemies_nearby": True,
                "player_health": 50,
                "discovered_item": "Ancient sword"
            },
            "prompt_type": "discovery"
        }
        
        dialogue_response = self.mcp_server.call_endpoint("ages/companion/dialogue", dialogue_request)
        self.assertIn("dialogue", dialogue_response)
        self.assertIn("companion", dialogue_response)
        self.assertIn("relationship_level", dialogue_response)
        
        # Test companion info endpoint
        info_request = {
            "companion_name": "Finrod Felagund"
        }
        
        info_response = self.mcp_server.call_endpoint("ages/companion/info", info_request)
        self.assertIn("companion", info_response)
        self.assertIn("relationship_level", info_response)
        self.assertEqual(info_response["companion"]["name"], "Finrod Felagund")
        
        # Test timeline info endpoint
        timeline_response = self.mcp_server.call_endpoint("ages/timeline/info", {})
        self.assertIn("age", timeline_response)
        self.assertIn("year", timeline_response)
        self.assertIn("companion", timeline_response)
        self.assertIn("player_generation", timeline_response)
        
        # Test relationship update endpoint
        relationship_request = {
            "change": 15
        }
        
        relationship_response = self.mcp_server.call_endpoint("ages/relationship/update", relationship_request)
        self.assertIn("companion", relationship_response)
        self.assertIn("relationship_level", relationship_response)
        self.assertEqual(relationship_response["relationship_level"], 15)
        
        # Test player death endpoint
        death_response = self.mcp_server.call_endpoint("ages/player/death", {})
        self.assertIn("age", death_response)
        self.assertIn("year", death_response)
        self.assertIn("companion", death_response)
        self.assertIn("player_generation", death_response)
        self.assertEqual(death_response["year"], 60)
        self.assertEqual(death_response["companion"], "Beleg Cúthalion")


if __name__ == "__main__":
    unittest.main() 