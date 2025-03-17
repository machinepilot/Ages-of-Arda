@echo off
REM Build script for testing the SDL2 configuration generator

echo Building test-config-generator...
gcc -o test-config-generator.exe src/test-config-generator.c src/sdl2-config-generator.c -I./src -I./include -L./lib -lSDL2 -lSDL2_image -lSDL2_ttf -DUSE_SDL2

if %ERRORLEVEL% NEQ 0 (
    echo Build failed with error code %ERRORLEVEL%
    exit /b %ERRORLEVEL%
) else (
    echo Build successful!
    echo.
    echo Running test-config-generator...
    echo.
    test-config-generator.exe
) 