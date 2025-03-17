@echo on
setlocal enabledelayedexpansion

:: Set the base directory
set "BASE_DIR=C:\working_directory\ages-project\clean-ages-of-arda"
cd /d "%BASE_DIR%"
echo Current directory: %CD%

:: Check if the game exists
if not exist "angband.exe" (
    echo ERROR: Game executable not found at: %BASE_DIR%\angband.exe
    echo Please make sure the game is installed correctly.
    pause
    exit /b 1
) else (
    echo Found game executable at: %BASE_DIR%\angband.exe
    echo File size: 
    dir angband.exe
)

echo Starting Ages of Arda with companion support...
echo.
echo Command to execute: start /wait "" "%BASE_DIR%\angband.exe" -n3
echo.
echo Remember to configure the companion in-game:
echo 1. Press '%%' to open the companions menu
echo 2. Select 'External Companion' and choose 'localhost:3000'
echo.

:: Start the game with companions enabled
echo Attempting to launch game with companion support...
start /wait cmd /k "%BASE_DIR%\angband.exe" -n3

echo Game process ended.
echo If the game window didn't appear, try running angband.exe directly:
echo %BASE_DIR%\angband.exe -n3
echo.

pause
exit /b 0 