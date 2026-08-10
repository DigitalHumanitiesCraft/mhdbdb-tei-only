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

### KWIC concordance in the search results (#129)

An expandable keyword-in-context concordance per matching text, with line references (suggested by K.M. Schmidt).

**How it works:**
- „Belege anzeigen" in the result card (list view) or the chevron column (table view)
- The TEI is loaded on demand (through the reader cache), `assets/js/search/kwic-service.js` extracts the citations
- Configurable context window (5/10/15/20 words per side, default 10)
- Line reference per citation: verse (`<l n>`) before prose line (`<lb n>`) before page (`<pb n>`)
- Display cap of 100 citations per text (the total is stated)
- Clicking a citation opens the reading view at exactly that occurrence (`targetPosition`)
- Position counting in parity with CONTRACTS §B (only `<w>` with `@lemmaRef`); hit matching exact via `lemmaRefMatchesId` (§B.1)
- **Citation export (#203):** the button „Belege (CSV)" in the panel header exports ALL occurrences of the text (no display cap, current context width) as CSV (UTF-8 BOM): columns `Vers/Zeile | Kontext davor | Keyword | Kontext danach`; file name `mhdbdb-belege-<lemma>-<sigle>-<datum>.csv`

### Table view of the search results (#114)

A switchable result presentation, list against table, for the question „how does a lemma spread across the corpus" (a user request carried over from the old MHDBDB).

**How it works:**
- Toggle in the results header, the choice persists in `localStorage` (`mhdbdb-results-view`)
- Sortable columns: title (with sigle prefix), author, hits, frequency per 10k words, keyness (LL), words, plus the citation column (KWIC #129)
- The results header shows `N von X ausgewählten Texten · M Treffer gesamt` (in the list view as well; X is the search space at the time of the search, #204)
- **Total row** (sticky `<tfoot>`): sum of hits, overall frequency, sum of words across all result texts
- **Keyness (LL):** signed log-likelihood (Dunning 1993) of the hit frequency in the text against the rest of the whole corpus; values ≥ 10.83 (p<0.001) are marked bold and in the brand color, meaning a keyword of that text (reference: Linda's naming-analysis). The reference corpus is always every text of the corpus index, independent of the text selection; contingency table and signing are normative in [CONTRACTS §H.1](CONTRACTS.md#h1-keyness-signed-log-likelihood-114)
- **Types and dictionary links:** for each resolved lemma (max. 3) the lemma panel shows the spellings from the variants dictionary (expandable; MHG-normalized search forms, not original graphies, and labelled as such) plus asynchronously loaded deep links into five dictionaries (MWB, Lexer, Lexer-Nachträge, Benecke/Müller/Zarncke, Findebuch) through the shared, session-cached client `assets/js/lib/woerterbuchnetz.js` (#258, CONTRACTS §D.2). The sigle appears once per dictionary and carries the full title as a tooltip; up to three entries are linked per dictionary, with a grammatical note to tell homographs apart
- Export: TSV to clipboard („Kopieren") plus CSV download (UTF-8 BOM, RFC 4180 quoting), respecting the current sorting; the total row is deliberately not exported
- Clicking a row opens the reader (switching to the list layout automatically; the localStorage preference stays `table`)

### Text Selection Interface

Include/exclude specific texts from search corpus.

**How it works:**
- Click button to open selection panel
- See all texts with checkboxes (all checked by default)
- Filter by title, sigle, or author
- Bulk actions: „Alle auswählen" / „Keine auswählen" / „Nur diese" (the filtered ones only)
- Search respects selected texts
- **Filter is not selection, and that is now guarded (#204):** the filter only hides rows, it does not change the selection. If a wider selection was searched while a filter was active, a note appears above the results with a one-click correction („Nur die M gefilterten Texte durchsuchen"); the zero-hit box names both term and search space („0 Treffer für ‚X' in N ausgewählten Texten")

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
- **Back to the start of the text (#138):** a round jump button at the bottom right, as soon as the panel header has scrolled out of the viewport; it jumps back to title and metadata, not to the top of the page
- **Verse numbering per counting range (#138):** the visible margin numbering restarts at 1 in every `<div>` that begins its own **continuous** count at `n="1"`. Two conditions make the criterion: the first numeric `<l>` carries `n="1"`, and the 1 occurs exactly once inside the `<div>`. Lines of an embedded parallel witness (`div[@type="parallel"]` inside another `<div>`) do not count towards this: every witness is measured on its own lines only (#250, see below). Of 6,789 `<div>`s in the corpus 2,661 meet the first condition, of which **1,492 in 137 texts** qualify (897 `chapter`, 252 `song`, 159 without `@type`, 156 `section`, 21 `parallel`, 7 `number`). This makes **1,352 additional margin numbers in 49 texts** visible. The largest case is PZ (Parzival) with +826, followed by FR3 (+136), CHH (+53), TKR (+40) and HUG (+39, Julia's original case). The basis is `python scripts/audit/count-verse-numbering-resets.py`, which rebuilds the render order and compares „with reset" against „without reset"; since #302 it carries the witness separation, so every number in this paragraph is reproducible.

  **Witness separation (#250, as of 2026-07-31):** since the Frauenlob rebuild (#236) FR3 carries a `div[@type="parallel"]` inside the `div[@type="section"]` of the base witness. Both witnesses start at `n="1"`, so the subtree of the `section` contained two ones, the `section` failed the second condition, and the visible 1 wandered from the base witness to the parallel one. **19 of the 127** FR3 `section`s were affected. Since the witness separation the base witness gets its 1 back and the parallel witness keeps its own. Measuring across all 667 texts shows the effect in FR3 only: 19 `section`s qualify in addition, not a single one loses its qualification, and the 21 qualifying `parallel` divs stay unchanged. DES2 and PKP also have nested `parallel` divs and do not change.

  The second condition is the actual protection: texts with **stanza-local** counting inside a `<div>` deliberately get no anchor. It discards 1,169 `<div>`s in 84 texts corpus-wide and thereby prevents 1,007 unmotivated margin ones. NLA (Nibelungenlied ms. A) is the textbook case: 38 untyped `<div>`s in which every stanza starts at 1 again and which render no heading at all for lack of `@type`/`@n`; without the condition the text would get exactly 38 additional margin ones, that is the #127 regression through `<div>` instead of through `<lg>`. NBB is structurally untouched by the change, because the text contains no `<div>` elements
- **URL parameters:** `?textId=ABG&lemmaIds=879,7532&position=310`
- **Excerpt context (#134):** texts with `biblScope unit="verse"` in the header (excerpts of a larger work, e.g. AK from the Steirische Reimchronik) show a visible banner above the text plus an „Ausschnitt" metadata section (excerpt, whole work, verse range, context); see TEI-MODEL.md §2.1
- **Editorial interventions (#250):** an expandable metadata section with the statements from the `<editorialDecl>` of the text, in document order. It carries the note that where the MHDBDB intervened in the text, the printed edition is authoritative for quotation. The clearest case is FR3: there the two appendices of the edition are swapped (appendix I counted as XV) and an error in the editors' verse numbering is corrected. Not shown is the repository boilerplate about resolving local file references, which 666 headers carry word for word in German and English; after that filter 664 texts keep between 1 and 42 paragraphs, while CEFB, GWTK and KVO keep none and the section is omitted there. Numbers reproducible via `python scripts/audit/count-editorial-notes-and-div-heads.py`
- **Section label above an own heading (#250):** if a typed `<div>` carries a `<head>` of its own, the synthetic label („Lied 5", „Rezept 1") becomes the superordinate line of that heading instead of a second heading of equal rank next to it. This affects 1,097 of the 4,676 typed `<div>`s in 35 texts (403 `song`, 320 `chapter`, 301 `recipe`, 72 `number`, 1 `section`), led by NEI and NEIC (124 each), WZB (97) and KBL4/SUB1 (66 each). The label stays visible because in none of these cases does the `<head>` carry the number from `@n` (AC1: `n="1"` and „das i capitel", ABS: `n="1"` and „basteten .") and 932 of the divs have an `@n`; suppressing it would remove the only visible count of the section

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

### Dictionary, the A–Z register (#117)

A conventional dictionary entry page (`woerterbuch.html`) for all 43,879 lemma pages.

**How it works:**
- An A–Z index bar (plus `#` for numeric lemmata) with the entry count per letter as a tooltip
- Bucketing over the `normalized` field of the authority index (NFD fallback for initial `ë`/`ú`)
- Pagination at 200 entries within the letter, sorted alphabetically (`Intl.Collator('de')`)
- Every entry (lemma plus POS badge) links to the persistent lemma page `lemma/?id=N`
- Deep links through URL state: `woerterbuch.html?buchstabe=s&seite=3`
- Reachable from the header menu item „Wörterbuch" on every page

**Naming decision:** „Wörterbuch" instead of „Lemmata" (the playground's technical term) or „Wortindex" (old MHDBDB; mentioned in the page subtitle as a bridge), reasoned in issue #117.

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
- Action „Belege suchen" (#58): hands that lemma to the multi-lemma search in document mode, with its id pinned via the `ids` route parameter, so a homograph group cannot swap the lemma on the way. Both render paths carry the button, which is why they share one `lemmaItemButtons()`

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
- Resting state is the typology as an expandable tree, from its two roots
  (*Epik, Lyrik und Dramatik*, *Wissensliteratur und Gebrauchsliteratur*),
  9 levels deep. Each node names its own works and how many sit in the branch
  below it; branches leading to no work at all are dimmed and labelled, because
  482 of the 615 categories are in that position (#361)
- The 171 categories with more than one parent are shown at every one of those
  positions, and each position opens and closes on its own. A *Predigtmärlein*
  is a *Märe* and a *Predigt*, and the tree says both
- The #119 filter applies to the tree as well, and there it drops the empty
  branches rather than dimming them: 1,167 tree positions become 246, behind
  them the 133 categories that lead anywhere. Dropping cannot tear the tree
  apart, because a parent's work set is the superset of every child branch;
  both roots survive. One checkbox, but its meaning has to differ between the
  views, so its label says which one is in force: in the tree „works in the
  branch" (an intermediate node without works of its own has to survive, or its
  children become unreachable), in the result list „works of its own" (a card
  without them is a dead end, its „Werke anzeigen" button would have nothing to
  show). That is 41 of the 133
- Detail panel per category: every root-to-category path (up to 9), plus the
  works assigned to it
- Search by genre term steps in front of the tree; a hit names its path
  (`Epik, Lyrik und Dramatik › Kurzdichtung › Märe`) instead of the unordered
  " UND " chain of all ancestors that stood there until #361
- Action: view all works in a genre, or all authors
- Note: v1.1.0 fixed hierarchy extraction

**Name Explorer:**
- Search by proper name
- Display: Name, related concepts
- Action: View concept relationships

### TEI Text Analysis

Corpus-wide text analysis using pre-built indexes. Eleven analysis tools in eleven playground entries (multi-lemma offers document, proximity and verse mode in one entry), all of them in place in the results panel as form plus body (except multi-lemma, which is a modal). The two curated external datasets described at the end of this section, character naming (#59) and arthurian horses (#193), are counted separately: with #194 they moved into a group of their own, "Experimentelle Forschungsdaten".

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

**Multi-lemma search „Im selben Vers" (#106 point 8):**
- Co-occurrence restricted to a shared `<l>` (syntactically tighter than the word window of the proximity search)
- Data basis: `lineStarts[]`/`lineEnds[]` from corpus index v4.1.0+, no new build step
- Verse texts only (600 of 667); prose is skipped automatically
- Hits name the verse number; expand and reader deep link as in the proximity search
- URL routing: `#multi-lemma&lemmata=…&mode=verse`

**Lemma search by verse position (#47.3):**
- A single lemma plus a position choice (verse start or verse end, verse end by default)
- Finds lemmata sitting exactly at the first or last `<w>` of an `<l>`
- Use case: rhyme analysis, stylistics of verse endings („how often does Wolfram rhyme on `minne`?")
- Hit list with the share per text („54 % of all `minne` occurrences in Tristan sit at the verse end"). Numerator and denominator both come from `text.lemmata`, so the ratio holds up even for tokens with multiple lemma references, unlike the rhyme pressure of the verse-ending profile: [CONTRACTS §H.5](CONTRACTS.md#h5-normalized-figures-in-the-remaining-tools)
- Verse texts only (600 of 667, about 90 % of the corpus); prose is skipped automatically
- Clicking a hit opens the reading view with highlighting

**Word frequency analysis (#88):**
- Top-N lemmata over the whole corpus or per text
- POS-based stopword filter (DET, ART, POS, PRO, PRP, CCNJ, SCNJ, CNJ, NEG, IPA, VEX, VEM): removes frequent function words, brings content-bearing lemmata forward
- Absolute or relative frequency
- Sorting by frequency or alphabetically

**True hapax legomena (#196):**
- Lemmata (not word forms) with a corpus-wide total frequency ≤ n (hapax/dis/tris, 1 by default), to be distinguished from the per-text hapax rate of the text statistics (#89). Counting rule and filter order are normative in [CONTRACTS §H.2](CONTRACTS.md#h2-hapax-legomena-196)
- Data path: one aggregation pass over `text.lemmata` of all texts (the word frequency analysis pattern); per lemma the first ≤3 occurrences (`textId` plus word position) are carried along, the verse number via binary search over `lineStarts[]`
- **Facet precedence (the same for all three default filters):** a part of speech chosen explicitly in the POS facet overrides the filter of the same name (NAM, NUM, any POS from `FUNCTION_WORD_POS`); the affected checkbox then renders `disabled` and dimmed. Without this rule the facet returns an empty list without comment
- Filters: hide proper names (NAM, on by default, 28 % of the hapaxes), hide numerals (on by default, applies only to pure NUM, not to multiple parts of speech such as `zwispeltic` ADJ/NUM; affects 72 of the 119 NUM hapaxes. The trigger was the three numeral lemmata 42/46/49, which stood alphabetically at ranks 1 to 3, see #228), hide function words (the shared `FUNCTION_WORD_POS` set from word-frequency.js), POS facet, initial-letter facet (on `lemma.normalized`)
- Per entry: lemma link to the lemma page, PoS badges, occurrence(s) as a reader deep link (`korpus.html?textId=&lemmaIds=&position=`), a details expander with concept chips and a lazy lookup against the Wörterbuchnetz (five dictionaries via the shared client `assets/js/lib/woerterbuchnetz.js`, #258, CONTRACTS §D.2), which answers „a true MHG hapax, or only a corpus hapax?". The negative finding names the dictionaries it queried, because the reading „true hapax" hangs on exactly that list
- Lemma ids without an authority entry are shown with a badge (curation finds, 99 of them as of 2026-07)
- Tab „Beitrag pro Text": rarities per text, absolute and per 1,000 tokens, sortable
- CSV export of the filtered list (UTF-8 BOM, semicolon); pagination at 100 entries
- A deliberate limit: no freely chosen subcorpus (hapax relative to a text selection), a follow-up candidate, see issue #196

**Text statistics (#89, selection UI #136):**
- Per text: token count, lemma diversity (unique / total), hapax rate, average lemma frequency
- Corpus overview as a sortable table
- Stylistic indicator: high lemma diversity in short texts means lexically rich. **Careful when comparing across texts:** the figure is a type-token ratio and falls with text length for purely mathematical reasons, so the column sometimes sorts by length rather than by richness of vocabulary. Counting rule and bases are normative in [CONTRACTS §H.5](CONTRACTS.md#h5-normalized-figures-in-the-remaining-tools)
- Building a subset: a checkbox per row plus a master checkbox, „Nur Auswahl anzeigen", a selection counter; the selection survives sorting

**Lemma distribution (#90):**
- A single lemma gives a bar chart across all texts
- Top-N bars in the chart, the rest as an expandable table
- Absolute or relative frequency (per 1000 tokens; the base of the rate is in [CONTRACTS §H.5](CONTRACTS.md#h5-normalized-figures-in-the-remaining-tools))
- Clicking a bar or a sigle opens the reading view with highlighting

**Concept distribution (#47 R2, with autocomplete #113):**
- A single concept (German, English, or a `concept_xxxxx` id) gives a bar chart across all texts
- Aggregates every lemma whose `senses[*].conceptIds` contains the concept
- Data path: concept → senses → lemmata → texts (summing occurrences per text); the base of the mode „Relativ (pro 1000)" is in [CONTRACTS §H.5](CONTRACTS.md#h5-normalized-figures-in-the-remaining-tools)
- Alternative concept candidates are shown (e.g. „love" offers Intimität and Liebe/Zuneigung)
- An expandable „zugeordnete Lemmata" section for validating the concept selection
- Clicking a hit opens the reading view
- A **live autocomplete dropdown** in the concept input (max. 8 suggestions, arrow navigation, Enter selects and searches, Escape closes), the same pattern as DWDS or Google search

**Text comparison (#108):**
- Choose two texts through dropdown menus (all 667 sigles with title and author)
- Three lemma sets are computed: only in A, in both, only in B
- Per lemma: frequency in A, frequency in B, absolute difference |A−B|
- Sorting by frequency, difference or alphabetically, plus a substring filter on the lemma name
- An A↔B swap button for the mirrored perspective
- Data path: pure set operations on `Object.keys(text.lemmata)`, no new index fields
- Use cases: „which lemmata does PZ share with JT?", „evidence for borrowed verses (shared rare lemmata between otherwise unconnected texts)", „lemma profiles per work"
- Clicking a frequency number opens the reading view of that text with highlighting

**Co-occurrence ranking (#107):**
- DWDS-style „which lemmata occur most often near X?"
- An input lemma plus a context window (±3 to 25 words, ±10 by default) gives a ranked table of the top-N partner lemmata
- The POS filter is essential: the default „Inhaltswörter" (NOM/VRB/ADJ/ADV) keeps stopwords (der/und/ich/daz/er) from dominating the list; „nur Nomen", „nur Verben", „nur Adjektive" and „alle" are available too
- Data path: a window scan over `text.words[pos±w]` for every position in `text.lemmata[X]`
- Async chunking (a MessageChannel yield every 30 ms) keeps the UI responsive even for frequent lemmata; switching the POS filter needs no recompute (rawCounts are cached)
- Use cases: „what typically stands near `êre`?" (tuon, sprechen, got, herre), „which adjectives accompany `wîp`?"
- Clicking a partner opens the multi-lemma search prefilled with both lemmata and the current distance; clicking a lemma opens the lemma page

**Rhyme dictionary (#106, minimal variant):**
- „Which lemmata rhyme on X?": an input lemma plus an optional text/author filter (exact sigle or a substring of title/author) gives a ranked table of rhyme partner lemmata
- Data path: a scan over `text.lineEnds[]` (corpus index v4.1.x); the candidates are the lemmata of the immediately neighboring verse endings (±1 verse, assuming couplet rhyme)
- Rhyme heuristic: a three-letter suffix match on the MHG-normalized lemma forms (two letters only if both forms are ≤4 characters, which finds `wîp : lîp` and `tac : slac` without letting short words like `en`/`dô` flood long target lemmata); an identical rhyme (a lemma on itself) is counted once only. The full counting rule including the asymmetry between target and partner side: [CONTRACTS §H.3](CONTRACTS.md#h3-rhyme-dictionary-106)
- Per partner: the number of rhyme pairs, texts as sigle chips with their pair count, and „→ Belege" expands the counted verse pairs inside the table: both verses as full `<l>` content (lazily fetched TEI; the highlight mapping runs over the CONTRACTS §B position counting, so that `lineEnds[]` positions point at the right words), marked rhyme words, the verse number from `<l n>`, a reader deep link (`position=`); paginated at 10, with a cap of 1000 stored verse pairs per partner. (Previously only a link into the proximity mode of the multi-lemma search at distance 15, which also showed co-occurrences away from the verse endings, so not rhymes; KZW report 2026-07-09)
- Async chunking plus an abort token (the #107 pattern), prose (empty `lineEnds`) is skipped
- Deliberate limits of the minimal variant (issue #106): lemma-based instead of token-based (the rhyming inflected form may differ), structural instead of phonetic, and alternating rhymes (ABAB) escape the ±1 scan; an original-token variant would need an index extension (`lineEndWords[]`), phonetic classification is follow-up work in #109

**Verse-ending profile (#106 point 2):**
- The top-N most frequent lemmata at the verse end, with a selectable scope: the whole corpus, an author (optgroup) or a single text
- Data path: `text.words[lineEnds[i]]` per verse (corpus index v4.1.x), no new build step
- Columns: verse-ending occurrences (absolute), the share of all verse endings in the scope, and **rhyme pressure**, the share of a lemma's occurrences that sit at the verse end against all of them (#106 point 3: a high value means rhyme-driven, a low one semantically motivated). Numerator and denominator are both scope-local and come from different index fields, which would skew the figure as soon as there are tokens with multiple lemma references (there are none today): [CONTRACTS §H.4](CONTRACTS.md#h4-verse-ending-profile-and-reim-druck-106-points-2-and-3)
- Function word filter (the same POS set as word frequency and hapax), lemma links to the lemma pages
- Verse texts only (empty `lineEnds` are skipped); the use case from the issue: comparing the rhyme style of Wolfram, Hartmann and Gottfried

**Extended character naming (#59, beta):**
- Curated naming practices beyond the proper name, for four works (ENE, IW, ROL, TRO), from Linda Beutel-Thurow's doctoral project Naming-analysis
- Choose a work, then a character (sorted by number of attestations), then terms in four categories: proper names, cover names, antonomasias („der rîter" for Iwein), epithets („der küene"). The **cover name** names the character the way a name does without being her name; it comes from the curated overrides only and shows up as a tab and a summary tile in the works where it occurs, currently for Alexander as the name Paris goes under in the Trojanerkrieg (Linda Beutel-Thurow, #59 comment of 2026-08-10: „not as 'proper name' but as 'cover name'")
- Per term: frequency plus expandable attestations with verse number, naming phrase and speaker (narrator / character speech with the naming character / self-naming)
- **Two perspectives on the same records** (Linda Beutel-Thurow, #59 comment of 2026-07-29). Every record carries both who is named and who does the naming, and until 2026-08 only the first direction was selectable:
  - *named character*: pick a character, then narrow by naming instance („how is Iwein named, and which of that is Lunete speaking?"). The sub-filter offers the narrator, self-naming, all character speech, and each namer individually, each with its count
  - *naming instance*: pick a namer, and the terms come grouped by the character named („which namings for whom does Iwein use in the Iwein?" is Linda's own example). The narrator is one of the selectable namers, and a character's self-namings count towards that character as namer. Called *instance* rather than *character* on both sides since 2026-08-10, because the narrator is in the list and is not a character (Linda's wording)
- The source notation stays visible. A leading `#` and square brackets mark an instance that is not an acting character of the work: an indeterminate crowd (`#haiden`, `[MENGE]`) or a person merely quoted by the narrator (`#David`). Counted over the distinct `by` values per work, the hash occurs in ROL (13) and TRO (2), the brackets in IW (7), ENE (7) and TRO (14); Linda explained the brackets for the Trojanerkrieg, and the ones in IW and ENE look alike but are not separately confirmed. The module explains this below the selection instead of cutting the notation off, and the grouping key that used to cut it is gone: it existed to merge five namers that had split into two entries each, and Linda unified those in the source on 2026-08-10 (`b7cc0585`). Measured against that state the key merges nothing (distinct `by` values per work, so excluding the narrator and self-namings: 33/29/48/71 in IW/ENE/ROL/TRO, identical with and without the cut), and cutting would now be wrong, since `#David` and an acting David would become the same namer
- The term filter is MHG-normalized („tore" finds `tôre`)
- Reader deep links for ROL and TRO: verse numbers link into the reading view via `korpus.html?textId=<SIG>&verse=<n>` (jumping to the verse line with a highlight pulse). The verse counting of these two works coincides with the MHDBDB TEI counting (Linda Beutel-Thurow, #59 comment of 2026-06-11; TRO spot check verified 4 of 4). ENE and IW follow different edition counts and deliberately stay without links
- Attribution visible in the module: Beutel-Thurow, L. (2026). Naming-analysis (v0.1.0-beta), DOI 10.5281/zenodo.18770138, CC BY-NC-SA 4.0
- Data basis: `data/naming-index.json.gz` (~110 KB), built via `scripts/ingest/naming/01-fetch-and-build-index.py`, lazily loaded without an IndexedDB cache. One work-specific alias addition sits on our side in `scripts/ingest/naming/alias-overrides.json`: „Alexander" is the name Paris goes under in the Trojanerkrieg, so the naming names him rather than describing him, and it counts as a cover name there. Linda's `lemma_normalization.json` normalizes across all works and would carry the alias into places where it is wrong (approved by Linda, #59 comments of 2026-07-28 for the alias and 2026-08-10 for the category; affects exactly one record, TRO V. 20665)

**Arthurian horses (#193, beta):**
- Curated encoding of the horses in five works (WH, PZ, ER, IW, TR) from Luise Borek's exemplary study: 13 horses (10 named, 3 unnamed), 346 attestations
- Choose a horse; the table gives every attestation with Borek's wording and what she marked there: the event (intro, combat, care, loss, transfer, communication, recognition, gift), traits (colour, marking, quality), gear, and owner or rider. The event buttons filter the attestations
- The summary names the works, the traits and gear attested, the characters involved, and the horse's spelling variants (Gringuljete alone has six)
- **Both citations are shown, and Borek's is the visible one.** Her verse reference is the citable one and stays verbatim; our resolved verse only drives the link. For nine of the 346 attestations the two diverge, because our Parzival follows Leitzmann (ATB 12) while Borek names no edition at all. Those attestations carry an asterisk with the reason; the link still lands on the right verse, since every citation was matched on wording
- Reader deep links via `korpus.html?textId=<SIG>&verseId=<wordId>`, the word-id route added for this feature (#193). `?verse=<l n>` would not do: in PZ the `@n` counts only inside the thirty-line section, in WH the section number did not exist in the TEI at all when this was built (it became `<div type="chapter">` in #358, and the `@n` there now counts inside the section just as in PZ), and the Ambraser insert in ER sits as one `<l n="4629">` covering the cores 462900 to 462957, that is 57 verses in a single element. The reading view therefore renders every `<l>` with `data-core`, the numeric part of its first word id, plus `data-core-max` wherever an `<l>` spans more than one verse; the jump falls back to that range, so the ten Ambraser attestations land on the passage even though their line does not exist as its own element
- Attribution visible in the module: Borek, L. (2023). Exemplarische Auszeichnung arthurischer Pferde, hdl:tudatalib/3695, CC0 1.0
- Data basis: `data/horses-index.json.gz` (11 KB), built via `scripts/ingest/horses/03-build-index.py`, lazily loaded without an IndexedDB cache

Both of the above sit in the playground's third group, **Experimentelle Forschungsdaten** (#194), which collects curated datasets from external research projects. Every entry there carries a beta badge, its own prebuilt index, and visible attribution naming author, origin and work coverage.

**Cross-platform workflow:**
1. Perform analysis in playground
2. Find interesting result (co-occurrence, peak in distribution, top lemma at a verse ending, etc.)
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
- Optional `ids`, paired positionally with `lemmata`, pins the resolution to exact lemma ids instead of deriving them from the written forms (#58): `#multi-lemma&lemmata=minne&ids=4130&mode=document`. The lemma explorer sets it, hand-typed terms never carry one
- Sharing a URL reproduces the exact view state

### Search Normalization

Consistent search behavior across all 18 entry points via Middle High German character normalization.

**Normalization rules:**
- Long vowels: â→a, ê→e, î→i, ô→o, û→u
- Umlauts: ä→ae, ö→oe, ü→ue; the breve umlauts of the Wenzelsbibel: ŏ→oe, ŭ→ue (#224)
- Ligatures: æ→ae, œ→oe

**Implementation:**
- Shared utility: `assets/js/lib/text-normalizer.js`
- Applied to all search inputs and indexed data
- Enables consistent matching across orthographic variations

**Note:** Normalization handles **character variations**, variants.xml handles **spelling variations**. Both used together for comprehensive search coverage.

## Lemma Page Features

Persistent pages for individual lemmata, accessible at `/lemma/{numericId}`. These URLs are stable external identifiers used by Wörterbuchnetz, MWB, and Wikidata (P9351).

### Dictionaries (#73, extended in #258)

A section „Wörterbücher" with deep links into five Middle High German dictionaries of the Wörterbuchnetz: MWB, Lexer, Lexer-Nachträge, Benecke/Müller/Zarncke and Findebuch. The lemma page is the page for going deeper and therefore the only surface that spells the sigle out: one heading with the full title per dictionary, below it every entry as a card with its grammatical note (unabridged, unlike the compact search panel). Dictionaries without a hit do not appear.

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
