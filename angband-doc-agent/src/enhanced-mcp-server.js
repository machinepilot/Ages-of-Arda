/**
 * Enhanced MCP Server for Ages of Arda
 * 
 * This server implements a simplified Model Context Protocol (MCP) for the Ages of Arda,
 * providing companion responses with a clean implementation.
 */

const express = require('express');
const fs = require('fs');
const path = require('path');
require('dotenv').config({ path: path.join(__dirname, '..', '.env') });

// Initialize the server
const app = express();
app.use(express.json());

// Configuration
const config = {
    port: process.env.PORT || 3000,
    sourcePath: process.env.SOURCE_PATH || '../src',
};

// Memory storage for responses
const responseHistory = [];

// Log requests for debugging
app.use((req, res, next) => {
    console.log(`${new Date().toISOString()} - ${req.method} ${req.url}`);
    next();
});

// Health check endpoint
app.get('/health', (req, res) => {
    res.status(200).send('MCP Server is running');
});

// Companion response endpoint
app.post('/companion/query', (req, res) => {
    try {
        const query = req.body.query;
        console.log(`Received query: ${query}`);
        
        // Generate a simple response based on the query
        let response;
        
        if (query.toLowerCase().includes('hello') || query.toLowerCase().includes('hi')) {
            response = "Greetings, adventurer! How may I assist you on your journey through Middle-earth?";
        } else if (query.toLowerCase().includes('help')) {
            response = "I can provide information about Middle-earth, offer tactical advice, or simply chat with you during your adventures.";
        } else if (query.toLowerCase().includes('middle-earth') || query.toLowerCase().includes('arda')) {
            response = "Arda, the world where Middle-earth exists, was created by Eru Ilúvatar and shaped by the Ainur. It has a rich history spanning many ages.";
        } else if (query.toLowerCase().includes('mordor')) {
            response = "Mordor lies to the east of Gondor and is surrounded by mountain ranges on three sides, creating a natural fortress. It is the realm of the Dark Lord Sauron.";
        } else if (query.toLowerCase().includes('gondor')) {
            response = "Gondor was founded by the Númenórean brothers Isildur and Anárion. It is a proud kingdom of Men, though its glory has diminished over the ages.";
        } else if (query.toLowerCase().includes('rohan')) {
            response = "Rohan, home of the Rohirrim, is known for its skilled horsemen and vast grasslands. They are staunch allies of Gondor.";
        } else if (query.toLowerCase().includes('hobbit') || query.toLowerCase().includes('shire')) {
            response = "Hobbits are a peaceful folk who dwell in the Shire, preferring comfort and good food to adventures. Yet, they have shown remarkable resilience when called upon.";
        } else if (query.toLowerCase().includes('ring') || query.toLowerCase().includes('one ring')) {
            response = "The One Ring was forged by Sauron to control the other Rings of Power. It corrupts all who wield it, save perhaps the most pure of heart.";
        } else if (query.toLowerCase().includes('dwarf') || query.toLowerCase().includes('dwarves')) {
            response = "The Dwarves, created by Aulë, are master craftsmen and miners who dwell in great halls beneath the mountains. They are known for their stubbornness and courage.";
        } else if (query.toLowerCase().includes('elf') || query.toLowerCase().includes('elves')) {
            response = "The Elves, the Firstborn of Ilúvatar, are immortal beings of great beauty and wisdom. Many have departed Middle-earth for the Undying Lands across the sea.";
        } else {
            response = "I'm your faithful companion on this journey through the Ages of Arda. What would you like to know about this world?";
        }
        
        // Store the interaction
        responseHistory.push({ query, response, timestamp: new Date() });
        
        // Keep only the last 50 interactions
        if (responseHistory.length > 50) {
            responseHistory.shift();
        }
        
        // Send the response
        res.status(200).json({ response });
    } catch (error) {
        console.error('Error processing query:', error);
        res.status(500).json({ error: 'Failed to process query' });
    }
});

// Also handle the original endpoint path for backward compatibility
app.post('/companion/response', (req, res) => {
    try {
        // Extract query from request body, handling both formats
        const query = req.body.query || (req.body.context && req.body.query ? req.body.query : "Hello");
        console.log(`Received query on legacy endpoint: ${query}`);
        
        // Process the query the same way as the primary endpoint
        let response = "Greetings, adventurer! I'm your companion on this journey.";
        
        // Basic responses for common queries
        if (query.toLowerCase().includes('hello') || query.toLowerCase().includes('hi')) {
            response = "Well met, traveler! How may I assist you on your quest?";
        }
        
        // Store the interaction
        responseHistory.push({ query, response, timestamp: new Date(), legacy: true });
        
        // Keep only the last 50 interactions
        if (responseHistory.length > 50) {
            responseHistory.shift();
        }
        
        // Send the response
        res.status(200).json({ response });
    } catch (error) {
        console.error('Error processing query on legacy endpoint:', error);
        res.status(500).json({ 
            error: 'Failed to process query',
            response: "I apologize, but I seem to be having trouble understanding you."
        });
    }
});

// Start the server with error handling
const PORT = config.port;
const server = app.listen(PORT, () => {
    console.log(`===================================================`);
    console.log(`Enhanced MCP Server running on port ${PORT}`);
    console.log(`Source path: ${config.sourcePath}`);
    console.log(`===================================================`);
    console.log(`Server is ready to receive companion queries`);
    console.log(`Health check: http://localhost:${PORT}/health`);
    console.log(`Press Ctrl+C to stop the server`);
    console.log(`===================================================`);
}).on('error', (err) => {
    if (err.code === 'EADDRINUSE') {
        console.error(`Error: Port ${PORT} is already in use.`);
        console.error('Please update the PORT value in the .env file or close the application using this port.');
        console.error('You can find the process using this port with the command: netstat -ano | findstr :' + PORT);
        process.exit(1);
    } else {
        console.error('Server error:', err);
        process.exit(1);
    }
});
