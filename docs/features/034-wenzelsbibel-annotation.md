#Issue # 034 — Wenzelsbibel Annotation Pipeline

**Issue:** #34 (Ingest neue Texte: WB, dann CoReMA)
**Status:** Planning
**Owner:** Julia (@juliahin)
**Support:** Chris (@chsteiner)

## Schema History

This document was written incrementally during the Wenzelsbibel ingest. The MHDBDB schema evolved in parallel, which means some encodings agreed upon early in the project were later superseded. The table below records those changes so that the decisions in this doc can be read in their correct context.

| Changed element | Old encoding (used during work) | Correct encoding (per final schema) | Phase affected |
| --- | --- | --- | --- |
| Non-lexical punctuation / scribal marks | `<seg type="pc">` | `<pc join="left\|right">` | Phase 1b paratext cleanup |
| Genre link in works.xml | `<ref target="genres.xml#...">` | `<ptr target="genres.xml#..."/>` | Pre-requisite |
| Manuscript shelfmark in works.xml | `<note type="manuscript">` | `<idno type="shelfmark">` | Pre-requisite |
| Article POS tag | `ART` | `DET` | Phase 2 (tagset migration applied via patch, commit cf71ae48) |

Where the old encoding was written into `WZB.tei.xml` or `authority-files/`, it has since been corrected. This doc now reflects the final schema (`schema/mhdbdb.rng`, `schema/mhdbdb-authority.rng`).

---

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
| Unique word forms (text content of `<w>`) | ~4,900 (Genesis alone) |
| MHDBDB lexicon entries | 43,750 |
| MHDBDB variant forms | 192,674 |
| POS tag set | PRO, VRB, NOM, ADJ, ADV, DET, CNJ, PRP, VEX, POS, NAM, NUM (can be space-separated for multi-tag) |

## Phased Plan

### Phase 1: Auto-Match lemmaRef (script-assisted)

**Goal:** Assign `@lemmaRef` to as many words as possible using the existing MHDBDB lexicon and variant mappings.

**Approach:**
1. Extract all unique word forms from `WZB.tei.xml` (the **text content** of each `<w>` element is the matching form — during transformation, the WB-DEA `@norm` value was written as text content; there is no `@norm` attribute in WZB.tei.xml itself)
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

**Important caveat — MHG normalization:** The MHDBDB uses a specific normalization scheme (`â→a, ê→e, î→i, ô→o, û→u, ä→ae, ö→oe, ü→ue`; see `assets/js/lib/text-normalizer.js`). Verified status:

- **`variants.xml`**: Contains 34,149 forms with special characters (â, ê, î, ô, û, ä, ö, ü) — **NOT pre-normalized**
- **`WZB.tei.xml`**: Contains **zero** special characters — word forms use manuscript-level normalization (e.g. "herczen" not "hêrzen")

The matching script **must** apply MHDBDB normalization (via `scripts/mhg_normalizer.py`) to **both** the variant forms and the WZB word forms before comparing. The Python normalizer has parity tests against the JS version (`testing/tests/normalization-parity.spec.js`).

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

**Output format:** Phase 1b produces a TSV file (`wzb-disambiguation.tsv`) with columns:

| Column | Description |
|--------|-------------|
| `xml_id` | `<w>` element ID (e.g. `WZB_1ra_6_5`) |
| `form` | Word form as it appears in WZB |
| `context` | Surrounding 5-word window |
| `match_type` | `ambiguous` or `unmatched` |
| `candidate_lemmas` | Pipe-separated lemma IDs from Phase 1 (empty for unmatched) |
| `resolved_lemma` | Final lemma ID after LLM/human review (or `NEW`) |
| `confidence` | `high` / `medium` / `low` |
| `reviewer` | `claude` or `julia` |

The TSV is generated automatically from the Phase 1 CSV report using `scripts/wzb-generate-tsv.py`.  This ensures the columns stay in sync with whatever `wzb-auto-match.py` emits; rerun the script whenever the report is refreshed.  The Python script writes the file to `Wenzelsbibel/wzb-disambiguation.tsv` and populates only the first six fields (including a new `count` column), leaving the last three blank for human/LLM review.

A companion helper (`scripts/wzb-split-tsv.py`) can split the
versioned TSV into smaller chunks (default 50 rows) to make Claude
prompting easier.  Run:

```bash
python scripts/wzb-split-tsv.py --input Wenzelsbibel/wzb-disambiguation.tsv
# or specify a different size:
python scripts/wzb-split-tsv.py -s 30
```

This creates `<basename>-partNN.tsv` files alongside the input.**Escalation:** Words marked `confidence=low` by Claude are reviewed by Julia. Words marked `NEW` are collected in a separate list for the editorial team (not added to `lexicon.xml` in this phase).

### Editorial workflow for new forms

Unmatched forms from Phase 1 are not simply discarded; they form the
basis of a pending additions list for the lexicon editorial team.  After
running the auto-match script you can generate a frequency-sorted file
with `scripts/wzb-extract-unmatched.py`:

```bash
python scripts/wzb-extract-unmatched.py
# => Wenzelsbibel/wzb-unmatched-forms.tsv
```

The TSV contains each unique unmatched form, its count of occurrences,
and a few sample contexts.  Editors can use this to prioritise which
lemmas to create and then feed the new lemma IDs back into the Phase 1b
TSV (in the `resolved_lemma` column) once they have been added to
`lexicon.xml`.

This keeps the pipeline closed-loop: auto-match → disambiguate →
publish new forms for editorial intake → reuse updated lexicon in next
run.

**Coverage target:** Best-effort with existing lexicon. Unmatched words are flagged in the report but NOT added to `lexicon.xml` in this phase (that requires a separate editorial decision).

### Phase 1b Disambiguation Workflow (actual)

After running Phase 1 auto-match, `wzb-disambiguation.tsv` contained **72,358** ambiguous/unmatched token rows. The following tiered workflow was agreed upon for resolving them, ordered by impact and tractability.

Current coverage (as of batch 40): 89.5% resolved (64,732 / 72,358)

#### Token population breakdown

| Population | Forms | Tokens | Strategy |
| --- | --- | --- | --- |
| Ambiguous — high freq (21+ tokens) | 6 forms | ~260 | Tier 1: bulk resolve now |
| Ambiguous — mid/low freq (2–20) | 66 forms | ~500 | Tier 2: Claude proposes, Julia spot-checks |
| Ambiguous — hapax (count = 1) | 263 forms | 263 | Tier 3: deferred |
| Unmatched — mid freq (6–20) | 12 forms | ~150 | Tier 4: flag NEW or resolve via Wörterbuchnetz |
| Unmatched — long tail (1–5) | 3,803 forms | ~5,400 | Tier 5: deferred |

#### Tier 1 — Bulk resolve (Claude, now)

High-frequency ambiguous forms where the dominant reading is clear from context patterns across all five books. Claude produces a `wzb-resolutions-batchNN.tsv` (form-level) plus a `wzb-patch-batchNN.tsv` for minority exceptions, applied via `wzb-bulk-resolve.py` + `wzb-patch-rows.py`.

Current Tier 1 targets: `mer`, `fur`, `fure`, `wegen`, `wert`, `weise`.

#### Tier 2 — Context-by-context review (Claude proposes, Julia spot-checks)

Mid- and low-frequency ambiguous forms (2–20 token occurrences) that genuinely split between readings depending on sentence context — e.g. `herte` can be ADJ "hard", NOM "heart", VRB "to harden", or NAM "shepherd". Claude reads every instance, proposes a per-instance resolution with a confidence rating, and writes a patch file. Julia reviews all `confidence=low` rows and a random 20% sample of `confidence=medium` rows before applying.

#### Tier 3 — Hapax ambiguous (deferred)

263 ambiguous forms each occurring exactly once. Per-instance resolution is the only option but the ROI is low (263 patches for 263 tokens, each requiring lexicon lookup). Deferred until after Phase 2 unless a form is philologically significant.

#### Tier 4 — Unmatched mid-frequency (flag NEW or resolve)

~12 forms with 6–20 occurrences that are genuine MHG words not in the MHDBDB lexicon (e.g. `scot`, `erstlinge`, `humeral`, `hebreer`, `keuchel`). Two sub-strategies:

- Claude cross-references BMZ/Lexer via the [Wörterbuchnetz API](https://api.woerterbuchnetz.de) and proposes a headword + lemma ID if the word can be found
- If not resolvable: mark `resolved_lemma = NEW` → collected in the editorial additions list for the lexicon team

#### Tier 5 — Unmatched long tail (deferred)

~3,800 forms with 1–5 occurrences. These are mostly: orthographic variants with normalization gaps, rare biblical proper nouns, Latin inflections within Vulgate quotations, or compound forms. Deferred — accepted as residual coverage gap. May be revisited after a future lexicon enrichment pass.

#### Special token categories (resolved inline)

Two additional categories were identified during Phase 1b and resolved as complete batches before the tier workflow above:

- **Scribal/structural marks** (batches 39–40, resolved): `ł`, `-`, `̃`, `჻`, `=`, `؞` → `lemma_2`; Roman numeral chapter apparatus (`U`, `XU`, `UII`, `I`–`VI` etc.) → `lemma_13826`; Latin running headers split mid-word across folios (`GENE`+`SIS`, `EXO`+`DUS`, `LEUITICUS`, `ERI`, `DEUTRO`+`NOMIUS`, `GEN`+`ESIS`, `CAPITULUM`, `LIBER`, `S`) → `lemma_2`
- **Old Czech/Bohemian glosses** (flagged, pending): `toho`, `thoho`, `pzde`, `bzde`, `؞` — marginal glosses in Old Czech interspersed in the Exodus/Numbers sections, reflecting the manuscript's production context for Wenceslas IV. Separate GitHub issue to be created. Will be resolved to `lemma_2` as non-MHG paratextual content.

#### Tooling

| Script | Purpose |
| --- | --- |
| `scripts/wzb-bulk-resolve.py` | Apply form-level resolutions to disambiguation TSV |
| `scripts/wzb-patch-rows.py` | Apply per-xml_id corrections (minority exceptions) |
| `scripts/wzb-pending-review.py` | Regenerate `wzb-pending-review.tsv` from current TSV state |
| `Wenzelsbibel/wzb-resolutions-batchNN.tsv` | Form-level resolution files (one per batch) |
| `Wenzelsbibel/wzb-patch-batchNN.tsv` | Per-row correction files (one per batch, where needed) |

### Phase 2: POS Tagging (LLM-assisted)

**Goal:** Assign `@pos` to every `<w>` element.

**Approach:**
1. For words with `@lemmaRef` from Phase 1: inherit POS from `lexicon.xml` entry **only if the entry has exactly one `<pos>` element** in its `<gramGrp>`. If a lemma has multiple `<pos>` elements (e.g. `lemma_722` has both `NOM` and `VRB`), the word is flagged for LLM-assisted disambiguation — the correct POS depends on sentence context.
2. For remaining words (no `@lemmaRef`, or multi-POS lemma): LLM-assisted tagging in batches via Claude Code

**Prompt template:**

```
Assign POS tags to these Middle High German words from the Wenzelsbibel.
Use MHDBDB tag set: PRO VRB NOM ADJ ADV DET CNJ PRP VEX POS NAM NUM
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
  <idno type="shelfmark">Wien, ÖNB, Cod. 2759-2764</idno>
  <ptr target="genres.xml#genre_93f5fac5"/>
  <author ref="persons.xml#person_anonym">Anonym</author>
</bibl>
```

**Resolved:** Genre is **Bibelübersetzung** (`genre_93f5fac5`) — the Wenzelsbibel is a prose translation of the Vulgate, not verse poetry.

### 2. Build the auto-match script

Python script: `scripts/wzb-auto-match.py`

Input: `Wenzelsbibel/WZB.tei.xml` + `authority-files/variants.xml` + `authority-files/lexicon.xml`
Output: Annotated WZB with `@lemmaRef` where unambiguous + CSV report of ambiguous/unmatched words

### 3. Verify word form coverage in WZB.tei.xml

Some WB-DEA source words had `norm=""` (empty). During transformation, these may have produced `<w>` elements with empty text content. These need to be identified and handled:
- If the WB-DEA source has `@orig` for the corresponding word: use it as fallback
- If both were empty: flag for manual review
- The auto-match script should skip empty `<w>` elements and report them separately

## Git Workflow

All annotation work happens on the `feature/wenzelsbibel-ingest` branch. Each phase produces a separate commit to enable rollback and review:

| Phase | Commit message pattern | What changes |
|-------|----------------------|--------------|
| Pre-req | `Add WZB to works.xml` | `authority-files/works.xml` |
| Phase 1 | `WZB: auto-match lemmaRef (N% coverage)` | `Wenzelsbibel/WZB.tei.xml` + match report |
| Phase 1b | `WZB: resolve ambiguous/unmatched lemmaRef` | `Wenzelsbibel/WZB.tei.xml` + disambiguation TSV |
| Phase 2 | `WZB: assign POS tags` | `Wenzelsbibel/WZB.tei.xml` |

**Rules:**
- Phase 1b corrections are **additive** — they never overwrite Phase 1 unambiguous matches
- The auto-match script (`wzb-auto-match.py`) is committed separately from its output
- The disambiguation TSV (`wzb-disambiguation.tsv`) is committed alongside the annotated XML for audit trail
- After all phases: PR into `main`, then Chris moves WZB to `tei/` and rebuilds indexes

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
| `scripts/mhg_normalizer.py` | MHG text normalization (Python, parity with JS) | 1 |
| `scripts/wzb-auto-match.py` | Auto-matching script (to be built) | 1 |

## Estimated Effort

| Phase | Estimated effort | Bottleneck |
|-------|-----------------|------------|
| Pre-requisites | 1-2 hours | Script development |
| Phase 1 (auto-match) | 2-4 hours | Script + reviewing report |
| Phase 1b (LLM disambiguation) | TBD after Phase 1 report | Depends on ambiguous/unmatched count — refine after auto-match |
| Phase 2 (POS tagging) | TBD after Phase 1b | Depends on multi-POS lemma ratio — refine after Phase 1b |
| Phase 3 (meaningRef + wordRef) | TBD | Deferred |

## Open Questions

1. ~~**Genre for WZB in works.xml**~~ — **Resolved:** `genre_93f5fac5` (Bibelübersetzung)
2. **Lexicon gaps** — When words aren't in the lexicon, do we create a separate "pending additions" list for Alan/the team to review?
3. **CoReMA is separate** — Issue #34 also mentions CoReMA texts, but they are a distinct corpus with different characteristics. This plan is WZB-specific. Lessons learned here may inform a future CoReMA pipeline, but that's not guaranteed.
4. **Index rebuild** — After annotation, WZB needs to be moved to `tei/` and indexes rebuilt. This is Christian's task, not Julia's.

---

## Paratext Encoding Decisions (Issue #66)

During Phase 1b disambiguation, ~1,500 `<w>` elements were identified as non-lexical manuscript elements. The following decisions were made and implemented via `scripts/wzb-structural-cleanup.py` (2026-04-07).

### General Principle

> Structural elements are encoded in TEI but excluded from lexical annotation. Only linguistically relevant tokens enter the lemmatisation pipeline. When necessary, new lemmata are created rather than using a generic fallback.

### Decision Table

| Category | Examples | Count | TEI encoding | Lemma treatment |
| -------- | -------- | ----- | ----------- | --------------- |
| **Book headers** (running headers in `<fw>`) | GENESIS, EXODUS, LEUI+TICUS, GENE+SIS | 909 `<w>` in 905 `<fw>` | Already `<fw type="header">` — strip `@lemmaRef`/`@pos` | None — not lexical |
| **PROLOGUS** | PROLOGUS | 6 `<w>` in `<fw>` | Already `<fw type="header">` — strip annotation attrs | None — treated as book header |
| **Chapter apparatus** | CAPITULUM + Roman numeral | 106 CAPITULUM `<w>` + adjacent numerals | `<head type="chapter" n="N">` as first child of `<div type="chapter">`; `<milestone unit="chapter" n="N"/>` inline in `<l>` | None — not lexical |
| **Scribal section initials** | S, O, a, A (single-letter paragraph marks) | ~6 | Convert `<w>` → `<pc join="left">` | None |
| **Pure scribal marks** | ł, -, ̃, ჻, =, ؞, ׀, ⫶ | ~654 | Convert `<w>` → `<pc join="left">` | None |
| **Roman numerals** (inline) | UIII, XU, XLU, XXUII (U=V in WZB script) | 16 | Keep as `<w>` | `lemma_13826` (DIG, concept_31422100 Römische Ziffern + concept_23123100 Lateinisch) |
| **Latin words** | Et, et (conjunction); est (verbal form of esse) | 6 | Keep as `<w>` | `Et`/`et` → `lemma_1732` (CNJ); `est` → `lemma_9387` (VEX, esse) |
| **Czech glosses** | toho, thoho, pzde, bzde, kde | ~115 | Keep as `<w>` | `lemma_78628` (cs, NOM; concept_23123610 Tschechisch + concept_90000000 Funktionswörter) |
| **Surplus elements** | Scribat, cap̄, ̄, . XX . c | 11 | Already in `<surplus>` — strip annotation attrs | None |

### Implementation Notes

- **CAPITULUM position**: The chapter number appears either before or after CAPITULUM in the manuscript (e.g. "III CAPITULUM" and "CAPITULUM XIII" both occur). The script collects all adjacent Roman numeral `<w>` siblings (within 4 positions in the same `<l>`) and combines them. The `@n` attribute receives the Arabic equivalent (`U=V`).
- **`<head type="chapter">` placement**: Initially inserted inline within the existing `<l>` element (by `wzb-structural-cleanup.py`). Subsequently corrected by `wzb-structural-fix.py` (2026-04-13): `<head>` is now a direct first child of its `<div type="chapter">` (TEI P5 conformant), and a `<milestone unit="chapter" n="N"/>` is inserted at the original text-flow position inside the `<l>`. The `@n` attribute is recomputed with a space-tolerant roman_to_arabic converter (fixes "I X" → IX = 9 etc.).
- **`<fw>` words**: Book header tokens are *already* inside `<fw type="header">` in the source TEI. The cleanup only removes incorrectly assigned `@lemmaRef`/`@pos` attributes — no structural change to the `<fw>` elements.
- **Roman numeral notation**: WZB uses `U` for `V` throughout (Bohemian scribal convention). `UIII`=VIII, `XU`=XV, `XLU`=XLV etc. The `@n` attribute on `<head type="chapter">` stores the correct Arabic numeral.
- **Latin `et`/`Et`**: Mapped to `lemma_1732` (existing CNJ lemma with concept_23123100 Lateinisch). Occurs in direct Vulgate quotations embedded in the German translation (e.g. "Fiat lux Et facta est").
- **Czech glosses**: Mapped to `lemma_78628` (new lemma created in Phase 1b batch40, orth=`cs`). These are Old Czech/Bohemian interlinear glosses from the bilingual manuscript context of Wenceslas IV.

### Script Reference

```bash
# Structural cleanup (TEI modification)
python scripts/wzb-structural-cleanup.py --dry-run
python scripts/wzb-structural-cleanup.py

# Lemma assignments for Roman numerals and Latin words
python scripts/wzb-bulk-resolve.py --resolutions Wenzelsbibel/wzb-resolutions-batch-paratext.tsv
```

**Result (2026-04-07):** 149,154 `<w>` elements (down from 150,017); 106 `<head type="chapter">`; 35,473 `<seg type="pc">`.

---

## Structural Fix — Div Types and Head Placement (2026-04-13)

A second structural pass corrected two issues in the WB-DEA chapter division encoding.

### Issue 1: Unnamed chapter divs

The WB-DEA transformation produced 213 `<div>` elements with `type=""` and `xml:id` values like `Genesis.1`, `Exodus.12`, `Josua.24`. These represent biblical chapters and require `@type="chapter"` for schema conformance and query disambiguation.

**Fix:** 212 divs updated to `<div type="chapter">`. (The remaining unnamed div is a pre-Genesis transition wrapper.)

### Issue 2: `<head type="chapter">` inside `<l>` — TEI-invalid

`wzb-structural-cleanup.py` placed `<head type="chapter">` elements inside `<l>` elements (where the scribal CAPITULUM tokens were in the text flow). TEI P5 does not allow `<head>` as a child of `<l>`; it must be a direct child of a block container such as `<div>`.

**Fix:** `wzb-structural-fix.py` moves each `<head type="chapter">` to be the first child of its target `<div type="chapter">`, and replaces the former inline position with `<milestone unit="chapter" n="N"/>`.

**Target div selection:**

- By `@n` value: `<head type="chapter" n="5">` → `<div xml:id="Deuteronomium.5">` (preferred)
- By "next sibling" fallback: bare CAPITULUM (no numeral) → first `<div type="chapter">` sibling after the containing div
- Final fallback: bare CAPITULUM in last chapter of book → containing div itself (Josua.24)

**Result (2026-04-13):**

- 212 `<div type="chapter">` elements (was 0)
- 106 `<head type="chapter">` now TEI-conformant (direct `<div>` children)
- 106 `<milestone unit="chapter">` at original text-flow positions
- 0 `<head>` remaining inside `<l>`

```bash
python scripts/wzb-structural-fix.py --dry-run
python scripts/wzb-structural-fix.py
```

---

## Encoding Cleanup (2026-04-13)

Four targeted fixes applied via `scripts/wzb-encoding-cleanup.py`.

### Fix 1 — Historiated initials

6 `<w>` elements inside `<hi rend="initial_historisiert">` were decorative first letters of words split across the TEI (e.g. `I` + `n` = "In", `U` + `nd` = "Und"). They were incorrectly annotated: one as DIG/lemma_13826 (Roman numeral), five as NOM/lemma_2. All converted to `<pc join="left">`, consistent with other section initials.

### Fix 2 — Josua.0 misclassified as chapter

`<div xml:id="Josua.0">` sits at body level between `<div type="paratext" id="Transition6">` and `<div type="book" id="Josua">`. It contains introductory Joshua text (21 words). `wzb-structural-fix.py` had incorrectly assigned it `type="chapter"` (the `Josua.0` xml:id matched the `BookName.N` pattern). Fixed: `type="paratext"`, `xml:id="JosuaPrologus"`. The `wzb-structural-fix.py` regex was also corrected to require N ≥ 1.

### Fix 3 — Transition2.1 type normalised

`<div type="Transition2.1" xml:id="Transition2.1">` used an ad-hoc type string. Fixed: `type="paratext"`.

### Fix 4 — Unnamed prologus body div

`<div type="" xml:id="">` inside `<div type="prologus">` (914 `<w>` elements, the main prologue text body) had no type or xml:id. Fixed: `type="section"`, `xml:id="Prologus.1"`.

**Result (2026-04-13):**

| div type | before | after |
| -------- | ------ | ----- |
| `chapter` | 212 | 211 |
| `paratext` | 10 | 12 |
| `prologus` | 1 | 1 |
| `section` | 0 | 1 |
| `book` | 6 | 6 |
| unnamed | 1 | 0 |

```bash
python scripts/wzb-encoding-cleanup.py --dry-run
python scripts/wzb-encoding-cleanup.py
```

---

## References

- [MHDBDB POS Tag Set](../DATA-MODEL.MD) — Full tag definitions
- [Variant Resolution](../ARCHITECTURE.MD) — 3-stage matching algorithm
- [MHG Normalization (JS)](../../assets/js/lib/text-normalizer.js) — Canonical normalization rules
- [MHG Normalization (Python)](../../scripts/mhg_normalizer.py) — Python parity implementation for build scripts
- [Wörterbuchnetz API](https://api.woerterbuchnetz.de) — BMZ/Lexer for cross-referencing
- [WB-DEA Project](https://gams.uni-graz.at/context:wbdea) — Source edition
