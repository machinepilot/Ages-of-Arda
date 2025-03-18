---
title: borg-flow-stairs.h Documentation
id: borgflowstairsh-documentation
section: development
category: guides
created: '2025-03-14'
updated: '2025-03-14'
version: 0.1.0
---


# borg-flow-stairs.h Documentation

## File Overview

`borg-flow-stairs.h` is a header file in the Angband roguelike game codebase that handles pathfinding logic related to navigating stairs within the dungeon. It is part of the "Borg" system, which is an AI player that can autonomously navigate the game.

This file provides functions for calculating the cost of moving to stairs, preparing to use stairs to flee or navigate levels, and casting preparatory spells before level transitions. It also defines data structures for tracking the location of upward and downward stairs.

## Data Structures

The file defines two main data structures:

1. `struct borg_track track_less`: Tracks the location of upward stairs ("stairs up").

2. `struct borg_track track_more`: Tracks the location of downward stairs ("stairs down").

The `borg_track` struct is defined in `borg-flow.h`, which is included by this file.

## Global Variables

- `track_less`: An instance of `struct borg_track` that holds information about the location of upward stairs.

- `track_more`: An instance of `struct borg_track` that holds information about the location of downward stairs.

## Functions

1. `borg_flow_cost_stair(int y, int x, int b_stair)`
   - Purpose: Calculates the cost of moving to a specific grid location based on its proximity to the closest upward or downward stair.
   - Parameters:
     - `y`, `x`: The coordinates of the grid to calculate the cost for.
     - `b_stair`: The type of stair to consider (upward or downward).
   - Return value: The cost of moving to the specified grid location.
   - Side effects: None.
   - Relationships: Used by other pathfinding functions to determine optimal paths.
   - Game mechanics: Implements a cost heuristic for AI pathfinding based on stair proximity.

2. `borg_flow_stair_both(int why, bool sneak)`
   - Purpose: Prepares the Borg AI to flee the current level using either upward or downward stairs.
   - Parameters:
     - `why`: The reason for fleeing (e.g., low health, dangerous situation).
     - `sneak`: Whether to use sneaking/stealth during the flee operation.
   - Return value: True if successfully prepared to flee, False otherwise.
   - Side effects: Modifies Borg AI state and may initiate level transition.
   - Relationships: Calls `borg_flow_stair_less()` and `borg_flow_stair_more()` internally.
   - Game mechanics: Implements AI decision-making for fleeing levels based on situational factors.

3. `borg_flow_stair_less(int why, bool sneak)`
   - Purpose: Prepares the Borg AI to navigate towards the upward stairs on the current level.
   - Parameters:
     - `why`: The reason for navigating to the upward stairs.
     - `sneak`: Whether to use sneaking/stealth during the navigation.
   - Return value: True if successfully prepared to navigate to upward stairs, False otherwise.
   - Side effects: Modifies Borg AI state and may initiate level transition.
   - Relationships: Called by `borg_flow_stair_both()`.
   - Game mechanics: Implements AI pathfinding to upward stairs.

4. `borg_flow_stair_more(int why, bool sneak, bool brave)`
   - Purpose: Prepares the Borg AI to navigate towards the downward stairs on the current level.
   - Parameters:
     - `why`: The reason for navigating to the downward stairs.
     - `sneak`: Whether to use sneaking/stealth during the navigation.
     - `brave`: Whether to navigate aggressively or cautiously.
   - Return value: True if successfully prepared to navigate to downward stairs, False otherwise.
   - Side effects: Modifies Borg AI state and may initiate level transition.
   - Relationships: Called by `borg_flow_stair_both()`.
   - Game mechanics: Implements AI pathfinding to downward stairs, considering bravery/caution.

5. `borg_prep_leave_level_spells(void)`
   - Purpose: Prepares and casts necessary spells before the Borg AI leaves the current level.
   - Parameters: None.
   - Return value: True if successfully prepared spells, False otherwise.
   - Side effects: Casts spells and modifies Borg AI state.
   - Relationships: Called as part of the level transition process.
   - Game mechanics: Implements AI spell-casting logic for pre-transition buffs and effects.

6. `borg_init_flow_stairs(void)`
   - Purpose: Initializes the stair tracking data structures (`track_less` and `track_more`).
   - Parameters: None.
   - Return value: None.
   - Side effects: Modifies global stair tracking variables.
   - Relationships: Should be called during Borg AI initialization.
   - Game mechanics: Sets up initial state for stair-related pathfinding.

7. `borg_free_flow_stairs(void)`
   - Purpose: Frees any resources associated with the stair tracking data structures.
   - Parameters: None.
   - Return value: None.
   - Side effects: Deallocates memory and cleans up stair tracking state.
   - Relationships: Should be called during Borg AI shutdown.
   - Game mechanics: Cleans up stair-related pathfinding state.

## Algorithms

The main algorithmic component in this file is the `borg_flow_cost_stair()` function, which calculates the cost of moving to a specific grid location based on its proximity to the closest upward or downward stair. The exact algorithm is not shown in the header file, but it likely uses a heuristic based on the Manhattan distance or similar metric to estimate the cost of reaching the stairs from the given location.

The other functions in the file use this cost calculation to make decisions about navigating to stairs, fleeing levels, and preparing spells before level transitions. The specific algorithms for these behaviors are not detailed in the header file.

## Dependencies

- `borg-flow-stairs.h` includes `../angband.h` for access to core Angband game definitions and data structures.
- It also includes `borg-flow.h`, which likely defines the `borg_track` struct and other Borg AI pathfinding components.
- Other Borg AI source files may include and use the functions and data structures defined in `borg-flow-stairs.h`.

## Historical Context

The code in this file is part of the larger Borg AI system, which has been developed and refined by multiple contributors over the years. The header comment indicates that the code is based on work by Ben Harrison, James E. Wilson, and Robert A. Koeneke, with further contributions and modifications by Andi Sidwell, Chris Carr, Ed Graham, and Erik Osheim.

The Borg AI was a significant advancement in roguelike game AI, demonstrating the possibility of creating an autonomous player that could navigate the complex game world and make strategic decisions based on game state. The stair navigation logic in this file is one component of the larger Borg AI system.