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

The Wenzelsbibel (WZB) has been structurally transformed from WB-DEA source into MHDBDB-conformant TEI (`Wenzelsbibel/WZB.tei.xml`, Phase 1). The ~150,000 `<w>` elements currently have only text content — no `@lemmaRef`, `@pos`, `@ana`, or `@corresp` attributes. Without these, the text cannot participate in MHDBDB search, lemma highlighting, or concept navigation.

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
   ana="lexicon.xml#lemma_722_sense_1177"
   pos="VRB"
   corresp="variants.xml#type_2239">bitte</w>
```

### What WZB currently has

```xml
<w xml:id="WZB_1ra_6_5">herczen</w>
```

### Gap

Every `<w>` needs: `@lemmaRef`, `@pos`. Later also: `@ana`, `@corresp`.

## Data Profile

| Metric | Value |
|--------|-------|
| Total `<w>` elements | ~150,000 |
| Source files (WB-DEA) | 5 |
| Unique word forms (text content of `<w>`) | ~4,900 (Genesis alone) |
| MHDBDB lexicon entries | 43,750 |
| MHDBDB variant forms | 175,910 |
| POS tag set | PRO, VRB, NOM, ADJ, ADV, DET, CCNJ, SCNJ, PRP, VEX, POS, NAM, NUM, NEG, IPA, VEM, INJ, DIG (19-tag MHDBDB set) |

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

The TSV is generated automatically from the Phase 1 CSV report using `scripts/ingest/wzb/wzb-generate-tsv.py`.  This ensures the columns stay in sync with whatever `wzb-auto-match.py` emits; rerun the script whenever the report is refreshed.  The Python script writes the file to `Wenzelsbibel/wzb-disambiguation.tsv` and populates only the first six fields (including a new `count` column), leaving the last three blank for human/LLM review.

A companion helper (`scripts/ingest/wzb/wzb-split-tsv.py`) can split the
versioned TSV into smaller chunks (default 50 rows) to make Claude
prompting easier.  Run:

```bash
python scripts/ingest/wzb/wzb-split-tsv.py --input Wenzelsbibel/wzb-disambiguation.tsv
# or specify a different size:
python scripts/ingest/wzb/wzb-split-tsv.py -s 30
```

This creates `<basename>-partNN.tsv` files alongside the input.**Escalation:** Words marked `confidence=low` by Claude are reviewed by Julia. Words marked `NEW` are collected in a separate list for the editorial team (not added to `lexicon.xml` in this phase).

### Editorial workflow for new forms

Unmatched forms from Phase 1 are not simply discarded; they form the
basis of a pending additions list for the lexicon editorial team.  After
running the auto-match script you can generate a frequency-sorted file
with `scripts/ingest/wzb/wzb-extract-unmatched.py`:

```bash
python scripts/ingest/wzb/wzb-extract-unmatched.py
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
| `scripts/ingest/wzb/wzb-bulk-resolve.py` | Apply form-level resolutions to disambiguation TSV |
| `scripts/ingest/wzb/wzb-patch-rows.py` | Apply per-xml_id corrections (minority exceptions) |
| `scripts/ingest/wzb/wzb-pending-review.py` | Regenerate `wzb-pending-review.tsv` from current TSV state |
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
Use MHDBDB tag set (19 tags): NOM NAM ADJ ADV DET POS PRO PRP NEG NUM
  CNJ SCNJ CCNJ IPA VRB VEX VEM INJ DIG
Multiple tags allowed (space-separated) when word is genuinely ambiguous.
Prefer SCNJ/CCNJ over CNJ; prefer NEG over PRO for niht/nie/ne; use DIG
for Roman numerals (WZB notation: U=V, e.g. UIII=VIII).

Context: [2-3 lines of surrounding text]
Words: [batch with positions]
```

**Auto-assignment rules (no LLM needed):**
- If lemma's `<gramGrp>/<pos>` has exactly one POS value → assign it
- Common patterns: `der/die/daz` → DET, `und/vnd/oder` → CCNJ, `in/an/mit` → PRP

**QA:** Script validates that assigned POS is in the MHDBDB tag set. Julia spot-checks ~5% per chapter.

### Phase 3: Word Sense Disambiguation — @meaningRef + @wordRef (MHDBDB extensions)

**Goal:** Assign `@meaningRef` and `@wordRef` to every annotated `<w>` element, achieving full MHDBDB conformance with semantic concept links and variant form references. The Wenzelsbibel serves as the first controlled testcase for LLM-assisted word sense disambiguation (WSD) in the MHDBDB pipeline — approximately one third of the entire MHDBDB corpus currently lacks these attributes.

**Note on attribute naming:** The production MHDBDB corpus uses `@ana` (TEI-conformant, format `lexicon.xml#lemma_{ID}_sense_{SENSE_ID}`) and `@corresp` (format `variants.xml#type_{TYPE_ID}`) for sense and variant references. WZB uses the planned MHDBDB extension attributes `@meaningRef` and `@wordRef` (same data, different names) which are allowed by `schema/mhdbdb.rnc` (Stage 2) but fail TEI P5 `tei_all.rng` (Stage 1) — a documented trade-off (see `schema/README.md` GAP 15). Both conventions refer to the same underlying lexicon/variants data.

**Research context:** Phase 3 is the subject of a doctoral research project (Hintersteiner, ongoing). The pipeline described below constitutes both the engineering contribution and the empirical testbed for evaluating LLM-assisted WSD on Middle High German historical texts.

#### Attribute formats

| Attribute | Format | Example |
| --- | --- | --- |
| `@meaningRef` | `lexicon.xml#lemma_{ID}_sense_{SENSE_ID}` | `lexicon.xml#lemma_722_sense_1177` |
| `@wordRef` | `lexicon.xml#lemma_{ID}_sense_{SENSE_ID}_type_{TYPE_ID}` | `lexicon.xml#lemma_722_sense_1177_type_2239` |

#### Lexicon sense statistics (as of 2026-04)

| Sense count | Entries | Proportion | Treatment |
| --- | --- | --- | --- |
| 0 senses | 4 | < 0.1% | Skip — flag for editorial review |
| 1 sense | 35,985 | 82.3% | Auto-assign |
| 2+ senses | 7,765 | 17.7% | LLM disambiguation |
| Total | 43,754 | | |

Note: token frequency skews toward high-frequency polysemous words (pronouns, verbs, common nouns), so the proportion of *tokens* requiring disambiguation is substantially higher than the 17.7% of entry types.

#### Step 1 — Auto-assign single-sense lemmata (`wzb-sense-assign.py`)

For every `<w>` with `@lemmaRef` pointing to a lemma with exactly one `<sense>`:

- Set `@meaningRef` to that sense ID
- Attempt `@wordRef` auto-resolution: look up the word form in `variants.xml`; if the matching variant type appears in the sense's `@ana` attribute list, set `@wordRef`
- Emit remaining multi-sense tokens to `Wenzelsbibel/phase3/wzb-sense-pending.tsv`

#### Step 2 — LLM sense disambiguation

**Pending TSV schema:**

| Column | Description |
| --- | --- |
| `xml_id` | `<w>` element ID |
| `form` | Word form as it appears in WZB |
| `lemmaRef` | Existing `@lemmaRef` value |
| `pos` | Existing `@pos` value |
| `context` | Surrounding 10-word window (5 left, 5 right) |
| `candidate_senses` | Pipe-separated: `sense_id :: concept_label_DE (concept_label_EN)` |
| `resolved_sense` | Sense ID chosen by LLM/human — filled during review |
| `confidence` | `high` / `medium` / `low` |
| `reviewer` | `claude` / `julia` |

**Sense label construction:** Each `<sense>` in `lexicon.xml` links to one or more concepts via `<ptr target="concepts.xml#concept_..."/>`. The `concepts.xml` `<catDesc>` provides `<term xml:lang="de">` and `<term xml:lang="en">` labels. These are concatenated as the human-readable sense description presented to the LLM.

**Prompt template:**

```
You are disambiguating word senses in a Middle High German biblical text (Wenzelsbibel, ca. 1390).
The word has already been lemmatised. Your task is to choose which sense of the lemma applies
given the sentence context.

Lemma: {orth} | POS: {pos}
Word form in text: {form}
Context: ... {left_context} **{form}** {right_context} ...

Available senses:
{sense_id_1}: {concept_labels_1}
{sense_id_2}: {concept_labels_2}
...

Reply with exactly one sense ID and a confidence level (high/medium/low).
Format: SENSE_ID | CONFIDENCE
```

**Batching:** Use `wzb-split-tsv.py` (adapted for phase3 input) to produce 50-row batches. Julia reviews all `confidence=low` decisions and a 20% random sample of `confidence=medium`.

#### Step 3 — Apply resolutions (`wzb-sense-bulk-resolve.py`, `wzb-sense-apply.py`)

- `wzb-sense-bulk-resolve.py`: writes resolved sense IDs back to `wzb-sense-pending.tsv`
- `wzb-sense-apply.py`: reads the resolved TSV, writes `@meaningRef` to TEI; also attempts `@wordRef` auto-resolution for each resolved token

#### Step 4 — `@wordRef` resolution

Once `@meaningRef` is known, `@wordRef` can often be auto-assigned:

1. Look up the word form in `variants.xml` → get candidate type IDs
2. Intersect with the sense's `@ana` type list
3. If exactly one match: assign `@wordRef = "lexicon.xml#{sense_id}_type_{type_id}"`
4. If zero matches: word form not in variants.xml → flag for editorial additions list
5. If multiple matches: flag for manual review (rare)

#### Evaluation design (research component)

The Wenzelsbibel pipeline also serves as an empirical evaluation of LLM-assisted WSD quality. A subset of already-annotated MHDBDB texts provides a gold standard. **Gold standard provenance:** MHDBDB `@meaningRef`/`@wordRef` annotations are human-annotated — not automated — making them a valid reference for inter-annotator agreement style evaluation.

---

#### Pre-registered evaluation protocol (2026-04-24)

This section is written before evaluation is run, constituting a pre-registration to support scientific reproducibility.

**Research question:** Does LLM-assisted (bulk + per-instance) WSD on Middle High German historical text exceed the majority-sense baseline (66.7% weighted accuracy, computed from 675 MHDBDB corpus files)?

**Null hypothesis:** LLM pipeline accuracy ≤ majority-sense baseline accuracy on the held-out sample.

##### Sample design

| Parameter | Value | Rationale |
| --- | --- | --- |
| Minimum N | **400 tokens** | Power analysis: two-tailed binomial test, H₀=66.7%, target detect δ≥8pp at α=0.05, power=0.80 requires ~380 tokens; round to 400 |
| Recommended N | **600 tokens** | Allows 2×3 subgroup analysis (sense count × POS) with ≥50 tokens per cell |
| Source | Already-annotated MHDBDB texts (excl. WZB) | Gold standard is pre-existing human annotation |
| Sampling frame | All `<w>` with `@lemmaRef` pointing to lemmata with 2+ senses | Mirrors pending TSV scope |

##### Stratification grid

Sample is drawn proportionally across the following 6 cells (sense count × POS):

| | NOM | VRB | ADJ/ADV/PRP |
|---|---|---|---|
| 2 senses | ≥50 | ≥50 | ≥50 |
| 3–5 senses | ≥50 | ≥50 | ≥50 |
| 6+ senses | ≥50 | ≥50 | ≥50 |

Within each cell: stratified random sample across at least 3 different lemmata (to avoid single-lemma dominance inflating accuracy).

##### Gold standard handling

1. Extract stratified sample from corpus, recording `xml_id`, `form`, `lemmaRef`, `meaningRef`, `context`
2. Strip `@meaningRef` and `@wordRef` from the sample copy — LLM sees only `form` + `context` + candidate senses, never the gold label
3. Run through Phase 3 pipeline (same `wzb-sense-bulk-resolve.py` / per-instance flow, same prompts, `--decision-type instance-llm`)
4. Compare LLM `resolved_sense` against gold `meaningRef` fragment

##### Baseline

**Majority-sense baseline: 66.7%** (computed 2026-04-24 from 675 MHDBDB corpus files via `wzb-sense-baseline.py`). The baseline TSV is at `Wenzelsbibel/phase3/wzb-sense-majority-baseline.tsv`.

**Genre mismatch caveat (for publication):** The 66.7% baseline is computed from the full MHDBDB corpus, which covers mixed genres (mystical prose, epic poetry, didactic literature, etc.). The Wenzelsbibel is biblical prose — an OT translation exhibiting higher lexical consistency, more monosemous usage of high-frequency content words, and fewer metaphorical extensions than mixed-genre secular literature. This means the majority-sense heuristic likely performs *better* on WZB than the 66.7% figure suggests. The baseline is therefore a **conservative lower bound** for comparison: if LLM accuracy exceeds 66.7%, the true advantage over a WZB-specific majority-sense baseline may be smaller. Report this comparison as: *"LLM pipeline accuracy of X% vs. mixed-genre majority-sense baseline (66.7%); a genre-matched biblical-prose baseline was not computed."*

##### Primary metric

**Sense accuracy** = proportion of sample tokens where `resolved_sense` matches gold `meaningRef` fragment (exact match on sense ID). Reported overall and per stratum.

##### Secondary metrics

- **Accuracy by decision type**: `bulk-llm` vs `instance-llm` — tests whether bulk decisions (applied uniformly per lemma) match instance-level decisions (per-token context)
- **Accuracy by ambiguity level**: 2-sense / 3–5-sense / 6+-sense
- **Accuracy by POS**: NOM / VRB / ADJ+ADV+PRP
- **Confidence calibration**: `high`-confidence accuracy vs `medium`-confidence accuracy (Brier score for probabilistic calibration if confidence is converted to p)
- **ABSTAIN rate**: proportion of tokens where LLM abstained rather than choosing a sense; excluded from accuracy denominator but reported separately
- **@wordRef hit rate**: proportion of correctly resolved senses where `@wordRef` could be auto-assigned (diagnostic for variants.xml coverage)

##### Blind review protocol (Julia's spot-checks)

To maintain evaluator blindness for the scientific record, Julia's manual spot-checks follow this procedure:

1. Generate review sheet: for each sampled token, show `form`, `context`, `candidate_senses` — **without** the `resolved_sense` column visible
2. Julia records her own sense choice independently (her call is the inter-annotator reference)
3. Only after recording: reveal `resolved_sense` (LLM choice) and gold label
4. Document: LLM correct? Julia correct? LLM == Julia? Disagreement analysis

This produces three-way agreement data (LLM / Julia / gold), supporting inter-annotator agreement reporting (Cohen's κ between LLM and human annotator).

##### Decision type taxonomy (for scientific record)

All resolutions in `wzb-sense-pending.tsv` carry a `decision_type` column:

| Value | Meaning |
| --- | --- |
| `auto-single` | Single-sense lemma — trivially correct by definition; **excluded from WSD accuracy** |
| `bulk-llm` | LLM chose one sense for all tokens of a lemma without per-instance context |
| `bulk-human` | Human chose one sense for all tokens of a lemma |
| `instance-llm` | LLM chose sense per individual token with context |
| `instance-human` | Human chose sense per individual token |
| `abstain` | Principled abstention — context insufficient for disambiguation; excluded from TEI output and accuracy denominator |

**Reporting distinction:** `bulk-llm` accuracy and `instance-llm` accuracy are reported separately, since bulk decisions assume distributional uniformity while instance decisions use per-token evidence. Scientific comparison to baseline should use `instance-llm` only (apples-to-apples with majority-sense baseline which is also a distributional prior).

##### Tooling

| Script | Purpose |
| --- | --- |
| `scripts/ingest/wzb/wzb-sense-assign.py` | Step 1: auto-assign single-sense; generate pending TSV |
| `scripts/ingest/wzb/wzb-sense-bulk-resolve.py` | Step 2: apply batch resolutions (bulk or per-instance) |
| `scripts/ingest/wzb/wzb-sense-apply.py` | Step 3: write @meaningRef / @wordRef to TEI; reports ABSTAIN counts separately |
| `scripts/ingest/wzb/wzb-sense-baseline.py` | Compute majority-sense baseline from annotated MHDBDB corpus |
| `scripts/_archived/wzb/wzb-sense-migrate-schema.py` | One-time: add decision_type + model_id columns to pending TSV |
| `scripts/ingest/wzb/wzb-sense-evaluate.py` | Compare LLM output against gold standard corpus sample; two modes: `sample` (extract stratified gold + stripped pending TSV) and `evaluate` (compute accuracy, Brier score, Cohen's κ, stratum breakdown) |

---

### Phase 3 Progress (as of 2026-04-21)

#### Pipeline commands

```bash
# Step 1 — auto-assign single-sense + generate pending TSV (run once)
python scripts/ingest/wzb/wzb-sense-assign.py [--dry-run]

# Step 2 — bulk-resolve a lemma (all tokens of one lemma → one sense)
python scripts/ingest/wzb/wzb-sense-bulk-resolve.py -r Wenzelsbibel/phase3/resolutions/wzb-sense-batchNN.tsv [--dry-run]

# Step 2b — per-instance patch (individual xml_id overrides)
python scripts/ingest/wzb/wzb-sense-bulk-resolve.py -r <patch.tsv> --by xml_id [--dry-run]

# Step 3 — write @meaningRef / @wordRef to TEI (run after each batch round)
python scripts/ingest/wzb/wzb-sense-apply.py [--dry-run]
```

#### Resolution file formats

**Bulk (lemma-level)** — `Wenzelsbibel/phase3/resolutions/wzb-sense-batchNN.tsv`:

```
lemmaRef    resolved_sense          confidence  note
lexicon.xml#lemma_905   lemma_905_sense_1489    high    OT has no monks; all blood-brother
```

**Patch (xml_id-level)** — same columns but with `xml_id` instead of `lemmaRef`:

```
xml_id          resolved_sense          confidence  note
WZB_12ra_5_3    lemma_2684_sense_4322   medium      refers to Pharaoh, not God
```

#### Step 1 results (auto-assign, 2026-04-21)

| Result | Count | % of 149,148 |
| --- | --- | --- |
| Auto-assigned `@meaningRef` (single-sense) | 102,559 | 68.8% |
| Auto-assigned `@wordRef` (form match) | 67,839 | 45.5% |
| Pending — multi-sense (→ TSV) | 39,418 | 26.4% |
| Skipped — no `@lemmaRef` (Phase 1b residual) | 6,974 | 4.7% |
| Skipped — 0 senses (new Phase 1b lemmata) | 197 | 0.1% |

The 197 zero-sense tokens belong to the 4 lemmata added during Phase 1b (`lemma_78628` cs, `lemma_78648` herte, `lemma_78668` scot, `lemma_78688` weise) which have no `<sense>` entries yet.

#### Pending TSV distribution (39,418 rows, 854 unique lemmata)

| Sense count | Rows | % |
| --- | --- | --- |
| 2 senses | 7,220 | 18.3% |
| 3 senses | 10,136 | 25.7% |
| 4 senses | 6,048 | 15.3% |
| 5 senses | 6,055 | 15.4% |
| 6–9 senses | 8,456 | 21.4% |
| 10+ senses | 1,503 | 3.8% |

**POS distribution of pending tokens:** NOM 36% · VRB 24% · PRP 16% · VEX 10% · ADJ 5% · VEM 5%

**Coverage concentration:** Top 10 lemmata = 36.8% of pending tokens; top 100 = 77.6% — strongly Zipfian.

#### Bulk resolutions applied (batches 01–05, 2026-04-21)

| Batch | Lemmata | Tokens | Key decisions |
| --- | --- | --- | --- |
| 01 | `bruder` | 264 | `_sense_1489` blood-brother; OT has no monks |
| 02 | `herre`, `svn`, `opfer` | 3,055 | Lord=God (`_sense_4323`); blood-son (`_sense_9315`); OT sacrifice (`_sense_31702`) |
| 03 | 11 lemmata | 1,269 | `seine` possessive, `hous` domestic, `hin` spatial, `erste` ordinal, `golde` material, `vortilgen` destroy, `menedis` month-as-time, `stimme` voice, `brvnne` well, `hercze` theological-heart, `wasche` laundry |
| 04 | 19 lemmata | 613 | `ruche` fragrance, `gepurt` birth, `treten` step, `gelt` money, `gestalt` shape, `segen` OT blessing, `silber` material, `lenge` spatial-length, `legerten` military-encamp, `engel` angel, `breite` width, `koufen` buy, `milch` dairy, `pflage` plague, `eingange` entrance, `gehorsam` obedience, `hie` here, `vorbrante` burning, `gesalbet` ritual-anoint |
| 05 | 8 lemmata | 2,169 | `machen` make/craft, `gebieten` command, `mensch` human, `mitte` spatial-middle, `ochsen` ox, `gewant` clothing, `fride` peace/covenant, `was/waren` existential-be |
| **Total** | **~40 lemmata** | **7,370** | — |

#### Current TEI coverage (after applying batches 01–05)

| Attribute | Count | Coverage |
| --- | --- | --- |
| `@meaningRef` | 109,929 | **73.7%** |
| `@wordRef` | 71,228 | **47.8%** |

#### Remaining work — 32,048 rows

The bulk-resolvable pool is largely exhausted. Remaining rows require per-instance disambiguation:

| Lemma | Tokens | Senses | Note |
| --- | --- | --- | --- |
| `in` (lemma_3028) | 3,585 | 3 | temporal / spatial / relational |
| `haben` (lemma_2598) | 2,132 | 8 | auxiliary / possessive / modal |
| `werden` (lemma_7489) | 1,987 | 5 | future / passive-aux / become |
| `an` (lemma_199) | 967 | 3 | directional / temporal / relational |
| `sollen` (lemma_5608) | 954 | 4 | obligation / future / modal |
| `noch` (lemma_4415) | 742 | 2 | adversative / temporal |
| `ziehen` (lemma_7861) | 553 | 16 | complex polysemy |
| `gehen` (lemma_1844) | 546 | 8 | motion senses |
| ... | ... | ... | ~840 more lemmata |

**Next step:** Split `wzb-sense-pending.tsv` into 50-row batches (by highest-frequency lemma first) and run per-instance LLM disambiguation via `--by xml_id` patches.

## Pre-Requisites (before Julia starts)

### 1. Register WZB in works.xml

Add a new entry to `authority-files/works.xml`:

```xml
<bibl xml:id="work_WZB">
  <title xml:lang="de">Wenzelsbibel</title>
  <title xml:lang="en">Wenceslas Bible</title>
  <idno type="sigle">WZB</idno>
  <ptr target="genres.xml#genre_93f5fac5"/>
  <author ref="persons.xml#person_anonym">Anonym</author>
</bibl>
```

**Resolved:** Genre is **Bibelübersetzung** (`genre_93f5fac5`) — the Wenzelsbibel is a prose translation of the Vulgate, not verse poetry.

### 2. Build the auto-match script

Python script: `scripts/ingest/wzb/wzb-auto-match.py`

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
- No `<w>` elements have `@ana` without `@lemmaRef` (dependency order)
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
| `authority-files/concepts.xml` | Semantic concepts for @ana | 3 |
| `authority-files/works.xml` | Needs WZB entry added | Pre-req |
| `scripts/mhg_normalizer.py` | MHG text normalization (Python, parity with JS) | 1 |
| `scripts/ingest/wzb/wzb-auto-match.py` | Auto-matching script (to be built) | 1 |

## Estimated Effort

| Phase | Estimated effort | Bottleneck |
|-------|-----------------|------------|
| Pre-requisites | 1-2 hours | Script development |
| Phase 1 (auto-match) | 2-4 hours | Script + reviewing report |
| Phase 1b (LLM disambiguation) | TBD after Phase 1 report | Depends on ambiguous/unmatched count — refine after auto-match |
| Phase 2 (POS tagging) | TBD after Phase 1b | Depends on multi-POS lemma ratio — refine after Phase 1b |
| Phase 3 (ana + corresp) | TBD | Deferred |

## Open Questions

1. ~~**Genre for WZB in works.xml**~~ — **Resolved:** `genre_93f5fac5` (Bibelübersetzung)
2. **Lexicon gaps** — When words aren't in the lexicon, do we create a separate "pending additions" list for Alan/the team to review?
3. **CoReMA is separate** — Issue #34 also mentions CoReMA texts, but they are a distinct corpus with different characteristics. This plan is WZB-specific. Lessons learned here may inform a future CoReMA pipeline, but that's not guaranteed.
4. **Index rebuild** — After annotation, WZB needs to be moved to `tei/` and indexes rebuilt. This is Christian's task, not Julia's.

---

## Paratext Encoding Decisions (Issue #66)

During Phase 1b disambiguation, ~1,500 `<w>` elements were identified as non-lexical manuscript elements. The following decisions were made and implemented via `scripts/ingest/wzb/wzb-structural-cleanup.py` (2026-04-07).

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
python scripts/ingest/wzb/wzb-structural-cleanup.py --dry-run
python scripts/ingest/wzb/wzb-structural-cleanup.py

# Lemma assignments for Roman numerals and Latin words
python scripts/ingest/wzb/wzb-bulk-resolve.py --resolutions Wenzelsbibel/wzb-resolutions-batch-paratext.tsv
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
python scripts/ingest/wzb/wzb-structural-fix.py --dry-run
python scripts/ingest/wzb/wzb-structural-fix.py
```

---

## Encoding Cleanup (2026-04-13)

Four targeted fixes applied via `scripts/ingest/wzb/wzb-encoding-cleanup.py`.

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
python scripts/ingest/wzb/wzb-encoding-cleanup.py --dry-run
python scripts/ingest/wzb/wzb-encoding-cleanup.py
```

---

## References

- [MHDBDB POS Tag Set](../DATA-MODEL.md) — Full tag definitions
- [Variant Resolution](../ARCHITECTURE.md) — 3-stage matching algorithm
- [MHG Normalization (JS)](../../assets/js/lib/text-normalizer.js) — Canonical normalization rules
- [MHG Normalization (Python)](../../scripts/mhg_normalizer.py) — Python parity implementation for build scripts
- [Wörterbuchnetz API](https://api.woerterbuchnetz.de) — BMZ/Lexer for cross-referencing
- [WB-DEA Project](https://gams.uni-graz.at/context:wbdea) — Source edition
