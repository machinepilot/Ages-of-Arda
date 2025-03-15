#!/bin/bash
# Angband Startup Script with MCP Server
# This script launches both the MCP server and Angband game

# Set the current directory as the base path
BASE_PATH="$(cd "$(dirname "$0")" && pwd)"
CONFIG_FILE="$BASE_PATH/mcp_config.ini"

echo "======================================================="
echo "Angband Startup with MCP Server Integration"
echo "======================================================="

# Function to read INI values
read_ini() {
    local file=$1
    local section=$2
    local key=$3
    
    # Get the value from the INI file
    value=$(grep -A 100 "^\[$section\]" "$file" | grep -m 1 "^$key=" | cut -d '=' -f 2- | sed 's/;.*$//' | tr -d ' ')
    echo "$value"
}

# Check if the config file exists
if [ ! -f "$CONFIG_FILE" ]; then
    echo "Configuration file not found: $CONFIG_FILE"
    echo "Creating default configuration file..."
    
    if [ -f "$BASE_PATH/lib/customize/mcp_config_default.ini" ]; then
        cp "$BASE_PATH/lib/customize/mcp_config_default.ini" "$CONFIG_FILE"
    else
        echo "Default configuration file not found!"
        echo "Please create a configuration file: $CONFIG_FILE"
        exit 1
    fi
fi

# Read MCP server configuration
MCP_ENABLED=$(read_ini "$CONFIG_FILE" "MCP_SERVER" "enabled")
MCP_AUTOSTART=$(read_ini "$CONFIG_FILE" "MCP_SERVER" "autostart")
MCP_SERVER_PATH=$(read_ini "$CONFIG_FILE" "MCP_SERVER" "server_path")
MCP_PORT=$(read_ini "$CONFIG_FILE" "MCP_SERVER" "port")

echo "Configuration loaded successfully."

# Start MCP server if enabled and autostart is true
if [ "$MCP_ENABLED" = "true" ] && [ "$MCP_AUTOSTART" = "true" ]; then
    echo "Starting MCP server on port $MCP_PORT..."
    
    # Check if Node.js is installed
    if ! command -v node &> /dev/null; then
        echo "Node.js is not installed."
        echo "Please install Node.js to use the MCP server."
    else
        # Convert to absolute path if necessary
        if [[ "$MCP_SERVER_PATH" != /* ]]; then
            MCP_SERVER_PATH="$BASE_PATH/$MCP_SERVER_PATH"
        fi
        
        # Check if server directory exists
        if [ ! -d "$MCP_SERVER_PATH" ]; then
            echo "MCP server directory not found: $MCP_SERVER_PATH"
        else
            # Check if server is already running on the specified port
            if netstat -tuln 2>/dev/null | grep -q ":$MCP_PORT "; then
                echo "MCP server is already running on port $MCP_PORT."
            else
                # Start the MCP server in the background
                cd "$MCP_SERVER_PATH"
                node mcp-server.js > "$BASE_PATH/mcp-server.log" 2>&1 &
                MCP_PID=$!
                
                # Wait for the server to start
                echo "Waiting for MCP server to start..."
                sleep 3
                
                # Verify server is running
                if kill -0 $MCP_PID 2>/dev/null; then
                    echo "MCP server started successfully (PID: $MCP_PID)."
                    # Store PID in a file for future reference
                    echo $MCP_PID > "$BASE_PATH/mcp-server.pid"
                else
                    echo "Warning: MCP server may not have started correctly."
                fi
                
                cd "$BASE_PATH"
            fi
        fi
    fi
fi

echo "Starting Angband..."

# Extract graphics settings
USE_GRAPHICS=$(read_ini "$CONFIG_FILE" "WINDOW_PREFERENCES" "use_graphics")
GRAPHICS_MODE=$(read_ini "$CONFIG_FILE" "WINDOW_PREFERENCES" "graphics_mode")

# Set graphics flags if enabled
GRAPHICS_FLAG=""
if [ "$USE_GRAPHICS" = "true" ]; then
    if [ "$GRAPHICS_MODE" = "old" ]; then
        GRAPHICS_FLAG="-g"
    elif [ "$GRAPHICS_MODE" = "new" ]; then
        GRAPHICS_FLAG="-gn"
    fi
fi

# Set debug mode if enabled
DEBUG_MODE=$(read_ini "$CONFIG_FILE" "ADVANCED" "debug_mode")
DEBUG_FLAG=""
if [ "$DEBUG_MODE" = "true" ]; then
    DEBUG_FLAG="-w"
fi

# Run Angband with the appropriate flags
if [ -f "$BASE_PATH/angband" ]; then
    "$BASE_PATH/angband" $GRAPHICS_FLAG $DEBUG_FLAG
else
    echo "Angband executable not found!"
    exit 1
fi

echo "Angband exited."

# Function to handle exit
cleanup() {
    # Terminate MCP server if it was started by this script
    if [ -f "$BASE_PATH/mcp-server.pid" ]; then
        MCP_PID=$(cat "$BASE_PATH/mcp-server.pid")
        if kill -0 $MCP_PID 2>/dev/null; then
            echo "Shutting down MCP server (PID: $MCP_PID)..."
            kill $MCP_PID
            rm "$BASE_PATH/mcp-server.pid"
        fi
    fi
    
    echo "Cleanup complete."
    exit 0
}

# Register cleanup function on script exit
trap cleanup EXIT 