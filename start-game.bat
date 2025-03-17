@echo off
setlocal enabledelayedexpansion

:: Set the base directory
set "BASE_DIR=C:\working_directory\ages-project\clean-ages-of-arda"
cd /d "%BASE_DIR%"

:: Check if the game exists
if not exist "angband.exe" (
    echo Game executable not found at: %BASE_DIR%\angband.exe
    echo Please make sure the game is installed correctly.
    pause
    exit /b 1
)

echo Starting Ages of Arda with companion support...
echo.
echo If the game doesn't start correctly, try running angband.exe directly:
echo %BASE_DIR%\angband.exe -n3
echo.
echo Remember to configure the companion in-game:
echo 1. Press '%%' to open the companions menu
echo 2. Select 'External Companion' and choose 'localhost:3000'
echo.

:: Start the game with companions enabled using PowerShell
echo Launching game...
powershell -Command "Start-Process '%BASE_DIR%\angband.exe' -ArgumentList '-n3'"

echo Command sent to launch game.
echo If no game window appears, try running the game executable directly.
pause
exit /b 0 