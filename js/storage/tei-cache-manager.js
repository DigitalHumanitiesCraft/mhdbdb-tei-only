/**
 * TEI Cache Manager
 * Manages IndexedDB caching of parsed TEI XML DOMs
 *
 * Strategy: Cache serialized DOMs after first parse to dramatically
 * reduce repeat load times from 30-60s to 2-3s
 */

class TEICacheManager {
    constructor() {
        this.dbName = 'MHDBDB_TEI_Cache';
        this.dbVersion = 1;
        this.storeName = 'parsedTEI';
        this.cacheExpiration = 30 * 24 * 60 * 60 * 1000; // 30 days in ms
        this.db = null;
    }

    /**
     * Initialize IndexedDB
     */
    async init() {
        return new Promise((resolve, reject) => {
            const request = indexedDB.open(this.dbName, this.dbVersion);

            request.onerror = () => reject(request.error);
            request.onsuccess = () => {
                this.db = request.result;
                console.log('[TEICacheManager] Initialized');
                resolve();
            };

            request.onupgradeneeded = (event) => {
                const db = event.target.result;

                // Create object store if it doesn't exist
                if (!db.objectStoreNames.contains(this.storeName)) {
                    const store = db.createObjectStore(this.storeName, { keyPath: 'filename' });
                    store.createIndex('cachedAt', 'cachedAt', { unique: false });
                    console.log('[TEICacheManager] Created parsedTEI store');
                }
            };
        });
    }

    /**
     * Get cached TEI Document
     * @param {string} filename - TEI filename (e.g., "BAR.tei.xml")
     * @returns {Document|null} - Parsed XML Document or null if not cached/expired
     */
    async get(filename) {
        try {
            if (!this.db) await this.init();

            const transaction = this.db.transaction([this.storeName], 'readonly');
            const store = transaction.objectStore(this.storeName);

            return new Promise((resolve, reject) => {
                const request = store.get(filename);

                request.onsuccess = () => {
                    const cached = request.result;

                    if (!cached) {
                        console.log(`[TEICacheManager] Cache miss: ${filename}`);
                        resolve(null);
                        return;
                    }

                    // Check expiration
                    const age = Date.now() - cached.cachedAt;
                    if (age > this.cacheExpiration) {
                        console.log(`[TEICacheManager] Cache expired: ${filename} (${Math.round(age / (24 * 60 * 60 * 1000))} days old)`);
                        this.delete(filename); // Clean up expired entry
                        resolve(null);
                        return;
                    }

                    // Parse cached XML string back to Document
                    const parser = new DOMParser();
                    const doc = parser.parseFromString(cached.xmlString, 'text/xml');

                    // Check for parse errors
                    const parseError = doc.querySelector('parsererror');
                    if (parseError) {
                        console.error(`[TEICacheManager] Parse error in cached XML: ${filename}`);
                        this.delete(filename); // Remove corrupted cache
                        resolve(null);
                        return;
                    }

                    console.log(`[TEICacheManager] Cache hit: ${filename} (age: ${Math.round(age / (60 * 60 * 1000))}h)`);
                    resolve(doc);
                };

                request.onerror = () => {
                    console.error(`[TEICacheManager] Error reading cache: ${filename}`, request.error);
                    resolve(null); // Fail gracefully
                };
            });

        } catch (error) {
            console.error('[TEICacheManager] Get error:', error);
            return null;
        }
    }

    /**
     * Cache a TEI Document
     * @param {string} filename - TEI filename
     * @param {Document} doc - Parsed XML Document
     * @param {Object} metadata - Optional metadata (title, author, etc.)
     */
    async set(filename, doc, metadata = {}) {
        try {
            if (!this.db) await this.init();

            // Serialize Document to string
            const serializer = new XMLSerializer();
            const xmlString = serializer.serializeToString(doc);

            const cacheEntry = {
                filename,
                xmlString,
                cachedAt: Date.now(),
                size: xmlString.length,
                metadata
            };

            const transaction = this.db.transaction([this.storeName], 'readwrite');
            const store = transaction.objectStore(this.storeName);

            return new Promise((resolve, reject) => {
                const request = store.put(cacheEntry);

                request.onsuccess = () => {
                    console.log(`[TEICacheManager] Cached: ${filename} (${Math.round(xmlString.length / 1024)}KB)`);
                    resolve();
                };

                request.onerror = () => {
                    console.error(`[TEICacheManager] Cache write failed: ${filename}`, request.error);
                    reject(request.error);
                };
            });

        } catch (error) {
            console.error('[TEICacheManager] Set error:', error);
            throw error;
        }
    }

    /**
     * Delete cached entry
     * @param {string} filename - TEI filename
     */
    async delete(filename) {
        try {
            if (!this.db) await this.init();

            const transaction = this.db.transaction([this.storeName], 'readwrite');
            const store = transaction.objectStore(this.storeName);

            return new Promise((resolve) => {
                const request = store.delete(filename);

                request.onsuccess = () => {
                    console.log(`[TEICacheManager] Deleted: ${filename}`);
                    resolve();
                };

                request.onerror = () => {
                    console.error(`[TEICacheManager] Delete failed: ${filename}`, request.error);
                    resolve(); // Fail gracefully
                };
            });

        } catch (error) {
            console.error('[TEICacheManager] Delete error:', error);
        }
    }

    /**
     * Get cache statistics
     * @returns {Object} - Cache stats (count, totalSize, oldestEntry, newestEntry)
     */
    async getStats() {
        try {
            if (!this.db) await this.init();

            const transaction = this.db.transaction([this.storeName], 'readonly');
            const store = transaction.objectStore(this.storeName);

            return new Promise((resolve, reject) => {
                const request = store.getAll();

                request.onsuccess = () => {
                    const entries = request.result;

                    if (entries.length === 0) {
                        resolve({
                            count: 0,
                            totalSize: 0,
                            totalSizeMB: 0,
                            oldestEntry: null,
                            newestEntry: null
                        });
                        return;
                    }

                    const totalSize = entries.reduce((sum, entry) => sum + entry.size, 0);
                    const sortedByAge = entries.sort((a, b) => a.cachedAt - b.cachedAt);

                    resolve({
                        count: entries.length,
                        totalSize,
                        totalSizeMB: (totalSize / (1024 * 1024)).toFixed(2),
                        oldestEntry: sortedByAge[0].filename,
                        oldestAge: Math.round((Date.now() - sortedByAge[0].cachedAt) / (60 * 60 * 1000)),
                        newestEntry: sortedByAge[sortedByAge.length - 1].filename,
                        newestAge: Math.round((Date.now() - sortedByAge[sortedByAge.length - 1].cachedAt) / (60 * 60 * 1000))
                    });
                };

                request.onerror = () => reject(request.error);
            });

        } catch (error) {
            console.error('[TEICacheManager] Stats error:', error);
            return {
                count: 0,
                totalSize: 0,
                error: error.message
            };
        }
    }

    /**
     * Clear all cached entries
     */
    async clear() {
        try {
            if (!this.db) await this.init();

            const transaction = this.db.transaction([this.storeName], 'readwrite');
            const store = transaction.objectStore(this.storeName);

            return new Promise((resolve, reject) => {
                const request = store.clear();

                request.onsuccess = () => {
                    console.log('[TEICacheManager] Cache cleared');
                    resolve();
                };

                request.onerror = () => reject(request.error);
            });

        } catch (error) {
            console.error('[TEICacheManager] Clear error:', error);
            throw error;
        }
    }

    /**
     * Clean up expired entries
     */
    async cleanExpired() {
        try {
            if (!this.db) await this.init();

            const transaction = this.db.transaction([this.storeName], 'readwrite');
            const store = transaction.objectStore(this.storeName);

            return new Promise((resolve) => {
                const request = store.getAll();

                request.onsuccess = async () => {
                    const entries = request.result;
                    let deletedCount = 0;

                    for (const entry of entries) {
                        const age = Date.now() - entry.cachedAt;
                        if (age > this.cacheExpiration) {
                            await this.delete(entry.filename);
                            deletedCount++;
                        }
                    }

                    console.log(`[TEICacheManager] Cleaned ${deletedCount} expired entries`);
                    resolve(deletedCount);
                };

                request.onerror = () => resolve(0);
            });

        } catch (error) {
            console.error('[TEICacheManager] Clean error:', error);
            return 0;
        }
    }
}

export { TEICacheManager };
