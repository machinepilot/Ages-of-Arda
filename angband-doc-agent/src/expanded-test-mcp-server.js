/**
 * Expanded MCP Server Test Script
 * 
 * This script tests the MCP server with an expanded set of narrative generation requests
 * and saves the responses to a file for offline reference.
 */

const axios = require('axios');
const fs = require('fs');
const path = require('path');

// Configuration
const config = {
    serverUrl: process.env.MCP_SERVER_URL || 'http://localhost:3000',
    characterId: 'test-character-' + Date.now(),
    outputFile: path.join(__dirname, 'mcp-test-results.md')
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

// Store all test results for output to file
const testResults = [];

/**
 * Test narrative generation with different event types
 */
async function runTests() {
    console.log(`${colors.bright}${colors.blue}====== Lute the Bard - Expanded MCP Server Tests ======${colors.reset}\n`);
    
    try {
        // First, check if the server is running
        console.log(`${colors.cyan}Checking server health...${colors.reset}`);
        const healthResponse = await axios.get(`${config.serverUrl}/health`);
        console.log(`${colors.green}Server is running with provider: ${healthResponse.data.provider}, model: ${healthResponse.data.model}${colors.reset}\n`);
        
        testResults.push(`# Lute the Bard - MCP Test Results\n\n`);
        testResults.push(`**Server Status:** Running with provider: ${healthResponse.data.provider}, model: ${healthResponse.data.model}\n\n`);
        testResults.push(`**Test Date:** ${new Date().toLocaleString()}\n\n`);
        testResults.push(`**Character ID:** ${config.characterId}\n\n`);
        testResults.push(`## Test Results\n\n`);
        
        // Original tests
        await testMonsterDeath('Ancient Red Dragon', 50, true, 'heroic', 'triumphant');
        await testItemDiscovery('Glamdring, the Foe-hammer', true, 'sword', 'fantasy', 'mystical');
        await testNewLevel(40, 'menacing', 'dark', 'foreboding');
        await testNearDeath(5, 'Balrog of Morgoth', 'dramatic', 'tense');
        await testQuestComplete('Defeat the Witch-king', 30, 'epic', 'triumphant');
        await testLevelUp(26, 'Warrior', 'celebratory', 'proud');
        
        // Additional tests
        await testMonsterDeath('Shelob', 35, true, 'dark', 'relieved');
        await testItemDiscovery('Mithril Coat of Celebrimbor', true, 'armor', 'mythic', 'reverent');
        await testNewLevel(50, 'haunted', 'poetic', 'mysterious');
        await testNearDeath(1, 'Sauron the Deceiver', 'minimalist', 'desperate');
        await testQuestComplete('Recover the Arkenstone', 40, 'heroic', 'nostalgic');
        await testLevelUp(30, 'Warrior', 'fantasy', 'reflective');
        
        // Test with different player character
        const originalCharacterId = config.characterId;
        config.characterId = 'test-character-elf-' + Date.now();
        
        testResults.push(`\n## Tests with Elven Character\n\n`);
        testResults.push(`**Character ID:** ${config.characterId}\n\n`);
        
        // Elven character tests
        await testMonsterDeath('Glaurung, Father of Dragons', 60, true, 'poetic', 'sorrowful', {
            name: 'Legolas',
            race: 'Elf',
            class: 'Ranger',
            level: 28
        });
        await testItemDiscovery('Bow of Galadriel', true, 'bow', 'fantasy', 'reverent', {
            name: 'Legolas',
            race: 'Elf',
            class: 'Ranger',
            level: 28
        });
        
        // Restore original character ID
        config.characterId = originalCharacterId;
        
        // Test memory retrieval
        await testMemoryRetrieval();
        
        // Save results to file
        fs.writeFileSync(config.outputFile, testResults.join(''));
        console.log(`\n${colors.bright}${colors.green}All tests completed successfully!${colors.reset}`);
        console.log(`${colors.bright}${colors.blue}Results saved to: ${config.outputFile}${colors.reset}`);
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
async function testMonsterDeath(monsterName, monsterLevel, isUnique, style, tone, playerInfo = {}) {
    console.log(`${colors.magenta}==== Testing Monster Death Narrative: ${monsterName} ====${colors.reset}`);
    
    const defaultPlayerInfo = {
        name: 'Thorin',
        race: 'Dwarf',
        class: 'Warrior',
        level: 25
    };
    
    const params = {
        event_type: 'monster_death',
        event_data: JSON.stringify({
            monster_name: monsterName,
            monster_level: monsterLevel,
            is_unique: isUnique
        }),
        character_id: config.characterId,
        style: style,
        tone: tone,
        player_info: { ...defaultPlayerInfo, ...playerInfo }
    };
    
    const result = await makeRequest('generate_narrative', params);
    
    testResults.push(`### Monster Death: ${monsterName}\n\n`);
    testResults.push(`**Style:** ${style}, **Tone:** ${tone}\n\n`);
    testResults.push(`**Character:** ${params.player_info.name} the ${params.player_info.race} ${params.player_info.class} (Level ${params.player_info.level})\n\n`);
    testResults.push(`**Narrative:**\n\n${result.narrative}\n\n`);
    testResults.push(`**Is Spoken:** ${result.is_spoken}, **Importance:** ${result.importance}\n\n`);
    testResults.push(`---\n\n`);
    
    return result;
}

/**
 * Test item discovery narrative
 */
async function testItemDiscovery(itemName, isArtifact, itemType, style, tone, playerInfo = {}) {
    console.log(`${colors.magenta}==== Testing Item Discovery Narrative: ${itemName} ====${colors.reset}`);
    
    const defaultPlayerInfo = {
        name: 'Thorin',
        race: 'Dwarf',
        class: 'Warrior',
        level: 25
    };
    
    const params = {
        event_type: 'item_discovery',
        event_data: JSON.stringify({
            item_name: itemName,
            is_artifact: isArtifact,
            item_type: itemType
        }),
        character_id: config.characterId,
        style: style,
        tone: tone,
        player_info: { ...defaultPlayerInfo, ...playerInfo }
    };
    
    const result = await makeRequest('generate_narrative', params);
    
    testResults.push(`### Item Discovery: ${itemName}\n\n`);
    testResults.push(`**Style:** ${style}, **Tone:** ${tone}\n\n`);
    testResults.push(`**Character:** ${params.player_info.name} the ${params.player_info.race} ${params.player_info.class} (Level ${params.player_info.level})\n\n`);
    testResults.push(`**Narrative:**\n\n${result.narrative}\n\n`);
    testResults.push(`**Is Spoken:** ${result.is_spoken}, **Importance:** ${result.importance}\n\n`);
    testResults.push(`---\n\n`);
    
    return result;
}

/**
 * Test new level narrative
 */
async function testNewLevel(dungeonLevel, levelFeeling, style, tone, playerInfo = {}) {
    console.log(`${colors.magenta}==== Testing New Level Narrative: Level ${dungeonLevel} ====${colors.reset}`);
    
    const defaultPlayerInfo = {
        name: 'Thorin',
        race: 'Dwarf',
        class: 'Warrior',
        level: 25
    };
    
    const params = {
        event_type: 'new_level',
        event_data: JSON.stringify({
            dungeon_level: dungeonLevel,
            level_feeling: levelFeeling
        }),
        character_id: config.characterId,
        style: style,
        tone: tone,
        player_info: { ...defaultPlayerInfo, ...playerInfo }
    };
    
    const result = await makeRequest('generate_narrative', params);
    
    testResults.push(`### New Level: ${dungeonLevel} (${levelFeeling})\n\n`);
    testResults.push(`**Style:** ${style}, **Tone:** ${tone}\n\n`);
    testResults.push(`**Character:** ${params.player_info.name} the ${params.player_info.race} ${params.player_info.class} (Level ${params.player_info.level})\n\n`);
    testResults.push(`**Narrative:**\n\n${result.narrative}\n\n`);
    testResults.push(`**Is Spoken:** ${result.is_spoken}, **Importance:** ${result.importance}\n\n`);
    testResults.push(`---\n\n`);
    
    return result;
}

/**
 * Test near death narrative
 */
async function testNearDeath(hpPercent, enemyName, style, tone, playerInfo = {}) {
    console.log(`${colors.magenta}==== Testing Near Death Narrative: ${enemyName} ====${colors.reset}`);
    
    const defaultPlayerInfo = {
        name: 'Thorin',
        race: 'Dwarf',
        class: 'Warrior',
        level: 25
    };
    
    const params = {
        event_type: 'near_death',
        event_data: JSON.stringify({
            hp_percent: hpPercent,
            enemy_name: enemyName
        }),
        character_id: config.characterId,
        style: style,
        tone: tone,
        player_info: { ...defaultPlayerInfo, ...playerInfo }
    };
    
    const result = await makeRequest('generate_narrative', params);
    
    testResults.push(`### Near Death: ${enemyName}\n\n`);
    testResults.push(`**Style:** ${style}, **Tone:** ${tone}\n\n`);
    testResults.push(`**Character:** ${params.player_info.name} the ${params.player_info.race} ${params.player_info.class} (Level ${params.player_info.level})\n\n`);
    testResults.push(`**Narrative:**\n\n${result.narrative}\n\n`);
    testResults.push(`**Is Spoken:** ${result.is_spoken}, **Importance:** ${result.importance}\n\n`);
    testResults.push(`---\n\n`);
    
    return result;
}

/**
 * Test quest complete narrative
 */
async function testQuestComplete(questName, questLevel, style, tone, playerInfo = {}) {
    console.log(`${colors.magenta}==== Testing Quest Complete Narrative: ${questName} ====${colors.reset}`);
    
    const defaultPlayerInfo = {
        name: 'Thorin',
        race: 'Dwarf',
        class: 'Warrior',
        level: 25
    };
    
    const params = {
        event_type: 'quest_complete',
        event_data: JSON.stringify({
            quest_name: questName,
            quest_level: questLevel
        }),
        character_id: config.characterId,
        style: style,
        tone: tone,
        player_info: { ...defaultPlayerInfo, ...playerInfo }
    };
    
    const result = await makeRequest('generate_narrative', params);
    
    testResults.push(`### Quest Complete: ${questName}\n\n`);
    testResults.push(`**Style:** ${style}, **Tone:** ${tone}\n\n`);
    testResults.push(`**Character:** ${params.player_info.name} the ${params.player_info.race} ${params.player_info.class} (Level ${params.player_info.level})\n\n`);
    testResults.push(`**Narrative:**\n\n${result.narrative}\n\n`);
    testResults.push(`**Is Spoken:** ${result.is_spoken}, **Importance:** ${result.importance}\n\n`);
    testResults.push(`---\n\n`);
    
    return result;
}

/**
 * Test level up narrative
 */
async function testLevelUp(newLevel, characterClass, style, tone, playerInfo = {}) {
    console.log(`${colors.magenta}==== Testing Level Up Narrative: Level ${newLevel} ====${colors.reset}`);
    
    const defaultPlayerInfo = {
        name: 'Thorin',
        race: 'Dwarf',
        class: 'Warrior',
        level: newLevel - 1
    };
    
    const params = {
        event_type: 'level_up',
        event_data: JSON.stringify({
            new_level: newLevel,
            class: characterClass
        }),
        character_id: config.characterId,
        style: style,
        tone: tone,
        player_info: { ...defaultPlayerInfo, ...playerInfo }
    };
    
    const result = await makeRequest('generate_narrative', params);
    
    testResults.push(`### Level Up: ${newLevel}\n\n`);
    testResults.push(`**Style:** ${style}, **Tone:** ${tone}\n\n`);
    testResults.push(`**Character:** ${params.player_info.name} the ${params.player_info.race} ${params.player_info.class} (Level ${params.player_info.level})\n\n`);
    testResults.push(`**Narrative:**\n\n${result.narrative}\n\n`);
    testResults.push(`**Is Spoken:** ${result.is_spoken}, **Importance:** ${result.importance}\n\n`);
    testResults.push(`---\n\n`);
    
    return result;
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
            top: 5
        }
    };
    
    const result = await makeRequest('query_memory', params);
    
    testResults.push(`### Memory Retrieval\n\n`);
    testResults.push(`**Top 5 Memories:**\n\n`);
    
    if (result.memories && result.memories.length > 0) {
        result.memories.forEach((memory, index) => {
            testResults.push(`#### Memory ${index + 1}: ${memory.event_type}\n\n`);
            testResults.push(`**Timestamp:** ${new Date(memory.timestamp).toLocaleString()}\n\n`);
            testResults.push(`**Details:** ${JSON.stringify(memory.details)}\n\n`);
            testResults.push(`**Narrative:**\n\n${memory.narrative}\n\n`);
            testResults.push(`**Importance:** ${memory.importance}\n\n`);
        });
    } else {
        testResults.push(`No memories found.\n\n`);
    }
    
    return result;
}

// Run the tests
runTests(); 