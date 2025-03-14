# borg-item-id.h Documentation

## File Overview

`borg-item-id.h` is a header file in the Angband roguelike game codebase, specifically within the "borg" AI module. This file contains function declarations related to identifying the properties and capabilities of game items, which is a key aspect of the borg AI decision-making process.

The borg AI needs to understand the items it encounters in the dungeon in order to make informed decisions about equiping, using, and managing its inventory. The functions declared here provide an interface for the borg to query the identification status of items.

## Data Structures

This header file does not define any structs or typedefs. It relies on the `borg_item` struct which is defined in `borg-item.h`.

## Global Variables

This file does not declare any global variables.

## Functions

### `borg_object_fully_id`

```c
extern bool borg_object_fully_id(void);
```

- **Purpose:** This function checks whether there are any unidentified items in the borg's inventory.
- **Parameters:** None
- **Return Value:** Returns `true` if all items are fully identified, `false` otherwise.
- **Side Effects:** None
- **Related Functions:** Likely uses functions from `borg-item.c` to inspect the inventory.
- **Game Mechanics:** In Angband, items can have unknown properties until they are identified via scrolls, spells, or usage. The borg needs to track identification status to decide when to use identification resources.

### `borg_item_note_needs_id`

```c
extern bool borg_item_note_needs_id(const borg_item *item);
```

- **Purpose:** Checks whether a given item needs to be identified based on its inscription.
- **Parameters:**
  - `item`: A pointer to a `borg_item` struct representing the item to check.
- **Return Value:** Returns `true` if the item has an inscription indicating it needs identification, `false` otherwise.
- **Side Effects:** None
- **Related Functions:** Likely implemented in `borg-item.c`.
- **Game Mechanics:** In Angband, players can manually inscribe items with notes. The borg uses the `{??}` inscription to mark items that need identification. This function checks for that inscription.

## Algorithms

This header does not implement any complex algorithms directly. The algorithmic complexity is encapsulated in the corresponding `.c` file.

## Dependencies

- Includes `angband.h` for core game definitions.
- Includes `borg-item.h` for the `borg_item` struct definition.
- The functions declared here are likely implemented in `borg-item.c`.
- Other borg AI source files probably call the functions declared here.

## Historical Context

The borg AI was developed as an "Automatic Winner" for Angband - a program that plays the game autonomously with the goal of winning. It requires heuristics and decision-making logic for all aspects of the game, including inventory management and item identification.

The comments indicate this code incorporates work from the late 1990s to late 2000s by several contributors. The borg AI was a significant achievement in demonstrating the kind of complex behavior that can be programmed into a roguelike game AI.