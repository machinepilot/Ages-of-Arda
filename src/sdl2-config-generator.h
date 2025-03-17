#ifndef INCLUDED_SDL2_CONFIG_GENERATOR_H
#define INCLUDED_SDL2_CONFIG_GENERATOR_H

/**
 * @file sdl2-config-generator.h
 * @brief Dynamically generate SDL2 configuration based on screen resolution
 */

#ifdef USE_SDL2

/**
 * Generate a proper SDL2 configuration file based on current display resolution.
 * This function detects the user's screen size and creates an optimized sdl2init.txt
 * file with appropriate window and subwindow layouts.
 *
 * @return true if the configuration was generated successfully, false otherwise
 */
bool generate_sdl2_config(void);

#endif /* USE_SDL2 */

#endif /* INCLUDED_SDL2_CONFIG_GENERATOR_H */ 