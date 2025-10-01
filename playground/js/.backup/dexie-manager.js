/**
 * DexieManager - Unified IndexedDB management with Dexie.js
 *
 * Features:
 * - Storage quota checking (Critical Fix #3)
 * - LRU eviction when quota exceeded
 * - Automatic expiration handling
 * - Error handling with user-friendly messages
 */

import { initDB, INDEX_VERSION, getDatabaseSize } from './db-schema.js';
import ErrorHandler from './error-handler.js';

export class DexieManager {
  constructor() {
    this.db = null;
    this.isInitialized = false;
  }

  /**
   * Initialize database connection
   */
  async init() {
    if (this.isInitialized) {
      return this.db;
    }

    try {
      this.db = initDB();
      await this.db.open();

      // Check storage quota on init
      const quota = await this.checkStorageQuota();
      console.log(`💾 Storage: ${quota.usageMB} MB / ${quota.quotaMB} MB (${quota.percentUsed.toFixed(1)}%)`);

      if (!quota.available) {
        console.warn('⚠️ Storage quota critical (>90%). Evicting old entries...');
        await this.evictOldestEntries('fullTexts', 50); // Keep only 50 newest
      }

      this.isInitialized = true;
      return this.db;
    } catch (error) {
      throw ErrorHandler.createError(
        'Failed to initialize database',
        'DB_INIT_ERROR',
        { originalError: error }
      );
    }
  }

  /**
   * Check storage quota (Critical Fix #3)
   * @returns {Promise<{available: boolean, percentUsed: number, usageMB: string, quotaMB: string}>}
   */
  async checkStorageQuota() {
    if (!navigator.storage?.estimate) {
      // Fallback for browsers without Storage API
      return {
        available: true,
        percentUsed: 0,
        usageMB: 'N/A',
        quotaMB: 'N/A',
        supported: false
      };
    }

    const estimate = await navigator.storage.estimate();
    const percentUsed = (estimate.usage / estimate.quota) * 100;

    return {
      available: percentUsed < 90, // Leave 10% buffer
      percentUsed,
      usage: estimate.usage,
      quota: estimate.quota,
      usageMB: (estimate.usage / (1024 * 1024)).toFixed(2),
      quotaMB: (estimate.quota / (1024 * 1024)).toFixed(2),
      supported: true
    };
  }

  /**
   * Check if data will fit in available quota
   * @param {any} data - Data to store
   * @returns {Promise<boolean>}
   */
  async willFitInQuota(data) {
    const quota = await this.checkStorageQuota();

    if (!quota.supported) {
      // Can't check, assume it fits
      return true;
    }

    // Rough estimate: JSON.stringify size
    const dataSize = new Blob([JSON.stringify(data)]).size;
    const availableSpace = quota.quota - quota.usage;

    // Leave 10% buffer
    const safeSpace = availableSpace * 0.9;

    return dataSize < safeSpace;
  }

  /**
   * Evict oldest entries when quota exceeded (LRU eviction)
   * @param {string} storeName - Store to evict from
   * @param {number} keepCount - Number of entries to keep
   */
  async evictOldestEntries(storeName, keepCount = 50) {
    const store = this.db[storeName];

    if (!store) {
      console.warn(`⚠️ Store ${storeName} not found for eviction`);
      return;
    }

    // Get all entries sorted by timestamp
    const allEntries = await store
      .orderBy('fetchedAt')
      .reverse()
      .toArray();

    if (allEntries.length <= keepCount) {
      // Nothing to evict
      return;
    }

    // Keep newest, delete oldest
    const toDelete = allEntries.slice(keepCount);
    const deleteIds = toDelete.map(entry => entry.id);

    await store.bulkDelete(deleteIds);

    console.log(`🗑️ Evicted ${deleteIds.length} old entries from ${storeName}`);
  }

  /**
   * Put data into store with quota checking
   * @param {string} storeName - Store name
   * @param {Object} data - Data to store
   * @returns {Promise<any>} Primary key of stored item
   */
  async put(storeName, data) {
    return await ErrorHandler.withErrorBoundary(async () => {
      // Check if data will fit
      const fitsInQuota = await this.willFitInQuota(data);

      if (!fitsInQuota) {
        // Try to make space
        console.warn('⚠️ Data too large, evicting old entries...');
        await this.evictOldestEntries(storeName, 50);

        // Check again
        const fitsNow = await this.willFitInQuota(data);
        if (!fitsNow) {
          throw new Error('QuotaExceededError: Cannot store data, quota full');
        }
      }

      try {
        return await this.db[storeName].put(data);
      } catch (error) {
        if (error.name === 'QuotaExceededError') {
          // Try one more time with aggressive eviction
          console.warn('⚠️ QuotaExceededError caught, aggressive eviction...');
          await this.evictOldestEntries(storeName, 10); // Keep only 10
          return await this.db[storeName].put(data);
        }
        throw error;
      }
    }, `Put data into ${storeName}`);
  }

  /**
   * Get data from store
   * @param {string} storeName - Store name
   * @param {string|number} key - Primary key
   * @returns {Promise<any>}
   */
  async get(storeName, key) {
    return await this.db[storeName].get(key);
  }

  /**
   * Get data with expiration check
   * @param {string} storeName - Store name
   * @param {string|number} key - Primary key
   * @param {number} expirationMs - Expiration time in milliseconds
   * @returns {Promise<any|null>} Data or null if expired
   */
  async getWithExpiry(storeName, key, expirationMs) {
    const data = await this.get(storeName, key);

    if (!data) {
      return null;
    }

    // Check expiration
    const now = Date.now();
    const age = now - (data.fetchedAt || data.cachedAt || data.uploadedAt || 0);

    if (age > expirationMs) {
      // Expired, delete and return null
      await this.delete(storeName, key);
      console.log(`🗑️ Expired entry deleted: ${storeName}/${key}`);
      return null;
    }

    return data;
  }

  /**
   * Delete data from store
   * @param {string} storeName - Store name
   * @param {string|number} key - Primary key
   */
  async delete(storeName, key) {
    await this.db[storeName].delete(key);
  }

  /**
   * Clear entire store
   * @param {string} storeName - Store name
   */
  async clear(storeName) {
    await this.db[storeName].clear();
    console.log(`🗑️ Cleared ${storeName} store`);
  }

  /**
   * Get all entries from store
   * @param {string} storeName - Store name
   * @returns {Promise<Array>}
   */
  async getAll(storeName) {
    return await this.db[storeName].toArray();
  }

  /**
   * Count entries in store
   * @param {string} storeName - Store name
   * @returns {Promise<number>}
   */
  async count(storeName) {
    return await this.db[storeName].count();
  }

  /**
   * Check if key exists in store
   * @param {string} storeName - Store name
   * @param {string|number} key - Primary key
   * @returns {Promise<boolean>}
   */
  async has(storeName, key) {
    const data = await this.get(storeName, key);
    return data !== undefined;
  }

  /**
   * Bulk put (efficient for multiple entries)
   * @param {string} storeName - Store name
   * @param {Array} dataArray - Array of data objects
   * @returns {Promise<any>}
   */
  async bulkPut(storeName, dataArray) {
    return await ErrorHandler.withErrorBoundary(async () => {
      // Check total size
      const totalSize = new Blob([JSON.stringify(dataArray)]).size;
      const quota = await this.checkStorageQuota();

      if (quota.supported) {
        const availableSpace = quota.quota - quota.usage;
        if (totalSize > availableSpace * 0.9) {
          throw new Error('QuotaExceededError: Bulk data too large');
        }
      }

      return await this.db[storeName].bulkPut(dataArray);
    }, `Bulk put into ${storeName}`);
  }

  /**
   * Query store with filter
   * @param {string} storeName - Store name
   * @param {Function} filterFn - Filter function
   * @returns {Promise<Array>}
   */
  async query(storeName, filterFn) {
    const all = await this.getAll(storeName);
    return all.filter(filterFn);
  }

  /**
   * Get database statistics
   * @returns {Promise<Object>}
   */
  async getStats() {
    const stats = {
      quota: await this.checkStorageQuota(),
      stores: {}
    };

    const storeNames = ['corpusIndex', 'authorityIndex', 'uploadedTEI', 'fullTexts', 'authorityFiles', 'metadata'];

    for (const storeName of storeNames) {
      if (this.db[storeName]) {
        stats.stores[storeName] = await this.count(storeName);
      }
    }

    return stats;
  }

  /**
   * Clean up expired entries from all stores
   * @returns {Promise<number>} Number of entries cleaned
   */
  async cleanupExpired() {
    let totalCleaned = 0;

    // fullTexts: 1 day expiration
    const fullTexts = await this.getAll('fullTexts');
    const oneDayAgo = Date.now() - (24 * 60 * 60 * 1000);

    for (const entry of fullTexts) {
      if ((entry.fetchedAt || 0) < oneDayAgo) {
        await this.delete('fullTexts', entry.id);
        totalCleaned++;
      }
    }

    // authorityFiles: 30 day expiration
    const authorityFiles = await this.getAll('authorityFiles');
    const thirtyDaysAgo = Date.now() - (30 * 24 * 60 * 60 * 1000);

    for (const entry of authorityFiles) {
      if ((entry.expiresAt || 0) < Date.now() || (entry.cachedAt || 0) < thirtyDaysAgo) {
        await this.delete('authorityFiles', entry.key);
        totalCleaned++;
      }
    }

    if (totalCleaned > 0) {
      console.log(`🗑️ Cleaned up ${totalCleaned} expired entries`);
    }

    return totalCleaned;
  }

  /**
   * Close database connection
   */
  async close() {
    if (this.db) {
      this.db.close();
      this.isInitialized = false;
      console.log('✅ Database closed');
    }
  }
}

export default DexieManager;
