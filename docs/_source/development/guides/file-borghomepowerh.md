---
title: 'File: borg-home-power.h'
id: file-borghomepowerh
section: development
category: guides
created: '2025-03-14'
updated: '2025-03-14'
version: 0.1.0
---


# File: borg-home-power.h

## File Overview

`borg-home-power.h` is a header file in the Angband source code that declares a function for calculating the "power" of the player's home in the Borg (an AI player for Angband). The power of the home likely refers to a heuristic value representing the strength and resources available to the player in their home town.

This file is part of the Borg AI system and is only compiled when the `ALLOW_BORG` preprocessor directive is defined.

## Data Structures

This header file does not define any data structures.

## Global Variables

This header file does not declare any global variables.

## Functions

### `borg_power_home`

```c
extern int32_t borg_power_home(void);
```

- **Purpose**: Calculate the basic "power" of the player's home.
- **Parameters**: None
- **Return value**: An `int32_t` value representing the calculated power of the home.
- **Side effects**: None apparent from the function declaration.
- **Relationships to other functions**: This function is likely called by other Borg AI functions to assess the strength of the player's home and make decisions accordingly.
- **Game mechanics implemented**: The specifics of how the home power is calculated are not apparent from this header file. The implementation likely considers various factors such as the player's level, equipment, resources, and other game state to arrive at a numeric value representing the overall strength of the home.

## Algorithms

No algorithms are directly implemented in this header file. The complexity lies in the implementation of the `borg_power_home` function, which is not provided here.

## Dependencies

This header file depends on the following files:

- `angband.h`: The main Angband header file, which must be included before this file.

No other files in the Angband codebase directly depend on this header file, as it is specific to the Borg AI system.

## Historical Context

The Borg AI was developed as an automated player for Angband to help test and balance the game. It has a long history within the Angband community, with various developers contributing to its improvement over the years.

The presence of the `ALLOW_BORG` preprocessor directive suggests that the Borg AI can be optionally compiled into the game, allowing the developers to easily enable or disable it as needed.

The copyright notice at the top of the file acknowledges the contributions of several individuals to the Borg AI codebase, including Ben Harrison, James E. Wilson, Robert A. Koeneke, Andi Sidwell, Chris Carr, Ed Graham, and Erik Osheim, spanning from 1997 to 2009.