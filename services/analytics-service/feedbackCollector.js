class PlayerFeedbackAnalyzer {
    constructor(database) {
        this.db = database;
    }
    
    /**
     * Track implicit feedback through player actions after narrative events
     */
    async recordImplicitFeedback(playerId, narrativeId, playerActions) {
        // Calculate engagement score
        const engagementScore = this.calculateEngagementScore(playerActions);
        
        // Record feedback
        await this.db.query(
            'INSERT INTO narrative_feedback (player_id, narrative_id, engagement_score, actions_json) VALUES (?, ?, ?, ?)',
            [playerId, narrativeId, engagementScore, JSON.stringify(playerActions)]
        );
        
        // Update narrative effectiveness score
        await this.updateNarrativeEffectiveness(narrativeId, engagementScore);
        
        return engagementScore;
    }
    
    /**
     * Calculate how engaged the player was with the narrative
     * based on their subsequent actions
     */
    calculateEngagementScore(playerActions) {
        // Analyze time spent reading (pause after narrative)
        const readingTime = playerActions.pauseDurationMs || 0;
        const readingScore = Math.min(readingTime / 3000, 1.0) * 0.4;
        
        // Analyze if player followed narrative suggestions
        const suggestedActionScore = playerActions.followedSuggestion ? 0.3 : 0;
        
        // Analyze player excitement (rapid inputs/actions after narrative)
        const actionDensity = calculateActionDensity(playerActions.subsequentActions);
        const excitementScore = Math.min(actionDensity / 5, 1.0) * 0.3;
        
        return readingScore + suggestedActionScore + excitementScore;
    }
} 