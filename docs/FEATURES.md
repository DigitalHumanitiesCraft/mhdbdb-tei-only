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
- Sortierbare Spalten: Titel (mit Sigle-Präfix), Autor*in, Treffer, Frequenz/10k Wörter, Keyness (LL), Wörter — plus Belege-Spalte (KWIC #129)
- Results-Header zeigt `N von X ausgewählten Texten · M Treffer gesamt` (auch in der Listenansicht; X = Suchraum zum Suchzeitpunkt, #204)
- **Gesamtzeile** (sticky `<tfoot>`): Summe Treffer, Gesamt-Frequenz, Summe Wörter über alle Ergebnis-Texte
- **Keyness (LL):** signierte Log-Likelihood (Dunning 1993) der Trefferfrequenz im Text gegen den Rest des Gesamtkorpus; Werte ≥ 10,83 (p<0,001) fett/brand markiert = Schlüsselwort des Textes (Referenz: Lindas naming-analysis)
- **Types + Wörterbuch-Links:** das Lemma-Panel zeigt pro resolviertem Lemma (max. 3) die Schreibformen aus dem Variants-Dictionary (aufklappbar; MHG-normalisierte Suchformen, nicht Original-Graphien — so beschriftet) plus asynchron geladene MWB-/Lexer-Deep-Links über den geteilten, session-gecachten Client `assets/js/lib/woerterbuchnetz.js` (CONTRACTS §D.2)
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
- **URL parameters:** `?textId=ABG&lemmaIds=879,7532&position=310`
- **Ausschnitts-Kontext (#134):** Texte mit `biblScope unit="verse"` im Header (Ausschnitte eines Gesamtwerks, z. B. AK aus der Steirischen Reimchronik) zeigen einen sichtbaren Banner über dem Text sowie eine „Ausschnitt"-Metadaten-Sektion (Ausschnitt/Gesamtwerk/Versbereich/Kontext); siehe TEI-MODEL.md §2.1

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

**Namensentscheidung:** „Wörterbuch" statt „Lemmata" (Playground-Fachbegriff) oder „Wortindex" (Alt-MHDBDB; wird im Untertitel der Seite als Brücke erwähnt) — begründet in Issue #117.

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

**Lemma Explorer:**
- Search by lemma (normalized MHG)
- Display: Lemma, POS, sense count, etymology, full sense definitions with concepts
- Lemma titles link to persistent lemma pages (`/lemma/{id}`)
- Action: Search lemma in corpus

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

Corpus-wide text analysis using pre-built indexes. Zehn Werkzeuge in zehn Playground-Einträgen (Multi-Lemma bietet Dokument- und Proximity-Modus in einem Eintrag), alle direkt im Results-Panel als in-place Form + Body (außer Multi-Lemma als Modal).

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

**Lemmasuche nach Versposition (#47.3):**
- Single Lemma + Position-Auswahl (Versanfang / Versende, Default Versende)
- Findet Lemmata, die genau am ersten oder letzten `<w>` einer `<l>` stehen
- Use Case: Reim-Analyse, Versende-Stilistik („wie oft reimt Wolfram auf `minne`?")
- Trefferliste mit Anteil pro Text („54 % aller `minne`-Vorkommen in Tristan stehen am Versende")
- Nur Versdichtungs-Texte (603 von 667, ca. 90 % des Korpus); Prosa wird automatisch übersprungen
- Klick auf Treffer → Reading View mit Highlighting

**Wortfrequenz-Analyse (#88):**
- Top-N Lemmata über das gesamte Korpus oder pro Text
- POS-basierter Stopwort-Filter (DET, ART, POS, PRO, PRP, CCNJ, SCNJ, CNJ, NEG, IPA, VEX, VEM) — entfernt häufige Funktionswörter, hebt inhaltstragende Lemmata hervor
- Absolute oder relative Frequenz
- Sortierung nach Frequenz oder alphabetisch

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
- **Live-Autocomplete-Dropdown** im Begriffs-Input (max. 8 Suggestions, Pfeil-Navigation, Enter wählt + sucht, Escape schließt) — gleiches Pattern wie DWDS oder Google-Suche

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
- „Welche Lemmata reimen sich auf X?" — Eingabe-Lemma + optionaler Text/Autor-Filter (Sigle exakt oder Titel/Autor-Substring) → rangierte Tabelle der Reimpartner-Lemmata
- Datenpfad: Scan über `text.lineEnds[]` (Corpus-Index v4.1.x); Kandidaten sind die Lemmata der unmittelbar benachbarten Versenden (±1 Vers, Paarreim-Annahme)
- Reim-Heuristik: 3-Letter-Suffix-Match der MHG-normalisierten Lemma-Formen (2-Letter nur, wenn beide Formen ≤4 Zeichen — findet `wîp : lîp` und `tac : slac`, ohne dass Kurzwörter wie `en`/`dô` lange Ziel-Lemmata fluten); identischer Reim (Lemma auf sich selbst) wird nur einfach gezählt
- Pro Partner: Reimpaar-Zahl, Texte als Sigle-Chips mit Paarzahl, „→ Belege" klappt die gezählten Verspaare direkt in der Tabelle auf: beide Verse als vollständiger `<l>`-Inhalt (lazy per TEI-Fetch; Highlight-Mapping über CONTRACTS-§B-Positionszählung, damit `lineEnds[]`-Positionen auf die richtigen Wörter zeigen), markierte Reimwörter, Versangabe aus `<l n>`, Reader-Deep-Link (`position=`); paginiert zu 10, Cap 1000 gespeicherte Verspaare pro Partner. (Vorher nur Link in den Nähe-Modus der Multi-Lemma-Suche mit Distanz 15 — zeigte auch Kookkurrenzen abseits der Versenden, also keine Reime; KZW-Report 2026-07-09)
- Async-Chunking + Abort-Token (Pattern wie #107), Prosa (leere `lineEnds`) wird übersprungen
- Bewusste Grenzen der Minimalvariante (Issue #106): lemma- statt token-basiert (reimende Flexionsform kann abweichen), strukturell statt phonetisch, Kreuzreime (ABAB) entgehen dem ±1-Scan; Original-Token-Variante bräuchte Index-Erweiterung (`lineEndWords[]`), phonetische Klassifikation ist #109-Folgearbeit

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

Consistent search behavior across all 16 entry points via Middle High German character normalization.

**Normalization rules:**
- Long vowels: â→a, ê→e, î→i, ô→o, û→u
- Umlauts: ä→ae, ö→oe, ü→ue
- Ligatures: æ→ae, œ→oe

**Implementation:**
- Shared utility: `assets/js/lib/text-normalizer.js`
- Applied to all search inputs and indexed data
- Enables consistent matching across orthographic variations

**Note:** Normalization handles **character variations**, variants.xml handles **spelling variations**. Both used together for comprehensive search coverage.

## Lemma Page Features

Persistent pages for individual lemmata, accessible at `/lemma/{numericId}`. These URLs are stable external identifiers used by Wörterbuchnetz, MWB, and Wikidata (P9351).

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

Static JSON API under `/api/`, served directly by GitHub Pages — stable, citable URLs for every authority record and text.

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
