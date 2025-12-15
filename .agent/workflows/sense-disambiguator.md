# Middle High German Sense Disambiguator Workflow

**Target Model**: Gemini 2.5 Pro (1M context window)
**Last Updated**: December 2025
**Status**: DRAFT - Requires sense definitions before implementation

---

## Overview

This workflow assigns `meaningRef` attributes to `<w>` elements in TEI files where the lemma has multiple senses (polysemy). Currently, ~1.56 million word occurrences across 6,910 polysemous lemmas lack sense disambiguation.

### Key Statistics

| Metric | Value |
|--------|-------|
| Total `<w>` without `meaningRef` | 3,476,217 |
| Polysemous lemmas needing disambiguation | 6,910 |
| Word occurrences to disambiguate | 1,558,958 |
| Top-50 lemmas cover | 701,206 occurrences (45%) |

---

## Critical Prerequisite: Sense Definitions

**BLOCKER**: The current lexicon lacks textual definitions for senses. Each `<sense>` element contains only abstract concept references (e.g., "Wert/Unwert", "Besitz") without human-readable glosses.

### Current State (Unusable for LLM)

```xml
<sense xml:id="lemma_2573_sense_4120">
  <ptr target="concepts.xml#concept_23308000"/>  <!-- Besitz -->
  <ptr target="concepts.xml#concept_31330000"/>  <!-- Wert/Unwert -->
  <ptr target="concepts.xml#concept_31410000"/>  <!-- Mengenbegriffe -->
</sense>
```

### Required State (Usable for LLM)

```xml
<sense xml:id="lemma_2573_sense_4120">
  <def xml:lang="de">Besitz, Vermögen, Hab und Gut</def>
  <def xml:lang="en">property, possessions, wealth</def>
  <ptr target="concepts.xml#concept_23308000"/>
  <ptr target="concepts.xml#concept_31330000"/>
  <ptr target="concepts.xml#concept_31410000"/>
</sense>
```

### Options to Generate Definitions

1. **Manual curation** (highest quality, most effort)
   - Create definitions for Top-50 lemmas first (covers 45% of cases)
   - Use BMZ, Lexer, Grimm as sources

2. **LLM-assisted generation** (medium quality, medium effort)
   - Generate draft definitions from concept combinations
   - Human review and correction

3. **External lexicon mapping** (variable quality)
   - Map to existing MHG dictionaries with APIs
   - woerterbuchnetz.de, BMZ online

---

## Workflow Architecture (Once Definitions Exist)

### Phase 0: Preparation

1. **Generate sense definition file** for target lemmas
2. **Split TEI** into chunks (similar to PoS workflow)
3. **Create manifest** tracking progress

### Phase 1: Chunk Processing

For each chunk, the LLM receives:

```markdown
## Lemma: guot (ADJ) - lemma_2573

### Available Senses

| Sense ID | Definition | Concepts |
|----------|------------|----------|
| sense_4120 | Besitz, Vermögen | Besitz, Wert/Unwert |
| sense_4121 | moralisch gut, tugendhaft | Moralisches Empfinden |
| sense_4122 | glücklich, erfreulich | Glückseligkeit, Freude |
| sense_4123 | Bauernhof, Landgut | Bauernhof, Besitz |
| sense_4125 | von guter Qualität | Physikalische Eigenschaften |
| sense_4126 | fähig, tüchtig | Fähigkeiten |
| sense_4127 | wohlgesinnt, freundlich | Vertrauen, Vorteil |

## Context

[50 words before] **TARGET: guot** [50 words after]

daz er sô **guot** und sô getriuwe was

## Task

Which sense best fits this occurrence? Output:
`ABG_401010_5 | → sense_4121 | high | morally good in context of loyalty (getriuwe)`
```

### Phase 2: Merge Results

Apply disambiguations to TEI:

```xml
<!-- Before -->
<w xml:id="ABG_401010_5" lemmaRef="lexicon.xml#lemma_2573">guot</w>

<!-- After -->
<w xml:id="ABG_401010_5"
   lemmaRef="lexicon.xml#lemma_2573"
   meaningRef="lexicon.xml#lemma_2573_sense_4121">guot</w>
```

### Phase 3: Validation

- Check all target words have `meaningRef`
- Validate sense IDs exist in lexicon
- Generate statistics report

---

## Prioritization Strategy

### Tier 1: High-Impact Lemmas (Priority)

Focus on Top-20 lemmas first:

| Rank | Lemma | Occurrences | Senses |
|------|-------|-------------|--------|
| 1 | haben | 80,094 | 8 |
| 2 | wellen | 35,076 | 5 |
| 3 | werden | 32,446 | 5 |
| 4 | wesen | 30,287 | 3 |
| 5 | herre | 28,373 | 2 |
| 6 | guot | 27,582 | 8 |
| 7 | mügen | 23,863 | 4 |
| 8 | müezen | 22,440 | 4 |
| 9 | grôz | 20,187 | 4 |
| 10 | lâʒen | 20,142 | 5 |

**Tier 1 total**: ~320,000 occurrences (20% of all)

### Tier 2: Medium-Impact (Secondary)

Lemmas 11-50: ~380,000 occurrences

### Tier 3: Long Tail (Optional)

Remaining 6,860 lemmas: ~860,000 occurrences

---

## Differences from PoS Disambiguation

| Aspect | PoS Workflow | Sense Workflow |
|--------|--------------|----------------|
| **Decision basis** | Grammar/Syntax | Semantics/Context |
| **Context needed** | 50 words usually sufficient | May need full sentence/paragraph |
| **Reference data** | 19 PoS tags (fixed) | Variable senses per lemma |
| **Ambiguity** | Usually 2-3 options | Up to 10+ senses |
| **Chunk strategy** | By text | By lemma OR by text |
| **Definitions** | Built into tagset | MUST BE CREATED FIRST |

---

## Chunk Strategy Options

### Option A: By Text (like PoS)

- Process all words in text chunks
- Pro: Maintains narrative context
- Con: Each chunk needs definitions for many different lemmas

### Option B: By Lemma

- Process all occurrences of one lemma across corpus
- Pro: Consistent sense inventory per chunk
- Con: Less narrative context, jumping between texts

### Option C: Hybrid (Recommended)

- Group by lemma, then chunk by text
- Each chunk: One lemma, one text, all occurrences
- Maintains context while focusing definitions

---

## Output Format

### Standard Format

```
xml_id | → sense_id | confidence | reason
```

### Examples

```
ABG_401010_5 | → lemma_2573_sense_4121 | high | moral goodness with getriuwe
ABG_402030_12 | → lemma_2573_sense_4120 | medium | possessions in inheritance context
ABG_403050_8 | → lemma_2573_sense_4125 | high | quality descriptor for sword
```

### Skip Format (truly ambiguous)

```
ABG_405070_3 | → SKIP | low | fragmentary context, multiple senses possible
```

---

## Next Steps

1. **DECISION NEEDED**: How to create sense definitions?
   - [ ] Option A: Manual curation (start with Top-10 lemmas)
   - [ ] Option B: LLM-assisted with human review
   - [ ] Option C: External lexicon mapping

2. **Pilot**: Once definitions exist for 1-2 lemmas, run pilot disambiguation

3. **Scripts**: Adapt PoS scripts for sense disambiguation:
   - `split-tei-for-sense-validation.py`
   - `merge-sense-validation-results.py`
   - `validate-sense-disambiguation.py`

---

## Appendix: Top-50 Polysemous Lemmas

| Rank | Lemma | POS | Senses | Occurrences |
|------|-------|-----|--------|-------------|
| 1 | haben | NOM | 8 | 80,094 |
| 2 | wellen | VEM | 5 | 35,076 |
| 3 | werden | VEX | 5 | 32,446 |
| 4 | wesen | NOM | 3 | 30,287 |
| 5 | herre | NOM | 2 | 28,373 |
| 6 | guot | ADJ | 8 | 27,582 |
| 7 | mügen | VEM | 4 | 23,863 |
| 8 | müezen | VEM | 4 | 22,440 |
| 9 | grôz | ADJ | 4 | 20,187 |
| 10 | lâʒen | NOM | 5 | 20,142 |
| 11 | nâch | ADJ | 4 | 18,450 |
| 12 | reht | ADJ | 6 | 18,448 |
| 13 | soln | VEM | 4 | 17,949 |
| 14 | gân | NOM | 8 | 17,217 |
| 15 | herze | NOM | 2 | 16,366 |
| 16 | umbe | ADV | 4 | 16,183 |
| 17 | nemen | NOM | 10 | 12,741 |
| 18 | hin | ADV | 2 | 12,425 |
| 19 | heiʒʒen | VRB | 5 | 12,001 |
| 20 | wîp | NOM | 3 | 11,624 |
| 21 | tragen | NOM | 12 | 11,332 |
| 22 | tac | ADV | 4 | 11,259 |
| 23 | wiʒʒen | NOM | 4 | 10,664 |
| 24 | bringen | NOM | 6 | 10,129 |
| 25 | rîche | ADJ | 6 | 9,580 |
| 26 | stân | VRB | 5 | 9,494 |
| 27 | hœren | INJ | 6 | 9,159 |
| 28 | gegen | ADV | 4 | 9,043 |
| 29 | noch | ADV | 2 | 9,033 |
| 30 | hôch | ADJ | 5 | 8,196 |
| 31 | vinden | VRB | 6 | 7,883 |
| 32 | machen | NOM | 3 | 7,721 |
| 33 | gewinnen | VRB | 8 | 7,643 |
| 34 | lanc | ADJ | 2 | 7,626 |
| 35 | wider | ADV | 5 | 7,036 |
| 36 | slahen | NOM | 10 | 6,888 |
| 37 | varn | NOM | 7 | 6,642 |
| 38 | vernemen | VRB | 7 | 6,474 |
| 39 | vater | NOM | 4 | 6,410 |
| 40 | enphâhen | NOM | 8 | 6,331 |
| 41 | phlegen | VRB | 8 | 6,311 |
| 42 | kraft | NOM | 4 | 6,186 |
| 43 | sitzen | NOM | 5 | 6,159 |
| 44 | liut | NOM | 6 | 6,070 |
| 45 | verliesen | NOM | 5 | 6,059 |
| 46 | muot | ADJ | 3 | 5,842 |
| 47 | jehen | VRB | 5 | 5,828 |
| 48 | maget | NOM | 4 | 5,737 |
| 49 | strît | NOM | 8 | 5,724 |
| 50 | kleine | ADJ | 5 | 4,853 |

**Total Top-50**: 701,206 occurrences
