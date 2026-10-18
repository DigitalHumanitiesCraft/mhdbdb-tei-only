/**
 * MHDBDB Playground - ONAMA-Narrativ-Explorer, Pilot Argonautensage (Beta)
 *
 * Zeigt einen kuratierten, selektiven Ausschnitt der ONAMA-Annotationen
 * (Ontology of Narratives of the Middle Ages, Salzburg): die Argonautensage in
 * Herborts "Liet von Troye" (TRY), Konrads "Trojanischem Krieg" (TRO) und den
 * Bildrealisierungen aus REALonline. Datenquelle: data/onama/argonauten.json,
 * gebaut von scripts/ingest/onama/build-paket.py (Auswahlkriterium im Docstring
 * dort und im Paket unter meta.auswahl). Der Anker-Abgleich gegen das TEI
 * (anker-abgleich.py) steckt im Paket als Status je Textpassage.
 *
 * Vier Dinge bleiben in der Oberflaeche getrennt, weil das Modell sie trennt
 * (Manifest 16.10.2026, Abschnitt 4): Konzept (abstrakt) und Realisierung
 * (konkret), Handlung (Verb) und Rolle, Rolle und Funktion, allgemeine
 * Funktion (an der Entitaet) und temporaere Funktion (am Rollenknoten).
 * Der Pruefstatus "geprueft" heisst technisch geprueft, nicht fachlich bestaetigt.
 *
 * Lazy-Load per fetch beim ersten show(); bewusst kein IndexedDB-Cache, wie bei
 * den anderen experimentellen Datensaetzen (kleine Datei).
 *
 * Issue: #609
 */

import { getNavigationEpoch } from '../core/router.js';

const ROLLE_LABEL = {
  AgentRole: 'Agens', PatientRole: 'Patiens', ThemeRole: 'Thema', RecipientRole: 'Empfänger',
  InstrumentRole: 'Instrument', GoalRole: 'Ziel', PlaceRole: 'Ort', WitnessRole: 'Zeuge',
  BenefactiveRole: 'Begünstigter', ActantRole: 'Aktant', SourceRole: 'Ausgangspunkt',
  ExperiencerRole: 'Erlebender', StimulusRole: 'Auslöser', 'Co-AgentRole': 'Mit-Agens',
  ModeRole: 'Art und Weise', TemporalityRole: 'Zeitbezug', ParticipatorRole: 'Beteiligter',
  LocalisationRole: 'Lokalisierung', PredicativeRole: 'Prädikativ', CauserRole: 'Verursacher',
  PossessorRole: 'Besitzer'
};

const TYP_LABEL = {
  Person: 'Person', Thing: 'Ding', Place: 'Ort', Animal: 'Tier', MythicalBeing: 'Fabelwesen',
  Group: 'Gruppe', PersistentItem: 'Dauerhaftes Objekt', TemporalEntity: 'Zeit'
};

const QUELLE_LABEL = {
  TRO: 'Konrad, Trojanischer Krieg (TRO)',
  TRY: 'Herbort, Liet von Troye (TRY)',
  OENB2773: 'Bild, ÖNB cod. 2773 (Sammlung)',
  REALONLINE: 'Bild, REALonline (Handschrift nicht belegt)'
};

const QUELLE_KURZ = { TRO: 'TRO', TRY: 'TRY', OENB2773: 'Bild ÖNB 2773', REALONLINE: 'Bild REALonline' };

const PASSAGE_STATUS = {
  wortanker: ['Anker geprüft', 'on-badge-ok'],
  nichtwort_anker: ['Endpunkt ist kein Wort', 'on-badge-warn'],
  umgekehrt: ['Reihenfolge umgekehrt', 'on-badge-bad'],
  nicht_gefunden: ['Anker nicht gefunden', 'on-badge-bad']
};

const PRUEF_BADGE = {
  geprueft: ['technisch geprüft', 'on-badge-ok'],
  abgeleitet: ['abgeleitet', 'on-badge-warn'],
  offen: ['offen', 'on-badge-bad']
};

const KANTE_LABEL = {
  hasActor: 'Akteur', hasThing: 'Ding', hasPlace: 'Ort', hasTemporalEntity: 'Zeit', hasNarrative: 'Erzählung'
};

const MODI = [
  ['ding', 'Ding'],
  ['handlung', 'Handlung'],
  ['entitaet', 'Beteiligte Entität'],
  ['konzept', 'Konzept']
];

export class OnamaExplorer {
  constructor(basePath = 'data/onama') {
    this.basePath = basePath;
    this.paket = null;
    this.loadError = null;
    this.state = { modus: 'ding', auswahl: null, art: 'alle', filter: '' };
  }

  async show() {
    const container = document.getElementById('resultsContainer');
    if (!container) return;
    if (!this.paket && !this.loadError) {
      container.innerHTML = '<div class="on-box on-small" style="text-align:center">Lade ONAMA-Pilot ...</div>';
      const myEpoch = getNavigationEpoch();
      await this.loadPaket();
      if (getNavigationEpoch() !== myEpoch) return;
    }
    this.render();
  }

  async loadPaket() {
    try {
      const response = await fetch(`${this.basePath}/argonauten.json`);
      if (!response.ok) throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      this.paket = await response.json();
      this.loadError = null;
      this.baueIndizes();
    } catch (error) {
      console.error('[OnamaExplorer] Paket konnte nicht geladen werden:', error);
      this.loadError = error.message;
    }
  }

  /** Umkehrindizes: Entitaet, Verb, Konzept -> Realisierungen. Gezaehlt werden Ressourcen, nie Kanten. */
  baueIndizes() {
    const p = this.paket;
    this.realById = new Map(p.realisierungen.map(r => [r.id, r]));
    this.nachEntitaet = new Map();
    this.nachVerb = new Map();
    this.nachKonzept = new Map();
    const add = (map, key, id) => {
      if (!map.has(key)) map.set(key, new Set());
      map.get(key).add(id);
    };
    for (const r of p.realisierungen) {
      for (const rolle of r.rollen) {
        for (const b of rolle.beteiligte) if (b.entitaet) add(this.nachEntitaet, b.entitaet, r.id);
      }
      for (const v of r.handlung) add(this.nachVerb, v, r.id);
      for (const c of [...r.konzepte, ...r.nebenhandlungs_konzepte]) add(this.nachKonzept, c, r.id);
    }
  }

  // ---------------------------------------------------------------- Auswahl

  eintraege() {
    const p = this.paket;
    const f = this.state.filter.trim().toLocaleLowerCase('de');
    const passt = (text) => !f || text.toLocaleLowerCase('de').includes(f);
    let liste = [];
    if (this.state.modus === 'ding' || this.state.modus === 'entitaet') {
      const istDing = (e) => e.typen.includes('Thing');
      liste = Object.values(p.entitaeten)
        .filter(e => (this.state.modus === 'ding' ? istDing(e) : !istDing(e)))
        .map(e => ({ id: e.id, label: e.labels.de || e.labels.en || e.id, sub: e.typen.map(t => TYP_LABEL[t] || t).join(', '),
                     n: (this.nachEntitaet.get(e.id) || new Set()).size }));
    } else if (this.state.modus === 'handlung') {
      liste = Object.entries(p.verben)
        .map(([id, l]) => ({ id, label: l.de || l.en || id, sub: '', n: (this.nachVerb.get(id) || new Set()).size }));
    } else {
      liste = Object.entries(p.konzepte)
        .filter(([id]) => this.nachKonzept.has(id))
        .map(([id, k]) => ({ id, label: k.labels.de || k.labels.en || id, sub: '', n: this.nachKonzept.get(id).size }));
    }
    return liste.filter(x => x.n > 0 && passt(x.label))
      .sort((a, b) => b.n - a.n || a.label.localeCompare(b.label, 'de'));
  }

  ausgewaehlteRealisierungen() {
    const a = this.state.auswahl;
    if (!a) return [];
    let ids = [];
    if (a.art === 'realisierung') ids = [a.id];
    else if (a.art === 'entitaet') ids = [...(this.nachEntitaet.get(a.id) || [])];
    else if (a.art === 'verb') ids = [...(this.nachVerb.get(a.id) || [])];
    else if (a.art === 'konzept') ids = [...(this.nachKonzept.get(a.id) || [])];
    return ids.map(id => this.realById.get(id))
      .filter(r => r && (this.state.art === 'alle' || r.art === this.state.art))
      .sort((x, y) => x.id.localeCompare(y.id, 'de', { numeric: true }));
  }

  // ---------------------------------------------------------------- Rendern

  render() {
    const container = document.getElementById('resultsContainer');
    if (!container) return;
    if (this.loadError) {
      container.innerHTML = `<div class="on-banner">Der ONAMA-Pilot konnte nicht geladen werden: ${esc(this.loadError)}</div>`;
      return;
    }
    container.innerHTML = `
      <div class="on-wrap">
        ${this.renderKopf()}
        ${this.renderEinstieg()}
        ${this.renderTreffer()}
        ${this.renderRandfaelle()}
        ${this.renderHerkunft()}
      </div>`;
    this.attachHandlers();
  }

  renderKopf() {
    const m = this.paket.meta;
    const s = m.statistik;
    const z = (pred) => this.paket.realisierungen.filter(pred).length;
    const text = z(r => r.art === 'text');
    const bild = z(r => r.art === 'bild');
    const abgeleitet = z(r => r.zuordnung === 'abgeleitet');
    const neben = z(r => r.nebenhandlung);
    return `
      <div class="on-box-soft on-stack">
        <h3 class="on-h">ONAMA: Argonautensage <span class="on-badge on-badge-warn">Beta</span></h3>
        <p class="on-text">
          Wer tut was mit welchem Ding? ONAMA hat Handlungen in mittelalterlichen Texten und Bildern annotiert.
          Dieser Pilot zeigt die Geschichte von Jason und dem Goldenen Vlies in Konrads <em>Trojanischem Krieg</em>,
          Herborts <em>Liet von Troye</em> und in Bildern aus REALonline.
        </p>
        <div class="on-banner">
          <strong>Selektiver Bestand.</strong> Das ist ein kuratierter Ausschnitt, kein Gesamtbestand der
          mittelalterlichen Narrative; was hier nicht steht, ist nicht annotiert oder nicht ausgewählt, aber nicht
          nachweislich abwesend. Gezählt wird nach Realisierungen:
          ${s.realisierungen_gesamt} (${text} Text, ${bild} Bild; davon ${abgeleitet} Bilder nur über Konzept und
          RO-Label zugeordnet, ${neben} Nebenhandlungen).
          Datenversion: ONAMA-Korpus <span class="on-mono">${esc(m.quellen.korpus_commit.slice(0, 7))}</span>,
          Ontologie <span class="on-mono">${esc(m.quellen.ontologie_commit.slice(0, 7))}</span>,
          MHDBDB-Anker <span class="on-mono">${esc(m.quellen.mhdbdb_commit.slice(0, 7))}</span>.
          Der Status "technisch geprüft" bedeutet: Zuordnung über die Sammlung und bei Texten zwei Wortanker im
          Korpus in richtiger Reihenfolge, bei Bildern ein Bildlink. Es gilt der Vorrang offen vor abgeleitet vor
          geprüft: "offen" bei unauffindbarem oder umgekehrtem Anker, fehlender Textpassage oder fehlendem
          Bildlink; "abgeleitet" bei fehlender Sammlung oder umgerechneter Wortspanne.
          Fachlich bestätigt ist noch nichts.
        </div>
      </div>`;
  }

  renderEinstieg() {
    const modus = MODI.map(([key, label]) =>
      `<button type="button" class="on-tab" data-on-modus="${key}" aria-pressed="${this.state.modus === key}">${esc(label)}</button>`).join('');
    const art = [['alle', 'Text und Bild'], ['text', 'nur Text'], ['bild', 'nur Bild']].map(([key, label]) =>
      `<button type="button" class="on-tab" data-on-art="${key}" aria-pressed="${this.state.art === key}">${esc(label)}</button>`).join('');
    const eintraege = this.eintraege();
    const aktiv = this.state.auswahl;
    const items = eintraege.map(e => {
      const art2 = { ding: 'entitaet', entitaet: 'entitaet', handlung: 'verb', konzept: 'konzept' }[this.state.modus];
      const cur = aktiv && aktiv.art === art2 && aktiv.id === e.id;
      return `<li><button type="button" class="on-item" data-on-wahl="${esc(art2)}:${esc(e.id)}"${cur ? ' aria-current="true"' : ''}>
        <span>${esc(e.label)}${e.sub ? ` <span class="on-small">${esc(e.sub)}</span>` : ''}</span><span class="on-count">${e.n}</span></button></li>`;
    }).join('');
    const hinweis = {
      ding: 'Dinge (Gegenstände, auch Orte mit Dingcharakter), nach Zahl der Realisierungen, in denen sie eine Rolle haben.',
      handlung: 'Verben der annotierten Handlungen.',
      entitaet: 'Personen, Tiere, Fabelwesen, Orte und Gruppen, die an Handlungen beteiligt sind.',
      konzept: 'Abstrakte Konzepte, die in diesem Ausschnitt realisiert sind (überwiegend aus dem Teilbaum "Geschichte von den Argonauten").'
    }[this.state.modus];
    return `
      <div class="on-box-soft on-stack">
        <div class="on-row"><span class="on-small">Einstieg über</span><div class="on-tabs">${modus}</div></div>
        <p class="on-small" style="margin:0">${esc(hinweis)}</p>
        <label class="on-stack" style="gap:0.25rem"><span class="on-small">Filter</span>
          <input type="search" id="onFilter" class="on-input" value="${esc(this.state.filter)}" placeholder="Eintrag suchen ..." autocomplete="off"></label>
        <ul class="on-list" id="onListe">${items || '<li class="on-small" style="padding:0.75rem">Kein Eintrag.</li>'}</ul>
        <div class="on-row"><span class="on-small">Anzeigen</span><div class="on-tabs">${art}</div></div>
      </div>`;
  }

  renderTreffer() {
    const a = this.state.auswahl;
    if (!a) {
      return '<div class="on-box on-small" style="text-align:center;border-style:dashed">Bitte oben einen Einstieg wählen.</div>';
    }
    const treffer = this.ausgewaehlteRealisierungen();
    const titel = this.auswahlLabel(a);
    if (!treffer.length) {
      return `<div class="on-box on-small">Keine Realisierung für "${esc(titel)}" in diesem Ausschnitt${this.state.art !== 'alle' ? ' (Filter Text/Bild beachten)' : ''}.</div>`;
    }
    // Nach Konzept gruppieren: ein Konzept, darunter seine Realisierungen.
    const gruppen = new Map();
    for (const r of treffer) {
      const k = r.konzepte[0] || r.nebenhandlungs_konzepte[0] || '';
      if (!gruppen.has(k)) gruppen.set(k, []);
      gruppen.get(k).push(r);
    }
    const offen = gruppen.size <= 3;
    const karten = [...gruppen.entries()].map(([k, rs]) => this.renderGruppe(k, rs, offen)).join('');
    return `
      <div class="on-stack">
        <div class="on-small"><strong>${esc(titel)}</strong>: ${treffer.length} Realisierung${treffer.length === 1 ? '' : 'en'}
          in ${gruppen.size} Konzept${gruppen.size === 1 ? '' : 'en'}.</div>
        ${karten}
      </div>`;
  }

  auswahlLabel(a) {
    const p = this.paket;
    if (a.art === 'entitaet') return p.entitaeten[a.id]?.labels.de || a.id;
    if (a.art === 'verb') return p.verben[a.id]?.de || a.id;
    if (a.art === 'konzept') return p.konzepte[a.id]?.labels.de || a.id;
    return this.realById.get(a.id)?.labels.de || a.id;
  }

  renderGruppe(konzeptId, reals, offen) {
    const k = this.paket.konzepte[konzeptId];
    const label = k ? (k.labels.de || k.labels.en) : 'Ohne Konzept';
    const nebenInfo = reals.some(r => r.nebenhandlung) ? ' (Nebenhandlung)' : '';
    const konzeptSchicht = k ? `
      <div class="on-layer on-layer-concept on-stack">
        <h4 class="on-h3">Konzept: abstrakt, medienübergreifend</h4>
        <div class="on-text"><strong>${esc(label)}</strong>${nebenInfo}
          <span class="on-mono on-small">${esc(k.uri.split('/').pop())}</span></div>
        ${k.labels.en ? `<div class="on-small">${esc(k.labels.en)}</div>` : ''}
        ${k.handlung.length ? `<div class="on-small">Handlung: ${k.handlung.map(v => esc(this.paket.verben[v]?.de || v)).join(', ')}</div>` : ''}
        ${k.rollen.length ? this.renderRollen(k.rollen, 'Rollen auf Konzeptebene') : ''}
        ${this.renderKonzeptBezug(k, konzeptId)}
      </div>` : '';
    const real = reals.map(r => this.renderRealisierung(r)).join('');
    return `
      <details class="on-card"${offen ? ' open' : ''}>
        <summary class="on-card-head"><span class="on-h2">${esc(label)}</span>
          <span class="on-small">${reals.length} Realisierung${reals.length === 1 ? '' : 'en'}</span></summary>
        <div class="on-card-body">${konzeptSchicht}${real}</div>
      </details>`;
  }

  renderKonzeptBezug(k, id) {
    const teile = [];
    const chips = (ids) => ids.map(c => this.paket.konzepte[c]
      ? `<button type="button" class="on-btn" data-on-wahl="konzept:${esc(c)}">${esc(this.paket.konzepte[c].labels.de || c)}</button>` : '').join(' ');
    if (k.uebergeordnet.length) teile.push(`<div class="on-small">Teil von: ${chips(k.uebergeordnet)}</div>`);
    const mitReal = k.untergeordnet.filter(c => this.nachKonzept.has(c));
    if (mitReal.length) {
      teile.push(`<div class="on-small">Teilhandlungen (${mitReal.length} mit Realisierung von ${k.untergeordnet.length}): ${chips(mitReal.slice(0, 12))}${mitReal.length > 12 ? ' ...' : ''}</div>`);
    }
    if (k.wikidata.length || k.iconclass.length) {
      teile.push(`<div class="on-small">Normdaten laut ONAMA (Beziehung wie gespeichert, keine Identitätsbehauptung): ${[
        ...k.wikidata.map(w => `<a class="on-link" href="${esc(w)}" target="_blank" rel="noopener">Wikidata ${esc(w.split('/').pop())}</a>`),
        ...k.iconclass.map(i => `Iconclass ${esc(i)}`)].join(', ')}</div>`);
    }
    return teile.join('');
  }

  renderRealisierung(r) {
    const [pTxt, pCls] = PRUEF_BADGE[r.pruefstatus];
    const quelle = QUELLE_KURZ[r.quelle] || r.quelle;
    const zuordnung = r.zuordnung === 'abgeleitet'
      ? '<span class="on-badge on-badge-warn" title="Keine Sammlung gespeichert; Zuordnung nur über Konzept und RO-Label.">Zuordnung abgeleitet</span>' : '';
    const sammlung = r.sammlungen.length
      ? `<div class="on-small">Sammlung: ${r.sammlungen.map(s => esc(this.paket.sammlungen[s]?.de || s)).join(', ')}</div>`
      : '<div class="on-small">Keine Sammlung gespeichert.</div>';
    const quellen = r.art === 'text' ? this.renderPassagen(r) : this.renderBild(r);
    return `
      <div class="on-layer on-layer-real on-stack" data-on-real="${esc(r.id)}">
        <h4 class="on-h3">Realisierung: konkret in ${r.art === 'text' ? 'einem Text' : 'einem Bild'}</h4>
        <div class="on-row">
          <strong class="on-text">${esc(r.labels.de)}</strong>
          <span class="on-badge on-badge-brand">${esc(quelle)}</span>
          <span class="on-badge ${pCls}">${esc(pTxt)}</span>${zuordnung}
          ${r.nebenhandlung ? '<span class="on-badge">Nebenhandlung</span>' : ''}
          <span class="on-mono on-small" title="${esc(r.uri)}">${esc(r.id)}</span>
        </div>
        ${r.labels.en ? `<div class="on-small">${esc(r.labels.en)}</div>` : ''}
        ${sammlung}
        ${r.handlung.length ? `<div class="on-small">Handlung: ${r.handlung.map(v => esc(this.paket.verben[v]?.de || v)).join(', ')}</div>` : ''}
        ${this.renderRollen(r.rollen, 'Rollen und Funktionen in dieser Realisierung')}
        ${quellen}
        ${this.renderFolge(r)}
      </div>`;
  }

  /** Rolle, allgemeine Funktion (an der Entitaet) und temporaere Funktion (am Rollenknoten) in getrennten Spalten. */
  renderRollen(rollen, titel) {
    if (!rollen.length) return '<div class="on-small">Keine Rollen annotiert.</div>';
    const p = this.paket;
    const fn = (ids, cls) => ids.map(i => `<span class="on-badge ${cls}">${esc(p.funktionen[i]?.de || p.funktionen[i]?.en || i)}</span>`).join(' ');
    const sel = this.state.auswahl;
    const zeilen = rollen.map(rolle => {
      const wer = rolle.beteiligte.map(b => {
        if (b.entitaet) {
          const e = p.entitaeten[b.entitaet];
          const fett = sel && sel.art === 'entitaet' && sel.id === b.entitaet ? ' style="font-weight:700"' : '';
          return `<button type="button" class="on-btn"${fett} data-on-wahl="entitaet:${esc(b.entitaet)}" title="${esc((e.typen || []).map(t => TYP_LABEL[t] || t).join(', '))}">${esc(e.labels.de || b.entitaet)}</button>`;
        }
        if (b.zeit) return `<span class="on-badge">${esc(b.zeit.de || b.zeit.en)}</span>`;
        if (b.verweis) return `<span class="on-badge" title="${esc(KANTE_LABEL[b.kante])}">Verweis ${esc(b.verweis)}</span>`;
        return '';
      }).join(' ');
      const allg = [...new Set(rolle.beteiligte.filter(b => b.entitaet).flatMap(b => p.entitaeten[b.entitaet].allgemeine_funktionen))];
      return `<tr><td><span title="${esc(rolle.klasse)}">${esc(ROLLE_LABEL[rolle.klasse] || rolle.klasse)}</span></td>
        <td>${wer}</td><td>${fn(allg, 'on-fn-gen')}</td><td>${fn(rolle.temporaere_funktionen, 'on-fn-tmp')}</td></tr>`;
    }).join('');
    return `
      <div>
        <div class="on-small" style="margin-bottom:0.25rem">${esc(titel)}</div>
        <table class="on-table">
          <thead><tr><th>Rolle</th><th>Beteiligte</th><th>Allgemeine Funktion (der Entität)</th><th>Funktion in dieser Handlung</th></tr></thead>
          <tbody>${zeilen}</tbody>
        </table>
      </div>`;
  }

  renderPassagen(r) {
    if (!r.passagen.length) return '<div class="on-small">Keine Textpassage gespeichert (Status offen).</div>';
    const zeilen = r.passagen.map(pa => {
      const [txt, cls] = PASSAGE_STATUS[pa.status];
      const springen = (pa.status === 'wortanker' || pa.status === 'nichtwort_anker') && pa.text
        ? `<a class="on-link" href="../korpus.html?textId=${encodeURIComponent(pa.text)}&verseId=${encodeURIComponent(pa.von)}" target="_blank" rel="noopener" title="Anfang der Passage in der Leseansicht öffnen">Leseansicht</a>`
        : '<span class="on-small">kein Sprung</span>';
      const span = pa.wortspanne
        ? `Wörter ${pa.wortspanne[0].toLocaleString('de-DE')}–${pa.wortspanne[1].toLocaleString('de-DE')}`
        : '';
      return `<tr><td class="on-mono">${esc(pa.von)}</td><td class="on-mono">${esc(pa.bis)}</td>
        <td><span class="on-badge ${cls}">${esc(txt)}</span></td>
        <td class="on-small">${esc(span)}${pa.umgerechnet ? ' <span class="on-badge on-badge-warn" title="Ein Endpunkt ist kein Wort mit Lemma-Annotation; Start und Ende sind auf das nächste gezählte Wort verschoben.">umgerechnet</span>' : ''}</td><td>${springen}</td></tr>`;
    }).join('');
    return `
      <div>
        <div class="on-small" style="margin-bottom:0.25rem">Textstelle im MHDBDB-Korpus, Anker wie in ONAMA gespeichert</div>
        <table class="on-table"><thead><tr><th>von</th><th>bis</th><th>Prüfung</th><th>Wortspanne</th><th></th></tr></thead><tbody>${zeilen}</tbody></table>
      </div>`;
  }

  renderBild(r) {
    return r.bildlink
      ? `<div class="on-small">Bildquelle: <a class="on-link" href="${esc(r.bildlink)}" target="_blank" rel="noopener">REALonline ${esc(r.bildlink.split('=').pop())}</a> (nur verlinkt)</div>`
      : '<div class="on-small">Kein Bildlink gespeichert (Status offen).</div>';
  }

  renderFolge(r) {
    const chips = (ids) => ids.map(i => this.realById.has(i)
      ? `<button type="button" class="on-btn" data-on-wahl="realisierung:${esc(i)}">${esc(this.realById.get(i).labels.de)}</button>` : '').filter(Boolean).join(' ');
    const vor = chips(r.vorher);
    const nach = chips(r.nachher);
    if (!vor && !nach) return '';
    return `<div class="on-small">Ereignisfolge (Fabula) innerhalb des Ausschnitts:
      ${vor ? `davor ${vor}` : ''} ${nach ? `danach ${nach}` : ''}</div>`;
  }

  renderRandfaelle() {
    const rf = this.paket.randfaelle;
    const aus = this.paket.ausgeschlossen;
    const gruppen = new Map();
    for (const x of rf) {
      if (!gruppen.has(x.grund)) gruppen.set(x.grund, []);
      gruppen.get(x.grund).push(x);
    }
    const teile = [...gruppen.entries()].map(([grund, xs]) => `
      <div><div class="on-small"><strong>${esc(grund)}</strong> (${xs.length})</div>
        <ul class="on-small" style="margin:0.25rem 0 0.5rem 1rem;padding:0">${xs.map(x =>
          `<li>${esc(x.label)} <span class="on-mono">${esc(x.id)}${x.sammlung ? `, ${esc(x.sammlung)}` : ''}</span></li>`).join('')}</ul></div>`).join('');
    return `
      <details class="on-box-soft on-details">
        <summary>Nicht im Ausschnitt: ${rf.length} Randfälle zur fachlichen Entscheidung, ${aus.length} ausgeschlossen</summary>
        <div class="on-stack" style="margin-top:0.5rem">
          <p class="on-small" style="margin:0">Randfälle haben möglicherweise Argonautenbezug, hängen aber nicht am Konzeptbaum
            oder haben keine Sammlung. Sie werden nicht stillschweigend aufgenommen; die Entscheidung liegt bei der
            Projektleitung. Ausgeschlossen sind Realisierungen aus Sammlungen außerhalb des Piloten
            (${aus.map(a => esc(a.label)).join('; ')}).</p>
          ${teile}
        </div>
      </details>`;
  }

  renderHerkunft() {
    const m = this.paket.meta;
    return `
      <div class="on-box-soft on-small">
        <div><strong>ONAMA</strong> (Ontology of Narratives of the Middle Ages), Universität Salzburg
          (MHDBDB und IMAREAL/REALonline), 2019–2021. Korpus:
          <a class="on-link" href="${esc(m.quellen.korpus)}" target="_blank" rel="noopener">onama-corpus</a>,
          Ontologie: <a class="on-link" href="${esc(m.quellen.ontologie)}" target="_blank" rel="noopener">onama</a>.</div>
        <div>Lizenz: ${esc(m.lizenz.festlegung)}. Herkunft: ${esc(m.lizenz.herkunft)}</div>
        <div>${esc(m.hinweise.namensraum)} Die Wortspannen zählen nur Wörter mit Lemma-Annotation wie der Rest des
          Playgrounds. ${esc(m.hinweise.wortspanne)}</div>
        <div><a class="on-link" href="../hilfe-playground.html#onama-narrativ-explorer" target="_blank" rel="noopener">Hilfe zum Narrativ-Explorer</a></div>
      </div>`;
  }

  attachHandlers() {
    document.querySelectorAll('[data-on-modus]').forEach(b => b.addEventListener('click', (e) => {
      this.state.modus = e.currentTarget.getAttribute('data-on-modus');
      this.state.filter = '';
      this.render();
    }));
    document.querySelectorAll('[data-on-art]').forEach(b => b.addEventListener('click', (e) => {
      this.state.art = e.currentTarget.getAttribute('data-on-art');
      this.render();
    }));
    document.querySelectorAll('[data-on-wahl]').forEach(b => b.addEventListener('click', (e) => {
      const [art, ...rest] = e.currentTarget.getAttribute('data-on-wahl').split(':');
      this.state.auswahl = { art, id: rest.join(':') };
      this.render();
      document.getElementById('resultsContainer')?.scrollTo?.({ top: 0 });
    }));
    const filter = document.getElementById('onFilter');
    if (filter) {
      filter.addEventListener('input', (e) => {
        this.state.filter = e.target.value;
        const pos = e.target.selectionStart;
        this.render();
        const neu = document.getElementById('onFilter');
        neu?.focus();
        neu?.setSelectionRange(pos, pos);
      });
    }
  }
}

function esc(s) {
  if (s == null) return '';
  return String(s).replace(/[&<>"']/g, c => (
    { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]
  ));
}
