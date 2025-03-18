Original Location: C:\working_directory\ages-project\clean-ages-of-arda\angband-doc-agent\README.md
# Ages of Arda - Angband Variant

## Overview

Ages of Arda is an Angband variant that integrates AI-driven companions through the Model Context Protocol (MCP). The game spans the Three Ages of Arda (First, Second, and Third Age) from Tolkien's legendarium, with each age featuring unique companions who guide the player through their journey.

This project implements a companion system where players interact with notable characters from Tolkien's world. As players progress through the game and inevitably die, they are reborn in a new era with a new companion, creating a sense of continuity and progression across multiple playthroughs.

## Key Features

- **Timeline-Based Progression**: The game spans the Three Ages of Arda, with each age featuring 10 unique companions.
- **AI-Driven Companions**: Companions provide contextual dialogue, guidance, and lore based on the current game state.
- **Relationship System**: Build relationships with companions through gameplay actions, unlocking deeper dialogue and assistance.
- **Persistent Memory**: The game remembers your previous incarnations and relationships, creating a sense of continuity.
- **MCP Integration**: Utilizes the Model Context Protocol to enable AI-driven gameplay elements.
- **Lore Management**: Rich lore database from Tolkien's works with intelligent retrieval and generation.

## Project Structure

```
angband-doc-agent/
├── memory-bank/               # Memory storage for companions and timeline
│   ├── ages/                  # Timeline information
│   ├── companions/            # Companion profiles
│   │   ├── first_age/         # First Age companions
│   │   ├── second_age/        # Second Age companions
│   │   └── third_age/         # Third Age companions
│   ├── lore/                  # Lore database from Tolkien's works
│   │   ├── first_age/         # First Age lore
│   │   ├── second_age/        # Second Age lore
│   │   └── third_age/         # Third Age lore
│   └── player/                # Player relationship data
├── src/                       # Source code
│   ├── game_integration/      # C code for Angband integration
│   └── mcp/                   # MCP server implementation
│       ├── companions/        # Companion dialogue generation
│       ├── lore/              # Lore management system
│       │   ├── narrative_generator.py  # Narrative generation using lore
│       │   └── lore_integration.py     # MCP integration for lore
│       └── server/            # MCP server endpoints
└── tests/                     # Test scripts
```

## Companions

The game features 30 companions across the Three Ages of Arda:

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

## MCP Integration

The Ages of Arda variant integrates with the Model Context Protocol (MCP) to enable AI-driven gameplay elements. The MCP server provides the following endpoints:

### Companion System
- `ages/companion/dialogue`: Generate dialogue for the current companion
- `ages/companion/info`: Get information about a companion
- `ages/relationship/update`: Update the relationship level with a companion

### Lore System
- `ages/lore/character`: Get lore about a character
- `ages/lore/location`: Get lore about a location
- `ages/lore/artifact`: Get lore about an artifact
- `ages/lore/random`: Get random lore content
- `ages/lore/age/set`: Set the current age
- `ages/lore/age/get`: Get the current age

### Narrative Generation
- `ages/narrative/location`: Generate narrative descriptions for locations
- `ages/narrative/companion`: Generate companion dialogue based on lore
- `ages/narrative/quest`: Generate quests informed by lore

### Timeline Management
- `ages/timeline/info`: Get information about the current timeline
- `ages/player/death`: Handle player death and advance the timeline

## Game Integration

The Ages of Arda variant integrates with the Angband game through a C module that handles game events and communicates with the MCP server. The integration module provides the following features:

- Initialization and cleanup of the Ages of Arda integration
- Dialogue generation based on game context
- Relationship level tracking
- Timeline advancement on player death
- Event handling for game events (entering levels, finding artifacts, killing monsters, etc.)
- Lore retrieval and generation for game world elements

## Development

### Prerequisites

- Python 3.8 or higher
- Angband source code
- MCP server implementation

### Setup

1. Clone the repository
2. Install dependencies: `pip install -r requirements.txt`
3. Start the MCP server: `python src/mcp/server/main.py`
4. Build Angband with the Ages of Arda integration

### Testing

Run the test suite to verify the functionality of the Ages of Arda integration:

```
python -m unittest discover tests
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgements

- The Angband development team
- J.R.R. Tolkien for creating the rich world of Middle-earth
- The MCP project for enabling AI-driven gameplay 