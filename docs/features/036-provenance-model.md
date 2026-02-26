# Issue #36: Provenance Model for Digital Intermediaries

## Context

Many MHDBDB TEI files derive not directly from a print edition but from a **digital intermediate** (e-text): a third-party transcription, online library text, or research project digitization. The actual chain is:

```
Print Edition → Digital Intermediate (e-text) → MHDBDB TEI
```

Currently, digital intermediaries are documented only as **unstructured prose in `<note>` elements** — not machine-readable, not consistent, sometimes missing entirely.

Five sub-issues need this resolved: #35 (Klug, 18 texts), #37 (Harsch/Augustana, 25 texts), #38 (TITUS, 4 texts), #39 (Gloning, 8 texts), #40 (Virginia/Trier, 5 texts). ~55 files total (with some overlaps).

## Current State (Data Exploration)

### Existing `<sourceDesc>` Pattern (all 670 files)

```xml
<sourceDesc>
  <msDesc>
    <msIdentifier corresp="works.xml#work_XXX">
      <idno type="sigle">ABG</idno>
      <!-- handschriftencensus, GND, Wikidata -->
    </msIdentifier>
    <additional>
      <listBibl>
        <biblStruct type="bookSection" xml:id="ABG_ABG" corresp="http://zotero.org/..." key="ABG">
          <!-- print edition only -->
          <note>...sometimes mentions digital source in plain text...</note>
        </biblStruct>
      </listBibl>
    </additional>
  </msDesc>
</sourceDesc>
```

### How Digital Intermediaries Are Currently Documented

| Provider | Example | How documented |
|----------|---------|----------------|
| Klug (#35) | ABS | **Not at all** — no mention of Klug |
| Harsch (#37) | AC3 | In `<note>`: "Digitale Version: Ulrich Harsch 1998 http://..." + "weist viele Abweichungen von der gedruckten Edition auf" |
| TITUS (#38) | AXS | In `<note>`: multiple URLs and contributors in prose |
| Gloning (#39) | ABG | In `<note>`: "Digitale Fassung: Thomas Gloning, 1/2002" |
| Virginia/Trier (#40) | DL2 | In `<note>`: "Die digitale Textfassung beruht teilweise auf..." |

### Overlapping Sigles

FWWB, GSP, KDO, KME appear in both #35 (Klug) and #39 (Gloning). Their `<note>` elements credit Gloning as the digital transcriber. This suggests Klug built on Gloning's transcriptions for these texts — **dual provenance** that needs explicit modeling.

## TEI P5 Research

### What the Standard Says

**Chapter 2.2.7 (`<sourceDesc>`):** Multiple sources are explicitly supported. `<listBibl>` can contain multiple `<bibl>` or `<biblStruct>` elements. No constraint on number.

**Chapter 2.2.8 (Electronic-to-Electronic):** Recommends `<biblFull>` when deriving from another TEI file. Overkill for non-TEI sources (HTML e-texts, OCR).

**`@type` on `<bibl>`:** Unconstrained free text (from `att.typed`). Projects define their own values. No standard vocabulary — `type="digitalIntermediary"` is valid and self-documenting.

**`@corresp`:** Standard mechanism for cross-referencing related elements. Can link the digital intermediary back to the print edition it derives from.

### Approaches Evaluated

| Approach | Mechanism | Pros | Cons |
|----------|-----------|------|------|
| **A. Flat `<listBibl>`** | Multiple `<bibl>`/`<biblStruct>` siblings | Simple, extensible | No explicit derivation direction |
| **B. Nested `<relatedItem>`** | `<bibl>` nested inside `<biblStruct>` via `<relatedItem type="otherForm">` | Semantically precise | Inverts actual derivation direction; harder to query |
| **C. `<biblFull>`** | Full file description of source | TEI recommended for TEI→TEI | Overkill for HTML/OCR sources |
| **D. Flat + `@corresp`** | Siblings with `@corresp` cross-reference | Simple, machine-readable, explicit link | `@corresp` implies bidirectional — direction from context |

### How Other Projects Handle It

- **DTA (Deutsches Textarchiv):** Uses `<msDesc>/<idno>` chain to link physical exemplar to digital facsimile. No separate `<bibl>` for intermediaries because DTA controls the full pipeline.
- **TEI by Example / BPTL:** Focus on print→digital for own transcriptions, not third-party intermediaries.
- **Real-world consensus:** No standard pattern exists for "third-party digital intermediate" — projects define their own.

## Decision: Approach D (Flat `<listBibl>` with `@corresp`)

### Rationale

- Simplest TEI-conformant approach
- Keeps existing `<biblStruct>` untouched — only adds a sibling `<bibl>`
- `@corresp` creates explicit link between intermediary and print edition
- `@type="digitalIntermediary"` enables programmatic filtering
- Optional `@subtype` categorizes the intermediary type
- Matches Katharina's proposals in spirit, refines them structurally

### Template

```xml
<!-- Inside existing <listBibl>, AFTER the print edition <biblStruct> -->

<bibl type="digitalIntermediary" xml:id="{SIGLE}_etext"
      corresp="#{SIGLE}_{SIGLE}">
  <title>Elektronische Zwischenstufe</title>
  <respStmt>
    <resp>{responsibility description}</resp>
    <name>{person or orgName}</name>
  </respStmt>
  <date {when|notBefore|notAfter}="{date}">{display date}</date>
  <ref target="{URL}"/>  <!-- if available -->
  <note type="provenance">
    {How this e-text relates to the print edition and to our TEI file.}
  </note>
  <note type="fidelity">
    Keine diplomatische Transkription der zugrundeliegenden
    Druckedition. Abweichungen hinsichtlich Strukturierung,
    Zeilenumbrüchen und Layoutmerkmalen sind möglich.
  </note>
</bibl>
```

### Provider-Specific Templates

#### #35 Klug (18 texts): `subtype="personal"`
```xml
<bibl type="digitalIntermediary" xml:id="{SIGLE}_etext_klug"
      corresp="#{SIGLE}_{SIGLE}">
  <title>Elektronische Zwischenstufe (E-Text Klug)</title>
  <respStmt>
    <resp>Erstellung des elektronischen Ausgangstextes</resp>
    <name>Helmut W. Klug</name>
  </respStmt>
  <date notBefore="2008" notAfter="2013">ca. 2008–2013</date>
  <note type="provenance">
    Im Rahmen der Dissertation „Pflanzen in deutschsprachigen Texten
    des Mittelalters" (Graz 2015, URN: urn:nbn:at:at-ubg:1-81622)
    erstellter E-Text. Der MHDBDB vom Verfasser zur Verfügung gestellt.
  </note>
  <note type="fidelity">
    Keine diplomatische Transkription der Druckedition. Abweichungen
    hinsichtlich Zeilenumbrüchen und Layoutmerkmalen sind möglich.
  </note>
</bibl>
```

#### #37 Harsch/Augustana (25 texts): `subtype="onlineLibrary"`
```xml
<bibl type="digitalIntermediary" xml:id="{SIGLE}_etext_harsch"
      corresp="#{SIGLE}_{SIGLE}">
  <title>Elektronische Zwischenstufe (Bibliotheca Augustana)</title>
  <respStmt>
    <resp>Digitale Aufbereitung und Online-Bereitstellung</resp>
    <name>Ulrich Harsch</name>
  </respStmt>
  <date from="1996">seit 1996</date>
  <ref target="https://www.hs-augsburg.de/~harsch/augustana.html"/>
  <note type="provenance">
    E-Text aus der Bibliotheca Augustana. Von der MHDBDB als
    elektronische Vorlage übernommen.
  </note>
  <note type="fidelity">
    Keine diplomatische Transkription der Druckedition. Abweichungen
    hinsichtlich Strukturierung, Zeilenumbrüchen und Layoutmerkmalen
    sind möglich.
  </note>
</bibl>
```

#### #38 TITUS (4 texts): `subtype="researchProject"`
```xml
<bibl type="digitalIntermediary" xml:id="{SIGLE}_etext_titus"
      corresp="#{SIGLE}_{SIGLE}">
  <title>Elektronische Zwischenstufe (TITUS-Projekt)</title>
  <respStmt>
    <resp>Digitale Erfassung und texttechnische Aufbereitung</resp>
    <orgName>TITUS-Projekt (Goethe-Universität Frankfurt)</orgName>
  </respStmt>
  <ref target="http://titus.uni-frankfurt.de/texte/etcs/germ/mhd/"/>
  <note type="provenance">
    E-Text aus dem TITUS-Projekt (Thesaurus Indogermanischer
    Text- und Sprachmaterialien). Von der MHDBDB als elektronische
    Vorlage übernommen. Konkretes Digitalisierungsdatum nicht dokumentiert.
  </note>
  <note type="fidelity">
    Keine diplomatische Transkription der Druckedition. Die Textfassung
    folgt projektinternen Transkriptions- und Codierungsprinzipien
    des TITUS-Korpus.
  </note>
</bibl>
```

#### #39 Gloning (8 texts): `subtype="personal"`
```xml
<bibl type="digitalIntermediary" xml:id="{SIGLE}_etext_gloning"
      corresp="#{SIGLE}_{SIGLE}">
  <title>Elektronische Zwischenstufe (E-Text Gloning)</title>
  <respStmt>
    <resp>Elektronische Bereitstellung</resp>
    <name>Thomas Gloning</name>
  </respStmt>
  <ref target="https://www.uni-giessen.de/de/fbz/fb05/germanistik/absprache/sprachverwendung/gloning/etexte.htm"/>
  <note type="provenance">
    E-Text aus der E-Texte-Sammlung von Prof. Thomas Gloning
    (Universität Gießen). Von der MHDBDB als elektronische
    Vorlage übernommen.
  </note>
  <note type="fidelity">
    Keine diplomatische Transkription der Druckedition. Abweichungen
    hinsichtlich Strukturierung, Zeilenumbrüchen und Layoutmerkmalen
    sind möglich.
  </note>
</bibl>
```

#### #40 Virginia/Trier (5 texts): `subtype="digitalArchive"`
```xml
<bibl type="digitalIntermediary" xml:id="{SIGLE}_etext_mhgta"
      corresp="#{SIGLE}_{SIGLE}">
  <title>Elektronische Zwischenstufe (MHGTA)</title>
  <respStmt>
    <resp>Projektleitung</resp>
    <orgName>Akademie der Wissenschaften und der Literatur Mainz</orgName>
  </respStmt>
  <respStmt>
    <resp>Digitale Erfassung</resp>
    <orgName>Kompetenzzentrum Trier</orgName>
  </respStmt>
  <respStmt>
    <resp>TEI-Auszeichnung</resp>
    <orgName>Electronic Text Center, University of Virginia</orgName>
  </respStmt>
  <date notBefore="2001" notAfter="2003">2001–2003</date>
  <ref target="http://etext.lib.virginia.edu/german/mhg"/>
  <note type="provenance">
    E-Text aus dem Mittelhochdeutschen Textarchiv (MHGTA),
    Kooperationsprojekt von Mainz, Trier und Virginia.
    Von der MHDBDB als elektronische Vorlage übernommen.
  </note>
  <note type="fidelity">
    Keine diplomatische Transkription der Druckedition.
    Abweichungen sind möglich.
  </note>
</bibl>
```

### Dual Provenance (FWWB, GSP, KDO, KME)

These texts have two intermediaries (Gloning transcription → Klug annotation). Add both `<bibl>` elements:

```xml
<bibl type="digitalIntermediary" xml:id="FWWB_etext_gloning" corresp="#FWWB_FWWB">
  <!-- Gloning template -->
</bibl>
<bibl type="digitalIntermediary" xml:id="FWWB_etext_klug" corresp="#FWWB_etext_gloning">
  <!-- Klug template, but @corresp points to Gloning's etext, not print edition -->
</bibl>
```

This models: `Print → Gloning e-text → Klug e-text → MHDBDB TEI`.

## Implementation Plan

1. **Pilot**: Apply Klug template (#35) to one file (e.g., ABS), validate TEI conformance
2. **Batch #35**: All 18 Klug texts
3. **Batch #37**: All 25 Harsch texts
4. **Batch #38**: All 4 TITUS texts
5. **Batch #39**: All 8 Gloning texts (including the 4 overlapping with Klug)
6. **Batch #40**: All 5 Virginia/Trier texts
7. **Update `<encodingDesc>`**: Document the `type="digitalIntermediary"` convention project-wide

## Differences from Katharina's Proposals

| Aspect | Katharina's proposal (#35) | This model |
|--------|---------------------------|-----------|
| Element | `<bibl type="digitalIntermediary">` | Same |
| Placement | Unclear (standalone?) | Inside existing `<listBibl>`, after `<biblStruct>` |
| Link to print edition | None explicit | `@corresp="#{SIGLE}_{SIGLE}"` |
| Dissertation context | Nested `<relatedItem type="dissertation">` with full `<biblStruct>` | Prose in `<note type="provenance">` (simpler, less structural noise) |
| Availability note | Separate `<note type="availability">` | Folded into `<note type="provenance">` |
| Fidelity note | `<note type="editorialStatus">` | `<note type="fidelity">` (more precise label) |

The structural difference is small — mainly: explicit `@corresp` linking, placement inside `<listBibl>`, and less nesting.

## TEI P5 References

| Topic | Chapter |
|-------|---------|
| `<sourceDesc>` | [2.2.7](https://www.tei-c.org/release/doc/tei-p5-doc/en/html/HD.html) |
| Electronic-to-electronic | [2.2.8](https://www.tei-c.org/release/doc/tei-p5-doc/en/html/HD.html) |
| `<bibl>` | [ref-bibl](https://tei-c.org/release/doc/tei-p5-doc/en/html/ref-bibl.html) |
| `att.typed` (free `@type`) | [ref-att.typed](https://tei-c.org/release/doc/tei-p5-doc/en/html/ref-att.typed.html) |
| `<derivation>` | [Ch. 16](https://tei-c.org/release/doc/tei-p5-doc/en/html/CC.html) |

## Out of Scope

- RDF/graph export of provenance chains (future)
- ODD schema formalization (see #32)
- Retroactive cleanup of existing `<note>` prose (keep for human context)
- `<biblFull>` modeling (only needed for TEI→TEI derivation)
