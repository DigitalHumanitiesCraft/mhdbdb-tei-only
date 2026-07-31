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
| 0 | | o + U+0306 | ŏ | dito | dito |
| 1 | Lowercase | all | lowercase | `.toLowerCase()` | `.lower()` |
| 2 | Long vowels (circumflex + macron) | â ā | a | `/[âā]/g` | `.replace('â','a').replace('ā','a')` |
| 2 | | ê ē | e | `/[êē]/g` | `.replace('ê','e').replace('ē','e')` |
| 2 | | î ī | i | `/[îī]/g` | `.replace('î','i').replace('ī','i')` |
| 2 | | ô ō | o | `/[ôō]/g` | `.replace('ô','o').replace('ō','o')` |
| 2 | | û ū | u | `/[ûū]/g` | `.replace('û','u').replace('ū','u')` |
| 3 | Umlauts → digraphs | ä | ae | `/ä/g` | `.replace('ä','ae')` |
| 3 | | ö | oe | `/ö/g` | `.replace('ö','oe')` |
| 3 | | ü | ue | `/ü/g` | `.replace('ü','ue')` |
| 3 | Breve-Umlaute (WZB, #224) | ŏ | oe | `/ŏ/g` | `.replace('ŏ','oe')` |
| 3 | | ŭ | ue | `/ŭ/g` | `.replace('ŭ','ue')` |
| 4 | Ligatures | æ | ae | `/æ/g` | `.replace('æ','ae')` |
| 4 | | œ | oe | `/œ/g` | `.replace('œ','oe')` |
| 5 | Special | ǒ | o | `/ǒ/g` | `.replace('ǒ','o')` |

### Test Cases

These 23 cases must pass in both languages (der `None`-Fall ist Python-only, die JS-Liste hat entsprechend 22). Source: `scripts/mhg_normalizer.py` → `TEST_CASES`, gespiegelt in `testing/tests/normalization-parity.spec.js`

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
| `bo` + U+0308 + `ses` | `boeses` | Schritt 0: zerlegtes ö komponiert vor Schritt 3 (#224) |
| `Mu` + U+0308 + `hldorf` | `muehldorf` | dito mit ü, plus Grossbuchstabe |
| `bo` + U+0306 + `ses` | `boeses` | Der gemeldete Fall: Breve, Schritt 0 komponiert zu ŏ, Schritt 3 löst auf (#224) |
| `bŏses` | `boeses` | dito, schon präkomponiert |
| `wŭnschet` | `wuenschet` | ŭ → ue |
| `''` | `''` | Empty string |
| `None`/`null` | `''` | Null handling |

### Common Pitfall

`schône` (ô = circumflex) → `schone`, NOT `schoene`. The circumflex ô maps to plain `o`, while the umlaut ö maps to `oe`. Visually similar, semantically different.

### Schritt 0: Unicode-Komposition (#224)

Ein „ö" kann als ein Zeichen (U+00F6) oder als `o` + kombinierendes Trema (U+006F U+0308) kodiert sein. Beide sehen identisch aus, aber nur die komponierte Form trifft die Umlaut-Regel in Schritt 3. Ohne die Komposition fällt eine zerlegte Eingabe durch Stufe 1 **und** Stufe 2 der Lemma-Auflösung (§C) und landet im Partial-Match-Fallback. Der Bug-Report #224 ist genau dieser Fall, nur mit einem anderen Diakritikum: die gemeldete Eingabe trug `o` + kombinierendes **Breve** (U+0306), kopiert aus der WZB-Leseansicht. Schritt 0 komponiert das zu `ŏ`, und erst die Breve-Regel in Schritt 3 macht daraus `oe`. Beide Schritte zusammen sind der Fix, keiner allein.

Zerlegte Formen entstehen beim Kopieren aus macOS-Quellen und aus manchen Editionsdatenbanken, sind also normale Nutzereingaben.

**Breve statt Trema (WZB, #224).** Die Wenzelsbibel schreibt Umlaute mit Breve: der Korpus-Token `bo` + U+0306 + `ses` trägt `lemmaRef` auf `lemma_788` (`bœse`), `scho` + U+0306 + `ne` auf `lemma_5280` (`schœne`), `wŭnschet` ist `wünschet`. Belegt an 469 lemmatisierten WZB-Tokens. Deshalb `ŏ` → `oe` und `ŭ` → `ue` in Schritt 3. Breve auf anderen Basiszeichen bleibt unangetastet: 136 weitere WZB-Tokens (w 91, n 22, y 5, a 5, v 4, r 2, m 2, i 2, e 2, z 1). Der Grund ist, dass es dort keine Umlaute sind (`hălses`, `nămen`, `geslăgen`, `schĕpfen`, `erschĭnen`), nicht eine fehlende präkomponierte Form – für `a`, `e` und `i` gibt es sie (U+0103, U+0115, U+012D), und Schritt 0 erzeugt sie auch. **Bekannte Restlücke:** 64 dieser 136 Tokens sind lemmatisiert (48 auf `w`, 16 auf `n`, etwa `few̆er` → `viur`, `wenn̆` → `wan`) und bleiben per Copy-Paste aus der Leseansicht unauffindbar. Eine Regel dafür wäre eine editorische Entscheidung über die böhmische Schreibkonvention, keine technische.

**Wirkung auf die Build-Seite:** Der Schritt ändert die Ausgabe an genau drei Stellen, weil die Authority-Files sonst NFC sind. Betroffen sind die Datensätze mit zerlegtem ü in `persons.xml` und `works.xml`:

| Datensatz | vorher | nachher |
|-----------|--------|---------|
| `person_1052` Hugo von Mühldorf | `hugo von mühldorf` | `hugo von muehldorf` |
| `person_1332` Wachsmut von Mühlhausen | `wachsmut von mühlhausen` | `wachsmut von muehlhausen` |
| `work_435` Lyrik von Hugo von Mühldorf | `lyrik von hugo von mühldorf` | `lyrik von hugo von muehldorf` |

Alle drei waren über die normalisierte Suche nicht auffindbar. Alle 43.879 Lemma-Normalisierungen und alle 234.244 Varianten-Schlüssel bleiben unverändert. Deshalb Authority-Index v1.6.2. **Die 234.244 sind der Stand von v1.6.2, nicht der heutige** (heute 234.243, siehe §C): #138 hat mit den HUG-Strophenziffern den nur dort belegten Typ `type_195524` „cxlvix" mitgenommen, gemessen am Blob vor `87b6dc941`. Die Differenz von eins ist also ein realer Datenschritt und kein Tippfehler in einer der beiden Zeilen (#277).

**Nicht betroffen:** Der Korpus-Index speichert Lemma-IDs und Positionen, keine normalisierten Textformen; `build-corpus-index.py` importiert `normalize_mhg` zwar, ruft es aber nirgends auf. Zum Korpustext selbst ist die prüfbare Aussage schärfer als die ursprünglich hier notierte Stichprobe: **in `<w>` gibt es korpusweit kein einziges kombinierendes Trema und keine kombinierende Tilde.** Die 1.343 Tremata in 567 der 667 Dateien stehen sämtlich außerhalb der annotierten Tokens, größtenteils in `<note>`-Bibliographieprosa des teiHeader (Verlagsorte wie Tübingen, Zürich). In `<w>` stehen insgesamt 774 kombinierende Marken, davon 752 WZB-Breves und 22 Exoten: 11 Punkt darunter, 8 Makron, 3 U+035B (Abbreviatur-Zickzack in `cetera͛`, `her͛re`).

**Kein Gewinn, aber derselbe Topf:** In `<w>` stehen acht kombinierende Makra (u 3, p 2, d 1, i 1, n 1). Schritt 0 komponiert davon vier, die drei `u` zu `ū` und das `i` zu `ī`; Schritt 2 löst beide auf. Für `d`, `n` und `p` gibt es keine präkomponierte Form. **Auffindbar werden sie dadurch trotzdem nicht: keines der acht Tokens trägt ein `@lemmaRef`** (`flūte`, `Dorūmbe`, `cap̄`, `vn̄`). Sie gehören in denselben Backfill-Topf wie die 289 Kandidaten unten, nicht in eine Gewinn-Spalte.

**Berührt, aber nicht in diesem PR nachgezogen:** Die WZB-Ingest-Skripte (`scripts/ingest/wzb/wzb-auto-match.py`, `-sense-assign.py`, `-sense-apply.py`) normalisieren über dieselbe Funktion. 289 WZB-`<w>` mit o/u-Breve tragen bisher kein `@lemmaRef`, weil das Breve am Matcher stehenblieb; ein Re-Run wird einen Teil davon auflösen. Siehe ADR-016.

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

**Eine dokumentierte Ausnahme:** der XML-Fallback der Nähesuche für hochgeladene Dateien (`tei-manager.js`, `findCooccurringLemmas`) zählt alle `<w>`, auch die ohne `@lemmaRef`. Der Unterschied ist erheblich: über alle 667 Korpusdateien tragen 1.898.318 von 9.431.316 `<w>` kein `@lemmaRef`, also 20,1 % (Spitzenwerte AUP 41,6 %, REF 39,3 %, DL1 38,8 %; 145 Dateien tragen durchgehend `@lemmaRef`). Nachzurechnen mit einem Zähllauf über `tei/*.tei.xml`, der je Datei die `<w`-Starttags mit und ohne `lemmaRef=` gegenüberstellt. Innerhalb dieses Pfades bleibt es konsistent, weil Positionen und Kontextfenster aus derselben Liste stammen; ein `maxDistance` von 10 heißt dort aber „10 Tokens" statt „10 lemmatisierte Tokens". Ergebnisse beider Pfade dürfen deshalb nicht vermischt oder verglichen werden. Nicht angeglichen, weil hochgeladene Dateien nicht lemmatisiert sein müssen und ein `[@lemmaRef]`-Filter dort im Zweifel alles verwerfen würde.

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

**Applies to all highlight/match paths**, all routed through the single `lemmaRefMatchesId` since #130 (was 6 inline copies across 4 files, the duplication that made #126 possible): `tei-text-reader.js` (single + multi-lemma) and the playground (`tei-manager.js` proximity + enrichment, `ui-helpers.js` context highlight). (`text-renderer.js` was a fourth call site until its dead render path, then the whole shim, were removed: audit #42 plus Carearbeit 2026-07.) Validated on real corpus data: PL1 689 → 57, OVG 369 → 26 (matches the result-card count).

### Test Coverage

`testing/tests/lemma-matching.spec.js` (#130). Block 1 asserts the §B.1 case table against the real `lemmaRefMatchesId`; Block 2 is an e2e reader assertion (`korpus.html?textId=PL1&lemmaIds=lemma_308` → exactly 57 `.highlight`, OVG → 26). Verified to fail red against the pre-#126 substring logic.

---

## C. 3-Stage Lemma Resolution Algorithm

**Contract:** Search resolves user input to lemma IDs through exactly 3 stages, in order, with early return.

**Why:** MHG has extensive orthographic variation. A single lemma can appear as dozens of attested forms. The 3-stage approach balances precision (exact first) with recall (fuzzy last).

Source: `assets/js/search/search-engine.js` (`resolveLemmaIds`), `playground/js/data/authority-manager.js` (`searchLemmaByOrthography`). Das Stage-3-Prädikat und sein Ranking-Abstand liegen seit #224 gemeinsam in `assets/js/lib/lemma-resolve.js`; beide Oberflächen importieren sie. Geteilt ist ausdrücklich nur Stufe 3: Stufe 1 unterscheidet sich weiterhin (die Hauptseite vergleicht gegen das vorberechnete `lemma.normalized` des Index, der Playground normalisiert zur Laufzeit und rankt Homographen zusätzlich nach Korpus-Frequenz). Den Frequenz-Tie-Break setzt der Playground seit #224 auch in **Stufe 3** ein, nach der Längendistanz und vor der Index-Reihenfolge (`authority-manager.js`, `searchLemmaByOrthography`). Der Pseudocode unten bildet die Hauptseiten-Sortierung ab; wer die Playground-Reihenfolge braucht, liest die Lehre aus #163/#164 mit: bei gleicher Distanz gewinnt das häufigere Lemma, weil `matches[0]`-Konsumenten still den ersten Treffer nehmen.

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
    return results.map(lemma => lemma.id)                          // May be empty
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
- 234,243 normalized entries (Stand 2026-07-28; 256,760 raw forms in variants.xml, deduped first-occurrence-wins), extracted from `authority-files/variants.xml`
- **Zwei Zahlen, die verschieden bleiben müssen:** 256.760 ist die Zahl der Rohformen in `variants.xml`, 234.243 die Zahl der Mappings im Runtime-Dictionary nach der Deduplizierung. Wer „variants dictionary" schreibt, meint die kleinere. Wer 234.244 liest, liest den Stand vor #138 (§A, Schritt 0)
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

### C.2.2 Playground: Proximity Window Selection and Context Dedup

Source: `playground/js/data/tei-manager.js` (`findCoveringWindow`, `searchProximityUsingEnhancedIndex`)

Two steps that both changed with #169 (KZW decision 2026-07-28). Numbers from before 2026-07-29 are not comparable for searches with three or more lemmata; see the JOURNAL entry of that date.

**Caveat on the input positions.** This function builds its per-lemma position lists by scanning `words[]` for equality, so it is first-id only and does not follow the §B.1 consumer rule (the verse search next to it does, via `lemmata{}`). Same standing justification as `cooccurrence-ranking.js`: 0 multi-ref cases in the corpus today. It becomes wrong the moment a `<w>` carries two `@lemmaRef` ids.

**Step 1 – window selection.** `maxDistance` bounds the SPAN of all matched positions, not each position's distance to the anchor lemma. A hit requires one window of width `maxDistance` that holds the anchor and one occurrence of every other lemma.

`maxDistance` is clamped to the range the UI declares (`0…50`, from `input#proximityDistance[max=50]`) before the search runs, with a non-numeric value falling back to 10. The hash route only validates `dist > 0`, and unlike the old anchor test the window search gets more expensive as the distance grows, so the data layer enforces the bound itself rather than trusting the surface.

**Precondition on the lemma list (same reasoning, one level over).** Both enhanced paths, `searchProximityUsingEnhancedIndex` and `searchVerseUsingEnhancedIndex`, normalise their `lemmaIds` once to bare ids (`lemma_7532` and `7532` are the same lemma), deduplicate them, and continue with that list. **With fewer than two remaining ids they return `[]` before searching.** Without this, a search degenerates silently: `findCoveringWindow` has no list left to cover and returns an empty array, which is truthy, and the caller only tests `chosen === null`, so every occurrence of the single lemma would be reported as a hit with distance 0. The verse path degenerates the same way for a different reason: its comparison loop starts at `i = 1` and never runs, leaving `allInVerse` true. Duplicates reach this point in practice because different inputs resolve to the same lemma (`wîn` via stage 1, `wein` via the variants list). The pseudocode below therefore describes a case, the empty `otherPositionLists`, that the enhanced paths can no longer produce; it is kept because `findCoveringWindow` is also tested directly.

```
function findCoveringWindow(firstPos, otherPositionLists, maxDistance):
    // otherPositionLists = ascending position arrays, one per non-anchor lemma
    if otherPositionLists is empty: return []

    // An optimal window always starts on an occupied position
    candidates = {firstPos}
    for each list in otherPositionLists:
        candidates += every p in list with firstPos - maxDistance <= p <= firstPos

    best = null, bestSpan = INFINITY
    for each windowStart in sorted(candidates):
        windowEnd = windowStart + maxDistance
        if firstPos > windowEnd: continue

        chosen = []
        for each list in otherPositionLists:
            p = first element of list >= windowStart     // binary search
            if p does not exist OR p > windowEnd: mark uncovered, break
            chosen.push(p)
        if uncovered: continue

        span = max(firstPos, ...chosen) - min(firstPos, ...chosen)
        if span < bestSpan: bestSpan = span, best = chosen

    return best        // null when no window carries all lemmata
```

**Why the search over window starts, not just a range check.** Until 2026-07-29 each further lemma was tested against `firstPos` alone (`positions.find(p => abs(p - firstPos) <= maxDistance)`), so B at anchor−5 and C at anchor+5 both passed at `maxDistance` 5 although they sit 10 apart; `actualDistance` then reported the 10 correctly in the very same result object. Adding a span check on top of the old selection would not fix it, because `find()` returns the FIRST position in anchor range, not the most useful one. With B = {90, 110}, C = {109}, `firstPos` = 100 and `maxDistance` = 10 that selection yields B = 90, span 19, and the hit would be dropped although B = 110 with C = 109 spans exactly 10. Iterating the possible window starts also keeps the reported distance minimal.

**Step 2 – context dedup.** Overlapping context windows in the same file collapse to the one with the SHORTEST distance.

```
function deduplicateProximityResults(rawMatches):
    // rawMatches = [{filename, matchPositions, distance, contextStart, contextEnd, ...}, ...]
    byFile = groupBy(rawMatches, 'filename')
    deduplicated = []

    for each (filename, fileResults) in byFile:
        byDistance = COPY of fileResults sorted by (distance asc, contextStart asc)

        kept = []
        for each result in byDistance:
            overlaps = kept.any(existing =>
                max(existing.contextStart, result.contextStart)
                    < min(existing.contextEnd, result.contextEnd)
            )
            if NOT overlaps: kept.push(result)
            // else: discard — the kept match is the closer one by construction

        sort kept by contextStart ascending      // output follows the text
        deduplicated += kept

    return deduplicated
```

**Behavior:** the closest co-occurrence in a passage wins; output order stays reading order. Before 2026-07-29 the sort key was `contextStart`, so the EARLIEST match won while the comment and the console log claimed "keeping shorter distance" (#169 finding 48). Users were shown the more distant co-occurrence whenever the earlier window happened to be the wider one.

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

**Single implementation:** `assets/js/lib/woerterbuchnetz.js` (`fetchWbnetzEntries`, `decodeHtmlEntities`, `DICTIONARIES`, `DICTIONARY_TITLES`, `dictionaryTitle`) – shared by all three call sites; do NOT re-implement the fetch inline.

**Triggers:**
- Lemma page loads (`lemma/lemma-page.js`, `fetchWoerterbuchnetz`, #73)
- Korpus search renders the lemma panel (`assets/js/app.js`, `fetchWbnetzLinksInto`, #114 – up to 3 lemmata per search)
- Hapax tool expands a row's detail panel (`playground/js/ui/tei/hapax-legomena.js`, #196 – one lookup per expanded row)

```
GET https://api.woerterbuchnetz.de/open-api/dictionaries/{sigle}/lemmata/{normalizedForm}

Parallel requests for: MWB, Lexer, LexerN, BMZ, FindeB   (five since #258, 2026-07-31)
Uses: Promise.all() (each request individually try/catch-guarded,
      so one failure yields empty entries instead of rejecting)
Caching: memoized per normalizedForm for the browser session
      (repeat searches must not re-hit the external API)
Safety: entries whose wbnetzlink is not http(s) are dropped by the
      shared client; callers must still attribute-escape values
      (incl. quotes) before interpolating into href="..."
Dedup: within one dictionary, a wbnetzlink already seen is dropped —
      FindeB repeats a wbnetzid across spelling doublets and would
      otherwise render as several identical links. Deliberately NOT
      global: the same deep-link under two sigles is two articles.
Returns: [{sigle, entries, failed}] — `failed` marks the empty lists
      that mean "request did not go through" (timeout, network, 5xx)
      rather than "no such headword" (4xx). Link renderers may ignore
      it; any caller that turns an empty result into a STATEMENT about
      the evidence must not (see below).

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

**Dictionary list and order.** `DICTIONARIES` is query order and display order in one; `DICTIONARY_TITLES` resolves the sigles, which the API itself does not expose (`/dictionaries` returns sigle + path only, no titles). Rendering rule per surface: the lemma page, as the deep-dive surface, spells the title out as a heading above each dictionary group and shows every entry; the two compact surfaces (korpus lemma panel, hapax detail cell) carry the title as a `title` attribute on the sigle and cap each dictionary at three entries. The `gram` value belongs in the link text on all three: several entries of one dictionary are homographs and would otherwise render as identical adjacent links.

**Not a defect:** a dictionary returning zero entries for a well-attested word. The MWB is still being published; measured 2026-07-31 it has no entry for `minne` or `vriunt`, while `herze` and `liebe` resolve. Do not treat that as a broken endpoint and do not build a workaround.

**Absence of a link is not absence of attestation.** The hapax tool (#196) is the one consumer that reads an empty result as evidence („Kandidat für ein echtes Hapax"). It must therefore branch on `failed`: on a full outage it says the evidence is not checkable, on a partial one it names the dictionaries that did not answer. Any future consumer that draws a philological conclusion from an empty result carries the same obligation, otherwise a network fault is published as a finding.

**HTML entity decoding:** `lemma` field contains HTML entities. Decoded via the shared `decodeHtmlEntities` from `lib/woerterbuchnetz.js` – implemented with `DOMParser('text/html')` + `textContent`, NOT the textarea-`innerHTML` trick: a `</textarea><img onerror=…>` payload would create live elements during the `innerHTML` write (mXSS class), before any downstream escaping runs. DOMParser documents have no browsing context (no script execution, no resource loads).

**Datenschutz:** All three triggers send the normalized lemma form to a third party; documented in `impressum.html` → Datenschutz („Wörterbuch-Verweise"), which names the queried dictionaries and must be updated whenever `DICTIONARIES` changes.

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
| `MHDBDB_Playground` | Raw IndexedDB | `tei_files` | `filename` (string) | `playground/js/indexed-db-manager.js` |

**`MHDBDB_Playground` hält genau einen Store:** `tei_files`, die vom Benutzer selbst hochgeladenen TEI-Dateien, ohne Ablauffrist. Korpus- und Authority-Daten liegen auch im Playground im gemeinsamen `CorpusLoader` (`MHDBDBMainSite`), nicht hier. Ein zweiter Cache-Pfad darf nicht wieder entstehen: DB-Version 3 löscht die drei schreiberlosen Altstores `corpus_tei_files`, `authority_files` und `metadata` aus bestehenden Browser-Datenbanken (#280).

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
- **Full records** are the index records verbatim, plus `license`, with two transformations: `persons.works` is normalized from comma-string to a JSON array; texts are stripped of the heavy `words`/`lemmata`/`lineStarts`/`lineEnds` arrays (full token data stays in `data/corpus-index.json.gz` and `tei/`). Verbatim means additive index fields flow into the API automatically – e.g. lemma records carry `posAll[]` (every `<pos>` value; `pos` stays the first one) since Authority Index v1.6.0 (#161), and the curated fields `origin` (source languages + attribution) plus `senses[].definition` / `senses[].comment` since v1.7.0. The curated fields are **present only where curated** (1 lemma today) – consumers must treat them as optional, never as a schema promise per record. `origin.languages[]` is an **unordered set of origin layers**, source and transmission language alike; which is which is stated in the German prose of `origin.attribution`, not machine-readable. It is kept congruent with the language concepts in the `concept_23123000` subtree by curation rule (TEI-MODEL-AUTH-FILES §3.1), not by the build. The `*Resp` fields carry `contributors.xml#contrib_N` verbatim per §G.3's ref convention; `contributors.xml` is deliberately absent from the authority index, so resolving the ID to a person name needs the XML file, not the API. Since v1.8.0 (#307) person records carry the same kind of optional pair: `altNames[]` (alternative name forms from `persons.xml`, present for 80 of 211 persons) and `altNormalized[]`. The two are **index-parallel by contract** – `altNormalized[i]` is `normalizeMHG(altNames[i])` – because the person explorer matches on the normalized entry and displays the readable one at the same position. A consumer that filters or reorders one list must do the same to the other. `@xml:lang` from the source is deliberately not carried: for a person both language forms name the same individual, so an alternative is a search key, not a display label (unlike concepts, where `termDE`/`termEN` are distinct labels and both get shown). One consequence to know before anyone asks for the language back: the dedup collapses the 34 cases where the German and English form are the same string, so a later parallel `altLangs[]` would have to carry a list per entry, not a single value.
- **Ref convention:** cross-references stay raw as in the source XML/indexes (`persons.xml#person_786`, `lexicon.xml#lemma_879_sense_1449`). Consumers parse the ID as the substring **after `#`**; the part before `#` names the source authority file, not an API path.

### G.4 Determinism = CI Gate Basis

Same committed index state → byte-identical `api/` output (no timestamps, no randomness, compact `json.dumps`, iteration in index list order – the #125 principle). This is what makes the CI check "Freshness API (#45)" in `data-integrity.yml` possible: rebuild + `git diff` (plain JSON, no decompression step). Anything non-deterministic added to `build-api.py` turns the gate into a permanent false alarm.

---

## H. Analysis Tools: Counting Rules (#281)

**Contract:** the tools below emit *numbers that can be cited*. Each number's counting rule is normative and must not be changed silently. A different reference corpus, a different denominator or a different threshold produces a different published figure from the same data.

**Why this section exists:** §A to §C cover the search chain, which is where wrong behavior is *visible*. Analysis output is different: a keyness value computed against the wrong reference corpus looks exactly like one computed against the right one. The rebuild test ("could I delete every `.js`/`.py` and reconstruct it from the docs?") failed for these four, while it passed for search, build pipeline and reader.

**Scope note that applies to all four:** none of them reads the corpus-search text selection. The main-site checkbox selection (`corpusData.includedTexts`) filters *search results*; every tool here works on the full corpus index and defines its own scope. This is intentional and is the single most misreadable property of the whole section.

### H.1 Keyness (signed log-likelihood, #114)

Source: `assets/js/app.js`, `computeKeyness()` and `logLikelihood()`. Rendered as a sortable column in the main-site table view, one value per result row (= per text).

**Contingency values** for a row belonging to text *T*:

| | Value | Source |
|---|---|---|
| `a` | hits in *T* | `r.matchCount`, summed over all lemma IDs that matched in *T* |
| `b` | hits in the rest of the corpus | `corpusMatches - a` |
| `c` | **indexed** tokens in *T* | `text.wordCount` |
| `d` | **indexed** tokens in the rest of the corpus | `corpusWordTotal - c` |

"Indexed token" everywhere in §H means what `build-corpus-index.py` counts: a `<w>` that has an `@lemmaRef` **and** non-empty text content. `wordCount` is therefore not "words in the text". Within the statistic this is harmless, because `a`, `b`, `c` and `d` all use the same population. For anyone reconstructing it, it is not: reading `c` as "all `<w>`" produces a different value in every row, and it looks exactly like the right one.

```
# Reference corpus: ALL texts in the corpus index, never the user's selection.
corpusWordTotal = sum(text.wordCount for text in corpusIndex.texts)
corpusMatches   = sum(len(text.lemmata[id])
                      for id in lemmaIds
                      for text in corpusIndex.lemmaIndex[id])

logLikelihood(a, b, c, d):
    if c <= 0 or d <= 0 or (a + b) <= 0: return 0
    e1 = c * (a + b) / (c + d)
    e2 = d * (a + b) / (c + d)
    ll = 0
    if a > 0 and e1 > 0: ll += a * ln(a / e1)
    if b > 0 and e2 > 0: ll += b * ln(b / e2)
    ll *= 2
    return ll if (a / c) >= ((a + b) / (c + d)) else -ll
```

Four properties that are decisions, not implementation details:

1. **The reference corpus is always every text in the corpus index, independent of the text selection.** Deselecting texts changes which rows appear, never the value in a row. The code comment records this as the same reference used in Beutel-Thurow's naming-analysis; that comparability is asserted there, not verified against her data here.
2. **`c` and `d` are total token counts, not non-hit counts.** This is the Rayson/Garside form of the statistic (two-term sum over observed vs. expected), not a full four-cell table. Both are current practice; mixing them up changes every value.
3. **`lemmaIds` is the resolution of the search term, not the set of lemmata that actually produced hits.** Taken from `resolveLemmaIds(normalized(term))`, i.e. the same three-stage resolution the search itself used (§C). Using the hit set instead would make the reference frequency depend on the selection through the back door.
4. **Signing:** relative frequency in the text ≥ relative frequency overall → positive (overrepresented), else negative. Equality counts as overrepresented.

**Thresholds** (df = 1): 3.84 → p < 0.05, 10.83 → p < 0.001. Only 10.83 is used in the UI, as bold + brand color. `keyness` is `undefined` when no results or no index exist, and renders as `–`; sorting maps that to `-Infinity`.

### H.2 Hapax legomena (#196)

Source: `playground/js/ui/tei/hapax-legomena.js`. Scope: the full corpus, always.

```
# Corpus-wide LEMMA frequency, not word-form frequency
counts[lemmaId] = sum over all texts of len(text.lemmata[lemmaId])
entry qualifies  <=>  counts[lemmaId] <= maxFreq        # 1 | 2 | 3
```

- **The threshold is `<=`, not `=`.** "Hapaxlegomena (Frequenz = 1)" is the label for `maxFreq = 1`, where both readings coincide; Dis- and Trislegomena are cumulative (`<= 2`, `<= 3`), so each level contains the previous one.
- **The unit is the lemma, not the word form.** A lemma attested once, in an inflected form, is a hapax here. This is a lemmatized corpus, so lemma frequency is the only figure the index supports; a form-based hapax count would need the token layer.
- **At most 3 occurrences are retained per lemma** during aggregation (hard cap, in text and position iteration order). The display says "Angezeigt sind die ersten N von M Vorkommen" whenever the stored count exceeds them. For `maxFreq <= 3` the cap cannot truncate; it exists so the aggregation stays bounded.
- **Filter chain**, in this order: no authority entry (kept only when neither facet is set) → proper names (`hideNames`, default **on**, any tag `NAM`) → numerals (`hideNumerals`, default **on**, but only when `NUM` is the *sole* tag, so ADJ/NUM compounds survive) → function words (`hideFunctionWords`, default **off**, any tag in `FUNCTION_WORD_POS`, but lemmata with no tags at all are kept) → PoS facet → initial letter. An explicitly chosen PoS facet always overrides the identically named default filter.
- **The percentage in the header uses the unfiltered count** (`rawCount / totalTypes`), and "ausgeblendet" is `rawCount` minus the whole filtered list, not minus the visible page. So the headline figure describes the corpus, not the current filter setting.
- **Per-text tab counts distinct lemmata, not attestations:** `abs` = number of qualifying lemma IDs occurring in that text, `rel` = `abs / text.wordCount * 1000`. The denominator is indexed tokens (see H.1), and the numerator counts types while the denominator counts tokens, so `rel` is a types-per-thousand-tokens rate, not a share.

### H.2a What `lineEnds[]` actually points at (prerequisite for H.3 and H.4)

Both verse tools read `text.lineEnds[]` from the corpus index. Its definition is narrower than "end of verse" and is the main source of misreading:

- An entry exists **only for `<l>` elements containing at least one indexed word.** A verse whose tokens carry no `@lemmaRef` is absent from `lineEnds[]` entirely, and therefore from every count derived from it.
- The entry is the §B position of the **last indexed word** of that verse, not of the last word. If the final token of a verse is unannotated, `lineEnds[]` points at a word inside the verse, and what the rhyme tools treat as the rhyme word is not the rhyme word.
- Every position in `lineEnds[]` is guaranteed to have an ID in `words[]`: the index appends to `words[]` and to the line frame in the same step (`build-corpus-index.py`, single-pass `iterwalk`). Guards of the form `if (!lemmaId) continue` in the consuming code are dead code against a consistent index, not a filter.

**Multi-`@lemmaRef` status:** `words[pos]` stores the **first** ID only, while `lemmata` lists the position under every referenced ID. Measured 2026-07-31: the corpus holds **7,532,982** `<w>` elements with an `@lemmaRef`, and `sum(text.wordCount)` over the built index is the same number, so the non-empty-text guard removes none of them. Of those, **0 carry more than one reference.** Every place below where the two fields are said to diverge is therefore a latent property today, not a present distortion. It becomes real the moment an ingest introduces multi-reference tokens.

### H.3 Rhyme dictionary (#106)

Source: `playground/js/ui/tei/rhyme-dictionary.js`. Scope: full corpus, optionally narrowed by a free-text filter. All three fields are lowercased before comparison: sigle must match exactly, title and author match as substrings.

```
for each text with non-empty lineEnds[] and words[] and containing targetId:
    targetPositions = set(text.lemmata[targetId])
    for k in 0 .. len(lineEnds)-1:
        if lineEnds[k] not in targetPositions: continue
        for delta in (-1, +1):
            j = k + delta
            if j < 0 or j >= len(lineEnds): continue     # no wrap-around
            partnerId = text.words[lineEnds[j]]
            if partnerId == targetId and delta == -1: continue   # count self-rhyme once
            if rhymesWith(normalized[targetId], normalized[partnerId]):
                record pair (k, j)

rhymesWith(a, b):
    return a[-3:] == b[-3:]  or  (len(a) <= 4 and len(b) <= 4 and a[-2:] == b[-2:])
```

- **"Adjacent" means adjacent index in `lineEnds[]`**, i.e. the preceding and following *verse of the same text*, not adjacency by `@n`. The pairing assumption is the rhyming couplet. Cross rhyme (distance 2) is **not** captured, and the UI says so.
- **The two sides of a pair are read from different index fields, deliberately.** The target side uses `text.lemmata[targetId]` (all positions, so multi-`@lemmaRef` tokens count), the partner side uses `text.words[pos]` (the **first** ID only). A partner lemma that only ever appears as a second `@lemmaRef` would therefore be invisible (see H.2a: no such token exists today). Reading the target side the same way would silently drop target attestations, which is the worse error.
- **The rhyme criterion is graphemic, on MHG-normalized lemma forms**, not phonetic, and not on the original token. A partner without a lexicon entry has an empty normalized form and therefore never rhymes. It is a *heuristic*, explicitly a minimal variant; the full treatment (original tokens, phonetics) is parked in #109. The 2-character fallback is gated on both forms being short, otherwise high-frequency short words flood every target.
- Retained evidence per partner is capped at 1000 pairs; the displayed list is capped at 200 partners after the `minCount` filter.

### H.4 Verse-ending profile and "Reim-Druck" (#106 points 2 and 3)

Source: `playground/js/ui/tei/verse-ending-profile.js`. Scope: verse texts only (`lineEnds[]` non-empty), then all of them, or one author, or one text.

```
verseCount  = sum(len(text.lineEnds) for text in scope)
endCounts[l]   = count of verses whose last annotated word maps to lemma l   # from text.words[]
totalCounts[l] = sum(len(text.lemmata[l]) for text in scope)                 # from text.lemmata

shareOfVerses = endCounts[l] / verseCount * 100
rhymePressure = endCounts[l] / (totalCounts[l] or endCounts[l]) * 100
```

- **"Reim-Druck" is scope-local on both sides.** Numerator and denominator come from the same scope, so a value for one text answers "how often does this lemma land at the verse end *in this text*", not "compared to the corpus". At `scope = corpus` the denominator still excludes prose, because prose texts are filtered out before counting.
- **Numerator and denominator come from different index fields:** `endCounts` reads `text.words[pos]` (first `@lemmaRef` only), `totalCounts` reads `text.lemmata` (every ID). With multi-reference tokens present, the numerator could only ever lose attestations while the denominator stays exact, so the figure would be too *low*, never too high. Today the two fields agree (H.2a: 0 multi-reference tokens), so the value is exact. This is a property to preserve, not a defect to fix: an ingest that introduces multi-reference tokens silently biases this column downward.
- **The `|| endCount` fallback** in the denominator turns a missing total into 100 %. It cannot trigger from consistent index data (a verse-ending attestation is also an attestation) and exists as a division guard.
- `sum(shareOfVerses)` over all lemmata is **exactly 100 %** (up to rounding), because `verseCount` and `endCounts` are built from the same `lineEnds[]` entries and every entry has an ID (H.2a). The share is therefore a share of *annotated* verses; verses without a single annotated token are in neither number. Do not read it as a share of all verses in the text.
- Sorting is by `endCount` only, then truncated to `topN`. The optional function-word filter keeps lemmata with **no** PoS tags, same as in H.2. There is no facet override here: a chosen filter always applies.

### H.5 Normalized figures in the remaining tools

Five tools outside H.1 to H.4 produce derived figures. Each is simple enough that a formula suffices, but the **base of each ratio** is not obvious from the UI label, and most of them do not divide like over like.

```
# Word frequency, "relative Frequenz" mode      (word-frequency.js)
rel = count(lemma in scope) / totalTokens * 1000

# Lemma distribution, per text                  (lemma-distribution.js)
rel = len(text.lemmata[id]) / text.wordCount * 1000

# Concept distribution, per text                (concept-distribution.js)
rel = sum(len(text.lemmata[id]) for id in concept) / text.wordCount * 1000

# Verse-position search, "(N%)" per text        (verse-position-search.js)
ratio = positionsAtBoundary / len(text.lemmata[id]) * 100

# Text statistics, three columns                (text-statistics.js)
diversity    = uniqueLemmata / wordCount                 # type-token ratio
hapaxRate    = hapaxInText / uniqueLemmata
avgLemmaFreq = sum(len(text.lemmata[id])) / uniqueLemmata
```

Four properties that decide whether a comparison across texts is valid:

0. **Every denominator counts annotated tokens only, the share of annotated tokens differs per text, and what is missing is not a random sample.** `wordCount` and `totalTokens` count `<w>` elements carrying a `@lemmaRef` (§B). Measured 2026-07-31 with `scripts/audit/quantify-unannotated-tokens.py`: of **9,431,294** `<w>` elements, **1,898,312 (20.13 %) carry no `@lemmaRef`**; per-text coverage runs from **58.4 % to 100 %**, median **77.4 %**, 358 of 667 texts below 80 %.

   The size of the gap alone would be harmless. If the unannotated tokens were spread evenly over lemmata, a text annotated at 60 % would lose the same fraction from numerator and denominator, and every per-thousand rate would come out unchanged. **They are not spread evenly.** Of the 1,898,312 unannotated tokens, **1,868,921 (98.5 %) are homographs of forms that *are* annotated elsewhere** in the corpus, i.e. ambiguity cases the legacy system left alone, and they cluster hard on high-frequency function words and pronouns: `in` (128,144), `ir` (111,958), `er` (101,242), `sî` (80,989), `man` (62,285).

   The bias on a rate for lemma *L* in text *T* is `coverage(L) / coverage(T)`, so the direction depends on how well *L* itself is covered relative to the text average, and it **inverts** for a lemma whose own forms sit in the unannotated set (exactly the deliberately skipped homographs of #189). For the content words people usually measure, coverage(L) is above the text average and a sparsely annotated text therefore *tends to* score higher, saying nothing about its style. Do not state that as a law: for `in`, `ir`, `er`, `sî` or `man` it is simply wrong.

   Where the effect was measured, it held: for the corpus-wide hapax tool's "pro 1000" column (whose numerator is also depressed by missing annotation, since an unannotated rare form is invisible as a rarity), Spearman r(coverage, rate) = **-0.17** over the 345 texts with at least 1000 tokens, and the median rate in the lowest coverage quartile is about twice that of the highest. Text length is not the driver: it correlates with coverage (+0.31) but not with the rate (+0.01), and the negative relation survives within each length tercile (-0.24 and -0.29 for the middle and long thirds; it vanishes for the short third). So the denominator effect wins over the numerator effect, moderately and not uniformly.

   None of this is a defect of the formulas, which correctly answer "per thousand *indexed* tokens". It is the first thing to state when the numbers get quoted, and the reason the UI labels say "annotierte Tokens" since #309. **The same bias applies to keyness (§H.1)**, whose `c` and `d` are the same token counts; the sign there is harder to reason about because both corpus and text side are affected.
1. **`diversity` is a type-token ratio and therefore length-dependent.** TTR falls systematically as texts get longer, for mathematical reasons and not stylistic ones. Sorting the column across texts of very different length ranks by length as much as by vocabulary richness. Comparisons are only safe between texts of comparable size, or after a length-normalized measure replaces it.
2. **Most of these rates do not divide like over like**, and they fail to in three distinct ways:

   | Formula | Numerator counts | Denominator counts | Symmetric? |
   |---|---|---|---|
   | the three per-thousand rates | positions, i.e. **every** `@lemmaRef` | token slots (`wordCount`), i.e. the **first** ID only | no |
   | `avgLemmaFreq` | positions, every ID | **types** (`uniqueLemmata`) | no, and differently |
   | `diversity` | **types** | token slots | no, and differently again |
   | `hapaxRate` | types | types | **yes** |
   | `ratio` (verse position) | positions | positions, same list | **yes** |

   The per-thousand rates carry the same latent asymmetry H.4 records for rhyme pressure. With zero multi-reference tokens today (H.2a) both sides agree exactly; they diverge the moment that changes. `hapaxRate` and the verse-position `ratio` are unaffected in principle, not just today.

3. **The verse-position search is the symmetric counterpart to H.4 and worth knowing about.** It answers the same shape of question ("how much of this lemma's usage sits at a verse boundary?") but reads **both** sides from `text.lemmata`, deliberately and with a comment saying why (`verse-position-search.js:61-69`, the #170 review finding). Rhyme pressure in H.4 reads its numerator from `text.words[]`. After an ingest that introduces multi-reference tokens, the two views will report different percentages for the same lemma, and this is the reason: the verse-position figure is the correct one.

`hapaxRate` is a within-text rate over types and is unrelated to the corpus-wide hapax tool in H.2. The two answer different questions and their numbers must never be compared.

### H.6 Deliberately not here

The remaining tools carry no derived figure. Checked, not assumed: percentages that only size a progress bar do not count as output.

- **Plain counts over `text.lemmata`:** text comparison and co-occurrence ranking. They stay documented in prose in `docs/FEATURES.md`.
- **Already under contract elsewhere:** multi-lemma search (document, proximity and same-verse) is §C.2. Its data path over `lineStarts[]`/`lineEnds[]`, like that of the verse-position search, follows the definition in H.2a.
- **Curated external dataset, trivial counting rule:** the extended character-naming explorer (#59) reads its own prebuilt `data/naming-index.json.gz` and reports attestation counts verbatim from it. What needs documenting there is provenance, not arithmetic, and that sits with the attribution in the view itself.

If any of them grows a normalized, weighted or otherwise derived figure, it belongs in H.5.

**Open dependency:** #255 asks whether parallel witnesses should count as independent texts in these evaluations. All four rules above currently count a witness like any other text. Whatever #255 decides changes H.1 (`corpusWordTotal`, `corpusMatches`), H.2 (`counts`), H.4 (`verseCount`) and every base in H.5, and this section is where it has to be written down.
