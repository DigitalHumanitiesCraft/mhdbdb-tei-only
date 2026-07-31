/**
 * MHDBDB Playground - IndexedDB Manager
 *
 * Core IndexedDB wrapper for the playground's *only* persistent client data:
 * TEI files the user uploads themselves (object store `tei_files`).
 *
 * Deliberately NOT in here (#280): caches for the corpus and the authority
 * files. Those live in the shared `CorpusLoader` (Dexie database
 * `MHDBDBMainSite`, 30-day TTL plus version invalidation, see ADR-004 and
 * `assets/js/lib/corpus-loader.js`), which the playground uses as well. The
 * stores `corpus_tei_files`, `authority_files` and `metadata` predate that
 * loader, had no writer left, and are dropped on upgrade to DB version 3.
 * Do not reintroduce a second cache path here.
 */

export class IndexedDBManager {
    // Stores removed in v3; deleted from existing browser databases on upgrade.
    static OBSOLETE_STORES = ['corpus_tei_files', 'authority_files', 'metadata'];

    constructor() {
        this.dbName = 'MHDBDB_Playground';
        // v2 added the (never written) corpus store, v3 removes the three
        // writer-less stores again (#280).
        this.dbVersion = 3;
        this.db = null;
        this.isInitialized = false;
    }

    // ==================== DATABASE INITIALIZATION ====================

    async initialize() {
        if (this.isInitialized && this.db) {
            return true;
        }

        try {
            // Check IndexedDB support
            if (!window.indexedDB) {
                console.warn('⚠️ IndexedDB not supported, falling back to memory-only mode');
                return false;
            }

            this.db = await this.openDatabase();
            this.isInitialized = true;
            console.log('✅ IndexedDB initialized successfully');
            return true;
        } catch (error) {
            console.error('❌ Failed to initialize IndexedDB:', error);
            return false;
        }
    }

    openDatabase() {
        return new Promise((resolve, reject) => {
            const request = indexedDB.open(this.dbName, this.dbVersion);

            // onblocked can be followed by a late onsuccess once the blocking tab
            // goes away. The resolve is a no-op by then, so remember that we already
            // settled and close the connection nobody holds a reference to.
            let settled = false;

            request.onerror = () => {
                settled = true;
                reject(new Error(`IndexedDB open failed: ${request.error}`));
            };

            // Another tab still holds a connection on the older version, so the
            // upgrade cannot run. Without this handler the promise would stay
            // pending forever and every await on ensureInitialized() would hang
            // silently (#280). Reject instead: the caller reports "storage not
            // available" and the user can close the other tab and reload.
            request.onblocked = () => {
                console.warn('⚠️ IndexedDB upgrade blocked by another open tab: close it and reload the page');
                settled = true;
                reject(new Error('IndexedDB upgrade blocked by another open tab'));
            };

            request.onsuccess = () => {
                const db = request.result;

                if (settled) {
                    db.close();
                    return;
                }

                // Do not block a future version bump made in another tab.
                db.onversionchange = () => {
                    console.warn('⚠️ IndexedDB version change requested elsewhere: closing this connection');
                    db.close();
                    this.db = null;
                    this.isInitialized = false;
                };

                settled = true;
                resolve(db);
            };

            request.onupgradeneeded = (event) => {
                const db = event.target.result;

                // Create object store for TEI files (user uploads) — the only
                // store with a write path (saveTEIFile via data/storage/tei-storage.js)
                if (!db.objectStoreNames.contains('tei_files')) {
                    const teiStore = db.createObjectStore('tei_files', { keyPath: 'filename' });
                    teiStore.createIndex('timestamp', 'timestamp', { unique: false });
                    teiStore.createIndex('size', 'size', { unique: false });
                    teiStore.createIndex('source', 'source', { unique: false }); // Track source
                }

                // v3: drop the leftovers of the playground-local cache path that
                // predates the shared CorpusLoader (#280). `authority_files` did
                // have a writer until 3126c175c (authority-storage-manager.js), so
                // long-time users may still carry stale authority XML here; the
                // other two were never written to. Nothing is lost: the indexes
                // live in MHDBDBMainSite and are re-fetched on demand.
                for (const obsolete of IndexedDBManager.OBSOLETE_STORES) {
                    if (db.objectStoreNames.contains(obsolete)) {
                        db.deleteObjectStore(obsolete);
                        console.log(`🧹 Removed obsolete object store: ${obsolete}`);
                    }
                }

                console.log('📦 IndexedDB stores created/upgraded');
            };
        });
    }

    // ==================== TEI FILES OPERATIONS ====================

    async saveTEIFile(filename, content, metadata = {}) {
        await this.ensureInitialized();

        try {
            const transaction = this.db.transaction(['tei_files'], 'readwrite');
            const store = transaction.objectStore('tei_files');

            const fileData = {
                filename: filename,
                content: content,
                size: content.length,
                timestamp: Date.now(),
                type: 'tei',
                source: metadata.source || 'user-upload', // Default to user-upload
                ...metadata
            };

            await this.promisifyRequest(store.put(fileData));
            console.log(`✅ TEI file saved to IndexedDB: ${filename} (${(content.length / 1024).toFixed(1)} KB)`);
            return true;
        } catch (error) {
            console.error(`❌ Failed to save TEI file ${filename}:`, error);
            return false;
        }
    }

    async loadTEIFile(filename) {
        await this.ensureInitialized();

        try {
            const transaction = this.db.transaction(['tei_files'], 'readonly');
            const store = transaction.objectStore('tei_files');

            const result = await this.promisifyRequest(store.get(filename));

            if (result) {
                console.log(`📁 TEI file loaded from IndexedDB: ${filename}`);
                return result.content;
            }
            return null;
        } catch (error) {
            console.error(`❌ Failed to load TEI file ${filename}:`, error);
            return null;
        }
    }

    async removeTEIFile(filename) {
        await this.ensureInitialized();

        try {
            const transaction = this.db.transaction(['tei_files'], 'readwrite');
            const store = transaction.objectStore('tei_files');

            await this.promisifyRequest(store.delete(filename));
            console.log(`🗑️ TEI file removed from IndexedDB: ${filename}`);
            return true;
        } catch (error) {
            console.error(`❌ Failed to remove TEI file ${filename}:`, error);
            return false;
        }
    }

    async listTEIFiles() {
        await this.ensureInitialized();

        try {
            const transaction = this.db.transaction(['tei_files'], 'readonly');
            const store = transaction.objectStore('tei_files');

            const request = store.getAll();
            const files = await this.promisifyRequest(request);

            return files.map(file => ({
                filename: file.filename,
                size: file.size || 0,
                timestamp: file.timestamp || 0,
                isCachedFile: true // Mark as cached for UI
            })).sort((a, b) => b.timestamp - a.timestamp);
        } catch (error) {
            console.error('❌ Failed to list TEI files:', error);
            return [];
        }
    }

    async clearAllTEIFiles() {
        await this.ensureInitialized();

        try {
            const transaction = this.db.transaction(['tei_files'], 'readwrite');
            const store = transaction.objectStore('tei_files');

            const request = store.clear();
            await this.promisifyRequest(request);

            console.log('🧹 All TEI files cleared from IndexedDB');
            return true;
        } catch (error) {
            console.error('❌ Failed to clear TEI files:', error);
            return false;
        }
    }

    async clearTEIFiles() {
        await this.ensureInitialized();

        try {
            const transaction = this.db.transaction(['tei_files'], 'readwrite');
            const store = transaction.objectStore('tei_files');

            // Get count of files before clearing
            const countRequest = store.count();
            const count = await this.promisifyRequest(countRequest);

            // Clear all TEI files
            await this.promisifyRequest(store.clear());

            console.log(`🧹 Cleared ${count} TEI files from IndexedDB cache`);
            return count;
        } catch (error) {
            console.error('❌ Failed to clear TEI files:', error);
            return 0;
        }
    }

    // ==================== STORAGE INFORMATION ====================

    async getStorageEstimate() {
        try {
            if (navigator.storage && navigator.storage.estimate) {
                const estimate = await navigator.storage.estimate();
                return {
                    quota: estimate.quota || 0,
                    usage: estimate.usage || 0,
                    available: (estimate.quota || 0) - (estimate.usage || 0),
                    percentUsed: estimate.quota ? Math.round((estimate.usage / estimate.quota) * 100) : 0
                };
            }

            // Fallback for browsers without storage.estimate
            return {
                quota: 50 * 1024 * 1024, // Assume 50MB minimum
                usage: 0,
                available: 50 * 1024 * 1024,
                percentUsed: 0
            };
        } catch (error) {
            console.warn('⚠️ Could not estimate storage:', error);
            return {
                quota: 0,
                usage: 0,
                available: 0,
                percentUsed: 0
            };
        }
    }

    async getDatabaseSize() {
        await this.ensureInitialized();

        try {
            const teiFiles = await this.listTEIFiles();
            const teiSize = teiFiles.reduce((sum, file) => sum + (file.size || 0), 0);

            // tei_files is the only store in this database, so its size is the
            // whole database size (#280).
            return {
                teiFiles: {
                    count: teiFiles.length,
                    size: teiSize
                },
                total: {
                    count: teiFiles.length,
                    size: teiSize
                }
            };
        } catch (error) {
            console.error('❌ Failed to calculate database size:', error);
            return {
                teiFiles: { count: 0, size: 0 },
                total: { count: 0, size: 0 }
            };
        }
    }

    async getStorageQuotaInfo() {
        await this.ensureInitialized();

        try {
            const estimate = await this.getStorageEstimate();
            const dbSize = await this.getDatabaseSize();

            return {
                storageType: 'IndexedDB',
                quota: estimate.quota,
                usage: estimate.usage,
                used: estimate.usage, // Alias for backward compatibility
                available: estimate.available,
                estimatedQuota: estimate.quota, // Alias for backward compatibility
                percentUsed: estimate.percentUsed,
                dbSize: dbSize.total.size,
                teiFiles: dbSize.teiFiles
            };
        } catch (error) {
            console.error('❌ Failed to get storage quota info:', error);
            return {
                storageType: 'IndexedDB',
                quota: 0,
                usage: 0,
                used: 0,
                available: 0,
                estimatedQuota: 0,
                percentUsed: 0,
                dbSize: 0,
                teiFiles: { count: 0, size: 0 }
            };
        }
    }


    // ==================== UTILITY METHODS ====================

    async ensureInitialized() {
        if (!this.isInitialized) {
            await this.initialize();
        }
        if (!this.isInitialized) {
            throw new Error('IndexedDB not available');
        }
    }

    promisifyRequest(request) {
        return new Promise((resolve, reject) => {
            request.onsuccess = () => resolve(request.result);
            request.onerror = () => reject(request.error);
        });
    }

    formatFileSize(bytes) {
        if (bytes < 1024) return bytes + ' B';
        if (bytes < 1024 * 1024) return Math.round(bytes / 1024) + ' KB';
        return Math.round(bytes / 1024 / 1024 * 100) / 100 + ' MB';
    }

    // ==================== ERROR RECOVERY ====================

    async validateDatabase() {
        try {
            await this.ensureInitialized();

            // Test basic operations
            const testKey = 'validation_test';
            const testData = 'test_content';

            await this.saveTEIFile(testKey, testData);
            const retrieved = await this.loadTEIFile(testKey);
            await this.removeTEIFile(testKey);

            if (retrieved !== testData) {
                throw new Error('Database validation failed - data integrity issue');
            }

            console.log('✅ IndexedDB validation successful');
            return true;
        } catch (error) {
            console.error('❌ IndexedDB validation failed:', error);
            return false;
        }
    }
}