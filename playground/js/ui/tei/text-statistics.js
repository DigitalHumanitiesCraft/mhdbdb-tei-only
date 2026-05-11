/**
 * MHDBDB Playground - Text-Statistiken
 *
 * Stil-Visitenkarte pro Text: Token-Anzahl, Lemma-Diversität, Hapax-Rate,
 * durchschnittliche Lemmafrequenz. Sortierbare Übersichtstabelle aller
 * 667 Korpus-Texte.
 *
 * Issue: #89
 */

const COLUMNS = [
  { key: 'id',            label: 'Sigle',        align: 'left',  fmt: 'text' },
  { key: 'title',         label: 'Titel',        align: 'left',  fmt: 'text' },
  { key: 'wordCount',     label: 'Tokens',       align: 'right', fmt: 'int' },
  { key: 'uniqueLemmata', label: 'Unique',       align: 'right', fmt: 'int' },
  { key: 'diversity',     label: 'Diversität',   align: 'right', fmt: 'pct3' },
  { key: 'hapaxRate',     label: 'Hapax-Rate',   align: 'right', fmt: 'pct3' },
  { key: 'avgLemmaFreq',  label: 'Ø-Freq',       align: 'right', fmt: 'float' }
];

const DEFAULT_SORT = { key: 'wordCount', dir: 'desc' };

export class TextStatistics {
  constructor(getCorpusTexts) {
    this.getCorpusTexts = getCorpusTexts;
    this._stats = null;
    this.sort = { ...DEFAULT_SORT };
  }

  computeAllStats() {
    const texts = this.getCorpusTexts() || [];
    return texts.map(text => {
      const wordCount = text.wordCount || 0;
      const lemmaIds = Object.keys(text.lemmata || {});
      const uniqueLemmata = lemmaIds.length;
      let totalLemmaTokens = 0;
      let hapax = 0;
      for (const id of lemmaIds) {
        const freq = text.lemmata[id].length;
        totalLemmaTokens += freq;
        if (freq === 1) hapax++;
      }
      return {
        id: text.id,
        title: text.title || text.id,
        author: text.author || '',
        wordCount,
        uniqueLemmata,
        diversity: wordCount > 0 ? uniqueLemmata / wordCount : 0,
        hapaxRate: uniqueLemmata > 0 ? hapax / uniqueLemmata : 0,
        avgLemmaFreq: uniqueLemmata > 0 ? totalLemmaTokens / uniqueLemmata : 0
      };
    });
  }

  show() {
    const texts = this.getCorpusTexts();
    if (!texts || texts.length === 0) {
      this.renderError('Korpus ist noch nicht geladen. Bitte einen Moment warten und Button erneut klicken.');
      return;
    }
    this._stats = this.computeAllStats();
    this.render();
  }

  render() {
    const container = document.getElementById('resultsContainer');
    if (!container) return;

    container.innerHTML = `
      <div class="space-y-4">
        ${this.renderHeader()}
        ${this.renderTable()}
      </div>
    `;
    this.attachHandlers();
  }

  renderHeader() {
    const count = this._stats?.length || 0;
    return `
      <div class="rounded-2xl border border-slate-200 bg-slate-50/70 p-4">
        <h3 class="text-sm font-semibold uppercase tracking-wide text-slate-500">Text-Statistiken</h3>
        <p class="mt-2 text-sm text-slate-600">
          Stil-Visitenkarte aller ${count.toLocaleString('de-DE')} Texte im Korpus.
          Klick auf eine Spaltenüberschrift sortiert; Klick auf eine Sigle öffnet den Text im Reader.
        </p>
        <dl class="mt-3 grid gap-2 text-xs text-slate-600 sm:grid-cols-3">
          <div><dt class="font-medium text-slate-700">Diversität</dt><dd>unique Lemmata ÷ Tokens (Type-Token-Ratio)</dd></div>
          <div><dt class="font-medium text-slate-700">Hapax-Rate</dt><dd>Anteil Lemmata mit Frequenz 1</dd></div>
          <div><dt class="font-medium text-slate-700">Ø-Freq</dt><dd>durchschnittliche Lemmafrequenz im Text</dd></div>
        </dl>
      </div>
    `;
  }

  renderTable() {
    const sorted = this.sortedStats();
    const headerRow = COLUMNS.map(col => {
      const isActive = this.sort.key === col.key;
      const arrow = isActive ? (this.sort.dir === 'asc' ? ' ↑' : ' ↓') : '';
      const alignClass = col.align === 'right' ? 'text-right' : 'text-left';
      return `<th data-sort-key="${col.key}" class="cursor-pointer select-none px-3 py-2 ${alignClass} text-xs font-semibold uppercase tracking-wide ${isActive ? 'text-brand-700' : 'text-slate-500'} hover:text-brand-700">${escapeHtml(col.label)}${arrow}</th>`;
    }).join('');

    const rows = sorted.map(s => {
      const cells = COLUMNS.map(col => {
        const v = s[col.key];
        let display;
        switch (col.fmt) {
          case 'int':   display = (v || 0).toLocaleString('de-DE'); break;
          case 'pct3':  display = (v || 0).toFixed(3); break;
          case 'float': display = (v || 0).toFixed(2); break;
          default:      display = escapeHtml(v == null ? '' : String(v));
        }
        const alignClass = col.align === 'right' ? 'text-right tabular-nums' : 'text-left';
        if (col.key === 'id') {
          return `<td class="px-3 py-2 ${alignClass}"><a href="../korpus.html?textId=${encodeURIComponent(s.id)}" target="_blank" rel="noopener" class="font-mono text-brand-700 hover:underline">${escapeHtml(s.id)}</a></td>`;
        }
        if (col.key === 'title') {
          const author = s.author ? `<span class="block text-xs text-slate-500">${escapeHtml(s.author)}</span>` : '';
          return `<td class="px-3 py-2 ${alignClass}"><span class="text-sm text-slate-700">${escapeHtml(s.title)}</span>${author}</td>`;
        }
        return `<td class="px-3 py-2 ${alignClass} text-sm text-slate-700">${display}</td>`;
      }).join('');
      return `<tr class="border-t border-slate-100 hover:bg-brand-50/50">${cells}</tr>`;
    }).join('');

    return `
      <div class="overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-sm">
        <div class="max-h-[640px] overflow-auto">
          <table class="w-full">
            <thead class="sticky top-0 bg-slate-50/95 backdrop-blur">
              <tr>${headerRow}</tr>
            </thead>
            <tbody>${rows}</tbody>
          </table>
        </div>
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

  sortedStats() {
    if (!this._stats) return [];
    const { key, dir } = this.sort;
    const factor = dir === 'asc' ? 1 : -1;
    const stats = [...this._stats];
    stats.sort((a, b) => {
      const va = a[key];
      const vb = b[key];
      if (typeof va === 'number' && typeof vb === 'number') return (va - vb) * factor;
      return String(va || '').localeCompare(String(vb || ''), 'de') * factor;
    });
    return stats;
  }

  attachHandlers() {
    document.querySelectorAll('[data-sort-key]').forEach(th => {
      th.addEventListener('click', () => {
        const key = th.dataset.sortKey;
        if (this.sort.key === key) {
          this.sort.dir = this.sort.dir === 'asc' ? 'desc' : 'asc';
        } else {
          this.sort.key = key;
          // Text-columns default to asc, numeric to desc
          const col = COLUMNS.find(c => c.key === key);
          this.sort.dir = (col && (col.fmt === 'text')) ? 'asc' : 'desc';
        }
        this.render();
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
