---
title: borg-formulas.h Documentation
id: borgformulash-documentation
section: development
category: guides
created: '2025-03-14'
updated: '2025-03-14'
version: 0.1.0
---


# borg-formulas.h Documentation

## File Overview

`borg-formulas.h` is a header file in the Angband roguelike game codebase that provides data structures, enums, and function declarations for the Borg AI system's formula handling. The Borg is an automated player that makes decisions based on predefined formulas and heuristics.

This file defines the data structures used to represent formulas, provides functions for parsing and evaluating these formulas, and includes declarations for functions that calculate various aspects of the Borg's decision-making process, such as its power level and readiness to descend to deeper dungeon levels.

## Data Structures

### `struct borg_array`

A simple growing array of pointers.

- `int max`: The maximum number of items the array can hold.
- `int count`: The current number of items in the array.
- `void **items`: The array of pointers to the items.

### `enum value_type`

An enumeration of possible types for values used in formulas.

- `VT_NONE = -1`: Indicates an error.
- `VT_RANGE_INDEX`: The index into range processing.
- `VT_TRAIT`: A Borg trait value.
- `VT_CONFIG`: A configuration value.
- `VT_ACTIVATION`: An activation value.
- `VT_CLASS`: A character class value.
- `VT_*`: Various tval types (e.g., `VT_SWORD`, `VT_POTION`, etc.).
- `VT_MAX`: The maximum valid value type.

### `struct value_sec`

Represents a value section in a formula.

- `enum value_type type`: The type of the value.
- `int32_t index`: The index associated with the value.

## Global Variables

None.

## Functions

### `int borg_array_add(struct borg_array *a, void *item)`

Adds an item to a `borg_array`.

- Parameters:
  - `struct borg_array *a`: The array to add the item to.
  - `void *item`: The item to add.
- Returns: The index of the added item in the array.
- Side effects: Modifies the `borg_array` by adding the item.

### `void borg_formula_error(const char *section, const char *full_line, const char *section_label, const char *error)`

Notes an error in a formula.

- Parameters:
  - `const char *section`: The section of the line where the error occurred.
  - `const char *full_line`: The full line as read from `borg.txt`.
  - `const char *section_label`: The current parsing location.
  - `const char *error`: Additional error text to clarify the error.
- Returns: None.
- Side effects: Prints an error message.

### `int32_t calculate_from_value(struct value_sec *value, int range_index)`

Calculates a value from a `value_sec` structure.

- Parameters:
  - `struct value_sec *value`: The value section to calculate from.
  - `int range_index`: The index into range processing.
- Returns: The calculated value.

### `struct value_sec *parse_value(char *line, const char *full_line)`

Parses a "value(x, y)" string into a `value_sec` structure.

- Parameters:
  - `char *line`: The string containing the value section.
  - `const char *full_line`: The full line as read from `borg.txt`.
- Returns: A pointer to the parsed `value_sec` structure.

### `int32_t borg_power_dynamic(void)`

Calculates the basic "power" of the Borg.

- Returns: The calculated power value.

### `const char *borg_prepared_dynamic(int depth)`

Determines the level the Borg is prepared to dive to.

- Parameters:
  - `int depth`: The current depth.
- Returns: A string indicating the Borg's preparedness.

### `const char *borg_restock_dynamic(int depth)`

Determines if the Borg is out of "crucial" supplies.

- Parameters:
  - `int depth`: The current depth.
- Returns: A string indicating the Borg's supply status.

### `bool borg_load_formulas(ang_file *fp)`

Loads the FORMULA SECTION from `borg.txt`.

- Parameters:
  - `ang_file *fp`: The file pointer to `borg.txt`.
- Returns: `true` if the formulas were loaded successfully, `false` otherwise.

### `void borg_free_formulas(void)`

Frees all memory used by formulas.

## Algorithms

This file does not contain any complex algorithms. It primarily focuses on data structures and function declarations related to formula handling for the Borg AI system.

## Dependencies

- Includes `"../angband.h"` for basic Angband definitions.
- Includes `"borg-trait.h"` for Borg trait definitions.
- Depends on `"../list-tvals.h"` for tval type definitions.

## Historical Context

The Borg AI system was originally developed by Ben Harrison, James E. Wilson, and Robert A. Koeneke in 1997. It was later maintained and updated by Andi Sidwell, Chris Carr, Ed Graham, and Erik Osheim in 2007-2009. The purpose of the Borg is to provide an automated player that can make intelligent decisions based on predefined formulas and heuristics, helping to test and balance the game.

The code in this file is part of the larger Borg AI system and focuses on the data structures and functions needed to handle the formulas used by the Borg to make decisions. These formulas are loaded from the `borg.txt` file and are used to calculate various aspects of the Borg's behavior, such as its power level, readiness to descend to deeper dungeon levels, and supply management.