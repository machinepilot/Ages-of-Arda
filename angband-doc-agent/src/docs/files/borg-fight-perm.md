# File: borg-fight-perm.h

## File Overview
`borg-fight-perm.h` is a header file in the Angband source code that relates to the Borg AI system, specifically the AI's handling of "permanent" spells during combat. The file is guarded by the `ALLOW_BORG` preprocessor directive, indicating that it is only compiled when the Borg AI is enabled.

## Data Structures
This header file does not define any data structures.

## Global Variables
This header file does not declare any global variables.

## Functions

### `borg_perma_spell`
```c
extern bool borg_perma_spell(void);
```
- **Purpose**: Determine if the Borg AI should cast a "permanent" spell in the current situation.
- **Parameters**: None
- **Return value**: 
  - `true` if the Borg AI decides to cast a permanent spell
  - `false` otherwise
- **Side effects**: None apparent from this declaration. The actual implementation may have side effects.
- **Relationships**: This function is likely called by other Borg AI routines responsible for making combat decisions.
- **Game mechanics**: In Angband, some spells have long-lasting or "permanent" effects that the Borg AI needs to consider using strategically. This function encapsulates the logic for deciding when to use such spells.

## Algorithms
The specific algorithm used by `borg_perma_spell` is not apparent from this header file. The implementation details would be found in the corresponding `.c` file.

## Dependencies
- `angband.h`: This header file is included before `borg-fight-perm.h` to ensure that necessary types and constants are defined.

No other files in the Angband codebase appear to depend on `borg-fight-perm.h` based on the information provided.

## Historical Context
The copyright notice at the top of the file indicates that this code has been part of Angband since at least 1997, with contributions from several developers over the years. The Borg AI was a significant addition to Angband and has been refined over time to improve the game's single-player experience.

The comment about including this file before `ALLOW_BORG` to avoid an empty compilation unit suggests that at some point, there may have been issues with the Borg-specific code being excluded entirely from the build in certain configurations.