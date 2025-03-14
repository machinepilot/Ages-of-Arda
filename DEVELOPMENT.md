# Ages of Arda Development Guide

This document provides essential information for developers working on the Ages of Arda Angband variant, with a particular focus on the lore management system integration.

## Development Environment Setup

### Prerequisites
- C Compiler (GCC 10+ or Clang 12+)
- Python 3.8+
- Ollama for local LLM integration
- CMake 3.15+
- Git

### Getting Started

1. Clone the repository:
```
git clone https://github.com/your-username/ages-of-arda.git
cd ages-of-arda
```

2. Install Python dependencies:
```
pip install -r requirements.txt
```

3. Build the game:
```
mkdir build
cd build
cmake ..
make
```

4. Set up Ollama (for AI-driven features):
```
# Install Ollama from https://ollama.ai
ollama pull llama2:13b
ollama pull codellama:13b
ollama pull mistral:7b
```

## Project Structure

### Key Directories
- `src/`: Core game source code
  - `src/mcp/`: Model Context Protocol implementation
  - `src/mcp/lore/`: Lore management and narrative generation
- `memory-bank/`: Structured memory for AI systems
  - `memory-bank/lore/`: Lore database organized by age
- `tests/`: Test suite
- `docs/`: Documentation

## Lore Management System

The lore management system is a critical component that provides AI agents with accurate Tolkien lore to ensure consistent narrative generation.

### File Organization

All lore content is organized in the `memory-bank/lore` directory with the following structure:
```
memory-bank/lore/
├── first_age/
│   ├── characters/
│   ├── locations/
│   ├── artifacts/
│   └── events/
├── second_age/
└── third_age/
```

### Lore File Format

Lore entries are stored as JSON files with the following format:

```json
{
  "name": "Entity Name",
  "description": "Short description",
  "content": "Detailed lore content",
  "source": "Source book or material",
  "year": 1234,
  "is_canonical": true,
  "type": "character|location|artifact|event",
  "additional_fields": "as needed for specific entity types"
}
```

### API Usage

#### C Code Integration

```c
// Initialize the lore manager
lore_manager_t *manager = init_lore_manager("path/to/memory-bank");

// Get character lore
lore_data_t *character_lore = get_character_lore(manager, "Aragorn", "third_age");
if (character_lore) {
    printf("Lore: %s\n", character_lore->content);
    free_lore_data(character_lore);
}

// Clean up
free_lore_manager(manager);
```

#### Python Integration

```python
from src.mcp.lore.lore_integration import LoreIntegration

# Initialize the lore integration
lore = LoreIntegration(memory_bank_path="path/to/memory-bank")

# Get location lore
location_info = lore.get_location_lore("Minas Tirith", age="third_age")
print(f"Description: {location_info['content']}")

# Generate narrative
description = lore.generate_location_description("Minas Tirith", "third_age")
print(description)
```

## AI-Driven Gameplay Features

### Narrative Generation

The narrative generator creates dynamic, lore-accurate descriptions and dialogue:

```python
from src.mcp.lore.narrative_generator import NarrativeGenerator

generator = NarrativeGenerator(lore_integration=lore)

# Generate location description
description = generator.describe_location("Moria", age="third_age", context={
    "time_of_day": "night",
    "player_race": "dwarf",
    "previous_events": ["encountered_balrog", "lost_companion"]
})
```

### MCP Integration

The lore management system is integrated with the MCP server to provide AI agents with accurate context:

```c
// Register lore-related tools with the MCP server
mcp_server_t *server = init_mcp_server("AgesOfArda", 8000);
register_lore_tools(server, lore_manager);
```

## Testing

### Running Tests

```
cd build
ctest
```

### Lore Accuracy Testing

To test lore accuracy:

```
python tests/test_lore_accuracy.py
```

## Documentation

### Generating Documentation

```
cd docs
doxygen Doxyfile
```

## Contribution Guidelines

### Lore Contributions

When adding new lore entries:

1. Ensure all content is sourced from Tolkien's works when possible
2. Clearly mark non-canonical extensions
3. Format JSON files according to the specification
4. Add a test case for each new lore entry
5. Update relevant documentation

### Code Style

- Follow the C style guidelines in `.cursor/rules/c-style.mdc`
- Use 4 spaces for indentation
- Keep line length under 120 characters
- Document all functions with appropriate comments

### Review Process

All changes require:
1. Code review from at least one maintainer
2. Passing all automated tests
3. For lore additions, verification against canonical sources

## Troubleshooting

### Common Issues

#### MCP Server Connection Issues
- Ensure Ollama is running
- Check port configuration (default: 11434)
- Verify network permissions

#### Lore Retrieval Failures
- Check file paths and JSON formatting
- Verify memory bank directory structure
- Enable debug logging for detailed error messages

## Resources

- [Tolkien Gateway](http://tolkiengateway.net/) - Reference for lore verification
- [LLM Documentation](https://github.com/ollama/ollama/blob/main/docs/modelfile.md) - For model configuration 