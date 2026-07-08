/**
 * MHDBDB Playground - Begriffs-Verteilung
 *
 * "Wo ist Begriff X (z.B. Sterben) im Korpus verteilt?" — Bar-Chart-Visualisierung
 * der Frequenz pro Text. Aggregiert alle Lemmata, deren senses[i].conceptIds
 * den gewählten Concept enthalten.
 *
 * Datenpfad: concept (gewählt) -> alle lemmata.senses[*].conceptIds matches
 *   -> Summe der text.lemmata[lemmaId].length über alle matching lemmata pro Text
 *
 * Analog zu lemma-distribution.js (#90), aber concept-basiert (#47-R2).
 */

import { getNavigationEpoch } from '../core/router.js';

const DEFAULT_STATE = Object.freeze({
  query: '',
  resolvedConcept: null,     // {id, termDE, termEN, normalized} oder null
  selectedConcept: null,     // explizite Autocomplete-Auswahl (#163) — schlägt resolveQuery
  candidates: [],            // alternative Concept-Matches
  matchingLemmata: [],       // [{id, lemma}] alle Lemmata, die diesen Concept referenzieren
  distribution: null,        // [{id, title, count, ...}] oder null wenn (noch) nicht berechnet
  computing: false,          // true waehrend async-Aggregation
  computeProgress: 0,        // 0..1 fuer Spinner-Anzeige
  sortBy: 'frequency',       // 'frequency' | 'alphabetic'
  freqMode: 'absolute',      // 'absolute' | 'relative'
  topN: 30,
  // Autocomplete (#113)
  autocompleteOpen: false,   // sichtbar/unsichtbar
  autocompleteIndex: -1,     // -1 = nichts highlighted; 0..N-1 = highlighted
  autocompleteItems: []      // gecachte top-N Suggestions fuer den aktuellen Eingabe-Text
});

// Max Anzahl Suggestions im Dropdown. resolveQuery() liefert oben bis zu 12;
// 8 reichen visuell ohne dass das Dropdown zu lang wird.
const AUTOCOMPLETE_LIMIT = 8;

const TOP_N_OPTIONS = [15, 30, 50, 100];
// Worst-case (concept_21072000: 8718 Lemmata) erzeugt ohne Chunking ~2.7s Long-
// Task. Mit time-based Yield bei 30ms pro Chunk bleiben Long-Tasks unter dem
// 50ms-Schwellwert, an dem der Browser sie als "blocking" wertet (UI bleibt
// responsive, Scroll/Klick reagieren). Gesamtdauer steigt minimal durch das
// Yield-Overhead, aber subjektiv ist es "Spinner laeuft" statt "Browser haengt".
const CHUNK_BUDGET_MS = 30;

// MessageChannel statt setTimeout(0) als yield-Mechanismus: setTimeout hat
// einen 4ms-Mindest-Delay im fokussierten Tab und wird auf >=1000ms
// gedrosselt, sobald der Tab in den Hintergrund geht (Chrome timer throttling
// fuer hidden tabs). MessageChannel hat keine solche Drosselung und liefert
// trotzdem einen frischen Macrotask, der den Longtask-Reporter zurueck-
// setzt. Beobachtet 2026-05-12: hidden tab + setTimeout(0) -> 95x langsamer.
function yieldToMain() {
  return new Promise(resolve => {
    const ch = new MessageChannel();
    ch.port1.onmessage = () => resolve();
    ch.port2.postMessage(null);
  });
}

export class ConceptDistribution {
  constructor(getCorpusTexts, authorityManager, getAuthorityData) {
    this.getCorpusTexts = getCorpusTexts;
    this.authorityManager = authorityManager;
    this.getAuthorityData = getAuthorityData;
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

  /**
   * Resolve user query to a concept. Matches termDE / termEN / normalized
   * primarily, falls back to altDE / altEN (with slightly lower scores so
   * the primary term wins on ties).
   *
   * Returns each candidate with `matchedAlt` when the hit came only via an
   * alternative term — used by the autocomplete dropdown to render the
   * "auch: …" hint (#113-Followup).
   */
  resolveQuery(query) {
    const trimmed = (query || '').trim();
    if (!trimmed) return { resolved: null, candidates: [] };

    const concepts = this.getAuthorityData().concepts || [];
    if (concepts.length === 0) return { resolved: null, candidates: [] };

    const needle = trimmed.toLowerCase();
    // Direct ID match (e.g. "concept_21104000")
    if (/^concept_\d+$/.test(trimmed)) {
      const direct = concepts.find(c => c.id === trimmed);
      if (direct) return { resolved: direct, candidates: [direct] };
    }

    const scored = [];
    for (const c of concepts) {
      const de = (c.termDE || '').toLowerCase();
      const en = (c.termEN || '').toLowerCase();
      const norm = (c.normalized || '').toLowerCase();

      let primaryScore = 0;
      if (de === needle || en === needle || norm === needle) primaryScore = 100;
      else if (de.startsWith(needle) || en.startsWith(needle) || norm.startsWith(needle)) primaryScore = 50;
      else if (de.includes(needle) || en.includes(needle) || norm.includes(needle)) primaryScore = 10;

      let altScore = 0;
      let matchedAlt = null;
      const altCandidates = [
        ...(c.altDE || []).map(t => ({ text: t, lower: t.toLowerCase() })),
        ...(c.altEN || []).map(t => ({ text: t, lower: t.toLowerCase() })),
        ...(c.altNormalized || []).map(t => ({ text: t, lower: t.toLowerCase() })),
      ];
      for (const alt of altCandidates) {
        let s = 0;
        if (alt.lower === needle) s = 90;
        else if (alt.lower.startsWith(needle)) s = 45;
        else if (alt.lower.includes(needle)) s = 8;
        if (s > altScore) {
          altScore = s;
          // Prefer the human-readable form (DE/EN) for the hint, not normalized
          if (alt.text && !(c.altNormalized || []).includes(alt.text)) {
            matchedAlt = alt.text;
          } else if (!matchedAlt) {
            matchedAlt = alt.text;
          }
        }
      }

      const score = Math.max(primaryScore, altScore);
      if (score === 0) continue;
      // Only attach hint when alternative-only match (no primary hit)
      const viaAlternative = primaryScore === 0 && altScore > 0;
      scored.push({ c, score, matchedAlt: viaAlternative ? matchedAlt : null });
    }
    if (scored.length === 0) return { resolved: null, candidates: [] };
    scored.sort((a, b) => b.score - a.score || (a.c.termDE || '').localeCompare(b.c.termDE || '', 'de'));
    return {
      resolved: scored[0].c,
      candidates: scored.slice(0, 12).map(s => ({ ...s.c, matchedAlt: s.matchedAlt }))
    };
  }

  /**
   * Find all lemmata whose senses reference the given concept.
   *
   * Synchron: pro Suche ein einzelner Pass ueber 43.754 Lemmata. Worst-Case
   * ~80-100ms Long-Task; akzeptabel, weil danach der async-chunked
   * computeDistribution-Pfad anlaeuft und die UI sofort wieder frei wird.
   * Async machen brachte ueberraschend mehr 100-200ms-Tasks (zusaetzliche
   * render()-Cycles dazwischen kosten mehr als die Synchronizitaet spart).
   */
  findMatchingLemmata(conceptId) {
    const lemmata = this.getAuthorityData().lemmata || [];
    const out = [];
    for (const l of lemmata) {
      if (!l.senses) continue;
      for (const s of l.senses) {
        if (s.conceptIds && s.conceptIds.includes(conceptId)) {
          out.push({ id: l.id, lemma: l.lemma, pos: l.pos });
          break;
        }
      }
    }
    return out;
  }

  /**
   * For each text, sum occurrences of all matching lemmata.
   *
   * Async + time-based Chunking: nach jeweils CHUNK_BUDGET_MS Rechenzeit yield
   * auf die Event-Loop. Das haelt jeden einzelnen Long-Task unter 50ms, sodass
   * die UI (Scroll, Klick, Spinner-Animation) waehrend der Aggregation
   * responsive bleibt. Wird sonst spuerbar bei concepts mit >2000 Lemmata
   * (13 Stueck im Korpus, Worst-Case 8718 Lemmata).
   */
  async computeDistribution(matchingLemmata, onProgress) {
    const texts = this.getCorpusTexts() || [];
    const lemmaIds = matchingLemmata.map(l => l.id);
    const hits = [];
    let chunkStart = performance.now();
    const myGen = this._searchGen;
    const myEpoch = getNavigationEpoch();
    for (let i = 0; i < texts.length; i++) {
      const text = texts[i];
      let total = 0;
      let distinctLemmata = 0;
      for (const lid of lemmaIds) {
        const positions = text.lemmata?.[lid];
        if (positions && positions.length > 0) {
          total += positions.length;
          distinctLemmata += 1;
        }
      }
      if (total > 0) {
        const wc = text.wordCount || 0;
        hits.push({
          id: text.id,
          title: text.title || text.id,
          author: text.author || '',
          count: total,
          distinctLemmata,
          rel: wc > 0 ? (total / wc) * 1000 : 0,
          wordCount: wc
        });
      }
      if (performance.now() - chunkStart > CHUNK_BUDGET_MS) {
        if (onProgress) onProgress((i + 1) / texts.length);
        await yieldToMain();
        // Abort on new search (generation token, #168) OR router navigation
        // to another view (epoch, #159) while we were yielding.
        if (this._searchGen !== myGen || getNavigationEpoch() !== myEpoch) return null;
        chunkStart = performance.now();
      }
    }
    if (onProgress) onProgress(1);
    return hits;
  }

  sortedDistribution(dist) {
    const factor = this.state.sortBy === 'alphabetic' ? 1 : -1;
    const out = [...dist];
    out.sort((a, b) => {
      if (this.state.sortBy === 'alphabetic') {
        return a.id.localeCompare(b.id, 'de');
      }
      const va = this.state.freqMode === 'relative' ? a.rel : a.count;
      const vb = this.state.freqMode === 'relative' ? b.rel : b.count;
      return (vb - va) * factor * -1;
    });
    return out;
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
    const topNOptions = TOP_N_OPTIONS
      .map(n => `<option value="${n}"${this.state.topN === n ? ' selected' : ''}>Top ${n} Balken</option>`)
      .join('');
    return `
      <div class="rounded-2xl border border-slate-200 bg-slate-50/70 p-4 space-y-3">
        <h3 class="text-sm font-semibold uppercase tracking-wide text-slate-500">Begriffs-Verteilung</h3>
        <p class="text-xs text-slate-600">
          Geben Sie einen Begriff ein (z.B. <code class="rounded bg-white px-1.5 py-0.5 font-mono">Sterben</code>,
          <code class="rounded bg-white px-1.5 py-0.5 font-mono">Liebe</code>, oder eine Concept-ID wie
          <code class="rounded bg-white px-1.5 py-0.5 font-mono">concept_21104000</code>).
          Aggregiert alle Lemmata, die diesem Begriff zugeordnet sind, und zeigt deren gemeinsame Häufigkeit pro Text.
        </p>
        <div class="grid gap-3 sm:grid-cols-4">
          <div class="sm:col-span-2">
            <label class="block">
              <span class="text-xs font-medium text-slate-600">Begriff (deutsch oder englisch)</span>
              <div class="relative mt-1">
                <input id="cdQuery" type="text" autocomplete="off" role="combobox"
                  aria-autocomplete="list" aria-controls="cdAutocomplete" aria-expanded="false"
                  value="${escapeAttr(this.state.query)}"
                  placeholder="z.B. Sterben"
                  class="w-full rounded-lg border border-slate-200 bg-white px-3 py-2 text-sm focus:border-brand-400 focus:outline-none"/>
                <div id="cdAutocomplete" role="listbox"
                  class="absolute left-0 right-0 top-full z-30 mt-1 hidden max-h-72 overflow-y-auto rounded-lg border border-slate-200 bg-white shadow-lg"></div>
              </div>
            </label>
          </div>
          <label class="block">
            <span class="text-xs font-medium text-slate-600">Frequenz</span>
            <select id="cdFreqMode" class="mt-1 w-full rounded-lg border border-slate-200 bg-white px-3 py-2 text-sm focus:border-brand-400 focus:outline-none">
              <option value="absolute"${this.state.freqMode === 'absolute' ? ' selected' : ''}>Absolut</option>
              <option value="relative"${this.state.freqMode === 'relative' ? ' selected' : ''}>Relativ (pro 1000)</option>
            </select>
          </label>
          <label class="block">
            <span class="text-xs font-medium text-slate-600">Sortierung</span>
            <select id="cdSortBy" class="mt-1 w-full rounded-lg border border-slate-200 bg-white px-3 py-2 text-sm focus:border-brand-400 focus:outline-none">
              <option value="frequency"${this.state.sortBy === 'frequency' ? ' selected' : ''}>Frequenz</option>
              <option value="alphabetic"${this.state.sortBy === 'alphabetic' ? ' selected' : ''}>Alphabetisch (Sigle)</option>
            </select>
          </label>
        </div>
        <div class="flex items-center gap-3">
          <select id="cdTopN" class="rounded-lg border border-slate-200 bg-white px-3 py-1.5 text-xs">${topNOptions}</select>
          <button id="cdSearchBtn" type="button" class="rounded-lg border border-brand-200 bg-brand-50 px-4 py-1.5 text-sm font-medium text-brand-700 hover:border-brand-400 hover:bg-brand-100">Suchen</button>
        </div>
      </div>
    `;
  }

  renderBody() {
    if (!this.state.query) {
      return '<div class="rounded-2xl border border-dashed border-slate-200 bg-white p-8 text-center text-sm text-slate-500">Bitte Begriff eingeben und auf „Suchen" klicken.</div>';
    }
    if (!this.state.resolvedConcept) {
      return `
        <div class="rounded-2xl border border-amber-200 bg-amber-50 p-4 text-sm text-amber-800">
          Kein Begriff gefunden für <code class="font-mono">${escapeHtml(this.state.query)}</code>.
          Versuchen Sie eine andere Schreibweise oder einen englischen Term.
        </div>
      `;
    }

    const concept = this.state.resolvedConcept;
    const candidates = this.state.candidates.length > 1
      ? `<div class="mt-2 text-xs text-slate-500">Weitere passende Begriffe: ${this.state.candidates.slice(1, 8).map(c => `<span class="mr-2 rounded bg-slate-100 px-1.5 py-0.5">${escapeHtml(c.termDE || c.id)}</span>`).join('')}</div>`
      : '';

    if (this.state.matchingLemmata.length === 0) {
      return `
        <div class="rounded-2xl border border-slate-200 bg-white p-6 text-sm">
          <div class="font-semibold text-slate-800">${escapeHtml(concept.termDE || concept.id)}</div>
          <div class="mt-1 text-xs text-slate-500">${escapeHtml(concept.id)}${concept.termEN ? ` · ${escapeHtml(concept.termEN)}` : ''}</div>
          <p class="mt-3 text-slate-600">Keine Lemmata sind diesem Begriff zugeordnet.</p>
          ${candidates}
        </div>
      `;
    }

    if (this.state.computing) {
      const pct = Math.round(this.state.computeProgress * 100);
      return `
        <div class="rounded-2xl border border-slate-200 bg-white p-6 text-sm">
          <div class="font-semibold text-slate-800">${escapeHtml(concept.termDE || concept.id)}</div>
          <div class="mt-1 text-xs text-slate-500">${escapeHtml(concept.id)} &middot; ${this.state.matchingLemmata.length.toLocaleString('de-DE')} Lemmata zugeordnet</div>
          <p class="mt-4 text-slate-600">Berechne Verteilung &uuml;ber 667 Texte ...</p>
          <div class="mt-2 h-2 w-full rounded bg-slate-100 overflow-hidden">
            <div id="cdProgressBar" class="h-full bg-brand-400 transition-all" style="width: ${pct}%"></div>
          </div>
          <div id="cdProgressLabel" class="mt-1 text-xs text-slate-500 tabular-nums">${pct} %</div>
        </div>
      `;
    }

    if (!this.state.distribution) {
      // sollte nie passieren ausser direkt nach Search-Klick vor erstem Render
      return '<div class="rounded-2xl border border-slate-100 bg-white p-6 text-sm text-slate-500">...</div>';
    }

    const dist = this.state.distribution;
    if (dist.length === 0) {
      return `
        <div class="rounded-2xl border border-slate-200 bg-white p-6 text-sm">
          <div class="font-semibold text-slate-800">${escapeHtml(concept.termDE || concept.id)}</div>
          <div class="mt-1 text-xs text-slate-500">${escapeHtml(concept.id)} · ${this.state.matchingLemmata.length} Lemmata zugeordnet</div>
          <p class="mt-3 text-slate-600">Keine der zugeordneten Lemmata kommt im aktuellen Korpus vor.</p>
          ${candidates}
        </div>
      `;
    }

    const sorted = this.sortedDistribution(dist);
    const totalOccurrences = dist.reduce((s, h) => s + h.count, 0);

    return `
      <div class="rounded-2xl border border-slate-200 bg-white p-4 space-y-3">
        <header class="flex items-start justify-between gap-4">
          <div>
            <div class="text-xs uppercase tracking-wide text-slate-500">Begriff</div>
            <div class="text-lg font-semibold text-brand-700">${escapeHtml(concept.termDE || concept.id)}</div>
            <div class="text-xs text-slate-500">${escapeHtml(concept.id)}${concept.termEN ? ` · ${escapeHtml(concept.termEN)}` : ''}</div>
            ${candidates}
          </div>
          <div class="text-right text-xs text-slate-500">
            <div>${this.state.matchingLemmata.length.toLocaleString('de-DE')} Lemmata zugeordnet</div>
            <div>${dist.length.toLocaleString('de-DE')} Texte mit Treffern</div>
            <div>${totalOccurrences.toLocaleString('de-DE')} Vorkommen gesamt</div>
          </div>
        </header>
        ${this.renderLemmataPreview()}
        ${this.renderChart(sorted, concept)}
      </div>
    `;
  }

  renderLemmataPreview() {
    const top = this.state.matchingLemmata.slice(0, 30);
    const rest = this.state.matchingLemmata.length - top.length;
    return `
      <details class="rounded-xl border border-slate-100 bg-slate-50/40 p-3">
        <summary class="cursor-pointer text-xs font-medium text-slate-600">Zugeordnete Lemmata anzeigen (${top.length}${rest > 0 ? ` von ${this.state.matchingLemmata.length}` : ''})</summary>
        <div class="mt-2 flex flex-wrap gap-1.5">
          ${top.map(l => {
            const cleanId = l.id.replace(/^lemma_/, '');
            return `<a href="../lemma/?id=${encodeURIComponent(cleanId)}" target="_blank" rel="noopener"
              class="inline-block rounded bg-white border border-slate-200 px-2 py-0.5 text-xs hover:border-brand-400 hover:text-brand-700">${escapeHtml(l.lemma)}${l.pos ? `<span class="ml-1 text-slate-400">${escapeHtml(l.pos)}</span>` : ''}</a>`;
          }).join('')}
          ${rest > 0 ? `<span class="text-xs text-slate-500 px-2 py-0.5">+${rest} weitere</span>` : ''}
        </div>
      </details>
    `;
  }

  renderChart(sorted, concept) {
    const topN = this.state.topN;
    const top = sorted.slice(0, topN);
    const rest = sorted.slice(topN);
    const maxVal = top.length === 0
      ? 1
      : Math.max(...top.map(h => this.state.freqMode === 'relative' ? h.rel : h.count));
    const barWidth = 18;
    const barGap = 4;
    const chartHeight = 220;
    const labelHeight = 60;
    const totalWidth = Math.max(top.length * (barWidth + barGap), 200);

    const bars = top.map((h, idx) => {
      const val = this.state.freqMode === 'relative' ? h.rel : h.count;
      const barH = maxVal > 0 ? Math.max(1, (val / maxVal) * chartHeight) : 0;
      const x = idx * (barWidth + barGap);
      const y = chartHeight - barH;
      // Click target: korpussuche im Text mit allen matching Lemmata highlighted.
      // Wir verlinken nur auf den Text (textId); die multi-lemma-Hervorhebung
      // wäre wertvoll, ist aber URL-mäßig limitiert. Nur textId schickt User
      // in die Leseansicht, von dort kann er weiter suchen.
      const href = `../korpus.html?textId=${encodeURIComponent(h.id)}`;
      const tooltip = `${h.id} - ${h.title}\nVorkommen: ${h.count.toLocaleString('de-DE')}\npro 1000 Tokens: ${h.rel.toFixed(2)}\ndistinkte Lemmata: ${h.distinctLemmata}`;
      return `
        <a href="${href}" target="_blank" rel="noopener">
          <title>${escapeHtml(tooltip)}</title>
          <rect x="${x}" y="${y}" width="${barWidth}" height="${barH}" rx="2"
            class="fill-brand-400 hover:fill-brand-600 transition" />
          <text x="${x + barWidth / 2}" y="${chartHeight + 12}"
            transform="rotate(45 ${x + barWidth / 2} ${chartHeight + 12})"
            class="fill-slate-600 text-[10px] font-mono">${escapeHtml(h.id)}</text>
        </a>
      `;
    }).join('');

    const restListHtml = rest.length > 0
      ? `
        <details class="mt-4 rounded-xl border border-slate-200 bg-slate-50 p-3">
          <summary class="cursor-pointer text-sm font-medium text-slate-700">Weitere ${rest.length} Texte anzeigen</summary>
          <ul class="mt-3 grid gap-1 text-sm sm:grid-cols-2">
            ${rest.map(h => `
              <li>
                <a href="../korpus.html?textId=${encodeURIComponent(h.id)}" target="_blank" rel="noopener"
                  class="flex items-center justify-between rounded px-2 py-1 hover:bg-white">
                  <span class="font-mono text-xs text-brand-700">${escapeHtml(h.id)}</span>
                  <span class="ml-2 flex-1 truncate text-xs text-slate-600">${escapeHtml(h.title)}</span>
                  <span class="ml-2 tabular-nums text-xs text-slate-700">${h.count.toLocaleString('de-DE')} | ${h.rel.toFixed(2)}</span>
                </a>
              </li>
            `).join('')}
          </ul>
        </details>
      `
      : '';

    return `
      <div class="overflow-x-auto rounded-xl border border-slate-100 bg-slate-50/40 p-3">
        <svg width="${totalWidth}" height="${chartHeight + labelHeight}" viewBox="0 0 ${totalWidth} ${chartHeight + labelHeight}" class="block">
          ${bars}
        </svg>
        <div class="mt-2 flex justify-between text-xs text-slate-500">
          <span>${this.state.freqMode === 'relative' ? 'Frequenz pro 1000 Tokens' : 'Absolute Frequenz'} - Maximum: ${maxVal.toFixed(this.state.freqMode === 'relative' ? 2 : 0)}</span>
          <span>Klick auf Balken oder Sigle öffnet Text im Reader</span>
        </div>
      </div>
      ${restListHtml}
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

  /**
   * Build dropdown DOM from current autocompleteItems. Direct DOM mutation,
   * KEIN re-render — sonst verliert das Input bei jedem Keypress den Fokus
   * und die Selection-Range.
   */
  renderAutocomplete() {
    const dd = document.getElementById('cdAutocomplete');
    const input = document.getElementById('cdQuery');
    if (!dd) return;
    const items = this.state.autocompleteItems || [];
    if (!this.state.autocompleteOpen || items.length === 0) {
      dd.classList.add('hidden');
      dd.innerHTML = '';
      if (input) input.setAttribute('aria-expanded', 'false');
      return;
    }
    const idx = this.state.autocompleteIndex;
    dd.innerHTML = items.map((c, i) => {
      const active = i === idx;
      const cls = active ? 'bg-brand-50 text-brand-800' : 'text-slate-700 hover:bg-slate-50';
      const en = c.termEN ? `<span class="text-xs text-slate-500"> · ${escapeHtml(c.termEN)}</span>` : '';
      const altHint = c.matchedAlt
        ? `<div class="mt-0.5 text-xs italic text-slate-500">auch: ${escapeHtml(c.matchedAlt)}</div>`
        : '';
      return `<button type="button" role="option" data-cd-ac-idx="${i}"
        aria-selected="${active}"
        class="block w-full cursor-pointer px-3 py-2 text-left text-sm ${cls}">
        <span class="font-medium">${escapeHtml(c.termDE || c.id)}</span>${en}
        <span class="ml-2 text-xs font-mono text-slate-400">${escapeHtml(c.id)}</span>
        ${altHint}
      </button>`;
    }).join('');
    dd.classList.remove('hidden');
    if (input) input.setAttribute('aria-expanded', 'true');
    // Active-Eintrag in den Viewport scrollen
    const activeEl = dd.querySelector(`[data-cd-ac-idx="${idx}"]`);
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
    const { candidates } = this.resolveQuery(trimmed);
    this.state.autocompleteItems = candidates.slice(0, AUTOCOMPLETE_LIMIT);
    // Bei Tippen: keinen Auto-Highlight setzen, sonst springt Enter unerwartet
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
    const runSearch = async () => {
      const input = document.getElementById('cdQuery');
      if (!input) return;
      this.state.query = input.value;
      this.closeAutocomplete();
      const { resolved, candidates } = this.resolveQuery(this.state.query);
      // Explizite Autocomplete-Auswahl (#163) schlägt die String-Auflösung —
      // aber nur solange der Query-Text noch der gewählten Form entspricht.
      const sel = this.state.selectedConcept;
      const useSelected = sel && (sel.termDE || sel.id) === (this.state.query || '').trim();
      const concept = useSelected ? sel : resolved;
      this.state.resolvedConcept = concept;
      this.state.candidates = candidates;
      this.state.matchingLemmata = concept ? this.findMatchingLemmata(concept.id) : [];
      this.state.distribution = null;

      if (!concept || this.state.matchingLemmata.length === 0) {
        this.state.computing = false;
        this.state.computeProgress = 0;
        this.render();
        this.refocusInput();
        return;
      }

      // Such-Generation (#168): das computing-Flag taugt nicht als
      // Identitätskriterium — bei zwei überlappenden Suchen gewann sonst
      // die ÄLTERE (sie committete ihre Verteilung und setzte computing=false,
      // die neuere verwarf sich selbst). Der Zähler macht jede Suche
      // eindeutig; der Navigation-Epoch verhindert zusätzlich, dass ein
      // fertiger Scan eine andere, inzwischen angezeigte View überschreibt (#159).
      this._searchGen = (this._searchGen || 0) + 1;
      const myGen = this._searchGen;
      const myEpoch = getNavigationEpoch();

      // Asynchrone Aggregation mit Chunking. Render Spinner zuerst, dann
      // Patch-Update der Progress-Bar ohne komplettes re-render (Form bleibt
      // stehen, Input behaelt Fokus). Nach Abschluss komplettes re-render.
      this.state.computing = true;
      this.state.computeProgress = 0;
      this.render();
      this.refocusInput();

      const dist = await this.computeDistribution(this.state.matchingLemmata, (frac) => {
        if (this._searchGen !== myGen) return;
        this.state.computeProgress = frac;
        const bar = document.getElementById('cdProgressBar');
        const label = document.getElementById('cdProgressLabel');
        if (bar) bar.style.width = `${Math.round(frac * 100)}%`;
        if (label) label.textContent = `${Math.round(frac * 100)} %`;
      });

      // Nur committen, wenn dies noch die aktuelle Suche ist und der User
      // nicht wegnavigiert hat.
      if (this._searchGen !== myGen || getNavigationEpoch() !== myEpoch) return;
      if (!dist) {
        this.state.computing = false;
        return;
      }

      this.state.distribution = dist;
      this.state.computing = false;
      this.state.computeProgress = 1;
      this.render();
    };

    document.getElementById('cdSearchBtn')?.addEventListener('click', runSearch);

    const input = document.getElementById('cdQuery');
    if (input) {
      // Live-Suggestions waehrend Tippen
      input.addEventListener('input', (e) => {
        // Manuelle Eingabe invalidiert eine frühere Dropdown-Auswahl (#163).
        this.state.selectedConcept = null;
        this.updateAutocomplete(e.target.value);
      });

      // Tastatur-Navigation im Dropdown
      input.addEventListener('keydown', (e) => {
        const open = this.state.autocompleteOpen && this.state.autocompleteItems.length > 0;
        if (e.key === 'Enter') {
          e.preventDefault();
          // Wenn ein Eintrag aktiv ist (Pfeil-Nav benutzt): diesen waehlen.
          if (open && this.state.autocompleteIndex >= 0) {
            const c = this.state.autocompleteItems[this.state.autocompleteIndex];
            input.value = c.termDE || c.id;
            this.state.selectedConcept = c;
            this.closeAutocomplete();
            runSearch();
            return;
          }
          // Sonst: normale Submit-Resolution wie bisher
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
          if (open) {
            e.preventDefault();
            this.closeAutocomplete();
          }
        }
      });

      // Bei Focus mit existierenden Items wieder oeffnen
      input.addEventListener('focus', () => {
        if (input.value.trim() && this.state.autocompleteItems.length > 0) {
          this.state.autocompleteOpen = true;
          this.renderAutocomplete();
        }
      });

      // Blur schliesst — aber mit setTimeout, sonst feuert blur vor click in dropdown
      input.addEventListener('blur', () => {
        setTimeout(() => this.closeAutocomplete(), 150);
      });
    }

    // Klick auf einen Dropdown-Eintrag waehlt + sucht
    const dd = document.getElementById('cdAutocomplete');
    if (dd) {
      dd.addEventListener('mousedown', (e) => {
        // mousedown statt click: feuert VOR blur, sodass das Dropdown nicht
        // erst geschlossen wird, bevor wir den geklickten Eintrag identifizieren.
        const btn = e.target.closest('[data-cd-ac-idx]');
        if (!btn) return;
        e.preventDefault();
        const idx = parseInt(btn.getAttribute('data-cd-ac-idx'), 10);
        const c = this.state.autocompleteItems[idx];
        if (!c) return;
        const inputEl = document.getElementById('cdQuery');
        if (inputEl) inputEl.value = c.termDE || c.id;
        this.state.selectedConcept = c;
        this.closeAutocomplete();
        runSearch();
      });
    }
    // sortBy / freqMode / topN aendern nur Anzeige, nicht die Aggregation.
    // Re-Render reicht; computeDistribution muss nicht erneut laufen.
    document.getElementById('cdFreqMode')?.addEventListener('change', (e) => {
      this.state.freqMode = e.target.value;
      this.render();
    });
    document.getElementById('cdSortBy')?.addEventListener('change', (e) => {
      this.state.sortBy = e.target.value;
      this.render();
    });
    document.getElementById('cdTopN')?.addEventListener('change', (e) => {
      this.state.topN = parseInt(e.target.value, 10) || DEFAULT_STATE.topN;
      this.render();
    });
  }

  refocusInput() {
    const newInput = document.getElementById('cdQuery');
    if (newInput) {
      newInput.focus();
      newInput.setSelectionRange(newInput.value.length, newInput.value.length);
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
