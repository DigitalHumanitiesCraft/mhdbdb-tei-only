# TEI Authority Files: Target Model

Normative data model for the 8 authority files in `authority-files/`.
Counterpart to `docs/TEI-MODEL.md` (corpus files).

> **Audience:** This file is a technical reference specification, written primarily for development and automated tooling (precise, machine-oriented). A general introduction is offered by the help pages of the website, for example [Daten & Downloads](https://dhcraft.org/mhdbdb-tei-only/hilfe-daten.html).

**Status:** Implemented (2026-04-10, phases F-K; `contributors.xml` added 2026-04-14)
**Schema:** `schema/mhdbdb-authority.rnc` (source) → `schema/mhdbdb-authority.rng` (generated)
**Examples:** `schema/examples/authority-*.example.xml`
**Validation:** All 8 files valid against `tei_all.rng` AND `mhdbdb-authority.rnc`.

---

## 1. Overview

| File | Content | Entries | Size |
|-------|--------|-----------|---------|
| `lexicon.xml` | Lemmata with senses, POS, etymology | 43,879 | 33 MB |
| `variants.xml` | Orthographic variants per lemma | 42,627 variant entries, 256,761 forms | 16 MB |
| `persons.xml` | Authors/persons with authority data | 211 | 74 KB |
| `works.xml` | Works with bibliography and genre | 584 | 1.4 MB |
| `contributors.xml` | MHDBDB contributors (founders, coordination, editors) | 52 persons + 2 orgs | 15 KB |
| `concepts.xml` | Semantic concept ontology | 567 categories | 207 KB |
| `genres.xml` | Genre taxonomy | 615 categories | 405 KB |
| `names.xml` | Onomastic system (proper names) | 90 categories | 33 KB |

### Functional groups

| Group | Files | TEI model | Data in |
|--------|---------|------------|----------|
| Dictionary | lexicon.xml, variants.xml | TEI Ch. 9 (Dictionaries) | `<body>` |
| Persons | persons.xml | TEI Ch. 13 (Names/People) | `<body>` |
| Bibliography | works.xml | TEI Ch. 3 (Bibliography) | `<body>` |
| Contributors | contributors.xml | TEI Ch. 13 (Names/People) + Ch. 3 (Orgs) | `<body>` |
| Taxonomies | concepts.xml, genres.xml, names.xml | TEI Ch. 2.3.7 (Taxonomy) | `<encodingDesc>/<classDecl>` |

### Provenance and currency

Important for day-to-day operation (see [INDEX.md → Current Phase](INDEX.md#current-phase)): all authority files came out of **a single one-off migration** (2025-07-22) that ran in **three stages**: old MHDBDB (RDF triple store in Salzburg, SPARQL via dh.plus.ac.at) → CSV snapshots (via SPARQL queries, on branch `initial-data-wrangling` under `lists/`) → TEI-XML (via `scripts/_archived/tei-transformation.py`, commit `8513589ea`). **Since that migration this repository is the sole master for all 8 authority files. There is no re-export from Salzburg and no live external source.** The CSV exports were snapshots, not an interface: everything after them is maintained here.

"Stale" here means: derived from the corpus and not regenerated along with it once the data changes. The corpus is edited continuously (script ingest AND manual corrections), so corpus-coupled files drift. Detector: `scripts/audit/check-authority-cross-refs.py` (in CI via `data-integrity.yml`).

| File | Origin (one-off, 2025-07-22) | Current maintenance | Drift risk |
|-------|-----------|-----------|--------------|
| `variants.xml` | corpus-extracted (`initial-data-wrangling`) | **corpus-derived**, regenerable via `scripts/sync/extract-variants.py` (#44/#115) | high: every new or changed form has to be carried over. Regeneration is lossless and automatable |
| `lexicon.xml` | RDF→CSV snapshot (`lists/lexicon.csv`) → `tei-transformation.py::create_lexicon_tei` | **repo = master AND corpus index** (the corpus leads, lexicon follows) | medium: lemma/sense IDs created by ingest need a repo-internal backfill (category A stubbed 2026-07-02; the remaining 396 refs / 109 IDs are curatorial, #115). No Salzburg re-export possible (the CSV was itself only a snapshot) |
| `persons.xml` | RDF→CSV→TEI snapshot | maintained by hand in-repo, **no re-export** | low (0 unresolved) |
| `works.xml` | RDF snapshot + Zotero enrichment | `enhance_works_with_zotero.py` + manual, in-repo | low (0 unresolved) |
| `concepts.xml` | RDF→CSV→TEI snapshot (concept system) | maintained by hand in-repo, **no re-export** | low (0 unresolved) |
| `genres.xml` | RDF→CSV→TEI snapshot | maintained by hand in-repo, **no re-export** | low (0 unresolved) |
| `names.xml` | RDF→CSV→TEI snapshot | maintained by hand in-repo, decoupled from the corpus | low (0 corpus coupling) |
| `contributors.xml` | born-digital (2026-04) | **maintained by hand** (no generator) | none |

**Overall pattern:** all files are RDF-derived migration snapshots (2025-07-22), maintained **in-repo** since the migration: there is no external master left and no re-export source. Only `variants.xml` is corpus-derived and regenerable. `lexicon.xml` is repo master AND index of the corpus annotation: if a corpus `<w>` carries a `@lemmaRef`/`@ana` that is missing from lexicon.xml, the corpus leads and lexicon.xml has to be brought in line (see [CONTRACTS.md → Authority Source Rules](CONTRACTS.md#f-authority-source-rules)). New **sense meanings** are curatorial (the team assigns the concept), not automatically reconstructible from the corpus. `lexicon.xml` and `variants.xml` were stale until 2026-05; `variants.xml` has been regenerated (most recently 256,761 forms, 2026-08-31 with #382), `lexicon.xml` still has 396 ingest-caused dangling refs after the category A stub backfill (2026-07-02) (109 IDs, curatorial remainder B/C open, #115; cause in §6.1). The `_archived` generators write pre-#32 attributes (`@wordRef`/`@meaningRef`) on the corpus side and must never be run against the current corpus unchecked.

---

## 2. Ground rules (valid for all 8 files)

### 2.1 Where the data sits

| File | Data in | Model |
|-------|----------|--------|
| lexicon.xml | `<body>` | TEI Ch. 9 Dictionaries |
| variants.xml | `<body>` | TEI Ch. 9 Dictionaries |
| persons.xml | `<body>` | TEI Ch. 13 Names/People |
| works.xml | `<body>` | TEI Ch. 3 Bibliography |
| concepts.xml | `<encodingDesc>/<classDecl>` | TEI Ch. 2.3.7 Taxonomy |
| genres.xml | `<encodingDesc>/<classDecl>` | TEI Ch. 2.3.7 Taxonomy |
| names.xml | `<encodingDesc>/<classDecl>` | TEI Ch. 2.3.7 Taxonomy |

**Taxonomies stay in `<encodingDesc>`.** TEI allows `<taxonomy>` ONLY in `<encodingDesc>/<classDecl>`, not in `<body>` (tested against tei_all.rng). That is the placement TEI foresees for classification systems. The `<body>` holds a placeholder `<p>`.

### 2.2 Cross-referencing

**Target:** one mechanism per semantics, consistent across all files.

| Semantics | Attribute/element | When to use |
|----------|-----------------|----------------|
| Canonical definition | `@ref` | element POINTS TO its definition: `<author ref="persons.xml#person_1">` |
| Correspondence | `@corresp` | element CORRESPONDS TO another one: `<entry corresp="lexicon.xml#lemma_1">` |
| Pointer (no label) | `<ptr target="..."/>` | reference without visible text: `<ptr target="concepts.xml#concept_N"/>` |

**FORBIDDEN:**
- `<ref target="...">label text</ref>` for cross-file references: that is denormalization. The label text belongs in the target file.
- Bidirectional links (the same information in 2 places): one direction is master, the other one is derived.

### 2.3 Identifiers

**Format:** `{prefix}_{id}`

| File | Prefix | ID format | Example |
|-------|--------|-----------|----------|
| lexicon.xml | `lemma` | numeric | `lemma_879` |
| lexicon.xml | `lemma_N_sense` | numeric | `lemma_879_sense_1449` |
| variants.xml | `type` | numeric | `type_2783` |
| persons.xml | `person` | numeric | `person_1` |
| works.xml | `work` | numeric | `work_89` |
| contributors.xml | `contrib` | 3 digits, zero-padded | `contrib_001` |
| concepts.xml | `concept` | 8 digits, hierarchical | `concept_11200000` |
| genres.xml | `genre` | UUID hash | `genre_2c9f837c` |
| names.xml | `name` | 8 digits, hierarchical | `name_41232000` |

**Note:** the genre UUIDs stay (renaming 615 IDs plus 3422 references would be out of proportion). Concepts and names use hierarchical 8-digit IDs, which is a sensible scheme for taxonomies.

**Migration:** 4 persons in UUID format were migrated to `person_N` (2026-04-10). 1 person was newly created: `person_anonym` (generic collective author for anonymous works, Wikidata Q4233718; no GND). Separate from it, `person_1772` exists (Schweizer Anonymus, GND 103130276).

### 2.4 External identifiers (authority data)

**Target:** one spelling across all files.

| Authority file | `@type` value | Example |
|-----------|-------------|---------|
| GND | `GND` (Uppercase) | `<idno type="GND">118565133</idno>` |
| Wikidata | `wikidata` | `<idno type="wikidata">Q77480</idno>` |
| Handschriftencensus | `handschriftencensus` | `<idno type="handschriftencensus">217</idno>` |

All files use `GND` (uppercase, the official acronym of the Deutsche Nationalbibliothek). Migrated 2026-04-10.

### 2.5 Shared teiHeader

All 8 files carry the same minimal header:

```xml
<teiHeader>
  <fileDesc>
    <titleStmt>
      <title>MHDBDB {filename}</title>
    </titleStmt>
    <publicationStmt>
      <publisher>Mittelhochdeutsche Begriffsdatenbank (MHDBDB)</publisher>
      <date>{date}</date>
    </publicationStmt>
    <sourceDesc>
      <p>{provenance description}</p>
    </sourceDesc>
  </fileDesc>
</teiHeader>
```

Taxonomy files (concepts, genres, names) additionally carry `<encodingDesc>/<classDecl>/<taxonomy>`: that is where the taxonomy data lives (TEI allows `<taxonomy>` only there).

---

## 3. File-specific models

### 3.1 lexicon.xml: dictionary

TEI Ch. 9 (Dictionaries). Contains all lemmata of the MHDBDB lexicon.

```xml
<body>
  <div type="lexicon">
    <entry xml:id="lemma_879">
      <form type="lemma"><orth>brôt</orth></form>
      <gramGrp><pos>NOM</pos></gramGrp>
      <etym type="morphological">
        <seg type="component" corresp="lexicon.xml#lemma_X">component</seg>
      </etym>
      <sense xml:id="lemma_879_sense_1449" ana="#type_2783 #type_2784 #type_2785">
        <ptr target="concepts.xml#concept_21111300"/>
      </sense>
    </entry>
  </div>
</body>
```

**Elements:**

| Element | Required | Attributes | Content |
|---------|---------|-----------|--------|
| `<entry>` | yes | `@xml:id` (lemma_N) | form + gramGrp + etym? + sense+ |
| `<form type="lemma">` | yes | `@type="lemma"` | `<orth>` |
| `<gramGrp>` | yes | – | `<pos>` (1+, some lemmata carry several POS) |
| `<etym type="morphological">` | optional | `@type="morphological"` | `<seg type="component">` |
| `<etym type="borrowing">` | optional | `@type="borrowing"` | `<lang>`+ , `<note type="attribution">`? |
| `<sense>` | yes (1+) | `@xml:id`, `@ana`? | `<def>`? , `<note type="comment">`? , `<ptr target="concepts.xml#..."/>`* |

**`@ana` on `<sense>`:** space-separated `#type_N` values (references into variants.xml). 30% of the senses have no `@ana`, which is acceptable (not every sense has attestations with word forms).

**Referential integrity:** all concept references valid (19 orphaned references cleaned up 2026-04-10).

#### Curated statements (since 2026-07-30)

The RDF migration brought classification only (POS, concept pointers, compound components), no prose. For knowledge curated by hand there are three optional productions. All of them are additive: the 43,879 migrated entries stay valid unchanged.

```xml
<entry xml:id="lemma_37818">
  <form type="lemma"><orth>Abba</orth></form>
  <gramGrp><pos>NOM</pos></gramGrp>
  <etym type="borrowing">
    <lang norm="arc">Aramäisch</lang>
    <lang norm="la">Lateinisch</lang>
    <note type="attribution" resp="contributors.xml#contrib_003">Quellsprache ist das Aramäische; vermittelt hat die lateinische Bibel …</note>
  </etym>
  <sense xml:id="lemma_37818_sense_59052" ana="#type_198634">
    <def xml:lang="de" resp="contributors.xml#contrib_003">Aramäische Anrede Gottes: „mein Vater“ …</def>
    <note type="comment" xml:lang="de" resp="contributors.xml#contrib_003">Im Korpus nur in ZUK 2377 …</note>
    <ptr target="concepts.xml#concept_23123905"/>
  </sense>
</entry>
```

| Element | Carries | Rule |
|---------|-------|-------|
| `<etym type="borrowing">` | source languages (`<lang>` with `@norm` = BCP-47) plus the source of the attribution | layer B of the foreign-language phase plan (#28). 1+ `<lang>`, because multiple origins are normal (`mirre`: ar + he + arc). **No** verdict on the degree of integration (KZW decision 3 of 2026-07-29). Strictly separate from `@xml:lang` on the corpus `<w>` (layer A = code-switching in the text). |
| `<def>` inside `<sense>` | the meaning stated in prose | the concept system classifies, it does not formulate. Dictionary content, not argument. |
| `<note type="comment">` inside `<sense>` | philological comment (attestation context, related passages) | deliberately separate from `<def>`: the reasoning goes here, the meaning there. |

**`@resp`** points at `contributors.xml#contrib_N` and is required on both `<note>` types: a comment without an author is not citable. On `<def>` it is optional (a meaning statement can be editorial consensus). The value is typed as a pattern (`contrib_` plus three digits), so that a typo in the form already shows up in stage-2 validation. That the ID also **exists** is checked only by `scripts/audit/audit-authority-files.py`, and that does not run in CI: a well-formed but unbacked `contrib_N` validates green. So run the audit by hand after every round of curation. Attributability currently stops at the data layer: `contributors.xml` is not part of the authority index, so the interfaces cannot resolve `contrib_003` to a name and show the prose without an attribution. That is a decision with a trigger, not an oversight, and the reason is not the size of a contributor map (764 bytes gzipped, measured): at one curated lemma the display question cannot be answered, and #28 layer B will ask a second one that `@resp` does not answer. See [DECISIONS.md ADR-018](DECISIONS.md#adr-018-attribution-of-curated-lemma-statements-stops-at-the-data-layer-for-now), which fires as soon as more than 25 lemmata are curated.

**Language concepts vs. `<etym type="borrowing">`:** the concept subtree `concept_23123000` (individual languages) is already used as an origin marker in the existing data (`mirre` carries Arabic, Hebrew, Aramaic; `Golgota` and `Barjona` Aramaic). Both stay side by side: the concept pointers make the origin searchable and analysable inside the concept system, `<etym type="borrowing">` makes it explicit together with its source.

**Rule: the two layers have to be congruent.** Whoever assigns a new origin sets both for every language, the `<lang>` entry and the concept pointer. Otherwise a consumer gets different sets depending on the access path: `lemma.origin.languages` from the index against the concept subtree from the same file. Transmitting languages count as an origin layer too and appear in both (`Abba`: `arc` as source language, `la` as transmission via the Vulgate). Which of the languages is source and which is transmission is stated by the `<note type="attribution">` in prose; for a machine the list is unordered.

**Order (RELAX NG, sequence without interleave):** inside `<entry>`, `<etym type="morphological">` comes before `<etym type="borrowing">`; inside `<sense>`, `<def>` comes before `<note type="comment">` before the `<ptr>` elements. Appending generation (`SubElement`, as in `scripts/ingest/wzb/wzb-add-lemma.py`) gets this right by itself; inserting by hand otherwise yields a stage-2 error whose message does not name the cause.

**Index mapping:** `lemma.origin = {languages[{name, code}], attribution?, resp?}` plus `sense.definition` / `sense.comment` (and `definitionResp` / `commentResp`), each only where present in the lexicon: 43,879 lemmata with empty fields would inflate index and API for no gain. Authority index from v1.7.0 on.

**Current state:** 1 entry (`lemma_37818` Abba, 2026-07-30). The rest follows via #28 phase 2/3.

### 3.2 variants.xml: orthographic variants

TEI Ch. 9 (Dictionaries). Each entry corresponds to one lemma and lists all attested spellings.

```xml
<body>
  <div type="orthographicVariants">
    <entry corresp="lexicon.xml#lemma_879">
      <form xml:id="type_2783">brôt</form>
      <form xml:id="type_2784">brôte</form>
      <form xml:id="type_2785">brôtes</form>
    </entry>
  </div>
</body>
```

**Design decision:** variants in a separate file instead of in lexicon.xml (256k forms would inflate the 33 MB lexicon past 60 MB). Linked via `@corresp`.

**Referential integrity:** all lemma references valid (154 orphaned entries cleaned up 2026-04-10).

### 3.3 persons.xml: register of persons

TEI Ch. 13 (Names, Dates, People, Places).

```xml
<body>
  <listPerson>
    <person xml:id="person_1">
      <persName type="preferred">Konrad von Würzburg</persName>
      <idno type="GND">118565133</idno>
      <idno type="wikidata">Q77480</idno>
    </person>
    <person xml:id="person_1768">
      <persName type="preferred">Karl IV.</persName>
      <persName type="alternative" xml:lang="en">Charles IV</persName>
      <idno type="GND">118560085</idno>
      <idno type="wikidata">Q155669</idno>
    </person>
  </listPerson>
</body>
```

**Target changes against the current state:**

| Current | Target | Reason |
|-----|------|-------------|
| `<listBibl><bibl corresp="works.xml#..."/>` | removed | redundant: works.xml carries `<author ref="persons.xml#...">`. The build script derives it. |
| 4x `person_UUID` | `person_N` | consistency with the remaining 206 entries |
| `<idno type="GND">` | `<idno type="GND">` | already correct (uppercase) |

**No persons→works link:** works.xml is master for the author-work relation. The build script (`build-authority-index.py`) derives `person.works` from works.xml.

### 3.4 works.xml: register of works

TEI Ch. 3 (Core Tags for Headers / Bibliography).

```xml
<body>
  <listBibl>
    <bibl xml:id="work_350">
      <title xml:lang="de">Aalener Stadtratsgedicht</title>
      <idno type="sigle">ASG</idno>
      <ptr target="genres.xml#genre_2c9f837c"/>
      <author ref="persons.xml#person_786">Heinrich von Rang</author>
      <relatedItem>
        <biblStruct type="journalArticle" xml:id="ASG_ASG"
                    corresp="http://zotero.org/..." key="ASG">
          <analytic>
            <author><name>Heinrich von Rang</name></author>
            <title level="a">Das Stadtratsgedicht</title>
          </analytic>
          <monogr>
            <title level="j">Aalener Jahrbuch</title>
            <idno type="callNumber">ASG</idno>
            <imprint>
              <biblScope unit="page">45-74</biblScope>
              <date>1978</date>
            </imprint>
          </monogr>
        </biblStruct>
      </relatedItem>
    </bibl>
  </listBibl>
</body>
```

**Target changes against the current state:**

| Current | Target | Reason |
|-----|------|-------------|
| `<biblStruct>` directly inside `<bibl>` | `<biblStruct>` inside `<relatedItem>` | TEI: biblStruct not allowed as a child of bibl |
| `<ref target="genres.xml#...">label</ref>` | `<ptr target="genres.xml#..."/>` | the label is denormalized; the genre name belongs in genres.xml |
| `<idno type="gnd">` | `<idno type="GND">` | one capitalization |
| external IDs in `<note type="identifiers">` | external IDs as plain `<idno>` | possible because `<ref>` → `<ptr>` (tested: valid) |
| genre parent refs `<ref type="parent">` | removed | the hierarchy belongs in genres.xml, not in works.xml |
| `<monogr>`: editor before idno | idno before editor | TEI content model |

**Genre references, current vs. target:**

Current (denormalized, 4 elements per genre):
```xml
<ref target="genres.xml#genre_2c9f837c" xml:lang="de" n="prefLabel">Kleindidaxe</ref>
<ref target="genres.xml#genre_2c9f837c" xml:lang="en" n="prefLabel">Didactic Short Poetry</ref>
<ref target="genres.xml#genre_d75ff6ba" xml:lang="de" type="parent" n="prefLabel">Lehrdichtung</ref>
<ref target="genres.xml#genre_d75ff6ba" xml:lang="en" type="parent" n="prefLabel">Didactic Poetry</ref>
```

Target (normalized, 1 element):
```xml
<ptr target="genres.xml#genre_2c9f837c"/>
```

Label and parent hierarchy are resolved from genres.xml at runtime. The build script already does this.

**Author name in `<author>`:** the text content (`Heinrich von Rang`) stays, because TEI expects readable text in `<author>`. The source of truth for the author name is `persons.xml`; the text in `<author>` is a convenience for human readers. This is not denormalization in the same sense as the genre labels, because `<author>` without text would be semantically incomplete.

### 3.5 concepts.xml: concept ontology

TEI Ch. 2.3.7 (The Classification Declaration / Taxonomy). Data in `<encodingDesc>/<classDecl>` (TEI allows `<taxonomy>` only there).

```xml
<encodingDesc>
  <classDecl>
    <taxonomy xml:id="mhdbdb-concepts">
      <desc>Semantische Begriffsontologie der MHDBDB</desc>
      <category xml:id="concept_11200000">
        <catDesc>
          <term xml:lang="de">Wetter/Winde</term>
          <term xml:lang="en">Weather/Winds</term>
          <ptr type="broader" target="#concept_11000000"/>
        </catDesc>
      </category>
      <category xml:id="concept_13023100">
        <catDesc>
          <term xml:lang="de">Obst</term>
          <term xml:lang="de" type="alternative">Früchte</term>
          <term xml:lang="en">Fruits</term>
          <ptr type="broader" target="#concept_13023000"/>
        </catDesc>
      </category>
    </taxonomy>
  </classDecl>
</encodingDesc>
...
<body>
  <p>Taxonomy data in encodingDesc/classDecl.</p>
</body>
```

**`<term type="alternative">`**: optional synonyms alongside the primary term. Several `type="alternative"` entries per language are allowed; 263 of 567 concepts currently have at least one German synonym, 266 an English one. The build script (`scripts/build-authority-index.py:parse_concepts()`) separates primary (`termDE`/`termEN`) from alternative (`altDE[]`/`altEN[]`), see DATA-MODEL.md §Concepts. **Quirk:** some entries use slash-separated strings inside a single `<term type="alternative">` (for example `Abendessen/Nachtmahl/Festmahl`); the editorial follow-up that splits them into separate `<term>` elements is still open.

### 3.6 genres.xml: genre taxonomy

Same model as concepts.xml.

```xml
<taxonomy xml:id="mhdbdb-genres">
  <desc>Gattungstaxonomie der MHDBDB</desc>
  <category xml:id="genre_2c9f837c">
    <catDesc>
      <term xml:lang="de">Kleindidaxe</term>
      <term xml:lang="en">Didactic Short Poetry</term>
      <ptr type="broader" target="#genre_d75ff6ba"/>
    </catDesc>
  </category>
</taxonomy>
```

### 3.7 names.xml: onomastic system

Same model as concepts.xml, with additional concept references.

```xml
<taxonomy xml:id="mhdbdb-names">
  <desc>Onomastisches System der MHDBDB</desc>
  <category xml:id="name_41232000">
    <catDesc>
      <term xml:lang="de">Städtenamen (Urbanonyme)</term>
      <term xml:lang="en">City names (Urbanonyms)</term>
      <ptr type="broader" target="#name_41230000"/>
      <ptr type="exactMatch" target="concepts.xml#concept_24212000"/>
    </catDesc>
  </category>
</taxonomy>
```

### 3.8 contributors.xml: register of contributors

TEI Ch. 13 (Names/People) + Ch. 3 (Organizations). Central register of all persons and organizations that have worked on the MHDBDB project. It serves as the authority source for editor attribution in the corpus headers (via `@ref` from `<titleStmt>/<respStmt>` and `<publicationStmt>/<authority>`).

**Roles on `<person>/@role`:** `founder` | `coordinator` | `lead-editor` | `editor`. Enforced by the authority schema (`schema/mhdbdb-authority.rnc`). `<org>` entries carry no `@role`.

**ID convention:** `contrib_NNN` (zero-padded, 3 digits). Slots 001–006 are fixed (founders, coordinator, lead editors), 007+ follow the chronological list of contributors.

```xml
<text>
  <body>
    <listOrg>
      <org xml:id="mhdbdb-team">
        <orgName xml:lang="de">MHDBDB-Team</orgName>
        <desc xml:lang="de">Alle Mitwirkenden der MHDBDB — Verweis-Anker für kollektive Team-Attribution.</desc>
      </org>
      <org xml:id="dhcraft">
        <orgName xml:lang="de">Digital Humanities Craft</orgName>
        <desc xml:lang="de">Digital-Humanities-Dienstleister, technische Umsetzung.</desc>
        <idno type="URL">https://dhcraft.org</idno>
      </org>
    </listOrg>
    <listPerson>
      <person xml:id="contrib_001" role="founder">
        <persName xml:lang="de">Klaus M. Schmidt</persName>
      </person>
      <person xml:id="contrib_003" role="coordinator">
        <persName xml:lang="de">Katharina Zeppezauer-Wachauer</persName>
      </person>
      <person xml:id="contrib_004" role="lead-editor">
        <persName xml:lang="de">Vlastimil Brom</persName>
        <note xml:lang="de">Haupteditor für TKR, TKA, VTC, PUC.</note>
      </person>
      <!-- further contrib_NNN ... -->
    </listPerson>
  </body>
</text>
```

**How the corpus uses this register:**

- `<titleStmt>/<respStmt>` in every corpus header points via `<orgName ref="contributors.xml#mhdbdb-team">` at the collective team attribution, so the header is not inflated by 50+ names.
- `<publicationStmt>/<authority>` carries three `<persName ref="contributors.xml#contrib_00X">` for the founders plus the coordinator (always the same, in every file).
- For prominent lead editors (currently TKR/TKA/VTC/PUC/JT) a second `<respStmt>` with `<name role="lead-editor" ref="contributors.xml#contrib_00X">` is added.

**Name structure, a deliberate asymmetry:**

In `contributors.xml` itself the names are stored as plain text in `<persName>`:

```xml
<person xml:id="contrib_001" role="founder">
  <persName xml:lang="de">Klaus M. Schmidt</persName>
</person>
```

In the corpus headers, by contrast, the same three fixed-slot persons (Schmidt, Pütz, Zeppezauer-Wachauer) are written out **structured** as `<forename>` + `<surname>`:

```xml
<persName role="founder" ref="contributors.xml#contrib_001">
  <forename>Klaus M.</forename>
  <surname>Schmidt</surname>
</persName>
```

This is deliberate: `contributors.xml` is the canonical semantic source (with `@xml:id` as identity), the header entry is a serialized rendering that the `scripts/_archived/migrate-header-credits.py` migration produced on 2026-04-15 from a hardcoded `CANONICAL_AUTHORITY` constant. The constant sits in the script file and was the simplest means of expression, because the split "forename | surname" was known and stable for three persons. The remaining editors have no header entry, only the collective `mhdbdb-team` reference.

**For future tools** that read contributors.xml and need structured names (for example a reader-view integration showing lead editors): the plain-text form has to be split on whitespace (last token = surname), with special handling for prefixes such as "van", "von" and so on. The fixed-slot entries in the script constant are not a reliable source for non-fixed contrib_NNN IDs.

For details see [`TEI-MODEL.md`](TEI-MODEL.md) §2.1bis.

---

## 4. Reference graphs

### 4.1 Who points at whom? (authority-internal only)

```
lexicon.xml ──ptr──> concepts.xml
     ^                    ^
     │corresp             │exactMatch/closeMatch
variants.xml        names.xml

works.xml ──author @ref──> persons.xml
     │
     └──ptr──> genres.xml
```

**No back references:** persons.xml does NOT point at works.xml. The build script derives the reverse direction.

**Corpus → authority** (not shown): the 667 TEI files point via `@lemmaRef` at lexicon.xml, `@ana` at lexicon.xml (senses), `@corresp` at variants.xml, `@ref` at persons.xml and works.xml. These references are documented in the corpus model (`docs/TEI-MODEL.md`).

### 4.2 Reference types

| From | To | Element/attribute | Cardinality |
|-----|------|-----------------|---------------|
| lexicon → concepts | `<ptr target="concepts.xml#..."/>` | a sense has 0-N concept pointers |
| lexicon → lexicon | `<seg corresp="lexicon.xml#...">` | etymology components |
| variants → lexicon | `@corresp="lexicon.xml#..."` | 1:1 (one entry per lemma) |
| works → persons | `<author ref="persons.xml#...">` | 1:N (4 works have 2 authors) |
| works → genres | `<ptr target="genres.xml#..."/>` | 1:N (one work, several genres) |
| names → concepts | `<ptr type="exactMatch\|closeMatch" target="concepts.xml#..."/>` | 0-N |
| taxonomy-internal | `<ptr type="broader" target="#..."/>` | 0-N (polyhierarchy) |

---

## 5. Data quality: known problems

| Problem | File | Status |
|---------|-------|--------|
| orphaned lemma references | variants.xml → lexicon.xml | cleaned up (154 removed, 2026-04-10) |
| orphaned concept references | lexicon.xml → concepts.xml | cleaned up (19 removed, 2026-04-10) |
| orphaned person reference | works.xml → persons.xml | solved: `person_anonym` created (collective author for anonymous works, Wikidata Q4233718) |
| work without bibliography | works.xml (work_6) | solved: Frauendienst/Frauenbuch split (work_6/work_7) |
| 30% of the senses without @ana | lexicon.xml | acceptable (no attestations with word forms) |

---

## 6. Migration (completed 2026-04-10)

All migration steps were implemented in phases F-K. After #32 was closed, the scripts moved to `scripts/_archived/` or into the git history.

### Changes carried out

| Step | Script | Result |
|---------|--------|----------|
| strip labels from genre refs | `normalize-work-genres.py` | 3,422 `<ref>` → 870 `<ptr/>` (deduplicated, parent refs removed) |
| unwrap external IDs | `unwrap-work-identifiers.py` | 368 `<note type="identifiers">` resolved, 176x `gnd`→`GND` |
| remove works links | `remove-person-works-links.py` | 209 `<listBibl>` removed from persons.xml |
| migrate UUID IDs | `migrate-person-uuids.py` | 4 UUID→numeric, cascade into works.xml + tei/LUU.tei.xml |
| Schweizer Anonymus | `migrate-person-uuids.py` | `person_1772` (Schweizer Anonymus, GND 103130276) |
| Frauendienst split | `split-frauendienst.py` | work_6 (Frauendienst) / work_7 (Frauenbuch) separated |
| orphaned references | `fix-orphan-refs.py` | 154 variants + 61+10 lexicon orphans removed |

### Script adjustments

| Script | Change |
|--------|-----------|
| `build-authority-index.py` | genre text resolved from genres.xml; person→works derived from works.xml; GND casing. For versioning see [TEI-MODEL.md §11](TEI-MODEL.md#11-versioning). |
| `enhance_works_with_zotero.py` | wrap `<biblStruct>` in `<relatedItem>`; 4 bugs fixed |

### 6.1 Post-migration ingest drift (WZB) and the backfill gap

Active ingest began after the #32 migration. The Wenzelsbibel pipeline (WZB, 2026-04 to 2026-05) exposed the drift pattern that #115 uncovered:

- **Phase 1b** (commit `5cdc98831`, 2026-04) recognized new word forms and assigned new lemma IDs ≥78000. Only 4 of them made it into `lexicon.xml` (senseless at first). In total **98 lemma IDs ≥78000** are missing from `lexicon.xml` today (#115): `wzb-apply-lemmarefs.py` wrote them into the corpus as `@lemmaRef`, but **no script carried `lexicon.xml` along**.
- **Phase 3** (sense resolution) mostly picked existing senses (<78000); the missing sense IDs ≥78000 are largely structural artefacts of the lemma creation, not new meanings.
- **Emergency repair** (commits `8caa09627`/`649c0fe55`, 2026-05): the 4 senseless lemmata each got a `<sense>` by hand; `scripts/audit/check-lexicon-senses.py` was written as regression protection.

**Lesson** (→ [ADR-015](DECISIONS.md#adr-015-authority-source-model-the-corpus-leads-ingest-needs-a-backward-sync), [CONTRACTS.md → F.3](CONTRACTS.md#f3-ingest-requires-backward-sync)): a forward-only ingest pipeline without a `*-backfill-lexicon.py` inevitably produces dangling refs. Result: 977 unresolved refs (349 IDs); the automatable lemma stubs (category A) were closed on 2026-07-02 via `scripts/sync/backfill-lexicon.py`, the curatorial remainder (396 refs / 109 IDs) is open. Detector: `scripts/audit/check-authority-cross-refs.py --check` (CI gate in `data-integrity.yml`).

---

## 7. Validation

Two-stage validation, in analogy to the corpus files:

| Stage | Schema | Checks |
|-------|--------|--------|
| 1 | `tei_all.rng` | TEI P5 conformance |
| 2 | `mhdbdb-authority.rnc` | MHDBDB-specific constraints (required attributes, allowed values, reference patterns) |

---

## 8. References

- TEI P5 Ch. 2.3.7: [The Classification Declaration](https://tei-c.org/release/doc/tei-p5-doc/en/html/HD.html#HD55)
- TEI P5 Ch. 3.12: [Bibliographic Citations](https://tei-c.org/release/doc/tei-p5-doc/en/html/CO.html#COBI)
- TEI P5 Ch. 9: [Dictionaries](https://tei-c.org/release/doc/tei-p5-doc/en/html/DI.html)
- TEI P5 Ch. 13: [Names, Dates, People, Places](https://tei-c.org/release/doc/tei-p5-doc/en/html/ND.html)
- TEI att.canonical: [`@ref`](https://tei-c.org/release/doc/tei-p5-doc/en/html/ref-att.canonical.html)
- TEI att.global.linking: [`@corresp`](https://tei-c.org/release/doc/tei-p5-doc/en/html/ref-att.global.linking.html)
