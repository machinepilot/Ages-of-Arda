/**
 * @file mcp-client.c
 * @brief Implementation of the MCP client for Angband
 */

#include "mcp-client.h"
#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <curl/curl.h>
#include <jansson.h>

#ifdef _WIN32
#include <windows.h>
#else
#include <pthread.h>
#include <unistd.h>
#endif

/* Defines */
#define DEFAULT_TIMEOUT_MS 5000
#define DEFAULT_MAX_RETRIES 3
#define MAX_PENDING_REQUESTS 32
#define USER_AGENT "TowerOfBabel-MCP-Client/1.0"
#define CONTENT_TYPE "application/json"

/* Structs */
struct mcp_client {
    char server_url[256];
    char api_key[64];
    int timeout_ms;
    int max_retries;
    bool verbose;
    struct pending_request {
        bool in_use;
        char tool_name[64];
        char *json_params;
        mcp_callback_fn callback;
        void *user_data;
        CURL *curl_handle;
        struct curl_slist *headers;
        struct memory_buffer {
            char *data;
            size_t size;
        } response_buffer;
    } pending_requests[MAX_PENDING_REQUESTS];
    
    #ifndef _WIN32
    pthread_mutex_t mutex;
    #else
    CRITICAL_SECTION mutex;
    #endif
};

/* Forward declarations */
static size_t curl_write_callback(void *contents, size_t size, size_t nmemb, void *userp);
static void lock_client(mcp_client_t *client);
static void unlock_client(mcp_client_t *client);
static void check_curl_error(mcp_client_t *client, CURLcode res, const char *operation);
static char *append_path_to_url(const char *base_url, const char *path);

/* Type definitions for json_builder */
typedef struct json_builder {
    json_t *root;
    json_t *current;
    json_t *parent_stack[32];
    int stack_depth;
} json_builder_t;

/* MCP client implementation */

mcp_client_t *mcp_client_init(const char *server_url, const char *api_key) {
    mcp_client_t *client;
    CURLcode res;
    
    /* Initialize curl */
    res = curl_global_init(CURL_GLOBAL_DEFAULT);
    if (res != CURLE_OK) {
        fprintf(stderr, "curl_global_init failed: %s\n", curl_easy_strerror(res));
        return NULL;
    }
    
    /* Allocate client structure */
    client = (mcp_client_t *)calloc(1, sizeof(mcp_client_t));
    if (!client) {
        curl_global_cleanup();
        return NULL;
    }
    
    /* Initialize client data */
    strncpy(client->server_url, server_url, sizeof(client->server_url) - 1);
    if (api_key) {
        strncpy(client->api_key, api_key, sizeof(client->api_key) - 1);
    }
    client->timeout_ms = DEFAULT_TIMEOUT_MS;
    client->max_retries = DEFAULT_MAX_RETRIES;
    
    /* Initialize mutex */
    #ifdef _WIN32
    InitializeCriticalSection(&client->mutex);
    #else
    pthread_mutex_init(&client->mutex, NULL);
    #endif
    
    /* Initialize pending requests */
    memset(client->pending_requests, 0, sizeof(client->pending_requests));
    
    return client;
}

bool mcp_client_configure(mcp_client_t *client, int timeout_ms, int max_retries, bool verbose) {
    if (!client) {
        return false;
    }
    
    lock_client(client);
    
    if (timeout_ms > 0) {
        client->timeout_ms = timeout_ms;
    }
    
    if (max_retries >= 0) {
        client->max_retries = max_retries;
    }
    
    client->verbose = verbose;
    
    unlock_client(client);
    
    return true;
}

mcp_response_t *mcp_invoke_tool(mcp_client_t *client, const char *tool_name, 
                             const char *json_params) {
    CURL *curl;
    CURLcode res;
    struct curl_slist *headers = NULL;
    struct memory_buffer response_buffer = {0};
    mcp_response_t *response;
    char *url;
    int retry_count = 0;
    
    if (!client || !tool_name || !json_params) {
        return NULL;
    }
    
    /* Allocate response structure */
    response = (mcp_response_t *)calloc(1, sizeof(mcp_response_t));
    if (!response) {
        return NULL;
    }
    
    /* Construct URL */
    url = append_path_to_url(client->server_url, tool_name);
    if (!url) {
        free(response);
        return NULL;
    }
    
    /* Initialize curl handle */
    curl = curl_easy_init();
    if (!curl) {
        free(url);
        free(response);
        return NULL;
    }
    
    /* Set up headers */
    headers = curl_slist_append(headers, "Accept: application/json");
    headers = curl_slist_append(headers, CONTENT_TYPE);
    if (client->api_key[0] != '\0') {
        char auth_header[512];
        snprintf(auth_header, sizeof(auth_header), "Authorization: Bearer %s", client->api_key);
        headers = curl_slist_append(headers, auth_header);
    }
    
    /* Set up curl options */
    curl_easy_setopt(curl, CURLOPT_URL, url);
    curl_easy_setopt(curl, CURLOPT_WRITEFUNCTION, curl_write_callback);
    curl_easy_setopt(curl, CURLOPT_WRITEDATA, (void *)&response_buffer);
    curl_easy_setopt(curl, CURLOPT_HTTPHEADER, headers);
    curl_easy_setopt(curl, CURLOPT_USERAGENT, USER_AGENT);
    curl_easy_setopt(curl, CURLOPT_TIMEOUT_MS, client->timeout_ms);
    curl_easy_setopt(curl, CURLOPT_POSTFIELDS, json_params);
    
    if (client->verbose) {
        curl_easy_setopt(curl, CURLOPT_VERBOSE, 1L);
    }
    
    /* Perform request with retries */
    while (retry_count <= client->max_retries) {
        res = curl_easy_perform(curl);
        
        if (res == CURLE_OK) {
            /* Get HTTP response code */
            curl_easy_getinfo(curl, CURLINFO_RESPONSE_CODE, &response->status_code);
            
            /* Check if response code indicates success */
            if (response->status_code >= 200 && response->status_code < 300) {
                break;
            } else {
                /* Server error, maybe retry */
                if (retry_count < client->max_retries && response->status_code >= 500) {
                    retry_count++;
                    
                    /* Free previous response data */
                    if (response_buffer.data) {
                        free(response_buffer.data);
                        response_buffer.data = NULL;
                        response_buffer.size = 0;
                    }
                    
                    /* Wait before retrying */
                    #ifdef _WIN32
                    Sleep(1000);
                    #else
                    sleep(1);
                    #endif
                    
                    continue;
                }
                
                /* Not retrying, set error message */
                snprintf(response->error_message, sizeof(response->error_message),
                         "HTTP error: %d", response->status_code);
                break;
            }
        } else {
            /* Network error */
            snprintf(response->error_message, sizeof(response->error_message),
                     "CURL error: %s", curl_easy_strerror(res));
            
            /* Retry on some errors */
            if (retry_count < client->max_retries &&
                (res == CURLE_OPERATION_TIMEDOUT || res == CURLE_COULDNT_CONNECT)) {
                retry_count++;
                
                /* Wait before retrying */
                #ifdef _WIN32
                Sleep(1000);
                #else
                sleep(1);
                #endif
                
                continue;
            }
            
            break;
        }
    }
    
    /* Store response content */
    response->content = response_buffer.data;
    response->length = response_buffer.size;
    
    /* Cleanup */
    curl_slist_free_all(headers);
    curl_easy_cleanup(curl);
    free(url);
    
    return response;
}

bool mcp_invoke_tool_async(mcp_client_t *client, const char *tool_name,
                        const char *json_params, mcp_callback_fn callback,
                        void *user_data) {
    int i;
    char *url;
    struct pending_request *request = NULL;
    
    if (!client || !tool_name || !json_params || !callback) {
        return false;
    }
    
    /* Find unused request slot */
    lock_client(client);
    for (i = 0; i < MAX_PENDING_REQUESTS; i++) {
        if (!client->pending_requests[i].in_use) {
            request = &client->pending_requests[i];
            request->in_use = true;
            break;
        }
    }
    unlock_client(client);
    
    if (!request) {
        /* No available slots */
        if (client->verbose) {
            fprintf(stderr, "No available slots for async request\n");
        }
        return false;
    }
    
    /* Construct URL */
    url = append_path_to_url(client->server_url, tool_name);
    if (!url) {
        request->in_use = false;
        return false;
    }
    
    /* Copy request parameters */
    strncpy(request->tool_name, tool_name, sizeof(request->tool_name) - 1);
    request->json_params = strdup(json_params);
    request->callback = callback;
    request->user_data = user_data;
    
    /* Initialize response buffer */
    request->response_buffer.data = NULL;
    request->response_buffer.size = 0;
    
    /* Initialize curl handle */
    request->curl_handle = curl_easy_init();
    if (!request->curl_handle) {
        free(url);
        free(request->json_params);
        request->in_use = false;
        return false;
    }
    
    /* Set up headers */
    request->headers = NULL;
    request->headers = curl_slist_append(request->headers, "Accept: application/json");
    request->headers = curl_slist_append(request->headers, CONTENT_TYPE);
    if (client->api_key[0] != '\0') {
        char auth_header[512];
        snprintf(auth_header, sizeof(auth_header), "Authorization: Bearer %s", client->api_key);
        request->headers = curl_slist_append(request->headers, auth_header);
    }
    
    /* Set up curl options */
    curl_easy_setopt(request->curl_handle, CURLOPT_URL, url);
    curl_easy_setopt(request->curl_handle, CURLOPT_WRITEFUNCTION, curl_write_callback);
    curl_easy_setopt(request->curl_handle, CURLOPT_WRITEDATA, (void *)&request->response_buffer);
    curl_easy_setopt(request->curl_handle, CURLOPT_HTTPHEADER, request->headers);
    curl_easy_setopt(request->curl_handle, CURLOPT_USERAGENT, USER_AGENT);
    curl_easy_setopt(request->curl_handle, CURLOPT_TIMEOUT_MS, client->timeout_ms);
    curl_easy_setopt(request->curl_handle, CURLOPT_POSTFIELDS, request->json_params);
    
    /* Set to non-blocking */
    curl_easy_setopt(request->curl_handle, CURLOPT_NOSIGNAL, 1L);
    
    if (client->verbose) {
        curl_easy_setopt(request->curl_handle, CURLOPT_VERBOSE, 1L);
    }
    
    /* Start the request (non-blocking) */
    CURLcode res = curl_easy_perform(request->curl_handle);
    if (res != CURLE_OK) {
        if (client->verbose) {
            fprintf(stderr, "Failed to start async request: %s\n", curl_easy_strerror(res));
        }
        
        curl_slist_free_all(request->headers);
        curl_easy_cleanup(request->curl_handle);
        free(request->json_params);
        free(url);
        request->in_use = false;
        return false;
    }
    
    free(url);
    return true;
}

int mcp_process_pending_requests(mcp_client_t *client) {
    int i, completed = 0;
    
    if (!client) {
        return 0;
    }
    
    lock_client(client);
    
    for (i = 0; i < MAX_PENDING_REQUESTS; i++) {
        struct pending_request *request = &client->pending_requests[i];
        
        if (request->in_use) {
            CURLcode res;
            long response_code = 0;
            int retry_count = 0;
            bool request_complete = false;
            
            /* Check if request is complete */
            res = curl_easy_getinfo(request->curl_handle, CURLINFO_RESPONSE_CODE, &response_code);
            if (res == CURLE_OK) {
                request_complete = true;
            }
            
            if (request_complete) {
                mcp_response_t *response = calloc(1, sizeof(mcp_response_t));
                
                if (response) {
                    /* Fill response data */
                    response->content = request->response_buffer.data;
                    response->length = request->response_buffer.size;
                    response->status_code = (int)response_code;
                    
                    if (response_code < 200 || response_code >= 300) {
                        snprintf(response->error_message, sizeof(response->error_message),
                                 "HTTP error: %ld", response_code);
                    }
                    
                    /* Call the callback with the response */
                    request->callback(response, request->user_data);
                    
                    /* Don't free response->content, it's owned by the callback now */
                    free(response);
                }
                
                /* Cleanup request resources */
                curl_slist_free_all(request->headers);
                curl_easy_cleanup(request->curl_handle);
                free(request->json_params);
                
                /* Mark request slot as unused */
                request->in_use = false;
                completed++;
            }
        }
    }
    
    unlock_client(client);
    
    return completed;
}

void mcp_response_free(mcp_response_t *response) {
    if (response) {
        if (response->content) {
            free(response->content);
        }
        free(response);
    }
}

void mcp_client_free(mcp_client_t *client) {
    int i;
    
    if (!client) {
        return;
    }
    
    /* Cancel and free any pending requests */
    for (i = 0; i < MAX_PENDING_REQUESTS; i++) {
        struct pending_request *request = &client->pending_requests[i];
        
        if (request->in_use) {
            if (request->curl_handle) {
                curl_easy_cleanup(request->curl_handle);
            }
            if (request->headers) {
                curl_slist_free_all(request->headers);
            }
            if (request->json_params) {
                free(request->json_params);
            }
            if (request->response_buffer.data) {
                free(request->response_buffer.data);
            }
        }
    }
    
    /* Destroy mutex */
    #ifdef _WIN32
    DeleteCriticalSection(&client->mutex);
    #else
    pthread_mutex_destroy(&client->mutex);
    #endif
    
    free(client);
    
    /* Cleanup curl global state */
    curl_global_cleanup();
}

narrative_text_t *mcp_generate_narrative(mcp_client_t *client, const char *event_type,
                                      const char *event_data, const char *character_id,
                                      const char *style, const char *tone) {
    mcp_response_t *response;
    json_t *json_params_obj, *json_response_obj;
    json_error_t json_error;
    char *json_params_str;
    narrative_text_t *narrative = NULL;
    
    if (!client || !event_type || !event_data) {
        return NULL;
    }
    
    /* Create JSON parameters */
    json_params_obj = json_object();
    json_object_set_new(json_params_obj, "eventType", json_string(event_type));
    json_object_set_new(json_params_obj, "eventData", json_loads(event_data, 0, &json_error));
    json_object_set_new(json_params_obj, "characterId", 
                         character_id ? json_string(character_id) : json_string("default"));
    
    if (style) {
        json_object_set_new(json_params_obj, "narrativeStyle", json_string(style));
    }
    
    if (tone) {
        json_object_set_new(json_params_obj, "toneHint", json_string(tone));
    }
    
    /* Convert to string */
    json_params_str = json_dumps(json_params_obj, 0);
    json_decref(json_params_obj);
    
    if (!json_params_str) {
        return NULL;
    }
    
    /* Make the request */
    response = mcp_invoke_tool(client, "generateNarrative", json_params_str);
    free(json_params_str);
    
    if (!response) {
        return NULL;
    }
    
    /* Check for errors */
    if (response->status_code < 200 || response->status_code >= 300) {
        if (client->verbose) {
            fprintf(stderr, "Error generating narrative: %s\n", response->error_message);
        }
        mcp_response_free(response);
        return NULL;
    }
    
    /* Parse response */
    json_response_obj = json_loads(response->content, 0, &json_error);
    if (!json_response_obj) {
        if (client->verbose) {
            fprintf(stderr, "Error parsing narrative response: %s\n", json_error.text);
        }
        mcp_response_free(response);
        return NULL;
    }
    
    /* Extract narrative fields */
    narrative = calloc(1, sizeof(narrative_text_t));
    if (narrative) {
        json_t *text_obj = json_object_get(json_response_obj, "narrative");
        json_t *tone_obj = json_object_get(json_response_obj, "tone");
        json_t *is_spoken_obj = json_object_get(json_response_obj, "is_spoken");
        json_t *event_id_obj = json_object_get(json_response_obj, "eventId");
        
        if (json_is_string(text_obj)) {
            narrative->text = strdup(json_string_value(text_obj));
        } else {
            narrative->text = strdup("Error: narrative text not found in response");
        }
        
        if (json_is_string(tone_obj)) {
            strncpy(narrative->tone, json_string_value(tone_obj), sizeof(narrative->tone) - 1);
        } else {
            strncpy(narrative->tone, "neutral", sizeof(narrative->tone) - 1);
        }
        
        narrative->is_spoken = json_is_true(is_spoken_obj);
        
        if (json_is_string(event_id_obj)) {
            strncpy(narrative->event_id, json_string_value(event_id_obj), sizeof(narrative->event_id) - 1);
        }
        
        /* Default importance based on tone */
        if (strcmp(narrative->tone, "triumphant") == 0 || 
            strcmp(narrative->tone, "solemn") == 0) {
            narrative->importance = 80;
        } else if (strcmp(narrative->tone, "tense") == 0 ||
                  strcmp(narrative->tone, "dramatic") == 0) {
            narrative->importance = 70;
        } else {
            narrative->importance = 50;
        }
    }
    
    json_decref(json_response_obj);
    mcp_response_free(response);
    
    return narrative;
}

/* Callback for async narrative generation */
typedef struct {
    void (*callback)(narrative_text_t*, void*);
    void *user_data;
} narrative_callback_data;

static void narrative_request_callback(mcp_response_t *response, void *user_data) {
    narrative_callback_data *callback_data = (narrative_callback_data *)user_data;
    narrative_text_t *narrative = NULL;
    json_t *json_response_obj;
    json_error_t json_error;
    
    /* Check for valid response */
    if (response && response->status_code >= 200 && response->status_code < 300) {
        /* Parse response */
        json_response_obj = json_loads(response->content, 0, &json_error);
        if (json_response_obj) {
            /* Extract narrative fields */
            narrative = calloc(1, sizeof(narrative_text_t));
            if (narrative) {
                json_t *text_obj = json_object_get(json_response_obj, "narrative");
                json_t *tone_obj = json_object_get(json_response_obj, "tone");
                json_t *is_spoken_obj = json_object_get(json_response_obj, "is_spoken");
                json_t *event_id_obj = json_object_get(json_response_obj, "eventId");
                
                if (json_is_string(text_obj)) {
                    narrative->text = strdup(json_string_value(text_obj));
                } else {
                    narrative->text = strdup("Error: narrative text not found in response");
                }
                
                if (json_is_string(tone_obj)) {
                    strncpy(narrative->tone, json_string_value(tone_obj), sizeof(narrative->tone) - 1);
                } else {
                    strncpy(narrative->tone, "neutral", sizeof(narrative->tone) - 1);
                }
                
                narrative->is_spoken = json_is_true(is_spoken_obj);
                
                if (json_is_string(event_id_obj)) {
                    strncpy(narrative->event_id, json_string_value(event_id_obj), sizeof(narrative->event_id) - 1);
                }
                
                /* Default importance based on tone */
                if (strcmp(narrative->tone, "triumphant") == 0 || 
                    strcmp(narrative->tone, "solemn") == 0) {
                    narrative->importance = 80;
                } else if (strcmp(narrative->tone, "tense") == 0 ||
                        strcmp(narrative->tone, "dramatic") == 0) {
                    narrative->importance = 70;
                } else {
                    narrative->importance = 50;
                }
            }
            
            json_decref(json_response_obj);
        }
    }
    
    /* Call the user callback */
    if (callback_data->callback) {
        callback_data->callback(narrative, callback_data->user_data);
    } else if (narrative) {
        /* No callback to take ownership, so free the narrative */
        narrative_text_free(narrative);
    }
    
    /* Free callback data */
    free(callback_data);
    
    /* Response is freed by the caller (mcp_process_pending_requests) */
}

bool mcp_generate_narrative_async(mcp_client_t *client, const char *event_type,
                               const char *event_data, const char *character_id,
                               const char *style, const char *tone,
                               void (*callback)(narrative_text_t*, void*),
                               void *user_data) {
    json_t *json_params_obj;
    json_error_t json_error;
    char *json_params_str;
    narrative_callback_data *callback_data;
    bool result;
    
    if (!client || !event_type || !event_data || !callback) {
        return false;
    }
    
    /* Create callback data */
    callback_data = malloc(sizeof(narrative_callback_data));
    if (!callback_data) {
        return false;
    }
    
    callback_data->callback = callback;
    callback_data->user_data = user_data;
    
    /* Create JSON parameters */
    json_params_obj = json_object();
    json_object_set_new(json_params_obj, "eventType", json_string(event_type));
    json_object_set_new(json_params_obj, "eventData", json_loads(event_data, 0, &json_error));
    json_object_set_new(json_params_obj, "characterId", 
                         character_id ? json_string(character_id) : json_string("default"));
    
    if (style) {
        json_object_set_new(json_params_obj, "narrativeStyle", json_string(style));
    }
    
    if (tone) {
        json_object_set_new(json_params_obj, "toneHint", json_string(tone));
    }
    
    /* Convert to string */
    json_params_str = json_dumps(json_params_obj, 0);
    json_decref(json_params_obj);
    
    if (!json_params_str) {
        free(callback_data);
        return false;
    }
    
    /* Make the async request */
    result = mcp_invoke_tool_async(client, "generateNarrative", json_params_str, 
                             narrative_request_callback, callback_data);
    
    free(json_params_str);
    
    if (!result) {
        free(callback_data);
    }
    
    return result;
}

void narrative_text_free(narrative_text_t *narrative) {
    if (narrative) {
        if (narrative->text) {
            free(narrative->text);
        }
        free(narrative);
    }
}

/* JSON Builder implementation */

void *json_builder_create(void) {
    json_builder_t *builder = calloc(1, sizeof(json_builder_t));
    if (builder) {
        builder->root = json_object();
        builder->current = builder->root;
        builder->stack_depth = 0;
    }
    return builder;
}

void json_builder_add_string(void *builder_ptr, const char *key, const char *value) {
    json_builder_t *builder = (json_builder_t *)builder_ptr;
    if (builder && key && value) {
        json_object_set_new(builder->current, key, json_string(value));
    }
}

void json_builder_add_int(void *builder_ptr, const char *key, int value) {
    json_builder_t *builder = (json_builder_t *)builder_ptr;
    if (builder && key) {
        json_object_set_new(builder->current, key, json_integer(value));
    }
}

void json_builder_add_bool(void *builder_ptr, const char *key, bool value) {
    json_builder_t *builder = (json_builder_t *)builder_ptr;
    if (builder && key) {
        json_object_set_new(builder->current, key, value ? json_true() : json_false());
    }
}

void json_builder_start_object(void *builder_ptr, const char *key) {
    json_builder_t *builder = (json_builder_t *)builder_ptr;
    if (builder && builder->stack_depth < 31) {
        json_t *new_obj = json_object();
        
        if (key) {
            json_object_set_new(builder->current, key, new_obj);
        } else if (json_is_array(builder->current)) {
            json_array_append_new(builder->current, new_obj);
        }
        
        builder->parent_stack[builder->stack_depth++] = builder->current;
        builder->current = new_obj;
    }
}

void json_builder_end_object(void *builder_ptr) {
    json_builder_t *builder = (json_builder_t *)builder_ptr;
    if (builder && builder->stack_depth > 0) {
        builder->current = builder->parent_stack[--builder->stack_depth];
    }
}

void json_builder_start_array(void *builder_ptr, const char *key) {
    json_builder_t *builder = (json_builder_t *)builder_ptr;
    if (builder && key && builder->stack_depth < 31) {
        json_t *new_array = json_array();
        
        json_object_set_new(builder->current, key, new_array);
        
        builder->parent_stack[builder->stack_depth++] = builder->current;
        builder->current = new_array;
    }
}

void json_builder_end_array(void *builder_ptr) {
    json_builder_t *builder = (json_builder_t *)builder_ptr;
    if (builder && builder->stack_depth > 0) {
        builder->current = builder->parent_stack[--builder->stack_depth];
    }
}

char *json_builder_get_string(void *builder_ptr) {
    json_builder_t *builder = (json_builder_t *)builder_ptr;
    char *result = NULL;
    
    if (builder) {
        /* Reset to root before getting string */
        builder->current = builder->root;
        builder->stack_depth = 0;
        
        result = json_dumps(builder->root, 0);
    }
    
    return result;
}

void json_builder_free(void *builder_ptr) {
    json_builder_t *builder = (json_builder_t *)builder_ptr;
    if (builder) {
        json_decref(builder->root);
        free(builder);
    }
}

/* Helper functions */

static size_t curl_write_callback(void *contents, size_t size, size_t nmemb, void *userp) {
    size_t realsize = size * nmemb;
    struct memory_buffer *mem = (struct memory_buffer *)userp;
    char *ptr;
    
    /* Reallocate memory */
    ptr = realloc(mem->data, mem->size + realsize + 1);
    if (!ptr) {
        return 0;  /* Out of memory */
    }
    
    mem->data = ptr;
    memcpy(&(mem->data[mem->size]), contents, realsize);
    mem->size += realsize;
    mem->data[mem->size] = 0;  /* Null-terminate */
    
    return realsize;
}

static void lock_client(mcp_client_t *client) {
    if (client) {
        #ifdef _WIN32
        EnterCriticalSection(&client->mutex);
        #else
        pthread_mutex_lock(&client->mutex);
        #endif
    }
}

static void unlock_client(mcp_client_t *client) {
    if (client) {
        #ifdef _WIN32
        LeaveCriticalSection(&client->mutex);
        #else
        pthread_mutex_unlock(&client->mutex);
        #endif
    }
}

static void check_curl_error(mcp_client_t *client, CURLcode res, const char *operation) {
    if (client && client->verbose && res != CURLE_OK) {
        fprintf(stderr, "CURL error during %s: %s\n", operation, curl_easy_strerror(res));
    }
}

static char *append_path_to_url(const char *base_url, const char *path) {
    char *url;
    size_t base_len = strlen(base_url);
    size_t path_len = strlen(path);
    size_t need_slash = (base_url[base_len - 1] != '/' && path[0] != '/') ? 1 : 0;
    size_t tool_path_len = sizeof("/mcp/tools/") - 1;
    
    /* Allocate memory for the URL */
    url = malloc(base_len + need_slash + tool_path_len + path_len + 1);
    if (!url) {
        return NULL;
    }
    
    /* Copy base URL */
    strcpy(url, base_url);
    
    /* Add slash if needed */
    if (need_slash) {
        url[base_len] = '/';
        url[base_len + 1] = '\0';
    }
    
    /* Check if path already includes /mcp/tools/ */
    if (strncmp(path, "/mcp/tools/", tool_path_len) == 0 ||
        strncmp(path, "mcp/tools/", tool_path_len - 1) == 0) {
        /* Path already includes the prefix */
        strcat(url, path);
    } else {
        /* Add /mcp/tools/ prefix */
        strcat(url, "/mcp/tools/");
        strcat(url, path);
    }
    
    return url;
} 