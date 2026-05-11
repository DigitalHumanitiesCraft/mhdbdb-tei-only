/**
 * MHDBDB Playground - Wortfrequenz-Analyse
 *
 * Top-N Lemmata-Frequenz, korpusweit oder pro Text. Daten aus dem
 * pre-built Corpus-Index (`text.lemmata` + `text.wordCount`).
 *
 * Issue: #88
 */

const TOP_N_OPTIONS = [20, 50, 100, 200];
const DEFAULT_TOP_N = 50;
const SORT_OPTIONS = [
  { value: 'absolute', label: 'Absolute Frequenz' },
  { value: 'relative', label: 'Relative Frequenz (pro 1000 Tokens)' }
];

export class WordFrequencyAnalyzer {
  /**
   * @param {() => Array} getCorpusTexts  thunk returning the current corpus
   *   texts array. Indirection lets the analyser read from whichever loader
   *   populated it first (`playground.corpusData` from autoLoadCorpus, or
   *   `playground.teiManager.corpusIndex` from the manual button).
   * @param {object} authorityData
   */
  constructor(getCorpusTexts, authorityData) {
    this.getCorpusTexts = getCorpusTexts;
    this.authorityData = authorityData;
    this._lemmaById = null;
    this._lastFreqData = null;
    this.state = {
      scope: 'corpus',
      topN: DEFAULT_TOP_N,
      sortBy: 'absolute'
    };
  }

  // O(1) lemma lookup, lazy-built once
  getLemmaById(id) {
    if (!this._lemmaById) {
      const lemmata = this.authorityData?.lemmata || [];
      this._lemmaById = new Map(lemmata.map(l => [l.id, l]));
    }
    return this._lemmaById.get(id);
  }

  computeFrequencies(scope) {
    const texts = this.getCorpusTexts() || [];
    if (texts.length === 0) return null;

    if (scope === 'corpus') {
      const counts = new Map();
      let totalTokens = 0;
      for (const text of texts) {
        totalTokens += text.wordCount || 0;
        for (const [lemmaId, positions] of Object.entries(text.lemmata || {})) {
          counts.set(lemmaId, (counts.get(lemmaId) || 0) + positions.length);
        }
      }
      return {
        counts,
        totalTokens,
        scopeLabel: 'Gesamtkorpus',
        scopeMeta: `${texts.length.toLocaleString('de-DE')} Texte`,
        uniqueCount: counts.size
      };
    }

    const text = texts.find(t => t.id === scope);
    if (!text) return null;
    const counts = new Map();
    for (const [lemmaId, positions] of Object.entries(text.lemmata || {})) {
      counts.set(lemmaId, positions.length);
    }
    return {
      counts,
      totalTokens: text.wordCount || 0,
      scopeLabel: text.title || text.id,
      scopeMeta: text.author ? `${text.id} • ${text.author}` : text.id,
      uniqueCount: counts.size
    };
  }

  async show() {
    const texts = this.getCorpusTexts();
    if (!texts || texts.length === 0) {
      this.renderError('Korpus ist noch nicht geladen. Bitte einen Moment warten und Button erneut klicken.');
      return;
    }
    this._lastFreqData = this.computeFrequencies(this.state.scope);
    this.render();
  }

  render() {
    const container = document.getElementById('resultsContainer');
    if (!container) return;

    container.innerHTML = `
      <div class="space-y-4">
        ${this.renderToolbar()}
        ${this.renderTable()}
      </div>
    `;
    this.attachToolbarHandlers();
  }

  renderToolbar() {
    const texts = [...(this.getCorpusTexts() || [])].sort((a, b) =>
      (a.id || '').localeCompare(b.id || '', 'de')
    );
    const scopeOptions = [
      `<option value="corpus"${this.state.scope === 'corpus' ? ' selected' : ''}>Gesamtkorpus (${texts.length} Texte)</option>`,
      ...texts.map(t => {
        const label = `${escapeHtml(t.id)}${t.title ? ' — ' + escapeHtml(t.title) : ''}`;
        return `<option value="${escapeHtml(t.id)}"${this.state.scope === t.id ? ' selected' : ''}>${label}</option>`;
      })
    ].join('');

    const topNOptions = TOP_N_OPTIONS
      .map(n => `<option value="${n}"${this.state.topN === n ? ' selected' : ''}>Top ${n}</option>`)
      .join('');

    const sortOptions = SORT_OPTIONS
      .map(o => `<option value="${o.value}"${this.state.sortBy === o.value ? ' selected' : ''}>${o.label}</option>`)
      .join('');

    return `
      <div class="rounded-2xl border border-slate-200 bg-slate-50/70 p-4">
        <h3 class="mb-3 text-sm font-semibold uppercase tracking-wide text-slate-500">Wortfrequenz-Analyse</h3>
        <div class="grid gap-3 sm:grid-cols-3">
          <label class="block">
            <span class="text-xs font-medium text-slate-600">Korpus-Auswahl</span>
            <select id="wfScope" class="mt-1 w-full rounded-lg border border-slate-200 bg-white px-3 py-2 text-sm focus:border-brand-400 focus:outline-none">${scopeOptions}</select>
          </label>
          <label class="block">
            <span class="text-xs font-medium text-slate-600">Anzahl</span>
            <select id="wfTopN" class="mt-1 w-full rounded-lg border border-slate-200 bg-white px-3 py-2 text-sm focus:border-brand-400 focus:outline-none">${topNOptions}</select>
          </label>
          <label class="block">
            <span class="text-xs font-medium text-slate-600">Sortierung</span>
            <select id="wfSortBy" class="mt-1 w-full rounded-lg border border-slate-200 bg-white px-3 py-2 text-sm focus:border-brand-400 focus:outline-none">${sortOptions}</select>
          </label>
        </div>
      </div>
    `;
  }

  renderTable() {
    const data = this._lastFreqData;
    if (!data) {
      return '<div class="rounded-2xl border border-dashed border-slate-200 bg-slate-50/70 p-6 text-center text-sm text-slate-500">Keine Daten.</div>';
    }
    const { counts, totalTokens, scopeLabel, scopeMeta, uniqueCount } = data;

    const entries = Array.from(counts.entries()).map(([id, c]) => ({
      id,
      count: c,
      rel: totalTokens > 0 ? (c / totalTokens) * 1000 : 0
    }));
    entries.sort((a, b) =>
      this.state.sortBy === 'relative' ? b.rel - a.rel : b.count - a.count
    );
    const top = entries.slice(0, this.state.topN);

    const rows = top.map((e, idx) => {
      const lemma = this.getLemmaById(e.id);
      const lemmaText = lemma ? lemma.lemma : e.id;
      const cleanId = e.id.replace(/^lemma_/, '');
      const pos = lemma?.pos
        ? `<span class="ml-2 rounded bg-slate-100 px-1.5 py-0.5 text-xs font-mono text-slate-600">${escapeHtml(lemma.pos)}</span>`
        : '';
      return `
        <tr class="border-t border-slate-100 hover:bg-brand-50/50">
          <td class="px-3 py-2 text-xs text-slate-500 tabular-nums">${idx + 1}</td>
          <td class="px-3 py-2">
            <a href="../lemma/?id=${escapeHtml(cleanId)}" target="_blank" rel="noopener" class="font-medium text-brand-700 hover:underline">${escapeHtml(lemmaText)}</a>
            ${pos}
          </td>
          <td class="px-3 py-2 text-right tabular-nums text-sm text-slate-700">${e.count.toLocaleString('de-DE')}</td>
          <td class="px-3 py-2 text-right tabular-nums text-sm text-slate-700">${e.rel.toFixed(2)}</td>
        </tr>
      `;
    }).join('');

    return `
      <div class="overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-sm">
        <header class="flex items-center justify-between border-b border-slate-200 bg-slate-50/80 px-4 py-3">
          <div>
            <div class="text-sm font-semibold text-slate-800">${escapeHtml(scopeLabel)}</div>
            <div class="text-xs text-slate-500">${escapeHtml(scopeMeta)}</div>
          </div>
          <div class="text-right text-xs text-slate-500">
            <div>${uniqueCount.toLocaleString('de-DE')} unique Lemmata</div>
            <div>${totalTokens.toLocaleString('de-DE')} Tokens</div>
          </div>
        </header>
        <table class="w-full">
          <thead class="text-xs uppercase tracking-wide text-slate-500">
            <tr class="bg-white">
              <th class="w-12 px-3 py-2 text-left">#</th>
              <th class="px-3 py-2 text-left">Lemma</th>
              <th class="px-3 py-2 text-right">Absolut</th>
              <th class="px-3 py-2 text-right">pro 1000</th>
            </tr>
          </thead>
          <tbody>${rows}</tbody>
        </table>
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

  attachToolbarHandlers() {
    const scopeEl = document.getElementById('wfScope');
    const topNEl = document.getElementById('wfTopN');
    const sortEl = document.getElementById('wfSortBy');

    scopeEl?.addEventListener('change', (e) => {
      this.state.scope = e.target.value;
      this._lastFreqData = this.computeFrequencies(this.state.scope);
      this.render();
    });
    topNEl?.addEventListener('change', (e) => {
      this.state.topN = parseInt(e.target.value, 10) || DEFAULT_TOP_N;
      this.render();
    });
    sortEl?.addEventListener('change', (e) => {
      this.state.sortBy = e.target.value;
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
