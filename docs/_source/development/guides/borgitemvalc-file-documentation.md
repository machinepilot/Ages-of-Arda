---
title: borg-item-val.c File Documentation
id: borgitemvalc-file-documentation
section: development
category: guides
created: '2025-03-14'
updated: '2025-03-14'
version: 0.1.0
---


# borg-item-val.c File Documentation

## File Overview

`borg-item-val.c` is part of the Angband roguelike game's "borg" AI system. The borg is an automated player that makes decisions based on game state. This file initializes and provides lookup for the "sval" (sub-value) and "kval" (kind-value) of various game items such as potions, scrolls, wands, etc. The svals and kvals are used by the borg to reason about and compare items.

## Data Structures

There are no major struct or typedef definitions in this file.

## Global Variables

This file defines a large number of global integer variables for the svals and kvals of specific item types. Some key examples:

- `sv_food_ration`: The sval for ration food items
- `sv_potion_healing`: The sval for healing potions
- `kv_potion_healing`: The corresponding kval for healing potions
- `sv_scroll_teleport`: The sval for teleportation scrolls
- `sv_rod_detection`: The sval for detection rods
- `sv_staff_holiness`: The sval for holiness staves
- `sv_wand_magic_missile`: The sval for magic missile wands

Each tval (item category like potions, scrolls, etc.) has its own set of sval globals defined. Some important tvals also have kval globals defined.

## Functions

### borg_lookup_sval_fail

```c
static int borg_lookup_sval_fail(int tval, const char *name)
```

A helper function that looks up the sval for an item subtype given its tval and name string. If the lookup fails, it logs a borg startup failure message.

- Parameters:
  - `tval`: The tval to look up the sval for
  - `name`: The name string of the sval to find
- Returns: The sval integer if found, -1 otherwise
- Side effects: May log a borg startup failure message
- Used by: `borg_init_item_val` to initialize sval globals

### borg_init_item_val

```c
void borg_init_item_val(void)
```

Initializes all the sval and kval global variables using `borg_lookup_sval_fail` and `borg_lookup_kind`.

- Parameters: None
- Returns: Nothing
- Side effects: Initializes the sval and kval globals
- Depends on: `borg_lookup_sval_fail`, `borg_lookup_kind`

### borg_lookup_kind

```c
int borg_lookup_kind(int tval, int sval)
```

Looks up the corresponding `k_idx` (kind index) for an object type given its tval and sval. Used to initialize kval globals.

- Parameters: 
  - `tval`: The tval of the object type
  - `sval`: The sval of the object type
- Returns: The k_idx if found, 0 otherwise
- Side effects: May print an error message if lookup fails
- Used by: `borg_init_item_val` to initialize kval globals

## Algorithms

No major complex algorithms. The file mainly deals with data setup and lookup.

## Dependencies

- Includes several Angband core headers: `init.h`, `obj-tval.h`, `obj-util.h`
- Includes some borg-specific headers: `borg-init.h`, `borg-io.h`
- Is `#included` in other borg files that use the sval and kval globals

## Historical Context

The borg AI system was a later addition to Angband, aimed at creating an automated player. This file is part of the borg's initialization and world modeling logic, allowing it to understand and differentiate game items. The Angband borg was developed by Ben Harrison, building on ideas from earlier Moria and Angband AI projects.

Understanding object types is a key aspect of roguelike AI, as the borg needs to be able to reason about and compare the relative worth of different items for survival and dungeon exploration. The sval and kval abstractions help simplify this reasoning.