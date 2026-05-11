/**
 * MHDBDB Playground - Lemma-Verteilung
 *
 * "In welchen Texten kommt Lemma X vor?" — Bar-Chart-Visualisierung
 * der Frequenz pro Text. Lemma-Auflösung über die 3-Stage-Resolution
 * im AuthorityFilesManager (exact → variants → partial).
 *
 * Issue: #90
 */

const DEFAULT_STATE = Object.freeze({
  query: '',
  resolvedLemma: null,       // {id, lemma, pos} oder null
  candidates: [],            // alternative Resolutions bei Partial-Match
  sortBy: 'frequency',       // 'frequency' | 'alphabetic'
  freqMode: 'absolute',      // 'absolute' | 'relative'
  topN: 30                   // wie viele Balken im Chart, Rest in Liste
});

const TOP_N_OPTIONS = [15, 30, 50, 100];

export class LemmaDistribution {
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

  computeDistribution(lemmaId) {
    const texts = this.getCorpusTexts() || [];
    const hits = [];
    for (const text of texts) {
      const positions = text.lemmata?.[lemmaId];
      if (positions && positions.length > 0) {
        const wc = text.wordCount || 0;
        hits.push({
          id: text.id,
          title: text.title || text.id,
          author: text.author || '',
          count: positions.length,
          rel: wc > 0 ? (positions.length / wc) * 1000 : 0,
          wordCount: wc
        });
      }
    }
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
      return (vb - va) * factor * -1;  // -1 to invert so desc
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
        <h3 class="text-sm font-semibold uppercase tracking-wide text-slate-500">Lemma-Verteilung</h3>
        <p class="text-xs text-slate-600">
          Geben Sie ein Lemma ein (z.B. <code class="rounded bg-white px-1.5 py-0.5 font-mono">minne</code>,
          <code class="rounded bg-white px-1.5 py-0.5 font-mono">êre</code>, <code class="rounded bg-white px-1.5 py-0.5 font-mono">vriunt</code>).
          Mittelhochdeutsche Sonderzeichen werden automatisch normalisiert (â→a, ê→e, ü→ue).
        </p>
        <div class="grid gap-3 sm:grid-cols-4">
          <label class="sm:col-span-2 block">
            <span class="text-xs font-medium text-slate-600">Lemma</span>
            <input id="ldQuery" type="text" autocomplete="off"
              value="${escapeAttr(this.state.query)}"
              placeholder="z.B. minne"
              class="mt-1 w-full rounded-lg border border-slate-200 bg-white px-3 py-2 text-sm focus:border-brand-400 focus:outline-none"/>
          </label>
          <label class="block">
            <span class="text-xs font-medium text-slate-600">Frequenz</span>
            <select id="ldFreqMode" class="mt-1 w-full rounded-lg border border-slate-200 bg-white px-3 py-2 text-sm focus:border-brand-400 focus:outline-none">
              <option value="absolute"${this.state.freqMode === 'absolute' ? ' selected' : ''}>Absolut</option>
              <option value="relative"${this.state.freqMode === 'relative' ? ' selected' : ''}>Relativ (pro 1000)</option>
            </select>
          </label>
          <label class="block">
            <span class="text-xs font-medium text-slate-600">Sortierung</span>
            <select id="ldSortBy" class="mt-1 w-full rounded-lg border border-slate-200 bg-white px-3 py-2 text-sm focus:border-brand-400 focus:outline-none">
              <option value="frequency"${this.state.sortBy === 'frequency' ? ' selected' : ''}>Frequenz</option>
              <option value="alphabetic"${this.state.sortBy === 'alphabetic' ? ' selected' : ''}>Alphabetisch (Sigle)</option>
            </select>
          </label>
        </div>
        <div class="flex items-center gap-3">
          <select id="ldTopN" class="rounded-lg border border-slate-200 bg-white px-3 py-1.5 text-xs">${topNOptions}</select>
          <button id="ldSearchBtn" type="button" class="rounded-lg border border-brand-200 bg-brand-50 px-4 py-1.5 text-sm font-medium text-brand-700 hover:border-brand-400 hover:bg-brand-100">Suchen</button>
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

    const dist = this.computeDistribution(lemma.id);
    if (dist.length === 0) {
      return `
        <div class="rounded-2xl border border-slate-200 bg-white p-6 text-sm">
          <div class="font-semibold text-slate-800">${escapeHtml(lemma.lemma || lemma.id)}</div>
          <div class="mt-1 text-xs text-slate-500">${escapeHtml(lemma.id)}</div>
          <p class="mt-3 text-slate-600">Keine Vorkommen im Korpus gefunden.</p>
          ${candidates}
        </div>
      `;
    }

    const sorted = this.sortedDistribution(dist);
    const totalOccurrences = dist.reduce((s, h) => s + h.count, 0);
    const cleanId = lemma.id.replace(/^lemma_/, '');

    return `
      <div class="rounded-2xl border border-slate-200 bg-white p-4 space-y-3">
        <header class="flex items-start justify-between gap-4">
          <div>
            <div class="text-xs uppercase tracking-wide text-slate-500">Lemma</div>
            <div class="text-lg font-semibold text-brand-700">
              <a href="../lemma/?id=${escapeHtml(cleanId)}" target="_blank" rel="noopener" class="hover:underline">${escapeHtml(lemma.lemma || lemma.id)}</a>
              ${lemma.pos ? `<span class="ml-2 rounded bg-slate-100 px-1.5 py-0.5 text-xs font-mono text-slate-600">${escapeHtml(lemma.pos)}</span>` : ''}
            </div>
            <div class="text-xs text-slate-500">${escapeHtml(lemma.id)}</div>
            ${candidates}
          </div>
          <div class="text-right text-xs text-slate-500">
            <div>${dist.length.toLocaleString('de-DE')} Texte</div>
            <div>${totalOccurrences.toLocaleString('de-DE')} Vorkommen gesamt</div>
          </div>
        </header>
        ${this.renderChart(sorted, lemma)}
      </div>
    `;
  }

  renderChart(sorted, lemma) {
    const cleanId = lemma.id.replace(/^lemma_/, '');
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
      const href = `../korpus.html?textId=${encodeURIComponent(h.id)}&lemmaIds=${encodeURIComponent(cleanId)}`;
      const tooltip = `${h.id} — ${h.title}\nAbsolut: ${h.count.toLocaleString('de-DE')}\npro 1000 Tokens: ${h.rel.toFixed(2)}`;
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
                <a href="../korpus.html?textId=${encodeURIComponent(h.id)}&lemmaIds=${encodeURIComponent(cleanId)}" target="_blank" rel="noopener"
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
          <span>${this.state.freqMode === 'relative' ? 'Frequenz pro 1000 Tokens' : 'Absolute Frequenz'} — Maximum: ${maxVal.toFixed(this.state.freqMode === 'relative' ? 2 : 0)}</span>
          <span>Klick auf Balken oder Sigle öffnet Text im Reader (mit Highlighting)</span>
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

  attachHandlers() {
    const runSearch = () => {
      const input = document.getElementById('ldQuery');
      if (!input) return;
      this.state.query = input.value;
      const { resolved, candidates } = this.resolveQuery(this.state.query);
      this.state.resolvedLemma = resolved;
      this.state.candidates = candidates;
      this.render();
      // Restore focus after re-render (only if user just clicked search)
      const newInput = document.getElementById('ldQuery');
      if (newInput) {
        newInput.focus();
        newInput.setSelectionRange(newInput.value.length, newInput.value.length);
      }
    };

    document.getElementById('ldSearchBtn')?.addEventListener('click', runSearch);
    document.getElementById('ldQuery')?.addEventListener('keydown', (e) => {
      if (e.key === 'Enter') {
        e.preventDefault();
        runSearch();
      }
    });
    document.getElementById('ldFreqMode')?.addEventListener('change', (e) => {
      this.state.freqMode = e.target.value;
      this.render();
    });
    document.getElementById('ldSortBy')?.addEventListener('change', (e) => {
      this.state.sortBy = e.target.value;
      this.render();
    });
    document.getElementById('ldTopN')?.addEventListener('change', (e) => {
      this.state.topN = parseInt(e.target.value, 10) || DEFAULT_STATE.topN;
      this.render();
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
