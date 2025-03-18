---
title: borg-flow-misc.h File Documentation
id: borgflowmisch-file-documentation
section: development
category: guides
created: '2025-03-14'
updated: '2025-03-14'
version: 0.1.0
---


# borg-flow-misc.h File Documentation

## File Overview
The `borg-flow-misc.h` file is part of the Borg AI system in Angband, which is an automated player that can play the game independently. This header file declares various functions and data structures used by the Borg AI to make decisions related to movement, exploration, and recovery.

The primary purpose of the code in this file is to handle the "flow" of the Borg AI, which involves navigating the dungeon, searching for items, and managing resources. The functions declared here are responsible for tasks such as locating store doors, tracking mineral veins, checking for safe resting spots, and moving towards light sources or vault grids.

## Data Structures

### `borg_track` Structure
The `borg_track` structure is used to track the mineral veins with treasure. It likely contains fields to store the location and properties of the veins, but the actual definition is not provided in this header file.

## Global Variables

### `track_shop_x` and `track_shop_y` Variables
- Type: `int *`
- Purpose: Arrays to store the x and y coordinates of store doors in the dungeon.

### `track_vein` Variable
- Type: `struct borg_track`
- Purpose: Tracks the mineral veins with treasure in the dungeon.

## Functions

### `borg_check_rest` Function
- Purpose: Checks if there are any monsters around that should prevent resting at a given location.
- Parameters:
  - `y`: The y-coordinate of the resting location.
  - `x`: The x-coordinate of the resting location.
- Return Value: Returns `true` if it is safe to rest at the specified location, `false` otherwise.

### `borg_flow_reverse` Function
- Purpose: Performs a "reverse" flow from the player outwards, likely to explore or escape the dungeon.
- Parameters:
  - `depth`: The depth of the dungeon level.
  - `optimize`: A boolean indicating whether to optimize the flow.
  - `avoid`: A boolean indicating whether to avoid certain grids during the flow.
  - `tunneling`: A boolean indicating whether tunneling is allowed during the flow.
  - `stair_idx`: The index of the stairs to consider during the flow.
  - `sneak`: A boolean indicating whether the Borg should sneak during the flow.
- Return Value: None
- Side Effects: Modifies the Borg's internal state and may cause the Borg to move or perform actions.

### `borg_happy_grid_bold` Function
- Purpose: Checks if a given floor grid is "happy" for the Borg, likely meaning it is safe or desirable.
- Parameters:
  - `y`: The y-coordinate of the grid to check.
  - `x`: The x-coordinate of the grid to check.
- Return Value: Returns `true` if the grid is considered "happy," `false` otherwise.

### `borg_flow_recover` Function
- Purpose: Makes the Borg go to a safe place to rest and recover.
- Parameters:
  - `viewable`: A boolean indicating whether the recovery spot should be viewable by the player.
  - `dist`: The maximum distance to search for a recovery spot.
- Return Value: Returns `true` if a suitable recovery spot was found and the Borg moved there, `false` otherwise.
- Side Effects: Modifies the Borg's internal state and may cause the Borg to move.

### `borg_flow_vein` Function
- Purpose: Prepares the Borg to "flow" towards mineral veins with treasure.
- Parameters:
  - `viewable`: A boolean indicating whether the mineral veins should be viewable by the player.
  - `nearness`: The maximum distance to search for mineral veins.
- Return Value: Returns `true` if mineral veins were found and the Borg prepared to flow towards them, `false` otherwise.
- Side Effects: Modifies the Borg's internal state and may cause the Borg to move.

### `borg_flow_spastic` Function
- Purpose: Makes the Borg search carefully for secret doors and other hidden features.
- Parameters:
  - `bored`: A boolean indicating whether the Borg is bored and should search more thoroughly.
- Return Value: Returns `true` if the Borg performed a spastic search, `false` otherwise.
- Side Effects: Modifies the Borg's internal state and may cause the Borg to move or perform actions.

### `borg_flow_shop_entry` Function
- Purpose: Prepares the Borg to flow towards a specific shop entry.
- Parameters:
  - `i`: The index of the shop entry to flow towards.
- Return Value: Returns `true` if the Borg prepared to flow towards the specified shop entry, `false` otherwise.
- Side Effects: Modifies the Borg's internal state and may cause the Borg to move.

### `borg_flow_light` Function
- Purpose: Prepares the Borg to flow towards light sources in the dungeon.
- Parameters:
  - `why`: An integer indicating the reason for flowing towards light (not explained in the header).
- Return Value: Returns `true` if the Borg prepared to flow towards light, `false` otherwise.
- Side Effects: Modifies the Borg's internal state and may cause the Borg to move.

### `borg_flow_vault` Function
- Purpose: Prepares the Borg to flow towards a vault grid which can be excavated.
- Parameters:
  - `nearness`: The maximum distance to search for a vault grid.
- Return Value: Returns `true` if a suitable vault grid was found and the Borg prepared to flow towards it, `false` otherwise.
- Side Effects: Modifies the Borg's internal state and may cause the Borg to move.

### `borg_twitchy` Function
- Purpose: Makes the Borg act twitchy, likely to simulate human-like behavior or to avoid detection by monsters.
- Parameters: None
- Return Value: Returns `true` if the Borg performed a twitchy action, `false` otherwise.
- Side Effects: Modifies the Borg's internal state and may cause the Borg to move or perform actions.

### `borg_extract_dir` Function
- Purpose: Extracts a direction given a source and target location.
- Parameters:
  - `y1`: The y-coordinate of the source location.
  - `x1`: The x-coordinate of the source location.
  - `y2`: The y-coordinate of the target location.
  - `x2`: The x-coordinate of the target location.
- Return Value: Returns an integer representing the direction from the source to the target.

### `borg_goto_dir` Function
- Purpose: Moves the Borg in a given direction from a source to a target location.
- Parameters:
  - `y1`: The y-coordinate of the source location.
  - `x1`: The x-coordinate of the source location.
  - `y2`: The y-coordinate of the target location.
  - `x2`: The x-coordinate of the target location.
- Return Value: Returns an integer indicating the result of the movement (not explained in the header).
- Side Effects: Modifies the Borg's internal state and may cause the Borg to move.

### `borg_flow_far_from_stairs` Function
- Purpose: Checks if a given square is "too far" from the stairs.
- Parameters:
  - `x`: The x-coordinate of the square to check.
  - `y`: The y-coordinate of the square to check.
  - `b_stair`: The index of the stairs to consider.
- Return Value: Returns `true` if the square is considered too far from the stairs, `false` otherwise.

### `borg_flow_far_from_stairs_dist` Function
- Purpose: Checks if a given square is "too far" from the stairs, considering a specific distance.
- Parameters:
  - `x`: The x-coordinate of the square to check.
  - `y`: The y-coordinate of the square to check.
  - `b_stair`: The index of the stairs to consider.
  - `distance`: The maximum distance to consider.
- Return Value: Returns `true` if the square is considered too far from the stairs within the specified distance, `false` otherwise.

### `borg_init_flow_misc` Function
- Purpose: Initializes the data structures and variables used by the flow-related functions in the Borg AI.
- Parameters: None
- Return Value: None
- Side Effects: Initializes the `track_shop_x`, `track_shop_y`, and `track_vein` variables.

### `borg_free_flow_misc` Function
- Purpose: Frees the memory allocated for the data structures and variables used by the flow-related functions in the Borg AI.
- Parameters: None
- Return Value: None
- Side Effects: Frees the memory allocated for the `track_shop_x`, `track_shop_y`, and `track_vein` variables.

## Algorithms
The specific algorithms used by the functions in this file are not evident from the header alone. The implementations of these functions would need to be examined to determine the exact algorithms employed.

## Dependencies
This header file depends on the `angband.h` header file, which is included at the beginning of the file. The functions and data structures declared in this file are likely used by other parts of the Borg AI system, but the specific dependencies are not clear from the header alone.

## Historical Context
The Borg AI system in Angband has a long history, with contributions from various developers over the years. The comments at the beginning of the file mention the original authors (Ben Harrison, James E. Wilson, and Robert A. Koeneke) as well as more recent contributors (Andi Sidwell, Chris Carr, Ed Graham, and Erik Osheim). The code in this file is part of the ongoing development and improvement of the Borg AI system.