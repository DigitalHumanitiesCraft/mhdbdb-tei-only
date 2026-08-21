# MHDBDB TEI Target Model

Defines the normative TEI encoding for all texts in the MHDBDB corpus. New texts **must** conform to this model. Existing texts are migrated incrementally (see Issue #30).

> **Audience:** This file is a technical reference specification, written primarily for development and automated tooling (precise, machine-oriented). A general introduction is offered by the help pages of the website, for example [Daten & Downloads](https://dhcraft.org/mhdbdb-tei-only/hilfe-daten.html) and [Eigene Texte beitragen](https://dhcraft.org/mhdbdb-tei-only/hilfe-daten-beitragen.html).

**Issue:** #32 (TEI schema)
**Schema:** `schema/mhdbdb.rnc` (RELAX NG compact, source of truth) + `schema/mhdbdb.rng` (generated via `trang`)
**Validated against:** TEI P5 version 4.11.0 (`tei_all.rng`, 18 Feb 2026)
**Maximal example:** `schema/examples/corpus.example.tei.xml` (validated against tei_all.rng)

---

## 1. Document Skeleton

Every TEI file follows this structure:

```xml
<?xml version='1.0' encoding='UTF-8'?>
<TEI xmlns="http://www.tei-c.org/ns/1.0" xml:id="{SIGLE}">
  <teiHeader>
    <!-- Section 2: Header -->
  </teiHeader>
  <text>
    <body>
      <!-- Section 3: Body (genre-specific) -->
    </body>
  </text>
</TEI>
```

**Rules:**
- Namespace: `http://www.tei-c.org/ns/1.0` (always)
- Encoding: UTF-8 (always)
- `@xml:id` on `<TEI>`: the text sigle (e.g., `ABG`, `WUT`, `SUB1`)
- Sigle format: uppercase letters + optional digits, no spaces

---

## 2. Header Template (`<teiHeader>`)

The header is already largely standardized across all 667 files. This section documents the canonical structure.

### 2.1 `<fileDesc>`

```xml
<fileDesc>
  <titleStmt>
    <title xml:lang="de">{work title}</title>
    <author ref="#person_{id}">{author name}</author>
    <respStmt>
      <resp>digitale Zusammenfuehrung, Annotation und semantische Klassifikation</resp>
      <name ref="https://mhdbdb.plus.ac.at" xml:lang="de">
        Mittelhochdeutsche Begriffsdatenbank (MHDBDB)
      </name>
    </respStmt>
  </titleStmt>

  <publicationStmt>
    <!-- standard block: MHDBDB/Uni Salzburg, CC BY-NC-SA 4.0 -->
    <!-- identical in all files -->
  </publicationStmt>

  <sourceDesc>
    <msDesc>
      <msIdentifier corresp="works.xml#work_{id}">
        <idno type="sigle">{SIGLE}</idno>
        <idno type="handschriftencensus">{HC no.}</idno>  <!-- optional, 354 texts -->
        <idno type="GND">{GND no.}</idno>                 <!-- optional, 216 texts -->
        <idno type="wikidata">{Q no.}</idno>              <!-- optional, 129 texts, work level -->
        <idno type="mwb-sigle">{MWB short sigle}</idno>   <!-- optional, 19 texts -->
        <msName xml:lang="de">{work title}</msName>
      </msIdentifier>
      <additional>
        <listBibl>
          <!-- primary edition as <biblStruct> -->
          <biblStruct type="{book|bookSection}" xml:id="{SIGLE}_{SIGLE}"
                      corresp="{Zotero URI}" key="{SIGLE}">
            <!-- monogr or analytic+monogr -->
          </biblStruct>

          <!-- optional: digital intermediary -->
          <bibl type="digitalIntermediary" xml:id="{SIGLE}_etext_{name}"
                corresp="#{SIGLE}_{SIGLE}">
            <title>Elektronische Zwischenstufe ({Beschreibung})</title>
            <note type="provenance">...</note>
            <note type="fidelity">...</note>
          </bibl>
        </listBibl>
      </additional>
    </msDesc>
  </sourceDesc>
</fileDesc>
```

**Rules:**
- `<author ref>` points at the `<person>` entry in the same document (`profileDesc`), which in turn points at `persons.xml` via `@corresp`
- `<msIdentifier corresp>` points at `works.xml` via fragment ID (`works.xml#work_{id}`)
- the primary edition is always a `<biblStruct>` with a Zotero `corresp`
- digital intermediaries as `<bibl type="digitalIntermediary">` (ADR-012)

**Excerpt texts (#134):** if the corpus text is a defined excerpt from a larger work (for example AK = "Buch von Akkon" inside the Steirische Reimchronik), the primary edition additionally carries `<biblScope unit="verse">{from}–{to}</biblScope>` in the `<imprint>` plus, optionally, `<note type="context">{contextual relation}</note>` on the `<biblStruct>`. The `unit="verse"` is the machine-readable excerpt signal: the reader then shows a banner plus "Ausschnitt" metadata (excerpt title from `<analytic>/<title>`). An `<analytic>` title alone marks NO excerpt: 534 headers carry one for ordinary edition data.

### 2.1bis Editor attribution and credits

Attribution of the people who worked on the MHDBDB runs centrally through `authority-files/contributors.xml` (see [`TEI-MODEL-AUTH-FILES.md`](TEI-MODEL-AUTH-FILES.md) §3.8). The corpus headers reference that register via `@ref`; the header spells out by name only what varies per file or has to be directly visible to readers.

**What goes where:**

| Information | Place in the header | Pattern |
|-------------|-----------------|--------|
| collective team attribution | `<titleStmt>/<respStmt>` | `<orgName ref="contributors.xml#mhdbdb-team">` |
| founders + coordinator (always the same, all 667 files) | `<publicationStmt>/<authority>` | `<persName role="founder\|coordinator" ref="contributors.xml#contrib_00X">` |
| prominent lead editor (only for TKR/TKA/VTC/PUC/JT/WZB) | second `<titleStmt>/<respStmt>` | `<name role="lead-editor" ref="contributors.xml#contrib_00X">` |

**Example (ABG after the 2026-04-14 migration):**

```xml
<titleStmt>
  <title xml:lang="de">Von abgescheidenheit (Traktat)</title>
  <author ref="#person_445">Meister Eckhart</author>
  <respStmt>
    <resp>digitale Zusammenfuehrung, Annotation und semantische Klassifikation</resp>
    <orgName ref="contributors.xml#mhdbdb-team">MHDBDB-Team (vollständige Liste in contributors.xml)</orgName>
  </respStmt>
</titleStmt>
<publicationStmt>
  <!-- ... -->
  <authority>
    <persName role="coordinator" ref="contributors.xml#contrib_003">
      <forename>Katharina</forename><surname>Zeppezauer-Wachauer</surname>
    </persName>
    <persName role="founder" ref="contributors.xml#contrib_001">
      <forename>Klaus M.</forename><surname>Schmidt</surname>
    </persName>
    <persName role="founder" ref="contributors.xml#contrib_002">
      <forename>Horst</forename><surname>Pütz</surname>
    </persName>
  </authority>
  <!-- ... -->
</publicationStmt>
```

**Additional pattern for lead editors** (currently TKR/TKA/VTC/PUC with Brom, JT with Woesner, WZB with Hintersteiner):

```xml
<titleStmt>
  <title>...</title>
  <author>...</author>
  <respStmt>
    <resp>digitale Zusammenfuehrung, Annotation und semantische Klassifikation</resp>
    <orgName ref="contributors.xml#mhdbdb-team">...</orgName>
  </respStmt>
  <respStmt>
    <resp>Haupt-Editor dieser Ausgabe</resp>
    <name role="lead-editor" ref="contributors.xml#contrib_004">Vlastimil Brom</name>
  </respStmt>
</titleStmt>
```

**Rules:**
- `<orgName>`/`<persName>`/`<name>` ALWAYS carry the attribution information through `@ref`, never through inline text alone. The visible text is frozen, the canonical source is `contributors.xml`.
- `@ref` on `<orgName>` is meant for organization records in `contributors.xml` (MHDBDB team, Digital Humanities Craft). For the homepage of an organization, `contributors.xml` uses the TEI-P5-idiomatic pattern `<org><idno type="URL">https://...</idno></org>` instead of `@ref`.
- `<persName role>` inside the `<authority>` block may only carry the fixed roles from the authority schema: `"founder" | "coordinator" | "lead-editor" | "editor"`.
- 50+ further editors who worked on the existing texts are listed only in `contributors.xml`, NOT inline in the respective corpus header, to keep the header lean.

### 2.1a `<monogr>` element order

TEI P5 requires in `<monogr>`: `(author|editor)*, title+, editor*, (idno|imprint)*`. That means `<author>` **before** `<title>`, `<idno>` **after** `<editor>`. A few existing files (WUT for example) have the wrong order and fail tei_all validation.

### 2.2 `<encodingDesc>`

```xml
<encodingDesc>
  <projectDesc>
    <!-- standard block: MHDBDB description DE + EN -->
  </projectDesc>
  <editorialDecl>
    <!-- standard block: explanation of the local file references DE + EN -->
    <interpretation>
      <p>Part-of-Speech-Tags folgen dem MHDBDB-Tagset (19 Tags).
         Dokumentation: .gemini/skills/pos-disambiguator/SKILL.md</p>
    </interpretation>
  </editorialDecl>
  <classDecl>
    <taxonomy xml:id="genres">
      <bibl>Genreklassifikation gemaess der Textreihentypologie
        <ptr target="https://www.mhdbdb.sbg.ac.at/textreihen"/>
      </bibl>
      <category xml:id="genre_{hash}" ana="parent" corresp="genres.xml#genre_{hash}">
        <!-- parent genre with glosses DE/EN -->
      </category>
      <category xml:id="genre_{hash}" corresp="genres.xml#genre_{hash}">
        <!-- specific genre with glosses DE/EN -->
      </category>
    </taxonomy>
  </classDecl>
</encodingDesc>
```

### 2.3 `<profileDesc>`

```xml
<profileDesc>
  <langUsage>
    <language ident="gmh">Mittelhochdeutsch (ca. 1050-1350)</language>
    <language ident="la">Latein</language>  <!-- where present -->
  </langUsage>
  <particDesc>
    <listPerson>
      <person xml:id="person_{id}" corresp="persons.xml#person_{id}">
        <persName type="preferred">{author name}</persName>
        <idno type="GND">{GND no.}</idno>          <!-- optional -->
        <idno type="wikidata">{Q no.}</idno>        <!-- optional -->
        <note type="works">{work_id1},{work_id2}</note>
      </person>
    </listPerson>
  </particDesc>
</profileDesc>
```

### 2.4 `<revisionDesc>`

```xml
<revisionDesc>
  <change when="{YYYY-MM-DD}" who="#{editor-id}">{description}</change>
</revisionDesc>
```

---

## 3. Body Structure (genre-specific)

### 3.1 Verse texts (epic, lyric)

**Target structure:**

```xml
<body>
  <div type="section" n="1">           <!-- optional: book/section -->
    <lg type="stanza" n="1">
      <l n="1">
        <w xml:id="..." ...>wort</w>
        <w xml:id="..." ...>wort</w>
      </l>
      <l n="2">...</l>
    </lg>
    <lg type="stanza" n="2">...</lg>
  </div>
</body>
```

**Rules:**
- lines of verse as `<l>` with `@n`
- stanzas as `<lg>` with `@n`. Allowed `@type` values: `stanza`
- optional enclosing `<div>` for books/sections
- for songs: `<div type="song">` > `<lg type="stanza">` > `<l>`
- caesuras as `<caesura/>` inside `<l>` (optional, rare)

**Current state:** most verse texts have `<l>` without an `<lg>` wrapper. The migration happens step by step (issue #30, stage 2).

### 3.2 Prose texts

**Target structure:**

```xml
<body>
  <div type="chapter" n="1">
    <head>
      <w xml:id="..." ...>Kapiteltitel</w>
    </head>
    <p>
      <lb n="1"/>
      <w xml:id="..." ...>wort</w>
      <w xml:id="..." ...>wort</w>
      <lb n="2"/>
      <w xml:id="..." ...>wort</w>
    </p>
  </div>
</body>
```

**Rules:**
- paragraphs as `<p>`
- line breaks as `<lb/>` (line beginning) with `@n`
- chapters/sections as `<div type="chapter">` with `<head>`
- `<l>` is reserved for verse texts, `<lb/>` for prose line breaks
- 18 prose texts in the existing corpus are being migrated (`<l>` → `<lb/>`), see [Section 8.1](#81-l-vs-lb-in-prose-migration)

### 3.3 Recipe texts (cookbooks, medical texts)

**Target structure:**

```xml
<body>
  <div type="recipe" n="1">
    <head>
      <w xml:id="..." ...>Rezepttitel</w>
    </head>
    <p>
      <lb n="1"/>
      <w xml:id="..." ...>wort</w>
      <w xml:id="..." ...>wort</w>
    </p>
  </div>
  <div type="recipe" n="2">...</div>
</body>
```

**Rules:**
- every recipe as `<div type="recipe">` with `@n` (recipe number from the edition)
- recipe title as `<head>` inside the `<div>`
- running text in `<p>` with `<lb/>` for line breaks

### 3.4 Mixed texts

Texts with both verse and prose sections use nested `<div>` elements:

```xml
<body>
  <div type="section" n="1">
    <!-- prose section -->
    <p>...</p>
  </div>
  <div type="section" n="2">
    <!-- verse section -->
    <lg type="stanza" n="1">
      <l n="1">...</l>
    </lg>
  </div>
</body>
```

### 3.5 `div/@type` values (audit)

15 distinct values in the existing corpus. They came over as 1:1 translations from the old database export (Julia's TEI documentation, June 2024).

For the full list of accepted values see the table "All div/@type decisions in full" below.

**Design decision: `song` stays broad, no differentiation into `spruch`/`leich`**

Middle High German lyric scholarship distinguishes between Lied, Spruch and Leich. The question was whether future ingests should differentiate more finely. Decision: **no.**

1. **Unstable in the discipline:** the triad Lied/Spruch/Leich is a modern scholarly categorization, not a medieval self-description. The boundaries are contested in German studies: texts move between forms, assignments depend on the state of research (Hugo von Montfort, for example, is "Lied" or "Rede" depending on the edition).
2. **The information already has a better place:** the genre typology in `<classDecl>` holds 600+ genre labels. Minnelied, Spruchdichtung and Leich can be distinguished finely there as genre categories. `div/@type` marks the **structural unit** (= numbered lyric unit), not the genre.
3. **Consistency beats precision:** 1,406 existing `song` units would have to be reclassified (not scriptable, it needs philological case-by-case decisions). Every future ingest would have to be judged text by text.

In the MHDBDB model `song` means **"numbered lyric unit"**, deliberately broader than the scholarly terminology. Finer distinctions are made through the genre taxonomy in the header.

**Migration (decided):**

| Type | Count | Examples | Action |
|-----|-------|-----------|--------|
| `stanza` | 1,122 | LZT | ✓ migrated to `<lg type="stanza">` (#23, index v4.1.1); 0 `div type="stanza"` left in the corpus |
| `deed` | 300 | HZU, HZU2 | → `number` (the genre sits in the header; `deed` was a genre marker, not a structural type) |
| `part` | 176 | DL2, EHB | → `section` (identical use, leftover from the migration) |
| `sermon` | 113 | ADP, ECK | → `number` (the genre sits in the header; same as `deed`) |
| `subsection` | 3 | KVM | → `section` (nesting instead of a type of its own) |
| `§` | 7 | KVM | encoding artefact (Linecode conversion) → `section` |
| `sigil` | 9 | BOP | song sigles from the edition → `number` (same as deed/sermon) |

**Rationale for `deed`/`sermon` → `number`:** these `div` types mark no genre information (that comes from the `<classDecl>` taxonomy in the header) but numbered units (charter no. 1, sermon no. 2). The type `number` expresses the function correctly. An existing `@n` is kept.

**In addition: `note type="date"` and `note type="year"` in HZU/HZU2**

HZU (36 date notes + 19 year notes) and HZU2 (241 date notes + 100 year notes) carry dates inside charters:

```xml
<note type="year" n="1293"/>        <!-- year, unambiguous -->
<note type="date" n="24. Februar"/> <!-- plain-text format, Austrian German (Jaenner instead of Januar) -->
```

**History:** the `n` attribute on `<note type="date">` used to carry a compact MMDD encoding (last two digits = day, the rest = month: `"224"` = 24 February, `"1211"` = 11 December). The migration to plain text is done (as part of the phase D normalization in 2026-04, documented as #84). As of 2026-04-15 all 277 date notes in both files are in plain-text form; new ingests should use that form directly, not the old compact one.

**Further migrations (decided on 2026-04-09):**

| Type | Count | Examples | Action |
|-----|-------|-----------|--------|
| `paragraph` | 76 | BDK | → `number` (Katharina: "get rid of it, more trouble than use") |
| `volume` | 7 | FLG, FLG1 | → remove (obsolete, purely technical reasons; the metadata suffice) |

**`volume` special cases (FLG, FLG1, PL1-3):**

Katharina: "volume and part had purely obsolete technical reasons. This can move into the metadata."

- **FLG** (books 1-2, edition 2009) + **FLG1** (books 3-7, edition 1990-93): merging is **not recommended**, the editions differ. Remove `div type="volume"`, keep the book numbers as `div type="section"`.
- **PL1/PL2/PL3** (Prosa-Lancelot): merging is **possible**, the structure is identical (same author, flat `<body><p>`), only the text differs. But: 822k `<w>` in total makes for a huge file. Separate files with `section` divs instead of `volume` is the more pragmatic option.

**All `div/@type` decisions in full:**

| Type | Count | Examples | Status |
|-----|-------|-----------|--------|
| **`song`** | 1,406 | BOP, BRH | ✓ accepted |
| **`chapter`** | 2,107 | AC1, BDK, PZ, WH | ✓ accepted |
| **`recipe`** | 606 | ABS, BRIX | ✓ accepted |
| **`section`** | 460 | DL1, DL2, EHB, KVM | ✓ accepted (incl. ex-part/subsection/§) |
| **`number`** | 498 | HZU, ADP, BDK, BOP | ✓ accepted (incl. ex-deed/sermon/sigil/paragraph) |
| **`parallel`** | 51 | BRW, DES2, FR3 | ✓ accepted (parallel transmission) |
| **`colophon`** | 15 | ALX, APO | ✓ accepted (TEI has `<colophon>`, but `div type` is compatible) |

All numbers recounted on 2026-08-09 across all 667 corpus files (`div[@type]`, 5,143 in total, no further types). Against the count of 2026-07-30 only `chapter` moved, 1,640 → 2,107: #358 gave the Willehalm the 467 `<div type="chapter">` its thirty-line sections had never had. Until then all 14,002 of its `<l>` hung in a single `<p>` and the section number lived only in the word ids plus a `<pb n="77"/>`, which claimed a page beginning where 465 of the 467 units hold exactly 30 verses. The Parzival, same author and same convention, had encoded it as `<div>` from the start and carries no `<pb>` at all. Five of the seven values had been wrong before, and only three of the deviations go back to #236: `song` −13 and `parallel` +36 (FR3 rebuilds 23 equally ranked Töne into 10 Töne with 36 `div[@type="parallel"]`), `section` −36 from the same rehanging. `chapter` 604 → 1,640, `recipe` 452 → 606 and the rest of `section` had already drifted before that, presumably since the WZB ingest; they are corrected here as well, so that the table is not half right.

**Stanza check (verified):** `div type="stanza"` historically existed only in LZT (1,122) and has been migrated to `lg type="stanza"` since #23/v4.1.1; currently **0** `div type="stanza"` in the corpus (LZT now uses `lg type="stanza"`).

---

## 4. Word element (`<w>`)

The `<w>` element is the central unit of annotation. In the target model all its attributes come from TEI P5 `att.linguistic` and `att.global.analytic` (since TEI 3.3.0, Jan 2018).

> **Status (phase B1/B2, 2026-04, completed):** the migrations `@meaningRef → @ana` and `@wordRef → @corresp` that were once needed have been carried out across the corpus (WZB included). There are **0** remaining `@meaningRef`/`@wordRef` attributes, **667/667** files use `@ana`, and no active JS or Python code reads the old names (the `@meaningRef` hit in `WZB.tei.xml` is only a `revisionDesc` log entry, not an attribute). §§4.1, 4.3 and 4.4 document the migrated model and the migration history; compare §10 "Earlier errors (all fixed by migration)".

**Before** (existing data up to phase B1/B2):
```xml
<w xml:id="{SIGLE}_{page}{line}_{pos}"
   lemmaRef="lexicon.xml#lemma_{id}"
   pos="{POS-Tags}"
   meaningRef="lexicon.xml#lemma_{id}_sense_{id}"
   wordRef="lexicon.xml#lemma_{id}_sense_{id}_type_{id}">visible text</w>
```

**Now** (TEI-conformant, migrated):
```xml
<w xml:id="{SIGLE}_{page}{line}_{pos}"
   lemmaRef="lexicon.xml#lemma_{id}"
   pos="{POS-Tag}"
   ana="lexicon.xml#lemma_{id}_sense_{id}"
   corresp="variants.xml#type_{id}">visible text</w>
```

### 4.1 Attributes

| Attribute | TEI status | Required | Current (audit) | Target |
|----------|------------|---------|-------------|------|
| `@xml:id` | standard (att.global) | yes | 9,282,982 (100%) | keep |
| `@lemmaRef` | **standard** (att.linguistic) | yes* | 7,391,273 (79.6%) | keep |
| `@pos` | **standard** (att.linguistic) | yes* | 7,406,168 (79.8%) | keep |
| `@ana` | **standard** (att.global.analytic) | no | ~5.9M (migrated from `@meaningRef`, phase B1) | keep |
| `@corresp` | **standard** (att.global) | no | ~7.5M (migrated from `@wordRef`, phase B2; URI → `variants.xml`) | keep |

Corpus at the time of the audit (#32, 2026-04, before WZB): 9,282,982 `<w>` elements in 666 files; 20.4% without `@lemmaRef` (unannotated words, skipped by the corpus index, see CONTRACTS.md sec. B). Current state: 667 files, 9,431,311 `<w>`, of which 7,533,010 with `@lemmaRef` and 1,898,301 without (20.13%), measured 2026-08-21 with `scripts/audit/quantify-unannotated-tokens.py`. The figure 9,432,130 from 2026-06-10 (Code4Lib article, #142) predates the token removals from #138 and #236.

> **Important:** `@lemmaRef` has been a standard attribute of the class `att.linguistic` since TEI P5 3.3.0 and did **not** have to be migrated. `@meaningRef` and `@wordRef` **were** the validation blockers (not TEI standard attributes); they were migrated corpus-wide to `@ana` and `@corresp` respectively (phase B1/B2, completed, 0 remaining occurrences, 667/667 files with `@ana`).

### 4.2 `@xml:id` format

```
{SIGLE}_{page}{line}_{word position}

Examples:
  ABG_400001_0    (ABG, page 400, line 001, word 0)
  WUT_101_0       (WUT, line 101, word 0)
  WZB_1ra_6_5     (WZB, folio 1ra, line 6, word 5)
```

The format varies for historical reasons. New texts should use a consistent scheme. IDs have to be unique within a document.

### 4.3 Migration plan (completed, phase B1/B2)

> A historical plan. The migration was carried out corpus-wide in 2026-04 (WZB included); the table documents what was done.

| Attribute | TEI status | Action | Effort | Dependency |
|----------|------------|--------|---------|---------------|
| `@lemmaRef` | standard | **keep** | none | – |
| `@pos` | standard | **keep** | none | – |
| `@meaningRef` | not standard | **→ `@ana`** | small (rename) | playground JS (8 places, 2 of them critical) |
| `@wordRef` | not standard | **→ `@corresp`** | small (rename + URI correction) | see sec. 4.4 |

**Priority:** `@meaningRef` → `@ana` and `@wordRef` → `@corresp` are both needed for TEI conformance. Both are batch renames (change the attribute name). For `@wordRef` the URI has to be corrected as well (see sec. 4.4).

**Code adjustment `@meaningRef` → `@ana`** (✓ done): the active playground JS already reads `@ana` (querySelectorAll `[ana]`/`getAttribute('ana')`). There are **0** places in the active JS code that read `meaningRef`/`wordRef` (confirmed by grep across `assets/` + `playground/`, 2026-06-05). Python references only in the archived `_ARCHIVED_tei-transformation.py` (not active).

**`@lemma` deliberately not implemented:** TEI P5 allows `@lemma` (att.linguistic) as a human-readable base form directly on the word. We do not set it. Reasons:

- **Denormalization.** The source of truth for the base form is `lexicon.xml` → `<form type="lemma"><orth>`. `@lemma` would be a redundant copy next to `@lemmaRef`. That contradicts the principle from [TEI-MODEL-AUTH-FILES.md](TEI-MODEL-AUTH-FILES.md) sec. 2.2 ("bidirectional links: one direction is master, the other one is derived"), which holds for the authority files and is carried through here.
- **Data volume.** ~9.3M `<w>` elements × ~10 bytes → around 90 MB of additional raw XML across 667 files with no functional gain.
- **No consumer.** Neither `build-corpus-index.py` (which reads only `@lemmaRef` and extracts the ID) nor the JS renderer (`tei-text-reader.js`) reads `@lemma`. Displaying the base form happens in the browser through the authority index.
- **Sync risk.** Every orthographic correction in the lexicon would have to propagate into all 667 corpus files, otherwise they drift apart.

The human-readable base form stays accessible through the lookup `@lemmaRef` → `lexicon.xml`: for debug inspection via `xmllint`/`grep`, for tooling via the authority index.

**WZB:** WZB is migrated as well and uses `@ana` (141,978 occurrences). The only `@meaningRef` hit in `WZB.tei.xml` is a `<change>` log entry in the `revisionDesc`, not an attribute.

### 4.4 `@wordRef` → `@corresp`: keeping the word-form reference (✓ completed)

> The migration is done; this section documents the reasoning (why it was not deleted) and the URI correction.

`@wordRef` was not a TEI standard attribute, but it carried **information that cannot be reconstructed** (hence the migration to `@corresp` instead of deletion):

- ~21% of the `<w>` elements **with** `@wordRef` have no `@meaningRef` (1,553,943 of 7,406,166): without a sense the lookup path sense→type is impossible
- 42 of 43,404 senses have types with identical form text: even with a sense, text matching is not unambiguous
- `@wordRef` is the only direct link from an attestation to its word form (type) in `variants.xml`

**Reference chain:**
```
@wordRef="lexicon.xml#lemma_2598_sense_77615_type_8717"  (before: synthetic URI)
    │
    ├─ lexicon.xml: <sense xml:id="lemma_2598_sense_77615" ana="#type_8717 ...">
    │
    └─ variants.xml: <form xml:id="type_8717">hân</form>
```

**Migration (✓ completed):** `@wordRef` became `@corresp` (a standard attribute from `att.global`). The URI was corrected in the process, because the target sits in `variants.xml`, not in `lexicon.xml`:

```
before:  wordRef="lexicon.xml#lemma_2598_sense_77615_type_8717"  (synthetic, wrong file)
now:     corresp="variants.xml#type_8717"                        (direct, correct file)
```

**Implementation:** a batch transformation extracted the `type_{id}` part from the synthetic URI and set it as `variants.xml#type_{id}`. No active code read `@wordRef`, so no JS adjustment was needed.

---

## 5. POS tagset (19 tags)

The canonical tagset for all MHDBDB texts. Full reference (tag table, compound rules, legacy mapping, corpus distribution): [POS-TAGSET.md](POS-TAGSET.md). The operational disambiguation workflow is implemented as the agent skill `.gemini/skills/pos-disambiguator/`.

> **Note:** `ART` is not a valid tag. Articles are tagged `DET`.

| Tag | Name | Examples |
|-----|------|-----------|
| **NOM** | noun | acker, zit, minne |
| **NAM** | proper name | Uolrich, Wiene, Rhin, sant (before names) |
| **ADJ** | adjective | groz, schoene, guot |
| **ADV** | adverb | schone, vil, sere, gar |
| **DET** | determiner | der, diu, daz, ein, diser, jener, kein |
| **POS** | possessive pronoun | min, din, unser |
| **PRO** | pronoun | ich, ez, wir, relative pronouns |
| **PRP** | preposition | uf, zuo, under, durch |
| **NEG** | negation | nie, niht, nit, ne, en |
| **NUM** | numeral | zwo, dri |
| **CNJ** | conjunction (generic) | fallback where ambiguous |
| **SCNJ** | subordinating conj. | daz (subordinate clause), ob, swenne, sit |
| **CCNJ** | coordinating conj. | und, oder, aber, ouch |
| **IPA** | interrogative particle | wie (question), war (where to?) |
| **VRB** | full verb | liuhten, varn, machen |
| **VEX** | auxiliary verb | haben/sin/werden (with past participle) |
| **VEM** | modal verb | muezen, suln, kunnen |
| **INJ** | interjection | ahi, owe |
| **DIG** | numeral (Roman) | IX, XVII, III |

### 5.1 POS migration of the legacy data

The legacy data uses an older tagset (`ART` instead of `DET`, `CNJ` instead of `CCNJ`/`SCNJ`, `GRA` merged into `ADJ`). Full mapping table and the shares remaining in the corpus: [POS-TAGSET.md §3](POS-TAGSET.md#3-legacy-tags-older-stock). The CNJ differentiation (CCNJ vs. SCNJ) needs linguistic analysis and cannot be done mechanically.

### 5.2 Compound tags

Many `<w>` elements in the legacy data carry compound tags (~35-40%) (for example `pos="VRB VEX"`, `pos="ART NUM"`) that express ambiguity. The disambiguation workflow resolves them to a single tag; only genuine morphological fusions (for example `wiltu` = wilt + du -> `VEM PRO`) keep two tags. Rules and exceptions: [POS-TAGSET.md §2](POS-TAGSET.md#2-compound-tags).

---

## 6. Inline elements

### 6.0 Optional extensions (since 2026-05-08, PD-001)

With the ARITHMETIC ingest the following TEI P5 standard elements were taken into the schema as **optional** inline elements. They are allowed for every corpus but required for none. Corpora of lyric, sermons or recipes do not have to use them. Full reasoning in [DECISIONS.md § PD-001](DECISIONS.md).

| Category | Elements | Use |
|---|---|---|
| editorial | `<unclear>`, `<add>`, `<gap>`, `<abbr>`, `<expan>`, `<am>`, `<g>` | editions with a philological apparatus; `<unclear>` used to be present in the existing data as an italics marker |
| onomastics | `<roleName>`, `<occupation>`, `<placeName>`, `<persName>` (inline), `<person>` (inline) | person and place annotations in the body |
| arithmetic domain | `<unit>` (`@type` = `measurement\|weight\|length\|volume\|distance`), `<rs>` (`@type` = `currency\|goods`), `<figure>` | units of measurement, currencies, diagrams and calculation layout |

**Extensions to existing elements:**
- `<w>` may now contain `<hi>` (initial-letter pattern such as `<hi rend="initial">A</hi>in`)
- `<lb>` may carry `@break="no"` (TEI P5 standard for a word running across a line end)
- `<note>` may carry `@place` and contain `<p>`
- `<hi>` may again contain `<hi>` (a controlled exception to ADR-013, for Carina's struck-through fractions `<hi rend="line-through"><hi rend="superscript">2</hi>/<hi rend="subscript">3</hi></hi>`)

**`<div>/@type` enum extension** (for arithmetic-book corpora): in addition to the 7 standard values, 24 further ones (`outline`, `commodity_calculation`, `reckoning_example`, `fraction_calculation`, `regula_de_tri`, `addition`, `multiplication`, `division`, `subtraction` and others). Full list in `schema/mhdbdb.rnc` § `div.type.arithmetic`.

**Follow-up tasks** (after the ingest):
- connect `<unit>` and `<rs>` to the concept system via `@ana="concepts.xml#concept_NNNN"` (a mapping task to be done together with the contributors)
- keep the reading-view render policy minimal: show `<expan>` instead of `<abbr>`; rendering fractions, figures and calculations is a follow-up worth funding

### 6.1 Punctuation

**Current** (existing data):
```xml
<seg xml:id="{SIGLE}_{page}{line}_{pos}" type="pc">,</seg>
```

**Target** (TEI P5 has a dedicated element):
```xml
<pc join="left">.</pc>
```

TEI P5 provides `<pc>` (punctuation character) as the counterpart to `<w>`. It is a member of `att.linguistic` and therefore supports `@pos`, `@lemma` and so on, unlike `<seg type="pc">`. The `@join` attribute (`left`, `right`, `both`, `no`) governs whitespace adjacency.

**Migration:** 1,370,191 occurrences. A simple batch rename (`<seg type="pc">` → `<pc join="left">`). The JS rendering has to treat `<pc>` as an inline element (as it does `<seg type="pc">`).

**Careful:** `&lt;` and `&gt;` inside `<seg type="pc">` (and inside `<pc>` in future) are correct XML entities (angle brackets in the source text), not bugs.

### 6.2 Highlighting

```xml
<hi rend="initial">
  <w xml:id="...">Wort</w>
</hi>

<hi rend="upper_case_first_letter">
  <w xml:id="...">Wort</w>
</hi>
```

`<hi rend="initial">` is a corpus convention and encodes decorated initials from manuscripts and prints.

**Audit: `hi/@rend` values (666 files):**

| Value | Count |
|------|-------|
| `initial` | 314,529 |
| `upper_case_first_letter` | 92,488 |
| `upper_case` | 7,953 |
| `bold` | 201 |
| `italic` | 124 |

**Optional improvement (DTABf model):** `@rendition` instead of `@rend`, with centralized definitions in `<tagsDecl>`:
```xml
<!-- in the header: -->
<rendition xml:id="in" scheme="css">font-size: 150%;</rendition>
<!-- in the text: -->
<hi rendition="#in"><w ...>Wort</w></hi>
```
Advantage: consistent, centrally managed rendition definitions instead of free-text values.

### 6.3 Page breaks

```xml
<pb n="{page number}"/>
<pb type="folio" n="{folio}"/>
```

### 6.4 Editorial supplements

```xml
<supplied>
  <w xml:id="...">ergaenztes Wort</w>
</supplied>
```

Only for parts of the text supplied by the editor. Do not misuse it for recipe titles or structural marking.

### 6.5 Caesura

```xml
<caesura/>
```

Marks a caesura inside a line of verse (`<l>`). Rare (5 files in the existing data).

### 6.6 Numbers

```xml
<num>
  <w xml:id="..." pos="DIG">ccccvi</w>
</num>
```

Wraps `<w>` elements with numeric content (Roman numerals and the like). Rendered as `<span class="number">`.

### 6.7 Column breaks

```xml
<cb n="{column no.}"/>
```

Marks a column break. Rare (996 occurrences in 3 files). Rendered as `[Sp. {n}]`.

### 6.8 Known errors in the existing data

- **`<suppplied>`** (typo, 1 occurrence in 1 file): has to be corrected to `<supplied>`.

---

## 7. Authority file references

All references to controlled vocabularies use relative paths:

| Reference | TEI status | Target | Example |
|----------|------------|------|----------|
| `@lemmaRef` | standard | lexicon.xml | `lexicon.xml#lemma_879` |
| `@ana` (target) | standard | lexicon.xml (sense) | `lexicon.xml#lemma_879_sense_1234` |
| ~~`@meaningRef`~~ (current) | not standard | lexicon.xml (sense) | → becomes `@ana` |
| `@corresp` (target) | standard | variants.xml (type) | `variants.xml#type_8717` |
| ~~`@wordRef`~~ (current) | not standard | lexicon.xml (synthetic) | → becomes `@corresp` |
| `@ref` (author) | standard | document-internal `<person>` in profileDesc (-> persons.xml via `@corresp`) | `#person_445` |
| `@corresp` (msIdentifier) | standard | works.xml | `works.xml#work_89` |
| `@corresp` (genre) | standard | genres.xml | `genres.xml#genre_0480b285` |

**Integrity constraint:** all referenced IDs have to exist in the authority files. Validated at build time.

---

## 8. Decided migration points

### 8.1 `<l>` vs `<lb/>` in prose: migration

TEI P5 defines `<l>` as "a single line of **verse**" and uses the redefinition of `<l>` as a "typographic line" in chapter 24 (Conformance) as an **explicit counterexample** of non-conformance.

**Decision:** 18 prose texts are migrated from `<l>` to `<lb/>`. Three texts kept their `<l>` in #32 with the reason "verse composition". That classification was wrong (a mix-up with verse works of the same name by other authors) and was revised in 2026-07 (#143, KZW decision of 2026-06-12):

**Correction 2026-07 (#143): these 3 are prose as well, `<l>` → `<lb/>` converted:**

| Sigle | Title | Finding |
|-------|-------|--------|
| HMT | Buch von Troja (Hans Mair) | prose according to geschichtsquellen.de/werk/3419; the mix-up candidate was Konrad von Würzburg's verse Trojanerkrieg (rhyme rate 1.6%) |
| APO | Apollonius (Heinrich Steinhöwel, 1461) | prose translation (Terrahe edition); the mix-up candidate was Heinrich von Neustadt's "Apollonius von Tyrland" (rhyme rate 4.5%) |
| HH | Himmel und Hölle | early MHG rhythmic prose in short cola, not verse composition (rhyme rate 1.1%) |

The #143 heuristic named 17 candidates. Two of them (APO, HMT) stand in the table above and are converted; the other 15 (ALX, DIO, FB, FP, GWTK, MR1, MR2, PSG, PTS, RUD, TKA, TKR, WH, WLE, WRB) were checked on their content (rhyme sample 18-36%, word density) and are verse composition, so `<l>` stays correct there. (This figure said 17 until 2026-08-02, that is the size of the candidate list instead of the size of the remainder; the list of sigles was always 15 long. HH did not come out of that heuristic.)

**To be migrated (`<l>` → `<lb/>`):** 18 files

| Sigle | Title | Group |
|-------|-------|--------|
| PL1 | Prosa-Lancelot | prose romance |
| PL2 | Prosa-Lancelot | prose romance |
| PL3 | Prosa-Lancelot | prose romance |
| FLG1 | Das fließende Licht der Gottheit (books 3-7) | mysticism |
| VTC | Vita Caroli Quarti Imperatoris | chronicle |
| NBU | Dat nuwe Boych | chronicle |
| PUC | Pulkava Chronik | chronicle |
| ESB | Engelthaler Schwesternbuch | chronicle |
| LUU | Lehre und Unterweisung | Bämler print 1476 |
| EHB | Ehbüchlein | Bämler print 1476 |
| EB1 | Erstes Ehbüchlein | Bämler print 1476 |
| EB2 | Zweites Ehbüchlein | Bämler print 1476 |
| MSP | Der menschen spiegel | Bämler print 1476 |
| PRJ | Processus juris | Bämler print 1476 |
| REG | Register der Augsburger Sittenlehre | Bämler print 1476 |
| ATF | Facetiae Latinae et Germanicae | other |
| SPH | Der Stein philosophorum | other |
| WGI | Der Welsche Gast (Prosavorrede) | other |

**Note:** the Bämler 1476 group (7 texts) stands out: two further texts from the same print (FAN, NST) already use `<lb/>` correctly.

**Migration:** `<l n="X">content</l>` → `<lb n="X"/>content`. JS adjustment: 2 places (`tei-text-reader.js`, `tei-manager.js`).

---

## 9. Ingest requirements

New texts have to meet the following minimum requirements:

### 9.1 Required (blocking)

- [ ] valid XML with the TEI namespace
- [ ] `<TEI @xml:id>` with a unique sigle
- [ ] `<teiHeader>` with `<titleStmt>`, `<publicationStmt>`, `<sourceDesc>` (template from sec. 2)
- [ ] `<author @ref>` points at an existing `persons.xml` entry (or a new entry is created)
- [ ] `<msIdentifier @corresp>` points at an existing `works.xml` entry (or a new entry is created)
- [ ] at least one genre via `<classDecl>/<taxonomy>`
- [ ] `<w>` elements with `@xml:id` (unique within the document)
- [ ] `<w @lemmaRef>` for every annotated word
- [ ] `@pos` with a valid tag from the 19-tag set (sec. 5)
- [ ] body structure conforming to the genre pattern (sec. 3)
- [ ] validation against `schema/mhdbdb.rnc` (once available)

### 9.2 Recommended (non-blocking)

- [ ] `@ana` for semantic search (reference to a sense in lexicon.xml)
- [ ] `<pb>` for page and folio references
- [ ] `<bibl type="digitalIntermediary">` for the provenance chain
- [ ] Handschriftencensus number in `<msIdentifier>`
- [ ] GND/Wikidata IDs for author and work

### 9.3 Validation pipeline (two stages)

```bash
# stage 1: TEI conformance (no illegal attributes/elements)
# schema/tei_all.rng sits in the repo (committed, TEI P5 4.11.0) -- no download needed
jing schema/tei_all.rng tei/{SIGLE}.tei.xml

# stage 2: MHDBDB conformance (stricter, subset of tei_all)
jing schema/mhdbdb.rnc tei/{SIGLE}.tei.xml

# 3. referential integrity (corpus -> authority): dangling @lemmaRef/@ana/@corresp/@ref/@target
python scripts/audit/check-authority-cross-refs.py --check

# 4. index rebuild
python scripts/build-corpus-index.py
python scripts/build-authority-index.py

# 5. tests
npm test
```

**Schema files:**
- `schema/mhdbdb.rnc`: source of truth (RELAX NG compact, hand-edited)
- `schema/mhdbdb.rng`: generated via `trang schema/mhdbdb.rnc schema/mhdbdb.rng` (for lxml/Python)
- `schema/tei_all.rng`: TEI P5 4.11.0 reference (gitignored, download command above)

**No ODD:** the TEI ODD toolchain (stylesheets + Roma) has 60-80 open issues, depends on XSLT 2.0 (Saxon), and the Roma web interface is unstable. TEI conformance criterion 5 ("documented via ODD or **analogous documentation**") is met by this document (TEI-MODEL.md) and the RELAX NG schema together.

---

## 10. Validation baseline

### Corpus status (667 files, as of 2026-05-11)

| Metric | Value |
|--------|------|
| files | 667 (out of 675 original files: 9 disamb files merged into base; +1 WZB ingest 2026-05-08) |
| `<w>` elements | ~9.3M |
| `<pc>` elements | ~1.4M (migrated from `<seg type="pc">`) |
| `@ana` attributes | ~5.9M (migrated from `@meaningRef`) |
| `@corresp` attributes | ~7.5M (migrated from `@wordRef`) |
| unannotated `<w>` (no `@lemmaRef`) | ~1.9M (20.4%) |

Migration scripts: run once in phases A-E, since the close of #32 they live in `scripts/_archived/` or in the git history.
Validation script: `scripts/audit/validate-corpus.py`, a two-stage RelaxNG validation (stage 1 `tei_all.rng`, stage 2 `mhdbdb.rng`/`mhdbdb-authority.rng`). The earlier structural Python check (5 checks) was retired on 2026-04-15 and is covered by `schema/mhdbdb.rnc`.

### Validation result (as of 2026-05-11)

**mhdbdb.rnc:** 667/667 files valid against the project-specific schema (`schema/mhdbdb.rnc`).

**tei_all.rng:** 637/667 files valid against TEI P5 4.11.0. 30 files carry deliberately documented deviations that our custom schema covers explicitly through GAP comments 1-11. Categories:

| Category | Files | Count |
|-----------|---------|-------:|
| `@reason` on `<w>` (compound POS split such as `wiltu = wilt + du`) | ABS, AC1, AC2, AC3, ADP, AGS, FLG | 7 |
| `<hi>` directly in block context without a wrapper | DAL, DBK, DBS, DKA, DKF, DKI, DKM, DKR | 8 |
| `<div>` in a position tei_all does not expect | DES2, DJEM, LVS, PUL, RDS, RDV, RVB | 7 |
| `<w>` directly in block context without a wrapper | DDE, FDS, KAA, PKP, PUC | 5 |
| `<p>` in an unexpected position | LZT | 1 |
| `<head>` missing or unexpected | TKR, VOR | 2 |

These 30 files are **not bugs** but documented deviations in the existing data. The MHDBDB model is deliberately more permissive than strict tei_all on these points: the GAP comments in the schema justify every deviation. (The former feature doc `032-schema-followup.md` was deleted when the issue closed; details in the git history.)

**Note on WZB (ingested 2026-05-08):** the 667th file, added with the Wenzelsbibel, conforms to both stage 1 (tei_all) and stage 2 (mhdbdb) and therefore does not fall under the baseline of 30. WZB uses none of the GAP patterns from the table above.

Earlier errors (all fixed by migration):

| Error | Fix |
|--------|----------|
| `@meaningRef` (5.9M) | → `@ana` (phase B1) |
| `@wordRef` (7.5M) | → `@corresp` (phase B2) |
| `<seg type="pc">` (1.4M) | → `<pc join="left\|right">` (phase C1) |
| `<l>` in 18 prose texts (86k) | → `<lb/>` (phase C2) |
| `<author>` after `<title>` in `<monogr>` | order corrected (phase A2) |
| `<suppplied>` typo | → `<supplied>` (phase A3) |

### TEI conformance: 5 criteria (TEI P5, chapter 24)

| # | Criterion | Status |
|---|-----------|--------|
| 1 | well-formed XML | ✓ |
| 2 | valid against the TEI schema | ✓ |
| 3 | conformant with the TEI abstract model | ✓ |
| 4 | correct TEI namespace | ✓ |
| 5 | documented via ODD or an equivalent | ✓ (TEI-MODEL.md + mhdbdb.rnc) |

**Two-stage validation:**
- **Stage 1:** `tei_all.rng` = the TEI P5 conformance test (criteria 1-4). Baseline: 637/667 green.
- **Stage 2:** `mhdbdb.rnc` = the MHDBDB stamp. It covers all patterns in the existing data, including the 30 tei_all deviations (GAPs 1-11). Baseline: 667/667 green.

`mhdbdb.rnc` is **not a strict subset** of `tei_all.rng`: it is stricter on some points (enumerated `@type` values, more restrictive child elements) and more permissive on others (the GAPs). The two stages check different properties and are complementary, not redundant.

### Authority files status (8 files, as of 2026-05-11)

| File | Entries | Validation |
|-------|----------|-------------|
| lexicon.xml | 43,879 lemmata (+4 WZB 2026-05-08, +125 #115 stubs 2026-07-02) | tei_all ✓ · mhdbdb-authority ✓ |
| variants.xml | 42,627 variant entries (256,760 forms) | tei_all ✓ · mhdbdb-authority ✓ |
| persons.xml | 211 persons | tei_all ✓ · mhdbdb-authority ✓ |
| works.xml | 584 works (+1 work_WZB) | tei_all ✓ · mhdbdb-authority ✓ |
| concepts.xml | 567 categories | tei_all ✓ · mhdbdb-authority ✓ |
| genres.xml | 615 categories | tei_all ✓ · mhdbdb-authority ✓ |
| names.xml | 90 categories | tei_all ✓ · mhdbdb-authority ✓ |
| contributors.xml | 52 persons + 2 orgs (project-internal MHDBDB team register since #83) | tei_all ✓ · mhdbdb-authority ✓ |

Migration scripts: run once in phases F-K, since the close of #32 they live in `scripts/_archived/` or in the git history.
Schema: `schema/mhdbdb-authority.rnc` (source) → `schema/mhdbdb-authority.rng` (generated)

Clean-ups carried out:
- 3,422 genre `<ref>` → 870 `<ptr/>` (deduplicated, parent refs removed)
- 368 `<note type="identifiers">` unwrapped, 176× `gnd`→`GND`
- 209 denormalized `<listBibl>` removed from persons.xml
- 4 UUID person IDs → numeric, 1 person newly created (Schweizer Anonymus)
- 225 orphaned references removed (154 variants, 61+10 lexicon)
- Frauendienst/Frauenbuch split (work_6/work_7)

### Known encoding exceptions and open data gaps (#133)

A consolidated list of all deliberately non-normalized islands of data and of the known gaps. **Maintenance rule:** every new ingest and every new deliberate exception gets an entry here with its reason and tracking issue, otherwise shadow heterogeneity grows unseen (a finding of the documentation health check of 2026-06-05).

| Exception / gap | Affected | Reason | Status / tracking |
|------------------|-----------|-------|-------------------|
| schema GAPs 1-11 (`schema/mhdbdb.rnc`) | 30 corpus files (category table above) | existing data; migration disproportionately expensive or semantically risky: documented exceptions to the data-before-schema rule | permanent; every GAP is commented in the schema |
| ARI/PD-001 domain elements | 6 ARITHMETIC manuscripts (not yet in the corpus) | 12 non-schema element classes + 24 `div/@type` + 7 `hi/@rend` values from Carina's arithmetic books; they block stage-2 validation | decided 2026-05-08: domain tags go into the schema (DECISIONS.md § PD-001); schema extension + ingest still pending → #92 |
| lexicon.xml backfill | remaining 396 dangling refs / 109 IDs (category B: sense curation, category C: typos/homographs) | the WZB forward ingest stamped lemma IDs into the corpus only; category A (125 entries) was stubbed on 2026-07-02 via `backfill-lexicon.py` | open → #115 (B/C curatorial, KZW/Julia) |
| WVV stanza anchors | WVV, 23 stanzas | unusual Linecode template, anchors missing (#23 follow-up) | **solved** 2026-07-08 (#110): the 4 open places contained 11 header-separated verse blocks, each is now an `<lg type="stanza">` of its own; WVV has 489 stanzas, token stream byte-identical |
| editorial `<div>` shell | HUG, KLA, PL1-PL3, MBS series | follow-up from the manual TEI review (#30) | open → #138 (needs-clarification) |
| prose policy `<l>` vs. `<lb/>` | 3 texts (APO, HMT, HH) | phase C2 converted 18 texts, for the remaining candidates the policy was unclear | **solved** 2026-07-03 (#143): the 3 are converted, the other candidates are verified verse composition and keep `<l>` (§8.1) |
| WZB `@meaningRef` (historical) | WZB | legacy annotation of the first delivery | **solved**: migrated to `@ana`; only a `revisionDesc` log entry remains |

---

## 11. Versioning

**Source of truth for the index versions.** All other promptotyping docs (DATA-MODEL.md, DEVELOPMENT.md, CONTRACTS.md, INDEX.md §Status, TEI-MODEL-AUTH-FILES.md) point at this table and name only generic placeholders in their code snippets (`X.Y.Z`, `"1.x.x"`). To maintain on every index bump: here, in `corpus-loader.js`, in the build script, in INDEX.md §Status (see memory `feedback_index_version_bump`).

| Artefact | Version | Date |
|----------|---------|-------|
| this document | 1.0.0 | 2026-04-10 |
| RELAX NG schema (`schema/mhdbdb.rnc`) | 1.0.0 | 2026-04-09 |
| POS tagset | 1.0 (19 tags) | 2026-03 |
| Corpus Index | 4.2.3 | 2026-08-21 |
| Authority Index | 1.9.1 | 2026-08-21 |
| authority schema (`schema/mhdbdb-authority.rnc`) | 1.1.0 | 2026-07-30 |

---

## 12. Conventions for new ingests

When new texts are ingested, the following defaults hold for editor attribution and credits. They add to the minimum requirements from §9.

**Always the same (in every new file):**

1. **Authority block** in `<publicationStmt>/<authority>`: three entries in this order (coordinator first, then the founders chronologically):
   - `<persName role="coordinator" ref="contributors.xml#contrib_003">Katharina Zeppezauer-Wachauer</persName>`
   - `<persName role="founder" ref="contributors.xml#contrib_001">Klaus M. Schmidt</persName>`
   - `<persName role="founder" ref="contributors.xml#contrib_002">Horst Pütz</persName>`
2. **Collective team attribution** in `<titleStmt>/<respStmt>`:
   - `<orgName ref="contributors.xml#mhdbdb-team">MHDBDB-Team (vollständige Liste in contributors.xml)</orgName>`

These three building blocks are identical in all 667 existing files and were set by the migration script `scripts/_archived/migrate-header-credits.py` (initially 666 files on 2026-04-15, WZB brought in line at the branch merge on 2026-05-06). For new ingests simply copy them from an existing file or from `schema/examples/corpus.example.tei.xml`.

**Do not write the full contributor list into the header.** The 50+ editors who historically worked on the existing texts live in `contributors.xml` and are covered by the collective `mhdbdb-team` reference. The header stays lean.

**Specific lead editors in a new ingest:** if a new text has one or more lead editors in today's sense (as Brom has for TKR/TKA/VTC/PUC, Woesner for JT or Hintersteiner for WZB), then:

1. create a new `<person xml:id="contrib_NNN">` with `@role="lead-editor"` in `contributors.xml` (IDs continue from the last one assigned).
2. add a second `<respStmt>` next to the collective one in the new corpus header:

   ```xml
   <respStmt>
     <resp>Hauptbearbeitung</resp>
     <name role="lead-editor" ref="contributors.xml#contrib_NNN">Vorname Nachname</name>
   </respStmt>
   ```

3. run both validation stages: `contributors.xml` against `mhdbdb-authority.rng`, the new corpus header against `mhdbdb.rng`.

**Non-lead editors (single contributions):** anyone who worked on a single text as an editor but should not be visible as "lead editor of this edition" is recorded only in `contributors.xml` as `<person role="editor">`, without needing a separate `<respStmt>` in the corpus header. Visibility through the collective `mhdbdb-team` reference is enough.

**External providers of primary texts** (Harsch/Bibliotheca Augustana, Gloning/Kochbuchkorpus, Klug/Pflanzendissertation, or institutions such as Akademie Mainz / ETC Virginia / Kompetenzzentrum Trier / TITUS Frankfurt) are **not** recorded in `contributors.xml`: they are already documented in the `<sourceDesc>/<listBibl>/<bibl type="digitalIntermediary">/<respStmt>` of the respective corpus header (see ADR-012, issues #35-#40). `contributors.xml` is deliberately limited to MHDBDB-internal participation.

---

## References

### Project-internal
- [CONTRACTS.md](CONTRACTS.md) -- cross-system contracts (position counting, normalization)
- [DATA-MODEL.md](DATA-MODEL.md) -- authority file schemas, index structure
- [ARCHITECTURE.md](ARCHITECTURE.md) -- technical components, data flow
- `.gemini/skills/pos-disambiguator/SKILL.md` -- POS tagset definition and disambiguation rules
- `schema/examples/corpus.example.tei.xml` -- maximal corpus example (validated against tei_all.rng)
- `schema/examples/authority-*.example.xml` -- authority file examples (validated against tei_all.rng + mhdbdb-authority.rnc)
- `schema/tei_all.rng` -- TEI P5 4.11.0 RELAX NG schema (committed in the repo, no download needed)

### TEI P5 specification
- [att.linguistic](https://www.tei-c.org/release/doc/tei-p5-doc/en/html/ref-att.linguistic.html) -- `@lemma`, `@lemmaRef`, `@pos`, `@msd`, `@join`
- [att.global.analytic](https://tei-c.org/release/doc/tei-p5-doc/en/html/ref-att.global.analytic.html) -- `@ana` (replaces `@meaningRef`)
- [element `<w>`](https://www.tei-c.org/release/doc/tei-p5-doc/en/html/ref-w.html) -- word element
- [element `<pc>`](https://www.tei-c.org/release/doc/tei-p5-doc/en/html/ref-pc.html) -- punctuation element (replaces `<seg type="pc">`)
- [element `<l>`](https://tei-c.org/release/doc/tei-p5-doc/en/html/ref-l.html) -- "a single line of verse" (not for prose)
- [element `<lb/>`](https://tei-c.org/release/doc/tei-p5-doc/en/html/ref-lb.html) -- "line beginning" (for line breaks)
- [chapter 24: Conformance](https://tei-c.org/release/doc/tei-p5-doc/en/html/USE.html) -- the 5 conformance criteria

### Comparable projects
- [DTABf (Deutsches Textarchiv)](https://www.deutschestextarchiv.de/doku/basisformat/) -- gold standard for historical German texts
- [MENOTA (Medieval Nordic Text Archive)](https://www.menota.org/HB3_ch11.xml) -- medieval texts with custom namespace extensions
- [ReM (Referenzkorpus Mittelhochdeutsch)](https://www.linguistics.rub.de/rem/) -- MHG corpus with the HiTS tagset
