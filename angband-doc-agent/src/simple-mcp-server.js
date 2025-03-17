// Simple MCP Server for Ages of Arda
const express = require('express');
const fs = require('fs');
const path = require('path');
require('dotenv').config({ path: path.join(__dirname, '..', '.env') });

const app = express();
const PORT = process.env.PORT || 3000;
const SOURCE_PATH = process.env.SOURCE_PATH || '../src';

// Middleware to parse JSON
app.use(express.json());

// Log requests
app.use((req, res, next) => {
  console.log(`${new Date().toISOString()} - ${req.method} ${req.url}`);
  next();
});

// Basic health check endpoint
app.get('/health', (req, res) => {
  res.json({ status: 'ok', message: 'MCP Server is running' });
});

// Companion response endpoint
app.post('/companion/response', (req, res) => {
  try {
    const { context, query } = req.body;
    
    console.log('Received companion query:', query);
    console.log('Context:', JSON.stringify(context).substring(0, 200) + '...');
    
    // Generate a simple response based on the query
    let response;
    
    if (query.includes('hello') || query.includes('hi')) {
      response = "Greetings, adventurer! How may I assist you on your journey?";
    } else if (query.includes('help')) {
      response = "I am your faithful companion. I can provide advice, share lore, or simply keep you company on your adventures.";
    } else if (query.includes('lore') || query.includes('history')) {
      response = "The Ages of Arda are filled with wondrous tales and ancient wisdom. What specific lore interests you?";
    } else if (query.includes('quest') || query.includes('mission')) {
      response = "Your current quest seems perilous. Proceed with caution, but know that great rewards await the brave.";
    } else if (query.includes('weapon') || query.includes('sword') || query.includes('bow')) {
      response = "A warrior is only as good as their weapon. Choose wisely, for your life may depend on it.";
    } else if (query.includes('magic') || query.includes('spell')) {
      response = "The arcane arts are powerful but unpredictable. Master your spells before venturing into danger.";
    } else if (query.includes('monster') || query.includes('enemy') || query.includes('creature')) {
      response = "Many foul creatures lurk in the shadows. Learn their weaknesses, and you shall prevail.";
    } else if (query.includes('treasure') || query.includes('gold') || query.includes('wealth')) {
      response = "Riches beyond imagination await those who dare to delve deep into forgotten places.";
    } else if (query.includes('thank')) {
      response = "You're most welcome. It is my honor to serve.";
    } else {
      response = "I stand ready to assist you on your journey. What guidance do you seek?";
    }
    
    // Send the response
    res.json({ response });
    
  } catch (error) {
    console.error('Error processing companion response:', error);
    res.status(500).json({ error: 'Failed to process companion response' });
  }
});

// Start the server
app.listen(PORT, () => {
  console.log(`===================================================`);
  console.log(`MCP Server running on port ${PORT}`);
  console.log(`Source path: ${SOURCE_PATH}`);
  console.log(`===================================================`);
  console.log(`Server is ready to receive companion queries`);
  console.log(`Press Ctrl+C to stop the server`);
  console.log(`===================================================`);
}); 