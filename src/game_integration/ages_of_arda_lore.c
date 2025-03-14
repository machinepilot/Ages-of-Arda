/**
 * ages_of_arda_lore.c
 * 
 * Integration module for the Ages of Arda lore system with the Angband game.
 * 
 * This module provides functions for the Angband game to interact with the
 * Ages of Arda lore system through the MCP server.
 */

#include "angband.h"
#include "mcp_client.h"
#include "ui-companion.h"
#include "ages_of_arda.h"
#include "ages_of_arda_lore.h"

/**
 * Constants
 */
#define AGES_LORE_CHARACTER_ENDPOINT "ages/lore/character"
#define AGES_LORE_LOCATION_ENDPOINT "ages/lore/location"
#define AGES_LORE_ARTIFACT_ENDPOINT "ages/lore/artifact"

/**
 * Generate lore dialogue for a character.
 * 
 * This function generates lore dialogue for a character based on the
 * current companion's knowledge.
 * 
 * @param character_name The name of the character to get lore for
 * @return true if dialogue was generated successfully, false otherwise
 */
bool ages_generate_character_lore(const char *character_name)
{
    mcp_response_t *response;
    char request[256];
    char dialogue[1024] = "";
    
    /* Build the request */
    sprintf(request, "{"
                     "\"character_name\": \"%s\""
                     "}",
            character_name);
    
    /* Call the MCP server */
    response = mcp_client_call(AGES_LORE_CHARACTER_ENDPOINT, request);
    if (!response) {
        return false;
    }
    
    /* Parse the response */
    if (mcp_response_get_string(response, "dialogue", dialogue, sizeof(dialogue))) {
        /* Display the dialogue */
        ui_companion_display_dialogue(ages_get_current_companion(), dialogue);
        
        mcp_response_free(response);
        return true;
    }
    
    /* Failure */
    mcp_response_free(response);
    return false;
}

/**
 * Generate lore dialogue for a location.
 * 
 * This function generates lore dialogue for a location based on the
 * current companion's knowledge.
 * 
 * @param location_name The name of the location to get lore for
 * @return true if dialogue was generated successfully, false otherwise
 */
bool ages_generate_location_lore(const char *location_name)
{
    mcp_response_t *response;
    char request[256];
    char dialogue[1024] = "";
    
    /* Build the request */
    sprintf(request, "{"
                     "\"location_name\": \"%s\""
                     "}",
            location_name);
    
    /* Call the MCP server */
    response = mcp_client_call(AGES_LORE_LOCATION_ENDPOINT, request);
    if (!response) {
        return false;
    }
    
    /* Parse the response */
    if (mcp_response_get_string(response, "dialogue", dialogue, sizeof(dialogue))) {
        /* Display the dialogue */
        ui_companion_display_dialogue(ages_get_current_companion(), dialogue);
        
        mcp_response_free(response);
        return true;
    }
    
    /* Failure */
    mcp_response_free(response);
    return false;
}

/**
 * Generate lore dialogue for an artifact.
 * 
 * This function generates lore dialogue for an artifact based on the
 * current companion's knowledge.
 * 
 * @param artifact_name The name of the artifact to get lore for
 * @return true if dialogue was generated successfully, false otherwise
 */
bool ages_generate_artifact_lore(const char *artifact_name)
{
    mcp_response_t *response;
    char request[256];
    char dialogue[1024] = "";
    
    /* Build the request */
    sprintf(request, "{"
                     "\"artifact_name\": \"%s\""
                     "}",
            artifact_name);
    
    /* Call the MCP server */
    response = mcp_client_call(AGES_LORE_ARTIFACT_ENDPOINT, request);
    if (!response) {
        return false;
    }
    
    /* Parse the response */
    if (mcp_response_get_string(response, "dialogue", dialogue, sizeof(dialogue))) {
        /* Display the dialogue */
        ui_companion_display_dialogue(ages_get_current_companion(), dialogue);
        
        mcp_response_free(response);
        return true;
    }
    
    /* Failure */
    mcp_response_free(response);
    return false;
}

/**
 * Check if lore is available for a character.
 * 
 * This function checks if lore is available for a character.
 * 
 * @param character_name The name of the character to check
 * @return true if lore is available, false otherwise
 */
bool ages_has_character_lore(const char *character_name)
{
    mcp_response_t *response;
    char request[256];
    char dialogue[1024] = "";
    
    /* Build the request */
    sprintf(request, "{"
                     "\"character_name\": \"%s\""
                     "}",
            character_name);
    
    /* Call the MCP server */
    response = mcp_client_call(AGES_LORE_CHARACTER_ENDPOINT, request);
    if (!response) {
        return false;
    }
    
    /* Parse the response */
    bool has_lore = mcp_response_get_string(response, "dialogue", dialogue, sizeof(dialogue)) &&
                    !strstr(dialogue, "I know little of") &&
                    !strstr(dialogue, "tale yet untold");
    
    mcp_response_free(response);
    return has_lore;
}

/**
 * Check if lore is available for a location.
 * 
 * This function checks if lore is available for a location.
 * 
 * @param location_name The name of the location to check
 * @return true if lore is available, false otherwise
 */
bool ages_has_location_lore(const char *location_name)
{
    mcp_response_t *response;
    char request[256];
    char dialogue[1024] = "";
    
    /* Build the request */
    sprintf(request, "{"
                     "\"location_name\": \"%s\""
                     "}",
            location_name);
    
    /* Call the MCP server */
    response = mcp_client_call(AGES_LORE_LOCATION_ENDPOINT, request);
    if (!response) {
        return false;
    }
    
    /* Parse the response */
    bool has_lore = mcp_response_get_string(response, "dialogue", dialogue, sizeof(dialogue)) &&
                    !strstr(dialogue, "I know little of") &&
                    !strstr(dialogue, "tale yet untold");
    
    mcp_response_free(response);
    return has_lore;
}

/**
 * Check if lore is available for an artifact.
 * 
 * This function checks if lore is available for an artifact.
 * 
 * @param artifact_name The name of the artifact to check
 * @return true if lore is available, false otherwise
 */
bool ages_has_artifact_lore(const char *artifact_name)
{
    mcp_response_t *response;
    char request[256];
    char dialogue[1024] = "";
    
    /* Build the request */
    sprintf(request, "{"
                     "\"artifact_name\": \"%s\""
                     "}",
            artifact_name);
    
    /* Call the MCP server */
    response = mcp_client_call(AGES_LORE_ARTIFACT_ENDPOINT, request);
    if (!response) {
        return false;
    }
    
    /* Parse the response */
    bool has_lore = mcp_response_get_string(response, "dialogue", dialogue, sizeof(dialogue)) &&
                    !strstr(dialogue, "I know little of") &&
                    !strstr(dialogue, "tale yet untold");
    
    mcp_response_free(response);
    return has_lore;
} 