#!/bin/bash
# Script to run all the Lute the Bard tests

set -e # Exit on error

# Print colored output
GREEN='\033[0;32m'
RED='\033[0;31m'
BLUE='\033[0;34m'
YELLOW='\033[0;33m'
NC='\033[0m' # No Color

echo -e "${BLUE}====== Lute the Bard Test Suite ======${NC}"

# Check if dependencies are installed
echo -e "\n${YELLOW}Checking dependencies...${NC}"

# Check for Node.js
if ! command -v node &> /dev/null; then
    echo -e "${RED}Node.js is not installed. Please install Node.js to continue.${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Node.js is installed.${NC}"

# Check for curl
if ! command -v curl &> /dev/null; then
    echo -e "${RED}curl is not installed. Please install curl to continue.${NC}"
    exit 1
fi
echo -e "${GREEN}✓ curl is installed.${NC}"

# Check for Ollama (optional)
if command -v ollama &> /dev/null; then
    echo -e "${GREEN}✓ Ollama is installed.${NC}"
    OLLAMA_INSTALLED=true
else
    echo -e "${YELLOW}⚠ Ollama is not installed. You can still use OpenAI, but local LLM testing will not be available.${NC}"
    OLLAMA_INSTALLED=false
fi

# Check for dependencies in package.json
echo -e "\n${YELLOW}Installing Node.js dependencies...${NC}"
npm install

# Check if Ollama is running (if installed)
if [ "$OLLAMA_INSTALLED" = true ]; then
    echo -e "\n${YELLOW}Checking if Ollama is running...${NC}"
    if curl -s http://localhost:11434/api/tags | grep -q "llama3"; then
        echo -e "${GREEN}✓ Ollama is running and llama3 model is available.${NC}"
        OLLAMA_RUNNING=true
    else
        echo -e "${YELLOW}⚠ Ollama is not running or llama3 model is not available.${NC}"
        echo -e "${YELLOW}Starting Ollama and pulling llama3 model...${NC}"
        ollama pull llama3 &
        echo -e "${YELLOW}Continue with tests while Ollama model is downloading...${NC}"
        OLLAMA_RUNNING=false
    fi
fi

# Compile C test programs
echo -e "\n${YELLOW}Compiling C test programs...${NC}"
make clean && make

# Start the MCP server
echo -e "\n${YELLOW}Starting MCP server...${NC}"
if [ "$OLLAMA_RUNNING" = true ]; then
    # Use Ollama provider if available
    LLM_PROVIDER=ollama node bard-mcp-server.js &
else
    # Fall back to OpenAI if Ollama is not available
    if [ -z "$OPENAI_API_KEY" ]; then
        echo -e "${YELLOW}No OpenAI API key found in environment variables.${NC}"
        echo -e "${YELLOW}Enter your OpenAI API key (leave blank to skip OpenAI tests):${NC}"
        read -r OPENAI_API_KEY
        export OPENAI_API_KEY
    fi
    
    if [ -n "$OPENAI_API_KEY" ]; then
        LLM_PROVIDER=openai node bard-mcp-server.js &
    else
        echo -e "${RED}No LLM provider available. Tests cannot continue.${NC}"
        exit 1
    fi
fi
SERVER_PID=$!

# Wait for server to start
echo -e "${YELLOW}Waiting for server to start...${NC}"
sleep 3

# Run MCP server tests
echo -e "\n${YELLOW}Running MCP server tests...${NC}"
node test-mcp-server.js

# Run MCP client tests
echo -e "\n${YELLOW}Running MCP client tests...${NC}"
./test-mcp-client

# Run Bard module tests
echo -e "\n${YELLOW}Running Bard module tests...${NC}"
./test-bard

# Clean up
echo -e "\n${YELLOW}Cleaning up...${NC}"
kill $SERVER_PID
make clean

echo -e "\n${GREEN}All tests completed successfully!${NC}"
echo -e "\n${BLUE}====== Lute the Bard Test Suite Completed ======${NC}" 