---
title: Ages of Arda - MCP System
id: ages-of-arda-mcp-system
section: development
category: guides
created: '2025-03-17'
updated: '2025-03-18'
version: 0.1.0
---


original location: C:\working_directory\ages-project\clean-ages-of-arda\README-MCP.md
# Ages of Arda - MCP System

This document explains how to use the Model Context Protocol (MCP) system with Ages of Arda.

## Quick Start

### Option 1: All-in-One Launcher
Run `scripts/start.bat` to:
- Check for Node.js installation
- Find an available port for the MCP server
- Start the MCP server in the background
- Launch the game with companion support

### Option 2: Individual Scripts
1. Start the MCP server: `scripts/mcp-server.bat`
2. Start the game: `scripts/game.bat`

### Option 3: Reset and Utilities
- Reset window configurations: `scripts/reset-windows.bat`
- Kill running MCP server processes: `scripts/kill-mcp.bat`

## Troubleshooting

### Port Already in Use
If you see an "EADDRINUSE" error:
1. Run `scripts/kill-mcp.bat` to terminate any running MCP server processes
2. Try starting the server again

### Game Executable Not Found
If the game launcher cannot find `angband.exe`:
1. Make sure you're running the scripts from the main game directory
2. The game executable should be in one of these locations:
   - Main directory: `./angband.exe`
   - Source directory: `./src/angband.exe`
   - Binary directory: `./bin/angband.exe`

### Companion Window Not Showing
1. Run `scripts/reset-windows.bat` to clear window configurations
2. Start the game again and reconfigure windows

## Technical Details

The MCP system uses a Node.js server to provide AI-driven companion responses in the game. When the MCP server is not running, the game will fall back to template-based responses.

The server listens on port 3000 by default but will automatically find an alternative port (3001-3010) if the default is unavailable.

## Script Descriptions

- `scripts/start.bat` - Main launcher that starts both the MCP server and game
- `scripts/mcp-server.bat` - Starts only the MCP server with port availability checking
- `scripts/game.bat` - Starts only the game with executable location detection
- `scripts/reset-windows.bat` - Resets window configurations for a fresh setup
- `scripts/kill-mcp.bat` - Terminates any running MCP server processes

## System Architecture

The MCP system consists of:

1. **MCP Server**: A Node.js server that handles narrative generation requests
2. **MCP Client**: C code integrated into the game that communicates with the server
3. **Companion UI**: A game window that displays companion information and dialogue

## Technical Details

### MCP Server

The server provides several endpoints:

- `/mcp/tools/generateNarrative`: Generates narrative text for game events
- `/mcp/tools/queryMemory`: Retrieves stored memories for a character
- `/health`: Health check endpoint

The server uses template-based narrative generation when running in offline mode.

### MCP Client

The C client (`mcp-client.c`) provides functions for:

- Connecting to the MCP server
- Sending narrative generation requests
- Processing responses asynchronously
- Fallback to template-based responses when the server is unavailable

### Companion UI

The companion UI is implemented in the game's SDL2 interface and displays:

- Companion portrait
- Dialogue and narrative text
- Relationship status
- Interaction options

## Troubleshooting

### MCP Server Won't Start

1. Ensure Node.js is installed (v14+ recommended)
2. Check that all dependencies are installed (`npm install` in the `angband-doc-agent` directory)
3. Verify the `.env` file has the correct `ANGBAND_SOURCE_PATH`
4. Try running `start-mcp-standalone.bat` to see any error messages

### Companion Window Not Showing

1. Ensure you've enabled "Display companion information" for Term-2
2. Check that the game was started with `-n3` parameter
3. Verify the MCP server is running

### No AI-Generated Responses

1. The system falls back to template-based responses when the AI server is unavailable
2. This is normal behavior and allows the game to function offline

## Advanced Configuration

### Environment Variables

- `ANGBAND_SOURCE_PATH`: Path to the game source code
- `PORT`: Port for the MCP server (default: 3000)

### Custom Templates

You can add custom narrative templates by editing the `generateTemplateNarrative` function in `simple-mcp-server.js`.

## Development

To extend the MCP system:

1. Add new event types in the client code
2. Add corresponding templates in the server
3. Update the companion UI to display the new content

## License

This MCP system is part of the Ages of Arda project and is subject to the same license terms. 