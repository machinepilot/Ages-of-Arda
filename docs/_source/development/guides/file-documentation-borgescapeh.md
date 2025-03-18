---
title: 'File Documentation: borg-escape.h'
id: file-documentation-borgescapeh
section: development
category: guides
created: '2025-03-14'
updated: '2025-03-14'
version: 0.1.0
---


# File Documentation: borg-escape.h

## File Overview
`borg-escape.h` is a header file in the Angband source code that provides declarations for functions related to the Borg's escape and teleportation mechanics. The Borg is an AI player that can automatically play the game, making decisions based on various game states and heuristics.

This file contains functions for evaluating the safety of the Borg's current location, determining when to use teleportation or phasing abilities, and attempting to escape from dangerous situations. It plays a crucial role in the Borg's decision-making process when it comes to survival and navigation within the dungeon.

## Data Structures
This header file does not contain any structs or typedefs.

## Global Variables
This header file does not contain any global variables.

## Functions

### `borg_recall()`
```c
extern bool borg_recall(void);
```
- **Purpose**: Attempts to induce the WORD_OF_RECALL effect, which teleports the player back to the dungeon's surface.
- **Parameters**: None
- **Return value**: Returns true if the recall attempt was successful, false otherwise.
- **Side effects**: If successful, the player will be teleported to the dungeon's surface.
- **Relationships**: This function is likely related to the game's teleportation mechanics and may interact with other functions that handle the WORD_OF_RECALL effect.
- **Game mechanics**: In Angband, WORD_OF_RECALL is a means for the player to escape the dungeon and return to the surface. This function allows the Borg to utilize this mechanic when it deems necessary.

### `borg_freedom()`
```c
extern int borg_freedom(int y, int x);
```
- **Purpose**: Evaluates the "freedom" of the given location (y, x) within the dungeon.
- **Parameters**:
  - `y`: The y-coordinate of the location to evaluate.
  - `x`: The x-coordinate of the location to evaluate.
- **Return value**: Returns an integer value representing the degree of freedom at the given location. Higher values likely indicate more freedom of movement.
- **Side effects**: None
- **Relationships**: This function is likely used by other Borg functions to assess the safety and maneuverability of different dungeon locations.
- **Game mechanics**: The concept of "freedom" in this context relates to the Borg's ability to move and navigate at a given location without being trapped or surrounded by obstacles or enemies.

### `borg_caution_teleport()`
```c
extern bool borg_caution_teleport(int emergency, int turns);
```
- **Purpose**: Helps determine if using the "Teleport" ability seems like a good idea given the current situation.
- **Parameters**:
  - `emergency`: An integer value representing the urgency of the situation. Higher values may indicate a greater need for teleportation.
  - `turns`: The number of game turns to consider when evaluating the need for teleportation.
- **Return value**: Returns true if teleportation is recommended, false otherwise.
- **Side effects**: None
- **Relationships**: This function likely uses other Borg functions to assess the current game state and determine if teleportation is necessary.
- **Game mechanics**: Teleportation is a means for the player to instantly move to a random location on the current dungeon level. This function helps the Borg decide when to use this ability based on the perceived danger and urgency of the situation.

### `borg_caution_phase()`
```c
extern bool borg_caution_phase(int emergency, int turns);
```
- **Purpose**: Helps determine if using the "Phase Door" ability seems like a good idea given the current situation.
- **Parameters**:
  - `emergency`: An integer value representing the urgency of the situation. Higher values may indicate a greater need for phasing.
  - `turns`: The number of game turns to consider when evaluating the need for phasing.
- **Return value**: Returns true if phasing is recommended, false otherwise.
- **Side effects**: None
- **Relationships**: This function likely uses other Borg functions to assess the current game state and determine if phasing is necessary.
- **Game mechanics**: Phase Door is an ability that allows the player to pass through solid walls and obstacles. This function helps the Borg decide when to use this ability based on the perceived danger and urgency of the situation.

### `borg_shadow_shift()`, `borg_dimension_door()`, `borg_allow_teleport()`
```c
extern bool borg_shadow_shift(int allow_fail);
extern bool borg_dimension_door(int allow_fail);
extern bool borg_allow_teleport(void);
```
- **Purpose**: These functions are related to special teleportation abilities available to the player.
  - `borg_shadow_shift()`: Likely handles the "Shadow Shifting" ability, which teleports the player to a nearby location.
  - `borg_dimension_door()`: Likely handles the "Dimension Door" ability, which teleports the player to a specific location.
  - `borg_allow_teleport()`: Determines if teleportation is allowed in the current situation.
- **Parameters**:
  - `allow_fail`: An integer value indicating whether the ability should be attempted even if it may fail. Non-zero values likely allow for failure.
- **Return value**: Returns true if the ability was successfully used or is allowed, false otherwise.
- **Side effects**: If successful, the player will be teleported according to the specific ability.
- **Relationships**: These functions are related to the Borg's decision-making process for using special teleportation abilities.
- **Game mechanics**: Shadow Shifting, Dimension Door, and other teleportation abilities provide the player with additional movement options. These functions help the Borg determine when and how to use these abilities effectively.

### `borg_surrounded()`
```c
extern bool borg_surrounded(void);
```
- **Purpose**: Evaluates the likelihood of the Borg being surrounded by enemies or obstacles.
- **Parameters**: None
- **Return value**: Returns true if the Borg is likely to be surrounded, false otherwise.
- **Side effects**: None
- **Relationships**: This function is probably used by other Borg functions to assess the current situation and make decisions accordingly.
- **Game mechanics**: Being surrounded can be a dangerous situation in Angband, as it limits the player's movement and escape options. This function allows the Borg to recognize when it is surrounded and take appropriate actions.

### `borg_escape()`
```c
extern bool borg_escape(int b_q);
```
- **Purpose**: Attempts to make the Borg escape from a dangerous situation.
- **Parameters**:
  - `b_q`: An integer value representing the level of danger or the escape strategy to use.
- **Return value**: Returns true if the escape attempt was successful, false otherwise.
- **Side effects**: If successful, the Borg may use various abilities or strategies to escape, such as teleportation or phasing.
- **Relationships**: This function likely uses other Borg functions to assess the situation and determine the best escape strategy.
- **Game mechanics**: Escaping from dangerous situations is crucial for survival in Angband. This function encapsulates the Borg's escape mechanics and decision-making process.

## Algorithms
This header file does not contain any complex algorithms. The actual implementations of the escape and teleportation mechanics are likely found in the corresponding source files.

## Dependencies
- This header file depends on the `angband.h` header file, which is included before the `ALLOW_BORG` preprocessor directive.
- Other source files that implement the Borg's AI and decision-making processes likely depend on this header file.

## Historical Context
The code in this header file contains copyright notices dating back to 1997, indicating that it has been part of the Angband codebase for a considerable time. The original authors listed are Ben Harrison, James E. Wilson, and Robert A. Koeneke, with additional contributions from Andi Sidwell, Chris Carr, Ed Graham, and Erik Osheim in 2007-2009.

The Borg AI player is a unique feature of Angband that has been developed and refined over the years to provide an automated gameplay experience. The escape and teleportation mechanics implemented in this file are essential for the Borg's ability to navigate the dungeon and survive dangerous encounters.