/**
 * @file bard.c
 * @brief Implementation of the Lute the Bard narrative system in Tower of Babel
 */

#include "bard.h"
#include "mcp-client.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>

#define BARD_MAX_QUEUE_SIZE 20
#define BARD_MAX_TEXT_SIZE 1024

/* Tool names for MCP invocation */
#define TOOL_GENERATE_NARRATIVE "generate_narrative"
#define TOOL_UPDATE_MEMORY "update_memory"
#define TOOL_QUERY_MEMORY "query_memory"

/**
 * @brief Structure to hold narrative text in the queue
 */
typedef struct {
    char text[BARD_MAX_TEXT_SIZE];
    bool is_spoken;
    int importance;
    time_t timestamp;
} narrative_entry;

/**
 * @brief Structure to hold the bard state
 */
typedef struct {
    bool initialized;
    bool paused;
    bool debug;
    
    mcp_client *client;
    char character_id[64];
    
    /* Configuration */
    int narrative_frequency; /* 0-100 */
    int verbosity;           /* 0-100 */
    char default_style[32];
    
    /* Player info */
    char player_name[32];
    char player_race[32];
    char player_class[32];
    int player_level;
    
    /* Narrative queue */
    narrative_entry queue[BARD_MAX_QUEUE_SIZE];
    int queue_head;
    int queue_tail;
    int queue_size;
    
    /* Request tracking */
    char pending_requests[10][64]; /* Track IDs of pending requests */
    int num_pending_requests;
    
} bard_state;

/* Global bard state */
static bard_state bard;

/* Private function prototypes */
static void bard_init_state(void);
static bool bard_queue_narrative(const char *text, bool is_spoken, int importance);
static bool bard_handle_response(const char *request_id, const char *response_json);
static bool bard_invoke_narrative_tool(const char *event_type, const char *event_data, 
                                     const char *style, const char *tone);
static void bard_build_context_json(char *buffer, size_t buffer_size);

/* Implementation of public functions */

bool bard_init(const char *server_url, const char *api_key, const char *character_id) {
    if (bard.initialized) {
        return true; /* Already initialized */
    }
    
    /* Initialize state */
    bard_init_state();
    
    /* Store character ID */
    if (character_id) {
        strncpy(bard.character_id, character_id, sizeof(bard.character_id) - 1);
    }
    
    /* Initialize MCP client */
    bard.client = mcp_client_init(server_url, api_key);
    if (!bard.client) {
        fprintf(stderr, "Failed to initialize MCP client\n");
        return false;
    }
    
    /* Set default configuration */
    bard.narrative_frequency = 50; /* Medium frequency */
    bard.verbosity = 50;          /* Medium verbosity */
    strcpy(bard.default_style, "fantasy");
    
    bard.initialized = true;
    
    if (bard.debug) {
        printf("Bard system initialized with URL: %s\n", server_url);
    }
    
    return true;
}

void bard_shutdown(void) {
    if (!bard.initialized) {
        return;
    }
    
    /* Free MCP client */
    if (bard.client) {
        mcp_client_free(bard.client);
        bard.client = NULL;
    }
    
    bard.initialized = false;
    
    if (bard.debug) {
        printf("Bard system shutdown\n");
    }
}

int bard_process_pending(void) {
    int processed = 0;
    
    if (!bard.initialized || bard.paused) {
        return 0;
    }
    
    /* Process any completed requests */
    for (int i = 0; i < bard.num_pending_requests; i++) {
        char *request_id = bard.pending_requests[i];
        
        /* Check if request is complete */
        if (mcp_client_is_request_complete(bard.client, request_id)) {
            char *response = mcp_client_get_response(bard.client, request_id);
            
            if (response) {
                /* Process the response */
                if (bard_handle_response(request_id, response)) {
                    processed++;
                }
                
                /* Free the response */
                free(response);
                
                /* Remove this request from pending list */
                for (int j = i; j < bard.num_pending_requests - 1; j++) {
                    strcpy(bard.pending_requests[j], bard.pending_requests[j + 1]);
                }
                bard.num_pending_requests--;
                i--; /* Re-process this index since we shifted elements */
            }
        }
    }
    
    return processed;
}

bool bard_is_initialized(void) {
    return bard.initialized;
}

void bard_set_paused(bool paused) {
    bard.paused = paused;
    
    if (bard.debug) {
        printf("Bard system %s\n", paused ? "paused" : "resumed");
    }
}

bool bard_is_paused(void) {
    return bard.paused;
}

bool bard_configure(int frequency, int verbosity, const char *default_style) {
    if (!bard.initialized) {
        return false;
    }
    
    /* Validate parameters */
    if (frequency < 0 || frequency > 100 || verbosity < 0 || verbosity > 100) {
        return false;
    }
    
    bard.narrative_frequency = frequency;
    bard.verbosity = verbosity;
    
    if (default_style) {
        strncpy(bard.default_style, default_style, sizeof(bard.default_style) - 1);
    }
    
    if (bard.debug) {
        printf("Bard configured: frequency=%d, verbosity=%d, style=%s\n",
               frequency, verbosity, bard.default_style);
    }
    
    return true;
}

bool bard_narrate_monster_death(const char *monster_name, int monster_level, 
                               bool is_unique, const char *style, const char *tone) {
    if (!bard.initialized || bard.paused) {
        return false;
    }
    
    /* Decide whether to generate narrative based on frequency setting */
    if (rand() % 100 > bard.narrative_frequency) {
        return true; /* Skip narrative but report success */
    }
    
    /* Create event data */
    char event_data[512];
    snprintf(event_data, sizeof(event_data),
             "{\"monster_name\":\"%s\",\"monster_level\":%d,\"is_unique\":%s}",
             monster_name, monster_level, is_unique ? "true" : "false");
    
    return bard_invoke_narrative_tool("monster_death", event_data, style, tone);
}

bool bard_narrate_item_discovery(const char *item_name, bool is_artifact,
                                const char *item_type, const char *style, 
                                const char *tone) {
    if (!bard.initialized || bard.paused) {
        return false;
    }
    
    /* Decide whether to generate narrative based on frequency setting */
    if (rand() % 100 > bard.narrative_frequency) {
        return true; /* Skip narrative but report success */
    }
    
    /* Create event data */
    char event_data[512];
    snprintf(event_data, sizeof(event_data),
             "{\"item_name\":\"%s\",\"is_artifact\":%s,\"item_type\":\"%s\"}",
             item_name, is_artifact ? "true" : "false", item_type ? item_type : "unknown");
    
    return bard_invoke_narrative_tool("item_discovery", event_data, style, tone);
}

bool bard_narrate_new_level(int dungeon_level, const char *level_feeling,
                           const char *style, const char *tone) {
    if (!bard.initialized || bard.paused) {
        return false;
    }
    
    /* Always generate narrative for new levels */
    
    /* Create event data */
    char event_data[512];
    snprintf(event_data, sizeof(event_data),
             "{\"dungeon_level\":%d,\"level_feeling\":\"%s\"}",
             dungeon_level, level_feeling ? level_feeling : "normal");
    
    return bard_invoke_narrative_tool("new_level", event_data, style, tone);
}

bool bard_narrate_near_death(int hp_percent, const char *enemy_name,
                            const char *style, const char *tone) {
    if (!bard.initialized || bard.paused) {
        return false;
    }
    
    /* Always generate narrative for near-death experiences */
    
    /* Create event data */
    char event_data[512];
    if (enemy_name) {
        snprintf(event_data, sizeof(event_data),
                 "{\"hp_percent\":%d,\"enemy_name\":\"%s\"}",
                 hp_percent, enemy_name);
    } else {
        snprintf(event_data, sizeof(event_data),
                 "{\"hp_percent\":%d}", hp_percent);
    }
    
    return bard_invoke_narrative_tool("near_death", event_data, style, tone);
}

bool bard_narrate_quest_complete(const char *quest_name, int quest_level,
                                const char *style, const char *tone) {
    if (!bard.initialized || bard.paused) {
        return false;
    }
    
    /* Always generate narrative for quest completions */
    
    /* Create event data */
    char event_data[512];
    snprintf(event_data, sizeof(event_data),
             "{\"quest_name\":\"%s\",\"quest_level\":%d}",
             quest_name, quest_level);
    
    return bard_invoke_narrative_tool("quest_complete", event_data, style, tone);
}

bool bard_narrate_level_up(int new_level, const char *class_name,
                          const char *style, const char *tone) {
    if (!bard.initialized || bard.paused) {
        return false;
    }
    
    /* Always generate narrative for level ups */
    
    /* Create event data */
    char event_data[512];
    snprintf(event_data, sizeof(event_data),
             "{\"new_level\":%d,\"class\":\"%s\"}",
             new_level, class_name ? class_name : bard.player_class);
    
    return bard_invoke_narrative_tool("level_up", event_data, style, tone);
}

bool bard_narrate_custom(const char *event_type, const char *event_data,
                        const char *style, const char *tone) {
    if (!bard.initialized || bard.paused) {
        return false;
    }
    
    /* Decide whether to generate narrative based on frequency setting */
    if (rand() % 100 > bard.narrative_frequency) {
        return true; /* Skip narrative but report success */
    }
    
    return bard_invoke_narrative_tool(event_type, event_data, style, tone);
}

int bard_get_queue_length(void) {
    return bard.queue_size;
}

bool bard_get_next_narrative(char *text, size_t max_text_len, bool *is_spoken, int *importance) {
    if (!bard.initialized || bard.queue_size == 0 || !text || max_text_len == 0) {
        return false;
    }
    
    /* Get the next narrative from the queue */
    narrative_entry *entry = &bard.queue[bard.queue_head];
    
    /* Copy the narrative text to the output buffer */
    strncpy(text, entry->text, max_text_len - 1);
    text[max_text_len - 1] = '\0';
    
    /* Set other output parameters if provided */
    if (is_spoken) {
        *is_spoken = entry->is_spoken;
    }
    
    if (importance) {
        *importance = entry->importance;
    }
    
    /* Remove the entry from the queue */
    bard.queue_head = (bard.queue_head + 1) % BARD_MAX_QUEUE_SIZE;
    bard.queue_size--;
    
    return true;
}

bool bard_update_player_info(const char *name, const char *race, const char *class_name, int level) {
    if (!bard.initialized) {
        return false;
    }
    
    /* Update player info */
    if (name) {
        strncpy(bard.player_name, name, sizeof(bard.player_name) - 1);
    }
    
    if (race) {
        strncpy(bard.player_race, race, sizeof(bard.player_race) - 1);
    }
    
    if (class_name) {
        strncpy(bard.player_class, class_name, sizeof(bard.player_class) - 1);
    }
    
    bard.player_level = level;
    
    if (bard.debug) {
        printf("Updated player info: %s (%s %s), level %d\n",
               bard.player_name, bard.player_race, bard.player_class, bard.player_level);
    }
    
    return true;
}

void bard_set_debug(bool debug) {
    bard.debug = debug;
}

/* Private functions */

static void bard_init_state(void) {
    memset(&bard, 0, sizeof(bard_state));
    
    /* Initialize random seed */
    srand(time(NULL));
    
    /* Initialize queue */
    bard.queue_head = 0;
    bard.queue_tail = 0;
    bard.queue_size = 0;
}

static bool bard_queue_narrative(const char *text, bool is_spoken, int importance) {
    if (bard.queue_size >= BARD_MAX_QUEUE_SIZE) {
        /* Queue is full - remove the oldest or least important entry */
        int least_important_idx = bard.queue_head;
        int least_importance = bard.queue[bard.queue_head].importance;
        
        for (int i = 0; i < bard.queue_size; i++) {
            int idx = (bard.queue_head + i) % BARD_MAX_QUEUE_SIZE;
            if (bard.queue[idx].importance < least_importance) {
                least_important_idx = idx;
                least_importance = bard.queue[idx].importance;
            }
        }
        
        /* If the new narrative is less important than all existing ones, discard it */
        if (importance <= least_importance) {
            return false;
        }
        
        /* Remove the least important entry */
        if (least_important_idx == bard.queue_head) {
            bard.queue_head = (bard.queue_head + 1) % BARD_MAX_QUEUE_SIZE;
        } else {
            /* Shift entries to fill the gap */
            for (int i = least_important_idx; i != bard.queue_tail; i = (i + 1) % BARD_MAX_QUEUE_SIZE) {
                int next = (i + 1) % BARD_MAX_QUEUE_SIZE;
                if (next == bard.queue_tail) {
                    break;
                }
                memcpy(&bard.queue[i], &bard.queue[next], sizeof(narrative_entry));
            }
            bard.queue_tail = (bard.queue_tail + BARD_MAX_QUEUE_SIZE - 1) % BARD_MAX_QUEUE_SIZE;
        }
        bard.queue_size--;
    }
    
    /* Add new narrative to the queue */
    narrative_entry *entry = &bard.queue[bard.queue_tail];
    strncpy(entry->text, text, sizeof(entry->text) - 1);
    entry->text[sizeof(entry->text) - 1] = '\0';
    entry->is_spoken = is_spoken;
    entry->importance = importance;
    entry->timestamp = time(NULL);
    
    /* Update queue tail and size */
    bard.queue_tail = (bard.queue_tail + 1) % BARD_MAX_QUEUE_SIZE;
    bard.queue_size++;
    
    if (bard.debug) {
        printf("Queued narrative: %s\n", text);
    }
    
    return true;
}

static bool bard_handle_response(const char *request_id, const char *response_json) {
    if (bard.debug) {
        printf("Handling response for request %s\n", request_id);
    }
    
    /* Parse JSON response */
    mcp_json *json = mcp_json_parse(response_json);
    if (!json) {
        fprintf(stderr, "Failed to parse response JSON\n");
        return false;
    }
    
    /* Extract narrative text */
    const char *narrative = mcp_json_get_string(json, "narrative");
    bool is_spoken = mcp_json_get_bool(json, "is_spoken", false);
    int importance = mcp_json_get_int(json, "importance", 50);
    
    if (narrative) {
        /* Queue the narrative */
        bard_queue_narrative(narrative, is_spoken, importance);
    } else {
        fprintf(stderr, "Response missing narrative field\n");
    }
    
    /* Clean up */
    mcp_json_free(json);
    
    return narrative != NULL;
}

static bool bard_invoke_narrative_tool(const char *event_type, const char *event_data, 
                                     const char *style, const char *tone) {
    if (!bard.initialized || !bard.client) {
        return false;
    }
    
    /* Construct parameters */
    mcp_json *params = mcp_json_create_object();
    if (!params) {
        return false;
    }
    
    /* Add event type and data */
    mcp_json_set_string(params, "event_type", event_type);
    mcp_json_set_string(params, "event_data", event_data);
    
    /* Add style and tone if provided */
    if (style) {
        mcp_json_set_string(params, "style", style);
    } else {
        mcp_json_set_string(params, "style", bard.default_style);
    }
    
    if (tone) {
        mcp_json_set_string(params, "tone", tone);
    }
    
    /* Add character ID */
    mcp_json_set_string(params, "character_id", bard.character_id);
    
    /* Add player info */
    mcp_json *player_info = mcp_json_create_object();
    mcp_json_set_string(player_info, "name", bard.player_name);
    mcp_json_set_string(player_info, "race", bard.player_race);
    mcp_json_set_string(player_info, "class", bard.player_class);
    mcp_json_set_int(player_info, "level", bard.player_level);
    mcp_json_set_object(params, "player_info", player_info);
    
    /* Add verbosity setting */
    mcp_json_set_int(params, "verbosity", bard.verbosity);
    
    /* Convert parameters to JSON string */
    char *params_json = mcp_json_stringify(params);
    mcp_json_free(params);
    
    if (!params_json) {
        return false;
    }
    
    /* Invoke the tool */
    char request_id[64];
    if (!mcp_client_invoke_tool_async(bard.client, TOOL_GENERATE_NARRATIVE, 
                                      params_json, request_id, sizeof(request_id))) {
        free(params_json);
        return false;
    }
    
    free(params_json);
    
    /* Add to pending requests */
    if (bard.num_pending_requests < 10) {
        strcpy(bard.pending_requests[bard.num_pending_requests], request_id);
        bard.num_pending_requests++;
        
        if (bard.debug) {
            printf("Added request %s to pending list (total: %d)\n", 
                   request_id, bard.num_pending_requests);
        }
    } else {
        fprintf(stderr, "Too many pending requests\n");
        return false;
    }
    
    return true;
}

static void bard_build_context_json(char *buffer, size_t buffer_size) {
    snprintf(buffer, buffer_size,
             "{"
             "\"character_id\":\"%s\","
             "\"player\":{"
             "\"name\":\"%s\","
             "\"race\":\"%s\","
             "\"class\":\"%s\","
             "\"level\":%d"
             "}"
             "}",
             bard.character_id,
             bard.player_name,
             bard.player_race,
             bard.player_class,
             bard.player_level);
} 