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
- **Legacy Linecode sources** - 306 pre-TEI ingest files under [`sources/linecode/`](../sources/README.md) covering 199 of the 667 sigles, plus a catalogue of the 9,1 GB local archive they came from. **Not normative, never indexed, never edited**: they exist to diagnose what the original Linecode-to-TEI conversion flattened (#248). The archive itself stays on KZW's OneDrive; `sources/INVENTAR-ARCHIV.md` is the access path

### Key Architecture Decision
The project migrated from runtime XML parsing to pre-built JSON indexes because large XML files caused 30-second browser load times. Pre-built indexes reduce download size by 19× and eliminate parsing overhead. Trade-off: requires Python build step when XML sources change.

## Core Features

### Main Site (Public Interface)
Simple search and reading interface optimized for students and general users:

- **Single Lemma Search** - Search across corpus with Middle High German character normalization
- **KWIC-Belege** - Pro Treffer ausklappbare Keyword-in-Context-Konkordanz mit Vers-/Zeilenangabe, Sprung zur Fundstelle (#129) und CSV-Export aller Fundstellen eines Texts (#203)
- **Tabellenansicht** - Umschaltbare Ergebnis-Tabelle (sortierbar) mit Gesamtzeile, Keyness-Spalte (Log-Likelihood), Types + Wörterbuch-Links im Lemma-Panel sowie TSV-/CSV-Export (#114)
- **Text Selection** - Include/exclude texts via checkbox interface with live filtering
- **Reading View** - Full-text reader with:
  - Multi-lemma highlighting (5 colors for concurrent searches)
  - Rich metadata panel with Wikidata integration
  - Context navigation (jump between occurrences)
  - Separate work vs author identifiers (GND/Wikidata)
- **Variant Resolution** - Automatic mapping of orthographic variants via variants.xml
- **Wörterbuch** - A–Z-Einstiegsseite (`woerterbuch.html`) zu allen 43.879 Lemma-Seiten mit Indexleiste, Pagination und Deep-Links (#117)

### Playground (Research Interface)
Advanced exploration tools for medievalists and digital humanities researchers:

- **18 Search Entry Points** - 6 authority file explorers + 12 TEI analysis tools
- **Multi-Lemma Search** - Find texts containing multiple lemmata with:
  - Document-level search (all lemmata anywhere in text)
  - Proximity search (co-occurrence within N words)
  - Same-verse search (co-occurrence within a single verse line, #106)
  - 3-stage lemma resolution (exact match → variants → prefix match in both directions, #224)
  - Color-coded results with clickable navigation to reading view
- **Authority Exploration** - Browse and search persons, works, lemmata, concepts, genres, names; the Lemmata explorer additionally offers a word-component mode for compound research, grouped by position of the component (#239)
- **TEI Analysis** - Twelve analysis tools over the pre-loaded MHDBDB corpus: multi-lemma search (document + proximity + same-verse), verse-position lemma search, word frequency, corpus-wide hapax legomena, text statistics, lemma distribution, concept distribution, text comparison, co-occurrence ranking, rhyme dictionary, verse-ending profile, curated character-naming explorer (4 works, Beta)

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
| **[DATA-MODEL.md](DATA-MODEL.md)** | Data sources, schemas, transformation pipeline, Ingest-Verfahren (normatives Phasenmuster), Data-Change-Lifecycle | Data engineers |
| **[ARCHITECTURE.md](ARCHITECTURE.md)** | Technical components, data flow, storage patterns | Developers |
| **[DESIGN.md](DESIGN.md)** | Visual patterns, color system, components, CSS architecture | Developers/Designers |
| **[FEATURES.md](FEATURES.md)** | User-facing functionality descriptions | Users/Stakeholders |
| **[DEVELOPMENT.md](DEVELOPMENT.md)** | Build commands, git workflow, deployment | New contributors |
| **[RESEARCH.md](RESEARCH.md)** | Academic context, TEI/MHG standards | Researchers |
| **[DECISIONS.md](DECISIONS.md)** | Architecture Decision Records (ADRs) | Architects |
| **[CONTRACTS.md](CONTRACTS.md)** | Cross-language parity constraints, algorithm pseudocode, API contracts | Developers |
| **[TEI-MODEL.md](TEI-MODEL.md)** | Normative TEI encoding (Soll-Modell), IST/SOLL-Vergleiche, Validierungsbaseline | Data engineers, Developers |
| **[TEI-MODEL-AUTH-FILES.md](TEI-MODEL-AUTH-FILES.md)** | Authority-File-Schemas und Migrationshistorie (lexicon, persons, works, concepts, genres, names, variants) | Data engineers |
| **[LINECODE.md](LINECODE.md)** | Legacy Linecode → TEI mapping (Letter-zu-Element-Tabelle, xml:id-Pattern-Erklärung, Diagnose-Workflows für #23) | Data engineers |
| **[POS-TAGSET.md](POS-TAGSET.md)** | Kanonische `@pos`-Referenz (19-Tag-Zielschema, Compound-Regeln, Legacy-Mapping ART/CNJ/GRA, Korpus-Verteilung, Disambiguierungs-/Migrations-Policy §6) | Data engineers, Developers |

### Process (what's happening and why)

| Document | Content | Target Reader |
|----------|---------|---------------|
| **[ROADMAP.md](ROADMAP.md)** | Current priorities, strategic direction, what's blocked | Everyone |
| **[JOURNAL.md](JOURNAL.md)** | Chronological development log, decisions, dead ends | Developers |

Die 15 Dateien oben (13 Stable + 2 Process) sind die vollständige Menge der Promptotyping-Dokumente. (`POS-TAGSET.md` 2026-06-17 ergänzt: das `@pos`-Tagset war zuvor nur im Agent-Skill `.gemini/skills/pos-disambiguator/` sowie verstreut in TEI-MODEL.md/DATA-MODEL.md dokumentiert; als zitierfähige Single Source of Truth herausgezogen, TEI-MODEL.md §5 verweist nun darauf.) `docs/features/` enthält temporäre, ticket-gebundene Planungsartefakte und ist **nicht Teil** der Promptotyping-Dokumente – siehe `CLAUDE.md` → „Temporal Artifacts". `docs/playbooks/` enthält wiederverwendbare Session-Verfahren (autonome Issue-/Merge-/Carearbeit-Sessions): dauerhaft, aber ebenfalls **nicht Teil** der Promptotyping-Dokumente (2026-07-08 aus `docs/features/` herausgezogen, da nicht ticket-gebunden). Die Nutzer-facing Hilfe lebt als `hilfe-*.html` im Frontend, nicht in `docs/`. Zwei weitere Ablagen unter `docs/` gehören ebenfalls nicht dazu: `journal-archive.md` (Volltexte der verdichteten JOURNAL-Einträge) und `docs/data/` (zwei Linecode-CSVs als Archivstand des Legacy-Exports, siehe [LINECODE.md](LINECODE.md)).

### Publications (project outputs, not development docs)

Located in `/publications/` (outside `docs/`):
- `BLOG-POST-POS-WORKFLOW.md` – DHCraft blog draft on PoS disambiguation
- `BLOG-POST-WZB-PIPELINE.md` – DHCraft blog draft on the WZB (Wenzelsbibel) ingest pipeline (unpublished, v3)
- `JAHRESBERICHT-2025.md` – CLARIAH-AT annual report
- `BERICHT-REKTORAT-MITTELVERWENDUNG-2026.md` – Freiwilliger Bericht + Dankesbrief an das Rektorat über die im Oktober 2025 freigegebenen Mittel (#145, Entwurf, KZW-Review vor Versand)

## Project Status

### Current Phase
Post-MVP und **aktiver Betrieb**. Drei Aspekte, die jede Session kennen sollte:

- **Herkunft (abgeschlossen):** einmalige, dreistufige Migration Alt-MHDBDB (RDF-Triple-Store bei Salzburg) → CSV-Snapshots (via SPARQL) → TEI-only-Repo (`tei-transformation.py`, 2025-07-22). **Seither ist dieses Repo der alleinige Master aller 8 Authority-Files** (kein Salzburg-Re-Export, keine lebende externe Quelle).
- **Heute:** aktives Projekt mit laufendem Daten-Ingest (WZB/Wenzelsbibel, ARITHMETIC #92, weitere geplant) UND laufenden händischen Korpus-Korrekturen, nicht eingefroren.
- **Konsequenz:** Jede Änderung in `tei/` oder `authority-files/` muss die abgeleitete Schicht mitziehen (Indexe, korpus-abgeleitete `variants.xml`); dabei **führt der Korpus**, `lexicon.xml` ist Index und zieht nach (siehe [CONTRACTS.md → Authority Source Rules](CONTRACTS.md#f-authority-source-rules)), sonst driftet es still. Verbindliche Schrittfolge: [DATA-MODEL.md → Data-Change-Lifecycle](DATA-MODEL.md#data-change-lifecycle).

Aktuelle Index-Versionen siehe [TEI-MODEL.md §11](TEI-MODEL.md#11-versionierung) (Stand 2026-07-31: Corpus Index v4.2.1, Authority Index v1.8.0).

### Was zuletzt fertig wurde

- **[JOURNAL.md](JOURNAL.md)** – chronologisch, mit Begründungen und Sackgassen; die Volltexte
  der verdichteten Einträge liegen in [journal-archive.md](journal-archive.md)
- Die [ROADMAP.md](ROADMAP.md) führt seit 2026-08-02 keine eigene Chronik mehr (#316); sie sagt,
  was ansteht, und ordnet Laufendes ein.

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
- **Zenodo (DOI):** https://doi.org/10.5281/zenodo.20627656 (Concept-DOI, zeigt immer auf die neueste Version; v1.0.0: 10.5281/zenodo.20627657)

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
