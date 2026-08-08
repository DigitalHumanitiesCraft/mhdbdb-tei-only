/**
 * MHDBDB Playground - Arthurische Pferde (Beta)
 *
 * Luise Boreks exemplarische semantische Auszeichnung der Pferde in fünf
 * arthurischen Werken (WH, PZ, ER, IW, TR): 13 Pferde, 346 Belegstellen mit
 * Ereignissen, Eigenschaften, Ausrüstung, Besitzern und Reitern.
 * Datenquelle: data/horses-index.json.gz, gebaut von
 * scripts/ingest/horses/03-build-index.py.
 *
 * Lazy-Load per fetch+pako beim ersten show(), wie beim Naming-Explorer und
 * aus demselben Grund bewusst KEIN IndexedDB-Cache: der Index ist klein
 * (11 KB gz), und ohne Cache entfällt der Versions-Bump-Kanal (#94).
 *
 * Zwei Angaben pro Beleg, und das ist Absicht: `citation` ist Boreks
 * Stellenangabe im Wortlaut, `target` unser aufgelöster Vers. Für acht Verse
 * fallen sie auseinander, weil unser Parzival Leitzmann (ATB 12) folgt und
 * Borek gar keine Ausgabe nennt. Sichtbar ist immer Boreks Angabe, das ist
 * die zitierfähige Referenz; der Link benutzt `target`. Siehe
 * DATA-MODEL.md → Horses Index.
 *
 * Der Sprung geht über ?verseId=<Wort-ID>, nicht über ?verse=<l n>: im
 * Parzival zählt @n nur innerhalb des Dreißigers, im Willehalm existiert die
 * Abschnittsnummer im TEI überhaupt nicht.
 *
 * Issue: #193
 */

import { getNavigationEpoch } from '../core/router.js';

const DEFAULT_STATE = Object.freeze({
  horseId: '',
  eventType: 'all'
});

// Boreks Typwerte, ausgeschrieben. Sie stehen im Datensatz als englische
// Kürzel; die Ansicht ist deutsch wie der Rest der Seite.
const EVENT_LABEL = {
  intro: 'Einführung',
  care: 'Pflege',
  combat: 'Kampf',
  loss: 'Verlust',
  trans: 'Übergabe',
  communication: 'Kommunikation',
  recognition: 'Wiedererkennen',
  gift: 'Geschenk'
};

const TRAIT_LABEL = { color: 'Farbe', quality: 'Qualität', marking: 'Abzeichen' };
const OBJECT_LABEL = { gear: 'Ausrüstung', armor: 'Rüstung', deco: 'Zierrat', weapon: 'Waffe' };
const ROLE_LABEL = { owner: 'Besitzer', rider: 'Reiter', claimant: 'Anspruch' };

const WORK_LABEL = {
  WH: 'Willehalm', PZ: 'Parzival', ER: 'Erec', IW: 'Iwein', TR: 'Tristan'
};

// Belege, deren Stellenangabe nicht deckungsgleich mit unserer Zählung ist.
// Der Hinweis gehört an den einzelnen Beleg, nicht in eine Fußnote: er
// betrifft acht von 346 und wäre pauschal formuliert irreführend.
const MATCH_NOTE = {
  shifted: 'Die zitierte Ausgabe zählt hier abweichend; der Wortlaut belegt die Stelle.',
  distant: 'Die zitierte Ausgabe zählt hier deutlich abweichend; der Wortlaut belegt die Stelle.',
  unresolved: 'Diese Stelle konnte im Korpus nicht sicher zugeordnet werden.'
};

export class HorsesExplorer {
  constructor(basePath = '../data') {
    this.basePath = basePath;
    this.index = null;
    this.loadError = null;
    this.state = { ...DEFAULT_STATE };
  }

  async show() {
    const container = document.getElementById('resultsContainer');
    if (!container) return;

    if (!this.index && !this.loadError) {
      container.innerHTML = '<div class="rounded-2xl border border-slate-200 bg-white p-8 text-center text-sm text-slate-500">Lade arthurische Pferde ...</div>';
      const myEpoch = getNavigationEpoch();
      await this.loadIndex();
      // Navigiert der User während des Erst-Loads weg, nicht rendern —
      // sonst überschreibt der fertige Index die andere View (#159).
      if (getNavigationEpoch() !== myEpoch) return;
    }
    this.render();
  }

  async loadIndex() {
    try {
      const response = await fetch(`${this.basePath}/horses-index.json.gz`);
      if (!response.ok) throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      const compressed = await response.arrayBuffer();
      const json = pako.ungzip(new Uint8Array(compressed), { to: 'string' });
      this.index = JSON.parse(json);
      this.loadError = null;
      console.log(`[HorsesExplorer] Index geladen: ${this.index.horses.length} Pferde, ${this.index.attestations.length} Belege`);
    } catch (error) {
      console.error('[HorsesExplorer] Index konnte nicht geladen werden:', error);
      this.loadError = error.message;
    }
  }

  getHorse(id) {
    if (!id || !this.index) return null;
    return this.index.horses.find(h => h.id === id) || null;
  }

  /** Belege des gewählten Pferds, in Textreihenfolge (so gebaut). */
  getAttestations(horseId) {
    if (!horseId || !this.index) return [];
    return this.index.attestations.filter(a => a.horse === horseId);
  }

  /** Wie oft kommt jeder Ereignistyp beim gewählten Pferd vor? */
  countEvents(attestations) {
    const counts = new Map();
    for (const a of attestations) {
      for (const type of new Set((a.events || []).map(e => e.type))) {
        counts.set(type, (counts.get(type) || 0) + 1);
      }
    }
    return counts;
  }

  horseLabel(horse) {
    if (horse.named) return horse.name;
    return `ungenanntes Pferd (${WORK_LABEL[horse.works[0]] || horse.works[0]})`;
  }

  render() {
    const container = document.getElementById('resultsContainer');
    if (!container) return;

    if (this.loadError) {
      container.innerHTML = `
        <div class="rounded-2xl border border-red-200 bg-red-50 p-4 text-sm text-red-700">
          Die arthurischen Pferde konnten nicht geladen werden: ${escapeHtml(this.loadError)}
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
    const horses = this.index?.horses || [];
    const options = horses.map(h => {
      const works = h.works.map(w => WORK_LABEL[w] || w).join(', ');
      return `<option value="${escapeAttr(h.id)}"${h.id === this.state.horseId ? ' selected' : ''}>${escapeHtml(this.horseLabel(h))} - ${escapeHtml(works)} (${h.attestations.toLocaleString('de-DE')} Belege)</option>`;
    }).join('');

    return `
      <div class="rounded-2xl border border-slate-200 bg-slate-50/70 p-4 space-y-3">
        <h3 class="flex items-center gap-2 text-sm font-semibold uppercase tracking-wide text-slate-500">
          Arthurische Pferde
          <span class="rounded bg-amber-100 px-1.5 py-0.5 text-[10px] font-semibold uppercase tracking-wide text-amber-800">Beta</span>
        </h3>
        <p class="text-xs text-slate-600">
          Wie erzählen die arthurischen Romane von Pferden? Der Datensatz zeichnet für 13 Pferde aus fünf Werken aus,
          was ihnen widerfährt (Kampf, Pflege, Verlust, Übergabe), wie sie aussehen, was sie tragen und wer sie besitzt oder reitet.
          Aus der exemplarischen Auszeichnung <strong>von Luise Borek (TU Darmstadt).</strong>
        </p>
        <label class="block">
          <span class="text-xs font-medium text-slate-600">Pferd</span>
          <select id="hxHorseSelect" class="mt-1 w-full rounded-lg border border-slate-200 bg-white px-3 py-2 text-sm focus:border-brand-400 focus:outline-none">
            <option value="">Pferd wählen ...</option>
            ${options}
          </select>
        </label>
        <p class="text-[11px] text-slate-500">
          Angegeben ist immer Boreks Stellenangabe. Sie folgt einer anderen Textgrundlage als unser Korpus:
          bei acht der 346 Belege weicht die Verszählung ab, dort ist die Stelle über den Wortlaut zugeordnet und der Beleg entsprechend markiert.
        </p>
      </div>
    `;
  }

  renderBody() {
    const horse = this.getHorse(this.state.horseId);
    if (!horse) {
      const total = this.index?.attestations.length || 0;
      return `<div class="rounded-2xl border border-dashed border-slate-200 bg-white p-8 text-center text-sm text-slate-500">${total.toLocaleString('de-DE')} Belegstellen zu ${(this.index?.horses.length || 0)} Pferden. Bitte ein Pferd auswählen.</div>`;
    }

    const all = this.getAttestations(horse.id);
    const counts = this.countEvents(all);
    const visible = this.state.eventType === 'all'
      ? all
      : all.filter(a => (a.events || []).some(e => e.type === this.state.eventType));

    return this.renderSummary(horse, all)
      + this.renderEventTabs(counts, all.length)
      + this.renderAttestations(visible, horse);
  }

  renderSummary(horse, attestations) {
    const distinct = (key, field) => {
      const set = new Set();
      for (const a of attestations) for (const x of (a[key] || [])) if (x[field]) set.add(x[field]);
      return set;
    };
    const traits = distinct('traits', 'type');
    const objects = distinct('objects', 'type');
    const persons = new Set();
    for (const a of attestations) {
      for (const p of (a.persons || [])) for (const r of (p.ref || [])) persons.add(r);
    }

    const cell = (label, value, sub) => `
      <div>
        <div class="text-xs uppercase tracking-wide text-slate-500">${label}</div>
        <div class="font-semibold text-brand-700">${value}</div>
        ${sub ? `<div class="text-xs text-slate-500">${sub}</div>` : ''}
      </div>
    `;

    const variants = horse.variants.length
      ? `Schreibvarianten: ${horse.variants.map(escapeHtml).join(', ')}`
      : '';

    return `
      <div class="rounded-2xl border border-slate-200 bg-white p-4">
        <div class="grid gap-4 sm:grid-cols-4">
          ${cell('Belegstellen', attestations.length.toLocaleString('de-DE'),
            horse.works.map(w => escapeHtml(WORK_LABEL[w] || w)).join(', '))}
          ${cell('Eigenschaften', [...traits].map(t => escapeHtml(TRAIT_LABEL[t] || t)).join(', ') || '&ndash;')}
          ${cell('Ausrüstung', [...objects].map(t => escapeHtml(OBJECT_LABEL[t] || t)).join(', ') || '&ndash;')}
          ${cell('Figuren', [...persons].map(escapeHtml).join(', ') || '&ndash;')}
        </div>
        ${variants ? `<div class="mt-3 border-t border-slate-100 pt-2 text-xs text-slate-500">${variants}</div>` : ''}
      </div>
    `;
  }

  renderEventTabs(counts, total) {
    const tab = (key, label, count) => {
      const active = this.state.eventType === key;
      return `
        <button type="button" data-hx-event="${escapeAttr(key)}"
          class="rounded-full border px-3 py-1 text-xs font-medium transition ${active
            ? 'border-brand-400 bg-brand-50 text-brand-700'
            : 'border-slate-200 bg-white text-slate-600 hover:border-brand-300'}">
          ${escapeHtml(label)} <span class="text-slate-400">${count.toLocaleString('de-DE')}</span>
        </button>
      `;
    };

    const sorted = [...counts.entries()].sort((a, b) => b[1] - a[1] || a[0].localeCompare(b[0]));
    if (!sorted.length) return '';
    return `
      <div class="flex flex-wrap gap-2">
        ${tab('all', 'Alle Belege', total)}
        ${sorted.map(([type, n]) => tab(type, EVENT_LABEL[type] || type, n)).join('')}
      </div>
    `;
  }

  renderAttestations(attestations, horse) {
    if (!attestations.length) {
      return '<div class="rounded-2xl border border-dashed border-slate-200 bg-white p-8 text-center text-sm text-slate-500">Keine Belege für diesen Ereignistyp.</div>';
    }

    const rows = attestations.map(a => this.renderAttestation(a)).join('');
    return `
      <div class="overflow-hidden rounded-2xl border border-slate-200 bg-white">
        <table class="w-full text-sm">
          <thead class="bg-slate-50 text-xs uppercase tracking-wide text-slate-500">
            <tr>
              <th class="px-4 py-2 text-left font-medium">Stelle</th>
              <th class="px-4 py-2 text-left font-medium">Wortlaut</th>
              <th class="px-4 py-2 text-left font-medium">Auszeichnung</th>
            </tr>
          </thead>
          <tbody>${rows}</tbody>
        </table>
      </div>
    `;
  }

  renderAttestation(a) {
    const label = `${escapeHtml(a.citation)}`;
    const stelle = a.target
      ? `<a href="../korpus.html?textId=${encodeURIComponent(a.work)}&verseId=${encodeURIComponent(a.target)}"
             target="_blank" rel="noopener" class="font-mono text-xs text-brand-700 hover:underline"
             title="Stelle in der Leseansicht öffnen">${label}</a>`
      : `<span class="font-mono text-xs text-slate-500">${label}</span>`;

    const note = a.match && a.match !== 'exact'
      ? `<span class="ml-1 cursor-help text-amber-600" title="${escapeAttr(MATCH_NOTE[a.match] || '')}">*</span>`
      : '';

    const badge = (text, cls) =>
      `<span class="mr-1 inline-block rounded border px-1.5 py-0.5 text-[10px] ${cls}">${escapeHtml(text)}</span>`;

    const badges = [
      ...(a.events || []).map(e => badge(EVENT_LABEL[e.type] || e.type, 'border-brand-200 bg-brand-50 text-brand-700')),
      ...(a.traits || []).map(t => badge(`${TRAIT_LABEL[t.type] || t.type}: ${t.text}`, 'border-rose-200 bg-rose-50 text-rose-700')),
      ...(a.objects || []).map(o => badge(`${OBJECT_LABEL[o.type] || o.type}: ${o.text}`, 'border-amber-200 bg-amber-50 text-amber-800')),
      ...(a.persons || []).filter(p => p.role).map(p => badge(`${ROLE_LABEL[p.role] || p.role}: ${p.text}`, 'border-slate-200 bg-slate-50 text-slate-600')),
      ...(a.designations || []).map(d => badge(d.text, 'border-slate-200 bg-white text-slate-500'))
    ].join('');

    return `
      <tr class="border-t border-slate-100 align-top">
        <td class="whitespace-nowrap px-4 py-2">${stelle}${note}</td>
        <td class="px-4 py-2 text-slate-700">${escapeHtml(a.text)}</td>
        <td class="px-4 py-2">${badges || '<span class="text-xs text-slate-400">&ndash;</span>'}</td>
      </tr>
    `;
  }

  renderAttribution() {
    const s = this.index?.source || {};
    return `
      <div class="rounded-2xl border border-slate-200 bg-slate-50/70 p-4 text-xs text-slate-600 space-y-1">
        <div class="font-semibold text-slate-700">Arthurische Pferde nach Luise Borek</div>
        <div>
          Borek, L. (2023). ${escapeHtml(s.title || 'Exemplarische Auszeichnung arthurischer Pferde')}. TU Darmstadt.
          <a href="${escapeAttr(s.url || '')}" target="_blank" rel="noopener" class="text-brand-700 hover:underline">${escapeHtml(s.handle || '')}</a>
        </div>
        <div>
          Lizenz: ${escapeHtml(s.licence || 'CC0 1.0')} |
          Werkabdeckung: Willehalm, Parzival, Erec, Iwein, Tristan |
          Belegstellen den Versen des MHDBDB-Korpus über den Wortlaut zugeordnet
        </div>
      </div>
    `;
  }

  attachHandlers() {
    document.getElementById('hxHorseSelect')?.addEventListener('change', (e) => {
      this.state.horseId = e.target.value;
      this.state.eventType = 'all';
      this.render();
    });

    document.querySelectorAll('[data-hx-event]').forEach(btn => {
      btn.addEventListener('click', (e) => {
        this.state.eventType = e.currentTarget.getAttribute('data-hx-event');
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

function escapeAttr(s) {
  return escapeHtml(s);
}
