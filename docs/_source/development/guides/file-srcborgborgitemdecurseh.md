---
title: 'File: src/borg/borg-item-decurse.h'
id: file-srcborgborgitemdecurseh
section: development
category: guides
created: '2025-03-14'
updated: '2025-03-14'
version: 0.1.0
---


# File: src/borg/borg-item-decurse.h

## File Overview

This header file is part of the Angband roguelike game's "borg" module, which implements an AI player (bot) for the game. The file specifically deals with the AI's ability to handle cursed items by attempting to remove curses from the character's equipped armor and weapons.

The header defines three functions that the AI uses to manage cursed items:

1. `borg_decurse_armour()`: Attempts to remove curses from equipped armor.
2. `borg_decurse_weapon()`: Attempts to remove curses from equipped weapons.
3. `borg_decurse_any()`: Attempts to remove curses from any equipped item.

## Data Structures

This header file does not define any data structures.

## Global Variables

This header file does not define any global variables.

## Functions

### `borg_decurse_armour()`

```c
extern bool borg_decurse_armour(void);
```

- **Purpose**: Attempts to remove curses from the character's equipped armor.
- **Parameters**: None
- **Return value**: `true` if the function managed to remove a curse, `false` otherwise.
- **Side effects**: May modify the character's inventory and equipped items.
- **Game mechanics implemented**: 
  - Checks if any equipped armor is cursed.
  - Attempts to uncurse the armor using various methods (scrolls, spells, etc.).
  - If successful, re-equips the uncursed armor.

### `borg_decurse_weapon()`

```c
extern bool borg_decurse_weapon(void);
```

- **Purpose**: Attempts to remove curses from the character's equipped weapons.
- **Parameters**: None
- **Return value**: `true` if the function managed to remove a curse, `false` otherwise.
- **Side effects**: May modify the character's inventory and equipped items.
- **Game mechanics implemented**:
  - Checks if any equipped weapons are cursed. 
  - Attempts to uncurse the weapons using various methods (scrolls, spells, etc.).
  - If successful, re-equips the uncursed weapons.

### `borg_decurse_any()`

```c
extern bool borg_decurse_any(void);
```

- **Purpose**: Attempts to remove curses from any of the character's equipped items.
- **Parameters**: None
- **Return value**: `true` if the function managed to remove a curse, `false` otherwise.
- **Side effects**: May modify the character's inventory and equipped items.
- **Game mechanics implemented**:
  - Checks if any equipped items are cursed.
  - Attempts to uncurse the items using various methods (scrolls, spells, etc.).
  - If successful, re-equips the uncursed items.

## Algorithms

This header does not implement any complex algorithms directly. The actual implementations of the curse removal mechanics would be found in the corresponding .c file.

## Dependencies

- This header file depends on the core Angband header `angband.h`.
- The actual implementations of these functions in `borg-item-decurse.c` likely depend on various other borg and core Angband files.

## Historical Context

The borg module was originally developed by Ben Harrison and has been maintained and expanded by various Angband developers over the years. The curse removal functionality is an important part of the AI's item management capabilities, as cursed items in roguelikes often have significant negative effects on the character until removed.