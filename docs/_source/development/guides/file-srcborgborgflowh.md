---
title: 'File: src/borg/borg-flow.h'
id: file-srcborgborgflowh
section: development
category: guides
created: '2025-03-14'
updated: '2025-03-14'
version: 0.1.0
---


# File: src/borg/borg-flow.h

## File Overview
`borg-flow.h` is a header file that contains definitions, data structures, and function prototypes related to the Borg's "flow" and pathfinding algorithms in the Angband roguelike game. The Borg is an AI player that navigates the dungeon, makes decisions, and fights monsters autonomously. This file plays a crucial role in the Borg's decision-making process by providing the necessary data structures and functions for the Borg to find optimal paths and navigate the dungeon effectively.

## Data Structures

### struct borg_track
The `borg_track` structure is used to track the locations of certain things in the dungeon.

- `num`: The number of elements being tracked.
- `size`: The maximum size of the track array.
- `x`: An array of x-coordinates for the tracked elements.
- `y`: An array of y-coordinates for the tracked elements.

### struct borg_data
The `borg_data` structure encapsulates a 2D array of bytes, representing various data about each grid in the dungeon.

- `data[AUTO_MAX_Y][AUTO_MAX_X]`: A 2D array of bytes holding the data for each grid.

## Global Variables

- `borg_flow_n`: The number of grids in the "flow" array.
- `borg_flow_y[AUTO_FLOW_MAX]`: An array of y-coordinates for the grids in the "flow" array.
- `borg_flow_x[AUTO_FLOW_MAX]`: An array of x-coordinates for the grids in the "flow" array.
- `flow_head`: The head index of the "flow" array queue.
- `flow_tail`: The tail index of the "flow" array queue.
- `borg_data_flow`: A pointer to the current "flow" data.
- `borg_data_cost`: A pointer to the current "cost" data.
- `borg_data_hard`: A pointer to the constant "hard" data.
- `borg_data_know`: A pointer to the current "know" flags.
- `borg_data_icky`: A pointer to the current "icky" flags.
- `borg_temp_n`: The number of grids in the "temp" array.
- `borg_temp_y[AUTO_TEMP_MAX]`: An array of y-coordinates for the grids in the "temp" array.
- `borg_temp_x[AUTO_TEMP_MAX]`: An array of x-coordinates for the grids in the "temp" array.
- `track_step`: A `borg_track` structure for tracking steps.
- `track_door`: A `borg_track` structure for tracking closed doors which the Borg has closed.
- `track_closed`: A `borg_track` structure for tracking closed doors which started closed.
- `borg_desperate`: A boolean indicating if the Borg is in a desperate situation.
- `vault_on_level`: A boolean indicating if there is a vault on the current level.
- `borg_t_antisummon`: An integer used for anti-summoning.
- `borg_as_position`: A boolean related to anti-summoning position.
- `borg_digging`: A boolean indicating if the Borg is currently digging.
- `my_need_alter`: A boolean indicating if the Borg needs to alter something.
- `my_no_alter`: A boolean indicating if the Borg is not allowed to alter something.
- `my_need_redraw`: A boolean indicating if the Borg needs to redraw the screen.
- `avoidance`: The current danger threshold for the Borg.
- `borg_ddx_ddd[24]`: An array of x-coordinate offsets for search grids.
- `borg_ddy_ddd[24]`: An array of y-coordinate offsets for search grids.

## Functions

### borg_can_dig
```c
bool borg_can_dig(bool check_fail, uint8_t feat);
```
Checks if the Borg can dig through a specific feature.

- Parameters:
  - `check_fail`: A boolean indicating whether to check for failure conditions.
  - `feat`: The feature to check for diggability.
- Returns: A boolean indicating whether the Borg can dig through the specified feature.
- Side Effects: None.
- Related Functions: None.
- Game Mechanics: Determines if the Borg has the necessary equipment and capabilities to dig through a specific dungeon feature.

### borg_flow_clear
```c
void borg_flow_clear(void);
```
Clears the "flow" information.

- Parameters: None.
- Returns: None.
- Side Effects: Clears the "flow" data structures.
- Related Functions: None.
- Game Mechanics: Resets the "flow" information used by the Borg's pathfinding algorithms.

### borg_flow_spread
```c
void borg_flow_spread(int depth, bool optimize, bool avoid, bool tunneling, int stair_idx, bool sneak);
```
Spreads a "flow" from the "destination" grids outwards.

- Parameters:
  - `depth`: The maximum depth to spread the flow.
  - `optimize`: A boolean indicating whether to optimize the flow.
  - `avoid`: A boolean indicating whether to avoid certain grids.
  - `tunneling`: A boolean indicating whether tunneling is allowed.
  - `stair_idx`: The index of the stairs to consider.
  - `sneak`: A boolean indicating whether the Borg is sneaking.
- Returns: None.
- Side Effects: Modifies the "flow" data structures.
- Related Functions: None.
- Game Mechanics: Implements the core of the Borg's pathfinding algorithm, spreading a "flow" from the destination grids to determine optimal paths.

### borg_flow_enqueue_grid
```c
void borg_flow_enqueue_grid(int y, int x);
```
Enqueues a fresh (legal) starting grid, if it is safe.

- Parameters:
  - `y`: The y-coordinate of the grid to enqueue.
  - `x`: The x-coordinate of the grid to enqueue.
- Returns: None.
- Side Effects: Modifies the "flow" data structures.
- Related Functions: None.
- Game Mechanics: Adds a new starting grid to the "flow" queue for pathfinding.

### borg_flow_commit
```c
bool borg_flow_commit(const char *who, int why);
```
Commits the current "flow".

- Parameters:
  - `who`: A string identifying who is committing the flow.
  - `why`: An integer indicating the reason for committing the flow.
- Returns: A boolean indicating whether the flow was successfully committed.
- Side Effects: Modifies the "flow" data structures.
- Related Functions: None.
- Game Mechanics: Finalizes the current "flow" and prepares it for use in pathfinding.

### borg_flow_old
```c
bool borg_flow_old(int why);
```
Attempts to take an optimal step towards the current goal location.

- Parameters:
  - `why`: An integer indicating the reason for the step.
- Returns: A boolean indicating whether a step was successfully taken.
- Side Effects: Modifies the Borg's position and state.
- Related Functions: None.
- Game Mechanics: Uses the current "flow" to determine the optimal step for the Borg to take towards its goal location.

### borg_init_track
```c
void borg_init_track(struct borg_track *track, int size);
```
Initializes a `borg_track` structure.

- Parameters:
  - `track`: A pointer to the `borg_track` structure to initialize.
  - `size`: The maximum size of the track array.
- Returns: None.
- Side Effects: Modifies the `borg_track` structure.
- Related Functions: `borg_free_track`.
- Game Mechanics: Sets up a `borg_track` structure for tracking dungeon elements.

### borg_free_track
```c
void borg_free_track(struct borg_track *track);
```
Frees the memory associated with a `borg_track` structure.

- Parameters:
  - `track`: A pointer to the `borg_track` structure to free.
- Returns: None.
- Side Effects: Frees memory.
- Related Functions: `borg_init_track`.
- Game Mechanics: Cleans up a `borg_track` structure when it is no longer needed.

### borg_init_flow
```c
void borg_init_flow(void);
```
Initializes the Borg's flow-related data structures.

- Parameters: None.
- Returns: None.
- Side Effects: Modifies the Borg's flow-related data structures.
- Related Functions: `borg_free_flow`.
- Game Mechanics: Sets up the necessary data structures for the Borg's pathfinding algorithms.

### borg_free_flow
```c
void borg_free_flow(void);
```
Frees the memory associated with the Borg's flow-related data structures.

- Parameters: None.
- Returns: None.
- Side Effects: Frees memory.
- Related Functions: `borg_init_flow`.
- Game Mechanics: Cleans up the Borg's flow-related data structures when they are no longer needed.

## Algorithms

The main algorithm in this file is the Borg's pathfinding algorithm, implemented in the `borg_flow_spread` function. This function uses a flood-fill approach to spread a "flow" from the destination grids outwards, assigning costs to each grid based on various factors such as distance, terrain, and obstacles. The Borg then uses this "flow" information to determine the optimal path to its goal location.

## Dependencies

This file depends on the following files:
- `../angband.h`: The main Angband header file.
- `borg-cave.h`: Header file containing definitions related to the Borg's cave management.

Other files that may depend on this file:
- Other Borg-related source files that use the functions and data structures defined here.

## Historical Context

The Borg AI player was a significant addition to the Angband roguelike game, providing players with an automated way to explore the dungeon and fight monsters. The code in this file represents a crucial part of the Borg's decision-making process, particularly in terms of pathfinding and navigation. Over time, the Borg AI has been refined and improved to better handle the challenges of the Angband dungeon.