# File: borg-io.h

## File Overview
`borg-io.h` is a header file in the Angband codebase that provides input/output functionality for the Borg AI player. The Borg is an automated player that can play Angband on its own, making decisions based on game state and heuristics.

This file defines functions for interacting with the game's user interface, such as querying screen contents, simulating keypresses, and handling messages. It also provides functions for managing the Borg's input queue and keypress history.

## Data Structures

### `struct keypress`
This struct is not defined in this file, but is used as a parameter type for the `save_keypress_history` function. It likely represents a single keypress event, but its fields are not visible in this context.

## Global Variables

### `borg_confirm_target`
- Type: `bool`
- Purpose: Indicates whether the Borg should confirm its selected target before attacking.

## Functions

### `borg_what_text`
- Purpose: Query the attribute and characters at a given location on the screen.
- Parameters:
  - `x`, `y`: The coordinates of the screen location to query.
  - `n`: The maximum number of characters to retrieve.
  - `a`: A pointer to a `uint8_t` array to store the attribute of each character.
  - `s`: A pointer to a `char` array to store the characters.
- Return value: An `errr` code indicating the status of the operation.
- Side effects: Modifies the contents of the `a` and `s` arrays.

### `borg_note`
- Purpose: Memorize, log, search, and display a message in pieces.
- Parameters:
  - `what`: The message to process.
- Return value: None.
- Side effects: Modifies the Borg's internal state and may display output to the user.

### `borg_warning`
- Purpose: Memorize, log, search, and display a warning message in pieces.
- Parameters:
  - `what`: The warning message to process.
- Return value: None.
- Side effects: Modifies the Borg's internal state and may display output to the user.

### `borg_keypress`
- Purpose: Add a keypress to the Borg's input queue.
- Parameters:
  - `k`: The keycode to add to the queue.
- Return value: An `errr` code indicating the status of the operation.
- Side effects: Modifies the Borg's input queue.

### `borg_keypresses`
- Purpose: Add a string of keypresses to the Borg's input queue.
- Parameters:
  - `str`: The string of keypresses to add to the queue.
- Return value: An `errr` code indicating the status of the operation.
- Side effects: Modifies the Borg's input queue.

### `save_keypress_history`
- Purpose: Add a keypress to the Borg's keypress history.
- Parameters:
  - `k`: A pointer to the `keypress` struct to add to the history.
- Return value: None.
- Side effects: Modifies the Borg's keypress history.

### `borg_dump_recent_keys`
- Purpose: Dump the Borg's recent keypress history.
- Parameters:
  - `num`: The number of recent keypresses to dump.
- Return value: None.
- Side effects: Displays output to the user.

### `borg_inkey`
- Purpose: Get the next keypress from the Borg's input queue.
- Parameters:
  - `take`: Whether to remove the keypress from the queue.
- Return value: The keycode of the next keypress.
- Side effects: May modify the Borg's input queue if `take` is true.

### `borg_flush`
- Purpose: Clear all keypresses from the Borg's input queue.
- Parameters: None.
- Return value: None.
- Side effects: Modifies the Borg's input queue.

### `borg_queue_direction`
- Purpose: Save a directional keypress for later retrieval.
- Parameters:
  - `k`: The keycode of the directional keypress.
- Return value: None.
- Side effects: Modifies the Borg's saved directional keypress.

### `borg_get_queued_direction`
- Purpose: Retrieve the previously saved directional keypress.
- Parameters: None.
- Return value: The keycode of the saved directional keypress.
- Side effects: None.

### `borg_massage_special_chars`
- Purpose: Handle special characters (� and �) in names.
- Parameters:
  - `name`: The name string to process.
- Return value: A pointer to the processed name string.
- Side effects: May modify the contents of the `name` string.

### `borg_init_io`
- Purpose: Initialize the Borg's input/output functionality.
- Parameters: None.
- Return value: None.
- Side effects: Initializes the Borg's internal I/O state.

### `borg_free_io`
- Purpose: Clean up the Borg's input/output functionality.
- Parameters: None.
- Return value: None.
- Side effects: Frees any resources used by the Borg's I/O system.

## Algorithms
This file does not implement any complex algorithms directly, but provides an interface for the Borg AI to interact with the game's input/output systems.

## Dependencies
- `angband.h`: The main Angband header file, which must be included before `borg-io.h`.
- `ui-event.h`: Defines the `keycode_t` type used for representing keypresses.

This file is likely used by other Borg-related source files to handle input and output.

## Historical Context
The code in this file is based on work by several contributors over the years, as indicated by the copyright notice at the top of the file. The Borg AI player has been a part of Angband since at least 1997, with continuous improvements and updates by the community.

The presence of special handling for the `�` and `�` characters suggests that this code may have been written before Unicode support was common, as these characters often appeared in place of proper accented letters in older character encodings.