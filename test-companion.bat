@echo off
REM Test script for companion UI implementation

echo Testing companion UI implementation...

REM Run the game with the companion window enabled
start angband.exe -n2 -o

echo.
echo If the companion UI is working correctly, you should see:
echo 1. A companion window in subwindow 2
echo 2. The companion portrait and stats displayed
echo 3. Dialogue and thoughts from the companion
echo.
echo Press Ctrl+C to exit the test. 