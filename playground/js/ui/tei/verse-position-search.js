/**
 * MHDBDB Playground - Lemmasuche nach Versposition
 *
 * Sucht ein einzelnes Lemma am Versanfang oder Versende. Nutzt die
 * lineStarts/lineEnds-Arrays aus dem Corpus-Index v4.1.0 (#47.3).
 *
 * Use case: Mediävistik — Reim- bzw. Versendanalyse, Argumentation
 * über reimgetriebene vs. nicht-reimgetriebene Wortwahl.
 */

const DEFAULT_STATE = Object.freeze({
  query: '',
  resolvedLemma: null,
  selectedLemma: null,  // explizite Autocomplete-Auswahl (#163) — schlägt resolveQuery
  candidates: [],
  position: 'end',  // 'start' | 'end' — Versende ist der häufigere Use Case (Reim)
  // Autocomplete (Port aus #113-Pattern)
  autocompleteOpen: false,
  autocompleteIndex: -1,
  autocompleteItems: []
});

const AUTOCOMPLETE_LIMIT = 8;

export class VersePositionSearch {
  constructor(getCorpusTexts, authorityManager) {
    this.getCorpusTexts = getCorpusTexts;
    this.authorityManager = authorityManager;
    this.state = { ...DEFAULT_STATE };
  }

  show() {
    const texts = this.getCorpusTexts();
    if (!texts || texts.length === 0) {
      this.renderError('Korpus ist noch nicht geladen. Bitte einen Moment warten und Button erneut klicken.');
      return;
    }
    this.render();
  }

  resolveQuery(query) {
    const trimmed = (query || '').trim();
    if (!trimmed) return { resolved: null, candidates: [] };
    const matches = this.authorityManager.searchLemmaByOrthography(trimmed) || [];
    if (matches.length === 0) return { resolved: null, candidates: [] };
    return { resolved: matches[0], candidates: matches.slice(0, 12) };
  }

  /**
   * Find texts where lemmaId sits exactly at line start (or end).
   * Returns hits sorted desc by count.
   */
  findHits(lemmaId) {
    const texts = this.getCorpusTexts() || [];
    const isStart = this.state.position === 'start';
    const hits = [];

    for (const text of texts) {
      const boundary = isStart ? text.lineStarts : text.lineEnds;
      if (!boundary || boundary.length === 0) continue; // prose
      // Ueber die lemmata{}-Positionsliste statt words[idx] === lemmaId:
      // words[] traegt bei Mehrfach-@lemmaRef nur die ERSTE ID (CONTRACTS
      // §B.1), lemmata{} listet die Position unter JEDER referenzierten ID —
      // sonst wuerde ein kuenftiges Multi-Ref-Wort an der Versgrenze fuer
      // seine Zweit-ID nicht gefunden (#170 Review-Finding).
      const lemmaPositions = text.lemmata?.[lemmaId];
      if (!lemmaPositions || lemmaPositions.length === 0) continue;
      const boundarySet = new Set(boundary);
      const positions = lemmaPositions.filter(idx => boundarySet.has(idx));
      if (positions.length > 0) {
        const totalForLemma = lemmaPositions.length;
        hits.push({
          id: text.id,
          title: text.title || text.id,
          author: text.author || '',
          count: positions.length,
          positions,
          totalOccurrences: totalForLemma,
          lineCount: text.lineStarts.length
        });
      }
    }
    hits.sort((a, b) => b.count - a.count);
    return hits;
  }

  render() {
    const container = document.getElementById('resultsContainer');
    if (!container) return;
    container.innerHTML = `
      <div class="space-y-4">
        ${this.renderForm()}
        ${this.renderBody()}
      </div>
    `;
    this.attachHandlers();
  }

  renderForm() {
    return `
      <div class="rounded-2xl border border-slate-200 bg-slate-50/70 p-4 space-y-3">
        <h3 class="text-sm font-semibold uppercase tracking-wide text-slate-500">Lemmasuche nach Versposition</h3>
        <p class="text-xs text-slate-600">
          Sucht Lemmata am Anfang oder Ende eines Verses. Genauer: am ersten bzw. letzten Wort
          <em>mit Lemma-Zuordnung</em>, denn nur solche Wörter sind im Index adressierbar.
          Nützlich für Reim- und Versendanalyse
          (z.B. <code class="rounded bg-white px-1.5 py-0.5 font-mono">minne</code> am Versende).
          Nur Verstexte (mit <code class="rounded bg-white px-1.5 py-0.5 font-mono">&lt;l&gt;</code>); Prosa wird ignoriert.
        </p>
        <div class="grid gap-3 sm:grid-cols-4">
          <div class="sm:col-span-2">
            <label class="block">
              <span class="text-xs font-medium text-slate-600">Lemma</span>
              <div class="relative mt-1">
                <input id="vpsQuery" type="text" autocomplete="off" role="combobox"
                  aria-autocomplete="list" aria-controls="vpsAutocomplete" aria-expanded="false"
                  value="${escapeAttr(this.state.query)}"
                  placeholder="z.B. minne"
                  class="w-full rounded-lg border border-slate-200 bg-white px-3 py-2 text-sm focus:border-brand-400 focus:outline-none"/>
                <div id="vpsAutocomplete" role="listbox"
                  class="absolute left-0 right-0 top-full z-30 mt-1 hidden max-h-72 overflow-y-auto rounded-lg border border-slate-200 bg-white shadow-lg"></div>
              </div>
            </label>
          </div>
          <label class="block">
            <span class="text-xs font-medium text-slate-600">Position</span>
            <select id="vpsPosition" class="mt-1 w-full rounded-lg border border-slate-200 bg-white px-3 py-2 text-sm focus:border-brand-400 focus:outline-none">
              <option value="start"${this.state.position === 'start' ? ' selected' : ''}>Versanfang</option>
              <option value="end"${this.state.position === 'end' ? ' selected' : ''}>Versende</option>
            </select>
          </label>
          <div class="flex items-end">
            <button id="vpsSearchBtn" type="button" class="w-full rounded-lg border border-brand-200 bg-brand-50 px-4 py-2 text-sm font-medium text-brand-700 hover:border-brand-400 hover:bg-brand-100">Suchen</button>
          </div>
        </div>
      </div>
    `;
  }

  renderBody() {
    if (!this.state.query) {
      return '<div class="rounded-2xl border border-dashed border-slate-200 bg-white p-8 text-center text-sm text-slate-500">Bitte Lemma eingeben und auf „Suchen" klicken.</div>';
    }
    if (!this.state.resolvedLemma) {
      return `
        <div class="rounded-2xl border border-amber-200 bg-amber-50 p-4 text-sm text-amber-800">
          Kein Lemma gefunden für <code class="font-mono">${escapeHtml(this.state.query)}</code>.
          Versuchen Sie eine andere Schreibweise oder eine Variante.
        </div>
      `;
    }

    const lemma = this.state.resolvedLemma;
    const candidates = this.state.candidates.length > 1
      ? `<div class="mt-2 text-xs text-slate-500">Weitere Treffer: ${this.state.candidates.slice(1, 8).map(c => `<span class="mr-2 rounded bg-slate-100 px-1.5 py-0.5 font-mono">${escapeHtml(c.lemma || c.id)}</span>`).join('')}</div>`
      : '';

    const hits = this.findHits(lemma.id);
    const positionLabel = this.state.position === 'start' ? 'Versanfang' : 'Versende';
    const cleanId = lemma.id.replace(/^lemma_/, '');

    if (hits.length === 0) {
      return `
        <div class="rounded-2xl border border-slate-200 bg-white p-6 text-sm">
          <div class="font-semibold text-slate-800">${escapeHtml(lemma.lemma || lemma.id)}</div>
          <div class="mt-1 text-xs text-slate-500">${escapeHtml(lemma.id)}</div>
          <p class="mt-3 text-slate-600">Keine Treffer am ${positionLabel} im Versdichtungs-Korpus.</p>
          ${candidates}
        </div>
      `;
    }

    const totalHits = hits.reduce((s, h) => s + h.count, 0);

    const rows = hits.map(h => {
      const ratio = h.totalOccurrences > 0 ? (h.count / h.totalOccurrences * 100) : 0;
      const href = `../korpus.html?textId=${encodeURIComponent(h.id)}&lemmaIds=${encodeURIComponent(lemma.id)}`;
      return `
        <li>
          <a href="${href}" target="_blank" rel="noopener"
            class="flex items-center justify-between gap-3 rounded px-2 py-1.5 hover:bg-slate-50">
            <span class="font-mono text-xs text-brand-700 w-16 flex-shrink-0">${escapeHtml(h.id)}</span>
            <span class="flex-1 truncate text-xs text-slate-600">${escapeHtml(h.title)}${h.author ? ` <span class="text-slate-400">, ${escapeHtml(h.author)}</span>` : ''}</span>
            <span class="tabular-nums text-xs text-slate-700 flex-shrink-0">
              <strong>${h.count.toLocaleString('de-DE')}</strong>
              <span class="text-slate-400">/${h.totalOccurrences.toLocaleString('de-DE')}</span>
              <span class="ml-1 text-slate-400">(${ratio.toFixed(0)}%)</span>
            </span>
          </a>
        </li>
      `;
    }).join('');

    // #187: alle POS-Werte anzeigen (Fallback: Erstwert aus altem Cache)
    const posLabel = (lemma.posAll || (lemma.pos ? [lemma.pos] : [])).join(' ');

    return `
      <div class="rounded-2xl border border-slate-200 bg-white p-4 space-y-3">
        <header class="flex items-start justify-between gap-4">
          <div>
            <div class="text-xs uppercase tracking-wide text-slate-500">Lemma am ${positionLabel}</div>
            <div class="text-lg font-semibold text-brand-700">
              <a href="../lemma/?id=${escapeHtml(cleanId)}" target="_blank" rel="noopener" class="hover:underline">${escapeHtml(lemma.lemma || lemma.id)}</a>
              ${posLabel ? `<span class="ml-2 rounded bg-slate-100 px-1.5 py-0.5 text-xs font-mono text-slate-600">${escapeHtml(posLabel)}</span>` : ''}
            </div>
            <div class="text-xs text-slate-500">${escapeHtml(lemma.id)}</div>
            ${candidates}
          </div>
          <div class="text-right text-xs text-slate-500">
            <div>${hits.length.toLocaleString('de-DE')} Texte</div>
            <div>${totalHits.toLocaleString('de-DE')} Treffer am ${positionLabel}</div>
          </div>
        </header>
        <div class="text-xs text-slate-500 border-t border-slate-100 pt-3">
          Spalte: <strong>Treffer am ${positionLabel}</strong> / Gesamtvorkommen im Text (Anteil). Klick öffnet Text im Reader mit Highlighting.
        </div>
        <ul class="grid gap-1 sm:grid-cols-2">
          ${rows}
        </ul>
      </div>
    `;
  }

  renderError(msg) {
    const container = document.getElementById('resultsContainer');
    if (!container) return;
    container.innerHTML = `
      <div class="rounded-2xl border border-red-200 bg-red-50 p-4 text-sm text-red-700">
        ${escapeHtml(msg)}
      </div>
    `;
  }

  // Autocomplete-Pattern (DESIGN.md §Live-Autocomplete-Dropdown, Port aus #113).
  renderAutocomplete() {
    const dd = document.getElementById('vpsAutocomplete');
    const input = document.getElementById('vpsQuery');
    if (!dd) return;
    const items = this.state.autocompleteItems || [];
    if (!this.state.autocompleteOpen || items.length === 0) {
      dd.classList.add('hidden');
      dd.innerHTML = '';
      if (input) input.setAttribute('aria-expanded', 'false');
      return;
    }
    const idx = this.state.autocompleteIndex;
    dd.innerHTML = items.map((l, i) => {
      const active = i === idx;
      const cls = active ? 'bg-brand-50 text-brand-800' : 'text-slate-700 hover:bg-slate-50';
      const acPosLabel = (l.posAll || (l.pos ? [l.pos] : [])).join(' ');
      const pos = acPosLabel ? `<span class="ml-1 rounded bg-slate-100 px-1 text-[10px] font-mono text-slate-600">${escapeHtml(acPosLabel)}</span>` : '';
      return `<button type="button" role="option" data-vps-ac-idx="${i}"
        aria-selected="${active}"
        class="block w-full cursor-pointer px-3 py-2 text-left text-sm ${cls}">
        <span class="font-medium">${escapeHtml(l.lemma || l.id)}</span>${pos}
        <span class="ml-2 text-xs font-mono text-slate-400">${escapeHtml(l.id)}</span>
      </button>`;
    }).join('');
    dd.classList.remove('hidden');
    if (input) input.setAttribute('aria-expanded', 'true');
    const activeEl = dd.querySelector(`[data-vps-ac-idx="${idx}"]`);
    if (activeEl) activeEl.scrollIntoView({ block: 'nearest' });
  }

  updateAutocomplete(query) {
    const trimmed = (query || '').trim();
    if (!trimmed) {
      this.state.autocompleteItems = [];
      this.state.autocompleteIndex = -1;
      this.state.autocompleteOpen = false;
      this.renderAutocomplete();
      return;
    }
    // getLemmaAutocompleteMatches statt resolveQuery: liefert echte prefix-
    // Vorschläge (startsWith + includes), nicht den Stage-1-Early-Return.
    this.state.autocompleteItems = this.authorityManager.getLemmaAutocompleteMatches(trimmed, AUTOCOMPLETE_LIMIT);
    this.state.autocompleteIndex = -1;
    this.state.autocompleteOpen = this.state.autocompleteItems.length > 0;
    this.renderAutocomplete();
  }

  closeAutocomplete() {
    this.state.autocompleteOpen = false;
    this.state.autocompleteIndex = -1;
    this.renderAutocomplete();
  }

  attachHandlers() {
    const runSearch = () => {
      const input = document.getElementById('vpsQuery');
      if (!input) return;
      this.state.query = input.value;
      this.closeAutocomplete();
      const { resolved, candidates } = this.resolveQuery(this.state.query);
      // Explizite Autocomplete-Auswahl (#163) schlägt die String-Auflösung —
      // aber nur solange der Query-Text noch der gewählten Form entspricht.
      const sel = this.state.selectedLemma;
      const useSelected = sel && (sel.lemma || sel.id) === (this.state.query || '').trim();
      this.state.resolvedLemma = useSelected ? sel : resolved;
      this.state.candidates = candidates;
      this.render();
      const newInput = document.getElementById('vpsQuery');
      if (newInput) {
        newInput.focus();
        newInput.setSelectionRange(newInput.value.length, newInput.value.length);
      }
    };

    document.getElementById('vpsSearchBtn')?.addEventListener('click', runSearch);

    const input = document.getElementById('vpsQuery');
    if (input) {
      input.addEventListener('input', (e) => {
        // Manuelle Eingabe invalidiert eine frühere Dropdown-Auswahl (#163).
        this.state.selectedLemma = null;
        this.updateAutocomplete(e.target.value);
      });
      input.addEventListener('keydown', (e) => {
        const open = this.state.autocompleteOpen && this.state.autocompleteItems.length > 0;
        if (e.key === 'Enter') {
          e.preventDefault();
          if (open && this.state.autocompleteIndex >= 0) {
            const c = this.state.autocompleteItems[this.state.autocompleteIndex];
            input.value = c.lemma || c.id;
            this.state.selectedLemma = c;
            this.closeAutocomplete();
            runSearch();
            return;
          }
          runSearch();
        } else if (e.key === 'ArrowDown') {
          if (!open) return;
          e.preventDefault();
          this.state.autocompleteIndex = (this.state.autocompleteIndex + 1) % this.state.autocompleteItems.length;
          this.renderAutocomplete();
        } else if (e.key === 'ArrowUp') {
          if (!open) return;
          e.preventDefault();
          const n = this.state.autocompleteItems.length;
          this.state.autocompleteIndex = (this.state.autocompleteIndex - 1 + n) % n;
          this.renderAutocomplete();
        } else if (e.key === 'Escape') {
          if (open) { e.preventDefault(); this.closeAutocomplete(); }
        }
      });
      input.addEventListener('focus', () => {
        if (input.value.trim() && this.state.autocompleteItems.length > 0) {
          this.state.autocompleteOpen = true;
          this.renderAutocomplete();
        }
      });
      input.addEventListener('blur', () => setTimeout(() => this.closeAutocomplete(), 150));
    }

    const dd = document.getElementById('vpsAutocomplete');
    if (dd) {
      dd.addEventListener('mousedown', (e) => {
        const btn = e.target.closest('[data-vps-ac-idx]');
        if (!btn) return;
        e.preventDefault();
        const idx = parseInt(btn.getAttribute('data-vps-ac-idx'), 10);
        const c = this.state.autocompleteItems[idx];
        if (!c) return;
        const inputEl = document.getElementById('vpsQuery');
        if (inputEl) inputEl.value = c.lemma || c.id;
        this.state.selectedLemma = c;
        this.closeAutocomplete();
        runSearch();
      });
    }

    document.getElementById('vpsPosition')?.addEventListener('change', (e) => {
      this.state.position = e.target.value;
      if (this.state.resolvedLemma) this.render();
    });
  }
}

function escapeHtml(s) {
  if (s == null) return '';
  return String(s).replace(/[&<>"']/g, c => (
    { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]
  ));
}

function escapeAttr(s) {
  return escapeHtml(s);
}
