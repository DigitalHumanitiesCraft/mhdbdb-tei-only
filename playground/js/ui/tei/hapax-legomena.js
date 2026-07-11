/**
 * MHDBDB Playground - Echte Hapaxlegomena
 *
 * Lemmata (nicht Wortformen) mit korpusweiter Gesamtfrequenz <= n über alle
 * Texte, aggregiert aus dem pre-built Corpus-Index (`text.lemmata`). Abzugrenzen
 * von der Hapax-Rate der Text-Statistiken (#89), die TEXT-Hapaxe zählt
 * (Frequenz 1 innerhalb eines Texts).
 *
 * Zwei Ansichten: Raritätenliste (mit Fundort + Reader-Link, PoS-/Buchstaben-
 * Facette, Wörterbuchnetz-Check pro Eintrag) und Hapax-Beitrag pro Text
 * (absolut + pro 1000 Tokens). Frontend-only, kein neuer Index.
 *
 * Issue: #196
 */

import { buildTextLabelDisambiguator } from '../core/ui-helpers.js';
import { FUNCTION_WORD_POS } from './word-frequency.js';
import { fetchWbnetzEntries, decodeHtmlEntities } from '../../../../assets/js/lib/woerterbuchnetz.js';

const FREQ_OPTIONS = [
  { value: 1, label: 'Hapaxlegomena (Frequenz = 1)' },
  { value: 2, label: 'Dislegomena (Frequenz ≤ 2)' },
  { value: 3, label: 'Trislegomena (Frequenz ≤ 3)' }
];
const PAGE_SIZE = 100;
const INITIALS = 'abcdefghijklmnopqrstuvwxyz'.split('');

export class HapaxLegomenaAnalyzer {
  /**
   * @param {() => Array} getCorpusTexts  thunk returning the current corpus
   *   texts array (same indirection as WordFrequencyAnalyzer).
   * @param {object} authorityData
   */
  constructor(getCorpusTexts, authorityData) {
    this.getCorpusTexts = getCorpusTexts;
    this.authorityData = authorityData;
    this._lemmaById = null;
    this._conceptById = null;
    this._corpusAgg = null;      // einmalige korpusweite Aggregation
    this._textLabelCache = null;
    this.state = {
      tab: 'list',               // 'list' | 'perText'
      maxFreq: 1,
      hideNames: true,           // Eigennamen (NAM) sind 28 % der Hapaxe
      hideFunctionWords: false,
      posFilter: 'all',
      initial: 'all',
      page: 0,
      perTextSort: { key: 'abs', dir: 'desc' }
    };
  }

  getLemmaById(id) {
    if (!this._lemmaById) {
      const lemmata = this.authorityData?.lemmata || [];
      this._lemmaById = new Map(lemmata.map(l => [l.id, l]));
    }
    return this._lemmaById.get(id);
  }

  getConceptById(id) {
    if (!this._conceptById) {
      const concepts = this.authorityData?.concepts || [];
      this._conceptById = new Map(concepts.map(c => [c.id, c]));
    }
    return this._conceptById.get(id);
  }

  /**
   * Ein Durchlauf über alle Texte: Gesamtfrequenz je Lemma + die ersten
   * (max. 3) Fundorte. 3 = höchste wählbare Frequenzschwelle; für alles
   * darüber werden keine Fundorte angezeigt.
   */
  aggregateCorpus() {
    if (this._corpusAgg) return this._corpusAgg;
    const texts = this.getCorpusTexts() || [];
    const counts = new Map();
    const occurrences = new Map();
    for (const text of texts) {
      for (const [lemmaId, positions] of Object.entries(text.lemmata || {})) {
        counts.set(lemmaId, (counts.get(lemmaId) || 0) + positions.length);
        let occ = occurrences.get(lemmaId);
        if (!occ) { occ = []; occurrences.set(lemmaId, occ); }
        for (const pos of positions) {
          if (occ.length >= 3) break;
          occ.push({ textId: text.id, pos });
        }
      }
    }
    this._corpusAgg = { counts, occurrences, totalTypes: counts.size };
    return this._corpusAgg;
  }

  /** Versnummer (1-basiert) für eine Wortposition via lineStarts, sonst null. */
  verseForPosition(text, pos) {
    const ls = text?.lineStarts;
    if (!ls || ls.length === 0) return null;
    let lo = 0, hi = ls.length;
    while (lo < hi) {
      const mid = (lo + hi) >> 1;
      if (ls[mid] <= pos) lo = mid + 1; else hi = mid;
    }
    return lo > 0 ? lo : null;
  }

  /** Lemma-Level-Filter (NAM, Funktionswörter, PoS-Facette, Anfangsbuchstabe). */
  passesFilters(lemmaId) {
    const lemma = this.getLemmaById(lemmaId);
    // Lemmata ohne Authority-Eintrag sind Kuratierungs-Funde: immer zeigen,
    // solange keine Buchstaben-Facette aktiv ist (keine Form bekannt).
    if (!lemma) return this.state.initial === 'all' && this.state.posFilter === 'all';
    const tags = lemma.posAll || (lemma.pos ? String(lemma.pos).trim().split(/\s+/) : []);
    if (this.state.hideNames && tags.includes('NAM')) return false;
    if (this.state.hideFunctionWords && tags.length > 0 && tags.some(t => FUNCTION_WORD_POS.has(t))) return false;
    if (this.state.posFilter !== 'all' && !tags.includes(this.state.posFilter)) return false;
    if (this.state.initial !== 'all') {
      const first = (lemma.normalized || lemma.lemma || '').charAt(0).toLowerCase();
      if (first !== this.state.initial) return false;
    }
    return true;
  }

  /** Gefilterte, alphabetisch sortierte Raritätenliste zur aktuellen Schwelle. */
  computeList() {
    const { counts, occurrences, totalTypes } = this.aggregateCorpus();
    const raw = [];
    let rawCount = 0;
    for (const [lemmaId, count] of counts) {
      if (count > this.state.maxFreq) continue;
      rawCount += 1;
      if (!this.passesFilters(lemmaId)) continue;
      raw.push({ lemmaId, count, occ: occurrences.get(lemmaId) || [] });
    }
    raw.sort((a, b) => {
      const la = this.getLemmaById(a.lemmaId);
      const lb = this.getLemmaById(b.lemmaId);
      const ka = (la?.normalized || la?.lemma || a.lemmaId).toLowerCase();
      const kb = (lb?.normalized || lb?.lemma || b.lemmaId).toLowerCase();
      return ka.localeCompare(kb, 'de');
    });
    return { entries: raw, rawCount, totalTypes };
  }

  /** Tab 2: Raritäten-Beitrag pro Text (absolut + pro 1000 Tokens). */
  computePerText() {
    const { counts } = this.aggregateCorpus();
    const texts = this.getCorpusTexts() || [];
    const rows = [];
    for (const text of texts) {
      let abs = 0;
      for (const lemmaId of Object.keys(text.lemmata || {})) {
        if ((counts.get(lemmaId) || 0) > this.state.maxFreq) continue;
        if (!this.passesFilters(lemmaId)) continue;
        abs += 1;
      }
      const tokens = text.wordCount || 0;
      rows.push({
        id: text.id,
        title: text.title || text.id,
        abs,
        rel: tokens > 0 ? (abs / tokens) * 1000 : 0,
        tokens
      });
    }
    const { key, dir } = this.state.perTextSort;
    const sign = dir === 'asc' ? 1 : -1;
    rows.sort((a, b) => {
      if (key === 'id') return sign * a.id.localeCompare(b.id, 'de');
      return sign * ((a[key] || 0) - (b[key] || 0));
    });
    return rows;
  }

  async show() {
    const texts = this.getCorpusTexts();
    if (!texts || texts.length === 0) {
      this.renderError('Korpus ist noch nicht geladen. Bitte einen Moment warten und Button erneut klicken.');
      return;
    }
    this.render();
  }

  render() {
    const container = document.getElementById('resultsContainer');
    if (!container) return;
    container.innerHTML = `
      <div class="space-y-4">
        ${this.renderToolbar()}
        ${this.renderInfoBox()}
        ${this.state.tab === 'list' ? this.renderList() : this.renderPerText()}
      </div>
    `;
    this.attachHandlers();
  }

  renderToolbar() {
    const freqOptions = FREQ_OPTIONS
      .map(o => `<option value="${o.value}"${this.state.maxFreq === o.value ? ' selected' : ''}>${o.label}</option>`)
      .join('');
    // PoS-Facette aus dem Authority-Bestand (statisch über posAll)
    const posTags = new Set();
    for (const l of (this.authorityData?.lemmata || [])) {
      for (const t of (l.posAll || [])) posTags.add(t);
    }
    const posOptions = ['all', ...[...posTags].sort()]
      .map(t => `<option value="${t}"${this.state.posFilter === t ? ' selected' : ''}>${t === 'all' ? 'alle Wortarten' : t}</option>`)
      .join('');
    const initialOptions = ['all', ...INITIALS]
      .map(c => `<option value="${c}"${this.state.initial === c ? ' selected' : ''}>${c === 'all' ? 'alle Buchstaben' : c.toUpperCase()}</option>`)
      .join('');

    const tabBtn = (tab, label) => `
      <button data-hx-tab="${tab}" class="rounded-lg px-3 py-1.5 text-sm font-medium transition ${this.state.tab === tab
        ? 'bg-brand-600 text-white'
        : 'bg-white text-slate-600 border border-slate-200 hover:border-brand-400 hover:text-brand-700'}">${label}</button>`;

    return `
      <div class="rounded-2xl border border-slate-200 bg-slate-50/70 p-4">
        <div class="mb-3 flex flex-wrap items-center justify-between gap-2">
          <h3 class="text-sm font-semibold uppercase tracking-wide text-slate-500">Echte Hapaxlegomena</h3>
          <div class="flex gap-2">
            ${tabBtn('list', 'Raritätenliste')}
            ${tabBtn('perText', 'Beitrag pro Text')}
          </div>
        </div>
        <div class="grid gap-3 sm:grid-cols-3">
          <label class="block">
            <span class="text-xs font-medium text-slate-600">Frequenzschwelle (korpusweit)</span>
            <select id="hxFreq" class="mt-1 w-full rounded-lg border border-slate-200 bg-white px-3 py-2 text-sm focus:border-brand-400 focus:outline-none">${freqOptions}</select>
          </label>
          <label class="block">
            <span class="text-xs font-medium text-slate-600">Wortart</span>
            <select id="hxPos" class="mt-1 w-full rounded-lg border border-slate-200 bg-white px-3 py-2 text-sm focus:border-brand-400 focus:outline-none">${posOptions}</select>
          </label>
          <label class="block">
            <span class="text-xs font-medium text-slate-600">Anfangsbuchstabe (normalisiert)</span>
            <select id="hxInitial" class="mt-1 w-full rounded-lg border border-slate-200 bg-white px-3 py-2 text-sm focus:border-brand-400 focus:outline-none">${initialOptions}</select>
          </label>
        </div>
        <div class="mt-3 flex flex-wrap items-center gap-x-6 gap-y-2">
          <label class="flex items-center gap-2 text-sm text-slate-700 cursor-pointer">
            <input type="checkbox" id="hxHideNames" ${this.state.hideNames ? 'checked' : ''} class="w-4 h-4 rounded border-slate-300 text-brand-600 focus:ring-brand-500" />
            <span>Eigennamen ausblenden <span class="text-xs text-slate-500">(PoS NAM, 28 % der Hapaxe)</span></span>
          </label>
          <label class="flex items-center gap-2 text-sm text-slate-700 cursor-pointer">
            <input type="checkbox" id="hxHideFunc" ${this.state.hideFunctionWords ? 'checked' : ''} class="w-4 h-4 rounded border-slate-300 text-brand-600 focus:ring-brand-500" />
            <span>Funktionswörter ausblenden</span>
          </label>
          <button id="hxCsvExport" class="ml-auto rounded-lg border border-slate-200 bg-white px-3 py-1.5 text-sm font-medium text-slate-700 transition hover:border-brand-400 hover:text-brand-700 flex items-center gap-1.5">
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v2a2 2 0 002 2h12a2 2 0 002-2v-2M7 10l5 5 5-5M12 15V3"></path></svg>
            CSV-Export
          </button>
        </div>
      </div>
    `;
  }

  renderInfoBox() {
    return `
      <div class="rounded-2xl border border-blue-200 bg-blue-50 p-4 text-xs text-blue-900 space-y-1">
        <p><strong>Korpus-Hapax ≠ Text-Hapax:</strong> Hier zählt die Gesamtfrequenz eines <em>Lemmas</em> über alle Texte. Die Hapax-Rate der Text-Statistiken zählt dagegen Lemmata, die innerhalb <em>eines</em> Texts nur einmal vorkommen.</p>
        <p><strong>Annotationslücken verzerren:</strong> Unlemmatisierte Tokens sind im Index unsichtbar. Ein angezeigtes Hapax kann unannotierte Geschwister haben, besonders in frisch ingestierten Texten.</p>
        <p><strong>Kuratierungsinstrument:</strong> Hapaxe sind oft Lemmatisierungs- oder Tippfehler; Einträge „ohne Authority-Eintrag" sind direkte Datenqualitäts-Funde. Der Wörterbuchnetz-Abgleich je Eintrag hilft bei der Frage: echtes mhd. Hapax oder nur Korpus-Hapax?</p>
      </div>
    `;
  }

  renderList() {
    const { entries, rawCount, totalTypes } = this.computeList();
    const totalPages = Math.max(1, Math.ceil(entries.length / PAGE_SIZE));
    if (this.state.page >= totalPages) this.state.page = totalPages - 1;
    const pageEntries = entries.slice(this.state.page * PAGE_SIZE, (this.state.page + 1) * PAGE_SIZE);
    this._lastEntries = pageEntries; // für Detail-Expand / Reader-Links
    this._lastFiltered = entries;    // für CSV-Export

    const texts = this.getCorpusTexts() || [];
    const textById = new Map(texts.map(t => [t.id, t]));

    const rows = pageEntries.map((e, idx) => {
      const lemma = this.getLemmaById(e.lemmaId);
      const cleanId = e.lemmaId.replace(/^lemma_/, '');
      const lemmaLabel = lemma
        ? `<a href="../lemma/?id=${escapeHtml(cleanId)}" target="_blank" rel="noopener" class="font-medium text-brand-700 hover:underline">${escapeHtml(lemma.lemma)}</a>`
        : `<span class="font-mono text-sm text-slate-500">${escapeHtml(e.lemmaId)}</span>
           <span class="ml-1 rounded bg-amber-100 px-1.5 py-0.5 text-xs text-amber-800" title="Lemma-ID ohne Eintrag in lexicon.xml — Datenqualitäts-Fund">ohne Authority-Eintrag</span>`;
      const posLabel = (lemma?.posAll || []).join(' ');
      const pos = posLabel
        ? `<span class="ml-2 rounded bg-slate-100 px-1.5 py-0.5 text-xs font-mono text-slate-600">${escapeHtml(posLabel)}</span>`
        : '';
      const fundorte = e.occ.map(o => {
        const text = textById.get(o.textId);
        const verse = this.verseForPosition(text, o.pos);
        const label = verse ? `${o.textId}, Vers ${verse}` : `${o.textId}, Pos. ${o.pos}`;
        const url = `../korpus.html?textId=${encodeURIComponent(o.textId)}&lemmaIds=${encodeURIComponent(e.lemmaId)}&position=${o.pos}`;
        return `<a href="${url}" target="_blank" rel="noopener" class="text-brand-700 hover:underline whitespace-nowrap" title="Im Reader mit Highlight öffnen">${escapeHtml(label)}</a>`;
      }).join('<span class="text-slate-300"> · </span>');
      return `
        <tr class="border-t border-slate-100 hover:bg-brand-50/50">
          <td class="px-3 py-2 text-xs text-slate-500 tabular-nums">${this.state.page * PAGE_SIZE + idx + 1}</td>
          <td class="px-3 py-2">${lemmaLabel}${pos}</td>
          <td class="px-3 py-2 text-right tabular-nums text-sm text-slate-700">${e.count}</td>
          <td class="px-3 py-2 text-sm">${fundorte || '<span class="text-slate-400">–</span>'}</td>
          <td class="px-3 py-2 text-right">
            <button data-hx-detail="${idx}" class="rounded-lg border border-slate-200 px-2 py-1 text-xs font-medium text-slate-600 transition hover:border-brand-400 hover:text-brand-700">Details</button>
          </td>
        </tr>
        <tr id="hxDetailRow-${idx}" class="hidden border-t border-slate-100 bg-slate-50/70">
          <td></td>
          <td colspan="4" class="px-3 py-3" id="hxDetailCell-${idx}"></td>
        </tr>
      `;
    }).join('');

    const pager = totalPages > 1 ? `
      <div class="flex items-center justify-between border-t border-slate-200 bg-slate-50/80 px-4 py-2 text-sm">
        <button id="hxPrev" ${this.state.page === 0 ? 'disabled' : ''} class="rounded-lg border border-slate-200 bg-white px-3 py-1 font-medium text-slate-600 transition hover:border-brand-400 hover:text-brand-700 disabled:opacity-40 disabled:hover:border-slate-200 disabled:hover:text-slate-600">← Zurück</button>
        <span class="text-xs text-slate-500">Seite ${this.state.page + 1} von ${totalPages.toLocaleString('de-DE')}</span>
        <button id="hxNext" ${this.state.page >= totalPages - 1 ? 'disabled' : ''} class="rounded-lg border border-slate-200 bg-white px-3 py-1 font-medium text-slate-600 transition hover:border-brand-400 hover:text-brand-700 disabled:opacity-40 disabled:hover:border-slate-200 disabled:hover:text-slate-600">Weiter →</button>
      </div>` : '';

    const pct = totalTypes > 0 ? ((rawCount / totalTypes) * 100).toFixed(1) : '0';
    return `
      <div class="overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-sm">
        <header class="flex items-center justify-between border-b border-slate-200 bg-slate-50/80 px-4 py-3">
          <div>
            <div class="text-sm font-semibold text-slate-800">${entries.length.toLocaleString('de-DE')} Lemmata mit Frequenz ≤ ${this.state.maxFreq}</div>
            <div class="text-xs text-slate-500">${rawCount.toLocaleString('de-DE')} vor Filterung (${pct} % von ${totalTypes.toLocaleString('de-DE')} Lemma-Types), ${(rawCount - entries.length).toLocaleString('de-DE')} ausgeblendet</div>
          </div>
        </header>
        <table class="w-full">
          <thead class="text-xs uppercase tracking-wide text-slate-500">
            <tr class="bg-white">
              <th class="w-14 px-3 py-2 text-left">#</th>
              <th class="px-3 py-2 text-left">Lemma</th>
              <th class="w-20 px-3 py-2 text-right">Freq.</th>
              <th class="px-3 py-2 text-left">Fundort(e)</th>
              <th class="w-24 px-3 py-2 text-right"></th>
            </tr>
          </thead>
          <tbody>${rows || '<tr><td colspan="5" class="px-4 py-6 text-center text-sm text-slate-500">Keine Treffer mit den aktuellen Filtern.</td></tr>'}</tbody>
        </table>
        ${pager}
      </div>
    `;
  }

  renderPerText() {
    const rows = this.computePerText();
    this._lastPerText = rows;
    const disambig = this._getTextLabelDisambiguator();
    const { key, dir } = this.state.perTextSort;
    const arrow = (k) => key === k ? (dir === 'desc' ? ' ↓' : ' ↑') : '';

    const body = rows.map((r, idx) => `
      <tr class="border-t border-slate-100 hover:bg-brand-50/50">
        <td class="px-3 py-2 text-xs text-slate-500 tabular-nums">${idx + 1}</td>
        <td class="px-3 py-2">
          <a href="../korpus.html?textId=${encodeURIComponent(r.id)}" target="_blank" rel="noopener" class="font-medium text-brand-700 hover:underline">${escapeHtml(r.id)}</a>
          <span class="ml-2 text-sm text-slate-600">${escapeHtml(r.title + (disambig.get(r.id) || ''))}</span>
        </td>
        <td class="px-3 py-2 text-right tabular-nums text-sm text-slate-700">${r.abs.toLocaleString('de-DE')}</td>
        <td class="px-3 py-2 text-right tabular-nums text-sm text-slate-700">${r.rel.toFixed(2)}</td>
        <td class="px-3 py-2 text-right tabular-nums text-sm text-slate-500">${r.tokens.toLocaleString('de-DE')}</td>
      </tr>
    `).join('');

    const th = (k, label, align = 'right') => `
      <th class="px-3 py-2 text-${align}">
        <button data-hx-sort="${k}" class="font-semibold uppercase tracking-wide hover:text-brand-700">${label}${arrow(k)}</button>
      </th>`;

    return `
      <div class="overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-sm">
        <header class="border-b border-slate-200 bg-slate-50/80 px-4 py-3">
          <div class="text-sm font-semibold text-slate-800">Raritäten-Beitrag pro Text (Frequenz ≤ ${this.state.maxFreq}, Filter aktiv)</div>
          <div class="text-xs text-slate-500">Wie viele der korpusweiten Raritäten stehen in welchem Text? Normierung: pro 1.000 Tokens.</div>
        </header>
        <table class="w-full">
          <thead class="text-xs text-slate-500">
            <tr class="bg-white">
              <th class="w-12 px-3 py-2 text-left font-semibold uppercase tracking-wide">#</th>
              ${th('id', 'Text', 'left')}
              ${th('abs', 'Raritäten')}
              ${th('rel', 'pro 1000')}
              <th class="px-3 py-2 text-right font-semibold uppercase tracking-wide">Tokens</th>
            </tr>
          </thead>
          <tbody>${body}</tbody>
        </table>
      </div>
    `;
  }

  _getTextLabelDisambiguator() {
    if (!this._textLabelCache) {
      const texts = this.getCorpusTexts() || [];
      this._textLabelCache = buildTextLabelDisambiguator(texts, this.authorityData?.works || []);
    }
    return this._textLabelCache;
  }

  /** Detail-Panel: Konzepte + Wörterbuchnetz-Abgleich (lazy, on expand). */
  async toggleDetail(idx) {
    const row = document.getElementById(`hxDetailRow-${idx}`);
    const cell = document.getElementById(`hxDetailCell-${idx}`);
    if (!row || !cell) return;
    if (!row.classList.contains('hidden')) {
      row.classList.add('hidden');
      return;
    }
    row.classList.remove('hidden');
    if (cell.dataset.loaded) return;
    cell.dataset.loaded = '1';

    const entry = this._lastEntries?.[idx];
    if (!entry) return;
    const lemma = this.getLemmaById(entry.lemmaId);
    if (!lemma) {
      cell.innerHTML = '<span class="text-sm text-slate-500">Kein Eintrag in lexicon.xml — Kandidat für die Kuratierung (Lemma-ID wird im Korpus referenziert, fehlt aber im Authority-File).</span>';
      return;
    }

    const conceptChips = (lemma.senses || [])
      .flatMap(s => s.conceptIds || [])
      .map(cid => this.getConceptById(cid))
      .filter(Boolean)
      .map(c => `<span class="rounded bg-slate-100 px-1.5 py-0.5 text-xs text-slate-600">${escapeHtml(c.termDE || c.id)}</span>`)
      .join(' ');

    cell.innerHTML = `
      <div class="space-y-2 text-sm">
        ${conceptChips ? `<div><span class="text-xs font-medium text-slate-500">Konzepte:</span> ${conceptChips}</div>` : ''}
        <div id="hxDict-${idx}" class="text-xs text-slate-500">Wörterbuchnetz wird abgefragt …</div>
      </div>
    `;

    const dictEl = document.getElementById(`hxDict-${idx}`);
    try {
      const results = await fetchWbnetzEntries(lemma.normalized || lemma.lemma);
      if (!dictEl) return;
      const links = results.flatMap(({ sigle, entries }) =>
        entries.slice(0, 3).map(e =>
          `<a href="${escapeHtml(e.wbnetzlink)}" target="_blank" rel="noopener" class="text-brand-700 hover:underline">${escapeHtml(sigle)}: ${escapeHtml(decodeHtmlEntities(e.textstring || e.lemma || lemma.lemma))}</a>`
        )
      );
      dictEl.innerHTML = links.length > 0
        ? `<span class="font-medium text-slate-500">Wörterbücher:</span> ${links.join('<span class="text-slate-300"> · </span>')}`
        : `<span class="text-slate-500">In MWB/Lexer nicht als Lemma gefunden — Kandidat für ein echtes Hapax (oder Schreibform-/Lemmatisierungsproblem).</span>`;
    } catch (e) {
      if (dictEl) dictEl.textContent = 'Wörterbuchnetz nicht erreichbar.';
    }
  }

  exportCsv() {
    const entries = this._lastFiltered || [];
    const texts = this.getCorpusTexts() || [];
    const textById = new Map(texts.map(t => [t.id, t]));
    const lines = ['Lemma;ID;PoS;Frequenz;Fundorte'];
    for (const e of entries) {
      const lemma = this.getLemmaById(e.lemmaId);
      const fundorte = e.occ.map(o => {
        const verse = this.verseForPosition(textById.get(o.textId), o.pos);
        return verse ? `${o.textId} V.${verse}` : `${o.textId} Pos.${o.pos}`;
      }).join(' | ');
      const cells = [lemma?.lemma || '', e.lemmaId, (lemma?.posAll || []).join(' '), String(e.count), fundorte];
      lines.push(cells.map(c => `"${String(c).replace(/"/g, '""')}"`).join(';'));
    }
    const date = new Date().toISOString().slice(0, 10);
    const blob = new Blob(['﻿' + lines.join('\r\n')], { type: 'text/csv;charset=utf-8' });
    const a = document.createElement('a');
    a.href = URL.createObjectURL(blob);
    a.download = `mhdbdb-hapaxe-freq${this.state.maxFreq}-${date}.csv`;
    a.click();
    URL.revokeObjectURL(a.href);
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

  attachHandlers() {
    const rerender = () => { this.state.page = 0; this.render(); };
    document.getElementById('hxFreq')?.addEventListener('change', (e) => {
      this.state.maxFreq = parseInt(e.target.value, 10) || 1;
      rerender();
    });
    document.getElementById('hxPos')?.addEventListener('change', (e) => {
      this.state.posFilter = e.target.value;
      rerender();
    });
    document.getElementById('hxInitial')?.addEventListener('change', (e) => {
      this.state.initial = e.target.value;
      rerender();
    });
    document.getElementById('hxHideNames')?.addEventListener('change', (e) => {
      this.state.hideNames = e.target.checked;
      rerender();
    });
    document.getElementById('hxHideFunc')?.addEventListener('change', (e) => {
      this.state.hideFunctionWords = e.target.checked;
      rerender();
    });
    document.getElementById('hxCsvExport')?.addEventListener('click', () => {
      if (this.state.tab !== 'list') { this.state.tab = 'list'; this.render(); }
      this.exportCsv();
    });
    document.getElementById('hxPrev')?.addEventListener('click', () => {
      if (this.state.page > 0) { this.state.page -= 1; this.render(); }
    });
    document.getElementById('hxNext')?.addEventListener('click', () => {
      this.state.page += 1; this.render();
    });
    document.querySelectorAll('[data-hx-tab]').forEach(btn => {
      btn.addEventListener('click', () => {
        this.state.tab = btn.dataset.hxTab;
        this.render();
      });
    });
    document.querySelectorAll('[data-hx-sort]').forEach(btn => {
      btn.addEventListener('click', () => {
        const k = btn.dataset.hxSort;
        const cur = this.state.perTextSort;
        this.state.perTextSort = {
          key: k,
          dir: cur.key === k && cur.dir === 'desc' ? 'asc' : 'desc'
        };
        this.render();
      });
    });
    document.querySelectorAll('[data-hx-detail]').forEach(btn => {
      btn.addEventListener('click', () => this.toggleDetail(parseInt(btn.dataset.hxDetail, 10)));
    });
  }
}

function escapeHtml(s) {
  if (s == null) return '';
  return String(s).replace(/[&<>"']/g, c => (
    { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]
  ));
}
