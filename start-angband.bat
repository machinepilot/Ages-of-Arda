@echo off
REM Angband Startup Script with MCP Server
REM This script launches both the MCP server and Angband game

SETLOCAL EnableDelayedExpansion

REM Set the current directory as the base path
SET BASE_PATH=%~dp0
SET CONFIG_FILE=%BASE_PATH%mcp_config.ini

ECHO =======================================================
ECHO Angband Startup with MCP Server Integration
ECHO =======================================================

REM Check if the config file exists
IF NOT EXIST "%CONFIG_FILE%" (
    ECHO Configuration file not found: %CONFIG_FILE%
    ECHO Creating default configuration file...
    COPY "%BASE_PATH%\lib\customize\mcp_config_default.ini" "%CONFIG_FILE%" > NUL
    IF NOT EXIST "%CONFIG_FILE%" (
        ECHO Failed to create configuration file!
        GOTO ERROR
    )
)

REM Read MCP server configuration
CALL :ReadINI "%CONFIG_FILE%" "MCP_SERVER" "enabled" mcp_enabled
CALL :ReadINI "%CONFIG_FILE%" "MCP_SERVER" "autostart" mcp_autostart
CALL :ReadINI "%CONFIG_FILE%" "MCP_SERVER" "server_path" mcp_server_path
CALL :ReadINI "%CONFIG_FILE%" "MCP_SERVER" "port" mcp_port

ECHO Configuration loaded successfully.

REM Start MCP server if enabled and autostart is true
IF "%mcp_enabled%"=="true" (
    IF "%mcp_autostart%"=="true" (
        ECHO Starting MCP server on port %mcp_port%...
        
        REM Check if Node.js is installed
        WHERE node >nul 2>nul
        IF %ERRORLEVEL% NEQ 0 (
            ECHO Node.js is not installed or not in PATH.
            ECHO Please install Node.js to use the MCP server.
            GOTO SKIP_MCP
        )
        
        REM Check if server directory exists
        IF NOT EXIST "%mcp_server_path%" (
            ECHO MCP server directory not found: %mcp_server_path%
            GOTO SKIP_MCP
        )
        
        CD "%mcp_server_path%"
        
        REM Check if server is already running on the specified port
        netstat -ano | findstr ":%mcp_port%" > NUL
        IF %ERRORLEVEL% EQU 0 (
            ECHO MCP server is already running on port %mcp_port%.
        ) ELSE (
            REM Start the MCP server in a separate window
            START "Angband MCP Server" /MIN node mcp-server.js
            
            REM Wait for server to start
            ECHO Waiting for MCP server to start...
            TIMEOUT /T 3 > NUL
            
            REM Verify server is running
            netstat -ano | findstr ":%mcp_port%" > NUL
            IF %ERRORLEVEL% EQU 0 (
                ECHO MCP server started successfully.
            ) ELSE (
                ECHO Warning: MCP server may not have started correctly.
            )
        )
        
        CD "%BASE_PATH%"
    )
)

:SKIP_MCP
ECHO Starting Angband...

REM Extract graphics settings
CALL :ReadINI "%CONFIG_FILE%" "WINDOW_PREFERENCES" "use_graphics" use_graphics
CALL :ReadINI "%CONFIG_FILE%" "WINDOW_PREFERENCES" "graphics_mode" graphics_mode

REM Set graphics flags if enabled
SET GRAPHICS_FLAG=
IF "%use_graphics%"=="true" (
    IF "%graphics_mode%"=="old" SET GRAPHICS_FLAG=-g
    IF "%graphics_mode%"=="new" SET GRAPHICS_FLAG=-gn
)

REM Set debug mode if enabled
CALL :ReadINI "%CONFIG_FILE%" "ADVANCED" "debug_mode" debug_mode
SET DEBUG_FLAG=
IF "%debug_mode%"=="true" SET DEBUG_FLAG=-w

REM Run Angband with the appropriate flags
START "" angband.exe %GRAPHICS_FLAG% %DEBUG_FLAG%

ECHO Angband launched successfully.
GOTO END

:ERROR
ECHO An error occurred during startup.
PAUSE
EXIT /B 1

:END
EXIT /B 0

REM Function to read INI values
:ReadINI
FOR /F "tokens=*" %%A IN ('FINDSTR /B /I "[%~2]" %~1') DO (
    SET SECTION=%%A
)
FOR /F "tokens=1,2 delims==" %%A IN ('FINDSTR /B /I "%~3=" %~1') DO (
    IF "%%A"=="%~3" (
        SET %~4=%%B
        REM Remove leading/trailing spaces and comments
        SET %~4=!%~4:;=!
        CALL :Trim %~4
        EXIT /B 0
    )
)
EXIT /B 1

:Trim
SET %1=!%1:~0,1!
EXIT /B 0 