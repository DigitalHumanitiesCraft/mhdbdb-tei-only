# Backup: Unused JavaScript Files

These files were replaced during the MHDBDB rework (October 2025) and are kept here for reference.

## Files

### `authority-storage-manager.js`
- **Original purpose:** Manages caching of authority XML files in IndexedDB with 30-day expiration
- **Replaced by:** Pre-built authority index loaded via `CorpusLoader` from main site
- **Last used:** Before playground polish (Phase 4)
- **Status:** Obsolete - authority data now loaded from `authority-index.json.gz` (1.27 MB, 1.2s load time vs 5-7s with XML)

### `db-schema.js`
- **Original purpose:** Dexie.js database schema definition
- **Replaced by:** `indexed-db-manager.js` (more flexible IndexedDB wrapper)
- **Last used:** Phase 1 (infrastructure setup)
- **Status:** Obsolete - new code uses IndexedDB directly via indexed-db-manager.js

### `dexie-manager.js`
- **Original purpose:** Wrapper around Dexie.js for storage operations
- **Replaced by:** `indexed-db-manager.js` (lighter, more direct IndexedDB access)
- **Last used:** Phase 1 (infrastructure setup)
- **Status:** Obsolete - functionality merged into indexed-db-manager.js

### `error-handler.js`
- **Original purpose:** Centralized error handling utility
- **Replaced by:** Inline error handling in each module
- **Last used:** Never fully integrated
- **Status:** Unused - error handling is now done locally in each module

## Architecture Changes

The rework consolidated IndexedDB operations into a single, lightweight `indexed-db-manager.js` module that:
- Handles both TEI files and authority files
- Provides simple get/set/list/delete operations
- Includes automatic expiration for authority data (30-day TTL)
- Eliminates dependency on Dexie.js library

## Restoration

If you need to restore any of these files:

```bash
# From playground/js directory
cp .backup/filename.js .
```

However, note that restoring these files will likely break the current architecture, as the new code expects the `indexed-db-manager.js` interface.
