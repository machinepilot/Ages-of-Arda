/**
 * Improved event capture system for Brogue CE
 * 
 * Uses pointer redirection instead of function hooks for better stability
 */
void initialize_brogue_mcp_hooks(void) {
    // Register memory-safe event listeners
    register_game_event_handler(EVENT_MONSTER_KILLED, &handle_monster_event, EVENT_PRIORITY_HIGH);
    register_game_event_handler(EVENT_ITEM_DISCOVERED, &handle_item_event, EVENT_PRIORITY_MEDIUM);
    
    // Save original function pointers for fallback
    original_display_message = brogue.display_message;
    brogue.display_message = mcp_enhanced_display_message;
    
    // ... existing code ...
} 