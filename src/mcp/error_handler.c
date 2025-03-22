/**
 * Comprehensive error handling system for MCP integration
 */
typedef enum {
    ERROR_NETWORK,
    ERROR_TIMEOUT,
    ERROR_SERVER,
    ERROR_PARSING,
    ERROR_MEMORY
} error_type_t;

/**
 * Gracefully handle MCP failures with tiered fallback
 */
void handle_mcp_error(error_type_t error_type, const char* message) {
    // Log error with context
    log_error("[MCP ERROR] Type: %d, Message: %s", error_type, message);
    
    // Engage appropriate fallback mechanism
    switch (error_type) {
        case ERROR_NETWORK:
        case ERROR_TIMEOUT:
            // Network issues - switch to offline mode
            activate_offline_mode();
            break;
            
        case ERROR_SERVER:
            // Server error - retry with exponential backoff
            schedule_retry_with_backoff();
            break;
            
        case ERROR_PARSING:
        case ERROR_MEMORY:
            // Critical errors - use template fallbacks
            use_template_responses();
            break;
    }
    
    // Notify player with appropriate non-breaking message
    display_system_message("The dungeon's magic flickers momentarily...");
} 