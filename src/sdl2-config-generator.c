#include "angband.h"

#ifdef USE_SDL2

#include <SDL.h>
#include "z-file.h"
#include "z-util.h"
#include "init.h"

/* Add these constants near the top after includes */
#define DEFAULT_FONT_MAIN "16x24x.fon"
#define DEFAULT_FONT_SUB "12x18x.fon"
#define DEFAULT_FONT_MSG "10x20x.fon"
#define DEFAULT_FONT_MENU "10x20x.fon"

/* Add this function before generate_sdl2_config */
/**
 * Calculate optimal font size based on screen resolution
 */
static void adjust_font_size(char *font_name, int screen_height, bool is_main) {
    /* For high resolution displays (4K+), use larger fonts */
    if (screen_height >= 2160) {
        if (is_main) {
            my_strcpy(font_name, "20x30x.fon", 16);
        } else {
            my_strcpy(font_name, "16x24x.fon", 16);
        }
    } else if (screen_height >= 1440) {
        if (is_main) {
            my_strcpy(font_name, "16x24x.fon", 16);
        } else {
            my_strcpy(font_name, "12x18x.fon", 16);
        }
    } else {
        if (is_main) {
            my_strcpy(font_name, "12x18x.fon", 16);
        } else {
            my_strcpy(font_name, "10x16x.fon", 16);
        }
    }
}

/**
 * Generate an optimized SDL2 configuration file based on current display resolution
 */
bool generate_sdl2_config(void) {
    SDL_Rect display_bounds;
    int screen_width, screen_height;
    char config_path[1024];
    ang_file *config_file;
    
    /* Initialize SDL just for getting display information */
    if (SDL_Init(SDL_INIT_VIDEO) != 0) {
        return false;
    }
    
    /* Get screen dimensions, fallback to 2560x1660 if not available */
    if (SDL_GetDisplayBounds(0, &display_bounds) != 0) {
        screen_width = 2560;
        screen_height = 1660;
    } else {
        screen_width = display_bounds.w;
        screen_height = display_bounds.h;
    }
    
    /* Calculate dimensions - 100% of screen size for fullscreen */
    int main_width = screen_width;
    int main_height = screen_height;
    int main_x = 0;
    int main_y = 0;
    
    /* Calculate dimensions for windowed mode (90% of screen) */
    int window_main_width = screen_width * 0.9;
    int window_main_height = screen_height * 0.9;
    int window_main_x = (screen_width - window_main_width) / 2;
    int window_main_y = (screen_height - window_main_height) / 2;
    
    /* Calculate better positioned subwindows to avoid overlap */
    /* Main game area (center) */
    int sw0_x = screen_width * 0.2;
    int sw0_y = screen_height * 0.14;
    int sw0_w = screen_width * 0.6;
    int sw0_h = screen_height * 0.7;
    
    /* Left side inventory panel */
    int sw1_x = screen_width * 0.02;
    int sw1_y = screen_height * 0.14;
    int sw1_w = screen_width * 0.16;
    int sw1_h = screen_height * 0.42;
    
    /* Message window (bottom center) */
    int sw2_x = sw0_x;
    int sw2_y = screen_height * 0.85;
    int sw2_w = sw0_w;
    int sw2_h = screen_height * 0.14;
    
    /* Monster recall (bottom left) */
    int sw3_x = screen_width * 0.02;
    int sw3_y = screen_height * 0.58;
    int sw3_w = screen_width * 0.16;
    int sw3_h = screen_height * 0.41;
    
    /* Right side top panel */
    int sw4_x = screen_width * 0.82;
    int sw4_y = screen_height * 0.14;
    int sw4_w = screen_width * 0.16;
    int sw4_h = screen_height * 0.28;
    
    /* Right side middle panel */
    int sw5_x = screen_width * 0.82;
    int sw5_y = screen_height * 0.44;
    int sw5_w = screen_width * 0.16;
    int sw5_h = screen_height * 0.28;
    
    /* Companion window (right side bottom) */
    int sw6_x = screen_width * 0.82;
    int sw6_y = screen_height * 0.74;
    int sw6_w = screen_width * 0.16;
    int sw6_h = screen_height * 0.25;
    
    /* Calculate dimensions for submenus to fill empty space */
    int menu_height = screen_height * 0.04;  // 4% of screen height for each menu
    int menu_spacing = screen_height * 0.01;  // 1% spacing between menus
    int menu_x = sw0_x;  // Align with main game window
    int menu_width = sw0_w;  // Same width as main game window
    int menu_y = sw0_y - (menu_height + menu_spacing) * 3;  // Position above main window
    
    /* Build path to config file */
    path_build(config_path, sizeof(config_path), ANGBAND_DIR_USER, "sdl2init.txt");
    
    /* Open config file for writing */
    config_file = file_open(config_path, MODE_WRITE, FTYPE_TEXT);
    if (config_file == NULL) {
        SDL_Quit();
        return false;
    }
    
    /* Window configuration */
    file_putf(config_file, "/* Main window configuration */\n");
    file_putf(config_file, "window-display:0:0\n");
    file_putf(config_file, "window-full-rect:0:%d:%d:%d:%d\n", window_main_x, window_main_y, window_main_width, window_main_height);
    file_putf(config_file, "window-full-rect-fs:0:0:0:%d:%d\n", screen_width, screen_height);
    file_putf(config_file, "window-fullscreen:0:true\n");
    file_putf(config_file, "window-renderer:0:hardware\n");
    file_putf(config_file, "window-wallpaper-path:0:.\\lib\\icons\\att-128.png\n");
    file_putf(config_file, "window-wallpaper-mode:0:tiled\n");
    
    /* Adjust fonts based on resolution */
    char main_font[16], sub_font[16], msg_font[16], menu_font[16];
    adjust_font_size(main_font, screen_height, true);
    adjust_font_size(sub_font, screen_height, false);
    my_strcpy(msg_font, DEFAULT_FONT_MSG, sizeof(msg_font));
    my_strcpy(menu_font, DEFAULT_FONT_MENU, sizeof(menu_font));
    
    file_putf(config_file, "window-status-bar-font:0:0:%s\n", menu_font);
    file_putf(config_file, "window-graphics-id:0:3\n");
    file_putf(config_file, "window-tile-scale:0:width:2\n");
    file_putf(config_file, "window-tile-scale:0:height:2\n");
    file_putf(config_file, "\n");

    /* Main game window (0) - Map display */
    file_putf(config_file, "/* Main game area */\n");
    file_putf(config_file, "subwindow-window:0:0:1\n");
    file_putf(config_file, "subwindow-full-rect:0:%d:%d:%d:%d\n", 
              (int)(window_main_width * 0.2), (int)(window_main_height * 0.14),
              (int)(window_main_width * 0.6), (int)(window_main_height * 0.7));
    file_putf(config_file, "subwindow-full-rect-fs:0:%d:%d:%d:%d\n", sw0_x, sw0_y, sw0_w, sw0_h);
    file_putf(config_file, "subwindow-font:0:0:%s\n", main_font);
    file_putf(config_file, "subwindow-borders:0:true\n");
    file_putf(config_file, "subwindow-top:0:true:false\n");
    file_putf(config_file, "subwindow-alpha:0:255\n");
    file_putf(config_file, "\n");
    
    /* Items window (1) - Inventory */
    file_putf(config_file, "/* Inventory panel */\n");
    file_putf(config_file, "subwindow-window:1:0:1\n");
    file_putf(config_file, "subwindow-full-rect:1:%d:%d:%d:%d\n", 
              (int)(window_main_width * 0.02), (int)(window_main_height * 0.14),
              (int)(window_main_width * 0.16), (int)(window_main_height * 0.42));
    file_putf(config_file, "subwindow-full-rect-fs:1:%d:%d:%d:%d\n", sw1_x, sw1_y, sw1_w, sw1_h);
    file_putf(config_file, "subwindow-font:1:0:%s\n", sub_font);
    file_putf(config_file, "subwindow-borders:1:true\n");
    file_putf(config_file, "subwindow-top:1:false:false\n");
    file_putf(config_file, "subwindow-alpha:1:255\n");
    file_putf(config_file, "\n");
    
    /* Message window (2) */
    file_putf(config_file, "/* Message window */\n");
    file_putf(config_file, "subwindow-window:2:0:1\n");
    file_putf(config_file, "subwindow-full-rect:2:%d:%d:%d:%d\n", 
              (int)(window_main_width * 0.2), (int)(window_main_height * 0.85),
              (int)(window_main_width * 0.6), (int)(window_main_height * 0.14));
    file_putf(config_file, "subwindow-full-rect-fs:2:%d:%d:%d:%d\n", sw2_x, sw2_y, sw2_w, sw2_h);
    file_putf(config_file, "subwindow-font:2:0:%s\n", msg_font);
    file_putf(config_file, "subwindow-borders:2:true\n");
    file_putf(config_file, "subwindow-top:2:false:false\n");
    file_putf(config_file, "subwindow-alpha:2:255\n");
    file_putf(config_file, "\n");
    
    /* Monster recall window (3) */
    file_putf(config_file, "/* Monster recall */\n");
    file_putf(config_file, "subwindow-window:3:0:1\n");
    file_putf(config_file, "subwindow-full-rect:3:%d:%d:%d:%d\n", 
              (int)(window_main_width * 0.02), (int)(window_main_height * 0.58),
              (int)(window_main_width * 0.16), (int)(window_main_height * 0.41));
    file_putf(config_file, "subwindow-full-rect-fs:3:%d:%d:%d:%d\n", sw3_x, sw3_y, sw3_w, sw3_h);
    file_putf(config_file, "subwindow-font:3:0:%s\n", sub_font);
    file_putf(config_file, "subwindow-borders:3:true\n");
    file_putf(config_file, "subwindow-top:3:false:false\n");
    file_putf(config_file, "subwindow-alpha:3:255\n");
    file_putf(config_file, "\n");
    
    /* Monsters in sight window (4) */
    file_putf(config_file, "/* Visible monsters */\n");
    file_putf(config_file, "subwindow-window:4:0:1\n");
    file_putf(config_file, "subwindow-full-rect:4:%d:%d:%d:%d\n", 
              (int)(window_main_width * 0.82), (int)(window_main_height * 0.14),
              (int)(window_main_width * 0.16), (int)(window_main_height * 0.28));
    file_putf(config_file, "subwindow-full-rect-fs:4:%d:%d:%d:%d\n", sw4_x, sw4_y, sw4_w, sw4_h);
    file_putf(config_file, "subwindow-font:4:0:%s\n", sub_font);
    file_putf(config_file, "subwindow-borders:4:true\n");
    file_putf(config_file, "subwindow-top:4:false:false\n");
    file_putf(config_file, "subwindow-alpha:4:255\n");
    file_putf(config_file, "\n");
    
    /* Inventory window (5) */
    file_putf(config_file, "/* Equipment */\n");
    file_putf(config_file, "subwindow-window:5:0:1\n");
    file_putf(config_file, "subwindow-full-rect:5:%d:%d:%d:%d\n", 
              (int)(window_main_width * 0.82), (int)(window_main_height * 0.44),
              (int)(window_main_width * 0.16), (int)(window_main_height * 0.28));
    file_putf(config_file, "subwindow-full-rect-fs:5:%d:%d:%d:%d\n", sw5_x, sw5_y, sw5_w, sw5_h);
    file_putf(config_file, "subwindow-font:5:0:%s\n", sub_font);
    file_putf(config_file, "subwindow-borders:5:true\n");
    file_putf(config_file, "subwindow-top:5:false:false\n");
    file_putf(config_file, "subwindow-alpha:5:255\n");
    file_putf(config_file, "\n");
    
    /* Companion window (6) */
    file_putf(config_file, "/* Companion status */\n");
    file_putf(config_file, "subwindow-window:6:0:1\n");
    file_putf(config_file, "subwindow-full-rect:6:%d:%d:%d:%d\n", 
              (int)(window_main_width * 0.82), (int)(window_main_height * 0.74),
              (int)(window_main_width * 0.16), (int)(window_main_height * 0.25));
    file_putf(config_file, "subwindow-full-rect-fs:6:%d:%d:%d:%d\n", sw6_x, sw6_y, sw6_w, sw6_h);
    file_putf(config_file, "subwindow-font:6:0:%s\n", sub_font);
    file_putf(config_file, "subwindow-borders:6:true\n");
    file_putf(config_file, "subwindow-top:6:false:false\n");
    file_putf(config_file, "subwindow-alpha:6:255\n");
    file_putf(config_file, "\n");
    
    /* Menu settings */
    file_putf(config_file, "menu-shortcut:0:Alt+F\n");
    file_putf(config_file, "menu-shortcut:1:Alt+E\n");
    file_putf(config_file, "menu-shortcut:2:Alt+H\n");
    file_putf(config_file, "menu-shortcut:3:Alt+W\n");
    file_putf(config_file, "menu-shortcut:4:Alt+O\n");
    file_putf(config_file, "menu-shortcut:5:Alt+C\n");
    
    /* Menu window configurations */
    file_putf(config_file, "\n/* File Menu */\n");
    file_putf(config_file, "menu-window:0:0:1\n");
    file_putf(config_file, "menu-full-rect:0:%d:%d:%d:%d\n", 
              (int)(window_main_width * 0.2), (int)(window_main_height * 0.05),
              (int)(window_main_width * 0.6), (int)(window_main_height * 0.04));
    file_putf(config_file, "menu-full-rect-fs:0:%d:%d:%d:%d\n", menu_x, menu_y, menu_width, menu_height);
    file_putf(config_file, "menu-font:0:0:10x20x.fon\n");
    file_putf(config_file, "menu-borders:0:true\n");
    file_putf(config_file, "menu-top:0:true:false\n");
    file_putf(config_file, "menu-alpha:0:255\n");
    file_putf(config_file, "\n");
    
    /* Edit Menu */
    file_putf(config_file, "menu-window:1:0:1\n");
    file_putf(config_file, "menu-full-rect:1:%d:%d:%d:%d\n", 
              (int)(window_main_width * 0.2), (int)(window_main_height * 0.09),
              (int)(window_main_width * 0.6), (int)(window_main_height * 0.04));
    file_putf(config_file, "menu-full-rect-fs:1:%d:%d:%d:%d\n", menu_x, menu_y + menu_height + menu_spacing, menu_width, menu_height);
    file_putf(config_file, "menu-font:1:0:10x20x.fon\n");
    file_putf(config_file, "menu-borders:1:true\n");
    file_putf(config_file, "menu-top:1:true:false\n");
    file_putf(config_file, "menu-alpha:1:255\n");
    file_putf(config_file, "\n");
    
    /* Help Menu */
    file_putf(config_file, "menu-window:2:0:1\n");
    file_putf(config_file, "menu-full-rect:2:%d:%d:%d:%d\n", 
              (int)(window_main_width * 0.2), (int)(window_main_height * 0.13),
              (int)(window_main_width * 0.6), (int)(window_main_height * 0.04));
    file_putf(config_file, "menu-full-rect-fs:2:%d:%d:%d:%d\n", menu_x, menu_y + (menu_height + menu_spacing) * 2, menu_width, menu_height);
    file_putf(config_file, "menu-font:2:0:10x20x.fon\n");
    file_putf(config_file, "menu-borders:2:true\n");
    file_putf(config_file, "menu-top:2:true:false\n");
    file_putf(config_file, "menu-alpha:2:255\n");
    file_putf(config_file, "\n");
    
    /* Window Menu */
    file_putf(config_file, "menu-window:3:0:1\n");
    file_putf(config_file, "menu-full-rect:3:%d:%d:%d:%d\n", 
              (int)(window_main_width * 0.2), (int)(window_main_height * 0.17),
              (int)(window_main_width * 0.6), (int)(window_main_height * 0.04));
    file_putf(config_file, "menu-full-rect-fs:3:%d:%d:%d:%d\n", menu_x, menu_y + (menu_height + menu_spacing) * 3, menu_width, menu_height);
    file_putf(config_file, "menu-font:3:0:10x20x.fon\n");
    file_putf(config_file, "menu-borders:3:true\n");
    file_putf(config_file, "menu-top:3:true:false\n");
    file_putf(config_file, "menu-alpha:3:255\n");
    file_putf(config_file, "\n");
    
    /* Options Menu */
    file_putf(config_file, "menu-window:4:0:1\n");
    file_putf(config_file, "menu-full-rect:4:%d:%d:%d:%d\n", 
              (int)(window_main_width * 0.2), (int)(window_main_height * 0.21),
              (int)(window_main_width * 0.6), (int)(window_main_height * 0.04));
    file_putf(config_file, "menu-full-rect-fs:4:%d:%d:%d:%d\n", menu_x, menu_y + (menu_height + menu_spacing) * 4, menu_width, menu_height);
    file_putf(config_file, "menu-font:4:0:10x20x.fon\n");
    file_putf(config_file, "menu-borders:4:true\n");
    file_putf(config_file, "menu-top:4:true:false\n");
    file_putf(config_file, "menu-alpha:4:255\n");
    file_putf(config_file, "\n");
    
    /* Character Menu */
    file_putf(config_file, "menu-window:5:0:1\n");
    file_putf(config_file, "menu-full-rect:5:%d:%d:%d:%d\n", 
              (int)(window_main_width * 0.2), (int)(window_main_height * 0.25),
              (int)(window_main_width * 0.6), (int)(window_main_height * 0.04));
    file_putf(config_file, "menu-full-rect-fs:5:%d:%d:%d:%d\n", menu_x, menu_y + (menu_height + menu_spacing) * 5, menu_width, menu_height);
    file_putf(config_file, "menu-font:5:0:10x20x.fon\n");
    file_putf(config_file, "menu-borders:5:true\n");
    file_putf(config_file, "menu-top:5:true:false\n");
    file_putf(config_file, "menu-alpha:5:255\n");
    file_putf(config_file, "\n");
    
    /* Additional menu settings */
    file_putf(config_file, "kp-as-modifier:1\n");
    
    /* Close the file */
    file_close(config_file);
    
    /* Clean up */
    SDL_Quit();
    
    return true;
}

#endif /* USE_SDL2 */ 