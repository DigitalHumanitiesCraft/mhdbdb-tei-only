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
 * Belege: „→ Belege" klappt pro Partner die gezählten Verspaare selbst
 * auf — beide Verse als vollständiger <l>-Inhalt (lazy aus dem TEI
 * gefetcht; das Highlight-Mapping folgt der CONTRACTS-§B-Positions-
 * zählung) mit markierten Reimwörtern und Reader-Deep-Link. Vorher
 * verlinkte der Button in die Multi-Lemma-Nähe-Suche (dist 15), die auch
 * Kookkurrenzen abseits der Versenden zeigt — kein Reim (KZW-Report
 * 2026-07-09).
 *
 * Issue: #106
 */

import { getNavigationEpoch } from '../core/router.js';

const DEFAULT_STATE = Object.freeze({
  query: '',
  resolvedLemma: null,
  selectedLemma: null,        // explizite Autocomplete-Auswahl (#163) — schlägt resolveQuery
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
const BELEGE_PAGE_SIZE = 10;         // Verspaare pro „Weitere laden"-Klick
const MAX_BELEGE_PER_PARTNER = 1000; // Speicher-Cap für Verspaar-Referenzen pro Partner

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
    this._verseCache = new Map();   // textId -> Promise<{forms[], lineNs[]}>
    this._textById = null;          // textId -> Corpus-Index-Texteintrag
    this._visiblePartners = [];     // aktuell gerenderte Partner (für Belege-Toggle)
    this._belegeShown = {};         // partnerIdx -> Anzahl bereits gerenderter Belege
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
    const myEpoch = getNavigationEpoch();

    for (let i = 0; i < texts.length; i++) {
      // Abort on new search in this module (token) OR router navigation
      // to another view (epoch, #159) while we were running.
      if (this._abortToken !== myToken || getNavigationEpoch() !== myEpoch) return null;

      const text = texts[i];
      const ends = text.lineEnds;
      // Prosa (leere lineEnds) überspringen — kanonischer Guard aus #47.3
      if (!ends || ends.length === 0) continue;
      verseTextCount++;

      const words = text.words;
      if (!words || words.length === 0) continue;

      // Nur scannen, wenn das Lemma im Text überhaupt vorkommt
      if (!text.lemmata?.[targetId]) continue;

      // Ziel-Seite ueber die lemmata{}-Positionsliste statt words[...] ===
      // targetId: words[] traegt bei Mehrfach-@lemmaRef nur die ERSTE ID
      // (CONTRACTS §B.1) — die Zweit-ID eines kuenftigen Multi-Ref-Worts am
      // Versende wuerde sonst nie als Reimwort gefunden (#170 Review-
      // Finding). Die Partner-Seite (words[ends[j]]) bleibt bewusst
      // Erst-ID: alle IDs einer Position braeuchten eine Reverse-Map,
      // die der Index nicht hat — bei heute 0 Multi-Ref-Faellen nicht
      // gerechtfertigt.
      const targetPositions = new Set(text.lemmata[targetId]);

      for (let k = 0; k < ends.length; k++) {
        if (!targetPositions.has(ends[k])) continue;
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
            entry = { count: 0, texts: new Map(), belege: [] };
            partners.set(partnerId, entry);
          }
          entry.count++;
          entry.texts.set(text.id, (entry.texts.get(text.id) || 0) + 1);
          // Verspaar-Referenz für die Belege-Ansicht: Versindizes genügen,
          // der Anzeigetext kommt beim Rendern lazy aus dem TEI (getVerseData).
          if (entry.belege.length < MAX_BELEGE_PER_PARTNER) {
            entry.belege.push({ textId: text.id, vTarget: k, vPartner: j });
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
        // #187: alle POS-Werte (Fallback: Erstwert aus altem Cache)
        pos: (lemma?.posAll || (lemma?.pos ? [lemma.pos] : [])).join(' '),
        count: entry.count,
        belege: entry.belege,
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
    // Explizite Autocomplete-Auswahl (#163) schlägt die String-Auflösung —
    // aber nur solange der Query-Text noch der gewählten Form entspricht.
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
    const raw = await this.computeRhymes(this.state.resolvedLemma, (p) => {
      if (this._abortToken !== myToken) return;
      this.state.progress = p;
      this.updateProgressBar();
    });
    if (this._abortToken !== myToken || getNavigationEpoch() !== myEpoch) return;
    if (!raw) {
      this.state.computing = false;
      return;
    }

    this.state.result = {
      ...raw,
      partners: this.enrichPartners(raw.partners)
    };
    this.state.computing = false;
    this.render();
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
          „Welche Lemmata reimen sich auf X?" Scannt die annotierten Versenden des Korpus und sammelt
          die Lemmata benachbarter Versenden (±1 Vers, Paarreim-Annahme), deren normalisierte
          Form im Auslaut übereinstimmt. Lemma-basiert und strukturell, keine phonetische
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
    // Referenz für den Belege-Toggle; Anzeige-Zähler zurücksetzen, weil
    // jedes Re-Render (Suche, Mindest-Reimpaare) die Belege-Boxen leert.
    this._visiblePartners = visible;
    this._belegeShown = {};

    const trs = visible.map((p, idx) => {
      const partnerClean = p.lemmaId.replace(/^lemma_/, '');
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
            <button type="button" data-rd-belege-btn="${idx}" aria-expanded="false"
              class="text-xs text-brand-700 hover:underline"
              title="Reimpaar-Belege (Verspaare am Versende) anzeigen">→ Belege</button>
          </td>
        </tr>
        <tr data-rd-belege-row="${idx}" class="hidden">
          <td colspan="5" class="border-b border-slate-100 bg-slate-50/60 px-4 py-3">
            <div data-rd-belege-box="${idx}"></div>
          </td>
        </tr>
      `;
    }).join('');

    const truncated = filtered.length > visible.length;
    // #187: alle POS-Werte anzeigen (Fallback: Erstwert aus altem Cache)
    const posLabel = (lemma.posAll || (lemma.pos ? [lemma.pos] : [])).join(' ');

    return `
      <div class="rounded-2xl border border-slate-200 bg-white p-4 space-y-3">
        <header class="flex items-start justify-between gap-4">
          <div>
            <div class="text-xs uppercase tracking-wide text-slate-500">Reim-Lemma</div>
            <div class="text-lg font-semibold text-brand-700">
              <a href="../lemma/?id=${escapeAttr(cleanId)}" target="_blank" rel="noopener" class="hover:underline">${escapeHtml(lemma.lemma || lemma.id)}</a>
              ${posLabel ? `<span class="ml-2 rounded bg-slate-100 px-1.5 py-0.5 text-xs font-mono text-slate-600">${escapeHtml(posLabel)}</span>` : ''}
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
          Lemma-basiert: die tatsächlich reimende Flexionsform kann abweichen; phonetische
          Reim-Klassifikation (sauberer Reim vs. Assonanz) ist Folgearbeit (#106/#109).
          Als Versende gilt das letzte Wort mit Lemma-Zuordnung: trägt das eigentliche
          Schlusswort keine, wird ein weiter vorne stehendes Wort als Reimwort gewertet.
          Verse ohne jede Zuordnung sind gar nicht erst im Scan.
          „→ Belege" klappt die gezählten Verspaare auf – ausschließlich Vorkommen
          an benachbarten Versenden, mit Sprung in die Leseansicht.
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

  // ===== Belege: Verspaare am Versende (statt Multi-Lemma-Nähe-Suche) =====

  getTextEntry(textId) {
    if (!this._textById) {
      this._textById = new Map();
      for (const t of (this.getCorpusTexts() || [])) {
        if (t?.id) this._textById.set(t.id, t);
      }
    }
    return this._textById.get(textId);
  }

  /**
   * Verse eines Texts als vollständige <l>-Inhalte (ALLE nicht-leeren <w>,
   * auch unannotierte — sonst fehlen Wörter wie er/an/sein im Anzeigetext),
   * plus Mapping CONTRACTS-§B-Position -> Versindex fürs Highlight: nur ein
   * <w> mit @lemmaRef und nicht-leerem Text zählt als Position (Parität mit
   * build-corpus-index.py und kwic-service.js).
   * Gecacht als Promise, damit parallele Expands nicht doppelt fetchen.
   */
  getVerseData(textId) {
    if (this._verseCache.has(textId)) return this._verseCache.get(textId);
    const promise = (async () => {
      const resp = await fetch(`../tei/${encodeURIComponent(textId)}.tei.xml`);
      if (!resp.ok) throw new Error(`HTTP ${resp.status}`);
      const xml = await resp.text();
      const doc = new DOMParser().parseFromString(xml, 'text/xml');
      const body = doc.querySelector('body');
      const lines = [];      // {n, tokens: [{f: Oberflächenform, p: §B-Position|null}]}
      const lineOfPos = [];  // §B-Position -> Index in lines[] (null außerhalb von <l>)
      if (body) {
        let lastL = null;
        const walker = doc.createTreeWalker(body, NodeFilter.SHOW_ELEMENT);
        let node = walker.nextNode();
        while (node) {
          if (node.localName === 'w') {
            const t = node.textContent.trim();
            if (t) {
              const counted = !!node.getAttribute('lemmaRef');
              // Umschließendes <l> suchen (Pattern kwic-service.js)
              let anc = node.parentElement;
              let lEl = null;
              while (anc && anc.localName !== 'body') {
                if (anc.localName === 'l') { lEl = anc; break; }
                anc = anc.parentElement;
              }
              if (lEl && lEl !== lastL) {
                lines.push({ n: lEl.getAttribute('n') || null, tokens: [] });
                lastL = lEl;
              }
              const pos = counted ? lineOfPos.length : null;
              if (lEl) lines[lines.length - 1].tokens.push({ f: t, p: pos });
              if (counted) lineOfPos.push(lEl ? lines.length - 1 : null);
            }
          }
          node = walker.nextNode();
        }
      }
      return { lines, lineOfPos };
    })();
    this._verseCache.set(textId, promise);
    promise.catch(() => this._verseCache.delete(textId));
    return promise;
  }

  toggleBelege(idx, btn) {
    const row = document.querySelector(`[data-rd-belege-row="${idx}"]`);
    if (!row) return;
    const nowHidden = row.classList.toggle('hidden');
    if (btn) btn.setAttribute('aria-expanded', String(!nowHidden));
    if (!nowHidden && !(this._belegeShown[idx] > 0)) {
      this.loadMoreBelege(idx);
    }
  }

  async loadMoreBelege(idx) {
    const partner = this._visiblePartners?.[idx];
    const box = document.querySelector(`[data-rd-belege-box="${idx}"]`);
    if (!partner || !partner.belege || !box) return;

    let list = box.querySelector('[data-rd-belege-list]');
    let footer = box.querySelector('[data-rd-belege-footer]');
    if (!list) {
      box.innerHTML = '<div data-rd-belege-list class="space-y-2"></div><div data-rd-belege-footer class="pt-2"></div>';
      list = box.querySelector('[data-rd-belege-list]');
      footer = box.querySelector('[data-rd-belege-footer]');
    }
    footer.innerHTML = '<div class="text-xs text-slate-500">Lade Belege …</div>';

    const shown = this._belegeShown[idx] || 0;
    const next = partner.belege.slice(shown, shown + BELEGE_PAGE_SIZE);
    const myToken = this._abortToken;
    const myEpoch = getNavigationEpoch();

    const html = [];
    for (const beleg of next) {
      let verseData = null;
      try {
        verseData = await this.getVerseData(beleg.textId);
      } catch (e) {
        // fällt unten auf die Fehlerbox zurück
      }
      if (this._abortToken !== myToken || getNavigationEpoch() !== myEpoch) return;
      html.push(verseData
        ? this.renderBelegItem(beleg, verseData, partner)
        : `<div class="rounded-lg border border-red-100 bg-red-50 p-2 text-xs text-red-700">${escapeHtml(beleg.textId)}: TEI-Datei konnte nicht geladen werden.</div>`);
    }

    list.insertAdjacentHTML('beforeend', html.join(''));
    const newShown = shown + next.length;
    this._belegeShown[idx] = newShown;

    const stored = partner.belege.length;
    const capNote = partner.count > stored
      ? ` (erfasst: erste ${stored.toLocaleString('de-DE')} von ${partner.count.toLocaleString('de-DE')} Reimpaaren)`
      : '';
    footer.innerHTML = `
      <div class="flex items-center gap-3">
        <span class="text-xs text-slate-500">${newShown} von ${stored.toLocaleString('de-DE')} Belegen${capNote}</span>
        ${newShown < stored
          ? `<button type="button" data-rd-belege-more class="rounded border border-brand-200 bg-white px-2 py-1 text-xs text-brand-700 hover:bg-brand-50">Weitere ${Math.min(BELEGE_PAGE_SIZE, stored - newShown)} laden</button>`
          : ''}
      </div>`;
    footer.querySelector('[data-rd-belege-more]')?.addEventListener('click', () => this.loadMoreBelege(idx));
  }

  /**
   * Ein Beleg = ein Verspaar: beide Verse in Textreihenfolge, Reimwörter
   * (die beiden Versende-Positionen) hervorgehoben, Deep-Link in den Reader.
   */
  renderBelegItem(beleg, verseData, partner) {
    const target = this.state.resolvedLemma;
    const text = this.getTextEntry(beleg.textId);
    if (!text || !text.lineEnds) return '';

    const renderVerse = (v, highlightPos, markCls) => {
      const endPos = text.lineEnds[v];
      const lineIdx = verseData.lineOfPos[endPos];
      const line = lineIdx != null ? verseData.lines[lineIdx] : null;
      if (!line) return { html: '…', n: null };
      const html = line.tokens.map(t => t.p === highlightPos
        ? `<span class="rounded px-1 font-semibold ${markCls}">${escapeHtml(t.f)}</span>`
        : escapeHtml(t.f)).join(' ');
      return { html, n: line.n };
    };

    const targetPos = text.lineEnds[beleg.vTarget];
    const partnerPos = text.lineEnds[beleg.vPartner];
    const targetVerse = renderVerse(beleg.vTarget, targetPos, 'bg-rose-100 text-rose-800');
    const partnerVerse = renderVerse(beleg.vPartner, partnerPos, 'bg-sky-100 text-sky-800');
    const inOrder = beleg.vTarget < beleg.vPartner
      ? [targetVerse, partnerVerse]
      : [partnerVerse, targetVerse];

    const verseLabel = inOrder[0].n && inOrder[1].n
      ? ` · V. ${escapeHtml(inOrder[0].n)}–${escapeHtml(inOrder[1].n)}`
      : '';
    const readerHref = `../korpus.html?textId=${encodeURIComponent(beleg.textId)}&lemmaIds=${encodeURIComponent(target.id)},${encodeURIComponent(partner.lemmaId)}&position=${targetPos}`;

    return `
      <div class="rounded-lg border border-slate-200 bg-white p-2.5">
        <div class="flex items-center justify-between gap-2 text-[10px] text-slate-500">
          <span><span class="font-mono text-slate-600">${escapeHtml(beleg.textId)}</span>${verseLabel}${text.title ? ` · ${escapeHtml(text.title)}` : ''}</span>
          <a href="${readerHref}" target="_blank" rel="noopener" class="flex-shrink-0 text-brand-700 hover:underline">im Reader öffnen</a>
        </div>
        <div class="mt-1 space-y-0.5 text-sm text-slate-700">
          <div>${inOrder[0].html}</div>
          <div>${inOrder[1].html}</div>
        </div>
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
      const acPosLabel = (l.posAll || (l.pos ? [l.pos] : [])).join(' ');
      const pos = acPosLabel ? `<span class="ml-1 rounded bg-slate-100 px-1 text-[10px] font-mono text-slate-600">${escapeHtml(acPosLabel)}</span>` : '';
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
        this.state.selectedLemma = c;
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

    document.querySelectorAll('[data-rd-belege-btn]').forEach(btn => {
      btn.addEventListener('click', () => {
        const idx = parseInt(btn.getAttribute('data-rd-belege-btn'), 10);
        if (!isNaN(idx)) this.toggleBelege(idx, btn);
      });
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
