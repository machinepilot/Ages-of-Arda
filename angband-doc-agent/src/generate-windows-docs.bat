@echo off
REM Windows Documentation Generator
REM This batch file runs the documentation generator with Windows-specific settings

echo Angband Windows Documentation Generator
echo =======================================

REM Check if Python is available
python --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo Error: Python is not available in the PATH
    exit /b 1
)

REM Check if the MCP server is running
curl -s http://localhost:3000/mcp/ping >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo Starting MCP server...
    start /b cmd /c "node mcp-server.js"
    timeout /t 5
)

REM Create output directory
if not exist "..\output\windows" mkdir "..\output\windows"

REM Run the Windows module creator
echo Creating Windows module documentation...
python windows-module-creator.py

REM Generate Windows documentation
echo Generating Windows documentation...
python document-angband.py --windows-only --output ..\output\windows

REM Generate Visual Studio project documentation
echo Generating Visual Studio project documentation...
python document-angband.py --vs-project --output ..\output\windows\vs-project

REM Run tests
echo Running tests...
python test-windows-doc.py --test detection

echo Documentation generation complete!
echo Output is available in ..\output\windows

REM Open the documentation in the default browser
start "" "..\output\windows\windows_index.md" 