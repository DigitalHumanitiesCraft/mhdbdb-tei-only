# Features

This document describes user-facing functionality of the MHDBDB TEI Repository, organized by interface (Main Site vs Playground).

## Main Site Features

The main site provides a streamlined interface optimized for students and general users.

### Single Lemma Search

Search for Middle High German words across the corpus with automatic normalization and variant resolution.

**How it works:**
- User enters search term
- System normalizes MHG characters (â→a, ô→o, ü→ue)
- Resolves orthographic variants (e.g., "brot", "brott" → "brôt")
- Searches across selected texts
- **Multi-lemma disambiguation:** When search resolves to multiple lemmata, results are deduplicated by text with all matched lemmata displayed
- Returns results with match counts aggregated across lemmata

**Visual design:**
- Blue info box showing all matched lemmata as badges
- White result cards showing title, sigle, author, genre
- Match count with lemma indicator (e.g., "2399 Treffer (2 Lemmata)")
- Auto-scroll to results with offset for sticky header

### KWIC-Belege in den Suchergebnissen (#129)

Pro Treffer-Text ausklappbare Keyword-in-Context-Konkordanz mit Zeilenangaben (Vorschlag K.M. Schmidt).

**How it works:**
- "Belege anzeigen" in der Ergebnis-Karte (Listenansicht) bzw. Chevron-Spalte (Tabellenansicht)
- TEI wird on-demand geladen (über den Reader-Cache), `assets/js/search/kwic-service.js` extrahiert die Belegstellen
- Kontextfenster konfigurierbar (5/10/15/20 Wörter je Seite, Default 10)
- Zeilenreferenz je Beleg: Vers (`<l n>`) vor Prosazeile (`<lb n>`) vor Seite (`<pb n>`)
- Anzeige-Cap 100 Belege pro Text (Gesamtzahl wird ausgewiesen)
- Klick auf einen Beleg öffnet die Leseansicht an genau dieser Fundstelle (`targetPosition`)
- Positionszählung in Parität zu CONTRACTS §B (nur `<w>` mit `@lemmaRef`); Treffer-Match exakt per `lemmaRefMatchesId` (§B.1)
- **Belege-Export (#203):** Button „Belege (CSV)" im Panel-Kopf exportiert ALLE Fundstellen des Texts (ohne Anzeige-Cap, aktuelle Kontextbreite) als CSV (UTF-8 BOM): Spalten `Vers/Zeile | Kontext davor | Keyword | Kontext danach`; Dateiname `mhdbdb-belege-<lemma>-<sigle>-<datum>.csv`

### Tabellenansicht der Suchergebnisse (#114)

Umschaltbare Ergebnis-Darstellung Liste ↔ Tabelle für die Frage „wie verteilt sich ein Lemma über den Korpus" (Userwunsch aus der alten MHDBDB).

**How it works:**
- Toggle im Results-Header, Wahl persistiert in `localStorage` (`mhdbdb-results-view`)
- Sortierbare Spalten: Titel (mit Sigle-Präfix), Autor*in, Treffer, Frequenz/10k Wörter, Keyness (LL), Wörter – plus Belege-Spalte (KWIC #129)
- Results-Header zeigt `N von X ausgewählten Texten · M Treffer gesamt` (auch in der Listenansicht; X = Suchraum zum Suchzeitpunkt, #204)
- **Gesamtzeile** (sticky `<tfoot>`): Summe Treffer, Gesamt-Frequenz, Summe Wörter über alle Ergebnis-Texte
- **Keyness (LL):** signierte Log-Likelihood (Dunning 1993) der Trefferfrequenz im Text gegen den Rest des Gesamtkorpus; Werte ≥ 10,83 (p<0,001) fett/brand markiert = Schlüsselwort des Textes (Referenz: Lindas naming-analysis). Referenzkorpus sind immer alle Texte des Korpus-Index, unabhängig von der Textauswahl; Kontingenztafel und Signierung normativ in [CONTRACTS §H.1](CONTRACTS.md#h1-keyness-signed-log-likelihood-114)
- **Types + Wörterbuch-Links:** das Lemma-Panel zeigt pro resolviertem Lemma (max. 3) die Schreibformen aus dem Variants-Dictionary (aufklappbar; MHG-normalisierte Suchformen, nicht Original-Graphien – so beschriftet) plus asynchron geladene Deep-Links in fünf Wörterbücher (MWB, Lexer, Lexer-Nachträge, Benecke/Müller/Zarncke, Findebuch) über den geteilten, session-gecachten Client `assets/js/lib/woerterbuchnetz.js` (#258, CONTRACTS §D.2). Die Sigle steht einmal je Wörterbuch und trägt den ausgeschriebenen Titel als Tooltip; je Wörterbuch werden bis zu drei Einträge verlinkt, mit grammatischer Angabe zur Unterscheidung der Homographen
- Export: TSV-Clipboard („Kopieren") + CSV-Download (UTF-8 BOM, RFC-4180-Quoting), respektiert aktuelle Sortierung; Gesamtzeile wird bewusst nicht exportiert
- Row-Klick öffnet den Reader (wechselt automatisch auf Listen-Layout; localStorage-Präferenz bleibt `table`)

### Text Selection Interface

Include/exclude specific texts from search corpus.

**How it works:**
- Click button to open selection panel
- See all texts with checkboxes (all checked by default)
- Filter by title, sigle, or author
- Bulk actions: "Alle auswählen" / "Keine auswählen" / "Nur diese" (nur gefilterte)
- Search respects selected texts
- **Filter ≠ Auswahl abgesichert (#204):** Der Filter blendet nur die Liste aus, ändert die Auswahl nicht. Wenn bei aktivem Filter eine breitere Auswahl durchsucht wurde, erscheint über den Ergebnissen ein Hinweis mit One-Click-Korrektur („Nur die M gefilterten Texte durchsuchen"); die 0-Treffer-Box benennt Begriff + Suchraum („0 Treffer für ‚X' in N ausgewählten Texten")

**Use cases:**
- Genre-specific search (select only mystical prose)
- Author-specific search (select all Meister Eckhart works)
- Comparative analysis across selected authors

### Reading View

Full-text immersive reader with multi-lemma highlighting and rich metadata.

**Key features:**
- **Multi-lemma highlighting:** Up to 5 lemmas with distinct colors (red, blue, green, yellow, purple)
- **Rich metadata panel:** Work details, author info, bibliographic references
- **Edition navigation:** Navigate between related editions (sigles) of same work while preserving highlights
- **TEI structural rendering:** Full support for structural elements (headings, divisions, stanzas, page/column breaks, caesuras, editor insertions)
- **Wikidata integration:** Automatic image fetching with attribution
- **Dual identifiers:** Separate GND/Wikidata for work vs author
- **Context navigation:** Prev/next buttons to jump between occurrences
- **Zum Textanfang (#138):** Runder Sprung-Button unten rechts, sobald der Panelkopf aus dem Viewport gescrollt ist; springt zurück zu Titel und Metadaten, nicht zum Seitenanfang
- **Verszählung pro Zählungsbereich (#138):** Die sichtbare Randnummerierung setzt bei jedem `<div>` wieder mit der 1 ein, das eine eigene **durchlaufende** Zählung bei `n="1"` beginnt. Kriterium sind zwei Bedingungen: die erste numerische `<l>` trägt `n="1"`, und die 1 kommt im `<div>` genau einmal vor. Zeilen eines eingehängten Parallelzeugen (`div[@type="parallel"]` innerhalb eines anderen `<div>`) zählen dabei nicht mit: jeder Zeuge wird nur an seinen eigenen Zeilen gemessen (#250, siehe unten). Von 6.789 `<div>`s im Korpus erfüllen 2.661 die erste Bedingung, davon qualifizieren **1.492 in 137 Texten** (897 `chapter`, 252 `song`, 159 ohne `@type`, 156 `section`, 21 `parallel`, 7 `number`). Sichtbar werden dadurch **1.352 zusätzliche Randnummern in 49 Texten**. Größter Fall ist PZ (Parzival) mit +826, gefolgt von FR3 (+136), CHH (+53), TKR (+40) und HUG (+39, Julias Ausgangsfall). Grundlage ist `python scripts/audit/count-verse-numbering-resets.py`, das die Render-Reihenfolge nachbaut und „mit Reset" gegen „ohne Reset" vergleicht; die Zeugentrennung ist dort noch nicht nachgezogen, das Skript weist deshalb weiterhin die Werte davor aus (1.473 qualifizierende, 1.333 zusätzliche, FR3 +117).

  **Zeugentrennung (#250, Stand 2026-07-31):** Seit dem Frauenlob-Umbau (#236) sitzt in FR3 eine `div[@type="parallel"]` innerhalb der `div[@type="section"]` des Basiszeugen. Beide Zeugen beginnen bei `n="1"`, der Teilbaum der `section` enthielt damit zwei Einsen, die `section` fiel durch die zweite Bedingung, und die sichtbare 1 wanderte vom Basiszeugen zum Parallelzeugen. Betroffen waren **19 der 127** FR3-`section`s. Seit der Zeugentrennung bekommt der Basiszeuge seine 1 zurück und der Parallelzeuge behält seine eigene. Die Messung über alle 667 Texte zeigt den Effekt ausschließlich in FR3: 19 `section`s qualifizieren zusätzlich, keine einzige verliert ihre Qualifikation, die 21 qualifizierenden `parallel`-divs bleiben unverändert. DES2 und PKP haben ebenfalls verschachtelte `parallel`-divs und ändern sich nicht.

  Die zweite Bedingung ist der eigentliche Schutz: Texte mit **strophenlokaler** Zählung innerhalb eines `<div>` bekommen bewusst keinen Anker. Sie verwirft korpusweit 1.169 `<div>`s in 84 Texten und verhindert damit 1.007 unmotivierte Randeinsen. NLA (Nibelungenlied Hs. A) ist der Musterfall: 38 untypisierte `<div>`s, in denen jede Strophe wieder bei 1 beginnt und die mangels `@type`/`@n` gar keine Überschrift rendern; ohne die Bedingung bekäme der Text genau 38 zusätzliche Randeinsen, also die #127-Regression über `<div>` statt über `<lg>`. NBB ist von der Änderung strukturell gar nicht berührt, weil der Text keine `<div>`-Elemente enthält
- **URL parameters:** `?textId=ABG&lemmaIds=879,7532&position=310`
- **Ausschnitts-Kontext (#134):** Texte mit `biblScope unit="verse"` im Header (Ausschnitte eines Gesamtwerks, z. B. AK aus der Steirischen Reimchronik) zeigen einen sichtbaren Banner über dem Text sowie eine „Ausschnitt"-Metadaten-Sektion (Ausschnitt/Gesamtwerk/Versbereich/Kontext); siehe TEI-MODEL.md §2.1
- **Editorische Eingriffe (#250):** Aufklappbarer Metadaten-Abschnitt mit den Angaben aus `<editorialDecl>` des Texts, in Dokumentreihenfolge. Er trägt den Hinweis, dass für Zitate die gedruckte Ausgabe maßgeblich ist, wo die MHDBDB in die Textgestalt eingegriffen hat. Deutlichster Fall ist FR3: dort sind die beiden Anhänge der Edition vertauscht (Anhang I als XV. gezählt) und ein Verszählungsfehler der Herausgeber korrigiert. Nicht angezeigt wird das Repository-Boilerplate über die Auflösung lokaler Dateireferenzen, das 666 Header wortidentisch je auf Deutsch und Englisch führen; nach diesem Filter bleiben in 664 Texten 1 bis 42 Absätze, in CEFB, GWTK und KVO keiner, dort entfällt der Abschnitt. Zahlen reproduzierbar über `python scripts/audit/count-editorial-notes-and-div-heads.py`
- **Abschnittslabel unter eigener Überschrift (#250):** Trägt ein typisiertes `<div>` einen eigenen `<head>`, wird das synthetische Label („Lied 5", „Rezept 1") zur übergeordneten Zeile der Überschrift statt zur gleichrangigen zweiten Überschrift daneben. Betroffen sind 1.097 der 4.676 typisierten `<div>`s in 35 Texten (403 `song`, 320 `chapter`, 301 `recipe`, 72 `number`, 1 `section`), angeführt von NEI und NEIC (je 124), WZB (97) und KBL4/SUB1 (je 66). Das Label bleibt sichtbar, weil in keinem dieser Fälle der `<head>` die Nummer aus `@n` mitführt (AC1: `n="1"` und „das i capitel", ABS: `n="1"` und „basteten .") und 932 der divs ein `@n` haben; es zu unterdrücken hieße, die einzige sichtbare Zählung des Abschnitts zu entfernen

**TEI elements rendered:**
- Text structure: `<head>`, `<p>`, `<div>`, `<lg>` (stanzas), `<l>` (verse lines)
- Layout markers: `<pb>` (page breaks), `<lb>` (line breaks), `<cb>` (column breaks)
- Verse elements: `<caesura>` (metrical pauses)
- Editorial markup: `<hi>` (highlighting with @rend), `<supplied>` (editor insertions)
- Special elements: `<num>` (numbers), `<pc>` (punctuation with `@join`)

**Visual design:**
- Side-by-side 3-column grid (search + results + reading)
- Readable serif font with comfortable line height
- Expandable/collapsible metadata sections
- Fixed navigation controls (responsive positioning)
- Distinct visual treatment for verse vs prose (indentation, line breaks)

### Wörterbuch (A–Z-Register) (#117)

Konventionelle Wörterbuch-Einstiegsseite (`woerterbuch.html`) für alle 43.879 Lemma-Seiten.

**How it works:**
- Indexleiste A–Z (+ `#` für Ziffern-Lemmata) mit Eintragszahl pro Buchstabe als Tooltip
- Bucketing über das `normalized`-Feld des Authority-Index (NFD-Fallback für `ë`/`ú`-Anfänge)
- Pagination à 200 Einträge innerhalb des Buchstabens, alphabetisch sortiert (`Intl.Collator('de')`)
- Jeder Eintrag (Lemma + POS-Badge) verlinkt auf die persistente Lemma-Seite `lemma/?id=N`
- Deep-Links über URL-State: `woerterbuch.html?buchstabe=s&seite=3`
- Erreichbar über den Header-Menüpunkt „Wörterbuch" auf allen Seiten

**Namensentscheidung:** „Wörterbuch" statt „Lemmata" (Playground-Fachbegriff) oder „Wortindex" (Alt-MHDBDB; wird im Untertitel der Seite als Brücke erwähnt) – begründet in Issue #117.

### TEI File Caching

Cache large TEI files in browser storage for faster subsequent loads.

**How it works:**
- Every opened TEI file is cached in IndexedDB after first download (no size threshold)
- The first load per session revalidates against the server via conditional GET (ETag / Last-Modified, #151): unchanged files are served from cache after a 304 roundtrip, updated files re-download immediately; repeat loads in the same session skip the network entirely
- Subsequent loads skip the multi-MB transfer (~100-200ms vs 3-5 seconds); network failures, server errors and timeouts fall back to the cached copy

## Playground Features

The playground provides advanced research tools for medievalists and digital humanities researchers.

### Authority File Exploration

Browse and search six controlled vocabularies with consistent interface patterns.

**Person Explorer:**
- Search by author name
- Display: Name, GND/Wikidata links, work count
- Action: View all works by author

**Work Explorer:**
- Search by title, sigle, or author
- Display: Title, sigle, author, genres, GND/Wikidata (work-specific), bibliographic references
- Note: v1.1.0 added separate work identifiers (distinct from author)

**Lemma Explorer:** two named modes, switchable in the header, routed as `#lemmata` and `#lemmata&mode=component`

*Lemma suchen* (default):
- Search by lemma (normalized MHG)
- Display: Lemma, POS, sense count, etymology, full sense definitions with concepts
- Lemma titles link to persistent lemma pages (`/lemma/{id}`)
- Action: Search lemma in corpus

*Wortbestandteil suchen* (#239, word-component search for compounds):
- Searches the lemma list, not the corpus: the result is a vocabulary survey, not a concordance
- Results grouped by where the component sits: word-final (the head of a determinative compound, expanded), word-initial (expanded), word-medial (collapsed by default, most false hits live there)
- Matching runs on the normalized form, display keeps the original. The input additionally resolves through the variants list, which is what lets „wein" reach `wîn` and thus `ôsterwîn`; without that bridge nothing would match, because `normalizeMHG("wein")` is `wein` and `normalizeMHG("ôsterwîn")` is `osterwin`. The header names both forms
- Minimum input length 3, enforced on the bridged form as well
- Selected lemmata (including the base word itself) can be handed to the multi-lemma search as a set
- Two layers. The default is a character scan, which is why „win" also hits `winter`, `gewinnen`, and why the `-swîn` (pig) compounds sit next to the `-wîn` (wine) ones. On top of it, hits whose `lemma.etymology[]` names one of the target lemmata as a morphological component are badged „belegte Wortbildung", and a checkbox narrows the list to those. That data is curated in `lexicon.xml` (`<etym type="morphological">`, 27,166 lemmata or ~62 %) and already ships in the authority index, so the filter needs no new build step. It separates exactly the cases the character scan cannot: `wiltswîn` lists `swîn`, not `wîn`, and `winter` lists nothing. The remaining ~38 % without recorded word formation are reachable only through the character scan, which is why that stays the default
- Group order also drives the 200-per-group cap: badged hits first, then sense count, then alphabetical. A purely alphabetical cut would show an arbitrary prefix for frequent components like `lich`
- Stage 1 to 3 of the regular resolution are untouched (ADR-016)

**Concept Explorer:**
- Search by concept term (German or English)
- Display: Term, hierarchy (broader/narrower), associated lemmata
- Action: Navigate hierarchy, view all lemmata for concept
- Note: v1.1.0 replaced inline truncation with full searchable interface

**Genre Explorer:**
- Search by genre term
- Display: Term, hierarchy (broader genres), associated works
- Action: View all works in genre
- Note: v1.1.0 fixed hierarchy extraction

**Name Explorer:**
- Search by proper name
- Display: Name, related concepts
- Action: View concept relationships

### TEI Text Analysis

Corpus-wide text analysis using pre-built indexes. Zwölf Werkzeuge in zwölf Playground-Einträgen (Multi-Lemma bietet Dokument-, Proximity- und Vers-Modus in einem Eintrag), alle direkt im Results-Panel als in-place Form + Body (außer Multi-Lemma als Modal).

**Multi-Lemma Document Search:**
- Input multiple lemmata (space-separated or one per line)
- Find texts containing ALL lemmata (anywhere in document)
- Automatic variant resolution
- Results: List of matching texts

**Multi-Lemma Proximity Search:**
- Input multiple lemmata
- Set max distance (1-50 words, default 10)
- Find co-occurrences within distance
- Automatic variant resolution
- Results: Context snippets with color-coded highlighting
- Click result → open main site reading view with URL parameters

**Multi-Lemma-Suche „Im selben Vers" (#106 Punkt 8):**
- Kookkurrenz auf ein gemeinsames `<l>` beschränkt (syntaktisch enger als das Wort-Fenster der Proximity-Suche)
- Datenbasis: `lineStarts[]`/`lineEnds[]` aus dem Corpus-Index v4.1.0+, kein neuer Build-Schritt
- Nur Versdichtung (603 von 667 Texten); Prosa wird automatisch übersprungen
- Treffer nennen die Versnummer; Expand + Reader-Deep-Link wie in der Proximity-Suche
- URL-Routing: `#multi-lemma&lemmata=…&mode=verse`

**Lemmasuche nach Versposition (#47.3):**
- Single Lemma + Position-Auswahl (Versanfang / Versende, Default Versende)
- Findet Lemmata, die genau am ersten oder letzten `<w>` einer `<l>` stehen
- Use Case: Reim-Analyse, Versende-Stilistik („wie oft reimt Wolfram auf `minne`?")
- Trefferliste mit Anteil pro Text („54 % aller `minne`-Vorkommen in Tristan stehen am Versende")
- Nur Versdichtungs-Texte (603 von 667, ca. 90 % des Korpus); Prosa wird automatisch übersprungen
- Klick auf Treffer → Reading View mit Highlighting

**Wortfrequenz-Analyse (#88):**
- Top-N Lemmata über das gesamte Korpus oder pro Text
- POS-basierter Stopwort-Filter (DET, ART, POS, PRO, PRP, CCNJ, SCNJ, CNJ, NEG, IPA, VEX, VEM) – entfernt häufige Funktionswörter, hebt inhaltstragende Lemmata hervor
- Absolute oder relative Frequenz
- Sortierung nach Frequenz oder alphabetisch

**Echte Hapaxlegomena (#196):**
- Lemmata (nicht Wortformen) mit korpusweiter Gesamtfrequenz ≤ n (Hapax/Dis/Tris, Default 1) – abzugrenzen von der Text-Hapax-Rate der Text-Statistiken (#89). Zählregel und Filterreihenfolge normativ in [CONTRACTS §H.2](CONTRACTS.md#h2-hapax-legomena-196)
- Datenpfad: ein Aggregations-Durchlauf über `text.lemmata` aller Texte (Pattern Wortfrequenz-Analyse); je Lemma werden die ersten ≤3 Fundorte (`textId` + Wortposition) mitgeführt, Versnummer via Binärsuche über `lineStarts[]`
- **Facetten-Vorrang (einheitlich für alle drei Default-Filter):** Eine explizit in der Wortart-Facette gewählte Wortart hebt den gleichnamigen Filter auf (NAM, NUM, jede Wortart aus `FUNCTION_WORD_POS`); die betroffene Checkbox rendert dann `disabled` und gedimmt. Ohne diese Regel liefert die Facette kommentarlos eine leere Liste
- Filter: Eigennamen ausblenden (NAM, Default an – 28 % der Hapaxe), Zahlwörter ausblenden (Default an – greift nur bei reinem NUM, nicht bei Mehrfach-Wortarten wie `zwispeltic` ADJ/NUM; betrifft 72 der 119 NUM-Hapaxe. Anlass waren die drei Ziffern-Lemmata 42/46/49, die alphabetisch auf den Rängen 1 bis 3 standen, siehe #228), Funktionswörter ausblenden (geteilte `FUNCTION_WORD_POS`-Menge aus word-frequency.js), Wortarten-Facette, Anfangsbuchstaben-Facette (auf `lemma.normalized`)
- Pro Eintrag: Lemma-Link auf die Lemma-Seite, PoS-Badges, Fundort(e) als Reader-Deep-Link (`korpus.html?textId=&lemmaIds=&position=`), Details-Aufklapp mit Konzept-Chips und lazy Wörterbuchnetz-Abgleich (fünf Wörterbücher via geteiltem Client `assets/js/lib/woerterbuchnetz.js`, #258, CONTRACTS §D.2) – beantwortet „echtes mhd. Hapax oder nur Korpus-Hapax?". Der Negativbefund nennt die abgefragten Wörterbücher beim Namen, weil die Deutung „echtes Hapax" genau an dieser Liste hängt
- Lemma-IDs ohne Authority-Eintrag werden mit Badge angezeigt (Kuratierungs-Funde, 99 Stück Stand 2026-07)
- Tab „Beitrag pro Text": Raritäten je Text absolut + pro 1.000 Tokens, sortierbar
- CSV-Export der gefilterten Liste (UTF-8-BOM, Semikolon); Pagination zu 100 Einträgen
- Bewusste Grenze: kein frei wählbares Subkorpus (Hapax relativ zu einer Textauswahl) – Follow-up-Kandidat, siehe Issue #196

**Text-Statistiken (#89, Auswahl-UI #136):**
- Pro Text: Token-Count, Lemma-Diversität (unique / total), Hapax-Rate, durchschnittliche Lemma-Frequenz
- Korpus-Übersicht als Tabelle, sortierbar
- Stilistik-Indikator: hohe Lemma-Diversität bei knappen Texten = lexikalisch reich
- Subset-Bildung: Checkbox je Zeile + Master-Checkbox, „Nur Auswahl anzeigen", Auswahlzähler; Auswahl übersteht Sortieren

**Lemma-Verteilung (#90):**
- Single Lemma → Bar-Chart über alle Texte
- Top-N Bars im Chart, Rest als auklappbare Tabelle
- Absolute oder relative Frequenz (pro 1000 Tokens)
- Klick auf Balken oder Sigle → Reading View mit Highlighting

**Begriffs-Verteilung (#47 R2, mit Autocomplete #113):**
- Single Concept (deutsch, englisch, oder `concept_xxxxx`-ID) → Bar-Chart über alle Texte
- Aggregiert alle Lemmata, deren `senses[*].conceptIds` das Concept enthält
- Datenpfad: concept → senses → lemmata → texts (summiert Vorkommen pro Text)
- Alternative Begriffs-Candidates werden angezeigt (z.B. bei „love" → Intimität + Liebe/Zuneigung)
- Auklappbare „zugeordnete Lemmata"-Sektion zur Validierung der Concept-Selektion
- Klick auf Treffer → Reading View
- **Live-Autocomplete-Dropdown** im Begriffs-Input (max. 8 Suggestions, Pfeil-Navigation, Enter wählt + sucht, Escape schließt) – gleiches Pattern wie DWDS oder Google-Suche

**Textvergleich (#108):**
- Zwei Texte über Dropdown-Menüs auswählen (alle 667 Sigles mit Titel + Autor)
- Drei Lemma-Mengen werden berechnet: Nur in A, in Beiden, Nur in B
- Per Lemma: Frequenz in A, Frequenz in B, absolute Differenz |A−B|
- Sortierung Frequenz / Differenz / Alphabetisch, Lemma-Name-Substring-Filter
- A↔B-Swap-Button für gespiegelte Perspektive
- Datenpfad: reine Set-Ops auf `Object.keys(text.lemmata)`, keine neuen Index-Felder
- Use Cases: „Welche Lemmata teilt PZ mit JT?", „Lehnvers-Indizien (geteilte seltene Lemmata zwischen sonst unverbundenen Texten)", „Lemma-Profile pro Werk"
- Klick auf Frequenz-Zahl öffnet Reading View des jeweiligen Texts mit Highlighting

**Kookkurrenz-Ranking (#107):**
- DWDS-Style „Welche Lemmata stehen am häufigsten bei X?"
- Eingabe-Lemma + Kontextfenster (±3-25 Wörter, Default ±10) → rangierte Tabelle Top-N Partner-Lemmata
- POS-Filter essentiell: Default „Inhaltswörter" (NOM/VRB/ADJ/ADV) verhindert dass Stopwords (der/und/ich/daz/er) die Liste dominieren; auch „nur Nomen", „nur Verben", „nur Adjektive", oder „alle"
- Datenpfad: Window-Scan über `text.words[pos±w]` für jede Position in `text.lemmata[X]`
- Async-Chunking (MessageChannel-Yield alle 30ms) hält UI responsiv auch für häufige Lemmata; POS-Filter-Switch ohne Re-Compute (rawCounts gecacht)
- Use Cases: „Was steht typisch bei `êre`?" (→ tuon, sprechen, got, herre), „Welche Adjektive begleiten `wîp`?"
- Klick auf Partner → Multi-Lemma-Suche mit beiden Lemmata + aktueller Distanz vorbefüllt; Klick auf Lemma → Lemma-Page

**Reim-Wörterbuch (#106, Minimalvariante):**
- „Welche Lemmata reimen sich auf X?" – Eingabe-Lemma + optionaler Text/Autor-Filter (Sigle exakt oder Titel/Autor-Substring) → rangierte Tabelle der Reimpartner-Lemmata
- Datenpfad: Scan über `text.lineEnds[]` (Corpus-Index v4.1.x); Kandidaten sind die Lemmata der unmittelbar benachbarten Versenden (±1 Vers, Paarreim-Annahme)
- Reim-Heuristik: 3-Letter-Suffix-Match der MHG-normalisierten Lemma-Formen (2-Letter nur, wenn beide Formen ≤4 Zeichen – findet `wîp : lîp` und `tac : slac`, ohne dass Kurzwörter wie `en`/`dô` lange Ziel-Lemmata fluten); identischer Reim (Lemma auf sich selbst) wird nur einfach gezählt. Vollständige Zählregel samt der Asymmetrie zwischen Ziel- und Partnerseite: [CONTRACTS §H.3](CONTRACTS.md#h3-rhyme-dictionary-106)
- Pro Partner: Reimpaar-Zahl, Texte als Sigle-Chips mit Paarzahl, „→ Belege" klappt die gezählten Verspaare direkt in der Tabelle auf: beide Verse als vollständiger `<l>`-Inhalt (lazy per TEI-Fetch; Highlight-Mapping über CONTRACTS-§B-Positionszählung, damit `lineEnds[]`-Positionen auf die richtigen Wörter zeigen), markierte Reimwörter, Versangabe aus `<l n>`, Reader-Deep-Link (`position=`); paginiert zu 10, Cap 1000 gespeicherte Verspaare pro Partner. (Vorher nur Link in den Nähe-Modus der Multi-Lemma-Suche mit Distanz 15 – zeigte auch Kookkurrenzen abseits der Versenden, also keine Reime; KZW-Report 2026-07-09)
- Async-Chunking + Abort-Token (Pattern wie #107), Prosa (leere `lineEnds`) wird übersprungen
- Bewusste Grenzen der Minimalvariante (Issue #106): lemma- statt token-basiert (reimende Flexionsform kann abweichen), strukturell statt phonetisch, Kreuzreime (ABAB) entgehen dem ±1-Scan; Original-Token-Variante bräuchte Index-Erweiterung (`lineEndWords[]`), phonetische Klassifikation ist #109-Folgearbeit

**Versendings-Profil (#106 Punkt 2):**
- Top-N häufigste Lemmata am Versende – Scope wählbar: Gesamtkorpus, Autor*in (optgroup) oder Einzeltext
- Datenpfad: `text.words[lineEnds[i]]` je Vers (Corpus-Index v4.1.x), kein neuer Build-Schritt
- Spalten: Versende-Belege (absolut), Anteil an allen Versenden des Scopes, **Reim-Druck** = Anteil der Vorkommen des Lemmas am Versende vs. gesamt (#106 Punkt 3: hoher Wert = reimgetrieben, niedriger = semantisch motiviert). Zähler und Nenner sind beide scope-lokal und stammen aus verschiedenen Index-Feldern, was die Kennzahl verzerren würde, sobald es Tokens mit Mehrfach-Lemmareferenz gibt (heute keine): [CONTRACTS §H.4](CONTRACTS.md#h4-verse-ending-profile-and-reim-druck-106-points-2-and-3)
- Funktionswort-Filter (gleiche POS-Menge wie Wortfrequenz/Hapax), Lemma-Links auf die Lemma-Seiten
- Nur Versdichtung (leere `lineEnds` -> übersprungen); Use Case aus dem Issue: Reim-Stil-Vergleich Wolfram/Hartmann/Gottfried

**Erweiterte Figurenbezeichnungen (#59, Beta):**
- Kuratierte Bezeichnungspraktiken jenseits des Eigennamens für vier Werke (ENE, IW, ROL, TRO) aus dem Dissertationsprojekt Naming-analysis von Linda Beutel-Thurow
- Auswahl Werk → Figur (nach Belegzahl sortiert) → Terme in drei Kategorien: Eigennamen, Antonomasien („der rîter" für Iwein), Epitheta („der küene")
- Pro Term: Häufigkeit + aufklappbare Belegstellen mit Versangabe, Nennphrase und Sprecher (Erzähler / Figurenrede mit nennender Figur / Selbstnennung)
- Term-Filter MHG-normalisiert („tore" findet `tôre`)
- Reader-Deep-Links für ROL und TRO: Versangaben verlinken via `korpus.html?textId=<SIG>&verse=<n>` in die Leseansicht (Sprung zur Verszeile mit Hervorhebungs-Puls). Die Verszählung dieser beiden Werke ist mit der MHDBDB-TEI-Zählung deckungsgleich (Linda Beutel-Thurow, #59-Kommentar 2026-06-11; TRO-Stichprobe 4/4 verifiziert). ENE und IW folgen abweichenden Editionszählungen und bleiben bewusst link-los
- Sichtbare Attribution im Modul: Beutel-Thurow, L. (2026). Naming-analysis (v0.1.0-beta), DOI 10.5281/zenodo.18770138, CC BY-NC-SA 4.0
- Datenbasis: `data/naming-index.json.gz` (~110 KB), gebaut via `scripts/ingest/naming/01-fetch-and-build-index.py`, lazy-geladen ohne IndexedDB-Cache

**Cross-platform workflow:**
1. Perform analysis in playground
2. Find interesting result (co-occurrence, peak in distribution, top lemma at Versende, etc.)
3. Click result
4. Opens main site reading view with relevant lemmata highlighted
5. Auto-scroll to exact position

### Shareable URLs

All playground views are bookmarkable and shareable via hash-based URLs.

**How it works:**
- Each view has a URL fragment (e.g., `#authors`, `#lemmata`, `#multi-lemma`)
- Search state preserved via `q` parameter (e.g., `#lemmata&q=minne`)
- Detail drill-down via `show` parameter
- Multi-lemma search fully serialized: `#multi-lemma&lemmata=minne,êre&mode=proximity&dist=10`
- Sharing a URL reproduces the exact view state

### Search Normalization

Consistent search behavior across all 18 entry points via Middle High German character normalization.

**Normalization rules:**
- Long vowels: â→a, ê→e, î→i, ô→o, û→u
- Umlauts: ä→ae, ö→oe, ü→ue; Breve-Umlaute der Wenzelsbibel: ŏ→oe, ŭ→ue (#224)
- Ligatures: æ→ae, œ→oe

**Implementation:**
- Shared utility: `assets/js/lib/text-normalizer.js`
- Applied to all search inputs and indexed data
- Enables consistent matching across orthographic variations

**Note:** Normalization handles **character variations**, variants.xml handles **spelling variations**. Both used together for comprehensive search coverage.

## Lemma Page Features

Persistent pages for individual lemmata, accessible at `/lemma/{numericId}`. These URLs are stable external identifiers used by Wörterbuchnetz, MWB, and Wikidata (P9351).

### Wörterbücher (#73, erweitert in #258)

Abschnitt „Wörterbücher" mit Deep-Links in fünf mittelhochdeutsche Wörterbücher des Wörterbuchnetzes: MWB, Lexer, Lexer-Nachträge, Benecke/Müller/Zarncke und Findebuch. Die Lemma-Seite ist die Vertiefungsseite und darum die einzige Oberfläche, die die Sigle ausschreibt: je Wörterbuch eine Überschrift mit vollem Titel, darunter alle Einträge als Karten mit grammatischer Angabe (ungekürzt, anders als im kompakten Suchpanel). Wörterbücher ohne Treffer erscheinen nicht.

### Similar Lemmata

Concept-based similarity section on each lemma page.

**How it works:**
- Scans all 43,879 lemmata for shared concept references (pre-built `sense.conceptIds` in the authority index, extracted at build time from `<sense>`/`<ptr target="concepts.xml#...">`)
- Ranks by concept overlap with the current lemma
- Displays top 50 as clickable chip links
- Performance: client-side full scan over all lemmata (sub-100 ms in practice)

**Use cases:**
- Explore semantic neighborhoods (e.g., from "minne" discover related terms for love, devotion, affection)
- Navigate between conceptually related lemmata without knowing the exact term

## JSON API for Programmatic Access (#45)

Static JSON API under `/api/`, served directly by GitHub Pages – stable, citable URLs for every authority record and text.

**What it offers:**
- Root manifest at [`api/index.json`](https://dhcraft.org/mhdbdb-tei-only/api/index.json) listing all collections with counts
- Individual records (`api/persons/person_445.json`, `api/works/work_WZB.json`, ...) plus a summary `index.json` per collection (persons, works, concepts, genres, names, texts)
- Lemmata as a single bundle (`api/lemmata/index.json`, 43,879 full records) instead of 43k individual files
- Every file carries its license (`CC BY-NC-SA 4.0`)

**Documentation:** human-readable docs page at [`api/index.html`](https://dhcraft.org/mhdbdb-tei-only/api/index.html) (German), linked from `hilfe-daten.html`.

**Target audience:** external projects that already reference MHDBDB lemma pages (MWB, Wörterbuchnetz, Wikidata P9351) and researchers who want machine-readable access without cloning the repo or parsing the gzipped indexes.

---

For technical implementation, see [ARCHITECTURE.md](ARCHITECTURE.md).
For data structures, see [DATA-MODEL.md](DATA-MODEL.md).
For development workflow, see [DEVELOPMENT.md](DEVELOPMENT.md).
