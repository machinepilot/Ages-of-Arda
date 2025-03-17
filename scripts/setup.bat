@echo off
echo ===================================================
echo Ages of Arda - Setup
echo ===================================================

REM Set the current directory as the base directory
set "BASE_DIR=%CD%"

REM Check if scripts directory exists, create if not
if not exist "scripts" (
    echo Creating scripts directory...
    mkdir scripts
)

REM Check if the script files exist in the scripts directory
set MISSING_FILES=0

if not exist "scripts\start.bat" set /a MISSING_FILES+=1
if not exist "scripts\mcp-server.bat" set /a MISSING_FILES+=1
if not exist "scripts\game.bat" set /a MISSING_FILES+=1
if not exist "scripts\reset-windows.bat" set /a MISSING_FILES+=1
if not exist "scripts\kill-mcp.bat" set /a MISSING_FILES+=1
if not exist "scripts\install.bat" set /a MISSING_FILES+=1
if not exist "scripts\cleanup.bat" set /a MISSING_FILES+=1

if %MISSING_FILES% GTR 0 (
    echo Some script files are missing. Please make sure all required scripts are in the scripts directory.
    echo If this is your first time running setup, this is normal.
    echo.
    echo Press any key to continue with setup...
    pause >nul
)

REM Run the installation script
echo Running MCP server installation...
call scripts\install.bat

REM Check if old batch files exist
set OLD_FILES=0

if exist "setup-game-launcher.bat" set /a OLD_FILES+=1
if exist "start-game-with-companion.bat" set /a OLD_FILES+=1
if exist "start-mcp-server.bat" set /a OLD_FILES+=1
if exist "start-mcp-standalone.bat" set /a OLD_FILES+=1
if exist "custom-game-launcher.bat" set /a OLD_FILES+=1

if %OLD_FILES% GTR 0 (
    echo.
    echo Old batch files were detected in the main directory.
    echo These can be removed using the cleanup script.
    echo.
    set /p CLEANUP=Would you like to run the cleanup script now? (Y/N): 
    
    if /i "%CLEANUP%" EQU "Y" (
        call scripts\cleanup.bat
    ) else (
        echo You can run the cleanup script later using scripts\cleanup.bat
    )
)

echo ===================================================
echo Setup complete!
echo ===================================================
echo You can now:
echo - Start the game with MCP server: scripts\start.bat
echo - Start only the MCP server: scripts\mcp-server.bat
echo - Start only the game: scripts\game.bat
echo - Reset window configurations: scripts\reset-windows.bat
echo - Kill MCP server processes: scripts\kill-mcp.bat
echo ===================================================
pause 