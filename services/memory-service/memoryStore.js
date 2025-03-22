class TransactionalMemoryStore {
    constructor(dbPath) {
        this.db = new Database(dbPath);
        this.transactionActive = false;
    }
    
    async beginTransaction() {
        if (this.transactionActive) {
            throw new Error("Transaction already active");
        }
        
        await this.db.run('BEGIN TRANSACTION');
        this.transactionActive = true;
    }
    
    async commit() {
        if (!this.transactionActive) {
            throw new Error("No active transaction");
        }
        
        await this.db.run('COMMIT');
        this.transactionActive = false;
    }
    
    async rollback() {
        if (!this.transactionActive) {
            return; // No transaction to rollback
        }
        
        await this.db.run('ROLLBACK');
        this.transactionActive = false;
    }
    
    async storeMemory(memoryObject) {
        const needsTransaction = !this.transactionActive;
        
        try {
            if (needsTransaction) await this.beginTransaction();
            
            // Store the memory with proper escaping and validation
            // ... implementation ...
            
            if (needsTransaction) await this.commit();
            return true;
        } catch (error) {
            if (needsTransaction && this.transactionActive) {
                await this.rollback();
            }
            throw error;
        }
    }
} 