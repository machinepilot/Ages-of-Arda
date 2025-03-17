/**
 * \file ui-companion.h
 * \brief Companion UI for AI-driven NPCs
 *
 * Copyright (c) 2023 The Ages of Arda Team
 *
 * This work is free software; you can redistribute it and/or modify it
 * under the terms of either:
 *
 * a) the GNU General Public License as published by the Free Software
 *    Foundation, version 2, or
 *
 * b) the "Angband licence":
 *    This software may be copied and distributed for educational, research,
 *    and not for profit purposes provided that this copyright and statement
 *    are included in all such copies.  Other copyrights may also apply.
 */

#ifndef INCLUDED_UI_COMPANION_H
#define INCLUDED_UI_COMPANION_H

#include "angband.h"

/**
 * Add companion display to subwindow flags
 */
#define PW_COMPANION    0x80000000 /* Display companion information */

/**
 * Maximum lengths for dialogue and thoughts
 */
#define COMPANION_TEXT_LEN 256
#define COMPANION_HISTORY_SIZE 5

/**
 * Companion relationship levels
 */
enum companion_relationship {
    RELATIONSHIP_HOSTILE = 0,
    RELATIONSHIP_WARY = 1,
    RELATIONSHIP_NEUTRAL = 2,
    RELATIONSHIP_FRIENDLY = 3,
    RELATIONSHIP_LOYAL = 4
};

/**
 * Companion data structure
 */
struct companion_data {
    char name[64];
    int hp_current;
    int hp_max;
    char status[32];
    int relationship_level;
    
    /* Dialogue and thoughts history */
    char dialogue[COMPANION_HISTORY_SIZE][COMPANION_TEXT_LEN];
    char thoughts[COMPANION_HISTORY_SIZE][COMPANION_TEXT_LEN];
    
    /* Portrait information */
    void *portrait;     /* SDL_Texture* - Avoid SDL dependency in header */
    SDL_Rect portrait_rect;
    
    /* Last MCP request time for throttling */
    Uint32 last_request_time;
    
    /* State tracking */
    bool needs_update;
};

/**
 * Initialize companion for a subwindow
 */
errr companion_init(struct subwindow *subwindow);

/**
 * Free companion resources
 */
void companion_free(struct companion_data *companion);

/**
 * Verify the companion window flag is properly initialized
 */
bool check_companion_window_flag(void);

/**
 * Update companion statistics from MCP
 */
bool companion_update_stats(struct companion_data *companion);

/**
 * Add dialogue and update display
 */
void companion_add_dialogue(struct companion_data *companion, 
                          const char *text, bool is_thought);

/**
 * Request dialogue from MCP server
 */
bool companion_mcp_request_dialogue(struct companion_data *companion, 
                                  const char *topic);

/**
 * Mark companion for redraw
 */
void companion_mark_for_redraw(struct companion_data *companion);

/**
 * Get companion name
 */
const char *companion_get_name(struct companion_data *companion);

/**
 * Process game events for companion reactions
 */
void companion_event_handler(game_event_type type, game_event_data *data, void *user);

/**
 * Render companion window
 */
void render_companion_window(struct subwindow *subwindow);

#endif /* INCLUDED_UI_COMPANION_H */ 