@echo off
echo ===================================================
echo Ages of Arda - MCP Server Startup
echo ===================================================

cd %~dp0..

echo Checking for Node.js...
where node >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Node.js is not installed or not in PATH.
    echo Please install Node.js from https://nodejs.org/
    pause
    exit /b 1
)

echo Checking for dependencies...
if not exist "node_modules" (
    echo Installing dependencies...
    call npm install
    if %ERRORLEVEL% NEQ 0 (
        echo ERROR: Failed to install dependencies.
        pause
        exit /b 1
    )
)

echo Setting up environment...
if not exist ".env" (
    echo Creating default .env file...
    echo ANGBAND_SOURCE_PATH=%CD%> .env
    echo PORT=3000>> .env
)

echo Starting MCP server...
cd src
node simple-mcp-server.js

if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Failed to start MCP server.
    pause
    exit /b 1
)

pause 