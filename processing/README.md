# Tolkien ePub Processing Framework

This framework provides tools for processing J.R.R. Tolkien's works from ePub format into structured data for the Ages of Arda Memory Bank system.

## Overview

The framework extracts content from ePub files, identifies entities (characters, locations, etc.), and integrates them into the Ages of Arda Memory Bank system with proper categorization by age and entity type.

## Directory Structure

- `processing/`: Main processing directory
  - `temp/`: Temporary extraction files
  - `logs/`: Processing logs
  - `epub_content/`: Extracted content from ePub files
  - `schemas/`: JSON schemas for entity validation
  - `json_output/`: Extracted entities
  - `consolidated/`: Consolidated entities
  - `checkpoints/`: Processing checkpoints for resuming interrupted work

## Processing Pipeline

1. **ePub Parsing**: Extract content from ePub files
2. **Entity Extraction**: Identify entities (characters, locations, etc.) using Ollama
3. **Entity Consolidation**: Merge entities across chapters and books
4. **Memory Bank Integration**: Add entities to the Memory Bank structure

## Requirements

- Python 3.7+
- Ollama server running locally (for entity extraction)

Install dependencies:
```
pip install -r processing/requirements.txt
```

## Usage

### 1. Process ePub Files

```bash
python processing/main.py --epub-dir "raw_inputs/New Files"
```

This will:
- Extract content from all ePub files in the specified directory
- Save extracted content to `processing/epub_content/`

### 2. Extract Entities

```bash
python processing/entity_extractor.py --input-dir "processing/epub_content" --output-dir "processing/json_output"
```

This will:
- Process text content using Ollama
- Extract entities (characters, locations, items, events)
- Save extracted entities to JSON files

### 3. Consolidate Entities

```bash
python processing/entity_consolidator.py --input-dir "processing/json_output" --output-dir "processing/consolidated"
```

This will:
- Load all extracted entities
- Merge duplicates and resolve aliases
- Create consolidated entity records

### 4. Integrate with Memory Bank

```bash
python processing/memory_bank_integrator.py --input-dir "processing/consolidated" --memory-bank-dir ".memory-bank"
```

This will:
- Format entities for Memory Bank storage
- Create appropriate directory structure in Memory Bank
- Save entities to Memory Bank with proper categorization

## All-in-One Processing

To run the entire pipeline at once:

```bash
python processing/main.py --epub-dir "raw_inputs/New Files" --clean
python processing/entity_extractor.py
python processing/entity_consolidator.py
python processing/memory_bank_integrator.py
```

## Notes

- The framework includes checkpointing to resume processing if interrupted
- Processing logs are stored in `processing/logs/` for debugging
- Schemas in `processing/schemas/` define the required structure for entities

## Entity Types

The framework extracts the following types of entities:

- **Characters**: People, beings, creatures
- **Locations**: Places, regions, landmarks
- **Items**: Objects, artifacts, weapons
- **Events**: Battles, councils, journeys

## Age Categorization

Entities are categorized into the following ages:

- **First Age**: Early history (Silmarillion)
- **Second Age**: Middle history
- **Third Age**: Late history (The Hobbit, Lord of the Rings)
- **Fourth Age**: Post-Ring history

## License

This project is part of Ages of Arda, developed for educational and research purposes. 