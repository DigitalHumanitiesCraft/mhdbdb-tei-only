/**
 * MHDBDB Playground - Erweiterte Figurenbezeichnungen (Beta)
 *
 * Kuratierte Figurenbezeichnungen (Eigennamen, Antonomasien, Epitheta) aus
 * Linda Beutel-Thurows Naming-analysis für 4 Werke (ENE, IW, ROL, TRO).
 * Datenquelle: data/naming-index.json.gz, gebaut von
 * scripts/ingest/naming/01-fetch-and-build-index.py.
 *
 * Lazy-Load per fetch+pako beim ersten show(); bewusst KEIN IndexedDB-Cache:
 * der Index ist klein (~110 KB gz) und ohne Cache entfällt der
 * Versions-Bump-Kanal, der bei corpus-/authority-index schiefgehen kann (#94).
 *
 * Die Verszählung folgt Lindas Editionsgrundlagen. Bei ROL und TRO ist sie
 * mit der MHDBDB-TEI-Zählung deckungsgleich (Linda, #59-Kommentar
 * 2026-06-11; TRO-Stichprobe 4/4 verifiziert) — dort verlinken die
 * Belegstellen per ?textId=<SIG>&verse=<n> in die Leseansicht. ENE und IW
 * weichen ab (andere Editionen, Dezimal-Verse) und bleiben link-los.
 *
 * Issue: #59
 */

import { TextNormalizer } from '../../../../assets/js/lib/text-normalizer.js';

const DEFAULT_STATE = Object.freeze({
  workSigle: '',
  figure: '',
  category: 'all',       // 'all' | 'eig' | 'ant' | 'epi'
  nameFilter: ''
});

const CATEGORY_META = {
  eig: { label: 'Eigenname',   badge: 'border-brand-200 bg-brand-50 text-brand-700' },
  ant: { label: 'Antonomasie', badge: 'border-amber-200 bg-amber-50 text-amber-800' },
  epi: { label: 'Epitheton',   badge: 'border-rose-200 bg-rose-50 text-rose-700' }
};

const EVIDENCE_LIMIT = 50;

// Werke, deren Edition-Verszählung der MHDBDB-<l n>-Zählung entspricht —
// nur dort sind Vers-Deep-Links in den Reader korrekt (siehe Header-Kommentar).
const READER_LINK_SIGLES = new Set(['ROL', 'TRO']);

export class NamingExplorer {
  constructor(basePath = '../data') {
    this.basePath = basePath;
    this.index = null;
    this.loadError = null;
    this.state = { ...DEFAULT_STATE };
    this.expandedTerms = new Set();
  }

  async show() {
    const container = document.getElementById('resultsContainer');
    if (!container) return;

    if (!this.index && !this.loadError) {
      container.innerHTML = '<div class="rounded-2xl border border-slate-200 bg-white p-8 text-center text-sm text-slate-500">Lade Figurenbezeichnungen ...</div>';
      await this.loadIndex();
    }
    this.render();
  }

  async loadIndex() {
    try {
      const response = await fetch(`${this.basePath}/naming-index.json.gz`);
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }
      const compressed = await response.arrayBuffer();
      const json = pako.ungzip(new Uint8Array(compressed), { to: 'string' });
      this.index = JSON.parse(json);
      this.loadError = null;
      console.log(`[NamingExplorer] Index geladen: ${this.index.works.length} Werke (Quelle: ${this.index.source?.repo})`);
    } catch (error) {
      console.error('[NamingExplorer] Index konnte nicht geladen werden:', error);
      this.loadError = error.message;
    }
  }

  getWork(sigle) {
    if (!sigle || !this.index) return null;
    return this.index.works.find(w => w.sigle === sigle) || null;
  }

  /** Figuren des Werks als [{name, count}], nach Belegzahl absteigend. */
  getFigures(work) {
    if (!work) return [];
    return Object.entries(work.figures)
      .map(([name, records]) => ({ name, count: records.length }))
      .sort((a, b) => b.count - a.count || a.name.localeCompare(b.name, 'de'));
  }

  /**
   * Aggregation der Records einer Figur zu Termen:
   * [{term, cat, count, evidence: [{v, ph, who, by}]}]
   */
  computeTerms(records) {
    const map = new Map();
    for (const record of records) {
      for (const cat of ['eig', 'ant', 'epi']) {
        for (const term of (record[cat] || [])) {
          const key = `${cat}|${term}`;
          if (!map.has(key)) {
            map.set(key, { term, cat, count: 0, evidence: [] });
          }
          const entry = map.get(key);
          entry.count += 1;
          entry.evidence.push({ v: record.v, ph: record.ph, who: record.who, by: record.by });
        }
      }
    }
    return [...map.values()].sort((a, b) => b.count - a.count || a.term.localeCompare(b.term, 'de'));
  }

  render() {
    const container = document.getElementById('resultsContainer');
    if (!container) return;

    if (this.loadError) {
      container.innerHTML = `
        <div class="rounded-2xl border border-red-200 bg-red-50 p-4 text-sm text-red-700">
          Figurenbezeichnungen konnten nicht geladen werden: ${escapeHtml(this.loadError)}
        </div>
      `;
      return;
    }

    container.innerHTML = `
      <div class="space-y-4">
        ${this.renderForm()}
        ${this.renderBody()}
        ${this.renderAttribution()}
      </div>
    `;
    this.attachHandlers();
  }

  renderForm() {
    const works = this.index?.works || [];
    const workOptions = works.map(w =>
      `<option value="${escapeAttr(w.sigle)}"${w.sigle === this.state.workSigle ? ' selected' : ''}>${escapeHtml(w.sigle)} - ${escapeHtml(w.bookName)}</option>`
    ).join('');

    const work = this.getWork(this.state.workSigle);
    const figures = this.getFigures(work);
    const figureOptions = figures.map(f =>
      `<option value="${escapeAttr(f.name)}"${f.name === this.state.figure ? ' selected' : ''}>${escapeHtml(f.name)} (${f.count.toLocaleString('de-DE')} Belege)</option>`
    ).join('');

    return `
      <div class="rounded-2xl border border-slate-200 bg-slate-50/70 p-4 space-y-3">
        <h3 class="flex items-center gap-2 text-sm font-semibold uppercase tracking-wide text-slate-500">
          Erweiterte Figurenbezeichnungen
          <span class="rounded bg-amber-100 px-1.5 py-0.5 text-[10px] font-semibold uppercase tracking-wide text-amber-800">Beta</span>
        </h3>
        <p class="text-xs text-slate-600">
          Kuratierte Bezeichnungspraktiken jenseits des Eigennamens: Wie wird eine Figur benannt, umschrieben (Antonomasie) und charakterisiert (Epitheton)?
          Verfügbar für die vier Werke mit kuratierten Daten aus dem Dissertationsprojekt Naming-analysis.
        </p>
        <div class="grid gap-3 sm:grid-cols-2">
          <label class="block">
            <span class="text-xs font-medium text-slate-600">Werk</span>
            <select id="neWorkSelect" class="mt-1 w-full rounded-lg border border-slate-200 bg-white px-3 py-2 text-sm focus:border-brand-400 focus:outline-none">
              <option value="">Werk wählen ...</option>
              ${workOptions}
            </select>
          </label>
          <label class="block">
            <span class="text-xs font-medium text-slate-600">Figur (nach Belegzahl)</span>
            <select id="neFigureSelect" class="mt-1 w-full rounded-lg border border-slate-200 bg-white px-3 py-2 text-sm focus:border-brand-400 focus:outline-none"${work ? '' : ' disabled'}>
              <option value="">Figur wählen ...</option>
              ${figureOptions}
            </select>
          </label>
        </div>
        <p class="text-[11px] text-slate-500">
          Versangaben folgen den Editionsgrundlagen der Naming-analysis-Erhebung. Bei ROL und TRO ist die Zählung mit der MHDBDB deckungsgleich; dort führen die Versangaben direkt in die Leseansicht. Bei ENE und IW kann die Zählung abweichen.
        </p>
      </div>
    `;
  }

  renderBody() {
    const work = this.getWork(this.state.workSigle);
    if (!work) {
      return '<div class="rounded-2xl border border-dashed border-slate-200 bg-white p-8 text-center text-sm text-slate-500">Bitte ein Werk auswählen.</div>';
    }
    if (!this.state.figure) {
      const figureCount = Object.keys(work.figures).length;
      return `<div class="rounded-2xl border border-dashed border-slate-200 bg-white p-8 text-center text-sm text-slate-500">${escapeHtml(work.bookName)}: ${figureCount.toLocaleString('de-DE')} Figuren mit kuratierten Bezeichnungen. Bitte eine Figur auswählen.</div>`;
    }

    const records = work.figures[this.state.figure];
    if (!records) {
      return '<div class="rounded-2xl border border-amber-200 bg-amber-50 p-4 text-sm text-amber-800">Die gewählte Figur wurde im Werk nicht gefunden.</div>';
    }

    const terms = this.computeTerms(records);
    const counts = { all: terms.length, eig: 0, ant: 0, epi: 0 };
    for (const t of terms) counts[t.cat] += 1;

    const summary = this.renderSummary(work, records, terms);
    const tabs = this.renderCategoryTabs(counts);

    let visible = this.state.category === 'all' ? terms : terms.filter(t => t.cat === this.state.category);
    const filter = this.state.nameFilter.trim();
    if (filter) {
      // MHG-normalisiert, damit "riter" auch "rîter"/"rîtaere" findet
      visible = visible.filter(t => TextNormalizer.matchesNormalized(t.term, filter));
    }

    const controls = this.renderControls(visible.length);
    const table = this.renderTermTable(visible);

    return summary + tabs + controls + table;
  }

  renderSummary(work, records, terms) {
    const occurrences = { eig: 0, ant: 0, epi: 0 };
    for (const t of terms) occurrences[t.cat] += t.count;

    const plural = { eig: 'Eigennamen', ant: 'Antonomasien', epi: 'Epitheta' };
    const cells = ['eig', 'ant', 'epi'].map(cat => {
      const distinct = terms.filter(t => t.cat === cat).length;
      return `
        <div>
          <div class="text-xs uppercase tracking-wide text-slate-500">${plural[cat]}</div>
          <div class="font-semibold text-brand-700">${distinct.toLocaleString('de-DE')} <span class="font-normal text-slate-500">${distinct === 1 ? 'Term' : 'Terme'}</span></div>
          <div class="text-xs text-slate-500">${occurrences[cat].toLocaleString('de-DE')} Vorkommen</div>
        </div>
      `;
    }).join('');

    return `
      <div class="rounded-2xl border border-slate-200 bg-white p-4">
        <div class="mb-3">
          <div class="text-xs uppercase tracking-wide text-slate-500">${escapeHtml(work.sigle)} - ${escapeHtml(work.bookName)}</div>
          <div class="text-lg font-semibold text-slate-800">${escapeHtml(this.state.figure)}</div>
          <div class="text-xs text-slate-500">${records.length.toLocaleString('de-DE')} kuratierte Belegstellen</div>
        </div>
        <div class="grid gap-2 sm:grid-cols-3 text-sm">${cells}</div>
      </div>
    `;
  }

  renderCategoryTabs(counts) {
    const cats = [
      { key: 'all', label: 'Alle' },
      { key: 'eig', label: 'Eigennamen' },
      { key: 'ant', label: 'Antonomasien' },
      { key: 'epi', label: 'Epitheta' }
    ];
    const buttons = cats.map(c => {
      const active = c.key === this.state.category;
      const cls = active
        ? 'border-brand-400 bg-brand-50 text-brand-700'
        : 'border-slate-200 bg-white text-slate-600 hover:border-slate-400';
      return `<button type="button" data-ne-cat="${c.key}" class="rounded-lg border px-3 py-1.5 text-sm transition ${cls}">${c.label}<span class="ml-2 rounded bg-slate-100 px-1.5 py-0.5 text-xs font-mono text-slate-600">${counts[c.key].toLocaleString('de-DE')}</span></button>`;
    }).join('');
    return `<div class="flex flex-wrap gap-2">${buttons}</div>`;
  }

  renderControls(visibleCount) {
    return `
      <div class="flex flex-wrap items-center gap-3 rounded-xl border border-slate-200 bg-slate-50/60 p-3 text-sm">
        <label class="flex items-center gap-2 flex-1 min-w-[200px]">
          <span class="text-xs font-medium text-slate-600">Term-Filter</span>
          <input id="neNameFilter" type="text" autocomplete="off"
            value="${escapeAttr(this.state.nameFilter)}"
            placeholder="z.B. tore (findet tôre)"
            class="w-full rounded-lg border border-slate-200 bg-white px-2 py-1 text-xs focus:border-brand-400 focus:outline-none" />
        </label>
        <span class="text-xs text-slate-500">${visibleCount.toLocaleString('de-DE')} Terme</span>
      </div>
    `;
  }

  renderTermTable(terms) {
    if (terms.length === 0) {
      return '<div class="rounded-2xl border border-dashed border-slate-200 bg-white p-6 text-center text-sm text-slate-500">Keine Terme in dieser Kategorie (mit aktuellem Filter).</div>';
    }

    const rows = terms.map(t => {
      const key = `${t.cat}|${t.term}`;
      const expanded = this.expandedTerms.has(key);
      const meta = CATEGORY_META[t.cat];
      const chevron = expanded
        ? '<svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"></path></svg>'
        : '<svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"></path></svg>';

      const mainRow = `
        <tr class="border-b border-slate-100 hover:bg-slate-50 cursor-pointer" data-ne-term="${escapeAttr(key)}">
          <td class="px-3 py-1.5">
            <span class="inline-flex items-center gap-1.5 font-medium text-slate-800">${chevron}${escapeHtml(t.term)}</span>
          </td>
          <td class="px-3 py-1.5"><span class="rounded border px-1.5 py-0.5 text-[10px] font-semibold uppercase tracking-wide ${meta.badge}">${meta.label}</span></td>
          <td class="px-3 py-1.5 text-right tabular-nums text-slate-600">${t.count.toLocaleString('de-DE')}</td>
        </tr>
      `;

      if (!expanded) return mainRow;
      return mainRow + this.renderEvidenceRow(t);
    }).join('');

    return `
      <div class="overflow-x-auto rounded-2xl border border-slate-200 bg-white">
        <table class="w-full text-sm">
          <thead class="bg-slate-50">
            <tr>
              <th class="px-3 py-2 text-left text-xs font-semibold text-slate-600">Bezeichnung</th>
              <th class="px-3 py-2 text-left text-xs font-semibold text-slate-600">Kategorie</th>
              <th class="px-3 py-2 text-right text-xs font-semibold text-slate-600">Häufigkeit</th>
            </tr>
          </thead>
          <tbody>${rows}</tbody>
        </table>
      </div>
    `;
  }

  renderEvidenceRow(t) {
    // Deep-Link nur bei deckungsgleicher Verszählung und ganzzahligem Vers
    // (Dezimal-Verse wie 17.02 existieren in ROL/TRO nicht, Guard bleibt).
    const linkable = READER_LINK_SIGLES.has(this.state.workSigle);
    const visible = t.evidence.slice(0, EVIDENCE_LIMIT);
    const items = visible.map(e => {
      let speaker;
      if (e.who === 'fig') {
        speaker = e.by ? `Figurenrede: ${escapeHtml(e.by)}` : 'Figurenrede';
      } else if (e.who === 'self') {
        speaker = 'Selbstnennung';
      } else {
        speaker = 'Erzähler';
      }
      const verse = (linkable && /^\d+$/.test(e.v))
        ? `<a href="../korpus.html?textId=${encodeURIComponent(this.state.workSigle)}&verse=${encodeURIComponent(e.v)}" target="_blank" rel="noopener" class="text-brand-700 hover:underline" title="Vers ${escapeAttr(e.v)} in der Leseansicht öffnen">V. ${escapeHtml(e.v)}</a>`
        : `<span title="Versangabe der Editionsgrundlage">V. ${escapeHtml(e.v)}</span>`;
      return `
        <div class="flex items-baseline gap-3 border-b border-slate-100 py-1 last:border-b-0">
          <span class="w-16 flex-shrink-0 text-right font-mono text-xs text-slate-500">${verse}</span>
          <span class="flex-1 text-slate-700">${escapeHtml(e.ph)}</span>
          <span class="flex-shrink-0 text-xs text-slate-400">${speaker}</span>
        </div>
      `;
    }).join('');

    const truncated = t.evidence.length > EVIDENCE_LIMIT
      ? `<div class="pt-1 text-center text-xs text-slate-400">Zeige ${EVIDENCE_LIMIT} von ${t.evidence.length.toLocaleString('de-DE')} Belegstellen.</div>`
      : '';

    return `
      <tr class="border-b border-slate-100 bg-slate-50/50">
        <td colspan="3" class="px-6 py-2 text-xs">${items}${truncated}</td>
      </tr>
    `;
  }

  renderAttribution() {
    return `
      <div class="rounded-2xl border border-slate-200 bg-slate-50/70 p-4 text-xs text-slate-600 space-y-1">
        <div class="font-semibold text-slate-700">Naming-analysis nach Linda Beutel-Thurow</div>
        <div>
          Beutel-Thurow, L. (2026). Naming-analysis (v0.1.0-beta).
          <a href="https://doi.org/10.5281/zenodo.18770138" target="_blank" rel="noopener" class="text-brand-700 hover:underline">https://doi.org/10.5281/zenodo.18770138</a>
        </div>
        <div>
          Lizenz: CC BY-NC-SA 4.0 |
          <a href="https://github.com/lindabeutel/Naming-analysis" target="_blank" rel="noopener" class="text-brand-700 hover:underline">github.com/lindabeutel/Naming-analysis</a>
        </div>
      </div>
    `;
  }

  attachHandlers() {
    document.getElementById('neWorkSelect')?.addEventListener('change', (e) => {
      this.state.workSigle = e.target.value;
      this.state.figure = '';
      this.state.category = 'all';
      this.state.nameFilter = '';
      this.expandedTerms.clear();
      this.render();
    });

    document.getElementById('neFigureSelect')?.addEventListener('change', (e) => {
      this.state.figure = e.target.value;
      this.state.category = 'all';
      this.state.nameFilter = '';
      this.expandedTerms.clear();
      this.render();
    });

    document.querySelectorAll('[data-ne-cat]').forEach(btn => {
      btn.addEventListener('click', (e) => {
        this.state.category = e.currentTarget.getAttribute('data-ne-cat');
        this.render();
      });
    });

    document.querySelectorAll('[data-ne-term]').forEach(row => {
      row.addEventListener('click', (e) => {
        const key = e.currentTarget.getAttribute('data-ne-term');
        if (this.expandedTerms.has(key)) {
          this.expandedTerms.delete(key);
        } else {
          this.expandedTerms.add(key);
        }
        this.render();
      });
    });

    const nameFilter = document.getElementById('neNameFilter');
    if (nameFilter) {
      nameFilter.addEventListener('input', (e) => {
        this.state.nameFilter = e.target.value;
        this.render();
        const newInput = document.getElementById('neNameFilter');
        if (newInput) {
          newInput.focus();
          newInput.setSelectionRange(newInput.value.length, newInput.value.length);
        }
      });
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
