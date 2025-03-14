/**
 * @file test-bard.c
 * @brief Test program for the Bard module
 *
 * This program tests the Bard module by triggering various narrative
 * events and displaying the generated narratives.
 */

#include "bard.h"
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
 * Helper function to display narratives from the queue
 */
void display_narratives() {
    char narrative[1024];
    bool is_spoken;
    int importance;
    
    printf("\n--- Displaying Narratives ---\n");
    while (bard_get_next_narrative(narrative, sizeof(narrative), &is_spoken, &importance)) {
        if (is_spoken) {
            printf("Lute says: \"%s\"\n", narrative);
        } else {
            printf("%s\n", narrative);
        }
        printf("(Importance: %d)\n\n", importance);
    }
}

/**
 * Helper function to process pending narratives
 */
void process_pending() {
    printf("\n--- Processing Pending Narratives ---\n");
    for (int i = 0; i < 10; i++) {
        int processed = bard_process_pending();
        if (processed > 0) {
            printf("Processed %d narrative(s)\n", processed);
            break;
        }
        printf("Waiting for narratives... (%d/10)\n", i + 1);
        sleep(1);
    }
}

/**
 * Main function
 */
int main(int argc, char *argv[]) {
    const char *server_url = argc > 1 ? argv[1] : "http://localhost:3000";
    const char *character_id = argc > 2 ? argv[2] : "test-character-bard";
    
    printf("Testing Bard module with server URL: %s\n", server_url);
    
    // Enable debug mode
    bard_set_debug(true);
    
    // Initialize the Bard system
    if (!bard_init(server_url, NULL, character_id)) {
        fprintf(stderr, "Failed to initialize Bard system\n");
        return 1;
    }
    
    // Configure Bard
    bard_configure(80, 70, "fantasy");
    
    // Set player info
    bard_update_player_info("Frodo", "Hobbit", "Burglar", 10);
    
    // Test various narrative events
    printf("\n=== Testing Monster Death Narrative ===\n");
    bard_narrate_monster_death("Shelob", 30, true, "dramatic", "tense");
    process_pending();
    display_narratives();
    
    printf("\n=== Testing Item Discovery Narrative ===\n");
    bard_narrate_item_discovery("Sting", true, "sword", "poetic", "mystical");
    process_pending();
    display_narratives();
    
    printf("\n=== Testing New Level Narrative ===\n");
    bard_narrate_new_level(20, "sinister", "dark", "foreboding");
    process_pending();
    display_narratives();
    
    printf("\n=== Testing Near Death Narrative ===\n");
    bard_narrate_near_death(5, "Balrog", "dramatic", "desperate");
    process_pending();
    display_narratives();
    
    printf("\n=== Testing Quest Complete Narrative ===\n");
    bard_narrate_quest_complete("Destroy the Ring", 50, "epic", "triumphant");
    process_pending();
    display_narratives();
    
    printf("\n=== Testing Level Up Narrative ===\n");
    bard_narrate_level_up(11, "Burglar", "celebratory", "proud");
    process_pending();
    display_narratives();
    
    // Clean up
    bard_shutdown();
    
    printf("\nAll tests completed\n");
    return 0;
} 