# borg-fight-attack.h File Documentation

## File Overview

`borg-fight-attack.h` is a header file in the Angband roguelike game's codebase, specifically for the Borg AI system. The Borg is an AI player that attempts to play the game optimally. This file contains declarations and definitions related to the Borg's combat and attack decision-making process.

The file defines various constants, enumerations, and function prototypes that handle different types of attacks the Borg can perform, such as melee attacks, missile attacks, spells, prayers, wands, rods, staves, scrolls, activatable items, and more. The functions defined here are used to evaluate and select the most effective attack method in a given situation.

## Data Structures

### `enum` for Attack Types

The file defines a large enumeration of constants representing different attack types available to the Borg. These include:

- `BORG_ATTACK_MISSILE`: Missile attacks
- `BORG_ATTACK_ARROW`: Arrow attacks
- `BORG_ATTACK_MANA`: Mana-based attacks
- `BORG_ATTACK_METEOR`: Meteor attacks
- ... (many more attack types)

These constants are used to identify and select specific attack methods.

### `enum` for Attack Methods

Another enumeration is defined to represent various attack methods the Borg can use, such as:

- `BF_REST`: Resting
- `BF_THRUST`: Melee attacks
- `BF_OBJECT`: Using objects
- `BF_LAUNCH`: Launching missiles
- ... (many more attack methods)

Each constant corresponds to a specific function that evaluates and executes the attack.

## Global Variables

- `successful_target`: Indicates if the last attack successfully targeted a monster.
- `target_closest`: Indicates if the target is the closest monster.
- `borg_tp_other_n`: Count of special grids used for Teleport Other.
- `borg_tp_other_x`: Array of x-coordinates for Teleport Other grids.
- `borg_tp_other_y`: Array of y-coordinates for Teleport Other grids.
- `borg_tp_other_index`: Array of indices for Teleport Other grids.

## Functions

### `borg_mon_blow_effect`

```c
int borg_mon_blow_effect(const char *name);
```

- Purpose: Determines the effect of a blow from a monster.
- Parameters:
  - `name`: The name of the monster.
- Return value: The effect of the monster's blow.

### `borg_launch_bolt`

```c
int borg_launch_bolt(int rad, int dam, int typ, int max, int ammo_location);
```

- Purpose: Simulates or applies the optimal result of launching a beam/bolt/ball.
- Parameters:
  - `rad`: Radius of the attack.
  - `dam`: Damage of the attack.
  - `typ`: Type of the attack.
  - `max`: Maximum range of the attack.
  - `ammo_location`: Location of the ammunition.
- Return value: The effectiveness of the attack.

### `borg_attack_aux_launch`

```c
int borg_attack_aux_launch(void);
```

- Purpose: Simulates or applies the optimal result of launching a missile.
- Return value: The effectiveness of the missile attack.

### `borg_attack_aux_spell_bolt`

```c
int borg_attack_aux_spell_bolt(
    const enum borg_spells spell, int rad, int dam, int typ, int max_range, bool is_arc);
```

- Purpose: Simulates or applies the optimal result of using a "normal" attack spell.
- Parameters:
  - `spell`: The specific spell being used.
  - `rad`: Radius of the spell.
  - `dam`: Damage of the spell.
  - `typ`: Type of the spell.
  - `max_range`: Maximum range of the spell.
  - `is_arc`: Indicates if the spell is an arc.
- Return value: The effectiveness of the spell attack.

### `borg_calculate_attack_effectiveness`

```c
int borg_calculate_attack_effectiveness(int attack_type);
```

- Purpose: Simulates or applies the optimal result of using the given type of attack.
- Parameters:
  - `attack_type`: The type of attack to evaluate.
- Return value: The effectiveness of the attack.

### `borg_attack`

```c
bool borg_attack(bool boosted_bravery);
```

- Purpose: Attacks nearby monsters in the best possible way, if any.
- Parameters:
  - `boosted_bravery`: Indicates if the Borg's bravery is boosted.
- Return value: `true` if an attack was performed, `false` otherwise.
- Side effects: Performs the selected attack action.

## Dependencies

- Includes `"../angband.h"` for core Angband definitions.
- Depends on `"borg-magic.h"` for Borg's magic-related definitions.

## Historical Context

The file includes copyright notices dating back to 1997, indicating that this code has been part of the Angband project for a long time. The Borg AI system was a significant addition to the game, allowing players to observe and learn from an AI player's decisions.

The code has been maintained and updated by various contributors over the years, with the latest modifications in 2009 based on the copyright notices.