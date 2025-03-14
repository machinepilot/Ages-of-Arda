/**
 * @file test-mcp-client.c
 * @brief Test program for the MCP client
 *
 * This program tests the MCP client by making various narrative requests
 * and printing the responses.
 */

#include "mcp-client.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>

#ifdef _WIN32
#include <windows.h>
#define sleep(x) Sleep((x) * 1000)
#else
#include <unistd.h>
#endif

/**
 * @brief Callback function for asynchronous narrative generation
 */
static void narrative_callback(narrative_text_t *narrative, void *user_data) {
    if (narrative) {
        printf("\n=== Narrative Generated (via callback) ===\n");
        printf("Text: %s\n", narrative->text);
        printf("Is spoken: %s\n", narrative->is_spoken ? "Yes" : "No");
        printf("Importance: %d\n", narrative->importance);
        printf("Event ID: %s\n", narrative->event_id);
    } else {
        printf("Narrative generation failed\n");
    }
}

/**
 * @brief Test synchronous narrative generation
 */
void test_sync_narrative(mcp_client_t *client) {
    printf("\n=== Testing Synchronous Narrative Generation ===\n");
    
    // Create a JSON builder for the event data
    void *builder = json_builder_create();
    json_builder_add_string(builder, "monster_name", "Morgoth, Lord of Darkness");
    json_builder_add_int(builder, "monster_level", 100);
    json_builder_add_bool(builder, "is_unique", true);
    
    char *event_data = json_builder_get_string(builder);
    json_builder_free(builder);
    
    // Generate narrative
    printf("Generating narrative for monster_death event...\n");
    narrative_text_t *narrative = mcp_generate_narrative(
        client,
        "monster_death",
        event_data,
        "test-character",
        "epic",
        "triumphant"
    );
    free(event_data);
    
    if (narrative) {
        printf("Narrative generated:\n");
        printf("Text: %s\n", narrative->text);
        printf("Is spoken: %s\n", narrative->is_spoken ? "Yes" : "No");
        printf("Importance: %d\n", narrative->importance);
        printf("Event ID: %s\n", narrative->event_id);
        narrative_text_free(narrative);
    } else {
        printf("Failed to generate narrative\n");
    }
}

/**
 * @brief Test asynchronous narrative generation
 */
void test_async_narrative(mcp_client_t *client) {
    printf("\n=== Testing Asynchronous Narrative Generation ===\n");
    
    // Create a JSON builder for the event data
    void *builder = json_builder_create();
    json_builder_add_string(builder, "item_name", "Narsil, Flame of the West");
    json_builder_add_bool(builder, "is_artifact", true);
    json_builder_add_string(builder, "item_type", "sword");
    
    char *event_data = json_builder_get_string(builder);
    json_builder_free(builder);
    
    // Generate narrative asynchronously
    printf("Requesting asynchronous narrative for item_discovery event...\n");
    bool success = mcp_generate_narrative_async(
        client,
        "item_discovery",
        event_data,
        "test-character",
        "poetic",
        "mystical",
        narrative_callback,
        NULL
    );
    free(event_data);
    
    if (success) {
        printf("Asynchronous request sent successfully\n");
        printf("Processing pending requests...\n");
        
        // Process pending requests for up to 10 seconds
        for (int i = 0; i < 10; i++) {
            int processed = mcp_process_pending_requests(client);
            if (processed > 0) {
                printf("Processed %d requests\n", processed);
                break;
            }
            printf("Waiting for response... (%d/10)\n", i + 1);
            sleep(1);
        }
    } else {
        printf("Failed to send asynchronous request\n");
    }
}

/**
 * @brief Test direct tool invocation
 */
void test_tool_invocation(mcp_client_t *client) {
    printf("\n=== Testing Direct Tool Invocation ===\n");
    
    // Create a JSON builder for the parameters
    void *builder = json_builder_create();
    json_builder_add_string(builder, "event_type", "new_level");
    
    // Add event data as a nested object
    json_builder_start_object(builder, "event_data");
    json_builder_add_int(builder, "dungeon_level", 50);
    json_builder_add_string(builder, "level_feeling", "terrible");
    json_builder_end_object(builder);
    
    json_builder_add_string(builder, "character_id", "test-character");
    json_builder_add_string(builder, "style", "dark");
    json_builder_add_string(builder, "tone", "foreboding");
    
    // Add player info as a nested object
    json_builder_start_object(builder, "player_info");
    json_builder_add_string(builder, "name", "Aragorn");
    json_builder_add_string(builder, "race", "Human");
    json_builder_add_string(builder, "class", "Ranger");
    json_builder_add_int(builder, "level", 30);
    json_builder_end_object(builder);
    
    char *params_json = json_builder_get_string(builder);
    json_builder_free(builder);
    
    printf("Invoking generate_narrative tool with params:\n%s\n", params_json);
    
    // Invoke the tool
    mcp_response_t *response = mcp_invoke_tool(client, "generate_narrative", params_json);
    free(params_json);
    
    if (response) {
        printf("Response received (status %d):\n", response->status_code);
        if (response->status_code >= 200 && response->status_code < 300) {
            printf("%s\n", response->content);
        } else {
            printf("Error: %s\n", response->error_message);
        }
        mcp_response_free(response);
    } else {
        printf("Failed to get response\n");
    }
}

/**
 * @brief Main function
 */
int main(int argc, char *argv[]) {
    const char *server_url = argc > 1 ? argv[1] : "http://localhost:3000";
    const char *api_key = argc > 2 ? argv[2] : NULL;
    
    printf("Testing MCP client with server URL: %s\n", server_url);
    
    // Initialize the MCP client
    mcp_client_t *client = mcp_client_init(server_url, api_key);
    if (!client) {
        fprintf(stderr, "Failed to initialize MCP client\n");
        return 1;
    }
    
    // Configure the client
    mcp_client_configure(client, 5000, 3, true);
    
    // Run tests
    test_sync_narrative(client);
    test_async_narrative(client);
    test_tool_invocation(client);
    
    // Clean up
    mcp_client_free(client);
    
    printf("\nAll tests completed\n");
    return 0;
} 