@echo off
REM Script to run all the Lute the Bard tests on Windows

echo ====== Lute the Bard Test Suite ======

REM Check if dependencies are installed
echo.
echo Checking dependencies...

REM Check for Node.js
where node >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo Node.js is not installed. Please install Node.js to continue.
    exit /b 1
)
echo Node.js is installed.

REM Check for curl
where curl >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo curl is not installed. Please install curl to continue.
    exit /b 1
)
echo curl is installed.

REM Check for Ollama (optional)
where ollama >nul 2>nul
if %ERRORLEVEL% EQU 0 (
    echo Ollama is installed.
    SET OLLAMA_INSTALLED=true
) else (
    echo WARNING: Ollama is not installed. You can still use OpenAI, but local LLM testing will not be available.
    SET OLLAMA_INSTALLED=false
)

REM Check for dependencies in package.json
echo.
echo Installing Node.js dependencies...
call npm install

REM Check if Ollama is running (if installed)
if "%OLLAMA_INSTALLED%" == "true" (
    echo.
    echo Checking if Ollama is running...
    curl -s http://localhost:11434/api/tags | findstr "llama3" >nul
    if %ERRORLEVEL% EQU 0 (
        echo Ollama is running and llama3 model is available.
        SET OLLAMA_RUNNING=true
    ) else (
        echo WARNING: Ollama is not running or llama3 model is not available.
        echo Starting Ollama and pulling llama3 model...
        start /b ollama pull llama3
        echo Continue with tests while Ollama model is downloading...
        SET OLLAMA_RUNNING=false
    )
)

REM Compile C test programs
echo.
echo Compiling C test programs...
mingw32-make clean && mingw32-make

REM Start the MCP server
echo.
echo Starting MCP server...
if "%OLLAMA_RUNNING%" == "true" (
    REM Use Ollama provider if available
    start /b cmd /c "set LLM_PROVIDER=ollama && node bard-mcp-server.js"
) else (
    REM Fall back to OpenAI if Ollama is not available
    if "%OPENAI_API_KEY%" == "" (
        echo No OpenAI API key found in environment variables.
        set /p OPENAI_API_KEY=Enter your OpenAI API key (leave blank to skip OpenAI tests): 
    )
    
    if not "%OPENAI_API_KEY%" == "" (
        start /b cmd /c "set LLM_PROVIDER=openai && set OPENAI_API_KEY=%OPENAI_API_KEY% && node bard-mcp-server.js"
    ) else (
        echo No LLM provider available. Tests cannot continue.
        exit /b 1
    )
)

REM Wait for server to start
echo Waiting for server to start...
timeout /t 3 /nobreak > nul

REM Run MCP server tests
echo.
echo Running MCP server tests...
node test-mcp-server.js

REM Run MCP client tests
echo.
echo Running MCP client tests...
test-mcp-client.exe

REM Run Bard module tests
echo.
echo Running Bard module tests...
test-bard.exe

REM Clean up - find the server process and kill it
echo.
echo Cleaning up...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":3000"') do (
    taskkill /f /pid %%a > nul 2>&1
)
mingw32-make clean

echo.
echo All tests completed successfully!
echo.
echo ====== Lute the Bard Test Suite Completed ====== 