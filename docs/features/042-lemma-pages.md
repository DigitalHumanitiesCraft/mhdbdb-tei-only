# Issue #42: Persistent Lemma Pages + MWB-API Preparation

## Context

MWB (Mittelhochdeutsches Wörterbuch) and Wörterbuchnetz want to link to MHDBDB lemmata from their global dictionary search. The old Java app URL (`https://mhdbdb-old.sbg.ac.at/mhdbdb/App?action=Dic&lid=879`) will eventually die.

## Key Finding: IDs Already Aligned

| System | brôt | minne |
|--------|------|-------|
| Our `lexicon.xml` | `lemma_879` | `lemma_4130` |
| Wörterbuchnetz `lid=` | 879 | 4130 |
| Wikidata P9351 | 879 | 4130 |
| Old MHDBDB URL | `?lid=879` | `?lid=4130` |

Zero mapping work. The numeric suffix IS the shared ID.

## Implementation Status

### Done (shipped in `fc901df`)

| Feature | Status |
|---------|--------|
| URL routing: `/lemma/879`, `/lemma/?id=879`, `/lemma/#879` | Done |
| 404.html redirect for clean GitHub Pages paths | Done |
| Lemma title block (form, normalized, POS, copyable ID) | Done |
| Etymology with clickable component links | Done |
| Senses with concept labels (DE) | Done |
| Corpus occurrences (text list, frequency, sorted, clickable to reading view) | Done |
| Wörterbuchnetz API integration (BMZ + Lexer, live lookup) | Done |
| External links (old MHDBDB, corpus search) | Done |
| 11 Playwright tests (all passing) | Done |
| Tailwind CSS rebuilt for lemma page | Done |

**Files created:**
- `lemma/index.html` — Page shell
- `lemma/lemma-page.js` — Page logic (ES6 module, 320 lines)
- `404.html` — GitHub Pages SPA redirect

### Still Missing: Gap Analysis vs Old MHDBDB (Feb 2026)

Compared [old page for brôt](https://mhdbdb-old.sbg.ac.at/mhdbdb/App?action=Dic&lid=879) with [new page](https://dhcraft.org/mhdbdb-tei-only/lemma/?id=879). All 4 gaps use data we already have — purely rendering work.

#### 1. Orthographic Variants List (priority: high)

Old page shows 50+ attested spelling forms (brot, brôt, brote, prot, prôt, prott...), each clickable to corpus search.

**Data source:** `variants` dictionary in authority index (176k entries). Currently a flat map `variant → lemmaId`. To render: invert the map at page load to find all variants pointing to current lemma.

**Rendering:** Clickable list, each variant links to `../korpus.html?search={variant}`.

#### 2. Compounds Section (priority: high)

Old page lists 21 compounds (betelbrôt, himelbrôt, weizebrôt...).

**Data source:** `etymology` arrays in lemmata. Invert the lookup: find all lemmata whose `etymology` contains `lemmaRef: "lemma_879"`. Already works in playground (e.g., halpbrôt shows morphology halbe + brôt).

**Rendering:** List of compound lemmata, each linking to their own lemma page.

#### 3. Prev/Next Lemma Navigation (priority: medium)

Old page has sequential browsing buttons `[<==]` `[===>]`.

**Implementation:** Sort lemmata array by ID (or alphabetically by lemma form), find neighbors of current lemma, render as nav arrows. Trivial.

#### 4. IMAREAL Image Link (priority: low)

Old page links to [IMAREAL/REALonline](https://realonline.imareal.sbg.ac.at/) image database.

**Implementation:** Add as external link. URL pattern needs investigation — unclear if IMAREAL has a stable query-by-concept API.

## URL Routing Decision

**Decision: Option C (clean paths) with fallback support.**

| Pattern | Example | Support |
|---------|---------|---------|
| Clean path (canonical) | `/lemma/879` | Via 404.html redirect |
| Query param | `/lemma/?id=879` | Direct |
| Hash | `/lemma/#879` | Direct |

## Data Flow

```
URL: /lemma/879
  → lemma/index.html loads
  → Parse ID from path / query / hash
  → Load authority-index.json.gz (IndexedDB cache or network)
  → Find lemma_879 in lemmata array
  → Render: title, etymology, senses
  → Load corpus-index.json.gz (non-blocking)
  → Render: occurrences list with frequency
  → Fetch Wörterbuchnetz API (non-blocking, BMZ + Lexer)
  → Render: external links + dictionary entries
```

## Open Questions

1. MWB backlink: Do we need their ID mapping table, or can we derive it from Lexer references?
2. Should we add `<link rel="canonical">` and structured data (JSON-LD) for SEO? (Nice to have)
3. IMAREAL: What's the URL pattern for querying by concept/keyword?
