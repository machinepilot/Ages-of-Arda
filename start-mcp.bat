@echo off
setlocal enabledelayedexpansion

:: Set the base directory
set "BASE_DIR=C:\working_directory\ages-project\clean-ages-of-arda"
cd /d "%BASE_DIR%"

echo Starting MCP server setup...

:: Check if Node.js is installed
where node >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo Node.js is not installed or not in PATH.
    echo Please install Node.js from https://nodejs.org/
    echo After installation, run this script again.
    pause
    exit /b 1
)

:: Check if angband-doc-agent directory exists
if not exist "angband-doc-agent" (
    echo Creating angband-doc-agent directory...
    mkdir "angband-doc-agent"
    mkdir "angband-doc-agent\src"
)

:: Check if any previous MCP server is running on port 3000
set "PORT=3000"
netstat -ano | find ":%PORT% " | find "LISTENING" > nul
if %ERRORLEVEL% equ 0 (
    echo Port %PORT% is already in use.
    :: Find an available port between 3001-3010
    for /L %%p in (3001,1,3010) do (
        netstat -ano | find ":%%p " | find "LISTENING" > nul
        if !ERRORLEVEL! neq 0 (
            set "PORT=%%p"
            echo Will use port !PORT! instead.
            goto :port_found
        )
    )
    echo No available ports found in range 3001-3010.
    echo Please close any applications using these ports and try again.
    pause
    exit /b 1
)
:port_found

:: Check if package.json exists
if not exist "angband-doc-agent\package.json" (
    echo Creating package.json...
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
        echo     "dotenv": "^16.3.1"
        echo   }
        echo }
    ) > "angband-doc-agent\package.json"
)

:: Update .env file with port
echo Creating/updating .env file...
(
    echo PORT=%PORT%
    echo SOURCE_PATH=%BASE_DIR%
) > "angband-doc-agent\.env"

:: Check if dependencies are installed
if not exist "angband-doc-agent\node_modules" (
    echo Installing dependencies...
    cd /d "%BASE_DIR%\angband-doc-agent"
    call npm install
    cd /d "%BASE_DIR%"
)

echo Starting MCP server on port %PORT%...
cd /d "%BASE_DIR%\angband-doc-agent"
start cmd /k "node src/enhanced-mcp-server.js"
cd /d "%BASE_DIR%"

echo MCP server started!
echo.
echo To use the companion in-game:
echo 1. Run start-game.bat to launch the game
echo 2. In-game, press '%%' to open the companions menu
echo 3. Select 'External Companion' and choose 'localhost:%PORT%'
echo.
echo The MCP server will continue running in the background.
echo You can close it by closing the command window that opened.
echo.

exit /b 0 