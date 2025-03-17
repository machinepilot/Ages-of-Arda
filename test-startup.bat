@echo off
SETLOCAL EnableDelayedExpansion

REM Test script for Ages of Arda startup components
echo *** Ages of Arda - Startup Components Test ***
echo.

REM Test 1: Check if files exist
echo === Test 1: Verifying files ===
set MISSING_FILES=0

REM List of files to check
set FILES_TO_CHECK=^
src\sdl2-config-generator.c^
src\sdl2-config-generator.h^
src\tests\test-sdl2-config-generator.c^
start-ages-of-arda.bat^
start-ages-of-arda.sh^
lib\customize\mcp_config_default.ini^
README-STARTUP.md^
STARTUP-IMPLEMENTATION.md^
IMPLEMENTATION-NOTES.md

for %%F in (%FILES_TO_CHECK%) do (
    if not exist "%%F" (
        echo [FAIL] File not found: %%F
        set /a MISSING_FILES+=1
    ) else (
        echo [PASS] File exists: %%F
    )
)

if %MISSING_FILES% EQU 0 (
    echo All files present.
) else (
    echo %MISSING_FILES% files missing!
)
echo.

REM Test 2: Check configuration files
echo === Test 2: Testing config file generation ===
if exist "lib\user\sdl2init.txt" (
    echo SDL2 config exists, backing it up for testing...
    copy "lib\user\sdl2init.txt" "lib\user\sdl2init.txt.bak" > nul
    del "lib\user\sdl2init.txt"
)

echo Calling configuration generator directly would require compilation...
echo Instead, we'll test if the startup script handles missing config correctly.
echo.

REM Test 3: Test configuration file handling in startup script
echo === Test 3: Testing configuration file handling ===
if exist "mcp_config.ini" (
    echo MCP config exists, backing it up for testing...
    copy "mcp_config.ini" "mcp_config.ini.bak" > nul
    del "mcp_config.ini"
)

echo Checking if startup script creates default config...
call start-ages-of-arda.bat test_mode

if exist "mcp_config.ini" (
    echo [PASS] Startup script created default configuration file
) else (
    echo [FAIL] Startup script did not create default configuration file
)
echo.

REM Test 4: Verify MCP Server path detection
echo === Test 4: Checking MCP server path detection ===
set SERVER_PATH=angband-doc-agent/src
if exist "%SERVER_PATH%" (
    echo [PASS] MCP Server path is valid: %SERVER_PATH%
) else (
    echo [WARN] MCP Server path might be invalid: %SERVER_PATH%
    echo This may cause the server autostart to fail.
)
echo.

REM Test 5: Check Node.js installation
echo === Test 5: Checking Node.js installation ===
where node > nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo [PASS] Node.js is installed
    for /f "tokens=1,2 delims=v" %%a in ('node -v') do echo Version: %%b
) else (
    echo [WARN] Node.js not found in PATH
    echo This may cause the MCP server autostart to fail.
)
echo.

REM Test 6: Restore any backed up files
echo === Restoring backed up files ===
if exist "lib\user\sdl2init.txt.bak" (
    copy "lib\user\sdl2init.txt.bak" "lib\user\sdl2init.txt" > nul
    del "lib\user\sdl2init.txt.bak"
    echo Restored SDL2 configuration file
)

if exist "mcp_config.ini.bak" (
    copy "mcp_config.ini.bak" "mcp_config.ini" > nul
    del "mcp_config.ini.bak"
    echo Restored MCP configuration file
)
echo.

REM Summary
echo === Test Summary ===
echo File verification: %MISSING_FILES% missing files
echo Configuration handling: Tested
echo MCP server path detection: Checked
echo Node.js installation: Checked
echo.
echo Test script completed.
ENDLOCAL 