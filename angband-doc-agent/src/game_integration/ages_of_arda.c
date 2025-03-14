/**
 * ages_of_arda.c
 * 
 * Integration module for the Ages of Arda companion system with the Angband game.
 * 
 * This module provides functions for the Angband game to interact with the
 * Ages of Arda companion system through the MCP server.
 */

#include "angband.h"
#include "mcp_client.h"
#include "ui-companion.h"
#include "game-event.h"

/**
 * Constants
 */
#define AGES_DIALOGUE_ENDPOINT "ages/companion/dialogue"
#define AGES_COMPANION_INFO_ENDPOINT "ages/companion/info"
#define AGES_TIMELINE_INFO_ENDPOINT "ages/timeline/info"
#define AGES_RELATIONSHIP_UPDATE_ENDPOINT "ages/relationship/update"
#define AGES_PLAYER_DEATH_ENDPOINT "ages/player/death"

/**
 * Global variables
 */
static char current_companion_name[100] = "Unknown";
static char current_age[20] = "First Age";
static int current_year = 1;
static int relationship_level = 0;

/**
 * Forward declarations
 */
static void ages_handle_game_event(game_event_type type, game_event_data *data, void *user);

/**
 * Initialize the Ages of Arda integration.
 * 
 * This function initializes the Ages of Arda integration by registering
 * event handlers and retrieving the current timeline information.
 * 
 * @return true if initialization was successful, false otherwise
 */
bool ages_of_arda_init(void)
{
    mcp_response_t *response;
    
    /* Register event handlers */
    event_add_handler(EVENT_ENTER_LEVEL, ages_handle_game_event, NULL);
    event_add_handler(EVENT_LEAVE_LEVEL, ages_handle_game_event, NULL);
    event_add_handler(EVENT_PLAYER_DEATH, ages_handle_game_event, NULL);
    event_add_handler(EVENT_INVENTORY_CHANGE, ages_handle_game_event, NULL);
    event_add_handler(EVENT_MONSTER_DEATH, ages_handle_game_event, NULL);
    
    /* Get current timeline information */
    response = mcp_client_call(AGES_TIMELINE_INFO_ENDPOINT, "{}");
    if (!response) {
        msg_print("Failed to connect to MCP server for Ages of Arda.");
        return false;
    }
    
    /* Parse the response */
    if (mcp_response_get_string(response, "age", current_age, sizeof(current_age)) &&
        mcp_response_get_int(response, "year", &current_year) &&
        mcp_response_get_string(response, "companion", current_companion_name, sizeof(current_companion_name))) {
        
        /* Success */
        mcp_response_free(response);
        
        /* Get companion info */
        char request[256];
        sprintf(request, "{\"companion_name\": \"%s\"}", current_companion_name);
        
        response = mcp_client_call(AGES_COMPANION_INFO_ENDPOINT, request);
        if (response) {
            mcp_response_get_int(response, "relationship_level", &relationship_level);
            mcp_response_free(response);
        }
        
        /* Display welcome message */
        char buf[1024];
        sprintf(buf, "Welcome to the %s, Year %d. Your companion is %s.",
                current_age, current_year, current_companion_name);
        msg_print(buf);
        
        /* Generate greeting dialogue */
        ages_generate_dialogue("greeting");
        
        return true;
    }
    
    /* Failure */
    mcp_response_free(response);
    msg_print("Failed to initialize Ages of Arda integration.");
    return false;
}

/**
 * Clean up the Ages of Arda integration.
 * 
 * This function cleans up the Ages of Arda integration by unregistering
 * event handlers.
 */
void ages_of_arda_cleanup(void)
{
    /* Unregister event handlers */
    event_remove_handler(EVENT_ENTER_LEVEL, ages_handle_game_event, NULL);
    event_remove_handler(EVENT_LEAVE_LEVEL, ages_handle_game_event, NULL);
    event_remove_handler(EVENT_PLAYER_DEATH, ages_handle_game_event, NULL);
    event_remove_handler(EVENT_INVENTORY_CHANGE, ages_handle_game_event, NULL);
    event_remove_handler(EVENT_MONSTER_DEATH, ages_handle_game_event, NULL);
}

/**
 * Generate dialogue for the current companion.
 * 
 * This function generates dialogue for the current companion based on the
 * specified prompt type and the current game context.
 * 
 * @param prompt_type The type of dialogue to generate (e.g., "greeting", "combat", "discovery")
 * @return true if dialogue was generated successfully, false otherwise
 */
bool ages_generate_dialogue(const char *prompt_type)
{
    mcp_response_t *response;
    char request[1024];
    char dialogue[1024] = "";
    char context[512];
    
    /* Build the context */
    sprintf(context, "{"
                     "\"location\": \"%s\", "
                     "\"depth\": %d, "
                     "\"player_health\": %d, "
                     "\"player_health_max\": %d, "
                     "\"enemies_nearby\": %s"
                     "}",
            p_ptr->depth ? "dungeon" : "town",
            p_ptr->depth,
            p_ptr->chp,
            p_ptr->mhp,
            cave_monster_count(cave) > 0 ? "true" : "false");
    
    /* Build the request */
    sprintf(request, "{"
                     "\"context\": %s, "
                     "\"prompt_type\": \"%s\""
                     "}",
            context, prompt_type);
    
    /* Call the MCP server */
    response = mcp_client_call(AGES_DIALOGUE_ENDPOINT, request);
    if (!response) {
        return false;
    }
    
    /* Parse the response */
    if (mcp_response_get_string(response, "dialogue", dialogue, sizeof(dialogue))) {
        /* Update relationship level */
        mcp_response_get_int(response, "relationship_level", &relationship_level);
        
        /* Display the dialogue */
        ui_companion_display_dialogue(current_companion_name, dialogue);
        
        mcp_response_free(response);
        return true;
    }
    
    /* Failure */
    mcp_response_free(response);
    return false;
}

/**
 * Update the relationship level with the current companion.
 * 
 * This function updates the relationship level with the current companion
 * based on the specified change.
 * 
 * @param change The amount to change the relationship level by
 * @return true if the update was successful, false otherwise
 */
bool ages_update_relationship(int change)
{
    mcp_response_t *response;
    char request[256];
    
    /* Build the request */
    sprintf(request, "{"
                     "\"change\": %d"
                     "}",
            change);
    
    /* Call the MCP server */
    response = mcp_client_call(AGES_RELATIONSHIP_UPDATE_ENDPOINT, request);
    if (!response) {
        return false;
    }
    
    /* Parse the response */
    if (mcp_response_get_int(response, "relationship_level", &relationship_level)) {
        mcp_response_free(response);
        return true;
    }
    
    /* Failure */
    mcp_response_free(response);
    return false;
}

/**
 * Handle player death.
 * 
 * This function handles player death by advancing the timeline and
 * updating the current companion.
 * 
 * @return true if the timeline was advanced successfully, false otherwise
 */
bool ages_handle_player_death(void)
{
    mcp_response_t *response;
    
    /* Call the MCP server */
    response = mcp_client_call(AGES_PLAYER_DEATH_ENDPOINT, "{}");
    if (!response) {
        return false;
    }
    
    /* Parse the response */
    if (mcp_response_get_string(response, "age", current_age, sizeof(current_age)) &&
        mcp_response_get_int(response, "year", &current_year) &&
        mcp_response_get_string(response, "companion", current_companion_name, sizeof(current_companion_name))) {
        
        /* Reset relationship level */
        relationship_level = 0;
        
        /* Display message */
        char buf[1024];
        sprintf(buf, "As your spirit departs, you find yourself reborn in the %s, Year %d. "
                     "Your new companion is %s.",
                current_age, current_year, current_companion_name);
        msg_print(buf);
        
        mcp_response_free(response);
        return true;
    }
    
    /* Failure */
    mcp_response_free(response);
    return false;
}

/**
 * Get the current companion name.
 * 
 * @return The current companion name
 */
const char *ages_get_current_companion(void)
{
    return current_companion_name;
}

/**
 * Get the current age and year.
 * 
 * @param age Pointer to store the current age
 * @param year Pointer to store the current year
 */
void ages_get_current_age_and_year(const char **age, int *year)
{
    if (age) *age = current_age;
    if (year) *year = current_year;
}

/**
 * Get the current relationship level.
 * 
 * @return The current relationship level
 */
int ages_get_relationship_level(void)
{
    return relationship_level;
}

/**
 * Handle game events.
 * 
 * This function handles game events by generating appropriate dialogue
 * and updating the relationship level.
 * 
 * @param type The type of event
 * @param data The event data
 * @param user User data (unused)
 */
static void ages_handle_game_event(game_event_type type, game_event_data *data, void *user)
{
    /* Handle different event types */
    switch (type) {
        case EVENT_ENTER_LEVEL:
            /* Generate dialogue when entering a new level */
            if (p_ptr->depth > 0) {
                ages_generate_dialogue("exploration");
            } else {
                ages_generate_dialogue("town");
            }
            break;
            
        case EVENT_LEAVE_LEVEL:
            /* Nothing to do when leaving a level */
            break;
            
        case EVENT_PLAYER_DEATH:
            /* Generate final dialogue before death */
            ages_generate_dialogue("death");
            
            /* Handle player death */
            ages_handle_player_death();
            break;
            
        case EVENT_INVENTORY_CHANGE:
            /* Check if an artifact was found */
            if (data && data->inventory.item && artifact_p(data->inventory.item)) {
                /* Generate dialogue for artifact discovery */
                ages_generate_dialogue("artifact");
                
                /* Increase relationship level */
                ages_update_relationship(5);
            }
            break;
            
        case EVENT_MONSTER_DEATH:
            /* Check if a unique monster was killed */
            if (data && data->monster.m_idx > 0) {
                monster_type *m_ptr = cave_monster(cave, data->monster.m_idx);
                monster_race *r_ptr = &r_info[m_ptr->r_idx];
                
                if (rf_has(r_ptr->flags, RF_UNIQUE)) {
                    /* Generate dialogue for unique monster kill */
                    ages_generate_dialogue("victory");
                    
                    /* Increase relationship level */
                    ages_update_relationship(10);
                }
            }
            break;
            
        default:
            /* Ignore other events */
            break;
    }
} 