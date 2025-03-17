@echo off
echo ===================================================
echo Enhanced MCP Server Test
echo ===================================================

rem Check if Node.js is installed
where node >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo Error: Node.js is not installed or not in PATH.
    echo Please install Node.js from https://nodejs.org/
    pause
    exit /b 1
)

rem Check if axios is installed
if not exist "node_modules\axios" (
    echo Installing axios package...
    call npm install axios
)

rem Check if the server is running
curl -s http://localhost:3000/health >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo MCP server does not appear to be running.
    echo Please run start-mcp.bat first, then run this test script again.
    pause
    exit /b 1
)

echo Running enhanced MCP server tests...
echo.
node test-enhanced-mcp.js

if %ERRORLEVEL% equ 0 (
    echo.
    echo ===================================================
    echo Tests completed successfully!
    echo ===================================================
) else (
    echo.
    echo ===================================================
    echo Tests failed with errors.
    echo ===================================================
)

pause 