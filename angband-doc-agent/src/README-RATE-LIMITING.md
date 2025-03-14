# Angband Documentation Generator with Rate Limiting

This README explains how to use the rate-limited documentation generator to avoid hitting API rate limits while ensuring all files are processed.

## The Problem

The Anthropic API has a rate limit of 2,000 output tokens per minute. When generating documentation for many files in quick succession, we can hit this limit, resulting in errors like:

```
Error code: 429 - Rate limit exceeded. For details, refer to: https://docs.anthropic.com/en/api/rate-limits.
```

## The Solution

The enhanced documentation generator includes:

1. **Rate limiting** - Adds configurable delays between file processing
2. **Checkpointing** - Saves progress regularly so you can resume if interrupted
3. **Batch processing** - Processes files in small batches with checkpoints between batches
4. **Retry mechanism** - Automatically retries with exponential backoff when rate limits are hit
5. **Progress tracking** - Shows estimated completion time and progress

## How to Use

### On Windows

Run the batch script:

```
generate-docs-with-rate-limit.bat
```

### On Unix-like Systems (Linux, macOS)

Make the script executable (if not already):

```
chmod +x generate-docs-with-rate-limit.sh
```

Then run it:

```
./generate-docs-with-rate-limit.sh
```

## Configuration

The scripts use these default settings:

- **Delay between files**: 60 seconds (to stay well under the rate limit)
- **Batch size**: 5 files (small batches ensure frequent checkpoints)

You can modify these values in the scripts if needed.

## Command Line Options

If you want to run the Python script directly with custom options:

```
python document-angband.py --delay 60 --batch-size 5 [other options]
```

Available options:

- `--delay SECONDS`: Delay between processing files (default: 30)
- `--batch-size N`: Number of files to process before saving a checkpoint (default: 10)
- `--resume`: Resume from the last checkpoint
- `--max-files N`: Process only N files (useful for testing)
- `--file PATH`: Process only a specific file
- `--module PATH`: Process only files in a specific module/directory

## Resuming After Interruption

If the process is interrupted (by error, power outage, or manual cancellation), simply run the script again. It will automatically detect the checkpoint file and resume from where it left off.

## Estimated Completion Time

The script will provide an estimated completion time at the start and update it after each batch. This helps you plan accordingly for long-running processes.

## Troubleshooting

### Rate Limits Still Occurring

If you're still hitting rate limits:

1. Increase the `--delay` parameter (try 90 or 120 seconds)
2. Decrease the `--batch-size` parameter (try 3 or even 1)

### Process Taking Too Long

If the process is taking too long:

1. You can safely interrupt it and resume later
2. Consider processing only specific modules or directories using the `--module` option
3. Process Windows files separately with `--windows-only`

## Example: Processing Only Core Files

```
python document-angband.py --delay 60 --batch-size 5 --module src/core
```

This will process only files in the `src/core` directory, making the task more manageable. 