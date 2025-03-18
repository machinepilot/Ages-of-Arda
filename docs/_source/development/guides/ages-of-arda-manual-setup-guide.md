---
title: Ages of Arda - Manual Setup Guide
id: ages-of-arda-manual-setup-guide
section: development
category: guides
created: '2025-03-17'
updated: '2025-03-18'
version: 0.1.0
---


original location: C:\working_directory\ages-project\clean-ages-of-arda\manual-setup.md
# Ages of Arda - Manual Setup Guide

This guide provides step-by-step instructions for starting the Ages of Arda game with companion support.

## Requirements

- Node.js installed and in your PATH
- Game files properly installed

## Starting the MCP Server

The MCP (Model Context Protocol) server enables AI features like the companion dialogue.

### Option 1: Using the batch file (recommended)

1. Run `start-mcp-server.bat` from the main game directory
2. Leave the command window open while playing

### Option 2: Manual startup

1. Open a command prompt
2. Navigate to the MCP server directory:
   ```
   cd angband-doc-agent\src
   ```
3. Start the server:
   ```
   node mcp-server.js
   ```
4. Leave this window open while playing

## Starting the Game

### Option 1: Using the batch file (recommended)

1. Run `start-game.bat` from the main game directory

### Option 2: Manual startup

1. Open a command prompt
2. Navigate to the game directory
3. Start the game with multiple terminal support:
   ```
   angband.exe -n3
   ```

## Configuring the Companion Window

1. In the game, press the `=` (equals) key to access options
2. Press `w` to access window display options
3. Navigate to Term-2 and make sure "Display companion information" is selected
4. Press Escape to save settings and exit the options menu

## Troubleshooting

If "Display companion information" doesn't appear in the window options:

1. Delete your preferences file:
   ```
   %USERPROFILE%\Documents\Angband\user\windows.prf
   ```
2. Restart the game

If the MCP server fails to start:

1. Make sure Node.js is installed
2. Check that you're in the correct directory
3. Verify that `mcp-server.js` exists

## Manual Play Without MCP

If you can't or don't want to use the MCP server, the game will still work with templated companion responses instead of AI-generated ones. 