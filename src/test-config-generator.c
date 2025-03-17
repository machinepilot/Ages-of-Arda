#include "angband.h"
#include "sdl2-config-generator.h"
#include "z-file.h"
#include "init.h"

#ifdef USE_SDL2
#include <SDL.h>

/**
 * Simple test program for the SDL2 configuration generator
 */
int main(int argc, char *argv[]) {
    /* Initialize SDL for display detection */
    if (SDL_Init(SDL_INIT_VIDEO) != 0) {
        printf("Failed to initialize SDL: %s\n", SDL_GetError());
        return 1;
    }
    
    /* Initialize any necessary Angband systems */
    init_file_paths(".");
    
    /* Test the generation of the configuration file */
    bool result = generate_sdl2_config();
    
    /* Clean up SDL */
    SDL_Quit();
    
    /* Check the result */
    if (result) {
        printf("SDL2 configuration file generated successfully!\n");
        
        /* Read and display part of the generated file */
        char config_path[1024];
        path_build(config_path, sizeof(config_path), ANGBAND_DIR_USER, "sdl2init.txt");
        
        ang_file *config_file = file_open(config_path, MODE_READ, FTYPE_TEXT);
        if (config_file) {
            char line[1024];
            int line_count = 0;
            
            printf("\nContents of sdl2init.txt (first 10 lines):\n");
            printf("--------------------------------------------\n");
            
            while (file_getl(config_file, line, sizeof(line)) && line_count < 10) {
                printf("%s\n", line);
                line_count++;
            }
            
            printf("--------------------------------------------\n");
            file_close(config_file);
        }
        
        return 0;
    } else {
        printf("Failed to generate SDL2 configuration file.\n");
        return 1;
    }
}

#else /* !USE_SDL2 */

int main(int argc, char *argv[]) {
    printf("SDL2 support is not enabled.\n");
    return 1;
}

#endif /* USE_SDL2 */ 