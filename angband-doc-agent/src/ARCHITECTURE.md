# Lute the Bard - Architecture Overview

This document describes the architecture of the Lute the Bard narrative generation system for Tower of Babel.

## System Components

```
┌───────────────────┐      ┌───────────────────┐      ┌───────────────────┐
│                   │      │                   │      │                   │
│  Tower of Babel   │      │    MCP Client     │      │    MCP Server     │
│  (Angband Game)   │─────▶│    (mcp-client.c) │─────▶│  (Node.js)        │
│                   │      │                   │      │                   │
└───────────┬───────┘      └───────────┬───────┘      └───────────┬───────┘
            │                          │                          │
            │                          │                          │
            ▼                          ▼                          ▼
┌───────────────────┐      ┌───────────────────┐      ┌───────────────────┐
│                   │      │                   │      │                   │
│  Bard Interface   │      │  HTTP/JSON        │      │  OpenAI API       │
│  (bard.c/h)       │      │  Communication    │      │  Integration      │
│                   │      │                   │      │                   │
└───────────────────┘      └───────────────────┘      └───────────────────┘
                                                                │
                                                                │
                                                                ▼
                                                      ┌───────────────────┐
                                                      │                   │
                                                      │  Memory System    │
                                                      │  (JSON Files)     │
                                                      │                   │
                                                      └───────────────────┘
```

## Component Details

### 1. Tower of Babel (Angband Game)

This is the core roguelike game, an Angband variant. The game triggers narrative generation at key gameplay moments:

- When monsters are defeated
- When items are discovered
- When new dungeon levels are entered
- When the player has a near-death experience
- When quests are completed
- When the player levels up

The game communicates with the Bard system through the Bard Interface.

### 2. Bard Interface (bard.c/h)

The Bard Interface is a C module that provides a clean API for the game to interact with the narrative generation system:

- It maintains a queue of generated narratives
- It tracks pending narrative requests
- It handles configuration of narrative style, frequency, and verbosity

The Bard Interface uses the MCP Client to communicate with the MCP Server.

### 3. MCP Client (mcp-client.c)

The MCP Client implements the Model Context Protocol in C:

- It handles HTTP communication with the MCP Server
- It manages asynchronous requests and responses
- It serializes and deserializes JSON data
- It provides error handling and retry mechanisms

### 4. MCP Server (bard-mcp-server.js)

The MCP Server is a Node.js application that implements the server-side of the Model Context Protocol:

- It exposes an HTTP API for the MCP Client to connect to
- It processes narrative generation requests
- It integrates with the OpenAI API to generate narratives
- It manages the Memory System

### 5. Memory System (JSON Files)

The Memory System stores and retrieves character memories:

- Each character has its own memory file
- Memories are stored as JSON data
- Memories are organized by type (events, relationships, etc.)
- Memories have importance values and timestamps
- The system automatically prunes less important memories when the storage limit is reached

### 6. OpenAI API Integration

The MCP Server uses the OpenAI API to generate narratives:

- It constructs detailed prompts based on the event type and details
- It includes relevant memories to provide context
- It supports different narrative styles and tones
- It receives structured JSON responses containing the narrative text and metadata

## Data Flow

1. **Game Event → Bard Interface**: The game calls the appropriate Bard function when an event occurs.

2. **Bard Interface → MCP Client**: The Bard Interface creates a request with event details and sends it to the MCP Client.

3. **MCP Client → MCP Server**: The MCP Client serializes the request to JSON and sends it to the MCP Server via HTTP.

4. **MCP Server → OpenAI API**: The MCP Server constructs a prompt with event details and relevant memories, then sends it to the OpenAI API.

5. **OpenAI API → MCP Server**: The API returns a generated narrative.

6. **MCP Server → Memory System**: The MCP Server stores the event and narrative in the character's memory.

7. **MCP Server → MCP Client**: The MCP Server sends the narrative back to the MCP Client.

8. **MCP Client → Bard Interface**: The MCP Client deserializes the response and notifies the Bard Interface.

9. **Bard Interface → Game**: The Bard Interface adds the narrative to its queue, which the game can display at the appropriate time.

## Memory Management

The Memory System uses a sophisticated approach to manage memories:

1. **Importance-Based Storage**: Memories are assigned importance values (1-100) based on the event type and the AI's assessment of significance.

2. **Retrieval by Relevance**: When generating new narratives, the system retrieves memories based on:
   - Recency (newer memories are favored)
   - Importance (more significant memories are favored)
   - Relevance to the current event (e.g., previous encounters with the same monster)

3. **Memory Pruning**: When a character's memory exceeds the size limit, less important memories are automatically pruned.

## Asynchronous Processing

The system uses asynchronous processing to avoid blocking gameplay:

1. The game calls Bard functions, which return immediately
2. The Bard Interface sends asynchronous requests to the MCP Server
3. The game periodically calls `bard_process_pending()` to check for completed narratives
4. Completed narratives are added to the queue
5. The game calls `bard_get_next_narrative()` to retrieve and display narratives at appropriate times

## Configuration

The system is highly configurable:

1. **Narrative Frequency**: Controls how often narratives are generated (0-100)
2. **Verbosity**: Controls the length and detail of narratives (0-100)
3. **Style**: Sets the default narrative style (fantasy, poetic, humorous, etc.)
4. **Debug Mode**: Enables detailed logging for troubleshooting

## Error Handling

The system implements robust error handling:

1. **Client-Side Retries**: The MCP Client automatically retries failed requests
2. **Server-Side Fallbacks**: The MCP Server provides fallback narratives if the AI generation fails
3. **Graceful Degradation**: If the narrative system is unavailable, the game continues to function without narratives 