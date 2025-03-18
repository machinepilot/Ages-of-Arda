---
title: Documentation Standards
id: documentation-rules
section: development
category: guides
created: '2025-03-18'
updated: '2025-03-18'
version: 0.1.0
auto_generated: true
cursor_rules:
  - documentation-rules.mdc
tags:
  - cursor-rule
  - guides
---

# Documentation Standards

## Core Principles
- Every significant component must be documented
- Documentation lives in `docs/_source` directory
- Code comments reference documentation by ID
- Use standardized format with proper frontmatter

## Document Structure

### Required Frontmatter
```yaml
---
title: "Document Title"
id: "unique-document-identifier"
section: "development|gameplay"
category: "guides|architecture|reference"
created: "YYYY-MM-DD"
updated: "YYYY-MM-DD"
version: "MAJOR.MINOR.PATCH"
---
```

### Optional Frontmatter
```yaml
contributors: ["developer1", "developer2"]
tags: ["tag1", "tag2"]
related: ["related-doc-id1", "related-doc-id2"]
cursor_rule: true  # If this should become a cursor rule
github_doc: true   # If this should be published as a GitHub doc
publish_to: ["wiki", "github"]  # Output targets
```

## Implementation Pattern

### Documentation References in Code
```c
/**
 * Function description
 * 
 * @see docs:dev-gameplay-movement
 */
void player_movement_handler(player_t *player, movement_type_t move_type)
{
    // Implementation
}
```

### History Tracking
Always maintain a history section at the end of your document:

```markdown
## History
- **2023-12-01**: Updated section X with clarification on Y
- **2023-10-15**: Initial document creation
```

## Build Process

Documentation is automatically processed by our build system:
1. Changes in source files trigger documentation rebuild
2. Documentation is compiled to multiple formats
3. Output is generated for wiki, cursor rules, and GitHub 