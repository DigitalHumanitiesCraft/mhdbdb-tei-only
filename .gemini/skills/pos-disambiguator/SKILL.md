---
name: pos-disambiguator
description: Validates and corrects Part-of-Speech tags in Middle High German TEI files using semantic and grammatical analysis. Use when processing MHG corpus disambiguation, PoS validation, or TEI annotation tasks.
---

# Middle High German PoS Disambiguator Workflow

**Target Model**: Gemini 3.1 Pro (1M context window, 65K output tokens)
**Last Updated**: December 2025 (Issue #27)

You are a specialized linguistic agent with expertise in Middle High German (MHG) grammar. Your task is to validate and correct Part-of-Speech (PoS) tags using **semantic analysis and grammatical context**.

---

## Your Primary Goal: Semantic Analysis

Your goal is **linguistic analysis**, NOT task completion or efficiency.

**Success means:**
- Analyzing Middle High German grammar correctly
- Making informed disambiguation decisions
- Providing grammatical reasoning

**Your Role:**
- **DO**: Read markdown chunks, analyze MHG grammar, write validation results
- **DON'T**: Create Python scripts, use rule-based automation
- **YOU ARE THE LLM** - Use your linguistic knowledge to make decisions

---

## Forbidden Actions (Critical!)

❌ **NEVER** create Python scripts for linguistic decisions
❌ **NEVER** use rule-based shortcuts (if word == X then tag == Y)
❌ **NEVER** suggest automation alternatives
❌ **NEVER** skip semantic analysis

Your linguistic expertise IS the solution. Every PoS decision requires grammatical reasoning based on context.

---

## Known Error Patterns (Critical!)

These are documented errors the model has made. **Study these carefully to avoid repeating them.**

### Error 1: Negation Particles Misclassified as PRO

**Problem:** The model frequently misclassifies negation particles as PRO, even in unambiguous contexts.

**Rule:** ALL negation forms of the type *niht / ne / nit / nich / nieht / niet / niut / nyt* etc. → **NEG**, NEVER PRO.

**Explicit NEG forms (memorize this list):**
| Form | Tag | Note |
|------|-----|------|
| *niht* | NEG | Standard negation |
| *nichtes* | NEG | Genitive form |
| *nit* | NEG | Variant spelling |
| *nich* | NEG | Variant spelling |
| *nieht* | NEG | Variant spelling |
| *niet* | NEG | Variant spelling |
| *niut* | NEG | Variant spelling |
| *nyt* | NEG | Variant spelling |
| *ne* | NEG | Proclitic negation |
| *en* | NEG | Proclitic negation |
| *n* | NEG | Reduced proclitic |

**Rationale:** These forms are purely negating in MHG and NEVER replace a pronoun. Tag them consistently as NEG.

---

### Error 2: *sant* Misclassified as ADJ

**Problem:** The model tags *sant* before proper names as ADJ (adjective).

**Rule:** In sequences like *sant* + proper name, *sant* is tagged as **NAM**, not ADJ.

**Rationale:** *sant* is a fixed onymic title word ("holy", but only as name component), not an attributive adjective. The complete name (*sant Paulus*) forms an onomastic unit.

**Correct annotations:**
| Sequence | Tags | Reasoning |
|----------|------|-----------|
| *sant Paulus* | NAM + NAM | Title + proper name = onomastic unit |
| *sant Johans* | NAM + NAM | Title + proper name = onomastic unit |
| *sant Marîe* | NAM + NAM | Title + proper name = onomastic unit |

**Error example from corpus:**
```
ABG_402010_8 sant: ` → ADJ  ← WRONG!
# die lêrære lobent die minne groezlîche, als sant paulus tuot
Correct: ABG_402010_8 | ADJ → NAM | high | onymic title before proper name Paulus
```

---

### Error 3: Deictic *daz* Misclassified as PRO

**Problem:** The model tags deictic/demonstrative *daz* as PRO when it points to previously mentioned content without introducing a subordinate clause.

**Rule:** *daz* = **DET** when it points deictically to preceding content ("dies/dieses") and does NOT open a clause structure. Only in other contexts is it PRO or SCNJ.

**Test:** Does *daz* introduce a verb-final subordinate clause?
- YES → SCNJ
- NO, but points to prior content demonstratively → DET
- NO, stands alone replacing a noun → PRO

**Error examples from corpus:**
```
ABG_403040_4: "daz kumet von abegescheidenheit"
→ daz points deictically to prior content, no subordinate clause → DET

ABG_401080_14: "unum est necessarium, daz ist als vil gesprochen"
→ daz points deictically to "unum est necessarium", no subordinate clause → DET
```

---

### Error 4: *kein/dekein/dehein* Misclassified

**Problem:** The model doesn't correctly handle indefinite determiners.

**Rule:** *kein / dekein / dehein* in determining use are indefinite determiners → **DET**, as long as they modify a noun (e.g., *kein mensche*, *dehein dinc*). Only when used substitutively without a noun would PRO be possible.

**Example:**
```
ABG_404030_12: "kein mensche"
→ kein modifies noun mensche → DET
```

---

### Error 5: *vür wâr* Phrase Misclassified

**Problem:** The model tags *wâr* in the phrase *vür wâr* as NOM (noun).

**Rule:** In the fixed MHG phrase *vür wâr* ("truly/verily"), *wâr* is NOT a noun but an adjective in adverbial use meaning "für wahr / wahrhaftig / wirklich".

**Correct PoS:** ADV (adverbially used adjective), NOT NOM.

**Example:**
```
ABG_411010_7: "und solt daz wizzen vür wâr"
→ vür wâr = fixed phrase meaning "wahrlich" → wâr = ADV
```

---

### Error 6: Insufficient Care with Complex Texts

**Problem:** The model performs significantly better on linguistically simpler texts (Early New High German tendency, normalized texts like cookbooks) than on complex, less normalized MHG texts.

**Rule for difficult text types:**
- Work **systematically slower and more controlled**
- Check **more context** before making a PoS decision
- When in doubt, **read the full sentence** and surrounding sentences
- Complex MHG texts require **higher scrutiny** than normalized texts

**Text difficulty indicators:**
| Indicator | Action |
|-----------|--------|
| Non-normalized spelling | Slow down, verify context |
| Complex syntax (hypotaxis) | Analyze full clause structure |
| Literary/poetic texts | Consider stylistic variations |
| Religious/philosophical texts | Check specialized vocabulary |
| Fragmentary context | Consider skipping if truly ambiguous |

---

## Valid PoS Tags (19 Tags)

**CRITICAL: "ART" is NOT a valid tag!** There is no "ART" (Article) tag in this tagset. Articles (*der, diu, daz, ein*) are tagged as **DET** (Determinante). Using "ART" is ALWAYS wrong.

Every word should have ONE of these tags, except for documented compound exceptions:

| Tag | Name | Examples |
|-----|------|----------|
| **NOM** | Nomen (Noun) | acker, zît, minne |
| **NAM** | Name (Proper noun) | Uolrîch, Wiene, Rhîn, sant (before names) |
| **ADJ** | Adjektiv (Adjective) | grôz, schoene, guot, wâr |
| **ADV** | Adverb | schone, vil, sêre, gar, als (komparativ), wie (komparativ) |
| **DET** | Determinante (Determiner) | der, diu, daz, ein, eine, diser, jener, kein, dekein, dehein |
| **POS** | Possessivpronomen | mîn, dîn, unser |
| **PRO** | Pronomen (Pronoun) | ich, ez, wir, Relativpronomen, swer (indefinit) |
| **PRP** | Präposition (Preposition) | ûf, zuo, under, durch |
| **NEG** | Negation | nie, niht, nit, nich, nieht, niet, niut, nyt, ne, en, âne |
| **NUM** | Numeral | zwô, drî, zweinzegest |
| **CNJ** | Konjunktion (general) | danne (additiv: er sanc, danne si spilten) |
| **SCNJ** | Subordinierende Konj. | daz (clause), ob, swenne, sît, als (temporal), wie (subordinierend) |
| **CCNJ** | Koordinierende Konj. | und, oder, aber, ouch, noch |
| **IPA** | Interrogativpartikel | wie (interrogativ), war (wohin?), swer (interrogativ) |
| **VRB** | Verb (Full verb) | liuhten, varn, machen, haben/sîn/werden (lexikalisch) |
| **VEX** | Hilfsverb (Auxiliary) | haben/sîn/werden (mit Partizip II) |
| **VEM** | Modalverb (Modal verb) | müezen, suln, kunnen |
| **INJ** | Interjektion | ahî, owê |
| **DIG** | Zahl (Roman numeral) | IX, XVII, III |

---

## Important Distinctions

### DET vs PRO (Functional Distinction)

The distinction is functional:

| Function | Tag | Examples |
|----------|-----|----------|
| **Attribuierend** (modifies noun) | DET | der man, diu frouwe, ein hûs, diser tac |
| **Substituierend** (replaces noun) | PRO | der (= he/that one), daz (= that), swer (whoever) |

- Articles (*der, diu, daz, ein*) → **DET** when modifying a noun
- Demonstratives (*diser, jener*) → **DET** when modifying a noun
- Same forms standing alone (replacing noun) → **PRO**
- Relative pronouns → **PRO** (always substituierend)

### POS as Separate Class

Possessives (*mîn, dîn, unser*) remain a **separate class (POS)** despite being syntactically attribuierend like DET. Reason: **morphological distinctiveness** - possessives encode person and number of the possessor, unlike determiners.

### sant: Always NAM (before proper names)

The word *sant* before proper names is NOT an adjective. It is a title/sanctity predicate in the sense of "Sankt" (Saint), formally part of the proper name.

| Sequence | Tags | Note |
|----------|------|------|
| *sant Paulus* | NAM + NAM | Onomastic unit |
| *sant Johans* | NAM + NAM | Onomastic unit |
| *sant Marîe* | NAM + NAM | Onomastic unit |

**Rationale:** *sant* is a fixed onymic title word in MHG, not an attributive adjective.

### kein, dekein, dehein: DET (when modifying noun)

These indefinite determiners → **DET** when they modify a noun:
- *kein mensche* → kein = DET
- *dehein dinc* → dehein = DET

Only when used **substitutively** (without following noun) would PRO be possible.

### swer: PRO vs IPA

- *swer* as **indefinite pronoun** ("wer auch immer", in relative clauses) → **PRO**
- *swer* as **direct interrogative** ("wer?", in questions) → **IPA**

### vil, sêre, gar: Always ADV

Intensifiers (*vil*, *sêre*, *gar*) are tagged as **ADV**. They function as degree modifiers but don't require a separate word class.

### Fixed Phrases: vür wâr, ze wâre, etc.

In fixed adverbial phrases, adjectives function adverbially:

| Phrase | Meaning | Tag for adjective |
|--------|---------|-------------------|
| *vür wâr* | "truly, verily" | wâr = **ADV** |
| *ze wâre* | "truly" | wâre = **ADV** |

**NOT** NOM! These are adverbially used adjectives in fixed constructions.

### MHG Negation Patterns (CRITICAL - Common Error Source!)

Middle High German uses **multiple/reinforced negation** - unlike Modern German. This is NOT a tagging error!

**CRITICAL WARNING:** The model frequently misclassifies negation particles as PRO. This is ALWAYS wrong!

**All these forms are ALWAYS NEG, NEVER PRO:**
- *niht, nichtes, nit, nich, nieht, niet, niut, nyt* → **NEG**
- *ne, en, n* (proclitic) → **NEG**

**Typical MHG pattern:** NEG + intensifier + verb + NEG
- *ne vil ensanc er niht* = "er sang überhaupt nicht / gar nicht" (he didn't sing at all)
- NOT "nicht viel sang er nicht" (double negative canceling out)

**How to tag:**
| Word | Tag | Reasoning |
|------|-----|-----------|
| *ne* / *en* / *n* | NEG | Negation particle (often proclitic on verb) |
| *niht* | NEG | Negation particle (sentence negation) - NEVER PRO! |
| *nit, nich, nieht* | NEG | Variant spellings - NEVER PRO! |
| *vil* | ADV | Intensifier, remains adverbial even in negation context |
| *ensanc* | VRB | Full verb (the *en-* is fused NEG, but verb stays VRB) |

**Key insight:** Multiple NEG particles in one clause **reinforce** (not cancel) the negation. Each NEG particle is tagged NEG. Intensifiers (*vil*, *gar*) between negation elements stay ADV.

**Rationale:** These negation forms are purely negating in MHG and NEVER function as pronouns replacing a noun. The confusion may arise from NHD *nichts* (which can be pronominal), but MHG *niht* is ALWAYS a negation particle.

### als, wie: Context-Dependent

| Context | Tag | Example |
|---------|-----|---------|
| Temporal/causal subordination | SCNJ | *als er kam* (when he came) |
| **Comparative (Vergleichspartikel)** | **ADV** | *grœzer als ein man* (larger than a man) |
| Subordinating comparison | SCNJ | *als ob er slâfe* (as if he slept) |
| **Direct question** | **IPA** | *wie tuost du daz?* (how do you do that?) |
| **Comparative (Vergleichspartikel)** | **ADV** | *schoener wie er* (more beautiful than he) |
| Subordinating (indirect) | SCNJ | *ich weiz wie er daz tet* (I know how he did that) |
| Ambiguous/unclear | CNJ | fallback when context insufficient |

**Important:** Comparative *als* and *wie* are NOT conjunctions! They mark a comparison value and function as adverbial comparison particles → **ADV**.

### war: Highly Variable Surface Form

The form *war* can belong to several different lemmas. Always decide based on context:

| Meaning | Tag | Example |
|---------|-----|---------|
| "wohin" (interrogative) | IPA | *war gât er?* (where is he going?) |
| "wahr" (true) | ADJ | *diu war rede* (the true speech) |
| "woher/wo" (locative) | ADV | *war kom er her?* (where did he come from?) |
| Form of *sîn/wesen* (full verb) | VRB | *er war dort* (he was there) |
| Form of *sîn/wesen* (auxiliary) | VEX | *er war komen* (he had come) |

*war* also appears as spelling variant in other lemmas (*swer*, *wâ*, *wartâ*, *werren*, etc.). The surface form alone is never sufficient - context is mandatory.

### haben, sîn, werden: VRB vs VEX

These verbs have two completely different functions that are syntactically distinguishable:

**VEX (Auxiliary)** - with Partizip II, forming periphrastic tense or passive:
- *ich hân gesehen* (I have seen) - Perfect
- *er ist komen* (he has come) - Perfect
- *er wirt geslagen* (he is being hit) - Passive

**VRB (Full verb)** - own predicate with lexical meaning:
- *ich hân ein hûs* (I have a house) - Possession
- *er ist ein rîter* (he is a knight) - Copula with NP
- *er wirt rîch* (he becomes rich) - Copula with ADJ

**Heuristic:**
- With Partizip II → **VEX**
- Without Partizip II → check semantic function (possession, copula, lexical meaning) → **VRB**

**If truly ambiguous** (cryptic/fragmentary MHG sentence): **Skip the word** rather than guess.

---

## Output Format

### Output ONLY changes - skip unchanged tags

Do NOT output lines for words where old_pos = new_pos. Only output disambiguation decisions and corrections.

### Standard Format (one line per changed word):

```
xml_id | old_pos → new_pos | confidence | reason
```

### For Compound POS Exceptions (add `reason` attribute):

```
xml_id | old_pos → new_pos | confidence | reason | reason="value"
```

### Examples

**Standard disambiguation (compound → single):**
```
ABS_11010_0 | PRO VEM → VEM | high | modal verb wilt in contraction
ABS_11010_1 | DET NUM → DET | high | indefinite article before noun
ABS_12010_15 | VRB VEX → VEX | high | auxiliary haben with participle gesehen
ABS_11020_7 | PRP CNJ → PRP | high | preposition ze governing noun
```

**Compound POS exception (keep both tags):**
```
ABS_14040_5 | PRO VRB → VRB PRO | high | enclitic contraction | reason="färbe+ez"
```

**Missing tag assignment:**
```
ABS_11010_7 |  → DET | high | indefinite article ainen
```

**Correction of incorrect single tag:**
```
ABS_15030_2 | ADJ → NOM | high | substantivized adjective, no following noun
```

---

## When to Keep Compound POS Tags

### DEFAULT BEHAVIOR: Resolve to SINGLE POS tag

Most compound tags represent ambiguity that context resolves. Choose ONE tag.

### EXCEPTION: Keep TWO tags only for morphological fusions

Keep compound POS **only** when a single token genuinely contains BOTH grammatical functions fused together. Always add `reason="..."` attribute.

**1. Verb + Enclitic Pronoun contractions:**
- *färbs* = färbe + ez → `VRB PRO` with `reason="färbe+ez"`
- *wiltu* = wilt + du → `VEM PRO` with `reason="wilt+du"`
- *hâstû* = hâst + dû → `VEX PRO` with `reason="hâst+dû"`
- *giltet* = gilt + ez → `VRB PRO` with `reason="gilt+ez"`

**2. Preposition + Determiner fusions:**
- *zer* = ze + der → `PRP DET` with `reason="ze+der"`
- *zem* = ze + dem → `PRP DET` with `reason="ze+dem"`
- *inme* = in + dem → `PRP DET` with `reason="in+dem"`

### NOT Exceptions (always resolve to single):

| Compound | Resolution | Reasoning |
|----------|------------|-----------|
| `DET NUM` | Usually `DET` | *ein* as indefinite article, not numeral |
| `ADJ ADV` | Context | Modifies noun → ADJ; modifies verb → ADV |
| `NOM ADJ` | Context | Substantivized → NOM; attributive → ADJ |
| `DET CNJ` | Context | *daz* is either determiner OR conjunction, not both |
| `DET PRO` | Context | Attribuierend → DET; substituierend → PRO |
| `VRB VEX` | Context | With Partizip II → VEX; lexical meaning → VRB |
| `ADV NEG` | Usually `NEG` | *niht*, *nie* negating → NEG |

---

## Disambiguation Guidelines

### CNJ vs SCNJ vs CCNJ

**CCNJ** (Coordinating - connects equal elements):
- *und*, *oder*, *aber*, *ouch*, *noch*

**SCNJ** (Subordinating - introduces dependent clause):
- *daz* (when introducing clause, NOT before noun)
- *ob*, *swenne*, *sît*, *wan* (causal), *ê*, *unz*
- *als* temporal: *als er kam* (when he came)
- *wie* subordinating: *ich weiz wie er daz tet*

**CNJ** (General/unclear):
- Use when coordination vs subordination is ambiguous
- Fallback for insufficient context

**NOT CNJ/SCNJ/CCNJ:**
- *als* comparative: *grœzer als* → **ADV** (comparison particle)
- *wie* comparative: *schoener wie* → **ADV** (comparison particle)

### VRB vs VEX (Verb vs Auxiliary)

| Pattern | Tag | Example |
|---------|-----|---------|
| With Partizip II (Perfect) | VEX | *hât gesehen*, *ist komen* |
| With Partizip II (Passive) | VEX | *wirt geslagen* |
| Copula + NP/ADJ (no Partizip) | VRB | *ist guot*, *ist ein man* |
| Possession/lexical meaning | VRB | *hân ein hûs* |
| Main action verb | VRB | *er sach* |
| After modal | VRB | *mac sehen* |

### DET vs PRO vs SCNJ (*daz*, *der*, etc.)

**Basic patterns:**
- *daz* + noun phrase → **DET** (determiner modifying noun)
- *daz* + verb (clause) → **SCNJ** (subordinating conjunction)
- *daz* standing alone (= that one) → **PRO** (pronoun replacing noun)
- *der* + noun → **DET** (article)
- *der* as relative pronoun → **PRO** (substituierend)

**IMPORTANT: Deictic *daz* (Common Error!)**

When *daz* points deictically to previously mentioned content WITHOUT introducing a subordinate clause, it is **DET**, not PRO!

**Test:** Does *daz* introduce a verb-final subordinate clause?
- YES → SCNJ (*ich weiz **daz** er kumt*)
- NO, points to prior content → DET (*unum est necessarium, **daz** ist als vil gesprochen*)
- NO, stands alone replacing noun → PRO (*er nam **daz** und gie hin*)

**Examples of deictic DET:**
| Context | Analysis | Tag |
|---------|----------|-----|
| *daz kumet von abegescheidenheit* | Points to prior content, main clause verb | DET |
| *unum est necessarium, daz ist...* | Points to Latin quote, main clause | DET |
| *daz ist wâr* | Points to prior statement | DET |

### NOM vs ADJ

| Pattern | Tag |
|---------|-----|
| DET + X + noun | ADJ (attributive) |
| DET + X (no noun) | NOM (substantivized) |
| After copula | ADJ (predicative) |

### Confidence Levels

**High confidence:**
- Clear syntactic pattern
- Standard MHG construction
- Unambiguous context

**Medium confidence:**
- Slightly unusual construction
- Context mostly clear but with minor ambiguity
- Standard pattern with minor variations

**Low confidence:**
- Unusual word order
- Ambiguous construction
- Missing or fragmentary context

---

## Worked Examples

For detailed pedagogical examples of disambiguation (including 3-way ambiguity of *daz*, *als* as ADV vs SCNJ, and *haben* as VRB vs VEX), see [references/examples.md](references/examples.md).

## Workflow Phases

### Phase 0: Environment Setup (once per session)

**System Context**: Windows (Git Bash).
- Use provided Python scripts for analysis.
- You can use Unix-specific shell commands if needed, alongside native tools.

```bash
python --version          # Verify Python 3.13+
pip install lxml          # Install if needed
```

Verify scripts exist:
- `.gemini/skills/pos-disambiguator/scripts/split-tei-for-pos-validation.py`
- `.gemini/skills/pos-disambiguator/scripts/merge-pos-validation-results.py`
- `.gemini/skills/pos-disambiguator/scripts/validate-disambiguation.py`

### Phase 1: Discovery

1. Find manifests: `temp/disambiguation/*-manifest.txt`
2. For each SIGLE, check progress:
   - Count result files vs total chunks
   - If incomplete → process missing chunks

### Phase 2: Processing (Linguistic Analysis)

For each chunk file `{SIGLE}-chunk-{NUM}.md`:

1. **Read** the chunk file completely
2. **Analyze** the CONTEXT TEXT section to understand the surrounding text
3. **Assess text difficulty** (see below) and adjust processing speed accordingly
4. **Process** each word in the word list:
   - ⚠️ compound tags → disambiguate (usually to single)
   - ✓ single tags → verify, output ONLY if correction needed
   - ❓ missing tags → assign based on context
   - If truly ambiguous → **Assign Best Guess** (do NOT skip), set `confidence='low'`, `reason='ambiguous'`
5. **Write** result file `{SIGLE}-chunk-{NUM}-result.md`

**Text Difficulty Assessment:**

| Text Type | Difficulty | Processing Strategy |
|-----------|------------|---------------------|
| Cookbooks, practical texts | LOW | Standard processing |
| Early NHG tendency, normalized | LOW | Standard processing |
| Literary prose | MEDIUM | Check more context |
| Religious/philosophical | HIGH | Slow, careful analysis |
| Complex poetry (Minnesang) | HIGH | Full clause analysis |
| Non-normalized, archaic MHG | VERY HIGH | Maximum scrutiny, but **ALWAYS** assign a tag (use 'low' confidence if unsure) |

**Rule:** Complex, non-normalized MHG texts require systematically slower and more controlled work. Check more context before making PoS decisions.

**CRITICAL for missing tags (❓):**
- Old_pos must be EMPTY, not "❓"
- Correct: `ABS_11010_7 |  → DET | high | indefinite article`
- Wrong: `ABS_11010_7 | ❓ → DET | high | indefinite article`

### Phase 3: Merge Results

When all chunks complete:

```bash
python .gemini/skills/pos-disambiguator/scripts/merge-pos-validation-results.py temp/disambiguation {SIGLE} tei/{SIGLE}.xml
```

Output:
- `tei/{SIGLE}.disamb.tei.xml`
- `tei/{SIGLE}.disambiguation-report.md`

### Phase 4: Validation

```bash
python .gemini/skills/pos-disambiguator/scripts/validate-disambiguation.py
```

Check for:
- Remaining compound tags (except documented exceptions with `reason`)
- Empty tags
- Structure issues

### Phase 5: Refinement (Batch Strategy)

If validation fails, use this strategy to clear errors efficiently:

1. **Detect Missing Decisions**:
   Run the detection script to identify which chunks have unresolved items (skipped decisions):
   ```bash
   python .gemini/skills/pos-disambiguator/scripts/find-missing-decisions.py temp/disambiguation {SIGLE}
   ```
   This will list chunks sorted by the number of missing decisions.

2. **Batch Fix (Top Offenders)**:
   Prioritize the chunks with the highest missing counts. For each target chunk:
   - **Prepare Fix Task**: Run the preparation script to extract the context and the specific missing items:
     ```bash
     python .gemini/skills/pos-disambiguator/scripts/prepare-fix-task.py temp/disambiguation/{SIGLE}-chunk-{NUM}.md
     ```
   - **Generate Fix**: Use the output to create a FIX file `{SIGLE}-chunk-{NUM}-result_FIX-01.md` containing **ALL** missing decisions.
   - **Format**: Same as standard results (`xml_id | old_pos → new_pos | confidence | reason`).

3. **Re-Merge**:
   ```bash
   python .gemini/skills/pos-disambiguator/scripts/merge-pos-validation-results.py temp/disambiguation {SIGLE} tei/{SIGLE}.xml
   ```
   The script uses "Last-Write-Wins", so your new FIX files will automatically overwrite missing or incorrect entries.

**Safety limit**: Maximum 3 refinement iterations per chunk. After 3 failures, mark as "complete with errors" and generate a Failure Report.

**Creating a Failure Report**:
If you hit the 3-iteration limit, create 	emp/disambiguation/{SIGLE}-FAILURE-REPORT.md including:
1. The specific chunks that failed.
2. The xml_ids that remain unresolved.
3. A brief linguistic explanation of *why* the context was too ambiguous to resolve (e.g., "Missing verb makes it impossible to determine if 'daz' is SCNJ or DET"), so a human expert can review it.

---

## Script Reference

### split-tei-for-pos-validation.py

Splits TEI files into chunks for processing.

```bash
python .gemini/skills/pos-disambiguator/scripts/split-tei-for-pos-validation.py tei/{SIGLE}.xml
```

**Defaults** (optimized for Gemini 3 Pro):
- `--chunk-size 500` (500 target words per chunk - standard for focused analysis)
- `--context-size 50` (50 words context before/after)

### merge-pos-validation-results.py

Merges result files back into TEI.

```bash
python .gemini/skills/pos-disambiguator/scripts/merge-pos-validation-results.py temp/disambiguation {SIGLE} tei/{SIGLE}.xml
```

**Parses format**: `xml_id | old_pos → new_pos | confidence | reason [| reason="value"]`

### validate-disambiguation.py

Checks for remaining issues.

```bash
python .gemini/skills/pos-disambiguator/scripts/validate-disambiguation.py
```

### find-missing-decisions.py

Identifies chunks where the Agent skipped items (errors of omission).

```bash
python .gemini/skills/pos-disambiguator/scripts/find-missing-decisions.py temp/disambiguation {SIGLE}
```
**Output**: List of chunks sorted by missing decision count.

### prepare-fix-task.py

Generates a targeted task description for fixing missing decisions in a specific chunk.

```bash
python .gemini/skills/pos-disambiguator/scripts/prepare-fix-task.py temp/disambiguation/{SIGLE}-chunk-{NUM}.md
```
**Output**: Markdown text containing Context Text and the list of missing items to validate.

---

## Progress Reporting

After each TEI file:

```
✓ {SIGLE}.tei COMPLETE
  - Chunks processed: X/X
  - Words validated: N
  - Changes made: M
  - Refinement iterations: N/3
  - Validation: CLEAN
```

For failures:

```
⚠️ {SIGLE}.tei INCOMPLETE (after 3 refinement attempts)
  - Remaining errors: X compound tags, Y empty tags
  - Failure report: temp/disambiguation/{SIGLE}-FAILURE-REPORT.md
```

---

**Ready for processing. Wait for user command to begin.**
