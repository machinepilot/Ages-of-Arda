# Borg Flow Take Documentation

## File Overview

`borg-flow-take.h` is a header file in the Angband roguelike game codebase, specifically for the Borg AI system. The Borg is an automated player that makes decisions based on game state analysis. This file defines data structures and function prototypes related to the Borg's decision-making process for taking (picking up) objects in the dungeon.

The primary purpose of this code is to allow the Borg to evaluate and prioritize objects on the ground, then navigate towards high-value targets to collect them. This involves tracking object locations, properties, and values, as well as providing algorithms for optimal pathfinding.

## Data Structures

### `borg_take`

The `borg_take` struct represents an object that the Borg is tracking and considering taking.

- `kind`: Pointer to the `object_kind` (type) of the object.
- `known`: Boolean indicating if the object's kind has been verified.
- `seen`: Boolean indicating if the Borg has assigned a motion to reach this object.
- `extra`: Unused boolean flag for additional state tracking.
- `orbed`: Boolean indicating if the Orb of Draining spell has been cast on this object.
- `x`, `y`: Coordinates of the object's location in the dungeon.
- `when`: Turn counter for when the object was last seen by the Borg.
- `value`: The Borg's estimated value of the object, used for prioritization.
- `tval`: The known `tval` (type value) of the object.

## Global Variables

- `borg_takes_cnt`: Current number of objects being tracked in the `borg_takes` array.
- `borg_takes_nxt`: Index of the next available slot in the `borg_takes` array.
- `borg_takes`: Array of `borg_take` structs representing the objects being tracked.

## Functions

### `borg_get_top_object`

```c
struct object *borg_get_top_object(struct chunk *c, struct loc grid);
```

- Purpose: Helper function to get the top non-ignored object at a given dungeon grid location.
- Parameters:
  - `c`: Pointer to the current dungeon `chunk`.
  - `grid`: The dungeon grid location to check.
- Return value: Pointer to the top non-ignored `object` at the specified grid, or NULL if no suitable object is found.
- Side effects: None.

### `borg_delete_take`

```c
void borg_delete_take(int i);
```

- Purpose: Delete an old "object" record from the `borg_takes` array.
- Parameters:
  - `i`: Index of the object record to delete.
- Return value: None.
- Side effects: Removes the object record at index `i` from the `borg_takes` array, updating `borg_takes_cnt` and shuffling subsequent records down.

### `borg_follow_take`

```c
void borg_follow_take(int i);
```

- Purpose: Attempt to "follow" a missing object by updating its location based on other objects moving in the same direction.
- Parameters:
  - `i`: Index of the object record to follow.
- Return value: None.
- Side effects: Updates the location of the object record at index `i` in the `borg_takes` array if a matching object is found to follow.

### `observe_take_diff`

```c
bool observe_take_diff(int y, int x, uint8_t a, wchar_t c);
```

- Purpose: Attempt to notice a changing "take" by comparing the current dungeon state with the Borg's tracked object list.
- Parameters:
  - `y`, `x`: Coordinates of the dungeon grid to check.
  - `a`: Attribute (color) of the object glyph.
  - `c`: Character code for the object glyph.
- Return value: Boolean indicating if a difference was observed and processed.
- Side effects: May update the `borg_takes` array based on observed differences.

### `observe_take_move`

```c
bool observe_take_move(int y, int x, int d, uint8_t a, wchar_t c);
```

- Purpose: Attempt to "track" a "take" at the given location by updating the `borg_takes` array based on observed object movement.
- Parameters:
  - `y`, `x`: Coordinates of the dungeon grid where the object was seen.
  - `d`: Direction the object is moving (based on relative offset from previous position).
  - `a`: Attribute (color) of the object glyph.
  - `c`: Character code for the object glyph.
- Return value: Boolean indicating if the object was successfully tracked.
- Side effects: May add a new record to the `borg_takes` array or update an existing one.

### `borg_flow_take`

```c
bool borg_flow_take(bool viewable, int nearness);
```

- Purpose: Prepare to "flow" towards objects to "take" by calculating paths and priorities.
- Parameters:
  - `viewable`: Boolean indicating if only viewable (in line of sight) objects should be considered.
  - `nearness`: Maximum distance from the Borg to consider objects for taking.
- Return value: Boolean indicating if a suitable object was found to flow towards.
- Side effects: Calculates flow paths and priorities for reachable objects, updating Borg state variables.

### `borg_flow_take_scum`

```c
bool borg_flow_take_scum(bool viewable, int nearness);
```

- Purpose: Prepare to "flow" towards special "scum" objects to "take" by calculating paths and priorities. "Scum" objects are those which the Borg should only pursue if no other goals are available.
- Parameters:
  - `viewable`: Boolean indicating if only viewable (in line of sight) objects should be considered.
  - `nearness`: Maximum distance from the Borg to consider objects for taking.
- Return value: Boolean indicating if a suitable "scum" object was found to flow towards.
- Side effects: Calculates flow paths and priorities for reachable "scum" objects, updating Borg state variables.

### `borg_flow_take_lunal`

```c
bool borg_flow_take_lunal(bool viewable, int nearness);
```

- Purpose: Prepare to "flow" towards special "lunal" objects to "take" by calculating paths and priorities. "Lunal" objects are those which are only relevant in certain special dungeon branches or areas.
- Parameters:
  - `viewable`: Boolean indicating if only viewable (in line of sight) objects should be considered.
  - `nearness`: Maximum distance from the Borg to consider objects for taking.
- Return value: Boolean indicating if a suitable "lunal" object was found to flow towards.
- Side effects: Calculates flow paths and priorities for reachable "lunal" objects, updating Borg state variables.

### `borg_init_flow_take`

```c
void borg_init_flow_take(void);
```

- Purpose: Initialize the `borg_takes` array and related state variables for a new game or level.
- Parameters: None.
- Return value: None.
- Side effects: Clears the `borg_takes` array and resets `borg_takes_cnt` and `borg_takes_nxt`.

### `borg_free_flow_take`

```c
void borg_free_flow_take(void);
```

- Purpose: Free any resources associated with the `borg_takes` array and related state variables.
- Parameters: None.
- Return value: None.
- Side effects: Deallocates memory used by the `borg_takes` array (if any).

## Algorithms

The main algorithms in this file relate to the Borg's decision-making process for taking objects:

1. Object tracking: The Borg maintains a list of objects in the dungeon that it considers valuable. When the Borg observes changes in the dungeon state (objects appearing, disappearing, or moving), it updates its object list accordingly. This involves comparing the current state to the previous state and making inferences about object movements.

2. Object evaluation: Each tracked object is assigned a value based on the Borg's assessment of its worth. This value takes into account factors such as the object's type, rarity, potential usefulness to the character, and distance from the Borg. The Borg uses these values to prioritize which objects to pursue.

3. Pathfinding: Once the Borg has identified a high-value object to take, it needs to navigate the dungeon to reach the object's location. The `borg_flow_take` functions handle this by calculating a path from the Borg's current location to the target object. The pathfinding algorithm likely takes into account factors such as distance, obstacles, and potential dangers along the route.

4. Special case handling: The `borg_flow_take_scum` and `borg_flow_take_lunal` functions provide specialized handling for certain categories of objects. "Scum" objects are low-priority items that the Borg should only pursue if no other goals are available, while "lunal" objects are those that are only relevant in specific dungeon areas or branches. These functions allow the Borg to adapt its object-taking behavior based on the current game context.

## Dependencies

This file depends on:

- `angband.h`: The main Angband header file, which defines core game data structures and constants.
- `borg-flow.h`: Header file defining data structures and functions related to the Borg's general "flow" algorithms for navigation and decision-making.

Other files that depend on `borg-flow-take.h` may include:

- `borg-think.c`: The main Borg "thinking" logic which decides on high-level goals and actions.
- `borg-flow.c`: Implementation of general Borg "flow" algorithms which may call the `borg_flow_take` functions.

## Historical Context

The Borg AI system was originally developed by Ben Harrison, James E. Wilson, and Robert A. Koeneke for earlier versions of Angband. The code in this file, however, is attributed to more recent contributors including Andi Sidwell, Chris Carr, Ed Graham, and Erik Osheim, with modifications made between 2007-2009.

The Borg represents an early attempt at creating an automated player for roguelike games, with the goal of demonstrating how an AI system can navigate the complex decision spaces and challenges posed by these games. While newer and more sophisticated game AI techniques have since been developed, the Borg remains an interesting historical example and a testament to the long-running community efforts to extend and enhance the Angband codebase.