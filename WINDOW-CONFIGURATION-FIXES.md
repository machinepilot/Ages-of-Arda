# Ages of Arda - Window Configuration Fixes

## Overview

This document summarizes the changes made to fix window overlap issues and improve the fullscreen experience in Ages of Arda.

## Issues Fixed

1. **Overlapping Windows**: The original configuration had windows that overlapped, making it difficult to see content in multiple windows simultaneously.

2. **Fullscreen Mode**: The game window was not properly set to fullscreen mode.

## Solutions Implemented

### 1. Improved SDL2 Configuration Generator

The SDL2 configuration generator was updated with the following improvements:

- **Better Window Positioning**: Adjusted the position and size calculations for all windows to prevent overlap.
- **Fullscreen Mode**: Set the default mode to fullscreen.
- **Responsive Layout**: Improved the layout to better scale with different screen resolutions.
- **Window Proportions**: Adjusted the proportions of the game windows for better visibility.

### 2. Enhanced Configuration Management

Added configuration options and tools:

- **Fullscreen Toggle**: Added a configuration option to toggle between fullscreen and windowed mode.
- **Configuration Utility**: Created reset-window-config.bat and reset-window-config.sh utilities for users to:
  - Reset window configuration
  - Toggle fullscreen mode
  - Backup current configurations
  - Restore from backups

### 3. Updated Startup Scripts

Modified the startup scripts to better handle window configuration:

- **Force Regeneration**: Added a command-line option to force regeneration of the SDL2 configuration.
- **Fullscreen Setting**: Properly reads and applies the fullscreen setting from the configuration file.
- **Test Mode**: Added a test mode for script verification without launching the game.

## Technical Details

### Window Layout

The new window layout follows this arrangement:

```
┌─────────────┬────────────────────────────┬─────────────┐
│             │                            │             │
│             │                            │             │
│ Inventory   │                            │ Monsters    │
│ (Left)      │       Main Game            │ in Sight    │
│             │        Window              │ (Right Top) │
│             │                            │             │
│             │                            │             │
├─────────────┤                            ├─────────────┤
│             │                            │             │
│             │                            │ Inventory   │
│ Monster     │                            │ (Right Mid) │
│ Recall      │                            │             │
│ (Left Bot)  │                            │             │
│             │                            ├─────────────┤
│             │                            │             │
├─────────────┴────────────────────────────┤ Companion   │
│                                          │ (Right Bot) │
│           Message Window                 │             │
│                                          │             │
└──────────────────────────────────────────┴─────────────┘
```

### Configuration File Changes

Added a new `fullscreen` option to the `[WINDOW_PREFERENCES]` section:

```ini
[WINDOW_PREFERENCES]
use_graphics=true
graphics_mode=3
fullscreen=true  # New option
```

## User Instructions

### Resetting Window Configuration

If windows still overlap or display incorrectly:

1. Run `reset-window-config.bat` (Windows) or `reset-window-config.sh` (Linux/Unix)
2. Select option 1 to reset the window configuration
3. Start the game using `start-ages-of-arda.bat` or `start-ages-of-arda.sh`

### Toggling Fullscreen Mode

To switch between fullscreen and windowed mode:

1. Run `reset-window-config.bat` (Windows) or `reset-window-config.sh` (Linux/Unix)
2. Select option 2 to toggle fullscreen mode
3. Start the game using `start-ages-of-arda.bat` or `start-ages-of-arda.sh`

### Force Regenerating Configuration

To force regeneration of the SDL2 configuration:

```
start-ages-of-arda.bat force_config_regen
```

or 

```
./start-ages-of-arda.sh force_config_regen
```

## Future Improvements

Potential future improvements for window handling:

1. **In-Game Configuration**: Add the ability to configure windows from within the game.
2. **Layout Presets**: Create multiple layout presets for different play styles.
3. **Multi-Monitor Support**: Enhanced support for multi-monitor setups.
4. **Resolution Detection**: More robust screen resolution detection.
5. **Adaptive Fonts**: Automatically adjust font sizes based on resolution. 