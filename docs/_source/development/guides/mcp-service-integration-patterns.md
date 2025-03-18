---
title: MCP Service Integration Patterns
id: mcp-service-integration-patterns
section: development
category: guides
created: '2025-03-14'
updated: '2025-03-14'
version: 0.1.0
---

# MCP Service Integration Patterns

## Overview

This document outlines patterns and strategies for integrating various services with Model Context Protocol (MCP). These integration patterns enable AI models to interact with external tools, data sources, and APIs in standardized ways.

## Core Integration Patterns

### 1. Direct API Integration

**Pattern**: Connect MCP directly to a service's API endpoints.

**Implementation**:
```javascript
// Example: GitHub API integration
const { createServer } = require('@modelcontextprotocol/server');

const githubTools = [{
  name: 'searchRepositories',
  description: 'Search GitHub repositories',
  parameters: {
    type: 'object',
    properties: {
      query: { type: 'string', description: 'Search query' },
      limit: { type: 'number', description: 'Maximum results to return' }
    },
    required: ['query']
  },
  handler: async ({ query, limit = 10 }) => {
    const response = await fetch(`https://api.github.com/search/repositories?q=${query}&per_page=${limit}`);
    const data = await response.json();
    return { repositories: data.items };
  }
}];

createServer({ tools: githubTools }).listen(3000);
```

**Use Cases**: GitHub, Slack, Jira, Google Maps

### 2. Database Connectors

**Pattern**: Enable AI models to query and manipulate database systems.

**Implementation**:
```javascript
// Example: PostgreSQL integration
const { createServer } = require('@modelcontextprotocol/server');
const { Pool } = require('pg');

const pool = new Pool({
  connectionString: process.env.DATABASE_URL
});

const postgresTools = [{
  name: 'queryDatabase',
  description: 'Run a SQL query against PostgreSQL database',
  parameters: {
    type: 'object',
    properties: {
      query: { type: 'string', description: 'SQL query to execute' },
      params: { type: 'array', description: 'Query parameters', items: { type: 'string' } }
    },
    required: ['query']
  },
  handler: async ({ query, params = [] }) => {
    const result = await pool.query(query, params);
    return { rows: result.rows, rowCount: result.rowCount };
  }
}];

createServer({ tools: postgresTools }).listen(3000);
```

**Use Cases**: PostgreSQL, MySQL, MongoDB, Supabase

### 3. File System Access

**Pattern**: Provide AI models with access to local or cloud file systems.

**Implementation**:
```javascript
// Example: Local file system integration
const { createServer } = require('@modelcontextprotocol/server');
const fs = require('fs/promises');
const path = require('path');

const basePath = process.env.FILES_BASE_PATH || './files';

const fileSystemTools = [{
  name: 'readFile',
  description: 'Read a file from the allowed directory',
  parameters: {
    type: 'object',
    properties: {
      filePath: { type: 'string', description: 'Path to the file' }
    },
    required: ['filePath']
  },
  handler: async ({ filePath }) => {
    // Security check to prevent path traversal
    const normalizedPath = path.normalize(filePath);
    if (normalizedPath.startsWith('..')) {
      throw new Error('Invalid file path');
    }
    
    const fullPath = path.join(basePath, normalizedPath);
    const content = await fs.readFile(fullPath, 'utf8');
    return { content };
  }
}];

createServer({ tools: fileSystemTools }).listen(3000);
```

**Use Cases**: Local files, Google Drive, S3, Everything Search

### 4. Web Browsing and Scraping

**Pattern**: Allow AI models to browse websites and extract information.

**Implementation**:
```javascript
// Example: Puppeteer integration for web browsing
const { createServer } = require('@modelcontextprotocol/server');
const puppeteer = require('puppeteer');

let browser;

const initBrowser = async () => {
  if (!browser) {
    browser = await puppeteer.launch();
  }
  return browser;
};

const webTools = [{
  name: 'browseWebpage',
  description: 'Browse a webpage and extract its content',
  parameters: {
    type: 'object',
    properties: {
      url: { type: 'string', description: 'URL to browse' },
      selector: { type: 'string', description: 'Optional CSS selector to extract specific content' }
    },
    required: ['url']
  },
  handler: async ({ url, selector }) => {
    const browser = await initBrowser();
    const page = await browser.newPage();
    
    await page.goto(url, { waitUntil: 'networkidle2' });
    
    let content;
    if (selector) {
      content = await page.evaluate((sel) => {
        const element = document.querySelector(sel);
        return element ? element.textContent : null;
      }, selector);
    } else {
      content = await page.content();
    }
    
    await page.close();
    
    return { content, title: await page.title() };
  }
}];

createServer({ tools: webTools }).listen(3000);

// Cleanup
process.on('exit', async () => {
  if (browser) {
    await browser.close();
  }
});
```

**Use Cases**: Puppeteer, Firecrawl, browser automation

### 5. Authentication and Authorization

**Pattern**: Implement OAuth flows and API key authentication for secure service access.

**Implementation**:
```javascript
// Example: OAuth flow for Google services
const { createServer } = require('@modelcontextprotocol/server');
const { google } = require('googleapis');
const oauth2Client = new google.auth.OAuth2(
  process.env.GOOGLE_CLIENT_ID,
  process.env.GOOGLE_CLIENT_SECRET,
  process.env.GOOGLE_REDIRECT_URL
);

// Store tokens (in production, use a secure database)
const tokens = {};

const authTools = [{
  name: 'getAuthUrl',
  description: 'Get URL for Google OAuth authorization',
  parameters: {
    type: 'object',
    properties: {
      userId: { type: 'string', description: 'Unique user identifier' }
    },
    required: ['userId']
  },
  handler: async ({ userId }) => {
    const url = oauth2Client.generateAuthUrl({
      access_type: 'offline',
      scope: ['https://www.googleapis.com/auth/drive.readonly'],
      state: userId
    });
    return { authUrl: url };
  }
}];

// Additional handler for OAuth callback (not exposed as MCP tool)
// This would be a separate HTTP endpoint in your server
const handleOAuthCallback = async (req, res) => {
  const { code, state } = req.query;
  const { tokens: authTokens } = await oauth2Client.getToken(code);
  tokens[state] = authTokens;
  res.send('Authentication successful, you can close this window.');
};

createServer({ tools: authTools }).listen(3000);
```

**Use Cases**: OAuth services, API key management, JWT authentication

## Service-Specific Integration Examples

### GitHub Integration

```javascript
// GitHub MCP server for repository management
const githubTools = [
  {
    name: 'createRepository',
    description: 'Create a new GitHub repository',
    parameters: {
      type: 'object',
      properties: {
        name: { type: 'string', description: 'Repository name' },
        description: { type: 'string', description: 'Repository description' },
        isPrivate: { type: 'boolean', description: 'Whether the repository is private' }
      },
      required: ['name']
    },
    handler: async ({ name, description = '', isPrivate = false }) => {
      const response = await fetch('https://api.github.com/user/repos', {
        method: 'POST',
        headers: {
          'Authorization': `token ${process.env.GITHUB_TOKEN}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          name,
          description,
          private: isPrivate
        })
      });
      return await response.json();
    }
  }
];
```

### Slack Integration

```javascript
// Slack MCP server for messaging
const slackTools = [
  {
    name: 'sendMessage',
    description: 'Send a message to a Slack channel',
    parameters: {
      type: 'object',
      properties: {
        channel: { type: 'string', description: 'Channel ID or name' },
        text: { type: 'string', description: 'Message text' }
      },
      required: ['channel', 'text']
    },
    handler: async ({ channel, text }) => {
      const response = await fetch('https://slack.com/api/chat.postMessage', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${process.env.SLACK_TOKEN}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ channel, text })
      });
      return await response.json();
    }
  }
];
```

### Google Drive Integration

```javascript
// Google Drive MCP server for file access
const driveTools = [
  {
    name: 'listFiles',
    description: 'List files in Google Drive',
    parameters: {
      type: 'object',
      properties: {
        userId: { type: 'string', description: 'User identifier for token lookup' },
        query: { type: 'string', description: 'Search query (optional)' }
      },
      required: ['userId']
    },
    handler: async ({ userId, query = '' }) => {
      const userTokens = tokens[userId];
      if (!userTokens) {
        throw new Error('User not authenticated');
      }
      
      oauth2Client.setCredentials(userTokens);
      const drive = google.drive({ version: 'v3', auth: oauth2Client });
      
      const response = await drive.files.list({
        q: query,
        pageSize: 10,
        fields: 'nextPageToken, files(id, name, mimeType, webViewLink)'
      });
      
      return { files: response.data.files };
    }
  }
];
```

### Healthcare Data (FHIR) Integration

```javascript
// FHIR MCP server for healthcare data
const fhirTools = [
  {
    name: 'getPatientData',
    description: 'Get patient data from FHIR server',
    parameters: {
      type: 'object',
      properties: {
        patientId: { type: 'string', description: 'FHIR patient identifier' }
      },
      required: ['patientId']
    },
    handler: async ({ patientId }) => {
      const response = await fetch(`https://fhir-api.example.com/Patient/${patientId}`, {
        headers: {
          'Authorization': `Bearer ${process.env.FHIR_TOKEN}`
        }
      });
      return await response.json();
    }
  }
];
```

## MCP Server Directory Information

Several directories list available MCP servers for integration:

1. **smithery.ai/mcp/servers**
2. **glama.ai/mcp/servers**
3. **cursor.directory**
4. **lmsystems.ai/marketplace**

## Best Practices for MCP Integration

### Security

- Implement proper authentication for all service integrations
- Use environment variables for sensitive credentials
- Validate all input parameters before executing actions
- Implement rate limiting to prevent abuse
- Use HTTPS for all external API calls

### Performance

- Implement connection pooling for database integrations
- Cache frequently accessed data when appropriate
- Use streaming for large data transfers
- Implement timeout handling for external services

### Error Handling

- Provide meaningful error messages for debugging
- Implement retry logic for transient failures
- Log errors for monitoring and troubleshooting
- Handle service-specific error codes appropriately

### Documentation

- Clearly document all available tools and their parameters
- Provide examples of tool usage for developers
- Document authentication requirements and setup process
- Keep documentation updated as services evolve

## Resource Management

- Implement proper cleanup for resources (database connections, browser instances)
- Monitor memory usage and implement garbage collection as needed
- Implement proper shutdown procedures for clean process termination
- Use connection pooling for frequently accessed services

## Testing Strategies

- Unit test individual tool handlers
- Integration test with mock services
- End-to-end test with actual service connections
- Implement continuous integration for automated testing

## Resources

For implementation examples and additional resources:
- Official MCP Documentation: [Anthropic MCP GitHub](https://github.com/anthropics/model-context-protocol)
- Example Implementations: [Community MCP Servers](https://github.com/topics/mcp-server)
