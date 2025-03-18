---
title: Angband Documentation Agent - Quick Start Guide
id: angband-documentation-agent-quick-start-guide
section: gameplay
category: guides
created: '2025-03-14'
updated: '2025-03-18'
version: 0.1.0
---


Original Location: C:\working_directory\ages-project\clean-ages-of-arda\angband-doc-agent\QUICK_START.md
# Angband Documentation Agent - Quick Start Guide

This guide will help you quickly set up and start using the Angband Documentation Agent to generate documentation for the Angband codebase.

## Prerequisites

Before you begin, make sure you have:

- Python 3.8 or higher installed
- Node.js 14 or higher installed
- Angband source code downloaded to your computer

## Setup Steps

1. **Clone the Repository**

   ```
   git clone https://github.com/yourusername/angband-doc-agent.git
   cd angband-doc-agent
   ```

2. **Set Up Environment Variables**

   Copy the sample environment file and edit it:

   ```
   copy .env.sample .env
   ```

   Open the `.env` file in a text editor and update the `ANGBAND_SOURCE_PATH` to point to your Angband source code.

3. **Install Dependencies**

   The batch files will automatically check for and install required dependencies, but you can also install them manually:

   ```
   pip install requests
   npm install express cors
   ```

## Generating Documentation

### Option 1: Using the Batch File (Recommended)

1. Run the documentation generation batch file:

   ```
   cd src
   generate-docs.bat
   ```

   This will:
   - Check for required dependencies
   - Start the MCP server if it's not already running
   - Generate documentation
   - Output the results to the `docs` directory

2. View the generated documentation by opening `docs/index.md` in your preferred Markdown viewer.

### Option 2: Manual Steps

1. Start the MCP server:

   ```
   cd src
   node simple-mcp-server.js
   ```

   Keep this terminal window open.

2. In a new terminal, run the documentation generator:

   ```
   cd src
   python document-angband.py
   ```

## Customizing Documentation Generation

You can customize the documentation generation by editing the `document-angband.py` file or by passing command-line arguments:

```
python document-angband.py --windows-only --output custom-docs
```

Common options include:
- `--windows-only`: Only document Windows-specific files
- `--output DIR`: Specify a custom output directory
- `--force`: Force regeneration of all documentation
- `--verbose`: Show detailed output during generation

## Troubleshooting

### MCP Server Issues

If you see errors connecting to the MCP server:
1. Check that the server is running (you should see "MCP Server running on port 3000" in the terminal)
2. Verify that port 3000 is not being used by another application
3. Check that the `MCP_SERVER_URL` in your `.env` file is correct

### File Access Issues

If the documentation generator can't access the Angband source code:
1. Verify that the path in `ANGBAND_SOURCE_PATH` in your `.env` file is correct
2. Make sure the path doesn't contain special characters or spaces
3. Ensure you have read permissions for the Angband source directory

### Python or Node.js Issues

If you see errors related to Python or Node.js:
1. Verify that both are installed and in your PATH
2. Check that you have the required versions (Python 3.8+, Node.js 14+)
3. Try reinstalling the dependencies manually 