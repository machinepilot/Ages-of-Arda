---
title: MCP Integration Patterns for C Codebases
id: mcp-integration-patterns-for-c-codebases
section: development
category: guides
created: '2025-03-14'
updated: '2025-03-14'
version: 0.1.0
---

# MCP Integration Patterns for C Codebases

## Overview

This document outlines specific patterns and strategies for integrating Model Context Protocol (MCP) into C codebases, with a focus on Angband's architecture. These patterns enable AI-powered narrative generation while preserving the performance and structure of the original game.

## C Client Implementation Patterns

### HTTP Client Pattern

A lightweight HTTP client implementation for C that can communicate with the MCP server:

```c
typedef struct mcp_client {
    char server_url[256];
    char api_key[64];
    int timeout_ms;
    // Optional connection pool/cache
    void *connection_cache;
} mcp_client_t;

typedef struct mcp_response {
    char *content;
    size_t length;
    int status_code;
    char error_message[256];
} mcp_response_t;

// Initialize client
mcp_client_t *mcp_client_init(const char *server_url, const char *api_key);

// Make MCP tool request
mcp_response_t *mcp_invoke_tool(mcp_client_t *client, const char *tool_name, 
                             const char *json_params);

// Free response resources
void mcp_response_free(mcp_response_t *response);

// Cleanup client
void mcp_client_free(mcp_client_t *client);
```

### Asynchronous Request Pattern

Non-blocking requests to prevent game slowdown during API calls:

```c
typedef void (*mcp_callback_fn)(mcp_response_t *response, void *user_data);

// Asynchronous tool invocation
void mcp_invoke_tool_async(mcp_client_t *client, const char *tool_name,
                       const char *json_params, mcp_callback_fn callback,
                       void *user_data);

// Check for completed requests
void mcp_process_pending_requests(mcp_client_t *client);
```

### JSON Handling Pattern

Lightweight JSON generation and parsing for C:

```c
// Simple JSON builder
typedef struct json_builder json_builder_t;

json_builder_t *json_builder_create();
void json_builder_add_string(json_builder_t *builder, const char *key, const char *value);
void json_builder_add_int(json_builder_t *builder, const char *key, int value);
void json_builder_add_bool(json_builder_t *builder, const char *key, bool value);
void json_builder_start_array(json_builder_t *builder, const char *key);
void json_builder_end_array(json_builder_t *builder);
void json_builder_start_object(json_builder_t *builder, const char *key);
void json_builder_end_object(json_builder_t *builder);
char *json_builder_get_string(json_builder_t *builder);
void json_builder_free(json_builder_t *builder);

// Simple JSON parser
typedef struct json_parser json_parser_t;

json_parser_t *json_parser_create(const char *json_str);
const char *json_parser_get_string(json_parser_t *parser, const char *key);
int json_parser_get_int(json_parser_t *parser, const char *key);
bool json_parser_get_bool(json_parser_t *parser, const char *key);
void json_parser_free(json_parser_t *parser);
```

## Game Integration Patterns

### Event Hook Pattern

Strategic placement of hooks in the game code to trigger narrative generation:

```c
// Hook definition
typedef void (*narrative_hook_fn)(game_event_type event, game_event_data *data);

// Register hook for specific event type
void register_narrative_hook(game_event_type event, narrative_hook_fn hook);

// Example event types for narrative triggers
typedef enum {
    EVENT_PLAYER_LEVEL_UP,
    EVENT_MONSTER_DEATH,
    EVENT_FIND_ARTIFACT,
    EVENT_ENTER_NEW_LEVEL,
    EVENT_NEAR_DEATH_ESCAPE,
    EVENT_QUEST_COMPLETE,
    // ... other narrative-worthy events
} narrative_event_type;

// Example hook implementation
void on_monster_death(game_event_type event, game_event_data *data) {
    monster_type *m_ptr = data->monster;
    
    // Only trigger for noteworthy monsters
    if (m_ptr->level >= player->level + 10 || m_ptr->is_unique) {
        char json_params[1024];
        
        // Build JSON parameters for the narrative request
        sprintf(json_params, 
                "{"
                "\"event\":\"monster_death\","
                "\"monster_name\":\"%s\","
                "\"monster_level\":%d,"
                "\"unique\":%s,"
                "\"player_name\":\"%s\","
                "\"player_level\":%d,"
                "\"player_class\":\"%s\","
                "\"dungeon_level\":%d"
                "}",
                m_ptr->name, m_ptr->level, 
                m_ptr->is_unique ? "true" : "false",
                player->name, player->level, 
                player->class->name, player->depth);
        
        // Queue async request
        mcp_invoke_tool_async(mcp_client, "generateNarrative", 
                          json_params, on_narrative_received, NULL);
    }
}
```

### Narrative Display Pattern

Integration with the game's text display system:

```c
// Narrative text display structure
typedef struct {
    char text[1024];
    int importance;  // How important this narrative is (affects display duration)
    bool is_spoken; // Whether this is spoken dialog from the Bard
    char speaker[32]; // Name of speaker if is_spoken is true
} narrative_text_t;

// Queue of pending narratives
narrative_text_t narrative_queue[NARRATIVE_QUEUE_SIZE];
int narrative_queue_size = 0;

// Add narrative to display queue
void queue_narrative(const char *text, int importance, bool is_spoken, const char *speaker) {
    if (narrative_queue_size < NARRATIVE_QUEUE_SIZE) {
        narrative_text_t *narrative = &narrative_queue[narrative_queue_size++];
        my_strcpy(narrative->text, text, sizeof(narrative->text));
        narrative->importance = importance;
        narrative->is_spoken = is_spoken;
        
        if (is_spoken && speaker) {
            my_strcpy(narrative->speaker, speaker, sizeof(narrative->speaker));
        } else {
            narrative->speaker[0] = '\0';
        }
    }
}

// Process narratives during game loop
void process_narrative_queue(void) {
    if (narrative_queue_size > 0) {
        narrative_text_t *narrative = &narrative_queue[0];
        
        // Display the narrative text appropriately
        if (narrative->is_spoken) {
            display_message("%s: %s", narrative->speaker, narrative->text);
        } else {
            display_message("%s", narrative->text);
        }
        
        // Remove from queue
        memmove(&narrative_queue[0], &narrative_queue[1], 
                (narrative_queue_size - 1) * sizeof(narrative_text_t));
        narrative_queue_size--;
    }
}
```

### State Serialization Pattern

Efficiently packaging game state for narrative context:

```c
// Build a compact representation of relevant game state
char *build_game_state_json(void) {
    json_builder_t *builder = json_builder_create();
    
    // Player information
    json_builder_start_object(builder, "player");
    json_builder_add_string(builder, "name", player->name);
    json_builder_add_int(builder, "level", player->level);
    json_builder_add_string(builder, "race", player->race->name);
    json_builder_add_string(builder, "class", player->class->name);
    json_builder_add_int(builder, "hp", player->chp);
    json_builder_add_int(builder, "max_hp", player->mhp);
    json_builder_end_object(builder);
    
    // Location information
    json_builder_start_object(builder, "location");
    json_builder_add_int(builder, "dungeon_level", player->depth);
    json_builder_add_string(builder, "level_feeling", describe_level_feeling());
    json_builder_end_object(builder);
    
    // Recent events (from circular buffer)
    json_builder_start_array(builder, "recent_events");
    for (int i = 0; i < recent_event_count; i++) {
        json_builder_start_object(builder, NULL);
        json_builder_add_string(builder, "type", recent_events[i].type);
        json_builder_add_string(builder, "description", recent_events[i].description);
        json_builder_add_int(builder, "turn", recent_events[i].turn);
        json_builder_end_object(builder);
    }
    json_builder_end_array(builder);
    
    char *result = json_builder_get_string(builder);
    json_builder_free(builder);
    
    return result;
}
```

### Memory Persistence Pattern

Save and load narrative context across game sessions:

```c
// Save narrative context to savefile
void save_narrative_context(savefile_ptr file) {
    // Write version info
    wr_u16b(file, NARRATIVE_CONTEXT_VERSION);
    
    // Write event history size
    wr_u16b(file, recent_event_count);
    
    // Write each event
    for (int i = 0; i < recent_event_count; i++) {
        wr_string(file, recent_events[i].type);
        wr_string(file, recent_events[i].description);
        wr_u32b(file, recent_events[i].turn);
    }
    
    // Write relationship data
    wr_u16b(file, relationship_count);
    for (int i = 0; i < relationship_count; i++) {
        wr_string(file, relationships[i].entity_name);
        wr_s16b(file, relationships[i].affinity);
        wr_string(file, relationships[i].last_interaction);
    }
}

// Load narrative context from savefile
void load_narrative_context(savefile_ptr file) {
    // Read version info
    u16b version = rd_u16b(file);
    
    // Read event history
    recent_event_count = rd_u16b(file);
    for (int i = 0; i < recent_event_count; i++) {
        recent_events[i].type = rd_string(file);
        recent_events[i].description = rd_string(file);
        recent_events[i].turn = rd_u32b(file);
    }
    
    // Read relationship data
    relationship_count = rd_u16b(file);
    for (int i = 0; i < relationship_count; i++) {
        relationships[i].entity_name = rd_string(file);
        relationships[i].affinity = rd_s16b(file);
        relationships[i].last_interaction = rd_string(file);
    }
}
```

## Performance Optimization Patterns

### Request Batching Pattern

Group multiple narrative requests to reduce API calls:

```c
// Narrative request structure
typedef struct {
    narrative_event_type event;
    void *event_data;
    game_turn_t game_turn;
    mcp_callback_fn callback;
    void *user_data;
} narrative_request_t;

// Batch of pending requests
narrative_request_t request_batch[MAX_BATCH_SIZE];
int batch_size = 0;

// Add request to batch
void batch_narrative_request(narrative_event_type event, void *event_data,
                          mcp_callback_fn callback, void *user_data) {
    if (batch_size < MAX_BATCH_SIZE) {
        narrative_request_t *req = &request_batch[batch_size++];
        req->event = event;
        req->event_data = event_data;
        req->game_turn = game_turn;
        req->callback = callback;
        req->user_data = user_data;
    }
}

// Process batched requests
void process_narrative_batch(void) {
    if (batch_size == 0)
        return;
        
    // Only process batch periodically or when full
    if (batch_size < MAX_BATCH_SIZE && (game_turn % BATCH_PROCESSING_INTERVAL != 0))
        return;
    
    // Build combined JSON for all requests
    json_builder_t *builder = json_builder_create();
    json_builder_start_array(builder, "events");
    
    for (int i = 0; i < batch_size; i++) {
        narrative_request_t *req = &request_batch[i];
        json_builder_start_object(builder, NULL);
        json_builder_add_string(builder, "type", event_type_to_string(req->event));
        
        // Serialize event-specific data
        switch (req->event) {
            case EVENT_MONSTER_DEATH:
                add_monster_death_data(builder, req->event_data);
                break;
            case EVENT_FIND_ARTIFACT:
                add_artifact_data(builder, req->event_data);
                break;
            // ... other event types
        }
        
        json_builder_add_int(builder, "turn", req->game_turn);
        json_builder_end_object(builder);
    }
    
    json_builder_end_array(builder);
    
    // Add current game state
    json_builder_add_string(builder, "game_state", build_game_state_json());
    
    char *json_params = json_builder_get_string(builder);
    json_builder_free(builder);
    
    // Make the batch request
    mcp_invoke_tool_async(mcp_client, "generateNarrativeBatch", 
                      json_params, on_batch_narrative_received, NULL);
    
    // Clear the batch
    batch_size = 0;
}
```

### Cache Pattern

Cache responses to reduce API calls:

```c
#define NARRATIVE_CACHE_SIZE 128

typedef struct {
    char key[64];
    char narrative[1024];
    game_turn_t timestamp;
} narrative_cache_entry_t;

narrative_cache_entry_t narrative_cache[NARRATIVE_CACHE_SIZE];
int cache_count = 0;

// Generate cache key from request parameters
void generate_cache_key(const char *event_type, const void *event_data, char *key, size_t key_size) {
    // Implementation depends on event type
    // Example for monster death:
    if (strcmp(event_type, "monster_death") == 0) {
        const monster_type *m_ptr = (const monster_type *)event_data;
        snprintf(key, key_size, "death_%s_%d", m_ptr->name, m_ptr->level);
    }
    // ...other event types
}

// Look up narrative in cache
const char *find_cached_narrative(const char *key) {
    for (int i = 0; i < cache_count; i++) {
        if (strcmp(narrative_cache[i].key, key) == 0) {
            // Check if cache entry is still valid (not too old)
            if (game_turn - narrative_cache[i].timestamp < CACHE_TTL) {
                return narrative_cache[i].narrative;
            }
            break;
        }
    }
    return NULL;
}

// Add narrative to cache
void cache_narrative(const char *key, const char *narrative) {
    // Replace oldest entry if cache is full
    int target_idx = cache_count < NARRATIVE_CACHE_SIZE ? cache_count++ : 0;
    game_turn_t oldest_time = narrative_cache[0].timestamp;
    
    for (int i = 1; i < cache_count; i++) {
        if (narrative_cache[i].timestamp < oldest_time) {
            oldest_time = narrative_cache[i].timestamp;
            target_idx = i;
        }
    }
    
    // Store in cache
    my_strcpy(narrative_cache[target_idx].key, key, sizeof(narrative_cache[target_idx].key));
    my_strcpy(narrative_cache[target_idx].narrative, narrative, 
             sizeof(narrative_cache[target_idx].narrative));
    narrative_cache[target_idx].timestamp = game_turn;
}
```

## Testing and Debugging Patterns

### Mock Server Pattern

Test MCP integration without real server calls:

```c
// Mock MCP responses for testing
typedef struct {
    char tool_name[64];
    char params_pattern[256];
    char response[1024];
} mock_response_t;

mock_response_t mock_responses[MAX_MOCK_RESPONSES];
int mock_response_count = 0;

// Add mock response
void add_mock_response(const char *tool, const char *params_pattern, const char *response) {
    if (mock_response_count < MAX_MOCK_RESPONSES) {
        mock_response_t *mock = &mock_responses[mock_response_count++];
        my_strcpy(mock->tool_name, tool, sizeof(mock->tool_name));
        my_strcpy(mock->params_pattern, params_pattern, sizeof(mock->params_pattern));
        my_strcpy(mock->response, response, sizeof(mock->response));
    }
}

// Find matching mock response
const char *find_mock_response(const char *tool, const char *params) {
    for (int i = 0; i < mock_response_count; i++) {
        if (strcmp(mock_responses[i].tool_name, tool) == 0 && 
            strstr(params, mock_responses[i].params_pattern) != NULL) {
            return mock_responses[i].response;
        }
    }
    return NULL;
}

// Mock client implementation
mcp_response_t *mock_mcp_invoke_tool(mcp_client_t *client, const char *tool_name, 
                                  const char *json_params) {
    mcp_response_t *response = malloc(sizeof(mcp_response_t));
    memset(response, 0, sizeof(mcp_response_t));
    
    const char *mock_content = find_mock_response(tool_name, json_params);
    if (mock_content) {
        response->content = strdup(mock_content);
        response->length = strlen(response->content);
        response->status_code = 200;
    } else {
        response->status_code = 404;
        strcpy(response->error_message, "No mock response found");
    }
    
    return response;
}
```

## Resources

- Angband C Coding Style Guide
- MCP C Client Reference Implementation
- Narrative Integration Best Practices 