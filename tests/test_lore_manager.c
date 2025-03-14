/**
 * test_lore_manager.c
 * Tests for the lore manager module.
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <assert.h>

#include "../src/mcp/lore/lore_manager.h"

/**
 * Test the cache functionality
 */
static void
test_lore_cache(void)
{
    printf("Testing lore cache...\n");
    
    lore_manager_t *manager = init_lore_manager("memory-bank");
    assert(manager != NULL);
    
    /* Request the same character lore multiple times to test cache */
    lore_data_t *lore1 = get_character_lore(manager, "Gandalf", "third_age");
    
    /* First request should be a cache miss */
    assert(manager->cache_misses == 1);
    assert(manager->cache_hits == 0);
    
    /* If the lore was found, validate it */
    if (lore1 != NULL) {
        assert(lore1->content != NULL);
        assert(lore1->source != NULL);
        assert(lore1->age != NULL);
        assert(strcmp(lore1->age, "third_age") == 0);
        
        /* Request the same lore again to test cache hit */
        lore_data_t *lore2 = get_character_lore(manager, "Gandalf", "third_age");
        
        /* Should be a cache hit */
        assert(manager->cache_hits == 1);
        assert(manager->cache_misses == 1);
        
        /* Both lore pointers should be the same, since the second request returns
         * the cached data */
        assert(lore1 == lore2);
        
        /* Clean up */
        free_lore_data(lore1);
        /* Don't free lore2, it's the same pointer as lore1 */
    }
    
    free_lore_manager(manager);
    printf("Lore cache test passed\n");
}

/**
 * Test character lore functionality
 */
static void
test_character_lore(void)
{
    printf("Testing character lore retrieval...\n");
    
    lore_manager_t *manager = init_lore_manager("memory-bank");
    assert(manager != NULL);
    
    /* Test retrieving character lore for characters from different ages */
    lore_data_t *gandalf = get_character_lore(manager, "Gandalf", "third_age");
    lore_data_t *feanor = get_character_lore(manager, "Feanor", "first_age");
    
    /* Validate if lore was found */
    if (gandalf != NULL) {
        assert(gandalf->content != NULL);
        assert(gandalf->source != NULL);
        assert(strcmp(gandalf->age, "third_age") == 0);
        free_lore_data(gandalf);
    }
    
    if (feanor != NULL) {
        assert(feanor->content != NULL);
        assert(feanor->source != NULL);
        assert(strcmp(feanor->age, "first_age") == 0);
        free_lore_data(feanor);
    }
    
    /* Test retrieving lore for a non-existent character */
    lore_data_t *nonexistent = get_character_lore(manager, "NonExistentCharacter", "third_age");
    assert(nonexistent == NULL);
    
    free_lore_manager(manager);
    printf("Character lore test passed\n");
}

/**
 * Test location lore functionality
 */
static void
test_location_lore(void)
{
    printf("Testing location lore retrieval...\n");
    
    lore_manager_t *manager = init_lore_manager("memory-bank");
    assert(manager != NULL);
    
    /* Test retrieving location lore for locations from different ages */
    lore_data_t *minas_tirith = get_location_lore(manager, "Minas Tirith", "third_age");
    lore_data_t *gondolin = get_location_lore(manager, "Gondolin", "first_age");
    
    /* Validate if lore was found */
    if (minas_tirith != NULL) {
        assert(minas_tirith->content != NULL);
        assert(minas_tirith->source != NULL);
        assert(strcmp(minas_tirith->age, "third_age") == 0);
        free_lore_data(minas_tirith);
    }
    
    if (gondolin != NULL) {
        assert(gondolin->content != NULL);
        assert(gondolin->source != NULL);
        assert(strcmp(gondolin->age, "first_age") == 0);
        free_lore_data(gondolin);
    }
    
    free_lore_manager(manager);
    printf("Location lore test passed\n");
}

/**
 * Test companion lore functionality
 */
static void
test_companion_lore(void)
{
    printf("Testing companion lore retrieval...\n");
    
    lore_manager_t *manager = init_lore_manager("memory-bank");
    assert(manager != NULL);
    
    /* Test retrieving lore for a companion */
    lore_data_t *companion_lore = get_companion_lore(manager, "Aragorn", "third_age");
    
    /* Validate if lore was found */
    if (companion_lore != NULL) {
        assert(companion_lore->content != NULL);
        assert(companion_lore->source != NULL);
        free_lore_data(companion_lore);
    }
    
    free_lore_manager(manager);
    printf("Companion lore test passed\n");
}

/**
 * Main test function
 */
int
main(void)
{
    printf("Running lore manager tests...\n");
    
    test_lore_cache();
    test_character_lore();
    test_location_lore();
    test_companion_lore();
    
    printf("All lore manager tests passed!\n");
    return 0;
} 