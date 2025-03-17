@echo off
echo ===================================================
echo Ages of Arda - MCP Server
echo ===================================================

REM Store the current directory
set BASE_DIR=%~dp0..
cd "%BASE_DIR%"

REM Check if Node.js is installed
where node >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Node.js is not installed or not in PATH.
    echo Please install Node.js from https://nodejs.org/
    echo After installing Node.js, run scripts/install.bat
    pause
    exit /b 1
)

REM Check if port 3000 is already in use
set PORT=3000
netstat -ano | findstr ":%PORT%" >nul
if %ERRORLEVEL% EQU 0 (
    echo WARNING: Port %PORT% is already in use.
    echo Attempting to find an available port...
    
    REM Try ports 3001-3010
    for /L %%p in (3001,1,3010) do (
        netstat -ano | findstr ":%%p" >nul
        if %ERRORLEVEL% NEQ 0 (
            echo Found available port: %%p
            set PORT=%%p
            goto port_found
        )
    )
    
    echo ERROR: Could not find an available port.
    echo Try running scripts/kill-mcp.bat to free up port 3000.
    pause
    exit /b 1
)

:port_found
echo Using port: %PORT%

REM Create or update .env file with correct port
echo PORT=%PORT%> "%BASE_DIR%\angband-doc-agent\.env"
echo SOURCE_PATH=%BASE_DIR%\src>> "%BASE_DIR%\angband-doc-agent\.env"
echo MEMORY_PATH=%BASE_DIR%\angband-doc-agent\memories>> "%BASE_DIR%\angband-doc-agent\.env"

REM Check for dependencies
if not exist "%BASE_DIR%\angband-doc-agent\node_modules" (
    echo Dependencies not found. Running installation...
    call scripts\install.bat
    if %ERRORLEVEL% NEQ 0 (
        echo ERROR: Failed to install dependencies.
        pause
        exit /b 1
    )
)

REM Ensure the memories directory exists
if not exist "%BASE_DIR%\angband-doc-agent\memories" (
    echo Creating memories directory...
    mkdir "%BASE_DIR%\angband-doc-agent\memories"
)

REM Check if enhanced-mcp-server.js exists
if not exist "%BASE_DIR%\angband-doc-agent\src\enhanced-mcp-server.js" (
    echo ERROR: Enhanced MCP server script not found.
    echo Checking for simple-mcp-server.js instead...
    
    if not exist "%BASE_DIR%\angband-doc-agent\src\simple-mcp-server.js" (
        echo ERROR: No MCP server scripts found.
        echo Please run scripts/install.bat first.
        pause
        exit /b 1
    )
    
    echo Using simple-mcp-server.js as fallback.
    set SERVER_SCRIPT=simple-mcp-server.js
) else (
    echo Using enhanced MCP server.
    set SERVER_SCRIPT=enhanced-mcp-server.js
)

echo ===================================================
echo Starting MCP server on port %PORT%...
echo ===================================================
echo Server: %SERVER_SCRIPT%
echo Press Ctrl+C to stop the server
echo ===================================================

cd "%BASE_DIR%\angband-doc-agent\src"
node %SERVER_SCRIPT%

echo ===================================================
echo MCP server stopped.
echo ===================================================
pause 