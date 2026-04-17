# MHDBDB Data Contribution Guide

How to prepare and submit a Middle High German text for inclusion in the MHDBDB TEI corpus.

**Dependencies**: This guide assumes a finalised TEI schema (#32) and is illustrated with the Wenzelsbibel ingestion pilot (#34).

---

## 1. Introduction

### What is MHDBDB?

The Mittelhochdeutsche Begriffsdatenbank (MHDBDB ) is a corpus of Middle High German texts with word-level semantic annotations, maintained at the University of Salzburg. The repository holds ~670 TEI files with lemmatisation, part-of-speech tagging, and links to controlled authority vocabularies (persons, works, lemmata, concepts, genres, names).

### Benefits of Inclusion

- Your text becomes searchable across the full corpus (lemma, concept, genre, person queries)
- Automatic integration with MHDBDB authority files (Wikidata/GND person IDs, genre ontology)
- Long-term preservation under CC BY-NC-SA 3.0 AT

### Eligibility Criteria

- Middle High German text (approx. 1050–1350 CE) or closely related dialect/period
- A citable edition exists as the text basis
- Rights to publish under CC BY-NC-SA 3.0 AT are cleared
- At minimum: plain text with sentence/word segmentation; TEI P5 XML preferred

---

## 2. Prerequisites

### Required Formats

TEI P5 XML is strongly preferred. Plain text or other formats require a conversion step before the annotation pipeline can be applied.

### Minimum Encoding Standards Before Submission

| Element | Minimum | Preferred |
|---------|---------|-----------|
| File encoding | UTF-8 | UTF-8 |
| Word segmentation | `<w>` elements with `@xml:id` | + `@norm` (normalised spelling) |
| Punctuation | `<pc join="left|right">` | + `@xml:id` |
| Structure | `<body>` with `<div>` and `<p>` or `<l>` | + chapter/book divs typed |
| Header | `<teiHeader>` with `<fileDesc>` | Full header per §3 below |

### Required Authority File Entries

Before submitting a TEI file, the following must exist (or be created as part of your PR):

1. **Work entry** in `authority-files/works.xml` — sigle, titles, genre reference, author reference
2. **Author entry** in `authority-files/persons.xml` — or use the existing `person_anonym` if anonymous
3. **Genre entry** in `authority-files/genres.xml` — if no suitable genre exists, propose one

### xml:id Naming Convention

Every `<w>` and `<pc>` element needs a unique `@xml:id`. The convention is:

```
{SIGLE}_{folio/page}_{line}_{position}
```

Example: `WZB_1ra_6_5` = Wenzelsbibel, folio 1 recto, column a, line 6, word position 5.

For printed editions without folio notation, use page and line numbers: `ABG_400002_6`.

---

## 3. TEI Model Overview

### 3.1 Header Structure

The schema (`schema/mhdbdb.rng`) requires the following header structure:

```xml
<teiHeader>
  <fileDesc>
    <titleStmt>
      <title xml:lang="de">...</title>
      <title xml:lang="en">...</title>
      <author ref="persons.xml#person_ID">Name</author>
    </titleStmt>
    <publicationStmt>
      <publisher>...</publisher>
      <availability>
        <licence target="https://creativecommons.org/licenses/by-nc-sa/3.0/at/">
          CC BY-NC-SA 3.0 AT
        </licence>
      </availability>
      <date when="YYYY">YYYY</date>
    </publicationStmt>
    <sourceDesc>
      <msDesc>
        <msIdentifier corresp="works.xml#work_ID">
          <idno type="sigle">SIGLE</idno>
          <msName xml:lang="de">...</msName>
          <!-- manuscript or edition details -->
        </msIdentifier>
      </msDesc>
    </sourceDesc>
  </fileDesc>

  <encodingDesc>
    <projectDesc>
      <p xml:lang="de">...</p>
      <p xml:lang="en">...</p>
    </projectDesc>
    <editorialDecl>
      <p>...</p>
    </editorialDecl>
    <classDecl>
      <taxonomy xml:id="genres">
        <bibl>Genreklassifikation gemäß der Textreihentypologie
          <ptr target="https://www.mhdbdb.sbg.ac.at/textreihen"/>
        </bibl>
        <category xml:id="genre_PARENTID" ana="parent" corresp="genres.xml#genre_PARENTID">
          <gloss xml:lang="de">...</gloss>
          <gloss xml:lang="en">...</gloss>
        </category>
        <category xml:id="genre_SPECIFICID" corresp="genres.xml#genre_SPECIFICID">
          <gloss xml:lang="de">...</gloss>
          <gloss xml:lang="en">...</gloss>
        </category>
      </taxonomy>
    </classDecl>
  </encodingDesc>

  <profileDesc>
    <langUsage>
      <language ident="gmh">Mittelhochdeutsch</language>
    </langUsage>
    <particDesc>
      <listPerson>
        <person xml:id="person_ID" corresp="persons.xml#person_ID">
          <persName type="preferred">...</persName>
          <idno type="GND">...</idno>       <!-- if known -->
          <idno type="wikidata">...</idno>  <!-- if known -->
        </person>
      </listPerson>
    </particDesc>
  </profileDesc>

  <revisionDesc>
    <change when="YYYY-MM-DD" who="#contributor" n="1.0">Initial TEI transformation</change>
  </revisionDesc>
</teiHeader>
```

### 3.2 Body Structure

```xml
<text>
  <body>
    <div type="book|chapter|section|paratext|prologus" xml:id="SIGLE.N">
      <head type="chapter" n="1">I</head>  <!-- optional; first child of div -->
      <p ana="paragraph">                   <!-- or <l> for verse -->
        <pb n="1r" facs="#page_ID"/>
        <cb n="a"/>                          <!-- column break, if applicable -->
        <lb n="1" facs="#line_ID"/>
        <w xml:id="SIGLE_1r_1_0" lemmaRef="lexicon.xml#lemma_ID" pos="TAG">wort</w>
        <pc xml:id="SIGLE_1r_1_1" join="left">,</pc>
        <pc xml:id="SIGLE_1r_1_2" join="right">•</pc>  <!-- caesura marker -->
      </p>
    </div>
  </body>
</text>
```

**Structural rules:**
- Chapter `<head>` elements must be the **first child** of their containing `<div type="chapter">`, not inline in the text flow. Use `<milestone unit="chapter"/>` at the original text position if needed.
- Decorative or scribal elements that are not lexical words (`<hi rend="initial_historisiert">`, running headers in `<fw>`) should not carry `@lemmaRef` or `@pos`.
- Scribal marks (ł, -, ̃, ჻, =) should be `<pc>` elements, not `<w>`.

### 3.3 Word Annotation Model

```xml
<w xml:id="SIGLE_folio_line_pos"
   lemmaRef="lexicon.xml#lemma_ID"
   pos="TAG">
  wordform
</w>
```

| Attribute | Required | Description |
|-----------|----------|-------------|
| `@xml:id` | Yes | Unique identifier per §2 naming convention |
| `@lemmaRef` | Phase 1 | Pointer to `lexicon.xml#lemma_ID` |
| `@pos` | Phase 2 | One of the 19 MHDBDB POS tags |
| `@meaningRef` | Future | Sense-level pointer (not yet required) |
| `@wordRef` | Future | Variant form pointer (not yet required) |

### 3.4 Punctuation Encoding

```xml
<!-- Standard punctuation (attaches to preceding word) -->
<pc xml:id="..." join="left">,</pc>

<!-- Caesura / clause boundary marker -->
<pc xml:id="..." join="right">•</pc>
```

`<seg type="pc">` is **not valid** in this schema. Use `<pc join="left|right">` exclusively.

---

## 4. Mapping Instructions

### Step 1 — Prepare the Source TEI

1. Ensure UTF-8 encoding throughout.
2. Assign `@xml:id` to every `<w>` and `<pc>` following the naming convention.
3. Create or verify the work, author, and genre entries in the authority files.
4. Write the `<teiHeader>` per §3.1.

### Step 2 — Auto-Match Lemmaref (Phase 1)

Run the auto-match script against `authority-files/variants.xml` (~192,674 forms):

```bash
python scripts/wzb-auto-match.py --input tei/SIGLE.tei.xml --output tei/SIGLE.lemma-autofill.tei.xml
```

This assigns `@lemmaRef` for unambiguous matches only. Ambiguous and unmatched forms go to a TSV for manual resolution (Phase 1b).

**MHG normalisation**: The script normalises both word forms and variants before matching using the rules in `scripts/mhg_normalizer.py`:

```
â → a,  ê → e,  î → i,  ô → o,  û → u
ä → ae, ö → oe, ü → ue
```

Your source file may use manuscript-level spellings (e.g., `herczen` not `hêrzen`). Normalisation handles this automatically.

**Expected coverage**: 85–92% auto-resolved for typical MHG texts.

### Step 3 — Resolve Ambiguous / Unmatched Lemmata (Phase 1b)

The auto-match script produces a disambiguation TSV. Work through it in frequency tiers:

| Tier | Condition | Strategy |
|------|-----------|----------|
| 1 | High-freq, uniform usage | Bulk form-level resolution |
| 2 | Context-dependent | Per-instance review (±4-word context) |
| 3 | Hapax, unambiguous | Bulk if clear; defer if unclear |
| 4 | Unmatched mid-freq | Check [Wörterbuchnetz](https://www.woerterbuchnetz.de/) (BMZ/Lexer); add new lemma if missing |
| 5 | Unmatched long tail | Accept residual gap |

Common deferred items (expect ~5–8% residual):
- Pronoun/case ambiguity: `in`, `des`, `ir`, `im`
- Multi-sense verbs: `werden`, `haben`
- Language-specific annotations (Czech glosses, Latin quotes): map to existing or new lemma

If a lemma is genuinely missing from `lexicon.xml`, add it following the `lemma_ID` convention (next available ID, increment by 20).

### Step 4 — Assign POS Tags (Phase 2)

Auto-assign tags for lemmata with a single POS value in `lexicon.xml`:

```bash
python scripts/wzb-pos-assign.py --tei tei/SIGLE.lemma-autofill.tei.xml
```

Multi-POS lemmata go to a pending TSV for manual resolution. See §5 for the full tagset.

Apply resolved POS values to the TEI:

```bash
python scripts/wzb-pos-apply.py --tei tei/SIGLE.lemma-autofill.tei.xml --pending Wenzelsbibel/phase2/wzb-pos-pending.tsv
```

**Expected coverage**: 93–96% after auto-assign + manual disambiguation batches.

### Step 5 — Structural Cleanup

Review and fix:
- Book/chapter headers in `<fw>` elements: strip `@lemmaRef`/`@pos` (not lexical)
- Chapter numbering: move `<head type="chapter">` to first child of `<div type="chapter">`
- Scribal marks: convert `<w>` → `<pc>` for non-lexical tokens (ł, -, ̃, etc.)
- Decorative initials in `<hi>`: convert split letters (`I+n`, `U+nd`) to `<pc>` or `<w>` as appropriate

### Step 6 — Validate

See §5 for validation commands and checklists.

---

## 5. Validation

### Level 1 — TEI Conformance

```bash
source .venv/Scripts/activate
python -c "
from lxml import etree
relaxng = etree.RelaxNG(etree.parse('schema/mhdbdb.rng'))
doc = etree.parse('tei/SIGLE.tei.xml')
print('Valid:', relaxng.validate(doc))
if not relaxng.validate(doc):
    for e in relaxng.error_log: print(e)
"
```

All errors must be resolved. Common fixable errors:

| Error | Fix |
|-------|-----|
| `Did not expect element seg there` | Convert `<seg type="pc">` → `<pc join="left">` |
| `Expecting an element, got nothing` | Missing required header element (check `classDecl`, `particDesc`) |
| `Element hi has extra content: w` | `<w>` inside inline element that doesn't allow it; restructure |

### Level 2 — MHDBDB Conformance

```bash
python scripts/wzb-pos-apply.py --dry-run  # check POS coverage
```

Manual checks:
- [ ] Every `@lemmaRef` resolves to a real entry in `authority-files/lexicon.xml`
- [ ] Every `@pos` value is one of the 19 valid tags (no `ART`, no `GRA`)
- [ ] No `<w>` has `@meaningRef` without `@lemmaRef`
- [ ] `@xml:id` values are unique across the file

### Level 3 — Referential Integrity

```bash
python scripts/build-corpus-index.py --file tei/SIGLE.tei.xml --dry-run
```

Verifies that position counting (only `<w>` elements with `@lemmaRef`) is consistent between Python and the expected JS output.

### Checklist

Before opening a PR:
- [ ] File validates against `schema/mhdbdb.rng`
- [ ] `@lemmaRef` coverage ≥ 85% (document residual gaps in PR description)
- [ ] `@pos` coverage ≥ 90%
- [ ] No `<seg type="pc">` elements remain
- [ ] Work entry exists in `authority-files/works.xml`
- [ ] Author entry exists in `authority-files/persons.xml`
- [ ] Genre entries exist in `authority-files/genres.xml` and are reflected in `<classDecl>`
- [ ] `<revisionDesc>` updated with contributor and date
- [ ] `docs/JOURNAL.md` updated with a brief ingestion note

---

## 6. POS Tagset Reference

The MHDBDB uses 19 POS tags. **`ART` is not valid — use `DET`.**

| Tag | Category | MHG Examples |
|-----|----------|--------------|
| `NOM` | Noun | *acker, zît, minne, kraft* |
| `NAM` | Proper noun | *Uolrîch, Wiene, Rhîn*; *sant* before a name → `NAM` |
| `ADJ` | Adjective | *grôz, schoene, guot* |
| `ADV` | Adverb | *schone, vil, sêre, gar* |
| `DET` | Determiner | *der, diu, daz, ein, diser, kein* — articles + demonstratives + indefinites |
| `POS` | Possessive | *mîn, dîn, unser, ir* (attributive possessive) |
| `PRO` | Pronoun | *ich, ez, wir*; relative and indefinite pronouns |
| `PRP` | Preposition | *ûf, zuo, under, durch* |
| `NEG` | Negation | *niht, nit, nie, ne, en, n* — **never tag as PRO** |
| `NUM` | Numeral | *zwô, drî, zweinzegest* |
| `CNJ` | Conjunction (fallback) | Use only when SCNJ/CCNJ cannot be determined |
| `SCNJ` | Subordinating conj. | *daz* (clause-opening), *ob, swenne, sît, als* (temporal) |
| `CCNJ` | Coordinating conj. | *und, oder, aber, ouch, noch* |
| `IPA` | Interrogative particle | *wie* (direct question), *war* |
| `VRB` | Full verb | *liuhten, varn, machen*; *haben/sîn/werden* when lexical |
| `VEX` | Auxiliary verb | *haben/sîn/werden* forming perfect/passive tenses |
| `VEM` | Modal verb | *müezen, suln, kunnen* |
| `INJ` | Interjection | *ahî, owê* |
| `DIG` | Roman numeral | *IX, XVII* (medieval: U = V, e.g., *UIII* = VIII) |

**Common disambiguation rules:**
- `daz`: `DET` when deictic (points to prior content), `SCNJ` when opening a dependent clause
- `ein`: `DET` before a noun, `NUM` when standalone ("one")
- `haben/sîn/werden`: `VEX` with Partizip II (perfect/passive), `VRB` otherwise
- `ûf/ûʒ/vor/wider`: `PRP` governing a noun phrase, `ADV` when standalone
- `âne`: `NEG` (negation particle)
- `kein/dekein`: `DET` when modifying a noun

---

## 7. Submission and Review

### Option A — Pull Request (Preferred)

1. Fork or branch from `main`: `git checkout -b feature/ingest-SIGLE`
2. Place the annotated TEI file in `tei/SIGLE.tei.xml`
3. Add or update authority file entries
4. Open a PR against `main` with:
   - Text title, sigle, and edition used
   - `@lemmaRef` and `@pos` coverage percentages
   - Description of any residual gaps and why
   - Confirmation that all checklist items in §5 are complete

### Option B — Email Submission

Send annotated TEI + a brief description of the edition basis and coverage statistics to **mhdbdb@plus.ac.at**.

### Review Timeline

Expect 2–4 weeks for review. The review focuses on:
- Schema validity
- Authority file alignment (lemmaRef targets, person/work/genre entries)
- POS tag quality (spot-check of content words)
- Structural correctness (chapter hierarchy, scribal marks)

---

## 8. Worked Example — Wenzelsbibel (WZB)

The Wenzelsbibel ingestion (#34) is the reference implementation for this guide. It covers:

- **Source**: WB-DEA critical edition of the Wenceslas Bible (Vienna, ÖNB Cod. 2759–2764), a Middle High German Bible translation for Wenceslas IV, ~149,000 word tokens
- **Challenges**: Bohemian scribal conventions (`cz=z`, `v=u`, `ou=û`), Old Czech interlinear glosses (~115 tokens), historiated initials, extensive paratext

### Phase 1 result

```
Auto-matched:   ~86% (lemmaRef on first pass)
After Phase 1b: 91.6% (disambiguation batches + new lemmata)
Residual:        8.4% (pronoun/case ambiguity, Czech glosses, Latin hapax)
```

### Phase 2 result

```
Auto-assigned:   ~75% (single-POS lemmata)
After batches:   95.3% (LLM disambiguation, context patterns)
Residual:         4.7% (~6,050 no-lemmaRef tokens; accepted ceiling)
```

### Key decisions documented in JOURNAL.md

- Czech glosses (`toho`, `pzde`, `bzde`) → new `lemma_78628` (type: cs)
- `et` (Latin) → `lemma_78608`; `CAPITULUM` chapter markers → `lemma_2`
- Scribal marks (ł, -, ̃, ჻, =) → `<pc>` elements, not `<w>`
- Caesura marker `•` → `<pc join="right">` (10,265 instances)

### Pipeline commands (WZB-specific scripts, adaptable for other texts)

```bash
# Phase 1 — auto-match
python scripts/wzb-auto-match.py

# Phase 1b — resolve disambiguation TSV
python scripts/wzb-bulk-resolve.py --resolutions Wenzelsbibel/phase1b/resolutions/wzb-resolutions-batchNN.tsv --dry-run
python scripts/wzb-bulk-resolve.py --resolutions Wenzelsbibel/phase1b/resolutions/wzb-resolutions-batchNN.tsv

# Phase 2 — POS auto-assign + apply
python scripts/wzb-pos-assign.py
python scripts/wzb-pos-bulk-resolve.py --resolutions Wenzelsbibel/phase2/resolutions/wzb-pos-resolutions-batchNN.tsv
python scripts/wzb-pos-apply.py

# Validation
python -c "from lxml import etree; ..."  # per §5
```

Full pipeline documentation: `docs/features/034-wenzelsbibel-annotation.md`

---

## Appendix — Common Errors

| Symptom | Cause | Fix |
|---------|-------|-----|
| `<seg type="pc">` in output | Legacy encoding | Convert to `<pc join="left\|right">` |
| `@lemmaRef` points to non-existent ID | Typo or deleted lemma | Verify ID in `authority-files/lexicon.xml` |
| `pos="ART"` | Invalid tag | Change to `pos="DET"` |
| `pos="GRA"` | Invalid tag (grammar particle) | Reclassify as `ADV` or `PRP` depending on context |
| Schema error: `Expecting an element, got nothing` | Missing `<classDecl>` or `<particDesc>` | Add required header sections per §3.1 |
| Zero lemmaRef matches on auto-run | Source uses `@orig` not text content | Check element text vs `@norm`/`@orig` attribute handling in auto-match script |
| Very low lemmaRef coverage (<70%) | Text dialect far from core MHG | Extend normalisation rules; consider manual Tier 1 before running script |

---

*Guide version 1.0 — 2026-04-17 | Based on Wenzelsbibel ingestion pilot (#34)*
