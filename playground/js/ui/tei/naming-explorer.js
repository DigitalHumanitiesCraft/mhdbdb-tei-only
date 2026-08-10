/**
 * MHDBDB Playground - Erweiterte Figurenbezeichnungen (Beta)
 *
 * Kuratierte Figurenbezeichnungen (Eigennamen, Decknamen, Antonomasien,
 * Epitheta) aus Linda Beutel-Thurows Naming-analysis für 4 Werke
 * (ENE, IW, ROL, TRO).
 * Datenquelle: data/naming-index.json.gz, gebaut von
 * scripts/ingest/naming/01-fetch-and-build-index.py.
 *
 * Lazy-Load per fetch+pako beim ersten show(); bewusst KEIN IndexedDB-Cache:
 * der Index ist klein (~110 KB gz) und ohne Cache entfällt der
 * Versions-Bump-Kanal, der bei corpus-/authority-index schiefgehen kann (#94).
 *
 * ## Zwei Perspektiven auf dieselben Records (Linda, #59-Kommentar 2026-07-29)
 *
 * Jeder Record trägt beides: WER benannt wird (die Figur, unter der er im
 * Index hängt) und WER benennt (`who` plus `by`). Bis 2026-08 war nur die
 * erste Richtung wählbar.
 *
 *   benannt   Figur wählen, darunter nach der nennenden Instanz filtern
 *             ("Wie wird Iwein genannt, und was davon sagt Lunete?")
 *   nennend   Nenner wählen, Terme nach genannter Figur gruppiert
 *             ("Welche Benennungen für wen findet Iwein im Iwein?")
 *
 * Die zweite Perspektive nimmt drei Arten von Nenner zusammen, weil die Frage
 * sie zusammen meint: den Erzähler, die nennenden Figuren aus `by` und die
 * Selbstnennungen (`who === 'self'`, kein `by`, der Nenner ist die Figur
 * selbst). Ein Nenner ohne Selbstnennungen verliert dadurch nichts.
 *
 * ## Die Notation der Quelle bleibt stehen
 *
 * Die Nennerspalte trägt eine Notation, die die Figurenspalte nicht hat: ein
 * führendes `#` (Rolandslied, zweimal im Trojanerkrieg) und eckige Klammern
 * (Trojanerkrieg). Beide meinen dasselbe: eine Instanz, die keine handelnde
 * Figur des Werks ist, also eine unbestimmbare Menge (`#haiden`, `[MENGE]`)
 * oder eine nur zitierte Person (`#David`, im Werk selbst nicht handelnd).
 * Linda, #59-Kommentar 2026-08-10.
 *
 * Bis dahin war unklar, wofür das Gitter steht, und die Ansicht schnitt es für
 * die Gruppierung ab: fünf Nenner waren durch Schreibvarianten in je zwei
 * Einträge zerfallen (`#David`/`David` und vier weitere). Linda hat die Quelle
 * am selben Tag vereinheitlicht (`b7cc0585`); daran gemessen führt der
 * Schlüssel nichts mehr zusammen (4 Werke, 33/29/48/71 Nenner, mit und ohne
 * Gitter-Schnitt identisch). Damit fällt hier eine Funktion weg statt eines
 * Datenstands, und das `#` steht wieder in der Anzeige, mit einer Erklärung
 * darunter. Es abzuschneiden wäre jetzt sogar falsch: `#David` und ein
 * handelnder David wären derselbe Schlüssel und damit derselbe Nenner.
 *
 * Was der Schlüssel weiter tut: Unterstriche zu Leerzeichen (`#diu_stimme`)
 * und Groß-/Kleinschreibung angleichen, damit erneut auftretende
 * Schreibvarianten nicht wieder zerfallen.
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
import { getNavigationEpoch } from '../core/router.js';

const DEFAULT_STATE = Object.freeze({
  perspective: 'named',  // 'named' = benannte Figur | 'namer' = nennende Instanz
  workSigle: '',
  subject: '',           // gewählte Figur bzw. gewählter Nenner (dessen Schlüssel)
  speaker: '',           // nur 'named': '' | 'erz' | 'self' | 'fig' | 'fig:<key>'
  target: '',            // nur 'namer': '' | Name der genannten Figur
  category: 'all',       // 'all' | einer der CATS
  nameFilter: ''
});

// Kategorien in Anzeigereihenfolge, identisch mit CATS im Build-Skript.
// `deck` (Deckname) ist die vierte, 2026-08-10 auf Lindas Präzisierung hin
// eingeführte Kategorie: ein Term, der die Figur benennt wie ein Name, ohne
// ihr Name zu sein. Sie kommt ausschließlich aus alias-overrides.json und
// trägt derzeit genau einen Beleg (Alexander für Paris, TRO V. 20665) —
// deshalb blenden Tabs und Kacheln sie aus, wo sie leer ist.
const CATS = ['eig', 'deck', 'ant', 'epi'];

const CATEGORY_META = {
  eig:  { label: 'Eigenname',   plural: 'Eigennamen',   badge: 'border-brand-200 bg-brand-50 text-brand-700' },
  deck: { label: 'Deckname',    plural: 'Decknamen',    badge: 'border-violet-200 bg-violet-50 text-violet-700' },
  ant:  { label: 'Antonomasie', plural: 'Antonomasien', badge: 'border-amber-200 bg-amber-50 text-amber-800' },
  epi:  { label: 'Epitheton',   plural: 'Epitheta',     badge: 'border-rose-200 bg-rose-50 text-rose-700' }
};

const EVIDENCE_LIMIT = 50;

// Schlüssel des Erzählers in der Nenner-Perspektive. NUL kann in keinem
// Quellwert stehen, der Schlüssel ist damit unabhängig von der Notation
// kollisionsfrei — anders als früher, als das abgeschnittene '#' ihn trug.
const NARRATOR_KEY = '\u0000erzaehler';

// Werke, deren Edition-Verszählung der MHDBDB-<l n>-Zählung entspricht —
// nur dort sind Vers-Deep-Links in den Reader korrekt (siehe Header-Kommentar).
const READER_LINK_SIGLES = new Set(['ROL', 'TRO']);

// Die Notation der Quelle für „keine handelnde Figur des Werks": Gitter im
// ROL, eckige Klammern im TRO. Steuert nur, ob der Erklärsatz erscheint.
const NOTATION = /^[#[]/;

/** Nenner-Schlüssel: Unterstriche zu Leerzeichen, kleingeschrieben. Das
 *  führende '#' bleibt darin, es ist bedeutungstragend (siehe Header). */
function namerKey(raw) {
  return anzeigeform(raw).toLowerCase();
}

/** Anzeigeform eines Nenners: Unterstriche zu Leerzeichen wie in der
 *  Figurenspalte, Whitespace kollabiert. Die Notation bleibt stehen. */
function anzeigeform(raw) {
  return raw.replace(/_/g, ' ').trim().replace(/\s+/g, ' ');
}

/** Anzeigeform einer Nenner-Gruppe: Großschreibung vor Häufigkeit vor Alphabet. */
function namerLabel(variants) {
  const forms = [...variants.entries()].map(([raw, count]) => ({ text: anzeigeform(raw), count }));
  // Ersten Buchstaben statt erstem Zeichen prüfen: '#' und '[' sind
  // schriftlos, sonst gälte jede Form mit Notation als kleingeschrieben.
  const klein = (text) => {
    const b = text.match(/\p{L}/u)?.[0] || '';
    return b === b.toLowerCase() ? 1 : 0;
  };
  forms.sort((a, b) =>
    klein(a.text) - klein(b.text) || b.count - a.count || a.text.localeCompare(b.text, 'de'));
  return forms[0]?.text || '';
}

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
   * Nenner des Werks als [{key, label, count, figures, variants}], nach
   * Belegzahl absteigend. Der Erzähler steht als eigener Eintrag darin,
   * Selbstnennungen zählen zum Nenner gleichen Namens (siehe Header).
   * Ergebnis wird je Werk gecacht, es hängt nur am Index.
   */
  getNamers(work) {
    if (!work) return [];
    this._namerCache = this._namerCache || new Map();
    if (this._namerCache.has(work.sigle)) return this._namerCache.get(work.sigle);

    const map = new Map();
    const touch = (key, raw) => {
      if (!map.has(key)) {
        map.set(key, { key, count: 0, figures: new Set(), variants: new Map() });
      }
      const entry = map.get(key);
      entry.count += 1;
      entry.variants.set(raw, (entry.variants.get(raw) || 0) + 1);
      return entry;
    };

    for (const [figure, records] of Object.entries(work.figures)) {
      for (const record of records) {
        let entry;
        if (record.who === 'erz') {
          entry = touch(NARRATOR_KEY, 'Erzähler');
        } else if (record.who === 'self') {
          entry = touch(namerKey(figure), figure);
        } else if (record.by) {
          entry = touch(namerKey(record.by), record.by);
        } else {
          continue;  // Figurenrede ohne erfassten Nenner (3x im Iwein)
        }
        entry.figures.add(figure);
      }
    }

    const list = [...map.values()]
      .map(e => ({ ...e, label: e.key === NARRATOR_KEY ? 'Erzähler' : namerLabel(e.variants) }))
      .sort((a, b) => {
        if (a.key === NARRATOR_KEY) return -1;
        if (b.key === NARRATOR_KEY) return 1;
        return b.count - a.count || a.label.localeCompare(b.label, 'de');
      });
    this._namerCache.set(work.sigle, list);
    return list;
  }

  /** Auswahlliste der zweiten Selectbox, je nach Perspektive. */
  getSubjects(work) {
    if (this.state.perspective === 'namer') {
      return this.getNamers(work).map(n => ({
        value: n.key, label: n.label, count: n.count,
        hint: `${n.figures.size} ${n.figures.size === 1 ? 'genannte Figur' : 'genannte Figuren'}`
      }));
    }
    return this.getFigures(work).map(f => ({ value: f.name, label: f.name, count: f.count, hint: '' }));
  }

  /**
   * Records des gewählten Subjekts als [{figure, record}], Unterfilter bereits
   * angewandt. In beiden Perspektiven dieselbe Form, damit computeTerms und
   * die Tabelle nur einmal existieren.
   */
  collectPairs(work) {
    const pairs = [];
    if (this.state.perspective === 'namer') {
      for (const [figure, records] of Object.entries(work.figures)) {
        if (this.state.target && figure !== this.state.target) continue;
        for (const record of records) {
          if (this.namerKeyOf(figure, record) === this.state.subject) {
            pairs.push({ figure, record });
          }
        }
      }
      return pairs;
    }

    const records = work.figures[this.state.subject] || [];
    const speaker = this.state.speaker;
    for (const record of records) {
      if (speaker) {
        if (speaker === 'erz' && record.who !== 'erz') continue;
        if (speaker === 'self' && record.who !== 'self') continue;
        if (speaker === 'fig' && record.who !== 'fig') continue;
        if (speaker.startsWith('fig:')) {
          if (record.who !== 'fig' || !record.by) continue;
          if (namerKey(record.by) !== speaker.slice(4)) continue;
        }
      }
      pairs.push({ figure: this.state.subject, record });
    }
    return pairs;
  }

  /** Nenner-Schlüssel eines Records (Erzähler, Selbstnennung oder `by`). */
  namerKeyOf(figure, record) {
    if (record.who === 'erz') return NARRATOR_KEY;
    if (record.who === 'self') return namerKey(figure);
    return record.by ? namerKey(record.by) : null;
  }

  /**
   * Aggregation zu Termen:
   * [{term, cat, count, figure?, evidence: [{v, ph, who, by}]}]
   *
   * `byFigure` schlüsselt zusätzlich nach genannter Figur auf: in der
   * Nenner-Perspektive ist „vrouwe für Lunete" eine andere Aussage als
   * „vrouwe für Laudine", zusammengezählt verlöre die Tabelle die Antwort
   * auf Lindas Frage („für wen").
   */
  computeTerms(pairs, byFigure) {
    const map = new Map();
    const figureTotals = new Map();
    for (const { figure, record } of pairs) {
      figureTotals.set(figure, (figureTotals.get(figure) || 0) + 1);
      for (const cat of CATS) {
        for (const term of (record[cat] || [])) {
          const key = byFigure ? `${figure}|${cat}|${term}` : `${cat}|${term}`;
          if (!map.has(key)) {
            map.set(key, { key, term, cat, count: 0, evidence: [], figure: byFigure ? figure : null });
          }
          const entry = map.get(key);
          entry.count += 1;
          entry.evidence.push({ v: record.v, ph: record.ph, who: record.who, by: record.by });
        }
      }
    }

    const terms = [...map.values()];
    if (!byFigure) {
      return terms.sort((a, b) => b.count - a.count || a.term.localeCompare(b.term, 'de'));
    }
    // Die meistgenannte Figur zuerst, darin der häufigste Term zuerst.
    return terms.sort((a, b) =>
      (figureTotals.get(b.figure) - figureTotals.get(a.figure))
      || a.figure.localeCompare(b.figure, 'de')
      || b.count - a.count
      || a.term.localeCompare(b.term, 'de'));
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

  renderPerspectiveTabs() {
    const modes = [
      // „Instanz" statt „Figur", weil der Erzähler mit in der Liste steht und
      // keine Figur ist (Linda, #59-Kommentar 2026-08-10). Dieselbe
      // Beschriftung trägt der Unterfilter der anderen Perspektive.
      { key: 'named', label: 'Benannte Figur',   hint: 'Wie wird eine Figur genannt?' },
      { key: 'namer', label: 'Nennende Instanz', hint: 'Wen benennt eine Instanz wie?' }
    ];
    const buttons = modes.map(m => {
      const active = m.key === this.state.perspective;
      const cls = active
        ? 'border-brand-400 bg-brand-50 text-brand-700'
        : 'border-slate-200 bg-white text-slate-600 hover:border-slate-400';
      return `<button type="button" data-ne-persp="${m.key}" title="${escapeAttr(m.hint)}" class="rounded-lg border px-3 py-1.5 text-sm transition ${cls}">${m.label}</button>`;
    }).join('');
    return `
      <div class="flex flex-wrap items-center gap-2">
        <span class="text-xs font-medium text-slate-600">Perspektive</span>
        ${buttons}
      </div>
    `;
  }

  renderForm() {
    const works = this.index?.works || [];
    const workOptions = works.map(w =>
      `<option value="${escapeAttr(w.sigle)}"${w.sigle === this.state.workSigle ? ' selected' : ''}>${escapeHtml(w.sigle)} - ${escapeHtml(w.bookName)}</option>`
    ).join('');

    const work = this.getWork(this.state.workSigle);
    const namerMode = this.state.perspective === 'namer';
    const subjects = this.getSubjects(work);
    const subjectOptions = subjects.map(s => {
      const suffix = s.hint ? `, ${s.hint}` : '';
      return `<option value="${escapeAttr(s.value)}"${s.value === this.state.subject ? ' selected' : ''}>${escapeHtml(s.label)} (${s.count.toLocaleString('de-DE')} Belege${suffix})</option>`;
    }).join('');

    return `
      <div class="rounded-2xl border border-slate-200 bg-slate-50/70 p-4 space-y-3">
        <h3 class="flex items-center gap-2 text-sm font-semibold uppercase tracking-wide text-slate-500">
          Erweiterte Figurenbezeichnungen
          <span class="rounded bg-amber-100 px-1.5 py-0.5 text-[10px] font-semibold uppercase tracking-wide text-amber-800">Beta</span>
        </h3>
        <p class="text-xs text-slate-600">
          Kuratierte Bezeichnungspraktiken jenseits des Eigennamens: Wie wird eine Figur benannt, umschrieben (Antonomasie) und charakterisiert (Epitheton)?
          Verfügbar für die vier Werke mit kuratierten Daten aus dem Dissertationsprojekt <em>Naming-analysis</em> <strong>von Linda Beutel-Thurow (Universität Salzburg).</strong>
        </p>
        ${this.renderPerspectiveTabs()}
        <div class="grid gap-3 sm:grid-cols-2">
          <label class="block">
            <span class="text-xs font-medium text-slate-600">Werk</span>
            <select id="neWorkSelect" class="mt-1 w-full rounded-lg border border-slate-200 bg-white px-3 py-2 text-sm focus:border-brand-400 focus:outline-none">
              <option value="">Werk wählen ...</option>
              ${workOptions}
            </select>
          </label>
          <label class="block">
            <span class="text-xs font-medium text-slate-600">${namerMode ? 'Nennende Instanz (nach Belegzahl)' : 'Figur (nach Belegzahl)'}</span>
            <select id="neFigureSelect" class="mt-1 w-full rounded-lg border border-slate-200 bg-white px-3 py-2 text-sm focus:border-brand-400 focus:outline-none"${work ? '' : ' disabled'}>
              <option value="">${namerMode ? 'Nenner wählen ...' : 'Figur wählen ...'}</option>
              ${subjectOptions}
            </select>
          </label>
        </div>
        ${this.renderNotationHint(work)}
        <p class="text-[11px] text-slate-500">
          Versangaben folgen den Editionsgrundlagen der Naming-analysis-Erhebung. Bei ROL und TRO ist die Zählung mit der MHDBDB deckungsgleich; dort führen die Versangaben direkt in die Leseansicht. Bei ENE und IW kann die Zählung abweichen.
        </p>
      </div>
    `;
  }

  /**
   * Erklärt die Notation der Quelle, sobald sie im gewählten Werk vorkommt.
   * Die Beispiele stammen aus dem Werk selbst (die zwei belegstärksten), damit
   * der Satz auch dann stimmt, wenn Linda die eckigen Klammern im TRO noch auf
   * das Gitter vereinheitlicht — angekündigt im #59-Kommentar 2026-08-10.
   */
  renderNotationHint(work) {
    if (!work) return '';
    const treffer = this.getNamers(work).filter(n => NOTATION.test(n.label));
    if (treffer.length === 0) return '';
    const beispiele = treffer.slice(0, 2)
      .map(n => `<code class="rounded bg-white px-1">${escapeHtml(n.label)}</code>`)
      .join(', ');
    return `
      <p class="text-[11px] text-slate-500">
        <span class="font-medium">Notation der Quelle:</span> Ein vorangestelltes <code class="rounded bg-white px-1">#</code> und eckige Klammern markieren eine Instanz, die keine handelnde Figur des Werks ist: eine unbestimmbare Menge oder eine nur zitierte Person. In diesem Werk etwa ${beispiele}.
      </p>
    `;
  }

  renderBody() {
    const work = this.getWork(this.state.workSigle);
    const namerMode = this.state.perspective === 'namer';
    if (!work) {
      return '<div class="rounded-2xl border border-dashed border-slate-200 bg-white p-8 text-center text-sm text-slate-500">Bitte ein Werk auswählen.</div>';
    }
    if (!this.state.subject) {
      const hint = namerMode
        ? `${this.getNamers(work).length.toLocaleString('de-DE')} nennende Instanzen (Erzähler, Figurenrede, Selbstnennung). Bitte einen Nenner auswählen.`
        : `${Object.keys(work.figures).length.toLocaleString('de-DE')} Figuren mit kuratierten Bezeichnungen. Bitte eine Figur auswählen.`;
      return `<div class="rounded-2xl border border-dashed border-slate-200 bg-white p-8 text-center text-sm text-slate-500">${escapeHtml(work.bookName)}: ${hint}</div>`;
    }
    if (!namerMode && !work.figures[this.state.subject]) {
      return '<div class="rounded-2xl border border-amber-200 bg-amber-50 p-4 text-sm text-amber-800">Die gewählte Figur wurde im Werk nicht gefunden.</div>';
    }

    const pairs = this.collectPairs(work);
    const terms = this.computeTerms(pairs, namerMode);
    const counts = { all: terms.length };
    for (const cat of CATS) counts[cat] = 0;
    for (const t of terms) counts[t.cat] += 1;

    const summary = this.renderSummary(work, pairs, terms);
    const tabs = this.renderCategoryTabs(counts);

    let visible = this.state.category === 'all' ? terms : terms.filter(t => t.cat === this.state.category);
    const filter = this.state.nameFilter.trim();
    if (filter) {
      // MHG-normalisiert, damit "riter" auch "rîter"/"rîtaere" findet
      visible = visible.filter(t => TextNormalizer.matchesNormalized(t.term, filter));
    }

    const controls = this.renderControls(work, visible.length);
    const table = this.renderTermTable(visible, namerMode);

    return summary + tabs + controls + table;
  }

  renderSummary(work, pairs, terms) {
    const occurrences = {};
    for (const cat of CATS) occurrences[cat] = 0;
    for (const t of terms) occurrences[t.cat] += t.count;

    // Der Deckname bekommt nur dann eine eigene Kachel, wenn es ihn hier gibt:
    // er ist ein einzelner kuratierter Sonderfall, und eine dauerhafte
    // Null-Kachel neben drei gefuellten liest sich wie ein Erhebungsmangel.
    const sichtbar = CATS.filter(cat => cat !== 'deck' || occurrences.deck > 0);
    const cells = sichtbar.map(cat => {
      const distinct = terms.filter(t => t.cat === cat).length;
      return `
        <div>
          <div class="text-xs uppercase tracking-wide text-slate-500">${CATEGORY_META[cat].plural}</div>
          <div class="font-semibold text-brand-700">${distinct.toLocaleString('de-DE')} <span class="font-normal text-slate-500">${distinct === 1 ? 'Term' : 'Terme'}</span></div>
          <div class="text-xs text-slate-500">${occurrences[cat].toLocaleString('de-DE')} Vorkommen</div>
        </div>
      `;
    }).join('');

    // Bei gesetztem Unterfilter die Bezugsgroesse mitschreiben: sonst liest
    // sich die gefilterte Zahl wie die Gesamtzahl der Figur.
    const teil = pairs.length.toLocaleString('de-DE');
    let heading, sub;
    if (this.state.perspective === 'namer') {
      const namer = this.getNamers(work).find(n => n.key === this.state.subject);
      const genannte = new Set(pairs.map(p => p.figure)).size;
      heading = namer ? namer.label : this.state.subject;
      const von = this.state.target && namer ? ` von ${namer.count.toLocaleString('de-DE')}` : '';
      sub = `benennt ${genannte.toLocaleString('de-DE')} ${genannte === 1 ? 'Figur' : 'Figuren'} in ${teil}${von} kuratierten Belegstellen`;
      const roh = namer && namer.variants.size > 1 ? [...namer.variants.keys()].join(', ') : '';
      if (roh) sub += ` <span class="cursor-help underline decoration-dotted" title="Schreibungen in der Quelle: ${escapeAttr(roh)}">(${namer.variants.size} Schreibungen)</span>`;
    } else {
      const gesamt = (work.figures[this.state.subject] || []).length;
      heading = this.state.subject;
      sub = `${teil}${this.state.speaker ? ` von ${gesamt.toLocaleString('de-DE')}` : ''} kuratierte Belegstellen`;
    }

    return `
      <div class="rounded-2xl border border-slate-200 bg-white p-4">
        <div class="mb-3">
          <div class="text-xs uppercase tracking-wide text-slate-500">${escapeHtml(work.sigle)} - ${escapeHtml(work.bookName)}</div>
          <div class="text-lg font-semibold text-slate-800">${escapeHtml(heading)}</div>
          <div class="text-xs text-slate-500">${sub}</div>
        </div>
        <div class="grid gap-2 ${sichtbar.length === 4 ? 'sm:grid-cols-4' : 'sm:grid-cols-3'} text-sm">${cells}</div>
      </div>
    `;
  }

  renderCategoryTabs(counts) {
    // Wie bei den Kacheln: der Deckname-Tab erscheint nur, wo er trifft — es
    // sei denn, er ist gerade der gewaehlte. Sonst verschwaende ein
    // Unterfilter, der ihn auf 0 bringt, das aktive Steuerelement, und die
    // leere Tabelle haette keinen sichtbaren Grund mehr.
    const cats = [
      { key: 'all', label: 'Alle' },
      ...CATS.filter(key => key !== 'deck' || counts.deck > 0 || this.state.category === 'deck')
             .map(key => ({ key, label: CATEGORY_META[key].plural }))
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

  /**
   * Unterfilter plus Term-Filter. Der Unterfilter ist die Gegenrichtung der
   * gewählten Perspektive: bei einer Figur die nennende Instanz (Lindas
   * Wunsch 1), bei einem Nenner die genannte Figur.
   */
  renderSubFilter(work) {
    if (this.state.perspective === 'namer') {
      const pairs = [];
      for (const [figure, records] of Object.entries(work.figures)) {
        for (const record of records) {
          if (this.namerKeyOf(figure, record) === this.state.subject) pairs.push(figure);
        }
      }
      const counts = new Map();
      for (const f of pairs) counts.set(f, (counts.get(f) || 0) + 1);
      const options = [...counts.entries()]
        .sort((a, b) => b[1] - a[1] || a[0].localeCompare(b[0], 'de'))
        .map(([name, n]) => `<option value="${escapeAttr(name)}"${name === this.state.target ? ' selected' : ''}>${escapeHtml(name)} (${n.toLocaleString('de-DE')})</option>`)
        .join('');
      return `
        <label class="flex items-center gap-2">
          <span class="text-xs font-medium text-slate-600">Genannte Figur</span>
          <select id="neSubFilter" class="rounded-lg border border-slate-200 bg-white px-2 py-1 text-xs focus:border-brand-400 focus:outline-none">
            <option value="">Alle</option>
            ${options}
          </select>
        </label>
      `;
    }

    const records = work.figures[this.state.subject] || [];
    const tally = { erz: 0, self: 0, fig: 0 };
    const namers = new Map();  // key -> {variants, count}, gleiche Gruppierung
    for (const r of records) {   // wie in getNamers, damit die Beschriftung in
      tally[r.who] = (tally[r.who] || 0) + 1;   // beiden Perspektiven gleich ist
      if (r.who === 'fig' && r.by) {
        const key = namerKey(r.by);
        if (!namers.has(key)) namers.set(key, { variants: new Map(), count: 0 });
        const n = namers.get(key);
        n.count += 1;
        n.variants.set(r.by, (n.variants.get(r.by) || 0) + 1);
      }
    }
    const einzeln = [...namers.entries()]
      .map(([key, n]) => ({ key, count: n.count, label: namerLabel(n.variants) }))
      .sort((a, b) => b.count - a.count || a.label.localeCompare(b.label, 'de'))
      .map(n => `<option value="fig:${escapeAttr(n.key)}"${this.state.speaker === `fig:${n.key}` ? ' selected' : ''}>&nbsp;&nbsp;${escapeHtml(n.label)} (${n.count.toLocaleString('de-DE')})</option>`)
      .join('');
    const opt = (value, label, count) =>
      `<option value="${value}"${this.state.speaker === value ? ' selected' : ''}>${label} (${count.toLocaleString('de-DE')})</option>`;

    return `
      <label class="flex items-center gap-2">
        <span class="text-xs font-medium text-slate-600">Nennende Instanz</span>
        <select id="neSubFilter" class="rounded-lg border border-slate-200 bg-white px-2 py-1 text-xs focus:border-brand-400 focus:outline-none">
          <option value=""${this.state.speaker === '' ? ' selected' : ''}>Alle (${records.length.toLocaleString('de-DE')})</option>
          ${opt('erz', 'Erzähler', tally.erz)}
          ${opt('self', 'Selbstnennung', tally.self)}
          ${opt('fig', 'Figurenrede, alle', tally.fig)}
          ${einzeln}
        </select>
      </label>
    `;
  }

  renderControls(work, visibleCount) {
    return `
      <div class="flex flex-wrap items-center gap-3 rounded-xl border border-slate-200 bg-slate-50/60 p-3 text-sm">
        ${this.renderSubFilter(work)}
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

  renderTermTable(terms, namerMode) {
    if (terms.length === 0) {
      return '<div class="rounded-2xl border border-dashed border-slate-200 bg-white p-6 text-center text-sm text-slate-500">Keine Terme in dieser Kategorie (mit aktuellem Filter).</div>';
    }

    let letzteFigur = null;
    const rows = terms.map(t => {
      const expanded = this.expandedTerms.has(t.key);
      const meta = CATEGORY_META[t.cat];
      const chevron = expanded
        ? '<svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"></path></svg>'
        : '<svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"></path></svg>';

      // Die genannte Figur nur beim Wechsel ausschreiben: die Tabelle ist nach
      // ihr sortiert, wiederholt stuende sie in jeder Zeile derselben Gruppe.
      // Der Wechsel bekommt dafuer eine kraeftigere Trennlinie, sonst ist die
      // Gruppengrenze nur am Namen zu erkennen.
      let figurZelle = '';
      let gruppenRand = '';
      if (namerMode) {
        const neu = t.figure !== letzteFigur;
        gruppenRand = neu && letzteFigur !== null ? ' border-t-2 border-t-slate-200' : '';
        letzteFigur = t.figure;
        figurZelle = neu
          ? `<td class="px-3 py-1.5 align-top font-medium text-slate-700">${escapeHtml(t.figure)}</td>`
          : '<td class="px-3 py-1.5"></td>';
      }

      const mainRow = `
        <tr class="border-b border-slate-100 hover:bg-slate-50 cursor-pointer${gruppenRand}" data-ne-term="${escapeAttr(t.key)}">
          ${figurZelle}
          <td class="px-3 py-1.5">
            <span class="inline-flex items-center gap-1.5 font-medium text-slate-800">${chevron}${escapeHtml(t.term)}</span>
          </td>
          <td class="px-3 py-1.5"><span class="rounded border px-1.5 py-0.5 text-[10px] font-semibold uppercase tracking-wide ${meta.badge}">${meta.label}</span></td>
          <td class="px-3 py-1.5 text-right tabular-nums text-slate-600">${t.count.toLocaleString('de-DE')}</td>
        </tr>
      `;

      if (!expanded) return mainRow;
      return mainRow + this.renderEvidenceRow(t, namerMode);
    }).join('');

    const figurKopf = namerMode
      ? '<th class="w-52 px-3 py-2 text-left text-xs font-semibold text-slate-600">Genannte Figur</th>'
      : '';

    return `
      <div class="overflow-x-auto rounded-2xl border border-slate-200 bg-white">
        <table class="w-full text-sm">
          <thead class="bg-slate-50">
            <tr>
              ${figurKopf}
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

  renderEvidenceRow(t, namerMode) {
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
      // In der Nenner-Perspektive steht der Sprecher schon in der Auswahl.
      // Die Selbstnennung bleibt trotzdem stehen, sie ist die Ausnahme.
      if (namerMode && e.who !== 'self') speaker = '';
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
        <td colspan="${namerMode ? 4 : 3}" class="px-6 py-2 text-xs">${items}${truncated}</td>
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

  /** Auswahl unterhalb des Werks zurücksetzen (Perspektiv- oder Werkwechsel). */
  resetSelection() {
    this.state.subject = '';
    this.state.speaker = '';
    this.state.target = '';
    this.state.category = 'all';
    this.state.nameFilter = '';
    this.expandedTerms.clear();
  }

  attachHandlers() {
    document.querySelectorAll('[data-ne-persp]').forEach(btn => {
      btn.addEventListener('click', (e) => {
        const mode = e.currentTarget.getAttribute('data-ne-persp');
        if (mode === this.state.perspective) return;
        this.state.perspective = mode;
        // Die Auswahl ist perspektivgebunden: ein Figurenname ist kein
        // Nenner-Schluessel, und ein Nenner ist oft gar keine benannte Figur.
        this.resetSelection();
        this.render();
      });
    });

    document.getElementById('neWorkSelect')?.addEventListener('change', (e) => {
      this.state.workSigle = e.target.value;
      this.resetSelection();
      this.render();
    });

    document.getElementById('neFigureSelect')?.addEventListener('change', (e) => {
      const subject = e.target.value;
      this.resetSelection();
      this.state.subject = subject;
      this.render();
    });

    document.getElementById('neSubFilter')?.addEventListener('change', (e) => {
      if (this.state.perspective === 'namer') {
        this.state.target = e.target.value;
      } else {
        this.state.speaker = e.target.value;
      }
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
