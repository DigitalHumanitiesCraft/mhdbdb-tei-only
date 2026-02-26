# 034 — Wenzelsbibel Annotation Pipeline

**Issue:** #34 (Ingest neue Texte: WB, dann CoReMA)
**Status:** Planning
**Owner:** Julia (@juliahin)
**Support:** Chris (@chsteiner)

## Problem

The Wenzelsbibel (WZB) has been structurally transformed from WB-DEA source into MHDBDB-conformant TEI (`Wenzelsbibel/WZB.tei.xml`, Phase 1). The ~150,000 `<w>` elements currently have only text content — no `@lemmaRef`, `@pos`, `@meaningRef`, or `@wordRef` attributes. Without these, the text cannot participate in MHDBDB search, lemma highlighting, or concept navigation.

## Current State

### What exists

| Asset | Status | Details |
|-------|--------|---------|
| `Wenzelsbibel/WZB.tei.xml` | Phase 1 complete | 236k lines, 150k words, valid TEI, no annotations |
| `Wenzelsbibel/WB-DEA/` | Source data | 5 XML files (Prologus-Genesis, Exodus, Leviticus, Numeri, Deuteronomium) |
| WB-DEA word attributes | Available | `@orig` (diplomatic) + `@norm` (normalized) on every `<w>` |
| WB-DEA `<standOff>` | Available | Rich editorial commentary (out of scope for now) |
| `authority-files/works.xml` | **Missing WZB entry** | Needs new `work_WZB` entry |
| `authority-files/persons.xml` | Ready | `person_anonym` exists |

### What a fully annotated `<w>` looks like (existing MHDBDB texts)

```xml
<w xml:id="ALL_20100010_1"
   lemmaRef="lexicon.xml#lemma_722"
   meaningRef="lexicon.xml#lemma_722_sense_1177"
   pos="VRB"
   wordRef="lexicon.xml#lemma_722_sense_1177_type_2239">bitte</w>
```

### What WZB currently has

```xml
<w xml:id="WZB_1ra_6_5">herczen</w>
```

### Gap

Every `<w>` needs: `@lemmaRef`, `@pos`. Later also: `@meaningRef`, `@wordRef`.

## Data Profile

| Metric | Value |
|--------|-------|
| Total `<w>` elements | ~150,000 |
| Source files (WB-DEA) | 5 |
| Unique normalized word forms (@norm) | ~4,900 (Genesis alone) |
| MHDBDB lexicon entries | 43,750 |
| MHDBDB variant forms | 192,674 |
| POS tag set | PRO, VRB, NOM, ADJ, ADV, ART, CNJ, PRP, VEX, POS, NAM, NUM (can be space-separated for multi-tag) |

## Phased Plan

### Phase 1: Auto-Match lemmaRef (script-assisted)

**Goal:** Assign `@lemmaRef` to as many words as possible using the existing MHDBDB lexicon and variant mappings.

**Approach:**
1. Extract all unique `@norm` forms from `WZB.tei.xml` (the text content is already the @norm value from the WB-DEA transformation)
2. Match each form against `variants.xml` entries (192k forms linking to lemma IDs)
3. For unambiguous matches (one form maps to exactly one lemma), auto-assign `@lemmaRef`
4. For ambiguous matches (one form maps to multiple lemmata), flag for human/LLM disambiguation
5. For unmatched forms, flag for Phase 1b

**Expected outcome:** A significant portion of high-frequency function words (articles, pronouns, conjunctions, prepositions) should match unambiguously. Content words will have more ambiguity.

**Deliverable:** Python script that:
- Reads `variants.xml` into a lookup dictionary `{normalized_form: [lemma_id_1, lemma_id_2, ...]}`
- Walks `WZB.tei.xml`, matches each `<w>` text against the dictionary
- Writes `@lemmaRef` for unambiguous matches
- Outputs a report: matched (unambiguous), matched (ambiguous), unmatched

**Important caveat — MHG normalization:** The MHDBDB uses a specific normalization scheme (`â→a, ê→e, î→i, ô→o, û→u, ä→ae, ö→oe, ü→ue`; see `assets/js/lib/text-normalizer.js`). The WB-DEA `@norm` values may NOT follow this scheme (they preserve the manuscript normalization like "herczen" instead of MHDBDB-normalized "herze"). The matching script must apply MHDBDB normalization to both the variant forms and the WZB word forms before comparing.

### Phase 1b: LLM-Assisted Lemma Resolution (ambiguous + unmatched)

**Goal:** Resolve ambiguous matches and identify correct lemmata for unmatched words using Claude.

**Approach — Claude Code workflow:**
1. Julia opens `WZB.tei.xml` in her IDE with Claude Code
2. For each batch of ambiguous/unmatched words, Julia asks Claude to:
   - Identify the correct lemma given the sentence context
   - Suggest a `@lemmaRef` value (existing lemma ID or "NEW" if not in lexicon)
3. Claude has access to `lexicon.xml` and `variants.xml` for reference
4. Julia reviews Claude's suggestions and applies them

**Prompt template for Claude Code:**

```
I'm annotating the Wenzelsbibel (MHG biblical text) for MHDBDB.
Here are words that couldn't be auto-matched to our lexicon.
For each word, given its sentence context, suggest:
1. The correct MHG lemma (headword/dictionary form)
2. Whether it exists in our lexicon.xml (search for it)
3. If it exists: the lemma_ID. If not: mark as NEW.

Words to resolve:
[batch of ~20-50 words with surrounding context]
```

**Coverage target:** Best-effort with existing lexicon. Unmatched words are flagged in a report but NOT added to `lexicon.xml` in this phase (that requires a separate editorial decision).

### Phase 2: POS Tagging (LLM-assisted)

**Goal:** Assign `@pos` to every `<w>` element.

**Approach:**
1. For words with unambiguous `@lemmaRef` from Phase 1: inherit POS from `lexicon.xml` entry (the `<pos>` child of `<gramGrp>`)
2. For remaining words: LLM-assisted tagging in batches via Claude Code

**Prompt template:**

```
Assign POS tags to these Middle High German words from the Wenzelsbibel.
Use MHDBDB tag set: PRO VRB NOM ADJ ADV ART CNJ PRP VEX POS NAM NUM
Multiple tags allowed (space-separated) when word is ambiguous.

Context: [2-3 lines of surrounding text]
Words: [batch with positions]
```

**Auto-assignment rules (no LLM needed):**
- If lemma's `<gramGrp>/<pos>` has exactly one POS value → assign it
- Common patterns: `der/die/daz` → ART, `und/vnd` → CNJ, `in/an/mit` → PRP

**QA:** Script validates that assigned POS is in the MHDBDB tag set. Julia spot-checks ~5% per chapter.

### Phase 3: meaningRef + wordRef (future)

**Goal:** Full MHDBDB conformance with semantic concept links and variant form references.

**Approach (to be refined when Phase 2 is complete):**
- `@meaningRef`: Requires word sense disambiguation — which sense of a polysemous lemma is meant. This is the hardest annotation task. LLM-assisted with `concepts.xml` as reference.
  - Format: `lexicon.xml#lemma_{ID}_sense_{SENSE_ID}`
- `@wordRef`: Links to the specific orthographic variant in `variants.xml`.
  - Format: `lexicon.xml#lemma_{ID}_sense_{SENSE_ID}_type_{TYPE_ID}`
  - For existing variant forms: auto-assignable once lemmaRef + meaningRef are known
  - For new forms not in variants.xml: may need new `<form>` entries

**This phase is deferred** until Phase 1+2 are validated and the team decides how to handle lexicon gaps.

## Pre-Requisites (before Julia starts)

### 1. Register WZB in works.xml

Add a new entry to `authority-files/works.xml`:

```xml
<bibl xml:id="work_WZB">
  <title xml:lang="de">Wenzelsbibel</title>
  <title xml:lang="en">Wenceslas Bible</title>
  <idno type="sigle">WZB</idno>
  <ref target="genres.xml#[TBD_GENRE_ID]" xml:lang="de">[Bibelübersetzung/Bibeldichtung]</ref>
  <author ref="persons.xml#person_anonym">Anonym</author>
  <note type="manuscript">Wien, ÖNB, Cod. 2759-2764</note>
</bibl>
```

**Decision needed:** Genre classification — is WZB "Bibeldichtung" (Bible poetry), "Bibelübersetzung" (Bible translation), or a prose genre? Check `genres.xml` for best fit.

### 2. Build the auto-match script

Python script: `scripts/wzb-auto-match.py`

Input: `Wenzelsbibel/WZB.tei.xml` + `authority-files/variants.xml` + `authority-files/lexicon.xml`
Output: Annotated WZB with `@lemmaRef` where unambiguous + CSV report of ambiguous/unmatched words

### 3. Verify @norm coverage in WZB.tei.xml

Some WB-DEA words have `norm=""` (empty). These need to be identified and handled:
- If `@orig` is available: use it as fallback
- If both are empty: flag for manual review

## QA Strategy

### Automated checks (script)
- Every `@lemmaRef` value points to a real entry in `lexicon.xml`
- Every `@pos` value is in the MHDBDB tag set
- No `<w>` elements have `@meaningRef` without `@lemmaRef` (dependency order)
- Position counting: `<w>` elements with `@lemmaRef` must be countable by the corpus index builder (test with `scripts/build-corpus-index.py`)

### Manual checks (Julia)
- ~5% random sample per biblical book (chapter-level sampling)
- Focus on: content words (nouns, verbs, adjectives) where disambiguation matters most
- Cross-check against MHG dictionaries (BMZ, Lexer via Wörterbuchnetz, MWB Online)

### Integration test
- After Phase 1+2: Run `scripts/build-corpus-index.py` on annotated WZB
- Verify WZB appears in playground search
- Test lemma search with known WZB words

## File Inventory

| File | Role | Phase |
|------|------|-------|
| `Wenzelsbibel/WZB.tei.xml` | The file being annotated | All |
| `Wenzelsbibel/WB-DEA/*.xml` | Source reference (orig/norm forms, standOff) | Reference |
| `authority-files/lexicon.xml` | Lemma ID lookup | 1, 2 |
| `authority-files/variants.xml` | Normalized form → lemma mapping | 1 |
| `authority-files/concepts.xml` | Semantic concepts for meaningRef | 3 |
| `authority-files/works.xml` | Needs WZB entry added | Pre-req |
| `scripts/wzb-auto-match.py` | Auto-matching script (to be built) | 1 |

## Estimated Effort

| Phase | Estimated effort | Bottleneck |
|-------|-----------------|------------|
| Pre-requisites | 1-2 hours | Script development |
| Phase 1 (auto-match) | 2-4 hours | Script + reviewing report |
| Phase 1b (LLM disambiguation) | 1-2 weeks | Human review of LLM suggestions |
| Phase 2 (POS tagging) | 1-2 weeks | LLM batches + spot-checking |
| Phase 3 (meaningRef + wordRef) | TBD | Deferred |

## Open Questions

1. **Genre for WZB in works.xml** — Which `genres.xml` ID to use?
2. **Lexicon gaps** — When words aren't in the lexicon, do we create a separate "pending additions" list for Alan/the team to review?
3. **CoReMA is separate** — Issue #34 also mentions CoReMA texts, but they are a distinct corpus with different characteristics. This plan is WZB-specific. Lessons learned here may inform a future CoReMA pipeline, but that's not guaranteed.
4. **Index rebuild** — After annotation, WZB needs to be moved to `tei/` and indexes rebuilt. This is Christian's task, not Julia's.

## References

- [MHDBDB POS Tag Set](../DATA-MODEL.MD) — Full tag definitions
- [Variant Resolution](../ARCHITECTURE.MD) — 3-stage matching algorithm
- [MHG Normalization](../../assets/js/lib/text-normalizer.js) — Canonical normalization rules
- [Wörterbuchnetz API](https://api.woerterbuchnetz.de) — BMZ/Lexer for cross-referencing
- [WB-DEA Project](https://gams.uni-graz.at/context:wbdea) — Source edition
