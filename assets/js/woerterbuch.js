/**
 * Wörterbuch Page Controller (#117)
 * A–Z-Einstiegsseite für die persistenten Lemma-Seiten (/lemma/?id=N).
 * Liest den pre-built Authority-Index (CorpusLoader, IndexedDB-Cache).
 * URL-State: ?buchstabe=s&seite=3
 */

import { CorpusLoader } from './lib/corpus-loader.js';
import { TextNormalizer } from './lib/text-normalizer.js';

const PAGE_SIZE = 200;
const LETTERS = [...'abcdefghijklmnopqrstuvwxyz', '#'];

class WoerterbuchPage {
    constructor() {
        this.corpusLoader = new CorpusLoader('data');
        this.buckets = new Map();   // letter → sortierte Lemma-Einträge
        this.allEntries = [];       // alle Lemmata, global a–z–# sortiert (für die Suche)
        this.collator = new Intl.Collator('de');
        this.activeLetter = 'a';
        this.activePage = 1;
        this.searchQuery = '';

        this.elements = {
            loadingScreen: document.getElementById('loadingScreen'),
            loadingStatus: document.getElementById('loadingStatus'),
            loadingProgress: document.getElementById('loadingProgress'),
            content: document.getElementById('woerterbuchContent'),
            searchInput: document.getElementById('lemmaSearch'),
            letterBar: document.getElementById('letterBar'),
            letterHeading: document.getElementById('letterHeading'),
            entryGrid: document.getElementById('entryGrid'),
            pagination: document.getElementById('pagination'),
            errorDisplay: document.getElementById('errorDisplay'),
            errorMessage: document.getElementById('errorMessage'),
        };
    }

    /**
     * Anfangsbuchstabe a–z über normalized; NFD-Strip fängt die Randfälle
     * ë/ú ab, die die MHG-Normalisierungstabelle nicht abdeckt. Alles
     * andere (Ziffern-Lemmata) landet im '#'-Bucket.
     */
    bucketKey(entry) {
        const base = entry.normalized || entry.lemma || '';
        if (!base) return '#';
        const c = base[0].toLowerCase().normalize('NFD').replace(/[̀-ͯ]/g, '');
        return c >= 'a' && c <= 'z' ? c : '#';
    }

    buildBuckets(lemmata) {
        for (const letter of LETTERS) this.buckets.set(letter, []);
        for (const entry of lemmata) {
            this.buckets.get(this.bucketKey(entry)).push(entry);
        }
        for (const list of this.buckets.values()) {
            list.sort((a, b) =>
                this.collator.compare(a.normalized || a.lemma, b.normalized || b.lemma)
                || this.collator.compare(a.lemma, b.lemma));
        }
        // Flache Gesamtliste in Bucket-Reihenfolge → bereits global a–z–# sortiert
        this.allEntries = LETTERS.flatMap(letter => this.buckets.get(letter));
    }

    readUrlState() {
        const params = new URLSearchParams(window.location.search);
        const letter = (params.get('buchstabe') || 'a').toLowerCase();
        if (this.buckets.has(letter)) this.activeLetter = letter;
        const page = parseInt(params.get('seite'), 10);
        this.activePage = Number.isInteger(page) && page >= 1 ? page : 1;
    }

    writeUrlState() {
        const params = new URLSearchParams();
        params.set('buchstabe', this.activeLetter);
        if (this.activePage > 1) params.set('seite', String(this.activePage));
        history.replaceState(null, '', `${window.location.pathname}?${params}`);
    }

    selectLetter(letter, page = 1) {
        // Buchstabenwahl verlässt den Suchmodus
        if (this.searchQuery) {
            this.searchQuery = '';
            this.elements.searchInput.value = '';
        }
        this.activeLetter = letter;
        const pageCount = Math.max(1, Math.ceil(this.buckets.get(letter).length / PAGE_SIZE));
        this.activePage = Math.min(Math.max(1, page), pageCount);
        this.writeUrlState();
        this.renderLetterBar();
        this.renderEntries();
        this.renderPagination();
    }

    /**
     * Präfix-Suche über alle Lemmata (normalisierte Form). Filtert global,
     * blendet Pagination aus; leere Eingabe stellt die Buchstabenansicht her.
     */
    runSearch() {
        const query = this.elements.searchInput.value.trim();
        this.searchQuery = query;

        if (!query) {
            this.renderLetterBar();
            this.renderEntries();
            this.renderPagination();
            return;
        }

        const nq = TextNormalizer.normalizeMHG(query);
        const matches = this.allEntries.filter(
            e => (e.normalized || e.lemma.toLowerCase()).startsWith(nq));

        this.renderLetterBar();              // ohne Aktiv-Markierung (searchQuery gesetzt)
        this.elements.pagination.innerHTML = '';

        if (matches.length === 0) {
            this.elements.letterHeading.textContent = `Keine Treffer für „${query}“`;
        } else if (matches.length > PAGE_SIZE) {
            this.elements.letterHeading.textContent =
                `„${query}“ – ${matches.length.toLocaleString('de-DE')} Treffer (erste ${PAGE_SIZE} angezeigt)`;
        } else {
            this.elements.letterHeading.textContent =
                `„${query}“ – ${matches.length.toLocaleString('de-DE')} Treffer`;
        }
        this.renderEntryList(matches.slice(0, PAGE_SIZE));
    }

    renderLetterBar() {
        this.elements.letterBar.innerHTML = '';
        for (const letter of LETTERS) {
            const count = this.buckets.get(letter).length;
            const btn = document.createElement('button');
            btn.type = 'button';
            btn.textContent = letter === '#' ? '#' : letter.toUpperCase();
            btn.title = `${count.toLocaleString('de-DE')} Lemmata`;
            btn.dataset.letter = letter;
            btn.disabled = count === 0;
            const isActive = !this.searchQuery && letter === this.activeLetter;
            btn.className = isActive
                ? 'w-9 h-9 rounded-md text-sm font-semibold bg-brand-600 text-white'
                : count === 0
                    ? 'w-9 h-9 rounded-md text-sm font-medium text-slate-300 cursor-default'
                    : 'w-9 h-9 rounded-md text-sm font-medium text-slate-600 hover:bg-brand-100 hover:text-brand-700 transition';
            if (!btn.disabled && !isActive) {
                btn.addEventListener('click', () => this.selectLetter(letter));
            }
            this.elements.letterBar.appendChild(btn);
        }
    }

    renderEntries() {
        const list = this.buckets.get(this.activeLetter);
        const start = (this.activePage - 1) * PAGE_SIZE;
        const pageEntries = list.slice(start, start + PAGE_SIZE);

        const label = this.activeLetter === '#' ? '#' : this.activeLetter.toUpperCase();
        this.elements.letterHeading.textContent =
            `${label} – ${list.length.toLocaleString('de-DE')} Lemmata`;

        this.renderEntryList(pageEntries);
    }

    renderEntryList(entries) {
        this.elements.entryGrid.innerHTML = '';
        for (const entry of entries) {
            const numericId = entry.id.replace('lemma_', '');
            const row = document.createElement('div');
            row.className = 'flex items-center justify-between gap-2 py-1.5 px-2 rounded hover:bg-slate-50';

            const link = document.createElement('a');
            link.href = `lemma/?id=${numericId}`;
            link.textContent = entry.lemma;
            link.className = 'text-brand-700 hover:text-brand-900 hover:underline font-medium truncate';

            const pos = document.createElement('span');
            // #187: posAll[] zeigt alle POS-Werte (Fallback: Erstwert aus altem Cache)
            pos.textContent = (entry.posAll || (entry.pos ? [entry.pos] : [])).join(' ') || '–';
            pos.className = 'pos-badge bg-brand-100 text-brand-700 flex-shrink-0';

            row.appendChild(link);
            row.appendChild(pos);
            this.elements.entryGrid.appendChild(row);
        }
    }

    renderPagination() {
        const total = this.buckets.get(this.activeLetter).length;
        const pageCount = Math.max(1, Math.ceil(total / PAGE_SIZE));
        const el = this.elements.pagination;
        el.innerHTML = '';
        if (pageCount === 1) return;

        const makeBtn = (text, page, { disabled = false, active = false } = {}) => {
            const btn = document.createElement('button');
            btn.type = 'button';
            btn.textContent = text;
            btn.disabled = disabled || active;
            btn.className = active
                ? 'px-3 py-1.5 rounded-md text-sm font-semibold bg-brand-600 text-white'
                : disabled
                    ? 'px-3 py-1.5 rounded-md text-sm text-slate-300 cursor-default'
                    : 'px-3 py-1.5 rounded-md text-sm text-slate-600 hover:bg-brand-100 hover:text-brand-700 transition';
            if (!btn.disabled) {
                btn.addEventListener('click', () => this.selectLetter(this.activeLetter, page));
            }
            return btn;
        };

        el.appendChild(makeBtn('‹ Zurück', this.activePage - 1, { disabled: this.activePage === 1 }));

        // Fensterung: erste, letzte, ±2 um die aktive Seite; Lücken als „…"
        let lastShown = 0;
        for (let p = 1; p <= pageCount; p++) {
            const show = p === 1 || p === pageCount || Math.abs(p - this.activePage) <= 2;
            if (!show) continue;
            if (p - lastShown > 1) {
                const gap = document.createElement('span');
                gap.textContent = '…';
                gap.className = 'px-1 text-slate-400 text-sm';
                el.appendChild(gap);
            }
            el.appendChild(makeBtn(String(p), p, { active: p === this.activePage }));
            lastShown = p;
        }

        el.appendChild(makeBtn('Weiter ›', this.activePage + 1, { disabled: this.activePage === pageCount }));
    }

    updateLoading(message, percent) {
        if (this.elements.loadingStatus) this.elements.loadingStatus.textContent = message;
        if (this.elements.loadingProgress) this.elements.loadingProgress.style.width = `${percent}%`;
    }

    showError(message) {
        this.elements.loadingScreen.style.display = 'none';
        this.elements.errorDisplay.classList.remove('hidden');
        this.elements.errorMessage.textContent = message;
    }

    async init() {
        try {
            this.updateLoading('Lade Wörterbuchdaten...', 30);
            const authorityIndex = await this.corpusLoader.loadAuthorityIndex();
            this.updateLoading('Baue Register...', 80);

            this.buildBuckets(authorityIndex.lemmata);
            this.readUrlState();
            this.selectLetter(this.activeLetter, this.activePage);

            this.elements.searchInput.addEventListener('input', () => this.runSearch());

            this.elements.loadingScreen.style.display = 'none';
            this.elements.content.classList.remove('hidden');
        } catch (error) {
            console.error('[WoerterbuchPage] Initialisierung fehlgeschlagen:', error);
            this.showError(`Der Authority-Index konnte nicht geladen werden: ${error.message}`);
        }
    }
}

const page = new WoerterbuchPage();
page.init();
