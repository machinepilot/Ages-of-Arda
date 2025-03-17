@echo off
echo ===================================================
echo Ages of Arda - Kill MCP Server Processes
echo ===================================================

echo Checking for running MCP server processes...

REM Find Node.js processes running MCP server
for /f "tokens=1" %%p in ('tasklist /fi "imagename eq node.exe" /fo csv /nh') do (
    for /f "tokens=2 delims=," %%i in ('tasklist /fi "imagename eq node.exe" /fi "windowtitle eq *MCP Server*" /fo csv /nh') do (
        echo Found MCP server process: %%i
        echo Terminating process...
        taskkill /PID %%i /F
        if %ERRORLEVEL% EQU 0 (
            echo Successfully terminated MCP server process.
        ) else (
            echo Failed to terminate process.
        )
    )
)

REM Check if port 3000 is still in use
netstat -ano | findstr ":3000" > nul
if %ERRORLEVEL% EQU 0 (
    echo Port 3000 is still in use.
    for /f "tokens=5" %%p in ('netstat -ano ^| findstr ":3000"') do (
        echo Found process using port 3000: %%p
        echo Terminating process...
        taskkill /PID %%p /F
        if %ERRORLEVEL% EQU 0 (
            echo Successfully terminated process.
        ) else (
            echo Failed to terminate process.
        )
    )
) else (
    echo No processes found using port 3000.
)

echo ===================================================
echo Process cleanup complete.
echo ===================================================
pause 