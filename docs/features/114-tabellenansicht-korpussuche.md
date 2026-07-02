# Issue #114: Tabellenansicht für Korpussuche

## Context

User-Wunsch ([#114](https://github.com/DigitalHumanitiesCraft/mhdbdb-tei-only/issues/114)):

> „Bei der alten MHDBDB konnte man immer so schön tabellarisch sehen, wie sich
> ein Lemma verteilt. […] aber da kann man nicht so richtig absolute Zahlen
> sehen. Wäre es ggf. möglich, dass man die Listenansicht in der Korpussuche
> in eine Tabellenansicht wechseln kann?"

Die aktuelle Korpussuche (`korpus.html`) rendert Treffer als Karten mit Titel,
Sigle, Trefferanzahl und Autor*in. Für die Frage „wie verteilt sich ein Lemma
über den Korpus" ist das semantisch korrekt, aber visuell schlecht zu scannen
und nicht direkt weiterverarbeitbar. Forscher kopieren typischerweise in Excel,
um eigene Auswertungen zu fahren.

Scope: nur die Hauptseite (`korpus.html`). Playground hat eigene Analyse-Module
(#90 Lemma-Verteilung als Bar-Chart, #47 R2 Begriffs-Verteilung), die anders
spezialisiert sind.

## Design Decisions

### Spalten (5)

Sigle wird mit dem Titel kombiniert, um Platz zu sparen. Begründung: das
3-Spalten-Layout (`grid-cols-[1fr_1fr_2fr]` über die `three-column`-Klasse)
wird in `app.js:553-557` aktiviert, sobald Suchergebnisse erscheinen — der
Reader-Slot ist auch bei geschlossenem Reader Platzhalter, die Results-Spalte
bleibt entsprechend schmal. Konkrete Breiten messurabar: ~300 px bei 1280 px
Viewport, ~460 px bei 1920 px, ~612 px bei 2560 px. Bei <1280 px (xl-
Breakpoint) fällt Tailwind auf `grid-cols-1` zurück und stackt vollbreit.

Konsequenz: Im 3-Spalten-Layout reicht der horizontale Platz für die Tabelle
typischerweise *nicht*. → siehe „Layout-Modus in Tabellen-Ansicht" unten.

| Spalte | Format | Sortierbar |
|---|---|---|
| Titel (mit Sigle-Präfix) | `JT · Der Jüngere Titurel` (Sigle monospace, dann `·` und Titel) | ja (nach Titel) |
| Autor*in | Volltext, Ellipsis bei Überlänge | ja |
| Treffer | absolute Zahl, rechtsbündig | ja, Default ↓ |
| Frequenz/10k W. | `matchCount / wordCount * 10000`, 1 Nachkommastelle | ja |
| Wortanzahl | mit Tausender-Trennzeichen | ja |

Genre wurde verworfen: ist im Status quo schon halb-präsent (viele Texte ohne),
kostet Spaltenplatz und ist für die Frage „Verteilung eines Lemmas" kein
primärer Indikator. Filter-Sidebar deckt Genre weiter ab.

### Layout-Modus in Tabellen-Ansicht

In `viewMode === 'table'` wird die `three-column`-Klasse vom `#mainGrid`
**entfernt** und durch einen neuen Modus (z.B. `table-layout`-Klasse) ersetzt,
der per CSS auf `grid-cols-1` zurückfällt — der Results-Block belegt damit die
volle Breite (~1100-2400 px je nach Viewport). Search-Sidebar wandert über
oder unter die Tabelle (zu entscheiden in Implementation; Vorschlag: Sidebar
collapsed oben mit „Filter ein-/ausklappen"-Affordance).

Konsequenz für den Reader: Im Tabellen-Modus ist *kein* Reader-Slot reserviert.
Ein Row-Klick (siehe „Zeilen-Klick" unten) **wechselt automatisch zurück auf
`viewMode === 'list'`** und öffnet dann den Reader. Mental-Modell: „Tabelle =
Vergleichs-/Export-Modus; Liste = Lese-Modus." `localStorage`-Eintrag bleibt
auf `'table'` — beim nächsten Schließen des Readers kehrt der User in die
Tabelle zurück.

### Sortierung

- Klickbare Spalten-Header, asc/desc-Toggle bei Re-Klick auf dieselbe Spalte
- Neue Spalte → immer `desc` initial; Re-Klick auf dieselbe Spalte toggelt. Konsistentes Modell auch für Text-Spalten (Titel/Autor*in) — User kommt mit einem Re-Klick zur natürlichen Alphabetik.
- Default beim ersten Anzeigen: **Treffer ↓** (identisch zur aktuellen Listenansicht — kein Überraschungseffekt beim Toggle)
- Sortierung wird **nicht** persistiert (jede neue Suche startet mit Default)
- Sortierung **überlebt** View-Toggle innerhalb derselben Suche: Tabelle → Liste → Tabelle behält den Sort-Spec. Nur eine neue Suche setzt auf Default zurück.
- Visuelle Indikatoren: `↑` / `↓` neben Header-Text, `↕` im hover-state als Affordance
- Accessibility: `aria-sort` Attribut auf `<th>`, sort-Trigger ist `<button>` innerhalb `<th>` (kein Klick auf den `<th>` direkt)

### Toggle Liste ↔ Tabelle

- Segmented-Control im Results-Header neben `(N Texte gefunden)`
- Zwei Buttons mit Text-Labels („Liste" / „Tabelle") plus Icon (Heroicon `list-bullet` und `table-cells`)
- Aktuell aktive Ansicht ist visuell hervorgehoben (brand-Background)
- Wahl persistiert in `localStorage` unter Key `mhdbdb-results-view`
- Toggle-Klick re-rendert nur die Ergebnis-Darstellung — keine erneute Suche

### Pagination

- Tabellen-Ansicht rendert **alle** Treffer auf einmal (kein „Mehr laden")
- Begründung: Sortierung + Export müssen sowieso über alle Treffer operieren; teilweise gerenderte Tabelle wäre inkonsistent zur Datengrundlage
- Performance: 660 Zeilen (max bei „der") rendern in <50 ms; kein virtuelles Scrollen nötig
- Listenansicht behält das bestehende „Mehr laden"-Verhalten (20er-Blöcke) — unverändert

### Export

Zwei Buttons rechts neben/unter der Tabelle:

- **„📋 In Zwischenablage kopieren"** — TSV (Tab-getrennt) via `navigator.clipboard.writeText()`, direkt in Excel/LibreOffice paste-fertig
- **„⬇ CSV herunterladen"** — Komma-getrennt mit Excel-konformem Quoting, UTF-8 mit BOM (`﻿`), Dateiname `mhdbdb-suche-<lemma>-<YYYY-MM-DD>.csv`

Beide Exports respektieren die aktuelle Sortierung. Alle Treffer werden
exportiert, nicht nur sichtbare.

Edge cases:
- Titel mit Komma → CSV-Quoting (`"Der Titel, mit Komma"`)
- Titel mit doppelten Quotes → escapen (`"Er sagte ""hallo"""`)
- `wordCount === 0` → Frequenz-Zelle als `–`, CSV-Wert leer

### Zeilen-Klick

Klick auf `<tr>` öffnet den Reader für den entsprechenden Text — analog zum
Klick auf eine Card in der Listenansicht. Implementation:
- Handler ruft denselben Pfad wie der Card-Click in `app.js:632 ff.`: `openReadingView(result.textId, { lemmaIds: result.lemmaIds || [result.lemmaId] }, this.elements)`.
- Da Reader im 3-Spalten-Layout lebt: Row-Click wechselt `viewMode` auf `'list'`, re-rendert (Karten erscheinen), öffnet dann den Reader. Wenn User Reader schließt, zeigt die Listenansicht den Stand bis zum nächsten Toggle.
- Klick auf Sort-Header-`<button>` darf den Row-Handler **nicht** triggern → `event.stopPropagation()` im Sort-Handler.
- Hover-Visual: `bg-slate-50`, `cursor: pointer`.
- Keyboard-Navigation: `<tr>` ist `tabindex="0"` mit `role="button"` plus `Enter`/`Space`-Handler für Accessibility.

### Sticky Header

Beim Scrollen innerhalb des Tabellen-Containers bleibt der Header sichtbar.

Implementation:
- Tabelle in einem `<div class="overflow-y-auto" style="max-height: calc(100vh - 240px)">`-Wrapper (240 px = Page-Header + Suchbereich + Padding-Puffer, beim Implementieren am echten Layout justieren).
- `position: sticky; top: 0;` auf jedem `<th>` (nicht auf `<thead>` — Firefox unterstützte das lange nicht, Chrome erst ab v91; per-`<th>` ist cross-browser robust seit ~2020).
- `top` ist relativ zum Wrapper, nicht zum Viewport — kollidiert daher *nicht* mit dem Site-Page-Header (der außerhalb des Wrappers liegt).
- `background: white` / `slate-50` auf `<th>` nötig, damit Body-Zeilen beim Scroll nicht durchscheinen.
- `z-index: 10` auf `<th>` als Vorsorge gegen Stacking-Context-Konflikte mit hover-states.

## Voraussetzung — wordCount-Propagation

`wordCount` liegt im Corpus-Index (`scripts/build-corpus-index.py:250`,
validiert in `scripts/validate-indices.py:169`), wird aber von
`assets/js/search/search-engine.js:97-105` **nicht** in das Result-Objekt
projiziert. Aktueller Result-Shape:

```js
{ textId, lemmaId, title, author, genre, matchCount, snippet }
```

Vor Implementation der Tabelle: `search-engine.js:97-105` um `wordCount:
text.wordCount` ergänzen (1-Zeilen-Change). Aggregations-Pfad in
`app.js:454-464` reicht das automatisch per Spread weiter. Alternative
(textId→wordCount-Lookup-Map zur Render-Zeit) wäre weniger sauber: das
Result-Objekt soll semantisch vollständig sein.

## Data Flow

```
search() → search-engine.js results: [{textId, lemmaId, title, author, genre,
                                       matchCount, snippet, wordCount}]
                                      ↑ wordCount nach Propagation-Fix
            ↓
        app.js aggregiert dedupliziert über textId →
            currentResults: [{textId, title, author, genre /* nicht angezeigt */,
                              matchCount, snippet, wordCount, lemmaIds}]
            ↓
        displayResults()
            ↓
        viewMode === 'table' ?
            ↓                           ↓
        renderTable()              loadMoreResults() / createResultCard()
            ↓
        sortResults(currentResults, sortSpec)
            ↓
        HTML <table> in #resultsList (oder eigener Container)
```

## Files Touched

| Datei | Änderung |
|---|---|
| `assets/js/search/search-engine.js` | 1-Zeilen-Fix: `wordCount: text.wordCount` in der Result-Projektion (Zeile 97-105) — siehe Voraussetzung oben |
| `assets/js/app.js` | `+viewMode` + `+sortSpec` state, neue Methoden `renderTable()`, `handleSortClick()`, `copyToClipboard()`, `downloadCSV()`, Branching in `displayResults()`, Layout-Klassen-Toggle (`three-column` ↔ `table-layout`) |
| `korpus.html` | Toggle-Buttons im Results-Header, Export-Buttons-Container, optional leerer `<table>`-Slot (alternativ in JS erstellt) |
| `assets/css/` (Stylesheet je nach Projekt-Konvention) | Neue `.table-layout`-Klasse (Grid-Override auf `grid-cols-1` für `#mainGrid`), sticky-Header-Styles, sort-Indicator-Hover |
| `testing/` | Neuer Playwright-Spec: Toggle umschalten, Sort-Klick verifizieren, CSV-Download per `download`-Event abfangen, Row-Klick → Reader-Öffnen |

Geschätzter Diff: ~150–220 Zeilen neues JS, 10–25 Zeilen HTML, 15–25 Zeilen CSS.

## Non-Functional

- Keine Index-Schema-Änderung
- Keine Build-Skript-Änderung
- Reader-View nicht betroffen
- Existing Listenansicht bleibt unverändert (kein Verhaltensbruch für Bestands-User)
- Accessibility: native `<table>` mit `<thead>` / `<th scope="col">`, Sort-Buttons mit `aria-sort` + lesbarem Sort-Indikator

## Risks

- **Clipboard-API auf HTTP**: Lokaler Dev-Server ist `http://localhost:8080`, Clipboard-API verlangt secure context — Chrome erlaubt das auf `localhost` als Ausnahme, Firefox tut es seit ~2023 auch. Für GitHub-Pages-Production (HTTPS) kein Problem.
- **Sehr lange Treffer-Listen** (max ~667 Texte bei extrem häufigen Wörtern wie „der"): linear render bleibt <100 ms, aber Sort triggert vollständiges Re-Render. Akzeptabel.
- **Layout-Klassen-Mutation auf `#mainGrid`**: Das Umschalten von `three-column` auf `table-layout` beim View-Toggle berührt einen globalen Layout-Container — andere Logik, die auf `three-column` testet, muss ebenfalls geprüft werden. Stand der Recherche: nur `displayResults()` setzt `three-column`. Beim Implementieren ein `grep "three-column"`-Sanity-Check.
- **Reader-Öffnen aus Tabelle**: Wechselt automatisch in den Listen-Modus (siehe „Layout-Modus in Tabellen-Ansicht"). User-Erwartung dafür: in Tabelle steht „Text öffnen" oder ein „→"-Icon als Affordance, damit der Modus-Wechsel nicht überraschend ist. Visualisierungs-Detail für Implementation: dezenter Hint im Tabellen-Footer oder als Icon-Suffix in der ersten Spalte.

## Out of Scope

- Mobile-responsive Tabelle (Projekt ist desktop-only, min 1200 px)
- Excel-Direkt-Export (.xlsx) — CSV reicht für 99% der Use Cases
- Multi-Lemma-Tabelle (würde Spalten-Explosion bedeuten — separate Issue falls gewünscht)
- Persistente Sortier-Spec (User-Default Treffer ↓ ist überraschungsfrei)
- Server-side Pagination (kein Backend)

## Open Questions

Keine — alle Klärungen erledigt.

## Addendum: Integrationswünsche aus der Prüfung (2026-07)

Nach dem Shipping der Tabelle kamen aus Lindas Prüfung drei Wünsche; alle drei
sind umgesetzt:

1. **Gesamttrefferzahl-Ergebniszeile** — `<tfoot>` mit sticky-bottom-Gesamtzeile
   (Summe Treffer, Gesamt-Frequenz/10k, Summe Wörter über alle Ergebnis-Texte);
   zusätzlich steht die Gesamttrefferzahl im Results-Header
   (`N Texte gefunden · M Treffer gesamt`), damit sie auch in der Listenansicht
   sichtbar ist. CSS: `.results-table-total-td` in `korpus.css`.
2. **Types + Wörterbuch-Verweise** — das Lemma-Panel (`#lemmaInfo`) zeigt pro
   resolviertem Lemma (max. 3) die belegten Schreibformen aus dem
   Variants-Dictionary als aufklappbare `<details>`-Liste (MHG-normalisiert,
   gleiche Datenbasis wie die Lemma-Seite) plus asynchron nachgeladene
   MWB-/Lexer-Deep-Links über die Wörterbuchnetz-API (Pattern aus #73,
   `lemma/lemma-page.js`). Neue Methoden: `displayLemmaTypes()`,
   `getVariantFormsFor()` (lazy invertierte Variants-Map),
   `fetchWbnetzLinksInto()`.
3. **Keyness** — neue sortierbare Spalte „Keyness (LL)": signierte
   Log-Likelihood (Dunning 1993) der Trefferfrequenz im Text gegen den Rest des
   **Gesamtkorpus** (alle Texte, unabhängig von der Auswahl — gleiche Referenz
   wie Lindas naming-analysis). Werte ≥ 10,83 (p<0,001, df=1) werden fett/brand
   markiert (= Schlüsselwort des Textes); Erklärungszeile unter der Tabelle.
   Spalte ist in TSV-/CSV-Export enthalten; die Gesamtzeile wird bewusst NICHT
   exportiert (Summenzeilen stören Weiterverarbeitung in Excel/R).
