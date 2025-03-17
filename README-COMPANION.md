# Companion UI for Ages of Arda

This document describes the Companion UI feature added to Ages of Arda. The Companion UI provides a dedicated window that displays information about your current companion, their status, and their interactions with you during gameplay.

## Overview

The Companion UI window displays:
- Companion portrait
- Companion name and health status
- Relationship level with your character
- Recent dialogue and thoughts from your companion
- Status effects and conditions affecting your companion

## Setup Instructions

To enable and use the Companion UI:

1. Start the game with multiple terminal windows (e.g., `angband.exe -n2` to have Term-2 available)
2. Press `=` (equals) to access the options menu
3. Press `w` to access window display options
4. Navigate to Term-2 and make sure "Display companion information" is selected
5. Press Escape to exit the options menu

The Companion UI will now be visible in Term-2 and will update automatically as you play.

## Technical Implementation

The Companion UI is implemented using the following components:

- `ui-companion.c/h`: Core companion UI code
- `ui-display.c`: Window flag management and event handling
- `ui-init.c`: Default window flag initialization

The Companion UI uses the `PW_COMPANION` window flag (0x80000000) to determine which terminal should display companion information.

## Companion Interactions

The Companion UI responds to various game events:
- Monster deaths
- Entering/leaving dungeons or levels
- Inventory changes
- Combat situations

Your companion will offer dialogue, thoughts, and commentary based on these events. The relationship with your companion can evolve based on your actions in the game.

## Testing

A test script is provided to verify the Companion UI functionality:
```
test-companion-window.bat
```

This script will:
1. Reset your window configuration
2. Launch the game with Term-2 active
3. Guide you through setting up and testing the Companion UI

## Customization

Future updates may include:
- Customizable companion portraits
- Additional dialogue options
- Companion-specific quests
- Mood and relationship system improvements

## Troubleshooting

If the Companion UI is not visible:
1. Ensure you have selected "Display companion information" in the Term-2 window options
2. Check that Term-2 is visible on your screen
3. Try resetting your window configuration using `reset-window-config.bat`
4. Restart the game with multiple terminals using `angband.exe -n2`

If "Display companion information" is not showing up in the window options:
1. Make sure you're running the latest version of the game
2. Try using the test script `test-companion-window.bat` which ensures proper configuration
3. Delete your preferences file located at `%USERPROFILE%\Documents\Angband\user\windows.prf`
4. If the issue persists, try resetting your entire configuration using `reset-window-config.bat`
5. Alternatively, edit your `sdl2init.txt` file to manually add the companion window flag (0x80000000) to Term-2 