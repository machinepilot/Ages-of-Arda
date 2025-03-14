/**
 * ages_of_arda_lore.h
 * 
 * Header file for the Ages of Arda lore system integration with the Angband game.
 */

#ifndef INCLUDED_AGES_OF_ARDA_LORE_H
#define INCLUDED_AGES_OF_ARDA_LORE_H

#include "angband.h"

/**
 * Generate lore dialogue for a character.
 * 
 * This function generates lore dialogue for a character based on the
 * current companion's knowledge.
 * 
 * @param character_name The name of the character to get lore for
 * @return true if dialogue was generated successfully, false otherwise
 */
bool ages_generate_character_lore(const char *character_name);

/**
 * Generate lore dialogue for a location.
 * 
 * This function generates lore dialogue for a location based on the
 * current companion's knowledge.
 * 
 * @param location_name The name of the location to get lore for
 * @return true if dialogue was generated successfully, false otherwise
 */
bool ages_generate_location_lore(const char *location_name);

/**
 * Generate lore dialogue for an artifact.
 * 
 * This function generates lore dialogue for an artifact based on the
 * current companion's knowledge.
 * 
 * @param artifact_name The name of the artifact to get lore for
 * @return true if dialogue was generated successfully, false otherwise
 */
bool ages_generate_artifact_lore(const char *artifact_name);

/**
 * Check if lore is available for a character.
 * 
 * This function checks if lore is available for a character.
 * 
 * @param character_name The name of the character to check
 * @return true if lore is available, false otherwise
 */
bool ages_has_character_lore(const char *character_name);

/**
 * Check if lore is available for a location.
 * 
 * This function checks if lore is available for a location.
 * 
 * @param location_name The name of the location to check
 * @return true if lore is available, false otherwise
 */
bool ages_has_location_lore(const char *location_name);

/**
 * Check if lore is available for an artifact.
 * 
 * This function checks if lore is available for an artifact.
 * 
 * @param artifact_name The name of the artifact to check
 * @return true if lore is available, false otherwise
 */
bool ages_has_artifact_lore(const char *artifact_name);

#endif /* INCLUDED_AGES_OF_ARDA_LORE_H */ 