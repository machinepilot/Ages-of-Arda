/**
 * MCP Server Test Script
 * 
 * This script tests the MCP server by sending various narrative generation requests
 * and printing the responses.
 */

const axios = require('axios');

// Configuration
const config = {
    serverUrl: process.env.MCP_SERVER_URL || 'http://localhost:3000',
    characterId: 'test-character-' + Date.now()
};

// ANSI colors for terminal output
const colors = {
    reset: '\x1b[0m',
    bright: '\x1b[1m',
    dim: '\x1b[2m',
    red: '\x1b[31m',
    green: '\x1b[32m',
    yellow: '\x1b[33m',
    blue: '\x1b[34m',
    magenta: '\x1b[35m',
    cyan: '\x1b[36m'
};

/**
 * Test narrative generation with different event types
 */
async function runTests() {
    console.log(`${colors.bright}${colors.blue}====== Lute the Bard - MCP Server Tests ======${colors.reset}\n`);
    
    try {
        // First, check if the server is running
        console.log(`${colors.cyan}Checking server health...${colors.reset}`);
        const healthResponse = await axios.get(`${config.serverUrl}/health`);
        console.log(`${colors.green}Server is running with provider: ${healthResponse.data.provider}, model: ${healthResponse.data.model}${colors.reset}\n`);
        
        // Test different narrative generation scenarios
        await testMonsterDeath();
        await testItemDiscovery();
        await testNewLevel();
        await testNearDeath();
        await testQuestComplete();
        await testLevelUp();
        
        // Test memory persistence
        await testMemoryRetrieval();
        
        console.log(`\n${colors.bright}${colors.green}All tests completed successfully!${colors.reset}`);
    } catch (error) {
        console.error(`${colors.red}Error running tests: ${error.message}${colors.reset}`);
        if (error.response) {
            console.error(`${colors.red}Server response: ${JSON.stringify(error.response.data, null, 2)}${colors.reset}`);
        }
    }
}

/**
 * Helper function to make an MCP request
 */
async function makeRequest(tool, params) {
    console.log(`${colors.cyan}Invoking tool: ${tool}${colors.reset}`);
    console.log(`${colors.dim}Parameters: ${JSON.stringify(params, null, 2)}${colors.reset}`);
    
    const response = await axios.post(`${config.serverUrl}/invoke`, {
        tool,
        params
    });
    
    console.log(`${colors.green}Response: ${JSON.stringify(response.data, null, 2)}${colors.reset}\n`);
    return response.data;
}

/**
 * Test monster death narrative
 */
async function testMonsterDeath() {
    console.log(`${colors.magenta}==== Testing Monster Death Narrative ====${colors.reset}`);
    
    const params = {
        event_type: 'monster_death',
        event_data: JSON.stringify({
            monster_name: 'Ancient Red Dragon',
            monster_level: 50,
            is_unique: true
        }),
        character_id: config.characterId,
        style: 'heroic',
        tone: 'triumphant',
        player_info: {
            name: 'Thorin',
            race: 'Dwarf',
            class: 'Warrior',
            level: 25
        }
    };
    
    return makeRequest('generate_narrative', params);
}

/**
 * Test item discovery narrative
 */
async function testItemDiscovery() {
    console.log(`${colors.magenta}==== Testing Item Discovery Narrative ====${colors.reset}`);
    
    const params = {
        event_type: 'item_discovery',
        event_data: JSON.stringify({
            item_name: 'Glamdring, the Foe-hammer',
            is_artifact: true,
            item_type: 'sword'
        }),
        character_id: config.characterId,
        style: 'fantasy',
        tone: 'mystical',
        player_info: {
            name: 'Thorin',
            race: 'Dwarf',
            class: 'Warrior',
            level: 25
        }
    };
    
    return makeRequest('generate_narrative', params);
}

/**
 * Test new level narrative
 */
async function testNewLevel() {
    console.log(`${colors.magenta}==== Testing New Level Narrative ====${colors.reset}`);
    
    const params = {
        event_type: 'new_level',
        event_data: JSON.stringify({
            dungeon_level: 40,
            level_feeling: 'menacing'
        }),
        character_id: config.characterId,
        style: 'dark',
        tone: 'foreboding',
        player_info: {
            name: 'Thorin',
            race: 'Dwarf',
            class: 'Warrior',
            level: 25
        }
    };
    
    return makeRequest('generate_narrative', params);
}

/**
 * Test near death narrative
 */
async function testNearDeath() {
    console.log(`${colors.magenta}==== Testing Near Death Narrative ====${colors.reset}`);
    
    const params = {
        event_type: 'near_death',
        event_data: JSON.stringify({
            hp_percent: 5,
            enemy_name: 'Balrog of Morgoth'
        }),
        character_id: config.characterId,
        style: 'dramatic',
        tone: 'tense',
        player_info: {
            name: 'Thorin',
            race: 'Dwarf',
            class: 'Warrior',
            level: 25
        }
    };
    
    return makeRequest('generate_narrative', params);
}

/**
 * Test quest complete narrative
 */
async function testQuestComplete() {
    console.log(`${colors.magenta}==== Testing Quest Complete Narrative ====${colors.reset}`);
    
    const params = {
        event_type: 'quest_complete',
        event_data: JSON.stringify({
            quest_name: 'Defeat the Witch-king',
            quest_level: 30
        }),
        character_id: config.characterId,
        style: 'epic',
        tone: 'triumphant',
        player_info: {
            name: 'Thorin',
            race: 'Dwarf',
            class: 'Warrior',
            level: 25
        }
    };
    
    return makeRequest('generate_narrative', params);
}

/**
 * Test level up narrative
 */
async function testLevelUp() {
    console.log(`${colors.magenta}==== Testing Level Up Narrative ====${colors.reset}`);
    
    const params = {
        event_type: 'level_up',
        event_data: JSON.stringify({
            new_level: 26,
            class: 'Warrior'
        }),
        character_id: config.characterId,
        style: 'celebratory',
        tone: 'proud',
        player_info: {
            name: 'Thorin',
            race: 'Dwarf',
            class: 'Warrior',
            level: 25
        }
    };
    
    return makeRequest('generate_narrative', params);
}

/**
 * Test memory retrieval
 */
async function testMemoryRetrieval() {
    console.log(`${colors.magenta}==== Testing Memory Retrieval ====${colors.reset}`);
    
    const params = {
        character_id: config.characterId,
        query_type: 'events',
        query_params: {
            top: 3
        }
    };
    
    return makeRequest('query_memory', params);
}

// Run the tests
runTests().catch(err => {
    console.error(`${colors.red}Unhandled error: ${err.message}${colors.reset}`);
    process.exit(1);
}); 