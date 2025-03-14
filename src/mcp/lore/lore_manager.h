/**
 * lore_manager.h
 * Functions for retrieving lore data from the memory bank.
 */

#ifndef INCLUDED_LORE_MANAGER_H
#define INCLUDED_LORE_MANAGER_H

#include <stdbool.h>
#include "../mcp_server.h"

/**
 * Lore data type representing age-specific lore
 */
typedef struct lore_data_t {
    char *content;         /* The lore content text */
    char *source;          /* Source of the lore (book, chapter) */
    char *age;             /* Age identifier (first_age, third_age, etc.) */
    int year;              /* Year within the age */
    bool is_canonical;     /* Whether this is canonical or generated */
} lore_data_t;

/**
 * Lore manager structure to handle lore retrieval and caching
 */
typedef struct lore_manager_t {
    char *memory_bank_path;        /* Path to the memory bank directory */
    void *lore_cache;              /* Cache for recently accessed lore */
    unsigned int cache_size;       /* Size of the lore cache */
    unsigned int cache_hits;       /* Number of cache hits */
    unsigned int cache_misses;     /* Number of cache misses */
} lore_manager_t;

/**
 * Initialize the lore manager
 *
 * @param memory_bank_path Path to the memory bank directory
 * @return Initialized lore manager or NULL on failure
 */
lore_manager_t *
init_lore_manager(const char *memory_bank_path);

/**
 * Free resources used by the lore manager
 *
 * @param manager The lore manager to free
 */
void
free_lore_manager(lore_manager_t *manager);

/**
 * Get lore about a character from a specific age
 *
 * @param manager The lore manager
 * @param character_name The name of the character
 * @param age The age to get lore from (NULL for all ages)
 * @return Lore data for the character or NULL if not found
 */
lore_data_t *
get_character_lore(lore_manager_t *manager, const char *character_name, const char *age);

/**
 * Get lore about a location from a specific age
 *
 * @param manager The lore manager
 * @param location_name The name of the location
 * @param age The age to get lore from (NULL for all ages)
 * @return Lore data for the location or NULL if not found
 */
lore_data_t *
get_location_lore(lore_manager_t *manager, const char *location_name, const char *age);

/**
 * Get lore about an artifact or item from a specific age
 *
 * @param manager The lore manager
 * @param artifact_name The name of the artifact
 * @param age The age to get lore from (NULL for all ages)
 * @return Lore data for the artifact or NULL if not found
 */
lore_data_t *
get_artifact_lore(lore_manager_t *manager, const char *artifact_name, const char *age);

/**
 * Get a random lore snippet related to the current age
 *
 * @param manager The lore manager
 * @param age The age to get lore from
 * @param topic Optional topic filter (character, location, event, etc.)
 * @return Random lore data or NULL if none available
 */
lore_data_t *
get_random_lore(lore_manager_t *manager, const char *age, const char *topic);

/**
 * Get lore for a companion based on their background
 *
 * @param manager The lore manager
 * @param companion_name The name of the companion
 * @param age The current age
 * @return Lore data relevant to the companion or NULL if none available
 */
lore_data_t *
get_companion_lore(lore_manager_t *manager, const char *companion_name, const char *age);

/**
 * Free a lore data structure
 *
 * @param lore The lore data to free
 */
void
free_lore_data(lore_data_t *lore);

/**
 * Register lore-related tools with the MCP server
 *
 * @param server The MCP server
 * @param manager The lore manager
 * @return true if registration was successful, false otherwise
 */
bool
register_lore_tools(mcp_server_t *server, lore_manager_t *manager);

#endif /* INCLUDED_LORE_MANAGER_H */ 