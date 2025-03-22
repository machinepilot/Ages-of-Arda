/**
 * Dynamically scores memory importance based on gameplay context
 */
function calculateMemoryPriority(memory, gameState) {
    let baseScore = memory.baseImportance || 0.5;
    
    // Adjust for recency (exponential decay)
    const ageInHours = (Date.now() - memory.timestamp) / (1000 * 60 * 60);
    const recencyScore = Math.exp(-0.05 * ageInHours);
    
    // Adjust for relevance to current context
    const contextRelevance = calculateContextualRelevance(memory, gameState);
    
    // Adjust for emotional impact/player engagement
    const emotionalImpact = memory.playerReaction ? 0.3 : 0;
    
    // Calculate final priority score
    return (baseScore * 0.3) + (recencyScore * 0.3) + (contextRelevance * 0.3) + (emotionalImpact * 0.1);
} 