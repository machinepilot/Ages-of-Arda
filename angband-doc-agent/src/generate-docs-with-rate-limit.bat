@echo off
REM Angband Documentation Generator with Rate Limiting
REM This script runs the documentation generator with settings to avoid rate limits

echo Angband Documentation Generator with Rate Limiting
echo ==============================================

REM Set parameters for rate limiting
set DELAY_BETWEEN_FILES=60
set BATCH_SIZE=5

REM Check if we should resume from a checkpoint
if exist doc_generator_checkpoint.json (
    echo Checkpoint found. Resuming from previous run.
    set RESUME_FLAG=--resume
) else (
    echo No checkpoint found. Starting a new run.
    set RESUME_FLAG=
)

echo Running documentation generator with:
echo - Delay between files: %DELAY_BETWEEN_FILES% seconds
echo - Batch size: %BATCH_SIZE% files
echo - Resume: %RESUME_FLAG%
echo.
echo This configuration is designed to avoid rate limits while ensuring all files are processed.
echo The process will automatically save checkpoints and can be resumed if interrupted.
echo.
echo Press Ctrl+C to stop the process at any time. You can resume later using this same script.
echo.
echo Starting in 5 seconds...
timeout /t 5

python document-angband.py --delay %DELAY_BETWEEN_FILES% --batch-size %BATCH_SIZE% %RESUME_FLAG%

echo.
if %ERRORLEVEL% EQU 0 (
    echo Documentation generation completed successfully!
) else (
    echo Documentation generation was interrupted or encountered an error.
    echo You can resume the process by running this script again.
)

pause 