---
title: 'File: src/alloc.h'
id: file-srcalloch
section: development
category: guides
created: '2025-03-14'
updated: '2025-03-14'
version: 0.1.0
---


# File: src/alloc.h

## File Overview

`alloc.h` is a header file that defines the `alloc_entry` struct used for object and monster allocation in the Angband roguelike game. This struct is central to the game's allocation system, which determines the probability of objects and monsters appearing at different dungeon levels.

The allocation system uses a three-pass process to determine the final probabilities for each object or monster. The `alloc_entry` struct holds the necessary data for each item in this process.

## Data Structures

### `alloc_entry`

The `alloc_entry` struct represents an entry in the allocation table for objects or monsters. It contains the following fields:

- `index` (int): The actual index of the object or monster in the game's data tables.
- `level` (int): The base dungeon level at which this object or monster can appear.
- `prob1` (int): The probability of the object or monster being chosen, determined in pass 1 of the allocation process.
- `prob2` (int): The probability of the object or monster being chosen, determined in pass 2 of the allocation process.
- `prob3` (int): The probability of the object or monster being chosen, determined in pass 3 of the allocation process.

## Global Variables

This header file does not define any global variables.

## Functions

This header file does not define any functions.

## Algorithms

The allocation system in Angband uses a three-pass process to determine the probabilities of objects and monsters appearing at each dungeon level. The exact details of this process are not defined in this header file, but the `alloc_entry` struct provides the necessary data for each pass:

1. **Pass 1**: Determined from allocation information. This pass likely uses the base `level` and `prob1` fields to establish an initial probability.

2. **Pass 2**: Determined from allocation restriction. This pass might adjust the probability based on additional criteria, using the `prob2` field.

3. **Pass 3**: Determined from allocation calculation. The final pass finalizes the probability, possibly using a more complex calculation, and stores the result in `prob3`.

The specific algorithms for each pass are likely defined in the corresponding source files that use this header.

## Dependencies

This header file does not directly depend on any other files. However, it is likely included by various source files that implement the object and monster allocation systems.

## Historical Context

The code includes an "Angband licence" which states that the software may be copied and distributed for educational, research, and not-for-profit purposes provided that the copyright and statement are included in all copies. This suggests that Angband has a long history and has been used as a basis for various educational and research projects over the years.

The GNU General Public License (GPL) is also mentioned, implying that Angband is open-source software and welcomes contributions from the community.

Understanding this historical context helps to appreciate the significance of Angband as a long-standing and influential roguelike game that has inspired numerous variants and spin-offs.