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
| Texts | 666 |
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

## Open Design Question: File Volume

Splitting every resource into an individual JSON file produces ~46,000 files (43,750 from lemmata alone). Options:

| Approach | Files | Pros | Cons |
|----------|-------|------|------|
| All individual | ~46k | True REST-like API, one URL per resource | Git repo bloat, slow builds |
| Hybrid | ~2k + bundled lemmata | Individual files for persons/works/concepts/genres/names/texts; lemmata as one index | Lemmata not individually addressable |
| Bundled only | ~7 | Like current indexes, just at nicer URLs | Not a real API — consumers must filter client-side |

**Not yet decided.** Needs size estimation (how large would 43,750 lemma JSON files be?) and practical testing.

## URL Structure (proposed)

```
/api/index.json                  # Root: links to all resource indexes, version, license
/api/lemmata/index.json          # Lightweight list (id, form, pos)
/api/lemmata/{id}.json           # Full lemma with senses, grammar, variants
/api/persons/index.json
/api/persons/{id}.json
/api/works/index.json
/api/works/{id}.json
/api/concepts/index.json
/api/concepts/{id}.json
/api/texts/index.json
/api/texts/{sigle}.json          # Metadata only (no word positions)
/api/index.html                  # Human-readable docs page
```

## Build Approach

New script: `scripts/build-api.py`
- Reads existing `data/authority-index.json.gz` and `data/corpus-index.json.gz`
- Outputs individual JSON files into `/api/`
- Idempotent, fast (reads pre-built indexes, not XML)
- Follows patterns from `build-authority-index.py`

## FAIR Compliance

- **Findable:** Stable URLs, index files for discovery, API root with metadata
- **Accessible:** Open HTTP, JSON, CORS (GitHub Pages default)
- **Interoperable:** Standard URL patterns, linked identifiers (GND, Wikidata)
- **Reusable:** CC BY-NC-SA 3.0 AT in every response

## Out of Scope

- Server-side search
- Authentication / rate limiting
- Variants as individual resources (176k entries, map only)
- Word position data in text API (too large, stays in corpus index)
