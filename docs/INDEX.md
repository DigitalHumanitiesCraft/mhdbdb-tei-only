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

### Key Architecture Decision
The project migrated from runtime XML parsing to pre-built JSON indexes because large XML files caused 30-second browser load times. Pre-built indexes reduce download size by 19× and eliminate parsing overhead. Trade-off: requires Python build step when XML sources change.

## Core Features

### Main Site (Public Interface)
Simple search and reading interface optimized for students and general users:

- **Single Lemma Search** - Search across corpus with Middle High German character normalization
- **KWIC-Belege** - Pro Treffer ausklappbare Keyword-in-Context-Konkordanz mit Vers-/Zeilenangabe und Sprung zur Fundstelle (#129)
- **Text Selection** - Include/exclude texts via checkbox interface with live filtering
- **Reading View** - Full-text reader with:
  - Multi-lemma highlighting (5 colors for concurrent searches)
  - Rich metadata panel with Wikidata integration
  - Context navigation (jump between occurrences)
  - Separate work vs author identifiers (GND/Wikidata)
- **Variant Resolution** - Automatic mapping of orthographic variants via variants.xml
- **Wörterbuch** - A–Z-Einstiegsseite (`woerterbuch.html`) zu allen 43.754 Lemma-Seiten mit Indexleiste, Pagination und Deep-Links (#117)

### Playground (Research Interface)
Advanced exploration tools for medievalists and digital humanities researchers:

- **15 Search Entry Points** - 6 authority file explorers + 9 TEI analysis tools
- **Multi-Lemma Search** - Find texts containing multiple lemmata with:
  - Document-level search (all lemmata anywhere in text)
  - Proximity search (co-occurrence within N words)
  - 3-stage lemma resolution (exact match → variants → partial match)
  - Color-coded results with clickable navigation to reading view
- **Authority Exploration** - Browse and search persons, works, lemmata, concepts, genres, names
- **TEI Analysis** - Nine analysis tools over the pre-loaded MHDBDB corpus: multi-lemma search (document + proximity), verse-position lemma search, word frequency, text statistics, lemma distribution, concept distribution, text comparison, co-occurrence ranking, curated character-naming explorer (4 works, Beta)

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
| **[POS-TAGSET.md](POS-TAGSET.md)** | Kanonische `@pos`-Referenz (19-Tag-Zielschema, Compound-Regeln, Legacy-Mapping ART/CNJ/GRA, Korpus-Verteilung) | Data engineers, Developers |

### Process (what's happening and why)

| Document | Content | Target Reader |
|----------|---------|---------------|
| **[ROADMAP.md](ROADMAP.md)** | Current priorities, strategic direction, what's blocked | Everyone |
| **[JOURNAL.md](JOURNAL.md)** | Chronological development log, decisions, dead ends | Developers |

Die 15 Dateien oben (13 Stable + 2 Process) sind die vollständige Menge der Promptotyping-Dokumente. (`POS-TAGSET.md` 2026-06-17 ergänzt: das `@pos`-Tagset war zuvor nur im Agent-Skill `.gemini/skills/pos-disambiguator/` sowie verstreut in TEI-MODEL.md/DATA-MODEL.md dokumentiert; als zitierfähige Single Source of Truth herausgezogen, TEI-MODEL.md §5 verweist nun darauf.) `docs/features/` und `docs/research/` enthalten temporäre, ticket-gebundene Planungs- und Recherche-Artefakte und sind **nicht Teil** der Promptotyping-Dokumente — siehe `CLAUDE.md` → „Temporal Artifacts". Die Nutzer-facing Hilfe lebt als `hilfe-*.html` im Frontend, nicht in `docs/`.

### Publications (project outputs, not development docs)

Located in `/publications/` (outside `docs/`):
- `BLOG-POST-POS-WORKFLOW.md` — DHCraft blog draft on PoS disambiguation
- `BLOG-POST-WZB-PIPELINE.md` — DHCraft blog draft on the WZB (Wenzelsbibel) ingest pipeline (unpublished, v3)
- `JAHRESBERICHT-2025.md` — CLARIAH-AT annual report

## Project Status

### Current Phase
Post-MVP und **aktiver Betrieb**. Drei Aspekte, die jede Session kennen sollte:

- **Herkunft (abgeschlossen):** einmalige, dreistufige Migration Alt-MHDBDB (RDF-Triple-Store bei Salzburg) → CSV-Snapshots (via SPARQL) → TEI-only-Repo (`tei-transformation.py`, 2025-07-22). **Seither ist dieses Repo der alleinige Master aller 8 Authority-Files** (kein Salzburg-Re-Export, keine lebende externe Quelle).
- **Heute:** aktives Projekt mit laufendem Daten-Ingest (WZB/Wenzelsbibel, ARITHMETIC #92, weitere geplant) UND laufenden händischen Korpus-Korrekturen, nicht eingefroren.
- **Konsequenz:** Jede Änderung in `tei/` oder `authority-files/` muss die abgeleitete Schicht mitziehen (Indexe, korpus-abgeleitete `variants.xml`); dabei **führt der Korpus**, `lexicon.xml` ist Index und zieht nach (siehe [CONTRACTS.md → Authority Source Rules](CONTRACTS.md#f-authority-source-rules)), sonst driftet es still. Verbindliche Schrittfolge: [DATA-MODEL.md → Data-Change-Lifecycle](DATA-MODEL.md#data-change-lifecycle).

Aktuelle Index-Versionen siehe [TEI-MODEL.md §11](TEI-MODEL.md#11-versionierung) (Stand 2026-06-12: Corpus Index v4.1.4, Authority Index v1.4.1).

### Recent Milestones
- ✅ **Phase 7 Refactoring** - Modular UI architecture
- ✅ **Corpus Index v4.0.0** - Document-level word indexing for accurate proximity search
- ✅ **Reading View** - Full-text reader with multi-lemma highlighting and Wikidata integration
- ✅ **Pre-Built Index Migration** - Eliminated runtime XML parsing
- ✅ **#32 TEI Model Consolidation** (2026-04-09/10) - Custom RELAX NG schemas (`mhdbdb.rnc`, `mhdbdb-authority.rnc`), 15M+ data transformations across 675→666 corpus files
- ✅ **#32-Followup Schema Hardening** (2026-04-14/15) - Tightened enums (`persName/@type`, `idno/@type` in authority, `msIdentifier/@corresp` mandatory), removed `<hi>` recursion from schema by flattening 36,924 nested instances across 143 corpus files, split the PL1/PL2/PL3 mega-`<p>` elements at `<pb/>` milestones (245× faster validation on PL1), CI schema-validation workflow (`schema-validation.yml`)
- ✅ **#83 Editor Attribution** (2026-04-15) - `contributors.xml` (51 persons + 2 orgs), uniform editor attribution in all 666 TEI headers via `@ref`, five texts (TKR/TKA/VTC/PUC/JT) with prominent lead-editor respStmts
- ✅ **#31 Linecode Documentation** (2026-04-15) - `docs/LINECODE.md` extracted from legacy MHDBDB linecode-to-TEI mapping
- ✅ **#48 Playground URL Routing** (2026-04-15) - Hash-based shareable/bookmarkable URLs for all playground views, including multi-lemma search state serialization
- ✅ **#56 Lemmata Explorer** (2026-04-15) - Title links to persistent lemma pages, URL bug fix, concept-based "Similar Lemmata" section
- ✅ **#62 Impressum** (2026-04-16) - Legal notice page (`impressum.html`) with Datenschutz section, footer links on all pages
- ✅ **#17 Reader View TEI-Strukturelemente** (2026-04-16) - Token-basierte `<hi rend>` CSS-Klassen (43k Compound-Werte gefixt), `<div>/<lg>/<l>/<lb>` Rendering mit Margin-Numbers, Note-Badges für `@type="year|date"`, 128/128 Tests grün
- ✅ **#52 Authority Files Card** (2026-04-16) - Playground-Sidebar-Card collapse-by-default, weniger visuelle Dominanz
- ✅ **#32-Followup vollständig 17/17** (2026-05-07) - P1-5 `idno/@type` Enum (3 kontextspezifische Patterns: `msIdentifier` / `monogr` / `person`), WZB-shelfmark-Fix (Daten vor Schema), Stage-1 PI-Cleanup auf allen 667 Korpus-Files, CI Schema-Validation triggert auch auf direkte main-Pushes
- ✅ **#68 Teil 1: `hilfe-daten-beitragen.html`** (2026-05-07) - User-facing Schema-Konversions-Leitfaden für TEI-Beitragende (deutsch); Issue tracked weitere Hilfe-Arbeit
- ✅ **WZB Skript-Reorg** (2026-05-07) - 20 WZB-Pipeline-Skripte nach `scripts/ingest/wzb/`, 4 Sackgassen nach `scripts/_archived/wzb/`
- ✅ **#79 User-facing Hilfe-Seiten** (2026-05-08) - 5 Seiten live: `hilfe.html` (Hub), `hilfe-korpussuche.html`, `hilfe-playground.html`, `hilfe-daten.html`, `hilfe-daten-beitragen.html`; Header-Nav-Eintrag „Hilfe" auf allen Hauptseiten
- ✅ **#94 Authority-Cache-Bugfix + WZB-Index-Rebuild** (2026-05-08) - Cache invalidiert jetzt korrekt bei Versions-Bump (selbstreferenzieller Vergleich gefixt); WZB live in beiden Indexen (corpus-index.json.gz damals v4.0.1, jetzt v4.1.1; authority-index.json.gz mit +4 Lemmata + work_WZB)
- ✅ **#87/#88/#89/#90 Playground TEI Textanalyse Release 1** (2026-05-11) - UX-Cleanup mit 3 broken-Button-Entfernung, Wortfrequenz-Analyse (Top-N Lemmata), Text-Statistiken (Token, Lemma-Diversität, Hapax), Lemma-Verteilung (Bar-Chart Lemma × Text). Chrome-DevTools-verifiziert mit „minne"/„êre"-Stichproben.
- ✅ **#20 Lesbarkeits-Followups** (2026-05-11) - Counter „667/667 Texte ausgewählt" auf `text-2xl font-semibold`, dedizierte blue-50-Info-Box statt unscheinbarem Tipp-Text, expliziter Default-Hinweis („Standardmäßig sind alle Texte ausgewählt")
- ✅ **#96 Metadatenanzeige + TEI-Download** (2026-05-11) - Hinweisblock am Ende des Reader-Metadaten-Panels mit Download-Link auf `tei/<SIG>.tei.xml`; Wikidata-Link für `authorId === 'person_anonym'` unterdrückt (KZW-Comment)
- ✅ **#97-#100 Playground-Cleanups + Pre-flight-Check** (2026-05-11) - Corpus-Index-Property-Drift behoben (`teiManager.corpusIndex` gespiegelt), ~700 Zeilen Dead Code aus `tei-ui.js` entfernt (581 → 404 Z.), `git status --porcelain`-Pre-flight im Index-Build verhindert dirty Builds
- ✅ **WZB Schema-Konformität in `works.xml`** (2026-05-11) - Julias Fix `af72bd261` für den initial fehlerhaften `<ref>`/`<note type=>`-Block im work_WZB-Eintrag plus Normdaten-Ergänzung (Wikidata Q476495, GND 4117632-7, HSC werke/4577); CI-Schema-Validation seit `26a4cd882` wieder grün
- ✅ **#91 Zenodo-Stub** (2026-05-11) - `CITATION.cff` mit konservativem Lead-Author-Eintrag (KZW); README-DOI-Badge wartet auf Zenodo-Aktivierung + ersten getaggten Release
- ✅ **#26 pb-Insertion** (2026-05-11) - 1293 `<pb>`-Elemente über 14 TEI-Files via Linecode-Handover-Templates; #102 (BDK) + #103 (DIS) als Followups separat closed
- ✅ **#85 div-Wrapper-Umbrella** (closed 2026-05-12) - Kat. 2 (7 Lieder) bereits in `ef939f530`; Kat. 3 (DJEM, DES2 als `<div type="parallel">`, DUB nach `u=1`-Klärung); 13 MBS-Serie strukturell implizit-OK
- ✅ **#101 Reading-View-Render-Policy** (2026-05-12, Julia) - `milestone[@unit="verse"]` → superscript verse-marker, `div[@type="chapter"]` → `<h3 class="section-head">`, `.hi-initial` Sonderformatierung entfernt; Marginalia/Glossen/Rubrum unstylisiert
- ✅ **#73 Lemma-Linking MWB + Lexer** (2026-05-12) - Beide Wörterbücher über Wörterbuchnetz-API (`/dictionaries/{MWB|Lexer}/lemmata/{form}`); ersetzt Julias initialen, defekten MWB-Suchlink (POST-only-Form öffnete leere Suchseite); Section nur sichtbar wenn min. 1 Treffer
- ✅ **WZB Pentateuch-Scope** (2026-05-12, Julia) - WZB-Titel + works.xml + projectDesc auf „Wenzelsbibel (Pentateuch: Gen–Dtn, Cod. 2759–2764)" präzisiert; Authority-Index-Rebuild
- ✅ **Blog-Post-Draft WZB-Pipeline** (2026-05-12, Julia + C. Pollin) - `publications/BLOG-POST-WZB-PIPELINE.md` v3: 30J. MHDBDB-Kontext, LOD, dreiphasige LLM-Pipeline, böhmische Schreibkonventionen; unpublished
- ✅ **#105 Authority-Files-Counter** (2026-05-12) - Stats-Block auf Startseite 7 → 8 angeglichen; Playground-Loader-Status bleibt 7 (technisch korrekt, `contributors.xml` nicht im authority-index)
- ✅ **#47.3 Lemmasuche nach Versposition** (2026-05-12) - Neuer Playground-Eintrag unter Multi-Lemma-Suche, findet Lemmata am Versanfang/Versende; Corpus-Index v4.1.0 mit `lineStarts[]`/`lineEnds[]` (1,359,789 `<l>` über 603 Versdichtungs-Texte, +6 MB gz); Chrome-verifiziert mit echten Reimpaaren in AGS
- ✅ **#47 R2 Begriffs-Verteilung** (2026-05-12) - Neuer Playground-Eintrag analog Lemma-Verteilung (#90), aber concept-basiert. Datenpfad: concept → senses → lemmata → texts. Verifiziert mit „Sterben" (682 Lemmata, 659 Texte, 103.657 Vorkommen) und englischer Eingabe „love" (Intimität, mit alternativen Candidates)
- ✅ **#47 Umbrella TEI Textanalyse geschlossen** (2026-05-12) - R1 + R2-Hauptpunkt shipped; Folgepunkte #107 Kookkurrenz-Ranking + #108 Textvergleich (beide inzwischen geshippt, siehe nächster Eintrag), #106 Vers-Boundary-Features (Punkt 1 als Rolling-Backlog) und #109 FWF-Einzelprojekt für NER und tiefere Analysen ausgelagert
- ✅ **#107 Kookkurrenz-Ranking + #108 Textvergleich** (2026-05-15) - Zwei neue Playground-TEI-Analyse-Modi: häufigste Nachbar-Lemmata pro Lemma (`cooccurrence-ranking.js`) bzw. gemeinsame/exklusive Lemmata zweier Texte (`text-comparison.js`); damit 8 TEI-Analyse-Werkzeuge im Playground
- ✅ **#59 Erweiterte Figurenbezeichnungen (Beta)** (2026-06-11) - Neuntes TEI-Analyse-Werkzeug: kuratierte Eigennamen, Antonomasien und Epitheta je Figur aus Linda Beutel-Thurows Naming-analysis (ENE/IW/ROL/TRO, 10.506 Belegstellen); eigener vorgebauter Index `data/naming-index.json.gz` (110 KB) via `scripts/ingest/naming/01-fetch-and-build-index.py`; sichtbare Attribution mit DOI, Chrome-verifiziert
- ✅ **#125 Deterministische Index-Builds + CI-Freshness-Gate** (2026-06-12) - Identischer Quellstand erzeugt byte-identische Indexe (kein `generatedAt`, sortiertes glob, gzip `mtime=0`); CI-Workflow `data-integrity.yml` (konsolidiert die früheren `schema-validation.yml` + `index-version-check.yml`) rebuildet variants.xml + beide Indexe bei jedem Daten-PR und blockt vergessene Rebuilds; Dependency-Pins in `requirements.txt`; Corpus v4.1.4, Authority v1.4.1
- ✅ **#45 Statische JSON-API** (2026-06-12) - FAIR-orientierte JSON-API unter `/api/` (2.742 Dateien, ~14 MB): Root-Manifest, Lemmata-Bundle (43.754 volle Records), Einzelressourcen für Persons/Works/Concepts/Genres/Names/Texte; deterministischer Build (`scripts/build-api.py`) + CI-Freshness-Gate; Doku-Seite `api/index.html`

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
