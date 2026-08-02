# MHDBDB TEI Knowledge Base

Digital corpus of Middle High German literature with semantic annotations from the Mittelhochdeutsche Begriffsdatenbank (MHDBDB), University of Salzburg.

## Project Overview

The MHDBDB TEI Repository provides a comprehensive digital corpus of Middle High German literature with sophisticated semantic markup. The project combines traditional philological scholarship with modern digital humanities methods, offering both a public-facing search interface and an advanced research playground.

**Live Demos:**
- Main Site: https://dhcraft.org/mhdbdb-tei-only/
- Playground: https://dhcraft.org/mhdbdb-tei-only/playground/

**Target Audience:** Digital humanities researchers, medievalists, linguists, students of Middle High German literature

## Data Basis

### Curated Corpus
- **667 TEI files** - Complete Middle High German texts with word-level annotations
- **8 authority files** - 7 searchable controlled vocabularies (persons, works, lexicon, concepts, genres, names, variants) plus `contributors.xml` as project-internal MHDBDB team register (since 2026-04). All are RDF-derived migration snapshots now maintained in-repo (this repo is the sole master, no Salzburg re-export); `variants.xml` is corpus-derived and regenerated after corpus changes. See [TEI-MODEL-AUTH-FILES.md → Provenienz](TEI-MODEL-AUTH-FILES.md#provenienz-und-aktualitaet)
- **Pre-built indexes** - Compressed JSON (3 MB authority + 40 MB corpus) replacing runtime XML parsing
- **Static JSON API** - 2,742 plain JSON files under `/api/` (generated from the indexes) for programmatic access with stable, citable URLs; docs at [`api/index.html`](https://dhcraft.org/mhdbdb-tei-only/api/index.html) (#45)
- **Legacy Linecode sources** - 306 pre-TEI ingest files under [`sources/linecode/`](../sources/README.md) covering 199 of the 667 sigles, plus a catalog of the 9,1 GB local archive they came from. **Not normative, never indexed, never edited**: they exist to diagnose what the original Linecode-to-TEI conversion flattened (#248). The archive itself stays on KZW's OneDrive; `sources/INVENTAR-ARCHIV.md` is the access path

### Key Architecture Decision
The project migrated from runtime XML parsing to pre-built JSON indexes because large XML files caused 30-second browser load times. Pre-built indexes reduce download size by 19× and eliminate parsing overhead. Trade-off: requires Python build step when XML sources change.

## Core Features

Two interfaces over the same corpus.

The **main site** is for search and reading: lemma search with Middle High German
normalization, KWIC concordances per hit, a sortable results table with keyness and
export, a reading view with multi-lemma highlighting and a metadata panel, and an
A–Z register of all lemma pages.

The **playground** is for analysis: explorers for the authority files (persons, works,
lemmata, concepts, genres, names) and the TEI analysis tools, from multi-lemma
proximity search to the rhyme dictionary.

The complete list, with counts, examples and issue references, is
[FEATURES.md](FEATURES.md). It was duplicated here until 2026-08-02. The copy happened
to be accurate, but a second catalog is a second place to keep in step with every new
tool, and #316 asked to stop paying that twice.

## Technical Stack

### Frontend Architecture
- Vanilla JavaScript ES6+ (no frameworks)
- Pre-built JSON indexes with gzip compression
- IndexedDB caching (30-day expiration for reference data)
- Desktop-optimized (minimum 1200px width)

### Build Pipeline
- Python 3.13+ with lxml for XML processing
- Build scripts extract data from XML → JSON
- Gzip compression for production indexes

### Testing & Deployment
- Playwright end-to-end tests
- GitHub Pages hosting (static site)
- Automated deployment via GitHub Actions

## Documentation Structure

This knowledge base follows a hub-and-spoke architecture with INDEX.md as the central gateway:

### Stable Knowledge (what the project IS)

| Document | Content | Target Reader |
|----------|---------|---------------|
| **[INDEX.md](INDEX.md)** | Project overview, navigation hub | Anyone |
| **[DATA-MODEL.md](DATA-MODEL.md)** | Data sources, schemas, transformation pipeline, ingest procedure (normative phase pattern), Data-Change-Lifecycle | Data engineers |
| **[ARCHITECTURE.md](ARCHITECTURE.md)** | Technical components, data flow, storage patterns | Developers |
| **[DESIGN.md](DESIGN.md)** | Visual patterns, color system, components, CSS architecture | Developers/Designers |
| **[FEATURES.md](FEATURES.md)** | User-facing functionality descriptions | Users/Stakeholders |
| **[DEVELOPMENT.md](DEVELOPMENT.md)** | Build commands, git workflow, deployment | New contributors |
| **[RESEARCH.md](RESEARCH.md)** | Academic context, TEI/MHG standards | Researchers |
| **[DECISIONS.md](DECISIONS.md)** | Architecture Decision Records (ADRs) | Architects |
| **[CONTRACTS.md](CONTRACTS.md)** | Cross-language parity constraints, algorithm pseudocode, API contracts | Developers |
| **[TEI-MODEL.md](TEI-MODEL.md)** | Normative TEI encoding (target model), actual-vs-target comparisons, validation baseline | Data engineers, Developers |
| **[TEI-MODEL-AUTH-FILES.md](TEI-MODEL-AUTH-FILES.md)** | Authority file schemas and migration history (lexicon, persons, works, concepts, genres, names, variants) | Data engineers |
| **[LINECODE.md](LINECODE.md)** | Legacy Linecode → TEI mapping (letter-to-element table, xml:id pattern explanation, diagnostic workflows for #23) | Data engineers |
| **[POS-TAGSET.md](POS-TAGSET.md)** | Canonical `@pos` reference (19-tag target schema, compound rules, legacy mapping ART/CNJ/GRA, corpus distribution, disambiguation/migration policy §6) | Data engineers, Developers |

### Process (what's happening and why)

| Document | Content | Target Reader |
|----------|---------|---------------|
| **[ROADMAP.md](ROADMAP.md)** | Current priorities, strategic direction, what's blocked | Everyone |
| **[JOURNAL.md](JOURNAL.md)** | Chronological development log, decisions, dead ends | Developers |

The 15 files above (13 stable plus 2 process) are the complete set of promptotyping documents. (`POS-TAGSET.md` was added on 2026-06-17: the `@pos` tagset had until then only been documented in the agent skill `.gemini/skills/pos-disambiguator/` and scattered across TEI-MODEL.md and DATA-MODEL.md; it was pulled out as a citable single source of truth, and TEI-MODEL.md §5 now points to it.) `docs/features/` holds temporary, ticket-bound planning artifacts and is **not part** of the promptotyping documents, see `CLAUDE.md` → "Temporal Artifacts". `docs/playbooks/` holds reusable session procedures (autonomous issue, merge and care-work sessions): permanent, but likewise **not part** of the promptotyping documents (pulled out of `docs/features/` on 2026-07-08 because they are not ticket-bound). The user-facing help lives as `hilfe-*.html` in the frontend, not in `docs/`. Two further stores under `docs/` are also excluded: `journal-archive.md` (full text of the condensed JOURNAL entries) and `docs/data/` (two Linecode CSVs as an archival snapshot of the legacy export, see [LINECODE.md](LINECODE.md)).

### Publications (project outputs, not development docs)

Located in `/publications/` (outside `docs/`):
- `BLOG-POST-POS-WORKFLOW.md` – DHCraft blog draft on PoS disambiguation
- `BLOG-POST-WZB-PIPELINE.md` – DHCraft blog draft on the WZB (Wenzelsbibel) ingest pipeline (unpublished, v3)
- `JAHRESBERICHT-2025.md` – CLARIAH-AT annual report
- `BERICHT-REKTORAT-MITTELVERWENDUNG-2026.md` – voluntary report and letter of thanks to the rectorate about the funds released in October 2025 (#145, draft, KZW review before sending)

## Project Status

### Current Phase
Post-MVP and **in active operation**. Three things every session should know:

- **Origin (finished):** a one-off three-stage migration from the old MHDBDB (RDF triple store in Salzburg) to CSV snapshots (via SPARQL) to this TEI-only repository (`tei-transformation.py`, 2025-07-22). **Since then this repository is the sole master of all 8 authority files** (no re-export from Salzburg, no live external source).
- **Today:** an active project with ongoing data ingest (WZB/Wenzelsbibel, ARITHMETIC #92, more planned) and ongoing manual corpus corrections. Not frozen.
- **Consequence:** every change in `tei/` or `authority-files/` must carry the derived layer with it (indexes, corpus-derived `variants.xml`). The **corpus leads**, `lexicon.xml` is an index and follows (see [CONTRACTS.md → Authority Source Rules](CONTRACTS.md#f-authority-source-rules)); otherwise it drifts silently. Binding step sequence: [DATA-MODEL.md → Data-Change-Lifecycle](DATA-MODEL.md#data-change-lifecycle).

For the current index versions see [TEI-MODEL.md §11](TEI-MODEL.md#11-versionierung) (as of 2026-07-31: Corpus Index v4.2.1, Authority Index v1.8.0).

### What was finished recently

- **[JOURNAL.md](JOURNAL.md)** – chronological, with reasoning and dead ends; the full text of
  the condensed entries lives in [journal-archive.md](journal-archive.md)
- Since 2026-08-02 the [ROADMAP.md](ROADMAP.md) no longer keeps a chronicle of its own (#316); it
  says what is coming up and places ongoing work in context.

### Known Limitations
- Desktop-only interface (not mobile-responsive)
- No backend processing (all computation in browser)
- No live updates: index-backed features (search, lemma counts, playground analyses) read from pre-built `data/*.json.gz` and require a manual rebuild + deploy after each data change. Manual corpus edits appear in the TEI reading view on the next page load (the IndexedDB TEI cache revalidates against the server per load, #151) but stay invisible to search until indexes are rebuilt. The corpus itself is **not** static (active ingest plus ongoing manual correction); see the Data-Change-Lifecycle in [DATA-MODEL.md](DATA-MODEL.md#data-change-lifecycle).

### Future Directions
- Mobile optimization
- Advanced visualizations (network graphs, timelines)
- Backend integration for real-time updates (programmatic read access shipped 2026-06 as the static JSON API, #45; real-time backend remains future work)

## Links and Resources

### Project
- **Main Site:** https://dhcraft.org/mhdbdb-tei-only/
- **Playground:** https://dhcraft.org/mhdbdb-tei-only/playground/
- **GitHub Repository:** https://github.com/DigitalHumanitiesCraft/mhdbdb-tei-only
- **Issue Tracker:** https://github.com/DigitalHumanitiesCraft/mhdbdb-tei-only/issues
- **Zenodo (DOI):** https://doi.org/10.5281/zenodo.20627656 (concept DOI, always resolves to the latest version; v1.0.0: 10.5281/zenodo.20627657)

### Data Sources
- **MHDBDB Salzburg:** https://www.mhdbdb.sbg.ac.at
- **University of Salzburg:** https://www.plus.ac.at

### Standards
- **TEI P5 Guidelines:** https://www.tei-c.org/release/doc/tei-p5-doc/en/html/
- **GND (Gemeinsame Normdatei):** https://www.dnb.de/gnd
- **Wikidata:** https://www.wikidata.org

### Related Projects
- **ParzivAI:** https://github.com/ssciwr/parzivAI (Heidelberg chatbot on Middle High German language and literature; uses MHDBDB translations from the CLARIAH-AT project "MHDBDB goes AI" as training and reference data). Blog post: https://dhsalzburg.hypotheses.org/6295. Details in [RESEARCH.md → Downstream Reuse and Related Projects](RESEARCH.md#downstream-reuse-and-related-projects)

### Contact
- **Email:** mhdbdb@plus.ac.at
- **Maintainer:** Digital Humanities Craft OG
- **Project Lead:** University of Salzburg, Department of German Studies
- **License:** CC BY-NC-SA 4.0

## Quick Start

### For Users
1. Visit [Main Site](https://dhcraft.org/mhdbdb-tei-only/)
2. Enter a Middle High German word (e.g., "vriunt", "minne", "êre")
3. Browse search results and click "Text öffnen" to read full text with highlighting

### For Researchers
1. Visit [Playground](https://dhcraft.org/mhdbdb-tei-only/playground/)
2. Explore authority files (persons, works, lemmata, concepts, genres, names)
3. Try multi-lemma search with proximity analysis

### For Developers
1. Clone repository: `git clone https://github.com/DigitalHumanitiesCraft/mhdbdb-tei-only.git`
2. Install dependencies: `npm install`
3. Serve locally: `npm run serve`
4. Read [DEVELOPMENT.md](DEVELOPMENT.md) for build and deployment workflows

---

**License:** [CC BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/) | **Contact:** mhdbdb@plus.ac.at
