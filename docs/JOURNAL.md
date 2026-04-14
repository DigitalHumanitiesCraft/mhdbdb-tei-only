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

**Erledigt (diese Session):**
- PR #69 (Korpus) + PR #71 (Authority) gemergt
- #32 geschlossen (mit ODD-Begründung)
- #70 geschlossen (pc-spacing implementiert)
- Branch Protection auf main (force-push + deletion blocked)
- Feature-Branch + 2 obsolete Branches gelöscht

**Open issues:**
- #20 Lesbarkeit/CSS — offen
- #52 Authority Files Karte im Playground — offen

**WZB-Branch (`feature/wenzelsbibel-ingest`):**
WZB braucht KEINE Attribut-Migration (hat bereits `@ana`/`@corresp`, nie `@meaningRef`/`@wordRef`). Der Branch hat 5 eigene Commits (Issue #66), 1451 Dateien (WZB TEI + Disambiguation-TSVs). Rebase auf `main` nötig, aber nur für Merge-Konflikte in Docs/Config — nicht für TEI-Attribute.

**Next session:**
1. `/promptotyping orient`
2. Browser smoke test: pc spacing, empty state, nav
3. Nächstes Issue aus ROADMAP.md wählen

---

## 2026-04-14 18:30 — handoff

**Summary:** Frontend Quick-Wins #62 (Impressum) und #52 (Authority-Files-Card) umgesetzt und an @wachauer zum Review eskaliert. Editor-Attribution-Plan bis Commit 3/7 durchgezogen (contributors.xml mit 51 Personen + 2 Orgs, Authority-Schema um contributors.body-Pattern erweitert, Corpus-Schema additiv für Mehrfach-respStmt und persName+@ref, Standalone-Migration-Script inkl. Whitespace-Bug-Fix verifiziert). WorksSyncer-gnd-Drift als P0-5 Pre-Fix vorab gefixt, damit der nächste `--works`-Sync-Lauf den P0-4-Fix (Commit `61a0b4a1a`) nicht revertiert.

**Phase:** Implementation — editor-attribution 3/7 Commits abgeschlossen. Commits 4-7 (666-Datei Header-Migration, Lead-Editor respStmts, Doku-Updates, Script-Archivierung) warten auf User-Review des Migration-Scripts und Go/No-Go für den Massenlauf.

**Docs-Status:**
- `docs/features/editor-attribution.md` — unverändert, 680-Zeilen-Plan vom Kollegen mit 3× /check-md Iterationen (32 Findings gefixt)
- `docs/features/032-schema-followup.md` — unverändert, neues P0-5 Item (WorksSyncer) erledigt, Rest offen (P1-5/6/10, P2-11/12/13/14, P3)
- `docs/features/062-impressum.md` + `docs/features/052-authority-files-card.md` — unverändert, Issues offen bis Katharina OK gibt
- `authority-files/contributors.xml` — NEU, 51 Personen + 2 Orgs, validiert gegen beide Stages
- `schema/mhdbdb-authority.rnc` + `.rng` — `contributors.body = (listOrg?, contributors.listPerson)` Pattern ergänzt, Rollen-Enum direkt auf `<person>/@role`
- `schema/mhdbdb.rnc` + `.rng` — `respStmt+`, `name/@role`, `persName+` mit `@ref` in `<authority>` (alle additiv)
- `schema/examples/authority-contributors.example.xml` — NEU, 8 Personen (2×founder, 1×coordinator, 2×lead-editor, 3×editor) + 2 Orgs
- `scripts/migrate-header-credits.py` — NEU, Standalone-Skelett mit `_child_indent`/`_capture_closing_indent` Whitespace-Mimicry (kein `pretty_print=True`), idempotent über `@ref`-Match, verifiziert via Sample + Full-Dry-Run
- `scripts/sync/sync_tei_headers.py` — 3× `gnd` → `GND` (XPath + set('type', ...))

**Erledigt (diese Session, 5 Commits auf main):**
- `83d8546ed` Frontend #62 + #52 (impressum.html + footer-links + authority-card collapse)
- `05e9c2d91` #32-followup P0-5: WorksSyncer gnd→GND (Pre-Fix für editor-attribution)
- `6f80e5d47` editor-attribution Commit 1: contributors.xml + authority schema + example
- `1849a09fa` editor-attribution Commit 2: Corpus-Schema additiv
- `f2034fe94` editor-attribution Commit 3: migrate-header-credits.py (nur Script, keine TEI-Änderung)

**Validierungsstand:**
- 8/8 Authority-Files grün gegen tei_all.rng + mhdbdb-authority.rng (inkl. neue contributors.xml)
- 9/9 Schema-Examples grün
- Volle Korpus-Validierung (666 Dateien, 831s): 30/30 tei_all baseline, 0/0 mhdbdb baseline → keine Regression durch die Schema-Erweiterung
- Migration-Script Sample-Test (ABG/AK/BRW/LZT/WUT/TKR): Diff visuell sauber, 0 Whitespace-Noise
- Full-Dry-Run über alle 666 Dateien: 0 Fehler, `auth=True resp=True` überall, `lead=True` exakt bei TKR/TKA/VTC/JT

**Whitespace-Bug gefunden und gefixt:**
`add_lead_editor()` las im ersten Wurf `child_indent` aus einer Struktur, in der die vorherige letzte `<respStmt>` (die von `migrate_collective_respstmt()` angelegt wurde) noch `closing_indent` als `.tail` hatte. Dadurch wurde die neue lead-editor-respStmt 2 Spaces zu weit links eingerückt. Fix: vor dem Append `title_stmt[-1].tail = child_indent` setzen, damit der Übergang von „last child" zu „zweitletztem child" sauber ist. Verifiziert auf TKR — jetzt bündig zur kollektiven respStmt.

**Kommentare an @wachauer (Issues bleiben offen):**
- [#62 Impressum](https://github.com/DigitalHumanitiesCraft/mhdbdb-tei-only/issues/62#issuecomment-4244878530)
- [#52 Authority-Files-Card](https://github.com/DigitalHumanitiesCraft/mhdbdb-tei-only/issues/52#issuecomment-4244879862)

**Open Issues (offen für nächste Session):**

*Editor-Attribution (nach User-Review des Scripts):*
- **Commit 4** (666-Datei Header-Migration): Script bereit, User soll Diff auf Sample prüfen (z.B. ABG), dann Massenlauf (~3 Min Migration + ~14 Min Validation)
- **Commit 5** (Lead-Editor-respStmts für TKR/TKA/VTC/JT): trivial nach Commit 4, idempotentes Script-Rerun
- **Commit 6** (Doku-Updates): `TEI-MODEL.md` §2.1bis + §12, `TEI-MODEL-AUTH-FILES.md` §1/§2.3/§3.8, `schema/README.md` Tabellen
- **Commit 7** (Script archivieren): `git mv scripts/migrate-header-credits.py scripts/_archived/`

*Schema-Followup (parallel oder danach):*
- **P1-5** (`mhdbdb.rnc` idno/@type Enum) — **komplexer als Plan vorgibt**: Korpus hat 7 @type-Werte (`callNumber, GND, handschriftencensus, ISBN, mwb-sigle, sigle, wikidata`), davon müssen `ISBN` und `callNumber` unter `<biblStruct>//<idno>` frei bleiben. Braucht kontextspezifische Enum-Verteilung, nicht einen globalen Enum wie im Plan vorgeschlagen (~1 h saubere Schema-Lektüre)
- **P1-6** persName/@type Enum — Audit sauber: nur `"preferred"` + `"alternative"` im Korpus. Quick-Win, 30 Min
- **P1-10** msIdentifier/@corresp auf Pflicht — braucht Daten-Audit zur Existenz des Attributs in allen 666 Files
- **P2-11** Taxonomie-Kopplung Option 3 (Doku-Kommentar) — 5 Min
- **P2-12** `validate-corpus.py` rewrite — self-contained, 30 Min
- **P2-13/14** CI-Schema-Validation-Workflow — ~1 h

*Andere:*
- **WZB Lead-Editor-Mini-Commit** (nach #66-Merge): `contrib_006 role editor → lead-editor` + respStmt in WZB.tei.xml
- **#62** + **#52** + **#79** bleiben offen bis Katharina/Julia Feedback geben

**Nicht-Befunde (damit niemand nochmal sucht):**
- `persName/@type` im Korpus: nur 2 Werte (`"preferred"`, `"alternative"`), P1-6 ist sauber ohne Daten-Migration machbar
- `idno/@type` im Korpus: 7 verschiedene Werte, 2 davon (`ISBN`, `callNumber`) leben unter `<biblStruct>`, daher nicht global enumerierbar
- Migration-Script-Logik: verifiziert idempotent (zweiter Lauf macht nichts, weil Alt-Muster erkannt wird und neue Muster via `@ref`-Check skippen)

**Next session:**
1. `/promptotyping orient`
2. User reviewt `scripts/migrate-header-credits.py` — optional Sample-Check: `python scripts/migrate-header-credits.py --sample ABG --dry-run`, dann ohne `--dry-run`, dann `git diff tei/ABG.tei.xml`, dann `git restore tei/ABG.tei.xml`
3. Go/No-Go für editor-attribution Commit 4 (Full-Korpus-Migration, ~3 Min Lauf + ~14 Min Validation)
4. Bei grün: Commit 5 → Commit 6 (Doku) → Commit 7 (Archiv)
5. Danach: Schema-Followup Quick-Wins in Reihenfolge P2-11 (5 Min) → P1-6 (30 Min) → P1-5 kontextspezifisch (~1 h) → P1-10 mit Audit → P2-12 → P2-13/14
