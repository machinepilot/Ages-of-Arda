class LRUCache {
    constructor(maxSize = 100) {
        this.maxSize = maxSize;
        this.cache = new Map();
        this.keys = [];
    }
    
    get(key) {
        if (!this.cache.has(key)) return null;
        
        // Move to most recently used
        this.keys = this.keys.filter(k => k !== key);
        this.keys.push(key);
        
        return this.cache.get(key);
    }
    
    set(key, value) {
        if (this.cache.has(key)) {
            // Update existing key
            this.cache.set(key, value);
            this.keys = this.keys.filter(k => k !== key);
            this.keys.push(key);
        } else {
            if (this.keys.length >= this.maxSize) {
                const oldestKey = this.keys.shift();
                this.cache.delete(oldestKey);
            }
            this.cache.set(key, value);
            this.keys.push(key);
        }
    }
} 