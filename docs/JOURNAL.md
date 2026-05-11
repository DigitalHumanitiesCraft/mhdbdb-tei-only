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

## 2026-02-27 — Documentation Health Check (#49, closed 2026-05-11)

Quarterly check. Actions filed: #54 (dedup docs), #55 (lemma page docs). Process decision: health check reports go as Issue #49 comments, not as .md files in `docs/`. Convention later moved to `CLAUDE.md §Temporal Artifacts` when #49 was closed.

---

## 2026-04-07 — TEI Model Consolidation: Design (#32)

**Trigger:** Katharina will externe Daten aufnehmen → braucht formales Schema als Validierungsgate.

**Strategy:** 3+1 phases — Soll-Modell (TEI-MODEL.md) → Structural fixes → Schema (RELAX NG) → Attribute migration.

**Key findings:**
- 0/100 files valid against tei_all.rng — only 2 error types: `@meaningRef` + `@wordRef` (non-standard attrs)
- `@lemmaRef` IS standard TEI (att.linguistic since v3.3.0/2018) — no migration needed
- Batch rename `@meaningRef` → `@ana` + `@wordRef` → `@corresp` makes corpus TEI-conformant

**Policy decisions (all resolved):**
- POS tagset: 19-tag system from SKILL.md is canonical
- `<hi rend="initial">`: keep (655/675 files)
- `<l>` → `<lb/>`: migrate 18 prose files
- `<seg type="pc">` → `<pc join>`: migrate (1.4M elements)
- `@wordRef` → `@corresp` (not delete — carries non-reconstructible type→variant mapping)
- `@lemmaRef` → `@lemma`: deferred (cost >> benefit)

---

## 2026-04-13 — WZB Annotation Pipeline: Phases 1b, 2 + Structural Encoding (#34, #66)

**Trigger:** Resume Wenzelsbibel ingest on `feature/wenzelsbibel-ingest`. TEI hatte 150k `<w>` ohne Annotation. Ziel: korpus-integrationsreif.

**Phase 1b — Lemma disambiguation (91.6% coverage):** Pipeline `wzb-bulk-resolve.py` → TSV-Batches in `wzb-disambiguation.tsv` → `wzb-apply-lemmarefs.py` schreibt `@lemmaRef`. Batches 01–49 = 66,298 / 72,362 rows. Neue Lemmata: `lemma_78608` (Latin *et*), `78628` (Czech glosses), `78648` (*herte*), `78668` (*scot*), `78688` (*weise*). Residual ~6,064 (Pronomen/Kasus-Ambiguität, Bohemian hapax) intentional ohne `@lemmaRef`. Key insight: Bohemian scribal conventions (cz=z, v=u, ou=û, vor-=ver-) brauchten manual pattern recognition.

**Phase 2 — POS tagging (95.5% coverage):** `wzb-pos-assign.py` → pending TSV → LLM-Batches via `wzb-pos-bulk-resolve.py` → `wzb-pos-apply.py`. Batches 01–10 + context-resolver: 0% → 95.5% (143,340 / 150,017). Tagset migration `cf71ae48`: ART→DET, CNJ bulk re-routed zu CCNJ/SCNJ/ADV. Context-based resolver `ff83d087` löste 14,660 rows via ±4-word neighbour `@pos`. Key rules: `daz` (DET vs SCNJ), `haben` (VEX vs VRB), `ûf`/`vor` (PRP vs ADV), `ir` (POS vs PRO), `noch` (CCNJ vs NEG).

**Phase 3 — Paratext encoding (#66):** Strukturelemente encoded, vom lemma pipeline excluded. Via `wzb-structural-cleanup.py` + `wzb-resolutions-batch-paratext.tsv`:

| Element | Decision |
| ------- | -------- |
| `<fw type="header">` book names | Strip `@lemmaRef`/`@pos` — running headers, not lexical |
| CAPITULUM + Roman numeral `<w>` | `<head type="chapter" n="N">` + `<milestone unit="chapter">` inline |
| Scribal marks (ł, -, ̃, =, etc.) | `<w>` → `<seg type="pc">` |
| Single-letter initials (a, s, O) | `<w>` → `<seg type="pc">` |
| Roman numerals inline (UIII, XU) | Keep as `<w>`, `lemma_13826` (DIG) |
| Latin *et*, *est* | Keep as `<w>`, `lemma_1732`/`lemma_9387` |
| Czech glosses | Keep as `<w>`, `lemma_78628` |

**Structural fix `1d8fa549`:** 212 unnamed chapter divs → `type="chapter"`; 106 `<head type="chapter">` inside `<l>` (TEI-invalid) → first child of target div, `<milestone unit="chapter" n="N"/>` an Original-Position; space-tolerant `roman_to_arabic()` ("I X" → IX = 9).

**Encoding cleanup `2a6cbdd7`:** 6 `<w>` in `<hi rend="initial_historisiert">` → `<seg type="pc">`. `Josua.0` → `type="paratext"`, `xml:id="JosuaPrologus"`. `<div type="Transition2.1">` → `type="paratext"`. Unnamed prologus div → `type="section"`, `xml:id="Prologus.1"`.

**Final WZB state (2026-04-13):** 149,148 `<w>`, lemmaRef 91.6%, pos 95.5%, chapter-divs 211, book-divs 6, paratext-divs 12, head-chapter 106, milestone-chapter 106, seg-pc 35,479, fw-header 905. Remaining: `@meaningRef`/`@wordRef` migration (Phase 3 — nicht gestartet), dann main-merge.

---

## 2026-04-09 — TEI Migration: Implementation (Phases A-E)

15M+ Transformations über 675 Files in einer Session:

| Phase | What | Count |
|-------|------|-------|
| A | div/@type renames, monogr order, typos, dates, langUsage | 675 |
| B | @meaningRef→@ana (5.9M), @wordRef→@corresp (7.5M) + JS fixes | 675 |
| C | seg→pc (1.4M), l→lb in 18 prose files (86k) + JS fix | 668+18 |
| D | normalization from XLSX | 663 |
| E | RELAX NG schema + validation (675/675 pass) | 675 |

Plus: 9 disamb files merged into base (+35k POS), corpus index rebuilt (XPath→iter performance fix für PL1 45MB hang).

**Dead ends:** `encoding='unicode'` on Windows lxml → `LookupError` (Fix: `UTF-8`); l→lb script O(n²) auf PL1 → `addprevious`/`addnext`; 9 zombie Python processes → `taskkill`; Corpus index hanging at 440/666 → `tree.xpath()` mit namespace dict ist O(n²), Fix `iter()` mit Clark notation.

---

## 2026-04-10 — PR #1 Merged + Authority Migration + Schema Audit

**PR #69 (Corpus Migration → main):** 34 commits, 731 files, ~33M lines. Code review fand 3 bugs: `resolveConceptReferences` missed `@ana`, `<pc>` missing span wrapper in second rendering path, `etree.fromstring/tostring` round-trip. Alle gefixt vor merge.

**Post-merge cleanup:** Rendering refactor (dual path → single `_renderElement` closure); TEI-MODEL.md §10 auf v1.0.0; Example XML cleaned; Test invocation dokumentiert (`npm test` nicht `npx playwright test`).

**Authority Migration (Phases F-K, parallel Claude instance):** works.xml: 3,422 genre `<ref>` → 870 `<ptr/>`, IDs unwrapped, GND casing, Frauendienst/Frauenbuch split. persons.xml: listBibl removed (derived from works.xml), 4 UUID→numeric. lexicon.xml + variants.xml: 225 orphaned references removed. Build scripts: person→works derived from works.xml, version 1.2.0. Authority schema + 7 example files. Frontend: empty state, multi-word filter, pc-spacing with data-join.

**Corpus Schema Deep Audit — 11 gaps fixed:** `div` ist reserved keyword in RNC → `tei.div` (root cause of RNC→RNG conversion failure); `text` in choices → `mixed {}`; div/@type optional (154 files); body/div allow inline children (137+ files); multiple titles (291), @type/@level/@ana on title, multiple authors (5); biblStruct allows `<note>`, date allows @from/@notBefore/@notAfter; imprint flexible ordering; taxonomy `<bibl>` before categories. **Result: 666/666 valid, RNG generation works.**

Stale references in 6 docs gefixt (DATA-MODEL, RESEARCH, FEATURES, DESIGN, CONTRACTS, CLAUDE).  
Branch protection auf main via gh CLI (no force push, no deletion, PRs required).  
schema/README.md als single entry point. /check-md review (8 findings fixed).

---

## 2026-04-10 17:00 — handoff

**Summary:** #32 TEI Model Consolidation feature-complete. PR #69 (Corpus) + PR #71 (Authority) gemergt. Deep schema audit: 666/666 corpus files valid. Branch protection on main. 121/121 Playwright tests passing. #32, #70 (pc-spacing) geschlossen. Feature-Branch + 2 obsolete Branches gelöscht.

**Docs status (v1.0.0):** TEI-MODEL.md, TEI-MODEL-AUTH-FILES.md, `schema/mhdbdb.rnc`+`.rng` (666/666), `schema/mhdbdb-authority.rnc`+`.rng` (7/7), schema/README.md (external mapping guide), `schema/examples/` (8 validated).

**WZB-Branch:** braucht KEINE Attribut-Migration (hat bereits `@ana`/`@corresp`). Rebase auf main nötig nur für Docs/Config-Konflikte. 5 eigene Commits (#66), 1451 Dateien.

**Open:** #20 Lesbarkeit, #52 Authority Files Card — beide offen.

---

## 2026-04-14 18:30 — handoff

**Summary:** Frontend Quick-Wins #62 (Impressum) + #52 (Authority-Files-Card) gebaut, an wachauer eskaliert. Editor-Attribution-Plan bis Commit 3/7 durch (contributors.xml mit 51 Personen + 2 Orgs, Authority-Schema um `contributors.body`-Pattern erweitert, Corpus-Schema additiv für Mehrfach-respStmt + persName+@ref, Standalone-Migration-Script inkl. Whitespace-Bug-Fix verifiziert). WorksSyncer-gnd-Drift als P0-5 Pre-Fix vorab gefixt, damit nächster `--works`-Sync den P0-4-Fix (`61a0b4a1a`) nicht revertiert.

**Phase:** Implementation — editor-attribution 3/7 Commits done. Commits 4-7 (666-Datei Header-Migration, Lead-Editor respStmts, Doku, Script-Archivierung) warten auf User-Review + Go/No-Go.

**Whitespace-Bug:** `add_lead_editor()` las `child_indent` aus Struktur, wo vorherige letzte `<respStmt>` (von `migrate_collective_respstmt()`) noch `closing_indent` als `.tail` hatte → neue lead-editor-respStmt 2 Spaces zu weit links. Fix: vor Append `title_stmt[-1].tail = child_indent`. Verifiziert auf TKR.

**Commits (5 auf main):**
- `83d8546ed` Frontend #62 + #52 (impressum.html + footer-links + authority-card collapse)
- `05e9c2d91` #32-followup P0-5: WorksSyncer gnd→GND
- `6f80e5d47` editor-attribution Commit 1: contributors.xml + authority schema + example
- `1849a09fa` editor-attribution Commit 2: Corpus-Schema additiv
- `f2034fe94` editor-attribution Commit 3: migrate-header-credits.py (Script-only)

**Validierung:** 8/8 Authority-Files grün gegen tei_all + mhdbdb-authority. 9/9 Schema-Examples grün. Volle Korpus-Validierung 30/30 baseline, 0/0 mhdbdb baseline. Migration-Script Sample-Test sauber, 0 Whitespace-Noise. Full-Dry-Run 666 Files: 0 Fehler, `auth=True resp=True` überall, `lead=True` bei TKR/TKA/VTC/JT.

**Schema-Followup-Stand:** P1-5 `idno/@type` Enum braucht kontextspezifische Verteilung (Korpus hat 7 @type-Werte, `ISBN`/`callNumber` müssen unter `<biblStruct>`/`<monogr>` frei bleiben — nicht globaler Enum). P1-6 persName/@type clean (nur `preferred` + `alternative`). P1-10 msIdentifier/@corresp braucht Daten-Audit. P2-11 Doku-Kommentar 5 Min. P2-12 validate-corpus.py rewrite 30 Min. P2-13/14 CI-Schema-Validation 1h.

---

## 2026-04-15 12:10 — handoff

**Summary:** Massiver Schema-/Daten-Cleanup-Tag. editor-attribution komplett (Commits 1–6, #83 closed nach Katharina-Review), 16/17 Items aus `032-schema-followup.md` erledigt, zwei „Daten vor Schema"-Migrationen (PL1/PL2/PL3 Mega-`<p>` Split + nested `<hi>` Flatten über 143 Files), Schema verschärft (`<hi>`-Rekursion entfernt, persName/@type Enum, msIdentifier/@corresp Pflicht, Taxonomie-Body Doku-Kommentar), neue CI-Workflow `schema-validation.yml` mit RNG-Drift-Check + 2-stufiger Validation, `validate-corpus.py` als echter RelaxNG-Validator reimplementiert, `claude.yml`-Workflow entfernt (versehentliche `@claude`-Pings), CLAUDE.md Hard Constraint „Daten vor Schema".

**Phase:** Implementation — #32-followup praktisch komplett (1 Item offen: P1-5), editor-attribution komplett (WZB-Mini-Commit wartet auf #66-Merge), Korpus-Validation ~40% schneller (830s → 493s nach Data+Schema-Cleanup).

**Commit-Serie (alle main):** `7e526c8f2` P2-11 Doku-Kommentar; `f72887eaa` P1-6 persName/@type Enum; `7a79693d7` editor-attribution Doku; `9ab92cdb2` CLAUDE.md „Daten vor Schema"; `49d7b58aa` + `67526399e` PL-Mega-`<p>` Split + Archive; `b3e76ce7b` + `38b0bdd10` + `0f503ada8` Nested `<hi>` Flatten + Schema-Simplification + Archive; `54b450f32` claude.yml entfernt; `3ceb6b738` + `6bcd61d07` + `62ad64d2a` editor-attribution Commits 4-6 (full migration + doc-fix + archive, Closes #83); `674fd3258` + `1590f9405` P2-15 xml-model PIs + Archive; `8b5d0e6ac` + `20a9d1a22` #84 Doku-Fix + Klarstellungs-Commit (Closes #84); `83b511eec` P1-10 msIdentifier/@corresp Pflicht; `e9d43ead4` P2-12 validate-corpus.py rewrite; `becceda03` + `2d752769f` 032-Plan Status-Updates; `7d3801520` P2-13/14 schema-validation.yml CI.

Parallel Kollege (Frontend): `2c204cd4c` #56 Lemmata-Explorer, `aad5a55bd`, `0189a2eed`, `897431795`, `ba6b1ebcc` #31 Linecode-Doku — keine Kollisionen. `8b5d0e6ac` hat versehentlich gestagete Kollegen-Dateien aus `playground/` mit-committet, klarstellung in `20a9d1a22`.

**Katharinas Antworten (#83 closed):** Reihenfolge `<authority>`: Zeppezauer-Wachauer → Schmidt → Pütz. PUC auch Brom-Lead-Editor: JA. Klug/Gloning/Harsch NICHT in `contributors.xml` (externe Provider). 4 Institutionen NICHT (Datengeber). DHC drin.

**Open:** P1-5 letztes #32-followup-Item (~1h, kontextspezifischer `idno/@type` Enum); WZB Lead-Editor Mini-Commit wartet auf #66-Merge.

**Nicht-Befunde:** #84 (HZU/HZU2 MMTT) war bereits seit `415e70147` erledigt — Phase A hatte das migriert; TEI-MODEL.md §3.5 war veraltet, jetzt aktualisiert. P1-7/8/9 vom Kollegen schon erledigt (`f436963e0`), Plan-Status nachgezogen. CRLF-Falle in Windows `Path.write_text()` → 14,6M-Zeilen-Diff statt 2; Fix: `path.write_bytes()` mit dynamischer Newline-Erkennung. PL1-Validation-Pathologie war nicht Größe (63 MB OVG validiert in 7.5s) sondern **eine `<p>` mit 404k direkten Kindern**; rekursiver `<hi>`-Matcher Verstärker. GitHub `@claude`-Bot via Katharinas „Bestätige: @claude" auf #84 getriggert, hat `claude/issue-84-…`-Branch angelegt, ist gelöscht; `claude.yml` weg, automatischer PR-Review bleibt.

---

## 2026-04-15 14:45 — handoff (Frontend, post-audit)

**Summary:** Parallele Session zum 12:10-Schema-Track. 7 eigene Commits auf main: #31 Linecode-Referenz-Docs, #56 S1+S2 (URL-Bug-Fix) + S3 concept-based Similar Lemmata, #48 alle 5 Phasen Hash-Router. Plus Audit: #44 Triage-Matrix neu, `docs/features/031-*` gelöscht, CLAUDE.md Git-Rule concurrent sessions, Memory um `feedback_concurrent_sessions.md` + `feedback_scratch_files.md` erweitert.

**Commits:**
- `ba6b1ebcc` #31 — `docs/LINECODE.md` + `docs/data/linecode-mapping.csv` aus Julias Handover (OneDrive, lokal `C:/Users/chstn/Downloads/Linecode2TEI/`); 3 offene Template-Decoding-Fragen als #31-Kommentar an Julia.
- `2c204cd4c` #56 S1+S2 — `lemma-explorer.js`: Lemma-Titel klickbare Links, URL-Bug-Fix im „MEHR →"-Button (`../lemma/${l.id}` → `../lemma/lemma_879` → `parseLemmaId()` lemmaKey doppelt → nicht gefunden; MEHR→ war live broken).
- `dad8bb8a7` #56 S3 (concept-based) — Ähnliche Lemmata: rankt 43,750 Lemmata nach Concept-Overlap, Top 50 als Chip-Links. Full-Scan 75ms. S3 distributional similarity (Co-Occurrence) out-of-scope, eigenes Folge-Ticket bei Bedarf.
- `aad5a55bd` #48 Phase 3 — `?q=` Auto-Fill via Shared `dispatch()`-Helper, 6 Authority-Views mit per-View Search-Input-ID-Map.
- `0189a2eed` #48 Phase 4 — `?show=` Drill-Down. View-agnostische `triggerExpand(itemId)`: findet ersten Button, dessen onclick die Item-ID als gequotete Substring enthält. Limit: nur für Items im sichtbaren Top-50-Result-Set.
- `897431795` #48 Phase 5 — Multi-Lemma Modal State. `handleMultiLemmaRoute(params)` füllt `ui.lemmas` + Chips direkt, ruft `executeSearch()` auf. Test `#multi-lemma&lemmata=minne,êre&mode=proximity&dist=10` → 67 Treffer · 25 Kontexte.
- `db1a3b51e` audit — `031-linecode2tei-doku.md` archiviert.
- `44cf51adc` audit — CLAUDE.md Git-Rule „never `git add -A` with concurrent sessions" (Folge des `8b5d0e6ac`-Mishaps).

**Audit ohne Commit:** #44 Triage-Matrix komplett neu (Quick Stats, Full Matrix, 26 open issues exkl. evergreen — #73/#78/#79/#80/#81 fehlten vorher). Memory: neu `feedback_concurrent_sessions.md` + `feedback_scratch_files.md`, Update `project_tei_consolidation.md`, MEMORY.md-Index erweitert.

**Katharina-Status:** #17 freigegeben (alle 5 Design-Fragen beantwortet — Scope-Refinement passt, deutsche `div/@type`-Labels passen, jede 5. Zeile Marginalia, „Strophe N"-Label oben, `hi rend="bold|italic|upper_case"` visuell). Keine Blocker. #56 „Bedeutungen anzeigen"-Frage, #52/#62/#20 weiter auf Approval. #85 neu (Julia + Katharina für Hierarchie + DL1/DWA). #31 wartet auf Julia (3 Template-Fragen).

**Nicht-Befunde:** `@claude`-Action-Kommentar auf #17 um 09:05 stale — claude.yml direkt danach (`54b450f32`) entfernt, Action hat nie committet. Julias OneDrive-Handover hat `Mhdbdb_to_TEI(Linecode).csv` als Single-Source-of-Truth (21 Zeilen, ~1.4 KB) — jetzt als `docs/data/linecode-mapping.csv` committed. PDF-Template `0000000000aaau----h` ist illustrativ — stimmt NICHT mit ALLs tatsächlichem 13-stelligen Linecode überein. Pro-Text-Varianz Regelfall (ANN 5 Digits, AT 3 Digits, ALL 8 Digits per `Stanza Problem/fix_tei_stanzas.py`).

---

## 2026-04-16 — handoff (Docs + Triage-Konsolidierung)

**Summary:** Promptotyping-Docs-Session nach Team-Issue-Triage. Zwei Health-Checks (Round 1 + ULTRATHINK Round 2), 10 Findings, alle gefixt. Systematische Neubewertung der `depends-on-human` TEI-Issues → 4 von 5 zu `claude-ready`. #44 Body komplett neu mit Lösungskategorien-Framework. Playground-Router via Chrome browser-verifiziert.

**Decisions:**
- Lösungskategorien A–G (Code/KI/KI+Web/Vorbereitung/Chris/Katharina/Julia/Extern) als Triage-Framework. In #44 dokumentiert.
- `depends-on-human` entfernt von #85, #81, #26, #73 — durch Julias 15.04.-Antworten, lokale Linecode-Files und KI-Web-Recherche lösbar.
- Label `external-research` reaktiviert + beschrieben.
- Audit-Output-Files (`scripts/audit/*.json`, `*-REPORT.md`) per `.gitignore` ignoriert.
- Feature-Doc `062-impressum.md` archiviert (#62 closed). `052-authority-files-card.md` wiederhergestellt (versehentlich gelöscht).

**Commits:** `1c3c71136` docs post-triage update (ROADMAP, ARCHITECTURE, FEATURES, INDEX, DEVELOPMENT, CONTRACTS, .gitignore, 062 archiviert); `092839c4f` docs/features/017 Reader View Plan mit Corpus-Inventar + hi/@rend compound fix.

**GitHub-Aktionen:** #49 Health-Check-Kommentar; #44 Body neu (Lösungskategorien, Matrix, TEI-Daten Details, Reihenfolge); #44 historische Kommentare gelöscht (Body = SoT); 8 Label-Änderungen (#85/#81/#26/#23/#73/#86/#78/#58/#59).

**Browser-Verifizierung (Chrome):** `#lemmata&q=minne` → 168 Treffer; `#multi-lemma&lemmata=minne,êre&mode=proximity&dist=10` → 67 / 25 Kontexte; `#authors` → 210; `#concepts&q=liebe` → 1 Treffer.

**Nicht-Befunde:** `<seg type="pc">` in TEI-MODEL, DECISIONS, JOURNAL ist historisch korrekt (Migrations-Doku). `<seg type="component">` in DATA-MODEL/TEI-MODEL-AUTH-FILES ist anderer Typ (Etymologie). Fragile Zeilennummern in CONTRACTS + DESIGN vorbestehend, separates Ticket wert.

---

## 2026-04-16 — handoff (Audit + #17 Reader View)

**Summary:** Großer Issue-Audit (27 open, alle Kat/Julia/Linda-Kommentare ausgewertet), 7 Issues closed (#48, #31, #56, #62, #17 + 2 Temporal-Artifacts gelöscht), 4 Sub-Issues für #47 Release 1 angelegt (#87–#90), #17 Reader View vollständig implementiert und Chrome-verifiziert, 2 vorbekannte Playground-Test-Failures gefixt (128/128 grün).

**Decisions:**
- #17 braucht keinen Index-Rebuild — Reader View parst Raw-TEI-XML via DOMParser, nicht Corpus-Index.
- `processHi()` von Switch auf Token-basierte Klassen (`rend.split(/\s+/)` → CSS-Klassen `hi-initial`, `hi-bold`) — löst ~43k bisher unstyled Compound-`@rend`-Elemente.
- `<lb>` Rendering: `<br>` + inline `<span class="lb-number">` statt Block-Span (Milestone-Element, Inhalt folgt nach, nicht innerhalb).
- Playground-Test-Failures waren veraltete englische Strings ("TEI Data Explorer" → "TEI-Daten-Explorer").

**Commits:** `1616f582e` Impressum (Korrekturen + Datenschutz); `1c3c71136` docs post-triage; `092839c4f` features/017 Plan; `ecebbb94e` **#17 Reader View** (JS + CSS + 7 Tests); `d364cc38b` fix(tests) Playground deutsche Title.

`017-reader-view-tei-elements.md` dreifach per `/check-md` verifiziert: FR1 war "Frauenlob" nicht "Frauendienst", h_-Präfix in 43/64 Texten (nicht nur ABG/HZU), ASCII-Art per-stanza statt continuous.

---

## 2026-05-07 22:41 — handoff (#32-followup Abschluss + #68 Guide + WZB-Reorg + ARITHMETIC vorbereitet)

**Summary:** #32-followup komplett (17/17, P1-5 `idno/@type` Enum + WZB-shelfmark + Stage-1-PI cleanup 667 Files + CI push trigger). Neuer user-facing `hilfe-daten-beitragen.html` als technischer Schema-Konversions-Leitfaden (deutsch). WZB-Skripte aus `scripts/`-Wurzel in `scripts/ingest/wzb/` (20) und `scripts/_archived/wzb/` (4) reorganisiert. ARITHMETIC-Probe (Carina, 6 HS) inspiziert, #92 angelegt, Mail-Entwurf für Katharina an Carina vorbereitet.

**Decisions:**
- **#68 Architektur:** HTML user-facing in `hilfe-daten-beitragen.html`, kein Promptotyping-Doc-Duplikat. Promptotyping-Docs = LLM-targeted (englisch), user-facing = deutsch (`hilfe-*.html`-Pattern).
- **Guide-Tonality:** 99% der Leser haben TEI-Erfahrung; Erstkontakt via Kernteam. Guide ist Schema-Konversions-Reference, nicht Onboarding-Funnel. Erste Version (Eligibility/3-Pfade) komplett umgeschrieben zu technischem Re-Frame.
- **WZB-Skript-Aufräum-Tiefe:** Mittel (ingest-Struktur) statt Maximal (generische Skripte). Pipeline ist fertig, Refaktor ohne Nutzen.
- **ARITHMETIC:** Carina muss nicht nochmal an TEI ran. Konversions-Drift (`<seg type="token">` → `<w>`, `tei:`-Namespace, Header, xml:id) ist scriptbar. Sie liefert Metadaten + QA.
- **Domänen-Klassifikation in ARITHMETIC** (`<unit>`, `<person>`, `div/@type=commodity_calculation/reckoning_example`): offen an Katharina/Carina — erhalten (Schema-Erweiterung) vs. wegtransformieren.

**Dead ends:**
- Erstversion `hilfe-daten-beitragen.html` (Eligibility-Funnel + 3-Pfade + 6-Step-Workflow) komplett verworfen. Lesson: Tonality-Annahmen vorab abklären, nicht spekulativ bauen.
- Versehentlich `Arithmetic_MHDBDB.zip` mit `rm -f` gelöscht (dachte stray) — User hatte das absichtlich für Folgetask drin. Lesson: nie `rm` auf untracked files ohne Bestätigung.

**Commits:**
- `3d481c633` `#32-followup: P1-5 + WZB shelfmark + Stage-1 PI cleanup + CI push trigger`
- `56b97728b` `feat(hilfe): #68 hilfe-daten-beitragen.html — technischer Leitfaden`
- `5d3d3083b` `refactor(scripts): WZB-Pipeline nach ingest/wzb/, 4 Sackgassen archiviert`

Issue #92 ARITHMETIC angelegt (Labels `ingestpipeline`, `enhancement`). Memory: `project_arithmetic_ingest.md`. Mail-Entwurf für Katharina kopierbereit (extern).

---

## 2026-05-08 13:26 — handoff (Memory-Audit + #44 Re-Push + #81/#23/#91 Comments + GND-Fix)

**Summary:** Memory-System auditiert (3 stale Einträge weg, 2 Files gelöscht, MEMORY.md re-indexed). Schema-Bug `gnd → GND` in `corpus.example.tei.xml` gefixt (gepusht, valide gegen `mhdbdb.rng`). #44 zweimal nachgezogen (#17/#52 closed, #91/#92 ergänzt, Em-Dashes raus, #81/#23 Status präzisiert). Issue-Comments: #81 (4/7 Sprachstufen abgehakt + AC1-3 Klärungsfrage zu `enm`-Typo), #23 (Verifizierung "Julia bis RVR korrigiert" widerlegt: nur 2/104 gefixt; Stufe-1-Recon 96/100 HIGH-Konfidenz), #91 (Zenodo-Scoping mit 3 Team-Decisions + CITATION.cff-Skelett).

**Decisions:**
- **Memory-Hygiene:** `feedback_tei_model_file_locations.md` gelöscht (Pfad existiert nicht mehr). `project_tei_consolidation.md` zu Wissensanker (kein Status-Tracking). `feedback_script_conventions.md` auf neue Topologie aktualisiert. `feedback_no_playwright_parallel.md` → `feedback_ask_before_npm_test.md` umgewidmet.
- **#23 Stanza-Wrap-Format:** ohne `@n` (Schema sagt optional). User: "wir nehmen das was simpler ist".
- **#23 Skript-Location:** `scripts/temp/` (gitignored, lokal). Nicht `scripts/migrate/` weil Stufe 1 Recherche.
- **#81 AC1-3:** Action verschoben. Issue-Body Typo: `enm` ist Middle English (ISO 639-3), nicht FNHD. Klärung an Katharina: `gmh-x-fnhd` (BCP 47) vs. `gmh` lassen vs. `de-x-fnhd`.
- **ARI-Konfliktzonen-Disziplin:** `scripts/ingest/`, `tei/ARI*`, `schema/mhdbdb.rnc`, `hilfe-daten-beitragen.html`, `docs/TEI-MODEL.md` nicht angefasst.

**Dead ends:**
- Erste #81-Annahme: AC1-3 direkt scriptbar (per #44 „kanonisch FNHD"). Issue-Body hat Typo. Klärung > Action.
- Zwei Em-Dashes im ersten #44-Vorschlag durchgerutscht. Eigen-Review aufgedeckt: 13 Em-Dashes total. Lesson: bei Edits eines bestehenden Bodys nicht auf Original-Konsistenz vertrauen.
- Slip in Commit-Message für GND-Fix: `Schema-Konformitaet`/`gross` statt mit Umlauten (Verstoß `feedback_german_umlauts`). Memory war im Kontext, trotzdem passiert. Lesson: Commit-Messages mit gleicher Strenge prüfen.

**Commit:** `58fecc9b3` `fix(schema): GND-Casing in corpus.example.tei.xml` (gepusht).

**Externe:** #44 zweimal repush; #81 Body + Comment (`issuecomment-4405563024`); #23 Comments `4405583456` + `4405784301`; #91 Comment `4405625581`; Memory-System cleanups (siehe Decisions).

**Lokale Artefakte:** `scripts/temp/stanza-23-recon.{py,csv,md}` (gitignored). Plus 2 Commits paralleler Session: `5d118e5b7` (ARI Stage-0 #92), `81cd5b7c5` (docs/hilfe Konversions-Sektion). Gehören zu #92-Track.

---

## 2026-05-08 14:04 — handoff (Doc-Sync 3 Iterationen + ARI Stage 0 + Schema-Erweiterung PD-001)

**Summary:** Drei Iterationen `/promptotyping check` mit Faktenverifikation (10 Stable Docs aktualisiert, 3 Feature-Docs entfernt). ARI Stage 0 implementiert mit Dogfood auf München UB 279. Mail-Klärung mit Carina + Schema-Diskussion mit Katharina → PD-001-Beschluss „Mittelweg": alle 12 Element-Klassen + 24 `div/@type`-Werte optional ins Hauptschema. Schema-Erweiterung implementiert, RNG regeneriert, 667 Bestand + 6 ARI-HS validieren grün gegen Stage 2.

**Decisions:**
- **PD-001 Mittelweg (Katharina + Christian via Signal):** TEI-P5-Standardelemente aus Carinas Daten (`<unclear>`, `<add>`, `<gap>`, `<abbr>`, `<expan>`, `<am>`, `<g>`, `<roleName>`, `<occupation>`, `<placeName>`, `<unit>`, `<rs>`, `<figure>`) + Inline-Patterns für `<persName>`/`<person>` + 24 `<div>/@type`-Werte optional. Aufnehmen = erlauben, nicht vorschreiben. Modulares Schema (eigenes `mhdbdb-arithmetic.rnc`) wäre TEI-Lehrbuch-konformer, aber für n=2 (WZB+ARI) verfrühte Architektur.
- **ADR-013-Ausnahme: nested `<hi>` wieder erlaubt.** Carinas durchgestrichene Brüche (`<hi rend="line-through"><hi rend="superscript">2</hi>/<hi rend="subscript">3</hi></hi>`) semantisch nicht via Compound-Rend transformierbar. Performance unauffällig (2 Vorkommen in WIEN5206).
- **Lizenz BY-SA für ARI** (statt Doppelung BY-SA + BY-NC-SA). Carinas BY-SA Share-Alike-Klausel ist mit BY-NC-SA inkompatibel.
- **Generische Ingest-Skripte: noch nicht.** Audit `wzb-auto-match.py` und `wzb-pos-assign.py`: 95–98% mechanisch/korpus-agnostisch. Trotzdem n=2 zu wenig. Strategie: bei ARI-Phase 1 zu `ari-auto-match.py` kopieren mit `# ARI-only:`-Kommentaren, Diff messen. <10% → generalisieren. >30% → auf CoReMA (n=3) warten.

**Dead ends:**
- Erste Mail-Entwurf war faktisch falsch — nur München UB 279 inspiziert, 5 statt 12 Element-Klassen genannt. Audit aller 6 HS zeigte 12 Klassen + 24 div/@type. Lesson: bei „alle Daten"-Spec-Aussagen immer voll-auditieren.
- Mail-Vermischung — kompletten Entwurf geschrieben ohne zu wissen, dass User schon gesendet hat. Lesson: bei E-Mail-Tasks erst nach existierendem Stand fragen.
- Lizenz-Doppelung im Header-Template — mechanisch MHDBDB-Pattern (BY-SA + BY-NC-SA) ins ARI-Skript übernommen. User: „wieso doppelung?".
- Skript-Crash bei XML-Comments. Erste Konversion Einsiedeln 624 crashte, weil Carinas TEI Kommentare enthält und `deep_clone` die nicht handhabte. Defensive Checks ergänzt.
- Schema-Validation-Cascade unterschätzt. 5/6 ARI-HS failten erst mit Cascade-Fehlern. Schritt für Schritt aufgelöst (`<lb @break>`, `<roleName>`/`<occupation>` mit `inline.model`-Inhalt, `<persName>`/`<person>` als Inline-Patterns, `<note>` mit `<p>`-Children + `@place`, nested `<hi>`).

**Ingest-Pattern eingeführt:** `ingest/<sigle>/` als Top-Level für Source-Daten + Pipeline-Artefakte (analog `scripts/ingest/<sigle>/` für Skripte). Konvention seit dieser Session. WZB liegt aus historischen Gründen noch unter `Wenzelsbibel/` — Refactor zu `ingest/wzb/` als Folge-Task.

**Commits (alle main, NICHT gepusht außer `b5061085e`):**
- `b5061085e` `docs: Promptotyping doc-sync nach 2026-05-07-Handoff` — gepusht
- `5d118e5b7` `feat(ingest): ARI Stage-0-Konversion + Dogfood-Befund (#92)`
- `81cd5b7c5` `docs(hilfe): Konversions-Sektion + Katharinas ARITHMETIC-Antworten`
- `4972793ba` `docs(ari): PD-001 entschieden + Lizenz-Doppelung korrigiert`
- `b59350bb5` `feat(schema): MHDBDB-Schema-Erweiterung fuer ARITHMETIC (PD-001)`
- `bbb2c3549` `docs(tei-model): §6.0 "Optionale Erweiterungen" (PD-001)`

**Committete ARI-Artefakte (nicht in `tei/`):** `ingest/ari/` mit allen 6 HS + README. Stage-0 sauber + Stage-2-validiert. Header haben `work_TBD`/`genre_TBD`/`msIdentifier corresp TBD`-Platzhalter, deshalb `ingest/ari/` statt `tei/` (build-corpus-index würde sonst Platzhalter indexieren). Ziehen nach `tei/` um sobald Carina finale Metadaten liefert.

---

## 2026-05-08 14:54 — handoff (WZB live in beiden Indexen + Authority-Cache-Bugfix #94)

**Summary:** WZB.tei.xml lag annotiert in `tei/`, aber weder Corpus- noch Authority-Index rebuilt. Beide neu gebaut, Version-Bumps (corpus 4.0.0 → 4.0.1, authority 1.2.0 → 1.2.1). Beim Verifizieren entdeckt: Authority-Cache invalidierte de-facto nie, weil `cached.version !== cached.data.version` per Konstruktion immer falsch ist. Fix in derselben Session: zweite JS-Konstante `AUTHORITY_INDEX_VERSION` analog zu `INDEX_VERSION`, beide Pfade vergleichen gegen Konstante. End-to-end Browser-getestet, Suche „got" findet WZB.

**Decisions:**
- **PATCH statt MINOR für Datenzugänge.** Index-Bumps für „neuer Text rein" sind PATCH (4.0.1, 1.2.1). MINOR/MAJOR bleibt reserviert für Schema/Algorithmus-Änderungen.
- **Ein Commit für Rebuild + Bugfix.** Bug wurde *durch* den Versions-Bump entdeckt, ohne Fix wäre Bump wirkungslos. Coupling rechtfertigt gemeinsamen Commit.
- **AUTHORITY_INDEX_VERSION-Konstante statt self-referential check.** Bestand-Logik verglich `cached.version` gegen `cached.data.version` — beide aus derselben Cache-Quelle, also nie auseinanderlaufend. Neue Logik spiegelt Corpus-Pattern (Konstante als Wahrheitsquelle).
- **`variants.xml`-Sweep des Kollegen NICHT in WZB-Commit aufgenommen** — Header „666 → 667" war parallele Sweep-Session, gehörte in dessen Commit `f14683f07`. Memory `feedback_concurrent_sessions` hielt das scharf.

**Dead ends:**
- Erster Rebuild zog ARI_MUE279 als Beifang. Build-Skript scannt blind `tei/`. Während paralleler ARI-Session lag `tei/ARI_MUE279.tei.xml` als untracked file dort. Erster Build → 668 Texte (WZB + ARI). User-Hint → nach ARI-Entfernung sauber rebuilt → 667.
- „Nur kosmetisch"-Fehlschluss bei `variants.xml`. Erster Check via `git status` zeigte nur uncommitted Diff. User korrigierte: Authority-Files könnten zwischen WZB-Ingest und letztem Index-Build *committed* worden sein. mtime-Check bewies: `lexicon.xml`/`works.xml` 2026-05-07, Index 2026-04-10. Lesson: bei „Hat sich was geändert?" nicht nur `git status`, auch mtimes + commit-history gegen `generatedAt`.
- Backup-Race-Condition: Backup parallel zum Build → `cp` erwischte NEUE Datei statt alter. Workaround: `git show HEAD:data/authority-index.json.gz` für sauberen Diff. Lesson: Backup VOR Build, nicht parallel.

**Commit:** `d7011105f` `feat(ingest): WZB-Index-Rebuild + Authority-Cache-Bugfix` (5 Files). Push umfasste auch 3 Kollegen-Commits ab `f14683f07`.

**Externe:** Push deployed WZB live `https://dhcraft.org/mhdbdb-tei-only/korpus.html?text=WZB`. #94 erstellt + sofort geschlossen (Bug-Doku, Fix-Referenz `d7011105f`, Label `frontend`). Kommentare auf #34 (WB live) und #68 (Dogfood-Lessons aus WZB).

**Verifikation:** `totalTextCount` 666 → 667 nach Cache-Invalidation, Console `Cache version mismatch for authority-index: 1.2.0 != 1.2.1` und `Authority index loaded: 43754 lemmata`. Suche „got" findet WZB (~800ms). 142,174 Tokens / 2,142 Lemmata in WZB, +4 neue Lemmata + work_WZB.

---

## 2026-05-08 15:04 — handoff (Hilfe-Faktencheck + Issue-Updates + #79 closed)

**Summary:** Nach parallelem WZB-Rebuild-Track (`19aa5b955`) Faktencheck über 4 Hilfe-Seiten: Variantenzahl `175.910 → 192.472` an 5 Stellen, 4 Authority-File-Größen in `hilfe-daten.html` aktualisiert, Stand „Mai 2026" überall, Em-Dash-Hygiene. Issue-Comments auf #92 + #68. #79 (User-facing Hilfe-Seite) geschlossen, 7/8 AKs erfüllt; Plan-Doc `079-hilfe-seite.md` gelöscht.

**Decisions:**
- **#79 schließen, nicht offen lassen:** 7/8 AKs erfüllt — Hub erreichbar, 5 V1-Seiten live (pragmatisch reduziert von 12), Nav-„Hilfe" auf allen Hauptseiten, Zitation mit Copy-Button, Lemmata-/Variantenzahl konsistent, keine englischen UI-Strings, `docs/research/` archiviert. Playwright-Smoke-Test als Maintenance-Folge.
- **Plan-Doc `079-hilfe-seite.md` löschen** statt aufbewahren: ursprünglicher 12-Seiten-Plan in 5 Seiten umgesetzt; Doc beschrieb nicht-existente Struktur. Promptotyping-Konvention sagt zwar „Doc bleibt während Issue offen", aber obsoletes Doc schadet mehr als es nützt. Git-Historie als Archiv.
- **Em-Dash-Hygiene auch in Code-Snippets:** einen Em-Dash gefixt, den ich heute eingeführt hatte (§7 `'FAIL — toleriert'`). Memory verbietet Em-Dashes in user-facing — auch in Code-Snippets (sichtbar im print-Output). Doppelpunkt statt Em-Dash.

**Dead ends:**
- Eigenes Review unvollständig. Erstes „alle Punkte gefixt"-Statement übersah einen SHOULD-FIX (S3 Initial-Pattern §3.2). User: „hast du das alles gefixed?". Lesson: bei eigenem Self-Check Punkt-für-Punkt abgleichen, nicht auf Buchhaltung im Kopf verlassen.
- Mail-Quellen vermischt (vorige Session): Entwurf vermischte Carinas Originalmail, ihre Antwort und Katharinas Signal-Chat. Lesson: bei Mail-Tasks erst nach existierendem Stand fragen.

**Commits:** `cb99c1df5` Hilfe-Faktenkorrektur + Stand-Update Mai 2026; `ff504cdf8` features/079-hilfe-seite.md gelöscht.

**Externe:** #92 Comment `4406549960` (ARITHMETIC-Stand); #68 Comment `4406552591` (hilfe-daten-beitragen.html Erweiterungen); #79 closed.

---

## 2026-05-11 11:59 — handoff (Session A: Playground Release 1 + 3 Follow-up-Cleanups)

**Summary:** Parallele Zwei-Session-Arbeit. Session A: Playground Release 1 komplett (#87 UX-Cleanup, #88 Wortfrequenz, #89 Text-Statistiken, #90 Lemma-Verteilung) — alle Chrome-DevTools-verifiziert (Stichproben „minne"/„êre", NBB/PZ/ABG). Vier Follow-ups: Corpus-Index-Schema in DATA-MODEL.MD dokumentiert, #97 Corpus-Source-Inkonsistenz repariert, #98 Dead Code raus, #99 toter loadCorpusBtn-Setup-Block weg, #100 Pre-flight-Check für Build-Skripte. Session B parallel: #20 Lesbarkeit + #96 Metadatenanzeige + CITATION.cff-Vorbereitung.

**Decisions:**
- **Briefing-Workflow für parallele Sessions etabliert:** zwei detaillierte Briefing-MDs (`briefing-session-a.md` + `briefing-session-b.md` auf Desktop) mit Audit-Sektion „ist das schon erledigt?" und Pfad-Ankern. Wert: Audit präzisierte in Session A bereits beim Start #87-Tasks (Buttons nicht „broken", nur redundant) und entdeckte Corpus-Index-Schema-Mismatch früh.
- **Corpus-Quelle-Inkonsistenz minimal-invasiv (#97):** `autoLoadCorpus()` spiegelt Index zusätzlich nach `teiManager.corpusIndex`, statt einen Pfad zu eliminieren. Same Reference, kein Refactor-Schock. Größere Aufräumarbeit → #99 separat.
- **Dead-Code-Cleanup-Strategie:** zwei Wellen. Erst direkt durch #88/89/90 obsolete Methoden (`calculate*Frequency`/`POSDistribution`), dann tot-aber-sichtbarer Block (Context, Cross-Reference, CSV-Export, Lemma-Prompt). ~700 Zeilen raus, tei-ui.js 581 → 404 Zeilen.
- **Pre-build-Hygiene als Issue + Implementation (#100):** subprocess-basierter `git status --porcelain`-Check vor jedem Index-Build. `--allow-dirty` für lokale Tests; CI baut von committetem main. Windows-cp1252-Encoding-Issue (Unicode-Pfeil `→`) durch ASCII-only umgangen.
- **Test-Sicherheit vor Refactor:** `corpus.spec.js:302` referenziert `loadCorpusIntoPlayground` per `typeof`-Check. Methode bleibt in tei-manager.js, nur nie-laufender Setup-Handler in playground-main.js raus.

**Dead ends:**
- Test-Sigle „NIB" für Nibelungenlied: Briefing-Annahme, tatsächlich Sigle `NBB`. Erst gemerkt als `s.value='NIB'` 0 Rows lieferte. Lesson: Sigle-Listen nicht raten, einmal `corpusData.texts[].id` greppen.
- DevTools-Console-Polling zu kurzer Timeout: initiale `autoLoadCorpus`-Wartezeit 4s, Promise gab `TIMEOUT` zurück obwohl Corpus tatsächlich da war (unter anderer Property). Lesson: erst Property-Pfad verifizieren, dann polling-Logik bauen.
- `020-lesbarkeit.md` durch meinen Commit gelöscht: Session B hatte Plan-Doc nach #20-Abschluss gestaged, mein `git add <files> && git commit` nahm staged Deletion mit. Schaden null, gutes Beispiel für `feedback_concurrent_sessions`.

**Commits (alle gepusht, neueste zuerst):**
- `c8dfe0f0c` Pre-flight Working-Tree-Check (#100)
- `cd01c811e` toter loadCorpusBtn-Setup-Block raus (#99)
- `d75956e0e` Dead Code tei-ui.js raus (#98)
- `30c512d64` Corpus-Index unter teiManager.corpusIndex spiegeln (#97)
- `a6721de7e` docs+chore: Corpus-Index-Schema dokumentiert + Frequency-Dead-Code raus
- `a5a4a750c` feat(playground): Lemma-Verteilung Bar-Chart (#90)
- `42a7b4467` feat(playground): Text-Statistiken (#89)
- `2fc4f02d7` feat(playground): Wortfrequenz-Analyse (#88)
- `3f97bbc7d` fix(playground): UX-Cleanup (#87)

Session B (chronologisch verschachtelt): `0a287cccf` (#96 Reader-Download), `5ea823f5e` (CITATION.cff + DOI-Badge), `b5f947001` (#20 Lesbarkeit), `1c28b8b09` (CITATION-Stub-Reduce).

**Externe:** #87/#88/#89/#90 closed via `Closes #X` (~09:41). #97/#98/#99/#100 gefilet und sofort geschlossen (09:45-09:57). Session B closed #20 + #96.

**Open:** #47 Release 2 (Begriffs-Verteilung) und Release 3 (POS-Anteile in #89, abhängig von #27) noch ungeplant. Upload-UI Dead-Code-Großreinigung (`handleTEIFiles`, `uploadZone`, `fileInput`, ungenutzte tei-manager.js-Methoden) als M-Effort-Cluster mit #98/#99 wert.

---

## 2026-05-11 12:32 — handoff (Session B: #20 + #96 + #91-Stub + Doku-Sync + Audit-Toolchain)

**Summary:** Session B parallel zum Playground-Track. Drei Briefing-Issues: #20 (Counter `text-2xl` + blue-50-Hinweisbox), #96 (TEI-XML-Download-Link am Ende Reader-Metadaten + Anonym-Wikidata-Link unterdrückt), #91 (CITATION.cff-Stub + DOI-Badge-Platzhalter; KZW gepingt, hat in dieser Session auf `type=dataset` verfeinert). WZB-Stage-2-Fail in `works.xml` aufgelöst gemeinsam mit Julias `af72bd261`. Anschließend `/promptotyping check` — alle drei Should-Fixes erledigt (TEI-MODEL.md §10 auf 667/667 + Authority-Files 8 + WZB-Note, ROADMAP.md closed-Issues raus, INDEX.MD Milestones extended) und 4 von 6 Blind-Spots umgesetzt.

**Decisions:**
- **Daten vor Schema bei WZB-Eintrag:** works.xml-Verstöße (`<ref>` statt `<ptr>`, `<note type="manuscript">` direkt unter `<bibl>`, `<biblStruct>` ohne `<relatedItem>`-Wrapper, `<date>` außerhalb `<imprint>`) durch Daten-Migration gelöst statt Schema-Lockerung. KZW: Manuskript-Signatur "Wien, ÖNB, Cod. 2759-2764" in `note` mergen statt droppen. Julias paralleler Fix `af72bd261` flanschte Normdaten an (Wikidata Q476495, GND 4117632-7, HSC werke/4577); Merge-Konflikt sauber via `git checkout` + ff-pull + Folge-Edit.
- **Reading-View-Render-Policy als Issue #101:** nach drei Handoffs Schwebezustand jetzt explizit als Issue mit Domain-Element-Fragenkatalog (Bibelvers-Marker, Kapitelköpfe, Initialen, Marginalia, Rubrum) für KZW + Julia.
- **Pre-Commit-Hook (Blind-Spot F) verworfen:** CI Schema-Validation deckt es ab.
- **Briefing-Tooling (Blind-Spot E) verworfen:** Briefings sind ad-hoc.
- **doc-count-audit.py als Drift-Detektor, kein Auto-Fixer:** meldet stale Zahlen, ändert keine Markdown. Heuristik Window ±2 absolut bzw. ±2% relativ + striktem Keyword-Anchor unmittelbar nach der Zahl, damit historische Migration-Counts ("@meaningRef in 666/666 Dateien") nicht als Drift gemeldet werden.
- **CITATION.cff Single-Author belassen:** KZW-Edit `8e4202ffc` hat Stub auf nur sie als Lead-Autorin reduziert + `type=dataset` (passender für ZfdG-Data-Paper-Einreichung). Pre-Tag-Checkliste auf #91 dokumentiert.

**Dead ends:**
- Briefing-Sigle-Drift: Briefing nannte "NIB" für #96 — existiert nicht im Korpus, NLA-Treffer (Nibelungenlied) genutzt. Zweite Briefing-Drift-Bestätigung neben Session A's NIB→NBB. Als Blind-Spot E verworfen.
- doc-count-audit.py Heuristik-Iteration: erste Version Window ±30 + generic-keyword: 39 False Positives auf Migration-Counts. Mit engerem Window + striktem Anchor reduziert.
- Redundanter `git rm docs/features/020-lesbarkeit.md`: Session A hatte das File schon in `cd01c811e` (Cluster-Cleanup) gelöscht. Lesson: vor Doc-Cleanups einmal `git log` durchschauen.
- Stage-1-Drift-Diagnose im Kreis gelaufen: `[:20]`-Truncation in `validate-corpus.py` verbarg, dass „31. Fail" works.xml selbst war (gleichzeitig Stage-1 + Stage-2). Erst nach Vollvalidierung (~7 min) + CI-History-Check klar. Mit `b6881c3ad` + Baseline-Drift-Marker in `3155082e7` für künftige Drifts adressiert.

**Commits (alle gepusht):**
- `26a4cd882` `fix(WZB): Manuskript-Signatur in Note aufnehmen`
- `0a287cccf` `feat(reader): TEI-XML-Download-Hinweis + Anonym-Wikidata weg` (Closes #96)
- `b5f947001` `style(korpus): Counter prominenter + klarer Deselect-Hinweis` (Closes #20)
- `5ea823f5e` `chore(release): CITATION.cff + Zenodo-DOI-Badge-Stub`
- `1c28b8b09` `chore(release): CITATION.cff Author-Stub auf Lead-Autorin reduziert`
- `b6881c3ad` `chore(audit): validate-corpus.py — volle s1-fail-Liste`
- `7f4efa7fa` `docs: stable docs auf 667-Korpus synchronisieren`
- `3155082e7` `chore(audit): Baseline-Drift-Marker + Doc-Count-Audit`

**Externe:** #20 + #96 closed via `Closes #X`. #44 aktualisiert (25→24 open, 12 closed seit 05-08, claude-ready reduziert). #91 KZW-Ping für Final-Author-Liste + Pre-Tag-Checkliste (8 Punkte, Trennung Claude vs. User). #101 neu (Reading-View-Render-Policy, Label `frontend`).

**Verifikation:** Chrome: NLB im Reader — Download-Link auf `tei/NLB.tei.xml` aktiv (HTTP 200, 14.3 MB), Wikidata weg. HTR: Download aktiv, Wikidata bleibt. `korpus.html` "667/667 Texte" deutlich größer, Hinweis-Box sichtbar. Filter („Nibelung" → 4, „Keine" → 0/667) regressionsfrei. Vollvalidierung lokal: 30/30 baseline, 0 Stage-2-Fails. CI seit `26a4cd88` grün. `doc-count-audit.py`: alle Zahlen auf 667/8/43,754/584 — keine Drift.

---

## 2026-05-11 14:04 — handoff (Session D: #26 pb-Insertion + #49 close + Editorial-Assignees + JOURNAL-Kompression)

**Summary:** #26 (Nov 2025, 6 Monate offen) gelöst — 1293 `<pb>`-Elemente über 14 TEI-Files via Linecode-Handover-Templates. Drei Folgearbeiten: #49 als evergreen geschlossen (operative Mechanik via `/promptotyping check` + MHDBDB-Checkliste nach CLAUDE.md §Temporal Artifacts migriert), 9 editorische Issues mit beiden Assignees (wachauer + juliahin) ausgestattet, JOURNAL.md von 937 → 458 Zeilen komprimiert (49% Reduktion, alle Hard-Facts erhalten).

**Decisions:**
- **`<pb>`-Insertion-Logik:** immer-`<pb>`-direkt-vor-`<w>`-Wrapper. Bei Line-Aligned (preceding sibling = `<lb>` oder erste Position in `<l>`): insert vor `<lb>`/`<l>` (BDK-Konvention). Sonst inline vor `<w>` (Mid-Line-Page-Break wie MBS7 page 141r zwischen "ein"/"grosse").
- **Combined `n="62r"`-Format** statt zwei `<pb>` für recto/verso (folgt WZB-Precedent). Schema erlaubt beides; WZB-Stil ist konsistenter.
- **lxml-PI-Serialization-Bug umgangen:** lxml droppt Newline zwischen `<?xml-model?>` und `<TEI>` auf write. Workaround: `etree.tostring(tree)` → bytes-replace `?><TEI ` → `?>\n<TEI `. Funktioniert für alle 14 Files.
- **#102/#103 als separate Followups** statt #26-Erweiterung: BDK (vorhandene 24 `<pb>` ohne BDK.txt verifizierbar — Julia/Edition-blockiert), DIS (Linecode-Template hat keine `p`-Position — Katharina-Policy + Edition Grubmüller 1996 nötig). Beide diagnostisch dokumentiert.
- **#49 schließen statt evergreen halten:** Doppelung zu `/promptotyping check`. MHDBDB-spezifische Checkliste (Flow / Algorithm-Spot / XPath-Spot / Rebuild-Test + Trigger + Meta-Fragen) jetzt in CLAUDE.md, operative Mechanik im Slash-Command. Historische Comments via Issue-Search erreichbar.
- **Editorial-Assignee-Konvention (User-Direktive):** bei allen Issues mit editorial-philologischer Komponente immer beide (wachauer + juliahin) — Memory-Regel `feedback_editorial_assignees.md` angelegt.
- **JOURNAL-Kompression moderat:** Boilerplate raus (15× identische "Phase: Implementation (iteration)"-Zeilen, bereits-erledigte "Next session"-Items, redundante "Externe Side Effects"-Verschmelzung), Prosa-Puffer gedichtet, leerer Stub-Header entfernt. Alle 91 Commit-Hashes + 54 Issue-Refs + alle Decisions/Dead-Ends/Lessons inhaltlich erhalten.

**Dead ends:**
- Initiale `find_line_element()` walkte preceding-siblings zu weit zurück → fand `<pb>` aus früherer Sektion → False-Positive "already_has_pb" für 30 MR1/MR2-Anker. Fix: nur immediate preceding sibling prüfen. Lesson: bei walk-back-Logik IMMER auf den ersten Treffer beschränken, nicht den Loop weiterlaufen lassen.
- Falsche "Bug"-Diagnose bei MAJ/MSV: `MAJ` letztes Song `@n="3"` und `MSV` zweites Song `@n="1"` schienen wie Tippfehler. Verifikation via xml:id-Linecode-Decoding zeigte: chapter-lokale Nummerierung (`MAJ_2030101_0` = chapter 2 / lied 3). KEINE Bugs — Spec-Aussagen ohne Daten-Cross-Check sind riskant. Lesson: vor "Fix"-Action immer am xml:id verifizieren.
- HEREDOC für `gh issue edit 44` mit komplexem Body (Backticks + Quotes) failte → über `--body-file` mit Scratch-Datei `~/.cache/claude-scratch/issue44-body.md` gelöst. Lesson: für komplexe Issue-Bodies immer `--body-file` mit Temp-File.
- DUE-Lieder-Struktur ist editorial-blockiert: Linecode sagt 1 Lied × 5 Strophen (`dd=00` für alle 5), TEI hat 5 Songs × 1 Strophe. Beide Lesungen plausibel (Spruchdichter-Tradition vs. DB-Encoding). Nicht-deterministisch ohne Julia/Katharina.

**Phase:** Implementation (iteration). Alle 14 Promptotyping-Docs aktuell + heute 1× `CLAUDE.md` aktualisiert (§Temporal Artifacts erweitert um Health-Check-Checkliste, "NEVER close"-Liste auf #44 + #91 reduziert). Nur noch 2 Feature-Docs in `docs/features/`: `034-wenzelsbibel-annotation.md`, `045-static-api.md`. JOURNAL.md neu komprimiert (458 Zeilen statt 937).

**Open issues (post-Session):**
- **#102 BDK (neu, Julia + KZW):** 24 `<pb>` verifizieren. Template aus CSV passt nicht zur Datei. Braucht originale BDK.txt oder Edition Eckhardt/Hübner (MGH Fontes). Gap-Analyse flagged pb=8→9 (973 Zeilen) und pb=9→10 (1255 Zeilen) als potentiell fehlende Marker.
- **#103 DIS (neu, KZW + Julia):** Linecode hat keine `p`-Position. Editorial-Policy-Entscheidung: paginieren ja/nein? Wenn ja: Edition Grubmüller 1996 konsultieren. 408-Vers-Reimpaarspruch von Hans Rosenplüt verteilt sich auf 8-12 Druckseiten.
- **#85 (KZW + Julia):** Kat. 2 strukturell done (`ef939f530`), nur DUE editorial-blockiert (5 Songs × 1 Strophe TEI vs. 1 Lied × 5 Strophen Linecode). Kat. 1 (13 MBS-Serie) und Kat. 3 (3 parallel/supplied) noch zu machen.
- **#101 Reading-View-Render-Policy:** KZW + Julia für Domain-Element-Entscheidungen (Bibelvers-Marker, Kapitelköpfe, Initialen, Marginalia, Rubrum). Erst nach Antwort wird Implementation-Issue eröffnet.
- **#92 ARITHMETIC:** unverändert (Carinas Antwort zu Metadaten + Begriffssystem).
- **#91 Zenodo:** Pre-Tag-Checkliste auf Issue, wartet auf manuellen Webhook-Setup + ersten Tag.
- **#81 Sprachstufen AC1-3:** wartet auf KZW BCP-47-Entscheidung. 5-min-Edit danach.
- **#23 Stanza-Insert:** ~80 Texte skript-ready (deterministisch), aber 21 Prosa-Texte brauchen Katharina-Policy zu `l` vs. `lb`.
- **package.json/build-vendor.js (heute morgen) und Session C's prismjs-Setup:** zwischen Sessions parallel committed durch Kollegen; nicht von dieser Session.

**Commits (alle gepusht, neueste zuerst):**
- `a1a53f663` `docs(journal): JOURNAL.md von 937 auf 458 Zeilen komprimiert`
- `5040bfabc` `docs: #49 Health-Check-Checkliste nach CLAUDE.md migrieren` (+ Evergreen-Liste auf #44 + #91 reduziert)
- `795670240` `feat(tei): #26 pb-Insertion fuer 14 Texte (1293 <pb> aus Linecode-Handover)` (Closes #26)

**Skript-Artefakt:** `scripts/insert-pb-from-linecode.py` (NEU) — wiederverwendbar für künftige pb-Insertions aus Linecode-Quellen. Bonus für BDK falls Julia BDK.txt nachliefert.

**Externe Side Effects:**
- Issues geschlossen: **#26** via Commit `795670240`, **#49** via Status-Comment + `gh issue close`.
- Issues angelegt: **#102** (BDK pb verifizieren), **#103** (DIS Page-Encoding) — beide mit präziser Diagnose + Unblocking-Request.
- **#44 Triage-Matrix** zweimal aktualisiert: erst #26→Recently-Completed + #102/#103 in Depends-on-Human, dann #78 (Kollege) + #49 in Recently-Completed; Evergreen-Liste auf #44 + #91 reduziert.
- **9 Issues mit Assignees ergänzt:** #101/#102/#103 (beide neu zugewiesen), #23/#34/#63 (wachauer ergänzt), #73/#85/#92 (beide neu zugewiesen). Memory-Regel `feedback_editorial_assignees.md` persistiert.
- Comment auf #85 mit Audit-Befund (Kat. 2 strukturell done).
- Status-Comments auf #102 + #103 mit konkreter Diagnose.

**Verifikations-Artefakte:**
- `scripts/audit/validate-corpus.py --sample APO ARB ATF DIO DL2 ESB MBS1 MBS5 MBS7 MNA MR1 MR2 MSP REG`: 14/14 valid, 0 Stage-2-Fails.
- Chrome-DevTools-Browser-Verifikation MBS7 in Reader-View: `[140v]` am Zeilenanfang, `[141r]` mid-line zwischen "ein"/"grosse" (siehe `MR2_140201_4` → `MR2_141101_0` Token-Sequenz). Render via `<span class="page-break" title="Seite 141r">[141r]</span>`.

**Next session:**
1. `/promptotyping orient`
2. **Falls Carinas Antwort eingetroffen (#92):** ARI-Phase 1 starten — `wzb-auto-match.py` → `ari-auto-match.py` mit `# ARI-only:`-Diff-Kommentaren, Diff messen für Generic-Skript-Entscheidung.
3. **Falls KZW auf #101 antwortet:** Implementation-Issue mit Schema-Mapping (TEI-Element → CSS-Klasse → Browser-Anzeige) eröffnen.
4. **Claude-ready ohne Antwort-Abhängigkeit:**
   - **#23 Stanza-Insert** für die ~80 nicht-Prosa Texte (Skript-ready, ähnlich `insert-pb-from-linecode.py`).
   - **#85 Kat. 1** (13 MBS-Serie): Strukturanalyse pro Text + KI-Einschätzung, ~4h.
   - **#85 Kat. 3** (DES2, DJEM, DUB): Julia hat parallel/supplied erklärt, vorbereitbar.
   - **#45 Static JSON API:** Planning-Doc `045-static-api.md` fertig, FAIR-Wert hoch, koppelt mit #91 Zenodo.
   - **Upload-UI Dead-Code-Cleanup:** `handleTEIFiles`, `uploadZone`, `fileInput`, ungenutzte tei-manager.js-Methoden — Cluster mit #98/#99.
5. **Manuelle User-Aufgaben:** #91 Zenodo-Webhook aktivieren + Tag pushen.
6. **WZB-Skript-Refactor** zu `scripts/ingest/wzb/` als ältester offener Folge-Task.

---

## 2026-05-11 13:30 — handoff (Session C: #78 Schema-Hilfe-Seite + zwei Faktencheck-Iterationen)

**Summary:** #78 komplett — neue `hilfe-schema.html` mit normativer Schema-Doku, neun lazy-fetched Beispieldateien (Prism-Highlighting), Step-by-Step-Tutorial für Carina (#92) und 5-Tab-Hilfe-Nav in allen Hilfe-Seiten. Zwei `/check-md`-Iterationen: Iteration 1 fand vier Doku-Drift-Punkte (cache size, contributors.xml fehlend, Lemma-Zahl, §-Querverweis), Iteration 2 fand einen CRITICAL Sprachstufen-Code-Fehler und drei kleinere Inkonsistenzen.

**Decisions:**
- **Prism.js als gevendortes npm-Bundle, nicht CDN:** parallel zu Tailwind-Pattern (Source via npm devDep, Output committed via `scripts/build-vendor.js`). Repo-Footprint ~12 KB, kein Drittanbieter im Auslieferungspfad, versionsgebunden via `package-lock.json`. Vorbereitung für künftige Vendor-Bundles.
- **Beispieldateien lazy-fetched statt inline:** 9 `<details>`-Blöcke, XML erst beim Aufklappen via `fetch()` aus `schema/examples/` geladen und mit Prism gehighlightet. Initial-Render-Size sonst ~50 KB extra HTML (HTML-Escapen verdoppelt Char-Count). Trade-off: braucht JS, aber Hilfe-Seiten brauchen JS sowieso für Mobile-Menu.
- **5. Tab „Schema" in der Hilfe-Nav** statt Daten-Submenü: einfacher visuell, ein-Klick-Zugriff. Tab-Patches in 5 Hilfe-Seiten.
- **#78 schließt Lücke zwischen Schema-README (Entwickler) und `hilfe-daten-beitragen.html` (Konversion):** Schema-Seite addressiert „ich habe Plaintext/CSV → wie kommt das zu MHDBDB-TEI", bisher nirgends user-facing dokumentiert. Beide Seiten verlinken sich.
- **/check-md zweistufig:** Iteration 1 hat zwei eigene Befunde widerlegt — ich hatte gegen abgeleitete Indizes statt Source-Files verifiziert. Iteration 2 systematisch korrigiert: jede Behauptung gegen `tei/*.tei.xml`/`variants.xml`/`lexicon.xml`/Frontend-Code, nicht `data/*.json.gz`. **Lehre: Source vor Index, immer.**

**Dead ends:**
- Sprachstufen-Codes in erster Schema-Seiten-Version waren erfunden: `gmh-bavarian`, `gmh-alemannic`, `gmh-rhinefranconian` und `enm` als FNHD-Code empfohlen, ohne gegen Korpus zu verifizieren. Korpus nutzt ausschließlich `gmh`; ARI nutzt `gmf` (ad hoc); `enm` ist ISO-639-3 Middle English. Iteration 2 entfernt und auf #81 verwiesen. Carina hätte beinahe `enm`-Tags in ihre Rechenbücher reingeschrieben.
- /check-md Iteration 1 Befund #2 + #3 (WZB Coverage, 192.472 Varianten): beide auf Index-Drift zurückgeführt. Korrektur: 149,148 WZB-Tokens + 95.3/95.3/95.2% sind echte Werte; 192,472 Wortformen in variants.xml stimmen auch. Index zählt 175,910 weil Build-Filter Untermenge. Beide Iteration-1-Befunde zurückgezogen.

**Commits (alle gepusht, neueste zuerst):**
- `88d52885b` Faktencheck Iteration 2 (Sprachstufen, Edition-Switch, Genderzeichen)
- `5edf4fa24` Faktencheck Iteration 1
- `c87357378` `feat(docs): hilfe-schema.html (#78) + 5-Tab-Hilfe-Nav` — Closes #78
- `cba62d41d` `chore(deps): Prism.js als gevendortes npm-Bundle`

Aus paralleler Session: `795670240` `feat(tei): #26 pb-Insertion fuer 14 Texte (1293 <pb> aus Linecode-Handover)`.

**Externe:** #78 closed via Commit `c87357378`. `hilfe-schema.html` live. Neuer Output-Pfad `assets/vendor/prism/` (3 Files + MANIFEST.txt) committed. `package.json`: prismjs als devDep + neues script `build:vendor`.

**Open issues:**
- **#92 ARITHMETIC:** weiter blockiert auf Carina. Schema-Seite ist jetzt user-facing Einstieg für sie.
- **#91 Zenodo:** Katharina war mit CITATION.cff dran, Stand unbekannt; Plan in 12:32-Handoff (#91 Pre-Tag-Checkliste).
- **#81 Sprachstufen:** in neuer Schema-Seite als offener Diskussionspunkt verlinkt. Carina `gmf`, Korpus `gmh`, ARI-Branch noch nicht offiziell — KZW + Julia sollten Konvention setzen.
- **playground/index.html Hero-Tagline + Korpus-Loader-Text:** aktualisiert (43,754 statt 43,750, ~39 MB gzipped). Pattern: jedes Mal bei Index-Rebuild Strings nachziehen — könnte auf `manifest.json`-driven UI umstellen, eigenes Ticket wert.
- **Autor:in vs. Autor*in Genderzeichen-Konsistenz:** in Hilfe-Seiten jetzt alles `Autor*in` (matched UI). Einige Stellen mit `Autor:in` evtl. noch da, nicht systematisch geprüft.
