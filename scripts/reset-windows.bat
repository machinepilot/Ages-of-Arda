@echo off
echo ===================================================
echo Ages of Arda - Window Configuration Reset
echo ===================================================

REM Store the current directory
set BASE_DIR=%~dp0..
cd "%BASE_DIR%"

echo Checking for window configuration files...

set PRF_PATH=%USERPROFILE%\Documents\Angband\user\windows.prf
set SDL2_CONFIG_PATH=%BASE_DIR%\lib\user\sdl2init.txt

set FILES_DELETED=0

if exist "%PRF_PATH%" (
    echo Deleting windows.prf...
    del "%PRF_PATH%"
    set /a FILES_DELETED+=1
)

if exist "%SDL2_CONFIG_PATH%" (
    echo Deleting sdl2init.txt...
    del "%SDL2_CONFIG_PATH%"
    set /a FILES_DELETED+=1
)

if %FILES_DELETED% GTR 0 (
    echo Successfully reset %FILES_DELETED% window configuration file(s).
    echo The game will generate new configurations on next startup.
) else (
    echo No window configuration files found to reset.
)

echo ===================================================
echo Reset complete.
echo ===================================================
pause 