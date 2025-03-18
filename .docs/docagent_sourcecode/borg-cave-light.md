# File: borg-cave-light.h

## File Overview

`borg-cave-light.h` is a header file that is part of the Borg AI system in the Angband roguelike game. The Borg is an AI player that can autonomously navigate the dungeon and make gameplay decisions. This specific file deals with managing and updating the set of grids that are considered "liteable" by the Borg AI.

The file defines constants, data structures, and function prototypes related to maintaining and updating the list of grids that the Borg AI considers as potential targets for lighting up using light sources like torches or spells.

## Data Structures

The file does not define any structs or typedefs.

## Global Variables

1. `borg_light_n` (int16_t): 
   - Represents the current number of grids in the `borg_light` arrays.
   - Used to keep track of the size of the lite array.

2. `borg_light_y` (uint8_t[AUTO_LIGHT_MAX]):
   - An array that stores the y-coordinates of the grids considered liteable by the Borg AI.
   - The size of the array is determined by the `AUTO_LIGHT_MAX` constant.

3. `borg_light_x` (uint8_t[AUTO_LIGHT_MAX]):
   - An array that stores the x-coordinates of the grids considered liteable by the Borg AI.
   - The size of the array is determined by the `AUTO_LIGHT_MAX` constant.

4. `borg_glow_n` (int16_t):
   - Represents the current number of grids in the `borg_glow` arrays.
   - Used to keep track of the size of the glow array.

5. `borg_glow_y` (uint8_t[AUTO_LIGHT_MAX]):
   - An array that stores the y-coordinates of the grids considered glowable by the Borg AI.
   - The size of the array is determined by the `AUTO_LIGHT_MAX` constant.

6. `borg_glow_x` (uint8_t[AUTO_LIGHT_MAX]):
   - An array that stores the x-coordinates of the grids considered glowable by the Borg AI.
   - The size of the array is determined by the `AUTO_LIGHT_MAX` constant.

## Functions

1. `borg_update_light(void)`:
   - Purpose: Updates the list of grids considered liteable and glowable by the Borg AI.
   - Parameters: None
   - Return value: None
   - Side effects: Modifies the `borg_light` and `borg_glow` arrays and their corresponding size variables.
   - Relationships: This function is likely called periodically by the Borg AI to refresh its knowledge of liteable and glowable grids based on the current state of the dungeon.

## Algorithms

The specific algorithms used to determine which grids are considered liteable or glowable are not detailed in this header file. The implementation of these algorithms would be found in the corresponding source file or other related files.

## Dependencies

This header file depends on the `angband.h` header file, which is included before the `ALLOW_BORG` preprocessor directive. The `angband.h` file likely contains fundamental types, constants, and other definitions used throughout the Angband codebase.

Other files in the Borg AI system, particularly those dealing with dungeon navigation and decision-making, likely depend on the data structures and functions declared in this header file.

## Historical Context

The code includes copyright notices dating back to 1997, indicating that this file has been part of the Angband codebase for a significant period. The Borg AI system has likely evolved over time, with contributions from various developers as mentioned in the copyright header.

## Game Mechanics

The liteable and glowable grids maintained by this code are used by the Borg AI to make decisions related to using light sources effectively in the dungeon. This could involve:

1. Deciding when to light torches or cast light spells to illuminate dark areas.
2. Prioritizing exploration of liteable grids to discover new parts of the dungeon.
3. Identifying potential locations of interest based on the distribution of liteable grids.
4. Optimizing the use of limited light resources by focusing on key liteable areas.

The specific mechanics of how the Borg AI uses this information would be implemented in other parts of the AI system, but the data structures and functions provided by `borg-cave-light.h` form the foundation for these light-based decisions.