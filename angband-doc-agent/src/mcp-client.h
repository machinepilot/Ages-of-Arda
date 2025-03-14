/**
 * @file mcp-client.h
 * @brief C client for Model Context Protocol (MCP) integration in Angband
 *
 * This header provides a lightweight MCP client implementation for integrating
 * Claude-powered narrative generation via the Lute the Bard character.
 */

#ifndef INCLUDED_MCP_CLIENT_H
#define INCLUDED_MCP_CLIENT_H

#include <stdbool.h>
#include <stdlib.h>

#ifdef __cplusplus
extern "C" {
#endif

/**
 * @struct mcp_client
 * @brief MCP client context structure
 */
typedef struct mcp_client mcp_client_t;

/**
 * @struct mcp_response
 * @brief Structure containing an MCP server response
 */
typedef struct mcp_response {
    char *content;         /**< Response content (JSON string) */
    size_t length;         /**< Content length */
    int status_code;       /**< HTTP status code */
    char error_message[256]; /**< Error message if status_code indicates failure */
} mcp_response_t;

/**
 * @struct narrative_text
 * @brief Structure containing narrative text generated for a game event
 */
typedef struct narrative_text {
    char *text;            /**< Generated narrative text */
    char tone[32];         /**< Tone of the narrative (triumphant, tense, etc.) */
    bool is_spoken;        /**< Whether the text is spoken by Lute (vs. narration) */
    int importance;        /**< Importance score (0-100) for display prioritization */
    char event_id[64];     /**< ID of the generated event for future reference */
} narrative_text_t;

/**
 * @brief Callback function type for asynchronous MCP requests
 */
typedef void (*mcp_callback_fn)(mcp_response_t *response, void *user_data);

/**
 * @brief Initialize an MCP client
 * 
 * @param server_url URL of the MCP server
 * @param api_key Optional API key for authentication (can be NULL)
 * @return Initialized MCP client or NULL on failure
 */
mcp_client_t *mcp_client_init(const char *server_url, const char *api_key);

/**
 * @brief Set configuration options for the MCP client
 * 
 * @param client Initialized MCP client
 * @param timeout_ms Request timeout in milliseconds (0 for default)
 * @param max_retries Maximum number of retries for failed requests (0 for default)
 * @param verbose Enable verbose logging
 * @return true on success, false on failure
 */
bool mcp_client_configure(mcp_client_t *client, int timeout_ms, int max_retries, bool verbose);

/**
 * @brief Make a synchronous request to invoke an MCP tool
 * 
 * @param client Initialized MCP client
 * @param tool_name Name of the MCP tool to invoke
 * @param json_params JSON string containing the tool parameters
 * @return Response from the MCP server (must be freed with mcp_response_free)
 */
mcp_response_t *mcp_invoke_tool(mcp_client_t *client, const char *tool_name, 
                             const char *json_params);

/**
 * @brief Make an asynchronous request to invoke an MCP tool
 * 
 * @param client Initialized MCP client
 * @param tool_name Name of the MCP tool to invoke
 * @param json_params JSON string containing the tool parameters
 * @param callback Function to call when the response is received
 * @param user_data Pointer passed to the callback function
 * @return true if request was successfully queued, false otherwise
 */
bool mcp_invoke_tool_async(mcp_client_t *client, const char *tool_name,
                        const char *json_params, mcp_callback_fn callback,
                        void *user_data);

/**
 * @brief Process pending asynchronous requests
 * 
 * This function should be called regularly (e.g., once per game loop iteration)
 * to check for completed asynchronous requests and invoke their callbacks.
 * 
 * @param client Initialized MCP client
 * @return Number of completed requests processed
 */
int mcp_process_pending_requests(mcp_client_t *client);

/**
 * @brief Free resources used by an MCP response
 * 
 * @param response Response to free
 */
void mcp_response_free(mcp_response_t *response);

/**
 * @brief Cleanup and free resources used by an MCP client
 * 
 * @param client Client to cleanup
 */
void mcp_client_free(mcp_client_t *client);

/**
 * @brief Generate a narrative for a game event
 * 
 * @param client Initialized MCP client
 * @param event_type Type of event (monster_defeat, item_discovery, etc.)
 * @param event_data JSON string with event details
 * @param character_id Player character ID
 * @param style Narrative style (brief, standard, detailed)
 * @param tone Suggested tone (optional, can be NULL)
 * @return Narrative text structure (must be freed with narrative_text_free)
 */
narrative_text_t *mcp_generate_narrative(mcp_client_t *client, const char *event_type,
                                      const char *event_data, const char *character_id,
                                      const char *style, const char *tone);

/**
 * @brief Generate a narrative asynchronously
 * 
 * @param client Initialized MCP client
 * @param event_type Type of event
 * @param event_data JSON string with event details
 * @param character_id Player character ID
 * @param style Narrative style
 * @param tone Suggested tone (optional)
 * @param callback Function to call with the generated narrative
 * @param user_data Pointer passed to the callback function
 * @return true if request was successfully queued, false otherwise
 */
bool mcp_generate_narrative_async(mcp_client_t *client, const char *event_type,
                               const char *event_data, const char *character_id,
                               const char *style, const char *tone,
                               void (*callback)(narrative_text_t*, void*),
                               void *user_data);

/**
 * @brief Free a narrative text structure
 * 
 * @param narrative Narrative text to free
 */
void narrative_text_free(narrative_text_t *narrative);

/**
 * @brief Helper function to build JSON strings for event data
 * 
 * @return A new JSON builder object (must be freed with json_builder_free)
 */
void *json_builder_create(void);

/**
 * @brief Add a string property to a JSON builder
 * 
 * @param builder JSON builder object
 * @param key Property key
 * @param value String value
 */
void json_builder_add_string(void *builder, const char *key, const char *value);

/**
 * @brief Add an integer property to a JSON builder
 * 
 * @param builder JSON builder object
 * @param key Property key
 * @param value Integer value
 */
void json_builder_add_int(void *builder, const char *key, int value);

/**
 * @brief Add a boolean property to a JSON builder
 * 
 * @param builder JSON builder object
 * @param key Property key
 * @param value Boolean value
 */
void json_builder_add_bool(void *builder, const char *key, bool value);

/**
 * @brief Start a new object property in a JSON builder
 * 
 * @param builder JSON builder object
 * @param key Property key (NULL for array elements)
 */
void json_builder_start_object(void *builder, const char *key);

/**
 * @brief End the current object in a JSON builder
 * 
 * @param builder JSON builder object
 */
void json_builder_end_object(void *builder);

/**
 * @brief Start a new array property in a JSON builder
 * 
 * @param builder JSON builder object
 * @param key Property key
 */
void json_builder_start_array(void *builder, const char *key);

/**
 * @brief End the current array in a JSON builder
 * 
 * @param builder JSON builder object
 */
void json_builder_end_array(void *builder);

/**
 * @brief Get the JSON string from a builder
 * 
 * @param builder JSON builder object
 * @return JSON string (must be freed with free)
 */
char *json_builder_get_string(void *builder);

/**
 * @brief Free a JSON builder
 * 
 * @param builder JSON builder object
 */
void json_builder_free(void *builder);

#ifdef __cplusplus
}
#endif

#endif /* INCLUDED_MCP_CLIENT_H */ 