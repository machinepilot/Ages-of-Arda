const { expect } = require('chai');
const { startMockBrogueClient } = require('../mocks/brogue_client');
const { MCPServer } = require('../../services/core-service');

describe('MCP System Integration Tests', () => {
    let mockClient;
    let mcpServer;
    
    before(async () => {
        // Start MCP server in test mode
        mcpServer = new MCPServer({
            port: 8999,
            memoryPath: './test_memory',
            ollamaEndpoint: 'mock://ollama',
            testMode: true
        });
        await mcpServer.start();
        
        // Start mock client
        mockClient = await startMockBrogueClient({
            serverUrl: 'http://localhost:8999'
        });
    });
    
    after(async () => {
        await mockClient.stop();
        await mcpServer.stop();
    });
    
    it('should process monster encounter events', async () => {
        // Simulate monster encounter
        const response = await mockClient.sendEvent({
            type: 'MONSTER_ENCOUNTER',
            data: {
                monsterType: 'goblin',
                playerLevel: 3,
                firstEncounter: true,
                locationDesc: 'dark corridor'
            }
        });
        
        expect(response.status).to.equal('success');
        expect(response.narrative).to.be.a('string');
        expect(response.narrative.length).to.be.greaterThan(50);
    });
    
    // Additional test cases
    // ...
}); 