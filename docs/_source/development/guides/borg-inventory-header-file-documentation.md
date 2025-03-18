---
title: Borg Inventory Header File Documentation
id: borg-inventory-header-file-documentation
section: development
category: guides
created: '2025-03-14'
updated: '2025-03-14'
version: 0.1.0
---


# Borg Inventory Header File Documentation

## File Overview

`borg-inventory.h` is a header file in the Angband roguelike game's codebase, specifically within the "borg" module. The borg is an AI player that can autonomously play the game. This file contains declarations and definitions related to managing the borg's inventory and equipment.

The header includes functions for parsing the player's inventory and equipment screens, determining item values and usability, and making decisions about item usage and management. It also defines some key data structures and constants used in the borg's inventory logic.

## Data Structures

This header does not directly define any structs or typedefs. However, it does rely on the `borg_item` struct which is defined in `borg-item.h`.

## Global Variables

- `borg_do_crush_junk`: A boolean variable that tracks whether the borg needs to crush (destroy) junk items to free up inventory space.

## Functions

### `borg_wield_slot`

```c
extern int borg_wield_slot(const borg_item *item);
```

- **Purpose**: Determine which equipment slot an item could be wielded into.
- **Parameters**:
  - `item`: A pointer to a `borg_item` struct representing the item to check.
- **Return value**: An integer representing the equipment slot the item can be wielded into, or -1 if it cannot be wielded.
- **Side effects**: None.
- **Relationships**: Uses the `borg_item` struct defined in `borg-item.h`.
- **Game mechanics**: Implements the logic for determining if an item is wieldable and in which slot based on its type and the game's equipment rules.

### `borg_slot`

```c
extern int borg_slot(int tval, int sval);
```

- **Purpose**: Find an item in the borg's inventory with a given tval (type value) and sval (subtype value).
- **Parameters**:
  - `tval`: The desired item's tval.
  - `sval`: The desired item's sval.
- **Return value**: The inventory slot of the first item found matching the given tval and sval, or -1 if no such item is found.
- **Side effects**: None.
- **Relationships**: None.
- **Game mechanics**: Provides a way to search the borg's inventory for specific item types.

### `borg_cheat_equip` and `borg_cheat_inven`

```c
extern void borg_cheat_equip(void);
extern void borg_cheat_inven(void);
```

- **Purpose**: Parse the player's equipment and inventory screens to update the borg's knowledge of its gear.
- **Parameters**: None.
- **Return value**: None.
- **Side effects**: Updates the borg's internal representation of its equipment and inventory.
- **Relationships**: These functions are called as part of the borg's game state update process.
- **Game mechanics**: Allows the borg to "cheat" by reading the player's actual inventory and equipment information from the game's interface.

### `borg_first_empty_inventory_slot`

```c
extern int borg_first_empty_inventory_slot(void);
```

- **Purpose**: Find the first empty slot in the borg's inventory.
- **Parameters**: None.
- **Return value**: The index of the first empty inventory slot, or -1 if the inventory is full.
- **Side effects**: None.
- **Relationships**: Used by the borg when deciding whether to pick up new items.
- **Game mechanics**: Helps manage the borg's inventory by finding available space.

### `borg_item_worth_id`

```c
extern bool borg_item_worth_id(const borg_item *item);
```

- **Purpose**: Determine if an item is likely to be worthless and not worth identifying.
- **Parameters**:
  - `item`: A pointer to a `borg_item` struct representing the item to evaluate.
- **Return value**: True if the item is likely worthless, false if it may be worth identifying.
- **Side effects**: None.
- **Relationships**: Uses the `borg_item` struct defined in `borg-item.h`.
- **Game mechanics**: Implements heuristics for judging item value based on the borg's knowledge and game mechanics, to avoid wasting resources identifying junk items.

## Algorithms

This header does not implement any complex algorithms directly. The decision-making logic for inventory management is likely spread across other files in the borg module.

## Dependencies

- `angband.h`: The main Angband header file, included before this header.
- `borg-item.h`: Defines the `borg_item` struct used in this header.

This header is likely included by several other files in the borg module that implement inventory-related logic.

## Historical Context

The comments at the top of the file indicate that this code is part of a long-running open-source project with contributions dating back to 1997. The borg module itself seems to have been developed starting around 2007.

The borg AI player is a distinctive feature of Angband compared to other roguelikes. Its development over the years has involved fine-tuning the AI to handle the game's complex item and resource management challenges.