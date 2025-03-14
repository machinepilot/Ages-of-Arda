/**
 * Bard MCP Server - Enhanced narrative generation for Tower of Babel
 * 
 * This server implements the Model Context Protocol (MCP) for the Tower of Babel Angband variant,
 * providing narrative generation capabilities through Lute the Bard.
 */

const express = require('express');
const bodyParser = require('body-parser');
const cors = require('cors');
const fs = require('fs');
const path = require('path');
const { v4: uuidv4 } = require('uuid');
const axios = require('axios');
const { Configuration, OpenAIApi } = require('openai');

// Initialize the server
const app = express();
app.use(cors());
app.use(bodyParser.json());

// Configuration 
const config = {
    port: process.env.PORT || 3000,
    apiKey: process.env.OPENAI_API_KEY,
    modelName: process.env.MODEL_NAME || 'gpt-4',
    memoryPath: process.env.MEMORY_PATH || './memories',
    llmProvider: process.env.LLM_PROVIDER || 'ollama', // 'openai' or 'ollama'
    ollamaUrl: process.env.OLLAMA_URL || 'http://localhost:11434',
    ollamaModel: process.env.OLLAMA_MODEL || 'llama3.2',
    narrativeStyles: {
        fantasy: "Rich, epic fantasy with vivid imagery in the style of Tolkien or George R.R. Martin",
        poetic: "Lyrical and rhythmic, employing verse and metaphor like ancient bards",
        humorous: "Light-hearted and witty, with a dose of situational humor",
        dark: "Grim and foreboding, emphasizing the dangers and darkness of the dungeon",
        minimalist: "Brief, concise descriptions focused on essential details only",
        heroic: "Epic, emphasizing the player's bravery and legendary deeds",
        mythic: "Drawing on classic mythology tropes and archetypes"
    }
};

// Initialize LLM client based on provider
let openai;
if (config.llmProvider === 'openai') {
    const configuration = new Configuration({
        apiKey: config.apiKey,
    });
    openai = new OpenAIApi(configuration);
}

// Memory storage initialization
if (!fs.existsSync(config.memoryPath)) {
    fs.mkdirSync(config.memoryPath, { recursive: true });
}

// In-memory store for pending requests
const pendingRequests = new Map();

/**
 * Tool definitions for the MCP server
 */
const tools = {
    // Generate narrative for game events
    generate_narrative: async (params) => {
        const { 
            event_type, 
            event_data, 
            character_id, 
            style = 'fantasy', 
            tone, 
            verbosity = 50,
            player_info = {} 
        } = params;

        // Parse event data
        let eventDetails;
        try {
            eventDetails = typeof event_data === 'string' ? JSON.parse(event_data) : event_data;
        } catch (err) {
            return { error: "Invalid event data format" };
        }

        // Retrieve character memories
        const memories = await getCharacterMemories(character_id);
        
        // Determine narrative style
        const narrativeStyle = config.narrativeStyles[style] || config.narrativeStyles.fantasy;
        
        // Build context for narrative generation
        const context = buildNarrativeContext(
            event_type, 
            eventDetails, 
            player_info, 
            style, 
            tone, 
            verbosity, 
            memories
        );
        
        // Generate the narrative using selected LLM provider
        const narrative = await generateNarrative(context);
        
        // Store relevant event in memory
        await updateMemory(character_id, event_type, eventDetails, narrative);
        
        return {
            narrative: narrative.text,
            is_spoken: narrative.is_spoken,
            importance: narrative.importance
        };
    },
    
    // Update character memory explicitly
    update_memory: async (params) => {
        const { character_id, memory_type, memory_content } = params;
        
        if (!character_id || !memory_type || !memory_content) {
            return { error: "Missing required parameters" };
        }
        
        await updateCharacterMemory(character_id, memory_type, memory_content);
        
        return { success: true };
    },
    
    // Query character memories
    query_memory: async (params) => {
        const { character_id, query_type, query_params } = params;
        
        if (!character_id) {
            return { error: "Missing character_id parameter" };
        }
        
        const memories = await queryCharacterMemories(character_id, query_type, query_params);
        
        return { memories };
    }
};

/**
 * Build a context object for narrative generation
 */
function buildNarrativeContext(eventType, eventDetails, playerInfo, style, tone, verbosity, memories) {
    // Format event type for the prompt
    const formattedEventType = eventType.replace(/_/g, ' ');
    
    // Extract key memories relevant to this event
    const relevantMemories = getRelevantMemories(memories, eventType, eventDetails);
    
    return {
        eventType: formattedEventType,
        eventDetails,
        playerInfo,
        style,
        tone,
        verbosity,
        relevantMemories
    };
}

/**
 * Generate narrative text using the configured LLM provider
 */
async function generateNarrative(context) {
    const { eventType, eventDetails, playerInfo, style, tone, verbosity, relevantMemories } = context;
    
    // Build prompt based on narrative style
    const narrativeStyle = config.narrativeStyles[style] || config.narrativeStyles.fantasy;
    
    // Create the base system prompt
    let systemPrompt = `You are Lute the Bard, a talented storyteller in the Tower of Babel, an Angband variant. 
Your task is to create compelling narrative text for ${eventType} events in the game.

Create a ${verbosity < 30 ? 'brief' : verbosity > 70 ? 'detailed' : 'balanced'} narrative in the ${narrativeStyle} style.
${tone ? `The tone should be ${tone}.` : ''}

The player character is ${playerInfo.name || 'the adventurer'}, a level ${playerInfo.level || '?'} ${playerInfo.race || ''} ${playerInfo.class || ''}.

EVENT DETAILS:
${JSON.stringify(eventDetails, null, 2)}

RELEVANT PAST EVENTS:
${relevantMemories.length > 0 ? relevantMemories.join("\n") : "No relevant past events."}

Generate ONLY the narrative text. Your response should be in this JSON format:
{
  "text": "Your narrative text here",
  "is_spoken": true/false (whether this should be presented as character dialogue),
  "importance": 1-100 (how important this narrative is compared to other events)
}`;

    try {
        let content;
        
        // Use the appropriate LLM provider
        if (config.llmProvider === 'openai') {
            // OpenAI API
            const response = await openai.createChatCompletion({
                model: config.modelName,
                messages: [
                    { role: "system", content: systemPrompt },
                    { role: "user", content: `Generate a narrative for this ${eventType} event.` }
                ],
                temperature: 0.7,
                response_format: { type: "json_object" }
            });
            
            content = response.data.choices[0].message.content;
        } else if (config.llmProvider === 'ollama') {
            // Ollama API
            const response = await axios.post(`${config.ollamaUrl}/api/chat`, {
                model: config.ollamaModel,
                messages: [
                    { role: "system", content: systemPrompt },
                    { role: "user", content: `Generate a narrative for this ${eventType} event.` }
                ],
                stream: false,
                options: {
                    temperature: 0.7
                }
            });
            
            content = response.data.message.content;
        } else {
            throw new Error(`Unknown LLM provider: ${config.llmProvider}`);
        }
        
        let parsedResponse;
        
        try {
            parsedResponse = JSON.parse(content);
        } catch (e) {
            console.error("Failed to parse AI response as JSON:", e);
            console.log("Raw response:", content);
            
            // Attempt to extract JSON if it's embedded in markdown or other text
            const jsonMatch = content.match(/```json\n([\s\S]*)\n```/) || 
                             content.match(/```\n([\s\S]*)\n```/) || 
                             content.match(/{[\s\S]*}/);
                             
            if (jsonMatch) {
                try {
                    parsedResponse = JSON.parse(jsonMatch[1] || jsonMatch[0]);
                } catch (e2) {
                    console.error("Failed to extract JSON from markdown:", e2);
                }
            }
            
            // If still no valid JSON, create a fallback response
            if (!parsedResponse) {
                // Fallback: extract text and create a basic response
                return {
                    text: content.slice(0, 500),
                    is_spoken: false,
                    importance: 50
                };
            }
        }
        
        return {
            text: parsedResponse.text,
            is_spoken: !!parsedResponse.is_spoken,
            importance: parseInt(parsedResponse.importance) || 50
        };
    } catch (error) {
        console.error("Error generating narrative:", error);
        return {
            text: `The bard seems at a loss for words...`,
            is_spoken: false,
            importance: 10
        };
    }
}

/**
 * Get character memory file path
 */
function getCharacterMemoryPath(characterId) {
    return path.join(config.memoryPath, `${characterId}.json`);
}

/**
 * Retrieve character memories
 */
async function getCharacterMemories(characterId) {
    if (!characterId) return [];
    
    const memoryPath = getCharacterMemoryPath(characterId);
    
    try {
        if (fs.existsSync(memoryPath)) {
            const data = fs.readFileSync(memoryPath, 'utf8');
            return JSON.parse(data);
        }
    } catch (error) {
        console.error(`Error reading memories for character ${characterId}:`, error);
    }
    
    return [];
}

/**
 * Update character memory with new event
 */
async function updateMemory(characterId, eventType, eventDetails, narrative) {
    if (!characterId) return;
    
    // Define memory importance based on event type and narrative importance
    const importanceMap = {
        quest_complete: 90,
        near_death: 85,
        level_up: 80,
        new_level: 70,
        monster_death: eventDetails.is_unique ? 85 : 50,
        item_discovery: eventDetails.is_artifact ? 85 : 50
    };
    
    const baseImportance = importanceMap[eventType] || 40;
    const finalImportance = Math.min(100, Math.max(1, 
        Math.floor((baseImportance + narrative.importance) / 2)));
    
    const memory = {
        id: uuidv4(),
        timestamp: Date.now(),
        event_type: eventType,
        details: eventDetails,
        narrative: narrative.text,
        importance: finalImportance
    };
    
    await updateCharacterMemory(characterId, 'events', memory);
}

/**
 * Update a specific memory type for a character
 */
async function updateCharacterMemory(characterId, memoryType, content) {
    if (!characterId) return;
    
    const memoryPath = getCharacterMemoryPath(characterId);
    let memories = [];
    
    // Read existing memories
    try {
        if (fs.existsSync(memoryPath)) {
            const data = fs.readFileSync(memoryPath, 'utf8');
            memories = JSON.parse(data);
        }
    } catch (error) {
        console.error(`Error reading memories for character ${characterId}:`, error);
    }
    
    // Find memory category
    const categoryIndex = memories.findIndex(m => m.type === memoryType);
    
    if (categoryIndex >= 0) {
        // Category exists, add memory to it
        if (Array.isArray(memories[categoryIndex].items)) {
            memories[categoryIndex].items.push(content);
            
            // Keep only the most important memories if we exceed the limit
            const MAX_MEMORIES_PER_TYPE = 100;
            if (memories[categoryIndex].items.length > MAX_MEMORIES_PER_TYPE) {
                memories[categoryIndex].items.sort((a, b) => (b.importance || 0) - (a.importance || 0));
                memories[categoryIndex].items = memories[categoryIndex].items.slice(0, MAX_MEMORIES_PER_TYPE);
            }
        } else {
            // Memory is a single value, replace it
            memories[categoryIndex].value = content;
        }
    } else {
        // Category doesn't exist, create it
        if (typeof content === 'object' && 'id' in content) {
            // Create as array if it's a complex object with ID
            memories.push({
                type: memoryType,
                items: [content]
            });
        } else {
            // Create as single value
            memories.push({
                type: memoryType,
                value: content
            });
        }
    }
    
    // Write back to file
    try {
        fs.writeFileSync(memoryPath, JSON.stringify(memories, null, 2), 'utf8');
    } catch (error) {
        console.error(`Error writing memories for character ${characterId}:`, error);
    }
}

/**
 * Query character memories by type and parameters
 */
async function queryCharacterMemories(characterId, queryType, queryParams) {
    if (!characterId) return [];
    
    const memories = await getCharacterMemories(characterId);
    
    if (!queryType) {
        return memories; // Return all memories
    }
    
    // Find the specified memory category
    const category = memories.find(m => m.type === queryType);
    if (!category) return [];
    
    // Return entire category if no query params
    if (!queryParams) {
        return category.items || [category.value];
    }
    
    // Handle specific query types
    if (category.items && Array.isArray(category.items)) {
        // For events, we can filter by event_type
        if (queryParams.event_type) {
            return category.items.filter(item => item.event_type === queryParams.event_type);
        }
        
        // Filter by time range
        if (queryParams.since && typeof queryParams.since === 'number') {
            return category.items.filter(item => 
                item.timestamp && item.timestamp >= queryParams.since);
        }
        
        // Return top N most important memories
        if (queryParams.top && typeof queryParams.top === 'number') {
            return [...category.items]
                .sort((a, b) => (b.importance || 0) - (a.importance || 0))
                .slice(0, queryParams.top);
        }
    }
    
    return category.items || [category.value];
}

/**
 * Get memories relevant to the current event
 */
function getRelevantMemories(memories, eventType, eventDetails) {
    const relevantMemories = [];
    
    // Find the events category
    const eventsCategory = memories.find(m => m.type === 'events');
    if (!eventsCategory || !eventsCategory.items) {
        return relevantMemories;
    }
    
    // Copy items and sort by recency and importance
    const items = [...eventsCategory.items]
        .sort((a, b) => {
            // Score is 70% importance, 30% recency
            const importanceA = a.importance || 0;
            const importanceB = b.importance || 0;
            const recencyA = a.timestamp || 0;
            const recencyB = b.timestamp || 0;
            
            const scoreA = (importanceA * 0.7) + (recencyA * 0.3);
            const scoreB = (importanceB * 0.7) + (recencyB * 0.3);
            
            return scoreB - scoreA;
        });
    
    // Get most recent events (up to 5)
    const recentEvents = items.slice(0, 5);
    
    // Add specific event type matches 
    const typeMatches = items
        .filter(item => item.event_type === eventType)
        .slice(0, 3);
    
    // Add context-specific matches
    let contextMatches = [];
    
    switch (eventType) {
        case 'monster_death':
            // Find previous encounters with the same monster
            if (eventDetails.monster_name) {
                contextMatches = items.filter(item => 
                    item.event_type === 'monster_death' && 
                    item.details && 
                    item.details.monster_name === eventDetails.monster_name
                ).slice(0, 2);
            }
            break;
            
        case 'new_level':
            // Find previous visits to this dungeon level
            if (eventDetails.dungeon_level) {
                contextMatches = items.filter(item =>
                    item.event_type === 'new_level' &&
                    item.details &&
                    item.details.dungeon_level === eventDetails.dungeon_level
                ).slice(0, 2);
            }
            break;
            
        case 'near_death':
            // Find previous near-death experiences with the same enemy
            if (eventDetails.enemy_name) {
                contextMatches = items.filter(item =>
                    item.event_type === 'near_death' &&
                    item.details &&
                    item.details.enemy_name === eventDetails.enemy_name
                ).slice(0, 2);
            }
            break;
    }
    
    // Combine all relevant memories, removing duplicates
    const allRelevant = [...recentEvents, ...typeMatches, ...contextMatches];
    const uniqueMemories = allRelevant.filter((memory, index, self) =>
        index === self.findIndex(m => m.id === memory.id)
    );
    
    // Sort by timestamp (most recent first) and take top 7
    uniqueMemories.sort((a, b) => (b.timestamp || 0) - (a.timestamp || 0));
    const topMemories = uniqueMemories.slice(0, 7);
    
    // Format memories as strings
    return topMemories.map(memory => 
        `[${new Date(memory.timestamp).toLocaleDateString()}] ${memory.event_type}: ${memory.narrative}`
    );
}

// MCP Server routes
app.post('/invoke', async (req, res) => {
    const { tool, params, request_id } = req.body;
    
    // Validate request
    if (!tool || !tools[tool]) {
        return res.status(400).json({ error: `Unknown tool: ${tool}` });
    }
    
    try {
        // Handle synchronous vs asynchronous requests
        if (request_id) {
            // Asynchronous request
            const taskId = uuidv4();
            pendingRequests.set(taskId, { status: 'pending', tool, params });
            
            // Start processing in the background
            tools[tool](params)
                .then(result => {
                    pendingRequests.set(taskId, { 
                        status: 'completed', 
                        result,
                        completed_at: new Date().toISOString()
                    });
                })
                .catch(error => {
                    pendingRequests.set(taskId, { 
                        status: 'error', 
                        error: error.message,
                        completed_at: new Date().toISOString()
                    });
                });
            
            return res.json({ request_id: taskId });
        } else {
            // Synchronous request
            const result = await tools[tool](params);
            return res.json(result);
        }
    } catch (error) {
        console.error(`Error processing tool ${tool}:`, error);
        return res.status(500).json({ error: error.message });
    }
});

// Check status of asynchronous requests
app.get('/status/:requestId', (req, res) => {
    const { requestId } = req.params;
    const request = pendingRequests.get(requestId);
    
    if (!request) {
        return res.status(404).json({ error: 'Request not found' });
    }
    
    // If completed, return the result and clean up
    if (request.status === 'completed' || request.status === 'error') {
        const response = { ...request };
        
        // Clean up completed requests after 1 hour
        setTimeout(() => {
            pendingRequests.delete(requestId);
        }, 60 * 60 * 1000);
        
        return res.json(response);
    }
    
    // Still pending
    return res.json({ status: 'pending' });
});

// Health check endpoint
app.get('/health', (req, res) => {
    res.json({
        status: 'ok',
        provider: config.llmProvider,
        model: config.llmProvider === 'ollama' ? config.ollamaModel : config.modelName
    });
});

// Start the server
const server = app.listen(config.port, () => {
    console.log(`Bard MCP Server listening on port ${config.port}`);
    console.log(`LLM Provider: ${config.llmProvider}`);
    console.log(`Model: ${config.llmProvider === 'ollama' ? config.ollamaModel : config.modelName}`);
    console.log(`Memory path: ${config.memoryPath}`);
});

// Handle graceful shutdown
process.on('SIGTERM', () => {
    console.log('SIGTERM received, shutting down...');
    server.close(() => {
        console.log('Server closed');
        process.exit(0);
    });
});

module.exports = app; 