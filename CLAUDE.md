# CLAUDE.md

Operational briefing for Claude Code. Details live in `docs/` — this file is the concise pointer.

## Project in One Paragraph

MHDBDB TEI Repository: ~667 TEI-encoded Middle High German texts with semantic annotations. **Frontend-only** (GitHub Pages, no backend). Pre-built JSON indexes replace runtime XML parsing. Target audience: medievalists and DH researchers.

**Transformation → active project:** Started as a one-time migration (old MHDBDB + RDF export → TEI-only repo); that migration is done. It is now an **active project with ongoing ingest** (WZB, ARITHMETIC, more planned), so every data change must propagate through the derived layer (indexes, corpus-derived `variants.xml`) or it drifts silently. The mandatory step sequence lives in `docs/DATA-MODEL.md` → Data-Change-Lifecycle; the normative ingest procedure (Stage-0 → Phase 1–3 → Backfill) in `docs/DATA-MODEL.md` → Ingest-Verfahren.

## Documentation Hub

@docs/INDEX.md — gateway to all project knowledge:

| Doc | What's in it |
|-----|-------------|
| DATA-MODEL.md | Schemas, data pipeline, index structure |
| ARCHITECTURE.md | Components, data flow, storage |
| DESIGN.md | Visual patterns, color system, CSS architecture |
| FEATURES.md | User-facing functionality |
| DEVELOPMENT.md | Build commands, git workflow, deployment |
| RESEARCH.md | Academic context, TEI/MHG standards |
| DECISIONS.md | Architecture Decision Records |
| CONTRACTS.md | Cross-language parity, algorithm pseudocode, API contracts |
| ROADMAP.md | Current priorities and strategic direction |
| JOURNAL.md | Chronological development log |
| `features/` | Feature-scoped planning docs (active issues only) |
| `playbooks/` | Wiederverwendbare Session-Verfahren (autonome Issue-/Merge-/Carearbeit-Sessions) |

## Directory Layout

```
assets/js/           # Main site JS (app.js, search/, rendering/, storage/, lib/)
assets/css/          # Stylesheets
authority-files/     # 8 XML authority files (source of truth, inkl. contributors.xml seit 2026-04-14)
tei/                 # 667 TEI corpus files
data/                # Pre-built indexes (.json.gz, generated)
api/                 # Statische JSON-API (generiert via scripts/build-api.py, #45)
scripts/             # Python build scripts + data-wrangling
playground/          # Research tool (self-contained sub-app)
lemma/               # Persistent lemma pages (Issue #42)
testing/             # Playwright tests
docs/                # Knowledge documentation
publications/        # Blog posts, reports
```

## Commands

```bash
npm run serve                    # Dev server on :8080
npm test                         # Playwright (auto-starts server) — NEVER use `npx playwright test` from root
python scripts/build-authority-index.py   # Rebuild authority index
python scripts/build-corpus-index.py      # Rebuild corpus index
python scripts/build-api.py               # Rebuild static JSON API
```

## Hard Constraints

- **TEI namespace**: `http://www.tei-c.org/ns/1.0` — always
- **UTF-8**: All files
- **Desktop-only**: min 1200px width
- **IndexedDB required**: Large indexes cached in browser
- **Position counting**: Only `<w>` elements with `@lemmaRef` — Python and JS must match exactly
- **Daten vor Schema**: Bei Konflikten zwischen Bestandsdaten (Korpus, Authority-Files) und dem Schema immer zuerst die Daten migrieren, nicht das Schema aufweichen. Eine Schema-Lockerung ist nur zulässig, wenn die Daten-Migration unverhältnismäßig teuer oder semantisch gefährlich wäre — und dann explizit als `GAP`-Kommentar im Schema dokumentiert (siehe `schema/mhdbdb.rnc` GAPs 1–11).

## Git Rules

- **NEVER commit or push without user testing and approval**
- **Concurrent sessions share the working directory** — never use `git add -A` or `git add .`. Always stage specific files by name (`git add path/to/file1 path/to/file2`). Another Claude session may have staged files that do not belong in your commit. Example: commit `8b5d0e6ac` mistakenly swept router files into an unrelated #84 commit because `git add -A` captured the other session's staged playground edits.
- Never force push to `main`
- **Evergreen issue (#44): NEVER close** — no `Closes #44` or `Fixes #44` in commits. Permanent tracking issue (labeled `evergreen`, pinned). (#91 Zenodo was mislabeled `evergreen` and is a normal closeable task — corrected 2026-06-09.)
- Rebuild indexes after modifying XML in `authority-files/` or `tei/`
- Run tests before pushing
- Update `docs/` when architecture changes

### Commit Format
```
Brief description

## Changes
- What changed

Co-Authored-By: Claude <noreply@anthropic.com>
```

### Branches
- `main` — production
- `feature/*` — active work
- `initial-data-wrangling` — archived (`pre-main-site` wurde inzwischen gelöscht)

## Temporal Artifacts (Promptotyping convention)

- **Feature docs** (`docs/features/`): Live while issue is open. On completion: extract critical knowledge into stable docs (CONTRACTS.md, ARCHITECTURE.md, etc.), then delete. Git history = archive.
- **Playbooks** (`docs/playbooks/`): Bewusste Ausnahme von der Lösch-Regel — wiederverwendbare Session-Verfahren (autonome Issue-/Merge-/Carearbeit-Sessions), nicht ticket-gebunden. Nach jeder Session: Lehren einarbeiten, session-spezifischen Anhang leeren bzw. neu befüllen, Kernwissen ins JOURNAL. Autorisieren NICHTS von selbst; sie laufen nur nach explizitem User-Kickoff (Betriebsvertrag steht in den Dateien).
- **Health check reports**: Run via `/promptotyping check` (operative Mechanik). Full report → Scorecard in JOURNAL.md (3-4 Zeilen, dated). Action items → separate Issues. **Keine .md-Datei in `docs/`** — der Report ist disposable, sobald Action Items extrahiert sind.

### Health-Check-Checkliste (MHDBDB-spezifisch)

Nach größeren Doku-Änderungen oder quartalsweise (auch ohne Änderungen, gegen schleichenden Drift):

- **Flow check:** Jede modifizierte Doku end-to-end lesen — fließt sie logisch?
- **Algorithm spot-check:** 3 Algorithmen ziehen, Pseudo-Code in Docs gegen tatsächlichen Code abgleichen
- **XPath spot-check:** 3 XPaths in Docs gegen Build-Skripte verifizieren
- **Rebuild test:** Frage: "Könnte ich alle `.js`/`.py` löschen und aus den Docs rekonstruieren?" — wenn ja für kritische Pfade (Suche, Build-Pipeline, Reader), sind wir bei 85%+

**Trigger:** nach PRs an `docs/`, nach neuen Build-Skripten oder Algorithmen-Änderungen, nach neuen Authority-Files oder TEI-Elementen, quartalsweise.

**Meta-Fragen (periodisch prüfen):** Sind die .md-Namen selbsterklärend? Gibt es zu viele oder zu wenige Promptotyping-Docs (Overlap vs. Mixed Concerns)? Strukturelle Doc-Änderungen immer mit Begründung listen.

## Gotchas

- **Angle bracket entities** (`&lt;`, `&gt;`) in `<pc>` are correct XML — not bugs
- **Nav/Footer sind build-injiziert**: Nicht in den HTML-Seiten direkt editieren. Quelle ist `includes/` + `scripts/build-pages.py` (Marker-Bereiche); `build-pages.py --check` ist das Drift-Gate. Mobile-Menü bleibt inline. Siehe DEVELOPMENT.md.
- **Zotero cache** (`.zotero_cache.json`) is gitignored — use `--offline` for reproducible builds
- **German Title Case**: Zotero sync capitalizes words except articles/prepositions (der, die, von, und...)

## Key Patterns

- **3-stage lemma resolution**: exact match → variants dictionary (~257k entries) → partial match fallback. See ARCHITECTURE.md.
- **Lemma highlight matching**: a `<w>` is highlighted only if `@lemmaRef` contains the searched id as an exact whitespace-separated token (never a substring: `#lemma_308` must not match `#lemma_3089`). Centralized in `assets/js/lib/lemma-match.js` (`lemmaRefMatchesId`). See CONTRACTS.md §B.1 (#126/#130).
- **MHG normalization**: `â→a, ê→e, î→i, ô→o, û→u, ä→ae, ö→oe, ü→ue`. Centralized in `assets/js/lib/text-normalizer.js`.
- **Pre-built indexes**: authority (~3 MB gz) + corpus (~40 MB gz). Aktuelle Versionen: TEI-MODEL.md §11 (Source of Truth). See DATA-MODEL.md for schemas.

## License

CC BY-NC-SA 4.0 | mhdbdb@plus.ac.at
