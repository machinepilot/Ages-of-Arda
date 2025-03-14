# Borg Item Activation Header File Documentation

## File Overview
The `borg-item-activation.h` file is part of the Borg AI system in the Angband roguelike game. It contains declarations for variables representing various item activation effects and a function to initialize them. These activations are used by the Borg AI to make decisions about using items during gameplay.

## Data Structures
This header file does not define any structs or typedefs.

## Global Variables
The file declares numerous global variables, each representing a specific item activation effect. These variables are of type `int` and are intended to store the index or identifier of the corresponding activation effect within the game's activation system.

Some examples of the activation effect variables include:
- `act_dragon_power`, `act_dragon_shining`, `act_dragon_balance`, etc.: Activations related to dragon-themed items.
- `act_ring_lightning`, `act_ring_ice`, `act_ring_flames`, `act_ring_acid`: Activations for rings with elemental powers.
- `act_staff_holy`, `act_staff_magi`: Activations for holy and magic staves.
- `act_heal1`, `act_heal2`, `act_heal3`: Activations for healing effects of varying potency.
- `act_cure_confusion`, `act_cure_paranoia`, `act_cure_mind`, `act_cure_body`: Activations for curing various status ailments.

The full list of activation variables covers a wide range of effects, including offensive spells, defensive buffs, restorative actions, and utility functions.

## Functions

### `borg_findact`
```c
extern int borg_findact(const char *act_name);
```
- **Purpose**: Finds the index of an activation effect based on its name.
- **Parameters**:
  - `act_name`: A string representing the name of the activation effect to find.
- **Return value**: The index of the activation effect if found, or some default value if not found.
- **Side effects**: None.
- **Relationships**: This function likely interacts with the game's activation system to map activation names to their corresponding indices.

### `borg_init_item_activation`
```c
extern void borg_init_item_activation(void);
```
- **Purpose**: Initializes the item activation variables used by the Borg AI.
- **Parameters**: None.
- **Return value**: None.
- **Side effects**: Modifies the global activation variables declared in this file, setting them to their appropriate values based on the game's activation system.
- **Relationships**: This function is likely called during the initialization phase of the Borg AI to set up the activation variables for use in decision-making.

## Algorithms
This header file does not implement any complex algorithms. It mainly serves to declare variables and functions related to item activations for the Borg AI.

## Dependencies
- This file depends on the main Angband header file `angband.h` for basic type definitions and game-related declarations.
- The contents of this file are conditionally compiled based on the presence of the `ALLOW_BORG` macro, which enables the Borg AI functionality.

## Historical Context
The Borg AI is a unique feature of Angband that allows the game to play itself by making decisions based on pre-defined rules and heuristics. The item activation system is an essential part of the Borg AI's decision-making process, as it allows the AI to evaluate and use various items to overcome challenges and progress through the dungeon.

The presence of numerous activation variables in this file suggests that the Borg AI has been designed to handle a wide variety of item effects, reflecting the diverse range of items available in Angband. The inclusion of dragon-themed activations, elemental rings, and various utility effects demonstrates the depth and complexity of the game's item system.

The use of global variables for activation indices, rather than enums or constants, may be a historical design choice or a requirement of the Borg AI's integration with the game's codebase.

Overall, this header file plays a crucial role in enabling the Borg AI to make informed decisions about item usage based on the available activation effects, enhancing the AI's capability to autonomously navigate the complex world of Angband.