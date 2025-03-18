---
title: Lore Management System for Ages of Arda
id: lore-management-system-for-ages-of-arda
section: gameplay
category: reference
created: '2025-03-14'
updated: '2025-03-14'
version: 0.1.0
---

# Lore Management System for Ages of Arda

This directory contains the Lore Management System for the Ages of Arda Angband variant, which provides a unified API for accessing and using lore data from the memory bank.

## Overview

The Lore Management System integrates with the MCP (Model Context Protocol) server to provide lore-driven gameplay generation capabilities:

- Retrieve and cache lore data from the memory bank
- Generate narrative descriptions for locations based on lore
- Create companion dialogue that reflects their knowledge of the world
- Generate quests and events that are consistent with the age and location
- Provide a unified API for other game systems to access lore data

## Components

The system consists of the following main components:

- **Lore Manager (C)**: Core lore retrieval and caching functionality in C
- **Narrative Generator (Python)**: Generates narrative content using the lore data and LLMs
- **Lore Integration (Python)**: Ties everything together and provides the MCP endpoints

## Directory Structure

```
src/mcp/lore/
├── lore_manager.h           # C API for lore retrieval
├── lore_manager.c           # Implementation of the C API
├── lore_integration.py      # Python integration with MCP
├── narrative_generator.py   # Narrative generation using lore
├── initialize_lore_system.py # Utility to initialize the system
└── README.md                # This file
```

## MCP Endpoints

The system registers the following endpoints with the MCP server:

### Lore Endpoints

- `ages/lore/character` - Get lore for a character
- `ages/lore/location` - Get lore for a location
- `ages/lore/artifact` - Get lore for an artifact
- `ages/lore/random` - Get random lore
- `ages/lore/companion` - Get lore for a companion

### Narrative Endpoints

- `ages/narrative/location` - Generate a narrative description for a location
- `ages/narrative/companion` - Generate dialogue for a companion
- `ages/narrative/quest` - Generate a quest description

### Age Management

- `ages/lore/age/set` - Set the current age
- `ages/lore/age/get` - Get the current age

## Usage

### Initializing the System

To initialize the lore system and connect it to the MCP server:

```bash
python src/mcp/lore/initialize_lore_system.py --memory-bank-path /path/to/memory-bank --mcp-server-url http://localhost:3000
```

### Command Line Options

- `--memory-bank-path`: Path to the memory bank directory (default: "../memory-bank")
- `--mcp-server-url`: URL of the MCP server (default: "http://localhost:3000")
- `--model-name`: Name of the LLM model to use (default: "llama2:13b")
- `--without-llm`: Disable LLM-based generation (use templates only)
- `--debug`: Enable debug logging

### Using the MCP Endpoints

#### Get Character Lore

```json
// Request
{
  "character_name": "Gandalf",
  "age": "third_age"
}

// Response
{
  "content": "Gandalf, also known as Mithrandir, was an Istar (Wizard) sent to Middle-earth in the Third Age to combat the threat of Sauron...",
  "source": "The Lord of the Rings",
  "age": "third_age",
  "year": 3018,
  "is_canonical": true
}
```

#### Generate Location Description

```json
// Request
{
  "location_name": "Minas Tirith",
  "age": "third_age",
  "context": {
    "time_of_day": "dawn",
    "weather": "clear"
  }
}

// Response
{
  "description": "The white towers of Minas Tirith gleamed in the early dawn light, rising tier upon tier like a mountain crowned with pearl...",
  "location": "Minas Tirith",
  "age": "third_age"
}
```

#### Generate Companion Dialogue

```json
// Request
{
  "companion_name": "Aragorn",
  "age": "third_age",
  "topic": "Gondor",
  "relationship_level": 3,
  "context": {
    "location": "Rivendell",
    "quest_progress": 0.5
  }
}

// Response
{
  "dialogue": "Aragorn: Gondor has no king. Gondor needs no king. Yet... I begin to feel the weight of my ancestry calling to me.",
  "companion": "Aragorn",
  "age": "third_age",
  "topic": "Gondor"
}
```

#### Generate Quest

```json
// Request
{
  "quest_type": "retrieve",
  "location": "Moria",
  "age": "third_age",
  "target": "Mithril armor"
}

// Response
{
  "title": "The Lost Mithril",
  "description": "Deep in the darkness of Moria, a legendary set of mithril armor was left behind during the hasty retreat of Balin's folk...",
  "quest_type": "retrieve",
  "location": "Moria",
  "age": "third_age",
  "target": "Mithril armor"
}
```

## Integration with Game Systems

### Companion System

The companion system can use the lore API to:
- Load companion profiles based on the current age
- Generate dialogue that reflects the companion's knowledge and personality
- Create relationships between companions based on lore
- Provide lore-appropriate reactions to game events

### World Generation

The world generation system can use the lore API to:
- Create age-appropriate environments, enemies, and items
- Ensure consistency with the lore of the current age
- Generate dynamic descriptions for locations
- Place artifacts and characters according to lore

### Quest and Event System

The quest and event system can use the lore API to:
- Generate quests that are consistent with the current age
- Create events that reflect the history and conflicts of the age
- Ensure quest rewards and difficulty are appropriate for the age
- Provide rich narrative context for quests and events

## Performance Considerations

- The lore manager includes a caching system to reduce memory bank access
- The narrative generator can fall back to template-based generation when LLM is not available
- Asynchronous processing can be used for non-blocking gameplay
- The system includes error handling and fallbacks for graceful degradation

## Future Enhancements

- Extend the system to support additional ages (Second Age, Fourth Age)
- Implement a lore codex UI for players to explore the lore
- Add support for player-discovered lore that persists across playthroughs
- Create a dynamic event system that uses lore to generate age-appropriate events 