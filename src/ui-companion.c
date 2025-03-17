/**
 * \file ui-companion.c
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

#include "angband.h"
#include "init.h"
#include "ui-term.h"
#include "ui-companion.h"
#include "game-event.h"
#include "SDL.h"
#include "SDL_image.h"

/* MCP integration */
#include "mcp-client.h"

/**
 * Constants for MCP integration
 */
#define AGES_COMPANION_DIALOGUE_ENDPOINT "ages/companion/dialogue"
#define AGES_COMPANION_INFO_ENDPOINT "ages/companion/info"
#define MCP_REQUEST_INTERVAL 500 /* Minimum time between MCP requests in ms */

/* Current game age - would normally come from game state */
static char current_age[32] = "First Age";

/**
 * Relationship level names
 */
static const char *relationship_names[] = {
    "Hostile",
    "Wary",
    "Neutral",
    "Friendly",
    "Loyal"
};

/**
 * Fallback dialogue templates for offline mode
 */
static const char *fallback_dialogue[] = {
    "We should be careful here. I sense danger ahead.",
    "This reminds me of tales from the elder days.",
    "We should rest soon. The journey has been long.",
    "I wonder what treasures lie hidden in these depths?",
    "Stay alert! These halls have an ancient malice to them."
};

/**
 * Fallback thoughts templates for offline mode
 */
static const char *fallback_thoughts[] = {
    "I don't trust this place, but I cannot show my fear.",
    "I hope we find what we seek before something finds us.",
    "The weight of ages presses down in these halls.",
    "I should compose a song about this adventure... if we survive.",
    "There's something familiar about this place..."
};

/**
 * Verify companion window flag is properly initialized
 * Used to ensure the window flag descriptor is set correctly
 */
bool check_companion_window_flag(void)
{
    /* Verify the companion window flag description is set */
    if (window_flag_desc[PW_COMPANION] == NULL) {
        /* Error - the window flag description wasn't set properly */
        return false;
    }
    
    /* Verify the description matches expected text */
    if (strcmp(window_flag_desc[PW_COMPANION], "Display companion information") != 0) {
        /* Error - wrong description */
        return false;
    }
    
    /* All checks passed */
    return true;
}

/**
 * Initialize companion for a subwindow
 */
errr companion_init(struct subwindow *subwindow)
{
    if (!subwindow) {
        return -1;
    }
    
    /* Ensure companion window flag is properly set */
    if (!check_companion_window_flag()) {
        /* Set the window flag description if it's not already set */
        if (window_flag_desc[PW_COMPANION] == NULL) {
            window_flag_desc[PW_COMPANION] = "Display companion information";
        }
    }

    /* Allocate companion data if not already allocated */
    if (!subwindow->companion) {
        subwindow->companion = mem_zalloc(sizeof(struct companion_data));
        if (!subwindow->companion) {
            return -1;
        }
    }

    /* Initialize companion data */
    struct companion_data *companion = subwindow->companion;
    memset(companion, 0, sizeof(struct companion_data));
    
    /* Set default values */
    strcpy(companion->name, "Lute the Bard");
    companion->hp_current = 80;
    companion->hp_max = 100;
    strcpy(companion->status, "Healthy");
    companion->relationship_level = RELATIONSHIP_FRIENDLY;
    companion->needs_update = true;
    companion->last_request_time = 0;
    
    /* Clear dialogue history */
    for (int i = 0; i < COMPANION_HISTORY_SIZE; i++) {
        companion->dialogue[i][0] = '\0';
        companion->thoughts[i][0] = '\0';
    }
    
    /* Load portrait */
    char portrait_path[1024];
    path_build(portrait_path, sizeof(portrait_path), ANGBAND_DIR_ICONS, "lute-portrait.png");
    
    /* We'll handle the actual loading in the SDL rendering context later */
    companion->portrait = NULL;
    
    /* Attach to subwindow */
    subwindow->companion = companion;
    
    /* Set window flag */
    subwindow->term->sidebar_mode |= PW_COMPANION;
    
    /* Add initial dialogue */
    companion_add_dialogue(companion, "Hello, adventurer! I'm ready to accompany you.", false);
    companion_add_dialogue(companion, "I wonder what we'll find in these lands...", true);
    
    /* Register for game events */
    event_add_handler(EVENT_ENTER_DUNGEON, companion_event_handler, NULL);
    event_add_handler(EVENT_MONSTER_DEATH, companion_event_handler, NULL);
    event_add_handler(EVENT_LEAVE_LEVEL, companion_event_handler, NULL);
    event_add_handler(EVENT_INVENTORY_CHANGE, companion_event_handler, NULL);
    
    return 0;
}

/**
 * Free companion resources
 */
void companion_free(struct companion_data *companion)
{
    if (!companion)
        return;
    
    /* Free SDL texture if it exists */
    if (companion->portrait) {
        SDL_DestroyTexture((SDL_Texture *)companion->portrait);
        companion->portrait = NULL;
    }
    
    /* Free companion data */
    mem_free(companion);
}

/**
 * Mark companion for redraw
 */
void companion_mark_for_redraw(struct companion_data *companion)
{
    if (!companion)
        return;
    
    companion->needs_update = true;
    
    /* Mark Term for update */
    Term_mark(0, 0);
}

/**
 * Get companion name
 */
const char *companion_get_name(struct companion_data *companion)
{
    if (!companion)
        return "Unknown";
    
    return companion->name;
}

/**
 * Add dialogue and update display
 */
void companion_add_dialogue(struct companion_data *companion, const char *text, bool is_thought)
{
    int i;
    
    if (!companion || !text)
        return;
    
    /* Shift existing dialogue/thoughts up */
    for (i = COMPANION_HISTORY_SIZE - 1; i > 0; i--) {
        if (is_thought)
            strcpy(companion->thoughts[i], companion->thoughts[i-1]);
        else
            strcpy(companion->dialogue[i], companion->dialogue[i-1]);
    }
    
    /* Add new text */
    if (is_thought)
        my_strcpy(companion->thoughts[0], text, COMPANION_TEXT_LEN);
    else
        my_strcpy(companion->dialogue[0], text, COMPANION_TEXT_LEN);
    
    /* Mark for redraw */
    companion_mark_for_redraw(companion);
}

/**
 * Get fallback template response when MCP is unavailable
 */
static char *companion_get_template_response(struct companion_data *companion, const char *topic)
{
    int index;
    static char response[COMPANION_TEXT_LEN];
    
    /* Choose a random template based on topic and companion */
    index = randint0(5);
    
    /* Copy appropriate fallback text */
    my_strcpy(response, fallback_dialogue[index], COMPANION_TEXT_LEN);
    
    return response;
}

/**
 * Update companion statistics from MCP
 */
bool companion_update_stats(struct companion_data *companion)
{
    char request[256];
    mcp_response_t *response;
    bool success = false;
    
    if (!companion)
        return false;
    
    /* Throttle MCP requests */
    if (SDL_GetTicks() - companion->last_request_time < MCP_REQUEST_INTERVAL)
        return false;
    
    companion->last_request_time = SDL_GetTicks();
    
    /* Build the request */
    sprintf(request, "{"
                    "\"companion_name\": \"%s\","
                    "\"age\": \"%s\""
                    "}",
            companion->name, current_age);
    
    /* Call the MCP server */
    response = mcp_client_call(AGES_COMPANION_INFO_ENDPOINT, request);
    if (!response) {
        /* Fallback: slight random variation */
        companion->hp_current = companion->hp_current + randint0(5) - 2;
        companion->hp_current = MIN(companion->hp_max, MAX(1, companion->hp_current));
        return false;
    }
    
    /* Parse the response */
    if (mcp_response_get_int(response, "hp_current", &companion->hp_current) &&
        mcp_response_get_int(response, "hp_max", &companion->hp_max) &&
        mcp_response_get_string(response, "status", companion->status, sizeof(companion->status)) &&
        mcp_response_get_int(response, "relationship_level", &companion->relationship_level)) {
        
        success = true;
    }
    
    /* Free response */
    mcp_response_free(response);
    
    /* Mark for redraw */
    if (success)
        companion_mark_for_redraw(companion);
    
    return success;
}

/**
 * Request dialogue from MCP server
 */
bool companion_mcp_request_dialogue(struct companion_data *companion, const char *topic)
{
    char request[512];
    mcp_response_t *response;
    char dialogue[COMPANION_TEXT_LEN] = "";
    char thoughts[COMPANION_TEXT_LEN] = "";
    bool success = false;
    
    if (!companion || !topic)
        return false;
    
    /* Throttle MCP requests */
    if (SDL_GetTicks() - companion->last_request_time < MCP_REQUEST_INTERVAL)
        return false;
    
    companion->last_request_time = SDL_GetTicks();
    
    /* Build the request */
    sprintf(request, "{"
                    "\"companion_name\": \"%s\","
                    "\"age\": \"%s\","
                    "\"topic\": \"%s\","
                    "\"relationship_level\": %d"
                    "}",
            companion->name, current_age, topic, companion->relationship_level);
    
    /* Call the MCP server */
    response = mcp_client_call(AGES_COMPANION_DIALOGUE_ENDPOINT, request);
    if (!response) {
        /* Fallback to template response */
        char *template_response = companion_get_template_response(companion, topic);
        companion_add_dialogue(companion, template_response, false);
        
        /* Add a thought as well */
        int index = randint0(5);
        companion_add_dialogue(companion, fallback_thoughts[index], true);
        
        return false;
    }
    
    /* Parse the response */
    if (mcp_response_get_string(response, "dialogue", dialogue, sizeof(dialogue))) {
        companion_add_dialogue(companion, dialogue, false);
        success = true;
    }
    
    if (mcp_response_get_string(response, "thoughts", thoughts, sizeof(thoughts))) {
        companion_add_dialogue(companion, thoughts, true);
    }
    
    /* Free response */
    mcp_response_free(response);
    
    return success;
}

/**
 * Process game events for companion reactions
 */
void companion_event_handler(game_event_type type, game_event_data *data, void *user)
{
    term *old = Term;
    term *companion_term = angband_term[2]; /* Subwindow 2 */
    struct subwindow *subwindow;
    
    /* Ensure companion term exists */
    if (!companion_term || !companion_term->data)
        return;
    
    subwindow = companion_term->data;
    if (!subwindow->companion)
        return;
    
    /* Handle different events */
    switch (type) {
        case EVENT_ENTER_DUNGEON:
            companion_mcp_request_dialogue(subwindow->companion, "dungeon_enter");
            break;
            
        case EVENT_MONSTER_DEATH:
            if (data->monster_death.r_idx > 0 && one_in_(3)) {
                /* Only react to some monster deaths to avoid spamming */
                companion_mcp_request_dialogue(subwindow->companion, "monster_death");
            }
            break;
            
        case EVENT_LEAVE_LEVEL:
            companion_mcp_request_dialogue(subwindow->companion, "level_change");
            break;
            
        case EVENT_INVENTORY_CHANGE:
            if (one_in_(5)) {
                /* React occasionally to inventory changes */
                companion_mcp_request_dialogue(subwindow->companion, "item_found");
            }
            break;
            
        default:
            /* Ignore other events */
            break;
    }
    
    /* Restore term */
    Term_activate(old);
}

/**
 * Load companion portrait
 */
static void load_companion_portrait(struct companion_data *companion, struct subwindow *subwindow)
{
    char portrait_path[1024];
    SDL_Surface *surface;
    SDL_Texture *texture;
    
    if (!companion || !subwindow || companion->portrait)
        return;
    
    /* Build path to portrait image */
    path_build(portrait_path, sizeof(portrait_path), ANGBAND_DIR_ICONS, "lute-portrait.png");
    
    /* Load image */
    surface = IMG_Load(portrait_path);
    if (!surface) {
        /* Fallback to a default image */
        path_build(portrait_path, sizeof(portrait_path), ANGBAND_DIR_ICONS, "att-32.png");
        surface = IMG_Load(portrait_path);
        
        if (!surface)
            return;
    }
    
    /* Create texture */
    texture = SDL_CreateTextureFromSurface(subwindow->window->renderer, surface);
    SDL_FreeSurface(surface);
    
    if (!texture)
        return;
    
    /* Store texture */
    companion->portrait = texture;
}

/**
 * Render companion window
 */
void render_companion_window(struct subwindow *subwindow)
{
    struct companion_data *companion;
    SDL_Rect rect;
    SDL_Color text_color = {255, 255, 255, 255};
    SDL_Color title_color = {255, 220, 150, 255};
    SDL_Color header_color = {180, 180, 255, 255};
    int i;
    
    if (!subwindow || !subwindow->companion)
        return;
    
    companion = subwindow->companion;
    
    /* Only update if needed */
    if (!companion->needs_update)
        return;
    
    /* Clear the window */
    render_fill_rect(subwindow->window, subwindow->texture, 
            &subwindow->inner_rect, &subwindow->color);
    
    /* Render title */
    rect = subwindow->inner_rect;
    rect.h = subwindow->font_height;
    render_text(subwindow->window, subwindow->texture, subwindow->font,
            companion->name, &rect, &title_color, NULL);
    
    /* Ensure portrait is loaded */
    if (!companion->portrait)
        load_companion_portrait(companion, subwindow);
    
    /* Render portrait */
    rect.y += rect.h + 5;
    rect.h = subwindow->inner_rect.h * 0.25;
    rect.w = rect.h;
    companion->portrait_rect = rect;
    if (companion->portrait) {
        SDL_RenderCopy(subwindow->window->renderer, companion->portrait, NULL, &rect);
    } else {
        render_fill_rect(subwindow->window, subwindow->texture, &rect, &text_color);
    }
    
    /* Render stats */
    SDL_Rect stat_rect = {
        rect.x + rect.w + 10,
        rect.y,
        subwindow->inner_rect.w - rect.w - 20,
        subwindow->font_height
    };
    
    /* Relationship level */
    char relationship_text[100];
    sprintf(relationship_text, "Relationship: %s", 
            relationship_names[companion->relationship_level]);
    render_text(subwindow->window, subwindow->texture, subwindow->font,
            relationship_text, &stat_rect, &text_color, NULL);
    
    /* Health */
    stat_rect.y += subwindow->font_height + 5;
    char health_text[100];
    sprintf(health_text, "Health: %d/%d", companion->hp_current, companion->hp_max);
    render_text(subwindow->window, subwindow->texture, subwindow->font,
            health_text, &stat_rect, &text_color, NULL);
    
    /* Status */
    stat_rect.y += subwindow->font_height + 5;
    char status_text[100];
    sprintf(status_text, "Status: %s", companion->status);
    render_text(subwindow->window, subwindow->texture, subwindow->font,
            status_text, &stat_rect, &text_color, NULL);
    
    /* Dialogue section */
    rect.y = rect.y + rect.h + 10;
    rect.x = subwindow->inner_rect.x;
    rect.w = subwindow->inner_rect.w;
    rect.h = subwindow->font_height;
    render_text(subwindow->window, subwindow->texture, subwindow->font,
            "DIALOGUE:", &rect, &header_color, NULL);
    
    /* Render dialogue */
    rect.y += rect.h + 5;
    rect.h = subwindow->font_height;
    for (i = 0; i < COMPANION_HISTORY_SIZE && companion->dialogue[i][0] != '\0'; i++) {
        render_text(subwindow->window, subwindow->texture, subwindow->font,
                companion->dialogue[i], &rect, &text_color, NULL);
        rect.y += rect.h;
    }
    
    /* Thoughts section */
    rect.y += 10;
    rect.x = subwindow->inner_rect.x;
    rect.w = subwindow->inner_rect.w;
    rect.h = subwindow->font_height;
    render_text(subwindow->window, subwindow->texture, subwindow->font,
            "THOUGHTS:", &rect, &header_color, NULL);
    
    /* Render thoughts */
    rect.y += rect.h + 5;
    rect.h = subwindow->font_height;
    for (i = 0; i < COMPANION_HISTORY_SIZE && companion->thoughts[i][0] != '\0'; i++) {
        /* Italicize thoughts with * characters */
        char thought[COMPANION_TEXT_LEN + 2];
        sprintf(thought, "*%s*", companion->thoughts[i]);
        render_text(subwindow->window, subwindow->texture, subwindow->font,
                thought, &rect, &text_color, NULL);
        rect.y += rect.h;
    }
    
    /* Mark as updated */
    companion->needs_update = false;
    subwindow->window->dirty = true;
} 