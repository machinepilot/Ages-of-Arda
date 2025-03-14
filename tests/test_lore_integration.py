"""
Tests for the lore integration module.
"""

import os
import sys
import unittest
from unittest.mock import MagicMock, patch
from pathlib import Path

# Add the src directory to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from mcp.lore.lore_integration import LoreIntegration

class MockMCPServer:
    """Mock MCP server for testing."""
    
    def __init__(self):
        self.endpoints = {}
    
    def register_endpoint(self, endpoint_name, handler_func):
        """Register an endpoint with the server."""
        self.endpoints[endpoint_name] = handler_func
    
    def call_endpoint(self, endpoint_name, request_data):
        """Call an endpoint with request data."""
        if endpoint_name not in self.endpoints:
            return {"error": f"Endpoint {endpoint_name} not found"}
        
        return self.endpoints[endpoint_name](request_data)

class MockLLMClient:
    """Mock LLM client for testing."""
    
    def generate(self, prompt):
        """Generate a response to a prompt."""
        if "location" in prompt.lower():
            return "This is a generated location description."
        elif "companion" in prompt.lower():
            return "Gandalf: I sense a great darkness ahead."
        elif "quest" in prompt.lower():
            return '{"title": "The Lost Artifact", "description": "A quest to find a lost artifact."}'
        else:
            return "Generated text."

class TestLoreIntegration(unittest.TestCase):
    """Test the lore integration module."""
    
    def setUp(self):
        """Set up the test environment."""
        # Create a temporary memory bank path for testing
        self.memory_bank_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../memory-bank'))
        
        # Create a mock MCP server
        self.mcp_server = MockMCPServer()
        
        # Create a mock LLM client
        self.llm_client = MockLLMClient()
        
        # Initialize the lore integration
        self.integration = LoreIntegration(self.memory_bank_path, self.llm_client)
        self.integration.register_mcp_endpoints(self.mcp_server)
        
        # Override the current age for testing
        self.integration.current_age = "third_age"
    
    def test_get_current_age(self):
        """Test getting the current age."""
        response = self.mcp_server.call_endpoint("ages/lore/age/get", {})
        self.assertEqual(response["age"], "third_age")
    
    def test_set_current_age(self):
        """Test setting the current age."""
        # Test valid age
        response = self.mcp_server.call_endpoint("ages/lore/age/set", {"age": "first_age"})
        self.assertEqual(response["status"], "success")
        self.assertEqual(response["age"], "first_age")
        self.assertEqual(self.integration.current_age, "first_age")
        
        # Test invalid age
        response = self.mcp_server.call_endpoint("ages/lore/age/set", {"age": "invalid_age"})
        self.assertIn("error", response)
    
    def test_get_location_description(self):
        """Test getting a location description."""
        # Test with narrative generator
        response = self.mcp_server.call_endpoint("ages/narrative/location", {
            "location_name": "Minas Tirith",
            "age": "third_age"
        })
        
        self.assertIn("description", response)
        self.assertEqual(response["location"], "Minas Tirith")
        self.assertEqual(response["age"], "third_age")
    
    def test_get_companion_dialogue(self):
        """Test getting companion dialogue."""
        # Test with narrative generator
        response = self.mcp_server.call_endpoint("ages/narrative/companion", {
            "companion_name": "Gandalf",
            "age": "third_age",
            "topic": "darkness"
        })
        
        self.assertIn("dialogue", response)
        self.assertEqual(response["companion"], "Gandalf")
        self.assertEqual(response["age"], "third_age")
        self.assertEqual(response["topic"], "darkness")
    
    def test_generate_quest(self):
        """Test generating a quest."""
        # Test with narrative generator
        response = self.mcp_server.call_endpoint("ages/narrative/quest", {
            "quest_type": "retrieve",
            "location": "Mordor",
            "age": "third_age",
            "target": "Ring of Power"
        })
        
        self.assertIn("title", response)
        self.assertIn("description", response)
        self.assertEqual(response["quest_type"], "retrieve")
        self.assertEqual(response["location"], "Mordor")
        self.assertEqual(response["age"], "third_age")
        self.assertEqual(response["target"], "Ring of Power")
    
    def test_get_random_lore(self):
        """Test getting random lore."""
        response = self.mcp_server.call_endpoint("ages/lore/random", {
            "topic_type": "character",
            "age": "first_age"
        })
        
        self.assertIn("content", response)
        self.assertEqual(response["topic_type"], "character")
        self.assertEqual(response["age"], "first_age")
    
    def test_missing_parameters(self):
        """Test handling of missing parameters."""
        # Test missing location_name
        response = self.mcp_server.call_endpoint("ages/narrative/location", {
            "age": "third_age"
        })
        self.assertIn("error", response)
        
        # Test missing companion_name
        response = self.mcp_server.call_endpoint("ages/narrative/companion", {
            "age": "third_age"
        })
        self.assertIn("error", response)
        
        # Test missing quest_type
        response = self.mcp_server.call_endpoint("ages/narrative/quest", {
            "location": "Mordor",
            "age": "third_age"
        })
        self.assertIn("error", response)

if __name__ == "__main__":
    unittest.main() 