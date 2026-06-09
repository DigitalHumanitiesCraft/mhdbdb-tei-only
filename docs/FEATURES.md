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

### Text Selection Interface

Include/exclude specific texts from search corpus.

**How it works:**
- Click button to open selection panel
- See all texts with checkboxes (all checked by default)
- Filter by title, sigle, or author
- Bulk actions: "Alle auswählen" / "Keine auswählen"
- Search respects selected texts

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

### TEI File Caching

Cache large TEI files in browser storage for faster subsequent loads.

**How it works:**
- Every opened TEI file is cached in IndexedDB after first parse (no size threshold)
- 30-day expiration (expired entries auto-removed on read and via cleanup; caches read-only corpus TEI files)
- Subsequent loads ~100-200ms vs 3-5 seconds

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

Corpus-wide text analysis using pre-built indexes. Neun Werkzeuge (acht Playground-Einträge; Multi-Lemma bietet Dokument- und Proximity-Modus), alle direkt im Results-Panel als in-place Form + Body (außer Multi-Lemma als Modal).

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

**Text-Statistiken (#89):**
- Pro Text: Token-Count, Lemma-Diversität (unique / total), Hapax-Rate, durchschnittliche Lemma-Frequenz
- Korpus-Übersicht als Tabelle, sortierbar
- Stilistik-Indikator: hohe Lemma-Diversität bei knappen Texten = lexikalisch reich

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

Consistent search behavior across all 14 entry points via Middle High German character normalization.

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
- Scans all 43,754 lemmata for shared concept references (pre-built `sense.conceptIds` in the authority index, extracted at build time from `<sense>`/`<ptr target="concepts.xml#...">`)
- Ranks by concept overlap with the current lemma
- Displays top 50 as clickable chip links
- Performance: client-side full scan over all lemmata (sub-100 ms in practice)

**Use cases:**
- Explore semantic neighborhoods (e.g., from "minne" discover related terms for love, devotion, affection)
- Navigate between conceptually related lemmata without knowing the exact term

---

For technical implementation, see [ARCHITECTURE.md](ARCHITECTURE.md).
For data structures, see [DATA-MODEL.md](DATA-MODEL.md).
For development workflow, see [DEVELOPMENT.md](DEVELOPMENT.md).
