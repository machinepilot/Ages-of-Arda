#!/bin/bash
# Windows Documentation Generator for Linux/Mac
# This shell script runs the documentation generator with Windows-specific settings

echo "Angband Windows Documentation Generator"
echo "======================================="

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not available in the PATH"
    exit 1
fi

# Check if the MCP server is running
if ! curl -s http://localhost:3000/mcp/ping &> /dev/null; then
    echo "Starting MCP server..."
    node mcp-server.js &
    sleep 5
fi

# Create output directory
mkdir -p ../output/windows

# Run the Windows module creator
echo "Creating Windows module documentation..."
python3 windows-module-creator.py

# Generate Windows documentation
echo "Generating Windows documentation..."
python3 document-angband.py --windows-only --output ../output/windows

# Generate Visual Studio project documentation
echo "Generating Visual Studio project documentation..."
python3 document-angband.py --vs-project --output ../output/windows/vs-project

# Run tests
echo "Running tests..."
python3 test-windows-doc.py --test detection

echo "Documentation generation complete!"
echo "Output is available in ../output/windows"

# Open the documentation in the default browser (if available)
if command -v xdg-open &> /dev/null; then
    xdg-open "../output/windows/windows_index.md"
elif command -v open &> /dev/null; then
    open "../output/windows/windows_index.md"
else
    echo "Documentation is available at: ../output/windows/windows_index.md"
fi 