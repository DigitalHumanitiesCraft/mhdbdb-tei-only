/**
 * MHDBDB Playground - Textvergleich
 *
 * Zwei Texte auswählen → drei Lemma-Mengen (Nur A / Beide / Nur B).
 * Reine Set-Operationen auf Object.keys(text.lemmata); Frequenzen direkt
 * aus text.lemmata[lid].length. Kein neuer Index-Build-Schritt.
 *
 * Issue: #108
 */

import { buildTextLabelDisambiguator } from '../core/ui-helpers.js';
import { TextNormalizer } from '../../../../assets/js/lib/text-normalizer.js';

const DEFAULT_STATE = Object.freeze({
  textAId: '',
  textBId: '',
  category: 'both',          // 'both' | 'only-a' | 'only-b'
  sortBy: 'frequency',       // 'frequency' | 'difference' | 'alphabetic'
  nameFilter: '',
  showAll: false
});

const TOP_N_DEFAULT = 100;

export class TextComparison {
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
    this.ensureLemmaMap();
    this.render();
  }

  getTextById(id) {
    if (!id) return null;
    const texts = this.getCorpusTexts() || [];
    return texts.find(t => t.id === id) || null;
  }

  /**
   * Compute the three lemma sets for the currently selected text pair.
   * Returns { onlyA, onlyB, both } — each is an array of
   *   { lemmaId, lemma, pos, countA, countB, diff }.
   * Heavy lookups (lemma form, POS) happen lazily during render, not here.
   */
  computeComparison(textA, textB) {
    if (!textA || !textB) return { onlyA: [], onlyB: [], both: [] };

    const lemmataA = textA.lemmata || {};
    const lemmataB = textB.lemmata || {};

    const keysA = Object.keys(lemmataA);
    const keysB = new Set(Object.keys(lemmataB));

    const onlyA = [];
    const both = [];
    for (const k of keysA) {
      const countA = lemmataA[k]?.length || 0;
      if (keysB.has(k)) {
        const countB = lemmataB[k]?.length || 0;
        both.push({ lemmaId: k, countA, countB, diff: Math.abs(countA - countB) });
      } else {
        onlyA.push({ lemmaId: k, countA, countB: 0, diff: countA });
      }
    }

    const keysASet = new Set(keysA);
    const onlyB = [];
    for (const k of Object.keys(lemmataB)) {
      if (!keysASet.has(k)) {
        onlyB.push({ lemmaId: k, countA: 0, countB: lemmataB[k]?.length || 0, diff: lemmataB[k]?.length || 0 });
      }
    }

    return { onlyA, onlyB, both };
  }

  /**
   * O(N)-Linear-Lookup in authorityManager.findLemmaById ist bei 3000+
   * gemeinsamen Lemmata × 42.000 Lexikon-Einträgen unbenutzbar (≈6s).
   * Diese Map wird einmal pro show() aufgebaut und für alle Render-Cycles
   * der gleichen Session wiederverwendet.
   */
  ensureLemmaMap() {
    if (this._lemmaMap) return;
    this._lemmaMap = new Map();
    const lemmata = this.authorityManager?.authorityData?.lemmata || [];
    for (const l of lemmata) {
      if (l?.id) this._lemmaMap.set(l.id, l);
    }
  }

  enrichWithLemma(row) {
    const lemma = this._lemmaMap?.get(row.lemmaId);
    return {
      ...row,
      lemma: lemma?.lemma || row.lemmaId,
      // #187: alle POS-Werte (Fallback: Erstwert aus altem Cache)
      pos: (lemma?.posAll || (lemma?.pos ? [lemma.pos] : [])).join(' ')
    };
  }

  sortRows(rows, category) {
    const out = [...rows];
    const { sortBy } = this.state;
    if (sortBy === 'alphabetic') {
      out.sort((a, b) => (a.lemma || a.lemmaId).localeCompare(b.lemma || b.lemmaId, 'de'));
    } else if (sortBy === 'difference') {
      out.sort((a, b) => b.diff - a.diff);
    } else {
      // frequency: für 'only-a' nach countA, für 'only-b' nach countB, sonst summe
      if (category === 'only-a') {
        out.sort((a, b) => b.countA - a.countA);
      } else if (category === 'only-b') {
        out.sort((a, b) => b.countB - a.countB);
      } else {
        out.sort((a, b) => (b.countA + b.countB) - (a.countA + a.countB));
      }
    }
    return out;
  }

  filterByName(rows) {
    const f = this.state.nameFilter.trim();
    if (!f) return rows;
    // MHG-normalisierter Vergleich wie im naming-explorer: „tot" muss
    // „tôtwunt" finden (#167 Finding 23).
    return rows.filter(r => TextNormalizer.matchesNormalized(r.lemma || r.lemmaId, f));
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
    const texts = this.getCorpusTexts() || [];
    const sorted = [...texts].sort((a, b) => (a.id || '').localeCompare(b.id || '', 'de'));
    const disambig = buildTextLabelDisambiguator(
      sorted, this.authorityManager?.authorityData?.works || []
    );
    const options = sorted.map(t => {
      const label = `${t.id}-${t.title || ''}${disambig.get(t.id) || ''}${t.author ? ', ' + t.author : ''}`;
      return { value: t.id, label };
    });

    const buildSelect = (selectedId) => options.map(o =>
      `<option value="${escapeAttr(o.value)}"${o.value === selectedId ? ' selected' : ''}>${escapeHtml(o.label)}</option>`
    ).join('');

    return `
      <div class="rounded-2xl border border-slate-200 bg-slate-50/70 p-4 space-y-3">
        <h3 class="text-sm font-semibold uppercase tracking-wide text-slate-500">Textvergleich</h3>
        <p class="text-xs text-slate-600">
          Zwei Texte auswählen. Die Lemma-Mengen werden verglichen: Was hat nur Text A, was nur Text B, was beide gemeinsam (mit Frequenz und Differenz).
        </p>
        <div class="grid gap-3 sm:grid-cols-2">
          <label class="block">
            <span class="text-xs font-medium text-slate-600">Text A</span>
            <select id="tcSelectA" class="mt-1 w-full rounded-lg border border-slate-200 bg-white px-3 py-2 text-sm focus:border-brand-400 focus:outline-none">
              <option value="">Text wählen …</option>
              ${buildSelect(this.state.textAId)}
            </select>
          </label>
          <label class="block">
            <span class="text-xs font-medium text-slate-600">Text B</span>
            <select id="tcSelectB" class="mt-1 w-full rounded-lg border border-slate-200 bg-white px-3 py-2 text-sm focus:border-brand-400 focus:outline-none">
              <option value="">Text wählen …</option>
              ${buildSelect(this.state.textBId)}
            </select>
          </label>
        </div>
        <div class="flex flex-wrap items-center gap-3">
          <button id="tcCompareBtn" type="button" class="rounded-lg border border-brand-200 bg-brand-50 px-4 py-1.5 text-sm font-medium text-brand-700 hover:border-brand-400 hover:bg-brand-100">Vergleichen</button>
          <button id="tcSwapBtn" type="button" class="rounded-lg border border-slate-200 bg-white px-3 py-1.5 text-xs text-slate-600 hover:border-slate-400" title="Texte tauschen">A ↔ B</button>
        </div>
      </div>
    `;
  }

  renderBody() {
    if (!this.state.textAId || !this.state.textBId) {
      return '<div class="rounded-2xl border border-dashed border-slate-200 bg-white p-8 text-center text-sm text-slate-500">Bitte zwei Texte auswählen und auf „Vergleichen" klicken.</div>';
    }

    const textA = this.getTextById(this.state.textAId);
    const textB = this.getTextById(this.state.textBId);

    if (!textA || !textB) {
      return '<div class="rounded-2xl border border-amber-200 bg-amber-50 p-4 text-sm text-amber-800">Mindestens ein ausgewählter Text wurde nicht im Korpus gefunden.</div>';
    }

    if (textA.id === textB.id) {
      return '<div class="rounded-2xl border border-amber-200 bg-amber-50 p-4 text-sm text-amber-800">Text A und Text B sind identisch. Bitte zwei unterschiedliche Texte wählen.</div>';
    }

    const { onlyA, onlyB, both } = this.computeComparison(textA, textB);

    const summary = `
      <div class="rounded-2xl border border-slate-200 bg-white p-4 space-y-3">
        <div class="grid gap-2 sm:grid-cols-2 text-sm">
          <div>
            <div class="text-xs uppercase tracking-wide text-slate-500">Text A</div>
            <div class="font-semibold text-brand-700">${escapeHtml(textA.id)}-${escapeHtml(textA.title || '')}</div>
            ${textA.author ? `<div class="text-xs text-slate-500">${escapeHtml(textA.author)}</div>` : ''}
            <div class="mt-1 text-xs text-slate-500">${(Object.keys(textA.lemmata || {}).length).toLocaleString('de-DE')} unique Lemmata · ${(textA.wordCount || 0).toLocaleString('de-DE')} annot. Tokens</div>
          </div>
          <div>
            <div class="text-xs uppercase tracking-wide text-slate-500">Text B</div>
            <div class="font-semibold text-brand-700">${escapeHtml(textB.id)}-${escapeHtml(textB.title || '')}</div>
            ${textB.author ? `<div class="text-xs text-slate-500">${escapeHtml(textB.author)}</div>` : ''}
            <div class="mt-1 text-xs text-slate-500">${(Object.keys(textB.lemmata || {}).length).toLocaleString('de-DE')} unique Lemmata · ${(textB.wordCount || 0).toLocaleString('de-DE')} annot. Tokens</div>
          </div>
        </div>
      </div>
    `;

    const tabs = this.renderCategoryTabs(onlyA.length, both.length, onlyB.length);

    let activeRows;
    if (this.state.category === 'only-a') activeRows = onlyA;
    else if (this.state.category === 'only-b') activeRows = onlyB;
    else activeRows = both;

    const enriched = activeRows.map(r => this.enrichWithLemma(r));
    const filtered = this.filterByName(enriched);
    const sortedRows = this.sortRows(filtered, this.state.category);

    const controls = this.renderControls(filtered.length);
    const table = this.renderTable(sortedRows, textA, textB);

    return summary + tabs + controls + table;
  }

  renderCategoryTabs(nA, nBoth, nB) {
    const cats = [
      { key: 'only-a', label: 'Nur A', count: nA, color: 'rose' },
      { key: 'both', label: 'Beide', count: nBoth, color: 'brand' },
      { key: 'only-b', label: 'Nur B', count: nB, color: 'amber' }
    ];
    const buttons = cats.map(c => {
      const active = c.key === this.state.category;
      const cls = active
        ? 'border-brand-400 bg-brand-50 text-brand-700'
        : 'border-slate-200 bg-white text-slate-600 hover:border-slate-400';
      return `<button type="button" data-tc-cat="${c.key}" class="rounded-lg border px-3 py-1.5 text-sm transition ${cls}">${c.label}<span class="ml-2 rounded bg-slate-100 px-1.5 py-0.5 text-xs font-mono text-slate-600">${c.count.toLocaleString('de-DE')}</span></button>`;
    }).join('');
    return `<div class="flex flex-wrap gap-2">${buttons}</div>`;
  }

  renderControls(filteredCount) {
    return `
      <div class="flex flex-wrap items-center gap-3 rounded-xl border border-slate-200 bg-slate-50/60 p-3 text-sm">
        <label class="flex items-center gap-2">
          <span class="text-xs font-medium text-slate-600">Sortierung</span>
          <select id="tcSortBy" class="rounded-lg border border-slate-200 bg-white px-2 py-1 text-xs">
            <option value="frequency"${this.state.sortBy === 'frequency' ? ' selected' : ''}>Frequenz</option>
            <option value="difference"${this.state.sortBy === 'difference' ? ' selected' : ''}>Differenz |A−B|</option>
            <option value="alphabetic"${this.state.sortBy === 'alphabetic' ? ' selected' : ''}>Alphabetisch</option>
          </select>
        </label>
        <label class="flex items-center gap-2 flex-1 min-w-[200px]">
          <span class="text-xs font-medium text-slate-600">Lemma-Filter</span>
          <input id="tcNameFilter" type="text" autocomplete="off"
            value="${escapeAttr(this.state.nameFilter)}"
            placeholder="z.B. minne"
            class="w-full rounded-lg border border-slate-200 bg-white px-2 py-1 text-xs focus:border-brand-400 focus:outline-none" />
        </label>
        <label class="flex items-center gap-2 text-xs text-slate-600">
          <input id="tcShowAll" type="checkbox"${this.state.showAll ? ' checked' : ''} class="rounded border-slate-300" />
          Alle ${filteredCount.toLocaleString('de-DE')} Zeilen
        </label>
      </div>
    `;
  }

  renderTable(rows, textA, textB) {
    if (rows.length === 0) {
      return '<div class="rounded-2xl border border-dashed border-slate-200 bg-white p-6 text-center text-sm text-slate-500">Keine Lemmata in dieser Kategorie (mit aktuellem Filter).</div>';
    }

    const limit = this.state.showAll ? rows.length : Math.min(TOP_N_DEFAULT, rows.length);
    const visible = rows.slice(0, limit);
    const truncated = rows.length > limit;

    const showA = this.state.category !== 'only-b';
    const showB = this.state.category !== 'only-a';
    const showDiff = this.state.category === 'both';

    const trs = visible.map(r => {
      const cleanId = r.lemmaId.replace(/^lemma_/, '');
      const lemmaLink = `<a href="../lemma/?id=${escapeAttr(cleanId)}" target="_blank" rel="noopener" class="font-medium text-brand-700 hover:underline">${escapeHtml(r.lemma)}</a>`;
      const posSpan = r.pos ? `<span class="ml-1 rounded bg-slate-100 px-1 text-[10px] font-mono text-slate-600">${escapeHtml(r.pos)}</span>` : '';
      const readerA = showA && r.countA > 0
        ? `<a href="../korpus.html?textId=${encodeURIComponent(textA.id)}&lemmaIds=${encodeURIComponent(r.lemmaId)}" target="_blank" rel="noopener" class="tabular-nums text-brand-700 hover:underline" title="Im Reader von ${escapeAttr(textA.id)} anzeigen">${r.countA.toLocaleString('de-DE')}</a>`
        : `<span class="tabular-nums text-slate-400">${r.countA.toLocaleString('de-DE')}</span>`;
      const readerB = showB && r.countB > 0
        ? `<a href="../korpus.html?textId=${encodeURIComponent(textB.id)}&lemmaIds=${encodeURIComponent(r.lemmaId)}" target="_blank" rel="noopener" class="tabular-nums text-brand-700 hover:underline" title="Im Reader von ${escapeAttr(textB.id)} anzeigen">${r.countB.toLocaleString('de-DE')}</a>`
        : `<span class="tabular-nums text-slate-400">${r.countB.toLocaleString('de-DE')}</span>`;
      const diffCell = showDiff ? `<td class="px-3 py-1.5 text-right tabular-nums text-slate-600">${r.diff.toLocaleString('de-DE')}</td>` : '';
      return `
        <tr class="border-b border-slate-100 hover:bg-slate-50">
          <td class="px-3 py-1.5">${lemmaLink}${posSpan}</td>
          ${showA ? `<td class="px-3 py-1.5 text-right">${readerA}</td>` : ''}
          ${showB ? `<td class="px-3 py-1.5 text-right">${readerB}</td>` : ''}
          ${diffCell}
        </tr>
      `;
    }).join('');

    const headA = showA ? `<th class="px-3 py-2 text-right text-xs font-semibold text-slate-600">${escapeHtml(textA.id)}</th>` : '';
    const headB = showB ? `<th class="px-3 py-2 text-right text-xs font-semibold text-slate-600">${escapeHtml(textB.id)}</th>` : '';
    const headDiff = showDiff ? `<th class="px-3 py-2 text-right text-xs font-semibold text-slate-600">|A−B|</th>` : '';

    const footer = truncated
      ? `<div class="mt-2 text-center text-xs text-slate-500">Zeige ${visible.length.toLocaleString('de-DE')} von ${rows.length.toLocaleString('de-DE')} Zeilen. „Alle anzeigen" oben aktivieren für vollständige Tabelle.</div>`
      : '';

    return `
      <div class="overflow-x-auto rounded-2xl border border-slate-200 bg-white">
        <table class="w-full text-sm">
          <thead class="bg-slate-50">
            <tr>
              <th class="px-3 py-2 text-left text-xs font-semibold text-slate-600">Lemma</th>
              ${headA}
              ${headB}
              ${headDiff}
            </tr>
          </thead>
          <tbody>${trs}</tbody>
        </table>
      </div>
      ${footer}
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
    const selA = document.getElementById('tcSelectA');
    const selB = document.getElementById('tcSelectB');
    if (selA) selA.addEventListener('change', (e) => { this.state.textAId = e.target.value; });
    if (selB) selB.addEventListener('change', (e) => { this.state.textBId = e.target.value; });

    document.getElementById('tcCompareBtn')?.addEventListener('click', () => {
      this.state.showAll = false;
      this.render();
    });

    document.getElementById('tcSwapBtn')?.addEventListener('click', () => {
      const tmp = this.state.textAId;
      this.state.textAId = this.state.textBId;
      this.state.textBId = tmp;
      this.render();
    });

    document.querySelectorAll('[data-tc-cat]').forEach(btn => {
      btn.addEventListener('click', (e) => {
        this.state.category = e.currentTarget.getAttribute('data-tc-cat');
        this.state.showAll = false;
        this.render();
      });
    });

    document.getElementById('tcSortBy')?.addEventListener('change', (e) => {
      this.state.sortBy = e.target.value;
      this.render();
    });

    const nameFilter = document.getElementById('tcNameFilter');
    if (nameFilter) {
      nameFilter.addEventListener('input', (e) => {
        this.state.nameFilter = e.target.value;
        this.render();
        const newInput = document.getElementById('tcNameFilter');
        if (newInput) {
          newInput.focus();
          newInput.setSelectionRange(newInput.value.length, newInput.value.length);
        }
      });
    }

    document.getElementById('tcShowAll')?.addEventListener('change', (e) => {
      this.state.showAll = e.target.checked;
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
