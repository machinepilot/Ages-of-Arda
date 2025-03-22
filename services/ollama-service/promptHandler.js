// Optimized prompt handler with caching and streaming
async function generateResponse(context, playerState) {
    // Calculate hash of context for cache lookup
    const contextHash = hashContext(context);
    
    // Check cache for similar contexts
    if (responseCache.has(contextHash) && !isDynamicContext(context)) {
        return responseCache.get(contextHash);
    }
    
    // Prepare optimized prompt with specific instruction formatting
    const prompt = buildStructuredPrompt(context, playerState);
    
    // Stream response for real-time narration
    const stream = await fetchStreamingResponse(OLLAMA_ENDPOINT, {
        model: process.env.OLLAMA_MODEL || "llama3",
        prompt: prompt,
        temperature: parseFloat(process.env.TEMPERATURE || "0.7"),
        system: SYSTEM_PROMPTS.DUNGEON_MASTER,
        stream: true
    });
    
    // ... stream handling logic ...
} 