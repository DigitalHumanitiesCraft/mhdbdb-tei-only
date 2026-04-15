# CLAUDE.md

Operational briefing for Claude Code. Details live in `docs/` — this file is the concise pointer.

## Project in One Paragraph

MHDBDB TEI Repository: ~670 TEI-encoded Middle High German texts with semantic annotations. **Frontend-only** (GitHub Pages, no backend). Pre-built JSON indexes replace runtime XML parsing. Target audience: medievalists and DH researchers.

## Documentation Hub

@docs/INDEX.MD — gateway to all project knowledge:

| Doc | What's in it |
|-----|-------------|
| DATA-MODEL.MD | Schemas, data pipeline, index structure |
| ARCHITECTURE.MD | Components, data flow, storage |
| DESIGN.MD | Visual patterns, color system, CSS architecture |
| FEATURES.MD | User-facing functionality |
| DEVELOPMENT.MD | Build commands, git workflow, deployment |
| RESEARCH.MD | Academic context, TEI/MHG standards |
| DECISIONS.MD | Architecture Decision Records |
| CONTRACTS.MD | Cross-language parity, algorithm pseudocode, API contracts |
| ROADMAP.md | Current priorities and strategic direction |
| JOURNAL.md | Chronological development log |
| `features/` | Feature-scoped planning docs (active issues only) |

## Directory Layout

```
assets/js/           # Main site JS (app.js, search/, rendering/, storage/, lib/)
assets/css/          # Stylesheets
authority-files/     # 7 XML authority files (source of truth)
tei/                 # ~670 TEI corpus files
data/                # Pre-built indexes (.json.gz, generated)
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
- **Evergreen issues (#44, #49): NEVER close** — no `Closes #44` or `Fixes #49` in commits. These are permanent tracking issues (labeled `evergreen`, pinned).
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
- `pre-main-site`, `initial-data-wrangling` — archived

## Temporal Artifacts (Promptotyping convention)

- **Feature docs** (`docs/features/`): Live while issue is open. On completion: extract critical knowledge into stable docs (CONTRACTS.MD, ARCHITECTURE.MD, etc.), then delete. Git history = archive.
- **Health check reports** (Issue #49): Full report → Issue #49 comment. Scorecard → JOURNAL.md. Action items → separate Issues. **No .md files in `docs/`**. Load `/promptotyping` skill before running checks.

## Gotchas

- **Angle bracket entities** (`&lt;`, `&gt;`) in `<pc>` are correct XML — not bugs
- **25 skipped tests** (main site) — intentional, tracked in #43
- **Zotero cache** (`.zotero_cache.json`) is gitignored — use `--offline` for reproducible builds
- **German Title Case**: Zotero sync capitalizes words except articles/prepositions (der, die, von, und...)

## Key Patterns

- **3-stage lemma resolution**: exact match → variants dictionary (176k entries) → partial match fallback. See ARCHITECTURE.MD.
- **MHG normalization**: `â→a, ê→e, î→i, ô→o, û→u, ä→ae, ö→oe, ü→ue`. Centralized in `assets/js/lib/text-normalizer.js`.
- **Pre-built indexes**: authority (3 MB gz, v1.2.0) + corpus (34 MB gz, v4.0.0). See DATA-MODEL.MD for schemas.

## License

CC BY-NC-SA 4.0 | mhdbdb@plus.ac.at
