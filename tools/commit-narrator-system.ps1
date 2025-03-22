# Narrator Personality System Commit Script
# This script automates the process of committing the narrator personality system changes

# Stop on errors
$ErrorActionPreference = "Stop"

Write-Host "Starting commit process for Narrator Personality System..." -ForegroundColor Cyan

# Check if we're on the development branch
$currentBranch = git rev-parse --abbrev-ref HEAD
if ($currentBranch -ne "development") {
    Write-Host "WARNING: Currently on branch $currentBranch, switching to development..." -ForegroundColor Yellow
    git checkout development
    if ($LASTEXITCODE -ne 0) {
        Write-Host "ERROR: Failed to switch to development branch. Aborting." -ForegroundColor Red
        exit 1
    }
}

# Stage the GitHub commit standards rule
Write-Host "Adding GitHub commit standards rule..." -ForegroundColor Green
git add .cursor/rules/infrastructure/github-commit.mdc
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Failed to add GitHub commit standards rule. Aborting." -ForegroundColor Red
    exit 1
}

# Stage the narrative system files
Write-Host "Adding Narrator Personality System files..." -ForegroundColor Green

# Narrative core system
git add BrogueMCP/dm-agent/narrative/narrator.js
git add BrogueMCP/dm-agent/narrative/settings.js
git add BrogueMCP/dm-agent/narrative/generator.js

# UI components
git add BrogueMCP/dm-agent/public/narrator.html
git add BrogueMCP/dm-agent/public/css/narrator.css
git add BrogueMCP/dm-agent/public/images/parchment-texture.jpg
git add BrogueMCP/dm-agent/public/images/parchment-background.jpg

# Server components
git add BrogueMCP/dm-agent/server/server.js

# C integration
git add BrogueMCP/src/mcp/dm_main.c

# Documentation
git add BrogueMCP/dm-agent/README-NARRATOR.md
git add BrogueMCP/dm-agent/IMPLEMENTATION-SUMMARY.md

# Check if all the files were added successfully
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Failed to add some files. Please check the errors above. Aborting." -ForegroundColor Red
    exit 1
}

# Create the commit message
$commitTitle = "[BrogueMCP] Add narrator personality system"
$commitBody = @"
Implements a configurable narrator personality system for the Dungeon Master AI:
- Adds personality attributes and presets (Gandalf, Galadriel, Aragorn)
- Creates web-based UI for adjusting narrator voice
- Integrates with prompt generation system
- Adds 'N' key binding to access settings in-game

The system allows players to customize the storytelling style during gameplay
with fine-grained control over voice tone, wisdom level, thematic elements,
and speech patterns. The system significantly enhances the narrative experience
by making the AI-generated content more personalized and engaging.

Related updates:
- Added GitHub commit standards rule for better contribution workflow
- Implemented detailed documentation for the narrator system
"@

# Commit the changes
Write-Host "Committing changes with message: $commitTitle" -ForegroundColor Green
git commit -m "$commitTitle" -m "$commitBody"
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Failed to commit changes. Aborting." -ForegroundColor Red
    exit 1
}

Write-Host "SUCCESS: Changes committed successfully!" -ForegroundColor Green
Write-Host "NEXT: To push the changes, run: git push origin development" -ForegroundColor Cyan 