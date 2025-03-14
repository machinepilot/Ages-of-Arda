/**
 * lore_manager.c
 * Implementation of the lore management system.
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdbool.h>
#include <ctype.h>
#include <dirent.h>

#include "lore_manager.h"
#include "../mcp_server.h"
#include "../mcp_tools.h"
#include "../../util/json.h"
#include "../../util/string.h"
#include "../../util/path.h"
#include "../../util/file.h"

/* Maximum number of lore entries to cache */
#define LORE_CACHE_SIZE 50

/* Structure to represent a lore cache entry */
typedef struct lore_cache_entry_t {
    char *key;              /* Cache key (e.g., "character:Gandalf:third_age") */
    lore_data_t *data;      /* The cached lore data */
    unsigned int hits;      /* Number of times this entry has been accessed */
    unsigned int timestamp; /* Timestamp for LRU replacement */
} lore_cache_entry_t;

/* Cache implementation */
typedef struct lore_cache_t {
    lore_cache_entry_t *entries[LORE_CACHE_SIZE];
    unsigned int count;
    unsigned int timestamp; /* Current timestamp, incremented on each access */
} lore_cache_t;

/**
 * Create a new lore cache
 * 
 * @return Initialized lore cache or NULL on failure
 */
static lore_cache_t *
create_lore_cache(void)
{
    lore_cache_t *cache = malloc(sizeof(lore_cache_t));
    
    if (cache == NULL) {
        return NULL;
    }
    
    memset(cache, 0, sizeof(lore_cache_t));
    return cache;
}

/**
 * Free a lore cache entry
 * 
 * @param entry The cache entry to free
 */
static void
free_cache_entry(lore_cache_entry_t *entry)
{
    if (entry == NULL) {
        return;
    }
    
    free(entry->key);
    free_lore_data(entry->data);
    free(entry);
}

/**
 * Free all resources used by a lore cache
 * 
 * @param cache The cache to free
 */
static void
free_lore_cache(lore_cache_t *cache)
{
    if (cache == NULL) {
        return;
    }
    
    for (unsigned int i = 0; i < cache->count; i++) {
        free_cache_entry(cache->entries[i]);
    }
    
    free(cache);
}

/**
 * Create a cache key from components
 * 
 * @param type The type of lore (character, location, etc.)
 * @param name The name of the entity
 * @param age The age (can be NULL)
 * @return Allocated cache key string or NULL on failure
 */
static char *
create_cache_key(const char *type, const char *name, const char *age)
{
    size_t key_len = strlen(type) + strlen(name) + 2; /* +2 for ':' and '\0' */
    
    if (age != NULL) {
        key_len += strlen(age) + 1; /* +1 for ':' */
    }
    
    char *key = malloc(key_len);
    if (key == NULL) {
        return NULL;
    }
    
    if (age != NULL) {
        snprintf(key, key_len, "%s:%s:%s", type, name, age);
    } else {
        snprintf(key, key_len, "%s:%s", type, name);
    }
    
    return key;
}

/**
 * Look up an item in the lore cache
 * 
 * @param cache The lore cache
 * @param key The cache key
 * @return The cache entry or NULL if not found
 */
static lore_cache_entry_t *
cache_lookup(lore_cache_t *cache, const char *key)
{
    for (unsigned int i = 0; i < cache->count; i++) {
        if (strcmp(cache->entries[i]->key, key) == 0) {
            /* Update access stats */
            cache->entries[i]->hits++;
            cache->entries[i]->timestamp = cache->timestamp++;
            return cache->entries[i];
        }
    }
    
    return NULL;
}

/**
 * Find the least recently used cache entry
 * 
 * @param cache The lore cache
 * @return Index of the LRU entry
 */
static unsigned int
find_lru_entry(lore_cache_t *cache)
{
    unsigned int lru_idx = 0;
    unsigned int min_timestamp = cache->entries[0]->timestamp;
    
    for (unsigned int i = 1; i < cache->count; i++) {
        if (cache->entries[i]->timestamp < min_timestamp) {
            min_timestamp = cache->entries[i]->timestamp;
            lru_idx = i;
        }
    }
    
    return lru_idx;
}

/**
 * Add an item to the lore cache
 * 
 * @param cache The lore cache
 * @param key The cache key
 * @param data The lore data to cache
 * @return true if added successfully, false otherwise
 */
static bool
cache_add(lore_cache_t *cache, const char *key, lore_data_t *data)
{
    lore_cache_entry_t *entry = malloc(sizeof(lore_cache_entry_t));
    if (entry == NULL) {
        return false;
    }
    
    entry->key = strdup(key);
    if (entry->key == NULL) {
        free(entry);
        return false;
    }
    
    entry->data = data;
    entry->hits = 1;
    entry->timestamp = cache->timestamp++;
    
    /* If cache is full, replace the least recently used entry */
    if (cache->count == LORE_CACHE_SIZE) {
        unsigned int lru_idx = find_lru_entry(cache);
        free_cache_entry(cache->entries[lru_idx]);
        cache->entries[lru_idx] = entry;
    } else {
        cache->entries[cache->count++] = entry;
    }
    
    return true;
}

/**
 * Initialize the lore manager
 *
 * @param memory_bank_path Path to the memory bank directory
 * @return Initialized lore manager or NULL on failure
 */
lore_manager_t *
init_lore_manager(const char *memory_bank_path)
{
    lore_manager_t *manager = malloc(sizeof(lore_manager_t));
    if (manager == NULL) {
        return NULL;
    }
    
    manager->memory_bank_path = strdup(memory_bank_path);
    if (manager->memory_bank_path == NULL) {
        free(manager);
        return NULL;
    }
    
    manager->lore_cache = create_lore_cache();
    if (manager->lore_cache == NULL) {
        free(manager->memory_bank_path);
        free(manager);
        return NULL;
    }
    
    manager->cache_size = LORE_CACHE_SIZE;
    manager->cache_hits = 0;
    manager->cache_misses = 0;
    
    return manager;
}

/**
 * Free resources used by the lore manager
 *
 * @param manager The lore manager to free
 */
void
free_lore_manager(lore_manager_t *manager)
{
    if (manager == NULL) {
        return;
    }
    
    free(manager->memory_bank_path);
    free_lore_cache((lore_cache_t *)manager->lore_cache);
    free(manager);
}

/**
 * Create a new lore data structure
 * 
 * @param content The lore content
 * @param source The source of the lore
 * @param age The age the lore is from
 * @param year The year within the age
 * @param is_canonical Whether the lore is canonical
 * @return New lore data structure or NULL on failure
 */
static lore_data_t *
create_lore_data(const char *content, const char *source, const char *age, int year, bool is_canonical)
{
    lore_data_t *lore = malloc(sizeof(lore_data_t));
    if (lore == NULL) {
        return NULL;
    }
    
    lore->content = strdup(content);
    if (lore->content == NULL) {
        free(lore);
        return NULL;
    }
    
    lore->source = strdup(source);
    if (lore->source == NULL) {
        free(lore->content);
        free(lore);
        return NULL;
    }
    
    lore->age = strdup(age);
    if (lore->age == NULL) {
        free(lore->source);
        free(lore->content);
        free(lore);
        return NULL;
    }
    
    lore->year = year;
    lore->is_canonical = is_canonical;
    
    return lore;
}

/**
 * Free a lore data structure
 *
 * @param lore The lore data to free
 */
void
free_lore_data(lore_data_t *lore)
{
    if (lore == NULL) {
        return;
    }
    
    free(lore->content);
    free(lore->source);
    free(lore->age);
    free(lore);
}

/**
 * Read lore from a JSON file
 * 
 * @param filepath The path to the JSON file
 * @param entity_name The name of the entity to find
 * @param is_character Whether the entity is a character
 * @return Lore data or NULL if not found
 */
static lore_data_t *
read_lore_from_json(const char *filepath, const char *entity_name, bool is_character)
{
    /* Logic to read and parse JSON file to extract lore */
    /* For now, this is a simplified implementation */
    /* In a real implementation, this would use the json.h utility functions */
    
    FILE *file = fopen(filepath, "r");
    if (file == NULL) {
        return NULL;
    }
    
    /* Read the file into memory */
    fseek(file, 0, SEEK_END);
    long file_size = ftell(file);
    fseek(file, 0, SEEK_SET);
    
    char *buffer = malloc(file_size + 1);
    if (buffer == NULL) {
        fclose(file);
        return NULL;
    }
    
    size_t read_size = fread(buffer, 1, file_size, file);
    buffer[read_size] = '\0';
    fclose(file);
    
    /* Parse JSON and extract lore (simplified) */
    /* In a real implementation, use proper JSON parsing */
    char *content = NULL;
    char *source = NULL;
    char *age = NULL;
    int year = 0;
    bool is_canonical = true;
    
    /* Get the age from the filepath */
    if (strstr(filepath, "first_age") != NULL) {
        age = "first_age";
    } else if (strstr(filepath, "third_age") != NULL) {
        age = "third_age";
    } else {
        age = "unknown_age";
    }
    
    /* Determine content, source, and year based on the JSON content */
    /* This is a simplified placeholder - real implementation would parse JSON properly */
    if (is_character) {
        content = "Character lore placeholder";
        source = "The Silmarillion";
        year = 1;
    } else {
        content = "Location lore placeholder";
        source = "The Lord of the Rings";
        year = 3018;
    }
    
    /* Create lore data */
    lore_data_t *lore = create_lore_data(content, source, age, year, is_canonical);
    
    /* Clean up */
    free(buffer);
    
    return lore;
}

/**
 * Get lore about a character from a specific age
 *
 * @param manager The lore manager
 * @param character_name The name of the character
 * @param age The age to get lore from (NULL for all ages)
 * @return Lore data for the character or NULL if not found
 */
lore_data_t *
get_character_lore(lore_manager_t *manager, const char *character_name, const char *age)
{
    if (manager == NULL || character_name == NULL) {
        return NULL;
    }
    
    /* Check cache first */
    lore_cache_t *cache = (lore_cache_t *)manager->lore_cache;
    char *cache_key = create_cache_key("character", character_name, age);
    
    if (cache_key == NULL) {
        return NULL;
    }
    
    lore_cache_entry_t *entry = cache_lookup(cache, cache_key);
    
    if (entry != NULL) {
        manager->cache_hits++;
        lore_data_t *result = entry->data;
        free(cache_key);
        return result;
    }
    
    manager->cache_misses++;
    
    /* Not in cache, load from file */
    char filepath[PATH_MAX];
    if (age != NULL) {
        /* Look in specific age directory */
        snprintf(filepath, sizeof(filepath), "%s/lore/%s/characters/%s.json", 
                 manager->memory_bank_path, age, character_name);
    } else {
        /* Try first age, then third age if not found */
        snprintf(filepath, sizeof(filepath), "%s/lore/first_age/characters/%s.json", 
                 manager->memory_bank_path, character_name);
        
        if (access(filepath, F_OK) != 0) {
            snprintf(filepath, sizeof(filepath), "%s/lore/third_age/characters/%s.json", 
                     manager->memory_bank_path, character_name);
        }
    }
    
    lore_data_t *lore = read_lore_from_json(filepath, character_name, true);
    
    /* Add to cache if found */
    if (lore != NULL) {
        cache_add(cache, cache_key, lore);
    }
    
    free(cache_key);
    return lore;
}

/**
 * Get lore about a location from a specific age
 *
 * @param manager The lore manager
 * @param location_name The name of the location
 * @param age The age to get lore from (NULL for all ages)
 * @return Lore data for the location or NULL if not found
 */
lore_data_t *
get_location_lore(lore_manager_t *manager, const char *location_name, const char *age)
{
    if (manager == NULL || location_name == NULL) {
        return NULL;
    }
    
    /* Similar implementation to get_character_lore, but for locations */
    /* Check cache first */
    lore_cache_t *cache = (lore_cache_t *)manager->lore_cache;
    char *cache_key = create_cache_key("location", location_name, age);
    
    if (cache_key == NULL) {
        return NULL;
    }
    
    lore_cache_entry_t *entry = cache_lookup(cache, cache_key);
    
    if (entry != NULL) {
        manager->cache_hits++;
        lore_data_t *result = entry->data;
        free(cache_key);
        return result;
    }
    
    manager->cache_misses++;
    
    /* Not in cache, load from file */
    char filepath[PATH_MAX];
    if (age != NULL) {
        /* Look in specific age directory */
        snprintf(filepath, sizeof(filepath), "%s/lore/%s/locations/%s.json", 
                 manager->memory_bank_path, age, location_name);
    } else {
        /* Try first age, then third age if not found */
        snprintf(filepath, sizeof(filepath), "%s/lore/first_age/locations/%s.json", 
                 manager->memory_bank_path, location_name);
        
        if (access(filepath, F_OK) != 0) {
            snprintf(filepath, sizeof(filepath), "%s/lore/third_age/locations/%s.json", 
                     manager->memory_bank_path, location_name);
        }
    }
    
    lore_data_t *lore = read_lore_from_json(filepath, location_name, false);
    
    /* Add to cache if found */
    if (lore != NULL) {
        cache_add(cache, cache_key, lore);
    }
    
    free(cache_key);
    return lore;
}

/**
 * Get lore about an artifact or item from a specific age
 *
 * @param manager The lore manager
 * @param artifact_name The name of the artifact
 * @param age The age to get lore from (NULL for all ages)
 * @return Lore data for the artifact or NULL if not found
 */
lore_data_t *
get_artifact_lore(lore_manager_t *manager, const char *artifact_name, const char *age)
{
    /* Implementation similar to get_character_lore and get_location_lore */
    /* For brevity, not showing the full implementation */
    /* Would follow the same pattern as the above functions */
    return NULL;
}

/**
 * Get a random lore snippet related to the current age
 *
 * @param manager The lore manager
 * @param age The age to get lore from
 * @param topic Optional topic filter (character, location, event, etc.)
 * @return Random lore data or NULL if none available
 */
lore_data_t *
get_random_lore(lore_manager_t *manager, const char *age, const char *topic)
{
    /* Implementation would select a random lore entry from the specified age */
    /* For brevity, not showing the full implementation */
    return NULL;
}

/**
 * Get lore for a companion based on their background
 *
 * @param manager The lore manager
 * @param companion_name The name of the companion
 * @param age The current age
 * @return Lore data relevant to the companion or NULL if none available
 */
lore_data_t *
get_companion_lore(lore_manager_t *manager, const char *companion_name, const char *age)
{
    /* Implementation would retrieve companion-specific lore */
    /* This would combine character lore with relationship data */
    return NULL;
}

/* MCP Tool handler functions */

/**
 * MCP tool handler for character lore requests
 */
static char *
handle_character_lore_request(void *user_data, json_object_t *params)
{
    lore_manager_t *manager = (lore_manager_t *)user_data;
    
    /* Extract parameters */
    const char *character_name = json_object_get_string(params, "character_name");
    const char *age = json_object_get_string(params, "age");
    
    if (character_name == NULL) {
        return strdup("{\"error\": \"Missing character_name parameter\"}");
    }
    
    /* Get the lore */
    lore_data_t *lore = get_character_lore(manager, character_name, age);
    
    if (lore == NULL) {
        return strdup("{\"error\": \"Character lore not found\"}");
    }
    
    /* Format the response */
    char *response = NULL;
    size_t response_size = strlen(lore->content) + strlen(lore->source) + 
                          strlen(lore->age) + 200;
    
    response = malloc(response_size);
    if (response == NULL) {
        free_lore_data(lore);
        return strdup("{\"error\": \"Memory allocation failed\"}");
    }
    
    snprintf(response, response_size, 
             "{\"content\": \"%s\", \"source\": \"%s\", \"age\": \"%s\", "
             "\"year\": %d, \"is_canonical\": %s}",
             lore->content, lore->source, lore->age, 
             lore->year, lore->is_canonical ? "true" : "false");
    
    free_lore_data(lore);
    return response;
}

/**
 * MCP tool handler for location lore requests
 */
static char *
handle_location_lore_request(void *user_data, json_object_t *params)
{
    /* Similar implementation to handle_character_lore_request */
    /* Would extract parameters, get location lore, and format the response */
    return NULL;
}

/**
 * MCP tool handler for artifact lore requests
 */
static char *
handle_artifact_lore_request(void *user_data, json_object_t *params)
{
    /* Similar implementation to handle_character_lore_request */
    /* Would extract parameters, get artifact lore, and format the response */
    return NULL;
}

/**
 * MCP tool handler for random lore requests
 */
static char *
handle_random_lore_request(void *user_data, json_object_t *params)
{
    /* Similar implementation to other handlers */
    /* Would extract parameters, get random lore, and format the response */
    return NULL;
}

/**
 * MCP tool handler for companion lore requests
 */
static char *
handle_companion_lore_request(void *user_data, json_object_t *params)
{
    /* Similar implementation to other handlers */
    /* Would extract parameters, get companion lore, and format the response */
    return NULL;
}

/**
 * Register lore-related tools with the MCP server
 *
 * @param server The MCP server
 * @param manager The lore manager
 * @return true if registration was successful, false otherwise
 */
bool
register_lore_tools(mcp_server_t *server, lore_manager_t *manager)
{
    /* Register character lore tool */
    if (!register_mcp_tool(server, "ages/lore/character", handle_character_lore_request, manager)) {
        return false;
    }
    
    /* Register location lore tool */
    if (!register_mcp_tool(server, "ages/lore/location", handle_location_lore_request, manager)) {
        return false;
    }
    
    /* Register artifact lore tool */
    if (!register_mcp_tool(server, "ages/lore/artifact", handle_artifact_lore_request, manager)) {
        return false;
    }
    
    /* Register random lore tool */
    if (!register_mcp_tool(server, "ages/lore/random", handle_random_lore_request, manager)) {
        return false;
    }
    
    /* Register companion lore tool */
    if (!register_mcp_tool(server, "ages/lore/companion", handle_companion_lore_request, manager)) {
        return false;
    }
    
    return true;
} 