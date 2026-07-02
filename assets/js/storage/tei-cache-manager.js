/**
 * TEI Cache Manager
 * Manages IndexedDB caching of TEI XML sources
 *
 * Strategy: Cache the raw XML string after first download to skip the
 * multi-MB transfer on repeat loads. Every load() revalidates against the
 * server via conditional GET (ETag / Last-Modified), so corpus updates
 * become visible on the next page load instead of after the 30-day TTL (#151).
 */

class TEICacheManager {
    constructor() {
        this.dbName = 'MHDBDB_TEI_Cache';
        this.dbVersion = 1;
        this.storeName = 'parsedTEI';
        this.cacheExpiration = 30 * 24 * 60 * 60 * 1000; // 30 days in ms (storage hygiene only, see cleanExpired)
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
     * Load a TEI Document, revalidating any cached copy against the server (#151)
     *
     * Sends a conditional GET (If-None-Match / If-Modified-Since): unchanged
     * files cost one 304 roundtrip instead of a multi-MB download, changed
     * files are re-fetched immediately. Falls back to the cached copy when
     * the network is unavailable.
     * @param {string} filename - TEI filename (e.g., "BAR.tei.xml")
     * @returns {Document} - Parsed XML Document
     */
    async load(filename) {
        const cached = await this.getEntry(filename);

        const headers = {};
        if (cached && cached.etag) headers['If-None-Match'] = cached.etag;
        if (cached && cached.lastModified) headers['If-Modified-Since'] = cached.lastModified;

        let response;
        try {
            // cache: 'no-cache' forces revalidation with the server instead of
            // a silent browser-HTTP-cache hit (GitHub Pages serves max-age=600)
            response = await fetch(`tei/${filename}`, { cache: 'no-cache', headers });
        } catch (networkError) {
            const fallback = cached ? this.parseCachedEntry(cached) : null;
            if (fallback) {
                console.warn(`[TEICacheManager] Network unavailable, serving cached copy: ${filename}`);
                return fallback;
            }
            throw networkError;
        }

        if (response.status === 304) {
            const doc = cached ? this.parseCachedEntry(cached) : null;
            if (doc) {
                console.log(`[TEICacheManager] Revalidated (304): ${filename}`);
                return doc;
            }
            // Cached copy unusable despite 304 → force full download
            response = await fetch(`tei/${filename}`, { cache: 'reload' });
        }

        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }

        const xmlString = await response.text();
        const parser = new DOMParser();
        const doc = parser.parseFromString(xmlString, 'text/xml');
        if (doc.querySelector('parsererror')) {
            throw new Error(`XML parsing failed: ${filename}`);
        }

        console.log(`[TEICacheManager] Fetched from network: ${filename} (${Math.round(xmlString.length / 1024)}KB)`);

        // Cache for next time (don't wait)
        this.set(filename, xmlString, {
            etag: response.headers.get('ETag'),
            lastModified: response.headers.get('Last-Modified')
        }).catch(err =>
            console.error(`[TEICacheManager] Cache write failed: ${filename}`, err)
        );

        return doc;
    }

    /**
     * Read the raw cache entry (xmlString + validators), no freshness decision
     * @param {string} filename - TEI filename
     * @returns {Object|null} - Cache entry or null
     */
    async getEntry(filename) {
        try {
            if (!this.db) await this.init();

            const transaction = this.db.transaction([this.storeName], 'readonly');
            const store = transaction.objectStore(this.storeName);

            return new Promise((resolve) => {
                const request = store.get(filename);
                request.onsuccess = () => resolve(request.result || null);
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
     * Parse a cache entry's XML string; deletes the entry if corrupted
     * @param {Object} cached - Cache entry from getEntry()
     * @returns {Document|null} - Parsed XML Document or null if corrupted
     */
    parseCachedEntry(cached) {
        const parser = new DOMParser();
        const doc = parser.parseFromString(cached.xmlString, 'text/xml');

        if (doc.querySelector('parsererror')) {
            console.error(`[TEICacheManager] Parse error in cached XML: ${cached.filename}`);
            this.delete(cached.filename); // Remove corrupted cache
            return null;
        }

        return doc;
    }

    /**
     * Cache a TEI XML source with its HTTP validators
     * @param {string} filename - TEI filename
     * @param {string} xmlString - Raw XML source as delivered by the server
     * @param {Object} validators - HTTP validators ({ etag, lastModified })
     */
    async set(filename, xmlString, { etag = null, lastModified = null } = {}) {
        try {
            if (!this.db) await this.init();

            const cacheEntry = {
                filename,
                xmlString,
                etag,
                lastModified,
                cachedAt: Date.now(),
                size: xmlString.length
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
