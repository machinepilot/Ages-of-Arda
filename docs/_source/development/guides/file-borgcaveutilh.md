---
title: 'File: borg-cave-util.h'
id: file-borgcaveutilh
section: development
category: guides
created: '2025-03-14'
updated: '2025-03-14'
version: 0.1.0
---


# File: borg-cave-util.h

## File Overview

`borg-cave-util.h` is a header file in the Angband roguelike game's "borg" module, which provides utility functions for interacting with the cave (dungeon) data structure. The file defines several functions that check properties of grid locations within the cave, such as whether a grid is a floor tile or protected from needing a glyph. It also provides functions to get the dimensions of the game's display panel.

## Data Structures

This header file does not define any structs or typedefs directly. However, it uses the `borg_grid` type, which is likely defined in the `borg-cave.h` header file included at the top.

## Global Variables

This file does not define any global variables.

## Functions

### `borg_cave_floor_bold`
```c
extern bool borg_cave_floor_bold(int y, int x);
```
- **Purpose**: Determine if a grid location in the cave is a floor grid and only a floor grid.
- **Parameters**:
  - `y`: The y-coordinate of the grid location.
  - `x`: The x-coordinate of the grid location.
- **Return value**: Returns `true` if the specified grid is a floor grid and only a floor grid, `false` otherwise.
- **Side effects**: None.
- **Relationships**: This function likely uses the `borg_grid` data structure to check the properties of the specified grid location.
- **Game mechanics**: In roguelike games, it's important to distinguish between walkable floor tiles and other types of terrain. This function provides a way to check if a given location is a plain floor tile.

### `borg_cave_floor_grid`
```c
extern bool borg_cave_floor_grid(borg_grid *ag);
```
- **Purpose**: Grid-based version of `borg_cave_floor_bold()`. Determines if a `borg_grid` represents a floor grid and only a floor grid.
- **Parameters**:
  - `ag`: A pointer to the `borg_grid` to check.
- **Return value**: Returns `true` if the specified `borg_grid` is a floor grid and only a floor grid, `false` otherwise.
- **Side effects**: None.
- **Relationships**: This function is a grid-based equivalent of `borg_cave_floor_bold()`, using a `borg_grid` pointer instead of coordinates.
- **Game mechanics**: Same as `borg_cave_floor_bold()`, but operates directly on a `borg_grid` data structure.

### `borg_feature_protected`
```c
extern bool borg_feature_protected(borg_grid *ag);
```
- **Purpose**: Determine if a `borg_grid` represents a square that is protected and doesn't need a glyph.
- **Parameters**:
  - `ag`: A pointer to the `borg_grid` to check.
- **Return value**: Returns `true` if the specified `borg_grid` is protected and doesn't need a glyph, `false` otherwise.
- **Side effects**: None.
- **Relationships**: This function likely checks specific properties of the `borg_grid` to determine if it's protected.
- **Game mechanics**: In some roguelike games, certain terrain features or object types may be protected and not require a glyph to be displayed. This function provides a way to check for such cases.

### `borg_panel_hgt`
```c
extern int borg_panel_hgt(void);
```
- **Purpose**: Get the height of the game's display panel.
- **Parameters**: None.
- **Return value**: Returns the height of the display panel as an integer.
- **Side effects**: None.
- **Relationships**: This function likely interacts with the game's display system to determine the panel height.
- **Game mechanics**: The panel height is a UI-related concept, determining how many rows of the dungeon are displayed on the screen at once.

### `borg_panel_wid`
```c
extern int borg_panel_wid(void);
```
- **Purpose**: Get the width of the game's display panel.
- **Parameters**: None.
- **Return value**: Returns the width of the display panel as an integer.
- **Side effects**: None.
- **Relationships**: This function likely interacts with the game's display system to determine the panel width.
- **Game mechanics**: The panel width is a UI-related concept, determining how many columns of the dungeon are displayed on the screen at once.

## Algorithms

This header file does not implement any complex algorithms directly. The functions provided are utility functions for checking properties of cave grids and getting display panel dimensions.

## Dependencies

- This file depends on the `angband.h` header file for general Angband game definitions and types.
- It also depends on the `borg-cave.h` header file, which likely defines the `borg_grid` data structure used in some of the functions.
- Other files in the "borg" module likely depend on this header to use its utility functions for interacting with the cave.

## Historical Context

The "borg" module in Angband is an AI player that can automatically play the game. This header file provides utility functions for the borg to reason about and interact with the cave environment. The inclusion of the GNU General Public License and Angband License text at the top of the file suggests this code has been part of the Angband project for a long time, with contributions from multiple developers over the years.