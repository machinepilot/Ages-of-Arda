"""
Lore Integration Module for Ages of Arda

This module integrates the lore data extracted from Tolkien's works with the
Ages of Arda companion system. It provides functions for accessing lore data
and incorporating it into companion dialogue and knowledge.
"""

import os
import json
import random
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class LoreManager:
    """
    Manager for accessing and integrating lore data with the Ages of Arda companion system.
    """
    
    def __init__(self, lore_dir=None):
        """
        Initialize the lore manager.
        
        Args:
            lore_dir (str, optional): Path to the lore directory. If None, uses default path.
        """
        self.lore_dir = Path(lore_dir) if lore_dir else Path(__file__).parent
        self.index_path = self.lore_dir / "lore_index.json"
        self.lore_index = self._load_lore_index()
        self.book_metadata = {}
        self.character_lore = {}
        
        # Load book metadata
        self._load_book_metadata()
    
    def _load_lore_index(self):
        """
        Load the lore index file.
        
        Returns:
            dict: Lore index data
        """
        if not self.index_path.exists():
            logger.warning(f"Lore index file not found at {self.index_path}")
            return {"books": {}}
        
        try:
            with open(self.index_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading lore index: {e}")
            return {"books": {}}
    
    def _load_book_metadata(self):
        """
        Load metadata for all books in the lore index.
        """
        for book_id, book_info in self.lore_index.get("books", {}).items():
            metadata_path = self.lore_dir / book_info["path"]
            
            if not metadata_path.exists():
                logger.warning(f"Book metadata file not found at {metadata_path}")
                continue
            
            try:
                with open(metadata_path, 'r', encoding='utf-8') as f:
                    self.book_metadata[book_id] = json.load(f)
            except Exception as e:
                logger.error(f"Error loading book metadata for {book_id}: {e}")
    
    def get_books_for_age(self, age):
        """
        Get books for a specific age.
        
        Args:
            age (str): Age to get books for (e.g., "first_age", "second_age", "third_age")
            
        Returns:
            list: List of book IDs for the specified age
        """
        return [
            book_id for book_id, book_info in self.lore_index.get("books", {}).items()
            if book_info["age"] == age
        ]
    
    def get_character_lore(self, character_name, age=None):
        """
        Get lore for a specific character.
        
        Args:
            character_name (str): Name of the character
            age (str, optional): Age to limit the search to
            
        Returns:
            dict: Character lore data
        """
        character_lore = {}
        
        # Normalize character name for comparison
        character_name_lower = character_name.lower()
        
        # Search for character in all books (or books for a specific age)
        for book_id, metadata in self.book_metadata.items():
            # Skip if age doesn't match
            if age and metadata["age"] != age:
                continue
            
            # Check if character appears in this book
            entities = metadata.get("entities", {})
            characters = entities.get("characters", {})
            
            # Look for character (case-insensitive)
            for char_name, appearances in characters.items():
                if character_name_lower in char_name.lower():
                    # Load character file if it exists
                    char_file = self.lore_dir / metadata["age"] / f"{book_id}_{char_name.lower()}.md"
                    
                    if char_file.exists():
                        try:
                            with open(char_file, 'r', encoding='utf-8') as f:
                                character_lore[f"{char_name} ({metadata['title']})"] = f.read()
                        except Exception as e:
                            logger.error(f"Error loading character file {char_file}: {e}")
                    
                    # Add appearances
                    if not character_lore.get(f"{char_name} ({metadata['title']})"):
                        character_lore[f"{char_name} ({metadata['title']})"] = {
                            "appearances": appearances
                        }
        
        return character_lore
    
    def get_location_lore(self, location_name, age=None):
        """
        Get lore for a specific location.
        
        Args:
            location_name (str): Name of the location
            age (str, optional): Age to limit the search to
            
        Returns:
            dict: Location lore data
        """
        location_lore = {}
        
        # Normalize location name for comparison
        location_name_lower = location_name.lower()
        
        # Search for location in all books (or books for a specific age)
        for book_id, metadata in self.book_metadata.items():
            # Skip if age doesn't match
            if age and metadata["age"] != age:
                continue
            
            # Check if location appears in this book
            entities = metadata.get("entities", {})
            locations = entities.get("locations", {})
            
            # Look for location (case-insensitive)
            for loc_name, appearances in locations.items():
                if location_name_lower in loc_name.lower():
                    location_lore[f"{loc_name} ({metadata['title']})"] = {
                        "appearances": appearances
                    }
                    
                    # Get a sample of text from chapters where the location appears
                    for chapter in appearances[:2]:  # Limit to first 2 chapters
                        chapter_file = self._find_chapter_file(metadata["age"], book_id, chapter)
                        
                        if chapter_file and chapter_file.exists():
                            try:
                                with open(chapter_file, 'r', encoding='utf-8') as f:
                                    content = f.read()
                                    
                                    # Find paragraphs containing the location name
                                    paragraphs = content.split("\n\n")
                                    loc_paragraphs = [p for p in paragraphs if loc_name in p][:1]  # Limit to 1 paragraph
                                    
                                    if loc_paragraphs:
                                        if "excerpts" not in location_lore[f"{loc_name} ({metadata['title']})"]:
                                            location_lore[f"{loc_name} ({metadata['title']})"]["excerpts"] = {}
                                        
                                        location_lore[f"{loc_name} ({metadata['title']})"]["excerpts"][chapter] = loc_paragraphs[0]
                            except Exception as e:
                                logger.error(f"Error loading chapter file {chapter_file}: {e}")
        
        return location_lore
    
    def get_artifact_lore(self, artifact_name, age=None):
        """
        Get lore for a specific artifact.
        
        Args:
            artifact_name (str): Name of the artifact
            age (str, optional): Age to limit the search to
            
        Returns:
            dict: Artifact lore data
        """
        artifact_lore = {}
        
        # Normalize artifact name for comparison
        artifact_name_lower = artifact_name.lower()
        
        # Search for artifact in all books (or books for a specific age)
        for book_id, metadata in self.book_metadata.items():
            # Skip if age doesn't match
            if age and metadata["age"] != age:
                continue
            
            # Check if artifact appears in this book
            entities = metadata.get("entities", {})
            artifacts = entities.get("artifacts", {})
            
            # Look for artifact (case-insensitive)
            for art_name, appearances in artifacts.items():
                if artifact_name_lower in art_name.lower():
                    artifact_lore[f"{art_name} ({metadata['title']})"] = {
                        "appearances": appearances
                    }
                    
                    # Get a sample of text from chapters where the artifact appears
                    for chapter in appearances[:2]:  # Limit to first 2 chapters
                        chapter_file = self._find_chapter_file(metadata["age"], book_id, chapter)
                        
                        if chapter_file and chapter_file.exists():
                            try:
                                with open(chapter_file, 'r', encoding='utf-8') as f:
                                    content = f.read()
                                    
                                    # Find paragraphs containing the artifact name
                                    paragraphs = content.split("\n\n")
                                    art_paragraphs = [p for p in paragraphs if art_name in p][:1]  # Limit to 1 paragraph
                                    
                                    if art_paragraphs:
                                        if "excerpts" not in artifact_lore[f"{art_name} ({metadata['title']})"]:
                                            artifact_lore[f"{art_name} ({metadata['title']})"]["excerpts"] = {}
                                        
                                        artifact_lore[f"{art_name} ({metadata['title']})"]["excerpts"][chapter] = art_paragraphs[0]
                            except Exception as e:
                                logger.error(f"Error loading chapter file {chapter_file}: {e}")
        
        return artifact_lore
    
    def _find_chapter_file(self, age, book_id, chapter_title):
        """
        Find the file for a specific chapter.
        
        Args:
            age (str): Age of the book
            book_id (str): Book ID
            chapter_title (str): Chapter title
            
        Returns:
            Path: Path to the chapter file, or None if not found
        """
        # Create a safe filename
        import re
        safe_title = re.sub(r'[^\w\s-]', '', chapter_title).strip().lower()
        safe_title = re.sub(r'[-\s]+', '_', safe_title)
        
        # Check if file exists
        chapter_file = self.lore_dir / age / f"{book_id}_chapters" / f"{safe_title}.md"
        
        if chapter_file.exists():
            return chapter_file
        
        # If not found, try to find a file with a similar name
        chapter_dir = self.lore_dir / age / f"{book_id}_chapters"
        
        if not chapter_dir.exists():
            return None
        
        for file_path in chapter_dir.glob("*.md"):
            if safe_title in file_path.stem:
                return file_path
        
        return None
    
    def get_random_lore_for_companion(self, companion_name, age, topic=None):
        """
        Get random lore for a companion to use in dialogue.
        
        Args:
            companion_name (str): Name of the companion
            age (str): Age of the companion
            topic (str, optional): Topic to get lore for (character, location, artifact)
            
        Returns:
            dict: Random lore data
        """
        # If topic is specified, get lore for that topic
        if topic:
            if topic.lower() == "character":
                # Get random character lore
                characters = []
                
                for book_id, metadata in self.book_metadata.items():
                    if metadata["age"] == age:
                        entities = metadata.get("entities", {})
                        characters.extend(entities.get("characters", {}).keys())
                
                if characters:
                    character = random.choice(characters)
                    return {
                        "type": "character",
                        "name": character,
                        "lore": self.get_character_lore(character, age)
                    }
            
            elif topic.lower() == "location":
                # Get random location lore
                locations = []
                
                for book_id, metadata in self.book_metadata.items():
                    if metadata["age"] == age:
                        entities = metadata.get("entities", {})
                        locations.extend(entities.get("locations", {}).keys())
                
                if locations:
                    location = random.choice(locations)
                    return {
                        "type": "location",
                        "name": location,
                        "lore": self.get_location_lore(location, age)
                    }
            
            elif topic.lower() == "artifact":
                # Get random artifact lore
                artifacts = []
                
                for book_id, metadata in self.book_metadata.items():
                    if metadata["age"] == age:
                        entities = metadata.get("entities", {})
                        artifacts.extend(entities.get("artifacts", {}).keys())
                
                if artifacts:
                    artifact = random.choice(artifacts)
                    return {
                        "type": "artifact",
                        "name": artifact,
                        "lore": self.get_artifact_lore(artifact, age)
                    }
        
        # If no topic specified or no lore found for the topic, get random lore
        topics = ["character", "location", "artifact"]
        random.shuffle(topics)
        
        for topic in topics:
            lore = self.get_random_lore_for_companion(companion_name, age, topic)
            if lore:
                return lore
        
        return None
    
    def enhance_companion_dialogue(self, companion_name, age, dialogue, context):
        """
        Enhance companion dialogue with lore references.
        
        Args:
            companion_name (str): Name of the companion
            age (str): Age of the companion
            dialogue (str): Original dialogue
            context (dict): Context information
            
        Returns:
            str: Enhanced dialogue
        """
        # Check if dialogue already contains lore references
        if "according to the lore" in dialogue.lower() or "as it is written" in dialogue.lower():
            return dialogue
        
        # Determine if we should add lore (random chance)
        if random.random() > 0.3:  # 30% chance to add lore
            return dialogue
        
        # Get random lore based on context
        lore_topic = None
        
        # Check if context contains relevant information
        if context.get("discovered_item"):
            lore_topic = "artifact"
        elif context.get("location"):
            lore_topic = "location"
        
        # Get random lore
        lore_data = self.get_random_lore_for_companion(companion_name, age, lore_topic)
        
        if not lore_data:
            return dialogue
        
        # Create lore reference
        lore_reference = ""
        
        if lore_data["type"] == "character":
            character_name = lore_data["name"]
            character_lore = lore_data["lore"]
            
            if character_lore:
                for source, info in character_lore.items():
                    if isinstance(info, str):
                        # Extract a quote from the markdown content
                        import re
                        quotes = re.findall(r'> (.*?)\n', info)
                        
                        if quotes:
                            lore_reference = f" As it is written of {character_name}, \"{quotes[0]}\""
                            break
                    elif isinstance(info, dict) and "appearances" in info:
                        lore_reference = f" The tales speak of {character_name} in the lore of old."
                        break
        
        elif lore_data["type"] == "location":
            location_name = lore_data["name"]
            location_lore = lore_data["lore"]
            
            if location_lore:
                for source, info in location_lore.items():
                    if isinstance(info, dict) and "excerpts" in info:
                        for chapter, excerpt in info["excerpts"].items():
                            # Extract a sentence containing the location name
                            import re
                            sentences = re.split(r'(?<=[.!?])\s+', excerpt)
                            loc_sentences = [s for s in sentences if location_name in s]
                            
                            if loc_sentences:
                                lore_reference = f" According to the lore, {loc_sentences[0]}"
                                break
                        
                        if lore_reference:
                            break
                    
                    if not lore_reference:
                        lore_reference = f" The ancient texts speak of {location_name}."
        
        elif lore_data["type"] == "artifact":
            artifact_name = lore_data["name"]
            artifact_lore = lore_data["lore"]
            
            if artifact_lore:
                for source, info in artifact_lore.items():
                    if isinstance(info, dict) and "excerpts" in info:
                        for chapter, excerpt in info["excerpts"].items():
                            # Extract a sentence containing the artifact name
                            import re
                            sentences = re.split(r'(?<=[.!?])\s+', excerpt)
                            art_sentences = [s for s in sentences if artifact_name in s]
                            
                            if art_sentences:
                                lore_reference = f" The lore tells us of {artifact_name}: \"{art_sentences[0]}\""
                                break
                        
                        if lore_reference:
                            break
                    
                    if not lore_reference:
                        lore_reference = f" The {artifact_name} is spoken of in ancient texts."
        
        # Add lore reference to dialogue
        if lore_reference:
            # Find a suitable place to insert the lore reference
            sentences = re.split(r'(?<=[.!?])\s+', dialogue)
            
            if len(sentences) > 1:
                # Insert after a random sentence (but not the last one)
                insert_index = random.randint(0, len(sentences) - 2)
                sentences.insert(insert_index + 1, lore_reference)
                return " ".join(sentences)
            else:
                # Just append to the dialogue
                return dialogue + lore_reference
        
        return dialogue


# Example usage
if __name__ == "__main__":
    lore_manager = LoreManager()
    
    # Get books for First Age
    first_age_books = lore_manager.get_books_for_age("first_age")
    print(f"First Age books: {first_age_books}")
    
    # Get lore for Finrod
    finrod_lore = lore_manager.get_character_lore("Finrod", "first_age")
    print(f"Finrod lore: {finrod_lore.keys()}")
    
    # Get random lore for a companion
    random_lore = lore_manager.get_random_lore_for_companion("Finrod Felagund", "first_age")
    print(f"Random lore: {random_lore}")
    
    # Enhance dialogue
    dialogue = "The shadows grow deeper as we venture further. Be on your guard."
    context = {"location": "dungeon", "depth": 10}
    enhanced_dialogue = lore_manager.enhance_companion_dialogue("Finrod Felagund", "first_age", dialogue, context)
    print(f"Enhanced dialogue: {enhanced_dialogue}") 