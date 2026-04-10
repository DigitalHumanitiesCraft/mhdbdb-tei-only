# Authority Files Audit Report

**Date:** 2026-04-09
**Files:** 7

---

## Overview

| File | Elements | IDs | Cross-Refs | Size |
|------|----------|-----|------------|------|
| concepts.xml | 3,444 | 568 | 630 | 211 KB |
| genres.xml | 6,704 | 616 | 3,175 | 413 KB |
| lexicon.xml | 559,575 | 105,990 | 238,989 | 33,373 KB |
| names.xml | 537 | 91 | 160 | 34 KB |
| persons.xml | 1,784 | 210 | 588 | 80 KB |
| variants.xml | 232,126 | 192,674 | 39,436 | 12,758 KB |
| works.xml | 20,754 | 1,263 | 4,009 | 1,437 KB |

## ID Formats

**concepts.xml:** {'numeric': 567, 'taxonomy_root': 1}
**genres.xml:** {'uuid/hash': 602, 'numeric': 13, 'taxonomy_root': 1}
**lexicon.xml:** {'compound': 62240, 'numeric': 43750}
**names.xml:** {'numeric': 90, 'taxonomy_root': 1}
**persons.xml:** {'numeric': 205, 'uuid/hash': 4, 'other': 1}
**variants.xml:** {'numeric': 192674}
**works.xml:** {'sigle_key': 635, 'numeric': 580, 'other': 45, 'uuid/hash': 3}

## Cross-Reference Summary

| From | To | Count | Mechanism |
|------|------|-------|-----------|
| lexicon.xml | concepts.xml | 191,990 | <ptr @target> |
| lexicon.xml | lexicon.xml (internal) | 46,999 | <seg @corresp> |
| variants.xml | lexicon.xml | 39,436 | <entry @corresp> |
| works.xml | genres.xml | 3,422 | <ref @target> |
| genres.xml | genres.xml (internal) | 3,175 | <ptr @target> |
| concepts.xml | concepts.xml (internal) | 630 | <ptr @target> |
| persons.xml | works.xml | 588 | <bibl @corresp> |
| works.xml | persons.xml | 587 | <author @ref> |
| names.xml | names.xml (internal) | 89 | <ptr @target> |
| names.xml | concepts.xml | 71 | <ptr @target> |

## Referential Integrity

**226 orphaned references found:**

| Source | Target | Element | Attribute |
|--------|--------|---------|-----------|
| lexicon.xml | concepts.xml#concept_23123919 | ptr | target |
| lexicon.xml | concepts.xml#concept_41430000 | ptr | target |
| lexicon.xml | concepts.xml#concept_41120000 | ptr | target |
| lexicon.xml | concepts.xml#concept_44100000 | ptr | target |
| lexicon.xml | lexicon.xml#lemma_56929 | seg | corresp |
| lexicon.xml | concepts.xml#concept_41120000 | ptr | target |
| lexicon.xml | lexicon.xml#lemma_56929 | seg | corresp |
| lexicon.xml | lexicon.xml#lemma_56929 | seg | corresp |
| lexicon.xml | lexicon.xml#lemma_56929 | seg | corresp |
| lexicon.xml | lexicon.xml#lemma_46395 | seg | corresp |
| lexicon.xml | concepts.xml#concept_41120000 | ptr | target |
| lexicon.xml | concepts.xml#concept_41120000 | ptr | target |
| lexicon.xml | concepts.xml#concept_41120000 | ptr | target |
| lexicon.xml | concepts.xml#concept_44100000 | ptr | target |
| lexicon.xml | concepts.xml#concept_41120000 | ptr | target |
| lexicon.xml | concepts.xml#concept_44100000 | ptr | target |
| lexicon.xml | lexicon.xml#lemma_46395 | seg | corresp |
| lexicon.xml | concepts.xml#concept_41120000 | ptr | target |
| lexicon.xml | concepts.xml#concept_42210000 | ptr | target |
| lexicon.xml | concepts.xml#concept_41120000 | ptr | target |
| lexicon.xml | concepts.xml#concept_40000000 | ptr | target |
| lexicon.xml | lexicon.xml#lemma_46395 | seg | corresp |
| lexicon.xml | concepts.xml#concept_41120000 | ptr | target |
| lexicon.xml | concepts.xml#concept_40000000 | ptr | target |
| lexicon.xml | lexicon.xml#lemma_47925 | seg | corresp |
| lexicon.xml | concepts.xml#concept_41120000 | ptr | target |
| lexicon.xml | concepts.xml#concept_41120000 | ptr | target |
| lexicon.xml | concepts.xml#concept_41120000 | ptr | target |
| lexicon.xml | concepts.xml#concept_41120000 | ptr | target |
| lexicon.xml | concepts.xml#concept_44100000 | ptr | target |
| lexicon.xml | lexicon.xml#lemma_55428 | seg | corresp |
| lexicon.xml | concepts.xml#concept_41120000 | ptr | target |
| lexicon.xml | concepts.xml#concept_42210000 | ptr | target |
| lexicon.xml | concepts.xml#concept_41120000 | ptr | target |
| lexicon.xml | concepts.xml#concept_44100000 | ptr | target |
| lexicon.xml | concepts.xml#concept_40000000 | ptr | target |
| lexicon.xml | concepts.xml#concept_41322100 | ptr | target |
| lexicon.xml | concepts.xml#concept_40000000 | ptr | target |
| lexicon.xml | concepts.xml#concept_41322200 | ptr | target |
| lexicon.xml | concepts.xml#concept_41321300 | ptr | target |
| lexicon.xml | concepts.xml#concept_46110000 | ptr | target |
| lexicon.xml | concepts.xml#concept_46110000 | ptr | target |
| lexicon.xml | concepts.xml#concept_41322100 | ptr | target |
| lexicon.xml | concepts.xml#concept_41321300 | ptr | target |
| lexicon.xml | concepts.xml#concept_41230000 | ptr | target |
| lexicon.xml | concepts.xml#concept_45200000 | ptr | target |
| lexicon.xml | concepts.xml#concept_45200000 | ptr | target |
| lexicon.xml | concepts.xml#concept_41322100 | ptr | target |
| lexicon.xml | concepts.xml#concept_41322100 | ptr | target |
| lexicon.xml | concepts.xml#concept_41322100 | ptr | target |
| ... | ... | ... | (176 more) |

## Denormalization

- works.xml: 3422 denormalized `<ref>` elements

## Data Placement

- concepts.xml: encodingDesc=3431 elements, body=2 elements
- genres.xml: encodingDesc=6691 elements, body=2 elements
- lexicon.xml: encodingDesc=0 elements, body=559564 elements
- names.xml: encodingDesc=524 elements, body=2 elements
- persons.xml: encodingDesc=0 elements, body=1773 elements
- variants.xml: encodingDesc=0 elements, body=232112 elements
- works.xml: encodingDesc=0 elements, body=20743 elements