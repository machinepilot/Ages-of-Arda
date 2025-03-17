#!/bin/bash

# *** Ages of Arda Startup Script ***
# This script starts both the MCP server and the Angband game with optimized window settings

# Set base paths
BASE_PATH="$(dirname "$(readlink -f "$0")")/"
CONFIG_FILE="$BASE_PATH/mcp_config.ini"
DEFAULT_CONFIG_PATH="$BASE_PATH/lib/customize/mcp_config_default.ini"
SDL2_CONFIG_PATH="$BASE_PATH/lib/user/sdl2init.txt"

# Display welcome message
echo
echo "*** Ages of Arda - First Age ***"
echo "*** Starting game environment..."
echo

# Function to read values from INI file
read_ini() {
    local file=$1
    local section=$2
    local key=$3
    local value=$(awk -F= '/^\['"$section"'\]/{flag=1; next} /^\[/{flag=0} flag && $1=="'"$key"'" {print $2}' "$file")
    echo "$value"
}

# Check for configuration file
if [ ! -f "$CONFIG_FILE" ]; then
    echo "Configuration file not found: $CONFIG_FILE"
    echo "Creating default configuration..."
    
    if [ -f "$DEFAULT_CONFIG_PATH" ]; then
        cp "$DEFAULT_CONFIG_PATH" "$CONFIG_FILE"
    else
        echo "ERROR: Default configuration file not found at $DEFAULT_CONFIG_PATH"
        echo "Creating basic configuration file..."
        
        cat > "$CONFIG_FILE" << EOF
[MCP_SERVER]
enabled=true
autostart=true
server_path=angband-doc-agent/src
port=3000
timeout=30
retry_attempts=3

[WINDOW_PREFERENCES]
use_graphics=true
graphics_mode=3

[ADVANCED]
debug_mode=false
EOF
    fi
fi

# Read configuration settings
MCP_ENABLED=$(read_ini "$CONFIG_FILE" "MCP_SERVER" "enabled")
MCP_AUTOSTART=$(read_ini "$CONFIG_FILE" "MCP_SERVER" "autostart")
MCP_SERVER_PATH=$(read_ini "$CONFIG_FILE" "MCP_SERVER" "server_path")
MCP_PORT=$(read_ini "$CONFIG_FILE" "MCP_SERVER" "port")
MCP_TIMEOUT=$(read_ini "$CONFIG_FILE" "MCP_SERVER" "timeout")
MCP_RETRY_ATTEMPTS=$(read_ini "$CONFIG_FILE" "MCP_SERVER" "retry_attempts")

# Set defaults if values are missing
[ -z "$MCP_ENABLED" ] && MCP_ENABLED="true"
[ -z "$MCP_AUTOSTART" ] && MCP_AUTOSTART="true"
[ -z "$MCP_SERVER_PATH" ] && MCP_SERVER_PATH="angband-doc-agent/src"
[ -z "$MCP_PORT" ] && MCP_PORT="3000"
[ -z "$MCP_TIMEOUT" ] && MCP_TIMEOUT="30"
[ -z "$MCP_RETRY_ATTEMPTS" ] && MCP_RETRY_ATTEMPTS="3"

# Start MCP server if enabled and autostart is true
if [ "$MCP_ENABLED" = "true" ]; then
    if [ "$MCP_AUTOSTART" = "true" ]; then
        echo "Checking for Node.js installation..."
        if ! command -v node &> /dev/null; then
            echo "ERROR: Node.js is not installed or not in PATH."
            echo "Please install Node.js to use the MCP server."
            echo "The game will start without MCP server support."
        else
            echo "Node.js found. Checking MCP server directory..."
            
            FULL_SERVER_PATH="$BASE_PATH$MCP_SERVER_PATH"
            if [ ! -d "$FULL_SERVER_PATH" ]; then
                echo "ERROR: MCP server directory not found at $FULL_SERVER_PATH"
                echo "The game will start without MCP server support."
            else
                echo "Starting MCP server from $FULL_SERVER_PATH..."
                
                # Set environment variables for the MCP server
                export PORT="$MCP_PORT"
                
                # Create .env file if it doesn't exist
                if [ ! -f "$FULL_SERVER_PATH/.env" ]; then
                    echo "Creating .env file for MCP server..."
                    cat > "$FULL_SERVER_PATH/.env" << EOF
PORT=$MCP_PORT
NODE_ENV=production
EOF
                fi
                
                # Start the MCP server in the background
                cd "$FULL_SERVER_PATH"
                node mcp-server.js > /dev/null 2>&1 &
                MCP_PID=$!
                cd "$BASE_PATH"
                
                echo "MCP server started on port $MCP_PORT (PID: $MCP_PID)."
                echo "Waiting for server to initialize..."
                sleep 2
            fi
        fi
    else
        echo "MCP server autostart is disabled in configuration."
    fi
else
    echo "MCP server is disabled in configuration."
fi

# Check for SDL2 configuration file
if [ ! -f "$SDL2_CONFIG_PATH" ]; then
    echo "SDL2 configuration file not found."
    echo "The game will generate an optimized configuration based on your screen resolution."
fi

# Read graphics settings
USE_GRAPHICS=$(read_ini "$CONFIG_FILE" "WINDOW_PREFERENCES" "use_graphics")
GRAPHICS_MODE=$(read_ini "$CONFIG_FILE" "WINDOW_PREFERENCES" "graphics_mode")

# Set defaults if values are missing
[ -z "$USE_GRAPHICS" ] && USE_GRAPHICS="true"
[ -z "$GRAPHICS_MODE" ] && GRAPHICS_MODE="3"

# Set graphics flag based on configuration
GRAPHICS_FLAG=""
if [ "$USE_GRAPHICS" = "true" ] && [ -n "$GRAPHICS_MODE" ]; then
    GRAPHICS_FLAG="-mgcu:$GRAPHICS_MODE"
fi

# Read debug mode setting
DEBUG_MODE=$(read_ini "$CONFIG_FILE" "ADVANCED" "debug_mode")

# Set debug flag based on configuration
DEBUG_FLAG=""
if [ "$DEBUG_MODE" = "true" ]; then
    DEBUG_FLAG="-d"
fi

# Start the game
echo
echo "Starting Ages of Arda..."
echo
./angband $GRAPHICS_FLAG $DEBUG_FLAG &

# Save the game PID to allow proper cleanup on exit
GAME_PID=$!

# Function to handle cleanup on exit
cleanup() {
    echo
    echo "Shutting down Ages of Arda environment..."
    
    # Kill the MCP server if it's running
    if [ -n "$MCP_PID" ] && ps -p $MCP_PID > /dev/null; then
        echo "Stopping MCP server (PID: $MCP_PID)..."
        kill $MCP_PID
    fi
    
    echo "Cleanup complete."
    exit 0
}

# Set up trap to catch termination signals
trap cleanup SIGINT SIGTERM

# Wait for the game to exit
wait $GAME_PID

# Clean up after the game exits
cleanup 