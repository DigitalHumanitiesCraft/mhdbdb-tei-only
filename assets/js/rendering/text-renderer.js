/**
 * Text Renderer — reduced to providing the shared TEI DOM cache.
 *
 * The former render/highlight/context-navigation path in this class
 * duplicated the live reading view (tei-text-reader.js) and was never
 * called from anywhere (audit #42). app.js instantiates this class solely
 * to hand its `cache` to TEITextReader.
 */

import { TEICacheManager } from '../storage/tei-cache-manager.js';

class TextRenderer {
    constructor(corpusIndex, authorityIndex) {
        this.corpusIndex = corpusIndex;
        this.authorityIndex = authorityIndex;

        // Shared TEI DOM cache (IndexedDB, revalidated per load — #151);
        // consumed by TEITextReader via app.js.
        this.cache = new TEICacheManager();
        this.cache.init().catch(err => console.error('[TextRenderer] Cache init failed:', err));
    }
}

export { TextRenderer };
