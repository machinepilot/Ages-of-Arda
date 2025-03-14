/**
 * @file bard.h
 * @brief Interface for the Lute the Bard narrative system in Tower of Babel
 */

#ifndef INCLUDED_BARD_H
#define INCLUDED_BARD_H

#include <stdbool.h>
#include "mcp-client.h"

/**
 * @brief Initialize the Bard system
 * 
 * This must be called before any other Bard functions.
 * 
 * @param server_url URL of the MCP server
 * @param api_key Optional API key for authentication (can be NULL)
 * @param character_id ID of the current player character
 * @return true if initialization was successful, false otherwise
 */
bool bard_init(const char *server_url, const char *api_key, const char *character_id);

/**
 * @brief Shutdown the Bard system
 * 
 * Call this when the game exits to free resources.
 */
void bard_shutdown(void);

/**
 * @brief Process pending narrative requests
 * 
 * This should be called regularly (e.g., once per game loop iteration)
 * to check for completed narrative generation requests.
 * 
 * @return Number of narratives processed
 */
int bard_process_pending(void);

/**
 * @brief Check if the Bard system is initialized
 * 
 * @return true if initialized, false otherwise
 */
bool bard_is_initialized(void);

/**
 * @brief Pause or resume narrative generation
 * 
 * @param paused true to pause, false to resume
 */
void bard_set_paused(bool paused);

/**
 * @brief Check if narrative generation is paused
 * 
 * @return true if paused, false if active
 */
bool bard_is_paused(void);

/**
 * @brief Configure the Bard system
 * 
 * @param frequency Frequency of narratives (0-100)
 * @param verbosity Level of detail (0-100)
 * @param default_style Default narrative style
 * @return true if configuration was successful, false otherwise
 */
bool bard_configure(int frequency, int verbosity, const char *default_style);

/**
 * @brief Request a narrative for a monster death event
 * 
 * @param monster_name Name of the defeated monster
 * @param monster_level Level of the monster
 * @param is_unique Whether the monster is unique
 * @param style Narrative style (NULL for default)
 * @param tone Suggested emotional tone (NULL for default)
 * @return true if request was successful, false otherwise
 */
bool bard_narrate_monster_death(const char *monster_name, int monster_level, 
                               bool is_unique, const char *style, const char *tone);

/**
 * @brief Request a narrative for an item discovery event
 * 
 * @param item_name Name of the discovered item
 * @param is_artifact Whether the item is an artifact
 * @param item_type Type of item (weapon, armor, etc.)
 * @param style Narrative style (NULL for default)
 * @param tone Suggested emotional tone (NULL for default)
 * @return true if request was successful, false otherwise
 */
bool bard_narrate_item_discovery(const char *item_name, bool is_artifact,
                                const char *item_type, const char *style, 
                                const char *tone);

/**
 * @brief Request a narrative for entering a new dungeon level
 * 
 * @param dungeon_level New dungeon level number
 * @param level_feeling Feeling about the level
 * @param style Narrative style (NULL for default)
 * @param tone Suggested emotional tone (NULL for default)
 * @return true if request was successful, false otherwise
 */
bool bard_narrate_new_level(int dungeon_level, const char *level_feeling,
                           const char *style, const char *tone);

/**
 * @brief Request a narrative for a near-death experience
 * 
 * @param hp_percent Percentage of hit points remaining
 * @param enemy_name Name of the enemy that nearly killed the player (can be NULL)
 * @param style Narrative style (NULL for default)
 * @param tone Suggested emotional tone (NULL for default)
 * @return true if request was successful, false otherwise
 */
bool bard_narrate_near_death(int hp_percent, const char *enemy_name,
                            const char *style, const char *tone);

/**
 * @brief Request a narrative for a quest completion
 * 
 * @param quest_name Name of the completed quest
 * @param quest_level Level of the quest
 * @param style Narrative style (NULL for default)
 * @param tone Suggested emotional tone (NULL for default)
 * @return true if request was successful, false otherwise
 */
bool bard_narrate_quest_complete(const char *quest_name, int quest_level,
                                const char *style, const char *tone);

/**
 * @brief Request a narrative for player level-up
 * 
 * @param new_level New player level
 * @param class_name Player class name
 * @param style Narrative style (NULL for default)
 * @param tone Suggested emotional tone (NULL for default)
 * @return true if request was successful, false otherwise
 */
bool bard_narrate_level_up(int new_level, const char *class_name,
                          const char *style, const char *tone);

/**
 * @brief Request a narrative for a custom event
 * 
 * @param event_type Type of event
 * @param event_data JSON string with event details
 * @param style Narrative style (NULL for default)
 * @param tone Suggested emotional tone (NULL for default)
 * @return true if request was successful, false otherwise
 */
bool bard_narrate_custom(const char *event_type, const char *event_data,
                        const char *style, const char *tone);

/**
 * @brief Get the number of narratives in the display queue
 * 
 * @return Number of queued narratives
 */
int bard_get_queue_length(void);

/**
 * @brief Get the next narrative to display
 * 
 * @param text Buffer to store the narrative text
 * @param max_text_len Maximum length of the text buffer
 * @param is_spoken Output parameter indicating if the text is spoken dialogue
 * @param importance Output parameter indicating the importance of the narrative
 * @return true if a narrative was retrieved, false if queue is empty
 */
bool bard_get_next_narrative(char *text, size_t max_text_len, bool *is_spoken, int *importance);

/**
 * @brief Update player information for the Bard
 * 
 * @param name Player name
 * @param race Player race
 * @param class_name Player class
 * @param level Player level
 * @return true if update was successful, false otherwise
 */
bool bard_update_player_info(const char *name, const char *race, const char *class_name, int level);

/**
 * @brief Enable or disable debug mode
 * 
 * @param debug true to enable debug mode, false to disable
 */
void bard_set_debug(bool debug);

#endif /* INCLUDED_BARD_H */ 