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

## 2026-04-13 — WZB Annotation Pipeline: Phases 1b, 2 + Structural Encoding (#34, #66)

**Trigger:** Resume Wenzelsbibel ingest work on `feature/wenzelsbibel-ingest`. The TEI file had 150k `<w>` tokens with no annotation. Goal: reach a state suitable for corpus integration.

### Phase 1b — Lemma disambiguation (91.6% coverage)

Pipeline: `wzb-bulk-resolve.py` applies TSV resolution batches to `wzb-disambiguation.tsv`, then `wzb-apply-lemmarefs.py` writes `@lemmaRef` to the TEI.

- Batches 01–49 applied: 66,298 / 72,362 rows resolved
- New lemmata created: `lemma_78608` (Latin *et*), `lemma_78628` (Czech glosses *cs*), `lemma_78648` (*herte* herd), `lemma_78668` (*scot* shekel), `lemma_78688` (*weise* orphan)
- Residual ~6,064 rows: pronoun/case ambiguity (`in`, `des`, `ir`), genuinely deferred multi-sense verbs, Bohemian hapax — left without `@lemmaRef` intentionally
- Key insight: Bohemian scribal conventions (cz=z, v=u, ou=û, vor-=ver-) required manual pattern recognition; Czech interlinear glosses form a distinct lemma class

### Phase 2 — POS tagging (95.5% coverage)

Pipeline: `wzb-pos-assign.py` → pending TSV → LLM batches via `wzb-pos-bulk-resolve.py` → `wzb-pos-apply.py` writes `@pos` to TEI.

- Batches 01–10 + context-based resolver: 0% → 95.5% (143,340 / 150,017 tokens)
- **Tagset migration** (`cf71ae48`): ART→DET, CNJ bulk re-routed to CCNJ/SCNJ/ADV by lemma identity. SKILL.md 19-tag set enforced throughout.
- **Context-based resolver** (`ff83d087`): 14,660 rows resolved using ±4-word neighbour `@pos` context. Key rules: `daz` (DET vs SCNJ), `haben` (VEX vs VRB), `ûf`/`vor` (PRP vs ADV), `ir` (POS vs PRO), `noch` (CCNJ vs NEG).
- Residual ~506 low-confidence + ~6,064 no-lemmaRef — effectively at the ceiling for bulk methods

### Phase 3 — Paratext encoding (Issue #66)

Decision: structural elements encoded in TEI but excluded from lemma pipeline. Implemented via `wzb-structural-cleanup.py` + `wzb-resolutions-batch-paratext.tsv`.

| Element | Decision |
| ------- | -------- |
| `<fw type="header">` book names | Strip `@lemmaRef`/`@pos` — running headers, not lexical |
| CAPITULUM + Roman numeral `<w>` | `<head type="chapter" n="N">` + `<milestone unit="chapter">` inline |
| Scribal marks (ł, -, ̃, =, etc.) | `<w>` → `<seg type="pc">` |
| Single-letter initials (a, s, O) | `<w>` → `<seg type="pc">` |
| Roman numerals inline (UIII, XU) | Keep as `<w>`, `lemma_13826` (DIG) |
| Latin *et*, *est* | Keep as `<w>`, `lemma_1732`/`lemma_9387` |
| Czech glosses | Keep as `<w>`, `lemma_78628` |

### Structural fix pass (`1d8fa549`)

`wzb-structural-fix.py` corrected two TEI P5 conformance issues found by structural survey:

- 212 unnamed chapter divs (xml:id="Genesis.1" etc.) missing `@type` → `type="chapter"`
- 106 `<head type="chapter">` inside `<l>` (TEI-invalid) → moved to first child of target `<div type="chapter">`; `<milestone unit="chapter" n="N"/>` placed at original text-flow position
- Space-tolerant `roman_to_arabic()`: "I X" → IX = 9 (was incorrectly 11)

### Encoding cleanup (`2a6cbdd7`)

`wzb-encoding-cleanup.py` fixed four residual issues:

- 6 `<w>` in `<hi rend="initial_historisiert">` (decorative split-word first letters) → `<seg type="pc">`
- `Josua.0` mis-classified as `type="chapter"` → `type="paratext"`, `xml:id="JosuaPrologus"`
- `<div type="Transition2.1">` → `type="paratext"`
- Unnamed prologus body div → `type="section"`, `xml:id="Prologus.1"`

### Final WZB TEI state (2026-04-13)

| Metric | Value |
| ------ | ----- |
| `<w>` total | 149,148 |
| `@lemmaRef` coverage | ~91.6% |
| `@pos` coverage | ~95.5% |
| `<div type="chapter">` | 211 |
| `<div type="book">` | 6 |
| `<div type="paratext">` | 12 |
| `<head type="chapter">` | 106 (direct div children) |
| `<milestone unit="chapter">` | 106 |
| `<seg type="pc">` | 35,479 |
| `<fw type="header">` | 905 |

Remaining before corpus integration: `@meaningRef` + `@wordRef` (Phase 3 — not started), then merge into main.

---

## 2026-02-24 — Quick Wins: #21, #46, #45 doc update

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

---

## 2026-04-15 12:10 — handoff

**Summary:** Massiver Schema-/Daten-Cleanup-Tag. editor-attribution vollständig abgeschlossen (Commits 1–6, #83 closed nach Katharinas Review), 16/17 Items aus `032-schema-followup.md` erledigt, zwei große „Daten vor Schema"-Migrationen durchgezogen (PL1/PL2/PL3 Mega-`<p>` Split + nested `<hi>` Flatten über 143 Dateien), Schema verschärft (`<hi>`-Rekursion entfernt, persName/@type Enum, msIdentifier/@corresp Pflicht, Taxonomie-Body Doku-Kommentar), neue CI-Workflow `schema-validation.yml` mit RNG-Drift-Check und zwei-stufiger Validation, `validate-corpus.py` als echter RelaxNG-Validator reimplementiert, `claude.yml`-Workflow entfernt (versehentliche `@claude`-Pings auf Issues), CLAUDE.md um Hard Constraint „Daten vor Schema" erweitert.

**Phase:** Implementation — #32-followup praktisch komplett (1 Item offen: P1-5), editor-attribution komplett (WZB-Mini-Commit wartet auf #66-Merge), Korpus-Validation ~40 % schneller als am Vormittag (830s → 493s nach Data+Schema-Cleanup).

**Docs-Status:**
- `docs/features/032-schema-followup.md` — Status-Tabelle oben, 16/17 done, P1-5 als einziges offenes Item mit aktualisiertem Komplexitäts-Callout
- `docs/features/editor-attribution.md` — unverändert, Sequenz ist durch
- `docs/TEI-MODEL.md` — §2.1bis „Editor-Attribution & Credits" neu, §12 „Konventionen für neue Ingests" neu, §3.5 `<note type="date">` auf Ist-Zustand (Klartext) umgestellt
- `docs/TEI-MODEL-AUTH-FILES.md` — §1 Übersicht (7 → 8 Authority-Files), §2.3 Identifier-Tabelle um `contrib_NNN` ergänzt, §3.8 NEU: contributors.xml
- `schema/README.md` — 8 Authority-Files, examples-Tabelle erweitert
- `CLAUDE.md` — Hard Constraint „Daten vor Schema" (`9ab92cdb2`)
- Memory (per-user, `~/.claude/projects/.../memory/`): `feedback_data_first.md`, `feedback_targeted_validation.md` — beide in `MEMORY.md` indexiert

**Commit-Serie heute (Vormittag, alle auf `main`):**
- `7e526c8f2` P2-11 Taxonomie-Body Doku-Kommentar
- `f72887eaa` P1-6 persName/@type Enum
- `7a79693d7` editor-attribution Doku
- `9ab92cdb2` CLAUDE.md „Daten vor Schema"
- `49d7b58aa` + `67526399e` PL1/2/3 Mega-`<p>` Split + Archive
- `b3e76ce7b` + `38b0bdd10` + `0f503ada8` Nested `<hi>` Flatten + Schema-Simplification + Archive
- `54b450f32` claude.yml Workflow entfernt
- `3ceb6b738` + `6bcd61d07` + `62ad64d2a` editor-attribution Commits 4-6 (full migration + doc-fix + archive, Closes #83)
- `674fd3258` + `1590f9405` P2-15 xml-model PIs + Archive
- `8b5d0e6ac` + `20a9d1a22` #84 Doku-Fix + Klarstellungs-Commit (Closes #84)
- `83b511eec` P1-10 msIdentifier/@corresp Pflicht
- `e9d43ead4` P2-12 validate-corpus.py als RelaxNG-Validator reimplementiert
- `becceda03` + `2d752769f` 032-Plan Status-Updates
- `7d3801520` P2-13 + P2-14 schema-validation.yml CI-Workflow

Parallel committete der Kollege (dieselbe Person in anderer Session) mehrere Playground-Commits (`2c204cd4c` #56 Lemmata-Explorer, `aad5a55bd`, `0189a2eed`, `897431795`, `ba6b1ebcc` #31 Linecode-Doku) — keine Kollisionen mit meinen Änderungen. Ein Commit (`8b5d0e6ac`) hat versehentlich bereits-gestagte Kollegen-Dateien aus `playground/` mit-committet, das ist in `20a9d1a22` klarstellungs-dokumentiert.

**Katharinas Antworten (Issue #83, durch):**
- Reihenfolge im `<authority>`: Zeppezauer-Wachauer → Schmidt → Pütz (korrigiert im Script + 666 Headern)
- PUC auch Brom-Lead-Editor: JA (+1 Eintrag in `LEAD_EDITORS`)
- Klug/Gloning/Harsch: bewusst NICHT in `contributors.xml` (externe Primärtext-Provider sind im provenance-Block gemodelt)
- 4 Institutionen (Mainz/Virginia/Trier/TITUS): NICHT in `contributors.xml` (nur Datengeber, keine editorische Arbeit)
- DHC ist drin, weil editorische Arbeit

**Open Issues (für nächste Session):**

*Schema-Followup (letztes Item):*
- **P1-5** `mhdbdb.rnc` `<idno @type>` Enum kontextspezifisch (~1 h). Audit heute: 7 Werte im Korpus (`callNumber`, `GND`, `handschriftencensus`, `ISBN`, `mwb-sigle`, `sigle`, `wikidata`), davon `ISBN` + `callNumber` nur unter `<biblStruct>`/`<monogr>`. Braucht positionsspezifische Enum-Verteilung, nicht einen globalen Enum wie im Plan vorgeschlagen. Details im aktualisierten §P1-5-Block von `docs/features/032-schema-followup.md`.

*Warten auf externes Feedback (alles an Katharina/Julia):*
- **#52** Authority-Files-Card — letzter Ping 2026-04-14, keine Antwort
- **#62** Impressum — letzter Ping 2026-04-14, keine Antwort
- **#79** /hilfe/ Hilfe-Seite — keine Kommentare, braucht Starter-Aufmerksamkeit (kein Katharina-Gate)

*Editor-Attribution-Nachzug:*
- **WZB Lead-Editor Mini-Commit** für Julia Hintersteiner (contrib_006, role → `lead-editor`) — wartet auf Merge von `feature/wenzelsbibel-ingest` (#66). Analog zu den 4 heute gesetzten Lead-Editor-respStmts (TKR/TKA/VTC/PUC/JT), aber in einem eigenen Commit.

*Roadmap (unabhängig, nicht heute angefasst):*
- **#17** Reader View TEI-Strukturelemente (prio-1, L effort) — nach Abschluss von #32-followup der nächste logische Großbrocken
- **#48** Playground URL-Routing — Kollege arbeitet parallel dran (`router.js` ist bereits in main, versehentlich in `8b5d0e6ac` gelandet)
- **#45** Static JSON API (L effort) — noch nicht angefangen
- **#47** TEI-Textanalyse-Playground — needs-clarification, Feature-Scoping offen

**Nicht-Befunde (damit niemand nochmal sucht):**
- Issue **#84** HZU/HZU2-Datum-Migration (heute früh vom User angelegt) war bereits seit 2026-04-09 erledigt — Phase A des ursprünglichen #32-Konsolidierung hatte das MMTT-Encoding auf Klartext migriert (`415e70147`, Co-Autor war Claude). Die TEI-MODEL.md §3.5 war veraltet und hat den User zur Falsch-Annahme „noch offen" verleitet. §3.5 ist jetzt auf Ist-Zustand aktualisiert.
- P1-7, P1-8, P1-9 waren bereits gestern (`f436963e0`) durch den Kollegen erledigt. Der `032-schema-followup.md`-Plan war nicht nachgezogen — heute repariert (Status-Tabelle am Dateianfang).
- Nicht-triviale CRLF-Falle in `Path.write_text()` auf Windows: erzeugt 14,6M-Zeilen-Diff statt der erwarteten 2-Zeilen-pro-Datei. Fix: `path.write_bytes()` mit dynamischer Newline-Erkennung. Dokumentiert im Commit-Body von `674fd3258` (P2-15).
- PL1-Validation-Pathologie war nicht die Größe (63 MB OVG validiert in 7.5 s), sondern **eine einzige `<p>` mit 404k direkten Kindern** (Prosa-Lancelot-Body komplett in einem Element). Der rekursive `<hi>`→`inline.model`-Matcher war der Verstärker. Fix: Daten-Split an `<pb/>`-Milestones + Schema-Rekursion entfernt.
- Der GitHub-Actions-`@claude`-Bot wurde heute versehentlich via Katharinas "Bestätige: @claude" auf #84 getriggert, hat einen Branch `claude/issue-84-20260415-0902` angelegt und die (bereits durchgeführte) HZU-Migration nochmal vorbereitet. Branch ist gelöscht, `claude.yml` ist weg. Der automatische PR-Review-Workflow `claude-code-review.yml` bleibt aktiv — reiner PR-Trigger, keine Mentions mehr.

**Next session:**
1. `/promptotyping orient`
2. **P1-5** angehen — das letzte offene #32-followup-Item, kontextspezifisches `idno/@type`-Enum im Korpus-Schema. Vorgehen: (a) Audit pro Position (`msIdentifier/idno`, `biblStruct/monogr/idno`) als ergänzendes Dry-Run-Ergebnis zu den schon vorliegenden 7 Werten, (b) neues `idno.type.msIdentifier` bzw. `idno.type.biblStruct` Pattern einführen, (c) `python -m rnc2rng` regenerieren, (d) smoke-test mit `scripts/audit/validate-corpus.py --sample ABG PUC GWTK TKR` — keine Full-Validation, weil die Semantik-Abdeckung heute schon gesichert ist.
3. Dann **Plan endgültig als 17/17 done** markieren und das Issue-Ticket (falls es eines gibt) schließen.
4. **Eigentlicher Nachmittag:** entweder Roadmap #17 (Reader-View, prio-1, L) oder auf externes Feedback zu #52/#62/#79 warten.
5. Im Hinterkopf: `tei/OVG.tei.xml` ist 62.89 MB (GitHub-Warning bei jedem Push wegen 50-MB-Empfehlung). Kein Blocker, aber LFS-Migration wäre ein sinnvolles separates Ticket, falls noch weitere Dateien diese Größenordnung erreichen.

---

## 2026-04-15 14:45 — handoff (Frontend-Session, post-audit)

Komplementär zum 12:10-Handoff des Schema-Kollegen. Diese Session lief parallel im gleichen Working-Directory und hat den Frontend-Stack bearbeitet: Playground-Router (#48), Lemmata-Explorer-Fixes + Similar-Lemmata-Section (#56), Linecode-Doku-Extraktion (#31), dazu einen Post-Session-Audit.

**Summary:** 7 eigene Commits auf `main` (plus `8b5d0e6ac` als versehentlicher Mit-Commit durch den Kollegen): #31 Linecode-Referenz-Docs, #56 Sub-Task 1+2 (URL-Bug-Fix) + Sub-Task 3 concept-based Similar Lemmata, #48 alle 5 Phasen des Hash-Routers, plus Audit: `#44` Triage-Matrix neu gefasst, `docs/features/031-*` gelöscht, `CLAUDE.md` Git-Rule für concurrent sessions ergänzt, Memory um `feedback_concurrent_sessions.md` + `feedback_scratch_files.md` erweitert.

**Commits (post-12:10 und für die Frontend-Track):**
- `ba6b1ebcc` #31 — `docs/LINECODE.md` + `docs/data/linecode-mapping.csv` aus Julias Handover-Ordner (OneDrive-SharePoint, lokal unter `C:/Users/chstn/Downloads/Linecode2TEI/`). Content aus `docs/features/031-linecode2tei-doku.md` in stable docs gehoben. 3 offene Template-Decoding-Fragen gehen als #31-Kommentar an Julia.
- `2c204cd4c` #56 S1+S2 — `playground/js/ui/authority/lemma-explorer.js`: Lemma-Titel werden klickbare `<a>`-Links zur persistenten Lemma-Seite (`../lemma/?id={numericId}`), plus URL-Bug-Fix im „MEHR →"-Button (alte Form `../lemma/${l.id}` produzierte `../lemma/lemma_879`, was `parseLemmaId()` zu `lemmaKey='lemma_lemma_879'` → nicht gefunden führte — MEHR→ war live broken).
- `dad8bb8a7` #56 S3 (concept-based) — `lemma/lemma-page.js` + `lemma/index.html`: neue „Ähnliche Lemmata"-Section, rankt alle 43 750 Lemmata nach Concept-Overlap mit dem aktuellen Lemma, Top 50 als Chip-Links. Performance: 75 ms für den Full-Scan. S3 distributional similarity (Co-Occurrence-Vektoren) remains out-of-scope — braucht Build-Time-Matrix, eigenes Follow-up-Ticket wenn gewünscht.
- `aad5a55bd` #48 Phase 3 — `?q=`-Auto-Fill. Shared `dispatch()`-Helper, 6 Authority-Views mit per-View Search-Input-ID-Map, `dispatchEvent('input')` triggert den bestehenden `setupSearchInput`-Listener.
- `0189a2eed` #48 Phase 4 — `?show=`-Drill-Down. View-agnostische `triggerExpand(itemId)`-Helper: findet den ersten Button, dessen onclick-Attribut die Item-ID als einfach-gequotete Substring enthält, und klickt ihn. Bekannte Limitierung: nur für Items im aktuell sichtbaren Result-Set (Top 50 nach Suche).
- `897431795` #48 Phase 5 — Multi-Lemma Modal State. Neuer `handleMultiLemmaRoute(params)`-Helper füllt `ui.lemmas` + Chips direkt, setzt Mode-Radio + Distance, ruft `executeSearch()` auf — Modal wird nie sichtbar, Ergebnisse landen direkt im `resultsContainer`. Chrome-Test: `#multi-lemma&lemmata=minne,êre&mode=proximity&dist=10` → 67 Treffer · 25 Kontexte.
- `db1a3b51e` audit — `docs/features/031-linecode2tei-doku.md` archiviert (Content in `docs/LINECODE.md`), per Temporal-Artifacts-Regel in `CLAUDE.md`.
- `44cf51adc` audit — `CLAUDE.md` Git-Rule „never `git add -A` with concurrent sessions" als direkte Konsequenz des `8b5d0e6ac`-Mishaps.

**Audit-Aktionen ohne eigenen Commit:**
- `#44` Triage-Matrix via `gh issue edit 44 --body-file` komplett neu gefasst (Quick Stats, Changes Since 2026-04-10, Full Matrix, Recommended Work Order). 26 open issues (excl. evergreen) — war vor dem Audit unvollständig, weil #73/#78/#79/#80/#81 nicht gelistet waren.
- Memory-Updates (lokal in `~/.claude/projects/.../memory/`, nicht im Repo): neu `feedback_concurrent_sessions.md` + `feedback_scratch_files.md`, Update `project_tei_consolidation.md` (Post-Milestone-Section 2026-04-15), `MEMORY.md`-Index um beide neuen Einträge erweitert.

**Katharina-Status (Stand 14:45):**
- **#17 ist freigegeben** (wachauer 2026-04-15 09:03): alle 5 Design-Fragen beantwortet — Scope-Refinement passt, deutsche `div/@type`-Labels passen, jede 5. Zeile Marginalia passt, „Strophe N"-Label oberhalb des Blocks passt, `hi rend="bold|italic|upper_case"` visuell abbilden. **Keine technischen Blocker mehr**, Top-of-Queue.
- **#56** „Bedeutungen anzeigen"-Entfernungsfrage an Katharina, noch keine Antwort.
- **#52, #62, #20** weiter auf Katharina-Approval.
- **#85** (neu heute) wartet auf Julia + Katharina für Hierarchie-Fragen und DL1/DWA-Sonderfälle.
- **#31** wartet auf Julia für 3 Template-Decoding-Fragen.

**Schnittstelle zum Schema-Kollegen-Track:**
Die #32-followup-Arbeit (P1-10, P2-12, P2-13, P2-14, P2-15, `<hi>`-Flatten, PL1-Split) ist weitgehend durch und hat alle technischen Blocker für #17 entfernt. Commit `8b5d0e6ac` (Kollegen-`#84`-Doku-Fix) hat versehentlich meine damals gestageten Phase-1+2-Router-Dateien mit-committet. Retroaktive Klarstellung in `20a9d1a22`. Die neue `CLAUDE.md`-Git-Rule + `feedback_concurrent_sessions.md`-Memory sollen das künftig verhindern.

**Nicht-Befunde (damit niemand nochmal sucht):**
- Der `@claude`-Action-Kommentar auf #17 um 09:05 mit einer Todo-Liste ist stale — der `.github/workflows/claude.yml`-Workflow wurde direkt danach (`54b450f32`) entfernt, die Action hat nie committet. #17 ist nicht in Arbeit, nur geplant.
- Julias OneDrive-Handover zur Linecode-Doku hat die `Mhdbdb_to_TEI(Linecode).csv` als Single-Source-of-Truth (kanonisches Letter-→-TEI-Mapping, 21 Zeilen, ~1.4 KB). Die ist jetzt als `docs/data/linecode-mapping.csv` committed. Julias PDF-Template `0000000000aaau----h` ist illustrativ — stimmt NICHT mit ALLs tatsächlichem 13-stelligen Linecode überein. Pro-Text-Varianz ist der Regelfall, siehe die hardkodierten per-text Regex in `Stanza Problem/fix_tei_stanzas.py` (ANN 5 Digits, AT 3 Digits, ALL 8 Digits).
- `docs/features/editor-attribution.md` bewusst nicht angefasst — Kollegen-Territorium, auch wenn #83 closed ist. Löschung per Temporal-Artifacts-Regel ist Kollegen-Entscheidung.

**Next session:**
1. `/promptotyping orient`
2. **#17 Reader View** — prio-1, direkt startbar. Implementation-Plan im 2026-04-15-Kommentar zum Issue. Erwartete Touches: `assets/js/rendering/tei-text-reader.js` (`extractAndFormatBody()`-Switch: neue Fälle für `note` (critical gap), `div`+`type`+`n` data-attrs, `lg`+`n`, `l`+`n`, `lb`+`n`, `hi rend` bold/italic/upper_case; `pb`/`cb`+`type`) + `assets/css/korpus.css` (CSS-Counter für jede-5.-Zeile-Marginalie, `attr(data-n)`-`::before`-Labels für div-Header, Strophe-Labels, hi-Varianten). Browser-Verifikation mit NIB (Strophen), ABG (Prosa), BRIX/ABS (Rezepte), HZU (`note type="date"`-Badges), PZ (Mixed), ALX/APO (colophon).
3. **Follow-up-Pings** (falls keine Antwort in 24 h): #52, #62, #56 (Bedeutungen anzeigen), #31 (Julia 3 Fragen), #85 (Julia + Katharina).
4. **Optional falls Leerlauf:** #45 Static JSON API (Planning-Doc vorhanden) oder #79 /hilfe/-Seite (braucht Wording-Entscheidungen, content-heavy).

---

## 2026-04-16 — handoff (Docs + Triage-Konsolidierung)

**Summary:** Promptotyping-Docs-Session nach gemeinsamer Issue-Triage mit Katharina, Julia und Chris. Zwei Health-Checks (Round 1 + ULTRATHINK Round 2) mit 10 Findings, alle gefixt. Systematische Neubewertung aller `depends-on-human` TEI-Daten-Issues → 4 von 5 umgelabelt auf `claude-ready`. Issue #44 Body komplett neu geschrieben mit Lösungskategorien-Framework. Playground-Router via Chrome-Extension browser-verifiziert.

**Decisions:**
- Lösungskategorien A–G eingeführt (Code/KI/KI+Web/Vorbereitung/Chris/Katharina/Julia/Extern) als Framework für Issue-Triage. In #44 Body dokumentiert.
- `depends-on-human` entfernt von #85, #81, #26, #73 — diese Issues sind durch Julias Antworten (15.04.), lokale Linecode-Files und KI-Web-Recherche-Fähigkeit tatsächlich lösbar.
- `external-research` Label reaktiviert und beschrieben: "KI kann via Web-Recherche lösen (HSC, Wikidata, VL, GND, Online-Editionen)".
- Audit-Output-Files (`scripts/audit/*.json`, `*-REPORT.md`) werden per `.gitignore` ignoriert, nicht committed.
- Feature-Doc `062-impressum.md` archiviert (#62 closed). `052-authority-files-card.md` wiederhergestellt (#52 noch offen — war versehentlich gelöscht).

**Phase:** Implementation (stable). Alle 14 Promptotyping-Docs aktuell. 6 Feature-Docs in `docs/features/` (017, 020, 032, 034, 045, 079 + restored 052).

**Commits:**
- `1c3c71136` — docs: post-triage update (ROADMAP, ARCHITECTURE, FEATURES, INDEX, DEVELOPMENT, CONTRACTS, .gitignore, 062 archiviert)
- `092839c4f` — docs/features/017: Reader View Plan mit Corpus-Inventar + hi/@rend compound fix

**Docs-Status (geänderte Dateien):**
- `docs/ROADMAP.md` — komplett neu: 6 geschlossene raus, #86-90 rein, #47 Sub-Issues, #34 Branch korrigiert
- `docs/ARCHITECTURE.MD` — Rendering Map `<seg>→<pc>` fix, Playground Router Section (Hash-Routing, dispatch, Views, Params), fragile Zeilennummern → Funktionsnamen
- `docs/FEATURES.MD` — Shareable URLs, Similar Lemmata, Lemma-Explorer-Links, TEI Text Analysis aktualisiert
- `docs/INDEX.MD` — Milestones #48, #56, #62
- `docs/DEVELOPMENT.MD` — CI Schema-Validation-Workflow (`schema-validation.yml`) dokumentiert
- `docs/CONTRACTS.MD` — fragile Zeilennummer → Funktionsname
- `docs/features/017-reader-view-tei-elements.md` — Corpus-Element-Inventar, hi/@rend compound fix, 7-Text Testmatrix

**GitHub-Aktionen (keine Commits):**
- Issue #49: Health-Check-Ergebnis als Kommentar gepostet
- Issue #44: Body komplett neu geschrieben (Lösungskategorien, Full Matrix, TEI-Daten Detail-Aufschlüsselung, Empfohlene Reihenfolge)
- Issue #44: 4 historische Kommentare gelöscht (Body ist jetzt Single Source of Truth)
- 8 Label-Änderungen: #85 (+claude-ready, -depends-on-human), #81 (+claude-ready, +external-research, +effort:small, -depends-on-human), #26 (+claude-ready, +pipeline, -depends-on-human), #23 (+claude-ready), #73 (-depends-on-human), #86 (+needs-clarification, +effort:medium), #78 (+effort:medium), #58/59 (+future plans)

**Browser-Verifizierung (Chrome-Extension):**
- `#lemmata&q=minne` → 168 Treffer, Suchfeld befüllt ✅
- `#multi-lemma&lemmata=minne,êre&mode=proximity&dist=10` → 67 Treffer, 25 Kontexte ✅
- `#authors` → 210 Einträge ✅
- `#concepts&q=liebe` → 1 Treffer "Liebe/Zuneigung..." ✅

**Nicht-Befunde:**
- `<seg type="pc">` Referenzen in TEI-MODEL.md, DECISIONS.MD, JOURNAL.md sind historisch korrekt (Migrations-Dokumentation), kein Fix nötig.
- `<seg type="component">` in DATA-MODEL.MD / TEI-MODEL-AUTH-FILES.md ist ein anderer `<seg>`-Typ (Etymologie), nicht von der pc-Migration betroffen.
- Fragile Zeilennummern in CONTRACTS.MD (search-engine.js, app.js, lemma-page.js, corpus-loader.js) und DESIGN.MD (app.js) — vorbestehend, separates Cleanup-Ticket wert.
- `docs/features/017-reader-view-tei-elements.md` modifiziert vom Kollegen (#17 Implementierung) — sein Commit, nicht meiner.

**Open Issues:**
- P1-5 `idno/@type` Enum — letztes offenes #32-followup-Item, ~1h, danach 032-schema-followup.md archivierbar.
- Julias Linecode-Quelldateien liegen lokal unter `C:\Users\chstn\Downloads\Linecode2TEI\` (291 Dateien). Noch nicht im Repo — Entscheidung ob/wie committen steht aus.
- #85 DWA: Julia sagt "passt vollkommen", aber DL1-Anzeige-Bug noch ungeklärt (Julia hat nicht reagiert).
- #23: Verifizierung welche Texte Julia bis RVR schon gefixt hat, steht noch aus (schneller grep).

**Next session:**
1. `/promptotyping orient`
2. **#81 Sprachstufen** (Quick Win, ~1h) — KI-Web-Recherche für 7 Kandidaten, Chris bestätigt, Header-Fix
3. **#85 Kat. 2** (7 song-Texte) — deterministisch, Script aus Linecode-Files
4. **#23 Verifizierung** — grep nach Julias bisherigen Stanza-Fixes
5. **#17 Reader View** — Kollege arbeitet aktiv dran, nicht anfassen
6. **#87-90** Playground TEI Textanalyse — 4 kleine Frontend-Issues, claude-ready


## 2026-04-16 — handoff (Audit + #17 Reader View)

**Summary:** Großer Issue-Audit (27 offene Issues, alle Kommentare von Katharina/Julia/Linda ausgewertet), 7 Issues geschlossen (#48, #31, #56, #62, #17 + 2 Temporal-Artifacts-Docs gelöscht), 4 Sub-Issues für #47 Release 1 angelegt (#87–#90), #17 Reader View vollständig implementiert und Chrome-verifiziert, 2 vorbekannte Playground-Test-Failures gefixt (128/128 grün).

**Decisions:**
- #17 braucht keinen Index-Rebuild — Reader View parst Raw-TEI-XML via DOMParser, nicht den Corpus-Index.
- `processHi()` von Switch auf Token-basierte Klassen umgestellt (`rend.split(/\s+/)` → CSS-Klassen `hi-initial`, `hi-bold` etc.) — löst ~43k bisher unstyled Compound-`@rend`-Elemente.
- `<lb>` Rendering: `<br>` + inline `<span class="lb-number">` statt Block-Span, weil `<lb>` ein Milestone-Element ist (Inhalt folgt nach, nicht innerhalb).
- Playground-Test-Failures waren veraltete englische Strings ("TEI Data Explorer" → "TEI-Daten-Explorer").

**Dead ends:** Keine.

**Phase:** Implementation (iteration). Alle 14 Promptotyping-Docs aktuell. `docs/features/017-reader-view-tei-elements.md` dreifach per `/check-md` verifiziert und korrigiert (FR1 war "Frauenlob" nicht "Frauendienst", h\_-Präfix in 43/64 Texten nicht nur ABG/HZU, ASCII-Art hatte continuous statt per-stanza Zeilenzählung).

**Open issues:**
- **#52** wartet auf Katharina OK (Card shipped, via Signal gepingt)
- **#79/#80** wartet auf Katharina Review (4 Hilfe-Seiten + Zitationsformat, 5+5 Fragen)
- **#73** MWB-Linking: 3 Fragen an Katharina, zero Antworten
- **#85** DL1-Frage auf GitHub beantwortet (Quelle: Julias Draft-Issue 06 aus OneDrive), Rückfrage an Julia was "weird" in der Anzeige war
- **#47** Sub-Issues #87–#90 angelegt, Katharina bestätigte 3-Release-Plan
- **#68** Katharina lieferte strategische Roadmap: WB → ARITHMETIC → CoReMA → Linda → Minnereden (10k EUR DFG)
- P1-5 (`idno/@type` kontextspezifisches Enum) noch offen — letztes #32-followup-Item

**Nicht-Befunde:**
- Die 2 Playground-Test-Failures (`should handle cache clearing`, `should load main playground page`) waren keine Regressionen sondern veraltete Strings seit der Lokalisierung. Fix: `d364cc38b`.
- `docs/features/052-authority-files-card.md` und `docs/features/062-impressum.md` gelöscht per Temporal-Artifacts-Regel (Issues geschlossen).

**Commits:**
- `1616f582e` Impressum: rechtliche Korrekturen + Datenschutz
- `1c3c71136` docs: post-triage update (6 closed, 5 new, stale refs)
- `092839c4f` docs/features/017: vollständiges Reader View Plan
- `ecebbb94e` **#17 Reader View: TEI-Strukturelemente** (JS + CSS + 7 Tests)
- `d364cc38b` fix(tests): Playground-Tests an deutschen Title

**Next session:**
1. `/promptotyping orient`
2. **#87 Playground UX-Cleanup** (broken buttons entfernen, TEI-Textanalyse nach oben) — S, schnell
3. **#20 Lesbarkeit follow-ups** — Katharinas 2 Punkte: Counter-Sichtbarkeit + Text-Deselection-Hint — S
4. **#88/#89/#90** Wortfrequenz / Text-Statistiken / Lemma-Verteilung — erste #47-Release-1-Features
5. **Follow-up-Pings** (falls keine Antwort): #52, #73, #79/#80
6. **Optional:** P1-5 `idno/@type` Enum (letztes #32-followup) oder #85 Implementation (Julia+Katharina haben geantwortet)
