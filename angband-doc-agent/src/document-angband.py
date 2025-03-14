#!/usr/bin/env python
"""
Angband Documentation Generator
This script connects to an MCP server to analyze and document an Angband codebase.
"""

import os
import json
import time
import re
import requests
import anthropic
import markdown
import argparse
import random
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

# Configure API clients
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
ANGBAND_SOURCE_PATH = os.getenv("ANGBAND_SOURCE_PATH", "C:/working_directory/angband")
MCP_SERVER_URL = os.getenv("MCP_SERVER_URL", "http://localhost:3000/mcp")

# Initialize Anthropic client
client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

# Rate limiting and checkpoint configuration
DEFAULT_DELAY_BETWEEN_FILES = 30  # seconds between file processing
DEFAULT_RETRY_DELAY = 60  # seconds to wait after a rate limit error
MAX_RETRIES = 5  # maximum number of retries for a file
CHECKPOINT_FILE = "doc_generator_checkpoint.json"  # file to store progress

def make_mcp_request(tool, params):
    """
    Make a request to the MCP server to use a tool.
    
    Args:
        tool (str): The name of the tool to use
        params (dict): Parameters for the tool
        
    Returns:
        dict: The response from the MCP server
    """
    try:
        print(f"Making MCP request to {tool} with params: {params}")
        
        # Check if MCP_SERVER_URL already ends with /mcp
        if MCP_SERVER_URL.endswith('/mcp'):
            url = f"{MCP_SERVER_URL}/tools/{tool}"
        else:
            url = f"{MCP_SERVER_URL}/mcp/tools/{tool}"
            
        print(f"Request URL: {url}")
        
        response = requests.post(
            url,
            json=params,
            headers={"Content-Type": "application/json"},
            timeout=30  # Add timeout to prevent hanging
        )
        
        if response.status_code != 200:
            print(f"Error calling MCP tool {tool}: {response.status_code}")
            print(response.text)
            return {"error": f"HTTP {response.status_code}: {response.text}"}
        
        result = response.json()
        print(f"MCP request to {tool} successful")
        return result
    except requests.exceptions.ConnectionError:
        error_msg = f"Connection error: Could not connect to MCP server at {MCP_SERVER_URL}. Is the server running?"
        print(error_msg)
        return {"error": error_msg}
    except requests.exceptions.Timeout:
        error_msg = f"Timeout error: MCP server at {MCP_SERVER_URL} did not respond in time"
        print(error_msg)
        return {"error": error_msg}
    except Exception as e:
        error_msg = f"Exception calling MCP tool {tool}: {str(e)}"
        print(error_msg)
        return {"error": error_msg}

def list_project_files(directory="."):
    """
    List all files in the project directory recursively.
    
    Args:
        directory (str): The directory to list files from
        
    Returns:
        list: A list of file paths
    """
    # Use the absolute path to the Angband source code
    if directory == ".":
        directory = ANGBAND_SOURCE_PATH
    
    print(f"Listing files from directory: {directory}")
    
    # Try using the MCP server first
    response = make_mcp_request("listDirectory", {"path": directory})
    
    if "error" not in response:
        files = response.get("files", [])
        print(f"Found {len(files)} files in total via MCP server")
        
        # Filter to only include .c and .h files
        c_files = [f for f in files if f.endswith((".c", ".h"))]
        print(f"Filtered to {len(c_files)} C and header files")
        return c_files
    
    # If MCP server fails, fall back to direct file system access
    print(f"MCP server failed with error: {response.get('error', 'Unknown error')}")
    print("Falling back to direct file system access...")
    
    try:
        files = []
        
        # Walk the directory tree
        for root, _, filenames in os.walk(directory):
            for filename in filenames:
                if filename.endswith((".c", ".h")):
                    # Get the path relative to the Angband source directory
                    full_path = os.path.join(root, filename)
                    rel_path = os.path.relpath(full_path, directory)
                    files.append(rel_path.replace("\\", "/"))
        
        print(f"Found {len(files)} C and header files via direct file system access")
        return files
    except Exception as e:
        print(f"Error listing files via direct file system access: {str(e)}")
        return []

def read_memory_bank(file_name):
    """
    Read a file from the memory bank.
    
    Args:
        file_name (str): The name of the file to read
        
    Returns:
        str: The content of the file
    """
    try:
        memory_bank_path = os.path.join(os.path.dirname(__file__), '..', 'memory-bank', file_name)
        with open(memory_bank_path, "r") as f:
            return f.read()
    except Exception as e:
        print(f"Error reading memory bank file {file_name}: {str(e)}")
        return ""

def build_file_context(file_path):
    """
    Build context information for a file.
    
    Args:
        file_path (str): The path to the file
        
    Returns:
        dict: Context information about the file
    """
    # Get file content
    response = make_mcp_request("readFile", {"path": file_path})
    
    # If MCP server fails, fall back to direct file system access
    if "error" in response:
        print(f"Error reading file via MCP server: {response['error']}")
        print("Falling back to direct file system access...")
        
        try:
            full_path = os.path.join(ANGBAND_SOURCE_PATH, file_path)
            with open(full_path, 'r', encoding='utf-8', errors='replace') as f:
                file_content = f.read()
            print(f"Successfully read file via direct file system access: {file_path}")
        except Exception as e:
            print(f"Error reading file via direct file system access: {str(e)}")
            return {"error": f"Error reading file: {str(e)}"}
    else:
        file_content = response.get("content", "")
    
    # Get basic file info
    info_response = make_mcp_request("getFileInfo", {"path": file_path})
    
    # If MCP server fails, fall back to direct file system access
    if "error" in info_response:
        print(f"Error getting file info via MCP server: {info_response['error']}")
        print("Falling back to direct file system access...")
        
        try:
            full_path = os.path.join(ANGBAND_SOURCE_PATH, file_path)
            stat = os.stat(full_path)
            file_info = f"""
File: {file_path}
Size: {stat.st_size} bytes
Last Modified: {datetime.fromtimestamp(stat.st_mtime).isoformat()}
"""
            print(f"Successfully got file info via direct file system access: {file_path}")
            
            # Check if this is a Windows-specific file
            is_windows_file = (
                "src/win" in file_path or 
                "src\\win" in file_path or
                file_path.endswith("_win.c") or
                file_path.endswith("_win.h") or
                "windows" in file_path.lower()
            )
        except Exception as e:
            print(f"Error getting file info via direct file system access: {str(e)}")
            file_info = f"File: {file_path}\n"
            is_windows_file = False
    else:
        file_info = f"""
File: {file_path}
Size: {info_response.get('size', 'Unknown')} bytes
Last Modified: {info_response.get('modifiedAt', 'Unknown')}
"""
        is_windows_file = (
            "src/win" in file_path or 
            "src\\win" in file_path or
            file_path.endswith("_win.c") or
            file_path.endswith("_win.h") or
            info_response.get("isWindowsFile", False)
        )
    
    # Extract function names for further analysis
    function_names = re.findall(r'\b(\w+)\s*\([^)]*\)\s*{', file_content)
    
    # Get memory bank context
    project_brief = read_memory_bank("projectBrief.md")
    code_context = read_memory_bank("codeContext.md")
    game_context = read_memory_bank("gameContext.md")
    windows_compilation = read_memory_bank("windowsCompilation.md")
    windows_api_reference = read_memory_bank("windowsApiReference.md")
    
    # Detect Windows API usage
    windows_api_usage = {}
    if is_windows_file:
        # Check for Windows API includes
        windows_includes = re.findall(r'#include\s+<(win[^>]+\.h)>', file_content)
        
        # Check for common Windows API function calls
        api_patterns = {
            "Window Management": [r'\b(CreateWindow\w*|RegisterClass\w*|ShowWindow|UpdateWindow|GetMessage|PeekMessage|DispatchMessage)\b'],
            "Graphics": [r'\b(BitBlt|StretchBlt|CreateCompatibleDC|CreateCompatibleBitmap|SelectObject|LoadBitmap|LoadImage)\b'],
            "Font and Text": [r'\b(CreateFont\w*|TextOut\w*|ExtTextOut|GetTextMetrics)\b'],
            "Sound": [r'\b(PlaySound|waveOut\w+)\b'],
            "File and Resource": [r'\b(FindFirstFile|FindNextFile|FindClose|LoadResource|FindResource|GetModuleFileName)\b'],
            "Registry": [r'\b(RegOpenKey\w*|RegQueryValue\w*|RegCloseKey)\b'],
            "Dialog": [r'\b(DialogBox\w*|CreateDialog\w*|GetDlgItem|SetDlgItemText)\b'],
            "Memory": [r'\b(GlobalAlloc|GlobalLock|GlobalUnlock|GlobalFree|VirtualAlloc|VirtualFree)\b'],
            "DirectX": [r'\b(Direct3D|DirectDraw|DirectSound|DirectInput|D3D|IDirect\w+|LPDIRECT\w+)\b']
        }
        
        for category, patterns in api_patterns.items():
            for pattern in patterns:
                matches = re.findall(pattern, file_content)
                if matches:
                    if category not in windows_api_usage:
                        windows_api_usage[category] = []
                    windows_api_usage[category].extend(matches)
        
        # Check for Windows-specific preprocessor directives
        windows_directives = re.findall(r'#if(?:def)?\s+(?:defined\()?\s*(_WIN32|WIN32|WINDOWS)\b', file_content)
    
    # Detect GUI elements
    gui_elements = []
    if is_windows_file:
        # Look for dialog resources
        dialog_matches = re.findall(r'DIALOG\s+(\d+),\s*(\d+),\s*(\d+),\s*(\d+)', file_content)
        if dialog_matches:
            gui_elements.append("Dialog boxes")
        
        # Look for menu resources
        if "MENU" in file_content:
            gui_elements.append("Menus")
        
        # Look for control creation
        control_patterns = [
            r'\bCreateWindow\w*\s*\(\s*"BUTTON"',
            r'\bCreateWindow\w*\s*\(\s*"EDIT"',
            r'\bCreateWindow\w*\s*\(\s*"LISTBOX"',
            r'\bCreateWindow\w*\s*\(\s*"COMBOBOX"',
            r'\bCreateWindow\w*\s*\(\s*"STATIC"'
        ]
        
        for pattern in control_patterns:
            if re.search(pattern, file_content):
                gui_elements.append("Standard controls")
                break
    
    return {
        "file_path": file_path,
        "file_info": file_info,
        "file_content": file_content,
        "function_names": function_names,
        "project_brief": project_brief,
        "code_context": code_context,
        "game_context": game_context,
        "windows_compilation": windows_compilation,
        "windows_api_reference": windows_api_reference,
        "is_windows_file": is_windows_file,
        "windows_api_usage": windows_api_usage,
        "gui_elements": gui_elements
    }

def analyze_file_with_ai(context, retry_count=0, delay=DEFAULT_RETRY_DELAY):
    """
    Use AI to analyze and document a file with retry logic for rate limits.
    
    Args:
        context (dict): Context information about the file
        retry_count (int): Current retry attempt
        delay (int): Delay in seconds before retrying
        
    Returns:
        str: Generated documentation for the file
    """
    if "error" in context:
        return f"# Error\n\n{context['error']}"
        
    file_path = context["file_path"]
    file_content = context["file_content"]
    
    # Create prompt for the AI
    prompt = f"""You are an expert C programmer specializing in roguelike game code documentation, particularly for Angband and its variants. You're tasked with creating comprehensive documentation for an Angband clone written in C.

# PROJECT CONTEXT
{context["project_brief"]}

# C CODE CONTEXT
{context["code_context"]}

# ROGUELIKE GAME CONTEXT
{context["game_context"]}"""

    # Add Windows-specific context if needed
    if context["is_windows_file"]:
        prompt += f"""
# WINDOWS COMPILATION CONTEXT
{context["windows_compilation"]}

# WINDOWS API REFERENCE
{context["windows_api_reference"]}"""

        # Add detected Windows API usage if available
        if context["windows_api_usage"]:
            prompt += "\n\n# DETECTED WINDOWS API USAGE IN THIS FILE\n"
            for category, functions in context["windows_api_usage"].items():
                prompt += f"\n## {category}\n"
                for func in set(functions):  # Use set to remove duplicates
                    prompt += f"- {func}\n"
        
        # Add detected GUI elements if available
        if context["gui_elements"]:
            prompt += "\n\n# DETECTED GUI ELEMENTS IN THIS FILE\n"
            for element in context["gui_elements"]:
                prompt += f"- {element}\n"

    # Add file content to document
    prompt += f"""
# FILE TO DOCUMENT
{context["file_info"]}

{file_content}

Create detailed documentation for this file with the following sections:

1. **File Overview**: A summary of the file's purpose and role in the Angband codebase.

2. **Data Structures**: Document all structs and important typedefs with explanations of each field.

3. **Global Variables**: List and explain all global variables, including their purpose and usage.

4. **Functions**: Document each function with:
   - Purpose and description
   - Parameters with types and explanations
   - Return value meaning
   - Side effects
   - Relationships to other functions
   - Game mechanics implemented

5. **Algorithms**: Explain any complex algorithms or game mechanics implementations.

6. **Dependencies**: Identify what other files this depends on and what depends on it.
"""

    # Add Windows-specific documentation request if needed
    if context["is_windows_file"]:
        prompt += """
7. **Windows-Specific Notes**: Explain any Windows API usage, GUI elements, or platform-specific behavior, including:
   - Window management and message handling
   - Graphics rendering approach (GDI, DirectX, etc.)
   - User input processing
   - Resource management
   - Integration with the Windows environment

8. **Compilation Considerations**: Note any special requirements for compiling this file on Windows using:
   - MinGW compilation method
   - Cygwin compilation method
   - MSYS2 compilation method
   - Visual Studio compilation method
   
   Include any required libraries, header files, preprocessor definitions, and linker settings.
   
9. **Windows Performance Considerations**: Discuss any performance implications specific to the Windows implementation, such as:
   - Memory management strategies
   - Graphics optimization techniques
   - Event handling efficiency
   - Resource loading optimizations
"""
    else:
        prompt += """
7. **Historical Context**: If relevant, note any interesting historical aspects of this code.
"""

    prompt += """
Format your response in Markdown. Be comprehensive yet clear. Focus on explaining the roguelike game mechanics implemented in this code.
"""

    # Call the AI model with retry logic
    try:
        message = client.messages.create(
            model="claude-3-opus-20240229",  # Use the latest available model
            max_tokens=4000,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        
        # Extract the response text
        documentation = message.content[0].text
        return documentation
    except anthropic.RateLimitError as e:
        if retry_count < MAX_RETRIES:
            # Calculate exponential backoff with jitter
            backoff_delay = delay * (2 ** retry_count) + random.uniform(1, 10)
            print(f"Rate limit hit for file {file_path}. Retrying in {backoff_delay:.1f} seconds (attempt {retry_count+1}/{MAX_RETRIES})...")
            time.sleep(backoff_delay)
            return analyze_file_with_ai(context, retry_count + 1, delay)
        else:
            print(f"Max retries exceeded for file {file_path}. Giving up.")
            return f"""# {os.path.basename(file_path)}

## File Overview

This file is located at `{file_path}` in the Angband codebase.

## Error Generating Documentation

An error occurred while generating documentation: Error code: 429 - Rate limit exceeded. The documentation for this file will need to be generated later.

## Raw File Content

```c
{file_content[:1000]}
...
```

*Note: File content truncated for brevity.*
"""
    except Exception as e:
        print(f"Error calling AI for file {file_path}: {str(e)}")
        
        # Create a basic documentation if AI fails
        documentation = f"""# {os.path.basename(file_path)}

## File Overview

This file is located at `{file_path}` in the Angband codebase.

## Error Generating Documentation

An error occurred while generating documentation: {str(e)}

## Raw File Content

```c
{file_content[:1000]}
...
```

*Note: File content truncated for brevity.*
"""
        return documentation

def save_documentation(file_path, documentation, output_dir):
    """
    Save the generated documentation to a file.
    
    Args:
        file_path (str): The original file path
        documentation (str): The generated documentation
        output_dir (str): The output directory
        
    Returns:
        str: The path to the saved documentation file
    """
    # Create file name for documentation based on original file name
    base_name = os.path.basename(file_path)
    doc_file_name = f"{os.path.splitext(base_name)[0]}.md"
    
    # Determine the output path
    files_dir = os.path.join(output_dir, "files")
    os.makedirs(files_dir, exist_ok=True)
    doc_path = os.path.join(files_dir, doc_file_name)
    
    # Save documentation
    with open(doc_path, "w", encoding="utf-8") as f:
        f.write(documentation)
    
    print(f"Saved documentation for {file_path} to {doc_path}")
    return doc_path

def create_module_documentation(files_by_module, output_dir):
    """
    Create documentation for modules (directories).
    
    Args:
        files_by_module (dict): Files grouped by module
        output_dir (str): The output directory
        
    Returns:
        dict: Module documentation
    """
    print("Creating module documentation...")
    
    module_docs = {}
    modules_dir = os.path.join(output_dir, "modules")
    os.makedirs(modules_dir, exist_ok=True)
    
    for module, files in files_by_module.items():
        print(f"Creating module documentation for {module}...")
        
        # Create module documentation content
        module_doc = f"# Module: {module}\n\n"
        module_doc += "## Overview\n\n"
        module_doc += f"This module contains {len(files)} files related to {module} functionality.\n\n"
        module_doc += "## Files\n\n"
        
        for file in files:
            base_name = os.path.basename(file)
            doc_file_name = f"{os.path.splitext(base_name)[0]}.md"
            module_doc += f"- [{base_name}](../files/{doc_file_name})\n"
        
        # Save module documentation
        module_docs[module] = module_doc
        module_file_path = os.path.join(modules_dir, f"{module.replace('/', '_').replace('\\', '_')}.md")
        
        with open(module_file_path, "w", encoding="utf-8") as f:
            f.write(module_doc)
        
        print(f"Saved module documentation to {module_file_path}")
    
    return module_docs

def create_windows_compilation_guide(output_dir):
    """
    Create a dedicated guide for Windows compilation methods.
    
    Args:
        output_dir (str): The output directory
    
    Returns:
        str: The path to the saved guide file
    """
    print("Creating Windows compilation guide...")
    
    # Load Windows compilation information from memory bank
    windows_compilation = read_memory_bank("windowsCompilation.md")
    
    # Create an enhanced compilation guide with additional details
    compilation_guide = """# Windows Compilation Guide for Angband

This document details various methods for compiling Angband on Windows platforms.

"""
    # Add the base Windows compilation information
    compilation_guide += windows_compilation
    
    # Add visual compilation flow diagram using Mermaid syntax
    compilation_guide += """
## Compilation Flow Diagram
```mermaid
graph TD
    S[Source Code] --> A[./autogen.sh]
    A --> C[./configure]
    C --> M[make]
    M --> I[make install]
    
    C -- Windows --> C1[--enable-win]
    C -- Cygwin --> C2[--host=i686-pc-mingw32]
    
    M --> M1[Compile C files]
    M1 --> M2[Link executable]
    M2 --> M3[Copy DLLs]
    
    subgraph "MSYS2 Method"
    MS[Source] --> MS1[make -f Makefile.msys2]
    MS1 -- SDL2 --> MS2[make -f Makefile.msys2.sdl2]
    end
```

## Build Environment Matrix

| Method | Pros | Cons | Key Dependencies |
|--------|------|------|------------------|
| MinGW | Simple setup, standard build process | Limited graphics options | gcc, make, autoconf |
| MSYS2 | Modern, supports SDL2, active development | Larger installation footprint | mingw-w64-x86_64-gcc, SDL2 packages |
| Cygwin | UNIX-like environment, familiar tools | Performance overhead | mingw32 compiler packages |
| Visual Studio | Native IDE, debugging tools | Complex setup, project maintenance | MSVC toolchain, Windows SDK |

## Common Issues and Solutions

### DLL Missing Errors
If you encounter "Missing DLL" errors when running the compiled executable, ensure you've copied the required DLLs:
- libpng12.dll
- zlib1.dll

### Path Issues
Windows paths use backslashes, but the configure scripts expect forward slashes. Use forward slashes in your commands, e.g.:

```
./configure --prefix=C:/angband
```

### MSYS2 Environment Issues
If MSYS2 shell has trouble launching, try setting the MSYSTEM environment variable:

```
set MSYSTEM=MINGW64
```
"""

    # Save the compilation guide to the output directory
    os.makedirs(output_dir, exist_ok=True)
    guide_path = os.path.join(output_dir, "windows_compilation.md")
    
    with open(guide_path, "w", encoding="utf-8") as f:
        f.write(compilation_guide)
    
    print(f"Created Windows compilation guide at {guide_path}")
    return guide_path

def create_windows_documentation_index(windows_files, output_dir):
    """
    Create an index of Windows-specific documentation.
    
    Args:
        windows_files (list): List of Windows-specific files
        output_dir (str): The output directory
        
    Returns:
        str: The path to the saved index file
    """
    print("Creating Windows documentation index...")
    
    if not windows_files:
        print("No Windows-specific files found. Skipping Windows index creation.")
        return None
    
    # Create Windows index content
    windows_index = "# Windows-Specific Documentation\n\n"
    windows_index += "This section contains documentation for Windows-specific components of Angband.\n\n"
    
    # Categorize Windows files
    categories = {
        "Core": [],
        "Graphics": [],
        "Sound": [],
        "Interface": [],
        "System": []
    }
    
    # Group files by category based on filename patterns
    for file_path in windows_files:
        base_name = os.path.basename(file_path)
        
        if "gfx" in base_name or "bitmap" in base_name or "font" in base_name:
            categories["Graphics"].append(file_path)
        elif "sound" in base_name or "music" in base_name or "audio" in base_name:
            categories["Sound"].append(file_path)
        elif "menu" in base_name or "dialog" in base_name or "ui" in base_name:
            categories["Interface"].append(file_path)
        elif "term" in base_name or "main" in base_name:
            categories["Core"].append(file_path)
        else:
            categories["System"].append(file_path)
    
    # Add each category to the index
    for category, files in categories.items():
        if files:
            windows_index += f"## {category} Components\n\n"
            
            for file_path in files:
                base_name = os.path.basename(file_path)
                doc_file_name = f"{os.path.splitext(base_name)[0]}.md"
                windows_index += f"- [{base_name}](files/{doc_file_name})\n"
            
            windows_index += "\n"
    
    # Add link to compilation guide
    windows_index += "## Compilation\n\n"
    windows_index += "For detailed instructions on compiling Angband on Windows, see the [Windows Compilation Guide](windows_compilation.md).\n\n"
    
    # Save Windows index to output directory
    index_path = os.path.join(output_dir, "windows_index.md")
    
    with open(index_path, "w", encoding="utf-8") as f:
        f.write(windows_index)
    
    print(f"Created Windows documentation index at {index_path}")
    return index_path

def create_main_documentation(module_docs, output_dir):
    """
    Create the main documentation file.
    
    Args:
        module_docs (dict): All module documentation
        output_dir (str): The output directory
        
    Returns:
        str: The path to the saved main documentation file
    """
    print("Creating main documentation README...")
    
    main_doc = "# Angband Clone Documentation\n\n"
    main_doc += f"*Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n\n"
    
    main_doc += "## Project Overview\n\n"
    main_doc += read_memory_bank("projectBrief.md") + "\n\n"
    
    # Add Windows Compilation section with link
    main_doc += "## Windows Compilation\n\n"
    main_doc += "For detailed instructions on compiling Angband on Windows, see the [Windows Compilation Guide](windows_compilation.md).\n\n"
    
    main_doc += "## Modules\n\n"
    
    for module in sorted(module_docs.keys()):
        main_doc += f"- [{module}](modules/{module.replace('/', '_').replace('\\', '_')}.md)\n"
    
    # Save main documentation
    readme_path = os.path.join(output_dir, "README.md")
    
    with open(readme_path, "w", encoding="utf-8") as f:
        f.write(main_doc)
    
    print(f"Saved main documentation to {readme_path}")
    return readme_path

def save_checkpoint(processed_files, remaining_files, output_dir):
    """
    Save progress checkpoint to resume later.
    
    Args:
        processed_files (list): Files that have been processed
        remaining_files (list): Files that still need processing
        output_dir (str): Output directory
    """
    checkpoint = {
        "timestamp": datetime.now().isoformat(),
        "processed_files": processed_files,
        "remaining_files": remaining_files,
        "output_dir": output_dir
    }
    
    with open(CHECKPOINT_FILE, "w") as f:
        json.dump(checkpoint, f, indent=2)
    
    print(f"Checkpoint saved: {len(processed_files)} files processed, {len(remaining_files)} files remaining")

def load_checkpoint():
    """
    Load progress checkpoint to resume processing.
    
    Returns:
        dict: Checkpoint data or None if no checkpoint exists
    """
    if not os.path.exists(CHECKPOINT_FILE):
        return None
    
    try:
        with open(CHECKPOINT_FILE, "r") as f:
            checkpoint = json.load(f)
        
        print(f"Checkpoint loaded: {len(checkpoint['processed_files'])} files processed, {len(checkpoint['remaining_files'])} files remaining")
        return checkpoint
    except Exception as e:
        print(f"Error loading checkpoint: {str(e)}")
        return None

def estimate_completion_time(remaining_files, delay_between_files):
    """
    Estimate the time to complete processing all remaining files.
    
    Args:
        remaining_files (list): Files that still need processing
        delay_between_files (int): Delay between file processing in seconds
        
    Returns:
        str: Estimated completion time
    """
    # Estimate average processing time per file (30 seconds + delay)
    avg_time_per_file = 30 + delay_between_files
    
    # Calculate total estimated time in seconds
    total_time = len(remaining_files) * avg_time_per_file
    
    # Convert to hours, minutes, seconds
    hours = total_time // 3600
    minutes = (total_time % 3600) // 60
    seconds = total_time % 60
    
    return f"{hours}h {minutes}m {seconds}s"

def main():
    """
    Main function to run the documentation generator.
    """
    parser = argparse.ArgumentParser(description="Generate documentation for an Angband clone codebase.")
    parser.add_argument("--source", default=ANGBAND_SOURCE_PATH, help="Path to the Angband source code")
    parser.add_argument("--output", default="docs", help="Output directory for documentation")
    parser.add_argument("--force", action="store_true", help="Force regeneration of all files")
    parser.add_argument("--verbose", action="store_true", help="Verbose output")
    parser.add_argument("--windows-only", action="store_true", help="Only process Windows-specific files")
    parser.add_argument("--vs-project", action="store_true", help="Document Visual Studio project files")
    parser.add_argument("--win-api-version", type=str, default="", help="Specify Windows API version (e.g., 'win32', 'win64')")
    parser.add_argument("--max-files", type=int, default=0, help="Maximum number of files to process (0 for all)")
    parser.add_argument("--module", type=str, default="", help="Only process files in a specific module/directory")
    parser.add_argument("--file", type=str, default="", help="Only process a specific file")
    parser.add_argument("--incremental", action="store_true", help="Only process files that have changed since last run")
    parser.add_argument("--format", type=str, choices=["markdown", "html", "pdf"], default="markdown", help="Output format")
    parser.add_argument("--delay", type=int, default=DEFAULT_DELAY_BETWEEN_FILES, help="Delay between file processing in seconds")
    parser.add_argument("--resume", action="store_true", help="Resume from last checkpoint")
    parser.add_argument("--batch-size", type=int, default=10, help="Number of files to process before saving a checkpoint")
    args = parser.parse_args()
    
    print("Angband Documentation Generator")
    print("==============================")
    print(f"Source path: {args.source}")
    print(f"MCP server: {MCP_SERVER_URL}")
    print(f"Delay between files: {args.delay} seconds")
    print(f"Batch size: {args.batch_size} files")
    
    # Check if resuming from checkpoint
    if args.resume:
        checkpoint = load_checkpoint()
        if checkpoint:
            processed_files = checkpoint["processed_files"]
            project_files = checkpoint["remaining_files"]
            args.output = checkpoint["output_dir"]
            print(f"Resuming from checkpoint: {len(processed_files)} files processed, {len(project_files)} files remaining")
            
            # Estimate completion time
            est_time = estimate_completion_time(project_files, args.delay)
            print(f"Estimated completion time: {est_time}")
        else:
            print("No checkpoint found. Starting from scratch.")
            processed_files = []
            project_files = None
    else:
        processed_files = []
        project_files = None
    
    # Create output directory
    os.makedirs(args.output, exist_ok=True)
    os.makedirs(os.path.join(args.output, "files"), exist_ok=True)
    os.makedirs(os.path.join(args.output, "modules"), exist_ok=True)
    
    # List all project files if not resuming
    if project_files is None:
        if args.file:
            project_files = [args.file]
            print(f"Processing single file: {args.file}")
        else:
            print(f"Listing files in {args.source}...")
            project_files = list_project_files(args.source)
            if not project_files:
                print("No project files found.")
                return
            
            print(f"Found {len(project_files)} C and header files.")
            
            # Filter files if module specified
            if args.module:
                project_files = [f for f in project_files if f.startswith(args.module)]
                print(f"Filtered to {len(project_files)} files in module {args.module}")
            
            # Filter for Windows files if requested
            if args.windows_only:
                # Enhanced Windows file detection
                windows_files = []
                for f in project_files:
                    # Check path patterns
                    if ("src/win" in f or 
                        "src\\win" in f or 
                        f.endswith("_win.c") or 
                        f.endswith("_win.h") or
                        "windows" in f.lower()):
                        windows_files.append(f)
                        continue
                    
                    # Check file info from MCP server
                    info_response = make_mcp_request("getFileInfo", {"path": f})
                    if "error" not in info_response and info_response.get("isWindowsFile", False):
                        windows_files.append(f)
                
                project_files = windows_files
                print(f"Filtered to {len(project_files)} Windows-specific files.")
            
            # Filter for Visual Studio project files if requested
            if args.vs_project:
                vs_files = [f for f in project_files if 
                           f.endswith(".vcxproj") or 
                           f.endswith(".sln") or 
                           f.endswith(".props") or 
                           "vs2019" in f or
                           "visual_studio" in f.lower()]
                project_files = vs_files
                print(f"Filtered to {len(project_files)} Visual Studio project files.")
            
            # Filter based on Windows API version if specified
            if args.win_api_version:
                api_version = args.win_api_version.lower()
                api_files = []
                
                for f in project_files:
                    # Read file content
                    response = make_mcp_request("readFile", {"path": f})
                    if "error" in response:
                        continue
                    
                    content = response.get("content", "")
                    
                    # Check for API version references
                    if api_version == "win32" and ("WIN32" in content or "_WIN32" in content):
                        api_files.append(f)
                    elif api_version == "win64" and ("WIN64" in content or "_WIN64" in content):
                        api_files.append(f)
                    elif api_version in content.lower():
                        api_files.append(f)
                
                project_files = api_files
                print(f"Filtered to {len(project_files)} files matching Windows API version '{api_version}'.")
            
            # Handle incremental processing
            if args.incremental:
                # Get last run timestamp from metadata file
                metadata_path = os.path.join(args.output, "metadata.json")
                last_run_time = None
                
                if os.path.exists(metadata_path):
                    try:
                        with open(metadata_path, "r") as f:
                            metadata = json.load(f)
                            last_run_time = metadata.get("last_run")
                    except Exception as e:
                        print(f"Error reading metadata: {str(e)}")
                
                if last_run_time:
                    # Filter files that have changed since last run
                    changed_files = []
                    for f in project_files:
                        info_response = make_mcp_request("getFileInfo", {"path": f})
                        if "error" not in info_response:
                            modified_time = info_response.get("modifiedAt")
                            if modified_time and modified_time > last_run_time:
                                changed_files.append(f)
                    
                    project_files = changed_files
                    print(f"Filtered to {len(project_files)} files changed since last run.")
            
            # Limit number of files if max-files specified
            if args.max_files > 0:
                project_files = project_files[:args.max_files]
                print(f"Limited to {len(project_files)} files")
    
    # Estimate completion time
    est_time = estimate_completion_time(project_files, args.delay)
    print(f"Estimated completion time: {est_time}")
    
    # Process files in batches
    batch_count = 0
    total_files = len(project_files)
    
    while project_files:
        # Process a batch of files
        batch_size = min(args.batch_size, len(project_files))
        batch = project_files[:batch_size]
        project_files = project_files[batch_size:]
        
        batch_count += 1
        print(f"\nProcessing batch {batch_count} ({batch_size} files)...")
        
        for file_path in batch:
            output_file = os.path.join(args.output, "files", os.path.basename(file_path) + ".md")
            
            # Skip if file already exists and force is not set
            if os.path.exists(output_file) and not args.force:
                if args.verbose:
                    print(f"Skipping {file_path} (already exists)")
                continue
            
            print(f"Processing {file_path}... ({len(processed_files) + 1}/{total_files})")
            
            # Build file context
            context = build_file_context(file_path)
            if "error" in context:
                print(f"Error building context for {file_path}: {context['error']}")
                continue
            
            # Analyze file with AI
            documentation = analyze_file_with_ai(context)
            
            # Save documentation
            doc_path = save_documentation(file_path, documentation, args.output)
            processed_files.append({
                "file_path": file_path,
                "doc_path": doc_path,
                "is_windows_file": context["is_windows_file"],
                "timestamp": datetime.now().isoformat()
            })
            
            # Add a delay to avoid rate limits
            if project_files:  # Only delay if there are more files to process
                print(f"Waiting {args.delay} seconds before processing next file...")
                time.sleep(args.delay)
        
        # Save checkpoint after each batch
        save_checkpoint(processed_files, project_files, args.output)
        
        # Update estimated completion time
        if project_files:
            est_time = estimate_completion_time(project_files, args.delay)
            print(f"Updated estimated completion time: {est_time}")
    
    # Group files by module
    files_by_module = {}
    for file_info in processed_files:
        file_path = file_info["file_path"]
        module = os.path.dirname(file_path) or "root"
        module = module.replace('\\', '/') # Normalize path separators
        
        if module not in files_by_module:
            files_by_module[module] = []
        
        files_by_module[module].append(file_path)
    
    # Create Windows documentation components
    windows_guide_path = create_windows_compilation_guide(args.output)
    print(f"Created Windows compilation guide at {windows_guide_path}")
    
    # Identify Windows files for the index
    windows_files = [f["file_path"] for f in processed_files if f["is_windows_file"]]
    
    if windows_files:
        windows_index_path = create_windows_documentation_index(windows_files, args.output)
        print(f"Created Windows documentation index at {windows_index_path}")
        
        # Run the Windows module creator
        try:
            print("Creating Windows module documentation...")
            from windows_module_creator import create_windows_module_page
            create_windows_module_page()
        except Exception as e:
            print(f"Error creating Windows module: {str(e)}")
    
    if not args.file:  # Skip module docs for single file processing
        # Create module documentation
        module_docs = create_module_documentation(files_by_module, args.output)
        
        # Create main documentation
        main_doc_path = create_main_documentation(module_docs, args.output)
        print(f"Created main documentation at {main_doc_path}")
    
    # Save metadata for incremental processing
    metadata = {
        "last_run": datetime.now().isoformat(),
        "processed_files": len(processed_files),
        "windows_files": len(windows_files),
        "command_line_args": vars(args)
    }
    
    with open(os.path.join(args.output, "metadata.json"), "w") as f:
        json.dump(metadata, f, indent=2)
    
    # Convert to other formats if requested
    if args.format != "markdown":
        try:
            if args.format == "html":
                print("Converting documentation to HTML...")
                # Convert markdown to HTML
                for root, dirs, files in os.walk(args.output):
                    for file in files:
                        if file.endswith(".md"):
                            md_path = os.path.join(root, file)
                            html_path = os.path.join(root, file.replace(".md", ".html"))
                            
                            with open(md_path, "r", encoding="utf-8") as f:
                                md_content = f.read()
                            
                            html_content = markdown.markdown(md_content, extensions=['tables', 'fenced_code'])
                            
                            # Add basic HTML styling
                            styled_html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{os.path.basename(file).replace(".md", "")}</title>
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; max-width: 900px; margin: 0 auto; padding: 20px; }}
        pre {{ background-color: #f5f5f5; padding: 10px; border-radius: 5px; overflow-x: auto; }}
        code {{ font-family: Consolas, monospace; }}
        table {{ border-collapse: collapse; width: 100%; }}
        th, td {{ border: 1px solid #ddd; padding: 8px; }}
        th {{ background-color: #f2f2f2; }}
        h1, h2, h3 {{ color: #333; }}
        a {{ color: #0066cc; }}
    </style>
</head>
<body>
    {html_content}
</body>
</html>"""
                            
                            with open(html_path, "w", encoding="utf-8") as f:
                                f.write(styled_html)
            
            elif args.format == "pdf":
                print("PDF conversion not implemented yet.")
                # Would require additional libraries like weasyprint or pdfkit
        
        except Exception as e:
            print(f"Error converting to {args.format}: {str(e)}")
    
    # Clean up checkpoint file if processing completed successfully
    if os.path.exists(CHECKPOINT_FILE):
        os.remove(CHECKPOINT_FILE)
        print("Checkpoint file removed as processing completed successfully")
    
    print("Documentation generation complete!")

if __name__ == "__main__":
    main()