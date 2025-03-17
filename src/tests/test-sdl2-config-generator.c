#include "unit-test.h"
#include "z-file.h"
#include "init.h"
#include "sdl2-config-generator.h"

#ifdef USE_SDL2

/**
 * Test that the SDL2 configuration generator creates a valid configuration file
 */
static int test_sdl2_config_generator(void *state) {
    char config_path[1024];
    ang_file *config_file;
    char line[1024];
    bool found_main_window = false;
    bool found_subwindow_6 = false;
    
    /* Delete any existing config file to ensure we're testing the generator */
    path_build(config_path, sizeof(config_path), ANGBAND_DIR_USER, "sdl2init.txt");
    file_delete(config_path);
    
    /* Generate the configuration file */
    require(generate_sdl2_config());
    
    /* Verify the file was created */
    config_file = file_open(config_path, MODE_READ, FTYPE_TEXT);
    require(config_file != NULL);
    
    /* Check for key configuration elements */
    while (file_getl(config_file, line, sizeof(line))) {
        /* Check for main window configuration */
        if (strstr(line, "window-full-rect:0:") != NULL) {
            found_main_window = true;
        }
        
        /* Check for companion subwindow (the 7th one) */
        if (strstr(line, "subwindow-window:6:0:1") != NULL) {
            found_subwindow_6 = true;
        }
    }
    
    file_close(config_file);
    
    /* Verify we found the required elements */
    require(found_main_window);
    require(found_subwindow_6);
    
    return 0;
}

/**
 * Test that the SDL2 configuration generator handles screen dimensions correctly
 */
static int test_sdl2_config_dimensions(void *state) {
    char config_path[1024];
    ang_file *config_file;
    char line[1024];
    int main_width = 0, main_height = 0;
    int sw0_width = 0, sw0_height = 0;
    
    /* Delete any existing config file to ensure we're testing the generator */
    path_build(config_path, sizeof(config_path), ANGBAND_DIR_USER, "sdl2init.txt");
    file_delete(config_path);
    
    /* Generate the configuration file */
    require(generate_sdl2_config());
    
    /* Verify the file was created */
    config_file = file_open(config_path, MODE_READ, FTYPE_TEXT);
    require(config_file != NULL);
    
    /* Extract window dimensions */
    while (file_getl(config_file, line, sizeof(line))) {
        int x, y, w, h;
        
        /* Parse main window dimensions */
        if (sscanf(line, "window-full-rect:0:%d:%d:%d:%d", &x, &y, &w, &h) == 4) {
            main_width = w;
            main_height = h;
        }
        
        /* Parse main subwindow dimensions */
        if (sscanf(line, "subwindow-full-rect:0:%d:%d:%d:%d", &x, &y, &w, &h) == 4) {
            sw0_width = w;
            sw0_height = h;
        }
    }
    
    file_close(config_file);
    
    /* Verify dimensions are reasonable */
    require(main_width > 0);
    require(main_height > 0);
    require(sw0_width > 0);
    require(sw0_height > 0);
    
    /* Main subwindow should be smaller than main window */
    require(sw0_width < main_width);
    require(sw0_height < main_height);
    
    return 0;
}

const char *suite_name = "sdl2/config-generator";
struct test tests[] = {
    { "sdl2-config-generator", test_sdl2_config_generator },
    { "sdl2-config-dimensions", test_sdl2_config_dimensions },
    { NULL, NULL }
};

#else /* !USE_SDL2 */

const char *suite_name = "sdl2/config-generator";
struct test tests[] = {
    { NULL, NULL }
};

#endif /* USE_SDL2 */ 