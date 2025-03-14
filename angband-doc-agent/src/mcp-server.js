// Import required packages
const { MCPServer } = require('@modelcontextprotocol/server');
const express = require('express');
const cors = require('cors');
const fs = require('fs');
const path = require('path');
const { exec } = require('child_process');
require('dotenv').config({ path: path.join(__dirname, '..', '.env') });

// Helper function to identify Windows-specific files
const isWindowsFile = (filePath) => {
  // Check path patterns
  if (filePath.includes('/win/') || 
      filePath.includes('\\win\\') ||
      filePath.endsWith('_win.c') ||
      filePath.endsWith('_win.h') ||
      filePath.toLowerCase().includes('windows')) {
    return true;
  }
  
  // If we can read the file, check its contents for Windows-specific patterns
  try {
    const fullPath = path.join(ANGBAND_SOURCE_PATH, filePath);
    const content = fs.readFileSync(fullPath, 'utf8');
    
    // Check for Windows API includes
    if (content.includes('#include <windows.h>') ||
        content.includes('#include <winuser.h>') ||
        content.includes('#include <wingdi.h>') ||
        content.includes('#include <winbase.h>') ||
        content.includes('#include <commctrl.h>') ||
        content.includes('#include <commdlg.h>') ||
        content.includes('#include <shellapi.h>') ||
        content.includes('#include <mmsystem.h>')) {
      return true;
    }
    
    // Check for Windows preprocessor directives
    if (content.includes('#ifdef _WIN32') ||
        content.includes('#if defined(_WIN32)') ||
        content.includes('#ifdef WIN32') ||
        content.includes('#if defined(WIN32)') ||
        content.includes('#ifdef WINDOWS') ||
        content.includes('#if defined(WINDOWS)')) {
      return true;
    }
    
    // Check for common Windows API function calls
    if (content.includes('CreateWindow') ||
        content.includes('RegisterClass') ||
        content.includes('MessageBox') ||
        content.includes('GetMessage') ||
        content.includes('PeekMessage') ||
        content.includes('LoadIcon') ||
        content.includes('LoadCursor') ||
        content.includes('BitBlt') ||
        content.includes('PlaySound') ||
        content.includes('RegOpenKey') ||
        content.includes('ShellExecute') ||
        content.includes('HWND') ||
        content.includes('HINSTANCE') ||
        content.includes('WPARAM') ||
        content.includes('LPARAM') ||
        content.includes('LRESULT') ||
        content.includes('CALLBACK') ||
        content.includes('WINAPI')) {
      return true;
    }
    
    // Check for DirectX or other Windows graphics libraries
    if (content.includes('Direct3D') ||
        content.includes('DirectDraw') ||
        content.includes('DirectSound') ||
        content.includes('DirectInput') ||
        content.includes('D3D') ||
        content.includes('IDirect') ||
        content.includes('LPDIRECT')) {
      return true;
    }
    
    // Check for Windows resource file content
    if (content.includes('ICON') ||
        content.includes('BITMAP') ||
        content.includes('DIALOG') ||
        content.includes('MENU') ||
        content.includes('STRINGTABLE') ||
        content.includes('ACCELERATORS') ||
        content.includes('VS_VERSION_INFO')) {
      return true;
    }
  } catch (error) {
    // If we can't read the file, just use the path-based detection
    console.error(`Error reading file ${filePath} for Windows detection:`, error.message);
  }
  
  return false;
};

// Get base path for Angband source code
const ANGBAND_SOURCE_PATH = process.env.ANGBAND_SOURCE_PATH || 'C:/working_directory/angband';

// Create Express app
const app = express();
app.use(cors());
app.use(express.json());

// Create MCP server
const server = new MCPServer({
  name: "angband-doc-server",
  description: "Provides filesystem access to Angband codebase",
  tools: [
    // Tool to read a file
    {
      name: "readFile",
      description: "Read a file from the Angband codebase",
      parameters: {
        type: "object",
        properties: {
          path: { type: "string", description: "File path relative to codebase root" }
        },
        required: ["path"]
      },
      handler: async ({ path: filePath }) => {
        try {
          const fullPath = path.join(ANGBAND_SOURCE_PATH, filePath);
          const content = fs.readFileSync(fullPath, 'utf8');
          return { content };
        } catch (error) {
          return { error: error.message };
        }
      }
    },
    
    // Tool to list files in a directory
    {
      name: "listDirectory",
      description: "List all files in a directory",
      parameters: {
        type: "object",
        properties: {
          path: { type: "string", description: "Directory path relative to codebase root" }
        },
        required: ["path"]
      },
      handler: async ({ path: dirPath }) => {
        try {
          const fullPath = path.join(ANGBAND_SOURCE_PATH, dirPath);
          
          // Get list of all files with full paths
          const getFilesRecursively = (dir) => {
            let files = [];
            const items = fs.readdirSync(dir);
            
            for (const item of items) {
              const fullPath = path.join(dir, item);
              const stat = fs.statSync(fullPath);
              
              if (stat.isDirectory()) {
                files = files.concat(getFilesRecursively(fullPath));
              } else {
                // Convert absolute path to relative path from ANGBAND_SOURCE_PATH
                const relativePath = path.relative(ANGBAND_SOURCE_PATH, fullPath);
                files.push(relativePath.replace(/\\/g, '/')); // Convert Windows backslashes to forward slashes
              }
            }
            
            return files;
          };
          
          const files = getFilesRecursively(fullPath);
          return { files };
        } catch (error) {
          return { error: error.message };
        }
      }
    },
    
    // Tool to get basic file info
    {
      name: "getFileInfo",
      description: "Get information about a file",
      parameters: {
        type: "object",
        properties: {
          path: { type: "string", description: "File path relative to codebase root" }
        },
        required: ["path"]
      },
      handler: async ({ path: filePath }) => {
        try {
          const fullPath = path.join(ANGBAND_SOURCE_PATH, filePath);
          const stat = fs.statSync(fullPath);
          
          return {
            size: stat.size,
            createdAt: stat.birthtime,
            modifiedAt: stat.mtime,
            isDirectory: stat.isDirectory(),
            extension: path.extname(fullPath),
            isWindowsFile: isWindowsFile(filePath) 
          };
        } catch (error) {
          return { error: error.message };
        }
      }
    },
    
    // Tool to find function references
    {
      name: "findFunctionReferences",
      description: "Find all references to a function in the codebase",
      parameters: {
        type: "object",
        properties: {
          functionName: { type: "string", description: "Name of the function to find references for" }
        },
        required: ["functionName"]
      },
      handler: async ({ functionName }) => {
        try {
          // Use PowerShell to find function references (Windows equivalent of grep)
          return new Promise((resolve, reject) => {
            const command = `powershell -Command "Get-ChildItem -Path '${ANGBAND_SOURCE_PATH}' -Recurse -Include *.c,*.h | Select-String -Pattern '${functionName}\\(' | ForEach-Object { \\"$($_.Path.Substring('${ANGBAND_SOURCE_PATH}'.Length+1)):\\n$($_.Line)\\" }"`;
            
            exec(command, { maxBuffer: 1024 * 1024 * 10 }, (error, stdout, stderr) => {
              if (error && error.code !== 1) { // 1 is standard for "no matches found"
                reject({ error: error.message });
                return;
              }
              
              const lines = stdout.split('\n').filter(Boolean);
              const references = [];
              
              for (let i = 0; i < lines.length; i += 2) {
                if (i + 1 < lines.length) {
                  const file = lines[i].replace(':', '');
                  const line = lines[i + 1];
                  references.push({
                    file: file.replace(/\\/g, '/'), // Convert Windows backslashes to forward slashes
                    line: line.trim()
                  });
                }
              }
              
              resolve({ references });
            });
          });
        } catch (error) {
          return { error: error.message };
        }
      }
    },
    
    // Tool to find struct definitions
    {
      name: "findStructDefinition",
      description: "Find the definition of a struct in the codebase",
      parameters: {
        type: "object",
        properties: {
          structName: { type: "string", description: "Name of the struct to find" }
        },
        required: ["structName"]
      },
      handler: async ({ structName }) => {
        try {
          // Use PowerShell to find struct definitions
          return new Promise((resolve, reject) => {
            const command = `powershell -Command "Get-ChildItem -Path '${ANGBAND_SOURCE_PATH}' -Recurse -Include *.c,*.h | Select-String -Pattern 'struct ${structName}' | ForEach-Object { \\"$($_.Path.Substring('${ANGBAND_SOURCE_PATH}'.Length+1)):\\n$($_.Line)\\" }"`;
            
            exec(command, { maxBuffer: 1024 * 1024 * 10 }, (error, stdout, stderr) => {
              if (error && error.code !== 1) {
                reject({ error: error.message });
                return;
              }
              
              const lines = stdout.split('\n').filter(Boolean);
              let definitions = [];
              
              for (let i = 0; i < lines.length; i += 2) {
                if (i + 1 < lines.length) {
                  const file = lines[i].replace(':', '');
                  const match = lines[i + 1];
                  
                  if (match.includes('{')) {
                    // Probably found the start of a struct definition
                    try {
                      const content = fs.readFileSync(path.join(ANGBAND_SOURCE_PATH, file), 'utf8');
                      const startIndex = content.indexOf(match);
                      if (startIndex !== -1) {
                        // Find the matching closing brace
                        let braceCount = 0;
                        let endIndex = startIndex;
                        
                        for (let i = startIndex; i < content.length; i++) {
                          if (content[i] === '{') braceCount++;
                          if (content[i] === '}') {
                            braceCount--;
                            if (braceCount === 0) {
                              endIndex = i + 1;
                              break;
                            }
                          }
                        }
                        
                        if (endIndex > startIndex) {
                          const definition = content.substring(startIndex, endIndex);
                          definitions.push({
                            file: file.replace(/\\/g, '/'),
                            definition
                          });
                        }
                      }
                    } catch (readError) {
                      console.error(`Error reading file ${file}:`, readError);
                    }
                  } else {
                    // Just a reference, not a definition
                    definitions.push({
                      file: file.replace(/\\/g, '/'),
                      reference: match.trim()
                    });
                  }
                }
              }
              
              resolve({ definitions });
            });
          });
        } catch (error) {
          return { error: error.message };
        }
      }
    }
  ]
});

// Integrate MCP server with Express
app.use('/mcp', server.expressMiddleware());

// Start the server
const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
  console.log(`MCP Server running on port ${PORT}`);
  console.log(`Serving Angband source from: ${ANGBAND_SOURCE_PATH}`);
});