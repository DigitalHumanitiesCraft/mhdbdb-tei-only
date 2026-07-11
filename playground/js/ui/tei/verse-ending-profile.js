/**
 * MHDBDB Playground - Versendings-Profil
 *
 * Top-N häufigste Versende-Lemmata pro Gesamtkorpus, Autor oder Text
 * (#106 Punkt 2). Datenbasis sind die lineEnds[]-Arrays des Corpus-Index
 * v4.1.0+ (#47.3): text.words[lineEnds[i]] ist das Lemma am Ende von Vers i.
 * Kein neuer Build-Schritt. Prosa-Texte (leere lineEnds) werden übersprungen.
 *
 * Die Spalte „Reim-Druck" setzt die Versende-Belege eines Lemmas ins
 * Verhältnis zu allen seinen Vorkommen im gewählten Scope (#106 Punkt 3:
 * ein Lemma mit hohem Ende-Anteil ist stark reimgetrieben, eines mit
 * niedrigem eher semantisch motiviert).
 */

import { buildTextLabelDisambiguator } from '../core/ui-helpers.js';
import { FUNCTION_WORD_POS } from './word-frequency.js';

const TOP_N_OPTIONS = [20, 50, 100, 200];
const DEFAULT_TOP_N = 50;

export class VerseEndingProfileAnalyzer {
  /**
   * @param {() => Array} getCorpusTexts  thunk returning the current corpus
   *   texts array (same indirection as word-frequency.js).
   * @param {object} authorityData
   */
  constructor(getCorpusTexts, authorityData) {
    this.getCorpusTexts = getCorpusTexts;
    this.authorityData = authorityData;
    this._lemmaById = null;
    this._lastProfile = null;
    this.state = {
      scope: 'corpus',
      topN: DEFAULT_TOP_N,
      hideFunctionWords: false
    };
  }

  getLemmaById(id) {
    if (!this._lemmaById) {
      const lemmata = this.authorityData?.lemmata || [];
      this._lemmaById = new Map(lemmata.map(l => [l.id, l]));
    }
    return this._lemmaById.get(id);
  }

  // Nur Versdichtung zählt: Texte ohne <l>-Grenzen liefern keine Versenden.
  verseTexts() {
    return (this.getCorpusTexts() || []).filter(t => t.lineEnds && t.lineEnds.length > 0);
  }

  scopedTexts(scope) {
    const texts = this.verseTexts();
    if (scope === 'corpus') return texts;
    if (scope.startsWith('author:')) {
      const author = scope.slice('author:'.length);
      return texts.filter(t => (t.author || 'Unbekannt') === author);
    }
    return texts.filter(t => t.id === scope);
  }

  computeProfile(scope) {
    const texts = this.scopedTexts(scope);
    if (texts.length === 0) return null;

    const endCounts = new Map();   // lemmaId -> Belege am Versende
    const totalCounts = new Map(); // lemmaId -> alle Vorkommen im Scope
    let verseCount = 0;

    for (const text of texts) {
      verseCount += text.lineEnds.length;
      for (const endIdx of text.lineEnds) {
        const lemmaId = text.words[endIdx];
        if (!lemmaId) continue;
        endCounts.set(lemmaId, (endCounts.get(lemmaId) || 0) + 1);
      }
      for (const [lemmaId, positions] of Object.entries(text.lemmata || {})) {
        totalCounts.set(lemmaId, (totalCounts.get(lemmaId) || 0) + positions.length);
      }
    }

    let scopeLabel, scopeMeta;
    if (scope === 'corpus') {
      scopeLabel = 'Gesamtkorpus (Versdichtung)';
      scopeMeta = `${texts.length.toLocaleString('de-DE')} Vers-Texte`;
    } else if (scope.startsWith('author:')) {
      scopeLabel = scope.slice('author:'.length);
      scopeMeta = `${texts.length.toLocaleString('de-DE')} Vers-Text${texts.length === 1 ? '' : 'e'}`;
    } else {
      const t = texts[0];
      scopeLabel = t.title || t.id;
      scopeMeta = t.author ? `${t.id} • ${t.author}` : t.id;
    }

    return { endCounts, totalCounts, verseCount, scopeLabel, scopeMeta };
  }

  async show() {
    const texts = this.getCorpusTexts();
    if (!texts || texts.length === 0) {
      this.renderError('Korpus ist noch nicht geladen. Bitte einen Moment warten und Button erneut klicken.');
      return;
    }
    this._lastProfile = this.computeProfile(this.state.scope);
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
    const texts = [...this.verseTexts()].sort((a, b) =>
      (a.id || '').localeCompare(b.id || '', 'de')
    );
    const disambig = buildTextLabelDisambiguator(texts, this.authorityData?.works || []);

    // Autoren mit mindestens einem Vers-Text, alphabetisch
    const authors = [...new Set(texts.map(t => t.author || 'Unbekannt'))]
      .sort((a, b) => a.localeCompare(b, 'de'));

    const authorOptions = authors.map(a => {
      const val = `author:${a}`;
      return `<option value="${escapeHtml(val)}"${this.state.scope === val ? ' selected' : ''}>${escapeHtml(a)}</option>`;
    }).join('');
    const textOptions = texts.map(t => {
      const label = `${escapeHtml(t.id)}${t.title ? '-' + escapeHtml(t.title + (disambig.get(t.id) || '')) : ''}`;
      return `<option value="${escapeHtml(t.id)}"${this.state.scope === t.id ? ' selected' : ''}>${label}</option>`;
    }).join('');

    const scopeOptions = `
      <option value="corpus"${this.state.scope === 'corpus' ? ' selected' : ''}>Gesamtkorpus (${texts.length} Vers-Texte)</option>
      <optgroup label="Autor*in">${authorOptions}</optgroup>
      <optgroup label="Text">${textOptions}</optgroup>
    `;

    const topNOptions = TOP_N_OPTIONS
      .map(n => `<option value="${n}"${this.state.topN === n ? ' selected' : ''}>Top ${n}</option>`)
      .join('');

    return `
      <div class="rounded-2xl border border-slate-200 bg-slate-50/70 p-4">
        <h3 class="mb-3 text-sm font-semibold uppercase tracking-wide text-slate-500">Versendings-Profil</h3>
        <div class="grid gap-3 sm:grid-cols-2">
          <label class="block">
            <span class="text-xs font-medium text-slate-600">Korpus / Autor*in / Text</span>
            <select id="vepScope" class="mt-1 w-full rounded-lg border border-slate-200 bg-white px-3 py-2 text-sm focus:border-brand-400 focus:outline-none">${scopeOptions}</select>
          </label>
          <label class="block">
            <span class="text-xs font-medium text-slate-600">Anzahl</span>
            <select id="vepTopN" class="mt-1 w-full rounded-lg border border-slate-200 bg-white px-3 py-2 text-sm focus:border-brand-400 focus:outline-none">${topNOptions}</select>
          </label>
        </div>
        <label class="mt-3 flex items-center gap-2 text-sm text-slate-700 cursor-pointer">
          <input type="checkbox" id="vepHideFunc" ${this.state.hideFunctionWords ? 'checked' : ''} class="w-4 h-4 rounded border-slate-300 text-brand-600 focus:ring-brand-500" />
          <span>Funktionswörter ausblenden <span class="text-xs text-slate-500">(der/die/daz, ich/er/sie, in/zuo, und/oder, niht, hân/wesen, …)</span></span>
        </label>
        <p class="mt-3 text-xs text-slate-500">
          Zählt das Lemma am letzten Wort jedes Verses (<code>lineEnds[]</code>, Corpus-Index v4.1.0+).
          „Reim-Druck" = Anteil der Vorkommen dieses Lemmas, die am Versende stehen — hohe Werte deuten
          auf reimgetriebene Verwendung. Nur Versdichtung; Prosa-Texte werden übersprungen.
        </p>
      </div>
    `;
  }

  renderTable() {
    const data = this._lastProfile;
    if (!data) {
      return '<div class="rounded-2xl border border-dashed border-slate-200 bg-slate-50/70 p-6 text-center text-sm text-slate-500">Keine Daten für diese Auswahl (nur Versdichtung wird ausgewertet).</div>';
    }
    const { endCounts, totalCounts, verseCount, scopeLabel, scopeMeta } = data;

    const allEntries = Array.from(endCounts.entries()).map(([id, endCount]) => {
      const total = totalCounts.get(id) || endCount;
      return {
        id,
        endCount,
        shareOfVerses: verseCount > 0 ? (endCount / verseCount) * 100 : 0,
        rhymePressure: total > 0 ? (endCount / total) * 100 : 0
      };
    });
    const entries = this.state.hideFunctionWords
      ? allEntries.filter(e => {
          const l = this.getLemmaById(e.id);
          const tags = l?.posAll
            || (l?.pos ? String(l.pos).trim().split(/\s+/) : []);
          if (tags.length === 0) return true;
          return !tags.some(t => FUNCTION_WORD_POS.has(t));
        })
      : allEntries;
    entries.sort((a, b) => b.endCount - a.endCount);
    const top = entries.slice(0, this.state.topN);
    const hiddenCount = allEntries.length - entries.length;

    const rows = top.map((e, idx) => {
      const lemma = this.getLemmaById(e.id);
      const lemmaText = lemma ? lemma.lemma : e.id;
      const cleanId = e.id.replace(/^lemma_/, '');
      const posLabel = (lemma?.posAll || (lemma?.pos ? [lemma.pos] : [])).join(' ');
      const pos = posLabel
        ? `<span class="ml-2 rounded bg-slate-100 px-1.5 py-0.5 text-xs font-mono text-slate-600">${escapeHtml(posLabel)}</span>`
        : '';
      return `
        <tr class="border-t border-slate-100 hover:bg-brand-50/50">
          <td class="px-3 py-2 text-xs text-slate-500 tabular-nums">${idx + 1}</td>
          <td class="px-3 py-2">
            <a href="../lemma/?id=${escapeHtml(cleanId)}" target="_blank" rel="noopener" class="font-medium text-brand-700 hover:underline">${escapeHtml(lemmaText)}</a>
            ${pos}
          </td>
          <td class="px-3 py-2 text-right tabular-nums text-sm text-slate-700">${e.endCount.toLocaleString('de-DE')}</td>
          <td class="px-3 py-2 text-right tabular-nums text-sm text-slate-700">${e.shareOfVerses.toFixed(2)} %</td>
          <td class="px-3 py-2 text-right tabular-nums text-sm text-slate-700">${e.rhymePressure.toFixed(1)} %</td>
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
            <div>${endCounts.size.toLocaleString('de-DE')} verschiedene Versende-Lemmata${hiddenCount > 0 ? ` <span class="text-slate-400">(–${hiddenCount.toLocaleString('de-DE')} ausgeblendet)</span>` : ''}</div>
            <div>${verseCount.toLocaleString('de-DE')} Verse</div>
          </div>
        </header>
        <table class="w-full">
          <thead class="text-xs uppercase tracking-wide text-slate-500">
            <tr class="bg-white">
              <th class="w-12 px-3 py-2 text-left">#</th>
              <th class="px-3 py-2 text-left">Lemma</th>
              <th class="px-3 py-2 text-right">Versende-Belege</th>
              <th class="px-3 py-2 text-right">Anteil aller Versenden</th>
              <th class="px-3 py-2 text-right">Reim-Druck</th>
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
    const scopeEl = document.getElementById('vepScope');
    const topNEl = document.getElementById('vepTopN');
    const hideFuncEl = document.getElementById('vepHideFunc');

    scopeEl?.addEventListener('change', (e) => {
      this.state.scope = e.target.value;
      this._lastProfile = this.computeProfile(this.state.scope);
      this.render();
    });
    topNEl?.addEventListener('change', (e) => {
      this.state.topN = parseInt(e.target.value, 10) || DEFAULT_TOP_N;
      this.render();
    });
    hideFuncEl?.addEventListener('change', (e) => {
      this.state.hideFunctionWords = e.target.checked;
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
