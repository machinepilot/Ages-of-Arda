# File: borg-flow-glyph.h

## File Overview

`borg-flow-glyph.h` is a header file in the Angband roguelike game's codebase, specifically within the "borg" AI module. The borg is an automated player that can navigate the dungeon and make decisions based on game state.

This file contains declarations for data structures, global variables, and functions related to the borg's "flow" system for tracking and navigating special glyphs (symbols) in the dungeon. These glyphs likely represent important terrain features, objects, or other points of interest that the borg needs to be aware of to make decisions.

## Data Structures

The file declares one main data structure:

```c
extern struct borg_track track_glyph;
```

`borg_track` is likely a struct defined elsewhere that represents a generic tracking data structure used by the borg. The `track_glyph` instance specifically tracks glyphs in the dungeon.

## Global Variables

The file declares two global variables:

```c
extern bool borg_needs_new_sea;
```

`borg_needs_new_sea` is a boolean flag indicating whether the borg needs to recalculate or update its "sea" of glyphs. The "sea" likely refers to the overall map or representation of glyphs in the dungeon.

## Functions

The file declares four functions:

```c
extern bool borg_flow_glyph(int why);
```

`borg_flow_glyph` is likely the main function for updating the borg's glyph flow information. It takes an integer parameter `why`, which may indicate the reason for the update (e.g., dungeon change, borg state change). It returns a boolean value, possibly indicating the success or necessity of the update.

```c
extern void borg_init_flow_glyph(void);
```

`borg_init_flow_glyph` is an initialization function for the glyph flow system. It likely sets up initial data structures and state.

```c
extern void borg_free_flow_glyph(void);
```

`borg_free_flow_glyph` is a cleanup function for the glyph flow system. It likely frees any allocated memory and resets state.

## Algorithms

The specific algorithms used for glyph flow are not detailed in this header file. They are likely implemented in the corresponding `.c` file.

However, based on the naming and context, the glyph flow system probably involves some form of pathfinding or graph traversal algorithm to efficiently navigate between important glyphs in the dungeon. This could be used for the borg to plan routes, avoid obstacles, or seek out objectives.

## Dependencies

This file has the following direct dependencies:

- `angband.h`: The main Angband header file, included before the `ALLOW_BORG` conditional compilation directive.
- `borg-flow.h`: Another borg-related header file, likely containing definitions used by the glyph flow system.

Other files in the borg module likely depend on this file to use the glyph flow functionality.

## Historical Context

The copyright notice at the top of the file indicates that this code has been part of the Angband project since at least 1997, with contributions from several developers over the years.

The `ALLOW_BORG` conditional compilation directive suggests that the borg AI is an optional feature that can be excluded from builds if desired.

## Game Mechanics

The glyph flow system implemented in this file is part of the larger borg AI mechanics in Angband. The borg is essentially an autopilot that can control the player character and make decisions based on the current game state and its knowledge of the dungeon.

Tracking and navigating between important glyphs (which may represent things like doors, stairs, objects, traps, or special terrain) allows the borg to plan efficient routes and make informed decisions about where to go and what to interact with. This could involve pathfinding to navigate to a target glyph, or avoidance behaviors to steer clear of dangerous glyphs.

The `borg_needs_new_sea` variable suggests that the borg maintains an overall map or representation of the dungeon glyphs, which may need to be updated when the dungeon changes (e.g., through digging or other terrain modifications).

Overall, the glyph flow system contributes to the borg's ability to intelligently navigate the procedurally-generated dungeons of Angband and progress through the game in an automated fashion.