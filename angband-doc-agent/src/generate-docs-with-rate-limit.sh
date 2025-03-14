#!/bin/bash
# Angband Documentation Generator with Rate Limiting
# This script runs the documentation generator with settings to avoid rate limits

echo "Angband Documentation Generator with Rate Limiting"
echo "=============================================="

# Set parameters for rate limiting
DELAY_BETWEEN_FILES=60
BATCH_SIZE=5

# Check if we should resume from a checkpoint
if [ -f "doc_generator_checkpoint.json" ]; then
    echo "Checkpoint found. Resuming from previous run."
    RESUME_FLAG="--resume"
else
    echo "No checkpoint found. Starting a new run."
    RESUME_FLAG=""
fi

echo "Running documentation generator with:"
echo "- Delay between files: $DELAY_BETWEEN_FILES seconds"
echo "- Batch size: $BATCH_SIZE files"
echo "- Resume: $RESUME_FLAG"
echo ""
echo "This configuration is designed to avoid rate limits while ensuring all files are processed."
echo "The process will automatically save checkpoints and can be resumed if interrupted."
echo ""
echo "Press Ctrl+C to stop the process at any time. You can resume later using this same script."
echo ""
echo "Starting in 5 seconds..."
sleep 5

python3 document-angband.py --delay $DELAY_BETWEEN_FILES --batch-size $BATCH_SIZE $RESUME_FLAG

echo ""
if [ $? -eq 0 ]; then
    echo "Documentation generation completed successfully!"
else
    echo "Documentation generation was interrupted or encountered an error."
    echo "You can resume the process by running this script again."
fi

read -p "Press Enter to continue..." 