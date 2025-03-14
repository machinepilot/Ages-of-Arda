# borg-cave.h Documentation

## File Overview

`borg-cave.h` is a header file in the Angband codebase that defines data structures and functions related to the Borg AI's representation of the game dungeon. The Borg AI is an automated player that navigates the dungeon and makes decisions based on its internal model of the game state.

This file defines the `borg_grid` struct, which represents a single grid (tile) in the dungeon, as well as global variables and functions for initializing and freeing the Borg's dungeon model.

## Data Structures

### `borg_grid`

The `borg_grid` struct represents a single grid (tile) in the Borg's model of the game dungeon. It contains the following fields:

- `feat` (uint8_t): The terrain feature type of the grid. This may be incorrect and is based on the standard "feature" values, with some values never used or used in non-standard ways.
- `info` (uint16_t): Grid flags that store additional information about the grid.
- `trap` (bool): Indicates if the grid contains a trap.
- `glyph` (bool): Indicates if the grid contains a glyph.
- `web` (bool): Indicates if the grid contains a web.
- `store` (uint8_t): Unknown purpose (not documented).
- `take` (uint8_t): An object index into the "object tracking" array.
- `kill` (uint8_t): A monster index into the "monster tracking" array.
- `xtra` (uint8_t): An extra field that tracks how much "searching" has been done in the grid or in any adjacent grid.

## Global Variables

- `borg_grids` (borg_grid**): A 2D array of pointers to `borg_grid` structs representing the current dungeon map. The dimensions are `AUTO_MAX_Y` (maximum dungeon height) by `AUTO_MAX_X` (maximum dungeon width).

## Functions

### `borg_init_cave`

```c
void borg_init_cave(void);
```

- **Purpose**: Initializes the Borg's dungeon model by allocating memory for the `borg_grids` array.
- **Parameters**: None
- **Return Value**: None
- **Side Effects**: Allocates memory for the `borg_grids` array.
- **Relationships**: Should be called before using the Borg AI.
- **Game Mechanics**: Initializes the data structures needed for the Borg AI to model and navigate the dungeon.

### `borg_free_cave`

```c
void borg_free_cave(void);
```

- **Purpose**: Frees the memory allocated for the Borg's dungeon model.
- **Parameters**: None
- **Return Value**: None
- **Side Effects**: Frees the memory allocated for the `borg_grids` array.
- **Relationships**: Should be called when the Borg AI is no longer needed or the game is exiting.
- **Game Mechanics**: Cleans up the data structures used by the Borg AI to model the dungeon.

## Algorithms

There are no complex algorithms implemented directly in this header file. However, the data structures defined here are used by the Borg AI to implement pathfinding, dungeon navigation, and decision-making algorithms.

## Dependencies

- This file depends on `angband.h` being included before `ALLOW_BORG` is defined.
- Other files in the `borg` directory likely depend on this file for the `borg_grid` struct and related functions.

## Historical Context

The Borg AI was developed as an automated player for Angband, originally created by Ben Harrison. The code in this file has been maintained and updated by several contributors over the years, including James E. Wilson, Robert A. Koeneke, Andi Sidwell, Chris Carr, Ed Graham, and Erik Osheim.

The copyright notice at the top of the file indicates that this code is free software, available under either the GNU General Public License or the "Angband License", which allows copying and distribution for educational, research, and not-for-profit purposes.