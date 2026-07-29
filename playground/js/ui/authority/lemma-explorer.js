/**
 * MHDBDB Playground - Lemma Explorer
 * Handles lemma browsing, search, and sense display with etymology
 */

import {
  createSearchInterface,
  handleSearchResults,
  generateResultItem,
  setupSearchInput,
  toggleDetails,
  showEmptySearchState,
  renderToContainer,
  formatMetadata,
  SearchPatterns,
} from "../search/SearchHelpers.js";
import { TextNormalizer } from "../../../../assets/js/lib/text-normalizer.js";

/**
 * Mindestlänge der Eingabe im Wortbestandteil-Modus (#239 Anforderung 5).
 * Darunter ist die Trefferliste sinnlos groß: „en" allein steckt in
 * mehreren tausend Lemmata.
 */
const COMPONENT_MIN_LENGTH = 3;

/** Höchstzahl angezeigter Treffer je Positionsgruppe. Wird sichtbar gemeldet. */
const COMPONENT_GROUP_LIMIT = 200;

/**
 * Die drei Positionsgruppen aus #239 Anforderung 3, in Anzeigereihenfolge.
 * `collapsed` steuert, ob die Gruppe zugeklappt startet: die Wortmitte tut
 * das, weil dort die meisten Zufallstreffer liegen.
 */
const COMPONENT_GROUPS = [
  {
    key: "ende",
    title: "Als Grundwort am Wortende",
    hint: "Determinativkomposita: der gesuchte Bestandteil ist das Grundwort.",
    collapsed: false,
  },
  {
    key: "anfang",
    title: "Als Bestimmungswort am Wortanfang",
    hint: "Der gesuchte Bestandteil bestimmt ein anderes Grundwort näher.",
    collapsed: false,
  },
  {
    key: "mitte",
    title: "In der Wortmitte",
    hint: "Hier liegen die meisten Zufallstreffer, deshalb startet die Gruppe zugeklappt.",
    collapsed: true,
  },
];

export class LemmaExplorer {
  constructor(authorityData) {
    this.authorityData = authorityData;
    this.searchMode = "lemma";
  }

  showLemmata() {
    if (this.authorityData.lemmata.length > 500) {
      this.showLemmataWithSearch();
    } else {
      this.showAllLemmata();
    }
  }

  showAllLemmata() {
    const displayCount = Math.min(100, this.authorityData.lemmata.length);
    const resultHTML = this.authorityData.lemmata
      .slice(0, displayCount)
      .map((l) =>
        generateResultItem({
          meta: formatMetadata([
            `ID: ${l.id}`,
            (l.posAll?.length || l.pos) ? `POS: ${(l.posAll || [l.pos]).join(' ')}` : null,
            l.senseCount ? `${l.senseCount} Bedeutungen` : null,
          ]),
          title: `<a href="../lemma/?id=${l.id.replace(/^lemma_/, '')}" target="_blank" rel="noopener" class="text-brand-700 hover:text-brand-900 hover:underline">${l.lemma}</a>`,
          buttons: [
            ...(l.senseCount > 0
              ? [
                  {
                    text: "Bedeutungen anzeigen",
                    action: `window.playground.ui.authorityExplorers.showLemmaSenses('${l.id}')`,
                  },
                ]
              : []),
            {
              text: "MEHR \u2192",
              action: `window.open('../lemma/?id=${l.id.replace(/^lemma_/, '')}', '_blank')`,
            },
          ],
          detailsId: `senses-${l.id}`,
        })
      )
      .join("");

    const header = `<div class="rounded-xl bg-slate-50/80 px-4 py-2 text-sm font-medium text-slate-600">
      <span>Lemmata-Explorer</span>
      <span class="ml-2 text-sm uppercase tracking-wide text-slate-600">erste ${displayCount} von ${this.authorityData.lemmata.length}</span>
    </div>`;

    renderToContainer("resultsContainer", header + `<div class="space-y-3">${resultHTML}</div>`);
  }

  showLemmataWithSearch(mode = "lemma") {
    this.searchMode = mode === "component" ? "component" : "lemma";
    const istKomponente = this.searchMode === "component";

    const searchHTML = createSearchInterface({
      title: "Lemmata-Explorer",
      placeholder: istKomponente
        ? `Wortbestandteil eingeben (z.B. wein, herze, lich), mindestens ${COMPONENT_MIN_LENGTH} Zeichen`
        : "Lemma eingeben (z.B. vriunt, minne, ere)",
      searchInputId: "lemmaSearch",
      resultsId: "lemmaResults",
      totalCount: this.authorityData.lemmata.length,
      helpText: istKomponente
        ? `Sucht Lemmata, die den eingegebenen Bestandteil enthalten, und gruppiert sie danach, wo er steht. Mindestens ${COMPONENT_MIN_LENGTH} Zeichen.`
        : "Geben Sie einen Suchbegriff ein, um zu starten.",
      extraControlsHTML: this.buildModeSwitchHTML(this.searchMode),
    });

    renderToContainer("resultsContainer", searchHTML);
    setupSearchInput("lemmaSearch", (term) =>
      this.searchMode === "component"
        ? this.searchWordComponents(term)
        : this.searchLemmata(term)
    );
  }

  /**
   * Umschalter zwischen der normalen Lemmasuche und der Wortbestandteil-Suche
   * (#239). Bewusst zwei benannte Modi statt einer stillen Erweiterung der
   * Lemmasuche: die Infix-Discovery war der Träger des #224-Rauschens und
   * gehört nicht zurück in die reguläre Auflösung (ADR-016 bleibt).
   */
  buildModeSwitchHTML(aktiv) {
    const knopf = (modus, label, beschreibung) => {
      const an = aktiv === modus;
      const klassen = an
        ? "rounded-xl border border-brand-400 bg-brand-50 px-4 py-2 text-left text-sm font-semibold text-brand-700"
        : "rounded-xl border border-slate-200 bg-white px-4 py-2 text-left text-sm font-medium text-slate-700 transition hover:border-brand-400 hover:text-brand-700";
      return `
        <button type="button" aria-pressed="${an}"
          onclick="window.playground.ui.authorityExplorers.switchLemmaSearchMode('${modus}')"
          class="${klassen}">
          <span class="block">${label}</span>
          <span class="mt-0.5 block text-xs font-normal text-slate-500">${beschreibung}</span>
        </button>
      `;
    };

    return `
      <div class="flex flex-wrap gap-2">
        ${knopf("lemma", "Lemma suchen", "Findet Lemmata zu einer Schreibform")}
        ${knopf("component", "Wortbestandteil suchen", "Findet Komposita zu einem Bestandteil")}
      </div>
    `;
  }

  /**
   * Modus wechseln und den bereits eingegebenen Suchbegriff mitnehmen.
   * Geht über den Hash, damit der Modus bookmarkbar bleibt (#48-Konvention).
   */
  switchLemmaSearchMode(modus) {
    // Der Moduswechsel verwirft die Trefferliste, also auch ihren gesicherten
    // Zustand. Sonst überlebt eine Sicherung den Ausflug in die normale
    // Lemmasuche und wird nach der Rückkehr auf einen anderen Begriff gelegt.
    this.discardComponentViewState();
    const eingabe = document.getElementById("lemmaSearch");
    const term = eingabe ? eingabe.value.trim() : "";
    const teile = ["lemmata"];
    if (modus === "component") teile.push("mode=component");
    if (term) teile.push(`q=${encodeURIComponent(term)}`);
    window.location.hash = teile.join("&");
  }

  searchLemmata(searchTerm) {
    if (!searchTerm.trim()) {
      showEmptySearchState("lemmaResults");
      return;
    }

    const matches = SearchPatterns.textContainsNormalized(
      this.authorityData.lemmata,
      searchTerm,
      (lemma) => lemma.lemma
    );

    // #137: alphabetisch nach Lemma-Label sortieren (vorher implizit nach Lemma-ID),
    // VOR dem maxResults-Cut in handleSearchResults. Idiom wie concept-explorer.js.
    matches.sort((a, b) => (a.lemma || "").localeCompare(b.lemma || "", "de"));

    const result = handleSearchResults(searchTerm, matches, {
      maxResults: 50,
      emptyMessage: 'Keine Lemmata gefunden für "{term}"',
    });

    if (typeof result === "string") {
      renderToContainer("lemmaResults", result);
      return;
    }

    const resultHTML = result.matches
      .map((lemma) =>
        generateResultItem({
          meta: formatMetadata([
            `ID: ${lemma.id}`,
            (lemma.posAll?.length || lemma.pos) ? `POS: ${(lemma.posAll || [lemma.pos]).join(' ')}` : null,
            lemma.senseCount ? `${lemma.senseCount} Bedeutungen` : null,
          ]),
          title: `<a href="../lemma/?id=${lemma.id.replace(/^lemma_/, '')}" target="_blank" rel="noopener" class="text-brand-700 hover:text-brand-900 hover:underline">${lemma.lemma}</a>`,
          buttons: [
            ...(lemma.senseCount > 0
              ? [
                  {
                    text: "Bedeutungen anzeigen",
                    action: `window.playground.ui.authorityExplorers.showLemmaSenses('${lemma.id}')`,
                  },
                ]
              : []),
            {
              text: "MEHR \u2192",
              action: `window.open('../lemma/?id=${lemma.id.replace(/^lemma_/, '')}', '_blank')`,
            },
          ],
          detailsId: `senses-${lemma.id}`,
        })
      )
      .join("");

    renderToContainer("lemmaResults", result.headerHTML + resultHTML);
  }

  // ==================== WORTBESTANDTEIL-SUCHE (#239) ====================

  /**
   * Welche normalisierten Zeichenfolgen als Bestandteil gesucht werden.
   *
   * Die Eingabe allein reicht nicht. `normalizeMHG` bildet „wein" auf „wein"
   * ab, `wîn` dagegen auf „win", und ein Kompositum wie `ôsterwîn` heißt
   * normalisiert „osterwin". Eine reine Zeichensuche nach „wein" fände es
   * also nie. Deshalb werden zusätzlich die normalisierten Formen der
   * Lemmata aufgenommen, auf die die Eingabe exakt oder über die
   * Variantenliste zeigt: „wein" führt über `variants["wein"]` auf
   * `lemma_7532 wîn` und damit auf den Bestandteil „win".
   *
   * Das ist zugleich die im Ticket benannte Fehltreffer-Quelle: mit „win"
   * kommen `winter`, `gewinnen`, `winden` und die Eigennamen auf -wîn mit.
   * Der Zeichenvergleich allein kann das nicht trennen. Wo `lexicon.xml` die
   * Wortbildung ausdrücklich verzeichnet (27.166 Lemmata tragen
   * `etymology[]`, rund 62 Prozent), markiert die Trefferliste das und der
   * Filter blendet den Rest aus; für die übrigen 38 Prozent bleibt der
   * Zeichenvergleich der einzige Zugang.
   *
   * @returns {{formen: string[], quellen: Array<{form: string, lemma: object}>}}
   */
  resolveComponentForms(term) {
    const eingabeNorm = TextNormalizer.normalizeMHG(term);
    const formen = [eingabeNorm];
    const quellen = [];

    // Nur die Variantenbrücke erweitert die Formenliste. Ein exakter Treffer
    // in Stufe 1 hätte per Definition dieselbe normalisierte Form wie die
    // Eingabe, brächte also nichts Neues; dass es ihn gibt, meldet die
    // Exakt-Zeile im Kopf ohnehin.
    const variantenId = this.authorityData.variants?.[eingabeNorm];
    if (variantenId) {
      const lemma = this.authorityData.lemmata.find((l) => l.id === variantenId);
      const form = lemma ? TextNormalizer.normalizeMHG(lemma.lemma || "") : "";
      // Die Mindestlänge gilt auch für die Brückenform, sonst umgeht ein
      // dreibuchstabiges Stichwort, dessen Lemma kürzer ist, die Schranke
      // aus Anforderung 5 und die Trefferliste explodiert doch.
      if (form && form.length >= COMPONENT_MIN_LENGTH && !formen.includes(form)) {
        formen.push(form);
        quellen.push({ form, lemma });
      }
    }

    return { formen, quellen };
  }

  /**
   * Position eines Bestandteils in einer normalisierten Lemmaform.
   * `null`, wenn der Bestandteil gar nicht vorkommt.
   */
  componentPosition(lemmaNorm, form) {
    if (!lemmaNorm || !form || !lemmaNorm.includes(form)) return null;
    if (lemmaNorm === form) return "exakt";
    if (lemmaNorm.endsWith(form)) return "ende";
    if (lemmaNorm.startsWith(form)) return "anfang";
    return "mitte";
  }

  searchWordComponents(searchTerm) {
    const term = (searchTerm || "").trim();

    if (!term) {
      this.discardComponentViewState();
      showEmptySearchState(
        "lemmaResults",
        `Wortbestandteil eingeben, mindestens ${COMPONENT_MIN_LENGTH} Zeichen.`
      );
      return;
    }

    // Beide Längen prüfen. normalizeMHG VERLÄNGERT bei Umlauten und
    // Ligaturen (ä zu ae, œ zu oe), eine zweibuchstabige Eingabe wie „wä"
    // oder „bœ" käme sonst dreizeichig durch die Schranke, obwohl Platzhalter
    // und Fehlermeldung drei Zeichen versprechen.
    if (term.length < COMPONENT_MIN_LENGTH ||
        TextNormalizer.normalizeMHG(term).length < COMPONENT_MIN_LENGTH) {
      this.discardComponentViewState();
      showEmptySearchState(
        "lemmaResults",
        `Mindestens ${COMPONENT_MIN_LENGTH} Zeichen, sonst wird die Trefferliste unbrauchbar groß.`
      );
      return;
    }

    this.lastComponentTerm = term;

    const { formen, quellen } = this.resolveComponentForms(term);
    const rang = { exakt: 0, ende: 1, anfang: 2, mitte: 3 };
    const gruppen = { exakt: [], ende: [], anfang: [], mitte: [] };

    this.authorityData.lemmata.forEach((lemma) => {
      const lemmaNorm = TextNormalizer.normalizeMHG(lemma.lemma || "");
      if (!lemmaNorm) return;

      // Ein Lemma kann mehrere der gesuchten Formen enthalten; es zählt die
      // aussagekräftigste Position (exakt vor Wortende vor Wortanfang).
      let beste = null;
      let besteForm = null;
      formen.forEach((form) => {
        const pos = this.componentPosition(lemmaNorm, form);
        if (pos && (beste === null || rang[pos] < rang[beste])) {
          beste = pos;
          besteForm = form;
        }
      });

      if (beste) gruppen[beste].push({ lemma, form: besteForm, norm: lemmaNorm });
    });

    // Kuratierte Wortbildung: welche Treffer führen eines der Ziel-Lemmata
    // ausdrücklich als morphologische Komponente? Die Exakt-Gruppe ist genau
    // die Menge der Lemmata, die der Eingabe entsprechen (bei „wein" also
    // wîn über die Variantenbrücke).
    const zielIds = new Set(gruppen.exakt.map((e) => e.lemma.id));
    Object.values(gruppen).forEach((liste) =>
      liste.forEach((eintrag) => {
        eintrag.belegt = (eintrag.lemma.etymology || []).some(
          (komponente) => komponente.lemmaRef && zielIds.has(komponente.lemmaRef)
        );
      })
    );

    const belegteGesamt = Object.entries(gruppen)
      .filter(([key]) => key !== "exakt")
      .reduce((s, [, liste]) => s + liste.filter((e) => e.belegt).length, 0);

    // Die Antwort auf „wie viele Lemmata enthalten den Bestandteil" ist immer
    // die ungefilterte Zahl. Was der Filter ändert, ist die Anzeigemenge.
    const gefundenGesamt = Object.entries(gruppen)
      .filter(([key]) => key !== "exakt")
      .reduce((s, [, liste]) => s + liste.length, 0);

    if (this.componentOnlyMorph) {
      Object.keys(gruppen).forEach((key) => {
        if (key !== "exakt") gruppen[key] = gruppen[key].filter((e) => e.belegt);
      });
    }

    // Sortierung: belegte Wortbildungen zuerst, dann nach Bedeutungszahl,
    // dann alphabetisch. Die Reihenfolge entscheidet zugleich, was der
    // Gruppendeckel abschneidet; rein alphabetisch wäre das ein beliebiges
    // Präfix statt der aussagekräftigsten Treffer.
    Object.values(gruppen).forEach((liste) =>
      liste.sort(
        (a, b) =>
          Number(b.belegt) - Number(a.belegt) ||
          (b.lemma.senseCount || 0) - (a.lemma.senseCount || 0) ||
          (a.lemma.lemma || "").localeCompare(b.lemma.lemma || "", "de")
      )
    );

    // Die Leer-Meldung hängt an den Positionsgruppen OHNE die Exakt-Gruppe.
    // Sonst kann sie nie erscheinen, sobald der gesuchte Bestandteil selbst
    // ein Lemma ist, und das ist in diesem Modus der Regelfall.
    const angezeigt = Object.entries(gruppen)
      .filter(([key]) => key !== "exakt")
      .reduce((s, [, liste]) => s + liste.length, 0);

    if (angezeigt === 0) {
      // Der Kopf MUSS auch hier stehen. In ihm sitzt die Filter-Checkbox, und
      // die Meldung darunter rät gerade dazu, den Filter abzuschalten: ohne
      // Kopf verschwindet das Bedienelement zusammen mit den Treffern,
      // `componentOnlyMorph` bleibt aber gesetzt. Wer einmal hier landet, käme
      // nur über eine neue Suche mit belegten Treffern wieder heraus.
      const meldung = this.componentOnlyMorph && gefundenGesamt > 0
        ? `Keiner der ${gefundenGesamt} Treffer für "${this.escapeText(term)}" führt ein passendes Grundwort als belegte Wortbildung. Filter abschalten, um alle Zeichen-Treffer zu sehen.`
        : gruppen.exakt.length
          // „Kein Lemma enthält …" wäre hier falsch: das Lemma steht im Kopf.
          ? `Außer dem Lemma selbst enthält kein weiteres den Bestandteil "${this.escapeText(term)}".`
          : `Kein Lemma enthält den Bestandteil "${this.escapeText(term)}".`;

      renderToContainer(
        "lemmaResults",
        this.buildComponentHeaderHTML(
          term, formen, quellen, gruppen, gefundenGesamt, belegteGesamt, angezeigt
        ) +
        `<div class="rounded-2xl border border-dashed border-slate-200 bg-slate-50/70 p-6 text-center text-sm text-slate-500">
          ${meldung}
        </div>`
      );
      this.restoreComponentViewState();
      return;
    }

    renderToContainer(
      "lemmaResults",
      this.buildComponentHeaderHTML(
        term, formen, quellen, gruppen, gefundenGesamt, belegteGesamt, angezeigt
      ) + COMPONENT_GROUPS.map((g) => this.buildComponentGroupHTML(g, gruppen[g.key])).join("")
    );

    this.restoreComponentViewState();
  }

  /**
   * Filter „nur belegte Wortbildungen" umschalten und dieselbe Suche neu
   * rendern. Vorher werden Auswahl und aufgeklappte Gruppen gesichert: der
   * wahrscheinlichste Ablauf ist ankreuzen, dann filtern, dann weiter
   * ankreuzen, und ein kommentarloser Verlust der Häkchen wäre echter
   * Arbeitsverlust.
   */
  toggleComponentMorphFilter(an) {
    this.rememberComponentViewState();
    this.componentOnlyMorph = !!an;
    if (this.lastComponentTerm) this.searchWordComponents(this.lastComponentTerm);
  }

  rememberComponentViewState() {
    this._componentPicked = new Set(
      Array.from(document.querySelectorAll(".component-pick:checked")).map((b) => b.value)
    );
    // Nur Gruppen erfassen, die es im aktuellen Render überhaupt gab, und den
    // Zustand je Gruppe ablegen statt als Menge der offenen. Der Unterschied
    // entscheidet den Rückweg aus dem Leerzustand: dort existiert keine
    // einzige Gruppe, eine Menge wäre leer, und ein leeres Set ist truthy.
    // Die Wiederherstellung würde daraufhin ALLE Gruppen zuklappen, auch die
    // beiden, die COMPONENT_GROUPS offen startet. Wer den Filter abschaltet,
    // um wieder alle Treffer zu sehen, bekäme drei zugeklappte Kopfzeilen.
    const gerendert = COMPONENT_GROUPS.map((g) => [
      g.key, document.getElementById(`component-group-${g.key}`)
    ]).filter(([, el]) => el);

    this._componentOpen = gerendert.length
      ? Object.fromEntries(
          gerendert.map(([key, el]) => [key, !el.classList.contains("hidden")])
        )
      : null;
  }

  /**
   * Gesicherten Ansichtszustand wegwerfen. Nötig in jedem Pfad, der die
   * Trefferliste verlässt, ohne sie neu aufzubauen: die Sicherung wird sonst
   * von der NÄCHSTEN Suche eingelöst und setzt dort Häkchen, die zu einem
   * anderen Suchbegriff gehören. Sichtbar würde das erst bei der Übergabe an
   * die Multi-Lemma-Suche, also zu spät.
   */
  discardComponentViewState() {
    this._componentPicked = null;
    this._componentOpen = null;
  }

  restoreComponentViewState() {
    if (this._componentPicked) {
      document.querySelectorAll(".component-pick").forEach((box) => {
        if (this._componentPicked.has(box.value)) box.checked = true;
      });
      this._componentPicked = null;
    }
    if (this._componentOpen) {
      COMPONENT_GROUPS.forEach((g) => {
        const el = document.getElementById(`component-group-${g.key}`);
        if (!el) return;
        // Für eine Gruppe, die es beim Merken nicht gab, existiert kein
        // gemerkter Zustand. Dann gilt ihre Voreinstellung, nicht „zu".
        const sollOffen = g.key in this._componentOpen
          ? this._componentOpen[g.key]
          : !g.collapsed;
        el.classList.toggle("hidden", !sollOffen);
        const knopf = document.querySelector(`[aria-controls="component-group-${g.key}"]`);
        if (knopf) knopf.setAttribute("aria-expanded", String(sollOffen));
      });
      this._componentOpen = null;
    }
  }

  buildComponentHeaderHTML(term, formen, quellen, gruppen, gefundenGesamt, belegteGesamt, angezeigt) {
    const gesucht = formen.map((f) => `<code>${this.escapeText(f)}</code>`).join(", ");

    // Anforderung 4: sichtbar machen, worauf tatsächlich gesucht wird. Ohne
    // diesen Satz ist nicht nachvollziehbar, warum die Eingabe „wein" das
    // Lemma wîn und dessen Komposita findet.
    const bruecke = quellen.length
      ? `Über die Lemma-Auflösung kommt hinzu: ${quellen
          .map(
            (q) =>
              `${this.escapeText(q.lemma.lemma)} (<code>${this.escapeText(q.form)}</code>)`
          )
          .join(", ")}.`
      : "";

    // Nicht „die Eingabe ist ein Lemma": bei „wein" steht hier wîn, das die
    // Eingabe nur über die Variantenbrücke erreicht. Die Checkbox trägt
    // dieselbe Klasse wie die Gruppentreffer, damit das Grundwort selbst
    // mit an die Multi-Lemma-Suche gehen kann (wîn + trinken).
    const exakt = gruppen.exakt.length
      ? `<p class="mt-2 flex flex-wrap items-center gap-2 text-sm text-slate-600">
          <span>Der gesuchte Bestandteil ist selbst ein Lemma:</span>
          ${gruppen.exakt
            .map(
              (e) => `<label class="inline-flex items-center gap-1">
                  <input type="checkbox" class="component-pick" value="${this.escapeText(e.lemma.lemma)}"
                    aria-label="${this.escapeText(e.lemma.lemma)} auswählen" />
                  <a href="../lemma/?id=${e.lemma.id.replace(/^lemma_/, "")}" target="_blank" rel="noopener" class="font-semibold text-brand-700 hover:underline">${this.escapeText(e.lemma.lemma)}</a>
                </label>`
            )
            .join(" ")}
        </p>`
      : "";

    return `
      <div class="space-y-3">
        <div class="rounded-xl bg-slate-50/80 px-4 py-3 text-sm text-slate-600">
          <p class="font-medium text-slate-700">
            ${gefundenGesamt} Lemmata enthalten den Bestandteil "${this.escapeText(term)}"${
              this.componentOnlyMorph
                ? `, davon ${angezeigt} als belegte Wortbildung angezeigt`
                : ""
            }
          </p>
          <p class="mt-2">
            Gesucht wird auf der normalisierten Form (<code>î</code> zu <code>i</code>,
            <code>ö</code> zu <code>oe</code>): ${gesucht}. ${bruecke}
            Angezeigt werden die Originalformen.
          </p>
          <p class="mt-2 text-xs text-slate-500">
            Der Scan vergleicht Zeichenfolgen, nicht Wortbildung. „win" trifft
            deshalb auch <em>winter</em>, <em>gewinnen</em> und <em>winden</em>, und die
            Komposita auf <em>-swîn</em> (Schwein) landen neben denen auf <em>-wîn</em>
            (Wein). Wo das Wörterbuch die Wortbildung ausdrücklich verzeichnet, ist der
            Treffer mit „belegte Wortbildung" markiert; der Filter darunter blendet
            alles andere aus. Geben Sie den Bestandteil unflektiert ein: die Brücke über
            die Variantenliste greift nur bei belegten Schreibformen, „weine" führt
            also nicht auf <em>wîn</em>.
          </p>
          ${exakt}
        </div>
        <div class="flex flex-wrap items-center gap-3 rounded-xl border border-slate-200 bg-white px-4 py-3">
          <label class="inline-flex items-center gap-2 text-xs text-slate-600">
            <input type="checkbox" id="componentOnlyMorph" ${this.componentOnlyMorph ? "checked" : ""}
              onchange="window.playground.ui.authorityExplorers.toggleComponentMorphFilter(this.checked)" />
            <span>Nur belegte Wortbildungen (${belegteGesamt})</span>
          </label>
          <button type="button"
            onclick="window.playground.ui.authorityExplorers.sendWordComponentSelection()"
            class="rounded-lg bg-brand-600 px-3 py-1 text-xs font-semibold text-white shadow-sm transition hover:bg-brand-700">
            Auswahl an die Multi-Lemma-Suche übergeben
          </button>
          <span id="componentPickHint" class="text-xs text-slate-500">
            Lemmata ankreuzen und übergeben, um ihre Belege im Korpus zu suchen.
            Mehrere Lemmata werden dort UND-verknüpft, also als Texte gesucht,
            die alle Gewählten enthalten.
          </span>
        </div>
      </div>
    `;
  }

  buildComponentGroupHTML(gruppe, eintraege) {
    const anzahl = eintraege.length;
    const listenId = `component-group-${gruppe.key}`;
    const versteckt = gruppe.collapsed ? " hidden" : "";

    if (anzahl === 0) {
      return `
        <div class="mt-4 rounded-xl border border-dashed border-slate-200 px-4 py-2 text-sm text-slate-400">
          ${gruppe.title}: keine Treffer
        </div>
      `;
    }

    // Gekappt wird nach der Sortierung „belegte Wortbildung zuerst, dann
    // Bedeutungszahl": ein alphabetischer Schnitt würde bei häufigen
    // Bestandteilen wie „lich" ein beliebiges Präfix zeigen.
    const sichtbar = eintraege.slice(0, COMPONENT_GROUP_LIMIT);
    const gekappt =
      anzahl > COMPONENT_GROUP_LIMIT
        ? `<p class="px-1 pb-2 text-xs text-slate-500">Angezeigt werden
             ${COMPONENT_GROUP_LIMIT} von ${anzahl} Treffern dieser Gruppe: erst die
             belegten Wortbildungen, dann die Lemmata mit den meisten Bedeutungen.</p>`
        : "";

    const eintraegeHTML = sichtbar
      .map(({ lemma, belegt }) => {
        const kurzId = lemma.id.replace(/^lemma_/, "");
        const abzeichen = belegt
          ? `<span class="rounded bg-brand-50 px-1.5 py-0.5 text-xs font-medium text-brand-700">belegte Wortbildung</span>`
          : "";
        return `
          <article class="result-item flex items-start gap-3 rounded-2xl border border-slate-200 bg-white/95 p-3 shadow-sm">
            <input type="checkbox" class="component-pick mt-1" value="${this.escapeText(lemma.lemma)}"
              aria-label="${this.escapeText(lemma.lemma)} auswählen" />
            <div class="min-w-0">
              <p class="text-xs font-semibold uppercase tracking-wide text-brand-600">
                ${formatMetadata([
                  `ID: ${lemma.id}`,
                  lemma.posAll?.length || lemma.pos
                    ? `POS: ${(lemma.posAll || [lemma.pos]).join(" ")}`
                    : null,
                  lemma.senseCount ? `${lemma.senseCount} Bedeutungen` : null,
                ])}
              </p>
              <p class="mt-1 flex flex-wrap items-center gap-2 text-sm font-semibold text-slate-900">
                <a href="../lemma/?id=${kurzId}" target="_blank" rel="noopener"
                   class="text-brand-700 hover:text-brand-900 hover:underline">${this.escapeText(lemma.lemma)}</a>
                ${abzeichen}
              </p>
            </div>
          </article>
        `;
      })
      .join("");

    return `
      <div class="mt-4">
        <button type="button" aria-expanded="${!gruppe.collapsed}" aria-controls="${listenId}"
          onclick="window.playground.ui.authorityExplorers.toggleWordComponentGroup('${gruppe.key}')"
          class="w-full rounded-xl bg-slate-50/80 px-4 py-2 text-left text-sm font-medium text-slate-700 transition hover:bg-slate-100">
          ${gruppe.title} (${anzahl})
          <span class="ml-2 text-xs font-normal text-slate-500">${gruppe.hint}</span>
        </button>
        <div id="${listenId}" class="mt-2 space-y-2${versteckt}">
          ${gekappt}
          ${eintraegeHTML}
        </div>
      </div>
    `;
  }

  toggleWordComponentGroup(key) {
    const liste = document.getElementById(`component-group-${key}`);
    if (!liste) return;
    const jetztVersteckt = liste.classList.toggle("hidden");
    const knopf = document.querySelector(`[aria-controls="component-group-${key}"]`);
    if (knopf) knopf.setAttribute("aria-expanded", String(!jetztVersteckt));
  }

  /**
   * Anforderung 2: ausgewählte Lemmata gesammelt an die Multi-Lemma-Suche
   * geben. Übergeben werden die Originalformen, nicht die IDs, weil die
   * Multi-Lemma-Route Schreibformen erwartet und sie in der Ergebnisanzeige
   * auch so beschriftet. Sie laufen dort durch Stufe 1 der Auflösung.
   */
  sendWordComponentSelection() {
    const gewaehlt = Array.from(document.querySelectorAll(".component-pick:checked")).map(
      (box) => box.value
    );
    const meldung = document.getElementById("componentPickHint");

    if (gewaehlt.length === 0) {
      // Kein alert(): ein blockierender Dialog hängt die Seite. Der Altfall
      // dieser Art in den Such-Flows, das prompt() in
      // executeProximitySearch(), ist inzwischen entfernt. Übrig sind nur
      // noch die Dialoge in playground-main.js (Ladefehler und
      // Cache-Verwaltung), die keinen Suchweg blockieren.
      //
      // Der Originaltext wird gemerkt und beim nächsten Häkchen wieder
      // hergestellt. Ohne das bliebe der Hinweis nach einem Fehlklick
      // dauerhaft rot und der Satz zur UND-Verknüpfung für immer weg.
      if (meldung) {
        if (!meldung.dataset.originalText) {
          meldung.dataset.originalText = meldung.textContent;
          meldung.dataset.originalClass = meldung.className;
        }
        meldung.textContent = "Bitte zuerst mindestens ein Lemma ankreuzen.";
        meldung.className = "text-xs font-medium text-red-600";
        document.querySelectorAll(".component-pick").forEach((box) =>
          box.addEventListener("change", () => this.resetComponentPickHint(), { once: true })
        );
      }
      return;
    }

    const terme = gewaehlt.map((t) => encodeURIComponent(t)).join(",");
    window.location.hash = `multi-lemma&lemmata=${terme}&mode=document`;
  }

  /** Fehlerzustand des Übergabe-Hinweises zurücknehmen. */
  resetComponentPickHint() {
    const meldung = document.getElementById("componentPickHint");
    if (!meldung || !meldung.dataset.originalText) return;
    meldung.textContent = meldung.dataset.originalText;
    meldung.className = meldung.dataset.originalClass || "text-xs text-slate-500";
  }

  /** Self-contained per module (DESIGN.md §Escaping-Konvention). */
  escapeText(s) {
    if (s == null) return "";
    return String(s).replace(
      /[&<>"']/g,
      (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" })[c]
    );
  }

  showLemmaSenses(lemmaId) {
    toggleDetails(`senses-${lemmaId}`, () => {
      const lemma = this.authorityData.lemmata.find((l) => l.id === lemmaId);
      if (!lemma) return "Lemma nicht gefunden";

      return this.generateLemmaSenseContent(lemma, lemmaId);
    });
  }

  showComponentLemma(originalLemmaId, componentLemmaId, componentText) {
    const container = document.getElementById(`senses-${originalLemmaId}`);
    if (!container) return;

    const lemma = this.authorityData.lemmata.find((l) => l.id === componentLemmaId);

    if (!lemma) {
      container.innerHTML = `Lemma "${componentText}" nicht gefunden`;
      return;
    }

    const content = this.generateLemmaSenseContent(
      lemma,
      componentLemmaId,
      originalLemmaId
    );

    container.innerHTML = `
        <div style="margin-bottom: 10px; padding: 8px; background: rgba(40, 167, 69, 0.1); border-radius: 4px;">
            <strong>Komponente:</strong> ${componentText} → ${lemma.lemma}
            <button onclick="window.playground.ui.authorityExplorers.showOriginalLemmaSenses('${originalLemmaId}')"
                    style="float: right; padding: 2px 6px; background: #6c757d; color: white; border: none; border-radius: 3px; font-size: 0.75rem; cursor: pointer;">
                ← Zurück
            </button>
        </div>
        ${content}
    `;
  }

  // #167 Finding 17: „← Zurück" bei Etymologie-Komponenten darf das sichtbare
  // Panel nicht togglen (= ausblenden), sondern rendert die Original-
  // Bedeutungen direkt in den Container.
  showOriginalLemmaSenses(lemmaId) {
    const container = document.getElementById(`senses-${lemmaId}`);
    if (!container) return;
    const lemma = this.authorityData.lemmata.find((l) => l.id === lemmaId);
    container.innerHTML = lemma
      ? this.generateLemmaSenseContent(lemma, lemmaId)
      : "Lemma nicht gefunden";
  }

  generateLemmaSenseContent(lemma, lemmaId, originalLemmaId = null) {
    let resultHTML = "";

    // Extract etymology from index data
    if (lemma.etymology && lemma.etymology.length > 0) {
      const componentsHTML = lemma.etymology
        .map((comp) => {
          const text = comp.text;
          const referencedLemmaId = comp.lemmaRef;

          if (referencedLemmaId) {
            const targetOriginal = originalLemmaId || lemmaId;
            return `
                      <span style="background: rgba(40, 167, 69, 0.1); padding: 2px 6px; border-radius: 3px; margin-right: 5px;">
                          <strong>${text}</strong>
                          <button onclick="window.playground.ui.authorityExplorers.showComponentLemma('${targetOriginal}', '${referencedLemmaId}', '${text}')"
                                  style="margin-left: 4px; padding: 1px 4px; background: #28a745; color: white; border: none; border-radius: 2px; font-size: 0.7rem; cursor: pointer;">
                              →
                          </button>
                      </span>
                  `;
          }
          return `<span style="background: rgba(108, 117, 125, 0.1); padding: 2px 6px; border-radius: 3px; margin-right: 5px;">${text}</span>`;
        })
        .join("");

      resultHTML += `
              <div style="font-weight: 500; margin-bottom: 8px; color: #28a745;">
                  Morphologie: ${componentsHTML}
              </div>
          `;
    }

    // Extract senses from index data
    if (!lemma.senses || lemma.senses.length === 0) {
      resultHTML += "Keine Bedeutungen gefunden";
      return resultHTML;
    }

    const sensesHTML = lemma.senses
      .map((sense, index) => {
        const senseId = sense.id || `sense_${index + 1}`;

        let conceptsHTML = "";
        if (sense.conceptIds && sense.conceptIds.length > 0) {
          const concepts = sense.conceptIds
            .map((conceptId) => {
              const concept = this.authorityData.concepts.find(
                (c) => c.id === conceptId
              );
              return concept ? concept.termDE || concept.termEN : conceptId;
            })
            .filter(Boolean);

          if (concepts.length > 0) {
            conceptsHTML = `
                    <div style="margin-top: 5px; font-size: 0.85rem; color: #475569;">
                        <strong>Begriffe:</strong> ${concepts.join(" • ")}
                    </div>
                `;
          }
        }

        // Ohne Begriffszuordnung (z.B. #115-Stubs) keine rohe Sense-ID als
        // Pseudo-Bedeutung anzeigen — gleiche Behandlung wie lemma-page.js.
        const senseLabel =
          sense.conceptIds && sense.conceptIds.length > 0
            ? senseId
            : '<span style="color: #94a3b8;">Keine Begriffszuordnung</span>';

        return `
            <div style="margin-bottom: 8px; font-size: 0.9rem;">
                <strong>Bedeutung ${index + 1}:</strong> ${senseLabel}
                ${conceptsHTML}
            </div>
        `;
      })
      .join("");

    resultHTML += `
        <div style="font-weight: 500; margin-bottom: 8px; color: #667eea;">
            ${lemma.senses.length} Bedeutungen:
        </div>
        ${sensesHTML}
    `;

    return resultHTML;
  }

  showLemmaDetails(lemmaId, lemmaText) {
    // Navigate to Lemma Explorer with pre-filled search
    this.showLemmataWithSearch();

    // Pre-fill search input and trigger search
    setTimeout(() => {
      const searchInput = document.getElementById("lemmaSearch");
      if (searchInput) {
        searchInput.value = lemmaText;
        this.searchLemmata(lemmaText);
        searchInput.focus();
      }
    }, 0);
  }
}
