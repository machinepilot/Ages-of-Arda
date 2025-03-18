---
title: 'File Documentation: borg-formulas-calc.h'
id: file-documentation-borgformulascalch
section: development
category: guides
created: '2025-03-14'
updated: '2025-03-14'
version: 0.1.0
---


# File Documentation: borg-formulas-calc.h

## File Overview

`borg-formulas-calc.h` is a header file in the Angband roguelike game codebase that provides functionality for parsing and calculating dynamic formulas used by the Borg AI system. The Borg is an autonomous player agent that attempts to play the game intelligently.

This file defines functions for reading mathematical calculations from formula strings and evaluating those formulas using previously parsed data. It also includes a function for freeing the memory used by the calculations.

## Data Structures

This header file does not define any structs or typedefs.

## Global Variables

This header file does not define any global variables.

## Functions

### `parse_calculation_line`

```c
extern int parse_calculation_line(char *line, const char *full_line);
```

- **Purpose**: Reads a mathematical calculation from a dynamic formula string.
- **Parameters**:
  - `line`: A pointer to the current line being parsed.
  - `full_line`: A pointer to the full formula string.
- **Return value**: An integer index of the parsed calculation, or an error code if parsing fails.
- **Side effects**: Stores the parsed calculation for later evaluation.
- **Relationships**: Used by the Borg AI to parse dynamic formulas from configuration files.
- **Game mechanics**: Allows the Borg AI to use customizable formulas for decision making.

### `borg_calculate_dynamic`

```c
extern int32_t borg_calculate_dynamic(int formula, int range_index);
```

- **Purpose**: Calculates a value from a previously parsed dynamic formula.
- **Parameters**:
  - `formula`: The integer index of the formula to evaluate.
  - `range_index`: An index into the formula's input range (if applicable).
- **Return value**: The calculated value as a 32-bit integer.
- **Side effects**: None.
- **Relationships**: Uses the calculations parsed by `parse_calculation_line`.
- **Game mechanics**: Allows the Borg AI to evaluate dynamic formulas for decision making.

### `calculations_free`

```c
extern void calculations_free(void);
```

- **Purpose**: Frees all memory used by the parsed calculations.
- **Parameters**: None.
- **Return value**: None.
- **Side effects**: Deallocates memory used by the calculations.
- **Relationships**: Should be called when the Borg AI is no longer needed.
- **Game mechanics**: Manages memory used by the Borg AI's dynamic formulas.

## Algorithms

This header file does not implement any complex algorithms directly. The actual parsing and evaluation of the formulas is likely handled in the corresponding source file.

## Dependencies

- `angband.h`: The main Angband header file, included before the `ALLOW_BORG` conditional compilation directive.
- `borg-trait.h`: A header file related to the Borg AI, included within the `ALLOW_BORG` conditional compilation block.

This header file is likely included by other files in the Borg AI subsystem.

## Historical Context

The Borg AI was developed as an autonomous player agent for Angband, capable of playing the game intelligently without human intervention. The dynamic formula parsing and evaluation system allows the Borg AI to be customized and adapted to different playstyles and strategies.

The original developers of the Borg AI are Ben Harrison, James E. Wilson, and Robert A. Koeneke, with later contributions from Andi Sidwell, Chris Carr, Ed Graham, and Erik Osheim, among others.