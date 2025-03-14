# borg-danger.h Documentation

## File Overview

`borg-danger.h` is a header file in the Angband codebase that contains declarations and definitions related to the Borg AI's danger assessment system. The Borg AI is an automated player that attempts to make optimal decisions based on the current game state. 

This file defines data structures and functions used by the Borg AI to evaluate the potential danger posed by monsters to the player character at specific grid locations in the dungeon. The danger assessment takes into account various factors such as the monster's abilities, potential damage output, and special effects.

## Data Structures

### `BORG_MONBLOW` Enumeration

The `BORG_MONBLOW` enumeration defines constants representing different types of monster blows or attacks. Each constant corresponds to a specific effect or damage type inflicted by a monster's blow. The enumeration includes:

- `MONBLOW_NONE`: No special effect.
- `MONBLOW_HURT`: Physical damage.
- `MONBLOW_POISON`: Poisoning effect.
- `MONBLOW_DISENCHANT`: Disenchantment of the player's equipment.
- `MONBLOW_DRAIN_CHARGES`: Draining charges from the player's magical devices.
- `MONBLOW_EAT_GOLD`: Consumption of the player's gold.
- `MONBLOW_EAT_ITEM`: Consumption of the player's items.
- `MONBLOW_EAT_FOOD`: Consumption of the player's food.
- `MONBLOW_EAT_LIGHT`: Consumption of the player's light source.
- `MONBLOW_ACID`: Acid damage.
- `MONBLOW_ELEC`: Electric damage.
- `MONBLOW_FIRE`: Fire damage.
- `MONBLOW_COLD`: Cold damage.
- `MONBLOW_BLIND`: Blinding effect.
- `MONBLOW_CONFUSE`: Confusion effect.
- `MONBLOW_TERRIFY`: Fear effect.
- `MONBLOW_PARALYZE`: Paralysis effect.
- `MONBLOW_LOSE_STR`: Loss of strength stat.
- `MONBLOW_LOSE_INT`: Loss of intelligence stat.
- `MONBLOW_LOSE_WIS`: Loss of wisdom stat.
- `MONBLOW_LOSE_DEX`: Loss of dexterity stat.
- `MONBLOW_LOSE_CON`: Loss of constitution stat.
- `MONBLOW_LOSE_ALL`: Loss of all stats.
- `MONBLOW_SHATTER`: Shattering of the player's equipment.
- `MONBLOW_EXP_10`: Experience drain by 10%.
- `MONBLOW_EXP_20`: Experience drain by 20%.
- `MONBLOW_EXP_40`: Experience drain by 40%.
- `MONBLOW_EXP_80`: Experience drain by 80%.
- `MONBLOW_HALLU`: Hallucination effect.
- `MONBLOW_BLACK_BREATH`: Black breath effect.
- `MONBLOW_UNDEFINED`: Undefined effect.

## Global Variables

- `borg_fear_region`: A 2D array of `uint16_t` values representing the extra fear induced in each dungeon region. The dungeon is divided into 11x11 regions, and each element in the array corresponds to a specific region.
- `borg_fear_monsters`: A 2D array of `uint16_t` values representing the extra fear induced by monsters in each grid of the dungeon. The array dimensions are `AUTO_MAX_Y + 1` and `AUTO_MAX_X + 1`, corresponding to the maximum dungeon dimensions.
- `borg_danger_wipe`: A boolean flag indicating whether the danger values need to be recalculated.

## Functions

### `borg_danger_one_kill`

```c
int borg_danger_one_kill(int y, int x, int c, int i, bool average, bool full_damage);
```

- Purpose: Calculate the danger posed by a single monster to a specific grid.
- Parameters:
  - `y`: The y-coordinate of the grid.
  - `x`: The x-coordinate of the grid.
  - `c`: The distance from the player to the grid.
  - `i`: The index of the monster.
  - `average`: A boolean flag indicating whether to use average damage or maximum damage.
  - `full_damage`: A boolean flag indicating whether to consider full damage or adjusted damage.
- Return Value: The calculated danger value.
- Side Effects: None.
- Relationships: Called by `borg_danger` to calculate the total danger of a grid.
- Game Mechanics: Evaluates the potential damage and effects of a monster's blows on the player character at the specified grid location. Takes into account factors such as the monster's abilities, distance, and damage output.

### `borg_danger`

```c
int borg_danger(int y, int x, int c, bool average, bool full_damage);
```

- Purpose: Calculate the total danger of a specific grid.
- Parameters:
  - `y`: The y-coordinate of the grid.
  - `x`: The x-coordinate of the grid.
  - `c`: The distance from the player to the grid.
  - `average`: A boolean flag indicating whether to use average damage or maximum damage.
  - `full_damage`: A boolean flag indicating whether to consider full damage or adjusted damage.
- Return Value: The calculated total danger value.
- Side Effects: None.
- Relationships: Calls `borg_danger_one_kill` for each monster to calculate the danger posed by individual monsters and sums up the values.
- Game Mechanics: Assesses the overall danger of a grid location by considering the combined danger posed by all monsters that can potentially affect the player character at that grid. The danger value is influenced by factors such as monster abilities, distance, and damage output.

## Algorithms

The danger assessment algorithms implemented in this file evaluate the potential threat posed by monsters to the player character at specific grid locations. The `borg_danger_one_kill` function calculates the danger of a single monster by considering its abilities, distance, and damage output. The `borg_danger` function aggregates the danger values of all monsters that can affect the player character at a given grid location to determine the total danger.

The algorithms take into account various factors such as the monster's blow effects (defined in the `BORG_MONBLOW` enumeration), the distance between the monster and the player, and the potential damage inflicted by the monster's attacks. The danger values are calculated based on these factors and can be influenced by flags such as `average` (to use average damage instead of maximum damage) and `full_damage` (to consider full damage or adjusted damage).

## Dependencies

- `angband.h`: The main Angband header file that includes fundamental game definitions and structures.
- `borg-cave.h`: Header file that defines data structures and functions related to the Borg AI's dungeon map representation.

Other files in the Borg AI subsystem may depend on `borg-danger.h` to access the danger assessment functions and data structures.

## Historical Context

The Borg AI was developed as an automated player for Angband, aiming to make optimal decisions based on the current game state. The danger assessment system implemented in `borg-danger.h` is a crucial component of the Borg AI, allowing it to evaluate the potential threats posed by monsters and make informed decisions accordingly.

The code in this file has evolved over time, with contributions from various developers, including Ben Harrison, James E. Wilson, Robert A. Koeneke, Andi Sidwell, Chris Carr, Ed Graham, and Erik Osheim.