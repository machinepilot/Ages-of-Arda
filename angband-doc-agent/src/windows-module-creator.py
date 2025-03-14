#!/usr/bin/env python
"""
Windows Module Page Creator
This script creates a specialized Windows module documentation page
"""

import os
import re
import json
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

def read_memory_bank(file_name):
    """Read a file from the memory bank."""
    try:
        memory_bank_path = os.path.join(os.path.dirname(__file__), '..', 'memory-bank', file_name)
        with open(memory_bank_path, "r") as f:
            return f.read()
    except Exception as e:
        print(f"Error reading memory bank file {file_name}: {str(e)}")
        return ""

def categorize_windows_files(files):
    """Categorize Windows files by their functionality."""
    categories = {
        "Core": [],
        "Graphics": [],
        "Sound": [],
        "User Interface": [],
        "Resource Management": [],
        "Input Handling": [],
        "System Integration": [],
        "Utilities": []
    }
    
    for file in files:
        file_name = file['file'].lower()
        title = file['title']
        
        # Categorize based on filename and title
        if any(term in file_name for term in ['gfx', 'bitmap', 'image', 'draw', 'blit', 'font']):
            categories["Graphics"].append(file)
        elif any(term in file_name for term in ['sound', 'audio', 'music', 'wave']):
            categories["Sound"].append(file)
        elif any(term in file_name for term in ['menu', 'dialog', 'button', 'control', 'ui']):
            categories["User Interface"].append(file)
        elif any(term in file_name for term in ['term', 'main', 'init', 'core']):
            categories["Core"].append(file)
        elif any(term in file_name for term in ['file', 'resource', 'memory', 'alloc']):
            categories["Resource Management"].append(file)
        elif any(term in file_name for term in ['input', 'key', 'mouse', 'event']):
            categories["Input Handling"].append(file)
        elif any(term in file_name for term in ['system', 'registry', 'shell']):
            categories["System Integration"].append(file)
        else:
            categories["Utilities"].append(file)
    
    return categories

def create_windows_module_page():
    """Create a dedicated Windows module documentation page."""
    # Create the directory if it doesn't exist
    output_dir = os.path.join(os.path.dirname(__file__), '..', 'output', 'modules')
    os.makedirs(output_dir, exist_ok=True)
    
    # Get Windows context
    windows_compilation = read_memory_bank("windowsCompilation.md")
    windows_api_reference = read_memory_bank("windowsApiReference.md")
    
    # Build Windows module documentation
    windows_module_doc = f"""# Windows Module

## Overview

This module documents all Windows-specific code in the Angband codebase, including:

- Windows port-specific code
- Windows GUI implementation
- DLL dependencies and requirements
- Windows-specific gameplay features
- Compilation instructions for Windows environments

*Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*

## Table of Contents

- [Overview](#overview)
- [Compilation Methods](#compilation-methods)
- [Windows Files](#windows-files)
- [Windows Graphics Implementation](#windows-graphics-implementation)
- [Windows Sound System](#windows-sound-system)
- [Windows-Specific Configuration](#windows-specific-configuration)
- [Windows API Usage](#windows-api-usage)
- [Troubleshooting](#troubleshooting)

## Compilation Methods

"""
    windows_module_doc += windows_compilation

    # Find all Windows files in the output directory
    files_dir = os.path.join(os.path.dirname(__file__), '..', 'output', 'files')
    windows_files = []
    
    if os.path.exists(files_dir):
        for file in os.listdir(files_dir):
            if file.endswith('.md'):
                file_path = os.path.join(files_dir, file)
                
                # Read the file content
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Check if it's a Windows file
                if ('Windows-Specific Notes' in content or 
                    'win_' in file or 
                    '_win' in file or
                    'src/win' in content or
                    'src\\win' in content):
                    
                    # Extract the title
                    title_match = re.search(r'^# (.+)$', content, re.MULTILINE)
                    title = title_match.group(1) if title_match else file.replace('.md', '')
                    
                    # Extract Windows API usage if available
                    api_usage = []
                    api_section = re.search(r'## Windows-Specific Notes\s+(.+?)(?=##|\Z)', content, re.DOTALL)
                    if api_section:
                        api_text = api_section.group(1)
                        api_functions = re.findall(r'\b(Create\w+|Register\w+|Show\w+|Load\w+|Get\w+|Set\w+|Play\w+|Bit\w+|Text\w+)\b', api_text)
                        api_usage = list(set(api_functions))  # Remove duplicates
                    
                    windows_files.append({
                        'file': file,
                        'title': title,
                        'api_usage': api_usage
                    })
    
    # Categorize Windows files
    categorized_files = categorize_windows_files(windows_files)
    
    # Add Windows files to the documentation by category
    windows_module_doc += """
## Windows Files

Below are all the Windows-specific files in the codebase, organized by category:

"""
    
    for category, files in categorized_files.items():
        if files:
            windows_module_doc += f"### {category}\n\n"
            for win_file in files:
                windows_module_doc += f"- [{win_file['title']}](../files/{win_file['file']})\n"
            windows_module_doc += "\n"
    
    # Add Windows graphics section with more details
    windows_module_doc += """
## Windows Graphics Implementation

The Windows port supports multiple graphics modes:

### ASCII Mode
- Classic text-based display using Windows console functions
- Implemented using Windows GDI text rendering
- Supports customizable fonts and colors
- Lowest system requirements

### Tiled Mode
- Graphical tiles rendered using Windows GDI functions
- Supports various tile sizes (8x8, 16x16, 32x32)
- Uses BitBlt and StretchBlt for tile rendering
- Supports transparency via color keying

### DirectX Mode (when available)
- Hardware-accelerated graphics using DirectX
- Faster rendering for complex tile sets
- Supports alpha blending and scaling effects
- Requires DirectX runtime libraries

### Graphics Pipeline
```mermaid
graph TD
    A[Game State] --> B[Term Layer]
    B --> C{Graphics Mode}
    C -->|ASCII| D[GDI Text Rendering]
    C -->|Tiles| E[GDI BitBlt/StretchBlt]
    C -->|DirectX| F[DirectX Surface Rendering]
    D --> G[Windows Display]
    E --> G
    F --> G
```

## Windows Sound System

The Windows port implements sound using multiple methods:

### Basic Sound Support
- Windows API `PlaySound` function for basic sound effects
- Supports WAV files for game events
- Simple to implement but limited features

### SDL Mixer Support
- Available when compiled with SDL support
- Supports multiple audio channels
- Enables background music playback
- Supports various audio formats (WAV, OGG, MP3)

### FMOD Support
- High-quality music playback in some variants
- Advanced 3D positional audio
- Requires additional runtime libraries

### Sound Configuration
Sound settings are stored in the Windows registry and can be configured through the in-game options menu or by editing the configuration files directly.

## Windows-Specific Configuration

### Registry Settings
Windows-specific options are stored in:
- Registry entries under `HKEY_CURRENT_USER\\Software\\Angband`
- Key settings include:
  - Window positions and sizes
  - Graphics mode preferences
  - Font selections
  - Sound settings

### INI Files
Alternative configuration through INI files in the user's Application Data directory:
- `angband.ini` - Main configuration
- `graphics.ini` - Graphics settings
- `sound.ini` - Sound mappings

### Command-Line Parameters
Windows-specific command-line options:
- `-n#` - Number of terminal windows to use
- `-r#` - Sets screen resolution
- `-s#` - Sets tile size
- `-g` - Enables graphics mode
- `-o` - Enables original graphics

## Windows API Usage

The Windows port makes use of various Windows API functions:

"""

    # Add Windows API reference summary
    api_categories = ["Window Management", "Graphics", "Font and Text", "Sound", "File and Resource", "Registry", "Dialog", "Memory"]
    for category in api_categories:
        windows_module_doc += f"### {category}\n"
        
        # Extract relevant section from API reference
        section_match = re.search(f"## {category}(.+?)(?=^##|\Z)", windows_api_reference, re.MULTILINE | re.DOTALL)
        if section_match:
            section_text = section_match.group(1).strip()
            # Extract function names from the section
            function_names = re.findall(r'### ([^#\n]+)', section_text)
            for func in function_names:
                windows_module_doc += f"- {func.strip()}\n"
        
        windows_module_doc += "\n"
    
    # Add troubleshooting section
    windows_module_doc += """
## Troubleshooting

### Common Issues and Solutions

#### Missing DLL Errors
If you encounter "Missing DLL" errors when running Angband:
- Ensure libpng.dll and zlib1.dll are in the same directory as the executable
- Check that you have the correct version of the DLLs for your build (32-bit or 64-bit)
- Install the Visual C++ Redistributable package if using the Visual Studio build

#### Graphics Issues
If graphics don't display correctly:
- Verify that the tile set files are in the correct directory
- Check that the selected graphics mode is supported by your system
- Try different graphics modes through the options menu
- Update your graphics drivers

#### Sound Problems
If sound doesn't work:
- Ensure the sound files are in the correct directory
- Check that sound is enabled in the options
- Verify that your system's sound is working properly
- If using SDL sound, ensure SDL_mixer.dll is available

#### Performance Issues
If the game runs slowly:
- Reduce the number of terminal windows
- Switch to a simpler graphics mode
- Close other applications running in the background
- Check for system resource usage (CPU, memory)

### Reporting Windows-Specific Bugs
When reporting bugs in the Windows version:
1. Note your Windows version and build
2. Specify your compilation method (MinGW, Visual Studio, etc.)
3. Include any error messages exactly as they appear
4. Describe the steps to reproduce the issue
5. Mention any recent changes to your system or game configuration
"""
    
    # Save Windows module documentation
    with open(os.path.join(output_dir, "windows.md"), "w", encoding="utf-8") as f:
        f.write(windows_module_doc)
    
    print("Created Windows module page at: ../output/modules/windows.md")
    
    # Create a JSON file with Windows file metadata for other tools
    windows_metadata = {
        "files": windows_files,
        "categories": {category: [f["file"] for f in files] for category, files in categorized_files.items()},
        "generated_at": datetime.now().isoformat()
    }
    
    with open(os.path.join(output_dir, "windows_metadata.json"), "w", encoding="utf-8") as f:
        json.dump(windows_metadata, f, indent=2)
    
    print("Created Windows metadata at: ../output/modules/windows_metadata.json")

if __name__ == "__main__":
    create_windows_module_page()