#!/bin/bash
# Create Desktop Launcher for Angband with MCP
# This script creates a desktop launcher icon for Angband with MCP integration

# Set the current directory as the base path
BASE_PATH="$(cd "$(dirname "$0")" && pwd)"
DESKTOP_DIR="$HOME/Desktop"
APPLICATIONS_DIR="$HOME/.local/share/applications"

echo "Creating desktop launcher for Angband with MCP..."

# Create desktop entry file
create_desktop_entry() {
    local output_dir=$1
    local filename="angband-mcp.desktop"
    local filepath="$output_dir/$filename"
    
    cat > "$filepath" << EOF
[Desktop Entry]
Version=1.0
Type=Application
Name=Angband with MCP
Comment=Play Angband with Model Context Protocol integration
Exec=$BASE_PATH/start-angband.sh
Icon=$BASE_PATH/lib/icons/angband.png
Terminal=false
Categories=Game;RolePlaying;
Keywords=roguelike;rpg;dungeon;
EOF
    
    chmod +x "$filepath"
    echo "Created desktop entry at: $filepath"
}

# Check if the icons directory exists, create default icon if not
if [ ! -d "$BASE_PATH/lib/icons" ]; then
    mkdir -p "$BASE_PATH/lib/icons"
    
    # Create a simple text-based icon if no icon exists
    if [ ! -f "$BASE_PATH/lib/icons/angband.png" ]; then
        echo "No icon found, attempting to create a placeholder..."
        
        # Check if convert (ImageMagick) is available
        if command -v convert &> /dev/null; then
            convert -size 128x128 -background black -fill white -font Helvetica -pointsize 20 \
                    label:"Angband\nMCP" "$BASE_PATH/lib/icons/angband.png"
            echo "Created placeholder icon."
        else
            echo "ImageMagick not found. No icon was created."
            echo "Please add an icon manually at: $BASE_PATH/lib/icons/angband.png"
        fi
    fi
fi

# Make sure start-angband.sh is executable
if [ -f "$BASE_PATH/start-angband.sh" ]; then
    chmod +x "$BASE_PATH/start-angband.sh"
else
    echo "Error: start-angband.sh not found in $BASE_PATH"
    echo "Please make sure the startup script exists before creating a desktop launcher."
    exit 1
fi

# Create desktop entry in user's desktop directory
if [ -d "$DESKTOP_DIR" ]; then
    create_desktop_entry "$DESKTOP_DIR"
else
    echo "Desktop directory not found at: $DESKTOP_DIR"
fi

# Create desktop entry in applications directory
mkdir -p "$APPLICATIONS_DIR"
create_desktop_entry "$APPLICATIONS_DIR"

echo "Desktop launcher creation complete!"
echo ""
echo "You can now launch Angband with MCP from your application menu"
echo "or by double-clicking the icon on your desktop (if available)." 