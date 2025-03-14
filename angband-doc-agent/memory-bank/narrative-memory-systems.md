# Narrative Memory Systems for Storytelling Continuity

## Overview

This document outlines the architecture and implementation of memory systems for Lute the Bard in Tower of Babel. Effective narrative memory is crucial for maintaining storytelling continuity across game sessions and creating a cohesive player experience.

## Memory System Architecture

### Key Components

1. **Event Repository**
   - Persistent storage of significant game events
   - Structured data format for efficient retrieval
   - Priority scoring system for memory importance

2. **Character Memory**
   - Player character attributes and evolution
   - Relationships with NPCs and factions
   - Personal narrative arc tracking

3. **World State Memory**
   - Discovered locations and their significance
   - Major world changes from player actions
   - Current threats and opportunities

4. **Meta Memory**
   - Player narrative preferences
   - Response to previous narrative styles
   - Session frequency and duration patterns

### Memory Hierarchies

#### By Persistence
- **Ephemeral** (current session only)
- **Short-term** (persists across several sessions)
- **Long-term** (permanent record of major events)
- **Foundational** (core world lore, never forgotten)

#### By Importance
- **Critical** (unique monsters, artifacts, major achievements)
- **Significant** (level gains, special encounters, near-death experiences)
- **Contextual** (environmental details, routine encounters)
- **Ambient** (mood, atmosphere, general progression)

## Data Structures

### Event Record
```json
{
  "event_id": "uuid-string",
  "event_type": "monster_defeat",
  "timestamp": {
    "game_turn": 145678,
    "real_time": "2023-03-15T21:34:12Z",
    "dungeon_level": 23
  },
  "importance": 85,
  "entities": {
    "monster": {
      "name": "Shelob",
      "unique": true,
      "level": 45,
      "type": "spider",
      "special_properties": ["poisonous", "webspinner"]
    },
    "player": {
      "name": "Elendil",
      "level": 28,
      "race": "High-Elf",
      "class": "Ranger",
      "hp_remaining_pct": 15
    }
  },
  "location": {
    "area_name": "Webbed Cavern",
    "area_type": "special room",
    "notable_features": ["spider webs", "bone pile", "treasure chest"]
  },
  "narrative_summary": "A desperate battle against the ancient spider queen Shelob, nearly ending in defeat before a critical arrow shot found its mark.",
  "narrative_detail": "Full narrative text generated at the time...",
  "narrative_impact": ["established_as_spider_slayer", "near_death_experience", "major_unique_defeated"],
  "references": ["event_id_of_first_encounter", "event_id_of_finding_special_arrow"]
}
```

### Character Memory Record
```json
{
  "character_id": "uuid-string",
  "base_info": {
    "name": "Elendil",
    "race": "High-Elf",
    "class": "Ranger",
    "significant_attributes": ["exceptional_dexterity", "eagle_eyed"]
  },
  "narrative_identity": {
    "defining_moments": ["event_id1", "event_id2", "event_id3"],
    "character_arc": "reluctant_hero",
    "behavioral_patterns": ["cautious_explorer", "monster_specialist"],
    "recurring_themes": ["vengeance_against_undead", "seeking_ancient_knowledge"]
  },
  "relationships": {
    "lute_the_bard": {
      "affinity": 85,
      "key_moments": ["event_id4", "event_id5"],
      "relationship_arc": "initial_skepticism_to_trusted_companion"
    },
    "npcs": [
      {
        "name": "Town Healer",
        "affinity": 65,
        "key_moments": ["event_id6"],
        "relationship_traits": ["respectful", "professional"]
      }
    ],
    "factions": [
      {
        "name": "Mages Guild",
        "standing": "allied",
        "key_moments": ["event_id7", "event_id8"]
      }
    ]
  },
  "achievements": {
    "uniques_defeated": ["Shelob", "Wormtongue", "Azog"],
    "artifacts_found": ["Sting", "Phial of Galadriel"],
    "depths_reached": 45,
    "quests_completed": ["The Dark Spire", "Moria's Depths"]
  }
}
```

## Memory Management Algorithms

### Event Selection Algorithm

The system must determine which events to include in narrative context. Key factors:

1. **Recency**: More recent events receive higher priority
2. **Importance**: Events marked as critical take precedence
3. **Relevance**: Events related to current situation get boosted priority
4. **Continuity**: Events that connect narrative threads are preserved
5. **Uniqueness**: Preference for diverse event types over repetition

Pseudo-code implementation:
```python
def select_narrative_context_events(current_state, event_repository, token_budget):
    # Get all events
    candidate_events = event_repository.get_all_events()
    
    # Initialize scores
    for event in candidate_events:
        event.context_score = 0
        
        # Base score from importance
        event.context_score += event.importance * 0.5
        
        # Recency factor (inverse log decay)
        turns_ago = current_state.game_turn - event.timestamp.game_turn
        event.context_score += 100 / math.log(turns_ago + 10) 
        
        # Relevance to current situation
        if event.location.area_type == current_state.location.area_type:
            event.context_score *= 1.2
        if any(entity in current_state.visible_entities for entity in event.entities):
            event.context_score *= 1.5
            
        # Narrative continuity
        if event.narrative_impact:
            for impact in event.narrative_impact:
                if impact in current_state.active_narrative_threads:
                    event.context_score *= 1.3
    
    # Sort by score
    candidate_events.sort(key=lambda e: e.context_score, reverse=True)
    
    # Select events up to token budget
    selected_events = []
    current_tokens = 0
    
    for event in candidate_events:
        event_tokens = estimate_tokens(event)
        if current_tokens + event_tokens <= token_budget:
            selected_events.append(event)
            current_tokens += event_tokens
        elif is_critical_event(event):
            # Try to fit critical events by using summary instead of full detail
            summary_tokens = estimate_tokens(event.narrative_summary)
            if current_tokens + summary_tokens <= token_budget:
                summarized_event = summarize_event(event)
                selected_events.append(summarized_event)
                current_tokens += summary_tokens
    
    return selected_events
```

### Memory Compression Algorithm

As memory grows, older events need compression to conserve space:

1. **Summarization**: Convert detailed narratives to summaries
2. **Aggregation**: Combine similar or related events
3. **Prioritization**: Retain only highest-impact details
4. **Pattern Extraction**: Identify and store recurring themes instead of instances

Example implementation:
```python
def compress_memory(event_repository, character_memory, compression_threshold):
    # Find old events eligible for compression
    old_events = [e for e in event_repository.get_all_events() 
                 if e.timestamp.game_turn < current_game_turn - compression_threshold]
    
    # Group events by type and proximity
    event_clusters = cluster_events_by_similarity(old_events)
    
    for cluster in event_clusters:
        if len(cluster) <= 1:
            continue  # No compression needed for single events
            
        if are_similar_combat_events(cluster):
            # Create a summary combat record
            summary = create_combat_summary(cluster)
            event_repository.add_event(summary)
            
            # Remove the individual events, but keep references
            for event in cluster:
                summary.references.append(event.event_id)
                event_repository.archive_event(event.event_id)
        
        elif are_exploration_events(cluster):
            # Summarize exploration into area knowledge
            area_knowledge = create_area_knowledge(cluster)
            character_memory.add_area_knowledge(area_knowledge)
            
            # Archive exploration events
            for event in cluster:
                event_repository.archive_event(event.event_id)
                
    # Extract recurring patterns into character traits
    recurring_behaviors = identify_recurring_behaviors(event_repository)
    for behavior in recurring_behaviors:
        if not character_memory.has_trait(behavior.trait_name):
            character_memory.add_character_trait(behavior.trait_name, 
                                               behavior.confidence,
                                               behavior.supporting_events)
```

## Persistence Implementation

### File-Based Storage
```javascript
// In the MCP server
const fs = require('fs');
const path = require('path');

// Base path for memory storage
const MEMORY_PATH = path.join(__dirname, '..', 'memory-bank', 'narrative-memory');

// Ensure directories exist
if (!fs.existsSync(MEMORY_PATH)) {
    fs.mkdirSync(MEMORY_PATH, { recursive: true });
}

// Character memory persistence
async function saveCharacterMemory(characterId, memoryData) {
    const charPath = path.join(MEMORY_PATH, 'characters');
    if (!fs.existsSync(charPath)) {
        fs.mkdirSync(charPath, { recursive: true });
    }
    
    const filePath = path.join(charPath, `${characterId}.json`);
    await fs.promises.writeFile(filePath, JSON.stringify(memoryData, null, 2), 'utf8');
    
    console.log(`Character memory saved for ${characterId}`);
}

// Event repository persistence
async function saveEventToRepository(event) {
    const eventsPath = path.join(MEMORY_PATH, 'events');
    if (!fs.existsSync(eventsPath)) {
        fs.mkdirSync(eventsPath, { recursive: true });
    }
    
    // Organize events by type for easier retrieval
    const typePath = path.join(eventsPath, event.event_type);
    if (!fs.existsSync(typePath)) {
        fs.mkdirSync(typePath);
    }
    
    const filePath = path.join(typePath, `${event.event_id}.json`);
    await fs.promises.writeFile(filePath, JSON.stringify(event, null, 2), 'utf8');
    
    // Also maintain an index for quick lookups
    await updateEventIndex(event);
    
    console.log(`Event saved: ${event.event_id} (${event.event_type})`);
}
```

### Database Storage (Alternative)
For larger implementations, a NoSQL document database like MongoDB can be used:

```javascript
// MongoDB implementation example
const { MongoClient } = require('mongodb');

const uri = process.env.MONGODB_URI || "mongodb://localhost:27017";
const client = new MongoClient(uri);

async function connectToDatabase() {
    await client.connect();
    return client.db("towerOfBabelNarrativeMemory");
}

async function saveEventToRepository(event) {
    try {
        const database = await connectToDatabase();
        const events = database.collection("events");
        
        // Add created timestamp if not present
        if (!event.system_metadata) {
            event.system_metadata = {
                created_at: new Date(),
                last_accessed: new Date()
            };
        }
        
        // Insert or update
        await events.updateOne(
            { event_id: event.event_id },
            { $set: event },
            { upsert: true }
        );
        
        console.log(`Event saved to database: ${event.event_id}`);
    } catch (error) {
        console.error("Error saving event to database:", error);
        throw error;
    }
}
```

## MCP Integration

### Memory-Aware Narrative Tools

The MCP server should expose memory-aware tools for generating narratives:

```javascript
// Example MCP tool definition
const memoryAwareNarrativeTools = [
    {
        name: 'generateEventNarrative',
        description: 'Generate a narrative for a game event with memory awareness',
        parameters: {
            type: 'object',
            properties: {
                eventType: {
                    type: 'string',
                    description: 'Type of event (monster_encounter, item_discovery, etc.)'
                },
                eventData: {
                    type: 'object',
                    description: 'Data specific to the event type'
                },
                characterId: {
                    type: 'string',
                    description: 'ID of the player character'
                },
                narrativeStyle: {
                    type: 'string',
                    enum: ['brief', 'standard', 'detailed'],
                    description: 'Desired length and detail level'
                },
                toneHint: {
                    type: 'string',
                    description: 'Suggested emotional tone for the narrative'
                }
            },
            required: ['eventType', 'eventData', 'characterId']
        },
        handler: async (params) => {
            // Load character memory
            const characterMemory = await loadCharacterMemory(params.characterId);
            
            // Select relevant past events
            const relevantEvents = await selectRelevantEvents(
                params.characterId, 
                params.eventType, 
                params.eventData
            );
            
            // Build context for Claude
            const context = buildNarrativeContext(characterMemory, relevantEvents, params);
            
            // Generate narrative with Claude
            const narrative = await generateWithClaude(context, params);
            
            // Create new event record
            const eventRecord = createEventRecord(
                params.eventType,
                params.eventData,
                narrative
            );
            
            // Save to repository
            await saveEventToRepository(eventRecord);
            
            // Update character memory if needed
            if (isSignificantEvent(params.eventType, params.eventData)) {
                await updateCharacterMemory(params.characterId, eventRecord);
            }
            
            return {
                narrative: narrative.text,
                tone: narrative.tone,
                eventId: eventRecord.event_id
            };
        }
    }
];
```

### Context Builder Function

```javascript
function buildNarrativeContext(characterMemory, relevantEvents, params) {
    // Start with character information
    let context = `# Character Information\n`;
    context += `Name: ${characterMemory.base_info.name}\n`;
    context += `Race: ${characterMemory.base_info.race}\n`;
    context += `Class: ${characterMemory.base_info.class}\n\n`;
    
    // Add defining character traits
    context += `## Character Traits\n`;
    for (const trait of characterMemory.narrative_identity.recurring_themes) {
        context += `- ${trait}\n`;
    }
    context += '\n';
    
    // Add relationship with Lute
    context += `## Relationship with Lute\n`;
    const luteRelationship = characterMemory.relationships.lute_the_bard;
    context += `Affinity: ${luteRelationship.affinity}/100\n`;
    context += `Arc: ${luteRelationship.relationship_arc}\n\n`;
    
    // Add relevant past events
    context += `# Relevant Past Events\n`;
    for (const event of relevantEvents) {
        context += `## ${formatEventTitle(event)}\n`;
        context += `${event.narrative_summary}\n\n`;
    }
    
    // Add current event details
    context += `# Current Event\n`;
    context += `Type: ${params.eventType}\n`;
    context += JSON.stringify(params.eventData, null, 2);
    context += '\n\n';
    
    // Add tone guidance
    if (params.toneHint) {
        context += `# Tone Guidance\n`;
        context += `Suggested tone: ${params.toneHint}\n\n`;
    }
    
    // Add narrative style guidance
    context += `# Narrative Style\n`;
    context += `Style: ${params.narrativeStyle || 'standard'}\n`;
    context += narrativeStyleGuidance(params.narrativeStyle);
    
    return context;
}
```

## Memory Visualization

To help debug and understand the narrative memory system:

```javascript
// MCP tool for visualizing character memory
const memoryVisualizationTool = {
    name: 'visualizeCharacterMemory',
    description: 'Generate a visualization of the character memory for debugging',
    parameters: {
        type: 'object',
        properties: {
            characterId: {
                type: 'string',
                description: 'ID of the character to visualize'
            },
            format: {
                type: 'string',
                enum: ['markdown', 'html', 'json'],
                description: 'Output format'
            }
        },
        required: ['characterId']
    },
    handler: async (params) => {
        const characterMemory = await loadCharacterMemory(params.characterId);
        const recentEvents = await loadRecentEvents(params.characterId, 10);
        
        let visualization;
        
        switch (params.format || 'markdown') {
            case 'html':
                visualization = generateHTMLVisualization(characterMemory, recentEvents);
                break;
            case 'json':
                visualization = JSON.stringify({characterMemory, recentEvents}, null, 2);
                break;
            case 'markdown':
            default:
                visualization = generateMarkdownVisualization(characterMemory, recentEvents);
                break;
        }
        
        return { visualization };
    }
};
```

## Performance Considerations

1. **Indexing**: Implement efficient indexing for quick event retrieval
2. **Caching**: Cache frequently accessed memory records
3. **Lazy Loading**: Only load detailed events when needed
4. **Background Processing**: Compress and organize memory during idle time
5. **Throttling**: Limit memory updates to prevent I/O bottlenecks

## Conclusion

A well-implemented narrative memory system creates the foundation for Lute the Bard to provide consistent, contextually rich storytelling that evolves with the player's journey. The layered approach to memory management ensures both performance and narrative depth, creating a more immersive Tower of Babel experience. 