/**
 * MHDBDB Playground - Authority Files Storage Manager
 * Handles caching of authority files using IndexedDB for improved performance
 */

import { IndexedDBManager } from './indexed-db-manager.js';

export class AuthorityStorageManager {
    constructor() {
        this.indexedDBManager = new IndexedDBManager();
        this.isInitialized = false;
        this.initPromise = null;

        // Cache expiration settings
        this.defaultExpirationHours = 24; // Authority files expire after 24 hours
        this.maxRetries = 3;

        // Network fetch settings
        this.fetchTimeout = 30000; // 30 seconds
    }

    // ==================== INITIALIZATION ====================

    async initialize() {
        if (this.initPromise) {
            return this.initPromise;
        }

        this.initPromise = this._doInitialize();
        return this.initPromise;
    }

    async _doInitialize() {
        try {
            this.isInitialized = await this.indexedDBManager.initialize();

            if (this.isInitialized) {
                // Clean expired files on initialization
                await this.indexedDBManager.clearExpiredAuthorityFiles();
                console.log('🔧 Authority storage initialized with IndexedDB');
            } else {
                console.log('🔧 Authority storage initialized (memory-only mode)');
            }

            return this.isInitialized;
        } catch (error) {
            console.error('❌ Authority storage initialization failed:', error);
            this.isInitialized = false;
            return false;
        }
    }

    // ==================== AUTHORITY FILE OPERATIONS ====================

    async loadAuthorityFile(filename, basePath = '../authority-files/') {
        await this.initialize();

        try {
            // First, try to load from cache
            let content = null;

            if (this.isInitialized) {
                content = await this.indexedDBManager.loadAuthorityFile(filename);
                if (content) {
                    console.log(`📁 Authority file loaded from cache: ${filename}`);
                    return {
                        content: content,
                        cached: true,
                        source: 'IndexedDB'
                    };
                }
            }

            // If not cached or cache disabled, fetch from network
            console.log(`🌐 Fetching authority file from network: ${filename}`);
            content = await this.fetchWithRetry(`${basePath}${filename}`);

            // Cache the fetched content if IndexedDB is available
            if (this.isInitialized && content) {
                const cached = await this.indexedDBManager.saveAuthorityFile(
                    filename,
                    content,
                    this.defaultExpirationHours
                );

                if (cached) {
                    console.log(`💾 Authority file cached: ${filename}`);
                }
            }

            return {
                content: content,
                cached: false,
                source: 'Network'
            };

        } catch (error) {
            console.error(`❌ Failed to load authority file ${filename}:`, error);
            throw error;
        }
    }

    async fetchWithRetry(url, retryCount = 0) {
        try {
            // Create abort controller for timeout
            const controller = new AbortController();
            const timeoutId = setTimeout(() => controller.abort(), this.fetchTimeout);

            const response = await fetch(url, {
                signal: controller.signal
            });

            clearTimeout(timeoutId);

            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }

            const content = await response.text();

            // Basic validation - ensure it's XML
            if (!content.trim().startsWith('<?xml') && !content.trim().startsWith('<')) {
                throw new Error('Invalid XML content received');
            }

            return content;

        } catch (error) {
            if (retryCount < this.maxRetries) {
                const delay = Math.pow(2, retryCount) * 1000; // Exponential backoff
                console.warn(`⚠️ Fetch failed, retrying in ${delay}ms (attempt ${retryCount + 1}/${this.maxRetries + 1}):`, error.message);

                await new Promise(resolve => setTimeout(resolve, delay));
                return this.fetchWithRetry(url, retryCount + 1);
            }

            throw error;
        }
    }

    // ==================== CACHE MANAGEMENT ====================

    async getCacheStatus() {
        await this.initialize();

        if (!this.isInitialized) {
            return {
                available: false,
                reason: 'IndexedDB not available',
                files: []
            };
        }

        try {
            const transaction = this.indexedDBManager.db.transaction(['authority_files'], 'readonly');
            const store = transaction.objectStore('authority_files');
            const request = store.getAll();

            const files = await this.indexedDBManager.promisifyRequest(request);
            const now = Date.now();

            const cacheInfo = files.map(file => ({
                filename: file.filename,
                size: file.size,
                cached: new Date(file.timestamp).toISOString(),
                expires: new Date(file.expires).toISOString(),
                expired: now > file.expires,
                ageHours: Math.round((now - file.timestamp) / (1000 * 60 * 60))
            }));

            return {
                available: true,
                files: cacheInfo,
                totalSize: files.reduce((sum, f) => sum + (f.size || 0), 0),
                expiredCount: cacheInfo.filter(f => f.expired).length
            };

        } catch (error) {
            console.error('❌ Failed to get cache status:', error);
            return {
                available: false,
                reason: error.message,
                files: []
            };
        }
    }

    async clearCache() {
        await this.initialize();

        if (!this.isInitialized) {
            return false;
        }

        try {
            const transaction = this.indexedDBManager.db.transaction(['authority_files'], 'readwrite');
            const store = transaction.objectStore('authority_files');

            await this.indexedDBManager.promisifyRequest(store.clear());
            console.log('🧹 Authority files cache cleared');
            return true;

        } catch (error) {
            console.error('❌ Failed to clear authority cache:', error);
            return false;
        }
    }

    async clearExpired() {
        await this.initialize();

        if (!this.isInitialized) {
            return 0;
        }

        return await this.indexedDBManager.clearExpiredAuthorityFiles();
    }

    async removeCachedFile(filename) {
        await this.initialize();

        if (!this.isInitialized) {
            return false;
        }

        return await this.indexedDBManager.removeAuthorityFile(filename);
    }

    // ==================== VALIDATION UTILITIES ====================

    validateXMLContent(content, filename) {
        try {
            const parser = new DOMParser();
            const xmlDoc = parser.parseFromString(content, 'text/xml');

            const parseError = xmlDoc.querySelector('parsererror');
            if (parseError) {
                throw new Error(`XML Parse Error in ${filename}: ${parseError.textContent}`);
            }

            // Basic structure validation based on filename
            if (filename.includes('persons') && !xmlDoc.querySelector('person')) {
                console.warn(`⚠️ No person elements found in ${filename}`);
            }

            if (filename.includes('works') && !xmlDoc.querySelector('bibl')) {
                console.warn(`⚠️ No bibl elements found in ${filename}`);
            }

            if (filename.includes('lexicon') && !xmlDoc.querySelector('entry')) {
                console.warn(`⚠️ No entry elements found in ${filename}`);
            }

            return xmlDoc;

        } catch (error) {
            console.error(`❌ XML validation failed for ${filename}:`, error);
            throw error;
        }
    }

    // ==================== BATCH OPERATIONS ====================

    async loadAllAuthorityFiles(authorityFiles, basePath = '../authority-files/') {
        const results = [];
        const errors = [];

        // Load files in parallel for better performance
        const loadPromises = authorityFiles.map(async (filename) => {
            try {
                const result = await this.loadAuthorityFile(filename, basePath);
                return {
                    filename,
                    success: true,
                    ...result
                };
            } catch (error) {
                errors.push({ filename, error: error.message });
                return {
                    filename,
                    success: false,
                    error: error.message
                };
            }
        });

        const loadResults = await Promise.all(loadPromises);

        // Separate successful and failed loads
        const successful = loadResults.filter(r => r.success);
        const failed = loadResults.filter(r => !r.success);

        console.log(`📊 Authority files loaded: ${successful.length} succeeded, ${failed.length} failed`);

        if (failed.length > 0) {
            console.warn('⚠️ Failed authority files:', failed.map(f => f.filename));
        }

        // Log cache statistics
        const cachedCount = successful.filter(r => r.cached).length;
        const networkCount = successful.filter(r => !r.cached).length;
        console.log(`📁 Cache stats: ${cachedCount} from cache, ${networkCount} from network`);

        return {
            successful,
            failed,
            totalSize: successful.reduce((sum, r) => sum + (r.content?.length || 0), 0),
            cacheHitRate: successful.length > 0 ? Math.round((cachedCount / successful.length) * 100) : 0
        };
    }

    // ==================== DEBUGGING UTILITIES ====================

    async getStorageStats() {
        await this.initialize();

        const cacheStatus = await this.getCacheStatus();
        const storageEstimate = this.isInitialized ?
            await this.indexedDBManager.getStorageEstimate() : null;

        return {
            indexedDBAvailable: this.isInitialized,
            cacheStatus,
            storageEstimate,
            settings: {
                defaultExpirationHours: this.defaultExpirationHours,
                maxRetries: this.maxRetries,
                fetchTimeout: this.fetchTimeout
            }
        };
    }

    formatFileSize(bytes) {
        if (bytes < 1024) return bytes + ' B';
        if (bytes < 1024 * 1024) return Math.round(bytes / 1024) + ' KB';
        return Math.round(bytes / 1024 / 1024 * 100) / 100 + ' MB';
    }
}