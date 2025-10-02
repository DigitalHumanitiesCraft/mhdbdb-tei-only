/**
 * MHDBDB - IndexedDB Base Class
 * Shared IndexedDB utilities for both main site and playground
 */

export class IndexedDBBase {
    constructor(dbName, version, storeConfigs) {
        this.dbName = dbName;
        this.dbVersion = version;
        this.storeConfigs = storeConfigs; // Array of {name, keyPath, indexes}
        this.db = null;
        this.isInitialized = false;
    }

    async initialize() {
        if (this.isInitialized && this.db) {
            return true;
        }

        try {
            if (!window.indexedDB) {
                console.warn('⚠️ IndexedDB not supported, falling back to memory-only mode');
                return false;
            }

            this.db = await this.openDatabase();
            this.isInitialized = true;
            return true;
        } catch (error) {
            console.error('❌ Failed to initialize IndexedDB:', error);
            return false;
        }
    }

    openDatabase() {
        return new Promise((resolve, reject) => {
            const request = indexedDB.open(this.dbName, this.dbVersion);

            request.onerror = () => {
                reject(new Error(`IndexedDB open failed: ${request.error}`));
            };

            request.onsuccess = () => {
                resolve(request.result);
            };

            request.onupgradeneeded = (event) => {
                const db = event.target.result;

                // Create stores based on config
                this.storeConfigs.forEach(config => {
                    if (!db.objectStoreNames.contains(config.name)) {
                        const store = db.createObjectStore(config.name, { keyPath: config.keyPath });

                        // Create indexes if specified
                        if (config.indexes) {
                            config.indexes.forEach(index => {
                                store.createIndex(index.name, index.keyPath, index.options || {});
                            });
                        }

                        if (config.logMessage) {
                            console.log(config.logMessage);
                        }
                    }
                });

                console.log('📦 IndexedDB stores created/upgraded');
            };
        });
    }

    async ensureInitialized() {
        if (!this.isInitialized) {
            await this.initialize();
        }
        if (!this.db) {
            throw new Error('IndexedDB not initialized');
        }
    }

    // ==================== GENERIC CRUD OPERATIONS ====================

    async get(storeName, key) {
        await this.ensureInitialized();

        return new Promise((resolve, reject) => {
            const transaction = this.db.transaction([storeName], 'readonly');
            const store = transaction.objectStore(storeName);
            const request = store.get(key);

            request.onsuccess = () => resolve(request.result);
            request.onerror = () => reject(request.error);
        });
    }

    async put(storeName, data) {
        await this.ensureInitialized();

        return new Promise((resolve, reject) => {
            const transaction = this.db.transaction([storeName], 'readwrite');
            const store = transaction.objectStore(storeName);
            const request = store.put(data);

            request.onsuccess = () => resolve(request.result);
            request.onerror = () => reject(request.error);
        });
    }

    async delete(storeName, key) {
        await this.ensureInitialized();

        return new Promise((resolve, reject) => {
            const transaction = this.db.transaction([storeName], 'readwrite');
            const store = transaction.objectStore(storeName);
            const request = store.delete(key);

            request.onsuccess = () => resolve();
            request.onerror = () => reject(request.error);
        });
    }

    async getAll(storeName) {
        await this.ensureInitialized();

        return new Promise((resolve, reject) => {
            const transaction = this.db.transaction([storeName], 'readonly');
            const store = transaction.objectStore(storeName);
            const request = store.getAll();

            request.onsuccess = () => resolve(request.result);
            request.onerror = () => reject(request.error);
        });
    }

    async clear(storeName) {
        await this.ensureInitialized();

        return new Promise((resolve, reject) => {
            const transaction = this.db.transaction([storeName], 'readwrite');
            const store = transaction.objectStore(storeName);
            const request = store.clear();

            request.onsuccess = () => resolve();
            request.onerror = () => reject(request.error);
        });
    }

    async count(storeName) {
        await this.ensureInitialized();

        return new Promise((resolve, reject) => {
            const transaction = this.db.transaction([storeName], 'readonly');
            const store = transaction.objectStore(storeName);
            const request = store.count();

            request.onsuccess = () => resolve(request.result);
            request.onerror = () => reject(request.error);
        });
    }

    async getAllKeys(storeName) {
        await this.ensureInitialized();

        return new Promise((resolve, reject) => {
            const transaction = this.db.transaction([storeName], 'readonly');
            const store = transaction.objectStore(storeName);
            const request = store.getAllKeys();

            request.onsuccess = () => resolve(request.result);
            request.onerror = () => reject(request.error);
        });
    }

    // ==================== INDEX QUERIES ====================

    async getByIndex(storeName, indexName, value) {
        await this.ensureInitialized();

        return new Promise((resolve, reject) => {
            const transaction = this.db.transaction([storeName], 'readonly');
            const store = transaction.objectStore(storeName);
            const index = store.index(indexName);
            const request = index.get(value);

            request.onsuccess = () => resolve(request.result);
            request.onerror = () => reject(request.error);
        });
    }

    async getAllByIndex(storeName, indexName, value) {
        await this.ensureInitialized();

        return new Promise((resolve, reject) => {
            const transaction = this.db.transaction([storeName], 'readonly');
            const store = transaction.objectStore(storeName);
            const index = store.index(indexName);
            const request = index.getAll(value);

            request.onsuccess = () => resolve(request.result);
            request.onerror = () => reject(request.error);
        });
    }
}
