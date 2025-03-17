@echo off
echo ===================================================
echo Ages of Arda - Enhanced MCP System Setup
echo ===================================================

REM Set the current directory as the base directory
set "BASE_DIR=%CD%"

REM Check if scripts directory exists, create if not
if not exist "scripts" (
    echo Creating scripts directory...
    mkdir scripts
)

REM Check if Node.js is installed
where node >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Node.js is not installed or not in PATH.
    echo Please install Node.js from https://nodejs.org/
    echo After installing Node.js, run this script again.
    pause
    exit /b 1
)

echo Node.js is installed. Checking version...
node --version

REM Check if the angband-doc-agent directory exists, create if not
if not exist "angband-doc-agent" (
    echo angband-doc-agent directory not found. Creating it now...
    mkdir "angband-doc-agent"
)

echo Making sure angband-doc-agent structure is correct...

REM Create src directory if it doesn't exist
if not exist "angband-doc-agent\src" (
    echo Creating src directory...
    mkdir "angband-doc-agent\src"
)

REM Create memories directory if it doesn't exist
if not exist "angband-doc-agent\memories" (
    echo Creating memories directory...
    mkdir "angband-doc-agent\memories"
)

REM Create or update package.json
echo Creating/updating package.json...
(
    echo {
    echo   "name": "angband-doc-agent",
    echo   "version": "1.0.0",
    echo   "description": "MCP server for Ages of Arda",
    echo   "main": "src/enhanced-mcp-server.js",
    echo   "scripts": {
    echo     "start": "node src/enhanced-mcp-server.js"
    echo   },
    echo   "dependencies": {
    echo     "express": "^4.18.2",
    echo     "dotenv": "^16.0.3"
    echo   }
    echo }
) > "angband-doc-agent\package.json"

REM Create or update .env file
echo Creating/updating .env file...
(
    echo PORT=3000
    echo SOURCE_PATH=%BASE_DIR%\src
    echo MEMORY_PATH=%BASE_DIR%\angband-doc-agent\memories
) > "angband-doc-agent\src\.env"
(
    echo PORT=3000
    echo SOURCE_PATH=%BASE_DIR%\src
    echo MEMORY_PATH=%BASE_DIR%\angband-doc-agent\memories
) > "angband-doc-agent\.env"

echo Installing dependencies...
cd "angband-doc-agent"
call npm install express dotenv

if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Failed to install dependencies.
    cd "%BASE_DIR%"
    pause
    exit /b 1
)

cd "%BASE_DIR%"

echo ===================================================
echo Testing for game executable...
echo ===================================================

REM Find the game executable
set FOUND_GAME=0
set GAME_PATH=

REM Check common locations
if exist "%BASE_DIR%\angband.exe" (
    set FOUND_GAME=1
    set GAME_PATH=%BASE_DIR%\angband.exe
    echo Found game at: %GAME_PATH%
) else if exist "%BASE_DIR%\src\angband.exe" (
    set FOUND_GAME=1
    set GAME_PATH=%BASE_DIR%\src\angband.exe
    echo Found game at: %GAME_PATH%
) else if exist "%BASE_DIR%\bin\angband.exe" (
    set FOUND_GAME=1
    set GAME_PATH=%BASE_DIR%\bin\angband.exe
    echo Found game at: %GAME_PATH%
)

if %FOUND_GAME%==0 (
    echo WARNING: Could not find angband.exe
    echo You will need to specify the game path manually when running the game.
)

REM Make sure enhanced-mcp-server.js exists
echo Creating enhanced MCP server script...
(
    echo /**
    echo  * Enhanced MCP Server for Ages of Arda
    echo  * 
    echo  * This server implements a simplified Model Context Protocol (MCP) for the Ages of Arda,
    echo  * providing narrative generation and companion responses with fallback to template-based responses.
    echo  */
    echo 
    echo const express = require('express');
    echo const fs = require('fs');
    echo const path = require('path');
    echo require('dotenv').config({ path: path.join(__dirname, '..', '.env') });
    echo 
    echo // Initialize the server
    echo const app = express();
    echo app.use(express.json());
    echo 
    echo // Configuration
    echo const config = {
    echo     port: process.env.PORT || 3000,
    echo     sourcePath: process.env.SOURCE_PATH || '../src',
    echo     memoryPath: process.env.MEMORY_PATH || './memories',
    echo     styles: {
    echo         fantasy: "Epic fantasy with vivid imagery in the style of Tolkien",
    echo         heroic: "Bold and dramatic, emphasizing courage and legendary deeds",
    echo         mysterious: "Enigmatic and intriguing, focusing on the unknown",
    echo         folksy: "Warm and conversational, as if shared around a campfire"
    echo     }
    echo };
    echo 
    echo // Ensure memory directory exists
    echo if (!fs.existsSync(config.memoryPath)) {
    echo     fs.mkdirSync(config.memoryPath, { recursive: true });
    echo }
    echo 
    echo // Memory storage for character interactions
    echo const characterMemories = {};
    echo 
    echo // Log requests for debugging
    echo app.use((req, res, next) => {
    echo     console.log(`${new Date().toISOString()} - ${req.method} ${req.url}`);
    echo     next();
    echo });
    echo 
    echo // Health check endpoint
    echo app.get('/health', (req, res) => {
    echo     res.json({ 
    echo         status: 'ok', 
    echo         provider: 'template',
    echo         uptime: process.uptime().toFixed(2) + 's'
    echo     });
    echo });
    echo 
    echo // Companion response endpoint
    echo app.post('/companion/response', (req, res) => {
    echo     try {
    echo         const { context, query } = req.body;
    echo         
    echo         console.log('Received companion query:', query);
    echo         if (context) {
    echo             console.log('Context:', typeof context === 'string' ? context.substring(0, 100) + '...' : JSON.stringify(context).substring(0, 100) + '...');
    echo         }
    echo         
    echo         // Extract character ID from context if available
    echo         const characterId = context?.character_id || 'unknown';
    echo         
    echo         // Store the query in memory
    echo         storeInteraction(characterId, 'query', query);
    echo         
    echo         // Generate response based on the query
    echo         const response = generateCompanionResponse(characterId, query, context);
    echo         
    echo         // Store the response in memory
    echo         storeInteraction(characterId, 'response', response);
    echo         
    echo         res.json({ response });
    echo         
    echo     } catch (error) {
    echo         console.error('Error processing companion response:', error);
    echo         res.status(500).json({ 
    echo             error: 'Failed to process companion response',
    echo             response: "I apologize, but I seem to be at a loss for words at the moment."
    echo         });
    echo     }
    echo });
    echo 
    echo /**
    echo  * Generate a companion response based on templates and context
    echo  */
    echo function generateCompanionResponse(characterId, query, context) {
    echo     // Convert query to lowercase for easier matching
    echo     const q = query.toLowerCase();
    echo     
    echo     // Get previous interactions
    echo     const previousInteractions = getCharacterMemories(characterId, 'interactions');
    echo     
    echo     // Basic response templates
    echo     if (q.includes('hello') || q.includes('hi') || q.includes('greetings')) {
    echo         return previousInteractions.length > 2 
    echo             ? "Well met again, friend. How may I assist you now?"
    echo             : "Greetings, adventurer! How may I assist you on your journey?";
    echo     } 
    echo     
    echo     if (q.includes('help') || q.includes('what can you do')) {
    echo         return "I am your faithful companion. I can provide advice, share lore about our world, or simply keep you company on your adventures.";
    echo     } 
    echo     
    echo     if (q.includes('lore') || q.includes('history') || q.includes('world')) {
    echo         return "The Ages of Arda span countless years, from the Music of the Ainur to the present day. The First Age saw the wars against Morgoth, while the Second Age witnessed the rise and fall of Númenor. The Third Age ended with the War of the Ring, and now we find ourselves in a new age of uncertainty and hope.";
    echo     } 
    echo     
    echo     if (q.includes('quest') || q.includes('mission')) {
    echo         return "Your current path seems perilous. Proceed with caution, but know that great rewards await the brave who persevere.";
    echo     } 
    echo     
    echo     // Default responses with some variety based on interaction count
    echo     const defaultResponses = [
    echo         "I stand ready to assist you on your journey. What guidance do you seek?",
    echo         "The path ahead is uncertain, but I shall accompany you nonetheless.",
    echo         "Many have walked these halls before us. Few have returned to tell their tales.",
    echo         "Listen closely to the whispers of these ancient stones. They have much wisdom to share.",
    echo         "Even in the darkest places, hope can be found if one knows where to look."
    echo     ];
    echo     
    echo     // Select a response based on the number of previous interactions
    echo     const responseIndex = previousInteractions.length % defaultResponses.length;
    echo     return defaultResponses[responseIndex];
    echo }
    echo 
    echo /**
    echo  * Store an interaction in memory
    echo  */
    echo function storeInteraction(characterId, type, content) {
    echo     if (!characterId) return;
    echo     
    echo     if (!characterMemories[characterId]) {
    echo         characterMemories[characterId] = {
    echo             interactions: [],
    echo             narratives: []
    echo         };
    echo     }
    echo     
    echo     // Add to interactions with timestamp
    echo     characterMemories[characterId].interactions.push({
    echo         timestamp: new Date().toISOString(),
    echo         type,
    echo         content
    echo     });
    echo     
    echo     // Keep only the last 20 interactions
    echo     if (characterMemories[characterId].interactions.length > 20) {
    echo         characterMemories[characterId].interactions.shift();
    echo     }
    echo     
    echo     // Save to disk (async)
    echo     saveMemoriesToDisk(characterId);
    echo }
    echo 
    echo /**
    echo  * Save memories to disk
    echo  */
    echo function saveMemoriesToDisk(characterId) {
    echo     try {
    echo         const memoryPath = path.join(config.memoryPath, `${characterId}.json`);
    echo         fs.writeFile(
    echo             memoryPath, 
    echo             JSON.stringify(characterMemories[characterId], null, 2), 
    echo             'utf8',
    echo             (err) => {
    echo                 if (err) {
    echo                     console.error(`Error saving memories to disk for ${characterId}:`, err);
    echo                 }
    echo             }
    echo         );
    echo     } catch (error) {
    echo         console.error(`Error in saveMemoriesToDisk for ${characterId}:`, error);
    echo     }
    echo }
    echo 
    echo /**
    echo  * Load memories from disk
    echo  */
    echo function loadMemoriesFromDisk(characterId) {
    echo     try {
    echo         const memoryPath = path.join(config.memoryPath, `${characterId}.json`);
    echo         if (fs.existsSync(memoryPath)) {
    echo             const data = fs.readFileSync(memoryPath, 'utf8');
    echo             characterMemories[characterId] = JSON.parse(data);
    echo             return true;
    echo         }
    echo     } catch (error) {
    echo         console.error(`Error loading memories from disk for ${characterId}:`, error);
    echo     }
    echo     return false;
    echo }
    echo 
    echo /**
    echo  * Get character memories of specified type
    echo  */
    echo function getCharacterMemories(characterId, type) {
    echo     if (!characterId) return [];
    echo     
    echo     // Try to load from memory first
    echo     if (!characterMemories[characterId]) {
    echo         // Try to load from disk
    echo         const loaded = loadMemoriesFromDisk(characterId);
    echo         
    echo         // Initialize if not found
    echo         if (!loaded) {
    echo             characterMemories[characterId] = {
    echo                 interactions: [],
    echo                 narratives: []
    echo             };
    echo         }
    echo     }
    echo     
    echo     // Return the requested memory type
    echo     if (type === 'interactions') {
    echo         return characterMemories[characterId].interactions || [];
    echo     }
    echo     
    echo     // Return all memories by default
    echo     return characterMemories[characterId];
    echo }
    echo 
    echo // Start the server
    echo app.listen(config.port, () => {
    echo     console.log(`===================================================`);
    echo     console.log(`Enhanced MCP Server running on port ${config.port}`);
    echo     console.log(`Source path: ${config.sourcePath}`);
    echo     console.log(`Memory path: ${config.memoryPath}`);
    echo     console.log(`===================================================`);
    echo     console.log(`Server is ready to receive companion queries`);
    echo     console.log(`Press Ctrl+C to stop the server`);
    echo     console.log(`===================================================`);
    echo });
) > "angband-doc-agent\src\enhanced-mcp-server.js"

echo ===================================================
echo Creating README file...
echo ===================================================

(
    echo # Ages of Arda - Enhanced MCP System
    echo 
    echo This document explains how to use the Enhanced Model Context Protocol (MCP) system with Ages of Arda.
    echo 
    echo ## Quick Start
    echo 
    echo ### Option 1: All-in-One Launcher
    echo Run `scripts/start-enhanced.bat` to:
    echo - Check for Node.js installation
    echo - Find an available port for the MCP server
    echo - Start the MCP server in the background
    echo - Launch the game with companion support
    echo 
    echo ### Option 2: Individual Scripts
    echo 1. Start the MCP server: `scripts/mcp-server.bat`
    echo 2. Start the game: `scripts/game.bat`
    echo 
    echo ### Option 3: Reset and Utilities
    echo - Reset window configurations: `scripts/reset-windows.bat`
    echo - Kill running MCP server processes: `scripts/kill-mcp.bat`
    echo 
    echo ## Enhanced Features
    echo 
    echo The Enhanced MCP System includes:
    echo - Character memory that persists between sessions
    echo - Context-aware companion responses
    echo - Improved performance and reliability
    echo 
    echo ## Technical Details
    echo 
    echo The MCP system stores memories in `angband-doc-agent/memories` and generates
    echo responses based on previous interactions and game events.
) > "README-ENHANCED-MCP.md"

echo ===================================================
echo Setup complete!
echo ===================================================
echo You can now:
echo - Start the game with enhanced MCP server: scripts/start-enhanced.bat
echo - Start only the MCP server: scripts/mcp-server.bat
echo - Start only the game: scripts/game.bat
echo ===================================================
pause 