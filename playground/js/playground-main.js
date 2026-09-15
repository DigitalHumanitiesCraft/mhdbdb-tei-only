/**
 * MHDBDB Playground - Main Application Class (MIGRATED)
 * Now using modular UI components instead of monolithic ui-helpers.js
 */

import { AuthorityFilesManager } from './data/authority-manager.js';
import { TEIFilesManager } from './data/tei-manager.js';

// NEW: Import modular UI components (decomposed from UICore.js)
import { updateAllUI } from './ui/core/ui-helpers.js';
import { initRouter, navigate, dispatchFromHash } from './ui/core/router.js';
import { AuthorityUI } from './ui/authority/authority-ui.js';
import { TEIExplorer } from './ui/tei/tei-ui.js';
import { MultiLemmaSearchUI } from './ui/tei/multi-lemma-search.js';
import { WordFrequencyAnalyzer } from './ui/tei/word-frequency.js';
import { TextStatistics } from './ui/tei/text-statistics.js';
import { LemmaDistribution } from './ui/tei/lemma-distribution.js';
import { VersePositionSearch } from './ui/tei/verse-position-search.js';
import { ConceptDistribution } from './ui/tei/concept-distribution.js';
import { TextComparison } from './ui/tei/text-comparison.js';
import { CooccurrenceRanking } from './ui/tei/cooccurrence-ranking.js';
import { RhymeDictionary } from './ui/tei/rhyme-dictionary.js';
import { HapaxLegomenaAnalyzer } from './ui/tei/hapax-legomena.js';
import { VerseEndingProfileAnalyzer } from './ui/tei/verse-ending-profile.js';
import { NamingExplorer } from './ui/tei/naming-explorer.js';
import { HorsesExplorer } from './ui/tei/horses-explorer.js';

// Import utilities for global exposure (needed for testing)
import { TextNormalizer } from '../../assets/js/lib/text-normalizer.js';
import { SearchPatterns } from './ui/search/SearchHelpers.js';

class MHDBDBPlayground {
    constructor() {
        // Data containers (UNCHANGED)
        this.authorityData = {
            files: [],
            parsedXML: [],
            persons: [],
            works: [],
            lemmata: [],
            concepts: [],
            genres: [],
            names: [],
            variants: []
        };
        
        // Hier stand bis #325 ein this.teiData mit fünf Feldern (files,
        // parsedXML, words, lines, annotations). Befüllt hat es der
        // Datei-Upload, den #314 zurückgebaut hat; danach hatte kein Feld mehr
        // einen Schreiber. Der Container wurde trotzdem noch durch drei
        // Konstruktoren gereicht und hat damit einen Datenfluss suggeriert,
        // den es nicht mehr gab.

        // Data managers (UNCHANGED)
        this.authorityManager = new AuthorityFilesManager(this.authorityData);
        this.teiManager = new TEIFilesManager();

        // NEW: Modular UI instead of single UIHelpers
        this.ui = {
            authorityExplorers: new AuthorityUI(this.authorityData),
            teiExplorer: new TEIExplorer()
        };

        // Initialize after teiExplorer is created
        this.ui.multiLemmaSearch = new MultiLemmaSearchUI(
            this.ui.teiExplorer,
            this.authorityManager
        );
        // Zwei Sichten auf denselben Korpus (#204).
        //
        // corpusTextsThunk liefert ALLE geladenen Texte, selectedTextsThunk nur
        // die im Korpus-Browser angehakten. Bis #204 bekamen alle Werkzeuge den
        // ersten, auch die, deren Ergebnis sich auf eine Auswahl beziehen soll:
        // gemessen am 15.09. lieferte das Kookkurrenz-Ranking für „minne" bei
        // Auswahl „nur Moriz von Craûn" 7.161 Vorkommen, also exakt den
        // korpusweiten Wert, während in CR selbst 14 stehen. Der Zähler
        // „1 / 667 Texte aktiv" stand daneben und stimmte. Nur die
        // Multi-Lemma-Suche hat die Auswahl je gelesen, sie geht über den
        // teiManager und nicht über diese Thunks.
        //
        // Wer hier ein Werkzeug ergänzt, wählt bewusst: die Auswahl gilt,
        // außer das Ergebnis ist seiner Natur nach korpusweit.
        const corpusTextsThunk = () => this.corpusData?.texts || this.teiManager.corpusIndex?.texts || [];
        const selectedTextsThunk = () => {
            const alle = corpusTextsThunk();
            const auswahl = this.corpusData?.includedTexts;
            // Vor dem Korpus-Load gibt es noch keine Auswahl. Dann ist die
            // leere Menge kein Nutzerinnen-Wunsch, sondern ein Ladezustand,
            // und die Werkzeuge sollen ihre Lade-Meldung zeigen dürfen.
            if (!auswahl) return alle;
            return alle.filter(t => auswahl.has(t.id));
        };

        this.ui.wordFrequency = new WordFrequencyAnalyzer(
            selectedTextsThunk,
            this.authorityData
        );
        this.ui.textStatistics = new TextStatistics(selectedTextsThunk);
        this.ui.lemmaDistribution = new LemmaDistribution(selectedTextsThunk, this.authorityManager);
        this.ui.versePositionSearch = new VersePositionSearch(selectedTextsThunk, this.authorityManager);
        this.ui.conceptDistribution = new ConceptDistribution(
            selectedTextsThunk,
            this.authorityManager,
            () => this.authorityData
        );
        // Textvergleich und Hapaxlegomena bleiben korpusweit (KZW/chsteiner,
        // 15.09.): der Vergleich laesst seine zwei Texte ohnehin selbst waehlen,
        // und "korpusweit einmalig" ist beim Hapax die Definition und nicht eine
        // Voreinstellung. Beide sagen das in ihrer Kopfzeile, damit die Auswahl
        // daneben nicht als wirkungslos missverstanden wird.
        this.ui.textComparison = new TextComparison(corpusTextsThunk, this.authorityManager);
        this.ui.cooccurrenceRanking = new CooccurrenceRanking(selectedTextsThunk, this.authorityManager);
        // Das Reim-Wörterbuch hat ein eigenes Textfilter-Feld und bleibt
        // deshalb korpusweit (chsteiner, 15.09.). Zwei Filter übereinander
        // wären hier der Fehler aus #204 in klein: das eigene Feld zeigt
        // seinen Zustand nur an, wenn es gefüllt ist, eine stille
        // Schnittmenge mit Schritt 1 stünde also nirgends. Stattdessen trägt
        // es einen einzeln ausgewählten Text sichtbar in sein Feld ein.
        this.ui.rhymeDictionary = new RhymeDictionary(corpusTextsThunk, this.authorityManager);
        this.ui.hapaxLegomena = new HapaxLegomenaAnalyzer(corpusTextsThunk, this.authorityData);
        this.ui.verseEndingProfile = new VerseEndingProfileAnalyzer(selectedTextsThunk, this.authorityData);
        this.ui.namingExplorer = new NamingExplorer('../data');
        this.ui.horsesExplorer = new HorsesExplorer('../data');

        this.init();
    }

    async init() {
        this.initializeEventListeners();

        // #314: Die Datenbank MHDBDB_Playground hielt einen einzigen Store
        // (tei_files) für den Datei-Upload. Der ist weg, damit hat sie keinen
        // Schreiber mehr. Bis #280 räumte eine Schema-Migration hier noch
        // Altstores auf; die lief über den IndexedDBManager, den nach dem
        // Rückbau niemand mehr instanziiert. Statt 397 Zeilen Schema-Pflege
        // für eine leere Datenbank wird sie einmalig gelöscht. Auf einer
        // nicht vorhandenen Datenbank ist das ein No-op, der Aufruf darf
        // also bei jedem Start laufen. Korpus und Authority-Daten liegen in
        // MHDBDBMainSite und sind nicht betroffen.
        // Entfernbar, sobald keine Profile mehr im Umlauf sind, die den
        // Playground vor Juli 2026 geöffnet haben: realistisch ab Mitte 2027.
        // Ohne dieses Datum wird der Aufruf selbst zu dem konservierten
        // Zweig, den #314 gerade entfernt hat.
        this.dropLegacyPlaygroundDatabase();

        // Load authority files from pre-built index (UPDATED)
        await this.loadAuthorityIndex();

        // NEW: Auto-load corpus on startup
        await this.autoLoadCorpus();

        this.updateUI();

        // NEW: Wire up hash router and dispatch any initial hash from the URL.
        // Done after data loading so that handlers can rely on populated state.
        initRouter();
        dispatchFromHash();
    }

    async loadAuthorityIndex() {
        try {
            console.log('📥 Loading pre-built authority index...');

            // Dynamically import CorpusLoader (from parent directory)
            const { CorpusLoader } = await import('../../assets/js/lib/corpus-loader.js');

            // Create loader with correct path (playground is in playground/ subdirectory)
            const loader = new CorpusLoader('../data');
            await loader.dbReady;

            // Load authority index
            const authorityIndex = await loader.loadAuthorityIndex();

            // Populate authorityData from index
            this.authorityData.persons = authorityIndex.persons || [];
            this.authorityData.works = authorityIndex.works || [];
            this.authorityData.lemmata = authorityIndex.lemmata || [];
            this.authorityData.concepts = authorityIndex.concepts || [];
            this.authorityData.genres = authorityIndex.genres || [];
            this.authorityData.names = authorityIndex.names || [];
            this.authorityData.variants = authorityIndex.variants || {};

            // Load pre-built performance Maps (if available)
            if (authorityIndex.maps) {
                // Convert objects to Maps for efficient lookup
                if (authorityIndex.maps.conceptToLemmas) {
                    this.authorityManager.indexes.conceptToLemmas = new Map(Object.entries(authorityIndex.maps.conceptToLemmas));
                }
                if (authorityIndex.maps.genreToWorks) {
                    this.authorityManager.indexes.genreToWorks = new Map(Object.entries(authorityIndex.maps.genreToWorks));
                }
                // #361: maps.genreHierarchy is gone. The hierarchy now sits on
                // the genre entries as parents[], with ids and direct parents.
                console.log(`📊 Performance Maps loaded: concept→lemmas: ${this.authorityManager.indexes.conceptToLemmas.size}, genre→works: ${this.authorityManager.indexes.genreToWorks.size}`);
            }

            // Mark authority files as loaded
            this.authorityData.files = [
                { name: 'persons.xml' },
                { name: 'works.xml' },
                { name: 'lexicon.xml' },
                { name: 'concepts.xml' },
                { name: 'genres.xml' },
                { name: 'names.xml' },
                { name: 'variants.xml' }
            ];

            console.log(`✅ Authority index loaded: ${this.authorityData.lemmata.length} lemmata, ${this.authorityData.persons.length} persons`);

        } catch (error) {
            console.error('❌ Failed to load authority index:', error);
            alert('Failed to load authority data. Please refresh the page.');
        }
    }

    dropLegacyPlaygroundDatabase() {
        if (!window.indexedDB) return;
        try {
            const req = indexedDB.deleteDatabase('MHDBDB_Playground');
            req.onsuccess = () => console.log('Alt-Datenbank MHDBDB_Playground entfernt (#314)');
            // onblocked heißt: ein anderer Tab hält die Datenbank noch offen.
            // Kein Fehlerfall, der nächste Start erledigt es.
            req.onblocked = () => console.log('MHDBDB_Playground noch von einem anderen Tab belegt');
            req.onerror = () => console.warn('MHDBDB_Playground ließ sich nicht löschen:', req.error);
        } catch (e) {
            console.warn('deleteDatabase auf MHDBDB_Playground hat geworfen:', e);
        }
    }

    async autoLoadCorpus() {
        try {
            console.log('📥 Auto-loading corpus on startup...');

            // Show loading state
            const loadingState = document.getElementById('corpusLoadingState');
            const fileBrowserSection = document.getElementById('fileBrowserSection');

            if (loadingState) loadingState.style.display = 'block';
            if (fileBrowserSection) fileBrowserSection.style.display = 'none';

            // Load corpus from pre-built index
            const { CorpusLoader } = await import('../../assets/js/lib/corpus-loader.js');
            const loader = new CorpusLoader('../data');
            await loader.dbReady;

            const corpusIndex = await loader.loadCorpusIndex();

            // Store corpus data (not parsedXML - we'll use the index directly)
            this.corpusData = {
                texts: corpusIndex.texts || [],
                lemmaIndex: corpusIndex.lemmaIndex || {},
                includedTexts: new Set() // Track which texts are included in search
            };

            // Also expose under teiManager.corpusIndex so downstream callers
            // (multi-lemma search, word-frequency, text-statistics,
            // lemma-distribution, future modules) can read from a single
            // canonical location regardless of which loader populated it.
            // See #97.
            this.teiManager.corpusIndex = corpusIndex;

            // Initially include all texts
            this.corpusData.texts.forEach(text => {
                this.corpusData.includedTexts.add(text.id);
            });

            console.log(`✅ Corpus loaded: ${this.corpusData.texts.length} texts`);

            // Hide loading, show file browser
            if (loadingState) loadingState.style.display = 'none';
            if (fileBrowserSection) fileBrowserSection.style.display = 'block';

            // Populate file browser
            this.populateFileBrowser();

            // Enable TEI queries. Seit #410 sind es zwei Bloecke: die
            // Korpusanalysen (teiQueries) und die weiteren (moreTeiQueries).
            // Beide haengen am geladenen Korpus und werden zusammen sichtbar;
            // die Register daneben brauchen ihn nicht und stehen von Anfang an.
            ['teiQueries', 'moreTeiQueries'].forEach((id) => {
                const block = document.getElementById(id);
                if (block) block.style.display = 'block';
            });

        } catch (error) {
            console.error('❌ Failed to auto-load corpus:', error);
            alert('Failed to load corpus. Please refresh the page.');
        }
    }

    populateFileBrowser() {
        const fileList = document.getElementById('fileList');
        if (!fileList) return;

        fileList.innerHTML = '';

        this.corpusData.texts.forEach(text => {
            const label = document.createElement('label');
            label.className = 'file-item';
            label.dataset.textId = text.id;
            label.dataset.title = text.title.toLowerCase();
            label.dataset.author = (text.author || '').toLowerCase();

            const checkbox = document.createElement('input');
            checkbox.type = 'checkbox';
            checkbox.checked = true;
            checkbox.dataset.textId = text.id;
            checkbox.addEventListener('change', () => this.handleTextToggle(text.id, checkbox.checked));

            const info = document.createElement('div');
            info.className = 'file-info';

            const title = document.createElement('span');
            title.className = 'file-title';
            title.textContent = text.title;

            const meta = document.createElement('span');
            meta.className = 'file-meta';
            const author = text.author || 'Unbekannt';
            const wordCount = text.wordCount ? text.wordCount.toLocaleString() : '0';
            meta.textContent = `${text.id} • ${author} • ${wordCount} Wörter`;

            info.appendChild(title);
            info.appendChild(meta);

            label.appendChild(checkbox);
            label.appendChild(info);

            fileList.appendChild(label);
        });

        // Update summary stats
        this.updateFileBrowserStats();

        // Setup filter
        this.setupFileBrowserFilter();
    }

    handleTextToggle(textId, isIncluded) {
        if (isIncluded) {
            this.corpusData.includedTexts.add(textId);
        } else {
            this.corpusData.includedTexts.delete(textId);
        }
        this.updateFileBrowserStats();
    }

    updateFileBrowserStats() {
        const includedCount = this.corpusData.includedTexts.size;
        const totalTexts = this.corpusData.texts.length;

        // Update included count
        const includedCountEl = document.getElementById('includedCount');
        if (includedCountEl) includedCountEl.textContent = includedCount;

        // Calculate total words and lemmata for included texts
        let totalWords = 0;
        let lemmataSet = new Set();

        this.corpusData.texts.forEach(text => {
            if (this.corpusData.includedTexts.has(text.id)) {
                totalWords += text.wordCount || 0;
                Object.keys(text.lemmata || {}).forEach(lemmaId => lemmataSet.add(lemmaId));
            }
        });

        const totalWordsEl = document.getElementById('totalWords');
        const totalLemmataEl = document.getElementById('totalLemmata');

        if (totalWordsEl) totalWordsEl.textContent = totalWords.toLocaleString();
        if (totalLemmataEl) totalLemmataEl.textContent = lemmataSet.size.toLocaleString();

        // Jede Auswahlaenderung kann den Hinweis faellig machen oder erledigen
        // (#204). Diese Methode ist der gemeinsame Durchgang aller vier Wege:
        // Einzel-Haekchen, Alle, Keine, Nur diese.
        this.updateFilterMismatchNote();
    }

    /**
     * Die aktuell sichtbaren (gefilterten) Texte werden zur Auswahl (#204).
     * Geteilt von „Nur diese" und der Korrektur im Mismatch-Hinweis.
     */
    selectOnlyVisibleTexts() {
        const fileList = document.getElementById('fileList');
        if (!fileList) return;
        this.corpusData.includedTexts.clear();
        Array.from(fileList.querySelectorAll('input[type="checkbox"]')).forEach(cb => {
            const item = cb.closest('.file-item');
            const isVisible = !item.style.display || item.style.display !== 'none';
            cb.checked = isVisible;
            if (isVisible) {
                this.corpusData.includedTexts.add(cb.dataset.textId);
            }
        });
        this.updateFileBrowserStats();
    }

    /**
     * Issue #204: Hinweis, solange der Anzeigefilter aktiv ist und die Auswahl
     * ueber die sichtbare Liste hinausgeht.
     *
     * Die Verwechslung ist zweimal unabhaengig passiert (Korpussuche 07/2026,
     * Playground 09/2026): gefiltert wird gelesen als ausgewaehlt. Der Hinweis
     * steht deshalb am Filterfeld und nicht am Ergebnis, denn hier laesst er
     * sich noch mit einem Klick beantworten.
     */
    updateFilterMismatchNote() {
        const note = document.getElementById('filterSelectionMismatch');
        const fileList = document.getElementById('fileList');
        const filterInput = document.getElementById('fileFilter');
        if (!note || !fileList || !filterInput) return;

        const query = filterInput.value.trim();
        const sichtbare = query
            ? Array.from(fileList.querySelectorAll('.file-item'))
                .filter(item => item.style.display !== 'none')
                .map(item => item.dataset.textId)
            : [];

        // Mismatch nur, wenn gefiltert wird, die Filterung etwas uebrig laesst
        // und die Auswahl mehr umfasst als die sichtbare Liste. Ein Filter, der
        // genau die ausgewaehlten Texte zeigt, ist kein Missverstaendnis.
        const sichtbarSet = new Set(sichtbare);
        const mismatch = query && sichtbare.length > 0 &&
            [...this.corpusData.includedTexts].some(id => !sichtbarSet.has(id));

        const onlyVisibleBtn = document.getElementById('selectOnlyVisibleBtn');
        if (!mismatch) {
            note.classList.add('hidden');
            // Ohne Mismatch traegt „Nur diese" wieder das ruhige Link-Styling
            if (onlyVisibleBtn) onlyVisibleBtn.classList.remove('font-semibold', 'underline');
            return;
        }

        // Das Wort steht hier und nicht im HTML: genau ein ausgewaehlter Text
        // ist erreichbar (auf „mori" verengen, dann nach „par" weitersuchen)
        // und stand sonst als „1 Texte" da.
        const anzahl = this.corpusData.includedTexts.size;
        document.getElementById('mismatchSelectedCount').textContent =
            `${anzahl.toLocaleString('de-DE')} ${anzahl === 1 ? 'Text' : 'Texte'}`;
        // Der haeufigste Fall ist genau ein Text: beide gemeldeten
        // Verwechslungen hatten bis auf einen Text herunter gefiltert.
        document.getElementById('mismatchUseFilteredLabel').textContent = sichtbare.length === 1
            ? 'Nur diesen einen Text verwenden'
            : `Nur die ${sichtbare.length.toLocaleString('de-DE')} gefilterten Texte verwenden`;
        note.classList.remove('hidden');
        // KZW 15.09.: „Nur diese" deckt die Erwartung ab und darf auffallen
        if (onlyVisibleBtn) onlyVisibleBtn.classList.add('font-semibold', 'underline');
    }

    setupFileBrowserFilter() {
        const fileFilter = document.getElementById('fileFilter');
        const fileList = document.getElementById('fileList');
        const filterInfo = document.getElementById('filterInfo');
        const visibleCountEl = document.getElementById('visibleCount');
        const clearFilterBtn = document.getElementById('clearFilterBtn');

        if (!fileFilter || !fileList) return;

        fileFilter.addEventListener('input', (e) => {
            const query = e.target.value.toLowerCase().trim();
            const items = fileList.querySelectorAll('.file-item');
            let visibleCount = 0;

            items.forEach(item => {
                const title = item.dataset.title || '';
                const author = item.dataset.author || '';
                const textId = item.dataset.textId || '';

                const matches = title.includes(query) ||
                               author.includes(query) ||
                               textId.toLowerCase().includes(query);

                if (matches) {
                    item.style.display = '';
                    visibleCount++;
                } else {
                    item.style.display = 'none';
                }
            });

            // Show/hide filter info + "Nur diese" button
            const onlyVisibleBtn = document.getElementById('selectOnlyVisibleBtn');
            const onlyVisibleSep = document.getElementById('selectOnlyVisibleSep');
            if (query) {
                if (filterInfo) filterInfo.style.display = 'flex';
                if (visibleCountEl) visibleCountEl.textContent = visibleCount;
                if (onlyVisibleBtn) onlyVisibleBtn.style.display = '';
                if (onlyVisibleSep) onlyVisibleSep.style.display = '';
            } else {
                if (filterInfo) filterInfo.style.display = 'none';
                if (onlyVisibleBtn) onlyVisibleBtn.style.display = 'none';
                if (onlyVisibleSep) onlyVisibleSep.style.display = 'none';
            }

            // #204: Der Hinweis haengt am Filter, nicht am Ergebnis
            this.updateFilterMismatchNote();
        });

        // Clear filter button
        if (clearFilterBtn) {
            clearFilterBtn.addEventListener('click', () => {
                fileFilter.value = '';
                fileFilter.dispatchEvent(new Event('input'));
            });
        }

        // Select All / None buttons
        const selectAllBtn = document.getElementById('selectAllBtn');
        const selectNoneBtn = document.getElementById('selectNoneBtn');

        if (selectAllBtn) {
            selectAllBtn.addEventListener('click', () => {
                const allCheckboxes = Array.from(fileList.querySelectorAll('input[type="checkbox"]'));
                allCheckboxes.forEach(cb => {
                    cb.checked = true;
                    this.corpusData.includedTexts.add(cb.dataset.textId);
                });
                const fileFilter = document.getElementById('fileFilter');
                if (fileFilter) {
                    fileFilter.value = '';
                    fileFilter.dispatchEvent(new Event('input'));
                }
                this.updateFileBrowserStats();
            });
        }

        if (selectNoneBtn) {
            selectNoneBtn.addEventListener('click', () => {
                this.corpusData.includedTexts.clear();
                const allCheckboxes = Array.from(fileList.querySelectorAll('input[type="checkbox"]'));
                allCheckboxes.forEach(cb => {
                    cb.checked = false;
                });
                const fileFilter = document.getElementById('fileFilter');
                if (fileFilter) {
                    fileFilter.value = '';
                    fileFilter.dispatchEvent(new Event('input'));
                }
                this.updateFileBrowserStats();
            });
        }

        // "Nur diese" — select only visible (filtered) texts, deselect all others
        const selectOnlyVisibleBtn = document.getElementById('selectOnlyVisibleBtn');
        if (selectOnlyVisibleBtn) {
            selectOnlyVisibleBtn.addEventListener('click', () => this.selectOnlyVisibleTexts());
        }

        // #204: dieselbe Korrektur aus dem Hinweis heraus, einen Klick entfernt
        const mismatchUseFiltered = document.getElementById('mismatchUseFiltered');
        if (mismatchUseFiltered) {
            mismatchUseFiltered.addEventListener('click', () => this.selectOnlyVisibleTexts());
        }
    }


    // ==================== EVENT LISTENERS (UPDATED) ====================
    
    initializeEventListeners() {
        this.setupSectionToggles();
        this.setupAuthorityQueries();
        this.setupTEIQueries();
    }

    /**
     * Die vier Abschnitte der Abfragespalte auf- und zuklappbar machen (#410).
     *
     * Erste Runde (KZW am 2026-09-08): „Es steht sonst zu viel auf einmal da.
     * Zumal die experimentellen Forschungsdaten ja erweitert werden auch
     * noch." Damals wurden genau die beiden Abschnitte aus ihren Screenshots
     * zuklappbar, die elf Analysewerkzeuge blieben als ein Block stehen.
     *
     * Zweite Runde (KZW am 2026-09-11, nach der Bewertung vom 10.09.): die
     * elf Werkzeuge sind auf zwei Bloecke aufgeteilt, und die Grenze ist nicht
     * Wichtigkeit, sondern der Ausgangspunkt der Frage. Sechs Werkzeuge
     * beginnen mit einem Wort oder Begriff („Korpusanalysen"), fuenf mit einem
     * Text oder einer Autor*in („Weitere Korpusanalysen"). Die Register heissen
     * jetzt „Register & Indizes (Authority Files)" und stehen offen, weil sie
     * fuer die fachwissenschaftliche Nutzung der vertraute Einstieg sind.
     *
     * Die Vorgabe ist deshalb nicht mehr fuer alle gleich: die beiden oberen
     * Bloecke stehen offen, die beiden unteren zu. Die eigene Wahl wiegt
     * schwerer als die Vorgabe und wird gemerkt. localStorage kann in privaten
     * Fenstern und bei gesperrten Site-Daten werfen, deshalb steht jeder
     * Zugriff in try/catch und der Ausfall bedeutet: es gilt die Vorgabe.
     *
     * Der Umschalter ist ein <button> INNERHALB der <h3> und nicht die <h3>
     * selbst: in der Ueberschrift steht daneben der Hilfe-Link, und ein <a>
     * in einem <button> waere weder gueltiges HTML noch bedienbar (der Klick
     * auf Hilfe wuerde mitklappen).
     */
    setupSectionToggles() {
        const abschnitte = [
            { toggle: 'corpusAnalysesToggle',   panel: 'corpusAnalysesPanel',   chevron: 'corpusAnalysesChevron',   offen: true },
            { toggle: 'authorityQueriesToggle', panel: 'authorityQueriesPanel', chevron: 'authorityQueriesChevron', offen: true },
            { toggle: 'moreAnalysesToggle',     panel: 'moreAnalysesPanel',     chevron: 'moreAnalysesChevron',     offen: false },
            { toggle: 'experimentalToggle',     panel: 'experimentalPanel',     chevron: 'experimentalChevron',     offen: false }
        ];

        abschnitte.forEach(({ toggle, panel, chevron, offen: vorgabeOffen }) => {
            const knopf = document.getElementById(toggle);
            const inhalt = document.getElementById(panel);
            const pfeil = document.getElementById(chevron);
            if (!knopf || !inhalt) {
                console.warn(`Missing section toggle: ${toggle}/${panel}`);
                return;
            }

            const schluessel = `mhdbdb-playground-section-${panel}`;
            const anwenden = (offen) => {
                inhalt.classList.toggle('hidden', !offen);
                knopf.setAttribute('aria-expanded', String(offen));
                if (pfeil) pfeil.classList.toggle('rotate-180', offen);
            };

            let gemerkt = null;
            try {
                gemerkt = localStorage.getItem(schluessel);
            } catch (e) {
                // privates Fenster oder gesperrte Site-Daten: Default gilt
            }
            // Die Vorgabe ist seit #410 nicht mehr fuer alle Abschnitte
            // dieselbe: die beiden oberen stehen offen, die beiden unteren zu.
            // Deshalb wird der fehlende Speicherwert gegen die jeweilige
            // Vorgabe aufgeloest und nicht pauschal als "zu" gelesen.
            if (gemerkt === 'offen') {
                anwenden(true);
            } else if (gemerkt === 'zu') {
                anwenden(false);
            } else {
                anwenden(vorgabeOffen);
            }

            knopf.addEventListener('click', () => {
                const offen = inhalt.classList.contains('hidden');
                anwenden(offen);
                try {
                    localStorage.setItem(schluessel, offen ? 'offen' : 'zu');
                } catch (e) {
                    // nicht speicherbar; die Sitzung selbst funktioniert weiter
                }
            });
        });
    }

    setupAuthorityQueries() {
        // UPDATED: Go through the hash router so the URL reflects the current view.
        const authorityButtons = [
            { id: 'showAuthorsBtn',  handler: () => navigate('authors') },
            { id: 'showWorksBtn',    handler: () => navigate('works') },
            { id: 'showLemmataBtn',  handler: () => navigate('lemmata') },
            { id: 'showConceptsBtn', handler: () => navigate('concepts') },
            { id: 'showGenresBtn',   handler: () => navigate('genres') },
            { id: 'showNamesBtn',    handler: () => navigate('names') }
        ];

        authorityButtons.forEach(({ id, handler }) => {
            const button = document.getElementById(id);
            if (button) {
                button.addEventListener('click', handler);
            } else {
                console.warn(`Missing authority button: ${id}`);
            }
        });
    }

    setupTEIQueries() {
        // UPDATED: Go through the hash router so the URL reflects the current view.
        const teiButtons = [
            { id: 'findMultiLemmaBtn',       handler: () => navigate('multi-lemma') },
            { id: 'findVersePositionBtn',    handler: () => navigate('verse-position') },
            { id: 'showWordFrequencyBtn',    handler: () => navigate('word-frequency') },
            { id: 'showTextStatisticsBtn',   handler: () => navigate('text-statistics') },
            { id: 'showLemmaDistributionBtn', handler: () => navigate('lemma-distribution') },
            { id: 'showConceptDistributionBtn', handler: () => navigate('concept-distribution') },
            { id: 'showTextComparisonBtn', handler: () => navigate('text-comparison') },
            { id: 'showCooccurrenceRankingBtn', handler: () => navigate('cooccurrence-ranking') },
            { id: 'showRhymeDictionaryBtn', handler: () => navigate('rhyme-dictionary') },
            { id: 'showHapaxLegomenaBtn', handler: () => navigate('hapax-legomena') },
            { id: 'showVerseEndingProfileBtn', handler: () => navigate('verse-ending-profile') },
            { id: 'showNamingExplorerBtn', handler: () => navigate('naming') },
            { id: 'showHorsesExplorerBtn', handler: () => navigate('horses') }
        ];

        teiButtons.forEach(({ id, handler }) => {
            const button = document.getElementById(id);
            if (button) {
                button.addEventListener('click', handler);
            } else {
                console.warn(`Missing TEI button: ${id}`);
            }
        });
    }

    // ==================== UI UPDATES (SIMPLIFIED) ====================

    updateUI() {
        // NEW: Use centralized UI update function
        updateAllUI(this.authorityData);
    }
}

// ==================== GLOBAL ONCLICK HANDLER SUPPORT ====================

// Global reference for dynamically generated onclick handlers
window.playground = null;

// Initialize the playground when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.playground = new MHDBDBPlayground();

    // CRITICAL: Expose UI modules globally for onclick handlers
    // This maintains backward compatibility with dynamically generated onclick calls
    if (window.playground && window.playground.ui) {
        // Make authority explorers methods available globally
        window.playground.ui.authorityExplorers = window.playground.ui.authorityExplorers;
        window.playground.ui.teiExplorer = window.playground.ui.teiExplorer;
    }

    // Expose utilities globally for testing
    window.TextNormalizer = TextNormalizer;
    window.SearchPatterns = SearchPatterns;

    // Note: The "Load Full Corpus" button was removed in the redesign;
    // autoLoadCorpus() in init() handles corpus loading. See #99.

    console.log('MHDBDB Playground migrated to modular UI successfully!');
    console.log('Available UI modules:', Object.keys(window.playground.ui));
});