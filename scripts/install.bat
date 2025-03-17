@echo off
echo ===================================================
echo Ages of Arda - MCP Server Installation
echo ===================================================

REM Set the base directory to the location of this script
set "BASE_DIR=%~dp0.."
cd "%BASE_DIR%"

REM Check if Node.js is installed
where node >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Node.js is not installed.
    echo Please install Node.js from https://nodejs.org/
    echo After installing Node.js, run this script again.
    pause
    exit /b 1
)

echo Node.js is installed. Checking version...
node --version

REM Check if the angband-doc-agent directory exists
if not exist "angband-doc-agent" (
    echo ERROR: angband-doc-agent directory not found.
    echo Please make sure you're running this script from the main game directory.
    pause
    exit /b 1
)

echo Checking for package.json in angband-doc-agent directory...

REM Check if package.json exists, create if not
if not exist "angband-doc-agent\package.json" (
    echo Creating package.json file...
    (
        echo {
        echo   "name": "angband-doc-agent",
        echo   "version": "1.0.0",
        echo   "description": "MCP server for Ages of Arda",
        echo   "main": "src/simple-mcp-server.js",
        echo   "scripts": {
        echo     "start": "node src/simple-mcp-server.js"
        echo   },
        echo   "dependencies": {
        echo     "express": "^4.18.2",
        echo     "dotenv": "^16.0.3"
        echo   }
        echo }
    ) > "angband-doc-agent\package.json"
    echo package.json created successfully.
) else (
    echo package.json found.
)

REM Check if .env file exists, create if not
if not exist "angband-doc-agent\.env" (
    echo Creating .env file...
    (
        echo PORT=3000
        echo SOURCE_PATH=../src
    ) > "angband-doc-agent\.env"
    echo .env file created successfully.
) else (
    echo .env file found.
)

REM Check if simple-mcp-server.js exists in the src directory
if not exist "angband-doc-agent\src" (
    echo Creating src directory...
    mkdir "angband-doc-agent\src"
)

echo Installing dependencies...
cd "angband-doc-agent"
call npm install

if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Failed to install dependencies.
    echo Trying to install specific packages...
    call npm install express dotenv
    
    if %ERRORLEVEL% NEQ 0 (
        echo ERROR: Installation failed.
        cd "%BASE_DIR%"
        pause
        exit /b 1
    )
)

cd "%BASE_DIR%"
echo ===================================================
echo Installation complete!
echo ===================================================
echo You can now run the MCP server using scripts/mcp-server.bat
echo or start both the server and game using scripts/start.bat
echo ===================================================
pause 