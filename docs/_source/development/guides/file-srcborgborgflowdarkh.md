---
title: 'File: src/borg/borg-flow-dark.h'
id: file-srcborgborgflowdarkh
section: development
category: guides
created: '2025-03-14'
updated: '2025-03-14'
version: 0.1.0
---


# File: src/borg/borg-flow-dark.h

## File Overview

`borg-flow-dark.h` is a header file in the Angband roguelike game's codebase, specifically related to the "Borg" AI player. The Borg is an automated player that can navigate the dungeon and make decisions based on programmed strategies.

This header file declares a function `borg_flow_dark()` which is responsible for making the Borg AI "flow" towards "interesting" grids in the dungeon, particularly when the Borg's current location is dark (i.e., not lit).

## Data Structures

This header file does not define any data structures.

## Global Variables

This header file does not declare any global variables.

## Functions

### `borg_flow_dark()`

```c
extern bool borg_flow_dark(bool neer);
```

- **Purpose**: This function makes the Borg AI move towards "interesting" grids in the dungeon when the current location is dark.
- **Parameters**:
  - `neer` (bool): If true, the Borg will only consider grids that are directly adjacent to its current position.
- **Return value** (bool): Indicates whether the Borg successfully moved to an interesting grid.
- **Side effects**: The Borg's position in the dungeon may change as a result of calling this function.
- **Relationships to other functions**: This function is part of the Borg AI's decision-making process and may be called by other Borg AI functions.
- **Game mechanics implemented**: This function helps the Borg navigate the dungeon intelligently by seeking out interesting locations even when its surroundings are dark. The specifics of what constitutes an "interesting" grid are not defined in this header file, but likely involve factors such as item locations, monster positions, and dungeon features.

## Algorithms

This header file does not implement any algorithms directly. The actual implementation of the `borg_flow_dark()` function would contain the specific algorithm for determining interesting grids and navigating towards them.

## Dependencies

- This header file depends on `../angband.h` and `borg-flow.h`.
- Other files in the Borg AI system likely depend on this header file to access the `borg_flow_dark()` function.

## Historical Context

This file contains a copyright notice indicating that portions of the code are derived from earlier works by Ben Harrison, James E. Wilson, and Robert A. Koeneke, dating back to 1997. It also credits more recent contributors including Andi Sidwell, Chris Carr, Ed Graham, and Erik Osheim in 2007-2009.

The presence of the `ALLOW_BORG` preprocessor directive suggests that the Borg AI is an optional feature that can be enabled or disabled at compile time.