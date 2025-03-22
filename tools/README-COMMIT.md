# Commit Scripts

This directory contains scripts to automate the Git commit process for different features in the Ages of Arda project.

## Narrator Personality System Commit

The following scripts automate the process of committing the narrator personality system for the BrogueMCP module:

- `commit-narrator-system.ps1` - PowerShell script for Windows
- `commit-narrator-system.sh` - Bash script for Linux/macOS

### How to Use

#### Windows

```powershell
# Navigate to the root of the repository
cd path/to/ages-of-arda

# Run the PowerShell script
.\tools\commit-narrator-system.ps1
```

#### Linux/macOS

```bash
# Navigate to the root of the repository
cd path/to/ages-of-arda

# Ensure the script is executable
chmod +x tools/commit-narrator-system.sh

# Run the bash script
./tools/commit-narrator-system.sh
```

### What the Scripts Do

1. Check if you're on the development branch (and switch to it if necessary)
2. Add the GitHub commit standards rule
3. Add all the narrator personality system files:
   - Core system files (narrator.js, settings.js, generator.js)
   - UI components (HTML, CSS, image assets)
   - Server components (API endpoints)
   - C code integration (key binding)
   - Documentation
4. Create a properly formatted commit message
5. Commit the changes

### After Running the Script

After successfully running the script, you'll need to push your changes:

```bash
git push origin development
```

## Creating Your Own Commit Scripts

To create commit scripts for other features:

1. Copy one of the existing scripts as a template
2. Update the list of files to include in the commit
3. Modify the commit message to accurately describe the changes
4. Run the script when you're ready to commit

## Integration with Cursor

The commit scripts work alongside the GitHub Commit Standards cursor rule (`.cursor/rules/infrastructure/github-commit.mdc`), which provides guidance on creating proper commit messages when using the Cursor editor. 