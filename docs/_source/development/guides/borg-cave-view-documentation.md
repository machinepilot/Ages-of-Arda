---
title: Borg Cave View Documentation
id: borg-cave-view-documentation
section: development
category: guides
created: '2025-03-14'
updated: '2025-03-14'
version: 0.1.0
---


# Borg Cave View Documentation

## File Overview

`borg-cave-view.h` is a header file in the Angband roguelike game codebase that defines data structures and functions related to the "view" system used by the Borg AI player. The Borg is an automated player that uses AI techniques to explore the dungeon and make gameplay decisions.

The view system maintains a set of grids that are currently viewable by the Borg AI. It uses various flags to track the state and properties of each grid, such as whether it is lit, in line of sight, or has been observed before.

This file is part of the larger Borg AI subsystem within Angband.

## Data Structures

### `AUTO_VIEW_MAX`

A macro constant that defines the maximum size of the "view" array used to store viewable grids for the Borg AI. It is currently set to 9000.

### Flags for the "info" field of grids

The following flags are used in the "info" field of grids to track various properties:

- `BORG_MARK`: The grid has been "observed" by the Borg AI, though the terrain feature may or may not be memorized.
- `BORG_GLOW`: The grid is probably "perma-lit", but could be recently darkened by a darkness attack.
- `BORG_DARK`: The grid is probably not "perma-lit", but could be recently lit by a "call lite" spell.
- `BORG_OKAY`: The grid is on the current panel (screen view).
- `BORG_LIGHT`: The grid is probably lit by the player's torch, subject to the accuracy of nearby "BORG_VIEW" flags and the current lite radius.
- `BORG_VIEW`: The grid is probably in line of sight of the player, subject to the accuracy of information about intervening grids.
- `BORG_TEMP`: The grid has been added to the "borg_temp_x"/"borg_temp_y" arrays (typically ignored).
- `BORG_XTRA`: Used for various "extra" purposes, primarily to assist with the "update_view()" code.
- `BORG_IGNORE_MAP`: Causes the Borg AI to prefer its internally tracked information about an unseen grid over what is returned by the game's `map_info()` function.

These flags are used as bitmasks and can be combined using bitwise operations.

## Global Variables

- `borg_view_n`: An integer (int16_t) that stores the number of grids currently in the Borg AI's view.
- `borg_view_y`: An array (uint8_t) that stores the y-coordinates of the viewable grids.
- `borg_view_x`: An array (uint8_t) that stores the x-coordinates of the viewable grids.

The `borg_view_y` and `borg_view_x` arrays are used in conjunction with `borg_view_n` to maintain the set of viewable grids.

## Functions

### `borg_forget_view`

```c
void borg_forget_view(void);
```

- Purpose: Forgets the current "view" maintained by the Borg AI.
- Parameters: None
- Return Value: None
- Side Effects: Clears the `borg_view_n`, `borg_view_y`, and `borg_view_x` arrays, effectively resetting the Borg AI's view.
- Relationships: Called when the Borg AI needs to forget its current view, such as when the game state changes significantly.
- Game Mechanics: Implements the forgetting of the Borg AI's view, allowing it to start fresh with new observations.

### `borg_update_view`

```c
void borg_update_view(void);
```

- Purpose: Updates the "view" maintained by the Borg AI based on the current game state.
- Parameters: None
- Return Value: None
- Side Effects: Modifies the `borg_view_n`, `borg_view_y`, and `borg_view_x` arrays to reflect the updated view.
- Relationships: Called periodically to keep the Borg AI's view synchronized with the actual game state.
- Game Mechanics: Implements the updating of the Borg AI's view, allowing it to make decisions based on the most recent information about the dungeon and its surroundings.

## Algorithms

The specific algorithms used by the `borg_update_view` function to update the Borg AI's view are not provided in this header file. The implementation details would be found in the corresponding source file.

## Dependencies

This header file depends on the `angband.h` header file, which is included before the `ALLOW_BORG` macro check. It is likely that other parts of the Borg AI subsystem depend on this header file to access the view-related data structures and functions.

## Historical Context

The code in this header file includes copyright notices dating back to 1997, indicating that it has been part of the Angband codebase for a significant period. The Borg AI player is a well-known feature of Angband and has undergone various improvements and modifications over the years.

The presence of the `ALLOW_BORG` macro suggests that the Borg AI code can be conditionally compiled, allowing the game to be built with or without the Borg AI functionality.