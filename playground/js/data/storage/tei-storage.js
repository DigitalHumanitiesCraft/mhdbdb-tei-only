/**
 * MHDBDB Playground - TEI Storage Manager
 * Handles TEI file storage using IndexedDB
 */

import { IndexedDBManager } from '../../indexed-db-manager.js';

export class TEIStorageManager {
    constructor() {
        this.indexedDBManager = new IndexedDBManager();
        this.isInitialized = false;
    }

    // ==================== INITIALIZATION ====================

    async initialize() {
        if (this.isInitialized) return true;

        try {
            // IndexedDBManager.initialize() wirft nicht, sondern liefert
            // false (kein IndexedDB-Support / open fehlgeschlagen) — das
            // Ergebnis darf nicht als Erfolg gemeldet werden (#167 Finding 63).
            const ok = await this.indexedDBManager.initialize();
            if (!ok) {
                console.error('❌ Storage initialization failed: IndexedDB not available');
                this.isInitialized = false;
                return false;
            }
            this.isInitialized = true;

            console.log('🔧 Storage initialized: IndexedDB cache ready');
            return true;
        } catch (error) {
            console.error('❌ Storage initialization failed:', error);
            this.isInitialized = false;
            return false;
        }
    }

    // ==================== CORE STORAGE OPERATIONS ====================

    async saveToCache(filename, content) {
        if (!await this.initialize()) {
            console.error('❌ Cannot save - storage not available');
            return false;
        }

        return await this.indexedDBManager.saveTEIFile(filename, content);
    }

    async loadFromCache(filename) {
        if (!await this.initialize()) {
            console.error('❌ Cannot load - storage not available');
            return null;
        }

        return await this.indexedDBManager.loadTEIFile(filename);
    }

    async removeFromCache(filename) {
        if (!await this.initialize()) {
            console.error('❌ Cannot remove - storage not available');
            return false;
        }

        return await this.indexedDBManager.removeTEIFile(filename);
    }

    async isInCache(filename) {
        if (!await this.initialize()) {
            return false;
        }

        const content = await this.indexedDBManager.loadTEIFile(filename);
        return content !== null;
    }

    async listCachedFiles() {
        if (!await this.initialize()) {
            return [];
        }

        return await this.indexedDBManager.listTEIFiles();
    }

    async clearAllCache() {
        if (!await this.initialize()) {
            return 0;
        }

        return await this.indexedDBManager.clearTEIFiles();
    }

    // ==================== STORAGE INFO ====================

    async getStorageInfo() {
        if (!await this.initialize()) {
            return {
                used: 0,
                available: 0,
                estimatedQuota: 0,
                storageType: 'Not Available'
            };
        }

        return await this.indexedDBManager.getStorageQuotaInfo();
    }

    // Alias for backward compatibility with tests
    async getStorageQuotaInfo() {
        return await this.getStorageInfo();
    }
}