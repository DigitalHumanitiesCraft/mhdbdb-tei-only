/**
 * MHDBDB Playground - IndexedDB Manager
 * Core IndexedDB wrapper with async operations for TEI and Authority files
 */

export class IndexedDBManager {
    constructor() {
        this.dbName = 'MHDBDB_Playground';
        this.dbVersion = 2; // Bumped to 2 for corpus support
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

            request.onerror = () => {
                reject(new Error(`IndexedDB open failed: ${request.error}`));
            };

            request.onsuccess = () => {
                resolve(request.result);
            };

            request.onupgradeneeded = (event) => {
                const db = event.target.result;

                // Create object store for TEI files (user uploads)
                if (!db.objectStoreNames.contains('tei_files')) {
                    const teiStore = db.createObjectStore('tei_files', { keyPath: 'filename' });
                    teiStore.createIndex('timestamp', 'timestamp', { unique: false });
                    teiStore.createIndex('size', 'size', { unique: false });
                    teiStore.createIndex('source', 'source', { unique: false }); // NEW: Track source
                }

                // Create object store for Corpus TEI files (pre-loaded 667 files)
                if (!db.objectStoreNames.contains('corpus_tei_files')) {
                    const corpusStore = db.createObjectStore('corpus_tei_files', { keyPath: 'filename' });
                    corpusStore.createIndex('timestamp', 'timestamp', { unique: false });
                    corpusStore.createIndex('size', 'size', { unique: false });
                    corpusStore.createIndex('sigle', 'metadata.sigle', { unique: false });
                    corpusStore.createIndex('author', 'metadata.author', { unique: false });
                    corpusStore.createIndex('title', 'metadata.title', { unique: false });
                    console.log('📦 Created corpus_tei_files store for 667 pre-loaded texts');
                }

                // Create object store for Authority files
                if (!db.objectStoreNames.contains('authority_files')) {
                    const authStore = db.createObjectStore('authority_files', { keyPath: 'filename' });
                    authStore.createIndex('timestamp', 'timestamp', { unique: false });
                    authStore.createIndex('expires', 'expires', { unique: false });
                }

                // Create object store for metadata
                if (!db.objectStoreNames.contains('metadata')) {
                    db.createObjectStore('metadata', { keyPath: 'key' });
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

    // ==================== AUTHORITY FILES OPERATIONS ====================

    async saveAuthorityFile(filename, content, expirationHours = 24) {
        await this.ensureInitialized();

        try {
            const transaction = this.db.transaction(['authority_files'], 'readwrite');
            const store = transaction.objectStore('authority_files');

            const fileData = {
                filename: filename,
                content: content,
                size: content.length,
                timestamp: Date.now(),
                expires: Date.now() + (expirationHours * 60 * 60 * 1000),
                type: 'authority'
            };

            await this.promisifyRequest(store.put(fileData));
            console.log(`✅ Authority file cached: ${filename} (${(content.length / 1024).toFixed(1)} KB, expires in ${expirationHours}h)`);
            return true;
        } catch (error) {
            console.error(`❌ Failed to cache authority file ${filename}:`, error);
            return false;
        }
    }

    async loadAuthorityFile(filename) {
        await this.ensureInitialized();

        try {
            const transaction = this.db.transaction(['authority_files'], 'readonly');
            const store = transaction.objectStore('authority_files');

            const result = await this.promisifyRequest(store.get(filename));

            if (result) {
                // Check if expired
                if (Date.now() > result.expires) {
                    console.log(`⏰ Authority file expired: ${filename}, removing from cache`);
                    await this.removeAuthorityFile(filename);
                    return null;
                }

                console.log(`📁 Authority file loaded from cache: ${filename}`);
                return result.content;
            }
            return null;
        } catch (error) {
            console.error(`❌ Failed to load authority file ${filename}:`, error);
            return null;
        }
    }

    async removeAuthorityFile(filename) {
        await this.ensureInitialized();

        try {
            const transaction = this.db.transaction(['authority_files'], 'readwrite');
            const store = transaction.objectStore('authority_files');

            await this.promisifyRequest(store.delete(filename));
            console.log(`🗑️ Authority file removed from cache: ${filename}`);
            return true;
        } catch (error) {
            console.error(`❌ Failed to remove authority file ${filename}:`, error);
            return false;
        }
    }

    async clearExpiredAuthorityFiles() {
        await this.ensureInitialized();

        try {
            const transaction = this.db.transaction(['authority_files'], 'readwrite');
            const store = transaction.objectStore('authority_files');
            const index = store.index('expires');

            // Get all expired files
            const range = IDBKeyRange.upperBound(Date.now());
            const request = index.openCursor(range);

            let removedCount = 0;

            await new Promise((resolve, reject) => {
                request.onsuccess = (event) => {
                    const cursor = event.target.result;
                    if (cursor) {
                        cursor.delete();
                        removedCount++;
                        cursor.continue();
                    } else {
                        resolve();
                    }
                };
                request.onerror = () => reject(request.error);
            });

            if (removedCount > 0) {
                console.log(`🧹 Removed ${removedCount} expired authority files`);
            }
            return removedCount;
        } catch (error) {
            console.error('❌ Failed to clear expired authority files:', error);
            return 0;
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

    async clearAllCaches() {
        await this.ensureInitialized();

        try {
            const transaction = this.db.transaction(['tei_files', 'authority_files'], 'readwrite');

            // Clear TEI files
            const teiStore = transaction.objectStore('tei_files');
            const teiCount = await this.promisifyRequest(teiStore.count());
            await this.promisifyRequest(teiStore.clear());

            // Clear authority files
            const authorityStore = transaction.objectStore('authority_files');
            const authorityCount = await this.promisifyRequest(authorityStore.count());
            await this.promisifyRequest(authorityStore.clear());

            const totalCount = teiCount + authorityCount;
            console.log(`🧹 Cleared all caches: ${teiCount} TEI files + ${authorityCount} authority files = ${totalCount} total`);
            return { tei: teiCount, authority: authorityCount, total: totalCount };
        } catch (error) {
            console.error('❌ Failed to clear all caches:', error);
            return { tei: 0, authority: 0, total: 0 };
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

            // Get authority files count and size
            const transaction = this.db.transaction(['authority_files'], 'readonly');
            const store = transaction.objectStore('authority_files');
            const authorityFiles = await this.promisifyRequest(store.getAll());
            const authoritySize = authorityFiles.reduce((sum, file) => sum + (file.size || 0), 0);

            return {
                teiFiles: {
                    count: teiFiles.length,
                    size: teiSize
                },
                authorityFiles: {
                    count: authorityFiles.length,
                    size: authoritySize
                },
                total: {
                    count: teiFiles.length + authorityFiles.length,
                    size: teiSize + authoritySize
                }
            };
        } catch (error) {
            console.error('❌ Failed to calculate database size:', error);
            return {
                teiFiles: { count: 0, size: 0 },
                authorityFiles: { count: 0, size: 0 },
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
                teiFiles: dbSize.teiFiles,
                authorityFiles: dbSize.authorityFiles
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
                teiFiles: { count: 0, size: 0 },
                authorityFiles: { count: 0, size: 0 }
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

    // ==================== CORPUS TEI FILES OPERATIONS ====================

    async saveCorpusFile(filename, content, metadata = {}) {
        await this.ensureInitialized();

        try {
            const transaction = this.db.transaction(['corpus_tei_files'], 'readwrite');
            const store = transaction.objectStore('corpus_tei_files');

            const fileData = {
                filename: filename,
                content: content,
                size: content.length,
                timestamp: Date.now(),
                metadata: {
                    sigle: metadata.sigle || '',
                    title: metadata.title || '',
                    author: metadata.author || '',
                    authorRef: metadata.authorRef || '',
                    workRef: metadata.workRef || ''
                },
                source: 'corpus'
            };

            await this.promisifyRequest(store.put(fileData));
            console.log(`✅ Corpus file saved: ${filename} (${(content.length / 1024).toFixed(1)} KB)`);
            return true;
        } catch (error) {
            console.error(`❌ Failed to save corpus file ${filename}:`, error);
            return false;
        }
    }

    async loadCorpusFile(filename) {
        await this.ensureInitialized();

        try {
            const transaction = this.db.transaction(['corpus_tei_files'], 'readonly');
            const store = transaction.objectStore('corpus_tei_files');

            const result = await this.promisifyRequest(store.get(filename));

            if (result) {
                console.log(`📁 Corpus file loaded: ${filename}`);
                return result.content;
            }
            return null;
        } catch (error) {
            console.error(`❌ Failed to load corpus file ${filename}:`, error);
            return null;
        }
    }

    async listCorpusFiles() {
        await this.ensureInitialized();

        try {
            const transaction = this.db.transaction(['corpus_tei_files'], 'readonly');
            const store = transaction.objectStore('corpus_tei_files');

            const files = await this.promisifyRequest(store.getAll());

            return files.map(file => ({
                filename: file.filename,
                size: file.size || 0,
                timestamp: file.timestamp || 0,
                sigle: file.metadata?.sigle || '',
                title: file.metadata?.title || '',
                author: file.metadata?.author || '',
                authorRef: file.metadata?.authorRef || '',
                workRef: file.metadata?.workRef || ''
            })).sort((a, b) => (a.sigle || '').localeCompare(b.sigle || ''));
        } catch (error) {
            console.error('❌ Failed to list corpus files:', error);
            return [];
        }
    }

    async isCorpusLoaded() {
        await this.ensureInitialized();

        try {
            const transaction = this.db.transaction(['corpus_tei_files'], 'readonly');
            const store = transaction.objectStore('corpus_tei_files');
            const count = await this.promisifyRequest(store.count());

            console.log(`📊 Corpus status: ${count}/667 files loaded`);
            return count === 667;
        } catch (error) {
            console.error('❌ Failed to check corpus status:', error);
            return false;
        }
    }

    async getCorpusCount() {
        await this.ensureInitialized();

        try {
            const transaction = this.db.transaction(['corpus_tei_files'], 'readonly');
            const store = transaction.objectStore('corpus_tei_files');
            return await this.promisifyRequest(store.count());
        } catch (error) {
            console.error('❌ Failed to get corpus count:', error);
            return 0;
        }
    }

    async copyCorpusToPlayground(filename) {
        await this.ensureInitialized();

        try {
            const transaction = this.db.transaction(['corpus_tei_files', 'tei_files'], 'readwrite');

            // Read from corpus
            const corpusStore = transaction.objectStore('corpus_tei_files');
            const corpusFile = await this.promisifyRequest(corpusStore.get(filename));

            if (!corpusFile) {
                throw new Error(`Corpus file not found: ${filename}`);
            }

            // Write to playground with source marker
            const teiStore = transaction.objectStore('tei_files');
            const playgroundFile = {
                filename: corpusFile.filename,
                content: corpusFile.content,
                size: corpusFile.size,
                timestamp: Date.now(),  // Update timestamp
                type: 'tei',
                source: 'corpus-copy',  // Mark as copied from corpus
                metadata: corpusFile.metadata  // Preserve metadata
            };

            await this.promisifyRequest(teiStore.put(playgroundFile));
            console.log(`✅ Copied corpus file to playground: ${filename}`);
            return true;
        } catch (error) {
            console.error(`❌ Failed to copy corpus file ${filename}:`, error);
            return false;
        }
    }

    async copyAllCorpusToPlayground(progressCallback) {
        await this.ensureInitialized();

        try {
            const corpusFiles = await this.listCorpusFiles();
            let copiedCount = 0;

            for (const file of corpusFiles) {
                const success = await this.copyCorpusToPlayground(file.filename);
                if (success) {
                    copiedCount++;

                    if (progressCallback) {
                        progressCallback(copiedCount, corpusFiles.length);
                    }
                }
            }

            console.log(`✅ Copied ${copiedCount} corpus files to playground`);
            return copiedCount;
        } catch (error) {
            console.error('❌ Failed to copy corpus to playground:', error);
            return 0;
        }
    }

    async clearCorpusFiles() {
        await this.ensureInitialized();

        try {
            const transaction = this.db.transaction(['corpus_tei_files'], 'readwrite');
            const store = transaction.objectStore('corpus_tei_files');

            const countRequest = store.count();
            const count = await this.promisifyRequest(countRequest);

            await this.promisifyRequest(store.clear());

            console.log(`🧹 Cleared ${count} corpus files from IndexedDB`);
            return count;
        } catch (error) {
            console.error('❌ Failed to clear corpus files:', error);
            return 0;
        }
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

            // Clean up expired authority files
            await this.clearExpiredAuthorityFiles();

            console.log('✅ IndexedDB validation successful');
            return true;
        } catch (error) {
            console.error('❌ IndexedDB validation failed:', error);
            return false;
        }
    }
}