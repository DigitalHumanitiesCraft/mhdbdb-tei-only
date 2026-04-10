# MHDBDB TEI Schemas

RELAX NG schemas for the MHDBDB corpus and authority files. Designed for projects that want to produce TEI data compatible with the [Mittelhochdeutsche Begriffsdatenbank](https://mhdbdb.plus.ac.at).

## Files

| File | Purpose |
|------|---------|
| `mhdbdb.rnc` | Corpus schema (source of truth, RELAX NG Compact) |
| `mhdbdb.rng` | Corpus schema (generated, for lxml/jing) |
| `mhdbdb-authority.rnc` | Authority files schema (source of truth) |
| `mhdbdb-authority.rng` | Authority files schema (generated) |
| `tei_all.rng` | TEI P5 4.11.0 (gitignored, download below) |
| `examples/` | Validated example files for all document types |

## Two-stage validation

Every MHDBDB file must pass both stages:

1. **TEI P5 conformance** (`tei_all.rng`) -- the file is valid TEI
2. **MHDBDB constraints** (`mhdbdb.rnc` or `mhdbdb-authority.rnc`) -- the file follows MHDBDB conventions

Stage 1 ensures interoperability with the TEI ecosystem. Stage 2 ensures the file works with MHDBDB tools (indexes, search, rendering).

## Quick start: validate a file

```bash
# Download tei_all.rng (once)
curl -sL "https://tei-c.org/release/xml/tei/custom/schema/relaxng/tei_all.rng" -o schema/tei_all.rng

# Regenerate RNG from RNC (after editing .rnc)
python -m rnc2rng schema/mhdbdb.rnc schema/mhdbdb.rng
python -m rnc2rng schema/mhdbdb-authority.rnc schema/mhdbdb-authority.rng

# Validate a corpus file (Python)
python -c "
from lxml import etree
tree = etree.parse('tei/ABG.tei.xml')
# Stage 1
tei_all = etree.RelaxNG(etree.parse('schema/tei_all.rng'))
print('TEI P5:', 'VALID' if tei_all.validate(tree) else tei_all.error_log)
# Stage 2
mhdbdb = etree.RelaxNG(etree.parse('schema/mhdbdb.rng'))
print('MHDBDB:', 'VALID' if mhdbdb.validate(tree) else mhdbdb.error_log)
"
```

## Corpus schema (`mhdbdb.rnc`)

For the 666 TEI-encoded Middle High German texts in `tei/`.

### Document structure

```
TEI [@xml:id = sigle]
  teiHeader
    fileDesc (titleStmt, publicationStmt, sourceDesc)
    encodingDesc (projectDesc, editorialDecl, classDecl)
    profileDesc (langUsage, particDesc)
    revisionDesc
  text > body
    div [@type, @n] (recursive)
      p, lg, head, l, ab    -- block elements
      w, pc, hi, ...        -- inline elements (also allowed directly)
```

### Key elements

| Element | Attributes | Purpose |
|---------|-----------|---------|
| `<w>` | `@xml:id` (required), `@lemmaRef`, `@pos`, `@ana`, `@corresp`, `@reason`, `@xml:lang` | Word token |
| `<pc>` | `@join` (required: `left`\|`right`), `@xml:id` | Punctuation |
| `<div>` | `@type` (optional: chapter, section, number, song, parallel, colophon, recipe), `@n` | Text division |
| `<lg>` | `@type` (stanza), `@n` | Line group (verse) |
| `<l>` | `@n` | Verse line |
| `<lb/>` | `@n` | Line break (prose) |
| `<hi>` | `@rend` (initial, upper_case_first_letter, ...) | Highlighting |

### Word annotation pattern

```xml
<w xml:id="ABG_101_0"
   lemmaRef="lexicon.xml#lemma_879"
   pos="NOM"
   ana="lexicon.xml#lemma_879_sense_1234"
   corresp="variants.xml#type_5678">brôt</w>
```

- `@lemmaRef` -- pointer to lexicon entry (authority file)
- `@pos` -- POS tag from the MHDBDB tagset (see `docs/TEI-MODEL.md` Section 5); compound tags space-separated (`VEM PRO`)
- `@ana` -- pointer to sense/concept (semantic annotation)
- `@corresp` -- pointer to orthographic variant type
- `@reason` -- decomposition for compound POS tags (`wilt+du`)
- Words without `@lemmaRef` are skipped by the corpus index

### Cross-references to authority files

Cross-references between corpus and authority files use relative URIs:

```
lexicon.xml#lemma_879       -- lemma entry
lexicon.xml#lemma_879_sense_1234  -- sense within lemma
variants.xml#type_5678      -- orthographic variant type
persons.xml#person_445      -- person
works.xml#work_89           -- work
genres.xml#genre_aaa        -- genre category
```

## Authority schema (`mhdbdb-authority.rnc`)

For the 7 XML files in `authority-files/` that serve as controlled vocabularies.

| File | Content | Body structure |
|------|---------|---------------|
| `lexicon.xml` | 43,750 lemmata with senses | `<div>/<entry>` |
| `variants.xml` | 192,472 variant forms (39,282 lemma groups) | `<div>/<entry>/<form>` |
| `persons.xml` | 211 persons (authors, editors) | `<listPerson>/<person>` |
| `works.xml` | 583 works with bibliographic data | `<listBibl>/<bibl>` |
| `concepts.xml` | 567 semantic concepts | `<taxonomy>` in `<encodingDesc>` |
| `genres.xml` | 615 genre categories (hierarchical) | `<taxonomy>` in `<encodingDesc>` |
| `names.xml` | 90 medieval name forms | `<taxonomy>` in `<encodingDesc>` |

### Identifier conventions

- Person IDs: `person_` + integer (`person_445`)
- Work IDs: `work_` + integer (`work_89`)
- Lemma IDs: `lemma_` + integer (`lemma_879`)
- Genre IDs: `genre_` + UUID hex (`genre_0480b285`)
- External IDs: `<idno type="GND">`, `<idno type="wikidata">`, `<idno type="handschriftencensus">`

## Examples

The `examples/` directory contains validated example files for every document type:

| Example | Schema | Shows |
|---------|--------|-------|
| `corpus.example.tei.xml` | mhdbdb.rnc | All genre patterns (verse, prose, recipe, lyric, sermon, colophon) |
| `authority-lexicon.example.xml` | mhdbdb-authority.rnc | Lemma entries with senses |
| `authority-persons.example.xml` | mhdbdb-authority.rnc | Person records with external IDs |
| `authority-works.example.xml` | mhdbdb-authority.rnc | Work records with bibliographic data |
| `authority-genres.example.xml` | mhdbdb-authority.rnc | Hierarchical genre taxonomy |
| `authority-concepts.example.xml` | mhdbdb-authority.rnc | Semantic concept taxonomy |
| `authority-variants.example.xml` | mhdbdb-authority.rnc | Orthographic variant mappings |
| `authority-names.example.xml` | mhdbdb-authority.rnc | Medieval name forms |

## Mapping your data to MHDBDB

If you want to produce TEI files that work with MHDBDB tools:

1. **Start from an example** in `examples/` -- copy and adapt
2. **Use the corpus schema** for text files, authority schema for vocabularies
3. **Required minimum** per `<w>`: `@xml:id` (unique within file) and text content
4. **Recommended**: `@lemmaRef` (enables search), `@pos` (enables filtering)
5. **Optional**: `@ana` (semantic annotation), `@corresp` (variant linking)
6. **Punctuation**: always use `<pc join="left|right">`, never `<seg type="pc">`
7. **Prose line breaks**: use `<lb/>`, never `<l>` (reserved for verse)
8. **Validate** against both `tei_all.rng` and `mhdbdb.rnc` before submitting

### RNC editing note

The `.rnc` files are the source of truth. After editing, regenerate `.rng`:

```bash
python -m rnc2rng schema/mhdbdb.rnc schema/mhdbdb.rng
```

Note: `div` is a reserved keyword in RELAX NG Compact syntax. The corpus schema uses `tei.div` as the pattern name for `<div>` elements.

## Normative documents

- [TEI-MODEL.md](../docs/TEI-MODEL.md) -- corpus encoding model (Soll-Modell)
- [TEI-MODEL-AUTH-FILES.md](../docs/TEI-MODEL-AUTH-FILES.md) -- authority file encoding model
- [CONTRACTS.MD](../docs/CONTRACTS.MD) -- position counting contract (Python/JS parity)
