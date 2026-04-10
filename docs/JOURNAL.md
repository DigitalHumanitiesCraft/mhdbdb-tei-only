# MHDBDB Development Journal

Chronological log of development decisions, dead ends, and savepoints. Not a changelog — captures the *reasoning* behind changes.

---

## 2025-02-24 — Phase 0: Stabilization

**Trigger:** Codebase cleanup before #42.

- Moved Wenzelsbibel (652k lines) to `feature/wenzelsbibel-ingest` branch
- Consolidated `css/`, `js/`, `lib/` into `assets/{css,js,images}`
- Playwright tests: 2/106 → 36 passed, 25 skipped. Root causes: outdated Chromium, worker count, relative import paths. Filed #43.
- Savepoints: `4562c08`, `6849758`, `e16306d`, `5154d04`

---

## 2025-02-24 — Issue #42: Persistent Lemma Pages

**Key finding:** Worterbuchnetz IDs already aligned (`lid=879` = our `lemma_879` = Wikidata P9351 `879`). No mapping work needed.

**Decisions:**
- Clean URL paths (`/lemma/879`) — external systems store these for years
- 404.html redirect trick for GitHub Pages (no server-side routing)
- Scope: single `lemma/index.html`, out of scope: MWB backlinks, JSON-LD

---

## 2026-02-24 — Issue Triage, Quick Wins, Provenance

- **#44 Triage:** 23 issues analyzed, 11 labels created. Key finding: 13/23 are data/TEI, only 7 frontend.
- **#21:** "Konzepte" → "Begriffe" rename (11 files)
- **#46:** Merged redundant Lemma-Suche into Multi-Lemma-Suche
- **#45 API:** Hybrid file strategy decided — individual files for small collections, bundled for lemmata (~23 MB total)
- **#36-40 Provenance:** Model decided (ADR-012): flat `<listBibl>` with `<bibl type="digitalIntermediary">` + `@corresp`. 50 files across 5 provider groups.

---

## 2026-02-27 — Documentation Health Check (#49)

Quarterly check. Actions filed: #54 (dedup docs), #55 (lemma page docs). Process decision: health check reports go as Issue #49 comments, not as .md files in docs/.

---

## 2026-04-07 — TEI Model Consolidation: Design (Issue #32)

**Trigger:** Katharina will externe Daten aufnehmen → braucht formales Schema als Validierungsgate.

### Strategy: Hybrid approach
3+1 phases: Soll-Modell (TEI-MODEL.md) → Structural fixes → Schema (RELAX NG) → Attribute migration.

### Key findings
- **0/100 files valid** against tei_all.rng — but only 2 error types: `@meaningRef` + `@wordRef` (non-standard attributes)
- **`@lemmaRef` IS standard TEI** (att.linguistic since v3.3.0/2018) — no migration needed
- Batch rename `@meaningRef` → `@ana` + `@wordRef` → `@corresp` would make corpus TEI-conformant

### Policy decisions (all resolved)
- POS tagset: 19-tag system from SKILL.md is canonical
- `<hi rend="initial">`: keep (655/675 files)
- `<l>` → `<lb/>`: migrate 18 prose files
- `<seg type="pc">` → `<pc join>`: migrate (1.4M elements)
- `@wordRef` → `@corresp` (not delete — carries non-reconstructible type→variant mapping)
- `@lemmaRef` → `@lemma`: deferred (cost >> benefit)

---

## 2026-04-09 — TEI Migration: Implementation (Phases A-E)

Corpus migration implemented in one session. 15M+ transformations across 675 files.

| Phase | What | Count |
|-------|------|-------|
| A | div/@type renames, monogr order, typos, dates, langUsage | 675 files |
| B | @meaningRef→@ana (5.9M), @wordRef→@corresp (7.5M) + JS fixes | 675 files |
| C | seg→pc (1.4M), l→lb in 18 prose files (86k) + JS fix | 668+18 files |
| D | normalization from XLSX (663 files) | 663 files |
| E | RELAX NG schema + validation (675/675 pass) | 675 files |

Additional: 9 disamb files merged into base (+35k POS), corpus index rebuilt (XPath→iter performance fix for PL1 45MB hang).

### Dead ends
- `encoding='unicode'` on Windows lxml → `LookupError`. Fix: `encoding='UTF-8'`
- l→lb script O(n^2) on PL1 → fixed with `addprevious`/`addnext`
- 9 zombie Python processes from background tasks → `taskkill`
- Corpus index build hanging at 440/666 → root cause: `tree.xpath()` with namespace dict is O(n^2) on large docs. Fix: `iter()` with Clark notation.

---

## 2026-04-10 — PR #1 Merged + Authority Migration + Schema Audit

### PR #69 (Corpus Migration → main)
34 commits, 731 files, ~33M lines. Code review found 3 bugs: `resolveConceptReferences` missed `@ana`, `<pc>` missing span wrapper in second rendering path, `etree.fromstring/tostring` round-trip. All fixed before merge.

### Post-merge cleanup (this session)
- Rendering refactor: dual path (switch + if-chain) → single `_renderElement` closure
- TEI-MODEL.md Section 10 updated to post-migration state (v1.0.0)
- Example XML cleaned: all IST/SOLL/NEU migration comments removed, missing features added (pc join=right, hi upper_case_first_letter, 6 POS tags, @reason, provenance notes)
- Test invocation documented: `npm test` not `npx playwright test` (config in `testing/` subdir)

### Authority Migration (Phases F-K, parallel Claude instance)
- works.xml: 3,422 genre `<ref>` → 870 `<ptr/>`, IDs unwrapped, GND casing, Frauendienst/Frauenbuch split
- persons.xml: listBibl removed (derived from works.xml), 4 UUID→numeric, Schweizer Anonymus added
- lexicon.xml + variants.xml: 225 orphaned references removed
- Build scripts: person→works derived from works.xml, genre text from genres.xml, version 1.2.0
- Authority schema + 7 example files created
- Frontend: empty state, multi-word text filter, pc-spacing with data-join

### Corpus Schema Deep Audit
11 gaps found and fixed:
- `div` is a **reserved keyword** in RNC — renamed to `tei.div` (root cause of RNC→RNG conversion failure)
- `text` in choices causes interleave conflicts — solved with `mixed {}`
- div/@type made optional (154 files without), body/div allow inline children (137+ files)
- Multiple titles (291 files), @type/@level/@ana on title, multiple authors (5 files)
- biblStruct allows `<note>`, date allows @from/@notBefore/@notAfter
- imprint/publicationStmt: flexible child ordering
- taxonomy: `<bibl>` before categories
- **Result: 666/666 valid, RNG generation works**

### Stale references fixed
6 docs updated: DATA-MODEL.MD, RESEARCH.MD, FEATURES.MD, DESIGN.MD, CONTRACTS.MD, CLAUDE.md — all `@wordRef`→`@corresp`, `<seg type="pc">`→`<pc>`.

### Branch protection
`main` protected via gh CLI: no force push, no deletion, PRs required.

### Open issues
- **PR #2** (Authority Migration) being prepared by colleague
- **#70** (pc join spacing): colleague implemented data-join + 2-pass regex approach — needs visual verification after merge
- **work_7** (Frauenbuch): Katharina confirmed genres, but "haengen zusammen" needs documentation
- **WZB branch**: 9 disamb files need migration scripts run after rebase (old @meaningRef/@wordRef)
- **Corpus index rebuild** needed after PZ/DKK/Stricker structural changes

### Schema README
Single entry point for external projects: validation guide, data mapping instructions, all document types covered. /check-md reviewed (8 findings fixed: wrong authority file counts/structures).

---

## 2026-04-10 17:00 — handoff

**Summary:** Issue #32 TEI Model Consolidation feature-complete. Corpus migration merged (PR #69), authority migration ready for PR #2 (colleague). Deep schema audit: 666/666 corpus files valid, RNC→RNG conversion fixed. All docs updated to post-migration state. Branch protection on main. 121/121 Playwright tests passing.

**Phase:** Implementation complete. PR #2 pending (colleague).

**Docs status:**
- `docs/TEI-MODEL.md` — v1.0.0, post-migration (current)
- `docs/TEI-MODEL-AUTH-FILES.md` — Implementiert, all counts updated
- `schema/mhdbdb.rnc` + `.rng` — 666/666 valid, RNG generated
- `schema/mhdbdb-authority.rnc` + `.rng` — 7/7 valid
- `schema/README.md` — External mapping guide
- `schema/examples/` — 8 validated examples (1 corpus + 7 authority)

**Open issues:**
- PR #2 (colleague)
- #70 pc join spacing (colleague implemented, needs post-merge visual test)
- work_7 Frauenbuch documentation (Katharina)
- WZB branch rebase (after merge)
- Corpus index rebuild (PZ + Stricker changes)

**Next session:**
1. `/promptotyping orient`
2. Verify PR #2 merged
3. Corpus index rebuild if TEI files changed
4. Browser smoke test: pc spacing with colleague's data-join approach
5. Consider closing #32 after both PRs merged
