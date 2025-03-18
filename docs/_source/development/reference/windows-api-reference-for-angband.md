---
title: Windows API Reference for Angband
id: windows-api-reference-for-angband
section: development
category: reference
created: '2025-03-14'
updated: '2025-03-13'
version: 0.1.0
---

# Windows API Reference for Angband

This document provides a reference for the Windows API functions commonly used in the Angband Windows port.

## Window Management

### Window Creation and Handling
- **CreateWindow**: Creates a window with specified properties
- **RegisterClass**: Registers a window class for use
- **ShowWindow**: Sets the window's show state
- **UpdateWindow**: Forces an immediate repaint of the window
- **DestroyWindow**: Destroys a window

### Window Messaging
- **GetMessage**: Retrieves a message from the thread's message queue
- **PeekMessage**: Checks for messages without removing them from the queue
- **TranslateMessage**: Translates virtual-key messages into character messages
- **DispatchMessage**: Dispatches a message to a window procedure
- **PostMessage**: Posts a message to a thread's message queue
- **SendMessage**: Sends a message to a window and waits for processing

### Window Procedure
- **WNDPROC**: Function pointer type for window procedures
- **DefWindowProc**: Default window procedure for messages not handled by the application

## Graphics and Display

### Device Contexts
- **GetDC**: Retrieves a device context for a window
- **ReleaseDC**: Releases a device context
- **CreateCompatibleDC**: Creates a memory device context
- **DeleteDC**: Deletes a device context

### Bitmap Handling
- **CreateCompatibleBitmap**: Creates a bitmap compatible with a device
- **SelectObject**: Selects an object into a device context
- **DeleteObject**: Deletes a GDI object
- **BitBlt**: Performs a bit-block transfer of color data
- **StretchBlt**: Copies a bitmap with stretching or compression

### Drawing Functions
- **TextOut**: Writes text at a specified location
- **ExtTextOut**: Writes text with more formatting options
- **Rectangle**: Draws a rectangle
- **FillRect**: Fills a rectangle with a specified brush
- **DrawText**: Draws formatted text in a rectangle

### Font Management
- **CreateFont**: Creates a logical font with specified characteristics
- **GetTextMetrics**: Retrieves metrics for the current font

## Input Handling

### Keyboard Input
- **GetAsyncKeyState**: Determines if a key is currently pressed
- **GetKeyState**: Retrieves the status of a virtual key
- **MapVirtualKey**: Maps a virtual-key code to a scan code or character value

### Mouse Input
- **GetCursorPos**: Retrieves the cursor's position
- **SetCursorPos**: Moves the cursor to a specified position
- **ShowCursor**: Shows or hides the cursor
- **SetCapture**: Captures mouse input
- **ReleaseCapture**: Releases mouse capture

## Resource Management

### Icons and Cursors
- **LoadIcon**: Loads an icon resource
- **LoadCursor**: Loads a cursor resource
- **SetCursor**: Sets the cursor shape

### Menus
- **LoadMenu**: Loads a menu resource
- **GetMenu**: Retrieves a handle to a window's menu
- **SetMenu**: Assigns a menu to a window
- **EnableMenuItem**: Enables or disables a menu item

### Dialog Boxes
- **DialogBox**: Creates a modal dialog box
- **CreateDialog**: Creates a modeless dialog box
- **EndDialog**: Destroys a modal dialog box
- **GetDlgItem**: Retrieves a handle to a control in a dialog box
- **SetDlgItemText**: Sets the text of a control in a dialog box

## File Operations

### File I/O
- **CreateFile**: Creates or opens a file or device
- **ReadFile**: Reads data from a file
- **WriteFile**: Writes data to a file
- **CloseHandle**: Closes an open object handle

### File System
- **FindFirstFile**: Searches a directory for a file or subdirectory
- **FindNextFile**: Continues a file search
- **FindClose**: Closes a file search handle

## Sound and Multimedia

### Sound Playback
- **PlaySound**: Plays a sound specified by a filename, resource, or system event
- **waveOutOpen**: Opens a waveform audio output device
- **waveOutWrite**: Sends a data block to a waveform audio output device
- **waveOutClose**: Closes a waveform audio output device

## Memory Management

### Heap Functions
- **GlobalAlloc**: Allocates memory from the global heap
- **GlobalLock**: Locks a global memory object and returns a pointer
- **GlobalUnlock**: Unlocks a global memory object
- **GlobalFree**: Frees a global memory object
- **VirtualAlloc**: Reserves or commits memory pages
- **VirtualFree**: Releases memory pages

## Registry Access

### Registry Functions
- **RegOpenKeyEx**: Opens a registry key
- **RegQueryValueEx**: Retrieves the type and data for a registry value
- **RegSetValueEx**: Sets the data and type of a registry value
- **RegCloseKey**: Closes a registry key

## Common Structures

### Window-Related Structures
- **WNDCLASS**: Contains window class information
- **MSG**: Contains message information from a thread's message queue
- **RECT**: Defines a rectangle by coordinates
- **POINT**: Defines the x- and y-coordinates of a point
- **PAINTSTRUCT**: Contains information for painting a window

### Graphics-Related Structures
- **BITMAPINFO**: Defines the dimensions and color information for a DIB
- **TEXTMETRIC**: Contains metrics for a font
- **LOGFONT**: Defines the attributes of a font

## Best Practices

1. **Error Handling**: Always check return values from Windows API functions
   ```c
   HWND hwnd = CreateWindow(...);
   if (hwnd == NULL) {
       // Handle error
       DWORD error = GetLastError();
       // Log or display error
   }
   ```

2. **Resource Management**: Release resources when done
   ```c
   // Device contexts
   DeleteDC(hdc);
   
   // GDI objects
   DeleteObject(hBitmap);
   
   // Handles
   CloseHandle(hFile);
   ```

3. **Unicode Support**: Use the wide-character versions of functions for better internationalization
   ```c
   // Instead of CreateWindowA, use:
   CreateWindowW(L"ClassName", L"Title", ...);
   ```

4. **Thread Safety**: Be careful with shared resources in multi-threaded code
   ```c
   // Use synchronization objects
   EnterCriticalSection(&cs);
   // Access shared resource
   LeaveCriticalSection(&cs);
   ```

5. **DPI Awareness**: Handle high-DPI displays properly
   ```c
   // Set DPI awareness
   SetProcessDPIAware();
   
   // Get DPI for scaling
   HDC hdc = GetDC(NULL);
   int dpiX = GetDeviceCaps(hdc, LOGPIXELSX);
   int dpiY = GetDeviceCaps(hdc, LOGPIXELSY);
   ReleaseDC(NULL, hdc);
   ``` 