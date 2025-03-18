---
title: Documentation for src/borg/borg-fight-defend.h
id: documentation-for-srcborgborgfightdefendh
section: development
category: guides
created: '2025-03-14'
updated: '2025-03-14'
version: 0.1.0
---


# Documentation for src/borg/borg-fight-defend.h

## File Overview

`borg-fight-defend.h` is a header file in the Angband roguelike game's "borg" module, which is an AI player that can play the game autonomously. This file specifically deals with the borg's defensive combat behaviors and decisions.

The header includes two key components:
1. Declaration of the global variable `borg_attempting_refresh_resist`
2. Prototype for the function `borg_defend()`

These components are guarded by the `ALLOW_BORG` preprocessor directive to allow exclusion of borg-related code during compilation if desired.

## Data Structures

This header file does not define any structs or typedefs.

## Global Variables

- `borg_attempting_refresh_resist`: A boolean variable indicating whether the borg is currently attempting to refresh its resistances. This likely ties into the borg's decision-making process for using resistance-granting items or abilities.

## Functions

### `borg_defend()`

```c
bool borg_defend(int p1);
```

- **Purpose**: This function likely encapsulates the borg's defensive combat decision-making process. It would be called during the borg's turn to determine what defensive action, if any, the borg should take.

- **Parameters**:
  - `int p1`: The meaning of this parameter is not clear from the context provided. It likely provides some additional context for the borg's decision, such as the severity of the threat or the type of defensive action to consider.

- **Return Value**: The function returns a boolean value. A `true` value likely indicates that the borg has decided to take a defensive action, while a `false` value suggests the borg will not take a defensive action.

- **Side Effects**: Without the function definition, it's difficult to say for certain, but this function likely modifies the game state in some way if the borg decides to take a defensive action. This could involve using items, casting spells, or changing the borg's position in the dungeon.

- **Relationships to Other Functions**: This function is probably called from the main borg AI routine that determines the borg's actions for each turn. It may also call other borg-related functions to gather information about the current situation or to execute the chosen defensive action.

- **Game Mechanics Implemented**: The specifics would be in the function definition, but in general, this function would handle things like:
  - Assessing the current threat level based on visible monsters and their capabilities
  - Checking the borg's current resistances and deciding if they need to be refreshed
  - Choosing between different defensive options like quaffing potions, reading scrolls, casting spells, or retreating to a safer position
  - Executing the chosen defensive action

## Algorithms

Without the function definition, we cannot discuss the specific algorithms implemented. However, the defensive decision-making process likely involves some form of threat assessment and cost-benefit analysis to choose the optimal defensive action for the current situation.

## Dependencies

This header file directly includes the main `angband.h` header, which suggests it depends on definitions and declarations from that file.

Other files in the `borg` module likely include this header to access the `borg_defend()` function and the `borg_attempting_refresh_resist` variable.

## Historical Context

The copyright notice at the top of the file attributes the code to several individuals and spans a range from 1997 to 2009. This suggests that the borg module, and possibly this specific file, has a long history with contributions from multiple developers over more than a decade of Angband's development.

The licensing options provided (GPL2 or the "Angband License") reflect the open-source nature of the Angband project and the desire to allow free use and modification of the code for non-commercial purposes.