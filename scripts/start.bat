@echo off
echo ===================================================
echo Ages of Arda - Complete Launcher
echo ===================================================

REM Store the current directory
set BASE_DIR=%~dp0..
cd "%BASE_DIR%"

REM Create scripts directory if it doesn't exist
if not exist "%BASE_DIR%\scripts" (
    mkdir "%BASE_DIR%\scripts"
)

REM Check if Node.js is installed
where node >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Node.js is not installed or not in PATH.
    echo Please install Node.js from https://nodejs.org/
    echo The game will start without MCP server support.
    goto start_game
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
    
    echo WARNING: Could not find an available port.
    echo The game will start without MCP server support.
    goto start_game
)

:port_found
echo Using port: %PORT%

REM Create or update .env file with correct port
echo PORT=%PORT%> "%BASE_DIR%\angband-doc-agent\.env"
echo ANGBAND_SOURCE_PATH=%BASE_DIR%>> "%BASE_DIR%\angband-doc-agent\.env"

REM Check for dependencies
if not exist "%BASE_DIR%\angband-doc-agent\node_modules" (
    echo Installing dependencies...
    cd "%BASE_DIR%\angband-doc-agent"
    call npm install
    if %ERRORLEVEL% NEQ 0 (
        echo WARNING: Failed to install dependencies.
        echo The game will start without MCP server support.
        cd "%BASE_DIR%"
        goto start_game
    )
    cd "%BASE_DIR%"
)

REM Create a temporary batch file to start the MCP server
echo @echo off > "%TEMP%\start_mcp_server.bat"
echo cd "%BASE_DIR%\angband-doc-agent\src" >> "%TEMP%\start_mcp_server.bat"
echo set PORT=%PORT% >> "%TEMP%\start_mcp_server.bat"
echo node simple-mcp-server.js >> "%TEMP%\start_mcp_server.bat"
echo pause >> "%TEMP%\start_mcp_server.bat"

echo Starting MCP server in background...
start "Ages of Arda - MCP Server" cmd /c "%TEMP%\start_mcp_server.bat"

echo Waiting for MCP server to initialize...
timeout /t 3 /nobreak > nul

:start_game
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
    echo ERROR: Could not find angband.exe
    echo Please make sure the game executable is in one of these locations:
    echo - %BASE_DIR%\angband.exe
    echo - %BASE_DIR%\src\angband.exe
    echo - %BASE_DIR%\bin\angband.exe
    pause
    exit /b 1
)

echo Starting Ages of Arda...
"%GAME_PATH%" -n3

echo ===================================================
echo Game closed. MCP server may still be running.
echo Close the MCP Server window when finished.
echo ===================================================
pause 