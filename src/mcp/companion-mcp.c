/**
 * \file companion-mcp.c
 * \brief MCP integration for companion dialogue
 *
 * This file provides functions for communicating with the MCP server for
 * companion dialogue and information.
 */

#include "angband.h"
#include "init.h"
#include "ui-companion.h"
#include "ui-term.h"
#include "game-event.h"

/* Constants for MCP endpoints */
#define COMPANION_DIALOGUE_ENDPOINT "ages/companion/dialogue"
#define COMPANION_INFO_ENDPOINT "ages/companion/info"
#define COMPANION_RELATIONSHIP_ENDPOINT "ages/relationship/update"

/**
 * Current game age - this would normally come from game state
 */
static char current_age[32] = "First Age";

/**
 * Simple JSON response structure
 */
typedef struct {
    char *text;
    size_t length;
} mcp_response_t;

/**
 * Create a new MCP response
 */
static mcp_response_t *mcp_response_new(const char *text, size_t length)
{
    mcp_response_t *response = mem_zalloc(sizeof(mcp_response_t));
    if (!response)
        return NULL;
    
    response->text = mem_zalloc(length + 1);
    if (!response->text) {
        mem_free(response);
        return NULL;
    }
    
    memcpy(response->text, text, length);
    response->text[length] = '\0';
    response->length = length;
    
    return response;
}

/**
 * Free an MCP response
 */
static void mcp_response_free(mcp_response_t *response)
{
    if (!response)
        return;
    
    if (response->text)
        mem_free(response->text);
    
    mem_free(response);
}

/**
 * Extract a string value from a JSON response
 */
static bool mcp_response_get_string(mcp_response_t *response, const char *key, 
                                  char *value, size_t max_length)
{
    char search_key[100];
    char *start, *end;
    size_t length;
    
    if (!response || !response->text || !key || !value)
        return false;
    
    /* Create the JSON key to search for */
    sprintf(search_key, "\"%s\":\"", key);
    
    /* Find the key in the response */
    start = strstr(response->text, search_key);
    if (!start)
        return false;
    
    /* Move past the key and opening quote */
    start += strlen(search_key);
    
    /* Find the end of the value (closing quote) */
    end = strchr(start, '\"');
    if (!end)
        return false;
    
    /* Calculate length of the value */
    length = end - start;
    if (length >= max_length)
        length = max_length - 1;
    
    /* Copy the value */
    memcpy(value, start, length);
    value[length] = '\0';
    
    return true;
}

/**
 * Extract an integer value from a JSON response
 */
static bool mcp_response_get_int(mcp_response_t *response, const char *key, int *value)
{
    char search_key[100];
    char *start;
    
    if (!response || !response->text || !key || !value)
        return false;
    
    /* Create the JSON key to search for */
    sprintf(search_key, "\"%s\":", key);
    
    /* Find the key in the response */
    start = strstr(response->text, search_key);
    if (!start)
        return false;
    
    /* Move past the key */
    start += strlen(search_key);
    
    /* Parse the value */
    *value = atoi(start);
    
    return true;
}

/**
 * Mock MCP client for offline development
 * In a real implementation, this would be replaced with actual HTTP calls
 */
static mcp_response_t *mcp_client_call(const char *endpoint, const char *request)
{
    static const char *dialogue_responses[] = {
        "{\"dialogue\":\"Be careful here. These caverns are known to house ancient evils.\",\"thoughts\":\"I hope we don't disturb anything too dangerous.\"}",
        "{\"dialogue\":\"Listen! Do you hear that? A faint melody on the wind...\",\"thoughts\":\"It reminds me of a song from my childhood.\"}",
        "{\"dialogue\":\"The air grows colder. We must be nearing something ancient.\",\"thoughts\":\"I can feel a presence watching us.\"}",
        "{\"dialogue\":\"Such remarkable stonework! The dwarves of old truly were masters.\",\"thoughts\":\"I should compose a ballad about these halls.\"}",
        "{\"dialogue\":\"Stay close. The shadows here seem to move with purpose.\",\"thoughts\":\"I wish I had studied more combat techniques.\"}",
    };
    
    static const char *info_responses[] = {
        "{\"hp_current\":75,\"hp_max\":100,\"status\":\"Healthy\",\"relationship_level\":3}",
        "{\"hp_current\":60,\"hp_max\":100,\"status\":\"Winded\",\"relationship_level\":3}",
        "{\"hp_current\":80,\"hp_max\":100,\"status\":\"Alert\",\"relationship_level\":4}",
        "{\"hp_current\":55,\"hp_max\":100,\"status\":\"Injured\",\"relationship_level\":3}",
        "{\"hp_current\":90,\"hp_max\":100,\"status\":\"Inspired\",\"relationship_level\":3}",
    };
    
    /* Simulate network latency */
    //SDL_Delay(50);
    
    /* Return appropriate mock response based on endpoint */
    if (strstr(endpoint, "dialogue")) {
        int idx = randint0(5);
        return mcp_response_new(dialogue_responses[idx], strlen(dialogue_responses[idx]));
    } else if (strstr(endpoint, "info")) {
        int idx = randint0(5);
        return mcp_response_new(info_responses[idx], strlen(info_responses[idx]));
    }
    
    /* Unknown endpoint */
    return NULL;
}

/**
 * Request dialogue from the MCP server
 */
bool companion_request_dialogue(struct companion_data *companion, const char *topic)
{
    char request[512];
    mcp_response_t *response;
    char dialogue[256] = "";
    char thoughts[256] = "";
    
    if (!companion || !topic)
        return false;
    
    /* Build the request */
    sprintf(request, "{"
                     "\"companion_name\": \"%s\","
                     "\"age\": \"%s\","
                     "\"topic\": \"%s\","
                     "\"relationship_level\": %d"
                     "}",
            companion->name, current_age, topic, companion->relationship_level);
    
    /* Call the MCP server */
    response = mcp_client_call(COMPANION_DIALOGUE_ENDPOINT, request);
    if (!response)
        return false;
    
    /* Parse the response */
    if (mcp_response_get_string(response, "dialogue", dialogue, sizeof(dialogue))) {
        companion_add_dialogue(companion, dialogue, false);
    }
    
    if (mcp_response_get_string(response, "thoughts", thoughts, sizeof(thoughts))) {
        companion_add_dialogue(companion, thoughts, true);
    }
    
    mcp_response_free(response);
    return true;
}

/**
 * Update companion stats from the MCP server
 */
bool companion_update_info(struct companion_data *companion)
{
    char request[256];
    mcp_response_t *response;
    
    if (!companion)
        return false;
    
    /* Build the request */
    sprintf(request, "{"
                     "\"companion_name\": \"%s\","
                     "\"age\": \"%s\""
                     "}",
            companion->name, current_age);
    
    /* Call the MCP server */
    response = mcp_client_call(COMPANION_INFO_ENDPOINT, request);
    if (!response)
        return false;
    
    /* Parse the response */
    mcp_response_get_int(response, "hp_current", &companion->hp_current);
    mcp_response_get_int(response, "hp_max", &companion->hp_max);
    mcp_response_get_string(response, "status", companion->status, sizeof(companion->status));
    mcp_response_get_int(response, "relationship_level", &companion->relationship_level);
    
    mcp_response_free(response);
    return true;
}

/**
 * Update relationship level with companion
 */
bool companion_update_relationship(struct companion_data *companion, int change, const char *reason)
{
    char request[512];
    mcp_response_t *response;
    
    if (!companion)
        return false;
    
    /* Build the request */
    sprintf(request, "{"
                     "\"companion_name\": \"%s\","
                     "\"change\": %d,"
                     "\"reason\": \"%s\""
                     "}",
            companion->name, change, reason ? reason : "");
    
    /* Call the MCP server */
    response = mcp_client_call(COMPANION_RELATIONSHIP_ENDPOINT, request);
    if (!response)
        return false;
    
    /* Parse the response */
    mcp_response_get_int(response, "relationship_level", &companion->relationship_level);
    
    mcp_response_free(response);
    return true;
} 