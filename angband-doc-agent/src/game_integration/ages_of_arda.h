/**
 * ages_of_arda.h
 * 
 * Header file for the Ages of Arda companion system integration with the Angband game.
 */

#ifndef INCLUDED_AGES_OF_ARDA_H
#define INCLUDED_AGES_OF_ARDA_H

#include "angband.h"

/**
 * Initialize the Ages of Arda integration.
 * 
 * This function initializes the Ages of Arda integration by registering
 * event handlers and retrieving the current timeline information.
 * 
 * @return true if initialization was successful, false otherwise
 */
bool ages_of_arda_init(void);

/**
 * Clean up the Ages of Arda integration.
 * 
 * This function cleans up the Ages of Arda integration by unregistering
 * event handlers.
 */
void ages_of_arda_cleanup(void);

/**
 * Generate dialogue for the current companion.
 * 
 * This function generates dialogue for the current companion based on the
 * specified prompt type and the current game context.
 * 
 * @param prompt_type The type of dialogue to generate (e.g., "greeting", "combat", "discovery")
 * @return true if dialogue was generated successfully, false otherwise
 */
bool ages_generate_dialogue(const char *prompt_type);

/**
 * Update the relationship level with the current companion.
 * 
 * This function updates the relationship level with the current companion
 * based on the specified change.
 * 
 * @param change The amount to change the relationship level by
 * @return true if the update was successful, false otherwise
 */
bool ages_update_relationship(int change);

/**
 * Handle player death.
 * 
 * This function handles player death by advancing the timeline and
 * updating the current companion.
 * 
 * @return true if the timeline was advanced successfully, false otherwise
 */
bool ages_handle_player_death(void);

/**
 * Get the current companion name.
 * 
 * @return The current companion name
 */
const char *ages_get_current_companion(void);

/**
 * Get the current age and year.
 * 
 * @param age Pointer to store the current age
 * @param year Pointer to store the current year
 */
void ages_get_current_age_and_year(const char **age, int *year);

/**
 * Get the current relationship level.
 * 
 * @return The current relationship level
 */
int ages_get_relationship_level(void);

#endif /* INCLUDED_AGES_OF_ARDA_H */ 