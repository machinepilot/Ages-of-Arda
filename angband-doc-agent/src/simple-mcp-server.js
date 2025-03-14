// Import required packages
const express = require('express');
const cors = require('cors');
const fs = require('fs');
const path = require('path');
const { exec } = require('child_process');
require('dotenv').config({ path: path.join(__dirname, '..', '.env') });

// Log environment variables for debugging
console.log('Environment variables:');
console.log(`ANGBAND_SOURCE_PATH from env: ${process.env.ANGBAND_SOURCE_PATH}`);

// Get base path for Angband source code
let ANGBAND_SOURCE_PATH = process.env.ANGBAND_SOURCE_PATH || 'C:/working_directory/angband';

// Normalize path to use forward slashes
ANGBAND_SOURCE_PATH = ANGBAND_SOURCE_PATH.replace(/\\/g, '/');

console.log(`Using ANGBAND_SOURCE_PATH: ${ANGBAND_SOURCE_PATH}`);

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

// Create Express app
const app = express();
app.use(cors());
app.use(express.json());

// Define routes for the MCP server tools
app.post('/mcp/tools/readFile', async (req, res) => {
  try {
    const filePath = req.body.path;
    console.log(`Reading file: ${filePath}`);
    
    // Determine the full path correctly
    let fullPath;
    if (path.isAbsolute(filePath)) {
      fullPath = filePath;
    } else {
      fullPath = path.join(ANGBAND_SOURCE_PATH, filePath);
    }
    
    console.log(`Full path: ${fullPath}`);
    const content = fs.readFileSync(fullPath, 'utf8');
    res.json({ content });
  } catch (error) {
    console.error(`Error reading file:`, error.message);
    res.json({ error: error.message });
  }
});

app.post('/mcp/tools/listDirectory', async (req, res) => {
  try {
    // Handle both 'path' and 'directory' parameters for compatibility
    const dirPath = req.body.path || req.body.directory || '.';
    console.log(`Listing directory: ${dirPath}`);
    
    // Determine the full path correctly
    let fullPath;
    
    // Check if dirPath is already an absolute path
    if (path.isAbsolute(dirPath)) {
      fullPath = dirPath;
      console.log(`Using absolute path: ${fullPath}`);
    } else {
      fullPath = path.join(ANGBAND_SOURCE_PATH, dirPath);
      console.log(`Using relative path: ${fullPath}`);
    }
    
    console.log(`Full path: ${fullPath}`);
    
    // Get list of all files with full paths
    const getFilesRecursively = (dir) => {
      let files = [];
      try {
        console.log(`Scanning directory: ${dir}`);
        const items = fs.readdirSync(dir);
        console.log(`Found ${items.length} items in directory`);
        
        for (const item of items) {
          const itemPath = path.join(dir, item);
          try {
            const stat = fs.statSync(itemPath);
            
            if (stat.isDirectory()) {
              files = files.concat(getFilesRecursively(itemPath));
            } else {
              // Convert absolute path to relative path from ANGBAND_SOURCE_PATH
              let relativePath;
              try {
                relativePath = path.relative(ANGBAND_SOURCE_PATH, itemPath);
                // If the relative path starts with .., it means the file is outside the ANGBAND_SOURCE_PATH
                if (relativePath.startsWith('..')) {
                  console.log(`File ${itemPath} is outside the ANGBAND_SOURCE_PATH, skipping`);
                  continue;
                }
                files.push(relativePath.replace(/\\/g, '/')); // Convert Windows backslashes to forward slashes
              } catch (relativePathError) {
                console.error(`Error getting relative path for ${itemPath}:`, relativePathError.message);
              }
            }
          } catch (itemError) {
            console.error(`Error processing item ${itemPath}:`, itemError.message);
          }
        }
      } catch (dirError) {
        console.error(`Error reading directory ${dir}:`, dirError.message);
      }
      
      return files;
    };
    
    const files = getFilesRecursively(fullPath);
    console.log(`Found ${files.length} files`);
    res.json({ files });
  } catch (error) {
    console.error(`Error in listDirectory:`, error.message);
    res.json({ error: error.message });
  }
});

app.post('/mcp/tools/getFileInfo', async (req, res) => {
  try {
    const filePath = req.body.path;
    console.log(`Getting file info: ${filePath}`);
    
    // Determine the full path correctly
    let fullPath;
    if (path.isAbsolute(filePath)) {
      fullPath = filePath;
    } else {
      fullPath = path.join(ANGBAND_SOURCE_PATH, filePath);
    }
    
    console.log(`Full path: ${fullPath}`);
    const stat = fs.statSync(fullPath);
    
    res.json({
      size: stat.size,
      createdAt: stat.birthtime,
      modifiedAt: stat.mtime,
      isDirectory: stat.isDirectory(),
      extension: path.extname(fullPath),
      isWindowsFile: isWindowsFile(filePath) 
    });
  } catch (error) {
    console.error(`Error getting file info:`, error.message);
    res.json({ error: error.message });
  }
});

app.post('/mcp/tools/findFunctionReferences', async (req, res) => {
  try {
    const { functionName } = req.body;
    
    // Use PowerShell to find function references (Windows equivalent of grep)
    const command = `powershell -Command "Get-ChildItem -Path '${ANGBAND_SOURCE_PATH}' -Recurse -Include *.c,*.h | Select-String -Pattern '${functionName}\\(' | ForEach-Object { \\"$($_.Path.Substring('${ANGBAND_SOURCE_PATH}'.Length+1)):\\n$($_.Line)\\" }"`;
    
    exec(command, { maxBuffer: 1024 * 1024 * 10 }, (error, stdout, stderr) => {
      if (error && error.code !== 1) { // 1 is standard for "no matches found"
        res.json({ error: error.message });
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
      
      res.json({ references });
    });
  } catch (error) {
    res.json({ error: error.message });
  }
});

app.post('/mcp/tools/findStructDefinition', async (req, res) => {
  try {
    const { structName } = req.body;
    
    // Use PowerShell to find struct definitions
    const command = `powershell -Command "Get-ChildItem -Path '${ANGBAND_SOURCE_PATH}' -Recurse -Include *.c,*.h | Select-String -Pattern 'struct ${structName}' | ForEach-Object { \\"$($_.Path.Substring('${ANGBAND_SOURCE_PATH}'.Length+1)):\\n$($_.Line)\\" }"`;
    
    exec(command, { maxBuffer: 1024 * 1024 * 10 }, (error, stdout, stderr) => {
      if (error && error.code !== 1) {
        res.json({ error: error.message });
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
      
      res.json({ definitions });
    });
  } catch (error) {
    res.json({ error: error.message });
  }
});

// Add a ping endpoint for health checks
app.get('/mcp/ping', (req, res) => {
  res.json({ status: 'ok' });
});

// Start the server
const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
  console.log(`Simple MCP Server running on port ${PORT}`);
  console.log(`Serving Angband source from: ${ANGBAND_SOURCE_PATH}`);
}); 