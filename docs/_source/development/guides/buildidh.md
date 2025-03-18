---
title: buildid.h
id: buildidh
section: development
category: guides
created: '2025-03-14'
updated: '2025-03-13'
version: 0.1.0
---


# buildid.h

## File Overview

This file is located at `src/buildid.h` in the Angband codebase.

## Error Generating Documentation

An error occurred while generating documentation: Error code: 429 - {'type': 'error', 'error': {'type': 'rate_limit_error', 'message': 'This request would exceed the rate limit for your organization (ca0567f9-a66c-44e9-8bd6-dfea5ad83443) of 10,000 input tokens per minute. For details, refer to: https://docs.anthropic.com/en/api/rate-limits. You can see the response headers for current usage. Please reduce the prompt length or the maximum tokens requested, or try again later. You may also contact sales at https://www.anthropic.com/contact-sales to discuss your options for a rate limit increase.'}}

## Raw File Content

```c
/**
 * \file buildid.h
 * \brief Compile in build details
 *
 * Copyright (c) 2011 Andi Sidwell
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

#ifndef BUILDID
#define BUILDID

#define VERSION_NAME	"Angband"

extern const char *buildid;
extern const char *buildver;
extern const char *copyright;

#endif /* BUILDID */

...
```

*Note: File content truncated for brevity.*
