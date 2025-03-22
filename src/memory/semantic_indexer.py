from sentence_transformers import SentenceTransformer
import numpy as np
import json
import os

class SemanticMemoryIndex:
    def __init__(self, model_name="all-MiniLM-L6-v2"):
        # Use lightweight embedding model for performance
        self.model = SentenceTransformer(model_name)
        self.memory_vectors = {}
        self.memory_content = {}
        
    def add_memory(self, memory_id, content):
        """Add memory with semantic embedding for fast retrieval"""
        # Generate embedding vector for memory content
        embedding = self.model.encode(content["description"])
        
        # Store normalized vector and content
        self.memory_vectors[memory_id] = embedding / np.linalg.norm(embedding)
        self.memory_content[memory_id] = content
        
    def find_relevant_memories(self, query, max_results=5, threshold=0.6):
        """Find memories relevant to the current game context"""
        # Encode query to same vector space
        query_vector = self.model.encode(query)
        query_vector = query_vector / np.linalg.norm(query_vector)
        
        # Calculate similarity scores
        similarities = {
            memory_id: np.dot(query_vector, memory_vector)
            for memory_id, memory_vector in self.memory_vectors.items()
        }
        
        # Return top matches above threshold
        relevant_memories = [
            (memory_id, self.memory_content[memory_id], score)
            for memory_id, score in similarities.items()
            if score > threshold
        ]
        
        return sorted(relevant_memories, key=lambda x: x[2], reverse=True)[:max_results] 