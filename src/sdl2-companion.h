/**
 * \file sdl2-companion.h
 * \brief Integration helper for companion UI with SDL2
 *
 * This file contains modifications to be applied to main-sdl2.c to support
 * the companion UI feature.
 */

/* 
 * Add the following to the subwindow struct:
 * 
 * struct companion_data *companion;
 *
 * Add the following forward declarations:
 *
 * extern errr companion_init(struct subwindow *subwindow);
 * extern void companion_free(struct companion_data *companion);
 * extern void render_companion_window(struct subwindow *subwindow);
 *
 * In load_term function, add:
 *
 * if (subwindow->index == 2 && !subwindow->companion) {
 *     companion_init(subwindow);
 * }
 *
 * In free_subwindow function, add:
 *
 * if (subwindow->companion) {
 *     companion_free(subwindow->companion);
 *     subwindow->companion = NULL;
 * }
 *
 * In render_all function, look for any place that renders subwindow content
 * and add this check:
 *
 * if (subwindow->term->sidebar_mode & PW_COMPANION && subwindow->companion) {
 *     render_companion_window(subwindow);
 *     continue;
 * }
 */ 