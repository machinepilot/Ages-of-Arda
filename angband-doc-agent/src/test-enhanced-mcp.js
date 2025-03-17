/**
 * Enhanced MCP Server Test Script
 * 
 * This script tests the enhanced MCP server by sending various companion queries
 * and displaying the responses.
 */

const axios = require('axios');

// Configuration
const config = {
    serverUrl: process.env.MCP_SERVER_URL || 'http://localhost:3000',
    testId: 'test-' + Date.now()
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
 * Test companion queries with different topics
 */
async function runTests() {
    console.log(`${colors.bright}${colors.blue}====== Ages of Arda - Enhanced MCP Server Tests ======${colors.reset}\n`);
    
    try {
        // First, check if the server is running
        console.log(`${colors.cyan}Checking server health...${colors.reset}`);
        const healthResponse = await axios.get(`${config.serverUrl}/health`);
        console.log(`${colors.green}Server is running! Response: ${healthResponse.data}${colors.reset}\n`);
        
        // Test both endpoints
        console.log(`${colors.bright}${colors.yellow}Testing /companion/query endpoint:${colors.reset}`);
        await testCompanionQueryEndpoint();
        
        console.log(`\n${colors.bright}${colors.yellow}Testing /companion/response endpoint (legacy):${colors.reset}`);
        await testCompanionResponseEndpoint();
        
        // Test different query topics
        console.log(`\n${colors.bright}${colors.yellow}Testing specific query topics:${colors.reset}`);
        await testGreetingQuery();
        await testLoreQuery();
        await testLocationQuery();
        await testCreatureQuery();
        await testItemQuery();
        
        console.log(`\n${colors.bright}${colors.green}All tests completed successfully!${colors.reset}`);
    } catch (error) {
        console.error(`${colors.red}Error running tests: ${error.message}${colors.reset}`);
        if (error.response) {
            console.error(`${colors.red}Server response: ${JSON.stringify(error.response.data, null, 2)}${colors.reset}`);
        }
    }
}

/**
 * Make a request to the MCP server
 */
async function makeQueryRequest(endpoint, query) {
    console.log(`${colors.dim}Sending to ${endpoint}: "${query}"${colors.reset}`);
    
    try {
        const response = await axios.post(`${config.serverUrl}${endpoint}`, { query });
        console.log(`${colors.green}Response: "${response.data.response}"${colors.reset}`);
        return response.data;
    } catch (error) {
        console.error(`${colors.red}Request failed: ${error.message}${colors.reset}`);
        throw error;
    }
}

/**
 * Test the main companion query endpoint
 */
async function testCompanionQueryEndpoint() {
    console.log(`${colors.cyan}Testing basic query functionality...${colors.reset}`);
    await makeQueryRequest('/companion/query', 'Hello, companion!');
}

/**
 * Test the legacy companion response endpoint
 */
async function testCompanionResponseEndpoint() {
    console.log(`${colors.cyan}Testing legacy endpoint compatibility...${colors.reset}`);
    await makeQueryRequest('/companion/response', 'Hello, companion!');
}

/**
 * Test greeting queries
 */
async function testGreetingQuery() {
    console.log(`${colors.cyan}Testing greeting queries...${colors.reset}`);
    await makeQueryRequest('/companion/query', 'Hello');
    await makeQueryRequest('/companion/query', 'Hi there');
    await makeQueryRequest('/companion/query', 'Greetings, friend');
}

/**
 * Test lore queries
 */
async function testLoreQuery() {
    console.log(`${colors.cyan}Testing lore queries...${colors.reset}`);
    await makeQueryRequest('/companion/query', 'Tell me about Middle-earth');
    await makeQueryRequest('/companion/query', 'What is Arda?');
    await makeQueryRequest('/companion/query', 'Who are the elves?');
}

/**
 * Test location queries
 */
async function testLocationQuery() {
    console.log(`${colors.cyan}Testing location queries...${colors.reset}`);
    await makeQueryRequest('/companion/query', 'Tell me about Mordor');
    await makeQueryRequest('/companion/query', 'What is Gondor?');
    await makeQueryRequest('/companion/query', 'Where is Rohan?');
}

/**
 * Test creature queries
 */
async function testCreatureQuery() {
    console.log(`${colors.cyan}Testing creature queries...${colors.reset}`);
    await makeQueryRequest('/companion/query', 'Tell me about hobbits');
    await makeQueryRequest('/companion/query', 'What are dwarves?');
    await makeQueryRequest('/companion/query', 'Who are the elves?');
}

/**
 * Test item queries
 */
async function testItemQuery() {
    console.log(`${colors.cyan}Testing item queries...${colors.reset}`);
    await makeQueryRequest('/companion/query', 'What is the One Ring?');
    await makeQueryRequest('/companion/query', 'Tell me about magical artifacts');
    await makeQueryRequest('/companion/query', 'What weapons are good against dragons?');
}

// Run the tests
runTests().catch(error => {
    console.error(`${colors.red}Unhandled error: ${error}${colors.reset}`);
    process.exit(1);
}); 