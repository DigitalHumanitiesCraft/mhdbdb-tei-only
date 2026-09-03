# POS tagset

The canonical reference for the part-of-speech tagset (`@pos`) of the MHDBDB TEI texts: the normative 19-tag target schema, the rules for compound tags, the legacy tags still present in the older stock, and the actual distribution in the corpus.

This is the **single source of truth** for the `@pos` values. The operational disambiguation workflow that goes with it (LLM-assisted resolution of compound and wrong tags) is implemented as an agent skill under `.gemini/skills/pos-disambiguator/`; it uses this tagset but does not define it.

> **Audience:** this file is a technical reference specification, meant primarily for development and automated tools (precise, machine-oriented).

## 1. The 19-tag target schema

Every annotated `<w>` element carries exactly one tag from this set (exception: documented morphological fusions, see §2).

> **Note:** `ART` is **not** a valid tag. Articles (*der, diu, daz, ein*) are tagged `DET`. `ART` in the stock is legacy and is being migrated (see §3).

| Tag | Name | Examples |
|-----|------|-----------|
| **NOM** | noun | acker, zît, minne |
| **NAM** | proper name | Uolrîch, Wiene, Rhîn, sant (before names) |
| **ADJ** | adjective | grôz, schoene, guot, wâr |
| **ADV** | adverb | schône, vil, sêre, gar, als/wie (comparative) |
| **DET** | determiner | der, diu, daz, ein, diser, jener, kein, dekein, dehein |
| **POS** | possessive pronoun | mîn, dîn, unser |
| **PRO** | pronoun | ich, ez, wir, relative pronouns, swer (indefinite) |
| **PRP** | preposition | ûf, zuo, under, durch |
| **NEG** | negation | nie, niht, nit, nich, nieht, ne, en, âne |
| **NUM** | numeral | zwô, drî, zweinzegest |
| **CNJ** | conjunction (general) | the fallback under ambiguity (danne additive) |
| **SCNJ** | subordinating conjunction | daz (subordinate clause), ob, swenne, sît, als (temporal) |
| **CCNJ** | coordinating conjunction | und, oder, aber, ouch, noch |
| **IPA** | interrogative particle | wie (question), war (where to?), swer (interrogative) |
| **VRB** | full verb | liuhten, varn, machen; haben/sîn/werden (lexical) |
| **VEX** | auxiliary verb | haben/sîn/werden (with a past participle) |
| **VEM** | modal verb | müezen, suln, kunnen |
| **INJ** | interjection | ahî, owê |
| **DIG** | numeral (Roman) | IX, XVII, III |

The detailed linguistic distinctions (DET against PRO, VRB against VEX, the context-dependent *als/wie*, MHG negation patterns and so on) live in the disambiguation skill (`.gemini/skills/pos-disambiguator/SKILL.md`).

## 2. Compound tags

In the older stock many `<w>` elements (~35 to 40 %) carry space-separated compound values (e.g. `pos="VRB VEX"`, `pos="ADJ ADV"`) expressing an unresolved ambiguity. **The standard rule:** the disambiguation workflow resolves them to a single tag depending on context.

**Exception:** genuine morphological fusions keep two tags and receive a `reason` attribute:

| Fusion | Example | Tags | `reason` |
|--------|----------|------|----------|
| verb plus enclitic pronoun | *wiltu* = wilt + du | `VEM PRO` | `wilt+du` |
| verb plus enclitic pronoun | *färbs* = färbe + ez | `VRB PRO` | `färbe+ez` |
| preposition plus determiner | *zer* = ze + der | `PRP DET` | `ze+der` |
| preposition plus determiner | *zem* = ze + dem | `PRP DET` | `ze+dem` |

## 3. Legacy tags (older stock)

The stock taken over from the RDF migration partly uses an older tagset. These tags are **not** part of the 19-tag schema and are being migrated:

| Legacy | Target | Action |
|--------|------|--------|
| `ART` | `DET` | batch rename (articles are determiners) |
| `CNJ` (coordinating) | `CCNJ` | context-dependent (needs linguistic analysis) |
| `CNJ` (subordinating) | `SCNJ` | context-dependent (needs linguistic analysis) |
| `GRA` | *dropped* | merges into `ADJ` (gradation and superlative are ADJ) |

`CNJ` stays valid in the 19 set as a general fallback tag, but the bulk of the `CNJ` occurrences in the stock is not yet differentiated into `CCNJ`/`SCNJ`.

Besides that there are scattered non-canonical leftovers from the migration (`-`, `KOKOM`, `FM`, `PTK`, `X` and the typo `SCJN` for `SCNJ`), which are normalized during disambiguation.

## 4. Distribution in the corpus

**Measured 2026-09-02** over all 667 corpus files: `@pos` carries a non-empty value on **7,581,206** of the 9,431,311 `<w>` elements, **80.4 %**. The table below counts **atomic tag occurrences**: compound values are split at the spaces, so a token `pos="ADJ ADV"` counts once under `ADJ` and once under `ADV`. The sum therefore exceeds the number of tokens; here it is 10,019,248.

**Two numbers that are both right, so state which one you mean.** 14,941 `<w>` carry a `@pos` attribute whose value is empty (`pos=""`). Counting the attribute's presence gives 7,596,147, counting non-empty values gives 7,581,206, and the difference is exactly those 14,941. This table is built on the non-empty count, because an empty value contributes no tag to it. (The empty attributes are a corpus observation, not a documented policy; nothing here says whether they should be removed.)

The earlier figure in this section, 7,406,168 (79.8 %), was an audit value from 2026-04 measured over **666** files, before the WZB ingest. It also cited "TEI-MODEL.md §10" for its date and method, where no `@pos` row has ever stood: that framing lives in [TEI-MODEL.md §4.1](TEI-MODEL.md#41-attributes), which states the 666-file basis explicitly.

| Tag | Occurrences (atomic) | Status |
|-----|-------------------:|--------|
| VRB | 1,537,294 | 19 set |
| NOM | 1,520,028 | 19 set |
| ADV | 1,362,356 | 19 set |
| **ART** | 1,064,439 | legacy → DET |
| ADJ | 1,030,127 | 19 set |
| CNJ | 943,199 | 19 set (the bulk still to be differentiated into CCNJ/SCNJ) |
| PRP | 659,800 | 19 set |
| PRO | 658,741 | 19 set |
| VEX | 223,279 | 19 set |
| NEG | 204,786 | 19 set |
| NAM | 194,319 | 19 set |
| POS | 150,663 | 19 set |
| VEM | 133,064 | 19 set |
| NUM | 116,967 | 19 set |
| **GRA** | 60,278 | legacy → ADJ |
| IPA | 59,061 | 19 set |
| DET | 53,443 | 19 set |
| INJ | 22,071 | 19 set |
| CCNJ | 13,805 | 19 set |
| SCNJ | 7,371 | 19 set |
| DIG | 4,061 | 19 set |
| `-` 47, KOKOM 39, FM 5, PTK 3, SCJN 1, X 1 | 96 in total | leftovers → normalization |

The dominance of `ART` (over 1 million) and the low `DET` value (53k) show that the ART to DET migration still concerns the bulk of the stock. The most frequent compound values are `ADJ ADV` (304,069), `ART CNJ` (271,352) and `VRB VEX` (206,440).

Against the previous table (the 2026-04 audit) 12 of the 21 tags are unchanged to the token and 9 moved. Two of those nine are worth naming: `DIG` fell by 722, which is the margin numerals removed in #138, and `NOM` rose by 11,483, **+0.761 %**, which is the WZB ingest and not noise. The other seven moved by less than a tenth of a percent (`VRB` +1,356 is the largest of them at +0.088 %).

> **Reproduction.** Count only `<w>` **inside `<body>`**, split the value at spaces, drop empty segments. That is the boundary `build-corpus-index.py` counts on (CONTRACTS §B), and the project's Python/JS parity rule hangs on it.
>
> The one-liner given here previously was `grep -rhoE 'pos="[^"]*"' tei/ | …`, which takes every `@pos` in the document, on any element and inside or outside `<body>`. Measured 2026-09-02, both rules return **the same** numbers, tag for tag, because today no `@pos` sits outside `<body>` and none sits on an element other than `<w>`. That is a property of the current data, not of the rules, so prefer the narrow one: it stays correct if an ingest ever annotates a header.
>
> The numbers are a snapshot and shift as disambiguation proceeds and new texts come in.

## 5. Disambiguation

Resolving compound tags, correcting wrong tags and the ART/CNJ/GRA migration do not happen mechanically but depend on context, through semantic and grammatical analysis. The workflow provided for this is implemented as the agent skill `.gemini/skills/pos-disambiguator/` (phases: split → analysis → merge → validation → refinement). Teaching examples of ambiguities (*daz*, *als*, *haben*) live under `.gemini/skills/pos-disambiguator/references/examples.md`.

## 6. Disambiguation and migration policy (#27)

The binding policy for moving the older stock (compound tags, legacy tags, known misannotations) into the 19-tag schema of §1. It makes the workflow plannable: what is migrated in which order, what the LLM decides on its own, what needs a sample review, and what stays put until KZW decides. No part of this policy changes the tagset itself.

### 6.1 Levels of obligation

| Level | Meaning |
|-------|-----------|
| **P-MUSS** | no batch is committed without it |
| **P-SOLL** | deviation is allowed, give the reason in the provenance log |
| **P-OFFEN** | an explicit decision by KZW is needed, until then the status quo holds |

### 6.2 Migration classes and their order

The classes are sorted by how far they can be automated, in descending order, and are worked through in that order; every class is a batch of its own that can be checked independently (its own branch and PR, its own provenance log).

| Class | Stock (atomic, §4) | Procedure | Level |
|--------|---------------------:|-----------|-------|
| K1: leftovers (`-`, KOKOM, FM, PTK, X, SCJN) | < 100 | a deterministic table (SCJN→SCNJ; for the rest a case-by-case list in the PR) | P-MUSS, deterministic |
| K2: ART → DET | 1,064,439 | batch rename, NO context needed (articles are DET by the definition in §1) | P-MUSS, deterministic |
| K3: GRA → ADJ | 60,278 | batch according to §3 (gradation and superlative are ADJ) | P-MUSS, deterministic; the deviation in the issue body („GRA→ADV/PART") is OLD, see 6.5 |
| K4: compound resolution (ADJ ADV, VRB VEX, ART CNJ, …) | ~35 to 40 % of the tokens | LLM, context-dependent (the skill workflow), EXCEPT genuine fusions (§2: they stay two-valued plus `@reason`) | P-MUSS, LLM plus the gates in 6.3 |
| K5: CNJ → CCNJ/SCNJ | 943,199 | LLM, context-dependent; CNJ stays allowed as a fallback under genuine ambiguity | P-SOLL (fallback allowed) |
| K6: known misannotation patterns (issue §2: enhaben, wiest, morphology as a second tag, unifying NEG, NAM overreach) | scattered | LLM with a watch list (the skill's „Known Error Patterns") | P-MUSS, LLM plus the gates in 6.3 |

Why that order: K1 to K3 are context-free and shrink the problem space measurably (over 1.1 million atomic old tags) before the expensive LLM classes run; K4 before K5, because many CNJ cases sit inside compounds (ART CNJ: 271k) and would otherwise be touched twice.

### 6.3 Quality gates (for K4 to K6, P-MUSS)

1. **Batch size:** at most 1 text per LLM run unit; the output is a diff list (xml:id, old, new, reason, confidence).
2. **Golden set:** before the first K4 batch, 200 manually verified cases (KZW and students) across all classes; every change of model or prompt is first measured against the golden set (target ≥ 95 % agreement) and only then put to use. (This applies to the LLM classes K4 to K6 only; the deterministic K1 to K3 need no golden set.)
3. **Sample review:** 50 random cases per batch plus ALL cases with confidence='low' go to human checking; an error rate above 5 % discards the batch and the prompt or model is readjusted.
4. **Invariants (automatic, CI-capable):** (a) only tags from §1 (plus the documented fusions of §2), (b) token text, order and xml:id byte-identical (only `@pos`, `@comp`, `@needsSplit`, `@reason` change), (c) position counting unchanged (an index rebuild is diff-free apart from the expected pos fields), (d) no ART, GRA or leftover in the output.
5. **Provenance:** one log per batch under `ingest/pos-disambig/<batch>/` (model, prompt version, date, diff statistics, review result); a revisionDesc change entry per file. (Deliberately a third kind of path under `ingest/`: `scripts/ingest/<sigle>/` carries pipeline scripts, `ingest/<sigle>/` raw sources per text, `ingest/pos-disambig/` campaign review logs.)

### 6.4 Technical attributes (from KZW's decision of 2025-11-20)

- Contractions and fusions: the token stays ONE `<w>`; genuine morphological fusions carry two tags plus `@reason` (§2); in addition `@comp="VRB+PRO"` and `@needsSplit="true"` where the decomposition is analytically wanted. NO token splits in the edition. **Caveat:** `@comp` and `@needsSplit` are NOT yet in `schema/mhdbdb.rnc` (the `<w>` production does not allow them) and do not occur in the corpus so far. Before the first K4 batch the schema has to be extended (or a GAP documented), otherwise the CI schema validation breaks.
- NEG: for negation particles only (*niht, ne, en, n, nie* …); carriers of negation from another part of speech get ONLY their part of speech (*dehein* → DET, *nieman* → PRO, *nie* → ADV). Existing combinations such as `ADJ|NEG` are resolved in K6.
- Foreign-language material: NOT through `@pos` but through `@xml:lang` (plus an optional `<foreign>`), see the phase plan in #28; out of scope for the POS migration.

### 6.5 Resolved discrepancies and open points

**Resolved (the policy follows the tagset decision of 2025-11-20, that is §1):**
- ART is not a tag (the table in issue §3 was an interim state) → K2.
- PART is NOT in the 19 set (issue §5 named it as a candidate; the fixed list does not contain it). Particles of particle verbs are tagged ADV until further notice; see the next point.
- GRA → ADJ (the issue body said ADV in one place and PART in another; §3 of this file is the single source of truth).
- **No 20th tag PART** (KZW's decision of 2026-07-08, #27): particles of particle verbs are marked by convention as ADV plus `@ana`. A technical constraint before implementing this: `@ana` is already taken as a sense reference (`lexicon.xml#lemma_{N}_sense_{M}`, see DATA-MODEL.md → Phase 3: sense resolution), so the POS marking needs a value schema of its own that can be told apart from it (to be fixed before the first K4 batch, in the same way as the `@comp`/`@needsSplit` caveat in 6.4).
- **Double tagging is admissible for contractions** (KZW's decision of 2026-07-08, #27): genuine MHG contraction words, two lemmata drawn together into one token for economy of speech (*wiltu* = wilt + du), keep two tags (§2). What is expressly NOT meant are ordinary compounds (*hûsmûs* is simply NOM). This confirms the §2 exception as policy.

**P-OFFEN (a decision by KZW is needed, but it does NOT block the class as a whole):**
1. **The remaining CNJ share:** „undifferentiated CNJ" means tokens that still carry the unspecific `CNJ` after the K5 campaign instead of `CCNJ`/`SCNJ`, that is, exactly the cases where the context too does not decide whether they coordinate or subordinate (which answers KZW's question of 2026-07-08 in the affirmative). The open question: how much of that is acceptable as a K5 fallback? Proposal: ≤ 10 % of the original CNJ amount (943,199 tokens, so ≤ ~94,000).
2. **Finalize the list of fusion pairs:** the principle is decided (see above), what stays open is the final list of admissible tag pairs, in particular whether modal verb contractions such as *wiltu* are tagged `VEM PRO` (as in §2) or generically `VRB PRO`.

### 6.6 Expressly NOT part of this policy

No pilot run, no corpus change, no token campaign within #27 (scope decision by chsteiner on 2026-07-03). This policy is the template from which future campaign issues (one per class) are set up. #18 (data migration) depends on K1 to K3.

## Cross-references

- [TEI-MODEL.md §5](TEI-MODEL.md) – `@pos` in the normative TEI target model
- [DATA-MODEL.md](DATA-MODEL.md) – `@pos` in the annotation data model and in the backfill pipeline
- `.gemini/skills/pos-disambiguator/SKILL.md` – the operational disambiguation workflow and the linguistic rules for telling tags apart
