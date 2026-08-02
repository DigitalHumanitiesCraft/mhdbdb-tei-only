/**
 * MHDBDB Playground - Kookkurrenz-Ranking
 *
 * "Welche Lemmata stehen am häufigsten bei X?" (DWDS-Style).
 * Window-Scan über text.words für jede Position von Lemma X, zählt
 * Nachbar-Lemmata in einer Map. Reines Lese-Pattern auf v4.1.x-Corpus-Index,
 * kein neuer Build-Schritt.
 *
 * Issue: #107
 */

import { getNavigationEpoch } from '../core/router.js';

const DEFAULT_STATE = Object.freeze({
  query: '',
  resolvedLemma: null,
  selectedLemma: null,        // explizite Autocomplete-Auswahl (#163) — schlägt resolveQuery
  candidates: [],
  window: 10,                 // ± Nachbarn pro Vorkommen
  topN: 50,
  minFreq: 2,                 // Cutoff fuer Long-Tail
  posMode: 'content',         // 'all' | 'content' (NOM/VRB/ADJ/ADV) | 'nom' | 'vrb' | 'adj'
  filter: '',                 // Lemma-Name-Substring
  computing: false,
  progress: 0,
  result: null,               // {target, totalOccurrences, partners: [{lemmaId, count}, ...]}
  // Autocomplete (Port aus #113-Pattern)
  autocompleteOpen: false,
  autocompleteIndex: -1,
  autocompleteItems: []
});

const WINDOW_OPTIONS = [3, 5, 10, 15, 25];
const TOP_N_OPTIONS = [25, 50, 100, 250];
const AUTOCOMPLETE_LIMIT = 8;

// Async-Chunking analog concept-distribution.js: ueber CHUNK_BUDGET_MS Rechenzeit
// yieldToMain(), damit UI reagibel bleibt. Worst-Case "der" ~800k Positionen *
// window=10 -> 16M Map-Ops -> ohne Yield ~800ms Block.
const CHUNK_BUDGET_MS = 30;

function yieldToMain() {
  return new Promise(resolve => {
    const ch = new MessageChannel();
    ch.port1.onmessage = () => resolve();
    ch.port2.postMessage(null);
  });
}

export class CooccurrenceRanking {
  constructor(getCorpusTexts, authorityManager) {
    this.getCorpusTexts = getCorpusTexts;
    this.authorityManager = authorityManager;
    this.state = { ...DEFAULT_STATE };
    this._lemmaMap = null;
    this._abortToken = 0;
  }

  show() {
    const texts = this.getCorpusTexts();
    if (!texts || texts.length === 0) {
      this.renderError('Korpus ist noch nicht geladen. Bitte einen Moment warten und Button erneut klicken.');
      return;
    }
    this.ensureLemmaMap();
    this.render();
  }

  ensureLemmaMap() {
    if (this._lemmaMap) return;
    this._lemmaMap = new Map();
    const lemmata = this.authorityManager?.authorityData?.lemmata || [];
    for (const l of lemmata) {
      if (l?.id) this._lemmaMap.set(l.id, l);
    }
  }

  resolveQuery(query) {
    const trimmed = (query || '').trim();
    if (!trimmed) return { resolved: null, candidates: [] };
    const matches = this.authorityManager.searchLemmaByOrthography(trimmed) || [];
    if (matches.length === 0) return { resolved: null, candidates: [] };
    return { resolved: matches[0], candidates: matches.slice(0, 12) };
  }

  async computeCooccurrences(targetLemmaId, window, onProgress) {
    const texts = this.getCorpusTexts() || [];
    const counts = new Map();
    let totalOccurrences = 0;
    let chunkStart = performance.now();
    const myToken = this._abortToken;
    const myEpoch = getNavigationEpoch();

    for (let i = 0; i < texts.length; i++) {
      // Abort on new search in this module (token) OR router navigation
      // to another view (epoch, #159) while we were running.
      if (this._abortToken !== myToken || getNavigationEpoch() !== myEpoch) return null;

      const text = texts[i];
      const positions = text.lemmata?.[targetLemmaId];
      if (positions && positions.length > 0) {
        const words = text.words;
        if (words && words.length > 0) {
          const wLen = words.length;
          totalOccurrences += positions.length;
          for (const pos of positions) {
            const start = Math.max(0, pos - window);
            const end = Math.min(wLen, pos + window + 1);
            for (let k = start; k < end; k++) {
              if (k === pos) continue;
              const neighbor = words[k];
              if (!neighbor || neighbor === targetLemmaId) continue;
              counts.set(neighbor, (counts.get(neighbor) || 0) + 1);
            }
          }
        }
      }

      if (performance.now() - chunkStart > CHUNK_BUDGET_MS) {
        if (onProgress) onProgress((i + 1) / texts.length);
        await yieldToMain();
        if (this._abortToken !== myToken || getNavigationEpoch() !== myEpoch) return null;
        chunkStart = performance.now();
      }
    }

    if (onProgress) onProgress(1);
    return { counts, totalOccurrences };
  }

  /**
   * Pruefen, ob die POS-Tags eines Lemmas dem aktuellen posMode entsprechen.
   * posTags ist posAll[] aus dem Authority-Index (v1.6.0, #161): ein Eintrag
   * pro <pos>-Element; einzelne Eintraege koennen Legacy-Compound-Tags wie
   * "ART CNJ" sein, daher werden sie zusaetzlich an Whitespace gesplittet.
   * Wir akzeptieren ein Partner-Lemma, sobald MINDESTENS EIN Token matched
   * (z.B. NOM+VRB zaehlt als Nomen UND als Verb) — generoeser ist hier
   * besser, sonst entgehen ambige Faelle mit Inhaltswort-Charakter.
   */
  posPasses(posTags) {
    if (this.state.posMode === 'all') return true;
    if (!posTags || !posTags.length) return false;
    const tokens = posTags.flatMap(p => p.split(/\s+/));
    if (this.state.posMode === 'content') {
      return tokens.some(t => t === 'NOM' || t === 'VRB' || t === 'ADJ' || t === 'ADV');
    }
    if (this.state.posMode === 'nom') return tokens.includes('NOM');
    if (this.state.posMode === 'vrb') return tokens.includes('VRB');
    if (this.state.posMode === 'adj') return tokens.includes('ADJ');
    return true;
  }

  enrichPartners(counts) {
    const out = [];
    for (const [lemmaId, count] of counts) {
      if (count < this.state.minFreq) continue;
      const lemma = this._lemmaMap?.get(lemmaId);
      const posTags = lemma?.posAll || (lemma?.pos ? [lemma.pos] : []);
      if (!this.posPasses(posTags)) continue;
      out.push({
        lemmaId,
        lemma: lemma?.lemma || lemmaId,
        pos: posTags.join(' '),
        count
      });
    }
    out.sort((a, b) => b.count - a.count);
    return out;
  }

  filterPartners(partners) {
    const f = this.state.filter.trim().toLowerCase();
    if (!f) return partners;
    return partners.filter(p => (p.lemma || p.lemmaId).toLowerCase().includes(f));
  }

  async runSearch() {
    const { resolved, candidates } = this.resolveQuery(this.state.query);
    // Explizite Autocomplete-Auswahl (#163) schlägt die String-Auflösung —
    // aber nur solange der Query-Text noch der gewählten Form entspricht
    // (Tippen setzt selectedLemma im input-Handler zurück).
    const sel = this.state.selectedLemma;
    const useSelected = sel && (sel.lemma || sel.id) === (this.state.query || '').trim();
    this.state.resolvedLemma = useSelected ? sel : resolved;
    this.state.candidates = candidates;
    this.state.result = null;
    if (!this.state.resolvedLemma) {
      this.render();
      return;
    }
    this._abortToken += 1;
    this.state.computing = true;
    this.state.progress = 0;
    this.render();

    const myToken = this._abortToken;
    const myEpoch = getNavigationEpoch();
    const target = this.state.resolvedLemma;
    const result = await this.computeCooccurrences(target.id, this.state.window, (p) => {
      if (this._abortToken !== myToken) return;
      this.state.progress = p;
      this.updateProgressBar();
    });
    if (this._abortToken !== myToken || getNavigationEpoch() !== myEpoch) return;
    if (!result) {
      this.state.computing = false;
      return;
    }

    const partners = this.enrichPartners(result.counts);
    this.state.result = {
      targetLemmaId: target.id,
      totalOccurrences: result.totalOccurrences,
      partners,
      _rawCounts: result.counts // fuer POS-Mode-Switching ohne Re-Compute
    };
    this.state.computing = false;
    this.render();
  }

  updateProgressBar() {
    const bar = document.getElementById('coRkProgressBar');
    if (bar) {
      const pct = Math.round(this.state.progress * 100);
      bar.style.width = `${pct}%`;
    }
    const label = document.getElementById('coRkProgressLabel');
    if (label) {
      label.textContent = `Berechne Kookkurrenzen … ${Math.round(this.state.progress * 100)}%`;
    }
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
    const windowOpts = WINDOW_OPTIONS
      .map(w => `<option value="${w}"${this.state.window === w ? ' selected' : ''}>± ${w} annot. Tokens</option>`).join('');
    const topNOpts = TOP_N_OPTIONS
      .map(n => `<option value="${n}"${this.state.topN === n ? ' selected' : ''}>Top ${n}</option>`).join('');
    return `
      <div class="rounded-2xl border border-slate-200 bg-slate-50/70 p-4 space-y-3">
        <h3 class="text-sm font-semibold uppercase tracking-wide text-slate-500">Kookkurrenz-Ranking</h3>
        <p class="text-xs text-slate-600">
          „Welche Lemmata stehen am häufigsten bei X?" Window-Scan über alle Vorkommen
          des Eingabe-Lemmas, zählt Nachbar-Lemmata. Mittelhochdeutsche Sonderzeichen
          werden normalisiert (â→a, ê→e, ü→ue).
        </p>
        <div class="grid gap-3 sm:grid-cols-4">
          <div class="sm:col-span-2">
            <label class="block">
              <span class="text-xs font-medium text-slate-600">Lemma</span>
              <div class="relative mt-1">
                <input id="coRkQuery" type="text" autocomplete="off" role="combobox"
                  aria-autocomplete="list" aria-controls="coRkAutocomplete" aria-expanded="false"
                  value="${escapeAttr(this.state.query)}"
                  placeholder="z.B. minne"
                  class="w-full rounded-lg border border-slate-200 bg-white px-3 py-2 text-sm focus:border-brand-400 focus:outline-none"/>
                <div id="coRkAutocomplete" role="listbox"
                  class="absolute left-0 right-0 top-full z-30 mt-1 hidden max-h-72 overflow-y-auto rounded-lg border border-slate-200 bg-white shadow-lg"></div>
              </div>
            </label>
          </div>
          <label class="block">
            <span class="text-xs font-medium text-slate-600">Kontextfenster</span>
            <select id="coRkWindow" class="mt-1 w-full rounded-lg border border-slate-200 bg-white px-3 py-2 text-sm">${windowOpts}</select>
          </label>
          <label class="block">
            <span class="text-xs font-medium text-slate-600">Mindest-Frequenz</span>
            <input id="coRkMinFreq" type="number" min="1" max="10000"
              value="${this.state.minFreq}"
              class="mt-1 w-full rounded-lg border border-slate-200 bg-white px-3 py-2 text-sm focus:border-brand-400 focus:outline-none"/>
          </label>
        </div>
        <div class="flex flex-wrap items-center gap-3">
          <label class="flex items-center gap-2 text-xs text-slate-600">
            <span class="font-medium">Wortart-Filter</span>
            <select id="coRkPosMode" class="rounded-lg border border-slate-200 bg-white px-2 py-1.5 text-xs">
              <option value="content"${this.state.posMode === 'content' ? ' selected' : ''}>Inhaltswörter (NOM/VRB/ADJ/ADV)</option>
              <option value="nom"${this.state.posMode === 'nom' ? ' selected' : ''}>Nur Nomen (NOM)</option>
              <option value="vrb"${this.state.posMode === 'vrb' ? ' selected' : ''}>Nur Verben (VRB)</option>
              <option value="adj"${this.state.posMode === 'adj' ? ' selected' : ''}>Nur Adjektive (ADJ)</option>
              <option value="all"${this.state.posMode === 'all' ? ' selected' : ''}>Alle (inkl. Funktionswörter)</option>
            </select>
          </label>
          <select id="coRkTopN" class="rounded-lg border border-slate-200 bg-white px-3 py-1.5 text-xs">${topNOpts}</select>
          <button id="coRkSearchBtn" type="button" class="rounded-lg border border-brand-200 bg-brand-50 px-4 py-1.5 text-sm font-medium text-brand-700 hover:border-brand-400 hover:bg-brand-100">Suchen</button>
        </div>
      </div>
    `;
  }

  renderBody() {
    if (this.state.computing) {
      return `
        <div class="rounded-2xl border border-slate-200 bg-white p-6 space-y-3">
          <div id="coRkProgressLabel" class="text-sm text-slate-600">Berechne Kookkurrenzen … ${Math.round(this.state.progress * 100)}%</div>
          <div class="h-2 w-full overflow-hidden rounded-full bg-slate-100">
            <div id="coRkProgressBar" class="h-full rounded-full bg-brand-400 transition-all" style="width: ${Math.round(this.state.progress * 100)}%"></div>
          </div>
        </div>
      `;
    }

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
    if (!this.state.result) {
      return '<div class="rounded-2xl border border-dashed border-slate-200 bg-white p-8 text-center text-sm text-slate-500">Auf „Suchen" klicken, um Berechnung zu starten.</div>';
    }

    return this.renderResults();
  }

  renderResults() {
    const lemma = this.state.resolvedLemma;
    const { totalOccurrences, partners } = this.state.result;
    const cleanId = lemma.id.replace(/^lemma_/, '');
    // Alle POS-Tags wie in enrichPartners(), nicht nur den Erstwert —
    // sonst zeigt der Header fuer Multi-POS-Lemmata (salve: NOM VRB)
    // weniger als die Partner-Zeilen daneben (Review-Finding PR #177).
    const posLabel = (lemma.posAll || (lemma.pos ? [lemma.pos] : [])).join(' ');

    const candidates = this.state.candidates.length > 1
      ? `<div class="mt-2 text-xs text-slate-500">Weitere Treffer: ${this.state.candidates.slice(1, 8).map(c => `<span class="mr-2 rounded bg-slate-100 px-1.5 py-0.5 font-mono">${escapeHtml(c.lemma || c.id)}</span>`).join('')}</div>`
      : '';

    if (partners.length === 0) {
      return `
        <div class="rounded-2xl border border-slate-200 bg-white p-6 text-sm">
          <div class="font-semibold text-slate-800">${escapeHtml(lemma.lemma || lemma.id)}</div>
          <div class="mt-1 text-xs text-slate-500">${escapeHtml(lemma.id)}</div>
          <p class="mt-3 text-slate-600">${totalOccurrences.toLocaleString('de-DE')} Vorkommen, aber keine Nachbar-Lemmata mit Frequenz ≥ ${this.state.minFreq} im Kontextfenster ± ${this.state.window}.</p>
          ${candidates}
        </div>
      `;
    }

    const filtered = this.filterPartners(partners);
    const visible = filtered.slice(0, this.state.topN);

    const trs = visible.map((p, idx) => {
      const partnerClean = p.lemmaId.replace(/^lemma_/, '');
      // Klick auf Partner-Lemma → Multi-Lemma-Suche mit beiden Lemmata vorbefuellt.
      // Ohne Authority-Eintrag ist p.lemma die rohe ID ("lemma_NNN"), die die
      // Multi-Lemma-Suche nicht aufloesen kann — dann die numerische ID
      // uebergeben (deren Route akzeptiert /^\d+$/ direkt).
      const partnerTerm = p.lemma && p.lemma !== p.lemmaId ? p.lemma : partnerClean;
      const multiHref = `#multi-lemma&lemmata=${encodeURIComponent(lemma.lemma || cleanId)},${encodeURIComponent(partnerTerm)}&mode=proximity&dist=${this.state.window}`;
      return `
        <tr class="border-b border-slate-100 hover:bg-slate-50">
          <td class="px-3 py-1.5 text-right tabular-nums text-xs text-slate-500">${idx + 1}</td>
          <td class="px-3 py-1.5">
            <a href="../lemma/?id=${escapeAttr(partnerClean)}" target="_blank" rel="noopener" class="font-medium text-brand-700 hover:underline">${escapeHtml(p.lemma)}</a>
            ${p.pos ? `<span class="ml-1 rounded bg-slate-100 px-1 text-[10px] font-mono text-slate-600">${escapeHtml(p.pos)}</span>` : ''}
          </td>
          <td class="px-3 py-1.5 text-right tabular-nums text-slate-700">${p.count.toLocaleString('de-DE')}</td>
          <td class="px-3 py-1.5 text-right">
            <a href="${multiHref}" class="text-xs text-brand-700 hover:underline" title="Beide Lemmata in der Multi-Lemma-Suche (Distanz ${this.state.window})">→ Belege</a>
          </td>
        </tr>
      `;
    }).join('');

    const truncated = filtered.length > visible.length;

    return `
      <div class="rounded-2xl border border-slate-200 bg-white p-4 space-y-3">
        <header class="flex items-start justify-between gap-4">
          <div>
            <div class="text-xs uppercase tracking-wide text-slate-500">Zentrum-Lemma</div>
            <div class="text-lg font-semibold text-brand-700">
              <a href="../lemma/?id=${escapeAttr(cleanId)}" target="_blank" rel="noopener" class="hover:underline">${escapeHtml(lemma.lemma || lemma.id)}</a>
              ${posLabel ? `<span class="ml-2 rounded bg-slate-100 px-1.5 py-0.5 text-xs font-mono text-slate-600">${escapeHtml(posLabel)}</span>` : ''}
            </div>
            <div class="text-xs text-slate-500">${escapeHtml(lemma.id)} · Kontextfenster ± ${this.state.window} · Mindest-Frequenz ${this.state.minFreq}</div>
            ${candidates}
          </div>
          <div class="text-right text-xs text-slate-500">
            <div>${totalOccurrences.toLocaleString('de-DE')} Vorkommen</div>
            <div>${partners.length.toLocaleString('de-DE')} Partner ≥ ${this.state.minFreq}</div>
          </div>
        </header>

        <div class="flex items-center gap-3 rounded-xl border border-slate-200 bg-slate-50/60 p-3 text-sm">
          <label class="flex flex-1 items-center gap-2 min-w-[200px]">
            <span class="text-xs font-medium text-slate-600">Partner-Filter</span>
            <input id="coRkFilter" type="text" autocomplete="off"
              value="${escapeAttr(this.state.filter)}"
              placeholder="Lemma-Name eingrenzen"
              class="w-full rounded-lg border border-slate-200 bg-white px-2 py-1 text-xs focus:border-brand-400 focus:outline-none" />
          </label>
          <span class="text-xs text-slate-500">${visible.length.toLocaleString('de-DE')} / ${filtered.length.toLocaleString('de-DE')} angezeigt</span>
        </div>

        <div class="overflow-x-auto rounded-2xl border border-slate-200">
          <table class="w-full text-sm">
            <thead class="bg-slate-50">
              <tr>
                <th class="px-3 py-2 text-right text-xs font-semibold text-slate-600 w-12">#</th>
                <th class="px-3 py-2 text-left text-xs font-semibold text-slate-600">Partner-Lemma</th>
                <th class="px-3 py-2 text-right text-xs font-semibold text-slate-600">Kookkurrenz-Frequenz</th>
                <th class="px-3 py-2 text-right text-xs font-semibold text-slate-600">Belege</th>
              </tr>
            </thead>
            <tbody>${trs}</tbody>
          </table>
        </div>
        ${truncated ? `<div class="text-center text-xs text-slate-500">Zeige Top ${visible.length} von ${filtered.length.toLocaleString('de-DE')} Treffern. Top-N oben erhöhen für mehr.</div>` : ''}
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

  // Autocomplete-Pattern (DESIGN.md §Live autocomplete dropdown, Port aus #113).
  renderAutocomplete() {
    const dd = document.getElementById('coRkAutocomplete');
    const input = document.getElementById('coRkQuery');
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
      const posTags = (l.posAll || (l.pos ? [l.pos] : [])).join(' ');
      const pos = posTags ? `<span class="ml-1 rounded bg-slate-100 px-1 text-[10px] font-mono text-slate-600">${escapeHtml(posTags)}</span>` : '';
      return `<button type="button" role="option" data-co-rk-ac-idx="${i}"
        aria-selected="${active}"
        class="block w-full cursor-pointer px-3 py-2 text-left text-sm ${cls}">
        <span class="font-medium">${escapeHtml(l.lemma || l.id)}</span>${pos}
        <span class="ml-2 text-xs font-mono text-slate-400">${escapeHtml(l.id)}</span>
      </button>`;
    }).join('');
    dd.classList.remove('hidden');
    if (input) input.setAttribute('aria-expanded', 'true');
    const activeEl = dd.querySelector(`[data-co-rk-ac-idx="${idx}"]`);
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
      const input = document.getElementById('coRkQuery');
      if (!input) return;
      this.state.query = input.value;
      this.closeAutocomplete();
      this.runSearch();
    };

    document.getElementById('coRkSearchBtn')?.addEventListener('click', runSearch);

    const input = document.getElementById('coRkQuery');
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

    const dd = document.getElementById('coRkAutocomplete');
    if (dd) {
      dd.addEventListener('mousedown', (e) => {
        const btn = e.target.closest('[data-co-rk-ac-idx]');
        if (!btn) return;
        e.preventDefault();
        const idx = parseInt(btn.getAttribute('data-co-rk-ac-idx'), 10);
        const c = this.state.autocompleteItems[idx];
        if (!c) return;
        const inputEl = document.getElementById('coRkQuery');
        if (inputEl) inputEl.value = c.lemma || c.id;
        this.state.selectedLemma = c;
        this.closeAutocomplete();
        runSearch();
      });
    }

    document.getElementById('coRkWindow')?.addEventListener('change', (e) => {
      this.state.window = parseInt(e.target.value, 10) || DEFAULT_STATE.window;
    });
    document.getElementById('coRkMinFreq')?.addEventListener('change', (e) => {
      const v = parseInt(e.target.value, 10);
      this.state.minFreq = isNaN(v) || v < 1 ? 1 : v;
      // minFreq wirkt in enrichPartners (Post-Compute) — die Partnerliste
      // muss aus den Roh-Counts neu gefiltert werden, sonst widerspricht
      // der Header der Tabelle (#167 Finding 21; analog posMode-Handler).
      if (this.state.result) {
        this.state.result.partners = this.enrichPartners(this.state.result._rawCounts || new Map());
        this.render();
      }
    });
    document.getElementById('coRkTopN')?.addEventListener('change', (e) => {
      this.state.topN = parseInt(e.target.value, 10) || DEFAULT_STATE.topN;
      if (this.state.result) this.render();
    });
    document.getElementById('coRkPosMode')?.addEventListener('change', (e) => {
      this.state.posMode = e.target.value;
      // POS-Filter wirkt erst bei enrichPartners (Post-Compute), reicht re-render.
      if (this.state.result) {
        const partners = this.enrichPartners(this.state.result._rawCounts || new Map());
        this.state.result.partners = partners;
        this.render();
      }
    });

    const filter = document.getElementById('coRkFilter');
    if (filter) {
      filter.addEventListener('input', (e) => {
        this.state.filter = e.target.value;
        this.render();
        const newInput = document.getElementById('coRkFilter');
        if (newInput) {
          newInput.focus();
          newInput.setSelectionRange(newInput.value.length, newInput.value.length);
        }
      });
    }
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
