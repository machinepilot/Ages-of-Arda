@echo off
REM Test script for companion UI window functionality

echo Testing companion UI window functionality...

REM Reset any existing window configuration
call reset-window-config.bat 1

REM Run the game with Term-2 showing the companion window
echo When the game starts, do the following:
echo 1. Press = (equals) to access window options
echo 2. Press w to access window displays
echo 3. For Term-2, make sure "Display companion information" is selected
echo 4. Verify that the companion UI is now visible in Term-2 

REM Start the game with Term-2 active
start angband.exe -n2

echo.
echo If the companion window feature is working correctly, you should be able to:
echo 1. Select "Display companion information" from the window options 
echo 2. See the companion portrait and information in Term-2
echo 3. See companion dialogue and thoughts that respond to game events
echo.
echo Press Ctrl+C to exit this window when done testing. 