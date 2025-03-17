# Ages of Arda - Startup Guide

This document explains how to start the Ages of Arda game with the integrated MCP (Model Context Protocol) server for enhanced AI-driven narrative experiences.

## Quick Start

### Windows
1. Double-click `start-ages-of-arda.bat` to launch both the MCP server and the game.

### Linux/Unix
1. Make the startup script executable: `chmod +x start-ages-of-arda.sh`
2. Run the script: `./start-ages-of-arda.sh`

## Configuration

The startup scripts use a configuration file (`mcp_config.ini`) to control various aspects of the game and MCP server. If this file doesn't exist, a default one will be created automatically.

### MCP Server Configuration

The `[MCP_SERVER]` section in the configuration file controls the MCP server:

- `enabled`: Set to `true` to enable MCP server integration, `false` to disable it.
- `autostart`: When `true`, the MCP server will start automatically with the game.
- `server_path`: Path to the MCP server directory (relative to the game root).
- `port`: Port for the MCP server to listen on (default: 3000).
- `timeout`: Timeout in seconds for MCP server operations.
- `retry_attempts`: Number of retry attempts for MCP server operations.

### Window Preferences

The `[WINDOW_PREFERENCES]` section controls the game's display settings:

- `use_graphics`: Set to `true` to enable graphical tiles, `false` for ASCII mode.
- `graphics_mode`: Graphics mode to use (0-4, where 3 is recommended).
- `main_font_size`: Font size for the main window.
- `subwindow_font_size`: Font size for subwindows.
- `show_borders`: Enable or disable window borders.
- `inactive_alpha`: Alpha transparency for inactive windows (0-255).

### Gameplay Settings

The `[GAMEPLAY]` section controls various gameplay options:

- `show_flavors`: Show object flavors in inventory.
- `pickup_always`: Automatically pick up items.
- `confirm_close`: Confirm when closing windows with unsaved changes.
- `use_sound`: Enable sound effects.
- `sound_volume`: Volume level (0-100).

### Advanced Settings

The `[ADVANCED]` section contains advanced configuration options:

- `debug_mode`: Enable debug mode.
- `enable_logging`: Enable logging.
- `log_level`: Log level (1-5, where 1 is critical and 5 is debug).
- `autosave_freq`: Autosave frequency in turns.
- `max_save_files`: Maximum number of save files to keep.

## Dynamic Window Configuration

The game will automatically generate an optimized window configuration based on your screen resolution. This configuration is stored in `lib/user/sdl2init.txt` and includes:

- Main window dimensions and position
- Subwindow layouts optimized for your screen
- Font settings for each window
- Graphics settings

If you want to customize the window layout further, you can edit this file manually after it's been generated.

## Troubleshooting

### MCP Server Issues

If the MCP server fails to start:

1. Ensure Node.js is installed and in your PATH.
2. Check that the server path in the configuration file is correct.
3. Verify that port 3000 (or your configured port) is not in use by another application.
4. Check the server logs in the MCP server directory.

### Display Issues

If the game windows don't appear correctly:

1. Delete the `lib/user/sdl2init.txt` file to regenerate the window configuration.
2. Try different graphics modes in the configuration file.
3. Adjust font sizes if text appears too large or small.

## Advanced Usage

### Command Line Arguments

The startup scripts pass command line arguments to the game based on your configuration:

- Graphics mode: `-mgcu:X` where X is the graphics mode number
- Debug mode: `-d` enables debug features

You can modify the startup scripts to add additional command line arguments if needed.

### Custom MCP Server

If you want to use a custom MCP server:

1. Set `autostart=false` in the configuration file.
2. Start your custom MCP server manually.
3. Update the `port` setting to match your custom server's port.

## Contact and Support

For issues or questions about the startup process, please file an issue on the project's GitHub repository or contact the development team. 