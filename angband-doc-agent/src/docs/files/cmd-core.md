# cmd-core.c

## File Overview

This file is located at `src/cmd-core.c` in the Angband codebase.

## Error Generating Documentation

An error occurred while generating documentation: Error code: 429 - {'type': 'error', 'error': {'type': 'rate_limit_error', 'message': 'This request would exceed the rate limit for your organization (ca0567f9-a66c-44e9-8bd6-dfea5ad83443) of 2,000 output tokens per minute. For details, refer to: https://docs.anthropic.com/en/api/rate-limits. You can see the response headers for current usage. Please reduce the prompt length or the maximum tokens requested, or try again later. You may also contact sales at https://www.anthropic.com/contact-sales to discuss your options for a rate limit increase.'}}

## Raw File Content

```c
/**
 * \file cmd-core.c
 * \brief Handles the queueing of game commands.
 *
 * Copyright (c) 2008-9 Antony Sidwell
 * Copyright (c) 2014 Andi Sidwell
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
#include "cmds.h"
#include "cmd-core.h"
#include "effects-info.h"
#include "game-input.h"
#include "game-world.h"
#include "obj-chest.h"
#include "obj-desc.h"
#include "obj-tval.h"
#include "obj-util.h"
#include "player-attack.h"
#include "player-birth.h"
#include "player-calcs.h"
#include "player-spell.h"
#include "pla
...
```

*Note: File content truncated for brevity.*
