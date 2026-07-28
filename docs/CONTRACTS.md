# Cross-System Contracts

Technical contracts that bind Python (build-time) and JavaScript (runtime) together. Breaking any of these causes silent data corruption – search returns wrong results, highlights land on wrong words, or caches serve stale data.

**Why this document exists:** These constraints span multiple files and languages. No single module owns them. They are the most dangerous knowledge to lose because violations produce no error messages – just silently wrong behavior.

> **Audience:** This file is a technical reference specification, written primarily for development and automated tooling (precise, machine-oriented).

---

## A. MHG Normalization Parity

**Contract:** `scripts/mhg_normalizer.py` and `assets/js/lib/text-normalizer.js` MUST produce identical output for all inputs.

**Why:** Build scripts normalize lemma forms when creating the authority index. The browser normalizes user search input at runtime. If the two normalizations diverge, indexed terms won't match runtime queries – search appears broken with no error.

**Parity test:** `testing/tests/normalization-parity.spec.js`

### Transformation Rules (ordered – order matters)

| Step | Operation | Characters | Result | JS | Python |
|------|-----------|-----------|--------|-----|--------|
| 0 | Unicode-Komposition | o + U+0308 | ö | `.normalize('NFC')` | `unicodedata.normalize('NFC', …)` |
| 1 | Lowercase | all | lowercase | `.toLowerCase()` | `.lower()` |
| 2 | Long vowels (circumflex + macron) | â ā | a | `/[âā]/g` | `.replace('â','a').replace('ā','a')` |
| 2 | | ê ē | e | `/[êē]/g` | `.replace('ê','e').replace('ē','e')` |
| 2 | | î ī | i | `/[îī]/g` | `.replace('î','i').replace('ī','i')` |
| 2 | | ô ō | o | `/[ôō]/g` | `.replace('ô','o').replace('ō','o')` |
| 2 | | û ū | u | `/[ûū]/g` | `.replace('û','u').replace('ū','u')` |
| 3 | Umlauts → digraphs | ä | ae | `/ä/g` | `.replace('ä','ae')` |
| 3 | | ö | oe | `/ö/g` | `.replace('ö','oe')` |
| 3 | | ü | ue | `/ü/g` | `.replace('ü','ue')` |
| 4 | Ligatures | æ | ae | `/æ/g` | `.replace('æ','ae')` |
| 4 | | œ | oe | `/œ/g` | `.replace('œ','oe')` |
| 5 | Special | ǒ | o | `/ǒ/g` | `.replace('ǒ','o')` |

### Test Cases

These 18 cases must pass in both languages. Source: `scripts/mhg_normalizer.py:131-151`

| Input | Expected | Why |
|-------|----------|-----|
| `brôt` | `brot` | ô → o (circumflex, NOT umlaut) |
| `BRÔT` | `brot` | Uppercase + circumflex |
| `wîn` | `win` | î → i |
| `vriunt` | `vriunt` | No special characters – passthrough |
| `schône` | `schone` | ô → o (circumflex – NOT ö → oe) |
| `schöne` | `schoene` | ö → oe (actual umlaut) |
| `Âventiure` | `aventiure` | Uppercase Â → lowercase → a |
| `mære` | `maere` | æ → ae (ligature) |
| `âne` | `ane` | â → a |
| `fröude` | `froeude` | ö → oe |
| `müede` | `mueede` | ü → ue, existing e remains → "mueede" |
| `ûzer` | `uzer` | û → u |
| `ōre` | `ore` | ō → o (macron) |
| `sǒne` | `sone` | ǒ → o |
| `cæsar` | `caesar` | æ → ae |
| `œnologie` | `oenologie` | œ → oe |
| `''` | `''` | Empty string |
| `None`/`null` | `''` | Null handling |

### Common Pitfall

`schône` (ô = circumflex) → `schone`, NOT `schoene`. The circumflex ô maps to plain `o`, while the umlaut ö maps to `oe`. Visually similar, semantically different.

### Schritt 0: Unicode-Komposition (#224)

Ein „ö" kann als ein Zeichen (U+00F6) oder als `o` + kombinierendes Trema (U+006F U+0308) kodiert sein. Beide sehen identisch aus, aber nur die komponierte Form trifft die Umlaut-Regel in Schritt 3. Ohne die Komposition fällt eine zerlegte Eingabe durch Stufe 1 **und** Stufe 2 der Lemma-Auflösung (§C) und landet im Partial-Match-Fallback. Genau das war die erste Ursache im Bug-Report #224: die Suche nach „böses" mit zerlegtem ö lieferte `ês`, `ô`, `sê` statt `bœse`.

Zerlegte Formen entstehen beim Kopieren aus macOS-Quellen und aus manchen Editionsdatenbanken, sind also normale Nutzereingaben.

**Wirkung auf die Build-Seite:** Der Schritt ändert die Ausgabe an genau drei Stellen, weil die Authority-Files sonst NFC sind. Betroffen sind die Datensätze mit zerlegtem ü in `persons.xml` und `works.xml`:

| Datensatz | vorher | nachher |
|-----------|--------|---------|
| `person_1052` Hugo von Mühldorf | `hugo von mühldorf` | `hugo von muehldorf` |
| `person_1332` Wachsmut von Mühlhausen | `wachsmut von mühlhausen` | `wachsmut von muehlhausen` |
| `work_435` Lyrik von Hugo von Mühldorf | `lyrik von hugo von mühldorf` | `lyrik von hugo von muehldorf` |

Alle drei waren über die normalisierte Suche nicht auffindbar. Alle 43.879 Lemma-Normalisierungen und alle 234.244 Varianten-Schlüssel bleiben unverändert. Deshalb Authority-Index v1.6.2.

**Nicht betroffen:** Der Korpus selbst enthält kombinierende Zeichen (Stichprobe: rund 110 Tremata in 60 Dateien, dazu Tilde und Cedille). Die sind editorisch gewollt und werden nicht normalisiert; der Korpus-Index speichert Lemma-IDs und Positionen, keine normalisierten Textformen.

### Helper Functions

Die Vergleichs-Helfer existieren nur auf der JS-Seite (`TextNormalizer.matchesNormalized` / `.exactMatchNormalized` / `.startsWithNormalized`). Die Python-Pendants wurden entfernt, weil kein Build-Skript sie je aufrief (Audit #107) – Python-Code vergleicht direkt über `normalize_mhg(a) == normalize_mhg(b)` etc. Der harte Paritäts-Vertrag gilt für `normalize_mhg()` ↔ `TextNormalizer.normalizeMHG()`; wer einen Python-Vergleichs-Helfer neu einführt, muss ihn wieder 1:1 gegen die JS-Semantik spiegeln (Substring/Exact/Prefix auf normalisierten Strings).

---

## B. Position Counting Contract

**Contract:** Python build scripts and JavaScript TEI renderer MUST assign identical word positions to each `<w>` element.

**Why:** The corpus index stores lemma positions as integers (e.g., lemma_879 appears at positions [0, 15, 42]). The reading view uses these positions to navigate between hits (scroll to next/previous occurrence) and to align a clicked search result with the right word during DOM traversal. If Python counts position 42 differently than JavaScript, navigation jumps to the wrong word and proximity search (`|pos_a - pos_b| <= maxDistance`) breaks. (The highlight *decision* itself is by exact `@lemmaRef` id, not by position – see Contract B.1.)

**Parity test:** `testing/tests/position-parity.spec.js` (#131) – runs a prose text (PL1), a verse text (OVG) and a synthetic empty-`<w>` fixture through both counting paths and asserts identical position sequences.

### Rules

1. **Only count `<w>` elements with `@lemmaRef` attribute**
2. `<w>` elements without `@lemmaRef` are **skipped** (not counted, not stored)
3. All other elements (`<pb>`, `<lb>`, `<seg>`, `<hi>`, text nodes, etc.) are **ignored** for counting
4. Counting starts at **0** for each document
5. Order = **document order** (depth-first traversal of `<body>`)

### Python (build-time)

Source: `scripts/build-corpus-index.py` (`extract_word_data`)

The selector below is the *logical* counting rule, not the literal implementation. The build does a single-pass `etree.iterwalk(body, events=('start','end'), tag=(w, l))` – chosen over a separate XPath / `.iter()` to avoid lxml proxy-id instability and to capture `<l>` boundaries (`lineStarts`/`lineEnds`, #47.3) in the same traversal.

```
Logical selection: //tei:body//tei:w[@lemmaRef]   (document order)

For each <w lemmaRef="..."> in document order:
    word_text = ''.join(el.itertext()).strip()
    if not word_text: continue              → empty <w lemmaRef> is NOT counted (JS matches this since #131)
    # @lemmaRef may carry SEVERAL whitespace-separated references (§B.1),
    # e.g. "lexicon.xml#lemma_308 lexicon.xml#lemma_5" (#170):
    lemma_ids = [frag.split('#')[1] for frag in lemmaRef.split()]
    position = len(words)                   → sequential from 0; ONE slot per token
    words.append(lemma_ids[0])              → words[] keeps the FIRST id only
    for lemma_id in dedupe(lemma_ids):
        lemmata[lemma_id].append(position)  → lemmata{} lists the position under EVERY id
```

**Consumer rule (follows from the words[]/lemmata{} split):** code answering "is position P an occurrence of lemma X?" MUST consult `lemmata[X]` (multi-ref-aware), never `words[P] === X` (first-id only). Applied in `verse-position-search.js` and `rhyme-dictionary.js` (target side); `cooccurrence-ranking.js`'s neighbor counting deliberately stays first-id (a full reverse map is not justified at 0 multi-ref corpus cases today).

### JavaScript (runtime)

Source: `extractAndFormatBody()` / `processWord()` in `assets/js/rendering/tei-text-reader.js`

```
Recursive DOM traversal of <body> children:
    state = { wordPosition: 0 }

    For each element encountered:
        if tagName === 'w':
            hasLemmaRef = el.getAttribute('lemmaRef')
            hasText     = el.textContent.trim().length > 0
            processWord(el, ...)  // render + check highlight
            if (hasLemmaRef && hasText):
                state.wordPosition++   // increment only when lemmaRef AND non-empty text (parity with Python)
```

### Parity note – empty `<w lemmaRef>` (resolved #131)

Both sides now **skip** `<w lemmaRef>` with empty text content: Python via `if not word_text: continue`, JS via the `hasText` guard in `extractAndFormatBody` (`tei-text-reader.js`, `case 'w'`). Before #131 the JS runtime incremented `wordPosition` for **every** `<w lemmaRef>` regardless of text – a latent parity gap (harmless then: **0** empty `<w lemmaRef>` across all 667 files, so the fix was a no-op on real data) that a future ingest with placeholder/gap tokens would have silently broken. The empty-`<w>` case is now pinned by `testing/tests/position-parity.spec.js`. (Because the corpus has no empty `<w lemmaRef>`, the shipped index is unchanged – no rebuild or version bump needed.)

### Parity note – note children, multi-`@lemmaRef`, proximity context (resolved #170)

Three further latent drifts of the same class ("0 corpus cases today, armed by the next ingest"), all fixed behavior-neutrally (byte-identical index rebuild):

1. **`<w>` inside date/year `<note>`:** the reader's badge branch swallowed `children()`, so a future lemmatized `<w>` inside such a note would be counted by Python/KWIC but not rendered/counted by the reader – every position after it would shift. The badge now renders **plus** its children.
2. **Whitespace-separated multi-`@lemmaRef`:** `split('#')[1]` on the whole attribute produced the broken key `"lemma_308 lexicon.xml"`. Now resolved per fragment (see pseudocode above): `words[]` keeps the first id, `lemmata{}` lists the position under every id.
3. **Proximity-context enrichment (`playground/js/ui/core/ui-helpers.js`, `enrichFileResults`):** the fourth counting path mapped index positions back onto DOM words without the empty-`<w>` guard from #131 – one empty `<w lemmaRef/>` would shift every context window behind it. Now guarded identically.

All three (plus the consumer rule above) are pinned by `testing/tests/position-parity.spec.js` with the fixture `position-parity-170.tei.xml`.

### Example

```xml
<body>
  <p>
    <w lemmaRef="lexicon.xml#lemma_100">Der</w>        <!-- position 0 -->
    <w>unbekannt</w>                                     <!-- SKIPPED (no lemmaRef) -->
    <w lemmaRef="lexicon.xml#lemma_879">brôt</w>        <!-- position 1 -->
    <pc join="left">,</pc>                                <!-- not a <w>, ignored -->
    <w lemmaRef="lexicon.xml#lemma_200">ist</w>         <!-- position 2 -->
  </p>
</body>
```

Corpus index stores: `lemmata: { "lemma_879": [1] }` – position 1, not 2.

### Version History

- **v3.x:** Paragraph-based indexing (positions reset per `<p>` – caused misalignment between Python XPath extraction and JavaScript DOM traversal)
- **v4.0.0:** Document-level indexing (positions never reset – simple, reliable)

---

## B.1 Lemma Highlight Matching Contract

**Contract:** A `<w>` is highlighted iff its `@lemmaRef` contains the searched lemma id as an **exact whitespace-separated token** – never as a substring.

**Why:** `@lemmaRef` may carry several space-separated values (e.g. `lexicon.xml#lemma_308 lexicon.xml#lemma_5`). A substring test (`lemmaRef.includes('#lemma_308')`) also matches neighbouring ids like `#lemma_3089` (jâmer), `#lemma_3087`, `#lemma_30800` – so a search for one lemma highlights unrelated words and inflates the in-reader hit counter. This was bug #126 (fix `8e38f25cc`).

### Rule

Single source: `lemmaRefMatchesId(lemmaRef, lemmaId)` in `assets/js/lib/lemma-match.js` (shared by main site and playground, like `text-normalizer.js`).

```
function lemmaRefMatchesId(lemmaRef, lemmaId):
    if not lemmaRef or not lemmaId: return false
    refIds = lemmaRef.split(/\s+/).map(t => t.split('#')[1]).filter(Boolean)
    return refIds.includes(lemmaId)        // exact — NOT lemmaRef.includes('#' + id)
```

### Test cases

| `@lemmaRef` | search id | match? |
|-------------|-----------|--------|
| `lexicon.xml#lemma_308` | `lemma_308` | yes |
| `lexicon.xml#lemma_3089` | `lemma_308` | **no** (substring trap) |
| `lexicon.xml#lemma_308 lexicon.xml#lemma_5` | `lemma_5` | yes |
| `lexicon.xml#lemma_30800` | `lemma_308` | **no** |

**Applies to all highlight/match paths**, all routed through the single `lemmaRefMatchesId` since #130 (was 6 inline copies across 4 files, the duplication that made #126 possible): `tei-text-reader.js` (single + multi-lemma) and the playground (`tei-manager.js` proximity + enrichment, `ui-helpers.js` context highlight). (`text-renderer.js` was a fourth call site until its dead render path, then the whole shim, were removed — audit #42 + Carearbeit 2026-07.) Validated on real corpus data: PL1 689 → 57, OVG 369 → 26 (matches the result-card count).

### Test Coverage

`testing/tests/lemma-matching.spec.js` (#130). Block 1 asserts the §B.1 case table against the real `lemmaRefMatchesId`; Block 2 is an e2e reader assertion (`korpus.html?textId=PL1&lemmaIds=lemma_308` → exactly 57 `.highlight`, OVG → 26). Verified to fail red against the pre-#126 substring logic.

---

## C. 3-Stage Lemma Resolution Algorithm

**Contract:** Search resolves user input to lemma IDs through exactly 3 stages, in order, with early return.

**Why:** MHG has extensive orthographic variation. A single lemma can appear as dozens of attested forms. The 3-stage approach balances precision (exact first) with recall (fuzzy last).

Source: `assets/js/search/search-engine.js` (`resolveLemmaIds`), `playground/js/data/authority-manager.js` (`searchLemmaByOrthography`). Das Stage-3-Prädikat und sein Ranking-Abstand liegen seit #224 gemeinsam in `assets/js/lib/lemma-resolve.js`; beide Oberflächen importieren sie. Geteilt ist ausdrücklich nur Stufe 3: Stufe 1 unterscheidet sich weiterhin (die Hauptseite vergleicht gegen das vorberechnete `lemma.normalized` des Index, der Playground normalisiert zur Laufzeit und rankt Homographen zusätzlich nach Korpus-Frequenz).

### Pseudocode

```
function resolveLemmaIds(normalized):
    // Input: already normalized via normalizeMHG() (Contract A)
    // Called by searchLemma() which normalizes the raw user input first

    // Stage 1: Exact match on normalized canonical form
    results = []
    for each lemma in authorityIndex.lemmata:
        if lemma.normalized === normalized:
            results.push(lemma.id)
    if results.length > 0:
        return results                       // EARLY RETURN — skip stages 2-3

    // Stage 2: Variants dictionary lookup (O(1) hash map)
    variantMatch = authorityIndex.variants[normalized]
    if variantMatch:
        return [variantMatch]                // EARLY RETURN — skip stage 3

    // Stage 3: Partial match fallback (bidirectional PREFIX, see #224)
    results = []
    for each lemma in authorityIndex.lemmata:
        if lemma.normalized.startsWith(normalized)                  // Stamm-Eingabe
           OR (lemma.normalized.length >= 3
               AND normalized.startsWith(lemma.normalized)):        // flektierte Eingabe
            results.push(lemma)
    sort results by abs(len(lemma.normalized) - len(normalized))    // Nähe zuerst
    return results.map(id)                   // May be empty
```

### Stage Behavior

| Stage | Input Type | Return | Performance | Example |
|-------|-----------|--------|-------------|---------|
| 1 | Canonical or normalized form | 0..N lemma IDs (homographs) | O(n) scan | `brot` → `[lemma_879]` |
| 2 | Attested orthographic variant | Exactly 1 lemma ID | O(1) lookup | `brott` → normalize → `brot` → variants[`brot`] → `lemma_879` |
| 3 | Prefix match, both directions | 0..N lemma IDs, nächste zuerst | O(n) scan + Sort | `minnecl` → `minnec`, `minne`, `minneclîch`, …; `schwertkampf` → keine |

### Stufe 3: warum Präfix und nicht Substring (#224)

Bis Juli 2026 war Stufe 3 ein bidirektionaler **Substring**-Test. Die Richtung „Eingabe enthält Lemma" traf jedes Kurzlemma, das irgendwo in der Eingabe steckte. Das Lexikon hält 5 ein-, 98 zwei- und 598 dreibuchstabige normalisierte Formen; sie trafen praktisch jede Eingabe, die Stufe 3 überhaupt erreichte. Für `minnecl` kamen 16 Treffer zurück, angeführt von `i`, `unminneclîche` und `nec`; für `schwertkampf` 14, darunter `a`, `êr`, `wert`, `kamp`.

Mittelhochdeutsche Flexion ist suffixal, deshalb hält ein Präfix-Test beide nützlichen Fälle (Stamm-Eingabe findet das volle Lemma, flektierte Eingabe findet das Lemma) und lässt das Rauschen fallen. Die Mindestlänge 3 gilt nur in der Richtung „Eingabe beginnt mit Lemma"; in der anderen ist das Lemma konstruktionsbedingt länger als die Eingabe.

**Zur Genese des Bug-Reports, weil sie leicht falsch erzählt wird:** Die dort gezeigte Suche nach „böses" trug ein **zerlegtes** Umlaut-ö (`o` + U+0308 statt U+00F6). Deshalb verfehlte sie Stufe 1 und Stufe 2 (die Varianten-Map hält den Schlüssel `boeses`, nicht die zerlegte Form) und landete überhaupt erst in Stufe 3, wo der Substring-Test daraus `ês`, `ô`, `sê` machte, ohne `bœse`. Mit komponiertem ö löst Stufe 2 dieselbe Eingabe korrekt zu `bœse` auf. Der Report hatte also zwei Ursachen, und beide sind behoben: die NFC-Komposition in Contract A und die Präfix-Regel hier.

Gemessen über 300 mit festem Seed gezogene Varianten-Formen mit bekanntem Ziel-Lemma (`scripts/audit/measure-stage3-resolution.py`, Stufe 1 und 2 umgangen):

| Metrik | alt (Substring) | alt + neues Ranking | neu (Präfix) |
|--------|----------------:|--------------------:|-------------:|
| Recall (Ziel irgendwo in der Liste) | 11,3 % | 11,3 % | 10,7 % |
| Top-1 nach Ranking | 0,3 % | 9,3 % | 10,0 % |
| Median der Listengröße | 8 | 8 | 0 |
| Größte Liste | 108 | 108 | 8 |

**Die mittlere Spalte ist wichtig:** Der große Sprung bei Top-1 (0,3 % → 9,3 %) kommt von der neuen Sortierung nach Längendifferenz, nicht von der neuen Regel. Die Regel selbst trägt 9,3 % → 10,0 % bei. Ihr eigentlicher Gewinn steht in den unteren beiden Zeilen: die Ergebnisliste schrumpft von median 8 auf 0.

Der Recall-Verlust von 2 Fällen auf 300 betrifft Präfix-Brecher: `gewieren` → `wieren` (Präfix `ge-`) und die römische Zahl `ccccxli`. Beide sind im Echtbetrieb belegte Varianten und werden bereits von Stufe 2 aufgelöst; die Messung umgeht Stufe 2 absichtlich. Der Median von 0 heißt: für eine zufällige unbekannte Form liefert Stufe 3 jetzt meist nichts statt acht Falschtreffern. Das ist gewollt, die Oberfläche zeigt dann ihren Kein-Treffer-Zustand.

**Bias der Messung:** Echte Stufe-3-Eingaben sind eher neuhochdeutsche Wörter und Tippfehler als mittelhochdeutsche Flexionsformen. Die Stichprobe misst, ob der Fix Recall kostet, nicht wie oft Stufe 3 im Alltag überhaupt das Richtige findet.

**Nebenwirkung auf Stufe 3 hinaus:** `resolveLemmaIds` liefert auch die Referenzmenge für die Keyness-Spalte der Tabellenansicht (#114, `app.js`). Bei Suchbegriffen, die Stufe 3 erreichen, ändern sich damit die Log-Likelihood-Werte, weil die Referenzsumme über weniger Lemmata läuft.

### Worked Example

User types: **brott**

1. Normalize: `brott` → `brott` (no special MHG characters)
2. Stage 1: Scan all lemmata for `.normalized === 'brott'` → no match
3. Stage 2: Check `authorityIndex.variants['brott']` → `'lemma_879'` → **found!**
4. Return: `['lemma_879']` (Stage 3 never runs)

### Variant Dictionary Structure

- Flat map: `{ normalized_variant_form: lemma_id }`
- 234,244 normalized entries (Stand 2026-07-12; 256,761 raw forms in variants.xml, deduped first-occurrence-wins), extracted from `authority-files/variants.xml`
- **First occurrence wins** – if two lemmata claim the same variant form, only the first one stored (source: `build-authority-index.py:643-644`, in `parse_variants()`)
- Keys are **normalized** forms (lowercase + MHG character mapping applied before storage)

---

## C.2 Multi-Lemma Deduplication

**Contract:** When a search resolves to multiple lemma IDs, results MUST be deduplicated by text and match counts aggregated before display. Two separate dedup algorithms exist for two different contexts.

**Why:** A single user search can resolve to multiple lemmata (e.g., homographs, or variant → multiple canonical forms). Without dedup, the same text appears multiple times in results – confusing and inflating counts.

### C.2.1 Main Site: Dedup by textId

Source: inline dedup in `handleSearch()`, `assets/js/app.js` (lemmaSet/textMap aggregation; no standalone function)

**Trigger:** User searches on `korpus.html`. `SearchEngine.searchLemma()` returns one result per (textId, lemmaId) pair. When N lemmata match, the same text can appear N times.

```
// inline in handleSearch() — pseudocode:
dedup(rawResults):
    // rawResults = [{textId, lemmaId, matchCount, ...}, ...]
    // Multiple entries per textId when search resolved to >1 lemmaId

    lemmaSet = new Set()       // unique lemmata found
    textMap = new Map()        // textId → aggregated result

    for each result in rawResults:
        lemmaSet.add(result.lemmaId)

        if textMap.has(result.textId):
            existing = textMap.get(result.textId)
            existing.matchCount += result.matchCount    // SUM counts
            existing.lemmaIds.push(result.lemmaId)      // COLLECT all matching lemmata
        else:
            textMap.set(result.textId, {
                ...result,
                lemmaIds: [result.lemmaId]              // start list
            })

    return Array.from(textMap.values())
    // Each text appears ONCE with total matchCount and all lemmaIds
```

**Worked example** – user searches "brot":

1. Resolution: Stage 1 finds `lemma_879` ("brôt") AND `lemma_12345` ("brot", different entry)
2. `SearchEngine.searchLemma()` returns:
   - `{textId: "ABG", lemmaId: "lemma_879", matchCount: 3}`
   - `{textId: "ABG", lemmaId: "lemma_12345", matchCount: 1}`
   - `{textId: "DES2", lemmaId: "lemma_879", matchCount: 5}`
3. After dedup:
   - `{textId: "ABG", matchCount: 4, lemmaIds: ["lemma_879", "lemma_12345"]}`
   - `{textId: "DES2", matchCount: 5, lemmaIds: ["lemma_879"]}`
4. Both lemmata get distinct highlight colors in reading view

### C.2.2 Playground: Proximity Context Window Dedup

Source: `playground/js/data/tei-manager.js` (proximity search function)

**Trigger:** Proximity search finds multiple overlapping co-occurrence windows in the same text. Without dedup, the same passage appears multiple times with slightly shifted windows.

```
function deduplicateProximityResults(rawMatches):
    // rawMatches = [{filename, matchPositions, distance, contextStart, contextEnd, ...}, ...]

    // Step 1: Group by filename
    byFile = groupBy(rawMatches, 'filename')

    deduplicated = []

    // Step 2: For each file, remove overlapping windows
    for each (filename, fileResults) in byFile:
        sort fileResults by contextStart ascending

        for each result in fileResults:
            overlaps = deduplicated.any(existing =>
                existing.filename === result.filename
                AND max(existing.contextStart, result.contextStart)
                    < min(existing.contextEnd, result.contextEnd)
            )

            if NOT overlaps:
                deduplicated.push(result)
            // else: discard (keep earlier/shorter-distance match)

    return deduplicated
```

**Behavior:** When two context windows overlap, the first one (earlier position, already added) wins. This keeps the closer match since results within each file are sorted by position.

### C.2.3 Playground: Document-Level Aggregation

Source: `playground/js/data/tei-manager.js` (document search function)

**Trigger:** Multi-lemma document search (find texts containing ALL searched lemmata).

```
function searchDocumentLevel(lemmaIds, corpusData):
    results = []

    for each text in corpusData.texts:
        // Require ALL lemmata present (intersection, not union)
        containsAll = lemmaIds.every(id => text.lemmata[id] exists)

        if containsAll:
            matchingWords = {}
            for each lemmaId in lemmaIds:
                matchingWords[lemmaId] = text.lemmata[lemmaId].length  // count per lemma

            results.push({filename, title, author, matchingWords, totalWords})

    return results
    // No dedup needed — each text can only appear once (checked via containsAll)
```

**Note:** No dedup needed here because the intersection check (`every`) guarantees each text appears at most once.

---

## D. External API Contracts

### D.1 Wikidata Image Fetch

**Trigger:** Reading view opens a text whose work has a `wikidata` field in the authority index.

Source: `assets/js/rendering/tei-text-reader.js` → `getWikidataImage()` (~line 939; P18 `wbgetclaims` request at ~line 944)

**Request chain (3 sequential calls):**

```
1. GET https://www.wikidata.org/w/api.php
     ?action=wbgetclaims&property=P18&entity={wikidataId}&format=json&origin=*
   Response: { claims: { P18: [{ mainsnak: { datavalue: { value: "Filename.jpg" }}}]}}
   Extract: filename from claims.P18[0].mainsnak.datavalue.value

2. Image URL (no API call):
   https://commons.wikimedia.org/wiki/Special:FilePath/{filename}?width=400

3. GET https://commons.wikimedia.org/w/api.php
     ?action=query&titles=File:{filename}&prop=imageinfo&iiprop=extmetadata&format=json&origin=*
   Response: { query: { pages: { "-1": { imageinfo: [{ extmetadata: {
     Artist: { value: "..." },
     LicenseShortName: { value: "CC BY-SA 3.0" }
   }}]}}}}
   Extract: Artist.value (HTML — cleaned to text), LicenseShortName.value
```

**Error handling:** All calls wrapped in try/catch. On any failure, image section stays hidden (graceful degradation).

### D.2 Wörterbuchnetz API

**Single implementation:** `assets/js/lib/woerterbuchnetz.js` (`fetchWbnetzEntries`, `decodeHtmlEntities`) – shared by both call sites; do NOT re-implement the fetch inline.

**Triggers:**
- Lemma page loads (`lemma/lemma-page.js`, `fetchWoerterbuchnetz`, #73)
- Korpus search renders the lemma panel (`assets/js/app.js`, `fetchWbnetzLinksInto`, #114 – up to 3 lemmata per search)

```
GET https://api.woerterbuchnetz.de/open-api/dictionaries/{sigle}/lemmata/{normalizedForm}

Parallel requests for: MWB, Lexer
Uses: Promise.all() (each request individually try/catch-guarded,
      so one failure yields empty entries instead of rejecting)
Caching: memoized per normalizedForm for the browser session
      (repeat searches must not re-hit the external API)
Safety: entries whose wbnetzlink is not http(s) are dropped by the
      shared client; callers must still attribute-escape values
      (incl. quotes) before interpolating into href="..."

Response: {                              // illustrative shape, IDs schematic
    result_set: [{
        sigle: "Lexer",
        lemma: "br&ocirc;t",     // HTML-encoded — decode via DOMParser (see below)
        gram: "stN",
        wbnetzid: "L02435",
        wbnetzlink: "https://www.woerterbuchnetz.de/Lexer/L02435"
    }]
}
```

**HTML entity decoding:** `lemma` field contains HTML entities. Decoded via the shared `decodeHtmlEntities` from `lib/woerterbuchnetz.js` – implemented with `DOMParser('text/html')` + `textContent`, NOT the textarea-`innerHTML` trick: a `</textarea><img onerror=…>` payload would create live elements during the `innerHTML` write (mXSS class), before any downstream escaping runs. DOMParser documents have no browsing context (no script execution, no resource loads).

**Datenschutz:** Both triggers send the normalized lemma form to a third party; documented in `impressum.html` → Datenschutz („Wörterbuch-Verweise").

### D.3 Static External Links (no API calls)

| Target | URL Pattern | Source |
|--------|------------|--------|
| Old MHDBDB | `https://mhdbdb-old.sbg.ac.at/mhdbdb/App?action=Dic&lid={numericId}` | `lemma-page.js:239` |
| REALonline (IMAREAL) | `https://realonline.imareal.sbg.ac.at/suche#{json}` where json = `{"s":"{normalized}"}` | `lemma-page.js:244` |
| Corpus search | `../korpus.html?search={lemma.lemma}` – ausgewertet in `app.js` `handleURLParameters()` (#144): befüllt das Suchfeld und löst die normale Suche aus | `lemma-page.js:249` |
| GND (person/work) | `https://d-nb.info/gnd/{gndId}` | `tei-text-reader.js` |
| Wikidata (person/work) | `https://www.wikidata.org/wiki/{wikidataId}` | `tei-text-reader.js` |
| Handschriftencensus | URL stored in authority index `work.handschriftencensus` | `tei-text-reader.js` |
| Zotero | URL stored in `work.biblStructs[].corresp` | `tei-text-reader.js` |

### D.4 MWB Online Metadata API (blocked)

```
GET http://tares-neu.uni-trier.de:8080/exist/rest/db/MWB/Services/retrieve_MWB_lemma_metadata.xql?lemma={term}

Response (XML):
<entry>
  <MWB><id>...</id><lemma>...</lemma><gram>...</gram><url>https://www.mhdwb-online.de/wb/{id}</url></MWB>
  <MWV><lexer>...</lexer><bmz>...</bmz><fb>...</fb></MWV>
</entry>
```

**Status:** HTTP-only API. Blocked by mixed content when called from HTTPS page. Currently using static link only. Upgrade to dynamic lookup when MWB team migrates to HTTPS.

### D.5 Lemma Page URL Routing Contract

**Contract:** The URL `/lemma/{numericId}` MUST resolve to a rendered lemma page. This URL is stored by external systems (Worterbuchnetz, MWB, Wikidata P9351) and must remain stable indefinitely.

**Why:** External dictionary networks link to MHDBDB lemmata by numeric ID. Breaking these URLs breaks scholarly infrastructure across institutions.

Source: `404.html` (redirect), `lemma/lemma-page.js:48-72` (parsing)

```
URL routing (GitHub Pages, no server-side routing):

1. /lemma/879          → 404.html intercepts
   404.html:           → detects 'lemma' in path, extracts '879'
                       → window.location.replace('/lemma/?id=879')
   lemma/index.html:   → loads lemma-page.js
   parseLemmaId():     → reads ?id=879 → returns '879'

2. /lemma/?id=879      → direct (no redirect needed)
   parseLemmaId():     → URLSearchParams.get('id') → '879'

3. /lemma/#879         → direct (no redirect needed)
   parseLemmaId():     → window.location.hash.slice(1) → '879'

Parse order: ?id > #hash > path segment (first match wins)
```

**ID mapping:** `numericId` → `lemma_{numericId}` (internal key) = Wikidata P9351 value = Worterbuchnetz `lid`

---

## E. Cache Invalidation

### IndexedDB Databases

| Database | Library | Store | Key | Used By |
|----------|---------|-------|-----|---------|
| `MHDBDBMainSite` | Dexie.js | `indices` | `name` (string) | `assets/js/lib/corpus-loader.js` |
| `MHDBDB_TEI_Cache` | Raw IndexedDB | `parsedTEI` | `filename` (string) | `assets/js/storage/tei-cache-manager.js` |

### Index Cache (MHDBDBMainSite)

**Store schema:** `{ name, version, timestamp, data }`

**Version check flow** (source: `corpus-loader.js:115-158`):

```
getCachedIndex(name):
    cached = db.indices.get(name)
    if !cached → return null (cache miss)

    // Version check (konkrete Konstanten siehe corpus-loader.js; aktueller Stand TEI-MODEL.md §11)
    if name === 'corpus-index':
        if cached.version !== INDEX_VERSION:           → invalidate
    if name === 'authority-index':
        if cached.version !== AUTHORITY_INDEX_VERSION: → invalidate

    // Expiration check
    age = Date.now() - cached.timestamp
    if age > 30 days:                                            → invalidate

    return cached.data
```

**Drei-Stellen-Versions-Bump (Pflicht-Synchronizität):**

Bei jedem Index-Schema-Bump müssen drei Stellen synchron gehalten werden, sonst greift die Cache-Invalidate-Logik nicht. Production-User mit altem Cache sehen sonst den neuen Index nie:

1. `scripts/build-corpus-index.py` → `'version': 'X.Y.Z'` im finalen Index-Dict
2. `scripts/build-authority-index.py` → analog
3. `assets/js/lib/corpus-loader.js` → `INDEX_VERSION` und `AUTHORITY_INDEX_VERSION`

Strukturell verankert: `scripts/audit/check-index-versions.py` plus CI-Workflow `.github/workflows/data-integrity.yml` (PR/Push für die drei Files). Lokal `python scripts/audit/check-index-versions.py` vor Commit ausführen; exit 1 bei Drift mit File:Line-Annotation.

**Bump-Pflicht bei Inhaltsänderung (#154):** Die drei Stellen synchron zu halten reicht nicht – auch ein komplett *vergessener* Bump (alle drei Stellen einträchtig auf der alten Version, Index-Inhalt aber geändert) ließe den Cache 30 Tage stale. Gate: `scripts/audit/check-index-version-bump.py --base <rev>` (CI-Step „Index-Versions-Bump-Gate" in `data-integrity.yml`) vergleicht den dekomprimierten Index-Inhalt mit der Diff-Base und fordert bei Änderung einen geänderten `version`-String. Ein Bump ohne Inhaltsänderung bleibt erlaubt (bewusster Cache-Flush).

**How to force refetch:**

| Method | What to change | When |
|--------|---------------|------|
| Corpus version bump | `INDEX_VERSION` in `corpus-loader.js` + `version`-Konstante in `build-corpus-index.py` | After rebuilding corpus index with schema changes |
| Authority version bump | `AUTHORITY_INDEX_VERSION` in `corpus-loader.js` + `version` in `build-authority-index.py` | After rebuilding authority index with schema changes |
| User manual clear | "Alle Daten löschen" button on index.html | Clears all IndexedDB + localStorage |
| Developer clear | Browser DevTools → Application → IndexedDB → delete databases | Debugging |

### TEI File Cache (MHDBDB_TEI_Cache)

**Store schema:** `{ filename, xmlString, etag, lastModified, cachedAt, size }`

**Strategy:** Cache the raw XML string as delivered by the server, restore via `DOMParser`. This avoids re-downloading multi-MB TEI files on repeat visits.

**Freshness (#151):** `load()` sends a conditional GET (`If-None-Match` / `If-Modified-Since` from the stored validators, `cache: 'no-cache'` to bypass the browser HTTP cache) – but at most **once per file per page load** (in-memory `revalidated` Set); later loads of the same file in the same session are pure IndexedDB hits with zero network. Server answers `304` → cached copy is served (one small roundtrip, `cachedAt` refreshed fire-and-forget); `200` → fresh content replaces the cached entry together with its new validators. Corpus updates therefore become visible on the **next page load**, not after a TTL. Entries without validators (legacy, pre-#151) trigger a full fetch once and are upgraded on write.

**Fallback to cache:** The cached copy is served with a console warning when the revalidation fails at network level (offline, 15s timeout via `AbortSignal.timeout`), when the server answers with an HTTP error (5xx/404 during a deploy window), or when a `200` body does not parse as XML (captive portal). A previously readable text therefore stays readable through server incidents.

**Expiration:** 30-day TTL is storage hygiene only: `cleanExpired()` runs in the background at `init()` (cursor over the `cachedAt` index, values never materialized) and purges entries not loaded/revalidated for 30 days – orphans of renamed or removed TEI files. Freshness is unaffected.

**Corruption handling:** If `DOMParser` returns a `parsererror` element for a cached entry, the entry is deleted; on the `304` path `load()` restarts and performs a plain full download.

---

## F. Authority Source Rules

**Contract:** When corpus annotation and authority files conflict, the corpus is authoritative. `lexicon.xml` and `variants.xml` are derived indexes, not the master.

**Why:** The corpus is edited continuously – both by script ingest and by manual correction (existing data is fixed, not only new data added). If the authority files were treated as master, legitimate corpus edits would be discarded as "errors" when in fact the authority is lagging behind. This rule stops a future session from misreading dangling refs as corpus errors instead of authority gaps to backfill. (#44/#115)

### F.1 Corpus Leads, Authority Follows

When a `<w>` carries a `@lemmaRef` / `@ana` / `@corresp` that does not exist in the target authority file – a **dangling ref** (detector: `scripts/audit/check-authority-cross-refs.py`):

- **Default:** the corpus annotation wins. The authority must gain the missing entry (lemma stub from form + `@pos`; variant via `extract-variants.py`).
- **Exception:** an obvious corpus typo (reference to a never-existing ID, single occurrence, a neighbouring ID exists with the right form) is fixed in the corpus instead.
- `lexicon.xml` is never the master for the question "does this lemma exist?" – the corpus is.

### F.2 Sense Meanings Are Curatorial

A lemma *form* is generatable from the corpus (word form + `@pos`). A sense *meaning* (its `concepts.xml` assignment) is NOT – it is assigned manually by the team (KZW / Julia). A backfill can therefore only create lemma/sense **stubs**; the semantic classification stays curatorial handwork. Phase-3 ingest records (e.g. WZB) hold resolved-sense IDs but no semantic classification.

### F.3 Ingest Requires Backward Sync

Any ingest pipeline that mints new lemma/sense IDs in the corpus MUST write them into `lexicon.xml` atomically. A forward-only pipeline (annotate corpus without authority sync) produces dangling refs – exactly the WZB drift (#115): Phase 1b minted lemma IDs ≥78000 into the corpus, but no script backfilled `lexicon.xml`. Detector: `scripts/audit/check-authority-cross-refs.py --check` (CI gate in `data-integrity.yml`). Since #152 the tolerated legacy set is pinned as an **ID-set ratchet** in the committed `scripts/audit/lexicon-baseline.json`: any dangling lexicon id outside that set fails CI – including compensating drift (new ids introduced while old ones are backfilled in the same PR). New ids must either be backfilled immediately or deliberately added via `--update-baseline` (KZW decision, reviewable file diff); when backfill lands, run `--update-baseline` and commit the shrunken file so the ratchet keeps gripping (CI emits a `::warning` until you do). See [DECISIONS.md → ADR-015](DECISIONS.md#adr-015-authority-source-modell-korpus-führt-ingest-braucht-rückwärts-sync). The full normative ingest procedure (Stage-0 conversion → Phases 1–3 → backfill) is documented in [DATA-MODEL.md → Ingest-Verfahren](DATA-MODEL.md#ingest-verfahren-neuaufnahme-von-texten).

**Master of record:** Since the migration (2025-07-22) this repository is the *sole* master for all 8 authority files; there is no Salzburg re-export and no live external source. See [TEI-MODEL-AUTH-FILES.md → Provenienz](TEI-MODEL-AUTH-FILES.md#provenienz-und-aktualitaet).

---

## G. Static JSON API Contract (#45)

**Contract:** The URL *schema* of the static API under `/api/` is stable; the *resources* follow the data. External consumers (MWB, Wörterbuchnetz, citing researchers) build URLs against the schema – breaking it silently breaks every external link.

**Why:** The API is plain files generated by `scripts/build-api.py` from the two indexes. Nothing at runtime enforces the URL structure or field shapes; only this contract and the CI freshness gate do.

### G.1 URL Schema Stability

- Path structure is **permanent**: `api/index.json`, `api/lemmata/index.json` (bundle only, no individual lemma files), `api/<coll>/index.json` + `api/<coll>/{id}.json` for `persons`, `works`, `concepts`, `genres`, `names`, `texts`.
- **No version prefix** (no `/api/v1/`). Schema changes are documented (here and in `api/index.html`), not versioned – additive changes are allowed, renames/removals of paths or fields are breaking and need an explicit decision.
- The `{id}` is the record ID exactly as in the indexes (`person_445`, `work_WZB`, text sigle `WZB`), filesystem- and URL-safe by build-time assertion (pattern check + case-insensitive uniqueness, Windows FS).

### G.2 Resources Follow the Data (no record permanence)

- An individual `{id}.json` exists exactly as long as the record exists in the source index. The build **wipes all `api/**/*.json` before writing** (orphan protection) – a removed record's file disappears, by design.
- There is **no promise of record permanence**, only of schema permanence. Removed states remain traceable via git history (the whole `api/` tree is committed).

### G.3 Field Schemas

- **Every emitted file** carries `"license": "CC BY-NC-SA 4.0"`. Collection indexes are `{"license", "items"}`.
- **Root manifest** (`api/index.json`): `project`, `license`, `contact`, `documentation`, `sources` (the two index versions – provenance for every consumer), `collections` (`href` + `count` each).
- **Summary list schemas** (`items[]` per collection): persons `{id, preferredName}`; works `{id, title, sigle}`; concepts/genres/names `{id, termDE, termEN}`; texts `{id, title, author, wordCount}`.
- **Full records** are the index records verbatim, plus `license`, with two transformations: `persons.works` is normalized from comma-string to a JSON array; texts are stripped of the heavy `words`/`lemmata`/`lineStarts`/`lineEnds` arrays (full token data stays in `data/corpus-index.json.gz` and `tei/`). Verbatim means additive index fields flow into the API automatically – e.g. lemma records carry `posAll[]` (every `<pos>` value; `pos` stays the first one) since Authority Index v1.6.0 (#161).
- **Ref convention:** cross-references stay raw as in the source XML/indexes (`persons.xml#person_786`, `lexicon.xml#lemma_879_sense_1449`). Consumers parse the ID as the substring **after `#`**; the part before `#` names the source authority file, not an API path.

### G.4 Determinism = CI Gate Basis

Same committed index state → byte-identical `api/` output (no timestamps, no randomness, compact `json.dumps`, iteration in index list order – the #125 principle). This is what makes the CI check "Freshness API (#45)" in `data-integrity.yml` possible: rebuild + `git diff` (plain JSON, no decompression step). Anything non-deterministic added to `build-api.py` turns the gate into a permanent false alarm.
