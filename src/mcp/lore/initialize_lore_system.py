#!/usr/bin/env python3
"""
Initialize Lore System

This script initializes the lore management system and connects it to the MCP server.
It serves as an entry point for integrating the lore system with the Ages of Arda Angband variant.
"""

import os
import sys
import logging
import argparse
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Add parent directory to path to import modules
sys.path.append(os.path.abspath(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))

# Import lore integration
from mcp.lore.lore_integration import initialize_lore_integration

# Import LLM client
try:
    from mcp.llm.llm_client import LLMClient
except ImportError:
    logger.warning("LLM client module not found, defaulting to template-based generation")
    LLMClient = None

def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Initialize the lore management system")
    parser.add_argument(
        "--memory-bank-path",
        default="../memory-bank",
        help="Path to the memory bank directory"
    )
    parser.add_argument(
        "--mcp-server-url",
        default="http://localhost:3000",
        help="URL of the MCP server"
    )
    parser.add_argument(
        "--model-name",
        default="llama2:13b",
        help="Name of the LLM model to use"
    )
    parser.add_argument(
        "--without-llm",
        action="store_true",
        help="Disable LLM-based generation (use templates only)"
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug logging"
    )
    
    return parser.parse_args()

def connect_to_mcp_server(server_url):
    """
    Connect to the MCP server.
    
    Args:
        server_url: URL of the MCP server
        
    Returns:
        MCP server client or None if connection failed
    """
    try:
        # Import the MCP client module
        sys.path.append(os.path.abspath(os.path.dirname(os.path.dirname(__file__))))
        from mcp.client import MCPClient
        
        # Connect to the server
        client = MCPClient(server_url)
        logger.info(f"Connected to MCP server at {server_url}")
        return client
    except ImportError:
        logger.error("Failed to import MCP client module")
        return None
    except Exception as e:
        logger.error(f"Failed to connect to MCP server: {e}")
        return None

def initialize_llm_client(model_name):
    """
    Initialize the LLM client.
    
    Args:
        model_name: Name of the LLM model to use
        
    Returns:
        LLM client or None if initialization failed
    """
    if LLMClient is None:
        logger.warning("LLM client module not available")
        return None
    
    try:
        # Initialize the LLM client
        llm_client = LLMClient(model_name)
        logger.info(f"Initialized LLM client with model {model_name}")
        return llm_client
    except Exception as e:
        logger.error(f"Failed to initialize LLM client: {e}")
        return None

def main():
    """Main entry point."""
    # Parse command line arguments
    args = parse_arguments()
    
    # Configure logging level
    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Resolve memory bank path
    memory_bank_path = os.path.abspath(args.memory_bank_path)
    if not os.path.exists(memory_bank_path):
        logger.error(f"Memory bank path '{memory_bank_path}' does not exist")
        sys.exit(1)
    
    logger.info(f"Using memory bank at: {memory_bank_path}")
    
    # Connect to MCP server
    mcp_server = connect_to_mcp_server(args.mcp_server_url)
    if mcp_server is None:
        logger.error("Failed to connect to MCP server, exiting")
        sys.exit(1)
    
    # Initialize LLM client if enabled
    llm_client = None
    if not args.without_llm:
        llm_client = initialize_llm_client(args.model_name)
        if llm_client is None:
            logger.warning("LLM client initialization failed, falling back to template-based generation")
    else:
        logger.info("LLM-based generation disabled, using templates only")
    
    # Initialize and register lore integration
    try:
        lore_integration = initialize_lore_integration(memory_bank_path, mcp_server, llm_client)
        logger.info("Lore integration initialized and registered with MCP server")
        
        # Keep the script running to maintain the MCP server connection
        logger.info("Lore system initialized and running")
        logger.info("Press Ctrl+C to exit")
        
        # Simple event loop to keep the script running
        try:
            while True:
                pass
        except KeyboardInterrupt:
            logger.info("Shutting down lore system")
    except Exception as e:
        logger.error(f"Failed to initialize lore integration: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 