@echo off
echo ===================================================
echo Ages of Arda - Cleanup Old Batch Files
echo ===================================================

REM Set the base directory to the location of this script
set "BASE_DIR=%~dp0.."
cd "%BASE_DIR%"

echo This script will remove old batch files from the main directory.
echo These files have been replaced by improved versions in the scripts folder.
echo.
echo Files to be removed:
echo - setup-game-launcher.bat
echo - start-game-with-companion.bat
echo - start-mcp-server.bat
echo - start-mcp-standalone.bat
echo - custom-game-launcher.bat (if exists)
echo.
set /p CONFIRM=Are you sure you want to continue? (Y/N): 

if /i "%CONFIRM%" NEQ "Y" (
    echo Operation cancelled.
    pause
    exit /b 0
)

echo.
echo Removing old batch files...
set COUNT=0

if exist "setup-game-launcher.bat" (
    del "setup-game-launcher.bat"
    set /a COUNT+=1
    echo Removed: setup-game-launcher.bat
)

if exist "start-game-with-companion.bat" (
    del "start-game-with-companion.bat"
    set /a COUNT+=1
    echo Removed: start-game-with-companion.bat
)

if exist "start-mcp-server.bat" (
    del "start-mcp-server.bat"
    set /a COUNT+=1
    echo Removed: start-mcp-server.bat
)

if exist "start-mcp-standalone.bat" (
    del "start-mcp-standalone.bat"
    set /a COUNT+=1
    echo Removed: start-mcp-standalone.bat
)

if exist "custom-game-launcher.bat" (
    del "custom-game-launcher.bat"
    set /a COUNT+=1
    echo Removed: custom-game-launcher.bat
)

echo.
echo Cleanup complete. Removed %COUNT% files.
echo ===================================================
echo The new scripts are available in the scripts folder:
echo - scripts/start.bat (main launcher)
echo - scripts/mcp-server.bat (MCP server only)
echo - scripts/game.bat (game only)
echo - scripts/reset-windows.bat (reset window configs)
echo - scripts/kill-mcp.bat (kill MCP processes)
echo ===================================================
pause 