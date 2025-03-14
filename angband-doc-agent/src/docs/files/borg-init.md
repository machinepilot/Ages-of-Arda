# borg-init.h Documentation

## File Overview

`borg-init.h` is a header file in the Angband codebase that contains declarations and definitions related to the initialization of the Borg, an AI player for the game. This file is part of the Borg module, which is an optional feature that can be enabled with the `ALLOW_BORG` macro.

The purpose of this file is to provide the necessary structures, variables, and function prototypes for initializing and managing the Borg's settings and resources. It also includes some utility functions for preparing race and class information and cleaning up allocated resources.

## Data Structures

### `borg_setting` struct

The `borg_setting` struct represents a single Borg setting. It contains the following fields:

- `setting_string`: A pointer to a constant character string that represents the name of the setting.
- `setting_type`: A character that indicates the type of the setting. It can be either 'b' for boolean or 'i' for integer.
- `default_value`: An integer that represents the default value of the setting.

## Global Variables

- `borg_init_failure`: A boolean variable that indicates whether the Borg initialization has failed.
- `borg_initialized`: A boolean variable that indicates whether the Borg has been initialized.
- `game_closed`: A boolean variable that indicates whether the game has been closed.
- `borg_settings`: An array of `borg_setting` structs that holds the Borg's settings.

## Functions

### `borg_init_txt_file`

```c
extern bool borg_init_txt_file(void);
```

- **Purpose**: Initializes the `borg.txt` file.
- **Parameters**: None.
- **Return value**: Returns `true` if a warning was given during the initialization, `false` otherwise.
- **Side effects**: None.
- **Relationships**: This function is called during the Borg initialization process.
- **Game mechanics**: Initializes the Borg's configuration file.

### `borg_reinit_options`

```c
extern void borg_reinit_options(void);
```

- **Purpose**: Resets the required options when returning from user control.
- **Parameters**: None.
- **Return value**: None.
- **Side effects**: Modifies the Borg's options.
- **Relationships**: This function is called when the user takes control of the game and then returns control to the Borg.
- **Game mechanics**: Resets the Borg's options to ensure a consistent state.

### `borg_prepare_race_class_info`

```c
extern void borg_prepare_race_class_info(void);
```

- **Purpose**: Prepares some information based on the player's race and class.
- **Parameters**: None.
- **Return value**: None.
- **Side effects**: Modifies the Borg's internal state based on the player's race and class.
- **Relationships**: This function is called during the Borg initialization process.
- **Game mechanics**: Prepares race and class-specific information for the Borg's decision-making process.

### `borg_init`

```c
extern void borg_init(void);
```

- **Purpose**: Initializes the Borg.
- **Parameters**: None.
- **Return value**: None.
- **Side effects**: Initializes the Borg's internal state and resources.
- **Relationships**: This function is called when the Borg is enabled.
- **Game mechanics**: Initializes the Borg AI player.

### `borg_free`

```c
extern void borg_free(void);
```

- **Purpose**: Cleans up resources allocated for the Borg.
- **Parameters**: None.
- **Return value**: None.
- **Side effects**: Frees memory and resources used by the Borg.
- **Relationships**: This function is called when the Borg is disabled or the game is closed.
- **Game mechanics**: Cleans up the Borg's resources to prevent memory leaks.

## Algorithms

This file does not contain any complex algorithms or game mechanics implementations. It primarily deals with initialization and resource management for the Borg AI player.

## Dependencies

- This file depends on the `angband.h` header file, which is included before the `ALLOW_BORG` macro check.
- Other files in the Borg module may depend on this file for the structures, variables, and function prototypes it provides.

## Historical Context

The Borg AI player has been a part of the Angband codebase for a long time. The code in this file has been contributed to and maintained by various developers over the years, as indicated by the copyright notices at the beginning of the file.