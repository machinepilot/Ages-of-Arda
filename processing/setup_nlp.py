#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Set up NLP environment for Tolkien ePub processing.

This script downloads the necessary spaCy models and sets up
Tolkien-specific entity types for entity extraction.
"""

import os
import sys
import logging
import subprocess
from datetime import datetime
import spacy
from pathlib import Path

# Initialize logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f"processing/logs/setup_nlp_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("setup_nlp")

def ensure_directories():
    """Create necessary directories if they don't exist."""
    directories = [
        "processing/logs",
        "processing/schemas/entity_lists",
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        logger.info(f"Ensured directory exists: {directory}")

def download_spacy_model():
    """Download and set up the spaCy model."""
    model_name = "en_core_web_lg"
    
    try:
        # Try to load the model to check if it's already installed
        spacy.load(model_name)
        logger.info(f"SpaCy model {model_name} is already installed")
    except OSError:
        # Model is not installed, download it
        logger.info(f"Downloading spaCy model: {model_name}")
        subprocess.check_call([sys.executable, "-m", "spacy", "download", model_name])
        logger.info(f"Successfully downloaded spaCy model: {model_name}")

def create_entity_list_files():
    """Create entity list files for Tolkien-specific entities."""
    entity_lists = {
        "character_list.txt": [
            "Bilbo Baggins", "Frodo Baggins", "Gandalf", "Aragorn", "Legolas", 
            "Gimli", "Samwise Gamgee", "Galadriel", "Elrond", "Boromir", 
            "Meriadoc Brandybuck", "Peregrin Took", "Gollum", "Sméagol",
            "Saruman", "Sauron", "Théoden", "Éowyn", "Éomer", "Faramir",
            "Denethor", "Treebeard", "Tom Bombadil", "Goldberry", "Arwen",
            "Thorin Oakenshield", "Smaug", "Bard", "Beorn", "Radagast",
            "Elendil", "Isildur", "Gil-galad", "Celeborn", "Fëanor",
            "Túrin Turambar", "Beren", "Lúthien", "Eärendil", "Elwing",
            "Morgoth", "Glorfindel", "Círdan", "Haldir", "Gwaihir"
        ],
        "location_list.txt": [
            "Hobbiton", "The Shire", "Rivendell", "Mordor", "Mount Doom", 
            "Gondor", "Minas Tirith", "Rohan", "Edoras", "Isengard", 
            "Moria", "Lothlórien", "Fangorn", "Helm's Deep", "Ithilien", 
            "Osgiliath", "Minas Morgul", "Barad-dûr", "Erebor", "Dale", 
            "Laketown", "Mirkwood", "Grey Havens", "Weathertop", "Bree",
            "Anduin", "Bruinen", "Misty Mountains", "Dead Marshes", "Brandywine River",
            "Khazad-dûm", "Caradhras", "Cair Andros", "Pelennor Fields", "Cirith Ungol",
            "Nargothrond", "Gondolin", "Angband", "Thangorodrim", "Doriath",
            "Valinor", "Númenor", "Beleriand", "Arnor", "Eregion"
        ],
        "item_list.txt": [
            "The One Ring", "Andúril", "Sting", "Glamdring", "Narsil", 
            "Galadriel's Phial", "Elven Cloaks", "Mithril Coat", "Palantír", "Arkenstone", 
            "Dragon-helm of Dor-lómin", "Aeglos", "Ringil", "Grond", "Silmarils",
            "Angrist", "Gurthang", "Belthronding", "Dramborleg", "Aranrúth"
        ],
        "event_list.txt": [
            "War of the Ring", "The Last Alliance", "Fall of Gondolin", "Nirnaeth Arnoediad",
            "Battle of Five Armies", "Fall of Númenor", "War of Wrath", "Dagor Dagorath",
            "Kinslaying at Alqualondë", "Council of Elrond", "Destruction of the Ring",
            "Coronation of King Elessar", "Battle of the Pelennor Fields", "Fall of Barad-dûr"
        ],
        "race_list.txt": [
            "Hobbit", "Elf", "Dwarf", "Man", "Orc", "Troll", "Ent", "Eagle", 
            "Balrog", "Valar", "Maiar", "Nazgûl", "Uruk-hai", "Warg", "Dragon",
            "Easterling", "Haradrim", "Dunlending", "Beorning", "Drúedain"
        ],
        "language_list.txt": [
            "Westron", "Sindarin", "Quenya", "Khuzdul", "Black Speech", 
            "Rohirric", "Adûnaic", "Entish", "Valarin", "Telerin"
        ]
    }
    
    # Create entity list files
    entity_lists_dir = Path("processing/schemas/entity_lists")
    
    for filename, entities in entity_lists.items():
        file_path = entity_lists_dir / filename
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(entities))
        
        logger.info(f"Created entity list file: {file_path} with {len(entities)} entities")

def setup_tolkien_nlp():
    """Set up the full NLP environment for Tolkien processing."""
    logger.info("Starting NLP setup for Tolkien ePub processing")
    
    # Ensure directories exist
    ensure_directories()
    
    # Download spaCy model
    download_spacy_model()
    
    # Create entity list files
    create_entity_list_files()
    
    # Create custom entity dictionaries
    logger.info("NLP setup complete")
    
    # Define Tolkien-specific entity types
    custom_entities = [
        "TOLKIEN_CHARACTER", 
        "TOLKIEN_LOCATION", 
        "TOLKIEN_ITEM", 
        "TOLKIEN_EVENT",
        "TOLKIEN_RACE",
        "TOLKIEN_LANGUAGE"
    ]
    
    logger.info(f"Configured custom entity types: {', '.join(custom_entities)}")
    
    return True

if __name__ == "__main__":
    setup_successful = setup_tolkien_nlp()
    
    if setup_successful:
        logger.info("NLP environment setup completed successfully")
        sys.exit(0)
    else:
        logger.error("NLP environment setup failed")
        sys.exit(1) 