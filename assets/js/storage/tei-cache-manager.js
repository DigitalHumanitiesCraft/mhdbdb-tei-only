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
        this.cacheExpiration = 30 * 24 * 60 * 60 * 1000; // 30 days in ms (storage hygiene, cleanExpired läuft bei init)
        this.fetchTimeout = 15000; // ms — stalled connections fall back to cache instead of hanging
        this.revalidated = new Set(); // filenames already revalidated this page load
        this.db = null;
    }

    /**
     * Initialize IndexedDB
     */
    async init() {
        await new Promise((resolve, reject) => {
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

        // Storage hygiene in the background: purge entries not refreshed in 30 days
        // (orphans of renamed/removed TEI files — the active-ingest corpus has those)
        this.cleanExpired().catch(err =>
            console.warn('[TEICacheManager] cleanExpired failed:', err)
        );
    }

    /**
     * Load a TEI Document, revalidating any cached copy against the server (#151)
     *
     * Sends a conditional GET (If-None-Match / If-Modified-Since): unchanged
     * files cost one 304 roundtrip instead of a multi-MB download, changed
     * files are re-fetched immediately. Each file is revalidated at most once
     * per page load; later loads in the same session are pure cache hits.
     * Falls back to the cached copy when the network or the server fails.
     * @param {string} filename - TEI filename (e.g., "BAR.tei.xml")
     * @returns {Document} - Parsed XML Document
     */
    async load(filename) {
        const cached = await this.getEntry(filename);

        // Already revalidated this page load → serve from cache without network
        if (cached && this.revalidated.has(filename)) {
            const doc = this.parseCachedEntry(cached);
            if (doc) {
                console.log(`[TEICacheManager] Session cache hit: ${filename}`);
                return doc;
            }
        }

        const headers = {};
        if (cached && cached.etag) headers['If-None-Match'] = cached.etag;
        if (cached && cached.lastModified) headers['If-Modified-Since'] = cached.lastModified;

        let response;
        try {
            // cache: 'no-cache' forces revalidation with the server instead of
            // a silent browser-HTTP-cache hit (GitHub Pages serves max-age=600)
            response = await fetch(`tei/${filename}`, {
                cache: 'no-cache',
                headers,
                signal: AbortSignal.timeout(this.fetchTimeout)
            });
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
                this.revalidated.add(filename);
                this.touch(cached); // keep cachedAt fresh so cleanExpired spares live entries
                return doc;
            }
            // Cached copy unusable despite 304 (parseCachedEntry deleted it) —
            // restart: without an entry this is a plain full fetch with fallback logic
            return this.load(filename);
        }

        if (!response.ok) {
            const fallback = cached ? this.parseCachedEntry(cached) : null;
            if (fallback) {
                console.warn(`[TEICacheManager] HTTP ${response.status}, serving cached copy: ${filename}`);
                return fallback;
            }
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }

        const xmlString = await response.text();
        const parser = new DOMParser();
        const doc = parser.parseFromString(xmlString, 'text/xml');
        if (doc.querySelector('parsererror')) {
            // e.g. captive portal answering 200 with an HTML login page
            const fallback = cached ? this.parseCachedEntry(cached) : null;
            if (fallback) {
                console.warn(`[TEICacheManager] Response not parseable, serving cached copy: ${filename}`);
                return fallback;
            }
            throw new Error(`XML parsing failed: ${filename}`);
        }

        console.log(`[TEICacheManager] Fetched from network: ${filename} (${Math.round(xmlString.length / 1024)}KB)`);
        this.revalidated.add(filename);

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
     * Refresh an entry's cachedAt after successful revalidation (fire-and-forget)
     * so cleanExpired() only purges entries that were truly unused for 30 days.
     * @param {Object} cached - Cache entry from getEntry()
     */
    touch(cached) {
        this.set(cached.filename, cached.xmlString, {
            etag: cached.etag || null,
            lastModified: cached.lastModified || null
        }).catch(err =>
            console.warn(`[TEICacheManager] touch failed: ${cached.filename}`, err)
        );
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
     * Clean up expired entries (runs in the background at init).
     * Cursor over the cachedAt index instead of getAll(), so the multi-MB
     * xmlStrings are never materialized just to check their age.
     */
    async cleanExpired() {
        if (!this.db) return 0; // called from init() after open; no-op otherwise

        const cutoff = Date.now() - this.cacheExpiration;
        const transaction = this.db.transaction([this.storeName], 'readwrite');
        const index = transaction.objectStore(this.storeName).index('cachedAt');
        const range = IDBKeyRange.upperBound(cutoff);

        return new Promise((resolve) => {
            let deletedCount = 0;
            const request = index.openCursor(range);

            request.onsuccess = () => {
                const cursor = request.result;
                if (cursor) {
                    cursor.delete();
                    deletedCount++;
                    cursor.continue();
                } else {
                    if (deletedCount > 0) {
                        console.log(`[TEICacheManager] Cleaned ${deletedCount} expired entries`);
                    }
                    resolve(deletedCount);
                }
            };

            request.onerror = () => resolve(0);
        });
    }
}

export { TEICacheManager };
