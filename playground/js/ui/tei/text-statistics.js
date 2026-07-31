/**
 * MHDBDB Playground - Text-Statistiken
 *
 * Stil-Visitenkarte pro Text: Token-Anzahl, Lemma-Diversität, Hapax-Rate,
 * durchschnittliche Lemmafrequenz. Sortierbare Übersichtstabelle aller
 * 667 Korpus-Texte.
 *
 * Auswahl-UI (#136): Checkbox je Zeile + Master-Checkbox, Aktionsleiste mit
 * Zähler, "Nur Auswahl anzeigen" und "Auswahl leeren". Die Auswahl lebt als
 * Set auf der Instanz und übersteht damit Sortieren und Filter-Toggles.
 *
 * Issues: #89, #136
 */

const COLUMNS = [
  { key: 'id',            label: 'Sigle',        align: 'left',  fmt: 'text' },
  { key: 'title',         label: 'Titel',        align: 'left',  fmt: 'text' },
  { key: 'wordCount',     label: 'Annot. Tokens', align: 'right', fmt: 'int' },
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
    this.selected = new Set();
    this.showSelectedOnly = false;
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
        ${this.renderSelectionBar()}
        ${this.renderTable()}
      </div>
    `;
    this.attachHandlers();
  }

  renderSelectionBar() {
    const n = this.selected.size;
    const total = this._stats?.length || 0;
    return `
      <div class="flex flex-wrap items-center gap-x-4 gap-y-2 rounded-2xl border border-slate-200 bg-white px-4 py-3 text-sm shadow-sm">
        <span class="text-slate-600">Ausgewählt:
          <strong id="tsSelCount" class="tabular-nums text-slate-800">${n.toLocaleString('de-DE')}</strong>
          <span class="text-slate-400">/ ${total.toLocaleString('de-DE')}</span>
        </span>
        <label class="flex cursor-pointer items-center gap-2 text-slate-600">
          <input type="checkbox" id="tsShowSelected" class="rounded border-slate-300"${this.showSelectedOnly ? ' checked' : ''}>
          Nur Auswahl anzeigen
        </label>
        <button id="tsClearSelection" type="button"
          class="rounded-lg border border-slate-200 bg-white px-3 py-1.5 text-xs text-slate-600 hover:border-slate-400${n === 0 ? ' opacity-50' : ''}"${n === 0 ? ' disabled' : ''}>
          Auswahl leeren
        </button>
      </div>
    `;
  }

  renderHeader() {
    const count = this._stats?.length || 0;
    return `
      <div class="rounded-2xl border border-slate-200 bg-slate-50/70 p-4">
        <h3 class="text-sm font-semibold uppercase tracking-wide text-slate-500">Text-Statistiken</h3>
        <p class="mt-2 text-sm text-slate-600">
          Stil-Visitenkarte aller ${count.toLocaleString('de-DE')} Texte im Korpus.
          Klick auf eine Spaltenüberschrift sortiert; Klick auf eine Sigle öffnet den Text im Reader.
          Mit den Häkchen lassen sich Texte auswählen und als Subset betrachten; die Auswahl bleibt beim Sortieren erhalten.
        </p>
        <dl class="mt-3 grid gap-2 text-xs text-slate-600 sm:grid-cols-3">
          <div><dt class="font-medium text-slate-700">Diversität</dt><dd>verschiedene Lemmata ÷ annotierte Tokens (Type-Token-Ratio). Sinkt mit der Textlänge, auch ohne stilistischen Grund: nach dieser Spalte sortiert stehen kurze Texte oben.</dd></div>
          <div><dt class="font-medium text-slate-700">Hapax-Rate</dt><dd>Anteil der Lemmata, die im Text genau einmal vorkommen, bezogen auf alle verschiedenen Lemmata des Texts. Nicht vergleichbar mit dem Werkzeug „Hapaxlegomena", das korpusweit einmalige Lemmata sucht.</dd></div>
          <div><dt class="font-medium text-slate-700">Ø-Freq</dt><dd>durchschnittliche Lemmafrequenz im Text: Vorkommen ÷ verschiedene Lemmata</dd></div>
        </dl>
        <p class="mt-2 text-xs text-slate-500">
          „Tokens" meint durchgehend die annotierten Wortformen: gezählt werden Wortformen mit Lemma-Zuordnung. Wörter ohne Zuordnung stehen im Text, aber in keiner dieser Zahlen, und ihr Anteil schwankt je Text zwischen 0 % und 42 %.
        </p>
      </div>
    `;
  }

  renderTable() {
    const sorted = this.sortedStats();
    const allVisibleSelected = sorted.length > 0 && sorted.every(s => this.selected.has(s.id));
    const selectAllTh = `<th class="px-3 py-2 text-left"><input type="checkbox" id="tsSelectAll" class="rounded border-slate-300" title="Alle angezeigten Texte aus-/abwählen"${allVisibleSelected ? ' checked' : ''}></th>`;
    const headerRow = selectAllTh + COLUMNS.map(col => {
      const isActive = this.sort.key === col.key;
      const arrow = isActive ? (this.sort.dir === 'asc' ? ' ↑' : ' ↓') : '';
      const alignClass = col.align === 'right' ? 'text-right' : 'text-left';
      return `<th data-sort-key="${col.key}" class="cursor-pointer select-none px-3 py-2 ${alignClass} text-xs font-semibold uppercase tracking-wide ${isActive ? 'text-brand-700' : 'text-slate-500'} hover:text-brand-700">${escapeHtml(col.label)}${arrow}</th>`;
    }).join('');

    if (sorted.length === 0 && this.showSelectedOnly) {
      return `
        <div class="rounded-2xl border border-slate-200 bg-white p-6 text-center text-sm text-slate-500 shadow-sm">
          Keine Texte ausgewählt. Häkchen in der Tabelle setzen oder „Nur Auswahl anzeigen" deaktivieren.
        </div>
      `;
    }

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
      const checkboxCell = `<td class="px-3 py-2 text-left"><input type="checkbox" data-select-id="${escapeHtml(s.id)}" class="rounded border-slate-300"${this.selected.has(s.id) ? ' checked' : ''}></td>`;
      return `<tr class="border-t border-slate-100 hover:bg-brand-50/50">${checkboxCell}${cells}</tr>`;
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
    const base = this.showSelectedOnly
      ? this._stats.filter(s => this.selected.has(s.id))
      : this._stats;
    const stats = [...base];
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

    // --- Auswahl (#136) ---
    // Einzel-Checkboxen aktualisieren nur Set + Leiste (kein Re-Render,
    // damit die Scroll-Position in der Tabelle erhalten bleibt).
    const updateBar = () => {
      const cnt = document.getElementById('tsSelCount');
      if (cnt) cnt.textContent = this.selected.size.toLocaleString('de-DE');
      const clearBtn = document.getElementById('tsClearSelection');
      if (clearBtn) {
        clearBtn.disabled = this.selected.size === 0;
        clearBtn.classList.toggle('opacity-50', this.selected.size === 0);
      }
      const master = document.getElementById('tsSelectAll');
      if (master) {
        const visible = this.sortedStats();
        master.checked = visible.length > 0 && visible.every(s => this.selected.has(s.id));
      }
    };

    document.querySelectorAll('[data-select-id]').forEach(cb => {
      cb.addEventListener('change', () => {
        if (cb.checked) this.selected.add(cb.dataset.selectId);
        else this.selected.delete(cb.dataset.selectId);
        // Im Modus „Nur Auswahl anzeigen" muss die abgewählte Zeile sofort
        // aus der Tabelle verschwinden (#167 Finding 67).
        if (this.showSelectedOnly) {
          this.render();
        } else {
          updateBar();
        }
      });
    });

    document.getElementById('tsSelectAll')?.addEventListener('change', (e) => {
      const visible = this.sortedStats();
      if (e.target.checked) visible.forEach(s => this.selected.add(s.id));
      else visible.forEach(s => this.selected.delete(s.id));
      this.render();
    });

    document.getElementById('tsShowSelected')?.addEventListener('change', (e) => {
      this.showSelectedOnly = e.target.checked;
      this.render();
    });

    document.getElementById('tsClearSelection')?.addEventListener('click', () => {
      this.selected.clear();
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
