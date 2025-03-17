# Ages of Arda - Simple MCP Setup

This document explains how to use the simplified MCP system with your Ages of Arda game.

## Quick Start (Two-Step Process)

### Step 1: Start the MCP Server
Run `start-mcp.bat` to:
- Check for Node.js
- Install required dependencies
- Start the MCP server

### Step 2: Start the Game
Run `start-game.bat` to:
- Launch the game with multi-window support
- You'll need to configure the companion window

## Configuring the Companion Window

Once in the game:
1. Press `=` to access options
2. Select `Window options` (press `w`)
3. For Term-2, enable "Display companion information"
4. Press ESC to save and return to the game

## Troubleshooting

### Node.js Not Found
If you receive a "Node.js not found" error:
1. Download and install Node.js from https://nodejs.org/
2. Make sure it's added to your PATH
3. Restart your computer
4. Try running the scripts again

### Port Already in Use
If port 3000 is already in use:
1. Close any applications that might be using it
2. Or manually edit the `.env` file in the `angband-doc-agent` folder to use a different port

### Game Not Finding the MCP Server
The game needs to be started with the `-n3` parameter to enable multiple windows. This is handled automatically by the `start-game.bat` script. 