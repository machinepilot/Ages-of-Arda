@echo off
REM Create Desktop Shortcut for Angband with MCP
REM This script creates a Windows shortcut for Angband with MCP integration

echo ===============================================================
echo Creating desktop shortcut for Angband with MCP...
echo ===============================================================

REM Get the current directory as the base path
set BASE_PATH=%~dp0
set DESKTOP_PATH=%USERPROFILE%\Desktop

REM Create VBScript to generate shortcut
echo Creating shortcut generator script...
set VBS_PATH=%TEMP%\create_angband_shortcut.vbs

echo Set oWS = WScript.CreateObject("WScript.Shell") > %VBS_PATH%
echo sLinkFile = "%DESKTOP_PATH%\Angband with MCP.lnk" >> %VBS_PATH%
echo Set oLink = oWS.CreateShortcut(sLinkFile) >> %VBS_PATH%
echo oLink.TargetPath = "%BASE_PATH%start-angband.bat" >> %VBS_PATH%
echo oLink.WorkingDirectory = "%BASE_PATH%" >> %VBS_PATH%
echo oLink.Description = "Play Angband with Model Context Protocol integration" >> %VBS_PATH%
echo oLink.IconLocation = "%BASE_PATH%lib\icons\angband.ico, 0" >> %VBS_PATH%
echo oLink.Save >> %VBS_PATH%

REM Check if icon directory exists, create if not
if not exist "%BASE_PATH%lib\icons" (
    echo Creating icons directory...
    mkdir "%BASE_PATH%lib\icons"
)

REM Check if icon file exists
if not exist "%BASE_PATH%lib\icons\angband.ico" (
    echo No icon found. Shortcut will use default icon.
    echo You can add a custom icon at: %BASE_PATH%lib\icons\angband.ico
)

REM Run the VBScript to create the shortcut
echo Creating desktop shortcut...
cscript //NoLogo %VBS_PATH%

REM Check if shortcut was created successfully
if exist "%DESKTOP_PATH%\Angband with MCP.lnk" (
    echo Desktop shortcut created successfully!
) else (
    echo Failed to create desktop shortcut. Please check for errors.
)

REM Clean up the temporary VBScript
del %VBS_PATH%

REM Create Start Menu shortcut
echo Creating Start Menu shortcut...
set START_MENU_DIR=%APPDATA%\Microsoft\Windows\Start Menu\Programs\Games
if not exist "%START_MENU_DIR%" (
    mkdir "%START_MENU_DIR%"
)

set VBS_PATH=%TEMP%\create_angband_start_menu.vbs
echo Set oWS = WScript.CreateObject("WScript.Shell") > %VBS_PATH%
echo sLinkFile = "%START_MENU_DIR%\Angband with MCP.lnk" >> %VBS_PATH%
echo Set oLink = oWS.CreateShortcut(sLinkFile) >> %VBS_PATH%
echo oLink.TargetPath = "%BASE_PATH%start-angband.bat" >> %VBS_PATH%
echo oLink.WorkingDirectory = "%BASE_PATH%" >> %VBS_PATH%
echo oLink.Description = "Play Angband with Model Context Protocol integration" >> %VBS_PATH%
echo oLink.IconLocation = "%BASE_PATH%lib\icons\angband.ico, 0" >> %VBS_PATH%
echo oLink.Save >> %VBS_PATH%

cscript //NoLogo %VBS_PATH%

REM Clean up the temporary VBScript
del %VBS_PATH%

echo ===============================================================
echo Shortcut creation complete!
echo ===============================================================
echo.
echo You can now launch Angband with MCP by:
echo - Double-clicking the shortcut on your desktop
echo - Using the Start Menu under Games
echo.
echo Press any key to exit...
pause > nul 