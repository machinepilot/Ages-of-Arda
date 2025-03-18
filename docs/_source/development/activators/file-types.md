---
title: File Type Rule Mapping
id: file-types
section: development
category: activators
created: '2025-03-18'
updated: '2025-03-18'
version: 0.1.0
auto_generated: true
cursor_rules:
  - activators/file-types.mdc
tags:
  - cursor-rule
  - activators
---

# File Type Rule Mapping

This rule automatically applies the appropriate rule files based on file type and location. It serves as a central dispatch mechanism for the rule system.

## Source Code Files

| File Pattern | Applied Rules |
|--------------|---------------|
| `**/*.c` | code-style/c-style.mdc, game/memory-bank.mdc |
| `**/*.h` | code-style/c-style.mdc, game/memory-bank.mdc |
| `**/src/**/*.c` | game/angband-variant.mdc |
| `**/html/**/*.html` | code-style/html.mdc |
| `**/ai/**/*.c` | ai/ai-gameplay.mdc, ai/ai-ux.mdc |
| `**/mcp/**/*.c` | mcp/mcp-integration.mdc, mcp/mcp-server.mdc |

## Configuration Files

| File Pattern | Applied Rules |
|--------------|---------------|
| `netlify.toml` | infrastructure/netlify.mdc |
| `.github/**` | infrastructure/github-standards.mdc |
| `**/mcp/config.json` | mcp/mcp-server.mdc |

## Game Content Files

| File Pattern | Applied Rules |
|--------------|---------------|
| `**/lore/**` | game/lore-management.mdc |
| `**/npc/**` | ai/ai-gameplay.mdc |
| `**/gameplay/**` | game/angband-variant.mdc, ai/ai-gameplay.mdc |

## Usage

This file does not need to be explicitly referenced. It automatically runs at priority 950 to ensure all appropriate rules are applied based on the file types being edited.

Each mapping indicates:
1. The glob pattern to match file paths
2. The rule files that should be applied when working with these files

When multiple rules apply, they are loaded in order of priority from highest to lowest. 