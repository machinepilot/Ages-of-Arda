# Setup environment for Tolkien ePub processing (Windows)

# Colors for pretty output
$GREEN = [ConsoleColor]::Green
$RED = [ConsoleColor]::Red
$YELLOW = [ConsoleColor]::Yellow

Write-Host "Setting up environment for Tolkien ePub processing..." -ForegroundColor $YELLOW

# Create necessary directories
Write-Host "Creating necessary directories..." -ForegroundColor $YELLOW
New-Item -ItemType Directory -Force -Path "processing\logs" | Out-Null
New-Item -ItemType Directory -Force -Path "processing\schemas\entity_lists" | Out-Null
New-Item -ItemType Directory -Force -Path "processing\temp" | Out-Null
New-Item -ItemType Directory -Force -Path "processing\epub_content" | Out-Null
New-Item -ItemType Directory -Force -Path "processing\json_output" | Out-Null
New-Item -ItemType Directory -Force -Path "processing\consolidated" | Out-Null
New-Item -ItemType Directory -Force -Path "processing\checkpoints" | Out-Null
New-Item -ItemType Directory -Force -Path ".memory-bank" | Out-Null

# Install Python dependencies
Write-Host "Installing Python dependencies..." -ForegroundColor $YELLOW
pip install -r processing\requirements.txt

# Check installation success
if ($LASTEXITCODE -eq 0) {
    Write-Host "Python dependencies installed successfully." -ForegroundColor $GREEN
} else {
    Write-Host "Failed to install Python dependencies. Exiting." -ForegroundColor $RED
    exit 1
}

# Run NLP setup
Write-Host "Running NLP setup..." -ForegroundColor $YELLOW
python processing\setup_nlp.py

# Check setup success
if ($LASTEXITCODE -eq 0) {
    Write-Host "NLP setup completed successfully." -ForegroundColor $GREEN
} else {
    Write-Host "NLP setup failed. Exiting." -ForegroundColor $RED
    exit 1
}

# Run setup tests
Write-Host "Running setup tests..." -ForegroundColor $YELLOW
python processing\test_setup.py

# Check test success
if ($LASTEXITCODE -eq 0) {
    Write-Host "Setup tests passed successfully." -ForegroundColor $GREEN
} else {
    Write-Host "Setup tests failed. Please check the output above." -ForegroundColor $RED
    exit 1
}

Write-Host "Environment setup completed successfully!" -ForegroundColor $GREEN
Write-Host "You can now run the Tolkien ePub processing pipeline." -ForegroundColor $GREEN 