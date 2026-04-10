# Authority Files Audit Report

**Date:** 2026-04-10
**Files:** 7

---

## Overview

| File | Elements | IDs | Cross-Refs | Size |
|------|----------|-----|------------|------|
| concepts.xml | 3,444 | 568 | 630 | 211 KB |
| genres.xml | 6,704 | 616 | 3,175 | 413 KB |
| lexicon.xml | 559,504 | 105,990 | 238,918 | 32,607 KB |
| names.xml | 537 | 91 | 160 | 34 KB |
| persons.xml | 990 | 211 | 0 | 55 KB |
| variants.xml | 231,770 | 192,472 | 39,282 | 12,473 KB |
| works.xml | 17,835 | 1,263 | 1,457 | 1,169 KB |

## ID Formats

**concepts.xml:** {'numeric': 567, 'taxonomy_root': 1}
**genres.xml:** {'uuid/hash': 602, 'numeric': 13, 'taxonomy_root': 1}
**lexicon.xml:** {'compound': 62240, 'numeric': 43750}
**names.xml:** {'numeric': 90, 'taxonomy_root': 1}
**persons.xml:** {'numeric': 210, 'other': 1}
**variants.xml:** {'numeric': 192472}
**works.xml:** {'numeric': 580, 'sigle_key': 635, 'other': 45, 'uuid/hash': 3}

## Cross-Reference Summary

| From | To | Count | Mechanism |
|------|------|-------|-----------|
| lexicon.xml | concepts.xml | 191,929 | <ptr @target> |
| lexicon.xml | lexicon.xml (internal) | 46,989 | <seg @corresp> |
| variants.xml | lexicon.xml | 39,282 | <entry @corresp> |
| genres.xml | genres.xml (internal) | 3,175 | <ptr @target> |
| works.xml | genres.xml | 870 | <ptr @target> |
| concepts.xml | concepts.xml (internal) | 630 | <ptr @target> |
| works.xml | persons.xml | 587 | <author @ref> |
| names.xml | names.xml (internal) | 89 | <ptr @target> |
| names.xml | concepts.xml | 71 | <ptr @target> |

## Referential Integrity

No orphaned references found.

## Denormalization

No denormalized references found.

## Data Placement

- concepts.xml: encodingDesc=3431 elements, body=2 elements
- genres.xml: encodingDesc=6691 elements, body=2 elements
- lexicon.xml: encodingDesc=0 elements, body=559493 elements
- names.xml: encodingDesc=524 elements, body=2 elements
- persons.xml: encodingDesc=0 elements, body=979 elements
- variants.xml: encodingDesc=0 elements, body=231756 elements
- works.xml: encodingDesc=0 elements, body=17824 elements