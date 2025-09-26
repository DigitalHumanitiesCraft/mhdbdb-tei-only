/**
 * MHDBDB Playground - TEI Storage Manager
 * Handles SessionStorage for TEI files with size monitoring and error handling
 */

export class TEIStorageManager {
    constructor() {
        this.storagePrefix = 'mhdbdb_tei_';
        this.metaKey = 'mhdbdb_tei_meta';
    }

    // ==================== CORE STORAGE OPERATIONS ====================

    saveToSession(filename, content) {
        try {
            const key = this.storagePrefix + filename;
            sessionStorage.setItem(key, content);

            // Update metadata
            this.updateMetadata(filename, {
                filename: filename,
                size: content.length,
                timestamp: Date.now(),
                type: 'tei'
            });

            console.log(`✅ TEI file saved to session: ${filename} (${(content.length / 1024).toFixed(1)} KB)`);
            return true;
        } catch (error) {
            console.error(`❌ Failed to save ${filename} to session:`, error);
            return false;
        }
    }

    loadFromSession(filename) {
        try {
            const key = this.storagePrefix + filename;
            const content = sessionStorage.getItem(key);

            if (content) {
                console.log(`📁 TEI file loaded from session: ${filename}`);
                return content;
            }
            return null;
        } catch (error) {
            console.error(`❌ Failed to load ${filename} from session:`, error);
            return null;
        }
    }

    removeFromSession(filename) {
        try {
            const key = this.storagePrefix + filename;
            sessionStorage.removeItem(key);

            // Update metadata
            const meta = this.getMetadata();
            delete meta[filename];
            this.saveMetadata(meta);

            console.log(`🗑️ TEI file removed from session: ${filename}`);
            return true;
        } catch (error) {
            console.error(`❌ Failed to remove ${filename} from session:`, error);
            return false;
        }
    }

    isInSession(filename) {
        const key = this.storagePrefix + filename;
        return sessionStorage.getItem(key) !== null;
    }

    // ==================== BULK OPERATIONS ====================

    listSessionFiles() {
        try {
            const files = [];
            const meta = this.getMetadata();

            for (const [filename, data] of Object.entries(meta)) {
                files.push({
                    filename: filename,
                    size: data.size || 0,
                    timestamp: data.timestamp || 0,
                    isSessionFile: true
                });
            }

            return files.sort((a, b) => b.timestamp - a.timestamp); // Most recent first
        } catch (error) {
            console.error('❌ Failed to list session files:', error);
            return [];
        }
    }

    clearAllSession() {
        try {
            const keys = Object.keys(sessionStorage);
            let removedCount = 0;

            keys.forEach(key => {
                if (key.startsWith(this.storagePrefix)) {
                    sessionStorage.removeItem(key);
                    removedCount++;
                }
            });

            // Clear metadata
            sessionStorage.removeItem(this.metaKey);

            console.log(`🧹 Cleared ${removedCount} TEI files from session storage`);
            return removedCount;
        } catch (error) {
            console.error('❌ Failed to clear session storage:', error);
            return 0;
        }
    }

    // ==================== STORAGE MONITORING ====================

    getSessionStorageSize() {
        try {
            let totalSize = 0;
            const keys = Object.keys(sessionStorage);

            keys.forEach(key => {
                if (key.startsWith(this.storagePrefix)) {
                    const value = sessionStorage.getItem(key);
                    totalSize += (key.length + (value?.length || 0)) * 2; // UTF-16 encoding
                }
            });

            return {
                bytes: totalSize,
                kb: Math.round(totalSize / 1024),
                mb: Math.round(totalSize / 1024 / 1024 * 100) / 100
            };
        } catch (error) {
            console.error('❌ Failed to calculate storage size:', error);
            return { bytes: 0, kb: 0, mb: 0 };
        }
    }

    getStorageQuotaInfo() {
        const size = this.getSessionStorageSize();
        const estimatedQuota = 5 * 1024 * 1024; // ~5MB typical sessionStorage limit

        return {
            used: size,
            estimatedQuota: estimatedQuota,
            percentUsed: Math.round((size.bytes / estimatedQuota) * 100),
            available: {
                bytes: estimatedQuota - size.bytes,
                mb: Math.round((estimatedQuota - size.bytes) / 1024 / 1024 * 100) / 100
            }
        };
    }

    // ==================== METADATA MANAGEMENT ====================

    getMetadata() {
        try {
            const meta = sessionStorage.getItem(this.metaKey);
            return meta ? JSON.parse(meta) : {};
        } catch (error) {
            console.warn('⚠️ Failed to parse metadata, resetting:', error);
            return {};
        }
    }

    saveMetadata(metadata) {
        try {
            sessionStorage.setItem(this.metaKey, JSON.stringify(metadata));
        } catch (error) {
            console.error('❌ Failed to save metadata:', error);
        }
    }

    updateMetadata(filename, data) {
        const meta = this.getMetadata();
        meta[filename] = { ...meta[filename], ...data };
        this.saveMetadata(meta);
    }

    // ==================== UTILITY METHODS ====================

    canStoreFile(content) {
        const quota = this.getStorageQuotaInfo();
        const fileSize = content.length * 2; // UTF-16 encoding

        return quota.available.bytes > fileSize;
    }

    formatFileSize(bytes) {
        if (bytes < 1024) return bytes + ' B';
        if (bytes < 1024 * 1024) return Math.round(bytes / 1024) + ' KB';
        return Math.round(bytes / 1024 / 1024 * 100) / 100 + ' MB';
    }

    // ==================== ERROR HANDLING & RECOVERY ====================

    validateStorage() {
        try {
            // Test write access
            const testKey = this.storagePrefix + 'test';
            sessionStorage.setItem(testKey, 'test');
            sessionStorage.removeItem(testKey);

            // Cleanup orphaned entries (files without metadata)
            this.cleanupOrphanedEntries();

            return true;
        } catch (error) {
            console.error('❌ SessionStorage validation failed:', error);
            return false;
        }
    }

    cleanupOrphanedEntries() {
        try {
            const meta = this.getMetadata();
            const keys = Object.keys(sessionStorage);
            let cleanedCount = 0;

            keys.forEach(key => {
                if (key.startsWith(this.storagePrefix) && key !== this.metaKey) {
                    const filename = key.substring(this.storagePrefix.length);
                    if (!meta[filename]) {
                        sessionStorage.removeItem(key);
                        cleanedCount++;
                    }
                }
            });

            if (cleanedCount > 0) {
                console.log(`🧹 Cleaned up ${cleanedCount} orphaned storage entries`);
            }
        } catch (error) {
            console.error('❌ Failed to cleanup orphaned entries:', error);
        }
    }

    // ==================== DEBUG UTILITIES ====================

    getStorageStats() {
        const files = this.listSessionFiles();
        const quota = this.getStorageQuotaInfo();

        return {
            fileCount: files.length,
            totalSize: quota.used,
            quota: quota,
            files: files.map(f => ({
                name: f.filename,
                size: this.formatFileSize(f.size),
                age: Math.round((Date.now() - f.timestamp) / 1000 / 60) + ' min ago'
            }))
        };
    }
}