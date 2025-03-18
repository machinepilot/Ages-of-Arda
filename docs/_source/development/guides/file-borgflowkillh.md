---
title: 'File: borg-flow-kill.h'
id: file-borgflowkillh
section: development
category: guides
created: '2025-03-14'
updated: '2025-03-14'
version: 0.1.0
---


# File: borg-flow-kill.h

## File Overview
`borg-flow-kill.h` is a header file in the Angband codebase that contains declarations and definitions related to the Borg AI's monster tracking and combat flow systems. The Borg is an AI player that aims to optimally play the game. This file focuses on how the Borg tracks and engages with monsters in the dungeon.

## Data Structures

### `borg_kill`
The `borg_kill` struct represents information about a monster tracked by the Borg AI. It contains the following fields:

- `r_idx` (uint16_t): The race index of the monster.
- `known` (bool): Whether the race of the monster has been verified.
- `awake` (bool): Whether the monster is probably awake.
- `confused` (bool): Whether the monster is probably confused.
- `afraid` (bool): Whether the monster is probably afraid.
- `quiver` (bool): Whether the monster is probably quivering.
- `stunned` (bool): Whether the monster is stunned.
- `poisoned` (bool): Whether the monster is probably poisoned.
- `seen` (bool): Whether motion has been assigned to the monster.
- `used` (bool): Whether a message has been assigned to the monster.
- `pos` (struct loc): The location of the monster.
- `ox`, `oy` (uint8_t): The old location of the monster.
- `speed` (uint8_t): The estimated speed of the monster.
- `moves` (uint8_t): The estimated moves of the monster.
- `ranged_attack` (uint8_t): The quantity of ranged attacks the monster has.
- `spell` (uint8_t[RSF_MAX]): Spell flags for the monster's spells.
- `power` (int16_t): The estimated hit-points of the monster.
- `injury` (int16_t): The percentage the monster is wounded.
- `other` (int16_t): An estimated value for something unspecified.
- `level` (int16_t): The monster's level.
- `spell_flags` (uint32_t[RF_MAX]): Preloaded monster race spell flags.
- `when` (int16_t): When the monster was last seen.
- `m_idx` (int16_t): The game's index for the monster.

## Global Variables

- `borg_kills_cnt` (int16_t): The count of monsters in the `borg_kills` array.
- `borg_kills_summoner` (int16_t): The index of a summoning monster in the `borg_kills` array.
- `borg_kills_nxt` (int16_t): The next available index in the `borg_kills` array.
- `borg_kills` (borg_kill*): The array of monsters tracked by the Borg AI.
- `borg_race_count` (int16_t*): A count of racial appearances per dungeon level.
- `borg_race_death` (int16_t*): A count of racial kills (for unique monsters).
- Various global variables tracking the presence of specific monsters or monster types on the current level.

## Functions

### `borg_race_name`
```c
const char *borg_race_name(int i);
```
- Purpose: Get the name of a monster race.
- Parameters:
  - `i` (int): The index of the monster race.
- Return value: The name of the monster race as a string.

### `borg_delete_kill`
```c
void borg_delete_kill(int i);
```
- Purpose: Delete an old "kill" record from the `borg_kills` array.
- Parameters:
  - `i` (int): The index of the "kill" record to delete.
- Side effects: Removes the "kill" record at index `i` from the `borg_kills` array.

### `borg_sleep_kill`
```c
void borg_sleep_kill(int i);
```
- Purpose: Force sleep onto a "kill" record in the `borg_kills` array.
- Parameters:
  - `i` (int): The index of the "kill" record to force sleep onto.
- Side effects: Modifies the "kill" record at index `i` in the `borg_kills` array to indicate the monster is sleeping.

### `borg_follow_kill`
```c
void borg_follow_kill(int i);
```
- Purpose: Attempt to "follow" a missing monster.
- Parameters:
  - `i` (int): The index of the "kill" record to follow.
- Side effects: Updates the "kill" record at index `i` in the `borg_kills` array based on the monster's movement.

### `observe_kill_diff`
```c
bool observe_kill_diff(int y, int x, uint8_t a, wchar_t c);
```
- Purpose: Attempt to notice a changing "kill" record.
- Parameters:
  - `y`, `x` (int): The coordinates of the monster.
  - `a` (uint8_t): The monster's attribute.
  - `c` (wchar_t): The monster's character representation.
- Return value: True if a change was noticed, false otherwise.
- Side effects: Updates the corresponding "kill" record in the `borg_kills` array if a change is noticed.

### `observe_kill_move`
```c
bool observe_kill_move(int y, int x, int d, uint8_t a, wchar_t c, bool flag);
```
- Purpose: Attempt to notice if a "kill" record moved.
- Parameters:
  - `y`, `x` (int): The coordinates of the monster.
  - `d` (int): The direction of movement.
  - `a` (uint8_t): The monster's attribute.
  - `c` (wchar_t): The monster's character representation.
  - `flag` (bool): A flag indicating something unspecified.
- Return value: True if movement was noticed, false otherwise.
- Side effects: Updates the corresponding "kill" record in the `borg_kills` array if movement is noticed.

### `borg_locate_kill`
```c
int borg_locate_kill(char *who, struct loc c, int r);
```
- Purpose: Attempt to locate a monster which could explain a message.
- Parameters:
  - `who` (char*): The name of the monster to locate.
  - `c` (struct loc): The coordinates to search around.
  - `r` (int): The radius to search within.
- Return value: The index of the located "kill" record in the `borg_kills` array, or -1 if not found.

### `borg_count_death`
```c
void borg_count_death(int i);
```
- Purpose: Notice the "death" of a monster.
- Parameters:
  - `i` (int): The index of the "kill" record of the dead monster.
- Side effects: Updates the racial kill count for the monster and removes the "kill" record from the `borg_kills` array.

### `borg_flow_kill`
```c
bool borg_flow_kill(bool viewable, int nearness);
```
- Purpose: Prepare to "flow" towards monsters to "kill".
- Parameters:
  - `viewable` (bool): Whether to consider only viewable monsters.
  - `nearness` (int): The desired nearness to the monsters.
- Return value: True if the flow was prepared successfully, false otherwise.
- Side effects: Sets up the Borg AI's flow towards monsters for combat.

### `borg_flow_kill_aim`
```c
bool borg_flow_kill_aim(bool viewable);
```
- Purpose: Take a couple of steps to line up a shot at a monster.
- Parameters:
  - `viewable` (bool): Whether to consider only viewable monsters.
- Return value: True if the Borg AI successfully lined up a shot, false otherwise.
- Side effects: Moves the Borg AI to line up a shot at a monster.

### `borg_flow_kill_corridor`
```c
bool borg_flow_kill_corridor(bool viewable);
```
- Purpose: Dig an anti-summon corridor.
- Parameters:
  - `viewable` (bool): Whether to consider only viewable monsters.
- Return value: True if the corridor was dug successfully, false otherwise.
- Side effects: Digs a corridor to prevent monster summoning.

### `borg_flow_kill_direct`
```c
bool borg_flow_kill_direct(bool viewable, bool twitchy);
```
- Purpose: Dig a straight tunnel to a close monster.
- Parameters:
  - `viewable` (bool): Whether to consider only viewable monsters.
  - `twitchy` (bool): Whether to allow twitchy movement.
- Return value: True if the tunnel was dug successfully, false otherwise.
- Side effects: Digs a straight tunnel towards a close monster.

### `borg_near_monster_type`
```c
void borg_near_monster_type(int dist);
```
- Purpose: Check if a dangerous monster is nearby.
- Parameters:
  - `dist` (int): The distance to check for monsters.
- Side effects: Updates global variables indicating the presence of specific monster types within the given distance.

### `borg_shoot_scoot_safe`
```c
bool borg_shoot_scoot_safe(int emergency, int turns, int b_p);
```
- Purpose: Perform a bit of magic missile and phase to escape danger.
- Parameters:
  - `emergency` (int): The level of emergency.
  - `turns` (int): The number of turns to spend.
  - `b_p` (int): The power of the magic missiles.
- Return value: True if the Borg AI successfully escaped danger, false otherwise.
- Side effects: Makes the Borg AI use magic missiles and phasing to escape dangerous situations.

### `borg_create_kill`
```c
int borg_create_kill(char *who, struct loc c);
```
- Purpose: Create a "kill" record at the given location.
- Parameters:
  - `who` (char*): The name of the monster.
  - `c` (struct loc): The coordinates of the monster.
- Return value: The index of the created "kill" record in the `borg_kills` array.
- Side effects: Adds a new "kill" record to the `borg_kills` array.

### `borg_init_flow_kill`
```c
void borg_init_flow_kill(void);
```
- Purpose: Initialize the data structures and variables related to the Borg AI's monster tracking and combat flow systems.
- Side effects: Allocates memory for the `borg_kills` array and initializes related variables.

### `borg_free_flow_kill`
```c
void borg_free_flow_kill(void);
```
- Purpose: Free the memory allocated for the Borg AI's monster tracking and combat flow systems.
- Side effects: Deallocates the memory used by the `borg_kills` array.

## Algorithms

The functions in this file implement various algorithms and game mechanics related to the Borg AI's monster tracking and combat flow systems. Some key algorithms include:

- Updating and maintaining the `borg_kills` array based on monster movements and state changes.
- Preparing the Borg AI's flow towards monsters for combat.
- Lining up shots at monsters.
- Digging anti-summon corridors and straight tunnels towards monsters.
- Escaping dangerous situations using magic missiles and phasing.

## Dependencies

- This file depends on the following files:
  - `angband.h`: For basic Angband data types and constants.
  - `mon-spell.h`: For monster spell constants.
  - `borg-flow.h`: For general Borg AI flow functionality.

- Other files may depend on this file to access the Borg AI's monster tracking and combat flow functionality.

## Historical Context

The Borg AI was developed as an add-on to Angband to create an automated player that could optimally play the game. The monster tracking and combat flow systems implemented in this file are crucial components of the Borg AI's decision-making process. The code has evolved over time to improve the Borg AI's effectiveness and efficiency in dealing with monsters in the dungeon.