# Data Model

This document describes the data sources, schemas, and transformation pipeline for the MHDBDB TEI Repository.

## Overview

The MHDBDB data architecture follows a three-stage flow:

```
[Source XML Files]
   ↓ Python Build Scripts
[Pre-Built JSON Indexes]
   ↓ Browser Fetch + Decompress
[Runtime Data Structures]
```

**Key Principle:** Pre-compute expensive operations (XML parsing, cross-reference resolution) at build time rather than runtime, reducing browser load from ~50 MB XML to ~3 MB compressed JSON (19× reduction).

## Source Data

### TEI Corpus Files

**Location:** `tei/` directory
**Format:** TEI P5 XML (UTF-8, namespace: `http://www.tei-c.org/ns/1.0`)

Each TEI file contains:
- TEI Header with bibliographic metadata
- Text body with word-level annotations
- Word elements (`<w>`) with `@lemmaRef`, `@ana`, and `@corresp` attributes

**Cross-reference pattern:**
```xml
<w lemmaRef="#lemma_879">brott</w>
```

### Authority Files

**Location:** `authority-files/` directory
**Format:** TEI P5 XML with custom MHDBDB schema

Eight authority files – seven inhaltstragende controlled vocabularies (in the corpus index) plus one projekt-interner Mitwirkenden-Register:

- `persons.xml` - Authors and historical persons
- `works.xml` - Work and manuscript metadata
- `lexicon.xml` - Dictionary with tens of thousands of lemmata
- `concepts.xml` - Semantic concept taxonomy
- `genres.xml` - Literary genre classification
- `names.xml` - Proper names with semantic relations
- `variants.xml` - Orthographic variants extracted from corpus
- `contributors.xml` - MHDBDB team register (founders, coordination, editors); **not** part of the corpus index, but a project-internal authority source for the editor attribution in the TEI headers (see `docs/TEI-MODEL-AUTH-FILES.md §3.8` and `docs/TEI-MODEL.md §2.1bis`)

**Cross-reference patterns:**
- Person ↔ Work via `xml:id` and `@ref`
- Lemma → Concept via `<ptr target="concepts.xml#...">`
- Work → Genre via `<ptr target="genres.xml#..."/>`
- Orthographic variant → Lemma via `@corresp="lexicon.xml#..."`
- Corpus header → contributors via `<persName ref="contributors.xml#contrib_NNN">` and `<orgName ref="contributors.xml#mhdbdb-team">`

### Authority File XML Schemas

All files use namespace `xmlns="http://www.tei-c.org/ns/1.0"`.

#### lexicon.xml (~33 MB, 43,879 entries)

```xml
<TEI><text><body><div type="lexicon">
  <entry xml:id="lemma_{n}">
    <form type="lemma"><orth>{lemma text}</orth></form>
    <gramGrp>
      <pos>{POS tag}</pos>+              <!-- NUM, NOM, VRB, ADJ, ADV, PRP, NAM, ... -->
    </gramGrp>
    <etym type="morphological">?          <!-- optional: morphological decomposition -->
      <seg type="component" corresp="lexicon.xml#lemma_{n}">{text}</seg>+
    </etym>
    <sense xml:id="lemma_{n}_sense_{m}" ana="#type_{id} ...">+
      <ptr target="concepts.xml#concept_{id}"/>*
    </sense>
  </entry>+
</div></body></text></TEI>
```

Notes: Multiple `<pos>` per entry possible. Multiple `<sense>` per entry (verb entries often have 2+). `@ana` contains space-separated semantic type references.

#### persons.xml (~74 KB)

```xml
<TEI><text><body><listPerson>
  <person xml:id="person_{n}">
    <persName type="preferred">{canonical name}</persName>
    <persName type="alternative" xml:lang="{de|en}">?{alt name}</persName>*
    <idno type="GND">?{gnd-id}</idno>
    <idno type="wikidata">?{Q-id}</idno>
    <!-- No works list: person→work derived from works.xml <author @ref> at build time -->
  </person>+
</listPerson></body></text></TEI>
```

Notes: IDs are numeric (`person_N`) except `person_anonym`. GND and Wikidata are optional.

#### works.xml (~1.4 MB)

```xml
<TEI><text><body><listBibl>
  <bibl xml:id="work_{n}">
    <title xml:lang="de">{title}</title>
    <title xml:lang="de" type="alternate">?{alt title}</title>*
    <idno type="sigle">{sigle}</idno>+      <!-- one or more sigles per work -->
    <idno type="GND">?{gnd-url-or-id}</idno>
    <idno type="wikidata">?{wikidata-url-or-id}</idno>
    <idno type="handschriftencensus">?{url}</idno>
    <ptr target="genres.xml#genre_{hash}"/>*  <!-- genre label resolved from genres.xml -->
    <author ref="persons.xml#person_{id}">{name}</author>
    <relatedItem>
      <biblStruct type="{journalArticle|bookSection|book}" xml:id="{sigle}_{sigle}"
                  corresp="{zotero-url}" key="{sigle}">*
        <analytic>?                           <!-- present for articles/chapters -->
          <title level="a">{article title}</title>
          <author><name>{name}</name></author>
        </analytic>
        <monogr>                              <!-- always present -->
          <title level="m">{book/journal title}</title>
        <idno type="callNumber">?{sigle}</idno>
        <editor>?<forename>{first}</forename><surname>{last}</surname></editor>
        <imprint>
          <pubPlace>?{place}</pubPlace>
          <publisher>?{publisher}</publisher>
          <date>?{year}</date>
          <biblScope unit="page">?{pages}</biblScope>
        </imprint>
      </monogr>
        <series>?<title level="s">{series title}</title></series>
      </biblStruct>
    </relatedItem>
    <bibl type="digitalIntermediary" corresp="{url}">?  <!-- provenance (Issue #36-40) -->
      <title>{provider name}</title>
      <respStmt><name>{person}</name><resp>{role}</resp></respStmt>
      <ref target="{source url}"/>
      <note type="provenance">{description}</note>
    </bibl>
  </bibl>+
</listBibl></body></text></TEI>
```

Notes: Multiple sigles per work (editions). GND/Wikidata may be full URLs or bare IDs – build script extracts ID portion. Genre `<ref>` elements come in de/en pairs, plus optional parent hierarchy refs.

#### concepts.xml, genres.xml, names.xml (shared pattern)

```xml
<TEI><teiHeader>...<encodingDesc><classDecl>
  <taxonomy xml:id="mhdbdb-{concepts|genres|names}">
    <category xml:id="{type}_{id}">
      <catDesc>
        <term xml:lang="de">{German term}</term>
        <term xml:lang="en">{English term}</term>
        <term type="alternative" xml:lang="{de|en}">?{synonym}</term>*
        <ptr type="broader" target="#{type}_{parent_id}"/>*
      </catDesc>
    </category>+
  </taxonomy>
</classDecl></encodingDesc></teiHeader></TEI>
```

| File | ID format | Extra `<ptr>` types |
|------|-----------|-------------------|
| concepts.xml | `concept_{numeric}` | – |
| genres.xml | `genre_{hex}` | – (but many broader pointers, polyhierarchical) |
| names.xml | `name_{numeric}` | `exactMatch`, `closeMatch` → `concepts.xml#...` |

#### variants.xml (~16 MB, 256,760 variant forms)

```xml
<TEI><text><body><div type="orthographicVariants">
  <entry corresp="lexicon.xml#lemma_{n}">
    <form xml:id="type_{m}">{variant text}</form>+
  </entry>+
</div></body></text></TEI>
```

Notes: Flat list of variants grouped by lemma cross-reference. Forms preserve MHG diacritics. One entry per lexicon lemma; multiple forms per entry.

## Pre-Built Index Architecture

The project uses pre-built JSON indexes to avoid runtime XML parsing.

### Authority Index

**File:** `data/authority-index.json.gz`
**Size:** ~3 MB compressed
**Version:** current state in [TEI-MODEL.md §11](TEI-MODEL.md#11-versioning). Source in the code: `AUTHORITY_INDEX_VERSION` in `assets/js/lib/corpus-loader.js` and `'version'` in `scripts/build-authority-index.py`.

**Schema (illustrative; for the concrete version see the table in TEI-MODEL.md §11):**
```javascript
{
  version: "1.x.x",

  persons: [{
    id: "person_445",
    preferredName: "Meister Eckhart",
    gnd: "118528823",
    wikidata: "Q76548",
    works: "work_001,work_002",   // comma-separated string; normalized to an array only in the static JSON API (see API section)
    normalized: "meister eckhart",
    // optional, only where persons.xml carries persName[@type="alternative"]
    // (80 of 211 persons). Index-parallel: altNormalized[i] belongs to altNames[i].
    altNames: ["Charles IV"],           // e.g. person_1768 "Karl IV."
    altNormalized: ["charles iv"]
  }],

  works: [{
    id: "work_001",
    title: "Von der Abgeschiedenheit",
    titles: [{text, lang, type, ana}],  // objects, not strings: 1,147 across all works,
                                        // 510 of them carry @ana (as of 2026-08-03)
    sigle: "ABG",
    sigles: ["ABG"],
    author: "Meister Eckhart",
    authorRef: "persons.xml#person_445",  // with file prefix throughout, all 584 works.
                                          // The corpus index writes the same reference
                                          // as "#person_445", see the texts record below
    gnd: "work GND",              // Added v1.1.0
    wikidata: "work Wikidata",    // Added v1.1.0
    genres: ["genre_123"],
    biblStructs: [{key, corresp, textContent}],
    handschriftencensus: "12345",
    normalized: "..."
  }],

  lemmata: [{
    id: "lemma_879",
    lemma: "brôt",
    pos: "N",             // first <pos> value (backwards compatible)
    posAll: ["N"],        // all <pos> values; >1 entry for Multi-POS lemmata, e.g. salve = NOM+VRB (v1.6.0, #161)
    senseCount: 3,
    etymology: [{text: "brot", lemmaRef: "lemma_7779"}],
    senses: [{
      id: "lemma_879_sense_1",
      conceptIds: ["concept_1234"],
      // the three curated fields below exist only where lexicon.xml carries them
      // (#248, authority index 1.7.0). As of 2026-08-03 that is a single sense,
      // lemma_37818 "Abba": one <def> and one <note type="comment">, each with
      // its @resp. Curation is ongoing, so expect this count to grow.
      definition: "...", definitionResp: "contributors.xml#contrib_003",
      comment: "...",    commentResp: "contributors.xml#contrib_003"
    }],
    // likewise curated, likewise a single lemma as of 2026-08-03: the borrowing
    // chain from <etym type="borrowing">
    origin: {languages: [{name, code}], attribution: "...", resp: "..."},
    normalized: "brot"
  }],

  concepts: [{
    id: "concept_1234",
    termDE: "Nahrung",
    termEN: "Food",
    normalized: "...",                 // no broader/narrower fields — concept hierarchy is not stored in the index
    altDE: ["Speise", "Essen"],        // optional, only if <term type="alternative" xml:lang="de"> exists
    altEN: ["Sustenance"],              // optional, only if <term type="alternative" xml:lang="en"> exists
    altNormalized: ["speise", "essen"]  // optional, only if altDE exists (normalized via normalizeMHG)
  }],

  genres: [{
    id: "genre_123",
    termDE: "Mystische Prosa",
    termEN: "Mystical Prose",
    normalized: "...",
    parents: ["genre_456"],             // direct parents as ids, omitted on the two roots (v1.9.0, #361)
    altDE: ["Prosa der Mystik"],        // optional, only if <term type="alternative" xml:lang="de"> exists (v1.5.0)
    altEN: ["Mystic prose"],            // optional, analog (v1.5.0)
    altNormalized: ["prosa der mystik"] // optional, only if altDE exists (v1.5.0)
  }],

  names: [{
    id: "name_456",
    termDE: "Aristoteles",
    termEN: "Aristotle",
    conceptIds: ["concept_7890"],
    normalized: "..."
  }],

  variants: {
    "brot": "lemma_879",   // normalized form → lemma ID
    "brott": "lemma_879",
    // ... 234,243 mappings (2026-07-28)
  },

  maps: {
    conceptToLemmas: {
      "concept_1234": ["lemma_879", ...]
    },
    genreToWorks: {
      "genre_123": ["work_001", ...]
    }
    // genreHierarchy was removed in v1.9.0 (#361), see genres[].parents above
  }
}
```

**Key features:**
- Normalized searchable text for all entities (MHG character conversion: â→a, ô→o, ü→ue)
- Performance maps pre-computed (conceptToLemmas, genreToWorks)
- Variants dictionary enables O(1) orthographic variant lookup
- Separate GND/Wikidata identifiers for works vs authors (added during the authority migration; current authority-index version per TEI-MODEL.md §11)

### Corpus Index

**File:** `data/corpus-index.json.gz`
**Size:** ~40 MB compressed (it was ~34 MB before `lineStarts`/`lineEnds` were added)
**Version:** current state in [TEI-MODEL.md §11](TEI-MODEL.md#11-versioning). Source in the code: `INDEX_VERSION` in `assets/js/lib/corpus-loader.js` and `'version'` in `scripts/build-corpus-index.py` (which also carries the version history comment). For MAJOR/MINOR/PATCH semantics see below.

**Schema (illustrative; for the concrete version see the table in TEI-MODEL.md §11):**
```javascript
{
  version: "4.x.x",
  totalTexts: 667,
  totalLemmata: 42630,

  texts: [{
    id: "ABG",                       // sigle (primary identifier, used in URLs)
    filename: "ABG.tei.xml",
    title: "Von der Abgeschiedenheit",
    author: "Meister Eckhart",
    authorRef: "#person_445",        // verbatim from the TEI @ref: 666 of 667 in this shape,
                                     // WZB alone writes "persons.xml#person_anonym" (#308)
    workRef: "works.xml#work_89",    // verbatim from msIdentifier/@corresp, with file prefix
    genre: "",                       // empty in all 667 texts, see the XPath table below
    wordCount: 2955,                 // lemmatized tokens only (<w> with @lemmaRef), NOT all <w>
    words: ["lemma_879", ...],       // lemma IDs in document order; index = position
    lemmata: {                       // reverse map per text: lemma → positions
      "lemma_879": [0, 12, 47],
      "lemma_881": [3, 9]
    },
    lineStarts: [0, 8, 15, ...],     // word-index where each <l> starts (#47.3)
    lineEnds:   [7, 14, 22, ...]     // word-index where each <l> ends (inclusive)
  }],

  lemmaIndex: {                      // global reverse index: lemma → text sigles
    "lemma_879": ["ABG", "NBB", "PZ"],
    "lemma_881": ["NBB"]
  }
}
```

**Key features:**
- Document-level word indexing (removed paragraph-based indexing in 4.0.0)
- `words[i]` = lemma ID at position `i` (sequential, 0-indexed)
- Only words with `@lemmaRef` are indexed
- `lemmata` is the per-text reverse index (lemma → positions), enables O(1) lookup of "where does lemma X appear in text Y"
- `lemmaIndex` is the global reverse index (lemma → list of text sigles), enables fast "which texts contain lemma X" queries
- `lineStarts[]` / `lineEnds[]` (since 4.1.0): per text, the word indices of the `<l>` boundaries. Same length as the number of `<l>` carrying at least one indexed word. Empty arrays for prose texts without `<l>` (67/667 ≈ 10 % of the corpus, as of 2026-07-31; it was 64 until #143 turned three texts into prose). Enables „lemma at verse start / verse end" lookups in O(L) instead of O(W).
  **How the verse count is measured (as of 2026-08-02):** 1,356,748 boundaries across 600 texts, counted as the sum of the `lineStarts` lengths in the built index. The corpus itself carries 1,358,973 `<l>`; the difference is verses without a single lemmatized word, which produce no boundary. Both numbers are right, they measure different things.
- 100% word coverage from TEI `<body>` elements (words outside `<l>`, such as in `<head>`, `<note>`, `<fw>`, count in `words[]` but match no verse boundary)
- Supports accurate proximity search plus the verse position filter

**Why v4.0.0?** Removed paragraph-based indexing due to position misalignment between Python extraction and JavaScript parsing. Document-level indexing is simpler and more accurate.

**Why v4.1.0?** Per-text `lineStarts[]` / `lineEnds[]` for the #47.3 lemma search by verse position. Bumped as `schema-feature-add` (MINOR), not just `data-add` (PATCH).

**Everything beyond that is changelog and does not belong here.** The reasoning for each individual bump from v4.1.5 on hangs as a comment on the `'version'` constant in `scripts/build-corpus-index.py`, the current version is in [TEI-MODEL.md §11](TEI-MODEL.md#11-versioning), the older ones in the git history of this file. A schema document retelling every PATCH goes stale in a place nobody maintains (#318).

**Field name note:** the primary identifier is `id` (sigle), not `textId`. Older docs and some code paths may use `textId` – the canonical field in the index JSON is `id`.

**Version sync (critical):** the index version string has to be kept in sync with `INDEX_VERSION` in `assets/js/lib/corpus-loader.js` and the `'version'` constant in `scripts/build-corpus-index.py`. Otherwise the cache invalidation logic does not fire (see `docs/CONTRACTS.md` §IndexedDB). Guaranteed in CI via `.github/workflows/data-integrity.yml`; locally run `python scripts/audit/check-index-versions.py` before committing.

### Naming Index (#59)

**File:** `data/naming-index.json.gz` (~110 KB gz, v1.0.0)
**Build:** `python scripts/ingest/naming/01-fetch-and-build-index.py` (fetches from GitHub `lindabeutel/Naming-analysis@master`; `--source-dir` for offline use)
**Consumer:** only `playground/js/ui/tei/naming-explorer.js` (extended character naming, beta)

An external curated dataset (not corpus-derived): proper names, antonomasias and epithets per character for ENE/IW/ROL/TRO, from Linda Beutel-Thurow's doctoral project (DOI 10.5281/zenodo.21916576, CC BY-NC-SA 4.0, v0.2.1-beta as of 2026-08-14). Around 10,500 records; the exact number moves, because a weekly cron rebuilds the index against Linda's repository (the PR series `chore/naming-index-update`). Current state: `python scripts/audit/check-naming-index.py`.

**Citation and typology are guarded, not documented.** The version and DOI live in `QUELL_VERSION`/`QUELL_DOI` of the build script, and `pruefe_zitation` compares both against the `CITATION.cff` of the source state being built: a weekly rebuild against a newer release fails rather than shipping new data under the old citation. The module renders its visible attribution from `source` in the index, so there is no second copy to keep in step. Two further guards run on every build: `pruefe_instanztypen` compares Linda's `data/instance_types.json` against `BEKANNTE_INSTANZTYPEN` and is deliberately **asymmetric** (a type we do not know is fatal, a type of ours missing from the source is a hint, because the freshness gate replays historical source states that predate the file), and `pruefe_frontend_paritaet` reads `MARKER_KLASSEN` out of `naming-explorer.js` and demands a class for every known marker.

**Work-specific alias additions:** `scripts/ingest/naming/alias-overrides.json` (#59). A lemma counts as a proper name when it hits the character's name or one of its aliases; the aliases come from Linda's `lemma_normalization.json`, which normalizes across all works. An alias that holds in one work only would be wrong there, so it lives here instead and Linda's repository stays faithful to its source. Every entry names its reason, its date, where it was approved, and its `category`, which is mandatory and takes one of two values: `deck` for a cover name (its own fourth category, between proper name and antonomasia) or `eig` for a proper name that is merely missing from `lemma_normalization.json`. The difference is a philological statement, not a default a new entry may inherit in silence. The build merges the entry into that character's alias set in that work alone and fails hard on an unknown work name, character name or category, since a typo would otherwise sit in the file with no effect at all. The weekly rebuild carries the file along. Currently one entry: „Alexander" as the cover name of Paris in the Trojanerkrieg (approved by Linda, #59 comments of 2026-07-28 and 2026-08-10; affects exactly one record, V. 20665, and leaves the separate character Alexander of V. 13808 untouched).

**Deterministic build:** `generatedAt` is the committer date of the source commit (not the build time), gzip without mtime, so the same source state produces byte-identical output. The **auto-update workflow** `.github/workflows/naming-index-update.yml` builds on that: a weekly cron (Mondays 05:17 UTC), a rebuild, and on a `git diff` a PR with the build log and a source compare link. Merge only after visual inspection (a gate against format drift in the externally curated source JSONs). In CI the build runs with `--require-commit` (#152): if the source commit cannot be resolved, the build fails hard instead of silently letting `generatedAt` fall back to build time (non-deterministic plus loss of provenance).

**CI gates (#152, in `data-integrity.yml`):** (1) a consistency check on every data PR: `source.commit` present and every `works[].sigle` exists as `tei/<SIG>.tei.xml` (a sigle rename would otherwise silently break the reader link in the playground). (2) rebuild-and-compare against the `source.commit` pinned in the index, only if naming paths changed (no external network dependency on every data PR).

```json
{
  "version": "1.0.0",
  "generatedAt": "...",
  "source": { "repo": "...", "ref": "master", "commit": "<sha>", "doi": "...", "citation": "...", "license": "..." },
  "works": [
    {
      "sigle": "IW",
      "bookName": "Iwein",
      "figures": {
        "Iwein": [
          { "v": "803", "ph": "herre Îwein", "who": "erz|fig|self", "by": "Keie?", "eig": ["Iwein"], "deck": ["..."], "ant": ["hêrre"], "epi": ["..."] }
        ]
      }
    }
  ]
}
```

Category derivation at build time: `Epitheta 1-5` becomes `epi`; `Bezeichnung 1-4` becomes `deck` on a `deck` override (checked first, being the work-specific and individually reasoned statement), `eig` if the lemma matches the character name (case-insensitively exact, or an alias from `lemma_normalization.json`, replicating Linda's `match_name_to_lemma`), otherwise `ant`. `who`: `erz` is the narrator, `fig` is character speech (`by` is the naming character), `self` is self-naming. Verse numbers (`v`) follow Linda's edition base, **not** the MHDBDB TEI counting, which is why there are no reader links.

**No version sync channel:** the index is loaded lazily through fetch plus pako, without an IndexedDB cache and without an entry in `corpus-loader.js`, so a rebuild is live with the commit (the #94 class of bugs is excluded by construction). Reason to update: new or updated data in the source repository, then a rebuild and a commit of the `.gz`.

### Horses Index (#193)

**File:** `data/horses-index.json.gz` (11 KB gz, 77 KB raw, v1.0.0)
**Build:** `python scripts/ingest/horses/03-build-index.py` (fetches the source once into the script directory, which is gitignored; `--dry-run` reports without writing)
**Consumer:** a curated playground query (in progress, together with #194)

A second external curated dataset, and again not corpus-derived: Luise Borek's `arthurianHorses.xml`, an exemplary semantic encoding of the horses in five Arthurian works (hdl:tudatalib/3695, **CC0 1.0**, published 2023-01-18). Note that the file's own header still reads "Veröffentlichung unter CC-BY-SA wird angestrebt" and carries the date January 2017: that is the draft state, the repository licence governs.

13 horses (10 named, 3 unnamed), 346 attestations across 336 verses in WH, PZ, ER, IW and TR, with Borek's inline annotations carried through: `event/@type` (care, intro, loss, combat, trans, communication, recognition, gift), `trait/@type` (quality, marking, color), `object/@type` (gear, armor, deco, weapon), `person/@role` (owner, claimant, rider), and the designation the horse appears under in the verse (`usg`, for instance `ors`).

Three of Borek's markings sit where a naive walk misses them, and each occurs once: an `event` **inside** the `<l>` rather than around it (Pz. 549,7 carries its `care` that way), an `objectName` without an enclosing `object` (Wh. 77,14, the sword Schoyuse), and a `horseGrp` for a group of animals rather than this one horse (Pz. 474,3 compares `ein ors` with `den orsn`). All three would have vanished silently from any filter, which is why the build collects ancestors and descendants of a verse.

**Both citations are stored, and that is the point.** Borek's reference and our resolved target are two different statements, and for nine of the 346 attestations they diverge. Our Parzival follows Leitzmann (ATB 12, 7th ed. 1961), our Erec Leitzmann/Wolff (ATB 39, 3rd ed. 1963); **Borek names no edition at all**, her `sourceDesc` carries only the work's GND. The difference is therefore documentable but not resolvable, so a silent conversion to our counting would not be verifiable. What is verifiable is the wording, and that is what the build measures.

| `match` | meaning | count |
|---|---|---|
| `exact` | Borek's number hits our verse | 337 |
| `shifted` | displaced within a four-verse radius, wording proves identity (Pz. 339,24 to 339,28 sit two verses lower here) | 5 |
| `distant` | outside the radius but unambiguous (Pz. 604,18 is our 603,18; Er. 4118 is 4718, a transposed digit in the source) | 3 |
| `unresolved` | no candidate holding both threshold and margin: `target` is `null` and the view must not offer a jump | 0 |

Counted **per attestation**. The report `02-map-citations.py` counts the same measurement **per verse** and therefore says 328 exact, not 338: ten verses are cited by two horses each. Two units, one measurement.

Comparison runs on the MHG-normalized letter string without word breaks (`difflib`), threshold 0.75, and a `distant` hit is only adopted with at least 0.15 margin over the runner-up. A word-set comparison was tried first and failed on orthography and word division (`ans grâles` against `an sgrâles`), reporting six verses as doubtful that were not. The rationale sits in `scripts/ingest/horses/mapping.py`, shared by the build and the report `02-map-citations.py` so the two cannot drift apart.

`target` is the **verse core** (`PZ_33926`), not the first word id: ongoing corpus corrections can change which `<w>` opens a verse, not where the verse sits. The frontend builds the anchor.

This is the point where #59 decided differently. The naming index builds **no** reader deep links because its verse counting diverges, and that remains right there. Here links are defensible, but only because every single citation was checked against the wording; a `target` without that check would silently hit the wrong verse.

**Deterministic build:** no build timestamp, gzip without mtime, and `source.sha256` pins the source state, so the same source plus the same corpus yields a byte-identical index. Rebuild after corpus changes to the five works: the resolution is measured against `tei/`.

```json
{
  "version": "1.0.0",
  "source": { "title": "...", "author": "Luise Borek", "handle": "hdl:tudatalib/3695",
              "licence": "CC0 1.0", "published": "2023-01-18", "sha256": "<hex>" },
  "horses": [
    { "id": "Gringuljete", "name": "Gringuljete", "named": true,
      "variants": ["Gringuljet", "Kringulet", "Gringalet"],
      "works": ["PZ", "ER"], "attestations": 120 }
  ],
  "attestations": [
    { "horse": "Gringuljete", "work": "PZ", "n": "339,24", "citation": "Pz. 339,24",
      "text": "dô hiez er gürten balde", "target": "PZ_33926", "match": "shifted", "score": 0.83,
      "events": [{ "type": "intro" }, { "type": "care" }],
      "persons": [{ "text": "er", "role": "owner", "ref": ["Gâwân"] }],
      "objects": [{ "type": "gear", "text": "gürten" }] }
  ]
}
```

**No version sync channel**, for the same reason as the naming index: lazy fetch, no IndexedDB cache, no entry in `corpus-loader.js`.

## Data Processing Pipeline

### Build Scripts

**Location:** `scripts/` directory
**Language:** Python 3.13+ with lxml

Three core build scripts:

1. **`build-authority-index.py`** - Extract authority data from 7 inhaltstragende XML files (the 8th, `contributors.xml`, is deliberately not indexed – see below)
   - Parse XML with lxml
   - Extract structured data for each entity type
   - Build performance maps (conceptToLemmas, genreToWorks)
   - Normalize searchable text
   - Variants dictionary built from `authority-files/variants.xml` (see *Variants regeneration* below)
   - Output: `data/authority-index.json.gz`

2. **`build-corpus-index.py`** - Extract word positions from TEI files
   - Scan `tei/` directory for all `.tei.xml` files
   - Extract metadata and words (logical selection `//tei:body//tei:w[@lemmaRef]`; implemented as a single-pass `etree.iterwalk` over `<body>`, see CONTRACTS §B)
   - Build words array with sequential positions
   - Output: `data/corpus-index.json.gz`

3. **`validate-indices.py`** - Integrity checks
   - Validate unique IDs
   - Check cross-references
   - Verify data quality

**Variants regeneration:** `authority-files/variants.xml` is consumed by `build-authority-index.py` but is itself **derived from the corpus** (one `<form xml:id="type_N">` per orthographic variant, grouped under the lemma it attests). Regenerate it with `python scripts/sync/extract-variants.py --apply` (reads current `@lemmaRef` + `@corresp`; xml:id uniqueness by majority vote) whenever the corpus gains new orthographic forms, then rebuild the authority index and bump its version. *Historical note:* the original extractor lived only on the archived `initial-data-wrangling` branch and read the pre-#32 `@wordRef`, so the file silently drifted by 64,287 forms until the maintained generator was added and `variants.xml` regenerated on 2026-05-29 (192,472 → 256,759 forms; #44/#115).

### Static JSON API (`api/`)

**Script:** `scripts/build-api.py` (alias: `npm run build:api`, not part of the `npm run build` aggregate)

Third derived layer beside the two indexes. Reads **only** the two pre-built indexes (`data/authority-index.json.gz` + `data/corpus-index.json.gz`), never the XML sources, and emits a static JSON API into `api/` (2,742 files, ~14 MB), served as plain files by GitHub Pages:

- `api/index.json` – root manifest (collection counts, source index versions)
- `api/lemmata/index.json` – full lemma records as one bundle (43,879 records, no individual files)
- `api/<coll>/{id}.json` + `api/<coll>/index.json` (summary list) for persons, works, concepts, genres, names, texts (texts stripped of the heavy `words`/`lemmata`/`lineStarts`/`lineEnds` arrays)
- every emitted file carries `"license": "CC BY-NC-SA 4.0"`; `persons.works` is normalized from comma-string to array

Build properties: deterministic on the #125 principle (no timestamps, compact JSON – same index state produces byte-identical output), pre-flight refuses a dirty `data/` (#100 pattern), wipes all `api/**/*.json` before writing (orphan protection; non-JSON files like the documentation page `api/index.html` are spared), ID-safety asserts before the wipe. CI-gated: the step "Freshness API (#45)" in `data-integrity.yml` rebuilds and compares. URL schema and field contracts: [CONTRACTS.md §G](CONTRACTS.md#g-static-json-api-contract-45).

### Build Script XPath Reference

| Script | Source File | XPath | Extracts |
|--------|-----------|-------|----------|
| `build-authority-index.py` | lexicon.xml | `//tei:entry` | All lemma entries |
| | | `.//tei:form[@type="lemma"]/tei:orth` | Lemma text |
| | | `.//tei:pos` | Part(s) of speech |
| | | `.//tei:etym[@type="morphological"]//tei:seg[@type="component"]` | Etymology components + `@corresp` |
| | | `.//tei:etym[@type="borrowing"]`, inside it `./tei:lang` and `./tei:note[@type="attribution"]` | `lemma.origin`: source languages (`@norm` → `code`), optional attribution including `@resp`. Curated, see below |
| | | `.//tei:sense` | Senses (with `@xml:id`; concept pointers per sense) |
| | | `.//tei:ptr[contains(@target,"concepts.xml#")]` *(relative to the `<sense>`)* | Concept pointers per sense |
| | | `./tei:def` *(relative to the `<sense>`)* | `sense.definition` + `sense.definitionResp` from `@resp`. Curated, see below |
| | | `./tei:note[@type="comment"]` *(relative to the `<sense>`)* | `sense.comment` + `sense.commentResp` from `@resp`. Curated, see below |
| | persons.xml | `//tei:person` | Person records |
| | | `.//tei:persName[@type="preferred"]` | Canonical name |
| | | `./tei:persName[@type="alternative"]` | `person.altNames` + `person.altNormalized` (index-parallel). Deduplicated by exact text: wherever the German and English form coincide, the same string stands twice. `@xml:lang` is not indexed, and the parser does not key on it |
| | | `.//tei:idno[@type="GND"]` | GND identifier |
| | | `.//tei:idno[@type="wikidata"]` | Wikidata ID |
| | | (derived from works.xml `<author @ref>`) | Work IDs (built at index time) |
| | works.xml | `.//tei:bibl` (fallback `.//work` for non-TEI sources) | Work records |
| | | `./tei:title` | All titles (with `@xml:lang`, `@type`, `@ana`). All 1,147 title objects carry an `ana` key, 510 of them non-null |
| | | `.//tei:idno[@type="sigle"]` | Sigles (may be multiple) |
| | | `.//tei:idno[@type="GND"]` | Work GND (extract ID from URL: strip `https://d-nb.info/gnd/`) |
| | | `.//tei:idno[@type="wikidata"]` | Work Wikidata (extract Q-ID from URL: strip `https://www.wikidata.org/entity/`) |
| | | `.//tei:idno[@type="handschriftencensus"]` | Handschriftencensus URL |
| | | `./tei:ptr[contains(@target,"genres.xml#")]` | Genre pointers (label from genres.xml lookup) |
| | | `./tei:author` (direct child only, see the note below the table) | Author name + `@ref` → person ID |
| | | `.//tei:biblStruct` | `work.biblStructs`: `key` (`@key`), `corresp` (`@corresp`), `textContent` (flattened `itertext()`). All 681 elements carry an `@type` and an `@xml:id`; **neither is read** |
| | concepts.xml | `//tei:category` (filter ID starts with `concept_`) | Concept entries |
| | genres.xml | `//tei:category` (filter ID starts with `genre_`) | Genre entries |
| | names.xml | `//tei:category` (filter ID starts with `name_`) | Name entries |
| | (all three) | `.//tei:catDesc//tei:term` (filter `@xml:lang`) | DE/EN labels. For concepts and genres additionally `@type="alternative"` → `altDE`/`altEN`/`altNormalized` (that is what index versions 1.3.0 and 1.5.0 were for). `names.xml` has no such handling: there the last `de` term overwrites the previous one, dormant today because no name category carries more than one |
| | genres.xml | `./tei:catDesc/tei:ptr[@type="broader"]` *(direct children throughout; the only reader is `build_performance_maps`, not `parse_genres`)* | Genre hierarchy, 3,175 pointers |
| | genres.xml | `tei:catDesc/tei:term` *(direct child, first `de` wins)* in `_build_genre_names()` | `work.genres[].text`, the label shown for a genre pointer. Different axis **and** different selection logic from the `.//tei:catDesc//tei:term` row above |
| | names.xml | `.//tei:ptr[contains(@target,"concepts.xml#")]` | Concept cross-references |
| | variants.xml | `.//tei:entry` (TEI namespace hard-coded) | Variant groups |
| | | `.//tei:form` | Orthographic forms per lemma |
| `sync/extract-variants.py` | tei/*.tei.xml | `tei:w` with `@lemmaRef` + `@corresp`, via `iter()` over the **whole document** | Regenerates `variants.xml` from the corpus. Note the scope: `build-corpus-index.py` restricts itself to `<body>`, this one does not. Identical over the current data (all 9,431,294 `<w>` sit in `<body>`) |
| | variants.xml | `tei:entry` + `./tei:form` | Diff against the previous state before writing |
| `build-corpus-index.py` | tei/*.tei.xml | `//tei:idno[@type="sigle"]/text()` | Sigle (fallback: filename without `.tei.xml`) |
| | | `//tei:titleStmt/tei:title` → `itertext()` + whitespace collapse | Title. **Not** `/text()`: that is the reading #228 removed, six titles carried a line break into `api/texts/*.json` |
| | | `//tei:titleStmt/tei:author` | Author name + `@ref` |
| | | `//tei:msIdentifier` | `@corresp` → work reference |
| | | `//tei:keywords/tei:term[@type="genre"]/text()`, Fallback `//tei:term[@type="genre"]/text()` | `text.genre`. **Never fires: the element occurs 0 times in the corpus, so the field is empty in all 667 texts.** The interface takes the genre via `workRef` from `genres.xml` instead (`search-engine.js`). Kept so an ingest that does supply it is picked up |
| | | `//tei:body//tei:w[@lemmaRef]` *(logical; real code: single-pass `iterwalk`)* | All words with positions (see [CONTRACTS.md](CONTRACTS.md#b-position-counting-contract)) |
| | | `//tei:body//tei:l` *(in the same `iterwalk`)* | `lineStarts`/`lineEnds`, the word index of the first and last indexed `<w>` per verse |

#### Curated lexicon fields (#268, since authority index v1.7.0)

The three productions marked „curated" (`etym[@type="borrowing"]`, `def`, `note[@type="comment"]`) are the only ones in the lexicon carrying editorial prose instead of classification. The build writes the corresponding index fields **only where they actually stand in the XML**: 43,879 lemmata entries with empty keys would inflate index and API for nothing. As of 2026-07-31 exactly one lemma is curated (`lemma_37818` „Abba"), so consumers have to treat the fields as optional, never as a promise per record. Normative: [CONTRACTS.md §G.3](CONTRACTS.md#g3-field-schemas). The `@resp` values land in the index unchanged as `contributors.xml#contrib_N`; the id can only be resolved through the XML file, because `contributors.xml` is deliberately not indexed.

#### Namespace Handling

Build scripts use `get_namespaces()` which handles TEI documents with or without explicit namespace prefix:

1. Read document's `nsmap`
2. If `None` key exists (default namespace), remap to `'tei'` prefix
3. Fallback: set `'tei'` = `'http://www.tei-c.org/ns/1.0'`

Source: `scripts/tei_namespaces.py` (`get_namespaces`, a shared lib since #171 F97; imported by `build-authority-index.py`)

**How far this robustness reaches.** It applies only to XPaths running through the `ns` parameter. Where the build uses `findall()` with a hardcoded `{http://www.tei-c.org/ns/1.0}`, there is no namespace-free branch: `.//tei:entry` in `variants.xml` and `.//tei:bibl` in `works.xml` find nothing in a document without the TEI namespace. Point 3 of the list above does not help there either, because in a namespace-free document it inserts exactly the TEI namespace. Both files are namespaced, so the case does not arise; but the robustness is narrower than the table used to claim (#293).

**Why `./tei:author` and not `.//tei:author`.** The author of a work is a direct child of the `<bibl>`. Since the Zotero sync all 584 works in `works.xml` contain at least one `<biblStruct>`, and nearly all of those carry `<author>` elements of their own: those are the authors of the **edition**, not of the work. For a work without its own `<author>` a descendant search would silently record the edition's author as the work's author. Measured on 2026-07-31: not a single entry is affected, all of them have a direct `<author>` child. The narrow path therefore costs nothing and rules the case out before it arises (#293).

#### Variant Dictionary Deduplication

When building the variants map, **first occurrence wins**: if two lemmata claim the same normalized variant form, only the first is stored. No collision detection or warning. Source: `build-authority-index.py`, `parse_variants()` (line anchors drift, so search for the function by name).

### Data Wrangling Scripts

**Location:** `scripts/sync/` (ongoing sync) and `scripts/audit/` (validation)

Scripts for enriching authority files with external data:

1. **`enhance_works_with_zotero.py`** - Sync Zotero bibliographic data
   - Fetch from Zotero API (group 5043625, collection 7JU362QV)
   - Extract ALL fields: title, edition, volume, issue, series, seriesNumber, authors, editors, place, publisher, date, pages, ISBN, notes
   - Transform titles to German Title Case (capitalize words except articles/prepositions)
   - Update works.xml with complete biblStruct elements
   - Three modes: live API, cache, offline

2. **`sync_tei_headers.py`** - Propagate authority metadata to TEI headers
   - Read authority file changes (works.xml, persons.xml)
   - Update corresponding TEI file headers
   - Maintain intentional redundancy for accessibility

**Title Case Transformation:** Zotero stores titles in sentence case, but German bibliographic style requires Title Case. The script converts automatically:
- Capitalizes first word and words after colons
- Keeps German articles/prepositions lowercase (der, die, von, und, etc.)
- Capitalizes all other words
- Example: "Das stadtratsgedicht heinrichs von rang" → "Das Stadtratsgedicht Heinrichs von Rang"

### Browser Loading Pipeline

**Component:** `assets/js/lib/corpus-loader.js`

**Process:**
1. Check IndexedDB cache (30-day expiration for indices)
2. If expired or missing, fetch compressed index
3. Decompress with Pako (gzip)
4. Parse JSON
5. Store in IndexedDB with expiration timestamp
6. Populate runtime data structures

**Cache strategy:**
- Authority index: 30-day expiration (reference data)
- Corpus index: 30-day expiration (corpus data)
- TEI files: No expiration (user content)

## Data Relationships

### 3-Stage Lemma Resolution

Search resolves user input to lemma IDs through 3 stages with early return:

| Stage | Method | Return | Performance |
|-------|--------|--------|-------------|
| 1 | Exact match on normalized canonical form | 0..N (homographs) | O(n) scan |
| 2 | Variants dictionary lookup (normalized variant mappings, deduplicated from the raw forms; figures with a date in [CONTRACTS §C](CONTRACTS.md#c-3-stage-lemma-resolution-algorithm)) | Exactly 1 | O(1) hash |
| 3 | Bidirectional PREFIX fallback, sorted by length distance (#224) | 0..N (fuzzy) | O(n) scan |

Stages are mutually exclusive, first match wins. **Full pseudocode with worked example:** see [CONTRACTS.md](CONTRACTS.md#c-3-stage-lemma-resolution-algorithm)

**Why 3 stages?** Historical spelling variations in Middle High German are extensive. Variants dictionary captures actual corpus attestations, while fallback handles edge cases.

### Cross-Reference Integrity

All cross-references validated during build:
- Work `authorRef` points to existing person
- Lemma `conceptIds` point to existing concepts
- Word `lemmaRef` points to existing lemma
- Work `genres` point to existing genre IDs

### Performance Maps

Three pre-computed maps accelerate common queries:

**conceptToLemmas:** Find all lemmata for a concept
- Avoids scanning entire lexicon
- Used in concept explorer

**genreToWorks:** Find all works in a genre
- Avoids scanning entire works list
- Used in genre explorer

A third map, `genreHierarchy`, held parent *names* for a genre until v1.9.0. It was
dropped in #361 in favour of `genres[].parents`, see the next section.

## Data Quality

### Known Issues

**Missing Identifiers:**
- Some works lack GND identifiers (historical: not all works have entries)
- Some persons lack Wikidata IDs (newer addition, ongoing enhancement)

**TEI Encoding:**
- Punctuation sometimes encoded as entities (`&lt;`, `&gt;` in `<pc>`)
- This is correct XML encoding, not a bug

**Genre hierarchy: a closure, not a tree.** `genres.xml` stores the relation as
`<ptr type="broader">`, and every category names *all* its ancestors, not just
the nearest ones: 615 categories carry 3,175 edges, all resolvable. This is a
faithful SKOS-style closure, but it cannot be displayed as a hierarchy, because
a shortcut edge (root → leaf) is indistinguishable from a real parent edge.
`build-authority-index.py` therefore computes the transitive reduction at build
time (`_direct_parents()`) and writes the result to `genres[].parents` as ids
(#361). Measured on 2026-08-10: 442 categories keep one direct parent, 139 keep
two, 29 keep three, 3 keep four, and 2 are roots (*Epik, Lyrik und Dramatik*,
*Wissensliteratur und Gebrauchsliteratur*). Tree depth is 9.

The result is a **DAG, not a tree**, and that is the data being right rather than
wrong: *Predigtmärlein* is both a *Märe* and a *Predigt*, *Monatsregimen* belongs
under *Kalender*, *Tagewählerei* and *Text zur Diätetik* at once. Any consumer
that assumes a single parent will silently drop one of the readings. Fully
expanded, the 615 categories occupy 1,167 tree positions.

### Validation

Build scripts perform integrity checks:
- Unique IDs across all entities
- Valid cross-references (no dangling references)
- No empty required fields
- Normalized text matches expected format

### Maintenance

**When to rebuild authority index:**
- Authority XML files modified
- Cross-references added/changed
- New GND/Wikidata identifiers added

**When to rebuild corpus index:**
- TEI files added/removed/modified
- Word annotations changed

**When to regenerate variants:**
- TEI corpus modified (new orthographic forms)
- Usually paired with corpus index rebuild

**Rebuild workflow:**
```bash
python scripts/sync/extract-variants.py --apply   # regenerate variants.xml from the corpus (#44/#115)
python scripts/build-authority-index.py
python scripts/build-corpus-index.py
python scripts/validate-indices.py
python scripts/build-api.py                       # static JSON API from the two indexes (#45)
```

**Cache invalidation:**
- Increment version number in build script
- Browser checks version and refetches if mismatch

---

## Ingest procedure (taking in new texts)

> Normative, internal procedural documentation (#132). It describes the phase pattern developed during the Wenzelsbibel ingest (#34, 2026-04) and reused for ARITHMETIC (#92) in a way that makes it **reconstructible without the scripts** (the rebuild test, CLAUDE.md). Delimitation: `hilfe-daten-beitragen.html` is the user-facing guide for external contributors (#68); `scripts/ingest/<sigle>/README.md` documents the text-specific instantiation including its end state; this section is the pattern itself.

**The scripts are not plug and play.** For every new text the three canonical scripts (`wzb-auto-match.py`, `wzb-pos-assign.py`, `wzb-sense-assign.py`) are copied into `scripts/ingest/<sigle>/` as a template; sigle constants, paths and text-specific heuristics (spelling conventions, language stage) are adapted. See [`scripts/ingest/wzb/README.md`](../scripts/ingest/wzb/README.md).

### Target state

By the end every lexical `<w>` carries four attributes:

```xml
<w xml:id="ALL_20100010_1"
   lemmaRef="lexicon.xml#lemma_722"
   ana="lexicon.xml#lemma_722_sense_1177"
   pos="VRB"
   corresp="variants.xml#type_2239">bitte</w>
```

| Attribute | Format | Phase | Meaning |
|---|---|---|---|
| `@lemmaRef` | `lexicon.xml#lemma_{N}` | 1 | lemma assignment |
| `@pos` | a tag from the 19-tag MHDBDB set (`NOM NAM ADJ ADV DET POS PRO PRP NEG NUM CNJ SCNJ CCNJ IPA VRB VEX VEM INJ DIG`; full reference in [POS-TAGSET.md](POS-TAGSET.md)) | 2 | part of speech (context-dependent for multi-POS lemmata) |
| `@ana` | `lexicon.xml#lemma_{N}_sense_{M}` | 3 | meaning (sense) |
| `@corresp` | `variants.xml#type_{K}` | 3 | orthographic variant form |

*Historical note:* during the WZB ingest the extension attributes `@meaningRef`/`@wordRef` were planned for a while (still visible in the feature doc for #34, in the git history). What holds in the end is the TEI-conformant `@ana`/`@corresp`; the scripts and `tei/WZB.tei.xml` use these exclusively.

### Overview of the phases

```
[source TEI / foreign format]
   ↓ Stage 0: schema conversion (mechanical)
[MHDBDB-conformant TEI, unannotated]
   ↓ structural cleanup + paratext policy (#66)
[only lexical <w> in the pipeline]
   ↓ Phase 1: lemmatization   (1a auto-match → 1b LLM/human disambiguation)
   ↓ Phase 2: POS tagging     (auto-inherit → LLM/human disambiguation)
   ↓ Phase 3: sense resolution (auto-assign → LLM/human disambiguation)
[fully annotated TEI]
   ↓ backward sync (lexicon.xml backfill, MANDATORY, CONTRACTS F.3)
   ↓ registration (works.xml, tei/) + Data-Change-Lifecycle (indexes, below)
[live in search and playground]
```

Every annotation phase follows the same three steps (**assign → resolve → apply**):

1. **Assign:** the script writes every unambiguously decidable case straight into the TEI and emits the ambiguous ones as a pending TSV.
2. **Resolve:** an LLM and/or a human fill the resolution columns in the TSV (`resolved_*`, `confidence`, `reviewer`). Two granularities: **bulk** (one decision per form or lemma, applying to all tokens) and **patch/instance** (a decision per `xml_id`, for minority exceptions and context-dependent cases).
3. **Apply:** the script writes the resolved TSV rows back into the TEI. Apply is **additive**, it never overwrites auto-assign results.

The TSVs are versioned along (audit trail) and split into chunks of about 50 rows for LLM batches (`wzb-split-tsv.py`). LLM decisions carry a `decision_type` taxonomy (`auto-single` / `bulk-llm` / `bulk-human` / `instance-llm` / `instance-human` / `abstain`); `abstain` is not written into the TEI. A human reviews every `confidence=low` row plus a sample of about 20 % of the `medium` ones.

### Stage 0: schema conversion (mechanical)

Foreign format to MHDBDB schema, fully scriptable (reference: `scripts/ingest/ari/01-convert-original-to-mhdbdb.py`):

- Remove the `tei:` prefix, move the elements into the default namespace `http://www.tei-c.org/ns/1.0`
- Normalize the tokenization: `<seg type="token">` becomes `<w>` (keeping the xml:id); `<seg type="pc">` becomes `<pc join="left|right">` by a predecessor heuristic (punctuation attaches to the preceding word, opening characters to the following one)
- A full header from the template (license, author, genre, particDesc; missing fields as TBD placeholders), `<TEI xml:id="{SIGLE}">`, xml-model PIs pointing at `mhdbdb.rng` and `tei_all.rng`
- **Do not silently transform away elements the schema does not know**, but leave them standing and escalate them as a pending decision (the PD-001 pattern, ADR-013 „Daten vor Schema"). During the ARI ingest this led to all 12 standard TEI P5 element classes being taken into the schema as optional elements.

To be settled per source in advance (example answers for ARI in `scripts/ingest/ari/README.md`): the sigle (`{PROJECT}_{SHORTNAME}`), **license compatibility** (ARI: the source's BY-SA is incompatible with BY-NC-SA, so BY-SA was adopted for data and annotations), author attribution (otherwise `person_anonym`), genre from `genres.xml`, and the edition record as a `<biblStruct>`.

### Structural cleanup and paratext policy (#66)

> **Principle:** structural elements are encoded in TEI but excluded from the lexical annotation. Only linguistically relevant tokens go into the lemmatization. Where necessary, new lemmata are created instead of a generic fallback.

| Category | Treatment |
|---|---|
| Running headers (`<fw>`), `<surplus>` | strip the annotation, not lexical |
| Chapter apparatus (e.g. CAPITULUM plus a number) | `<head type="chapter" n="{arabic}">` as the first child of the `<div type="chapter">`; `<milestone unit="chapter" n="N"/>` at the original position in the text flow (TEI P5 allows no `<head>` inside `<l>`) |
| Scribal marks, section initials | `<w>` becomes `<pc join="left">` |
| Roman numerals in the text flow | keep the `<w>`, `lemma_13826` (DIG) |
| Roman numerals as margin counting (stanza, chapter, verse numbers) | strip the annotation, remove the token; the counting belongs in `lg/@n` or the `@n` of the element concerned. Recognizable from the xml:id block: in the legacy Linecode the margin numeral sits in a subunit of its own (`SIG_30040_9` is the verse, `SIG_30041_0` the numeral), while a word of the text always sits in the block of its verse. `@pos="DIG"` is useless as a criterion: in HUG 108 of the 814 margin numerals carried no annotation at all (#138) |
| Foreign-language insertions (Latin, Old Czech …) | keep the `<w>`; assign an existing lemma or create a new language-specific one (e.g. `lemma_78628` for Old Czech glosses) |
| `<div>` hygiene | every `<div>` with an `@type` from the schema enum (`book`, `chapter`, `paratext`, `prologus`, `section`, …) |

### Phase 1: lemmatization

**1a auto-match** (canonical: `wzb-auto-match.py`), the algorithm:

```
lookup = {}                                  # normalized form → set(lemma_id)
for every <entry corresp="lexicon.xml#lemma_N"> in variants.xml:
    for every <form>: lookup[normalize_mhg(form)].add(lemma_N)

for every <w> in the text (the text content is the matching form):
    norm = normalize_mhg(form)
    candidates = lookup.get(norm)
    |candidates| == 1 → write @lemmaRef (matched)
    |candidates| == 0 → unmatched  → report
    |candidates| >  1 → ambiguous  → report
```

**Critical:** the MHG normalization (`â→a, ê→e, î→i, ô→o, û→u, ä→ae, ö→oe, ü→ue, ŏ→oe, ŭ→ue`) has to be applied to **both sides**, because `variants.xml` is not pre-normalized. Python side: `scripts/mhg_normalizer.py`, parity-tested against `assets/js/lib/text-normalizer.js` (`testing/tests/normalization-parity.spec.js`).

**1b disambiguation:** a pending TSV (`xml_id`, `form`, `context` of ±5 words, `match_type`, `candidate_lemmas`, `count`, `resolved_lemma`, `confidence`, `reviewer`), with tiers staggered by frequency: resolve high-frequency ambiguous forms in bulk (plus a patch file for minority readings), medium-frequency ones per instance with a human sample, and deliberately defer hapaxes and the unmatched long tail (an accepted coverage gap). Check unmatched real words against BMZ/Lexer ([Wörterbuchnetz API](https://api.woerterbuchnetz.de)); hand what cannot be resolved to the lexicon team as a frequency-sorted editorial list (`wzb-extract-unmatched.py`). **New lemmata come into being only through an editorial decision**, then a rerun (a closed loop).

### Phase 2: POS tagging

(canonical: `wzb-pos-assign.py`)

```
for every <w> with an @lemmaRef:
    pos_list = lexicon.xml entry → gramGrp/pos
    |pos_list| == 1 → write @pos (auto-inherit)
    |pos_list| >  1 → pending TSV (context decides, e.g. NOM against VRB)
```

Resolution as in 1b (bulk by lemma or form, instance by `xml_id`). QA: every `@pos` has to be in the 19-tag set; human sample of about 5 % per section.

### Phase 3: sense resolution (`@ana`, `@corresp`)

(canonical: `wzb-sense-assign.py`) Precondition: `@lemmaRef` is set, never `@ana` without `@lemmaRef`.

```
for every <w> with an @lemmaRef to lemma L:
    |senses(L)| == 1 → @ana = lexicon.xml#lemma_N_sense_M (auto-assign)
    |senses(L)| >  1 → pending TSV with the candidate senses
    |senses(L)| == 0 → skip + editorial flag (sense-less lemma, usually a backfill stub)

@corresp resolution (once @ana is set):
    types = variants.xml lookup of the word form  ∩  type list in the @ana of the sense
    exactly 1 hit → @corresp = variants.xml#type_K
    0 hits → the form is missing from variants.xml → editorial list; >1 → manual review
```

Candidate senses are presented to the LLM as `sense_id :: concept label DE (EN)` (the labels via `<sense>` → `<ptr target="concepts.xml#…">` → `catDesc/term`). Resolution is either bulk (one sense per lemma where the context of the work forces it, e.g. „bruoder" always meaning a blood relative in the Old Testament) or per instance; `abstain` is a legitimate decision and stays unannotated. **Reference value:** the majority-sense baseline over the annotated corpus is 66.7 % (weighted accuracy, `wzb-sense-baseline.py`); a full pre-registered evaluation protocol (stratification, metrics, blind review) sits in the git history of the feature doc for #34 and in `publications/BLOG-POST-WZB-PIPELINE.md`.

### Backward sync and registration (the mandatory closing steps)

1. **`lexicon.xml` backfill (MANDATORY, [CONTRACTS F.3](CONTRACTS.md#f-authority-source-rules)):** every pipeline minting new lemma or sense ids has to add them to `lexicon.xml` atomically (reference implementation: `scripts/sync/backfill-lexicon.py`, #115). Lemma stubs (form plus POS) can be generated from the corpus; the sense-to-concept assignment is curatorial (F.2, the team). The WZB pipeline was forward-only, and the result was 977 dangling refs, whose category A share was closed by a stub backfill on 2026-07-02 (#115, [ADR-015](DECISIONS.md#adr-015-authority-source-model-the-corpus-leads-ingest-needs-a-backward-sync)). Do not repeat that.
2. **Registration:** a `works.xml` entry (`work_{SIGLE}`, title, genre `<ptr>`, author `@ref`, authority ids), the TEI file into `tei/<SIGLE>.tei.xml`, header sync.
3. **Derived layer:** `extract-variants.py --apply`, then the index rebuilds, then the version bump, then the tests. The binding step sequence is the [Data-Change-Lifecycle](#data-change-lifecycle) directly below.

### Coverage reference values and QA

| Corpus | Language stage | `@lemmaRef` | `@pos` | `@ana` |
|---|---|---|---|---|
| WZB (149,148 tokens, actual 2026-04-15) | MHG | 95.3 % | 95.3 % | 95.2 % |
| ARI (expected) | ENHG | ≥85 % | ≥90 % | – |

100 % is not the goal: the deferred long tail (hapaxes, rare proper names, Latin inflections) is an accepted and documented gap. Automatic checks after every phase: every `@lemmaRef` target id exists (after the backfill; the detector is `check-authority-cross-refs.py`), `@pos` is in the tagset, there is no `@ana` without a `@lemmaRef`, and `build-corpus-index.py` runs over the new text as a smoke test.

---

## Data-Change-Lifecycle

> This is an **active project with ongoing ingest** (see [INDEX.md → Current Phase](INDEX.md#current-phase)). The reader reads TEI live (`tei/<SIG>.tei.xml`) and shows edits immediately, BUT search, lemma counts and every index-backed feature are served from the pre-built `data/*.json.gz`. A data change is only „live" once the derived layer has been rebuilt, versioned and committed. These checklists are the binding step sequence; they replace the rebuild notes formerly scattered across several docs.

Legend for the status column: **CI** means automated (GitHub Actions) · **script** means a guard built into the script · **manual** means documented but not enforced.

**Since #125 (2026-06-12):** the index builds are deterministic (no `generatedAt`, a sorted glob, gzip without mtime), so a no-op rebuild from an unchanged source state produces **no diff** any more, which makes „rebuilding just to be safe" free. The CI gate `data-integrity.yml` rebuilds variants.xml, both indexes and the static JSON API (#45) on every data PR and compares the content (decompressed for the indexes) against the committed state: forgotten rebuilds (steps 4 to 7) block the merge.

**Basic principles for the lifecycle** (an excerpt; the complete rules F.1 to F.3 are normative in [CONTRACTS.md → Authority Source Rules](CONTRACTS.md#f-authority-source-rules)):

1. **The corpus leads, the authority files follow.** `lexicon.xml` and `variants.xml` are derived indexes of the corpus annotation. If a `<w>` carries a `@lemmaRef` or `@ana` missing there, the corpus annotation is authoritative and the authority file has to be brought in line, never the other way round. (The single exception: an obvious typo in the corpus is corrected in the corpus.)
2. **Manual edits count exactly like an ingest.** This step sequence applies to EVERY corpus change, not only to a scripted ingest: a `@pos` corrected by hand, a newly set `@lemmaRef` or a variant annotation as well. The corpus is edited manually all the time (corrections, not just additions), and every such change triggers the same duty to follow up.

### Which steps apply to my change? (routing)

The two checklists below describe the **maximum case**. Not every change needs every step, and one single question decides: does the build read the changed place at all?

**What the four builds read:**

- `build-corpus-index.py` reads from `tei/` the file name and five header statements (the sigle from `idno[@type="sigle"]`, title, author including `@ref`, `msIdentifier/@corresp`, genre term), plus every `<w @lemmaRef>` with non-empty text inside `<body>` including document order, plus the `<l>` boundaries. Everything else in the TEI is invisible to it, in particular `@pos` and `@ana` as well as `<div>`, `<lg>` and `<pb>`. XPaths: [Build Script XPath Reference](#build-script-xpath-reference).
- `extract-variants.py` reads from `tei/` only those `<w>` carrying **both** a `@lemmaRef` and a `@corresp="variants.xml#type_N"`, and from those the lemma id, the type id and the wording. Plus the number of corpus files, which stands in the header of `variants.xml`.
- `build-authority-index.py` reads `authority-files/` exclusively (the seven indexed files including `variants.xml`, without `contributors.xml`). It does not read `tei/`. Unlike the corpus index, here the file decides rather than the element: any change of substance in one of the seven files requires the rebuild. Which markup ends up in the index is in the [Build Script XPath Reference](#build-script-xpath-reference).
- `build-api.py` reads the two built `data/*.json.gz` exclusively, neither `tei/` nor `authority-files/`.

**Routing by type of change:**

| Changed | Steps needed | Build time |
|---|---|---|
| `tei/`: `@pos` or `@ana`; `<note>` in the header, the encoding description, `<respStmt>`; `<div>`, `<lg>`, `<pb>`, comments, indentation outside `<w>`. Condition: the sequence of `<w>` and the `<l>` boundaries stay unchanged | no rebuild, and therefore no version bump either. What remains is step 2 (schema) and step 8 (cross-ref audit), then commit and push | 0 s |
| `tei/`: `<l>` boundaries moved, or one of the five header statements changed. No `<w>` added, removed, or changed in wording, `@lemmaRef` or `@corresp` | the corpus checklist without steps 5 and 6 | about 50 s |
| `tei/`: the stock of `<w>`, their wording, `@lemmaRef` or `@corresp` touched; a file added or removed | the corpus checklist in full | about 85 s |
| `authority-files/contributors.xml` | no rebuild, no bump (none of the outputs contains the file). Schema and cross-ref audit, then commit and push | 0 s |
| One of the seven indexed `authority-files/` other than `works.xml` | the authority checklist in full except step 1 | about 17 s |
| `authority-files/works.xml` | the authority checklist in full | about 17 s plus the Zotero run |

The version bump (corpus checklist step 3, authority checklist step 2) is dropped only in the rows without a rebuild. As soon as an index is rebuilt it is mandatory, because the browser invalidates its 30-day cache through the version number alone (#94). Since #154 `scripts/audit/check-index-version-bump.py` catches the forgotten bump: it compares the decompressed index content against the diff base and runs in `data-integrity.yml` deliberately **before** the rebuild step. Two gaps remain: without a determinable diff base (`workflow_dispatch`, a force push) the workflow skips the gate with a `notice`, and it does not cover the version statements in the documentation (TEI-MODEL.md §11, INDEX.md).

The converse also holds: do not set a bump without a change of content. It forces every returning person to reload the index although nothing changed, and no CI notices.

Individual times, measured on 2026-07-31 over 667 corpus files on a Windows laptop with 16 cores, using the default of 8 parallel processes set in #284: `build-corpus-index.py` 46 s, `extract-variants.py --apply` 23 s, `build-authority-index.py` 12 s, `build-api.py` 4 s. Sequentially (`--jobs 1`) it was 184 s, 97 s, 12 s and 4 s, so 297 s in total instead of 85 s. On machines with fewer cores the value lies in between, the default being `min(8, cpu_count)`. Orders of magnitude for planning, not a guarantee.

A rebuild may be dropped, an inspection may not: `<div>`, `<lg>` and `<pb>` are invisible to the indexes but not to the **reading view** (which renders chapter `<div>`, stanzas and page breaks, see #17/#101). Whoever changes something there looks at the text in the reader, even if the table says 0 s. The same holds for `@n`: the margin numbers and the `?verse=` deep links resolve directly against it (`data-n` in `tei-text-reader.js`). A renumbering therefore silently retargets every link already shared, at 0 s build time and without a CI signal.

**Two peculiarities of `variants.xml`** that can make the diff larger than expected, neither of them an error: a corpus file added or removed changes the file even if it contains not a single variant-bearing `<w>` (the file count sits in the header). And per type id the most frequent form in the **entire** corpus decides, so an intervention in one text can rewrite entries attested only in other texts.

**When in doubt, build.** Since #125 a rebuild from an unchanged source state produces no diff. Overestimating therefore costs waiting time only, underestimating produces silent drift. The table saves time where the case is clear, it does not replace building in a borderline case.

Row 2 against row 3 can be measured instead of guessed: run `extract-variants.py` **without** `--apply` and read the four semantic counters in its output (`added`, `removed`, `form text changed`, `lemma assignment changed`). All four at 0 means row 2, provided no corpus file was added or removed: the file count in the header is the fifth condition and does not show up in the counters. The dry run costs the same scan, does not touch `variants.xml` and drops its result as `authority-files/variants.regen.xml`, which must not be committed. Do not decide via `--apply` plus `git status`: the script itself warns against that fallacy at this point, because a byte diff can also come from lxml serialization drift (the local version against the pin in `requirements.txt`) without anything having changed in substance.

### When `tei/` changes (scripted ingest, a new text OR a manual correction)

| # | Step | Breaks if forgotten | Status |
|---|---------|----------------------|--------|
| 1 | UTF-8, namespace `http://www.tei-c.org/ns/1.0`; position-bearing annotation on `<w @lemmaRef>` (only those count for positions) | the word is invisible to search, highlight positions are wrong | manual |
| 2 | Schema: `python scripts/audit/validate-corpus.py --sample <SIG>` | invalid TEI; `data-integrity.yml` catches it on PR/push | CI |
| 3 | Bump the version (the `'version'` dict literal in `build-*-index.py` plus `corpus-loader.js`), then `python scripts/audit/check-index-versions.py` | returning users keep the 30-day IndexedDB cache with the old index (#47.3/#94) | CI (consistency plus the #154 bump gate, see the routing section) |
| 4 | Corpus index: `python scripts/build-corpus-index.py` (the pre-flight aborts on a dirty tree, otherwise `--allow-dirty`) | search, hit counts, proximity, verse position and the playground analyses go stale; a new text is missing entirely | CI (freshness gate in data-integrity.yml) |
| 5 | **For new forms:** `python scripts/sync/extract-variants.py --apply` (`variants.xml` is corpus-derived) | new word forms do not resolve to their lemma (stage 2 resolution); the lemma page chips are incomplete | CI (freshness gate) |
| 6 | After step 5: `python scripts/build-authority-index.py` | the variant map in the index stays stale | CI (freshness gate) |
| 7 | Regenerate the API: `python scripts/build-api.py` (it reads both `data/*.json.gz`, hence after steps 4 and 6; the freshly built, still uncommitted indexes require `--allow-dirty` locally) | the static JSON API under `api/` serves stale or orphaned records | CI (freshness gate in data-integrity.yml) |
| 8 | Cross-ref audit: `python scripts/audit/check-authority-cross-refs.py --check` | dangling refs (lemma or variant not found, empty panels) | CI (in `data-integrity.yml`) |
| 9 | `python scripts/validate-indices.py` plus `npm test` (**ask the user first**) | structural index or frontend regression | manual |
| 10 | Commit **the TEI, the built `data/*.json.gz`, `api/` and the bumps together**, staging files by name (never `git add -A`, the working dir is shared) | production serves a stale search or an old cache | manual |
| 11 | Push to main, GitHub Pages deploys statically (~2 to 5 min, no Pages build) | it never reaches production; what is committed is what ships | CI (auto deploy) |

### When `authority-files/` changes

| # | Step | Breaks if forgotten | Status |
|---|---------|----------------------|--------|
| 1 | (`works.xml` only) `enhance_works_with_zotero.py` plus `sync_tei_headers.py --works` (with `--dry-run` first) | editor and bibliography plus headers go stale (only WorksSyncer is implemented, persons/genres/concepts are TODO stubs) | manual |
| 2 | Bump the version (`build-authority-index.py` plus `corpus-loader.js`) plus `check-index-versions.py` | a stale cache for up to 30 days | CI (consistency plus the #154 bump gate, see the routing section) |
| 3 | **Authority index: `python scripts/build-authority-index.py`** (the frontend reads ONLY the index, never the XML) | every authority change stays invisible until rebuild and commit (this is how the lexicon/variants drift went unnoticed) | CI (freshness gate in data-integrity.yml) |
| 4 | Regenerate the API: `python scripts/build-api.py` (after step 3; the freshly built, still uncommitted index requires `--allow-dirty` locally) | the static JSON API under `api/` serves stale authority records | CI (freshness gate in data-integrity.yml) |
| 5 | Cross-ref audit `--check` plus schema `validate-corpus.py --fail-fast` | dangling refs or invalid XML | CI |
| 6 | Commit the built `data/authority-index.json.gz`, `api/` and the bumps, by name | production serves the old index | manual |

**Decoupling:** a pure `authority-files/` change needs **no** corpus index rebuild (`build-corpus-index.py` does not read `authority-files/`). A pure `tei/` change needs the authority rebuild only if new forms force a regeneration of `variants.xml` (step 5 into step 6). Which steps drop out in a given case is in the [routing table](#which-steps-apply-to-my-change-routing) above.

**Open gap (no trigger):** the curatorial remainder of the `lexicon.xml` backfill (396 dangling refs across 109 ids: category B is the sense-to-concept assignment on existing lemmata, category C is typos and homographs needing a corpus correction; #44/#115). **Cause:** the ingest pipelines (WZB phases 1b to 3, 2026-04/05) were pure forward pipelines without a lexicon follow-up; the automatable category A share (125 missing `<entry>`, 581 refs) was closed as stubs on 2026-07-02 via `scripts/sync/backfill-lexicon.py` (orth is the dominant corpus form, senses without a concept `<ptr>`, so the review of base form and concept stays curatorial). This is **not** a Salzburg re-export problem (the repository is the master) but a missing backward synchronization. Lemma stubs (form plus POS) can be generated from the corpus; the **sense-to-concept assignment is curatorial** (the team assigns the concept, it cannot be reconstructed from the corpus). Until the backfill lands, the cross-ref CI tolerates the legacy stock through an id-set ratchet (the committed `scripts/audit/lexicon-baseline.json`, #152): refs outside `lexicon.xml` break the build immediately, and so does every dangling lexicon id outside the baseline (even with a compensating backfill in the same PR); once a backfill has landed, run `--update-baseline` and commit the file diff along. `scripts/audit/check-lexicon-senses.py` detects sense-less lemmata locally. For the consequence for future ingests see [DECISIONS.md → ADR-015](DECISIONS.md#adr-015-authority-source-model-the-corpus-leads-ingest-needs-a-backward-sync).

---

For technical implementation, see [ARCHITECTURE.md](ARCHITECTURE.md).
For architecture decisions, see [DECISIONS.md](DECISIONS.md).
