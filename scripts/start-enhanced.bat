@echo off
echo ===================================================
echo Ages of Arda - Enhanced Launcher
echo ===================================================

REM Store the absolute path to the game directory
set BASE_DIR=C:\working_directory\ages-project\clean-ages-of-arda
cd "%BASE_DIR%"

REM Check if Node.js is installed
where node >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Node.js is not installed or not in PATH.
    echo Please install Node.js from https://nodejs.org/
    echo The game will start without MCP server support.
    goto start_game
)

REM Check if enhanced-mcp-server.js exists, create if not
if not exist "%BASE_DIR%\angband-doc-agent\src\enhanced-mcp-server.js" (
    echo Enhanced MCP server not found. Creating a simplified version...
    
    REM Make sure src directory exists
    if not exist "%BASE_DIR%\angband-doc-agent\src" (
        mkdir "%BASE_DIR%\angband-doc-agent\src"
    )
    
    REM Create simple server script
    echo const express = require('express'); > "%BASE_DIR%\angband-doc-agent\src\enhanced-mcp-server.js"
    echo const fs = require('fs'); >> "%BASE_DIR%\angband-doc-agent\src\enhanced-mcp-server.js"
    echo const path = require('path'); >> "%BASE_DIR%\angband-doc-agent\src\enhanced-mcp-server.js"
    echo require('dotenv').config({ path: path.join(__dirname, '..', '.env') }); >> "%BASE_DIR%\angband-doc-agent\src\enhanced-mcp-server.js"
    echo. >> "%BASE_DIR%\angband-doc-agent\src\enhanced-mcp-server.js"
    echo const app = express(); >> "%BASE_DIR%\angband-doc-agent\src\enhanced-mcp-server.js"
    echo app.use(express.json()); >> "%BASE_DIR%\angband-doc-agent\src\enhanced-mcp-server.js"
    echo. >> "%BASE_DIR%\angband-doc-agent\src\enhanced-mcp-server.js"
    echo app.post('/companion/response', (req, res) => { >> "%BASE_DIR%\angband-doc-agent\src\enhanced-mcp-server.js"
    echo   const { query } = req.body; >> "%BASE_DIR%\angband-doc-agent\src\enhanced-mcp-server.js"
    echo   console.log('Query:', query); >> "%BASE_DIR%\angband-doc-agent\src\enhanced-mcp-server.js"
    echo   res.json({ response: 'Greetings, adventurer! I am your companion on this journey.' }); >> "%BASE_DIR%\angband-doc-agent\src\enhanced-mcp-server.js"
    echo }); >> "%BASE_DIR%\angband-doc-agent\src\enhanced-mcp-server.js"
    echo. >> "%BASE_DIR%\angband-doc-agent\src\enhanced-mcp-server.js"
    echo app.get('/health', (req, res) => { >> "%BASE_DIR%\angband-doc-agent\src\enhanced-mcp-server.js"
    echo   res.json({ status: 'ok' }); >> "%BASE_DIR%\angband-doc-agent\src\enhanced-mcp-server.js"
    echo }); >> "%BASE_DIR%\angband-doc-agent\src\enhanced-mcp-server.js"
    echo. >> "%BASE_DIR%\angband-doc-agent\src\enhanced-mcp-server.js"
    echo const PORT = process.env.PORT || 3000; >> "%BASE_DIR%\angband-doc-agent\src\enhanced-mcp-server.js"
    echo app.listen(PORT, () => { >> "%BASE_DIR%\angband-doc-agent\src\enhanced-mcp-server.js"
    echo   console.log(`Enhanced MCP Server running on port ${PORT}`); >> "%BASE_DIR%\angband-doc-agent\src\enhanced-mcp-server.js"
    echo }); >> "%BASE_DIR%\angband-doc-agent\src\enhanced-mcp-server.js"
)

REM Check if package.json exists, update if needed
if not exist "%BASE_DIR%\angband-doc-agent\package.json" (
    echo Creating package.json...
    echo { > "%BASE_DIR%\angband-doc-agent\package.json"
    echo   "name": "angband-doc-agent", >> "%BASE_DIR%\angband-doc-agent\package.json"
    echo   "version": "1.0.0", >> "%BASE_DIR%\angband-doc-agent\package.json"
    echo   "description": "MCP server for Ages of Arda", >> "%BASE_DIR%\angband-doc-agent\package.json"
    echo   "main": "src/enhanced-mcp-server.js", >> "%BASE_DIR%\angband-doc-agent\package.json"
    echo   "dependencies": { >> "%BASE_DIR%\angband-doc-agent\package.json"
    echo     "express": "^4.18.2", >> "%BASE_DIR%\angband-doc-agent\package.json"
    echo     "dotenv": "^16.0.3" >> "%BASE_DIR%\angband-doc-agent\package.json"
    echo   } >> "%BASE_DIR%\angband-doc-agent\package.json"
    echo } >> "%BASE_DIR%\angband-doc-agent\package.json"
)

REM Make sure .env file exists
if not exist "%BASE_DIR%\angband-doc-agent\.env" (
    echo Creating .env file...
    echo PORT=3000 > "%BASE_DIR%\angband-doc-agent\.env"
    echo SOURCE_PATH=%BASE_DIR%\src >> "%BASE_DIR%\angband-doc-agent\.env"
)

REM Check if dependencies are installed
if not exist "%BASE_DIR%\angband-doc-agent\node_modules" (
    echo Installing dependencies...
    cd "%BASE_DIR%\angband-doc-agent"
    call npm install express dotenv
    cd "%BASE_DIR%"
)

REM Check if port 3000 is already in use
netstat -ano | findstr ":3000" >nul
if %ERRORLEVEL% EQU 0 (
    echo WARNING: Port 3000 is already in use.
    echo The game will start without MCP server support.
    goto start_game
)

REM Create a temporary batch file to start the MCP server
echo @echo off > "%TEMP%\start_mcp_server.bat"
echo cd "%BASE_DIR%\angband-doc-agent" >> "%TEMP%\start_mcp_server.bat"
echo node src\enhanced-mcp-server.js >> "%TEMP%\start_mcp_server.bat"
echo pause >> "%TEMP%\start_mcp_server.bat"

echo Starting MCP server in background...
start "Ages of Arda - MCP Server" cmd /c "%TEMP%\start_mcp_server.bat"

echo Waiting for MCP server to initialize...
timeout /t 3 /nobreak > nul

:start_game
echo ===================================================
echo Starting Ages of Arda with companion support...
echo ===================================================
echo 1. When in-game, press '=' to access options
echo 2. Select 'Window options' (press 'w')
echo 3. For Term-2, enable "Display companion information"
echo 4. Press ESC to save and return to the game
echo ===================================================

cd "%BASE_DIR%"
"%BASE_DIR%\angband.exe" -n3

echo ===================================================
echo Game closed. MCP server may still be running.
echo Close the MCP Server window when finished.
echo ===================================================
pause 