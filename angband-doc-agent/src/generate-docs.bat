@echo off
REM Generate Angband Documentation

echo Checking for Python...
python --version > nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo Python is not installed or not in PATH. Please install Python 3.8 or higher.
    exit /b 1
)

echo Checking for required Python packages...
pip show requests > nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo Installing required Python packages...
    pip install requests
)

echo Checking for Node.js...
node --version > nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo Node.js is not installed or not in PATH. Please install Node.js.
    exit /b 1
)

echo Checking for required Node.js packages...
if not exist "node_modules\express" (
    echo Installing required Node.js packages...
    npm install express cors
)

echo Checking if MCP server is running...
curl -s http://localhost:3000/mcp/ping > nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo Starting simplified MCP server...
    start "MCP Server" cmd /c "node simple-mcp-server.js"
    
    echo Waiting for server to start...
    timeout /t 5 /nobreak > nul
)

echo Generating documentation...
python document-angband.py

echo Documentation generation complete!
echo Output files are in the 'docs' directory.
pause 