# Issue #45: Static JSON API (FAIR, GitHub Pages)

## Context

External projects (MWB, Worterbuchnetz) and researchers need programmatic access to MHDBDB data. Currently the only way to consume data is loading the full compressed indexes in a browser. A static JSON API provides stable, citable URLs for every resource — without leaving GitHub Pages.

Connects to #42 (persistent lemma pages): the API provides the data layer, #42 provides the human-readable HTML layer. Both share the same ID scheme.

## Design Decisions

**Static, not dynamic:** Pre-built JSON files at predictable URLs. No server, no search endpoint. Search stays client-side. This is the only option on GitHub Pages.

**No versioning prefix:** URLs are `/api/lemmata/lemma_879.json`, not `/api/v1/...`. Living project — if schema changes, we document it. Keeps URLs short and permanent.

**No auth:** FAIR principle = as public as possible. GitHub Pages doesn't support auth anyway. CC BY-NC-SA license governs reuse.

**JSON only:** No TEI-XML endpoint. TEI files are already accessible in `/tei/`.

## Data Exploration Results (updated 2026-06-12)

Actual counts and sizes from the existing indexes:

### Authority Index (22 MB uncompressed, 3 MB gz)

| Resource | Count | Example ID |
|----------|-------|-----------|
| Lemmata | 43,754 | `lemma_879` (brôt) |
| Persons | 211 | `person_1768` (Karl IV.) |
| Works | 584 | `work_350` (Aalener Stadtratsgedicht) |
| Concepts | 567 | `concept_10000000` (Universum/Welt) |
| Genres | 615 | `genre_00bb7cc9` (Lokalchronik...) |
| Names | 90 | `name_40000000` (Namen) |
| Variants | 234,244 | key-value map, not individual resources |

### Corpus Index (~200 MB uncompressed, 42 MB gz)

| Field | Value |
|-------|-------|
| Texts | 667 |
| Unique lemmata indexed | 42,630 |
| Per-text structure | `id`, `filename`, `title`, `author`, `authorRef`, `workRef`, `genre`, `wordCount`, `words` (array of lemma IDs), `lemmata` (position map), `lineStarts`, `lineEnds` (added corpus index v4.1.0, #47.3) |

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
  "id": "person_1768",
  "preferredName": "Karl IV.",
  "gnd": "118560085",
  "wikidata": "Q155669",
  "works": [],
  "normalized": "karl iv.",
  "license": "CC BY-NC-SA 4.0"
}
```

**Note on `works`:** The source authority index stores `works` as a comma-separated string (`"work_4,work_36,..."`) or `null`. `build-api.py` normalizes this to a JSON array — `person_1` for example gets a 15-entry array; `person_1768` above has `null` in the source, hence `[]`.

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
  "genres": [{"id": "genre_2c9f837c", "text": "Kleindidaxe"}],
  "gnd": "...",
  "wikidata": "...",
  "handschriftencensus": "...",
  "biblStructs": [...]
}
```

Individual record files contain the full index record. The fields `gnd`, `wikidata`, `handschriftencensus`, and `biblStructs` are present where available.

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
| Lemmata | 43,754 | 311 B | 13 MB |
| Persons | 211 | 166 B | 35 KB |
| Works | 584 | 1.1 KB | 665 KB |
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
- 43,754 tiny lemma files (311 B avg) add massive file-count overhead for minimal addressability gain
- Lemmata are still discoverable via `/api/lemmata/index.json`; consumers filter client-side by `id`

**Tradeoff accepted:** Lemmata are not individually addressable via REST URL. Consumers filter client-side from the bundled index. If individual lemma addressing becomes a real need later, we can split without changing existing URLs.

## URL Structure

```
/api/index.json                  # Root: links to all resource collections, version, license
/api/lemmata/index.json          # Bundled: full lemma records (id, lemma, normalized, pos, senseCount, senses, etymology)
/api/persons/index.json          # Lightweight list (id, preferredName)
/api/persons/{id}.json           # Full person record
/api/works/index.json            # Lightweight list (id, title, sigle)
/api/works/{id}.json             # Full work record
/api/concepts/index.json         # Lightweight list (id, termDE, termEN)
/api/concepts/{id}.json          # Full concept record
/api/genres/index.json           # Lightweight list (id, termDE, termEN)
/api/genres/{id}.json            # Full genre record
/api/names/index.json            # Lightweight list (id, termDE, termEN)
/api/names/{id}.json             # Full name record
/api/texts/index.json            # Lightweight list (id, title, author, wordCount)
/api/texts/{sigle}.json          # Text metadata (no word positions, no lemmata map)
/api/index.html                  # Human-readable docs page
```

Note: No `/api/lemmata/{id}.json` — lemmata are bundled per the hybrid decision above. Genres and names added (they were missing from the original proposal but exist in the authority index).

## API Schemas

### License

Every JSON file carries `"license": "CC BY-NC-SA 4.0"` (~30 B/file). Collection index files (`lemmata/index.json`, `persons/index.json`, etc. — not the root manifest) are wrapped as:

```json
{"license": "CC BY-NC-SA 4.0", "items": [...]}
```

Individual record files carry `"license"` as a top-level key of the record object.

### Reference Field Convention

Reference fields keep their raw index syntax: `authorRef: "persons.xml#person_786"` in work records vs. `"#person_445"` in text records. The parsing convention (ID = the part after `#`) is documented on `api/index.html`. The only exception is `person.works` — see Person Object note above.

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

**Excluded:** `words` (full lemma ID array), `lemmata` (position map), `lineStarts`, and `lineEnds`. These stay in the corpus index for client-side search — too large for individual API files.

### Index Files (lightweight lists for discovery)

Each `index.json` is wrapped as `{"license": "CC BY-NC-SA 4.0", "items": [...]}` where `items` is an array of summary objects:

- **Lemmata index:** full records — `[{id, lemma, normalized, pos, senseCount, senses, etymology}, ...]` — this is where the lemma→concept link lives (~13 MB, 311 B avg per object). Individual lemma files don't exist; the bundle is the API.
- **Persons index:** `[{id, preferredName}, ...]`
- **Works index:** `[{id, title, sigle}, ...]`
- **Concepts index:** `[{id, termDE, termEN}, ...]` — full records additionally contain `altDE`, `altEN`, `altNormalized` (since authority index v1.3.0)
- **Genres index:** `[{id, termDE, termEN}, ...]`
- **Names index:** `[{id, termDE, termEN}, ...]` — full records additionally contain `conceptIds`
- **Texts index:** `[{id, title, author, wordCount}, ...]`

### Corpus Enrichment

The API does **not** cross-reference corpus statistics into authority data (e.g., "lemma X appears in N texts"). Rationale: keeps the build simple (authority index in, authority API out; corpus index in, text API out). If consumers need occurrence counts, they can derive them from the lemmata index + texts index client-side.

### Root Index (`/api/index.json`)

```json
{
  "project": "MHDBDB",
  "license": "CC BY-NC-SA 4.0",
  "contact": "mhdbdb@plus.ac.at",
  "documentation": "index.html",
  "sources": {"authorityIndex": "1.4.1", "corpusIndex": "4.1.4"},
  "collections": {
    "lemmata": {"href": "lemmata/index.json", "count": 43754},
    "persons": {"href": "persons/index.json", "count": 211},
    "works":   {"href": "works/index.json",   "count": 584},
    "concepts":{"href": "concepts/index.json", "count": 567},
    "genres":  {"href": "genres/index.json",   "count": 615},
    "names":   {"href": "names/index.json",    "count": 90},
    "texts":   {"href": "texts/index.json",    "count": 667}
  }
}
```

`sources` version strings are read from the indexes at build time (not hardcoded). There is no API schema version field: schema changes are documented, not versioned (see Design Decisions).

## Determinism & Freshness (#125)

`build-api.py` is deterministic by design: no timestamps, compact JSON output (`separators=(',', ':')` or equivalent), stable iteration order (index list order — itself deterministic since #125). This means `api/**/*.json` is byte-identical across builds when the input indexes are identical.

`api/` is a derived layer in the Data-Change-Lifecycle (see DATA-MODEL.md): any change to the source indexes must propagate through both the index rebuild and the API rebuild.

### CI Gate

`.github/workflows/data-integrity.yml` includes an API freshness step:

1. Rebuild `api/` with `python scripts/build-api.py`
2. Run `git status --porcelain -- api/` — any non-empty output means the committed `api/` is stale (this also catches untracked files, which a plain `git diff` would miss); CI fails

This step runs **before** the index freshness step. Rationale: the CI index-rebuild leaves `data/*.json.gz` dirty even for identical content (gzip is not byte-stable across builds — identical content re-compresses to different bytes), and that dirty `data/` would trip `build-api.py`'s own pre-flight (`git status --porcelain -- data/` must be clean) and abort the API build. The API output itself is built from the decompressed index content and is byte-stable, so the `api/` gate never triggers falsely. The ordering exists only to keep `data/` clean while `build-api.py` runs.

The handwritten `api/index.html` is never touched by `build-api.py`.

## Build Approach

New script: `scripts/build-api.py`
- Reads existing `data/authority-index.json.gz` and `data/corpus-index.json.gz`
- Outputs JSON files into `/api/`; wipes all `api/**/*.json` before writing (orphan protection); `api/index.html` is untouched
- Idempotent, fast (reads pre-built indexes, not XML)
- Follows patterns from `build-authority-index.py`
- Pre-flight: refuses to run on dirty `data/` (pattern from #100, `git status --porcelain -- data/` — also catches untracked files); override with `--allow-dirty`
- Runs manually: `python scripts/build-api.py`
- `npm run build:api` convenience alias in `package.json`
- ID-safety asserts at startup:
  - Authority IDs match `^[a-z]+_[A-Za-z0-9-]+$` (note: `work_WZB` is valid — uppercase after the underscore; the hyphen covers three RDF-migration UUID work ids like `work_f1576278-e28b-...`)
  - Text IDs match `^[A-Z0-9]+$`
  - Case-insensitive uniqueness check per collection (prevents `lemma_X` vs `lemma_x` collisions)
- CI: see Determinism & Freshness (#125) above

## FAIR Compliance

- **Findable:** Stable URLs, index files for discovery, API root with metadata
- **Accessible:** Open HTTP, JSON, CORS (GitHub Pages default)
- **Interoperable:** Standard URL patterns, linked identifiers (GND, Wikidata)
- **Reusable:** CC BY-NC-SA 4.0 in every response

## Out of Scope

- Server-side search
- Authentication / rate limiting
- Variants as individual resources (234k entries, map only)
- Word position data in text API (too large, stays in corpus index)
- Individual lemma files (hybrid decision — bundled index only)
- Corpus-derived enrichment (occurrence counts, text lists per lemma)
- API versioning (documented schema changes instead)
- Authority index `maps` (`conceptToLemmas`, `genreToWorks`, `genreHierarchy`) — not exposed; derivable client-side from the lemmata bundle
