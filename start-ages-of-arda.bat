@echo off
SETLOCAL EnableDelayedExpansion

REM *** Ages of Arda Startup Script ***
REM This script starts both the MCP server and the Angband game with optimized window settings

REM Parse command line arguments
SET TEST_MODE=false
SET FORCE_CONFIG_REGEN=false

:parse_args
IF "%1"=="" GOTO end_parse_args
IF /I "%1"=="test_mode" SET TEST_MODE=true
IF /I "%1"=="force_config_regen" SET FORCE_CONFIG_REGEN=true
SHIFT
GOTO parse_args
:end_parse_args

REM Set base paths
SET BASE_PATH=%~dp0
SET CONFIG_FILE=%BASE_PATH%mcp_config.ini
SET DEFAULT_CONFIG_PATH=%BASE_PATH%lib\customize\mcp_config_default.ini
SET SDL2_CONFIG_PATH=%BASE_PATH%lib\user\sdl2init.txt
SET SDL2_CONFIG_BACKUP=%BASE_PATH%lib\user\sdl2init.txt.backup

REM Create backup of SDL2 config if it doesn't exist
IF EXIST "%SDL2_CONFIG_PATH%" IF NOT EXIST "%SDL2_CONFIG_BACKUP%" (
    COPY "%SDL2_CONFIG_PATH%" "%SDL2_CONFIG_BACKUP%" > NUL
)

REM Restore SDL2 config from backup if needed
IF NOT EXIST "%SDL2_CONFIG_PATH%" IF EXIST "%SDL2_CONFIG_BACKUP%" (
    COPY "%SDL2_CONFIG_BACKUP%" "%SDL2_CONFIG_PATH%" > NUL
)

REM Display welcome message
ECHO.
ECHO *** Ages of Arda - First Age ***
ECHO *** Starting game environment...
ECHO.

REM Check for configuration file
IF NOT EXIST "%CONFIG_FILE%" (
    ECHO Configuration file not found: %CONFIG_FILE%
    ECHO Creating default configuration...
    
    IF EXIST "%DEFAULT_CONFIG_PATH%" (
        COPY "%DEFAULT_CONFIG_PATH%" "%CONFIG_FILE%" > NUL
    ) ELSE (
        ECHO ERROR: Default configuration file not found at %DEFAULT_CONFIG_PATH%
        ECHO Creating basic configuration file...
        
        ECHO [MCP_SERVER]> "%CONFIG_FILE%"
        ECHO enabled=true>> "%CONFIG_FILE%"
        ECHO autostart=true>> "%CONFIG_FILE%"
        ECHO server_path=angband-doc-agent/src>> "%CONFIG_FILE%"
        ECHO port=3000>> "%CONFIG_FILE%"
        ECHO timeout=30>> "%CONFIG_FILE%"
        ECHO retry_attempts=3>> "%CONFIG_FILE%"
        ECHO.>> "%CONFIG_FILE%"
        
        ECHO [WINDOW_PREFERENCES]>> "%CONFIG_FILE%"
        ECHO use_graphics=true>> "%CONFIG_FILE%"
        ECHO graphics_mode=3>> "%CONFIG_FILE%"
        ECHO fullscreen=true>> "%CONFIG_FILE%"
        ECHO.>> "%CONFIG_FILE%"
        
        ECHO [ADVANCED]>> "%CONFIG_FILE%"
        ECHO debug_mode=false>> "%CONFIG_FILE%"
    )
)

REM Force regeneration of SDL2 config if requested
IF "%FORCE_CONFIG_REGEN%"=="true" (
    ECHO Forcing regeneration of SDL2 configuration...
    IF EXIST "%SDL2_CONFIG_PATH%" (
        DEL "%SDL2_CONFIG_PATH%"
    )
)

REM Read configuration settings
CALL :ReadINI "%CONFIG_FILE%" "MCP_SERVER" "enabled" mcp_enabled
CALL :ReadINI "%CONFIG_FILE%" "MCP_SERVER" "autostart" mcp_autostart
CALL :ReadINI "%CONFIG_FILE%" "MCP_SERVER" "server_path" mcp_server_path
CALL :ReadINI "%CONFIG_FILE%" "MCP_SERVER" "port" mcp_port
CALL :ReadINI "%CONFIG_FILE%" "MCP_SERVER" "timeout" mcp_timeout
CALL :ReadINI "%CONFIG_FILE%" "MCP_SERVER" "retry_attempts" mcp_retry_attempts

REM Set defaults if values are missing
IF "%mcp_enabled%"=="" SET mcp_enabled=true
IF "%mcp_autostart%"=="" SET mcp_autostart=true
IF "%mcp_server_path%"=="" SET mcp_server_path=angband-doc-agent/src
IF "%mcp_port%"=="" SET mcp_port=3000
IF "%mcp_timeout%"=="" SET mcp_timeout=30
IF "%mcp_retry_attempts%"=="" SET mcp_retry_attempts=3

REM Skip MCP server in test mode
IF NOT "%TEST_MODE%"=="true" (
    REM Start MCP server if enabled and autostart is true
    IF /I "%mcp_enabled%"=="true" (
        IF /I "%mcp_autostart%"=="true" (
            ECHO Checking for Node.js installation...
            WHERE node >nul 2>nul
            IF !ERRORLEVEL! NEQ 0 (
                ECHO ERROR: Node.js is not installed or not in PATH.
                ECHO Please install Node.js to use the MCP server.
                ECHO The game will start without MCP server support.
            ) ELSE (
                ECHO Node.js found. Checking MCP server directory...
                
                SET FULL_SERVER_PATH=%BASE_PATH%%mcp_server_path%
                IF NOT EXIST "!FULL_SERVER_PATH!" (
                    ECHO ERROR: MCP server directory not found at !FULL_SERVER_PATH!
                    ECHO The game will start without MCP server support.
                ) ELSE (
                    ECHO Starting MCP server from !FULL_SERVER_PATH!...
                    
                    REM Set environment variables for the MCP server
                    SET PORT=%mcp_port%
                    
                    REM Create .env file if it doesn't exist
                    IF NOT EXIST "!FULL_SERVER_PATH!\.env" (
                        ECHO Creating .env file for MCP server...
                        ECHO PORT=%mcp_port%> "!FULL_SERVER_PATH!\.env"
                        ECHO NODE_ENV=production>> "!FULL_SERVER_PATH!\.env"
                    )
                    
                    REM Start the MCP server in a new window
                    CD /D "!FULL_SERVER_PATH!"
                    START "Angband MCP Server" /MIN cmd /c "node mcp-server.js"
                    CD /D "%BASE_PATH%"
                    
                    ECHO MCP server started on port %mcp_port%.
                    ECHO Waiting for server to initialize...
                    TIMEOUT /T 2 /NOBREAK >NUL
                )
            )
        ) ELSE (
            ECHO MCP server autostart is disabled in configuration.
        )
    ) ELSE (
        ECHO MCP server is disabled in configuration.
    )
)

REM Check for SDL2 configuration file
IF NOT EXIST "%SDL2_CONFIG_PATH%" (
    ECHO SDL2 configuration file not found.
    ECHO The game will generate an optimized configuration based on your screen resolution.
)

REM Read graphics settings
CALL :ReadINI "%CONFIG_FILE%" "WINDOW_PREFERENCES" "use_graphics" use_graphics
CALL :ReadINI "%CONFIG_FILE%" "WINDOW_PREFERENCES" "graphics_mode" graphics_mode
CALL :ReadINI "%CONFIG_FILE%" "WINDOW_PREFERENCES" "fullscreen" fullscreen

REM Set defaults if values are missing
IF "%use_graphics%"=="" SET use_graphics=true
IF "%graphics_mode%"=="" SET graphics_mode=3
IF "%fullscreen%"=="" SET fullscreen=true

REM Set graphics flag based on configuration
SET GRAPHICS_FLAG=
IF /I "%use_graphics%"=="true" (
    IF NOT "%graphics_mode%"=="" (
        SET GRAPHICS_FLAG=-mgcu:%graphics_mode%
    )
)

REM Read debug mode setting
CALL :ReadINI "%CONFIG_FILE%" "ADVANCED" "debug_mode" debug_mode

REM Set debug flag based on configuration
SET DEBUG_FLAG=
IF /I "%debug_mode%"=="true" (
    SET DEBUG_FLAG=-d
)

REM Skip game start in test mode
IF "%TEST_MODE%"=="true" (
    ECHO Test mode active - skipping game launch.
    ECHO Configuration file created and settings loaded successfully.
    GOTO :EOF
)

REM Start the game
ECHO.
ECHO Starting Ages of Arda...
ECHO.
START "" angband.exe %GRAPHICS_FLAG% %DEBUG_FLAG%

GOTO :EOF

REM Function to read values from INI file
:ReadINI
SET file=%~1
SET section=%~2
SET key=%~3
SET return_var=%~4

SET %return_var%=
SET found_section=false

FOR /F "usebackq tokens=* delims=" %%A IN ("%file%") DO (
    SET line=%%A
    
    REM Remove leading/trailing spaces
    SET line=!line: =!
    
    REM Check if this is a section header
    IF "!line:~0,1!"=="[" (
        SET current_section=!line:~1,-1!
        IF /I "!current_section!"=="%section%" (
            SET found_section=true
        ) ELSE (
            SET found_section=false
        )
    ) ELSE (
        REM If we're in the right section, look for the key
        IF /I "!found_section!"=="true" (
            FOR /F "tokens=1,2 delims==" %%B IN ("!line!") DO (
                IF /I "%%B"=="%key%" (
                    SET %return_var%=%%C
                )
            )
        )
    )
)

EXIT /B 0 