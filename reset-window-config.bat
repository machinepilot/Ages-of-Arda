@echo off
SETLOCAL EnableDelayedExpansion

REM *** Ages of Arda Window Configuration Utility ***
REM This script helps reset or configure the window layout for Ages of Arda

REM Set base paths
SET BASE_PATH=%~dp0
SET CONFIG_FILE=%BASE_PATH%mcp_config.ini
SET SDL2_CONFIG_PATH=%BASE_PATH%lib\user\sdl2init.txt

ECHO.
ECHO *** Ages of Arda - Window Configuration Utility ***
ECHO.

REM Display menu
ECHO Choose an option:
ECHO 1. Reset window configuration (regenerate based on screen resolution)
ECHO 2. Toggle fullscreen mode
ECHO 3. Backup current configuration
ECHO 4. Restore from backup
ECHO 5. Exit
ECHO.

SET /P CHOICE=Enter your choice (1-5): 

IF "%CHOICE%"=="1" (
    CALL :ResetConfig
) ELSE IF "%CHOICE%"=="2" (
    CALL :ToggleFullscreen
) ELSE IF "%CHOICE%"=="3" (
    CALL :BackupConfig
) ELSE IF "%CHOICE%"=="4" (
    CALL :RestoreBackup
) ELSE IF "%CHOICE%"=="5" (
    ECHO Exiting...
    GOTO :EOF
) ELSE (
    ECHO Invalid choice.
    GOTO :EOF
)

ECHO.
ECHO Configuration utility completed.
ECHO You can now start the game with the new settings.
ECHO.

PAUSE
GOTO :EOF

REM Function to reset the window configuration
:ResetConfig
ECHO Resetting window configuration...

IF EXIST "%SDL2_CONFIG_PATH%" (
    DEL "%SDL2_CONFIG_PATH%"
    ECHO Deleted existing SDL2 configuration.
)

ECHO Configuration will be regenerated when you next start the game.
ECHO To start the game with the new configuration, run: start-ages-of-arda.bat

EXIT /B 0

REM Function to toggle fullscreen mode
:ToggleFullscreen
ECHO Checking current fullscreen setting...

SET FULLSCREEN_VALUE=
IF EXIST "%CONFIG_FILE%" (
    CALL :ReadINI "%CONFIG_FILE%" "WINDOW_PREFERENCES" "fullscreen" FULLSCREEN_VALUE
)

IF /I "%FULLSCREEN_VALUE%"=="true" (
    ECHO Changing to windowed mode...
    CALL :UpdateConfigValue "WINDOW_PREFERENCES" "fullscreen" "false"
) ELSE (
    ECHO Changing to fullscreen mode...
    CALL :UpdateConfigValue "WINDOW_PREFERENCES" "fullscreen" "true"
)

ECHO Fullscreen setting updated. 
ECHO The new setting will apply the next time you start the game.

EXIT /B 0

REM Function to backup the current configuration
:BackupConfig
ECHO Backing up configuration files...

SET TIMESTAMP=%date:~10,4%%date:~4,2%%date:~7,2%_%time:~0,2%%time:~3,2%%time:~6,2%
SET TIMESTAMP=%TIMESTAMP: =0%

IF EXIST "%SDL2_CONFIG_PATH%" (
    COPY "%SDL2_CONFIG_PATH%" "%SDL2_CONFIG_PATH%.bak.%TIMESTAMP%" > NUL
    ECHO Backed up SDL2 configuration to %SDL2_CONFIG_PATH%.bak.%TIMESTAMP%
) ELSE (
    ECHO No SDL2 configuration file found to backup.
)

IF EXIST "%CONFIG_FILE%" (
    COPY "%CONFIG_FILE%" "%CONFIG_FILE%.bak.%TIMESTAMP%" > NUL
    ECHO Backed up MCP configuration to %CONFIG_FILE%.bak.%TIMESTAMP%
) ELSE (
    ECHO No MCP configuration file found to backup.
)

EXIT /B 0

REM Function to restore from backup
:RestoreBackup
ECHO Available backups:
ECHO.

SET BACKUPS_FOUND=false

SET COUNT=0
FOR /F "tokens=*" %%F IN ('DIR /B "%SDL2_CONFIG_PATH%.bak.*" 2^>NUL') DO (
    SET /A COUNT+=1
    SET "BACKUP!COUNT!=%%F"
    ECHO !COUNT!. %%F
    SET BACKUPS_FOUND=true
)

IF "%BACKUPS_FOUND%"=="false" (
    ECHO No backups found.
    EXIT /B 1
)

ECHO.
SET /P BACKUP_CHOICE=Enter the number of the backup to restore: 

SET SELECTED_BACKUP=!BACKUP%BACKUP_CHOICE%!

IF NOT DEFINED SELECTED_BACKUP (
    ECHO Invalid selection.
    EXIT /B 1
)

COPY "%SDL2_CONFIG_PATH%.bak.%SELECTED_BACKUP:~-19%" "%SDL2_CONFIG_PATH%" > NUL
ECHO Restored configuration from backup.

EXIT /B 0

REM Function to update a value in the INI file
:UpdateConfigValue
SET section=%~1
SET key=%~2
SET value=%~3
SET tempfile=%TEMP%\temp_config.ini
SET found_section=false
SET updated=false

IF NOT EXIST "%CONFIG_FILE%" (
    ECHO Configuration file does not exist: %CONFIG_FILE%
    EXIT /B 1
)

(
    FOR /F "usebackq tokens=* delims=" %%A IN ("%CONFIG_FILE%") DO (
        SET line=%%A
        
        REM Check if this is a section header
        SET first_char=!line:~0,1!
        IF "!first_char!"=="[" (
            ECHO !line!
            SET current_section=!line:~1,-1!
            IF /I "!current_section!"=="%section%" (
                SET found_section=true
            ) ELSE (
                SET found_section=false
            )
        ) ELSE (
            REM If we're in the right section, look for the key
            IF /I "!found_section!"=="true" (
                FOR /F "tokens=1,* delims==" %%B IN ("!line!") DO (
                    IF /I "%%B"=="%key%" (
                        ECHO %key%=%value%
                        SET updated=true
                    ) ELSE (
                        ECHO !line!
                    )
                )
            ) ELSE (
                ECHO !line!
            )
        )
    )
    
    REM If we didn't find and update the key, add it to the section
    IF /I "%updated%"=="false" (
        REM Look through the file again to find the section end
        SET found_section=false
        SET end_of_section=false
        
        FOR /F "usebackq tokens=* delims=" %%A IN ("%CONFIG_FILE%") DO (
            SET line=%%A
            SET first_char=!line:~0,1!
            
            IF "!first_char!"=="[" (
                IF /I "!found_section!"=="true" (
                    IF /I "!end_of_section!"=="false" (
                        ECHO %key%=%value%
                        SET end_of_section=true
                    )
                )
                
                IF /I "!line:~1,-1!"=="%section%" (
                    SET found_section=true
                ) ELSE (
                    SET found_section=false
                )
            )
        )
        
        REM If we're at the end of file and still haven't added the key
        IF /I "!found_section!"=="true" (
            IF /I "!end_of_section!"=="false" (
                ECHO %key%=%value%
            )
        )
    )
) > "%tempfile%"

MOVE /Y "%tempfile%" "%CONFIG_FILE%" > NUL

EXIT /B 0

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