---
title: cmd-cave.c File Documentation
id: cmdcavec-file-documentation
section: development
category: guides
created: '2025-03-14'
updated: '2025-03-13'
version: 0.1.0
---


# cmd-cave.c File Documentation

## 1. File Overview
`cmd-cave.c` is a critical file in the Angband roguelike codebase that implements many of the game's core dungeon exploration mechanics. This includes handling player actions such as moving between dungeon levels, opening and closing doors, disarming traps, tunneling through walls, resting to recover HP/mana, and more.

The file defines command functions for each of these actions that are called by the game's command handling system. It also contains various helper functions for testing the viability of actions and applying their effects to the game state.

## 2. Data Structures

### struct command
The `command` struct represents a game command with the following fields:
- `code`: The command code identifying the action 
- `arg`: Optional argument data passed to the command
- `repeat`: Number of times to repeat the command
- `energy`: Energy cost of the command

## 3. Global Variables
- `ddgrid`: Array of grid deltas representing the 8 cardinal and diagonal directions on the map

## 4. Functions

### do_cmd_go_up
```c
void do_cmd_go_up(struct command *cmd)
```
Attempts to make the player go up a dungeon level via stairs.

Parameters:
- `cmd`: The command being executed (unused) 

Mechanics:
- Checks for stairs in the player's current location
- Determines the destination level based on dungeon connectivity
- Takes an energy turn and saves the level for returning
- Updates player location and dungeon level

### do_cmd_go_down
```c
void do_cmd_go_down(struct command *cmd)  
```
Attempts to make the player go down a dungeon level via stairs.

Parameters:
- `cmd`: The command being executed (unused)

Mechanics:  
- Checks for stairs in the player's current location
- Determines the destination level based on dungeon connectivity 
- Takes an energy turn and saves the level for returning
- Updates player location and dungeon level
- Special handling for quest levels and forcing descent

### do_cmd_open
```c
void do_cmd_open(struct command *cmd)
```
Attempts to open a closed door or chest.

Parameters:
- `cmd`: The command being executed, contains a direction argument

Mechanics:
- Gets a direction from the player or automatically finds an adjacent door/chest
- Determines if it's a door or chest and calls the appropriate helper function:
  - `do_cmd_open_aux` for doors
  - `do_cmd_open_chest` for chests
- Handles "unlocking" of locked doors based on player skill
- Consumes energy on success
  
### do_cmd_close
```c
void do_cmd_close(struct command *cmd)
```  
Attempts to close an open door.

Parameters:
- `cmd`: The command being executed, contains a direction argument

Mechanics:
- Gets a direction from the player or automatically finds an adjacent door
- Calls `do_cmd_close_aux` to actually close the door
- Consumes energy on success

### do_cmd_tunnel
```c 
void do_cmd_tunnel(struct command *cmd)
```
Attempts to tunnel through obstructing walls/rubble.

Parameters: 
- `cmd`: The command being executed, contains a direction argument

Mechanics:
- Gets a direction from the player
- Calls `do_cmd_tunnel_aux` to actually dig through the wall
- Takes an energy turn and determines success based on player digging ability
- May "discover" hidden treasure veins

### move_player
```c
void move_player(int dir, bool disarm)
```
Actually moves the player in the given direction, handling various terrain.

Parameters:
- `dir`: The direction to move
- `disarm`: Whether to try disarming traps

Mechanics:
- Determines the destination grid based on direction
- Attacks any monsters present
- Handles attempting to open closed doors
- Handles attempting to disarm traps
- Refuses to move into walls and other blocking terrain
- Actually moves the player and updates FOV/LOS
- Stops running if entering a trap detected area

### do_cmd_rest
```c
void do_cmd_rest(struct command *cmd)
```
Makes the player rest for a specified number of turns (or until interrupted).

Parameters:
- `cmd`: The command being executed, contains a numeric "choice" argument for number of turns to rest

Mechanics:
- Determines the number of turns to rest from the argument
- Starts resting and handles updating the game state each turn
- Stops when the requested number of turns has elapsed or HP/mana is fully restored
- Handles interruptions by canceling the resting state

### do_cmd_alter
```c
void do_cmd_alter(struct command *cmd)
```
Alters the terrain in the specified direction (open, tunnel, close, disarm).

Parameters:
- `cmd`: The command being executed, contains a direction argument

Mechanics:
- Gets a direction from the player
- Looks up the grid in that direction and chooses an action based on the terrain:
  - Attack any monster present
  - Tunnel through walls/rubble
  - Open closed doors
  - Disarm traps
  - Close open doors
- Calls the appropriate `do_cmd_*` helper for the action
  
### do_cmd_feeling
```c
void do_cmd_feeling(void)
```
Displays the player's "feeling" about the level based on monster and object difficulty.

Mechanics:
- Determines a monster feeling and object feeling independently based on level threat levels
- Prints a text description of the combined feeling to the player
- Suppressed if the player has disabled the birth option to display feelings

## 5. Algorithms

### Dungeon Traversal
The `do_cmd_go_up` and `do_cmd_go_down` functions implement the core mechanic of traversing between dungeon levels. The algorithm:

1. Check the player is on a valid up or down staircase 
2. Determine the destination dungeon level depth by incrementing/decrementing the current depth
3. Save the previous level's state for later return
4. Move the player to the new level at the destination depth
5. Generate a new level at that depth if not already visited
6. Update the game state and redraw

This allows the dungeon to be dynamically generated as the player progresses, with visited levels saved.

### Digging Tunnels 
The `do_cmd_tunnel` command allows tunneling through walls and rubble. The algorithm:

1. Check the requested direction contains a diggable wall or rubble
2. Check if the player's digging ability meets the difficulty of the terrain
3. Consume energy and:  
   a. Permanently remove the wall/rubble on success
   b. Chip away at it on partial success
   c. Fail to affect it if the player is not strong enough
4. Check for hidden treasure veins exposed by the digging

This allows progressive tunneling through impassable terrain, with a degree of skill/strength vs difficulty.

## 6. Dependencies

`cmd-cave.c` depends on:
- `angband.h`: Core Angband header with essential type and constant definitions
- `cave.h`: Dungeon grid/level representation 
- `cmds.h`: Command definitions
- `game-event.h`: Game event type definitions
- `generate.h`: Dungeon generation
- `init.h`: Initialization routines
- `mon-attack.h`: Monster attacking 
- `mon-desc.h`: Monster description generation
- `mon-lore.h`, `mon-spell.h`, `mon-timed.h`, `mon-util.h`: Monster data and utilities
- `monster.h`: Monster type definitions
- `obj-chest.h`, `obj-desc.h`: Object and treasure chest handling
- `obj-gear.h`, `obj-ignore.h`, `obj-knowledge.h`, `obj-pile.h`, `obj-util.h`: Object utilities
- `player-attack.h`, `player-calcs.h`, `player-path.h`, `player-timed.h`, `player-util.h`: Player data and utilities
- `player-quest.h`: Quest handling
- `project.h`: Projectile and effect handling
- `store.h`: Store/shop definitions
- `trap.h`: Trap definitions

Files dependent on `cmd-cave.c`:
- `cmd-core.h`: Core command processing that calls these dungeon commands

## 7. Historical Context
`cmd-cave.c` contains code dating back to the earliest Angband versions in the 1990s. The core dungeon exploration mechanics implemented here were established by the Moria and Umoria codebases that Angband derived from. While modernized over the years, the fundamental algorithms remain similar.

Many roguelikes that branched off of Angband use a similar organization and share the concepts of manual actions for interacting with the dungeon terrain.

The code is part of Angband's long history and still bears some "cryptic" elements, such as the heavy use of global variables and extremely terse naming. Modern refactoring aims to improve the organization while retaining compatibility.