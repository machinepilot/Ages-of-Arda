#!/bin/bash

# *** Ages of Arda Window Configuration Utility ***
# This script helps reset or configure the window layout for Ages of Arda

# Set base paths
BASE_PATH="$(dirname "$(readlink -f "$0")")/"
CONFIG_FILE="$BASE_PATH/mcp_config.ini"
SDL2_CONFIG_PATH="$BASE_PATH/lib/user/sdl2init.txt"

echo
echo "*** Ages of Arda - Window Configuration Utility ***"
echo

# Function to read values from INI file
read_ini() {
    local file=$1
    local section=$2
    local key=$3
    local value=$(awk -F= '/^\['"$section"'\]/{flag=1; next} /^\[/{flag=0} flag && $1=="'"$key"'" {print $2}' "$file")
    echo "$value"
}

# Function to update a value in the INI file
update_config_value() {
    local section=$1
    local key=$2
    local value=$3
    local tempfile=$(mktemp)
    local found_section=false
    local updated=false
    
    if [ ! -f "$CONFIG_FILE" ]; then
        echo "Configuration file does not exist: $CONFIG_FILE"
        return 1
    fi
    
    while IFS= read -r line; do
        # Check if this is a section header
        if [[ $line =~ ^\[(.*)\]$ ]]; then
            echo "$line" >> "$tempfile"
            section_name="${BASH_REMATCH[1]}"
            if [[ $section_name == $section ]]; then
                found_section=true
            else
                found_section=false
            fi
        else
            # If we're in the right section, look for the key
            if [[ $found_section == true ]]; then
                if [[ $line =~ ^$key= ]]; then
                    echo "$key=$value" >> "$tempfile"
                    updated=true
                else
                    echo "$line" >> "$tempfile"
                fi
            else
                echo "$line" >> "$tempfile"
            fi
        fi
    done < "$CONFIG_FILE"
    
    # If we didn't find and update the key, add it to the section
    if [[ $updated != true ]]; then
        # We need to go through the file again to find where the section ends
        found_section=false
        end_of_section=false
        tempfile2=$(mktemp)
        
        while IFS= read -r line; do
            echo "$line" >> "$tempfile2"
            
            if [[ $line =~ ^\[(.*)\]$ ]]; then
                section_name="${BASH_REMATCH[1]}"
                if [[ $found_section == true && $end_of_section != true ]]; then
                    # We just hit a new section after our target section
                    echo "$key=$value" >> "$tempfile2"
                    end_of_section=true
                fi
                
                if [[ $section_name == $section ]]; then
                    found_section=true
                else
                    found_section=false
                fi
            fi
        done < "$tempfile"
        
        # If we're at the end of the file and still haven't added the key
        if [[ $found_section == true && $end_of_section != true ]]; then
            echo "$key=$value" >> "$tempfile2"
        fi
        
        mv "$tempfile2" "$tempfile"
    fi
    
    # Replace the original file with our modified version
    mv "$tempfile" "$CONFIG_FILE"
}

# Function to reset the window configuration
reset_config() {
    echo "Resetting window configuration..."
    
    if [ -f "$SDL2_CONFIG_PATH" ]; then
        rm "$SDL2_CONFIG_PATH"
        echo "Deleted existing SDL2 configuration."
    fi
    
    echo "Configuration will be regenerated when you next start the game."
    echo "To start the game with the new configuration, run: ./start-ages-of-arda.sh"
}

# Function to toggle fullscreen mode
toggle_fullscreen() {
    echo "Checking current fullscreen setting..."
    
    if [ -f "$CONFIG_FILE" ]; then
        FULLSCREEN_VALUE=$(read_ini "$CONFIG_FILE" "WINDOW_PREFERENCES" "fullscreen")
    fi
    
    if [ "$FULLSCREEN_VALUE" = "true" ]; then
        echo "Changing to windowed mode..."
        update_config_value "WINDOW_PREFERENCES" "fullscreen" "false"
    else
        echo "Changing to fullscreen mode..."
        update_config_value "WINDOW_PREFERENCES" "fullscreen" "true"
    fi
    
    echo "Fullscreen setting updated."
    echo "The new setting will apply the next time you start the game."
}

# Function to backup the current configuration
backup_config() {
    echo "Backing up configuration files..."
    
    TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
    
    if [ -f "$SDL2_CONFIG_PATH" ]; then
        cp "$SDL2_CONFIG_PATH" "$SDL2_CONFIG_PATH.bak.$TIMESTAMP"
        echo "Backed up SDL2 configuration to $SDL2_CONFIG_PATH.bak.$TIMESTAMP"
    else
        echo "No SDL2 configuration file found to backup."
    fi
    
    if [ -f "$CONFIG_FILE" ]; then
        cp "$CONFIG_FILE" "$CONFIG_FILE.bak.$TIMESTAMP"
        echo "Backed up MCP configuration to $CONFIG_FILE.bak.$TIMESTAMP"
    else
        echo "No MCP configuration file found to backup."
    fi
}

# Function to restore from backup
restore_backup() {
    echo "Available backups:"
    echo
    
    # Find SDL2 config backups
    BACKUPS=($(find "$BASE_PATH" -name "$(basename "$SDL2_CONFIG_PATH").bak.*" | sort -r))
    
    if [ ${#BACKUPS[@]} -eq 0 ]; then
        echo "No backups found."
        return 1
    fi
    
    # Display available backups
    for i in "${!BACKUPS[@]}"; do
        echo "$((i+1)). $(basename "${BACKUPS[$i]}")"
    done
    
    echo
    read -p "Enter the number of the backup to restore: " BACKUP_CHOICE
    
    # Validate input
    if ! [[ "$BACKUP_CHOICE" =~ ^[0-9]+$ ]] || [ "$BACKUP_CHOICE" -lt 1 ] || [ "$BACKUP_CHOICE" -gt ${#BACKUPS[@]} ]; then
        echo "Invalid selection."
        return 1
    fi
    
    # Get the selected backup
    SELECTED_BACKUP="${BACKUPS[$((BACKUP_CHOICE-1))]}"
    
    # Restore the backup
    cp "$SELECTED_BACKUP" "$SDL2_CONFIG_PATH"
    echo "Restored configuration from backup."
}

# Display menu
echo "Choose an option:"
echo "1. Reset window configuration (regenerate based on screen resolution)"
echo "2. Toggle fullscreen mode"
echo "3. Backup current configuration"
echo "4. Restore from backup"
echo "5. Exit"
echo

read -p "Enter your choice (1-5): " CHOICE

case $CHOICE in
    1)
        reset_config
        ;;
    2)
        toggle_fullscreen
        ;;
    3)
        backup_config
        ;;
    4)
        restore_backup
        ;;
    5)
        echo "Exiting..."
        exit 0
        ;;
    *)
        echo "Invalid choice."
        exit 1
        ;;
esac

echo
echo "Configuration utility completed."
echo "You can now start the game with the new settings."
echo

read -p "Press Enter to continue..." 