# Development

This document describes the development workflow, build processes, and deployment procedures for the MHDBDB TEI Repository.

## Prerequisites

- **Node.js 16+** (for npm scripts and testing)
- **Python 3.13+** with lxml (for building pre-built indexes)
- **Web Browser** (Chrome/Chromium preferred for testing)
- **Git** (for version control)

**Note:** Pre-built indexes are included in repository, so Python is only needed if modifying source XML files.

## Project Setup

```bash
# Clone repository
git clone https://github.com/DigitalHumanitiesCraft/mhdbdb-tei-only.git
cd mhdbdb-tei-only

# Install dependencies
npm install

# Start development server
npm run serve
# Opens on http://localhost:8080
```

### Directory Structure

```
mhdbdb-tei-only/
├── assets/                # Main site static assets
│   ├── css/               # Stylesheets (korpus.css, tailwind)
│   ├── js/                # Main site JavaScript
│   │   ├── app.js         # Application entry point
│   │   ├── site-chrome.js # Shared nav/footer behaviour (mobile menu, current-year, clear-site-data) — loaded on every page
│   │   ├── search/        # Search engine
│   │   ├── rendering/     # TEI text reader, text renderer
│   │   ├── storage/       # TEI cache manager
│   │   └── lib/           # Shared utilities (corpus-loader, text-normalizer, lemma-match)
│   └── images/            # Static images
├── includes/              # Nav/footer/matomo single-source partials (_nav.html, _footer.html, _matomo.html) → build-injected by scripts/build-pages.py
├── authority-files/       # 8 XML authority files (inkl. contributors.xml)
├── tei/                   # TEI corpus files
├── data/                  # Pre-built indexes (generated)
├── scripts/               # Python build scripts
├── playground/            # Playground interface (self-contained sub-app)
├── lemma/                 # Persistent lemma pages (Issue #42)
├── publications/          # Project outputs (blog posts, reports)
├── testing/               # Playwright tests
├── docs/                  # Documentation hub
├── schema/                # RELAX NG schemas (mhdbdb.rnc, mhdbdb-authority.rnc, examples)
├── index.html             # Landing page
├── korpus.html            # Main site search + reading view
├── woerterbuch.html       # Wörterbuch: A–Z-Register aller Lemmata (#117)
├── impressum.html         # Legal notice (#62)
├── barrierefreiheit.html  # Barrierefreiheitserklärung
├── hilfe.html             # Hilfe-Hub (entry point)
├── hilfe-korpussuche.html # Korpus-Suche-Anleitung
├── hilfe-playground.html  # Playground-Anleitung
├── hilfe-daten.html       # Daten-Erklärung für Leser:innen
├── hilfe-daten-beitragen.html  # Schema-Konversions-Guide für TEI-Beitragende (#68 Teil 1)
├── hilfe-schema.html      # Normatives TEI-Schema + Prism-Beispiele (#78)
└── 404.html               # Lemma-page redirect (GitHub-Pages-Workaround)
```

## Building Pre-Built Indexes

Pre-built indexes are included in repository. Rebuild only when modifying source XML files.

### When to Rebuild

> **Kanonische, geordnete Schrittfolge:** [DATA-MODEL.md → Data-Change-Lifecycle](DATA-MODEL.md#data-change-lifecycle). Die Liste hier ist nur die Kurzfassung der Trigger.

**Authority Index:**
- Authority XML files modified
- Cross-references added/changed
- New GND/Wikidata identifiers

**Corpus Index:**
- TEI files added/removed/modified
- Word annotations changed

**Variants:**
- TEI corpus modified (new orthographic forms)
- Usually paired with corpus index rebuild

### Build Commands

```bash
# Build authority index (consumes authority-files/variants.xml, no extraction step)
python scripts/build-authority-index.py
# Output: data/authority-index.json.gz (~3 MB)

# Build corpus index
python scripts/build-corpus-index.py
# Output: data/corpus-index.json.gz (~40 MB, v4.1.x)

# Validate indices
python scripts/validate-indices.py

# Build static JSON API from the two indexes (#45) — alias: npm run build:api
python scripts/build-api.py
# Output: api/ (2,742 plain JSON files, ~14 MB). Single-shot target, needs a clean data/.
# Run build:api ALONE to regenerate only the API from the already-committed indexes
# (no index rebuild). To rebuild the indexes AND the API together (kept in lockstep),
# use `npm run build:data` / `npm run build` (see below).
```

### Frontend Build Commands

```bash
# Rebuild the purged Tailwind stylesheet (run after new utility classes appear in HTML/JS)
npm run build:css        # assets/css/tailwind-input.css → assets/css/tailwind-output.css (--minify)

# Bundle vendored JS dependencies (PrismJS, pako, Dexie — no runtime CDN dependencies;
# sources pinned via package.json/package-lock, output committed under assets/vendor/)
npm run build:vendor     # node scripts/build-vendor.js

# Re-inject the shared nav + footer into every registered page after editing
# includes/_nav.html or includes/_footer.html (NOT the pages directly):
python scripts/build-pages.py            # rewrite changed pages (idempotent)
python scripts/build-pages.py --check    # exit 1 if any page is out of sync (drift gate)

# Build the full derived layer in dependency order: corpus index → variants.xml → authority index → API
npm run build:data       # build:corpus && extract-variants --apply && build:authority && build-api --allow-dirty
# build-api runs with --allow-dirty here because the just-rebuilt indexes in data/ are still uncommitted (dirty)

# Aggregate: CSS + vendor + the full data chain (npm run build now includes build:data)
npm run build            # build:css && build:vendor && build:data
```

**Note on variants:** `authority-files/variants.xml` is corpus-derived. Regenerate it with `python scripts/sync/extract-variants.py --apply` after the corpus gains new orthographic forms, then rebuild the authority index and bump its version. Full step sequence: [DATA-MODEL.md → Data-Change-Lifecycle](DATA-MODEL.md#data-change-lifecycle).

### Version Increment

After significant changes, increment version in build script to force browser cache invalidation:

```python
# In build-authority-index.py / build-corpus-index.py liegt die Version als
# Inline-Dict-Literal im Index, z.B. 'version': '1.4.0' (KEINE VERSION-Konstante).
# Muss zusammen mit der passenden Konstante in assets/js/lib/corpus-loader.js
# (INDEX_VERSION / AUTHORITY_INDEX_VERSION) gebumpt werden; check-index-versions.py
# erzwingt Paritaet. Aktueller Stand siehe TEI-MODEL.md §11.
```

## Testing

### Playwright Tests

```bash
npm test              # Run all tests (headless), 5,0 bis 5,3 min (6 Worker)
npm run test:changed  # Nur Specs, die seit origin/main angefasst wurden
npm run test:quick    # Drei Specs als Rauchprobe, 29 Tests (main-site, playground, corpus)
npm run test:ui       # Interactive mode
npm run test:debug    # Debug with breakpoints
npm run test:headed   # Visible browser
npm run report        # View HTML report
```

Positionale Argumente sind bei Playwright **Reguläre Ausdrücke gegen den Dateipfad**, keine Dateinamen. Unverankert zog der Filter `corpus.spec.js` in `test:quick` deshalb auch `playground-corpus.spec.js` und `search-with-corpus.spec.js` mit, also 47 Tests in fünf Dateien statt 29 in drei, darunter ausgerechnet die Datei mit den meisten `waitForTimeout`-Aufrufen. Seit #323 sind die Filter hinten mit `$` verankert und vorne durch das Präfix `tests.` diszipliniert. Ein `^` wäre falsch und würde nichts mehr finden: Playwright prüft gegen den **absoluten** Pfad, nachgemessen (`^main-site\.spec\.js$` und `^tests.main-site\.spec\.js$` liefern beide null Tests, `tests.main-site\.spec\.js$` liefert 14). Wer die Auswahl ändert, zählt sie mit `-- --list` nach; das startet den `webServer` nicht und kostet deshalb nur Sekunden.

`test:changed` (`--only-changed=origin/main`) ist der Alltagsbefehl beim Arbeiten an einem Zweig: es läuft nur, was der Zweig angefasst hat. **Vor dem Push bleibt `npm test` Pflicht.** `--only-changed` verfolgt zwar die Node-Importe der Specs, aber keine Spec importiert Projektcode über Node. Alles, was die Specs prüfen, erreichen sie zur Laufzeit: Site-Code über den Browser (`await import('/assets/js/…')` innerhalb von `page.evaluate`), Python über `execSync`, Fixtures und Vendor-Dateien über den Pfad. Blind ist der Befehl deshalb für:

| Was | geprüft von | wie erreicht |
|---|---|---|
| `assets/js/`, `playground/js/`, `tei/`, `data/` | fast alle Specs | Browser, `localhost:8080` |
| `scripts/mhg_normalizer.py` | `normalization-parity.spec.js` | `execSync` |
| `scripts/build-corpus-index.py` | `position-parity.spec.js` | `importlib` aus dem Helper heraus |
| `testing/helpers/extract_word_positions.py` | `position-parity.spec.js` | `execSync` |
| `tei/PL1.tei.xml`, `tei/OVG.tei.xml` | `position-parity.spec.js` | Pfad (Python) und Browser |
| `testing/fixtures/*.tei.xml` | `position-parity.spec.js` | Pfad |
| `assets/vendor/`, alle HTML-Seiten | `vendor.spec.js` | `readdirSync`/`readFileSync` |

Die Python-Zeilen sind die unangenehmsten, weil man dort das Gegenteil erwartet. `scripts/mhg_normalizer.py` und `scripts/build-corpus-index.py` sind je eine Hälfte der Paritäts-Zusagen aus den Hard Constraints in `CLAUDE.md`, und die beiden `*-parity.spec.js` sind ihre Wächter. Beim Build-Skript ist der Weg zusätzlich verdeckt: `extract_word_positions.py` ist ein Shim, der die echte `extract_word_data()` per `importlib` lädt, statt sie nachzubauen. Wer die Python-Seite ändert und `test:changed` laufen lässt, bekommt null Specs, also gerade nicht den Test, der die Änderung prüft (nachgemessen für `mhg_normalizer.py`).

Für dieses Repo besonders relevant sind `tei/` und `data/`: das sind bei laufendem Ingest die am häufigsten geänderten Verzeichnisse, und beide sind blind, weil sie über `localhost:8080` geladen werden. Zwei Fallstricke am Ref: `origin/main` muss existieren (in einem Shallow Clone nicht der Fall), und er muss aktuell sein. Wer länger nicht gefetcht hat, vergleicht gegen einen alten Stand und bekommt zu viele oder zu wenige Specs, deshalb vorher `git fetch origin main`. Bleibt die Auswahl leer, endet der Befehl mit Exit 0 (gemessen, Playwright 1.55.1): `--pass-with-no-tests` braucht es nicht.

**Test configuration:** `testing/playwright.config.js`
- Always use `npm test` – never `npx playwright test` from the project root (config and `baseURL` live in `testing/`)
- Automated web server startup (port 8080)
- Headless Chrome with `--disable-web-security`
- 60-second timeout per test
- **6 Worker lokal, 2 in der CI** (#323), auf schwächeren Geräten mit `npm test -- --workers=2` überschreibbar: 20,4 min bei einem Worker gegen 5,0 bis 5,3 min bei sechs, über dieselben 276 Tests, fünf Läufe. Die Begründung für beide Zahlen steht als Kommentar in der Config; kurz: der Engpass ist der single-threaded `http-server` und der Chromium-Heap, nicht die Kernzahl, und Standard-CI-Runner haben zu wenige vCPUs für sechs
- **`retries: 1`** (überall, auch in der CI) und `failOnFlakyTests: true` dazu. Der Retry existiert nur, damit ein Timing-Flake unter sechs Workern einen Trace hinterlässt; ohne `failOnFlakyTests` würde er zugleich den Lauf schönen, denn Playwright endet mit Exit 0, sobald ein Test im zweiten Versuch grün wird. Mit der Option bleibt der Lauf rot, und die Trace-Datei liegt trotzdem da
- **`fullyParallel: false` ist Absicht.** `search-normalization.spec.js` teilt eine in `beforeAll` angelegte Seite über alle Tests der Datei, um den Index einmal statt vierzehnmal zu laden. Test-Parallelität würde die Seite nicht kaputtmachen (Playwright führt `beforeAll` pro Worker erneut aus), wohl aber den Spareffekt: der Index würde bis zu sechsmal geladen

### Test File Inventory

Vollständigkeit gegen `testing/tests/` gatet `scripts/audit/check-doc-inventories.py` (läuft in `no-cdn-check.yml`, lokal ohne Abhängigkeiten aufrufbar; dasselbe Skript prüft auch die Skript-Tabelle weiter unten). Eine neue Spec ohne Zeile hier macht die CI rot: die Tabelle ist der einzige Ort, an dem steht, wofür eine Spec da ist. Bis #329 fehlten zehn von dreißig.

| File | Category | What it tests |
|------|----------|--------------|
| `main-site.spec.js` | Main site | Landing page, search page loading, search results, reading view |
| `search-engine.spec.js` | Main site | SearchEngine class: resolution, filtering, deduplication |
| `search-normalization.spec.js` | Main site | MHG normalization functions in browser context |
| `search-with-corpus.spec.js` | Main site | Search against real corpus data |
| `reading-view.spec.js` | Main site | TEI reading view rendering, highlighting, navigation |
| `results-table.spec.js` | Main site | Corpus search results table view (#114): columns, sorting |
| `tei-caching.spec.js` | Main site | IndexedDB TEI cache behavior |
| `error-handling.spec.js` | Main site | Graceful error handling |
| `woerterbuch.spec.js` | Main site | A–Z-Register über den Authority-Index, Pagination, Deep-Links (#117) |
| `lemma-page.spec.js` | Lemma pages | URL parsing, data rendering, external links |
| `playground.spec.js` | Playground | Authority explorers, TEI analysis, UI navigation |
| `playground-authority-index.spec.js` | Playground | Authority index loading, data structure integrity |
| `playground-corpus.spec.js` | Playground | Corpus index loading, search functions |
| `concept-distribution.spec.js` | Playground | Concept distribution analysis (concept → senses → lemmata → texts) |
| `cooccurrence-ranking.spec.js` | Playground | Kookkurrenz-Ranking und Homographen-Auflösung der Multi-Lemma-Suche (#163/#164) |
| `proximity-and-resolution.spec.js` | Playground | Nähesuche-Fenster bei drei und mehr Lemmata, Überlappungs-Dedup, Lemma-Auflösung (#169) |
| `multi-lemma-verse.spec.js` | Playground | Suchmodus „Im selben Vers" über `lineStarts[]`/`lineEnds[]` (#106) |
| `rhyme-dictionary.spec.js` | Playground | Reim-Wörterbuch: Versende-Scan plus Suffix-Heuristik (#106) |
| `verse-ending-profile.spec.js` | Playground | Versendings-Profil: Top-N Lemmata an Versenden, Scope-Selector (#106) |
| `hapax-legomena.spec.js` | Playground | Korpusweite Hapax/Dis/Tris-Aggregation, Filter-Toolbar, Detail-Panel (#196) |
| `word-component-search.spec.js` | Playground | Wortbestandteil-Modus im Lemmata-Explorer für Komposita-Recherche (#239) |
| `naming-explorer.spec.js` | Playground | Figurenbezeichnungen: Route, Werk-/Figur-Auswahl, Kategorie-Tabs, Pflicht-Attribution (#59) |
| `normalization-parity.spec.js` | Cross-cutting | Python/JS normalizer agreement (see [CONTRACTS.md](CONTRACTS.md#a-mhg-normalization-parity)) |
| `lemma-matching.spec.js` | Cross-cutting | Lemma highlight matching exactness, #130 (see [CONTRACTS.md](CONTRACTS.md#b1-lemma-highlight-matching-contract)) |
| `position-parity.spec.js` | Cross-cutting | Python/JS word-position agreement, #131 (see [CONTRACTS.md](CONTRACTS.md#b-position-counting-contract)) |
| `site-chrome.spec.js` | Cross-cutting | Build-injected nav/footer + mobile-menu (`build-pages.py`) |
| `vendor.spec.js` | Cross-cutting | Runtime-Bibliotheken kommen aus `assets/vendor/`, keine CDN-Abhängigkeit (Laufzeit-Gegenstück zu `no-cdn-check.yml`) |
| `cross-reference-test.spec.js` | Data integrity | Authority/corpus cross-reference validity |
| `corpus.spec.js` | Data integrity | Corpus index structure validation |
| `visual-mobile-test.spec.js` | Visual | Responsive Screenshots + Touch-Target-Größe über mehrere Viewports (iPhone-SE 375px … Desktop 1440px) |

### CI: Data Integrity

**Workflow:** `.github/workflows/data-integrity.yml` (konsolidiert seit #125 die früheren `schema-validation.yml` + `index-version-check.yml`)
**Triggers:** PRs + main-Pushes, die `schema/`, `tei/`, `authority-files/`, die drei Index-`.json.gz` (corpus/authority/naming), `api/**`, die Build-Skripte (`build-*-index.py`, `build-api.py`, `mhg_normalizer.py`), `scripts/sync/`, `scripts/audit/`, `scripts/ingest/naming/`, `corpus-loader.js` oder `requirements.txt` berühren. Plus `workflow_dispatch`.

**Elf Checks, billig → teuer (fail fast);** vorab bestimmt ein Hilfs-Step die Diff-Base (PR: Base-Branch-Tip, Push: `event.before`) für die Checks 2 und 9:

1. **Index-Versions-Konstanten** (#47.3) – Build-Skripte + `corpus-loader.js` müssen dieselben Versionen nennen, sonst greift die IndexedDB-Cache-Invalidierung nicht. Lokal: `python scripts/audit/check-index-versions.py`.
2. **Index-Versions-Bump-Gate** (#154) – hat sich der dekomprimierte Inhalt von corpus-/authority-index gegenüber der Diff-Base geändert, muss auch der `version`-String geändert sein; sonst wurde der Drei-Stellen-Bump vergessen und der Dexie-Cache invalidiert nicht (Nutzer behalten bis zu 30 Tage den alten Index). Lokal: `python scripts/audit/check-index-version-bump.py --base origin/main`. Ohne bestimmbare Diff-Base (workflow_dispatch, Force-Push) wird der Check übersprungen.
3. **RNC→RNG sync check** (P2-14) – regeneriert `.rng` aus `.rnc`, Diff = Fail.
4. **TEI-P5-Pin** – das committete `tei_all.rng` wird gegen die gepinnte Version (4.11.0) geprüft.
5. **Freshness variants.xml** (#125) – `extract-variants.py --apply` muss die committete Datei byte-identisch reproduzieren („Korpus geändert, variants.xml vergessen"). Blockierend VOR Check 7: der Index-Vergleich allein kann variants-Drift nicht erkennen.
6. **Freshness API** (#45) – `build-api.py` muss das committete `api/` byte-identisch reproduzieren (plain JSON, `git diff` reicht). Vor dem Index-Gate, weil der CI-Index-Rebuild `data/` gz-dirty hinterlässt.
7. **Freshness Indexe** (#125, Rebuild-and-Compare) – beide Indexe werden frisch gebaut und dekomprimiert mit dem committeten Stand verglichen („Quelle/Build-Skript geändert, Rebuild vergessen"). Funktioniert nur, weil die Builds deterministisch sind.
8. **Naming-Index Konsistenz** (#152) – `source.commit`-Provenienz vorhanden + alle `works[].sigle` existieren als `tei/<SIG>.tei.xml` (ein Sigle-Rename bräche den Reader-Link im Playground sonst still). Offline, läuft immer. Lokal: `python scripts/audit/check-naming-index.py`.
9. **Freshness naming-index** (#152, Rebuild-and-Compare) – Rebuild aus dem im Index gepinnten `source.commit` muss den committeten Stand reproduzieren. Läuft NUR, wenn naming-Pfade sich gegenüber der Diff-Base geändert haben (externer Fetch nach `lindabeutel/Naming-analysis`; keine externe Netz-Abhängigkeit auf jedem Daten-PR, #125-Prinzip).
10. **Cross-Reference-Integrity** (#44/#115/#152) – dangling Refs außerhalb `lexicon.xml` brechen den Build; `lexicon.xml` wird als **ID-Set-Ratsche** gegen die committete Baseline (`scripts/audit/lexicon-baseline.json`) gegated: jede ID außerhalb der Baseline = rot (auch bei kompensierendem Backfill im selben PR), tolerierter Altbestand = grün, geschrumpfter Ist-Stand = `::warning` → `--update-baseline` ausführen und Datei-Diff mitcommitten.
11. **Zweistufige RelaxNG-Validierung** (P2-13) – Stage 1 `tei_all.rng` (Warnungen, #30-Baseline), Stage 2 `mhdbdb.rng`/`mhdbdb-authority.rng` (hartes Gate). Als teuerster Check bewusst zuletzt.

**Hinweis Dependency-Pins:** lxml und rnc2rng sind in `requirements.txt` gepinnt (Single Source – CI installiert daraus), damit Serialisierungsänderungen neuer Versionen nicht als Drift-Fehlalarm erscheinen. Lokal `pip install -r requirements.txt` verwenden; beim Pin-Bump danach `variants.xml` regenerieren und die `.rng` neu erzeugen.

**Debugging failures:**
- Versions-Drift → `python scripts/audit/check-index-versions.py` lokal, Konstanten angleichen
- Bump vergessen (#154) → Version in `build-*-index.py` + `corpus-loader.js` bumpen, Index rebuilden, alles in einem Commit
- RNG drift → `python -m rnc2rng schema/mhdbdb.rnc schema/mhdbdb.rng` lokal, committen
- variants-/Index-Freshness → Data-Change-Lifecycle in DATA-MODEL.md abarbeiten (regenerieren, rebuilden, bumpen, alles in einem Commit)
- API-Freshness → `python scripts/build-api.py` lokal, `api/` mitcommitten
- Stage 2 fail → `python scripts/audit/validate-corpus.py --sample <SIGLE>` lokal
- TEI version mismatch → `EXPECTED` im Workflow + `schema/README.md` bumpen

### CI: Release Version Check (Zenodo)

**Workflow:** `.github/workflows/release-version-check.yml`
**Triggers:** Push von Tags `v*` + `workflow_dispatch`.

**Hintergrund (#91, 2026-06-10):** Zenodo zieht die Record-Metadaten beim Release aus `.zenodo.json`. Ein dort hartkodiertes, beim Taggen vergessenes `version`-Feld produziert einen Zenodo-Record mit falscher Versionsangabe – ohne Fehler, ohne Warnung. Deshalb zwei Regeln: `.zenodo.json` hat **kein** `version`-Feld (Zenodo nimmt dann automatisch den Tag-Namen; der Git-Tag ist Single Source of Truth), und `CITATION.cff → version` muss dem Tag entsprechen (speist GitHubs „Cite this repository"-Widget).

**Timing:** Der Check läuft beim Tag-Push, der Zenodo-Webhook feuert erst beim Publizieren des GitHub-Releases. Scheitert der Check, einfach Tag löschen, `CITATION.cff` fixen, neu taggen – Zenodo hat dann noch nichts gesehen.

**Release-Ablauf:** (1) `CITATION.cff`: `version` + `date-released` bumpen (ggf. `.zenodo.json`-Contributors nachziehen), (2) `git tag vX.Y.Z && git push origin vX.Y.Z`, (3) GitHub-Release erstellen (`gh release create vX.Y.Z`) → Zenodo archiviert automatisch eine neue Version unter dem Concept-DOI `10.5281/zenodo.20627656`.

**Lokal:** `python scripts/audit/check-release-version.py v1.1.0`

### Audit Scripts Reference

Diagnose- und Validierungs-Skripte in `scripts/audit/`. Vollständigkeit gegen das Verzeichnis gatet `scripts/audit/check-doc-inventories.py`, dasselbe Skript wie für die Spec-Tabelle oben. Bis #329 nannte diese Tabelle 11 von 22 Skripten, darunter keines der beiden Em-Dash- und No-CDN-Gates, die in jeder CI laufen.

Zwei Sorten stehen hier gemischt, und der Unterschied ist der wichtigste: **Gates** haben einen Exit-Code und werden von einem Workflow gerufen, **Diagnosen** messen etwas für einen Menschen und laufen von Hand. Wo ein Workflow ruft, steht er in der Zeile.

| Script | Zweck |
|--------|-------|
| `validate-corpus.py` | Two-stage RelaxNG-Validierung aller 667 Korpus- + 8 Authority-Files (gerufen von data-integrity.yml) |
| `check-index-versions.py` | Versions-Konsistenz Build-Skripte ↔ Loader, gerufen von `data-integrity.yml` (Details oben) |
| `check-index-version-bump.py` | Versions-Bump-Gate (#154): Index-Inhalt gegenüber `--base` geändert ⇒ `version`-String muss mitgeändert sein. Gerufen von `data-integrity.yml` (Details oben) |
| `check-release-version.py` | Release-Tag ↔ `CITATION.cff`-Version; verbietet `version`-Feld in `.zenodo.json`. Gerufen von `release-version-check.yml` (Details oben) |
| `audit-authority-files.py` | Struktur, Querverweise und Datenqualität **innerhalb** der 8 Authority-Files (authority→authority; ID-Muster, verwaiste Referenzen, strukturelle Konsistenz) |
| `check-authority-cross-refs.py` | **Korpus→Authority** Cross-Ref-Integrität: dangling `@lemmaRef`/`@ana`/`@corresp`/`@ref`/`@target`. `--check` = CI-Gate in `data-integrity.yml`: unresolved refs außerhalb `lexicon.xml` = sofort rot; `lexicon.xml` als ID-Set-Ratsche gegen `lexicon-baseline.json` (#152) – neue IDs rot, Altbestand grün; `--update-baseline` zieht die Ratsche nach. Einziger Detektor der Derived-File-Drift (#44/#115) |
| `check-naming-index.py` | Naming-Index-Konsistenz (#152): `source.commit` vorhanden + alle `works[].sigle` existieren in `tei/`; `--print-source-commit` liefert den Pin für die Workflows. Gerufen von `data-integrity.yml` und `naming-index-update.yml` (Details oben) |
| `audit-tei-corpus.py` | Korpus-weite Stichproben (z.B. fehlende `<l>`/`<lg>`, ungewöhnliche xml:id-Pattern, Encoding-Anomalien) |
| `check-lexicon-senses.py` | `lexicon.xml`-Sanity: Lemmata ohne `<sense>`, Senses ohne `conceptIds` |
| `doc-count-audit.py` | Drift-Detektor zwischen tatsächlichen Korpus-/Authority-Zahlen und den in der Doku verankerten Werten. Heuristik: Window ±2 absolut oder ±2 % relativ, strikter Keyword-Anchor unmittelbar nach der Zahl. Läuft als Health-Check-Werkzeug von Hand, kein Workflow ruft es |
| `check-doc-inventories.py` | Inventar-Gate (#329) für beide Tabellen dieser Datei: „Test File Inventory" gegen `testing/tests/`, „Audit Scripts Reference" gegen `scripts/audit/`, je in beide Richtungen. Nur stdlib, gerufen von `no-cdn-check.yml`; `--selftest` prüft den Scanner an künstlichen Eingaben |
| `check-no-cdn.py` | Gate in `no-cdn-check.yml`: keine externen `<script src>` in committeten HTML-Seiten, Runtime-Bibliotheken kommen aus `assets/vendor/` (#78). Laufzeit-Gegenstück ist `vendor.spec.js` |
| `check-no-em-dash.py` | Gate in `no-cdn-check.yml` (#140): keine Em-Dashes in user-sichtbarem Text, Kommentare ausgenommen. `--selftest` sichert den Scanner gegen Mutationen ab, weil mehrere frühere Fassungen Fail-opens waren, die alle Testfälle bestanden |
| `check-author-refs.py` | Autorangaben im `titleStmt` gegen `persons.xml` (#228), sechs sich überschneidende Fehlerklassen. Anlass waren sieben Texte mit `<author ref="#person_N"/>` **ohne** Textinhalt: schema-valide, Referenz intakt, im Frontend trotzdem autorlos |
| `classify-lexicon-backfill.py` | Read-only-Klassifikation der offenen `lexicon.xml`-Lücken (#115/#44). Gruppiert jede unaufgelöste Referenz nach Lemma und trennt „Eintrag fehlt ganz" von „nur der Sense fehlt"; die Zuordnung Sense→Concept bleibt kuratorisch |
| `quantify-unannotated-tokens.py` | Bestandsaufnahme der `<w>` **ohne** `@lemmaRef` (#189): Coverage je Text, korpusweit aggregierte Oberflächenformen, Homograph-Flag. CSV-Reports, keine Korpus-Änderung |
| `coverage-bias-check.py` | Anschlussfrage zum vorigen (#309): verzerrt die ungleiche Annotationsabdeckung die pro-1000-Raten der Analyse-Werkzeuge, und in welche Richtung? Nicht trivial, weil bei Rarität auch der Zähler mitgedrückt wird |
| `measure-stage3-resolution.py` | Wirkungsmessung für Stufe 3 der Lemma-Auflösung (#224): wie viele Kurzlemmata das frühere bidirektionale Substring-Matching in jede Suche gespült hat |
| `survey-concept-distribution.py` | Spiegelt `concept-distribution.js` 1:1 in Python und misst pro Concept Lemma-Zahl, Treffer-Texte und Vorkommen (#47 R2), um Browser-Grenzfälle bei sehr großen Begriffen zu finden |
| `count-verse-numbering-resets.py` | Reichweite der #138-Verszählung: welche `<div>` setzen die Randnummerierung zurück, und wie viele Randnummern kommen dadurch hinzu. Baut die Render-Reihenfolge nach, statt zu schätzen; zwei frühere Schätzungen per Textfenster-Heuristik waren beide falsch |
| `count-editorial-notes-and-div-heads.py` | Messvorschrift hinter den zwei Reader-Änderungen aus #250 (editorische Eingriffe im Metadatenpanel, Label über eigener `head`-Überschrift). Beide hängen an Korpuseigenschaften, die sich mit jedem Ingest verschieben |
| `drop-negative-variant-corresp.py` | Einmal-Migration (#115): entfernt tote `@corresp="variants.xml#type_-N"` (Legacy-Interpunktions-Codes, in `variants.xml` nie definiert) von `<w>`. Bereits angewendet, der Korpus enthält heute 0 solche Referenzen; bleibt als Beleg der Änderung |

### Skipped Tests (Issue #43 – resolved)

Keine Tests sind aktuell geskippt (0 skipped projektweit). Die früher in `main-site.spec.js` deaktivierten 25 Tests (Phase-7-/Phase-0-Refactoring) wurden in Commit `259bc505a` (2026-02-24, „88 passing, 0 skipped") wieder aktiviert bzw. ersetzt; #43 ist damit erledigt.

### Manual Testing Checklist

Before deploying:
- [ ] Search for common word (e.g., "vriunt")
- [ ] Search with variant (e.g., "brot" → "brôt")
- [ ] Text selection and filtering
- [ ] Open reading view
- [ ] Playground explorers
- [ ] Multi-lemma proximity search
- [ ] Playground → main site navigation

## Git Workflow

### Branch Strategy

- **main:** Production-ready code, stable releases
- **Feature branches:** `feature/your-feature-name`
- **Historical branches:**
  - `pre-main-site` - Old XML parsing architecture (archived)
  - `initial-data-wrangling` - RDF/Relational DB → TEI transformation (archived)
  - `feature/wenzelsbibel-ingest` - Wenzelsbibel text ingest (Issue #34, active)

### Development Workflow

```bash
# 1. Create feature branch
git checkout -b feature/your-feature-name

# 2. Make changes and test locally
npm run serve
# Test in browser...

# 3. Run automated tests
npm test

# 4. CRITICAL: Wait for user to test and approve
# DO NOT COMMIT without user approval!

# 5. Commit with descriptive message
# Stage specific files BY NAME — never `git add .` / `git add -A`.
# Concurrent sessions share the working dir; a blanket add captures another
# session's staged files (see CLAUDE.md Git Rules, commit 8b5d0e6ac mishap).
git add path/to/file1 path/to/file2
git commit -m "Add feature: description

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>"

# 6. Push (ONLY AFTER USER APPROVAL)
git push -u origin feature/your-feature-name

# 7. Merge to main
git checkout main
git merge feature/your-feature-name
git push origin main
```

### Commit Guidelines

**DO:**
- Use descriptive messages (not "fix bug" or "update file")
- Include context (what changed and why)
- Reference issues/PRs when applicable
- Add AI-assisted footer

**DON'T:**
- Commit without user testing and approval
- Force push to main
- Skip hooks or validation

### Autonome Sessions (Playbooks)

Für autonome Issue-Abarbeitung und PR-Merge-Sessions existieren wiederverwendbare Verfahren mit Betriebsvertrag, Gates und Fehlerbildern in [`docs/playbooks/`](playbooks/). Sie laufen nur nach explizitem User-Kickoff und werden nach jeder Session mit den Lehren aktualisiert.

## Deployment

### GitHub Pages

**Hosting:** GitHub Pages (static site, free)
**URL:** https://dhcraft.org/mhdbdb-tei-only/
**Branch:** `main` (automatically deployed)

### Deployment Process

1. Push to `main` branch
2. GitHub Actions automatically builds and deploys
3. Site updates within 2-5 minutes

### Pre-Deployment Checklist

- [ ] All tests passing
- [ ] Manual testing complete
- [ ] Pre-built indexes rebuilt (if XML sources changed)
- [ ] Documentation updated
- [ ] User has tested and approved changes

### Post-Deployment Verification

1. Visit https://dhcraft.org/mhdbdb-tei-only/
2. Test main site search
3. Test playground explorers
4. Verify pre-built indexes load correctly

### Cache Invalidation

Increment version number in build scripts to force browser refetch:

```python
VERSION = "1.x.x"  # In build-authority-index.py; aktueller Stand siehe TEI-MODEL.md §11
```

## Historical Context: Initial Data Wrangling

### Branch: `initial-data-wrangling`

The MHDBDB project originally maintained data in multiple formats (RDF, relational database, partial XML). To create a single source of truth, all data was transformed into TEI-compliant XML documents.

**Process:**
1. Extract from RDF (semantic concepts, genre hierarchies, names)
2. Extract from relational DB (persons, works, lemmata, bibliographic references)
3. Transform to TEI with consistent cross-reference patterns
4. Validate against TEI P5 schema

**Output:** 7 inhaltstragende TEI authority files in `authority-files/` directory (the 8th, `contributors.xml`, was added later in 2026-04-14 as part of the editor-attribution feature and is not part of this legacy export)

**Status:** Archived (completed, preserved for reference)

**Benefits of TEI as single source:**
- Interoperability (TEI is widely supported standard)
- Self-describing (metadata embedded with data)
- Version control friendly (XML diffs are readable)
- Future-proof (TEI will be supported for decades)

**Trade-off:** Large file sizes (solved with pre-built indexes)

---

For data structures, see [DATA-MODEL.md](DATA-MODEL.md).
For technical architecture, see [ARCHITECTURE.md](ARCHITECTURE.md).
For user-facing features, see [FEATURES.md](FEATURES.md).
For architecture decisions, see [DECISIONS.md](DECISIONS.md).
