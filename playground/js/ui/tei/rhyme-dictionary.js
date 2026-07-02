/**
 * MHDBDB Playground - Reim-Wörterbuch
 *
 * "Welche Lemmata reimen sich auf X?" — Minimalvariante (lemma-basiert)
 * aus dem Reim-Audit in #106: scannt die Versende-Positionen (lineEnds[]
 * aus Corpus-Index v4.1.x), sammelt die Lemmata der unmittelbar
 * benachbarten Versenden (±1 Vers, Paarreim-Annahme) und behält Paare,
 * deren MHG-normalisierte Lemma-Formen im Auslaut übereinstimmen
 * (3-Letter-Suffix; sind beide Formen kurz, ≤4 Zeichen, genügt das
 * 2-Letter-Suffix, damit z.B. wîp : lîp und tac : slac gefunden werden).
 *
 * Grenzen der Minimalvariante (bewusst, siehe Issue #106):
 * - lemma-basiert, nicht token-basiert — die Original-Schreibung am
 *   Versende (Flexionsendung!) wäre erst mit Index-Erweiterung möglich
 * - strukturell, nicht phonetisch — kein sauberer Reim vs. Assonanz
 * - Paarreim-Annahme — Kreuzreime (ABAB) mit Distanz 2 entgehen dem Scan
 * - nur Verstexte — Prosa (leere lineEnds) wird ignoriert
 *
 * Issue: #106
 */

const DEFAULT_STATE = Object.freeze({
  query: '',
  resolvedLemma: null,
  candidates: [],
  textFilter: '',             // Sigle/Titel/Autor-Substring, optional
  minCount: 1,                // Mindestanzahl Reimpaare pro Partner
  computing: false,
  progress: 0,
  result: null,               // {endOccurrences, verseTextCount, scannedTextCount, partners}
  // Autocomplete (Pattern aus #107/#113)
  autocompleteOpen: false,
  autocompleteIndex: -1,
  autocompleteItems: []
});

const AUTOCOMPLETE_LIMIT = 8;
const MAX_VISIBLE_PARTNERS = 200;
const BELEGE_PROXIMITY_DIST = 15;   // Reimpaar = benachbarte Verse; ±15 Wörter decken zwei Verse ab

// Async-Chunking analog cooccurrence-ranking.js: 1,36M Versenden über 603
// Verstexte — mit yieldToMain() bleibt die UI auch auf langsamen Geräten reagibel.
const CHUNK_BUDGET_MS = 30;

function yieldToMain() {
  return new Promise(resolve => {
    const ch = new MessageChannel();
    ch.port1.onmessage = () => resolve();
    ch.port2.postMessage(null);
  });
}

/**
 * Strukturelle Reim-Heuristik auf MHG-normalisierten Formen (Audit #106):
 * 3-Letter-Suffix-Match; der 2-Letter-Fallback greift nur, wenn BEIDE
 * Formen kurz sind (≤4 Zeichen) — das findet wîp:lîp und tac:slac,
 * verhindert aber, dass hochfrequente Kurzwörter (en, dô, sô …) jedes
 * lange Ziel-Lemma über einen 2-Letter-Auslaut als "Reim" fluten.
 */
function rhymesWith(normA, normB) {
  if (!normA || !normB) return false;
  if (normA.slice(-3) === normB.slice(-3)) return true;
  if (normA.length <= 4 && normB.length <= 4 && normA.slice(-2) === normB.slice(-2)) return true;
  return false;
}

export class RhymeDictionary {
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

  /**
   * Textfilter (optional): Sigle exakt (case-insensitiv) ODER
   * Titel-/Autor-Substring. Leerer Filter = ganzer Korpus.
   */
  filterTexts(texts) {
    const f = this.state.textFilter.trim().toLowerCase();
    if (!f) return texts;
    return texts.filter(t =>
      (t.id || '').toLowerCase() === f ||
      (t.title || '').toLowerCase().includes(f) ||
      (t.author || '').toLowerCase().includes(f)
    );
  }

  async computeRhymes(target, onProgress) {
    const allTexts = this.getCorpusTexts() || [];
    const texts = this.filterTexts(allTexts);
    const targetNorm = target.normalized || '';
    const targetId = target.id;

    const partners = new Map();   // lemmaId -> {count, texts: Map(textId -> count)}
    let endOccurrences = 0;       // Zielvorkommen am Versende
    let verseTextCount = 0;
    let chunkStart = performance.now();
    const myToken = this._abortToken;

    for (let i = 0; i < texts.length; i++) {
      if (this._abortToken !== myToken) return null;

      const text = texts[i];
      const ends = text.lineEnds;
      // Prosa (leere lineEnds) überspringen — kanonischer Guard aus #47.3
      if (!ends || ends.length === 0) continue;
      verseTextCount++;

      const words = text.words;
      if (!words || words.length === 0) continue;

      // Nur scannen, wenn das Lemma im Text überhaupt vorkommt
      if (!text.lemmata?.[targetId]) continue;

      for (let k = 0; k < ends.length; k++) {
        if (words[ends[k]] !== targetId) continue;
        endOccurrences++;

        for (const delta of [-1, 1]) {
          const j = k + delta;
          if (j < 0 || j >= ends.length) continue;
          const partnerId = words[ends[j]];
          if (!partnerId) continue;
          // Identischer Reim (Lemma reimt auf sich selbst, "rührender Reim"):
          // nur in eine Richtung zählen, sonst zählt jedes Paar doppelt.
          if (partnerId === targetId && delta === -1) continue;

          const partnerNorm = this._lemmaMap?.get(partnerId)?.normalized || '';
          if (!rhymesWith(targetNorm, partnerNorm)) continue;

          let entry = partners.get(partnerId);
          if (!entry) {
            entry = { count: 0, texts: new Map() };
            partners.set(partnerId, entry);
          }
          entry.count++;
          entry.texts.set(text.id, (entry.texts.get(text.id) || 0) + 1);
        }
      }

      if (performance.now() - chunkStart > CHUNK_BUDGET_MS) {
        if (onProgress) onProgress((i + 1) / texts.length);
        await yieldToMain();
        if (this._abortToken !== myToken) return null;
        chunkStart = performance.now();
      }
    }

    if (onProgress) onProgress(1);
    return {
      endOccurrences,
      verseTextCount,
      scannedTextCount: texts.length,
      partners
    };
  }

  enrichPartners(partnersMap) {
    const out = [];
    for (const [lemmaId, entry] of partnersMap) {
      const lemma = this._lemmaMap?.get(lemmaId);
      out.push({
        lemmaId,
        lemma: lemma?.lemma || lemmaId,
        pos: lemma?.pos || '',
        count: entry.count,
        texts: Array.from(entry.texts.entries())
          .map(([id, count]) => ({ id, count }))
          .sort((a, b) => b.count - a.count)
      });
    }
    out.sort((a, b) => b.count - a.count || a.lemma.localeCompare(b.lemma, 'de'));
    return out;
  }

  async runSearch() {
    const { resolved, candidates } = this.resolveQuery(this.state.query);
    this.state.resolvedLemma = resolved;
    this.state.candidates = candidates;
    this.state.result = null;
    if (!resolved) {
      this.render();
      return;
    }
    this._abortToken += 1;
    this.state.computing = true;
    this.state.progress = 0;
    this.render();

    const myToken = this._abortToken;
    const raw = await this.computeRhymes(resolved, (p) => {
      if (this._abortToken !== myToken) return;
      this.state.progress = p;
      this.updateProgressBar();
    });
    if (this._abortToken !== myToken) return;
    if (!raw) {
      this.state.computing = false;
      return;
    }

    this.state.result = {
      ...raw,
      partners: this.enrichPartners(raw.partners)
    };
    this.state.computing = false;
    // Nicht rendern, wenn der User während des Scans zu einer anderen
    // Playground-View navigiert ist — sonst überschreibt das fertige
    // Ergebnis die aktuell angezeigte View in #resultsContainer.
    if (!this.isActiveView()) return;
    this.render();
  }

  /**
   * True, wenn die Router-Hash-Route noch zu diesem Modul gehört (oder kein
   * Hash gesetzt ist, z.B. bei programmatischem show() ohne Route).
   */
  isActiveView() {
    const view = (window.location.hash || '').replace(/^#/, '').split('&')[0];
    return view === '' || view === 'rhyme-dictionary';
  }

  updateProgressBar() {
    const bar = document.getElementById('rdProgressBar');
    if (bar) {
      bar.style.width = `${Math.round(this.state.progress * 100)}%`;
    }
    const label = document.getElementById('rdProgressLabel');
    if (label) {
      label.textContent = `Scanne Versenden … ${Math.round(this.state.progress * 100)}%`;
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
    return `
      <div class="rounded-2xl border border-slate-200 bg-slate-50/70 p-4 space-y-3">
        <h3 class="text-sm font-semibold uppercase tracking-wide text-slate-500">Reim-Wörterbuch</h3>
        <p class="text-xs text-slate-600">
          „Welche Lemmata reimen sich auf X?" Scannt alle Versenden des Korpus und sammelt
          die Lemmata benachbarter Versenden (±1 Vers, Paarreim-Annahme), deren normalisierte
          Form im Auslaut übereinstimmt. Lemma-basiert und strukturell — keine phonetische
          Reim-Klassifikation. Nur Verstexte; Prosa wird ignoriert.
        </p>
        <div class="grid gap-3 sm:grid-cols-4">
          <div class="sm:col-span-2">
            <label class="block">
              <span class="text-xs font-medium text-slate-600">Lemma</span>
              <div class="relative mt-1">
                <input id="rdQuery" type="text" autocomplete="off" role="combobox"
                  aria-autocomplete="list" aria-controls="rdAutocomplete" aria-expanded="false"
                  value="${escapeAttr(this.state.query)}"
                  placeholder="z.B. tugent"
                  class="w-full rounded-lg border border-slate-200 bg-white px-3 py-2 text-sm focus:border-brand-400 focus:outline-none"/>
                <div id="rdAutocomplete" role="listbox"
                  class="absolute left-0 right-0 top-full z-30 mt-1 hidden max-h-72 overflow-y-auto rounded-lg border border-slate-200 bg-white shadow-lg"></div>
              </div>
            </label>
          </div>
          <label class="block">
            <span class="text-xs font-medium text-slate-600">Text/Autor-Filter (optional)</span>
            <input id="rdTextFilter" type="text" autocomplete="off"
              value="${escapeAttr(this.state.textFilter)}"
              placeholder="Sigle, Titel oder Autor"
              class="mt-1 w-full rounded-lg border border-slate-200 bg-white px-3 py-2 text-sm focus:border-brand-400 focus:outline-none"/>
          </label>
          <label class="block">
            <span class="text-xs font-medium text-slate-600">Mindest-Reimpaare</span>
            <input id="rdMinCount" type="number" min="1" max="10000"
              value="${this.state.minCount}"
              class="mt-1 w-full rounded-lg border border-slate-200 bg-white px-3 py-2 text-sm focus:border-brand-400 focus:outline-none"/>
          </label>
        </div>
        <div class="flex items-center gap-3">
          <button id="rdSearchBtn" type="button" class="rounded-lg border border-brand-200 bg-brand-50 px-4 py-1.5 text-sm font-medium text-brand-700 hover:border-brand-400 hover:bg-brand-100">Suchen</button>
        </div>
      </div>
    `;
  }

  renderBody() {
    if (this.state.computing) {
      return `
        <div class="rounded-2xl border border-slate-200 bg-white p-6 space-y-3">
          <div id="rdProgressLabel" class="text-sm text-slate-600">Scanne Versenden … ${Math.round(this.state.progress * 100)}%</div>
          <div class="h-2 w-full overflow-hidden rounded-full bg-slate-100">
            <div id="rdProgressBar" class="h-full rounded-full bg-brand-400 transition-all" style="width: ${Math.round(this.state.progress * 100)}%"></div>
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
    const r = this.state.result;
    const cleanId = lemma.id.replace(/^lemma_/, '');
    const norm = lemma.normalized || '';
    const suffix = norm.length > 3 ? norm.slice(-3) : norm.slice(-2);

    const candidates = this.state.candidates.length > 1
      ? `<div class="mt-2 text-xs text-slate-500">Weitere Treffer: ${this.state.candidates.slice(1, 8).map(c => `<span class="mr-2 rounded bg-slate-100 px-1.5 py-0.5 font-mono">${escapeHtml(c.lemma || c.id)}</span>`).join('')}</div>`
      : '';

    const filterNote = this.state.textFilter.trim()
      ? ` · Filter „${escapeHtml(this.state.textFilter.trim())}" → ${r.scannedTextCount} Texte`
      : '';

    if (r.endOccurrences === 0) {
      return `
        <div class="rounded-2xl border border-slate-200 bg-white p-6 text-sm">
          <div class="font-semibold text-slate-800">${escapeHtml(lemma.lemma || lemma.id)}</div>
          <div class="mt-1 text-xs text-slate-500">${escapeHtml(lemma.id)}${filterNote}</div>
          <p class="mt-3 text-slate-600">Kein Vorkommen am Versende gefunden (${r.verseTextCount} Verstexte gescannt, Prosa ignoriert).</p>
          ${candidates}
        </div>
      `;
    }

    const filtered = r.partners.filter(p => p.count >= this.state.minCount);
    const visible = filtered.slice(0, MAX_VISIBLE_PARTNERS);

    const trs = visible.map((p, idx) => {
      const partnerClean = p.lemmaId.replace(/^lemma_/, '');
      // Ohne Authority-Eintrag ist p.lemma die rohe ID ("lemma_NNN"), die
      // die Multi-Lemma-Suche nicht auflösen kann — dann die numerische ID
      // übergeben (deren Route akzeptiert /^\d+$/ direkt).
      const partnerTerm = p.lemma && p.lemma !== p.lemmaId ? p.lemma : partnerClean;
      const multiHref = `#multi-lemma&lemmata=${encodeURIComponent(lemma.lemma || cleanId)},${encodeURIComponent(partnerTerm)}&mode=proximity&dist=${BELEGE_PROXIMITY_DIST}`;
      const textChips = p.texts.slice(0, 6).map(t =>
        `<span class="mr-1 rounded bg-slate-100 px-1.5 py-0.5 font-mono text-[10px] text-slate-600" title="${t.count} Reimpaar(e)">${escapeHtml(t.id)}&thinsp;·&thinsp;${t.count}</span>`
      ).join('');
      const moreTexts = p.texts.length > 6
        ? `<span class="text-[10px] text-slate-400">+${p.texts.length - 6} weitere</span>`
        : '';
      return `
        <tr class="border-b border-slate-100 hover:bg-slate-50">
          <td class="px-3 py-1.5 text-right tabular-nums text-xs text-slate-500">${idx + 1}</td>
          <td class="px-3 py-1.5">
            <a href="../lemma/?id=${escapeAttr(partnerClean)}" target="_blank" rel="noopener" class="font-medium text-brand-700 hover:underline">${escapeHtml(p.lemma)}</a>
            ${p.pos ? `<span class="ml-1 rounded bg-slate-100 px-1 text-[10px] font-mono text-slate-600">${escapeHtml(p.pos)}</span>` : ''}
          </td>
          <td class="px-3 py-1.5 text-right tabular-nums text-slate-700">${p.count.toLocaleString('de-DE')}</td>
          <td class="px-3 py-1.5">${textChips}${moreTexts}</td>
          <td class="px-3 py-1.5 text-right">
            <a href="${multiHref}" class="text-xs text-brand-700 hover:underline" title="Beide Lemmata in der Multi-Lemma-Suche (Distanz ${BELEGE_PROXIMITY_DIST})">→ Belege</a>
          </td>
        </tr>
      `;
    }).join('');

    const truncated = filtered.length > visible.length;

    return `
      <div class="rounded-2xl border border-slate-200 bg-white p-4 space-y-3">
        <header class="flex items-start justify-between gap-4">
          <div>
            <div class="text-xs uppercase tracking-wide text-slate-500">Reim-Lemma</div>
            <div class="text-lg font-semibold text-brand-700">
              <a href="../lemma/?id=${escapeAttr(cleanId)}" target="_blank" rel="noopener" class="hover:underline">${escapeHtml(lemma.lemma || lemma.id)}</a>
              ${lemma.pos ? `<span class="ml-2 rounded bg-slate-100 px-1.5 py-0.5 text-xs font-mono text-slate-600">${escapeHtml(lemma.pos)}</span>` : ''}
              <span class="ml-2 rounded bg-brand-50 px-1.5 py-0.5 text-xs font-mono text-brand-700" title="Struktureller Reimklang (Suffix der normalisierten Form)">-${escapeHtml(suffix)}</span>
            </div>
            <div class="text-xs text-slate-500">${escapeHtml(lemma.id)} · Mindest-Reimpaare ${this.state.minCount}${filterNote}</div>
            ${candidates}
          </div>
          <div class="text-right text-xs text-slate-500">
            <div>${r.endOccurrences.toLocaleString('de-DE')} Vorkommen am Versende</div>
            <div>${filtered.length.toLocaleString('de-DE')} Reimpartner-Lemmata</div>
            <div>${r.verseTextCount.toLocaleString('de-DE')} Verstexte gescannt</div>
          </div>
        </header>

        <div class="overflow-x-auto rounded-2xl border border-slate-200">
          <table class="w-full text-sm">
            <thead class="bg-slate-50">
              <tr>
                <th class="px-3 py-2 text-right text-xs font-semibold text-slate-600 w-12">#</th>
                <th class="px-3 py-2 text-left text-xs font-semibold text-slate-600">Reimpartner-Lemma</th>
                <th class="px-3 py-2 text-right text-xs font-semibold text-slate-600">Reimpaare</th>
                <th class="px-3 py-2 text-left text-xs font-semibold text-slate-600">Texte</th>
                <th class="px-3 py-2 text-right text-xs font-semibold text-slate-600">Belege</th>
              </tr>
            </thead>
            <tbody>${trs}</tbody>
          </table>
        </div>
        ${filtered.length === 0 ? '<div class="rounded-xl border border-amber-200 bg-amber-50 p-3 text-xs text-amber-800">Vorkommen am Versende vorhanden, aber kein benachbartes Versende mit übereinstimmendem Reimklang. Kreuzreime (ABAB) und rein klangliche Reime entgehen der Minimalvariante.</div>' : ''}
        ${truncated ? `<div class="text-center text-xs text-slate-500">Zeige Top ${visible.length} von ${filtered.length.toLocaleString('de-DE')} Reimpartnern.</div>` : ''}
        <p class="text-xs text-slate-500">
          Heuristik: benachbarte Versenden (±1 Vers, Paarreim-Annahme) mit übereinstimmendem
          3-Letter-Suffix der normalisierten Lemma-Form (2-Letter, wenn beide Formen kurz sind).
          Lemma-basiert — die tatsächlich reimende Flexionsform kann abweichen; phonetische
          Reim-Klassifikation (sauberer Reim vs. Assonanz) ist Folgearbeit (#106/#109).
        </p>
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

  // Autocomplete-Pattern (DESIGN.md §Live-Autocomplete-Dropdown)
  renderAutocomplete() {
    const dd = document.getElementById('rdAutocomplete');
    const input = document.getElementById('rdQuery');
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
      const pos = l.pos ? `<span class="ml-1 rounded bg-slate-100 px-1 text-[10px] font-mono text-slate-600">${escapeHtml(l.pos)}</span>` : '';
      return `<button type="button" role="option" data-rd-ac-idx="${i}"
        aria-selected="${active}"
        class="block w-full cursor-pointer px-3 py-2 text-left text-sm ${cls}">
        <span class="font-medium">${escapeHtml(l.lemma || l.id)}</span>${pos}
        <span class="ml-2 text-xs font-mono text-slate-400">${escapeHtml(l.id)}</span>
      </button>`;
    }).join('');
    dd.classList.remove('hidden');
    if (input) input.setAttribute('aria-expanded', 'true');
    const activeEl = dd.querySelector(`[data-rd-ac-idx="${idx}"]`);
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
      const input = document.getElementById('rdQuery');
      if (!input) return;
      this.state.query = input.value;
      const filterInput = document.getElementById('rdTextFilter');
      if (filterInput) this.state.textFilter = filterInput.value;
      this.closeAutocomplete();
      this.runSearch();
    };

    document.getElementById('rdSearchBtn')?.addEventListener('click', runSearch);

    const input = document.getElementById('rdQuery');
    if (input) {
      input.addEventListener('input', (e) => this.updateAutocomplete(e.target.value));
      input.addEventListener('keydown', (e) => {
        const open = this.state.autocompleteOpen && this.state.autocompleteItems.length > 0;
        if (e.key === 'Enter') {
          e.preventDefault();
          if (open && this.state.autocompleteIndex >= 0) {
            const c = this.state.autocompleteItems[this.state.autocompleteIndex];
            input.value = c.lemma || c.id;
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

    const dd = document.getElementById('rdAutocomplete');
    if (dd) {
      dd.addEventListener('mousedown', (e) => {
        const btn = e.target.closest('[data-rd-ac-idx]');
        if (!btn) return;
        e.preventDefault();
        const idx = parseInt(btn.getAttribute('data-rd-ac-idx'), 10);
        const c = this.state.autocompleteItems[idx];
        if (!c) return;
        const inputEl = document.getElementById('rdQuery');
        if (inputEl) inputEl.value = c.lemma || c.id;
        this.closeAutocomplete();
        runSearch();
      });
    }

    document.getElementById('rdTextFilter')?.addEventListener('keydown', (e) => {
      if (e.key === 'Enter') {
        e.preventDefault();
        runSearch();
      }
    });

    document.getElementById('rdMinCount')?.addEventListener('change', (e) => {
      const v = parseInt(e.target.value, 10);
      this.state.minCount = isNaN(v) || v < 1 ? 1 : v;
      // Cutoff wirkt erst bei der Anzeige — Re-Render genügt, kein Re-Compute.
      if (this.state.result) this.render();
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
