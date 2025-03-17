@echo off
echo ===================================================
echo Ages of Arda - Game Launcher
echo ===================================================

REM Store the current directory
set BASE_DIR=%~dp0..
cd "%BASE_DIR%"

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
echo Game closed.
echo ===================================================
pause 