---
title: 'File: src/borg/borg-attack-munchkin.h'
id: file-srcborgborgattackmunchkinh
section: development
category: guides
created: '2025-03-14'
updated: '2025-03-14'
version: 0.1.0
---


# File: src/borg/borg-attack-munchkin.h

## File Overview
The `borg-attack-munchkin.h` file is a header file in the Angband roguelike game, specifically within the "borg" AI player module. It declares functions related to the AI's "munchkin" attack strategies, which are presumably aggressive or exploitative approaches to combat.

The file is guarded by an `ALLOW_BORG` conditional compilation directive, indicating that it is only compiled when the borg AI module is enabled.

## Data Structures
This file does not define any structs or typedefs.

## Global Variables
This file does not declare any global variables.

## Functions

### `borg_munchkin_mage`
```c
extern bool borg_munchkin_mage(void);
```
- **Purpose**: Presumably implements the borg AI's munchkin attack strategy for mage-type characters.
- **Parameters**: None
- **Return value**: A boolean value, likely indicating the success or failure of the munchkin mage attack strategy.
- **Side effects**: Unknown, as the implementation is not provided in this header file.
- **Relationships**: May call other borg AI functions or interact with game state.
- **Game mechanics**: Specific munchkin attack strategies for mage characters are not described in this file.

### `borg_munchkin_melee`
```c
extern bool borg_munchkin_melee(void);
```
- **Purpose**: Presumably implements the borg AI's munchkin attack strategy for melee-type characters.
- **Parameters**: None
- **Return value**: A boolean value, likely indicating the success or failure of the munchkin melee attack strategy.
- **Side effects**: Unknown, as the implementation is not provided in this header file.
- **Relationships**: May call other borg AI functions or interact with game state.
- **Game mechanics**: Specific munchkin attack strategies for melee characters are not described in this file.

## Algorithms
This file does not implement any algorithms directly, as it is a header file. The actual implementations of the munchkin attack strategies would be found in corresponding .c files.

## Dependencies
- This file includes "../angband.h" before the `ALLOW_BORG` check to avoid empty compilation units.
- Other files may depend on this header to access the munchkin attack functions for the borg AI.

## Historical Context
The file includes a copyright notice indicating contributions from several individuals between 1997 and 2009, suggesting a long development history.

The term "munchkin" in gaming often refers to a player who aggressively exploits the game's mechanics to gain an advantage, sometimes in ways not intended by the game designers. The presence of explicit "munchkin attack" functions in the borg AI may indicate an attempt to model or simulate such aggressive playstyles.

Note: Without access to the actual implementation (.c) files, it is difficult to provide more detailed documentation on the specific game mechanics and algorithms involved in these munchkin attack strategies. The information provided is based on inferences from the limited content in the header file.