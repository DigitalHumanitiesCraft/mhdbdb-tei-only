/**
 * Dexie.js Database Schema
 *
 * Unified database schema for MHDBDB application.
 * Replaces custom IndexedDB manager with Dexie wrapper.
 */

export const DB_NAME = 'mhdbdb';
export const DB_VERSION = 1;

/**
 * Index version - bump this when corpus or authority data structure changes
 * This triggers cache invalidation for pre-built indices
 */
export const INDEX_VERSION = '1.0.0';

/**
 * Database schema definition
 * Format: storeName: 'primaryKey, index1, index2, ...'
 */
export const DB_SCHEMA = {
  // Pre-built corpus index (main site + playground optional load)
  corpusIndex: 'id, version',

  // Pre-built authority index (persons, works, lemmata, concepts, etc.)
  authorityIndex: 'type, version',

  // User-uploaded TEI files (playground only)
  uploadedTEI: 'id, filename, uploadedAt',

  // Full TEI texts (lazy-loaded from corpus or uploaded)
  // Cached with 1-day expiration
  fullTexts: 'id, fetchedAt',

  // Individual authority files (legacy, will migrate to authorityIndex)
  // 30-day expiration
  authorityFiles: 'key, expiresAt',

  // Application metadata (settings, version info, etc.)
  metadata: 'key'
};

/**
 * Initialize Dexie database with schema
 * @returns {Dexie} Initialized database instance
 */
export function initDB() {
  const db = new Dexie(DB_NAME);

  // Define schema version
  db.version(DB_VERSION).stores(DB_SCHEMA);

  // Optional: Add hooks for debugging
  if (process.env.NODE_ENV === 'development') {
    db.on('ready', () => {
      console.log('✅ Dexie database ready:', DB_NAME);
    });

    db.on('blocked', () => {
      console.warn('⚠️ Database blocked - close other tabs using MHDBDB');
    });
  }

  return db;
}

/**
 * Get table reference
 * @param {Dexie} db - Database instance
 * @param {string} tableName - Table name from DB_SCHEMA
 * @returns {Dexie.Table}
 */
export function getTable(db, tableName) {
  if (!DB_SCHEMA[tableName]) {
    throw new Error(`Unknown table: ${tableName}`);
  }
  return db[tableName];
}

/**
 * Clear all data from database (useful for testing)
 * @param {Dexie} db - Database instance
 */
export async function clearAllData(db) {
  const tableNames = Object.keys(DB_SCHEMA);
  await Promise.all(tableNames.map(name => db[name].clear()));
  console.log('🗑️ All database tables cleared');
}

/**
 * Get database size estimate
 * @param {Dexie} db - Database instance
 * @returns {Promise<{usage: number, quota: number, percentUsed: number}>}
 */
export async function getDatabaseSize(db) {
  if (!navigator.storage || !navigator.storage.estimate) {
    return {
      usage: 0,
      quota: 0,
      percentUsed: 0,
      supported: false
    };
  }

  const estimate = await navigator.storage.estimate();
  return {
    usage: estimate.usage || 0,
    quota: estimate.quota || 0,
    percentUsed: estimate.quota ? (estimate.usage / estimate.quota) * 100 : 0,
    usageMB: ((estimate.usage || 0) / (1024 * 1024)).toFixed(2),
    quotaMB: ((estimate.quota || 0) / (1024 * 1024)).toFixed(2),
    supported: true
  };
}

/**
 * Export database for debugging
 * @param {Dexie} db - Database instance
 * @returns {Promise<Object>} Database contents
 */
export async function exportDatabase(db) {
  const exported = {};

  for (const tableName of Object.keys(DB_SCHEMA)) {
    exported[tableName] = await db[tableName].toArray();
  }

  return exported;
}

/**
 * Import database from exported data
 * @param {Dexie} db - Database instance
 * @param {Object} data - Exported data
 */
export async function importDatabase(db, data) {
  for (const [tableName, records] of Object.entries(data)) {
    if (DB_SCHEMA[tableName]) {
      await db[tableName].bulkPut(records);
    }
  }
  console.log('✅ Database imported');
}

export default {
  DB_NAME,
  DB_VERSION,
  INDEX_VERSION,
  DB_SCHEMA,
  initDB,
  getTable,
  clearAllData,
  getDatabaseSize,
  exportDatabase,
  importDatabase
};
