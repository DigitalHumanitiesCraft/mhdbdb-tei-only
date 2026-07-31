/**
 * Corpus Loader
 * Handles loading and caching of pre-built corpus indices
 * Uses Pako for gzip decompression (Safari 14+ compatible)
 * Uses Dexie.js for IndexedDB caching
 */

const INDEX_VERSION = '4.2.1';  // 4.1.5: #143 APO/HMT/HH Prosa-Konversion l→lb. 4.1.6: #198 habe/hab-Disambiguierung (25 Tokens zu lemma_2593, 179 NOM-Strips). 4.1.7: #189 GWTK-Pilot — 257 nackte rot/jung-Tokens neu annotiert (Goldstandard-validiert). 4.1.8: #138 814 Strophenziffern aus dem HUG-Verstext entfernt (706 davon pos=DIG, 108 unannotiert). 4.2.0: #236 Frauenlob-Revision — FR3 Parallelueberlieferungs-Ebene rekonstruiert (23 gleichrangige Toene zu 10 zusammengefuehrt, 36 <div type="parallel">, 1.563 Verse jetzt als Parallelueberlieferung erkennbar); 42 roemische Ordnungszahl-Tokens aus FR1/FR2/FR3 entfernt und durch <head> ersetzt. 4.2.1: #228 sieben leere <author>-Elemente im titleStmt gefuellt (ALX/BVSN/PSG/PTS Moench von Heilsbronn, BOP Boppe, MHG Herger, MRB Burggraf von Riedenburg); betrifft nur das Feld text.author, keine Token- oder Positionsdaten. Ausserdem normalisiert der Build Whitespace im Autornamen: LUU trug ihn ueber zwei eingerueckte Zeilen, der Umbruch stand so in Index und API.
const AUTHORITY_INDEX_VERSION = '1.7.0';  // 1.2.0: Authority migration. 1.2.1: WZB-Lemmata + Werk-Eintrag. 1.2.2: #104 FLG/FLG1-Werk-Titel + work_571 biblStruct (Vollmann-Profe/Neumann 1990). 1.3.0: #113-Followup — concepts altDE/altEN/altNormalized. 1.4.0: #44/#115 variants.xml aus Korpus regeneriert (+64.287 Formen). 1.4.1: #125 deterministischer Build (generatedAt entfernt). 1.4.2: #143 HH-Genre-Korrektur (work_137). 1.4.3: #143 APO-Gattung nach Terrahe (work_568). 1.4.4: #115 A-Stub-Backfill (+125 Lemmata). 1.5.0: Audit #5 — parse_genres last-wins-Fix (250 Genre-Labels) + genre altDE/altEN/altNormalized. 1.6.0: #161 posAll[] Multi-POS (pos bleibt Erstwert). 1.6.1: #189 GWTK-Pilot — variants.xml +2 Typen (rotte/rotten unter lemma_4954) + Formen-Zuwachs aus der Neu-Annotation. 1.6.2: #224 NFC-Unicode-Komposition im Normalizer — zerlegte Umlaute (o + U+0308) werden jetzt komponiert, bevor die Umlaut-Regeln greifen; korrigiert 'hugo von mühldorf' zu 'hugo von muehldorf' in persons.xml (die Quelldatei traegt dort ein zerlegtes ue). 1.6.3: #235 kaputte Tilden in URLs (kombinierendes U+0303 hinter einem Leerzeichen statt ASCII-Tilde) in 24 works.xml-Notizen repariert; die gleichen Notizen stehen im TEI-Header, dort ohne Indexwirkung. 1.6.4: #138 814 Strophenziffern aus dem HUG-Verstext entfernt; variants.xml verliert dadurch den Typ type_195524 'cxlvix', der nur in HUG vorkam. 1.6.5: #236 FR3-Metadaten auf den Supplementband 2000 umgestellt (ISBN 3-525-82504-8, Hrsg. Haustein/Stackmann, Reihenband 232) und Zotero-Title-Case 'Teil Ii'/'Teil Iii' repariert; variants.xml unveraendert. 1.7.0: kuratierte Lemma-Angaben: lemma.origin (Herkunftssprache, Schicht B von #28) sowie sense.definition/sense.comment (Prosa aus <def> bzw. <note type="comment">); erster Eintrag lemma_37818 Abba.
const CACHE_DURATION = 30 * 24 * 60 * 60 * 1000; // 30 days in milliseconds

class CorpusLoader {
    constructor(basePath = 'data') {
        this.basePath = basePath; // Allow custom base path (e.g., '../data' from playground)
        this.db = null;
        this.dbReady = this.initDatabase();
    }

    async initDatabase() {
        try {
            // Initialize Dexie database
            this.db = new Dexie('MHDBDBMainSite');

            this.db.version(1).stores({
                indices: 'name, version, timestamp, data'
            });

            await this.db.open();

            console.log('[CorpusLoader] IndexedDB initialized');
        } catch (error) {
            console.error('[CorpusLoader] Failed to initialize IndexedDB:', error);
            throw error;
        }
    }

    /**
     * Load authority index (persons, works, lemmata, variants)
     */
    async loadAuthorityIndex() {
        await this.dbReady;
        const cachedIndex = await this.getCachedIndex('authority-index');

        if (cachedIndex) {
            console.log('[CorpusLoader] Using cached authority index');
            return cachedIndex;
        }

        console.log('[CorpusLoader] Fetching authority index from network...');

        try {
            const response = await fetch(`${this.basePath}/authority-index.json.gz`);

            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }

            const compressedData = await response.arrayBuffer();
            const decompressedData = pako.ungzip(new Uint8Array(compressedData), { to: 'string' });
            const index = JSON.parse(decompressedData);

            console.log(`[CorpusLoader] Authority index loaded: ${index.lemmata.length} lemmata, ${Object.keys(index.variants).length} variant mappings`);

            // Cache for future use
            await this.cacheIndex('authority-index', index);

            return index;

        } catch (error) {
            console.error('[CorpusLoader] Failed to load authority index:', error);
            throw new Error(`Authority index konnte nicht geladen werden: ${error.message}`);
        }
    }

    /**
     * Load corpus index (texts metadata and lemma positions)
     */
    async loadCorpusIndex() {
        await this.dbReady;
        const cachedIndex = await this.getCachedIndex('corpus-index');

        if (cachedIndex) {
            console.log('[CorpusLoader] Using cached corpus index');
            return cachedIndex;
        }

        console.log('[CorpusLoader] Fetching corpus index from network...');

        try {
            const response = await fetch(`${this.basePath}/corpus-index.json.gz`);

            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }

            const compressedData = await response.arrayBuffer();
            const decompressedData = pako.ungzip(new Uint8Array(compressedData), { to: 'string' });
            const index = JSON.parse(decompressedData);

            console.log(`[CorpusLoader] Corpus index loaded: ${index.texts.length} texts indexed`);

            // Cache for future use
            await this.cacheIndex('corpus-index', index);

            return index;

        } catch (error) {
            console.error('[CorpusLoader] Failed to load corpus index:', error);
            throw new Error(`Korpus-Index konnte nicht geladen werden: ${error.message}`);
        }
    }

    /**
     * Get cached index from IndexedDB
     */
    async getCachedIndex(name) {
        try {
            const cached = await this.db.indices.get(name);

            if (!cached) {
                return null;
            }

            const expectedVersion = name === 'corpus-index' ? INDEX_VERSION : AUTHORITY_INDEX_VERSION;
            if (cached.version !== expectedVersion) {
                console.log(`[CorpusLoader] Cache version mismatch for ${name}: ${cached.version} != ${expectedVersion}`);
                await this.db.indices.delete(name);
                return null;
            }

            // Check expiration
            const age = Date.now() - cached.timestamp;
            if (age > CACHE_DURATION) {
                console.log(`[CorpusLoader] Cache expired for ${name} (age: ${Math.round(age / (24 * 60 * 60 * 1000))} days)`);
                await this.db.indices.delete(name);
                return null;
            }

            return cached.data;

        } catch (error) {
            console.error(`[CorpusLoader] Failed to read cache for ${name}:`, error);
            return null;
        }
    }

    /**
     * Cache index in IndexedDB
     */
    async cacheIndex(name, data) {
        try {
            const version = name === 'corpus-index' ? INDEX_VERSION : AUTHORITY_INDEX_VERSION;

            await this.db.indices.put({
                name: name,
                version: version,
                timestamp: Date.now(),
                data: data
            });

            console.log(`[CorpusLoader] Cached ${name} (version ${version})`);

        } catch (error) {
            console.error(`[CorpusLoader] Failed to cache ${name}:`, error);
            // Non-critical error, continue without caching
        }
    }

}

export { CorpusLoader, INDEX_VERSION, AUTHORITY_INDEX_VERSION };
