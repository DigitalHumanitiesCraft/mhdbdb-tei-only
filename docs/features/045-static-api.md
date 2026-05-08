# Issue #45: Static JSON API (FAIR, GitHub Pages)

## Context

External projects (MWB, Worterbuchnetz) and researchers need programmatic access to MHDBDB data. Currently the only way to consume data is loading the full compressed indexes in a browser. A static JSON API provides stable, citable URLs for every resource — without leaving GitHub Pages.

Connects to #42 (persistent lemma pages): the API provides the data layer, #42 provides the human-readable HTML layer. Both share the same ID scheme.

## Design Decisions

**Static, not dynamic:** Pre-built JSON files at predictable URLs. No server, no search endpoint. Search stays client-side. This is the only option on GitHub Pages.

**No versioning prefix:** URLs are `/api/lemmata/lemma_879.json`, not `/api/v1/...`. Living project — if schema changes, we document it. Keeps URLs short and permanent.

**No auth:** FAIR principle = as public as possible. GitHub Pages doesn't support auth anyway. CC BY-NC-SA license governs reuse.

**JSON only:** No TEI-XML endpoint. TEI files are already accessible in `/tei/`.

## Data Exploration Results (Feb 2026)

Actual counts and sizes from the existing indexes:

### Authority Index (22 MB uncompressed, 3 MB gz)

| Resource | Count | Example ID |
|----------|-------|-----------|
| Lemmata | 43,750 | `lemma_879` (brôt) |
| Persons | 210 | `person_778d...` (Karl IV.) |
| Works | 583 | `work_350` (Aalener Stadtratsgedicht) |
| Concepts | 567 | `concept_10000000` (Universum/Welt) |
| Genres | 615 | `genre_00bb7cc9` (Lokalchronik...) |
| Names | 90 | `name_40000000` (Namen) |
| Variants | 176,056 | key-value map, not individual resources |

### Corpus Index (143 MB uncompressed, 34 MB gz)

| Field | Value |
|-------|-------|
| Texts | 667 |
| Unique lemmata indexed | 42,628 |
| Per-text structure | `id`, `filename`, `title`, `author`, `authorRef`, `workRef`, `genre`, `wordCount`, `words` (array of lemma IDs), `lemmata` (position map) |

### Lemma Object (actual schema from index)
```json
{
  "id": "lemma_879",
  "lemma": "brôt",
  "normalized": "brot",
  "pos": "N",
  "senseCount": 3,
  "etymology": [{"text": "brot", "lemmaRef": "lemma_7779"}],
  "senses": [{
    "id": "lemma_879_sense_1",
    "conceptIds": ["concept_1234"]
  }]
}
```

### Person Object
```json
{
  "id": "person_778d...",
  "preferredName": "Karl IV.",
  "gnd": "118560085",
  "wikidata": "Q155669",
  "works": "work_572",
  "normalized": "karl iv."
}
```

### Work Object
```json
{
  "id": "work_350",
  "title": "Aalener Stadtratsgedicht",
  "titles": [{"text": "...", "lang": "de", "type": null, "ana": null}],
  "sigle": "ASG",
  "sigles": ["ASG"],
  "author": "Heinrich von Rang",
  "authorRef": "persons.xml#person_786",
  "genres": [{"id": "genre_2c9f837c", "text": "Kleindidaxe"}]
}
```

### Text Object (corpus index)
```json
{
  "id": "ABG",
  "filename": "ABG.tei.xml",
  "title": "Von der Abgeschiedenheit",
  "author": "Meister Eckhart",
  "authorRef": "#person_445",
  "workRef": "works.xml#work_89",
  "wordCount": 2955,
  "words": ["lemma_7193", "lemma_37696", ...],
  "lemmata": {"lemma_7193": [0, 8, 12, ...], ...}
}
```

## Decision: Hybrid File Strategy

Resolved Feb 2026 after sizing analysis against the actual indexes.

### Size Estimation

| Resource | Count | Avg size | Total |
|----------|-------|----------|-------|
| Lemmata | 43,750 | 311 B | 13 MB |
| Persons | 210 | 166 B | 35 KB |
| Works | 583 | 1.1 KB | 665 KB |
| Concepts | 567 | 113 B | 64 KB |
| Genres | 615 | 113 B | 69 KB |
| Names | 90 | 176 B | 16 KB |
| Texts | 667 | 220 KB (full) / ~0.5 KB (metadata only) | 146 MB full / 330 KB metadata |

### Options Evaluated

| Approach | Files | Git inode overhead | Gzipped total |
|----------|-------|--------------------|---------------|
| All individual | ~46k | ~182 MB | ~23 MB |
| **Hybrid (chosen)** | **~2,700** | **~11 MB** | **~23 MB** |
| Bundled only | 7 | ~0 | ~23 MB |

### Decision: Hybrid

Individual JSON files for persons, works, concepts, genres, names, and texts (~2,700 files). Lemmata stay bundled as one index file.

**Rationale:**
- 17x fewer files than all-individual, 170x less inode overhead
- Gzipped size identical across all three approaches (~23 MB) — the savings from splitting are negligible
- Persons, works, and texts are the primary external-linking targets (GND, Wikidata, MWB) — they benefit most from individual URLs
- 43,750 tiny lemma files (311 B avg) add massive file-count overhead for minimal addressability gain
- Lemmata are still discoverable via `/api/lemmata/index.json` and individually via `#id` fragment

**Tradeoff accepted:** Lemmata are not individually addressable via REST URL. Consumers filter client-side from the bundled index. If individual lemma addressing becomes a real need later, we can split without changing existing URLs.

## URL Structure

```
/api/index.json                  # Root: links to all resource collections, version, license
/api/lemmata/index.json          # Bundled: all lemmata (id, lemma, normalized, pos, senseCount)
/api/persons/index.json          # Lightweight list (id, preferredName)
/api/persons/{id}.json           # Full person record
/api/works/index.json            # Lightweight list (id, title, sigle)
/api/works/{id}.json             # Full work record
/api/concepts/index.json         # Lightweight list (id, label)
/api/concepts/{id}.json          # Full concept record
/api/genres/index.json           # Lightweight list (id, label)
/api/genres/{id}.json            # Full genre record
/api/names/index.json            # Lightweight list (id, label)
/api/names/{id}.json             # Full name record
/api/texts/index.json            # Lightweight list (id, title, author, wordCount)
/api/texts/{sigle}.json          # Text metadata (no word positions, no lemmata map)
/api/index.html                  # Human-readable docs page
```

Note: No `/api/lemmata/{id}.json` — lemmata are bundled per the hybrid decision above. Genres and names added (they were missing from the original proposal but exist in the authority index).

## API Schemas

### Text Metadata (what goes into `/api/texts/{sigle}.json`)

The corpus index text objects are large (~220 KB avg) because of `words` and `lemmata` arrays. The API strips those:

```json
{
  "id": "ABG",
  "filename": "ABG.tei.xml",
  "title": "Von der Abgeschiedenheit",
  "author": "Meister Eckhart",
  "authorRef": "#person_445",
  "workRef": "works.xml#work_89",
  "genre": "Traktat",
  "wordCount": 2955
}
```

**Excluded:** `words` (full lemma ID array) and `lemmata` (position map). These stay in the corpus index for client-side search — too large for individual API files.

### Index Files (lightweight lists for discovery)

Each `index.json` contains an array of summary objects, not full records:

- **Lemmata index:** `[{id, lemma, normalized, pos, senseCount}, ...]` — full bundled data since individual files don't exist
- **Persons index:** `[{id, preferredName}, ...]`
- **Works index:** `[{id, title, sigle}, ...]`
- **Concepts index:** `[{id, label}, ...]`
- **Genres index:** `[{id, label}, ...]`
- **Names index:** `[{id, label}, ...]`
- **Texts index:** `[{id, title, author, wordCount}, ...]`

### Corpus Enrichment

The API does **not** cross-reference corpus statistics into authority data (e.g., "lemma X appears in N texts"). Rationale: keeps the build simple (authority index in, authority API out; corpus index in, text API out). If consumers need occurrence counts, they can derive them from the lemmata index + texts index client-side.

### Root Index (`/api/index.json`)

```json
{
  "project": "MHDBDB",
  "version": "1.0.0",
  "license": "CC BY-NC-SA 4.0",
  "contact": "mhdbdb@plus.ac.at",
  "generated": "2026-02-24T12:00:00Z",
  "collections": {
    "lemmata": {"href": "lemmata/index.json", "count": 43750},
    "persons": {"href": "persons/index.json", "count": 210},
    "works":   {"href": "works/index.json",   "count": 583},
    "concepts":{"href": "concepts/index.json", "count": 567},
    "genres":  {"href": "genres/index.json",   "count": 615},
    "names":   {"href": "names/index.json",    "count": 90},
    "texts":   {"href": "texts/index.json",    "count": 667}
  }
}
```

## Build Approach

New script: `scripts/build-api.py`
- Reads existing `data/authority-index.json.gz` and `data/corpus-index.json.gz`
- Outputs JSON files into `/api/`
- Idempotent, fast (reads pre-built indexes, not XML)
- Follows patterns from `build-authority-index.py`
- Runs manually: `python scripts/build-api.py`
- Not part of `npm run serve` or CI — API rebuild is an explicit step, same as index rebuilds
- Add `npm run build:api` convenience alias in `package.json`

## FAIR Compliance

- **Findable:** Stable URLs, index files for discovery, API root with metadata
- **Accessible:** Open HTTP, JSON, CORS (GitHub Pages default)
- **Interoperable:** Standard URL patterns, linked identifiers (GND, Wikidata)
- **Reusable:** CC BY-NC-SA 4.0 in every response

## Out of Scope

- Server-side search
- Authentication / rate limiting
- Variants as individual resources (176k entries, map only)
- Word position data in text API (too large, stays in corpus index)
- Individual lemma files (hybrid decision — bundled index only)
- Corpus-derived enrichment (occurrence counts, text lists per lemma)
- API versioning (documented schema changes instead)
