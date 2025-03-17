/**
 * \file test-companion-ui.c
 * \brief Test for companion UI system
 *
 * This file contains tests for the companion UI system.
 */

#include "angband.h"
#include "ui-term.h"
#include "ui-companion.h"
#include "ui-display.h"
#include "unit-test.h"

/**
 * Test companion data initialization
 */
static int test_companion_init(void *state)
{
    struct companion_data companion;
    
    /* Initialize with defaults */
    memset(&companion, 0, sizeof(companion));
    strcpy(companion.name, "Lute the Bard");
    companion.hp_current = 80;
    companion.hp_max = 100;
    strcpy(companion.status, "Healthy");
    companion.relationship_level = RELATIONSHIP_FRIENDLY;
    
    /* Verify initialization */
    require(strcmp(companion.name, "Lute the Bard") == 0);
    require(companion.hp_current == 80);
    require(companion.hp_max == 100);
    require(strcmp(companion.status, "Healthy") == 0);
    require(companion.relationship_level == RELATIONSHIP_FRIENDLY);
    
    ok;
}

/**
 * Test dialogue management
 */
static int test_companion_dialogue(void *state)
{
    struct companion_data companion;
    int i;
    
    /* Initialize */
    memset(&companion, 0, sizeof(companion));
    strcpy(companion.name, "Lute the Bard");
    
    /* Clear dialogue history */
    for (i = 0; i < COMPANION_HISTORY_SIZE; i++) {
        companion.dialogue[i][0] = '\0';
        companion.thoughts[i][0] = '\0';
    }
    
    /* Add dialogue */
    companion_add_dialogue(&companion, "Test dialogue 1", false);
    companion_add_dialogue(&companion, "Test dialogue 2", false);
    
    /* Add thoughts */
    companion_add_dialogue(&companion, "Test thought 1", true);
    companion_add_dialogue(&companion, "Test thought 2", true);
    
    /* Verify dialogue */
    require(strcmp(companion.dialogue[0], "Test dialogue 2") == 0);
    require(strcmp(companion.dialogue[1], "Test dialogue 1") == 0);
    
    /* Verify thoughts */
    require(strcmp(companion.thoughts[0], "Test thought 2") == 0);
    require(strcmp(companion.thoughts[1], "Test thought 1") == 0);
    
    /* Test shifting */
    for (i = 0; i < COMPANION_HISTORY_SIZE + 2; i++) {
        char buf[100];
        sprintf(buf, "Dialogue %d", i + 3);
        companion_add_dialogue(&companion, buf, false);
    }
    
    /* Verify older entries are pushed out */
    require(strcmp(companion.dialogue[0], "Dialogue 7") == 0);
    require(companion.dialogue[COMPANION_HISTORY_SIZE - 1][0] != '\0');
    
    ok;
}

/**
 * Test relationship system
 */
static int test_companion_relationship(void *state)
{
    struct companion_data companion;
    
    /* Initialize */
    memset(&companion, 0, sizeof(companion));
    strcpy(companion.name, "Lute the Bard");
    companion.relationship_level = RELATIONSHIP_NEUTRAL;
    
    /* Test relationship name mapping */
    const char *rel_names[] = {
        "Hostile", "Wary", "Neutral", "Friendly", "Loyal"
    };
    
    /* Verify level names */
    require(strcmp(rel_names[RELATIONSHIP_HOSTILE], "Hostile") == 0);
    require(strcmp(rel_names[RELATIONSHIP_WARY], "Wary") == 0);
    require(strcmp(rel_names[RELATIONSHIP_NEUTRAL], "Neutral") == 0);
    require(strcmp(rel_names[RELATIONSHIP_FRIENDLY], "Friendly") == 0);
    require(strcmp(rel_names[RELATIONSHIP_LOYAL], "Loyal") == 0);
    
    /* Verify initial state */
    require(companion.relationship_level == RELATIONSHIP_NEUTRAL);
    
    /* Change relationship */
    companion.relationship_level = RELATIONSHIP_FRIENDLY;
    require(companion.relationship_level == RELATIONSHIP_FRIENDLY);
    
    ok;
}

/**
 * Test the companion window flag
 */
static int test_companion_window_flag(void *state)
{
    u32b old_flag;
    
    /* Save current window flag for window 2 */
    old_flag = window_flag[2];
    
    /* Set the companion flag for window 2 */
    window_flag[2] |= PW_COMPANION;
    
    /* Verify flag is set */
    require((window_flag[2] & PW_COMPANION) != 0);
    
    /* Check that the window_flag_desc for companion is set */
    require(window_flag_desc[PW_COMPANION] != NULL);
    require(strcmp(window_flag_desc[PW_COMPANION], "Display companion information") == 0);
    
    /* Restore original flag */
    window_flag[2] = old_flag;
    
    ok;
}

/**
 * Run all companion UI tests
 */
int run_companion_ui_tests(void)
{
    const char *test_name = "companion-ui";
    int verbose = 0;
    
    suite_start(test_name, verbose);
    
    /* Core functionality tests */
    suite_add_test(test_companion_init, "companion-init");
    suite_add_test(test_companion_dialogue, "companion-dialogue");
    suite_add_test(test_companion_relationship, "companion-relationship");
    suite_add_test(test_companion_window_flag, "companion-window-flag");
    
    return suite_finish();
} 