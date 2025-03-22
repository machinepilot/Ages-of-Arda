#!/bin/bash
# Narrator Personality System Commit Script
# This script automates the process of committing the narrator personality system changes

# Stop on errors
set -e

echo -e "\033[1;36mStarting commit process for Narrator Personality System...\033[0m"

# Check if we're on the development branch
CURRENT_BRANCH=$(git rev-parse --abbrev-ref HEAD)
if [ "$CURRENT_BRANCH" != "development" ]; then
    echo -e "\033[1;33mWARNING: Currently on branch $CURRENT_BRANCH, switching to development...\033[0m"
    git checkout development
fi

# Stage the GitHub commit standards rule
echo -e "\033[1;32mAdding GitHub commit standards rule...\033[0m"
git add .cursor/rules/infrastructure/github-commit.mdc

# Stage the narrative system files
echo -e "\033[1;32mAdding Narrator Personality System files...\033[0m"

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

# Create the commit message
COMMIT_TITLE="[BrogueMCP] Add narrator personality system"
COMMIT_BODY="Implements a configurable narrator personality system for the Dungeon Master AI:
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
- Implemented detailed documentation for the narrator system"

# Commit the changes
echo -e "\033[1;32mCommitting changes with message: $COMMIT_TITLE\033[0m"
git commit -m "$COMMIT_TITLE" -m "$COMMIT_BODY"

echo -e "\033[1;32mSUCCESS: Changes committed successfully!\033[0m"
echo -e "\033[1;36mNEXT: To push the changes, run: git push origin development\033[0m" 