# Angband with MCP Server - Startup Guide

This document explains how to use the integrated startup system for Angband with the Model Context Protocol (MCP) server integration.

## Quick Start

### Windows
1. Double-click on `start-angband.bat` in your Angband installation directory
2. The script will automatically start both the MCP server and the Angband game

### Unix/Linux
1. Open a terminal in your Angband installation directory
2. Run `chmod +x start-angband.sh` to make the script executable (first time only)
3. Run `./start-angband.sh`
4. The script will automatically start both the MCP server and the Angband game

## Configuration

The startup system uses a configuration file (`mcp_config.ini`) to control various aspects of the game and MCP server. This file is automatically created on first run with default values, but you can modify it to customize your experience.

### Configuration File Location

The configuration file is located at:
- Windows: `[Angband Directory]\mcp_config.ini`
- Unix/Linux: `[Angband Directory]/mcp_config.ini`

### Configuration Sections

#### MCP_SERVER
Controls the Model Context Protocol server integration:

- `enabled`: Set to `true` to enable MCP server integration, `false` to disable
- `autostart`: When `true`, automatically starts the MCP server with the game
- `server_path`: Path to the MCP server directory (relative to game directory)
- `port`: Port number for the MCP server (default: 3000)
- `max_retry`: Maximum number of retry attempts if server fails to start
- `retry_delay`: Delay between retry attempts in milliseconds
- `timeout`: Timeout for server operations in milliseconds

#### WINDOW_PREFERENCES
Settings for game windows configuration:

- `main_window_width`: Width of the main game window
- `main_window_height`: Height of the main game window
- `font_size`: Font size for the main window
- `use_graphics`: Set to `true` to use graphical tiles, `false` for ASCII
- `graphics_mode`: Graphics mode: "old" or "new"

Subwindow configuration:
- `subwindows`: Number of subwindows to open
- `subwindowN_content`: Content for Nth subwindow: messages, recall, etc.
- `subwindowN_height`: Height of Nth subwindow

#### GAMEPLAY
General gameplay settings:

- `show_flavors`: Set to `true` to show object flavors
- `pickup_always`: Set to `true` to always pick up items
- `pickup_inven`: Set to `true` to pick up items if there's room in inventory

#### ADVANCED
Advanced settings:

- `debug_mode`: Set to `true` to enable debugging features
- `log_level`: Logging level: debug, info, warn, error
- `autosave`: Set to `true` to enable autosave
- `autosave_freq`: Frequency of autosave (in turns)
- `mcp_logging`: Set to `true` to log MCP server messages

## Requirements

For the MCP server integration to work properly:

1. **Node.js**: The MCP server requires Node.js to be installed on your system. Download it from [nodejs.org](https://nodejs.org/).

2. **Proper File Structure**: The startup scripts expect the MCP server files to be in the location specified by the `server_path` setting in the configuration file.

## Troubleshooting

### MCP Server Won't Start

1. Verify Node.js is installed by running `node --version` in a terminal/command prompt
2. Check the `mcp-server.log` file in your Angband directory for error messages
3. Make sure nothing else is using port 3000 (or whatever port you've configured)
4. Check that the `server_path` in `mcp_config.ini` points to the correct location

### Game Won't Start

1. Check that the Angband executable is properly installed and accessible
2. Look for any error messages in the console output
3. Try running Angband directly without the startup script to see if it works

## Advanced Usage

### Running MCP Server Separately

If you prefer to run the MCP server separately from the game:

1. Set `autostart=false` in the `[MCP_SERVER]` section of `mcp_config.ini`
2. Navigate to the MCP server directory
3. Run `node mcp-server.js`
4. Start Angband using the normal startup script

### Command Line Arguments

The startup scripts pass appropriate command line arguments to Angband based on your configuration. You can also add custom command line arguments by modifying the startup scripts.

Refer to the Angband documentation for a complete list of supported command line arguments. 